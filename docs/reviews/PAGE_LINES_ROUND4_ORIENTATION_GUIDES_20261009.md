# Round 4, part 3c: orientation from fitted font and accent guides

The font and accent lines provide useful way-up evidence, but this implementation is not reliable enough to be the default. On 216 full-resolution development rotations it accepted 126, made 0 wrong whole-page decisions, and left 90 unknown. Some local regions still get the wrong way up. Sparse labels and numeric print remain difficult. These are development tests, not held-out accuracy.

Both readings are fitted: 0° and 180° for text running across the page, 90° and 270° for text running down it. The comparison asks whether the accents, letter bottoms, capitals and descenders follow the font’s fitted lines. It chooses only when one reading has sufficient measured support. A word inherits its region’s answer. Unknown keeps both possible readings. Region assignment is incomplete: missed portions of a pasted block can still inherit the main page’s reading incorrectly, including number rows.

The guide-only whole-page step took mean 0.405 s, median 0.392 s and p95 0.638 s. Blind region discovery plus all region fits took mean 1.100 s, median 0.807 s and p95 3.328 s. The region total already includes the main guide fit; do not add the two numbers. Disk IO, image generation and OCR delivery are excluded.

The main fit meets the target on average. All-region work sometimes exceeds the 1–2 s allowance; its measured maximum was 5.842 s. In actual oriented delivery on the 54 original source rasters, the separately timed orientation work, including table confirmation, averaged 1.195 s (p95 3.332 s; maximum 5.562 s).

**Oriented mode remains opt-in.** The default `recognition_mode="textlayer"` is unchanged. No model was trained; no held-out page was accessed.

## Rules recorded before evaluation

This section was written before running the new implementation on development
pages, generated rotations, or research fixtures. The starting commit is
`420b320`. The aborted part-3b implementation is not used.

1. Keep the existing component-neighbour axis detector. An axis supplies exactly
   two readings: 0/180 or 90/270 degrees observed clockwise. Run identical fits
   in both readings. No sign, first-candidate, upright-page, or book-convention
   default may accept a reading. Words only inherit a region decision.
2. Sample at most twelve line windows in a large region, selected by body ink
   support, with at most 32 estimated body heights along a line and three body
   heights on either side of its centre. These are computation budgets and the
   full ascender/accent/descender envelope, not learned polarity thresholds.
   Use the same source windows, reversed, in the opposite reading. Every
   component in each window enters the detector's `line_glyphs` band fit and
   `page_font.fit_guides` class-conditioned six-guide model. Report sampling.
3. Reuse the existing font model's class boundaries, missing-class borrowing,
   and robust residual scale (0.15 x-height). Borrowed guides never count as
   observed evidence. Require twelve baseline contacts for an independent
   region decision (several words, rather than one lucky edge).
4. Require at least three observed accent marks and a three-to-one excess of
   above-band over below-baseline marks. Three independent marks prevent one
   fleck or punctuation mark from deciding; the supermajority allows damaged
   accents and iota subscripts. Require at least three tall/descending bodies
   as evidence of mixed letter heights. Baseline contacts must fit within
   0.15 x-height on average. The winning reading's net above-minus-below count
   must exceed the opposite reading by at least three marks. Its baseline
   residual must not be worse by more than 0.15 x-height.
5. Record measured capital height, descender depth, accent top/bottom, baseline
   contact residuals, class counts, and rejected or borrowed guides. When a
   main region is decided, compare minority ratios with its measured ratios;
   allow the greater of that font's observed spread and 0.15 x-height. A
   proportion disagreement is recorded and blocks a close-call confirmation;
   it cannot overturn clear accent evidence from a different type size/font.
6. A close call must already have positive guide evidence (at least one accent,
   mixed letter heights, and baseline support). Optional OSD on at least 24
   bodies or paired recognizer readings may confirm only that same candidate.
   Neither creates evidence when guides are silent, nor overturns a clear fit.
   Existing fallback confidence margins are retained and separately labelled.
7. A declared numbers-only region never decides itself. A region without
   observed accents also remains unknown regardless of baseline neatness.
   Numeric children inherit only from a decided header in their explicitly
   shared orientation group. Pixel-only detection cannot certify character
   identity: numeric-like/mark-free regions are conservatively abstentions.
8. Group same-axis chains spatially, using the existing chain proposals and
   gaps of at most three body heights along the line and four across it.
   Minority evidence must form a chain at least three bodies and two body
   heights long, consistent with existing discovery. An isolated perpendicular
   neighbour vote inside a main line is not proof of a separate region.
   At most two distinct accepted angles survive; additional angles become
   unknown with their original hypotheses/evidence retained.
9. Preserve the established line/table delivery for the main frame. Replace
   only words whose centres lie inside a confirmed local minority region;
   unknown perpendicular regions retain explicitly hypothetical geometry.
   Normalize a uniformly rotated page before layout based on coherent regions,
   not the old two-percent minority-component veto.
10. Book turning convention is measured only after testing. Report the sample
    size, direction, and uncertainty; do not fit a threshold or override clear
    evidence from it. No empirical prior will be enabled in this run.

Any subsequent changes to these rules or constants must be listed below with
before/after values and the evidence already seen at the time.

## Changes after recording the rules

After the first 104 development rotations had been evaluated, the navigation
spread was wrongly accepted upside down in all four rotations. Its wrong
reading had 87 raw tall/descending class assignments, but its measured capital
and descender guides had mean residuals 0.447 and 0.184 x-height. The upright
reading had only one accepted accent; numeric punctuation was supplying the
wrong reading's apparent accent band. Accordingly the **support definition**
was corrected: before, require three raw tall/descending class assignments;
after, require three contacts on observed capital/descender guides whose mean
residual is at most the existing 0.15 x-height tolerance. The numerical margins
remain 3 contacts and 0.15 x-height; no number was optimized. This is a
post-observation structural correction, not preregistered success. The first
implementation's results are retained separately. It cannot certify a
numbers-only region from pixels, so the numeric contract and blind numeric
results remain separate checks.

During rendered synthetic checks, the sampled crop initially forced the page's
component-size estimate into the band fit. It now lets `line_glyphs` estimate its
own x-height, as the detector does. No acceptance margin changed. Region
crossing-fragment rejection was made concrete as more than half a chain's box
covered by perpendicular chains; this geometry rule was implemented before
examining development results. OSD defaults to disabled; it remains an explicit
close-call option.

The first evaluator measured the main region on the largest chain block, while
the production path pooled its page/header context. This inconsistency was
removed before the final run: both use the pooled main-page guide test. No
margin changed; whole-page and main-region scores now refer to that same
orientation group. Local minority regions still receive independent fits.

