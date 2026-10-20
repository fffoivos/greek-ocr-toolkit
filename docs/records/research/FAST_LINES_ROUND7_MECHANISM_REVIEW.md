# Round 7 Task 1 — independent mechanism review

The useful physical ideas are present, but the installed stack is not one page model. It repeatedly reconstructs components, row paths and ownership, then uses vetoes and polygon subtraction to reconcile conflicting answers. **Keep the approved separator and ink evidence; replace the competing geometry/recovery models with region-scoped, jointly ordered row bands before porting the runtime to Rust.** Do not port the current dictionary/version/guard structure unchanged.

**Scope:** independent Task 1 review of `astra/ff-review` at `5783cec` on 11 October 2026. No implementation edits under `prototypes/` or `greekocr/`, no other agents, no unseen 44-page data, and no implementation of Tasks 2–4. The companion [machine ledger](FAST_LINES_ROUND7_MECHANISMS.json) has one record for each of **41 mechanisms**, including shared primitives and orchestration; it embeds function-level measurements, all numeric-source-line inventories, source hashes, all comment mappings and the target contracts.

## Findings that change the next task

1. **Region separation must precede the bend.** The inspected `an-e259bbf5081c-p000198` and `an-c8b96a901917-p000068` bend drawings fit across independent columns/leaves. A relative row-phase offset is then interpreted as curvature. A positive Jacobian prevents a folded mesh; it does not prove the mesh describes one leaf.
2. **A correct bend does not certify the rebuilt bands.** On `8686…p5`, the native per-row rebuild still applies the `.75h` nearest-axis test and the later selector rejects all linked groups. The exact census is 38 proposals, 36 late decision groups and 2 unowned proposals. The quoted four rejection-reason counts sum to 36. On p7, 9 early and 4 late replacements account for the 13 accepted proposals. Unowned proposals are never recovered by the selector.
3. **Trace the actual final segment before blaming a stage.** The bad bottom segments on `44b5…p2` and `4959…p5` are original Paddle descendants after column/curved-separator clipping; they are not accepted `page_field` polygons. `44b5…p2` #123 also has `duplicate_clipped=True`. This does not absolve the shared row model: it must repair inherited multirow boxes as well as its own candidates. It does mean “the field rebuilt these particular bands badly” is not established by the final provenance.
4. **The normal-run critique needs precision.** Current `normal_run` already requires three whole components. Separate `short_ambiguous` and normal-area guards can preserve a segment with no such run. A connected dark mass can therefore retain a ghost row. Removing those guards blindly would also lose legitimate short words, handwriting and touching front glyphs. The supplied known-front synthetic controls remove four of five front examples; they do not validate faint front text in a real line.
5. **Faintness must constrain endpoints, not only line deletion.** `8686…p26` #9/#40 and `93f…p1` #5 are field-owned segments extended over faint words. A real normal phrase inside them properly prevents whole-line deletion. Geometry needs the same calibrated component evidence to stop the endpoints.
6. **Short, last and initial-adjacent rows need an independent false-negative route.** The inspected newly relayed rows on d83 p99, ef481 p181 and 00f143 p258, and ffccc p354’s last word, remain missed. A five-body/4h–5h rule cannot be a universal definition of a line. Conversely `c0b…p10` #118 is present in R6 and absent from a fresh Paddle-only tile: keep it as a successful recovery control.
7. **Exact output parity protects the baseline, not its accuracy.** All 208 canonical polygon lists and all 208 stage-count records match R6. All 73 older comment page overviews were rechecked, with targeted current crops below. The 256 row-mark dispositions are retained, not presented as a new full-detail visual grading: 97 one-row marks retained; of 159 two-row marks, 25 fixed, 45 partly, 88 not fixed and one parked.
8. **Rust is not the first remedy for the latency.** Removing repeated interpretation and native work is more consequential than translating loops. Preserve the physical renderings as references while deleting superseded installed paths; do not delete the reference evidence merely because it is off the hot path.

## Evidence, reproduction and limits

- Runtime source signature: `071d0d2dcfe24e68e848a3f0c4eb771452871016742b45af840f9a002e37432f`. All **215** source files match both `source-r1.json` and `source-r2.json`; the two source receipts are identical.
- Model SHA-256: `b338e02bf836b2ff90e2faae6ed2d966c3a57b98affcab3e1969de59457ff036`. All **208 image hashes** match the supplied R6 receipts. The only adaptation was supplying the existing model path at runtime; no detector/preprocessing/threshold code changed.
- Fresh measurement: `.astra/r7_task1/profile_review.py`, then `analyze_review.py`; one warmed reusable `Stack` called on each receipt-bound page under `cProfile`, with bytecode disabled. No concurrent or background workload was launched. Per-function calls and inclusive/exclusive times are in the ledger; native library time is included in callers but not decomposed inside C/ONNX kernels.
- Authoritative uninstrumented latency is the **two supplied R6 passes**, reaggregated from per-page receipts after the source/model/input checks. The new profile has observer overhead and is used to attribute work, not to claim a new release benchmark. Quantiles include zeros for inactive stages and the parked page; p95 uses NumPy’s default linear percentile.
- Environment for the fresh profile: Python 3.11.3, NumPy 2.4.6, SciPy 1.17.1, OpenCV 5.0.0, Shapely 2.2.0, ONNX Runtime 1.31.0, macOS-26.5.1-arm64-arm-64bit. OpenCV reports **10 threads** despite the request for two; ONNX is sequential with one intra/inter-op worker. These are observations on this Mac, not bounded-worker guarantees.
- Raw Python polygon equality initially differed on 20 pages. All 20 match through the existing `detector_record` exporter and have zero coordinate overflow; this is tuple/list normalization, not geometric drift. The full output contains **15, 152 final segments**. The exporter is outside `Stack`; canonical representation and bounds belong in the target core contract.
- Visual scope: 13 contact sheets covering the 73 old comments; 24 targeted raw/final crops using the owner’s exact reading order; two rejection drawings, two false-region bend drawings, and a fresh Paddle-only comparison for c0 p10. These were inspected, not merely generated. This is not a fresh detailed visual inspection of every 208-page output or every 256 owner crop, nor an OCR recognition benchmark.

Local evidence roots (named explicitly because ignored `.astra` artifacts are not part of this documentation commit):

- Owner: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines`; read `review_r6/COMMENTS_CHECKED.md`, raw notes, `reading_order.py`, `review_r4/REVIEW.md`, all 318 raw row records (256 marked, 62 null/control), and the bend renderer/208-page summary.
- Frozen R6: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r6`; per-page `.json`, `.evidence.json`, `.r1.json`, `.r2.json`, source receipts, all 73 comment dispositions, 256 row dispositions, `RECOVERY.md`, `TIMING.md` and faint-front controls.
- New read-only diagnostics: `.astra/r7_task1/` in this worktree. The ledger embeds measured aggregates, per-page counts/hashes, the function-to-mechanism map and script hashes so the numerical findings do not depend solely on untracked screenshots.

Historical method evidence is in [FEATURES_A](FAST_LINES_FEATURES_A.md), [FEATURES_B](FAST_LINES_FEATURES_B.md), [FEATURES_C](FAST_LINES_FEATURES_C.md), [R6 faintness](FAST_LINES_ROUND6_A_FAINTNESS.md), [R6 rows](FAST_LINES_ROUND6_B_ROWS.md), [R6 curvature](FAST_LINES_ROUND6_C_CURVATURE.md) and the current [stack report](FAST_LINES_STACK.md). Their reported visual checks are historical claims, distinguished below from my current inspections. Standalone track counts and older early-field ordering must not be substituted for the final integrated source.

Reproduction uses the supplied interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python .astra/r7_task1/profile_review.py
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python .astra/r7_task1/analyze_review.py
```

`profile_review.py` intentionally refuses to overwrite its existing JSONL; use a separate output directory for another pass. Model initialization/warmup are outside per-page latency; decode, original inference and every triggered dependency are inside the call.

## Cost and activation census

All values below are **median / p95 / maximum milliseconds**. Parent and child timers overlap; neither medians nor maxima are additive.

| Population and scope | R6 pass 1 | R6 pass 2 |
|---|---:|---:|
| All 208 corrections | 189.438 / 1372.439 / 2393.061 | 187.094 / 1386.783 / 2379.603 |
| All 208 complete file-to-segments | 330.361 / 1543.114 / 2586.505 | 332.065 / 1564.698 / 2573.394 |
| Agreement 40 corrections | 62.336 / 564.354 / 673.740 | 61.808 / 561.108 / 677.147 |
| Agreement 40 complete file-to-segments | 214.034 / 695.938 / 824.255 | 210.471 / 692.230 / 836.217 |

There are **21 / 22 pages with corrections at least one second** in the two passes. Agreement pages are an overhead control, not proof of flawless base detections. The charter’s negligible clean-page overhead and under-one-second corrections target is not met.

| Major correction stage | R6 pass 1 ms | Interpretation |
|---|---:|---|
| Rule scout | 5.788 / 8.820 / 9.491 | 207 active pages; primitive reused |
| Ink parent | 10.396 / 131.265 / 420.564 | Mirror, seal, connected/discrete motifs included |
| Edge-map scout | 4.188 / 13.315 / 26.766 | 73 triggers |
| Shared field/proposal parent | 0.000 / 619.527 / 920.783 | Native preparation, mesh, 44 regional inferences and band rebuilding |
| Early field selector | 0.000 / 141.673 / 199.540 | 73 calls; changes 38 pages |
| Remaining geometry parent | 4.710 / 82.365 / 274.323 | Nested column/rule timers can refer to earlier cuts |
| Type/recovery parent | 17.183 / 274.130 / 768.098 | Grid, table, residual, confirmation and initials |
| Final envelope smoothing | 0.012 / 83.554 / 222.654 | 40 triggers, 9 changed pages |
| First relative faintness | 3.240 / 51.553 / 127.036 | 93 candidate pages, 31 removal pages |
| Late field selector | 0.000 / 49.517 / 165.958 | 18 calls, 8 changed pages; same proposals |
| B row parent | 5.401 / 91.939 / 379.999 | 108 nominated pages, 18 split pages |
| Duplicate reconciliation | 29.076 / 93.861 / 139.635 | All 207 calls, 30 changed pages |
| Changed-footprint faintness | 0.000 / 27.175 / 52.738 | 26 calls, 3 removal pages |

On the **35 edge-triggered pages with no final field-owned band**, the sum of edge scout + early cuts + proposal + early/late selector timers is 167.592 / 330.310 / 450.025 ms in pass 1 (mean 202.176ms). This is a defined field-work subtotal; other operators may still fix the page. It refines the briefing’s approximate177ms rather than treating “no final field band” as “no page improvement”.

Fresh profile highlights: 363 detector calls, 99 native contact preparations, 479 residual native fields, 956 native row inspections, 1, 185 faintness component extractions, 2, 898 height estimates, 81, 170 axis estimates and 642, 861 bounding-box calls. `reconcile` alone has about 4.3s Python self time across the cohort, plus native filtering/geometry. Component/context reuse and eliminating conflicting models have concrete targets; no Rust speedup is assumed.

## Actual execution order

```text
decode/session -> base Paddle -> DB polygons
rule scout -> conditional Q8 -> mirror ownership -> seal -> motif/discrete removal
edge-map scout
  if triggered: curved rules + columns -> native context/shared field
                -> unbend + Paddle + per-row rebuild -> early field selection
local-map geometry scout/correction
  if no earlier cuts: curved rules + columns
fragment nomination/contact trace/join
type blocks/slots -> native slot/table/ink checks -> regional recovery/guards
uncovered-ink scout -> native body chains -> regional recovery/guards -> initials
envelope smoothing -> page-relative faintness
conditional late field selection (same proposals)
multirow scout/native partition -> duplicate reconciliation
faintness on changed final footprints -> raw Stack result
review exporter normalizes/clips separately
```

The IDs below follow first conceptual use. M03 primitives and M40 orchestration are shared; M12/M13 move with the edge branch; M18 and M34/M35 are revisited. Early selection is invoked on all 73 triggered pages in the checked-in source, not only the 9-page early route described by older C prose.

## Mechanism ledger

Each subsection states the feature, contract, evidence, constants, duplicate/veto structure, alternatives, Rust implications and verdict. A helper does not independently change final polygons: its invocation count is measured, while its parent’s outcome is explicitly shared. No causal ablation or unseen accuracy is claimed. The JSON includes all observed functions assigned exactly once, with their inclusive and self times, plus numeric source lines for every listed module. Numeric inventories expose constants; they do not retroactively justify their calibration.

No runtime mechanism receives a book/page key. The only explicit page exception is the authorized sideways-page flag in the harness. Absence of page-name gates does not establish generalization: thresholds and version branches arose from the development cohort. Several density/overlap fractions function as empirical acceptance gates, in tension with the charter; they need a physical rendering and counterexamples, not another fitted ratio.

### M00 — File decode and reusable session

**Verdict: keep.** Keep an outer adapter; move page computation to an array interface. Keep orientation explicitly out of scope in this round.

**Feature and operation.** Read the page as grayscale; reuse a CPU ONNX session. The harness explicitly parks the sideways page after detection. **Current contract:** Path -> uint8 gray[H, W]; session is external state, not feature evidence. Startup seconds and decoder errors are returned.

**Principle and evidence.** A necessary adapter, not a page feature. The parked orientation is an explicit experimental scope exception; Stack itself receives only a boolean, not a filename. Source and decode receipts, not a heuristic rendering. All 208 supplied image hashes matched.

**Constants and units.** OpenCV requested threads=2 but this build reports 10; ONNX intra/inter-op=1. Startup is outside per-page receipts. No resampling here.

**Vetoes, duplication and routing.** Global cv2.setNumThreads side effect; timing and diagnostics mixed into the return value. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `decode_s` pass 1 23.771 / 92.245 / 107.764ms; pass 2 22.496 / 89.910 / 104.025ms.

**Firing / output changes.** Decode208 pages; session constructed once for the fresh pass; 207 pages composed and 1 explicitly parked. No independent correction decision.

**Alternative.** Accept decoded arrays in a pure core and keep file IO/session construction in a wrapper: cheaper reuse and testable ownership, one extra API. **Delete it:** Delete only the file wrapper if callers supply arrays; deleting decode without a replacement makes the entry point unusable.

**Rust.** image crate or opencv decoder; ort session wrapper. An image crate decoder is a candidate, not a promise of identical grayscale conversion. **Behavior to pin:** PNG decoder/grayscale semantics, thread build and ONNX startup must be pinned; warm and cold timing are different.

**Sources:** [stack/pipeline.py](../../../prototypes/fast_lines/stack/pipeline.py#L1). **Current comment links:** O26.

### M01 — Paddle preprocessing and inference

**Verdict: keep.** Keep the base detector and content-pinned model; make regional reruns exceptional after Tasks 2 and 3.

**Feature and operation.** Resize, normalize and infer a text-likelihood map; used once on every page and again on rectified or recovery crops. **Current contract:** uint8[H, W] -> contiguous float32[1, 3, Hn, Wn] -> float32[Hm, Wm], with explicit scale metadata.

**Principle and evidence.** A learned localization prior deliberately allowed by the charter. Its map is not ink darkness, a baseline or calibrated foreground ownership. Paddle/final overlays supply localization evidence; both detectors can be wrong. Repeated regional inference is visible in the 208-page call census.

**Constants and units.** 960-pixel maximum side; dimensions rounded to network multiples of 32; ImageNet mean/std and CPU sequential execution. Recovery chooses side from 16 samples per local height.

**Vetoes, duplication and routing.** 363 inference calls: 208 base + 44 unbent regions + 31 grid crops + 80 residual crops. Crop calls are already inside their parent correction timers. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `inference_s` pass 1 120.472 / 137.432 / 162.910ms; pass 2 119.016 / 133.978 / 163.963ms.

**Fresh profile.** `shared/detector.py:26:infer`: 363 calls on 208 pages; inclusive 128.598 / 309.953 / 453.052ms over 208, self total 66.206ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** Base inference208/208; 155 extra regional calls. Produces a localization map, not a correction decision.

**Alternative.** Use the existing map plus native row support for geometry, requesting another inference only for an unresolved unowned region: saves 155 crop calls if fully successful, but must prove short-row recall. **Delete it:** Deleting the base detector removes the starting localizer. Deleting all reruns saves time but loses confirmed recoveries unless the row model supplies their evidence.

**Rust.** ort binds ONNX Runtime; preprocessing can be plain loops/ndarray and explicit interpolation or OpenCV initially. This is not a pure-Rust inference implementation. **Behavior to pin:** Bilinear resize, round-to-32, normalization precision, model/backend version and summation order can move threshold crossings.

**Sources:** [shared/detector.py](../../../prototypes/fast_lines/shared/detector.py#L14), [shared/paddle_db.py](../../../prototypes/fast_lines/shared/paddle_db.py#L22). No isolated open owner comment is attributed to this adapter/helper; its callers carry the relevant outcomes.

### M02 — DB map contours, scoring and unclip

**Verdict: keep.** Keep the adapter while removing any assumption that its polygon defines physical ink ownership.

**Feature and operation.** Threshold the map, extract contours, score, expand and return quads; recovery uses polygon contours. **Current contract:** float32 map plus target size -> ragged polygons, detector scores, null baselines. Map coordinates are rounded into page pixels.

**Principle and evidence.** Reasonable detector adapter, not a physical row model. Expansion creates the mixed-row envelopes later stages struggle to repair. Default/variant detector experiments and current Paddle tiles; no independent proof that every expanded envelope contains one row.

**Constants and units.** Stack defaults: map .2, score .45, unclip 1.4, max 3000; DB minimum short side 3 map pixels (5 after expansion); polygon approximation .002 perimeter. Edge scout separately uses .3.

**Vetoes, duplication and routing.** Same adapter is invoked 363 times; 252 quad and 111 polygon paths. Keep its genealogy diagnostic-only. Unused inherited resize modes are not production requirements. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `detector_s` pass 1 126.642 / 143.851 / 174.946ms; pass 2 126.396 / 141.002 / 175.779ms. detector_s includes base preprocessing/inference/DB. postprocess function profile isolates DB for all base and regional calls.

**Fresh profile.** `shared/detector.py:31:postprocess`: 363 calls on 208 pages; inclusive 3.022 / 12.645 / 37.322ms over 208, self total 64.813ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** Base DB postprocess208/208; 155 regional postprocess calls. Produces source/candidate polygons; changes are charged to the invoking mechanism.

**Alternative.** Retain detector contours as support with explicit row bands instead of an expanded rectangle as ownership: less neighboring ink, requires a measured band model. **Delete it:** Deleting postprocessing needs a map-to-row replacement; using raw connected map islands alone would lose established localization behavior.

**Rust.** OpenCV bindings for contours/minAreaRect and a Clipper-compatible offset backend initially; own raster/contour code is possible. pyclipper integer offset behavior needs separate parity tests. **Behavior to pin:** Contour iteration order, float32 minAreaRect ties, round versus truncation, int16 quad conversion and offset join behavior are observable.

**Sources:** [shared/paddle_db.py](../../../prototypes/fast_lines/shared/paddle_db.py#L212), [shared/detector.py](../../../prototypes/fast_lines/shared/detector.py#L31). **Current comment links:** O06, O07, O24.

### M03 — Scale, axes, ROI and shared image primitives

**Verdict: merge.** Make one page/region measurement context with explicit immutable arrays; stop inferring an axis from arbitrary polygon vertices.

**Feature and operation.** Estimate a provisional letter scale and straight axis; crop/rasterize polygons, fit robust lines and enumerate connected components/runs. **Current contract:** Polygon lists and page size -> scalar h, axis intercept/slope, ROI bounds, masks and component arrays. h is half a box short side, not a measured x-height.

**Principle and evidence.** Centralizing units is principled; repeatedly recomputing a detector-box proxy after clipping/recovery makes the physical meaning drift. line_axis averages the first/last two x-sorted vertices, which is unsafe as a general ribbon axis. Feature reports explicitly distinguish proxy height from native body height. No independent complete font/guide model runs here.

**Constants and units.** height_proxy uses half the median minAreaRect short side with min(page size)/1000 floor; empty input fallback is min(size)/100 before halving. quantize rounds with a lower bound of 1; masks and ROI use different rounding/boundary conventions.

**Vetoes, duplication and routing.** 2, 898 height estimates, 81, 170 line_axis calls and 642, 861 bbox calls in the fresh profile; many parents rebuild equivalent arrays. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/contracts.py:47:bbox`: 642861 calls on 207 pages; inclusive 3.736 / 41.553 / 269.766ms over 208, self total 482.659ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** No independent final-item mutation; see the caller outcome and function invocation counts below.

**Alternative.** Measure per-region body height once, retain detector proxy separately, and carry typed axes/bounds/coordinate transforms: less work and clearer units, requires cache invalidation after mutations. **Delete it:** Deleting these utilities only helps if their duplicated callers are replaced; inlining them would worsen consistency.

**Rust.** Plain arrays and loops; OpenCV CC/min-area box can remain temporarily. Own Otsu, CC and run extraction or imageproc equivalents are feasible. **Behavior to pin:** Median/quantile definition, component connectivity/order, robust-fit ties, pixel-center versus pixel-edge convention must be specified.

