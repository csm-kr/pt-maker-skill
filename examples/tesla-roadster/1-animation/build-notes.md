# Build notes

- mode: `animation`
- production-direction: `animation` (format 1, 애니메이션 위주)
- version: v2 (2026-10-19), after the second fact-check round (E14–E20).
- final deliverable: `animation/tesla-roadster-발표용-v2.html` (horizontally navigable presentation built by `build_animated_presentation.py`). No MP4/WebM/GIF was requested, so none was rendered.
- visual direction: dark taste profile (`dark-taste-profile.md` v3) on top of `taste-profile.md` v12.

## Intake (completed in the shared brief; the owner was not asked again)

- format: animation, chosen by the owner for this sample.
- reference material: `research/SOURCE_MAP.md`, `research/facts.json`, `research/STORY.md`, `research/IMAGES.md` (content + evidence). No style reference deck.
- purpose: a clear, honest summary for people who did not watch the most recent Tesla Roadster presentation (2026-10-15, US Central). Separate what was promised, what was shown live, and what is still only a promise.
- audience: Korean general audience interested in cars and tech; a 10-minute study or team-sharing session on a shared screen.
- one-line message: 9년 만에 Roadster는 날아올랐다. 하지만 가격, 출시일, 성능 수치는 아직 테슬라의 약속이다.
- evidence: only `facts.json` and `SOURCE_MAP.md`. Every number on a slide is a fact id listed in the scene plan below. Status labels: 주장 = `claimed`, 시연 = `demonstrated`, 검증 = `verified`, 보도 = `reported` (SOURCE_MAP says to name the outlet for reported facts, so reported numbers carry a 보도 tag plus the outlet).
- CTA: 발표 숫자를 들으면 물어보세요: 주장인가, 시연인가, 검증인가?
- slides: 12. Language: Korean; product, spec and tool names stay in English.
- mood: near-black stage, subtle grid, five meaning colours, one or two accent words per title. Hero object: a generic SVG roadster silhouette.
- rights: no Tesla logos, wordmarks, press photos, livestream frames, or page screenshots. One CC BY-SA 4.0 Commons photo of the 2017 prototype (captioned as 2017, credited on the slide and in `animation/assets/CREDITS.txt`). The cover says 비공식 정리 and that the deck is not affiliated with Tesla. At most one quote per source (CNBC, Tesla X, Reuters/Munster, The Verge, Electrek).
- open questions: none.

## Words and claims kept out (from STORY.md)

- No "세계 최초", "가장 빠른 양산차", "날 수 있는 차" without the hop qualifier, "2028년 출시" (it is production start), or "$250,000 가격" (it is a deposit).
- Battery size (not disclosed), power (claimed: over 1 MW, `tg-power`, E19; left out for space, not because it is unknown), motor count, hover height, the 0.85 s variant, and the "400 mph" post are disputed or unconfirmed and are not shown. The 0.55 s figure appears only on scene 9, as the claim the one-foot rollout belongs to (E12).

## Scene plan

