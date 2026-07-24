#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import build_animated_presentation


ANIMATION = (
    Path(__file__).resolve().parent.parent / "assets" / "animation-mode"
)


class AnimatedPresentationTests(unittest.TestCase):
    def test_shipped_template_builds_navigable_animated_html(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "sample-presentation.html"
            built = build_animated_presentation.build(ANIMATION, output)
            document = built.read_text(encoding="utf-8")
        self.assertEqual(built, output.resolve())
        self.assertEqual(document.count('class="animated-slide"'), 5)
        self.assertIn('data-scene-id="scene-1"', document)
        self.assertIn('data-scene-id="scene-5"', document)
        self.assertIn("window.__ptMakerPresenter", document)
        self.assertIn("timeline.restart()", document)
        self.assertIn('"ArrowRight"', document)
        self.assertIn('"pointerup"', document)
        self.assertIn('id="transition-fx"', document)
        self.assertIn('id="scene-hud"', document)
        self.assertIn("buildTransitionTimelines()", document)
        self.assertIn("prefers-reduced-motion", document)

    def test_animation_contract_is_html_first(self):
        skill_root = Path(__file__).resolve().parent.parent
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        direction = (
            skill_root / "reference" / "production-direction.md"
        ).read_text(encoding="utf-8")
        self.assertIn("HTML이 animation의 기본 최종 산출물", skill)
        self.assertIn("영상은 사용자의 명시 요청이 있을 때만", skill)
        self.assertIn("발표용 HTML을 기본 완성본으로", direction)

    def test_master_clip_order_becomes_horizontal_slide_order(self):
        _, _, _, _, scenes, _ = build_animated_presentation.parse_project(
            ANIMATION
        )
        self.assertEqual(
            [scene.composition_id for scene in scenes],
            ["scene-1", "scene-2", "scene-3", "scene-4", "scene-5"],
        )

    def test_missing_composition_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            (project / "compositions").mkdir()
            source = (ANIMATION / "index.html").read_text(encoding="utf-8")
            (project / "index.html").write_text(source, encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                build_animated_presentation.parse_project(project)


if __name__ == "__main__":
    unittest.main()
