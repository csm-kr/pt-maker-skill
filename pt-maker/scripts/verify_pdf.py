#!/usr/bin/env python3
"""pt-maker: PDF 마감 검증 — 전 페이지를 콘택트 시트로 렌더해 bleed/잘림을 눈으로 확인.

사용:
  python verify_pdf.py deck.pdf [--out out/_contact.png] [--cols 4]

검사:
  - 페이지 수 출력
  - 각 페이지 MediaBox 비율이 16:9(≈1.778)인지 (아니면 용지 불일치 경고)
  - 모든 페이지를 한 장의 콘택트 시트 PNG로 합침 → Read로 열어 슬라이드 비침/잘림 확인

배경: reveal print-pdf는 .pdf-page 높이가 @page보다 1px 작으면(기본 pdfPageHeightOffset=-1)
페이지마다 어긋나 다음/이전 슬라이드가 비친다. 템플릿은 center:false + pdfPageHeightOffset:0으로
이를 막는다. 이 스크립트로 결과 PDF를 캡처 검증한다.

의존성(표준 아님): pip install pymupdf pillow
"""
import argparse, sys
from pathlib import Path

try:
    import fitz  # pymupdf
    from PIL import Image
except ImportError:
    sys.exit("ERROR: pip install pymupdf pillow 후 다시 실행하세요.")


def main():
    try:  # Windows cp949 콘솔에서 한글/특수문자 출력 깨짐·크래시 방지
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default=None, help="콘택트 시트 출력 경로 (기본: <pdf>_contact.png)")
    ap.add_argument("--cols", type=int, default=4)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.is_file():
        sys.exit(f"ERROR: 파일 없음: {pdf}")
    out = Path(args.out) if args.out else pdf.with_name(pdf.stem + "_contact.png")

    doc = fitz.open(str(pdf))
    n = doc.page_count
    print(f"pages: {n}")

    # 비율 검사 (16:9 = 1.778)
    bad_ratio = []
    for i in range(n):
        r = doc[i].rect
        ratio = r.width / r.height if r.height else 0
        if abs(ratio - 16 / 9) > 0.02:
            bad_ratio.append((i + 1, round(ratio, 3)))
    if bad_ratio:
        print(f"WARN: 16:9가 아닌 페이지 {len(bad_ratio)}개 (용지 불일치 → bleed 위험): {bad_ratio[:8]}")
    else:
        print("ratio: 전 페이지 16:9 OK")

    # 콘택트 시트
    cols = args.cols
    rows = (n + cols - 1) // cols
    tw, th, pad = 300, 169, 6
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * th + (rows + 1) * pad), (40, 23, 74))
    for i in range(n):
        pg = doc[i]
        zoom = tw / pg.rect.width
        pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).resize((tw, th))
        rr, cc = divmod(i, cols)
        sheet.paste(img, (pad + cc * (tw + pad), pad + rr * (th + pad)))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(out))
    print(f"OK: {out}  ({sheet.size[0]}x{sheet.size[1]}) - Read로 열어 비침/잘림을 확인하세요.")


if __name__ == "__main__":
    main()
