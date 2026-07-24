# Alignment And Readability Evaluation Rubric

Use this reference after the first rendered PDF/contact sheet and before final delivery.
It is platform-neutral and applies to Codex and Claude. If a multi-agent/subagent
tool is available and the user allows agent review, run a dedicated visual-alignment
reviewer. If no agent tool is available, perform the same review manually and record
the result in the build notes.

## Evidence Baseline

Use these external readability baselines when choosing font sizes:

- NDRN accessibility guidance: body text minimum is 24 pt for PowerPoint.
- UD2024 presentation guidance: heading 1 minimum 32 pt, heading 2 minimum 28 pt,
  text minimum 24 pt.
- High Point University accessibility guidance: body text minimum 24 pt and headings
  minimum 32 pt.
- WCAG 2.2 target-size guidance: interactive or dot-like target elements should be at
  least 24 by 24 CSS px when they function as selectable/visually target-like items.

Deck rule derived from those sources:

- Title/H1: normally 48-72 pt.
- Section/H2: normally 36-52 pt, never below 32 pt.
- For large-room/projector or strict accessibility delivery: body and main bullets
  normally 24-30 pt, never below 24 pt.
- For normal 1280x720 reveal HTML decks: body and main bullets normally 28-30 CSS px,
  hard floor 26 CSS px, card body 24-26 CSS px. This is the user's aesthetic default
  because forcing all body text to 32px makes slides look heavy.
- Use 20-22 CSS px only for short supporting labels, never for primary reading text.
- Source notes/fine print: avoid when possible; if used, keep 11-14 pt and visually
  separate from primary content, or 15-16 CSS px in normal HTML decks.
- Korean text needs more air than English: line-height >= 1.45 for headings/labels and
  >= 1.5 for body text.

## Required Alignment Agent Pass

After first render:

1. Render a contact sheet and full-size PNGs for any visually dense slide.
2. Run `qa_media_guard.py <html> --json` and fix any P0 before export if possible.
3. Ask a dedicated reviewer agent to inspect only alignment, visibility, and polish.
4. Provide the agent with the media guard JSON, contact sheet plus full-size PNGs of the cover, final
   slide, person/photo-led slides, real-map slides, and any diagram/table/checklist slide.
5. Ask for findings in three sections only:
   - severity-ordered issues
   - rubric improvements
   - final recheck checklist
6. Do not let the reviewer edit files unless explicitly assigned a disjoint write scope.

If no agent is available, do the same pass manually and record:

```text
alignment-review-mode: manual
reviewed-artifacts: qa_media_guard JSON, contact sheet, slide PNGs
result: pass/fail with issues fixed
```

## 100 Point Rubric

Failing any hard gate below requires another render before delivery.

### A. Readability And Scale - 25 pts

- 10 pts: H1/H2/body sizes meet the active delivery profile above.
- 5 pts: Korean body lines have enough line-height and do not feel cramped.
- 5 pts: source notes and labels are legible without competing with main content.
- 5 pts: no important text is visually smaller than nearby decorative numbers/icons.

Hard fail: body text below the active delivery profile floor, or any Korean body
paragraph looks cramped at full-slide view. Also fail if a normal HTML deck looks
visually heavy because ordinary body text was forced to 32px+ everywhere.

Additional hard fail: any text overflows, is clipped, escapes a card/table/slide,
or only fits because the font was shrunk below the active profile. If copy does not
fit, reduce text, split the slide, or redesign the layout completely.

Hard fail: any text, footer, caption, or label placed over a map, photo, screenshot,
or busy illustration lacks clear rendered contrast. Fix by moving/dimming the visual,
adding a solid or translucent complementary panel behind text, or relocating the text.

### B. Grid And Edge Alignment - 20 pts

- 5 pts: repeated headers, footers, and page numbers sit on the same coordinates.
- 5 pts: cards in the same row/column share matching x/y/width/height.
- 5 pts: left edges of related text blocks align to a visible grid.
- 5 pts: visual centers match the intended optical center, not only the mathematical
  center.

Hard fail: a row of bullets, dots, labels, or cards appears unintentionally staggered.

Hard fail: a table, matrix, checklist, card grid, or source/footer block wraps in a
way that makes the slide look broken, cheap, or misaligned. Technical readability is
not enough; the rendered PDF must look finished.

Hard fail: stale visible text remains from an earlier version, including placeholders,
old source notes, removed prompt text, duplicated labels, or text from a component that
was supposedly deleted.

### C. Diagram And Marker Accuracy - 20 pts

- 8 pts: dots/pins/number badges sit exactly on their intended path or anchor point.
- 4 pts: labels belong to the nearest visual element by proximity and alignment.
- 4 pts: visual markers have consistent size, stroke, and internal centering.
- 4 pts: arrow/path/line endpoints visually land on the target, not beside it.

Hard fail: map pins, numbered steps, or checklist dots visibly miss their targets.

Hard fail: any custom SVG/CSS/HTML diagram, flow chart, timeline, network, or triad
has not been inspected as a full-size rendered PNG/PDF page. The diagram container
must carry both `data-fullsize-qa="true"` and `data-rendered-qa="true"` only after
inspection. Missing proof blocks scoring.

Hard fail: a diagram connector, arrow, or line endpoint floats beside its intended
target, dangles without a target, cuts through text, collides with cards, or creates
an ambiguous relationship. Labels must sit inside their shapes or be clearly attached
by proximity and alignment.

