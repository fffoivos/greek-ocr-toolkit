# Track A: page geometry, rounds 3 and 4

Round 4 adds an original-pixel contact rendering and a guarded correction for
15 fragmented line groups on seven pages, including three on the severe right
edge of `s2-86865c33eef5932c013b-p00007`. A mathematically equivalent faster
geometry scout is available and was adopted by the separate stack track.
Physical page-leaf separation remains diagnostic; pure-skew now has independent
pixel/rotation validation but no new correction claim. The result is PARTIAL.

Latest owner artifacts: [round-4 gallery](../../../.astra/fast_lines/out/features_geometry/round4/index.html),
[legend and limits](../../../.astra/fast_lines/out/features_geometry/round4/README.md),
[raw summary](../../../.astra/fast_lines/out/features_geometry/round4/summary.json).
The detailed round-4 continuation follows the preserved round-3 account below.

## Round 3 result

Curvature, skew and separation now have explicit page renderings and both fast
routes on all 195 supplied pages. The conditional prototype changes 30 existing
line geometries on 11 pages and makes 92 additional cuts along three curved
column rules. All 308 round-2 separator cuts remain exactly unchanged. This is a
partial result: severely fragmented curl, physical page-leaf separation and
semantic baseline recovery are still unresolved.

The final review index is
[`features_geometry/index.html`](../../../.astra/fast_lines/out/features_geometry/index.html).
The output [README](../../../.astra/fast_lines/out/features_geometry/README.md)
explains the colors and versions. Code is under
[`features_geometry/`](../../../prototypes/fast_lines/features_geometry/README.md)
and new `shared/geometry_feature_*.py` modules only. The production page API and
its tests were not edited. No PDF text layer or held-out page was used.

## Scope and evidence

The existing Q8 manifest supplies exactly 54 development, 40 agreement, 80
discrepancy and 21 `discrepancy_extra` pages. The named skew anchor
`s2-44b5cf9e0d680b361091-p00005` is absent from both supplied PNG directories and
the manifest; it was not searched for elsewhere. Orientation remains parked on
the existing designated page. No thresholds, branches or geometric constants
depend on page names. Pixel quantization is the only absolute length floor.

Cached active guide arrays from the existing deterministic model are reused with
source and image hashes. The explicit renderer retains all six rails in V1;
V2 emphasizes baseline, meanline and their displacement from a central tangent.
Discounted lines are omitted everywhere. The references are observations, not
labels: some stamp curves, Arabic fragments, long borrowed guides and interpolated
ditto/table rows are plainly wrong. On `s2-831443dc5e6f1ccfbaf5-p00007` and p42 the
cached active output contains 10,453 and 10,061 fragments respectively; these are
not counts of real printed lines.

All 195 explicit curvature overview pages were inspected. Detailed raw/after
crops were inspected for all 30 proposed final geometry changes and all 92 final
extra separator cuts, including the earlier proposals rejected below. Both routes
were compared to visible model/raw features on the named curl, separation,
apparatus and straight control examples across successive versions. Every one
of the 13,639 small-detector source items has a JSON comparison record on both
routes, including absent/ambiguous cases. Overlapping model candidates retain
their IDs, offsets, shape residuals and slope differences; they are explicitly
**unadjudicated**, not converted into true/false labels. This is not an exhaustive
human adjudication of all 13,639 lines or every diagnostic image. No aggregate
accuracy score is claimed.

## “We want to recognize when there is curvature from books to correct the geometry of the line segments”

The physical observation is a row bending away from its central direction as it
approaches the binding. A tall bounding rectangle is a consequence, not a useful
normalizing font height. An apparent bend can also arise from accents, an
ornament, a switch to a neighboring row or a merged pair of columns.

**Explicit rendering.** `reference.py` samples the six model guides at a fraction
of their measured body height. V1's six colored paths were too busy on
`s2-3229200bf47ca465a42d-p00004`. V2 draws the baseline and meanline separately,
fits an affine tangent to the middle half, and draws orange residual ticks.
This makes the left curl on p4/p6 and right curl on
`s2-86865c33eef5932c013b-p00005`/p7 visible. The apparatus on
`an-d83e7a198ade-p000099` also shows why one page-wide font scale is inadequate.
The model sometimes extrapolates guides through empty space, bows around stamp
ink, and interpolates across distinct short numeric entries; those renderings
remain failures, not reference truth.

