#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import build_judged_deck as build
import qa_facts_gate
from browser_harness_runtime import BrowserHarnessError, IsolatedBrowserHarness, ensure_background_runtime


SCRIPT = Path(__file__).resolve().parent / "build_judged_deck.py"
NBSP = " "

HEAD = '<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="deck.css"></head><body>'
TAIL = "</body></html>"


class BuildJudgedDeckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "facts.json").write_text(
            json.dumps(
                {
                    "facts": [
                        {"id": "trials", "value": "35", "unit": "trials", "claim": "c", "source": "s", "checked": "2026-10-15"},
                        {"id": "share", "value": "41.5", "unit": "%", "claim": "c", "source": "s", "checked": "2026-10-15"},
                        {"id": "people", "value": "3.4", "unit": "billion", "claim": "c", "source": "s", "checked": "2026-10-15"},
                        {"id": "adopters", "value": "7", "unit": "in 100", "claim": "c", "source": "s", "checked": "2026-10-15"},
                    ]
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def render(self, body: str, env: dict[str, str] | None = None) -> build.BuildResult:
        src = self.root / "deck.src.html"
        src.write_text(HEAD + body + TAIL, encoding="utf-8")
        return build.build(src, env=env or {})

    def test_comments_are_stripped_but_not_inside_scripts(self):
        result = self.render(
            '<section class="slide"><!-- TODO owner --><p>Hi</p></section>'
            '<script>const s = "<!-- keep -->";</script><!-- gone -->'
        )
        self.assertNotIn("TODO", result.html)
        self.assertNotIn("gone", result.html)
        self.assertIn('const s = "<!-- keep -->";', result.html)
        self.assertIn("<p>Hi</p>", result.html)

    def test_facts_are_substituted_with_units(self):
        result = self.render(
            '<section class="slide"><p>{{fact:trials}} · {{fact:share}} · {{fact:trials:value}} of 50</p></section>'
        )
        self.assertIn(
            f'<span class="fact" data-fact="trials">35{NBSP}trials</span> · '
            '<span class="fact" data-fact="share">41.5%</span> · '
            '<span class="fact" data-fact="trials">35</span> of 50',
            result.html,
        )

    def test_numbers_get_thousands_separators_but_years_do_not(self):
        cases = {
            "$200000": "$200,000",
            "11889760": "11,889,760",
            "4000": "4,000",
            "12345.678": "12,345.678",
            "2028": "2028",
            "1999": "1999",
            "980": "980",
            "0.0120": "0.0120",
            "1,669": "1,669",
            "3 in 10": "3 in 10",
            "2026-10-15": "2026-10-15",
        }
        for raw, shown in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(build.format_value(raw), shown)

    def test_formatted_facts_still_pass_the_facts_gate(self):
        facts = json.loads((self.root / "facts.json").read_text(encoding="utf-8"))
        facts["facts"].append({"id": "price", "value": "$200000", "unit": "", "claim": "c", "source": "s", "checked": "2026-10-15"})
        facts["facts"].append({"id": "year", "value": "2028", "unit": "", "claim": "c", "source": "s", "checked": "2026-10-15"})
        (self.root / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
        result = self.render(
            '<section class="slide"><p>{{fact:price}} from {{fact:year:value}}</p>'
            '<footer class="ft"><div class="src">Details: price list</div></footer></section>'
        )
        self.assertIn('<span class="fact" data-fact="price">$200,000</span>', result.html)
        self.assertIn('<span class="fact" data-fact="year">2028</span>', result.html)
        (self.root / "deck.html").write_text(result.html, encoding="utf-8")
        gate = qa_facts_gate.run_checks(self.root / "deck.html", self.root / "facts.json", {})
        self.assertEqual(gate["qa_facts_gate"], "pass", gate["errors"])

    def test_bound_before_a_fact_stays_together(self):
        result = self.render("<p>≤ {{fact:trials}}</p>")
        self.assertIn(f'≤{NBSP}<span class="fact" data-fact="trials">', result.html)

    def test_fact_inside_svg_text_is_a_tspan(self):
        result = self.render(SVG_SLIDE)
        self.assertIn('<text x="40" y="120"><tspan class="fact" data-fact="trials">35', result.html)
        self.assertNotIn('<span class="fact"', result.html)
        with self.assertRaises(build.BuildError):
            self.render('<svg viewBox="0 0 10 10"><text>{{dots:adopters}}</text></svg>')

    def test_fact_inside_an_attribute_fails(self):
        with self.assertRaises(build.BuildError) as ctx:
            self.render('<img alt="{{fact:trials}}" src="x.png">')
        self.assertIn("attribute", str(ctx.exception))

    def test_unknown_fact_fails(self):
        with self.assertRaises(build.BuildError) as ctx:
            self.render('<section class="slide"><p>{{fact:missing}}</p></section>')
        self.assertIn("missing", str(ctx.exception))

    def test_link_placeholder_and_value(self):
        unset = self.render('<p>{{link:VIDEO_URL}}</p>')
        self.assertIn('<span class="v ph">VIDEO_URL</span>', unset.html)
        self.assertIn("placeholder: VIDEO_URL is not set", unset.warnings)
        done = self.render('<p>{{link:VIDEO_URL}}</p>', env={"VIDEO_URL": "https://example.com/watch/"})
        self.assertIn('<a class="v u" href="https://example.com/watch/">example.com/watch</a>', done.html)
        self.assertEqual(done.warnings, [])

    def test_dots_grid_comes_from_a_fact(self):
        result = self.render("<div>{{dots:adopters}}</div>")
        self.assertIn('<div class="dots" data-fact="adopters" role="img" aria-label="7 of 100">', result.html)
        self.assertEqual(result.html.count("<i"), 100)
        self.assertEqual(result.html.count('<i class="on">'), 7)
        with self.assertRaises(build.BuildError) as ctx:
            self.render("<div>{{dots:7}}</div>")
        self.assertIn("facts.json", str(ctx.exception))
        with self.assertRaises(build.BuildError):
            self.render("<div>{{dots:people}}</div>")  # 3.4 billion is not a count out of 100

    def test_icons_from_deck_assets(self):
        icons = self.root / "assets" / "icons"
        icons.mkdir(parents=True)
        (icons / "check.svg").write_text(
            '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5 12l5 5"/></svg>',
            encoding="utf-8",
        )
        result = self.render("<p>{{icon:check}} ok</p>")
        self.assertIn('<svg class="ic" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"', result.html)
        self.assertNotIn("<?xml", result.html)
        with self.assertRaises(build.BuildError):
            self.render("<p>{{icon:nope}}</p>")

    def test_qr_needs_segno_only_when_used(self):
        with mock.patch.dict(sys.modules, {"segno": None}):
            self.render("<p>no qr here</p>")
            with self.assertRaises(build.BuildError) as ctx:
                self.render("<p>{{qr:https://example.com}}</p>")
        self.assertIn("segno", str(ctx.exception))

    def test_qr_with_segno(self):
        calls = []

        class FakeCode:
            def svg_inline(self, **kwargs):
                return '<svg viewBox="0 0 21 21"><path d="M0 0h1"/></svg>'

        def make(content, **kwargs):
            calls.append(content)
            return FakeCode()

        fake = types.SimpleNamespace(make=make)
        with mock.patch.dict(sys.modules, {"segno": fake}):
            result = self.render("<p>{{qr:https://example.com/demo}}</p>")
        self.assertEqual(calls, ["https://example.com/demo"])
        self.assertIn('<svg class="qr" viewBox="0 0 21 21">', result.html)

    def test_number_unit_and_bounds_stay_together(self):
        result = self.render(
            '<p title="5 MB">Under 5 MB, ≤ 3 pages, 3.4 billion people, 12,500 원, 3 apples</p>'
            "<style>.x { margin: 0 2 s; }</style>"
        )
        self.assertIn('title="5 MB"', result.html)
        self.assertIn(f"5{NBSP}MB", result.html)
        self.assertIn(f"≤{NBSP}3", result.html)
        self.assertIn(f"3.4{NBSP}billion", result.html)
        self.assertIn(f"12,500{NBSP}원", result.html)
        self.assertIn("3 apples", result.html)
        self.assertIn(".x { margin: 0 2 s; }", result.html)

    def test_dates_never_break(self):
        result = self.render(
            "<p>Checked 2026-10-15 and 10-17.</p><p><code>2026-10-15</code> <code>run <b>2026-10-16</b></code></p>"
        )
        self.assertIn('Checked <span class="nw">2026-10-15</span> and <span class="nw">10-17</span>.', result.html)
        self.assertIn("<code>2026-10-15</code>", result.html)
        self.assertIn("<code>run <b>2026-10-16</b></code>", result.html)

    def test_long_code_paths_break_after_slashes(self):
        result = self.render("<p><code>evidence/runs/round-four/results.json</code> <code>a/b</code></p>")
        self.assertIn(
            '<code><span class="seg">evidence/</span><wbr><span class="seg">runs/</span><wbr>'
            '<span class="seg">round-four/</span><wbr><span class="seg">results.json</span></code>',
            result.html,
        )
        self.assertIn("<code>a/b</code>", result.html)

    def test_template_layer_is_injected(self):
        (self.root / "template.json").write_text(
            json.dumps({"slides": [{"index": 1, "layer_html": '<div class="tart" style="top:0px"></div>'}]}),
            encoding="utf-8",
        )
        (self.root / "template-layer.css").write_text(".tart { position: absolute; }\n", encoding="utf-8")
        result = self.render('<section class="slide" data-tpl="1"><p>x</p></section><section class="slide"><p>y</p></section>')
        self.assertIn(
            '<section class="slide" data-tpl="1"><div class="tart" style="top:0px"></div><p>x</p>',
            result.html,
        )
        self.assertIn('<section class="slide"><p>y</p>', result.html)
        self.assertIn('<style data-template-layer>\n.tart { position: absolute; }\n</style></head>', result.html)
        with self.assertRaises(build.BuildError):
            self.render('<section class="slide" data-tpl="4"></section>')

    def test_slide_template_without_template_json_fails(self):
        with self.assertRaises(build.BuildError) as ctx:
            self.render('<section class="slide" data-tpl="1"></section>')
        self.assertIn("template.json", str(ctx.exception))

    def test_unknown_placeholder_fails(self):
        with self.assertRaises(build.BuildError) as ctx:
            self.render("<p>{{mark}}</p>")
        self.assertIn("{{mark}}", str(ctx.exception))

    def test_cli_writes_deck_html_and_warns(self):
        src = self.root / "deck.src.html"
        src.write_text(HEAD + "<p>{{link:GITHUB_URL}}</p>" + TAIL, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(src)],
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("placeholder: GITHUB_URL is not set", result.stderr)
        self.assertTrue((self.root / "deck.html").is_file())


SVG_SLIDE = (
    '<section class="slide" data-main><svg viewBox="0 0 800 300" width="800" height="300">'
    '<rect x="10" y="10" width="300" height="200"/><text x="40" y="120">{{fact:trials}}</text>'
    '<rect x="400" y="10" width="300" height="200"/></svg>'
    '<footer class="ft"><div class="src">Details: evidence/trials.json</div></footer></section>'
)


def chrome_available() -> bool:
    try:
        ensure_background_runtime(install=False, quiet=True)
        return True
    except BrowserHarnessError:
        return False


@unittest.skipUnless(chrome_available(), "Chrome and browser-harness are required")
class SvgFactInBrowserTests(unittest.TestCase):
    def test_diagram_stays_intact_and_the_gate_sees_the_fact(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "facts.json").write_text(
                json.dumps({"facts": [{"id": "trials", "value": "35", "unit": "trials", "claim": "c", "source": "s", "checked": "2026-10-15"}]}),
                encoding="utf-8",
            )
            src = root / "deck.src.html"
            src.write_text(HEAD + SVG_SLIDE + TAIL, encoding="utf-8")
            deck = root / "deck.html"
            deck.write_text(build.build(src, env={}).html, encoding="utf-8")
            code = (
                f"new_tab({deck.as_uri()!r})\nwait_for_load(20)\n"
                "print(json.dumps(js(\"({rects: document.querySelectorAll('svg rect').length, "
                "fact: document.querySelector('svg text tspan.fact') ? document.querySelector('svg text tspan.fact').textContent : null})\")))"
            )
            with IsolatedBrowserHarness() as browser:
                out = browser.run_code(code, timeout=60).stdout.strip().splitlines()[-1]
            self.assertEqual(json.loads(out), {"rects": 2, "fact": "35\u00a0trials"})
            result = qa_facts_gate.run_checks(deck, root / "facts.json", {})
            self.assertEqual(result["qa_facts_gate"], "pass", result["errors"])


if __name__ == "__main__":
    unittest.main()
