# Round 5 — curvature, skew, separation and segment shape

The public `Stack()(image_path)` now separates 270 more cross-column segments
on 40 pages and accepts 16 additional smooth envelopes on 9 pages. These are
operations, not 286 recovered lines. No new whole line is added or deleted by A.
The ruled-column comments with available raw pages are fixed; severe curved
starts/ends and smooth bands for every segment remain **PARTIAL**. Physical leaf
separation and pure-skew-only corrections remain diagnostic. The latency target
is not met across this cohort.

The [gallery](../../../.astra/fast_lines/out/round5/geometry/index.html),
[verbatim comment ledger](../../../.astra/fast_lines/out/round5/geometry/COMMENTS.md)
and [legends](../../../.astra/fast_lines/out/round5/geometry/README.md) are outside Git.
The scope is the authorized 195 pages plus five new curved pages, never the 44
held-out pages. Base is merged `0ffe28d`, branch `astra/ff-geometry`. This report
measures **R5 A with merged R4 B/C**, not the other tracks' unmerged R5 runtime.
The optional C column-evidence hook is installed for their later merge.

## What was rendered first

The owner's words remain the objectives:

> We want to recognize when there is curvature from books to correct the geometry of the line segments (very important contribution in the field of line segmentation in general if could be done efficiently, but no less important than not matching back page words, or images)

> We want to recognize skewness to fix the geometry for the same reason.

> We want to keep the separateness of lines of the same horizontal height but different column or page to be respected

> We should also be thinking about changing segment spaces and making them smooth, because many contain parts of other lines in, the less this is the case the better

I reused the active six-guide renderings on all 195 pages from R3
`out/features_geometry/explicit-v2`. I ran the model on just the five new curved
pages and rendered its full active guides, affine skew comparison and line ends
in `out/round5/geometry/new-model-guides`. No discounted lines are drawn. The
model follows substantial curl but also misses text and borrows geometry; its
line list is not a reference. The physical letters in the raster decide whether
a rendered path describes the feature.

For the new segment-shape requirement I built an explicit original-pixel body
contact and envelope rendering. It assigns native connected components to
competing row paths, exposes ambiguous ownership, and renders smooth top/bottom
hypotheses beside the original polygons. A component is not necessarily a glyph,
a path centre is not a baseline, and neither proves front-side ink. Long-row
records are available for 11,011 segments across all 200 pages. Short segments
under eight provisional body heights remain unmodelled by this new renderer;
“all pages rendered” does not mean “all segments solved.”

The first native renderings were inspected on 3229 p4, 8686 p7 and 4959 p4, then
expanded through the versions below. Every native page overview was subsequently
viewed in `native-review/sheet-00..33.jpg`. All 52 changed/control composed
pages were viewed in `composed-review/sheet-00..08.jpg`. All 29 broader-trial
shape crops and 23 endpoint-pair crops were inspected at raw/before/after scale.
This is not an exhaustive manual judgement of every glyph on 200 pages.

## Curl and smooth bands: prediction → rendering → correction

1. **V1: native body density should follow curl beyond the box.** It follows
   many real curved rows, but 8686 p7 source 66 switches to the next row at a word
   gap; another lower trace duplicates its neighbor. Density continuity alone
   is falsified as row identity. These images remain in `shapes-v1-slow`.
2. **V2: original map ancestry should constrain the native contact assignment.**
   Native components now supply extent while the exact original contour lineage
   supplies the observed row inside the map. A missing end is still only a
   tangent hypothesis. Global extreme padding makes an entire row too tall when
   one accent requires extra room. It does not satisfy the new shape goal.
3. **V3: local smooth shoulders should retain letters without widening the full
   row.** Quadratic envelopes around native component extrema, followed by mild
   smoothing, reduce the global padding. Competitors expose ambiguous shared
   contacts. Inspection found our diagnostic ancestry bug: C additions lacking
   `source_ids` were borrowing the current list index as an original source.
4. **V4: absence of ancestry must stay absent.** Added items use their own
   polygon centre or supplied centreline; they never borrow an original title
   by position. Connected endpoint growth stops at a gap larger than 1.5 body
   heights. The contact path is independent of a guessed semantic baseline.
   A native glyph’s explicit contact can explain why another oversized old box
   also overlaps it. This does not certify an unseen fragment as front text.
5. **V5: distinguish off-row body tips from unassigned current marks.** Raw
   8686 p7 guard crops for records 2, 13, 66, 68 and 74 show both neighboring
   descenders and genuine marks in the old rectangle's lost-ink strip. A whole
   component centred over one height away may account for a neighboring body
   tip; small unassigned accents remain protected. The exemption uses exact
   component-label pixels, not its bounding rectangle. A rectangle exemption
   could erase unrelated marks inside the same bounds and was removed.

