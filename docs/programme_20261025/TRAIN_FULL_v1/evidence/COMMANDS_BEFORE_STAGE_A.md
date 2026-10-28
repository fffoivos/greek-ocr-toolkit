# TRAIN_FULL_v1 — standard ×1, owner-run commands

**TRAIN_X1 READY for smoke**, pending fresh CUDA BIT_IDENTICAL, focused Astra PASS and owner go. Payload `385856ea2166d9314d65b67cb0380ba4449e80260101a7f787d95b97638faf16`, ID `385856ea2166d931`. Sol ran no remote command or job. [Plan and exact recipe](../../docs/programme_20261025/TRAIN_FULL_v1/PLAN.md), [focused diff](../../docs/programme_20261025/TRAIN_FULL_v1/X1_CHANGE.md), [verbatim correction](../../docs/programme_20261025/TRAIN_FULL_v1/OWNER_X1_CORRECTION.md).

The old ×2 chain3749250/3749252/3749256 is CANCELLED; preserve its `train`, controls, claims and checkpoints as evidence. Never resume or use its model. Audit and prepared005 data are reused read-only by exact SHA/code proof. Old ×2 smoke/review are invalid for the changed scientific recipe. All new files go under fresh `full-v1-006-x1`; an existing directory must be inspected and another fresh name chosen rather than overwritten.

## 1. Deploy and compare exact payload — Mac, owner only

```bash
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/package
python3 -B "$TF_LOCAL/verify.py"
TF_SHA=$(shasum -a 256 "$TF_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_SHA" = 385856ea2166d9314d65b67cb0380ba4449e80260101a7f787d95b97638faf16
TF_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/385856ea2166d931
ssh clariden "test ! -e '$TF_REMOTE' && mkdir -p '$TF_REMOTE'"
rsync -rt --partial "$TF_LOCAL/" "clariden:$TF_REMOTE/"
ssh clariden "python3 -B '$TF_REMOTE/verify.py'; sha256sum '$TF_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_LOCAL/PAYLOAD.json"
```

Require matching full SHA256 values. In the Clariden shell:

```bash
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/385856ea2166d931
export TF_OLD=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn
export TF_RUNTIME="$TF_OLD/data/prepared/runtime.json"
export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-006-x1
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
test ! -e "$TF_WORK"
mkdir -p "$TF_WORK/controls"
sacct -X -n -P -j 3749250,3749252,3749256 \
  --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES > "$TF_WORK/controls/cancelled-x2-sacct.txt"
cat "$TF_WORK/controls/cancelled-x2-sacct.txt"
# Coordinator verifies cancelled/terminal state; if purged use retained proof.
# Keep original cancelled model/claims/logs unchanged in TF_OLD; no --prior IDs.
"$TF_PYTHON" -B - <<'PYPROOF'
import os
from pathlib import Path
from common import atomic, read, sha, bound, spec
from verify import data_compatibility, data_package_matches, RUNTIME_SHA
from horizon import resolve
work=Path(os.environ['TF_WORK']); runtime=Path(os.environ['TF_RUNTIME'])
r=read(runtime); proof=data_compatibility()
assert sha(runtime)==RUNTIME_SHA
assert data_package_matches(r['package_sha256'], runtime)
assert not r['mock'] and r['train_rows']==793227
assert r['horizon']==resolve(read(Path(os.environ['TF_PACKAGE'])/'recipe.json'),793227)
assert r['horizon']['total_updates']==198312
assert {n:r['pools'][n]['rows'] for n in ('seal04_dev','seal04_test','harvest_dev','harvest_test')} == dict(seal04_dev=437,seal04_test=2253,harvest_dev=16350,harvest_test=52847)
assert {n:len(refs) for n,refs in r['references'].items()} == dict(seal04_dev=437,seal04_test=2253,harvest_dev=16350,harvest_test=52847)
bound(r['manifest']); bound(r['config'])
atomic(work/'DATA_REUSE.json',dict(proof=proof,runtime=spec(runtime),manifest=r['manifest'],
  cancelled_x2_attempt=str(Path(os.environ['TF_OLD'])/'train'),policy='data only; never resume x2 training or reuse x2 smoke'))
print('UNCHANGED_AUDIT_AND_PREPARED_DATA_VERIFIED; X2_SMOKE_NOT_INHERITED')
PYPROOF
```