**Sources:** [shared/geometry.py](../../../prototypes/fast_lines/shared/geometry.py#L8), [shared/contracts.py](../../../prototypes/fast_lines/shared/contracts.py#L47), [shared/image_evidence.py](../../../prototypes/fast_lines/shared/image_evidence.py#L35). No isolated open owner comment is attributed to this adapter/helper; its callers carry the relevant outcomes.

### M04 — Reduced rule scout

**Verdict: merge.** Retain its cheap observations in a unified layout scout, without silently treating lack of a printed stroke as one leaf.

**Feature and operation.** Look for sustained vertical dark strokes that may separate a crossing text box. **Current contract:** Gray page and original quads -> reduced primitive image, h, candidate rule regions and crossing indices.

**Principle and evidence.** A visible printed separator is a real feature; the scout only nominates. It does not identify unruled gutters or page leaves. Q8 explicit rule/clear-paper comparisons, then R5 column review. Current boundary overview panels corroborate accepted cuts.

**Constants and units.** 12 samples/h and a1200px page cap; local mean over 3h, absolute contrast255*.06, close .5h, dilation .6h, run>=12h/width<=2h, >=3 boxes crossing at least6h from each end. These are Q8/R4 development choices, not universal laws.

**Vetoes, duplication and routing.** Runs on all 207 active pages; its primitives are reused by Q8, curved rules and columns. Later candidate protection still repeats regional rule extraction. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `rule_scout_s` pass 1 5.788 / 8.820 / 9.491ms; pass 2 5.713 / 8.516 / 9.467ms.

**Fresh profile.** `layout_barriers/fast.py:15:scout`: 207 calls on 207 pages; inclusive 5.865 / 8.847 / 9.588ms over 208, self total 143.804ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** scout207 pages; correct invoked25 pages; changes 308 sources on 18 pages (M05)

**Alternative.** Derive one reduced page layout map and retain stroke paths, whitespace gutters and leaf IDs: more complete boundaries, additional modeling work. **Delete it:** Deleting the scout loses cheap nominations and either drops column fixes or forces native verification everywhere.

**Rust.** Own reductions, run-length scans and morphology or imageproc/OpenCV; plain mask plus candidate interval arrays. **Behavior to pin:** Downsampling and integer kernel rounding change thin-stroke continuity; compare renderings at native scale.

**Sources:** [layout_barriers/fast.py](../../../prototypes/fast_lines/layout_barriers/fast.py#L15). **Current comment links:** O13.

### M05 — Native straight-rule verification and Q8 cutting

**Verdict: merge.** Fold verification and clipping into one boundary module; keep its approved cases as acceptance fixtures.

**Feature and operation.** Verify the proposed stroke, require clear paper on both sides and clip crossing polygons while protecting grids. **Current contract:** Original polygons + scout primitives -> verified rule paths, clipped pieces, source changes and decisions.

**Principle and evidence.** Clear paper and sustained stroke are physically inspectable. The many corridor/grid guards encode discovered counterexamples and only certify the actual rule extent. Q8/R4 before-after rule renderings and current fixed column pages; no new exhaustive native-rule experiment in Task 1.

**Constants and units.** Contrast>.12, straight residual<.12h and 85% sustained support; flank .22–.55h with density<.08; 3 horizontal intersections protect a grid; cuts offset±.12h. These empirical gates accompany a real stroke model; individual calibration is not documented.

**Vetoes, duplication and routing.** Repeated verify_rule/corridor_clear calls also serve column and recovery paths. This is a guard chain, but preserves owner-approved separation. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `q8_correction_s` pass 1 0.000 / 7.618 / 15.293ms; pass 2 0.001 / 7.699 / 14.465ms.

**Fresh profile.** `layout_barriers/fast.py:66:verify_rule`: 218 calls on 58 pages; inclusive 0.000 / 8.999 / 21.237ms over 208, self total 31.620ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `count.q8`: 308 on 18 pages

**Alternative.** A single region boundary graph with stroke and bilateral text-termination witnesses can serve every later stage; it gains consistency but must retain table-cell distinctions. **Delete it:** Deleting without a layout replacement rejoins known columns and risks table splits; retain as a protected reference during Task 2.

**Rust.** Own scanline/corridor tests and polygon half-plane clipping; OpenCV morphology initially. Input/output are arrays of paths and polygon offsets. **Behavior to pin:** Raster edge ownership, float intersection tolerances and boundary-inclusive tests must be fixed.

**Sources:** [layout_barriers/fast.py](../../../prototypes/fast_lines/layout_barriers/fast.py#L52). **Current comment links:** O13.

### M06 — Mirrored-glyph back-print ownership

**Verdict: merge.** Retain mirror evidence as an optional ink witness; remove the type-prefixed copies and reuse a single measured context.

**Feature and operation.** Compare weak bands with a local atlas of normal glyph shapes, testing direct and reflected matches plus nearby independent supporting rows. **Current contract:** Gray, boxes, optional requested regions -> tones, atlas glyph arrays, per-region front/back/unknown states and suppress indices.

**Principle and evidence.** Mirrored recurrence is more specific than faintness and appropriately preserves unknowns. It is still a component-shape proxy, not character recognition, and short running heads may lack enough corroboration. FEATURES_B records explicit/direct/reflected glyph renderings and controls. Current approved back-print removals survive exactly; short faint pieces remain.

**Constants and units.** Weak nomination uses tone < .72 of the page high tone, core < .5 anchor core, width >2h; up to 12 anchors (6 sampled), >=3 anchors and high>.08; two nearby supporters can corroborate a weak band.

**Vetoes, duplication and routing.** Type recovery carries an older near-copy with the same shape matching. Main path has 180 suspects/39 pages but 61 removals on only 3; not an adequate substitute for final faintness. Main ink pass before seals; type-prefixed variant during M27/M31.

**Fresh profile.** `shared/ink_ownership.py:15:analyze`: 227 calls on 207 pages; inclusive 2.298 / 24.313 / 342.649ms over 208, self total 23.225ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `ink.suspects`: 180 on 39 pages; `ink.atlas`: 13161 on 39 pages; `count.back`: 61 on 3 pages

**Alternative.** Use the shared component atlas and row-aligned reflection evidence only for ambiguous weak runs: retains causal specificity, avoids a second full box census, still cannot prove all show-through. **Delete it:** Deleting removes 61 currently suppressed source bands unless final faintness independently covers them; no ablation establishes that coverage.

**Rust.** Histogram percentiles, resizing, normalized correlation and neighbor searches are plain Rust; OpenCV remap/CC initially. Atlas should be fixed-size raster arrays plus component IDs. **Behavior to pin:** 8-bit percentile interpolation, glyph normalization/resize and best-match ties matter. Do not rename a reflected score as a probability.

**Sources:** [shared/ink_ownership.py](../../../prototypes/fast_lines/shared/ink_ownership.py#L15), [shared/ink_photometry.py](../../../prototypes/fast_lines/shared/ink_photometry.py#L10), [shared/type_ink_ownership.py](../../../prototypes/fast_lines/shared/type_ink_ownership.py#L1), [shared/type_ink_photometry.py](../../../prototypes/fast_lines/shared/type_ink_photometry.py#L11). **Current comment links:** O08, O09, O10, O11, O24.

### M07 — Seal-rim trace and tangent classification

**Verdict: keep.** Keep the narrow rim witness and exact removal contract; share its measurements in Task 3.

**Feature and operation.** Nominate weak stamp-like regions, trace a circular rim, and remove text detections tangent to that rim. **Current contract:** Gray, items, h and weak indices -> ring parameters/support and exact suppressed text polygons; the interior is not an exclusion disk.

**Principle and evidence.** A rim and tangent lettering are explicit geometric features. Circular nomination followed by an ellipse fit is a restricted model; pale interior marks and strongly noncircular seals remain difficult. FEATURES_B/R5 stamp renderings; current dbd, 466, d6 and 1be600 controls visually retain ordinary body text. Ring removal is not removal of every mark inside the stamp.

**Constants and units.** Polar sampling, radius/support and tangent tolerances are h-relative mixed with angular/occupancy constants. Hough40/28 at 8px/body are gradient/center thresholds; FAST_LINES_STACK explicitly says their original numeric calibration is undocumented.

**Vetoes, duplication and routing.** Candidate selection depends on the older ownership census. Exact polygon exclusions are sound; other modules later broaden them to bounding rectangles. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `seal_s` pass 1 0.074 / 13.066 / 64.218ms; pass 2 0.074 / 12.779 / 65.580ms.

**Fresh profile.** `shared/ink_seal.py:85:render`: 207 calls on 207 pages; inclusive 0.109 / 21.244 / 108.286ms over 208, self total 2.620ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `ink.seal_candidates`: 30 on 27 pages; `ink.seal_rings`: 21 on 21 pages; `count.seals`: 22 on 21 pages

**Alternative.** Fit connected closed curves/ellipses and test local tangent glyph runs in the shared ink context: more general stamps, greater complexity. **Delete it:** Deleting returns 22 rim boxes on 21 pages unless another mechanism takes responsibility; final faintness alone is not demonstrated equivalent.

**Rust.** Own polar sampling/DP and least-squares geometry, or OpenCV remap initially; rings and tangent support are plain numeric arrays. **Behavior to pin:** Polar interpolation, peak ties and angle wrapping affect marginal rim support.

**Sources:** [shared/ink_seal.py](../../../prototypes/fast_lines/shared/ink_seal.py#L13). **Current comment links:** O20.

### M08 — Coarse ornament nomination and gate

**Verdict: merge.** Unify nomination with M10 and keep M09 as the explicit repeated-support witness; do not add frame-specific page rules.

**Feature and operation.** Reject ordinary line geometry cheaply, inspect coarse repeated support, and request spatial motif evidence before removing ornament strips. **Current contract:** Gray, one polygon, h -> nomination and repetition verdict; inspect returns evidence dictionaries even for ordinary lines.

**Principle and evidence.** Repeated decoration is a real feature, but repetition alone also describes quotation marks, numbers and text. The gate is a staged heuristic, not image understanding. FEATURES_B documents failed whole-strip autocorrelation and the spatial-field replacement. Re-reviewed frame failures show the current rendering is incomplete.

**Constants and units.** 8/body coarse and 16/body refinement, aspect and repetition/connected-support thresholds are development constants; no page-keyed branch exists.

**Vetoes, duplication and routing.** 14, 603 main coarse calls and 721 nominations on 114 pages lead to only 11 removals/10 pages; type-prefixed gate is function-identical after import renaming. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/ink_motif_gate.py:34:inspect`: 14626 calls on 207 pages; inclusive 0.278 / 112.934 / 431.861ms over 208, self total 139.973ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `ink.motif_nominated`: 721 on 114 pages; `ink.motif_drops`: 11 on 10 pages

**Alternative.** One page component adjacency graph with motif repetition plus a non-text layout witness: less per-line work and better vertical frames, but needs new explicit controls. **Delete it:** Deleting loses approved horizontal ornament removals; deleting only the ordinary-line diagnostic allocation is safe after interface separation.

**Rust.** Own reductions/correlation and run scans; reuse one raster context. NumPy broadcasts and dictionary returns should become arrays and enums. **Behavior to pin:** Sampling phase and component ties can convert repeated punctuation into a false ornament.

**Sources:** [shared/ink_motif_gate.py](../../../prototypes/fast_lines/shared/ink_motif_gate.py#L12), [shared/type_ink_motif_gate.py](../../../prototypes/fast_lines/shared/type_ink_motif_gate.py#L13). **Current comment links:** O19, O21, O22, O23, O24, C05.

### M09 — Spatial repeated-ink field

**Verdict: merge.** Use one explicit motif witness behind a shared scout; retire the unused whole-strip decision experiment.

**Feature and operation.** Render repeated patch matches and the actual supported ink in and around a strip; contextual coverage verifies a decorative motif. **Current contract:** Rectified strip + h -> density/correlation fields, patch correspondences and support counts consumed by M08.

**Principle and evidence.** More principled than a scalar autocorrelation gate because the matched pixels can be drawn. It still needs typography controls and has no general picture/engraving classifier. FEATURES_B explicitly compares dense/R1/R2 spatial support and retained counterexamples. No evidence that all ornament orientations are covered.

**Constants and units.** Patch, lag and context extents are letter-relative; correlation, occupancy and peak-prominence constants remain empirically selected. ink_motifs.inspect autocorrelation is diagnostic, strip is live.

**Vetoes, duplication and routing.** Main spatial renderer runs 132 times on 54 pages; the type clone adds one call. Five repeat-field functions, recurrence and strip implementations are duplicated. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/ink_recurrence.py:12:render`: 132 calls on 54 pages; inclusive 0.000 / 7.281 / 32.192ms over 208, self total 118.538ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `ink.motif_drops`: 11 on 10 pages

**Alternative.** Component-shape recurrence with a single spatial index can avoid repeated raster field construction; gains reuse, loses some connected-strip evidence unless both renderings agree. **Delete it:** Deleting the verifier while keeping the gate makes removals unsupported; deleting the whole ornament route restores its false positives.

**Rust.** Own normalized correlation, summed-area tables and component graph; OpenCV remap is replaceable with explicitly specified bilinear interpolation. **Behavior to pin:** Correlation reduction order, peak selection, border sampling and normalization near zero energy require deterministic definitions.

**Sources:** [shared/ink_recurrence.py](../../../prototypes/fast_lines/shared/ink_recurrence.py#L12), [shared/ink_repeat_field.py](../../../prototypes/fast_lines/shared/ink_repeat_field.py#L13), [shared/ink_motifs.py](../../../prototypes/fast_lines/shared/ink_motifs.py#L8), [shared/type_ink_recurrence.py](../../../prototypes/fast_lines/shared/type_ink_recurrence.py#L13), [shared/type_ink_repeat_field.py](../../../prototypes/fast_lines/shared/type_ink_repeat_field.py#L14), [shared/type_ink_motifs.py](../../../prototypes/fast_lines/shared/type_ink_motifs.py#L9). **Current comment links:** O19, O21, O22, O23, C05.

### M10 — Disconnected motif and border-layout follow-up

**Verdict: merge.** Merge into the shared motif mechanism in Task 3; do not port a separate patch cascade.

**Feature and operation.** Use edge/layout nominations and repeating disconnected component shapes to catch ornaments missed by the connected-strip route. **Current contract:** Items and gray -> layout candidates, component features, native verification and exact removal indices.

**Principle and evidence.** Explicit component recurrence is defensible; isolated vertical quotation glyphs are a real counterexample. Page-edge position is context, not proof of decoration. R5 motif boards and current 7792/c99 failures. Only 5 additional drops on 5 pages after 95 checks on 64 pages.

**Constants and units.** Component area/aspect/spacing tolerances use h or h²; repetition and support fractions are empirical. Versioned controls constrain deletion.

**Vetoes, duplication and routing.** A second ornament nomination/refinement tree overlaps M08/M09 and repeats component work. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `discrete_refinement_s` pass 1 0.000 / 4.245 / 129.303ms; pass 2 0.000 / 4.393 / 145.522ms.

**Fresh profile.** `shared/ink_discrete_motifs.py:127:verify`: 95 calls on 64 pages; inclusive 0.000 / 5.057 / 152.496ms over 208, self total 2.324ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `ink.discrete_checks`: 95 on 64 pages; `ink.discrete_drops`: 5 on 5 pages

**Alternative.** One orientation-independent motif graph with frame continuity and text-run negative controls: may solve side frames, needs explicit native rendering first. **Delete it:** Deleting loses five present removals and simplifies a weak branch; acceptable only if the unified motif model covers these five.

**Rust.** Plain CC feature arrays, shape matching and graph grouping; morphology/CC via imageproc or own code with OpenCV parity reference. **Behavior to pin:** Component connectivity and resampling can merge or split decorative units and quotation marks.

**Sources:** [shared/ink_discrete_motifs.py](../../../prototypes/fast_lines/shared/ink_discrete_motifs.py#L13). **Current comment links:** O19, O21, O22, O23, O24, C05.

### M11 — Probability-map edge curvature scout

**Verdict: merge.** Use one shared scout after leaf/column partition; evaluate against explicit native geometry, not a percentage of changed boxes.

**Feature and operation.** Sample outer thirds and beyond original box ends, compare to an inner straight tangent, and require neighboring deviations with the same sign. **Current contract:** Paddle map, original polygons and image size -> sampled paths, deviations in h and nominated original IDs.

**Principle and evidence.** Directly tests the owner’s shared-edge-bend idea, but follows local map maxima and can switch rows or conflate column phase. It is a nomination only. R6 C map/native renderings and all 208 bend summary. Runtime fires on 73 pages; independent always-rendered bend is marked on 71, a different denominator.

**Constants and units.** Width >=12h; 65 offsets across ±4h but peak choice constrained to ±h; map strength .3; deviation >.35h; >=3 coherent neighbors within 6h x /8h y.

**Vetoes, duplication and routing.** Every trigger pays for field preparation; 35/73 pages retain no final field band. Geometry sparse scout later resamples the same map independently. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `edge_scout_s` pass 1 4.188 / 13.315 / 26.766ms; pass 2 3.960 / 13.182 / 26.481ms.

**Fresh profile.** `shared/geometry_edge_map.py:13:scout`: 207 calls on 207 pages; inclusive 6.507 / 23.405 / 43.230ms over 208, self total 470.419ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `edge.trigger`: 73 on 73 pages; `edge.nominated`: 1329 on 73 pages

**Alternative.** Combine region-separated map residuals and native row-gap consistency in one cheap layout/geometry scout; saves duplicate work, must not suppress difficult curls. **Delete it:** Deleting as an authorization gate and fitting a cheap flat/shared model everywhere is viable only if its clean-page cost is negligible; deleting field correction entirely loses current gains.

**Rust.** Own array sampling, regression, fixed convolution and neighbor bins; OpenCV remap initially. **Behavior to pin:** Map interpolation, argmax ties, regression precision and .35h threshold boundaries change nominations.

**Sources:** [shared/geometry_edge_map.py](../../../prototypes/fast_lines/shared/geometry_edge_map.py#L13). **Current comment links:** O02.

### M12 — Curved separator refinement

**Verdict: merge.** Keep the measured stroke path as part of M13’s boundary model, with a single clip operation.

**Feature and operation.** Follow bent vertical printed rules, check intersections/isolated stroke ownership, then clip crossings along the verified curve. **Current contract:** Scout, original items and native gray -> rule paths and split polygons; removed originals still participate in ownership tests.

**Principle and evidence.** A distinct page feature from text-line curvature. Preserving removed-source context avoids falsely proving a separator from prior deletion. R4/R5 geometry separator renderings and current column pages. Count is 92 applied changes on 3 pages, not 92 curvature-corrected rows.

**Constants and units.** Letter-scaled path search, grid intersection and isolated-stroke tests; wide_paper and ownership modes are regression-driven guards. Small numeric floors also occur.

**Vetoes, duplication and routing.** Uses Q8 verification and duplicates straight/column boundary logic. Runs before the field on triggered pages, otherwise after M20. Before M14 on edge-triggered pages; after M20 otherwise; cuts computed once and reused.

**Measured cost.** R6 `curved_s` pass 1 0.000 / 2.620 / 59.746ms; pass 2 0.000 / 2.682 / 58.598ms.

**Fresh profile.** `shared/geometry_feature_rules.py:43:grid_intersections`: 61 calls on 51 pages; inclusive 0.000 / 4.144 / 9.385ms over 208, self total 9.082ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `count.curved`: 92 on 3 pages

**Alternative.** A boundary path graph with shared verification and clipping handles straight and curved strokes in one place; requires identical protections on tables. **Delete it:** Deleting reinstates crossings on these three pages; replacement must preserve their approved cuts.

**Rust.** Own DP/path arrays and polygon clipping; OpenCV connected/rule primitives can be wrapped during migration. **Behavior to pin:** Path tie-breaking, smoothing and polygon intersection conventions affect which side owns touching letters.

**Sources:** [shared/geometry_feature_rules.py](../../../prototypes/fast_lines/shared/geometry_feature_rules.py#L15). **Current comment links:** O06.

### M13 — Bilateral column termination certificate

**Verdict: keep.** Keep the evidence and extend it into a shared region contract before fitting any bend. Do not remove column protection while deleting veto chains.

**Feature and operation.** Confirm printed column boundaries using text ending on both sides, then clip current or recovered boxes along the supported rule extent. **Current contract:** Original source boxes, native stroke evidence and retained-source IDs -> accepted boundary paths and clipped polygons.

**Principle and evidence.** Strong feature-backed separation with owner-approved results. A finite rule is not a complete column model: the row above its top can still cross, as c8b p155#2 does. R5 column renderings and current R4 fixed controls. 49 accepted rules on 45 pages; 279 geometry changes on 44 pages.

**Constants and units.** Termination windows/gaps in h plus density/overlap ratios; cut extent follows evidence. No page-name cases. Acceptance and actual output changes have separate counts.

**Vetoes, duplication and routing.** Q8, curved rules, native crossings, type barriers and field horizontal-source guards all protect similar boundaries with different meanings. With M12; also applied to recovered residual pieces. Rule evidence reused, changes list is geometry-stage only.

**Measured cost.** R6 `column_s` pass 1 0.170 / 17.355 / 24.614ms; pass 2 0.173 / 17.493 / 25.075ms.

**Fresh profile.** `shared/geometry_columns.py:50:analyze`: 207 calls on 207 pages; inclusive 0.146 / 15.278 / 21.504ms over 208, self total 10.014ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `column.accepted`: 49 on 45 pages; `count.columns`: 279 on 44 pages

**Alternative.** Promote accepted rule plus bilateral terminations into a region boundary with measured continuation through whitespace; preserve separate page leaves and table cells. **Delete it:** Deleting regresses the feature the owner explicitly approved; this is protected infrastructure for Task 2.

**Rust.** Plain interval/path arrays and deterministic half-plane/path clipping; OpenCV for native crossings at first. **Behavior to pin:** Raster stroke extent, inclusive endpoints and source-ID set/order handling affect top/bottom rows.

**Sources:** [shared/geometry_columns.py](../../../prototypes/fast_lines/shared/geometry_columns.py#L16). **Current comment links:** O05, O06, O07, O10, O13, O15, C02, C03, C04.

### M14 — Native page ink/contact context

**Verdict: merge.** Create one shared component context; keep intensity and geometric support as distinct arrays.

**Feature and operation.** Build page/local paper contrast, labels, body components and smoothed density used by field fitting and contact paths. **Current contract:** uint8 image + proxy h -> density float array, label raster, component IDs/bounds/centres and scale; optional fast filters and labels.

**Principle and evidence.** Explicit body contacts are useful physical evidence. The inherited .08 intensity floor does not distinguish front/back ink or under-inking. FEATURES_A contact renderings and R6 C native field renderings; not a font identity or semantic baseline measurement.

**Constants and units.** Native or 12-samples/h routes; letter-scaled paper/smoothing kernels, fixed 8-bit contrast floor and body-size gates. Several versions trade filters without a unified component contract.

**Vetoes, duplication and routing.** prepare executes 99 times on 95 pages. field_cache reuses it only when no excluded region was painted out; later native bands, rows and faintness extract components independently. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/geometry_contacts.py:17:prepare`: 99 calls on 95 pages; inclusive 0.000 / 129.855 / 192.870ms over 208, self total 2699.054ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** No independent final-item mutation; see the caller outcome and function invocation counts below.

**Alternative.** One immutable photometric/component context per page or requested ROI, with explicit excluded-ink labels rather than repainting gray: less recomputation, needs well-defined photometry. **Delete it:** Deleting requires another native support source; relying on the low-resolution map loses curled ends and detached accents.

**Rust.** Own summed-area/box filters, separable convolution and CC; imageproc candidates or OpenCV wrappers initially. Avoid Python dict per component. **Behavior to pin:** Otsu/contrast threshold, filtering borders, native versus resized connectivity and component ordering change the fitted field.

**Sources:** [shared/geometry_contacts.py](../../../prototypes/fast_lines/shared/geometry_contacts.py#L17). No isolated open owner comment is attributed to this adapter/helper; its callers carry the relevant outcomes.

### M15 — Shared displacement mesh and certification

**Verdict: replace.** Task 2: one region-scoped row model whose rendered gaps and row paths agree with the image before any fast route.

**Feature and operation.** Form horizontal-support blocks, correlate neighboring vertical ink profiles into a mesh, infer row phases and reject nonmonotone or unsupported bend. **Current contract:** Native context + original boxes + accepted columns -> fields with x samples, y knots, displacement mesh, support, row paths and Jacobian.

**Principle and evidence.** The shared, monotone bend is the right physical direction. Region formation is incomplete: crossing source boxes fill a gutter, and row phase between columns becomes false bend. R6 C explicit/reduced/map comparisons; coordinator bend drawings checked on 8686, e259 p198 and c8 p68. The last two visibly fit across independent columns/leaves.

**Constants and units.** Blocks need >=4 long boxes (>8h) and >=12h width; empty gaps >=2h. Knot spacing 8h, ±7h windows, 25 lags, two alignment iterations, .35h coherent edge departure and positive vertical Jacobian.

**Vetoes, duplication and routing.** render runs 73 times; 44 curved runtime fields on 39 pages. The independent 208-page rendering marks 71 pages, 59 outside the three curved books: detection is not correctness. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/geometry_page_field.py:42:render`: 73 calls on 73 pages; inclusive 0.000 / 333.778 / 451.969ms over 208, self total 873.300ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `field.curved`: 44 on 39 pages

**Alternative.** Separate leaves/columns first, fit one monotone deformation per region and place real row phases in native white gaps; the flat model is the zero-displacement case. **Delete it:** Deleting the current fitter avoids false bend and much cost but restores straight-box failures; replace its region/phase model rather than discard shared geometry.

**Rust.** Own interpolation, cross-correlation, robust fit and separable Gaussian; Vec/ndarray for mesh[K, X]. SciPy find_peaks and filters require explicit replacement semantics. **Behavior to pin:** Argmax/peak ties, iterative floating reduction, interpolation and Jacobian rounding matter; test topology and ink ownership rather than only polygon equality.

**Sources:** [shared/geometry_page_field.py](../../../prototypes/fast_lines/shared/geometry_page_field.py#L16). **Current comment links:** O01, O02, O03, O04, O05, O13, C01, C02, C03, C04.

### M16 — Unbend and second Paddle localization

**Verdict: replace.** Task 2 should derive bands from the shared row model and delete this unconditional rectified-region detector path where covered.

**Feature and operation.** Resample every accepted curved region into rectified space, rerun Paddle, densify polygon edges, map bands through the mesh and buffer them. **Current contract:** Gray + field mesh + session -> rectified image/map and 2, 859 mapped candidate polygons across 39 pages.

**Principle and evidence.** Geometric coordinate transport is principled; outsourcing row phase again to expanded detector boxes reintroduces the very mixed-row problem the bend should solve. R6 C mapped polygons/native bands, with rejection drawings and fresh output parity. A correct bend alone does not certify these row placements.

**Constants and units.** Linear remap with white border; edge sampling .4h, simplify 1e-5 pixels and buffer .06h; full region reruns use default 960 side.

**Vetoes, duplication and routing.** 44 regional inference calls plus M14/M15/M17 are inside this stage’s timer. Row coordinates are recomputed after native field row seeds already exist. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `field_proposal_s` pass 1 0.000 / 619.527 / 920.783ms; pass 2 0.000 / 629.304 / 936.568ms.

**Fresh profile.** `shared/geometry_field_detector.py:29:run`: 73 calls on 73 pages; inclusive 0.000 / 718.304 / 1107.808ms over 208, self total 214.239ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `field.proposals`: 2859 on 39 pages

**Alternative.** Transport the measured native row-gap bands directly; use a regional rerun only to nominate a genuinely unowned missing row. Less latency and no repeated phase reset. **Delete it:** Deleting the rerun route without native row localization loses 1, 060 final page_field-tagged polygons; this count is provenance, not a count of correct fixes.

**Rust.** Own bilinear remap and displacement interpolation; ort for exceptional reruns. Polygon buffering via geo is not GEOS-identical; direct band construction can avoid it. **Behavior to pin:** Interpolation blurs/connects strokes, second detection changes with crop sizing, Shapely simplification/buffering creates many vertices and rounding-dependent masks.

**Sources:** [shared/geometry_field_detector.py](../../../prototypes/fast_lines/shared/geometry_field_detector.py#L9). **Current comment links:** O11, O12, C01, C02.

### M17 — Per-row native-band rebuild and gap separation

**Verdict: replace.** Replace with neighboring-row bands in Task 2; do not relax .75h and add another retention guard.

**Feature and operation.** Assign connected bodies to the nearest rectified detector axis, attach marks, derive envelopes, then separate neighboring bands with low-ink gaps. **Current contract:** Rectified gray + rerun boxes + h -> row polygons and foreign-component flags; candidates are later mapped back by M16.

**Principle and evidence.** Bodies and white gaps are visible; independent nearest-axis ownership before joint row phase is not the owner’s parallel-row model. Good curled words can be excluded before retention is tested. 8686 p5/p7 rejection drawings: fitted bend reaches curled words, rebuilt bands omit them or hold another row. No claim that all candidates correspond to real text rows.

**Constants and units.** Nearest distance <.75 local h, margin >.15h; body height .3–2h, width <5h, area >.025h². Local h includes .65 of detector short side; contrasts >255*.08; mark attachment and gap smoothing add more cutoffs.

**Vetoes, duplication and routing.** 44 native rebuilds and separations; duplicates contact assignment, envelope fitting and B’s row partition. foreign_components drives whole-candidate vetoes. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/geometry_field_detector.py:54:native_bands`: 44 calls on 39 pages; inclusive 0.000 / 234.710 / 475.624ms over 208, self total 1294.550ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `field.proposals`: 2859 on 39 pages

**Alternative.** Jointly order rows, put each shared boundary in a white gap, assign whole bodies/marks consistently, and measure only endpoints per row using normal ink. **Delete it:** Deleting this rebuild while keeping raw DB rectangles restores broad bands; deleting it with the new joint model removes the central loss/veto conflict.

**Rust.** Own connected-component labels, row assignment and gap DP; use spatial bins instead of SciPy cKDTree if convenient. Arrays should store one component owner ID. **Behavior to pin:** Nearest-row ties, component centroid rounding, Otsu/connectivity and smoothed gap boundaries determine ownership.

**Sources:** [shared/geometry_field_detector.py](../../../prototypes/fast_lines/shared/geometry_field_detector.py#L54). **Current comment links:** O01, O02, O03, O04, O05, O11, O12, C01, C02.

### M18 — Early and late field replacement veto chain

**Verdict: replace.** Task 2 removes the per-line replacement/fixed-point chain with the band generator it protects; keep explicit preservation checks in validation.

**Feature and operation.** Link old and proposed bands through shared native labels, group them, reject unsafe replacements, and recompute retention to a fixed point. Revisit after shape/type/faint changes. **Current contract:** Old polygons + field candidates + exact exclusions/columns -> replacements with parent/source metadata, rejected decisions and unowned proposals.

**Principle and evidence.** Ink conservation and permanent exclusions are sound requirements. A veto cascade around independently wrong row bands cannot establish unique row ownership and deliberately cannot add unowned rows. R6 C rejection images directly expose the failure. p5: 38 proposals, 36 late decision groups all rejected and 2 unowned; p7 accepts 9 early +4 late. Green default outlines do not prove acceptance.

**Constants and units.** Label-vote links >=.8 of maximum; >8h old width; small-cell, foreign-row, completed-initial, existing-field and horizontal-source vetoes; 3×3 dilation and area >=max(2,.004h²) for lost ink.

**Vetoes, duplication and routing.** 73 early calls, 18 late calls; changes on 38 and 8 pages respectively. Late changes remove 30 old indices/emit29; do not add early and late counts as distinct final rows. Early before M19 and conditionally again between M35 and M36, reusing the same proposal.

**Measured cost.** R6 `field_early_replace_s` pass 1 0.000 / 141.673 / 199.540ms; pass 2 0.000 / 144.085 / 214.559ms.

**Fresh profile.** `shared/geometry_field_selection.py:9:apply`: 91 calls on 73 pages; inclusive 0.000 / 202.930 / 379.964ms over 208, self total 2114.081ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `field.early_replacement.called`: 73 on 73 pages; `field.early_replacement.changed`: 1034 on 38 pages; `field.early_replacement.emitted`: 1033 on 38 pages; `field.replacement.called`: 18 on 18 pages; `field.replacement.changed`: 30 on 8 pages; `field.replacement.emitted`: 29 on 8 pages; `count.page_field`: 1060 on 38 pages

**Alternative.** Construct a nonoverlapping band partition first with immutable region/exclusion ownership; validate invariant failures diagnostically instead of vetoing whole line groups. **Delete it:** Deleting vetoes alone would admit wrong-row/lost-ink candidates. Delete the chain only when the replacement model enforces these invariants by construction.

**Rust.** Array IDs, component-owner CSR and raster occupancy eliminate dict/set graph mutations. geo can support geometric checks, but main decisions should not require GEOS objects. **Behavior to pin:** Set/order traversal, .8 vote ties, raster dilation, polygon area epsilon and fixed-point rejection order affect results.

**Sources:** [shared/geometry_field_selection.py](../../../prototypes/fast_lines/shared/geometry_field_selection.py#L9). **Current comment links:** O01, O02, O03, O04, O05, O11, O12, C01, C02.

### M19 — Sparse local map geometry scout

**Verdict: merge.** Absorb map alignment evidence into the common Task 2 scout and retire its standalone correction route when covered.

**Feature and operation.** Sample native detector-map strips to nominate boxes whose straight geometry does not follow their text. **Current contract:** Original quads + pm -> sparse row profiles, candidate IDs and trigger; only intact original sources can be corrected downstream.

**Principle and evidence.** Cheap map-to-text alignment is inspectable and supports cost following need. It overlaps edge curvature checking and inherits map ambiguity. FEATURES_A scout audit compares explicit paths, reduced and sampled routes; fresh run triggers29 pages and nominates58 boxes on 24.

**Constants and units.** Installed route/version 3 uses letter-scaled sampling and empirical profile support/residual tests; not an absolute-pixel angle patch.

**Vetoes, duplication and routing.** Still runs after edge/field processing even when field-owned paths make later correction abstain. Repeated axes/height and remaps consume clean-page time. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `scout_s` pass 1 3.096 / 7.847 / 12.228ms; pass 2 3.094 / 7.659 / 23.848ms.

**Fresh profile.** `shared/geometry_scout.py:31:sparse_fast`: 207 calls on 207 pages; inclusive 5.294 / 12.504 / 20.746ms over 208, self total 202.959ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `geometry.trigger`: 29 on 29 pages; `geometry.nominated`: 58 on 24 pages

**Alternative.** One region-aware map residual scout can nominate skew, curve and envelope work together; gain shared sampling, lose simplicity of independent diagnostics. **Delete it:** Deleting restores the 10 accepted native geometry changes/7 pages unless the new row model supplies them; field correction alone is not proven to cover all.

**Rust.** Plain batch affine samples, reductions and robust regression; OpenCV remap parity can be used initially. **Behavior to pin:** float32 maps, quantized peaks and slope thresholds can change nominations on accents and dense rows.

**Sources:** [shared/geometry_scout.py](../../../prototypes/fast_lines/shared/geometry_scout.py#L15). No isolated open owner comment is attributed to this adapter/helper; its callers carry the relevant outcomes.

### M20 — Local map-contour geometry and ink retention

**Verdict: replace.** Retain native retention as a diagnostic invariant; remove the competing per-box contour corrector once Task 2 covers it.

**Feature and operation.** Describe map contour bands and native retained ink for intact original boxes, then adopt measured geometry only if neighboring ink/ownership remains safe. **Current contract:** Gray, map, originals, intact source IDs and scouts -> replacement polygons and native retention audit; map_bands can be reused by envelope smoothing.

**Principle and evidence.** Explicit map support plus native ink checking is stronger than box-angle fitting. Per-line contour paths and repeated vetoes are nevertheless a competing row model. FEATURES_A path/correction and R5 shape comparisons. Only10 native geometry changes survive on 7 pages in the final stack.

**Constants and units.** Versioned contour support, smoothness, padding, component area and retention tolerances in h/h²; empirical native-retention fractions remain in this path.

**Vetoes, duplication and routing.** Reuses M14-style ink ideas but with independent retention extraction; M33 later describes the same map bands and checks lost/off-row components again. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `geometry_s` pass 1 0.000 / 53.257 / 187.972ms; pass 2 0.000 / 56.024 / 216.777ms.

**Fresh profile.** `shared/geometry_feature_paths.py:110:bands`: 40 calls on 40 pages; inclusive 0.000 / 71.596 / 319.074ms over 208, self total 203.228ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `count.geometry`: 10 on 7 pages

**Alternative.** Use the shared region model’s skew/row boundaries and one component ownership map; a flat region still needs measured row placement. **Delete it:** Deleting saves little on median pages but can lose approved geometry on its 7 pages; replace after checking those exact examples.

**Rust.** Own contour-band sampling, interpolation and robust fit; OpenCV contours/remap plus explicit arrays initially. Retention should consume existing labels. **Behavior to pin:** Contour ownership ties, float polygon clipping and raster masking cause small but OCR-visible edge changes.

**Sources:** [shared/geometry_context.py](../../../prototypes/fast_lines/shared/geometry_context.py#L17), [shared/geometry_feature_paths.py](../../../prototypes/fast_lines/shared/geometry_feature_paths.py#L16), [shared/geometry_feature_correct.py](../../../prototypes/fast_lines/shared/geometry_feature_correct.py#L18). No isolated open owner comment is attributed to this adapter/helper; its callers carry the relevant outcomes.

### M21 — Fragment-pair nomination and connector geometry

**Verdict: merge.** Replace pairwise guessing with row membership and measured endpoints in Task 2.

**Feature and operation.** Find separated pieces that may belong to one line and construct a smooth Hermite connection hypothesis. **Current contract:** Original/current boxes and h -> ordered pairs/gaps and connector sample paths.

**Principle and evidence.** Common row direction and nearby endpoints are physical clues, but wide word gaps, two columns and a curled end can look alike. FEATURES_A fragment/contact renderings; present 3229/4959 cropped ends and ffccc wide-gap word remain unresolved.

**Constants and units.** Distances/angle changes and gap limits are mostly h-relative; candidate caps/ordering are heuristic. A Hermite interpolant is a smooth hypothesis, not evidence of text.

**Vetoes, duplication and routing.** 230 candidates calls on 207 pages including rechecks; 78 nominated pairs on 28 pages. Many are rejected after more expensive contact work. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/geometry_fragments.py:8:candidates`: 230 calls on 207 pages; inclusive 0.972 / 4.238 / 22.935ms over 208, self total 17.178ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `fragment.pairs`: 78 on 28 pages

**Alternative.** In the shared row coordinate frame, group normal ink by row and stop at region boundaries; a wide whitespace gap need not break a row. **Delete it:** Deleting restores fragmented lines that18 joins currently improve; the new model must own both endpoints before this route is retired.

**Rust.** Plain interval/spatial-bin indexing and polynomial interpolation; Vec pairs/path samples. **Behavior to pin:** Pair enumeration/ties and interpolation endpoints affect subsequent vetoes; source order currently leaks into choices.

**Sources:** [shared/geometry_fragments.py](../../../prototypes/fast_lines/shared/geometry_fragments.py#L8). **Current comment links:** O02, O03, O15.

### M22 — Native body/mark contact tracing

**Verdict: merge.** Keep its body/mark observations as shared arrays and retire the independent trace decision tree.

**Feature and operation.** Trace native body contacts across candidate fragments, attach nearby marks and expose whether a continuous row is supported. **Current contract:** Prepared component context + fragment hypotheses -> paths, contact IDs, mark support and per-pair evidence.

**Principle and evidence.** Whole bodies and detached marks are more physical than ink projection alone. Independent tracing per pair duplicates the shared page row model. FEATURES_A contact audits compare body paths against original pixels. Fresh profile:61 trace calls on 23 pages; this is not61 accepted joins.

**Constants and units.** Letter-relative body, gap, vertical-residual and mark-distance windows; robust polynomial/path fits use empirically chosen support bounds.

**Vetoes, duplication and routing.** Needs M14 context and may rebuild it; field bands and row splitter assign components/marks differently. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/geometry_contacts.py:199:render_contacts`: 23 calls on 23 pages; inclusive 0.000 / 21.770 / 86.491ms over 208, self total 4.660ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `fragment.pairs`: 78 on 28 pages

**Alternative.** Measure component-to-row ownership once from the shared bend and neighboring gaps, then reuse it for endpoints and recovery. **Delete it:** Deleting contact verification while leaving pair joining invites false cross-row joins; remove together with the pairwise model.

**Rust.** Own sparse adjacency graph, robust fit and path arrays; OpenCV sampling and SciPy-style spatial search can be replaced with deterministic bins. **Behavior to pin:** Component connectivity, nearest-body ties and smoothing alter mark ownership.

**Sources:** [shared/geometry_contacts.py](../../../prototypes/fast_lines/shared/geometry_contacts.py#L79). **Current comment links:** O02.

### M23 — Fragment join acceptance and separator veto

**Verdict: replace.** Replace the joiner with shared row ownership; keep separator facts as inputs, not re-detected guards.

**Feature and operation.** Build joined envelopes after contact confirmation, inspect printed barriers, check ink retention and reject overlaps with forbidden regions. **Current contract:** Current pieces + native paths/forbidden regions -> joined polygons and merged source IDs.

**Principle and evidence.** Preserving boundaries is essential. Bounding-box forbidden tests and several retention/shape guards conflate a footprint with all space inside its bounds. R4/R5 join and separator crop boards; current 18 joins on 8 pages reduce output by19 pieces, while curled/missed-word comments remain.

**Constants and units.** Letter-scaled envelope margins and rule windows plus empirical retention/intersection thresholds. local_filter=True restricts costly preparation to candidate bounds.

**Vetoes, duplication and routing.** Rule inspection duplicates M05/M12/M13/M28. Bbox exclusions disagree with exact polygon exclusions used by field/type/faint stages. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `fragment_s` pass 1 0.644 / 24.337 / 95.039ms; pass 2 0.651 / 23.801 / 97.434ms.

**Fresh profile.** `shared/geometry_fragment_correct.py:38:run`: 207 calls on 207 pages; inclusive 1.060 / 30.243 / 131.145ms over 208, self total 16.201ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `count.joins`: 18 on 8 pages; `count.joined_reduction`: 19 on 8 pages

**Alternative.** One row endpoint operation inside a fixed region and exclusion-label contract: fewer ad hoc vetoes and no need for pairwise envelope unions. **Delete it:** Deleting only the guards would regress columns; deleting the whole route needs native row endpoints to reproduce its 8 changed pages.

**Rust.** Plain band/endpoint arrays and source CSR; use one raster ownership map. Shapely-style polygon unions can be avoided by direct band construction. **Behavior to pin:** BBox versus polygon intersection is a semantic mismatch, not floating error; GEOS buffering and raster retention also need fixed conventions.

**Sources:** [shared/geometry_fragment_correct.py](../../../prototypes/fast_lines/shared/geometry_fragment_correct.py#L18), [shared/geometry_joinbarriers.py](../../../prototypes/fast_lines/shared/geometry_joinbarriers.py#L14). **Current comment links:** O02, O03, O04, O05, O15.

### M24 — Type blocks, pitch/phase gaps and edge slots

**Verdict: merge.** Fold pitch into regional row context as a prior, never a line-creation certificate.

**Feature and operation.** Convert ribbons to nomination quads, group similarly sized long lines, estimate repeated pitch, and propose internal/edge row slots. **Current contract:** Current polygons -> block members, h, slope, pitch/phase, candidate slot coordinates and neighbor IDs.

**Principle and evidence.** Typeset rows repeat pitch, but this is not font identification. It cannot prove absent blocks or irregular/short rows; a biased detector phase is inherited. FEATURES_C explicit pitch/phase renderings and R4 false-slot counterexamples. Current377 blocks/204 pages produce703 slots/182 pages.

**Constants and units.** Block length >8h, >=4 members; overlap>.65, center drift<.3 width, height ratio .6–1.67, gap<8h; gap multiples2–4 with residual<.4h; quantile extents .15/.85.

**Vetoes, duplication and routing.** Shared geometry field also estimates row phase; grid_view repeatedly refits min-area boxes. type_profiles.mode is live but its full font-profile machinery is not. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_lattice.py:16:blocks`: 207 calls on 207 pages; inclusive 1.257 / 3.921 / 14.908ms over 208, self total 47.024ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.blocks`: 377 on 204 pages; `type.slots`: 703 on 182 pages

**Alternative.** Use real row gaps in shared region coordinates and nominate unowned ink at missing phases, with shorter evidence allowed when neighboring layout explains it. **Delete it:** Deleting loses19 grid additions on 16 pages unless the unified recovery model covers them; removing its clean-page scan is attractive only with a replacement scout.

**Rust.** Own interval grouping, stable sort and histogram mode; arrays of block offsets/row IDs. minAreaRect can be removed once explicit axes are carried. **Behavior to pin:** Greedy grouping order, quantile definition and rounding a pitch index can move slots by an entire row.

**Sources:** [shared/type_lattice.py](../../../prototypes/fast_lines/shared/type_lattice.py#L16), [shared/type_grid_edges.py](../../../prototypes/fast_lines/shared/type_grid_edges.py#L12), [shared/type_profiles.py](../../../prototypes/fast_lines/shared/type_profiles.py#L29), [shared/type_context.py](../../../prototypes/fast_lines/shared/type_context.py#L7). **Current comment links:** O16, O17.

### M25 — Slot body support and exact point ownership

**Verdict: merge.** One body-run/ownership query should serve recovery, endpoint completion and ink rejection.

**Feature and operation.** Inspect candidate slots at reduced then native resolution for body-bottom contacts and test whether existing polygons already own their centers. **Current contract:** Gray + slot + current polygons -> component centers/bounds, contact mode, measured y, owned fraction and support decision.

**Principle and evidence.** Recover text through repeated body contacts rather than any dark ink. Center ownership alone is a weak approximation for clipped letters and mixed rows. FEATURES_C dense/reduced slot boards; current 49 supported unowned slots on 28 pages. Short rows in d83/ef481 remain below this kind of evidence requirement.

**Constants and units.** 12 samples/h then native; contrast>.18; body height .45–1.6h, width .1–3h, area>.06h²; >=5 bodies, span>=5h, contact support>=5 and >=half; owned fraction<.25.

**Vetoes, duplication and routing.** New edge slots can be dense-checked twice: once in type_extended and again in type_recovery. Body labels are not reused from geometry/faintness. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_lattice.py:132:point_ownership`: 1994 calls on 187 pages; inclusive 0.262 / 7.953 / 145.616ms over 208, self total 50.217ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.supported_slots`: 49 on 28 pages

**Alternative.** Query shared component labels in an actual row band; establish a normal-text run with measured uncertainty, rather than a fixed five-body length floor. **Delete it:** Deleting confirmation admits decorative/faint/grid slots. Deleting duplicate dense inspection is useful after preserving an immutable certificate.

**Rust.** Own CC/point-in-polygon or raster owner IDs; masks/points as arrays. OpenCV pointPolygonTest is currently float32 and boundary-inclusive. **Behavior to pin:** Dense versus reduced components and point-on-edge behavior change owned fractions; exact shared labels are preferable.

**Sources:** [shared/type_lattice.py](../../../prototypes/fast_lines/shared/type_lattice.py#L89). **Current comment links:** O16, O17, O18.

### M26 — Table lattice, rules, dot leaders and extent protection

**Verdict: merge.** Preserve table facts in the common layout stage and let recovery operate inside typed cells/regions.

**Feature and operation.** Recognize aligned cells, printed rules/intersections and dot leaders; protect their extents from prose recovery. **Current contract:** Gray + current boxes -> regional table/uncertain rectangles, rules, dots and support status. It does not rewrite existing table cells.

**Principle and evidence.** Treating tables as distinct layout and preserving Paddle’s strengths follows the charter. Bounding region protection is coarse and may suppress genuine adjacent text. FEATURES_C table/dot-leader renderings plus prose/frame controls; the approved8314 grid remains a protection case. Main table evidence has23 regions on 7 pages; extent has3 regions on 1 page.

**Constants and units.** Letter-scaled rule/leader measurements mixed with alignment/occupancy tolerances; installed table versions5 and extent6 differ. Multiple empirical dot/component rules were added after failures.

**Vetoes, duplication and routing.** 37 table analyses on 36 pages; 6 table_extent analyses can be expensive (profile max291ms). Residual and grid branches independently request tables. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_tables.py:118:analyze`: 37 calls on 36 pages; inclusive 0.000 / 48.429 / 123.628ms over 208, self total 20.162ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.tables_regions`: 23 on 7 pages; `type.table_extent_regions`: 3 on 1 pages

**Alternative.** One region/cell graph from shared boundaries and repeated alignment, with explicit cell IDs rather than broad veto rectangles; faster reuse, greater contract work. **Delete it:** Deleting protections risks filling table rows with prose-like hallucinations; deleting duplicate table analysis is desirable with cached evidence.

**Rust.** OpenCV LSD initially or own run/rule detector; own alignment clustering, intersections and leader recurrence. Arrays of rules/cells, not nested evidence dicts. **Behavior to pin:** LSD behavior, resize phase, dot connectivity, peak prominence and greedy alignment grouping are library-sensitive.

**Sources:** [shared/type_tables.py](../../../prototypes/fast_lines/shared/type_tables.py#L15), [shared/type_table_extent.py](../../../prototypes/fast_lines/shared/type_table_extent.py#L12). **Current comment links:** O04.

### M27 — Grid-slot regional Paddle recovery

**Verdict: replace.** Task 2 merges grid and residual recovery into one unowned-row operation with a measured row frame.

**Feature and operation.** Confirm supported empty slots with a height-scaled crop inference, then require body coverage, low existing ownership and safe extent. **Current contract:** Gray, measured slot, existing/excluded polygons and session -> added polygons with type_slot provenance and decisions.

**Principle and evidence.** Independent image evidence plus detector confirmation is stronger than filling a periodic grid. Multiple area/center/crop-edge vetoes remain surrogate row ownership. FEATURES_C recovery boards and inherited73 comment dispositions.31 crop calls/21 pages emit19 additions on 16 pages; no causal ablation separates each guard’s contribution.

**Constants and units.** >=5 seeds and >=.6 seed coverage; owned ink<.25; crop edge>.15h; crop ±4h vertically/2h horizontally; native dense confirmation, mirrored ownership and table veto precede inference.

**Vetoes, duplication and routing.** Runs old type_ink ownership, repeats dense slots and tables, then snap_components/barrier guards. No shared request budget or batched model calls. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `type_correction_s` pass 1 12.562 / 260.789 / 742.341ms; pass 2 12.979 / 266.349 / 732.010ms. type_correction_s is the whole type parent correction timer, not exclusive grid-recovery time. Use run function profile for the grid branch.

**Fresh profile.** `shared/type_context.py:39:recover`: 207 calls on 207 pages; inclusive 0.012 / 93.149 / 187.180ms over 208, self total 1.007ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.grid_calls`: 31 on 21 pages; `type.grid_added`: 19 on 16 pages

**Alternative.** Region row-band recovery from normal unowned ink, with Paddle only as an optional extra localization witness; fewer reruns and acceptance guards, needs explicit short-line tests. **Delete it:** Deleting loses current grid recoveries; retain all positive crops as controls while replacing this branch.

**Rust.** Plain slot/request arrays plus ort adapter. Recovery provenance must use stable IDs; it is not detector confidence. **Behavior to pin:** Crop side quantization, inferred contour order and .25/.6 threshold boundaries affect additions.

**Sources:** [shared/type_recovery.py](../../../prototypes/fast_lines/shared/type_recovery.py#L1), [shared/type_context.py](../../../prototypes/fast_lines/shared/type_context.py#L39). No isolated open owner comment is attributed to this adapter/helper; its callers carry the relevant outcomes.

### M28 — Recovery completion, exclusion and regional separator guards

**Verdict: merge.** One exact exclusion/region contract and one endpoint completion operation; distinguish rejected ink from all whitespace inside its polygon.

**Feature and operation.** Expand a recovered polygon to supported components, enforce removed footprints and cut/reject it at native separators. **Current contract:** Candidate polygon, gray, h, existing/excluded regions -> completed/split pieces and barrier decisions.

**Principle and evidence.** Full letters and exact exclusions are sound goals. Repeated completion then rejection is a repair chain; ink expansion lacks final page-relative faintness at endpoints. R4/R5 recovery/barrier examples; 1ba p35 still demonstrates an exclusion conflict, while fixed column examples must be preserved.

**Constants and units.** h-scaled padding/component windows, raster exact-overlap test, separator widths and interior-rule checks; contrast and support gates remain independent of M35 calibration.

**Vetoes, duplication and routing.** 21 snap calls/17 pages and 77 protect calls/29 pages. Accepted columns are reapplied in residual recovery, followed by another rule detector. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_barriers.py:9:protect`: 77 calls on 29 pages; inclusive 0.000 / 3.602 / 51.268ms over 208, self total 28.073ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.grid_added`: 19 on 16 pages; `type.residual_added`: 52 on 14 pages

**Alternative.** Row endpoints and component ownership constrained by the shared region/exclusion arrays: one operation can preserve complete front letters without repeated growth and veto. **Delete it:** Deleting without replacement risks reintroducing removed ink and crossing boundaries; remove the redundant guards only after those invariants are structural.

**Rust.** Own polygon raster/scanline tests and row-band clipping; typed exclusion IDs. Prefer label intersections over large temporary masks. **Behavior to pin:** Raster boundary inclusion, local origin rounding and Shapely versus OpenCV polygon interpretations are not interchangeable.

**Sources:** [shared/type_completion.py](../../../prototypes/fast_lines/shared/type_completion.py#L9), [shared/type_barriers.py](../../../prototypes/fast_lines/shared/type_barriers.py#L9), [shared/type_context.py](../../../prototypes/fast_lines/shared/type_context.py#L17). **Current comment links:** O19.

### M29 — Uncovered-ink scout and request merging

**Verdict: merge.** Retain an explicit false-negative scout, but drive it from shared component ownership and row context.

**Feature and operation.** Find body-like ink not already owned by current polygons and merge intersecting requests for native examination. **Current contract:** Gray, current/excluded polygons and h -> reduced residual mask, 3, 156 candidate regions and 479 merged requests on 146 pages.

**Principle and evidence.** Directly addresses the charter’s warning that looking only inside detector boxes cannot recover missing rows. Uncovered ink is a nomination, not text. R5 residual boards and RECOVERY.md; all new short-row comments are now explicitly included in the review even though earlier reports did not see them.

**Constants and units.** Installed scout version 5, letter-scaled sampling/component bounds and ownership masks; rectangular request merging takes a fixed point over positive overlaps.

**Vetoes, duplication and routing.** Runs on 207 pages and can merge distant reasons into large rectangles; this is a second spatial/ownership census after geometry and grid scans. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_residual.py:127:ink_scout`: 207 calls on 207 pages; inclusive 1.729 / 4.625 / 8.136ms over 208, self total 128.529ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.residual_regions`: 3156 on 146 pages; `type.residual_requests`: 479 on 146 pages

**Alternative.** Index unowned components in region/row coordinates and request only unresolved row intervals; less broad scanning, needs a scout that still sees wholly missing short rows. **Delete it:** Deleting loses52 residual additions on 14 pages, including confirmed c0 p10#118; a field that only replaces owned rows cannot substitute for it.

**Rust.** Own raster ownership, CC and interval-union/request graph; arrays of request bounds and CSR reason IDs. **Behavior to pin:** Polygon rasterization and request merge order alter ROI extent; sorting and stable tie rules must be part of the contract.

**Sources:** [shared/type_residual.py](../../../prototypes/fast_lines/shared/type_residual.py#L127), [shared/type_residual_recovery.py](../../../prototypes/fast_lines/shared/type_residual_recovery.py#L46), [shared/contracts.py](../../../prototypes/fast_lines/shared/contracts.py#L59). **Current comment links:** O14, O15, O16, O17, O20.

### M30 — Native unowned body contact chains

**Verdict: merge.** Task 2 should use one row-membership representation for existing, clipped and unowned ink.

**Feature and operation.** Extract native bodies inside requests, assemble repeated row/contact chains and distinguish interior-owned from merely touched components. **Current contract:** Native crop and translated current/excluded polygons -> body arrays, chains, free/interior-owned indices and local body heights.

**Principle and evidence.** Body contacts and actual current ownership are explainable. Distinguishing touched versus interior-owned fixes some clipped-row cases, but fragmented/short text remains under-supported. R5 native residual experiments and the current flat short-row crops.479 native fields on 146 pages are examined for 80 eventual detector calls.

**Constants and units.** Renderer version 4, recovery version 11; chain/body geometry in local h. Eligible recovery ultimately needs >=5 free bodies over>=4h; this blocks some short continuations by construction.

**Vetoes, duplication and routing.** This is another independent CC/row graph and another height estimate, after field contacts, slot contacts and ink analysis. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_residual_recovery.py:55:field`: 479 calls on 146 pages; inclusive 7.208 / 105.914 / 212.858ms over 208, self total 142.864ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.residual_requests`: 479 on 146 pages

**Alternative.** Reuse the shared component/row graph, allowing physically supported short rows and large initials without demanding five free bodies in every case. **Delete it:** Deleting native evidence would reduce recovery to detector reruns/ink blobs; deleting it with a shared measured graph removes duplicated work.

**Rust.** Own union-find, spatial adjacency and robust fits; contiguous body and chain arrays. SciPy filtering can become explicit kernels. **Behavior to pin:** Component connectivity, chain-order ties, ownership edges and local height fitting affect eligibility.

**Sources:** [shared/type_residual.py](../../../prototypes/fast_lines/shared/type_residual.py#L15), [shared/type_residual_recovery.py](../../../prototypes/fast_lines/shared/type_residual_recovery.py#L55). **Current comment links:** O01, O03, O04, O05, O14, O15, O16, O17, O18, O19, O20.

### M31 — Residual regional recovery and rejection chain

**Verdict: replace.** Replace the chain with one band-based recovery operation in Task 2; preserve positive recovered crops and exact exclusions as tests.

**Feature and operation.** Rerun Paddle on eligible native requests, require independent body chains, trim unsafe extents and reject competing rows, weak layers, motifs, exclusions and separators. **Current contract:** Native body chains + gray/session/current rows -> added polygons with type_residual provenance, witness points and support bounds.

**Principle and evidence.** Recover text, not arbitrary ink, is the right aim. Many sequential guards now compensate for incomplete row geometry; the 3.5h multirow veto discards a real recovered row on 3229 p4. R5 residual/candidate crop boards, R6 RECOVERY.md and new short-row crops.80 calls/42 pages yield52 additions/14 pages; three R5 recovered pieces were lost in R6.

**Constants and units.** >=5 free bodies over>=4h; side from 16 samples/h; multirow height>3.5h; crop edge .15h; competing-axis margin .5h; separate version gates2–11, weak-suspect veto and interior-rule check.

**Vetoes, duplication and routing.** Reuses a private mirrored-ink copy and extra full motif path, reapplies columns and barriers, and checks ownership after each operation. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_residual_recovery.py:84:recover`: 207 calls on 207 pages; inclusive 10.472 / 224.405 / 505.986ms over 208, self total 31.724ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.residual_calls`: 80 on 42 pages; `type.residual_added`: 52 on 14 pages

**Alternative.** Localize normal unowned ink in an existing shared row band; split genuine multirow support at its measured gap instead of rejecting a tall envelope wholesale. **Delete it:** Deleting loses52 additions including owner-approved fixes; deleting just the multirow veto without correct bands admits mixed-row OCR crops.

**Rust.** Own body-owner IDs and arrays plus optional ort crop call. Refactor before porting; carrying every version branch to Rust would fossilize the experiment history. **Behavior to pin:** Greedy proposal order, center-containment predicates, crop resize and component assignment affect outputs and source provenance.

**Sources:** [shared/type_residual_recovery.py](../../../prototypes/fast_lines/shared/type_residual_recovery.py#L27). **Current comment links:** O01, O03, O04, O05, O14, O15, O16, O17, O18, O19, O20.

### M32 — Large-initial completion

**Verdict: merge.** Keep initial geometry in the shared component model; do not limit completion to newly recovered lines.

**Feature and operation.** Attach a large paragraph initial to a newly recovered row when native support and ownership permit it. **Current contract:** One added row, current items, gray and h -> possibly extended polygon plus initial_completed flag.

**Principle and evidence.** A large initial is a real typographic feature. Only additions are considered, so an initial attached to an original multirow/missed-row box is outside this route. R5 initial renderings; 71 completion calls on 28 pages produce one change.00f143 p258 second row remains absent despite the large initial.

**Constants and units.** Body-size/neighbor and extension windows are h-scaled; only result[added] is iterated. Initial completion is subsequently protected from field replacement.

**Vetoes, duplication and routing.** Yet another component/envelope operation. initial_completed is an opaque control flag that vetoes a later geometry stage. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `shared/type_initials.py:45:complete`: 71 calls on 28 pages; inclusive 0.000 / 0.402 / 6.006ms over 208, self total 0.162ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `type.initial_changed`: 1 on 1 pages

**Alternative.** Represent an initial as a component spanning multiple row bands with explicit ownership/reading-order association; retain the small text row independently. **Delete it:** Deleting loses one current improvement and simplifies routing; safe only when the shared typography/row model covers that control.

**Rust.** Plain component arrays and polygon/band union; no semantic font classifier needed for a measured oversized component. **Behavior to pin:** Connected initial/body strokes and polygon edge contact can change which row claims the initial.

**Sources:** [shared/type_initials.py](../../../prototypes/fast_lines/shared/type_initials.py#L15). **Current comment links:** O18, O20.

### M33 — Final local envelope smoothing and retention

**Verdict: replace.** Remove the separate smoother where the joint row model supplies the actual segment; retain its crop controls.

**Feature and operation.** Fit smoother native envelopes from map-guided bands, pad unique ink and veto off-row or lost components. **Current contract:** Current/type rows + original map/scout + exclusions/cache -> shaped polygons and detailed per-line decisions.

**Principle and evidence.** The owner explicitly requested smoother, cleaner OCR crops. This implementation is another per-line row model whose expansions precede page-relative faintness. R5 shape renderings and current final crops.40 triggered pages lead to 14 changed polygons on 9 pages; native work often does not alter output.

**Constants and units.** Letter-scaled smoothing/padding, empirical retention and off-row rules; field-owned/partitioned shapes can abstain. Bbox forbidden-region guards conflict with exact footprints elsewhere.

**Vetoes, duplication and routing.** Reuses or recomputes M20 map bands, M14 components and retention; overlaps field native rebuild and B row splitting. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `shape_s` pass 1 0.012 / 83.554 / 222.654ms; pass 2 0.012 / 86.202 / 231.353ms.

**Fresh profile.** `shared/geometry_envelopes.py:174:correct`: 207 calls on 207 pages; inclusive 0.024 / 105.606 / 366.673ms over 208, self total 132.335ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `shapes.trigger`: 40 on 40 pages; `count.smooth`: 14 on 9 pages

**Alternative.** Construct smooth shared band boundaries directly, keep measured whole letters/accents, and determine endpoints using page-relative normal ink. **Delete it:** Deleting loses14 accepted shape improvements but removes another retention loop; Task 2 must cover these 9 pages first.

**Rust.** Own band interpolation, low-cost smoothing and component-owner queries. Avoid repeated Shapely objects/large mask materialization. **Behavior to pin:** Gaussian borders, polygon smoothing and raster-versus-vector retention change thin accents and touching glyphs.

**Sources:** [shared/geometry_envelopes.py](../../../prototypes/fast_lines/shared/geometry_envelopes.py#L40). **Current comment links:** O02, O15.

### M34 — Final-footprint faintness scout

**Verdict: keep.** Keep a cheap nomination layer, change its sampling to the shared band/context in Task 3 and recheck negatives.

**Feature and operation.** Sample longitudinal tiles in each final box and nominate segments lacking a repeated normal-contrast run. **Current contract:** Gray/current polygons and h ->8×8 samples per h-wide tile, median contrast/reference and candidate indices.

**Principle and evidence.** Cost-following-need is appropriate; the scout samples bbox interiors rather than the full sloped polygon and can be protected by unrelated dark marks. It cannot decide faintness itself. R6 A per-segment slow/fast comparisons. Current first-pass nominations302 on 93 pages; later final-pass nominations are separately scoped.

**Constants and units.** Three adjacent normal h-wide tiles; upper-half median reference, 1.4826 MAD and ref−3 spread boundary; central half of bbox height sampled. No fixed 8-bit ink threshold here.

**Vetoes, duplication and routing.** Recomputes after geometry as required, but older mirrored ownership already made a separate tone census. Calling all tiles normal is not proof of a normal letter run. Before first native faintness; reused inside M39 after all geometry mutations.

**Measured cost.** R6 `faint_scout_s` pass 1 0.963 / 2.898 / 4.835ms; pass 2 0.941 / 2.784 / 4.965ms.

**Fresh profile.** `shared/ink_faint_scout.py:8:render`: 233 calls on 207 pages; inclusive 1.208 / 4.922 / 9.590ms over 208, self total 158.081ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `faint.candidates`: 302 on 93 pages

**Alternative.** Share per-component photometry and query row-aligned normal-run support, with a sparse scout verified against exact final-band native evidence. **Delete it:** Deleting this gate and running native faintness everywhere protects recall at prohibitive cost; deleting faintness regresses the owner-approved result.

**Rust.** Plain strided samples, min/max, median/MAD and run scans; explicit array outputs and optional diagnostic tiles. **Behavior to pin:** Integer sample placement, NaN handling and percentile/tile boundaries can hide short faint fragments.

**Sources:** [shared/ink_faint_scout.py](../../../prototypes/fast_lines/shared/ink_faint_scout.py#L1). **Current comment links:** O08, O09, O10, O11, O12, O20, O24, O26.

### M35 — Native page-relative faintness and normal-run decision

**Verdict: replace.** Preserve approved decisions while replacing the run/ambiguity and calibration contract in Task 3. Do not describe the current problem as simply len>=1: the source already says3.

**Feature and operation.** Measure components on actual polygons, calibrate normal print from page samples, separate intensity from stroke width, and remove essentially all-faint segments without a normal run. **Current contract:** Gray/final polygons -> components with core, peak, noise, width, clipping; page reference; suppress indices and exact removed polygons.

**Principle and evidence.** Page-relative photometry, whole-segment judgment and separate width are principled. Connected components are not letters. Dark short-fragment/area exceptions and biased reference samples still let ghost pieces survive; faint front print is not reliably distinguished from back-print. R6 A slow/fast component renderings are historical evidence; final integrated source differs from early prose. R6 synthetic faint-front controls remove4/5 known-front cases. New crops confirm short ghosts, mirrored header and remainder.

**Constants and units.** Native localized route uses scalar median paper plus morphological core paper, h/40 blur, 3-noise floor, Otsu, body .25–2h/.07–3h, area .006h²; 8 calibration strips of±8h; ref support>=12, optical midpoint and ref−3MAD. normal_run requires 3 bodies, but short_ambiguous and isolated-normal-area guards bypass it.

**Vetoes, duplication and routing.** First pass removes134 on 31 pages; later pass removes3 more on 3 pages, total137/34. Re-extracts components per ROI/calibration and uses GEOS to intersect calibration strips. First after M33, reused selectively inside M39. Function profile includes both calls; faint_s receipt covers first only.

**Measured cost.** R6 `faint_s` pass 1 3.240 / 51.553 / 127.036ms; pass 2 3.094 / 51.289 / 121.985ms.

**Fresh profile.** `shared/ink_faintness.py:142:analyze`: 233 calls on 207 pages; inclusive 4.258 / 87.623 / 244.658ms over 208, self total 7.173ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `faint.removed`: 134 on 31 pages; `count.faint`: 137 on 34 pages

**Alternative.** Calibrate a per-region normal-ink distribution from measured normal runs, keep ambiguity explicit, and constrain both line existence and endpoints. Use a real faint front-text line to test recoverable foreground. **Delete it:** Deleting regresses approved watermark/back-print removal; deleting short protection wholesale would also remove legitimate short front text and punctuation.

**Rust.** Own histograms, CC, distance transform/ridge and runs are feasible; OpenCV morphology/DT and geo clipping initially. Arrays must keep intensity, width and ownership distinct. **Behavior to pin:** Otsu bins, quantile interpolation, distance-transform approximation, morphology borders and clipping/raster rules change classification; intensity alone cannot infer front/back cause.

**Sources:** [shared/ink_faintness.py](../../../prototypes/fast_lines/shared/ink_faintness.py#L15). **Current comment links:** O08, O09, O10, O11, O12, O20, O24, O26.

### M36 — Multirow-segment scout

**Verdict: replace.** Task 2 should replace segment-local nomination where the shared row model applies, not run both indefinitely.

**Feature and operation.** Sample polygon-clipped strips for two body-width density bands separated by a gap, nominating native partition. **Current contract:** Final surviving polygons and gray -> candidate indices/windows and reduced profiles.

**Principle and evidence.** Two vertically separated supported rows is a real feature; a profile can also split one accented word. The scout is correctly nonauthoritative. R6 B exhaustive native/reduced/scout comparisons are evidence of method, not the final integrated count. Current709 nominees on 108 pages, versus earlier standalone B’s875.

**Constants and units.** 8 samples/h, about 4h longitudinal blocks, quantized weak floating profile noise and h-scaled peak/gap widths; skips page_field segments entirely.

**Vetoes, duplication and routing.** Adds another full segment scan after map/field/type/shape/faint passes; page_field skip assumes those bands are already correct. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `rows_scout_s` pass 1 3.225 / 9.081 / 30.935ms; pass 2 3.079 / 8.770 / 31.676ms.

**Fresh profile.** `shared/geometry_rows.py:231:scout`: 207 calls on 207 pages; inclusive 5.161 / 14.040 / 51.467ms over 208, self total 331.448ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `rows.candidates`: 709 on 108 pages

**Alternative.** Find neighboring row gaps once in the shared page model, using a cheap flat case; recover mixed original boxes as part of that same partition. **Delete it:** Deleting alone leaves owner-marked two-row segments intact; deleting with Task 2 bands removes a redundant model.

**Rust.** Plain resampling, masks, short convolution and deterministic peak detection; array windows rather than dictionaries. **Behavior to pin:** Polygon rasterization, sparse sample phase and peak ties can mistake accents or miss narrow rows.

**Sources:** [shared/geometry_rows.py](../../../prototypes/fast_lines/shared/geometry_rows.py#L231). **Current comment links:** O03, O06, O07, O18.

### M37 — Native row witnesses and white-gap partition

**Verdict: replace.** Use its physical gap/mark evidence in Task 2, but remove the parent-envelope restriction and independent per-segment decision tree.

**Feature and operation.** Confirm two complete overlapping body runs, trace an inter-row valley avoiding attached marks, and partition the parent polygon without expansion. **Current contract:** Gray/parent polygon/window -> body runs, mark links, gap path and child polygons with retained parent metadata.

**Principle and evidence.** The explicit whole-body/white-gap model is strong. Confinement to a bad parent box cannot recover clipped text or unboxed rows; window confirmation and conservative runs miss many real two-row cases. R6 B reports reviewed native/child crops, reduced-route counterexamples and 5 window losses; integrated owner verdicts remain25 fixed, 45 partly, 88 not and 1 parked among 159 two-row marks.

**Constants and units.** Native Otsu/blur, body completeness, row overlap/separation and mark-distance constraints; h-scaled DP costs with pixel floors. Limited windows must qualify before full segment work.

**Vetoes, duplication and routing.** 956 native calls on 108 pages produce42 parent partitions/18 pages. Vector union conservation does not imply raster identity; the prior B report measured raster boundary differences. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `rows_native_s` pass 1 0.844 / 87.422 / 366.074ms; pass 2 0.908 / 86.110 / 367.353ms.

**Fresh profile.** `shared/geometry_rows.py:264:analyze`: 207 calls on 207 pages; inclusive 8.131 / 115.509 / 431.476ms over 208, self total 39.580ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `count.rows`: 42 on 18 pages

**Alternative.** One ordered region row partition with shared white-gap boundaries can split a parent and extend to its real endpoints without borrowing another row’s ink. **Delete it:** Deleting before replacement loses real splits. Keep the explicit renderer/crop reference even when the installed local splitter is retired.

**Rust.** Own DP over gap arrays and component adjacency; direct band partition avoids GEOS boolean differences. Raster ownership must specify exactly one row per boundary pixel. **Behavior to pin:** DP ties, Otsu connectivity, vector intersection and inclusive raster boundaries affect tiny accents; test actual OCR crops, not only polygon area.

**Sources:** [shared/geometry_rows.py](../../../prototypes/fast_lines/shared/geometry_rows.py#L18). **Current comment links:** O01, O03, O04, O05, O06, O07, O18, O20.

### M38 — Duplicate ink-owner reconciliation

**Verdict: replace.** Remove this late repair in Task 2/4 after exclusive row ownership is structural; preserve duplicate cases as invariant tests.

**Feature and operation.** Nominate overlapping polygons, compare shared native ink and subtract ink already claimed by a preferred neighbor, possibly retiring a duplicate. **Current contract:** Final polygons and gray -> clipped/deleted polygons, inherited source IDs and iterative duplicate evidence.

**Principle and evidence.** One owner per ink body is a valid invariant. Enforcing it late with directional polygon subtraction can preserve a wrong broad owner and clip the better row; it is not a physical row model. R6 integration receipts; 61 initial duplicate pairs on 30 pages result in68 changes.44b5 p2#123 is explicitly duplicate_clipped and still misplaced.

**Constants and units.** High-overlap nomination (.8), ink-share/containment and component tests, repeated passes and polygon-area/raster tolerances. Preference/order matters.

**Vetoes, duplication and routing.** Runs all 207 active pages; receipt median29ms even on pages without a change. Duplicates ownership checks already scattered through field, type and row splitting. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `row_ownership_s` pass 1 29.076 / 93.861 / 139.635ms; pass 2 29.634 / 95.580 / 140.919ms.

**Fresh profile.** `shared/stack_ownership.py:68:reconcile`: 207 calls on 207 pages; inclusive 29.245 / 100.556 / 157.699ms over 208, self total 4314.598ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** `ownership.pairs`: 61 on 30 pages; `count.row_duplicates`: 68 on 30 pages

**Alternative.** Assign each component and boundary pixel to one ordered row at construction; reject inconsistent topology in validation instead of trimming after all stages. **Delete it:** Deleting now leaves duplicate OCR crops. Delete only once the shared band model proves exclusivity including recovered and original rows.

**Rust.** Own spatial index/owner arrays and row-band construction. Current Shapely difference/union behavior is complex to reproduce and avoidable. **Behavior to pin:** Sorting ties, iterative retirement order, GEOS multipolygon handling and raster shared-ink counts affect which line survives.

**Sources:** [shared/stack_ownership.py](../../../prototypes/fast_lines/shared/stack_ownership.py#L16). **Current comment links:** O06, O07.

### M39 — Changed-polygon faintness recheck

**Verdict: merge.** Move to one final row/ink decision; use explicit dirty IDs if a transitional recheck is still required.

**Feature and operation.** After late field replacement, row splitting and duplicate clipping, re-run faintness only on polygons absent from the pre-partition shape list. **Current contract:** Final items plus stringified polygon membership -> selected IDs, new page calibration and up to 3 further removals.

**Principle and evidence.** Judging actual OCR footprints is necessary. String representation is not a stable identity, and recalibration changes the reference while unchanged rows keep earlier judgments. Final R6 integration receipts and source; 26 calls, 3 removals. This hook is later than the standalone A/B reports.

**Constants and units.** Exact str(polygon) set membership is the trigger; otherwise same M34/M35 constants. Tuple/list or vertex-order changes can look like a geometry change.

**Vetoes, duplication and routing.** Repeated photometry/scouting is a consequence of multiple geometry mutations after the first ink decision. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Measured cost.** R6 `final_faint_s` pass 1 0.000 / 27.175 / 52.738ms; pass 2 0.000 / 27.501 / 50.835ms.

**Firing / output changes.** `final_faint.called`: 26 on 26 pages; `final_faint.removed`: 3 on 3 pages

**Alternative.** Carry component photometry through stable band IDs and make one final line decision under a consistent reference after geometry stabilizes. **Delete it:** Deleting immediately would restore3 faint fragments and stop checking changed footprints; remove only with the unified decision ordering.

**Rust.** Plain stable IDs/dirty bitsets and reused component arrays. No reason to port stringified polygon equality. **Behavior to pin:** Python string representation and recalibration sample ordering are current behavioral dependencies, not physical evidence.

**Sources:** [stack/pipeline.py](../../../prototypes/fast_lines/stack/pipeline.py#L1). **Current comment links:** O10, O11, O12.

### M40 — Composition, identity, exclusions and diagnostic transport

**Verdict: replace.** Task 4 should expose plain array functions with written units and no diagnostic dictionaries controlling decisions; preserve the file wrapper and review exporters.

**Feature and operation.** Sequence every branch, track source ancestry and removed footprints, cache selected native work, collect timings/evidence and return the final list. **Current contract:** Gray/map/items/session -> large mutable nested dictionaries with polygon lists, heterogeneous flags, parent/source indices, decisions and arrays converted to lists.

**Principle and evidence.** An explicit source/removal ledger is valuable. It is not immutable despite the contract docstring: provenance flags change control flow and evidence dictionaries carry decisions. No complete page model exists. All 215 source hashes and model/image hashes matched both R6 source receipts; all 208 stage counts and canonical output polygons matched in a fresh pass.

**Constants and units.** Fixed version arguments select installed paths; _TYPE_ACCEPTS_COLUMNS introspection is obsolete for this checked-in signature. parked boolean bypasses compose; the harness contains the explicit parked filename.

**Vetoes, duplication and routing.** Unused imports, duplicated field passes, array/list/tuple conversions, source indices and repeated bbox/height work accumulate. Export detector_record clips/normalizes outside Stack; raw tuples differ from JSON lists on 20 pages. Order is first conceptual use; shared helpers execute inside their listed callers. See the branch-aware execution graph.

**Fresh profile.** `stack/pipeline.py:33:__call__`: 208 calls on 208 pages; inclusive 372.414 / 1881.183 / 2987.317ms over 208, self total 137.415ms. Nested functions and the full call census are in the JSON.

**Firing / output changes.** Stack208 calls, compose207 active pages; returns15, 152 final segments. Parent output depends on all subordinate mechanisms.

**Alternative.** A typed immutable PageContext, stable IDs, region/component/row arrays, one geometry stage and a separate optional diagnostic sink: clear Rust ownership and cheap clean-page exit. **Delete it:** Delete obsolete compatibility branches and diagnostic construction from the hot path, not the ancestry needed for review. Removing bookkeeping without typed replacements hides errors.

**Rust.** Rust structs of Vec arrays/slices, enums and stable IDs; optional serde diagnostics at the boundary. Explicit cache keys must bind pixels, scale, regions and exclusions. **Behavior to pin:** Mutation order and mixed polygon representations currently influence routing. Canonical geometry identity, bounds and raster conventions must be part of the target API.

**Sources:** [stack/pipeline.py](../../../prototypes/fast_lines/stack/pipeline.py#L33), [stack/geometry.py](../../../prototypes/fast_lines/stack/geometry.py#L11), [shared/contracts.py](../../../prototypes/fast_lines/shared/contracts.py#L1). **Current comment links:** O19, O25.

## Every current owner comment

O01–O14 are the 14 current R6 page comments; O15–O18 are the four newly relayed R5 comments; O19–O26 are the eight older unresolved blocks. C01/C02 are the additional bend narratives, C03/C04 the false-region examples and C05 the Task 3 frame control. New comment numbers use the owner’s `reading_order(items)[n-1]`, never the numbered R6 review JPG order. Older R4 numbers retain their original reference image.

| ID / page | Status and observed outcome | Responsible mechanisms / evidence |
|---|---|---|
| O01 `s2-3229200bf47ca465a42d-p00004` | **open** — The Μαυρομιχάλης row still lacks a segment. #10 is field-owned; #11 is original source33. RECOVERY.md identifies the lost prior addition and the multirow-height veto. | M15, M17, M18, M30, M31, M37. Native crop00 plus saved item provenance and R6 recovery audit; exact counterfactual attribution is inherited from that audit. |
| O02 `s2-3229200bf47ca465a42d-p00005` | **open** — Curled words remain beyond #13/#14/#18. These final items retain original sources35/34/30, so this is failed replacement/endpoint recovery, not a successful field band cutting them. | M11, M15, M17, M18, M21, M22, M23, M33. Native crop01 and final source IDs; mechanism candidates follow the execution path, not a new ablation. |
| O03 `s2-3229200bf47ca465a42d-p00006` | **open** — #27/#39 retain broad original boxes; left words between original fragments33–38 remain uncovered. #26 is a real residual addition, which does not fix the next mixed row. | M15, M17, M18, M21, M23, M30, M31, M36, M37. Native crops02/03 and item provenance; preserve the addition while replacing row/endpoint handling. |
| O04 `s2-49598b2e848ab1f0ee1e-p00001` | **open** — Unboxed rows and curled starts are visible. #41 is a B partition child; #44/#67/#75/#90 retain original sources. R6 recovery audit attributes two returned omissions to table context and multirow rejection. | M15, M17, M18, M23, M26, M30, M31, M37. Native crops04/05; R6 RECOVERY.md for the historical losses. Table veto is not evidence that the missing text is a table. |
| O05 `s2-49598b2e848ab1f0ee1e-p00004` | **open** — Residual additions #108/#112 are present, but rows between them and curled ends remain missing. #127 is a column-cut original, not page_field. The full-page overview also shows the earlier gap. | M13, M15, M17, M18, M23, M30, M31, M37. Crop06, R4 overview57, final provenance and owner coordinates; no new OCR transcription benchmark. |
| O06 `s2-49598b2e848ab1f0ee1e-p00005` | **open** — The mixed bottom rows are real. #116/#117 are verified-curved-separator descendants of original sources1 and 0/1, not accepted page-field polygons. Attribution in the briefing to rebuilt bands is too broad for these IDs. | M02, M12, M13, M36, M37, M38. Crop07 and exact current item flags/provenance; distinguish geometric defect from the operator that produced it. |
| O07 `s2-44b5cf9e0d680b361091-p00002` | **open** — The foot is misaligned as reported. #122/#123/#125–128 are bilateral-column descendants, not page_field items; #123 has duplicate_clipped=True. shape changes are empty. Shared rows must repair inherited boxes too. | M02, M13, M36, M37, M38. Crop08, exact provenance and stage evidence; this identifies final paths, not proof that column clipping created the vertical error. |
| O08 `an-ef481610a820-p000150` | **open** — The small margin mark remains in original source38. Short/ambiguous component handling is the relevant ink path; it is not recovered text. | M06, M34, M35. Crop10 and current item identity; exact classification reason is a diagnosis to test in Task 3, not a new controlled ablation. |
| O09 `an-ef481610a820-p000151` | **open** — All four short margin pieces remain while similar surrounding pieces were removed. Current source indices46/45/31/25 retain their original boxes. | M06, M34, M35. Crop11 and current item identity; the common short-piece exception is a code-supported explanation, with component-level control still required. |
| O10 `s2-44b5cf9e0d680b361091-p00005` | **open** — The mirrored bottom running head is retained as a bilateral-column descendant of original source1. The older R4 fixed faintness verdict on this page concerns different numbered material. | M06, M13, M34, M35, M39. Crop09 and owner reading order; do not reuse an older fixed label to close this new comment. |
| O11 `s2-93f8070059f938bda524-p00001` | **open** — #1 and #5 are accepted page-field items; #5 visibly includes faint left words. #89/#117/#126/#127 retain original ghost pieces, including the right remainder of a bottom line. Final mixed-segment preservation cannot trim a faint endpoint. | M06, M16, M17, M18, M34, M35, M39. Crops12/13 and source tags; FAST_LINES_STACK also documents11 returned ghosts from the conservative faintness guard. |
| O12 `s2-86865c33eef5932c013b-p00026` | **open** — Both named polygons carry page_field=True and extend over pale back words. Whole-segment faintness correctly sees normal print in the central phrase, so endpoint classification must happen inside geometry. | M16, M17, M18, M34, M35, M39. Crops14/15 and exact provenance; confirms the geometry/ink interface failure. |
| O13 `an-c8b96a901917-p000155` | **open** — Original source90 spans the columns above the visible rule. The finite-rule certificate has no supported continuation through that row. | M04, M05, M13, M15. Crop16, current source ID and column extent semantics. |
| O14 `s2-c0b02fe229794d2fe76d-p00010` | **present in R6** — The questioned row has its own final segment #118, type_residual=1, and is unboxed in a fresh Paddle-only tile. It should be a protected recovery control, not counted as an open R6 omission. | M29, M30, M31. Crop17, fresh c0-paddle.png and final item provenance. This confirms the coordinator’s conditional reading. |
| O15 `an-ffccc97c07de-p000354` | **open** — The word ἀμέλ after the gap has no segment. #64 ends after the Arabic-script word and is a column-cut source; endpoint/grouping must allow a real word after wide whitespace. | M13, M21, M23, M29, M30, M31, M33. Crop18; row membership, not a looser arbitrary gap ratio, is the proposed remedy. |
| O16 `an-d83e7a198ade-p000099` | **open** — Διαμπάξ, διόλου remains unboxed below #108. #108 itself is an accepted residual addition, so the older fixed recovery comment on the same page is a separate success. | M24, M25, M29, M30, M31. Crop19 and source metadata; short-row support/ownership must be tested rather than assuming all page recoveries failed. |
| O17 `an-ef481610a820-p000181` | **open** — σι τὸ ἴ remains between the two boxes. The next row #20 is a residual addition. Five-body/4h–5h eligibility is an explicit limitation for short continuations. | M24, M25, M29, M30, M31. Crop20 and source analysis; precise rejection should be logged against the target row in Task 2. |
| O18 `an-00f143ecce59-p000258` | **open** — The second row beside the large initial has no separate segment. #16/#17 are original-source boxes. The crop does not justify saying #16 fully contains both rows; some second-row ink is outside it. | M25, M30, M31, M32, M36, M37. Crop21 and provenance; initial completion currently only processes added rows. |
| O19 `an-1ba3fdb1436b-p000035` | **open** — The final real row remains unboxed near the removed frame. R6 evidence says its proposal touches a forbidden footprint. Exclusion semantics must be checked at exact ink/row support, not broadened bbox space. | M08, M09, M10, M28, M30, M31, M40. Crop22 and inherited R6 disposition; do not erase the frame-removal success to recover the row. |
| O20 `an-00f143ecce59-p000192` | **partly/open** — The bottom row remains unboxed; rim removals are preserved, but a small boxed piece inside the stamp is still visible. “Watermark removed” must not imply the whole stamp interior is clean. | M07, M29, M30, M31, M32, M34, M35, M37. Crop23 and current page overview; inherit exact rim exclusions and separately test the interior piece. |
| O21 `an-7792a3301892-p000059` | **partly/open** — Bottom decoration is removed; top and side frame fragments remain. Horizontal strip recurrence is not a full frame model. | M08, M09, M10. Current R4 contact-sheet overview and inherited R6 disposition. |
| O22 `an-7792a3301892-p000104` | **open** — Frame fragments remain. Vertical repetition must be separated from genuine quotation glyphs using frame/layout evidence. | M08, M09, M10. Current R4 overview and R6 counterexample record. |
| O23 `an-c99f1c450f55-p000025` | **open** — The approved first removal survives; the upper ivy strip remains. Keep both positive and failed motif examples. | M08, M09, M10. Current R4 overview and saved disposition; old numbers refer to the R4 image. |
| O24 `s2-922e617957fca8dfafd0-p00001` | **open** — The blob remains. Strong dark mass can protect a segment from faintness, which is not a text-versus-image classifier; a blob requires a text-run/structure witness. | M02, M06, M08, M10, M34, M35. Current R4 overview and saved disposition; no claim that dark ink is back-print. |
| O25 `s2-7534648e60694be1d180-p00018` | **unresolved intent** — The comment identifies numbers without a requested change. Preserve it verbatim, do not invent a defect or mark it fixed. Task 1 can finish without resolving task-specific owner intent. | M40. Owner text; this is a review-input limitation, not a runtime mechanism failure. |
| O26 `s2-6419488b7f8e69fd20da-p00001` | **parked** — Sideways page is passed through after Paddle by the explicit parked flag. Its faintness and one two-row mark are outside the active correction comparison. | M00, M34, M35. Harness/source and current overview; orientation was not implemented or inferred. |
| C01 `s2-86865c33eef5932c013b-p00005` | **open** — 38 proposals; late decisions have21 foreign-row, 9 separate-horizontal, 4 lost-ink, 2 small-cell groups, plus 2 unowned proposals. Zero accepted early or late. The four reason counts sum 36, not38. | M15, M16, M17, M18. Full saved rejection drawing plus actual evidence.json; two unowned candidates explain the briefing count mismatch. |
| C02 `s2-86865c33eef5932c013b-p00007` | **open** — 79 proposals; 9 early and 4 late accepted. Late6 candidates remain unowned; 40 decision groups preserve small cells. A physically correct shared bend cannot rescue a bad per-row rebuild. | M13, M15, M16, M17, M18. Full rejection drawing and both early/late decision lists. |
| C03 `an-e259bbf5081c-p000198` | **design failure** — The displayed mesh spans separate columns with row-phase offsets; it is not a leaf certificate. | M13, M15. Coordinator bend drawing inspected directly. |
| C04 `an-c8b96a901917-p000068` | **design failure** — A middle fitted region crosses the two page leaves and bridges different row phases. | M13, M15. Coordinator bend drawing inspected directly. |
| C05 `an-7792a3301892-p000154` | **required future control** — Included by the Task 3 brief in addition to the 26 current comment blocks. Keep it in the common208-page regression manifest. | M08, M09, M10. Explicit Task 3 requirement; Task 1 does not invent an additional owner verdict. |

Exact current comments, native crop paths/coordinates and attribution limits are in the JSON. “Open” means the physical defect remains, not that every listed mechanism caused it. Where no controlled ablation was run, paths are identified from source, saved decisions and polygon provenance; suspected thresholds are labeled as limitations to test.

## Protecting every older fixed comment and the row marks

All 73 earlier comment blocks are retained below, including praise and unresolved material. This is a baseline protection crosswalk: the inherited R6 status is not silently upgraded based on an overview. All canonical outputs are identical in the fresh run. Current comments on the same page remain separate, especially d83 p99’s new short row and 44b5 p5’s new mirrored head.

| Old ID / page | R6 disposition | Preserved observation | Relevant paths |
|---|---|---|---|
| R4-01 `s2-6419488b7f8e69fd20da-p00001` | outside this round | The sideways page is passed through unchanged because orientation is parked. The faint boxes remain. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-02 `an-dbd045ccd84c-p000249` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-03 `an-7792a3301892-p000107` | partly | The lower seal-rim lettering is removed; the damaged top and vertical flower-frame fragments remain boxed. | M08, M09, M10, M07, M35 |
| R4-04 `s2-831443dc5e6f1ccfbaf5-p00042` | fixed | The faint bottom back-page numeric grid is removed (36 relative-faintness removals). Front table entries remain; this does not make all table cells single-row. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-05 `an-7792a3301892-p000104` | not fixed | The frame fragments remain. Vertical repeated shapes also match genuine quotation marks on a control page; repetition alone is insufficient for deletion. | M08, M09, M10 |
| R4-06 `an-3352d912f2e9-p000160` | fixed | The isolated faint bottom character is removed; normal front body print remains. | M06, M07, M34, M35 |
| R4-07 `an-466cffad2cba-p000267` | fixed | The original is now included. Seal-rim lettering is removed and the pale front body remains. | M06, M07, M34, M35 |
| R4-08 `an-d6fd2cf2f618-p000047` | fixed | The faint watermark-letter segment is removed by page-relative faintness. | M06, M07, M34, M35 |
| R4-09 `an-1be60011c435-p000215` | partly | Two seal-rim boxes are removed. The uncertain inner seal text remains boxed; pale front text is retained. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-10 `s2-7534648e60694be1d180-p00018` | not fixed | The comment does not specify what to change. The two indicated rows look like front text and remain. No intent was invented from the numbers. | M40 |
| R4-11 `s2-032eaf8e6b3b83918feb-p00004` | partly | The original is now included. One real row is recovered and 14 field bands follow curved rows. Mixed broad boxes and small residual fragments remain, so the local region is not fully clean. | M15, M17, M18, M27, M31, M33, M37 |
| R4-12 `s2-922e617957fca8dfafd0-p00001` | not fixed | The dark blob at the right remains boxed. Neither darkness nor stroke width supplies a safe generic non-text decision. | M08, M09, M10 |
| R4-13 `an-ffccc97c07de-p000152` | fixed | The faint stain segment is removed by relative faintness. This is not a general dark-stain classifier. | M40 |
| R4-14 `an-d6002cf45e4d-p000058` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-15 `s2-86865c33eef5932c013b-p00026` | partly | Four faint ghost segments are removed. Other ghost boxes and severe curved body crossings remain; the six field bands mostly affect headings. | M06, M07, M34, M35 |
| R4-16 `an-00f143ecce59-p000258` | partly | The second row beside the large I is recovered. Another missing row remains; the I belongs to the preceding row and is not moved. | M15, M17, M18, M27, M31, M33, M37 |
| R4-17 `an-ef481610a820-p000151` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-18 `an-ef481610a820-p000150` | partly | Five faint ghost segments are removed among the retained front dialogue. Some ambiguous short or mixed fragments remain. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-19 `s2-c0b02fe229794d2fe76d-p00010` | fixed | Both clauses are addressed: the top crossing is split at the central rule and the missing third-from-bottom right-column row is recovered. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-20 `an-d6002cf45e4d-p000010` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-21 `an-1be60011c435-p000120` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-22 `an-7792a3301892-p000059` | partly | The bottom flower row and seal-rim lettering are removed. The top and side decoration fragments remain. | M08, M09, M10 |
| R4-23 `s2-74cdb23a34ca4a6cd01e-p00012` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-24 `an-7792a3301892-p000154` | not fixed | The original is now included. Faint ghosts are removed, but the black flower border remains detected as text. Border removal was not broadened this round. | M08, M09, M10 |
| R4-25 `an-2cfe28da5103-p000084` | fixed | Both missing left-page footnote rows are recovered at their own small body scale. | M15, M17, M18, M27, M31, M33, M37 |
| R4-26 `an-3352d912f2e9-p000036` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-27 `an-1be60011c435-p000066` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-28 `an-00f143ecce59-p000192` | partly | Two faint watermark segments are removed and duplicate overlap is clipped. The missing bottom body row is still not recovered. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-29 `an-db97e3dd59ca-p000066` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-30 `an-e74539ae215c-p000338` | partly | The right-rim seal box is removed. Overlapping/interior watermark material is not established as removable. | M06, M07, M34, M35 |
| R4-31 `s2-831443dc5e6f1ccfbaf5-p00039` | fixed | The faint bottom back-page line is removed. Front table text remains. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-32 `an-db97e3dd59ca-p000042` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-33 `s2-74cdb23a34ca4a6cd01e-p00003` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-34 `s2-74cdb23a34ca4a6cd01e-p00006` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-35 `s2-7247ee9b1bc2374b3980-p00001` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13 |
| R4-36 `s2-74cdb23a34ca4a6cd01e-p00002` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13 |
| R4-37 `s2-74cdb23a34ca4a6cd01e-p00007` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-38 `s2-44b5cf9e0d680b361091-p00001` | fixed | The original is now included; the marked crossings are split at the printed divider. Row containment is still partial elsewhere, with small unique remnants after duplicate clipping. | M05, M12, M13 |
| R4-39 `s2-44b5cf9e0d680b361091-p00002` | fixed | The original is now included; marked crossings are split at the printed divider. Field bands improve several rows, but mixed straight boxes and small remnants remain. | M05, M12, M13 |
| R4-40 `s2-44b5cf9e0d680b361091-p00003` | fixed | The original is now included; marked crossings are separated at the central rule. This does not resolve other tall row boxes. | M05, M12, M13 |
| R4-41 `s2-44b5cf9e0d680b361091-p00005` | fixed | The faint mirrored row is separated from the front row by overlap clipping and then removed by final faintness. The front text remains. | M06, M07, M34, M35 |
| R4-42 `an-466cffad2cba-p000323` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-43 `an-ef481610a820-p000181` | partly | The longer missing list entry is recovered and the seal-rim box is removed. The short preceding fragment remains unsupported. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-44 `s2-d12a9a4feb23254f4080-p00006` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-45 `s2-93f8070059f938bda524-p00001` | not fixed | The faint ghost heading remains. Relative faintness now abstains on short/ambiguous normal-body evidence; 11 ghosts removed by task C return here. This is a recorded regression. | M06, M07, M34, M35 |
| R4-46 `an-c153f2c605b3-p000040` | fixed | The faint watermark lettering is removed; the adjacent front print remains. | M06, M07, M34, M35 |
| R4-47 `an-1ba3fdb1436b-p000012` | fixed | The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-48 `an-1f8e7d022643-p000003` | fixed | The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded. | M06, M07, M34, M35 |
| R4-49 `an-c99f1c450f55-p000025` | not fixed | The previously correct lower-strip removal is retained; the upper ivy strip still remains boxed because the full spatial verifier rejects its tall arches. | M08, M09, M10 |
| R4-50 `an-1ba3fdb1436b-p000035` | not fixed | The real last row remains missed. Its proposal intersects the already removed frame footprint; preserving that veto costs recall here. | M15, M17, M18, M27, M31, M33, M37 |
| R4-51 `s2-0ce9d1025b3f23c7119e-p00001` | partly | The 56 old back-print removals remain and six further faint segments are removed. The ghost heading “Ἀριθ. 300” remains: a connected dark mass exceeds the conservative faint-body allowance. It is not a normal-print run. | M06, M07, M34, M35, M15, M17, M18, M27, M31, M33, M37 |
| R4-52 `s2-3229200bf47ca465a42d-p00006` | partly | Ten residual/grid segments are recovered and 12 final field bands improve rows. Several lower straight crops still contain neighbouring lines; no unowned field candidate is promoted. | M15, M17, M18, M27, M31, M33, M37 |
| R4-53 `an-d83e7a198ade-p000099` | fixed | The missing left apparatus row under the reviewed 106 is recovered. Existing apparatus envelopes also receive guarded shaping; other short fragments are not claimed solved. | M15, M17, M18, M27, M31, M33, M37 |
| R4-54 `s2-661ddf05c8865e7b2c45-p00005` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-55 `s2-49598b2e848ab1f0ee1e-p00001` | partly | Regression against task C: the real central row at y=2911–2974 and its left continuation at y=2866–2973 are mostly absent (7, 612/8, 231 and 3, 678/4, 145 old owned ink pixels uncovered). Field-first composition changes the grid/table context; table protection and a subsequent multirow veto reject them. The 60 field bands and seven additions are not evidence that these old fixes survived. | M15, M17, M18, M27, M31, M33, M37 |
| R4-56 `s2-661ddf05c8865e7b2c45-p00004` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-57 `s2-49598b2e848ab1f0ee1e-p00004` | partly | Column crossings are cut; seven real text pieces are recovered and 17 field bands follow the right bend. Some right-end words remain detached or outside the bands, and some neighbouring straight crops still cross rows. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-58 `s2-c0b02fe229794d2fe76d-p00007` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-59 `s2-60f24a3d8a2d714767f2-p00004` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-60 `an-466cffad2cba-p000242` | fixed | The original is now included. Watermark lettering is removed; 17 field bands follow the body bend. The real short word “οἱ” is retained. | M06, M07, M34, M35 |
| R4-61 `s2-c0b02fe229794d2fe76d-p00005` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-62 `s2-661ddf05c8865e7b2c45-p00010` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-63 `s2-3229200bf47ca465a42d-p00004` | partly | Regression against task C: the recovered name row at y=712–801 is mostly absent (12, 558 of 13, 696 old owned ink pixels uncovered). The changed regional detection hits the existing multirow-height veto. Other field bands improve the bend, but broad straight boxes and detached starts remain. | M15, M17, M18, M27, M31, M33, M37 |
| R4-64 `s2-a0e233bc6efda91a641b-p00002` | fixed | The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect. | M05, M12, M13 |
| R4-65 `an-fd4fa0018ae1-p000035` | fixed | The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain. | M05, M12, M13 |
| R4-66 `an-fd4fa0018ae1-p000028` | fixed | The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain. | M05, M12, M13 |
| R4-67 `an-466cffad2cba-p000277` | fixed | The large E is included with the first recovered paragraph row, with its tall shoulder preserved through final shaping. The large-initial rule was not widened. | M15, M17, M18, M27, M31, M33, M37 |
| R4-68 `an-00f143ecce59-p000221` | fixed | The owner-approved missing-row addition is preserved. | M15, M17, M18, M27, M31, M33, M37 |
| R4-69 `an-fd4fa0018ae1-p000031` | fixed | The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain. | M05, M12, M13 |
| R4-70 `an-1ba3fdb1436b-p000009` | fixed | The owner-approved addition and ornament removal are preserved. | M15, M17, M18, M27, M31, M33, M37 |
| R4-71 `s2-86865c33eef5932c013b-p00005` | partly | Seven native join groups and three recovered pieces remain. All field proposals are vetoed, so internal omissions and severe curled right ends remain unresolved. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-72 `s2-49598b2e848ab1f0ee1e-p00005` | partly | Columns are separated, 16 segments are recovered and 31 field bands follow the left bend. Several marked rows are now isolated; other crops remain multirow or include clipped strips. The added-row shape improves locally but smooth segments are not universal. | M05, M12, M13, M15, M17, M18, M27, M31, M33, M37 |
| R4-73 `s2-86865c33eef5932c013b-p00007` | partly | Three recovered pieces, three joins and 13 field bands help selected rows. Severe right-end words remain uncovered; the field does not solve the whole curl. | M15, M17, M18, M27, M31, M33, M37 |

The JSON embeds all 256 R6 marked-segment records with their original polygons, R5 segment indices, matching final indices and dispositions, and binds the 318-record owner source by hash. Null/control rows are not silently counted as marks. No row-count success is inferred from extra fragments or a change in polygon count. Tasks2–4 must re-evaluate these exact marks and inspect individual OCR crops, especially the 97 one-row preservation controls and previously recovered text.

## Dead, off-path and duplicated code

“Unobserved in this run” is not equivalent to dead. The ledger separately lists the full unobserved source inventory; it includes valid import-time constants, diagnostics, tests and cold branches. The following are concrete cleanup decisions, not permission to delete the source before its replacement is validated.

| Category | Action and paths | Reason / condition |
|---|---|---|
| obsolete runtime compatibility | **delete**: `stack/pipeline.py:_TYPE_ACCEPTS_COLUMNS`, `stack/pipeline.py:unused column_evidence import` | Checked-in recover accepts column_evidence; the R4/R5 merge compatibility fork is no longer needed. |
| live duplicated implementations | **merge**: `shared/type_ink_motif_gate.py`, `shared/type_ink_motifs.py`, `shared/type_ink_photometry.py`, `shared/type_ink_recurrence.py`, `shared/type_ink_repeat_field.py`, `shared/type_ink_ownership.py` | AST comparison finds17 function definitions identical in the first five files; ownership differs mainly by optional height/reuse metadata and weak_indices. Imports alone do not justify two maintained algorithms. |
| live duplicate computation | **merge**: `type_extended.recover -> inspect_slot(dense=True)`, `type_recovery.run -> inspect_slot(dense=True)`, `type_tables + type_table_extent`, `height_proxy/bbox/line_axis`, `geometry field/native bands/rows/faintness CC` | Cache immutable measurements with pixel/scale/region identity; do not reuse stale polygon-index evidence. |
| unused alternative field builders | **delete from installed tree after archiving reference**: `shared/geometry_page_field.py:proposals`, `shared/geometry_field_correct.py`, `shared/geometry_row_ownership.py`, `shared/geometry_pipeline.py` | Stack imports field_detector.run/field_selection.apply/stack_ownership.reconcile, not these alternative application paths. Diagnostic callers are not proof of runtime use. |
| inactive version branches | **delete obsolete installed branches after reference freeze**: `type_residual_recovery.py:versions2–10 branches`, `type_contact_band.py:narrow (version2 branch)`, `type_extended.py:run wrapper`, `type_recovery.py:initial/final separator wrappers` | Installed path selects residual11/renderer4/scout5, extended2 and context4 with both separator wrappers disabled. Some branches remain reachable in experiments/tests; do not call them globally dead. |
| off-path feature research | **archive outside runtime crate; keep references needed for Tasks2/3**: `ink_edges.py`, `ink_strokes.py`, `ink_images.py`, `ink_image_structure.py`, `ink_observability.py`, `ink_stamp_field.py`, `ink_stamps.py`, `ink_type_identity.py`, `type_book.py`, `type_identity.py`, `type_rows.py`, `geometry_feature_separation.py` | No observed Stack execution and no installed decision entry. They include useful explicit renderers; the runtime does not model all charter features merely because these files exist. |
| off-path obsolete prototype families | **archive/remove from shipping import graph**: `classical_residual`, `font_guides`, `foreground_profiles`, `image_motifs`, `ink_condition`, `local_ribbons`, `map_graph`, `native_contours`, `residual_ledger`, `selective_rerun`, `sheet_lattice`, `round2.py`, `workflow.py` | Alternative experiments, not dependencies needed to execute Stack. Preserve reproducibility in git/history rather than port every family. |
| diagnostics/harness, not dead code | **retain separately**: `features_geometry/round6_*`, `features_ink/round6_*`, `features_type study/audit/publish files`, `stack/__main__.py`, `stack/review_r6.py`, `shared/review.py`, `shared/manifest.py`, `tests` | Reference images, receipts, input manifest, serialization and validation remain necessary. manifest may execute at import; unobserved cProfile functions are not by themselves a deletion proof. |
| algorithm replacement dependencies | **delete only after Tasks2/3 replace and validate**: `M17/M18 field rebuild/selection`, `M19/M20 local corrector`, `M21–M23 pair joiner`, `M24–M31 competing recovery models`, `M33 shape model`, `M36/M37 local splitter`, `M38 late duplicate repair` | Leaving old/new models side by side would preserve veto interactions and latency. Deleting first without replacement would lose approved fixes. |

There is no complete runtime font identity, book-level font model, inkiness classifier or general image detector. `type_profiles.mode` is used, but the font/guide research is not the installed decision path. `ink_strokes`/edge observability diagnostics must not be cited as runtime separation of faintness and under-inking. Skew is measured in several local axes and the shared mesh rather than one coherent region contract. This feature gap matters when assessing whether the stack is “principled”; the existence of a renderer somewhere in the tree is insufficient.

## Target stages and plain-array contracts

Keep only one authoritative region/row/ink ownership representation. The target is a proposal for Tasks2–4, not implemented code or a promised accuracy/speed result. Array dimensions and units should be checked at boundaries; avoid passing a mutable dictionary whose flags silently choose later algorithms.

| Stage | Inputs -> outputs | Required invariant |
|---|---|---|
| T0 decode/detect | `gray:u8[H,W], immutable session/config` -> `pm:f32[Hm,Wm], map_to_page:f64[2], polygon_points:f64[P,2], offsets:u32[N+1], scores:f32[N], source_ids:u32[N]` | Separate pixel centers from polygon edges; bounded coordinates; baseline absent, not guessed. |
| T1 shared scout/layout | `gray,pm,original localization arrays` -> `region_bounds:f64[R,4], region_kind:u8[R], leaf_id:u32[R], boundary_paths CSR, table/cell IDs, provisional_h:f32[R], work_flags` | Leaves/columns separated before any bend; a finite printed rule and inferred continuation have distinct evidence status. Clean flat regions use a cheap route. |
| T2 native ink context only where needed | `gray, requested regions, scale, immutable exclusion IDs` -> `labels:u32[Hr,Wr] or ROI tiles, bounds:i32[C,4], centres:f32[C,2], area:u32[C], core/peak/noise/stroke:f32[C], body/mark flags:u8[C]` | One context per pixel/scale/region. Geometry support, faintness, stroke condition and exclusion are different fields, never one binary foreground label. |
| T3 shared region row model | `regions,pm,body contacts, boundary paths` -> `mesh:f32[K,X] with explicit x/y knots per region, row_id/region_id arrays, row phase/confidence, shared gap_paths CSR` | Flat displacement is zero. Positive vertical Jacobian; ordered noncrossing row paths. Gaps follow actual white space and retain detached accents; ambiguous touching components stay explicit. |
| T4 band endpoints and unowned-row recovery | `row model, components, normal-ink evidence, typed table/exclusion facts` -> `row bands with shared boundaries, x_start/x_end:f32[L], component_owner:i32[C], source ancestry CSR, unresolved requests` | Each body has one row owner or explicit unknown/spanning status; every non-table line follows its own path. Faint endpoint ink cannot extend a normal row. Short/last/initial-adjacent rows may be nominated independently of existing boxes. |
| T5 final ink decision and output | `stable row bands, component photometry/normal-run evidence, optional exceptional regional detector nominations` -> `packed final polygon points/offsets, row/source IDs, detector score with its origin, typed exclusion IDs` | One page/region reference and one line decision after geometry stabilizes. Mixed faint/normal words preserve normal text but do not authorize faint endpoint growth. Canonical bounded polygons; raster boundary pixels use a documented unique-owner rule. |
| D optional diagnostics | `immutable snapshots of the arrays and typed reason enums` -> `JSON,rendered feature/fast comparisons,owner-number mapping,timing/source receipts` | No dictionary/string created here can affect a decision. IDs are stable; owner reading order is display-only. |

Use top-left page coordinates in pixel units throughout, with explicit transforms for model/ROI/rectified frames. Distinguish provisional detector `h`, measured body height and stroke width. Polygons should be packed `points[P,2]` plus `offsets[N+1]`; do not overload list position as identity. Component/row/region/source IDs are stable integers; ancestry is CSR arrays. Table membership, boundary continuation and ambiguous/spanning components need explicit enums, not a boolean “text” shortcut.

Specify one raster convention: pixel centers, connectivity, inclusive/exclusive polygon edges, half-open ownership at a shared row boundary, clipping to the page and how detached accents attach. Neighboring bands must share exactly the same cut. A vector partition with zero uncovered area can still lose or double-own raster pixels. The R6 integration report records27 uncovered ink boundary pixels after duplicate subtraction; that is distinct from the earlier standalone B raster audit and from whole-word losses in recovery.

Keep normal-ink support separate from “not rejected.” A mixed normal/faint line may be retained while its faint extensions are excluded from endpoints. A touching initial can span rows without authorizing two rows in one OCR crop. Sparse sampling is a nomination route and must be compared to the explicit rendering, including negatives; it must never silently establish that a page is clean.

## Rust migration boundary

The per-mechanism dependency inventories are in the JSON; these are dependencies found in source, including conditional/diagnostic imports, not a claim that every import executes. The measured path uses OpenCV, NumPy, SciPy, Shapely, pyclipper and ONNX Runtime. No scikit-image function is on the observed Stack path; do not make it a Rust requirement merely because other research tools may use it.

- Start with [`ort`](https://docs.rs/ort/latest/ort/) for the same ONNX backend and [`opencv`](https://docs.rs/opencv/latest/opencv/) for behavior-sensitive native operations. Both are bindings, not a fully Rust implementation. Pin the model and backend, and measure actual worker behavior.
- Replace NumPy broadcasting/reductions with explicit slices/loops or `ndarray`; use stable ordering and avoid materializing per-line page-sized masks. Quantile interpolation, banker's rounding versus truncation, NaNs, Otsu ties, peak plateaus and Gaussian border/truncation rules need written semantics.
- Own code is reasonable for run scans, interpolation, correlation, robust fits, spatial bins, union-find, DP gaps and row-band construction. [`imageproc`](https://docs.rs/imageproc/latest/imageproc/) is a candidate source of image primitives, not a drop-in numerical-equivalence guarantee.
- [`geo` BooleanOps](https://docs.rs/geo/latest/geo/algorithm/bool_ops/trait.BooleanOps.html) is a candidate for polygon operations. GEOS/Shapely buffer, split, simplify, difference, ring order and multipolygon behavior must not be assumed identical. Prefer direct shared-band construction and label ownership so most hot-path boolean geometry disappears. DB unclip still needs its own Clipper-compatible offset decision.
- Keep `serde`/JSON/rendering in diagnostics. The core returns typed arrays/reason codes; no `str(polygon)` identity, reflective signature check, or full experiment evidence dictionary belongs in decision flow.

These crate roles were checked against their primary documentation on 11 October2026; no crate version is selected or Rust port benchmarked here. First reproduce the revised physical model; use exact equality where appropriate for a retained backend and explicit geometric/raster invariants where the new model intentionally changes the representation.

## Tasks 2–4 in order

**Task 2.** Render region separation, shared bend, real row phases/white gaps, bands and normal-ink endpoints first. Check three curved books, the two false shared-region examples and all four newly relayed short-row/initial/wide-gap cases. Replace field rebuild/selection and local row/shape/join/recovery paths where covered; do not run both competing models.

**Acceptance:** All 73 older comments, 26 current blocks, 256 owner marks and approved ink/boundary controls; actual raw/before/individual OCR crops; one component owner, no crossing regions, no lost recovered words. Real-line placement matters more than fitting an attractive mesh.

**Task 3.** Use Task 2 stable row/component IDs for normal-run calibration, short ghosts, mirrored heads, leftovers and faint endpoint stops. Render a real faint front-print line and preserve thin dark print, pale own-page print, short words, initials and table numerals. Unify seal/motif context; solve frames and blob through positive structure evidence.

**Acceptance:** Protect all approved faintness and column cases; include5 synthetic front controls with current 4 failures openly reported and the real-line test. No new page-keyed or unexplained percentage deletion gates.

**Task 4.** Delete superseded runtime paths/versions and type_ink clones, separate diagnostics, materialize each shared array once, fuse sampled passes and move cold native work behind the physically checked scout. Specify numeric/coordinate contracts per module, then compare Rust kernels/backend wrappers.

**Acceptance:** Two fresh uninstrumented208-page passes with all dependencies charged; report clean/agreement distributions and every page >=1s. Charter target is negligible clean overhead and <1s corrections on every supplied page; do not use cProfile numbers as release latency. Coordinator alone assesses unseen44.

The priority is row ownership and physical feature agreement, then coherent ink decisions, then cost/cleanup and Rust boundaries. Safe deletion opportunities such as identical helper copies and obsolete compatibility branches are already identified, but Task 1 makes none of those code changes. Every replacement must preserve the owner-approved faintness and column cases and the real recovered rows; improving a timing table by dropping those obligations would not satisfy the charter.

## Task 1 validation

- All 215 source hashes, 208 image hashes and the pinned model hash match the frozen baseline; both R6 source receipts agree.
- Fresh execution completes208/208 pages; stage counts match208/208 and canonical final polygon lists match208/208. The20 raw representation differences are explained and individually rechecked.
- All 41 mechanisms have contracts, principle/evidence/constant notes, alternatives including deletion, Rust dependencies/numeric hazards, measured function or receipt cost, owner mappings where applicable and a keep/replace/merge/delete verdict.
- All observed profiled functions are assigned once; 26 current owner blocks, 2 bend narratives, 73 earlier comments and 256 row dispositions are retained in the machine ledger.
- Document/schema/reference checks and `git diff --check` are performed by the handoff validation. This is a read-only review: implementation tests are not rerun or represented as newly passed, and no performance improvement is claimed.

## Task 1b addendum — task 2 re-review and closure assignment (9aa8d9d)

The candidate must remain opt-in until task 2b proves complete text retention. Its shared material-coordinate core is useful; its current layout, component ownership, endpoint admission and parent retirement are unsafe. Task 2b owns those fixes and the safe default switch. Task 3 owns ink follow-up. Task 4 owns the remaining recovery/local-geometry consolidation, speed and Rust preparation. The complete 53-record assignment and ordered task checklists are in [FAST_LINES_ROUND7_ASSIGNMENT.md](FAST_LINES_ROUND7_ASSIGNMENT.md).

This addendum supersedes the earlier task sequence where it would remove M19–M33 during geometry work. The coordinator’s [T1 correction](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T1_check.md) requires retaining their approved results; task 2’s incomplete recoveries reinforce that requirement. Keep the old body/gap `geometry_page_field.render/proposals` idea as an explicitly assessed reference, not indiscriminately discarded dead code. The new M43/M44 knowingly reuse that model. The R6 final foot boxes on 44b5p2/4959p5 are clipped detector descendants; R6 early replacement did attempt to rebuild the exact parents and rejected them for another native row (verified old groups[0,2,5]/[0,2]). Thus final provenance does not mean the old field never attempted them.

No code under prototypes/ or greekocr/ was changed. Old top-level ledger measurements remain pinned to5783cec; new records M41–M52 and `task 1b` evidence are pinned to9aa8d9d/c75c04e. All 53 records now contain one assignment. No held-out page was opened. Source paths below are relative to this repository unless explicitly absolute.

### Independent verification and limits

I read both new runtime modules, the entire stack diff and B-scout change, all five study scripts and the new tests. A fresh sequential cProfile run reproduced exact saved candidate items on 208/208 pages with image/model/source hashes verified. Independently compared the 208 saved default-check detector outputs with R6:208 match; this is saved-default parity, not a new default runtime timing run. The 10 new synthetic tests pass. Timing was recalculated from both sets of 208 final receipts. Three row contexts were freshly reconstructed to investigate ownership, and 11 targeted image contexts were inspected. This is not a new complete native-pixel audit or a visual re-certification of all 256 owner marks.

| Check claim | T1b verdict and evidence |
|---|---|
| Any old segment contributing one body can be dropped without complete coverage | **confirmed**. geometry_row_context.py59-60,100-103; fresh4959 p1 item 94 parent 63/65, parent 65 has2731 sampled visible pixels absent from final. Components need not be within the admitted endpoint interval when parents are chosen. |
| _endpoints requires three normal bodies and cuts back found text | **confirmed failure, qualified rule**. No named _endpoints exists in this commit; inline geometry_page_rows.py367-383 admits localized bodies without a3-body normal run. It still lacks a complete found-text floor; 31f40 p1 loses the word ending. Census/region/ownership also contribute; no isolated endpoint-only ablation establishes sole causation. |
| 4959 p1 horizontal rule-extent cut destroys a row | **confirmed**. Accepted rule y0=2125, y1=4168; local snap yields region boundary2091.5. Fresh reconstructed regions match saved evidence; item 94 in region 4/row 0 consumes63/65 and has comb edge. Upper region 2 is vetoed. Not merely missing modeling outside regions. |
| unresolved_columns is a whole-region veto | **confirmed**. geometry_page_rows.py403-425 returns bool; adapter38 substitutes None.26 regions on 21 pages in fresh208 replay; 3 active pages have no modeled fields. |
| 8314 p20 rules are not barriers | **confirmed**. Fresh adapter has0 accepted column rules and table_regions=[]. Final item 330 spans x2259.25..3255.75 and joins1,14248 /6,33474 /45,23474 across native rules. Crop also confirms whole Παρακαμπυλίων cell lost, beyond mere word endings. |
| The new stage is added after the whole R6 stack | **qualified: substantial legacy work retained, not the whole old field stack**. Fresh profile records zero geometry_field_detector/geometry_field_selection calls. Candidate bypasses old edge/field path and B skips row_model outputs. Local correction, fragment, type, smoothing, A remain; 207 native row calls add a large cost; final ownership and faintness run afterwards. Retaining M19–M33 is required until protected recoveries pass. |
| Whole-component audit cannot see any of these losses | **too broad**. Stored audit flags19 components on 4959p1,11 on 8314p20 and 6 on 31f40p1; its own loss crops show the failures. It cannot certify partial-letter retention or Ψ/nonbody/faint text, and the 3 required controls show why pixel and native crop review are needed. |
| observe≈105ms; model≈130ms; 90th percentile≈700ms | **verified with denominator clarified**. Fresh observer profile:observe median105.614ms, model131.646ms; model p90 is378.008ms. Receipt full row-stage p90 is701.355/709.218ms. These parent/child times must not be summed, and profiler timings are not release measurements. |
| All rows on example curved pages are now correct | **local improvement only; not a verified universal claim**. T1b inspected improved marked3229p6/4959p5 contexts, but full native OCR ownership remains unadjudicated for many rows. Report itself retains partial judgments; 104 comment links and 256 mark links do not establish correctness. |

The inline blocks called `_assign` and `_endpoints` in the independent check do not exist as named functions in c75c04e. They are reviewed separately as M48 and M47; they are not omitted from the ledger. `unresolved_columns` is separately reviewed as M50, and the shared registration/inverse as M43. The model’s impossible-obstacle branch and adapter’s always-empty `uncertain_topology` deserve particular attention: monotone gaps can still cut owned text.

The table-cell, word-ending and Ψ losses are visible, not inferred from timing or operation counts. A sampled lost-ink pixel count is not a lost-character count. For example, fresh4959p1 parent 65 has2731 observed-ink pixels outside the final candidate; page-wide real-text acceptance must additionally inspect weak, oversized and partially clipped text that this census does not capture. Task 2 reports999/0/253 uncovered control pixels on c0b02#118/d83#108/3229#26; I inspected their context images but did not independently repeat those exact control-pixel measurements.

### Cost and firing

| Final receipt measurement | Pass1 | Pass2 |
|---|---:|---:|
| All 208 corrections median / p95 / max ms | 383.151 /1220.338 /1779.736 |377.660 /1197.576 /1768.128 |
| All 208 row stage median / p90 / max ms |245.599 /701.355 /1057.666 |239.841 /709.218 /1044.479 |
| Agreement40 corrections median / p95 / max ms |324.794 /469.205 /591.677 |320.619 /466.815 /572.859 |
| Corrections over 1s |30 |30 |

Both charter targets remain unmet. Native observation runs on 207 active pages, regions934, models908 on 204 pages, displacement445 calls on 197 pages, obstacles826 calls. There are26 vetoed regions across 21 pages. The adapter retires10797 input items and emits10603 polygon parts across 204 pages; neither count is an accuracy score.1843 input items receive table/orientation protection across 22 pages. The profiler’s observe/model medians are105.614/131.646ms; their inclusive costs overlap the row-stage total. Inline endpoint/retirement blocks have no isolated timer; their ledger costs state that limit rather than invent a timing.

### Current array and port contract

`Ink` carries labels i32[Hs, Ws], bounds f64[C,4], centres f64[C,2], area/tone f64[C], body/normal bool[C], scale f64[2], height f64[1], reference f64[3]. `Field` carries region bounds, sampled x, material knots, displacement, phases, paths, shared gaps, inner envelopes, component owner (-1 unknown), endpoints (NaN absent), support. `bands` produces packed f64[V,2], i32[P+1] offsets and i32[P] row IDs. Units are page pixels and pixel-squared areas; observed raster scale is explicit. These are body-centred row paths, not typographic baselines. Half-open component boxes do not settle OpenCV polygon raster ownership.

This is a useful Rust boundary but not a ready port: mean/median ridge calibration differs, region ownership can split components, gaps may have impossible obstacles, polygon export cannot represent holes, and dict/GEOS decisions remain in the adapter. Sparse source incidence, explicit parent-versus-anchor roles, native pixel ownership, valid hole decomposition and deterministic rounding/ties/borders are required. A dependency inventory is not a Rust performance result.

### M41 — Native component and photometric observation

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:43` (observe).

**What it does:** Gray image, provisional h, optional exclusion raster and normal reference become Ink labels, half-open boxes, centres, area, ridge contrast, body/normal flags, scale and measured height. Mask exclusions before connected components; fit local repeated height modes and detach accents.

**Principle and explicit evidence:** Explicit measurable paper contrast and connected ink are sound features; body classification is a tuned typography prior, not a complete text census. Otsu removes weak pixels before localized ownership is considered. Large connected text can fail body dimensions. The code comment claiming the same A statistic is too strong: this takes mean ridge contrast on the global mask; A takes median ridge contrast on a different core/paper support. Native/reduced drawings exist for all development pages; exact obstacle reduction says nothing about these labels. T1b viewed the e745 p633 Ψ and 31f40 p1 word loss; both expose coverage outside this body census. Ten synthetic tests pass but do not establish real faint-front retention.

**Units and tuning:** Morphological closing 2h (odd kernel, min 3 px); 3-noise threshold; noise divisor .954; body h/3..2h, width h/12..4h, area h²/40; local tiles 8h, mode sigma h/20 (min1 px), body >=2/3 local mode; mark distance 2bh and gap local_h/3; upper-half median, 1.4826 MAD and 3 spreads. Reduced route target 12 samples/h is experimental.

**Special cases, vetoes and duplication:** No page/book keys. Typography, compact-body, connected-word and initial classes are special cases of glyph morphology; domain limits must remain explicit. Duplicates A paper/contrast/components and the older native contact census (M14/M22/M30). A supplied reference overwrites locally computed ref/spread/boundary after that work was already done. Localized status cannot revive thresholded-away pixels.

**Cost/firing:** observe: 207 calls on 207 pages; inclusive median/p90/max 105.614/318.216/440.842 ms per208-page denominator.

**Owner effects:** O08, O09, O10, O11, O12, O18, C05. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Share one measured photometric support with A while keeping detected text ownership distinct from body/mark features; gain calibrated endpoints and coverage, pay for native refinement only where a reduced observation is unresolved.

**Delete alternative:** Deleting the new census loses body-based phase/obstacle evidence. Keeping legacy boxes alone preserves inherited text but cannot deliver the shared rows.

**Rust readiness:** OpenCV morphology/Otsu/8-CC/distance transform/dilation; NumPy bincount and reductions; SciPy Gaussian and cKDTree. Port as image kernels plus component arrays and spatial index; specify mean versus median and reference units first. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: merge.** Merge into one typed page ink context, preserving all already-found text support; body flags may propose rows but cannot authorize text deletion. Closing task **2b**, checklist **2b-01**.

### M42 — Physical layout partition and finite boundary representation

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:105` (regions); `prototypes/fast_lines/shared/geometry_page_rows.py:165` (regions.divide).

**What it does:** Collect normal or localized body boxes, restrict to detector extent with halos, find empty vertical channels, coalesce finite accepted rule cuts, split horizontal slabs, then recursively split whitespace/margin blocks into rectangular regions.

**Principle and explicit evidence:** Native whitespace and printed separators are real layout evidence. A finite vertical rule does not justify a page-wide horizontal cut through its endpoint. The implementation attempts an outward snap, but only nearby body boxes within 8h vote; this is not a certified row gap. XY recursion yields independent paragraph meshes, not one physical-column surface. Header/binding separation is incomplete. Fresh 4959 p1 reconstruction gives regions meeting at y=2091.5 from rule y0=2125; item 94 consumes parents 63/65, cuts the row and joins its lower ink to the next row. Fresh 8314 p20 has zero accepted cuts and no protected table regions; inspected numeric band crosses three ruled columns. Body columns improve on reported e259/c8 examples; leaf headers remain unproved.

**Units and tuning:** Detector halo 2h/4h; rule coalescence |dx|<h, gap<=2h; projection h/8 min1px; channel h/2 or 2h, margins6h; endpoint neighborhood8h, clearance h/4; recursion depth4; compact margin block <3h tall/<8h wide; XY gaps 2h/h/2; vertical extent12h, margins2h.

**Special cases, vetoes and duplication:** No keys. Compact page-number isolation, word-river crossing veto, recursion depth and rule coalescence are tuned layout cases. Duplicated layout among M13/M18/M24/M26 and unresolved_columns. Median-x path compression in adapter discards curved/slanted rule shape; finite cuts currently introduce horizontal ownership changes where text still exists.

**Cost/firing:** regions: 207 calls on 207 pages; inclusive median/p90/max 4.693/12.425/31.079 ms per208-page denominator.

**Owner effects:** O04, O05, O06, O07, O13, C03, C04. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Represent physical leaves/columns with finite separator paths and region membership; find horizontal transitions only in certified white gaps or carry whole components across a partial rule endpoint. Keep table cells and headers as subdomains of a shared physical surface.

**Delete alternative:** Deleting partitions refits across columns and bindings, regressing approved separation. Retaining only current rectangles keeps demonstrated text slicing.

**Rust readiness:** NumPy sort/interval union plus recursive partitions are straightforward Rust vectors; use explicit boundary polylines and region IDs instead of implicit rectangle clipping. Pin inclusive versus half-open edge ownership. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Replace rectangular rule-extent slab construction with text-safe physical-region ownership; retain approved M13 evidence and add independent native table/gutter evidence. Closing task **2b**, checklist **2b-02**.

### M43 — Shared displacement registration and inverse material coordinates

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:207` (inverse); `prototypes/fast_lines/shared/geometry_page_rows.py:215` (displacement).

**What it does:** Register adjacent vertical body-density profiles from a central x anchor, refine against their mean twice, smooth displacement and impose increasing material y knots; invert the mesh for body centres.

**Principle and explicit evidence:** One shared coordinate deformation is the owner model and a real improvement over independent line fits. It currently shares only within each rectangular block. Periodic profile aliasing and tie choices can choose a wrong phase even with monotonicity; ordered knots alone do not prove text ownership or one physical-leaf bend. Explicit native paths and route comparisons exist; T1b inspected improved row alignment in 3229 p6 context. The whole-model slow/fast identity reuses this same registration and cannot independently validate its geometry. No universal flat/skew/mixed-font correctness has been demonstrated.

**Units and tuning:** Knots roughly8h; windows ±7h; 25 lags in ±h with parabolic interpolation; Gaussian sigma1 knot/sample; two refinements; denominator eps1e-9; minimum deformed knot spacing h. Model invokes bend with >=12 bodies and both dimensions>=8h, otherwise zero mesh.

**Special cases, vetoes and duplication:** No keys. Flat fallback and minimum support/domain are physical-resolution choices with tuned cutoffs. Supersedes M15 registration/certification rather than adding another detector rerun. Independent block meshes remain a duplication of the intended physical surface.

**Cost/firing:** displacement: 445 calls on 197 pages; inclusive median/p90/max 59.442/158.646/279.193 ms per208-page denominator. inverse: 5946 calls on 204 pages; inclusive median/p90/max 0.779/3.296/8.505 ms per208-page denominator.

**Owner effects:** O01, O02, O03, O04, O05, O06, O07, C01, C02, C03, C04. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Fit a single monotone displacement per leaf/column with subregions constraining it, using multiscale body profiles and uncertainty at low support. Retain a zero/affine case under the same contract.

**Delete alternative:** Deleting deformation keeps flat pages but loses the useful curl corrections; deleting only duplicate block fits requires shared-surface coupling first.

**Rust readiness:** NumPy interpolation/correlation and SciPy Gaussian can be explicit Rust loops over contiguous grids. Preserve tie order, correlation epsilons, smoothing boundary mode and monotone projection; f64 reference parity before lower precision. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: merge.** Keep the common-coordinate method; merge block fits into a physical-region model after M42/M50 layout repair. Closing task **2b**, checklist **2b-03**.

### M44 — Row phases, component ownership, shared gaps and inner envelopes

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:273` (model).

**What it does:** Build smoothed density, transport body centres into material coordinates, find row peaks, assign each body to the nearest phase, attach small marks/connected words and initial shoulders, then constrain ordered shared gaps with pixel obstacles. A ±h tube clipped to gaps becomes each inner envelope. Endpoints are M47.

**Principle and explicit evidence:** Body-centred phases and common gaps implement the owner idea. The assignment still forces every selected body to a nearest phase; centre-in-region selection can split whole components at region crops. Body/mark/initial size classes exclude valid Ψ and mixed orientation. On impossible obstacle overlap floor>ceiling, the code leaves the nominal cut then uses maximum.accumulate; order is enforced but no valid ownership solution is established. uncertain_topology stays an empty list in the adapter. Synthetic flat/curved/initial cases pass; tests often check centres, not all glyph pixels. T1b verified comb boundary on 4959 p1 and large Ψ cut into lower bands; owner-26 on 3229 p6 follows rows better in the displayed context. Improvement is local, not a blanket all-row verdict.

**Units and tuning:** Profile x step≈h, y≈h/10 (min1px); density sigma .75h/.2h; phase smoothing h/3, peak distance h, body centre within h/2; >=2 bodies or one localized body for seed. Mark area h²/100, distance<h/2; connected word <=2h tall/12h wide; initial 2h..6h tall, h/2..6h wide and left shoulder -2h..+h. Gap search 17 offsets ±h/2 plus .01 quadratic cost, native x spacing, tube ±h.

**Special cases, vetoes and duplication:** No keys. Connected-word, initial shoulder and singleton exceptions are morphological priors; subpixel empty-field return is a legitimate finite-domain guard. Old .75h-to-Paddle-axis gate is gone, but nearest-phase ownership, seed support and body classes still filter text. Ordered gaps are not a substitute for validating every owned glyph. B skips row_model items regardless of this failure.

**Cost/firing:** model: 908 calls on 204 pages; inclusive median/p90/max 131.646/378.008/635.890 ms per208-page denominator.

**Owner effects:** O01, O02, O03, O04, O05, O06, O07, O15, O16, O17, O18, O19, O20, C01, C02. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Resolve whole-component/part-of-connected-component ownership in the shared material coordinates, allowing explicit unknown ownership; use constrained smooth white-gap paths and preserve found text until it has a full replacement. Separate table/orientation domains before assigning rows.

**Delete alternative:** Deleting the model loses missing-row and curl improvements. Keeping only phase peaks without ownership/gap repair preserves the present severe crop errors.

**Rust readiness:** OpenCV Gaussian/remap, NumPy histogram/argmin/interpolation/accumulate and SciPy peaks/Gaussian. Plain arrays are useful, but Rust must not encode these known failure decisions as a finalized contract. Declare empty domains, unknown ownership and conflict outputs. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Retain the shared representation and phase evidence, replace unsafe component assignment/conflict handling and per-pixel unconstrained gaps with complete, smooth ownership construction. Closing task **2b**, checklist **2b-03**.

### M45 — Native assigned-pixel obstacle reduction

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:257` (obstacles).

**What it does:** Map each assigned native label pixel to a sampled x column; scatter min/max y with raster clearance to form upper/lower obstacle arrays [L, X], using infinities for empty columns.

**Principle and explicit evidence:** This is a direct geometric rendering, with an independently written slow loop for the same reduction. It is principled conditional on correct labels/ownership/domain; the reduction cannot rescue omitted, split or misassigned letters. Stored route 1 ledger reports identical emitted items on 207 pages; fresh 208 candidate replay verifies final outputs. No fresh slow-operator whole-cohort rerun was done in T1b. Future checks must compare obstacle arrays directly as well as final items, especially infinities/conflicts.

**Units and tuning:** rint sample index and clipping; upper y-.5/sy, lower (y+1)/sy+.5/sy. Pixel-centre convention is asymmetric in appearance and must be specified as the actual rule, not assumed to be a generic half-open polygon.

**Special cases, vetoes and duplication:** No page, book or glyph exceptions. Efficient array version replaces slow per-pixel Python study. Later cumulative gap constraints duplicate some ordering work but are a separate model decision.

**Cost/firing:** obstacles: 826 calls on 204 pages; inclusive median/p90/max 25.797/82.910/138.474 ms per208-page denominator.

**Owner effects:** O03, O06, O18. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Single native raster pass into row/x extrema in compiled code or sparse component spans reduces temporary arrays. Verify identical obstacle arrays against the slow reference.

**Delete alternative:** Deleting obstacles lets shared cuts shave accents and initials; dropping only the slow runtime implementation is already appropriate because it lives offline.

**Rust readiness:** NumPy nonzero, indexed lookup, rint and minimum.at/maximum.at map directly to deterministic Rust loops. Min/max order-independent for finite values; NaN/inf and rounding policy still explicit. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: keep.** Keep as a pure array primitive; audit all owned text and pin its raster convention before porting. Closing task **2b**, checklist **2b-03**.

### M46 — Packed band polygon assembly

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:387` (bands).

**What it does:** Clip each finite endpoint interval to sampled x, interpolate top/bottom envelopes, join into a polygon, and remove near-collinear vertices. Return packed vertices, offsets and row IDs.

**Principle and explicit evidence:** Compact arrays are a good port boundary. This only serializes the field; it does not ensure smoothness, whole-letter coverage, valid nonzero area or no holes after exclusion. Per-pixel envelope spikes survive. Comment says exactly collinear, but actual area test uses 1e-10. T1b 4959 cut shows a comb-shaped top edge; 3229 p6 owner context contains fine spikes. Ordered-vector claims apply within one raw region, not final overlapping retained legacy polygons.

**Units and tuning:** Cross-product tolerance1e-10 in squared page-pixel units; endpoint finite/r>l check; interpolation at endpoint x. No explicit curve smoothness scale.

**Special cases, vetoes and duplication:** No page keys. Finite endpoint/empty-domain handling is appropriate. Duplicated polygon assembly and late Shapely repair in adapter; old smoothing M33 runs before these bands and therefore cannot smooth the newly generated spikes.

**Cost/firing:** bands: 908 calls on 204 pages; inclusive median/p90/max 3.587/10.705/15.214 ms per208-page denominator.

**Owner effects:** O03, O06, O07, O18. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Generate a smooth constrained envelope that contains all owned text while excluding adjacent rows, then serialize with an ink-safe error bound. Prefer a shared gap spline/polyline contract over post-hoc smoothing of each polygon.

**Delete alternative:** Deleting packed export loses usable OCR polygons. Removing collinearity pruning alone preserves geometry with larger output; deleting the spikes by unconstrained simplification can cut letters.

**Rust readiness:** Straightforward Rust interpolation and packed Vec buffers. Specify polygon winding, degeneracy, numerical tolerances and raster fill; do not rely on Shapely buffer(0) to silently decide topology. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Replace serialization of unsmoothed extrema with smooth, text-preserving band construction; retain packed-array format. Closing task **2b**, checklist **2b-05**.

### M47 — Per-row endpoint admission (the check’s _endpoints)

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:367` (model endpoint block).

**What it does:** For each row collect normal OR localized owned components; restrict bodies to repeated runs (>=3 with gap<=2h) OR localized bodies. Span admitted bodies, admit nearby marks/initials, and pad endpoints h/8 clipped to region.

**Principle and explicit evidence:** Following real row ink is principled; equating complete text with the admitted component census is unsafe. Contrary to the check’s blanket description, localized bodies need not form a three-body normal run. Nonetheless localized text outside the census/body class, beyond region bounds, or with wrong ownership can be cut. It never unions a protected pre-existing text footprint. 31f40 p1 raw/R6/T2 crop confirms the found word loses its ending; c0b02 #118 and 3229 #26 controls have reported nonzero uncovered pixels (999/253). T1b viewed those controls but has not independently reproduced their exact control-pixel totals. A count is a review prompt, not a text-loss classifier.

**Units and tuning:** Three bodies, interbody gap2h, mark proximityh/2, end paddingh/8. Uses supplied A boundary on a different tone statistic. Support is all normal OR localized bodies, not exclusively normal bodies.

**Special cases, vetoes and duplication:** No keys. Localized exception and initial exception are state-dependent admissions; unlocalized short words below three bodies cannot set a new end. Duplicates M35 normal-run logic but has different components, gap calibration and grandfathering. It conflates growth permission with retention; M48 then makes that shrink destructive.

**Cost/firing:** Included in model; do not add parent cost. O(L*C + per-row sort), no separate timer. model: 908 calls on 204 pages; inclusive median/p90/max 131.646/378.008/635.890 ms per208-page denominator.

**Owner effects:** O02, O03, O05, O08, O09, O10, O11, O12, O14, O15, O16, O17. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Maintain separate found-text support and optional extension support. Preserve the former unless the ink stage explicitly excluded it; use calibrated normal runs only for new growth, including after a wide word gap. Let short found rows survive without a three-body gate.

**Delete alternative:** Deleting the endpoint test and spanning entire regions crosses whitespace, table cells and faint tails. Removing only the shrink/admission policy in favour of complete owned text preserves the owner intent.

**Rust readiness:** Inline NumPy scans/sorts split by gaps; portable once coverage and growth flags are typed. O(L*C) scans can be grouped once by row. No separate measured function timing. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Separate retain-found-text from extend-over-normal-ink; share the ink evidence contract with M35 and make each endpoint subordinate to complete coverage. Closing task **2b**, checklist **2b-04**.

### M48 — Parent incidence and destructive replacement (the check’s _assign)

**Entry/source:** `prototypes/fast_lines/shared/geometry_row_context.py:59` (run parent assignment); `prototypes/fast_lines/shared/geometry_row_context.py:100` (run covered update).

**What it does:** A modeled row inherits every input item containing any centre of any body assigned to that row. Once any polygon part is emitted, every such parent enters covered; all covered input items disappear. Surviving old items precede emitted bands.

**Principle and explicit evidence:** Ancestry is useful but a component-centre incidence is not a coverage certificate. Parents are chosen before checking whether their components even lie within final endpoints; exclusions/invalid topology can further remove parts. Any-one-body retirement is the strongest direct design fault. Fresh 4959 p1 confirms final item 94 parents[63,65], region 4 row 0; parent 65 alone has2731 sampled visible pixels absent from final T2. This mask includes observed ink, not an OCR accuracy count. 8314 whole-cell and Ψ crops show losses at other scales.

**Units and tuning:** Binary any-incidence criterion; body membership and centre-in-polygon test, no full-pixel coverage criterion or residual partition. Scores are max parent score/default1 (not native confidence).

**Special cases, vetoes and duplication:** No page keys. Any emitted Shapely part can retire a whole parent; holes are rejected while other emitted rows may still retire the parent. Creates the need for final M38 overlap clipping; source_ids are ancestry/anchors, not proof that inherited text is present. Complete-normal-component audit cannot certify this replacement.

**Cost/firing:** Inside adapter assembly; excludes separately timed child functions only in run self-time, which is not an isolated assignment cost. run: 207 calls on 207 pages; inclusive median/p90/max 260.398/746.489/1127.873 ms per208-page denominator.

**Owner effects:** O01, O03, O04, O05, O06, O07, O14, O16, O18. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Construct total ownership of found text before retiring a parent: new row/cell bands plus explicit residual ownership must cover its text. Unknown residuals remain represented locally and become repair obligations, not a whole-page/region accept-or-reject veto.

**Delete alternative:** Deleting retirement leaves duplicate old/new crops and revives multirow contamination; deleting the row replacement keeps R6 errors. Replace the ownership transfer itself.

**Rust readiness:** Use sparse component-to-source incidence, stable IDs and ownership arrays; segment union/raster membership must have deterministic semantics. Avoid C*N dense matrices and dict source lookups on the decision path. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Retire a parent only after every kept text component/pixel has a complete owner; repair assignment, not a blanket lost-anything veto. Closing task **2b**, checklist **2b-05**.

### M49 — Row-context input/output adapter, protection and ancestry gates

**Entry/source:** `prototypes/fast_lines/shared/geometry_row_context.py:17` (run).

**What it does:** Rasterize prior exclusions; obtain h, reference and median-x accepted rules; create dense component/source incidence; run layouts/fields; detect legacy box grids and table regions, protect long vertical items; require anchors for new rows; subtract exclusions via Shapely and export dictionary diagnostics.

**Principle and explicit evidence:** Pre-seed exclusions and preserving approved column evidence meet essential contracts. Dense incidence, source anchors and exact subtraction are understandable, but this remains a mixed decision/diagnostic adapter. Table protection runs after fields were already computed; unrecognized tables enter the model. Unowned new rows require three bodies plus a nearby source, limiting genuinely short/remote omissions. 8314 p20 fresh table_regions=[] and zero approved rules reproduce the barrier failure. Reported 7534 p16 losses show tall/thin protection is incomplete for sideways tables; Ψ owner-one proves glyph size is not orientation. Stored ancestry and exclusion audits check narrow contracts, not complete text.

**Units and tuning:** Incidence area>h²/100, centre bounding-box + pointPolygonTest; box_grid version5; vertical protection height>8bh and width<3bh; new support>=3, nearest2 sources within4bh; fallback original anchor uses Manhattan centre distance; buffer(0), clip to image W-1/H-1, reject holes.

**Special cases, vetoes and duplication:** No page keys. Tall narrow exception, grid-parent veto, body-count/anchor-distance gates and hole rejection are explicit special cases. Synthetic source-ID test proves nonempty IDs only. Duplicates table analysis M26, normal calibration M35, source tracking M40 and Shapely clipping M28/M38. Exclusion holes can drop bands; nearest original anchors can cross semantic domains and must remain labeled anchors.

**Cost/firing:** run: 207 calls on 207 pages; inclusive median/p90/max 260.398/746.489/1127.873 ms per208-page denominator.

**Owner effects:** O08, O09, O10, O11, O12, O13, O18, O19, O20, O25, O26, C03, C04. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Convert legacy inputs once to typed polygon/offset/source/region/barrier/exclusion arrays; compute table/orientation domains before dense modeling; separate pure decision functions from diagnostic serialization. Represent exclusion holes by valid pieces with preserved text ownership.

**Delete alternative:** Deleting the adapter breaks required exclusions/ancestry and output compatibility. Delete its mixed dictionaries and duplicate inference after contracts migrate, not the evidence it conveys.

**Rust readiness:** OpenCV fill/point tests, NumPy arrays and Shapely GEOS union/buffer/difference plus legacy table helpers. Port raster incidence/spatial indexing and polygon operations with pinned edge semantics; provide an explicit hole-capable intermediate or safe polygon decomposition. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Replace with a typed boundary adapter and explicit domain/ownership arrays; keep diagnostics outside decisions and keep all approved exclusions before seeds. Closing task **2b**, checklist **2b-01**.

### M50 — Whole-region unresolved-column veto

**Entry/source:** `prototypes/fast_lines/shared/geometry_page_rows.py:403` (unresolved_columns).

**What it does:** Find repeated nonoverlapping wide localization pairs whose inter-source gap has similar x and spans enough y; mark the entire region unresolved. Adapter substitutes None instead of a field.

**Principle and explicit evidence:** Protecting independent columns is necessary; declining all modeling for a region is still a veto under a new name, not boundary construction. It preserves some legacy boxes but loses the old field’s corrected text and leaves unresolved inherited rows. Fresh replay:26 vetoed regions on 21/207 active pages. 4959 p1 regions0 and 2 are vetoed; region 4 is modeled and damaged by the separate cut fault. Three pages have no modeled field. These facts distinguish skipped coverage from accepted correctness.

**Units and tuning:** Sources width>=12h; gap midpoint x cluster±h; witness y span>=12h. No explicit native boundary returned.

**Special cases, vetoes and duplication:** No keys. Repeated-wide-source assumption is a layout-specific guard. Direct descendant of M18 horizontal-source protection. Cheap computationally, expensive in omitted correction; cannot be removed until boundaries are enforced structurally.

**Cost/firing:** unresolved_columns: 207 calls on 207 pages; inclusive median/p90/max 0.112/0.283/0.666 ms per208-page denominator.

**Owner effects:** O04, O13, C03, C04. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Use these witnesses to form local source-column constraints, verify native gutters/rules and fit within each supported column; preserve local unknown text explicitly instead of suppressing the whole region.

**Delete alternative:** Deleting the veto alone rejoins approved columns. Delete it only with a demonstrated replacement for its separation guarantee.

**Rust readiness:** NumPy loops become sorted interval/spatial-index arrays in Rust; output boundaries/ownership/unknown intervals, not a bool that conceals unmodeled text. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Replace whole-region suppression with constrained subdomain ownership; preserve every fixed column-boundary case. Closing task **2b**, checklist **2b-02**.

### M51 — Opt-in stack orchestration and row-model B bypass

**Entry/source:** `prototypes/fast_lines/stack/pipeline.py:27` (Stack.__init__); `prototypes/fast_lines/stack/pipeline.py:51` (compose); `prototypes/fast_lines/shared/geometry_rows.py:235` (scout).

**What it does:** Default remains R6. Opt-in disables edge scout/old field detector/replacement, performs approved cuts, retains local geometry/joining/type recovery/smoothing/faintness, inserts native rows, skips B for row_model items, then runs final ownership and changed-footprint faintness.

**Principle and explicit evidence:** Keeping an unsafe candidate opt-in is correct. The full R6 stack does NOT also execute: old page-field placement and its second Paddle are bypassed; B abstains on modeled outputs. But most legacy corrections still precede full native observation on 207 pages, and M38/M39 can modify results afterwards. This is not the final replacement architecture. Fresh208 candidate exact replay; saved default-check208 items independently equal R6. Receipt corrections medians383.151/377.660ms, maxima1779.736/1768.128ms,30 pages>1s both passes. Agreement medians324.794/320.619ms. New10 synthetic tests pass. No fresh default runtime pass in T1b; saved-default parity and diff are the evidence.

**Units and tuning:** row_model bool false by default; faint reference supplied only with support>=12; full native route selected unconditionally. M36 now skips either page_field or row_model flags, with the old tall-polygon guard retained.

**Special cases, vetoes and duplication:** No new runtime page keys; existing explicitly parked orientation harness remains a cohort status. Support>=12 reference fallback is a calibration gate. Legacy geometry/recovery is legitimately retained until recoveries pass, yet duplicative for eventual architecture. B’s flag exemption does not certify row correctness; M38 prioritizes page_field, not the new flag. Added page_rows count and row_model=None mean full evidence-dictionary identity differs even when default detector items match.

**Cost/firing:** run: 207 calls on 207 pages; inclusive median/p90/max 260.398/746.489/1127.873 ms per208-page denominator. Release receipt timings are in the addendum table.

**Owner effects:** O01, O02, O03, O04, O05, O06, O07, O08, O09, O10, O11, O12, O13, O14, O15, O16, O17, O18, O19, O20, O25, O26, C01, C02, C03, C04. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** One ownership-preserving geometry path with calibrated ink/exclusions upstream; cheap need dispatch and native endpoint/boundary refinement; retain indispensable legacy recovery until equivalent approved results exist, then consolidate in task 4.

**Delete alternative:** Deleting opt-in candidate now preserves default but loses useful development work. Deleting legacy recoveries immediately violates failed control checks. Remove the obsolete field branch only after 2b promotion gates pass.

**Rust readiness:** Public file/session shell can remain outside the numeric core. Replace evidence-dictionary transport, polygon-string identity and runtime signature compatibility tests with explicit typed stage contracts and diagnostic collectors. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: replace.** Promote a repaired single row path only after complete no-text-loss and owner checks; remove covered old field/B paths, retain necessary recovery until task 4 proof. Closing task **2b**, checklist **2b-08**.

### M52 — Offline round-7 studies, audit/gallery and synthetic tests

**Entry/source:** `prototypes/fast_lines/features_geometry/round7_rows.py:1` (round7_rows); `prototypes/fast_lines/features_geometry/round7_evidence.py:1` (round7_evidence); `prototypes/fast_lines/features_geometry/round7_benchmark.py:1` (round7_benchmark); `prototypes/fast_lines/features_geometry/round7_retention.py:1` (round7_retention); `prototypes/fast_lines/features_geometry/round7_review.py:1` (round7_review); `prototypes/fast_lines/features_geometry/test_page_rows.py:1` (test_page_rows).

**What it does:** Study raw/native/reduced fields, substitute slow obstacle reduction, compare routes, benchmark source-pinned fresh stacks, count whole untouched normal components, produce owner-mark/comment galleries, and exercise10 synthetic cases.

**Principle and explicit evidence:** They belong outside runtime. Explicit rendering and falsification are valuable. Route 1 changes only obstacles and shares all other model errors; route 2 nearest-path matches are not bijective and do not prove topology equivalence. The normal-component audit ignores partial loss, large nonbody text and all not-normal ink. Owner ledgers deliberately report unresolved correctness, which cannot become acceptance by link/count completeness. T1b read every introduced study/test, independently recomputed timing from 416 receipts, verified208 saved default comparisons, replayed208 candidate outputs and ran10 tests. Viewed both loss and improved contexts. Did not rerun207 slow obstacle studies or visually certify all 256 marks; those remain explicit future acceptance work.

**Units and tuning:** Offline plot sizes/crop padding and nearest-match32 samples are presentation/diagnostic settings. Retention uses oldcount>0/newcount==0; grouping3h/8h is crop clustering, not runtime acceptance. Synthetic fixtures use four simple rectangular-body rows, not real faint front print.

**Special cases, vetoes and duplication:** Page selectors are allowed offline cohort filters, never model rules. round7_retention executes at import (sys.argv[1]), so keep it out of imports and give it a main guard during cleanup. Several render/mask/manifest loops duplicate other study utilities. final row ledgers intersection/exactness checks and nonempty ancestry are narrow diagnostics. Old normal-component audit actually flags31f40,8314,4959; the check’s assertion that it sees none of those is too broad.

**Cost/firing:** Not a runtime stage. slow obstacle loop traverses all assigned pixels in Python; benchmark includes complete stack; gallery/audit cost is separate and must never be reported as correction latency.

**Owner effects:** O01, O02, O03, O04, O05, O06, O07, O08, O09, O10, O11, O12, O13, O14, O15, O16, O17, O18, O19, O20, O21, O22, O23, O24, O25, O26, C01, C02, C03, C04, C05. These are responsibility/control mappings, not blanket fixed verdicts; see the 53 assignments and case suites for required crops.

**Alternative:** Keep one offline reference/audit harness with native pixel plus component ownership and crop verdicts, one cohort manifest, explicit slow/fast array comparison and stage-isolated timing. Archive superseded iterations with provenance.

**Delete alternative:** Deleting runtime imports is appropriate (none presently); deleting all studies would remove the evidence needed to validate fast routes and Rust. Delete duplication/obsolete runners after a canonical harness reproduces evidence.

**Rust readiness:** No Rust runtime port needed. Reference Python can remain as an oracle; portable fixture arrays, expected invariants and receipt formats should accompany Rust tests. Pin component connectivity/IDs, ties, rounding, scale conversion, border handling, interpolation and polygon raster ownership. No Rust port or speed parity has been measured.

**Verdict: keep.** Keep as offline reference/acceptance tools, consolidate duplicate runners in task 4; never put study or owner/page-key logic on the path. Closing task **4**, checklist **4-07**.

### Effect on the earlier41 verdicts

Only M16 and M20/M23/M27/M31/M33 change their verdict verb; the other entries below refine destinations, dependencies or evidence. The original verdict/reason is preserved under `task 1_verdict` in the ledger.

| Mechanism | Current verdict | Task 2 consequence |
|---|---|---|
| M11 |merge |M51 bypasses the old edge scout; the proposed reduced row route is not a validated replacement. Task 4 must retain missed-short-row sensitivity in cheap dispatch. |
| M13 |keep |Task 2 carries approved cuts but reduces paths to median x. Keep the M13 certificate; repair its M42/M49 consumers and add independent table/gutter evidence. |
| M14 |merge |M41 is another native census; converge on one context, after geometry and ink ownership agree. Do not interpret the new body mask as all text. |
| M15 |replace |M43/M44 are the concrete replacement core, still unsafe as a full page model because layout blocks are independent and assignment loses text. |
| M16 |delete |Delete the old unbend-and-second-Paddle placement from runtime once repaired rows preserve its found text. It is already bypassed by the candidate, not running alongside it. |
| M17 |replace |Replace with M44–M48 complete row ownership. Shared ordering does not by itself prevent clipping when components or regions are wrong. |
| M18 |replace |M50 merely moved horizontal-source protection into a whole-region veto. Replacement is not closed until structural boundaries preserve all approved column cases. |
| M19 |merge |Retain through 2b. Task 1’s broad early-retirement sequence is superseded by the coordinator correction and the failed task 2 recovery controls. |
| M20 |merge |Changed from unconditional replacement destination: consolidate local correction into shared context, retaining indispensable behavior until every approved result is reproduced. |
| M21 |merge |Retain joining nominations through 2b; merge later after shared ownership reproduces each good fragment join. |
| M22 |merge |M41 duplicates native contacts; consolidate in task 4 after complete text preservation, not by simply substituting body flags. |
| M23 |merge |Changed from replacement to conditional consolidation with shared ownership/barriers. Task 2’s unsafe parent retirement is not a substitute for good joins. |
| M24 |merge |M44 phase/contact model can consume pitch/slot evidence, but unlocalized short-row gates and table gaps show native recovery is not complete. |
| M25 |merge |Use M48 complete ownership in the shared candidate context; keep approved native support and recovery while migrating. |
| M26 |merge |8314 p20 proves table protection and approved column rules do not cover every printed cell barrier. Fix the row consumer in 2b; consolidate evidence in 4. |
| M27 |merge |Changed from replace: retain necessary regional Paddle recovery within one recovery service until actual native equivalence. Task 2 does not prove it redundant. |
| M28 |merge |Exact exclusions must precede rows and survive completion; M49 adds hole-rejection risks. Integrate complete recovery and barrier ownership in 4 after ink3. |
| M29 |merge |New row phase candidates still miss short/isolated text. Keep unowned requests until shared candidates reproduce their approved gains. |
| M30 |merge |M41/M44 are not a complete unowned-text census. Merge contacts only after found faint/large/connected text is represented. |
| M31 |merge |Changed from replace: all three approved controls block premature residual-recovery deletion; keep indispensable residual detection while consolidating in 4. |
| M32 |merge |Task 2 initial shoulders are a useful idea but the owner-one Ψ is a counterexample. Consolidate only with whole-glyph ownership and existing approved initials. |
| M33 |merge |Changed from replace: old smoothing runs before the new bands and cannot correct their spikes. Retain good behavior until final shared envelopes are smooth and complete; consolidate in 4. |
| M35 |replace |New endpoint logic exposes incompatible ridge statistics and another run rule. Task 3 must share calibrated evidence with geometry, protecting existing found text. |
| M36 |replace |The new row_model flag merely exempts outputs from B; it does not close row correctness. Replace covered domains in 2b, retaining explicit residual domains. |
| M37 |replace |M44/M46 can replace covered partitions only after complete glyph ownership and all owner marks pass. |
| M38 |replace |Late overlap clipping still operates on candidate bands and does not specially prefer row_model. Close complete ownership in 2b before promotion, not as deferred cosmetic cleanup. |
| M39 |merge |A changed geometry can both revive faint tails and cut faint front print. Stable text/ink-generation identities replace polygon-string membership in 3. |
| M40 |replace |Task 2 remains a mixed opt-in architecture. Task 2b owns safe default promotion; task 4 owns remaining consolidation, typed transport and full r7 benchmark. |

### Evidence locations and verification scope

- Task 2 report: [FAST_LINES_ROUND7_T2_ROWS.md](FAST_LINES_ROUND7_T2_ROWS.md); artifacts `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2_rows/final`.
- Read-only T1b scripts/receipts/crops: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/.astra/r7_task1b`; replay208 pages, reconstructed3 contexts, viewed11 images,10/10 synthetic tests. `task 1b` in the ledger embeds source hashes, timings, claim checks and visual manifest.
- Source and artifact identity do not make the candidate correct. No r7 benchmark, Rust port, code correction or held-out evaluation is claimed by this documentation-only review.
