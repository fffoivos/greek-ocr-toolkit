# R8-01b iteration 4: repeated work removed; physical calibration rejected

The candidate removes **368 repeated native mean filters** and repairs the M35 full-strip geometry shortcut. All **208 exports, 15,093 items and non-timing stage evidence** match independently checked `17e8845`. The proposed shared ink calibration failed native physical checks and remains offline. **G1b is PARTIAL; iteration-4 criteria 1 and 3 are not met.** These results do not authorize iterations 5–6.

## Sources and scope

The runtime baseline is `17e884598463afad8e4d97fc01a60a3e691d9b7a`; checkout `1090005` adds planning documents only. This work accessed only the 208 development pages. It changed no production `greekocr/` code and used no rejected page model, private page, PDF text, orientation work, background job or additional agent.

Evidence lives in [R8-01b-i4](../../../../.astra/fast_lines/out/round8/R8-01b-i4/index.html). The complete source/input/model/settings identities, exact commands, operation events, calibration probes and owner records are retained there. Reference reuse is separately bound by `REFERENCE_LINEAGE.json`; a pointer to slow code is not treated as validation.

## Accepted implementation

`geometry_feature_correct.retention_ink` prepares the original native source ROI, inherited 3h mean paper window and 15.3 DN support once. Its consumers are `geometry_context.correct_geometry`, `geometry_envelopes.correct` through `owned_retention`/`pad_unique`, and standalone `geometry_feature_correct.run`. They pass the prepared support through audit, nearby-ink repair and re-audit.

The producer returns image identity, source bounds, engineering height and an owned read-only boolean mask. A different image, ROI or height invalidates the result. Pixels remain immutable throughout the invocation. Candidate polygons, current neighboring ownership and off-row exemptions are always recomputed. This removes repeated kernels without caching a previous ownership verdict. The additional core-mask copies are measured: **28,782,816 bytes** across the full pass. No content-hash cache, global context or memo layer enters the runtime.

M35 again intersects every calibration polygon with its strip, including full-width strips. Empty/degenerate intersections are skipped; self-crossing geometry still raises instead of silently supplying calibration. If intersection repairs an invalid polygon, its normalized support is sampled afresh. Only a valid original full-strip polygon can reuse the existing components. Reused component dictionaries and bbox lists are unaliased. Valid development-page behavior is unchanged.

The tests exercise changed images, ROI/window changes, fresh neighbor ownership, changed candidate polygons, and valid, degenerate, self-crossing and repairable full-strip geometry. This is an observation/geometry contract repair, not a new page-feature gate.

## Physical experiment and first failing stage

[CUTOFF_CALLERS.md](../../../../.astra/fast_lines/out/round8/R8-01b-i4/CUTOFF_CALLERS.md) maps the actual .06/.08 DN callers, including Q8, native/reduced contacts, retained-ink guards, fragments, field bands, type barriers, rules and leaders. The two floors are 15.3 and 20.4 DN. A .06 **relative contrast** decision is a distinct quantity. Different spatial windows and populations remain explicit.

The proposed observation was darkness below the caller's local mean paper surface, compared with fluctuations between neighboring bright samples on that same raster. The estimator assumed locally stationary, independent Gaussian noise. Selecting two bright half-normal samples requires a variance correction by `1−2/π`; the initial unconditional estimator and its correction are both preserved. A 1/12 DN² uniform-rounding prior supplied the quantization variance. The three-sigma tolerance came from M35, not page tuning. These are hypotheses, not established scanner physics. The inherited 3h/4h engineering windows are not newly validated letter-body measurements.

The corrected estimator behaved as predicted on independent synthetic noise: true sigma 3 DN produced median 2.984766 DN and mask fraction 0.0012448. It failed on correlated noise: true sigma 0.419657 DN collapsed to the 0.288675 DN rounding prior, with mask fraction 0.0086983. Noise-free antialiased letters also contributed estimated noise. Thus selecting bright samples does not establish paper-only samples, and adjacent differences do not measure all structured background variation.