**Route 1.** Threshold the already computed DB map, retain connected-band support,
and render its probability-weighted centre along x, with an unclipped native
contour envelope. The first version assigned a band by a quad's centre and
occasionally chose the neighboring row. V2 reconstructs the exact contour-to-quad
genealogy using the pinned postprocessor, including its score, expansion and
rounding. V4 removes an obsolete centre-probe prerequisite: exact ancestry does
not require ink at the centre of a tall curved quad. Shared components and
multiple ridges are explicitly ambiguous. The map centre is not a baseline.

**Route 2.** Sample 19 columns and 31 vertical offsets around each sufficiently
long quad. Independent maxima in V1 visibly jumped rows on 3229 p4. V2 walks
outward from the central ridge with bounded movement; end curvature needs three
consecutive supported samples of consistent sign. V3 measures central DB-band
thickness rather than the inflated box proxy. This removes feedback in which
more curl enlarges the normalizer and makes the normalized bend smaller. Short
tilted neighboring fragments may wake the page but never authorize a join.
The sampled route still misses some end curvature; after a page wakes, the dense
map route can nominate additional well-supported bends. It does not search
outside existing map bands.

**Correction iterations.** Unguarded native replacement on nine early anchors
made 21 changes but uncovered entire neighboring rows on 3229 p6 and marks on
d83e. A zero-unique-ink-loss guard reduced those proposals to four geometries on
3229 p4. The next version permits envelope growth only for originally covered
ink within half a provisional body height of the native contour; farther losses
remain topology uncertainty. It then rechecks exact preservation. Each sequential
proposal sees the current neighbors, preventing two adjacent replacements from
each relying on the other's obsolete coverage. The guard measures local contrast
against surrounding paper; it does not establish ink ownership or readability.

Final examples: five ribbons on 3229 p4, one on p6, and one on the agreement p2
now follow the visible left bend. Six newspaper ribbons on
`s2-49598b2e848ab1f0ee1e-p00001` and five on p5 retain their original marks while
reducing rectangular overlap. One d83e apparatus band improves its envelope but
still spans two columns. All 30 final geometry changes preserve every uniquely
covered pixel at the guard's stated contrast threshold. Fainter unmeasured ink,
ideal glyph ownership and ideal envelopes are not certified by that invariant.

**Still wrong.** Neither 8686 p5 nor p7 receives a geometry repair: their curled
ends remain split/truncated, and some lines are absent altogether. The dense map
cannot infer text absent from the map. Whole-row-loss candidates on 3229 are
preserved rather than hidden by generous padding. Across the cohort 34 proposals
abstain because lost ink is not a nearby mark; 17 give separator corridors
priority; six lack dense corroboration. Those are decisions, not error counts.

## “We want to recognize skewness to fix the geometry for the same reason”

The renderer distinguishes the affine central slope from the non-affine end
residual. V2 `*.skew.jpg` draws the observed centre, its straight fit and signed
angle on the original page. The route-1 band and route-2 ridge each provide the
same decomposition, independently of the old-model slope. Comparing end
displacement in local height units avoids treating a small angle on a long line
as harmless merely because its angle is small.

The same successive failures apply here: choosing a neighboring band yields the
wrong slope; independent sparse peaks create false tilt; a tall curved box
inflates normalized displacement. Exact lineage, continuous sampling and local
band thickness address these mechanisms. Straight clean controls, including the
77d1 signatures that the stopped field experiment damaged, are preserved. A
known affine synthetic line has zero bend, while a known curled line retains
its central affine slope; both invariants pass.

The runtime can replace a wrongly tilted quad only when the dense path
corroborates it and the original-ink guard passes. The 30 envelope changes are
not counted again as 30 skew fixes: slope and curvature coexist, and many small
detector quads already have the correct slope. There is no separate verified
real-page pure-skew success count. The specifically requested skew page was
missing, so that anchor could not be checked. This does not rotate pages or
unpark orientation. Broadening skew correction to short, capital-heavy or
multirow boxes would require better body-contact evidence first.

## “We want to keep the separateness of lines of the same horizontal height but different column or page to be respected”

**Explicit whitespace and rules.** V1 scans original pixels in overlapping
12-height vertical bands for persistent low-ink corridors with ink on both
sides. It falsely treats border-adjacent margins as gutters. V2 requires
character-scale connected support on both sides. This removes many margin
candidates but also loses genuine fold-adjacent whitespace on
`an-c99f1c450f55-p000071`, where the dark fold interrupts the bilateral observation.
Q8's dense rule hypotheses are drawn separately in orange. They include back
rules and table rulings and are not separator labels.

