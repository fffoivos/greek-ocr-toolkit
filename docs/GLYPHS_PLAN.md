# Glyph-level readability (skew, cut-off, ink): owner requirements and plan

Written 8 Oct 2026 14:30 Athens. Owner = the project owner; requirements quoted or paraphrased from the 8 Oct sessions.

## Foundational tools (skew and ink are both built on these)

1. **Ink mask** (`glyphs.components.binarise`): which pixels are ink, plus its stability under a small threshold shift
   (faint ink flips; crisp ink does not).
2. **Blobs with roles** (`glyphs.components.line_glyphs`): letter, mark (accent/breathing/diaeresis/iota subscript),
   punct, fragment (broken piece), neighbour (adjacent line), rule, large (stain/ornament).
3. **Letter band** (`LineGlyphs.band`): baseline and mean line as functions of x. This is the coordinate system:
   skew = its angle; trail and boundary crossings = where it leaves the crop; cut-off letters = band outside the crop at
   that x; ink is measured inside it.
4. **Rough letter boxes** (`glyphs.letters.letter_boxes`): position and size per letter; merged blobs split at the letter pitch.
5. **Reference levels**: x-height, stroke width, ink darkness, ink density in the band, per line → page → document.
6. **Validation instruments**: rendered truth lines (`glyphs.synthetic`, `glyphs.evaluate`), known-defect injector
   (planned), owner blind review sheets, Luna as an independent second check.

State 16:20 (after CP-G1c3 HOLD fix and the four-line model; 34 glyph tests; raw outputs in
review_scratch/CP-G1c3-evidence/: evals_v7.txt, neighbour_eval.txt, fixture_double.txt):
- skew (100 straight rendered lines): high-confidence fits (95) max 0.217°; all fits median 0.009°, p99 0.98°, max 4.55°.
  Bent lines: lines with any column > 0.25 x-heights off 34 %.
- owner example (original crop): 31.6–31.8 % of the letter body inside the crop over the first 180 columns (the bend
  fit now follows the start); angle 2.209° with the document prior (26 px), 1.820° with the re-cut's 21 px.
- marks: separate accents found 98.7 %, all accents 75.4 % (23.6 % fused into their letter), precision 95.2 %;
  neighbour ink: 97.1 % of visible truth pixels called neighbour.
- letter states, two truths fixed before measurement (print = physical ink; visible = noise-free scan ≥ ¼ of
  paper→ink), ordinary renders / with injected defects:
  PRINT   broken recall 25.3 % / 41.4 %, under precision 42.6 % / 43.4 %, merged precision 3.6 % / 26.8 %;
  VISIBLE broken recall 56.9 % / 61.5 %, under precision 44.6 % / 48.6 %, merged precision 87.1 % / 84.5 %,
          merged recall 63.8 % / 79.5 %.
  Letters truly gone from the print: 0 / 282 (253 missed, no warning yet). 'Merged' = visibly touching in the scan.
- four guide lines for every line: neighbours borrow the main line's shape; on 150 rendered crops 96 % of visible
  neighbour lines found, median placement error 0.056 x-heights, 74 % within 0.25, 87 % within 0.5 (the rest:
  tall-letter tops taken for short-letter tops; a per-document line pitch would resolve it).
- double lines: real fixtures 7/7 double, 0/20 single, 2/17 partial flagged (in-sample threshold); rendered recall 93 %,
  precision 76 %.
Earlier figures on the review page v2 (84 %→45 % bends, broken 82 %/78 %, merged 99.5 %/74 %) used the
detector-dependent evaluator and are superseded.

## Owner direction, 8 Oct 16:40 (autonomous from here; owner reviews from the phone)
- Deliver a final review page of ≥ 200 lines. "The lines have a good shape; we are close."
- (1) Readability and OCR relevance per line: is it clear which text in the crop is the target (several lines, columns,
  dominant line)? Is the line readable: cut-offs at the top and at the bottom (separate thresholds), under- and over-ink?
  Thresholds come from the synthetic line generator's parameter ranges: measure the same quantities on synthetic lines
  with known degradation, read them with an OCR model, and set limits where the error rises; place real lines on
  that scale (the distribution).
- (2) API on top: (a) separate the lines when a crop holds more than one (per line and per column; e.g. for Google
  Document AI text), (b) fix the geometry (straighten along the fitted baseline, normalise height from the four guide
  lines; re-cutting clipped text needs the page image, via greekocr.real.geometry).
- Owner notes kept: lines are hierarchically above letters (a letter box never leaves its line); be careful with
  capitals (speaker names in capitals are common); split columns at rules and very wide gaps, never force alignment.
- Reviews batched: one independent review per completed step (letter/line fixes + columns + capitals; API; readability).

| step | content | review |
|---|---|---|
| S1 | CP-G2 findings, letters bounded by their line, line count, column split (rules + gaps), capitals | CP-G3 |
| S2 | lines API: separate_lines, straighten | CP-G4 (with S3) |
| S3 | readability: target clarity, top/bottom cut, ink; synthetic calibration with an OCR reader on the GPU node | CP-G4 |
| S4 | final page ≥ 200 lines with readability verdicts | in CP-G4 |

