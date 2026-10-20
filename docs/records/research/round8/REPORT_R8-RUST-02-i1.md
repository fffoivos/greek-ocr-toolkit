# R8-RUST-02 i1 — narrow hardening and current M15 batch port

14 October 2026. **PARTIAL.** The support-bound correction is retained locally as the independently reviewable H checkpoint; two strict hardening xfails now pass. The current M15 interpolation/correlation batch executes native Rust explicitly, with exact development parity. Python remains the normal default. The complete native batch is 9.3% slower and integrated benefit is unproven. This is a bounded batch port, not the complete per-field mesh kernel, adopted route, physical-field repair, or completed task speed gate. Private acceptance remains coordinator-only.

## Source checkpoints and retained correctness

S is launch `e8a29a2c8b85305a7dd941307e8ab026e8586a6d`, branch `astra/ff-r8-stack`: its runtime is exactly checked `5faa178`/`fea451c`. The branch was not reset. H changes only `type_barriers.protect` and removes the two repaired xfail decorators in `test_curl_consumer.py`. Its snapshot precedes all numerical edits. The exact patch SHA256 remains `26e513e0820b7aaadb600159c339678ac8d16c2c40ebd368038ba16bd4b88cb5`.

H consumes existing `supported_extent` only on the newly retained local-unknown side with valid supplied numeric bounds, then rechecks the actual clipped piece with `piece_support`. Verified-rule, absent/invalid-bound, witness-free and ordinary proposal paths retain their policies. The two real recover→protect assertions now pass; src37 and every unrelated physical failure remain strict xfails. The fixture's synthetic 15-pixel blank-paper overhang has zero ink and no natural occurrence on 208. It repairs a geometric admission contract, not newly recovered text.

The previous exact-source S↔H208 receipt is reused: all 192 non-test/non-evidence runtime files match its hardening source. `H_CHECKPOINT.json` binds that receipt, patch and source. Fresh native tests and actual integrated reruns of 8686 p5, 3229 p5, 9ea1 p202, 466c p323 and 93f8 p1 all reproduce the saved exports. The new full 208 H pass also matches every prior hardening export. A's recovered body stays present; its tails/νων remain incomplete.

The dedicated timer uses 20 warmups and 20 fixed alternating batches of 100 fresh-equivalent calls per arm. Gray/item copies occur before the timer; timer/empty-loop overhead and all samples are retained. Accepted 8686 p5, abstaining 93f8 p1 and a real non-branch 8686 control are captured from the real recovery caller. The accepted-side median paired increment is 0.138171 ms/call, p05/p95−0.283716/+0.545261ms, maximum0.667996ms. Charging that increment to all three actual 8686 protect calls gives 0.414513 ms/page, conservatively including unaffected calls. Abstention/non-branch increments are −0.001645/+0.011614ms. Both preset≤1ms/call and≤5ms/page budgets pass. Capturing an additional profiled compose duplicated records in the raw capture; the summary uses actual unprofiled counts 3 and 1, not those duplicated capture counts. No detector-drift criterion is imposed on this small correction.

H's coordinator private 44 identity, actual recovered-body review and affected private protect timer are pending. No private input/image was accessed. The old i3 receipts remain unchanged; dated report/handoff corrections name delivered5faa178 and the narrower withdrawn B failure.

## Boundary selection and actual caller

The current, separately instrumented call tree is in `PROFILE_CALL_TREE.json` and its two pstats files. Render calls prepare, the numerical batch and certify/invert; field proposal additionally includes unbend, regional model inference, current M17 and mapping. Inclusive timers are not added together. On8686p5/3229p5, render totals 0.19684/0.15149 s, prepare 0.13500/0.10306 s, and shifts_many 0.03150/0.02142 s. Certify is 0.01981/0.01790 s including its own inverse call; the second inverse belongs directly to render. The enclosing proposals are 0.4817/0.3756 s, including current field M17 of 0.1272/0.0755 s. Additional request-completion M17 on 8686 belongs to type, not field construction. This excludes the historical error of treating inference/M17 time as entirely Rust-addressable.

The implemented partial boundary is current nested `shifts_many`, now called through one typed-array `Batch` object per measured field. Each outward step remains sequential; a refinement batch contains up to 8 independent columns. Each actual batch executes one C ABI call, rather than one call per lag/pixel. The preferred entire per-field sweep/refinement port is **not delivered**. Python still prepares profiles/windows, performs moved-coordinate interpolation and demeaning before the batch, propagates the mesh, builds joint templates and shared template energy once per iteration, applies SciPy Gaussian filters and performs both refinement iterations. Seed/scale/body selection and certify/invert remain in their original callers.

