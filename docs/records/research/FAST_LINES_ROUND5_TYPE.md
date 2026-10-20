# Round 5 — type, native glyph ownership, apparatus and tables

This is a partial result. The public `Stack()` now supplements the existing
pitch/phase recovery with conditional original-pixel body contacts, and attaches
a large paragraph initial only to its first adjacent row. It does not identify
font names, infer a semantic baseline, or claim that every detected ink piece is
a letter. The output and owner-comment ledger are under
[round5/type](../../../.astra/fast_lines/out/round5/type/README.md).

The baseline is merged `0ffe28d`. This branch changes C's live imported modules;
it does not duplicate the stack or import a shadow pipeline. Its measured stack
contains round-4b A/B plus round-5 C. A's new column and final-band changes and B's
new seal/ornament removals are separate until the coordinator merges them. Their
timings and correctness are not claimed here.

## Feature rendered first: native body contacts outside an existing grid

The owner found missing rows in small apparatus, irregular lists and curved
paragraphs where the previous repeated-pitch scout never proposed a slot. The
prediction was that independent native bodies would expose those rows even when
the existing detector boxes supplied the wrong pitch or phase.

`type_residual.render` makes a local-paper ink mask, renders connected body
candidates and their bottom contacts, and connects nearby compatible contacts.
Each component retains its native bounding box, centroid, existing-polygon
ownership and exclusion state. Component size is measured locally; a footnote
does not inherit the main paragraph's body height. These are physical hypotheses,
not character recognition or certified front-page ownership.

The explicit images and numeric records are `contacts-v1/`, `contacts-v2/` and
`ownership-depth-v1/`. Raw/overlay crops were inspected for all 14 supplied owner
pages. The fifteenth, `s2-032eaf8e6b3b83918feb-p00004`, has only its numbered review
image in the located authorized material; its original image is outside the
195+5 cohort and was not recovered from an unrelated corpus.

The iterations were consequential:

1. Native v1 joined adjacent rows through capitals. Mutual-neighbour v2 reduces
   graph branching but still switches rows across word gaps and joined marks.
   The graph is therefore a nomination, never a replacement line census.
2. Fast explicit R1 at 12 samples per provisional body lost fine apparatus
   components. Twenty samples improve the rendering, but the short row on
   `an-d83e7a198ade-p000099` still differs. Runtime confirmation uses original
   pixels only in nominated regions, rather than trusting R1 as truth.
3. R2 v2 reused the already-paid DB map. It missed the left footnotes on
   `an-2cfe28da5103-p000084` and the last line on `an-00f143ecce59-p000192`.
   Coarse connected-ink v3/v4 then joined text to a stamp/frame and rejected the
   resulting giant component. Local overlapping strip ridges in v5 nominate
   small text without requiring that it form an isolated page component.
4. R2 v5 uses six samples per box-height proxy, then requests native component
   evidence. Its standalone 40-agreement scout median was 1.235584 ms; it woke on
   22/40. Those wakes are not 22 errors. The downstream cost must be included.

All routes retain per-page records. The paired contact crops expose row switches
and small-print sampling loss; no overall overlap score is used as correctness.
`route-audit/<page>.json` records every native row's nearest R1 bodies and their
distances in that row's measured body height, plus all intersecting R2 request
regions. R1 v4 adds measured ownership depth; R2 cannot measure this feature and
must request the native rendering. That limitation is explicit rather than
presenting the cheap ridge as equivalent glyph ownership.

## Ownership within a glyph, then conditional recovery

Regional Paddle localization removes the expensive blind line search. A region
is submitted only after an unowned native contact chain exists. Every accepted
output piece must independently contain at least five such bodies spanning four
local body heights. This restriction leaves very short legitimate rows missing.

The following prediction/test/inspection cycles are preserved in
`recovery-v1/` through `recovery-v9-all-controls/`:

- V1's existing-body veto rejects real close footnotes because a broad regional
  polygon contains neighbouring ink. V2 fitted/extrapolated body contacts to
  narrow it; this **failed**: `3229…p00004` switches to a neighbouring row and
  `d83…p000099` crosses an apparatus gutter. `type_contact_band` is retained only
  as the failed version-2 diagnostic, never called by the live version.
- V3 keeps regional envelopes and checks competing row centres. V4 clips every
  envelope to native support, but loses word ends. V5 clips only unsafe ends
  (exclusions, crop edges, competing rows or unresolved rules). This improves
  bounds but does not prove text ownership.
