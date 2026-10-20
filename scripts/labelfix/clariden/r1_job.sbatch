#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=03:00:00
#SBATCH --job-name=labelfix_R1_marks
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/logs/R1_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=4
if [[ "${R1_MOCK:-0}" == 1 ]]; then
  export PYTHONPATH="$PWD"
  "${R1_PYTHON:?}" -u scripts/labelfix/clariden/r1_run.py --mock --out "${R1_OUT:?}" \
    --crop-root "${R1_CROP_ROOT:?}" --layout toolkit
else
  R1_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016
  cd "$R1_ROOT"
  sha256sum --check DEPLOY_SHA256.txt
  source /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/runtime.sh
  export PYTHONPATH="$R1_ROOT"
  srun --ntasks=1 --cpu-bind=none "${E3_PYTHON[@]}" -u scripts/labelfix/clariden/r1_run.py \
    --out "$R1_ROOT/output_${SLURM_JOB_ID}" \
    --crop-root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/crops \
    --layout e3 --epochs 15 --workers 16 --source-commit "${R1_SOURCE_COMMIT:-TRACK_LEAD_FILL_SOURCE_COMMIT}"
fi
