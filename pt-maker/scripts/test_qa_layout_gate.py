#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
import zlib
from pathlib import Path

import import_template
import qa_layout_gate as gate
from browser_harness_runtime import BrowserHarnessError, ensure_background_runtime


TEMPLATE = {
    "slide_size": {"px": [1920, 1080], "in": [13.333, 7.5]},
    "min_font_px": 24.0,
    "slides": [
        {"index": 1, "art": [{"kind": "shape", "x": 0, "y": 0, "w": 1920, "h": 96}], "title_box": None},
        {
            "index": 2,
            "art": [{"kind": "shape", "x": 0, "y": 0, "w": 1920, "h": 144, "layer": "base"}],
            "title_box": {"x": 72, "y": 24, "w": 1776, "h": 96},
        },
    ],
}


class SettingsTests(unittest.TestCase):
    def test_template_sets_size_page_minimum_font_zones_and_title_boxes(self):
        settings = gate.resolve_settings({}, TEMPLATE)
        self.assertEqual((settings["width"], settings["height"]), (1920, 1080))
        self.assertEqual(settings["page_in"], [13.333, 7.5])
        self.assertEqual(settings["min_font_px"], 24.0)
        self.assertEqual(settings["zones"]["1"], [{"x": 0, "y": 0, "w": 1920, "h": 96}])
        self.assertEqual(settings["title_boxes"]["2"], {"x": 72, "y": 24, "w": 1776, "h": 96})
        self.assertNotIn("1", settings["title_boxes"])
        self.assertEqual((settings["max_words"], settings["max_footer_lines"]), (80, 3))

    def test_config_overrides_the_template(self):
        config = {"limits": {"max_words_per_slide": 60}, "layout": {"min_font_px": 26, "max_footer_lines": 2}}
        settings = gate.resolve_settings(config, TEMPLATE)
        self.assertEqual((settings["min_font_px"], settings["max_words"], settings["max_footer_lines"]), (26.0, 60, 2))

    def test_without_template_the_fine_print_floor_scales_from_1280(self):
        settings = gate.resolve_settings({}, None)
        self.assertEqual((settings["width"], settings["height"]), (1920, 1080))
        self.assertEqual(settings["page_in"], [20.0, 11.25])
        self.assertEqual(settings["min_font_px"], 22.5)
        self.assertEqual(settings["zones"], {})

    def test_template_path_comes_from_config_or_sits_next_to_the_deck(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            deck = root / "deck.html"
            deck.write_text("<html></html>", encoding="utf-8")
            self.assertIsNone(gate.find_template(deck, {}, None))
            (root / "template.json").write_text(json.dumps(TEMPLATE), encoding="utf-8")
            self.assertEqual(gate.find_template(deck, {}, None), root / "template.json")
            self.assertEqual(gate.find_template(deck, {"template": "other.json"}, None), root / "other.json")


class PdfAndReportTests(unittest.TestCase):
    def test_pdf_info_counts_plain_pages(self):
        pdf = (
            b"%PDF-1.4\n1 0 obj << /Type /Pages /Count 2 >> endobj\n"
            b"2 0 obj << /Type /Page /MediaBox [0 0 960 540] >> endobj\n"
            b"3 0 obj << /Type /Page /MediaBox [0 0 960 540] >> endobj\n"
        )
        self.assertEqual(gate.pdf_info(pdf), {"pages": 2, "media_boxes": [[960.0, 540.0], [960.0, 540.0]]})

    def test_pdf_info_reads_object_streams(self):
        hidden = zlib.compress(b"<< /Type /Pages /Kids [4 0 R 5 0 R 6 0 R] /Count 3 >> << /Type /Page /MediaBox [0 0 960 540] >>")
        head = b"7 0 obj << /Type /ObjStm /Filter /FlateDecode /Length " + str(len(hidden)).encode() + b" >>\nstream\n"
        pdf = b"%PDF-1.7\n" + head + hidden + b"\nendstream\nendobj\n"
        self.assertEqual(gate.pdf_info(pdf)["pages"], 3)

    def test_pdf_problems_use_the_physical_page(self):
        info = {"pages": 2, "media_boxes": [[960.0, 540.0], [1440.0, 810.0]]}
        problems = gate.pdf_problems(info, slides=3, page_in=[13.333, 7.5])
        self.assertEqual([problem["kind"] for problem in problems], ["pdf-pages", "pdf-size"])
        self.assertEqual(gate.pdf_problems({"pages": 1, "media_boxes": [[959.98, 539.6]]}, slides=1, page_in=[13.333, 7.5]), [])

    def test_report_lines(self):
        result = {
            "problems": [{"slide": "03", "kind": "small-text", "message": 'small text 20.0px: "Tiny"'}],
            "words": [{"slide": "03", "count": 91, "main": True}, {"slide": "A1", "count": 120, "main": False}],
            "max_words": 80,
        }
        lines = gate.report_lines(result)
        self.assertEqual(lines[0], '03 small text 20.0px: "Tiny"')
        self.assertIn("03  91 words  OVER", lines)
        self.assertIn("A1 120 words (appendix)", lines)
        self.assertEqual(gate.report_lines({"problems": [], "words": [], "max_words": 80})[0], "layout check: no problems found")

    def test_browser_code_prints_at_the_physical_page_size(self):
        code = gate.browser_code(Path("/tmp/deck.html"), gate.resolve_settings({}, TEMPLATE), Path("/tmp/slides"), Path("/tmp/deck.pdf"))
        self.assertIn("paperWidth=13.333", code)
        self.assertIn("paperHeight=7.5", code)
        self.assertIn("preferCSSPageSize=False", code)
        self.assertIn("captureBeyondViewport=True", code)


def chrome_available() -> bool:
    try:
        ensure_background_runtime(install=False, quiet=True)
        return True
    except BrowserHarnessError:
        return False


# The template layer rules exactly as import_template.py writes them (including pointer-events: none on .tart).
LAYER_CSS = import_template.layer_css({"source": "test.pptx", "slide_size": {"px": [1920, 1080]}})

STYLE = "<style>\n" + LAYER_CSS + """
body { margin: 0; font-family: sans-serif; }
@media screen { body { padding: 24px 0; background: #888; } .slide { margin: 0 auto 24px; } }
.slide { width: 1920px; height: 1080px; position: relative; overflow: hidden; isolation: isolate; background: #fff; padding: 160px 80px 0; box-sizing: border-box; break-after: page; }
.slide:last-child { break-after: auto; }
p, h1 { margin: 0; font-size: 30px; line-height: 1.4; }
.ft { position: absolute; left: 80px; right: 80px; bottom: 24px; font-size: 28px; line-height: 1.3; display: flex; justify-content: space-between; }
.box { height: 40px; overflow: hidden; }
.tt { position: absolute; left: 90px; top: 40px; font-size: 40px; color: #fff; }
.steps { list-style: none; padding: 0; display: flex; gap: 40px; }
.steps li { position: relative; width: 300px; font-size: 30px; }
.steps li::after { content: ""; position: absolute; right: -27px; top: 10px; width: 16px; height: 16px; background: #999; }
</style>"""

BAND_BASE = '<div class="tart tbase" style="left:0;top:0;width:1920px;height:144px;background:#1B6EC2"></div>'
BAND_TOP = '<div class="tart" style="left:0;top:0;width:1920px;height:144px;background:#1B6EC2"></div>'
HEADER = '<div class="tart" style="left:0;top:0;width:1920px;height:96px;background:#222"></div>'

DECK = f"""<!doctype html><html><head><meta charset="utf-8">{STYLE}</head><body>
<section class="slide" data-tpl="1" data-main>{HEADER}
  <h1>A clean slide</h1><p>Short and readable.</p>
  <ul class="steps"><li>Step one</li><li>Step two</li></ul>
  <footer class="ft"><div class="src">Details: x</div><div class="pg"><b>01</b></div></footer>
</section>
<section class="slide" data-tpl="1" data-main>{HEADER}
  <p style="font-size:20px">Tiny print</p>
  <p style="transform:scale(.4);transform-origin:left top">Drawn at forty percent of its size</p>
  <h1 style="white-space:nowrap;font-size:64px">A one-line headline that is far too long for the slide and keeps running past the right edge of it</h1>
  <p style="position:absolute;top:50px;left:200px">Under the header bar</p>
  <p style="position:absolute;left:10px;top:500px">At the edge</p>
  <p class="box">One<br>Two<br>Three</p>
  <img src="missing.png" alt="" style="width:10px;height:10px">
  <p>WORDS</p>
  <p style="position:absolute;left:300px;top:1000px">Sits on the footer</p>
  <footer class="ft"><div class="src" style="width:400px">Details: a long footer that wraps over many lines because the source box is narrow on purpose, so it runs to four or five lines at least.</div><div class="pg"><b>02</b></div></footer>
</section>
<section class="slide" data-tpl="2" data-main>{BAND_BASE}
  <div class="tt">Findings</div><p style="position:absolute;left:600px;top:100px">In the band, outside the title box</p>
  <h1 style="margin-top:40px">Below the band</h1>
  <footer class="ft"><div class="src">Details: x</div><div class="pg"><b>03</b></div></footer>
</section>
<section class="slide" data-tpl="2" data-main>{BAND_TOP}
  <div class="tt">Findings</div><h1 style="margin-top:40px">Below the band</h1>
  <footer class="ft"><div class="src">Details: x</div><div class="pg"><b>04</b></div></footer>
</section>
</body></html>"""


@unittest.skipUnless(chrome_available(), "Chrome and browser-harness are required for the rendered layout test")
class RenderedLayoutTests(unittest.TestCase):
    def test_defects_are_caught_and_outputs_written(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            deck = root / "deck.html"
            deck.write_text(DECK.replace("WORDS", " ".join(["word"] * 90)), encoding="utf-8")
            (root / "template.json").write_text(json.dumps(TEMPLATE), encoding="utf-8")
            result = gate.run_gate(deck, config={}, slides_dir=root / "slides", pdf_path=root / "deck.pdf")
            by_slide: dict[str, list[dict]] = {}
            for problem in result["problems"]:
                by_slide.setdefault(problem["slide"], []).append(problem)
            kinds = lambda slide: {p["kind"] for p in by_slide.get(slide, [])}  # noqa: E731
            self.assertNotIn("01", by_slide, result["problems"])
            for kind in ("small-text", "under-art", "edge", "overflow-x", "clipped", "broken-image", "words-over", "footer-overlap", "footer-lines"):
                self.assertIn(kind, kinds("02"), (kind, result["problems"]))
            messages = " ".join(p["message"] for p in by_slide["02"])
            self.assertIn("12.0px", messages)  # 30 px drawn at scale(.4)
            self.assertIn("A one-line headline", messages)
            # Title on the band: exempt and visible; other text on the band is still caught.
            self.assertEqual(kinds("03"), {"under-art"}, by_slide.get("03"))
            self.assertIn("outside the title box", by_slide["03"][0]["message"])
            self.assertEqual(kinds("04"), {"covered-by-art"}, by_slide.get("04"))
            self.assertEqual(sorted(path.name for path in (root / "slides").glob("*.png")), ["01.png", "02.png", "03.png", "04.png"])
            self.assertIn("=== 03 ===\nFindings", (root / "slides" / "text.txt").read_text(encoding="utf-8"))
            self.assertEqual(result["pdf_pages"], 4)
            info = gate.pdf_info((root / "deck.pdf").read_bytes())
            for box in info["media_boxes"]:
                self.assertAlmostEqual(box[0], 960, delta=1.5)
                self.assertAlmostEqual(box[1], 540, delta=1.5)


if __name__ == "__main__":
    unittest.main()
