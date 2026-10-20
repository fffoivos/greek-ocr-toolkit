# R8-04 iteration 1 — remove repeated field and glyph work

**The default stack now does less field and glyph work while preserving every accepted development output. G4 remains PARTIAL.** The fresh 208-page run retains all 15,093 items, all exclusions and all recorded non-clock feature decisions from checked 5961754. Corrections have a 199.421 ms median, 1287.272 ms p95 and 2007.555 ms maximum; 22 pages still exceed one second. No geometry, typography or ink-source failure is claimed fixed.

The launch checkout was `8c870a8`, a planning-only merge above `5961754bde92badddc14e8d403fd2a6a791eec65`. Its 190 runtime files matched 23ee49c, as specified. This candidate changes the runtime computations described below. It preserves the NaN inverse/certify correction, its consumer tests, all prior reuse and M06 propagation deletion. There were no edits to `greekocr/`, other worker trees or planner helpers, no held-out access, PDF text, extra agents, background jobs, pushes or successor launch. The supplied launch meter was 80%; no current meter is available.

Evidence is under [R8-04-i1](../../../../.astra/fast_lines/out/round8/R8-04-i1/index.html): `ACCEPTANCE.json`, `OPERATION_DELTA_208.json`, the six-control `OPERATION_DELTA.json`, `TIMING.json`/Markdown, full detector/evidence JSON, native crops, `PILOT_REUSE.json`, `CONSOLIDATION_DELTA.json` and `ITERATION_HANDOFF.json`. `runtime/source.json` binds the actual candidate; `work208-*` and paired receipts bind both implementations independently. Instrumented clocks are never used as performance evidence.

## What was removed from live callers

| Feature and provider | Before → candidate | What stays fresh |
|---|---|---|
| M15 `geometry_page_field.render` → `shifts_many` | Repeated squaring/reduction of the unchanged refinement template for every column → pass its already-computed energy to each batch | Every new mesh/template refinement; sequential outward propagation; image/exclusion/region/rule inputs |
| M17 `native_bands` | Sort all row distances for a two-distance margin → partial partition; Python ambiguity loops → equivalent array evaluation; scan all owners for each row → group once | Argmin tie ownership, margins, complete-component/mark thresholds, envelopes and all downstream decisions |
| M17 `separate_bands` → existing `geometry_rows.valley_path` | Recompute invariant pair nomination; allocate full gap cost planes → pass nominated pair geometry and evaluate cost only at the solver's existing lattice | Native dilation on the full exact ROI and border, sequential current-shape distance/split decisions, native component-crossing checks |
| B5 `glyph_pixels` → `normalized_glyph` → `glyphs` | Repeat patch extraction/resize/blur/vector normalization for the identical prepared component → retain fixed tiles/vectors in the existing exact-ROI preparation | Height/area/border/limit selection, independent writable tile/vector copies and fresh glyph/line records |
| B5 `ink_ownership.analyze` → `glyph_atlas` → `match_glyphs` | Build the same ordered atlas matrix/aspect array for each query → prepare once per invocation | New census/order/analysis rebuilds; query vectors, direct/reflected GEMMs, votes, anchors and source decisions |

The discarded full cost entries were never read by the existing DP. This is not lower raster resolution, a different path lattice, a cropped morphology operator or a new row model. `valley_grid` exposes the old coordinates; M37's ordinary full-cost callers remain supported. Only immutable pair geometry is passed through separation: mutable polygon distance and ownership decisions still execute in their original sequence.

Glyph sharing is narrow and invocation-local. Its identity remains the same immutable gray object, exact clipped ROI and threshold, with read-only labels/stats and that census's component ID. Different image/ROI/threshold preparation is rejected or rebuilt. The fixed 22×22 transform does not depend on engineering height; height-dependent selection still runs. Cached tiles/vectors are read-only, but every returned record owns writable copies. Atlas arrays are owned immutable snapshots of the exact ordered membership; they are never shared across analyses. There is no new global/page cache, content-key lookup, decorator, ContextVar or replay of final results.

