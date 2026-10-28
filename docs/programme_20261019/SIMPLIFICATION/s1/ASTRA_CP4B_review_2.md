# ASTRA-CP4B review 2 — S1 prelaunch certification

**PASS — B1, B2, B3 and H1 are closed under the accepted simplification standard; the unchanged eight-cell ladder is ready for launch.**

Reviewed `c9fe083` on `opus/s1-scaling`, firsthand on 22 October 2026. Actual HEAD `0070f68` adds only the review brief. Checks were read-only; no files written, jobs submitted or background jobs started.

## Findings — most severe first

1. **MEDIUM — The packet’s combined budget figures exclude subsequently completed wave-2 work.**

   [ACCOUNTING.md:15](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/ACCOUNTING.md:15) reports combined runtime/full-limit projections of **215.546771 / 316.745556 GPU-h**. Fresh parent-only `sacct` gives **245.425938 / 346.624722**, leaving only **3.375278 GPU-h** below 350 if every planned limit is consumed.

   **Failure scenario:** the older headroom permits an additional retry that the current full-limit envelope cannot accommodate.

   **Fix:** carry the refreshed totals below into the launch accounting and refresh at continuation boundaries, including outstanding work and every failed attempt. **Nonblocking:** the complete planned graph still fits; this review supplies the updated calculation.

2. **LOW — Adapter-deployment evidence remains untracked.**

   The records linked at [REVIEW_INPUTS.md:31](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/REVIEW_INPUTS.md:31), under `record/adapter_deploy_3714872/`, remain absent from the reviewed commit.

   **Failure scenario:** a clean checkout loses the deployment/readback/accounting evidence, although the operational measured-plan receipts remain available.

   **Fix:** commit the existing captured records when freezing the review packet. Live verification below establishes their deployment claims independently.

3. **LOW — Current-status prose retains superseded CP4 and cap statements.**

   [REVIEW_INPUTS.md:304](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/REVIEW_INPUTS.md:304) still says CP4 PASS is unavailable. The [programme amendment:55](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/SIMPLIFICATION/SIMPLIFICATION_AND_LAUNCH_PLAN.md:55) retains separate 120-hour series caps.

   **Failure scenario:** an operator follows obsolete requirements instead of the current launch authority.

   **Fix:** update the current-status summary to reference the completed CP4 review and **350 requested GPU-h, without separate series caps**. The implemented policy adoption already matches your explicit ruling.

## Cleared items

### B1 — Production runtime and limits

I checked all six native timing files and recomputed the three steady-window p90 values:

**0.430695123 / 0.428382904 / 0.431688694 seconds/update.**

The records describe three concurrent seeds, CUDA bf16, deterministic algorithms, CPU CTC, six workers and pinned memory. Each completed **100 initial + 20 resumed updates**. The recovered readout covers **103,528 rows per seed across ten instruments**.

Independent calculation for one three-seed cell:

| Component | Seconds |
|---|---:|
| Preparation upper bound + preflight | 2,142.055977 |
| Initial startup | 175.890160 |
| 53,616 updates × maximum p90 | 23,145.421014 |
| 537 checkpoint allowances | 862.425059 |
| Eight validation/epoch-write allowances | 165.926551 |
| Full readout allowance | 3,515.091602 |
| **Base** | **30,006.810363** |
| One restart allowance | 233.372018 |
| **Total** | **30,240.182381** |

This gives **25.200151984 requested GPU-h per cell**. The first segment supplies `43,200 / 1.5 = 28,800` estimated seconds; rounding the remaining work plus restart with the same margin gives:

`ceil((30,006.810363 − 28,800 + 233.372018) × 1.5 / 60) = 37 minutes`.

Thus **720 + 37 minutes** is reproduced exactly. Recomputed `LIMITS`, `SEGMENT_PLAN` and the launch graph match. See [derivation:87](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/bench/s1_runtime_qualification.py:87).

The **2,099-second preparation allowance is a whole-acceptance upper bound**, not a recovered preparation measurement. Bounded timing does not establish long-duration filesystem behaviour; that accepted limitation does not reopen B1.

