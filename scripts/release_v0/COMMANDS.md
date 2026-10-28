# REL0-S1 coordinator commands — 28 October 2026, Europe/Athens

These commands are for the coordinator. Sol has performed no SSH, network access,
processing of real lines, or scheduler submission. The Mac runs tiny tests only.
The two tools use the same JSON run list. Use a new output directory for each
analysis attempt; CPU and GPU speed jobs for that attempt share it and write
separate files. Never point `--out` into a run, package, or data directory.

## Local tests and deployment (Mac, repository root)

```bash
REL0_LOCAL_PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
PYTHONDONTWRITEBYTECODE=1 "$REL0_LOCAL_PY" -B -m pytest -q -p no:cacheprovider \
  --confcutdir=tests/release_v0 --basetemp=/tmp/rel0-s1-pytest \
  tests/release_v0/test_analyze_models.py
# Only after PASS: remove this test suite's disposable tiny fixture directory.
"$REL0_LOCAL_PY" -B - <<'PY'
from pathlib import Path
import shutil
p = Path('/tmp/rel0-s1-pytest')
assert p.name == 'rel0-s1-pytest' and p.parent == Path('/tmp')
shutil.rmtree(p)
assert not p.exists()
PY
bash -n scripts/release_v0/analyze.sbatch scripts/release_v0/bench.sbatch

# CLARIDEN is the coordinator's configured SSH host alias.
CLARIDEN=clariden
REL0_REMOTE_CODE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/code/rel0-s1-20261028
REL0_TRANSFER=$(mktemp -d /tmp/rel0-s1-deploy.XXXXXX)
cat > "$REL0_TRANSFER/FILES.txt" <<'EOF'
scripts/release_v0/analyze_models.py
scripts/release_v0/bench_speed.py
scripts/release_v0/analyze.sbatch
scripts/release_v0/bench.sbatch
scripts/release_v0/COMMANDS.md
tests/release_v0/test_analyze_models.py
EOF
while IFS= read -r f; do shasum -a 256 "$f"; done \
  < "$REL0_TRANSFER/FILES.txt" > "$REL0_TRANSFER/SHA256SUMS"
ssh "$CLARIDEN" "mkdir -p '$REL0_REMOTE_CODE'"
tar -cf - -T "$REL0_TRANSFER/FILES.txt" | \
  ssh "$CLARIDEN" "tar -xf - -C '$REL0_REMOTE_CODE'"
scp "$REL0_TRANSFER/SHA256SUMS" "$REL0_TRANSFER/FILES.txt" \
  "$CLARIDEN:$REL0_REMOTE_CODE/"
# Exact local/deployed comparison; all lines must be OK before any sbatch.
ssh "$CLARIDEN" "cd '$REL0_REMOTE_CODE' && sha256sum -c SHA256SUMS"
ssh "$CLARIDEN" "cd '$REL0_REMOTE_CODE' && xargs sha256sum < FILES.txt" \
  > "$REL0_TRANSFER/REMOTE_SHA256SUMS"
diff -u "$REL0_TRANSFER/SHA256SUMS" "$REL0_TRANSFER/REMOTE_SHA256SUMS"
```

Do not edit deployed sources after the comparison. If a source changes, redeploy
and repeat the full comparison. Keep the SHA files as deployment evidence.

## Run lists (Clariden login shell; configuration only)

```bash
export REL0_PYTHON=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
REL0_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0
REL0_CODE=$REL0_ROOT/code/rel0-s1-20261028
mkdir -p "$REL0_ROOT/config"
"$REL0_PYTHON" -B - "$REL0_ROOT/config" <<'PY'
import json
from pathlib import Path
import sys
root = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full')
config = Path(sys.argv[1])
now = [dict(label=label, width_mult=width,
            run_dir=str(root / 'attempts/full-v1-013-stage-c-sel/full/runs' / label),
            package=str(root / 'pkg/7e8a497f21527b90'))
       for label,width in [('w1.5-full',1.5), ('w2-full',2.0)]]
later = now + [dict(label='w1h14-full', width_mult=1.0,
                   run_dir=str(root / 'attempts/full-v1-014-w1-h14/full/runs/w1-full'),
                   package=str(root / 'pkg/e808f6ffe1363bd0'))]
for name,runs in [('runs-now.json',now),('runs-all-three.json',later)]:
    (config/name).write_text(json.dumps(runs,indent=2)+'\n')
PY
REL0_RUNS=$REL0_ROOT/config/runs-now.json
REL0_DATA=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared
REL0_OUT=$REL0_ROOT/analysis/2026-10-28/attempt-01
mkdir -p "$REL0_OUT/logs"
cd "$REL0_CODE"
sha256sum -c SHA256SUMS
sha256sum "$REL0_RUNS" > "$REL0_OUT/RUN_LIST_SHA256.txt"
bash -n scripts/release_v0/analyze.sbatch scripts/release_v0/bench.sbatch
"$REL0_PYTHON" -B scripts/release_v0/analyze_models.py --help
"$REL0_PYTHON" -B scripts/release_v0/bench_speed.py --help
```

