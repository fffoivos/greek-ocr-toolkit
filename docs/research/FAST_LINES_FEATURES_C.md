# Rounds 3–4, track C — type properties, font geometry and tables

**Round 4 continuation is below, under “Round 4”.** Round 3 receipts remain
unchanged for comparison. The experimental round 4 C pipeline adds two more
visually verified rows (sixteen total); the separately composed stack retains
the frozen adapter and its fifteen additions. Those are different pipelines.

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

## Round 4 — deeper physical renderings and conditional recovery

Round 4 remains **partial**. There are usable native component/row renderers,
an anonymous glyph atlas with alternate exemplars, explicit dot-run interiors,
and a wider type-grid scout. These do not establish font identity or semantic
script guides. Complete table boundaries remain unresolved. The inspected
experimental corrections recover two additional rows beside drop capitals,
without losing or changing any round 3 output item.

[Round 4 evidence and legend](../../.astra/fast_lines/out/features_type/round4-README.md)
and [image index](../../.astra/fast_lines/out/features_type/round4.html) link all
final page renderings, raw/slow/fast crop boards, failures and numeric records.
Outputs are outside git. The 195-page allowlist is unchanged; no held-out page,
PDF text layer, production pages implementation or production pages test changed.

### Font properties, size and spacing relative to the page and book

Round 3's A07 fragmentation was not repaired by renaming its clusters. The new
`type_identity.extract(gray, items, version=2)` exposes native connected ink,
physical bounding boxes, all localization owners, observed height, page-relative
size and aspect. `sample` limits exemplar work per line; `witnesses` returns up
to three alternatives and their physical size ratios. These are observed ink
pieces, not recognized characters. The earlier contact/spacing/stroke renderer
remains available and is not replaced with inferred font names.

The explicit atlas covers the three typography anchors and all four permitted
`an-1ba3fdb1436b` pages, 9, 12, 15 and 35. Seven within-page and six across-page
pairings expose repeated shapes against the actual print. This is a small book
atlas, not a claim to have processed the whole book or identified its fonts.
Viewed rho, mu, theta, beta and dense dictionary forms recur with different
impressions. Conversely, Greek and Arabic sticks can be very similar; a stick
match is weak font evidence.

1. V1 found identical apparatus glyphs with similarity 1.000 under different
   line IDs. Inspection showed overlapping detector localizations had supplied
   the **same physical ink twice**. V2 deduplicates coordinates while retaining
   all owners, and excludes common ownership from within-page matching.
2. Native route S uses a 64-cell normalized glyph image; route 1 uses 24 cells.
   Both preserve aspect and compare actual silhouettes. R2 v2 used eight-cell
   horizontal/vertical marginals. The book-page crops showed theta matched to a
   slash and a comma matched to beta. High similarity was not correctness.
3. R2 v3 (`identity_routes.py`) retains a 4×4 spatial occupancy grid as well as
   marginals, and penalizes differences in observed counters. The same inspected
   book crops no longer make those two errors. Sigma-like and circular pieces
   still interchange, and damage can itself change a counter. No font label or
   recovery decision uses this heuristic.

The audit retains 10,442 glyph/route records with source line IDs, each native
alternative, and each fast best match. Examples of R1/R2 best-in-native-top-three
counts are 218/254 versus 178/254 for book page 9→12, 676/790 versus 468/790 for
the apparatus, and 1,025/1,437 versus 665/1,436 for the dense dictionary.
These counts measure agreement with a rendering, **not letter recognition or
font accuracy**. A different real exemplar may be just as valid. All thirteen
pairings have separate records and crop boards; no pooled score accepts a route.

Extraction dominates the measured atlas cost. Reduced matching does not make
the entire pipeline cheap: the two repeated complete pairing measurements reach
roughly two seconds on the dense dictionary. The atlas therefore remains an
offline component and book diagnostic, not a dependency paid on clean pages.
B borrowed its stable native extraction snapshot for observability experiments.

### How many lines express font geometry, including joined scripts and accents

`type_rows.render(gray, item, route=..., version=3)` begins with a deskewed strip
wide enough to expose neighboring rows. It renders connected-body candidates,
detached marks, density ridges and valleys, component-to-row assignment, contact
populations, and upper/lower paths containing the central ink mass. A row may
have several bands or no supported single height. `baseline` stays null.
The paths are physical envelopes; they are not the six semantic Greek guides,
and their number does not prove how many semantic guides a script requires.

The five pages contain 533 detector localizations. Each has original pixels,
native evidence, route 1 at 24 samples per provisional body height, and route 2
at eight. All 1,066 line/route comparisons are saved, including every supported
row count, joined flag, and available height discrepancy. Selected raw crops
from each iteration and the twelve largest final height disagreements were
inspected. This is not a claim to have manually read every glyph in every crop.

