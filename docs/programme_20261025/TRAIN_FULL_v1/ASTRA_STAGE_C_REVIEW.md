# ASTRA — Stage C prelaunch certification

Review performed 27 October 2026, Europe/Athens, against the 26 October assignment and the latest owner decisions. **HOLD: 0 BLOCKER, 1 HIGH.** Stage C silently changes the inherited Stage B checkpoint-selection pool from seal04 dev (437 rows) to the legacy S1 validation mixture (13,088 rows). This is confirmed by both the executable path and all six real smoke logs; the Stage C documentation says the opposite. H1 below must close before launch.

The owner skipped B2, renewed spending after the 437.63/350 GPU-hour disclosure, and subsequently approved **“82 GPU-h, all three.”** Those decisions stand. Neither the skipped seed reruns nor the superseded 350-hour cap is a launch finding. This review performs no launch, network access, SSH, background work, training, or test execution. Only this report is written. Verification consists of source inspection, lightweight read-only checks, SHA recomputation, receipt/journal comparisons, and arithmetic recomputation. Recorded test execution and remote binary validation are identified separately from firsthand checks.

**Bindings and custody**

| Object | SHA256 / result |
|---|---|
| Current `stage_c_package/PAYLOAD.json` | `c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b` |
| Smoke PLAN | `4e7d3e50fd7f53b3caae2b4b8fad766e2f81c8ddcbe1c9695802d41c182b0e4e` |
| Full PLAN, independently reconstructed | `83ab4a4dbb78b0964965ee1ef2299154f697242a373935b77b5279e38c77d34e` |
| Prepared005 runtime, local byte-verified copy | `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4` |
| Fresh `SMOKE_IDENTITY.json` | `3fa23e49be2988943cc7b5da8624400106b34109f1a7866f327267eb0882227d` |
| `MEASURED_FORECAST.json` | `b18a10d5119889e6da6d2d462d06e3ab8b2f013f167a5596d7d64bb6a12ddaba` |
| `SMOKE_SACCT_ALL.txt` | `0875f1ebfea3cca26a6ca5e7804842a84cf68ff69e593a15e6773a00d88a0edd` |
| `SMOKE_MEMORY.txt` | `83863108ca5f7e8e0758be94e292f19f0798ce52b87b5832b2bea8dd1818674c` |

All **88 sealed files** match their recorded size and SHA; no extra files were present in the package. All package Python files parse and all sbatch files pass `bash -n`. The data-compatibility proof was executed read-only and exactly matches its receipt. Against Stage B, the only changed existing payload files are `full_hook.py` and `loss_journal.py`; the Stage C additions carry the driver and operational changes. Against the immediately preceding 515b7d86 seal, the four changes and two additions exactly match [STAGE_C_50K_RECEIPT.json](evidence/STAGE_C_50K_RECEIPT.json). Neither superseded C seal certifies this one.

The full PLAN/config files were not included in the smoke packet. I reconstructed their canonical bytes in memory from the byte-verified runtime, adopted inputs, smoke bindings, and `make_run`/`build` logic for `full-v1-012-stage-c-50k/full`. The resulting 1,956-byte PLAN has the coordinator-reported `83ab4a4d…` prefix. Its config SHAs are ×1 `ba5cea042c432c576058ddf5df3dc234a4d2458e3e6bf050c780526d531ed9e3`, ×1.5 `c9068a332f4ecc36bdd3a963afe74be5253b7820c00249e0ed4e4ffd33b9778f`, and ×2 `b39e1def246dea7f1bd4a57bebf3fe8ff9da46f198e00119aeab3916184b859c`. This identifies the reviewed plan content; it is not a new read of Clariden's files. The existing launch procedure must still authenticate the actual deployed bytes.

**H1 — HIGH: Stage C changes the selection/epoch-evaluation population**

Evidence chain:

