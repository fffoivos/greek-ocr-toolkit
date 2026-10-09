# Owner review of the page-lines detector, round 3 (9 October 2026)

This is the owner's review of Astra's round-3 output on the 48 development pages:
- branch `astra/page-lines-3`, commit 0c08015;
- review page https://claude.ai/artifact/7rt1qMCTEkPsvkj3iyrmjz.

Lines marked **Owner:** are the owner's own words, verbatim apart from typo fixes. The measurements, stated causes and
requirements were written by the coordinator from the round-3 outputs (`.astra/out/<key>.lines.json`, `.segments.json`)
and the page images. Line numbers are the indices on the review cards (indices into `<key>.lines.json`).

The cases are numbered after the 25 of round 2 (`OWNER_PAGE_LINES_REVIEW_ROUND2_20261009.md`). That document, its
required design for the guide lines and its checks remain in force; every round-2 case not mentioned here is to be
re-checked, not assumed fixed.

## The owner's overall comments

- **Verdict:** "ok this is quite good and I think we shouldnt improve on it before we complete the first work cycle."
- **Generalisation before trust:** "we should run this on 50 diverse new pages though before we are sure of the
  quality of the code."
  - That run is under way on the MacBook: 50 pages, 25 Anemi and 25 Vouli, each from a different book or PDF, none of
    them among the 72 pages used so far. It runs the frozen round-3 code, commit 0c08015.
  - Its results will be reviewed before any further fix.
- **Per-letter ink analysis:** "Does astra's code have per char detection so we can do the ink analysis like before?"
  - Not yet. Each line knows its own connected components (`component_ids`) and their classes; the output keeps only
    the class counts (`ink_classes`).
  - The per-letter ink state of the crop review (intact, merged, broken or faint) is not produced for page lines. It is
    a small addition: run the letter tool on each final line and write each letter's box and state.

## 26. s2-0ce9d1025b3f23c7119e-p00001: still joined across the columns, and the faint letters still detected

**Owner:** "s2-0ce9d1025b3f23c7119e-p00001 is still not solved, we have connections across columns, and the faint
letters are detected."

This is round-2 case 8 (faintness), not fixed, together with a column-crossing case on the same page.

Measured on the round-3 output:
- **The columns.** The page has two columns, with a column gap at x ≈ 1715 that has no ink at all down the page.
- **Lines crossing the gap.** Of the page's 64 lines, 34 are discounted as faint. Of the 30 active lines, **9 run
  across the gap**: lines 3, 4, 9, 11, 13, 19, 21, 23 and 24, each spanning from x ≈ 235–425 to x ≈ 2580–3190.
- **How the faint ink stays in.** In 7 of the 9, one half is faint and the other is printed text from the other column:

  | Line | Baseline y | Left half darkness | Right half darkness |
  |---|---|---|---|
  | 3 | 274 | 185 (faint) | 78 |
  | 4 | 339 | 163 (faint) | 71 |
  | 9 | 551 | 187 (faint) | 75 |
  | 19 | 1000 | 70 | 180 (faint) |
  | 21 | 1065 | 73 | 196 (faint) |
  | 23 | 1131 | 70 | 202 (faint) |
  | 24 | 1194 | 71 | 159 (faint) |

  Darkness is the median grey of the darkest fifth of the pixels between mean line and baseline; 0 is black and 255
  white.

  The faint half rides along with a dark line from the other column. The line as a whole passes the faintness test,
  with contrast 0.87–1.01 against the page's text, so the faint letters are kept.
- **Two dark-to-dark joins.** Lines 11 and 13 join two dark halves across the gap.
- **The checks report 0 rule or gutter crossings.**

What this means for the requirements of round 2:
- Column boundaries (round 2, section 5) must hold before lines are joined. A full-height empty gap is a column
  boundary even without a printed rule.
