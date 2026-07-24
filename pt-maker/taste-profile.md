---
version: 12
updated: 2026-07-24
profile_id: bright-notebook-default
---

# 사용자 취향 프로필

`pt-maker`가 덱을 만들기 전에 읽는 기본 취향 정본이다. 업데이트는 사용자가 명시적으로 말한 선호와, 좋은 발표자료에 대한 외부 자료 원칙을 합쳐 기록한다.

## 0. 절대 QA 게이트
- 텍스트 안정성이 최우선 미감 기준이다. 렌더된 PDF/PNG에서 텍스트가 넘침, 잘림, 겹침, 박스/아이콘/푸터 접촉, 어색한 줄바꿈을 보이면 그 덱은 0점으로 보고 수정 후 다시 렌더링한다. [conf: high]
- 한 슬라이드는 한 주제만 다룬다. 제목에 "그리고/및"이 들어가거나 두 주장을 동시에 설명하면 분리한다. [conf: high]
- 슬라이드 제목은 장식용 토픽명이 아니라 그 장의 결론/핵심 문장이어야 한다. 제목만 훑어도 발표 흐름이 읽혀야 한다. [conf: high]
- 최종 검수는 HTML 미리보기가 아니라 실제 전달 PDF 기준이다. PDF 페이지 순서, 누락/중복, contact sheet, 전체 회귀 검사를 확인한다. [conf: high]
- 텍스트가 안 맞으면 먼저 줄이고, 나누고, 넓히고, 재배치한다. 작은 글자, 빽빽한 줄간격, 임시 축소로 해결하지 않는다. [conf: high]

## 1. 구조와 스토리
- 전체 흐름은 명확한 한 줄 메시지를 중심으로 기-승-전-결이 있어야 한다. 훑어보는 사람이 "그래서 무엇을 기억해야 하는지"를 바로 잡아야 한다. [conf: high]
- 긴 수업/강의형 덱은 단조로운 반복보다 리듬감 있는 전환을 선호한다. 단, 변주는 alignment, hierarchy, spacing, text fit을 해치면 실패다. [conf: high]
- `one takeaway per slide`를 기본으로 한다. 한 슬라이드가 여러 역할을 하면 핵심 1개만 남기거나 여러 장으로 쪼갠다. [conf: high]
- 정보는 충분히 꽉 차 있어야 한다. 큰 빈 공간만 남기는 것보다, 의미 있는 시각자료, 손글씨 메모, 작은 도식, 색상 표식으로 화면을 밀도 있게 채운다. [conf: high]
- 꽉 찬 화면은 "많이 넣기"가 아니라 "잘 묶기"다. 같은 그룹은 가깝게, 다른 그룹은 확실히 띄우고, 시선이 지나가는 순서를 설계한다. [conf: high]

## 2. 비주얼 기본 취향
- 기본 무드는 밝은 크림 종이/모눈종이/노트 위에 정리한 느낌이다. 모눈종이에 글씨를 쓰는 듯한 질감은 좋다. [conf: high]
- 손글씨 같은 글씨체는 중요한 취향 포인트다. 짧은 메모, 감탄, 화살표 주석, 스티커 라벨, 챕터 전환의 작은 한 줄, 모눈종이 위 덧쓴 느낌으로 적극 사용한다. [conf: high]
- 단, 사실 정보와 숫자에는 쓰지 않는다. 정확한 주장, 연도, 수치, 고유명사, 출처는 정자체로 두고, 손글씨는 인간적인 강조와 리듬을 만드는 보조 장치로 쓴다. [conf: high]
- 알록달록한 색을 선호한다. 다만 색은 의미를 가져야 한다. 핵심/위험/기회/보조/중립처럼 역할을 나누고, 같은 의미에는 같은 색을 반복한다. [conf: high]
- 한 계열 색만 반복되는 덱은 피한다. 베이지 일변도, 어두운 남색/슬레이트 일변도, 보라 그라데이션 일변도, 브라운/오렌지 일변도는 특별한 이유가 없으면 피한다. [conf: high]
- 주요 슬라이드는 텍스트만 두지 않는다. 사진, 스크린샷, 차트, SVG 도식, 타임라인, 비교표, 지도, 원본 손그림 중 하나가 핵심 메시지를 실제로 받쳐야 한다. [conf: high]
- 사진은 피사체 보존이 우선이다. 얼굴, 머리, 제품, 음식, 로고, 지도, 스크린샷의 핵심 부분이 잘리면 이미지 선택이나 프레임을 바꾼다. [conf: high]
- 실제 지도는 공식/공개/웹 지도 베이스를 쓰고 그 위에 핀, 루트, 라벨을 얹는다. 지리 정확성이 필요한데 손으로 대충 그린 지도는 금지한다. [conf: high]