The physical quantities and limitations are unchanged: M15 correlates density profiles, M17 uses rectified component geometry and gap penalties, and B5 compares normalized optical shapes. None establishes a semantic baseline, a universal body height or front-source certainty. The removed unused M17 body-height median had no consumer; its deletion is not counted as removal of a height authority. Definitions remain **height 6 / ink 9 / ownership 9 / bend 7**, arithmetic modes 2, with zero physical subpolicies or bend authorities removed.

Runtime delta against 5961754 is **+88/−48 = +40 lines**. Cumulative against d5dc3e2 it is **+275/−750 = −475**; against caafbc5, **+359/−639 = −280**. Added helpers implement active sharing and the sampled-cost contract; extraction/renaming is not claimed as an algorithm or definition reduction. Tests, offline scripts and task documentation are separate in `LINE_DELTAS.json`. Inherited deletions are not counted again as this iteration's work.

## Measured work, including added copies

The same offline instrumentation ran on both sources over all 208 pinned development pages. It observes actual frame inputs and kernel calls, hashes inference request rasters and maps, and verifies final exports. Counters include full native operator inputs, not only Python call names. They are outside the timed default route; their substantial Python/hash overhead is not subtracted from or confused with benchmarks.

| Work over 208 pages | Baseline | Candidate | Change |
|---|---:|---:|---:|
| M15 template-energy input elements squared/reduced | 28,198,520 | 9,531,200 | −18,667,320 |
| M17 float gap-cost elements constructed | 165,031,416 | 6,587,953 | −158,443,463 |
| Owner entries visited when grouping rows | 12,318,429 | 156,577 | −12,161,852 |
| Full distance sorts / two-distance partitions | 44 / 0 | 0 / 44 | Same distance population, less ordering work |
| Glyph tile resize and blur pairs | 18,814 | 16,798 | −2,016 pairs |
| Atlas matrix/aspect builds | 184 | 47 | −137 net |
| Atlas array allocation bytes | 112,687,848 | 30,960,144 | −81,727,704 |
| Added owned tile/vector copy bytes | 0 | 72,847,808 | +72,847,808 |
| Detector inference requests | 363 | 363 | No duplicates or removed requests |

The full native dilation, CC8, remap and box-filter calls are unchanged. Gap **solver** entries and correlation lag observations are unchanged; only unused cost-plane entries and repeated template energy disappear. The partial partition still reads the same distance matrix. Owner visits are Python/array bookkeeping, not pixels. These distinctions prevent a smaller call count from hiding a larger scan.

Tile reuse occurs on six pages: ef481 p150, 0ce9 p1, 6f045 p1, 93f8 p1, d1ed p1 and dfcc p1. On 0ce9 it saves 352 resize/blur pairs and changes atlas builds from 66 to 2. This does not establish a broad ink-stage speed gain. One empty-query case, 778 p17, now prepares one atlas where the old matcher prepared none; that added work is included in the net totals and remains a small laziness opportunity. New normalization storage is 3,872 bytes per constructed tile/vector pair, plus dictionary overhead; returned copies above are charged separately. Per-page constructed bytes bound retained tile storage but are not measured process peak. No tile or atlas survives a page invocation.

All 363 inference inputs, resize sides, tensor shapes and output maps match between sources. There are **no identical within-page inference requests** in this census. Regional inference cannot be removed as duplicate work. The supplied profiles also had one M15 render per page: no duplicate whole-field construction was invented or claimed deleted. Different unbent regions remain distinct inputs.

## Preservation and review

The fresh uninstrumented 208 pass and both instrumented work censuses reproduce the accepted outputs. `ACCEPTANCE.json` compares every item, exclusion and non-clock feature record; timings alone are excluded. No tolerance hides a feature difference. All input hashes, model identity and runtime source files are bound. Both paired timing orders also reproduce accepted exports. There are zero changed final crops requiring a new loss/ownership adjudication.