| scene | claim (title) | evidence (fact ids) | visual plan | motion purpose | signature build | speaker note |
|---:|---|---|---|---|---|---|
| 1 | Roadster, 다시 나타나다: 날았지만, 아직 살 수는 없다 | hist-unveil-2017-date, event-date, days-unveil-to-event | big SVG roadster on a road, agenda row, unofficial pill | car drives in and hops once: the "날았지만" verb | text-write | 8.9년 만의 발표. 약속·시연·검증으로 나눠 본다 |
| 2 | 약속은 2020년, 시연은 2026년, 다음 약속은 2028년 | production-promise-2017, event-date, production-2028, years-promise-gap | road with three milestone cards, dashed future segment, 8-year brace | car drives from the 2020 card to the 2026 card while the road draws | diagram-build | 이 세 점이 오늘의 지도 |
| 3 | 2017년 테슬라의 약속: 1.9초, 620마일, 4인승, 2020년 출시 | zero60-claim-2017, range-claim-2017, conv-range-2017-km, seats-claim-2017, production-promise-2017, price-base-2017, deposit-2017, conv-60mph-kmh | 2017 prototype photo + four claim cards + price line | photo wipes in, then the four claims stamp | image-reveal | 숫자는 모두 당시 테슬라 주장 |
| 4 | 약속한 연도는 2020년에서 2028년까지 계속 밀렸다 | production-promise-2017, delay-2020-07, delay-2021-01, delay-2021-09, delay-2023-05, delay-2024-02, delay-2025-11, production-2028, production-slips-count, unveil-dates-count, quote-cnbc-missed, deposit-2017 | chart A: step chart, x = date said, y = promised year; side stats | the roadster is the pen and climbs each step | line-draw | 약속할 때마다 한 칸씩 올라감 |
| 5 | 2026년 10월 15일, SpaceX 로켓 시험장에서 23분짜리 생중계가 열렸다 | event-postponed-from, event-date, event-start-cdt, event-start-kst (계산), event-length-min, event-venue-acres, event-presenters, event-x-live-views, event-yt-views | timeline band drawn to scale (1 tick = 1 day: 9/28 → 10/1 struck → 10/15) + four metric cards | car drives the band; the original date is struck through; metrics stamp | metric-stamp | 한국 시간 16일 아침 |
| 6 | 관객 앞 시연은 네 가지, 그중 세 장면: 매달리기, 차 5대 넘기, 0-60 질주 | demo-count-live, demo-ramp-flip, suction-2g-2026, demo-kickflip-cars, q-zero60-run-live, demo-zero60-live (주장), demo-final-corkscrew, demo-autonomous | three schematic panels (ramp loop, five-car arc, 0.81 s dial); the fourth demo is named in the subtitle; no photos or stream frames | paths draw with arrowheads, stroboscopic ghost poses appear, the dial sweeps to 0.81 | diagram-build | 네 번 시연했고 사람은 타지 않았다. 0.81초는 테슬라 타이머 값 |
| 7 | 세 버전 중 '날 수 있다'는 것은 초대받은 1인승 Rocket뿐이다 | trims-2026, seats-2026, zero60-performance-2026, zero60-thrust-2026, zero60-rocket-2026, reservation-performance-2026, reservation-thrust-2026, q-it-can-fly | three trim cards with a status chip on every row, Rocket highlighted, quote sticker | cards assemble, rows fill, hero car hops into the Rocket card | card-assembly | Rocket만 초대제 |
| 8 | 2017년 약속과 비교하면 주행거리·좌석은 절반 수준, 가격은 아직 없다 | range-claim-2017, range-2026, conv-range-2017-km, conv-range-2026-km, topspeed-claim-2017, topspeed-2026 (Rocket only), tg-topspeed-now, seats-claim-2017, seats-2026, price-base-2017, q-no-price-no-delivery | chart B: outline 2017 bars vs solid 2026 bars, seat icons, price cells (2017 base vs empty 2026) | the car drives the 2026 range bar and stops halfway | line-draw | 가격 칸은 비어 있다 |
| 9 | 0.81초는 테슬라 타이머의 기록이고 독립 측정은 아직 없다 | demo-zero60-live (주장), demo-zero60-recorded, q-no-flight-range, q-live-audience, verify-no-independent-0-60, verify-rollout (Tesla's later 0.55 s figure), tg-thrust-burst (Thrust, quarter mile), q-no-rides-2026 | two columns: 보여 준 것 / 확인 안 된 것 | columns arrive from opposite sides; "0건" stamps | card-assembly | 본 것과 잰 것은 다르다 |
| 10 | 0-60 주장은 1.9초에서 0.59초 미만으로 줄었지만 측정된 기록은 아직 다른 차의 것이다 | zero60-claim-2017, zero60-claim-2024, demo-zero60-recorded, demo-zero60-live, zero60-rocket-2026, cmp-plaid-0-60 (검증, 1-ft rollout, VHT surface), cmp-mcmurtry-0-60-carwow (1.4 s, 검증), cmp-nevera-0-60 (검증, Dewesoft·Racelogic, 1-ft rollout) | chart C: horizontal bars coloured by status, footnote on different conditions | bars draw in order; the car rides the 0.81 s bar | line-draw | 초록 막대는 다른 차뿐 |
| 11 | 2028년 생산, 가격, 도로 주행: 세 가지 모두 아직 빈칸이다 | production-2028, q-no-price-no-delivery, reservation-performance-2026, reservation-thrust-2026, q-rocket-not-road, quote-munster, quote-verge | checklist with empty boxes, two reaction quotes | rows write in, boxes draw but get "?", the car fades to a dashed outline | text-write | 체크 칸 세 개가 비어 있다 |
| 12 | 보여준 묘기는 진짜였고 이제 확인할 것은 가격·수치·날짜다 | production-2028, quote-electrek | mirrored cover: car left, title right; three checkpoints; CTA chips | the car waits before checkpoint 1; CTA chips and all status chips light up (accent payoff) | diagram-build | 주장인가, 시연인가, 검증인가 |

Signature build families: text-write, diagram-build, image-reveal, line-draw, metric-stamp, card-assembly (6). Title entrances rotate A/B/C so no three scenes in a row open the same way. Presenter seams: prism, curtain, aperture by seam index.

## Layout record (normalized full-slide xywh)

- persistent frame: kicker `0.050 0.057 —`, status rail right-aligned at `x ≈ 0.62–0.95, y 0.052`, source line `0.050 0.885 0.900 0.030`.
- titles: `0.050 0.119` (cover `0.050 0.219`, close `0.417 0.139`).
- dominant visuals: scene 4 chart `0.050 0.363 0.750 0.481` (intent: left-weighted plot, side stats as counterweight at `0.813 0.380 0.138 0.38`); scene 8 bars from `0.219` to `0.688` wide; scene 10 bars `0.333–0.787`.
- hero poses per scene: `motion-ledger.json` → `scenes[].hero_resolved_pose_xywh`.

## Process notes

- The compositions were generated by a one-off script that is not part of this example; the folder holds only the generated HyperFrames project.
- HyperFrames lint reports `multiple_root_compositions` once the presenter HTML sits next to `index.html` in `animation/`. The skill places it there, so lint and `check --snapshots` were run before the presenter was built, then the presenter was built.
- qa-agent: an independent reviewer agent scored every pass from the rendered PNGs, contact sheet and pose strips. The rubric was also scored manually; see the QA log.

## QA log (v2 build, 2026-10-19)

- errata applied: research/ERRATA.md E1–E13 (fact-check round 1) and the ledger ids listed there.
  - E1 (four demos): scene 6.
  - E2 (0.81 s is 주장; the run is 시연): scenes 6, 9, 10.
  - E3 (230 mph is Rocket only): scene 8.
  - E4 (5 s is Thrust, quarter mile): scene 9.
  - E5 (McMurtry): the 1.35 s bar is dropped; scene 10 uses Carwow's 1.4 s, 검증, with the source on the slide.
  - E6 (2025-11 moved production to 2027–28): scene 4.
  - E7 (no person on board; Electrek and CNN): scene 6.
  - E8 (not quoted anywhere).
  - E9 ("2026년 기준" deposit): scene 11.
  - E10 (no 2017 CNBC date is shown).
  - E11 (Nevera 주장, Plaid 검증): superseded by E14 in v2.
  - E12 (rollout belongs to 0.55 s only): scene 9.
  - E13 (계산 chip for 3,255일, 8년 and KST): scenes 1, 2, 5.
- errata applied in v2 (second round, E14–E20):
  - E14: scene 10 Nevera 1.74 s is now 검증 (green bar), with "Dewesoft·Racelogic 계측 · 1-ft rollout" under the label.
  - E15: no mannequin wording anywhere; scene 6 says only that no person was on board (Electrek·CNN).
  - E16: the deck never says the gap was always one or two years; scene 4 plots the actual promised years.
  - E17: scene 4 source line cites Electrek for 2027~28 (TechCrunch removed).
  - E18: scene 4 "최소 6번" is labelled 생산 일정이 밀린 횟수 and sourced to Electrek's production-slip count; the 7 unveil dates are a separate figure.
  - E19: the deck does not call power undisclosed; build notes now record power as claimed (over 1 MW, `tg-power`) and not shown.
  - E20: scene 10 shows "1-ft rollout · 처리(VHT) 노면" under the Plaid label, beside the rollout footnote.
- static guard (`qa_animation_guard.py`): pass, P0=0, P2=0.
- HyperFrames lint: 0 errors, 0 warnings. Run before the presenter HTML is built, because the presenter next to `index.html` triggers `multiple_root_compositions`.
- HyperFrames `check --snapshots` (background): pass. Lint 0, runtime 0, layout 0 issues across 9 samples, motion assertions 0 errors, contrast 144/144 WCAG AA, 5 snapshots in `animation/snapshots/`. Log: `animation/.pt-maker-runtime/logs/check-20261019-161701.log`.
- presenter HTML: `animation/tesla-roadster-발표용-v2.html`, built by `build_animated_presentation.py` with the default theme. GSAP 3.14.2 loads from the CDN exactly as in the pt-maker template (`https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`); nothing is vendored.
- presenter QA (`qa_animated_presentation.py`), run twice: pass both times.
  - 12 slides and 12 timelines.
  - 11 forward and 11 reverse seams; the same family on reverse.
  - prism, curtain and aperture all used.
  - Jump plus replay, keyboard and touch all work.
  - Max frame 16.8 ms, 0 frames over 25 ms.
  - Output: `qa/presenter-qa-run1.json` and `qa/presenter-qa-run2.json`. Earlier runs while the machine was loaded (load average around 20) had single cold frames over 40 ms; they did not recur once the load dropped.
- extra probe: ArrowRight, ArrowLeft, R (replay), touch swipes, End and Home all move the slide and restart its timeline.
- rendered artifacts:
  - `qa/contact-sheet.png` (12 resolved scenes) and `qa/resolved/scene-NN-resolved.png`.
  - `qa/poses/scene-04|08|10-*` (start, build start, mid-build, resolved) and the matching pose strips.
- snapshot and contact-sheet review: every resolved scene was inspected at full size after each fix round. Fixed along the way:
  - Card overflow (scene 2) and a number/unit split (scene 3).
  - Chart A crowding (scene 4).
  - Scene 9 column overflow into the footer, and scene 11 row collision.
  - v2: scene 10 Nevera condition line collided with the footnote; fixed by moving the conditions inside the green bars.
  - Bad Korean breaks, stale labels and the to-scale timeline (scene 5).
- rubric score: 90/100, P0 = 0 (v2). Manual score and independent reviewer agree. Earlier reviewer passes: 74 (first draft, gates pending), 87 (after E1–E13), 91 (v1 with vendored GSAP). v2 lost one technical point because GSAP loads from the CDN again, as the coordinator asked.
- `qa_animation_score_gate.py`: fail on one item only, `user_render_approved`. No video render was requested and the owner has not reviewed a preview in this run.
- user preview approval: not requested (no MP4/WebM/GIF).
- regression check: pass. The contact sheet was regenerated from the final source after the last fix, and all 12 scenes were rechecked.
- managed jobs: `hyperframes_mode.py stop animation --target all`, then `status`: every job `alive:false`.
- remaining P2: see `animation/animation_qa_ledger.json` → `remaining_p2`.