1. [stage_b_trial.py](stage_c_package/stage_b_trial.py), line 43, installs the adapter with `study=True`. [run.py](stage_c_package/run.py), lines 38–44, then constructs `pools['validation']` from **seal04 dev**, changing only the in-memory split role to `val`.
2. [stage_c.py](stage_c_package/stage_c.py), line 112, calls `run.install(runtime_path)` with the default `study=False`. The mapping above is skipped. `shared_validation` at `run.py:89` therefore supplies the original runtime's `validation` pool.
3. The SHA-matching [prepared runtime](../../../out/TRAIN_FULL_v1/receipts_005/data_prepared_runtime.json) contains **13,088 validation rows** and **437 seal04-dev rows**. These are distinct pools with different file bindings. [prepare.py](stage_c_package/prepare.py), lines 136–146 and 194–195, separately builds the original S1 `val_mix` and seal04 benchmark panels.
4. Every real lane logs `val=13088 rows`; for example [×1 control log](../../../out/TRAIN_FULL_v1/receipts_stage_c_smoke/smoke_tree/runs/w1-control/srun-3757298.log), line 2. This is observed execution, not a hypothetical code path.
5. [train.py](stage_c_package/vendor/train/train.py), lines 1213–1233, evaluates that loader and uses its CER to update `best.pt`, `best['metric']`, and `bad_epochs`. [STAGE_C.md](STAGE_C.md) instead says selection remains seal04 dev; [STAGE_C_MEMORY_FIX.md](STAGE_C_MEMORY_FIX.md), lines 60–62, incorrectly conflates the S1 validation mixture with seal04 dev.

This violates the requested preservation of the study settings outside the explicitly authorized changes. It also adds eight 13,088-row CER passes per full run where the package narrative describes eight 437-row diagnostics. The four requested reporting panels are still evaluated, and I found no direct path from their test metrics to selection. H1 is an unauthorized selection-population change, **not a demonstrated test-leakage claim**. Early stopping remains unreachable, and final-state retention is not conditional on this metric; those facts do not repair the changed `best.pt` rule.

**Closure:** make Stage C's selection loader and provenance use the exact Stage B seal04-dev view while keeping all four reporting pools and full-pass checks. Merely passing `study=True` is insufficient: that mode excludes the test pools and changes full-pass provenance behavior. Add a regression with deliberately distinct legacy-validation and seal04-dev identities/counts, and assert the loader actually used for `best.pt`. Reseal, bind fresh plans, and qualify the corrected evaluation/selection path and resume identity; the current real smoke certifies the current behavior. Update the incorrect claims and measured cost evidence. An explicit owner decision to change the selection rule would be a different scientific specification; this review does not infer it.

**Recipe, data and horizon checks**

The three adopted JSON files are byte-for-byte equal to their `search_study1/trials/` originals. Independently ranking all 51 rows of `summary.csv` by final pooled NFD CER gives exactly these winners. B2 remains skipped, with seed variance and short-to-full-horizon transfer unmeasured.

| Width | Winner; batch / workers | Exact LR; beta1; weight decay | Updates; CER steps |
|---|---|---|---|
| ×1 | w1-h13; 256 / 6 | `0.004923790992275309`; `0.8441688793453093`; `0.08091629390345273` | 49,584; 12,396 / 24,792 / 37,188 / 49,584 |
| ×1.5 | w1.5-h14; 256 / 6 | `0.001557039425821051`; `0.9276696010439821`; `0.025859000361282754` | 49,584; 12,396 / 24,792 / 37,188 / 49,584 |
| ×2 | w2-h04; 64 / 6 | `0.0003692322353070561`; `0.8396755078487886`; `0.03793798675202968` | 198,312; 49,578 / 99,156 / 148,734 / 198,312 |

The ×2 LR above is the exact trial value, rather than the rounded value in the prose brief. Each run has eight epochs of 1,586,454 draws: one pass over 793,227 real rows plus equal synthetic exposure, totalling **12,691,632 draws**. Per-epoch rounding, not rounding the combined horizon, produces the stated update counts. The actual frozen sampler is checked before training. OneCycle uses the entire summed epoch-batch horizon, pct_start .075 and no momentum cycling; AdamW beta2 .999, epsilon default 1e-8, clip 5, norm/bias decay exclusion, accumulation 1, model seed 0 and data seed 20261015 remain unchanged. Vendor model/data/codec/scorer/optimizer source is unchanged from Stage B. The full-pass and parliament-share checks remain active.

