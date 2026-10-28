# ASTRA — Stage C focused re-review, 27 October 2026

**PASS: 0 BLOCKER, 0 HIGH. H1 is closed for seal `7e8a497f21527b90` and the plans identified below.** The corrected selection path is supported by the sealed source, a meaningful regression, and all six real CUDA smoke lanes. The new smoke supports real TERM/requeue continuation and retained-checkpoint behavior at every width. M1–M3 remain MEDIUM operational/extrapolation follow-ups; they do not constitute a scientific launch hold under the owner's stated disposition rule.

Scope: independent local inspection, SHA recomputation, source/diff review, raw receipt and journal comparisons, accounting/isolation reconstruction, and independent forecast arithmetic. No network, SSH, Slurm action, background job, training, or test suite was run. Only this report was written. Recorded tests and remote tensor validation are distinguished below from firsthand local checks.

The owner decisions remain in force: three full runs at ×1/×1.5/×2 with the adopted Stage B points; B2 skipped; all four panels at every 50,000-drawn-line loss/model point; full CER at 25/50/75/100%; test reporting only; **“82 GPU-h, all three”** and the subsequent autonomous overnight instruction. The 82 GPU-hours is an approved estimate, not a hard cap. No additional owner approval is requested here. The coordinator still executes the documented capacity/readback and submission procedure; this report is neither a launch nor confirmation of remote full-run completion.

**Exact reviewed bindings**

| Object | SHA256 |
|---|---|
| Current package PAYLOAD | `7e8a497f21527b90bfd758fa8afceeabcc4b329aa31dc08535a2ce0472dde1e6` |
| Preserved c826 parent PAYLOAD | `c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b` |
| Smoke PLAN, full-v1-013-stage-c-sel | `bccce2d5ac6e798970011739800514c52d04209229ad20a0e1b64d29ea94a261` |
| Full PLAN, same attempt | `81dc15a567fccfd1c3d911cdf268ed72f69fb883d6bc937dddc50d2681d207ca` |
| Prepared005 runtime | `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4` |
| New SMOKE_IDENTITY.json | `342d3cd5b1fa843152d4f99d530b67dc003fc6ac06dc1225fe0a43a69dd9019d` |
| New MEASURED_FORECAST.json | `f8b6918a001623459ab53d07100e79dfc8a1fba18eecbcd64d3246bad372be81` |
| New SMOKE_SACCT_ALL.txt | `d3195e9da7d955beb5fa75caff6e46c9db918b9d445b84be950d6ce0f9b8c6c8` |
| New SMOKE_MEMORY.txt | `ae51cdbb8eec56ae49aa101dda6216f1293a852499a89ce2e0dda66e6617dd3f` |
| Current COMMANDS.md | `e951217ef17e8afe624248e7321b73feaad005dd647526f85706198131de7529` |

All **93 sealed files** match their byte counts and hashes; there are no extra package files. Every package Python source parses. The sealed verifier and read-only data-compatibility function pass, and the latter exactly reproduces [STAGE_C_SEL_DATA_COMPATIBILITY.json](evidence/STAGE_C_SEL_DATA_COMPATIBILITY.json). I independently reconstructed the 35,177-byte [diff](evidence/STAGE_C_SEL.diff) from the preserved parent files and current files: exact match, SHA `46abed1556a79c58cd4d33b3c43c63fd38f286fd490cd557c9c4559f916830b2`.

The local [expected plans/configs](evidence/STAGE_C_SEL_BINDINGS/EXPECTED.json) have the table's hashes and valid config references. Each config's parameters match the adopted source plus the intended full/smoke horizon. The actual smoke bindings agree with these predictions. The latest [execution ledger](EXECUTION_STATE.md) records matching deployment/full-plan SHAs; I did not re-read the remote full PLAN. These exact full-config SHAs are reviewed: ×1 `168d59fd350f8820738c4d250352822c0e0214a4fd4ca4e36e1c21ae9cb6f02c`, ×1.5 `6522e316d58fcbc012998f3ecc4d6d6c17e506ea79be0bdabc37fa731c650121`, ×2 `e71f40b59a54015d937f6f1aaa2023f9cb319711b80fd56daaae9b6efbd1bf9c`.

