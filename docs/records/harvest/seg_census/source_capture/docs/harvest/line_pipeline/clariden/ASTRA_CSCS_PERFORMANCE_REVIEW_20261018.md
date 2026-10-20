# Astra review: qualified CSCS filtering throughput 0.4

**Reviewer:** GPT-6 Astra (`gpt-6-astra`), extra-high reasoning. **Updated:** 2026-10-19 (Europe/Athens; original review dated 2026-10-18). **Scope:** performance preservation, bounded concurrency and measurement validity only.

**Verdict: PASS; select 64 native workers with prefetch factor 64 on qualified source `6261c3f5…`.** The final fixed-worker 6,144-row comparison takes **55.44 seconds**, versus **65.78 seconds at factor 16**, with identical scientific records and zero faults. That is a **1.187× same-pilot throughput improvement** from wider lookahead. All 64 native worker PIDs are verified in the measured task cgroup; its cumulative peak across the three cases is **30.81 GB**. The source, full input bindings and selected configuration are ready for a diagnostic census. Full-census execution remains unlaunched. [Final pilot](efficiency/throughput_03.json) [Bound full plan](full-run-plan.json) [Runtime review](ASTRA_CSCS_REVIEW_20261018.md)

## P1 — PASS: larger lookahead remains bounded and ordered

The qualified `f9e06adc…` pool validates integer worker counts 1–64 and integer prefetch factors 1–16, default 2. It retains at most `workers × factor` pending row/future pairs: at most 1,024 for that qualified cap. The later qualified runtime extends the worker cap to 256; the final source also supports factors up to 64 under a strict global 4,096-record limit (P4–P5). Only worker measurement runs in executor threads. Input iteration, preparation, cache access, SQLite transactions, correction composition, deduplication and output publication stay on the coordinator. Results are emitted in original order. Existing cleanup waits for active deadline-bounded requests, cancels queued work and attempts every worker's cleanup. [Pool](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_parallel.py:18)

The wider window can keep other workers supplied while an earlier slow row blocks ordered consumption. It does not eliminate that delay: once the finite window drains behind the slow row, workers can still become idle. The bound counts pending observations, not a fixed number of bytes; increasing it retains more row payloads/results. Native row processing also consumes per-worker memory. Candidate deployment should therefore compare actual wall time and peak memory, not assume a larger queue is always faster.

The factor enters the run configuration and runtime receipt. Since the configuration is part of the ledger binding, changing it requires a separately bound run; it cannot silently alter an existing resume. Raw page summaries come from immutable registered inventories, so further lookahead does not read evolving correction decisions. [Coordinator](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py:370)

## P2 — PASS: scientific implementation and comparison contract are preserved

Compared with the earlier qualified `fd4d5e20…` archive, only `line_pipeline_census.py`, `line_pipeline_parallel.py` and the CS8 unavailable-context adapter in `line_pipeline_native.py` changed under `greekocr/` (293 files compared). All detector, geometry, label-correction, source-routing and accepted segmentation-policy bytes are unchanged. The candidate is pinned to manifest `f9e06adc1e43b24b1760935c45cefff70abc5a481b3411fae8df6ab64af94870`; its archive, all 319 payload entries and current source equality were independently verified. Registry hashes validate; census is 0.4 and segmentation remains 0.5.

The reviewer independently ran **235 pipeline/CP2/CP3/CP4c tests**, all passing in **2.34 seconds**. A separate metadata-only end-to-end fixture compared 50 rows at four workers with factors 1, 2, 8 and 16. All ordered decisions matched after removing the intentional run fingerprint, including duplicate-crop and held-out cases. No corpus image was processed on the Mac. The CS8 regression executes the actual `_direct_rules` function only on a tiny synthetic support plane with a fixed Hough proposal; its second real polynomial fit loses all support. The same exception outside that function is rejected by the classifier. Queue tests also establish coordinator-owned preparation, exact lookahead bounds and continued work behind a synthetic straggler.

The qualification helper keeps the same exact scientific comparison exclusions: run identity and the known segmentation orientation elapsed-time leaf. Raw decision records are retained. It requires unique legal factors with default 2 first, measures one-worker/factor-2 once as the serial baseline, and assigns distinct fresh directories to every worker/factor case. Existing zero-cache, complete-measurement and error checks remain active. Five ambiguous-factor guard cases pass. [Qualification helper](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/worker.py:106)

## P3 — PASS: native queue improvement on 768 rows and 6,144-row throughput

