# Round 6 B: rows inside an OCR segment

Task B starts from `cd1e52f`, with task A's relative faintness stage merged. It partitions **70 polygons into 140 children on 18 of 208 pages**. Forty-three owner-marked two-row polygons change; all 97 marked single-row polygons remain exact. The new operator partitions a polygon along an observed gap between rows, conserving its vector area. The parent polygon and original detector source IDs remain attached to every child so task C can replace these provisional partitions with a page-level field. Integer rasterization has a separate boundary limitation documented below.

This is a partial result. A split can separate two rows while leaving a third clipped fragment in a child. Splitting also cannot reconstruct the letters the old rectangle already clipped, merge duplicate fragments into a full row, or recover an unboxed row. Those distinctions matter when every output segment goes directly to OCR. The output review therefore includes white-masked **before and individual child OCR crops**, not only full-page overlays.

The local outputs are under `.astra/fast_lines/out/round6/B_rows/`. The fixed cohort contains all 208 explicitly supplied pages, including the thirteen review originals. No held-out page, PDF text layer, production `greekocr/pages/` source or production test was used or changed. Task C's page-edge curvature field has not been started.

## Explicit rows, before the heuristic

The slow rendering samples the native image in a segment-aligned strip, with one height of vertical context. The actual polygon determines which ink can witness a row. Context can expose a clipped glyph or an adjacent line, but cannot count an outside table cell as another row of this segment. The strip's slope is a straight reference, not an assertion that the row is straight.

Local Otsu ink after a small blur gives connected components. Horizontal density exposes candidate body-centre paths. These are **ink ridges, not measured baselines**, and multiple paths can be different words on one row. A qualifying horizontal run contains neighbouring complete body components. A row pair needs overlapping horizontal support and vertical separation. The rendering shows complete bodies, clipped bodies, qualified runs, other contextual ridges, nearby mark-to-body connections, accepted valleys and rejected valley proposals separately.

The valley follows empty space between two observed rows using a constrained minimum-cost path. It must preserve connected ink and nearby detached marks; a supported native row cannot change sides of the cut. An empty gap is stronger evidence than a low average ink density: otherwise a path can cheaply cross one small accent. Every resulting piece must retain a horizontal body run. The vector partition has no erased gutter and introduces no new page area.

Printed table rules need separate treatment. A tall stroke is not automatically a glyph or a rule. The operator reuses round 2's native `verify_rule`, observing the stroke beyond this segment before allowing a cut across it. It does not use an unverified aspect ratio to excuse cutting a letter. Neighbouring table entries still cannot supply the two internal word runs. Tall polygons remain unknown because a stack of numbers and a rotated label are not distinguished reliably here; orientation remains parked.

### Scale and limits

The unit `h` is the existing detector-derived height proxy: half the median short rectangle dimension, with a page-relative floor. It is not a certified x-height. Body candidates span `.45h–1.8h` vertically and `.08h–3h` horizontally, with area at least `.018h²`. A run needs at least two complete components, horizontal extent `1.2h`, and intercomponent gaps no greater than `h`. Detached marks smaller than `.45h` vertically are coupled to nearby bodies; ambiguous similarly near bodies can veto a split. All thresholds describe the explicit local construction, not OCR character identities or an unseen-page guarantee.

The native density uses horizontal sigma `.65h`, vertical sigma `.12h`, and path samples `.5h` apart. Peak separation is at least `.7h`; the bounded valley stays more than `.25h` from either ridge. Its dynamic-programming grid uses `.25h` horizontal and `.08h` vertical steps, with pixel discretization floors. The original 3×3 sigma-.6 blur is an image estimator setting. Heavy joining, unusual fonts, very small apparatus relative to the page scale, and incomplete clipped letters remain weaknesses.

## Prediction, test, inspection