- The 195-page v5 experiment proposed 92 pieces, including two mirrored rows on
  `s2-0ce9d1025b3f23c7119e-p00001`, two faint verso rows on
  `an-ef481610a820-p000150`, and horizontal hatching in the bee engraving on
  `an-1f8e7d022643-p000001`. All were visually false and none is promoted.
  V6 abstains on B's existing weak-layer suspects, rejects a localization taller
  than 3.5 measured body heights, and protects explicit regional table evidence.
  An ordinary-shape/front hypothesis or an unknown B decision never certifies
  recovery. This conservative policy can also miss genuine faint front text.
- V6 exposed a composition bug: a native chain in the left column authorized
  both pieces after a separator cut. V8 requires independent native support for
  **each final piece** and rechecks existing rows after splitting. No later A
  smoother is assumed to deduplicate C's output.
- V7/V8's any-pixel glyph-contact veto loses true close rows. The next native
  rendering records the maximum depth of existing-box penetration into a glyph
  and the glyph's measured inscribed stroke radius. Shallow edge contact is
  distinct from penetration beyond a stroke radius. Centred-owned glyphs remain
  excluded. V9 restores both left-page footnotes on `2cfe…p000084` and one list
  entry on `ef4816…p000181`. The short preceding fragment remains missing.
- V9's 194 nonparked supplied-page control run has 53 tentative pieces and zero
  agreement additions. Inspecting every non-owner addition catches a thin
  decorative band on `s2-658e6dcb48b540357a9d-p00001`. The C caller had passed local
  component height to B's motif API, whose documented scale is the page box
  proxy. Even at the correct scale, B's cheap nomination misses this band;
  independently nominated C candidates now pay for B's unchanged full spatial
  verifier. The ink track agreed this use. It rejects the decoration; no
  acceptance threshold is lowered.
- A remaining `4959…p00005` candidate crosses a central rule that ends inside its
  vertical envelope. Old `type_barriers.protect` required the rule to span the
  whole envelope. A's existing regional `geometry_joinbarriers.inspect` supplies
  a conservative unresolved-interior-rule veto. The candidate-only v10 audit
  rejects exactly that crossing and the decoration among the 53 v9 pieces.
  This leaves 51 text pieces for composition, not 51 completely repaired pages.
- The first composed v10 run charged the full spatial verifier for every
  nomination. It preserved those 51 pieces but took 1,601.020 ms in the worst new
  C stage and 2,357.347 ms in the worst complete correction. V11 reuses B's
  existing four-copy spatial recurrence scout before that unchanged verifier.
  Both explicit and fast recurrence renderings nominate the decorative band;
  the 53-candidate audit nominates only that band. The fresh 200-page public
  outputs before the later initial-outline fix are exactly equal to v10. This is a measured cost correction, not an
  accuracy improvement or a lower acceptance threshold.

The live C chain is `type_extended.recover` → `type_residual_recovery.recover`
(v11) → `type_initials.complete`. Existing R4 pitch/phase recovery runs first;
its output polygons own ink for the residual scout. Every B removal footprint
remains an exclusion. No full-page separator is rerun by C. Optional
`column_evidence` applies A's live `geometry_columns.apply` before independent
piece validation once merged; no A implementation is copied here. A direct
live-import contract check, recorded with A's source hash in `column-contract/`,
splits the refused 4959 p5 cross-rule candidate into two independently supported
pieces. Its raw/after overlay was inspected. This is an operator check, not a
merged-stack run; those two pieces are not included in the published 51.

## Large initial: explicit ownership of the first adjacent row

`type_initials.render` shows native connected components beside the start of a
recovered row, their size and vertical relationship, and the earlier adjacent
rows that could own them. Slow native, fast explicit 12/body and coarse 5/body
routes are drawn in `initials-v1/` and `initials-v2/`.

The native E on `an-466cffad2cba-p000277` is a clear positive. R1 initially rejected
it because a 1.8-pixel sampling displacement crossed a positional bound. V2 gives
the *nomination* a two-sample uncertainty margin; native confirmation remains
unchanged. All three routes then agree. The initial is unioned into the first
row's envelope with a shoulder, marked `initial_completed=True`, and checked
against removal footprints. The raw/after crop was inspected. The previous
round's 18 additions produce exactly one such completion in the standalone
control, this E. Synthetic earlier-row and exclusion controls prevent stealing
a drop cap from the row above. A was explicitly asked to preserve this metadata
and the tall letter in its final smoothing hook.