**The two fast routes.** Route 1 renders the same corridor feature on a reduced
pixel image, charging resizing and component extraction. Route 2 renders repeated
gaps between simultaneous detector endpoints, in local height units. Both can
confuse verse indentation with columns. Route 2 cannot discover a gutter when
every detector box crosses it. Neither whitespace route authorizes cuts.
The physical two-leaf model remains unfinished; the c99 spread is unchanged.

**Curved printed rules.** Q8 remains enabled. Its dense-rule-to-fast-verifier
workflow is reused, including grid protection and clear flanks. The stopped
`a003886` smooth-rule verifier was brought into a new owned module and rendered
before use. It follows a sustained original-pixel stroke, tests support over
moving local intervals and constrains path slope. It initially recovered cuts
on 661d p5/p9, 4959 p5 and d12a p8 that the straight verifier refused.

The V4 raw crop of `s2-93f8070059f938bda524-p00001`, source32, falsified local
acceptance: a **back-page rule** split a normal sentence at a convenient word
gap. Other crossings along that same rule join printed words. The new explicit
whole-rule crossing renderer checks the connected stroke at every crossing and
vetoes the entire extra rule when any glyph junction makes ownership uncertain.
It does not infer front ownership from darkness or a majority vote.

A synthetic full-width crossing then exposed a second failure: estimating white
inside a narrow dark strip can erase the crossing. V2 obtains white from the
surrounding two-height patch. The synthetic crossing now rejects; isolated-rule
controls pass. This also removes a spurious junction on 661d p9. The final
prototype rejects the 93f807 rule at all seven inspected crossings. Two tight
joins on d12a p8 remain uncertain, so its five tempting cuts are not shipped.

Final additional cuts are **55 on 661d p5, 21 on 661d p9 and 16 on 4959 p5**.
All 92 corresponding raw/after crops were inspected. These cuts separate
columns; multirow boxes within a column may remain multirow. The narrow rule
stripe may be removed, shown red, while surrounding letters are retained. An
absence of observed junctions is still not a general front-rule certificate.
The original 308 Q8 cuts are unchanged, including its existing table guards.

## Timing and raw counts

Fresh single-thread runs decode each page, run the pinned ONNX small detector and
quad postprocessor, then run the complete Q8+A correction. No cached probability
map, model guide or C census enters the timed path. An independent Q8-only call
alternates before/after Q8+A; added A time is their paired difference. This
includes both scouts, contour reconstruction, ink preservation, separator
verification and splitting. Serialization/review rendering is excluded. The Mac
was shared with the other tracks, so these are observations, not latency guarantees.

Repeat 1 covers all 195 pages; repeat 2 covers the 40 agreement and 80 discrepancy
pages. All **315/315 fresh baseline polygon lists and 315/315 final polygon lists**
exactly match the saved study. Sources stayed frozen within each run. Raw page
receipts and environment/source/model hashes are in
[`benchmark-v6/`](../../../.astra/fast_lines/out/features_geometry/benchmark-v6/).
Numbers below are milliseconds, **median / p95 / maximum**; rows are not pooled.

| Group and repeat | Added A above Q8 | Q8 alone | Q8+A correction | Decode + detector + Q8+A |
|---|---:|---:|---:|---:|
| Agreement 40, R1 | 8.398 / 13.458 / 27.923 | 11.505 / 15.187 / 23.826 | 19.764 / 28.027 / 36.161 | 173.156 / 214.227 / 259.644 |
| Agreement 40, R2 | 8.206 / 13.062 / 25.867 | 10.950 / 13.345 / 23.204 | 19.317 / 28.013 / 33.116 | 166.441 / 189.935 / 227.051 |
| Discrepancy 80, R1 | 8.431 / 90.031 / 122.672 | 12.209 / 29.462 / 41.039 | 23.059 / 117.166 / 139.402 | 178.518 / 339.158 / 411.438 |
| Discrepancy 80, R2 | 8.535 / 71.790 / 122.809 | 11.712 / 29.531 / 40.745 | 21.785 / 97.868 / 138.895 | 171.402 / 322.555 / 444.742 |

The extra 21 discrepancy pages were measured once, not repeated: Q8+A
24.016 / 48.747 / 132.401ms, full warm stack174.292 / 308.209 / 318.131ms.
Session construction was23.397ms and18.212ms, recorded separately from warm page
latency. The `detector/` exports include decode, inference, postprocessing and
Q8+A in `seconds`, with separate components and the repeat-1 receipt path.

