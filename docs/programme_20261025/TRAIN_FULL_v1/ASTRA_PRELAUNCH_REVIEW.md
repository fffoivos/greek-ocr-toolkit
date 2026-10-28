# ASTRA — TRAIN_FULL_v1 Gennadius prelaunch review, 25 October 2026

**PASS — the reviewed package and retained Clariden receipts support the specified launch; no BLOCKER or HIGH finding.**

## Findings

### F1 [MEDIUM] Inherited LR/batch remain an untested optimization choice

**Path/number:** [package/recipe.json](package/recipe.json), lines 10–12: batch **64**, maximum LR **0.0001**; [PLAN.md](PLAN.md), recipe table; the certifier brief's methodological point 6.

**Failure scenario:** preserving the O5-derived S1 settings does not establish that they are efficient for from-scratch width ×2 training over this larger population and longer OneCycle. The run could undertrain within its fixed budget. The four-update smoke establishes execution/continuation, not convergence. This is an inherited scientific limitation, not an undisclosed change or a defect requiring this launch to stop.

**Fix:** address the question in the coordinator's proposed separate LR screen, with its own recipe/results record and development-only selection. Keep this run's certified recipe fixed; do not use its checkpoint test metrics to tune or extend it.

### F2 [LOW] The 24.9000867-hour forecast omits planned continuation startup

**Path/number:** [package/readout.py](package/readout.py), lines 14 and 25–36; [OWNER_READOUT.json](../../../out/TRAIN_FULL_v1/receipts_005/OWNER_READOUT.json), `forecasts[0]`; [evidence/QUALIFIED.json](evidence/QUALIFIED.json), `restart_bound_seconds`.

**Raw discrepancy:** the reported **24.900086725682517 GPU-h** is arithmetically correct for its formula, but that formula includes one startup and **zero planned restarts**, although it requires **three 12-hour segments**. Two historical restart allowances add `2 × 233.372017674963 / 3600 =` **0.129651120930535 h**, yielding **25.029737846613052 h** under the same timing assumptions. This is still a projection: the smoke used only **128 mixed draws/epoch**, not **1,586,454**, so it did not time production-scale epoch construction or mid-epoch cursor replay. The reported full-evaluation allowance is **124.91356276196893 s**.

**Failure scenario:** treating 24.9 hours as the entire chain's measured runtime understates startup/replay costs. New width distribution and preemptions can change the estimate further. There is ample space within the proposed three-segment reservation; this discrepancy does not invalidate the horizon or segment plan.

**Fix:** annotate the operational estimate with planned restarts and replace historical throughput/startup assumptions with measurements from this run when available. Retain the distinction between useful runtime, **36 GPU-h** of three segment reservations, queue delay, and additional preemptions. A reporting correction can live outside the frozen payload.

### F3 [LOW] The narrative handoff still presents completed gates as pending

**Path/number:** [PLAN.md](PLAN.md), opening/closing status and historical population/recipe tables; [COMMANDS.md](../../../out/TRAIN_FULL_v1/COMMANDS.md), opening status and section 5 nominal projection.

**Raw discrepancy:** the files still contain “pending real prepare, CUDA smoke” and the nominal **782,151 train / 195,544 updates**, while the bound receipts establish **793,227 train / 198,312 updates**, prepare **3748345 COMPLETED**, and two completed real smoke parents. The nominal/current difference is **11,076 train rows / 2,768 updates**. Historical sections are labelled, and runtime startup recomputes the horizon, so these stale statements do not silently configure the training run.

**Failure scenario:** a reader can confuse historical preparation instructions or nominal estimates with the completed 005-Gennadius state.

**Fix:** add a concise current-state entry linking this review and `receipts_005`, with the exact hashes, counts, completed jobs and launch command. Preserve the historical attempts. Do not regenerate or change the certified payload for this documentation correction.

## Verified-good

### Scope and exact binding

I read the owner brief and all four RESUMEs, the recipe/PLAN/commands, the adapter, evaluator, scheduler and continuation sources, relevant frozen S1 sources, the tests and their retained results, and the local 005 receipts. All checks were local. No network, SSH, allocation, training process, background process or dataset transformation was run. This report is the only file written.

