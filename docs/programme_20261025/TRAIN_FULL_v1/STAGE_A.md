# Stage A — batch throughput before tuning

This supersedes the ×1-only optimizer-study order. **Prepared only.** No network,
remote command, job submission or GPU measurement was executed by Sol. The
cancelled ×2 state remains evidence and is never loaded. Stage A keeps no model
checkpoints. [Owner commands](../../../out/TRAIN_FULL_v1/COMMANDS.md).

Question: for each model width, which batch gives materially higher single-GPU
throughput on the audited full population? Prediction, not evidence: increasing
batch should raise lines/s until model/CTC/input throughput saturates or GPU OOM.
Choose the largest batch whose measured lines/s improves at least **5%** over the
last accepted smaller batch. This 5% threshold and the 10% loader-wait trigger
below are explicit engineering judgments, not owner filters or established
scientific constants. Report every point, 100-update chunk rates and CV; a gain
comparable to timing variation warrants a repeat before adopting it.

Source: requested nn-tuning skill, dependency order item 4 and
`references/initial_config.md` §3.3/3.5. Batch is a throughput choice; a changed
batch reopens LR/betas/weight decay and steps. The skill's batch/scaling guidance
does not prove that this workload preserves CER at every batch.

| Measurement parameter | S1 w1/ref_364871/s0 | Stage A | Reason |
|---|---|---|---|
| Width multiplier | 1.0 | 1.0, 1.5, 2.0 | Owner's three sizes |
| Batch / accumulation | 64 / 1 | 64,128,256,512,1024 / 1 | Throughput sweep; stop each width/worker lane at first actual CUDA OOM |
| Training population | S1 v4 real + synthetic | Audited prepared005 train pools | 793,227 unique real TRAIN rows; exact half synthetic; unchanged parliament cap |
| Data seed / model seed | 20261015 / 0 | unchanged | Same epoch-1 mixture and sampler for all points |
| Model / codec / labels / preprocessing | compact / nfd / v2.1 | unchanged | Frozen vendor bytes; original 48px strips and own-background halo |
| Bucketing / tail packing | 128px / packed | unchanged | Actual S1 sampler; no resize, truncation or width cap |
| AdamW LR / betas / eps / WD | 1e-4 / (.9,.999) / 1e-8 / .05 | unchanged | Measurement, no optimizer tuning or scaling rule |
| Norm/bias decay / clip | zero / 5 | unchanged | Same update math |
| OneCycle | pct_start=.075, no momentum cycling | same shape, 331 updates | One capacity update + 30 warmup + 300 timed updates; disposable measurement horizon |
| Runtime / deterministic CTC | S1 CUDA + segment mode | unchanged | bf16 model; differentiable fp32 CPU CTC for exact-resume profile |
| Workers / native threads | 6 / four keys=1 | 6 versus 12 / four keys=1 | Measure loader effect within 24 assigned CPUs/GPU |
| Evaluation / checkpoints | epoch CER / saved state | none / none | No held-out pool is opened; no loss/CER selection |
| Requeue | exact training continuation | reuse complete points, repeat incomplete point from initialization | Measurement weights disposable; failed/killed intents and logs retained |

Every point first runs one optimizer update on the **largest padded tensor in
the full epoch's actual packed batch plan**. This catches rare wide/tail OOMs
outside the timed prefix. It records capacity-probe peak allocated/reserved
memory separately from warmup/timed peaks. An OOM is only
`torch.cuda.OutOfMemoryError`; data errors, nonfinite losses or CPU errors fail
the job rather than masquerading as capacity limits. No larger batch in that
lane is tried after OOM. Capacity at batch 1024 is a tested ceiling, not proof
that larger batches would fit or improve throughput.

Each point assembles epoch 1 from all train components using unchanged S1
largest-remainder quotas. It times a seeded prefix of the shuffled packed plan,
not a full epoch. Different batches expose different prefix lengths and width
mixes; logs include per-update rows and padded widths, a whole-draw SHA, train
loss, CTC health, elapsed seconds and 100-update chunk throughput. Capacity
probe/startup are excluded from steady-state throughput. Short-horizon schedule,
synchronized per-update measurement and shared storage contention limit transfer
to long runs; long-run measurement must confirm the projection.

Four independent srun steps run concurrently: ×1/6 workers, ×1.5/6, ×2/6 and
×1/12. Each requests exactly one GPU and 24 CPUs, uses GPU binding and CPU core
binding, and refuses multiple visible CUDA devices or missing native thread
limits. Srun supplies each lane's `CUDA_VISIBLE_DEVICES`. The physical GPU UUID,
process ID, CPU affinity and point interval attest isolation; the readout refuses
overlapping points sharing a GPU UUID or logical CPUs. No DDP, shared optimizer,
shared output or checkpoint exists. This proves resource separation, not absence
of contention on host memory/storage. Those remain measured conditions.

If any ×1.5/×2 baseline point spends ≥10% of elapsed time waiting for `next(loader)`,
that width also sweeps twelve workers in a second wave. Twelve workers are adopted
only for ≥5% better throughput after selecting a batch within each worker profile.
This loader-wait share measures exposed input wait after prefetch; CPU CTC time
is included in total update time and is not attributed to input loading.

The result is `$TF_STAGE_A/STAGE_A.json` with all points, throughput, GPU
utilization samples/mean, PyTorch memory peaks, nvidia-smi memory/power, loader
stall share, selected batch/workers and cost forecasts. The driver prints the
short table. Missing GPU telemetry fails the measurement. Local
[STAGE_A.json](../../../out/TRAIN_FULL_v1/STAGE_A.json) is explicitly
`PREPARED_NOT_MEASURED`, never a substitute for the remote report.