| Cycle | Prediction and visible failure | Result |
|---|---|---|
| Native v1–v2 | Density paths would expose rows inside the polygon. Separate words on one row produced several paths; initial review indices also shifted after A's unrelated removals. | Require a vertically separated overlapping pair; map owner records by exact polygon, retaining their original R5 indices. |
| Valleys v3 | A low-density inter-row path would give the split. It could cut a large initial excluded by the ordinary body filter. | All components participate in the cut guard, including oversized initials. |
| Native v4–v5 | Complete bodies would distinguish table neighbours. Scattered complete descenders could still masquerade as a word. | Require a neighbouring horizontal body run, not arbitrary complete components spread along a row. The five provisional owner-one positives disappear. |
| Fast v5–v7 | Local peaks would be cheap nominations. Accents and holes within letters nominated almost every segment, making clean-page cost unacceptable. | Use body-width bands and an intervening low-ink gap in short longitudinal blocks. These still nominate; they cannot authorize a cut. |
| v8–v11 | A continuous valley and conditional native windows would improve both geometry and cost. Printed rules blocked genuine table cuts; single-body compact mode split vertical labels and ornaments. | Reuse native rule verification; remove the single-body shortcut and require a horizontal body run in every piece. |
| Actual OCR crops v11–v12 | The full-page overlay looked plausible, but `49598…p1`, A index 89, moved the final word into the upper fragment. `a73d…p47`, index 23, transferred detached accents. | Add native-row side consistency and explicit mark/body connections. v12 abstains on both. The later empty-space path restores the first split with its final word still in the lower row; the accent case remains unchanged. |
| v13–v14 | Hard empty-space costs should route around marks before abstaining. An intermediate finite-cost corridor bug was exposed. | Make the corridor strictly more expensive and explicitly verify the final path remains inside it. v13 is not a final result. |
| Sampling v15–v16 | Sparse interpolated samples should avoid reading every source pixel for the scout. Its apparent lost positive, `7534…p16`, index 2, was actually the rotated label `Έσοδα`. | Treat tall polygons as unresolved, including narrow numeric stacks. Use sparse sampling followed by native confirmation; no orientation classifier or new image-removal rule is introduced. |

All exploratory outputs remain in their named directories. Their timings are not the final stack measurements. In particular, the 99 v5 and 111 v11 proposed partitions include failures discovered later; they are not success counts.

## Both routes and the installed path

Route 1 renders the same components, ridges and valley at a reduced 20 pixels per height. It is a diagnostic alternative. Reducing the image changes component connections, clipped-body decisions and thin marks, so it is not accepted as a stand-alone splitter.

The installed fast explicit path keeps native pixels but first measures only windows nominated by route 2. A window that contains no two qualifying runs ends the investigation. When the nominated window covers the whole segment, its native extraction is reused as the full check. Otherwise, only a positive window requests the complete native valley. This is localization of the explicit feature, not an independent learned classifier.

Route 2 samples the page at eight pixels per height, intersects each profile with the actual polygon, and compares body-width vertical bands in approximately `4h` longitudinal blocks. Two separated bands with an intervening gap nominate native inspection. Quantizing insignificant floating profile noise stabilizes peak ties. Sparse point sampling is deliberately a lossy scout; per-segment disagreements against the native rendering are exported, including negatives and every missed nomination. No overall score is used as a substitute for that ledger or the crop inspection.

## Integration and retained contracts

`shared/geometry_rows.py` exposes `render`, `scout`, `native`, `confirmed_partition` and `analyze`. `Stack` calls `analyze` once, after the final geometry and task A. Every task-A removal remains the same polygon with the same reason, including `relative faintness`. No stamp disk, broad mask, new exclusion or restored footprint is introduced.

Children retain score, `source_ids` and other source metadata. `row_parent_polygon`, `row_parent_index` and `row_piece` give task C an explicit replacement ledger. An old centreline is removed from children; it cannot describe both rows. Baselines remain null. The row stage adds no claimed text confidence. Review numbering remains a separate reading-order mapping.

The operator uses live shared imports for scale, clipping/coordinates, native rule verification, detector JSON and review rendering. There is no copied runtime stack or ink/type implementation. The existing Q8, ink, type, fragment and curvature operators remain active; task B does not make the page-level work of task C redundant.

## Final comparison and the owner's segments

The final census covers **15,131 retained input segments on 208 pages**. Native and reduced renderings are saved for every page; every segment has its own comparison record.

| Native partition | Reduced partition | Segments |
|---|---|---:|
| No | No | 15,038 |
| Yes | Yes | 58 |
| Yes | No | 18 |
| No | Yes | 17 |

Among the 58 common positives, the median of segment-median cut differences is `0.025445h`; the largest sampled difference is `0.484415h`, on `s2-032eaf8e6b3b83918feb-p00004`, A index 29. Small average differences do not certify a safe cut. On `an-c8b96a901917-p000163`, A index 70, the reduced rendering interprets part of a single accented word as another row and proposes a cut through it. It is not installed. Reduced sampling also loses native valleys in `3229…p2/p4/p6/p8` as component and detached-mark connections change. Route 1 remains diagnostic.

