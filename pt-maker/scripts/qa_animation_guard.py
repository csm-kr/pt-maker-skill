#!/usr/bin/env python3
"""Static preflight for a pt-maker HyperFrames animation composition.

This guard catches cheap structural and determinism failures before the real
HyperFrames browser checks. It does not replace:

  npx --yes hyperframes@0.7.70 check --snapshots

Usage:
  python3 qa_animation_guard.py path/to/animation/index.html
  python3 qa_animation_guard.py path/to/animation/index.html --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


KNOWN_ASSERTIONS = {"appearsBy", "before", "staysInFrame", "keepsMoving"}
FORBIDDEN_PATTERNS = {
    "wall-clock-date": re.compile(r"\bDate\s*\.\s*now\s*\("),
    "wall-clock-performance": re.compile(r"\bperformance\s*\.\s*now\s*\("),
    "unseeded-random": re.compile(r"\bMath\s*\.\s*random\s*\("),
    "render-time-fetch": re.compile(r"\bfetch\s*\("),
    "timer-interval": re.compile(r"\bsetInterval\s*\("),
    "timer-timeout": re.compile(r"\bsetTimeout\s*\("),
    "imperative-play": re.compile(r"\.(?:play|resume)\s*\("),
    "infinite-gsap-repeat": re.compile(r"\brepeat\s*:\s*-1\b"),
}


class CompositionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.nodes: list[dict[str, Any]] = []
        self.script_chunks: list[str] = []
        self.in_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        parent = self.stack[-1][1] if self.stack else None
        node = {
            "tag": tag,
            "attrs": attr_map,
            "parent_id": parent.get("id") if parent else None,
            "depth": len(self.stack),
        }
        self.nodes.append(node)
        self.stack.append((tag, attr_map))
        if tag == "script":
            self.in_script = True

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        parent = self.stack[-1][1] if self.stack else None
        self.nodes.append(
            {
                "tag": tag,
                "attrs": attr_map,
                "parent_id": parent.get("id") if parent else None,
                "depth": len(self.stack),
            }
        )

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_script = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.in_script:
            self.script_chunks.append(data)


def finding(code: str, message: str, severity: str = "P0") -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def number(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def selector_is_present(selector: str, html: str) -> bool:
    if re.fullmatch(r"#[\w-]+", selector):
        return bool(re.search(rf'\bid=["\']{re.escape(selector[1:])}["\']', html))
    if re.fullmatch(r"\.[\w-]+", selector):
        class_name = re.escape(selector[1:])
        return bool(
            re.search(
                rf'\bclass=["\'][^"\']*(?<![\w-]){class_name}(?![\w-])[^"\']*["\']',
                html,
            )
        )
    return True


def validate_motion_sidecar(
    path: Path,
    root_duration: float | None,
    html: str,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not path.is_file():
        return [
            finding(
                "motion-sidecar-missing",
                f"Motion assertions are required next to index.html: {path.name}",
            )
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [finding("motion-sidecar-invalid", f"Invalid motion JSON: {exc}")]
    if not isinstance(data, dict):
        return [finding("motion-sidecar-invalid", "Motion sidecar must be an object.")]
    if data.get("version") != 1:
        findings.append(finding("motion-version-invalid", "Motion sidecar version must be 1."))
    duration = data.get("duration")
    if not isinstance(duration, (int, float)):
        findings.append(finding("motion-duration-invalid", "Motion duration must be numeric."))
    elif root_duration is not None and abs(float(duration) - root_duration) > 0.001:
        findings.append(
            finding(
                "motion-duration-mismatch",
                f"Motion duration {duration} does not match root {root_duration}.",
            )
        )
    assertions = data.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        findings.append(
            finding(
                "motion-assertions-empty",
                "At least one HyperFrames motion assertion is required.",
            )
        )
        return findings
    for index, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            findings.append(
                finding("motion-assertion-invalid", f"Assertion {index + 1} is not an object.")
            )
            continue
        kind = assertion.get("kind")
        if kind not in KNOWN_ASSERTIONS:
            findings.append(
                finding(
                    "motion-kind-unsupported",
                    f"Assertion {index + 1} uses unsupported kind {kind!r}.",
                )
            )
        selectors = [
            value
            for key, value in assertion.items()
            if key in {"selector", "a", "b", "withinSelector"}
            and isinstance(value, str)
            and value
        ]
        for selector in selectors:
            if not selector_is_present(selector, html):
                findings.append(
                    finding(
                        "motion-selector-missing",
                        f"Motion assertion selector not found in HTML: {selector}",
                    )
                )
    return findings


def run_checks(html_path: Path) -> dict[str, Any]:
    html_path = html_path.resolve()
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    parser = CompositionParser()
    parser.feed(html)
    findings: list[dict[str, str]] = []

    roots = [
        node
        for node in parser.nodes
        if node["attrs"].get("data-composition-id") is not None
        and not node["attrs"].get("data-composition-src")
    ]
    if len(roots) != 1:
        findings.append(
            finding(
                "composition-root-count",
                f"Expected exactly one composition root, found {len(roots)}.",
            )
        )
        root = None
    else:
        root = roots[0]

    root_id = root["attrs"].get("id") if root else None
    composition_id = root["attrs"].get("data-composition-id") if root else None
    root_duration = number(root["attrs"].get("data-duration")) if root else None
    if root:
        for key in (
            "id",
            "data-start",
            "data-duration",
            "data-width",
            "data-height",
        ):
            if not root["attrs"].get(key):
                findings.append(
                    finding("root-attribute-missing", f"Composition root requires {key}.")
                )
        if root["attrs"].get("data-width") != "1920" or root["attrs"].get(
            "data-height"
        ) != "1080":
            findings.append(
                finding(
                    "canvas-size-invalid",
                    "Animation mode canvas must be fixed at 1920×1080.",
                )
            )
        if root_duration is None or root_duration <= 0:
            findings.append(
                finding("root-duration-invalid", "Root data-duration must be positive.")
            )

    ids: list[str] = [
        node["attrs"]["id"] for node in parser.nodes if node["attrs"].get("id")
    ]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        findings.append(
            finding("duplicate-ids", f"Duplicate element IDs: {', '.join(duplicates)}")
        )

    clips = [
        node
        for node in parser.nodes
        if "clip" in node["attrs"].get("class", "").split()
    ]
    if not clips:
        findings.append(finding("clips-missing", "At least one timed .clip is required."))
    for clip in clips:
        clip_name = clip["attrs"].get("id", "<unnamed>")
        if clip["parent_id"] != root_id:
            findings.append(
                finding(
                    "clip-not-direct-child",
                    f"Clip {clip_name} must be a direct child of the composition root.",
                )
            )
        for key in ("id", "data-start", "data-duration", "data-track-index"):
            if not clip["attrs"].get(key):
                findings.append(
                    finding(
                        "clip-attribute-missing",
                        f"Clip {clip_name} requires {key}.",
                    )
                )

    track_zero: list[tuple[float, float, str]] = []
    for clip in clips:
        if clip["attrs"].get("data-track-index") != "0":
            continue
        start = number(clip["attrs"].get("data-start"))
        duration = number(clip["attrs"].get("data-duration"))
        if start is None or duration is None or duration <= 0:
            findings.append(
                finding(
                    "clip-time-invalid",
                    f"Track-0 clip {clip['attrs'].get('id', '<unnamed>')} has invalid time.",
                )
            )
            continue
        track_zero.append((start, start + duration, clip["attrs"].get("id", "")))
    track_zero.sort()
    if not track_zero:
        findings.append(
            finding("scene-track-missing", "Animation mode requires a tiled track 0.")
        )
    else:
        if abs(track_zero[0][0]) > 0.001:
            findings.append(
                finding("scene-track-start", "Track 0 must start at composition time 0.")
            )
        for previous, current in zip(track_zero, track_zero[1:]):
            delta = current[0] - previous[1]
            if abs(delta) > 0.001:
                label = "gap" if delta > 0 else "overlap"
                findings.append(
                    finding(
                        f"scene-track-{label}",
                        f"Track 0 {label} between {previous[2]} and {current[2]}.",
                    )
                )
        if root_duration is not None and abs(track_zero[-1][1] - root_duration) > 0.001:
            findings.append(
                finding(
                    "scene-track-end",
                    "Track 0 must tile exactly to the root duration.",
                )
            )

    combined_html = html
    combined_script_chunks = list(parser.script_chunks)
    for host in parser.nodes:
        source_value = host["attrs"].get("data-composition-src")
        if not source_value:
            continue
        source_path = (html_path.parent / source_value).resolve()
        try:
            source_path.relative_to(html_path.parent)
        except ValueError:
            findings.append(
                finding(
                    "composition-source-outside-project",
                    f"Nested composition must stay inside the project: {source_value}",
                )
            )
            continue
        if not source_path.is_file():
            findings.append(
                finding(
                    "composition-source-missing",
                    f"Nested composition source does not exist: {source_value}",
                )
            )
            continue
        source_html = source_path.read_text(encoding="utf-8", errors="ignore")
        combined_html += "\n" + source_html
        source_parser = CompositionParser()
        source_parser.feed(source_html)
        combined_script_chunks.extend(source_parser.script_chunks)
        expected_id = host["attrs"].get("data-composition-id")
        source_roots = [
            node
            for node in source_parser.nodes
            if node["attrs"].get("data-composition-id")
        ]
        if len(source_roots) != 1 or source_roots[0]["attrs"].get(
            "data-composition-id"
        ) != expected_id:
            findings.append(
                finding(
                    "composition-source-id-mismatch",
                    f"{source_value} must define exactly one {expected_id!r} composition root.",
                )
            )
        source_script = "\n".join(source_parser.script_chunks)
        if not re.search(
            r"gsap\s*\.\s*timeline\s*\(\s*\{\s*paused\s*:\s*true",
            source_script,
        ):
            findings.append(
                finding(
                    "subcomposition-paused-timeline-missing",
                    f"{source_value} requires a paused GSAP timeline.",
                )
            )
        if expected_id and not re.search(
            rf'window\s*\.\s*__timelines\s*\[\s*["\']{re.escape(expected_id)}["\']\s*\]',
            source_script,
        ):
            findings.append(
                finding(
                    "subcomposition-registry-mismatch",
                    f"{source_value} must register timeline key {expected_id!r}.",
                )
            )

    script = "\n".join(combined_script_chunks)
    if not re.search(r"gsap\s*\.\s*timeline\s*\(\s*\{\s*paused\s*:\s*true", script):
        findings.append(
            finding(
                "paused-timeline-missing",
                "Create the master timeline with gsap.timeline({ paused: true }).",
            )
        )
    if composition_id and not re.search(
        rf'window\s*\.\s*__timelines\s*\[\s*["\']{re.escape(composition_id)}["\']\s*\]',
        script,
    ):
        findings.append(
            finding(
                "timeline-registry-mismatch",
                "Register the paused timeline with the composition id as its key.",
            )
        )
    for code, pattern in FORBIDDEN_PATTERNS.items():
        if pattern.search(script):
            findings.append(
                finding(code, f"Deterministic animation mode forbids pattern: {code}.")
            )

    media_tags = {"img", "video", "audio"}
    for node in parser.nodes:
        if node["tag"] not in media_tags:
            continue
        if node["parent_id"] != root_id:
            findings.append(
                finding(
                    "media-not-direct-child",
                    f"<{node['tag']}> media must be a direct child of the composition root.",
                )
            )

    sidecar = html_path.with_suffix(".motion.json")
    findings.extend(validate_motion_sidecar(sidecar, root_duration, combined_html))

    p0_count = sum(item["severity"] == "P0" for item in findings)
    p2_count = sum(item["severity"] == "P2" for item in findings)
    return {
        "animation_guard_result": "pass" if p0_count == 0 else "fail",
        "html": str(html_path),
        "motion_sidecar": str(sidecar),
        "composition_id": composition_id,
        "duration": root_duration,
        "clip_count": len(clips),
        "p0_count": p0_count,
        "p2_count": p2_count,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_checks(args.html)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"animation-guard: {result['animation_guard_result']} "
            f"(P0={result['p0_count']}, P2={result['p2_count']})"
        )
        for item in result["findings"]:
            print(f"- {item['severity']} {item['code']}: {item['message']}")
    return 0 if result["animation_guard_result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