Native evidence independently falsified promotion:

| Native witness | Observation and consequence |
|---|---|
| 8686 p26, `[0,2092,80,2312]` | A visibly blank rectangular margin plateau contributes 2,899 selected near-white pixels. Response is 1.410522–4.426056 DN at a 0.866010 DN threshold. |
| 8686 p7, `[1574,1142,1754,1292]` | Rectangular support around isolated marks contributes 195 near-white pixels, with response 0.870621–2.959091 DN at 0.865981 DN. |
| Quiet 77d1, `[1380,1838,1590,1918]` | Raw 239–245 DN rectangles become native M14 components. The old M14 and slow M35 observations admit none in this checked region. Their actual bboxes and raw/contrast-stretched overlays are saved. |
| Weak 31f40 | Real weak front strokes and mirrored letters both respond. This observation cannot certify front print or authorize an exclusion. |
| 93f8 p1 background trace | Old .06 nominates two traces; old .08 none; the corrected trial one. Native verification accepts the background trace, but all seven proposed crossing cuts fail clear-flank checks: zero cuts. Verifier acceptance is not physical truth. |

Compression/sampling is a plausible explanation for the rectangular artifacts, not a proven source-history label. The first wrong stages are **paper/noise sample assignment and interpreting structured raster variation as independent noise**. The initial uncorrected 93f8 trial had five nominations; that superseded result is not conflated with the corrected one.

All **23 pinned pages and 92 native probes** were reviewed, including quiet/negative controls, e259 leaves/rule/blob, 3229 weak curves, 8686 ends, 8314 leaders/rules/cells, narrow 7a2 numerals, large Ψ/E and mixed typography. [CALIBRATION_REVIEW.md](../../../../.astra/fast_lines/out/round8/R8-01b-i4/CALIBRATION_REVIEW.md) retains each page's findings, old/new nominations and downstream dispositions. Raw, paper-sample, response and old/new-mask images, native/reduced arrays, coordinates and units are saved. Native component preparation and slow M35 photometry were forced on all 92 probes without scouts. Component identities are recorded; this does not claim that every component was semantically classified by eye.

Source-matched prior dense rule and slow pixel renderings were reused. The prior 574 native rule nominations were not treated as 574 genuine rules, and slow row/font identities remain conditional. The cheap/native comparison uses the actual Q8 crop and two-step area resampling, then pixel-center transforms; the initial coarse mapping was archived and corrected. Native arrays/images and rule nominations did not change during that coordinate correction. The forced old/new Q8 comparison returns identical items and the same nine cuts on all 23 pages; that downstream equality does not validate the changed component support.

**No calibration is promoted.** No old constant is equalized, hidden behind a caller-specific fallback or supplemented by a new guard. After physical falsification, a full 208-page trial of that policy was not run. The final 208-page candidate is only the safe reuse/geometry-validity change. Both empirical DN decisions remain explicit debt for 02; rejection of this trial does not validate them.

## Definitions, policies and execution accounting

| Feature | Iteration 1 | Candidate | Actual physical authority removed |
|---|---:|---:|---|
| Height | 6 | 6 | None; no valid body consumer was added. |
| Ink recipes/populations | 9 | 9 | None; selected DN cutoff subpolicies remain 2→2. |
| Ownership | 9 | 9 | None; fresh censuses still govern inherited decisions. |
| Bend/row paths | 7 | 7 | None; explicit 03 debt. |

Arithmetic modes remain two, following iteration 2's three-to-two algebraic consolidation. Moving a mask into `retention_ink` is not counted as a definition reduction.

| Runtime source comparison | Added | Deleted | Net |
|---|---:|---:|---:|
| This iteration versus 17e8845 | 48 | 31 | +17 |
| Cumulative versus d5dc3e2 | 142 | 682 | −540 |
| Cumulative versus caafbc5 | 227 | 572 | −345 |

