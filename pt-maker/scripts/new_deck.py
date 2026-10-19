#!/usr/bin/env python3
"""pt-maker: 다음 순번의 덱 폴더를 모드별로 스캐폴딩한다.

사용:
  python new_deck.py "<slug>" --production-direction animation|text|image
                     [--mode presentation|animation|both]
                     [--date YYYYMMDD] [--root <작업공간>]
  python new_deck.py "<slug>" --production-direction judged [--template template.pptx]

output/ 의 기존 최대 순번 +1 을 계산해
  presentation: deck.html + assets/
  animation:    animation/ HyperFrames project; live presentation HTML is
                generated from final compositions as the primary artifact
                (rendered video is optional on explicit request)
  both:         both outputs
와 build-notes.md, motion-ledger.json을 만든다.
judged(심사·제출용)는 Reveal이 아닌 고정 크기 HTML 슬라이드 프로젝트(deck.src.html, deck.css,
facts.json, judged.json, shots.json, CHANGES.md, NOTES.md, assets/)와 build-notes.md를 만든다.
--template을 주면 import_template.py로 template.json·template-layer.css·assets/template/을 만들고
템플릿 슬롯마다 한 페이지씩 deck.src.html을 채운다.
생성된 덱 폴더 경로를 마지막 줄에 출력한다.
표준 라이브러리만 사용.
"""
import argparse
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path

from browser_harness_runtime import (
    BrowserHarnessError,
    ensure_background_runtime,
)
from import_template import import_template, summary as template_summary

SEQ_RE = re.compile(r"^(\d{2,})_")
MODES = ("presentation", "animation", "both")
PRODUCTION_DIRECTIONS = ("animation", "text", "image", "judged")


def next_seq(output_dir: Path) -> int:
    mx = 0
    if output_dir.is_dir():
        for p in output_dir.iterdir():
            if p.is_dir():
                m = SEQ_RE.match(p.name)
                if m:
                    mx = max(mx, int(m.group(1)))
    return mx + 1


def write_credits(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# asset | source/generation mode | URL or prompt note | accessed/generated date\n",
        encoding="utf-8",
    )


def replace_placeholders(folder: Path, values: dict[str, str]) -> None:
    for path in folder.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".html",
            ".json",
            ".md",
            ".txt",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        for token, value in values.items():
            text = text.replace(token, value)
        path.write_text(text, encoding="utf-8")


def scaffold_presentation(deck_dir: Path, template: Path) -> None:
    (deck_dir / "assets").mkdir(parents=True)
    shutil.copyfile(template, deck_dir / "deck.html")
    write_credits(deck_dir / "assets" / "CREDITS.txt")


def scaffold_animation(
    deck_dir: Path,
    template_dir: Path,
    slug: str,
    created_at: str,
) -> None:
    target = deck_dir / "animation"
    shutil.copytree(template_dir, target)
    replace_placeholders(
        target,
        {
            "__PROJECT_SLUG__": slug,
            "__CREATED_AT__": created_at,
        },
    )


def judged_page(
    number: int,
    *,
    tpl: int | None = None,
    title: str = "",
    title_style: str = "",
    style: str = "",
    main: bool = True,
    headline: str = "CLAIM HEADLINE",
) -> str:
    attrs = ""
    if tpl is not None:
        attrs += f' data-tpl="{tpl}" data-slot="{tpl}"'
    if main:
        attrs += " data-main"
    if style:
        attrs += f' style="{style}"'
    slot = ""
    if title:
        cls = "tt nowc on-art" if title_style else "tt nowc"
        style_attr = f' style="{title_style}"' if title_style else ""
        slot = f'<div class="{cls}"{style_attr}>{html.escape(title)}</div>'
    comment_title = title.replace("--", "- -")
    return (
        f'<!-- {number:02d}{f" · template slot {tpl}: {comment_title}" if tpl else ""} -->\n'
        f'<section class="slide"{attrs}>\n'
        f'  <header class="hd">{slot}<h1><span class="ph">{headline}</span></h1></header>\n'
        '  <footer class="ft"><div class="src"><span class="ph">WHAT WAS MEASURED, HOW</span> '
        'Details: <span class="ph">SOURCE</span></div>'
        f'<div class="pg"><b>{number:02d}</b></div></footer>\n'
        "</section>\n"
    )


