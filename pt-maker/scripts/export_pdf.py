#!/usr/bin/env python3
"""pt-maker: reveal.js .html → .pdf through background browser-harness.

사용:
  python export_pdf.py deck.html [out.pdf]

browser-harness가 없으면 공식 uv 설치 경로로 자동 설치·스킬 등록한다.
사용자의 보이는 Chrome에는 연결하지 않고 임시 프로필의 headless Chrome을 쓴다.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from browser_harness_runtime import BrowserHarnessError, print_reveal_pdf


def run_guards(html: Path):
    for script, label in (
        ("qa_html_guard.py", "HTML/motion/accessibility"),
        ("qa_media_guard.py", "media/map"),
    ):
        guard = Path(__file__).with_name(script)
        r = subprocess.run([sys.executable, str(guard), str(html)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write((r.stdout or "") + (r.stderr or ""))
            sys.exit(f"ERROR: {script} blocked PDF export. Fix {label} P0 findings first.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out", nargs="?")
    args = ap.parse_args()

    html = Path(args.html).resolve()
    if not html.is_file():
        sys.exit(f"ERROR: 파일 없음: {html}")
    out = Path(args.out).resolve() if args.out else html.with_suffix(".pdf")
    run_guards(html)
    try:
        print_reveal_pdf(html, out)
    except BrowserHarnessError as exc:
        sys.exit(f"ERROR: browser-harness PDF export failed: {exc}")
    print(f"OK: {out} (isolated background browser-harness)")


if __name__ == "__main__":
    main()
