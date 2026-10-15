#!/usr/bin/env python3

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

import build_animated_presentation
import qa_animation_guard


COMPONENT = (
    Path(__file__).resolve().parent.parent / "assets" / "speaker-character"
)
DEMO = COMPONENT / "demo"
POSES = ("smile", "o", "wave", "side", "think")


def canonical_svg() -> str:
    markup = (COMPONENT / "speaker-markup.html").read_text(encoding="utf-8")
    return re.search(r"<svg\b.*?</svg>", markup, re.DOTALL).group(0)


class SpeakerCharacterTests(unittest.TestCase):
    def test_demo_passes_animation_guard(self):
        result = qa_animation_guard.run_checks(DEMO / "index.html")
        self.assertEqual(
            result["animation_guard_result"], "pass", result["findings"]
        )

    def test_demo_builds_paper_presentation(self):
        with tempfile.TemporaryDirectory() as folder:
            document = build_animated_presentation.build(
                DEMO, Path(folder) / "speaker-demo.html", theme="paper"
            ).read_text(encoding="utf-8")
        self.assertEqual(document.count('class="animated-slide"'), 3)
        self.assertIn('data-theme="paper"', document)
        self.assertIn("window.PtSpeaker", document)
        self.assertIn('id="s3-speaker"', document)
        self.assertEqual(document.count('data-transition="paper"'), 1)

    def test_demo_embeds_canonical_component(self):
        css = (COMPONENT / "speaker.css").read_text(encoding="utf-8")
        js = (COMPONENT / "speaker.js").read_text(encoding="utf-8")
        svg = canonical_svg()
        self.assertIn(css, (DEMO / "index.html").read_text(encoding="utf-8"))
        speaker_scenes = 0
        for scene in sorted((DEMO / "compositions").glob("*.html")):
            text = scene.read_text(encoding="utf-8")
            match = re.search(r'id="(s\d+)-speaker"', text)
            if not match:
                continue
            speaker_scenes += 1
            self.assertIn(js, text, scene.name)
            self.assertIn(svg.replace("sN-", match.group(1) + "-"), text, scene.name)
        self.assertGreaterEqual(speaker_scenes, 1)

    def test_markup_covers_every_pose_with_prefixed_ids(self):
        svg = canonical_svg()
        ids = re.findall(r'\bid="([^"]+)"', svg)
        self.assertTrue(ids)
        self.assertTrue(all(value.startswith("sN-") for value in ids), ids)
        declared = set(" ".join(re.findall(r'data-poses="([^"]+)"', svg)).split())
        self.assertEqual(declared, set(POSES))

    def test_helper_has_no_nondeterministic_patterns(self):
        js = (COMPONENT / "speaker.js").read_text(encoding="utf-8")
        for code, pattern in qa_animation_guard.FORBIDDEN_PATTERNS.items():
            self.assertIsNone(pattern.search(js), code)
        self.assertIn('var POSES = ["smile", "o", "wave", "side", "think"];', js)
        self.assertIn("{ start: null, tween: false, lipSync: false }", js)


if __name__ == "__main__":
    unittest.main()
