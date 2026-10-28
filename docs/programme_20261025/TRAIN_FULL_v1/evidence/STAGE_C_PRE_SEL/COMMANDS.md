# Stage C — checkpoint every 50,000 drawn lines; coordinator commands only

Seal **c826ff52b1764246**; full SHA
`c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b`.
[Policy, exact delta, tests, storage and forecast](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_C_CHECKPOINTS.md).
[Previous command file preserved](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/STAGE_C_PRE_50K/COMMANDS.md).

**Fresh CUDA smoke required**: retention/recovery and completion bindings changed.
The memory-only carry helper does not apply. Preserve every old deployment and
the running/queued `full-v1-010-stage-c` smoke; do not rebind or modify its files.
Run these in Bash as coordinator. Sol has run no remote command. B2 stays skipped;
prepared005 data reused, all adopted HPs unchanged. Owner spending renewal is
recorded at 19:09; focused Astra plus final owner-go readback precedes full launch.
A new full plan cannot resume cancelled ×2 or old smoke/full training states.

## 1. Deploy immutable package — Mac, coordinator

```bash
set -euo pipefail
TF_C_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/stage_c_package
python3 -B "$TF_C_LOCAL/verify.py"
TF_C_SHA=$(shasum -a 256 "$TF_C_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_C_SHA" = c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b
TF_C_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/c826ff52b1764246
ssh clariden "test ! -e '$TF_C_REMOTE' && mkdir -p '$TF_C_REMOTE'"
rsync -rt --exclude=__pycache__ "$TF_C_LOCAL/" "clariden:$TF_C_REMOTE/"
ssh clariden "python3 -B '$TF_C_REMOTE/verify.py' && sha256sum '$TF_C_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_C_LOCAL/PAYLOAD.json"
```

Require identical full local/remote SHAs before sbatch. If the destination exists,
verify all files and reuse only identical bytes; never overwrite a different seal.
No large model/data/cache written locally. The two Stage B accounting captures in
`train_full/stage-c-evidence` are already deployed; verify them against local SHAs
and reuse unchanged. They feed the provisional restart forecast.

## 2. Fresh PLANs and proof of data reuse — Clariden

```bash
set -euo pipefail
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/c826ff52b1764246
export TF_C_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-012-stage-c-50k
export TF_C_RUNTIME=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/runtime.json
export TF_C_EVIDENCE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/stage-c-evidence
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
test "$(sha256sum "$TF_PACKAGE/PAYLOAD.json" | cut -d ' ' -f1)" = c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b
test "$(sha256sum "$TF_C_RUNTIME" | cut -d ' ' -f1)" = 21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4
test ! -e "$TF_C_WORK"
mkdir -p "$TF_C_WORK"
"$TF_PYTHON" -B - <<'PY'
import os
from pathlib import Path
from common import atomic,read,spec
from verify import data_compatibility,data_package_matches
runtime=Path(os.environ['TF_C_RUNTIME'])
assert data_package_matches(read(runtime)['package_sha256'],runtime)
atomic(Path(os.environ['TF_C_WORK'])/'DATA_REUSE.json',dict(runtime=spec(runtime),proof=data_compatibility()))
PY
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" plan --runtime "$TF_C_RUNTIME" --out "$TF_C_WORK/smoke" --smoke
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" plan --runtime "$TF_C_RUNTIME" --out "$TF_C_WORK/full"
sha256sum "$TF_C_WORK/smoke/PLAN.json" "$TF_C_WORK/full/PLAN.json"
sha256sum "$TF_C_EVIDENCE/SACCT_D_SINCE_20261022.txt" \
  "$TF_C_EVIDENCE/STAGE_B_COLLECT_ISOLATION/SACCT_ALL_STEPS_DUPLICATES.txt"
df -h "$TF_C_WORK"
```

Confirm ~52 GB scratch/quota headroom for three run outputs (8/16/28 GB planning
allowances), excluding existing datasets. SHA compatibility checks all unchanged
data-producing code, recipe lineage and codec: no re-audit/import or data copy.
Fresh configs explicitly bind retention, adopted HPs, full-horizon OneCycle,
49,584/49,584/198,312 updates and 12,691,632 draws per run. All full loss-point
steps are sampler-derived and written to each run's LOSS_CADENCE.json at startup.

## 3. Fresh-seal real TERM/requeue CUDA smoke

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" submit --plan "$TF_C_WORK/smoke/PLAN.json" \
  | tee "$TF_C_WORK/SMOKE_SUBMITTED.txt"
