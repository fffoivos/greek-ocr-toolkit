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
5. **Lines cross into the other column, and across the fold of a two-page spread**, and the crossing check did not
   notice.
6. **Text is missed:**
   - mostly where the rule detector takes text for a rule: a darker grey corner of the page, the curled starts of lines
     next to the binding, text printed over a stamp;
   - also an all-capital running head.
7. **Illustrations and ornaments get lines.** The owner calls this a main issue: "ideally we would avoid those that
   are not letters".
8. **A letter-spaced heading is broken:** its first letter is split off at a wide letter gap.

**Open problem, not for this round:** a large first capital (drop cap) spanning several lines. See the end of the
document.

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

**What it must do instead:** measure every guide line on each line from its own class of ink, so that all of them
follow the line's skew and curve. The required design is at the end of this section, after the owner's accent
proposal and the measurements behind it.

### The owner's proposal: a separate accent band (2–3 lines) on top of the 4 font lines

**Owner:** "one of the reasons that there might be bad 4 font lines here, is that there might need to be a distinct
accent region from the fonts so maybe 2-3 lines for accents + 4 lines for fonts."

The measurements support it. They are rough: components were sorted by shape on the lines with ≥ 15 components. The
values are heights above the baseline, in x-heights (10th percentile / median / 90th percentile):

| | an-d6fd2cf2f618-p000047 | s2-49598b2e848ab1f0ee1e-p00001 |
|---|---|---|
| tops of small letters | 0.90 / 1.00 / 1.10 | 0.91 / 0.98 / 1.06 |
| tops of capitals and ascenders | 1.43 / 1.59 / 1.87 | 1.47 / 1.60 / 1.87 |
| bottoms of accents and breathings | 1.19 / 1.39 / 2.50 | 1.18 / 2.04 / 2.77 |
| tops of accents and breathings | 1.63 / 1.86 / 2.97 | 1.62 / 2.42 / 3.13 |
| descender depth below the baseline | 0.42 / 1.05 / 1.38 | 0.36 / 0.63 / 1.44 |

What this shows:
- On these pages, accents occupy their own band: about 1.2–1.9 x-heights over small letters (higher over capitals
  and stacked marks).
- That band **overlaps the height of the capitals** (about 1.4–1.9). So one "top" line cannot stand for both, and
  height alone cannot tell an accent from a capital. What separates them is that an accent is a small mark detached
  above a letter body.
- Astra's pooled top line (−1.91 x-heights on p000047, −1.84 on Vouli p00001) is effectively the **top of the
  accents** (median 1.86 on p000047), not the top of the capitals.

### Required design: 4 font lines + 2 accent lines, all following the line's curve

**Owner, on this design:** "this is basically important for following the curve or skew of the lines." The guide
lines are not decoration. They are how the detector **sees the curve**. A curve is measured from letter positions
along the line, and every letter contributes only if each piece of ink is matched to the right guide line. A capital
top read as a mean-line point, or an accent read as a capital top, bends the curve where the paper does not bend.

**The lines**, top to bottom. Typical heights are from the two pages measured above, in x-heights above the baseline.

| Line | Measured on | Typical height |
|---|---|---|
| accent top | tops of the detached marks above small letters | ~1.9 |
| accent bottom | bottoms of those marks | ~1.2–1.4 |
| capital / ascender | tops of capitals and of β δ ζ θ λ ξ φ ψ | ~1.6 |
| mean line | tops of small letters (α ε ι ο ν σ τ υ …), accents removed | 1.0 |
| baseline | bottoms of letters without descenders | 0 |
| descender | bottoms of β γ ζ η μ ξ ρ φ χ ψ ς | ~0.6–1.0 below |

- A third accent line is added only if accent tops prove to fall at two distinct heights (single marks, and stacked
  marks such as ἄ ἆ ὅ); otherwise stacked marks simply reach higher inside the same band.