- Faintness (round 2, section 3) must be judged on each piece of a line, not on the line as a whole. A faint piece is
  discounted even when it is joined to dark text; with the column boundary respected, the two would not be one line.

## 27. s2-93f8070059f938bda524-p00001: a good result, kept as a reference

**Owner:** "while for example s2-93f8070059f938bda524-p00001 is very good, even though it has faint letters in the
background."

Measured on the round-3 output:
- The page has two columns. It has 129 lines, of which 12 are discounted as faint.
- No active line crosses the columns: the widest active lines are 1422–1450 px, about one column's width on a
  3271 px page, and every active line lies in column 1 or 2.

This is how case 26 should come out: the faint background letters are discounted, and every line stays within its
column. Any change made for case 26 must keep this page as good as it is.

## 28. s2-831443dc5e6f1ccfbaf5-p00020: the first two table columns not detected

**Owner:** "s2-831443dc5e6f1ccfbaf5-p00020 the first 2 columns are not detected."

The page is a printed table (ΝΟΜΟΣ ΑΙΤΩΛΙΑΣ καὶ ΑΚΑΡΝΑΝΙΑΣ). Its first two columns are the row numbers 1–34 and the
names of the δήμοι (Μεσολογγίου … Ἐχίνου), with the heading «ΔΗΜΟΙ».

Measured on the round-3 output:
- **Nothing starts left of x 637.** No pixel segment and no active line starts there: every one of the 167 segments
  starts at x ≥ 637, and the leftmost active line starts at x 637.
- **The pixel segmenter removes the ink there before segmenting.** Left of x 637 the page has 128,544 dark pixels,
  but only 4,826 (4%) survive into the segmenter's ink.
  - It is not the rule mask, which covers 6–7% of that strip, about as much as elsewhere on the page.
  - The ink is dropped by the earlier rejection of frames, large graphics and scan borders (`pixel_segments`, the
    `keep` mask).
  - It also declares a full-height gutter at x 551–637, so the strip is treated as outside the text.
- **Text above the table loses its start too.** The same strip holds the beginnings of «Διαφορὰ ἀναλογισθέντων
  ποσῶν» and «Ἀναλογία ἀποδοτέου πλεονάσματος …». Their lines start only at the strip's edge.

Requirement:
- The table's outer frame and its rules are graphics. The text inside the frame is text, and must survive the frame
  rejection. Rejecting a frame means removing its strokes, not everything near it or connected to it.
- A gutter is declared only where there is no text, never over a column of row numbers and names.
- Tables stay in scope as before: text pieces that never cross a rule or a wide gap. Table structure itself is
  Docling's job.

## 29. s2-9de6cda8f03f0fc60a58-p00005: lines still joined across the columns

**Owner:** "s2-9de6cda8f03f0fc60a58-p00005 still has connections among the columns."

The page (Vouli, page 485) has two columns separated by a solid printed vertical rule. **The rule is slanted with
the page.** Its x position, traced every 400 px down the page, runs from x 1676 at y 300 to x 1729 at y 3900: 53 px
over 3,600 px, about 0.8°. It is dark in every row of every 200-row window.

Measured on the round-3 output:
- **Lines across the rule.** Of the 96 active lines, **37 run across the rule** (more than 30 px either side), from
  the top of the page (baseline y 116) to the bottom (y 4284). Most active lines are 2,900–2,930 px wide on a 3,323 px
  page, so each spans both columns.
- **Segments across the rule.** 8 of the 38 pixel segments span the rule.
- **The rule is only partly marked.** The rule mask marks it in some stretches and not others: 0–81% of rows per
  200-row window, and none at all in four of the ten windows.
- **No gutter is found.** No full-height gutter is found beside it, so nothing stops the joins.
- **The checks report 0 rule or gutter crossings.**

(An earlier version of this note called the rule faint and broken. That was wrong: it was measured at one fixed x,
and a slanted rule leaves any fixed x.)

