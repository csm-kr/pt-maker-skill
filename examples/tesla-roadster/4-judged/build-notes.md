# Build notes

- mode: `judged`
- production-direction: `judged`
- deck: `deck.src.html` → `deck.html` → `TeslaRoadsterJudgedv3.pdf` (13쪽, 13.333 × 7.5 in). v2 = 심사 라운드 1 반영, v3 = 라운드 2 반영(CHANGES.md).

## Intake (Grill Me, 이미 끝난 인테이크를 기록)

- 포맷: 4. 심사·제출용 (`judged`). 오너가 정한 답이라 질문하지 않았다.
- 심사용 질문 1 · 템플릿: 실제 대회 템플릿은 쓰지 않는다. 중립 합성 템플릿 "샘플 심사 템플릿"을 직접 만든다(`template/make_template.py`, `zipfile`만). 16:9 13.33 in, 모든 슬롯에 같은 120 px 머리 띠 + 아래 가는 막대. 슬롯(v3, 11개, 이야기 순서): 표지, 문제, 핵심 주장, 무엇을 보여줬나, 숫자 검증, 무엇을 약속했나, 일정, 한계, 결론, 출처, 감사. 머리 띠에 반쪽 표시 ① 보여준 것 / ② 남은 약속. 표지·감사는 띠에 슬롯 글자를 그리지 않는다(`match: skip`). 가장 작은 글자 12 pt = 24 px, 글꼴 Arial(한글은 시스템 고딕으로 대체).
- 심사용 질문 2 · 채점 기준(모의): 사실 정확성 40 · 메시지 명확성 25 · 근거 투명성 25 · 디자인 10.
- 심사용 질문 3 · 제한: 15쪽 이하, 5 MB 이하, 본편 슬라이드당 80단어 이하(v2부터 footer·슬롯 제목 포함으로 엄격히 셈), 본편 12장.
- 심사용 질문 4 · 근거: `research/facts.json`이 장부(그대로 복사, 있는 id만 사용). 실제 캡처는 공개 라이선스 페이지만: 영어 Wikipedia "Tesla Roadster (second generation)"의 텍스트만 자른 화면(CC BY-SA 4.0, footer와 CREDITS에 표기). 사진은 `IMAGES.md`의 2017 시제품 Commons 사진(연도 캡션, 로고 글자 없는 것). 나머지는 인라인 SVG. 생성 이미지는 근거로 쓰지 않는다(이 덱에는 생성 이미지가 없다).
- 참고자료: `research/SOURCE_MAP.md`, `facts.json`, `STORY.md`, `IMAGES.md`, `BRIEF.md` (content + evidence + constraint).
- 목적: 행사를 보지 못한 사람에게 약속한 것, 실제로 보여 준 것, 아직 약속인 것을 나눠 정직하게 요약.
- 청중: 차와 기술에 관심 있는 한국 일반 청중. 10분 스터디·팀 공유, 공유 화면.
- 한 줄 메시지: 보여준 것은 진짜 묘기, 남은 것은 약속. (긴 판: Roadster는 관객 앞에서 떠올랐지만, 가격·출시일·성능 수치는 아직 테슬라의 약속이다.)
- CTA(v2): 숫자를 들으면 물어보세요: 누가 말했고, 무엇으로 확인했나? (꼬리표 네 가지를 모두 덮는 질문)
- 분위기·색: 템플릿과 같은 중립 톤(짙은 슬레이트 띠, 강철 파랑 막대). 상태 꼬리표 색은 주장(호박색)·시연(파랑)·검증(초록)·보도(회색).
- 이미지 레벨: judged 고정 스타일(실제 캡처 + 주장형 문장 + 인라인 SVG). 애니메이션 없음.
- 미해결: 없음. 판단한 것: 꼬리표 네 가지(주장·시연·검증·보도, 보도는 스킬의 공식 4번째 상태). 계산값은 꼬리표 없이 근거 날짜를 옆에 둔다. "12장"은 본편 12장으로 읽고 부록 Q&A 1장을 더해 13쪽(15쪽 제한 안).

## Scene plan

