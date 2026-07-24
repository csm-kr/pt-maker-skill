#!/usr/bin/env python3
"""Rubric gate for pt-maker HyperFrames animation mode.

The ledger is intentionally safe by default: pending, zero points, no approval.
It may pass only after static guard, HyperFrames check/snapshots, browser preview,
and a human review of the timed composition.

Usage:
  python3 qa_animation_score_gate.py animation/index.html --print-template
  python3 qa_animation_score_gate.py animation/index.html animation_qa_ledger.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import qa_animation_guard


PASS_VALUES = {"pass", "passed", "ok", "true", "yes", "y", "완료", "통과"}

RUBRIC_WEIGHTS = {
    "narrative_claims": 16,
    "frame_design": 14,
    "motion_craft": 20,
    "seam_continuity": 14,
    "timing_readability": 12,
    "accessibility_safe_content": 8,
    "technical_determinism": 16,
}

REQUIRED_CHECKLIST = [
    "one_claim_per_scene",
    "evidence_matches_claim",
    "dominant_visual_per_scene",
    "static_end_states_complete",
    "motion_has_purpose",
    "transition_vocabulary_limited",
    "exit_entry_vectors_reviewed",
    "reading_time_sufficient",
    "safe_area_no_collisions",
    "image_identity_continuity",
    "no_infinite_or_wall_clock_motion",
    "motion_assertions_pass",
    "hero_snapshots_reviewed",
    "full_timeline_previewed",
    "audio_media_rights_checked",
]


def is_pass(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in PASS_VALUES
    return False


def number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def resolve_artifact(value: Any, base: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value.strip())
    return path if path.is_absolute() else base / path


def template_for(html_path: Path) -> dict[str, Any]:
    guard = qa_animation_guard.run_checks(html_path)
    return {
        "animation_qa_result": "pending",
        "score": 0,
        "p0_count": guard["p0_count"],
        "animation_guard_result": guard["animation_guard_result"],
        "hyperframes_lint_result": "pending",
        "hyperframes_check_result": "pending",
        "motion_assertions_result": "pending",
        "snapshots_reviewed": False,
        "preview_reviewed": False,
        "user_render_approved": False,
        "artifacts": {
            "html": str(html_path),
            "motion_sidecar": str(html_path.with_suffix(".motion.json")),
            "hyperframes_check_report": "",
            "snapshot_dir": "",
            "preview_review_notes": "",
            "render": "",
        },
        "checklist": {key: "pending" for key in REQUIRED_CHECKLIST},
        "rubric": {
            key: {"score": 0, "max": weight, "notes": ""}
            for key, weight in RUBRIC_WEIGHTS.items()
        },
        "notes": (
            "Fill only after HyperFrames check --snapshots and a complete browser "
            "preview. Render approval must come from the user."
        ),
    }


def error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def validate(
    html_path: Path,
    ledger_path: Path,
    min_score: int = 90,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    guard = qa_animation_guard.run_checks(html_path)
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {
            "animation_score_gate": "fail",
            "score": 0,
            "error_count": 1,
            "errors": [error("ledger-invalid", f"Could not read ledger: {exc}")],
        }
    if not isinstance(ledger, dict):
        return {
            "animation_score_gate": "fail",
            "score": 0,
            "error_count": 1,
            "errors": [error("ledger-invalid", "Ledger must be a JSON object.")],
        }

    if guard["animation_guard_result"] != "pass":
        errors.append(error("animation-guard-failed", "Static animation guard has P0 findings."))
    if not is_pass(ledger.get("animation_qa_result")):
        errors.append(error("qa-result-not-pass", "animation_qa_result must be pass."))
    if number(ledger.get("p0_count")) != 0:
        errors.append(error("p0-not-zero", "p0_count must be 0."))
    if not is_pass(ledger.get("animation_guard_result")):
        errors.append(error("guard-ledger-not-pass", "animation_guard_result must be pass."))
    for key in (
        "hyperframes_lint_result",
        "hyperframes_check_result",
        "motion_assertions_result",
    ):
        if not is_pass(ledger.get(key)):
            errors.append(error(f"{key}-not-pass", f"{key} must be pass."))
    for key in ("snapshots_reviewed", "preview_reviewed", "user_render_approved"):
        if not is_pass(ledger.get(key)):
            errors.append(error(f"{key}-missing", f"{key} must be true/pass."))

    checklist = ledger.get("checklist")
    if not isinstance(checklist, dict):
        errors.append(error("checklist-invalid", "checklist must be an object."))
    else:
        for key in REQUIRED_CHECKLIST:
            if not is_pass(checklist.get(key)):
                errors.append(error("checklist-incomplete", f"Checklist item not passed: {key}"))

    rubric = ledger.get("rubric")
    rubric_total = 0.0
    if not isinstance(rubric, dict):
        errors.append(error("rubric-invalid", "rubric must be an object."))
    else:
        for key, maximum in RUBRIC_WEIGHTS.items():
            item = rubric.get(key)
            if not isinstance(item, dict):
                errors.append(error("rubric-item-missing", f"Missing rubric item: {key}"))
                continue
            item_score = number(item.get("score"))
            item_max = number(item.get("max"))
            notes = item.get("notes")
            if item_max != maximum:
                errors.append(
                    error("rubric-max-mismatch", f"{key} max must be {maximum}.")
                )
            if item_score is None or item_score < 0 or item_score > maximum:
                errors.append(
                    error("rubric-score-invalid", f"{key} score must be 0–{maximum}.")
                )
            else:
                rubric_total += item_score
            if not isinstance(notes, str) or not notes.strip():
                errors.append(error("rubric-notes-missing", f"{key} needs review evidence."))

    declared_score = number(ledger.get("score"))
    if declared_score is None:
        errors.append(error("score-invalid", "score must be numeric."))
        declared_score = 0
    if abs(declared_score - rubric_total) > 0.001:
        errors.append(
            error(
                "rubric-total-mismatch",
                f"Declared score {declared_score:g} != rubric total {rubric_total:g}.",
            )
        )
    if rubric_total < min_score:
        errors.append(
            error("score-below-threshold", f"Animation score {rubric_total:g} < {min_score}.")
        )

    artifacts = ledger.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append(error("artifacts-invalid", "artifacts must be an object."))
    else:
        base = ledger_path.parent
        for key in ("html", "motion_sidecar", "hyperframes_check_report", "snapshot_dir"):
            artifact = resolve_artifact(artifacts.get(key), base)
            if artifact is None or not artifact.exists():
                errors.append(error("artifact-missing", f"Required artifact missing: {key}"))
        notes = artifacts.get("preview_review_notes")
        if not isinstance(notes, str) or not notes.strip():
            errors.append(
                error("preview-notes-missing", "preview_review_notes must describe the review.")
            )

    return {
        "animation_score_gate": "pass" if not errors else "fail",
        "score": rubric_total,
        "threshold": min_score,
        "error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("ledger", type=Path, nargs="?")
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--min-score", type=int, default=90)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.print_template:
        print(json.dumps(template_for(args.html.resolve()), ensure_ascii=False, indent=2))
        return 0
    if args.ledger is None:
        parser.error("ledger is required unless --print-template is used")
    result = validate(args.html.resolve(), args.ledger.resolve(), args.min_score)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"animation-score-gate: {result['animation_score_gate']} "
            f"(score={result['score']:g}, errors={result['error_count']})"
        )
        for item in result["errors"]:
            print(f"- {item['code']}: {item['message']}")
    return 0 if result["animation_score_gate"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
