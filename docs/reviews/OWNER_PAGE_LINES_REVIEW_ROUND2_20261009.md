# Owner review of the page-lines detector, round 2 (9 October 2026)

This note records what the owner saw on the review page (https://claude.ai/artifact/CjLzEq93DBohzH55rDubmv,
48 pages) for Astra's round-2 detector (branch `astra/page-lines-2`, commit f405fe3). For each point it gives the
measurement behind it and what the next round must do. **Every case the owner named is listed, with its page and
segment**; the summary table at the end has all of them.

The governing documents are still `docs/PAGE_LINES_ALGORITHM.md` and the owner's statement in `.astra/BRIEF.md` of
that branch. This note adds requirements; it does not replace them.

The figures were measured on Astra's own outputs (`.astra/out/<key>.lines.json`, `.segments.json`, `.checks.json`)
and on the page images. Line numbers are indices into `<key>.lines.json`; segment numbers are the review-page card
ids (`<key>-sNNNNN`), which are also indices into `<key>.segments.json`. Two terms are used throughout:
- **Ink darkness:** the median grey (0 black, 255 white) of the darkest fifth of the pixels between a line's mean line
  and baseline.
- **Jump:** the largest change of a region edge from one pixel column to the next, in x-heights.

## In short

1. **The four font lines are not measured on each line.** This is the main problem, and it causes others.
2. **Extra lines sit on parts of real lines.** A weak line is placed on the accents or on part of a real line, about
   one x-height away from it. The seam between the two then runs through the letters. So a line that is found
   correctly comes out of the unrolling with its top or bottom cut off.
3. **Ink that is not text gets lines:** library stamps, the lettering of a stamp, show-through from the back of the
   page, faint ghost marks. On these pages that ink is much fainter than the printed text. Faintness, relative to the
   page's own text, must count against a detection.
4. **The line regions are jagged.** Their edges jump up and down by several x-heights. Line geometry on a printed
   page is smooth, and so must the regions be.
5. **A line crosses into the other column**, and the crossing check did not notice.
6. **Text is missed where the rule detector takes it for a rule:** a darker grey corner of the page, and the curled
   starts of lines next to the binding.

## 1. The four font lines

**Owner:** "The main thing seems to be now that the 4 font lines are not accurately detected on the text-lines."

**What the code does** (`greekocr/glyphs/page_text_lines.py`, `_make_lines`):
- The **baseline** is fitted per line, and follows its skew or curve. It mostly sits on the letter bottoms.
- The **x-height** is estimated once per line model; the **mean line** is then simply `baseline − x-height`,
  never fitted to the tops of the small letters.
- The **top and bottom lines** are not measured on the line at all. They are the 98th percentile of how far ink rises
  above, and drops below, the baseline, pooled over every line on the page of a similar size (x-height within
  0.8–1.25×). Every line of that size on the page gets the same two offsets:
  - on an-d6fd2cf2f618-p000047, every line has top −1.91, mean −1.00, bottom +0.99 x-heights from the baseline;
  - on Vouli p00001 the pooled values are −1.84 and +0.70.
- Because the percentile includes accents and breathings, the top line sits at accent height rather than at the tops
  of capitals and ascenders. On lines without capitals or ascenders (all-capital headings, digits) it fits nothing.

**What it must do instead:**
- Measure all four lines **on each line, from its own letters**, and let them follow the line's skew or curve like
  the baseline:
  - baseline: letter bottoms, excluding descenders;
  - mean line: tops of the small letters (α ε ο ν …), excluding accents;
  - top line: tops of capitals and ascenders, excluding accents and breathings;
  - bottom line: bottoms of descenders.
- Accents, breathings and other diacritics are marks **above a line's letters**: they belong to the line beneath
  them and lie above its top line. The line's region must still include them (see 4).
- A line too short to give many points takes its geometry from same-size neighbours in the same column, as the
  algorithm's shared page geometry says. (The owner, round 1: "we need many points to find an orientation".) Where a
  line has no capitals or no descenders, the top or bottom offset comes from same-size lines, and the line record says
  so.
- The crop tools already measure the rise and drop per crop (`report.line_record`, `baseline.text_lines`). Reuse them,
  or show something better on these pages.

## 2. Extra lines on parts of real lines, and the cut-offs they cause

In all three cases below a weak extra line is placed about one x-height from a real line, on its accents or on part
of its letters. The region seam between the two then runs through the real line's letters.

### an-d6fd2cf2f618-p000047-s00006: accents split from their letters

**Owner:** "the first two lines are basically the split of the accents from the chars."

