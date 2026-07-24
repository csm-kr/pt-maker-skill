#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import qa_score_gate


HTML = """<!doctype html><html><head><style>
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style></head><body><div class="reveal"><div class="slides">
<section><h1>검증 가능한 주장</h1><aside class="notes">발표 메모</aside></section>
</div></div><script>
window.addEventListener('beforeprint', function () {});
Reveal.initialize({width:1280,height:720,center:false,pdfPageHeightOffset:0});
</script></body></html>"""


class ScoreGateTests(unittest.TestCase):
    def test_print_template_starts_pending_and_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            html_path = Path(folder) / "deck.html"
            html_path.write_text(HTML, encoding="utf-8")
            ledger = qa_score_gate.template_for(html_path)
        self.assertEqual(ledger["pt_qa_result"], "pending")
        self.assertEqual(ledger["score"], 0)
        self.assertFalse(ledger["rendered_pdf"])
        self.assertTrue(all(item["score"] == 0 for item in ledger["rubric"].values()))

    def test_completed_ledger_passes_and_rubric_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            html_path = root / "deck.html"
            html_path.write_text(HTML, encoding="utf-8")
            (root / "deck.pdf").write_bytes(b"%PDF smoke")
            (root / "contact.png").write_bytes(b"png")
            frames = root / "full"
            frames.mkdir()
            (frames / "page-1.png").write_bytes(b"png")

            ledger = qa_score_gate.template_for(html_path)
            ledger.update(
                {
                    "pt_qa_result": "pass",
                    "score": 100,
                    "p0_count": 0,
                    "html_guard_result": "pass",
                    "html_guard_p0_count": 0,
                    "media_guard_result": "pass",
                    "media_guard_p0_count": 0,
                    "rendered_pdf": True,
                    "contact_sheet_reviewed": True,
                    "regression_check": "pass",
                }
            )
            ledger["artifacts"].update(
                {
                    "pdf": "deck.pdf",
                    "contact_sheet": "contact.png",
                    "full_size_png_dir": "full",
                }
            )
            ledger["full_size_pages_reviewed"]["cover"] = [1]
            ledger["full_size_pages_reviewed"]["final"] = [1]
            ledger["checklist"] = {key: "pass" for key in qa_score_gate.REQUIRED_CHECKLIST_KEYS}
            for key, weight in qa_score_gate.RUBRIC_WEIGHTS.items():
                ledger["rubric"][key] = {
                    "score": weight,
                    "max": weight,
                    "notes": "Rendered page and artifact verified.",
                }

            ledger_path = root / "qa_ledger.json"
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            passed = qa_score_gate.validate(html_path, ledger_path, 90)
            self.assertEqual(passed["qa_score_gate"], "pass")

            ledger["score"] = 99
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            failed = qa_score_gate.validate(html_path, ledger_path, 90)
            self.assertTrue(any(item["code"] == "rubric-total-mismatch" for item in failed["errors"]))


if __name__ == "__main__":
    unittest.main()
