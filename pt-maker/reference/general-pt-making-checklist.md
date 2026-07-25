# General PT 제작/채점 체크리스트

이 체크리스트는 pt-maker의 최종 QA 게이트다. 모든 덱은 최종 산출 전 이 문서와 [html-quality-rubric.md](html-quality-rubric.md)로 채점하고, 실패 항목을 수정한 뒤 다시 렌더링해야 한다.

## 사용 규칙

1. `qa_html_guard.py`와 `qa_media_guard.py`를 통과한 뒤 HTML/PDF를 렌더링한다.
2. contact sheet를 생성한다.
3. 표지, 섹션 시작, 도표/SVG/타임라인, 활동/퀴즈, 마지막 페이지는 full-size PNG로 확인한다.
4. agent/subagent 도구가 있으면 dedicated QA reviewer agent를 실행한다.
5. [html-quality-rubric.md](html-quality-rubric.md)의 고정 7영역 배점으로 P0/P2와 100점 점수를 기록한다.
6. P0가 하나라도 있거나 점수가 90점 미만이면 source HTML/CSS를 수정하고 다시 렌더링한다.
7. 수정 후 contact sheet와 필요한 full-size PNG를 다시 만들고 QA를 반복한다.
8. 렌더 QA가 끝나면 `qa_ledger.json`의 `rubric`에 영역별 점수·근거를 작성하고 `qa_score_gate.py <html> <qa_ledger.json>`를 실행한다. 영역 합계는 최상위 `score`와 같아야 한다.
9. `qa_score_gate.py`가 pass하기 전에는 `pt-qa-result: pass`, 90점 이상 점수, 최종 후보 보고를 금지한다.
10. QA가 통과하면 먼저 QA 결과와 HTML/PDF 후보를 사용자에게 보고하고, 그 다음 수정 요청 단계로 들어간다.
11. 사용자가 수정 요청을 주면 새 버전으로 처리하고, 수정 → 재렌더 → QA 반복 → 재보고한다.
12. 사용자 최종 리뷰가 끝나면 `user_review_ledger.json`을 작성하고 `qa_final_review_gate.py <html> <qa_ledger.json> <user_review_ledger.json>`를 실행한다.
13. `qa_final_review_gate.py`가 pass하기 전에는 최종 납품, final 보고, 사용자 리뷰 기반 taste-profile 업데이트 완료 보고를 금지한다.
14. 최종 사용자 리뷰에서 재사용 가능한 취향 학습이 나오면 diff로 제안하고, 사용자가 확인한 경우에만 `taste-profile.md` 또는 `dark-taste-profile.md`를 업데이트한다. 업데이트/미업데이트 결정은 `user_review_ledger.json`에 남긴다.
15. PPTX는 기본 산출물이 아니다. 사용자가 명시 요청했거나 합의된 산출물에 PPTX가 포함된 경우에만, PDF/contact sheet 통과 후 export한다.

## Agent 검수 시스템

agent/subagent 도구가 있는 환경에서는 최종 산출 전 반드시 독립 QA reviewer agent를 사용한다. 이 agent는 파일을 수정하지 않고, 렌더된 결과물만 보고 판단한다.

### Agent에게 전달할 입력

- 덱의 목적/청중/발표 상황 요약.
- 최종 또는 후보 PDF.
- contact sheet 이미지.
- `qa_html_guard.py <html> --json`과 `qa_media_guard.py <html> --json` output.
- `qa_score_gate.py <html> <qa_ledger.json> --json` output once the reviewer has supplied the ledger.
- full-size PNG: 표지, 섹션 시작, 도표/SVG/타임라인, 활동/퀴즈, 마지막 페이지.
- 이 체크리스트.

### Agent 지시문 템플릿