The scout nominates 875 segments. It misses **zero native-positive proposals on active pages**, but native confirmation in its limited windows loses five proposals present in the full native rendering: `4959…p1` indices 75 and 97, `4959…p4` index 85, `7a2…p200` index 287, and `c3cc…p2` index 1. The numeric example is a real stack of rows; its narrow window triggers the unresolved-orientation guard. A sixth native proposal, `6419…p1` index 29, is on an already parked page and is not installed. Thus 76 native proposals yield 70 installed parent partitions. This agreement with the explicit rendering does **not** establish recall against all real multi-row segments: the rendering itself misses many.

| Owner's R5 mark | Partitioned | Unchanged |
|---|---:|---:|
| Two or more rows | 43 | 116 |
| One row | 0 | 97 |
| Unmarked record | 0 | 62 |

The 256 marked and 62 unmarked records retain their original mark, R5 polygon/index, task-B input index and final reading-order numbers in `owner-marks.json`. These are matched by polygon, not by a shifted integer index. Of the 116 unchanged two-row marks, 61 lack two complete word runs in the nominated windows, 40 fail the full valley/partition checks, 14 have no broad separated-band nomination, and one is parked. These are recorded abstentions, not declarations that the owner was wrong.

Thirty-eight of the 43 changed marks are in the three named curved books. The supplied ledger currently contains 102 two-row and ten one-row records for those books; 64 of those two-row records stay unchanged. This is the ledger count, which differs from the brief's earlier 100-of-110 subtotal. No `86865…` polygon is split by B; the severe curl there remains open.

### What the OCR crops show

All 70 final before/child crop sets were inspected, together with native/final overviews of all 208 pages and all 40 native/reduced or native/window disagreement crops. The complete viewed-file lists and observations are in `visual-review.json`. All 70 cuts separate visible ink from different rows; the final crop review found no recurrence of the v11 wrong-word transfer. This is visual inspection, not an OCR recognition benchmark or a proof of every character's ownership. Not all 318 owner crops were individually inspected at full size; all are exported, and changed marks are included in the 70 inspected sets.

Important residual failures are visible in the actual output children:

- `an-a73d22211479-p000301`, A indices 56 and 57: each original contains about four rows. A single gap gives two children; index 56 still has two rows per child, and index 57 leaves several rows in its lower child. These are partial partitions, not repaired single-row OCR inputs.
- `an-7a2b17a3fb0f-p000200`, index 282: two complete numeric rows separate, but clipped neighbouring row fragments remain. Index 287 is conservatively unchanged because the narrow confirmation window is ambiguous.
- `3229…`, `4959…`, `c3cc…p2`, `032e…p4` and `44b5…p1/p2/p3`: many main children retain clipped words or part of another row. The parent polygons already cut across the curved print; B preserves their outer boundaries and therefore cannot repair that clipping.
- `an-a73d22211479-p000047`, index 23: the accent-ownership counterexample remains unchanged. `4959…p1`, index 89, now has a valid empty-space path with the final word retained below it.
- `an-7a2b17a3fb0f-p000012`, index 2: the partition does not remove the stain. Joined-script components and tiny apparatus also remain weakly modelled; a horizontal run of complete body components is too restrictive in some true rows.

### Vector conservation and the raster boundary

Every changed parent equals the vector union of its children within `1e-6` square pixels; children have no positive-area overlap. Every unchanged segment is exactly the task-A item. However, rounding the new polygon intersection vertices for OpenCV masks changes the sampling of some existing outer edges. Across 70 parents the union of child masks loses **1,099 pixels**, gains **1,046 pixels**, and changes **178 locally Otsu-classified ink pixels**. All differences lie in the parent's one-pixel boundary neighbourhood. The audit also counts **92,877 shared cut-boundary pixels** drawn into both child masks; zero vector overlap does not imply disjoint integer masks.

Consequently this work claims vector conservation, **not pixel-exact OCR crops**. The native cut guards also have finite tolerances and a thresholded ink model. A downstream rasterizer should assign each shared boundary pixel once and preserve the parent's mask explicitly if exact pixel ownership is required. No production OCR rasterizer was changed in B. `raster-audit.json` records each parent separately.

## Fresh stack timing

Two fresh public `Stack()(page)` passes ran over all 208 pages, first forwards and then backwards, with fresh decode and Paddle inference. All 208 outputs were exactly equal between passes. The original detector output, inherited operator counts, and complete task-A removal ledger were also checked against the frozen A exports. Rendering and writing review artifacts are outside the timers. All runtime dependencies are inside the B or whole-correction timers; no cached native rendering supplies the runtime.

Milliseconds below are repeat 1 / repeat 2. The complete discrepancy set includes the manifest's 80 `discrepancy` plus 21 `discrepancy_extra` pages; the forty agreement pages are reported separately. These labels describe detector agreement, not verified absence of errors.