The first fresh queue experiment, job **3692858** on the pre-CS8 queue candidate, passes exact scientific parity for all seven cases on the same 192-row SHA-priority sample. Every case makes 192 native attempts with zero cache, unavailable, infrastructure or cleanup faults. At 16 workers, widening factor 2 to 8 reduces whole-call time from **13.17 to 8.85 seconds: 1.49× further sample speedup**. The serial baseline is 44.37 seconds. The 32-worker/factor-8 and 64-worker cases are approximately 8.83–8.85 seconds; this sample does not show a material benefit from those extra workers. The result qualifies the scheduling change for this sample, not the later CS8 repair or full-corpus throughput. [Fresh queue comparison](efficiency/queue_01-qualification.json)

| Workers | Prefetch factor | Whole-call seconds |
|---:|---:|---:|
| 1 | 2 | 44.37 |
| 16 | 2 | 13.17 |
| 16 | 8 | 8.85 |
| 32 | 2 | 11.80 |
| 32 | 8 | 8.83 |
| 64 | 2 | 8.84 |
| 64 | 8 | 8.85 |

The larger 768-row serial probe completed all native attempts but found one empty oblique-rule refit during source-context detection, stopping qualification. Its 145.25-second filtering/export boundary is not a successful speed benchmark. The exact traceback supports narrow unavailable-context handling without changing detector bytes; the repaired serial rerun now preserves all 767 prior scientific records and changes only the former error to conservative HOLD / UNCERTAIN. The expanded parallel sweep now passes all ten cases with the stricter within-generation comparator. [Repair preservation](efficiency/repair-preservation.json) [Failure receipt](efficiency/scaling-failure.json) [Trace](efficiency/empty_fit_probe.log)


The repaired **768-row** sweep established the next qualification stage. All ten cases have exactly the same ordered scientific digest, 768 fresh attempts each, and zero infrastructure, cache, unavailable-measurement or cleanup faults. The 32-worker/factor-16 case is fastest in this single sweep; 64-worker/factor-16 is 2.4% slower, which is too small a difference to treat as a repeatable advantage without a longer measurement. No setting changes detector or correction semantics. [Expanded comparison](efficiency/scaling_02-qualification.json)

| Workers | Prefetch factor | Whole-call seconds |
|---:|---:|---:|
| 1 | 2 | 146.31 |
| 16 | 2 | 29.34 |
| 16 | 8 | 18.86 |
| 16 | 16 | 16.34 |
| 32 | 2 | 21.36 |
| 32 | 8 | 14.33 |
| 32 | 16 | 11.36 |
| 64 | 2 | 17.08 |
| 64 | 8 | 11.95 |
| 64 | 16 | 11.63 |

A separate 6,144-row pilot compares 32/factor-16 with 64/factor-16 using fresh directories and the unchanged strict scientific comparator. It makes no serial-speedup claim. The exact executed helper and launcher are archived, and I verified both SHA values against the submission receipt. The actual pair has a separate validation receipt: two distinct cases, base configs equal to their qualifier ledgers, and configurations identical except worker/queue settings. The future helper now rejects fewer than two distinct cases, checks matching fixed configuration/qualification inputs before sampling and explicitly rejects INFRA dispositions. The staged script remains unchanged. The final pilot receipt now passes: 6,144 fresh attempts per case, no infrastructure, cache, unavailable-measurement or cleanup faults, exact scientific digest equality and 64-CPU affinity. I checked both base-config SHAs against the independently saved qualifier-ledger validation and verified the executed helper SHA. It records 4,692 segmentation KEEP, 1,247 UNCERTAIN and 205 DROP in each run, with final 5,939 HOLD and 205 DROP. No automatic admission is implied. [Executed helper](efficiency/throughput_native_01.py) [Submission](efficiency/throughput_01-submission.json) [Actual base-config validation](efficiency/throughput_01-base-config-validation.json)

| Longer pilot setting | Whole-call seconds | Rows/second |
|---|---:|---:|
| 32 workers, factor 16 | 81.05 | 75.80 |
| 64 workers, factor 16 | 63.00 | 97.53 |

This longer result reverses the small 768-row ranking of 32 versus 64 workers, demonstrating why the tiny timing difference was not a reliable node optimum. The sample contains 2,048 rows each from original-v2 train, W1 and W2; the full census has different parent weights and additionally includes original-v2 dev/test. These are throughput measurements for the bound sample, not a population retention estimate or a guaranteed corpus duration. [Longer pilot receipt](efficiency/throughput_01.json)

