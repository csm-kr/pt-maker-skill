# Build notes

- mode: `presentation`
- production-direction: `text` (format 2, 줄글 위주)
- final files (v2): `TeslaRoadster2026v2.html`, `TeslaRoadster2026v2.pdf`, `TeslaRoadster2026v2_contact.png`, `assets/`, `qa/full-size/`, `qa_ledger.json` (v1 files removed after v2 replaced them)
- template: pt-maker `assets/template.html` (Reveal 5.1.0, 1280x720, `center:false`, `pdfPageHeightOffset:0`), taste-profile v12 defaults (cream paper, ink, rose accent, Pretendard, handwritten memo only for non-facts)

## Intake (from the shared BRIEF; the owner was not asked again)

- format: text-led Reveal HTML + PDF, runtime mode `presentation`
- references: `research/SOURCE_MAP.md`, `research/facts.json`, `research/STORY.md`, `research/IMAGES.md` (content + evidence); no style reference
- audience: Korean general audience interested in cars and tech; 10-minute study or team session on a shared screen
- purpose: a clear, honest summary for people who did not watch the 2026-10-15 Roadster Event; separate what was promised, what was shown live and what is still only a promise
- one-line message (STORY.md): 9년 만에 Roadster는 떠올랐다. 하지만 가격, 출시일, 성능 수치는 아직 테슬라의 약속이다. Cover phrasing: "떠오르긴 했다. 살 수는 아직 없다."
- evidence: only `facts.json` and `SOURCE_MAP.md`
- CTA: when you hear a launch number, ask whether it was claimed, shown or verified (주장인가, 시연인가, 검증인가?)
- slides: 12; language Korean, product/spec names in English
- visual level: images only as support (1 credited Commons photo, 1 self-drawn SVG, 3 HTML/CSS diagrams)
- rights: no Tesla logos, press photos, livestream frames or screenshots; cover says 비공식 정리 and "Tesla와 제휴·후원 관계가 없는 독립 요약"; at most one short quote per source

## Number labelling rule