Tests, offline tools, documentation and planner-helper cleanup are counted separately in `source-line-delta.json`. The additional runtime lines implement explicit source support, invalidation and correct geometry reuse. No active physical function/policy deletion is claimed this iteration. Earlier cache/copy removals remain intact.

The execution audit prioritized actual processed work: 726 retention filters visited 111,366,244 pixels, compared with 18,816 glyph resizes over 11,544,212 elements and 5,015 frame resizes over 36,145,799 elements. Byte-identical tiles at different positions do not establish reusable spatial ownership, so those remaining glyph/frame routes were not merged speculatively.

| Scope | Mean filters before→after | Input pixels no longer filtered |
|---|---:|---:|
| Full 208 | 4,936→4,568 | 56,518,884 |
| Existing slow 21 | 1,431→1,336 | 18,285,095 |
| Existing 37-control union | 2,196→1,955 | 36,926,990 |

Within retention, preparations fall **726→358**. The saved threshold/mean work is not moved into another hidden scan. Candidate/current-neighbor masks remain fresh and the added 28.8 MB of owned copies are charged. All earlier reductions—103 closings, 103 CC8 builds, eight remaps and 2,205 net histograms—are preserved. Other operation totals equal 17e8845.

`operation-counts.json` uses the same selected cv2 resize/remap/morphologyEx/boxFilter/CC8 and numpy bincount/percentile/quantile scope as the checked baseline. Kernel-area work is a nominal proxy, not an OpenCV instruction count. Other kernels, GEOS, copying and passing overhead remain in uninstrumented clocks. Tracing/content hashing is offline. The baseline trace was reused only after source equality; two candidate instrumented passes agree on operations and output, with the final pass adding ROI/copy metadata. No runtime cache returned. The rejected calibration adds no default work.

## Timing and preservation

All times below are milliseconds; correction time excludes only decode and original Paddle. Every correction dependency is included. Nested stage times are not summed.

| Cohort | n | Median | p95 | Maximum |
|---|---:|---:|---:|---:|
| all | 208 | 195.854 | 1336.672 | 2085.002 |
| agreement | 40 | 66.676 | 548.503 | 662.693 |
| discrepancy | 101 | 217.951 | 1368.552 | 1965.037 |

The negligible-clean/under-one-second target remains unmet: **21 pages exceed one second**. [TIMING.md](../../../../.astra/fast_lines/out/round8/R8-01b-i4/TIMING.md) lists all of them, every stage, and all paired per-page clocks. The field, recovery and row/ownership mechanisms remain dominant.

On the same 37 controls, baseline→candidate forward and candidate→baseline reversed give paired correction medians **+7.953/-6.351 ms**, with totals +419.255/-314.856 ms. The sign reverses: there is **no demonstrated overall speed gain or consistent slowdown**. Detector median deltas are -0.413/-0.112 ms; decode deltas +0.045/-0.025 ms. None is subtracted to manufacture a normalized gain. Measured kernel work falls; wall-clock effects remain load-sensitive.

The suite reports **261 passed and one known strict faint-front xfail**. All 208 outputs and physical stage records match 17e8845 after clocks are removed, with 15,093 finite undiscounted items. All 104 comments and 256 marks preserve exact identities, quotations and status lineage. The unchanged ledger is inherited, not claimed as a fresh 360-record visual review.

Eleven historical controls were freshly rendered and inspected: Ψ, large E, narrow “32”, weak τῆς, wide-gap text, finite-rule ends and c0#118/d83#108 remain. The missing separate Μαυρομιχάλης row, 4959 central recovery and later d83 apparatus row remain missing/incomplete. Curled ends and fully faint genuine front print remain open. There are no changed final crops or new lost/reassigned glyphs in this candidate. Output equality supports preservation; it does not prove inherited rows correct.

## Iteration-4 decision and handoff

