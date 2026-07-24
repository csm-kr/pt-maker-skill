# Motion & Image Continuity

## 1. 먼저 “모션 법칙”을 정한다

덱 전체에서 다음을 한 문장으로 기록한다.

```text
dominant current: 화면 요소는 주로 왼쪽에서 오른쪽으로 진행한다.
transition vocabulary: rise reveal / carrier match / hard resolve
stillness: 핵심 수치 전후 0.4~0.7초
```

- dominant current는 기본 진행 방향이다. 역방향은 반전, 문제, 되돌림처럼 의미가 있을 때만 쓴다.
- 전환은 2~3종으로 제한한다.
- 속도, 방향, 피사체의 크기 변화가 슬라이드 경계에서 갑자기 바뀌지 않게 한다.

## 2. Vector ledger

모션이 중요한 장면은 작업 폴더에 `motion-ledger.json`을 둔다.

```json
{
  "dominant_current": "left-to-right",
  "transition_vocabulary": ["rise", "carrier-match", "hard-resolve"],
  "seams": [
    {
      "from": 3,
      "to": 4,
      "carrier": "red-orbit",
      "exit_vector": [1, 0],
      "entry_vector": [1, 0],
      "speed_match": "pass",
      "identity_match": "pass",
      "purpose": "문제의 원인이 해결 구조로 이동한다"
    }
  ]
}
```

carrier가 없으면 배경 방향, 카메라 이동, 광원 변화 중 하나를 연결 고리로 쓴다. 아무 연결도 없으면 hard cut을 의도적으로 선택한다.

## 3. 연속 이미지 생성: `$imagegen`

연속 이미지는 “비슷한 그림 여러 장”이 아니라 같은 세계의 시간 변화다.

### 사전 계약

생성 전에 아래를 고정한다.

- subject identity: 인물/제품/오브젝트의 외형, 재질, 색, 로고, 비율
- camera: 렌즈 느낌, 높이, 거리, 축, 프레이밍
- environment: 장소, 배경 구조, 광원, 시간대
- palette/style: 덱 토큰과 렌더 스타일
- motion path: 무엇이 어느 방향으로 얼마나 움직이는가
- invariants: 절대 변하면 안 되는 항목
- frame count: 보통 3~6장. 장수가 많다고 자연스러운 것이 아니다.

### 생성 절차

1. 사용자에게 storyboard와 예상 장수를 보여주고 생성 승인을 받는다.
2. 첫 프레임을 `$imagegen` built-in으로 만든다.
3. 결과를 눈으로 확인하고 `output/NN_slug_date/assets/sequence-name/01.png`로 보존한다.
4. 2번 프레임부터는 직전 승인 프레임을 reference/edit 입력으로 사용한다.
5. 프롬프트에는 전체 장면 설명보다 “직전 프레임에서 바뀌는 것”과 invariants를 먼저 쓴다.
6. 매 프레임마다 피사체 정체성, 카메라 축, 조명, 배경 구조를 확인한다.
7. 실패한 프레임을 다음 프레임의 reference로 쓰지 않는다.
8. 사실을 재현한 것처럼 보일 수 있으면 `AI-generated illustration`을 캡션/CREDITS에 명시한다.

프롬프트 골격:

```text
Continue the exact same scene and subject from the reference frame.
Invariant: [identity/camera/environment/palette].
Only change: [single motion delta].
Motion direction: [vector], progress [n/N].
Keep composition safe for a 16:9 presentation and leave [area] clear for text.
No text, no new objects, no camera jump, no identity drift, no style drift.
```

Codex에서는 direct image API나 `gen_image.py`를 기본 경로로 쓰지 않는다. built-in 실패 후 사용자가 명시적으로 허용했을 때만 fallback을 사용한다.

## 4. HTML image sequence

프레임은 같은 크기와 종횡비로 저장한다.

```html
<figure
  class="image-sequence"
  data-sequence-id="product-open"
  data-fps="3"
  data-loop="false"
  data-mode="crossfade"
  data-print-frame="3"
  aria-label="제품이 열리며 내부 구조가 드러나는 연속 장면"
>
  <img src="assets/product-open/01.png" alt="" data-frame>
  <img src="assets/product-open/02.png" alt="" data-frame>
  <img src="assets/product-open/03.png" alt="" data-frame>
  <img src="assets/product-open/04.png" alt="" data-frame>
</figure>
```

- 전체 의미는 `figure`의 `aria-label`에 쓴다. 장식 프레임의 `alt`는 빈 값으로 둔다.
- `data-print-frame`은 0부터 시작하는 인덱스다.
- `crossfade`는 미세한 형태 변화, `cut`은 stop-motion/단계 변화에 쓴다.
- 슬라이드를 벗어나면 재생을 멈추고 첫 프레임으로 되돌린다.
- reduced-motion과 PDF에서는 `data-print-frame` 한 장만 보인다.
- 무한 루프는 배경 ambient가 아니면 사용하지 않는다. 핵심 sequence는 `data-loop="false"`가 기본이다.

## 5. Seam QA

각 중요 seam에서 다음을 확인한다.

- 방향: exit와 entry vector가 같은가?
- 속도: cut 전후 체감 속도가 이어지는가?
- 정체성: carrier/피사체의 색, 크기, 질감이 이어지는가?
- 공간: 화면 밖으로 완전히 밀어낸 뒤 새 장면이 출발하는 지루한 push가 아닌가?
- 여백: climax 직전 0.3~0.75초 정지가 있는가?
- 의미: 전환을 제거하면 설명력이 줄어드는가?
- 접근성: reduced-motion에서 정보 손실이 없는가?

하나라도 실패하면 모션을 더 추가하지 말고 seam을 단순화한다.
