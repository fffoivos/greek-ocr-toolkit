# Stage C — three full runs, PREPARE ONLY

Owner 26 Oct: skip B2 and adopt the best final pooled dev CER per width.
Current payload: **`7e8a497f21527b90`**. [Selection correction and qualification](STAGE_C_SELECTION_FIX.md)
closes the code path identified by Astra H1: Stage C now installs exactly the
Stage B **seal04-dev437 selection view**, while loading all four reporting panels
and preserving full-pass enforcement. Earlier C seals used legacy validation
(13,088 rows); the earlier claim that they selected on seal04 dev was incorrect.
New memory diagnostics report job cgroup peaks/limits/OOM counters and lane-tree
PSS, without changing numerical training. `--mem=110G` remains requested;
long-segment headroom is still unqualified.

There are 254 SHA-bound model+codec+config loss checkpoints/run and four full-state
CER archives; [retention policy](STAGE_C_CHECKPOINTS.md) is unchanged.
**Fresh actual-TERM/requeue CUDA smoke is required at all three widths**, then
focused Astra closure before launch. Existing owner authority **“82 GPU-h, all
three” stands**. Prepared005 is reused by exact compatibility proof; B2 stays
skipped. New plans use `full-v1-013-stage-c-sel`. Sol performed local preparation
only and leaves all old attempt files untouched. See [commands](../../../out/TRAIN_FULL_v1/COMMANDS.md)
and [current receipt](evidence/STAGE_C_SEL_RECEIPT.json).

## Adopted recipe

All settings are fresh seed-0 runs, never continuation of the cancelled ×2 run
or a Stage B checkpoint. Exact winning configs are sealed under `adopted/`.
The two dev instruments' final NFD-atom CER was pooled as **sum of edits / sum of
reference units**, not the mean of their two rates. Test instruments were not
used in Stage B. The owner waived the B2 seed-spread decision rule: no measured
retrain variance, no claim of significance. The analyzer flags ×1/×1.5 LR near
the high boundary and ×2 beta1 near the low boundary. Values remain unchanged.
Optimizer transfer from 10%-length runs and OneCycle at the full length is
unqualified scientifically; the smoke checks execution/identity, not convergence.
This is the limitation identified by the requested
[nn-tuning skill](</Users/foivoskarounos-zamparloukos/.claude/skills/nn-tuning/SKILL.md>)
and its tuning-loop/length guidance. The owner's explicit decisions govern.

| Parameter | Stage B winner | Stage C | Changed / reason |
|---|---|---|---|
| width / batch / workers | ×1 / 256 / 6; ×1.5 / 256 / 6; ×2 / 64 / 6 | identical | no |
| ×1 lr / beta1 / wd | 0.004923790992275309 / 0.8441688793453093 / 0.08091629390345273 | identical (`w1-h13`) | no |
| ×1.5 lr / beta1 / wd | 0.001557039425821051 / 0.9276696010439821 / 0.025859000361282754 | identical (`w1.5-h14`) | no |
| ×2 lr / beta1 / wd | 0.0003692322353070561 / 0.8396755078487886 / 0.03793798675202968 | identical (`w2-h04`) | no |
| AdamW beta2 / eps / grad clip | .999 / 1e-8 / 5 | identical | no |
| no-decay norm+bias / accumulation | true / 1 | identical | no |
| OneCycle shape | pct_start .075; cycle momentum false; frozen default div factors | identical | no |
| OneCycle total steps | 4,958 / 4,958 / 19,831 | 49,584 / 49,584 / 198,312 | YES: owner full eight-pass horizon |
| epochs / epoch_rows | 1 / 1,269,164 | 8 / 1,586,454 | YES: one full real pass/epoch plus equal synthetic draws |
| full drawn lines | 1,269,164 | 12,691,632 | YES: owner |
| loss cadence | 50,000 actual real+synthetic draws, final once | identical | no; number of points 26 → 254 |
| loss instruments | seal04_dev, harvest_dev | seal04_dev, seal04_test, harvest_dev, harvest_test | YES: owner reporting; tests never select |
| loss-point model retention | no retained model at every loss point | immutable weights+codec+config with SHA at all 254 points | YES: owner checkpoint every 50k lines |
| full four-panel CER archives | study final dev only | 25/50/75/100% draws (end included once) | YES: owner few checkpoints |
| selection / patience | seal04 dev best; stopping unreachable | exact seal04 dev view; patience 9 / 8 epochs | H1 correction to earlier C seals; same selection population/provenance as Stage B; tests report only |
| model seed / data seed | 0 / 20261015 | identical | no |
| train pool / mixture / source caps | 793,227 unique real train; 50% synthetic; inherited source fractions and parliament cap | identical | no |
| model, heads, codec, image preprocessing, packing, synthetic source, furniture fallback | frozen S1/study paths and prepared005 pools | byte-identical | no; reuse proof below |
| recovery checkpoint cadence | ≤100 updates plus eval boundaries | ≤20 updates plus eval boundaries | operational; cap lost updates under abrupt preemption |
| resume iterator | decode/discard consumed prefix | skip consumed batch indices before loading | operational, RNG restored; qualify six-worker CUDA identity |
| warning / segment | TERM forwarded to srun; 2h default | persistent stop request; 23h segment, TERM@600 | operational repair; no srun signal; exact checkpoint → 75 → requeue |
| requested resources | 4 trials in exclusive node group | 3 independent non-exclusive 1-GPU jobs, 24 CPUs and explicit 110G each | operational: avoid idle allocated lanes and coupled retries |

