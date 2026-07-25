#!/usr/bin/env python3
"""Browser QA for pt-maker's horizontally navigable animated HTML deck."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from browser_harness_runtime import BrowserHarnessError, IsolatedBrowserHarness


def qa_code(html_path: Path, screenshots_dir: Path | None) -> str:
    output = str(screenshots_dir) if screenshots_dir is not None else ""
    return f"""
new_tab("about:blank")
cdp("Emulation.setDeviceMetricsOverride", width=1920, height=1080, deviceScaleFactor=1, mobile=False)
goto_url({html_path.as_uri()!r})
if not wait_for_load(30):
    raise RuntimeError("Animated presentation did not finish loading")
if not wait_for_element("#animated-presentation .animated-slide", timeout=20, visible=True):
    raise RuntimeError("Animated presentation slides were not rendered")
ready = False
for _ in range(80):
    ready = bool(js("Boolean(window.__ptMakerPresenter?.ready)"))
    if ready:
        break
    wait(.1)
if not ready:
    raise RuntimeError("Presenter runtime did not become ready")

expected = int(js("document.querySelectorAll('.animated-slide').length"))
timeline_count = int(js("Object.keys(window.__timelines || {{}}).filter(key => key !== 'main').length"))
if expected < 1:
    raise RuntimeError("No animated slides found")
if timeline_count != expected:
    raise RuntimeError(f"Timeline count mismatch: {{timeline_count}} / {{expected}}")
if not bool(js("Array.from(document.images).every(img => img.complete && img.naturalWidth > 0)")):
    raise RuntimeError("One or more presentation images failed to load")

out = Path({output!r}) if {bool(output)!r} else None
if out:
    out.mkdir(parents=True, exist_ok=True)

def capture(name):
    if not out:
        return
    payload = cdp("Page.captureScreenshot", format="png", fromSurface=True, captureBeyondViewport=False)
    destination = out / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode(payload["data"]))

def resolve_current():
    return js('''(() => {{
      const state = window.__ptMakerPresenter.state();
      const timeline = window.__timelines?.[state.sceneId];
      if (timeline) timeline.pause(timeline.duration());
      return window.__ptMakerPresenter.state();
    }})()''')

wait(2.3)
resolve_current()
initial = js("window.__ptMakerPresenter.state()")
if initial["index"] != 0 or initial["runtimeError"]:
    raise RuntimeError(f"Initial slide state failed: {{initial}}")
capture("slide-01-resolved.png")

def profile_transition(target):
    expression = '''new Promise(resolve => {{
      const deltas = [];
      let started = 0;
      let previous = 0;
      function frame(now) {{
        if (!started) {{
          started = now;
          previous = now;
        }} else {{
          deltas.push(now - previous);
          previous = now;
        }}
        if (now - started >= 800) {{
          resolve({{
            frames: deltas.length,
            maxFrameMs: Math.max(...deltas),
            averageFrameMs:
              deltas.reduce((sum, value) => sum + value, 0) / deltas.length,
            framesOver25Ms: deltas.filter(value => value > 25).length,
            framesOver40Ms: deltas.filter(value => value > 40).length
          }});
          return;
        }}
        requestAnimationFrame(frame);
      }}
      requestAnimationFrame(frame);
      window.__ptMakerPresenter.go(TARGET);
    }})'''.replace("TARGET", str(target))
    result = cdp(
        "Runtime.evaluate",
        expression=expression,
        awaitPromise=True,
        returnByValue=True,
    )
    payload = result["result"]["value"]
    payload["family"] = js(
        "window.__ptMakerPresenter.state().transitionFamily"
    )
    return payload

performance_samples = []
if expected > 3:
    for target in [1, 2, 3, 2, 1, 0]:
        performance_samples.append(profile_transition(target))
elif expected > 2:
    for target in [1, 2, 1, 0]:
        performance_samples.append(profile_transition(target))
elif expected > 1:
    for target in [1, 0]:
        performance_samples.append(profile_transition(target))
