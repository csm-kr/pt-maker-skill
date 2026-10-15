# Motion Graphics Grammar (paper-motion)

이 문서는 `motion-demo-video` 스킬(`csm-kr/motion-demo-video` `15446ac`, 원본 분석은 그 스킬의 `references/youtube-analysis.md`)에서 검증된 모션그래픽 문법을 pt-maker animation mode 용어와 계약으로 옮긴 것이다. 사용자가 `paper-motion` 스타일(종이 질감 모션그래픽 + 화자 캐릭터)을 고르면 [hyperframes-animation-mode.md](hyperframes-animation-mode.md), [motion-continuity.md](motion-continuity.md), [../assets/speaker-character/README.md](../assets/speaker-character/README.md)와 함께 읽는다.

우선순위는 `hyperframes-animation-mode.md` 계약 > 이 문서 > motion-demo-video 원문이다. 계약과 부딪히면 이 문서의 해소 방법을 따른다.

## 0. 범위와 가져오지 않는 것

- 산출물은 그대로 **사람이 넘기는 발표용 HTML**이다. 장면 하나 = composition 하나 = 클릭 한 번. MP4/WebM/GIF는 사용자가 명시 요청했을 때만 `hyperframes_mode.py render`로 만든다.
- 가져오지 않는 해커톤 전용 제약: 2:50 길이 제한, 영어 화면 텍스트·자막, Public YouTube 업로드, "기능은 실제 앱 녹화로만 증명" 규칙. 증거 규칙은 pt-maker 기존 규칙(생성 일러스트를 증거로 쓰지 않음, 출처 기록)을 따른다. 화면 언어는 사용자 언어(한국어)다.
- 가져오지 않는 제작 도구: 자체 렌더러(`engine/render.mjs`, `window.__seek`), 단일 master timeline, 음악·효과음 합성(`cues.mjs`, `score.py`). 발표 HTML은 소리 없이도 완결되어야 한다.
- 가져오지 않는 구현 습관: `document.fonts.ready` 뒤 DOM을 측정해 timeline을 짓기, `onUpdate`로 `textContent`를 바꾸는 카운트업, 화면 전체에 거는 `filter: blur`. 각각 결정성, 접근 가능한 텍스트 보존, live deck 성능 규칙과 충돌한다. 대체 방법은 아래 각 절에 있다.

## 1. 용어 대응표

| motion-demo-video | pt-maker animation mode | 기록 위치 |
|---|---|---|
| hero object | seam을 건너는 `carrier` (`carrier-match`) | `STORYBOARD.md` dominant visual, `motion-ledger.json` `seams[].carrier` |
| persistent frame | 모든 composition에 같은 좌표로 놓는 장면 틀(캡션 칩 등, 선택) | build-notes의 frame 좌표(xywh) |
| accent payoff | `--accent` 사용 시점 제한 + payoff 장면 1개 | `STORYBOARD.md` 한 줄 |
| timeline sheet `transition out` | seam의 handoff beat(exit pose → entry pose)와 기법 이름 | `motion-ledger.json` `seams[]` |
| kinetic typography | `text-write` signature build의 확장 | `STORYBOARD.md`, `motion-ledger.json` |
| `T` 상수표 | composition 스크립트 맨 위 절대 시각 상수 객체 | 각 `compositions/scene-*.html` |
| beat grid | 장면 내부 박자 격자(음악 없음) | build-notes |
| virtual camera `camTo`/`camAt` | composition 안 `.cam` 층 + 시간 함수 + GSAP modifiers | 해당 composition |

## 2. Hero object — 덱 전체를 관통하는 요소 하나

- 기획 단계에서 덱 전체를 끝까지 따라가는 요소 하나를 정한다. 주제 안에서 고른다. 예: 온톨로지 덱이면 개념을 뜻하는 점(노드) 하나가 클래스 → 관계 → 그래프로 자란다.
- 화자 캐릭터는 hero object가 아니다. paper-motion에서 화자는 도식 장면과 컷으로 번갈아 나오며 연결·반론·질문·CTA를 맡고, seam을 건너 의미를 운반하는 것은 개념 오브젝트다(`paper-motion-taste-profile.md` §6).
- 장면마다 hero object의 resolved pose(xywh·크기·색)를 기록하고 다음 장면의 t=0 포즈를 그것과 똑같이 둔다(**handoff pose**). 다음 장면에서는 등장 모션 없이 그 자리에서 출발한다.
- 마지막 장면에서 hero object는 결론 도식이나 결론 문장의 일부가 된다(원문: 점이 로고의 마침표가 됨).
- 모든 챕터 경계 seam에서 hero object가 화면에 있어야 한다.

