#!/usr/bin/env python3
"""pt-maker judged mode: judge panel ledger gate.

심사 패널(채점 기준마다 독립 심사 agent 하나 + 사실 확인 agent 하나)의 결과 장부를 검사한다.
진행 방법은 reference/judge-panel.md.

사용:
  python qa_judge_gate.py judge_ledger.json [--min 8.0] [--config judged.json] [--json]
  python qa_judge_gate.py --print-template judged.json      # 빈 장부(채점 전, 실패 상태)

통과 조건:
  - 기준 가중치 합 = 100, 각 기준 점수 0-10
  - 기준마다 서로 다른 심사자(reviewer), blind=true (슬라이드 PNG와 PDF 글자만 봄)
  - 사실 확인(fact_check) 있음: 다른 심사자, blind=true, 불일치 0, 덱에 fact가 있으면 확인한 숫자 ≥ 1
  - 남은 P0 = 0 (기준별 p0 + fact_check p0 + 불일치)
  - 가중 점수 = Σ(점수 × 가중치) / 100 ≥ --min (없으면 judged.json target, 그것도 없으면 8.0)
  - artifacts(slides_dir의 PNG, pdf, deck)가 실제로 있고, deck.html과 그 파일이 쓰는 로컬 파일(CSS, 이미지,
    CSS 안의 글꼴 등)이 심사 뒤 바뀌지 않음(deck_hash)
  - judged.json을 쓰면 기준 id와 가중치가 judged.json criteria와 같음 (심사자가 가중치를 못 바꿈)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

DEFAULT_MIN = 8.0


def number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


REF_RE = re.compile(r"""(?:\bhref|\bsrc)\s*=\s*["']([^"']+)["']|url\(\s*["']?([^"')]+)["']?\s*\)|@import\s+["']([^"']+)["']""", re.I)


def local_refs(path: Path, text: str) -> list[Path]:
    """Local files an HTML or CSS file points at (links, images, scripts, url(), @import)."""
    refs = []
    for match in REF_RE.finditer(text):
        ref = next(group for group in match.groups() if group).strip()
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", ref, re.I):
            continue
        ref = unquote(ref.split("#")[0].split("?")[0])
        if ref:
            refs.append((path.parent / ref).resolve())
    return sorted(set(refs))


def deck_hash(deck: Path) -> str:
    """sha256 over deck.html and every local file it uses, followed through CSS (fonts, images)."""
    digest = hashlib.sha256()
    root = deck.resolve().parent
    queue, seen = [deck.resolve()], set()
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        name = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        if not path.is_file():
            digest.update(f"missing:{name}\n".encode())
            continue
        data = path.read_bytes()
        digest.update(f"{name}\n".encode() + data)
        if path.suffix.lower() in (".html", ".htm", ".css"):
            queue.extend(local_refs(path, data.decode("utf-8", errors="ignore")))
    return digest.hexdigest()


def template_for(config: dict[str, Any], deck: Path) -> dict[str, Any]:
    return {
        "round": 1,
        "artifacts": {"slides_dir": "slides", "pdf": "", "deck": deck.name, "deck_hash": deck_hash(deck) if deck.is_file() else ""},
        "criteria": [
            {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "weight": item.get("weight", 0),
                "reviewer": "",
                "blind": False,
                "score": 0,
                "p0": [],
                "top_fixes": [],
            }
            for item in config.get("criteria", [])
        ],
        "fact_check": {"reviewer": "", "blind": False, "facts_checked": 0, "mismatches": [], "p0": []},
        "notes": "Fill only from independent reviewers who saw the slide PNGs and the PDF text, nothing else.",
    }


def validate(path: Path, *, min_score: float | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str, fix: str) -> None:
        errors.append({"code": code, "message": message, "fix": fix})

    config = config or {}
    minimum = min_score if min_score is not None else number(config.get("target")) or DEFAULT_MIN
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("the ledger must be a JSON object")
    except (OSError, ValueError) as exc:
        add("ledger-invalid-json", f"Could not read {path}: {exc}", "Start from --print-template judged.json.")
        return {"qa_judge_gate": "fail", "error_count": 1, "errors": errors, "weighted_score": None, "min": minimum, "p0_count": None}

    criteria = data.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        add("criteria-missing", "No scoring criteria in the ledger.", "List every scoring criterion with its weight from the contest rules.")
        criteria = []

    reviewers: list[str] = []
    total_weight = 0.0
    weighted = 0.0
    p0_count = 0
    for index, item in enumerate(criteria, start=1):
        if not isinstance(item, dict):
            add("criteria-missing", f"Criterion {index} is not an object.", "Use the template's criterion shape.")
            continue
        label = item.get("id") or f"#{index}"
        weight = number(item.get("weight"))
        score = number(item.get("score"))
        if weight is None or weight <= 0:
            add("criterion-weight-invalid", f"Criterion {label} weight is {item.get('weight')!r}.", "Copy the weight from the scoring rules.")
            weight = 0.0
        if score is None or not 0 <= score <= 10:
            add("criterion-score-invalid", f"Criterion {label} score is {item.get('score')!r}.", "Score each criterion from 0 to 10.")
            score = 0.0
        total_weight += weight
        weighted += score * weight / 100
        reviewer = str(item.get("reviewer") or "").strip()
        if not reviewer:
            add("criterion-reviewer-missing", f"Criterion {label} has no reviewer.", "Name the independent reviewer agent that scored it.")
        else:
            reviewers.append(reviewer)
        if item.get("blind") is not True:
            add("criterion-not-blind", f"Criterion {label} reviewer is not marked blind.", "Give each reviewer only the slide PNGs and the PDF text, then set blind=true.")
        p0 = item.get("p0")
        if not isinstance(p0, list):
            add("criterion-p0-missing", f"Criterion {label} has no p0 list.", "Record the reviewer's P0 list, even when empty.")
        elif p0:
            p0_count += len(p0)
            add("p0-open", f"Criterion {label} has {len(p0)} open P0: {p0}", "Fix the deck, rebuild, re-render, and run a fresh panel round.")
        if not isinstance(item.get("top_fixes"), list):
            add("criterion-fixes-missing", f"Criterion {label} has no top_fixes list.", "Record the reviewer's top fixes.")

    if criteria and abs(total_weight - 100) > 0.001:
        add("weights-not-100", f"Weights sum to {total_weight:g}, not 100.", "Use the contest's weights; they must add up to 100.")

    artifacts = data.get("artifacts") if isinstance(data.get("artifacts"), dict) else {}
    deck = path.parent / str(artifacts.get("deck") or "deck.html")
    deck_has_facts = deck.is_file() and "data-fact=" in deck.read_text(encoding="utf-8", errors="ignore")
    fact = data.get("fact_check")
    if not isinstance(fact, dict):
        add("fact-check-missing", "No fact_check entry.", "Run one blind fact-check reviewer against facts.json and the PDF text.")
    else:
        reviewer = str(fact.get("reviewer") or "").strip()
        if not reviewer:
            add("fact-check-reviewer-missing", "fact_check has no reviewer.", "Name the fact-check agent.")
        else:
            reviewers.append(reviewer)
        if fact.get("blind") is not True:
            add("fact-check-not-blind", "fact_check reviewer is not marked blind.", "Give it only the PDF text and facts.json, then set blind=true.")
        checked = number(fact.get("facts_checked"))
        if checked is None or (deck_has_facts and checked < 1):
            add("fact-check-empty", "fact_check checked no facts, but the deck shows facts.", "Check every number on the slides against facts.json and its sources.")
        mismatches = fact.get("mismatches")
        if not isinstance(mismatches, list):
            add("fact-check-mismatches", "fact_check has no mismatches list.", "Record mismatches as a list, even when empty.")
        elif mismatches:
            p0_count += len(mismatches)
            add("fact-check-mismatches", f"{len(mismatches)} fact mismatch(es): {mismatches}", "Fix the slide or the ledger, rebuild, and re-check.")
        fact_p0 = fact.get("p0") if isinstance(fact.get("p0"), list) else []
        if fact_p0:
            p0_count += len(fact_p0)
            add("p0-open", f"fact_check has {len(fact_p0)} open P0: {fact_p0}", "Fix and run a fresh fact check.")

    duplicates = sorted({name for name in reviewers if reviewers.count(name) > 1})
    if duplicates:
        add("reviewer-not-distinct", f"Reviewers used more than once: {duplicates}", "Use a fresh, separate agent for every criterion and for the fact check.")

    weighted = round(weighted, 4)
    if criteria and weighted < minimum:
        add("weighted-below-min", f"Weighted score {weighted:g} is below {minimum:g}.", "Apply the top fixes and run another blind round.")

    if not deck.is_file():
        add("artifact-missing", f"Deck not found: {deck}", "Point artifacts.deck at the deck.html the reviewers judged.")
    elif artifacts.get("deck_hash") != deck_hash(deck):
        add("ledger-stale", f"{deck.name} or a file it uses changed after this panel round.", "Re-render and run a fresh blind round on the current deck.")
    slides_dir = path.parent / str(artifacts.get("slides_dir") or "")
    if not artifacts.get("slides_dir") or not slides_dir.is_dir() or not any(slides_dir.glob("*.png")):
        add("artifact-missing", f"Slide PNGs not found: {slides_dir}", "Point artifacts.slides_dir at the PNGs the reviewers saw.")
    pdf = path.parent / str(artifacts.get("pdf") or "")
    if not artifacts.get("pdf") or not pdf.is_file():
        add("artifact-missing", f"PDF not found: {pdf}", "Point artifacts.pdf at the PDF whose text the reviewers read.")

    expected = config.get("criteria")
    if isinstance(expected, list) and expected:
        want = sorted((str(c.get("id")), number(c.get("weight"))) for c in expected if isinstance(c, dict))
        got = sorted((str(c.get("id")), number(c.get("weight"))) for c in criteria if isinstance(c, dict))
        if want != got:
            add("criteria-not-from-config", f"Ledger criteria {got} differ from judged.json {want}.", "Score exactly the criteria and weights in judged.json.")

    return {
        "qa_judge_gate": "fail" if errors else "pass",
        "error_count": len(errors),
        "weighted_score": weighted,
        "min": minimum,
        "p0_count": p0_count,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("ledger", type=Path, nargs="?")
    parser.add_argument("--min", type=float, default=None)
    parser.add_argument("--config", type=Path, help="judged.json (default: next to the ledger)")
    parser.add_argument("--print-template", type=Path, metavar="JUDGED_JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.print_template:
        deck = args.print_template.with_name("deck.html")
        print(json.dumps(template_for(load_json(args.print_template), deck), ensure_ascii=False, indent=2))
        return 0
    if args.ledger is None or not args.ledger.is_file():
        print(f"ERROR: judge ledger not found: {args.ledger}", file=sys.stderr)
        return 2
    config = load_json(args.config or args.ledger.with_name("judged.json"))
    result = validate(args.ledger, min_score=args.min, config=config)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        score = result["weighted_score"]
        print(
            f"qa-judge-gate: {result['qa_judge_gate']} (weighted {score if score is not None else '-'} / min {result['min']:g}, "
            f"P0 {result['p0_count']}, {result['error_count']} blocking issue(s))"
        )
        for error in result["errors"]:
            print(f"- P0 [{error['code']}]: {error['message']}")
            print(f"  fix: {error['fix']}")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