Native Rust replaces lagged profile interpolation, valid-window centering, energy/dot reductions, score normalization, first-maximum selection, parabolic lag refinement, weight floor and short-window outputs. It invokes no Python/numerical callback and never runs the Python scorer alongside native in normal execution. Explicit replay/tests intentionally compare both. The Python body is a readable oracle/default during qualification. No bridge copies a physical decision. M17/request axes/supports/domains/retain_support, gap/dilation logic and support_accounting are untouched; the historical pilot stays parked. Its gap/dilation mutation debt is not claimed fixed. INK's atlas membership defect is untouched.

`CONTRACT.md` freezes shapes, native-pixel units, dtypes, order, padding, endpoint/tie rules and synchronous buffer lifetime. Float32 measured profiles are promoted/transposed once per field. Broadcast/non-contiguous before/energy buffers are copied explicitly; contiguous finite arrays are borrowed only during the call. Rust uses two W-element scratch vectors and NumPy-owned delta/weight(C,K), scores(C,K,L). Allocations/copies and ctypes dispatch remain inside measured calls; per-field conversion is separately reported and charged to integrated clocks. This is not a total allocator/RSS census.

`FAST_LINES_FIELD_BACKEND` is read once at module import; default=python, explicit=rust. Missing/unusable native build raises before Stack page/session work. Actual Python/FFI entries, field preparation and copied bytes are counted at entry; fallback is absent and never inferred from region count. An import-only relocation after the first matched-input pass is recorded in `IMPORT_RELOCATION_EQUIVALENCE.json`: non-import AST is identical. The actual final source is exercised by all integrated clocks, including intermediate parity.

## Reproducible tests and local replay evidence

The dependency-free prototype crate has a committed lockfile/release configuration and bare build script. No PyO3/Python ABI, dynamic-lookup flags, ignored cargo-home setup, vendor location or another worktree's interpreter is required. Custom library/target locations are configurable. Compiler rustc/cargo 1.96.1, Apple aarch64, release O3/thinLTO/one codegen unit; original release build 1.832 s, independent clean-source build 1.917 s. Compiler/binary/source identities are in `BUILD.json` and `CLEAN_CHECKOUT.json`. Other platforms/compiler/NumPy combinations remain unqualified; interpolation explicitly uses the current NumPy FMA behavior.

Committed tests contain 24 numerical batches from actual standalone render calls (which may bypass the live edge gate) and six render→certify consumers from8686/4959/3229, c8p36, flat 466c p323 and skew 23a p3, plus independent constant, straight, known-shift, short, border/endpoint, near-tie and empty-page controls. All six capture calls explicitly invoke render; their fixture count is not a live-route denominator. The render consumers freeze actual prepared profiles/components, replace pixel preparation/remap with those inputs, then run the real numerical wrapper, row prediction and certify. They do not claim to test frozen pixel preparation itself. All tests fail if their committed fixtures are missing.

Worktree Python-default 411 passed / 15 strict xfails; native-selected 450 passed / 15 strict xfails. Clean checkout without a library 410 passed / one older skip / 15 strict xfails. Explicit native without a build fails clearly; clean offline build then 80 native comparison/consumer tests pass with zero skips. Native comparisons are enabled explicitly, never silently skipped in qualification. The initial test-only valid-mask mutation changed the Python lengths but missed Rust's prepared int64 input; its failing test receipt is preserved, and the mutation now changes the actual backend input.

Three independently release-built native mutations are reproducible with `r8_rust02_mutations.py`; each replacement asserts exactly one source target. Endpoint change fails 4 tests, including real c8/8686 render→certify consumers; last-maximum tie fails 13; dropping the valid-window mask fails 35. These are real native consumer mutations, not a second handwritten formula.

The full frozen 41 remains byte-identical with SHA256 `377df97a07b0428b8591783f2dd093d11e0c78fb56ea4c7511aa4a7ed998a766`; all 208 pages stay in the denominator. H↔R has 208/208 identical final exports, intermediate field/certificate/source/exclusion evidence and native-mask coverage: 15,094 items, 7,140 actual Rust calls on 73 pages / 124 fields, 135 no-call pages, zero fallbacks. The separate 22-page owner appendix has 719 identical items, 106 calls on two pages/two fields, 20 no-call pages. Those two are 1876 p0091/p0349; owner-confirmed 1868 p0023 makes zero live native calls. No forced display field is counted as production speedup. A separate p0023 forced replay makes 44 Rust calls and reproduces the H field exactly; those calls are diagnostic only and do not repair the silent runtime gate or certify physical curl.

All 22 internal PNGs were separately frozen before source changes, preserving_REPL names and the 7/15 book split. Only the permitted fieldview script, dev/owner metadata and owner PNGs were read. Owner pages are development-retest; no general positive label is invented. Full matched-input ledgers, initial-map/item hashes, both-arm whole pages, every actual line strip and actual-mask coverage are local evidence. Committed fixtures/tests are distinct from ignored 230-page replay evidence. Identical masks preserve existing defects and do not newly certify physical output.

