#!/usr/bin/env python3
"""Build a horizontally navigable animated deck from a HyperFrames project.

The HyperFrames ``index.html`` remains the deterministic, linear render source.
This script creates a separate presenter-facing HTML file from the same local
scene compositions. Entering a slide restarts that scene's registered GSAP
timeline, so the live deck and rendered film share one authored scene source.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
ROOT_RE = re.compile(
    r"<(?P<tag>[a-z0-9:-]+)\b(?=[^>]*\bid=[\"']root[\"'])[^>]*>",
    re.IGNORECASE,
)
CLIP_RE = re.compile(
    r"<[a-z0-9:-]+\b(?=[^>]*\bdata-composition-src=[\"'][^\"']+[\"'])[^>]*>",
    re.IGNORECASE,
)
TEMPLATE_RE = re.compile(
    r"<template\b[^>]*>(.*?)</template>",
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_RE = re.compile(
    r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
GSAP_RE = re.compile(
    r"<script\b[^>]*\bsrc=[\"']([^\"']*gsap[^\"']*)[\"'][^>]*>\s*</script>",
    re.IGNORECASE,
)
ATTR_RE_TEMPLATE = r"\b{name}\s*=\s*[\"']([^\"']*)[\"']"


@dataclass(frozen=True)
class Scene:
    composition_id: str
    source_path: Path
    markup: str
    scripts: tuple[str, ...]


def attribute(tag: str, name: str) -> str | None:
    match = re.search(
        ATTR_RE_TEMPLATE.format(name=re.escape(name)),
        tag,
        re.IGNORECASE,
    )
    return html.unescape(match.group(1)) if match else None


def resolve_project(value: Path) -> Path:
    path = value.resolve()
    for candidate in (path, path / "animation"):
        if (
            (candidate / "index.html").is_file()
            and (candidate / "compositions").is_dir()
        ):
            return candidate
    raise FileNotFoundError(
        f"HyperFrames project not found at {path} or {path / 'animation'}"
    )


def parse_scene(project: Path, composition_id: str, source: str) -> Scene:
    source_path = (project / source).resolve()
    try:
        source_path.relative_to(project)
    except ValueError as exc:
        raise ValueError(
            f"Composition escapes the project directory: {source}"
        ) from exc
    if not source_path.is_file():
        raise FileNotFoundError(f"Missing composition: {source_path}")
    document = source_path.read_text(encoding="utf-8")
    template_match = TEMPLATE_RE.search(document)
    if not template_match:
        raise ValueError(f"Composition has no <template>: {source_path}")
    template = template_match.group(1).strip()
    scripts = tuple(
        script.strip()
        for script in SCRIPT_RE.findall(template)
        if script.strip()
    )
    if not scripts:
        raise ValueError(
            f"Composition has no local GSAP timeline script: {source_path}"
        )
    markup = SCRIPT_RE.sub("", template).strip()
    if not re.search(
        rf"\bdata-composition-id=[\"']{re.escape(composition_id)}[\"']",
        markup,
    ):
        raise ValueError(
            f"Composition id mismatch for {source_path}: {composition_id}"
        )
    if (
        f'window.__timelines["{composition_id}"]' not in "\n".join(scripts)
        and f"window.__timelines['{composition_id}']"
        not in "\n".join(scripts)
    ):
        raise ValueError(
            f"Timeline registry key is missing for {composition_id}: {source_path}"
        )
    return Scene(
        composition_id=composition_id,
        source_path=source_path,
        markup=markup,
        scripts=scripts,
    )


def parse_project(
    project: Path,
) -> tuple[str, str, int, int, list[Scene], str]:
    project = project.resolve()
    source = (project / "index.html").read_text(encoding="utf-8")
    styles = "\n".join(STYLE_RE.findall(source)).strip()
    if not styles:
        raise ValueError("HyperFrames index.html has no <style> block.")
    title_match = TITLE_RE.search(source)
    title = (
        re.sub(r"\s+", " ", html.unescape(title_match.group(1))).strip()
        if title_match
        else project.name
    )
    root_match = ROOT_RE.search(source)
    if not root_match:
        raise ValueError("HyperFrames index.html has no #root composition.")
    root_tag = root_match.group(0)
    width_value = attribute(root_tag, "data-width")
    height_value = attribute(root_tag, "data-height")
    if not width_value or not height_value:
        raise ValueError("HyperFrames #root requires data-width and data-height.")
    width = int(float(width_value))
    height = int(float(height_value))
    if width <= 0 or height <= 0:
        raise ValueError("HyperFrames canvas dimensions must be positive.")

    scenes: list[Scene] = []
    seen_ids: set[str] = set()
    for clip_tag in CLIP_RE.findall(source):
        composition_id = attribute(clip_tag, "data-composition-id")
        composition_src = attribute(clip_tag, "data-composition-src")
        if not composition_id or not composition_src:
            continue
        if composition_id in seen_ids:
            raise ValueError(f"Duplicate composition id: {composition_id}")
        seen_ids.add(composition_id)
        scenes.append(
            parse_scene(
                project,
                composition_id=composition_id,
                source=composition_src,
            )
        )
    if not scenes:
        raise ValueError("No external scene compositions were found.")
    gsap_match = GSAP_RE.search(source)
    gsap_source = (
        gsap_match.group(1)
        if gsap_match
        else "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
    )
    return title, styles, width, height, scenes, gsap_source


def presenter_css(width: int, height: int) -> str:
    return f"""
    :root {{
      --show-a: #ff78aa;
      --show-b: #75e7e0;
      --show-c: #ffd166;
      --show-night: #090711;
    }}
    html, body {{
      width: 100%;
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: var(--show-night);
    }}
    body {{ overscroll-behavior: none; }}
    #animated-presentation {{
      position: fixed;
      inset: 0;
      overflow: hidden;
      background:
        radial-gradient(circle at 18% 16%, color-mix(in srgb, var(--show-a) 24%, transparent), transparent 36%),
        radial-gradient(circle at 82% 78%, color-mix(in srgb, var(--show-b) 19%, transparent), transparent 38%),
        linear-gradient(135deg, #120b19 0%, var(--show-night) 48%, #101321 100%);
      touch-action: pan-y;
      user-select: none;
      isolation: isolate;
      transition: background 700ms ease;
    }}
    .show-lightfield {{
      position: absolute;
      inset: -15%;
      z-index: 0;
      overflow: hidden;
      pointer-events: none;
      filter: saturate(1.2);
    }}
    .show-aurora {{
      position: absolute;
      width: 54vw;
      height: 54vw;
      border-radius: 50%;
      opacity: .26;
      filter: blur(80px);
      transform: translate3d(0,0,0);
      transition:
        background-color 700ms ease,
        transform 900ms cubic-bezier(.2,.8,.2,1),
        opacity 700ms ease;
    }}
    .show-aurora--a {{
      left: -8%;
      top: -18%;
      background: var(--show-a);
    }}
    .show-aurora--b {{
      right: -10%;
      bottom: -20%;
      background: var(--show-b);
    }}
    .show-aurora--c {{
      left: 42%;
      top: 34%;
      width: 30vw;
      height: 30vw;
      background: var(--show-c);
      opacity: .12;
    }}
    #animated-presentation[data-phase="1"] .show-aurora--a,
    #animated-presentation[data-phase="4"] .show-aurora--b {{
      transform: translate3d(11vw, 7vh, 0) scale(1.12);
    }}
    #animated-presentation[data-phase="2"] .show-aurora--c,
    #animated-presentation[data-phase="5"] .show-aurora--a {{
      transform: translate3d(-8vw, -5vh, 0) scale(.9);
    }}
    .show-grain {{
      position: absolute;
      inset: 0;
      opacity: .12;
      background-image:
        linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
      background-size: 5px 5px, 7px 7px;
      mix-blend-mode: overlay;
    }}
    .show-beam {{
      position: absolute;
      left: 50%;
      top: -30%;
      width: 12%;
      height: 160%;
      opacity: .14;
      background: linear-gradient(90deg, transparent, var(--show-b), transparent);
      filter: blur(18px);
      transform: rotate(24deg);
      transition: transform 900ms cubic-bezier(.2,.8,.2,1);
    }}
    #presentation-stage {{
      position: absolute;
      left: 50%;
      top: 50%;
      z-index: 5;
      width: {width}px;
      height: {height}px;
      overflow: hidden;
      background: var(--paper, #fff);
      transform: translate(-50%, -50%) scale(1);
      transform-origin: center center;
      border: 1px solid rgba(255,255,255,.24);
      box-shadow:
        0 0 0 1px color-mix(in srgb, var(--show-a) 20%, transparent),
        0 38px 120px rgba(0,0,0,.64),
        0 0 90px color-mix(in srgb, var(--show-a) 17%, transparent);
      perspective: 2600px;
      transition: box-shadow 700ms ease;
    }}
    .stage-atmosphere {{
      position: absolute;
      inset: 0;
      z-index: 1;
      overflow: hidden;
      pointer-events: none;
    }}
    .stage-atmosphere::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(115deg, color-mix(in srgb, var(--show-a) 10%, transparent), transparent 28%),
        linear-gradient(295deg, color-mix(in srgb, var(--show-b) 9%, transparent), transparent 30%);
      mix-blend-mode: screen;
    }}
    .stage-atmosphere::after {{
      content: "";
      position: absolute;
      inset: 0;
      box-shadow:
        inset 0 0 150px rgba(7,5,12,.28),
        inset 0 0 0 2px rgba(255,255,255,.08);
    }}
    .stage-corner {{
      position: absolute;
      width: 130px;
      height: 130px;
      border-color: color-mix(in srgb, var(--show-c) 76%, white);
      opacity: .72;
    }}
    .stage-corner--tl {{
      left: 26px;
      top: 26px;
      border-left: 2px solid;
      border-top: 2px solid;
    }}
    .stage-corner--br {{
      right: 26px;
      bottom: 26px;
      border-right: 2px solid;
      border-bottom: 2px solid;
    }}
    #slide-track {{
      position: absolute;
      inset: 0;
      z-index: 2;
      transform-style: preserve-3d;
      transition: transform .72s cubic-bezier(.16,.84,.24,1);
      will-change: transform;
    }}
    .animated-slide {{
      position: absolute;
      top: 0;
      width: {width}px;
      height: {height}px;
      overflow: hidden;
      background: var(--paper, #fff);
      opacity: .2;
      filter: blur(12px) brightness(.72) saturate(.78);
      transform: translateZ(-170px) scale(.92) rotateY(-5deg);
      transform-origin: center center;
      clip-path: inset(2.5% 3.5% round 28px);
      transition:
        opacity .5s ease,
        filter .62s ease,
        transform .72s cubic-bezier(.16,.84,.24,1),
        clip-path .72s cubic-bezier(.16,.84,.24,1);
      backface-visibility: hidden;
      will-change: transform, filter, opacity, clip-path;
    }}
    .animated-slide.is-current {{
      opacity: 1;
      filter: none;
      transform: translateZ(0) scale(1) rotateY(0);
      clip-path: inset(0 round 0);
    }}
    .animated-slide.is-before {{
      transform: translate3d(55px,0,-150px) scale(.93) rotateY(4deg);
      transform-origin: right center;
    }}
    .animated-slide.is-after {{
      transform: translate3d(-55px,0,-150px) scale(.93) rotateY(-4deg);
      transform-origin: left center;
    }}
    .animated-slide[aria-hidden="true"] {{ pointer-events: none; }}
    #transition-fx {{
      position: absolute;
      inset: 0;
      z-index: 30;
      overflow: hidden;
      pointer-events: none;
      mix-blend-mode: screen;
    }}
    .fx-blade {{
      position: absolute;
      top: -18%;
      width: 32%;
      height: 136%;
      opacity: 0;
      filter: blur(1px);
      transform: skewX(-13deg);
    }}
    #fx-blade-a {{
      left: -42%;
      background: linear-gradient(90deg, transparent, var(--show-a) 38%, white 52%, transparent 100%);
    }}
    #fx-blade-b {{
      right: -42%;
      background: linear-gradient(90deg, transparent, white 42%, var(--show-b) 60%, transparent 100%);
    }}
    #fx-flare {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 42%;
      aspect-ratio: 1;
      border-radius: 50%;
      opacity: 0;
      background:
        radial-gradient(circle, white 0 2%, var(--show-c) 6%, var(--show-a) 18%, transparent 62%);
      filter: blur(10px);
      transform: translate(-50%,-50%) scale(.2);
    }}
    #fx-prism {{
      position: absolute;
      inset: -12%;
      opacity: 0;
      background:
        linear-gradient(96deg,
          transparent 24%,
          color-mix(in srgb, var(--show-a) 72%, transparent) 42%,
          rgba(255,255,255,.72) 50%,
          color-mix(in srgb, var(--show-b) 72%, transparent) 58%,
          transparent 76%);
      filter: blur(18px);
    }}
    #scene-hud {{
      position: absolute;
      left: 42px;
      right: 42px;
      bottom: 28px;
      z-index: 34;
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      color: rgba(255,255,255,.94);
      pointer-events: none;
      text-shadow: 0 2px 16px rgba(0,0,0,.56);
      mix-blend-mode: difference;
    }}
    .scene-hud__chapter {{
      display: flex;
      align-items: center;
      gap: 12px;
      font: 800 17px/1 "Pretendard Local", system-ui, sans-serif;
      letter-spacing: .18em;
      text-transform: uppercase;
    }}
    .scene-hud__chapter::before {{
      content: "";
      width: 54px;
      height: 2px;
      background: linear-gradient(90deg, var(--show-a), var(--show-c));
      box-shadow: 0 0 12px var(--show-a);
    }}
    #scene-hud-number {{
      font: 900 44px/.78 "Pretendard Local", system-ui, sans-serif;
      letter-spacing: -.05em;
    }}
    #scene-hud-total {{
      margin-left: 6px;
      opacity: .52;
      font-size: 16px;
      letter-spacing: .1em;
    }}
    .presenter-progress {{
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 50;
      height: 6px;
      background: rgba(255,255,255,.1);
      pointer-events: none;
      box-shadow: 0 -1px 20px rgba(0,0,0,.28);
    }}
    #presenter-progress-fill {{
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, var(--show-a), var(--show-b), var(--show-c));
      transform: scaleX(0);
      transform-origin: left center;
      transition: transform .36s ease;
      box-shadow: 0 0 24px var(--show-a);
    }}
    .presenter-controls {{
      position: fixed;
      right: 22px;
      bottom: 22px;
      z-index: 60;
      display: flex;
      align-items: center;
      gap: 9px;
      padding: 8px;
      border: 1px solid color-mix(in srgb, var(--show-a) 44%, rgba(255,255,255,.2));
      border-radius: 999px;
      background: linear-gradient(135deg, rgba(25,16,35,.78), rgba(8,12,22,.72));
      backdrop-filter: blur(20px) saturate(1.35);
      box-shadow:
        0 16px 46px rgba(0,0,0,.42),
        inset 0 1px rgba(255,255,255,.14),
        0 0 28px color-mix(in srgb, var(--show-a) 14%, transparent);
      opacity: 0;
      transform: translateY(10px);
      transition:
        opacity 180ms ease,
        transform 180ms ease,
        border-color 500ms ease,
        box-shadow 500ms ease;
    }}
    .presenter-controls:hover,
    .presenter-controls:focus-within {{
      opacity: 1;
      transform: translateY(0);
    }}
    .presenter-controls button {{
      min-width: 42px;
      height: 42px;
      padding: 0 13px;
      border: 0;
      border-radius: 999px;
      color: #fff;
      background: linear-gradient(145deg, rgba(255,255,255,.14), rgba(255,255,255,.06));
      font: 750 15px/1 "Pretendard Local", system-ui, sans-serif;
      cursor: pointer;
      box-shadow: inset 0 1px rgba(255,255,255,.12);
      transition: transform 160ms ease, background 160ms ease;
    }}
    .presenter-controls button:hover,
    .presenter-controls button:focus-visible {{
      outline: 2px solid var(--show-a);
      outline-offset: 2px;
      background: rgba(255,255,255,.18);
      transform: translateY(-2px);
    }}
    .presenter-controls button:disabled {{
      opacity: .36;
      cursor: default;
    }}
    #presenter-count {{
      min-width: 72px;
      color: rgba(255,255,255,.86);
      text-align: center;
      font: 760 14px/1 "Pretendard Local", system-ui, sans-serif;
      letter-spacing: .06em;
    }}
    #presenter-error {{
      position: fixed;
      left: 50%;
      top: 24px;
      z-index: 80;
      display: none;
      transform: translateX(-50%);
      padding: 12px 18px;
      border-radius: 12px;
      color: #fff;
      background: #b42318;
      font: 700 15px/1.4 system-ui, sans-serif;
    }}
    #animated-presentation[data-runtime-error="true"] #presenter-error {{
      display: block;
    }}
    @media (prefers-reduced-motion: reduce) {{
      #slide-track,
      .animated-slide,
      .show-aurora,
      .show-beam,
      #presenter-progress-fill {{
        transition: none !important;
      }}
      #transition-fx {{ display: none; }}
    }}
    @media print {{
      .presenter-controls,
      .presenter-progress,
      #presenter-error,
      .show-lightfield,
      #transition-fx,
      #scene-hud {{
        display: none !important;
      }}
    }}