```text
You are a PT QA reviewer. Review only rendered artifacts, not source code.
Use reference/general-pt-making-checklist.md as the grading standard.
Use the provided qa_media_guard.py JSON output as a blocking source-level gate.

Return only:
1. pt-qa-result: pass/fail
2. score: __/100
3. P0 hard fails, with page numbers and concrete visual reason
4. P2 polish candidates, with page numbers
5. required fixes
6. recheck pages

Rules:
- Every P0 from qa_media_guard.py is a P0 hard fail unless the source was fixed and
  the affected rendered page was rechecked. Crop overrides require both
  `data-crop-ok="true"` and `data-rendered-qa="true"` or `data-fullsize-qa="true"`.
- A passing score is not valid until `qa_score_gate.py` passes against the final
  HTML and QA ledger. If the score gate fails, report `pt-qa-result: fail`.
- Any text overlap, broken Korean word/label, footer collision, cropped content,
  broken 16:9, disconnected diagram arrow, or score below 90 is fail.
- Any text overflow, clipped text, text outside its box, awkward Korean line
  break, table/card/checklist wrapping that looks broken, or final PDF page-order
  mismatch is a P0 hard fail.
- Any visible leftover text from a prior version, placeholder, deleted component,
  old prompt, duplicated label, or stale source note is a P0 stale-content fail.
- Any bottom content that exits the slide, touches the footer, or overlaps another
  element is a P0. Require layout expansion, copy reduction, or structural redesign;
  do not accept a fix that only shrinks text.
- Prominent headings must be visually intentional. A two-line title with a very
  short second line is at least P2 and becomes P0 if it makes the slide look broken.
  Prefer widening the text region, reducing the image/map region, or shortening the
  phrase so the title becomes one balanced line.
- A rendered Korean heading or prominent sentence whose wrapped line, especially the
  final line, has 5 Korean characters or fewer, excluding spaces and punctuation, is
  a P0 orphan-line failure unless the break is visibly intentional. Fix by changing
  the layout before accepting the slide: widen the text frame, reduce/reposition the
  visual, change the grid, or shorten the phrase.
- Closing and statement slides must keep clear title-to-subtitle spacing. If the
  subtitle sits too close to the headline, report it as P2 or P0 depending on severity.
- Large display headlines must keep enough distance from adjacent paragraphs. If a
  subtitle/body line sits so close that hierarchy collapses, report P2 or P0 and fix
  spacing/layout rather than only shrinking the headline.
- Text over a photo, map, screenshot, illustration, or footer-over-visual area must
  have clear rendered contrast. If the background makes text hard to read, report P0
  and require visual repositioning, dimming, or a solid/translucent complementary
  panel behind the text.
- Any person/photo-led slide where a face, head, identity cue, product, food,
  landmark, logo, or core object is cropped by the frame is a P0 hard fail.
- Any real geography map made as an inaccurate hand-drawn/SVG outline, or any map
  where pins/routes/regions do not align to a sourced map base, is a P0 hard fail.
- For custom SVG/CSS/HTML diagrams, flow charts, timelines, networks, or triads:
  inspect the full-size rendered page. All connector endpoints must land on their
  intended target, labels must be readable and attached by proximity/alignment,
  strokes must be consistent, and no line may dangle, float, cut through text, or
  collide with cards. The diagram container may have `data-fullsize-qa="true"` and
  `data-rendered-qa="true"` only after this check.
- If text does not fit, require copy reduction, slide split, or full layout
  redesign. Do not accept a fix that only shrinks the font into a cramped layout.
- Do not suggest broad redesign unless needed to remove a P0.
- Do not edit files.
```

### 반복 루프

1. Main agent runs `qa_media_guard.py <html> --json`.
2. Main agent renders PDF/contact sheet only if the media guard has no P0.
3. QA reviewer agent receives the media guard JSON, contact sheet, selected full-size PNGs, and returns P0/P2/score.
4. Main agent fixes the source HTML/CSS/assets.
5. Main agent reruns media guard and rerenders PDF/contact sheet.
6. Main agent writes `qa_ledger.json` from the rendered QA evidence and runs `qa_score_gate.py <html> <qa_ledger.json> --json`.
7. Repeat QA until `pt-qa-result: pass`, no P0, score >= 90, and `qa_score_gate: pass`.
8. Record a scored QA ledger in build notes: `qa-score`, `p0-count`, `p2-count`,
   `fixed-pages`, `recheck-pages`, and `regression-check`.
9. Inspect the full new contact sheet for regressions introduced by the fix: new
   wrapping, overflow, footer collision, contrast loss, crop damage, page-order drift,
   or broken visual rhythm. Do not rely only on fixed-page PNGs.
10. If `p0-count > 0`, `qa-score < 90`, `qa_score_gate` is fail, or `regression-check` is fail, fix, rerender,
    and restart at step 1.