No init/resume argument imports Stage B or cancelled ×2 weights. Fresh per-run claims and output directories, segment binding/provenance checks, and the unchanged prepared-data lineage separate data reuse from training-state reuse. Actual remote directory emptiness is not re-observed in this read-only local review.

The named test pools feed only the reporting hook; it restores RNG and model mode in `finally` and returns no selection metric to the trainer. `PATIENCE=epochs+1=9`; `bad_epochs` increases only once per completed epoch and is restored on resume. Nine bad epochs cannot occur in eight epochs. `last.pt` is written unconditionally, and COMPLETE requires the exact final step and draw count. The recorded stable-seal release suite includes all three eight-worsening-dev-epoch regressions. H1 concerns which dev population selects best, not premature stopping.

**Cadence and retained checkpoints**

[loss_cadence.py](stage_c_package/loss_cadence.py), lines 14–29, counts actual sampled indices, including shuffled partial batches. Evaluation occurs on the first completed update crossing each multiple of 50,000; overshoot is less than one batch. There are **253 crossings plus the final point = 254 checkpoints/run**, with final included once. The complete full-run step list depends on prepared pool widths and is generated at startup; it was not regenerated locally from unavailable parquet data.

Firsthand cross-check of the copied smoke tree found **24 unique model references per lane, 144 total**, at steps 2,4,…,48. Every loss point's SHA and size match the JSONL index and COMPLETE record; every index checkpoint reference equals its point's checkpoint reference. All points have matching step/draw/threshold values and all four complete runtime panels. At ×1/×1.5 the smoke finishes at 12,288 draws; ×2 finishes at 3,072. Each control/requeue pair has identical 48-update draw/loss traces, draw-chain digest, all 24 per-point model-state hashes and loss results, and final four-panel CER results.

The copied `loss_checkpoints/`, `checkpoints/`, and `yields/` directories contain **no `.pt` files**, as specified for this packet. Thus I verified reference consistency, not local archive bytes or local tensor loading. The authenticated real smoke readout records successful remote file-SHA and tensor/config/codec validation using the reviewed `smoke_readout`/`validate` implementation. Full scientific continuation identity, including optimizer/scheduler/RNG, is a recorded remote result; it cannot be recomputed from the stripped packet. The two COMPLETE state hashes need not be identical: the readout compares the explicit scientific `compare.FIELDS`, excluding operational provenance differences.

Source inspection supports the required recovery ordering: durable segment first; immutable CPU model+codec+parsed-config archive; file and directory fsync; SHA/reload validation; full loss evaluation; point JSON; append-only journal; directory fsync; then further training. Existing archives are validated and reused, not overwritten. Recovery reconciles a missing journal append and refuses corrupt/missing historical archives. These model archives omit optimizer/scheduler/RNG intentionally; exact continuation remains in `segment.pt` and the four full-state CER archives. No metric-based pruning exists.

The SHA-bound [release XML](evidence/TESTS_STAGE_C_50K_RELEASE_002.xml) records **165 passed, 0 failed/error/skipped**; the focused XML records 22 passed. I inspected the SIGKILL-after-archive and SIGKILL-after-loss tests at all widths, immutable inode/mtime/SHA checks, interrupted-write handling, corruption refusal, and weights-only/frozen-loader checks. I did not rerun these process-spawning, file-writing tests. The earlier unstable-seal failed suite is explicitly superseded, not counted as passing evidence.

**TERM, requeue, isolation and resources**

The shell installs its TERM trap before Python startup, persists a job/restart-scoped stop request, and does not forward the deadline warning to `srun`. The segment polls at optimizer boundaries, finishes any current evaluation publication, saves, and returns 75; the shell handles repeated interrupted `wait` calls and requeues once. The controller accepts 0/75. Genuine unexpected failures still raise, appropriately; the former warning-as-error branch is absent. Full segments request **23:00:00**, with warning at end-minus-600 seconds; the internal deadline calculation agrees and forces standard Slurm time formatting. This is below 24 hours. Requeue retains the same job/config/claim rather than relying on a purged dependency job.

