# Stage B collection + B2 — OWNER/COORDINATOR COMMANDS ONLY

Offline reconciliation: **151 allocations; 26 uniquely matched recovered ends;
18 GPU and 18 same-host CPU conflicts → zero**. Original receipts are retained.
[Findings and method](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_B_COLLECT.md).
[Detailed artifact](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/STAGE_B_COLLECT_ISOLATION/RECONCILIATION_OFFLINE.json).
[Prior commands preserved](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/COMMANDS_BEFORE_STAGE_B_COLLECT.md).

The sealed payload stays `3c9e5d5f4fb8702e`, SHA256
`3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8`.
No reseal, rebind, audit/import, retraining or new CUDA smoke is required.
The passed CUDA smoke 3752522 and scientific review keep their bindings.
Review the external accounting adapter and its tests; B2 requires its own
PLAN-bound focused Astra PASS. Sol runs none of these remote commands.

Use Bash with `set -euo pipefail`. Do not overwrite previous attempts, claims,
allocation/recovery receipts or submission intents. Stage C remains deferred.

## 1. Deploy only the external adapter and small accounting evidence — Mac

```bash
set -euo pipefail
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1
TF_CAPTURE=$TF_LOCAL/evidence/STAGE_B_COLLECT_ISOLATION/SACCT_ALL_STEPS_DUPLICATES.txt
python3 -B "$TF_LOCAL/package/verify.py"
test "$(shasum -a 256 "$TF_LOCAL/package/PAYLOAD.json" | cut -d ' ' -f1)" = 3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8
test "$(shasum -a 256 "$TF_CAPTURE" | cut -d ' ' -f1)" = 8ae7b9c82a00f0b510ab881c75317e5be85f4423fd5a8567723da639fcfa56a2
# Check code SHA against the implementation receipt, then compare remote below.
python3 -B - <<'PYVERIFY'
import hashlib,json
from pathlib import Path
p=Path('docs/programme_20261025/TRAIN_FULL_v1')
r=json.loads((p/'evidence/STAGE_B_COLLECT_ISOLATION/IMPLEMENTATION_RECEIPT.json').read_text())
assert hashlib.sha256((p/'collection/reconcile.py').read_bytes()).hexdigest()==r['tool']['sha256']
print('EXTERNAL_TOOL_LOCAL_SHA_VERIFIED')
PYVERIFY
TF_COLLECT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/tools/stage-b-collect-v1
ssh clariden "test ! -e '$TF_COLLECT' && mkdir -p '$TF_COLLECT'"
rsync -rt "$TF_LOCAL/collection/reconcile.py" "$TF_CAPTURE" \
  "$TF_LOCAL/evidence/STAGE_B_COLLECT_ISOLATION/IMPLEMENTATION_RECEIPT.json" "clariden:$TF_COLLECT/"
ssh clariden "sha256sum '$TF_COLLECT/reconcile.py' '$TF_COLLECT/SACCT_ALL_STEPS_DUPLICATES.txt'"
shasum -a 256 "$TF_LOCAL/collection/reconcile.py" "$TF_CAPTURE"
```

Require both hashes identical. The adapter is outside `pkg/`; nothing under
the sealed package is copied over or changed. If this deployment directory
already exists, verify its bytes and reuse only if identical.

## 2. Authenticate live plan + reconcile + collect — Clariden

