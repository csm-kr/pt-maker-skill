# 제품 판단 (product judgment)

> 슬라이드를 짜기 **전에**, "이 제품/주장이 애초에 맞는가"를 한 블록으로 정리하는 단계.
> 제품·AI 기능을 파는 덱에서만 쓴다. 단순 정보 전달 덱이면 건너뛴다.
> 덱 craft(브랜드 토큰·빌드·QA)는 여기 없다 — [presentation-craft.md](presentation-craft.md)와 SKILL.md를 본다.

핵심 믿음:

> 제품 디자인은 기능을 예쁘게 배열하는 게 아니라, **특정 유저가 이해·신뢰·행동하는 순간**을 설계하는 것이다.

## 진단 렌즈

기획 단계에서 이 렌즈로 한 번 훑는다. 중립적·일반론 답은 금지 — 직설적으로.

1. **유저 순간** — 데모그래픽("개발자들")이 아니라 **긴장의 순간**으로 못 박는다.
   - ❌ AI 도구를 쓰는 개발자
   - ✅ AI 에이전트에 작업을 맡긴 뒤, 그 결과를 믿어도 되는지 판단해야 하는 개발자
2. **king action** — 제품에 지배적 행동 1개. 모든 버튼이 동등하면 척추가 없는 것. 위계를 이 행동에 맞춘다.
3. **first-screen 3초** — 첫 화면이 답해야 하는 것: 이게 뭔가 / 왜 신경 써야 하나 / 뭐부터 하나 / 왜 대안 말고 이거 / 믿을 수 있나. 기능 나열이면 **유저 결과**로 다시 쓴다.
4. **empty state = 온보딩.** "아직 없음"이 아니라 첫 행동을 유도.
5. **failure state = 신뢰** (특히 AI). 뭐가 실패했나 / 왜 / 다음에 뭘 / 이 출력 써도 안전한가.
6. **반복 루프** — `input → action/AI → verify → saved memory/assets → better next run`. AI 제품은 이 루프가 진짜 해자.
7. **AI 특이점** — 이 제품에서만 경험되고, 선택 이유가 되는 **제품 특화** AI 능력.
   - ❌ 자동 요약 / 추천 / 텍스트 생성 / 시간 절약 (generic slop)
   - ✅ 이 제품이 프로젝트 상태·테스트 로그·과거 결정을 보기 때문에, AI 코딩 결과를 믿어도 되는지 판단한다 — 코드를 더 뱉는 게 아니라.

## 출력 — 제품 판단 블록

기획 합의 전에 이 블록을 채운다(슬라이드 개요로 넘어가기 전 게이트):

```text
Product thesis:
Target moment:
King action:
AI 특이점:
Trust mechanism:
Repeated-use loop:
Main risk:
What to remove:
```

채운 블록 → [presentation-craft.md](presentation-craft.md)의 스토리 아크·슬라이드 개요로 태운다. 제목은 라벨이 아니라 **주장**, 슬라이드마다 약속한 비주얼을 실제로 그린다(같은 문서 §2·§4).

## 안티패턴

- generic AI value prop → 제품 맥락·데이터·워크플로·기억에 묶어 다시 쓴다.
- feature soup → king action 하나 고르고 나머지는 강등.
- 예쁜데 신뢰 안 됨 → 로그·스샷·수치·before/after·failure state로 증명.
- 타겟을 "개발자/팀"으로 → 정확한 순간과 불안으로.
