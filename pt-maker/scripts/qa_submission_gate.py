#!/usr/bin/env python3
"""pt-maker judged mode: final submission gate.

제출 직전에 deck.html과 PDF가 대회 규칙과 템플릿을 지키는지 검사한다.

사용:
  python qa_submission_gate.py deck.html deck.pdf --config judged.json [--offline] [--json]

실패 조건:
  placeholder-left      {{…}} 자리표시, .ph(채우지 않은 자리·없는 링크), TODO/TBD/FIXME, lorem ipsum이 남음
  pdf-too-large         PDF가 limits.max_mb를 넘음 (1 MB = 1,000,000 bytes, 더 엄격한 쪽)
  pdf-too-many-pages    PDF 쪽수가 limits.max_pages를 넘음
  pdf-slide-mismatch    PDF 쪽수와 deck.html의 .slide 수가 다름 (화면과 1:1이 아님)
  pdf-stale             PDF가 deck.html보다 오래됨 (마지막 빌드 뒤 다시 렌더하지 않음)
  slot-invalid / slot-order / slot-missing / slot-title-mismatch
                        data-slot="N" 페이지가 template.json 슬롯 순서대로 다 있고, 각 페이지에
                        템플릿 슬롯 제목이 보이는지 (judged.json slots.skip의 슬롯은 빼도 됨).
                        template.json 슬라이드의 "match"로 제목 비교 방식을 정한다:
                        exact(기본, 제목 전체), prefix(첫 '(' ':' '—' 앞 부분만, 안내문이 붙은 제목용),
                        skip(제목 비교 안 함, "Click to add title" 같은 자리표시 제목용)
  link-not-200          deck.html의 http(s) 링크가 최종 HTTP 200이 아님 (--offline이면 건너뜀)
표준 라이브러리만 사용.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from qa_layout_gate import pdf_info

PROTECTED_RE = re.compile(r"<(script|style)\b[\s\S]*?</\1\s*>", re.I)
LEFTOVER_RE = re.compile(r"\{\{[^{}]*\}\}")
MARKER_RE = re.compile(r"\b(TODO|TBD|FIXME)\b|lorem ipsum", re.I)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
USER_AGENT = "Mozilla/5.0 (pt-maker submission check)"


class DeckText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict[str, Any]] = []
        self.links: list[str] = []
        self.placeholders: list[str] = []
        self.stack: list[tuple[str, bool, bool]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        if tag == "a" and re.match(r"^https?://", data.get("href", "")) and data["href"] not in self.links:
            self.links.append(data["href"])
        is_slide = "slide" in classes
        if is_slide:
            self.slides.append({"slot": data.get("data-slot"), "text": []})
        if tag in VOID_TAGS:
            return
        if "ph" in classes:
            self.placeholders.append("")
        self.stack.append((tag, is_slide, "ph" in classes))

    def handle_endtag(self, tag: str) -> None:
        for depth in range(len(self.stack) - 1, -1, -1):
            if self.stack[depth][0] == tag:
                del self.stack[depth:]
                break

    def handle_data(self, data: str) -> None:
        if any(tag in ("script", "style") for tag, _, _ in self.stack):
            return
        self.text.append(data)
        if any(ph for _, _, ph in self.stack):
            self.placeholders[-1] += data
        if self.slides and any(slide for _, slide, _ in self.stack):
            self.slides[-1]["text"].append(data)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_link(url: str, timeout: float = 15) -> dict[str, Any]:
    last: dict[str, Any] = {"url": url, "status": None}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                last = {"url": url, "status": response.status}
        except urllib.error.HTTPError as exc:
            last = {"url": url, "status": exc.code}
            exc.close()
        except (urllib.error.URLError, OSError, ValueError) as exc:
            last = {"url": url, "status": None, "error": str(getattr(exc, "reason", exc))}
        if last["status"] == 200:
            return last
    return last


def slot_title(entry: dict[str, Any]) -> str:
    """The part of the template slot title a page must show, by the slot's match mode."""
    match = entry.get("match", "exact")
    title = norm(entry.get("title", ""))
    if match == "skip":
        return ""
    if match == "prefix":
        return re.split(r"\s*[(:—–]", title, maxsplit=1)[0].strip()
    return title


def find_template(config: dict[str, Any], config_dir: Path, deck: Path) -> Path | None:
    if config.get("template"):
        return config_dir / str(config["template"])
    candidate = deck.parent / "template.json"
    return candidate if candidate.is_file() else None


