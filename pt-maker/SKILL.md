---
name: pt-maker
description: >-
  Create polished 발표자료 from discussions, notes, sketches, web pages,
  documents, reference decks, URLs, or research. Always begin by asking the
  user to choose one production format: HyperFrames animation, text-led, or
  image-led; use image-led when the user explicitly skips the choice. Support
  presentation mode (interactive Reveal HTML + PDF), animation mode
  (deterministic HyperFrames composition + horizontally navigable animated
  presentation HTML as the primary final artifact, with rendered video only
  when explicitly requested), and both mode.
  Require an isolated background browser-harness for preview, screenshot, and
  export QA, and bootstrap it automatically when missing. Use claim-led
  storytelling, purposeful finite motion, continuity contracts, speaker notes,
  and rubric-gated HTML/video QA. For raster generation, editing, or sequential
  frames in Codex, invoke imagegen and its built-in image_gen tool; use direct
  API/CLI only when explicitly requested or approved as fallback.
---

# pt-maker

## Required update: spacing and image decision rules
These rules override older deck-building habits whenever they conflict.

### Speaker-language and person-image saliency guardrail
Treat visible language consistency and human-subject cropping as hard QA gates.

- Match the visible deck language to the user's language and expected speaker/audience language unless the user explicitly asks otherwise. If the user speaks Korean and asks for a Korean PT, default all audience-facing labels to Korean.
- Apply this to slide titles, section/kicker labels, chart labels, brackets, scoreboards, tier lists, badges, map pins, footers, captions, and short UI-like labels. Do not leave mixed English such as `winner pick`, `market signal`, `France`, `Spain`, `FRA`, `ARG`, etc. unless it is an official source name, proper noun, model/product name, player name, or intentionally taught abbreviation.
- In a Korean deck, visible country/team names must be written in Korean. Three-letter country codes may be used only as small decorative metadata when paired with Korean names or when space makes the code clearly intentional.
- Use the same rule for any other presentation language: country/team names and explanatory labels should match the deck language unless an official English brand/name is intentionally required.
- After localization, rerender and inspect compact UI elements because translated names can be longer than three-letter codes.
- For people photos, do not ship crops that cut off faces, heads, hands holding key objects, or the obvious salient subject. Use a better source image, `object-position`, a focal crop, or `object-fit: contain` when needed.
- For player/person cards, inspect at least one full-size rendered slide for every reused crop pattern. If the cover or final slide uses a wide image crop, verify that the face and primary subject remain readable at thumbnail and full size.
- Generated or self-made visuals must also preserve the salient subject. Do not let labels, badges, dark overlays, or decorative panels cover a face or the main object.

### Narrative arc and layout variation guardrail
Treat deck rhythm as a hard design requirement, especially for promotional decks.

- Plan the slide sequence as `기-승-전-결`: opening hook, identity/build-up, proof/expansion, closing takeaway or action.
- Treat each slide as one topic. Do not make a slide explain two unrelated claims; split it or rewrite the title so the slide has a single role in the explanation flow.
- Before building, write a one-line role for each slide in the arc. The PDF should read in order without requiring presenter improvisation to connect the logic.
- Use deliberate layout variation only when it improves rhythm without breaking the deck's design system. Preserve the same typography, color tokens, footer/header logic, and spacing rules while varying object placement.
- For first/last slide variation, prefer a mirrored relationship rather than a new style. Example: if slide 1 uses `portrait photo | headline text`, the final slide may use `closing text | portrait photo`; this is allowed variation because the design language stays intact.
- Do not force variation into every slide. Use alternating split layouts, centered statement, member/grid, timeline, data cards, and final CTA only when the content supports that structure.
- Promotional decks should end with a clear synthesis, not another generic summary slide. The final slide should answer "why this matters now" or "what the audience should remember."
- During QA, inspect the contact sheet for rhythm: the eye should not see five nearly identical slides in a row, and the first/last slide should feel intentionally related but not duplicated.
- Layout variation must never lower finish quality. If a varied layout causes weaker alignment, awkward wrapping, text overflow, cramped cards, or unclear hierarchy, revert to a stronger layout or redesign it.
- Variation should be structural, not decorative: alternate between split, mirrored split, centered statement, matrix/table, flow/timeline, checklist, dashboard, and image-led layouts only when the content genuinely fits that form.
- Do not use variation as an excuse for inconsistency. Headers, page/kicker logic, type scale, color tokens, safe areas, and footer/source behavior must remain stable.
- If several slides repeat the same card grid but the copy does not fit, do not shrink the grid text. Change the layout pattern, reduce points, or split the slide while preserving polish.

### Spacing guardrail: readable but aesthetically light
Treat readable typography as a hard QA gate, but do not make every slide oversized.

- For the 1280x720 reveal canvas, use Pretendard as the default body typeface and target a lighter aesthetic scale: body and bullets normally `28-30px`, hard floor `26px`, card body `24-26px`, supporting labels `20-22px`, and source/fine-print `15-16px`. If the deck is for a large room/projector or accessibility-first delivery, raise primary body back toward `32px`.
- Body text must use `line-height >= 1.5`, normally `1.54-1.62`; dense captions, source notes, and labels must use `line-height >= 1.38`.
- Adjacent text blocks must have visible breathing room: bullet items `margin-block >= .58em`, card paragraphs `margin-block >= .46em`, and heading-to-body gaps `>= .52em`.
- If a slide feels crowded, reduce words first, split the idea into another slide second, and only then reduce font size. Do not solve crowding by tightening line-height.
- Small text is allowed only when it still looks airy: use wider line-height, shorter lines, and more surrounding whitespace.
- During visual QA, reject any slide where Korean lines visually touch, where two text blocks read as one paragraph, where a label sits too close to an icon/number, or where body text looks heavy and poster-like because everything was forced to 32px+.

### Text fit, wrapping, and layout integrity hard gate
Treat text fit as a zero-tolerance QA gate. A slide that looks pleasant in the source HTML but breaks after PDF/export is a failed deck.

- Any text that overflows its box, escapes the slide, touches a card edge, collides with another object, is clipped, or becomes visually trapped is a P0 hard fail.
- Any awkward Korean line break that splits a word, number/unit, product name, proper noun, section number, or short label in a way that looks accidental is a P0 hard fail.
- Any table, card grid, checklist, timeline, diagram label, or footer/source note whose wrapping makes the layout look misaligned, cheap, or broken is a P0 hard fail even if the text is technically readable.
- Do not “fix” overflow by only shrinking text. First reduce copy, then simplify the structure, then split the slide, and if the slide still does not fit, redesign the layout completely.
- If a row/column card layout cannot hold the text cleanly, change the layout: use fewer cards, a larger matrix, a split layout, a single diagram, or multiple slides.
- Before delivery, inspect the rendered PDF, not only the browser HTML. If the HTML looks good but the PDF/contact sheet is wrong, the deck is not done.

### Text overflow zero-score guardrail
Treat text stability as a hard fail, not a polish preference. A slide can have attractive typography and still score zero if text escapes, clips, collides, or wraps awkwardly in the rendered PDF/contact sheet.

- Reject any slide with text outside its container, clipped text, overlapping text, Korean syllables or English words broken in an unnatural place, labels touching borders/icons/footers, or a line break that makes the sentence visually unbalanced.
- QA must inspect rendered output, not only HTML/CSS. Check the contact sheet first, then full-size PNGs for dense slides, long headings, code blocks, cards, tables, diagrams, and any slide the user flagged.
- When a text defect is found, the agent must take corrective action before reporting: shorten the copy, reduce card/code/supporting text size, widen or move the container, split the slide, or simplify the layout. Do not merely list the issue as a QA note.
- Prefer deleting words and simplifying claims before shrinking below the readable floor. For dense cards/code, use the deck's proven small-content scale rather than keeping all body text at the base size.
- After every corrective action, rerender the PDF/contact sheet and recheck the affected slides. Do not deliver a deck with unresolved text overflow, clipping, or broken wrapping.
- In scoring, any unresolved text overflow/clipping/overlap/broken wrapping is `P0` and sets the deck score to `0` until fixed, regardless of overall visual style.

### Rendered micro-polish QA guardrail
Treat these as mandatory rendered-output checks, not subjective afterthoughts. The reviewer must call them out with page numbers, and the main agent must fix and rerender before delivery when they affect finish quality.

- **Bad short-line wrap**: If a heading or prominent sentence wraps into two lines where the second line is only a short tail, mark it `P2` at minimum. If the short tail makes the slide look broken or cheap, mark it `P0`. Prefer widening the text frame, reducing or moving the image/map, shortening copy, or using a slightly smaller heading within the approved scale. Do not accept an ugly two-line title just because it technically fits.
- **Five-character orphan line**: If a rendered Korean heading or prominent sentence leaves any wrapped line, especially the final line, with 5 Korean characters or fewer excluding punctuation and spaces, mark it `P0` unless the break is clearly intentional typography. Fix it by changing the layout first: widen the text region, reduce/reposition the image/map, change the grid, or shorten the phrase. Do not accept it as a font-size-only fix.
- **One-line opportunity**: If a title can naturally fit on one line by modestly reducing the visual region or widening the text region, do that before shrinking text. This is especially important for route/stage slides and activity slides.
- **Stale template or leftover copy**: Any visible text from a previous version, placeholder, old prompt, duplicated label, or removed component is a `P0` stale-content failure. Delete it and rerender.
- **Bottom spill and lower-third crowding**: Any content that exits the safe area, touches the footer, overlaps another element, or looks compressed into the bottom edge is a `P0`. Fix by expanding the content area horizontally, moving material to the right/left, increasing map/image flexibility, reducing list count, or splitting the structure. Do not solve by only shrinking text.
- **Title-to-subtitle spacing**: On closing, statement, and section slides, the main title and supporting line must have deliberate breathing room. If they look visually stuck together, mark `P2`; if they touch or undermine hierarchy, mark `P0`.
- **Large-heading neighbor spacing**: When using very large display type, the adjacent subtitle/body must not look snapped to the headline. If the headline and supporting paragraph read as one cramped block, mark it `P2`; if the hierarchy becomes unclear or the lines nearly touch, mark it `P0`. Fix with grid spacing, margin, copy position, or layout changes before reducing font size.
- **Text over image/map contrast**: Any text, footer, caption, or label placed over a map, photo, screenshot, or busy illustration must remain clearly readable in the rendered PDF. If the background image makes text hard to read, mark it `P0`. Fix by moving or dimming the visual, adding a solid/translucent complementary text panel, increasing local contrast, or relocating the text; do not rely on hope or thumbnail-only inspection.
- **Flagged-page recheck**: When a user names pages or visual defects, export full-size PNGs for those exact pages after the fix and inspect them again before reporting. The final response must mention that the flagged pages were rechecked.
- **Regression recheck**: After fixing any page, regenerate the full final PDF/contact sheet from the exact current source and inspect the whole deck for new wrapping, overflow, contrast, page-order, or visual-crop regressions. Do not deliver based only on the fixed page PNGs.