### B2 — Cumulative accounting

Fresh `sacct -X`, captured **22 October, 02:39 UTC**, contains:

- **39 S1 parents:** 18 completed, 19 failed, one timeout and one cancelled.
- **17 wave-2 parents:** all terminal.
- No active allocations in either selected scope.

Requested cost is `ElapsedRaw × requested GPUs / 3600`; steps are excluded.

| Scope | Requested GPU-h | Allocated GPU-h |
|---|---:|---:|
| S1 actual, including all retained failures | 5.268889 | 32.731111 |
| Wave-2 actual, including retries | 36.672500 | 69.255556 |
| **Combined actual** | **41.941389** | **101.986667** |

| Remaining/projection | Runtime basis | Full-limit basis |
|---|---:|---:|
| Eight cells | 201.601216 | 302.800000 |
| Aggregate allowance | 1.883333 | 1.883333 |
| S1 actual + remaining work | 208.753438 | 309.952222 |
| **Combined wave-2 + S1** | **245.425938** | **346.624722** |
| **Headroom below 350** | **104.574062** | **3.375278** |

Series A/B runtime estimates are **151.200912 / 50.400304 GPU-h**. Neither has a separate cap under the current ruling.

### H1 — RNG continuity and split evidence

The fix at [s1_segment.py:79](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/train/s1_segment.py:79) restores saved RNG after reconstructing an existing iterator; a checkpoint before the next iterator preserves that iterator’s fresh RNG consumption.

I independently reproduced byte-equal CPU RNG at both boundaries using a real, zero-worker DataLoader in memory. Reintroducing the unconditional restore fails the epoch-boundary comparison.

The eight H1-bound files match their hashes. The recorded [six-worker test:19](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/tests/test_s1_epoch_boundary.py:19) uses the real DataLoader with persistence/prefetch and compares model, optimizer, scheduler and RNG state, including CPU RNG bytes. Its saved results show both boundary cases passing and the old implementation failing the boundary case.

For the **live acceptance split**, I independently checked:

- Identical four-update trajectories and **256 draws**.
- **526/526 tensor-storage entries byte-identical** between final checkpoints.
- CPU RNG storage: **5,056 identical bytes**, SHA-256  
  `1aa572e9a7233ab259fa4e666a4fe2e1128d3eb4a2915036d351da3be137a833`.

The full native six-worker trainer boundary test remains skipped. This is the explicitly accepted compositional standard, not a claim that that missing case ran.

### Deployment, namespace and recovery gate

Live operational manifest:

`95b361468a695a578dc5ece75dd125500bc742d1473c66ff580428edd733fd07`

All **38 payload files** match both their deployed hashes and the corresponding `c9fe083` Git blobs. Their source record binds `8916f97`. The **699-entry base manifest** has no unexpected mismatches outside the declared overlay. I also checked **62 evidence bindings**, with zero mismatches.

All **16 cell wrappers**, including six A continuations and two B continuations, match the measured generator. [s1_common.sh:7](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/scripts/clariden/s1_common.sh:7) enters the shared namespace before the gate. [s1_production.sh:23](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/scripts/clariden/s1_production.sh:23) places `srun` outside `bwrap`; training executes directly inside that namespace, preserving the capstor mapping.

I reran the actual saved **FAIL acceptance + recovered readout** composition through `check_smoke_runtime()`: **RECOVERED**. The original acceptance remains byte-identical and **FAIL**. Missing original acceptance, smoke, split or timing receipts all fail; altered hashes also fail. This local exercise retained mocked source/factory/large-artifact boundaries, checked separately through live hashes and the deployed adapter receipt. See [recovery validator:98](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/scripts/ops/s1_acceptance.py:98).

All three measured-plan receipts are committed. The eight smoke completions report four updates, and all 16 panel scores retain complete **437 dev / 2,253 test** coverage.

### Preregistration, exposure and B3

The retained geometry is:

