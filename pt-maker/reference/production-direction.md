# 제작 포맷 선택 — 필수 첫 질문

`$pt-maker ... 만들어줘` 요청을 받으면 다른 질문이나 작업보다 먼저 아래
질문 하나만 제시한다.

```text
어떤 포맷으로 만들까요?
1. 애니메이션 위주
2. 줄글 위주
3. 이미지 위주
```

## 선택 처리

- 사용자가 하나를 선택하면 `animation`, `text`, `image`로 기록한다.
- 사용자가 `그냥 진행`, `알아서`, `넘어가`, `상관없음`처럼 선택을 생략하면
  추가로 되묻지 않고 `image`를 기본값으로 기록한다.
- 사용자가 요청문에 포맷을 이미 적었어도 첫 응답은 예외 없이 위의 정확한
  3지선다 질문이다. 요청문만 보고 조용히 선택하거나 다른 질문부터 하지 않는다.
- 포맷이 정해지기 전에는 참고자료 질문, 웹 검색, 리서치, 개요 작성,
  `new_deck.py` 실행, 이미지 수집이나 생성을 시작하지 않는다.
- 이후 Grill Me 질문도 한 번에 하나씩만 한다.

## 1. 애니메이션 위주

- HyperFrames로만 제작한다. Reveal 전환 효과로 대체하지 않는다.
- `animation/index.html`, 로컬 `compositions/`, 로컬 `assets/`를 하나의
  완성 HTML 프로젝트로 만든다.
- 같은 composition에서 좌우 키·스페이스·터치로 넘기는 발표용 HTML을
  생성한다. 슬라이드에 들어올 때마다 해당 장면 애니메이션을 처음부터
  재생하고, 이전 방향으로 돌아와도 동일하게 재생해야 한다.
- 슬라이드 내부 build와 슬라이드 사이 transition을 따로 설계한다. 내부
  build는 장면 의미에 맞게 다양화하고, transition은 2~3개 family로
  제한하되 seam마다 결정적으로 바꾼다. 12장 이상이면 기본적으로
  `prism / curtain / aperture` 세 family를 모두 사용한다.
- `qa_animation_guard → lint → check --snapshots → preview → 발표용 HTML 생성
  → 발표용 HTML 양방향 검수`를 끝까지 수행한다.
- 완성 HTML 프로젝트와 발표용 HTML을 기본 완성본으로 납품한다.
- MP4/WebM/GIF는 사용자가 영상 파일을 명시 요청한 경우에만
  `사용자 preview 승인 → render export → 영상 QA`를 추가한다.
  임시 경로나 누락된 composition/asset을 참조하는 HTML은 완료본으로
  인정하지 않는다.
- `check`, `preview`, 그리고 명시 요청된 `render`는 관리형
  `--background`로 실행한다.
- 최종 검수 뒤 `stop --target all`을 실행하고 모든 managed job이
  `alive:false`인지 확인한다. HyperFrames Studio/preview를 남겨 두지 않는다.

## 2. 줄글 위주

- 제목과 글자가 화면의 주인공인 Reveal HTML/PDF를 만든다.
- 핵심 주장을 제목으로 세우고 본문은 읽는 순서가 분명한 문단·인용·목록으로
  구성한다. 이미지 수량을 억지로 늘리지 않는다.
- 줄글 위주도 텍스트 벽이나 동일한 제목+문단 박스 반복을 뜻하지 않는다.
  각 슬라이드에 `focal phrase / supporting layer / reading path`를 정하고,
  초점 문구가 크기·굵기·색·위치 중 하나 이상으로 본문보다 먼저 보이게 한다.
- oversized statement, split contrast/quote, stepped phrase, metric-led copy,
  editorial text grid 중 최소 3개 타이포 구성 family를 덱에 분산한다. 같은
  정렬과 블록 분포를 3장 연속 반복하지 않는다.
- 가독성 하한, 여백, 한 아이디어 한 슬라이드, overflow·orphan·footer
  collision P0 규칙을 그대로 적용한다.
- 필요한 도식이나 근거 이미지는 보조적으로 쓸 수 있지만 텍스트보다
  시각적 우선순위를 높이지 않는다.

## 3. 이미지 위주

- 덱 전체에 이미지 자산을 여러 장 반드시 확보한다.
- 텍스트가 있는 모든 주요 슬라이드에는 해당 문장을 직접 설명하거나
  증명하는 이미지가 적어도 한 장 있어야 한다.
- visual plan에 각 주요 문장의 `claim → image` 대응을 적고, 렌더 QA에서
  이미지가 인접 문장을 실제로 설명·증명하는지 확인한다.
- 같은 이미지를 반복하거나 무관한 장식 이미지로 수량만 채우지 않는다.
- 사용자 자산과 공식·공개 웹 자료를 먼저 찾고, 적합한 이미지가 부족하면
  `imagegen` 스킬의 built-in `image_gen`을 적극 사용한다.
- `image` 선택 또는 기본값 적용은 부족한 비주얼을 `imagegen`으로 보강하는
  데 대한 원칙적 동의다. 생성 직전에 예상 장수와 슬라이드별 목적을
  알리되 별도 승인 질문 때문에 작업을 멈추지 않는다.
- 생성 이미지는 사실 증거처럼 제시하지 않는다. 실존 인물·제품·사건·수치의
  증거는 공식·공개 자료를 사용하고 생성 자산은 일러스트임을 기록한다.
- 최종 자산은 덱의 `assets/`에 저장하고 출처 또는 생성 사실을
  `assets/CREDITS.txt`에 남긴다.