- Every number about the car or the event carries a chip: 주장 (facts.json `claimed`, plus any number that comes from Tesla's own timer or a manufacturer, per ERRATA E2/E11), 시연 (shown live), 검증 (independently measured or a platform record), 계산 (plain date arithmetic, per ERRATA E13; added in v2). Where all numbers on a slide share one status (slides 04, 07, 08) a slide-level label says so ("이 장의 숫자는 모두 테슬라 발표 [주장]").
- facts.json also has a fourth status, `reported` (press reporting). To keep to the three labels, no `reported` number is shown: reported items appear only as wording without a number (no price announced, no independent timing found, no rides reported, the cars ran with nobody on board) and the CNBC/CNN/Reuters/Electrek quotes are translated without numbers. Dropped for that reason: reservation amounts ($50,000 / $250,000), McMurtry 1.35 s and Nevera 1.74 s, Electrek's slip counts, 97 km/h conversion, start time in CDT.
- Calendar years used only as time markers (2017년, 2026년) and page numbers are not tagged.

## Slide plan (claim / evidence / layout family / focal phrase / reading path)

| # | role | claim (title) | facts.json ids | family | focal phrase → support → path | visual |
|---:|---|---|---|---|---|---|
| 01 | cover | 떠오르긴 했다. 살 수는 아직 없다. | days-unveil-to-event (계산, dates shown) | oversized statement (dark field) | 80px two-line focal → 3,255일 metric right → tag legend line | none |
| 02 | overview | 약속은 2020년, 시연은 2026년, 다음 약속은 2028년 | production-promise-2017, event-date, production-2028 | stepped phrase | three stepped 40px lines joined by dashed arrows → legend top right → memo | CSS flow |
| 03 | 2017 promise | 2017년 테슬라는 숫자 네 개를 내걸고 2020년 출시를 약속했다 | zero60-claim-2017, range-claim-2017, conv-range-2017-km, seats-claim-2017, price-base-2017, production-promise-2017 | metric-led copy | 2x2 big numbers → photo with caption/credit | Commons photo (2017 prototype) |
| 04 | delays | 출시 약속은 2020년에서 출발해 2028년까지 밀렸다 | production-promise-2017, delay-2020-07, delay-2021-01, delay-2021-09, delay-2023-05, delay-2024-02, delay-2025-11, production-2028; quote-cnbc-missed | stepped phrase (staircase) | rising year labels left→right, 2028 in rose → CNBC quote in the empty top-left | CSS staircase |
| 05 | event | 2026년 10월 15일, Roadster는 23분짜리 야외 생중계로 공개됐다 | event-length-min, event-start-kst, unveil-2026-09 | metric-led split | 150px "23분" → editorial rows (time, venue, stage, original date) | none |
| 06 | demos | 관객 앞에서 보여준 묘기는 네 가지였다 | demo-ramp-flip, suction-2g-2026, demo-kickflip-cars, demo-zero60-live (주장), q-final-demo, demo-autonomous | editorial 2x2 grid | four panels: drawing → caption title → metric line with tag → body | self-drawn SVG (4 panels) |
| 07 | trims | 세 버전 가운데 ‘날 수 있다’고 한 것은 초대받은 1인승 Rocket뿐이다 | trims-2026, seats-2026, zero60-performance/thrust/rocket-2026, air-tank-2026, q-it-can-fly | split contrast (asymmetric) | small Performance/Thrust cards → large Rocket panel with Tesla quote | none |
| 08 | 2017 vs 2026 | 주행거리와 좌석은 절반 수준이 됐고, 가격은 아직 없다 | range-claim-2017, conv-range-2017-km, range-2026, conv-range-2026-km, seats-*, topspeed-*, price-base-2017, production-*, tg-topspeed-now, q-no-price-no-delivery | editorial text grid (table) | price row highlighted "발표 없음" → footnote on top speed | none |
| 09 | verification | 0.81초는 테슬라 타이머의 기록이다. 독립 측정은 아직 없다. | demo-zero60-live (주장), verify-no-independent-0-60, q-no-rides-2026, q-no-flight-range, quote-cnn-connor | split contrast + quote | shown (blue) vs not confirmed (amber) → curator quote | none |
| 10 | 0-60 | 0-60 주장은 1.9초에서 0.59초 미만까지 빨라졌다 | zero60-claim-2017, zero60-claim-2024, demo-zero60-recorded, demo-zero60-live, zero60-rocket-2026, cmp-plaid-0-60 | metric-led copy + chart | "1.9초 → 0.59초 미만" (claim) and the one measured value, Plaid 1.98 s → bars coloured by status → condition footnote | CSS bar chart |
| 11 | open questions | 생산은 2028년이라는 약속, 가격과 도로 허가는 아직 없다 | production-2028, q-no-price-no-delivery, q-rocket-not-road, quote-munster | stepped phrase (checklist) | three empty boxes stepping right → investor quote card | none |
| 12 | close | 보여준 묘기는 진짜였다. 이제 확인할 것은 날짜와 가격이다. | production-2028, quote-electrek | oversized statement (dark field, mirrors 01) | 60px focal → CTA question in status colours → "지켜볼 3가지" panel | none |

Family sequence: A C D C D E B E B D C A. No family three times in a row; all five families used.
Quotes (one per source): CNBC (04), Tesla X (07), CNN/Roger Connor (09), Reuters/Gene Munster (11), Electrek/Fred Lambert (12).

## Key placements (full-slide xywh)

- 01 focal `0.062 0.331 0.625 0.253` (left anchor, optical centre); metric `0.707 0.350 0.231 0.192` (right counterweight)
- 03 metric grid `0.062 0.364 0.461 0.346`; photo frame `0.556 0.364 0.382 0.300` (right counterweight, tops aligned)
- 04 staircase `0.063 0.375 0.875 0.500` (reading path left→right, rising); quote `0.062 0.314 0.313 0.200` (fills the empty triangle above low steps)
- 06 2x2 panel SVG `0.062 0.286 0.877 0.589`; captions inside each panel's right half
- 10 focal block `0.062 0.294 0.289 0.330`; chart `0.375 0.289 0.563 0.500`
- footer on every slide: `0.062 0.943 0.877 0.021` (source left, "비공식 정리 · Tesla와 무관 · NN / 12" right)

## Export decision

- `export_pdf.py` (Reveal `?print-pdf`) kept the line spacing but printed a 998x561 pt page in which the footer moved to about 27 px from the bottom edge (HTML: 70 px), so the PDF no longer matched the HTML. Per SKILL.md section 4 the final PDF was made with `export_pdf_shots.py` (screenshots of each slide, 1:1 with the HTML).

## QA log

- static guards: `qa_html_guard.py` pass (0 P0, 0 P2); `qa_media_guard.py` pass (0 P0, 0 findings) on `TeslaRoadster2026v1.html`
- layout probe (own helper using pt-maker's isolated browser runtime): no overflow, no element outside the stage, lowest content at least 49 px above the footer on every slide
- fixes made from rendered review (v1 build iterations before the final export):
  - 01 metric label wrapped "발표까지" as a short tail → intentional two-line label
  - 02 legend crowded the footer (19 px) → moved to the empty top-right; handwritten memo in the empty bottom-left
  - 03 photo top misaligned with the metric grid; caption break → aligned, intentional caption break
  - 04 quote split "목표로 / 한" → break at the clause
  - 05 "23분 / 21초" split across lines (P0) and a 5-character venue tail (P0) → kept the number together, one-line venue
  - 06 caption tails of 5 characters or fewer (P0) → title / metric line / body structure; ramp drawing redrawn so the car hangs under the overhang and lands
  - 07 title split "한 / 것은" and a dangling "·" in the Thrust line → explicit title break, shorter line, glossary moved to the note
  - 08 footnote touched the last table row (P0) → table moved up, footnote spaced
  - 09, 05, 07 large empty bands → blocks re-centred
  - 10 footnote collided with the axis labels (P0) → tighter rows, footnote below the axis, a tag on every value
  - 11 attribution split "Deepwater Asset / Management" → one name per line
  - 04 1 px raster seam on the staircase in the 2048 px capture → `will-change: auto` in the static pose and integer column widths; a faint 1 px seam remains in the capture only (recorded as P2)
- rendered artifacts: `TeslaRoadster2026v1.pdf` (12 pages, 16:9, 1280x720 pt), `TeslaRoadster2026v1_contact.png`, `qa/full-size/page_01..12.png` (2048x1152, rendered from the final PDF)
- independent QA reviewer agent, round 1 (rendered PNGs only): 87/100, P0 0. Fixes: p10 given its own role (claimed trend vs the one measured value), 0-60 mph defined on p3, 2G explained on p6, km/h added for top speeds on p8 (facts conv-topspeed-*), p11 title matched to its content, p1 footer made consistent, p5 tag moved to line end, p6 landing arrow and label, p7 card widths, p9 card balance, p4 memo wording
- live-HTML checks (isolated headless Chrome): keyboard ArrowRight/ArrowLeft works; notes on 12/12 slides; p4 wipe mid-frame opacity 0.31 resolves to 1 with no running animation; no infinite animation; reduced-motion and print show every animated element at opacity 1; nav arrows moved to the edges (`controlsLayout: 'edges'`); accessible labels added to the chart groups
- independent QA reviewer agent, round 2: 91/100, P0 0, pass
- final: guards pass (0 findings), PDF re-exported with `export_pdf_shots.py`, `verify_pdf.py` 12 pages all 16:9, contact sheet and all 12 full-size PNGs inspected, regression check pass
- qa-score: 91 · p0-count: 0 · p2-count: 6 · fixed-pages: 1, 3, 4, 5, 6, 7, 8, 9, 10, 11 · recheck-pages: all 12 · regression-check: pass
- `qa_score_gate.py TeslaRoadster2026v1.html qa_ledger.json`: pass (0 blocking issues)
- remaining P2 (accepted): p10 focal restates the title; no km/h for 214 mph or 60 mph (no labelled value in facts.json); bystander heads cut by the source photo's top edge; p9 4th item repeats p6; "v1" in the p1 footer meta; faint 1 px raster seam on p4 in the 2048 px capture
- not done: `qa_final_review_gate.py` (needs the owner's review and `user_review_ledger.json`); no taste-profile change proposed

## v2: research errata (ERRATA.md, fact-check round 1)

| errata | what changed in the deck |
|---|---|
| E1 four live demos | slide 06 title "관객 앞에서 보여준 묘기는 네 가지였다"; drawing redrawn as 4 panels, the 4th is a vertical launch into a corkscrew (livestream 00:21:28–00:22:12, Gizmodo); subtitle "네 시연 모두" |
| E2 0.81 s is Tesla's timer | the number is tagged 주장 on slides 06, 09 and 10 (bar recoloured from demo blue to claim amber, label "2026년 생중계 화면"); the run stays 시연 ("0-60 mph 가속 주행" in the 시연 card on 09) |
| E3 230 mph is Rocket only | slide 08 cell "Rocket만 230 mph 이상 (370 km/h 이상)"; notes cite Tesla X "up to >230mph (Rocket)" |
| E4 5 s of thrust is Thrust in a quarter mile | removed from slide 09 (it sat under "not confirmed" next to flight) and from its notes |
| E6 2025-11 moved production to 2027~28 | slide 04 already had the 2025.11 → 2027~28 step; checked, no change |
| E7 nobody on board | source changed from CBC to Electrek and CNN; notes mention the Starman mannequin |
| E10 CNBC 2017 date | footers on slides 02 and 03 now say CNBC(2017-11-17) |
| E13 calculated values | cover 3,255일 now tagged 계산 with both dates shown; new 계산 chip in the cover line and the slide 02 legend |
| E5, E8, E9, E11, E12 | not used in the deck (no McMurtry, no Wikipedia quote, no $250,000, no Rimac, no rollout claim); checked by grep |

Second pass after the updated facts.json (E13 now marks event-start-kst, conv-range-2017-km and conv-topspeed-2017-kmh as calculated): p5 Korean start time 검증 → 계산 with a note that it converts CNBC's 19:55 CDT; p3 "약 998 km로 환산 [계산]"; p8 note "2017년 km 값만 환산 [계산]"; p2 legend wording; p6 subtitle carries the slide-level 시연 label and card 4 a 시연 tag, card 2 arrow clearance; p9 시연 card lists the four live demos only ("스스로 달렸다" removed: demo-autonomous is a press report); p11 step offset reduced; internal ERRATA references removed from speaker notes; p5 rows tightened (lowest content 86 px above footer).

Fresh independent reviewer on v2: round 1 = 87, P0 1 (p5 tagged 검증); round 2 = 92/100, P0 0, E1–E13 all pass. `qa_score_gate.py TeslaRoadster2026v2.html qa_ledger.json`: pass (0 blocking issues).

v2 QA: guards pass (0 findings); PDF re-exported with `export_pdf_shots.py`; `verify_pdf.py` 12 pages, 16:9; live-HTML check repeated (keyboard, 12/12 notes, finite motion, reduced-motion and print poses); new 2x2 drawing on 06 inspected full-size before `data-fullsize-qa`/`data-rendered-qa` were set; fresh independent reviewer and `qa_score_gate.py` results are in `qa_ledger.json`.