def page_layout(entry: dict, height: int) -> tuple[str, str]:
    """(slide style, slot title style) that keep the scaffold clear of the template's art."""
    box = entry.get("title_box") or {}
    art = entry["art"]
    under_title = [a for a in art if a.get("layer") == "base"]
    bottom_art = [a["y"] for a in art if a["y"] >= height / 2]
    title_style = ""
    if under_title:
        # The template draws its title on a band: keep the slot title there and start the content below it.
        top = max(a["y"] + a["h"] for a in under_title) + 32
        title_style = f"left:{box['text_x']:g}px;top:{box['text_y']:g}px"
        if box.get("color"):
            title_style += f";color:{box['color']}"
    else:
        top_art = [a["y"] + a["h"] for a in art if a["y"] < height / 2]
        top = box.get("text_y") or (max(top_art) + 40 if top_art else 96)
    style = f"--top:{top:g}px"
    if box.get("text_x"):
        style += f";--left:{box['text_x']:g}px"
    if box.get("font_px"):
        style += f";--tt-size:{box['font_px']:g}px"
    if bottom_art:
        style += f";--ft-bottom:{round(height - min(bottom_art) + 16, 2):g}px"
    return style, title_style


def judged_source(template: dict | None) -> str:
    head = (
        "<!doctype html>\n<html lang=\"ko\" data-deck=\"judged\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>Judged deck</title>\n<link rel=\"stylesheet\" href=\"deck.css\">\n"
    )
    pages = []
    if template is None:
        pages.append(judged_page(1, headline="ONE-LINE MESSAGE"))
        pages.append(judged_page(2))
        pages.append(judged_page(3, main=False, headline="Q&amp;A"))
    else:
        height = template["slide_size"]["px"][1]
        fonts = template.get("fonts") or []
        if fonts:
            head += f'<style>:root {{ --tpl: "{fonts[0]["family"]}", var(--sans); }}</style>\n'
        for entry in template["slides"]:
            if not entry["title"]:
                pages.append(
                    f"<!-- {entry['index']:02d} · template slot {entry['index']} has no title: keep its art as is, "
                    "fill it, or list it in judged.json slots.skip -->\n"
                    f'<section class="slide" data-tpl="{entry["index"]}" data-slot="{entry["index"]}"></section>\n'
                )
                continue
            style, title_style = page_layout(entry, height)
            pages.append(judged_page(entry["index"], tpl=entry["index"], title=entry["title"], title_style=title_style, style=style))
    return (
        head
        + "</head>\n<body>\n"
        "<!-- Rules: one claim per slide; every number from facts.json via {{fact:id}} with a footer "
        "\"Details:\" line; evidence pictures are real captures (capture_screens.py) or public sources, never "
        "generated; comments stay in this source only. -->\n"
        + "\n".join(pages)
        + "</body>\n</html>\n"
    )


def scaffold_judged(deck_dir: Path, judged_dir: Path, template_path: Path | None) -> None:
    for name in ("deck.css", "facts.json", "judged.json", "shots.json", "CHANGES.md", "NOTES.md"):
        shutil.copyfile(judged_dir / name, deck_dir / name)
    (deck_dir / "assets" / "img").mkdir(parents=True)
    (deck_dir / "assets" / "icons").mkdir(parents=True)
    write_credits(deck_dir / "assets" / "CREDITS.txt")
    template = None
    if template_path is not None:
        template = import_template(template_path, deck_dir)
        print(template_summary(template))
        config_path = deck_dir / "judged.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["template"] = "template.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (deck_dir / "deck.src.html").write_text(judged_source(template), encoding="utf-8")


def write_build_notes(
    deck_dir: Path,
    mode: str,
    production_direction: str,
) -> None:
    (deck_dir / "build-notes.md").write_text(
        "# Build notes\n\n"
        f"- mode: `{mode}`\n\n"
        f"- production-direction: `{production_direction}`\n\n"
        "## Intake\n\n"
        "- audience:\n- context:\n- one-line message:\n- evidence:\n- CTA:\n\n"
        "## Scene plan\n\n"
        "| scene/slide | claim | evidence | visual plan | motion purpose | speaker note |\n"
        "|---:|---|---|---|---|---|\n\n"
        "## QA log\n\n"
        "- static guard:\n- rendered artifacts:\n- snapshot/contact-sheet review:\n"
        "- rubric score:\n- user preview approval:\n- regression check:\n",
        encoding="utf-8",
    )


