# Stage B — OWNER/COORDINATOR COMMANDS ONLY

Prepared package ID `f3944e2a242e83de`, full SHA `f3944e2a242e83def0ff86a034c7f1e64bb30276a1c52ed5e291b441e162dd17`. [Study/recipe/budget](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_B.md). [Offline tests](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/TESTS_STAGE_B_FINAL.xml):120passed. Sol executes none of these remote commands. Full C runs remain deferred until B/B2 decisions and a separate reviewed package. Historical Stage A commands are [preserved](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/COMMANDS_BEFORE_STAGE_B.md).

## 1. Deploy — Mac, owner/coordinator only

```bash
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/package
python3 -B "$TF_LOCAL/verify.py"
TF_SHA=$(shasum -a 256 "$TF_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_SHA" = f3944e2a242e83def0ff86a034c7f1e64bb30276a1c52ed5e291b441e162dd17
TF_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/f3944e2a242e83de
ssh clariden "test ! -e '$TF_REMOTE' && mkdir -p '$TF_REMOTE'"
rsync -rt --partial --exclude='__pycache__' --exclude='*.pyc' "$TF_LOCAL/" "clariden:$TF_REMOTE/"
ssh clariden "python3 -B '$TF_REMOTE/verify.py'; sha256sum '$TF_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_LOCAL/PAYLOAD.json"
```

Require identical full hashes. Never deploy over an existing payload directory. Clariden shell:

```bash
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/f3944e2a242e83de
export TF_RUNTIME=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/runtime.json
export TF_STAGE_A=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-007-stage-a/stage-a/STAGE_A.json
export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-008-stage-b
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
    policy='original audit/runtime/pools only; no old smoke/review/model state inherited'))
print('PREPARED005_DATA_REUSE_VERIFIED')
PYDATA
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" plan --runtime "$TF_RUNTIME" \
  --stage-a "$TF_STAGE_A" --out "$TF_WORK/smoke" --smoke
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" plan --runtime "$TF_RUNTIME" \
  --stage-a "$TF_STAGE_A" --out "$TF_WORK/study"
```

Planning refuses the old local PREPARED_NOT_MEASURED placeholder, wrong data, failed Stage A isolation or different adopted batches. The original audit and preparation are reused unchanged; no audit/rebind/import command is needed. Frozen trainer source restoration proves the beta1-only addition does not change data production. All consumed pool bytes are rehashed. Preserve every earlier failed/cancelled attempt.

## 2. Four-lane CUDA smoke — real forced requeue

Refresh scoped accounting before reserving GPUs. Budget cap350requested GPU-h;119used is historical. Smoke requests4GPUs×80min=5.33GPU-h. Study requests51GPUs×2h=102GPU-h (conservatively104if exclusive partial nodes account all4); B2requests9×2h=18GPU-h (conservatively24). Additional requeues/retries add reservations and must fit the remaining cap.

```bash
sacct -X -n -P --user="$USER" --account=a0140 --starttime=2026-10-25T00:00:00 \
  --format=JobIDRaw,JobName,Partition,State,ExitCode,ElapsedRaw,TimelimitRaw,ReqTRES,AllocTRES \
  > "$TF_WORK/controls/ACCOUNTING_BEFORE_SMOKE.txt"
sbatch --test-only --export=ALL --time=01:20:00 "$TF_PACKAGE/stage_b.sbatch" "$TF_WORK/smoke/PLAN.json" 0
test ! -e "$TF_WORK/controls/SMOKE_JOB_ID"
TF_B_SMOKE_JOB=$(sbatch --parsable --export=ALL --time=01:20:00 \
  --output="$TF_WORK/controls/smoke-%j.log" "$TF_PACKAGE/stage_b.sbatch" "$TF_WORK/smoke/PLAN.json" 0)
printf '%s\n' "$TF_B_SMOKE_JOB" > "$TF_WORK/controls/SMOKE_JOB_ID"
squeue -j "$TF_B_SMOKE_JOB" -o '%.18i %.12P %.14j %.10T %.10M %.6D %R'
```

