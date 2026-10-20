# Filtering execution efficiency — 2026-10-18

The initial 16-worker choice was a qualified improvement over serial execution, not a demonstrated optimum for a Clariden node. The earlier 12–16-hour estimate extrapolated a small, tail-sensitive batch and is withdrawn as a firm planning range. The full census and training remain unlaunched.

This iteration changes bounded scheduling and handles one witnessed missing-context condition. The owner-accepted segmentation policy remains 0.5; no detector, font fit, allowance, threshold or corrective decision is retuned. The census runtime is 0.4.

The separate native profile spends 49.18 of 56.68 profiled seconds in source-context `process_page`, versus approximately 1.54 seconds loading images. One row takes 11.12 seconds. This supports addressing work starvation behind slow rows before optimizing image decoding. Profiling overhead and non-additive coordinator thread counters prevent using these numbers as an exact production throughput forecast. [Function profile](native.json) · [Per-row profile](profile.json)

The fresh 192-row queue experiment preserves every scientific field across seven cases, excluding only run identity and the orientation elapsed clock. Every case measures all 192 rows without cache reuse or infrastructure/unavailable/cleanup faults. At 16 workers, increasing queue lookahead from 32 to 128 pending observations reduces whole-call wall time from 13.17 to 8.85 seconds, a further 1.49× measured speedup. The 32/64-worker cases plateau near 8.84 seconds on this small sample. [Queue qualification](queue_01-qualification.json)

The wider 768-row serial probe exposed an empty-support polynomial refit in the existing oblique-rule context detector. The new adapter recognizes only the exact TypeError, message and actual `_direct_rules` code frame, records unavailable context and lets the unchanged policy exclude uncertainty. It does not substitute a fit or suppress unrelated errors. All 767 previously measurable full scientific records are preserved after explicitly validated source-generation fingerprint exclusions. The witness is now UNCERTAIN/HOLD with the exact context-unavailable diagnostic; no replacement fit is fabricated. [Preservation receipt](repair-preservation.json) [Original failure](scaling-failure.json) · [Native trace](empty_fit_probe.log)

Source `f9e06adc1e43b24b1760935c45cefff70abc5a481b3411fae8df6ab64af94870` passed the same 768-row qualification at 1/16/32/64 workers, factors 2/8/16, with 64 requested task CPUs. All ten cases make 768 fresh native attempts with identical ordered scientific results, zero cache hits, unavailable measurements, infrastructure errors or cleanup faults: 601 KEEP, 139 UNCERTAIN and 28 DROP. These are segmentation verdicts, not training admissions. [768-row qualification](scaling_02-qualification.json) [Submission](scaling_02-submission.json) · [Independent Astra review](../ASTRA_CSCS_PERFORMANCE_REVIEW_20261018.md)

The timing boundary includes the census invocation, inventory registration, validation, filtering and exports. Slurm queue/startup, environment installation and shared sample selection are outside the comparison. A stratified row sample is useful execution evidence but does not prove corpus-wide retention, correction coverage, tail behavior or duration.

The 768-row sweep measures the following whole-call times. The fastest case is 32 workers with factor 16: 11.36 seconds, 12.88× the successful serial baseline and 2.58× the prior 16-worker/factor-2 setting on the same sample. The small 32/64-worker difference is not an established scaling optimum.

| Workers | Queue factor | Seconds |
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

A separate bounded 6,144-row stream (2,048 SHA-priority rows per parent) compares 32/64 workers with factor 16. It reuses the qualified immutable pipeline, fresh ledgers and the same strict scientific comparison; it makes no new serial-speedup or accuracy claim. The exact executed helper is [throughput_native_01.py](throughput_native_01.py), bound by its submission hash. Additional generic-input guards were subsequently added to the future helper, without modifying staged bytes. Actual pilot base configs were checked against the qualifier’s bound ledgers and differ only in worker/queue settings. [Submission](throughput_01-submission.json) · [Input validation](throughput_01-base-config-validation.json)