| Bound object | SHA256 |
|---|---|
| `package/PAYLOAD.json` | `294c3458c0d1fbbb45c61dcac2e11e8fab92f1ce10558cf9576ecccaabd30aac` |
| `receipts_005/data_prepared_runtime.json` | `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4` |
| `receipts_005/SMOKE_IDENTITY.json` | `19db742de50994112da04a893b6fb331f2f2daf09a8a120c21ad10b084243175` |
| `receipts_005/data_manifest_AUDIT.json` | `4fa31b81b301d510c586e037249104e2f905075da43c1d2b6b840275b6006ab3` |
| `receipts_005/OWNER_READOUT.json` | `d4a30705e72cdcd8af87fd66a74ccd450085730e15a8b78fd3733ab8e025ddee` |

I recomputed the local payload seal and verified all **50** listed files. The audit-completion → audit/reuse, preparation-completion → runtime/package, and owner-readout → runtime byte/hash links match. The runtime is **11,485,347 bytes**, `mock=false`, and binds this package. The successful audit is explicitly inherited from **3748169**, not represented as a new scan. I reran the read-only compatibility check: **46 unchanged parent files**, only **prepare.py** changed, and exactly the three declared additions. The parent payload is `e3a023657d27bae8ec219afe25289ba7a14fdaee2af35b510131a028efa5079b`.

### Recipe comparison

The original seed-0 completion has **24 explicit parameters**. **20** match the new recipe literally; the remaining four are the declared `mix`, `codec`, `val_mix` bindings and `epoch_rows`. The adapter supplies the first three, preserving codec bytes and the S1 selection-validation pool. It resolves `epoch_rows` from the audited count before training.

| Unchanged parameters | Verified values |
|---|---|
| `transfer_mix`, `selection_metric`, `transfer_final_only` | `null`, `val_cer`, `true` |
| `arch`, `head`, `width_mult` | `compact`, `nfd`, `2.0` |
| `epochs`, `bs`, `accum`, `seed` | `8`, `64`, `1`, `0` |
| `lr`, `wd`, `no_decay_norm_bias`, `no_cycle_momentum` | `0.0001`, `0.05`, `true`, `true` |
| `workers`, `pin_memory`, `device` | `6`, `true`, `cuda` |
| `pack_bucket_tails`, `repeat_to_epoch_rows`, `segment` | `true`, `true`, `true` |

All **14 upstream source/codec hashes** also match the available original S1 checkout. Restoring the single declared trainer condition reproduces original trainer SHA `dd0652856e2c46acb63d7b139566f2849fbcbb6afd81b66fda771b80457482f2`. The four scorer files match their binding. Model, AdamW defaults, norm/bias decay exclusion, gradient clipping **5.0**, OneCycle `pct_start=0.075`, disabled cycle momentum, bf16 forward, fp32 CPU CTC, sampler and preprocessing code remain bound to S1.

The scientific changes are the specified population, epoch/horizon/OneCycle length, checkpoint/evaluation cadence, disabled patience, and restoration of nonletter import handling. `PATIENCE=epochs+1` is **9** for production, so validation cannot truncate eight epochs. The table also explicitly discloses the necessary partition/GPU/CPU/thread-environment changes; they are not silent numerical recipe changes. Removing the accidental aggregate import-audit gate restores the earlier report-only policy while retaining exact coverage checks.

### Population, exclusions and mixture — recomputed from the receipt tables

| Population | Before train/eval crop exclusion | Retained rows | Unique dataset crops |
|---|---:|---:|---:|
| v4 train | 364,871 | 364,870 | 364,870 |
| Harvest train, including Gennadius | 428,359 | 428,357 | 428,357 |
| Harvest dev | 16,350 | 16,350 | 16,350 |
| Harvest test | 52,847 | 52,847 | 52,846 |
| **Dataset total** | **862,427** | **862,424** | **862,423** |

The external seal04 panels add **437 dev + 2,253 test = 2,690 rows**, giving the audit's **865,117 input / 865,114 retained / 865,112 unique crops** when included. The two recorded eval-crop repeats comprise one within the dataset test population and one additional repeat when the external panels are included; all eval rows survive. **52,846 is the unique harvest-test crop count; the evaluation denominator is 52,847 rows.**

The three exclusions are **one v4 train + two harvest train**. Therefore `364,870 + 428,357 =` **793,227** unique real train rows. Train-duplicate removals beyond these exclusions: **0**. Registry/crop/line collision count after the prescribed policy: **0**. S1 assignment resolution is **364,871 / 364,871**, with **0** unresolved/mismatched rows; resolution precedes exclusion. Source and primary-class comparison tables each independently sum to **364,871 S1 / 793,227 full train**, delta **428,356**. Gennadius contributes **11,079 train + 619 test = 11,698 rows**.