**H1 — CLOSED: the actual epoch loader selects on seal04 dev**

The evidence chain is now consistent:

1. [stage_c.py](stage_c_package/stage_c.py), lines 113 and 154–168, explicitly installs `selection_pool='seal04_dev'`, checks its runtime pool binding, publishes the immutable selection identity, and instruments the epoch evaluator around `trainer.train`. It retains `study=False`.
2. [run.py](stage_c_package/run.py), lines 41–52 and 86–100, maps validation to the exact ordered Stage B seal04-dev rows/labels with only the in-memory `split='val'` role change. The validation provenance uses that same pool spec. All test pools remain loaded, and full-pass, half-synthetic and parliament-share checks remain active. Setting `study=True`, which would remove tests and bypass full-pass enforcement, was correctly avoided.
3. [selection_diagnostics.py](stage_c_package/selection_diagnostics.py), lines 13–23, checks the **actual loader passed to the epoch evaluator**, including ordered `(line_id, label_ids)` digest, then returns the original evaluator result unchanged. The frozen [trainer](stage_c_package/vendor/train/train.py), lines 1211–1235, uses that result for `val_cer`, `best['metric']`, `best.pt` and `bad_epochs`. There is no transfer loader. Four-panel reporting remains a separate hook with RNG/model-mode restoration and no selection result returned to the trainer.
4. Every lane's `SELECTION_POOL.json`, `RUN_BINDING.json`, COMPLETE binding and both epoch-evaluation receipts agree: **437 rows**, ordered identity `6fb35287f561a4566271e2e3ea0f713fbb6b7ef86991352588c7f3861e62fb73`, parquet SHA `03fb2504d49fb0abf47af839bf023ab02456e90ea95c84b8701296b5cfa4bcae` (5,852,207 bytes). The pool spec matches the locally byte-verified prepared runtime. All **12 evaluation receipts** are SHA/size verified. All six logs show `val=437 rows`; all six metadata records select `val_cer`, retain best epoch 1/metric 1.0, and the logs end with `bad 1/3` after the equal second metric. Example: [×2 requeue log](../../../out/TRAIN_FULL_v1/receipts_stage_c_sel_smoke/smoke_tree/runs/w2-requeue/srun-3760344.log).
5. The reviewed remote `smoke_readout` additionally reconstructs this identity from the SHA-checked parquet and checks final checkpoint validation provenance. The parquet and weights are not in the local smoke packet, so their contents and final binary `best`/`bad_epochs` are remote validated results, not newly loaded local tensors. The local evidence independently corroborates the loader and best metadata; it does not pretend to rehash unavailable rows or weights.

The new [selection regression](stage_c_package/tests/test_stage_c_selection.py) is meaningful: legacy validation has eight distinct IDs, seal04 dev has three different IDs; it observes the actual epoch loader, injects eight worsening CER results, and asserts best epoch 1/metric .01, `bad_epochs=7`, the saved best checkpoint, provenance, final horizon and all reporting panels. The adapter/CTC/optimizer/trainer execute with a small stochastic model; only the model and controlled epoch scores are test substitutes. The second test proves equality to Stage B's view and rejects duplicated real draws in the production full-pass branch. It would catch the original wrong-loader defect. Existing eight-worsening-epoch tests also cover all three adopted widths with altered test references.

The SHA-bound [final release XML](evidence/TESTS_STAGE_C_SEL_RELEASE_002.xml), SHA `2bf9c082de28fd78ee4125aa1064acaf9b54f0014c3dccf1c4db3af561dc6fd8`, records **171 tests, zero failures/errors/skips**. The failed initial focused run and superseded 170-test release are preserved and are not substituted for this final receipt. I inspected the tests; I did not rerun them.

**Scientific delta and retained reporting**