The first delivery audit found eight annotated elements losing some ink on the
grammar-paradigm page even after preserving pieces with a table ID. Some table
content lies outside Docling's retained table bounds and the remaining generic
pieces still took the word-splitting path. The correction preserves the full parent
piece rectangle when splitting at word gaps, rather than tightening each box
to a second Otsu ink mask. Before: tight Otsu envelopes; after: a non-overlapping
partition of the accepted parent rectangle. No polarity margin or word-gap
constant changed. This is a delivery correction prompted by measured loss;
its final coverage is re-audited, not assumed.

The subsequent delivery audit reduced the grammar-page losses from eight to
four elements and exposed another concrete ownership bug: local perpendicular
proposals replaced pieces belonging to a pixel-detected table outside Docling's
supplied bounds. Before, only Docling table rectangles blocked those local
replacements; after, the union of each pixel-detected table's existing piece
rectangles receives the same protection, mapped through the main fit's frame.
This adds no polarity threshold or page-specific condition. The interrupted
intermediate audit is retained under `rectangle_delivery/`; the full final
delivery audit is rerun after this correction.

The subsequent production timing pass found repeated fits of the same whole
table for several local proposals: orientation alone reached 10.748 s on one
page. The final implementation memoizes a table decision by table ID and exact
rectangle within one page call. Before: one identical table fit per intersecting
proposal; after: one fit per distinct table rectangle. No threshold, region
proposal, candidate reading or acceptance rule changes. The completed 216-turn
and 51-composite delivery audit predates this cache-only change. The repeated
54-source timing pass also checks that every delivered box, crop frame,
orientation and ownership record equals that audit; a unit test checks that
two proposals share one table fit. Both the uncached timing and source file are
preserved beside the final timing records.

### Sampler details omitted from the initial prose

These controls were implemented before the development evaluation and were not
changed, but the first prose list did not enumerate them: sampler bodies are
0.6–2.8 estimated body heights tall, less than three body heights wide, and at
least 0.09 square body heights in area (retain lowercase through accented
capitals while excluding tiny flecks and long rules). Other sampler controls are:
body-profile Gaussian sigma 0.3 estimated body heights (suppress within-letter
strokes); peak spacing
1.5 body heights (avoid selecting two sub-bands of one row); candidate body
centres within one body height of the peak; baseline seed focus from 0.25 body
heights above to 1.25 below the row centre (body-bottom location with ascender
and descender variation). The fitted ownership envelope is the font model's
2.8 x-heights above / 1.3 below baseline; neighbour/rule/large classes are
excluded. The 3-pixel minimum scale is the crop fitter's raster-resolution
floor, not a learned typographic threshold. The at-most-1800-pixel analysis
image and at-most-2000-pixel chain-discovery image retain part 3's computation
budgets. Local delivery retains its five-body-height padding. Existing axis
votes and photometric constants are unchanged.

The cross-region proportion tolerance uses the maximum of 0.15 x-height and
both the reference and candidate font's observed spreads, so ordinary font
variation is not treated as an inversion. Word splitting retains its existing
0.35-x-height empty-gap threshold before and after the rectangle-preservation
correction; only the resulting boxes changed.

The shared model's missing-class defaults remain: meanline -1, capital/ascender
-1.5, descender +0.5, accent bottom -1.25 and accent top -1.85 x-heights from the
baseline. None of those borrowed coordinates votes for orientation. Optional
fallbacks retain part 3's OSD confidence >=6 and paired recognizer score margin
0.12 / confidence gap 0.03; these are external confirmation margins, not font
measurements, and were not used in the final benchmark.

## Final measured results

Angles are observed clockwise. A Pillow positive turn normalizes them. Each 90°/270° row below is reported independently. Accuracy is correct / accepted; coverage is accepted / all. Whole-page and main-region decisions share the pooled main orientation group, including headers.

### Development whole pages and main regions

| Applied turn | Whole accepted / total | Whole correct / accepted | Errors | Coverage | Axis correct / total | Main-region accepted / total | Main errors |
|---|---|---|---|---|---|---|---|
| 0° | 32/54 | 32/32 | 0 | 59.3% | 51/54 | 32/54 | 0 |
| 90° | 32/54 | 32/32 | 0 | 59.3% | 52/54 | 32/54 | 0 |
| 180° | 31/54 | 31/31 | 0 | 57.4% | 51/54 | 31/54 | 0 |
| 270° | 31/54 | 31/31 | 0 | 57.4% | 52/54 | 31/54 | 0 |


| Applied turn | Scored blind regions | Accepted | Correct | Errors | Coverage |
|---|---|---|---|---|---|
| 0° | 1093 | 66 | 63 | 3 | 6.0% |
| 90° | 1107 | 66 | 64 | 2 | 6.0% |
| 180° | 1091 | 63 | 61 | 2 | 5.8% |
| 270° | 1104 | 63 | 62 | 1 | 5.7% |

### Research whole pages and main regions

| Applied turn | Whole accepted / total | Whole correct / accepted | Errors | Coverage | Axis correct / total | Main-region accepted / total | Main errors |
|---|---|---|---|---|---|---|---|
| 0° | 4/10 | 4/4 | 0 | 40.0% | 10/10 | 4/10 | 0 |
| 90° | 4/10 | 4/4 | 0 | 40.0% | 10/10 | 4/10 | 0 |
| 180° | 3/10 | 3/3 | 0 | 30.0% | 10/10 | 3/10 | 0 |
| 270° | 3/10 | 3/3 | 0 | 30.0% | 10/10 | 3/10 | 0 |


| Applied turn | Scored blind regions | Accepted | Correct | Errors | Coverage |
|---|---|---|---|---|---|
| 0° | 234 | 19 | 18 | 1 | 8.1% |
| 90° | 235 | 19 | 18 | 1 | 8.1% |
| 180° | 234 | 18 | 17 | 1 | 7.7% |
| 270° | 235 | 18 | 17 | 1 | 7.7% |

Why 90 whole-page tests abstain: the following checks are evaluated on the known correct reading, after testing. Counts overlap; they are diagnostics, not fitted categories or new thresholds.

| Failed requirement on the correct reading | Unknown cases |
|---|---|
| Accent count or above/below supermajority fails | 79 |
| Correct axis unresolved or not selected | 10 |
| Net accent advantage below three marks | 13 |
| Too few measured capital/descender contacts | 7 |

Region counts include the main group and disconnected local proposals; they are not manual region recall. On the real mixed page, local polarity is scored only inside its four labelled ROIs. Other local regions have unknown truth and are excluded.

### Words and pieces