Measured:
- Line 15 (baseline y 817.7) sits 23 px, 1.1 x-heights, above line 16 (y 841.0). The printed line spacing on this
  page is about 50 px (2.4 x-heights).
- Line 15 is the accent row of «Οὗς δ' αὖ εἰς τὸν …». Between its mean line and baseline there is almost no ink: ink
  darkness 190, against about 85 on the page's text lines.

### s2-49598b2e848ab1f0ee1e-p00001-s00014: the first line is cut in the output, though it is detected

**Owner:** "seems to cut the first line here when it outputs it, but it seems to be properly detected."

Measured:
- The printed line «('Απαρτίας γενομένης, ἀνεγνώσθησαν καὶ ἐνεκρίθησαν τὰ» carries two lines:
  - line 10 (baseline y 901, 38 components, on the letter bottoms; this is the correct detection);
  - line 9 (baseline y 886, only 3 components, borrowed geometry), 15 px or 0.6 x-heights above it.
- The seam between them leaves line 10's region only 0.91 x-heights above its baseline. So its unrolled image loses
  the upper parts of the capitals, ascenders and accents. Line 9's region ends 0.23 x-heights *above its own
  baseline*.
- Both are on the page's cut-ink list.

### s2-49598b2e848ab1f0ee1e-p00001-s00024: the last line's bottom is cut off

**Owner:** "the last line's bottom is cutoff."

Measured:
- The last line of the segment is line 93, «πουργὸν ἀπὸ τῶν ὁποίων κατέχει ἐδωλίων. Ἀνάξια δὲ ἀ-», baseline y 2573.
- Below it, line 94 (x 1836–2789, baseline y 2616, 2 components, borrowed geometry) lies 22 px, 1 x-height, above
  the real next line 95 (y 2638). Line 94 sits on the upper part of «θεωρῶ καὶ κηρύσσω ὅσα ἀπρεπῶς», the words after
  «παντήσεως».
- The seam between 93 and 94 runs 0.43 x-heights below line 93's baseline, through its descenders (ρ, γ, χ).
- Lines 93 and 94 are both on the cut-ink list.

**Requirement:**
- A line must have letter bodies in its mean–base band, with enough support to stand on its own.
- A band of small marks within about one x-height above a line's letters joins that line; it never becomes a line of
  its own. The same holds for a fragment lying on the upper part of a line's letters.
- The column's baseline spacing is a second check. Two "lines" 0.6–1.1 x-heights apart in a column whose spacing is
  2.4–3 x-heights are one line.
- An unrolled line image must contain the whole of its line, from the tops of capitals and accents to the bottoms of
  descenders. On Vouli p00001, 45 of 120 lines are on the cut-ink list; that list is part of the acceptance.

## 3. Ink that is not text

### an-d6fd2cf2f618-p000047-s00008: a library stamp over the text

**Owner:** "another thing we should be thinking about is background ink stamps."

The page carries a round library stamp, lettered «…ΠΑΝΕΠΙΣΤΗΜΙΟ…» around its ring, over the right end of the last
eight text lines.

### an-d6fd2cf2f618-p000047-s00011 … s00017: the stamp's lettering taken for characters

**Owner:** segments from "s00011 (segment x 809–819, y 1647–1685) to s00017 (segment x 1124–1160, y 1559–1622) …
these are small marks interpreted as chars."

Measured:
- The pixel segmenter made segments s00011–s00017 (x 809–1160, y 1488–1821) out of the stamp's lettering.
- The detector put lines 40–42 on some of them: each 1–2 letters long, built from 1–7 components, with borrowed
  geometry.
- Their ink darkness is 180–191, against about 100 for the text lines next to them.

**Requirement for stamps:**
- Stamp ink is not text and gets no lines. The brief already says so: "Illustrations, ornaments, stamps and scan
  borders are not text and get no lines."
- Where a stamp lies over real text, the text line keeps its full extent, and the stamp ink must not move its baseline
  or font lines. Ideally the unrolled image shows the stamp faintly or not at all.
- Ring lettering is rotated and follows a circle. It fails the "same orientation as its neighbours" test as well as
  the faintness test below.

### Show-through, ghosts and faint pages

**Owner:**
- s2-09f5dfca4af4d74173c6-p00005: "the faint page has detection but the faintness should be used to discount the
  detections (relative to the others)";
- s2-0ce9d1025b3f23c7119e-p00001: "similarly … the faintness";
- s2-5ca02b142a2a3eaf078a-p00002: "ghost detection at bottom right corner of the page";
- s2-d1ed1c2db37f431f4acb-p00001: "in the left bottom corner the faint letters from the back of the page are
  detected".

Measured: on each of the four pages the lines fall into two groups by ink darkness, with a clear gap between them.

| Page | Lines | Text lines | Faint lines | Where the faint lines are |
|---|---|---|---|---|
| s2-09f5dfca4af4d74173c6-p00005 | 60 | 44, darkness 62–89 | 16, darkness 154–185 | the faint left half and the margins |
| s2-0ce9d1025b3f23c7119e-p00001 | 93 | 48, darkness 64–97 | 45, darkness 146–191 | the faint left half, the lower half, the right margin |
| s2-5ca02b142a2a3eaf078a-p00002 | 55 | 41, darkness 9–33 | 14, darkness 178–209 | left margin (lines 0–5); bottom right (lines 47–54, x 1473–1892, y 2457–3187) |
| s2-d1ed1c2db37f431f4acb-p00001 | 164 | 151, darkness up to 132 | 13, darkness 150–189 | bottom left (lines 43, 48–51, x 203–1590, y 3771–4269), and a few marks elsewhere |

Many of the faint lines also have little support (0–5 components) and borrowed geometry.

**Requirement for faint ink:**
- Measure the contrast of each candidate line's ink **relative to the page's own text**. For the darkest pages,
  measure it also relative to the local background.
- Discount detections that are much fainter than the page's text. "Relative" matters: a uniformly faded scan is still
  all text; only ink much fainter than the rest of the same page is suspect.
- Show-through from the back of the page is mirrored and usually out of register with the front lines. Use that as a
  second cue where it helps.
- Report a faint candidate as such, with its contrast, in the line record. It must not be silently kept or silently
  dropped, so that the review page can show what was discounted.

## 4. Jagged line regions

### an-ef481610a820-p000181

**Owner:** "the lines are very jagged, the areas you are presenting seem to spike vertically, which line geometry on
pages shouldn't be like that."

Measured:
- On this page the region edges jump by a median of 1.3 x-heights between neighbouring pixel columns, and by up to
  14.4 (line 30).
- On other pages: on s2-0ce9d1025b3f23c7119e-p00001 the median jump is 8.2 x-heights; on
  s2-09f5dfca4af4d74173c6-p00005 the largest is 73.

**Cause** (`_boundaries`):
- The edge between two lines is the midpoint between the lower line's top and the upper line's bottom.
- It is chosen **pixel column by pixel column**, against whichever line is the neighbour in that column.
- So wherever a short or spurious line starts or ends (an accent row, a stamp mark, a ghost: sections 2–3), the
  neighbour changes and the edge jumps. Where there is no neighbour, the edge falls back to the line's own font band.

**Requirement:**
- The region edges are smooth curves of the same kind as the baselines, following the column's shared skew and curve;
  they are not per-column midpoints.
- Neighbours are the real text lines of the same column. Rejected marks (sections 2–3) do not take part.
- The edges still tessellate (no gaps, no overlaps), and each region holds all of its line's ink, from accents above to
  descenders below.
- Where a neighbour's accents or descenders reach across the seam, the seam bends locally around that mark rather than
  cutting either line's ink.

## 5. Crossing into the other column

### s2-49598b2e848ab1f0ee1e-p00001-s00019

**Owner:** "a line from the opposite column is wrongly connected."

Measured:
- Line 81 is assigned to column 2 and spans x 1466–2943 (baseline y 1769, 46 components). Column 1's text ends at
  x ≈ 1511 (segment s00019 spans x 48–1511), so the line starts about 45 px inside column 1.
- It joins the end of a column-1 line to column 2's «τῶν προτέρων, ὅτι δὲν θέλω παρακολουθήσει τὸν κ. Πρωθυ-».
- The printed vertical rule between the columns is visible on the page. Yet the page's checks report **0 rule or
  gutter crossings**: the rule was not detected at this height, so the check could not see the crossing.

**Requirement:**
- A line never crosses a column boundary (the owner's statement: "These segments should respect column boundaries").
- The column boundary comes from the page's column structure as a whole: the printed rule where there is one, and the
  gutter, which runs down the full column height. Local evidence at one height is not enough.
- The crossing check must use that same boundary, so it cannot report 0 when a line crosses.

## 6. Text missed because the rule detector takes it for a rule

### s2-74cdb23a34ca4a6cd01e-p00002: the bottom-left corner of the page

**Owner:** "the bottom left corner of the page is not detected at all."

Measured:
- In the left column below y ≈ 4030 (x 200–1700), the rule mask (`pixel_segments._rule_mask`) marks 33% of the
  pixels as rule. The scan's background there is darker: median grey 207, against 225 just above.
- The pixel segmenter therefore cuts the block into 48 thin vertical slivers (segments s00055–s00102, 4–72 px wide).
- The detector produces fragments there: lines 100–127, mostly 4–60 px long.
- The lines above start late, at x 510–1183 instead of about 240.
- The last two printed lines get no line along their length:
  - «τὸ ἐπιὸν ἔτος ἡ γῆ θὰ δώσῃ εἰσοδήματα· ἀλλ' ἐὰν ὁ Πάμι-»
  - «σος πλημμυρήσῃ ἔτι μίαν φορὰν, δὲν ἔχομεν πλέον εἰσοδήματα»

### s2-3229200bf47ca465a42d-p00004: the first characters of each line

**Owner:** "a few chars at the beginning of each line are not detected, probably because the curve upwards."

Measured:
- The page curls towards the binding on the left, and the first 2–5 characters of every line bend away there.
- The rule mask covers the pixel columns x 0–~170 over most of the page height (all 2,499 rows at x 40–70; 963 rows
  at x 120).
- Those pixels are removed from the ink as rule, and 34 of the 39 lines start at the same x ≈ 180. The curled
  starts get no line.

**Requirement:**
- Only long, thin, straight strokes are rules. A darker background, a binding shadow or a curled margin full of
  letters is not a rule, and letter-shaped components never become barriers.
- Lines follow the curl to their first letter. The owner's statement: "the segment follows the true line from
  beginning to end".
- A curl at the start of a line is the same problem as the curl at the end, which the end-bend scorer (a4a1421)
  already handles on crops.

## Checks for the next round

Report per page, on all 48 development pages, then on the held-out pages:
1. **Font lines:** for each line, the distance from each of the four lines to the ink it should touch, in
   x-heights:
   - the baseline to the letter bottoms;
   - the mean line to the small-letter tops;
   - the top line to the capital tops;
   - the bottom line to the descender bottoms.

   Also report how many lines took a value from their neighbours.
2. **Extra lines:** the number of lines with no letter bodies in their mean–base band (should be 0), and the number
   of pairs of lines closer than half the column's line spacing (should be 0).
3. **Cut-offs:** lines whose unrolled image cuts their own ink at the top or bottom (should be ~0; 45 of 120 on Vouli
   p00001 now).
4. **Faint detections:** each line's ink contrast relative to the page's text, how many lines were discounted, and
   why.
5. **Smoothness:** the largest jump of each region edge between neighbouring pixel columns, in x-heights. It should be
   well under 0.1, except where a seam bends around a mark.
6. **Column crossings:** the count, measured against the full-height column boundaries (must be 0).
7. **Missed text:** ink of text size left without a line, and the share of the page marked as rule. Report both per
   page.
8. **The checks already in the brief:** foreign ink, boundary overlaps (0) and broken lines (~0).
9. **Every case in the table below, by name:** what the new output does there, with its image.

## Every case the owner named

| # | Page | Segment / place | What the owner saw | Section |
|---|---|---|---|---|
| 1 | all pages | — | the four font lines not accurately detected | 1 |
| 2 | an-d6fd2cf2f618-p000047 | s00006, first two lines | accents split from their letters | 2 |
| 3 | s2-49598b2e848ab1f0ee1e-p00001 | s00014, first line | detected, but cut in the output | 2 |
| 4 | s2-49598b2e848ab1f0ee1e-p00001 | s00024, last line | bottom cut off | 2 |
| 5 | an-d6fd2cf2f618-p000047 | s00008 | background ink stamp | 3 |
| 6 | an-d6fd2cf2f618-p000047 | s00011 (x 809–819, y 1647–1685) to s00017 (x 1124–1160, y 1559–1622) | small marks (stamp lettering) taken for characters | 3 |
| 7 | s2-09f5dfca4af4d74173c6-p00005 | faint page | faintness should discount the detections | 3 |
| 8 | s2-0ce9d1025b3f23c7119e-p00001 | faint lines | faintness should discount the detections | 3 |
| 9 | s2-5ca02b142a2a3eaf078a-p00002 | bottom right corner | ghost detection | 3 |
| 10 | s2-d1ed1c2db37f431f4acb-p00001 | bottom left corner | faint letters from the back of the page detected | 3 |
| 11 | an-ef481610a820-p000181 | whole page | jagged regions that spike vertically | 4 |
| 12 | s2-49598b2e848ab1f0ee1e-p00001 | s00019 | a line from the opposite column wrongly connected | 5 |
| 13 | s2-74cdb23a34ca4a6cd01e-p00002 | bottom left corner | not detected at all | 6 |
| 14 | s2-3229200bf47ca465a42d-p00004 | start of every line | first characters missed where the line curves | 6 |