Only three existing sealed files changed: `run.py` (selection mapping/provenance), `stage_c.py` (selection binding/instrumentation, memory diagnostics and readout), and `forecast.py` (cost/storage accounting). Five files were added: two diagnostic modules and three tests. All vendor/model/optimizer/data/codec/scorer files, adopted trials, recipe, horizon/cadence/retention hooks, runtime environment, and resource/signal shell bytes match c826. Memory collection is observational; it can impose operating overhead but does not change training math or selection. No additional scientific change was found.

| Width | Adopted point; batch/workers | LR; beta1; weight decay | Updates; CER steps |
|---|---|---|---|
| ×1 | w1-h13; 256/6 | .004923790992275309; .8441688793453093; .08091629390345273 | 49,584; 12,396 / 24,792 / 37,188 / 49,584 |
| ×1.5 | w1.5-h14; 256/6 | .001557039425821051; .9276696010439821; .025859000361282754 | 49,584; 12,396 / 24,792 / 37,188 / 49,584 |
| ×2 | w2-h04; 64/6 | .0003692322353070561; .8396755078487886; .03793798675202968 | 198,312; 49,578 / 99,156 / 148,734 / 198,312 |

Each full run still draws **12,691,632 lines** over eight epochs of 1,586,454: one pass over 793,227 real rows plus equal synthetic exposure each epoch. Model seed 0, data seed 20261015, full-horizon OneCycle, other optimizer settings and fresh initialization remain unchanged. Full patience is nine for eight epoch decisions, so it cannot truncate the horizon. B2 remains skipped with variance unmeasured.

The reporting denominators are **437 / 2,253 / 16,350 / 52,847**, total **71,887**, for seal04 dev/test and harvest dev/test. I checked all 144 smoke loss records and all six final CER records against those exact counts. Test metrics do not enter best/stopping. The 52,846 crop-unique figure is not the harvest-test evaluation denominator.

Each smoke lane retains references for 24 distinct models at steps 2,4,…,48. All point/index/COMPLETE references agree in SHA, size, step, draws and thresholds; every available referenced point and journal authenticates. Across each control/requeue pair, all 24 model-state digests, losses, training losses at those points and final CER results agree, as do all 48 update traces, draw positions and draw-chain digests. The full policy remains **253 crossings of 50,000 draws plus final = 254 retained models/run**, final once, alongside four full-state CER archives and last/final state. The frozen sampler determines the crossing update, including partial batches; the full-size step list was not regenerated without the prepared pools.

The copied packet intentionally contains **zero `.pt` files**. Local checks establish reference/trace/metric consistency. Full optimizer/scheduler/RNG/best/bad_epochs equality and archive tensor loading are the recorded real remote BIT_IDENTICAL result produced by the reviewed validator. No claim of locally redoing that binary comparison is made. Retention/publication/recovery code is unchanged from c826: durable state, immutable model archive and validation, full loss result, then journal; existing history is checked and retained without pruning.

**Real signal, requeue and isolation — PASS**

Jobs 3760339–3760344 ran the six lanes. Each requeue lane records actual `scancel --batch --signal=TERM` at observed step 3, a SHA-matching persistent stop request and a retained yield checkpoint. Its first numeric Slurm step exits **75:0**, parent is **REQUEUED**, and the same job resumes with restart count 1; measured resumed first update is 6. Each final parent is COMPLETED 0:0. The numeric step's `FAILED 75:0` is the intended yield, not an unexpected trainer failure.

I independently checked **nine measured allocation intervals** against the matching job/restart/host parent and numeric step, then every temporally overlapping pair: **zero global GPU-UUID conflicts and zero same-host CPU-affinity intersections**. Every affinity has 24 CPUs. Every parent requests/allocates one GPU, 24 CPUs and 110G; concurrent placement on nid006073 demonstrates sharing. No recovered-end estimate was needed. Summing parent allocation duplicates once gives **4.287777778 GPU-hours** for this new smoke, separately from full-run estimates and earlier attempts.