"""


def presenter_runtime(width: int, height: int, count: int) -> str:
    return f"""
    (() => {{
      const deck = document.getElementById("animated-presentation");
      const stage = document.getElementById("presentation-stage");
      const track = document.getElementById("slide-track");
      const slides = Array.from(document.querySelectorAll(".animated-slide"));
      const previousButton = document.getElementById("presenter-previous");
      const nextButton = document.getElementById("presenter-next");
      const replayButton = document.getElementById("presenter-replay");
      const countLabel = document.getElementById("presenter-count");
      const progressFill = document.getElementById("presenter-progress-fill");
      const chapterLabel = document.getElementById("scene-hud-chapter");
      const sceneNumber = document.getElementById("scene-hud-number");
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
      let current = 0;
      let pendingReplay = false;
      let touchStartX = null;
      let transitionForward = null;
      let transitionBackward = null;

      const palettes = [
        ["#ff78aa", "#75e7e0", "#ffd166", "#090711"],
        ["#ff9ac5", "#9ca6ff", "#8cf0cf", "#100814"],
        ["#ffcf6e", "#ff7e9f", "#6ee7ff", "#0b0c17"],
        ["#c995ff", "#ff88b7", "#f7e27a", "#0c0917"],
        ["#75e7e0", "#ff7fa7", "#ffdc85", "#071113"],
        ["#ff6c98", "#85a8ff", "#fff0aa", "#0d0712"],
      ];
      const chapters = [
        "OPEN THE SCENT",
        "MEMBER SIGNAL",
        "SCENE OF RESCENE",
        "NIGHT BLOOM",
        "AFTER SCENT",
      ];

      function clamp(index) {{
        return Math.max(0, Math.min(slides.length - 1, index));
      }}

      function timelineFor(index) {{
        const sceneId = slides[index]?.dataset.sceneId;
        return sceneId ? window.__timelines?.[sceneId] : null;
      }}

      function resetInactive() {{
        slides.forEach((slide, index) => {{
          if (index === current) return;
          const timeline = timelineFor(index);
          if (timeline) timeline.pause(0);
        }});
      }}

      function replayCurrent() {{
        const timeline = timelineFor(current);
        if (!timeline) {{
          deck.dataset.runtimeError = "true";
          document.getElementById("presenter-error").textContent =
            `장면 타임라인을 찾을 수 없습니다: ${{slides[current]?.dataset.sceneId || "unknown"}}`;
          return false;
        }}
        deck.dataset.runtimeError = "false";
        if (reduceMotion.matches) {{
          timeline.pause(timeline.duration());
        }} else {{
          timeline.restart();
          const content = slides[current]?.querySelector(".scene-content");
          if (content) {{
            window.gsap.fromTo(
              content,
              {{ scale: 1.025, filter: "brightness(1.16) saturate(1.12)" }},
              {{
                scale: 1,
                filter: "brightness(1) saturate(1)",
                duration: .9,
                ease: "power3.out",
                clearProps: "filter",
              }}
            );
          }}
        }}
        return true;
      }}

      function chapterFor(index) {{
        const chapterIndex = Math.min(
          chapters.length - 1,
          Math.floor(
            index / Math.max(1, Math.ceil(slides.length / chapters.length))
          )
        );
        return chapters[chapterIndex];
      }}

      function applyPalette(index) {{
        const palette = palettes[index % palettes.length];
        deck.style.setProperty("--show-a", palette[0]);
        deck.style.setProperty("--show-b", palette[1]);
        deck.style.setProperty("--show-c", palette[2]);
        deck.style.setProperty("--show-night", palette[3]);
        deck.dataset.phase = String(index % palettes.length);
      }}

      function buildTransitionTimelines() {{
        transitionForward = window.gsap.timeline({{ paused: true }})
          .fromTo(
            "#fx-blade-a",
            {{ xPercent: 0, opacity: 0 }},
            {{
              xPercent: 470,
              opacity: .72,
              duration: .54,
              ease: "power3.inOut",
            }},
            0
          )
          .to(
            "#fx-blade-a",
            {{ opacity: 0, duration: .18, ease: "power2.out" }},
            .38
          )
          .fromTo(
            "#fx-prism",
            {{ xPercent: -52, opacity: 0 }},
            {{
              xPercent: 52,
              opacity: .72,
              duration: .64,
              ease: "expo.inOut",
            }},
            .03
          )
          .to("#fx-prism", {{ opacity: 0, duration: .18 }}, .48)
          .fromTo(
            "#fx-flare",
            {{ xPercent: -38, scale: .18, opacity: 0 }},
            {{
              xPercent: 34,
              scale: 1.34,
              opacity: .74,
              duration: .42,
              ease: "power2.out",
            }},
            .08
          )
          .to(
            "#fx-flare",
            {{ scale: 1.8, opacity: 0, duration: .3, ease: "power3.out" }},
            .38
          );

        transitionBackward = window.gsap.timeline({{ paused: true }})
          .fromTo(
            "#fx-blade-b",
            {{ xPercent: 0, opacity: 0 }},
            {{
              xPercent: -470,
              opacity: .72,
              duration: .54,
              ease: "power3.inOut",
            }},
            0
          )
          .to(
            "#fx-blade-b",
            {{ opacity: 0, duration: .18, ease: "power2.out" }},
            .38
          )
          .fromTo(
            "#fx-prism",
            {{ xPercent: 52, opacity: 0 }},
            {{
              xPercent: -52,
              opacity: .72,
              duration: .64,
              ease: "expo.inOut",
            }},
            .03
          )
          .to("#fx-prism", {{ opacity: 0, duration: .18 }}, .48)
          .fromTo(
            "#fx-flare",
            {{ xPercent: 38, scale: .18, opacity: 0 }},
            {{
              xPercent: -34,
              scale: 1.34,
              opacity: .74,
              duration: .42,
              ease: "power2.out",
            }},
            .08
          )
          .to(
            "#fx-flare",
            {{ scale: 1.8, opacity: 0, duration: .3, ease: "power3.out" }},
            .38
          );
      }}

      function playTransition(direction) {{
        if (reduceMotion.matches) return;
        const timeline = direction < 0 ? transitionBackward : transitionForward;
        timeline?.restart();
      }}

      function updateUi() {{
        slides.forEach((slide, index) => {{
          const active = index === current;
          slide.setAttribute("aria-hidden", active ? "false" : "true");
          slide.classList.toggle("is-current", active);
          slide.classList.toggle("is-before", index < current);
          slide.classList.toggle("is-after", index > current);
        }});
        countLabel.textContent = `${{String(current + 1).padStart(2, "0")}} / {count}`;
        chapterLabel.textContent = chapterFor(current);
        sceneNumber.textContent = String(current + 1).padStart(2, "0");
        progressFill.style.transform = `scaleX(${{(current + 1) / slides.length}})`;
        previousButton.disabled = current === 0;
        nextButton.disabled = current === slides.length - 1;
        applyPalette(current);
        const hash = `#${{current + 1}}`;
        if (location.hash !== hash) history.replaceState(null, "", hash);
      }}

      function go(index, options = {{}}) {{
        const nextIndex = clamp(Number(index) || 0);
        if (
          nextIndex === current
          && options.replay !== false
          && options.force !== true
        ) {{
          replayCurrent();
          return current;
        }}
        const previousIndex = current;
        const incoming = timelineFor(nextIndex);
        if (incoming) incoming.pause(0);
        current = nextIndex;
        pendingReplay = options.replay !== false;
        if (options.instant) {{
          track.style.transition = "none";
        }}
        track.style.transform = `translate3d(${{-current * {width}}}px, 0, 0)`;
        updateUi();
        if (!options.instant && current !== previousIndex) {{
          playTransition(current > previousIndex ? 1 : -1);
        }}
        if (options.instant || reduceMotion.matches) {{
          resetInactive();
          if (pendingReplay) replayCurrent();
          pendingReplay = false;
          requestAnimationFrame(() => {{
            track.style.transition = "";
          }});
        }}
        return current;
      }}

      function next() {{ return go(current + 1); }}
      function previous() {{ return go(current - 1); }}

      function fitStage() {{
        const scale = Math.min(
          window.innerWidth / {width},
          window.innerHeight / {height}
        );
        stage.style.transform =
          `translate(-50%, -50%) scale(${{Math.max(.05, scale)}})`;
      }}

      track.addEventListener("transitionend", (event) => {{
        if (event.target !== track || event.propertyName !== "transform") return;
        resetInactive();
        if (pendingReplay) replayCurrent();
        pendingReplay = false;
      }});
      previousButton.addEventListener("click", previous);
      nextButton.addEventListener("click", next);
      replayButton.addEventListener("click", replayCurrent);
      window.addEventListener("resize", fitStage);
      window.addEventListener("keydown", (event) => {{
        if (event.altKey || event.ctrlKey || event.metaKey) return;
        if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) {{
          event.preventDefault();
          next();
        }} else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {{
          event.preventDefault();
          previous();
        }} else if (event.key === "Home") {{
          event.preventDefault();
          go(0);
        }} else if (event.key === "End") {{
          event.preventDefault();
          go(slides.length - 1);
        }} else if (event.key.toLowerCase() === "r") {{
          event.preventDefault();
          replayCurrent();
        }} else if (event.key.toLowerCase() === "f") {{
          event.preventDefault();
          if (!document.fullscreenElement) deck.requestFullscreen?.();
          else document.exitFullscreen?.();
        }}
      }});
      deck.addEventListener("pointerdown", (event) => {{
        if (event.pointerType === "touch" || event.pointerType === "pen") {{
          touchStartX = event.clientX;
        }}
      }});
      deck.addEventListener("pointerup", (event) => {{
        if (touchStartX === null) return;
        const delta = event.clientX - touchStartX;
        touchStartX = null;
        if (Math.abs(delta) < 72) return;
        if (delta < 0) next();
        else previous();
      }});
      window.addEventListener("hashchange", () => {{
        const target = Number(location.hash.slice(1)) - 1;
        if (Number.isInteger(target)) go(target);
      }});

      window.__ptMakerPresenter = {{
        ready: false,
        get index() {{ return current; }},
        get count() {{ return slides.length; }},
        go,
        next,
        previous,
        replay: replayCurrent,
        state() {{
          const timeline = timelineFor(current);
          return {{
            index: current,
            count: slides.length,
            sceneId: slides[current]?.dataset.sceneId || null,
            timelineProgress: timeline ? timeline.progress() : null,
            runtimeError: deck.dataset.runtimeError === "true",
          }};
        }},
      }};

      window.addEventListener("load", () => {{
        if (typeof window.gsap === "undefined") {{
          deck.dataset.runtimeError = "true";
          document.getElementById("presenter-error").textContent =
            "GSAP을 불러오지 못해 장면 애니메이션을 실행할 수 없습니다.";
          return;
        }}
        fitStage();
        buildTransitionTimelines();
        const start = clamp((Number(location.hash.slice(1)) || 1) - 1);
        go(start, {{ instant: true, replay: true, force: true }});
        window.__ptMakerPresenter.ready = true;
        document.documentElement.dataset.presenterReady = "true";
      }}, {{ once: true }});
    }})();