### Composition balance guardrail: do not dump content at the bottom
Treat layout balance as a hard QA gate. A slide can have enough whitespace and still fail if the visual weight is pushed to the bottom edge or one side.

- Do not use a row of small bottom cards as the default way to hold extra content. Use it only when each card has enough height, text is short, and the row does not feel like an afterthought.
- The primary message should sit near the visual center or optical center of the slide. If a slide has no large image, chart, or diagram, use the central area for the main structure rather than leaving the middle empty and crowding the bottom.
- Keep bottom content above the footer with clear separation. As a rule of thumb, leave at least `.42in` between content boxes and the footer zone in 16:9 paged decks.
- Avoid overlapping or near-overlapping boxes and Korean text. Reject any slide where a text baseline visually touches a box border, footer, card edge, icon, or neighboring label.
- Balance the visual mass: if an image sits on the right, the left should have comparable text/diagram weight; if a card stack sits on one side, the other side needs a deliberate counterweight.
- Prefer centered diagrams, two-column rhythm, or one strong statement plus one supporting visual over many small boxes.
- If content does not fit comfortably, reduce the number of boxes, merge points into a single diagram, or split the idea into another slide. Do not shrink text or compress lower margins to force it in.

### XYWH specificity guardrail: place objects deliberately
For every major slide object, decide the reference frame and record its actual `x y w h` as normalized ratios. Use this to make layout intent concrete instead of relying on vague visual feel.

- Default reference frame is the full 16:9 slide canvas, origin at top-left: `x = left / slideWidth`, `y = top / slideHeight`, `w = width / slideWidth`, `h = height / slideHeight`.
- For paged decks, use `slideWidth = 13.333in` and `slideHeight = 7.5in`. Example: `left: .86in; top: .72in; width: 5.2in; height: 4.1in` becomes `xywh: 0.065 0.096 0.390 0.547`.
- For percentage CSS, the ratio is direct: `left: 6.2%; top: 8%; width: 42%; height: 64%` becomes `xywh: 0.062 0.080 0.420 0.640`.
- If using an inner safe area, name it, but still record the full-slide ratio. Example: `frame: slide; safe-area: 0.062 0.080 0.876 0.840`.
- Add a short intent note for non-obvious placements: `intent: optical center pull`, `intent: right visual counterweight`, `intent: low-tension footer clearance`. This should capture the psychological reason for the position.
- During QA, reject placements whose recorded ratios contradict the rendered screenshot: crowded lower-third objects, off-center "centerpiece" objects, or counterweights that are too small to balance the dominant image.

Recommended CSS/layout defaults for paged decks:

```css
.slide main { display: grid; align-items: center; }
.split { align-items: center; gap: .58in; }
.cards { gap: .22in; }
.bottom-band { margin-top: .38in; margin-bottom: .52in; }
.card { min-height: .98in; padding: .22in .24in; }
```

Recommended CSS defaults for new decks:

```css
.reveal { font-size: 30px; line-height: 1.56; }
.reveal p { line-height: 1.6; margin: .5em 0; }
.reveal li { line-height: 1.55; margin: .58em 0; }
.reveal small, .source, .caption { line-height: 1.42; }
```

### Alignment and readability evaluation guardrail
Before final delivery, read and apply [reference/alignment-eval-rubric.md](reference/alignment-eval-rubric.md).

- Treat visual alignment, readable font size, and finished polish as hard QA gates.
- Use a dedicated alignment-review agent when the environment provides subagents and the user permits agent review. Give it the contact sheet plus full-size PNGs of the cover, final slide, and any diagram/table/checklist slide. It should review only alignment, visibility, and polish unless explicitly assigned a disjoint write scope.
- If no subagent is available, run the same rubric manually and record that in build notes.
- Use the web-backed readability baseline from the rubric, translated through the active delivery profile: normal HTML decks use body/bullets `28-30px` with `26px` hard floor; large-room/projector decks use the stricter PowerPoint-style `24pt` body minimum, approximately `32px` in CSS.
- Reject and rebuild any slide where numbered pins, checklist dots, arrow endpoints, card grids, or labels are visibly off their intended anchors.
- Score the deck with the 100-point rubric. If the score is below 90/100 or any hard fail appears, fix the source, rerender, regenerate the contact sheet, and repeat review before delivery.

### Mandatory PT QA iteration guardrail
Before final delivery, read and apply [reference/general-pt-making-checklist.md](reference/general-pt-making-checklist.md). This is a required process gate, not an optional review note.