## Owner requirements

### Hard constraints
- The PDF text layer is another OCR (InVision on the parliament scans). It is never a reference or a gate; at most a
  labelled diagnostic column.
- Fix and measure crop/line quality first; "which reader is right" is moot while the lines are wrong.
- Readability checks must be reliable, automated and low-computation.
- Localise: say which parts of the line have each issue and how strongly, as simple 2-D functions along x (not only
  a per-line scalar).
- Owner example `tests/fixtures/o4d_lines/regressions/s2-60f24a3d8a2d714767f2-p00003-l00024_old.png`: a well-cut crop
  whose first letters are only about a quarter visible; the output must say unreadable at the start, fine later.
- Three questions: (1) does the line trend up or down, and where does it cross the image boundary; (2) are the letters
  too faint or over-inked; (3) are there unusual characters.
- Skew is shown as a line underlining the words.
- Letters: rough detection, size only; no letter identity needed; 100 % accuracy not needed.
- An internal model distinguishes letters from polytonic accents.
- Ink is measured in a standardised region: the band between the top and bottom skew lines, with expectations from the
  document's font; other lines of the same document help.
- All tooling lives in greek-ocr-toolkit behind high-level APIs with tests (docs/STANDARD.md).
- Fonts are verified to render every needed accent before use (font_supports_polytonic gate).

### Open, to explore later
- Exact font dimensions in the line (ascender/descender ratios, per-letter proportions).
- Faintness from poor OCR output quality (owner idea B). Proposed form: the reader's per-character confidence (CLLG)
  rather than the text layer's output, which stays diagnostic only.
- Unusual characters (question 3), image side and text side.
- Letter clarity, obstruction, and "other features not yet detected".
- Luna checks of images and of Greek output; a reliable commercial OCR on small samples.
- Automating the loop by iterating on small samples with high-accuracy tools.

## Plan
- **P0 — done 8 Oct**: ink mask, blobs/roles, band, letter boxes, synthetic truth, evaluator, tests.
- **P1 — first iteration, ETA ~16:00 Athens 8 Oct**: `glyphs/baseline.py` (underline, skew °, trail px, straight vs
  curved, boundary crossings, cut-off points/intervals along x); `glyphs/ink.py` (one signed score per letter:
  − broken/under-inked, + over-inked; from stroke width, darkness, fragmentation, filled counters, threshold
  stability, each against the line reference); artifact on ~20 real lines: (1) underline + cut-off points,
  (2) letter boxes with the ink function plotted below each line.
- **P2**: `glyphs/inject.py` known-defect injector (rotation, curl, clip with trail, fade, over-ink, blur, occluder,
  neighbour intrusion, foreign glyph over known x-ranges) + localisation scorer; numbers for P1; owner review.
- **P3**: page/document reference levels (line ids encode document and page).
- **P4**: align with T7 `readability_profile` types; CLI `greekocr glyphs ...` after the coordinator's commit.
- **P5**: unusual characters; text-side checks mapped to x via reader character cuts.
- **P6**: Luna cross-check; commercial OCR bake-off (credentials = owner).

## Known open problems
- Band estimation when most letters in a crop are clipped (owner example): needs page/document x-height prior (P3).
- A broken descender piece under a vowel can be read as an iota subscript (no letter identity).
- Accents beside capitals (Ἀ, Ὁ) are excluded from mark scoring; capitals' spacing marks need their own rule.
- Punctuation recall ≈ 70 % (commas/full stops vs fragments); not needed for skew or ink.
- Fits can join two separate text pieces at different heights (sample crop s2-7534648e60694be1d180-p00023-l00013:
  −7.2° fitted, high confidence). Needs a test that support is continuous along x.
- Partial second lines (a few words at one end, possibly curved; owner case s2-49598b2e848ab1f0ee1e-p00001-l00054)
  are not flagged; the double-line check fits one band across the whole crop.
- Rendered neighbour tips are more prominent than real ones (double-line precision 74 % rendered vs 0/20 false on
  real singles): the neighbour leading in the renderer should be calibrated to real pages.
- Owner example original crop — RESOLVED by bend tracking (31.6 % inside at the start, where about 25 % is visible).
  Historical note: before x ≈ 180 the band was extrapolated (no supporting letters pass the evidence filter)
  and reads 0–6 % of the body inside where about 25 % is visible; the line likely curls there. Relaxing the filter for
  edge-cut slivers did not fix it and cost 1.8 % lost letters on the rendered set, so it was reverted (P2: end curl).
- The document prior for that crop is the median of the document's complete crops (26 px); the same line's re-cut crop
  measures 21 px. The fitted angle moves from 2.4° (prior 26) to 2.0° (21): the prior's precision matters for clipped crops.
- Rendered validation covers rotation, end bends and injected defects; page warping and real broken type are not in it.
- Letters faded below visibility vanish without a per-letter warning (717 of 7,595 truth letters in the defect set).