The original `recipe.json` is an unchanged S1 baseline used by inherited tools;
**Stage C's SHA-bound `configs/*.json` overrides are authoritative**, assembled
from `adopted/*.json` by `stage_c.py`. Vendor numerical source, including `vendor/train/train.py`, `s1_segment.py`, model,
optimizer, scheduler, assembler, codec and scorer, is byte-identical to Stage B.
The current delta from parent C seal c826 is limited to `run.py`, `stage_c.py`,
`forecast.py`, and five new diagnostic/regression files; see the exact receipt/diff.
Data-producing code, resources, runtime and adopted JSON files are unchanged.

## Horizon and exact cadence

Each epoch draws 1,586,454 lines = 793,227 real + 793,227 synthetic. There are
`8 * ceil(1,586,454 / batch)` optimizer updates, with no gradient accumulation.
Each epoch has one shuffled partial batch; rounding the whole run once would be
incorrect. Frozen 128-px buckets, packed tails and draw order are unchanged.

| Width | Updates / epoch | Total updates | Full four-instrument CER + archived states |
|---|---:|---:|---|
| ×1 | 6,198 | **49,584** | 12,396 / 24,792 / 37,188 / 49,584 |
| ×1.5 | 6,198 | **49,584** | 12,396 / 24,792 / 37,188 / 49,584 |
| ×2 | 24,789 | **198,312** | 49,578 / 99,156 / 148,734 / 198,312 |

At every actual draw threshold crossing of 50,000, run eval-mode, no-decoding,
training-equivalent fp32 CPU CTC loss (blank=0, zero_infinity=True), sample-weighted
per-instrument mean. The final point is included once: **253 thresholds + final =
254 evaluations**. Threshold steps depend on where the partial batch was shuffled;
`LOSS_CADENCE.json` records the exact full list, using the frozen sampler before
training starts, and enforces each observed draw count. No guessed step cadence.
Coverage: seal04 dev **437**, seal04 test **2,253**, harvest dev **16,350**,
harvest test **52,847**: **71,887 rows** per loss pass. RNG and training mode are
restored. The append-only journal and immutable per-step results resume pending
evals without duplicate or missing points. The corrected seal04-dev epoch
selection CER diagnostic runs each epoch (eight passes; timed separately); four-panel CER runs only at the four listed
points. Test loss/CER never selects, stops, tunes or alters the schedule.

## Warning, exact recovery and evidence

The batch TERM trap is installed before Python/data startup. It persists a
job+restart-scoped request file, and never sends TERM to `srun`. The controller
starts no lane if warning is already pending. A warning during step creation is
retained until the Python lane starts. Segment polls it at optimizer boundaries;
a running loss/CER finishes its atomic publication, then the lane saves state
and exits 75 (at most one additional update if the warning arrived inside save).
Completed work returns 0. An incomplete lane's 75 requires a durable yield receipt.
Unexpected 1/137 and real errors remain failures with logs, never disguised as
successful requeues. Repeated shell TERM interrupts `wait` safely; `scontrol requeue`
is called exactly once after the child has actually exited.

The internal deadline uses the already-fixed `SLURM_TIME_FORMAT=standard` and
aligns the frozen deadline-minus-300 stop hook to the same end-minus-600 warning.
A 23h segment is below the one-day limit; a longer continuation requeues the same
job and claims, with no dependency on purged job IDs. Hard preemption can still
SIGKILL a worker. Such an allocation cannot self-record its own end: it records
job/restart/**step ID**/kernel host/CPU/GPU/start before training; the C accounting
adapter accepts only a unique, SHA-bound, terminal sacct parent+step end. Worker
ends are measured in `finally`; no controller upper-bound end is invented.
Global GPU and same-host CPU overlap checks remain, printing any conflicting pair.

