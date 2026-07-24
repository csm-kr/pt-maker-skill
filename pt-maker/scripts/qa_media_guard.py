#!/usr/bin/env python3
"""pt-maker media QA guard.

Fails fast on recurring deck problems:
1) important web images cropped by object-fit: cover
2) real geography maps drawn as invented inline SVG outlines
3) custom SVG/CSS diagrams shipped without full-size rendered QA proof

Usage:
  python scripts/qa_media_guard.py output/NN_slug_date/deck.html
  python scripts/qa_media_guard.py output/NN_slug_date/deck.html --json

This is a source-level guard. It does not replace rendered PDF QA; it blocks risky
patterns before export and gives the QA reviewer concrete pages/classes to inspect.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.I | re.S)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
SECTION_RE = re.compile(r"<section\b[^>]*>.*?</section>", re.I | re.S)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I | re.S)
SVG_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.I | re.S)
TAG_RE = re.compile(r"<[a-z][^>]*>", re.I | re.S)
SPAN_RE = re.compile(r"<span\b[^>]*>.*?</span>", re.I | re.S)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.S)
CLASS_RE = re.compile(r"\bclass\s*=\s*([\"'])(.*?)\1", re.I | re.S)
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
HARD_BREAK_RE = re.compile(r"\s+")

RISKY_SELECTOR_WORDS = {
    "photo",
    "portrait",
    "person",
    "people",
    "player",
    "profile",
    "avatar",
    "founder",
    "speaker",
    "interview",
    "headshot",
    "hero",
    "closing-visual",
    "food",
    "product",
    "logo",
    "landmark",
    "place",
    "map",
    "thumb",
    "card",
}

SAFE_COVER_WORDS = {
    "cover-ok",
    "crop-ok",
    "background",
    "texture",
    "pattern",
    "decorative",
    "atmosphere",
    "bokeh",
    "abstract",
    "screenshot-crop-ok",
}

IMPORTANT_ALT_DENY = {
    "background",
    "texture",
    "pattern",
    "abstract",
    "decorative",
    "placeholder",
    "gradient",
}

MAP_WORDS = {
    "map",
    "route",
    "region",
    "country",
    "city",
    "canton",
    "language",
    "geography",
    "travel",
    "territory",
    "switzerland",
    "swiss",
    "지도",
    "지리",
    "국가",
    "도시",
    "지역",
    "권역",
    "루트",
    "여행",
    "언어권",
    "음식권",
    "역사",
    "스위스",
    "주",
    "칸톤",
    "경로",
    "위치",
    "지점",
    "핀",
}

DIAGRAM_CLASS_EXACT = {
    "class-flow",
    "concept-diagram",
    "concept-map",
    "diagram",
    "fitness-diagram",
    "flow",
    "flowchart",
    "mini-diagram",
    "network",
    "schematic-map",
    "timeline",
    "triad",
}

DIAGRAM_CLASS_FRAGMENTS = {
    "diagram",
    "flowchart",
    "network",
    "timeline",
    "triad",
}

DIAGRAM_SHAPE_RE = re.compile(r"<(?:circle|ellipse|line|path|polygon|polyline|rect)\b", re.I)


@dataclass
class Finding:
    severity: str
    code: str
    slide: int | None
    message: str
    fix: str


def attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): m.group(3) for m in ATTR_RE.finditer(tag)}


def class_attr(tag: str) -> str:
    m = CLASS_RE.search(tag)
    return m.group(2) if m else ""


def opening_tag(markup: str) -> str:
    m = re.match(r"<[a-z0-9]+[^>]*>", markup, re.I | re.S)
    return m.group(0) if m else markup


def classes_in(text: str) -> set[str]:
    found: set[str] = set()
    for _quote, value in CLASS_RE.findall(text):
        found.update(value.lower().split())
    return found


def norm(text: str) -> str:
    return HARD_BREAK_RE.sub(" ", text).strip().lower()


def selector_has_word(selector: str, words: set[str]) -> bool:
    s = selector.lower()
    return any(w in s for w in words)


def selector_is_safe(selector: str) -> bool:
    return selector_has_word(selector, SAFE_COVER_WORDS)


def css_cover_selectors(html: str) -> list[str]:
    selectors: list[str] = []
    for style in STYLE_RE.findall(html):
        for raw_selector, body in RULE_RE.findall(style):
            if re.search(r"object-fit\s*:\s*cover\b", body, re.I):
                for sel in raw_selector.split(","):
                    clean = norm(sel)
                    if clean:
                        selectors.append(clean)
    return selectors


def css_background_cover_selectors(html: str) -> list[str]:
    selectors: list[str] = []
    for style in STYLE_RE.findall(html):
        for raw_selector, body in RULE_RE.findall(style):
            if re.search(r"background-size\s*:\s*cover\b", body, re.I) and re.search(r"background(?:-image)?\s*:", body, re.I):
                for sel in raw_selector.split(","):
                    clean = norm(sel)
                    if clean:
                        selectors.append(clean)
    return selectors


def section_number(section_html: str, fallback: int) -> int:
    # Only read explicit slide-number UI, never body statistics such as "6/7".
    for span in SPAN_RE.findall(section_html):
        classes = set(class_attr(span).lower().split())
        if "num" not in classes:
            continue
        text = re.sub(r"<[^>]+>", "", span).strip()
        if re.fullmatch(r"\d{1,3}", text):
            value = int(text)
            return value if value > 0 else fallback

    footers = re.findall(r"<div\b[^>]*class\s*=\s*['\"][^'\"]*\bdeck-foot\b[^'\"]*['\"][^>]*>.*?</div>", section_html, re.I | re.S)
    for footer in footers:
        text = re.sub(r"<[^>]+>", "", footer)
        m = re.search(r"(?:^|[^\d])(\d{1,3})\s*/\s*\d{1,3}(?:[^\d]|$)", text)
        if m:
            value = int(m.group(1))
            return value if value > 0 else fallback
    return fallback


def img_is_important(tag: str, context: str) -> bool:
    a = attrs(tag)
    joined = norm(" ".join([a.get("alt", ""), a.get("src", ""), class_attr(tag), context[-500:]]))
    if not joined:
        return False
    if any(w in joined for w in IMPORTANT_ALT_DENY):
        return False
    if any(w in joined for w in RISKY_SELECTOR_WORDS):
        return True
    alt = a.get("alt", "").strip()
    src = a.get("src", "").strip().lower()
    if alt and len(alt) > 2:
        return True
    return src.endswith((".jpg", ".jpeg", ".png", ".webp", ".avif"))


def crop_override_status(tag: str, context: str) -> str:
    a = attrs(tag)
    joined = norm(" ".join([class_attr(tag), context[-300:]]))
    has_override = a.get("data-crop-ok", "").lower() == "true" or any(w in joined for w in SAFE_COVER_WORDS)
    if not has_override:
        return "none"
    has_rendered_proof = (
        a.get("data-rendered-qa", "").lower() == "true"
        or a.get("data-fullsize-qa", "").lower() == "true"
        or "data-rendered-qa=\"true\"" in context[-500:].lower()
        or "data-fullsize-qa=\"true\"" in context[-500:].lower()
    )
    return "verified" if has_rendered_proof else "unverified"


def tag_has_true_attr(tag: str, name: str) -> bool:
    return attrs(opening_tag(tag)).get(name, "").lower() == "true"


def has_required_diagram_qa(markup: str) -> bool:
    return tag_has_true_attr(markup, "data-fullsize-qa") and tag_has_true_attr(markup, "data-rendered-qa")


def class_tokens_indicate_diagram(classes: set[str]) -> bool:
    for cls in classes:
        if cls in DIAGRAM_CLASS_EXACT:
            return True
        if any(fragment in cls for fragment in DIAGRAM_CLASS_FRAGMENTS):
            return True
    return False


def svg_is_likely_custom_diagram(svg: str) -> bool:
    tag = opening_tag(svg)
    a = attrs(tag)
    classes = set(class_attr(tag).lower().split())
    if a.get("aria-hidden", "").lower() == "true" or a.get("data-decorative", "").lower() == "true":
        return False
    if class_tokens_indicate_diagram(classes):
        return True
    lower = svg.lower()
    shape_count = len(DIAGRAM_SHAPE_RE.findall(svg))
    has_text = "<text" in lower
    return has_text and shape_count >= 2


def tag_is_css_diagram_container(tag: str) -> bool:
    tag_name = re.match(r"<([a-z0-9]+)", tag, re.I)
    if not tag_name:
        return False
    if tag_name.group(1).lower() == "svg":
        return False
    a = attrs(tag)
    classes = set(class_attr(tag).lower().split())
    if a.get("aria-hidden", "").lower() == "true" or a.get("data-decorative", "").lower() == "true":
        return False
    return class_tokens_indicate_diagram(classes)


def selector_applies_to_img(selector: str, tag: str, context: str) -> bool:
    # Conservative: exact CSS matching is out of scope; this guard intentionally
    # treats class-name overlap and broad img selectors as risky.
    img_classes = set(class_attr(tag).lower().split())
    context_classes = classes_in(context[-600:])
    selector_tokens = set(re.findall(r"\.([a-z0-9_-]+)", selector.lower()))
    if selector.strip() == "img" or selector.endswith(" img") or " img" in selector:
        if selector_tokens and not (selector_tokens & (img_classes | context_classes)):
            return False
        return True
    return bool(selector_tokens & (img_classes | context_classes))


def check_cover_images(html: str, cover_selectors: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for idx, section in enumerate(SECTION_RE.findall(html), start=1):
        slide = section_number(section, idx)
        for tag in IMG_RE.findall(section):
            a = attrs(tag)
            style = a.get("style", "")
            context = section[: section.find(tag)]
            direct_cover = bool(re.search(r"object-fit\s*:\s*cover\b", style, re.I))
            selector_cover = any(selector_applies_to_img(sel, tag, context) for sel in cover_selectors)
            if not (direct_cover or selector_cover):
                continue
            override_status = crop_override_status(tag, context)
            if override_status == "verified":
                findings.append(
                    Finding(
                        "P2",
                        "cover-crop-needs-rendered-proof",
                        slide,
                        f"Image uses cover with an explicit override: {a.get('src', '') or a.get('alt', '')}",
                        "Inspect the full-size rendered PDF page and keep only if face/head/core subject is intact.",
                    )
                )
                continue
            if override_status == "unverified":
                findings.append(
                    Finding(
                        "P0",
                        "cover-crop-override-without-rendered-proof",
                        slide,
                        f"Image uses a crop override without rendered full-size QA evidence: {a.get('src', '') or a.get('alt', '')}",
                        "Keep the override only after full-size rendered PDF/PNG inspection and mark the image/container with data-rendered-qa=\"true\" or data-fullsize-qa=\"true\".",
                    )
                )
                continue
            if img_is_important(tag, context):
                findings.append(
                    Finding(
                        "P0",
                        "unsafe-object-fit-cover",
                        slide,
                        f"Important image may be cropped by object-fit: cover: {a.get('src', '') or a.get('alt', '')}",
                        "Use object-fit: contain, change object-position/frame ratio, choose another image, or redesign the slide. If a focal crop is truly verified, add data-crop-ok=\"true\" and re-run rendered QA.",
                    )
                )
    return findings


def check_cover_selectors(cover_selectors: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for selector in cover_selectors:
        if selector_is_safe(selector):
            continue
        if selector_has_word(selector, RISKY_SELECTOR_WORDS):
            findings.append(
                Finding(
                    "P0",
                    "risky-cover-selector",
                    None,
                    f"CSS selector uses object-fit: cover on a risky media class: {selector}",
                    "Default person/photo/product/map/card media to contain. Use cover only with a cover-ok/crop-ok class plus rendered full-size QA evidence.",
                )
            )
    return findings


def check_background_cover_selectors(background_selectors: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for selector in background_selectors:
        if selector_is_safe(selector):
            continue
        severity = "P0" if selector_has_word(selector, RISKY_SELECTOR_WORDS) else "P2"
        findings.append(
            Finding(
                severity,
                "background-cover-crop-risk",
                None,
                f"CSS selector uses background-size: cover: {selector}",
                "Do not use background-size: cover for people/products/maps unless the class is cover-ok/crop-ok and full-size rendered QA proves the important subject is intact.",
            )
        )
    return findings


def check_diagram_rendered_qa(html: str) -> list[Finding]:
    findings: list[Finding] = []
    for idx, section in enumerate(SECTION_RE.findall(html), start=1):
        slide = section_number(section, idx)

        for svg in SVG_RE.findall(section):
            if not svg_is_likely_custom_diagram(svg):
                continue
            if has_required_diagram_qa(svg):
                continue
            tag = opening_tag(svg)
            label = attrs(tag).get("aria-label") or class_attr(tag) or "inline SVG diagram"
            findings.append(
                Finding(
                    "P0",
                    "diagram-missing-fullsize-rendered-qa",
                    slide,
                    f"Custom SVG diagram lacks required full-size rendered QA proof: {label}",
                    "Render the slide as a full-size PNG/PDF page, inspect connector/arrow endpoints, labels, and collisions, then add both data-fullsize-qa=\"true\" and data-rendered-qa=\"true\" to the SVG/container.",
                )
            )

        for tag in TAG_RE.findall(section):
            if not tag_is_css_diagram_container(tag):
                continue
            if has_required_diagram_qa(tag):
                continue
            label = class_attr(tag) or "CSS diagram container"
            findings.append(
                Finding(
                    "P0",
                    "diagram-missing-fullsize-rendered-qa",
                    slide,
                    f"Custom CSS/HTML diagram lacks required full-size rendered QA proof: {label}",
                    "Render the slide as a full-size PNG/PDF page, inspect connector/arrow endpoints, labels, and collisions, then add both data-fullsize-qa=\"true\" and data-rendered-qa=\"true\" to the diagram container.",
                )
            )
    return findings


def svg_is_map(svg: str, surrounding: str) -> bool:
    head = svg[:500]
    text = norm(" ".join([head, surrounding[-500:]]))
    return any(w in text for w in MAP_WORDS)


def svg_is_allowed_schematic(svg: str) -> bool:
    head = svg[:800].lower()
    return (
        'data-map-type="schematic"' in head
        or "data-map-type='schematic'" in head
        or "concept-map" in head
        or "schematic-map" in head
    )


def map_base_sources(section: str) -> list[str]:
    sources: list[str] = []
    section_has_map_base_wrapper = "map-base" in classes_in(section)
    for tag in TAG_RE.findall(section):
        a = attrs(tag)
        classes = set(class_attr(tag).lower().split())
        tag_name = re.match(r"<([a-z0-9]+)", tag, re.I)
        name = tag_name.group(1).lower() if tag_name else ""
        explicit = "map-base" in classes or any(k in a for k in ("data-map-base-url", "data-map-base", "data-map-source"))
        if name == "img" and (explicit or section_has_map_base_wrapper):
            src = a.get("data-map-base-url") or a.get("data-map-base") or a.get("data-map-source") or a.get("src") or ""
            if src:
                sources.append(src)
        elif explicit:
            src = a.get("data-map-base-url") or a.get("data-map-base") or a.get("data-map-source") or ""
            if src:
                sources.append(src)
    return sources


def credits_match_map_sources(sources: list[str], credits_text: str) -> bool:
    if not sources:
        return False
    if not credits_text or not URL_RE.search(credits_text):
        return False
    for source in sources:
        source_l = source.lower()
        if source_l.startswith(("http://", "https://")) and source_l not in credits_text:
            return False
        if not source_l.startswith(("http://", "https://")):
            name = Path(source_l).name
            if name and name not in credits_text:
                return False
    return True


def check_maps(html: str, html_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    credits = html_path.parent / "assets" / "CREDITS.txt"
    credits_text = credits.read_text(encoding="utf-8", errors="ignore").lower() if credits.is_file() else ""
    for idx, section in enumerate(SECTION_RE.findall(html), start=1):
        slide = section_number(section, idx)
        section_text = norm(section[:1600])
        section_map_words = any(w in section_text for w in MAP_WORDS)
        sources = map_base_sources(section)
        has_verified_base = credits_match_map_sources(sources, credits_text)
        for svg in SVG_RE.findall(section):
            before = section[: section.find(svg)]
            if not svg_is_map(svg, before):
                continue
            if has_verified_base:
                continue
            if svg_is_allowed_schematic(svg):
                findings.append(
                    Finding(
                        "P2",
                        "schematic-map-needs-label",
                        slide,
                        "Inline SVG map is marked schematic.",
                        "Make the slide visibly say this is a conceptual schematic, not a real map.",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "P0",
                        "inline-real-map-svg",
                        slide,
                        "Inline SVG appears to be used as a real geography map without a sourced map base.",
                        "Use a web/official/public map image or screenshot as the base, cite it, then draw pins/routes/regions as an overlay.",
                    )
                )

        for tag in IMG_RE.findall(section):
            a = attrs(tag)
            src = a.get("src", "")
            joined = norm(" ".join([src, a.get("alt", ""), class_attr(tag), section_text]))
            if section_map_words and src.lower().endswith(".svg") and any(w in joined for w in MAP_WORDS):
                classes = set(class_attr(tag).lower().split())
                if "map-base" not in classes and not has_verified_base:
                    findings.append(
                        Finding(
                            "P0",
                            "external-map-svg-without-base-contract",
                            slide,
                            f"External SVG appears to be used as a real map without a verified map-base contract: {src}",
                            "Use an official/public map base with class=\"map-base\" or data-map-base-url and cite the exact source in assets/CREDITS.txt.",
                        )
                    )

        if section_map_words and "<canvas" in section.lower() and "data-map-type=\"schematic\"" not in section.lower():
            findings.append(
                Finding(
                    "P0",
                    "canvas-real-map-unverifiable",
                    slide,
                    "Canvas appears in a real-map slide, which cannot be source-verified by this guard.",
                    "Use a sourced map image base plus SVG/HTML overlay, or mark the canvas as a conceptual schematic and verify manually.",
                )
            )

        if section_map_words and sources and not has_verified_base:
            findings.append(
                Finding(
                    "P0",
                    "map-base-missing-credits",
                    slide,
                    "Map base appears in the slide, but assets/CREDITS.txt does not contain matching source URL/file evidence.",
                    "Add the exact map source URL/license or the local map-base filename plus source URL to assets/CREDITS.txt.",
                )
            )
    return findings


def collect_findings(html_path: Path) -> list[Finding]:
    if not html_path.is_file():
        raise FileNotFoundError(html_path)
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    cover_selectors = css_cover_selectors(html)
    background_selectors = css_background_cover_selectors(html)
    findings: list[Finding] = []
    findings.extend(check_cover_selectors(cover_selectors))
    findings.extend(check_background_cover_selectors(background_selectors))
    findings.extend(check_cover_images(html, cover_selectors))
    findings.extend(check_diagram_rendered_qa(html))
    findings.extend(check_maps(html, html_path))
    return findings


def result_from_findings(findings: list[Finding]) -> dict[str, object]:
    p0 = [f for f in findings if f.severity == "P0"]
    return {
        "qa_media_guard": "fail" if p0 else "pass",
        "p0_count": len(p0),
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
    }


def run_checks(html_path: Path) -> dict[str, object]:
    return result_from_findings(collect_findings(html_path))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    html_path = Path(args.html)
    try:
        findings = collect_findings(html_path)
    except FileNotFoundError:
        sys.stderr.write(f"ERROR: file not found: {html_path}\n")
        return 2

    p0 = [f for f in findings if f.severity == "P0"]
    result = result_from_findings(findings)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"qa-media-guard: {result['qa_media_guard']} ({len(p0)} P0, {len(findings)} total findings)")
        for f in findings:
            loc = f"slide {f.slide}" if f.slide is not None else "global"
            print(f"- {f.severity} [{f.code}] {loc}: {f.message}")
            print(f"  fix: {f.fix}")

    return 2 if p0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
