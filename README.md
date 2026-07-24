# pt-maker-skill

Codex에서 발표자료를 기획·제작·검수하는 `pt-maker` 스킬입니다.

- `애니메이션 위주`: HyperFrames 기반 완성 HTML 프로젝트와 렌더 export
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

# HyperFrames animation HTML project + render export
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

HyperFrames의 `preview`, `check`, `render`는 `--background`가 필수입니다.

```bash
python3 .codex/skills/pt-maker/scripts/hyperframes_mode.py \
  preview output/NN_topic_date --background

python3 .codex/skills/pt-maker/scripts/hyperframes_mode.py \
  status output/NN_topic_date

python3 .codex/skills/pt-maker/scripts/hyperframes_mode.py \
  stop output/NN_topic_date --target all
```

## 테스트

```bash
python3 -m unittest discover \
  pt-maker/scripts -p 'test_*.py'
```

스킬의 전체 동작 계약과 QA 기준은
[`pt-maker/SKILL.md`](pt-maker/SKILL.md)를 참고하세요.