Actual oriented_page delivery on all 216 rotated rasters, with exact normalized-pixel fit caching. Word/piece polarity truth by source orientation; case 35 only labelled ROIs. Not word-detection recall.
Table items remain boundary-safe pieces and may contain several words. Thus this is an inheritance audit over detector output, not a count of manually annotated linguistic words.

| Applied turn | Scored words/pieces | Accepted | Correct | Errors | Coverage | Mean delivery s |
|---|---|---|---|---|---|---|
| 0° | 33051 | 16060 | 16002 | 58 | 48.6% | 2.438 |
| 90° | 33464 | 16136 | 16086 | 50 | 48.2% | 2.263 |
| 180° | 33862 | 16082 | 16060 | 22 | 47.5% | 6.823 |
| 270° | 34300 | 16380 | 16366 | 14 | 47.8% | 2.113 |

Delivery timing runs oriented_page with the independently measured main decision and exact pixel-fit caching; includes region analysis, local fitting, splitting and crops. It excludes OCR and disk IO. Words have no independent polarity fit.

| Research standalone word turn | Accepted / total | Errors | Axis correct / total |
|---|---|---|---|
| 0° | 0/12 | 0 | 12/12 |
| 90° | 0/12 | 0 | 12/12 |
| 180° | 0/12 | 0 | 12/12 |
| 270° | 0/12 | 0 | 12/12 |


| Research crop unit | Turn | Total | Accepted | Correct | Errors | Coverage | Mean orientation s |
|---|---|---|---|---|---|---|---|
| line | 0° | 3 | 1 | 1 | 0 | 33.3% | 0.044 |
| line | 90° | 3 | 1 | 1 | 0 | 33.3% | 0.044 |
| line | 180° | 3 | 1 | 1 | 0 | 33.3% | 0.043 |
| line | 270° | 3 | 1 | 1 | 0 | 33.3% | 0.043 |
| block | 0° | 3 | 0 | 0 | 0 | 0.0% | 0.345 |
| block | 90° | 3 | 0 | 0 | 0 | 0.0% | 0.341 |
| block | 180° | 3 | 0 | 0 | 0 | 0.0% | 0.343 |
| block | 270° | 3 | 0 | 0 | 0 | 0.0% | 0.342 |

Research skew controls: 2/12 accepted correctly; 0 errors; 10 unknown. All have expected quarter-turn 0; this is not residual deskew accuracy.

| Turn | Mean main-fit s | p95 main-fit s | Mean all-region s | p95 all-region s |
|---|---|---|---|---|
| 0° | 0.397 | 0.619 | 1.089 | 3.159 |
| 90° | 0.421 | 0.643 | 1.121 | 3.072 |
| 180° | 0.390 | 0.600 | 1.079 | 3.137 |
| 270° | 0.410 | 0.625 | 1.110 | 3.068 |

54 original source rasters, actual oriented_page orientation including table confirmation; no OCR, no fit cache beyond same-frame verified part-2 main segmentation. The production timer includes direction discovery, both-reading region fits and any whole-table confirmation. It excludes the horizontal detector, word splitting and crop creation. This extra timing pass is on original source rasters only; the four-turn table above uses the guide-only benchmark. It times oriented_page alone: a complete Docling pipeline may additionally invoke the pre-layout adapter, and was not timed end to end.

| Production timer on 54 sources | Mean s | Median s | p95 s | Maximum s |
|---|---|---|---|---|
| Orientation only | 1.195 | 0.808 | 3.332 | 5.562 |
| Total delivery with verified main-fit reuse | 2.532 | 1.580 | 5.991 | 20.505 |

Before table-fit memoization, orientation averaged 1.457 s, with p95 3.925 s and maximum 10.748 s. All 54 source-page delivery records are identical after memoization (boxes, frames, labels and ownership); timings and guide-fit duration metadata naturally differ.
Standalone words deliberately abstain: no parent region is provided in those oracle word fixtures. This implements the owner’s inheritance rule; it does not satisfy the old part-3 standalone-word coverage gate.

### Two-orientation composites

| Scope | Minority turn | Axis found / cases | Guide-region errors | Minority words/pieces accepted / total | Correct | Errors | Coverage |
|---|---|---|---|---|---|---|---|
| development | 90 | 9/13 | 0 | 819/3218 | 109 | 710 | 25.5% |
| development | 270 | 8/13 | 0 | 872/2933 | 106 | 766 | 29.7% |
| development | 180 | 9/13 | 0 | 683/1478 | 289 | 394 | 46.2% |
| research | 90 | 4/6 | 0 | 69/497 | 69 | 0 | 13.9% |
| research | 270 | 4/6 | 0 | 68/721 | 68 | 0 | 9.4% |

Development composites:

| Fixture | Minority truth | Axis found | Chain-union IoU | Accepted region decisions | Errors | Oracle crop reading |
|---|---|---|---|---|---|---|
| paste_00_prose_cw90 | 90° | yes | 0.079 | ?,?,?,?,?,?,? | 0 | None |
| paste_00_prose_cw270 | 270° | yes | 0.079 | ?,?,?,?,?,?,? | 0 | None |
| paste_00_prose_cw180 | 180° | yes | 0.128 | 180,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_01_prose_cw90 | 90° | yes | 0.166 | ?,?,?,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_01_prose_cw270 | 270° | yes | 0.166 | ?,?,?,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_01_prose_cw180 | 180° | yes | 0.303 | ?,?,180,?,?,?,?,? | 0 | None |
| paste_02_label_cw90 | 90° | no | 0.000 | none | 0 | None |
| paste_02_label_cw270 | 270° | no | 0.000 | none | 0 | None |
| paste_02_label_cw180 | 180° | no | 0.000 | none | 0 | None |
| paste_03_label_cw90 | 90° | yes | 0.014 | ?,? | 0 | None |
| paste_03_label_cw270 | 270° | yes | 0.014 | ?,? | 0 | None |
| paste_03_label_cw180 | 180° | yes | 0.023 | ?,? | 0 | None |
| paste_04_table_cw90 | 90° | no | 0.000 | none | 0 | 270 |
| paste_04_table_cw270 | 270° | no | 0.000 | ?,?,? | 0 | 90 |
| paste_04_table_cw180 | 180° | no | 0.000 | ? | 0 | 0 |
| paste_05_table_cw90 | 90° | yes | 0.086 | ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,? | 0 | 90 |
| paste_05_table_cw270 | 270° | yes | 0.089 | ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,? | 0 | 270 |
| paste_05_table_cw180 | 180° | yes | 0.092 | ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,? | 0 | 180 |
| paste_06_table_cw90 | 90° | yes | 0.320 | ?,?,?,?,? | 0 | None |
| paste_06_table_cw270 | 270° | yes | 0.321 | ?,?,?,?,? | 0 | None |
| paste_06_table_cw180 | 180° | yes | 0.352 | ?,?,? | 0 | None |
| paste_07_table_cw90 | 90° | yes | 0.248 | ?,?,?,?,?,?,?,?,? | 0 | None |
| paste_07_table_cw270 | 270° | yes | 0.251 | ?,?,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_07_table_cw180 | 180° | yes | 0.277 | ?,180,?,?,?,?,?,? | 0 | None |
| paste_08_table_cw90 | 90° | yes | 0.395 | 90,90 | 0 | 90 |
| paste_08_table_cw270 | 270° | yes | 0.406 | 270,270,?,? | 0 | 270 |
| paste_08_table_cw180 | 180° | yes | 0.417 | 180,180 | 0 | 180 |
| paste_09_table_cw90 | 90° | yes | 0.278 | ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_09_table_cw270 | 270° | yes | 0.281 | ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_09_table_cw180 | 180° | yes | 0.263 | ?,?,?,?,180,?,?,180,?,?,?,?,?,?,?,?,?,?,?,? | 0 | None |
| paste_10_table_cw90 | 90° | yes | 0.006 | ? | 0 | None |
| paste_10_table_cw270 | 270° | no | 0.000 | ? | 0 | 270 |
| paste_10_table_cw180 | 180° | yes | 0.004 | ?,?,? | 0 | 180 |
| paste_11_numbers_cw90 | 90° | no | 0.000 | none | 0 | None |
| paste_11_numbers_cw270 | 270° | no | 0.000 | none | 0 | None |
| paste_11_numbers_cw180 | 180° | no | 0.000 | none | 0 | None |
| paste_12_numbers-header_cw90 | 90° | no | 0.000 | none | 0 | 90 |
| paste_12_numbers-header_cw270 | 270° | no | 0.000 | none | 0 | 270 |
| paste_12_numbers-header_cw180 | 180° | no | 0.000 | none | 0 | 180 |

