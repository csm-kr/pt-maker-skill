# Speaker character (paper-motion owl)

paper-motion 스타일의 화자 캐릭터인 독창적인 부엉이다. 이미지 생성 없이 코드로 그린 SVG라서 같은 시각이면 언제나 같은 그림이 나오고(결정적), 포즈 교체가 쉽다. 그림 문법(밝은 회색 몸, 균일한 검은 외곽선, 둥근 콩 모양, 망점 깃, 노란 소품 하나)은 레퍼런스 분석을 따르되 레퍼런스 채널의 고슴도치 마스코트는 복제하지 않는다. 운용 원칙은 [../../paper-motion-taste-profile.md](../../paper-motion-taste-profile.md) §6, 모션 문법은 [../../reference/motion-graphics-grammar.md](../../reference/motion-graphics-grammar.md)를 따른다.

## 파일

| 파일 | 용도 | 넣는 곳 |
|---|---|---|
| `speaker.css` | 생김새·포즈 표시·대사 스타일, `--spk-*` 토큰 | `animation/index.html`의 `<style>`에 한 번 |
| `speaker-markup.html` | 부엉이 SVG(5포즈) + 대사 뼈대 | 캐릭터가 나오는 composition마다 |
| `speaker.js` | GSAP 헬퍼 `PtSpeaker` | 그 composition의 inline `<script>` 맨 앞 |
| `demo/` | 3장면 paper-motion 예제(연회색 세계·찢긴 종이 카드·흰 외곽선 스티커·붓터치·match cut·종이 밀기·부엉이) | 참고용. 덱에 복사하지 않는다 |

`build_animated_presentation.py`는 `index.html`의 `<style>`과 composition의 inline `<script>`만 발표용 HTML로 옮긴다. 그래서 CSS·JS를 `<link>`/`<script src>`로 따로 불러오지 않고 붙여 넣는다. `speaker.js`는 여러 composition에 중복으로 들어가도 첫 정의만 쓰인다.

## 사용 순서

1. `speaker.css`를 `animation/index.html`의 `<style>` 끝에 붙인다.
2. `speaker-markup.html`의 `.spk` 블록을 composition root(`data-composition-id` 요소)의 **직계 자식**으로 붙인다. `.scene-content` 안에 넣지 않는다.
3. 블록 안의 `sN-`을 장면 접두어(`s3-` 등)로 **모두** 바꾼다. root id, 망점 `pattern` id, `fill="url(#...)"` 참조가 함께 바뀐다. 장면마다 id가 달라야 발표용 HTML 생성이 통과한다.
4. `data-pose`에 정지 포즈(인쇄·첫 진입 전에 보일 포즈, 보통 장면의 마지막 포즈)를 적는다. 대사 `<p class="spk-bubble">`은 줄 수만큼 두고 정지 포즈에 남길 한 줄에만 `is-rest`를 붙인다.
5. composition `<script>` 맨 앞에 `speaker.js`를 붙이고, 장면 timeline을 만든 뒤 호출한다.

```js
const s3T = { narrate: .2, object: 2.0, think: 4.0, cta: 5.8, end: 7.5 };
const scene3Tl = gsap.timeline({ paused: true });
PtSpeaker.attach(scene3Tl, "#s3-speaker", { start: "side" })
  .say(0, s3T.narrate, s3T.object - .1)
  .pose("o", s3T.object)
  .say(1, s3T.object, s3T.think - .1)
  .pose("think", s3T.think)
  .say(2, s3T.think, s3T.cta - .1)
  .pose("wave", s3T.cta)
  .say(3, s3T.cta, s3T.end - .2, { keep: true });
scene3Tl.set({}, {}, s3T.end);
window.__timelines["scene-3"] = scene3Tl;
```

## API

모든 시각은 그 composition 기준 절대 초다. 호출은 timeline에 변화를 추가할 뿐 아무것도 재생하지 않는다.

