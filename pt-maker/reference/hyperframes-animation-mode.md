# HyperFrames animation mode

This reference applies when the user confirms `애니메이션 위주` and `pt-maker`
produces a timed HyperFrames HTML project plus a horizontally navigable
animated presentation HTML as the primary final artifact. Rendered
MP4/WebM/GIF is optional and is produced only when the user explicitly asks
for a video export. The runtime is pinned to `hyperframes@0.7.70`.

## Mode boundary

| mode | authoring runtime | primary output | interaction | render model |
|---|---|---|---|---|
| `presentation` | Reveal.js | `.html` + PDF | keyboard, fragments, branches | one slide at a time |
| `animation` | HyperFrames + paused GSAP | live animated presentation HTML + complete project; optional MP4/WebM/GIF on explicit request | horizontal navigation + timeline preview | shared scenes, separate playback shells |
| `both` | both projects | Reveal live deck + animated presentation HTML; optional video on explicit request | separate outputs | separate QA gates |

Do not use HyperFrames slideshow mode for a deliverable that must become one
continuous MP4. A slideshow contains multiple top-level compositions and the
renderer will not concatenate them into a film. Animation mode therefore uses
one root composition with end-to-end scene clips on track 0.

The live deck is not a second hand-authored scene set. Generate it from the
same root clip order and external compositions with
`build_animated_presentation.py`. The generated shell moves horizontally and
restarts the registered scene timeline whenever that slide is entered.

## Composition contract

1. Use one `1920 × 1080` root with:
   `data-composition-id`, `data-start`, `data-duration`, `data-width`,
   `data-height`, and `data-fps`.
2. Every visible timed scene is a direct root-child host with class `clip`,
   `data-composition-src="compositions/scene-*.html"`, `data-start`,
   `data-duration`, and `data-track-index`.
3. Tile primary scenes end-to-end on track 0. Persistent carriers, progress
   rails, captions, or audio may use higher tracks.
4. Write the final static pose in CSS. Animate nested scene elements inside the
   external sub-composition, never the clip host itself.
5. Create one paused timeline **per composition** and register it with the same
   composition id. The parent owns persistent carriers/progress; each scene owns
   its local build. HyperFrames nests child timelines automatically, so never
   add them manually to the parent.

```js
const tl = gsap.timeline({ paused: true });
window.__timelines = window.__timelines || {};
window.__timelines["scene-1"] = tl;
```

6. Use absolute local positions such as `.25`, not chained timing that shifts
   when an earlier tween changes.
7. Keep parent duration, tiled scene durations, and `index.motion.json` duration
   equal. Each child timeline must cover its host duration.

## Deterministic animation

Allowed:

- paused GSAP timeline controlled by HyperFrames
- transforms, opacity, color, masks, and other visual properties
- finite repeat counts
- local media files in `assets/`
- explicit timeline positions

Forbidden:

- `Date.now()`, `performance.now()`, `Math.random()`
- `fetch()` for required render content
- `setTimeout()` or `setInterval()` as an animation clock
- hover, scroll, focus, or cursor state as required content
- `.play()`/`.resume()` on the GSAP timeline or media
- `repeat: -1` and infinite CSS animation
- dynamic duration calculated after load

The renderer seeks the paused master timeline to arbitrary timestamps. The frame
at time `t` must be the same regardless of when or how often it is requested.

## Scene timing

- Estimate reading time before decoration.
- Typical scene: `2–6s`.
- Start the first meaningful entrance `0.1–0.3s` after the scene begins.
- Reveal the claim before its evidence.
- Leave a stable reading beat after the build.
- Resolve the last scene; do not loop the ending.

Use a build–breathe–resolve rhythm:

1. **Build** — reveal the claim and evidence in semantic order.
2. **Breathe** — let the audience read without gratuitous movement.
3. **Resolve** — complete the idea and hand a vector or carrier to the next scene.

## Continuity

Every important seam is one of:

- `carrier-match`: one persistent or visually matched object crosses the boundary
- `vector-match`: outgoing and incoming elements share direction and speed
- `hard-resolve`: intentional cut after an idea fully lands

Record `exit.vector`, `exit.speed`, `entry.vector`, subject identity, and camera
state in `motion-ledger.json`. Limit a film to two or three transition families.

For image sequences, use `$imagegen`:

1. Lock subject, camera, environment, palette, light, and aspect ratio.
2. Generate the first frame.
3. Use the last approved frame as the edit/reference input for the next frame.
4. Change one state variable per frame.
5. Save equal-size frames under `assets/<sequence>/01.png`.
6. Mount each frame as a direct root-child timed image clip on the same track.
   HyperFrames controls visibility; never use a timer or GSAP to play media.

```html
<img
  id="product-open-01"
  class="clip sequence-frame"
  src="assets/product-open/01.png"
  alt=""
  data-start="8"
  data-duration="0.7"
  data-track-index="4"
>
<img
  id="product-open-02"
  class="clip sequence-frame"
  src="assets/product-open/02.png"
  alt=""
  data-start="8.7"
  data-duration="0.7"
  data-track-index="4"
>
```