Research composites:

| Fixture | Minority truth | Axis found | Chain-union IoU | Accepted region decisions | Errors | Oracle crop reading |
|---|---|---|---|---|---|---|
| research__composite_0_block_r90 | 90° | yes | 0.662 | 90 | 0 | 90 |
| research__composite_0_block_r270 | 270° | yes | 0.661 | 270,? | 0 | 270 |
| research__composite_0_line_r90 | 90° | yes | 0.703 | ? | 0 | None |
| research__composite_0_line_r270 | 270° | yes | 0.703 | ? | 0 | None |
| research__composite_0_word_r90 | 90° | yes | 0.803 | ? | 0 | None |
| research__composite_0_word_r270 | 270° | yes | 0.803 | ? | 0 | None |
| research__composite_1_block_r90 | 90° | yes | 0.605 | ? | 0 | None |
| research__composite_1_block_r270 | 270° | yes | 0.604 | ? | 0 | None |
| research__composite_1_line_r90 | 90° | no | 0.000 | none | 0 | None |
| research__composite_1_line_r270 | 270° | no | 0.000 | none | 0 | None |
| research__composite_1_word_r90 | 90° | no | 0.000 | none | 0 | None |
| research__composite_1_word_r270 | 270° | no | 0.000 | none | 0 | None |

Development composite word/piece delivery:

| Fixture | Minority turn | Main accepted / total | Main errors | Minority accepted / total | Minority correct | Minority errors | Delivery s |
|---|---|---|---|---|---|---|---|
| paste_00_prose_cw90 | 90 | 515/765 | 0 | 86/108 | 0 | 86 | 9.028 |
| paste_00_prose_cw270 | 270 | 515/765 | 0 | 87/110 | 0 | 87 | 8.726 |
| paste_00_prose_cw180 | 180 | 516/782 | 0 | 65/83 | 6 | 59 | 8.802 |
| paste_01_prose_cw90 | 90 | 502/694 | 0 | 1/46 | 0 | 1 | 9.086 |
| paste_01_prose_cw270 | 270 | 502/694 | 0 | 3/67 | 0 | 3 | 8.924 |
| paste_01_prose_cw180 | 180 | 285/757 | 0 | 7/14 | 7 | 0 | 9.191 |
| paste_02_label_cw90 | 90 | 529/754 | 0 | 8/8 | 0 | 8 | 7.295 |
| paste_02_label_cw270 | 270 | 534/784 | 0 | 12/12 | 0 | 12 | 7.557 |
| paste_02_label_cw180 | 180 | 297/754 | 0 | 0/30 | 0 | 0 | 7.445 |
| paste_03_label_cw90 | 90 | 517/764 | 0 | 3/3 | 0 | 3 | 7.399 |
| paste_03_label_cw270 | 270 | 518/765 | 0 | 2/2 | 0 | 2 | 7.366 |
| paste_03_label_cw180 | 180 | 301/775 | 0 | 0/4 | 0 | 0 | 7.661 |
| paste_04_table_cw90 | 90 | 0/2196 | 0 | 0/552 | 0 | 0 | 35.199 |
| paste_04_table_cw270 | 270 | 0/1726 | 0 | 0/561 | 0 | 0 | 37.477 |
| paste_04_table_cw180 | 180 | 309/786 | 0 | 332/335 | 0 | 332 | 13.090 |
| paste_05_table_cw90 | 90 | 295/822 | 0 | 0/175 | 0 | 0 | 9.861 |
| paste_05_table_cw270 | 270 | 546/822 | 0 | 114/163 | 0 | 114 | 10.183 |
| paste_05_table_cw180 | 180 | 297/793 | 0 | 0/155 | 0 | 0 | 9.567 |
| paste_06_table_cw90 | 90 | 296/766 | 0 | 0/289 | 0 | 0 | 11.524 |
| paste_06_table_cw270 | 270 | 528/766 | 0 | 1/282 | 0 | 1 | 11.642 |
| paste_06_table_cw180 | 180 | 528/752 | 0 | 3/307 | 0 | 3 | 10.434 |
| paste_07_table_cw90 | 90 | 300/780 | 0 | 0/284 | 0 | 0 | 10.813 |
| paste_07_table_cw270 | 270 | 296/752 | 0 | 0/248 | 0 | 0 | 10.812 |
| paste_07_table_cw180 | 180 | 507/725 | 0 | 126/160 | 126 | 0 | 9.415 |
| paste_08_table_cw90 | 90 | 512/770 | 0 | 123/123 | 109 | 14 | 13.605 |
| paste_08_table_cw270 | 270 | 301/772 | 0 | 106/123 | 106 | 0 | 13.276 |
| paste_08_table_cw180 | 180 | 301/781 | 0 | 109/120 | 109 | 0 | 11.676 |
| paste_09_table_cw90 | 90 | 293/737 | 0 | 0/1030 | 0 | 0 | 16.461 |
| paste_09_table_cw270 | 270 | 302/776 | 0 | 0/814 | 0 | 0 | 14.837 |
| paste_09_table_cw180 | 180 | 239/717 | 0 | 41/57 | 41 | 0 | 9.999 |
| paste_10_table_cw90 | 90 | 319/781 | 0 | 540/542 | 0 | 540 | 12.311 |
| paste_10_table_cw270 | 270 | 319/785 | 0 | 478/482 | 0 | 478 | 13.095 |
| paste_10_table_cw180 | 180 | 316/831 | 0 | 0/191 | 0 | 0 | 9.422 |
| paste_11_numbers_cw90 | 90 | 532/799 | 0 | 25/25 | 0 | 25 | 7.601 |
| paste_11_numbers_cw270 | 270 | 565/832 | 0 | 31/31 | 0 | 31 | 7.992 |
| paste_11_numbers_cw180 | 180 | 126/825 | 0 | 0/9 | 0 | 0 | 7.969 |
| paste_12_numbers-header_cw90 | 90 | 545/810 | 0 | 33/33 | 0 | 33 | 7.706 |
| paste_12_numbers-header_cw270 | 270 | 566/827 | 0 | 38/38 | 0 | 38 | 7.939 |
| paste_12_numbers-header_cw180 | 180 | 126/797 | 0 | 0/13 | 0 | 0 | 8.193 |