- **Background browser-harness is a hard dependency for pt-maker.** Before intake/build work, run `python3 scripts/browser_harness_runtime.py --ensure`; `new_deck.py`, `export_pdf.py`, `export_pdf_shots.py`, and HTML-based `export_pptx.py` enforce the same gate. If the executable or Codex skill registration is missing, the bootstrap installs the stable `browser-harness` package through `uv tool install --python 3.12 --upgrade --force browser-harness` and writes `${CODEX_HOME:-~/.codex}/skills/browser-harness/SKILL.md` from `browser-harness skill`. If `uv` is absent, it is bootstrapped inside pt-maker's ignored `.runtime/` only.
- For browser preview, screenshot capture, HTML inspection, and CDP PDF export, use only the bundled `browser_harness_runtime.py` isolated local headless Chrome path. It creates a temporary profile and remote-debugging port, sets a task-specific `BU_NAME` and `BU_CDP_URL`, disables recording for the run, and cleans up the named daemon/process/profile. Never use the default browser-harness daemon or call `new_tab()` against the user's interactive Chrome, because the helper activates the created target and can steal application/tab focus.
- Launch the isolated browser with the platform Chrome/Chromium binary, `--headless=new`, an unused localhost `--remote-debugging-port`, and a `mktemp -d` user-data directory. Keep the browser process/session ID and temporary directory explicit. When QA/export is complete, stop the named browser-harness daemon, terminate the headless browser process, and delete only that exact temporary profile directory.
- Use the user's visible Chrome only when they explicitly ask for a visible preview or when a signed-in interactive session is indispensable. Tell the user before any focus-changing browser action. Browser Use cloud is an optional isolated fallback, but it requires configured authentication and may incur usage charges; do not start it silently.
- Keep all calls in one connection mode. After starting an isolated run, never mix its `BU_NAME`/`BU_CDP_URL` calls with the default daemon.
- Do not fall back to `browse`, Playwright, DeckTape, the Codex in-app Browser, or another browser automation path when the required background fails. Fix/install `browser-harness` or report the blocking Chrome/Chromium prerequisite.
- For animated or interactive HTML, also read [reference/html-presentation-craft.md](reference/html-presentation-craft.md), [reference/motion-continuity.md](reference/motion-continuity.md), and [reference/html-quality-rubric.md](reference/html-quality-rubric.md).
- Run `python scripts/qa_html_guard.py <final-or-candidate.html>` and `python scripts/qa_media_guard.py <final-or-candidate.html>` before PDF export and after meaningful HTML/CSS/JS/assets edits. Any P0 blocks export.
- Run `python scripts/qa_media_guard.py <final-or-candidate.html>` before PDF export and after every meaningful HTML/CSS/assets edit. Any `P0` from this script blocks export/delivery until fixed. `export_pdf.py` and `export_pdf_shots.py` also run this guard automatically and must stop on P0.
- Use `python scripts/qa_media_guard.py <html> --json` when passing results to a QA reviewer agent. The agent must treat every script `P0` as a real P0 and then verify the affected pages in rendered PDF/PNG.
- Render PDF and contact sheet before claiming the deck is done.
- After rendering the exact final PDF/contact sheet, create a final `qa_ledger.json` and run `python scripts/qa_score_gate.py <html> <qa_ledger.json>`. A deck may not report `pt-qa-result: pass`, a rubric score `>= 90`, or a final delivery candidate unless this score gate passes.
- `qa_score_gate.py` is the checklist enforcement layer: it requires media guard pass, score >= 90, P0=0, rendered PDF evidence, contact-sheet review, full-size PNG evidence, regression review, all required checklist keys marked pass, and diagram-specific checks when diagrams exist.
- After `qa_score_gate.py` passes, show the HTML/PDF candidate and QA result to the user for final review. The deck is still only a candidate at this point.
- After the user's review, create `user_review_ledger.json` and run `python scripts/qa_final_review_gate.py <html> <qa_ledger.json> <user_review_ledger.json>`. A deck may not be called final, delivered as final, or used to update pt-maker taste guidance unless this final review gate passes.
- `qa_final_review_gate.py` enforces that the candidate was reported to the user, user feedback was accepted or resolved, the deck was rechecked after user review, `qa_score_gate.py` was rerun after the review state became final, and the taste-profile update decision was reviewed with the user.
- If user review produces reusable taste guidance, propose a diff to `taste-profile.md` and/or `dark-taste-profile.md`; update those files only after explicit user confirmation, increment the profile version, and record the decision in `user_review_ledger.json`. If there is no reusable learning or the user declines, record `not_applicable` or `declined` with a reason.
- Generate the contact sheet from the exact final PDF artifact, not from cached browser screenshots, stale PNGs, or an earlier export. If page order is uncertain, generate a numbered PDF contact sheet and verify page 1..N against the intended outline.
- Inspect full-size PNGs for the cover, section openers, person/photo-led slides, real-map slides, dense diagrams/SVGs/timelines, activity/quiz slides, and final slide.
- Every custom SVG/CSS/HTML diagram, flow, timeline, network, or triad must be included in full-size rendered QA. Add `data-fullsize-qa="true"` and `data-rendered-qa="true"` to the diagram container only after inspecting the full-size rendered PNG/PDF page. Missing attributes are a blocking source-level P0.
- When the user flags a page number or footer collision, export full-size PNGs for both the PDF page ordinal and any audience-facing slide label with the same number, then inspect both before scoring. Example: if the user says page 15 and the deck has a cover labeled 00, recheck PDF page 15 and the slide whose footer says `15 / N`.
- Treat any body/card/chart/source text that touches, overlaps, sits underneath, or visually competes with the footer, source note, or page number as `P0 footer collision`. The deck cannot be exported or delivered until the source layout is changed, the PDF/contact sheet is regenerated from that exact source, and the flagged page PNGs are rechecked.
- If the environment provides agent/subagent tools, always run a dedicated QA reviewer agent before delivery. Give it the contact sheet, selected full-size PNGs, and the checklist. The reviewer must return only P0 hard fails, P2 polish candidates, 100-point score, required fixes, and recheck pages.
- Give the QA reviewer the `qa_media_guard.py` output too. If the script reports unsafe media crop or inline real-map SVG, the reviewer must inspect those pages and keep the deck failed unless the source was changed or a verified `data-crop-ok="true"` crop with `data-rendered-qa="true"` or `data-fullsize-qa="true"` full-size rendered proof exists.
- If agent tooling is unavailable, record `qa-agent: unavailable` and run the same checklist manually.
- QA is an action loop. If rendered text is too large, clipped, outside a box, badly wrapped, or visually broken, immediately edit the source deck and rerender; do not stop at diagnosis.
- Treat wrong final PDF page order, duplicated/missing pages, stale contact sheets, and HTML/PDF mismatches as P0 export failures. Fix the export path and rerender before delivery.
- Treat any P0, export/aspect-ratio failure, or score below 90/100 as a blocking failure. Fix source HTML/CSS/assets, rerender PDF/contact sheet, and run the QA checklist again.
- Use a scored QA loop for every revision: score the rendered deck on the 100-point rubric, record `qa-score`, `p0-count`, `p2-count`, `fixed-pages`, and `recheck-pages` in build notes, then run `qa_score_gate.py`. Iterate until `p0-count = 0`, `qa-score >= 90`, and `qa_score_gate: pass`. If a user flags specific pages, those pages must appear in `recheck-pages` after the fix.
- Every QA loop must include regression inspection: compare the new contact sheet against the prior accepted version or against the intended outline, then record `regression-check: pass/fail` and any newly affected pages. A failed regression check is blocking even if the originally flagged pages look fixed.
- After internal QA passes, report the QA result and provide the HTML/PDF candidate for user review before entering revision work. Treat user-requested changes as a new version and rerun the QA loop before reporting again. Before final delivery, run `qa_final_review_gate.py`; if it fails, continue the review/update/recheck loop rather than reporting final.
- Do not export PPTX by default. Export PPTX only when the user explicitly asks for PPTX or the agreed output format requires it, and only after PDF/contact sheet QA passes with no P0 and score >= 90/100.

### Image fit rubric and generation trigger
For each slide that needs an image, search web/official/public sources first and score candidate images before use.

Score each candidate from 0-10:

- Content match, 0-3: directly shows the subject, place, species, behavior, data context, or response method named on the slide.
- Evidence value, 0-2: comes from an official, primary, educational, or clearly attributable source.
- Visual clarity, 0-2: readable at slide size, not dark, blurred, over-cropped, cluttered, or watermarked. If a face, head, product, landmark, food, or map detail is important to the slide, it must remain visible in the rendered PDF.
- Layout fit, 0-2: works in the slide crop/aspect ratio without hiding the important subject. A candidate that only works by cutting off the face/head or core object scores 0 for layout fit.
- Tone fit, 0-1: supports the deck mood and does not look like generic stock filler.

Use the image when score >= 7. If the best available web image scores 4-6, prefer a simple self-made diagram/chart/SVG when the slide is explanatory. If the best available web image scores <= 5 and the slide needs a concrete visual, trigger image generation with a short note in the working log: `image-generation-trigger: best web score X/10, reason ...`.

Generated images must be clearly illustrative, not presented as documentary evidence. For factual slides, keep sourced data/text separate from generated artwork and add an asset note in `assets/CREDITS.txt`.

### Image crop and real-map overlay hard gate
Treat image subject integrity as a hard QA gate. A visually stylish crop still fails if it removes the information the slide depends on.

- For people, athletes, interviewees, founders, artists, and profile photos, the face must be intact unless the slide is explicitly about an abstract body/detail crop. Do not cut off the top of the head, eyes, mouth, chin, hands holding the key object, jersey/name cues, or the identity-bearing part of the image.
- For products, food, logos, UI screenshots, buildings, landmarks, and artifacts, the named subject must remain whole enough to recognize. If a short fixed-height `object-fit: cover` frame cuts the subject, switch to `object-fit: contain`, change `object-position`, use a wider/taller frame, choose another image, or redesign the slide.
- Hero photos may use `cover` only after rendered QA confirms the important subject is not clipped. Thumbnails, cards, portraits, documentary photos, and evidence-like visuals default to `contain` or a verified focal crop. A focal-crop override must use `data-crop-ok="true"` plus `data-rendered-qa="true"` or `data-fullsize-qa="true"` after inspecting the rendered full-size PDF/PNG.
- Real geography maps are not freehand illustration tasks. For country, city, route, travel, region, language, food, history, or geopolitics slides, first fetch an official/public/licensed map or screenshot map base, cite it in `assets/CREDITS.txt`, then draw pins, route lines, translucent regions, labels, and callouts as an overlay on top.
- Do not hand-draw country outlines, canton/state borders, coastlines, transit routes, or real geographic shapes unless the slide clearly says it is a conceptual schematic and geographic accuracy is not part of the claim.
- If no acceptable map base can be used, replace the map with a non-geographic diagram/table, ask for a source map, or state the limitation. Do not invent a map outline.
- During QA, inspect all person-photo, product-photo, landmark, screenshot, and map slides at full size. Cropped faces/subjects, inaccurate homemade maps, misplaced pins, or unreadable map labels are P0 failures until fixed.

### Visual material requirement guardrail
Apply this guardrail according to the selected production direction.

- In `image`, concrete visual material is mandatory: cover, chapter opener, key concept, evidence/example, comparison, process/timeline, product, place, and closing slides must each have a planned visual asset. Every major text slide needs at least one directly relevant image, the deck must contain multiple distinct image assets, and the visual plan must record the exact `claim → image` match. Reject generic decoration that cannot explain or evidence the adjacent copy.
- In `text`, title and copy may be the visual focus, but “줄글 위주” never means evenly distributed paragraphs. Give every slide one focal phrase, one supporting layer, and an explicit reading path. Use at least three typographic composition families across the deck—such as oversized statement, split contrast/quote, stepped phrase, metric-led copy, or editorial text grid—and never repeat the same block alignment for three consecutive slides. Emphasis must be visibly unequal: the focal phrase should dominate body copy through scale, weight, position, or color while preserving readable line lengths and whitespace.
- In `animation`, kinetic typography may be a scene's primary visual, but every scene still needs an explicit motion/composition plan and a stable readable pose. Use two or three deterministic slide-transition families and vary them by seam; for decks with 12 or more slides, default to three families unless performance or narrative continuity clearly favors two.
- Acceptable visual assets: user/original image, official/public photo, screenshot, chart/data visualization, SVG diagram/timeline/map/card grid, or approved AI-generated illustration.
- Before building an `image` deck, write a `visual plan` for every slide in the outline: asset type, source/generation path, crop/layout role, subject/focal-point safety, map-base source if relevant, and fallback. For `text`, write a layout/copy plan; for `animation`, write a motion/composition plan.
- If no suitable external image exists, build a self-made SVG/chart/diagram first for explanatory content. In `image`, announce the planned image count/purpose and actively use the `imagegen` skill's built-in `image_gen` tool without pausing for a separate approval question.
- During QA, reject two consecutive text-only content slides only in `image`. In every format, reject a slide whose title promises a visual but the body does not show one.

## Overview
사용자와 **같이 만드는** HTML-native 발표자료 스킬. `presentation`은 Reveal.js 라이브 덱과 PDF, `animation`은 HyperFrames 단일 타임라인과 가로 탐색 발표용 HTML을 기본 완성본으로 만들고, MP4/WebM/GIF는 사용자가 명시 요청한 경우에만 파생 산출물로 만든다. `both`는 정적/인터랙티브 덱과 애니메이션 HTML을 별도 QA로 만든다. 이미지 기반 `.pptx`도 사용자가 명시 요청한 경우에만 옵션으로 생성한다.

