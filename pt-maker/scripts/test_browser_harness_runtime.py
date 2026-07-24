#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import browser_harness_runtime as runtime


VALID_SKILL = """---
name: browser-harness
description: test
---

# browser-harness
"""


class BrowserHarnessBootstrapTests(unittest.TestCase):
    def test_existing_binary_and_registration_are_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            registered = home / "skills" / "browser-harness" / "SKILL.md"
            registered.parent.mkdir(parents=True)
            registered.write_text(VALID_SKILL, encoding="utf-8")
            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(
                    runtime,
                    "_locate_browser_harness",
                    return_value=Path("/fake/browser-harness"),
                ),
                mock.patch.object(runtime, "_run") as run,
            ):
                executable = runtime.ensure_browser_harness(quiet=True)
            self.assertEqual(executable, Path("/fake/browser-harness"))
            run.assert_not_called()

    def test_missing_registration_is_generated_from_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            completed = subprocess.CompletedProcess(
                ["browser-harness", "skill"],
                0,
                stdout=VALID_SKILL,
                stderr="",
            )
            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(
                    runtime,
                    "_locate_browser_harness",
                    return_value=Path("/fake/browser-harness"),
                ),
                mock.patch.object(
                    runtime,
                    "_run",
                    return_value=completed,
                ),
            ):
                runtime.ensure_browser_harness(quiet=True)
            self.assertEqual(
                (home / "skills/browser-harness/SKILL.md").read_text(
                    encoding="utf-8"
                ),
                VALID_SKILL,
            )

    def test_missing_binary_installs_with_official_uv_tool_path(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            fake_binary = Path("/fake/browser-harness")
            calls: list[list[str]] = []

            def fake_run(command, **kwargs):
                normalized = [str(part) for part in command]
                calls.append(normalized)
                if normalized[-1:] == ["skill"]:
                    return subprocess.CompletedProcess(
                        normalized, 0, stdout=VALID_SKILL, stderr=""
                    )
                return subprocess.CompletedProcess(
                    normalized, 0, stdout="", stderr=""
                )

            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(
                    runtime,
                    "_locate_browser_harness",
                    side_effect=[None, fake_binary],
                ),
                mock.patch.object(
                    runtime,
                    "_bootstrap_uv",
                    return_value=Path("/fake/uv"),
                ),
                mock.patch.object(runtime, "_run", side_effect=fake_run),
            ):
                executable = runtime.ensure_browser_harness(quiet=True)

            self.assertEqual(executable, fake_binary)
            install = next(call for call in calls if "install" in call)
            self.assertEqual(
                install,
                [
                    "/fake/uv",
                    "tool",
                    "install",
                    "--python",
                    "3.12",
                    "--upgrade",
                    "--force",
                    "browser-harness",
                ],
            )
            self.assertIn(
                ["/fake/browser-harness", "recordings", "disable"],
                calls,
            )
            self.assertTrue(
                (home / "skills/browser-harness/SKILL.md").is_file()
            )

    def test_check_mode_fails_without_installing(self):
        with mock.patch.object(
            runtime,
            "_locate_browser_harness",
            return_value=None,
        ):
            with self.assertRaises(runtime.BrowserHarnessError):
                runtime.ensure_browser_harness(
                    install=False,
                    quiet=True,
                )

    def test_complete_background_gate_checks_chrome(self):
        with (
            mock.patch.object(
                runtime,
                "ensure_browser_harness",
                return_value=Path("/fake/browser-harness"),
            ),
            mock.patch.object(
                runtime,
                "find_chrome",
                return_value=Path("/fake/chrome"),
            ),
        ):
            self.assertEqual(
                runtime.ensure_background_runtime(quiet=True),
                (
                    Path("/fake/browser-harness"),
                    Path("/fake/chrome"),
                ),
            )


if __name__ == "__main__":
    unittest.main()
