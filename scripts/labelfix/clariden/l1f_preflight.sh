#!/usr/bin/env bash
# Read-only input checks and scheduler simulation. NEVER submits a job.
set -euo pipefail
L1F_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1F_ROOT="$L1F_BASE/l1f"
L1F_VENV=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1
cd "$L1F_ROOT"
mkdir -p preflight logs
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export PYTHONPATH="$L1F_ROOT" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=''
sha256sum --check L1F_DEPLOY_SHA256.txt > preflight/deploy_before.log
sha256sum --check L1F_EXTERNAL_SHA256.txt > preflight/external_verify.log
(cd "$L1F_VENV"; sha256sum --check --quiet "$L1F_BASE/runtime/L1_scipy_SHA256.txt")
"$L1F_VENV/bin/python" -B - <<'PY'
import json, sys
from pathlib import Path
import torch, numpy, scipy, PIL
assert sys.prefix == '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1'
Path('preflight/runtime.json').write_text(json.dumps(dict(
    executable=sys.executable, prefix=sys.prefix, torch=torch.__version__,
    cuda=torch.version.cuda, numpy=numpy.__version__, scipy=scipy.__version__,
    pillow=PIL.__version__), indent=2)+'\n')
PY
"$L1F_VENV/bin/python" -B -u scripts/labelfix/clariden/l1f_run.py \
  --config config/l1f_job.json --verify-only --out preflight/verified_inputs \
  > preflight/input_verification.log 2>&1
bash -n scripts/labelfix/clariden/l1f_job.sbatch
sbatch --test-only scripts/labelfix/clariden/l1f_job.sbatch > preflight/test_only.log 2>&1
sha256sum --check L1F_DEPLOY_SHA256.txt > preflight/deploy_after.log
squeue -u fffoivos > preflight/squeue_after.txt
