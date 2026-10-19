#!/usr/bin/env python3
"""pt-maker judged mode: facts ledger gate.

심사용 덱의 숫자·출처·금지 표현을 facts.json(근거 장부)과 대조한다.
build_judged_deck.py가 넣은 fact는 <span class="fact" data-fact="id">로 표시되어 있다.

사용:
  python qa_facts_gate.py deck.html [facts.json] [--config judged.json] [--json]

facts.json, judged.json을 생략하면 deck.html 옆의 파일을 쓴다.

실패 조건 (본편·부록 모든 슬라이드):
  untagged-number       {{fact:id}}로 넣지 않은 숫자. 장부 값과 같아도 표시가 없으면 실패다.
  fact-mismatch         data-fact 안의 숫자가 그 fact 값과 다르다.
  unknown-fact          data-fact가 facts.json에 없는 id를 가리킨다.
  dots-without-fact     점 격자(.dots)가 fact에서 오지 않았다 ({{dots:fact-id}}를 쓴다).
  facts-without-source  fact를 보여 주는 슬라이드에 footer 출처 줄("Details: …")이 없다.
  empty-source          footer의 "Details:" 뒤가 비어 있다.
  banned-phrase         금지 표현(기본: first, only, any, 100%, 최초, 유일)이 주장으로 쓰였다.
  fact-…                장부 항목이 id/value/claim/source/checked를 갖추지 않았다.

숫자로 세지 않는 것 (이유는 test_qa_facts_gate.py에 있다):
  .pg(쪽 번호), .nowc(템플릿 문구), .nofact(근거가 아닌 번호: 단계, 슬라이드 참조), 링크 글자(<a>),
  footer 출처 줄(.ft .src) 안의 날짜(YYYY-MM-DD, YYYY-MM)와 연도, 영문자 바로 뒤(또는 영문자 + -/_ 뒤)의
  숫자(A3, CO2, run-7: 이름이지 수량이 아님), .tart, <script>, <style>, <title>, <desc>.
금지 표현 검사는 .nowc와 .tart를 빼고 footer까지 본다. allowed_phrases 안의 사용은 통과한다.

judged.json "facts"로 바꿀 수 있는 값: source_label (기본 "Details:"), banned_phrases, allowed_phrases
표준 라이브러리만 사용.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

DEFAULT_BANNED = ["first", "only", "any", "100%", "최초", "유일"]
DEFAULT_SOURCE_LABEL = "Details:"
REQUIRED_FIELDS = ("id", "value", "claim", "source", "checked")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_DATE_RE = re.compile(r"^(?:\d{4}-\d{2}(?:-\d{2})?|(?:19|20)\d{2})$")
TOKEN_RE = re.compile(r"(?<![A-Za-z0-9.,])(?<![A-Za-z][-_])(\d{4}-\d{2}(?:-\d{2})?(?![\d-])|\d+(?:[.,]\d+)*)")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "title", "desc", "template", "noscript"}
NUMBER_SKIP_CLASSES = {"pg", "nowc", "nofact", "tart"}
PHRASE_SKIP_CLASSES = {"nowc", "tart"}


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def token_key(token: str) -> Any:
    if "-" in token:
        return token
    try:
        return Decimal(token.replace(",", ""))
    except InvalidOperation:
        return token


class Node:
    def __init__(self, tag: str, attrs: dict[str, str], parent: "Node | None") -> None:
        self.tag = tag
        self.classes = set(attrs.get("class", "").split())
        self.fact = attrs.get("data-fact")
        self.parent = parent
        ancestors = [self] + (parent.chain if parent else [])
        self.chain = ancestors
        self.in_footer = any("ft" in n.classes for n in ancestors)
        self.in_source = self.in_footer and any("src" in n.classes for n in ancestors)


class SlideText(HTMLParser):
    """Collects, per .slide, the text chunks each check needs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict[str, Any]] = []
        self.stack: list[Node] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        node = Node(tag, data, self.stack[-1] if self.stack else None)
        if "slide" in node.classes:
            self.slides.append({"main": "data-main" in data, "index": len(self.slides) + 1, "chunks": [], "facts": [], "dots": []})
        elif self.slides and self.in_slide():
            if "dots" in node.classes:
                self.slides[-1]["dots"].append(node.fact)
            if node.fact:
                self.slides[-1]["facts"].append(node.fact)
        if tag not in VOID_TAGS:
            self.stack.append(node)
        self.chunk(" ")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.chunk(" ")

    def handle_endtag(self, tag: str) -> None:
        for depth in range(len(self.stack) - 1, -1, -1):
            if self.stack[depth].tag == tag:
                del self.stack[depth:]
                break
        self.chunk(" ")

    def in_slide(self) -> bool:
        return any("slide" in node.classes for node in self.stack)

    def chunk(self, text: str, node: Node | None = None) -> None:
        if self.slides and self.in_slide():
            self.slides[-1]["chunks"].append((text, node))

    def handle_data(self, data: str) -> None:
        if self.stack:
            self.chunk(data, self.stack[-1])


