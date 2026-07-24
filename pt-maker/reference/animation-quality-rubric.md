# Animation mode quality rubric

Animation mode passes at `90/100`, aims for `94+`, and fails immediately if any
P0 exists. A score without snapshot and complete timeline evidence is invalid.

## Weighted rubric

| category | points | review evidence |
|---|---:|---|
| Narrative and claims | 16 | Each scene has one claim; titles alone form a coherent arc; evidence supports the exact claim. |
| Frame design | 14 | Hierarchy, safe area, contrast, typography, composition variety, and one dominant visual per scene. |
| Motion craft | 20 | Motion reveals meaning, has a build–breathe–resolve rhythm, uses finite easing and only 2–3 transition families. |
| Seam continuity | 14 | Exit/entry vectors, carrier identity, camera state, and image-sequence identity remain coherent. |
| Timing and readability | 12 | Claims appear before evidence; reading beats are long enough; no rushed last scene or accidental dead time. |
| Accessibility and safe content | 8 | No essential content depends on audio alone; captions/labels are readable; rights and attributions are recorded. |
| Technical determinism | 16 | Static guard, HyperFrames lint/check, assertions, snapshots, fixed duration, direct clips, and reproducible seeks pass. |

## P0 failures

- Composition cannot be deterministically sought or rendered.
- Root, clip, duration, track, or timeline registry contract is broken.
- Required content is loaded by network at render time.
- Timer/wall-clock/random/interaction state controls essential animation.
- Infinite motion or imperative `.play()` is used.
- Headline, evidence, or key subject leaves the safe frame or collides.
- Text is clipped, unreadable, or appears after the scene has effectively ended.
- Scene order, claim, evidence, or CTA is missing.
- Seam causes a key subject to teleport, reverse inexplicably, or change identity.
- HyperFrames `check --snapshots` fails.
- A video render was requested, but the user has not reviewed and approved the
  full preview before render.
- The final animation package has no horizontally navigable animated
  presentation HTML, or a slide does not replay its scene timeline on re-entry.
- Keyboard/touch navigation changes the visible slide without updating the
  scene animation, slide count, or progress state.

## Review sampling

At minimum inspect:

- start, build midpoint, and resolved pose of every scene
- `0.15s` before and after every scene seam
- first and last frame
- every frame where generated-image identity changes
- the full timeline once at normal speed and once at `0.25×`
- the live presentation HTML from first→last and last→first
- one arbitrary jump plus replay on the same slide
- one keyboard path and one touch-swipe path

Do not award a perfect category score without a written observation. The ledger
template starts at zero and `pending` so missing review cannot appear as a pass.
