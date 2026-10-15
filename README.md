# pt-maker-skill

Codex에서 발표자료를 기획·제작·검수하는 `pt-maker` 스킬입니다.

- `애니메이션 위주`: HyperFrames 기반 가로 탐색 애니메이션 HTML이 기본 완성본
  (MP4/WebM/GIF는 명시 요청 시만 추가)
  - `paper-motion` 스타일: 종이 질감 모션그래픽 + 코드로 그린 부엉이 화자 캐릭터
- `줄글 위주`: 제목·카피·본문 중심의 Reveal.js HTML 덱과 PDF
- `이미지 위주`: 주요 텍스트마다 관련 이미지가 들어가는 Reveal.js HTML 덱과 PDF
- 렌더링·미리보기·스크린샷은 격리된 background `browser-harness` 사용
- HTML·미디어·PDF·애니메이션·사용자 리뷰 QA gate 포함

## 설치

### 프로젝트 로컬 설치

```bash
git clone https://github.com/csm-kr/pt-maker-skill.git
mkdir -p /path/to/project/.codex/skills
cp -R pt-maker-skill/pt-maker /path/to/project/.codex/skills/

python3 /path/to/project/.codex/skills/pt-maker/scripts/browser_harness_runtime.py \
  --ensure
```

### 사용자 전역 설치

```bash
git clone https://github.com/csm-kr/pt-maker-skill.git
mkdir -p ~/.codex/skills
cp -R pt-maker-skill/pt-maker ~/.codex/skills/

python3 ~/.codex/skills/pt-maker/scripts/browser_harness_runtime.py --ensure
```

## 사용

Codex에서 자연어로 호출합니다.

```text
$pt-maker 제품 소개 발표자료를 15장으로 만들어줘.
$pt-maker 이 기획안을 발표용 HTML과 애니메이션 영상으로 만들어줘.
```

호출 직후에는 작업을 시작하기 전에 다음 질문을 반드시 하나만 합니다.

```text
어떤 포맷으로 만들까요?
1. 애니메이션 위주
2. 줄글 위주
3. 이미지 위주
```

사용자가 `그냥 진행`, `알아서`, `넘어가`처럼 선택을 건너뛰면
`이미지 위주`를 기본값으로 적용합니다. 이후 Grill Me 인테이크도 한 번에
질문 하나씩 진행합니다. 이미지 위주에서는 웹·공식·공개 자산을 먼저 찾고,
부족하면 built-in `imagegen`을 적극 사용해 여러 장의 관련 이미지를 채웁니다.

새 프로젝트를 직접 만들 때:

```bash
# 줄글 위주 Reveal HTML + PDF
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --production-direction text

# 이미지 위주 Reveal HTML + PDF
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --production-direction image

# HyperFrames project + 가로 탐색 애니메이션 HTML
# 영상 export는 사용자가 명시 요청한 경우에만 추가
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --production-direction animation

# 고급 옵션: 이미지 위주 발표 덱과 애니메이션 프로젝트를 함께 스캐폴딩
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --production-direction image --mode both
```

## Background 실행

`pt-maker`는 사용자의 보이는 Chrome에 연결하지 않습니다. 임시 프로필과
별도 CDP 포트를 가진 headless Chrome을 사용하고, 작업이 끝나면 daemon,
브라우저 프로세스와 임시 프로필을 정리합니다.

HyperFrames의 `preview`, `check`, 그리고 명시 요청된 `render`는
`--background`가 필수입니다. 최종 QA 뒤에는 `stop --target all`로
Studio/preview를 종료합니다.

```bash
python3 .codex/skills/pt-maker/scripts/hyperframes_mode.py \
  preview output/NN_topic_date --background

python3 .codex/skills/pt-maker/scripts/hyperframes_mode.py \
  status output/NN_topic_date

python3 .codex/skills/pt-maker/scripts/hyperframes_mode.py \
  stop output/NN_topic_date --target all
```

