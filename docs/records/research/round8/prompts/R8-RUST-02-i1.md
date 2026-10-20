# R8-RUST-02 i1 — land the small extent correction, then port a substantial numerical boundary

Fresh worker, **gpt-6.1-sol**, effort **high**, track `ff8-stack`. Runner thread argument `-`; coordinator records the returned ID and resumes it within this task. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start `<HEAD>` = independently checked `5faa178ebd18c593f9f1c47af64bcbc5dc7ea100` plus FP8aj documentation. Verify it; do not reset the branch. **Iteration 1 of at most 3**. No arbitrary wall-clock cap, extra task or later prompt authored by you.

Read `SOL_WORKER_HANDOFF.md`, PLAN's current FP8aj section, current notes in `RUST_COMPLETION_PLAN.md`, and these two **full independent checks** under `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/`:

- `R8-CURL-03-i3_check.md`, plus the stack's `REPORT_R8-CURL-03-i3.md` and source-bound handoff.
- `R8-RUST-01-i1_check.md`, plus the parked pilot's report/handoff in `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust` at 953fc4a. Read `RUST_SPEED_ESTIMATE.json` as historical measurement, not a current forecast.

Use generation/method/test documentation as focused references; do not consume the entire historical conversation before acting. Benchmark target is **this MacBook under the established authorised round-8 runner**, also for sequential release builds. No remote provisioning, production deployment or background jobs.

Owner's objective, verbatim:

> basically the same code with roughly the same behaviour but more architectonically sound and we would expect it to be actually faster because of the fewer duplicate processes
>
> I am planning to move this code to Rust to get a speedup.
>
> But the whole point of this generation of our model was so that we odnt have to have duplicate checks
>
> ok lets just normally continue with the rest of the tasks in the plan

CURL is CLOSED PARTIAL. The checked runtime is fea451c: A adds one witnessed body on 8686 p5 and another on a private page (coordinator only). No complete curved ending was retained. I3 is tests/evidence only, with 208 identical; worktree 368 passed / 17 strict xfails, bare 367 / one older skip / 17. Preserve A, the four R rows, the B row, exclusions and `final_export=False`, `bend=False`. General geometry and FONT are not reopened.

## 1. Builds on the existing code

### First checkpoint: support-bound hardening, before any port

Land the existing `prototypes/fast_lines/evidence/curl03_i3_support_bounds_unqualified.patch` after reading it. Its SHA256 is `26e513e0820b7aaadb600159c339678ac8d16c2c40ebd368038ba16bd4b88cb5`. It changes only A's newly retained unknown-side piece in `shared/type_barriers.protect`: reuse `type_residual_recovery.supported_extent` when supplied bounds are valid, then recheck `piece_support`. The actual route is compose → type_extended/recovery → recover → protect. No new bounds formula or ordinary-proposal clipping policy. Keep verified-rule, absent/invalid-bound and witness-free caller behaviour.

This correction belongs at entry to this task, in its existing first slot; it is not a fourth CURL iteration. Preserve an independently reviewable source checkpoint before changing numerical code. Remove only the two repaired hardening xfail markers in `features_geometry/test_curl_consumer.py`; retain the src37 end xfail and all unrelated physical failures. The fixture enters real recovery unclipped, but its added overhang is synthetic blank paper with zero ink and no natural occurrence on 208. Describe it accurately as a geometric contract repair, not new text recovery.

The planner replaces the invalid whole-page clock requirement **for this small correction only**. Time baseline and hardened `protect` in process on captured real branch inputs: 8686 p5 accepted side, 93f8 p1 abstention, and a non-branch control. Use fresh equivalent inputs, a fixed warmup and fixed alternating batches with enough calls to rise above timer overhead; report batching, distributions and per-call deltas. Keep measurement outside production behaviour. Preset added-cost budget: median ≤1 ms per affected call, and ≤5 ms per affected page using actual call counts. A clear excess requires investigation; timer noise is not evidence of regression. Do not force a detector-drift criterion onto a few polygon operations.

Reuse the exact-source existing hardening 208 identity receipt if patch/runtime/input hashes match, and rerun the native tests plus the four checker pages (8686 p5, 3229 p5, 9ea1 p202, 466c p323). If any binding differs, regenerate the comparison. Coordinator independently checks private44 equality and times `protect` on its affected private page. Keep the checked A if the correction causes a real regression. Do not let an unrelated theoretical repair block safe stable numerical work, and do not erase its remaining status.

### Main implementation: the current M15 numerical field calculation