Candidate envelopes have local margins; a nearby unexplained mark can enlarge
its own shoulder. A loss beyond half a height still rejects the replacement.
The final guard rejects ambiguous contacts, new retained-neighbor ink, removed
B footprints, unresolved regional printed rules, reused split ancestry and
`initial_completed` rows. It skips shape construction for rows already bounded
by an accepted column certificate, while retaining their paths as competitors.
The cheaper sparse geometry scout is reused; no duplicate page scout is run.

The conservative correction cycles accepted 3, then 5, then 10 changes on the
16-page curl study. The broader trial proposed 29 changes; native-label and
regional-boundary guards leave 16 in the public stack. Four occur on
`s2-86865c33eef5932c013b-p00007`: two curved body rows and two heading/page-label
shapes. Most severe right-edge characters remain unrecovered. Changes on
`an-d83e7a198ade-p000099` tighten two existing apparatus bands but do not recover
the missing apparatus row. Other accepted pages are `an-d3237d690aa0-p000138`,
`an-466cffad2cba-p000277`, `an-7792a3301892-p000138`,
`an-9ea1564fcf4f-p000202`, `an-c8b96a901917-p000036`,
`an-dbd045ccd84c-p000359`, and `s2-6f045b952f909b38d4db-p00001`.
These include titles and may retain existing non-text content; geometry is not
an ink-ownership classifier. C's completed large E will be protected by its
metadata after merge; that merge is not included in these measurements.

The new five pages receive no extra accepted R5 band or endpoint correction.
Their R4 mechanisms still produce the previously inspected curved joins/shapes
on 3229 p5/p8. Many 3229 p4/p6 and 4959 p1/p4/p5 ends remain unchanged. The
owner's broad shape goal is therefore not achieved by this narrow accepted set.

### Both fast routes against the native rendering

**Route 1** keeps the same native components and original map ancestry but omits
slow unused density/tracing work when constructing the envelope. All 11,011
polygon/contact/ambiguity comparisons are exact. The slow route additionally
records raw contact-trace observability; that field is not claimed identical.
`routes-v5/<page>.json` keeps the line-level comparison and complete route records;
R1 blue is drawn over the native green envelope on every page.

**Route 2** reduces the body proxy to 12 pixels before measuring components, then
uses the same geometric construction. Per-line maximum top/bottom differences
have median 0.1577764, p95 0.5012677 and maximum 1.3700154 body heights. The maximum
is 3229 p6 record 27. Full overlays on that page and 8686 p25 show shifted extents,
lost fine contacts and different treatment of shadow/verso. These are geometric
comparison distances, not segmentation accuracy. R2 is not promoted.

A separate contact-owned endpoint-pair study yielded 23 pairs on nine pages.
Real-looking joins on 8686 p5, 3229 p5 and 4959 p4 coexist with dictionary pairs
across rules and verso fragments on 31f40 p1/6f045 p1. All were inspected. Native
contact identity alone is insufficient; **none of these new joins is promoted**.
The existing R4 fragment operator stays enabled.

A final code review found a sequential-retention issue: two changing neighbors
could each borrow coverage from the other's pre-change rectangle. Retention and
neighbor checks now use the current output after each replacement. The native
ownership census stays fixed. A regression test checks that a later replacement
sees the already replaced polygon. Pre-fix receipts are preserved separately;
the final fresh runs include this fix.

## Respecting columns and page separation

The old Q8 rule check and R3 curved-rule check remain enabled. Owner images show
that their multi-crossing nomination and conservative glyph-junction veto miss
solitary first/last rows and many close typeset columns. A dark vertical stroke
alone remains insufficient: 93f807 p1 contains a back-page rule crossing prose.

**V1 prediction:** bilateral terminations of independently separated long rows
should establish front layout around a native verified rule. The rendering
marks the actual left/right endpoints and sustained rule, rather than reporting
a vote. This fixes isolated crosses but misses 661 p5/p10 and a0e233 p2 where
most original boxes span the divider.

**V2 prediction:** native horizontal strokes through the rule distinguish
letters crossing a verso stroke from print stopping at its sides. A native
remapped strip explicitly renders each through-run. No-through-stroke alone
wrongly accepts nine cuts on 93f807 p1; this falsifies it as an ownership proof.

**V3:** retain either extended bilateral termination runs, or the clear native
strip plus an independent co-level termination pair. Only B-surviving original
sources may provide positive endpoints; all original crossing sources remain
available to the scout. Grid intersections still veto. Wider drift nominations
are allowed in letter heights, with the same original-pixel rule verifier.
This resolves 7247 p1 and d12a p6 drift that the narrow nomination missed.

