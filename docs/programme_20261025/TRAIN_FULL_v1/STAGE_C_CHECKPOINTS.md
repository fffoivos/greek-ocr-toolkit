# Stage C — retain every 50,000-line model checkpoint (prepare only)

New seal **c826ff52b1764246** (full SHA256
`c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b`).
This supersedes `515b7d86f5f5758b` for future plans. It does not touch the old
running/queued smoke, its deployment, plans, claims or outputs. Sol performs no
remote commands, submissions, transfers, commits, pushes or HF actions.

## Retention and loading

Every loss point now has an immutable `loss_checkpoints/step-NNNNNNNNN.pt`.
There are **254 archives/run inclusive of final**: floor(12,691,632/50,000) =
253 threshold crossings, plus the final point. There is no extra 255th identical
final archive. Counts refer to all real+synthetic draws, measured from actual
packed/shuffled batches, including partial batches. A threshold is evaluated at
the first completed update crossing it; the logged draw count may exceed it by
less than a batch. Loss point step lists are generated from the frozen sampler
in `LOSS_CADENCE.json`, never approximated as step × nominal batch size.
The horizon remains 49,584 / 49,584 / 198,312 updates and 12,691,632 draws/run.

Each model archive includes FP32 model state (parameters and buffers), all parsed
training configuration, embedded exact codec JSON+SHA, architecture, width, head,
class count, seed, step, actual drawn lines, runtime SHA, package SHA and model
state SHA. It loads with `torch.load(..., map_location='cpu', weights_only=True)`;
the frozen `ckpt_io.load_model_weights()` also accepts its `model` wrapper and
architecture metadata. Instantiate the unchanged compact model with the embedded
`n_classes`, `arch`, `width_mult`, load `model` strictly, and use the embedded
codec for decoding. The package SHA identifies the frozen code required to score
it. No dependency on a mutable best/last file or continued existence of segment.pt.

**Optimizer, scheduler, RNG and iterator state are excluded from these 254 model
archives**: they are for later scoring/inference/model reuse, not exact mid-run
continuation. This avoids duplicating AdamW moments 254 times. Exact continuation
still uses full-state `segment.pt` saved at most 20 updates apart, all evaluation
boundaries, epochs, TERM/yield and final. The four 25/50/75/100% full-state CER
archives and final/last/best files remain retained unconditionally. Test metrics
remain reporting only; no change to selection, schedule or early stopping.

## Crash ordering and exactly-once retention

Under the existing per-run exclusive file lock: commit full segment → CPU-copy
weights → temporary archive → file fsync → atomic rename → directory fsync →
SHA/reload validation → full-coverage loss evaluation → immutable point JSON →
append-only JSONL index → directory fsync → allow next update. Loss point JSON
and journal carry the retained archive path, bytes and **file SHA**, plus the
model-state SHA of the exact evaluated model. No RNG draw or model-mode change
is made by serialization. Evaluation still restores RNG and model mode.

A kill before rename leaves only a temporary file, which recovery completes.
A kill after rename but before loss/log publication reuses and validates the
same inode/bytes; it does not re-save. A kill after point JSON but before journal
append reconciles the append-only index. A missing/corrupt historical archive,
changed config/model/runtime/package/codec, duplicate point or binding mismatch
fails. Final completion binds all 254 archives, all loss records, the journal and
CER records; cached completion rechecks their file SHAs. No checkpoint pruning.

## Storage and save-cost forecast

The CPU model measurement serializes into RAM only; no large local model file was
written. See `evidence/STAGE_C_50K_SIZE_ESTIMATE.json` (PyTorch 2.14.1 CPU; Clariden
is still the frozen 2.11 CUDA runtime). These are byte measurements of the actual
architecture plus codec and minimal config, not scratch-I/O timings. Full config
metadata and ZIP/version overhead motivate the rounded planning allowance.

| Width | tensor bytes | in-RAM serialized MB | 254 measured-size GB | conservative archive MB / total GB | total run scratch provision |
|---|---:|---:|---:|---:|---:|
| ×1 | 15,107,272 | 15.183 | 3.856 | 20 / 5.080 | 8 GB |
| ×1.5 | 33,581,320 | 33.657 | 8.549 | 41 / 10.414 | 16 GB |
| ×2 | 59,336,008 | 59.411 | 15.091 | 70 / 17.780 | 28 GB |

Decimal units. Total run provisions (52 GB for all three) allow space for the
four full-state CER copies, segment, best/last, existing content-addressed epoch
artifacts, prediction files and metadata. They are conservative capacity planning,
not measured peak occupancy; datasets/prepared pools are existing shared storage
and excluded. Confirm scratch quota before launch. Stage B's 57.4 MB ×1 state
included optimizer/resume state; the new model-only archive is smaller.

