# Round 3, track C — type properties, font geometry and tables

This is a **partial feature result**, with a usable conservative missing-line
prototype. Body size, component spacing/stroke, supported guide contacts, local
pitch/phase and regional table evidence are explicitly rendered. Both fast routes
have per-line or per-slot comparisons. Fourteen line polygons are added on twelve
supplied discrepancy pages after inspection, with round 2 separators retained.
Named font identification, complete table recognition and script-specific guide
semantics are unfinished. Nothing modifies the production pages implementation.

The physical premise is explicit: a repeated type grid can expose an empty slot
that contains body ink. It cannot prove that ink belongs to the front page.
The first combined experiment actually added a mirrored verso row; the retained
stack rejects that case using track B's independent reflected-glyph witnesses.

## Evidence and scope

Output root: [features_type](../../.astra/fast_lines/out/features_type/README.md).
`active-type.json`, `active-tables.json`, `active-lattice.json`,
`active-corrections.json` and `active-benchmark.json` locate final directories.
All review images have accompanying numeric evidence; images, not model line
counts, were used to adjudicate examples. No PDF text layer was used.

- Exact existing manifest: 54 development + 141 supplied new pages. New pages
  comprise 40 agreement, 80 discrepancy and 21 additional discrepancy pages.
  Forty-one new pages have direction `ours_more`; direction is not correctness.
- Cached slow model/glyph statistics on six typography anchors were reused with
  source-image and line-file SHA-256 checks. Only active model lines are drawn.
- Independent typography: nine pages, 814 detector items, original-pixel and both
  fast versions; all have line-indexed comparisons and raw/slow/R1/R2 crop boards.
- Tables: ten selected discrepancy pages, two requested development anchors,
  one prose and one ornamental-frame control. Fourteen three-route renderings.
- Type lattice: all 195 pages have dense raw-ridge, R1 and R2 images/records.
  Combined scout after Q8 nominates 261 slots, 53 with sampled body support.
  Seventeen pages make 25 local detector calls in the final study.
- All 71 slots in the initial 44-page lattice study were inspected on twelve
  enlarged boards. All proposed additions in combined v1, the changed completion
  examples in v2, all sixteen v3 additions, and all fourteen final v4 additions
  were inspected in raw/after crops. This is not exhaustive transcription or a
  claim that every glyph on all 195 pages was manually audited.
- The 44 held-out pages were never searched for or read. Orientation is parked.
  The existing parked development page passes through; sideways selected table
  `s2-7534648e60694be1d180-p00016` has no accepted type correction.

## “We want to recognize properties of different fonts like, font, size, spacing of letters, and so on, relative to the page and the book.”

### Explicit rendering and iterations

`model/<page>.font.jpg` overlays cached per-character size classes. The adjacent
`.a07.jpg` shows old `font_guides` family IDs; `.detail-NN.jpg` exposes raw print,
font classes and guide contacts. Apparatus `an-d83e7a198ade-p000099` is the clearest
counterexample: A07 assigns 65 families to 120 detector bands despite visibly
repeated verse bodies. It uses only 25 horizontal samples and 61 vertical samples,
measures total ink extent rather than body contacts, partitions by page quarters,
and compares against an immutable first exemplar. A straddling apparatus box
mixes adjacent rows; accents and local sampling then become artificial fonts.
Bilingual `an-ffccc97c07de-p000152` has 25 A07 families from 34 bands.

Independent `type_profiles.measure_line` deskews the localized strip, makes a
local-paper contrast mask and renders connected bodies, detached upper marks and
inter-component gaps. It records body-contact distance, width/body, gap quartiles
and ridge stroke/body. These are connected ink pieces, **not identified letters**.
Size groups use a bounded total size span; they are explicitly not font names.

1. V1 let neighbouring rows contaminate contact modes. Apparatus lines 75–79 and
   bilingual lines 15–19 show this directly.
2. V2 selected the nearest density band, restricted bottom contacts and suppressed
   guides with fewer than five supporting contacts. Arabic sampled line 17 still
   reported 75.5 px against dense 28 px: connected-script pieces are not Greek
   letter bodies. Short capital/lowercase mixtures also remained unstable.
3. V3 samples more finely and labels a large joined-component population uncertain.
   Arabic line 17 becomes about 32.4 versus dense 28 px but remains uncertain;
   another short row still gives a wrong large size. Such values are never borrowed
   as reliable x-height. Apparatus now has four supported size bins, not four fonts.