Ten native control contexts and masked/display-normalized crops were freshly rendered and inspected. They cover the six M33 regressions and four retained p5/p7 rows. The accepted πό and accent on 466 p277 remain; its tiny trailing horizontal mark is still outside. 7792 p138 keeps terminal punctuation/left-edge support, and c8 p36 keeps the isolated tick of uncertain identity. Useful M33 narrowing on 9ea p202, dbd p359 and d323 p138 still excludes preceding-row support. P5 residual rows 40/41 retain “ἀποξήρανσίν”; terminal curl tops remain clipped. P7 “ἀμπέλων” and row 40 remain prior type-slot recoveries, with existing tight boundaries. P5 row 5 remains unmatched.

The source/input/output-matched **23-pilot/127-mark** native review is explicitly reused and linked per page and image in `PILOT_REUSE.json`; it is not represented as a fresh adjudication of every mark. All affected recorded field/ink feature decisions were compared afresh. All **104 comments and 256 marks** preserve every original field, quote, polygon, number and prior status; only current source/equality lineage is appended. Historic c0#118, d83#108, Ψ/E, weak τῆς, pale 1be6 and the current 0ce9 dispositions are unchanged. Already missing 3229/4959 recovery support, grouped 30/31/32, ffccc's wide-gap word, multirow crops and unresolved mixed tails remain open. Equality preserves those failures rather than closing them.

The suite reports **278 passed, 1 known strict faint-front xfail**. New meaningful checks cover exact gap sampling with native border ink at three engineering heights, fresh versus reused matching, changed atlas membership/order, changed image/ROI/threshold, height/limit changes and unaliased mutable records. Existing inverse fold/edge, render finite-phase and mutation-tested `certify` consumer tests remain. The fully faint-front failure is unchanged and explicit.

## Timing and the incomplete clean-page gate

Uninstrumented pairs use the same native files, ONNX model, Paddle settings and all correction dependencies. Source order is baseline→candidate in forward page order, then candidate→baseline in reversed order. OpenCV actually reports **10 threads**; the requested Mac cap is not assumed enforced. ONNX uses CPU sequential execution with intra/inter threads 1. Decode and unchanged primary Paddle are separate controls, never subtracted to normalize correction gains. Startup and first-page versus subsequent execution are recorded separately. Exports, galleries, content hashing and offline references are outside the clock; no runtime preparation is moved there.

The initial 83-control union accidentally omitted 0ce9. A separate four-profile-page pair in both orders repairs that omission, with raw receipts retained; aggregate reporting uses 84 unique controls, including all 22 slow pages. This is documented rather than silently changing the earlier denominator.

A short offline JSON comparison overlapped part of the reversed baseline process. It was not a profiler or kernel benchmark, but it may contribute load; other machine activity was also uncontrolled. The raw timing and detector/decode controls remain unadjusted. Field savings are supported by both source orders and the independently counted removed operations, with this measurement limit disclosed.

| Paired result, candidate minus baseline | Forward pair | Reversed pair |
|---|---:|---:|
| All 84 corrections, median / total ms | −2.602 / −1434.397 | −1.180 / −1129.208 |
| Active field proposal, 43 pages, median / total ms | −16.340 / −993.322 | −20.659 / −1083.147 |
| Ink stage, total ms | −40.473 | +40.616 |
| Primary detector, total ms | +26.315 | −71.936 |
| Decode, total ms | −4.412 | −37.191 |

The field-stage reduction is repeatable across both orders and accompanies measured removed work. The small overall median and mixed ink deltas do **not** support a blanket per-page speed claim. 4959 p1's field stage falls 57.814/64.942 ms; p5 falls 40.365/32.768 ms. 0ce9 corrections change only −1.713/−3.634 ms, with mixed component timings: its historical approximately +200 ms debt versus cb4d6b4 remains. No material unexplained regression is carried as a speed gain.