핵심 흐름은 **.html을 장면 시스템으로 구성**하는 것이다. presentation은 고정 1280×720, print/reduced-motion 정지 포즈를 쓴다. animation은 고정 1920×1080, CSS 최종 포즈, composition별 paused GSAP timeline, 직접 자식 clip host, 절대 시간값과 deterministic seek를 계약으로 삼고, 같은 composition에서 발표용 HTML을 생성한다. 이미지 생성은 보조 기능이며 Codex에서는 생성·편집·연속 프레임이 필요할 때 `$imagegen` 스킬의 built-in `image_gen` 도구를 기본 경로로 사용한다.

### Mode selection
- Runtime mode를 정하기 전에 [reference/production-direction.md](reference/production-direction.md)의 필수 포맷 질문을 완료한다.
- 사용자가 일반 PT·발표자료·슬라이드를 요청하면 `presentation`이 기본이다.
- 애니메이션 PT·넘길 때 장면 모션이 재생되는 발표 HTML을 요청하면 `animation`을 쓴다. 이 모드의 기본 최종 파일은 HTML이다.
- 자동 재생 영상·MP4·WebM·GIF를 사용자가 명시 요청하면 `animation`의 선택적 render export를 추가한다.
- Reveal 라이브 덱과 애니메이션 HTML이 모두 필요하면 `both`를 쓴다. 공유 영상은 별도 명시 요청이 있을 때만 추가한다.
- animation은 여러 composition의 HyperFrames slideshow가 아니라 **한 개의 선형 master composition**이다. slideshow를 MP4 연결본으로 오해하지 않는다.
- 생성은 `new_deck.py "<slug>" --production-direction animation|text|image [--mode presentation|animation|both]`로 시작한다. `--production-direction`은 필수다.
- animation을 만들거나 검수할 때 [reference/hyperframes-animation-mode.md](reference/hyperframes-animation-mode.md)와 [reference/animation-quality-rubric.md](reference/animation-quality-rubric.md)를 반드시 읽는다.

## 시작 프로토콜: Grill Me + 자료 인테이크
사용자가 `$pt-maker ... 만들어줘`라고 요청하면 **도구 실행, 파일 읽기, 참고자료 질문, 리서치, 개요, 폴더 생성이나 HTML 빌드보다 먼저** [reference/production-direction.md](reference/production-direction.md)의 포맷 선택 질문을 정확히 하나만 묻는다. 포맷이 확정된 뒤 `taste-profile.md`를 읽고 [reference/intake.md](reference/intake.md)의 Grill Me 모드로 들어가며 이후 질문도 한 번에 하나씩만 한다.

시작 게이트:

1. **제작 포맷 선택** — `애니메이션 위주 / 줄글 위주 / 이미지 위주` 세 가지만 제시하고 하나를 고르게 한다. 사용자가 `그냥 진행`, `알아서`, `넘어가`, `상관없음`처럼 건너뛰면 `이미지 위주`를 기본값으로 확정한다.
2. **참고자료 여부 확인** — 포맷이 정해진 뒤 "추가로 참고할 PPT/PDF/문서/스크린샷/URL/데이터가 있나요?"를 묻는다. 여기서 reference/참고자료는 사용자가 주는 원자료를 뜻한다.
3. **목적별 분류** — 받은 자료를 `content`, `evidence`, `style`, `visual-asset`, `constraint` 중 하나 이상으로 분류하고, 어떤 용도로 쓸지 사용자에게 확인한다.
4. **한 번에 하나씩 인터뷰** — 목적, 기획 방향, 타겟 독자/청중, 발표 상황, 한줄메시지, 근거/데이터, CTA를 순서대로 하나씩 좁힌다.
5. **비주얼 방향 확인** — 의도와 청중이 정리된 뒤 분위기/톤과 색상 팔레트를 묻는다. 이미지 사용량은 선택된 포맷 계약을 우선한다.
6. **인테이크 노트 확정** — `production-direction`과 자료 맵, 필수 4항목, 발표 상황, 분위기/이미지 레벨, 미해결 질문을 짧게 정리한 뒤에야 리서치/기획/빌드로 넘어간다.

사용자가 참고자료가 없다고 하면 그 사실을 인테이크 노트에 남기고 진행한다. 참고자료가 있을 것 같지만 아직 안 줬다면 `input/`에 넣거나 URL/파일명을 알려 달라고 요청한다. Color Hunt 같은 컬러 팔레트 사이트는 참고자료가 아니라 **palette source**로 별도 취급한다.

### 웹에서 찾아서 PT 만들기 모드
사용자가 "웹에서 찾아서", "리서치해서", "요즘 자료로", "최신 근거로"처럼 말해도 제작 포맷 질문을 먼저 완료한다. 그다음 [reference/research.md](reference/research.md)를 따른다. 목적·청중·한줄메시지는 짧게 확인하되, 리서치가 필요한 사실/수치/사례를 명시적으로 소스 맵에 기록한다. 슬라이드에는 출처를 과하게 노출하지 말고, 작업 노트 또는 `assets/CREDITS.txt`에 URL·접속일·사용 사실을 남긴다. 최신성이 중요한 주장은 반드시 웹으로 확인하고, 근거가 약하면 슬라이드 문장을 낮은 확신 표현으로 바꾸거나 제외한다.

## 파일 구조
스킬이 동작하는 작업 공간 레이아웃(프로젝트 루트 기준):

```
input/                          ← 사용자 참고자료 드롭 (이미지·PDF·문서)
output/NN_<slug>_<YYYYMMDD>/    ← 덱마다 폴더 (순번_주제_날짜)
  ├── deck.html · deck.pdf · assets/         ← presentation/both
  ├── animation/index.html + presentation.html + assets/  ← animation/both 기본
  ├── animation/renders/                                  ← 영상 명시 요청 시만
  ├── build-notes.md · motion-ledger.json
  └── animation/index.motion.json            ← HyperFrames assertions
archive/                        ← 작업 스크래치 격리
```

- 새 덱은 `python3 .codex/skills/pt-maker/scripts/new_deck.py "<slug>" --production-direction <animation|text|image> [--mode <mode>]`로 만든다(포맷 선택 필수, 순번=기존 최대+1, 날짜=오늘 자동).
- 덱 산출물은 **항상 그 덱 폴더 안**에 둔다. 루트에 흩뿌리지 않는다.
- 이미지는 각 runtime project의 `assets/...` 상대경로를 쓴다. `both`에서 asset을 공유하려고 project root 바깥을 참조하지 않는다.

## 입력 (Codex가 이해하는 무엇이든)
제작 포맷이 확정된 뒤 손글씨·스케치·이미지 같은 참고자료가 있을 법하면 **"인풋을 넣어 달라"고 요청**한다. 받은 뒤에는 **그걸 어떻게 쓸지를 사용자에게 물어본 다음** 진행한다 — 단정하고 바로 쓰지 않는다.

- **자유 텍스트 토론**: 주제만 주면 같이 구조를 잡아간다.
- **이미지/스케치/필기**: 첨부 이미지나 `input/` 파일을 Codex가 직접 읽는다. 받은 이미지를 **어떻게 쓸지 반드시 확인**한다:
  - **(a) 내용으로만 활용** — 손글씨·메모에 적힌 데이터·아이디어를 읽어 **정자체 슬라이드로 재구성**(깔끔하게 타이핑).
  - **(b) 원본 그대로 임베드** — 손그림 다이어그램·스케치 자체를 **폴라로이드 프레임에** 리사이즈·재생성 없이 그대로 넣음(§2).
  손그림 자체에 의미가 있으면 보통 (b), 텍스트·데이터 메모면 (a)지만 **추측하지 말고 물어본다**. 참고자료는 `input/`에 두면 거기서 읽는다.
- **웹 URL**: 사용 가능한 브라우저/웹 도구로 페이지를 가져와 자료로 활용한다.
- **문서/데이터**: 요약·재구성해서 슬라이드로.

## Workflow
덱을 만들기 전에 **`taste-profile.md`를 읽어** 톤·구조·브랜드 프리셋 기본값을 적용한다(없으면 빈 템플릿 생성). 슬라이드 품질 기준은 [reference/presentation-craft.md](reference/presentation-craft.md). 단계 순서는 상황에 맞게 바뀔 수 있다(예: 참고자료를 먼저 받으면 4가 앞당겨짐).

