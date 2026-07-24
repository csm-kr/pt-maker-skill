# apiyi 이미지 API 레퍼런스 (gpt-image-2 계열)

> 레거시 direct-API 참고자료. Codex의 기본 이미지 생성·편집 경로가 아니다.
> Codex에서는 `$imagegen` 스킬의 built-in `image_gen` 도구를 우선하며 API 키가 필요 없다.
> 사용자가 direct API/CLI 방식을 명시적으로 요청한 경우에만 이 문서와 `scripts/gen_image.py`를 사용한다.

OpenAI 호환 게이트웨이. 레거시 `scripts/gen_image.py`가 내부적으로 이 형식을 호출한다.

## 엔드포인트
- `POST https://api.apiyi.com/v1/images/generations` (백업: `https://vip.apiyi.com/v1`)
- 헤더: `Authorization: Bearer <KEY>`, `Content-Type: application/json`

## 요청 body
```json
{ "model": "gpt-image-2-vip", "prompt": "...", "size": "1536x1024", "n": 1 }
```
- `quality`(auto|low|medium|high)는 **official `gpt-image-2`** 에서만. vip/-all에는 보내지 않는다.
- `size`: official/vip는 파라미터로 지정 가능(16:9는 `2048x1152`/`1792x1024`). `-all`은 size 파라미터 대신 프롬프트에 크기를 적는다.

## 응답
```json
{ "data": [ { "b64_json": "<prefix 없는 순수 base64 PNG>" } ] }
```
`b64_json`은 `data:image/png;base64,` 접두사가 없다. 브라우저 임베드 시 접두사를 붙여야 한다.

## 모델 변형 (모두 $0.03/장)
| 모델 | size 제어 | 속도 | 특징 |
|---|---|---|---|
| `gpt-image-2-vip` (기본) | ✅ 30 프리셋(16:9·4K) | 90~150s | 정확한 치수 — 슬라이드용 권장 |
| `gpt-image-2-all` | ❌(프롬프트에 명시) | 30~60s | 텍스트 렌더·프롬프트 준수 최고 |
| `gpt-image-2` (official) | ✅ + quality | - | 공식, 단가 높음 |

## .env 키 (프로젝트 루트, 훅으로 읽기 차단됨)
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.apiyi.com/v1
OPENAI_IMAGE_MODEL=gpt-image-2-vip
```
