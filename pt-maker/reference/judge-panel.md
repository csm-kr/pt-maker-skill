# 심사 패널 (judge panel)

심사용 덱을 실제 심사처럼 채점하는 절차다. 채점 기준마다 **서로 모르는 심사 agent**
하나씩, 그리고 **사실 확인 agent** 하나를 띄운다. 모두 같은 결과물만 보고, 만든 과정은
보지 않는다(blind, 눈가림). 결과는 `judge_ledger.json`에 적고 `qa_judge_gate.py`로 막는다.
기존 90점 미감 QA(`general-pt-making-checklist.md`, `qa_score_gate.py`)는 따로 그대로 돌린다.

## 언제

- `qa_layout_gate.py`와 `qa_facts_gate.py`가 통과한 뒤, 최종 후보를 사용자에게 보이기 전.
- 덱을 고친 뒤 다시. 라운드마다 **새 agent**를 띄운다. 이전 라운드 점수나 대화를 넘기지
  않는다(앞 점수에 끌려가지 않게).

## 심사 agent에게 주는 것 (이것만)

- `slides/NN.png` 전부 (`qa_layout_gate.py` 출력, 제출 PDF와 같은 렌더)
- 슬라이드 글자: `slides/text.txt` (`qa_layout_gate.py`가 같은 격리 browser-harness 렌더에서
  쪽마다 뽑은 글자. 별도 PDF 도구는 쓰지 않는다)
- 자기 기준 하나: 이름, 가중치, 대회 규칙의 설명 문장 그대로
- 대회 맥락 한 단락: 대회 이름, 제출 형식, 심사 방식 (사용자가 준 규칙에서만)

주지 않는 것: `deck.src.html`, CSS, `NOTES.md`, `CHANGES.md`, 빌드 로그, 작업 대화, 다른
기준의 점수. 심사위원도 이것들을 보지 못한다.

## 사실 확인 agent에게 주는 것

- `slides/text.txt`와 `slides/NN.png`
- `facts.json` (숫자, claim, source, checked)
- 출처 파일을 열 수 있으면 그 파일들 (공개 URL은 직접 열어 확인)

할 일: 슬라이드의 숫자를 모두 찾아 장부 값·출처와 대조하고, 출처 문장이 슬라이드 문장과
같은 것을 말하는지 본다(단위, 모집단, 기간, 조건). 확인한 숫자 수를 `facts_checked`에,
어긋난 것을 `mismatches`에 적는다.

## 심사 agent 지시문 템플릿

```text
You are one judge on a panel for <contest>. Score ONLY this criterion:
"<criterion name>" (weight <W> of 100): <the rules' description, verbatim>.

You see what the real judges see: the slide images and the slide text. Nothing else
exists. Do not guess how it was made.

Return only:
1. score: __/10 for this criterion (10 = best entry you could expect, 5 = average)
2. P0: problems that would make a judge stop trusting the deck or break a rule
   (unsupported or inconsistent numbers, a claim the slides contradict, a required
   template slot missing, unreadable text, a broken or missing link). Page numbers.
3. top_fixes: at most 3 changes that would raise THIS criterion most, with pages.
4. one sentence: what a judge will remember from this deck.

Rules: judge the deck as submitted; do not reward effort you cannot see; do not
suggest adding content that the page limit or word limit cannot hold.
```

## 사실 확인 agent 지시문 템플릿

```text
You check facts for a judged deck. Inputs: the slide text, the slide images,
facts.json, and the sources you can open.
For every number on every slide: find it in facts.json, open its source, and
confirm the slide sentence says what the source says (unit, population, period,
condition). Also flag numbers that appear on slides but not in facts.json.

Return only:
1. facts_checked: count
2. mismatches: list of "page: slide text vs source/ledger"
3. P0: claims that a judge could prove wrong, with pages
```

## 진행

1. `python3 scripts/qa_judge_gate.py --print-template judged.json > judge_ledger.json`
   (기준 id·가중치가 `judged.json`에서, 지금 `deck.html`의 sha256이 `artifacts`에 들어간다.
   빈 장부는 실패 상태다. 심사 뒤 `deck.html`이 바뀌면 장부가 낡은 것으로 실패한다.)
2. subagent 도구로 심사 agent N개와 사실 확인 agent 1개를 **동시에** 띄운다. 이름은
   라운드를 붙여 서로 다르게: `judge-<기준id>-r<라운드>`, `fact-check-r<라운드>`.
3. 각 결과를 장부에 옮긴다: `reviewer`, `blind: true`(위 입력만 줬을 때만), `score`,
   `p0`, `top_fixes`. 사실 확인은 `facts_checked`, `mismatches`, `p0`. 덱에 fact가 하나도
   없으면 `facts_checked`는 0이어도 된다. `artifacts`에 PNG 폴더와 PDF 경로.
   가중 점수(Σ 점수 × 가중치 / 100)는 게이트가 계산한다.
4. `python3 scripts/qa_judge_gate.py judge_ledger.json` (기본 목표는 `judged.json`의
   `target`, 없으면 8.0. `--min`으로 바꿀 수 있다.)
5. 실패하면: P0부터 고치고, 다음으로 가중치가 큰 기준의 top_fixes를 적용한다 → 빌드 →
   레이아웃·숫자 검사 → 새 라운드(새 agent). `CHANGES.md`에 라운드 결과(가중 점수, P0
   수, 적용한 수정)를 남긴다.
6. 통과(가중 점수 ≥ 목표, P0 = 0)하면 미감 QA 점수와 함께 사용자에게 후보로 보고한다.

세 라운드가 지나도 목표에 못 미치면 멈추고 사용자에게 남은 지적과 선택지(내용을 줄일지,
기준 해석을 바꿀지, 목표를 낮출지)를 묻는다. 점수를 맞추려고 근거 없는 주장을 더하지
않는다.

## subagent 도구가 없을 때

`qa_judge_gate.py`는 서로 다른 눈가림 심사자를 요구하므로 혼자서는 통과시킬 수 없다.
`judge-panel: unavailable`을 build-notes에 남기고 사용자에게 알린다. 팀원이나 사용자가
심사자를 맡으면 같은 입력만 주고 결과를 장부에 적는다.
