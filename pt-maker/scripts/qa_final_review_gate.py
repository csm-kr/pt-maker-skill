#!/usr/bin/env python3
"""Final user-review gate for pt-maker decks.

qa_score_gate.py proves that rendered QA passed. This script proves the deck
also went through the final user-review step before final delivery:

- the passed HTML/PDF candidate was reported to the user
- user review was accepted or requested changes were resolved
- the deck was rechecked after user review
- taste-profile updates were explicitly reviewed with the user

Usage:
  python scripts/qa_final_review_gate.py deck.html qa_ledger.json user_review_ledger.json
  python scripts/qa_final_review_gate.py deck.html qa_ledger.json user_review_ledger.json --json
  python scripts/qa_final_review_gate.py deck.html qa_ledger.json --print-template
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import qa_score_gate as score_gate


PASS_REVIEW_STATUSES = {
    "accepted",
    "approved",
    "no_changes",
    "changes_requested_resolved",
}

PROFILE_DECISIONS = {
    "accepted",
    "declined",
    "not_applicable",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("User review ledger must be a JSON object")
    return data


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def is_pass(value: Any) -> bool:
    return score_gate.is_pass(value)


def profile_path_exists(path_value: Any, ledger_dir: Path) -> bool:
    if not isinstance(path_value, str) or not path_value.strip():
        return False

    raw = Path(path_value.strip())
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend(
            [
                ledger_dir / raw,
                Path.cwd() / raw,
                Path(__file__).resolve().parents[1] / raw.name,
                Path(__file__).resolve().parents[1] / raw,
            ]
        )
    return any(path.is_file() for path in candidates)


def template_for(html_path: Path, qa_ledger_path: Path) -> dict[str, Any]:
    return {
        "pt_final_review_result": "pass",
        "reviewed_candidate_version": html_path.stem,
        "user_review_reported": True,
        "user_review_status": "accepted",
        "user_feedback_summary": "User accepted the QA-passed HTML/PDF candidate with no further changes.",
        "final_artifacts_confirmed": True,
        "post_user_review_recheck": True,
        "changes_requested": [],
        "changes_applied": [],
        "rerendered_after_user_review": False,
        "qa_score_gate_rerun_after_user_review": True,
        "qa_ledger": str(qa_ledger_path),
        "profile_update": {
            "reviewed_with_user": True,
            "decision": "not_applicable",
            "profile_diff_summary": "",
            "profile_files_updated": [],
            "profile_version_incremented": False,
            "reason": "No reusable taste-profile learning was confirmed by the user.",
        },
        "notes": "Fill this only after the user reviews the QA-passed candidate.",
    }


def validate(html_path: Path, qa_ledger_path: Path, review_ledger_path: Path, min_score: int) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    def add_error(code: str, message: str, fix: str) -> None:
        errors.append({"code": code, "message": message, "fix": fix})

    score_result = score_gate.validate(html_path, qa_ledger_path, min_score)
    if score_result.get("errors"):
        add_error(
            "qa-score-gate-not-pass",
            f"qa_score_gate.py has {len(score_result['errors'])} blocking issue(s).",
            "Rerun and pass qa_score_gate.py on the exact final HTML/PDF QA ledger before final user-review delivery.",
        )

    try:
        ledger = load_json(review_ledger_path)
    except Exception as exc:
        return {
            "qa_final_review_gate": "fail",
            "error_count": 1,
            "score_gate": score_result,
            "errors": [
                {
                    "code": "user-review-ledger-invalid-json",
                    "message": f"Could not read user review ledger JSON: {exc}",
                    "fix": "Create a valid user_review_ledger.json using --print-template after the user review step.",
                }
            ],
        }

    if not is_pass(ledger.get("pt_final_review_result")):
        add_error(
            "final-review-result-not-pass",
            "pt_final_review_result is not pass.",
            "Do not mark final delivery until user review, recheck, and profile-update decision are complete.",
        )

    if not has_text(ledger.get("reviewed_candidate_version")):
        add_error(
            "reviewed-candidate-version-missing",
            "reviewed_candidate_version is missing.",
            "Record the exact HTML/PDF candidate version that was shown to the user.",
        )

    if not is_pass(ledger.get("user_review_reported")):
        add_error(
            "user-review-not-reported",
            "user_review_reported must be true/pass.",
            "Report the QA result plus HTML/PDF candidate to the user before final delivery.",
        )

    status = str(ledger.get("user_review_status", "")).strip().lower()
    if status not in PASS_REVIEW_STATUSES:
        add_error(
            "user-review-status-not-final",
            f"user_review_status must be one of {sorted(PASS_REVIEW_STATUSES)}; got {ledger.get('user_review_status')!r}.",
            "Finish the user review loop first. If changes were requested, apply them, rerender, and rerun QA.",
        )

    if not has_text(ledger.get("user_feedback_summary")):
        add_error(
            "user-feedback-summary-missing",
            "user_feedback_summary is missing.",
            "Summarize the user's approval or requested changes in the final review ledger.",
        )

    if not is_pass(ledger.get("final_artifacts_confirmed")):
        add_error(
            "final-artifacts-not-confirmed",
            "final_artifacts_confirmed must be true/pass.",
            "Confirm the final HTML/PDF paths after user review and before delivery.",
        )

    if not is_pass(ledger.get("post_user_review_recheck")):
        add_error(
            "post-user-review-recheck-missing",
            "post_user_review_recheck must be true/pass.",
            "Re-inspect the rendered final candidate after user review, even when the user approved with no changes.",
        )

    if not is_pass(ledger.get("qa_score_gate_rerun_after_user_review")):
        add_error(
            "score-gate-not-rerun-after-user-review",
            "qa_score_gate_rerun_after_user_review must be true/pass.",
            "Run qa_score_gate.py after the user-review state is final.",
        )

    if status == "changes_requested_resolved":
        if not has_list(ledger.get("changes_requested")):
            add_error(
                "changes-requested-missing",
                "changes_requested must list the user's requested changes.",
                "Record the user's requested changes before marking them resolved.",
            )
        if not has_list(ledger.get("changes_applied")):
            add_error(
                "changes-applied-missing",
                "changes_applied must list what was changed.",
                "Record the applied fixes and affected pages/slides.",
            )
        if not is_pass(ledger.get("rerendered_after_user_review")):
            add_error(
                "rerender-after-user-review-missing",
                "rerendered_after_user_review must be true/pass when changes were requested.",
                "Rerender the PDF/contact sheet after user-requested edits.",
            )

    profile = ledger.get("profile_update")
    if not isinstance(profile, dict):
        add_error(
            "profile-update-missing",
            "profile_update object is missing.",
            "Record whether user review produced a confirmed taste-profile update.",
        )
        profile = {}

    if not is_pass(profile.get("reviewed_with_user")):
        add_error(
            "profile-update-not-reviewed-with-user",
            "profile_update.reviewed_with_user must be true/pass.",
            "Propose the taste-profile diff to the user and record the user's decision.",
        )

    decision = str(profile.get("decision", "")).strip().lower()
    if decision not in PROFILE_DECISIONS:
        add_error(
            "profile-update-decision-invalid",
            f"profile_update.decision must be one of {sorted(PROFILE_DECISIONS)}; got {profile.get('decision')!r}.",
            "Use accepted, declined, or not_applicable.",
        )
    elif decision == "accepted":
        files = profile.get("profile_files_updated")
        if not has_list(files):
            add_error(
                "profile-files-updated-missing",
                "profile_update.profile_files_updated must list updated profile file(s).",
                "Update taste-profile.md and/or dark-taste-profile.md after user confirmation and record the file path(s).",
            )
            files = []
        if not has_text(profile.get("profile_diff_summary")):
            add_error(
                "profile-diff-summary-missing",
                "profile_update.profile_diff_summary is missing.",
                "Summarize the user-approved taste-profile diff.",
            )
        if not is_pass(profile.get("profile_version_incremented")):
            add_error(
                "profile-version-not-incremented",
                "profile_update.profile_version_incremented must be true/pass when profile changes are accepted.",
                "Increment the profile version after applying the confirmed review learning.",
            )
        for path_value in files:
            if not profile_path_exists(path_value, review_ledger_path.parent):
                add_error(
                    "profile-file-not-found",
                    f"Updated profile file was not found: {path_value!r}.",
                    "Record an existing taste-profile.md or dark-taste-profile.md path.",
                )
    elif decision in {"declined", "not_applicable"} and not has_text(profile.get("reason")):
        add_error(
            "profile-update-reason-missing",
            "profile_update.reason is required when the profile was declined or not applicable.",
            "Record why no profile file was updated.",
        )

    return {
        "qa_final_review_gate": "fail" if errors else "pass",
        "error_count": len(errors),
        "score_gate": score_result,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("qa_ledger")
    ap.add_argument("user_review_ledger", nargs="?")
    ap.add_argument("--min-score", type=int, default=90)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--print-template", action="store_true")
    args = ap.parse_args()

    html_path = Path(args.html)
    qa_ledger_path = Path(args.qa_ledger)

    if not html_path.is_file():
        sys.stderr.write(f"ERROR: file not found: {html_path}\n")
        return 2
    if not qa_ledger_path.is_file():
        sys.stderr.write(f"ERROR: file not found: {qa_ledger_path}\n")
        return 2

    if args.print_template:
        print(json.dumps(template_for(html_path, qa_ledger_path), ensure_ascii=False, indent=2))
        return 0

    if not args.user_review_ledger:
        sys.stderr.write("ERROR: user review ledger path is required unless --print-template is used\n")
        return 2

    review_ledger_path = Path(args.user_review_ledger)
    if not review_ledger_path.is_file():
        sys.stderr.write(f"ERROR: file not found: {review_ledger_path}\n")
        return 2

    result = validate(html_path, qa_ledger_path, review_ledger_path, args.min_score)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"qa-final-review-gate: {result['qa_final_review_gate']} ({result['error_count']} blocking issue(s))")
        for err in result["errors"]:
            print(f"- P0 [{err['code']}]: {err['message']}")
            print(f"  fix: {err['fix']}")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