The largest repeated discrepancy correction is4959 p5 (139.402 / 138.895ms).
The largest full discrepancy latency is d12a p8 (411.438 / 444.742ms). The largest
agreement correction is the changed3229 p2 (36.161 / 33.116ms).
Thus the **sub-one-second correction target passes on the measured cohort**.
The **negligible-overhead target does not**: adding8.2–8.4ms median is substantial
beside Q8's roughly11ms. Most new cost is the per-line sparse geometry scout;
the next speed work should preserve its explicit witness while reducing this
cost, then repeat the same per-page decisions and fresh timing. No held-out
performance or accuracy claim follows from these numbers.

| Supplied group | Pages | Original items | Geometry changes | Q8 cuts | Extra curved cuts |
|---|---:|---:|---:|---:|---:|
| Development | 54 | 5,054 | 13 | 43 | 21 |
| Agreement | 40 | 1,662 | 1 | 0 | 0 |
| Discrepancy | 80 | 5,318 | 14 | 260 | 71 |
| Discrepancy extra | 21 | 1,605 | 2 | 5 | 0 |

There are 14,039 final items: 13,639 originals plus 400 separator pieces net.
No new missing text is discovered, no original source item is deleted, and no
false-positive line is suppressed. Thirty pages change. The geometry scout wakes
on 26/195 pages: 10 development, one agreement, 12 discrepancy, three extra.
The agreement label is detector agreement, not proof that geometry is correct;
the one changed agreement ribbon visibly curves on 3229 p2.

## Cooperation and reusable modules

Consumed C's apparatus font rendering and snapshotted
`type_profiles.measure_line(samples=24, version=3)` offline for all 30 changed
source boxes. Seven contact measurements are uncertain. The apparatus example
gives contact height16.3px, DB band18.5px and box proxy26px, making the distinct
scales explicit. On 3229 p4, source24 reports40.4px with `uncertain=False` while
adjacent same-type rows report21–23px; this remaining false certainty was sent
back to C with the raw crops. No C census or borrowed height is hidden in runtime.
The source hash, snapshot and all measurements are in `cooperation/body-scale.json`.

B's independently rendered same-pitch front/back layers rule out a majority-pitch
ownership shortcut. Direct relay confirmed that its glyph handedness cannot
certify rule ownership. C independently encountered separator-crossing recovery
failures; these support an ownership abstention rather than a relaxed cut.
No B/C line removals or recoveries are silently included in A's counts.

Published for the other tracks: exact DB contour ancestry and band paths;
continuous sparse geometry scouts; original-ink conservation with bounded mark
completion; curved-rule paths and whole-rule crossing uncertainty. Interfaces
and paths are in the prototype README and shared board. These are conditional
prototype modules, not promoted production APIs. The whitespace routes and
physical page model are not ready to become correction modules.

## Verification and next work

57/57 prototype tests pass, including 14 new feature/conservation tests.
2,955/2,955 artifact checks pass: 2,145 final image files, every-page source and
line accounting, finite/clipped detector coordinates, unchanged parked output,
30 geometry-conservation checks, and exact Q8 retention on194 unparked pages.
Fresh-export equality and repeated timing are recorded separately above.
No tests under `greekocr/pages/` were changed or substituted for visual review.

At the round-3 handoff, staging was blocked on the worktree index and a validated
patch/script was supplied. The coordinator subsequently committed that work as
`ef1a044` on `astra/ff-geometry` and merged the three tracks. Round 4 starts from
that committed state; the old handoff patch is historical evidence.

Next component work should render body contacts along severely curled fragments,
including accents and neighboring-row alternatives, then test a shared sheet
field against those contacts. The field must not borrow a row solely because
pitch agrees. Physical leaf separation needs a model that distinguishes a dark
fold from a printed/back rule and explains truncated page edges. Tight rule/letter
junctions need better local ownership evidence before the conservative d12a
abstention can be relaxed. Short pure-skew cases and the missing skew anchor need
direct raw-page verification. Finally, the remaining line ledger needs explicit
human adjudication; its counts must never be advertised as accuracy.

## Round 4: original ink along severely curled fragments

The old guide rendering was least convincing exactly where the owner's emphasis
lies: a line rises sharply at a book edge and the small detector emits several
fragments. This round first renders the original pixels. No reference guide,
model line count or corpus disagreement label decides the path or the correction.
The same 195-page allowlist is used; no new evaluation page is introduced.

### Explicit rendering and its failed iterations

`shared/geometry_contacts.py` estimates surrounding paper with a four-height
box filter, extracts ink at 0.08 contrast and renders connected components at a
body-sized scale. Its height/width/area filters use the detector-derived height
proxy, not a claimed font height. The component inventory, density field,
observed path samples, independent end traces and their disagreements remain
available in JSON. A component can still be an ornament, back-page ink or part
of a rule. A path is an ink-support centre, **not a baseline**.