def text_of(chunks: list[tuple[str, Node | None]], keep) -> str:
    return re.sub(r"\s+", " ", "".join(text if node is None or keep(node) else " " for text, node in chunks)).strip()


def skipped(node: Node, classes: set[str]) -> bool:
    return any(n.tag in SKIP_TAGS or n.classes & classes for n in node.chain)


def nearest_fact(node: Node) -> str | None:
    return next((n.fact for n in node.chain if n.fact), None)


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    left = r"(?<![A-Za-z0-9])" if phrase[:1].isascii() and phrase[:1].isalnum() else ""
    right = r"(?![A-Za-z0-9])" if phrase[-1:].isascii() and phrase[-1:].isalnum() else ""
    return re.compile(left + re.escape(phrase) + right, re.I)


def context(text: str, start: int, end: int) -> str:
    return text[max(0, start - 30): end + 30].strip()


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def validate_ledger(facts_path: Path, add) -> dict[str, dict[str, Any]]:
    try:
        data = json.loads(facts_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        add("ledger-invalid", f"Could not read {facts_path}: {exc}", "Write facts.json as {\"facts\": [...]}.")
        return {}
    facts = data.get("facts") if isinstance(data, dict) else None
    if not isinstance(facts, list):
        add("ledger-invalid", "facts.json has no \"facts\" list.", "Write facts.json as {\"facts\": [...]}.")
        return {}
    ledger: dict[str, dict[str, Any]] = {}
    for number, fact in enumerate(facts, start=1):
        if not isinstance(fact, dict):
            add("ledger-invalid", f"Fact {number} is not an object.", "Each fact is {id, value, unit, claim, source, checked}.")
            continue
        label = str(fact.get("id") or f"#{number}")
        missing = [key for key in REQUIRED_FIELDS if not str(fact.get(key, "")).strip()]
        if missing:
            add("fact-field-missing", f"Fact {label} lacks {missing}.", "Every number needs a claim, a source someone can open, and the date it was checked.")
        if label in ledger:
            add("fact-id-duplicate", f"Fact id {label} is used twice.", "Give every fact a unique id.")
        checked = str(fact.get("checked", "")).strip()
        if checked and not DATE_RE.match(checked):
            add("fact-checked-date-invalid", f"Fact {label} has checked={checked!r}.", "Use the date the source was last read, as YYYY-MM-DD.")
        if not tokens(str(fact.get("value", ""))):
            add("fact-value-no-number", f"Fact {label} value {fact.get('value')!r} has no number.", "The ledger holds numbers; put words in claim.")
        ledger[label] = fact
    return ledger


def run_checks(deck: Path, facts_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    def add(code: str, message: str, fix: str, slide: str | None = None) -> None:
        entry: dict[str, Any] = {"code": code, "message": message, "fix": fix}
        if slide is not None:
            entry["slide"] = slide
        errors.append(entry)

    settings = config.get("facts", {}) if isinstance(config.get("facts"), dict) else {}
    source_label = str(settings.get("source_label") or DEFAULT_SOURCE_LABEL)
    banned = settings.get("banned_phrases", DEFAULT_BANNED)
    allowed = settings.get("allowed_phrases", [])
    ledger = validate_ledger(facts_path, add)
    values = {fact_id: {token_key(t) for t in tokens(str(fact.get("value", "")))} for fact_id, fact in ledger.items()}

    parser = SlideText()
    parser.feed(deck.read_text(encoding="utf-8", errors="ignore"))
    for slide in parser.slides:
        chunks = slide["chunks"]
        label = text_of(chunks, lambda n: any("pg" in c.classes for c in n.chain)) or f"{slide['index']:02d}"
        loose: list[str] = []
        for text, node in chunks:
            if node is None or skipped(node, NUMBER_SKIP_CLASSES) or any(n.tag == "a" for n in node.chain):
                continue
            fact_id = nearest_fact(node)
            for token in tokens(text):
                if fact_id:
                    if fact_id not in ledger:
                        add("unknown-fact", f"data-fact=\"{fact_id}\" is not in facts.json.", "Insert facts only with {{fact:id}}.", label)
                    elif token_key(token) not in values[fact_id]:
                        add("fact-mismatch", f"{token} is shown as fact {fact_id} = {ledger[fact_id].get('value')!r}.", "Rebuild from facts.json; do not edit a fact on the slide.", label)
                elif not (node.in_source and SOURCE_DATE_RE.match(token)):
                    loose.append(token)
        if loose:
            body = text_of(chunks, lambda n: True)
            add(
                "untagged-number",
                f"Numbers not from facts.json: {loose} in \"{body[:90]}\"",
                "Add each number to facts.json and insert it with {{fact:id}}, or remove it. "
                "A step number or slide reference gets class=\"nofact\"; footer dates are written YYYY-MM-DD.",
                label,
            )
        for dots in slide["dots"]:
            if not dots:
                add("dots-without-fact", "A .dots grid has no data-fact.", "Write {{dots:fact-id}} so the picture comes from facts.json.", label)
        footer = text_of(chunks, lambda n: n.in_source)
        index = footer.lower().find(source_label.lower())
        if index >= 0 and not re.search(r"[\w]", footer[index + len(source_label):]):
            add("empty-source", f"\"{source_label}\" has nothing after it.", "Name the file, page or URL the numbers come from.", label)
        if (slide["facts"] or slide["dots"]) and index < 0:
            add(
                "facts-without-source",
                f"Shows facts {sorted(set(f for f in slide['facts'] if f))} but has no footer line with \"{source_label}\".",
                f"Add <footer class=\"ft\"><div class=\"src\">… {source_label} &lt;source&gt;</div></footer>.",
                label,
            )
        phrase_text = text_of(chunks, lambda n: not skipped(n, PHRASE_SKIP_CLASSES))
        allowed_spans = [(m.start(), m.end()) for phrase in allowed for m in phrase_pattern(str(phrase)).finditer(phrase_text)]
        for phrase in banned:
            for match in phrase_pattern(str(phrase)).finditer(phrase_text):
                if any(start <= match.start() and match.end() <= end for start, end in allowed_spans):
                    continue
                add(
                    "banned-phrase",
                    f"\"{phrase}\" in \"{context(phrase_text, match.start(), match.end())}\"",
                    "Say what was measured instead, or add the exact non-claim use to facts.allowed_phrases in judged.json.",
                    label,
                )
    return {
        "qa_facts_gate": "fail" if errors else "pass",
        "error_count": len(errors),
        "slides_checked": len(parser.slides),
        "facts": len(ledger),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("deck", type=Path)
    parser.add_argument("facts", type=Path, nargs="?")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.deck.is_file():
        print(f"ERROR: file not found: {args.deck}", file=sys.stderr)
        return 2
    facts = args.facts or args.deck.with_name("facts.json")
    if facts.is_file():
        result = run_checks(args.deck, facts, load_config(args.config or args.deck.with_name("judged.json")))
    else:
        result = {"qa_facts_gate": "fail", "error_count": 1, "errors": [{"code": "ledger-missing", "message": f"{facts} not found.", "fix": "Create facts.json next to the deck."}]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"qa-facts-gate: {result['qa_facts_gate']} ({result['error_count']} blocking issue(s))")
        for error in result["errors"]:
            where = f"slide {error['slide']} " if "slide" in error else ""
            print(f"- P0 [{error['code']}] {where}{error['message']}")
            print(f"  fix: {error['fix']}")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