- Accents on capitals sit to the **left** of the capital, at capital height (Ἀ Ἑ Ὁ). They belong to the capital on
  their right, not to the accent band.
- Iota subscripts and other marks below a letter belong to that letter and sit in the descender zone; they get no line
  of their own.

**Step 1: sort the ink.** Before any line is fitted, every component of a line is classed as one of:
- body on the baseline;
- body with a descender;
- tall body (capital or ascender);
- mark above a letter (accent, breathing, diaeresis);
- mark below a letter;
- punctuation (the raised dot · sits at the mean line and must not pull it; commas and full stops sit at the baseline
  but are too small to count as letter bottoms);
- not text (sections 3 and 7).

An accent that has run into its letter in a poor scan is split at the narrowest point just above the mean line.

**Step 2: give every mark an owner.** A mark belongs to the letter body below it, or, before a capital, to the capital
on its right; it never belongs to a line of its own (section 2).

**Step 3: fit the curve from all the classes together.** This is where the curve or skew is found.
- Each class gives sample points along the line, at each letter's x position:
  - body bottoms give baseline points;
  - small-letter tops give mean-line points;
  - tall tops give capital-line points;
  - descender bottoms give descender points;
  - mark bottoms and tops give accent points.
- On a printed page, within one line and one font, these six curves are the same shape, offset vertically. Fit **one
  shape per line** to all the points at once, with one vertical offset per class. This roughly triples the number of
  points behind the shape compared with the baseline alone, which answers the owner's round-1 remark: "we need many
  points to find an orientation".
- The shape is shared and smooth down the column. Neighbouring lines have nearly the same shape, and it changes
  gradually from one line to the next, as the algorithm's shared page geometry says. A short line takes its shape from
  its neighbours and fits only its offsets.
- Where the paper curls (the binding side of s2-3229200bf47ca465a42d-p00004, the end bends the crop tools already
  handle), the letters are also foreshortened. So the gap between the curves may shrink slowly towards the curl. The
  fit allows the x-height to vary slowly along the line, never abruptly.
- Each offset is a robust centre (a median) of its own class, never the 98th percentile of everything. One stray
  mark cannot move a line.

**Step 4: per-font ratios, used for borrowing and checking.**
- A font is a group of lines with the same x-height and proportions: body, footnote, heading, italic. Each font keeps
  its ratios: capital height, descender depth, accent bottom and top, all relative to the x-height.
- A line lacking a class borrows that line from its font's ratios and records it as borrowed. Examples: no
  descenders, or no small letters (an all-capital head like «ΧΡΗΣΤΟΗΘΕΙΑ», whose mean line is unknown).
- Order is a check: descender < baseline < mean line < accent bottom, and capital ≤ accent top. A candidate line whose
  classes break the order or its font's ratios is wrong. The accent rows on p000047 and Vouli p00001 fail it: they
  have no bodies.

**Step 5: the segments follow from the lines.**
- A line's region runs from just above its accent top to just below its descender line, along the same curve.
- The boundary between two lines lies where the upper line's descenders meet the lower line's accents. On tightly set
  pages (Vouli) these overlap. There the boundary follows which line each component belongs to, rather than a straight
  cut, so neither line's ink is cut (sections 2 and 4).
- The unrolled image is straightened along the fitted shape. The baseline and mean line are placed at fixed heights,
  with the accent band kept above them.

**Step 6: show and check.**
- The review page draws all six lines, each in its own style.
- The per-line check (Checks, item 1) is how far each class of ink sits from its own line. On a curled or skewed line
  that distance stays small along the whole length, not only on average.

The crop tools already measure the rise and drop per crop (`report.line_record`, `baseline.text_lines`). Reuse them,
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

### an-d6fd2cf2f618-p000047: the text under the stamp is lost

**Owner:** "header and text over watermark is not detected an-d6fd2cf2f618-p000047." (The header is in section 6.)