Research composite word/piece delivery:

| Fixture | Minority turn | Main accepted / total | Main errors | Minority accepted / total | Minority correct | Minority errors | Delivery s |
|---|---|---|---|---|---|---|---|
| research__composite_0_block_r90 | 90 | 0/218 | 0 | 69/69 | 69 | 0 | 6.489 |
| research__composite_0_block_r270 | 270 | 0/219 | 0 | 68/69 | 68 | 0 | 6.536 |
| research__composite_0_line_r90 | 90 | 0/212 | 0 | 0/12 | 0 | 0 | 3.907 |
| research__composite_0_line_r270 | 270 | 0/212 | 0 | 0/12 | 0 | 0 | 3.988 |
| research__composite_0_word_r90 | 90 | 0/213 | 0 | 0/1 | 0 | 0 | 3.728 |
| research__composite_0_word_r270 | 270 | 0/213 | 0 | 0/1 | 0 | 0 | 3.747 |
| research__composite_1_block_r90 | 90 | 0/27 | 0 | 0/413 | 0 | 0 | 13.508 |
| research__composite_1_block_r270 | 270 | 0/27 | 0 | 0/638 | 0 | 0 | 13.632 |
| research__composite_1_line_r90 | 90 | 0/27 | 0 | 0/0 | 0 | 0 | 10.093 |
| research__composite_1_line_r270 | 270 | 0/27 | 0 | 0/0 | 0 | 0 | 10.177 |
| research__composite_1_word_r90 | 90 | 0/25 | 0 | 0/2 | 0 | 0 | 9.306 |
| research__composite_1_word_r270 | 270 | 0/27 | 0 | 0/1 | 0 | 0 | 9.358 |


| Composite with wrong minority words | Wrong words/pieces | Actual inherited parent and reading |
|---|---|---|
| paste_00_prose_cw90 | 86 | page CW0: 86 |
| paste_00_prose_cw270 | 87 | page CW0: 87 |
| paste_00_prose_cw180 | 59 | page CW0: 59 |
| paste_01_prose_cw90 | 1 | page CW0: 1 |
| paste_01_prose_cw270 | 3 | page CW0: 3 |
| paste_02_label_cw90 | 8 | page CW0: 8 |
| paste_02_label_cw270 | 12 | page CW0: 12 |
| paste_03_label_cw90 | 3 | page CW0: 3 |
| paste_03_label_cw270 | 2 | page CW0: 2 |
| paste_04_table_cw180 | 332 | page CW0: 332 |
| paste_05_table_cw270 | 114 | page CW0: 114 |
| paste_06_table_cw270 | 1 | page CW0: 1 |
| paste_06_table_cw180 | 3 | page CW0: 3 |
| paste_08_table_cw90 | 14 | page CW0: 14 |
| paste_10_table_cw90 | 540 | page CW0: 540 |
| paste_10_table_cw270 | 478 | page CW0: 478 |
| paste_11_numbers_cw90 | 25 | page CW0: 25 |
| paste_11_numbers_cw270 | 31 | page CW0: 31 |
| paste_12_numbers-header_cw90 | 33 | page CW0: 33 |
| paste_12_numbers-header_cw270 | 38 | page CW0: 38 |

A proposal intersects the pasted ROI to count as axis found; the stricter 0.5 union-IoU diagnostic is also shown. Discovery is blind. Oracle-crop scores use the labelled ROI only after discovery, and never certify blind success. All 39 new pastes include a different-page donor (or explicitly rendered digits); each is tested at 90°, 270°, and 180°. Research fixtures are hash-verified and unchanged.

### Numbers-only contract

| Numeric fixture: actual delivered words | Accepted / total | Wrong reading |
|---|---|---|
| paste_11_numbers_cw90 | 25/25 | 25 |
| paste_11_numbers_cw270 | 31/31 | 31 |
| paste_11_numbers_cw180 | 0/9 | 0 |


| Numeric fixture | Blind accepted regions | Blind errors | Unlabelled oracle reading |
|---|---|---|---|
| paste_11_numbers_cw90 | 0 | 0 | None |
| paste_11_numbers_cw270 | 0 | 0 | None |
| paste_11_numbers_cw180 | 0 | 0 | None |

The explicit `content_kind="numbers"` contract always abstains independently and `resolve_regions` inherits only from a nonnumeric, decided header in the same named orientation group. Conflicting headers abstain. The blind `page_regions` path currently does not classify numeric content or create semantic header/figure group links; it can only pool the ink of a geometrically joined block. Automatic numeric-to-header grouping is therefore incomplete. Pixel-only classification cannot guarantee that a small mark is an accent rather than a decimal point. The blind results above remain a separate release gate; the explicit semantic contract is not evidence of blind numeric detection.

### Case 35: s2-6419488b7f8e69fd20da-p00001

| Part | Truth | Measured axis | Guide-only oracle reading | Accepted accents in the two readings | Outcome |
|---|---|---|---|---|---|
| title | 270 | vertical | None | [3, 4] | unknown |
| Kapnou | 180 | horizontal | None | [1, 1] | unknown |
| folio | 0 | horizontal | None | [0, 0] | unknown |
| numbers | 270 | horizontal | None | [11, 7] | unknown |


