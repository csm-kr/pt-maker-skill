#!/usr/bin/env python3
"""pt-maker judged mode: deck.src.html → deck.html.

심사용 덱의 소스(deck.src.html)를 제출용 deck.html로 만든다.

사용:
  python build_judged_deck.py deck.src.html [-o deck.html]
  GITHUB_URL=https://… VIDEO_URL=https://… python build_judged_deck.py deck.src.html

치환 규칙 (경로는 소스 폴더 기준, 자리표시는 글자 자리에만 쓴다. 속성 안이면 실패):
  <!-- … -->          HTML 주석은 소스에만 남기고 지운다 (<script>·<style> 안은 그대로).
  {{fact:id}}         facts.json의 값 + 단위를 <span class="fact" data-fact="id">로(<svg> 안에서는 <tspan>).
                      {{fact:id:value}}는 값만.
  {{dots:id}}         단위가 %, in 100, of 100, per 100인 fact 값만큼 채운 100칸 점 격자 (.dots, data-fact="id").
  {{link:NAME}}       환경변수 NAME의 URL. 없으면 경고 스타일 자리표시(.v.ph)와 stderr 경고.
  {{icon:name}}       assets/icons/name.svg를 인라인 SVG(.ic)로.
  {{qr:url}}          QR SVG(.qr). 선택 패키지 segno가 필요하며, 쓸 때만 검사한다.

숫자 표시: 장부 값은 그대로 두고, 화면에는 천 단위 쉼표를 넣는다(5자리 이상, 4자리는 1900-2099를 연도로 보고 제외).
  쉼표가 이미 있거나 숫자만으로 된 값이 아니면 적힌 그대로 보인다.

텍스트 규칙 (태그 안·<script>·<style>은 건드리지 않음):
  - 숫자와 단위, "≤ N"은 NBSP로 붙여 줄이 갈라지지 않게 한다 (facts.json 단위 포함).
  - 날짜(2026-10-15, 10-15)는 하이픈에서 끊기지 않게 .nw로 감싼다 (<code>/<text>/<title> 안은 제외).
  - <code> 안 24자 이상의 경로는 슬래시 뒤에서만 줄바꿈되게 나눈다.
  - template.json이 있으면 data-tpl="N" 슬라이드에 템플릿 아트 layer를 넣고 template-layer.css를 인라인한다.

남은 {{…}} 자리표시, 없는 fact/icon, fact가 아닌 dots는 빌드 실패(종료 코드 2)다.
표준 라이브러리만 사용 (QR만 선택 패키지 segno).
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping

NBSP = " "
GLUED_UNITS = ("%", "‰", "×", "°")
PER_100_UNITS = {"%", "in 100", "of 100", "per 100"}
DEFAULT_UNITS = [
    "%", "‰", "×", "x", "ms", "s", "min", "h", "px", "pt", "KB", "MB", "GB", "TB",
    "k", "K", "M", "B", "bn", "km", "m", "kg", "g", "°C",
    "thousand", "million", "billion", "trillion",
    "개", "명", "건", "원", "곳", "배", "초", "분", "시간", "일", "개월", "년", "회", "장", "점", "번", "쪽",
]
NOT_WORD_AFTER = r"(?![A-Za-z0-9_])"
ID = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
TOKEN_RE = re.compile(r"(<!--[\s\S]*?-->|<(?:script|style)\b[\s\S]*?</(?:script|style)\s*>|<[^>]+>)", re.I)
PROTECTED_RE = re.compile(r"(<(script|style)\b[\s\S]*?</\2\s*>)", re.I)
COMMENT_RE = re.compile(r"(<(script|style)\b[\s\S]*?</\2\s*>)|<!--[\s\S]*?-->", re.I)
IN_TAG_RE = re.compile(r"<[^<>]*\{\{(?:fact|dots|link|icon|qr):")
FACT_RE = re.compile(rf"\{{\{{fact:({ID}?)(:value)?\}}\}}")
DOTS_RE = re.compile(r"\{\{dots:([^}]*)\}\}")
LINK_RE = re.compile(r"\{\{link:([A-Z][A-Z0-9_]*)\}\}")
ICON_RE = re.compile(r"\{\{icon:([a-z0-9][a-z0-9-]*)\}\}")
QR_RE = re.compile(r"\{\{qr:([^}]+)\}\}")
LEFTOVER_RE = re.compile(r"\{\{[^{}]*\}\}")
DATE_RE = re.compile(r"(?<![A-Za-z0-9_])(\d{4}-\d{2}-\d{2}|\d{2}-\d{2})(?![A-Za-z0-9_])")
CODE_PATH_RE = re.compile(r"<code([^>]*)>([^<]*/[^<]*)</code>")
TPL_TAG_RE = re.compile(r'<[A-Za-z][^>]*\bdata-tpl="(\d+)"[^>]*>')


class BuildError(RuntimeError):
    """Raised when the deck source cannot be built cleanly."""


@dataclass
class BuildResult:
    html: str
    warnings: list[str] = field(default_factory=list)


def map_text(html: str, fn: Callable[[str], str], skip: tuple[str, ...] = ()) -> str:
    """Apply fn to text between tags; never to tags, comments, <script>/<style>, or text inside skip tags."""
    out = []
    depth = 0
    for index, piece in enumerate(TOKEN_RE.split(html)):
        if index % 2:
            out.append(piece)
            match = re.match(r"<(/?)([A-Za-z][\w-]*)", piece)
            if match and match.group(2).lower() in skip and not piece.endswith("/>"):
                depth = max(0, depth - 1) if match.group(1) else depth + 1
            continue
        out.append(fn(piece) if piece and not depth else piece)
    return "".join(out)


def map_text_with_svg(html: str, fn: Callable[[str, bool], str]) -> str:
    """Like map_text, but tells fn whether the text sits inside an <svg>."""
    out = []
    depth = 0
    for index, piece in enumerate(TOKEN_RE.split(html)):
        if index % 2:
            out.append(piece)
            match = re.match(r"<(/?)svg\b", piece, re.I)
            if match and not piece.endswith("/>"):
                depth = max(0, depth - 1) if match.group(1) else depth + 1
            continue
        out.append(fn(piece, depth > 0) if piece else piece)
    return "".join(out)


def outside_protected(html: str, fn: Callable[[str], str]) -> str:
    parts = PROTECTED_RE.split(html)  # [text, block, tag name, text, ...]
    return "".join(fn(part) if index % 3 == 0 else (part if index % 3 == 1 else "") for index, part in enumerate(parts))


def load_facts(folder: Path) -> dict[str, dict]:
    path = folder / "facts.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {str(fact.get("id")): fact for fact in data.get("facts", []) if isinstance(fact, dict)}


PLAIN_NUMBER_RE = re.compile(r"^([^\d\s,.-]*)(-?)(\d+)(\.\d+)?$")


def format_value(raw: str) -> str:
    """Thousands separators for display: 5+ digit integer parts always, 4 digits unless 1900-2099 (a year).
    Values that already have a comma, or are not a plain number, are shown as written."""
    match = PLAIN_NUMBER_RE.match(raw)
    if not match or "," in raw:
        return raw
    prefix, sign, whole, fraction = match.groups()
    if len(whole) < 4 or (len(whole) == 4 and 1900 <= int(whole) <= 2099):
        return raw
    return f"{prefix}{sign}{int(whole):,}{fraction or ''}"


def fact_html(fact_id: str, fact: dict, value_only: bool, tag: str = "span") -> str:
    value = html_lib.escape(format_value(str(fact.get("value", ""))), quote=False)
    unit = html_lib.escape(str(fact.get("unit") or ""), quote=False)
    if not value_only and unit:
        value = value + unit if unit.startswith(GLUED_UNITS) else f"{value} {unit}"
    return f'<{tag} class="fact" data-fact="{fact_id}">{value}</{tag}>'


def dots_html(spec: str, facts: dict[str, dict]) -> str:
    fact = facts.get(spec)
    if fact is None:
        raise BuildError(f"{{{{dots:{spec}}}}}: dots take a facts.json id ({{{{dots:fact-id}}}}) so the picture has a source")
    try:
        value = float(str(fact.get("value", "")).replace(",", ""))
    except ValueError:
        value = -1
    unit = str(fact.get("unit") or "").strip()
    if not 0 <= value <= 100 or unit not in PER_100_UNITS:
        raise BuildError(
            f"{{{{dots:{spec}}}}}: {fact.get('value')!r} {unit!r} is not a share out of 100 "
            f"(unit must be one of {sorted(PER_100_UNITS)})"
        )
    count = round(value)
    cells = "".join('<i class="on"></i>' if i < count else "<i></i>" for i in range(100))
    return f'<div class="dots" data-fact="{spec}" role="img" aria-label="{count} of 100">{cells}</div>'


def icon_svg(folder: Path, name: str) -> str:
    path = folder / "assets" / "icons" / f"{name}.svg"
    if not path.is_file():
        raise BuildError(f"icon not found: {path}")
    svg = re.sub(r"<\?xml[^>]*\?>|<!--[\s\S]*?-->|<!DOCTYPE[^>]*>", "", path.read_text(encoding="utf-8")).strip()
    match = re.search(r"<svg\b([^>]*)>", svg)
    if not match:
        raise BuildError(f"not an SVG file: {path}")
    attrs = match.group(1)
    prefix = ""
    if re.search(r'\sclass="', attrs):
        attrs = re.sub(r'\sclass="([^"]*)"', r' class="ic \1"', attrs, count=1)
    else:
        prefix = ' class="ic"'
    if "aria-hidden" not in attrs:
        prefix += ' aria-hidden="true"'
    return svg[: match.start()] + f"<svg{prefix}{attrs}>" + svg[match.end():]


def qr_svg(url: str) -> str:
    try:
        import segno  # optional
    except ImportError:
        segno = None
    if segno is None:
        raise BuildError(
            "{{qr:…}} needs the optional 'segno' package. Install it with "
            "`python3 -m pip install segno`, or remove the QR placeholder."
        )
    svg = segno.make(url, error="m", micro=False).svg_inline(scale=1, border=0, omitsize=True)
    return svg.replace("<svg ", '<svg class="qr" ', 1)


def unit_pattern(facts: dict[str, dict]) -> re.Pattern[str]:
    units = set(DEFAULT_UNITS)
    units.update(str(fact.get("unit") or "").split()[0] for fact in facts.values() if str(fact.get("unit") or "").strip())
    alternatives = "|".join(re.escape(unit) for unit in sorted(units, key=len, reverse=True))
    return re.compile(rf"(\d) ({alternatives}){NOT_WORD_AFTER}")


def keep_together(text: str, units: re.Pattern[str]) -> str:
    text = units.sub(lambda m: f"{m.group(1)}{NBSP}{m.group(2)}", text)
    return re.sub(r"([≤≥~]) (\S)", lambda m: f"{m.group(1)}{NBSP}{m.group(2)}", text)


def split_code_paths(text: str) -> str:
    def fix(match: re.Match[str]) -> str:
        attrs, value = match.group(1), match.group(2)
        if len(value) < 24:
            return match.group(0)
        joined = "<wbr>".join(f'<span class="seg">{segment}</span>' for segment in re.split(r"(?<=/)", value) if segment)
        return f"<code{attrs}>{joined}</code>"

    return CODE_PATH_RE.sub(fix, text)


def inject_template(html: str, folder: Path) -> str:
    used = TPL_TAG_RE.findall(html)
    if not used:
        return html
    template_path = folder / "template.json"
    if not template_path.is_file():
        raise BuildError(f"slides use data-tpl but {template_path} is missing; run import_template.py first")
    template = json.loads(template_path.read_text(encoding="utf-8"))
    layers = {int(entry["index"]): entry.get("layer_html", "") for entry in template.get("slides", [])}
    missing = sorted({int(n) for n in used if int(n) not in layers})
    if missing:
        raise BuildError(f"data-tpl refers to template slides that do not exist: {missing}")
    html = TPL_TAG_RE.sub(lambda m: m.group(0) + layers[int(m.group(1))], html)
    css_path = folder / "template-layer.css"
    if css_path.is_file():
        style = f"<style data-template-layer>\n{css_path.read_text(encoding='utf-8')}</style>"
        if re.search(r"</head>", html, re.I):
            html = re.sub(r"</head>", lambda m: style + m.group(0), html, count=1, flags=re.I)
        else:
            html = style + html
    return html


def build(src: Path, *, env: Mapping[str, str] | None = None) -> BuildResult:
    src = Path(src)
    folder = src.parent
    env = os.environ if env is None else env
    warnings: list[str] = []
    html = COMMENT_RE.sub(lambda m: m.group(1) or "", src.read_text(encoding="utf-8"))
    if IN_TAG_RE.search(outside_protected(html, lambda part: part)):
        raise BuildError("a {{…}} placeholder sits inside a tag attribute; put facts, dots, links, icons and QR codes in text")

    facts = load_facts(folder)
    unknown = sorted({m.group(1) for m in FACT_RE.finditer(html) if m.group(1) not in facts})
    if unknown:
        raise BuildError(f"facts not in facts.json: {unknown}")
    html = re.sub(r"([≤≥~]) (?=\{\{fact:)", lambda m: m.group(1) + NBSP, html)
    def place(text: str, in_svg: bool) -> str:
        # Inside <svg> an HTML <span> would end the SVG in the browser's parser, so facts become <tspan>.
        if in_svg and (DOTS_RE.search(text) or LINK_RE.search(text)):
            raise BuildError("{{dots:…}} and {{link:…}} make HTML; put them outside <svg>")
        text = FACT_RE.sub(lambda m: fact_html(m.group(1), facts[m.group(1)], bool(m.group(2)), "tspan" if in_svg else "span"), text)
        return DOTS_RE.sub(lambda m: dots_html(m.group(1), facts), text)

    html = map_text_with_svg(html, place)
    for name in sorted(set(ICON_RE.findall(html))):
        html = html.replace(f"{{{{icon:{name}}}}}", icon_svg(folder, name))
    for url in sorted(set(QR_RE.findall(html))):
        html = html.replace(f"{{{{qr:{url}}}}}", qr_svg(url))

    def link(match: re.Match[str]) -> str:
        name = match.group(1)
        url = env.get(name, "")
        if not url:
            warnings.append(f"placeholder: {name} is not set")
            return f'<span class="v ph">{name}</span>'
        label = re.sub(r"/$", "", re.sub(r"^https?://", "", url))
        return f'<a class="v u" href="{html_lib.escape(url)}">{html_lib.escape(label, quote=False)}</a>'

    html = LINK_RE.sub(link, html)
    units = unit_pattern(facts)
    html = map_text(html, lambda text: keep_together(text, units))
    html = map_text(html, lambda text: DATE_RE.sub(r'<span class="nw">\1</span>', text), skip=("code", "text", "title"))
    html = outside_protected(html, split_code_paths)

    leftovers = LEFTOVER_RE.findall(outside_protected(html, lambda part: part))
    if leftovers:
        raise BuildError(f"unknown placeholders left in the deck: {sorted(set(leftovers))}")
    return BuildResult(html=inject_template(html, folder), warnings=warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("src", type=Path)
    parser.add_argument("-o", "--out", type=Path, help="output HTML (default: deck.html next to the source)")
    args = parser.parse_args()
    src = args.src.resolve()
    if not src.is_file():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        return 2
    out = (args.out or src.with_name("deck.html")).resolve()
    if out == src:
        print("ERROR: the output would overwrite the source; name the source deck.src.html", file=sys.stderr)
        return 2
    try:
        result = build(src)
    except (BuildError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for warning in result.warnings:
        print(warning, file=sys.stderr)
    out.write_text(result.html, encoding="utf-8")
    print(f"{out} {round(out.stat().st_size / 1024)} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