```

This dry-checks then submits six non-exclusive **1 GPU / 24 CPUs / 110G**, 80-minute
jobs: three width-specific uninterrupted/requeue pairs. They use full prepared
pools, six workers, 48 updates, loss+retained model archives every two updates and
final full four-panel CER. The requeue controller sends actual
`scancel --batch --signal=TERM JOBID` at step ≥3; the real batch request reaches
the optimizer boundary, commits state, returns 75 and calls Slurm requeue.
Do not send another manual requeue. At least three loss/retained checkpoints
straddle each restart. Every old attempt remains untouched.

Inspect all six allocated jobs' `scontrol show job -o JOBID` and terminal
ReqTRES/AllocTRES: require cpu=24, mem=110G, one GPU; no exclusive node request.
Placement together is permitted, not guaranteed. At most four 110G shares fit
within the reported 450G/node. Actual child/cgroup RSS and shared-node throughput
still require readback. Investigate an unexpected failure; preserve logs/claims.

After all six complete, capture **every restart duplicate and step**, then read:

```bash
TF_C_JOBS=$("$TF_PYTHON" -B - <<'PY'
import os,json
from pathlib import Path
p=Path(os.environ['TF_C_WORK'])/'smoke/submit-controls'
rows=[json.loads(f.read_text()) for f in sorted(p.glob('*.json')) if not f.name.endswith('.INTENT.json')]
assert len(rows)==6
print(','.join(r['job_id'] for r in rows))
PY
)
SLURM_TIME_FORMAT=%s sacct -D -n -P -j "$TF_C_JOBS" \
  --format=JobIDRaw,JobID,State%40,ExitCode,Start,End,ElapsedRaw,NodeList,Restarts,ReqTRES%200,AllocTRES%200 \
  > "$TF_C_WORK/SMOKE_SACCT_ALL.txt"
SLURM_TIME_FORMAT=%s sacct -D -n -P --units=K -j "$TF_C_JOBS" \
  --format=JobIDRaw,JobID,State%40,NodeList,MaxRSS,MaxRSSTask,MaxRSSNode,ReqMem,AllocTRES%200,NTasks \
  > "$TF_C_WORK/SMOKE_MEMORY.txt"
TF_C_SACCT_SHA=$(sha256sum "$TF_C_WORK/SMOKE_SACCT_ALL.txt" | cut -d ' ' -f1)
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" smoke-readout --plan "$TF_C_WORK/smoke/PLAN.json" \
  --sacct "$TF_C_WORK/SMOKE_SACCT_ALL.txt" --sacct-sha "$TF_C_SACCT_SHA" \
  --out "$TF_C_WORK/SMOKE_IDENTITY.json"
"$TF_PYTHON" -B "$TF_PACKAGE/forecast.py" --evidence "$TF_C_EVIDENCE" \
  --smoke "$TF_C_WORK/SMOKE_IDENTITY.json" --out "$TF_C_WORK/MEASURED_FORECAST.json"
sha256sum "$TF_C_WORK/SMOKE_SACCT_ALL.txt" "$TF_C_WORK/SMOKE_MEMORY.txt" \
  "$TF_C_WORK/SMOKE_IDENTITY.json" "$TF_C_WORK/MEASURED_FORECAST.json"