Retained harvest totals `428,357 + 16,350 + 52,847 =` **497,554**. Successful preparation's coverage checks require the same complete ID set/count and an empty drop ledger before publishing runtime; its pool counts reconcile to **497,554 / 497,554**, with **0 permitted import drops**. The raw factory build-info file remains remote, bound by SHA `802912b670b71888319f087dabad20e0e162448a46ee4f103d27a6ac4bde9fbc`; I did not independently reread that 133,031,491-byte file.

Nonletter metadata in the actual runtime: S1 **13,767 `furniture`** rows; harvest **24,889 train + 1,823 dev + 3,392 test = 30,104**. The adapter applies the frozen tagger's no-script fallback, not a blanket `numerics_tables` remapping. Historical `export.py` calls the adapter that uses `cls or 'furniture'`; the frozen importer accepts that class. Existing v4 tensors are reused. `audit_ok=false` is explicitly report-only; coverage/custody failures still refuse preparation.

I inspected registry joins, source/edition/book/line conflict checks and eval-wins crop exclusion in `manifest.py`, then independently exercised the pure functions in memory: train/eval shared crops removed the train row while retaining both eval observations; contradictory book/edition, cross-split line and cross-split provider examples were all refused. These checks are real code paths, not assertions inferred from the word PASS. The complete crop scan itself is evidenced by the retained remote audit, not rerun locally.

The frozen largest-remainder calculation gives, per epoch:

| Pool | Fraction of all draws | Draws |
|---|---:|---:|
| Non-parliament real | 0.46391260005017476 | 735,976 |
| Parliament real | 0.03608739994982521 | 57,251 |
| Synthetic | 0.5 | 793,227 |

Parliament is **7.217479989965042% of real draws**, below the unchanged **25%** cap. Synthetic support is **190,486** frozen rows sampled cyclically for **793,227 draws/epoch**; half synthetic describes draws, not unique synthetic rows. The synthetic build-info SHA remains `e81aa95bdc32113b398f16ebe9741782fc875a50eb3de6b75522b8183f258271`. Production provenance verifies each real pool index occurs exactly once each epoch.

### Horizon and evaluation

Recomputed: `2 × 793,227 =` **1,586,454 mixed draws/epoch**; **24,788 full batches + one 22-row batch = 24,789 updates/epoch**; `8 × 24,789 =` **198,312 updates**. Total draws: **12,691,632**, split into **6,345,816 real + 6,345,816 synthetic**. Audit, runtime and independently called horizon/quota functions agree exactly.

Archives/evaluations are **50,000 / 100,000 / 150,000 / 198,312**. These fall at epoch/batch **3/422, 5/844, 7/1,266, 8/24,789**. The final archive waits for the completed-epoch state. OneCycle is initialized over **198,312**, not extended from the original **53,616**. The S1-literal alternative stays **53,616**; the 12-pass alternative is **297,468**.

`full_hook.py` uses the training-equivalent **fp32 CPU CTCLoss(blank=0, zero_infinity=True, reduction=mean)** and weights batch means by their row counts. Targets come from the stored codec IDs. CER uses the frozen literal-NFD scorer and literal panel references. Every checkpoint evaluates **437 / 2,253 / 16,350 / 52,847** rows separately: **71,887** rows across four instruments, **16 instrument records** over the run.

The evaluator runs under `no_grad()` and `model.eval()`, restoring Python/NumPy/Torch/CUDA RNG and model mode in `finally`. The compact model's BatchNorm consequently does not update running statistics during evaluation. The four-panel results never feed optimizer, scheduler, `best` or patience. Best-checkpoint selection remains the original **13,088-row shared validation CER**; checkpoint panel metrics are report-only. Incomplete evaluation cannot publish its final log. Restart completes a pending checkpoint evaluation before the next training iterator. Existing seal04 `diagnostic_only` limitations remain; this review does not establish independent human-gold or canonical-work generalization.

### Real scheduler requeue and continuation evidence

| Parent job | Retained accounting | ElapsedRaw | Restarts |
|---|---|---:|---:|
| Audit 3748169 | COMPLETED, 0:0 | 1,036 s | Not supplied |
| Failed old prepare 3748213 | FAILED, 1:0 | 1,900 s | Not supplied |
| Successful prepare 3748345 | COMPLETED, 0:0 | 2,113 s (35m13s) | Not supplied |
| Smoke control 3748974 | COMPLETED, 0:0 | 428 s | 0 |
| Smoke requeue 3748976 | COMPLETED, 0:0 | 293 s | 1 |

