#!/usr/bin/env python3
"""pt-maker judged mode: rendered layout gate, slide PNGs, slide text and the PDF.

심사용 덱(deck.html)을 격리 background browser-harness에서 템플릿 크기로 렌더링해 레이아웃을 검사하고,
slides/NN.png, slides/text.txt(심사 패널용 슬라이드 글자), 템플릿의 실제 쪽 크기(인치)로 인쇄한 PDF를 만든다.

사용:
  python qa_layout_gate.py deck.html [--config judged.json] [--template template.json]
                           [--pdf out.pdf] [--slides-dir slides] [--json]

검사 (슬라이드마다, .slide 하나 = PDF 한 쪽). 글자 위치는 요소 상자가 아니라 실제 글줄(Range rect)로 잰다:
  small-text       min_font_px보다 작은 글자 (CSS transform 배율과 SVG viewBox 배율을 곱한 실제 크기)
  edge             글자가 슬라이드 가장자리 여백(좌우 40, 위아래 10 px) 안으로 들어옴
  overflow-x       글자 줄이 자기 상자(내용 영역) 오른쪽으로 넘침 (scrollWidth로 거른 뒤 글줄 위치로 확인)
  under-art        글자가 템플릿 아트 영역(여유 4 px) 밑에 깔림 (템플릿 제목 상자 안의 글자와 .tart는 제외)
  covered-by-art   템플릿 제목 상자 안의 글자를 템플릿 아트가 덮음 (그리는 순서 오류)
  box-under-art    .card/figure/img/svg/.dots가 템플릿 아트 영역에 걸침 (.crop 안의 것은 제외)
  footer-overlap   footer(.ft) 밖의 글자가 footer와 겹침 (간격 6 px 미만)
  box-into-footer  상자가 footer 위쪽 경계를 넘음
  footer-lines     footer 출처(.ft .src)가 max_footer_lines줄을 넘음
  clipped          .card/p/h1/h2/h3/li/figcaption/td/th 내용이 잘림
  broken-image     로드되지 않은 이미지
  words-over       본편 슬라이드([data-main]) 단어 수가 max_words_per_slide를 넘음 (.ft, .nowc 제외)
  slide-size       .slide 크기가 템플릿 크기와 다름
  pdf-pages        PDF 쪽수가 .slide 수와 다름 (압축 object stream 안의 쪽도 센다)
  pdf-size         PDF 쪽 크기가 템플릿의 실제 쪽 크기와 다름

기준값: judged.json(layout.min_font_px, layout.max_footer_lines, limits.max_words_per_slide)
> template.json(slide_size, min_font_px, 슬라이드별 art와 title_box) > 기본값.
아트 영역은 슬라이드의 data-tpl="N"(템플릿 N번 슬라이드)으로 고른다.
템플릿이 없으면 1920×1080(20×11.25 in), 최소 글자 22.5 px(1280 기준 fine-print 15 px를 1920으로 환산)를 쓴다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zlib
from pathlib import Path
from typing import Any

from browser_harness_runtime import BrowserHarnessError, IsolatedBrowserHarness

DEFAULT_SIZE = (1920, 1080)

CHECK_JS = r"""
((cfg) => {
  const EDGE = { left: 40, right: 40, top: 10, bottom: 10 };
  const ART_MARGIN = 4, FOOTER_GAP = 6, TITLE_MARGIN = 8;
  const out = [];
  const said = new Set();
  const words = [];
  const texts = [];
  const add = (slide, kind, message) => {
    const key = `${slide}|${kind}|${message}`;
    if (!said.has(key)) { said.add(key); out.push({ slide, kind, message }); }
  };
  const label = (el) => (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) || el.tagName;
  // The size a reader sees: font size times every CSS transform scale on the way up.
  const scaleOf = (el) => {
    let scale = 1;
    for (let node = el; node && node.nodeType === 1; node = node.parentElement) {
      const t = getComputedStyle(node).transform;
      if (t && t !== "none") { const m = new DOMMatrix(t); scale *= Math.sqrt(Math.abs(m.a * m.d - m.b * m.c)); }
    }
    return scale;
  };
  // Where the text itself is drawn (each line box), not the box of its element.
  const textRect = (node, el) => {
    const range = document.createRange();
    range.selectNodeContents(node);
    const rects = Array.from(range.getClientRects()).filter((r) => r.width > 0 && r.height > 0);
    if (!rects.length) {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 ? r : null;
    }
    return {
      left: Math.min(...rects.map((r) => r.left)), right: Math.max(...rects.map((r) => r.right)),
      top: Math.min(...rects.map((r) => r.top)), bottom: Math.max(...rects.map((r) => r.bottom)),
      get height() { return this.bottom - this.top; },
    };
  };
  // Template art is pointer-events: none, which hides it from elementFromPoint; make it hit-testable while checking.
  const hit = document.createElement("style");
  hit.textContent = ".tart, .tart * { pointer-events: auto !important; }";
  document.head.appendChild(hit);
  const slides = Array.from(document.querySelectorAll(".slide"));
  slides.forEach((slide, i) => {
    window.scrollTo(0, slide.getBoundingClientRect().top + window.scrollY);
    const pg = slide.querySelector(".pg b") || slide.querySelector(".pg");
    const n = (pg && pg.textContent.trim()) || String(i + 1).padStart(2, "0");
    const s = slide.getBoundingClientRect();
    if (Math.abs(s.width - cfg.width) > 0.5 || Math.abs(s.height - cfg.height) > 0.5) {
      add(n, "slide-size", `slide is ${Math.round(s.width)}x${Math.round(s.height)}, expected ${cfg.width}x${cfg.height}`);
    }
    const key = slide.getAttribute("data-tpl");
    const zones = (key && cfg.zones[key]) || [];
    const titleBox = (key && cfg.title_boxes[key]) || null;
    const ft = slide.querySelector(".ft")?.getBoundingClientRect();
    const rel = (r) => ({ left: r.left - s.left, right: r.right - s.left, top: r.top - s.top, bottom: r.bottom - s.top });
    const inTitle = (r) => {
      if (!titleBox) return false;
      const q = rel(r), b = titleBox, m = TITLE_MARGIN;
      return q.left >= b.x - m && q.right <= b.x + b.w + m && q.top >= b.y - m && q.bottom <= b.y + b.h + m;
    };
    const underArt = (r) => {
      if (r.height <= 0 || inTitle(r)) return false;
      const q = rel(r), m = ART_MARGIN;
      return zones.some((z) => q.left < z.x + z.w + m && q.right > z.x - m && q.top < z.y + z.h + m && q.bottom > z.y - m);
    };
    const pos = (r) => `(${Math.round(r.left - s.left)},${Math.round(r.top - s.top)} → ${Math.round(r.right - s.left)},${Math.round(r.bottom - s.top)})`;
    for (const img of slide.querySelectorAll("img")) {
      if (!img.complete || img.naturalWidth === 0) add(n, "broken-image", `broken image ${img.getAttribute("src")}`);
    }
    const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
    let count = 0;
    while (walker.nextNode()) {
      const node = walker.currentNode;
      const t = node.textContent.trim();
      if (!t) continue;
      const el = node.parentElement;
      const r = textRect(node, el);
      if (!r) continue;
      if (!el.closest(".ft") && !el.closest(".nowc")) count += t.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;
      let size = parseFloat(getComputedStyle(el).fontSize) * scaleOf(el);
      const svg = el.closest("svg");
      if (svg && svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width) size *= svg.getBoundingClientRect().width / svg.viewBox.baseVal.width / scaleOf(svg);
      const quote = `"${t.slice(0, 50)}"`;
      if (size < cfg.min_font_px - 0.005) add(n, "small-text", `small text ${size.toFixed(1)}px: ${quote}`);
      if (r.right > s.right - EDGE.right || r.left < s.left + EDGE.left || r.bottom > s.bottom - EDGE.bottom || r.top < s.top + EDGE.top) {
        add(n, "edge", `near/over edge: ${quote} ${pos(r)}`);
      }
      if (!el.closest(".tart")) {
        if (underArt(r)) add(n, "under-art", `under template art: ${quote} (${Math.round(r.top - s.top)} → ${Math.round(r.bottom - s.top)})`);
        if (inTitle(r)) {
          const top = document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2);
          if (top && top.closest(".tart")) add(n, "covered-by-art", `template art is drawn over the title: ${quote}`);
        }
      }
      if (ft && !el.closest(".ft") && r.bottom > ft.top - FOOTER_GAP && r.top < ft.bottom) {
        add(n, "footer-overlap", `overlaps footer: ${quote} (bottom ${Math.round(r.bottom - s.top)}, footer top ${Math.round(ft.top - s.top)})`);
      }
    }
    for (const el of slide.querySelectorAll(".card, p, h1, h2, h3, li, figcaption, td, th")) {
      if (el.scrollHeight > el.clientHeight + 2 && getComputedStyle(el).overflow !== "visible") add(n, "clipped", `clipped: ${label(el)}`);
      if (el.scrollWidth > el.clientWidth + 2) {
        // scrollWidth also counts decoration (an arrow in ::after); only text past the content box counts.
        const box = el.getBoundingClientRect(), cs = getComputedStyle(el);
        const right = box.right - parseFloat(cs.borderRightWidth) - parseFloat(cs.paddingRight);
        const texts = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        let past = 0;
        while (texts.nextNode()) {
          if (!texts.currentNode.textContent.trim()) continue;
          const r = textRect(texts.currentNode, texts.currentNode.parentElement);
          if (r) past = Math.max(past, r.right - right);
        }
        if (past > 2) add(n, "overflow-x", `text runs past its box by ${Math.round(past)}px: ${label(el)} "${el.textContent.trim().slice(0, 50)}"`);
      }
    }
    for (const el of slide.querySelectorAll(".card, figure, img, svg, .dots")) {
      if (el.closest(".tart") || (el.parentElement && el.parentElement.closest(".crop"))) continue;
      const r = el.getBoundingClientRect();
      if (underArt(r)) add(n, "box-under-art", `box under template art: ${label(el)} (${Math.round(r.top - s.top)} → ${Math.round(r.bottom - s.top)})`);
      if (ft && !el.closest(".ft") && r.bottom > ft.top - FOOTER_GAP && r.height > 0) {
        add(n, "box-into-footer", `box into footer: ${label(el)} bottom ${Math.round(r.bottom - s.top)} footer top ${Math.round(ft.top - s.top)}`);
      }
    }
    const src = slide.querySelector(".ft .src");
    if (src) {
      const cs = getComputedStyle(src);
      const lineHeight = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
      const lines = Math.round(src.getBoundingClientRect().height / lineHeight);
      if (lines > cfg.max_footer_lines) add(n, "footer-lines", `footer has ${lines} lines (max ${cfg.max_footer_lines})`);
    }
    const main = slide.hasAttribute("data-main");
    if (main && count > cfg.max_words) add(n, "words-over", `${count} words on a main slide (max ${cfg.max_words})`);
    words.push({ slide: n, count, main });
    texts.push({ slide: n, text: slide.innerText.trim() });
  });
  hit.remove();
  window.scrollTo(0, 0);
  return { problems: out, words, texts, count: slides.length };
})
"""

BROWSER_CODE = r"""
new_tab("about:blank")
cdp("Emulation.setDeviceMetricsOverride", width=__WIDTH__, height=__HEIGHT__, deviceScaleFactor=1, mobile=False)
goto_url(__URL__)
if not wait_for_load(30):
    raise RuntimeError("deck did not finish loading")
