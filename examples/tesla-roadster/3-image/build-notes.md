# Build notes

- mode: `presentation`
- production-direction: `image` (이미지 위주, format 3; chosen by the owner, recorded in BRIEF.md)
- runtime: Reveal.js 5.1.0, 1280×720, PDF + contact sheet
- skill: `pt-maker` on branch `judged-deck` (read only; scripts run by absolute path)

## Intake (Grill Me already done in `roadster/BRIEF.md`; no questions asked)

- topic: the most recent Tesla Roadster presentation, the "Roadster Event" of 2026-10-15 (US Central time)
- purpose: an honest summary for people who did not watch it; separate what was promised, what was shown live, and what is still only a promise
- audience: Korean general audience interested in cars and tech; 10-minute study or team sharing on a shared screen
- one-line message (STORY.md): "9년 만에 Roadster는 날아올랐다. 하지만 가격, 출시일, 성능 수치는 아직 테슬라의 약속이다." Short form: "보여준 것은 진짜 묘기, 남은 것은 약속."
- evidence: only `research/facts.json` and `research/SOURCE_MAP.md` (accessed 2026-10-19)
- CTA: when you hear a launch number, ask whether it was claimed, shown or verified
- slides: 12; language Korean (product, spec and tool names stay in English)
- reference material: none beyond the research folder; palette: the skill's fixed brand tokens (cream paper, indigo ink, rose accent) plus three status colors
- rights: no Tesla logos or wordmarks, no press photos, no livestream frames, no screenshots; cover says 비공식 정리 / not affiliated
- image level: image-led; Claude Code has no image generator, so everything that is not a Commons photo is self-made SVG/CSS

## Number labels (every number on a slide carries one of three chips)

| facts.json status | chip on slide | rule |
|---|---|---|
| `claimed` | 주장 (amber) | Tesla or Musk said it |
| `demonstrated` | 시연 (blue) | shown live on 2026-10-15 |
| `verified` | 검증 (green) | platform record, date arithmetic or independent measurement |
| `reported` | never shown as 검증 | a reported number that originates from a company (Tesla deposit terms, Rimac and McMurtry records) is chipped 주장 with the owner named; press counts (`production-slips-count`, `unveil-dates-count`) are not used; reported qualitative items (no price, no rides, no independent timing) are shown as words, not numbers |

Unit conversions inherit the chip of the number they convert (620마일 ≈ 998 km → 주장). Pure calculations (3,255일 between two dates, the 8-year gap, 60 mph ≈ 97 km) carry no chip and show their inputs (ERRATA E13).

## Images