At every width, `REAL_SIGNAL_SENT.json` records the actual `scancel --batch --signal=TERM` command at observed step 3. The stop-file SHA matches its first yield receipt. Sacct shows the initial numeric step exiting **75:0**, the parent REQUEUED, and the same job running again. All six final parent entries are COMPLETED 0:0. The twins also underwent further requeues/preemption; there are **15 parent allocation segments** in all: six COMPLETED, six REQUEUED, three PREEMPTED. The final three cache-validation restarts do no training and explain why there are only **12 training allocation attestations**.

I independently compared all 12 recorded worker intervals: every end is measured, every interval lies inside its matching job/restart/host parent interval, and there are **zero global GPU-UUID or same-host CPU-affinity conflicts**. Each affinity has exactly 24 CPUs. The reviewed accounting fallback requires a unique terminal parent and numeric step with matching host/start/resources when a worker cannot record its end; it does not substitute a controller upper bound. No such fallback was needed for this smoke.

Every parent AllocTRES is **`cpu=24,gres/gpu=1,mem=110G,node=1`** (some also contain energy). Concurrent placement on `nid007225` independently demonstrates sharing. `node=1` counts the host touched; it does not mean four GPUs were allocated. Summing every parent duplicate once gives **4.815556 allocated GPU-hours** for the fresh smoke; summing child rows again would double count. The union of observed host-busy intervals is 1.865278 hours, illustrating why GPU-hours, per-job node-hours, and unique physical-host occupancy are different quantities.

The captures establish allocation, not the site's monetary/project billing tariff: no `billing` TRES, charging weights, or debit ledger is supplied. Under GPU-proportional charging the jobs consume one GPU-hour per running hour, not four. A four-GPU-node-equivalent conversion is useful for comparing the old renewal, but is not independent proof of billing.

**M1 — MEDIUM: 110G long-segment headroom is unverified**

The fresh smoke really ran with the explicit 110G request and full prepared pools. No OUT_OF_MEMORY terminal state or OOM diagnostic appears in the supplied logs. Active numeric steps report **200,098,880K–226,469,696K MaxRSS**, approximately **190.83–215.98 GiB**; the reference-lane peaks are 213.17 / 215.92 / 204.77 GiB. The very short final validation restarts report only 36,864K and must not be used as the training peak.

The supplied owner/coordinator evidence identifies `jobacct_gather/linux` without UsePss. Summed process RSS counts shared pages repeatedly, so these values do **not** establish that a job used 191–216 GiB of unique/cgroup-charged RAM. Dividing by the number of workers would not establish its true usage either. There is no raw scheduler-configuration capture, cgroup `memory.peak`/`memory.events`, aggregate PSS/USS series, or memory-enforcement configuration in this packet. Absence of OOM is useful short-run evidence, not proof that enforcement was active or that 110G has measured spare capacity.

Full runs additionally assemble 1,586,454 training rows per epoch versus 6,144/1,536 in the smoke. Dataset label arrays, persistent worker copy-on-write behavior, epoch transitions and longer-lived allocations remain unmeasured at that scale. **Judgment: 110G is not disproved by the RSS reading, but safety for 23-hour segments is unverified.** This is logged as an unresolved capacity risk rather than an invented OOM finding. Capture actual aggregate/cgroup peaks and enforcement/OOM counters during representative full-size setup and sustained loading; do not label the share capacity-qualified on this packet alone.

**M2 — MEDIUM: forecast reproduces exactly, but has little margin and unmeasured scaling costs**

I recomputed the supplied forecast without writing output; costs, totals and observed hazard match exactly. The older [STAGE_C_FORECAST.json](evidence/STAGE_C_FORECAST.json) is provisional and superseded for this decision. The measured inputs are 46 timed training updates per reference width, 24 full loss evaluations, one four-panel CER evaluation, archive saves, and short-run restarts.

| Width | Training GPU-h | Loss + four CER GPU-h | Eval/training; share of training+eval | Low / expected / high GPU-h |
|---|---:|---:|---|---|
| ×1 | 12.112 | 6.435 | 53.13%; 34.70% | 19.115 / 19.967 / 23.089 |
| ×1.5 | 12.998 | 6.959 | 53.54%; 34.87% | 20.571 / 21.567 / 25.283 |
| ×2 | 28.009 | 7.768 | 27.73%; 21.71% | 38.557 / 40.318 / 46.762 |
| Total | 53.119 | 21.162 | | **78.243 / 81.852 / 95.135** |