One preemptable node reserves **4 GPUs × 3 hours = 12 requested GPU-h**, ≤24h.
This is a reservation, not measured cost or a forecast of 3h completion. Historical
[S1 ×1 timing](package/s1_w1_timing.json) was .1041s/update at batch64 including
epoch validation. The coordinator observed .21s/update at ×2/batch64 in the
cancelled new-pool run. Neither establishes large-batch scaling. At those small
batch rates 330 updates cost roughly 34s/69s, excluding capacity/startup. Increasing
batch may increase time/update; actual cost comes from Stage A. The old 119/350
GPU-h accounting snapshot predates subsequent jobs and must be refreshed by the
coordinator before reserving 12 GPU-h. A timeout/preemption preserves completed
points and immutable attempt evidence; resume the same binding after inspection,
or use a new attempt for changed code/data. No dependencies on purged job IDs.

## B/C plan — implementation and launch remain pending Stage A

**B: three separate studies**, one per width at its selected batch/workers.
16 scrambled-Halton points, seed20261025, plus an unscaled S1 control:
LR1e-4, β1.9, β2.999, eps1e-8, WD.05. Initial search space stays
LRlog[5e-5,5e-3], β1one_minus_log[.8,.98], WDlog[.001,.3]. Larger batch alone
does not justify automatic LR scaling (skill §3.3); any range extension is
explicitly resealed before launch, and a best point near an edge triggers a new
study. Existing [space](hp_study1/lr_space.json) and
[16 points](hp_study1/lr_trials.jsonl) can be reused at each scientific width.
Beta1 trainer support/default.9 and per-trial runtime binding still need to be
implemented and reviewed; Stage A does not modify the vendor trainer.

Each trial draws **1,269,164 lines** = ceil(10% ×12,691,632), exactly half
synthetic. The final packed partial batch counts its actual rows, so the exposure
is equal across batches. OneCycle is initialized over the resulting trial
updates, pct_start.075 and no momentum cycling. Loss on **dev only** every50,000
drawn lines plus final (26 points), unchanged scorer dev CER at final; no test
pool loaded/evaluated. Fixed optimizer epsilon, β2, architecture, data/model seed,
gradclip, preprocessing and mixture are caveats. Train loss is also logged.

Primary `val_error` = pooled **nfd_atom corpus CER**: sum S1 scorer edits across
all 437 seal04-dev +16,350 harvest-dev rows divided by their summed reference
units, never an unweighted mean of panel CERs. Report both panels separately.
Only final dev CER exists, so `best_step=max_steps`; the analysis script's usual
best-ever-checkpoint convention then equals final. Emit per-trial top-level HPs,
width, batch, seed, status, val_error, best_step and max_steps in results.jsonl;
infeasible trials carry null objective and their real failure reason. Run the
skill's analyze_study.py separately per width with `--objective val_error` and
omit `--scientific` (the literal word `none` is treated as a column name).

Four independent single-GPU trials/node, each24CPUs, six or twelve workers as
measured. 51 trials use at most13 nodes if all started together; ≤5 nodes in waves
is an optional budget/availability constraint, not a requirement of this latest
brief. Owner/coordinator chooses concurrency against refreshed remaining budget.
Stage A readout gives 17×1,269,164/rate training GPU-hours per width, plus separate
three-seed and full-run training projections. It deliberately excludes dev
loss/CER/startup/requeue/reservation overhead: measure these in B's four-lane
CUDA smoke before submitting the study. If overhead exceeds25%, present complete
instrument/cadence options; never silently subsample.

Before B launch: per-trial claims/output locks, exact model/optimizer/scheduler/
RNG/iterator resume, loss journal recovery and cross-trial resource isolation
tests; four tiny CUDA trials with ≥3 loss points and a forced scheduler requeue
BIT_IDENTICAL to an uninterrupted twin; focused Astra PASS and owner go.
Nothing in Stage A qualifies this training smoke. Then rerun the best point at
seeds0/1/2 at the same short horizon; adopt only if its seed0 gain over control
exceeds its max-minus-min three-seed CER spread. Record the control's unmeasured
retrain variance as a remaining caveat; use control if the rule fails.

**C: one fresh full run per width**, after adoption and Astra/owner gates. No
cancelled state is reused. All train draws remain12,691,632 over8 epochs of
1,586,454 rows; total updates are **8×ceil(1,586,454/batch)**, not the old fixed
198,312 at every batch. Loss on all four complete dev/test instruments every
50,000 actual drawn lines plus final (254 points); exact sampler preflight binds
each batch's real step list. Tests remain report-only and never select/stop.
Latest wording requests four full-CER checkpoints **plus end**: proposed interior
draw targets20/40/60/80% plus final, crossing to the next optimizer boundary. This
replaces obsolete50k/100k/150k update archives, which large batches may never
reach. Bind the final target list in C's reviewable recipe before launch.
OneCycle must be reinitialized for each full horizon; short-study schedule/HP
transfer is a hypothesis, not proven full-horizon optimality. Patience disabled,
furniture fallback, unchanged data, deterministic exact resume, format-independent
Slurm reads, ≤24h preemptable segments and fresh per-run claims remain required.

| Chosen batch | B trial updates | C full updates | B target lines | C total lines |
|---:|---:|---:|---:|---:|
|64|19,831|198,312|1,269,164|12,691,632|
|128|9,916|99,160|1,269,164|12,691,632|
|256|4,958|49,584|1,269,164|12,691,632|
|512|2,479|24,792|1,269,164|12,691,632|
|1024|1,240|12,400|1,269,164|12,691,632|

STAGE A READY (B/C await measurements, implementation, CUDA smoke and review).