1. V1 independently chose upper and lower contact modes. On the bilingual page,
   modes from different rows manufactured bodies of 72 or 120 px. V2 requires
   contacts from the same component population and limits ridge spacing by the
   prior scale. Greek line 16 becomes 26 px; apparatus 75/78/79 show 15 px bodies.
2. V2 still included partially clipped neighbors. V3 excludes strip-edge and
   band-edge clipped bodies, and measures joined support by ink area rather
   than component count, since detached dots dilute a count.
3. The late geometry counterexample, `s2-3229200bf47ca465a42d-p00004` source 24,
   had round 3 height 40.4 px with a false-clear uncertainty flag while nearby
   same-type rows were about 21–23 px. All three v3 routes now abstain there.
   This repairs that observation; it does not calibrate the flags generally.

Important remaining failure: bilingual lines 17, 26 and 31 still have
`joined=False` despite visibly connected script. Line 17 gives native/R1/R2
28.0/32.38/48.56 px; line 26 gives 23.5/46.05/null. The scalar is consequently
not a trustworthy x-height. An early board shorthand suggesting line 17 was
reliably flagged joined was corrected after this audit. Line 19 abstains.
No other track borrows these new values as runtime heights.

Native ambiguous counts are 170/297 dense dictionary, 18/120 apparatus, 9/34
bilingual, 11/43 curled source page and 1/39 clean control. R1/R2 supported-row
count disagreements, page by page, are respectively 13/33, 5/11, 1/3, 2/8 and
2/3. Reduced sampling can merge adjacent rows; the largest dense R2 height
discrepancy is 0.630 of the prior height. Physical mass envelopes are useful
renderings even where a single body height is not justified. These measurements
remain diagnostic and cause no detector reshaping or line deletion.

### Tables and their complete boundaries

`type_table_extent.analyze` adds explicit terminal dot-run evidence to the
existing rule/numeric-grid table renderer. It retains each proposed dot, each
row witness and the regional extent; it never treats an unprotected area as
non-table. Numeric grids, such as `an-7a2b17a3fb0f-p000200` and the 831443 pages,
still need the older rule/grid witnesses. The new dot tool is not their replacement.

The native rendering went through six cycles on fourteen table/control pages:

1. Short regular chains occurred in ordinary prose and falsely protected it.
2. Dot-ink purity above 0.7 did not resolve clipped-letter and accent chains.
3. Requiring compact, complete components on the lower body rail removed those
   control errors but rejected most real leaders on `63c4…p4`.
4. Inspection showed Paddle clipped the leader dots. Sampling expands by 0.7h
   horizontally and 0.6h vertically; the original box still owns the row extent.
5. A print-relative core threshold reduced back-page noise and recovered fifteen
   scattered native leader rows on that page.
6. Aligned seed groups can bridge at most 12h only when intervening localized
   row centers leave no gap exceeding 4h. Three seed rows remain necessary, and
   the region never extends above/below the witnessed seed range.

V6 visibly spans the complete `922e…p5` table; `4b80…p9` stops above the following
prose. `63c4…p4` remains split and incomplete: native protects 44/77 localizations,
R1 22/77 and R2 13/77. R1 differs from native on 22 items and R2 on 43 there.
R1 otherwise agrees with native protected indices across these fourteen pages;
R2 also differs on 200e p10 (five items) and 831443 p39 (four). These are
rendering comparisons, not table ground-truth scores. Sideways tables stay parked.

A late audit rendered native and both fast extents on all seven pages that wake
the new runtime guard, using the actual post-Q8 items. `4959…p5` falsifies the
apparent control success: straddling prose localizations inflate the height prior,
so small whole letters qualify as dots. V6 protects large prose regions and
blocks a real missing row. `0ce9…p1` also yields spurious table hypotheses over
back-page print. The new protection is conservative for deletion but incomplete
and overbroad for recovery; it is **not ready as a general table-boundary module**.

The follow-up diagnostic `table_dots7.py` renders filled dot interiors and
observed counters at every proposed dot, retaining rejected witnesses in red.
It lives outside the frozen runtime and is tested against all fourteen anchors
plus seven triggered pages. Its final inspection is recorded in the evidence
README. No uninspected table change is silently promoted to recovery.

V7 rejects many original prose fragments but does not solve the feature:
`4959…p5` still has 4/14/23 native/R1/R2 seed rows and 22/40/48 falsely protected
items. Reduction fills small counters and makes the interior test weaker.
`922e…p5` remains fully protected on all three routes (39 items), while
`63c4…p4` remains at 44/22/13. Native and reduced failure images were inspected;
this cycle was not promoted, and its cost is not presented as a runtime win.

