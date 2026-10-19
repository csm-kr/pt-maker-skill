# NOTES

Tesla Roadster 발표(2026-10-15) 비공식 정리, 심사·제출용(`judged`) 샘플 덱 v3. 공개 예시용이며 실제 대회 제출물이 아니다.

## 마감과 근거 출처 (인테이크)

- 형식: 심사·제출용(`judged`). 실제 대회 템플릿은 쓰지 않고, 중립 합성 템플릿 "샘플 심사 템플릿"(`template/sample-judged-template.pptx`, `template/make_template.py`로 `zipfile`만 써서 만듦, 11슬롯)을 썼다.
- 모의 채점 기준: 사실 정확성 40 · 메시지 명확성 25 · 근거 투명성 25 · 디자인 10 (`judged.json`, 목표 가중 점수 8.0).
- 제한: 15쪽 이하, PDF 5 MB 이하, 쪽마다 80단어 이하(v3: 공백으로 나뉜 모든 토큰, footer·슬롯 제목·띠 표시·꼬리표 포함, 부록 포함), 본편 12장. 결과: 본편 12장 + 부록 1장 = 13쪽, PDF 1.5 MB, 쪽당 최대 77.
- 마감: 없음(샘플).
- 숫자를 가져올 문서: `facts.json` = `research/facts.json`(ERRATA E1–E20 반영본)을 바이트 그대로 복사. 덱은 37개 id를 쓴다.
- 실제 화면: 영어 Wikipedia 문서 "Tesla Roadster (second generation)" 판 1380953030의 한 문장(CC BY-SA 4.0, 그림·로고·각주 번호 없음).
- 사진: Wikimedia Commons의 2017년 시제품 사진 1장(Editor928111, CC BY-SA 4.0, 2019-06-11 촬영). 로고 글자가 보이는 사진은 쓰지 않았다.
- 저장소: `REPO_URL=https://github.com/csm-kr/pt-maker-skill/tree/judged-deck/examples/tesla-roadster/4-judged` (이 덱이 올라갈 폴더. 오케스트레이터가 push한 뒤 온라인 링크 검사를 돌린다.)

## 직접 채울 항목 (owner items)

| 항목 | 위치 | 채우는 법 |
|---|---|---|
| `REPO_URL` | 11, 12쪽 | `REPO_URL=https://github.com/csm-kr/pt-maker-skill/tree/judged-deck/examples/tesla-roadster/4-judged python3 build_judged_deck.py deck.src.html` (채움. 폴더가 생긴 뒤 `qa_submission_gate.py`를 `--offline` 없이 다시 돌린다) |
| 글꼴 | 전체 | Pretendard가 설치되지 않은 환경이라 Apple SD Gothic Neo로 렌더했다. 제출본은 글꼴이 들어간 PDF다. |

## 템플릿 슬롯 (v3 순서)

| 슬롯 | 제목 | 비교 | 반쪽 표시 |
|---|---|---|---|
| 1 | 표지 | skip (띠에 글자 없음) | |
| 2 | 문제 | exact | |
| 3 | 핵심 주장 | exact | |
| 4 | 무엇을 보여줬나 | exact | ① 보여준 것 |
| 5 | 숫자 검증 | exact | ① 보여준 것 |
| 6 | 무엇을 약속했나 | exact | ② 남은 약속 |
| 7 | 일정 | exact | ② 남은 약속 |
| 8 | 한계 | exact | ② 남은 약속 |
| 9 | 결론 | exact | |
| 10 | 출처 | exact | |
| 11 | 감사 | skip (띠에 글자 없음) | |

## 슬라이드 지도 (페이지 ↔ 템플릿 슬롯 ↔ 헤드라인)