0. **제작 포맷 첫 질문** → 어떤 파일이나 도구도 열기 전에 [reference/production-direction.md](reference/production-direction.md)의 세 가지 포맷만 묻는다. 사용자가 건너뛰면 `image`를 적용한다.
1. **브라우저 런타임 게이트** → 포맷 확정 뒤 `python3 .codex/skills/pt-maker/scripts/browser_harness_runtime.py --ensure`를 실행한다. 실패하면 browser-harness/Chrome 의존성을 복구하기 전까지 인테이크 이후 작업을 시작하지 않는다.
2. **소스 확보** → `taste-profile.md`를 읽고 [reference/intake.md](reference/intake.md)를 따른다. 참고자료, 목적, 타겟 독자/청중, 한줄메시지, 발표 상황, 근거/데이터, CTA, 기획 방향, 분위기/톤, 색상 팔레트를 **한 번에 하나씩** 묻는다. 받은 자료는 목적별로 분류하고, 손글씨·스케치·이미지는 활용 방식((a) 내용 재구성 vs (b) 원본 임베드)을 물어본 뒤 진행한다. → 산출물: 포맷이 기록된 인테이크 노트 + 자료 맵 + 비주얼 방향.
3. **웹 리서치** → [reference/research.md](reference/research.md). 근거가 빈 항목·최신 데이터를 웹으로 보강하고, 사용자가 웹에서 찾아서 만들라고 한 경우에는 이 단계를 생략하지 않는다. 리서치 결과는 `claim / source / date / slide-use` 형태로 소스 맵에 남긴다.
4. **기획** → 스토리 짜기 전에 먼저 [reference/product-judgment.md](reference/product-judgment.md)로 **제품 판단 블록**(타겟 순간·king action·AI 특이점·신뢰 장치·반복 루프·뺄 것)을 한 번 잡는다 — 제품/AI 기능을 파는 덱이면 필수, 단순 정보 전달 덱이면 생략 가능. 그 위에서 **타겟 청중을 확정**하고 그들에게 꽂히는 한줄메시지·스토리라인·Chapter 구조를 잡는다. 슬라이드 개요를 사용자와 합의한다. `image`는 슬라이드별 제목+요점+`visual plan`, `text`는 제목+카피+레이아웃 계획, `animation`은 제목+장면+모션/컴포지션 계획을 적는다. **One idea per slide** — 제목에 "그리고/및"이 들어가면 두 장으로.
5. **구성/빌드** → 적합한 mode로 `new_deck.py`를 실행한다. presentation은 `deck.html` section을, animation은 `animation/STORYBOARD.md`와 `animation/index.html`의 timed scene clip을 수정한다. animation 장면이 확정되면 `build_animated_presentation.py`로 같은 composition을 사용하는 가로 탐색 발표 HTML을 생성하고 이를 기본 최종 파일로 삼는다. MP4/WebM/GIF render는 사용자가 영상 파일을 명시 요청한 경우에만 추가한다. 사용자가 참고자료 덱(PPT/PDF)을 주면 [reference/reference-ingest.md](reference/reference-ingest.md)로 콘텐츠+스타일을 흡수(스타일은 확인 후 취향 반영). `image`는 `visual plan`의 모든 슬롯을 관련 자산으로 채우고, `text`는 제목·카피·본문 계층을 주인공으로, `animation`은 HyperFrames 장면과 모션 계획을 중심으로 빌드한다. **빌드 내내 craft.md의 [★ 심미성 체크리스트](reference/presentation-craft.md)(가독성·통일성·균형·여백·시각자료·다양성·디테일)를 기준으로 만든다.**
6. **이미지/시각자료** → 선택한 포맷 계약을 따른다. `image` 포맷은 모든 주요 텍스트에 대응 이미지가 있고 덱 전체에 이미지가 여러 장 있어야 한다. 사용자 자산과 웹·공식·공개 자료를 먼저 찾고, 적합한 이미지가 부족하면 예상 생성 장수와 슬라이드별 목적을 알린 뒤 별도 승인 질문 없이 `$imagegen`의 built-in `image_gen`을 적극 사용한다. `text` 포맷은 제목·문장을 주인공으로 두고 이미지는 보조적으로만 쓴다. 데이터·흐름·비교는 인라인 SVG/차트/다이어그램을 우선한다. 생성 결과를 검수한 뒤 해당 덱의 `assets/`로 복사·이동한다. built-in 경로에는 API 키가 필요하지 않으며 고정 장당 비용을 안내하지 않는다. 사용자 원본 이미지는 생성하지 말고 그대로 임베드한다. 로컬 이미지 편집은 먼저 `view_image`로 대상을 확인한 뒤 `$imagegen` 편집 흐름을 따른다.
7. **필수 QA iteration + 사용자 검수 단계** → PDF/contact sheet를 렌더링하고 [reference/general-pt-making-checklist.md](reference/general-pt-making-checklist.md)와 [alignment-eval-rubric.md](reference/alignment-eval-rubric.md)로 채점한다. agent/subagent 도구가 있으면 **반드시 dedicated QA reviewer agent**를 실행해 P0/P2/100점 점수/수정 목록을 받는다(없으면 `qa-agent: unavailable` 기록 후 수동으로 동일 체크). P0가 하나라도 있거나 점수 < 90이면 source HTML/CSS/assets를 수정 → PDF/contact sheet 재렌더 → agent/manual QA를 다시 반복한다. 통과하면 먼저 QA 결과(score, P0=0, 남은 P2)와 HTML/PDF 후보를 사용자에게 보고하고, 그 다음 수정 요청 단계로 들어간다. 사용자가 수정 요청을 주면 새 버전으로 처리해 수정 → 재렌더 → QA 반복 → 재보고한다. **변경마다 덱 버전을 올린다.** 최종 마감 시 이번 덱에서 배운 취향을 **diff로 제안**하고 사용자가 확인한 것만 `taste-profile.md`에 기록(version +1). 조용히 바꾸지 않는다. 생성 이미지 개수, 최종 저장 경로, 사용 모드(`imagegen built-in` 또는 명시적으로 승인된 `fallback`)를 요약한다.

### HTML-native 완성도 확장
- 기획표에는 슬라이드별 `claim / evidence / visual plan / motion purpose / speaker note`를 추가한다. 연속 장면에는 subject·camera·environment invariants와 예상 프레임 수를 적는다.
- 빌드 전에 [reference/html-presentation-craft.md](reference/html-presentation-craft.md)를 읽고 고정 1280×720 무대, scene layers, safe zone, finite motion, print/reduced-motion 정지 포즈를 적용한다.
- presentation 모드의 fragment 모션과 animation 모드의 **슬라이드 간 전환**은 덱 전체 2~3종으로 제한한다. animation 발표 HTML은 seam마다 전환 family를 결정적으로 배정하고, 같은 seam을 역방향으로 이동할 때도 같은 family를 반대로 재생한다. 12장 이상이면 기본 생성기의 `prism / curtain / aperture` 세 family를 모두 사용하되, animation 모드의 **슬라이드 내부 빌드**는 장면 의미에 맞춰 별도로 다양화하고 같은 generic reveal을 3장 연속 반복하지 않는다. 장식용 무한 반복을 금지하고 슬라이드 이탈 시 media/sequence를 멈춘다.
- 연속 이미지는 [reference/motion-continuity.md](reference/motion-continuity.md)에 따라 `$imagegen`으로 만들고, 프레임 1 이후에는 직전 승인 프레임을 reference로 사용한다.
- 내보내기 전에 `qa_html_guard.py`와 `qa_media_guard.py`를 모두 통과한다. 렌더 후 [reference/html-quality-rubric.md](reference/html-quality-rubric.md)의 7개 영역을 채점하며 pass는 90점, 완성도 목표는 94점이다.

### HyperFrames animation mode
- [reference/hyperframes-animation-mode.md](reference/hyperframes-animation-mode.md)의 root/clip/timeline/determinism 계약을 그대로 지킨다. runtime은 `hyperframes@0.7.70`으로 pin한다.
- track 0 장면은 root duration 전체를 빈틈·겹침 없이 덮는다. persistent carrier/progress/audio는 상위 track을 쓸 수 있다.
- static end state를 CSS로 먼저 완성하고 scene을 `compositions/scene-*.html` 외부 sub-composition으로 분리한다. parent는 persistent carrier/progress만, child는 자기 nested element만 `gsap.timeline({paused:true})`에서 절대 시간으로 tween한다. 각 timeline key는 composition id와 같아야 하며 child timeline을 parent에 수동으로 붙이지 않는다.
- 각 장면에 의미 있는 signature build를 하나 정한다. `text-write`, `line-draw`, `image-reveal`, `card-assembly`, `metric-stamp`, `diagram-build`, `photo-zoom` 중 내용을 가장 잘 설명하는 방식을 쓰고, 덱 전체에는 최소 4개 build family를 배치한다. 제목/짧은 라벨은 실제 텍스트를 유지한 채 clip/mask로 써지는 듯 보이게 하고, 선·화살표·차트·점선 도식은 SVG path 또는 transform-origin이 고정된 선으로 그려지게 한다. 타자 효과를 위해 DOM 텍스트를 시간마다 바꾸거나 `letter-spacing`을 tween하지 않는다.
- 실선 SVG는 `pathLength="1"`과 stroke dash reveal을 쓴다. 점선 경로는 점선 자체의 dash offset만 움직이지 말고, 별도의 solid stroke mask를 `stroke-dasharray="1"`/`stroke-dashoffset` attribute로 그려 점선이 점진적으로 나타나게 한다. 원/타원 위 라벨은 full-size 브라우저 좌표로 중심이 경로 위에 놓이는지 수치와 화면을 모두 확인한다.
- 한 장의 시작·빌드 중간·resolved pose를 캡처해 모션이 실제 제작 과정처럼 보이는지 확인한다. 사용자 지적 페이지와 모든 custom diagram은 이 3포즈 검수를 필수로 하고, 전체 resolved contact sheet로 회귀를 확인한다.
- `Date.now`, `performance.now`, `Math.random`, timer, render-time fetch, interaction-dependent state, imperative `.play()`, infinite repeat를 금지한다.
- `index.motion.json`에 `appearsBy`, `before`, `staysInFrame`, `keepsMoving` 중 의미 있는 assertion을 둔다.
- 먼저 `qa_animation_guard.py`, 그다음 `hyperframes_mode.py lint`, `check --snapshots`, browser preview를 실행한다. 장면 확정 후 `build_animated_presentation.py animation -o animation/<주제>-발표용-vN.html`을 실행하며, 이 HTML이 animation의 기본 최종 산출물이다. 발표용 HTML은 좌우 키·스페이스·터치로 넘길 수 있고, 어떤 방향으로 재진입해도 해당 장면 타임라인을 처음부터 다시 재생해야 한다. 전체화면과 현재 장면 재생 기능도 제공한다.
- 발표용 HTML은 `qa_animated_presentation.py`의 격리 background browser-harness로 처음→끝, 끝→처음, 임의 점프, 재생 버튼, 키보드, 터치 스와이프를 검수한다. 장면 수·순서·텍스트·이미지가 렌더 master와 일치해야 한다.
- MP4/WebM/GIF는 사용자가 영상 export를 명시 요청한 경우에만 만든다. 그때만 [reference/animation-quality-rubric.md](reference/animation-quality-rubric.md) 90점/P0=0과 사용자 전체 preview 승인을 render 전 게이트로 적용하고, `hyperframes_mode.py render ... --approved --qa-ledger ...`만 사용한다. 이 wrapper가 최종 `check --snapshots`를 재실행한다.
- Codex에서는 preview/check/render에 `--background`가 필수다. wrapper가 foreground 실행을 차단한다. `status`로 PID·완료·로그를 보고, `stop --target preview|check|render|all`로 wrapper가 만든 process group만 종료한다. shell `&`/`nohup`을 임의로 쓰지 않는다. background render도 승인·QA gate를 우회하지 않는다.
- 최종 산출물과 발표용 HTML 검수가 끝나면 반드시 `hyperframes_mode.py stop animation --target all`을 실행하고 `status`에서 모든 managed job의 `alive:false`를 확인한다. HyperFrames Studio/preview 서버를 최종 납품 뒤 계속 띄워 두지 않는다.