### Both fast routes against the rendering

Route 1 renders components at 24 samples per provisional body height. Route 2
uses 64 horizontal density probes and a body-envelope step. R2 does not recover
component spacing, stroke geometry or script-specific marks; those fields remain
absent. No attempt is made to fabricate parity by calling density height x-height.

Each record stores absolute guide/height values and normalized differences.
The following is a compact index into the line records, **not an accuracy score**.
Errors are absolute R1/dense contact-height differences divided by dense height,
restricted to lines both routes mark supported. Excluding uncertainty hides no
counts: those counts are shown explicitly.

| Page | Detector lines | Dense uncertain | Both supported | R1 median / p95 difference |
|---|---:|---:|---:|---:|
| an-d3237d690aa0-p000138 | 297 | 238 | 42 | .022 / .089 |
| an-d83e7a198ade-p000099 | 120 | 19 | 98 | .004 / .080 |
| an-ffccc97c07de-p000152 | 34 | 19 | 11 | .018 / .074 |
| an-e74539ae215c-p000338 | 97 | 25 | 67 | .025 / .113 |
| s2-77d1bd63d5babbe0df73-p00001 | 39 | 4 | 35 | .028 / .110 |
| an-1f8e7d022643-p000003 | 22 | 7 | 15 | .018 / .094 |

The dense small-print anchor is a major remaining failure: 238/297 localizations
are uncertain, often fragments or straddles. Good supported-line differences do
not make that page solved.

### Relative to the book

`book-v1/` renders the same measurements on allowed `an-1ba3fdb1436b` pages 9, 12
and 15. Following the model's independent-book-reference principle, each page is
compared to the median of the **other** pages. Dense median body/page-width values
are .0160631, .0163743 and .0163551; ratios to the other pages are .98157, 1.01019
and 1.00841. Gap and stroke ratios remain descriptive. `type_book.summarize` is
reusable but does not replace `process_book`, identify a font family or correct
scan framing. A full book/font atlas is unfinished.

No detector polygons are changed from size groups alone. Local body measurements
are conditional diagnostic evidence; a clear uncertainty flag is not sufficient
for automatic scale borrowing. Track B used
these contact measurements offline with its own proxy fallback.

## “We want to consider how many lines are required to express the geometry of the font, and if accents if that script has them and so on; without necessarily using them.”

The cached six-guide renderings show the model's full hypothesis; the independent
rendering draws only supported body top/bottom, tall top, descender bottom and
upper-mark top/bottom contacts. A line may therefore have two, four, six or zero
supported contacts. Supported contact count is **not** a theorem about how many
rails a script needs. A short all-capital row can lack evidence for descenders or
accents without proving that the font/script lacks them.

Greek verse in apparatus model lines 25–30 shows stable bodies plus distinct upper
marks. The bilingual Arabic section shows why imposing those six meanings is
unsafe. The control's short capitals and mixed case demonstrate abstention. The
v1→v3 row isolation and sampling iterations above apply to these guides too.

Route 1 retains contact and detached-mark evidence and per-guide differences.
Route 2 only supplies two density-envelope edges and cannot answer accent
semantics. Returned baselines are always null: a body-bottom mode or grid axis is
not a semantic baseline. Lower detached marks, robust joined-script partitioning,
script identification and curved contact surfaces remain unfinished.

### Pitch/phase as a visible consequence, then missed-line recovery

`type_lattice` groups spatially overlapping, similarly scaled long localizations,
fits local inter-row pitch, and draws phase/grid axes in blue. Dense original-pixel
body-density ridges are magenta. Empty *interior* slots bracketed by repeated rows
are orange; measured supported bodies are green; already-owned body centres grey.
Every slot records actual bodies, contact support and old-polygon ownership.

- V1 used body-centroid residual. It rejected the real Theotokion gap densely
  (47 bodies, residual .3407 heights) while the sampled version accepted it
  (45, .289). The grid phase was correct; the contact statistic was wrong.
- V2 used repeated body-bottom contacts. All 41 `ours_more` pages were rendered;
  `s2-86865c33eef5932c013b-p00007` exposes two long missing rows, but an unbracketed
  third row remains outside this witness. Curved `s2-3229200bf47ca465a42d-p00006`
  still has inconsistent slot/contact evidence.