| 페이지 | 슬롯 | 헤드라인 | 그림 | 단어(엄격) |
|---|---|---|---|---|
| 01 | 1 표지 | 보여준 것은 진짜 묘기, 남은 것은 약속 | 2017년 시제품 사진 | 49 |
| 02 | 2 문제 | 2020년 출시 약속은 지나갔고, 새 약속은 2028년 생산이다 | 3단계 흐름 + 8년(계산) | 53 |
| 03 | 3 핵심 주장 | 보여준 것은 진짜 묘기, 남은 것은 약속이다 | 꼬리표 4종 정의 + 예시 + 질문 | 75 |
| 04 | 4 무엇을 보여줬나 · ① | 관객 앞에서 4가지를 보여줬다: 매달리기, 차 5대 넘기, 가속, 수직 이륙 | 도식 4컷(넷째: 이륙 → 회전 → 착지) | 76 |
| 05 | 5 숫자 검증 · ① | 이번 성능 숫자는 모두 테슬라가 낸 값이다 | 큰 문장 "독립 계측 찾지 못함" + 0.81초 주장 + 작은 Wikipedia 캡처 | 64 |
| 06 | 5 숫자 검증 · ① | 테슬라 0-60 값은 더 빠르지만, 독립 측정 기록은 다른 차의 것뿐이다 | 가로 막대(점선 = 상한, 구분선) | 76 |
| 07 | 6 무엇을 약속했나 · ② | 첫 약속과 비교하면 주행거리와 좌석은 절반 수준, 가격은 아직 없다 | 비교표 | 76 |
| 08 | 7 일정 · ② | 2020년 약속은 2028년이 됐다: 생산 일정 최소 6번 연기 | 계단 ①–⑥ + 점마다 출처 링크 | 68 |
| 09 | 8 한계 · ② | 가격, 인도일, 독립 계측은 아직 확인할 수 없다 | 열린 항목 카드 4 + Munster 인용(번역 크게) | 76 |
| 10 | 9 결론 | 보여준 것은 진짜 묘기, 남은 것은 약속이다 | 지켜볼 세 가지 + 질문 + Electrek 인용 | 53 |
| 11 | 10 출처 | 슬라이드의 출처는 모두 열어 볼 수 있다 | 출처 26개 링크 + 장부 링크 | 76 |
| 12 | 11 감사 | 감사합니다 | 사진(표지와 짝) + 질문 + 장부 링크 | 32 |
| A1 | (슬롯 없음, 부록) | 질문 네 가지 | Q&A 카드 4 | 77 |

단어 수는 `slides/text.txt`에서 쪽 번호만 빼고 공백으로 나뉜 토큰을 모두 센 값이다. 라운드 2 심사위원의 11쪽 87–93은 " · " 구분자를 낱말로 센 값으로 보여, v3는 구분자를 쉼표·목록으로 바꾸고 같은 방식으로 셌다.

## 꼬리표 규칙 (하나의 체계)

- 정의(03, 06에서 같은 말): **주장** 회사나 발표자가 말한 값 · **시연** 관객 앞에서 보여 준 장면 · **검증** 독립 측정이나 공식 기록 · **보도** 언론 보도나 집계.
- 꼬리표는 숫자 바로 뒤에만 둔다. 제목, 질문, 숫자 없는 문장에는 두지 않는다.
- 계산값(3,255일, 8년)은 꼬리표 없이 계산에 쓴 날짜·해를 옆에 둔다.
- 고정 문구:
  - "생산 일정 최소 6번 연기 (Electrek 집계)" + 보도 (`production-slips-count`): 03, 08쪽.
  - "독립 계측 찾지 못함 (2026-10-19 기준)" + 보도 (`verify-no-independent-0-60`, The Verge): 03, 05, 09쪽.
- 0.81초는 주장(테슬라 타이머). 주행 자체만 시연(`q-zero60-run-live`).

## 숫자 → 출처 (페이지별 fact id)

| 페이지 | fact id (status) |
|---|---|
| 01 | hist-unveil-2017-date (reported), event-date (verified), days-unveil-to-event (calculated) |
| 02 | production-promise-2017, production-2028 (claimed); hist-unveil-2017-date (reported); event-date (verified); years-promise-gap (calculated); q-no-price-no-delivery |
| 03 | production-2028 (claimed), demo-kickflip-cars (demonstrated), cmp-plaid-0-60 (verified), production-slips-count (reported); 고정 문구 verify-no-independent-0-60 (reported) |
| 04 | demo-count-live, demo-kickflip-cars, demo-final-corkscrew (demonstrated); demo-zero60-live (claimed); conv-60mph-kmh, demo-autonomous (reported); q-zero60-run-live |
| 05 | demo-zero60-live (claimed); 고정 문구 verify-no-independent-0-60 (reported); Wikipedia 캡처 |
| 06 | zero60-claim-2017, zero60-rocket-2026, demo-zero60-live (claimed); cmp-plaid-0-60, cmp-nevera-0-60, cmp-mcmurtry-0-60-carwow (verified) |
| 07 | range-claim-2017, range-2026, seats-claim-2017, seats-2026, topspeed-claim-2017, topspeed-2026 (Rocket), zero60-claim-2017, zero60-performance-2026, price-base-2017 (모두 claimed); trims-2026, q-no-price-no-delivery |
| 08 | production-promise-2017 (처음 약속), delay-2020-07 ①, delay-2021-01 ②, delay-2021-09 ③, delay-2023-05 ④, delay-2024-02 ⑤, delay-2025-11 ⑥, production-2028 (새 약속) (claimed); production-slips-count (reported) |
| 09 | production-2028 (claimed); 고정 문구 verify-no-independent-0-60; q-no-price-no-delivery, q-rocket-not-road, quote-munster |
| 10 | production-2028 (claimed); quote-electrek |
| 11 | 숫자 없음 (출처 26개) |
| 12 | hist-unveil-2017-date (reported) |
| A1 | tg-thrust-burst, topspeed-2026, tg-topspeed-now, price-founders-2017, tg-power (claimed); reservation-thrust-2026 (reported); event-date (verified); q-no-flight-range |

