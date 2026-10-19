# Animation design contract: Tesla Roadster, unofficial summary

## Canvas

- Fixed frame: `1920 × 1080`, 30 fps, 12 scenes, 113 s in the linear HyperFrames film.
- Safe content area: `96px` left and right. Content stays between `y = 128` and `y ≈ 900`;
  the source line sits at `bottom: 92px` so it clears the presenter HUD.
- Final poses are written in CSS first; each scene's paused GSAP timeline animates into them.

## Visual system (dark taste profile)

- Stage `#0b0d12` with a 48 px grid at 3.8% white and two faint colour glows.
- Ink `#f3f1ec` (titles), soft `#c3c9d5` (body), muted `#8f98aa` (labels, sources).
- Five meaning colours, used the same way in every scene:
  - `#ffb547` amber = **주장** (Tesla or Musk said it)
  - `#35d4c7` teal = **시연** (shown live)
  - `#a7e15b` lime = **검증** (independently recorded or measured)
  - `#8db0ff` blue = **보도** (outlet reporting)
  - `#ff6b5d` coral = still missing, still a promise
- Titles use one or two accent words in those colours.
- Type: Pretendard, falling back to Apple SD Gothic Neo or Noto Sans KR. Titles 66–104 px,
  values 34–76 px, body 28–34 px, labels and sources 24 px, tags 22 px.

## Persistent frame

- Top left: kicker (scene topic).
- Top right: the status rail `주장 · 시연 · 검증 · 보도`. A chip is lit when that kind of
  evidence appears in the scene. All four light up together at the end of scene 12.
- Bottom: `Details:` source line on every scene that shows a number.

## Hero object

A generic SVG roadster in side view, facing right (the dominant current). It drives in from
the left, rides the step line as its pen in scene 4, rides the bar heads in scenes 8 and
10, turns into a dashed "not yet built" outline in scene 11, and waits in front of the
three checkpoints in scene 12. It is a drawing, not a likeness of any real car.

## Motion laws

1. One dominant current: left to right.
2. Slide-to-slide seams use the presenter's three families (`prism / curtain / aperture`),
   assigned per seam. The HyperFrames film cuts on track 0.
3. Each scene has one signature build (see `STORYBOARD.md`); six families are used.
4. Title entrances rotate between a writing wipe, a rise and a baseline lift, so no three
   scenes in a row open the same way.
5. Builds finish by 4–7 s, then the scene holds still for reading.
6. No wall clock, timers, random values, hover or scroll state, network-loaded content, or
   infinite repeats.
