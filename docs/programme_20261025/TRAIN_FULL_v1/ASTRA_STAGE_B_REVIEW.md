# ASTRA — Stage B prelaunch review

26 October 2026, Europe/Athens. Independent certifier review of the supplied 01:23 receipt snapshot. **HOLD: one HIGH finding blocks launch.** No BLOCKER-severity finding. The scientific trial configuration passes the focused checks, but the production collector incorrectly applies a single-node CPU-isolation check across the entire 13-node study.

Scope: latest RESUMEs in [TRAIN_FULL_v1_brief.md](../../ocr_program_2026-10-06/briefs/TRAIN_FULL_v1_brief.md), [STAGE_A.md](STAGE_A.md), [STAGE_B.md](STAGE_B.md), [EXECUTION_STATE.md](EXECUTION_STATE.md), sealed package, frozen search files, test evidence and [actual local receipt copies](../../../out/TRAIN_FULL_v1/receipts_stage_b/). The owner's overnight authorization is acknowledged; this review requests no new permission and launches nothing. All inspection was local and read-only. Only this report was written. No network, SSH, scheduler, training, background job or test-suite execution was performed.

## Findings

### H1 — HIGH: CPU isolation is compared across different physical nodes

**Evidence:** [stage_b.py:213](package/stage_b.py#L213) calls `isolation(p)` before collecting any result. Its `isolation()` at lines 256–272 flattens allocation records from **every group** into one list and calls `stage_a.check_isolation()`. [stage_a.py:82–91](package/stage_a.py#L82) rejects any temporally overlapping pair when either GPU UUIDs match **or CPU-affinity integer sets intersect**. CPU numbers are local to a host. [stage_b_trial.py:158–171](package/stage_b_trial.py#L158) records GPU UUID, job/restart, interval and affinity, but no physical host identity. Job IDs are not used to scope this comparison either.

**Firsthand, read-only reproduction:** I imported the sealed `check_isolation` function and passed two records with overlapping intervals `[100,200]`, distinct job IDs, distinct GPU UUIDs, distinct illustrative hostnames, and `cpu_affinity=list(range(24))` on each. The actual function returned:

```text
ValueError: overlapping GPU/CPU assignments
```

The same call with disjoint CPU sets passed. Adding hostname fields alone does not help: the current checker ignores them. This is a deterministic false rejection of valid allocation evidence, not evidence that Slurm actually shares CPUs between trials.

**Impact:** the real plan has groups `[4,4,4,4,4,4,4,4,4,4,4,4,3]`. Concurrent nodes can legitimately assign identical local CPU numbers. Production collection then fails before writing per-width `results.jsonl`; `seeds()` and `adoption()` also call this collector. The single-node smoke cannot exercise this case. The four-lane mocked collection test explicitly uses `fixture=True`, which bypasses production isolation; the B2 test mocks `collect()`.

**Required closure before launch:** attest physical node identity for every allocation, preserve it in recovery evidence, and compare CPU-affinity intersections only on the same physical host; retain global GPU-UUID collision checks and temporal overlap handling. A correctly bound per-node grouping is another possible implementation, provided it handles restarts and cross-job same-host reuse. Add coverage for simultaneous distinct hosts with reused CPU numbers, same-host CPU collisions, same-GPU collisions and recovered allocations. Reseal and refresh the affected plan/smoke/review bindings under the package's existing qualification rules. Do not merely remove isolation checks or bypass collection. No fix was made in this read-only review.

### M1 — MEDIUM: execution ledger understates recorded spend; supplied accounting is not a complete current balance

[EXECUTION_STATE.md](EXECUTION_STATE.md) estimates about 225 GPU-h remaining using historical 119 plus approximately 4–5 for today's jobs. The supplied parent accounting actually adds **49.680278 requested GPU-h** before the Stage B smoke when all recorded owner/account jobs are included: **46.130000** from other jobs and **3.550278** from `TRAIN_FULL*` jobs. Counting only the latter silently excludes most of the supplied wave activity.

The authoritative historical definition is **elapsed seconds × requested GPUs / 3600**, explicitly recorded in [S1_RESULTS.md, cumulative allocation accounting](../../programme_20261019/SIMPLIFICATION/s1/S1_RESULTS.md#cumulative-allocation-accounting) as **118.995000** spent at 22 October 13:43:45 UTC. The new capture starts on 25 October, leaving an unreconciled interval between those snapshots. The supplied smoke sacct row is one completed parent record after a forced requeue; it does not independently expose every allocation's charged interval.

The visible arithmetic still allows B/B2 reservations, so this finding is MEDIUM rather than an assertion that the cap has been exceeded. Update the operational ledger, reconcile the intervening period and requeue accounting, and perform the already prescribed accounting refresh before submission. Do not present the subtotal below as a verified live balance.

### L1 — LOW: narrative status remains pre-smoke

STAGE_B.md, EXECUTION_STATE.md and the commands' closing status still say the CUDA smoke is pending. The supplied receipt now records job **3749768 COMPLETED, exit 0:0, ElapsedRaw 241 s**, real restart and BIT_IDENTICAL. Update the status outside the sealed payload, while retaining this review's HOLD. A successful smoke does not resolve H1.

## Identities and firsthand checks

| Object | SHA256 |
|---|---|
| `package/PAYLOAD.json` | `f3944e2a242e83def0ff86a034c7f1e64bb30276a1c52ed5e291b441e162dd17` |
| Actual `study_PLAN.json` | `4813ea034d3ccaa523af316f3aa262fd4fb89dd29d86b10186269e20b9e6dfc4` |
| Actual `smoke_PLAN.json` | `9e7c6e0b07e320a304889f8e96bd901c426465c5ab2f132b98aa83d142d5e435` |
| `SMOKE_IDENTITY.json` | `556d26bfca95ed3bc04d8095fc538924d506c70ed973ca7d89002e1844ef1510` |
| Prepared runtime, bound by both plans | `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4` |
| Measured Stage A report, bound by both plans | `89ae4daaa60aebc03aae2f6bd0e88b010865883c21ba88cb5d2b676a5e5ee784` |

I ran the read-only `verify.verify()` and `verify.data_compatibility()` functions with Python bytecode writes disabled. **All 74 sealed files passed byte-count/SHA verification**, original numerical modules passed upstream verification, trainer restoration passed, and the prepared-data compatibility proof passed. This independently checks local package bytes and lineage; it does not reread remote pool files.

I regenerated the 16 points in memory using the included scrambled Halton generator, seed **20261025**, and the actual search-space file. Every parsed value matched exactly; both `hp_study1` files matched the packaged copies byte-for-byte. Trial-file copies are not in the supplied receipt folder, so I independently reconstructed the exact serialized configurations from the sealed builder and bound runtime metadata. **All 51 study config hashes/byte counts and all four smoke config hashes/byte counts match the actual plans.** Thus this review checks the configurations bound for launch, not just a narrative table.

The source-hash checks and arithmetic were executed firsthand. The recorded CUDA outcomes below are attestations in the supplied real receipt, checked against the readout implementation and local plan hashes. Remote checkpoints, individual point files, all four lanes' allocation records, raw logs and parquet bytes were not locally supplied and were not fetched. I did not independently rerun the CUDA tensor comparison or full data coverage readout.

## Scientific recipe and measurement checks

**Optimizer — PASS.** `vendor/train/train.py:125,148–149,907–917` adds `--beta1`, default **0.9**, validates `[0,1)`, and passes `betas=(args.beta1,0.999)` to the actual AdamW constructor. Undoing precisely these changes plus the pre-existing checkpoint hook reproduces the upstream trainer hash. No model, sampler or scorer numerical change was hidden in the payload. Recipe defaults preserve epsilon `1e-8`, norm/bias zero decay, gradient clip 5 and accumulation 1. `no_cycle_momentum=True` prevents OneCycle from overwriting the searched beta1.

`stage_b_trial.execute()` overlays each bound trial's LR/beta1/WD on the inherited recipe before parsing and training. Each width has the same 16 exact Halton points plus the **unscaled** S1 control `(lr=1e-4, beta1=.9, beta2=.999, wd=.05)`. No linear or square-root batch scaling is applied. All non-study callers that omit beta1 keep 0.9.

**Batches and horizons — PASS.** The plan embeds the actual Stage A selections, including measured rates **425.764882 / 368.362939 / 309.808403 lines/s**. Planning requires measured status, isolation PASS, exact runtime SHA and the adopted batch/worker choices. The local `PREPARED_NOT_MEASURED` placeholder is not accepted.

| Width | Batch | Workers | Draws per trial | Updates | Loss points |
|---|---:|---:|---:|---:|---:|
| ×1 | 256 | 6 | 1,269,164 | 4,958 | 26 |
| ×1.5 | 256 | 6 | 1,269,164 | 4,958 | 26 |
| ×2 | 64 | 6 | 1,269,164 | 19,831 | 26 |

The full target is `8 × 2 × 793,227 = 12,691,632` draws. Ten percent is 1,269,163.2, rounded upward to an even **1,269,164**, with **634,582 real + 634,582 synthetic**. This is one shortened epoch, not eight study epochs. OneCycle uses the actual packed trial update count, `pct_start=.075`, and disabled momentum cycling. The shuffled partial batch contributes its actual 172 or 44 rows; cadence is not inferred by repeating `ceil(50000/batch)`.

**Dev-only access and objective — PASS within inspected binding.** `run.install(study=True)` restricts pool loading to training components plus `seal04_dev` and `harvest_dev`, skipping other pool entries before opening/re-hashing parquet files. Its epoch diagnostic uses an in-memory `split=val` view of seal04 dev; it does not load the original validation pool. Runtime metadata still contains other pool/reference entries, but no study evaluation consumes them. The final hook receives only the two dev panel names. Completion checks require exactly those names and complete row counts.

The complete dev instruments are **437 + 16,350 = 16,787 rows**. `stage_b_trial.pooled()` sums the unchanged scorer's literal NFD-atom Levenshtein **edits**, then divides by summed **reference units**. It does not average panel CER rates or weight them by row counts. Both panels remain separately reported. The collector reads only the final evaluation; legacy `best.pt`/epoch diagnostic metadata cannot choose a study checkpoint.

**Loss and continuation — PASS on code/recorded tests and smoke, with remote evidence limitation above.** `loss_cadence.plan()` uses the same assembler and packed sampler, identifies crossings of 50,000 through 1,250,000 drawn lines, and includes final once: 26 points. Training checks actual draw counts against the plan. `full_hook.evaluate_panel(decode=False)` performs no greedy decoding and uses the training-equivalent fp32 CPU `CTCLoss(blank=0, zero_infinity=True)`; target-normalized batch means are weighted by sample count for a complete-panel mean.

The segment state commits before evaluation. Immutable point files publish before the append-only journal entry; restart reconciles missing index entries, resumes an unfinished current evaluation, and rejects missing historical points. Torn journal tails receive an explicit hash witness without truncating previous bytes. Completion requires the exact ordered step list, so duplicate/missing entries cannot silently pass. Loss and final CER hooks restore Python/NumPy/Torch/CUDA RNG and model mode in `finally`. Full segment continuation restores model, optimizer, scheduler, iterator/cursor and draw chain; completed lanes authenticate their bound files and skip on node restart.

The actual smoke receipt reports **BIT_IDENTICAL**, `mock=false`, five loss points **8/16/24/32/40**, forced yield at **step 12**, job **3749768** with restart counts **0 → 1**, matching final continuation fields, and zero test instruments opened. Its forced-yield checkpoint SHA is `51d3421a7e1fb34c01bc300ee6295723ba5fffefcb45a9b22d78516bc913a402`. The resumed lane moved between physical GPU UUIDs; the readout requires identity despite that restart. The comparison is the ×1/b256 control/twin; ×1.5/b256 and ×2/b64 complete smoke lanes but are not separate CUDA requeue twins.

**Lane execution — PASS for the single-node resource design; multi-node certification fails H1.** The wrapper requests preemptable/requeue operation and a standard-format deadline. Each srun uses exclusive/exact allocation, one GPU, 24 CPUs, core/GPU binding and six workers; runtime checks require a single visible GH200 and native thread limits. Claims/output locks prevent duplicate concurrent owners. Smoke isolation is recorded PASS. This establishes neither absence of shared storage contention nor correctness of the cross-node collector.

## Cost and cap reconciliation

I recomputed these from the actual smoke costs. They are **projections using measured Stage A throughput and measured smoke evaluation time**, not measured completed B/B2 expenditure.

| Width | B17 GPU-h | B2 three-seed GPU-h | Eval / training time |
|---|---:|---:|---:|
| ×1 | 16.236395 | 2.865246 | 15.34% |
| ×1.5 | 18.578665 | 3.278588 | 14.19% |
| ×2 | 21.842041 | 3.854478 | 12.91% |
| Total | **56.657101** | **9.998312** | All below 25% |

Per trial, the estimator uses **26 × maximum measured full-dev loss time + one measured final dev CER pass**. Startup, recurring checkpoint writes, full-horizon iterator reconstruction, extra epoch diagnostic, idle capacity in mixed-duration groups, storage contention and requeues remain outside that useful-work estimate. No subsampling is proposed or needed to meet the recorded 25% reporting threshold.

| Accounting item | Requested GPU-h |
|---|---:|
| Historical S1/wave2 spent at 22 Oct capture | 118.995000 |
| All rows in supplied pre-smoke capture: elapsed × ReqTRES GPUs | 49.680278 |
| Supplied smoke parent row: 241 seconds × 4 GPUs | 0.267778 |
| **Recorded subtotal, subject to M1 coverage gaps** | **168.943056** |
| Cap minus that subtotal | **181.056944** |
| Proposed B reservation: 51 GPUs × 2 h | 102.000000 |
| Proposed B2 reservation: 9 GPUs × 2 h | 18.000000 |
| Subtotal plus those B/B2 reservations | **288.943056** |
| With conservative exclusive-node B/B2 reservations 104 + 24 | **296.943056** |
| Headroom under that conservative visible-row calculation | **53.056944** |

The historical 119 is rounded; using it instead changes totals by 0.005 GPU-h. CPU-only requested GPUs count as zero in this particular cap, while node occupation remains distinct. The pre-smoke file's `TimelimitRaw × ReqTRES GPUs` sums to 309.333333 GPU-h, but those expired maximum reservations are **not** the authoritative historical spent measure and must not replace elapsed accounting. Conversely, the 56.657/9.998 useful-work forecasts must not replace the proposed launch reservations. Stage C is not reserved or certified here. Additional or intervening jobs and requeues must fit the reconciled remaining cap.

## Analysis and adoption — PASS as a plan, not an outcome

The supplied `analyze_study.py` checks infeasible fraction/location, parameter boundaries and bootstrap sampling density. Commands run it separately per width with `--objective val_error` and omit `--scientific`. Its generic docstring expects best-ever validation, but here the only CER measurement is final and the collector explicitly supplies final pooled dev CER. Omitting `best_step` correctly avoids pretending a checkpoint-position diagnostic exists; the registered replacement is inspection of train/dev loss curves. No LR range extension occurs automatically.

B2 creates fresh runs at model seeds **0/1/2**, preserving data seed, batch, data and short horizon. `adoption()` requires three complete reruns and a complete control, computes **gain = control-study(seed0) CER − selected-study(seed0) CER**, **spread = max(best rerun CER) − min(best rerun CER)**, and uses strictly **gain > spread**. Equality fails. All seed values/mean, boundary positions and unmeasured control/study variance are disclosed. Failure of this rule means retain the control; the emitted selected parameters are diagnostic candidate parameters, not permission to adopt them when `adoption_rule_met=false`. Stage C remains a separately reviewed package after actual B/B2 results.

## Existing tests and disposition

I parsed [TESTS_STAGE_B_FINAL.xml](evidence/TESTS_STAGE_B_FINAL.xml): **120 tests, 0 failures, 0 errors, 0 skipped**, recorded duration 50.004 s. These are prior test results, not a new run. Inspection confirms coverage for exact Halton/control values, beta1 defaults/validation, actual optimizer betas after hard-kill resume at each width, poisoned non-study pools, cadence/journal recovery, RNG-preserving evaluation, trial claims, submission binding and the seed-spread decision. That evidence does not cover the production multi-node CPU namespace failure demonstrated here.

Disposition: **do not launch the current Stage B plan**. Resolve H1, qualify the affected behavior and exact new bindings, and refresh the existing accounting ledger. M1 and L1 remain logged nonblocking findings; no additional scientific tuning condition or owner approval requirement is introduced by this review.

VERDICT: HOLD | BLOCKERS: 0 | HIGH: 1