HyperFrames 계약에 맞추는 법:

- 발표용 HTML 생성기는 `index.html`의 상위 track(`#carrier` 같은 parent-owned clip)을 옮기지 않는다. 그래서 paper-motion에서는 hero object를 **각 composition 안에 복제해서 그리고 handoff pose로 잇는다**. 각 composition timeline은 자기 복제본만 tween한다.
- hero object와 화자 캐릭터는 `.scene-content` 밖, composition root의 직계 자식으로 둔다. default 테마의 발표용 HTML은 재진입 때 `.scene-content`에 `scale 1.012 → 1`을 걸어 좌표가 미세하게 어긋나기 때문이다(`--theme paper`는 이 scale을 걸지 않는다).
- handoff pose 좌표는 `data-xywh`(0-1 비율)와 inline `left/top/width/height` px로 함께 적는다. 두 값이 렌더 결과와 맞는지 full-size 캡처로 확인한다.

## 3. Persistent frame — 장면이 바뀌어도 고정된 틀

- persistent frame은 선택이다. 레퍼런스에서 화자는 도식 장면과 컷으로 번갈아 나오므로 paper-motion은 화자를 고정 틀로 쓰지 않는다. 틀이 필요하면 캡션 칩(같은 자리, 문구만 교체) 하나만 둔다.
- 틀이 나오는 모든 composition에서 좌표를 같은 값으로 둔다(캡션 칩 xywh). 1px이라도 다르면 넘길 때 틀이 흔들려 보인다.
- 틀은 내용만 바꾼다. 틀 자체의 등장은 첫 장면, 퇴장은 마지막 장면에서만 한다.
- 발표용 HTML의 `#scene-hud`가 장 번호를 이미 보여주므로 composition 안에 `01 / 08` 같은 장 번호 틀을 또 만들지 않는다.
- 한계: default 테마의 슬라이드 트랙은 가로로 이동하므로 틀도 페이지와 함께 밀렸다가 같은 자리에 다시 놓인다. `--theme paper`의 `cut` seam과 HyperFrames 영상(track 0 하드 컷)에서는 같은 좌표의 틀이 그대로 고정돼 보인다.

## 4. Accent payoff — 강조색을 아꼈다가 한 번 터뜨리기

- `--accent`(기본 로즈 `#c73463`)는 payoff 장면 전까지 hero object의 작은 표식 하나를 넘지 않게 쓴다. eyebrow·kicker·밑줄 같은 반복 장식에는 `--ink`/`--muted`나 의미 색을 쓴다.
- payoff는 덱 전체에 한 번이다. 핵심 결론 장면에서 accent가 처음으로 화면을 차지하고(color flood, 포커스 링, 결론 단어), 그 뒤로는 같은 의미로 끝까지 유지한다. `STORYBOARD.md`에 `accent payoff: scene N`을 적는다.
- paper-motion에서 payoff는 덱당 한 번의 큰 색·밝기 사건(어둠→밝음 세계 전환, 흑백 속 단 하나의 컬러)이다. 레퍼런스처럼 반복해 쓰는 금색 붓터치는 '핵심 표시'라는 의미 색이라 payoff 예산에 넣지 않는다.
- `taste-profile.md`의 "알록달록하되 색은 의미를 가져야 한다"와 충돌하지 않는다. 의미 색(분류·관계·위험 등)은 처음부터 쓰는 팔레트이고, accent payoff는 브랜드 강조색 한 개의 **사용 시점**만 제한한다. 의미 색에 `--accent`와 같은 색을 배정하지 않는다.
- flood는 composition 안의 원형 요소를 `transform: scale`로 키워 만든다. 1920×1080 전체 `clip-path` 애니메이션이나 `width/height` tween은 쓰지 않는다.

## 5. 장면 간 연속 전환 — 사물이 시선을 넘겨준다

원칙: 장면 사이에 깜빡임, 흰/검은 화면, fade-to-black을 쓰지 않는다. 한 장면의 사물이 다음 장면으로 시선을 넘긴다. 원문에서 승패를 가른 기준이다.

