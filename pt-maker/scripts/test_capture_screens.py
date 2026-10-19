#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

import capture_screens as capture
from browser_harness_runtime import BrowserHarnessError, ensure_background_runtime


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    """Width and height from the first JPEG frame header (test helper)."""
    index = 2
    while data.startswith(b"\xff\xd8") and index + 9 <= len(data):
        marker, length = data[index + 1], struct.unpack(">H", data[index + 2: index + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[index + 5: index + 9])
            return width, height
        index += 2 + length
    return None


def fake_jpeg(width: int, height: int) -> bytes:
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    sof0 = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, height, width, 1) + b"\x01\x11\x00"
    return b"\xff\xd8" + app0 + sof0 + b"\xff\xd9"


class ShotSpecTests(unittest.TestCase):
    def test_defaults_are_filled(self):
        shots = capture.validate_shots({"shots": [{"name": "home", "url": "https://example.com/"}]})
        shot = shots[0]
        self.assertEqual(shot["viewport"], [1440, 900])
        self.assertEqual(shot["scale"], 2)
        self.assertEqual(shot["clip"], [0, 0, 1440, 900])
        self.assertEqual(shot["width"], 2880)
        self.assertEqual(shot["quality"], 85)
        self.assertEqual(shot["steps"], [])

    def test_bad_specs_are_rejected(self):
        bad = [
            {"name": "Bad Name", "url": "https://example.com"},
            {"name": "a", "url": "ftp://example.com"},
            {"name": "a", "url": "https://example.com", "quality": 0},
            {"name": "a", "url": "https://example.com", "clip": [0, 0, 0, 10]},
            {"name": "a", "url": "https://example.com", "steps": [{"hover": "#x"}]},
            {"name": "a", "url": "https://example.com", "steps": [{"type": "#x"}]},
        ]
        for spec in bad:
            with self.assertRaises(capture.ShotError, msg=spec):
                capture.validate_shots({"shots": [spec]})
        with self.assertRaises(capture.ShotError):
            capture.validate_shots({"shots": [{"name": "a", "url": "https://e.com"}, {"name": "a", "url": "https://e.com"}]})

    def test_clip_scale_hits_the_output_width(self):
        self.assertAlmostEqual(capture.clip_scale(clip_width=500, device_scale=2, width=600), 0.6)

    def test_jpeg_size_helper(self):
        self.assertEqual(jpeg_size(fake_jpeg(760, 1354)), (760, 1354))
        self.assertIsNone(jpeg_size(b"not a jpeg"))

    def test_credits_line_is_replaced_on_recapture(self):
        with tempfile.TemporaryDirectory() as folder:
            credits = Path(folder) / "CREDITS.txt"
            credits.write_text(
                "# asset | source/generation mode | URL or prompt note | accessed/generated date\n"
                "assets/img/home.jpg | real capture (capture_screens.py) | https://old | 2026-10-01T10:00:00+09:00\n"
                "assets/img/other.jpg | public source | https://x | 2026-10-01\n",
                encoding="utf-8",
            )
            capture.record_credit(credits, "assets/img/home.jpg", "https://new", "2026-10-19T13:00:00+09:00")
            capture.record_credit(credits, "assets/img/third.jpg", "https://third", "2026-10-19T13:01:00+09:00")
            lines = credits.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 4)
        self.assertIn("assets/img/home.jpg | real capture (capture_screens.py) | https://new | 2026-10-19T13:00:00+09:00", lines)
        self.assertNotIn("https://old", "\n".join(lines))
        self.assertTrue(lines[-1].startswith("assets/img/third.jpg"))

    def test_browser_code_uses_jpeg_clip(self):
        shots = capture.validate_shots({"shots": [{"name": "home", "url": "https://example.com/", "width": 600}]})
        code = capture.browser_code(shots, Path("/tmp/img"))
        self.assertIn('format="jpeg"', code)
        self.assertIn("captureBeyondViewport=True", code)


def chrome_available() -> bool:
    try:
        ensure_background_runtime(install=False, quiet=True)
        return True
    except BrowserHarnessError:
        return False


PAGE = """<!doctype html><html><body style="margin:0;font:24px sans-serif">
<input id="q" style="margin:20px;font-size:24px">
<button id="go" style="margin:20px;font-size:24px" onclick="document.getElementById('out').innerHTML='<p class=result>Hello ' + document.getElementById('q').value + '</p>'">Go</button>
<div id="out" style="margin:20px"></div>
</body></html>"""


@unittest.skipUnless(chrome_available(), "Chrome and browser-harness are required for the capture test")
class RenderedCaptureTests(unittest.TestCase):
    def test_steps_clip_and_width(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            page = root / "site" / "index.html"
            page.parent.mkdir()
            page.write_text(PAGE, encoding="utf-8")
            (root / "assets").mkdir()
            shots = root / "shots.json"
            shots.write_text(
                json.dumps(
                    {
                        "shots": [
                            {
                                "name": "answer",
                                "url": page.as_uri(),
                                "viewport": [800, 600],
                                "scale": 2,
                                "steps": [{"type": ["#q", "judges"]}, {"click": "#go"}, {"wait": ".result"}],
                                "clip": [0, 0, 500, 300],
                                "width": 300,
                                "quality": 80,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            results = capture.run(shots)
            output = root / "assets" / "img" / "answer.jpg"
            self.assertTrue(output.is_file())
            self.assertEqual(jpeg_size(output.read_bytes()), (300, 180))
            self.assertEqual(results[0]["width"], 300)
            credits = (root / "assets" / "CREDITS.txt").read_text(encoding="utf-8")
            self.assertIn(f"assets/img/answer.jpg | real capture (capture_screens.py) | {page.as_uri()} |", credits)


if __name__ == "__main__":
    unittest.main()