Use the current profile to select a substantial boundary in `shared/geometry_page_field.render`, beginning with **profile interpolation, lag correlation and mesh refinement**. Actual functions are nested `demean`, `shifts_many`, `shifts`, sequential outward propagation from the anchor, and the two joint-template refinement iterations. `render` is called by `geometry_field_detector.run` from `stack/pipeline.compose`'s `field_proposals`; its result also reaches field selection, `certify`, `invert_points`, `unbend/displacement` and `geometry_envelopes.correct` (`smooth_envelopes`). Read the real callers before fixing the interface.

First measure the current call tree without double-counting nested timers: `render/prepare`, numeric mesh work, `certify/invert_points`, M17 unbend/regional inference/native_bands, field selection, type/residual, ownership and final refresh. Instrumentation explains attribution; uninstrumented clocks establish speed. Historical field-proposal time includes model inference and M17, so it cannot all be claimed as Rust-addressable work. Implement the port after this short boundary check; another inventory alone does not meet i1's implementation target.

Prefer **one coarse typed-array call per field** that computes the current mesh/support from already measured profiles, coordinates, windows, valid lengths, lag grid and anchor. Keep pixel preparation, seed/scale decisions, body selection and physical certification in their existing callers. If the full block cannot be completed, a measured `shifts_many` batch is a bounded partial result, with the remaining Python loop/callback cost explicitly reported. Do not make a Rust call per pixel/label/lag or wrap a Python numerical callback and call it a port. A different substantial numerical boundary needs a concrete profile/contract reason recorded before implementing it; no scope change into physical field fitting.

The pilot ported historical M17 and delivered 1.621× at that boundary, 2.8–4.0% corrections, 2.2–3.0% file-to-final. About 75% of its Rust stage remained callbacks; M17 was about 7.7% of correction time, with a free-M17 ceiling around 1.083×. Its old Python/bridge/native bodies predate current R/B/request completion. **Do not merge that runtime or re-port M17 first merely because a crate exists.** Use its locked build pattern and lessons; keep its unrelated logic parked. If current profiling supports expanding to M17 later, that requires a subsequent planner prompt.

Use a prototype crate with explicit current integration, not production `greekocr/` or unrelated `linefactory`. A single native implementation and a readable Python oracle suffice. An accepted boundary must replace its old live work; do not execute both except in an explicit test/replay comparison, and do not copy Python decisions into another `bridge.py`.

## 2. Inputs match what that code expects

The M15 numerical kernel consumes the profiles and finite numerical arrays of **this call**, not native-page polygons, slow-reference row IDs or a re-detected image. Preserve units, array shapes/order, valid-padding masks, float dtypes, interpolation endpoints/borders, first-maximum ties, lag spacing, score floor, weights, Gaussian filtering, iteration counts and sequential dependencies. The outward sweep cannot be parallelised across dependent columns. Keep the existing immutable template energy shared once per refinement. Invalid/outside inverse domains remain NaN, and certification must skip them.

Freeze the Python boundary before translation. Write down the actual input/output schema and mutability/lifetime assumptions. Use current code as the oracle, including supported empty/short/constant and near-tie cases. Numerical comparisons must locate the first differing operation. Do not introduce a broad tolerance that hides a changed argmax, seed, certificate, row identity or final pixel. Require exact discrete decisions, source/exclusion identities and final native crop masks; prefer bit-exact polygon coordinates too. Any unavoidable coordinate roundoff needs an a-priori bound justified by the numerical operations, unchanged native masks and separate reporting in pixel units; do not fit a tolerance to the observed failures. If a platform-specific reduction/FMA/interpolation detail prevents those contracts, keep the native route experimental and report the counterexample. Do not change physical semantics to make the port agree.

Share preparation only under identical image, ROI, scale, threshold, label and exclusion state. Do not cache changed-row B5 selection/votes, M35's pool or ownership. Initial Paddle maps and items are immutable paired inputs. `PixelPage.boxes` never receives Paddle line polygons; the pixel-seeded slow detector is an offline reference only and is not needed in this numerical runtime.

The field view exposes existing semantic defects, which **parity must preserve and the backlog must retain**: false bending on flat pages, binding-side detection misses, current `blocks` finite-rule issues, and incomplete outside-box crop support. You are not certifying the physical field by translating it faithfully. Do not change no-curl gates, knot spacing, `.035/.05` occupancy criteria, DN floors, row selection, source votes, per-component ownership or final export while measuring a language speedup.

### Build and backend contract

Fix the pilot's applicable deployment mistakes before introducing native code into this worktree:

