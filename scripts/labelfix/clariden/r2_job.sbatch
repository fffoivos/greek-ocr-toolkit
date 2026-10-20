#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=02:00:00
#SBATCH --job-name=labelfix_R2
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/logs/R2_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
if [[ "${R2_MOCK:-0}" == 1 ]]; then
  export PYTHONPATH="$PWD"
  "${R2_PYTHON:?}" -B -u scripts/labelfix/clariden/r2_run.py --mock --config "${R2_CONFIG:?}" --out "${R2_OUT:?}"
else
  R2_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017
  cd "$R2_ROOT"
  sha256sum --check R2_DEPLOY_SHA256.txt
  export PYTHONPATH="$R2_ROOT"
  srun --ntasks=1 --cpu-bind=none /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python -B -u \
    scripts/labelfix/clariden/r2_run.py --config "${R2_CONFIG:-config/r2_job.json}" --out "${R2_OUT:-$R2_ROOT/output_${SLURM_JOB_ID}}"
fi