if any(sample["framesOver40Ms"] for sample in performance_samples):
    raise RuntimeError(
        f"Transition performance exceeded 40ms: {{performance_samples}}"
    )

forward = []
forward_families = []
forward_family_by_seam = {{}}
for index in range(1, expected):
    js(f"window.__ptMakerPresenter.go({{index}})")
    wait(.56)
    state = js("window.__ptMakerPresenter.state()")
    if state["index"] != index or state["runtimeError"]:
        raise RuntimeError(f"Forward navigation failed at {{index + 1}}: {{state}}")
    family = state.get("transitionFamily")
    if not family:
        raise RuntimeError(f"Missing transition family at seam {{index}}→{{index + 1}}")
    forward.append(state["sceneId"])
    forward_families.append(family)
    forward_family_by_seam[index - 1] = family
resolve_current()
wait(.1)
capture(f"slide-{{expected:02d}}-resolved.png")

reverse = []
reverse_families = []
for index in range(expected - 2, -1, -1):
    js(f"window.__ptMakerPresenter.go({{index}})")
    wait(.56)
    state = js("window.__ptMakerPresenter.state()")
    if state["index"] != index or state["runtimeError"]:
        raise RuntimeError(f"Reverse navigation failed at {{index + 1}}: {{state}}")
    family = state.get("transitionFamily")
    expected_family = forward_family_by_seam.get(index)
    if family != expected_family:
        raise RuntimeError(
            f"Transition family changed on reverse seam {{index + 1}}↔{{index + 2}}: "
            f"{{expected_family}} -> {{family}}"
        )
    reverse.append(state["sceneId"])
    reverse_families.append(family)

required_families = {{"prism", "curtain", "aperture"}}
observed_families = set(forward_families)
if expected >= 12 and not required_families.issubset(observed_families):
    raise RuntimeError(
        f"Transition family coverage failed: {{sorted(observed_families)}}"
    )

jump_index = min(12, expected - 1)
js(f"window.__ptMakerPresenter.go({{jump_index}})")
wait(.7)
wait(2.0)
jump_before = js("window.__ptMakerPresenter.state()")
if expected >= 12 and jump_index > 1 and jump_before.get("transitionFamily") != "aperture":
    raise RuntimeError(f"Multi-slide jump must use aperture: {{jump_before}}")
js("window.__ptMakerPresenter.replay()")
wait(.12)
jump_after = js("window.__ptMakerPresenter.state()")
if jump_after["index"] != jump_index or jump_after["runtimeError"]:
    raise RuntimeError(f"Replay failed: {{jump_after}}")
if jump_after["timelineProgress"] is None or jump_after["timelineProgress"] >= jump_before["timelineProgress"]:
    raise RuntimeError(f"Replay did not restart the timeline: {{jump_before}} -> {{jump_after}}")
resolve_current()
wait(.1)
capture(f"slide-{{jump_index + 1:02d}}-resolved.png")

keyboard_start = int(js("window.__ptMakerPresenter.index"))
if keyboard_start < expected - 1:
    cdp("Input.dispatchKeyEvent", type="keyDown", key="ArrowRight", code="ArrowRight")
    cdp("Input.dispatchKeyEvent", type="keyUp", key="ArrowRight", code="ArrowRight")
    wait(.62)
    keyboard_end = int(js("window.__ptMakerPresenter.index"))
    if keyboard_end != keyboard_start + 1:
        raise RuntimeError(f"Keyboard navigation failed: {{keyboard_start}} -> {{keyboard_end}}")
else:
    keyboard_end = keyboard_start

touch_start = int(js("window.__ptMakerPresenter.index"))
if touch_start < expected - 1:
    js('''(() => {{
      const deck = document.getElementById("animated-presentation");
      deck.dispatchEvent(new PointerEvent("pointerdown", {{
        bubbles: true, pointerType: "touch", clientX: 1450
      }}));
      deck.dispatchEvent(new PointerEvent("pointerup", {{
        bubbles: true, pointerType: "touch", clientX: 350
      }}));
      return true;
    }})()''')
    wait(.62)
    touch_end = int(js("window.__ptMakerPresenter.index"))
    if touch_end != touch_start + 1:
        raise RuntimeError(f"Touch navigation failed: {{touch_start}} -> {{touch_end}}")
