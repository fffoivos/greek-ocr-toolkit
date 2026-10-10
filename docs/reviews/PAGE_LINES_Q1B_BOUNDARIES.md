# Q1b: boundary evidence over frozen geometry

## Rules recorded before the development-page evaluation

These are dimensionless morphology and layout tests, not page-specific training.
No page name, annotation, OCR text or PDF text participates in a decision.

1. **Whitespace:** measure occupied horizontal runs in each line's own curved
   letter band. Internal empty runs supply a spacing distribution in that
   line's x-heights; exclude the candidate gap itself. Record the lower and
   upper halves separately as letter-gap and word-gap proxies (these are not
   linguistic labels). A gutter must be at least 1.5 local x-heights and exceed
   1.5 times the 90th percentile of observed ordinary spacing on **both** sides.
   Use every nearby participating text size, including a spanning heading.
   Require at least three distinct baselines per side, substantial text runs
   at least three local x-heights wide, a shared vertical span of at least six
   local x-heights, and support on both sides in at least 60% of occupied rows.
   These requirements separate a sustained pair of text blocks from a heading,
   a repeated word space, a short prefix or a margin. Missing spacing or block
   evidence is not permission to promote a gap.
2. **Printed rules:** evaluate original image ink, not the detector's rule
   mask. At each sampled row find the nearest stroke within 0.3 local x-height
   of the proposal. A supported row has stroke thickness at most 0.35
   x-height, blank flanks at 0.5 x-height, and centre residual at most 0.15
   x-height from the straight path. Require at least eight x-heights of
   extent. Continuous rules need at least 85% supported rows; dashed rules
   need at least 50%, at least three dashes, dash length at least one x-height,
   gaps at most two x-heights, and consistent dash/gap lengths (coefficient of
   variation at most 0.5). Validate the occupied extent rather than extrapolate
   through empty margins. Slopes are preserved. Wide shading, curved strokes
   and disconnected letter stems do not satisfy these tests.
3. **Crossings:** keep the complete ribbon/rectangle intersection test as the
   conservative join guard. Separately measure original ink inside the
   piece's curved band on both sides of each retained stop, excluding the rule
   stroke. Record counts, ranges and masks/crops so envelope-only intersections
   cannot be called proven detector errors. A true crossing requires text ink
   on both sides, supported inside the boundary's finite vertical extent.
   An unproven overlap is an unresolved gate failure, not a false boundary.
4. **Structure:** validate all proposed boundaries, including those with no
   crossings, before deriving columns, blocks, rows and reading order. Preserve
   folds separately with their inference provenance. Preserve every line
   curve, delivered piece and diagnostic record. Joining continues to reject
   any full-envelope crossing, including crossings inside interpolated gaps.

The 1.5 spacing margin separates ordinary spacing from structural whitespace;
three rows and six x-heights demand more than a one/two-line accident. The rule
width/flank/residual tests distinguish a stroke from merely finding dark pixels
near a proposed direction. Thresholds are fixed before evaluating the 54 pages.

## Measurement corrections (before the second evaluation)

The first implementation conflated isolated thin-stroke support with ink
continuity. A printed rule touching a letter or a horizontal rule has ink at
the junction, although its horizontal cross-section is no longer isolated.
The corrected measurement fits the same thin, straight samples, requires them
on at least half the occupied rows, and measures 85% continuity independently
inside a strip of the measured half-thickness plus 0.05 x-height. A synthetic
rule with repeated horizontal junctions reproduces the error. This is a change
to the measurement, recorded after the first evaluation; the initial results
were not treated as valid false-boundary classifications.

Similarly, separate columns can have staggered baselines. Bilateral support
matches rows within half the smaller measured median leading, rather than
requiring identical baseline phase. A synthetic half-leading offset tests
this. Original letter-band whitespace must independently pass the width test
on 60% of rows; a detector rectangle is only a proposal. No page-specific
thresholds or exceptions were added.

Before the final evaluation, crossing measurement also excludes neighbouring
verified rule strokes and long, thin connected rule remnants (at least three
x-heights long, at most half an x-height wide), and ignores components below
0.04 square x-heights. A synthetic double-border case tests that a second rule
stroke is not counted as text. Real crossings need at least 0.04 square
x-heights of text ink on each side and 0.2 x-heights of common occupied rows.
These are conservative evidence requirements: inconclusive cases remain
unresolved. Table-fragment spacing now includes facing fragments on the same
baseline, so delivery splitting cannot hide ordinary word spaces; a synthetic
fragmented-row case tests this.

The two-x-height maximum unprinted gap applies to continuous rules too:
high average ink support must not bridge a long blank interval. A synthetic
stroke with over 85% total support and a four-x-height blank middle tests that
requirement. No acceptance threshold was lowered to fit a development page.

The crossing mask uses the existing table component limits (height at most
3.5 x-heights, width at most 12) to avoid counting a broad adjacent frame as
text. The double-border test includes both thin and heavy second strokes.
This changes crossing evidence only, never delivered ink or geometry.

Original elongated components (at least three x-heights long and an aspect
ratio of eight) are excluded before rule subtraction can break them into
letter-sized remnants. Background texture retained by the permissive binariser
does not establish a crossing: after rule removal, foreground evidence must
be darker than the midpoint between local paper (90th percentile) and the
line's foreground (10th percentile). Synthetic slanted-frame and pale-texture
cases test these conservative exclusions. Counts that cannot meet them remain
unresolved rather than being relabelled as false boundaries.

Overlapping observations of the same white corridor share a separator track
when their widths overlap by at least a quarter of the smaller width. This
prevents their different centre paths from inventing extra columns, while all
finite paths remain in the join guard. A synthetic repeated-window test
checks this independently of page names.

## Results

The initial rules were recorded before evaluation; measurement corrections and their synthetic regressions are disclosed above. Every retained/rejected proposal, its local measurements, all original Q1 crossings and all remaining line/box crossings are in [the machine-readable audit](PAGE_LINES_Q1B_BOUNDARIES.json). Original Q1 files are frozen in `.astra/q1b-baseline/`; rebuilt sidecars and overlays are in `.astra/out/`.

| Gate | Result |
|---|---|
| no_false_boundaries | PASS |
| all_crossings_real | FAIL |
| no_joined_boundary_crossings | PASS |
| complete_addresses | PASS |
| geometry_unchanged | PASS |
| ordinary_exact_except_real_crossings | PASS |
| executed_tests_pass | PASS |

Boundaries: 825 → 258. Records: 10802 lines, 8546 delivered pieces. Ordinary whole lines safely rejoined exactly: 3202/3202.

Remaining line/boundary pairs: 4 real crossing (active), 8 real crossing (diagnostic), 146 unresolved envelope overlap (active), 11 unresolved envelope overlap (diagnostic).

Rule paths are refitted and trimmed against original ink. This can expose additional envelope intersections without moving any line or piece. Removed proposal IDs are Q1 IDs; retained boundary IDs belong to the rebuilt structure. The retained-boundary gate checks the declared pixel tests; fold inference retains Q1 provenance and is not scan-metadata certification.

Original Q1 active crossing ledger (all 119 pairs): 44 false boundary, 6 outside validated rule extent/path, 4 real crossing, 65 unresolved envelope overlap.

## Every page

Crossings count line/boundary pairs; active and discounted records are separate. A removed proposal is unsubstantiated by the fixed rule, not a claim that its entire neighbourhood is blank.

