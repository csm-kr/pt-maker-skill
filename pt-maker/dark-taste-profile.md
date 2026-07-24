---
version: 3
updated: 2026-07-09
profile_id: dark-theme-accent
---

# Dark Theme Taste Profile

어두운 테마를 쓸 때 참고하는 별도 취향 프로필이다. 기본 원칙은 `taste-profile.md`를 따르고, 이 파일은 dark slide에서 색, 대비, 밀도, 리듬을 어떻게 번역할지 정의한다.

## 0. 기본 관계
- dark 프로필은 일반 취향을 대체하지 않는다. `one takeaway per slide`, 텍스트 안정성, 시각 증거, 구조화된 밀도, 최종 PDF QA는 그대로 적용한다. [conf: high]
- dark 테마에서도 "다이나믹하지만 구조화된 레이아웃"을 선호한다. 어둡다는 이유로 단순히 큰 문장만 놓는 빈 슬라이드를 만들지 않는다. [conf: high]
- dark slide는 cover, closing, chapter opener, 강한 전환, 핵심 선언, 기술/AI/미래감이 필요한 구간에 특히 잘 맞는다. 전체 덱 dark는 사용자가 요청하거나 주제상 명확히 필요할 때만 한다. [conf: high]

## 1. 팔레트와 대비
- 배경은 near-black 또는 charcoal을 기본으로 하되, 검은 단색만 쓰지 말고 아주 은은한 grid/noise/paper texture를 넣어 깊이를 만든다. [conf: high]
- 제목은 white 또는 warm-white, 본문은 soft-gray를 쓰되, PDF에서 대비가 약하면 즉시 수정한다. [conf: high]
- 알록달록한 취향은 dark에서도 유지한다. coral, yellow, teal, blue, lime 같은 색을 3-5개까지 쓸 수 있지만, 각 색은 의미가 있어야 한다. [conf: high]
- coral은 강한 주장/위험/핵심 강조, yellow는 발견/주의, teal/blue는 구조/기술/데이터, lime은 기회/성장처럼 역할을 나누는 방식을 선호한다. [conf: med]
- 색은 많아도 hierarchy를 망치면 안 된다. 모든 요소가 빛나면 아무것도 강조되지 않는다. [conf: high]

## 2. 레이아웃과 밀도
- dark slide도 꽉 차게 만들 수 있다. 단, 풍성함은 배경 패턴, 얇은 grid, 작은 메모, diagram line, color chip, 데이터 조각을 구조적으로 배치해서 만든다. [conf: high]
- 주요 메시지는 optical center에 둔다. 하단에 얕은 카드만 늘어놓거나, 화면 중앙을 비워 둔 채 장식만 채우지 않는다. [conf: high]
- opening과 closing은 같은 dark visual language를 공유하되 배치를 mirror처럼 바꿔 의도적인 관계를 만든다. [conf: high]
- dark 구간이 여러 장이면 레이아웃을 바꾼다: full-bleed statement, split visual, diagram-led, dashboard, timeline, grid matrix를 섞는다. [conf: high]
- 박스 안 텍스트, 라벨, 아이콘, source, footer가 조금이라도 닿거나 겹치면 P0로 본다. dark에서는 작은 충돌이 더 눈에 띈다. [conf: high]

## 3. 타이포그래피
- dark slide의 headline은 크고 선명하게 잡되, 강조 단어는 1-2개만 color accent로 처리한다. [conf: high]
- 본문은 작게 만들지 않는다. 1280x720 기준 body/bullet은 보통 28-30px, hard floor 26px, line-height는 1.56 이상을 유지한다. [conf: high]
- soft-gray 본문이 배경에 묻히면 실패다. PDF/contact sheet에서 멀리 봐도 읽혀야 한다. [conf: high]
- 정확한 숫자, 연도, 출처, 고유명사는 Pretendard로 둔다. 손글씨는 dark에서도 짧은 메모나 화살표 주석에만 쓴다. [conf: high]
- 손글씨 같은 글씨체는 dark에서도 포인트로 사용한다. chalk/neon pencil 느낌의 짧은 메모, 표시선, 동그라미, 화살표 주석이 잘 맞는다. [conf: high]
- 단, 데이터나 본문보다 위계가 높아지면 안 된다. 손글씨 포인트는 "사람이 덧붙인 생각"처럼 보여야 하고, 핵심 정보의 가독성을 대신하면 안 된다. [conf: high]

## 4. 시각자료와 도식
- dark 주요 슬라이드도 텍스트만 두지 않는다. 사진, 스크린샷, SVG 도식, 타임라인, 비교 matrix, 데이터 조각 중 하나가 메시지를 받쳐야 한다. [conf: high]
- 사진 위 dark overlay를 쓸 때 얼굴, 제품, 지도, 핵심 피사체가 가려지면 실패다. overlay는 텍스트 가독성을 올리는 용도이지 피사체를 묻는 용도가 아니다. [conf: high]
- dark diagram은 선과 라벨의 대비를 충분히 확보한다. 화살표가 떠 있거나, 라벨이 도형 밖으로 밀리거나, 선이 텍스트를 가로지르면 P0다. [conf: high]
- 실제 지도/장소/경로는 dark 스타일로 직접 손그림 지도를 만들지 않는다. sourced map base 위에 dark overlay와 색상 라벨을 얹는다. [conf: high]

## 5. 외부 원칙의 dark 번역
- assertion-evidence 구조는 dark에서도 유지한다. 큰 제목은 주장, 아래 시각자료는 그 주장을 증명해야 한다. [conf: high]
- one takeaway per slide를 지킨다. dark slide가 멋있어도 두 메시지를 동시에 말하면 실패다. [conf: high]
- NN/g식 hierarchy 원칙을 강하게 적용한다. color, contrast, scale, grouping이 시선 순서를 만들어야 하며, 장식은 그 순서를 방해하면 제거한다. [conf: high]
- Duarte식 purposeful color를 따른다. dark에서 화려한 accent는 장식이 아니라 의미 부호여야 한다. [conf: high]

## 6. QA 규칙
- dark cover와 closing은 contact sheet에서 가장 먼저 눈에 들어와야 한다. 흐릿하거나 washed-out이면 배경, panel, headline contrast를 수정한다. [conf: high]
- dark slide만 header/footer 좌표가 흔들리면 실패다. 밝은 슬라이드와 같은 deck system 안에 있어야 한다. [conf: high]
- PDF에서 low-contrast gray, 얇은 grid, 작은 source가 사라지면 수정한다. HTML에서 보이는 것으로 충분하지 않다. [conf: high]
- P0: 텍스트 겹침/잘림/낮은 대비/footer 충돌/핵심 피사체 가림/도식 라벨 충돌. [conf: high]
- P2: dark slide가 너무 많아 전체 덱 리듬이 무거워지면 밝은 정보 슬라이드를 사이에 넣어 호흡을 만든다. [conf: med]

## 7. 안티 취향
- 검은 배경에 흰 문장만 크게 올린 빈 슬라이드. [conf: high]
- dark blue/slate 계열만 반복되는 단조로운 팔레트. [conf: high]
- neon accent가 많아 모든 요소가 동등하게 튀는 화면. [conf: high]
- 배경 texture가 headline 가독성을 해치는 화면. [conf: high]
- 사진을 어둡게 덮어 피사체가 안 보이는 hero. [conf: high]
