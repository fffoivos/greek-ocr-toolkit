# R8-GEOM-03 iteration 1 — land the verified separator and complete-row consumer

You are the implementation worker, **fresh thread**, model **`gpt-6.1-sol`**, effort **`high`**, track `ff8-stack`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start at **`<HEAD>`**, expected `db899f13bfcc03fa3feac82323c1d6b99fbc7efd` plus this planning-docs merge. db899f1 = checked 9367bd4 + FP8u docs; runtime equals 0474bf8. Verify that source identity before editing. The coordinator sets `MODEL=gpt-6.1-sol EFFORT=high` and records your new thread ID. Resume that thread for subsequent iterations; do not launch another worker yourself.

Owner instructions, verbatim, in order:

> ok I think we should keep going but try to use sol 6.1 as execution and astra as planner

> ok I want us to close the geometry aspect first before we continue so lets say we get +3 iterations

GEOM-03 moves first and has **three iterations total**, consuming the previously reserved GEOM-03 allowance. No GEOM-02 i6–i8 and no second GEOM-03 after font/curl. This first iteration targets one useful retained result, not every closure target at once. Read `docs/records/research/round8/SOL_WORKER_HANDOFF.md`, this prompt, and `GEOM03_GATE.md`/`GEOM03_COHORT.json`; use deeper historical documents only for a specific contract or contradiction.

