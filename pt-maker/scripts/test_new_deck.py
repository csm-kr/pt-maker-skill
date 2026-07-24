#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "new_deck.py"


class NewDeckTests(unittest.TestCase):
    def run_new_deck(self, root: Path, mode: str) -> Path:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "sample-topic",
                "--date",
                "20260724",
                "--root",
                str(root),
                "--mode",
                mode,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(result.stdout.strip().splitlines()[-1])

    def test_presentation_mode_is_backward_compatible(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.run_new_deck(Path(folder), "presentation")
            self.assertTrue((deck / "deck.html").is_file())
            self.assertTrue((deck / "assets" / "CREDITS.txt").is_file())
            self.assertFalse((deck / "animation").exists())

    def test_animation_mode_creates_pinned_hyperframes_project(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.run_new_deck(Path(folder), "animation")
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
            first = self.run_new_deck(root, "presentation")
            second = self.run_new_deck(root, "both")
            self.assertTrue(first.name.startswith("01_"))
            self.assertTrue(second.name.startswith("02_"))
            self.assertTrue((second / "deck.html").is_file())
            self.assertTrue((second / "animation" / "index.html").is_file())
            ledger = json.loads((second / "motion-ledger.json").read_text())
            self.assertEqual(ledger["mode"], "both")


if __name__ == "__main__":
    unittest.main()