- Commit the needed platform link configuration and lockfile. Interpreter/vendor locations must be configurable, not another worktree's absolute path or an ignored cargo-home prerequisite. Prefer already available pinned dependencies; record compiler, target, build flags and dependency identities. Report platform qualification honestly.
- A clean checkout without an extension still collects and runs Python tests. Gate only native comparisons; explicit native selection without a usable build fails clearly. Never silently fall back. In native qualification, missing native tests are failures, not skips.
- Keep one explicit backend selector at this boundary, read predictably before work. Count **actual entries** into Rust, Python and any documented fallback; do not derive counters from the number of regions. In i1 the normal default remains hardened Python; the native route is explicit while awaiting independent adoption. A later checked promotion must remove the displaced live route/adapter duplication, keeping an offline oracle.
- No copying historical `native_bands` over request_mode/axes/supports/domain/retain_support changes. Do not port `support_accounting` diagnostics. If any shared pilot component is imported, bring its real gap/dilation mutation, mutation-target assertions and current M17 caller parity with it; otherwise record them as still parked, not “fixed”. The atlas membership defect stays INK's; do not silently touch that interface.

## 3. Removal and verification scope

I1 must deliver the hardening checkpoint and an implemented, measurable numerical port or a concrete boundary counterexample. Keep physical repair and port comparisons separate: S = checked 5faa178, H = narrow hardening, R = native port of H. Compare S↔H for the correction and H↔R for translation/speed. If hardening cannot be retained, use S explicitly as the numerical baseline and keep the bounds defect open. Do not count A's existing gain, earlier Python sharing, or changed algorithms as Rust savings.

Commit small real numerical fixtures captured from actual `render` calls, plus independent constant/straight/known-shift cases. Include several books, both outward directions, flat/skew/curled, finite column domains, short windows and near-tie cases. Exercise the true Python→native wrapper→render→certify consumer, not only a second handwritten formula. Mutation controls must catch an interpolation endpoint change, changed lag/tie choice and dropped valid-window mask at their actual consumers. Preserve the existing NaN-certify, R/B final raster and source tests. Distinguish committed reproducible tests from ignored replay evidence. No new skip-if-capture-missing tests.

Use the frozen 41-page CURL cohort (same SHA256 `377df97a07b0428b8591783f2dd093d11e0c78fb56ea4c7511aa4a7ed998a766`) within the full 208. Keep all pages in the denominator, including no-field/no-Rust pages. The named controls include 8686 p5/p7, 4959 p1/p4/p5, 3229 p2/p4/p5/p6, c8 p36, 9ea1 p202, both 8314 tables, 74cd p2, 93f8 p1, 0ce9, pale 1be6, weak 31f40, and 466/7792/dbd/d323 endings or neighbour exclusions. Preserve A, R, B, `ἀποξήρανσίν` and current source exclusions. Exact exports do not close inherited physical failures.

### Add the owner books as a separate development appendix

