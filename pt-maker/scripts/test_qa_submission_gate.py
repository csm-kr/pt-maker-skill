#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import qa_submission_gate as gate


SCRIPT = Path(__file__).resolve().parent / "qa_submission_gate.py"

TEMPLATE = {
    "slide_size": {"px": [1920, 1080]},
    "slides": [
        {"index": 1, "title": "Cover"},
        {"index": 2, "title": "The idea"},
        {"index": 3, "title": "Links"},
    ],
}


class Handler(BaseHTTPRequestHandler):
    """/ok: 200. /picky: 403 unless the request looks like a browser, as some sites behind bot rules
    require: Accept with text/html, an Accept-Language, and a browser User-Agent (a made-up
    "Mozilla/5.0 (tool name)" string was refused by real sites). /get-only: HEAD not allowed, GET is
    picky. Anything else: 404."""

    def browser_like(self) -> bool:
        agent = self.headers.get("User-Agent", "")
        return (
            "text/html" in self.headers.get("Accept", "")
            and bool(self.headers.get("Accept-Language"))
            and "AppleWebKit" in agent
            and "Chrome/" in agent
        )

    def answer(self, method: str) -> None:
        if self.path == "/ok":
            code = 200
        elif self.path == "/picky":
            code = 200 if self.browser_like() else 403
        elif self.path == "/get-only":
            code = 405 if method == "HEAD" else (200 if self.browser_like() else 403)
        else:
            code = 404
        self.send_response(code)
        self.end_headers()

    def do_HEAD(self):
        self.answer("HEAD")

    def do_GET(self):
        self.answer("GET")

    def log_message(self, *args):
        pass


def pdf_bytes(pages: int, padding: int = 0) -> bytes:
    body = b"".join(b"%d 0 obj << /Type /Page /MediaBox [0 0 1440 810] >> endobj\n" % (i + 2) for i in range(pages))
    return b"%PDF-1.4\n1 0 obj << /Type /Pages >> endobj\n" + body + b"%" + b"x" * padding + b"\n"


def slide(slot: int | None, title: str, body: str = "") -> str:
    attr = f' data-slot="{slot}" data-tpl="{slot}"' if slot else ""
    return f'<section class="slide"{attr} data-main><div class="tt nowc">{title}</div><h1>Claim</h1>{body}</section>'


class SubmissionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "template.json").write_text(json.dumps(TEMPLATE), encoding="utf-8")
        self.config = {"template": "template.json", "limits": {"max_pages": 30, "max_mb": 5}, "slots": {"skip": []}}

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def check(self, slides: list[str], *, pages: int | None = None, offline: bool = True, stale: bool = False, padding: int = 0) -> dict:
        deck = self.root / "deck.html"
        pdf = self.root / "deck.pdf"
        deck.write_text('<!doctype html><html data-deck="judged"><body>' + "".join(slides) + "</body></html>", encoding="utf-8")
        pdf.write_bytes(pdf_bytes(len(slides) if pages is None else pages, padding))
        if stale:
            os.utime(pdf, (1_000_000_000, 1_000_000_000))
        return gate.run_checks(deck, pdf, self.config, config_dir=self.root, offline=offline)

    def codes(self, result: dict) -> set[str]:
        return {error["code"] for error in result["errors"]}

    def good(self, link: str = "") -> list[str]:
        return [
            slide(1, "Cover"),
            slide(2, "The idea"),
            slide(None, "", "<p>An extra page</p>"),
            slide(3, "Links", link),
        ]

    def test_clean_submission_passes_online(self):
        result = self.check(self.good(f'<a href="{self.base}/ok">demo</a>'), offline=False)
        self.assertEqual(result["qa_submission_gate"], "pass", result["errors"])
        self.assertEqual(result["links"], [{"url": f"{self.base}/ok", "status": 200}])

    def test_placeholders_left(self):
        slides = self.good('<span class="v ph">VIDEO_URL</span> {{link:GITHUB_URL}} <p>TODO: numbers</p>')
        result = self.check(slides)
        messages = " ".join(error["message"] for error in result["errors"])
        self.assertEqual(self.codes(result), {"placeholder-left"})
        for needle in ("VIDEO_URL", "{{link:GITHUB_URL}}", "TODO"):
            self.assertIn(needle, messages)

    def test_pdf_limits_and_slide_match(self):
        self.config["limits"] = {"max_pages": 3, "max_mb": 0.0002}
        result = self.check(self.good(), padding=400)
        self.assertIn("pdf-too-many-pages", self.codes(result))
        self.assertIn("pdf-too-large", self.codes(result))
        self.config["limits"] = {"max_pages": 30, "max_mb": 5}
        self.assertIn("pdf-slide-mismatch", self.codes(self.check(self.good(), pages=3)))
        self.assertIn("pdf-stale", self.codes(self.check(self.good(), stale=True)))

    def test_slot_order_titles_and_skips(self):
        swapped = [slide(2, "The idea"), slide(1, "Cover"), slide(3, "Links")]
        self.assertIn("slot-order", self.codes(self.check(swapped)))
        missing = [slide(1, "Cover"), slide(2, "The idea")]
        self.assertIn("slot-missing", self.codes(self.check(missing)))
        self.config["slots"] = {"skip": [3]}
        self.assertEqual(self.check(missing)["qa_submission_gate"], "pass")
        retitled = [slide(1, "Cove"), slide(2, "The idea")]
        self.assertIn("slot-title-mismatch", self.codes(self.check(retitled)))

    def test_slot_title_match_modes(self):
        template = json.loads(json.dumps(TEMPLATE))
        template["slides"][1]["title"] = "The idea (max 50 words)"
        template["slides"][2]["title"] = "Click to add your links"
        (self.root / "template.json").write_text(json.dumps(template), encoding="utf-8")
        pages = [slide(1, "Cover"), slide(2, "The idea"), slide(3, "Where to find it")]
        self.assertEqual(self.codes(self.check(pages)), {"slot-title-mismatch"})
        template["slides"][1]["match"] = "prefix"
        template["slides"][2]["match"] = "skip"
        (self.root / "template.json").write_text(json.dumps(template), encoding="utf-8")
        self.assertEqual(self.check(pages)["qa_submission_gate"], "pass")
        self.assertIn("slot-title-mismatch", self.codes(self.check([slide(1, "Cover"), slide(2, "Idea"), slide(3, "x")])))

    def test_links_send_browser_like_headers(self):
        for path in ("/picky", "/get-only"):
            with self.subTest(path=path):
                self.assertEqual(gate.check_link(f"{self.base}{path}")["status"], 200)
        result = self.check(self.good(f'<a href="{self.base}/picky">a</a> <a href="{self.base}/get-only">b</a>'), offline=False)
        self.assertEqual(result["qa_submission_gate"], "pass", result["errors"])

    def test_broken_link_fails_and_offline_skips(self):
        slides = self.good(f'<a href="{self.base}/missing">repo</a>')
        online = self.check(slides, offline=False)
        self.assertIn("link-not-ok", self.codes(online))
        offline = self.check(slides, offline=True)
        self.assertEqual(offline["qa_submission_gate"], "pass", offline["errors"])
        self.assertEqual(offline["links"], "skipped (--offline)")

    def test_cli(self):
        deck = self.root / "deck.html"
        pdf = self.root / "deck.pdf"
        deck.write_text("<html><body>" + "".join(self.good()) + "</body></html>", encoding="utf-8")
        pdf.write_bytes(pdf_bytes(4))
        config = self.root / "judged.json"
        config.write_text(json.dumps(self.config), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(deck), str(pdf), "--config", str(config), "--offline"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("qa-submission-gate: pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