The renderer was developed through seven versions, with raw crops inspected
between changes:

1. A maximum-density dynamic path from the main box centre followed a stronger
   neighboring row on the severe 8686 pages. More accumulated ink was not proof
   of row identity.
2. Restricting the middle span to its central prior helped, but the path still
   changed rows at curled ends. That did not justify accepting the tail.
3. Nearest local ridge following, with a short measured tangent history, stopped
   rewarding distant stronger rows. After three body heights without support,
   observation stops; the missing segment is not painted as observed ink.
4. Independent tracing from the main span and each existing fragment exposed
   competing row assignments. A shared observed span of at least four heights
   and p90 separation below 0.35 height is required. All original possible owners
   remain in the evidence, including ones removed by another operator.
5. A box centre could itself fall in interline paper. Seeding from a measured
   central body peak and a localized fragment peak fixed the section-sign gap
   on `s2-86865c33eef5932c013b-p00007`, sources 2 and 3. It did not fix source10+11:
   their measured p90 difference is 0.375 height, so they remain unjoined.
6. Faster **native-pixel** separable filtering replaced the slow Gaussian and
   the obsolete dynamic-path calculation was skipped. The ten-pixel-height
   reduced renderer was rejected: it changed source2's decision, reversed
   source10's disagreement and lost source70 on the same page. Native versus
   reduced paths could differ by 3.125 heights. A visually plausible small image
   was not equivalent evidence.
7. Ambiguous owners are rendered rather than omitted. An untraced competing
   original owner also prevents a correction; another track's removal cannot
   manufacture certainty by deleting the alternative.

Final slow renderings are `round4/body-slow-v7/`: one overview, machine-readable
component/path evidence and grouped raw/after long-line crops per page. All 195
overviews and all 69 proposed main/fragment crops were viewed. This is not manual
adjudication of all 9,086 paths. The [review record](../../../.astra/fast_lines/out/features_geometry/round4/review/notes.md)
names coverage and failures. Discounted model lines are never drawn.

### The two fast routes, checked against that rendering

Route 1 (`body-explicit_fast-v7/`) evaluates native ink with equivalent finite
Gaussian kernels through OpenCV's separable filter. It retains the components
and observed-ridge definition. Across 195 pages, all component inventories match;
9,086 line paths are compared individually. Thirteen have a one-sample maximum
vertical difference of 0.0625 height, with p90 difference zero. Every observed
span and all 69 independent fragment-agreement decisions match. The thirteen
page/line identities and every comparison image are in `contact-audit/`.
Floating-point ties are reported, not rounded into an “exact paths” claim.

Route 2 (`geometry_fragments.candidates` plus `hermite`) uses only box length,
end proximity and endpoint tangents to nominate a possible curled continuation.
It is inexpensive, but often wrong: on 8686 p5 source9+8 it points to a different
row, whereas source9+10 is the real continuation. On `an-7792a3301892-p000138`
it links different numbered rows. On `an-dbd045ccd84c-p000249`,
`an-ef481610a820-p000115` and p181 it points into a stamp. Its purple path is drawn
against the slow green observations, and p90 differences are stored per pair.
It serves only as a scout for native rendering; a tangent match never authorizes
geometry on its own. Both routes and every rejection are visible page by page.

The underlying slow field can also trace back-page ink on 8686 p26. Native ink
continuity is not front-side ownership. Track B's removal context and optional
forbidden regions must remain separate evidence when composing a larger stack.

### Corrections, envelope iterations and remaining curl failures

`geometry_fragment_correct.run` accepts original items plus current items with
stable original `source_ids`. Only retained, unsplit single-source items can be
joined. It uses two-ended contact agreement, a contact inside the candidate
fragment, competing-owner checks, a body bridge and an envelope that must contain
**every rasterized pixel of every participating old polygon**. Extra envelope
area must not take ink already owned by another retained item or enter a caller's
forbidden region. This preserves prior ink and Q8 separation, but it cannot prove
that previously unowned ink is front text.

Envelope V1 preserved the old polygons but pinched their connecting corners;
a blanket pixel pad also caused needless neighbor collisions. V2 uses the
measured body ribbon, 1.3 heights thick, while retaining all old polygon pixels.
The all-page V3 study proposed 24 joins on 11 pages. All 24 raw/after crops were
inspected; two classes were visibly wrong: numerical cells on
`an-7a2b17a3fb0f-p000200` and an index rule on `an-d3237d690aa0-p000138`.
Two paths agreeing at the same y do not establish a common reading unit.