| asset | source | license | used on |
|---|---|---|---|
| `assets/roadster-2017-prototype-side-2019.jpg` | Wikimedia Commons, Editor928111 (IMAGES.md #1) | CC BY-SA 4.0 | slide 1 only |
| `assets/roadster-2017-prototype-interior-2019.jpg` | Wikimedia Commons, Steve Jurvetson (IMAGES.md #3) | CC BY 2.0 | slide 3 only |

Not used: IMAGES.md #2 and #5 (same side angle as #1, would repeat it; #2 also shows identifiable faces), #4 and #6 (Tesla "T" logo visible on the nose), #7 ("TESLA" letters on the rear). Every other visual is drawn in SVG/CSS for this deck.

## Visual plan: claim → image (written before the build)

| # | role (기승전결) | claim (slide title) | image that explains or proves it | asset type | crop / subject safety | fallback |
|---:|---|---|---|---|---|---|
| 1 | 기 · hook | 9년 만에 나타난 Roadster: 날았지만, 아직 살 수는 없다 | Commons photo of the 2017 prototype from the side: the car promised in 2017 is real hardware, but it is a 2017 prototype (caption "2017년 공개 시제품, 2019년 촬영 — 2026년 차 아님"); indigo note card with 3,255일 검증 | photo + CSS panel | `object-fit: contain`, frame ratio = photo ratio (4120:1699), whole car visible; no logo visible at this angle | solid panel cover |
| 2 | 기 · map | 약속은 2020년, 시연은 2026년, 다음 약속은 2028년 | three-step SVG: 2017 promise (2020 출시, 주장) → 2026-10-15 live demo (시연) → new promise (2028 생산, 주장), bracket "8년 뒤로"; legend of the three chips | SVG diagram | n/a | — |
| 3 | 승 · 2017 promise | 2017년 테슬라는 1.9초, 620마일, 4인승, 2020년 출시를 약속했다 | Commons photo of the 2017 prototype's cabin (the car the promise came with) + four number cards, all 주장 | photo + CSS cards | `contain`, frame ratio = photo ratio; caption gives the year | cards only |
| 4 | 승 · delays | 출시 목표는 2020년에서 2028년까지 계속 밀렸다 | Chart A: step chart, x = when it was said, y = promised year, grey diagonal = the year it was said; CNBC quote | SVG chart | n/a | — |
| 5 | 승 · event | 2026년 10월 15일, SpaceX 로켓 시험장에서 23분짜리 생중계가 열렸다 | to-scale date timeline 9/12 teaser → 10/1 postponed → 10/15 held, 23-minute stream block; venue and presenters cards | SVG timeline + CSS cards | n/a | — |
| 6 | 전 · shown | 관객 앞 시연은 네 번: 뒤집기, 차 5대 넘기, 0-60 질주, 수직 상승 | demo-sequence diagram, four panels: ramp → upside-down → flip → landing; parabola over five vehicle blocks; speed–time curve (run 시연, 0.81 s value 주장); vertical launch into a corkscrew | SVG diagram with the generic roadster silhouette | n/a | — |
| 7 | 전 · trims | 세 버전 중 테슬라가 '날 수 있다'고 한 것은 초대제 1인승 Rocket뿐이다 | three generic roadster silhouettes showing where the thrusters are (none / rear / around the body) + three spec cards (주장) | SVG + CSS cards | silhouette is generic, not traced | — |
| 8 | 전 · then vs now | 주행거리는 절반, 좌석도 절반, 가격은 아직 없다 | Chart B: paired bars 2017 vs 2026 for range, seats, price (empty dashed bar = 발표 없음); deposit explainer card | CSS bar chart | n/a | — |
| 9 | 전 · verification | 0.81초는 테슬라 타이머의 기록이다. 독립 측정은 아직 없다 | measurement-chain diagram: Tesla lane filled, independent lane empty ("찾지 못함"); 1-ft rollout ruler | SVG diagram | n/a | — |
| 10 | 전 · comparison | 0-60 주장은 1.9초에서 0.59초 미만까지 줄었지만, 검증된 값은 다른 차의 것뿐이다 | Chart C: horizontal bars colored by chip (주장 / 검증), Roadster rows vs Model S Plaid (검증) and Rimac Nevera (주장, manufacturer), footnote "conditions differ" | CSS bar chart | n/a | — |
| 11 | 결 · open promises | 생산 시작, 가격, 도로 주행 허가: 세 가지는 아직 약속이다 | clipboard with three empty check boxes and icons (calendar, price tag, road sign); two press quotes | SVG drawing + quote cards | n/a | — |
| 12 | 결 · CTA | 보여 준 묘기는 진짜였다. 이제 확인할 것은 날짜와 가격이다 | sorter: numbers from the deck dropped into 주장 / 시연 / 검증 bins, arrow "주장 → 검증으로 옮기려면: 가격 발표 · 독립 계측 · 2028년 생산 시작"; mirrors the cover's indigo panel on the other side | SVG diagram on indigo panel | n/a | — |

No slide is text-only; no image is used twice; the generic silhouette appears as a glyph inside the slide 6, 7 and 9 diagrams.

## Scene plan

| slide | claim | evidence (facts.json ids) | visual plan | motion purpose | speaker note |
|---:|---|---|---|---|---|
| 1 | 9년 만에 나타난 Roadster | event-date, days-unveil-to-event | photo + note card | title rises, photo fades | unofficial summary, how to read the chips |
| 2 | 2020 → 2026 → 2028 | production-promise-2017, event-date, production-2028, years-promise-gap | 3-step SVG + legend | diagram fades in left to right reading | the three chips |
| 3 | the 2017 promise | zero60-claim-2017, range-claim-2017, conv-range-2017-km, seats-claim-2017, production-promise-2017, conv-60mph-kmh | interior photo + 4 cards | cards rise | 2017 numbers were promises |
| 4 | the date kept moving | production-promise-2017, delay-2020-07, delay-2021-01, delay-2021-09, delay-2023-05, delay-2024-02, delay-2025-11, production-2028, quote-cnbc-missed | chart A | chart wipes left to right (time) | always one or two years away |
| 5 | the event | unveil-2026-09, event-postponed-from (words only), event-date, event-start-kst, event-length-min | timeline + cards | timeline wipes | when and where |
| 6 | three demos | demo-ramp-flip, suction-2g-2026, demo-kickflip-cars, demo-zero60-live, demo-autonomous (words) | demo diagram | panels fade | what was really shown |
| 7 | three trims | trims-2026, seats-2026, zero60-performance-2026, zero60-thrust-2026, zero60-rocket-2026, q-it-can-fly | silhouettes + spec cards | rise | only Rocket is "air ready" |
| 8 | 2017 vs 2026 | range-claim-2017, range-2026, conv-range-2026-km, seats-claim-2017, seats-2026, price-base-2017, q-no-price-no-delivery, reservation-performance-2026, reservation-thrust-2026 | chart B | bars wipe | half the range, no price |
| 9 | who measured 0.81 s | demo-zero60-live, demo-zero60-recorded, verify-no-independent-0-60, verify-rollout, tg-thrust-burst, q-no-rides-2026, quote-cnn-connor | chain + ruler | fade | Tesla timer only |
| 10 | claims vs measured | zero60-claim-2017, zero60-claim-2024, demo-zero60-recorded, demo-zero60-live, zero60-rocket-2026, cmp-plaid-0-60, cmp-nevera-0-60, cmp-mcmurtry-0-60 | chart C | bars wipe | only one green bar, and it is another car |
| 11 | open promises | production-2028, q-no-price-no-delivery, q-rocket-not-road, quote-munster, quote-verge | clipboard | fade | three empty boxes |
| 12 | CTA | numbers already shown on 2, 5, 6, 7, 8 + quote-electrek | sorter | fade | ask: claimed, shown or verified? |

## XYWH (full-slide ratios, 1280×720)

Recorded as `frame: slide; xywh: …; intent: …` comments next to every major object in `테슬라로드스터발표v1.html`, corrected after the final layout moves so they match the rendered PNGs.

## Changes made during QA (all in v1, before first delivery)

- Generic silhouette: roofline lowered so it reads as a low roadster, not a sedan.
- Slide 5 timeline redrawn to scale (28 px per day) so the third stop no longer runs under the stream block.
- Slide 7 redrawn: plumes instead of loose lines; Tesla's "So...yes, it can fly" moved into a speech bubble over Rocket.
- Slides 9 and 11: two aria-labels reworded ("보여 주는" → "나타낸", "주행" → "운행"). `qa_media_guard.py` treats the syllable "주" in the 500 characters around an inline SVG as a map word and flagged both charts as real maps (false positive); the wording change clears it without marking charts as schematic maps.
- PDF route: `export_pdf.py` (print-pdf) was tried first in a scratch folder; its page box is 998×561 pt and the footer drifts to the page edge, so the final PDF uses `export_pdf_shots.py` (1280×720, identical to the screen).
- Reviewer round 1 (independent agent, 79/100, 2 P0): fixed the slide 6 landing arrowhead (drawn along the path tangent; the marker had rendered reversed) and the slide 8 correction text that split modifier and noun. Also fixed: cover "날았지만" → "잠깐 떠올랐지만" (no overclaim), 출시/생산 wording on slide 4, 주장 chip on the 10/1 date, slide 11 title ("세 칸은 아직 비어 있다"), concept labels on the slide 6 curve and slide 9 ruler, several phrase splits, page number 16 → 18 px.

- Reviewer round 2 (84/100, 1 P0): the cover's light panel ran under the "1 / 12" slide number. The panel is now inset 40 px on both sides at full height (number not shrunk). Also: slide 3 gloss clause order, slide 5 chip moved under its sub-label like the other stops, slide 8 repeated red line removed, slide 11 quote 1 breaks fixed.
- Live-HTML check (`qa/interaction_check.json`, `qa/motion/`): Reveal's default bottom-right arrows overlapped the slide number in the live deck (not visible in the PDF, which is captured with controls off). Fixed with `controlsLayout: 'edges'`.
- Reviewer round 3 (91/100, 0 P0). Optional P2s fixed afterwards and rechecked by me (score not raised): slide 5 scale note back under the timeline, slide 8 side card centred on the chart, live progress bar recoloured (accent on a light track), Reveal slide/background transitions switched off under prefers-reduced-motion (the 400 ms background fade was still running).

## Errata applied (research/ERRATA.md, fact-check round 1, received after reviewer round 3)

- E1: slide 6 now shows four live demos (adds the final vertical launch into a corkscrew).
- E2: 0.81 s is labelled 주장 (Tesla timer) on slides 6, 9, 10 and 12; the live run itself stays 시연.
- E3: no 230 mph figure appears in the deck.
- E4: the "추진 약 5초" item was removed from the flight context on slide 9.
- E5: McMurtry bar removed from slide 10.
- E6: chart A already had the 2025-11 → 2027~28 step; kept.
- E7: slide 6 says no person was on board (mannequin only), sourced to Electrek and CNN.
- E8: not used in this deck.
- E9: slide 8 card says "2026년 예약금은 차값이 아니다" and notes the 2017 Founders Series price was $250,000 (주장).
- E10: CNBC 2017 dated 2017-11-17 on slides 2 and 3.
- E11: Rimac 1.74 s stays 주장 (manufacturer), Plaid 1.98 s stays 검증 (MotorTrend).
- E12: the 1-ft rollout is attached to Tesla's later, faster figure, not to 0.59 s.
- E13: calculated values (3,255일, 8년, 60 mph ≈ 97 km) carry no chip and show their inputs.

- Reviewer round 4 (after the errata, 88/100, 2 P0): slide 5 Korean time still chipped 검증 although `event-start-kst` is now calculated (the 검증 chip now belongs to "Tesla YouTube 기록" and the time is an unchipped grey line); slide 12 source line still cited page 7 (now "2·5·6·8·9쪽"). P2s fixed in the same pass: slide 6 glosses moved into their own band, panel ③ concept label restored, panel ④ path starts at the car; slide 9 chain coloured by status (run 시연 blue, timer neutral, 0.81초 주장 amber); slide 2 note on unchipped calculated values; slide 3 "약 998 km(환산)"; slide 8 legend "km는 환산" and card aligned to the legend.
- Reviewer round 5: 93/100, 0 P0. No edits after that review.

## v2: errata round 2 (research/ERRATA.md E14–E20)

`테슬라로드스터발표v2.html` / `.pdf` / `_contact.png` replace v1 (v1 files kept in the folder as history; the cover footer, `<title>` and `data-deck-version` say v2).

- E14: slide 10 Rimac Nevera 1.74 s is now 검증 (label "외부 계측", green bar); the footnote names Dewesoft·Racelogic and the 1-ft rollout; speaker notes say two green bars, both other cars. This reverses E11.
- E15: slide 6 gloss says "사람은 타지 않았다" (no mannequin generalisation); notes cite Electrek and CNN.
- E16: slide 4 notes give the real gaps (2017-11 → 2020 is three years, 2025-11 → 2027~28 is two to three years) instead of "한두 해".
- E17: slide 4 source line cites Electrek (2026-10-13) for 2027~28; TechCrunch removed.
- E18, E19: not used in this deck (no production-slip count, no power figure).
- E20: slide 10 footnote states Plaid 1.98 s conditions (1-ft rollout, prepped VHT surface) next to the rollout note.

- v2 reviewer (fresh agent) round 1: 89/100, 0 P0. Fixed: p2 note "시속 약 97 km" and press-reported figures are 주장; slide 2 notes match the no-chip rule; p3 "시속 60마일 ≈ 시속 97 km"; p5 stops centred, scale note moved to the footer, "9:55 시작 예정(시차 계산)" (SVG made taller after I caught the second line clipped); p12 headline "묘기는 실제로 해냈다." and path to 검증 "독립 계측 · 실제 생산과 인도" (price is an open gap, not verification); p6 "1초" label; p11 row "Rocket 공공도로 주행 허가".
- v2 reviewer round 2: 91/100 with 1 P0 (p11 subline repeated "Rocket:"). Fixed, plus p6 tick labels on one baseline and slide 5 notes "시작 예정".
- v2 reviewer round 3: pass, 91/100, 0 P0. No edits after that review.

## QA log

- qa-agent: independent general-purpose reviewer agent (renders only, no edits)
- static guard: `qa_html_guard.py` pass (0 P0, 0 P2); `qa_media_guard.py` pass (0 findings)
- rendered artifacts: `테슬라로드스터발표v1.pdf` (12 pages, 1280×720 pt, from `export_pdf_shots.py`), `테슬라로드스터발표v1_contact.png` (`verify_pdf.py`: 12 pages, all 16:9), `qa/pages/page_01..12.png` (2048 px, rendered from the exact final PDF)
- snapshot/contact-sheet review: every page inspected at full size by me after the last export; contact sheet inspected for rhythm and bleed
- rubric score (v2): 91/100 (narrative 17, visual system 13, layout 17, evidence 12, motion 11, interaction 10, delivery 11), p0-count 0, p2-count 5 (listed in `qa_ledger.json`). v1 history: 79 → 84 → 91 → 88 → 93 with the earlier reviewer.
- score gate (v2): `qa_score_gate.py 테슬라로드스터발표v2.html qa_ledger.json` → pass (0 blocking issues), saved as `qa/score_gate.json`
- live HTML (v2): `qa/interaction_check.json` (keyboard, notes, alt, labelled motion build and backward replay, reduced motion with 0 running animations)
- user preview approval: not part of this run (sample deck; owner reviews later; `qa_final_review_gate.py` not run)
- regression check: full contact sheet and all 12 full-size pages rechecked after the last fix; no new wrapping, overflow, crop or order problems