## 취향 학습 루프
`taste-profile.md`가 취향 정본(구조·스토리 / 비주얼·브랜드 프리셋 / 어투·톤 / 안티-취향, 각 항목 `[conf:]`). 3지점에서 동작:
- **읽기**(시작): Phase 1 전에 읽어 기본값 적용. 없으면 빈 템플릿 생성.
- **흡수**(사용자 참고자료): 스타일을 추출해 "프로필에 추가할까요?" 제안 → 확인 시 반영.
- **갱신**(마감): 피드백을 diff로 제안 → **확인된 것만** 기록, version +1. silent drift 금지.

## 1. 덱 빌드
`assets/template.html`이 고정 브랜드 템플릿이다. 슬라이드 종류(클래스): `s-title` · `s-section` · `s-bullets` · `s-image` · `s-statement` · `s-end`. 블록을 복제해 내용만 채운다. `kicker`의 번호(`00 / ...`)를 순서대로 갱신. **kicker는 `.s-head`로 감싸 좌상단에 절대배치** — 콘텐츠 정렬(center/statement)과 무관하게 **번호가 모든 슬라이드 같은 자리**에 오도록 한다(마무리 s-end도 포함해 통일).

브랜드 토큰을 임의로 바꾸지 말 것 — 일관성이 핵심. 단, 사용자가 색상 변경/새 무드/팔레트 재구성을 요청했거나 기존 덱과 다른 톤이 명확히 필요하면 아래 Color Hunt 규칙으로 토큰을 재구성한다.

| 토큰 | 값 | 용도 |
|---|---|---|
| `--paper` | `#FAF3DE` | 종이 배경 |
| `--card` | `#FFFCF1` | 노트 카드 |
| `--ink` | `#20174A` | 본문 잉크 |
| `--accent` | `#C73463` | 제목·강조 (로즈) |
| `--cream-line` | `#E7DCB6` | 테두리 |
| 폰트 | Pretendard / JetBrains Mono / Nanum Pen Script | 본문 / 라벨 / 손글씨 |

### 컬러 팔레트 구성 (Color Hunt)
Color Hunt(`https://colorhunt.co/`)는 **reference 자료가 아니라 palette source**다. PPT/PDF/문서/스크린샷처럼 내용을 읽는 원자료로 취급하지 않는다. 색상 변경이나 새 무드가 필요할 때만 팔레트 영감과 후보 색을 찾는 용도로 쓴다.

- 사용자가 "색 바꿔줘", "다른 톤", "디자인 컬러 팔레트 참고"처럼 요청하면 Color Hunt에서 직접 팔레트를 찾고 덱 토큰을 재구성한다.
- 무드가 있으면 Color Hunt 태그(`Pastel`, `Vintage`, `Retro`, `Neon`, `Gold`, `Light`, `Dark`, `Warm`, `Cold`, `Nature`, `Earth`, `Night`, `Sky`, `Sea` 등)로 좁힌다. 무드가 없으면 발표 주제와 청중에 맞춰 2~3개 후보를 고른다.
- 후보 팔레트는 그대로 베끼지 말고 발표용 토큰으로 매핑한다: `paper/background`, `card/surface`, `ink/text`, `accent`, `line/border`, `muted`.
- 선택 기준은 가독성이 우선이다. `ink`는 배경과 충분히 대비되어야 하고, accent는 강조 1~2개에만 쓴다. 예쁜 팔레트라도 본문 대비가 약하면 버린다.
- 한 덱이 한 계열 색만 반복되는 one-note 팔레트가 되지 않게 한다. 사용자가 원하지 않는 한 과한 보라/남보라 그라데이션, 베이지/크림 일변도, 어두운 남색/슬레이트 일변도, 브라운/오렌지 일변도는 피한다.
- 최종 적용 전 작업 노트에 `palette source: Color Hunt`, 후보 hex, 선택 이유, 토큰 매핑을 짧게 남긴다. `taste-profile.md`에는 사용자가 확인한 경우에만 반영한다.

## 2. 사용자 이미지 임베드 (원본 보존)
**(b) 원본 임베드로 확인된 경우에만**(§입력에서 활용 방식을 물어본 뒤). `s-image`의 `<figure class="polaroid">` 안 `<img src="...">`에 원본 경로 또는 data URI를 넣는다. **리사이즈·재생성 금지**, 원본 그대로. 여러 장이면 `s-image` 슬라이드를 복제.

## 2.5 웹/스샷 쇼케이스 & 검증
- **결과물 스샷**: 배포된 웹은 필수 `browser-harness` background로 열고 로드 완료 후 스크린샷을 찍는다. SPA가 networkidle 타임아웃이면 load 완료 기준으로 확인한다.
- **세로로 긴 스샷**(풀페이지·상세페이지)은 폴라로이드 대신 **썸네일 카드** — `.thumb{height:~96px;overflow:hidden} img{object-fit:cover;object-position:top}`. 여러 프로젝트는 4열 카드 그리드로 쇼케이스.
- **슬라이드별 검증**: 브라우저에서 `Reveal.configure({transition:'none'}); Reveal.slide(N)`를 실행한 뒤 스크린샷을 찍는다. (fade 전환 중 캡처하면 이전 슬라이드가 겹쳐 보이는 잔상이 생김 → 전환을 끄면 깨끗.)
- **버전**: 표지/푸터에 `vX.Y`를 표기하고 변경마다 올린다.

## 3. 내부 이미지 생성 (Codex는 `$imagegen` 우선)
- Codex에서는 승인된 생성·편집 요청에 반드시 `$imagegen` 스킬을 적용하고 built-in `image_gen` 도구를 기본으로 사용한다. `OPENAI_API_KEY`나 `.env`를 요구하거나 `scripts/gen_image.py`를 기본 실행하지 않는다.
- 슬라이드별로 서로 다른 자산이 필요하면 자산마다 별도 built-in 호출을 사용한다. 생성 결과를 눈으로 검수하고, 선택본을 `$CODEX_HOME/generated_images/...`에만 남기지 말고 `output/NN_slug_date/assets/`로 복사·이동한다. 기존 파일을 덮어쓰라는 명시가 없으면 `hero-v2.png`처럼 버전 파일명을 사용한다.
- 편집 대상이 로컬 파일이면 먼저 `view_image`로 확인한 뒤 `$imagegen` 편집 흐름을 따른다. 투명 배경은 `$imagegen`의 built-in-first 크로마키 제거 규칙을 따르고, true native transparency가 필요한 CLI 폴백은 사용자 확인 전 실행하지 않는다.
- 프롬프트에는 현재 활성 팔레트, 슬라이드 용도, 구도, 피사체 보존, 금지 요소를 포함한다. 생성 이미지는 사실 증거가 아니라 일러스트로 표시하고 `assets/CREDITS.txt`에 생성 자산임을 기록한다.
- built-in 도구가 실패하거나 unavailable이면 API/CLI 폴백이 있음을 설명하고, 사용자가 명시적으로 승인한 경우에만 `$imagegen` 스킬의 fallback CLI 절차를 따른다. 이 경우에만 `OPENAI_API_KEY`가 필요하다.
- `scripts/gen_image.py`, `env.example`, [reference/apiyi.md](reference/apiyi.md)는 비-Codex 호환 또는 사용자가 직접 API 방식을 명시한 레거시 경로다. Codex 기본 경로로 사용하지 않는다.

### 연속 이미지 → HTML 애니메이션
- 먼저 subject identity, camera, environment, palette, motion path, invariants, 3~6장 storyboard를 고정하고 사용자 승인을 받는다.
- 프레임 1은 새로 만들고, 프레임 2부터는 직전 승인 프레임을 reference/edit 입력으로 사용한다. 바뀌는 것은 한 번에 하나만 지시한다.
- 모든 프레임은 같은 크기로 `assets/<sequence>/01.png` 형태로 저장한다. 실패 프레임을 다음 reference로 쓰지 않는다.
- `.image-sequence`에 `data-sequence-id`, `data-fps`, `data-loop="false"`, `data-print-frame`, `aria-label`을 둔다.
- 일반 화면에서는 유한 재생, 슬라이드 이탈 시 정지·reset, reduced-motion/PDF에서는 지정 정지 프레임이 기본이다.
- 중요 seam은 `motion-ledger.json`에 exit/entry vector, speed, identity match를 기록하고 full-size로 확인한다. 세부 절차는 [reference/motion-continuity.md](reference/motion-continuity.md).

