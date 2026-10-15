#!/usr/bin/env python3

from __future__ import annotations

import shutil
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
        self.assertIn('id="fx-curtain-top"', document)
        self.assertIn('id="fx-ring-a"', document)
        self.assertIn('id="scene-hud"', document)
        self.assertIn("buildTransitionTimelines()", document)
        self.assertIn("buildTransitionTimelines();\n        resetTransitionFx();", document)
        self.assertIn("function poseTransition(", document)
        self.assertIn("poseTransition,", document)
        self.assertIn(
            'const transitionFamilies = ["prism", "curtain", "aperture"]',
            document,
        )
        self.assertIn("transitionFamilyFor(previousIndex, nextIndex)", document)
        self.assertIn('data-transition-family="curtain"', document)
        self.assertIn('data-transition-family="aperture"', document)
        self.assertIn("prefers-reduced-motion", document)
        self.assertIn('slide.classList.toggle("is-near"', document)
        self.assertIn("replayCurrent();", document)
        self.assertIn("contain: layout paint", document)
        self.assertNotIn("filter: blur(12px)", document)
        self.assertNotIn("will-change: transform, filter", document)

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

    def test_hud_does_not_leak_hardcoded_chapter_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            document = build_animated_presentation.build(
                ANIMATION, Path(folder) / "out.html"
            ).read_text(encoding="utf-8")
        for stale in (
            "OPEN THE SCENT",
            "MEMBER SIGNAL",
            "SCENE OF RESCENE",
            "NIGHT BLOOM",
            "AFTER SCENT",
        ):
            self.assertNotIn(stale, document)

    def test_hud_chapter_comes_from_clip_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "animation"
            shutil.copytree(ANIMATION, project)
            index = project / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    'id="scene-1" class="scene clip"',
                    'id="scene-1" data-chapter="문제 정의" class="scene clip"',
                    1,
                ),
                encoding="utf-8",
            )
            document = build_animated_presentation.build(
                project, Path(folder) / "out.html"
            ).read_text(encoding="utf-8")
        self.assertIn(
            '<span id="scene-hud-chapter" class="scene-hud__chapter">문제 정의</span>',
            document,
        )
        self.assertIn('const chapters = ["문제 정의", ', document)

    def test_hud_chapter_falls_back_to_scene_heading(self):
        # Decks made before data-chapter existed must not end up with an empty
        # HUD, so a clip without it borrows its scene's first heading.
        with tempfile.TemporaryDirectory() as folder:
            document = build_animated_presentation.build(
                ANIMATION, Path(folder) / "out.html"
            ).read_text(encoding="utf-8")
        self.assertIn(
            '<span id="scene-hud-chapter" class="scene-hud__chapter">'
            "발표는 장수가 아니라 장면의 흐름으로 기억됩니다</span>",
            document,
        )
        self.assertIn(
            'const chapters = ["발표는 장수가 아니라 장면의 흐름으로 기억됩니다", '
            '"한 장에는 하나의 주장만", "설계 → 움직임 → 검수", "", '
            '"이제 PT를 보는 자료에서 경험하는 장면으로"];',
            document,
        )

    def test_paper_theme_has_no_flash_or_neon_layers(self):
        with tempfile.TemporaryDirectory() as folder:
            paper = build_animated_presentation.build(
                ANIMATION, Path(folder) / "paper.html", theme="paper"
            ).read_text(encoding="utf-8")
            default = build_animated_presentation.build(
                ANIMATION, Path(folder) / "default.html"
            ).read_text(encoding="utf-8")
        self.assertIn('data-theme="paper"', paper)
        self.assertIn('const paperFamilies = ["cut", "paper"];', paper)
        self.assertEqual(paper.count('class="animated-slide"'), 5)
        for neon in (
            'id="fx-flare"',
            'id="fx-blade-a"',
            'class="show-lightfield"',
            'class="stage-atmosphere"',
            "mix-blend-mode: screen",
            "#ff78aa",
        ):
            self.assertNotIn(neon, paper)
        # the paper HUD sits on a solid panel so it stays readable on every world
        self.assertNotIn("mix-blend-mode", paper)
        self.assertIn("--hud-panel", paper)
        self.assertIn('data-theme="default"', default)
        self.assertIn('id="fx-flare"', default)
        self.assertIn('class="show-lightfield"', default)

    def test_paper_theme_reads_seam_transition_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "animation"
            shutil.copytree(ANIMATION, project)
            index = project / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    'id="scene-3" class="scene clip"',
                    'id="scene-3" data-transition="paper" class="scene clip"',
                    1,
                ),
                encoding="utf-8",
            )
            document = build_animated_presentation.build(
                project, Path(folder) / "out.html", theme="paper"
            ).read_text(encoding="utf-8")
        self.assertEqual(document.count('data-transition="paper"'), 1)
        self.assertIn('data-scene-id="scene-3"\n        data-transition="paper"', document)

    def test_unknown_theme_and_transition_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                build_animated_presentation.build(
                    ANIMATION, Path(folder) / "out.html", theme="neon"
                )
            project = Path(folder) / "animation"
            shutil.copytree(ANIMATION, project)
            index = project / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    'id="scene-2" class="scene clip"',
                    'id="scene-2" data-transition="wipe" class="scene clip"',
                    1,
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                build_animated_presentation.parse_project(project)

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
