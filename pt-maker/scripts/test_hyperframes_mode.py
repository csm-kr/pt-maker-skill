#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import hyperframes_mode


ANIMATION = (
    Path(__file__).resolve().parent.parent / "assets" / "animation-mode"
)


class HyperFramesModeTests(unittest.TestCase):
    def test_resolve_animation_project(self):
        self.assertEqual(
            hyperframes_mode.resolve_project(ANIMATION),
            ANIMATION.resolve(),
        )

    def test_commands_pin_version_and_options(self):
        args = argparse.Namespace(
            action="render",
            output=None,
            quality="high",
            fps=60,
            format="webm",
        )
        command = hyperframes_mode.build_command(args, ANIMATION)
        self.assertEqual(command[:3], ["npx", "--yes", "hyperframes@0.7.70"])
        self.assertIn("high", command)
        self.assertIn("60", command)
        self.assertIn("webm", command)

    def test_background_worker_keeps_render_gate_arguments(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "render.json"
            ledger = Path(folder) / "ledger.json"
            args = argparse.Namespace(
                action="render",
                snapshots=False,
                strict=False,
                samples=None,
                port=4567,
                quality="standard",
                fps=30,
                format="mp4",
                output="renders/sample.mp4",
                approved=True,
                qa_ledger=ledger,
                dry_run=False,
            )
            command = hyperframes_mode.worker_command(args, ANIMATION, state)
        self.assertIn("--approved", command)
        self.assertIn("--qa-ledger", command)
        self.assertIn("--background-worker", command)
        self.assertNotIn("--background", command)
        output = command[command.index("--output") + 1]
        self.assertTrue(Path(output).is_absolute())

    def test_status_reports_completed_job(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            state = hyperframes_mode.state_path_for(project, "check")
            hyperframes_mode.write_state(
                state,
                {
                    "action": "check",
                    "status": "completed",
                    "pid": 999999,
                    "exit_code": 0,
                },
            )
            with mock.patch("builtins.print") as printed:
                result = hyperframes_mode.status_background(project)
        self.assertEqual(result, 0)
        payload = json.loads(printed.call_args.args[0])
        self.assertEqual(payload["jobs"][0]["status"], "completed")
        self.assertFalse(payload["jobs"][0]["alive"])

    def test_preview_rejects_foreground_execution(self):
        with (
            mock.patch.object(
                sys,
                "argv",
                [
                    "hyperframes_mode.py",
                    "preview",
                    str(ANIMATION),
                ],
            ),
            mock.patch("builtins.print"),
        ):
            result = hyperframes_mode.main()
        self.assertEqual(result, 2)

    def test_background_preview_checks_browser_harness(self):
        with (
            mock.patch.object(
                sys,
                "argv",
                [
                    "hyperframes_mode.py",
                    "preview",
                    str(ANIMATION),
                    "--background",
                    "--dry-run",
                ],
            ),
            mock.patch.object(
                hyperframes_mode,
                "ensure_background_runtime",
            ) as ensure,
            mock.patch("builtins.print"),
        ):
            result = hyperframes_mode.main()
        self.assertEqual(result, 0)
        ensure.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
