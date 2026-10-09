# Owner review of the page-lines detector, round 2 (9 October 2026)

What the owner saw on the review page (https://claude.ai/artifact/CjLzEq93DBohzH55rDubmv, 48 pages) for Astra's
round-2 detector (branch `astra/page-lines-2`, commit f405fe3), with the measurements behind each point and what
the next round must do. The governing documents are still `docs/PAGE_LINES_ALGORITHM.md` and the owner's
statement in `.astra/BRIEF.md` of that branch; this note adds requirements, it does not replace them.

The figures below were measured on Astra's own outputs (`.astra/out/<key>.lines.json`) and page images.
"Ink darkness" is the median grey (0 black, 255 white) of the darkest fifth of the pixels between a line's mean line
and baseline; "jump" is the largest change of a region boundary from one pixel column to the next, in x-heights.

## In short

1. **The four font lines are not measured on each line.** This is the main problem, and it causes others:
   accents split off as their own line, and region boundaries placed in the wrong place.
2. **Ink that is not text gets lines:** library stamps, the letters of a stamp, show-through from the back of the
   page, faint ghost marks. On these pages that ink is much fainter than the printed text; faintness, relative to the
   page's own text, must count against a detection.
3. **The line regions are jagged.** Their top and bottom edges jump up and down by several x-heights. Line
   geometry on a printed page is smooth, and so must the regions be.

## 1. The four font lines

**Owner:** "The main thing seems to be now that the 4 font lines are not accurately detected on the text-lines."

**What the code does** (`greekocr/glyphs/page_text_lines.py`, `_make_lines`):
- The **baseline** is fitted per line, and follows its skew or curve. It mostly sits on the letter bottoms.
- The **x-height** is estimated once per line model; the **mean line** is then simply `baseline − x-height`,
  never fitted to the tops of the small letters.
- The **top and bottom lines** are not measured on the line at all. They are the 98th percentile of how far ink rises
  above, and drops below, the baseline, pooled over every line on the page of a similar size (x-height within
  0.8–1.25×). Every line of that size on the page gets the same two offsets. On an-d6fd2cf2f618-p000047 every line
  has top −1.91, mean −1.00, bottom +0.99 x-heights from the baseline; on Vouli p00001 the pooled values are
  −1.84 and +0.70. Because the percentile includes accents and breathings, the top line sits at accent height rather
  than at the tops of capitals and ascenders, and on lines without them (all-capital headings, digits) it fits nothing.

**What it must do instead:**
- Measure all four lines **on each line, from its own letters**, and let them follow the line's skew or curve like
  the baseline:
  - baseline: letter bottoms, excluding descenders;
  - mean line: tops of the small letters (α ε ο ν …), excluding accents;
  - top line: tops of capitals and ascenders, excluding accents and breathings;
  - bottom line: bottoms of descenders.
- Accents, breathings and other diacritics are classified as marks **above a line's letters**: they belong to the
  line beneath them, and lie above its top line (the region must still include them; see 3).
- A line too short to give many points (the owner: "we need many points to find an orientation") takes its
  geometry from its neighbours of the same size in the same column, as the algorithm's shared page geometry says.
  Where a line has no capitals or no descenders, the top or bottom offset comes from same-size lines, and the line
  record says so.
- The crop tools already measure the rise and drop per crop (`report.line_record`, `baseline.text_lines`); reuse
  them or show something better on these pages.

### Accents split from their letters

**Owner, an-d6fd2cf2f618-p000047-s00006:** "the first two lines are basically the split of the accents from the
chars."

Measured: line 15 (baseline y 817.7) sits 23 px, 1.1 x-heights, above line 16 (y 841.0), while the printed line
spacing on this page is about 50 px (2.4 x-heights). Line 15 is the accent row of «Οὗς δ' αὖ εἰς τὸν …»; between its
mean line and baseline there is almost no ink (ink darkness 190, against about 85 on the page's text lines).

Requirement: a line must have letter bodies in its mean–base band. A band of small marks that lies within about one
x-height above a line's letters joins that line, never stands as a line of its own. The baseline spacing of the
column is a second check: two "lines" 1.1 x-heights apart where the column's spacing is 2.4 are one line.

## 2. Ink that is not text

### Stamps

**Owner, an-d6fd2cf2f618-p000047-s00008:** "another thing we should be thinking about is background ink stamps."
**Owner, s00011 (x 809–819, y 1647–1685) to s00017 (x 1124–1160, y 1559–1622):** "these are small marks interpreted
as chars."

The page carries a round library stamp (lettered «…ΠΑΝΕΠΙΣΤΗΜΙΟ…» around its ring) over the right end of the last
eight text lines of the page. The pixel segmenter made segments s00011–s00017 out of the stamp's lettering, and the
detector put lines on some of them: lines 40–42, 1–2 letters long, built from 1–7 components, geometry borrowed from
elsewhere. Their ink darkness is 180–191, against about 100 for the text lines next to them.

Requirement: stamp ink is not text and gets no lines (already out of scope in the brief: "Illustrations, ornaments,
stamps and scan borders are not text and get no lines"). Where a stamp lies over real text, the text line keeps its
full extent and the stamp ink must not move its baseline or font lines; ideally the unrolled line image shows the
stamp faintly or not at all. Ring lettering is rotated and follows a circle: it fails the "same orientation as its
neighbours" test, as well as the faintness test below.

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

Requirement:
- Measure the contrast of each candidate line's ink **relative to the page's own text** (and, for the darkest pages,
  relative to the local background), and discount detections that are much fainter than the page's text. "Relative"
  matters: a uniformly faded scan is still all text; only ink much fainter than the rest of the same page is
  suspect.
- Show-through from the back of the page is also mirrored and usually out of register with the front lines; use that
  as a second cue where it helps.
- A faint candidate is reported as such with its contrast in the line record, not silently kept or silently dropped,
  so the review page can show what was discounted.

## 3. Jagged line regions

**Owner, an-ef481610a820-p000181:** "the lines are very jagged, the areas you are presenting seem to spike
vertically, which line geometry on pages shouldn't be like that."

Measured: on that page the region edges jump by a median of 1.3 x-heights from one pixel column to the next and by up
to 14.4 (line 30). On s2-0ce9d1025b3f23c7119e-p00001 the median jump is 8.2 x-heights; on
s2-09f5dfca4af4d74173c6-p00005 the largest is 73.

Cause (`_boundaries`): the edge between two lines is the midpoint between the lower line's top and the upper line's
bottom, chosen **pixel column by pixel column** against whichever line is the neighbour in that column. Wherever a
short or spurious line (an accent row, a stamp mark, a ghost) starts or ends, the neighbour changes and the edge
jumps; where there is no neighbour the edge falls back to the line's own font band.

Requirement:
- The region edges are smooth curves of the same kind as the baselines (they follow the column's shared skew and
  curve), not per-column midpoints.
- Neighbours are the real text lines of the same column. Rejected marks (sections 1–2) do not take part.
- The edges still tessellate (no gaps, no overlaps), and each region holds all of its line's ink: accents above,
  descenders below. Where a neighbour's accents or descenders reach across the seam, the seam bends around that mark
  locally rather than cutting either line's ink.

## Checks for the next round

Report per page, on all 48 development pages, then on the held-out pages:
1. **Font lines:** for each line, the distance from each of the four lines to the ink it should touch (letter bottoms,
   small-letter tops, capital tops, descender bottoms), in x-heights; how many lines took a value from neighbours.
2. **Accent-only lines:** lines with no letter bodies in their mean–base band (should be 0); pairs of lines closer than
   half the column's line spacing (should be 0).
3. **Faint detections:** each line's ink contrast relative to the page's text; how many lines were discounted and why.
   On the six pages named above, the counts by name.
4. **Smoothness:** the largest jump of each region edge per pixel column, in x-heights (should be well under 0.1
   except where a seam bends around a mark).
5. The checks already in the brief: cut letters at region edges, foreign ink, rule crossings (0), overlaps (0),
   broken lines (~0).

## Pages and segments named by the owner

| Page | Segment / place | Issue |
|---|---|---|
| an-d6fd2cf2f618-p000047 | s00006, first two lines | accents split from their letters |
| an-d6fd2cf2f618-p000047 | s00008 | library stamp over the text |
| an-d6fd2cf2f618-p000047 | s00011–s00017 (x 809–1160, y 1488–1821) | stamp lettering taken for characters |
| an-ef481610a820-p000181 | whole page | jagged line regions |
| s2-09f5dfca4af4d74173c6-p00005 | faint left half | faint detections not discounted |
| s2-0ce9d1025b3f23c7119e-p00001 | faint lines | faint detections not discounted |
| s2-5ca02b142a2a3eaf078a-p00002 | bottom right corner | ghost detection |
| s2-d1ed1c2db37f431f4acb-p00001 | bottom left corner | show-through from the back of the page detected |