Measured:
- Six text lines cross the stamp: lines 30 and 32–36. Each stops where the stamp begins, at x 754–907, while the printed
  text runs on to x ≈ 1095.
- What is lost: «… τὸν φίλον ἀνα-», «… ἀπολογησάμενος συγ-», «… δικαίως ὀργίζοιο.», «… φίλον ἔρις ἐμπέ-», «…
  ἀκαιρίμαν, τοῦτο», «… ἀναιδῶς πρόφερε,» and the catchword «ἀμνη-».
- The rule mask covers 30% of the stamp area (x 780–1178, y 1450–1850), and with it the letters printed there.
- Over the stamp there are only fragment lines on the stamp's lettering (lines 29, 31 and 37–42; see above).

### an-3352d912f2e9-p000104-s00019: text printed over the stamp is not detected

**Owner:** "it also has a watermark which the letters are not detected on top of it."

This is the opposite failure to p000047: here the text over the stamp is lost. The "watermark" is the same round
library stamp, at the bottom right of the page.

Measured:
- Where the stamp lies (x ≳ 950, y 1600–1900), the pixel segmenter cuts the text into narrow slivers (segments
  s00020–s00029, 6–67 px wide).
- Line 27 («ἀγροικίας, ἧκεν ὡς αὐτὸν εἰς ἄστυ. ὁμοιωθεὶς ἀν-») stops at x 989, and line 28 («θρώπῳ, καὶ παρ' αὐτῷ
  κατήχθη. Τῆς δὲ τῶν βοῶν») stops at x 947. The printed text runs on to about x 1290.
- Over the stamp there are only fragments: lines 29–33, each 5–60 px long, with 1–4 components.
- «Τῆς δὲ τῶν βοῶν» and the catchword «ἀπω-» get no line.

**Requirement:** this is the case covered above, "the text line keeps its full extent". Text printed over a stamp or
watermark is text. The stamp must neither carry lines of its own nor cut the text lines that cross it.

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

### an-a73d22211479-p000301: the two columns joined across a broken rule

**Owner:** "there are many unions among the boundary for the bottom half of the page."

The page has two columns separated by a printed vertical rule at x ≈ 883.

Measured:
- The rule is printed as separate pieces about 80 px (3.5 x-heights) long, with short breaks between them. It has ink
  in 88–97% of rows from y 400 to y 2200.
- The rule mask (`pixel_segments._rule_mask`) marks it as a barrier above y ≈ 1230 and below y ≈ 1655, but not between
  them (0–15% of rows), although the pieces there are as thin and straight as the others.
- The pixel segmenter then makes one segment across both columns there (s00007, x 79–1703, y 1176–1486).
- Lines 27–33 (y 1319–1629) each run from x ≈ 80 across the rule to x ≈ 1680–1693, joining the two columns.
- At the top, lines 4 and 5 (y 346, 398) are joined the same way, where the rule's ink is weaker.
- Lines 6, 24 and 26 lie wholly in the right column but are labelled column 0.
- The checks report 0 crossings, 80 of 82 lines with cut ink and 78 with foreign ink.

**Requirement:**
- A dashed or broken rule is a rule. Collinear thin pieces with short breaks are joined into one boundary over the
  column's full height.
- One missed piece must not open the boundary. This is the same full-height column structure the cases above
  require.
- Column labels follow that boundary.

### an-5c093c79d6bb-p000199: the first lines of the two facing pages joined

**Owner:** "Bad connection of the first two lines of the two opposing pages here."

The scan is a two-page spread (pages 382 and 383) with a white fold between them.

Measured:
- Lines 20, 21 and 22 each run across both pages (x ≈ 670–2744). They join the first three lines of page 382 to the
  page number «383» and the first two lines of page 383 («ἐχθρικῶς· ἐκεῖνος ὁποῦ ἀλείφει κεντᾷ …», «κάμνει
  πλεσιωτέραν τράπεζαν …»).