def write_motion_ledger(
    deck_dir: Path,
    mode: str,
    production_direction: str,
) -> None:
    (deck_dir / "motion-ledger.json").write_text(
        json.dumps(
            {
                "mode": mode,
                "production_direction": production_direction,
                "dominant_current": "left-to-right",
                "transition_vocabulary": [
                    "rise",
                    "carrier-match",
                    "hard-resolve",
                ],
                "continuity_contract": {
                    "subject_identity": "",
                    "camera": "",
                    "environment": "",
                    "palette": "",
                    "invariants": [],
                },
                "seams": [],
                "image_sequences": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y%m%d"))
    ap.add_argument("--root", default=".")
    ap.add_argument(
        "--mode",
        choices=MODES,
        default=None,
        help=(
            "presentation=Reveal HTML, "
            "animation=HyperFrames project + primary live animated HTML "
            "(video export only on explicit request), "
            "both=both outputs"
        ),
    )
    ap.add_argument(
        "--production-direction",
        choices=PRODUCTION_DIRECTIONS,
        required=True,
        help="Required user-confirmed format: animation, text, image, or judged",
    )
    ap.add_argument(
        "--template",
        type=Path,
        help="judged only: the required .pptx template to import",
    )
    args = ap.parse_args()
    if args.template is not None and args.production_direction != "judged":
        ap.error("--template is only for --production-direction judged")
    if args.production_direction == "judged":
        if args.mode is not None:
            ap.error("judged production direction makes one fixed-size HTML deck; do not pass --mode")
        if args.template is not None and not args.template.is_file():
            ap.error(f"--template file not found: {args.template}")
    mode = "judged" if args.production_direction == "judged" else args.mode or (
        "animation"
        if args.production_direction == "animation"
        else "presentation"
    )
    if args.production_direction == "animation" and mode == "presentation":
        ap.error("animation production direction requires --mode animation or both")
    if args.production_direction in {"text", "image"} and mode == "animation":
        ap.error("text/image production direction requires --mode presentation or both")

    try:
        ensure_background_runtime()
    except BrowserHarnessError as exc:
        sys.exit(f"ERROR: browser-harness background is required: {exc}")

    root = Path(args.root).resolve()
    output_dir = root / "output"
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    presentation_template = assets_dir / "template.html"
    animation_template = assets_dir / "animation-mode"
    judged_template = assets_dir / "judged-mode"
    if mode in {"presentation", "both"} and not presentation_template.is_file():
        sys.exit(f"ERROR: 프레젠테이션 템플릿을 찾을 수 없음: {presentation_template}")
    if mode in {"animation", "both"} and not animation_template.is_dir():
        sys.exit(f"ERROR: 애니메이션 템플릿을 찾을 수 없음: {animation_template}")

    seq = next_seq(output_dir)
    deck_dir = output_dir / f"{seq:02d}_{args.slug}_{args.date}"
    if deck_dir.exists():
        sys.exit(f"ERROR: 이미 존재함: {deck_dir}")
    deck_dir.mkdir(parents=True)
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if mode in {"presentation", "both"}:
        scaffold_presentation(deck_dir, presentation_template)
    if mode in {"animation", "both"}:
        scaffold_animation(deck_dir, animation_template, args.slug, created_at)
    if mode == "judged":
        try:
            scaffold_judged(
                deck_dir,
                judged_template,
                args.template.resolve() if args.template else None,
            )
        except Exception as exc:  # any import failure: leave no half-made deck folder behind
            shutil.rmtree(deck_dir, ignore_errors=True)
            sys.exit(f"ERROR: 템플릿을 읽을 수 없음 ({type(exc).__name__}): {exc}")
    write_build_notes(deck_dir, mode, args.production_direction)
    if mode != "judged":
        write_motion_ledger(deck_dir, mode, args.production_direction)

    print(
        f"OK: 덱 폴더 생성 "
        f"(seq={seq:02d}, date={args.date}, mode={mode}, "
        f"production-direction={args.production_direction})"
    )
    print(deck_dir)


if __name__ == "__main__":
    main()
