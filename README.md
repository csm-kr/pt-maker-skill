# pt-maker-skill

Codex에서 발표자료를 기획·제작·검수하는 `pt-maker` 스킬입니다.

- `애니메이션 위주`: HyperFrames 기반 가로 탐색 애니메이션 HTML이 기본 완성본
  (MP4/WebM/GIF는 명시 요청 시만 추가)
  - `paper-motion` 스타일: 종이 질감 모션그래픽 + 코드로 그린 부엉이 화자 캐릭터
- `줄글 위주`: 제목·카피·본문 중심의 Reveal.js HTML 덱과 PDF
- `이미지 위주`: 주요 텍스트마다 관련 이미지가 들어가는 Reveal.js HTML 덱과 PDF
- `심사·제출용`: 공모전·투자 심사·지원사업처럼 채점 기준이나 지정 템플릿이 있는
  자리용. 템플릿 크기의 고정 HTML 슬라이드와 화면과 1:1인 PDF, 그리고 숫자·출처·
  레이아웃·심사 패널·제출 검사
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
4. 심사·제출용 (지정 템플릿 + 근거 검사)
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

# 심사·제출용: 지정 템플릿(.pptx)을 읽어 슬롯마다 한 페이지씩 스캐폴딩
python3 .codex/skills/pt-maker/scripts/new_deck.py \
  "topic-slug" --production-direction judged --template template.pptx
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

## 심사·제출용 모드

채점 기준이 있는 자리(공모전, 투자 심사, 지원사업, 입찰)에 내는 덱입니다. 첫 포맷
질문에서 `4. 심사·제출용`을 고르면, 지정 템플릿 → 채점 기준과 가중치 → 제한(쪽수·MB·
단어 수·마감) → 근거 출처를 한 번에 하나씩 묻습니다. 1~3 포맷의 흐름은 그대로입니다.

- 스타일은 고정입니다: 실제 제품 화면 캡처 + 주장형 문장 + 인라인 SVG 도식.
- 숫자는 모두 `facts.json`(근거 장부)에서 넣고, 숫자가 있는 슬라이드는 footer에 출처
  줄(`Details: …`)을 보입니다.
- 근거 자리에는 생성 이미지를 쓰지 않습니다. 실제 화면은 `capture_screens.py`로 찍습니다.
- 자세한 절차: `pt-maker/reference/judged-deck.md`, 심사 패널: `pt-maker/reference/judge-panel.md`

```bash
S=.codex/skills/pt-maker/scripts
D=output/NN_topic_date
python3 $S/new_deck.py "topic" --production-direction judged --template template.pptx
python3 $S/capture_screens.py $D/shots.json          # 실제 화면 → assets/img/
GITHUB_URL=… VIDEO_URL=… python3 $S/build_judged_deck.py $D/deck.src.html
python3 $S/qa_layout_gate.py $D/deck.html --pdf $D/topic-v1.pdf   # 검사 + slides/NN.png + PDF
python3 $S/qa_facts_gate.py $D/deck.html             # 장부에 없는 숫자, 출처 없는 슬라이드, 금지 표현
python3 $S/qa_judge_gate.py $D/judge_ledger.json     # 기준별 눈가림 심사 + 사실 확인 결과
python3 $S/qa_submission_gate.py $D/deck.html $D/topic-v1.pdf --config $D/judged.json
```

QR 자리표시(`{{qr:url}}`)를 쓸 때만 선택 패키지 `segno`가 필요합니다
(`python3 -m pip install segno`). 나머지는 Python 표준 라이브러리와 기존
browser-harness만 씁니다.

## 이전 방식과 달라진 점

### `judged-deck` 브랜치

| 항목 | 이전 | 지금 |
|---|---|---|
| 첫 포맷 질문 | 3지선다(애니메이션 / 줄글 / 이미지) | 4지선다: `4. 심사·제출용 (지정 템플릿 + 근거 검사)` 추가. 건너뛰면 여전히 `image` |
| 심사용 인테이크 | 없음 | 4번을 고르면 템플릿 → 채점 기준·가중치 → 제한 → 근거 출처를 하나씩 질문. 1~3에는 새 질문 없음 |
| `new_deck.py` | `--production-direction animation\|text\|image` | `judged` 추가, `--template template.pptx`로 템플릿을 읽어 요약과 warning을 출력하고 슬롯마다 한 페이지 스캐폴딩 |
| 지정 템플릿 | 참고자료로만 흡수 | `import_template.py`: 슬라이드 크기(px, 인치), 배경(`p:bg`, 전체 그림), 템플릿 아트(그림 crop, 모양·채우기 종류와 상관없는 채워진 도형), 슬롯 제목과 제목 상자, 최소 글자 px, 글꼴, 건너뛴 것 warning → `template.json` + 템플릿 layer |
| 덱 형식 | Reveal 1280×720 | 심사용은 템플릿 크기 고정 HTML 슬라이드, 템플릿 실제 쪽 크기로 인쇄한 1:1 PDF |
| 숫자와 출처 | 출처는 작업 노트·CREDITS에, 슬라이드에는 최소한 | 심사용은 `facts.json` 장부 + `{{fact:id}}`(빌드가 `data-fact`로 표시) + footer 출처 줄. `qa_facts_gate.py`가 모든 슬라이드의 표시 없는 숫자, 출처 없는 슬라이드, 빈 `Details:`, 금지 표현을 막음 |
| 근거 이미지 | 웹 이미지 또는 생성 일러스트 | 심사용 근거는 실제 캡처(`capture_screens.py`)나 공개 자료만. 생성 이미지는 근거 금지 |
| 레이아웃 검사 | 렌더 후 사람/agent 검수 | `qa_layout_gate.py`: 실제 글줄 기준 최소 글자(transform 배율 반영)·가장자리·가로 넘침, 템플릿 아트 겹침, footer 줄 수·겹침, 잘림, 깨진 이미지, 본편 단어 수 + PNG + 슬라이드 글자 + 1:1 PDF |
| 심사 리뷰 | 미감 QA agent 1개(90점) | 미감 QA는 그대로 + 채점 기준별 눈가림 심사 agent와 사실 확인 agent, `qa_judge_gate.py`(심사한 `deck.html`과 그 파일이 쓰는 CSS·이미지·글꼴의 해시로 낡은 장부를 막음) |
| 제출 직전 | 없음 | `qa_submission_gate.py`: 자리표시 잔여, PDF 크기·쪽수, 슬롯 순서·제목, 링크 HTTP 200 |
| HTML guard | Reveal 설정 필수 | `data-deck="judged"` 덱은 Reveal 설정 대신 `@page` 크기 검사 |
| 미감 QA 점수(정적 덱) | 모션·전환·탐색 항목 필수 | 심사용 덱은 그 항목을 빼고 86점을 100점으로 환산 |
| 숫자 확인 정도 | 없음 | `facts.json` `status` → 꼬리표 주장·시연·검증·보도 |
| 테스트 | 50개 | 145개 |

### `paper-motion-taste` 브랜치

기본 테마 덱의 동작은 그대로입니다.

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