08쪽 점별 출처(점 아래 링크): 처음 약속 CNBC 2017-11-17 · ① InsideEVs 2020-07-23 · ② Electrek 2021-01-28 · ③ Electrek 2021-09-01 · ④ InsideEVs 2023-05-17 · ⑤ Electrek 2024-02-28 · ⑥ Electrek 2026-10-13 · 새 약속 Reuters 2026-10-16. ①–⑥은 Electrek 2026-10-13의 "Every Roadster delay, so far" 목록과 하나씩 같다(2026-10-19 다시 읽음).

## 피한 주장 (claims avoided)

- "세계 최초의 비행 자동차", "세계에서 가장 빠른 양산차"(금지 표현에도 걸림).
- 조건 없는 "날 수 있다". 부록에서 "짧은 점프·회전·착지뿐"이라고 답한다.
- "시연은 세 가지"(E1).
- 0.81초를 시연 값으로(E2).
- 230 mph를 차 전체 값으로(E3).
- "공기 5초"를 비행으로(E4).
- McMurtry 1.35초(E5).
- 2025-11 발언 빼기(E6, E17).
- 마네킹만 탔다(E7, E15).
- Wikipedia "reservations reopened the same day"(E8, 캡처에서 뺐다).
- "차값 $250,000"(E9).
- 1피트를 0.59초에 붙이기(E12).
- 계산값에 꼬리표 붙이기(E13).
- Rimac을 주장으로(E14).
- "약속은 늘 한두 해 뒤"(E16).
- 시연 날짜 7개에서 "6번"을 끌어내기(E18).
- "출력 미공개"(E19).
- Plaid 조건 빼기(E20).
- "2028년 출시": 테슬라가 말한 것은 생산 시작이다.
- 배터리 용량, 모터 수, 충전 속도: 출처끼리 다르거나 미공개.
- "독립 시승·계측이 없었다": "찾지 못함 (2026-10-19 기준)"으로만 쓴다.
- "절반 수준"(07쪽): 주행거리 620 → 300 이상(하한), 좌석 4 → 2.

## 화면 캡처

| 페이지 | 그림 | 원본 URL · 판 · 찍은 시각 |
|---|---|---|
| 05 | `assets/img/wiki-roadster-not-timed.jpg` (한 문장) | https://en.wikipedia.org/w/index.php?title=Tesla_Roadster_(second_generation)&oldid=1380953030 · 판 1380953030 · 2026-10-19T15:41:16+09:00 (`shots.json`: viewport 1056×900, clip 16,1665,718,25, scale 2) |
| 01, 12 | `assets/img/roadster-2017-prototype-side.jpg` (사진) | https://commons.wikimedia.org/wiki/File:NextGenTeslaRoadster_(cropped).jpg |

캡처 문장: "Tesla also claimed a 0–60 mph run of 0.81 seconds during the event, which was not independently timed." 슬라이드는 "not independently timed" 위에 형광 표시를 겹친다.

## 검사 우회와 그 이유

- 손으로 쓴 fact span 두 곳(숫자 검사가 장부 단위 글자와 대조한다):
  - 07쪽 "Rocket 1인승"의 1 (`seats-2026` 단위 "…; 1 (Rocket)").
  - A1 "1,500마력" (`tg-power` 단위 "… (1,500 hp) …").
- `.nofact`:
  - "0-60"과 "0-60 mph"(지표 이름).
  - "1-ft rollout"(측정 조건 이름, 06쪽).
  - "(2026-10-19 기준)"(기준일).
- 05쪽 footer: 라이선스 이름이 문장 끝("CC BY-SA 4.0.")이면 숫자 검사가 4.0을 숫자로 센다(qa_facts_gate.py 55행 `(?![\w.])`). 괄호 안에 넣었다.
- 08쪽 점 아래 출처의 날짜는 SVG 링크(`<a>`) 글자라 숫자 검사에서 빠진다. 링크는 실제 기사로 간다.

## 아직 모르는 것

- 세 버전의 가격과 인도일.
- 모든 2026년 성능 수치의 독립 계측.
- 버전별 최고 속도(Rocket 230 mph 이상 vs 엔지니어 "지금은 214 mph"), 배터리 용량.
- 첫 공개 때 예약자 처리.
- Rocket의 도로 주행 승인 절차와 일정.