## 4. 내보내기
```bash
# 0) 작업본 deck.html → 주제+버전 이름으로 확정(rename). 같은 폴더라 assets 상대경로 안 깨짐.
#    (PowerShell)  Rename-Item output/NN_slug_date/deck.html "<주제>v<N>.html"
mv output/NN_slug_date/deck.html "output/NN_slug_date/<주제>v<N>.html"
# 1) 그 html에서 PDF 생성 — deck.pdf 말고 같은 주제+버전 이름으로.
python scripts/qa_html_guard.py "output/NN_slug_date/<주제>v<N>.html"                          # HTML/motion/a11y/sequence P0 guard
python scripts/qa_media_guard.py "output/NN_slug_date/<주제>v<N>.html"                         # media crop/map P0 guard
python scripts/export_pdf.py "output/NN_slug_date/<주제>v<N>.html" "output/NN_slug_date/<주제>v<N>.pdf"        # 기본: print-pdf
python scripts/export_pdf_shots.py "output/NN_slug_date/<주제>v<N>.html" "output/NN_slug_date/<주제>v<N>.pdf"   # 화면과 1:1(스샷 합치기)
python scripts/verify_pdf.py "output/NN_slug_date/<주제>v<N>.pdf"                                              # bleed 검증(콘택트 시트) → Read로 확인
# 2) 렌더 QA 후 점수 게이트 — qa_ledger.json 작성 후 통과해야 pass/90점 이상 보고 가능.
python scripts/qa_score_gate.py "output/NN_slug_date/<주제>v<N>.html" "output/NN_slug_date/qa_ledger.json"
# 3) 사용자 최종 리뷰 후 최종 게이트. user_review_ledger.json 작성 후 통과해야 final delivery 가능.
python scripts/qa_final_review_gate.py "output/NN_slug_date/<주제>v<N>.html" "output/NN_slug_date/qa_ledger.json" "output/NN_slug_date/user_review_ledger.json"

# 선택) 사용자가 PPTX를 명시 요청한 경우에만, PDF/contact sheet QA 통과 후 생성.
python scripts/export_pptx.py "output/NN_slug_date/<주제>v<N>.html" "output/NN_slug_date/<주제>v<N>.pptx"      # 정렬 보존용 이미지 기반 PPTX
```
- **파일명** — 산출물(`.html`·`.pdf`)은 `deck.*`가 아니라 **주제+버전**(`<주제>v<N>.html`/`.pdf`, 공백 없이)으로 저장한다. **`deck.html`을 그대로 남기지 않는다** — 작업 중엔 `deck.html`을 편집하고, **마감 때 위 0)단계로 rename**해 `.html`·`.pdf`가 같은 이름이 되게 한다. 표지 푸터의 `vN` 표기와 파일명 버전을 일치시킨다.
- **.html과 .pdf 줄간격이 다를 때** — reveal `?print-pdf`(pdf.css + Chromium 인쇄 엔진 + 폰트 로드 타이밍)는 화면(paper.css)보다 줄간격이 좁게 나올 수 있다. 화면 그대로가 필요하면 **`export_pdf_shots.py`**(브라우저로 각 슬라이드 고해상도 스샷 → pymupdf로 16:9 PDF 합치기)로 만들면 **HTML과 1:1**.
- **PPTX export (optional, not default)** — `export_pptx.py`는 시각 정렬을 우선한다. HTML 또는 PDF를 슬라이드별 PNG로 렌더링한 뒤 각 PPTX 슬라이드에 16:9 이미지 한 장으로 넣는다. 텍스트/도형 편집성은 포기한다. 기본 산출물에는 포함하지 말고, 사용자가 PPTX를 명시 요청했거나 합의한 산출물에 PPTX가 있을 때만 생성한다. 편집 가능한 PPTX가 필요하면 별도 네이티브 PPTX 빌드 플로우로 다룬다. **PPTX는 PDF/contact sheet가 general PT checklist QA를 통과한 뒤에만 생성한다.**

**PDF bleed 필수 점검** — 각 페이지 위·아래에 인접 슬라이드가 비치면 안 된다(장수 많을수록 심해짐). 템플릿에 `center:false` + `pdfPageHeightOffset:0`이 박혀 있어야 하고, `verify_pdf.py`로 캡처 검증. 자세히는 [presentation-craft.md](reference/presentation-craft.md) §4.
`.html`은 CDN 폰트/reveal을 쓰므로 온라인에서 그대로 열린다. 완전 오프라인 단일 파일이 필요하면 사용자에게 별도 요청 시 reveal/폰트를 인라인.

## 보안 — built-in 우선, `.env` 절대 읽지 말 것
Codex의 `$imagegen` built-in 경로에는 API 키가 필요하지 않다. API 키를 요청하거나 `.env`를 만들거나 읽지 않는다.
- 사용자가 direct API/CLI fallback을 명시적으로 선택한 경우에도 키를 채팅에 붙여 넣게 하지 말고 로컬 환경 변수로 설정하도록 안내한다. 실제 `.env`는 **읽거나 출력하지 않는다**.
- 스킬 폴더에 실제 키 `.env`를 두더라도 **공개 repo(csm-kr/pt-maker-skill)에는 절대 올리지 않는다**. 게시본에는 빈 `env.example` 템플릿만 포함한다.

## 빠른 사용법
| 하고 싶은 것 | 방법 |
|---|---|
| 제작 시작 | 첫 질문으로 `애니메이션 위주 / 줄글 위주 / 이미지 위주` 중 하나를 묻는다. 사용자가 선택을 넘기면 `image` |
| 새 덱 | `new_deck.py "<slug>" --production-direction <animation\|text\|image>` → 포맷별 산출물 채우기 |
| 웹에서 찾아 PT | 포맷 확정 → `reference/research.md`로 소스 맵 작성 → 개요 합의 → 해당 `--production-direction`으로 `new_deck.py` |
| 사용자 그림 넣기 | `input/`→덱 `assets/` 복사 후 `s-image` polaroid `<img src>`에 임베드 |
| 일러스트 생성·편집 | `image` 포맷이면 예상 장수·용도를 알린 뒤 `$imagegen` built-in을 적극 호출하고 선택본을 덱 `assets/`에 저장 |
| 연속 장면 애니메이션 | continuity contract → `$imagegen` 3~6장 → `.image-sequence` |
| 애니메이션 발표 HTML | `build_animated_presentation.py output/NN_.../animation -o output/NN_.../animation/<주제>-발표용-vN.html` |
| 발표 HTML 검수 | `qa_animated_presentation.py output/NN_.../animation/<주제>-발표용-vN.html --screenshots-dir output/NN_.../animation/renders/qa/presentation-html` |
| 애니메이션 영상 export(명시 요청 시만) | preview 승인·animation QA 90점/P0=0 뒤 `hyperframes_mode.py render ... --approved --qa-ledger ... --background` |
| HTML guard | `qa_html_guard.py output/NN_.../<주제>v<N>.html` |
| media guard | `qa_media_guard.py output/NN_.../<주제>v<N>.html` |
| PDF | `export_pdf.py output/NN_.../deck.html` |
| PPTX(명시 요청 시만) | PDF/contact sheet QA 통과 후 `export_pptx.py output/NN_.../<주제>v<N>.html output/NN_.../<주제>v<N>.pptx` |
| 미리보기 | `browser_harness_runtime.py --ensure` 확인 후 격리 background browser-harness로 `file://...output/NN_.../deck.html` 검수 |

