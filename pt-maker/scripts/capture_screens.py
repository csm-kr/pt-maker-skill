#!/usr/bin/env python3
"""pt-maker judged mode: real product screenshots for evidence slots.

심사용 덱의 근거 슬롯에 넣을 실제 제품 화면을 격리 background browser-harness로 찍는다.
생성 이미지를 근거로 쓰지 않기 위한 도구다.

사용:
  python capture_screens.py shots.json

shots.json (덱 폴더에 둔다):
  {"shots": [
    {"name": "checkout",                     # assets/img/<name>.jpg
     "url": "https://product.example/demo",  # http, https, file
     "viewport": [1440, 900],                 # CSS px (기본 1440×900)
     "scale": 2,                              # deviceScaleFactor (기본 2)
     "steps": [{"click": "#start"},           # 순서대로: 클릭(요소 중심을 실제 마우스로)
               {"type": ["#q", "hello"]},       #           입력(키 이벤트 + input/change)
               {"wait": ".result"}],          #           보일 때까지 기다림(20초)
     "clip": [0, 0, 1440, 900],               # 페이지 CSS px의 x, y, w, h (기본: 화면 전체)
     "width": 760,                            # 출력 JPEG 가로 px (기본: clip 폭 × scale)
     "quality": 82}                           # JPEG 품질 1-100 (기본 85)
  ]}

CDP Page.captureScreenshot(jpeg, clip.scale)로 크기를 맞추므로 Pillow가 필요 없다.
찍을 때마다 assets/CREDITS.txt에 "자산 | real capture | URL | 시각" 줄을 갱신한다.
로그인이 필요한 화면은 격리 브라우저에 세션이 없으므로 공개 데모 URL이나 file:// 사본을 쓴다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from browser_harness_runtime import BrowserHarnessError, IsolatedBrowserHarness

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
CREDIT_MODE = "real capture (capture_screens.py)"
CREDITS_HEADER = "# asset | source/generation mode | URL or prompt note | accessed/generated date\n"

BROWSER_CODE = r"""
import datetime
shots = json.loads(__SHOTS__)
out_dir = Path(__OUT__)
out_dir.mkdir(parents=True, exist_ok=True)
new_tab("about:blank")
results = []
for shot in shots:
    vw, vh = shot["viewport"]
    cdp("Emulation.setDeviceMetricsOverride", width=vw, height=vh, deviceScaleFactor=shot["scale"], mobile=False)
    goto_url(shot["url"])
    if not wait_for_load(30):
        raise RuntimeError(f"{shot['name']}: page did not finish loading")
    for step in shot["steps"]:
        if "click" in step:
            selector = step["click"]
            if not wait_for_element(selector, timeout=20, visible=True):
                raise RuntimeError(f"{shot['name']}: nothing to click at {selector}")
            box = js("(() => { const e = document.querySelector(" + json.dumps(selector) + "); e.scrollIntoView({block: 'center'}); const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
            click_at_xy(box[0], box[1])
        elif "type" in step:
            fill_input(step["type"][0], step["type"][1], timeout=20)
        elif "wait" in step:
            if not wait_for_element(step["wait"], timeout=20, visible=True):
                raise RuntimeError(f"{shot['name']}: {step['wait']} never appeared")
        wait(0.3)
    js("(async () => { if (document.fonts) await document.fonts.ready; window.scrollTo(0, 0); await new Promise((done) => setTimeout(done, 300)); return true; })()")
    x, y, w, h = shot["clip"]
    data = cdp("Page.captureScreenshot", format="jpeg", quality=shot["quality"], captureBeyondViewport=True,
               clip={"x": x, "y": y, "width": w, "height": h, "scale": shot["clip_scale"]})["data"]
    target = out_dir / f"{shot['name']}.jpg"
    target.write_bytes(base64.b64decode(data))
    results.append({"name": shot["name"], "path": str(target), "url": shot["url"],
                    "captured": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
print(json.dumps({"capture_screens": results}, ensure_ascii=False))
"""


class ShotError(ValueError):
    """Raised for an invalid shots.json entry."""


def clip_scale(*, clip_width: float, device_scale: float, width: int) -> float:
    return width / (clip_width * device_scale)


def _number_list(value: Any, length: int, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != length or not all(
        isinstance(item, (int, float)) and not isinstance(item, bool) for item in value
    ):
        raise ShotError(f"{label} must be a list of {length} numbers")
    return value


def validate_shots(data: Any) -> list[dict[str, Any]]:
    shots = data.get("shots") if isinstance(data, dict) else None
    if not isinstance(shots, list):
        raise ShotError('shots.json must be {"shots": [...]}')
    seen: set[str] = set()
    result = []
    for number, raw in enumerate(shots, start=1):
        if not isinstance(raw, dict):
            raise ShotError(f"shot {number} is not an object")
        name = str(raw.get("name", ""))
        where = f"shot {name or number}"
        if not NAME_RE.match(name):
            raise ShotError(f"{where}: name must be lowercase letters, digits, - or _")
        if name in seen:
            raise ShotError(f"{where}: name is used twice")
        seen.add(name)
        url = str(raw.get("url", ""))
        if not re.match(r"^(https?|file)://", url):
            raise ShotError(f"{where}: url must start with http://, https:// or file://")
        viewport = _number_list(raw.get("viewport", [1440, 900]), 2, f"{where}: viewport")
        scale = raw.get("scale", 2)
        if not isinstance(scale, (int, float)) or scale <= 0:
            raise ShotError(f"{where}: scale must be a positive number")
        clip = _number_list(raw.get("clip", [0, 0, viewport[0], viewport[1]]), 4, f"{where}: clip")
        if clip[2] <= 0 or clip[3] <= 0 or viewport[0] <= 0 or viewport[1] <= 0:
            raise ShotError(f"{where}: viewport and clip sizes must be positive")
        width = raw.get("width", round(clip[2] * scale))
        if not isinstance(width, int) or width <= 0:
            raise ShotError(f"{where}: width must be a positive integer")
        quality = raw.get("quality", 85)
        if not isinstance(quality, int) or not 1 <= quality <= 100:
            raise ShotError(f"{where}: quality must be 1-100")
        steps = raw.get("steps", [])
        if not isinstance(steps, list):
            raise ShotError(f"{where}: steps must be a list")
        for step in steps:
            if not isinstance(step, dict) or len(step) != 1 or next(iter(step)) not in {"click", "type", "wait"}:
                raise ShotError(f'{where}: each step is {{"click": sel}}, {{"type": [sel, text]}} or {{"wait": sel}}')
            key, value = next(iter(step.items()))
            if key == "type":
                if not (isinstance(value, list) and len(value) == 2 and all(isinstance(v, str) for v in value)):
                    raise ShotError(f'{where}: "type" takes [selector, text]')
            elif not isinstance(value, str) or not value:
                raise ShotError(f'{where}: "{key}" takes a CSS selector')
        result.append(
            {
                "name": name,
                "url": url,
                "viewport": [int(viewport[0]), int(viewport[1])],
                "scale": scale,
                "steps": steps,
                "clip": clip,
                "width": width,
                "quality": quality,
                "clip_scale": clip_scale(clip_width=clip[2], device_scale=scale, width=width),
            }
        )
    return result


def record_credit(credits: Path, asset: str, url: str, when: str) -> None:
    lines = credits.read_text(encoding="utf-8").splitlines(keepends=True) if credits.is_file() else [CREDITS_HEADER]
    lines = [line for line in lines if not line.startswith(f"{asset} |")]
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    lines.append(f"{asset} | {CREDIT_MODE} | {url} | {when}\n")
    credits.parent.mkdir(parents=True, exist_ok=True)
    credits.write_text("".join(lines), encoding="utf-8")


def browser_code(shots: list[dict[str, Any]], out_dir: Path) -> str:
    return BROWSER_CODE.replace("__SHOTS__", repr(json.dumps(shots))).replace("__OUT__", repr(str(out_dir)))


def run(shots_path: Path) -> list[dict[str, Any]]:
    shots_path = shots_path.resolve()
    shots = validate_shots(json.loads(shots_path.read_text(encoding="utf-8-sig")))
    if not shots:
        return []
    deck_dir = shots_path.parent
    out_dir = deck_dir / "assets" / "img"
    with IsolatedBrowserHarness() as browser:
        completed = browser.run_code(browser_code(shots, out_dir), timeout=120 + 60 * len(shots))
    payload = None
    for line in reversed([line.strip() for line in completed.stdout.splitlines() if line.strip()]):
        if line.startswith("{") and '"capture_screens"' in line:
            payload = json.loads(line)["capture_screens"]
            break
    if payload is None:
        raise BrowserHarnessError("browser-harness returned no capture result\n" + completed.stdout[-4000:] + completed.stderr[-4000:])
    results = []
    widths = {shot["name"]: shot["width"] for shot in shots}
    for item in payload:
        path = Path(item["path"])
        asset = path.relative_to(deck_dir).as_posix()
        record_credit(deck_dir / "assets" / "CREDITS.txt", asset, item["url"], item["captured"])
        results.append({**item, "asset": asset, "width": widths[item["name"]], "bytes": path.stat().st_size})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("shots", type=Path)
    args = parser.parse_args()
    if not args.shots.is_file():
        print(f"ERROR: file not found: {args.shots}", file=sys.stderr)
        return 2
    try:
        results = run(args.shots)
    except (ShotError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except BrowserHarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for item in results:
        print(f"{item['asset']} {item['width']} px wide, {round(item['bytes'] / 1024)} KB ← {item['url']} ({item['captured']})")
    print(f"captures: {len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