Requirement:
- A rule is found along its own direction, not along a pixel column. A page scanned a little askew has slanted rules
  and slanted gutters, and both must be found as straight lines at that slant. The page's skew is the same skew the
  text lines show.
- The rule is a column boundary over its full length and must hold before any line is joined.
- The crossing check must use the same slanted boundary.

## 30. s2-d1ed1c2db37f431f4acb-p00001: lines joined across the columns

**Owner:** "also this one has connections across the columns s2-d1ed1c2db37f431f4acb-p00001."

This page is also round-2 case 10 (show-through in the bottom-left corner). It has two columns separated by a solid
printed vertical rule, again slanted with the page: from x 1578 at y 300 to x 1605 at y 3900, 27 px over 3,600 px
(about 0.4°). The rule is dark in every row of every 200-row window.

Measured on the round-3 output:
- **Lines across the rule.** Of the 82 active lines, **43 run across the rule**, from baseline y 303 down to y 3318.
- **Segments across the rule.** 10 of the 17 pixel segments span the rule.
- **The rule is almost never marked.** The rule mask marks it in only two of the ten 200-row windows (58% and 100%
  of rows there), and not at all elsewhere.
- **No gutter is found** beside it.
- **The checks report 0 rule or gutter crossings.**

Requirement: as for case 29. Cases 26, 29 and 30 together show that the column boundary is still not found from the
page's column structure. A straight full-height rule, slanted with the page, is the clearest boundary there is.

## 31. s2-3229200bf47ca465a42d-p00004: the first characters of the bottom lines are still missed

**Owner:** "in s2-3229200bf47ca465a42d-p00004 at the bottom lines 32-46 have missed first chars."

This is round-2 case 14 (the curled starts of the lines on the binding side), improved but not fixed.

Measured on the round-3 output:
- **Line starts.** In round 2 the bottom lines started at x ≈ 184–224. In round 3 lines 32–44 start at x 109–123,
  and line 39 at 139.
- **The printed lines begin further left.** Most begin at about x 85–100 at this height (read from the page image).
  The first one or two letters of each line still lie left of the line's start.
  Examples: «π» of «προταχθῆ» (33), «Ἡ» of «Ἡ Βουλὴ» (35), «π» of «προβῇ» (40), «Β» of «Βουλευτῶν» (41).
- **Line 45** («Εἰς τοῦτο συνεφώνησε …») starts at x 167 and misses the whole first word «Εἰς».
- **The baseline curve at the start.** On several lines the baseline bends away from the letters over the first
  letters, where the paper curls (e.g. lines 36 and 37). So the curl itself is not yet followed to the line's
  first letter.
- Line 46 is a discounted candidate at the page's bottom edge.

Requirement (round 2, section 6 and the guide-line design in section 1):
- A line follows its curl to its first letter, the same way it does at its end.
- The guide-line fit near the start uses the first letters' own ink, so the baseline stays on their bottoms.

## Every case of this round

| # | Page | Place | What the owner saw | Round-2 case |
|---|---|---|---|---|
| 26 | s2-0ce9d1025b3f23c7119e-p00001 | whole page | still joined across the columns; faint letters still detected | 8 |
| 27 | s2-93f8070059f938bda524-p00001 | whole page | very good, despite faint letters in the background: the reference to keep | — |
| 28 | s2-831443dc5e6f1ccfbaf5-p00020 | table, left side | the first two table columns are not detected | tables (round-1 remark) |
| 29 | s2-9de6cda8f03f0fc60a58-p00005 | whole page | lines still joined across the columns (slanted rule) | — |
| 30 | s2-d1ed1c2db37f431f4acb-p00001 | whole page | lines joined across the columns (slanted rule) | 10 (show-through, same page) |
| 31 | s2-3229200bf47ca465a42d-p00004 | bottom, lines 32–46 | first characters still missed | 14 |
| 32 | an-1436ae03653f-p000163 (50-page set) | s00039, ornamental border | non-text line passed to OCR | 7 (ornaments) |
| 33 | an-7a2b17a3fb0f-p000200 | the spread's tables | cells missed, fused, or with characters missed | tables |
| 34 | an-a3c2bdf81256-p000112, s2-80513ae109b4f749ca58-p00003 (50-page set) | upper half | lower-half column boundary enforced in the upper half | — |
| 35 | s2-6419488b7f8e69fd20da-p00001 (50-page set) | whole page | no check of writing orientation (sideways table) | — |