| Criterion | Worker finding | Remaining independent decision |
|---|---|---|
| 1. Fewer independent physical definitions/decisions | **NOT MET**: DN policies remain two; counts 6/9/9/7. | Failed calibration cannot authorize 5–6. |
| 2. Deleted cache machinery and less redundant execution | **PASS cumulatively**: −540 runtime lines and prior savings plus 368 mean filters. | Check caller/dataflow and full accounting. |
| 3. Physical improvement in a real consumer | **NOT MET**: calibration rejected; body authority unresolved. | Live numerical reuse is not a physical authority. |
| 4. Preserved text and honest stable/improved cost | **PASS on worker evidence**, independent review pending. | Coordinator alone performs its private check. |

Recommend the safe reuse/geometry-validity candidate for independent carry-forward review. Until that review, the independently accepted best head remains 17e8845. No further iteration is launched or authorized by this report. Under PLAN, unmet criteria 1/3 call for the coordinator to hand the best checked code and explicit failures to 02.

02's next repair is to establish paper/source samples and scanner/resampling/quantization response without losing weak front strokes, then decide whether one calibrated observation can replace both floors. The remaining glyph/frame repeated work needs source/transform/ownership identity before reuse. 03 owns row/class attribution, finite domains and final crops. The clipped 4959 measurement, 3229 η descender, 31f40 λ/ghost contacts, 8314 leaders/numerals and capital priors remain unresolved; this iteration did not retry the conditional scalar fitter.

## Reproduction, housekeeping and actual commit state

`COMMANDS.md`, `ITERATION_HANDOFF.json`/Markdown and `CONSOLIDATION_DELTA.json` contain source/input/settings identities, exact replay commands, line accounting, test records and duration. The assigned Python runs with `PYTHONDONTWRITEBYTECODE=1`, OpenCV 10 threads and ONNX CPU sequential intra/inter one. The native gallery contains diagnostics as diagnostics, not discounted output lines.

A dated addendum and `R8-01b-i3/POST_CHECK_STATUS.json` record that 17e8845 now exists and was independently accepted; the historical staging failure and old receipts remain. Four imported worker-root helpers targeting ff-plan were inventoried and removed: FP8, FP8b, FP8e and FP8f. Their 181 deleted lines are housekeeping, not runtime savings. Worker fallbacks and the planner worktree are untouched.

The scoped staging attempt failed with `index.lock: Operation not permitted`. **No worker commit was made.** The source-bound fallback is `.astra/commit-F8-R8-01b-i4.sh`, with patch, commit message and isolated apply/hash validation. It stages only this iteration's 14 files and checks the branch, base, file hashes and empty index. No push occurred. The launch meter was 68%; no later reading is available. Actual duration and packaging completion are recorded in the handoff.

## Post-check addendum — 12 October 2026

The coordinator applied the worker patch as **cb4d6b4894f130e42a46885c626ec66b55f540b0** and independently accepted it as the best head. The full check is `greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8c-01b-i4_check.md`. Its criteria remain **FAIL/PASS/FAIL/PASS**, G1b **PARTIAL**. Consolidation closed at iteration 4; iterations 5–6 were not authorized. The historical worker staging failure above remains true and is not rewritten as a worker commit.

R8-02 began at `e1fe6ce`, a planning-documents merge over cb4d6b4; its runtime tree was verified identical before editing. The coordinator's private 44/44 result is reported by the coordinator only; the ink worker did not access those pages or outputs. A structured `POST_CHECK_STATUS.json` is beside a byte-preserved copy of the original handoff in this worktree's `.astra/fast_lines/out/round8/R8-01b-i4/`. Original external evidence, images, hashes and receipts remain untouched.

The newer R8-02 instructions supersede this report's proposed calibration direction: the mean-paper/bright-neighbor independent-noise assumption is rejected, not an invitation to another sigma/window/floor variant. DN sample/source debt remains with02; complete body, glyph-class and row attribution belongs to03.