| Blind delivered ROI | Pieces/words found | Accepted | Correct | Errors |
|---|---|---|---|---|
| title | 11 | 7 | 7 | 0 |
| Kapnou | 4 | 0 | 0 | 0 |
| folio | 0 | 0 | 0 | 0 |
| numbers | 43 | 0 | 0 | 0 |

ROI membership uses delivered box centres. These counts do not establish complete text/word recall.
The title oracle is a supplied single-line crop, so its long ink axis gives the 90°/270° pair. It has 3 above / 7 below marks at 90° and 4 above / 3 below at 270°: insufficient for the recorded three-to-one margin. «Καπνοῦ» has only 4/5 baseline contacts, below the twelve-contact minimum. The folio has no observed accents. The number-grid crop also fails to infer the correct axis independently; it needs its surrounding text group. The title and number rows are CW270, «Καπνοῦ» is CW180, and the ambiguous folio is upright in the source. That already exceeds the supported two accepted angles; an independently detected third reading must remain unknown. The folio’s appearance is not permission for digits to decide. Oracle crops are not proof that the blind path found each part.

[New case-35 regions](../../.astra/out/orientation_eval/s2-6419488b7f8e69fd20da-p00001__cw0.regions.jpg) · [New case-35 delivered pieces](../../.astra/out/orientation_eval/s2-6419488b7f8e69fd20da-p00001.words.jpg)

### Line preservation and table delivery

53/54 upright-source main-frame line records are exactly equal to the part-2 records. Existing base fits are reused only in the same image frame, with source SHA-256 verified; changed frames and minority fits execute the production code. The six horizontal detector modules are independently verified byte-identical to `f611ee2`. This is a reuse/compatibility check, not 54 fresh independent fits. Local replacements are audited separately through delivered pieces.

| Source page | Main CW | Main-frame lines part 2 / now | Exact lines | Accepted pieces / words |
|---|---|---|---|---|
| an-1436ae03653f-p000163 | 0 | 38/38 | yes | 384/388 |
| an-1be60011c435-p000215 | 0 | 56/56 | yes | 322/714 |
| an-1c6e1c0e929e-p000167 | None | 29/29 | yes | 0/260 |
| an-1f8e7d022643-p000003 | 0 | 21/21 | yes | 99/104 |
| an-2cfe28da5103-p000135 | 0 | 91/91 | yes | 580/602 |
| an-3352d912f2e9-p000104 | None | 38/38 | yes | 0/198 |
| an-466cffad2cba-p000323 | 0 | 25/25 | yes | 193/193 |
| an-5c093c79d6bb-p000199 | 0 | 79/79 | yes | 477/809 |
| an-778126cc8c2b-p000010 | 0 | 41/41 | yes | 270/309 |
| an-7a2b17a3fb0f-p000200 | None | 1623/1623 | yes | 0/1303 |
| an-9ea1564fcf4f-p000013 | None | 89/89 | yes | 0/988 |
| an-a3c2bdf81256-p000112 | 0 | 390/390 | yes | 364/385 |
| an-a73d22211479-p000301 | None | 91/91 | yes | 0/681 |
| an-b1a643813945-p000054 | 0 | 32/32 | yes | 202/206 |
| an-c153f2c605b3-p000040 | None | 34/34 | yes | 0/199 |
| an-c2c2053cfc10-p000056 | 0 | 75/75 | yes | 705/794 |
| an-c8b96a901917-p000068 | 0 | 139/139 | yes | 843/880 |
| an-d3237d690aa0-p000138 | None | 1402/1402 | yes | 16/1086 |
| an-d6002cf45e4d-p000058 | None | 10/10 | yes | 0/252 |
| an-d6fd2cf2f618-p000047 | None | 37/37 | yes | 0/306 |
| an-d83e7a198ade-p000099 | 0 | 84/84 | yes | 597/896 |
| an-e46611ae2fcc-p000041 | None | 67/67 | yes | 0/325 |
| an-e74539ae215c-p000338 | 0 | 95/95 | yes | 646/660 |
| an-ef481610a820-p000181 | None | 41/41 | yes | 0/223 |
| an-fabf591ca801-p000067 | 0 | 88/88 | yes | 284/578 |
| an-fd4fa0018ae1-p000037 | 0 | 33/33 | yes | 222/229 |
| an-ffccc97c07de-p000152 | None | 45/45 | yes | 29/229 |
| s2-0683f98f964a6d41cb72-p00003 | 0 | 49/49 | yes | 367/377 |
| s2-09f5dfca4af4d74173c6-p00005 | 0 | 69/69 | yes | 343/596 |
| s2-0ce9d1025b3f23c7119e-p00001 | 0 | 65/65 | yes | 253/469 |
| s2-200e977f2dab5291c42c-p00035 | None | 715/715 | yes | 57/463 |
| s2-23a70964fda83cb7aeb1-p00003 | 0 | 134/134 | yes | 712/719 |
| s2-3229200bf47ca465a42d-p00004 | None | 38/38 | yes | 27/279 |
| s2-49598b2e848ab1f0ee1e-p00001 | None | 130/130 | yes | 198/2332 |
| s2-5ca02b142a2a3eaf078a-p00002 | 0 | 45/45 | yes | 343/350 |
| s2-60f24a3d8a2d714767f2-p00003 | 0 | 129/129 | yes | 1303/1332 |
| s2-63f072d79585d71224b6-p00002 | None | 51/51 | yes | 0/382 |
| s2-6419488b7f8e69fd20da-p00001 | 270 | 1827/739 | no | 247/531 |
| s2-658e6dcb48b540357a9d-p00001 | 0 | 83/83 | yes | 223/254 |
| s2-661ddf05c8865e7b2c45-p00009 | 0 | 200/200 | yes | 1274/1338 |
| s2-6f552c96213b4c24a071-p00003 | None | 42/42 | yes | 0/338 |
| s2-7247ee9b1bc2374b3980-p00001 | 0 | 134/134 | yes | 692/809 |
| s2-74cdb23a34ca4a6cd01e-p00002 | 0 | 144/144 | yes | 1196/1206 |
| s2-77d1bd63d5babbe0df73-p00001 | 0 | 39/39 | yes | 232/546 |
| s2-80513ae109b4f749ca58-p00003 | 0 | 467/467 | yes | 488/499 |
| s2-831443dc5e6f1ccfbaf5-p00020 | None | 970/970 | yes | 0/730 |
| s2-86865c33eef5932c013b-p00005 | None | 42/42 | yes | 1/231 |
| s2-93f8070059f938bda524-p00001 | 0 | 129/129 | yes | 241/1640 |
| s2-9de6cda8f03f0fc60a58-p00005 | 0 | 123/123 | yes | 1009/1009 |
| s2-be269b8c315b16befc35-p00002 | 0 | 44/44 | yes | 353/356 |
| s2-d1ed1c2db37f431f4acb-p00001 | None | 124/124 | yes | 0/996 |
| s2-dee99fdf5214acdc6f25-p00005 | None | 41/41 | yes | 0/319 |
| s2-dfcc21869afc140111ce-p00001 | None | 119/119 | yes | 0/1089 |
| s2-f9ec82212abc808325d7-p00010 | 0 | 56/56 | yes | 508/537 |


