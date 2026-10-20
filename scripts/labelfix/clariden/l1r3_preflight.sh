#!/usr/bin/env bash
# Run from the deployed L1R3 directory on Clariden. Never submits a job.
set -euo pipefail
L1R3_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R3_ROOT="$L1R3_BASE/l1r_sf6"
L1R3_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
cd "$L1R3_ROOT"
mkdir -p preflight logs
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export PYTHONPATH="$L1R3_ROOT" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=''
sha256sum --check L1R3_DEPLOY_SHA256.txt > preflight/deploy_before.log
sha256sum --check L1R3_EXTERNAL_SHA256.txt > preflight/external_verify.log
(
  cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1
  sha256sum --check --quiet "$L1R3_BASE/runtime/L1_scipy_SHA256.txt"
)
# Full-population evidence decoding belongs to Job 2, never this login preflight.
"$L1R3_PYTHON" -B -u scripts/labelfix/clariden/l1r_recompose_ext.py \
  --config config/l1r_job.json --verify-only --workers 4 \
  --out preflight/input_verification.json > preflight/input_verification.log
"$L1R3_PYTHON" -B - <<'PY'
import json
from pathlib import Path
from greekocr.labelfix.release_gate import policy_binding
from scripts.labelfix.clariden.l1r_recompose_ext import code_sources
Path('preflight/policy.json').write_text(json.dumps(policy_binding(), indent=2) + '\n')
Path('preflight/code_sources.json').write_text(json.dumps(code_sources(), indent=2) + '\n')
PY
bash -n scripts/labelfix/clariden/l1r_job.sbatch
bash -n scripts/labelfix/clariden/l1r2_census_job.sbatch
sbatch --test-only scripts/labelfix/clariden/l1r_job.sbatch > preflight/job1_test_only.log 2>&1
# This argument only checks the second payload. The real afterok dependency
# cannot be scheduler-validated until a real Job 1 exists; see report commands.
sbatch --test-only scripts/labelfix/clariden/l1r2_census_job.sbatch 3680629 > preflight/job2_test_only.log 2>&1
sha256sum --check L1R3_DEPLOY_SHA256.txt > preflight/deploy_after.log
squeue -u fffoivos > preflight/squeue_after.txt