**V4:** all 41 changed-page V3 overviews exposed a running-title cut on
b9d6 p255 and prose below the list on 4b80 p9. Restrict cuts to row centres inside
the *observed* native rule extent. Deduplicate coincident rule nominees, which
otherwise produce a tiny sliver on a0e233 p2. This reduces 273 cuts/41 pages to
270 cuts/40 pages. The revised control images preserve those headings/prose;
93f807's verso rule remains rejected. There is no page-name dispatch.

**Route 1** vectorizes the native through-run computation. All 52 verified
corridor records exactly match the slow per-row rendering. **Route 2** uses only
the extended endpoint witness; it misses seven accepted corridor records on six
pages: 922e p5, 661 p5/p10, a73d p141/p231 and a0e233 p2 (two nominees). Both
routes are drawn against each explicit rule in `routes-v5/*.columns.jpg`.

The accepted module corrects the available owner-commented column crossings on
60f24 p4; 661 p4/p5/p10; c0b02 p5/p7/p10; d12a p6; 74cdb p2/p3/p6/p7/p12;
7247 p1; a0e233 p2; and 4959 p4/p5. Those fixes do not solve the missed rows or
curl also mentioned on the same pages. The raw inputs for 44b5 p1/p2/p3 are not
in the supplied 200-page cohort. Their numbered review images were inspected;
no new output or “fixed” claim is made for them.

### Vector versus raster conservation

Each cut shares one boundary; no vector gap is erased. The first artifact audit
incorrectly required identical integer raster masks and failed on c8b96 p68.
Independent clipping creates new floating vertices; rounding each polygon changes
Bresenham edge placement even when its vector union is unchanged. Across all 270
cuts, maximum vector symmetric-difference area is 1.2369e-9 square pixels.
Integer mask differences total **84,633 pixels**, including **9,231 pixels with
grey value below 200**. All missing raster cells are within one cell of the new
boundary. Largest affected raw strips on 74cdb p3 and d12a p6 were inspected.
The exact per-cut ledger is `final/column-conservation.json`; no raster-perfect
retention claim is made. The grey<200 diagnostic is not an acceptance gate.

### Physical page leaves and skew

Printed columns are not physical page leaves. The prior native seam/flank
renderings, both fast routes, table-border counterexample on 7a2b p200 and real
fold uncertainties on c99 p71/9ea p202 remain in the R4 gallery. This round does
not add a physical leaf certificate. In particular, the unruled two-page
separation objective remains incomplete.

Independent native pure-skew validation from R4 is reused, including its six
known ±2-degree rotations and per-line residual ledger. The new five model
skew renderings distinguish affine fit from curl but are not new independent
native-skew validation. No new pure-skew-only correction is claimed, and the
named 44b5 p5 raw anchor remains unavailable. Orientation stays parked.

## Runtime, dependency reuse and timing

The public sequence is Q8 once, B, ancestry-aware A geometry and curved rules,
new column evidence/cuts, old guarded fragment joins, C, then the guarded native
smooth envelope. The new certificate is passed as `column_evidence` when C's
API supports it. All source IDs survive clipping; deleted sources cannot supply
positive endpoint or retention evidence. No track's runtime is copied.

`geometry_context` now returns the DB bands already measured; the final smoother
reuses them. `geometry_contacts.prepare` can return native labels without an
unused density field. Defaults are preserved. Direct least-squares tangent
arithmetic replaces repeated general polynomial fits only in the fast native
fragment route. Every sample and alternative is checked against the prior
calculation: **71 traced records, 12,386 samples and 77 alternatives are exact**
across the authorized cohort. This helps cost but does not remove its full-page
native-density dependency.

Final timing table is generated from the two fresh public entry-point runs below.
Every dependency is charged in full correction time; new-A time is the measured
column-plus-envelope stage, reusing the charged earlier scout/map. It is not a
subtraction of unrelated historical timings. Image export is excluded. ONNX is
warm and CPU threads are limited; the shared Mac is not an isolated benchmark.

Milliseconds, repeat 1 / repeat 2:

| Measured cohort and stage | Median | p95 | Maximum |
|---|---:|---:|---:|
| Agreement: new A | 0.168 / 0.168 | 0.596 / 0.325 | 43.747 / 41.104 |
| Agreement: complete corrections | 19.896 / 18.648 | 48.702 / 42.735 | 99.172 / 96.756 |
| Discrepancy: new A | 4.299 / 4.347 | 177.661 / 170.214 | 244.154 / 229.938 |
| Discrepancy: complete corrections | 54.864 / 46.379 | 500.009 / 453.533 | 1037.450 / 1058.015 |
| All 200: new A | 0.253 / 0.259 | 167.898 / 166.232 | 289.803 / 334.762 |
| All 200: complete corrections | 38.607 / 37.209 | 468.120 / 401.715 | 1128.106 / 1147.866 |
| New five: complete corrections | 28.870 / 28.463 | 345.537 / 339.276 | 351.767 / 346.347 |

