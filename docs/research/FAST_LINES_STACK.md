# Fast line finding: combined stack, round 4b

R4b removes all eight owned track snapshots and imports the final merged modules
from `69db79f`. It adds **15 fragment joins and three real recovered rows** to the
previous stack. All 195 pages were run twice, with exact output agreement between
repeats. The measured correction maximum is **978.564 / 976.601 ms**: below one
second, but with little margin. Clean-page overhead is still not negligible, and
its maximum worsens to **107.472 / 99.312 ms**. The owner's target remains partial.

Final detector JSON: **`.astra/fast_lines/out/stack/r4b/<page>.json`**.
Open the [195-page gallery](../../.astra/fast_lines/out/stack/r4b/index.html),
[all nine changed pages with raw/before/after crops](../../.astra/fast_lines/out/stack/r4b/changes.html),
[raw timing summary](../../.astra/fast_lines/out/stack/r4b/summary.json), and
[validation](../../.astra/fast_lines/out/stack/r4b/validation.json).
The previous `final/` exports remain unchanged for comparison.

## Imports and composition

Deleted the stack copies of `geometry_scout`, `ink_pipeline`, `ink_ownership`,
`ink_motif_gate`, `ink_recurrence`, `ink_repeat_field`, `recovery` and `type_context`.
[reuse.json](../../prototypes/fast_lines/stack/reuse.json) now records merged-module
imports and hashes instead of snapshot destinations. B runs through
`features_ink.pipeline.ink_run`; C through `shared.type_extended.recover` and its
shared context/recovery dependencies. Geometry imports `geometry_scout`,
`geometry_context`, `geometry_feature_rules` and `geometry_fragment_correct`.
No track modules were edited, and no track acceptance logic remains copied in stack.

The geometry adapter is 38 lines of composition, source-list mapping and receipt
normalization. The shared context accepts intact original sources; Q8 pieces stay
in the current output but cannot masquerade as their original contour or own ink
lost by a reshape. This is conservative when split neighbors exist. All 30 prior
reshapes and all 400 separator cuts remain in the observed result. Shared scouts
are supplied, so Q8 is still called once. B removals precede geometry, fragment
joins and recovery. Their footprints are passed to both new stages.

The resulting order is Paddle → Q8 → B removals → shared geometry → curved-rule
cuts → native fragment joins → extended type recovery. Native contact and the
extended grid are the new runtime dependencies; diagnostic leaf, font, inkiness,
image and stamp censuses remain outside this path. Orientation stays parked.

Type's known v6 table-extent failure was checked explicitly. On
`s2-49598b2e848ab1f0ee1e-p00005`, the post-geometry layout does not nominate a new
supported extension slot, so `table_extents` is null. The prior real recovery at
old slot 15 survives without a bypass or a page-specific exception. The underlying
table-extent flaw remains a limitation on other layouts.

## R4b timings against the owner's target

Each cell is **median / p95 / max, in milliseconds**. Repeat 2 reverses page order.
Decode, original Paddle inference/postprocessing and all conditional corrections
are charged from image file to final items. Model initialization/warmup and review
rendering/serialization remain outside the per-page timer, as in round 4. Raw
receipts preserve the separate startup and stage timings.

| Cohort | n | Repeat | Paddle file-to-lines | Added corrections | Final file-to-lines |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 | 1 | 148.260 / 171.012 / 199.397 | 18.396 / 40.637 / 107.472 | 167.050 / 214.138 / 230.767 |
| Agreement | 40 | 2 | 145.865 / 171.570 / 199.926 | 19.479 / 37.129 / 99.312 | 165.379 / 208.700 / 231.607 |
| Discrepancy | 101 | 1 | 144.759 / 232.447 / 283.099 | 40.311 / 422.769 / 978.564 | 201.741 / 599.435 / 1179.828 |
| Discrepancy | 101 | 2 | 143.504 / 229.803 / 280.637 | 39.048 / 420.418 / 976.601 | 202.943 / 593.836 / 1177.813 |
| All supplied | 195 | 1 | 147.546 / 228.194 / 283.099 | 31.078 / 390.104 / 978.564 | 184.203 / 566.938 / 1179.828 |
| All supplied | 195 | 2 | 145.581 / 227.895 / 280.637 | 32.261 / 388.142 / 976.601 | 182.468 / 566.433 / 1177.813 |