paper-motion 레퍼런스는 대부분 하드컷으로 넘어가지만, 같은 사물이 같은 자리에 남아 시선이 끊기지 않는다. 그래서 paper-motion에서는 **match cut**(장면은 바뀌어도 같은 물체가 같은 위치에 있어 시선이 이어지는 컷)을 허용하고 기본 seam으로 쓴다. 금지 대상은 컷 자체가 아니라, 이어 주는 사물 없이 끊기는 컷과 깜빡임·플래시다.

### 충돌 해소: 두 층으로 나눈다

| 층 | 만드는 곳 | 규칙 |
|---|---|---|
| seam 전환(페이지 넘김) | `build_animated_presentation.py`. default 테마는 `prism` / `curtain` / `aperture`, `--theme paper`는 `cut`(기본, match cut) / `paper`(세계가 바뀔 때만, clip host에 `data-transition="paper"`) | 사람이 넘겼다는 신호다. seam별 결정적 배정, 역방향 동일 family 규칙을 유지한다. 12장 이상 덱의 prism/curtain/aperture 커버리지 규칙은 default 테마 계약이고, paper 테마는 `transitionContract`로 자기 family를 선언한다 |
| 시선 넘겨주기(handoff beat) | 장면 N의 마지막 resolve beat + 장면 N+1의 첫 beat | 아래 어휘표에서 seam마다 하나 고른다 |

- pt-maker의 "전환 family 2-3개" 규칙은 seam 전환 층에만 센다. 어휘표 기법은 슬라이드 내부 build 다양화 범주로 센다.
- exit beat: 장면 N의 마지막 0.3-0.6s에 hero object가 handoff pose로 간다. pt-maker는 장면이 읽을 수 있는 정지 포즈로 끝나야 하므로 handoff pose 자체가 읽히는 포즈여야 한다. 화면 밖으로 빠지거나 빈 화면으로 끝내지 않는다.
- entry beat: 장면 N+1의 t=0 포즈 = 장면 N의 handoff pose. 첫 0.2-0.6s 안에 변형을 시작한다. 발표용 HTML은 넘김 전환과 동시에 다음 timeline을 재생하므로 이 beat가 전환 중에 보인다.
- HyperFrames 영상에서는 track 0 경계가 composition 교체 하드 컷이지만, 양쪽 포즈가 같으면 보이지 않는 match cut이 된다.
- 생성기 default 테마의 흰 `fx-flare`, 네온 blade, 어두운 무대 배경은 원문의 "플래시 금지"와 종이 질감에 맞지 않는다. paper-motion은 이 FX가 없는 `--theme paper`로 발표용 HTML을 만든다.

### 전환 어휘

| 기법 | 무엇이 일어나나 | pt-maker 구현(composition 안) | ledger kind |
|---|---|---|---|
| 사물이 배경이 됨 | hero 점이 커져 그 색이 다음 장면 배경이 됨 | N 끝: 원형 요소 `scale` 확대 / N+1 t=0: 같은 색 배경에서 출발 | `carrier-match` |
| 사물이 도식이 됨 | 점이 늘어나 상자·링·노드가 됨 | 같은 요소의 `scaleX/scaleY` + `border-radius` 보간 | `carrier-match` |
| 모양 morph | 위치는 그대로, 모양만 바뀜 | 같은 자리에 겹친 두 모양의 opacity 교차 + scale | `carrier-match` |
| 수축 → 재조립 | 모든 것이 한 점으로 모였다가 다음 단어·도식으로 퍼짐 | 미리 정한 좌표표로 조각 배치, 절대 시각 stagger. 난수 배치 금지 | `carrier-match` |
| 모임 / 합침 | 흩어진 조각이 단어·도식으로 모임 | 위와 같음 | `carrier-match` |
| 매크로 줌 연속 | 카메라가 글자·노드에 붙었다가 전체로 빠짐 | §9 시간 함수 카메라 | `vector-match` |
| 푸시인 + dim | 중요한 하나로 들어가고 나머지는 흐려짐 | 카메라 + 나머지 `opacity .25`. blur는 작은 요소에만 | `vector-match` |
| 공유 요소 | 같은 카드가 목록에서 상세로 날아감 | N 끝 위치·크기 = N+1 시작 위치·크기 | `carrier-match` |
| 점 match cut | 작은 점으로 줌 → 벡터 점으로 교체 → 확대 → 다른 장면의 같은 점으로 수축 | 위 기법 조합 | `carrier-match` |
| color flood | 배경이 accent로 덮임 | accent payoff 장면에서 한 번만 | `carrier-match` |
| 고정 틀, 내용 교체 | 틀은 그대로, 안의 내용만 바뀜 | 화자 대사, 캡션 칩, 같은 자리 키워드 교체 | `carrier-match` |
| match cut | 장면은 바뀌어도 같은 사물이 같은 자리에 남음 | N 마지막 포즈 = N+1 t=0 포즈, paper 테마 seam은 `cut` | `carrier-match` |
| 모션 블러 휩 | 단어·화면이 옆으로 빠지고 다음이 들어옴 | dominant current 방향 `x` 이동 + 텍스트 요소에만 국소 blur | `vector-match` |

