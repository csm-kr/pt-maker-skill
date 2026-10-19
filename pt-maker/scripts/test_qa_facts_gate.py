#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import build_judged_deck
import qa_facts_gate as gate


SCRIPT = Path(__file__).resolve().parent / "qa_facts_gate.py"

FACTS = {
    "facts": [
        {"id": "trials", "value": "35", "unit": "trials", "claim": "Scripted trials completed", "source": "evidence/trials.json", "checked": "2026-10-15"},
        {"id": "latency", "value": "2,450", "unit": "ms", "claim": "Median response time", "source": "evidence/latency.json", "checked": "2026-10-15"},
        {"id": "ratio", "value": "3 in 10", "unit": "", "claim": "Survey respondents who asked for it", "source": "data/survey.csv", "checked": "2026-10-15"},
        {"id": "adopters", "value": "7", "unit": "in 100", "claim": "Pilot users who kept it on", "source": "data/pilot.csv", "checked": "2026-10-15"},
        {"id": "weekly", "value": "38", "unit": "of 100", "claim": "Respondents who would use it weekly", "source": "data/survey.csv", "checked": "2026-10-15"},
        {"id": "faults", "value": "4.2", "unit": "per 1,000 beds", "claim": "Faults reported per bed", "source": "data/survey.csv", "checked": "2026-10-15"},
    ]
}

FOOTER = '<footer class="ft"><div class="src">Checked 2026-10-15 (2026). Details: evidence/trials-v2.json</div><div class="pg"><b>03</b></div></footer>'


def fact(fact_id: str, text: str) -> str:
    return f'<span class="fact" data-fact="{fact_id}">{text}</span>'


def page(*slides: str) -> str:
    return "<!doctype html><html><head><title>Deck 2026</title><style>.a{width:12px}</style></head><body>" + "".join(slides) + "</body></html>"


class FactsGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.facts = self.root / "facts.json"
        self.facts.write_text(json.dumps(FACTS), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def check(self, html: str, config: dict | None = None) -> dict:
        deck = self.root / "deck.html"
        deck.write_text(html, encoding="utf-8")
        return gate.run_checks(deck, self.facts, config or {})

    def codes(self, result: dict) -> list[str]:
        return [error["code"] for error in result["errors"]]

    def test_tagged_facts_with_a_source_pass(self):
        result = self.check(
            page(
                f'<section class="slide" data-main><h1>{fact("trials", "35 trials")}, {fact("latency", "2,450 ms")}, '
                f'{fact("ratio", "3 in 10")}</h1>{FOOTER}</section>'
            )
        )
        self.assertEqual(result["qa_facts_gate"], "pass", result["errors"])

    def test_units_that_contain_numbers_are_part_of_the_fact(self):
        src = self.root / "deck.src.html"
        src.write_text(
            page(
                '<section class="slide" data-main><h1>{{fact:weekly}} would use it weekly.</h1>'
                "<p>Faults: {{fact:faults}}.</p>"
                '<footer class="ft"><div class="src">Survey, 2026-10. Details: data/survey.csv, p. 4, pp. 3–5, Table 2, 표 3, 12쪽</div></footer>'
                "</section>"
            ),
            encoding="utf-8",
        )
        (self.root / "deck.html").write_text(build_judged_deck.build(src, env={}).html, encoding="utf-8")
        result = gate.run_checks(self.root / "deck.html", self.facts, {})
        self.assertEqual(result["qa_facts_gate"], "pass", result["errors"])

    def test_untagged_numbers_fail_on_every_slide(self):
        main = self.check(page(f'<section class="slide" data-main><p>We saved 42 hours.</p>{FOOTER}</section>'))
        self.assertEqual(self.codes(main), ["untagged-number"])
        self.assertIn("42", main["errors"][0]["message"])
        self.assertEqual(main["errors"][0]["slide"], "03")
        appendix = self.check(page('<section class="slide"><p>Q&amp;A: 42 questions</p></section>'))
        self.assertEqual(self.codes(appendix), ["untagged-number"])

    def test_a_typed_ledger_value_still_needs_its_tag(self):
        result = self.check(page(f'<section class="slide" data-main><p>35 trials</p>{FOOTER}</section>'))
        self.assertEqual(self.codes(result), ["untagged-number"])

    def test_code_and_other_footer_numbers_are_checked(self):
        code = self.check(page(f'<section class="slide" data-main><p>Costs <code>40%</code> less.</p>{FOOTER}</section>'))
        self.assertEqual(self.codes(code), ["untagged-number"])
        footer = self.check(
            page('<section class="slide"><p>Hi</p><footer class="ft"><div class="src">n = 4,212. Details: x</div></footer></section>')
        )
        self.assertEqual(self.codes(footer), ["untagged-number"])

    def test_allowed_places(self):
        # Page numbers, template text (.nowc), explicit non-claims (.nofact), link labels, dates and years in
        # the footer source line, and letter-led identifiers such as A3, CO2 or run-7 are not quantities.
        result = self.check(
            page(
                '<section class="slide" data-main><div class="tt nowc">Step 1 of 4</div>'
                '<p>See A3, CO2 and run-7. <span class="nofact">slide 14</span> '
                '<a href="https://example.com/r2">example.com/r2 v3</a></p>'
                '<svg viewBox="0 0 10 10"><title>chart 99</title></svg>'
                '<footer class="ft"><div class="src">Read 2026-10-15 (2025 report). Details: x</div><div class="pg">05</div></footer>'
                "</section>"
            )
        )
        self.assertEqual(result["qa_facts_gate"], "pass", result["errors"])

    def test_tagged_value_must_match_its_fact(self):
        wrong = self.check(page(f'<section class="slide">{fact("trials", "99 trials")}{FOOTER}</section>'))
        self.assertEqual(self.codes(wrong), ["fact-mismatch"])
        unknown = self.check(page(f'<section class="slide">{fact("nope", "5")}{FOOTER}</section>'))
        self.assertEqual(self.codes(unknown), ["unknown-fact"])

    def test_facts_need_a_filled_footer_source(self):
        no_footer = self.check(page(f'<section class="slide"><p>{fact("trials", "35 trials")}</p></section>'))
        self.assertEqual(self.codes(no_footer), ["facts-without-source"])
        empty = self.check(page('<section class="slide"><p>Hi</p><footer class="ft"><div class="src">Details:</div></footer></section>'))
        self.assertEqual(self.codes(empty), ["empty-source"])
        korean = self.check(
            page(f'<section class="slide" data-main><p>{fact("trials", "35 trials")}</p><footer class="ft"><div class="src">출처: 실험 기록</div></footer></section>'),
            {"facts": {"source_label": "출처:"}},
        )
        self.assertEqual(korean["qa_facts_gate"], "pass", korean["errors"])

    def test_dots_must_come_from_a_fact(self):
        loose = self.check(page(f'<section class="slide"><div class="dots" role="img" aria-label="73 of 100"></div>{FOOTER}</section>'))
        self.assertEqual(self.codes(loose), ["dots-without-fact"])
        sourced = self.check(page('<section class="slide"><div class="dots" data-fact="adopters" role="img" aria-label="7 of 100"></div></section>'))
        self.assertEqual(self.codes(sourced), ["facts-without-source"])

    def test_banned_phrases_and_allowed_phrases(self):
        body = '<section class="slide"><p>The first app. First market: Korea.</p><h3 class="nowc">Any other ideas?</h3></section>'
        failed = self.check(page(body))
        self.assertEqual(self.codes(failed), ["banned-phrase", "banned-phrase"])
        allowed = self.check(page(body), {"facts": {"allowed_phrases": ["first market"]}})
        self.assertEqual(self.codes(allowed), ["banned-phrase"])
        self.assertIn("The first app", allowed["errors"][0]["message"])

    def test_korean_phrase_matches_before_a_particle(self):
        result = self.check(page('<section class="slide"><p>국내 최초로 출시</p></section>'))
        self.assertEqual(self.codes(result), ["banned-phrase"])

    def test_ledger_is_validated(self):
        self.facts.write_text(
            json.dumps(
                {
                    "facts": [
                        {"id": "a", "value": "3", "claim": "c", "source": "s", "checked": "2026-10-15"},
                        {"id": "a", "value": "4", "claim": "c", "source": "s", "checked": "2026-10-15"},
                        {"id": "b", "value": "5", "claim": "c", "checked": "yesterday"},
                        {"id": "c", "value": "many", "claim": "c", "source": "s", "checked": "2026-10-15"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        codes = self.codes(self.check(page('<section class="slide"></section>')))
        for code in ("fact-id-duplicate", "fact-field-missing", "fact-checked-date-invalid", "fact-value-no-number"):
            self.assertIn(code, codes)

    def test_cli_exit_codes(self):
        deck = self.root / "deck.html"
        deck.write_text(page('<section class="slide" data-main><p>We saved 42 hours.</p></section>'), encoding="utf-8")
        failed = subprocess.run([sys.executable, str(SCRIPT), str(deck), "--json"], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(json.loads(failed.stdout)["qa_facts_gate"], "fail")
        deck.write_text(page('<section class="slide" data-main><p>Hello.</p></section>'), encoding="utf-8")
        passed = subprocess.run([sys.executable, str(SCRIPT), str(deck)], capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stdout)
        self.assertIn("qa-facts-gate: pass", passed.stdout)


if __name__ == "__main__":
    unittest.main()