V4 reused C's regional pixel-rule method with Q8 native verification, in the new
`geometry_joinbarriers.py`. A nearby verified rule makes cell ownership uncertain
and vetoes the join. This removed the false joins but also five true 8686 p5
continuations: aligned glyph stems inside the existing main box were nominated
as rules. Native verification rejected those strokes as broken or non-straight.
V5 therefore lets an **unverified** long run veto only when it lies in the actual
inter-box gap; a verified rule remains a veto anywhere in the relevant region.
No page-name exception or relaxed contact threshold is used.

Final V5 joins **15 groups on seven pages**, uniting 31 source items into 15
(16 fewer boxes). Every accepted polygon is identical to its already reviewed
V3 counterpart. All 40 agreement pages are unchanged by this new operator.

| Page | Original source groups joined |
|---|---|
| `an-466cffad2cba-p000323` | 3+2 |
| `an-778126cc8c2b-p000010` | 12+11 |
| `an-a3c2bdf81256-p000112` | 39+38 |
| `s2-3229200bf47ca465a42d-p00004` | 12+13 |
| `s2-86865c33eef5932c013b-p00005` | 9+10, 11+12, 31+32, 33+34, 35+36, 41+42, 43+44 |
| `an-9ea1564fcf4f-p000202` | 130+131 |
| `s2-86865c33eef5932c013b-p00007` | 2+3, 38+39, 70+71+72 |

This is a fragmented-line correction, not discovery of fully missing lines.
The old main rectangle is retained, so the whole envelope is not an ideal curved
ribbon and boundary notches can remain. `s2-3229200bf47ca465a42d-p00006` still has
unjoined true-looking left tails; source23's trace moves into the next row and
its independent fragment disagrees by 1.312 heights. Source17+18 on p4 disagrees
by 1.375 heights. Other true pairs are refused for neighboring owned ink or
competing ownership. The sparse page field/ideal-guide problem on
`an-d83e7a198ade-p000099` is not solved by these joins. No new line removal or
fully missed-row recovery is claimed.

## Round 4: physical separation of page leaves

The R3 rules remain enabled. This study adds an explicit **physical fold
hypothesis**, because a printed rule and a book seam can have the same long dark
stroke. `features_geometry/leaves.py` and `leaf_paths.py` render native sustained
ink, a path through it, adjacent paper and contacts with scanned outer edges.
All 195 pages have native/R1/R2 V4 images and evidence. There is no new runtime
leaf separator.

V1's vertical components merged into the scanned frame on
`an-c99f1c450f55-p000071`, hiding the actual spine. V2's straight vertical opening
also removed curved spines. V3 traces native dark ridges from recurring-column
nominations: it follows c99's real crease, but on `an-9ea1564fcf4f-p000202` it also
follows aligned first letters into the frame. V4 explicitly measures both flanks
along the whole path. Requiring isolated paper removes that first-letter error.

The remaining “outer contact” label is still not physical leaf truth. Four native
V4 hypotheses pass it: c99 p46 and p71, c8b96 p68, and **7a2b p200's table border**.
The last was checked against the full raw page: two framed numeric panels are
visible, and the selected border is not the physical gutter. The actual 9ea p202
fold remains uncertain because one expected outer contact is absent.

V5 tested a separate observation: connected white-paper regions on the two sides
of the seam. It fails in both directions. White paper connects around scanned
edges or through holes in a real crease, so c99/c8b96 can become one component.
Conversely the 7a2b table panel is a separate region occupying 0.123 of the image
and still passes the leaf-sized-area test. Reduced pixels also change topology
(the panel becomes about 0.102). V5 is retained as a falsification, not promoted.

Route 1 traces the same structures at eight-pixel body height; native and reduced
paths and contact labels are compared per seam, with unmatched paths retained.
Route 2 is recurring dark-column support across horizontal bands. It nominates
printed rules and aligned letters as well as folds; V3 itself uses that nomination
before native tracing, so these are not independent proofs of physical ownership.
The gallery draws all routes against the native feature. The per-page ledger
records nearest lateral matches within two heights; this correspondence is an
explicit comparison convention, not a segmentation score. Neither fast route is
ready to correct physical leaf geometry. The work distinguishes observable
boundary evidence from a solved page-surface model, which remains unfinished.

## Round 4: independent pure-skew validation

