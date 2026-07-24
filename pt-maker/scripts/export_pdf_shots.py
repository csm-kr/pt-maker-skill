#!/usr/bin/env python3
"""pt-maker: reveal.js .html → .pdf — HTML 렌더 스샷을 그대로 합쳐 화면과 1:1.

언제 쓰나: 기본 export_pdf.py(reveal `?print-pdf` 경로)는 print용 pdf.css + Chromium
인쇄 엔진 + 폰트 로드 타이밍 때문에 화면(paper.css)보다 줄간격이 좁게 나올 수 있다.
화면 그대로를 PDF로 보장하려면 이 스크립트로 각 슬라이드를 고해상도 스샷 떠서 합친다.

사용:
  python export_pdf_shots.py deck.html ["<주제>.pdf"] [--width 2048]
  - out 생략 시 deck.pdf. 산출물은 주제 이름으로 저장 권장(예: "커피의 기원.pdf").

의존성: browser-harness background(없으면 자동 설치) + pymupdf(합치기).
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from browser_harness_runtime import (
    BrowserHarnessError,
    capture_reveal_slides,
)

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("ERROR: pip install pymupdf 후 다시 실행하세요.")


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
    ap.add_argument("--width", type=int, default=2048, help="스샷 가로 px(16:9). reveal maxScale 1.6 → 1280*1.6=2048 권장")
    args = ap.parse_args()

    html = Path(args.html).resolve()
    if not html.is_file():
        sys.exit(f"ERROR: 파일 없음: {html}")
    out = Path(args.out).resolve() if args.out else html.with_suffix(".pdf")
    run_guards(html)

    w = args.width
    tmp = Path(tempfile.mkdtemp(prefix="pt-maker-shots-"))
    try:
        try:
            pngs = capture_reveal_slides(html, tmp, width=w)
        except BrowserHarnessError as exc:
            sys.exit(f"ERROR: browser-harness screenshot export failed: {exc}")

        doc = fitz.open()
        for p in pngs:
            img = fitz.open(str(p))
            pdfb = img.convert_to_pdf()
            img.close()
            src = fitz.open("pdf", pdfb)
            page = doc.new_page(width=1280, height=720)  # 16:9
            page.show_pdf_page(page.rect, src, 0)
            src.close()
        out.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(out))
        page_count = doc.page_count
        doc.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(
        f"OK: {out} ({page_count} pages, "
        "isolated background browser-harness shots)"
    )


if __name__ == "__main__":
    main()