```bash
set -euo pipefail
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/3c9e5d5f4fb8702e
export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-009-stage-b-h1
export TF_COLLECT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/tools/stage-b-collect-v1
export TF_SACCT=$TF_COLLECT/SACCT_ALL_STEPS_DUPLICATES.txt
export TF_SACCT_SHA=8ae7b9c82a00f0b510ab881c75317e5be85f4423fd5a8567723da639fcfa56a2
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
"$TF_PYTHON" -B - <<'PYVERIFY'
import os,json,hashlib
from pathlib import Path
p=Path(os.environ['TF_COLLECT'])
r=json.loads((p/'IMPLEMENTATION_RECEIPT.json').read_text())
assert hashlib.sha256((p/'reconcile.py').read_bytes()).hexdigest()==r['tool']['sha256']
assert hashlib.sha256(Path(os.environ['TF_SACCT']).read_bytes()).hexdigest()==os.environ['TF_SACCT_SHA']
PYVERIFY
# Fresh reports; preserve the original failed collection evidence.
test ! -e "$TF_WORK/collection-v1"
mkdir "$TF_WORK/collection-v1"
"$TF_PYTHON" -B "$TF_COLLECT/reconcile.py" audit --package "$TF_PACKAGE" \
  --plan "$TF_WORK/study/PLAN.json" \
  --sacct "$TF_SACCT" --sacct-sha "$TF_SACCT_SHA" \
  --report "$TF_WORK/collection-v1/RECONCILIATION_AUDIT.json"
"$TF_PYTHON" -B "$TF_COLLECT/reconcile.py" collect --package "$TF_PACKAGE" \
  --plan "$TF_WORK/study/PLAN.json" \
  --sacct "$TF_SACCT" --sacct-sha "$TF_SACCT_SHA" \
  --report "$TF_WORK/collection-v1/RECONCILIATION_COLLECT.json"
```

Default study PLAN SHA is pinned to
`01cc2ae0bb09d2b61d3b6a7fc15627366d3a131e385efe30028e82cb81903f38`.
The live path verifies runtime, Stage A, trial, payload and result byte bindings.
The tool calls the sealed checker and `stage_b.collect(..., fixture=False)`;
it never collects from copied evidence. It writes `study/ISOLATION.json` with
the live reconciliation SHA and the original per-width `results.jsonl` files.
Any ambiguous parent/step or remaining overlap stops with the relevant file
or exact conflicting pair. Inspect it; do not relax isolation.

## 3. Analyze w1 / w1.5 / w2

```bash
for TF_WIDTH in 1 1.5 2; do
  "$TF_PYTHON" -B "$TF_PACKAGE/study/analyze_study.py" \
  "$TF_WORK/study/w$TF_WIDTH/results.jsonl" \
  --space "$TF_PACKAGE/study/lr_space.json" --objective val_error \
  --plots "$TF_WORK/study/w$TF_WIDTH/plots" \
  > "$TF_WORK/collection-v1/ANALYSIS-w$TF_WIDTH.txt"
done
```

Omit `--scientific` entirely. Objective is FINAL pooled dev CER (sum edits /
sum reference NFD units over seal04 dev and harvest dev). Keep both panels
separate in readout too. Review infeasible trials, boundaries, density and
train/dev curves before B2. CER was measured only at the end; there is no
retrospective best_step observation. No test-set selection or evaluation.
A range extension is a new study; no settings are silently changed.

## 4. B2 seed plans — same sealed stage_b.seeds(), with reconciliation

```bash
# Fresh output claims, never a resume of a study model.
test ! -e "$TF_WORK/b2"
"$TF_PYTHON" -B "$TF_COLLECT/reconcile.py" seeds --package "$TF_PACKAGE" \
  --plan "$TF_WORK/study/PLAN.json" --out "$TF_WORK/b2" \
  --sacct "$TF_SACCT" --sacct-sha "$TF_SACCT_SHA" \
  --report "$TF_WORK/collection-v1/RECONCILIATION_SEEDS.json"
TF_B2_PLAN_SHA=$(sha256sum "$TF_WORK/b2/PLAN.json" | cut -d ' ' -f1)
export TF_B2_PLAN_SHA
printf '%s\n' "$TF_B2_PLAN_SHA"
```

This invokes the original `stage_b.py` **seeds()** implementation and its
internal collector under the same evidence adapter. Raw `stage_b.py seeds`
without the adapter would repeat the recovery upper-bound rejection. The
output is nine fresh runs (seeds 0/1/2 × three widths), groups 4/4/1, original
short horizon/dev-only cadence and unchanged per-width batch/optimizer choice.