Coordinator fieldview base:
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/fieldview/`.
Read **only** `build.py`, `dev/fields.json`, `owner_out/fields.json` and `owner/owner-*.png`. Do not recurse through `heldout/`, the mixed `files.json` or the all-page site: private44 remains inaccessible to you.

Freeze all 22 PNGs as a separately hashed appendix before changes: seven `owner-1868-d8dfd7-p*.png`, fifteen `owner-1876-292f4a-p*.png`, preserving `_REPL` suffixes. These are internal Anemi development scans; do not publish or upload them. Originals are in the owner's glossapi-ocr-local `harvest_big/round1_look/accepted` book folders supplied by the coordinator. If the temporary copies disappear, obtain their exact source mapping from the coordinator; do not substitute scans silently.

Owner-confirmed 1868 p0023 has left/binding curl. Other pages contain a mixture; do not label all positive. Keep the established 208 and 41 intact and report appendix parity separately. The fieldview script draws arbitrary constant-phase curves but can force `render(..., route='slow')` when the runtime gate is silent. On p0023 it did that and still under-bent; only two owner pages triggered runtime. If the port boundary is not called by the live route on a page, report zero native calls. A separate forced-field replay can test numerical parity there, but is not a production speedup or a fixed curl detector.

Run H/R on the 208 and this 22-page appendix using matched initial detections, then actual integrated file-to-final comparisons. Review any changed actual crop/mask: a faithful numerical port must change no native mask or discrete decision; any bounded coordinate roundoff remains explicitly reported. Report intermediate field, certificate and final identity differences even if final crops happen to remain equal. Save whole-page and strip/coverage evidence locally; the coordinator owns private evaluation and publication restrictions.

### Performance measurement

Profile nested costs, then benchmark release-built code without profiling. Report buffer conversion/copies/allocations, the whole replaced boundary, the enclosing field-proposal stage, corrections and file-to-final. Include Python/native callbacks rather than subtracting them from “Rust” time. Freeze actual thread requests and observed backend settings for both arms; the pilot's request-of-2/receipt-of-10 mismatch must not recur. No extra worker parallelism to claim page latency improvement. Report compilation/import/cold setup separately from warmed service cost.

Use the established sequential MacBook runner and a quiet coordinator window. Pair both orders on the affected population and unchanged/no-call controls, with fixed repetitions and drift controls declared before measuring; retain invalid samples. Full 208 census includes median, p95, maximum, per-page changes and counts over one second; appendix is separate. A stage microbenchmark supports a stage claim only. Investigate same-sign downstream `shape_s`/`rows_native_s` give-back rather than dismissing it as noise. Use the current measured fraction f to report the ceiling 1/(1−f), with non-overlapping timing boundaries; do not reinstate the old whole-pipeline forecast.

For the tiny hardening checkpoint use its dedicated timer rule above, not the port's full-page clock rule. For native adoption require repeatable improvement of the complete replaced boundary and no reproducible integrated regression, with exact quality parity and build/test qualification. If clocks cannot establish integrated benefit, keep it explicit/off-default and state that. No skipping slow pages, dropping difficult rows, lowering image quality, relaxing source checks or promoting experimental final_export for speed. Global negligible-clean/under-one-second corrections remains an open task-level gate, not something this first kernel automatically meets.

## 4. No new pipeline or page model

Port existing numerical work within the existing stack. No new detector, 3D page reconstruction, per-line curve, field-band crop implementation, general reconcile/column repair, font provider, universal ink model, Rust OCR-model rewrite, production changes or repository mass reorganisation. `greekocr/` is read-only. The owner's field picture does not authorise changing the physical algorithm inside a parity port.

Archive CURL B precisely: own φ misclassified by every-pixel phase, anchor reset, remaining whole-row `rule_barriers`/`lost_ink`, and rectangular-strip tabs elsewhere. The unimplemented replacement is a shared-field band between neighbouring phase midlines beyond the anchor, with local component-shaped exceptions. It belongs to **unallocated CURL/geometry backlog**, not this task. The breathing over `ἐξόδων` at native `[1776,1074,1779,1078]` goes to INK-02's bounded mark/body question; no new owner can be guessed by phase alone. Flat/no-curl and left-edge field calibration remain open. A faithful Rust output cannot certify any of them.

## What counts as progress and the handoff

Report separately:

1. **Retained correctness:** support-bound helper now consumed on its intended branch, two physical xfails become passes, A preserved; stage cost and private acceptance status explicit. It is a bounds fix, not new text.
2. **Port progress:** a real current numerical caller executes Rust with meaningful fixtures, discrete/final parity and actual native counts. State exactly how much Python/native-library work remains and what old live work is displaced or still experimental.
3. **Speed progress:** repeatable boundary and integrated measurements, or a negative measured result that identifies the limiting work. Build-only, callback-only and no-call parity are not speed gains.
4. **Physical status:** complete curved-end count remains zero unless separately authorised later work changes it. Field-view defects and the new books remain named, not lost behind translation success.

Write `REPORT_R8-RUST-02-i1.md` and `.astra/fast_lines/out/round8/R8-RUST-02-i1/` with S/H/R source/build/input hashes, stage profile, boundary contract, real fixtures/mutations, deletion/caller map, clean-checkout tests, exact 208 and 22-page ledgers, raw valid/invalid clocks, backend counters and `ITERATION_HANDOFF.json/.md`. Add dated corrections to the CURL i3 report/handoff naming delivered 5faa178, the synthetic blank overhang and the narrower B failure. Preserve old receipts. Freeze a usable hardening checkpoint even if the port fails.

Coordinator-only held-out evaluation for changed frozen sources: baseline S and hardening H, then H and proposed R as applicable; **whole-page segmentation, every actual line strip, and actual-mask coverage maps for both versions on all44**, including unchanged pages and the recovered private body. Compare polygons/masks, source/row identities, exclusions, missing/extra text, native cuts/foreign/lost ink, overlaps/gaps and paired cost. Time the affected private `protect` call for hardening. Equivalent source checkpoints need no duplicate runs when equivalence is recorded. You receive aggregate checks, never private inputs/images. Repeated44 is regression evaluation; owner-disclosed material is development-retest.

A qualified numerical subset is a PARTIAL task result until the declared target route, duplicate removal, quality and task speed gate pass. At three iterations close honestly and advance to INK, then AUDIT; FONT stays parked. Astra writes i2 only after this result and full independent check; do not pre-write or self-launch it.

Meter 13% reported, no 14 October daily cap; standing 97% launch/99% run guards and stop signal remain. No worker spawning, private data, push or background job. Commit scoped changes with the required single trailer block. If Git is blocked, leave `.astra/commit-F8-R8-RUST-02-i1.sh`, source/hash-validated and **executable bare**; optional `--check` validates only. Keep commit state current and do not retry unguarded staging. Finish in plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