All 390 correction timings are below one second; full file-to-lines time is not:
the maximum is 1179.828 / 1177.813 ms. These are two measured runs on the shared Mac,
not a held-out latency guarantee or a worst-case bound.

There are **latency regressions**. Agreement max was 51.689 / 50.744 ms in the prior
stack and is now 107.472 / 99.312 ms on `an-dbd045ccd84c-p000249`. The new fragment
verifier spends 72.851 / 72.813 ms rejecting a stamp-related candidate; output is
unchanged. Discrepancy max was 688.609 / 653.701 ms and is now 978.564 / 976.601 ms
on `s2-49598b2e848ab1f0ee1e-p00004`: fragment verification costs 590.191 / 603.254 ms
without accepting a join, alongside 290.979 / 287.663 ms in type. These measured
outliers were relayed to geometry and recorded on the shared board. No new gate
was invented here to hide their cost. Lower aggregate medians do not establish a
speedup: Paddle's own timings also changed between rounds on this shared Mac.

The old ink tail stays resolved: `an-778126cc8c2b-p000011` now costs
22.867 / 22.453 ms in combined corrections, including 13.937 / 13.620 ms in B.
The new clean tail has a different cause, native fragment rejection.

## Changed-page review and remaining failures

Exactly **186 complete item lists are unchanged**. All nine changed page overviews
and all **21 raw / previous / R4b crops** were inspected. No new visual regression
was observed in that scope. The two older recoveries on 8686 p7 change their
polygon boundaries, so preservation is not claimed as polygon equality there.
The same visible rows remain covered. Full page observations, including remaining
failures on unchanged pages, are in the updated
[195-page ledger](../../prototypes/fast_lines/stack/review.json); the
[nine-page change ledger](../../prototypes/fast_lines/stack/review_r4b_changes.json)
records this round separately.

| Page | Improvement and remaining limitation |
|---|---|
| `an-466cffad2cba-p000323` | One native-validated join reconnects the curved final syllable to its real body row near the stamp. Prior polygon areas stay covered; the stamp overlap and other uneven row boundaries remain. No new visual regression observed. |
| `an-778126cc8c2b-p000010` | One join reconnects the left quotation mark to the same printed dialogue row. Its old rotated envelope leaves an angular corner; nearby quote fragments and central stamp interference remain. No new visual regression observed. |
| `an-a3c2bdf81256-p000112` | One join reconnects a separated ending in the prose heading between grammar tables. Table cells remain separate. The heading still has other fragmented endings; no new visual regression observed. |
| `s2-3229200bf47ca465a42d-p00004` | One join reconnects the left curved fragment with the matching body row. The five previous reshapes persist. Broad old envelopes and many other left-curl straddles remain; no new visual regression observed. |
| `s2-86865c33eef5932c013b-p00005` | Seven joins reconnect real curved right ends, preserving all fourteen old source polygons. Their changed grid also enables a real missing row beginning τους δε, μετα το κοπανισμα, with its right end following the curl. This is a pre-existing bracketed-slot method firing after joins, not a new edge slot. Remaining unjoined ends, incomplete rightmost words and block-edge missing text are visible. No new visual regression observed. |
| `an-466cffad2cba-p000277` | Extended type recovery adds the real first body row below the title beside the large E. The large initial remains outside the main recovered envelope; its full reading-unit geometry is not solved. No new visual regression observed. |
| `an-9ea1564fcf4f-p000202` | One join reconnects the left word continuation with its real dictionary row. Both earlier recovered entries and five reshapes remain. Dense short fragments and adjacent-column boundary difficulties persist; no new visual regression observed. |
| `an-fd4fa0018ae1-p000035` | Extended type recovery adds the real first prose row and includes its large B. It stays above the next body row. The top ornament remains boxed as before; no new visual regression observed. |
| `s2-86865c33eef5932c013b-p00007` | Three joins reconnect two pairs and one three-piece curved row. The two earlier recovered rows remain, but both envelopes shift slightly after the joins change the grid and regional crop. Raw comparisons show the same visible text covered; the last rightmost parts and an unbracketed missing row remain unresolved. No new visual regression observed. |