The discrepancy group here has 101 pages (80 main plus 21 extra). The 54 development pages are also included in the all-200 row; 4959 p1 is a development page, which explains why the overall maximum exceeds the discrepancy maximum. Per-page receipt times, including decode and Paddle, are retained rather than hidden by this grouping.

s2-49598b2e848ab1f0ee1e-p00001: complete correction 1128.106 / 1147.866 ms; native fragments 401.966 / 407.863 ms; final envelopes 158.394 / 156.708 ms.

s2-49598b2e848ab1f0ee1e-p00004: complete correction 1037.450 / 1058.015 ms; native fragments 495.229 / 504.507 ms; final envelopes 141.788 / 141.125 ms.


The clean-page median new overhead is small, but the 3229 p2 band attempt adds
a material tail despite leaving its R4b output unchanged. The inherited native
fragment tail on dbd045 p249 also remains. 4959 p1/p4 combine expensive fragment,
type and final-envelope work and exceed one second. No tuning or abstention
threshold was weakened to fit a latency budget. All five new curved pages also
have raw per-page receipts. No performance guarantee for unseen pages follows.

## Verification, handoff and remaining work

- The code is exercised through the actual public Stack, with fresh decode,
  Paddle inference/postprocessing and all dependencies, not a cached comparison
  pipeline. The finalized per-page polygon lists are compared with the reviewed
  pilot and with a reverse-order fresh repeat.
- All 40 agreement outputs are unchanged from R4b. The 47 changed pages are
  inspected; five new curved controls make 52 composed overview pages. All
  308 Q8 cuts, 92 curved cuts, 61 back-page removals and 11 old ornament removals
  are retained in the stage ledger. Across 200 pages the existing mechanisms
  supply 32 geometries, 18 join groups (19 fewer items), and 20 C additions.
  These include the five new pages and are not all R5 achievements.
- **158/158 prototype tests pass.** The export audit passes **75,710 checks** on 200 exports and 400 fresh receipts, including schema, bounds,
  source IDs, display-number mapping, native retention, vector partition and
  bounded raster differences. Every comparison remains page/line addressable;
  there is no single accuracy score or assumed ground-truth detector.
- New reusable modules are `shared/geometry_columns.py` (`analyze`, `apply`) and
  `shared/geometry_envelopes.py` (`guided`, `correct`, diagnostic `endpoint_pairs`).
  The former is a conditional ruled-column module; the latter is a conservative
  prototype with substantial coverage limits, not a universal segment shaper.

B's guidance prevented glyph or darkness evidence from certifying a rule; native
contacts never serve as front-text ownership. Its accepted removal footprints
remain permanent exclusions. C requested a candidate boundary API, and
`geometry_columns.apply(items, evidence)` is exposed before C's per-piece body
support check through the existing stack hook. C confirmed its initial completion
must retain its tall shoulder; `initial_completed` is skipped by the smoother.
No runtime height is borrowed from C's known false-clear height census. The
existing regional type/rule barrier logic is reused as a veto, not a complete
semantic table boundary. R5 B/C counts and timings reported by relay are not
folded into this branch's measurements; final merged validation is still needed.

Next work must address these observed failures, not lower guards to increase a
page score: local native contact fields with a mathematically adequate halo to
remove full-page fragment cost; explicit competing-row and accent ownership on
8686/3229 ends; front/back certification for otherwise plausible endpoint pairs;
post-C candidate shaping with the actual merged additions; paired page outlines
and paper-surface continuity against framed-table controls; and short-row native
skew validation. No new physical-leaf model, reliable local font-height census,
or complete all-segment smoothness solution was finished here.

Git staging was blocked with `Operation not permitted` at the common repository's
`.git/worktrees/greek-ocr-toolkit-fl-geometry/index.lock`. No commit or push was
created. The authorized fallback is `.astra/commit-Fgeometry-r5.sh`, with a
validated scoped patch and per-file hash receipt. It includes the exact requested
co-author/session trailers. Outputs remain outside Git.

The final numbered images place labels after resizing and use verified native
column evidence before geometric XY sorting, so touching column envelopes no
longer interleave their display numbers. Detector list order and polygons are
unchanged. The last source edits after timing were confined to export/audit code,
tests and missing-baseline failure handling; `final/handoff.json` verifies every
measured runtime source hash. No correction code changed after the final runs.