"""


def build_document(
    title: str,
    styles: str,
    width: int,
    height: int,
    scenes: list[Scene],
    gsap_source: str,
) -> str:
    slide_markup = []
    scene_scripts = []
    for index, scene in enumerate(scenes):
        slide_markup.append(
            f"""      <section
        class="animated-slide"
        data-scene-id="{html.escape(scene.composition_id, quote=True)}"
        aria-label="슬라이드 {index + 1} / {len(scenes)}"
        aria-hidden="{'false' if index == 0 else 'true'}"
        style="left:{index * width}px"
      >
{scene.markup}
      </section>"""
        )
        for script in scene.scripts:
            scene_scripts.append(
                "    {\n"
                f"      // {scene.composition_id}\n"
                f"{script}\n"
                "    }"
            )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="pt-maker-output" content="animated-presentation">
  <title>{html.escape(title)} · 발표용</title>
  <style>
{styles}
{presenter_css(width, height)}
  </style>
</head>
<body>
  <main
    id="animated-presentation"
    data-animated-presentation="true"
    data-slide-count="{len(scenes)}"
    data-runtime-error="false"
    aria-label="{html.escape(title, quote=True)} 발표자료"
  >
    <div class="show-lightfield" aria-hidden="true">
      <i class="show-aurora show-aurora--a"></i>
      <i class="show-aurora show-aurora--b"></i>
      <i class="show-aurora show-aurora--c"></i>
      <i class="show-beam"></i>
      <i class="show-grain"></i>
    </div>
    <div id="presentation-stage">
      <div class="stage-atmosphere" aria-hidden="true">
        <i class="stage-corner stage-corner--tl"></i>
        <i class="stage-corner stage-corner--br"></i>
      </div>
      <div id="slide-track">
{chr(10).join(slide_markup)}
      </div>
      <div id="transition-fx" aria-hidden="true">
        <i id="fx-blade-a" class="fx-blade"></i>
        <i id="fx-blade-b" class="fx-blade"></i>
        <i id="fx-prism"></i>
        <i id="fx-flare"></i>
      </div>
      <div id="scene-hud" aria-hidden="true">
        <span id="scene-hud-chapter" class="scene-hud__chapter">
          OPEN THE SCENT
        </span>
        <span>
          <strong id="scene-hud-number">01</strong>
          <small id="scene-hud-total">/ {len(scenes):02d}</small>
        </span>
      </div>
    </div>
    <div class="presenter-progress" aria-hidden="true">
      <div id="presenter-progress-fill"></div>
    </div>
    <nav class="presenter-controls" aria-label="발표 탐색">
      <button id="presenter-previous" type="button" aria-label="이전 슬라이드">←</button>
      <span id="presenter-count" aria-live="polite">01 / {len(scenes):02d}</span>
      <button id="presenter-replay" type="button" aria-label="현재 애니메이션 다시 재생">다시</button>
      <button id="presenter-next" type="button" aria-label="다음 슬라이드">→</button>
    </nav>
    <div id="presenter-error" role="alert"></div>
  </main>
  <script src="{html.escape(gsap_source, quote=True)}"></script>
  <script>
    window.__timelines = window.__timelines || {{}};
{chr(10).join(scene_scripts)}
  </script>
  <script>
{presenter_runtime(width, height, len(scenes))}
  </script>
</body>
</html>
"""


