#!/usr/bin/env python3

from __future__ import annotations

import base64
import contextlib
import io
import json
import re
import unittest
from pathlib import Path

import qa_animated_presentation


SPIKE = {
    "frames": 9,
    "maxFrameMs": 450.0,
    "averageFrameMs": 60.0,
    "framesOver25Ms": 1,
    "framesOver40Ms": 1,
}
SMOOTH = {
    "frames": 48,
    "maxFrameMs": 16.8,
    "averageFrameMs": 16.7,
    "framesOver25Ms": 0,
    "framesOver40Ms": 0,
}


class FakePresenter:
    """Minimal stand-in for browser-harness globals driving a 3-slide deck."""

    def __init__(self, spike_calls: set[int], count: int = 3) -> None:
        self.spike_calls = spike_calls
        self.count = count
        self.index = 0
        self.progress = 1.0
        self.profile_calls = 0

    def state(self) -> dict[str, object]:
        return {
            "index": self.index,
            "count": self.count,
            "sceneId": f"scene-{self.index + 1}",
            "transitionFamily": "cut",
            "timelineProgress": self.progress,
            "runtimeError": False,
        }

    def go(self, target: int) -> None:
        self.index = max(0, min(self.count - 1, target))
        self.progress = 1.0

    def js(self, expression: str):
        go = re.search(r"__ptMakerPresenter\.go\((\d+)", expression)
        if go:
            self.go(int(go.group(1)))
            return self.index
        if "?.ready" in expression:
            return True
        if ".animated-slide').length" in expression or "__timelines ||" in expression:
            return self.count
        if "document.images" in expression:
            return True
        if "transitionContract" in expression:
            return {"theme": "paper", "families": ["cut", "paper"], "required": [], "jump": "cut"}
        if "replay()" in expression:
            self.progress = .05
            return None
        if "pointerdown" in expression:
            self.go(self.index + 1)
            return True
        if "state().transitionFamily" in expression:
            return "cut"
        if "state()" in expression:
            return self.state()
        if expression.strip() == "window.__ptMakerPresenter.index":
            return self.index
        return None

    def cdp(self, method: str, **params):
        if method == "Runtime.evaluate":
            self.profile_calls += 1
            target = re.search(r"__ptMakerPresenter\.go\((\d+)\)", params["expression"])
            self.go(int(target.group(1)))
            sample = SPIKE if self.profile_calls in self.spike_calls else SMOOTH
            return {"result": {"value": dict(sample)}}
        if method == "Input.dispatchKeyEvent" and params.get("type") == "keyDown":
            self.go(self.index + 1)
        return {}


def run_generated_qa(spike_calls: set[int]) -> dict[str, object]:
    fake = FakePresenter(spike_calls)
    namespace = {
        "new_tab": lambda *_: None,
        "goto_url": lambda *_: None,
        "wait_for_load": lambda *_: True,
        "wait_for_element": lambda *_, **__: True,
        "wait": lambda *_: None,
        "js": fake.js,
        "cdp": fake.cdp,
        "Path": Path,
        "json": json,
        "base64": base64,
    }
    code = qa_animated_presentation.qa_code(Path("/tmp/deck.html"), None)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(code, namespace)
    return json.loads(stdout.getvalue().strip().splitlines()[-1])


class TransitionWarmupTests(unittest.TestCase):
    def test_first_transition_spike_is_warmup_not_a_failure(self):
        result = run_generated_qa(spike_calls={1})
        self.assertEqual(result["animated_presentation_qa"], "pass")
        performance = result["transition_performance"]
        self.assertEqual(performance["frames_over_40ms"], 0)
        self.assertEqual(result["transition_warmup"][0]["maxFrameMs"], 450.0)

    def test_spike_after_warmup_still_fails(self):
        with self.assertRaisesRegex(RuntimeError, "Transition performance exceeded 40ms"):
            run_generated_qa(spike_calls={4})


if __name__ == "__main__":
    unittest.main()