## Measured speed and remaining limits

**Measured speed result: negative at this boundary; no native adoption.** On the full 208, Python batch work is 4.741772 s and Rust 5.183365 s (sum of 7-pair call medians), **9.313% more time /0.915× speedup**. Owner 22 is 0.045478→0.050464 s, 10.962% more time. These batch-call clocks include per-call conversions, allocations and dispatch. Adding the separately recorded field binding gives 5.194315 s on 208 (about 9.54% more than H) and 0.050508 s on the appendix. The binding observations include the first replay library load; the actual warmed integrated clocks include all binding costs and keep import/session setup separate. Rust has no callbacks. Separately, 124/2 field preparations cost 0.010950/0.000044 s and promote/copy 42,020,240/402,664 bytes; integrated clocks include this work. Cumulative actual copied payload is191,005,104bytes on 208 and1,909,472bytes on22, not peak memory.

All 7,246 actual batches have bit-exact scores, deltas and weights. The relocated Python oracle also exactly reproduces H on every call. There is zero coordinate roundoff requiring a tolerance, zero changed discrete consumer/source/exclusion identities and zero changed actual native masks.

| Population | Repetition / order | Correction change | File-to-final change | Field proposal H→R, s | Detector drift | Valid |
|---|---|---:|---:|---:|---:|---|
| Established208 | 1 / HR | -0.727% | -0.975% | 37.9390→37.4472 | -0.096% | yes |
| Established208 | 1 / RH | +0.794% | +0.994% | 37.8577→38.3308 | +0.046% | yes |
| Established208 | 2 / HR | -1.093% | -1.242% | 38.3654→37.9056 | -0.108% | yes |
| Established208 | 2 / RH | +1.045% | +1.194% | 37.7120→38.4736 | -0.084% | yes |
| Owner22 | 1 / HR | -1.789% | -1.431% | 0.5082→0.4994 | -0.072% | yes |
| Owner22 | 1 / RH | +1.193% | +0.555% | 0.5018→0.4966 | -0.012% | yes |
| Owner22 | 2 / HR | +0.756% | -0.364% | 0.5252→0.5383 | -0.094% | yes |
| Owner22 | 2 / RH | -1.379% | -0.675% | 0.5161→0.5117 | -0.170% | yes |

Each order has two fixed repetitions; all 208 and the separate 22 appear in every pass. All eight population/order blocks pass the declared 5% aggregate primary-detector drift control and exactness checks. There are 920 paired samples / 1,840 file-to-final executions, zero invalid samples and no replacements. On 208, both forward runs improve and both reverse runs regress; field-proposal time also changes sign. **No repeatable integrated gain is established.** No-call controls and per-page deltas remain in `TIMING_PER_PAGE.json` and raw records. These clocks do not justify an adoption claim.

| Population / arm | Corrections median / p95 / max, ms | Corrections >1s | File-to-final median / p95 / max, ms | File-to-final >1s |
|---|---:|---:|---:|---:|
| 208 / H | 248.723 / 1675.736 / 2636.190 | 27 | 401.718 / 1870.012 / 2837.619 | 34 |
| 208 / R | 248.006 / 1682.306 / 2656.959 | 27 | 398.459 / 1877.265 / 2857.354 | 34 |
| 22 / H | 52.650 / 348.497 / 397.924 | 0 | 182.017 / 476.077 / 531.278 | 0 |
| 22 / R | 52.032 / 341.358 / 391.784 | 0 | 181.503 / 468.136 / 525.604 | 0 |

Census distributions take each page’s median of its four complete clocks, then compute the population statistics. Raw individual-pass distributions and each page’s paired changes are separately retained; the table is not a claim that the 27 slow pages have been solved.

| 208 call pages | shape R−H, ms | rows_native R−H, ms |
|---|---:|---:|
| 1 / HR | -59.524 | -37.715 |
| 1 / RH | +13.714 | +28.461 |
| 2 / HR | +31.618 | -10.066 |
| 2 / RH | +45.875 | +2.686 |

The historical pilot’s same-sign downstream give-back is not reproduced: these stages change sign across orders/repetitions, with all intermediate inputs/evidence and final masks equal. The 135 no-call controls are reported separately, not dismissed or subtracted as noise. This investigation establishes no stable downstream saving or penalty.