## Tables: first find out what Docling needs

**Owner:** "Also we have trouble with tables, but we need to determine first what specs docling requires from us to
compile proper tables." And: "make sure to record an independent search we should do to make sure we offer docling
what it needs to compile tables."

**To do:** an independent search, done before any further table work and before any table requirement goes to the
implementer. It should establish what Docling's table pipeline consumes from an OCR plugin:
- whether it needs word-level, cell-level or line-level text cells;
- how text cells are matched to the predicted table cells;
- what happens when one text cell spans two table cells or crosses a rule;
- what coordinates and confidence it expects;
- whether it re-runs anything on the table region itself.

Sources: Docling's code (table structure stage, cell matching, the OCR model interface) and its documentation,
checked against our plugin contract (`docs/` and `tests/test_docling_contract.py`). The text layer is not a
reference for this.

The search should be done independently of the page-lines implementer, and its answer recorded as the table
requirement. Until then, cases 28 and the round-2 table pages stay recorded but are not specified further. Earlier
note (not verified for tables): Docling runs OCR before layout, and the plugin receives the page image and bitmap
rectangles and returns text cells.

## Findings on the 50 new pages

The round-3 code was run, unchanged (commit 0c08015, pixel-only), on 50 pages it had never seen: 25 Anemi and 25
Vouli, each from a different book or PDF, none among the 72 pages used before. All 50 ran without failure, in 633 s
of compute on the MacBook. Review page: https://claude.ai/artifact/QkjS6GT3Bxyr5wqgd5BTVz.

### 32. an-1436ae03653f-p000163-s00039: a line on an ornamental border, passed to OCR

**Owner:** "we should be able to avoid passing to OCR non-text containing lines. Maybe there is some feature we can
detect."

The segment (x 373–2003, y 3512–3556) is a printed ornamental border: a band of repeated black fleurons along the
foot of the page. The detector keeps one active line on it (line 36, x 705–2003). It is not discounted, so it would
be passed to OCR.

Features already in the output that set it apart from a text line:
- **Almost no letter bodies.** Its ink classes are 31 of 36 components "punctuation", 1 body on the baseline,
  3 with descenders, no capitals or ascenders, no accents.
- **Little support for its geometry.** Its geometry is borrowed (support 3), and only 1–4 points fit each guide line.

Features not yet measured that would also separate it:
- the same shape repeated at a regular spacing along the band;
- ink density far above text (solid black fleurons);
- no word gaps.

Requirement: a candidate line whose ink is not letters (mostly one repeated non-letter shape, or almost no letter
bodies) is discounted as non-text and never passed to OCR. The ink-class counts the detector already computes are the
first test; repetition and density are the second.

## Principle: discounted lines are not rendered

**Owner:** "as a matter of principle you should stop rendering the discounted lines."

From now on, discounted candidates are not drawn on the review pages or in the overview images:
- no band;
- no guide lines;
- no straightened image.

They stay in `lines.json` with their reason, so they can still be counted and audited. The review pages show only what
would be passed to OCR.

## Tables: the owner's review of the table pages

Review page: https://claude.ai/artifact/WNgiJyBPKUiULoEZBoQiwV. It shows 8 table pages run with the round-3 code, and
only the lines passed to OCR: 3 development pages and 5 from the 50-page set. What Docling needs for tables is
established in `docs/research/DOCLING_TABLES_20261009.md`:
- **Layout:** Docling finds the table region from the image alone. Our text pieces count as table text only if more
  than 80% of each lies inside it.