def run_checks(deck: Path, pdf: Path, config: dict[str, Any], *, config_dir: Path, offline: bool) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str, fix: str) -> None:
        errors.append({"code": code, "message": message, "fix": fix})

    html = deck.read_text(encoding="utf-8", errors="ignore")
    parser = DeckText()
    parser.feed(html)

    leftovers = LEFTOVER_RE.findall(PROTECTED_RE.sub("", html))
    markers = sorted({match.group(0) for match in MARKER_RE.finditer(norm("".join(parser.text)))})
    unfilled = [norm(text) or "(empty)" for text in parser.placeholders]
    for kind, found in (("{{…}}", leftovers), (".ph", unfilled), ("marker", markers)):
        if found:
            add("placeholder-left", f"{kind} left in the deck: {sorted(set(found))}", "Fill it (set the link env var, write the copy) and rebuild.")

    limits = config.get("limits") if isinstance(config.get("limits"), dict) else {}
    data = pdf.read_bytes()
    info = pdf_info(data)
    size_mb = len(data) / 1_000_000
    if limits.get("max_mb") and size_mb > float(limits["max_mb"]):
        add("pdf-too-large", f"PDF is {size_mb:.2f} MB (limit {limits['max_mb']} MB).", "Lower JPEG quality or capture width in shots.json, then rebuild and re-render.")
    if limits.get("max_pages") and info["pages"] > int(limits["max_pages"]):
        add("pdf-too-many-pages", f"PDF has {info['pages']} pages (limit {limits['max_pages']}).", "Merge or cut pages; move detail to fewer appendix pages.")
    if info["pages"] != len(parser.slides):
        add("pdf-slide-mismatch", f"PDF has {info['pages']} pages, deck.html has {len(parser.slides)} slides.", "Re-render the PDF from this deck.html with qa_layout_gate.py.")
    if pdf.stat().st_mtime + 1 < deck.stat().st_mtime:
        add("pdf-stale", "PDF is older than deck.html.", "Re-render the PDF after the last build.")

    template_path = find_template(config, config_dir, deck)
    if template_path is not None and template_path.is_file():
        template = json.loads(template_path.read_text(encoding="utf-8"))
        titles = {int(entry["index"]): slot_title(entry) for entry in template.get("slides", [])}
        skip = {int(n) for n in (config.get("slots") or {}).get("skip", [])}
        previous = 0
        seen: set[int] = set()
        for page, entry in enumerate(parser.slides, start=1):
            if entry["slot"] is None:
                continue
            try:
                slot = int(entry["slot"])
            except ValueError:
                add("slot-invalid", f"Page {page:02d} has data-slot={entry['slot']!r}.", "Use the template slide number, e.g. data-slot=\"3\".")
                continue
            if slot not in titles:
                add("slot-invalid", f"Page {page:02d} data-slot={slot} is not a template slide.", "Use a slot number from template.json.")
                continue
            if slot < previous:
                add("slot-order", f"Page {page:02d} is slot {slot} after slot {previous}.", "Keep the template's slot order.")
            previous = max(previous, slot)
            seen.add(slot)
            title = norm(titles[slot])
            if title and title not in norm("".join(entry["text"])):
                add("slot-title-mismatch", f"Page {page:02d} (slot {slot}) does not show the slot title \"{title}\".", "Show the template's slot title exactly (class=\"tt nowc\").")
        missing = sorted(set(titles) - seen - skip)
        if missing:
            add("slot-missing", f"Template slots with no page: {missing}", "Add a page with data-slot for each, or list it in judged.json slots.skip if the rules allow.")

    links: Any = "skipped (--offline)"
    if not offline:
        links = [check_link(url) for url in parser.links]
        for link in links:
            if link["status"] != 200:
                add("link-not-200", f"{link['url']} → {link['status'] or link.get('error')}", "Fix the URL or make the page public, then rebuild.")

    return {
        "qa_submission_gate": "fail" if errors else "pass",
        "error_count": len(errors),
        "slides": len(parser.slides),
        "pdf": {"pages": info["pages"], "bytes": len(data), "mb": round(size_mb, 2)},
        "template": str(template_path) if template_path else None,
        "links": links,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("deck", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--config", type=Path, help="judged.json (default: next to the deck)")
    parser.add_argument("--offline", action="store_true", help="skip the HTTP 200 link check")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    for path in (args.deck, args.pdf):
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
    config_path = args.config or args.deck.with_name("judged.json")
    config = json.loads(config_path.read_text(encoding="utf-8-sig")) if config_path.is_file() else {}
    result = run_checks(args.deck, args.pdf, config, config_dir=config_path.parent, offline=args.offline)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        pdf = result["pdf"]
        print(
            f"qa-submission-gate: {result['qa_submission_gate']} ({result['slides']} slides, PDF {pdf['pages']} pages "
            f"{pdf['mb']} MB, links {'skipped' if isinstance(result['links'], str) else len(result['links'])}, "
            f"{result['error_count']} blocking issue(s))"
        )
        for error in result["errors"]:
            print(f"- P0 [{error['code']}]: {error['message']}")
            print(f"  fix: {error['fix']}")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
