# Stage C memory fix — coordinator commands; Sol PREPARE ONLY

New seal **515b7d86f5f5758b**; sole payload-file diff: `stage_c.sbatch` adds
`#SBATCH --mem=110G`. Driver/trainer/data/evaluator/signal code is byte-identical.
[Exact reasoning, early-stop proof and limitations](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_C_MEMORY_FIX.md).
[Previous commands, retained](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/COMMANDS_BEFORE_STAGE_C_MEMORY_FIX.md).

The existing `full-v1-010-stage-c` smoke (3756429–35) remains on its old seal,
PLANs and claims. **Do not modify its files or deployment.** Finish it and use
its old sealed readout. No new numerical CUDA smoke is required for this sole
memory directive. Host-memory capacity/headroom must still be assessed from
actual RSS including six workers; no local RSS capture exists yet. Sharing
permits, but does not guarantee, placement together or unchanged throughput.

Owner spending renewal at 19:09 is recorded in EXECUTION_STATE.md. Preserve all
accounting; focused Astra on this diff, external compatibility helper and measured
memory evidence precedes full launch. This file prepares commands only.

## 1. Deploy the new immutable seal and external helper — Mac, coordinator

```bash
set -euo pipefail
TF_C_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/stage_c_package
TF_C_HELPER_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/memory_fix/carry_smoke.py
python3 -B "$TF_C_LOCAL/verify.py"
test "$(shasum -a 256 "$TF_C_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)" = 515b7d86f5f5758be544e401ae06720e67db8b311e38ef6bcff22c649db5bf8d
test "$(shasum -a 256 "$TF_C_HELPER_LOCAL" | cut -d ' ' -f1)" = 285759afff8015b25cde60a4527d7fa394d504c4021cb4bc21c4b820eb16c62f
TF_C_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/515b7d86f5f5758b
TF_C_HELPER_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/tools/memory-fix-285759afff8015b2
ssh clariden "test ! -e '$TF_C_REMOTE' && mkdir -p '$TF_C_REMOTE'"
rsync -rt --exclude=__pycache__ "$TF_C_LOCAL/" "clariden:$TF_C_REMOTE/"
ssh clariden "test ! -e '$TF_C_HELPER_REMOTE' && mkdir -p '$TF_C_HELPER_REMOTE'"
rsync -rt "$TF_C_HELPER_LOCAL" "clariden:$TF_C_HELPER_REMOTE/"
ssh clariden "python3 -B '$TF_C_REMOTE/verify.py'; sha256sum '$TF_C_REMOTE/PAYLOAD.json' '$TF_C_HELPER_REMOTE/carry_smoke.py'"
shasum -a 256 "$TF_C_LOCAL/PAYLOAD.json" "$TF_C_HELPER_LOCAL"
```

Require matching full local/remote hashes. If a destination already exists,
verify and reuse identical bytes; never overwrite another deployment. Stage C
accounting captures already deployed in `train_full/stage-c-evidence` are reused.

## 2. Fresh full PLAN and prepared005 reuse — Clariden

```bash
set -euo pipefail
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/515b7d86f5f5758b
export TF_C_OLD_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/8b228d6e138151f4
export TF_C_OLD_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-010-stage-c
export TF_C_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-011-stage-c-mem110
export TF_C_RUNTIME=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/runtime.json
export TF_C_HELPER=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/tools/memory-fix-285759afff8015b2/carry_smoke.py
export TF_C_EVIDENCE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/stage-c-evidence
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
test "$(sha256sum "$TF_PACKAGE/PAYLOAD.json" | cut -d ' ' -f1)" = 515b7d86f5f5758be544e401ae06720e67db8b311e38ef6bcff22c649db5bf8d
test "$(sha256sum "$TF_C_HELPER" | cut -d ' ' -f1)" = 285759afff8015b25cde60a4527d7fa394d504c4021cb4bc21c4b820eb16c62f
test "$(sha256sum "$TF_C_RUNTIME" | cut -d ' ' -f1)" = 21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4
test ! -e "$TF_C_WORK"
mkdir -p "$TF_C_WORK"
"$TF_PYTHON" -B - <<'PY'
import importlib.util,os
from pathlib import Path
from common import atomic,read,spec
from verify import data_compatibility,data_package_matches
s=importlib.util.spec_from_file_location('memory_fix',os.environ['TF_C_HELPER'])
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
work=Path(os.environ['TF_C_WORK'])
atomic(work/'MEMORY_DIFF.json',m.delta(os.environ['TF_C_OLD_PACKAGE'],os.environ['TF_PACKAGE']))
runtime=Path(os.environ['TF_C_RUNTIME'])
assert data_package_matches(read(runtime)['package_sha256'],runtime)
atomic(work/'DATA_REUSE.json',dict(runtime=spec(runtime),proof=data_compatibility()))
PY
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" plan --runtime "$TF_C_RUNTIME" --out "$TF_C_WORK/full"
sha256sum "$TF_C_WORK/full/PLAN.json"
```