- V3 explicitly measures polygon ownership at body centres. This refuses already
  covered short rows on `s2-99b031dc55985b500294-p00003`; axis-only occupancy was
  insufficient. R1 includes sampled whole-block raw ridges; R2 checks only
  nominated slots. Both keep all original-pixel slot comparisons.

The final runtime uses R2 as the cheap scout, then **original pixels only in
positive slots**. It requires dense contact and ownership agreement, protects
regional table hypotheses, applies B4 reflected-glyph veto, and reruns Paddle in
a small context crop. A candidate must enclose nominated bodies, have little
already-owned ink, avoid enclosing existing line centres/crop edges, and pass
regional separator verification. Existing detector items are not replaced.

Component completion reuses stopped `0b052af`, but inspection caught its detached
initial growth wrongly pulling the preceding row's A into `an-00f143ecce59-p000221`.
That growth was removed. Only principally intersected, unowned components may
expand. New cross-separator newspaper rows on 4959 p4/p5 are refused when Q8's
physical rule/clear-flank checks cannot safely separate them. No threshold was
relaxed to save those additions. Final v4 also refuses sampled/dense disagreement
on ef4816 p181 and portions of 3229 p6.

Final additions: one each on `an-00f143ecce59-p000221`, `an-1ba3fdb1436b-p000009`,
`an-1ba3fdb1436b-p000015`, `an-778126cc8c2b-p000007`, `an-c8b96a901917-p000036`,
`an-c99f1c450f55-p000046`, `an-dbd045ccd84c-p000101`, `an-dbd045ccd84c-p000359`,
`an-fd4fa0018ae1-p000028`, `an-fd4fa0018ae1-p000031`; two each on
`an-9ea1564fcf4f-p000202` and `s2-86865c33eef5932c013b-p00007`.
These are fourteen polygons, not fourteen completely repaired pages. The French
row still overlaps a stamp; the c99 row touches the preceding drop cap's lower
portion; curly terminal glyphs/marks remain imperfect. There is no automatic
stamp eraser, no reading-order repair and no perfect glyph-ownership claim.

A late independent check by track A found a false-clear uncertainty flag:
3229 p4 source 24 reports 40.4 px with `uncertain=False`, while nearby same-type
sources 14/30/35/36 report 21.3/22.7/22.7/23.4 px and the DB band is 26 px.
Its raw crop suggests neighbouring-row/mark contamination. A's independently
rendered `cooperation/body-scale-00.jpg` and JSON, copied into C's outputs with
source attribution, preserve this counterexample.
No runtime module may treat `uncertain=False` alone as calibrated confidence.
Our final recovery uses its separate local grid proxy and dense slot contacts;
it does not borrow this full-line height census. This rendering failure remains
unfinished, rather than being silently rethresholded after timing.

Whole missing blocks, edge rows, irregular poetry, tiny apparatus and severe curl
are not solved. No precision/recall is inferred from `ours_more` or the model list.

## “We want to recognize tables and let small detector handle those”

Slow rendering combines original-pixel LSD rule segments/intersections, repeated
short-cell alignment and explicit dot centres/chains. Cached Docling regions are
purple on the development anchors. For new pages, `selection.json` gives table
counts but not proposal coordinates; no missing Docling box was invented.

V1 aligned columns across both physical leaves of `an-7a2b17a3fb0f-p000200`. V2
required nearby columns or intervening support; this removes the cross-leaf join
but leaves fragmented overlapping regions. Numeric 8314 p20 aligns with much of
the Docling proposal. Name/vote 4b80 p9 defeats short-cell tests because the small
detector already merges names, leaders and votes into long rows.

V2 therefore explicitly rendered dot leaders. V3 admitted observed thicker dot
components; V4 bound region expansion to actual leader rows, removing adjacent
prose from 4b80 p9. V5 replaces transitive punctuation flood-fill with regular dot
chains inside localized rows. This makes parts of 922e p5 explicit, but protection
is fragmented, not a complete table boundary. **63c4 p4 remains missed**: short or
irregular dot runs do not supply repeated six-dot chains. The sideways selected
page is unchanged; one fast rule hypothesis there is not accepted orientation.

Route 1 uses reduced-pixel long-run morphology, intersections and 16-sample/body
dot components. Route 2 uses box alignment and 8-sample/body dot chains, without
the rule graph. Every detector cell/row has a dense/R1/R2 membership record.
Both prose and ornamental-frame controls produce no protected table regions.
Rule edges alone cannot identify semantic cells or front-page ownership.

