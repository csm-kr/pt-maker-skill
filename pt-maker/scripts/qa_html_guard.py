#!/usr/bin/env python3
"""Static HTML quality guard for pt-maker decks.

This catches deterministic-rendering, accessibility, image-sequence, and
presentation-runtime risks before rendered QA. It does not replace visual QA.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


REMOTE_SCHEMES = {"http", "https", "data", "blob"}
MOTION_MARKERS = ("data-motion", "image-sequence", "requestAnimationFrame", ".fragment")
NONDETERMINISTIC_PATTERNS = {
    "math-random": r"\bMath\.random\s*\(",
    "wall-clock-date": r"\bDate\.now\s*\(",
    "wall-clock-performance": r"\bperformance\.now\s*\(",
    "timer-interval": r"\bsetInterval\s*\(",
}


class DeckParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.images: list[dict[str, str]] = []
        self.media: list[dict[str, str]] = []
        self.sections: list[dict[str, Any]] = []
        self.sequences: list[dict[str, Any]] = []
        self._section_depth = 0
        self._current_section: dict[str, Any] | None = None
        self._current_sequence: dict[str, Any] | None = None
        self._sequence_depth = 0

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key: (value or "") for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = self.attrs_dict(attrs)
        if data.get("id"):
            self.ids.append(data["id"])

        if tag == "section":
            if self._section_depth == 0:
                self._current_section = {
                    "attrs": data,
                    "headings": [],
                    "notes": False,
                    "buttons": [],
                }
                self.sections.append(self._current_section)
            self._section_depth += 1

        if tag in {"h1", "h2"} and self._current_section is not None:
            self._current_section["headings"].append(tag)

        classes = set(data.get("class", "").split())
        if tag == "aside" and "notes" in classes and self._current_section is not None:
            self._current_section["notes"] = True

        if tag in {"button", "a"} and self._current_section is not None:
            self._current_section["buttons"].append(data)

        if tag in {"figure", "div"} and "image-sequence" in classes:
            self._current_sequence = {"attrs": data, "frames": []}
            self.sequences.append(self._current_sequence)
            self._sequence_depth = 1
        elif self._current_sequence is not None and tag not in self.VOID_TAGS:
            self._sequence_depth += 1

        if tag == "img":
            self.images.append(data)
            if self._current_sequence is not None:
                self._current_sequence["frames"].append(data)

        if tag in {"video", "audio"}:
            item = dict(data)
            item["_tag"] = tag
            self.media.append(item)

    def handle_endtag(self, tag: str) -> None:
        if self._current_sequence is not None:
            self._sequence_depth -= 1
            if self._sequence_depth <= 0:
                self._current_sequence = None
                self._sequence_depth = 0

        if tag == "section" and self._section_depth:
            self._section_depth -= 1
            if self._section_depth == 0:
                self._current_section = None


def issue(level: str, code: str, message: str, fix: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message, "fix": fix}


def local_asset(src: str, html_path: Path) -> Path | None:
    if not src or src.startswith("#"):
        return None
    parsed = urlparse(src)
    if parsed.scheme.lower() in REMOTE_SCHEMES or src.startswith("//"):
        return None
    clean = unquote(parsed.path)
    return (html_path.parent / clean).resolve()


def image_size(path: Path) -> tuple[int, int] | None:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.size
    except Exception:
        return None


def run_checks(html_path: Path) -> dict[str, Any]:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    parser = DeckParser()
    parser.feed(html)
    findings: list[dict[str, str]] = []

    def add(level: str, code: str, message: str, fix: str) -> None:
        findings.append(issue(level, code, message, fix))

    if not re.search(r"\bwidth\s*:\s*1280\b", html) or not re.search(r"\bheight\s*:\s*720\b", html):
        add("P0", "canvas-not-1280x720", "Reveal canvas is not explicitly fixed at 1280×720.", "Set Reveal.initialize({width:1280,height:720}).")

    if "pdfPageHeightOffset" not in html or not re.search(r"\bcenter\s*:\s*false\b", html):
        add("P0", "print-bleed-contract-missing", "PDF bleed prevention settings are incomplete.", "Use center:false and pdfPageHeightOffset:0.")

    duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicates:
        add("P0", "duplicate-ids", f"Duplicate HTML ids: {duplicates}", "Give every interactive/labelled element a unique id.")

    for index, image in enumerate(parser.images, start=1):
        if "alt" not in image:
            add("P0", "image-alt-missing", f"Image {index} has no alt attribute.", "Add meaningful alt text, or alt=\"\" when the figure has an aria-label.")
        src = image.get("src", "")
        path = local_asset(src, html_path)
        if path is not None and not path.is_file():
            add("P0", "image-file-missing", f"Image {index} points to a missing file: {src}", "Copy the asset into the deck folder and fix src.")

    for item in parser.media:
        if "autoplay" in item and "muted" not in item:
            add("P0", "unmuted-autoplay", f"{item['_tag']} autoplays without muted.", "Remove autoplay or add muted and explicit accessible controls.")

    for name, pattern in NONDETERMINISTIC_PATTERNS.items():
        if re.search(pattern, html):
            add("P0", name, f"Render-critical source contains {name}.", "Precompute values and drive motion from slide state or a finite timeline.")

    if re.search(r"animation(?:-iteration-count)?\s*:[^;}]*\binfinite\b", html, re.I):
        add("P0", "infinite-css-animation", "CSS contains an infinite animation.", "Use a finite entrance/sequence and a stable final pose.")

    has_motion = any(marker in html for marker in MOTION_MARKERS)
    if has_motion and "prefers-reduced-motion" not in html:
        add("P0", "reduced-motion-missing", "Motion exists without a prefers-reduced-motion fallback.", "Show final states immediately under prefers-reduced-motion: reduce.")

    if has_motion and ("beforeprint" not in html and "print-pdf" not in html):
        add("P0", "print-motion-state-missing", "Motion exists without an explicit print/PDF pose.", "Freeze each sequence and motion element to a readable print state.")

    seen_sequence_ids: set[str] = set()
    for sequence in parser.sequences:
        attrs = sequence["attrs"]
        frames = sequence["frames"]
        sequence_id = attrs.get("data-sequence-id", "")
        if not sequence_id:
            add("P0", "sequence-id-missing", "An image sequence has no data-sequence-id.", "Give every sequence a stable unique id.")
        elif sequence_id in seen_sequence_ids:
            add("P0", "sequence-id-duplicate", f"Duplicate sequence id: {sequence_id}", "Use a unique data-sequence-id.")
        seen_sequence_ids.add(sequence_id)

        if len(frames) < 2:
            add("P0", "sequence-too-short", f"Sequence {sequence_id or '<unnamed>'} has fewer than two frames.", "Add at least two continuity-checked frames.")
        if not attrs.get("aria-label"):
            add("P0", "sequence-label-missing", f"Sequence {sequence_id or '<unnamed>'} has no aria-label.", "Describe the complete sequence on its container.")
        if attrs.get("data-loop", "false").lower() == "true":
            add("P2", "sequence-loop", f"Sequence {sequence_id or '<unnamed>'} loops.", "Use a finite sequence unless ambient looping has a clear presentation purpose.")

        declared = attrs.get("data-print-frame", "0")
        try:
            print_frame = int(declared)
        except ValueError:
            print_frame = -1
        if print_frame < 0 or print_frame >= max(1, len(frames)):
            add("P0", "sequence-print-frame-invalid", f"Sequence {sequence_id or '<unnamed>'} has invalid data-print-frame={declared}.", "Use a zero-based frame index present in the sequence.")

        sizes: set[tuple[int, int]] = set()
        for frame in frames:
            path = local_asset(frame.get("src", ""), html_path)
            if path is not None and path.is_file():
                size = image_size(path)
                if size:
                    sizes.add(size)
        if len(sizes) > 1:
            add("P0", "sequence-size-mismatch", f"Sequence {sequence_id or '<unnamed>'} mixes image sizes: {sorted(sizes)}", "Normalize every frame to the same dimensions and aspect ratio.")

    if parser.sections and not any(section["notes"] for section in parser.sections):
        add("P2", "speaker-notes-missing", "The deck has no speaker notes.", "Add concise transition/source notes with <aside class=\"notes\">.")

    interactive_targets = re.findall(r'data-target-slide\s*=\s*["\'][^"\']+["\']', html)
    if interactive_targets and "keydown" not in html and "<button" not in html:
        add("P0", "branch-keyboard-access-missing", "Branch navigation has no clear keyboard path.", "Use native buttons and keyboard-accessible navigation.")

    transition_values = set(re.findall(r'data-transition\s*=\s*["\']([^"\']+)["\']', html))
    if len(transition_values) > 3:
        add("P2", "transition-vocabulary-wide", f"The deck uses {len(transition_values)} transition styles.", "Limit the deck to two or three meaningful transition families.")

    p0 = [item for item in findings if item["level"] == "P0"]
    p2 = [item for item in findings if item["level"] == "P2"]
    return {
        "html_guard_result": "fail" if p0 else "pass",
        "p0_count": len(p0),
        "p2_count": len(p2),
        "slide_count": len(parser.sections),
        "image_sequence_count": len(parser.sequences),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.is_file():
        sys.stderr.write(f"ERROR: file not found: {html_path}\n")
        return 2

    result = run_checks(html_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"html-guard: {result['html_guard_result']} ({result['p0_count']} P0, {result['p2_count']} P2)")
        for item in result["findings"]:
            print(f"- {item['level']} [{item['code']}]: {item['message']}")
            print(f"  fix: {item['fix']}")
    return 2 if result["p0_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