- Further down, the pages are kept apart: left-page lines end at x ≈ 1605, right-page lines start at x ≈ 1747. The
  fold gap is therefore about 140 px, 5.9 x-heights.
- At the fold the joined lines kink. Line 20's baseline runs y 200 → 165 → 206 between x 1500 and 1763.
- Checks report 0 crossings.

### an-9ea1564fcf4f-p000013: the two facing pages joined all the way down

**Owner:** "Similarly bad connections between the two pages on all the pages here."

Measured:
- 26 lines (lines 34–59) each run across both pages, from x ≈ 440 to x ≈ 2230–2850. That is every line of the
  facing text from the top down to the start of the footnotes.
- Only the last six text lines of the left page (lines 60–65, ending at x ≈ 1525) and the lower lines of the right
  page stay separate.
- The fold is narrow here. The left page's text ends at x ≈ 1525 and the right page's starts at x ≈ 1570, so the gap
  is about 45–80 px, 2.5–4.5 x-heights (body x-height 18 px).
- The baselines of the two pages are almost level at the fold (e.g. line 50: y 1048 at x 1500, 1055 at x 1650), so
  nothing local stops the join.
- Checks report 0 crossings.

**Cause (both spreads):**
- `_coalesce_lines` extends a line across any gap of up to **10 x-heights** whose two ends are level within half an
  x-height, unless a detected rule or gutter blocks it.
- The fold of a spread was not detected as a boundary at those heights. Its gap (2.5–6 x-heights) is well within the
  10.

**Requirement:**
- The fold of a two-page spread is a page boundary: the strongest column boundary there is. No line, segment or
  region crosses it.
- Find it from the whole spread, not from the gap at one height. Evidence that runs the full height:
  - a white or shadowed strip down the middle;
  - two text blocks with their own margins and their own line phase (the baselines of facing pages are generally
    not in step);
  - page numbers and running heads at both tops;
  - often, dark scan borders at both outer edges.
- More generally, a gap of several x-heights between level line pieces is joined only when the column structure says
  both pieces are in the same column.

### Seen while checking these spreads (not named by the owner): lines on the book edge

On both spreads the scanned edge of the book block on the left (the stacked page edges and a dark scan border) carries
many lines: 20 of the 77 lines on an-5c093c79d6bb-p000199 and 37 of the 96 on an-9ea1564fcf4f-p000013 end left of
x 480 and 400. These are scan borders (section 7: not text, no lines).

## 6. Text missed

Most of these cases come from the rule mask (`pixel_segments._rule_mask`) taking text for a rule. The two stamp cases
in section 3 are the same; on p000047 the mask covers 30% of the stamp area. The last case here has a different
cause.

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

### an-d6fd2cf2f618-p000047: the running head «ΧΡΗΣΤΟΗΘΕΙΑ. 43»

**Owner:** "header … is not detected."

Measured:
- The running head lies at y ≈ 63–139: 47 components, capitals about 34 px tall against a body x-height of 21.
- Its ink is intact and not masked as rule. It falls inside pixel segment s00002 (y 73–284).
- No line is made for it: the first line of the segment is the first text line (line 2, baseline y 166).
- It is an all-capital line with no small letters from which to measure an x-height. That is the likely reason, not
  yet traced in the code.

**Requirement:**
- Headings and running heads in capitals are lines. Their geometry comes from their capitals: their x-height is
  unknown, so their mean line is borrowed from same-size type or left undetermined and recorded as such. They must not
  be dropped.
- Page numbers beside them belong to the same line or form their own short line, as the column structure says.

## 7. Illustrations and ornaments

### an-1f8e7d022643-p000003: the ornaments of a title page

**Owner:** "The main issue are illustrations in an-1f8e7d022643-p000003 seems to cause a lot of issues; ideally we
would avoid those that are not letters."