This module is usable as **regional protection for new type corrections**, with
uncertainty retained. It never joins, splits or removes existing table items.
The final runtime tests even alignment hypotheses conservatively; the small
Paddle detector continues handling tables. It is not a complete table detector.

## Timing and validation

The measured timing table is appended below from raw per-page receipts. Two fresh
runs include full-page Paddle preprocessing/inference/postprocessing, Q8, all type
scouting, conditional dense pixels, table/ownership dependencies, local inference,
completion and rule protection. Decode and one-time model startup are recorded
separately. Image/JSON rendering is excluded. Single-thread ONNX/OpenCV; shared Mac,
short sequential batches, no background jobs. These are observations under shared
load, not held-out latency guarantees. Font/table census costs are separately
repeated in `feature-timings.json`; they are not secretly paid on clean pages.

Seventeen mechanism/invariant tests pass. Validation additionally checks exact
allowlist coverage, detector JSON, input/retained-item preservation relative to
Q8, both repeat counts, unchanged agreement pages and every final addition's
raw/after review. The root output README contains the legend and clickable gallery.

## Reuse and next work

Reused Q8 unchanged, A07 as a counterexample, A04 lattice ideas, stopped `0b052af`
completion/regional rule guards and B4 ownership/photometry (source hashes in
`features_type/reuse.json`; imports renamed into owned `type_ink_*` snapshots).
B's result that front/verso may share pitch directly falsified a grid-only veto.
Geometry's contour genealogy remains complementary; it was not added as an
unvalidated dependency. A's warning that continuous rules can belong to the back
page prevents calling a rule a front-ownership proof.

Gave B measured contact-height and type-grid interfaces/renderings; it used them
offline for stroke normalization and front/back grid comparisons. A used apparatus
scale evidence. Shared board and direct relay messages record both directions.

Next: improve the **renderings** of joined scripts and dense apparatus, establish
component-to-row ownership around drop caps/stamps, represent curved local type
grids, and make dot-leader/table boundaries complete. Then use A's exact contour
genealogy for safe recovered endpoints and an explicit book font atlas. None of
those is claimed finished by the fourteen additions or the speed measurements.

## Measured final receipts

All times below are milliseconds. Each row covers a complete independent repeat.

| Cohort/repeat | n | C median / p95 / max | Q8+C median / p95 / max | Full detector+stack median / max |
|---|---:|---|---|---|
| agreement_r1 | 40 | 0.938 / 1.603 / 2.163 | 13.003 / 16.725 / 27.247 | 143.044 / 190.283 |
| agreement_r2 | 40 | 0.881 / 1.708 / 2.186 | 12.126 / 15.172 / 25.660 | 133.237 / 169.924 |
| new_discrepancy_r1 | 101 | 1.898 / 180.859 / 432.744 | 16.597 / 192.090 / 456.934 | 162.733 / 608.482 |
| new_discrepancy_r2 | 101 | 1.786 / 182.266 / 452.320 | 16.051 / 194.447 / 478.172 | 159.732 / 635.566 |
| correction_pages_r1 | 12 | 87.667 / 247.948 / 265.944 | 94.974 / 263.508 / 283.383 | 241.525 / 431.660 |
| correction_pages_r2 | 12 | 89.081 / 233.019 / 267.138 | 96.440 / 247.606 / 284.182 | 237.423 / 426.985 |

Raw numbers for every page: `benchmark-v4-fa2e30087b47/`. All 40 agreement outputs are identical in both fresh repeats. C adds under 3 ms on every agreement observation in these runs. All observed C corrections fit below one second; this is not a held-out guarantee. Full-stack times are reported separately from correction cost.

On-demand feature census, milliseconds (median / maximum across the named pages):

| Feature / route | repeat 1 | repeat 2 |
|---|---|---|
| typography / slow | 80.437 / 228.558 | 82.181 / 246.460 |
| typography / explicit | 45.626 / 122.305 | 49.682 / 130.699 |
| typography / heuristic | 4.638 / 23.180 | 4.676 / 24.570 |
| tables / slow | 286.031 / 746.328 | 313.545 / 834.340 |
| tables / explicit | 76.933 / 164.141 | 86.375 / 164.607 |
| tables / heuristic | 37.222 / 79.575 | 40.913 / 83.282 |