The appended 3748976 log contains two verified-package startups separated by the trainer's durable step-2 yield and `srun` exit **75**. The wrapper's corresponding branch invokes `scontrol requeue "$SLURM_JOB_ID"`. The identity receipt contains allocations **3748976/0** and **3748976/1**, both bound to the same final runtime. This is a scheduler requeue of the same job, not two mocked invocations. **293 s** is reproduced as the accounting field supplied; I do not assume it sums both allocations' wall times.

Both logs show **14,832,010 model parameters**, CUDA, **2 batches/epoch**, four total updates and matching printed results: epoch-1 train loss **17.2428**, val CER **0.8756**; epoch-2 train loss **11.1376**, val CER **0.8821**. Rounded log equality alone is not the identity proof. `compare.py` checks state digests across **14 scientific fields**: model, optimizer, scheduler, all RNG state, epoch, batch cursor, iterator-created flag, global step, best, bad epochs, CTC health, loss/draw trace, draw chain and draw position; it also compares all four instrument metrics at steps **2 and 4**. The real receipt reports **BIT_IDENTICAL**, `mock=false`, and this package/runtime binding. It requires CUDA / width2 / six workers and rejects mock completions.

The real forced split is after the last training batch of epoch 1 but before epoch bookkeeping. It exercises that transition; production checkpoints are mostly mid-epoch. The retained local tests additionally cover mid-epoch and last-batch SIGKILL recovery with the real S1 loop and a disclosed toy model. The continuation implementation saves model/optimizer/scheduler/RNG/cursor, verifies batch-plan identity, replays skipped loader batches without model updates, restores saved RNG, and rolls ancillary epoch artifacts back to the atomic checkpoint. No defect in those paths was found.

Evidence boundary: local 005 custody contains the comparison receipt, submission records, logs and sacct outputs, not the remote model checkpoints, COMPLETE/eval JSONs or full traces. Thus BIT_IDENTICAL and individual instrument metrics are verified here through the real comparison code and its bound receipt; I did not independently recompute tensor equality or the remote CTC/CER values. This is not described as a fresh local CUDA test.

### Launch, accounting and checks performed

`job.sbatch` requests **a0140 / preemptable / 1 node / 1 GPU / 24 CPUs / 12 hours / --requeue**, with an exclusive node. The driver uses **80 minutes** for each smoke. Production deadline handling requests a durable yield before timeout. Each segment is below **24 hours**. The driver verifies the exact package, performs `sbatch --test-only` with the same submission options, requires the review's exact package/runtime/smoke binding and `--owner-go`, and prevents blind resubmission after an existing intent.

I directly exercised dependency decisions in memory: **COMPLETED/0:0 → no dependency**, **RUNNING → afterok**, **FAILED/1:0 → refusal**. A completed predecessor also needs its bound yield checkpoint; no `afterok` on the already completed audit/prepare is used. Chaining remains a coordinator action; one invocation does not automatically submit all three segments. Completion requires the final horizon and all four checkpoint logs, not just a successful parent exit.

All three forecast formulas recompute with **0.0-hour discrepancy** from their recorded assumptions: full **24.900086725682517**, literal **6.834157663101246**, longer **37.32547784324292**. F2 records the omitted continuation allowance. **118.995 / 350 requested GPU-h**, remaining **231.005**, is explicitly the historical 22 October snapshot, not a live balance. Three 12-hour requests plus the two 80-minute smokes total **38.666666666666664 reserved GPU-h**. Exclusive-node capacity can be four times the requested-GPU measure. No live budget or queue availability was checked or inferred.

Fresh read-only checks: all 50 payload files; original S1 hashes and declared trainer patch; scorer pins; receipt hash/byte links; audit-reuse compatibility; table/source/class totals; mixture quotas; horizon/checkpoint arithmetic; forecast arithmetic; in-memory leakage/exclusion/dependency probes; AST parsing of **38 Python files**; shell syntax for the training wrapper/runtime environment. Retained latest test XML records **68 tests, 0 failures, 0 errors, 0 skipped, 13.735 s**. I inspected those tests/results but did not rerun their file-writing or process-spawning harness under this read-only assignment.

This PASS applies only to the package/runtime/smoke hashes above and the eight-pass Gennadius recipe. No launch was performed by the certifier.

VERDICT: PASS | BLOCKERS: 0 | HIGH: 0
