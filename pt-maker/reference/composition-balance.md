# Composition Balance Rule

Use this rule whenever designing or revising a slide deck.

## Failure Mode

A slide fails visually when content is technically readable but the composition is unbalanced:

- Too many boxes are pushed into the bottom strip.
- Korean text sits too close to a card border, footer, icon, or neighboring label.
- The center of the slide is empty while the lower third carries most of the information.
- A large image or diagram pulls attention to one side without a counterweight.
- Extra points are forced into smaller cards instead of being edited or split.
- Objects are placed by feel only, with no actual `x y w h` relationship to the slide frame.

## Required Practice

- Put the main idea near the visual center or optical center.
- Use the middle of the slide as the primary structure area, especially when there is no large photograph.
- Do not use bottom card rows as the default container for leftover content.
- Keep bottom content clearly separated from the footer. In 16:9 paged decks, leave at least `.42in` between the lowest content box and the footer zone.
- Reject any slide where text visually touches a box border or appears trapped inside a shallow card.
- Balance visual mass across the slide: image vs. text, diagram vs. caption, left vs. right.
- For every major object, record normalized `xywh` against the full slide frame: `x = left / slideWidth`, `y = top / slideHeight`, `w = width / slideWidth`, `h = height / slideHeight`.
- When a placement is psychologically important, name the intent beside the coordinate: `optical center`, `counterweight`, `quiet margin`, `tension`, or `reading path`.

## XYWH Coordinate Standard

- Frame: full 16:9 slide canvas.
- Origin: top-left.
- Values: decimals from `0.000` to `1.000`, rounded to three decimals.
- Paged decks: use `13.333in x 7.5in`.
- Percentage CSS: divide by 100.
- Safe areas may guide placement, but the recorded coordinate must still be full-slide `xywh`.

Example:

```css
.hero-copy {
  /* frame: slide; xywh: 0.065 0.213 0.390 0.427; intent: left anchor, calm reading path */
  position: absolute;
  left: .86in;
  top: 1.60in;
  width: 5.20in;
  height: 3.20in;
}

.hero-visual {
  /* frame: slide; xywh: 0.540 0.147 0.390 0.587; intent: right visual counterweight */
  position: absolute;
  left: 7.20in;
  top: 1.10in;
  width: 5.20in;
  height: 4.40in;
}
```

## Better Alternatives

- Replace four shallow bottom cards with one centered 2x2 grid.
- Replace bottom cards with a central diagram, flow, matrix, or hex map.
- Use one strong statement and one supporting visual instead of several small notes.
- Split crowded content into another slide.
- Shorten copy before reducing font size or margins.

## Layout Variation Rule

- Use variation to create rhythm across a deck: split layout, mirrored split, centered statement, matrix, timeline/flow, checklist, dashboard, image-led, or discussion/activity slide.
- Variation is only acceptable when it preserves finish quality. If it creates awkward wrapping, overflow, weak alignment, cramped cards, inconsistent hierarchy, or a footer/source collision, the slide fails.
- When content does not fit the current pattern, change the pattern before cramping the typography. Fewer cards, a wider table, a split slide, a central diagram, or an additional slide is better than a visually broken layout.
- Do not repeat one card-grid structure for too many consecutive content slides, but do not introduce variation that looks less polished than the repeated layout.

## QA Checklist

Before delivery:

1. Inspect the contact sheet at thumbnail size.
2. Confirm the viewer's eye lands near the center, not only at the bottom.
3. Confirm no text touches card edges, footers, icons, or neighboring labels.
4. Confirm each slide has balanced left/right and top/bottom visual mass.
5. Confirm major objects have `xywh` ratios that match the rendered screenshot.
6. If the lower third feels crowded, redraw the layout before exporting final PDF.