Read the full independent check:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i5_check.md`.
Also read your worktree's `docs/records/research/round8/REPORT_R8-GEOM-02-i5.md` and `.astra/fast_lines/out/round8/R8-GEOM-02-i5/` (`endpoint-attempt/`, `experimental-source/`, `WITNESSES.json`, `CONFIRMED_HULLS.json`, replay/timing receipts and `FINAL_COUNTEREXAMPLE.json`). The check supersedes the report's last-cause and best-head claims. Its scratch `halfpixel.diff` may be unavailable in this checkout: the full check specifies the two-condition change and its limits. Reconstruct it against the named archived source, verify it with the native fixture, and record the diff; do not invent a successful replay or wait for a missing scratch directory.

Architecture objective, verbatim:

> basically the same code with roughly the same behaviour but more architectonically sound and we would expect it to be actually faster because of the fewer duplicate processes

The owner's scope also remains, verbatim:

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

> (a) making sure we have one line per segment
>
> (b) columns

## 1. Builds on the existing code

Use the real chain `stack.pipeline.compose` → `type_extended.recover` → `type_residual_recovery.recover(version=11)`. The accepted runtime does **not** contain the completed i5 mode. Reintroduce only the reviewed pieces from `endpoint-attempt/prototypes/fast_lines/shared/`, by a scoped diff against current source, never by replacing the current tree wholesale:

- `type_completion.request_neighbours`, `complete_request`, `raster_envelope`, `corridor_hulls`: fixed request census, same-line finite neighbours, whole-component membership, tight final hull;
- `geometry_field_detector.native_bands/separate_bands` request mode, `rule_edges`, `body_supports`, `refine_corridor`, using existing `geometry_rows.valley_grid/valley_path` as the coarse proposal;
- the real `recover` completion caller and its source/exclusion checks.

I5 already completed four right rows with exactly equal hulls and membership in both genuine windows. Keep its rule-ink edge, observed spans union whole bodies and admitted whole-component hull. Do not restart with owned-only selection, a wide smooth strip, a new row finder, or a from-scratch font/bend model. Whole native components are not automatically characters or measured font lines.

**Repair the remaining raster contract.** The issue is not a steep join: a path passing0.46 or 0.15 px below a pixel centre can still include that pixel in both filled polygons. In the checker's endpoint source, treat the path as crossing when `delta.min()<.5 and delta.max()>-.5`, sending that case to the existing native refinement. Preserve endpoint widening, needed at origins 7/8. This is a testable candidate fix, not a universal raster theorem: certify on the actual exported `rint` plus inclusive `fillPoly` raster. Require all 13 x-origins in both windows, zero duplicated/clipped φ/β ink, and the restored coarse/tolerance mutations to fail. No tolerance, ignored pixel or phase-specific runtime offset.

**Remove avoidable repeated decisions.** Profile the restored real caller before altering its order. The checker measured ≈55 ms refreshing decisions, ≈66 ms in `native_bands` inside ≈80 ms completion; four hulls have 991–1089 vertices. In `type_residual_recovery.competing_axis`, hoist the identical float32 polygon conversion outside the neighbour loop. Inspect `candidate_motif`, `geometry_joinbarriers.inspect` imported as `rule_contacts`, `ink_ownership.analyze`, `axis_context`, and the pre-/post-completion checks in `recover`. Delete exact repeated array work and redundant decision evaluations while preserving the semantics of final geometry and the fixed neighbour census. If an earlier check is genuinely needed to select candidates, keep it and explain the dependency; do not blindly delete a source or exclusion test to reach one pass. A compact decision polygon is allowed only if actual affected decisions and native partitions are proven equivalent; simply simplifying the output hull or comparing areas is insufficient. Prefer exact hoisting/passing first. No new global cache.

For broader targets, locate existing consumers before proposing changes: `geometry_rows.native/confirmed_partition` and current callers for original multirow crops; `type_residual.render`/M17/M18 for residual row hypotheses and adoption; `geometry_page_field.blocks/render/certify` with finite column evidence for domain errors. The current request completion alone cannot fix every original Paddle box. This iteration records the first failing consumer for those cases and tries the same sound mechanism where compatible; it does not launch all upstream repairs in parallel. `greekocr/pages/lines.py:_discover/_pool_geometry/_assign/_make_lines` and `font.py:evidence/fit_guides` remain the pixel-seeded offline reference with known errors, not runtime replacements.

## 2. Inputs match what the code expects

- Keep native image identity, ROI origin, scale, existing M17 threshold/mean mask and CC8 provenance explicit. “Undilated” means before the extra separator dilation, not a new calibrated mask. Residual-closing body indices, M17 labels and component IDs in different windows are distinct; map by native support.
- `data['rows']` are finite lower-contact chains, not guaranteed full text rows or font baselines. The observed spans plus whole-body support and accepted column-rule side determine valid neighbour support. Unsupported gaps must not become full-width extrapolated axes. Include bodies 622/707 and “το”; preserve the i5 grouping/order invariance. Do not fix the left axes this iteration by changing height or widening acceptance.
- Existing accepted column evidence provides finite path/y range; its physical ink edge is the barrier, not a full-height median-x cut or a survey crossing count. Do not feed short supports into a wide-box-only clipping caller without the compatible existing primitive. A touching glyph/rule ambiguity remains explicit.
- Preserve both genuine requests y2576–3080 and y2583–3079 and their saved inference maps. No frozen favourable crop window. Complete all admitted components including apostrophe 757 and weak marks; inspect grayscale as well as masks. Tight hull construction must preserve membership after export/rasterisation.
- One `native_bands` batch per fixed request, independent of piece/neighbour order. Preserve all seven baseline rows; unknown completion keeps its existing row instead of dropping it. Residual/no-seed rows continue through existing scout and localisation. **No Paddle polygons in `PixelPage.boxes`**; the slow reference expects rough pixel-seeded regions.
- New polygons require new geometry-dependent B5 anchors/votes, M35 pool/source evidence, motif, ownership, rule/exclusion, duplicate and footprint decisions. Reuse only exact unchanged observations; never carry old decisions across changed geometry. Invalidation and candidate census are part of the speed test.

## 3. Removal and verification scope

**First freeze the cohort without tuning on validation.** Read the coordinator's `cases/README.md`, `cases.json`, `survey.py`, `survey.json` under `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/`. Verify hashes against `GEOM03_COHORT.json`. Do not rerun the survey or OCR just to rebuild its lists. The planner selected25 marked groups on eight books/pages, plus the seven-row4959 witness, missing 8686 row 5, c8 finite-rule and e259 leaf targets, and seven negative pages. All exact IDs/marks and split rules are fixed in the JSON/gate. Freeze working native coordinates, baseline ancestry/output mapping, expected row count and physical success criteria before editing. Retain the three validation pages for candidate-frozen evaluation; do not inspect failures and then describe the next adjusted candidate as untouched validation. No cherry-picking/replacing hard cases; false survey positives need explicit coordinator adjudication.

Within the qualified request population, the component hull replaces crop-window-sensitive raw residual extent. It must reach the default `recover` consumer after qualification, with the displaced trial/owned-only construction deleted in that scope. Keep the legacy route only for genuinely unsupported cases and the off-switch for differential verification. A dormant new mode is not a retained crop improvement. The page-field M17 contract remains unchanged outside the explicit request mode; do not repeat i4's shared default change which regressed4959 p4/p5.

**Iteration-1 target:** retain the corrected mode through the real default recover call, complete #109, “καὶ τακτοποιήση”, “πάτε” and “τος,” identically in both windows, pass 26/26 exported-raster cases, preserve the three left rows unchanged/unknown, and meet the ≤100 ms added-request cost. Then exercise the same consumer on the frozen working pages: seek at least one independently verified additional-page gain, and record all unsupported/failing paths. One-page success is a useful retained milestone, **not task closure**. Do not hold back an independently sound narrow improvement merely because all 25 marked groups or the left axes remain unresolved.

Use the actual `separate_bands`, `complete_request` and `recover(version=11)` calls with non-empty inputs. Test whole φ 754, excluded β/λ, preceding 588, apostrophe 757, body-support gap 622/707, rule 51/52 and “το” 1433/1466/1420 by native ink mapping. Keep the owner-preferred tight shape. Native phase, old coarse-path, old tolerance, rule-centre, missing body-span and owned-only-membership mutations must discriminate against the passing candidate. Remove strict xfail only for the corrected contract; a request-only fix must not erase a still-failing default-mode test. No reimplemented-formula or zero-proposal tests.

At candidate freeze, score every reserved validation target with the fixed configuration. A safe unknown counts as a failure to solve that target, not a text regression. Report working gains, validation gains, unchanged controls and unknowns separately. Earlier pages/windows are regression witnesses, not additional independent positive books.

Run the established208 development comparison after local correctness: disabled completion equals db899f1 in exports/non-clock evidence; page-field M17 is identical at identical inputs; enabled default shows intended final changes, all of which receive native crop/exclusion review. Preserve the named controls in `GEOM03_GATE.md`, including M33 endings/narrowings, “ἀποξήρανσίν”, pale/weak ink and 0ce9 #34/#36. Update the 133-mark and nine missing-page ledger without declaring unchanged cases fixed. The coordinator alone runs private 44.

Measure real full requests, including refreshed downstream decisions, against db899f1 in at least five warm pairs in both orders. The median paired increase for **each affected request** must be ≤100 ms; show each window/request and worst result. For any non-request geometry change use its affected page with the same 100 ms ceiling. Report unchanged-stage/detector controls and all samples; no favourable-order or pooled-median claim. Clean pages get no new processing pass or repeatable cost beyond control noise. Full208 clocks and slow-page counts remain required; this scoped bound does not claim the charter's global <1 s gate.

## 4. No new pipeline or page model

Adopt the bounded i5 construction in the existing stack. No Rust port, universal body/ink estimator, global curvature/gutter model, new row detector, per-page rules, default whole-slow-pipeline call, extra guard chain or mass module relocation. Do not restore M06 propagation or import the rejected M55 providers. No full-plane per-pixel Shapely test to certify a domain; use the already evidenced raster convention. The slow model can explain a first divergence without becoming truth or a second live pipeline. If this iteration exposes an upstream row-axis or column-domain defect, retain a native witness and compatible caller plan for the next planner-written prompt rather than broadening this iteration into an unbounded rewrite.

## What counts as progress

Report **completion, retained physical gain, retained mechanism/deletion, and experimental progress** separately. The i5 experiment is substantial evidence already; replaying its four good crops alone is not a new gain. New progress is the 26-case defect eliminated through the real consumer, necessary downstream cost removed and a qualified default repair retained. Additional-page success provides stronger generalization evidence. A precise upstream witness can narrow the next step but is not a physical correction.

If only a non-empty smaller population meets native and cost checks, keep that independently qualified result as PARTIAL; do not make all broad targets an all-or-nothing retention gate. If none qualifies, keep db899f1 runtime, preserve exact code/evidence and name the first remaining assumption. Do not relax the raster/cost gate or ship dormant unqualified code. This is iteration 1 of 3; the planner decides iteration 2 from your result and the independent check. Do not pre-write or launch it.

Full task closure is exactly `GEOM03_GATE.md`: all 25 marked groups, all seven witness rows (including left), missing row 5, finite/leaf boundaries, controls, deletion and cost. This iteration is **not expected to repair them all**. Wider a–d geometry, font measurement and shared edge-curl detection remain separate recorded work.

Ask the reviewer which earlier witness now passes and why, which gain is retained/default, whether a new book/layout passes, which exact caller is first wrong in the remaining cohort, whether the next iteration can reuse the solved dependency, and whether quality/cost/deletion claims hold. Avoid a single undifferentiated “failed” verdict.

## Deliverables and handoff

Write `docs/records/research/round8/REPORT_R8-GEOM-03-i1.md` and `.astra/fast_lines/out/round8/R8-GEOM-03-i1/`: `COHORT_FROZEN.json`, native row/column/phase and final crop evidence, actual-consumer/mutation receipts, phase 26 results, all working/validation outcomes, changed 208/exclusion review, ledger deltas, paired request/full-page timing, runtime/deleted-policy receipt and `ITERATION_HANDOFF.md`. Bind source/input hashes and archived-source provenance. Report per-request vertex/decision-pass costs, not only total latency. Fix the i5 report/handoff with a dated9367bd4 addendum and the correct origins 1/2 raster explanation; preserve historical evidence rather than silently rewrite it.

The handoff names accepted versus experimental APIs, best source head, retained four-row versus wider closure progress, remaining left axes/finite domains/missing rows, first failing broad-cohort callers, validation exposure, source/ink invalidation and exact deletion/cost. Hand the next prompt back to the Astra planner after independent review.

Use the established authorised MacBook runner only, no concurrent benchmarks, no held-out access, PDF-text truth, background jobs, extra agents, production edits or push. `greekocr/` and other worktrees are read-only. Commit scoped work on `astra/ff-r8-stack`; if blocked, leave `.astra/commit-F8-R8-GEOM-03-i1.sh`. Preserve repository-required trailers from the existing history. End in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` with iteration ID, commit/fallback, retained gains and recommended head. Task COMPLETE and iteration DONE are different.