This does not solve all initials: the recovered second row beside the I on
`an-00f143ecce59-p000258` must not acquire an initial owned by the first row.
The incomplete `initials-v3` exploratory run stopped on a missing parked-page
receipt field; completed artifacts and the error log are retained. The composed
run supplies the final all-candidate initial control.

A late native-pixel retention check falsified the first completion outline:
raster envelope simplification dropped 108 pixels from the old polygon, including
two dark pixels. The final implementation takes a vector union of the old
polygon, the measured initial and a short shoulder, using the already-installed
polygon library at 1/256-pixel precision. The old-minus-new vector area is zero.
Four raster-boundary differences remain, all white (255); no native ink is lost.
The new raw/after E was inspected in `initials-vector-v3/`. Disconnected unions
and any overlap with removal footprints abstain. `final-before-initial-retention/`
preserves the earlier exports and timing; `final/` was regenerated and replayed
with the vector union frozen.

## Tables: delegation guard, not complete semantic boundaries

The existing `type_tables` original-pixel rule/intersection and repeated-cell
renderings were reused, not replaced by the model's line list. New three-route
images are in `table-routes/` for `an-7a2b17a3fb0f-p000200` and
`s2-831443dc5e6f1ccfbaf5-p00039`.

Native and heuristic cell alignment leave the outer 7a2 table extent incomplete.
The fast explicit rule route protects the complete left table but only parts of
the right header. On 8314 p39 the explicit outer rule extent encloses the table
body. These renderings were checked by eye against the printed rules. A cheap
short-cell grid scout wakes this existing explicit route only on residual-positive
pages. Protected regions block new C recovery; existing detector cells are kept
for the small detector. Five v5 additions on 7a2 and a dot-row on 8314 are thereby
refused. This also avoids the v5 1,413-ms table correction outlier.

The slow/R1/R2 observed times on these two diagnostic pages were respectively
323/70/39 ms and 590/41/55 ms. These single diagnostic observations are not final
runtime benchmarks. Table extent remains incomplete, and an area outside a
protected table is not certified prose or image. B retains ownership of faint
table print; C does not erase pale cells or reclassify table borders as text.
The native 8314 rendering itself misses almost all long rules, while its fast
explicit reduction connects visible rule fragments. This is a failure of that
slow renderer, not evidence that the native page lacks a table; its only
horizontal rule and R2's narrow numeric strip are preserved in the comparison.

## Validation, timing and remaining work

Final measured results and per-comment outcomes are recorded below. The artifact validator
checks all 200 detector exports, finite in-image polygons, null baselines,
orientation passthrough, no discounted rendering, and permanent B exclusions.

The final result has 51 new residual text segments on 14 pages, plus the 18
previous grid additions (69 total), and the E completion. Every prior R4b polygon
is exactly retained except the intended E expansion. All 308 Q8 source cuts,
61 reflected-print removals and 11 ornament removals remain. Of the 41
`ours_more` pages, six receive 31 new segments: 9ea…202 (1), 3229…6 (10),
4959…4 (5), 4959…5 (13), 8686…7 (1), c0b02…10 (1). The other 20 segments
are on development or other discrepancy pages. No agreement page and none of
the five newly supplied curved pages receives a new C addition.

Four repair comments are fixed within their specified C clause: both 2cfe
footnotes, both 3229 p4 rows, the d83 apparatus row and the large E. Mixed comments
remain partial where column/curl/watermark work belongs another track. The two
positive controls are preserved exactly. The output ledger also records the
ambiguous `6,7,` comment and the unavailable 032e original without inventing an
interpretation or missing input. Every accepted new piece was viewed in native
raw/after crops; the final polygons are identical to those reviewed candidates.
This is not an exhaustive glyph transcription or a precision/recall claim.

### Frozen runtime measurements

Two fresh file-to-lines passes, forward then reverse cohort order, returned exactly
equal detector items on all 200 pages. The ONNX session was warmed once per pass.
Every correction dependency is included: native fields, conditional regional
inference, table/rule checks, B verification and initial completion. Session startup,
image decode and the initial small-detector inference are separately recorded;
they are not part of the correction target. This is the shared Mac, not an isolated
performance host. No diagnostic job ran concurrently in this C process.

Values below are measured milliseconds, median / maximum. Full-precision values
and every page are in `final/summary.json` and `final/*.r{1,2}.json`.