Totals are **308 Q8 cuts, 92 curved cuts, 30 reshapes, 61 back-print removals,
11 ornament removals, 15 joins and 18 recoveries**. The joins unite 31 prior source
polygons into 15, reducing the count by 16; three extra recoveries bring the final
count to **13,969 items**, down from 13,982. This is not an accuracy score. 58 pages
change relative to Paddle. The new row on 8686 p5 uses an old bracketed-gap slot
that becomes available after the seven joins; it is a combined interaction, beyond
the two new standalone type recoveries. Severe curl, missing ends, broad envelopes,
stamp interference and other failures in the previous ledger remain unresolved.

## Validation and handoff

**142/142 prototype tests pass**, including direct-function identity checks,
no duplicate Q8, rejection-footprint propagation and the raster-boundary audit.
The export validator passes **16,808 checks** over all 195 pages and both repeats:
fresh Paddle equality, source ancestry, Q8 pieces, zero accepted reshape ink loss,
all original joined polygon pixels retained within the actual image, no recovered
polygon intersecting a B removal, valid exports and reviewed outputs.

The first join audit mistakenly counted 22 pixels in the nonexistent column at
`x == image_width`. The audit canvas now clips to the actual half-open image
raster; a regression test distinguishes that boundary from real lost pixels.
No runtime or output changed. Both benchmark source snapshots remain identical;
the two validation-only file changes are separately hashed in
[post-timing-validation-source.json](../../.astra/fast_lines/out/stack/r4b/post-timing-validation-source.json).
No held-out pages, PDF text layer, production page modules or tests were used.

The imported composition is ready as a prototype; native negative-tail cost and
type's imperfect extent protection remain reasons not to claim the owner's whole
target achieved. The original stack patch was applied by the coordinator as
`f903ec5`; the material below is the historical round-4 record, not current imports
or current measurements.

Git staging was blocked by the sandbox (`index.lock: Operation not permitted`); no new commit or push was made. The requested fallback is [commit-Fstack-r4b.sh](../../.astra/commit-Fstack-r4b.sh) with its [validated patch](../../.astra/commit-Fstack-r4b.patch), exact file/deletion manifest and both required trailers.

---

## Historical round 4: owned snapshot version `final`

The combined prototype preserves all round-3 corrections: 308 printed-rule cuts,
92 curved-rule cuts, 30 reshapes, 61 back-print removals and 11 ornament removals.
It recovers 15 lines on 13 pages, one more than type alone. These are measured
operations, not precision/recall scores. Significant errors remain. Timing results
below judge the owner's target literally:

> for pages where small detector has no errors we add negligable overhead, and for pages where it needs fixes we have sub 1 second corrections.

The full [charter](../../.astra/fast_lines/CHARTER.md) retains the owner's words about
faintness and inkiness, tables, images, curvature, skew, separation and font geometry.
This composition does not turn those requests into solved categories.

Open the [final gallery](../../.astra/fast_lines/out/stack/final/index.html),
[raw timing summary](../../.astra/fast_lines/out/stack/final/summary.json),
[validation](../../.astra/fast_lines/out/stack/final/validation.json) and
[195-page inspection ledger](../../prototypes/fast_lines/stack/review.json).
The [entry point and commands](../../prototypes/fast_lines/stack/README.md) use
`prototypes.fast_lines.stack.Stack` or `python -m prototypes.fast_lines.stack IMAGE`.

## Pipeline and interactions

1. Decode the image once; run PP-OCRv6 small once and postprocess it. Keep its original
   probability map and ordered polygon list. No large detector enters this path.
2. Run Q8's cheap printed-rule scout once. Refine and split only its nominated
   corridors. Preserve original source indices on every piece. This establishes
   columns before ownership and grid measurements.
3. Run B's reflected-print ownership and ornament checks on the separated items.
   Delete only their accepted boxes. Store the actual removed polygons permanently.
   Broad image masks and front/unknown ownership never certify recovery.
4. Run A's probability-map geometry scout on original Paddle contours. Its faster
   batched arithmetic preserves the original samples, continuity walk and decisions.
   Dense bands run only on nominated pages. Only intact surviving original sources
   can reshape; the retention guard sees surviving polygons, so a removed neighbour
   cannot hide lost ink. Q8 pieces keep their exact geometry.
5. Refine curved rules from the existing Q8 witness, without repeating its scout.
   Rule ownership still sees all original crossings, including removed ones: deleting
   a back-print box must not manufacture evidence that its rule belongs to the front.
   Cut current survivors along accepted rules.
