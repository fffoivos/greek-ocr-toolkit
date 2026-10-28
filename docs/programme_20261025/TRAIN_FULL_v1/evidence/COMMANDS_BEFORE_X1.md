# TRAIN_FULL_v1 — LAUNCH FIX, owner-run commands

**LAUNCH FIX READY**, pending focused Astra PASS for the new payload. Sol performed no network, SSH, Slurm, commit, push or HF action. The owner's conditional launch go remains as reported; these commands are for the coordinator to execute after focused review.

Payload **0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f**, ID **0446ee734d2c867c**. Original payload `294c3458c0d1fbbb45c61dcac2e11e8fab92f1ce10558cf9576ecccaabd30aac` is retained as `package/launch_parent_payload.json`. Exact diff, compatibility proof and test results: [LAUNCH_FIX.md](../../docs/programme_20261025/TRAIN_FULL_v1/LAUNCH_FIX.md). Historical audit/prepare/smoke instructions remain in [COMMANDS_BEFORE_LAUNCH_FIX.md](../../docs/programme_20261025/TRAIN_FULL_v1/evidence/COMMANDS_BEFORE_LAUNCH_FIX.md); do not rerun them for this operational fix.

The existing `full-v1-005-genn` prepared runtime and BIT_IDENTICAL smoke are reused **without rewriting either file**. Runtime SHA256 `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`; smoke SHA256 `19db742de50994112da04a893b6fb331f2f2daf09a8a120c21ad10b084243175`. Current counts: 793,227 unique train /16,350 dev /52,846 test; 198,312 updates, evals 50k/100k/150k/198,312. Prepare 3748345 and smoke 3748974/3748976 completed; original Astra PASS is historical evidence, not approval of the new payload.

On the Mac, from this repository:

```bash
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/package
python3 -B "$TF_LOCAL/verify.py"
TF_SHA=$(shasum -a 256 "$TF_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_SHA" = 0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f
TF_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/0446ee734d2c867c
ssh clariden "test ! -e '$TF_REMOTE' && mkdir -p '$TF_REMOTE'"
rsync -rt --partial "$TF_LOCAL/" "clariden:$TF_REMOTE/"
ssh clariden "python3 -B '$TF_REMOTE/verify.py'; sha256sum '$TF_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_LOCAL/PAYLOAD.json"
```

Require both full SHA256 values to match. In the Clariden shell:

```bash
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/0446ee734d2c867c
export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn
export TF_RUNTIME="$TF_WORK/data/prepared/runtime.json"
export TF_CONTROLS="$TF_WORK/controls/train-launchfix-001"
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
test ! -e "$TF_CONTROLS"
mkdir -p "$TF_CONTROLS"
# Copy the failed chain's claims/logs into the new evidence directory; keep originals.
cp -a "$TF_WORK/controls/train" "$TF_CONTROLS/failed-chain-evidence"
sacct -X -n -P -j 3749193,3749195,3749197   --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES > "$TF_CONTROLS/failed-chain-sacct.txt"
cat "$TF_CONTROLS/failed-chain-sacct.txt"
# Confirm 3749193 FAILED 123:0 and 3749195/3749197 CANCELLED, never started.
# If accounting is already purged, retain the coordinator's saved accounting proof.
# Never pass these failed/cancelled IDs as --prior and never overwrite their claims.
"$TF_PYTHON" -B - <<'PYCHECK'
import os
from pathlib import Path
from common import atomic, read, sha, bound
from verify import launch_compatibility, package_matches
work=Path(os.environ['TF_WORK']); runtime=Path(os.environ['TF_RUNTIME'])
assert sha(runtime)=='21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4'
smoke=work/'SMOKE_IDENTITY.json'
assert sha(smoke)=='19db742de50994112da04a893b6fb331f2f2daf09a8a120c21ad10b084243175'
r=read(runtime); s=read(smoke)
assert package_matches(r['package_sha256']) and package_matches(s['package_sha256'])
assert s['status']=='BIT_IDENTICAL' and s['mock'] is False
assert s['runtime_sha256']==sha(runtime)
assert r['train_rows']==793227 and r['horizon']['total_updates']==198312
# The reported failure was before srun; refuse unexpected partial training evidence.
for name in ('segment.pt','RUN_BINDING.json','COMPLETE.json'):
    assert not (work/'train'/name).exists(), 'Inspect unexpected training state: '+name
for name in ('control','resumed'): bound(s[name])
atomic(Path(os.environ['TF_CONTROLS'])/'LAUNCH_COMPATIBILITY.json', launch_compatibility())
print('UNCHANGED_RUNTIME_AND_REAL_SMOKE_VERIFIED')
PYCHECK
```

Give Astra the verbatim latest RESUME, [LAUNCH_FIX.md](../../docs/programme_20261025/TRAIN_FULL_v1/LAUNCH_FIX.md), exact new payload/hash and compatibility proof, 81-test XML, original review and retained CUDA smoke. No re-audit, factory import or numerical smoke is required by this format-only change; the old smoke remains explicitly inherited. Astra must certify that inheritance and issue a **new** review file `$TF_WORK/ASTRA_LAUNCH_FIX_REVIEW.json` with verdict PASS, **new** package SHA, unchanged runtime SHA, and `smoke_identity` path/SHA for the original `$TF_WORK/SMOKE_IDENTITY.json`. Preserve `$TF_WORK/ASTRA_REVIEW.json`; Sol does not fabricate approval. The new review uses the original chain review schema, with reviewer and review_record identifying the focused review.

After focused Astra PASS and within the owner's existing conditional go, refresh live scoped GPU accounting against the 350 requested GPU-h cap. Three 12-hour reservations request 36 GPU-h. Projection including the two planned restart allowances is approximately **25.02974 useful GPU-h** plus preemption/queue/production-iterator tails; the historical remaining budget is not a live balance.

```bash
TRAIN_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py"   --runtime "$TF_RUNTIME" --out "$TF_WORK/train"   --controls "$TF_CONTROLS" --segment 1 --mode train   --review "$TF_WORK/ASTRA_LAUNCH_FIX_REVIEW.json" --owner-go)
printf '%s\n' "$TRAIN_JOB"
NEXT_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py"   --runtime "$TF_RUNTIME" --out "$TF_WORK/train"   --controls "$TF_CONTROLS" --segment 2 --prior "$TRAIN_JOB" --mode train   --review "$TF_WORK/ASTRA_LAUNCH_FIX_REVIEW.json" --owner-go)
LAST_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py"   --runtime "$TF_RUNTIME" --out "$TF_WORK/train"   --controls "$TF_CONTROLS" --segment 3 --prior "$NEXT_JOB" --mode train   --review "$TF_WORK/ASTRA_LAUNCH_FIX_REVIEW.json" --owner-go)
sacct -X -n -P -j "$TRAIN_JOB,$NEXT_JOB,$LAST_JOB"   --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

Every submission runs exact `sbatch --test-only` first. The wrapper overrides relative time formatting only for its `squeue` end-time read. Active predecessors use afterok; COMPLETED/0:0 predecessors use retained sacct proof and yield checkpoint, without a purged-ID dependency. Failed parents refuse. Monitor the first log through actual trainer startup, then each durable yield and final checkpoint/eval completion; scheduler exit alone does not establish completed training. New failed/ambiguous intents are preserved and require inspection before another attempt.

LAUNCH FIX READY
