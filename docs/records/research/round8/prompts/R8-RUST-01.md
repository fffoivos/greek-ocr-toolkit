# R8-RUST-01 iteration 1: port the checked 54cc8f9 row stage and measure the gain

Fresh Rust worker, track `ff8-rust`.

Worktree: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust`

Branch: `astra/ff-rust`

Start `<HEAD>` = independently checked **54cc8f9ead2809d3c7da11f5a8e9a87334d2df24** plus this planner-docs merge. The coordinator creates the worktree. Verify that its runtime equals 54cc8f9 before editing; report any discrepancy instead of resetting uncommitted work. This is **iteration 1 of a binding maximum of 2** for R8-RUST-01 in this allocation. The planner writes iteration 2 only after your result and independent check. Completion or the second iteration closes the task; the coordinator then advances to geometry from the best checked head even if the pilot is partial. Meter limits take precedence.

**Benchmark target: this MacBook, under the established round-8 runner.** The coordinator explicitly confirms that the owner's MacBook rule permits these established development runs. Use the same MacBook for Python and release-built Rust, existing native images/model and the established thread settings (OpenCV reports 10; ONNX CPU sequential, intra/inter threads 1). Verify actual settings rather than merely setting an environment variable. Schedule compilation, OCR, comparisons and benchmarks sequentially; no competing worker benchmark or offline job during timed pairs. No remote machine, paid compute or provisioning is needed for this pilot. Read applicable AGENTS.md. No production `greekocr/` edits or use of the unrelated synthetic `linefactory` crate as if it implemented this stack.

Read RUST_COMPLETION_PLAN.md, PLAN's binding allocation, RUST_SPEED_ESTIMATE.json, the relevant two R7 reviews, and **the full `FL/review_r8/R8-04-i1_check.md`**, REPORT_R8-04-i1 and `.astra/fast_lines/out/round8/R8-04-i1/` (candidate/runtime source receipts, TIMING, OPERATION_DELTA_208, ITERATION_HANDOFF and current profiles). FL is `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines`. Read the R8-03-i2 check/handoff for preserved text and physical failures, and the ink/consolidation reuse contracts. Older 5961754 profiles are historical, not this pilot's Python reference.

**Latest accepted result.** 54cc8f9 keeps five exact live rewrites and deletes the old loops: partial distance selection and array ambiguity/grouping in M17, pair geometry passed once and sampled gap-cost construction, template energy once per refinement, per-component glyph tiles and an atlas once per ownership call. The 208 outputs, 15,093 items and non-clock evidence are identical; 278 tests pass with the same strict xfail. The coordinator reports private 44 identical. Field time improves 5.1%/5.6%, total corrections 3.3%/2.6% in paired orders; these percentages use the checker's 83-page cohort, with 0ce9 paired separately. The full 208 run still has 22 pages above one second and a roughly 2.008 s maximum. Counts of 19/20 above one second belong to paired subsets, not all 208. No physical definition or owner quality issue was resolved. Runtime is +40 lines for i1, -475 cumulatively from d5dc3e2. Do not claim these savings a second time as Rust gains.

The owner's objective remains:

> basically the same code with roughly the same behaviour but more architectonically sound and we would expect it to be actually faster because of the fewer duplicate processes

The owner's new direction is:

> I am planning to move this code to Rust to get a speedup.

> OK recreate your plan.
>
> Do you think it would help in practice if we started with the RUST port so we could have a better sense of what we were dealing with?
>
> what speed up would you estiamte we would get

Answer the performance question with a representative implemented port and checked timing. This prompt scopes the first experiment; it does not request the entire pipeline translated at once. A correct negative performance result is useful. Do not spend the iteration producing only another inventory or a benchmark of a trivial loop.

## 1. Builds on existing code

Port the **54cc8f9** `shared/geometry_field_detector.native_bands` and its `separate_bands` computation, called by `geometry_field_detector.run` after `unbend`, `Detector.infer` and `postprocess`. Reuse the current `geometry_rows.valley_grid/valley_path` contract, including its sampled-cost mode. Do not resurrect the full distance sort, per-row owner scans, repeated pair computation or discarded full-plane M17 gap cost. Keep field construction, model inference, row nomination and downstream `geometry_field_selection.apply`, M20 retention, M33 envelopes, M35 and reconciliation unchanged for this comparison.

This target combines native preparation, component grouping, ownership calculations, pairwise separation and many small array/object operations. Read the complete functions and callees before fixing the interface. The current profiles include native-band costs of about 321 ms on 4959 p1 (including 205 ms separation), 194 ms on 4959 p5 and 111 ms on 8686 p5. These are instrumented costs, not expected Rust savings. 0ce9 has no M17 native-band call in this profile; keep it as a no-benefit/regression control rather than treating it as a port beneficiary. Regional inference remains outside the port and remains timed in the integrated route.

Use an isolated crate under the prototype and one coarse integration call. Prefer a minimal Python/Rust bridge with contiguous typed buffers to preserve the current harness; report all conversion/copy work. Inspect available supported bindings/toolchain on the assigned machine before choosing dependencies, pin the actual versions and lockfile, and record build settings. Keep existing native backends where feasible. If a dependency requires a replacement implementation, isolate and verify its semantics; do not silently replace interpolation, geometry or filtering during a claimed faithful port.

Choose a coherent implementation boundary rather than repeated per-component FFI calls. If the complete target cannot be integrated, deliver the working bounded portion with an explicit unported remainder, and give no full-stage or pipeline speed claim based on that portion alone. A different target requires a concrete measured dependency/cost reason and a similarly representative integration boundary.

## 2. Inputs match the code's contract

`native_bands` receives the exact rectified gray crop, row polygons in that crop's coordinates and engineering height. It does not receive original-page polygons or slow-reference row IDs. `separate_bands` must use the ink/stats/labels/owner derived from that same crop. Preserve dimensions, axes, offsets, dtypes, rounding, thresholds, borders, connectivity, NaN/empty behaviour, ties, ambiguity and downstream metadata. Rust integer casts must not replace Python/NumPy rounding accidentally.

Return the actual polygons and audit/ownership records consumed by `run`; do not omit foreign-component flags to gain apparent agreement. Distinguish categorical component labels from continuous rasters. Compare labels modulo documented equivalent labelling only when membership and every downstream decision agree; preserve source lineage independently of numbering.

Existing reusable preparation requires identical image/ROI/scale/threshold/window and immutable buffers. Changed rows still require fresh selection, ownership and calibration. Preserve the finite-inverse NaN fix and its `certify` regression tests. Do not feed Paddle polygons to `PixelPage.boxes`; this experiment does not need the slow detector in runtime.

## 3. Removal and verification scope

First establish a faithful Rust computation with normal typed loops and buffers. Simple removal of temporary representations is part of an idiomatic port; document it. Keep later algorithmic elimination or physical repairs in separate commits and comparisons. Do not add a cache beside the original computation, alter the model/resolution, skip hard inputs, suppress uncertainty or weaken retention.

Keep Python as an offline/replay reference and explicit experimental backend switch during qualification. Report how many real calls go through Rust and which fall back. A Python fallback is not a Rust speed gain. An accepted Rust route replaces the live computation within its declared complete scope; it does not append a second calculation on every page.

Pin fixtures on the four profiled pages (4959 p1/p5, 0ce9 p1, 8686 p5), clean/quiet controls and the six geometry rejection controls (466, 7792, c8, 9ea, dbd, d323). Include empty/no-field and multirow/ambiguous component cases. Build meaningful differential tests at the port boundary; trace any difference to the first operation rather than hiding it behind a broad tolerance. Numerical differences may be acceptable only with stated units/error bounds and unchanged physical decisions; inspect every changed crop. Exact parity proves translation fidelity, not correctness of inherited page policies.

Preserve accepted endings, punctuation, isolated marks and neighbour exclusions; p5 rows 40/41 and “ἀποξήρανσίν”, p7 recoveries, Ψ/E, weak τῆς, pale 1be6 and 0ce9 #34/#36. Keep the strict faint-front xfail explicit. M06 stays deleted; M55, both DN floors, M35 population dependence and unresolved source tails are inherited debt. The finite-y `blocks` bug, missing p5 row 5, missing fields and clipped endings are not fixed by parity and stay in the ledger.

### Close the test weaknesses that concern this port

The independent check found three weaknesses in `shared/test_speed_observations.py`. Give each an explicit disposition; do not describe the existing tests as covering these gaps.

1. **Exercise the real gap caller.** Add a test that calls `geometry_field_detector.separate_bands` on slanted/overlapping bands at multiple engineering heights, with border ink and nonzero crop offsets. Capture or otherwise verify the actual ROI/grid/cost supplied to `valley_path` against an independent full-plane reference. Check resulting paths, accepted/rejected crossings and output polygons. A second handwritten sampled-cost formula alone does not test the caller. Include a small in-memory mutation or equivalent negative check showing the test catches an incorrect sampling offset or dilating the sampled raster instead of the full exact ROI.
2. **Exercise M17 ownership.** Add direct tests of the real `native_bands` for single/multiple/empty rows, equal-distance ties, tall cross-row components, detached marks and final grouping after mark attachment. Pin some independently expected owner/ambiguous dispositions, then compare the same fixtures with the Rust implementation. Recreate the checker's useful coverage of varied slanted crops with non-empty ambiguity and gap/crossing audits; its 40-case scratch comparison is evidence, not a checked-in test. Target the partition, vectorised ambiguity test and final grouping. Keep the NaN `certify` consumer tests.
3. **Atlas membership is outside this port.** `glyph_atlas`/`match_glyphs(prepared=)` remain Python and unchanged here. Trace and record the current build-after-selection, immutable-membership-through-use caller; do not claim the circular test validates rejection of stale preparation. Assign the enforceable contract and actual stale-preparation test to R8-INK-02, before its first changed atlas consumer. The test must pass an old preparation with changed membership, including same-length replacement/reordering; a length-only check is insufficient. If this pilot unexpectedly touches that producer/consumer boundary, close this contract and test now in a separately identified change and benchmark against a Python baseline containing the same contract repair. Do not broaden the Rust port to ink solely to hide this debt.

The other full-plane cost caller, `geometry_rows.native` around lines 177–181, remains Python. Keep both `valley_path` input modes valid; its eventual migration and deletion of the unused full-plane work belong to R8-RUST-02. If the port needs an adapter for the shared solver, test both modes against 54cc8f9 without changing M37's caller algorithm in this comparison.

## 4. No new pipeline or physical page model

Translate the existing computation within the current stack. No universal page context, new row peak finder, new gutter model, noise estimator, Rust rewrite of the model, production deployment or synthetic-factory refactor. Language choice is independent of physical validity. Do not import the failed 880aee0/1eae16f models or offline rejected frame providers.

## Benchmark and deliverables

Use the established MacBook runner for both baseline and candidate as specified above. The coordinator supplies the current meter before launch (about 82% at planning; refresh it). The runner refuses launches at 97%; PLAN reserves closing headroom. Runs must finish in the worker turn. No held-out access, PDF text, orientation work, extra agents or background jobs.

1. Implement the pilot with release/optimised settings, meaningful tests, exact source/build/input identities and replay commands. Cold import/compilation/setup is reported separately from warmed page processing, not silently discarded. Preserve required thread budgets; first compare equal resources, and report extra parallelism separately.
2. Measure paired uninstrumented baseline/candidate runs in both orders over the representative controls, using enough repeats to distinguish noise. Time boundary conversions, the complete replaced stage, corrections and file-to-final. The in-memory replay excludes inference for diagnosis only; the integrated comparison includes all inference. Profile clocks are not benchmark clocks.
3. Once coherent, run the integrated candidate over the 208 development pages on the authorised target. Report all exports/exclusions/changed owner crops, per-page latency distributions, the slow tail, memory/copy cost and the number of actual Rust calls. The coordinator privately runs its 44 on a proposed accepted runtime. Do not access their data or outputs.
4. Write `docs/records/research/round8/REPORT_R8-RUST-01-i1.md` and `.astra/fast_lines/out/round8/R8-RUST-01-i1/` with commands, fixtures, parity/quality results, paired raw timing and a handoff. Report separately: port correctness, physical quality (inherited or changed), component gain, correction gain, total gain, remaining native/inference cost and unported work. Replace the planner's estimates with measured scope-specific results. Do not extrapolate one slow page to all pages.
5. Recommend the next component or the algorithmic work that matters more. If the explicit slow detector could plausibly become affordable, identify a measured follow-up comparison with its own correct inputs; do not claim it became fast because a different component did. Preserve all old partial gates.

Completion of this pilot means an implemented and independently checkable answer about speed and compatibility, including a negative answer. It does not require the full Rust port or final subsecond gate. A regression blocks promotion, not reporting; fix its actual cause or retain the best checked head. No arbitrary clock cap or invented speed threshold. The coordinator checks the result and returns it to the Astra planner. The planner writes the next iteration prompt, or geometry iteration 1 if this task closes; the coordinator checks all four launch sections and sends that prompt unchanged except its header and declared placeholders. Do not self-launch. Unused iterations do not transfer between tasks.

Commit scoped prototype/evidence documentation on the assigned branch, with the INFRA trailers. If Git is blocked, leave a source-bound `.astra/commit-F8-R8-RUST-01-i1.sh` fallback. Do not push or deploy. Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` with R8-RUST-01-i1, implemented scope, commit/fallback and measured speed at each timing boundary. Record launch/end meter if available, actual elapsed time, the three test dispositions, exact Python/Rust source and build identities, and candidate versus coordinator-accepted status in ITERATION_HANDOFF JSON/Markdown. Add a dated status note that 54cc8f9 was runner-committed and independently accepted; do not rewrite its original staging receipt.
