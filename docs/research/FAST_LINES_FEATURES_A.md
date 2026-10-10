# Round 3, track A: page geometry

Curvature, skew and separation now have explicit page renderings and both fast
routes on all 195 supplied pages. The conditional prototype changes 30 existing
line geometries on 11 pages and makes 92 additional cuts along three curved
column rules. All 308 round-2 separator cuts remain exactly unchanged. This is a
partial result: severely fragmented curl, physical page-leaf separation and
semantic baseline recovery are still unresolved.

The final review index is
[`features_geometry/index.html`](../../.astra/fast_lines/out/features_geometry/index.html).
The output [README](../../.astra/fast_lines/out/features_geometry/README.md)
explains the colors and versions. Code is under
[`features_geometry/`](../../prototypes/fast_lines/features_geometry/README.md)
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
[`benchmark-v6/`](../../.astra/fast_lines/out/features_geometry/benchmark-v6/).
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

Git staging is blocked by the sandbox denying creation of
`.git/worktrees/greek-ocr-toolkit-fl-geometry/index.lock`. No commit or push
occurred; the branch remains `astra/ff-geometry` at `b5199ad`. The requested
fallback is [the patch](../../.astra/commit-Fgeometry.patch) and
[commit script](../../.astra/commit-Fgeometry.sh), with exact trailers and a
file-hash/forward/reverse validation receipt beside them. The script stages only
this track's code and report and refuses an already populated index.

Next component work should render body contacts along severely curled fragments,
including accents and neighboring-row alternatives, then test a shared sheet
field against those contacts. The field must not borrow a row solely because
pitch agrees. Physical leaf separation needs a model that distinguishes a dark
fold from a printed/back rule and explains truncated page edges. Tight rule/letter
junctions need better local ownership evidence before the conservative d12a
abstention can be relaxed. Short pure-skew cases and the missing skew anchor need
direct raw-page verification. Finally, the remaining line ledger needs explicit
human adjudication; its counts must never be advertised as accuracy.