After ×1 h14 is complete and the coordinator's step-0 verification has passed,
repeat the jobs below with these variables (same code, all three pairs recomputed):

```bash
REL0_RUNS=$REL0_ROOT/config/runs-all-three.json
REL0_OUT=$REL0_ROOT/analysis/2026-10-29/attempt-01
mkdir -p "$REL0_OUT/logs"
cd "$REL0_CODE"
sha256sum -c SHA256SUMS
sha256sum "$REL0_RUNS" > "$REL0_OUT/RUN_LIST_SHA256.txt"
```

Use the actual Europe/Athens execution date if ×1 finishes later. The retired
attempt-013 ×1 is rejected by the tool. Do not replace selected weights with a
nearby archive. Missing selected predictions stop analysis and speed resolution;
the coordinator must arrange predictions for those already fixed weights in a
separate, authorised step, preserving the input-custody records.

## Scheduler dry check and submission (Clariden, coordinator only)

Partition, time and CPUs are standard `sbatch` overrides. Defaults: analysis
preemptable / 16 CPU / 2 h / no requeue; speed preemptable / 1 GPU / 8 CPU / 1 h /
no requeue. CPU speed gets its own CPU-only allocation. The wrappers do not
submit, requeue, alter inputs, or write bytecode into sealed packages.

```bash
REL0_PARTITION=preemptable
REL0_ANALYSIS_CPUS=16
REL0_ANALYSIS_TIME=02:00:00
REL0_BENCH_TIME=01:00:00

sbatch --test-only --partition="$REL0_PARTITION" --cpus-per-task="$REL0_ANALYSIS_CPUS" \
  --time="$REL0_ANALYSIS_TIME" --no-requeue \
  --output="$REL0_OUT/logs/analyze-%j.out" --error="$REL0_OUT/logs/analyze-%j.err" \
  scripts/release_v0/analyze.sbatch --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT"
sbatch --test-only --partition="$REL0_PARTITION" --gpus-per-node=0 --cpus-per-task=8 \
  --time="$REL0_BENCH_TIME" --no-requeue \
  --output="$REL0_OUT/logs/cpu-%j.out" --error="$REL0_OUT/logs/cpu-%j.err" \
  scripts/release_v0/bench.sbatch --device cpu --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT"
sbatch --test-only --partition="$REL0_PARTITION" --gpus-per-node=1 --cpus-per-task=8 \
  --time="$REL0_BENCH_TIME" --no-requeue \
  --output="$REL0_OUT/logs/gpu-%j.out" --error="$REL0_OUT/logs/gpu-%j.err" \
  scripts/release_v0/bench.sbatch --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT"

# Proceed after exact deployment, input-list SHA and dry checks pass.
REL0_ANALYZE_JOB=$(sbatch --parsable --partition="$REL0_PARTITION" \
  --cpus-per-task="$REL0_ANALYSIS_CPUS" --time="$REL0_ANALYSIS_TIME" --no-requeue \
  --output="$REL0_OUT/logs/analyze-%j.out" --error="$REL0_OUT/logs/analyze-%j.err" \
  scripts/release_v0/analyze.sbatch --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT")
REL0_CPU_JOB=$(sbatch --parsable --partition="$REL0_PARTITION" --gpus-per-node=0 \
  --cpus-per-task=8 --time="$REL0_BENCH_TIME" --no-requeue \
  --output="$REL0_OUT/logs/cpu-%j.out" --error="$REL0_OUT/logs/cpu-%j.err" \
  scripts/release_v0/bench.sbatch --device cpu --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT")
REL0_GPU_JOB=$(sbatch --parsable --partition="$REL0_PARTITION" --gpus-per-node=1 \
  --cpus-per-task=8 --time="$REL0_BENCH_TIME" --no-requeue \
  --output="$REL0_OUT/logs/gpu-%j.out" --error="$REL0_OUT/logs/gpu-%j.err" \
  scripts/release_v0/bench.sbatch --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT")
printf '%s\n' "$REL0_ANALYZE_JOB" "$REL0_CPU_JOB" "$REL0_GPU_JOB" > "$REL0_OUT/JOB_IDS.txt"
squeue -j "$REL0_ANALYZE_JOB,$REL0_CPU_JOB,$REL0_GPU_JOB"
# Inspect logs and terminal accounting; do not treat submission as completion.
sacct -D -j "$REL0_ANALYZE_JOB,$REL0_CPU_JOB,$REL0_GPU_JOB" \
  --format=JobID,JobName,Partition,State,ExitCode,Elapsed,AllocCPUS,AllocTRES,NodeList \
  > "$REL0_OUT/ACCOUNTING.txt"
```

