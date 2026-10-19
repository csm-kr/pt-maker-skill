# pt-maker-skill

`pt-maker`는 메모, 문서, URL, 리서치를 받아 발표자료를 기획하고 만들고 검사까지 하는 agent 스킬입니다. Codex와 Claude Code에서 씁니다.

<table>
<tr>
<td width="50%"><img src="examples/tesla-roadster/1-animation/preview/01-cover.jpg" alt="애니메이션 위주 예시"><br><b>1. 애니메이션 위주</b>: 넘길 때마다 장면이 움직이는 발표</td>
<td width="50%"><img src="examples/tesla-roadster/2-text/preview/01-cover.jpg" alt="줄글 위주 예시"><br><b>2. 줄글 위주</b>: 제목만 읽어도 이야기가 끝나는 덱</td>
</tr>
<tr>
<td width="50%"><img src="examples/tesla-roadster/3-image/preview/02-four-demos.jpg" alt="이미지 위주 예시"><br><b>3. 이미지 위주</b>: 문장마다 증거 그림이 붙는 덱</td>
<td width="50%"><img src="examples/tesla-roadster/4-judged/preview/02-step-chart.jpg" alt="심사·제출용 예시"><br><b>4. 심사·제출용</b>: 숫자마다 출처가 붙고 검사를 통과하는 덱</td>
</tr>
</table>

## 설치

```bash
git clone https://github.com/csm-kr/pt-maker-skill.git

# Claude Code
mkdir -p ~/.claude/skills && cp -R pt-maker-skill/pt-maker ~/.claude/skills/
python3 ~/.claude/skills/pt-maker/scripts/browser_harness_runtime.py --ensure

# Codex
mkdir -p ~/.codex/skills && cp -R pt-maker-skill/pt-maker ~/.codex/skills/
python3 ~/.codex/skills/pt-maker/scripts/browser_harness_runtime.py --ensure
```

- 필요한 것: Python 3, Chrome. 애니메이션 포맷을 쓸 때는 Node.js(`npx`)도 필요합니다.
- 선택: `python3 -m pip install pymupdf pillow segno`
- `--ensure`가 `browser-harness background: ready`를 출력하면 준비가 끝난 것입니다.
- 프로젝트 폴더에만 설치하는 방법은 [상세 가이드](docs/GUIDE.md)에 있습니다.

## 사용법

**1. 부릅니다.**

```text
/pt-maker 제품 소개 발표자료를 12장으로 만들어줘      ← Claude Code
$pt-maker 제품 소개 발표자료를 12장으로 만들어줘      ← Codex
```

**2. 포맷을 고릅니다.** 처음에 이 질문 하나만 나옵니다. 번호로 답하면 되고, "알아서"라고 하면 3번으로 진행합니다.

```text
어떤 포맷으로 만들까요?
1. 애니메이션 위주
2. 줄글 위주
3. 이미지 위주
4. 심사·제출용 (지정 템플릿 + 근거 검사)
```

**3. 질문에 답합니다.** 목적, 청중, 한 줄 메시지, 참고자료를 한 번에 하나씩 묻습니다.

**4. 결과를 받습니다.** 렌더한 화면 검사를 통과한 HTML·PDF가 후보로 나옵니다. 고칠 점을 말하면 새 버전으로 고쳐 줍니다.

| 포맷 | 나오는 것 | 이럴 때 |
|---|---|---|
| 1. 애니메이션 위주 | 키보드로 넘기면 장면이 재생되는 발표용 HTML (영상은 요청할 때만) | 화면 앞에서 말로 하는 발표 |
| 2. 줄글 위주 | HTML 슬라이드 + PDF, 글자가 주인공 | 논리를 전하는 발표, 읽히는 자료 |
| 3. 이미지 위주 | HTML 슬라이드 + PDF, 문장마다 이미지 | 처음 보는 사람에게 한눈에 설명 |
| 4. 심사·제출용 | 지정 템플릿 크기 HTML + 똑같은 PDF, 숫자마다 출처 | 공모전, 투자 심사, 지원사업 |

## 심사·제출용 (4번)

4번을 고르면 네 가지를 먼저 묻습니다.
- 지정 템플릿(.pptx)
- 채점 기준과 가중치
- 제한(쪽수, MB, 단어 수)
- 숫자의 근거 출처

그다음 아래 순서로 만들고 검사합니다. 하나라도 걸리면 어디를 고칠지 알려 주고 멈춥니다.

1. **템플릿 읽기:** 크기, 슬롯, 최소 글자 크기
2. **숫자 장부:** 모든 숫자는 `facts.json`에서만 가져옵니다. 숫자마다 주장·시연·검증·보도 꼬리표와 출처 줄이 붙습니다.
3. **실제 화면 캡처**
4. **레이아웃 검사**
5. **숫자 검사**
6. **눈가림 심사 패널:** 기준마다 따로 띄운 agent가 결과물만 보고 채점합니다. 사실 확인 agent는 출처를 다시 엽니다.
7. **제출 검사:** 쪽수, 용량, 링크

보통은 agent가 대신 돌립니다. 직접 돌릴 때는 아래 명령을 씁니다.

```bash
S=~/.claude/skills/pt-maker/scripts        # Codex: ~/.codex/skills/pt-maker/scripts
python3 $S/new_deck.py "topic" --production-direction judged --template template.pptx
D=output/01_topic_YYYYMMDD                 # 위 명령이 마지막 줄에 출력한 폴더

python3 $S/capture_screens.py $D/shots.json
python3 $S/build_judged_deck.py $D/deck.src.html
python3 $S/qa_layout_gate.py $D/deck.html --pdf $D/topic-v1.pdf
python3 $S/qa_facts_gate.py $D/deck.html
python3 $S/qa_judge_gate.py $D/judge_ledger.json
python3 $S/qa_submission_gate.py $D/deck.html $D/topic-v1.pdf --config $D/judged.json
```

## 예시

같은 주제(2026-10-15 Tesla Roadster 발표)를 네 포맷으로 만든 덱이 [`examples/tesla-roadster/`](examples/tesla-roadster/)에 있습니다. 컨셉, 스크린샷, 심사 라운드 기록은 [예시 설명](examples/tesla-roadster/README.md)에서 볼 수 있습니다. HTML은 내려받아 인터넷이 연결된 브라우저로 여세요. Tesla와 관계없는 비공식 정리입니다.

## 더 보기

- [상세 가이드](docs/GUIDE.md): 설치 세부, Codex와 Claude Code 차이, 심사용 단계별 설명, paper-motion 스타일, 바뀐 점, 자주 묻는 질문
- [`pt-maker/SKILL.md`](pt-maker/SKILL.md): 스킬의 전체 동작 규칙
- [`judged-deck.md`](pt-maker/reference/judged-deck.md), [`judge-panel.md`](pt-maker/reference/judge-panel.md): 심사용 절차와 심사 패널
- 테스트: `cd pt-maker/scripts && python3 -m unittest discover -p 'test_*.py'` (146개)