| Cohort and stage | Median | p95 | Maximum |
|---|---:|---:|---:|
| 40 agreement, B scout | 2.882 / 2.989 | 4.036 / 4.053 | 4.546 / 4.307 |
| 40 agreement, complete B | 3.145 / 3.175 | 31.014 / 31.333 | 239.845 / 235.598 |
| 40 agreement, all corrections | 30.075 / 26.116 | 69.420 / 68.476 | 312.799 / 316.849 |
| 101 discrepancy, complete B | 7.108 / 7.299 | 84.851 / 83.414 | 610.256 / 582.315 |
| 101 discrepancy, all corrections | 126.591 / 118.789 | 597.696 / 597.518 | 1511.663 / 1430.429 |
| All 208, complete B | 5.860 / 5.710 | 159.233 / 150.021 | 610.256 / 582.315 |
| All 208, all corrections | 92.334 / 88.592 | 551.023 / 548.404 | 1511.663 / 1430.429 |

The agreement B tail is `s2-3229200bf47ca465a42d-p00002`, where B partitions seven parents. The largest B and whole-correction costs occur on `s2-49598b2e848ab1f0ee1e-p00005`. The full correction pipeline exceeds one second on three pages in both passes (six of 416 calls): `4959…p1` at 1127.464 / 1115.587 ms, `4959…p4` at 1154.686 / 1154.454 ms, and `4959…p5` at 1511.663 / 1430.429 ms. **The negligible-overhead and strict subsecond targets remain unmet.** The standalone B stage stays below one second, but that does not satisfy the combined target.

## Artifacts, checks and handoff

- [Final 208-page gallery](../../../.astra/fast_lines/out/round6/B_rows/final-v16/index.html), with detector-format JSON, numbered images, per-segment comparisons and scout/route panels.
- [Native and reduced renderings](../../../.astra/fast_lines/out/round6/B_rows/native-final-v16/) and [legend / reproduction commands](../../../.astra/fast_lines/out/round6/B_rows/README.md).
- [All owner row records](../../../.astra/fast_lines/out/round6/B_rows/final-v16/owner-marks.json), [73 retained comments](../../../.astra/fast_lines/out/round6/B_rows/final-v16/COMMENTS.md), and [visual review receipt](../../../.astra/fast_lines/out/round6/B_rows/final-v16/visual-review.json).
- [Both timing passes](../../../.astra/fast_lines/out/round6/B_rows/final-v16/timings.json), [all 101 discrepancy pages](../../../.astra/fast_lines/out/round6/B_rows/final-v16/discrepancy-timings.json), and [raster audit](../../../.astra/fast_lines/out/round6/B_rows/final-v16/raster-audit.json).

The prototype suite passes **201/201 tests**, including eleven new image/geometry tests and the stack order contract. Export and detail validation perform **35,342 checks** (32,584 plus 2,758), including all 1,252 gallery links, comment links, 2,064 image decodes, source/receipt checks, exact unchanged items, child ancestry and vector conservation. These check counts are assertions, not additional independent test cases.

Both timed passes have source signature `18211feb0d1a49cb211fc8580d413123041a282163912a39f610ebfbbf450f80`. After the freeze, only the offline review script and documentation were extended; the source ledger verifies the runtime remains unchanged. The final handoff receipt records the current file hashes and commit or patch disposition. Outputs remain outside git.

Git staging was attempted and denied when creating `.git/worktrees/greek-ocr-toolkit-fl-geometry/index.lock` (`Operation not permitted`). No commit or push was made. The requested fallback is `.astra/commit-FB_rows-r6.patch`, executable `.astra/commit-FB_rows-r6.sh`, and `.astra/commit-FB_rows-r6.validation.json`, based on `cd1e52f4ff7c2addb06fc99b8b226c5937b9de58`. The patch contains only the nine task-B code/document files; the script verifies the base and file hashes before staging and commits with both required trailers. Forward/reverse application, byte equality and script syntax are checked in the validation receipt.

## Remaining work

The page-level field should replace these provisional cuts wherever it can identify complete parallel rows. It must use the saved parent polygons and permanent A exclusions, then rebuild full rows instead of accumulating duplicate fragments. Dense apparatus needs a defensible local body scale and ownership of connected/overlapping marks. Tall numeric stacks need horizontal-row evidence independent of rotated text. A post-partition faint fragment may merit task A's analysis again, but B does not silently create a new faintness rule.

The original owner comments about missed endpoints, missed lines, decorations, stains and columns are not claimed fixed by a vertical partition. Existing A/R5 outcomes are retained and identified separately. The row-owner ledger is the relevant per-segment comparison for this task.