def validate_document(document: str, expected_count: int) -> list[str]:
    problems: list[str] = []
    if 'data-animated-presentation="true"' not in document:
        problems.append("missing animated presentation marker")
    count = len(re.findall(r'class="animated-slide"', document))
    if count != expected_count:
        problems.append(
            f"slide count mismatch: expected {expected_count}, found {count}"
        )
    for token in (
        "window.__ptMakerPresenter",
        "timeline.restart()",
        '"ArrowRight"',
        '"ArrowLeft"',
        '"pointerup"',
        "requestFullscreen",
        "presenter-progress-fill",
    ):
        if token not in document:
            problems.append(f"missing presenter behavior: {token}")
    ids = re.findall(r'(?<![-:\w])id=["\']([^"\']+)["\']', document)
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        problems.append(f"duplicate ids: {', '.join(duplicates)}")
    return problems


def build(project_value: Path, output_value: Path | None = None) -> Path:
    project = resolve_project(project_value)
    title, styles, width, height, scenes, gsap_source = parse_project(project)
    document = build_document(
        title=title,
        styles=styles,
        width=width,
        height=height,
        scenes=scenes,
        gsap_source=gsap_source,
    )
    problems = validate_document(document, expected_count=len(scenes))
    if problems:
        raise ValueError("; ".join(problems))
    output = (
        output_value.resolve()
        if output_value is not None
        else project / "presentation.html"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    try:
        project = resolve_project(args.project)
        output = build(project, args.output)
        _, _, width, height, scenes, _ = parse_project(project)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"OK: animated presentation built "
        f"(slides={len(scenes)}, canvas={width}x{height})"
    )
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
