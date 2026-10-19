# 심사·제출용 덱 (judged) 플레이북

공모전, 투자 심사, 지원사업, 입찰처럼 **채점 기준이 있거나 지정 템플릿에 맞춰 PDF를
제출하는 자리**용 절차다. 첫 포맷 질문에서 `4. 심사·제출용`을 고르면 이 문서를 따른다.
심사위원은 짧은 시간에 많은 덱을 넘겨 보며 기준표에 점수를 매긴다. 그래서 이 모드의
목표는 "예쁜 덱"보다 **한 번 읽고 믿을 수 있는 덱**이다: 주장은 한 줄로 보이고, 숫자는
모두 출처가 보이고, 템플릿 규칙은 하나도 어기지 않는다.

## 고정 스타일

- **실제 제품 화면 캡처 + 주장형 문장 + 인라인 SVG 도식.** 줄글/이미지 중 하나를 다시
  고르지 않는다. 애니메이션은 쓰지 않는다.
- **생성 이미지는 근거로 절대 쓰지 않는다.** 근거 슬롯(제품이 실제로 동작함을 보여 주는
  자리)은 `capture_screens.py`로 찍은 실제 화면이나 공식·공개 자료만 쓴다. 도식은 SVG로
  직접 그린다.
- **Reveal이 아니다.** 템플릿 크기(기본 1920×1080 px)의 고정 HTML 슬라이드를 쓰고,
  `.slide` 하나가 PDF 한 쪽이다. PDF는 화면과 1:1이고, 템플릿의 실제 쪽 크기(인치)로 인쇄한다.

## 이 모드에서 바뀌는 규칙 두 가지

1. **출처를 보인다.** 일반 덱은 출처를 과하게 노출하지 않지만, 심사용 덱은 숫자가 있는
   슬라이드마다 footer에 출처 줄(`Details: …`)을 둔다. footer는 3줄 이하로 줄인다.
2. **생성 이미지는 근거가 아니다.** 근거는 실제 캡처나 공개 자료뿐이다.

나머지 pt-maker 규칙(한 장 한 아이디어, 가독성 하한, 줄바꿈·겹침 P0, 90점 미감 QA)은
그대로 적용된다.

## 흐름

1. **인테이크** — [intake.md](intake.md) §0.2의 네 질문(템플릿 → 채점 기준·가중치 →
   제한 → 근거 출처)을 하나씩 묻고 이어서 평소 인터뷰를 한다.
2. **스캐폴딩과 템플릿 가져오기** —
   `new_deck.py "<slug>" --production-direction judged --template 템플릿.pptx`.
   `import_template.py`가 템플릿을 읽어 `template.json`, `template-layer.css`,
   `assets/template/`을 만들고, 읽은 내용과 건너뛴 것(warning)을 출력한다. 슬롯마다 한
   페이지씩 `deck.src.html`을 채운다. warning이 있으면 렌더된 첫 PNG를 템플릿과 나란히
   보고 빠진 아트가 없는지 확인한다. 채점 기준·쪽수·MB·단어 수는 `judged.json`에, 마감과
   근거 출처는 인테이크 노트와 `NOTES.md`에 적는다.
3. **메시지 먼저** — 한 줄 메시지를 정하고, 슬롯마다 헤드라인(주장 한 문장)을 쓴다.
   `NOTES.md`에 슬라이드 지도(페이지 ↔ 템플릿 슬롯 ↔ 헤드라인)를 만든다. 사용자와 이
   지도를 합의한 뒤에 본문을 쓴다.
4. **숫자 장부** — 슬라이드에 들어갈 숫자를 모두 `facts.json`에 적는다.
5. **실제 화면** — `shots.json`에 찍을 화면을 적고 `capture_screens.py shots.json`.
   캡처한 화면의 글자(답변, 가격, 메뉴 등)도 사실인지 읽고 나서 쓴다.