11. Report the passed QA result and HTML/PDF candidate to the user, then enter the revision phase.
12. After user review is accepted or requested changes are resolved, write `user_review_ledger.json` and run `qa_final_review_gate.py <html> <qa_ledger.json> <user_review_ledger.json> --json`.
13. Repeat the user-review/update/recheck loop until `qa_final_review_gate: pass`.
14. Export PPTX only when explicitly requested and only after pass.

If no agent/subagent tool exists, record `qa-agent: unavailable` in build notes and run the same checklist manually. Do not skip the scoring loop.

## Text Fit, Wrapping, Export, And Variation Hard Gates

These rules override any softer polish language in this checklist.

- P0: text overflows, is clipped, leaves its intended box, touches a border, or escapes the slide.
- P0: Korean line breaks split a word, number/unit, proper noun, label, section number, or short phrase in a way that looks accidental.
- P0: table, card, matrix, checklist, timeline, source note, or footer wrapping makes the slide look broken, cheap, or misaligned.
- P0: the slide only fits by shrinking text below the delivery profile, tightening line-height, or degrading spacing. Reduce copy, split the slide, or redesign the layout completely.
- P0: visible stale text from a previous version, placeholder, removed module, old prompt, duplicated caption, or obsolete source note remains on the rendered slide.
- P0: lower-third content spills outside the slide, touches/overlaps the footer, or collides with neighboring text/cards.
- P0: body, card, chart, source, or lower-third content touches, overlaps, sits underneath, or visually competes with the footer/source note/page number. Fix the source layout and rerender; do not accept a score or export while the footer collision remains.
- P0: final PDF page order is wrong, pages are duplicated/missing, or the contact sheet was not generated from the exact final PDF.
- P0: a revision fixes the flagged page but introduces a new rendered regression elsewhere in the deck. Full contact-sheet regression review is mandatory after each fix.
- P0: a face, head, identity cue, product, food, landmark, logo, UI screenshot detail, or any named subject is cropped so the slide loses information.
- P0: a real geography map is hand-drawn inaccurately, lacks a cited map base, or uses overlay pins/routes/regions that do not align with the map.
- P0: a prominent Korean heading or sentence wraps with any wrapped line, especially the final line, of 5 Korean characters or fewer, unless it is clearly intentional display typography. Treat it as a layout failure and fix the layout first.
- P0: text, footer, caption, or map label sits on a busy visual background without enough contrast to read comfortably in the rendered PDF.
- P0: `qa_score_gate.py` fails or was not run before reporting `pt-qa-result: pass` or a score >= 90.
- P2/P0 depending on severity: a prominent heading wraps into two lines with a short orphan tail. Fix by changing layout width/image size/copy before accepting the slide.
- P2/P0 depending on severity: closing/statement slide title and subtitle sit too close together and weaken hierarchy.
- P2/P0 depending on severity: a very large headline and its adjacent subtitle/body are too tightly stacked. Add breathing room or redesign the layout before accepting the slide.
- P2/P0 depending on severity: too many consecutive slides reuse the same layout. Use deliberate variation, but only if the varied layout preserves alignment, hierarchy, spacing, and text fit.
- Required fix rule: when content does not fit, change the layout pattern before accepting cramped text. Prefer fewer cards, a larger matrix, a split layout, a diagram, or additional slides.
- User-flagged page rule: when a user names a page number, export full-size PNGs for the PDF page ordinal and for any visible slide label/footer number that matches it. If a cover is labeled `00`, page 15 and slide label `15 / N` may be different rendered pages; inspect both and list both in `recheck-pages`.

## 리뷰 등급

### P0: 즉시 수정해야 하는 hard fail

- 텍스트 겹침, 카드/푸터/출처 충돌, 잘림, 16:9 깨짐, 본문 가독성 실패.
- 카드 행/열 정렬 불일치.
- 타임라인 핀, 도식 라벨, SVG 라벨 위치 어긋남.
- 반복 header/footer/page number 좌표 흔들림.
- 섹션 번호나 핵심 라벨 줄바꿈.
- 한국어 단어, 고유명사, 숫자 라벨이 중간에서 끊김.
- 주요 도표의 선/화살표가 끊기거나 대상에 애매하게 닿음.
- `qa_score_gate.py` 실패 또는 미실행 상태에서 통과/90점 이상으로 보고함.
- 마지막 페이지의 제목, 이미지, 마무리 문구, 푸터가 서로 침범.