The fresh PLAN's payload hash binds the explicit shell memory request. No
scientific config edits, audit/import or data copy. Old full PLAN/submit claims
are preserved and superseded. No full run resumes the cancelled ×2 state.

## 3. After all six OLD smoke lanes complete: terminal accounting + memory

Write these captures in the **new** work directory. No old attempt files change.
Use actual submitted IDs from the original six claims, including requeue records.

```bash
TF_C_JOBS=$("$TF_PYTHON" -B - <<'PY'
import os,json
from pathlib import Path
p=Path(os.environ['TF_C_OLD_WORK'])/'smoke/submit-controls'
rows=[json.loads(f.read_text()) for f in sorted(p.glob('*.json')) if not f.name.endswith('.INTENT.json')]
assert len(rows)==6
print(','.join(r['job_id'] for r in rows))
PY
)
SLURM_TIME_FORMAT=%s sacct -D -n -P -j "$TF_C_JOBS" \
  --format=JobIDRaw,JobID,State%40,ExitCode,Start,End,ElapsedRaw,NodeList,Restarts,ReqTRES%200,AllocTRES%200 \
  > "$TF_C_WORK/OLD_SMOKE_SACCT_ALL.txt"
SLURM_TIME_FORMAT=%s sacct -D -n -P --units=K -j "$TF_C_JOBS" \
  --format=JobIDRaw,JobID,State%40,NodeList,MaxRSS,MaxRSSTask,MaxRSSNode,ReqMem,AllocTRES%200,NTasks \
  > "$TF_C_WORK/OLD_SMOKE_MEMORY.txt"
cat "$TF_C_WORK/OLD_SMOKE_MEMORY.txt"
TF_C_SACCT_SHA=$(sha256sum "$TF_C_WORK/OLD_SMOKE_SACCT_ALL.txt" | cut -d ' ' -f1)
TF_C_RSS_SHA=$(sha256sum "$TF_C_WORK/OLD_SMOKE_MEMORY.txt" | cut -d ' ' -f1)
"$TF_PYTHON" -B "$TF_C_HELPER" \
  --old "$TF_C_OLD_PACKAGE" --new "$TF_PACKAGE" \
  --smoke-plan "$TF_C_OLD_WORK/smoke/PLAN.json" --full-plan "$TF_C_WORK/full/PLAN.json" \
  --capture "$TF_C_WORK/OLD_SMOKE_SACCT_ALL.txt" --capture-sha "$TF_C_SACCT_SHA" \
  --rss "$TF_C_WORK/OLD_SMOKE_MEMORY.txt" --rss-sha "$TF_C_RSS_SHA" \
  --out "$TF_C_WORK/smoke-compat"
"$TF_PYTHON" -B "$TF_PACKAGE/forecast.py" --evidence "$TF_C_EVIDENCE" \
  --smoke "$TF_C_WORK/smoke-compat/SMOKE_COMPATIBLE.json" --out "$TF_C_WORK/MEASURED_FORECAST.json"
cat "$TF_C_WORK/smoke-compat/SMOKE_COMPATIBLE.json" "$TF_C_WORK/MEASURED_FORECAST.json"
```

The helper authenticates both seals and the exact single-line shell delta,
checks the new full PLAN using its own sealed checker, re-runs the **old sealed**
CUDA readout, and creates new original+derived reports. The original report is
never relabelled. Every CUDA/requeue/isolation check still executes. The derived
report records the exact source payload/report/PLAN, helper, RSS capture, new
full PLAN and unchanged numerical files. Readout fails if the smoke is incomplete,
if the runtime changed, or if the delta exceeds the 110G directive. Report paths
must be fresh; retain failures, choose a new output suffix if recapturing.