| Page | Boundaries before → after | Rejected | Real active / diagnostic | Unresolved line / box | Columns before → after | Rows before → after | Blocked rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| an-1436ae03653f-p000163 | 10 → 0 | 10 | 0 / 0 | 0 / 0 | 5 → 1 | 37 → 37 | 0 |
| an-1be60011c435-p000215 | 3 → 2 | 1 | 0 / 0 | 0 / 0 | 6 → 5 | 55 → 55 | 0 |
| an-1c6e1c0e929e-p000167 | 0 → 0 | 0 | 0 / 0 | 0 / 0 | 1 → 1 | 29 → 29 | 0 |
| an-1f8e7d022643-p000003 | 5 → 0 | 5 | 0 / 0 | 0 / 0 | 2 → 1 | 18 → 18 | 0 |
| an-2cfe28da5103-p000135 | 5 → 0 | 5 | 0 / 0 | 0 / 0 | 4 → 1 | 90 → 90 | 0 |
| an-3352d912f2e9-p000104 | 6 → 0 | 6 | 0 / 0 | 0 / 0 | 6 → 1 | 26 → 26 | 0 |
| an-466cffad2cba-p000323 | 0 → 0 | 0 | 0 / 0 | 0 / 0 | 1 → 1 | 25 → 25 | 0 |
| an-5c093c79d6bb-p000199 | 14 → 5 | 9 | 0 / 0 | 0 / 0 | 11 → 2 | 76 → 76 | 0 |
| an-778126cc8c2b-p000010 | 4 → 0 | 4 | 0 / 0 | 0 / 0 | 2 → 1 | 37 → 37 | 0 |
| an-7a2b17a3fb0f-p000200 | 87 → 49 | 38 | 0 / 0 | 31 / 27 | 111 → 81 | 688 → 630 | 25 |
| an-9ea1564fcf4f-p000013 | 22 → 3 | 19 | 0 / 0 | 0 / 0 | 6 → 3 | 84 → 84 | 0 |
| an-a3c2bdf81256-p000112 | 11 → 1 | 10 | 0 / 0 | 0 / 0 | 16 → 3 | 152 → 114 | 0 |
| an-a73d22211479-p000301 | 3 → 2 | 1 | 0 / 0 | 0 / 0 | 2 → 3 | 90 → 90 | 0 |
| an-b1a643813945-p000054 | 1 → 0 | 1 | 0 / 0 | 0 / 0 | 1 → 1 | 31 → 31 | 0 |
| an-c153f2c605b3-p000040 | 3 → 0 | 3 | 0 / 0 | 0 / 0 | 3 → 1 | 31 → 31 | 0 |
| an-c2c2053cfc10-p000056 | 11 → 2 | 9 | 0 / 0 | 0 / 0 | 7 → 2 | 75 → 75 | 0 |
| an-c8b96a901917-p000068 | 41 → 2 | 39 | 0 / 0 | 0 / 0 | 12 → 2 | 136 → 136 | 0 |
| an-d3237d690aa0-p000138 | 16 → 6 | 10 | 0 / 0 | 2 / 2 | 29 → 8 | 413 → 314 | 2 |
| an-d6002cf45e4d-p000058 | 4 → 0 | 4 | 0 / 0 | 0 / 0 | 2 → 1 | 6 → 6 | 0 |
| an-d6fd2cf2f618-p000047 | 0 → 0 | 0 | 0 / 0 | 0 / 0 | 1 → 1 | 35 → 35 | 0 |
| an-d83e7a198ade-p000099 | 52 → 2 | 50 | 0 / 0 | 0 / 0 | 12 → 4 | 83 → 83 | 0 |
| an-e46611ae2fcc-p000041 | 18 → 2 | 16 | 0 / 0 | 0 / 0 | 5 → 3 | 63 → 63 | 0 |
| an-e74539ae215c-p000338 | 11 → 2 | 9 | 0 / 0 | 0 / 0 | 2 → 3 | 94 → 94 | 0 |
| an-ef481610a820-p000181 | 3 → 0 | 3 | 0 / 0 | 0 / 0 | 3 → 1 | 34 → 34 | 0 |
| an-fabf591ca801-p000067 | 17 → 3 | 14 | 0 / 0 | 0 / 0 | 6 → 2 | 83 → 83 | 0 |
| an-fd4fa0018ae1-p000037 | 5 → 3 | 2 | 0 / 0 | 0 / 0 | 1 → 1 | 33 → 33 | 0 |
| an-ffccc97c07de-p000152 | 4 → 0 | 4 | 0 / 0 | 0 / 0 | 3 → 1 | 36 → 36 | 0 |
| s2-0683f98f964a6d41cb72-p00003 | 14 → 0 | 14 | 0 / 0 | 0 / 0 | 4 → 1 | 39 → 39 | 0 |
| s2-09f5dfca4af4d74173c6-p00005 | 75 → 0 | 75 | 0 / 0 | 0 / 0 | 4 → 1 | 60 → 60 | 0 |
| s2-0ce9d1025b3f23c7119e-p00001 | 23 → 0 | 23 | 0 / 0 | 0 / 0 | 2 → 1 | 35 → 35 | 0 |
| s2-200e977f2dab5291c42c-p00035 | 55 → 47 | 8 | 0 / 8 | 40 / 23 | 57 → 50 | 303 → 303 | 30 |
| s2-23a70964fda83cb7aeb1-p00003 | 4 → 2 | 2 | 0 / 0 | 0 / 0 | 3 → 5 | 125 → 125 | 0 |
| s2-3229200bf47ca465a42d-p00004 | 4 → 0 | 4 | 0 / 0 | 0 / 0 | 1 → 1 | 38 → 38 | 0 |
| s2-49598b2e848ab1f0ee1e-p00001 | 6 → 0 | 6 | 0 / 0 | 0 / 0 | 3 → 1 | 118 → 118 | 0 |
| s2-5ca02b142a2a3eaf078a-p00002 | 16 → 0 | 16 | 0 / 0 | 0 / 0 | 2 → 1 | 41 → 41 | 0 |
| s2-60f24a3d8a2d714767f2-p00003 | 3 → 0 | 3 | 0 / 0 | 0 / 0 | 4 → 1 | 129 → 129 | 0 |
| s2-63f072d79585d71224b6-p00002 | 8 → 0 | 8 | 0 / 0 | 0 / 0 | 4 → 1 | 45 → 45 | 0 |
| s2-6419488b7f8e69fd20da-p00001 | 105 → 62 | 43 | 3 / 0 | 15 / 13 | 145 → 61 | 713 → 667 | 15 |
| s2-658e6dcb48b540357a9d-p00001 | 16 → 0 | 16 | 0 / 0 | 0 / 0 | 3 → 1 | 35 → 35 | 0 |
| s2-661ddf05c8865e7b2c45-p00009 | 7 → 1 | 6 | 0 / 0 | 0 / 0 | 9 → 3 | 126 → 126 | 0 |
| s2-6f552c96213b4c24a071-p00003 | 13 → 0 | 13 | 0 / 0 | 0 / 0 | 2 → 1 | 38 → 38 | 0 |
| s2-7247ee9b1bc2374b3980-p00001 | 12 → 0 | 12 | 0 / 0 | 0 / 0 | 5 → 1 | 111 → 111 | 0 |
| s2-74cdb23a34ca4a6cd01e-p00002 | 13 → 2 | 11 | 0 / 0 | 0 / 0 | 3 → 5 | 130 → 130 | 0 |
| s2-77d1bd63d5babbe0df73-p00001 | 0 → 0 | 0 | 0 / 0 | 0 / 0 | 1 → 1 | 39 → 39 | 0 |
| s2-80513ae109b4f749ca58-p00003 | 5 → 2 | 3 | 0 / 0 | 1 / 0 | 12 → 5 | 167 → 151 | 0 |
| s2-831443dc5e6f1ccfbaf5-p00020 | 66 → 54 | 12 | 1 / 0 | 68 / 61 | 74 → 57 | 488 → 479 | 55 |
| s2-86865c33eef5932c013b-p00005 | 0 → 0 | 0 | 0 / 0 | 0 / 0 | 1 → 1 | 40 → 40 | 0 |
| s2-93f8070059f938bda524-p00001 | 3 → 0 | 3 | 0 / 0 | 0 / 0 | 2 → 1 | 117 → 117 | 0 |
| s2-9de6cda8f03f0fc60a58-p00005 | 4 → 2 | 2 | 0 / 0 | 0 / 0 | 4 → 3 | 123 → 123 | 0 |
| s2-be269b8c315b16befc35-p00002 | 5 → 0 | 5 | 0 / 0 | 0 / 0 | 4 → 1 | 43 → 43 | 0 |
| s2-d1ed1c2db37f431f4acb-p00001 | 3 → 1 | 2 | 0 / 0 | 0 / 0 | 2 → 3 | 116 → 116 | 0 |
| s2-dee99fdf5214acdc6f25-p00005 | 1 → 0 | 1 | 0 / 0 | 0 / 0 | 1 → 1 | 41 → 41 | 0 |
| s2-dfcc21869afc140111ce-p00001 | 5 → 0 | 5 | 0 / 0 | 0 / 0 | 2 → 1 | 115 → 115 | 0 |
| s2-f9ec82212abc808325d7-p00010 | 3 → 1 | 2 | 0 / 0 | 0 / 0 | 3 → 1 | 38 → 38 | 0 |

## Heading and four table pages

- **an-1f8e7d022643-p000003:** 5 → 0 boundaries. Original active flags: 1 false boundary.
  The Α Κ Ο Λ Ο Υ Θ Ι Α heading is still x=101–1426. Q1 boundary-0003 was 78.0px / 51.58px = 1.512 local x-heights; required width 123.00px. Rejected: spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace.
  [Heading comparison](q1b-evidence/heading.jpg). The frozen fitted x-height above is 51.58px; the nine substantial capital components measure 82, 81, 80, 78, 78, 85, 81, 86, 85px (median 81px, agreeing with the owner’s example). Thus 78px is 0.963 observed capital-heights. No fitted geometry was changed. The gutter also lacks a left-hand block and has only two nearby baselines.
- **an-7a2b17a3fb0f-p000200:** 87 → 49 boundaries. Original active flags: 14 false boundary, 23 unresolved envelope overlap.
- **s2-200e977f2dab5291c42c-p00035:** 55 → 47 boundaries. Original active flags: 2 false boundary, 3 outside validated rule extent/path, 16 unresolved envelope overlap.
- **s2-6419488b7f8e69fd20da-p00001:** 105 → 62 boundaries. Original active flags: 6 false boundary, 1 outside validated rule extent/path, 3 real crossing, 10 unresolved envelope overlap.
- **s2-831443dc5e6f1ccfbaf5-p00020:** 66 → 54 boundaries. Original active flags: 1 false boundary, 2 outside validated rule extent/path, 1 real crossing, 16 unresolved envelope overlap.