Give Astra the actual results, diagnostics/curves, reconciliation and adapter,
tests, existing valid CUDA smoke, B2 PLAN and current accounting. Record the
actual focused PASS at `$TF_WORK/ASTRA_B2.json`, with
`package_sha256=3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8`,
`plan_sha256=$TF_B2_PLAN_SHA`, `smoke_sha256=842bb11af2f00c318f48716b523eb128dc41fde55508bc89154854a96ff4d37f`,
author and review evidence. Never manufacture PASS.

## 5. B2 submit with an explicit 8-hour override — after review/budget gate

The warning shifts from 1h50 to 7h50, beyond measured B2 duration (nine-run cost
projection 9.99 GPU-h). It avoids the observed deadline-warning failure provided
trials finish before 7h50; no payload change is made. It does not repair future
warning/preemption paths. Nine GPUs ×8h = 72 requested GPU-h; three exclusive
4-GPU nodes ×8h = 96 GPU-h conservatively, plus requeues/retries. Refresh the wave
ledger against 350 before submission; no additional budget is assumed.

```bash
TZ=UTC sacct -X -n -P --user="$USER" --account=a0140 --starttime=2026-10-22T13:43:45 \
  --format=JobIDRaw,JobName,Partition,State,ExitCode,ElapsedRaw,TimelimitRaw,ReqTRES,AllocTRES \
  > "$TF_WORK/collection-v1/ACCOUNTING_BEFORE_B2.txt"
# Same sealed submit() gates, dry checks, intent/claim protocol, with
# --time=08:00:00 inserted in EVERY effective sbatch command.
"$TF_PYTHON" -B "$TF_COLLECT/reconcile.py" submit-b2 --package "$TF_PACKAGE" \
  --plan "$TF_WORK/b2/PLAN.json" --plan-sha "$TF_B2_PLAN_SHA" \
  --review "$TF_WORK/ASTRA_B2.json" --smoke-report "$TF_WORK/SMOKE_IDENTITY.json" \
  > "$TF_WORK/collection-v1/B2_JOB_IDS.txt"
```

The adapter submits groups 0/1/2 with GPU counts 4/4/1 and CPU counts
96/96/24. Each effective command includes `sbatch --time=08:00:00` before
the unchanged sealed arguments and retains Astra gating and idempotency. Original sealed receipts remain under
`b2/submit-controls/group-NNN.json`. Exact effective commands, tool/review/plan
bindings and scheduler IDs are additionally under
`b2/submit-controls/time-override/group-NNN.{INTENT.json,json}`. Inspect both;
an incomplete intent requires scheduler reconciliation before a retry.
No afterok dependencies or purged-ID assumptions. Monitor all jobs to actual
completion and inspect trial COMPLETE/journals/accounting before adoption.

After B2 completes, capture accounting for ALL original and B2/retry jobs
with `SLURM_TIME_FORMAT=%s sacct -D -n -P`, field order
`JobIDRaw,JobID,State,ExitCode,Start,End,ElapsedRaw,NodeList,Restarts,ReqTRES,AllocTRES`.
Keep the original capture, use a new file and verify its SHA. The same adapter
supports `collect --plan "$TF_WORK/b2/PLAN.json" --plan-sha "$TF_B2_PLAN_SHA"`
and `adoption --plan ... --plan-sha ... --out "$TF_WORK/ADOPTION.json"`, each
with `--package`, the new `--sacct`, `--sacct-sha`, and fresh `--report`.
Adoption authenticates/recollects BOTH parent and B2 plans and keeps separate
reconciliation reports by PLAN SHA. Any B2 recovery needs its own measured
step evidence too. No Stage C launch command is included.

[Stage C warning-path design, not implemented](../../docs/programme_20261025/TRAIN_FULL_v1/STAGE_C_DEADLINE_DESIGN.md).

STAGE B COLLECT READY