**Memory assessment:** report each lane's peak and 110G headroom. Confirm Slurm's
single-task MaxRSS includes all six children, consult cgroup/job peak/OOM logs if
available. MaxRSS is sampled; do not claim the old unlimited allocation tested a
110G limit. The helper refuses missing lane RSS or a peak at/above 110G. Missing
end/RSS records require a fresh terminal capture, not invented zeros. No current
local reading justifies a numerical host-memory footprint yet. Check actual
new-job ReqTRES/AllocTRES shows `mem=110G`, `cpu=24`, one GPU when submitted.
Memory sharing is allowed; actual co-location and throughput need observation.

**Smoke decision:** preserve the running attempt. No repeated CUDA numerical/
TERM identity pair is needed solely for `--mem`. Resource capacity assessment is
separate. If RSS/worker accounting cannot justify 110G, or any old lane fails,
use this explicit fresh-seal smoke fallback (does not touch the old attempt):

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" plan --runtime "$TF_C_RUNTIME" --out "$TF_C_WORK/smoke-mem110" --smoke
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" submit --plan "$TF_C_WORK/smoke-mem110/PLAN.json" \
  | tee "$TF_C_WORK/SMOKE_MEM110_SUBMITTED.txt"
```

Then use the previous command file's terminal captures + `smoke-readout` on that
new PLAN and fresh output names; point review/launch at its direct identity
report. This is a conditional fallback, **not** an instruction to submit another
six jobs automatically. It still requests 110G per job and exercises real TERM.

## 4. Focused Astra, then launch on the new full PLAN

Give Astra the owner brief, STAGE_C_MEMORY_FIX.md, exact one-line diff and both
seals, external helper/tests, full package test XML, DATA_REUSE, MEMORY_DIFF,
new full PLAN/configs, old actual-signal CUDA evidence and the original+derived
readouts, MaxRSS/child-memory justification, actual accounting and refreshed
forecast. Confirm full patience **9 > 8 epoch checks**, dev-only best selection,
all four archived CER states plus final/last, 12,691,632 draws and all 254 loss
points. Generic smoke text `patience 3` is two epochs + 1, not an active 8-epoch
stop threshold. Training and test reporting remain unchanged.

After actual PASS and the coordinator's final owner-go readback, write
`$TF_C_WORK/ASTRA_STAGE_C.json` with actual evidence; example fields only:

```json
{
  "status": "PASS",
  "package_sha256": "515b7d86f5f5758be544e401ae06720e67db8b311e38ef6bcff22c649db5bf8d",
  "plan_sha256": "ACTUAL SHA OF NEW full/PLAN.json",
  "smoke_sha256": "ACTUAL SHA OF smoke-compat/SMOKE_COMPATIBLE.json",
  "budget_extension_owner_go": true,
  "owner_go_evidence": "actual owner renewal/go evidence and authorised scope",
  "review_evidence": "actual focused Astra PASS including memory-only compatibility/RSS"
}
```

This example is not a PASS receipt. Then:

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" submit --plan "$TF_C_WORK/full/PLAN.json" \
  --review "$TF_C_WORK/ASTRA_STAGE_C.json" \
  --smoke-report "$TF_C_WORK/smoke-compat/SMOKE_COMPATIBLE.json" \
  | tee "$TF_C_WORK/FULL_SUBMITTED.txt"
```

The unchanged submitter dry-checks the exact sealed wrapper before submitting
three non-exclusive **1 GPU / 24 CPUs / 110G**, 23h jobs with exact resume/requeue.
If the direct new-seal fallback smoke was used, substitute its actual report in
both the Astra `smoke_sha256` and `--smoke-report`; no compatibility file is used.
No new test selection, checkpoint pruning, early stopping or scientific edits.
Record `scontrol show job -o JOBID`/sacct ReqTRES+AllocTRES after allocation and
actual node placement; never infer shared-node billing from non-exclusive alone.

At completion, retain the 11-field terminal sacct -D capture for all full jobs /
restarts and run the existing `stage_c_isolation.py` as in the archived commands.
Verify COMPLETE binds final state, 254 per-instrument loss points and all four
CER archives for each width. Reconcile actual requested resources and spend.
