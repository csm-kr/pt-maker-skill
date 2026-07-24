#!/usr/bin/env python3
"""pt-maker: 다음 순번의 덱 폴더를 모드별로 스캐폴딩한다.

사용:
  python new_deck.py "<slug>" --production-direction animation|text|image
                     [--mode presentation|animation|both]
                     [--date YYYYMMDD] [--root <작업공간>]

output/ 의 기존 최대 순번 +1 을 계산해
  presentation: deck.html + assets/
  animation:    animation/ HyperFrames project
  both:         both outputs
와 build-notes.md, motion-ledger.json을 만든다.
생성된 덱 폴더 경로를 마지막 줄에 출력한다.
표준 라이브러리만 사용.
"""
import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

from browser_harness_runtime import (
    BrowserHarnessError,
    ensure_background_runtime,
)

SEQ_RE = re.compile(r"^(\d{2,})_")
MODES = ("presentation", "animation", "both")
PRODUCTION_DIRECTIONS = ("animation", "text", "image")


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
        help="presentation=Reveal HTML, animation=HyperFrames MP4 project, both=both outputs",
    )
    ap.add_argument(
        "--production-direction",
        choices=PRODUCTION_DIRECTIONS,
        required=True,
        help="Required user-confirmed format: animation, text, or image",
    )
    args = ap.parse_args()
    mode = args.mode or (
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
    write_build_notes(deck_dir, mode, args.production_direction)
    write_motion_ledger(deck_dir, mode, args.production_direction)

    print(
        f"OK: 덱 폴더 생성 "
        f"(seq={seq:02d}, date={args.date}, mode={mode}, "
        f"production-direction={args.production_direction})"
    )
    print(deck_dir)


if __name__ == "__main__":
    main()
