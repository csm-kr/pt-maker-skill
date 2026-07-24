#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import qa_animation_score_gate


TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent / "assets" / "animation-mode"
)


class AnimationScoreGateTests(unittest.TestCase):
    def test_template_is_pending_zero_and_unapproved(self):
        ledger = qa_animation_score_gate.template_for(TEMPLATE_DIR / "index.html")
        self.assertEqual(ledger["animation_qa_result"], "pending")
        self.assertEqual(ledger["score"], 0)
        self.assertFalse(ledger["user_render_approved"])

    def test_full_evidence_passes_and_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            html = root / "index.html"
            motion = root / "index.motion.json"
            html.write_text((TEMPLATE_DIR / "index.html").read_text(), encoding="utf-8")
            shutil.copytree(TEMPLATE_DIR / "compositions", root / "compositions")
            motion.write_text(
                (TEMPLATE_DIR / "index.motion.json").read_text(),
                encoding="utf-8",
            )
            report = root / "check.json"
            report.write_text('{"ok":true}', encoding="utf-8")
            snapshots = root / "snapshots"
            snapshots.mkdir()
            (snapshots / "hero.png").write_bytes(b"png")

            ledger = qa_animation_score_gate.template_for(html)
            ledger.update(
                {
                    "animation_qa_result": "pass",
                    "score": 100,
                    "p0_count": 0,
                    "animation_guard_result": "pass",
                    "hyperframes_lint_result": "pass",
                    "hyperframes_check_result": "pass",
                    "motion_assertions_result": "pass",
                    "snapshots_reviewed": True,
                    "preview_reviewed": True,
                    "user_render_approved": True,
                }
            )
            ledger["artifacts"].update(
                {
                    "html": "index.html",
                    "motion_sidecar": "index.motion.json",
                    "hyperframes_check_report": "check.json",
                    "snapshot_dir": "snapshots",
                    "preview_review_notes": "Reviewed every scene and seam at 0.25× and 1×.",
                }
            )
            ledger["checklist"] = {
                key: "pass" for key in qa_animation_score_gate.REQUIRED_CHECKLIST
            }
            for key, weight in qa_animation_score_gate.RUBRIC_WEIGHTS.items():
                ledger["rubric"][key] = {
                    "score": weight,
                    "max": weight,
                    "notes": "Verified in snapshots and full timeline preview.",
                }
            ledger_path = root / "animation_qa_ledger.json"
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

            passed = qa_animation_score_gate.validate(html, ledger_path)
            self.assertEqual(passed["animation_score_gate"], "pass", passed["errors"])

            ledger["score"] = 99
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            failed = qa_animation_score_gate.validate(html, ledger_path)
            self.assertTrue(
                any(
                    item["code"] == "rubric-total-mismatch"
                    for item in failed["errors"]
                )
            )


if __name__ == "__main__":
    unittest.main()