- 하드 컷은 (a) 0.3s 이하 컷이 이어지는 몽타주 안, (b) 의도된 강조 박자 위, (c) paper-motion의 match cut에서만 쓴다. pt-maker `hard-resolve`는 챕터 결론이 완전히 착지한 뒤에만 쓰고, 검은/흰 화면을 거치지 않는다.
- crossfade는 화면을 덮는 사물 아래에서만 쓴다(링이나 날아가는 카드가 덮는 동안 아래 내용을 바꿈). crossfade 자체를 전환으로 쓰지 않는다.
- `motion-ledger.json`의 각 seam에 기존 `exit_vector`/`entry_vector`/`carrier`와 함께 `technique`(위 표의 기법 이름)과 `handoff_pose`(xywh)를 적는다.

## 6. 의미를 연기하는 kinetic typography

- 단어의 뜻을 동작으로 보여준다. "흔들린다"는 흔들리고, "정렬"은 글자가 줄을 맞추고, "연결"은 두 단어 사이에 선이 그어지고, "분류"는 단어들이 상자 안으로 들어가고, "상속"은 위 단어의 색이 아래로 흘러내린다.
- 장면당 의미 동사 하나만 연기한다. 모든 단어를 움직이는 장식은 금지한다.
- 단어 단위 등장, 같은 자리 키워드 교체를 쓸 수 있다. 교체가 반복되면 간격을 약 20%씩 줄여 가속한다.

pt-maker 계약에 맞추는 법:

- 글자는 저작할 때 한 번 `<span class="w">`(단어) 또는 `<span class="ch">`(글자)로 감싸고 각 span의 transform/opacity만 tween한다. `textContent`를 시간에 따라 바꾸거나 `letter-spacing`·width를 tween하지 않는다.
- 키워드 교체는 모든 후보를 DOM에 겹쳐 두고 절대 시각에 opacity/transform만 바꾼다.
- 숫자 카운트업은 `textContent` 변경 대신 자릿수 띠(0-9 세로 strip)를 `translateY`로 굴린다. 최종 숫자는 DOM에 그대로 둔다.
- 흔들림·회전은 유한 keyframes로 만든다. `repeat`는 유한 숫자만 쓰고 진폭을 난수로 만들지 않는다.
- 사실·숫자·고유명사는 정자체(Pretendard)로 둔다. 손글씨체는 화자의 짧은 감탄·주석에만 쓴다(`taste-profile.md`). paper-motion은 손글씨체 대신 그려지는 붓터치 주석으로 손맛을 낸다(`paper-motion-taste-profile.md`).
- signature build 이름은 `text-write`로 기록한다.

## 7. Purpose over art

- 청중이 바로 이해해야 한다. 멋지지만 모호한 장면보다 단순하고 분명한 장면을 고른다.
- 주장 → 증명을 번갈아 둔다. 글자 장면의 주장 바로 뒤에 도식·예시가 그 주장을 증명한다(pt-maker assertion-evidence와 같은 원칙).
- 첫 장면은 청중 자신의 문제나 질문으로 연다.
- 화자 캐릭터는 이해를 돕는 장치다. 연결·반론·질문·CTA만 맡기고 도식 장면과 컷으로 번갈아 둔다. 장면의 핵심 주장은 제목과 도식에 둔다. 대사는 장면당 1-4줄이다.
- 모션을 빼도 설명력이 그대로면 그 모션은 뺀다(`motion-continuity.md` seam QA와 같은 기준).

## 8. Beat grid — 박자 격자

