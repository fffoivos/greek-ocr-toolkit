#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=labelfix_L1R4_SF6F
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6f/logs/L1R4_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
if [[ "${L1R4_MOCK:-0}" == 1 ]]; then
  : "${L1R4_PYTHON:?}" "${L1R4_OUT:?}" "${L1R4_CONFIG:?}"
  export PYTHONPATH="$PWD"
  exec "$L1R4_PYTHON" -B -u scripts/labelfix/clariden/l1r_recompose_ext.py \
    --config "$L1R4_CONFIG" --workers 2 --audit-decisions --out "$L1R4_OUT"
fi
L1R4_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R4_ROOT="$L1R4_BASE/l1r_sf6f"
L1R4_VENV=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1
cd "$L1R4_ROOT"
sha256sum --check L1R4_DEPLOY_SHA256.txt
sha256sum --check L1R4_EXTERNAL_SHA256.txt
(cd "$L1R4_VENV"; sha256sum --check --quiet "$L1R4_BASE/runtime/L1_scipy_SHA256.txt")
export PYTHONPATH="$L1R4_ROOT"
srun --ntasks=1 --cpu-bind=none "$L1R4_VENV/bin/python" -B -u scripts/labelfix/clariden/l1r_recompose_ext.py \
  --config config/l1r4_job.json --workers 32 \
  --out "$L1R4_BASE/l1e_20261017/l1r_sf6f_${SLURM_JOB_ID:?}"
