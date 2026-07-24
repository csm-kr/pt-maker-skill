# Animation design contract

## Canvas

- Fixed frame: `1920 × 1080`
- Safe content area: `96px` horizontal, `84px` vertical
- Default frame rate: `30fps`
- Final state is authored in CSS first; GSAP animates into that resting state.

## Visual system

- Paper: `#faf3de`
- Card: `#fffaf0`
- Ink: `#20174a`
- Accent: `#c73463`
- Signal: `#1c8b78`
- Line: `#e7dcb6`
- Headline: `88–128px`
- Body: `34–44px`
- Fine print: `24px` minimum

The template is a starting system, not a reason to repeat one layout. Keep the
token roles but vary scene composition: statement, evidence, process, contrast,
and resolve.

## Motion laws

1. Use one dominant current for the whole film.
2. Reuse only two or three transition families.
3. Enter `0.1–0.3s` after a scene starts; leave enough time to read.
4. Use a persistent carrier or matched vector to bridge important seams.
5. Animate visual properties only. Never play media imperatively.
6. Use absolute GSAP positions on one paused timeline per composition. The
   parent owns persistent carriers; each external scene owns its local build.
7. No wall clock, timers, hover, scroll, network fetch, unseeded randomness, or
   infinite repeat.
8. End every scene in a deliberate, readable pose.

Default vocabulary:

- `rise`: hierarchy reveal
- `carrier-match`: causal continuity across a seam
- `hard-resolve`: decisive chapter or conclusion cut

## Image continuity

For AI-generated sequences, lock subject identity, camera, environment, palette,
light direction, and aspect ratio. Generate frame 1 with `$imagegen`; edit the
last approved frame for each next pose and change one variable at a time.
Required files live under `assets/<sequence-id>/01.png` and continue in numeric
order. Mount every frame as a direct root-child timed `<img class="clip">` on
one image-sequence track; let HyperFrames data attributes control visibility.
Do not drive image playback with GSAP or a timer. Record transition vectors in
`motion-ledger.json`.