6. Recover type-grid gaps last. The grid receives a quadrilateral view of curved
   ribbons; ink ownership uses the actual ribbons. Rejected regions veto candidate
   seeds before regional inference and veto proposed/completed polygons afterwards.
   Local table, reflected-print and separator checks remain conditional. New lines
   get regional rule protection, without repeating the full-page Q8 pass.

There is one reusable detector session, decode, map, Q8 witness and source ledger.
The standalone A/B/C wrappers each owned Q8; none of those wrappers is called.
Their distinct geometry, mirror, ornament and grid measurements still have costs;
calling them “one check” would conceal that work. Full-page character censuses,
type profiles and general image masks are not runtime dependencies. Lengths retain
track letter-height/page scaling; no runtime code dispatches by page name.

Type supplied a no-Q8 adapter and concave-polygon exclusions. Its 194 unparked-page
replay kept all 15 additions exactly. Geometry supplied `sparse_fast`: independently
checked 195 page dispatches and 9,586 line witnesses, maximum numeric difference
1.2505552149377763e-11; paths/support and decisions match. Source hashes are in
[reuse.json](../../prototypes/fast_lines/stack/reuse.json). Copies live within stack
ownership; no track module was edited. The relay exchanges and shared
[stack board](../../.astra/fast_lines/board/stack.md) record the coordination.

## Measurements

**The sub-second correction target holds on both measured runs; negligible clean-page overhead does not.** All 390 correction timings are below one second. On agreement controls the paired median overhead is 12.857% / 12.543% of Paddle file-to-lines time. Even after the tail fix, roughly 20 ms median and 41–49 ms p95 are material extra work. No latency promise is made for unseen pages.

All times below are milliseconds, shown as **median / p95 / max**, separately for each repeat. Full floating-point values and every page are retained in the receipts.

| Cohort | n | Repeat | Paddle file-to-lines | Added corrections | Final file-to-lines |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 | 1 | 162.326 / 214.133 / 221.794 | 20.400 / 48.545 / 51.689 | 181.795 / 256.500 / 266.600 |
| Agreement | 40 | 2 | 162.499 / 190.368 / 229.310 | 19.910 / 40.811 / 50.744 | 184.350 / 229.361 / 264.700 |
| Discrepancy | 101 | 1 | 170.010 / 258.198 / 290.048 | 40.328 / 371.628 / 688.609 | 226.254 / 542.397 / 922.662 |
| Discrepancy | 101 | 2 | 161.273 / 255.795 / 314.431 | 38.132 / 365.389 / 653.701 | 206.013 / 528.826 / 889.406 |
| Pages with corrections | 52 | 1 | 171.044 / 255.373 / 261.320 | 111.436 / 455.750 / 688.609 | 299.108 / 653.395 / 922.662 |
| Pages with corrections | 52 | 2 | 163.517 / 253.327 / 262.880 | 105.435 / 419.720 / 653.701 | 298.275 / 633.638 / 889.406 |
| All supplied | 195 | 1 | 167.163 / 255.050 / 290.048 | 31.765 / 280.884 / 688.609 | 206.636 / 477.317 / 922.662 |
| All supplied | 195 | 2 | 163.436 / 251.913 / 314.431 | 30.805 / 268.807 / 653.701 | 197.382 / 474.634 / 889.406 |

Both worst discrepancy correction times are `s2-49598b2e848ab1f0ee1e-p00005` (688.609 / 653.701 ms). Its first-run type stage is 532.077 ms, geometry including curved cuts 116.992 ms. The cost comes from conditional recovery and refinement. Agreement maxima are `an-db97e3dd59ca-p000042` (51.689 ms) and curved `s2-3229200bf47ca465a42d-p00002` (50.744 ms). The db97 first-run cost comprises 16.894 ms Q8 scout and 29.689 ms ink, so residual negative checks remain a target.

The agreement median stage costs (repeat 1 / 2) are: Q8 scout 12.412 / 11.898 ms; ink 3.327 / 3.617 ms; geometry scout 3.190 / 3.141 ms; type 0.892 / 0.907 ms. Medians of stages need not sum to a median total. Detector-session startup is 21.719 / 19.630 ms separately; module imports/process startup are outside those startup numbers. These are warm-session, likely warm-filesystem measurements on macOS 26.5.1 arm64 while the other agents were active, not cold-cache guarantees.