else:
    touch_end = touch_start

if out:
    for index in range(expected):
        js(
            f"window.__ptMakerPresenter.go({{index}}, "
            "{{instant:true,replay:false,force:true}})"
        )
        wait(.04)
        js('''(() => {{
          const track = document.getElementById("slide-track");
          const slide = document.querySelectorAll(".animated-slide")[INDEX];
          track.style.transition = "none";
          track.style.transform =
            `translate3d(${{-slide.offsetLeft}}px, 0, 0)`;
          void track.offsetWidth;
          return true;
        }})()'''.replace("INDEX", str(index)))
        resolve_current()
        wait(.04)
        capture(f"all-resolved/slide-{{index + 1:02d}}-resolved.png")

    if expected > 3:
        js(
            "window.__ptMakerPresenter.go(0, "
            "{{instant:true,replay:false,force:true}})"
        )
        wait(.06)
        js('document.getElementById("slide-track").style.transition = ""')
        resolve_current()
        for target in [1, 2, 3]:
            js(f"window.__ptMakerPresenter.go({{target}})")
            wait(.08)
            family = js(
                "window.__ptMakerPresenter.state().transitionFamily"
            )
            js(
                "window.__ptMakerPresenter.poseTransition("
                f"{{family!r}}, 1, .5)"
            )
            capture(f"transitions/{{target:02d}}-{{family}}.png")
            js(
                "window.__ptMakerPresenter.poseTransition("
                f"{{family!r}}, 1, 0)"
            )
            wait(.54)
            resolve_current()

final_state = js("window.__ptMakerPresenter.state()")
print(json.dumps({{
    "animated_presentation_qa": "pass",
    "slides": expected,
    "timelines": timeline_count,
    "forward_checked": len(forward),
    "reverse_checked": len(reverse),
    "jump_replay_checked": jump_index + 1,
    "keyboard_from_to": [keyboard_start + 1, keyboard_end + 1],
    "touch_from_to": [touch_start + 1, touch_end + 1],
    "runtime_error": final_state["runtimeError"],
    "transition_families": sorted(observed_families),
    "transition_family_forward": forward_families,
    "transition_family_reverse": reverse_families,
    "reverse_family_match": True,
    "transition_performance": {{
        "samples": len(performance_samples),
        "families": sorted(
            set(sample["family"] for sample in performance_samples)
        ),
        "sample_details": performance_samples,
        "max_frame_ms": max(
            (sample["maxFrameMs"] for sample in performance_samples),
            default=None,
        ),
        "frames_over_25ms": sum(
            sample["framesOver25Ms"] for sample in performance_samples
        ),
        "frames_over_40ms": sum(
            sample["framesOver40Ms"] for sample in performance_samples
        ),
    }},
    "screenshots": str(out) if out else None,
}}, ensure_ascii=False))
"""


def run_qa(
    html_value: Path,
    screenshots_dir: Path | None = None,
) -> dict[str, object]:
    html_path = html_value.resolve()
    if not html_path.is_file():
        raise FileNotFoundError(f"Animated presentation not found: {html_path}")
    output = screenshots_dir.resolve() if screenshots_dir else None
    with IsolatedBrowserHarness() as browser:
        result = browser.run_code(
            qa_code(html_path, output),
            timeout=240,
        )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    for line in reversed(lines):
        if line.startswith("{") and line.endswith("}"):
            payload = json.loads(line)
            if payload.get("animated_presentation_qa") == "pass":
                return payload
    raise BrowserHarnessError(
        "browser-harness did not return an animated presentation QA result\n"
        + result.stdout[-4000:]
        + result.stderr[-4000:]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--screenshots-dir", type=Path)
    args = parser.parse_args()
    try:
        result = run_qa(args.html, args.screenshots_dir)
    except (
        BrowserHarnessError,
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