| Table page | Part-1 complete / total | Now complete / total | Part-1 crossings | Now crossings | Elements losing ink | No worse? |
|---|---|---|---|---|---|---|
| [an-7a2b17a3fb0f-p000200](../../.astra/out/orientation_eval/an-7a2b17a3fb0f-p000200.words.jpg) | 430/801 | 430/801 | 114 | 114 | 0 | yes |
| [an-a3c2bdf81256-p000112](../../.astra/out/orientation_eval/an-a3c2bdf81256-p000112.words.jpg) | 40/88 | 40/88 | 0 | 0 | 0 | yes |
| [an-d3237d690aa0-p000138](../../.astra/out/orientation_eval/an-d3237d690aa0-p000138.words.jpg) | 359/455 | 359/455 | 68 | 68 | 0 | yes |
| [s2-200e977f2dab5291c42c-p00035](../../.astra/out/orientation_eval/s2-200e977f2dab5291c42c-p00035.words.jpg) | 124/267 | 124/267 | 20 | 20 | 0 | yes |
| [s2-6419488b7f8e69fd20da-p00001](../../.astra/out/orientation_eval/s2-6419488b7f8e69fd20da-p00001.words.jpg) | 56/306 | 137/306 | 47 | 105 | 35 | no |
| [s2-80513ae109b4f749ca58-p00003](../../.astra/out/orientation_eval/s2-80513ae109b4f749ca58-p00003.words.jpg) | 47/66 | 47/66 | 1 | 1 | 0 | yes |
| [s2-831443dc5e6f1ccfbaf5-p00020](../../.astra/out/orientation_eval/s2-831443dc5e6f1ccfbaf5-p00020.words.jpg) | 308/621 | 308/621 | 180 | 180 | 0 | yes |
| [s2-dee99fdf5214acdc6f25-p00005](../../.astra/out/orientation_eval/s2-dee99fdf5214acdc6f25-p00005.words.jpg) | 23/24 | 23/24 | 6 | 1 | 0 | yes |

Complete means at least 98% of independently annotated contrast pixels retained. Losses compare exact fractions even above 98%; crossing counts compare overlaps with multiple annotated cells. The annotations are the provisional part-1 pixel review. This measures detector delivery geometry, not OCR transcription or real TableFormer cell correctness.

The part-3 regression had re-split already safe table pieces into tight words and allowed small local proposals to replace them. The new path preserves the existing table pieces, protects both Docling-supplied and pixel-detected table extents, and normalizes a local table only when the whole table’s guide decision agrees. The actual installed TableFormer and backend contracts are covered by the test suite.

### Printing convention

Of the eight annotated table pages, seven have upright main text in the supplied raster and one has sideways main text: case 35, observed CW270 (normalize by a clockwise 90° turn). A landscape two-page scan such as the navigation spread is not itself a sideways printed table. One sideways source is insufficient to establish a book-wide convention; rotated test copies do not add independent evidence. No empirical turning prior is enabled.

### Errors and limitations

s2-6419488b7f8e69fd20da-p00001: 56 → 137 complete annotated elements, but 35 elements lose some previously covered ink and crossings change 47 → 105. The accepted CW270 main frame changes the detector’s grid and piece partition. It recovers substantially more numeric text, but the new partition still crosses cells and loses some previous fragments. That is a table-delivery regression despite a correct main way-up decision; no net-improvement exemption is claimed.

Uniform-page normalization remains incomplete. The old two-percent veto was replaced, and the synthetic cross-line-neighbour test passes, but real chain proposals still produce false mixed flags. The following replays the adapter predicate on the stored fitted decisions; it is not a new end-to-end Docling run. Case 35 is excluded because it really is mixed.

| Applied turn | Uniform sources | Accepted main | False mixed vetoes among accepted | Would rotate before layout |
|---|---|---|---|---|
| 0 | 53 | 31 | 28 | 0 |
| 90 | 53 | 31 | 28 | 3 |
| 180 | 53 | 30 | 26 | 4 |
| 270 | 53 | 31 | 27 | 4 |

No accepted whole-page or oracle-crop way-up errors were observed.


| Blind-region fixture | Region | Accepted | Expected | Explanation |
|---|---|---|---|---|
| an-1f8e7d022643-p000003__cw0 | region-1 | 180 | 0 | Mixed-size slanted Greek type and ornament: the upright reading measured 9 above / 6 below marks; the wrong reading 12 / 4. Both fit plausible classes; the count comparison chose wrongly. |
| an-1f8e7d022643-p000003__cw90 | region-1 | 270 | 90 | Mixed-size slanted Greek type and ornament: the upright reading measured 9 above / 6 below marks; the wrong reading 12 / 4. Both fit plausible classes; the count comparison chose wrongly. |
| s2-0ce9d1025b3f23c7119e-p00001__cw0 | region-19 | 180 | 0 | False text region on faint reverse-side ink. Local contrast admits show-through; the wrong reading fits 3 apparent accents / 1 below mark. Page-level faintness protection is missing in this proposal test. |
| s2-0ce9d1025b3f23c7119e-p00001__cw180 | region-18 | 0 | 180 | False text region on faint reverse-side ink. Local contrast admits show-through; the wrong reading fits 3 apparent accents / 1 below mark. Page-level faintness protection is missing in this proposal test. |
| s2-49598b2e848ab1f0ee1e-p00001__cw0 | region-2 | 270 | 0 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| s2-49598b2e848ab1f0ee1e-p00001__cw90 | region-2 | 0 | 90 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| s2-49598b2e848ab1f0ee1e-p00001__cw180 | region-2 | 90 | 180 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| s2-49598b2e848ab1f0ee1e-p00001__cw270 | region-2 | 180 | 270 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| research__s2-49598b2e848ab1f0ee1e-p00001__r0 | region-2 | 270 | 0 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| research__s2-49598b2e848ab1f0ee1e-p00001__r90 | region-2 | 0 | 90 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| research__s2-49598b2e848ab1f0ee1e-p00001__r180 | region-2 | 90 | 180 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |
| research__s2-49598b2e848ab1f0ee1e-p00001__r270 | region-2 | 180 | 270 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. |