A separate diagnostic on the 24 committed fixtures finds about 0.943% of measured batch time outside the C ABI interval. The interval includes ctypes argument handling and native computation; the proxy itself adds timer overhead. Thus bridge removal alone is not a demonstrated remedy on that subset. The immediate negative result is inside the current computation interval; interpolation versus reduction is not separately attributed. Source inspection suggests scalar repeated binary searches may cost more than NumPy’s bulk interpolation, but that is an **unmeasured inference**, not an established subkernel claim. No diagnostic time is subtracted from the reported Rust clocks.

Current measured fraction f = 5.144% of 208 corrections gives a free-boundary ceiling of 1.05423×; owner 22 is 2.359% / 1.02416×. These use non-overlapping whole-batch medians and uninstrumented correction sums, measured separately. They are approximate ceilings for this subset, not a new whole-pipeline forecast. Pixel preparation, the remaining Python mesh loop/refinement/smoothing, model inference, type/residual and ownership remain the large enclosing work.

The final isolated build uses an empty CARGO_HOME, empty RUSTFLAGS and a fresh target directory: 1.819 s, 80 native tests passed. Fresh process import+session is 0.677 s Python / 0.662 s Rust (session≈0.0166 s each); process wall 0.730/0.714 s. These are setup observations, not service speed gains. The final fixture-integrity tests again pass 80 with both the original and isolated binaries.

Unprofiled file clocks include decode, primary/regional inference, buffer conversion, all native/Python work and complete corrections; comparison/export/PNG work is outside clocks. OpenCV request0 disables parallel workers and receipts observe1; ONNX CPU is sequential intra/inter1/1. No extra worker parallelism, remote provisioning, push, publication or production work occurs. Compilation/import/session setup and warmed service clocks are separate. The coordinator supplied the quiet-machine window; OS-wide process listing is unavailable in this sandbox. Every valid/invalid sample and order is retained. The replay harness's initial source-inspection failure occurred before any kernel measurement and is preserved separately.

The default remains hardened Python. A qualified batch subset is a partial translation result; independent adoption and removal of the displaced live adapter/reference route have not happened. Global negligible-clean/under-one-second corrections remains open.

## Physical status and handoff

Complete curved endings retained: **zero**. A, the four R rows, accepted B row, ἀποξήρανσίν and current source exclusions remain identical. `final_export=False`, `bend=False`. False bending on flat pages, binding-side misses/under-bending, finite-rule blocks and incomplete outside-box support are preserved defects. Whole-row crop-floor/overlap/reconcile/source/mark failures are not hidden behind translation parity.

Withdrawn CURL B is archived precisely: ownφ wrongly fails every-pixel phase ownership; an anchor reset discards the continuation; whole-row rule/lost-ink gates survive; rectangular old-strip unions make tabs elsewhere. Shared-field bands between neighbouring phase midlines beyond the anchor, with local component-shaped exceptions, remain unimplemented, unallocated CURL/geometry backlog. The breathing overἐξόδων at `[1776,1074,1779,1078]` belongs to INK-02's bounded mark/body question. No new owner is guessed from phase. FONT stays parked.

This is i1 of at most 3. No i2/INK prompt, worker or successor job is authored/launched. Coordinator checks S↔H and H↔proposed R privately: whole pages, every actual strip and actual-mask coverage on all 44 including unchanged pages/recovered private body, sources/exclusions/ownership/cuts/foreign/lost ink/overlap/gaps and paired costs, plus the private affected protect timer. Source-equivalent checkpoints need no duplicate private run if equivalence is recorded. The worker receives aggregate results only.

**Worker commit: none.** One scoped staging attempt failed creating the protected worktree index.lock (`Operation not permitted`); no staging retry or alternate index was used. The executable `.astra/commit-F8-R8-RUST-02-i1.sh` validates exact head/branch, scoped files, source/build/input/receipt hashes, H budget,208+22 parity, all real batch/oracle/score comparisons, mutations and clean checkout. Invoked bare, it commits the two-file H checkpoint first and the remaining explicit/off-default R port second; `--check` validates only. Coordinator receipts supersede this worker-return commit state after execution. No push occurred. `ITERATION_HANDOFF.json/.md` records the source-bound candidate and pending private acceptance.

## 14 October 2026 — i2 dated commit/check correction

Coordinator committed H=8bfcbd056d639ae4e57cb1e23e69749471b80eb5 and explicit/off-default R=55607147cee021c6c1027ec3b2b7552abd0ce321. The full independent R8-RUST-02-i1 check accepts with notes. H is adopted and privately qualified: 44/44 polygons identical, affected protect +0.060 ms/call (p95 +0.075, max +0.078), paired correction median +0.7 ms with detector −0.1 ms. This supersedes the original worker-return “no commit/private pending” status; original receipts are preserved, with copies under i2/i1-originals. H repairs a synthetic blank-paper overhang, not new text. R remains exact but slower and off-default. Native parity remains platform-specific. No private input was received by the worker.