- 덱의 박자를 먼저 정한다. 기본은 0.6s(100 BPM, 30fps에서 18프레임)다. 음악은 쓰지 않으며 박자는 리듬 격자일 뿐이다.
- 장면 길이, 단어 교체, 착지는 박자 위에 둔다. 전환은 박자에 착지하도록 시작한다: `start = beat - duration`.
- 각 composition 스크립트 맨 위에 절대 시각 상수표를 둔다. 타이밍 수정은 상수 한 줄 편집이 되어야 하고, 앞 tween 길이에 이어 붙이는 상대 시각은 쓰지 않는다.

```js
const s3T = { title: .3, node: 1.2, link: 2.4, payoff: 3.6, end: 6 };
const scene3Tl = gsap.timeline({ paused: true });
scene3Tl.from("#s3-node", { scale: 0, duration: .5, ease: "back.out(1.8)" }, s3T.node);
```

- 상수 이름은 composition마다 접두어를 붙인다(`s3T`, `scene3Tl`). HyperFrames가 composition 스크립트를 같은 전역에서 실행해도 이름이 겹치지 않게 하기 위해서다.
- 화자 대사 구간이 곧 읽는 시간이다. 한국어는 1초에 약 6-7음절에 문장 끝 쉼을 더한다. `say()`의 기본 음절 간격은 0.13s다.
- 마지막 build 뒤에 최소 2박의 breathe를 둔다. composition timeline 길이 = host `data-duration`이며 박자의 정수배를 권장한다.

## 9. 시간만으로 평가되는 카메라 (camTo / camAt)

큰 도식(예: 온톨로지 그래프) 하나를 장면 안에서 확대·이동하며 설명할 때 쓴다. 장면마다 그림을 새로 그리는 대신 큰 종이 한 장 위를 카메라가 움직인다.

- composition root 직계 자식으로 `.cam` 층(예: 3840×2160 종이)을 두고 도식을 그 world 좌표에 배치한다. 화자 캐릭터와 캡션 칩은 `.cam` 밖에 둔다.
- 카메라 상태는 `{cx, cy, z}`다. 무대 중앙에 오는 world 점과, 무대 폭 1920px에 담기는 world 폭이다.
- 카메라는 이동 목록에서 시간 `t`만으로 계산한다. 각 이동은 이전 이동이 끝난 곳에서 출발하고, `z`는 로그 공간에서 보간해 줌 속도를 고르게 만든다.
- `onUpdate` 콜백에 기대지 않는다. 발표용 HTML은 `pause(0)`으로 장면을 리셋하는데 이때 콜백이 실행되지 않아 카메라가 이전 위치에 남는다. 대신 GSAP `modifiers`로 렌더할 때마다 시간에서 값을 계산한다.
- modifiers tween은 `immediateRender: false`로 두고, 생성 직후 `gsap.set`으로 t=0 포즈를 직접 적용한다. 생성 시 즉시 렌더에는 modifiers가 적용되지 않기 때문이다.

```css
.cam { position: absolute; left: 0; top: 0; width: 3840px; height: 2160px; transform-origin: 0 0; }
```

```js
const s4T = { push: 1.2, pull: 3.4, end: 6 };
const scene4Tl = gsap.timeline({ paused: true });
{ // 카메라 코드는 블록 안에 둬 다른 composition과 이름이 겹치지 않게 한다
  const moves = [];
  const camTo = (c, at, dur, ease = "power2.inOut") => moves.push({ at, dur, to: c, ease: gsap.parseEase(ease) });
  const camAt = (t) => {
    let cur = moves[0].to;
    for (const m of moves) {
      if (t < m.at) break;
      if (m.dur > 0 && t < m.at + m.dur) {
        const k = m.ease((t - m.at) / m.dur);
        return {
          cx: cur.cx + (m.to.cx - cur.cx) * k,
          cy: cur.cy + (m.to.cy - cur.cy) * k,
          z: Math.exp(Math.log(cur.z) + (Math.log(m.to.z) - Math.log(cur.z)) * k),
        };
      }
      cur = m.to;
    }
    return cur;
  };
  const pose = (t) => { const c = camAt(t), s = 1920 / c.z; return { x: 960 - c.cx * s, y: 540 - c.cy * s, s }; };
  camTo({ cx: 1920, cy: 1080, z: 3840 }, 0, 0);                         // 종이 전체
  camTo({ cx: 900, cy: 600, z: 1200 }, s4T.push, 1.5);                   // 노드로 푸시인
  camTo({ cx: 1920, cy: 1080, z: 3840 }, s4T.pull, 1.2, "power3.inOut"); // 다시 전체
  const p0 = pose(0);
  gsap.set("#s4-cam", { x: p0.x, y: p0.y, scaleX: p0.s, scaleY: p0.s });
  const D = s4T.end; // tween 원시값 = 장면 로컬 시각(0→D, ease none)
  scene4Tl.fromTo("#s4-cam", { x: 0, y: 0, scaleX: 0, scaleY: 0 }, {
    x: D, y: D, scaleX: D, scaleY: D, duration: D, ease: "none", immediateRender: false,
    modifiers: {
      x: (v) => pose(parseFloat(v)).x + "px",
      y: (v) => pose(parseFloat(v)).y + "px",
      scaleX: (v) => pose(parseFloat(v)).s,
      scaleY: (v) => pose(parseFloat(v)).s,
    },
  }, 0);
}
window.__timelines["scene-4"] = scene4Tl;
```