Hard fail: a real geography map is an inaccurate self-drawn outline, uses invented
country/city/region shapes, lacks a cited map base, or places pins/routes/regions
without matching the underlying map. Use a web/official/public map base and draw the
presentation overlay on top.

Hard fail: a person, player, founder, product, food, landmark, logo, UI screenshot,
or other named visual subject is cropped so the face/head/identity cue/core object is
cut off or hard to recognize. `object-fit: cover` is acceptable only after rendered
QA proves the important subject remains visible.

### D. Spacing, Collision, And Safe Area - 15 pts

- 5 pts: no text touches card borders, icons, dots, or neighboring text.
- 4 pts: bottom content clears the footer zone by at least 0.42 in in paged decks.
- 3 pts: card padding is large enough for Korean ascenders/descenders and line breaks.
- 3 pts: empty space feels intentional and balanced across the slide.

Hard fail: text baseline touches a border, dot, icon, or footer.

Hard fail: body, card, chart, source, or lower-third content touches, overlaps, sits
underneath, or visually competes with the footer, source note, or page number. Treat
this as `P0 footer collision`; fix the source layout, rerender the PDF/contact sheet,
and recheck the flagged page PNGs before scoring again.

Hard fail: bottom or lower-third content spills outside the slide, overlaps another
object, touches the footer, or looks visibly compressed into the bottom edge. Fix by
widening/rebalancing the layout, reducing copy, or splitting content; do not only
shrink text.

Hard fail: Korean line breaks split a word, number/unit, proper noun, section label,
or short phrase in a way that looks accidental. Bad wrapping is a layout failure,
not a minor copy issue.

Polish fail: a heading or major sentence wraps into two lines with a very short orphan
tail. Score it as P2 when still readable, and P0 if it makes the slide look unfinished.
The preferred fixes are to widen the text region, reduce or reposition the image/map,
or shorten the phrase before shrinking below the approved type scale.

Hard fail: a Korean heading or major sentence wraps with any wrapped line, especially
the final line, of 5 Korean characters or fewer, excluding spaces and punctuation,
unless the break is clearly intentional display typography. Treat this as a layout
failure and fix the layout before reducing type size.

Polish fail: a closing/statement slide headline and subtitle are too close together.
Keep enough vertical spacing that the headline reads as the primary thought and the
subtitle as support.

Polish fail: a very large display headline sits too close to an adjacent paragraph,
subtitle, or explanatory block. Score it as P2 when hierarchy is merely weakened and
P0 when the blocks visually merge or nearly touch. Fix with grid spacing, margin, or
layout changes before shrinking the headline.

## Scored QA Loop

Use the 100-point rubric as an iteration gate, not just a final note.

1. Score the rendered PDF/contact sheet and record `qa-score`, `p0-count`, `p2-count`,
   `fixed-pages`, `recheck-pages`, and `regression-check` in build notes.
2. Build `qa_ledger.json` from the rendered QA evidence and run
   `qa_score_gate.py <html> <qa_ledger.json>`. A passing score is valid only when
   the score gate passes.
3. Any P0, `qa-score < 90`, or `qa_score_gate: fail` blocks delivery.
4. Fix the source, rerender the PDF/contact sheet, regenerate full-size PNGs for all
   user-flagged pages, and score again.
   If a user names a page number, inspect both the PDF page ordinal and any visible
   slide/footer label with that same number, because cover slides labeled `00` can
   shift the two references by one page.
5. Inspect the entire new contact sheet for regressions introduced by the fix: new
   wrapping, overflow, contrast loss, crop damage, footer collision, page-order drift,
   or broken visual rhythm.
6. Stop only when `p0-count = 0`, `qa-score >= 90`, `qa_score_gate = pass`, and
   `regression-check = pass`.
7. For final delivery after the user has reviewed the candidate, build
   `user_review_ledger.json` and run
   `qa_final_review_gate.py <html> <qa_ledger.json> <user_review_ledger.json>`.
   Final delivery is valid only when this final review gate passes.

### E. Visual Rhythm And Polish - 10 pts

- 4 pts: contact sheet has clear layout variation without breaking the system.
- 3 pts: first and final slides feel intentionally related.
- 3 pts: color and contrast prioritize legibility over decoration.

Hard fail: layout variation lowers finish quality. Repeated layouts are a rhythm
problem, but variation that causes weaker alignment, overflow, cramped text, or
unclear hierarchy is worse and must be redesigned.

### F. Delivery Evidence - 10 pts

- 3 pts: PDF page count is correct.
- 2 pts: every page is 16:9.
- 2 pts: contact sheet is generated and inspected.
- 2 pts: selected full-size pages are inspected after changes.
- 1 pt: build notes record the review mode and fixes.

Hard fail: final PDF page order is wrong, pages are duplicated/missing, or the
reviewed contact sheet is stale/not generated from the exact delivered PDF. Prefer a
numbered PDF contact sheet for final verification.

Hard fail: user-flagged pages were not exported as full-size PNGs and rechecked after
the claimed fix.

Hard fail: `qa_score_gate.py` was not run, or it failed, before reporting a final
rubric score of 90/100 or higher.

Hard fail: `qa_final_review_gate.py` was not run, or it failed, before reporting
the deck as final after user review.

## Rebuild Rule

When the alignment score is below 90/100, or any hard fail is found:

1. Fix layout in source HTML/CSS.
2. Regenerate HTML/PDF.
3. Regenerate contact sheet and selected page PNGs.
4. Run the alignment reviewer again or repeat manual review.
5. Deliver only after no hard fails remain.