The unchanged shell has the early batch TERM trap, persistent stop file, optimizer-boundary yield, repeated-interrupted-wait handling and same-job requeue. Full time remains 23:00:00 with warning 600 seconds before expiry. This smoke tests the actual warning signal mechanism at short elapsed time; it is not a 23-hour endurance test. GPU allocation accounting is not an independently verified monetary tariff.

**M1 — MEDIUM retained: substantial measured headroom, full-length capacity unqualified**

I authenticated all nine `MEMORY_*.json` files through their allocation references and recomputed the summaries from raw counters. They identify `/sys/fs/cgroup/system.slice/slurmstepd.scope/job_<id>`, with actual cgroup-v2 `memory.max = 118,111,600,640` bytes (**110 GiB**) in every job sample. This is now direct finite-limit evidence, not an inference from Slurm's requested memory or summed RSS. All raw job events—`max`, `high`, `oom`, `oom_kill`, `oom_group_kill`, `low`—are zero. Every segment has start/end samples and every yielded segment also has a yield sample.

| Lane | Job memory.peak GiB | Maximum complete summed PSS GiB | Limit minus peak GiB |
|---|---:|---:|---:|
| ×1 control | 39.565 | 36.835 | 70.435 |
| ×1 requeue | 39.798 | 36.520 | 70.202 |
| ×1.5 control | 39.634 | 36.893 | 70.366 |
| ×1.5 requeue | 39.542 | 37.286 | 70.458 |
| ×2 control | 35.515 | 33.044 | 74.485 |
| ×2 requeue | 34.496 | 32.937 | 75.504 |

There are **505 samples, 504 with complete process-tree PSS**. One ×1-requeue sample records disappearing worker PIDs; it is excluded from the complete-PSS maximum, and cgroup counters remain available. The aggregate `capture_status=COMPLETE` does not mean every PSS sample was error-free. PSS includes up to seven processes and is sampled, while cgroup peak records the job high-water mark. The maximum raw job peak is 42,732,748,800 bytes; maximum PSS is 40,035,946,496 bytes. Thus the ledger's approximate 42.5/39.6 GB figures describe roughly the controls, not the exact all-lane maxima. `SMOKE_MEMORY.txt` still has much larger summed RSS; it does not override the direct cgroup/PSS measurements.

**Judgment:** the measured jobs use at most 36.2% of the finite limit, leaving at least **70.20 GiB** headroom. This supports proceeding with the existing 110G share and materially resolves the earlier apparent RSS contradiction. It does **not** certify 23-hour headroom: complete segments sampled about 33–43 minutes, with only 6,144/1,536 training rows per smoke epoch versus 1,586,454 in production. Full-size dataset/horizon setup, epoch transitions, worker copy-on-write growth and long-lived allocations remain unmeasured. Keep `capacity_qualified=false`; inspect the existing memory diagnostics through full setup and sustained training. No evidence in this packet warrants a HIGH memory hold or a resource change.

**M2 — MEDIUM retained: refreshed raw forecast is below 82 GPU-hours; scaling remains uncertain**

I authenticated all forecast inputs and independently recomputed raw timing aggregates, interruption hazard, save/evaluation costs, renewal fixed point and totals (agreement to floating-point rounding). Inputs per control width are 46 timed updates, 24 complete four-panel loss points, one four-panel CER pass, two measured selection evaluations, retained saves and an actual resumed startup.

| Width | Training GPU-h | Loss + four CER + eight selection GPU-h | Low / expected / high GPU-h | Renewals low / expected / high |
|---|---:|---:|---|---|
| ×1 | 9.704525 | 5.260382 | 15.417702 / 16.030620 / 18.240812 | 0 / 0 / 0 |
| ×1.5 | 10.795589 | 5.705327 | 17.120620 / 17.797236 / 20.228965 | 0 / 0 / 0 |
| ×2 | 19.990183 | 6.797276 | 29.506846 / 30.661902 / 34.814148 | 1 / 1 / 1 |
| Total | 40.490297 | 17.762985 | **62.045168 / 64.489758 / 73.283925** | |