| 호출 | 하는 일 |
|---|---|
| `PtSpeaker.attach(tl, rootSelector, { start, tween, lipSync })` | 부품을 찾고 t=0 출발 포즈를 등록한다. `start`가 없으면 `data-pose`. `tween`·`lipSync`는 기본 `false` |
| `.pose(name, at)` | `smile`(기본 진행) / `o`(놀람·반론) / `wave`(질문·CTA) / `side`(내레이션) / `think`(생각)로 **즉시** 교체한다. `tween: true`면 0.12초 교차 |
| `.say(index, at, until, { keep, lipSync, syllable })` | `index`번째 대사를 `at`~`until` 동안 즉시 보인다. `keep`이면 `until` 뒤에도 남는다. `lipSync`가 켜져 있으면 음절 수만큼 부리를 움직이고 `until` 전에 닫는다(한글은 모음에 따라 벌림 정도가 다름) |
| `.blink([t1, t2, ...])` | 지정한 시각마다 한 번 깜빡인다. 부르지 않으면 깜빡이지 않는다 |

paper-motion 기본값은 레퍼런스와 같이 **트윈 없는 즉시 교체, 깜빡임·립싱크 없음**이다. 살아 있는 느낌은 배경(우주 먼지 등)이 준다.

## 대사 스타일

- `spk--plain`(기본 마크업): 머리 위 굵은 글자. 우주 세계에서는 `--spk-bubble-ink:#fff`를 준다. 반론은 `“ 말 ”`처럼 따옴표 안쪽에 공백을 둔다.
- `spk--plain`을 빼면 상자 말풍선이 된다. 방향은 `spk--bubble-left`(기본) / `spk--bubble-right`.
- `spk--flip`: 좌우 반전. 이야기 속 인물과 마주 볼 때만 쓴다.
- 대사가 장면의 핵심 주장을 대신하지 않는다. 장면당 1-4줄, 한 줄에 포즈 하나. 줄바꿈은 pt-maker 텍스트 규칙(짧은 꼬리 줄 금지)을 따른다.

## 규칙

- 무한 반복, `setTimeout`/`setInterval`, `Date.now`/`performance.now`, `Math.random`, `.play()`를 쓰지 않는다.
- 위치는 `--spk-x`/`--spk-y`/`--spk-w`(1920×1080 프레임 px)로 정한다. 헬퍼는 DOM 크기를 측정하지 않는다.
- 캐릭터는 도식과 컷으로 번갈아 나온다. 도식 장면에 상주하거나 도식을 가리키게 두지 않는다.
- `say(until)`이 장면 길이를 넘지 않게 한다.

## 생김새 파라미터

`.spk`에 inline style이나 덱 CSS로 덮어쓴다.

| 토큰 | 기본값 | 의미 |
|---|---|---|
| `--spk-x`, `--spk-y` | 없음(필수) | 프레임 기준 좌상단 px |
| `--spk-w` | `300px` | 폭. 높이는 200:240 비율 |
| `--spk-body` / `--spk-belly` | `#e0e0e0` / `#f7f7f7` | 몸 / 얼굴 원반·연필 나무 |
| `--spk-ink` | `#111111` | 외곽선·눈·부리 |
| `--spk-cheek` | `#7a2a20` | 벌린 입 안쪽 |
| `--spk-tuft` / `--spk-tuft-bg` | `#222222` / `#7a7a7a` | 망점 점 / 바탕(깃·날개) |
| `--spk-prop` | `#e6d86c` | 노란 연필(캐릭터의 유일한 색) |
| `--spk-cut-shadow` | `rgba(17,17,17,.14)` | 상자 말풍선 그림자 |
| `--spk-bubble-bg` / `--spk-bubble-ink` | `#ffffff` / `#111111` | 대사 바탕 / 글자 |
| `--spk-bubble-w` / `--spk-bubble-size` | `760px` / `44px` | 대사 최대 폭 / 글자 크기 |

## 데모 확인

```bash
python3 scripts/qa_animation_guard.py assets/speaker-character/demo/index.html
python3 scripts/build_animated_presentation.py assets/speaker-character/demo --theme paper -o /tmp/speaker-demo.html
python3 scripts/qa_animated_presentation.py /tmp/speaker-demo.html
```

`demo/`의 CSS·JS·SVG는 위 원본 파일을 그대로 복사한 것이다(SVG는 `sN-`만 장면 접두어로 바뀜). 원본을 고치면 데모도 같이 고친다. `scripts/test_speaker_character.py`가 일치 여부를 검사한다.