- ×1 and ×1.5 × `{ref_208k, ref_364871, tgt_208k}` × three seeds.
- ×2 × `{ref_208k, ref_364871}` × three seeds.
- **Eight cells / 24 runs**, from scratch.

I rehashed and recounted all three subsets against seal04 suite  
`9447f09c6073028c1085996e1663232a18ac70ef8b81eda4be5c232a4025b924`.

| Subset | Rows / unique keys | Seal04 key / crop / edition hits |
|---|---:|---:|
| ref_208k | 208,000 / 208,000 | 0 / 0 / 0 |
| ref_364871 | 364,871 / 364,871 | 0 / 0 / 0 |
| tgt_208k | 208,000 / 208,000 | 0 / 0 / 0 |

`ref_208k` is an **exact prefix** of `ref_364871`; targeted rows outside the universe: **zero**. Original iopsstor subset hashes match the capstor copies.

The control is **not identical to wave-2 ctrl**, and that is disclosed at [PREREGISTRATION.md:8](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/PREREGISTRATION.md:8). Population, encoding/component policy, width and execution differences are enumerated in [PARITY.md:3](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/PARITY.md:3), including deterministic CPU CTC.

The supplied [CP4 results review](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/SIMPLIFICATION/wave2/ASTRA_CP4_results_review.md:1) is **PASS**. Its SHA-256 is:

`53385d320112f9f3a2c3fbcbed34d60d37ee16f3f83d9d3e9e6ca052356ec140`

B3 is closed.

## Decision for the owner

**Run the ladder unchanged.** CP4 shows a useful trade-off: substantial improvement on the new-source diagnostic panel alongside a small legacy-test regression. It leaves capacity, available data size and balancing as meaningful questions. S1 tests those questions with controlled within-ladder comparisons. Keep the scope explicit: S1 uses the preregistered **v3/census05 population of 364,871**, whereas CP4’s v4 add population was **364,173**; S1 is not an exact rerun of v4 H7 with wider models. Report legacy instruments alongside seal04, retain `diagnostic_only`, and do not turn this single sub-doubling into a data-floor claim. No redesign is required before spending the forecast budget.

## Exact launch order and run watch

1. **Bind the launch environment and refreshed accounting.** Use the physical capstor package, the operational manifest above, recovered `QUALIFIED.json` and `ACCEPTANCE_COMPOSITION.json`. Reuse the accepted preparation; no separate preflight allocation is required.
2. **Series A:** release the six first segments for ×1/×1.5 and all three subsets, each **12 hours / three GPUs**.
3. **Each A continuation:** refresh accounting at its boundary and run its own `_seg2`, **37 minutes / three GPUs**, with `afterany:<own segment-1 ID>`. It remains part of the graph even when segment 1 succeeds.
4. **Series B:** both ×2 reference first segments require `afterok` on **all six A continuation IDs**. Then each B `_seg2` uses `afterany` on its own first segment, with refreshed accounting.
5. **Aggregate:** **113 minutes / one GPU**, `afterok` on **all eight continuation IDs**.

This is the verified **17-node graph**. Continuations reuse the same cell directory and require all three `segment.pt` files; invalid recovery state is rejected. See [graph construction:44](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/scripts/ops/s1_segment_plan.py:44).

Watch:

- Progress against measured throughput, particularly preparation/I/O stalls and readout tails.
- Atomic checkpoints every 100 updates, cursor continuity, TERM/deadline handling and expected yield exit **75**.
- Actual requested GPU-hours plus outstanding commitments before retries; **3.375 GPU-h is the current full-limit cushion**.
- All 24 runs reaching **eight epochs / 53,616 updates**, complete instrument coverage and valid `CELL_COMPLETE` receipts. Early stopping or partial scoring must not become a completed scientific result.
- Legacy-test regressions alongside benchmark gains, with all preregistered panels and classes retained.

VERDICT: PASS — launch the unchanged eight-cell ladder with refreshed shared accounting and the reviewed continuation graph | BLOCKERS: 0 | HIGH: 0