cat "$TF_C_WORK/SMOKE_IDENTITY.json" "$TF_C_WORK/MEASURED_FORECAST.json" "$TF_C_WORK/SMOKE_MEMORY.txt"
```

Terminal sacct records must be complete. If accounting lags, retain that capture
and write a fresh suffixed capture/readout rather than fabricating missing ends.
Readout requires BIT_IDENTICAL final model/optimizer/scheduler/RNG/cursor,
per-point model SHA/loss equality, all archive file SHAs, coverage, actual Slurm
requeue/yield, six-worker CUDA profile, global GPU and same-host CPU isolation.
Killed allocations need a unique measured Slurm step end; ambiguity fails loudly.

Report per width: `loss_checkpoint_bytes_max`, `loss_checkpoint_seconds_mean/max`,
projected 254-save hours/bytes, all-panel loss/CER/update costs, restart startup,
eval/training ratio and refreshed low/expected/high GPU-hours. New archive save
cost includes CPU transfer, serialization, fsync, rename, SHA and reload. Loss
timing excludes that cost. Confirm all six step MaxRSS readings, aggregate child/
cgroup semantics, 110G headroom and absence of OOM; sampled RSS alone may miss peaks.
Account every parent sacct -D duplicate, including initial smoke jobs, requeues
and the old still-running smoke, against the owner's renewed spending authority.

If measured eval overhead exceeds 25%, retain cadence and present options: accept
measured cost, owner-authorized coarser cadence, or separately qualified identical
full-coverage evaluator optimization. No silent subsampling or skipped tests.

## 4. Focused Astra, owner-go readback, full launch

Review packet: owner's exact checkpoint-every-50k-line brief, STAGE_C_CHECKPOINTS.md,
STAGE_C_50K.diff, both seals, 165 passing tests+cleanup, data compatibility proof,
new immutable full PLAN/configs, new actual-signal CUDA identity/retention evidence,
archive bytes/save cost, RSS/worker/cgroup evidence, forecast and spending ledger.
Scientific HPs, adopted widths/batches, model/data/codec/preprocessing, full horizon,
patience 9 vs eight epoch decisions and dev-only best selection remain identical.
254 model+codec+config archives include final; four CER full-state archives and
last/final remain, independent of metric trends. Test reporting never selects.

Only after actual focused Astra PASS and the coordinator's final owner-go readback,
write `$TF_C_WORK/ASTRA_STAGE_C.json` using actual hashes/evidence. Example schema
only; do not treat this as a PASS receipt:

```json
{
  "status": "PASS",
  "package_sha256": "c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b",
  "plan_sha256": "ACTUAL full/PLAN.json SHA",
  "smoke_sha256": "ACTUAL SMOKE_IDENTITY.json SHA",
  "budget_extension_owner_go": true,
  "owner_go_evidence": "actual owner spending renewal and authorised launch scope",
  "review_evidence": "actual focused Astra PASS including new retained checkpoints"
}
```

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" submit --plan "$TF_C_WORK/full/PLAN.json" \
  --review "$TF_C_WORK/ASTRA_STAGE_C.json" --smoke-report "$TF_C_WORK/SMOKE_IDENTITY.json" \
  | tee "$TF_C_WORK/FULL_SUBMITTED.txt"
```

Three independent non-exclusive 1-GPU/24-CPU/110G jobs, 23h segments, automatic
requeue+exact resume. No fourth idle GPU. Confirm actual resources and placement;
full jobs release their allocations at completion. Preserve the new PLAN/claims.

After all three full runs complete, capture all full-job duplicates and verify:

```bash
TF_C_FULL_JOBS=$("$TF_PYTHON" -B - <<'PY'
import os,json
from pathlib import Path
p=Path(os.environ['TF_C_WORK'])/'full/submit-controls'
rows=[json.loads(f.read_text()) for f in sorted(p.glob('*.json')) if not f.name.endswith('.INTENT.json')]
assert len(rows)==3
print(','.join(r['job_id'] for r in rows))
PY
)
SLURM_TIME_FORMAT=%s sacct -D -n -P -j "$TF_C_FULL_JOBS" \
  --format=JobIDRaw,JobID,State%40,ExitCode,Start,End,ElapsedRaw,NodeList,Restarts,ReqTRES%200,AllocTRES%200 \
  > "$TF_C_WORK/FULL_SACCT_ALL.txt"
TF_C_FULL_SHA=$(sha256sum "$TF_C_WORK/FULL_SACCT_ALL.txt" | cut -d ' ' -f1)
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c_isolation.py" --plan "$TF_C_WORK/full/PLAN.json" \
  --sacct "$TF_C_WORK/FULL_SACCT_ALL.txt" --sacct-sha "$TF_C_FULL_SHA" --out "$TF_C_WORK/FULL_ISOLATION.json"
"$TF_PYTHON" -B - <<'PY'
import os
from common import read,bound
from stage_c import checked,complete
p=checked(os.path.join(os.environ['TF_C_WORK'],'full/PLAN.json'))
for e in p['runs']:
 c=complete(e['output'],read(bound(e['config'])))
 assert len(c['loss_checkpoints'])==len(c['loss_evaluations'])==254
 assert len(c['evaluations'])==4
 print(e['name'],'COMPLETE',len(c['loss_checkpoints']),'retained model checkpoints, all SHAs verified')
PY
```

Retain all model archives, codec/config bindings and append-only loss logs. Any
50k point can later receive full CER without retraining. Reconcile measured disk,
GPU/node-hours and final loss/CER coverage; scheduler COMPLETED alone is insufficient.