| Source with wrong delivered readings | Applied turn | Wrong accepted words/pieces | Explanation |
|---|---|---|---|
| an-1f8e7d022643-p000003 | 0 | 36 | Mixed-size slanted Greek type and ornament: the upright reading measured 9 above / 6 below marks; the wrong reading 12 / 4. Both fit plausible classes; the count comparison chose wrongly. Its word/piece descendants inherited that region decision. |
| an-1f8e7d022643-p000003 | 90 | 36 | Mixed-size slanted Greek type and ornament: the upright reading measured 9 above / 6 below marks; the wrong reading 12 / 4. Both fit plausible classes; the count comparison chose wrongly. Its word/piece descendants inherited that region decision. |
| s2-0ce9d1025b3f23c7119e-p00001 | 0 | 8 | False text region on faint reverse-side ink. Local contrast admits show-through; the wrong reading fits 3 apparent accents / 1 below mark. Page-level faintness protection is missing in this proposal test. Its word/piece descendants inherited that region decision. |
| s2-0ce9d1025b3f23c7119e-p00001 | 180 | 8 | False text region on faint reverse-side ink. Local contrast admits show-through; the wrong reading fits 3 apparent accents / 1 below mark. Page-level faintness protection is missing in this proposal test. Its word/piece descendants inherited that region decision. |
| s2-49598b2e848ab1f0ee1e-p00001 | 0 | 14 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. Its word/piece descendants inherited that region decision. |
| s2-49598b2e848ab1f0ee1e-p00001 | 90 | 14 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. Its word/piece descendants inherited that region decision. |
| s2-49598b2e848ab1f0ee1e-p00001 | 180 | 14 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. Its word/piece descendants inherited that region decision. |
| s2-49598b2e848ab1f0ee1e-p00001 | 270 | 14 | False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit. Its word/piece descendants inherited that region decision. |

The composite word errors above occur when a missed or incompletely covered pasted minority retains its surrounding main-group reading. Their actual inherited parents are listed per fixture. Correct accepted minority-region fits therefore do not certify the entire pasted block’s word delivery. Numeric-only pastes expose the same missing semantic grouping; inherited main polarity is not a numeric guide decision, but it still fails the requirement to inherit only from a header in the correct orientation group.
The explanations use source-crop inspection and fitted contacts; class-assignment mechanisms are interpretations, not manual glyph-class annotations. Research rows repeat the same source failure under exact rotations. A new crop sheet is [here](../../.astra/out/orientation_eval/error-regions.jpg).

The direct guide-region errors are retained in the raw two-reading receipts. Their mechanism is an ambiguous or incorrect ink-class assignment (punctuation, damaged numerals, fragmented letters, or nontext) supporting a geometrically plausible fitted guide. A tight fitted curve is conditional on those class assignments; it does not certify that the marks are Greek accents. Region proposals can also fragment a label or create cross-line chains. No threshold was adjusted to eliminate individual remaining failures.

Main-page priors, minority-turn priors, recognizer confirmation and OSD are not used in this final guide-only benchmark. OSD is optional and may only confirm the guide-supported close candidate. When supplied measured guide evidence, the paired recognizer helper preserves strong guide decisions, rejects independent word votes, and cannot decide a guide-silent region. Full real-recognition/pipeline accuracy was not rerun.

### Release gates

| Gate | Pass | Evidence |
|---|---|---|
| Zero whole-page and main-region way-up errors | yes | 0 whole, 0 main errors |
| At least 95% whole-page coverage | no | 58.3% |
| Every minority found, no wrong way up | no | 26/39 axis found; 0 accepted region errors; 1870 delivered minority word/piece errors |
| Numbers never decide alone | no | explicit numeric contract tested; blind numeric receipts above |
| 54 upright-source line outputs unchanged or measured improvement | no | 53/54 exact; no blanket improvement claim |
| Eight tables no worse than part 1 | no | 7/8 no worse |


| Support definition | Development accepted / 216 | Whole errors | 90-degree accepted / errors | 270-degree accepted / errors |
|---|---|---|---|---|
| Initial raw variable-body classes | 131 | 4 | 33 / 1 | 33 / 1 |
| Final measured variable-guide support | 126 | 0 | 32 / 0 | 31 / 0 |

### Tests, artifacts, and reproduction

Test suite: 2187/2203 passed; 16 skipped, 0 failures, 0 errors. The 16 browser-render checks were skipped because the Chromium executable is unavailable; it was not downloaded. All runnable tests pass. API documentation was regenerated.

New output only: [prose guide readings](../../.astra/out/orientation_eval/guides-prose.png), [numeric-table guide readings](../../.astra/out/orientation_eval/guides-navigation.png). Solid guides have measured contacts; dashed guides are borrowed.

Machine-readable results: [summary](../../.astra/out/orientation_eval/summary.json), [delivery audit](../../.astra/out/orientation_eval/delivery-summary.json), [per-case decisions](../../.astra/out/orientation_eval/decisions/), [production timing and cache equivalence](../../.astra/out/orientation_eval/production-orientation-time.json), [test XML](../../.astra/out/orientation_eval/tests.xml). The initial implementation is preserved under `initial/`. `run-source-hashes.json` binds the final fitted run; `source-finalization.json` records subsequent API-only annotations, the scoring-only correction that counts wrong-axis minority errors, and the auxiliary title oracle being supplied as a line. The guide acceptance rules did not change. Delivery source hashes bind the completed four-turn/composite audit after the table and word-partition corrections. `before-table-cache-oriented-page.py` preserves that audited source; the final timing file binds the cache-only revision and its 54-source delivery-equivalence checks.

Run from the worktree with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` and `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`:

```sh
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
GUIDES_PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
"$GUIDES_PYTHON" scripts/glyphs/generate_orientation_guides.py
"$GUIDES_PYTHON" scripts/glyphs/evaluate_orientation_guides.py
"$GUIDES_PYTHON" scripts/glyphs/audit_orientation_guides.py
"$GUIDES_PYTHON" scripts/glyphs/time_orientation_guides.py
"$GUIDES_PYTHON" scripts/glyphs/render_orientation_guides.py
"$GUIDES_PYTHON" scripts/generate_api_docs.py
"$GUIDES_PYTHON" -m pytest -p no:cacheprovider --junitxml=.astra/out/orientation_eval/tests.xml
"$GUIDES_PYTHON" scripts/glyphs/report_orientation_guides.py
```

No push, download, background shell job, training run, or held-out-page access was performed.