## paper-motion 스타일

종이 질감 모션그래픽과 화자 캐릭터가 나오는 애니메이션 덱입니다.
[motion-demo-video](https://github.com/csm-kr/motion-demo-video)의 모션그래픽
원칙과 레퍼런스 영상 분석을 바탕으로 만들었습니다.

- 고르는 법: 첫 포맷 질문에서 `애니메이션 위주`를 고른 뒤, 분위기 질문에서
  "종이 모션그래픽"이나 "화자 캐릭터"를 말합니다.
- 빌드 전에 읽는 파일
  - `pt-maker/paper-motion-taste-profile.md`: 이 스타일의 취향 프로필
  - `pt-maker/reference/motion-graphics-grammar.md`: 모션 원칙
  - `pt-maker/assets/speaker-character/README.md`: 부엉이 캐릭터 사용법
- 발표용 HTML은 종이 테마로 만듭니다.

```bash
python3 .codex/skills/pt-maker/scripts/build_animated_presentation.py \
  output/NN_topic_date/animation --theme paper \
  -o output/NN_topic_date/animation/<주제>-발표용-vN.html
```

- 장면 사이 전환은 기본이 하드컷입니다. 짧은 종이 밀기 전환이 필요한
  장면에만 clip host에 `data-transition="paper"`를 붙입니다.
- 화면 하단의 장 이름은 clip host의 `data-chapter` 값을 씁니다. 값이 없으면
  그 장면의 첫 제목(h1~h3)을 쓰고, 제목도 없으면 숨깁니다.

## 이전 방식과 달라진 점

`paper-motion-taste` 브랜치에서 바뀐 내용입니다. 기본 테마 덱의 동작은
그대로입니다.

| 항목 | 이전 | 지금 |
|---|---|---|
| 애니메이션 스타일 | 네온 계열 전환(prism · curtain · aperture) 한 가지 | `paper-motion` 스타일 추가 |
| 취향 프로필 | `taste-profile.md`, `dark-taste-profile.md` | `paper-motion-taste-profile.md` 추가. 부딪히는 부분은 paper-motion 덱 안에서 이 파일이 우선 |
| 모션 원칙 | `hyperframes-animation-mode.md` | `motion-graphics-grammar.md` 추가: 덱 전체를 관통하는 사물 하나, 같은 사물을 같은 자리에 두고 넘기는 컷, 강조색을 아껴 두었다 한 번 쓰기 등 |
| 화자 캐릭터 | 없음 | 코드로 그린 부엉이 SVG(포즈 5개)와 GSAP 헬퍼 `PtSpeaker` |
| 발표용 HTML 테마 | 네온 테마 하나 | `--theme paper` 추가(네온·플래시 없음, 하드컷 기본) |
| 하단 장 이름 | 다른 덱의 문구(`OPEN THE SCENT`, `MEMBER SIGNAL`)가 모든 덱에 고정으로 나오던 버그 | 장면의 `data-chapter`에서 읽고, 없으면 장면 제목(h1~h3), 둘 다 없으면 숨김. 그래서 예전 덱도 장 이름이 비지 않음 |
| 발표 HTML QA | 전환 종류를 코드에 고정, 로드 직후 첫 전환에서 가끔 실패 | 페이지가 알려 주는 전환 종류를 읽음, 측정 전에 전환을 한 번 미리 실행(warm-up) |
| 이미지 생성 도구가 없는 환경(Claude Code 등) | Codex `$imagegen` 전제 | 캐릭터·일러스트·도식을 SVG/CSS로 만든다는 규칙 추가 |
| 테스트 | 37개 | 50개 |

## 테스트

```bash
python3 -m unittest discover \
  pt-maker/scripts -p 'test_*.py'
```

스킬의 전체 동작 계약과 QA 기준은
[`pt-maker/SKILL.md`](pt-maker/SKILL.md)를 참고하세요.
