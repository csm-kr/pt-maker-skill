# HTML PT Quality Rubric

총점 100점. P0가 하나라도 있으면 점수와 무관하게 fail이다. pass 기준은 90점, 완성도 목표는 94점 이상이다.

| 영역 | 배점 | 만점 기준 |
|---|---:|---|
| Narrative & audience fit | 18 | 핵심 메시지·청중·CTA가 선명하고, 주장형 제목과 한 장 한 아이디어가 지켜진다. |
| Visual system & art direction | 14 | 토큰·타입·공간·레이어가 일관되고 lazy default가 없다. |
| Layout & typography | 18 | 1280×720에서 계층, 안전 여백, 한글 줄바꿈, 광학 정렬이 안정적이다. |
| Visual evidence & media | 14 | 모든 핵심 주장이 관련 시각 근거와 연결되고 피사체·출처가 보존된다. |
| Motion & continuity | 14 | 모션에 목적이 있고, 전환 어휘와 vector seam이 일관되며 정지 구간이 있다. |
| Interaction & accessibility | 10 | 탐색·fragment·분기·notes가 예측 가능하고 키보드/reduced-motion/대체텍스트가 작동한다. |
| Technical delivery | 12 | HTML guard, media guard, PDF/contact sheet, 브라우저·print 상태, 파일 경로가 모두 검증됐다. |

## P0 hard fail

- 잘린 텍스트, 겹침, 깨진 한글, 안전 영역/푸터 충돌.
- 핵심 인물·제품·로고·지도 영역이 잘린 이미지.
- 근거 없는 수치, 사실처럼 제시된 생성 이미지, 출처 누락.
- 슬라이드 주장과 무관한 장식 이미지.
- 핵심 인터랙션이 키보드로 접근 불가하거나 PDF에서 결론이 사라짐.
- reduced-motion에서 콘텐츠가 숨겨짐.
- 무한 애니메이션, 비결정적 난수/현재시각/네트워크 응답에 의존하는 핵심 장면.
- 연속 이미지에서 피사체 정체성·카메라 축·배경 구조가 눈에 띄게 튐.
- transition seam의 진행 방향이 이유 없이 반전되거나 흰 화면 flash가 발생.
- HTML guard 또는 media guard의 P0가 남아 있음.
- PDF bleed, 순서 오류, 빈 페이지, 로딩되지 않은 자산.

## P2 polish

- 주장 제목을 더 짧고 강하게 만들 수 있음.
- 모션 타이밍·stagger·정지 구간을 다듬을 수 있음.
- 장면 깊이, 엣지 앵커, 비대칭 구도를 더 강화할 수 있음.
- 캡션, 출처, 발표자 노트를 더 간결하게 만들 수 있음.
- 반복 레이아웃이나 transition을 한 번 줄일 수 있음.

## 채점 규칙

`qa_ledger.json`의 `rubric`에 각 영역 점수와 짧은 근거를 기록한다.

```json
{
  "rubric": {
    "narrative_audience": {"score": 17, "max": 18, "notes": "결론형 제목과 CTA 확인"},
    "visual_system": {"score": 13, "max": 14, "notes": "토큰/레이어 일관"},
    "layout_typography": {"score": 17, "max": 18, "notes": "full-size 검수"},
    "visual_evidence": {"score": 13, "max": 14, "notes": "주요 주장마다 시각 근거"},
    "motion_continuity": {"score": 13, "max": 14, "notes": "seam ledger 검수"},
    "interaction_accessibility": {"score": 9, "max": 10, "notes": "키보드/reduced-motion"},
    "technical_delivery": {"score": 12, "max": 12, "notes": "guard/export pass"}
  }
}
```

영역 합계가 최상위 `score`와 정확히 같아야 한다. 렌더를 보지 않고 추정 점수를 쓰지 않는다.
