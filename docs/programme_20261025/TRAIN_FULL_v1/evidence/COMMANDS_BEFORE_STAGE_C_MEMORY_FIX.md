# Stage C — coordinator commands; Sol PREPARE ONLY

B2 is **skipped by owner decision**. Stage B's package, data, results and attempts
stay intact. [C recipe / recovery / cost](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_C.md).
[Previous collection/B2 commands](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/COMMANDS_BEFORE_STAGE_C.md).

**Current gate:** 437.63 GPU-h used against cap 350. Obtain owner spending renewal
before the CUDA smoke; full launch additionally requires focused Astra PASS,
measured all-panel overhead/forecast and the owner's budget-extension/go.
These commands are for the coordinator to run; none have been executed remotely.
Use Bash, preserve every earlier attempt/claim/receipt, and do not resume ×2's
cancelled training state. No new dataset audit/preparation is required.

## 1. Deploy immutable C payload — Mac, coordinator only

```bash
set -euo pipefail
TF_C_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/stage_c_package
python3 -B "$TF_C_LOCAL/verify.py"
TF_C_SHA=$(shasum -a 256 "$TF_C_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_C_SHA" = 8b228d6e138151f498b7f8ea948c516ecac0fdae65a5602000ca27d530585d4c
TF_C_ID=${TF_C_SHA:0:16}
TF_C_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/$TF_C_ID
ssh clariden "test ! -e '$TF_C_REMOTE' && mkdir -p '$TF_C_REMOTE'"
rsync -rt --exclude=__pycache__ "$TF_C_LOCAL/" "clariden:$TF_C_REMOTE/"
ssh clariden "python3 -B '$TF_C_REMOTE/verify.py'; sha256sum '$TF_C_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_C_LOCAL/PAYLOAD.json"
# Copy only the two small, immutable accounting captures, for forecast refresh.
TF_C_EVIDENCE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/stage-c-evidence
ssh clariden "test ! -e '$TF_C_EVIDENCE' && mkdir -p '$TF_C_EVIDENCE/STAGE_B_COLLECT_ISOLATION'"
rsync -rt docs/programme_20261025/TRAIN_FULL_v1/evidence/SACCT_D_SINCE_20261022.txt "clariden:$TF_C_EVIDENCE/"
rsync -rt docs/programme_20261025/TRAIN_FULL_v1/evidence/STAGE_B_COLLECT_ISOLATION/SACCT_ALL_STEPS_DUPLICATES.txt \
  "clariden:$TF_C_EVIDENCE/STAGE_B_COLLECT_ISOLATION/"
ssh clariden "sha256sum '$TF_C_EVIDENCE/SACCT_D_SINCE_20261022.txt' '$TF_C_EVIDENCE/STAGE_B_COLLECT_ISOLATION/SACCT_ALL_STEPS_DUPLICATES.txt'"
shasum -a 256 docs/programme_20261025/TRAIN_FULL_v1/evidence/SACCT_D_SINCE_20261022.txt \
  docs/programme_20261025/TRAIN_FULL_v1/evidence/STAGE_B_COLLECT_ISOLATION/SACCT_ALL_STEPS_DUPLICATES.txt
```

Require identical local/remote hashes before sbatch. If either destination exists,
verify identical bytes and reuse; never overwrite a different deployment/evidence.
No local bulk transfer, training cache or prepared data copy.

## 2. Bind fresh C plans + prove prepared005 reuse — Clariden

```bash
set -euo pipefail
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/8b228d6e138151f4
export TF_C_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-010-stage-c
export TF_C_RUNTIME=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/runtime.json
export TF_C_EVIDENCE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/stage-c-evidence
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
test "$(sha256sum "$TF_PACKAGE/PAYLOAD.json" | cut -d ' ' -f1)" = 8b228d6e138151f498b7f8ea948c516ecac0fdae65a5602000ca27d530585d4c
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
```

Keep both PLANs immutable for this binding. Runtime/pools, data seed, synthetic
sources, furniture fallback, codec and preprocessing are unchanged. New configs
bind the three exact adopted points. A prior scientific smoke/review is not reused.

## 3. Real-signal CUDA smoke — after owner spending renewal

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" submit --plan "$TF_C_WORK/smoke/PLAN.json" \
  | tee "$TF_C_WORK/SMOKE_SUBMITTED.txt"
```

This dry-checks then submits six **non-exclusive 1-GPU / 24-CPU** jobs, each 80 min:
control+requeue at each width, 48 updates, real four-panel loss every two batches,
final four-panel CER. The resumed lane's controller automatically sends actual
`scancel --batch --signal=TERM JOBID` at observed step ≥3. It exercises the real
batch warning/file/optimizer-boundary save/75/requeue path. No in-program forced
yield. Same claims and full RNG/cursor resume, no decoding of consumed prefix.
No additional manual requeue is needed. Watch per-run srun and submit-controls
logs; an unexpected error must be investigated and retained, not auto-retried.
A completed control job releases its GPU immediately.

After **all six are terminal/completed**, retain accounting for every restart:

```bash
TF_C_JOBS=$("$TF_PYTHON" -B - <<'PY'
import os,json
from pathlib import Path
p=Path(os.environ['TF_C_WORK'])/'smoke/submit-controls'
print(','.join(json.loads(f.read_text())['job_id'] for f in sorted(p.glob('*.json')) if not f.name.endswith('.INTENT.json')))
PY
)
SLURM_TIME_FORMAT=%s sacct -D -n -P -j "$TF_C_JOBS" \
  --format=JobIDRaw,JobID,State%40,ExitCode,Start,End,ElapsedRaw,NodeList,Restarts,ReqTRES%200,AllocTRES%200 \
  > "$TF_C_WORK/SMOKE_SACCT_ALL.txt"