The first longer pilot passed exact ordered scientific equality on all 6,144 rows: 32 workers/factor 16 took 81.05 seconds (75.80 rows/s), and 64 workers/factor 16 took 63.00 seconds (97.53 rows/s). Each case had zero cache, unavailable, infrastructure and cleanup faults. Segmentation was 4,692 KEEP, 1,247 UNCERTAIN and 205 DROP; these are not training-admission counts. [Longer pilot](throughput_01.json)

A source-only capacity extension (cap64→256; detector/policy/native code unchanged) is pinned to `786f64d7712f0717b2d5ab7fadde9775fa00fd866163f737618eb119b67132d1`. The new 768-row sweep passes seven fresh serial/64/128/256-worker cases, and its serial scientific outputs exactly preserve the previously qualified generation after validated source-fingerprint exclusions. Actual task affinity is 256 CPUs. [Node-scale qualification](scaling_03-qualification.json) · [Source-generation preservation](scaling_03-generation-parity.json)

The second longer pilot compares 64/128/256 workers on the same 6,144-row SHA sample. Its diagnostic wrapper records active native-request latency (including startup/protocol but excluding queue wait) and Linux memory-cgroup peaks including descendants. Peak counters are cumulative across cases, not isolated per-case maxima; child PID cgroup membership is checked. Compare speed against this instrumented pilot’s own64-worker baseline because the diagnostics add overhead. The immutable executed helper is [throughput_native_04.py](throughput_native_04.py). Two earlier queued helper versions were cancelled before starting; their receipts remain in this directory. [Final submission](throughput_02-submission.json)

The instrumented node comparison passed all three 6,144-row cases with exact ordered scientific equality and zero native/cache/infrastructure/cleanup faults.

| Workers | Pending window | Whole-call seconds | Cumulative cgroup peak (GB) | Native p99 / max (s) |
|---:|---:|---:|---:|---:|
| 64 | 1024 | 65.85 | 27.19 | 2.72 / 15.75 |
| 128 | 2048 | 59.79 | 41.61 | 3.63 / 16.16 |
| 256 | 4096 | 62.19 | 63.73 | 7.09 / 16.75 |

All 64/128/256 native-worker PIDs were verified in the payload memory cgroup, with no diagnostic errors. Cumulative peaks include descendants and prior cases; they are not isolated RSS maxima. The observed maximum native request of 16.75 s is sample evidence, not an unseen-corpus upper bound. The120s hard native deadline is unchanged. [Instrumented node pilot](throughput_02.json)

The factor 16 worker sweep also changes total lookahead (1024/2048/4096 observations), so its modest128-worker advantage cannot be attributed purely to CPU count. A final candidate permits factors up to64 while retaining the **same global 4096-observation maximum**; pool and qualification planner reject oversized products before startup. The controlled comparison holds64workers and 256CPU affinity fixed while measuring factors 16/32/64. Native/detector/policy code remains unchanged. [Final queue candidate submission](scaling_04-submission.json) · [Longer controlled comparison](throughput_03-submission.json)

Final controlled64-worker pilot passed all three6,144-row cases with exact scientific equality and zero faults. Factor16/32/64 took 65.78/57.81/55.44 seconds respectively. Select 64workers/factor 64, with 256CPU affinity and the unchanged global 4096 pending bound. The cumulative whole-payload cgroup peak reached30.81 GB; all 64 native PIDs were verified. Nominal592,466-row arithmetic is1.49 hours, with a2–3 hour planning range plus queue time, not a measured population duration. [Final pilot](throughput_03.json) · [Selected deployment](../full-run-plan.json)

The full-data config was rebound to6261 source while preserving all frozen parents and corrective artifact hashes. Original-crop metadata and native-runtime hashes were revalidated. The exact normal-partition six-hour-limit command passed test-only; it has not been submitted. Canonical memory-accounting follow-up:[issue159](https://github.com/fffoivos/apertus-cscs-efficiency/issues/159), filed under [optimize-apertus-cscs](/Users/foivoskarounos-zamparloukos/.codex/skills/optimize-apertus-cscs/SKILL.md); canonical code is unchanged.
