# TRAIN_FULL — Stage A first; all commands below are OWNER/COORDINATOR ONLY

STAGE A READY for measurement. Payload `0fc3d5e3e287a5787ab9d8923ca010078ffbb49b7d9bceb0c7a55919e7994d2d`, ID `0fc3d5e3e287a578`. [Measurement recipe and B/C plan](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_A.md). [Tests](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/TESTS_STAGE_A_FULL.xml): 104 passed. Sol ran no network/SSH/Slurm/HF commands. No training launch is authorized by this handoff. The earlier ×1 launch commands are [historical only](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/COMMANDS_BEFORE_STAGE_A.md); do not execute that full run before the studies.

## 1. Deploy — Mac, owner only

```bash
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/package
python3 -B "$TF_LOCAL/verify.py"
TF_SHA=$(shasum -a 256 "$TF_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_SHA" = 0fc3d5e3e287a5787ab9d8923ca010078ffbb49b7d9bceb0c7a55919e7994d2d
TF_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/0fc3d5e3e287a578
ssh clariden "test ! -e '$TF_REMOTE' && mkdir -p '$TF_REMOTE'"
rsync -rt --partial --exclude='__pycache__' --exclude='*.pyc' "$TF_LOCAL/" "clariden:$TF_REMOTE/"
ssh clariden "python3 -B '$TF_REMOTE/verify.py'; sha256sum '$TF_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_LOCAL/PAYLOAD.json"
```

Require identical full hashes. Never deploy over an existing payload directory. In the Clariden shell:

```bash
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/0fc3d5e3e287a578
export TF_RUNTIME=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/runtime.json
export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-007-stage-a
export TF_STAGE_A="$TF_WORK/stage-a"
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
test ! -e "$TF_WORK"
mkdir -p "$TF_WORK/controls"
"$TF_PYTHON" -B - <<'PYDATA'
import os
from pathlib import Path
from common import atomic, bound, read, sha, spec
from verify import data_compatibility, data_package_matches, RUNTIME_SHA
runtime=Path(os.environ['TF_RUNTIME']); r=read(runtime)
assert sha(runtime)==RUNTIME_SHA and data_package_matches(r['package_sha256'],runtime)
assert not r['mock'] and r['train_rows']==793227
bound(r['manifest']); bound(r['config'])
atomic(Path(os.environ['TF_WORK'])/'DATA_REUSE.json',dict(runtime=spec(runtime),proof=data_compatibility(),
    policy='read-only audit/runtime/pools only; no cancelled weights or previous smoke inherited'))
print('PREPARED005_DATA_REUSE_VERIFIED')
PYDATA
```

No audit/rebind/factory rerun is needed. Stage A verifies all train shard hashes on the compute node and does not open dev/test pools. Preserve cancelled ×2 chain3749250/3749252/3749256, failed launches and all historical controls. No Mac paths or old model checkpoint are passed to Stage A.

## 2. Dry check, refresh accounting, submit the measurement

One preemptable node, four GPUs, 96 reserved CPUs (24 per GPU), 3h, **12 requested GPU-h**. Runtime may be shorter; no large-batch wall-time claim precedes measurement. Refresh actual owner-scoped accounting against the350requestedGPU-h cap;119used is a stale snapshot. Check the reservation fits the remaining budget, then perform the already requested Stage A measurement. Stage A changes no production recipe and retains no checkpoints. Its tiny update path and interruption orchestration passed offline; actual four-lane CUDA execution is part of this measurement.

```bash
sbatch --test-only --export=ALL "$TF_PACKAGE/stage_a.sbatch"
test ! -e "$TF_WORK/controls/STAGE_A_JOB_ID"
STAGE_A_JOB=$(sbatch --parsable --export=ALL \
  --output="$TF_WORK/controls/stage-a-%j.log" "$TF_PACKAGE/stage_a.sbatch")
printf '%s\n' "$STAGE_A_JOB" > "$TF_WORK/controls/STAGE_A_JOB_ID"
squeue -j "$STAGE_A_JOB" -o '%.18i %.12P %.14j %.10T %.10M %.6D %R'
```