The page is the opening of «ΑΚΟΛΟΥΘΙΑ ΤΟΥ ΑΓΙΟΥ ΕΝΔΟΞΟΥ ΝΕΟΜΑΡΤΥΡΟΣ ΚΩΝΣΤΑΝΤΙΝΟΥ». It carries:
- a printed headpiece at the top: two vine borders and a floral band;
- a dotted rule under the title;
- a picture initial «Τ» (a building inside a frame);
- a decorated initial «Μ»;
- the library stamp at the bottom right.

Measured:
- The headpiece (y 123–394) carries **10 lines** (lines 1–10): x-heights 27–44 px against the page's 28, support 0–9
  components, mostly borrowed geometry. They come from the pixel segmenter's segments s00000–s00007.
- Line 0 sits on the scan edge (x 6–10).
- The decorated «Μ» gets a fragment line (line 26, x 161–185).
- The dotted rule (segment s00013) correctly gets no line.

The brief already put these out of scope as text ("Illustrations, ornaments, stamps and scan borders are not text and
get no lines"). The detector does not yet tell them apart.

**Requirement:**
- Tell letter-like ink from ornament before lines are formed, at the component level. Ornament components are:
  - larger and denser than letters of the surrounding size;
  - repeated in regular bands (vines, fleurons);
  - without the letter spacing, x-height band or shared baseline of a text line.
- Ornaments, pictures and the frames of decorated initials get no lines and no segments.
- They must not move the geometry of the text lines next to them (the shared page geometry must not pool them).
- Where an initial is a real letter inside a picture («Τ» here), the letter belongs to its line. If that cannot be
  done yet, it falls under the drop-capital open problem below; it must not produce a fragment line.

### an-d6002cf45e4d-p000058: an engraving and a picture initial

**Owner:** "the image causes problems at an-d6002cf45e4d-p000058."

The page carries:
- a large engraving (ruins, figures, instruments), x ≈ 340–2440, y ≈ 280–1880;
- the Cyrillic caption «НОВАЯ АЛЕКСАНДРІЯ»;
- a framed woodcut initial (the «Н» of «Новая») at the bottom left;
- five lines of Cyrillic text, the first four set beside the woodcut.

Measured:
- **The engraving:**
  - The rule mask marks 36% of it as rule.
  - The pixel segmenter cuts it into about 30 narrow vertical segments (s00000–s00034, many only 5–60 px wide).
  - The detector puts **16 lines** in the picture (lines 0–16), each with 0–2 components and borrowed geometry.
- **Regions stretched into the picture and the empty space:**
  - The caption's line (line 17) has a region reaching up to y 1372, inside the engraving, and down to y 2487.
  - The last text line's region (line 18) reaches up to y 2027 at its left end, 940 px above its baseline, where it
    has no neighbour above.
- **The woodcut initial:**
  - The rule mask marks 86% of it as rule. It gets no line, which is right.
  - The last text line, «въ небольшомъ шокмо перешейкѣ, межъ двухъ гаваней; на мѣ-», starts at x 542, but the
    printed line starts at x ≈ 294. Its first word and a half, «въ небо…», have no line, although that ink is not
    masked. The cause is not traced; the woodcut is directly above it.
- **A broken line:** the line beside the woodcut that ends «… стѣснены» is broken into two lines (lines 22 and 23, the
  page's broken pair).

**Requirement:** as for the ornaments above.
- The engraving and the woodcut frame get no segments and no lines.
- Regions never extend into a picture. A line with no neighbour above or below takes the ordinary margin for its size,
  not the empty space up to the next ink.
- The text beside or under a picture keeps its full extent.
- The woodcut's letter «Н» is the drop-capital open problem below.

## 8. A letter-spaced heading

### an-1f8e7d022643-p000003: «Α Κ Ο Λ Ο Υ Θ Ι Α»

**Owner:** "and also the unusual spacing between letters at ΑΚΟΛΟΥΘΙΑ."

Measured:
- The heading is set in capitals about 81 px tall, with wide letter spacing.
- Its first letter «Α» (x 101–178) became a segment of its own (s00009) and a line of its own (line 12). That line has
  1 component and borrowed geometry with a 28 px x-height, the page's body size, not the heading's.
- The rest, «ΚΟΛΟΥΘΙΑ», is line 11 (segment s00010, x 258–1426, x-height 81).
- The gap between «Α» and «Κ» is 80 px: about one letter of the heading, but almost three x-heights of the page's
  body text.

**Requirement:**
- Gaps are judged against **the line's own letter size and its own letter spacing**, not the page's body x-height.
  A gap no wider than the heading's own spacing between letters is not a word or column break.
- A column gap must run down the column, not only across one or two lines.
- A heading stays one line from its first letter to its last.

## Open problem, not for this round: large first capitals (drop caps)

### an-3352d912f2e9-p000104-s00019

**Owner:** "is very special it has a large first capital letter, we should leave this as an open problem for now, but
we might need to consider it later."

What happens now:
- The paragraph «Ἑρμῆς βουλόμενος τὴν Τειρεσίου μαντικὴν …» opens with a drop capital «Ε» two lines tall.
- No line includes it: line 25 starts at x 288 and line 26 at x 254, to the right of the capital.
- The same page has a second drop capital «Ε», at «Ἑρμῆς γνῶναι βουλόμενος …». The picture initial on
  an-1f8e7d022643-p000003 (section 7) is of the same kind.

Not required this round. To be decided later: whether the capital is read as the first letter of the first line,
handled as a separate one-letter item, or left to the layout stage.

## Checks for the next round

Report per page, on all 48 development pages, then on the held-out pages:
1. **Font and accent lines:** for each line, the distance from each of the four font lines (and the accent lines) to
   the ink it should touch, in
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
6. **Column crossings:** the count, measured against the full-height column boundaries and the fold of a spread
   (must be 0).
7. **Missed text:** ink of text size left without a line, and the share of the page marked as rule. Report both per
   page.
8. **Non-text ink:** lines and segments on ornaments, pictures, stamps and scan edges (should be 0), and text lines
   cut short where a stamp or watermark crosses them (should be 0).
9. **Headings:** printed lines broken into more than one line at a letter gap (should be 0).
10. **The checks already in the brief:** foreign ink, boundary overlaps (0) and broken lines (~0).
11. **Every case in the table below, by name:** what the new output does there, with its image.

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
| 15 | an-1f8e7d022643-p000003 | headpiece, decorated initials | illustrations cause many issues; avoid what is not letters (a main issue) | 7 |
| 16 | an-1f8e7d022643-p000003 | «ΑΚΟΛΟΥΘΙΑ» | unusual spacing between the letters | 8 |
| 17 | an-3352d912f2e9-p000104 | s00019, text over the stamp | letters on top of the watermark not detected | 3 |
| 18 | an-3352d912f2e9-p000104 | s00019, first letter | large first capital: open problem, later | open |
| 19 | an-5c093c79d6bb-p000199 | first lines of both pages | lines of the two facing pages joined | 5 |
| 20 | an-9ea1564fcf4f-p000013 | all lines of both pages | lines of the two facing pages joined | 5 |
| 21 | all pages | — | proposal: a distinct accent region, 2–3 accent lines + the 4 font lines | 1 |
| 22 | an-a73d22211479-p000301 | bottom half, both columns | many unions across the column boundary | 5 |
| 23 | an-d6002cf45e4d-p000058 | engraving, woodcut initial | the image causes problems | 7 |
| 24 | an-d6fd2cf2f618-p000047 | running head «ΧΡΗΣΤΟΗΘΕΙΑ. 43» | header not detected | 6 |
| 25 | an-d6fd2cf2f618-p000047 | text under the stamp | text over the watermark not detected | 3 |