Four actual widths/profiles: ×1/b256control, identical ×1/b256twin forced to yield at12, ×1.5/b256 and ×2/b64. All use6workers,24CPUs and one pinned GPU. Each40update trial evaluates complete dev loss at8/16/24/32/40 and final dev CER; no test pool. The driver lets all lanes finish/yield before real `scontrol requeue`; completed lanes validate and skip on restart. The twin resumes its own durable state. Append logs are under `smoke/runs/*/srun-*.log`. Require same Slurm job ID with increased restart count and final COMPLETED0:0.

After actual completion:

```bash
sacct -X -n -P -j "$TF_B_SMOKE_JOB" \
  --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES,AllocTRES > "$TF_WORK/controls/SMOKE_SACCT.txt"
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" smoke-readout --plan "$TF_WORK/smoke/PLAN.json" \
  --out "$TF_WORK/SMOKE_IDENTITY.json"
"$TF_PYTHON" -B - <<'PYCOST'
import os
from pathlib import Path
from common import read
s=read(Path(os.environ['TF_WORK'])/'SMOKE_IDENTITY.json')
assert s['status']=='BIT_IDENTICAL' and s['mock'] is False
assert s['isolation']['status']=='PASS' and s['test_instruments_opened']==0
assert s['loss_steps']==[8,16,24,32,40]
for r in s['costs']:
    print(r)
print('B17 GPU-h including measured dev eval:',sum(r['study17_GPU_hours'] for r in s['costs']))
print('B2 GPU-h including measured dev eval:',sum(r['seed3_GPU_hours'] for r in s['costs']))
PYCOST
```

Readout proves complete state identity, the immutable forced-yield bytes, true scheduler restart, equal loss/CER, no journal omissions/repeats and physical GPU/CPU isolation. It reports per-width complete dev eval seconds,26point trial overhead and options if overhead>25% of training. No data/cadence is silently reduced. Add startup, recurring checkpoints, final epoch diagnostic and requeue/storage overhead. If measured cost does not fit the reservation or wave budget, report/review an explicit change before launch.

## 3. Focused Astra — before study launch

Give Astra the latest owner brief verbatim, STAGE_B.md, the current sealed package and diff inventory,120test report, local mocked rehearsal, actual smoke logs/accounting/SMOKE_IDENTITY, and the frozen study PLAN.json. Focus: beta1 default/actual optimizer, exact trials/batches/horizons, dev-only paths/pooling, eval RNG/mode restore, loss journal/requeue semantics, isolation and cost/budget. No previous ×2/×1/Stage A review certifies this study.

The actual reviewer/coordinator records `$TF_WORK/ASTRA_STAGE_B.json` only after the review, with `status` equal to the actual verdict, `package_sha256` equal to the full payload SHA, `plan_sha256` equal to SHA256(study/PLAN.json), `smoke_sha256` equal to SHA256(SMOKE_IDENTITY.json), plus author/review evidence. Do not manufacture a PASS. `stage_b.py submit` requires actual PASS with those exact bindings. The owner's overnight authorization applies to the coordinator; Sol still submits nothing.

Optional Mac evidence collection, coordinator only:

```bash
TF_B_LOCAL=out/TRAIN_FULL_v1/stage_b_remote_008
mkdir "$TF_B_LOCAL"
rsync -rt --partial \
  clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-008-stage-b/ \
  "$TF_B_LOCAL/"
```

Remote checkpoints can be large; copy selected review logs/JSON rather than all weights if local storage is limited. Sol's scratch is not used for remote bulk output.

## 4. Launch all51trials — coordinator after current Astra PASS and budget check

```bash
sacct -X -n -P --user="$USER" --account=a0140 --starttime=2026-10-25T00:00:00 \
  --format=JobIDRaw,JobName,State,ExitCode,ElapsedRaw,TimelimitRaw,ReqTRES,AllocTRES \
  > "$TF_WORK/controls/ACCOUNTING_BEFORE_STUDY.txt"
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" submit --plan "$TF_WORK/study/PLAN.json" \
  --review "$TF_WORK/ASTRA_STAGE_B.json" --smoke-report "$TF_WORK/SMOKE_IDENTITY.json" \
  > "$TF_WORK/controls/STUDY_JOB_IDS.txt"
```

