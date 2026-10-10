# Fast line finding, round 4: combined stack

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