B requested `s2-200e977f2dab5291c42c-p00035` as a conflict with engraving edges.
The old native/R1/R2 rule-grid renderings are in `cooperation-round4/`. They
protect 76/156/104 localized items, respectively, but visibly miss parts of the
table. Both tracks inspected this failure: long edges cannot certify image
ownership, and an incomplete table mask cannot certify the complement as image.

### Type grids, missed lines and the cheap check

`type_grid_edges.candidates` extends round 3's bracketed constant-phase slots.
V1 extrapolates one pitch past four consistently spaced rows. The native strips
on all 41 `ours_more` pages plus 40 agreement controls mostly expose blank margins;
only `4959…p5` has supported unowned edge ink. On `8686…p7` the extrapolation is
blank bottom margin, not the still-missed curled text.

V2 also renders uncertain interior intervals spanning two to four pitches where
the global phase residual exceeds 0.4h. It interpolates candidate positions,
not accepted lines. Actual current polygons own ink; separate quadrilateral
views give stable axes for many-vertex ribbons. Native body-contact witnesses
and independent ownership remain necessary. R1 renders reduced ridge fields
and sampled components; R2 only checks nominated strips. R1 and R2 share the
sampled slot test, so their equality is not independent confirmation.

All 195 pages now have native, R1 and R2 page images and 389 per-slot comparisons.
Eight slots are native-positive; both fast routes have nine, with three
disagreements. All ten slots positive on any route were visually inspected.
`31f40…p1` is back-page ink nominated only by reduced sampling; `dfcc…p1` is
back-page ink nominated only natively. `4959…p1` crosses an existing curved row,
so native rejection prevents accepting the fast nomination. `0ce9…p1`,
`6f045…p1` and `fb7364…p1` show real verso print, not missing front lines.
The reflected-glyph dependency vetoes the runnable ghost candidates.

The ornament on `an-7792a3301892-p000107` looks like a row of repeated bodies.
B's default motif scout returns negative here; it does **not** veto the candidate
or certify text. The regional detector declines it. This is an unresolved motif
failure, with the actual rejecting stage recorded.

`type_extended.recover` shares one block scout between old and new slots, checks
new positives against native pixels, then charges the B motif veto and table
extent dependency only when needed. It passes the same evidence to the guarded
round 3 regional recovery, with excluded footprints preserved through completion.
`type_extended.run` adds Q8 initially and after accepted additions. No row/font
census runs on the clean-page path. All final polygons retain `baseline: null`.

Final native-supported additions are `an-466cffad2cba-p000277` (ordinary text
beside an already separately localized large E) and `an-fd4fa0018ae1-p000035`
(first row with a large B). Raw/after inspection confirms the lines. The first
addition does not merge the separately owned initial; neither result proves an
ideal drop-cap reading-order representation. All fourteen round 3 additions
and all other old Q8+C output items are preserved exactly. There are sixteen
additions on fourteen pages, and no changes to agreement outputs.

### Composition, reuse and what is ready

The stable `type_context.recover(gray, current_items, detector,
excluded_regions=..., grid_items=..., lattice_evidence=...)` performs no initial
or final Q8. It preserves actual curved polygons for ownership, uses a distinct
quad view for pitch, and prevents B-rejected regions being reintroduced. The
old `type_recovery.run` defaults preserve round 3 behavior; its new options
allow the stack to pay shared separator work once. Precomputed evidence is tied
to the same current/grid pair and its generation cost belongs to the caller.

Stack independently snapshotted this adapter and verified its composed outputs.
Its A-before-C interaction recovers the genuine `4959…p5` row. I inspected that
raw crop and confirmed it ends before the central separator. Stack's fifteen
additions and reported 97 tests are **not** this experimental extension's sixteen
additions or this branch's test count. Stack intentionally excludes the new
extent guard and extended-grid module. No integration of the extension is claimed.

Reused B's stable motif/recurrence/pixel witnesses as import-renamed snapshots
with source and snapshot hashes in `reuse_round4.json`; all dependent work is
included in timings. Front/unknown are never recovery certification. Gave B
the native deduplicated component atlas and table-conflict images. Gave A the
false-clear height audit; A borrowed `type_barriers.protect` for native rule
checks around fragment joins. A's geometry scouts/joins are complementary and
were not silently introduced into the standalone C measurement.

Ready as explicit APIs: context/ownership composition, native glyph extraction
with alternate exemplars, physical row-band/mass-path rendering, and grid
nominations with the existing native ownership verifier. The extended correction
is a reproducible experimental option. General font identity, script-specific
guide counts, complete table boundaries and calibrated confidence remain open.