If a job fails or times out, inspect the phase and failure receipt/log first.
The tool does not silently lower batches, shorten the sample, or reduce repeats.
OOM is recorded as a failed case; bf16 is `UNSUPPORTED` only when the sealed
trainer's AMP helper says the device does not support it. Retry decisions and
resource changes belong to the coordinator; use a new attempt directory.

## Merge and read back (Clariden, after all three jobs have succeeded)

This merge only reads receipts and renders tables; it does not process images.

```bash
"$REL0_PYTHON" -B scripts/release_v0/analyze_models.py \
  --runs "$REL0_RUNS" --data-dir "$REL0_DATA" --out "$REL0_OUT" --collect-speed
"$REL0_PYTHON" -B - "$REL0_OUT" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
out = Path(sys.argv[1])
receipt = json.loads((out/'RECEIPT.json').read_text())
assert receipt['status'] == 'PASS'
for item in receipt['outputs']:
    p = Path(item['path'])
    assert p.stat().st_size == item['bytes']
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    assert h.hexdigest() == item['sha256']
s = json.loads((out/'SUMMARY.json').read_text())
assert s['status'] == 'PASS' and set(s['speed']) == set(s['runs'])
for label,r in s['runs'].items():
    assert len(r['trajectory']) == 4
    for device,bench in s['speed'][label].items():
        assert bench['status'] == 'PASS' and bench['repeats'] == 5
        assert bench['sample']['lines'] == 2000
        assert len(bench['cases']) == (4 if device == 'cpu' else 6)
    print(label, r['selection']['epoch'], r['selection']['step'], r['selection']['weight_sha256'])
assert s['bootstrap_resamples'] == 10000 and s['bootstrap_seed'] == 20261028
print('PASS: output hashes, selected-weight bindings, four CER steps, full speed grids, bootstrap recipe')
PY
```

Deliverables in `REL0_OUT`: `analysis_<label>.json` (selected checkpoint details,
per-line correctness and three metric edit/unit counts, four-point aggregate
trajectory, exact input/code identities), `speed_<label>_{cpu,gpu}.json`,
`SUMMARY.json` (all runs, overlap, dev-only paired bootstrap, merged speed),
`REPORT.md`, and `RECEIPT.json`. The report places dev decision evidence and
**Test — report only** in separate sections. Only dev gets three-way wrong-line
ID lists; test overlap has counts. With two runs, overlap means both and the
three-way list is explicitly pending ×1. Nothing chooses a model or threshold.

The paired bootstrap is 10,000 line draws with replacement, PCG64 seed 20261028,
corpus ratio of summed edits to summed NFD reference atoms, 2.5/97.5 percentile
interval with linear interpolation. Pooled dev combines both instruments and
namespaces their IDs; all pairs use a shared deterministic sample sequence.

Speed uses the first 2,000 harvest_dev rows in sorted shard/stored row order,
unchanged across widths, threads, precisions and batches. Five timed passes,
ten warm-up batches per case, median total seconds / 2,000 for ms/line, reciprocal
for lines/s. The final partial batch is included. Timings include in-memory PNG
decode, sealed normalisation/collation, host/device transfer, forward and CPU
greedy decoding; disk reads, model load and warm-up are excluded. CPU fp32:
1/8 threads × batches 1/32. GPU: 1 visible device, bf16/fp32 × batches 1/32/256;
one host Torch thread, interop 1, TF32 disabled. Hardware and all raw repeat
durations are in each speed receipt. CPU and GPU results are not pure-kernel
latencies. No parallel image workers or width sorting change the chosen order.

Checkpoint resolution loads only owner-custody `.pt` files, SHA-verified before
trusted pickle reads (full-state RNG/optimizer cannot use `weights_only=True`).
The sealed inference loader reads safetensors. Weight SHA is the producing
trainer's canonical v2 hash applied to a plain dictionary of independently
cloned contiguous CPU tensors, excluding format-specific container metadata;
every tensor name, dtype, shape and byte remains covered. The safetensors SHA
is recorded separately. `best.pt`, `best.safetensors`, and the selected archive
must have the same weight SHA. The selected archive's full state hash and its
eval record are also verified. The full checkpoint state SHA is a different
identity and must never be called the weight SHA.

Exactly eight ordered `SELECTION_EVAL_*` records, when available, verify strict first-minimum
selection across all eight epochs. Missing or extra records (possible after interrupted
epoch evaluations, which carry timestamps but no epoch/step) cannot be mapped safely;
in that case `checkpoint_meta`
and `best.pt` are authoritative, checked against all eight rounded CSV values;
the receipt explicitly states CSV rounding ambiguity. Missing predictions,
coverage differences, foreign package/codec/runtime/width, altered weights, or
any reproduced aggregate mismatch are fatal. No fallback archive is selected.

The attempt-014 package is not locally available to Sol. Both tools verify the
entire deployed package payload and its run binding before using its interfaces;
014 interface compatibility and actual Clariden measurements remain remote
verification work. Relevant provenance gaps are appended to the release GAPS.md.
