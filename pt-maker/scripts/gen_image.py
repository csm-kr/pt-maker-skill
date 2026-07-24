#!/usr/bin/env python3
"""pt-maker legacy direct-API image generation for non-Codex compatibility.

Codex must use the imagegen skill's built-in image_gen tool by default. Run this
script only when the user explicitly requests or approves the direct API path.

사용:
  python gen_image.py "프롬프트" out.png [--size 1536x1024] [--quality high] [--model gpt-image-2-vip]

키는 .env(또는 환경변수)에서만 읽고 절대 화면에 출력하지 않는다.
표준 라이브러리만 사용 (별도 설치 불필요).
"""
import argparse, base64, json, os, sys, urllib.request, urllib.error
from pathlib import Path


def load_dotenv(start_dirs=None):
    """이미 환경변수에 있으면 우선. 없으면 .env를 탐색한다.
    순서: cwd→상위, 그다음 스크립트(스킬) 폴더→상위 — 스킬 폴더만 떼어가도 동작.
    찾은 .env 경로를 반환, 없으면 None."""
    if start_dirs is None:
        start_dirs = [Path.cwd(), Path(__file__).resolve().parent]
    seen = set()
    for start in start_dirs:
        for d in [start, *start.parents]:
            if d in seen:
                continue
            seen.add(d)
            f = d / ".env"
            if f.is_file():
                for line in f.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
                return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("out")
    ap.add_argument("--size", default="1536x1024",
                    help="1536x1024(기본) / 16:9는 2048x1152 또는 1792x1024 (vip·official)")
    ap.add_argument("--quality", default=None, help="auto|low|medium|high (official gpt-image-2 전용)")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    load_dotenv()
    key = (os.environ.get("OPENAI_API_KEY") or os.environ.get("APIYI_API_KEY")
           or os.environ.get("OPENAI_KEY"))
    if not key:
        sys.exit("SKIP: .env에서 API 키(OPENAI_API_KEY/APIYI_API_KEY)를 찾지 못해 "
                 "이미지 생성을 건너뜁니다. (키 없이도 덱은 플레이스홀더로 계속 진행)")
    base = (os.environ.get("OPENAI_BASE_URL") or os.environ.get("APIYI_BASE_URL")
            or "https://api.apiyi.com/v1").rstrip("/")
    model = args.model or os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-2-vip"

    body = {"model": model, "prompt": args.prompt, "n": 1, "size": args.size}
    if args.quality:
        body["quality"] = args.quality  # vip 변형은 quality 미지원이므로 기본 생략

    req = urllib.request.Request(
        base + "/images/generations",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: HTTP {e.code}: {e.read().decode(errors='replace')[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: 연결 실패: {e}")

    item = (res.get("data") or [{}])[0]
    if item.get("b64_json"):
        raw = base64.b64decode(item["b64_json"])  # apiyi는 prefix 없는 순수 base64
    elif item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            raw = r.read()
    else:
        sys.exit("ERROR: 응답에 이미지가 없습니다: " + json.dumps(res)[:300])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    print(f"OK: {out} ({len(raw)} bytes · model={model} · size={args.size})")


if __name__ == "__main__":
    main()