The fresh full run is **199.421 / 1287.272 / 2007.555 ms** corrections median/p95/max; file-to-final is **338.899 / 1497.622 / 2196.551 ms**. All 22 slow pages and stage costs are in `TIMING.md`. The old accepted 194.913 / 1310.153 / 2002.474 distribution is a different session, not a causal delta. Nested clocks are not summed. This iteration supplies one fresh full timing pass plus paired controls; it does not claim the required two-pass G4 gate.

Clean-page qualification is **unfinished**. Agreement is insufficient: native inspection of db97 p90 shows clipped Cyrillic descenders, and quiet f9ec p12 shows tight μ/ρ/γ lower support. `CLEAN_REVIEW.json` records those negatives, the wider overview screen and raw native strips. No page has been falsely certified clean to produce a favorable number. Absolute extra cost against the same Paddle-only setup is available per page; the 40 agreement pages have 65.754 / 561.999 / 642.094 ms correction overhead, but these are **not clean-page statistics**. R8-04-i2 must complete a genuinely native-reviewed clean cohort as well as the two fresh full passes. This unmet deliverable is part of the PARTIAL result.

## Exact handoff to speed iteration 2

Candidate profiles remain dominated by field work. On 4959 p1, instrumented M17 is 877.6 ms: M15 296.1 ms, native bands 320.9 ms including separation 204.6 ms, and unbend 75.2 ms. These overlap and are diagnosis only. Field energy reduction leaves interpolation/lag construction and certification; separation still pays sequential native crossing and shape work. Row reconciliation totals 8.248 s in the full uninstrumented run, type 11.500 s, field proposals 26.238 s and ink 6.128 s. The next prompt should choose a demonstrated repeated scan or equivalent calculation there, preserving current dependencies.

Specific opportunities are existing-mesh interpolation/coordinate preparation, repeated component-region scans in certification/separation, immutable polygon/raster observations within reconciliation, and the small atlas/normalization allocations where no reuse occurs. Inspect the new profiles before changing them. The 363 distinct inference requests and useful residual/type locators stay until another justified observation preserves their unique text. Do not restore M06 propagation, weaken retention, skip a field by flags, or reopen M33/ink calibration to save time.

The finite-y `blocks` bug is deliberately **unchanged geometry debt**: c8's accepted rule at y995–2740 becomes a full-height median-x cut through the y688–783 heading. Full region/rule/path/y/exclusion/mesh dependencies remain part of every reuse contract. This task does not certify the physical partition or fix it. G2 source limits, M55 centre-only assumptions, both DN floors, unmeasured body height, M35 population dependence and all seven bend authorities remain for owner review and the closing audit.

Recommend the computational candidate for independent checking; **5961754 remains the best independently checked head until that check**. R8-04-i1 is PARTIAL because the all-page target and clean-cohort qualification remain unmet. It is useful live speed work, not a profiling-only handoff, a physical gate pass or permission to self-launch. Actual duration, commit/fallback state and source identity are in `ITERATION_HANDOFF.json`.

## Commit state

Git staging failed while creating the worktree `index.lock`: **Operation not permitted**. No worker commit was made. The requested fallback is `.astra/commit-F8-R8-04-i1.sh`, with the exact 16-file patch, file/runtime hashes and isolated forward/reverse validation under `R8-04-i1/COMMIT_VALIDATION.json`. The script checks the branch, launch HEAD, clean index and candidate hashes, then stages only this iteration's files and uses the required trailers. It does not apply a rejected experiment or run a planner helper.

## Post-check addendum — 12 October 2026, R8-GEOM-02-i1

The coordinator applied **54cc8f9ead2809d3c7da11f5a8e9a87334d2df24** and selected it as the independently checked Python best head. The prior pending-review and worker staging-failure statements above are historical, not the current commit state. The coordinator reports its private check unchanged; this worker did not access those inputs or outputs. R8-GEOM-02-i1 started at docs-only merge 0164991 with matching runtime and restores that runtime after rejecting the finite-domain trial. `R8-GEOM-02-i1/POST_CHECK_STATUS.json` records this status without replacing old hashes or evidence.
