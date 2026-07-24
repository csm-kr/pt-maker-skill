# pt-maker-skill

Codex에서 발표자료를 기획·제작·검수하는 `pt-maker` 스킬입니다.

- `presentation`: Reveal.js 기반 1280×720 HTML 덱과 PDF
- `animation`: HyperFrames 기반 deterministic animation과 영상
- `both`: 발표용 덱과 애니메이션을 각각 생성
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

새 프로젝트를 직접 만들 때:

```bash
# Reveal HTML + PDF
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --mode presentation

# HyperFrames animation
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --mode animation

# 두 형식 모두
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --mode both
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