The fixed allowlist is 54 development + 40 agreement + 80 discrepancy + 21 extra
discrepancy pages. The discrepancy table pools the latter 101. The same 195 images
are used in both repeats, reversing order in the second run. OpenCV and ONNX use
one thread. One explicit untimed detector warmup precedes each run. The reported
per-page total starts at opening the image file and ends with final polygons;
serialization, drawing and startup are excluded, startup separately recorded.
`paddle_file_s` is decode + original detector inference/postprocess within the same
run; `correction_s` is the paired added cost. This avoids subtracting unrelated
wall-clock runs on a Mac shared with three agents. Raw per-page times, environment,
image hashes, model hash and a frozen Python source tree accompany each repeat.

The 40 agreement pages are controls, not error-free truth: `s2-3229200bf47ca465a42d-p00002`
is visibly curved and acquires one justified reshape. The other 39 retain their
Paddle polygons. There is no PDF text-layer reference and no held-out access.

## The 305 ms ink tail

The initial combined run reproduced the tail on `an-778126cc8c2b-p000011`:
294.383750 ms added cost. This was not geometry, image decoding or ink ownership.
Independent repeated line profiling put ownership at 0.739/0.688 ms; rejected motif
searches on source 13 took 47.062/45.170 ms, source 11 46.738/47.431 ms, source 14
43.675/43.841 ms, source 12 39.117/39.321 ms and source 10 33.924/34.260 ms. Each
reported “reduced spatial repetition absent”. B's separate cProfile found 1,802
`matchTemplate` calls consuming 201 of 305 ms, with enumeration overhead explaining
much of the remainder. The offending work was negative reduced ornament searching.
The [profile receipt](../../.astra/fast_lines/out/stack/ink-profile-an-778126cc8c2b-p000011.json)
and initial v1 artifacts remain available. These initial single-pass numbers are
not the final repeated timing result.

B replaced that expensive negative nomination with local four-copy recurrence,
using patch correlations and a bounded displacement shortlist. The old reduced and
full template witnesses still make the removal decision. A first FFT/template
shortcut lost real ornaments and B did not ship it. The accepted gate preserved
all final 195-page outputs exactly in this combined run, including all 11 motifs;
this is observed equivalence, not proof of unseen ornament recall.

On the old tail page the complete stack now takes **26.301 / 33.770 ms** of
corrections, with **16.839 / 24.438 ms** in B. The former 305 ms mechanism is resolved
on that page. Positive ornament verification can still be costly:
`an-c99f1c450f55-p000025` spends **533.025 / 480.620 ms** in B. The retained
`motif_costs` records identify every line's nomination/refinement time and reason.
Shared Q8 height is reused only when no Q8 split changed the items; otherwise B
computes its own exact `height_proxy`. Neither map-band height nor type contact
height substitutes for that proxy.

## What the corrections contribute

| Operation | Count | Pages | Combined observation |
|---|---:|---:|---|
| Q8 printed-rule cuts | 308 | 18 | All original Q8 pieces survive unchanged or are explicitly removed by B. |
| A curved-rule cuts | 92 | 3 | 16 on 4959 p5; 55/21 on 661d p5/p9; front column rules produce separate rows. |
| A curved reshapes | 30 | 11 | All pass the surviving-ink conservation guard; no losses hidden by deleted neighbours. |
| B back-print removals | 61 | 3 | 56 on 0ce9 p1, four on 31f40 p1, one on 93f807 p1. |
| B ornament removals | 11 | 10 | Repeated headpieces/strips removed; drop capitals retained. |
| C additions | 15 | 13 | All 14 type-only additions remain, plus a newly available 4959 p5 row. |

52 pages change. Starting with 13,639 Paddle items, 400 cuts, 72 removals and 15
additions produce 13,982 final polygons. Geometry reshapes do not change the count.
Counts are not counts of correctly segmented real lines.

The new interaction is `s2-49598b2e848ab1f0ee1e-p00005`: after five reshapes and
16 curved column cuts, the type grid recovers the real left-column row beginning
“πληθὺς τῶν ἡμεδαπῶν καὶ ξένων μηχανικῶν”. The crop ends before the printed
separator. Type independently inspected the same raw crop and agreed it is real left-column text ending before the separator. Its letter/mark boundary is still imperfect. No page-specific rule was
added to get it. B removal footprints overlap none of the 15 final additions.