## 3. 레이아웃 취향
- 선호하는 방향은 "다이나믹하지만 구조화된 레이아웃"이다. 화면은 풍성해야 하지만, 요소들이 심리적으로 겹치거나 어디를 봐야 할지 모르게 만들면 실패다. [conf: high]
- 덱 안에서 3-4개 이상의 구조적 레이아웃을 섞는다: split, mirrored split, centered statement, card matrix, dashboard, timeline/flow, image-led, diagram-led. [conf: high]
- 반복 카드 그리드만 계속 쓰지 않는다. 카드가 답답해지면 카드 수를 줄이거나, 큰 도식/타임라인/분할 슬라이드로 바꾼다. [conf: high]
- 주요 메시지는 화면의 시각적 중심 근처에 있어야 한다. 남은 내용을 얕은 하단 카드로 몰아넣는 방식은 피한다. [conf: high]
- 도형, 라벨, 아이콘, 번호, 화살표는 서로 충분히 떨어져야 한다. "살짝 닿는" 상태도 지저분하게 보이면 P0로 본다. [conf: high]
- 페이지가 비어 보이면 의미 있는 저채도 장식, 손글씨 메모, 작은 보조 도식을 넣되 콘텐츠를 가리지 않는다. 장식은 슬라이드당 1-2개 정도로 제한한다. [conf: med]
- 화면이 너무 딱딱해 보이면 손글씨 포인트를 먼저 고려한다. 단어 하나를 손글씨로 바꾸기보다, 여백의 짧은 주석/밑줄/동그라미/화살표처럼 "누가 직접 표시한" 느낌을 선호한다. [conf: high]

## 4. 타이포그래피와 가독성
- 일반 1280x720 HTML 덱 기준 본문/불릿은 보통 28-30px, hard floor 26px, 카드 본문 24-26px, 보조 라벨 20-22px, 출처/fine-print 15-16px를 기준으로 한다. 큰 발표장용이면 본문을 32px 안팎으로 올린다. [conf: high]
- 줄간격은 넉넉해야 한다. 본문은 `line-height >= 1.5`, 보통 1.56 전후를 선호한다. [conf: high]
- 한국어 줄바꿈은 `word-break: keep-all`, 제목은 `text-wrap: balance`, 본문은 가능하면 `pretty`를 써서 짧은 꼬리 줄과 어색한 고유명사 분리를 막는다. [conf: high]
- 한글 라벨과 kicker에는 Pretendard를 쓴다. 한글을 JetBrains Mono로 벌려 보이게 만드는 것을 피한다. [conf: high]
- 정확한 연도, 숫자, 고유명사, 출처는 손글씨가 아니라 정자체로 둔다. [conf: high]

## 5. 외부 원칙 반영
- Harvard Catalyst와 Harvard T.H. Chan의 assertion-evidence 원칙처럼, 제목은 주장이고 본문은 그 주장을 시각 증거로 받치는 구조를 선호한다. [conf: high]
- Broad Institute/MIT Comm Lab과 PLOS의 원칙처럼, 각 슬라이드는 한 가지 메시지를 전달하고 제목이 그 메시지를 직접 말해야 한다. [conf: high]
- NN/g의 visual hierarchy/cognitive load 원칙처럼, 색상, 대비, 크기, 묶음, 여백으로 시선 순서를 설계하고 불필요한 장식·중복·의미 없는 타이포 변주를 줄인다. [conf: high]
- Duarte의 원칙처럼 색은 취향이 아니라 의미 전달 장치로 쓴다. 색이 많더라도 역할이 분명해야 한다. [conf: high]

## 6. 어투와 정보 밀도
- 문장은 짧고 단정하게 쓴다. 설명문보다 강한 제목, 짧은 라벨, 시각 증거가 우선이다. [conf: high]
- 수업/강의형 덱은 학생이나 청중이 한 장씩 따라갈 수 있게, 장마다 정확히 무엇을 봐야 하는지 드러내야 한다. [conf: high]
- 발표자가 말로 풀 내용과 슬라이드에 남길 내용을 분리한다. 슬라이드는 원고가 아니라 기억과 이해를 돕는 구조물이어야 한다. [conf: high]