| page | claim | evidence | visual plan |
|---:|---|---|---|
| 01 | 보여준 것은 진짜 묘기, 남은 것은 약속 | event-date, hist-unveil-2017-date, days-unveil-to-event | 2017 시제품 Commons 사진(contain), 비공식 표기 |
| 02 | 2020년 출시 약속은 지나갔고, 새 약속은 2028년 생산 | production-promise-2017, production-2028, years-promise-gap | 3단계 흐름 + 큰 숫자 |
| 03 | 한 줄 메시지와 꼬리표 4종 | demo-kickflip-cars, production-2028, event-length-min, production-slips-count | 카드 4개 + CTA 띠 |
| 04 | 관객 앞 시연은 세 장면 | demo-*, suction-2g-2026, conv-60mph-kmh, event-length-min | SVG 도식 3컷(설명용, 실제 장면 아님) |
| 05 | 첫 약속 대비 주행거리·좌석 절반 수준, 가격 없음 | 2017/2026 사양 fact 13개 | 비교표 |
| 06 | 0.81초는 테슬라 타이머 값, 독립 계측 없음 | demo-zero60-live/recorded, verify-* | Wikipedia 실제 화면 + 2열 카드 |
| 07 | 가장 빠른 0-60 발표 값은 줄었지만 측정 기록은 다른 차 | zero60-*, cmp-* | 가로 막대, 색 = 상태 |
| 08 | 출시 약속은 최소 6번 밀렸다 | delay-*, production-*, *-count | 계단 그래프, 가로축 = 말한 날짜(비례) |
| 09 | 가격·인도일·독립 측정은 확인 불가 | production-2028 + qualitative | 빈 체크리스트 + 인용 |
| 10 | 결론: 지켜볼 세 가지 | demo-zero60-live, production-2028 | 번호 목록 + CTA + 인용 |
| 11 | 모든 숫자는 출처로 이어진다 | 출처 링크 | 표 |
| 12 | 감사 | REPO_URL | 링크 + CTA |
| A1 | 예상 질문 네 가지 | tg-*, topspeed-2026, reservation-* | 카드 4개 |

## QA log

- v3 (심사 라운드 2 반영, 마지막 라운드)
  - static guard: qa_html_guard pass (P0 0, P2 1: speaker notes 없음) · qa_media_guard pass (0)
  - rendered artifacts: `slides/01.png`–`13.png`, `slides/text.txt`, `TeslaRoadsterJudgedv3.pdf`(13쪽, 1.5 MB), `TeslaRoadsterJudgedv3_contact.png`
  - layout/facts/submission: qa_layout_gate pass (0) · qa_facts_gate pass (0) · qa_submission_gate --offline pass (REPO_URL = tree/judged-deck/examples/tesla-roadster/4-judged)
  - 단어 수(엄격: 공백 토큰 전부, footer·슬롯 제목·띠 표시 포함): 쪽당 최대 77
  - rubric score: 93.02/100 (qa_score_gate pass)
  - 장부: research/facts.json, SOURCE_MAP.md, ERRATA.md에 E14–E20 반영 후 다시 복사
  - judge panel: 라운드 2 가중 7.4. 라운드 3은 없음(플레이북 한도).
- v2 (심사 라운드 1 반영)
  - static guard: qa_html_guard pass (P0 0, P2 1: speaker notes 없음) · qa_media_guard pass (0)
  - rendered artifacts: `slides/01.png`–`13.png`, `slides/text.txt`, `TeslaRoadsterJudgedv2.pdf`(13쪽, 1.46 MB), `TeslaRoadsterJudgedv2_contact.png`
  - layout/facts/submission: qa_layout_gate pass (0) · qa_facts_gate pass (0) · qa_submission_gate --offline pass (0, REPO_URL 채움)
  - 단어 수(footer·슬롯 제목 포함): 본편 최대 75(07쪽), 모두 80 이하
  - snapshot/contact-sheet review: 01–13 full-size PNG를 패스마다 직접 봄. 쪽 순서 01–12 + A1, bleed 없음.
  - rubric score: 93.02/100 (judged: 86점 만점 환산, qa_score_gate pass, `qa_ledger.json`)
  - judge panel: 라운드 1은 오케스트레이터가 실행(가중 7.0). 라운드 2도 오케스트레이터 몫(미실행).
  - regression check: pass (v2 contact sheet 전체)
  - browser: 모든 렌더·캡처는 skill의 격리 browser-harness로 했고 실행 뒤 종료됨.
- v1: CHANGES.md 패스 1–3 참고 (qa_score_gate 93/100, 판정 전).