6. **빌드** — `build_judged_deck.py deck.src.html` → `deck.html`.
7. **검사** — `qa_layout_gate.py`(PNG, 슬라이드 글자, PDF도 만든다) → `qa_facts_gate.py` →
   `qa_html_guard.py`, `qa_media_guard.py` → 렌더 PNG를 직접 읽기 → 기존 90점 미감 QA
   (`qa_score_gate.py`). 심사용 덱은 정적이라 모션·전환·탐색 항목이 빠지고, 나머지 86점을
   100점으로 환산한다(장부의 `score` = 항목 합 × 100 / 86). contact sheet는
   `verify_pdf.py`(pymupdf, pillow 필요)로 만든다.
8. **심사 패널** — [judge-panel.md](judge-panel.md). 기준마다 독립 심사 agent 하나와 사실
   확인 agent 하나. `qa_judge_gate.py judge_ledger.json`이 통과할 때까지 반복한다.
9. **제출 검사** — `qa_submission_gate.py deck.html <주제>.pdf --config judged.json`.
10. **기록** — 패스마다 `CHANGES.md`에 항목 하나: 무엇을 바꿨나, 왜, 검사 결과.

## 원칙

### 메시지가 먼저다
- 각 페이지의 `h1`은 주제가 아니라 주장이다. 템플릿의 슬롯 제목(`.tt`, 예: "Solution
  overview")은 템플릿 문구로 그대로 두고, 그 아래 헤드라인이 내 주장이다.
- 같은 한 줄 메시지를 표지, 아이디어 페이지, 마무리 페이지, 그리고 제품 첫 화면·README
  같은 다른 표면에서도 같은 말로 쓴다.
- 한 장 한 아이디어. 슬롯 하나에 할 말이 많으면 같은 슬롯 페이지를 하나 더 만든다
  (`data-slot`이 같은 페이지가 이어져도 된다).

### 숫자는 장부에서, 출처는 보이게
- 모든 숫자는 `facts.json` 값이고, 슬라이드에는 `{{fact:id}}`로 넣는다. 빌드가
  `<span class="fact" data-fact="id">`로 표시하고, `qa_facts_gate.py`는 표시 없는 숫자를
  본편·부록 어디서든 막는다. 장부 값과 같은 숫자를 손으로 쳐도 실패다.
- 숫자로 세지 않는 곳은 쪽 번호(`.pg`), 템플릿 문구(`.nowc`), 링크 글자, fact 단위 안의
  숫자("38 of 100", "4.2 per 1,000 beds"), 앞뒤가 모두 한글인 숫자("제3자"), footer 출처 줄의
  날짜(YYYY-MM-DD)·연도·쪽/표/그림 참조(p. 4, pp. 3–5, Table 2, Fig. 1, 표 2, 그림 1, 12쪽)·라이선스
  이름(CC BY 2.0, CC BY-SA 4.0, CC0)·위키 판 번호(oldid=…), 그리고 근거가 아닌 번호에 붙인
  `.nofact`뿐이다. `.nofact`는 단계 번호, "slide A3" 같은 참조, 그리고 "0-60 mph"처럼 숫자가 든
  측정 이름(값이 아니라 무엇을 쟀는지의 이름)에 쓴다. 아껴 쓴다. 심사 패널의 사실 확인이 다시 본다.
- 장부 값은 적힌 그대로 두고, 빌드가 화면에 천 단위 쉼표를 넣는다(`200000` → `200,000`). 다섯
  자리 이상은 항상, 네 자리는 1900–2099를 연도로 보고 빼고 넣는다. 쉼표를 직접 적은 값은 그대로다.
- 같은 결과는 어디서나 같은 문장, 같은 형태로 쓴다. 한 페이지에서 고친 숫자 문장은
  나오는 모든 페이지에서 똑같이 고친다.
- 서로 다른 실험·조건의 숫자를 더하거나 섞지 않는다. 묶음마다 따로 말한다.
- 큰 숫자는 가장 정직한 형태로 쓴다. 예: 실패를 빼고 성공만 크게 보이는 비율 대신,
  전체 중 안전하게 끝난 수와 그 내역을 함께 쓴다.
- footer 출처 줄: 무엇을 어떻게 쟀는지 한 문장, 그리고 `Details: <열어 볼 수 있는 문서나
  파일>`. `Details:` 뒤가 비면 실패다. 3줄 이하. 출처 목록이 길면 부록 출처 페이지로 보낸다.
- 바깥 숫자(시장, 통계, 가격)는 그날 직접 열어 읽고 `checked` 날짜를 적는다. 숫자를
  옮긴 문장과 원문 문장이 같은 것을 말하는지 확인한다(예: "매장 수"를 "기기 수"로 읽지 않기).
- 비율 그림 `{{dots:id}}`도 장부의 fact(단위 `%`, `in 100`, `of 100`, `per 100`)에서만 그린다.

### 상태 꼬리표 (주장 · 시연 · 검증 · 보도)
- 숫자가 얼마나 확인된 것인지 보여 줘야 하는 덱은 `facts.json`의 `status`를 쓴다:
  `claimed` → **주장**(회사·발표자가 말함), `demonstrated` → **시연**(관객 앞에서 보여 줌),
  `verified` → **검증**(독립적으로 재거나 확인함), `reported` → **보도**(언론·집계가 전함).
  다른 값이면 `qa_facts_gate.py`가 실패한다.
- 슬라이드에는 숫자 옆에 꼬리표를 둔다: `<span class="chip c-rep">보도</span>`(`c-claim`, `c-demo`,
  `c-ver`, `c-rep`).
- 보도를 검증으로 올리거나 주장으로 내리지 않는다. 보도를 검증으로 올리면 사실을 부풀리고,
  주장으로 내리면 말하지 않은 사람의 말이 된다.

### 피하는 주장
- `judged.json`의 `facts.banned_phrases`(기본: first, only, any, 100%, 최초, 유일)는
  주장으로 쓰지 않는다. 주장이 아닌 사용(예: "first market")만 `allowed_phrases`에 적는다.
- "규정 준수(compliant)", "누구나", "모든 기기" 같은 넓은 주장도 근거가 없으면 쓰지
  않는다. 비슷한 아이디어는 "보도된 바로는"으로 소개하고 내 방식을 옆에 놓되, 남이
  못 하는 것을 단정하지 않는다.
- 피한 주장 목록을 `NOTES.md`에 남긴다.

### 한계를 솔직하게
- "아직 해결하지 못한 것" 페이지를 둔다. 모르는 것은 `unknown`이라고 쓴다(가격, 실제
  사용자 시험 여부, 파트너 유무 등).
- 실제 사용자 시험이 없으면 "아직 없다"고 쓴다. 합성 데이터, 자동화된 시험, 팀이 만든
  시험이라면 그렇게 밝힌다.

### 부록
- 본편 뒤에 부록(A1, A2, …)을 둔다: 예상 질문과 답(Q&A) 1~2쪽, 출처 표, 상세 시험 결과.
- 본편 페이지는 `data-main`을 달고 단어 수 상한(기본 80, footer와 템플릿 문구 제외)을
  지킨다. 부록은 단어 수 상한을 받지 않지만 글자 크기·겹침·숫자 검사는 같다.

### 실제 화면
- 제품이 바뀌면 캡처를 다시 찍는다. 캡션이나 footer에 어느 배포(버전)를 언제 찍었는지
  적고, `assets/CREDITS.txt`에 URL과 시각이 남는다.
- 화면 속 글자도 사실이어야 한다. 실제 데이터에 없는 항목이 보이는 캡처는 쓰지 않는다.
- 잘라 쓸 때는 `shots.json`의 `clip`으로 자르고 `.crop` 틀 안에 넣는다. 너무 작아 읽을
  수 없는 부분(템플릿 최소 글자보다 작은 화면 글자)은 별도로 확대해 찍는다.

### 템플릿 규칙
- 슬롯 제목은 템플릿 문구 그대로(`class="tt nowc"`). 슬롯 순서를 지킨다. 빼도 되는
  슬롯(예: 안내 페이지)은 `judged.json` `slots.skip`에 적는다. 제목에 안내문이 붙은
  슬롯은 `template.json` 그 슬라이드의 `"match"`를 `"prefix"`(첫 `(`·`:`·`—` 앞까지만
  비교)로, "Click to add title" 같은 자리표시 제목은 `"skip"`으로 바꾼다. 템플릿을 다시
  가져와도 같은 번호·같은 제목의 슬롯은 이 값이 유지된다.
- 템플릿 아트 위에 아무것도 올리지 않는다. 예외는 템플릿 제목 상자다: 템플릿이 제목을
  띠 위에 그리면 그 띠는 제목 아래 layer로 그려지고, 제목 상자 안의 글자만 겹쳐도 된다.
- 템플릿의 가장 작은 글자 크기보다 작은 글자를 어디에도(footer 포함) 쓰지 않는다.
  px = pt × (출력 폭 px ÷ 슬라이드 폭 pt). 예: 13.33인치(960 pt) 슬라이드를 1920 px로
  그리면 10 pt = 20 px.
- 템플릿 글꼴은 템플릿 문구에만 쓰고, 파일이 없으면 `assets/fonts/`에 넣는다(라이선스 확인).

### 링크와 사용자 확인 항목
- GitHub, 영상 같은 링크는 `{{link:GITHUB_URL}}`처럼 쓰고 빌드할 때 환경 변수로 채운다.
  비어 있으면 경고 스타일 자리표시가 남고 `qa_submission_gate.py`가 막는다.
- 사용자가 직접 채워야 하는 항목(링크, 팀 역할, 확인 안 된 사실)을 `NOTES.md`의 "직접
  채울 항목" 표에 모은다.

### 기록
- 패스마다 `CHANGES.md` 맨 위에 항목 하나: 바꾼 것, 이유, 숫자·화면 변경, 검사 결과,
  다시 읽은 페이지.
- `NOTES.md`: 마감과 근거 출처, 직접 채울 항목, 슬라이드 지도, 숫자 → 출처, 피한 주장,
  화면 캡처 목록, 아직 모르는 것.

## 템플릿을 읽는 방법 (`import_template.py`)

- **배경**(내용 아래, 겹침 검사 없음): 슬라이드 → 레이아웃 → 마스터 순서로 처음 나오는
  `p:bg`(단색, 그라데이션, 그림), 슬라이드 전체를 덮는 그림·도형, 채워진 placeholder.
- **템플릿 아트**(겹치면 안 되는 영역): 그림(`srcRect` crop 반영)과 채워진 도형. 도형
  모양과 상관없이 단색, 그라데이션, 그림 채우기, `p:style`의 테마 채우기를 모두 읽는다.
  둥근 사각형과 타원은 모양대로, 나머지 모양은 사각형으로 그린다.
- **건너뛰고 warning을 남기는 것**: 그룹, 표·차트, 연결선, 채우기 없는 도형(테두리만),
  회전, 색 보정(밝기 조절 등). warning이 나오면 렌더 PNG에서 빠진 것을 확인한다.
- **최소 글자 크기**: 슬라이드와 그 레이아웃·마스터에 쓰인 가장 작은 `sz`.

## 클래스 규칙 (검사 스크립트가 읽는다)

| 표시 | 뜻 |
|---|---|
| `<html data-deck="judged">` | 심사용 덱. `qa_html_guard.py`가 Reveal 설정 대신 `@page` 크기를 검사 |
| `.slide` | 한 쪽. 템플릿 크기, `overflow: hidden` |
| `data-tpl="N"` | 이 쪽에 템플릿 N번 슬라이드의 배경과 아트를 깐다(빌드가 넣음, 레이아웃 검사가 아트 영역을 고름) |
| `data-slot="N"` | 이 쪽이 템플릿 N번 슬롯을 채운다(제출 검사가 순서·제목 확인) |
| `data-main` | 본편. 단어 수 상한을 받는다 |
| `.hd .tt` / `.hd h1` / `.hd .sub` | 슬롯 제목 / 주장 헤드라인 / 보조 문장 |
| `.ft .src` / `.ft .pg` | footer 출처 줄 / 쪽 번호 |
| `.fact[data-fact]` / `.dots[data-fact]` | 장부에서 온 숫자 / 비율 그림(빌드가 넣음) |
| `.nowc` | 템플릿 문구(단어 수와 숫자·금지 표현 검사에서 뺌) |
| `.nofact` | 주장이 아닌 번호(단계, 슬라이드 참조). 아껴 쓴다 |
| `.tart` / `.tart.tbase` | 템플릿 아트(내용 위) / 배경과 제목 아래 아트(내용 아래). 빌드가 넣음 |
| `.crop` | 캡처를 자르는 틀(안의 이미지는 아트 겹침 검사에서 뺌) |
| `.ph` | 채우지 않은 자리표시. 제출 검사가 막는다 |

## 빌드 자리표시

| 소스 | 결과 |
|---|---|
| `{{fact:id}}` / `{{fact:id:value}}` | 장부 값 + 단위 / 값만, `<span class="fact" data-fact="id">` (SVG 안에서는 `<tspan>`) |
| `{{dots:id}}` | 장부 fact 값만큼 채운 100칸 점 격자 |
| `{{link:NAME}}` | 환경 변수 NAME의 링크, 없으면 `.v.ph` 경고 |
| `{{icon:name}}` | `assets/icons/name.svg` 인라인 |
| `{{qr:url}}` | QR SVG (선택 패키지 `segno` 필요) |

자리표시는 글자 자리에만 쓴다(태그 속성 안이면 빌드 실패). `{{dots:…}}`와 `{{link:…}}`는
HTML을 만들므로 `<svg>` 밖에만 쓴다. 빌드는 숫자+단위와 `≤ N`을
붙이고(NBSP), 날짜가 하이픈에서 끊기지 않게 하고(`<code>` 안은 그대로), 긴 경로는 슬래시
뒤에서만 줄바꿈되게 한다. HTML 주석은 소스에만 남는다(`<script>` 안의 `<!--`는 그대로).

## 파일

### `judged.json`

| 키 | 뜻 |
|---|---|
| `template` | `template.json` 경로 |
| `criteria` | `[{"id", "name", "weight"}]`, 가중치 합 100 |
| `target` | 심사 패널 가중 점수 목표(기본 8.0/10) |
| `limits` | `max_pages`, `max_mb`(1 MB = 1,000,000 bytes), `max_words_per_slide`(기본 80) |
| `layout` | `min_font_px`(없으면 템플릿 값), `max_footer_lines`(기본 3) |
| `facts` | `source_label`(기본 `Details:`), `banned_phrases`, `allowed_phrases` |
| `slots` | `skip`: 빼도 되는 템플릿 슬롯 번호 |

### `facts.json`

```json
{"facts": [
  {"id": "survey-share", "value": "38", "unit": "%",
   "claim": "Respondents who said they would use it weekly",
   "source": "data/survey-results.csv", "checked": "2026-10-12", "status": "verified"}
]}
```

`value`에는 숫자가 있어야 한다. `status`는 선택이며 `claimed`, `demonstrated`, `verified`, `reported` 중 하나다. `source`는 심사위원이나 팀원이 열어 볼 수 있는 파일·URL이다.

### `shots.json`

`capture_screens.py` 문서 문자열에 형식이 있다. 찍은 파일은 `assets/img/<name>.jpg`.

## 명령

```bash
python3 scripts/new_deck.py "<slug>" --production-direction judged --template 템플릿.pptx
python3 scripts/capture_screens.py output/NN_.../shots.json
GITHUB_URL=… VIDEO_URL=… python3 scripts/build_judged_deck.py output/NN_.../deck.src.html
python3 scripts/qa_layout_gate.py output/NN_.../deck.html --pdf output/NN_.../<주제>v<N>.pdf
python3 scripts/qa_facts_gate.py output/NN_.../deck.html
python3 scripts/qa_html_guard.py output/NN_.../deck.html
python3 scripts/qa_media_guard.py output/NN_.../deck.html
python3 scripts/qa_judge_gate.py output/NN_.../judge_ledger.json
python3 scripts/qa_submission_gate.py output/NN_.../deck.html output/NN_.../<주제>v<N>.pdf --config output/NN_.../judged.json
```

`qa_layout_gate.py`가 만든 PDF가 제출본이다. Reveal용 `export_pdf.py`는 쓰지 않는다.