The model also includes 3.852 GPU-hours of durable/retention saves before interruption costs. Mean retained-model save times are 0.086 / 0.145 / 0.212 seconds. The hazard is 54 PREEMPTED+NODE_FAIL parents divided by 64.3103 allocated node-hours, or 0.839679/hour; high doubles it. The underlying capture accounts for 252.9703 requested GPU-hours, a different population from the final Stage B 255.14-hour ledger. The high case is a scenario, not a bound.

At four GPUs/node, the totals correspond to **19.56 / 20.46 / 23.78 full-node-equivalent hours**, below the earlier approximately 45-node-hour renewal on that proportional basis. Actual placement/physical-host occupancy and billing are not guaranteed by that division. The later 82-GPU-hour approval is the more specific owner decision. Expected cost is only **0.148 GPU-hours (8.87 GPU-minutes)** below 82; the approved estimate should not be represented as a hard runtime guarantee or as permission to ignore accounting. The fresh smoke's 4.816 hours are separate from the full-run forecast; the obsolete smoke's 34:52 is an additional coordinator-recorded 0.581 single-GPU hours, not reverified from accounting here.

Two material extrapolations remain: full-size sampler/dataset initialization on every restart (including eight-epoch planning and PNG-header/label validation in `train.py:833–839` / `ManifestDataset`), and validation of accumulated archives on late resume. The tiny-horizon smoke measures neither cost at full scale. The forecast also omits the separate epoch validation CER passes exposed by H1 and does not explicitly count deterministic 23-hour segment renewals; ×2 necessarily exceeds one segment even in the low case. These are reasons to refresh the estimate after H1 and monitor measured startup/accounting, not to shorten the requested horizon. All three eval/training ratios exceed 25%; retain the owner's cadence, already approved after the cost disclosure. Coarser cadence or an evaluator optimization would require its own authorized change and qualification.

**M3 — MEDIUM: storage allowance is planning evidence, not a quota or occupancy bound**

Smoke model archives are 15,182,375 / 33,656,615 / 59,411,175 bytes: **3.856 / 8.549 / 15.090 GB** for 254/run, **27.496 GB total**, before slightly larger full-horizon config metadata. The documented 8/16/28 GB run provisions total 52 GB and include other output types, but do not bound arbitrary requeues. Yield hardlinks retain old full-state segment inodes after later atomic replacements; a yield archive is not permanently free. Smoke final segments are approximately 58/113/190 MB. At the forecast's roughly 17/18/34 expected interruptions, retaining one such inode per graceful yield would add roughly 9.5 GB across widths; actual graceful-yield counts and full-state sizes differ, and the high tail adds more. Four CER states, epoch artifacts, best/last and predictions also remain.

The ledger reports 303 TB filesystem free at deployment. No raw `df`/project quota or inode-limit receipt is supplied locally, so per-user/project headroom is **unverified**. Preserve the existing prelaunch capacity check and account for retained yield history; there is no evidence here of an actual disk exhaustion or pruning bug.

**L1 — LOW: population count and stale status prose**

The exact prepared runtime and all 144 smoke loss records have harvest-test **52,847**, not 52,846; the four-panel total is therefore **71,887**, not 71,886. This is a stale description, not a newly changed runtime or missing-row observation. Measured C evaluation timings cover the actual 71,887 rows, so their measured forecast does not depend on the old row-scaling constant. Correct the narrative counts without changing data. Older PREPARED/PENDING and B2-required statements in historical notes are superseded by the latest ledger and owner decisions; preserve history but make the current disposition explicit.

The current seal's resource sharing, loss retention, real TERM/requeue trajectory, and sampled isolation checks have supporting evidence within the limits above. **Launch remains held on H1.** Closure must identify the corrected selection population in actual execution, bind its seal/plan and qualification evidence, and avoid promoting this old smoke as proof of changed behavior. No additional owner confirmation is requested by this report; the recorded authority remains in force.

VERDICT: HOLD | BLOCKERS: 0 | HIGH: 1