js("(async () => { if (document.fonts) await document.fonts.ready; await Promise.all(Array.from(document.images).map((img) => img.complete ? 0 : new Promise((done) => { img.onload = img.onerror = done; }))); await new Promise((done) => setTimeout(done, 200)); return true; })()")
check = js(__CHECK__ + "(" + __SETTINGS__ + ")")
slides_dir = Path(__SLIDES__)
slides_dir.mkdir(parents=True, exist_ok=True)
for old in slides_dir.glob("[0-9][0-9].png"):
    old.unlink()
(slides_dir / "text.txt").write_text("".join(f"=== {t['slide']} ===\n{t['text']}\n\n" for t in check["texts"]), encoding="utf-8")
rects = js("Array.from(document.querySelectorAll('.slide')).map((s) => { const r = s.getBoundingClientRect(); return [r.left + scrollX, r.top + scrollY, r.width, r.height]; })")
for index, rect in enumerate(rects):
    shot = cdp("Page.captureScreenshot", format="png", captureBeyondViewport=True, clip={"x": rect[0], "y": rect[1], "width": rect[2], "height": rect[3], "scale": 1})
    (slides_dir / f"{index + 1:02d}.png").write_bytes(base64.b64decode(shot["data"]))
pdf = cdp("Page.printToPDF", paperWidth=__PAPER_W__, paperHeight=__PAPER_H__, marginTop=0, marginBottom=0, marginLeft=0, marginRight=0, printBackground=True, preferCSSPageSize=False)
Path(__PDF__).write_bytes(base64.b64decode(pdf["data"]))
check.pop("texts", None)
print(json.dumps({"layout_gate_check": check, "pngs": len(rects)}, ensure_ascii=False))
"""


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def find_template(deck: Path, config: dict[str, Any], explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    if config.get("template"):
        return deck.parent / str(config["template"])
    candidate = deck.parent / "template.json"
    return candidate if candidate.is_file() else None


def resolve_settings(config: dict[str, Any], template: dict[str, Any] | None) -> dict[str, Any]:
    layout = config.get("layout") if isinstance(config.get("layout"), dict) else {}
    limits = config.get("limits") if isinstance(config.get("limits"), dict) else {}
    width, height = template["slide_size"]["px"] if template else DEFAULT_SIZE
    page_in = list(template["slide_size"]["in"]) if template else [round(width / 96, 3), round(height / 96, 3)]
    min_font = layout.get("min_font_px") or (template or {}).get("min_font_px") or round(15 * width / 1280, 2)
    zones: dict[str, list[dict[str, float]]] = {}
    title_boxes: dict[str, dict[str, float]] = {}
    for entry in (template or {}).get("slides", []):
        zones[str(entry["index"])] = [{key: item[key] for key in ("x", "y", "w", "h")} for item in entry.get("art", [])]
        if entry.get("title_box"):
            title_boxes[str(entry["index"])] = {key: entry["title_box"][key] for key in ("x", "y", "w", "h")}
    return {
        "width": int(width),
        "height": int(height),
        "page_in": page_in,
        "min_font_px": float(min_font),
        "max_footer_lines": int(layout.get("max_footer_lines") or 3),
        "max_words": int(limits.get("max_words_per_slide") or 80),
        "zones": zones,
        "title_boxes": title_boxes,
    }


def browser_code(deck: Path, settings: dict[str, Any], slides_dir: Path, pdf_path: Path) -> str:
    values = {
        "__WIDTH__": str(settings["width"]),
        "__HEIGHT__": str(settings["height"]),
        "__URL__": repr(deck.resolve().as_uri()),
        "__CHECK__": repr(CHECK_JS.strip()),
        "__SETTINGS__": repr(json.dumps(settings)),
        "__SLIDES__": repr(str(slides_dir)),
        "__PDF__": repr(str(pdf_path)),
        "__PAPER_W__": repr(settings["page_in"][0]),
        "__PAPER_H__": repr(settings["page_in"][1]),
    }
    code = BROWSER_CODE
    for token, value in values.items():
        code = code.replace(token, value)
    return code


def pdf_info(data: bytes) -> dict[str, Any]:
    """Page count and page sizes, also when the page objects sit in compressed object streams."""
    chunks = [data]
    for match in re.finditer(rb"<<(.*?)>>\s*stream\r?\n(.*?)\r?\nendstream", data, re.S):
        if b"/FlateDecode" in match.group(1):
            try:
                chunks.append(zlib.decompress(match.group(2)))
            except zlib.error:
                pass
    text = b"\n".join(chunks)
    counts = [int(value) for value in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", text)]
    counts += [int(value) for value in re.findall(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", text)]
    pages = max(counts) if counts else len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", text))
    boxes = [
        [float(m.group(3)) - float(m.group(1)), float(m.group(4)) - float(m.group(2))]
        for m in re.finditer(rb"/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]", text)
    ]
    return {"pages": pages, "media_boxes": boxes}


def pdf_problems(info: dict[str, Any], *, slides: int, page_in: list[float]) -> list[dict[str, str]]:
    problems = []
    if info["pages"] != slides:
        problems.append({"slide": "PDF", "kind": "pdf-pages", "message": f"PDF has {info['pages']} pages for {slides} slides"})
    expected = [page_in[0] * 72, page_in[1] * 72]
    wrong = [box for box in info["media_boxes"] if abs(box[0] - expected[0]) > 1.5 or abs(box[1] - expected[1]) > 1.5]
    if wrong:
        problems.append(
            {"slide": "PDF", "kind": "pdf-size", "message": f"PDF page size {wrong[0][0]:g}x{wrong[0][1]:g} pt, expected {expected[0]:g}x{expected[1]:g}"}
        )
    return problems


def report_lines(result: dict[str, Any]) -> list[str]:
    lines = [f"{problem['slide']} {problem['message']}" for problem in result["problems"]]
    if not lines:
        lines.append("layout check: no problems found")
    for entry in result["words"]:
        over = entry["main"] and entry["count"] > result["max_words"]
        lines.append(
            f"{entry['slide']} {entry['count']:>3} words"
            f"{'' if entry['main'] else ' (appendix)'}{'  OVER' if over else ''}"
        )
    return lines


def run_gate(
    deck: Path,
    *,
    config: dict[str, Any],
    template_path: Path | None = None,
    slides_dir: Path | None = None,
    pdf_path: Path | None = None,
) -> dict[str, Any]:
    deck = deck.resolve()
    template_file = find_template(deck, config, template_path)
    template = load_json(template_file) if template_file else None
    settings = resolve_settings(config, template)
    slides_dir = (slides_dir or deck.parent / "slides").resolve()
    pdf_path = (pdf_path or deck.with_suffix(".pdf")).resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with IsolatedBrowserHarness() as browser:
        completed = browser.run_code(browser_code(deck, settings, slides_dir, pdf_path), timeout=300)
    payload = None
    for line in reversed([line.strip() for line in completed.stdout.splitlines() if line.strip()]):
        if line.startswith("{") and '"layout_gate_check"' in line:
            payload = json.loads(line)
            break
    if payload is None:
        raise BrowserHarnessError("browser-harness returned no layout result\n" + completed.stdout[-4000:] + completed.stderr[-4000:])
    check = payload["layout_gate_check"]
    info = pdf_info(pdf_path.read_bytes())
    problems = check["problems"] + pdf_problems(info, slides=check["count"], page_in=settings["page_in"])
    return {
        "qa_layout_gate": "fail" if problems else "pass",
        "problems": problems,
        "words": check["words"],
        "max_words": settings["max_words"],
        "slides": check["count"],
        "pngs": payload["pngs"],
        "slides_dir": str(slides_dir),
        "pdf": str(pdf_path),
        "pdf_pages": info["pages"],
        "pdf_bytes": pdf_path.stat().st_size,
        "template": str(template_file) if template_file else None,
        "settings": {key: value for key, value in settings.items() if key not in ("zones", "title_boxes")},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("deck", type=Path)
    parser.add_argument("--config", type=Path, help="judged.json (default: next to the deck)")
    parser.add_argument("--template", type=Path, help="template.json (default: from judged.json or next to the deck)")
    parser.add_argument("--pdf", type=Path, help="PDF to write (default: the deck name with .pdf)")
    parser.add_argument("--slides-dir", type=Path, help="slide PNG folder (default: slides/ next to the deck)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.deck.is_file():
        print(f"ERROR: file not found: {args.deck}", file=sys.stderr)
        return 2
    config = load_json(args.config or args.deck.with_name("judged.json"))
    try:
        result = run_gate(args.deck, config=config, template_path=args.template, slides_dir=args.slides_dir, pdf_path=args.pdf)
    except (BrowserHarnessError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n".join(report_lines(result)))
        print(f"{result['pngs']} slide PNGs → {result['slides_dir']}")
        print(f"{result['pdf']} {result['pdf_pages']} pages, {result['pdf_bytes'] / 1_000_000:.2f} MB")
        print(f"qa-layout-gate: {result['qa_layout_gate']} ({len(result['problems'])} problem(s))")
    return 2 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
