#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import qa_animation_guard


TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "animation-mode"
    / "index.html"
)
MOTION = TEMPLATE.with_suffix(".motion.json")


class AnimationGuardTests(unittest.TestCase):
    def write_project(self, html: str, motion: dict | None = None) -> Path:
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        html_path = root / "index.html"
        html_path.write_text(html, encoding="utf-8")
        shutil.copytree(TEMPLATE.parent / "compositions", root / "compositions")
        if motion is not None:
            (root / "index.motion.json").write_text(
                json.dumps(motion),
                encoding="utf-8",
            )
        return html_path

    def tearDown(self):
        folder = getattr(self, "folder", None)
        if folder:
            folder.cleanup()

    def test_shipped_animation_template_passes(self):
        result = qa_animation_guard.run_checks(TEMPLATE)
        self.assertEqual(result["animation_guard_result"], "pass", result["findings"])

    def test_nondeterminism_and_nested_clip_fail(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        html = html.replace(
            '    <div id="scene-1"',
            '    <div id="bad-wrapper"><div id="scene-1"',
            1,
        ).replace(
            'data-height="1080"></div>\n    <div id="scene-2"',
            'data-height="1080"></div></div>\n    <div id="scene-2"',
            1,
        )
        html = html.replace(
            'const tl = gsap.timeline({ paused: true });',
            'const tl = gsap.timeline({ paused: true }); Math.random();',
        )
        result = qa_animation_guard.run_checks(
            self.write_project(html, json.loads(MOTION.read_text()))
        )
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("clip-not-direct-child", codes)
        self.assertIn("unseeded-random", codes)

    def test_motion_duration_must_match(self):
        motion = json.loads(MOTION.read_text())
        motion["duration"] = 19
        result = qa_animation_guard.run_checks(
            self.write_project(TEMPLATE.read_text(), motion)
        )
        self.assertTrue(
            any(
                item["code"] == "motion-duration-mismatch"
                for item in result["findings"]
            )
        )


if __name__ == "__main__":
    unittest.main()