Rolling full state is saved at most every 20 updates and before each evaluation:
model, optimizer, schedule, all RNG, CTC health, batch plan/cursor, exact draw chain,
epoch artifacts. PNG decoding is RNG-free; fast resume reconstructs the same batch
plan and starts loading at its cursor, restoring the saved RNG after iterator
creation. Yield checkpoints are retained using hardlinks to the atomic rolling
inode, avoiding an immediate copy. Subsequent atomic replacement retains that
old full-state inode: each graceful yield adds durable storage and is counted in
the low/expected/high scenario estimates. `STARTUP_*.json`, `CHECKPOINT_COST.json`, update timing
and loss/CER timings measure restart and save costs for the forecast refresh.

## Data reuse and qualification

Prepared005 `runtime.json` SHA256:
`21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`.
`verify.data_compatibility()` proves all audit/data-producing inputs, factory,
codec, population preparation, furniture fallback and environment are unchanged.
No audit/import/data copy is required. New full PLAN, configs and review bind the new payload. No scientific smoke carry
is valid for this selection behavior change. No B/C state can be adopted across
payloads, and no cancelled ×2 state resumes.

Local tests use real S1 updates/CTC plus the stochastic toy model: actual OS TERM
inside save/eval at all three adopted settings, full continuation-field identity,
all-panel loss equality, append-only recovery, cursor skipping, controller TERM
before/during step creation, repeated warning, genuine errors, real shell wait and
single requeue, and measured accounting ambiguity/overlap refusal. Inherited
leakage/dedupe/recipe/eval/journal/scheduler tests also run. See the release XML and
receipt. No local CUDA claim is made.

Required CUDA smoke: **six single-GPU jobs**, control+requeue at each width, each
48 updates (two epochs), tiny loss cadence every two batches, all four complete
panels. The resumed controller issues real **`scancel --batch --signal=TERM`**
after observing step ≥3; the actual batch trap/file/worker/75/Slurm requeue path
runs. No forced-step environment shortcut. At least one loss point before and
after the durable yield, then final all-panel CER. Readout requires BIT_IDENTICAL
full scientific state and every loss/CER result, actual same-job restart evidence,
measured yield state, real CUDA/six-worker profile, and hardware isolation.
Capture `sacct -D` for every restart; killed attempts need uniquely measured ends.
Readout must show seal04-dev437 identity/provenance, actual epoch timings, memory
receipts and measured save/eval/restart costs. Owner authority stands as recorded;
account the new smoke separately and compare the refreshed forecast to 82 GPU-h.

## Forecast and capacity

The current [interim forecast](evidence/STAGE_C_SEL_INTERIM_FORECAST.json) uses old
c826 four-panel measured costs **plus an unmeasured row-ratio estimate for the new
437-row epoch selection loader**. It is not new-smoke qualification or a launch
estimate. It explicitly counts eight selection passes, 23h renewals and their
startup/save cost, and retained yield full-state inodes. Low/expected/high total
is **78.284 / 81.895 / 95.497 GPU-h**; the expected estimate leaves little room
within the standing 82-GPU-h authority. New smoke must replace the selection
proxy and remeasure all costs before focused Astra. No automatic budget extension
is inferred. Full-size startup/late-resume verification and rare long CER
interruptions remain unmeasured; high is a scenario, not a bound.

See [current correction](STAGE_C_SELECTION_FIX.md) for per-width hours, renewals
and storage. The old 45–68 GPU-hour tables are superseded. The observed Stage B
hazard remains 54 PREEMPTED/NODE_FAIL over 64.3103 parent allocation hours
(0.839679/hour), from the SHA-bound accounting capture. Non-exclusive one-GPU
placement may change that rate. Three runs request 1 GPU / 24 CPUs / 110G each,
23h segments; no fourth GPU reserved, no DDP.

Retain the requested full 50k-drawn-line cadence even when evaluation exceeds
25% of training. Owner-authorized options remain coarser cadence in a new plan,
or a separately qualified full-coverage evaluator optimization; never silently
subsample. Prelaunch commands capture `df` bytes/inodes and actual user/project
quota immediately before full submit. High interim output storage is **55.753 GB**
including retained yield inodes and log allowance, plus operational headroom and
existing occupancy; arbitrary requeues can exceed that. Check real capacity,
not filesystem-wide free space alone. Unique physical-host occupancy and project
billing cannot be inferred by dividing GPU-hours by four.