Monitor actual startup and log paths under `$TF_STAGE_A/attempts/`. Width1/1.5/2 six-worker sweeps plus width1 twelve-worker sweep run as four independent srun steps, one visible GPU each. `--exclusive --exact --gpus-per-node=1 --gpus-per-task=1 --cpus-per-task=24 --gpu-bind=single:1 --cpu-bind=cores` binds each lane. Standard native thread limits and offline runtime are inherited. More-worker sweeps for1.5/2 run only when exposed loader wait≥10%. Capacity-probe OOM is recorded and stops larger batches in that lane; other failures stop the job and preserve logs. The three-hour limit is not training time selection.

Preemption/Slurm requeue reuses completed points by exact binding and repeats incomplete disposable measurements from initialization. It does **not** claim BIT_IDENTICAL training continuation; no Stage A weights are saved. On FAILED/TIMEOUT inspect logs and sacct before retry. Do not overwrite an intent. If the binding is unchanged a new job ID can use the same stage-a output; every interrupted attempt remains named by job/restart count. Changed code/data requires a new work directory and reviewable comparison. There are no afterok dependencies or parsed Slurm time strings in Stage A.

## 3. Collect measured report and table

After actual COMPLETED0:0 and durable STAGE_A.json:

```bash
sacct -X -n -P -j "$STAGE_A_JOB" \
  --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES > "$TF_WORK/controls/STAGE_A_SACCT.txt"
"$TF_PYTHON" -B "$TF_PACKAGE/stage_a.py" readout --out "$TF_STAGE_A" \
  > "$TF_WORK/STAGE_A_TABLE.txt"
cat "$TF_WORK/STAGE_A_TABLE.txt"
"$TF_PYTHON" -B - <<'PYCHECK'
import os
from pathlib import Path
from common import read
r=read(Path(os.environ['TF_STAGE_A'])/'STAGE_A.json')
assert r['status']=='MEASURED' and r['isolation']['status']=='PASS'
assert r['checkpoints_kept']==0 and r['eval_instruments_opened']==0
assert len(r['selections'])==3
for s in r['selections']:
    print(s)
print('Training-only projections: add B CUDA-smoke dev-eval cost/startup/requeue/reservation before requesting study budget.')
PYCHECK
```

The report includes lines/s, memory, GPU utilization, loader wait, chunk rates/CV, selected batch/workers, and Stage B/seed/full training-only GPU-hours per width. Choose batch by≥5% gain over last accepted smaller batch; choose12workers only for≥5% gain. Timing noise near that threshold warrants a repeat; report it. Four-lane UUID/CPU separation is attested; shared storage/memory contention remains a measured condition.

Owner/coordinator may copy results back from the Mac (Sol does not execute this):

```bash
TF_RESULT_LOCAL=out/TRAIN_FULL_v1/stage_a_measured_007
mkdir "$TF_RESULT_LOCAL"
rsync -rt --partial \
  clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-007-stage-a/ \
  "$TF_RESULT_LOCAL/"
```

## 4. B then C — pending packages, not executable launch commands

Provide measured STAGE_A.json, table, logs, scheduler accounting and full payload hash to the coordinator. Then prepare the51trial per-width study package at the selected batches, with beta1 flag, dev-only loss/eval, final pooled dev CER, per-trial exact-resume claims, four-lane CUDA smoke with forced requeue BIT_IDENTICAL, measured dev-evaluation overhead, refreshed budget and focused Astra PASS before launch. Existing16Halton points/seed20261025 plus unscaled S1 control apply per width; ranges/extensions are explicit. Analyze each width's results.jsonl with the nn-tuning analyze_study.py `--objective val_error`, omitting `--scientific`. Seeds0/1/2 of the best point precede adoption. Full runs wait for those results and fresh Astra/owner go. See the [B/C plan](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_A.md) for exact drawn-line horizons, pooling and checkpoint semantics.

STAGE A READY (and B/C plan; CUDA measurements pending coordinator execution).