`features_geometry/skew_contacts.py` fits an affine line to the central observed
original-ink contact span, independently of the probability-map fit and the box
axis. Route 1 is the existing native map path's slope; route 2 is the box axis.
All three are drawn at the same centre so translation does not conceal angle
error. The 195-page V2 ledger retains every fitted line and endpoint slope error
in body heights. This audit is diagnostic and adds no full-page runtime work.

Raw tilted rows and fit crops on `an-778126cc8c2b-p000007` and
`an-ef481610a820-p000151` confirm that the native fit follows real local skew;
Paddle's map and box slopes often already follow it. V1 falsely called the
central straight part of severe 8686 p7 curl “pure skew.” V2 also checks held-out
end residuals: small central residual alone is insufficient. The green label is
still provisional. Height is a proxy, ink can be from the wrong layer, and short
rows do not supply enough independent contacts.

Six known ±2-degree rotations of existing page pixels test measurement response.
The automatically selected longest provisional row on 77d1 p1, 778 p7 and ef481
p151 is followed after each rotation. Original and transformed measurements,
expected angles and images are in `skew-rotation/`. Signed slow-route errors are
−0.061672/−0.014657, +0.016142/−0.001684 and +0.044962/−0.021707 degrees respectively;
native fast gives identical measurements on these six controls. Two transformed
ef481 cases cross the provisional-straight residual threshold despite their
small angle error. These controls validate response to a known transform, not
unseen-page accuracy or the current label's reliability. The missing named
44b5 p5 anchor remains outside the supplied manifest. No new pure-skew-only
correction count is claimed and orientation remains parked.

## Round 4: faster scouts, charged timing and cooperation

`geometry_scout.sparse_fast` batches the existing 19×31 probability-map probes
and four-step robust affine calculation. It preserves the R3 feature, thresholds
and dispatch, including scalar replay at fragile zero-sign and 0.3-bend numerical
boundaries. The first attempt exposed those boundary differences before the
fallback was added. Across the 195-page comparison and a 120-page repeat,
315 page decisions and 14,840 line witnesses agree (numeric tolerance 1e−7).
Cached-map scout median on agreement pages falls from 7.671/7.869 ms to
2.644/2.760 ms in the two repeats. These microbenchmarks exclude inference and
are not a claim about complete correction latency.

The geometry-only `geometry_context.correct_geometry` can reuse rule/scout
witnesses and retained original indices. Original contour ancestry stays intact,
while ink retention sees only retained boxes; deleting a neighbor cannot allow
its lost ink to certify a shrink. Stack kept its own piece-aware adapter but
adopted a snapshot of `sparse_fast`. It independently found exact dispatch on
195 pages and 9,586 line witnesses (largest numeric delta 1.25e−11). Stack's
reported frozen combined results keep the 30 R3 reshapes and 92 curved cuts.
**The 15 new fragment joins here are optional and not in that frozen stack.**

C's regional Q8 rule protection was reused in the new join-barrier module; the
source method and limits were announced on the board and acknowledged by C.
C's font-height census and later table extent are not imported into runtime:
false-clear heights persist and its table protection is incomplete/overbroad.
B's glyph handedness cannot certify a rule, and a high-support contact path
cannot certify front ink. Original ancestry, retained context and caller-supplied
forbidden regions are available for composition. No B/C recoveries or removals
are silently included in A's output or timing.

The new `geometry_pipeline.run` performs one Q8 scout/correction, the equivalent
geometry scout and guarded R3 geometry, curved-rule separation, then conditional
native fragment work. Each timed run freshly decodes and infers every page with
the pinned detector and postprocessor. It includes both scouts, all native
filtering, components, traces, rule guards and envelope checks. It uses no saved
rendering, model guide or other track's census. JSON writing and review rendering
are outside the timer. Session construction is recorded separately. Both runs
are warm, single-thread and sequential; the second reverses page order.

All **390/390 fresh runs** exactly reproduce baseline polygons, prior R3+Q8
polygons and final study polygons. Saved final exports carry the full measured
page `seconds`. All geometry source hashes stayed fixed. Values below are
milliseconds **median / p95 / maximum**, not pooled repeats.

| Group / repeat | New fragment operator | Q8+A complete correction | Decode + detector + Q8+A |
|---|---:|---:|---:|
| Agreement 40, R1 | 0.578 / 0.878 / 87.728 | 15.459 / 30.586 / 99.320 | 177.176 / 216.976 / 251.636 |
| Agreement 40, R2 | 0.513 / 0.804 / 79.645 | 14.593 / 27.706 / 90.154 | 161.728 / 190.406 / 223.978 |
| Discrepancy 80, R1 | 0.794 / 188.452 / 675.397 | 20.347 / 215.452 / 760.734 | 184.612 / 387.467 / 999.536 |
| Discrepancy 80, R2 | 0.720 / 168.301 / 598.795 | 18.038 / 212.382 / 682.434 | 166.978 / 360.437 / 882.927 |