### P2: polish 개선 후보

- hard fail은 아니지만 시각 무게가 아래로 쏠림.
- 비슷한 레이아웃이 반복되어 지루함.
- 강조 요소, 배지, 아이콘, 장식이 메시지보다 과함.
- 첫 페이지와 마지막 페이지가 연결감 없이 따로 놂.
- 이미지가 예쁘지만 슬라이드 주장과 직접 연결되지 않음.

## 1. 기획 기준

- 청중, 목적, 발표 시간, 산출물 형식이 명확한가.
- 한 슬라이드에 하나의 핵심 역할만 있는가.
- 전체 흐름이 도입 → 맥락/문제 → 근거 → 정리/행동으로 이어지는가.
- 같은 형태의 슬라이드가 반복되어 지루하지 않은가.

## 2. 시각자료 기준

- 주요 슬라이드가 텍스트만으로 끝나지 않는가.
- 이미지, 도표, 지도, 타임라인, 캡처, AI 이미지의 역할이 명확한가.
- 이미지는 슬라이드 주장과 직접 연결되는가.
- `image` 포맷은 visual plan의 `claim → image` 대응이 모두 채워지고,
  서로 다른 이미지 여러 장이 실제 인접 문장을 설명·증명하는가.
- AI 이미지는 사료/증거가 아니라 보조 일러스트로 표시되는가.

## 2.1 줄글 포맷의 타이포 분포

- 각 슬라이드에 초점 문구, 보조 문구, 읽는 경로가 한눈에 구분되는가.
- 초점 문구가 크기·굵기·색·위치 중 하나 이상으로 본문보다 먼저 보이는가.
- 덱 전체에 최소 3개 타이포 구성 family가 있고, 같은 정렬/블록 분포가
  3장 연속 반복되지 않는가.
- 텍스트 양을 균등하게 채운 문단 벽 대신 여백과 비대칭 분포가 의도적으로
  사용되었는가.

## 3. 줄바꿈/정렬 기준

- 한국어 줄바꿈이 어절 단위로 되어 있는가.
- 단어 중간, 고유명사 중간, 숫자 라벨 중간에서 끊기지 않는가.
- `01`, `02`, `10` 같은 섹션 번호가 두 줄로 갈라지지 않는가.
- 제목 줄바꿈이 의미 단위에 맞는가: 주어/서술어, 원인/결과, 문제/해결, 대비/결론.
- 마지막 줄에 짧은 단어 하나만 외롭게 남지 않는가.
- 제목, 본문, 카드, 이미지의 왼쪽 기준선이 의도에 맞게 정렬되어 있는가.

## 4. 레이아웃 기준

- 텍스트, 이미지, 카드, 푸터가 겹치지 않는가.
- 카드 내부 여백이 충분한가.
- 헤더, 페이지 번호, 푸터 위치가 일관적인가.
- 이미지 영역과 텍스트 영역이 침범하지 않는가.
- 첫 페이지와 마지막 페이지가 완성도 있게 연결되는가.

## 5. 숫자/배지/아이콘 기준

- 동그라미 숫자나 배지가 본문보다 과하게 크지 않은가.
- 배지가 위아래 줄을 침범하지 않는가.
- 숫자와 아이콘이 장식이 아니라 정보 구조를 돕는가.

## 6. 도표/SVG/화살표 기준

