#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import qa_html_guard


BASE = """<!doctype html>
<html><head><style>
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style></head><body>
<div class="reveal"><div class="slides">
<section><h1>A complete claim</h1><aside class="notes">note</aside></section>
</div></div>
<script>
window.addEventListener('beforeprint', function () {});
Reveal.initialize({width: 1280, height: 720, center: false, pdfPageHeightOffset: 0});
</script></body></html>"""


class HtmlGuardTests(unittest.TestCase):
    def run_html(self, html: str, assets: dict[str, bytes] | None = None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "deck.html"
            path.write_text(html, encoding="utf-8")
            for name, content in (assets or {}).items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            return qa_html_guard.run_checks(path)

    def test_minimal_deck_passes(self):
        result = self.run_html(BASE)
        self.assertEqual(result["html_guard_result"], "pass")

    def test_infinite_animation_is_p0(self):
        result = self.run_html(BASE.replace("</style>", ".x{animation:spin 1s infinite}</style>"))
        self.assertTrue(any(item["code"] == "infinite-css-animation" for item in result["findings"]))

    def test_sequence_requires_frames_and_label(self):
        html = BASE.replace(
            "</section>",
            '<figure class="image-sequence" data-sequence-id="x" data-print-frame="0"><img src="missing.png" alt="" data-frame></figure></section>',
        )
        result = self.run_html(html)
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("sequence-too-short", codes)
        self.assertIn("sequence-label-missing", codes)
        self.assertIn("image-file-missing", codes)


if __name__ == "__main__":
    unittest.main()
