#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import qa_media_guard


SVG = '<svg viewBox="0 0 400 300" data-fullsize-qa="true" data-rendered-qa="true"><path d="M10 10 L200 40 L380 260 Z"/></svg>'


def slide(label: str) -> str:
    return f'<section class="slide"><h2>{label}</h2>{SVG}</section>'


class MapWordTests(unittest.TestCase):
    def map_codes(self, label: str) -> list[str]:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "deck.html"
            html = "<html><body>" + slide(label) + "</body></html>"
            path.write_text(html, encoding="utf-8")
            return [finding.code for finding in qa_media_guard.check_maps(html, path)]

    def test_real_map_labels_still_trip_the_guard(self):
        for label in ("스위스 칸톤 지도", "서울 지도를 보면", "배송 경로", "Route map of the region", "Cities we serve"):
            with self.subTest(label=label):
                self.assertIn("inline-real-map-svg", self.map_codes(label))

    def test_words_that_only_contain_a_map_word_do_not(self):
        for label in ("주장 · 시연 · 검증", "핵심 주장", "핀테크 시장", "경로당 방문", "Capacity by quarter", "Roadmap"):
            with self.subTest(label=label):
                self.assertEqual(self.map_codes(label), [])


if __name__ == "__main__":
    unittest.main()