| Cohort and work | First pass: median / maximum | Second pass: median / maximum |
|---|---:|---:|
| 40 agreement, new C stage | 2.295 / 31.710 | 2.467 / 36.471 |
| 40 agreement, all C | 3.394 / 34.303 | 3.487 / 39.474 |
| 40 agreement, whole stack correction | 22.851 / 104.802 | 21.574 / 109.720 |
| 101 discrepancy, new C stage | 16.189 / 457.012 | 20.050 / 485.216 |
| 101 discrepancy, all C | 29.714 / 895.781 | 30.099 / 913.253 |
| 101 discrepancy, whole stack correction | 83.980 / 1408.367 | 87.202 / 1454.941 |
| 5 new curved, new C stage | 4.211 / 58.590 | 4.476 / 59.255 |
| 5 new curved, all C | 5.668 / 60.038 | 5.947 / 62.039 |
| 5 new curved, whole stack correction | 78.905 / 263.145 | 81.488 / 255.500 |

The strict target is **not met**. New C work adds 2.295 / 2.468 ms median on
agreement pages, with 31.710 / 36.471 ms tails on `an-7a2b17a3fb0f-p000175`.
No agreement page receives an addition. Across discrepancy pages the new stage
maxes at 457.012 ms on 4959 p5 and 485.216 ms on 9ea p202; these are separate
pass maxima, not a guarantee. Whole corrections reach 1,408.367 / 1,454.941 ms
on 4959 p4. Its inherited A fragment work costs 602.368 / 619.762 ms and all C
costs 706.878 / 732.745 ms, including 408.856 / 429.589 ms of new C work.
The first pass exceeds one second on 4959 p4/p5; the second also exceeds it on
4959 p1 and 9ea p202. The earlier frozen pre-union passes reached 1,557.245 /
1,567.878 ms; those receipts are preserved. Changing the E outline does not
explain the timing variation on other pages. A is separately optimizing its
fragment arithmetic and duplicate dependencies; that future merged result is
not substituted for these measurements.

Validation: **153/153 prototype tests**, **29,120 export checks**, **603 gallery
links**, and **200/200 exact fresh replays**. Both source receipts equal the
frozen current source key `f30246c13b3d3a28ddda8c6ab14937044ea5726f93aba1f965449e55c4313d95`.
The 199 unaffected pages match the previous final exactly; the only changed
detector item is the completed E polygon. Its final public output independently
passes the vector and native-pixel retention check. Each of the 51 residual
pieces is unchanged from its inspected candidate. These checks establish export
and implementation consistency, not unseen-page accuracy.

Outstanding feature work remains substantial: native joined-script body
partitioning, reliable font identity within and across books, full table
boundaries, very short list fragments, stamped last rows, and connection of
detached starts to existing curled rows. The `uncertain=False` body-height
counterexample reported by A in round 4 remains valid; the font census is not
used as a runtime certificate. No held-out page or PDF text layer was used.

Reusable pieces are the native body/contact and overlap-depth renderer, the
conditional residual scout, the per-piece ownership check, and first-adjacent
initial completion. They are prototype modules with explicit abstention, not a
finished font or layout system. The failed extrapolation tool stays diagnostic.

Cooperation was material: B supplied reflected/weak-ink and spatial ornament
witnesses, corrected the scale contract and approved candidate-only full
verification; A supplied the sustained-rule veto and a live optional column
certificate, warned that its row ownership cannot certify C additions, and
preserves tall initials. C's regional table guard was already reused by A for
fragment joining. No other track folder or production pages file was edited.


The next component work should first render ownership across the gaps between
these detached starts and the already-localized row. Native bottom contacts alone
were falsified as a joining certificate; matching tangent or pitch is insufficient.
For short apparatus fragments, repeated native glyph exemplars and their row
relationships need a renderer that preserves alternate shapes before reducing the
five-body requirement. Stamped last rows need a separate glyph/stamp ownership
rendering, not a relaxed weak-ink veto. Full table boundaries remain a prerequisite
for treating outside regions as prose. The cost work should inspect the coarse
scout's unnecessary wakes, while retaining every native positive and including
all downstream dependencies in another fresh timing measurement.


## Handoff

The sandbox rejected `git add` because it could not create
`greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-fl-missed/index.lock`.
No commit or push was made. The requested fallback is
`.astra/commit-Ftype-r5.patch` with `.astra/commit-Ftype-r5.sh` and a validation
receipt. It contains only the ten owned code/document files. Forward application
against base `0ffe28d`, exact file hashes, reverse application and shell syntax
are checked before handoff. Images, model output and timing receipts remain
outside git under `.astra/fast_lines/out/round5/type/`.
