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

State 15:15 (after CP-G1 HOLD fixes and the owner's 14:55–15:10 changes; 25 offline tests; numbers from
scripts/glyphs/eval/*, raw outputs in review_scratch/CP-G1c2-evidence/):
- marks (truth-enumerated): separate accents found 97.95 %, detected 99.97 %, fused into their letter 25.4 % of all
  accents in these renders, mark component precision 96.1 %; neighbour ink pixels 97.3 %; letters one box 92.8 %,
  lost 1.0 %. The earlier 99.07 % counted only retained components (CP-G1 F1) and is retracted.
- skew (100 straight rendered lines): median 0.009°, high-confidence fits (95) max 0.515°; 2 medium/low-confidence
  misses (3.8°, 10.4°) on short lines between full-width neighbours. Bent lines: lines with any column > 0.25 xh off
  45 % (84 % before tracking), straight unchanged.
- ink state = letter completeness (owner rule): broken recall 82 %, precision 78 % (injected defects, seed 2); merged
  precision 99.5 %, recall 74 %; faint letters now detected (faint channel) and flagged.
- double lines: real fixtures 7/7 double, 0/20 single with my provisional labels (in-sample threshold 0.25); rendered
  crops recall 95 %, precision 74 %.
Artifact v2 (same URL): https://claude.ai/artifact/FrYMi9ra4boVf6auGm3arm — owner's cases, then interesting cases
selected from 452 measured crops, with inspection notes.

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
- Owner example original crop (resolved in part by bend tracking): before x ≈ 180 the band is extrapolated (no supporting letters pass the evidence filter)
  and reads 0–6 % of the body inside where about 25 % is visible; the line likely curls there. Relaxing the filter for
  edge-cut slivers did not fix it and cost 1.8 % lost letters on the rendered set, so it was reverted (P2: end curl).
- The document prior for that crop is the median of the document's complete crops (26 px); the same line's re-cut crop
  measures 21 px. The fitted angle moves from 2.4° (prior 26) to 2.0° (21): the prior's precision matters for clipped crops.
- Validation lines are straight (rotation only); curl, warping and real broken type are not yet in the rendered set.