## Common mistakes
- 받은 이미지(손글씨·스케치)를 **어떻게 쓸지 안 묻고** 임의로 임베드/재구성 → ❌. 먼저 인풋을 넣어 달라고 요청하고, 받으면 (a) 내용 재구성 vs (b) 원본 임베드를 **물어본 뒤** 진행.
- 사용자 원본 이미지를 생성/변형 → ❌. 원본 그대로 임베드.
- `image` 포맷이 아닌데 이미지 생성을 사용자에게 알리지 않고 시작하거나, `image` 포맷에서 적합한 자산이 부족한데도 웹 탐색·`imagegen` 보강 없이 텍스트만 남기기 → ❌. `image` 선택/기본 적용은 생성 보강의 원칙적 동의이며 예상 장수·용도는 실행 전에 알린다.
- Codex에서 `gen_image.py`나 direct API를 기본 이미지 생성 경로로 사용 → ❌. `$imagegen` 스킬의 built-in `image_gen`을 우선하고, 선택본을 덱 `assets/`에 저장한다. API/CLI fallback은 사용자가 명시적으로 요청하거나 built-in 실패 후 승인한 경우에만 사용한다.
- 연속 프레임을 각각 독립적인 새 그림으로 생성 → ❌. 첫 프레임 이후에는 직전 승인 프레임을 reference로 쓰고 subject/camera/environment invariants를 고정한다.
- 의미 없는 무한 wobble/pulse/float, transition을 4종 이상 혼용, reduced-motion/print 정지 포즈 누락 → ❌. 유한 모션과 2~3개 전환 어휘만 쓴다.
- 애니메이션 HTML의 모든 슬라이드에 `will-change`를 걸거나, 1920×1080 전체 화면 blur/backdrop-filter/animated clip-path를 전환 중 보간해 넘김이 버벅임 → ❌. `transform/opacity` 중심으로 만들고 현재·양옆 장면만 GPU 승격하며 `qa_animated_presentation.py`의 frame-time evidence를 확인한다.
- `image` 포맷의 표지·챕터 오프너·핵심 개념·사례·마감 슬라이드가 텍스트만 있음 → ❌. 각 주요 슬라이드에 관련 사진/스샷/차트/SVG/AI 일러스트 중 하나를 배치하고, 개요 단계부터 `visual plan`을 적는다.
- `image` 포맷에서 콘텐츠 슬라이드가 두 장 이상 연속 텍스트만 있음 → ❌. 설명형이면 SVG/차트/타임라인으로, 무드형이면 생성 이미지나 실사진으로 보강한다. `text` 포맷에는 이 이미지 수량 규칙을 적용하지 않는다.
- 모든 콘텐츠 슬라이드가 같은 레이아웃(불릿 좌·비주얼 우) → ❌ 단조롭다. 한 덱에서 카드 그리드·미러(비주얼 좌)·허브·가로 타임라인·중앙 statement·이미지 주연 등 3~4종 이상 섞는다(craft.md §2-11).
- `text` 포맷을 비슷한 크기의 제목+문단 박스로 반복하거나 모든 문장을 동일 굵기·정렬로 배치 → ❌. 슬라이드마다 초점 문구/보조 문구/읽는 경로를 정하고 최소 3개 타이포 구성 family를 분산한다.
- `image` 포맷에서 문장 옆에 분위기만 비슷한 사진을 붙이거나 한 이미지를 반복해 수량만 채움 → ❌. `claim → image` 대응을 기록하고 각 주요 문장을 실제로 설명·증명하는 서로 다른 이미지를 쓴다.
- 줄간격이 좁아 빽빽 / 한글 라벨(SVG·kicker)을 모노폰트로 / 정확한 연도·숫자·고유명사를 손글씨 폰트(Nanum Pen)로 → ❌ 가독성. 본문 `line-height ≥ 1.5`, 한글은 Pretendard, 손글씨는 가벼운 메모·감탄에만(사실 정보는 정자체).
- 본문·불릿을 무조건 32px 이상으로 키워 둔탁하게 만들기 → ❌. 일반 HTML 덱은 Pretendard 기준 본문 28-30px, hard floor 26px가 기본. 라벨은 20-22px, 출처/fine-print는 15-16px까지 허용하되, 작아 보이면 문장을 줄이거나 슬라이드를 나눈다. 큰 발표장/프로젝터용이면 32px로 올린다.
- 카드 썸네일/인물/선수/제품/음식 사진을 짧은 고정높이 `object-fit:cover`로 → ❌ 피사체 잘림. `aspect-ratio:3/2` 박스 + `object-fit:contain`(흰 배경) 또는 검증된 focal crop으로 얼굴·머리·손·로고·핵심 사물을 보존한다. 큰 히어로도 중요한 얼굴/피사체가 잘리면 실패다.
- 실제 국가/도시/여행/언어권/음식권/역사 지도에서 손그림 SVG 개략도를 지도로 제시 → ❌. 웹/공식/공개 라이선스 지도 베이스를 가져오고, 그 위에 핀·루트·영역·라벨을 overlay로 그린다. 직접 그린 지도는 "개념 스케치"라고 명시된 경우에만 허용한다.
- 원형 번호·아이콘 뱃지가 옆 라벨보다 커서 아랫줄 침범 → ❌. 라벨 크기에 맞춰 작게(≈1.2~1.3em)·`margin-bottom` 확보, 빌드 후 스샷으로 수직 겹침 점검.
- PDF를 `deck.pdf`로 저장 → ❌. 주제 이름(`"<주제>.pdf"`)으로.
- 산출 `.html`을 `deck.html`로 그대로 남기기 → ❌. 마감 때 `deck.html`을 `<주제>v<N>.html`로 rename(=PDF와 같은 이름). 작업 중 편집은 `deck.html`로 OK.
- `.pdf` 줄간격이 `.html`보다 좁다 → reveal print-pdf의 한계. `export_pdf_shots.py`로 HTML 스샷을 합쳐 1:1로 만든다.
- PPTX를 기본 산출물로 자동 생성하거나 편집 가능한 도형/텍스트로 바로 만들려고 함 → ❌. 현재 PPTX export는 정렬 보존용 이미지 기반 옵션이다. 사용자가 명시 요청한 경우에만 PDF QA 통과 후 생성한다. 편집 가능성이 필요하면 별도 네이티브 PPTX 빌드로 명시하고 QA 기준을 따로 잡는다.
- 최종 점수나 `pt-qa-result: pass`를 말하면서 `qa_score_gate.py`를 통과하지 않음 → ❌. 렌더 QA ledger와 score gate pass 없이는 90점 이상/통과 보고 금지.
- 최종 납품이라고 말하면서 사용자 최종 리뷰와 `qa_final_review_gate.py`를 통과하지 않음 → ❌. score gate 통과본은 후보일 뿐이고, final은 사용자 리뷰 ledger와 final review gate pass 이후에만 가능.
- SVG/CSS 도식 라벨이 도형 밖으로 넘침/도형과 겹쳐 안 읽힘 → ❌. 라벨은 도형 **중앙**(타원이면 `cx,cy`에 `text-anchor:middle`)에 넣거나, 도형과 **충분히 띄운다**. 선/화살표는 대상 중심 또는 경계에 명확히 닿아야 하고, 끊긴 선·떠 있는 선·텍스트를 가로지르는 선은 P0. 도식 컨테이너에는 full-size 렌더 검수 후에만 `data-fullsize-qa="true"`와 `data-rendered-qa="true"`를 붙인다.
- kicker 번호가 슬라이드마다 다른 위치(가운데/좌측 등)에 떠 통일성이 없음 → ❌. kicker를 `.s-head`(absolute 좌상단 고정)로 감싸 **모든 슬라이드 같은 자리**에. (템플릿에 반영됨)
- 브랜드 색·폰트 변경 → ❌. 토큰 고정.
- `.env`를 cat/Read로 열기 → ❌. Codex built-in 경로에는 필요도 없고 키가 대화에 노출될 수 있음.
- `browser-harness`가 없다고 `browse`/Playwright/DeckTape/Codex Browser로 우회하거나 사용자의 보이는 Chrome에 붙기 → ❌. bootstrap으로 설치·등록하고 격리 background만 사용.
- `$pt-maker ... 만들어줘` 요청에서 포맷 3지선다를 첫 질문으로 묻지 않거나, 여러 Grill Me 질문을 한 메시지에 묶거나, 포맷 확정 전에 참고자료·리서치·개요·스캐폴딩을 시작하기 → ❌. 사용자가 선택을 건너뛰면 `image`로 기록한 뒤 다음 질문 하나만 한다.
- 애니메이션 모드의 기본 결과물을 MP4로 간주하거나, 선형 HyperFrames `index.html`만 납품하고 좌우 탐색 발표용 HTML을 만들지 않거나, 슬라이드 재진입 시 모션이 재생되지 않음 → ❌. 기본은 같은 composition으로 생성한 발표 HTML이며, 영상은 사용자의 명시 요청이 있을 때만 추가한다.
- HyperFrames preview/Studio를 최종 QA 뒤 계속 실행해 둠 → ❌. `stop --target all` 후 `status`의 `alive:false`를 확인한다.
- 레거시 direct API에서 vip 모델에 `quality` 전송 → ❌. official 전용.
- deck.html을 작업공간 밖에 두고 브라우저 호출 → 열리지 않을 수 있음.
- 세로로 긴 스샷을 폴라로이드(가로)에 → 빈 공간. `object-fit:cover` 썸네일 카드로.
- fade 전환 중 스샷 → 이전 슬라이드 겹침. `transition:'none'` 후 캡처.
- 한 슬라이드에 여러 주장(제목에 "그리고") → 두 장으로. One idea per slide.
- 제목이 시각물(곡선·그래프·그림)을 약속했는데 본문에 안 그림 → ❌. 약속한 비주얼은 실제로 그린다(추상 막대·플레이스홀더 금지). statement 슬라이드는 미니 비주얼로 여백을 채움. 자세히는 [presentation-craft.md](reference/presentation-craft.md) §2-9·§4.
- PDF 각 페이지에 인접 슬라이드가 비침/잘림 → ❌. `Reveal.initialize`에 `center:false` + `pdfPageHeightOffset:0` 필수, `verify_pdf.py`로 캡처 검증. 장수 늘리면 누적되어 심해지니 매번 재검증.
- 포맷 확정 뒤 인테이크에서 참고자료 여부를 확인하지 않거나, 질문을 여러 개 한꺼번에 던지거나, 필수 4항목(메시지·청중·근거·CTA)과 발표 상황·분위기·이미지 레벨을 안 채우고 슬라이드부터 만들기 → ❌. intake.md 순서대로 하나씩 먼저.
- 취향을 사용자 확인 없이 조용히 taste-profile에 기록 → ❌. 항상 diff 제안 후 확인.
- 사용자 최종 리뷰에서 나온 취향 학습을 `taste-profile.md`/`dark-taste-profile.md`에 반영할지 묻지 않거나, 반영/미반영 결정을 `user_review_ledger.json`에 남기지 않음 → ❌.
- 덱 산출물(html·pdf·이미지)을 루트나 공용 `out/`에 흩뿌리기 → ❌. `output/NN_slug_date/`(이미지는 그 안 `assets/`)로.

## Cover Background QA

For cover and section-opening slides, follow `reference/cover-background-quality.md`.
Do not put pale paper texture, low-opacity overlays, or same-tone ivory panels behind the cover headline unless the rendered contact sheet confirms the cover is not washed out. If slide 1 looks faded, replace the background with a solid panel or darker field and rerender before delivery.

## Composition Balance QA

For slide layout balance, follow `reference/composition-balance.md`.
Do not push leftover content into shallow bottom cards. Keep the main message near the optical center, preserve clear distance from the footer, and reject any slide where Korean text visually touches card borders, icons, labels, or neighboring boxes. Record major object positions as normalized full-slide `xywh` ratios with a short intent note when placement carries psychological weight. If the lower third feels crowded, redraw the layout instead of shrinking text.