- 선과 화살표가 실제 대상에 정확히 연결되는가.
- 화살표가 텍스트나 카드와 겹치지 않는가.
- SVG가 떠 있거나 끊긴 것처럼 보이지 않는가.
- 복잡하면 화살표 대신 번호 단계나 단순 흐름도로 바꿨는가.
- 좌표가 중요한 도식은 가능한 한 실제 SVG 선/노드 좌표로 만든다. CSS pseudo-element나 div 선은 브라우저/PDF 렌더 차이로 어긋나기 쉬우므로 단순한 경우에만 쓴다.
- 연결선은 대상의 중심 또는 경계에 명확히 닿아야 한다. 선 끝이 원/카드 옆에 떠 있거나, 너무 길어 텍스트를 지나가거나, 다른 도형과 애매하게 닿으면 P0이다.
- 라벨은 도형 중앙 또는 명확한 근접 위치에 두고, 도형/선/화살표/카드와 겹치면 안 된다.
- 반복 노드의 크기, stroke, 내부 여백, 라벨 기준선은 일관되어야 한다.
- 모든 custom SVG/CSS/HTML 도식, flow, timeline, network, triad는 full-size PNG로 확인한다.
- full-size로 확인한 뒤에만 도식 컨테이너에 `data-fullsize-qa="true"`와 `data-rendered-qa="true"`를 붙인다. 이 표식이 없으면 `qa_media_guard.py`와 `qa_score_gate.py`에서 P0로 막는다.

## 7. 이미지 기준

- 이미지의 주제가 슬라이드 크기에서도 분명히 보이는가.
- 텍스트가 복잡한 이미지 위에 직접 올라가지 않는가.
- 인물 얼굴, 지도, 질감, 고대비 영역 위에 본문을 얹지 않았는가.
- 생성 이미지에 가짜 글자, 왜곡된 상징, 어색한 디테일이 없는가.

## 8. 최종 QA 기준

- PDF로 렌더링해 실제 보이는 상태를 확인했는가.
- contact sheet로 전체 페이지를 한눈에 점검했는가.
- 표지, 섹션 시작, 도표, 활동/퀴즈, 마지막 페이지를 큰 이미지로 확인했는가.
- `qa_ledger.json`을 작성하고 `qa_score_gate.py`를 통과했는가.
- QA 통과 후 HTML/PDF 후보와 QA 결과를 사용자에게 먼저 보고했는가.
- 사용자 최종 리뷰 후 `user_review_ledger.json`을 작성하고 `qa_final_review_gate.py`를 통과했는가.
- 사용자 리뷰 기반 취향 학습을 diff로 제안하고, 확인된 경우에만 `taste-profile.md`/`dark-taste-profile.md`를 업데이트했는가.
- PPTX가 기본 산출물로 자동 생성되지 않았는가.
- PPTX가 필요하다면 사용자의 명시 요청 또는 합의가 있고, PDF가 통과한 뒤에만 export했는가.
- 12장 이상의 animation 발표 HTML은 선언한 3개 transition family를 모두
  사용하고, 동일 seam의 역방향에서도 같은 family를 반대로 재생하는가.

## 100점 채점표

- 가독성 + 한국어 줄바꿈: 20
- 정렬 + 여백: 20
- 시각자료 적합성: 20
- 도표/SVG/화살표 완성도: 15
- 슬라이드 리듬과 변주: 10
- 표지/마무리 완성도: 10
- HTML/PDF export 검증 증거: 5

## 즉시 fail 조건

- 텍스트와 이미지가 겹침.
- 섹션 번호나 핵심 라벨이 줄바꿈됨.
- 한국어 단어가 중간에서 끊김.
- 주요 도표의 선/화살표가 끊기거나 애매함.
- 마지막 페이지의 제목/이미지/마무리 문구가 서로 침범함.
- 전체 점수 90점 미만.
- `qa_score_gate.py` 미통과.
- `qa_final_review_gate.py` 미통과.
- 사용자 리뷰 기반 profile 업데이트 결정을 기록하지 않음.

## 리뷰 기록 템플릿

```text
pt-qa-result: pass/fail
score: __/100

P0 hard fails:
- page __: ...

P2 polish candidates:
- page __: ...

fixes applied:
- ...

media-guard-result: pass/fail
media-guard-p0-count: __
score-gate-result: pass/fail
score-gate-error-count: __
final-review-gate-result: pass/fail
final-review-gate-error-count: __
rerendered: yes/no
contact-sheet-reviewed: yes/no
full-size-pages-reviewed: cover, section openers, person/photo-led slides, real-map slides, diagrams/SVGs, activities/quizzes, final
diagram-checks: connector_endpoints, labels_clear, no_collisions, layout_alignment
user-review-reported: yes/no
user-review-status: accepted/no_changes/changes_requested_resolved
profile-update-decision: accepted/declined/not_applicable
pptx-export-requested: yes/no
pptx-exported: yes/no/not-requested
```