**Instrument count correction:** 52,847 harvest-test observations /52,846 unique crops. Keep every observation, including its admitted same-split duplicate. This preserves the frozen instrument and makes 71,887 rows per evaluation; no subsampling.

## 2. CPU cadence preflight, then fresh ×1 smoke pair

The narrow-column preflight hashes/reads prepared training shards and replays exact seeded width batching without decoding pixels or running the model. It writes the exact 254-entry production loss step list, including the shuffled 22-row partial batch. Run it on a short CPU allocation:

```bash
srun --account=a0140 --partition=preemptable --nodes=1 --ntasks=1 \
  --cpus-per-task=8 --time=00:20:00 \
  "$TF_PYTHON" -B "$TF_PACKAGE/run.py" --runtime "$TF_RUNTIME" \
  --out "$TF_WORK/LOSS_CADENCE_PRODUCTION.json" --plan-only
"$TF_PYTHON" -B - <<'PYCADENCE'
import os
from pathlib import Path
from common import read
p=read(Path(os.environ['TF_WORK'])/'LOSS_CADENCE_PRODUCTION.json')
assert p['count']==len(p['steps'])==254 and p['total_updates']==198312
assert p['total_drawn_lines']==12691632 and p['steps'][-1]==198312
print(p['steps'])
PYCADENCE
SMOKE_CONTROL=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/smoke-control" \
  --controls "$TF_WORK/controls/smoke-control" --segment 1 --mode smoke-control)
SMOKE_REQUEUE=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/smoke-requeue" \
  --controls "$TF_WORK/controls/smoke-requeue" --segment 1 --mode smoke-requeue)
printf '%s\n' "$SMOKE_CONTROL" "$SMOKE_REQUEUE"
sacct -X -n -P -j "$SMOKE_CONTROL,$SMOKE_REQUEUE" \
  --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

Each submission runs exact `sbatch --test-only` first. Each smoke requests 1 GPU/24 CPUs/a0140/preemptable/80min/--requeue. Same production pools, standard ×1, six workers,2 epochs × 192 draws,6 updates. Loss-only points 2/4/6 at 128/256/384draws; full loss+CER 3/6. Smoke-requeue commits/evaluates step 3 and calls `scontrol requeue` once; restart must have SLURM_RESTART_COUNT≥1. Monitor logs through actual restart and durable COMPLETE. An 80 min deadline yield without COMPLETE does not qualify; inspect before continuation rather than fabricating completion or reusing a claim.

After both actually COMPLETE/0:0:

```bash
sacct -X -n -P -j "$SMOKE_CONTROL,$SMOKE_REQUEUE" \
  --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES > "$TF_WORK/controls/smoke-sacct.txt"
"$TF_PYTHON" -B "$TF_PACKAGE/compare.py" \
  --control "$TF_WORK/smoke-control" --resumed "$TF_WORK/smoke-requeue" \
  --out "$TF_WORK/SMOKE_IDENTITY.json"
TF_MANIFEST=$("$TF_PYTHON" -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["manifest"]["path"])' "$TF_RUNTIME")
"$TF_PYTHON" -B "$TF_PACKAGE/readout.py" --manifest "$TF_MANIFEST" \
  --runtime "$TF_RUNTIME" --smoke-control "$TF_WORK/smoke-control" \
  --out "$TF_WORK/OWNER_READOUT_X1.json"
"$TF_PYTHON" -B - <<'PYREADOUT'
import os
from pathlib import Path
from common import read
work=Path(os.environ['TF_WORK']); identity=read(work/'SMOKE_IDENTITY.json')
assert identity['status']=='BIT_IDENTICAL' and not identity['mock']
assert identity['width_mult']==1.0 and identity['loss_steps']==[2,4,6]
f=read(work/'OWNER_READOUT_X1.json')['forecasts'][0]
assert f['loss_evaluations']==254
print(f)
if f['exceeds_25_percent']:
    print('EVAL OVERHEAD EXCEEDS 25%; report measured cost and the three owner options above before launch. No silent subsampling.')