## 7. 안티 취향
- 텍스트만 있는 주요 슬라이드. [conf: high]
- 멋은 있지만 한 슬라이드 안의 주제가 흐려지는 구성. [conf: high]
- 알록달록하지만 의미 없이 흩어진 색. [conf: high]
- 빈 공간이 많아 성의 없어 보이는 슬라이드. [conf: high]
- 촘촘한 줄간격, 박스 가장자리에 붙은 글자, 푸터와 충돌하는 하단 요소. [conf: high]
- 모든 슬라이드가 같은 좌텍스트/우이미지 또는 같은 카드 그리드로 반복되는 덱. [conf: high]
- 손글씨를 사실 정보, 숫자, 고유명사에 쓰는 것. [conf: high]

## 8. 운영 메모
- 새 덱 시작 전 이 파일을 읽고 기본값으로 적용한다. [conf: high]
- 사용자 참고자료에서 스타일을 추출할 때는 바로 저장하지 말고, 반영할 diff를 제안하고 확인된 것만 기록한다. [conf: high]
- 이미지 생성은 사용자의 승인 전에는 플레이스홀더로 두고 예상 장수와 슬라이드별 목적을 알린다. Codex에서는 `$imagegen` built-in 경로를 사용하고 API 키나 고정 장당 비용을 요구하지 않는다. [conf: high]
- 최종 보고에서 QA 결과, PDF/contact sheet 검수 여부, 생성 이미지 수, 저장 경로, 사용 모드(`imagegen built-in` 또는 승인된 fallback)를 요약한다. [conf: high]

## 9. HTML-native 모션과 연속 이미지
- `.html`이 제공하는 레이어, fragment, 발표자 노트, 분기 이동, 유한 모션을 적극 활용하되, 효과 수보다 메시지 이해와 장면 연속성을 우선한다. [conf: high]
- 모션 전환 어휘는 덱당 2~3개로 제한하고, 진행 방향과 속도가 슬라이드 seam에서 이어져야 한다. 이유 없는 방향 반전과 무한 wobble/pulse/float는 피한다. [conf: high]
- 핵심 장면은 배경/중경/전경을 설계하고, 정적인 PDF에서도 메시지가 완전하게 남도록 print pose를 명시한다. [conf: high]
- `prefers-reduced-motion`에서 콘텐츠가 사라지지 않아야 하며, 애니메이션 없이도 정보 순서와 결론이 이해되어야 한다. [conf: high]
- 연속 이미지가 필요하면 Codex의 `$imagegen` built-in을 사용한다. 첫 프레임 이후에는 직전 승인 프레임을 reference로 삼고 subject, camera, environment, palette invariants를 유지한다. [conf: high]
- 연속 프레임은 3~6장을 기본으로 하고, 같은 크기와 비율로 저장해 HTML에서 유한 재생한다. PDF/reduced-motion에서는 가장 설명력 높은 한 프레임을 사용한다. [conf: high]
- HTML PT QA는 narrative, visual system, layout/typography, visual evidence, motion/continuity, interaction/accessibility, technical delivery의 100점 루브릭으로 한다. pass는 90점, 완성도 목표는 94점이며 P0가 있으면 점수와 무관하게 실패다. [conf: high]

## 10. Animation mode
- 사용자가 자동 재생·영상형 PT를 요청하면 HyperFrames 기반 `animation` mode를 사용한다. 여러 독립 슬라이드를 흉내 내기보다 한 개의 선형 master composition으로 장면을 연결한다. [conf: high]
- 애니메이션은 정지 화면의 완성도를 먼저 확보한 뒤 추가한다. CSS에 완성 end pose를 두고 composition별 paused GSAP timeline이 그 포즈로 들어오게 한다. 긴 film은 scene별 외부 sub-composition으로 나눈다. [conf: high]
- 장면은 build–breathe–resolve 리듬을 가지며, 한 film에서 2~3개의 전환 어휘만 쓴다. 중요 seam은 persistent carrier 또는 일치하는 exit/entry vector로 연결한다. [conf: high]
- 모션이 의미를 설명하지 않으면 넣지 않는다. wall clock, timer, unseeded random, hover/scroll 의존, 무한 repeat, imperative play처럼 seek 결과를 흔드는 동작은 금지한다. [conf: high]
- `hyperframes check --snapshots`, 전체 browser preview, 100점 animation rubric, P0=0을 통과하고 사용자가 preview를 승인하기 전에는 영상을 render하지 않는다. [conf: high]
