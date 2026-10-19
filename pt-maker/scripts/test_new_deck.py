#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "new_deck.py"


class NewDeckTests(unittest.TestCase):
    def run_new_deck(
        self,
        root: Path,
        mode: str | None,
        production_direction: str,
    ) -> Path:
        command = [
            "python3",
            str(SCRIPT),
            "sample-topic",
            "--date",
            "20260724",
            "--root",
            str(root),
            "--production-direction",
            production_direction,
        ]
        if mode is not None:
            command.extend(["--mode", mode])
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(result.stdout.strip().splitlines()[-1])

    def test_presentation_mode_is_backward_compatible(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.run_new_deck(
                Path(folder),
                "presentation",
                "text",
            )
            self.assertTrue((deck / "deck.html").is_file())
            self.assertTrue((deck / "assets" / "CREDITS.txt").is_file())
            self.assertFalse((deck / "animation").exists())

    def test_animation_mode_creates_pinned_hyperframes_project(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.run_new_deck(
                Path(folder),
                "animation",
                "animation",
            )
            animation = deck / "animation"
            self.assertFalse((deck / "deck.html").exists())
            self.assertTrue((animation / "index.html").is_file())
            package = json.loads((animation / "package.json").read_text())
            self.assertIn("hyperframes@0.7.70", package["scripts"]["check"])
            self.assertNotIn(
                "__PROJECT_SLUG__",
                (animation / "index.html").read_text(encoding="utf-8"),
            )

    def test_both_mode_has_both_outputs_and_increments_sequence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = self.run_new_deck(
                root,
                "presentation",
                "text",
            )
            second = self.run_new_deck(
                root,
                "both",
                "image",
            )
            self.assertTrue(first.name.startswith("01_"))
            self.assertTrue(second.name.startswith("02_"))
            self.assertTrue((second / "deck.html").is_file())
            self.assertTrue((second / "animation" / "index.html").is_file())
            ledger = json.loads((second / "motion-ledger.json").read_text())
            self.assertEqual(ledger["mode"], "both")
            self.assertEqual(ledger["production_direction"], "image")

    def test_image_direction_defaults_to_presentation_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.run_new_deck(Path(folder), None, "image")
            self.assertTrue((deck / "deck.html").is_file())
            self.assertFalse((deck / "animation").exists())
            ledger = json.loads((deck / "motion-ledger.json").read_text())
            self.assertEqual(ledger["mode"], "presentation")
            self.assertEqual(ledger["production_direction"], "image")

    def test_animation_direction_defaults_to_animation_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.run_new_deck(Path(folder), None, "animation")
            self.assertFalse((deck / "deck.html").exists())
            self.assertTrue((deck / "animation" / "index.html").is_file())
            ledger = json.loads((deck / "motion-ledger.json").read_text())
            self.assertEqual(ledger["mode"], "animation")
            self.assertEqual(ledger["production_direction"], "animation")

    def test_contradictory_direction_and_mode_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "sample-topic",
                    "--root",
                    folder,
                    "--production-direction",
                    "image",
                    "--mode",
                    "animation",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("text/image production direction", result.stderr)

    def run_judged(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "contest-entry",
                "--date",
                "20261019",
                "--root",
                str(root),
                "--production-direction",
                "judged",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_judged_direction_scaffolds_fixed_size_deck_files(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_judged(Path(folder))
            self.assertEqual(result.returncode, 0, result.stderr)
            deck = Path(result.stdout.strip().splitlines()[-1])
            for name in (
                "deck.src.html",
                "deck.css",
                "facts.json",
                "judged.json",
                "shots.json",
                "CHANGES.md",
                "NOTES.md",
                "assets/CREDITS.txt",
            ):
                self.assertTrue((deck / name).is_file(), name)
            self.assertTrue((deck / "assets" / "img").is_dir())
            self.assertTrue((deck / "assets" / "icons").is_dir())
            self.assertFalse((deck / "deck.html").exists())
            self.assertFalse((deck / "animation").exists())
            self.assertIn("production-direction: `judged`", (deck / "build-notes.md").read_text(encoding="utf-8"))
            source = (deck / "deck.src.html").read_text(encoding="utf-8")
            self.assertIn('class="slide', source)
            self.assertNotIn("Reveal", source)
            build = subprocess.run(
                ["python3", str(SCRIPT.with_name("build_judged_deck.py")), str(deck / "deck.src.html")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)

    def test_judged_direction_imports_the_template(self):
        from test_import_template import build_fixture

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pptx = root / "template.pptx"
            build_fixture(pptx)
            result = self.run_judged(root, "--template", str(pptx))
            self.assertEqual(result.returncode, 0, result.stderr)
            deck = Path(result.stdout.strip().splitlines()[-1])
            self.assertTrue((deck / "template.json").is_file())
            self.assertTrue((deck / "template-layer.css").is_file())
            self.assertTrue((deck / "assets" / "template" / "image1.png").is_file())
            config = json.loads((deck / "judged.json").read_text(encoding="utf-8"))
            self.assertEqual(config["template"], "template.json")
            self.assertNotIn("template_source", config)
            self.assertNotIn("evidence", config)
            self.assertNotIn("deadline", config["limits"])
            self.assertIn("min font: 12 pt = 24 px", result.stdout)
            self.assertIn("warning:", result.stdout)
            source = (deck / "deck.src.html").read_text(encoding="utf-8")
            for index, title in enumerate(["Opening", "Approach", "Thank you", "Findings"], start=1):
                self.assertIn(f'data-tpl="{index}" data-slot="{index}"', source)
                self.assertIn(title, source)
            # Findings puts its title on a band: the slot title sits in the band, the content starts below it.
            self.assertIn('<div class="tt nowc on-art" style="left:86.4px;top:31.2px;color:#FFFFFF">Findings</div>', source)
            self.assertIn("--top:176px", source)
            # One side margin, taken from the template title, for the left and right of the page and the footer.
            self.assertIn("--side:86.4px", source)
            self.assertNotIn("--left:", source)
            css = (deck / "deck.css").read_text(encoding="utf-8")
            self.assertIn("padding: var(--top, 96px) var(--side, 96px) 0 var(--side, 96px);", css)
            self.assertIn("left: var(--side, 96px); right: var(--side, 96px);", css)
            build = subprocess.run(
                ["python3", str(SCRIPT.with_name("build_judged_deck.py")), str(deck / "deck.src.html")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            self.assertIn('class="tart"', (deck / "deck.html").read_text(encoding="utf-8"))

    def test_a_broken_template_leaves_no_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            broken = root / "broken.pptx"
            import zipfile

            with zipfile.ZipFile(broken, "w") as z:
                z.writestr("ppt/presentation.xml", "<broken")
            result = self.run_judged(root, "--template", str(broken))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ERROR", result.stderr)
            self.assertEqual(list((root / "output").glob("*")) if (root / "output").exists() else [], [])

    def test_template_requires_judged_direction(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "sample-topic",
                    "--root",
                    folder,
                    "--production-direction",
                    "text",
                    "--template",
                    "template.pptx",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--template", result.stderr)

    def test_judged_direction_rejects_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_judged(Path(folder), "--mode", "presentation")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("judged", result.stderr)

    def test_production_direction_is_required(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "sample-topic",
                    "--date",
                    "20260724",
                    "--root",
                    folder,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--production-direction", result.stderr)


if __name__ == "__main__":
    unittest.main()