- 이 패턴은 headless Chrome + GSAP 3.14.2에서 정방향 seek, 섞은 순서 seek, `restart()` 뒤 seek 모두 `camAt(t)`과 같은 transform이 나오는 것을 확인했다.
- 카메라 요소를 다른 tween으로 동시에 건드리지 않는다. 카메라 목록은 장면 상수표의 시각으로만 만든다.
- 래스터 이미지는 원본 픽셀의 약 1.5배 이상 확대하면 흐려진다. 확대할 이미지는 2배 해상도로 준비하거나 벡터 복제본으로 바꾼다. paper-motion 도식은 SVG/HTML 벡터를 기본으로 한다.
- 카메라 프레임이 화자 캐릭터·말풍선 영역을 덮지 않도록 world 좌표의 목표 지점을 정한다.

## 10. 종이 질감 구현 제약

구체적인 색·질감 취향은 `paper-motion-taste-profile.md`가 정한다. 여기서는 결정성과 성능 제약만 정한다.

- 종이 바탕(모눈, 결, 얼룩)은 정적 배경이다. CSS gradient나 정적 이미지/인라인 SVG 패턴으로 만들고 애니메이션하지 않는다. `feTurbulence` 같은 SVG 필터를 전체 화면에 실시간으로 걸지 않는다.
- 개념 스티커는 그림자 없이 흰 다이컷 외곽선(blur 0인 `drop-shadow` 네 방향)으로, 찢긴 사진 카드만 부드러운 드롭 섀도로 띄운다. 둘 다 정적 요소에만 건다.
- 오린 종이 조각의 움직임은 transform(이동·회전·scale)과 opacity만 쓴다. 기울기 흔들림은 유한 keyframes로 만든다.
- Claude Code처럼 이미지 생성 도구가 없는 환경에서는 캐릭터·일러스트·질감을 SVG/CSS로 그린다. 화자 캐릭터는 환경과 관계없이 결정적으로 움직이도록 코드로 그린 SVG(`assets/speaker-character/`)를 기본으로 한다.

## 11. paper-motion 체크리스트

- [ ] hero object 하나를 정했고, 모든 챕터 seam의 handoff pose(xywh)를 기록했다.
- [ ] persistent frame(캡션 칩 등)을 쓴다면 좌표가 모든 composition에서 같다.
- [ ] accent payoff 장면이 하나이고, 그 전에는 `--accent`를 아꼈다.
- [ ] 모든 seam에 기법 이름과 carrier가 있고, 깜빡임·흰/검은 화면이 없다.
- [ ] 장면당 의미 동사 kinetic typography는 하나 이하이며 텍스트를 변형하지 않는다.
- [ ] 각 composition에 절대 시각 상수표가 있고 박자 격자를 따른다.
- [ ] 카메라는 modifiers 패턴을 쓰고 섞은 순서 seek로 확인했다.
- [ ] 화자 캐릭터 규칙(장면별 `sN-` 접두어와 고유 id, `.scene-content` 밖, 즉시 포즈 교체, 무한 루프 없음)을 지켰다.
- [ ] QA는 기존 순서(`qa_animation_guard` → lint → `check --snapshots` → 발표용 HTML 생성(`--theme paper`) → `qa_animated_presentation`)를 따르고, 각 seam 앞뒤 0.15s 프레임에서 hero object가 화면에 있는지 확인했다.