TF_C_SACCT_SHA=$(sha256sum "$TF_C_WORK/SMOKE_SACCT_ALL.txt" | cut -d ' ' -f1)
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" smoke-readout --plan "$TF_C_WORK/smoke/PLAN.json" \
  --sacct "$TF_C_WORK/SMOKE_SACCT_ALL.txt" --sacct-sha "$TF_C_SACCT_SHA" \
  --out "$TF_C_WORK/SMOKE_IDENTITY.json"
"$TF_PYTHON" -B "$TF_PACKAGE/forecast.py" --evidence "$TF_C_EVIDENCE" \
  --smoke "$TF_C_WORK/SMOKE_IDENTITY.json" --out "$TF_C_WORK/MEASURED_FORECAST.json"
cat "$TF_C_WORK/SMOKE_IDENTITY.json" "$TF_C_WORK/MEASURED_FORECAST.json"
```

Readout requires actual Slurm restart and immutable durable yield evidence at each
width, BIT_IDENTICAL final state/loss/CER, CUDA/six-worker profile, and global GPU /
same-host CPU isolation. Killed allocations require a unique measured sacct step
end; ambiguity or overlap fails with the pair. No inferred upper-bound ends.
If sacct has a temporarily missing end, wait for its terminal record and capture
again to a fresh filename; preserve earlier capture evidence.

`costs` measures **all-panel** loss/CER, update time, checkpoint time and restart
startup. Report eval/training and active-time shares per width. Initial projection
is ~50–58% eval/training (above 25%); show measured options to the owner, retain
50k-line cadence. The refreshed forecast uses measured costs and the historical
preemption rate, with low/expected/high scenarios. Reconcile actual smoke charge
from **every sacct -D parent duplicate** and refresh the overall budget ledger.

## 4. Focused Astra + explicit owner budget-extension/go

Give Astra the owner brief verbatim, STAGE_C.md, the separate C seal and diff
inventory, release test XML, local identity evidence, DATA_REUSE, both exact PLANs,
actual signal/requeue receipts and CUDA smoke logs, complete accounting/isolation,
SMOKE_IDENTITY and MEASURED_FORECAST. Focus on request-file TERM handling (including
startup/eval), 75/requeue barrier, fast cursor RNG identity, ≤20-step durable state,
exact adopted optimizer/horizon, four-panel reporting-only tests, append-only
cadence, resource accounting and the forecast assumptions. The C signal/resume
path is new; Stage B's PASS does not certify it.

Only **after actual Astra PASS and explicit owner go covering additional spend**,
the coordinator writes `$TF_C_WORK/ASTRA_STAGE_C.json` with:

```json
{
  "status": "PASS",
  "package_sha256": "8b228d6e138151f498b7f8ea948c516ecac0fdae65a5602000ca27d530585d4c",
  "plan_sha256": "ACTUAL SHA256 OF full/PLAN.json",
  "smoke_sha256": "ACTUAL SHA256 OF SMOKE_IDENTITY.json",
  "budget_extension_owner_go": true,
  "owner_go_evidence": "exact owner instruction and approved additional GPU-h",
  "review_evidence": "path/sha of the actual focused Astra PASS"
}
```

This is a schema example, not a fabricated PASS/approval receipt. Copy actual
hashes and owner/reviewer evidence. The submission command refuses absent budget
renewal or stale plan/payload/smoke binding.

## 5. Launch exactly three fresh full runs — only after those gates

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" submit --plan "$TF_C_WORK/full/PLAN.json" \
  --review "$TF_C_WORK/ASTRA_STAGE_C.json" --smoke-report "$TF_C_WORK/SMOKE_IDENTITY.json" \
  | tee "$TF_C_WORK/FULL_SUBMITTED.txt"
```

Three independent single-GPU jobs, **23h per segment**, preemptable + requeue,
24 CPUs / six workers each, no exclusive node and no DDP. Checkpoint ≤20 updates;
loss at every actual 50k draw crossing + final (254), CER/archive at 25/50/75/100%.
If a 23h segment is insufficient, the warning path requeues the same job/state;
no `afterok` on purged IDs. Claims/intents prevent duplicate submission. Never
change a bound config or overwrite an intent after a failure; inspect retained
logs/accounting and submit any approved same-binding retry with fresh receipt.

Final verification per width: COMPLETE.json binds final full state, all 254
loss records, append-only journal and four four-panel CER archives. Capture all
full-job sacct -D steps/duplicates in the same 11-field epoch format, then:

```bash
# TF_C_FULL_SACCT must name that retained terminal full-job capture.
TF_C_FULL_SACCT_SHA=$(sha256sum "$TF_C_FULL_SACCT" | cut -d ' ' -f1)
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c_isolation.py" --plan "$TF_C_WORK/full/PLAN.json" \
  --sacct "$TF_C_FULL_SACCT" --sacct-sha "$TF_C_FULL_SACCT_SHA" --out "$TF_C_WORK/FULL_ISOLATION.json"
```

Keep final test metrics report-only; report each instrument separately and keep
the actual final checkpoint. No B2, new search, automatic range extension or
change to owner cadence is included.