For all 101 new pages, Q8+A correction is 20.149/214.191/760.734 ms and
17.937/211.821/682.434 ms. The all-195 raw group tables and each page's measured
parts are in `round4/summary.json` and `runtime/repeat-{1,2}.jsonl`. The new
fragment operator's expensive negative agreement case is
`an-dbd045ccd84c-p000249`: a stamp fragment wakes the native verifier but is
rejected. The worst discrepancy cost is 4959 p4; profiling attributes about
314 of 672 ms to separable filtering and 418 ms to field preparation. This is
real charged cost, not hidden detector or rendering work.

All 390 observed correction paths remain below one second. Strict negligible
clean-page overhead is **not achieved**, particularly that 80–88 ms negative
tail. No unpaired subtraction from R3's historical timing is used to claim a
net gain. Stack's combined timings are separate measurements without the new
joins, and no held-out or production latency guarantee follows here.

## Round 4 verification, module readiness and next work

78/78 prototype tests pass: the previous 57 plus four scout tests, six context
and ancestry tests, and eleven fragment/evidence/conservation tests. New source
lives only in this track's folders and new `shared/geometry_*.py` modules. No
production page code or tests changed. The saved artifact audit checks every
final export, all old-polygon pixels in accepted joins, unchanged nonparticipants,
Q8 source multiplicity, exact reviewed-subset membership, all 40 agreement
outputs, the 390 fresh receipts and the source hashes. The gallery links each
page to both fast routes, per-line ledgers and detector JSON. Exact check/link
counts are recorded in `round4/validation.json` and `gallery-links.json`.

Ready as conditional prototype modules: the equivalent sparse scout; the
retention-aware geometry context; native body-contact preparation/tracing; and
the ancestry-preserving fragment join with native rule/neighbor guards. The
leaf renderer and independent skew audit are reusable diagnostics, not accepted
correction modules. The slow full-page body field itself is not a cheap census.

Next work, in order:

1. Render and compare **local** native density fields at nominated fragments,
   including a halo that preserves the exact surrounding-paper and Gaussian
   support. It must reproduce the current native paths and negative decisions
   before claiming to remove the stamp/large-page timing tails.
2. Make body scale and alternative-row ownership explicit on 3229 p6 and the
   remaining 8686 p7 tail. Keep measured main/fragment disagreement visible;
   do not relax the 0.35-height test because a named page would benefit.
3. Model paired page outlines and paper-surface continuity. Test against both
   real creases with holes/truncated edges and large framed tables. Connected
   white area and long dark rules have now been falsified as sufficient proofs.
4. Adjudicate the remaining per-line skew/contact ledger, especially short rows,
   letter-axis bias and opposite-page ink. Known rotations validate response but
   do not establish a semantic baseline or a safe new pure-skew correction.

These are remaining requirements, not completed features. The round remains
PARTIAL despite the accepted fragment corrections and faster equivalent scout.

Final artifact audit: **54,793 checks**, 1,755 decoded final images, 14,023 finite
exported items, all 15 join groups retaining every original Paddle polygon pixel,
9,086 native-route line checks and 390 exact fresh reproductions. The owner index
has **6,473 valid link occurrences** (4,718 distinct targets). The leaf ledger has
914 native hypotheses: 220 have no matched reduced route and 871 no matched
recurring-column route; only four carry the explicitly provisional outer-contact
label. The skew ledger has 9,071 fitted records, 5,301 provisionally straight.
These are observability counts, not correctness rates. All 131 leaf-positive
page overviews and the eight largest provisional map/native slope disagreements
were additionally viewed. Short spans, letter-shape bias and a stamp-adjacent row
remain ambiguous; no new skew correction follows that review.

Staging the finished round-4 files again failed with `Operation not permitted`
when Git tried to create `greek-ocr-toolkit-fl-geometry/index.lock`. No round-4
commit or push was created; the base remains `ef1a044`. The authorized fallback
is [commit-Fgeometry-round4.patch](../../../.astra/commit-Fgeometry-round4.patch),
[commit-Fgeometry.sh](../../../.astra/commit-Fgeometry.sh) and the adjacent
`commit-Fgeometry-round4.validation.json`. The script checks branch, exact base,
empty index, source hashes and patch hash, stages only this track's files and
uses the requested trailers. The round-3 script is preserved separately.