Local RAM serialization took ~0.007/0.011/0.017 s; this excludes GPU→CPU transfer,
filesystem fsync, hashing and reload, so it cannot predict Clariden save time.
Until the new smoke, use **1 s/archive** as an explicitly unmeasured sensitivity:
254 s = 0.07056 GPU-h/run, 0.21167 GPU-h total. At 5 s, the additional total is
1.0583 GPU-h. `checkpoint_save` measures the entire copy/save/fsync/SHA/reload call
at each point; the smoke reports mean/max/bytes and `forecast.py` consumes those
new-seal measurements. Loss timing excludes retention, preventing double counting.
The forecast now also counts a conservative upper bound of additional durable
segment saves at loss/CER/epoch boundaries (overlapping triggers may coalesce).
Recovery validates historical archive contents, so late-run cold resume may read
up to the accumulated model-archive size. The tiny smoke measures near-start
resume, not that full-history tail; its restart estimate is therefore incomplete
for cold late-run storage validation. Preserve startup timings throughout C and
refresh the forecast if they grow. No late-run resume-I/O bound is claimed.

| Width | training GPU-h | low | expected | high |
|---|---:|---:|---:|---:|
| ×1 | 8.28 | 13.27 | 13.81 | 19.64 |
| ×1.5 | 9.57 | 15.01 | 15.63 | 22.31 |
| ×2 | 11.38 | 17.55 | 18.26 | 25.99 |
| total | 29.23 | 45.82 | 47.69 | 67.94 |

GPU-h = allocated single-GPU wall time excluding queue. **Provisional**, using
old dev-only eval row-scaling, 1 s/archive, .15 s/segment and startup sensitivities;
see SHA-bound `evidence/STAGE_C_50K_FORECAST.json`. Expected interruption hazard
remains 0.83968/node-hour from every Stage B sacct duplicate; high doubles it.
Single-GPU shared-node scheduling may change that hazard and throughput. High is
a scenario, not a bound. The owner renewed spending at 19:09; preserve the old
437.63 GPU-h ledger and account for every subsequent smoke/requeue allocation.
All-panel evaluation remains projected >25% of training time; retain the owner's
cadence. Present measured cost, a possible owner-authorized coarser cadence, or a
qualified evaluator optimization; never silently subsample.

## Seal delta, smoke and review

`evidence/STAGE_C_50K.diff` is the exact code delta against preserved
`evidence/STAGE_C_PRE_50K/`. Changed existing payload files: `full_hook.py`
(retention/recovery binding), `loss_journal.py` (archive reference), `stage_c.py`
(bound retention policy, completion/readout checks and measured costs),
`forecast.py` (retention/storage/save costs). Added: `loss_checkpoint.py` and
`tests/test_loss_checkpoints.py`. PAYLOAD is resealed. All vendor/trainer/model,
data-producing code, adopted HPs, codec, preprocessing, furniture fallback,
resource wrapper (110G), signal/requeue code and runtime environment are identical.

**A fresh six-lane CUDA smoke is required.** Archive publication/recovery,
completion validation, measured retention I/O and configuration bindings changed;
the memory-only carry helper cannot certify this delta. Keep the existing old
smoke untouched; finish/read it with its original deployment. New plans/claims
use `full-v1-012-stage-c-50k`. New smoke: three uninterrupted/requeue pairs,
≥3 retained loss points straddling actual batch TERM → full-state save → exit 75
→ Slurm requeue, BIT_IDENTICAL final trajectory and per-point losses/models.
Readout validates all archive SHAs, RNG state, CUDA/six workers, full coverage,
measured restart cost, host/GPU isolation and retained points. It also measures
host RSS under the explicit 110G request; check child/cgroup accounting and OOMs.

Local tests exercise all widths with SIGKILL after archive publication and after
loss logging, interrupted temporary writes, immutable inode/mtime/SHA on recovery,
weights-only loading, corruption refusal, coverage and cost accounting. Existing
actual OS TERM, real batch shell and eight-worsening-epoch regressions remain.
Final test counts and cleanup are recorded in STAGE_C_50K_RECEIPT.json. An initial
full-suite pass was invalidated by finalizing the archive provenance field while
tests were running; its seal-mismatch failures are retained as superseded evidence.
The release suite is rerun against a stable verified seal.

Focused Astra must review this exact delta, new PLAN/configs, tests, data reuse,
real-signal new-seal CUDA readout, MaxRSS/cgroup evidence and refreshed save/eval/
preemption forecast before full launch. `prepared005` remains reusable: its
SHA-bound compatibility function still proves every data-producing byte unchanged.
No re-audit/import, no old-state resume, no scientific HP change. Exact deploy →
fresh plans → smoke → capture/readout/forecast → Astra → owner-go/launch commands
are in `out/TRAIN_FULL_v1/COMMANDS.md`.