Selection costs are genuinely measured on the corrected loader: **0.426769 / 0.443975 / 0.522295 seconds per epoch**; all eight are included, totaling 0.003095642 GPU-hours across the three full runs. Durable/retention save costs add 3.664721 GPU-hours before interruption costs. The observed hazard remains 54 preemptions/node failures divided by 64.310278 allocated node-hours = **0.839679/hour**, with twice that hazard in high. Segment usability is 22.833333 hours, and the renewal calculation includes startup plus a yield save. Counting renewals against aggregate elapsed time can overcount when actual preemptions reset the timer.

**Expected cost does not exceed the owner-approved estimate: 64.489758 GPU-hours is 17.510242 below 82.** This is the new measured-smoke forecast, superseding the explicitly unmeasured selection proxy/interim 81.894777 estimate. The new smoke's 4.287778 hours and earlier smoke spending are separate ledger entries. High is a scenario, not a bound, and 82 is not a runtime cutoff.

The reduction from the c826 expected 81.852 forecast is largely faster observed training/evaluation, not simply correcting selection: update seconds changed .879361→.704588 / .943743→.783804 / .508453→.362886; loss seconds changed 89.471→73.128 / 96.877→79.329 / 107.837→94.705. The source/diff provides no basis to promise these faster timings throughout production. Full-size planning/PNG-header/label validation at startup and epoch changes, late-resume verification of accumulated archives, placement contention and transfer of the Stage B hazard remain extrapolations. The model also uses resume-mean startup for the first start; observed control first starts were 137.150 / 133.913 / 109.944 seconds versus resume means 120.313 / 115.494 / 110.526 seconds. This small approximation is distinct from the larger unmeasured full-size startup cost.

All smoke selection results are CER/blank-rate 1.0, as expected for this very short training trajectory; they prove the selection route, not eventual OCR quality or mature decode cost. Eval/training ratios are still **54.21% / 52.85% / 34.00%**. Preserve the approved full coverage/cadence; no subsampling, shortened horizon or evaluator change is justified by this review. Follow actual costs and progress during the authorized runs.

**M3 — command requirement closed; MEDIUM residual capacity readback**

[COMMANDS.md](../../../out/TRAIN_FULL_v1/COMMANDS.md), lines 175–220, places the capacity capture **before full submission**: filesystem bytes and inodes; user and group quotas; directory project ID and its project quota; raw capture plus SHA; forecast storage comparison. It explicitly rejects treating filesystem free space as project-quota proof and requires the actual site's quota mapping if these commands fail. This satisfies the requested command-presence check. No local raw prelaunch quota receipt exists in the supplied packet, and this review did not execute those commands. The reported 305 TB free is ledger evidence only.

Fresh forecast storage totals are **33.218220 / 40.679464 / 50.100480 GB** low/expected/high, including 254 model archives per run, four CER states, best/last/rolling, the modelled retained yield inodes and log allowance. The model archives alone total 27.495542 GB. Hardlinks cease to be space-free when the rolling inode is replaced; arbitrary requeues, full-state/config growth and logs can exceed the scenarios. Keep the existing immediate pre-submit comparison against actual available bytes/inodes/quota plus occupancy and margin, and record its outcome. This is an operational step in the existing launch procedure, not a request for another scientific review or owner reconfirmation.

**L1 — LOW: current counts corrected; historical status remains stale**

The selection-fix note and runtime now use 52,847 harvest-test / 71,887 total rows. The ledger's initial table and older preparation statements still say pending/budget-held or claim the old seal selected on seal04 dev; the latest dated entries and this re-review supersede those statements. The generic provisional assumptions array in the measured forecast also retains conditional old wording; its actual cost fields use the new measurements. These are narrative limitations, not changed data or a launch defect.

No additional BLOCKER/HIGH issue was found that would justify wasting the authorized full runs through a changed scientific recipe, wrong selection population, test-based selection, premature stopping, broken retention or a demonstrated warning/requeue failure. Proceed through the existing exact-binding and capacity-readback procedure under the standing owner authority, retaining M1–M3 for operational follow-through.

VERDICT: PASS | BLOCKERS: 0 | HIGH: 0
