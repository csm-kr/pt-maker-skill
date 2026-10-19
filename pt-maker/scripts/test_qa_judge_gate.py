#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import qa_judge_gate as gate


SCRIPT = Path(__file__).resolve().parent / "qa_judge_gate.py"

CONFIG = {
    "criteria": [
        {"id": "impact", "name": "Impact", "weight": 40},
        {"id": "tech", "name": "Use of the required technology", "weight": 40},
        {"id": "design", "name": "Design", "weight": 20},
    ],
    "target": 8.0,
}


DECK = (
    '<html><head><link rel="stylesheet" href="deck.css"></head><body><section class="slide">'
    '<span class="fact" data-fact="trials">35</span><img src="assets/img/shot.jpg" alt=""></section></body></html>'
)


def ledger() -> dict:
    return {
        "round": 2,
        "artifacts": {"slides_dir": "slides", "pdf": "deck.pdf", "deck": "deck.html", "deck_hash": ""},
        "criteria": [
            {"id": "impact", "name": "Impact", "weight": 40, "reviewer": "judge-impact-r2", "blind": True, "score": 8.5, "p0": [], "top_fixes": ["Lead with the result"]},
            {"id": "tech", "name": "Use of the required technology", "weight": 40, "reviewer": "judge-tech-r2", "blind": True, "score": 8.0, "p0": [], "top_fixes": []},
            {"id": "design", "name": "Design", "weight": 20, "reviewer": "judge-design-r2", "blind": True, "score": 9.0, "p0": [], "top_fixes": ["Fewer words on 07"]},
        ],
        "fact_check": {"reviewer": "fact-check-r2", "blind": True, "facts_checked": 24, "mismatches": [], "p0": []},
    }


class JudgeGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "slides").mkdir()
        (self.root / "slides" / "01.png").write_bytes(b"png")
        (self.root / "deck.pdf").write_bytes(b"%PDF")
        (self.root / "deck.html").write_text(DECK, encoding="utf-8")
        (self.root / "deck.css").write_text("@font-face { src: url('assets/fonts/body.woff2'); }", encoding="utf-8")
        (self.root / "assets" / "img").mkdir(parents=True)
        (self.root / "assets" / "fonts").mkdir(parents=True)
        (self.root / "assets" / "img" / "shot.jpg").write_bytes(b"jpg-1")
        (self.root / "assets" / "fonts" / "body.woff2").write_bytes(b"font-1")
        self.path = self.root / "judge_ledger.json"
        self.fresh = gate.deck_hash(self.root / "deck.html")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def validate(self, data: dict, *, min_score: float | None = None, config: dict | None = None) -> dict:
        if data.get("artifacts", {}).get("deck_hash") == "":
            data["artifacts"]["deck_hash"] = self.fresh
        self.path.write_text(json.dumps(data), encoding="utf-8")
        return gate.validate(self.path, min_score=min_score, config=config)

    def codes(self, result: dict) -> set[str]:
        return {error["code"] for error in result["errors"]}

    def test_complete_ledger_passes(self):
        result = self.validate(ledger(), config=CONFIG)
        self.assertEqual(result["qa_judge_gate"], "pass", result["errors"])
        self.assertAlmostEqual(result["weighted_score"], 8.4)
        self.assertEqual(result["p0_count"], 0)

    def test_weights_must_sum_to_100(self):
        data = ledger()
        data["criteria"][2]["weight"] = 10
        self.assertIn("weights-not-100", self.codes(self.validate(data)))

    def test_reviewers_are_distinct_and_blind(self):
        data = ledger()
        data["criteria"][1]["reviewer"] = "judge-impact-r2"
        data["criteria"][2]["blind"] = False
        data["fact_check"]["reviewer"] = "judge-design-r2"
        codes = self.codes(self.validate(data))
        self.assertIn("reviewer-not-distinct", codes)
        self.assertIn("criterion-not-blind", codes)

    def test_open_p0_and_fact_mismatch_fail(self):
        data = ledger()
        data["criteria"][0]["p0"] = ["Slide 05 claims a number with no source"]
        data["fact_check"]["mismatches"] = ["06: 2.5 s on the slide vs 2,450 ms in the ledger"]
        result = self.validate(data)
        self.assertIn("p0-open", self.codes(result))
        self.assertIn("fact-check-mismatches", self.codes(result))
        self.assertEqual(result["p0_count"], 2)

    def test_fact_check_must_be_present(self):
        data = ledger()
        del data["fact_check"]
        self.assertIn("fact-check-missing", self.codes(self.validate(data)))

    def test_weighted_score_against_minimum(self):
        data = copy.deepcopy(ledger())
        for criterion in data["criteria"]:
            criterion["score"] = 7.0
        self.assertIn("weighted-below-min", self.codes(self.validate(data)))
        self.assertEqual(self.validate(data, min_score=6.5)["qa_judge_gate"], "pass")

    def test_a_changed_deck_or_any_file_it_uses_makes_the_ledger_stale(self):
        self.assertEqual(self.validate(ledger())["qa_judge_gate"], "pass")
        for path, content in (
            ("deck.css", "@font-face { src: url('assets/fonts/body.woff2'); } h1 { color: red; }"),
            ("assets/img/shot.jpg", "jpg-2"),
            ("assets/fonts/body.woff2", "font-2"),
            ("deck.html", DECK.replace("35", "36")),
        ):
            with self.subTest(path=path):
                original = (self.root / path).read_text(encoding="utf-8")
                (self.root / path).write_text(content, encoding="utf-8")
                self.assertIn("ledger-stale", self.codes(self.validate(ledger())))
                (self.root / path).write_text(original, encoding="utf-8")

    def test_fact_check_may_find_nothing_when_the_deck_has_no_facts(self):
        data = ledger()
        data["fact_check"]["facts_checked"] = 0
        self.assertIn("fact-check-empty", self.codes(self.validate(data)))
        plain = "<html><body><section class=\"slide\"><p>No numbers.</p></section></body></html>"
        (self.root / "deck.html").write_text(plain, encoding="utf-8")
        data["artifacts"]["deck_hash"] = gate.deck_hash(self.root / "deck.html")
        self.assertEqual(self.validate(data)["qa_judge_gate"], "pass", self.validate(data)["errors"])

    def test_scores_and_artifacts_are_checked(self):
        data = ledger()
        data["criteria"][0]["score"] = 11
        data["artifacts"]["pdf"] = "missing.pdf"
        codes = self.codes(self.validate(data))
        self.assertIn("criterion-score-invalid", codes)
        self.assertIn("artifact-missing", codes)

    def test_criteria_must_match_the_config(self):
        config = copy.deepcopy(CONFIG)
        config["criteria"][0]["weight"] = 50
        config["criteria"][2]["weight"] = 10
        self.assertIn("criteria-not-from-config", self.codes(self.validate(ledger(), config=config)))

    def test_print_template_starts_failing(self):
        template = gate.template_for(CONFIG, self.root / "deck.html")
        self.assertEqual(template["artifacts"]["deck_hash"], self.fresh)
        self.assertEqual([c["id"] for c in template["criteria"]], ["impact", "tech", "design"])
        self.assertTrue(all(c["score"] == 0 and c["blind"] is False and c["reviewer"] == "" for c in template["criteria"]))
        self.assertEqual(self.validate(template)["qa_judge_gate"], "fail")

    def test_cli(self):
        data = ledger()
        data["artifacts"]["deck_hash"] = self.fresh
        self.path.write_text(json.dumps(data), encoding="utf-8")
        passed = subprocess.run([sys.executable, str(SCRIPT), str(self.path), "--min", "8.0"], capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stdout)
        self.assertIn("qa-judge-gate: pass", passed.stdout)
        config = self.root / "judged.json"
        config.write_text(json.dumps(CONFIG), encoding="utf-8")
        printed = subprocess.run([sys.executable, str(SCRIPT), "--print-template", str(config)], capture_output=True, text=True)
        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertEqual(len(json.loads(printed.stdout)["criteria"]), 3)


if __name__ == "__main__":
    unittest.main()