All13independent node jobs are dry-checked before any submission;12groups of4 plus1group of3. Each lane has a permanent scientific claim, output lock and full-state resume. Node jobs are preemptable/--requeue,2h≤24h, with format-independent deadline reads; all warning yields are requeued. Finished lanes are authenticated and skipped. No afterok dependency or purged-job assumption exists. Every submission has an intent before sbatch and durable receipt after. Repeating submit does not duplicate received jobs; an intent without a receipt blocks for scheduler reconciliation.

Inspect FAILED logs and sacct before retry. `submit` does not automatically retry a failed job ID. For a same-binding retry, coordinator may sbatch the same `stage_b.sbatch PLAN.json GROUP_INDEX`, with the original group's GPU/CPU counts and a fresh retry log/receipt; completed lanes skip, unfinished lanes resume. Never overwrite the original submission/yield/claim or change the payload in place. Changed code/data/HPs need a fresh package/plan/output directory and review. Monitor every submitted job through terminal state and artifact completion.

## 5. Collect per-width results and analyze

After all groups are terminal, collect their actual sacct records with the IDs from submit-controls/group-*.json. Collector refuses pending/interrupted lanes without a final result, changed hashes or failed hardware isolation. Explicit failed trials get null objective and their error receipts; investigate infrastructure failures before interpreting study results.

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" collect --plan "$TF_WORK/study/PLAN.json"
for TF_WIDTH in 1 1.5 2; do
  "$TF_PYTHON" -B "$TF_PACKAGE/study/analyze_study.py" \
    "$TF_WORK/study/w$TF_WIDTH/results.jsonl" --space "$TF_PACKAGE/study/lr_space.json" \
    --objective val_error --plots "$TF_WORK/study/w$TF_WIDTH/plots" \
    > "$TF_WORK/study/w$TF_WIDTH/ANALYSIS.txt"
done
```

Omit --scientific entirely. The objective is final micro-pooled NFD CER; both dev instruments also remain separate. There is no retrospective CER best_step because CER is measured only at the end. Read infeasibility/boundary/density diagnostics and train/dev loss curves before declaring winners. A boundary LR is reported; extending the range is a new study, not automatic. Test results never enter the study.

## 6. B2 — best point, fresh model seeds0/1/2 per width

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" seeds --plan "$TF_WORK/study/PLAN.json" --out "$TF_WORK/b2"
```

This creates9fresh runs in3groups(4/4/1), reuses prepared data, and binds the selected best point/parent study. Model seeds0/1/2; fixed data seed20261015. Same per-width batch, trial draws, short OneCycle and complete dev cadence. No study checkpoint is loaded. After diagnostic review, obtain focused Astra PASS for this exact new B2plan, recorded at `$TF_WORK/ASTRA_B2.json` with the same schema/current payload and smoke hash but **B2 PLAN.json hash**. Refresh budget for18requested GPU-h (conservatively24for exclusive partial nodes), plus requeues. Then:

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" submit --plan "$TF_WORK/b2/PLAN.json" \
  --review "$TF_WORK/ASTRA_B2.json" --smoke-report "$TF_WORK/SMOKE_IDENTITY.json" \
  > "$TF_WORK/controls/B2_JOB_IDS.txt"
```

After all B2jobs actually complete:

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" collect --plan "$TF_WORK/b2/PLAN.json"
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" adoption --plan "$TF_WORK/b2/PLAN.json" \
  --out "$TF_WORK/ADOPTION.json"
```

Adoption diagnostic: control(seed0)CER−best-study(seed0)CER must exceed max-minus-min of the3fresh best-point seed CERs. Report all seeds/mean, boundary flags and the unmeasured incumbent/study variance. If the rule fails, keep the control. Cneeds its own full-horizon configs, complete four-instrument cadence, smoke/review and accounting; **no C launch command is supplied here**.

STAGE B READY (actual CUDA smoke/eval overhead and focused Astra pending coordinator execution).