PYREADOUT
```

The readout reports actual smoke L(loss-only), C(full loss+CER), s(synchronized update seconds),254L+4C total eval seconds and ratio to198312s training seconds. Width distribution, short smoke and epoch assembly/replay remain forecast limitations. If overhead>25%, show the owner options:keep exact cadence and reserve cost; explicitly approve larger drawn-line cadence with reseal/review; or qualify complete-instrument loss optimization with exact parity. Do not silently change the scientific request. No CUDA smoke result or measured ×1 loss overhead is claimed by this local preparation.

## 3. Focused Astra review, then owner go

Supply the verbatim OWNER_X1_CORRECTION.md, current PLAN/X1_CHANGE/exact diff, seal/test XML, DATA_REUSE.json,254-entry production cadence, both CUDA logs/checkpoints/COMPLETE files, actual restart evidence, SMOKE_IDENTITY.json, OWNER_READOUT_X1.json and fresh scoped GPU accounting. Astra must review standard ×1 and every 50k **drawn lines**, RNG/mode/trajectory isolation, no decoding, complete instruments including 52847test observations, journal/restart correctness and overhead options. Original Astra ×2 PASS cannot qualify this run.

Astra/coordinator writes `$TF_WORK/ASTRA_X1_REVIEW.json` only after actual PASS, using the existing chain schema:

```json
{
  "verdict": "PASS",
  "reviewer": "Astra",
  "review_record": "actual focused review artifact path/hash",
  "package_sha256": "385856ea2166d9314d65b67cb0380ba4449e80260101a7f787d95b97638faf16",
  "runtime_sha256": "21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4",
  "smoke_identity": {"path": "actual full-v1-006-x1/SMOKE_IDENTITY.json", "sha256": "actual fresh smoke SHA256"}
}
```

This is a schema example, not an approval file to fabricate. Keep previous reviews intact. Refresh owner-scoped accounting against 350requestedGPU-h; the 119 used snapshot predates failed/cancelled chains. Two smokes reserve2.667GPU-h; production reservesN×12GPU-h with useful wall time and requested accounting reported separately. Confirm sufficient budget and owner's go for this corrected ×1 recipe and measured eval overhead.

## 4. Launch fresh ×1 state — only after fresh Astra PASS and owner go

```bash
# Execute this block only once the review is real and the owner has given go.
# No model/resume path points at TF_OLD/train.
NSEG=$("$TF_PYTHON" -B - <<'PYSEG'
import os
from pathlib import Path
from common import read
f=read(Path(os.environ['TF_WORK'])/'OWNER_READOUT_X1.json')['forecasts'][0]
assert isinstance(f['minimum_12h_segments'],int) and f['minimum_12h_segments']>=1
print(f['minimum_12h_segments'])
PYSEG
)
printf 'Measured forecast minimum: %s x 12h segments (queue/restart tails extra)\n' "$NSEG"
test ! -e "$TF_WORK/train"
test ! -e "$TF_WORK/controls/train-x1"
TRAIN_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/train" \
  --controls "$TF_WORK/controls/train-x1" --segment 1 --mode train \
  --review "$TF_WORK/ASTRA_X1_REVIEW.json" --owner-go)
printf '%s\n' "$TRAIN_JOB"
TF_PRIOR="$TRAIN_JOB"
for TF_SEG in $(seq 2 "$NSEG"); do
  TF_NEXT=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py"   \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/train"   \
  --controls "$TF_WORK/controls/train-x1" --segment "$TF_SEG" --prior "$TF_PRIOR" --mode train   \
  --review "$TF_WORK/ASTRA_X1_REVIEW.json" --owner-go)
  printf '%s\n' "$TF_NEXT"
  TF_PRIOR="$TF_NEXT"
done
sacct -X -n -P -j "$TRAIN_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

Monitor startup to verify width_mult1.0,198312horizon and the254-point actual-draw plan. Monitor rolling saves, first loss rowcounts and full checkpoints to completion. `job.sbatch` still overrides SLURM_TIME_FORMAT only on the squeue end-time read. Active predecessors use afterok; COMPLETED parents use authenticated sacct/yield proof without afterok on purged IDs. New continuations may be needed after measured tails or preemptions; add one fresh claim/segment with the same current recipe/review/output and last valid parent, within owner budget. Never relaunch an existing intent or use a cancelled ×2 parent. Scheduler exit alone is not training completion: require COMPLETE,254loss records/final draw12691632, four archived full reports and durable final step 198312.

TRAIN_X1 READY (pending fresh ×1 CUDA smoke, focused Astra PASS and owner go).