The inspected 192-row profile spends **49.18 of 56.68 profiled seconds** in source-context `process_page`, with 29 detections; Pillow image loading takes **1.54 seconds**. The slowest row takes **11.12 seconds**, illustrating why a small batch can be dominated by one context tail. CPU time is 56.54 versus native wall time 56.69 seconds in this separate serial profiled pass. These observations support measuring queue occupancy and tails before prioritizing decoder caches; they do not establish the larger-run speedup. Profiling adds overhead, and timings from separate runs must not be combined into an exact speedup. The coordinator profile contains inconsistent/non-additive threaded counters (67 seconds of cumulative join against 14.19 seconds whole-call wall); it must not be summed or used to infer a serial fraction. [Native function profile](efficiency/native.json) [Per-row times](efficiency/profile.json) [Coordinator profile](efficiency/coordinator.json) The prefetch comparison must use the same frozen rows, fresh run directories and native runtime, and preserve every scientific result across 16/32/64-worker cases and factors 2/8. Record whole-call time, native attempts, memory and failures separately from cached or partial runs.

The previously prepared 12-hour Slurm limit was an allocation limit. The 192-row timing supported a measured sample speedup, not a validated 12–16-hour corpus ETA. A larger sample and profiling can improve the forecast, but 592,466-row completion time remains unmeasured until actual execution. No full census is launched by this review, and unresolved admission evidence remains unchanged.

## P4 — PASS: higher-worker equality and measured resource tradeoff

Candidate manifest `786f64d7712f0717b2d5ab7fadde9775fa00fd866163f737618eb119b67132d1` changes only the worker-cap literal under `greekocr/` compared with qualified `f9e06adc…`. The other changes are the matching qualifier guard, explicit CPU-affinity receipt, invalid-count regression inputs, registry history and documentation. Native measurement, detector, geometry, accepted segmentation and corrective bytes are unchanged. I verified the archive, all 319 payload files, their equality to current source, and the version registry. **235 pipeline/CP2/CP3/CP4c tests pass in 2.31 seconds.**

The ordered/coordinator-owned algorithm is unchanged; supported counts remain strict integers and the queue remains bounded by workers times factor. The larger cap permits up to 256 active native processes and 4,096 pending records. It is a supported limit, not an efficiency recommendation or memory guarantee. The fresh **768-row** comparison now passes on job **3692933** with actual 256-CPU affinity: seven serial/64/128/256 worker and factor-2/16 cases, identical ordered scientific digest and zero infrastructure/cache/unavailable/cleanup faults. A separately bound cross-generation comparison preserves all 768 scientific records from f9 after validating and excluding only changed source identity and the existing clock leaf. This qualifies `786f64d7…` for diagnostic use. [High-worker qualification](efficiency/scaling_03-qualification.json) [Generation preservation](efficiency/scaling_03-generation-parity.json)

More workers are slower in this short sweep: factor-16 cases take 13.05 seconds at 64, 14.70 at 128 and 18.81 at 256. The matched instrumented 6,144-row pilot now passes all three cases with exact scientific equality, 6,144 fresh attempts each, zero faults, actual 256-CPU affinity and verified membership for all 64/128/256 native worker PIDs. Each run reports 4,692 KEEP, 1,247 UNCERTAIN and 205 DROP, with final 5,939 HOLD / 205 DROP. No memory-diagnostic error appears. Its exact executed helper/launcher SHA values were verified. Diagnostic-only wrappers preserve Observation objects, record active measurement time including startup/protocol but excluding queue wait, and include native descendants through verified cgroup membership. The cgroup memory peak is cumulative across cases. Whole-call time includes instrumentation overhead, so compare against the 64-worker case in that same pilot. Memory evidence requires readable counters and no membership diagnostic errors; cumulative peaks cannot be treated as independent per-case peaks. No full census is launched. [Executed instrumented helper](efficiency/throughput_native_04.py) [Bound submission](efficiency/throughput_02-submission.json)

| Workers / factor 16 | Whole-call seconds | Native p99 seconds | Cumulative cgroup peak, GB |
|---:|---:|---:|---:|
| 64 | 65.85 | 2.72 | 27.19 |
| 128 | 59.79 | 3.63 | 41.61 |
| 256 | 62.19 | 7.09 | 63.73 |

The 128-worker result is 1.101× the same instrumented 64-worker baseline; 256 workers is slower than 128 and has a larger observed cumulative memory peak. These are single-pass sample comparisons. Counts and window size both change, so attributing the difference solely to cores would overstate the experiment. [Complete instrumented receipt](efficiency/throughput_02.json)

## P5 — PASS: final fixed-worker queue selection and full configuration