Next work should begin with original-pixel **component-to-row ownership** under
straddling localizations, since the same failure corrupts body size and dot
classification. Then distinguish joined-word contact paths from letter bodies,
and compare glyph constellations across book pages rather than assigning font
identity to one silhouette. Curved local grids need A's contact paths; one global
phase misses the remaining severe curl. Table extents must follow observed row
ends and rules without treating compact prose fragments as leader dots.

### Round 4 verification and measured receipts

Three fresh complete passes (585 page executions) recompute detector output,
Q8, scouting, every conditional dependency, regional inference and completion.
Every input detector polygon exactly reproduces the cached baseline and every
final output matches across passes. `round4-validation.json` records 29,549
schema, source, retained-item, agreement and repeat checks. The 69 prototype
tests cover the new no-Q8 adapter, many-vertex grid view, concave exclusions,
rejection before inference, row ambiguity, physical deduplication, old-gap
non-duplication and blank-page behavior, along with the existing prototype tests.

Times include all C runtime dependencies. Q8+C and full detector+Q8+C are separate
columns; decode, model startup and rendering are excluded from those columns.
OpenCV and ONNX use one thread; short foreground runs share the Mac with other
tracks. Repeats 2 and 3 had no competing feature census from this track. These
are observations, not held-out guarantees. All observed C correction costs fit
below one second, with agreement C medians below 1.5 ms and maxima below 3 ms.
The diagnostic atlas is much slower and remains outside this runtime path.

<!-- ROUND4 MEASURED TABLES -->

Milliseconds, raw per-page receipts in `round4-final-1c9641d65801/`.

| Cohort/repeat | n | C median / p95 / max | Q8+C median / p95 / max | Full median / max |
|---|---:|---|---|---|
| agreement r2 | 40 | 1.479 / 2.290 / 2.726 | 13.295 / 17.965 / 25.806 | 143.721 / 199.361 |
| new_discrepancy r2 | 101 | 2.709 / 197.980 / 333.807 | 17.100 / 210.443 / 359.359 | 154.727 / 500.827 |
| correction_pages r2 | 14 | 89.269 / 219.250 / 258.752 | 96.955 / 233.081 / 275.122 | 232.574 / 408.019 |
| all r2 | 195 | 2.000 / 143.743 / 505.121 | 14.601 / 159.926 / 532.897 | 148.421 / 680.308 |
| agreement r3 | 40 | 1.241 / 2.301 / 2.942 | 12.449 / 15.331 / 25.212 | 130.488 / 170.357 |
| new_discrepancy r3 | 101 | 2.534 / 199.145 / 325.623 | 16.697 / 211.823 / 352.581 | 148.813 / 491.429 |
| correction_pages r3 | 14 | 83.848 / 217.214 / 250.772 | 91.084 / 230.899 / 266.325 | 222.395 / 399.408 |
| all r3 | 195 | 1.972 / 131.082 / 492.865 | 14.387 / 142.845 / 519.670 | 146.280 / 665.941 |

The worst C page across all195 is `s2-0ce9d1025b3f23c7119e-p00001`: reflected-print rejection, not an accepted correction. The new discrepancy maximum is `s2-6f045b952f909b38d4db-p00001`, also a rejection. Paying ownership to reject a false wake is still charged.

On-demand census (median / maximum ms; all extraction included, image I/O excluded):

| Feature / route | n per repeat | repeat1 | repeat2 |
|---|---:|---|---|
| rows / slow | 5 | 250.253 / 318.616 | 241.112 / 338.140 |
| rows / explicit | 5 | 167.703 / 296.248 | 162.806 / 291.153 |
| rows / heuristic | 5 | 149.344 / 217.473 | 133.651 / 215.526 |
| table_extents / slow | 14 | 99.451 / 155.996 | 91.524 / 144.082 |
| table_extents / explicit | 14 | 67.167 / 118.965 | 62.615 / 106.999 |
| table_extents / heuristic | 14 | 40.207 / 67.502 | 38.751 / 61.528 |
| glyph_atlas / slow | 13 | 750.318 / 2115.734 | 788.624 / 2003.454 |
| glyph_atlas / explicit | 13 | 750.817 / 1968.749 | 777.689 / 1985.351 |
| glyph_atlas / heuristic | 13 | 746.127 / 1949.494 | 773.008 / 2033.231 |

The atlas charges fresh native extraction for both pages of each pairing (once for a within-page pairing). It is not a fast clean-page feature. The row census also remains outside the runtime. The numbers above measure v3 rows, v6 table extents and v3 atlas routes; the late v7 dot-interior diagnostic was not substituted into these timings.
