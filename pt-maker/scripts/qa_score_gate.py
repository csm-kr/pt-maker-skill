#!/usr/bin/env python3
"""Final pt-maker QA score gate.

This script blocks a deck from claiming a passing rubric score unless the full
rendered QA checklist has evidence. It is intentionally stricter than
qa_media_guard.py:

- qa_media_guard.py catches risky source patterns before export.
- qa_score_gate.py validates the final QA ledger after PDF/contact-sheet render.

Usage:
  python scripts/qa_score_gate.py deck.html qa_ledger.json
  python scripts/qa_score_gate.py deck.html qa_ledger.json --json
  python scripts/qa_score_gate.py deck.html --print-template
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import qa_media_guard as media
import qa_html_guard as html_guard


PASS_VALUES = {"pass", "passed", "ok", "true", "yes", "y", "완료", "통과"}

REQUIRED_CHECKLIST_KEYS = [
    "purpose_audience_context",
    "claim_headlines",
    "one_idea_per_slide",
    "visual_material_relevance",
    "visual_hierarchy",
    "design_token_consistency",
    "text_fit_wrapping",
    "korean_line_breaks",
    "layout_alignment",
    "safe_area_footer",
    "diagram_marker_accuracy",
    "image_subject_integrity",
    "contrast_readability",
    "motion_purposeful",
    "continuity_seams",
    "reduced_motion_accessibility",
    "interactive_navigation",
    "html_guard_result",
    "pdf_export_page_order",
    "contact_sheet_regression",
]

RUBRIC_WEIGHTS = {
    "narrative_audience": 18,
    "visual_system": 14,
    "layout_typography": 18,
    "visual_evidence": 14,
    "motion_continuity": 14,
    "interaction_accessibility": 10,
    "technical_delivery": 12,
}

REQUIRED_FULL_SIZE_BUCKETS = [
    "cover",
    "final",
    "diagrams_svgs_timelines",
]

REQUIRED_DIAGRAM_CHECKS = [
    "full_size_reviewed",
    "connector_endpoints",
    "labels_clear",
    "no_collisions",
    "layout_alignment",
]


def is_pass(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in PASS_VALUES
    return False


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("QA ledger must be a JSON object")
    return data


def number_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace("%", ""))
        except ValueError:
            return None
    return None


def pages_from(value: Any) -> set[int]:
    pages: set[int] = set()
    if value is None:
        return pages
    if isinstance(value, dict):
        for nested in value.values():
            pages.update(pages_from(nested))
        return pages
    if isinstance(value, (list, tuple, set)):
        for item in value:
            pages.update(pages_from(item))
        return pages
    if isinstance(value, int) and not isinstance(value, bool):
        pages.add(value)
        return pages
    if isinstance(value, str):
        for match in re.findall(r"\d{1,3}", value):
            pages.add(int(match))
    return pages


def resolve_artifact(path_value: Any, base_dir: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value.strip():
        return None
    path = Path(path_value.strip())
    if not path.is_absolute():
        path = base_dir / path
    return path


def detect_custom_diagrams(html: str) -> list[dict[str, Any]]:
    diagrams: list[dict[str, Any]] = []
    seen: set[tuple[int, str, str]] = set()
    for idx, section in enumerate(media.SECTION_RE.findall(html), start=1):
        slide = media.section_number(section, idx)

        for svg in media.SVG_RE.findall(section):
            if not media.svg_is_likely_custom_diagram(svg):
                continue
            tag = media.opening_tag(svg)
            a = media.attrs(tag)
            name = a.get("aria-label") or media.class_attr(tag) or "inline SVG diagram"
            key = (slide, "svg", name)
            if key in seen:
                continue
            seen.add(key)
            diagrams.append(
                {
                    "slide": slide,
                    "kind": "svg",
                    "name": name,
                    "has_required_qa_attrs": media.has_required_diagram_qa(svg),
                }
            )

        for tag in media.TAG_RE.findall(section):
            if not media.tag_is_css_diagram_container(tag):
                continue
            name = media.class_attr(tag) or "CSS diagram container"
            key = (slide, "css-html", name)
            if key in seen:
                continue
            seen.add(key)
            diagrams.append(
                {
                    "slide": slide,
                    "kind": "css-html",
                    "name": name,
                    "has_required_qa_attrs": media.has_required_diagram_qa(tag),
                }
            )
    return diagrams


def template_for(html_path: Path) -> dict[str, Any]:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    html_result = html_guard.run_checks(html_path)
    media_result = media.run_checks(html_path)
    diagrams = detect_custom_diagrams(html)
    diagram_slides = sorted({int(d["slide"]) for d in diagrams})
    return {
        "pt_qa_result": "pending",
        "score": 0,
        "p0_count": html_result["p0_count"] + media_result["p0_count"],
        "p2_count": html_result["p2_count"],
        "html_guard_result": html_result["html_guard_result"],
        "html_guard_p0_count": html_result["p0_count"],
        "media_guard_result": media_result["qa_media_guard"],
        "media_guard_p0_count": media_result["p0_count"],
        "rendered_pdf": False,
        "contact_sheet_reviewed": False,
        "regression_check": "pending",
        "artifacts": {
            "html": str(html_path),
            "pdf": "",
            "contact_sheet": "",
            "full_size_png_dir": "",
        },
        "full_size_pages_reviewed": {
            "cover": [],
            "section_openers": [],
            "person_photo_led": [],
            "real_maps": [],
            "diagrams_svgs_timelines": diagram_slides,
            "activities_quizzes": [],
            "final": [],
        },
        "checklist": {key: "pending" for key in REQUIRED_CHECKLIST_KEYS},
        "rubric": {
            key: {
                "score": 0,
                "max": weight,
                "notes": "",
            }
            for key, weight in RUBRIC_WEIGHTS.items()
        },
        "diagram_checks": [
            {
                "slide": d["slide"],
                "name": d["name"],
                "full_size_reviewed": False,
                "connector_endpoints": "pending",
                "labels_clear": "pending",
                "no_collisions": "pending",
                "layout_alignment": "pending",
            }
            for d in diagrams
        ],
        "notes": "Fill this ledger only after inspecting the rendered PDF/contact sheet and full-size PNGs.",
    }


def validate(html_path: Path, ledger_path: Path, min_score: int) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    html = html_path.read_text(encoding="utf-8", errors="ignore")
    html_result = html_guard.run_checks(html_path)
    media_result = media.run_checks(html_path)
    diagrams = detect_custom_diagrams(html)
    diagram_slides = sorted({int(d["slide"]) for d in diagrams})

    try:
        ledger = load_json(ledger_path)
    except Exception as exc:
        return {
            "qa_score_gate": "fail",
            "error_count": 1,
            "errors": [
                {
                    "code": "ledger-invalid-json",
                    "message": f"Could not read QA ledger JSON: {exc}",
                    "fix": "Create a valid qa_ledger.json using --print-template and fill it after rendered QA.",
                }
            ],
        }

    def add_error(code: str, message: str, fix: str) -> None:
        errors.append({"code": code, "message": message, "fix": fix})

    if media_result["p0_count"]:
        add_error(
            "media-guard-p0",
            f"qa_media_guard.py still reports {media_result['p0_count']} P0 finding(s).",
            "Fix all media guard P0 findings before scoring the deck.",
        )

    if html_result["p0_count"]:
        add_error(
            "html-guard-p0",
            f"qa_html_guard.py still reports {html_result['p0_count']} P0 finding(s).",
            "Fix all HTML guard P0 findings before scoring the deck.",
        )

    score = number_value(ledger.get("score"))
    if score is None or score < min_score or score > 100:
        add_error(
            "score-not-passable",
            f"Score must be numeric and between {min_score} and 100 for a pass; got {ledger.get('score')!r}.",
            "Do not claim a passing score until every required checklist item is rendered-verified.",
        )

    if not is_pass(ledger.get("pt_qa_result")):
        add_error(
            "qa-result-not-pass",
            "pt_qa_result is not pass.",
            "Set pt_qa_result to pass only after all P0 fixes, rerender, contact-sheet review, full-size page review, and regression review are complete.",
        )

    p0_count = number_value(ledger.get("p0_count"))
    if p0_count is None or p0_count != 0:
        add_error(
            "ledger-p0-not-zero",
            f"p0_count must be 0; got {ledger.get('p0_count')!r}.",
            "Fix all P0 findings and rerun the QA loop before scoring.",
        )

    if not is_pass(ledger.get("media_guard_result")) or number_value(ledger.get("media_guard_p0_count")) != 0:
        add_error(
            "ledger-media-guard-not-pass",
            "Ledger does not record media_guard_result=pass and media_guard_p0_count=0.",
            "Run qa_media_guard.py on the exact final HTML and update the ledger only after it passes.",
        )

    if not is_pass(ledger.get("html_guard_result")) or number_value(ledger.get("html_guard_p0_count")) != 0:
        add_error(
            "ledger-html-guard-not-pass",
            "Ledger does not record html_guard_result=pass and html_guard_p0_count=0.",
            "Run qa_html_guard.py on the exact final HTML and update the ledger only after it passes.",
        )

    rubric = ledger.get("rubric")
    if not isinstance(rubric, dict):
        add_error(
            "rubric-missing",
            "rubric object is missing from the QA ledger.",
            "Score every category in reference/html-quality-rubric.md after rendered review.",
        )
        rubric = {}

    rubric_total = 0.0
    for key, expected_max in RUBRIC_WEIGHTS.items():
        entry = rubric.get(key)
        if not isinstance(entry, dict):
            add_error(
                f"rubric-{key}-missing",
                f"rubric.{key} is missing.",
                "Add a score, max, and rendered-evidence note for every rubric category.",
            )
            continue
        category_score = number_value(entry.get("score"))
        category_max = number_value(entry.get("max"))
        notes = entry.get("notes")
        if category_max != expected_max:
            add_error(
                f"rubric-{key}-max-invalid",
                f"rubric.{key}.max must be {expected_max}; got {entry.get('max')!r}.",
                "Use the fixed weights from reference/html-quality-rubric.md.",
            )
        if category_score is None or category_score < 0 or category_score > expected_max:
            add_error(
                f"rubric-{key}-score-invalid",
                f"rubric.{key}.score must be between 0 and {expected_max}; got {entry.get('score')!r}.",
                "Set the category score only after checking its rendered evidence.",
            )
        else:
            rubric_total += category_score
        if not isinstance(notes, str) or len(notes.strip()) < 8:
            add_error(
                f"rubric-{key}-notes-missing",
                f"rubric.{key}.notes lacks concrete rendered evidence.",
                "Record a short page-specific or artifact-specific reason for the score.",
            )

    if score is not None and abs(rubric_total - score) > 0.001:
        add_error(
            "rubric-total-mismatch",
            f"Rubric category total {rubric_total:g} does not equal top-level score {score:g}.",
            "Make the top-level score equal the sum of the seven fixed-weight rubric categories.",
        )

    for field in ("rendered_pdf", "contact_sheet_reviewed"):
        if not is_pass(ledger.get(field)):
            add_error(
                f"{field}-missing",
                f"{field} must be true/pass.",
                "Render the final PDF/contact sheet from the exact final HTML before scoring.",
            )

    if not is_pass(ledger.get("regression_check")):
        add_error(
            "regression-check-not-pass",
            "regression_check is not pass.",
            "Inspect the full new contact sheet after the latest fix and record regression_check=pass only if no new issue appears.",
        )

    base_dir = ledger_path.parent
    artifacts = ledger.get("artifacts")
    if not isinstance(artifacts, dict):
        add_error(
            "artifacts-missing",
            "artifacts object is missing from the QA ledger.",
            "Record final html, pdf, contact_sheet, and full_size_png_dir paths in artifacts.",
        )
        artifacts = {}

    for key in ("pdf", "contact_sheet", "full_size_png_dir"):
        artifact_path = resolve_artifact(artifacts.get(key), base_dir)
        if artifact_path is None:
            add_error(
                f"artifact-{key}-missing",
                f"artifacts.{key} is missing.",
                f"Add artifacts.{key} to the QA ledger.",
            )
            continue
        if not artifact_path.exists():
            add_error(
                f"artifact-{key}-not-found",
                f"artifacts.{key} does not exist: {artifact_path}",
                "Generate the artifact from the exact final source and update the path.",
            )
            continue
        if key == "full_size_png_dir" and not any(artifact_path.glob("*.png")):
            add_error(
                "artifact-full-size-png-dir-empty",
                f"artifacts.full_size_png_dir has no PNG files: {artifact_path}",
                "Export full-size PNGs for required pages and point full_size_png_dir to that folder.",
            )

    full_size = ledger.get("full_size_pages_reviewed")
    if not isinstance(full_size, dict):
        add_error(
            "full-size-pages-missing",
            "full_size_pages_reviewed object is missing.",
            "Record reviewed page numbers for cover, final, and required diagram/SVG/timeline pages.",
        )
        full_size = {}

    for bucket in REQUIRED_FULL_SIZE_BUCKETS:
        pages = pages_from(full_size.get(bucket))
        if bucket == "diagrams_svgs_timelines" and not diagram_slides:
            continue
        if not pages:
            add_error(
                f"full-size-{bucket}-missing",
                f"full_size_pages_reviewed.{bucket} is empty.",
                f"Export and inspect full-size PNGs for {bucket}, then record the page numbers.",
            )

    reviewed_diagram_pages = pages_from(full_size.get("diagrams_svgs_timelines"))
    missing_diagram_pages = [p for p in diagram_slides if p not in reviewed_diagram_pages]
    if missing_diagram_pages:
        add_error(
            "diagram-pages-not-full-size-reviewed",
            f"Custom diagram slide(s) not listed under full_size_pages_reviewed.diagrams_svgs_timelines: {missing_diagram_pages}",
            "Export each custom diagram slide as a full-size PNG, inspect it, and record the slide/page numbers.",
        )

    for diagram in diagrams:
        if not diagram["has_required_qa_attrs"]:
            add_error(
                "diagram-missing-source-qa-attrs",
                f"Diagram on slide {diagram['slide']} lacks data-fullsize-qa and data-rendered-qa: {diagram['name']}",
                "Add both attributes only after inspecting the full-size rendered page for connector endpoints, labels, collisions, and alignment.",
            )

    checklist = ledger.get("checklist")
    if not isinstance(checklist, dict):
        add_error(
            "checklist-missing",
            "checklist object is missing from the QA ledger.",
            "Create checklist entries and mark each required item pass only after rendered QA.",
        )
        checklist = {}

    for key in REQUIRED_CHECKLIST_KEYS:
        if not is_pass(checklist.get(key)):
            add_error(
                f"checklist-{key}-not-pass",
                f"checklist.{key} is not pass.",
                "Do not raise the rubric score until every required checklist item is pass.",
            )

    diagram_checks = ledger.get("diagram_checks")
    if diagram_slides and not isinstance(diagram_checks, list):
        add_error(
            "diagram-checks-missing",
            "diagram_checks list is missing even though the deck contains custom diagrams.",
            "Add one diagram_checks entry per custom diagram slide.",
        )
        diagram_checks = []
    elif not isinstance(diagram_checks, list):
        diagram_checks = []

    for slide in diagram_slides:
        entries = [entry for entry in diagram_checks if isinstance(entry, dict) and slide in pages_from(entry.get("slide"))]
        if not entries:
            add_error(
                "diagram-check-slide-missing",
                f"diagram_checks has no entry for slide {slide}.",
                "Record a diagram_checks entry for every custom diagram slide.",
            )
            continue
        for required_key in REQUIRED_DIAGRAM_CHECKS:
            if not any(is_pass(entry.get(required_key)) for entry in entries):
                add_error(
                    f"diagram-check-{required_key}-not-pass",
                    f"diagram_checks for slide {slide} does not pass {required_key}.",
                    "Inspect the full-size rendered diagram and fix or record pass for every diagram criterion.",
                )

    return {
        "qa_score_gate": "fail" if errors else "pass",
        "error_count": len(errors),
        "score": score,
        "min_score": min_score,
        "detected_custom_diagrams": diagrams,
        "html_guard": html_result,
        "media_guard": media_result,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("ledger", nargs="?")
    ap.add_argument("--min-score", type=int, default=90)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--print-template", action="store_true")
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.is_file():
        sys.stderr.write(f"ERROR: file not found: {html_path}\n")
        return 2

    if args.print_template:
        print(json.dumps(template_for(html_path), ensure_ascii=False, indent=2))
        return 0

    if not args.ledger:
        sys.stderr.write("ERROR: qa ledger path is required unless --print-template is used\n")
        return 2

    ledger_path = Path(args.ledger)
    if not ledger_path.is_file():
        sys.stderr.write(f"ERROR: file not found: {ledger_path}\n")
        return 2

    result = validate(html_path, ledger_path, args.min_score)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"qa-score-gate: {result['qa_score_gate']} ({result['error_count']} blocking issue(s))")
        for err in result["errors"]:
            print(f"- P0 [{err['code']}]: {err['message']}")
            print(f"  fix: {err['fix']}")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
