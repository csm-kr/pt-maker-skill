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