## Original pixels beside crossing geometry

Each panel shows the original crop on the left and its frozen ribbon (red) and validated boundary (blue) on the right. All active line/boundary pairs are included; discounted candidates are not drawn.

- an-7a2b17a3fb0f-p000200: [panel 1](q1b-evidence/an-7a2b17a3fb0f-p000200-01.jpg), [panel 2](q1b-evidence/an-7a2b17a3fb0f-p000200-02.jpg), [panel 3](q1b-evidence/an-7a2b17a3fb0f-p000200-03.jpg).
- an-d3237d690aa0-p000138: [panel 1](q1b-evidence/an-d3237d690aa0-p000138-01.jpg).
- s2-200e977f2dab5291c42c-p00035: [panel 1](q1b-evidence/s2-200e977f2dab5291c42c-p00035-01.jpg), [panel 2](q1b-evidence/s2-200e977f2dab5291c42c-p00035-02.jpg), [panel 3](q1b-evidence/s2-200e977f2dab5291c42c-p00035-03.jpg).
- s2-6419488b7f8e69fd20da-p00001: [panel 1](q1b-evidence/s2-6419488b7f8e69fd20da-p00001-01.jpg), [panel 2](q1b-evidence/s2-6419488b7f8e69fd20da-p00001-02.jpg).
- s2-831443dc5e6f1ccfbaf5-p00020: [panel 1](q1b-evidence/s2-831443dc5e6f1ccfbaf5-p00020-01.jpg), [panel 2](q1b-evidence/s2-831443dc5e6f1ccfbaf5-p00020-02.jpg), [panel 3](q1b-evidence/s2-831443dc5e6f1ccfbaf5-p00020-03.jpg), [panel 4](q1b-evidence/s2-831443dc5e6f1ccfbaf5-p00020-04.jpg), [panel 5](q1b-evidence/s2-831443dc5e6f1ccfbaf5-p00020-05.jpg), [panel 6](q1b-evidence/s2-831443dc5e6f1ccfbaf5-p00020-06.jpg).

## Real crossings for the next detector round

L/R are original letter-band ink pixels within three own x-heights of the stop; shared rows must cover at least 0.2 x-height. Rule ink within 0.35 x-height is excluded. Discounted records remain diagnostic and are never rendered/delivered. IDs refer to rebuilt structure; the Q1 proposal ID is also preserved. Geometry was left unchanged.

| Page | Line | Pieces | Boundary (Q1 proposal) | Status | L/R ink | Shared rows | x-height |
|---|---:|---|---|---|---:|---:|---:|
| s2-200e977f2dab5291c42c-p00035 | 162 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 854/310 | 43 | 44.00 |
| s2-200e977f2dab5291c42c-p00035 | 164 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 891/416 | 44 | 44.39 |
| s2-200e977f2dab5291c42c-p00035 | 166 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 873/315 | 42 | 43.34 |
| s2-200e977f2dab5291c42c-p00035 | 168 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 904/244 | 43 | 43.49 |
| s2-200e977f2dab5291c42c-p00035 | 170 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 824/280 | 43 | 43.88 |
| s2-200e977f2dab5291c42c-p00035 | 172 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 986/239 | 44 | 45.06 |
| s2-200e977f2dab5291c42c-p00035 | 175 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 918/231 | 44 | 44.21 |
| s2-200e977f2dab5291c42c-p00035 | 176 | — | boundary-0029 (boundary-0035) | superseded by bounded table/prose delivery | 1046/199 | 39 | 43.00 |
| s2-6419488b7f8e69fd20da-p00001 | 479 | 112 | boundary-0054 (boundary-0094) | active | 502/188 | 25 | 26.00 |
| s2-6419488b7f8e69fd20da-p00001 | 682 | 315 | boundary-0022 (boundary-0055) | active | 241/81 | 21 | 19.00 |
| s2-6419488b7f8e69fd20da-p00001 | 1570 | 1203 | boundary-0053 (boundary-0093) | active | 178/450 | 21 | 27.00 |
| s2-831443dc5e6f1ccfbaf5-p00020 | 958 | 582 | boundary-0004 (boundary-0013) | active | 1038/636 | 44 | 44.72 |

## Rejected proposals and refused rows

### an-1436ae03653f-p000163

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007.
- Removed (isolated_thin_support): boundary-0008.
- Removed (sustained_straight_thin_ink, isolated_thin_support, no_long_unprinted_gap): boundary-0009.
### an-1be60011c435-p000215

- Removed (wide_at_local_scale): boundary-0000.
### an-1f8e7d022643-p000003

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0002, boundary-0003, boundary-0004.
### an-2cfe28da5103-p000135

- Removed (wide_at_local_scale): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0003, boundary-0004.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support): boundary-0002.
### an-3352d912f2e9-p000104

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004.
- Removed (sustained_straight_thin_ink, isolated_thin_support, no_long_unprinted_gap): boundary-0005.
### an-5c093c79d6bb-p000199

- Removed (separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0002, boundary-0003, boundary-0007.
- Removed (sustained_straight_thin_ink, no_long_unprinted_gap): boundary-0008, boundary-0009, boundary-0010, boundary-0011.
- Removed (isolated_thin_support): boundary-0012.
### an-778126cc8c2b-p000010

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002.
- Removed (sustained_straight_thin_ink, no_long_unprinted_gap): boundary-0003.
### an-7a2b17a3fb0f-p000200

- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0045.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0043, boundary-0044.
- Removed (wide_at_local_scale): boundary-0002, boundary-0042.
- Removed (wide_at_local_scale, original_whitespace): boundary-0003, boundary-0046.
- Removed (isolated_thin_support): boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0010, boundary-0011, boundary-0016, boundary-0017, boundary-0022, boundary-0025, boundary-0026, boundary-0027, boundary-0036, boundary-0047, boundary-0050, boundary-0052, boundary-0053, boundary-0054, boundary-0055, boundary-0058, boundary-0062, boundary-0065, boundary-0074, boundary-0078, boundary-0081, boundary-0082, boundary-0083, boundary-0085.
- Refused row-00386, lines 418: boundary-0019 (unresolved envelope overlap).
- Refused row-00392, lines 426: boundary-0019 (unresolved envelope overlap).
- Refused row-00487, lines 652: boundary-0006 (unresolved envelope overlap).
- Refused row-00498, lines 668: boundary-0006 (unresolved envelope overlap).
- Refused row-00430, lines 532: boundary-0006 (unresolved envelope overlap).
- Refused row-00511, lines 693: boundary-0001 (unresolved envelope overlap).
- Refused row-00493, lines 661: boundary-0002 (unresolved envelope overlap).
- Refused row-00390, lines 424: boundary-0011 (unresolved envelope overlap).
- Refused row-00495, lines 665: boundary-0015 (unresolved envelope overlap).
- Refused row-00683, lines 1059: boundary-0041 (unresolved envelope overlap).
- Refused row-00789, lines 1266: boundary-0024 (unresolved envelope overlap), boundary-0025 (unresolved envelope overlap).
- Refused row-00892, lines 1429: boundary-0024 (unresolved envelope overlap), boundary-0025 (unresolved envelope overlap), boundary-0030 (unresolved envelope overlap).
- Refused row-00969, lines 1564: boundary-0030 (unresolved envelope overlap).
- Refused row-00927, lines 1488: boundary-0036 (unresolved envelope overlap).
- Refused row-00667, lines 1036: boundary-0039 (unresolved envelope overlap).
- Refused row-00738, lines 1138: boundary-0027 (unresolved envelope overlap).
- Refused row-00745, lines 1158: boundary-0027 (unresolved envelope overlap).
- Refused row-00751, lines 1169: boundary-0026 (unresolved envelope overlap), boundary-0027 (unresolved envelope overlap), boundary-0035 (unresolved envelope overlap).
- Refused row-00853, lines 1360: boundary-0026 (unresolved envelope overlap).
- Refused row-00801, lines 1281: boundary-0029 (unresolved envelope overlap).
- Refused row-00806, lines 1286: boundary-0031 (unresolved envelope overlap).
- Refused row-00737, lines 1134: boundary-0040 (unresolved envelope overlap).
- Refused row-00950, lines 1522: boundary-0044 (unresolved envelope overlap), boundary-0045 (unresolved envelope overlap).
- Refused row-00732, lines 1126: boundary-0042 (unresolved envelope overlap).
- Refused row-00882, lines 1414: boundary-0032 (unresolved envelope overlap).
### an-9ea1564fcf4f-p000013

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0009, boundary-0010, boundary-0011, boundary-0012, boundary-0013, boundary-0014.
- Removed (wide_at_local_scale): boundary-0002.
- Removed (sustained_straight_thin_ink, isolated_thin_support): boundary-0015.
- Removed (sustained_straight_thin_ink, isolated_thin_support, no_long_unprinted_gap): boundary-0016.
- Removed (sustained_straight_thin_ink, no_long_unprinted_gap): boundary-0017, boundary-0018.
- Removed (isolated_thin_support): boundary-0020.
### an-a3c2bdf81256-p000112

- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0002.
- Removed (wide_at_local_scale, bilateral_support, original_whitespace): boundary-0001, boundary-0003.
- Removed (isolated_thin_support): boundary-0004.
- Removed (long_enough, sustained_straight_thin_ink, isolated_thin_support): boundary-0005.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0006.
- Removed (wide_at_local_scale, bilateral_support): boundary-0007.
- Removed (wide_at_local_scale): boundary-0008, boundary-0009.
### an-a73d22211479-p000301

- Removed (wide_at_local_scale, original_whitespace): boundary-0000.
### an-b1a643813945-p000054

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000.
### an-c153f2c605b3-p000040

- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001.
- Removed (isolated_thin_support): boundary-0002.
### an-c2c2053cfc10-p000056

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0002, boundary-0004, boundary-0006, boundary-0009.
- Removed (separate_blocks, persistent, bilateral_support): boundary-0003, boundary-0005, boundary-0007, boundary-0008.
### an-c8b96a901917-p000068

- Removed (wide_at_local_scale, original_whitespace): boundary-0000, boundary-0003.
- Removed (bilateral_support): boundary-0001.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0004, boundary-0006, boundary-0008, boundary-0009, boundary-0010, boundary-0011, boundary-0012, boundary-0014, boundary-0015, boundary-0016, boundary-0017, boundary-0018, boundary-0019, boundary-0020, boundary-0021, boundary-0022, boundary-0023, boundary-0024, boundary-0025, boundary-0026, boundary-0027.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support): boundary-0005.
- Removed (spacing_observed, separate_blocks, persistent): boundary-0007.
- Removed (separate_blocks, persistent, bilateral_support): boundary-0013.
- Removed (sustained_straight_thin_ink, no_long_unprinted_gap): boundary-0028.
- Removed (isolated_thin_support): boundary-0029, boundary-0030, boundary-0031, boundary-0032, boundary-0033, boundary-0034, boundary-0035, boundary-0036, boundary-0037, boundary-0038.
- Removed (sustained_straight_thin_ink, isolated_thin_support): boundary-0039.
### an-d3237d690aa0-p000138

- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0003, boundary-0004, boundary-0006, boundary-0010.
- Removed (wide_at_local_scale, separate_blocks, bilateral_support): boundary-0002.
- Removed (wide_at_local_scale, bilateral_support): boundary-0005.
- Removed (separate_blocks, persistent, bilateral_support): boundary-0007.
- Removed (wide_at_local_scale, persistent, bilateral_support): boundary-0011.
- Refused row-00466, lines 852: boundary-0000 (unresolved envelope overlap).
- Refused row-00613, lines 1335: boundary-0003 (unresolved envelope overlap).
### an-d6002cf45e4d-p000058

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.
- Removed (isolated_thin_support): boundary-0002, boundary-0003.
### an-d83e7a198ade-p000099

- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0004, boundary-0006, boundary-0008, boundary-0017.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0005, boundary-0007, boundary-0009, boundary-0010, boundary-0012, boundary-0013, boundary-0014, boundary-0015, boundary-0016, boundary-0018, boundary-0019, boundary-0020, boundary-0021, boundary-0023, boundary-0024, boundary-0026, boundary-0027, boundary-0028, boundary-0029, boundary-0030, boundary-0031.
- Removed (bilateral_support, original_whitespace): boundary-0002.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support): boundary-0003.
- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0011.
- Removed (wide_at_local_scale, persistent): boundary-0022.
- Removed (separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0025.
- Removed (isolated_thin_support): boundary-0033, boundary-0034, boundary-0036, boundary-0042, boundary-0043, boundary-0044, boundary-0046, boundary-0048, boundary-0049, boundary-0050.
- Removed (sustained_straight_thin_ink, isolated_thin_support): boundary-0035, boundary-0037, boundary-0038, boundary-0039, boundary-0040, boundary-0041, boundary-0045.
- Removed (sustained_straight_thin_ink): boundary-0047.
### an-e46611ae2fcc-p000041

- Removed (wide_at_local_scale): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008.
- Removed (isolated_thin_support): boundary-0009, boundary-0010, boundary-0011, boundary-0012, boundary-0014, boundary-0015, boundary-0016.
- Removed (sustained_straight_thin_ink, isolated_thin_support): boundary-0013.
### an-e74539ae215c-p000338

- Removed (bilateral_support): boundary-0000, boundary-0007.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0003, boundary-0008.
- Removed (bilateral_support, original_whitespace): boundary-0002, boundary-0004, boundary-0006.
- Removed (separate_blocks, bilateral_support, original_whitespace): boundary-0005.
### an-ef481610a820-p000181

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.
- Removed (sustained_straight_thin_ink, no_long_unprinted_gap): boundary-0002.
### an-fabf591ca801-p000067

- Removed (wide_at_local_scale): boundary-0000.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0002.
- Removed (separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0003.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0004, boundary-0006, boundary-0007, boundary-0008, boundary-0009, boundary-0010.
- Removed (sustained_straight_thin_ink, isolated_thin_support): boundary-0011.
- Removed (isolated_thin_support): boundary-0012, boundary-0013, boundary-0014, boundary-0015.
### an-fd4fa0018ae1-p000037

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.
### an-ffccc97c07de-p000152

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003.
### s2-0683f98f964a6d41cb72-p00003

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0009.
- Removed (long_enough, sustained_straight_thin_ink, isolated_thin_support): boundary-0010, boundary-0011, boundary-0012, boundary-0013.
### s2-09f5dfca4af4d74173c6-p00005

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0009, boundary-0010, boundary-0011, boundary-0012, boundary-0013, boundary-0014, boundary-0015, boundary-0016, boundary-0017, boundary-0018, boundary-0019, boundary-0020, boundary-0021, boundary-0022, boundary-0023, boundary-0024, boundary-0025, boundary-0026, boundary-0027, boundary-0029, boundary-0030, boundary-0031, boundary-0032, boundary-0033, boundary-0034, boundary-0035, boundary-0036, boundary-0037, boundary-0038, boundary-0039, boundary-0040, boundary-0041, boundary-0042, boundary-0043, boundary-0044, boundary-0045, boundary-0046, boundary-0047, boundary-0048, boundary-0049, boundary-0050, boundary-0051, boundary-0052, boundary-0053, boundary-0054, boundary-0055, boundary-0056, boundary-0057, boundary-0058, boundary-0059, boundary-0060, boundary-0061, boundary-0062, boundary-0063, boundary-0064, boundary-0065, boundary-0066, boundary-0067, boundary-0068, boundary-0069, boundary-0070, boundary-0071, boundary-0072, boundary-0073, boundary-0074.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0028.
### s2-0ce9d1025b3f23c7119e-p00001

- Removed (wide_at_local_scale, bilateral_support, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0006, boundary-0007, boundary-0008, boundary-0010, boundary-0011, boundary-0013, boundary-0017, boundary-0022.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0005, boundary-0009, boundary-0012, boundary-0014, boundary-0015, boundary-0016, boundary-0018, boundary-0019, boundary-0020, boundary-0021.
### s2-200e977f2dab5291c42c-p00035

- Removed (bilateral_support): boundary-0000.
- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001.
- Removed (wide_at_local_scale): boundary-0002, boundary-0004.
- Removed (wide_at_local_scale, bilateral_support, original_whitespace): boundary-0003.
- Removed (isolated_thin_support): boundary-0018, boundary-0047, boundary-0052.
- Refused row-00332, lines 332: boundary-0016 (unresolved envelope overlap).
- Refused row-00449, lines 509: boundary-0042 (unresolved envelope overlap).
- Refused row-00490, lines 555: boundary-0006 (unresolved envelope overlap).
- Refused row-00418, lines 470: boundary-0001 (unresolved envelope overlap).
- Refused row-00611, lines 705: boundary-0009 (unresolved envelope overlap).
- Refused row-00389, lines 427: boundary-0024 (unresolved envelope overlap).
- Refused row-00408, lines 457: boundary-0024 (unresolved envelope overlap), boundary-0042 (unresolved envelope overlap).
- Refused row-00420, lines 472: boundary-0042 (unresolved envelope overlap).
- Refused row-00594, lines 684: boundary-0030 (unresolved envelope overlap).
- Refused row-00535, lines 610: boundary-0006 (unresolved envelope overlap).
- Refused row-00396, lines 438: boundary-0010 (unresolved envelope overlap).
- Refused row-00348, lines 368: boundary-0044 (unresolved envelope overlap).
- Refused row-00351, lines 372: boundary-0003 (unresolved envelope overlap).
- Refused row-00427, lines 484: boundary-0003 (unresolved envelope overlap).
- Refused row-00542, lines 618: boundary-0017 (unresolved envelope overlap).
- Refused row-00532, lines 607: boundary-0017 (unresolved envelope overlap).
- Refused row-00353, lines 374: boundary-0029 (unresolved envelope overlap).
- Refused row-00428, lines 485: boundary-0033 (unresolved envelope overlap).
- Refused row-00435, lines 494: boundary-0014 (unresolved envelope overlap).
- Refused row-00523, lines 595: boundary-0045 (unresolved envelope overlap).
- Refused row-00502, lines 569: boundary-0045 (unresolved envelope overlap).
- Refused row-00615, lines 710: boundary-0037 (unresolved envelope overlap).
- Refused row-00437, lines 497: boundary-0002 (unresolved envelope overlap).
- Refused row-00515, lines 585: boundary-0022 (unresolved envelope overlap).
- Refused row-00475, lines 537: boundary-0025 (unresolved envelope overlap).
- Refused row-00356, lines 377: boundary-0021 (unresolved envelope overlap).
- Refused row-00619, lines 714: boundary-0000 (unresolved envelope overlap).
- Refused row-00372, lines 401: boundary-0028 (unresolved envelope overlap).
- Refused row-00488, lines 553: boundary-0000 (unresolved envelope overlap).
- Refused row-00333, lines 333: boundary-0028 (unresolved envelope overlap).
### s2-23a70964fda83cb7aeb1-p00003

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001.
- Removed (no_long_unprinted_gap): boundary-0003.
### s2-3229200bf47ca465a42d-p00004

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000.
- Removed (long_enough, sustained_straight_thin_ink, isolated_thin_support): boundary-0001, boundary-0002, boundary-0003.
### s2-49598b2e848ab1f0ee1e-p00001

- Removed (wide_at_local_scale, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0002.
- Removed (separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0003.
- Removed (sustained_straight_thin_ink, no_long_unprinted_gap): boundary-0004.
- Removed (isolated_thin_support): boundary-0005.
### s2-5ca02b142a2a3eaf078a-p00002

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0007, boundary-0008, boundary-0009.
- Removed (sustained_straight_thin_ink, isolated_thin_support, no_long_unprinted_gap): boundary-0010, boundary-0011, boundary-0012, boundary-0013.
- Removed (isolated_thin_support): boundary-0014, boundary-0015.
### s2-60f24a3d8a2d714767f2-p00003

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.
- Removed (no_long_unprinted_gap): boundary-0002.
### s2-63f072d79585d71224b6-p00002

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006.
- Removed (sustained_straight_thin_ink, isolated_thin_support, no_long_unprinted_gap): boundary-0007.
### s2-6419488b7f8e69fd20da-p00001

- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0005, boundary-0010, boundary-0013, boundary-0018, boundary-0019, boundary-0020, boundary-0025, boundary-0026.
- Removed (spacing_observed, wide_at_local_scale, separate_blocks, persistent, bilateral_support): boundary-0002, boundary-0028.
- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0003, boundary-0004, boundary-0006, boundary-0007, boundary-0008, boundary-0009, boundary-0022, boundary-0024.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support): boundary-0011, boundary-0023, boundary-0027.
- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support): boundary-0012, boundary-0021.
- Removed (wide_at_local_scale, bilateral_support, original_whitespace): boundary-0014, boundary-0015.
- Removed (wide_at_local_scale, persistent, bilateral_support, original_whitespace): boundary-0016.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0017.
- Removed (isolated_thin_support): boundary-0029, boundary-0041, boundary-0043, boundary-0047, boundary-0057, boundary-0062, boundary-0063, boundary-0074, boundary-0076, boundary-0077, boundary-0078, boundary-0101, boundary-0102.
- Removed (long_enough, sustained_straight_thin_ink, isolated_thin_support): boundary-0100.
- Refused row-00475, lines 494: boundary-0011 (unresolved envelope overlap).
- Refused row-00818, lines 1255: boundary-0018 (unresolved envelope overlap).
- Refused row-00779, lines 1153: boundary-0055 (unresolved envelope overlap).
- Refused row-00789, lines 1181: boundary-0055 (unresolved envelope overlap).
- Refused row-00467, lines 470: boundary-0038 (unresolved envelope overlap), boundary-0061 (unresolved envelope overlap).
- Refused row-01008, lines 1718: boundary-0024 (unresolved envelope overlap).
- Refused row-00591, lines 750: boundary-0035 (unresolved envelope overlap).
- Refused row-00991, lines 1667: boundary-0009 (unresolved envelope overlap).
- Refused row-00606, lines 776: boundary-0001 (unresolved envelope overlap), boundary-0004 (unresolved envelope overlap).
- Refused row-00870, lines 1407: boundary-0009 (unresolved envelope overlap), boundary-0041 (unresolved envelope overlap).
- Refused row-00469, lines 479: boundary-0054 (real crossing).
- Refused row-00489, lines 536: boundary-0054 (unresolved envelope overlap).
- Refused row-00558, lines 682: boundary-0022 (real crossing).
- Refused row-00944, lines 1570: boundary-0053 (real crossing).
- Refused row-00855, lines 1377: boundary-0057 (unresolved envelope overlap).
### s2-658e6dcb48b540357a9d-p00001

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0009, boundary-0010, boundary-0011, boundary-0012, boundary-0013, boundary-0014, boundary-0015.
### s2-661ddf05c8865e7b2c45-p00009

- Removed (wide_at_local_scale, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0002, boundary-0003.
- Removed (sustained_straight_thin_ink, isolated_thin_support, no_long_unprinted_gap): boundary-0004.
- Removed (isolated_thin_support): boundary-0005.
### s2-6f552c96213b4c24a071-p00003

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003, boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0009.
- Removed (isolated_thin_support): boundary-0010, boundary-0011, boundary-0012.
### s2-7247ee9b1bc2374b3980-p00001

- Removed (wide_at_local_scale): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0003, boundary-0005, boundary-0008, boundary-0009, boundary-0010, boundary-0011.
- Removed (separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0002, boundary-0004.
- Removed (separate_blocks, persistent, bilateral_support): boundary-0006, boundary-0007.
### s2-74cdb23a34ca4a6cd01e-p00002

- Removed (wide_at_local_scale): boundary-0000, boundary-0002.
- Removed (isolated_thin_support): boundary-0004, boundary-0005, boundary-0006, boundary-0007, boundary-0008, boundary-0009, boundary-0010, boundary-0011, boundary-0012.
### s2-80513ae109b4f749ca58-p00003

- Removed (wide_at_local_scale, bilateral_support): boundary-0000.
- Removed (separate_blocks, persistent, bilateral_support): boundary-0001.
- Removed (wide_at_local_scale, bilateral_support, original_whitespace): boundary-0002.
### s2-831443dc5e6f1ccfbaf5-p00020

- Removed (wide_at_local_scale, bilateral_support): boundary-0000, boundary-0001, boundary-0002.
- Removed (bilateral_support): boundary-0003.
- Removed (separate_blocks, persistent, bilateral_support): boundary-0004, boundary-0006, boundary-0008.
- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support): boundary-0005.
- Removed (wide_at_local_scale, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0007.
- Removed (isolated_thin_support): boundary-0043, boundary-0047, boundary-0052.
- Refused row-00448, lines 482: boundary-0019 (unresolved envelope overlap), boundary-0043 (unresolved envelope overlap), boundary-0047 (unresolved envelope overlap).
- Refused row-00453, lines 489: boundary-0019 (unresolved envelope overlap), boundary-0043 (unresolved envelope overlap), boundary-0047 (unresolved envelope overlap).
- Refused row-00543, lines 604: boundary-0003 (unresolved envelope overlap).
- Refused row-00555, lines 617: boundary-0016 (unresolved envelope overlap).
- Refused row-00572, lines 640: boundary-0016 (unresolved envelope overlap).
- Refused row-00581, lines 651: boundary-0016 (unresolved envelope overlap).
- Refused row-00688, lines 781: boundary-0015 (unresolved envelope overlap).
- Refused row-00758, lines 861: boundary-0033 (unresolved envelope overlap), boundary-0046 (unresolved envelope overlap).
- Refused row-00752, lines 855: boundary-0033 (unresolved envelope overlap).
- Refused row-00434, lines 464: boundary-0043 (unresolved envelope overlap), boundary-0047 (unresolved envelope overlap).
- Refused row-00642, lines 723: boundary-0042 (unresolved envelope overlap).
- Refused row-00545, lines 606: boundary-0042 (unresolved envelope overlap).
- Refused row-00835, lines 950: boundary-0015 (unresolved envelope overlap).
- Refused row-00511, lines 565: boundary-0028 (unresolved envelope overlap).
- Refused row-00618, lines 694: boundary-0008 (unresolved envelope overlap).
- Refused row-00455, lines 491: boundary-0024 (unresolved envelope overlap).
- Refused row-00732, lines 833: boundary-0030 (unresolved envelope overlap).
- Refused row-00762, lines 866: boundary-0008 (unresolved envelope overlap), boundary-0045 (unresolved envelope overlap), boundary-0053 (unresolved envelope overlap).
- Refused row-00842, lines 957: boundary-0013 (unresolved envelope overlap).
- Refused row-00483, lines 530: boundary-0036 (unresolved envelope overlap).
- Refused row-00843, lines 958: boundary-0004 (real crossing).
- Refused row-00847, lines 962: boundary-0044 (unresolved envelope overlap).
- Refused row-00844, lines 959: boundary-0001 (unresolved envelope overlap).
- Refused row-00845, lines 960: boundary-0039 (unresolved envelope overlap).
- Refused row-00568, lines 633: boundary-0001 (unresolved envelope overlap), boundary-0014 (unresolved envelope overlap).
- Refused row-00690, lines 784: boundary-0006 (unresolved envelope overlap), boundary-0025 (unresolved envelope overlap).
- Refused row-00717, lines 816: boundary-0018 (unresolved envelope overlap), boundary-0021 (unresolved envelope overlap).
- Refused row-00766, lines 870: boundary-0018 (unresolved envelope overlap).
- Refused row-00408, lines 427: boundary-0007 (unresolved envelope overlap).
- Refused row-00460, lines 499: boundary-0007 (unresolved envelope overlap).
- Refused row-00645, lines 729: boundary-0018 (unresolved envelope overlap), boundary-0021 (unresolved envelope overlap).
- Refused row-00674, lines 764: boundary-0032 (unresolved envelope overlap).
- Refused row-00693, lines 789: boundary-0010 (unresolved envelope overlap).
- Refused row-00749, lines 851: boundary-0010 (unresolved envelope overlap).
- Refused row-00807, lines 919: boundary-0010 (unresolved envelope overlap).
- Refused row-00420, lines 448: boundary-0011 (unresolved envelope overlap).
- Refused row-00486, lines 533: boundary-0011 (unresolved envelope overlap).
- Refused row-00593, lines 666: boundary-0032 (unresolved envelope overlap).
- Refused row-00646, lines 730: boundary-0032 (unresolved envelope overlap).
- Refused row-00709, lines 807: boundary-0035 (unresolved envelope overlap).
- Refused row-00720, lines 819: boundary-0035 (unresolved envelope overlap).
- Refused row-00817, lines 930: boundary-0026 (unresolved envelope overlap).
- Refused row-00465, lines 507: boundary-0031 (unresolved envelope overlap).
- Refused row-00493, lines 542: boundary-0009 (unresolved envelope overlap).
- Refused row-00526, lines 584: boundary-0009 (unresolved envelope overlap).
- Refused row-00527, lines 585: boundary-0009 (unresolved envelope overlap).
- Refused row-00659, lines 747: boundary-0005 (unresolved envelope overlap).
- Refused row-00770, lines 875: boundary-0000 (unresolved envelope overlap).
- Refused row-00841, lines 956: boundary-0017 (unresolved envelope overlap), boundary-0022 (unresolved envelope overlap).
- Refused row-00446, lines 480: boundary-0005 (unresolved envelope overlap).
- Refused row-00504, lines 555: boundary-0005 (unresolved envelope overlap).
- Refused row-00552, lines 614: boundary-0005 (unresolved envelope overlap).
- Refused row-00632, lines 710: boundary-0005 (unresolved envelope overlap).
- Refused row-00439, lines 472: boundary-0000 (unresolved envelope overlap).
- Refused row-00729, lines 830: boundary-0000 (unresolved envelope overlap).
### s2-93f8070059f938bda524-p00001

- Removed (wide_at_local_scale, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0002.
### s2-9de6cda8f03f0fc60a58-p00005

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.
### s2-be269b8c315b16befc35-p00002

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001, boundary-0002, boundary-0003.
- Removed (isolated_thin_support): boundary-0004.
### s2-d1ed1c2db37f431f4acb-p00001

- Removed (wide_at_local_scale, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001.
### s2-dee99fdf5214acdc6f25-p00005

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000.
### s2-dfcc21869afc140111ce-p00001

- Removed (wide_at_local_scale, original_whitespace): boundary-0000.
- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0001, boundary-0002, boundary-0003, boundary-0004.
### s2-f9ec82212abc808325d7-p00010

- Removed (spacing_observed, separate_blocks, persistent, bilateral_support, original_whitespace): boundary-0000, boundary-0001.

## Unresolved envelope overlaps

These are not proven real crossings. A valid stop is not removed merely to make the crossing count zero. The join guard remains conservative. Any entry below fails the all-crossings-real gate.

- an-7a2b17a3fb0f-p000200, line 418, boundary boundary-0019: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 424, boundary boundary-0011: L/R ink [315, 0], shared rows 0, x-height 21.00.
- an-7a2b17a3fb0f-p000200, line 426, boundary boundary-0019: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 532, boundary boundary-0006: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 652, boundary boundary-0006: L/R ink [300, 0], shared rows 0, x-height 19.29.
- an-7a2b17a3fb0f-p000200, line 661, boundary boundary-0002: L/R ink [0, 0], shared rows 0, x-height 20.73.
- an-7a2b17a3fb0f-p000200, line 665, boundary boundary-0015: L/R ink [0, 0], shared rows 0, x-height 22.86.
- an-7a2b17a3fb0f-p000200, line 668, boundary boundary-0006: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 693, boundary boundary-0001: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1036, boundary boundary-0039: L/R ink [0, 17], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1059, boundary boundary-0041: L/R ink [0, 0], shared rows 0, x-height 19.09.
- an-7a2b17a3fb0f-p000200, line 1126, boundary boundary-0042: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1134, boundary boundary-0040: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1138, boundary boundary-0027: L/R ink [242, 0], shared rows 0, x-height 22.50.
- an-7a2b17a3fb0f-p000200, line 1158, boundary boundary-0027: L/R ink [312, 0], shared rows 0, x-height 23.50.
- an-7a2b17a3fb0f-p000200, line 1169, boundary boundary-0026: L/R ink [0, 257], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1169, boundary boundary-0027: L/R ink [237, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1169, boundary boundary-0035: L/R ink [0, 257], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1266, boundary boundary-0024: L/R ink [368, 0], shared rows 0, x-height 22.04.
- an-7a2b17a3fb0f-p000200, line 1266, boundary boundary-0025: L/R ink [368, 0], shared rows 0, x-height 22.04.
- an-7a2b17a3fb0f-p000200, line 1281, boundary boundary-0029: L/R ink [383, 0], shared rows 0, x-height 20.03.
- an-7a2b17a3fb0f-p000200, line 1286, boundary boundary-0031: L/R ink [0, 0], shared rows 0, x-height 22.50.
- an-7a2b17a3fb0f-p000200, line 1360, boundary boundary-0026: L/R ink [0, 246], shared rows 0, x-height 24.50.
- an-7a2b17a3fb0f-p000200, line 1414, boundary boundary-0032: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1429, boundary boundary-0024: L/R ink [109, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1429, boundary boundary-0025: L/R ink [109, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1429, boundary boundary-0030: L/R ink [109, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1488, boundary boundary-0036: L/R ink [353, 0], shared rows 0, x-height 19.20.
- an-7a2b17a3fb0f-p000200, line 1522, boundary boundary-0044: L/R ink [376, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1522, boundary boundary-0045: L/R ink [376, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1564, boundary boundary-0030: L/R ink [132, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 418, boundary boundary-0019, piece 57: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 424, boundary boundary-0011, piece 63: L/R ink [315, 0], shared rows 0, x-height 21.00.
- an-7a2b17a3fb0f-p000200, line 426, boundary boundary-0019, piece 65: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 532, boundary boundary-0006, piece 171: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 652, boundary boundary-0006, piece 291: L/R ink [300, 0], shared rows 0, x-height 19.29.
- an-7a2b17a3fb0f-p000200, line 665, boundary boundary-0015, piece 304: L/R ink [0, 0], shared rows 0, x-height 22.86.
- an-7a2b17a3fb0f-p000200, line 668, boundary boundary-0006, piece 307: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 693, boundary boundary-0001, piece 332: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1036, boundary boundary-0039, piece 675: L/R ink [0, 17], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1126, boundary boundary-0042, piece 765: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1134, boundary boundary-0040, piece 773: L/R ink [0, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1138, boundary boundary-0027, piece 777: L/R ink [242, 0], shared rows 0, x-height 22.50.
- an-7a2b17a3fb0f-p000200, line 1158, boundary boundary-0027, piece 797: L/R ink [312, 0], shared rows 0, x-height 23.50.
- an-7a2b17a3fb0f-p000200, line 1169, boundary boundary-0026, piece 808: L/R ink [0, 257], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1169, boundary boundary-0027, piece 808: L/R ink [237, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1169, boundary boundary-0035, piece 808: L/R ink [0, 257], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1266, boundary boundary-0024, piece 905: L/R ink [368, 0], shared rows 0, x-height 22.04.
- an-7a2b17a3fb0f-p000200, line 1266, boundary boundary-0025, piece 905: L/R ink [368, 0], shared rows 0, x-height 22.04.
- an-7a2b17a3fb0f-p000200, line 1281, boundary boundary-0029, piece 920: L/R ink [383, 0], shared rows 0, x-height 20.03.
- an-7a2b17a3fb0f-p000200, line 1360, boundary boundary-0026, piece 999: L/R ink [0, 246], shared rows 0, x-height 24.50.
- an-7a2b17a3fb0f-p000200, line 1429, boundary boundary-0024, piece 1068: L/R ink [109, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1429, boundary boundary-0025, piece 1068: L/R ink [109, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1429, boundary boundary-0030, piece 1068: L/R ink [109, 0], shared rows 0, x-height 22.00.
- an-7a2b17a3fb0f-p000200, line 1488, boundary boundary-0036, piece 1127: L/R ink [353, 0], shared rows 0, x-height 19.20.
- an-7a2b17a3fb0f-p000200, line 1522, boundary boundary-0044, piece 1161: L/R ink [376, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1522, boundary boundary-0045, piece 1161: L/R ink [376, 0], shared rows 0, x-height 23.00.
- an-7a2b17a3fb0f-p000200, line 1564, boundary boundary-0030, piece 1203: L/R ink [132, 0], shared rows 0, x-height 22.00.
- an-d3237d690aa0-p000138, line 852, boundary boundary-0000: L/R ink [0, 0], shared rows 0, x-height 29.00.
- an-d3237d690aa0-p000138, line 1335, boundary boundary-0003: L/R ink [0, 0], shared rows 0, x-height 44.00.
- an-d3237d690aa0-p000138, line 852, boundary boundary-0000, piece 536: L/R ink [0, 0], shared rows 0, x-height 29.00.
- an-d3237d690aa0-p000138, line 1335, boundary boundary-0003, piece 1019: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 160, boundary boundary-0029: L/R ink [153, 17], shared rows 3, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 266, boundary boundary-0034: L/R ink [0, 0], shared rows 0, x-height 39.79.
- s2-200e977f2dab5291c42c-p00035, line 307, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 53.00.
- s2-200e977f2dab5291c42c-p00035, line 308, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 47.00.
- s2-200e977f2dab5291c42c-p00035, line 309, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 55.00.
- s2-200e977f2dab5291c42c-p00035, line 310, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-200e977f2dab5291c42c-p00035, line 311, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 32.45.
- s2-200e977f2dab5291c42c-p00035, line 312, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 35.00.
- s2-200e977f2dab5291c42c-p00035, line 313, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 33.00.
- s2-200e977f2dab5291c42c-p00035, line 332, boundary boundary-0016: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 333, boundary boundary-0028: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 368, boundary boundary-0044: L/R ink [0, 0], shared rows 0, x-height 41.00.
- s2-200e977f2dab5291c42c-p00035, line 372, boundary boundary-0003: L/R ink [4, 0], shared rows 0, x-height 43.55.
- s2-200e977f2dab5291c42c-p00035, line 374, boundary boundary-0029: L/R ink [154, 0], shared rows 0, x-height 43.50.
- s2-200e977f2dab5291c42c-p00035, line 377, boundary boundary-0021: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 401, boundary boundary-0028: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 427, boundary boundary-0024: L/R ink [420, 0], shared rows 0, x-height 45.00.
- s2-200e977f2dab5291c42c-p00035, line 438, boundary boundary-0010: L/R ink [116, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 457, boundary boundary-0024: L/R ink [422, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 457, boundary boundary-0042: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 470, boundary boundary-0001: L/R ink [147, 0], shared rows 0, x-height 43.00.
- s2-200e977f2dab5291c42c-p00035, line 472, boundary boundary-0042: L/R ink [684, 0], shared rows 0, x-height 43.00.
- s2-200e977f2dab5291c42c-p00035, line 484, boundary boundary-0003: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 485, boundary boundary-0033: L/R ink [138, 98], shared rows 5, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 494, boundary boundary-0014: L/R ink [355, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 497, boundary boundary-0002: L/R ink [128, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 509, boundary boundary-0042: L/R ink [559, 0], shared rows 0, x-height 42.50.
- s2-200e977f2dab5291c42c-p00035, line 537, boundary boundary-0025: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 553, boundary boundary-0000: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 555, boundary boundary-0006: L/R ink [892, 0], shared rows 0, x-height 43.50.
- s2-200e977f2dab5291c42c-p00035, line 569, boundary boundary-0045: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 585, boundary boundary-0022: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 595, boundary boundary-0045: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 607, boundary boundary-0017: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 610, boundary boundary-0006: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 618, boundary boundary-0017: L/R ink [1225, 0], shared rows 0, x-height 43.00.
- s2-200e977f2dab5291c42c-p00035, line 684, boundary boundary-0030: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 705, boundary boundary-0009: L/R ink [0, 0], shared rows 0, x-height 42.20.
- s2-200e977f2dab5291c42c-p00035, line 710, boundary boundary-0037: L/R ink [669, 0], shared rows 0, x-height 44.49.
- s2-200e977f2dab5291c42c-p00035, line 714, boundary boundary-0000: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 332, boundary boundary-0016, piece 15: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 333, boundary boundary-0028, piece 16: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 372, boundary boundary-0003, piece 55: L/R ink [4, 0], shared rows 0, x-height 43.55.
- s2-200e977f2dab5291c42c-p00035, line 427, boundary boundary-0024, piece 110: L/R ink [420, 0], shared rows 0, x-height 45.00.
- s2-200e977f2dab5291c42c-p00035, line 438, boundary boundary-0010, piece 121: L/R ink [116, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 457, boundary boundary-0024, piece 140: L/R ink [422, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 457, boundary boundary-0042, piece 140: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 470, boundary boundary-0001, piece 153: L/R ink [147, 0], shared rows 0, x-height 43.00.
- s2-200e977f2dab5291c42c-p00035, line 472, boundary boundary-0042, piece 155: L/R ink [684, 0], shared rows 0, x-height 43.00.
- s2-200e977f2dab5291c42c-p00035, line 484, boundary boundary-0003, piece 167: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 485, boundary boundary-0033, piece 168: L/R ink [138, 98], shared rows 5, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 494, boundary boundary-0014, piece 177: L/R ink [355, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 497, boundary boundary-0002, piece 180: L/R ink [128, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 509, boundary boundary-0042, piece 192: L/R ink [559, 0], shared rows 0, x-height 42.50.
- s2-200e977f2dab5291c42c-p00035, line 537, boundary boundary-0025, piece 220: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 553, boundary boundary-0000, piece 236: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 555, boundary boundary-0006, piece 238: L/R ink [892, 0], shared rows 0, x-height 43.50.
- s2-200e977f2dab5291c42c-p00035, line 569, boundary boundary-0045, piece 252: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 610, boundary boundary-0006, piece 293: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 618, boundary boundary-0017, piece 301: L/R ink [1225, 0], shared rows 0, x-height 43.00.
- s2-200e977f2dab5291c42c-p00035, line 684, boundary boundary-0030, piece 367: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-200e977f2dab5291c42c-p00035, line 710, boundary boundary-0037, piece 393: L/R ink [669, 0], shared rows 0, x-height 44.49.
- s2-200e977f2dab5291c42c-p00035, line 714, boundary boundary-0000, piece 397: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-6419488b7f8e69fd20da-p00001, line 470, boundary boundary-0038: L/R ink [0, 0], shared rows 0, x-height 18.00.
- s2-6419488b7f8e69fd20da-p00001, line 470, boundary boundary-0061: L/R ink [0, 0], shared rows 0, x-height 18.00.
- s2-6419488b7f8e69fd20da-p00001, line 494, boundary boundary-0011: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 536, boundary boundary-0054: L/R ink [315, 0], shared rows 0, x-height 25.00.
- s2-6419488b7f8e69fd20da-p00001, line 750, boundary boundary-0035: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 776, boundary boundary-0001: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 776, boundary boundary-0004: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1153, boundary boundary-0055: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1181, boundary boundary-0055: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1255, boundary boundary-0018: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1377, boundary boundary-0057: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1407, boundary boundary-0009: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1407, boundary boundary-0041: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1667, boundary boundary-0009: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1718, boundary boundary-0024: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 470, boundary boundary-0061, piece 103: L/R ink [0, 0], shared rows 0, x-height 18.00.
- s2-6419488b7f8e69fd20da-p00001, line 494, boundary boundary-0011, piece 127: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 536, boundary boundary-0054, piece 169: L/R ink [315, 0], shared rows 0, x-height 25.00.
- s2-6419488b7f8e69fd20da-p00001, line 750, boundary boundary-0035, piece 383: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 776, boundary boundary-0001, piece 409: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 776, boundary boundary-0004, piece 409: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1153, boundary boundary-0055, piece 786: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1181, boundary boundary-0055, piece 814: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1255, boundary boundary-0018, piece 888: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1377, boundary boundary-0057, piece 1010: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1407, boundary boundary-0041, piece 1040: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1667, boundary boundary-0009, piece 1300: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-6419488b7f8e69fd20da-p00001, line 1718, boundary boundary-0024, piece 1351: L/R ink [0, 0], shared rows 0, x-height 26.00.
- s2-80513ae109b4f749ca58-p00003, line 36, boundary boundary-0001: L/R ink [0, 0], shared rows 0, x-height 25.07.
- s2-831443dc5e6f1ccfbaf5-p00020, line 52, boundary boundary-0042: L/R ink [135, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 427, boundary boundary-0007: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 448, boundary boundary-0011: L/R ink [0, 421], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 464, boundary boundary-0043: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 464, boundary boundary-0047: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 472, boundary boundary-0000: L/R ink [52, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 480, boundary boundary-0005: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 482, boundary boundary-0019: L/R ink [366, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 482, boundary boundary-0043: L/R ink [376, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 482, boundary boundary-0047: L/R ink [376, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 489, boundary boundary-0019: L/R ink [458, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 489, boundary boundary-0043: L/R ink [125, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 489, boundary boundary-0047: L/R ink [458, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 491, boundary boundary-0024: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 499, boundary boundary-0007: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 507, boundary boundary-0031: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 530, boundary boundary-0036: L/R ink [0, 319], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 533, boundary boundary-0011: L/R ink [0, 459], shared rows 0, x-height 31.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 542, boundary boundary-0009: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 555, boundary boundary-0005: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 565, boundary boundary-0028: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 584, boundary boundary-0009: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 585, boundary boundary-0009: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 604, boundary boundary-0003: L/R ink [0, 638], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 606, boundary boundary-0042: L/R ink [134, 0], shared rows 0, x-height 44.71.
- s2-831443dc5e6f1ccfbaf5-p00020, line 614, boundary boundary-0005: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 617, boundary boundary-0016: L/R ink [624, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 633, boundary boundary-0001: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 633, boundary boundary-0014: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 640, boundary boundary-0016: L/R ink [709, 0], shared rows 0, x-height 44.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 651, boundary boundary-0016: L/R ink [577, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 666, boundary boundary-0032: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 694, boundary boundary-0008: L/R ink [717, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 710, boundary boundary-0005: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 723, boundary boundary-0042: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 729, boundary boundary-0018: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 729, boundary boundary-0021: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 730, boundary boundary-0032: L/R ink [0, 773], shared rows 0, x-height 45.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 747, boundary boundary-0005: L/R ink [0, 453], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 764, boundary boundary-0032: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 781, boundary boundary-0015: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 784, boundary boundary-0006: L/R ink [778, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 784, boundary boundary-0025: L/R ink [627, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 789, boundary boundary-0010: L/R ink [0, 730], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 807, boundary boundary-0035: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 816, boundary boundary-0018: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 816, boundary boundary-0021: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 819, boundary boundary-0035: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 830, boundary boundary-0000: L/R ink [0, 279], shared rows 0, x-height 32.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 833, boundary boundary-0030: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 851, boundary boundary-0010: L/R ink [0, 725], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 855, boundary boundary-0033: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 861, boundary boundary-0033: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 861, boundary boundary-0046: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 866, boundary boundary-0008: L/R ink [678, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 866, boundary boundary-0045: L/R ink [678, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 866, boundary boundary-0053: L/R ink [0, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 870, boundary boundary-0018: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 875, boundary boundary-0000: L/R ink [524, 0], shared rows 0, x-height 29.30.
- s2-831443dc5e6f1ccfbaf5-p00020, line 919, boundary boundary-0010: L/R ink [0, 430], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 930, boundary boundary-0026: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 950, boundary boundary-0015: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 956, boundary boundary-0017: L/R ink [0, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 956, boundary boundary-0022: L/R ink [0, 786], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 957, boundary boundary-0013: L/R ink [766, 0], shared rows 0, x-height 47.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 959, boundary boundary-0001: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 960, boundary boundary-0039: L/R ink [0, 0], shared rows 0, x-height 45.82.
- s2-831443dc5e6f1ccfbaf5-p00020, line 962, boundary boundary-0044: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 427, boundary boundary-0007, piece 51: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 448, boundary boundary-0011, piece 72: L/R ink [0, 421], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 464, boundary boundary-0043, piece 88: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 464, boundary boundary-0047, piece 88: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 472, boundary boundary-0000, piece 96: L/R ink [52, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 480, boundary boundary-0005, piece 104: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 482, boundary boundary-0019, piece 106: L/R ink [366, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 482, boundary boundary-0043, piece 106: L/R ink [376, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 482, boundary boundary-0047, piece 106: L/R ink [376, 0], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 489, boundary boundary-0019, piece 113: L/R ink [458, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 489, boundary boundary-0043, piece 113: L/R ink [125, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 489, boundary boundary-0047, piece 113: L/R ink [458, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 491, boundary boundary-0024, piece 115: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 499, boundary boundary-0007, piece 123: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 507, boundary boundary-0031, piece 131: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 530, boundary boundary-0036, piece 154: L/R ink [0, 319], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 533, boundary boundary-0011, piece 157: L/R ink [0, 459], shared rows 0, x-height 31.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 542, boundary boundary-0009, piece 166: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 555, boundary boundary-0005, piece 179: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 565, boundary boundary-0028, piece 189: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 584, boundary boundary-0009, piece 208: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 585, boundary boundary-0009, piece 209: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 604, boundary boundary-0003, piece 228: L/R ink [0, 638], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 606, boundary boundary-0042, piece 230: L/R ink [134, 0], shared rows 0, x-height 44.71.
- s2-831443dc5e6f1ccfbaf5-p00020, line 614, boundary boundary-0005, piece 238: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 633, boundary boundary-0001, piece 257: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 633, boundary boundary-0014, piece 257: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 640, boundary boundary-0016, piece 264: L/R ink [709, 0], shared rows 0, x-height 44.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 651, boundary boundary-0016, piece 275: L/R ink [577, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 666, boundary boundary-0032, piece 290: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 694, boundary boundary-0008, piece 318: L/R ink [717, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 710, boundary boundary-0005, piece 334: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 723, boundary boundary-0042, piece 347: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 729, boundary boundary-0018, piece 353: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 729, boundary boundary-0021, piece 353: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 730, boundary boundary-0032, piece 354: L/R ink [0, 773], shared rows 0, x-height 45.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 747, boundary boundary-0005, piece 371: L/R ink [0, 453], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 781, boundary boundary-0015, piece 405: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 784, boundary boundary-0006, piece 408: L/R ink [778, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 784, boundary boundary-0025, piece 408: L/R ink [627, 0], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 789, boundary boundary-0010, piece 413: L/R ink [0, 730], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 807, boundary boundary-0035, piece 431: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 816, boundary boundary-0018, piece 440: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 819, boundary boundary-0035, piece 443: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 830, boundary boundary-0000, piece 454: L/R ink [0, 279], shared rows 0, x-height 32.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 833, boundary boundary-0030, piece 457: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 851, boundary boundary-0010, piece 475: L/R ink [0, 725], shared rows 0, x-height 45.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 855, boundary boundary-0033, piece 479: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 861, boundary boundary-0033, piece 485: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 861, boundary boundary-0046, piece 485: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 866, boundary boundary-0008, piece 490: L/R ink [678, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 866, boundary boundary-0045, piece 490: L/R ink [678, 0], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 875, boundary boundary-0000, piece 499: L/R ink [524, 0], shared rows 0, x-height 29.30.
- s2-831443dc5e6f1ccfbaf5-p00020, line 919, boundary boundary-0010, piece 543: L/R ink [0, 430], shared rows 0, x-height 43.50.
- s2-831443dc5e6f1ccfbaf5-p00020, line 930, boundary boundary-0026, piece 554: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 950, boundary boundary-0015, piece 574: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 956, boundary boundary-0022, piece 580: L/R ink [0, 786], shared rows 0, x-height 43.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 957, boundary boundary-0013, piece 581: L/R ink [766, 0], shared rows 0, x-height 47.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 959, boundary boundary-0001, piece 583: L/R ink [0, 0], shared rows 0, x-height 44.00.
- s2-831443dc5e6f1ccfbaf5-p00020, line 960, boundary boundary-0039, piece 584: L/R ink [0, 0], shared rows 0, x-height 45.82.
- s2-831443dc5e6f1ccfbaf5-p00020, line 962, boundary boundary-0044, piece 586: L/R ink [0, 0], shared rows 0, x-height 44.00.

## Validation

**2232 passed, 16 skipped, 0 failures, 0 errors** (2248 collected). The 16 skipped tests require unavailable Chromium; they were not executed. The existing Docling deprecation warning remains.

The audit reads back all 54 line/cell/structure/row outputs, compares all original non-address fields, checks reciprocal addresses and tests every emitted joined ribbon against every retained stop. No OCR or line detection is rerun. Pixel segmentation proposals remain detector inputs; validated boundaries are structure outputs, so line geometry and delivered pieces stay frozen.

```sh
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "$PY" -m pytest -p no:cacheprovider --junitxml=.astra/q1b-tests.xml -q
PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/glyphs/archive/review_line_boundaries.py
```