## Visual review, remaining failures and regressions

Every one of the 195 final page overviews was inspected against visible print;
all 15 added lines also received raw/after crop inspection. Selected changed pages
were enlarged. The complete ledger records a page-specific observation for every
page. This is not exhaustive glyph-level adjudication of 13,982 polygons. Existing
track reports provide their deeper raw crop reviews; agreement with either detector
is never treated as truth.

No new composition regression was observed in that review scope. Known bad geometry,
incomplete recovery and false positives remain; “unchanged” is not “correct”. In
particular:

- `s2-86865c33eef5932c013b-p00005` remains badly fragmented at the curl. On p7 two
  recovered rows are real, but right ends and an unbracketed missing row remain;
  p23 is an agreement page with visibly imperfect curved geometry.
- `s2-3229200bf47ca465a42d-p00002` gets one useful reshape, but many boxes still
  straddle rows. p3 stays wrong; p4/p6 improve only selected contours.
- `an-d83e7a198ade-p000099` retains overlapping/multirow apparatus boxes despite
  one reshape; `an-d3237d690aa0-p000138` dense index fragments remain (full identifiers in ledger).
- `s2-0ce9d1025b3f23c7119e-p00001` loses the 56 accepted mirrored boxes but retains
  short ghost boxes at the top and elsewhere. `an-ef481610a820` p150/p151 retain
  mirrored/stamp fragments, and p181 remains unchanged. No broad mask was allowed
  to erase nearby text.
- `an-00f143ecce59-p000192` still misses bottom body text; p258 retains tall/drop-cap
  problems. `an-466cffad2cba-p000277` leaves the first body row below its initial unboxed.
- `an-778126cc8c2b-p000007` recovers a true row overlapping a stamp. Stamp exclusion
  is unresolved. `an-c99f1c450f55-p000046` recovers a true row whose envelope touches
  the lower part of the preceding drop capital B.
- The 4959 and 661d newspaper pages improve substantially, but dense multirow and
  cross-column joins remain. `s2-d12a9a4feb23254f4080` p8 abstains on a tight curved-rule corridor.
  `s2-93f8070059f938bda524-p00001` correctly does not turn its back rule into a front
  separator, leaving the corresponding layout difficulty unresolved.
- `s2-63c4d6b9e02507b34a10` p4's dot-leader/table layout is incomplete. Arabic joined-script
  fragments and physical-leaf boundaries remain unresolved. Orientation is parked;
  the designated `s2-6419488b7f8e69fd20da` p1 and sideways `s2-7534648e60694be1d180` p16 receive no rotation.

All full page identifiers and observations are in the tracked ledger, including
otherwise clean-looking controls. No aggregate accuracy or generalization claim is
made; the 44 held-out pages were neither searched for nor inspected.

## Readiness and validation

The one-entry composition, stable source provenance, permanent removal vetoes,
quad-only grid view and owned snapshots are ready as a prototype module. The
printed-rule, geometry, ownership, ornament and recovery operators retain their
track-specific limitations. Production adoption still needs independent held-out
review and a decision about the measured clean-page overhead. Unreadability,
causal inkiness, watermark/stamp separation, general image rejection and severe
curl recovery are not finished by composing the tracks.

**97/97 prototype tests pass** (90 pre-existing plus seven stack integration tests).
The final export audit passes **16,788 assertions on 195 pages**: image identity,
fresh Paddle equality, valid detector-format polygons, null semantic baselines,
no discounted output, original-source accounting, every Q8 piece accounted for,
zero accepted geometry ink loss, no addition intersecting a removal, both timing
receipts and completed page observations. The second fresh run enforces exact
final-item equality page by page. All 195 final exports also match the separately
reviewed initial v1 exports exactly, so the visual ledger transfers without an
unreviewed output change. The public import and single-image CLI were smoke-tested;
the exported line list matches the batch result.

No production `greekocr/pages/` source or tests changed, and importing stack loads
no production page module. No push or background job was started.

The sandbox blocked staging with `index.lock: Operation not permitted` in this
worktree's Git metadata. No commit or push was made. The requested fallback is
[validated patch](../../.astra/commit-Fstack.patch) and
[commit script](../../.astra/commit-Fstack.sh), with exact file hashes and both
required trailers. The script checks branch, base commit and unchanged files before
staging only the stack directory and this report.
