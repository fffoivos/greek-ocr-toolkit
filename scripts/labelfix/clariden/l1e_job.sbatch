#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=labelfix_L1E_AB
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/logs/L1E_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
if [[ "${L1E_MOCK:-0}" == 1 ]]; then
  export PYTHONPATH="$PWD"
  "${L1E_PYTHON:?}" -B -u scripts/labelfix/clariden/l1e_run.py \
    --mock --config "${L1E_CONFIG:?}" --out "${L1E_OUT:?}"
else
  L1E_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017
  L1E_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
  cd "$L1E_ROOT"
  export PYTHONPATH="$L1E_ROOT"
  sha256sum --check L1E_DEPLOY_SHA256.txt
  sha256sum --check L1E_EXTERNAL_SHA256.txt
  srun --ntasks=1 --cpu-bind=none "$L1E_PYTHON" -B -u scripts/labelfix/clariden/l1e_run.py \
    --config config/l1e_job.json --out "$L1E_ROOT/output_${SLURM_JOB_ID}"
fi