- **Table structure:** TableFormer never splits a text piece. Every piece must lie inside one table cell, and all the
  text must be found.

### 33. an-7a2b17a3fb0f-p000200: no good cell recognition

**Owner:** "there is no good cell recognition an-7a2b17a3fb0f-p000200, many cells are missed, some are fused, some
are detected but individual chars are missed."

The page is a two-page spread of navigation tables.

Measured on the round-3 output:
- **The left-hand table is almost entirely missed.** Of 414 active lines, 14 lie in the left half of the spread, 397
  in the right half, and 3 cross the fold. Docling's layout model finds both tables at full size, so the left one would
  reach the table model nearly empty.
- **Fused cells:** owner's observation. Their exact count needs the cell annotations of the acceptance test.
- **Characters missed inside detected cells:** owner's observation. In Sol's word-approximation experiment, the
  detected lines of this page were split into 833 pieces, against 408 lines.

What Docling needs here (research, section B): one piece per table cell, or several pieces within a cell, never across
two cells. Every cell's text must be found, since Docling does not recover missed text from the image.

### 34. an-a3c2bdf81256-p000112 and s2-80513ae109b4f749ca58-p00003: a column boundary from the lower half enforced in the upper half

**Owner:** "for some like an-a3c2bdf81256-p000112 and s2-80513ae109b4f749ca58-p00003 it seems a boundary is detected
in the second half of the page but it is also enforced where it shouldnt at the top half."

Measured on the round-3 output:
- **s2-80513ae109b4f749ca58-p00003.** The lower half is a two-column vote list with a gutter at x ≈ 1040–1057. The
  upper half is ordinary text running the full width (x ≈ 325–1780). Every full-width line of the upper half is cut at
  that same place, into a piece ending at x ≈ 1040 and a piece starting at x ≈ 1057 (e.g. baselines y 212, 281, 350,
  417, 486). The lower half's column boundary was carried up through the prose.
- **an-a3c2bdf81256-p000112.** The page opens with a three-line paragraph («§. 55. Περὶ τοῦ σχηματισμοῦ τῶν
  ἐπιθέτων …») running the full width. Below it the grammar paradigms stand in two columns, separated by a double rule
  that begins only under the paragraph. The paragraph's lines (baselines y ≈ 223–360) are each cut in two at
  x ≈ 606–646, the position of that rule. The paradigm lines below are correctly split at the rule.

Requirement:
- A column boundary holds only over the vertical extent where its gap or rule actually exists. It starts and ends
  where the column structure starts and ends.
- A full-width line that runs through that x position elsewhere on the page stays one line.
- Columns are found per block of the page, not per page. This is the same column structure that cases 26, 29 and 30
  require; here the error is the opposite one: a boundary where there is none.

### 35. s2-6419488b7f8e69fd20da-p00001: no check of the writing's orientation

**Owner:** "also we have no capacity to check for orientation of writting, which we generally should be doing
s2-6419488b7f8e69fd20da-p00001."

The page is a ruled table printed sideways: its text runs vertically on the scan.

Measured on the round-3 output:
- The detector still reads it as horizontal lines. It produced 368 candidates (327 active) with a median length of
  45 px, against a median x-height of 26 px.
- 69% of the active lines are shorter than three x-heights. They are slices across the vertical text, not lines.

Requirement:
- Detect the orientation of the writing (0°, 90°, 180°, 270°), per page and per block, before line detection. Rotate
  the block so that its lines are horizontal, and map the results back to page coordinates.
- A page or block whose orientation cannot be determined is reported as such, not read as horizontal.
- Open question for research: how Docling handles rotated pages and rotated tables. Does its layout model or table
  model expect the page already rotated? Which coordinate frame must our pieces then be in?