```css
.sequence-frame {
  position: absolute;
  inset: 150px 160px 120px;
  width: calc(100% - 320px);
  height: calc(100% - 270px);
  object-fit: contain;
}
```

If a dissolve is essential, wrap the sequence in an external nested composition
and animate nested wrappers. Do not imperatively show/hide or play the primitive
image clips from the parent script.

## Motion assertions

`index.motion.json` lives next to `index.html`:

```json
{
  "version": 1,
  "duration": 20,
  "assertions": [
    {"kind": "appearsBy", "selector": "#headline", "bySec": 0.8},
    {"kind": "before", "a": "#headline", "b": "#evidence"},
    {"kind": "staysInFrame", "selector": ".scene-content"},
    {"kind": "keepsMoving", "withinSelector": "#root", "maxStaticSec": 1.5}
  ]
}
```

Supported kinds are `appearsBy`, `before`, `staysInFrame`, and `keepsMoving`.
Use `keepsMoving` only when ongoing motion is meaningful. A progress rail is
valid; pointless drift added merely to satisfy a check is not.

## Build and QA order

```bash
python3 scripts/browser_harness_runtime.py --ensure
python3 scripts/qa_animation_guard.py animation/index.html
python3 scripts/hyperframes_mode.py lint animation
python3 scripts/hyperframes_mode.py check animation --snapshots --background
python3 scripts/hyperframes_mode.py preview animation --port 4567 --background
```

`browser-harness` background and its isolated headless Chrome are hard
dependencies for preview inspection. The bootstrap installs/registers the
skill when missing. Codex must keep `check`, `preview`, and `render` in managed
background jobs so they cannot change terminal/browser focus:

```bash
python3 scripts/hyperframes_mode.py preview animation --port 4567 --background
python3 scripts/hyperframes_mode.py check animation --snapshots --background
python3 scripts/hyperframes_mode.py status animation
python3 scripts/hyperframes_mode.py stop animation --target preview
```

Managed jobs store state and logs under `animation/.pt-maker-runtime/`. Use
`stop --target all` to stop all jobs created by this wrapper. Do not substitute
plain shell `&`/`nohup`: the wrapper validates stored PIDs and terminates the
whole child process group. Background rendering retains every approval and QA
gate.

Inspect hero snapshots and the whole timeline in the browser. Create the safe
zero-score ledger:

```bash
python3 scripts/qa_animation_score_gate.py \
  animation/index.html --print-template > animation/animation_qa_ledger.json
```

Fill the ledger only with observed evidence. The animation HTML does not require
a video render. Only when the user explicitly asks for MP4/WebM/GIF, obtain
preview approval and run:

```bash
python3 scripts/hyperframes_mode.py render animation \
  --approved \
  --qa-ledger animation/animation_qa_ledger.json \
  --quality standard --fps 30 --background \
  -o animation/renders/presentation.mp4
```

The render wrapper reruns `check --snapshots` after both gates pass.

## Live animated presentation HTML

After scene authoring is stable, build the presenter-facing deck:

```bash
python3 scripts/build_animated_presentation.py animation \
  -o animation/<topic>-발표용-v1.html
```

The generated HTML must:

- use the root clip order as the horizontal slide order;
- reuse the exact local composition markup, assets, and registered GSAP timeline;
- support left/right arrows, space, Page Up/Down, Home/End, touch swipe, replay,
  and fullscreen;
- restart the current scene timeline on forward entry, backward entry, hash
  jump, and replay;
- expose `window.__ptMakerPresenter` for background browser QA;
- respect `prefers-reduced-motion` by resolving to the final pose;
- show the current slide count and a deck progress rail.

Use `qa_animated_presentation.py` with isolated background browser-harness to
verify start→end, end→start, an arbitrary jump, replay, and at least one
keyboard and touch path. Confirm that every slide has a timeline and that the
live deck's count/order matches the HyperFrames root.

```bash
python3 scripts/qa_animated_presentation.py \
  animation/<topic>-발표용-v1.html \
  --screenshots-dir animation/renders/qa/presentation-html
```

The default final animation delivery must include the complete `animation/`
HTML project (`index.html`, live presentation HTML, local `compositions/`,
local `assets/`, motion assertions, and HyperFrames config). Include a rendered
export only when the user explicitly requested it.
Reject any final HTML project that points to a temporary path or is missing a
required local composition/asset.

After live-deck QA and any explicitly requested render, always close managed
Studio/preview resources:

```bash
python3 scripts/hyperframes_mode.py stop animation --target all
python3 scripts/hyperframes_mode.py status animation
```

Do not finish while any managed job reports `alive:true`.

## Source

Methodology and CLI contract were verified against
`heygen-com/hyperframes` commit
`688500f2d6bbe28987fd414c65a977b4eb337821`, release `0.7.70`,
licensed Apache-2.0. The local template is adapted for pt-maker rather than a
copy of HyperFrames' slideshow workflow.