Candidate `6261c3f58cc80e1bbfe70e35120aa9d9e8c388fa0dbc0a8f62f17a8d1045bf35` accepts factors 1–64 but adds a strict shared **workers × factor ≤ 4,096** limit. The pool enforces it before executor creation; the qualifier validates every planned combination before worker guard, sampling or output creation. Both factor/worker inputs retain exact integer checks. Boundary 64×64 and 256×16 configurations are accepted without launching workers; 128×64 is rejected. The factor-64 queue fixture verifies coordinator preparation, the actual bounded lookahead and original output order.

Only the pool's bounds change under `greekocr/`; native/detector/geometry/corrective and accepted-policy bytes are unchanged. I independently verified all 319 archive files, their current source equality and registry hashes. **240 pipeline/CP2/CP3/CP4c tests pass in 2.49 seconds.** No ordering or eligibility logic changes. Native qualification now passes on **job 3692980**, source 6261, with actual 256-CPU affinity. All five cases—serial/factor 2 and 64 workers with factors 2/16/32/64—measure 768 fresh rows, produce identical ordered scientific records, and have zero infrastructure/cache/unavailable/cleanup faults. This qualifies the final runtime candidate. Factor 16/32/64 times are 12.82/12.73/12.49 seconds on the small sample. A separate generation comparison preserves all 768 scientific records from the preceding source after validating the narrow source-identity/clock exclusions. The longer fixed-worker selection below is now complete. The full census is unlaunched. [Final queue qualification](efficiency/scaling_04-qualification.json)


The final instrumented pilot, **job 3692982**, uses the same 6,144 SHA-priority rows, source `6261c3f5…`, runtime, 256-CPU affinity and exact archived diagnostic helper for all three settings. Each case performs 6,144 fresh native attempts, with zero infrastructure dispositions, cache hits, invalid-cache records, unavailable observations or cleanup failures. Every case has the same ordered scientific digest and segmentation counts: **4,692 KEEP, 1,247 UNCERTAIN, 205 DROP**; final dispositions remain **5,939 HOLD and 205 DROP**. No automatic-admission claim is implied. [Final pilot receipt](efficiency/throughput_03.json) [Final generation preservation](efficiency/scaling_04-generation-parity.json)

| Fixed 64 workers | Whole-call seconds | Rows/second | Native p99 seconds | Cumulative cgroup peak, GB |
|---|---:|---:|---:|---:|
| Factor 16; 1,024 pending | 65.78 | 93.40 | 2.76 | 27.26 |
| Factor 32; 2,048 pending | 57.81 | 106.28 | 2.99 | 29.15 |
| **Factor 64; 4,096 pending** | **55.44** | **110.82** | **2.94** | **30.81** |

The selected factor 64 improves same-pilot throughput by 18.65% over factor 16 (15.72% less whole-call time); its 4.27% advantage over factor 32 is a single-pass result, not a replicated confidence interval. Native observation maximum is **16.62 seconds** in the selected case, including worker startup/protocol and excluding queue wait. All 64 native worker PIDs are verified in the task cgroup for each case, with no diagnostic errors. The memory peak is **cumulative across cases**, including native descendants, not an independent per-case peak or a bound on full-census memory.

I verified the final full-config SHA **`9d7e6c0607e96628aac40415d11201fbd97f4ade9157c4043fcd2990c0131600`** against both the binding receipt and plan. The source is `6261c3f58cc80e1bbfe70e35120aa9d9e8c388fa0dbc0a8f62f17a8d1045bf35`; all five complete parent dictionaries, corrective parent/artifact hashes and release statuses remain unchanged. Metadata `b5ff259b…` and runtime `84ed3add…` remain bound. The selected configuration is 64 workers/factor 64, 120-second per-row timeout, 256 requested task CPUs. The exact normal-partition, one-node, six-hour request passes test-only; the launch script passes shell syntax and is unexecuted. Resume retains the same immutable configuration and adds only explicit `--retry-errors`. [Final binding](full-run-config-binding.json) [Selected configuration](full-run-config.json) [Launch/resume plan](full-run-plan.json)

At the selected sample throughput, **592,466 / 110.82 rows per second = approximately 1.49 hours**. This is an arithmetic scenario, not a measured corpus ETA. The prepared **2–3-hour planning assumption** allows some overhead but is not a statistical interval; queue time is additional, and the **six-hour Slurm limit** is an allocation ceiling. Parent-balanced sample weights differ from the full corpus; dev/test rows, later geometry tails, correction work, SQLite/export growth and retries remain unmeasured at full scale. The old 12–16-hour assertion is not supported by these receipts. Further optimization is possible, but this review found no unclosed implementation blocker to the bound diagnostic census and no evidence requiring another tuning campaign before measuring its actual progress.
