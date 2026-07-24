# HTML Presentation Craft

이 문서는 pt-maker가 정적인 “웹 페이지 모음”이 아니라 발표용 장면 시스템을 만들기 위한 기준이다. HyperFrames의 HTML-native composition, deterministic rendering, slideshow, creative-direction 원칙을 PT 문맥에 맞게 재구성했다.

참조 기준:

- Repository: `heygen-com/hyperframes`
- Reviewed commit: `688500f2d6bbe28987fd414c65a977b4eb337821`
- License: Apache-2.0
- Docs: <https://hyperframes.heygen.com/>
- Showcase: <https://hyperframes.heygen.com/showcase>

코드나 패키지를 직접 복제하지 않는다. 아래 원칙만 pt-maker의 Reveal.js 기반 HTML 덱에 적용한다.

## 1. 장면 계약

- 캔버스는 `1280 × 720`, 16:9로 고정한다.
- 모든 슬라이드는 `background → midground → foreground → overlay`의 레이어로 생각한다.
- 주요 콘텐츠는 전체 폭·높이의 6% 이상을 안전 여백으로 둔다.
- 스크린과 PDF는 같은 최종 상태를 보여야 한다. print 모드에서는 움직이는 요소를 명시적인 정지 포즈로 고정한다.
- 런타임에 네트워크 응답, 현재 시각, 비결정적 난수, 스크롤/hover 상태에 의존해 핵심 장면을 만들지 않는다.
- 애니메이션이 없어도 메시지가 완전해야 한다. 모션은 이해 순서와 전환 의미를 강화하는 층이다.

## 2. 슬라이드 문장 규칙

- 제목은 주제명이 아니라 결론형 주장으로 쓴다.
  - 약함: `시장 현황`
  - 강함: `수요는 늘었지만 고객은 여전히 첫 결제에서 이탈한다`
- 한 슬라이드에는 주장 하나와 그 주장을 증명하는 주 시각물 하나만 둔다.
- 발표자가 말해야만 이해되는 핵심 수치는 슬라이드에 직접 쓴다.
- 수식과 시장규모는 결과부터 쓰지 말고 `단위 × 수량 × 빈도`의 bottom-up 구조를 보여준다.
- 텍스트만 두 장 연속되면 한 장 이상을 차트, 지도, 흐름도, 실제 화면, 사진, 승인된 AI 일러스트로 바꾼다.

## 3. 시각 시스템

- 덱 시작 전에 `background`, `surface`, `text`, `muted`, `accent`, `line` 토큰을 잠근다.
- 타입 스케일은 역할 기반으로 정의한다. 표지/장문장, 주장 제목, 본문, 캡션의 크기 차이가 즉시 보여야 한다.
- 그림자보다 테두리, 면 분리, 간격을 우선한다.
- 배경·중경·전경 중 적어도 두 층을 쓰되, 모든 슬라이드가 카드 격자로 보이지 않게 한다.
- 한 덱에 3~4개의 레이아웃 패밀리를 쓴다: split, full-bleed visual, timeline/flow, statement, comparison 등.
- lazy default를 점검한다: 습관적 보라 그라데이션, 모든 요소 중앙 정렬, 동일 카드 반복, 장식용 글로우, 의미 없는 유리 효과.

## 4. HTML로 추가할 가치가 있는 기능

다음은 발표 목적이 있을 때만 사용한다.

- `fragment`: 설명 순서, 단계 공개, 정답 공개.
- `data-target-slide`: 부록/드릴다운으로 이동하는 분기 버튼.
- speaker notes: 발표자 메모. 핵심 출처나 전환 멘트를 포함한다.
- image sequence: 한 피사체의 상태 변화, 프로세스, 시간 흐름.
- live chart/filter: 청중 질문에 따라 수치를 바꿔야 할 때.
- media controls: 데모 영상이 주장 자체의 근거일 때.

인터랙션이 PDF에 사라져도 본문과 정지 포즈만으로 핵심 결론이 유지되어야 한다.

## 5. 모션 시스템

- 한 덱의 전환 어휘는 2~3개로 제한한다.
- 입장은 보통 0.45~0.65초, 퇴장은 0.15~0.3초로 짧게 한다.
- 한 슬라이드 안에서는 `build → breathe → resolve` 리듬을 만든다.
- 정보 계층에 따라 제목 → 근거 → 결론 순으로 움직인다.
- 반복 wobble, pulse, 떠다니기는 사용하지 않는다. 움직임은 진행, 원인, 상태 변화, 강조 중 하나를 설명해야 한다.
- transform과 opacity를 우선한다. 레이아웃을 계속 다시 계산하는 top/left/width 애니메이션은 피한다.
- `prefers-reduced-motion`에서는 즉시 최종 포즈를 보여준다.

## 6. 발표자·탐색 경험

- 화살표, 스페이스, 터치로 다음 상태가 예측 가능해야 한다.
- 클릭 가능한 요소는 버튼 역할, 키보드 포커스, 명확한 레이블을 가져야 한다.
- 분기 이동 뒤 원래 흐름으로 돌아갈 수 있어야 한다.
- 현재 슬라이드 번호와 전체 장수를 제공한다.
- 슬라이드 이탈 시 재생 중인 video/audio/image sequence를 멈춘다.

## 7. 완성 조건

- 자동 guard에서 P0가 0이다.
- 브라우저 1280×720과 실제 프레젠테이션 창에서 모든 슬라이드를 확인했다.
- reduced-motion과 print/PDF 정지 포즈를 확인했다.
- 모션이 있는 모든 seam을 들어가기 직전/직후 캡처로 비교했다.
- HTML quality rubric 90점 이상이며, 목표 점수는 94점이다.
- PDF/contact sheet와 full-size 필수 페이지를 확인했다.
