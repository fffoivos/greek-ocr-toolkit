#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=labelfix_L1F_frames
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1f/logs/L1F_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
if [[ "${L1F_MOCK:-0}" == 1 ]]; then
  export PYTHONPATH="$PWD"
  "${L1F_PYTHON:?}" -B -u scripts/labelfix/clariden/l1f_run.py \
    --mock --config "${L1F_CONFIG:?}" --out "${L1F_OUT:?}"
else
  L1F_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
  L1F_ROOT="$L1F_BASE/l1f"
  L1F_VENV=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1
  cd "$L1F_ROOT"
  export PYTHONPATH="$L1F_ROOT"
  sha256sum --check L1F_DEPLOY_SHA256.txt
  sha256sum --check L1F_EXTERNAL_SHA256.txt
  (cd "$L1F_VENV"; sha256sum --check --quiet "$L1F_BASE/runtime/L1_scipy_SHA256.txt")
  # Coordinator may supply the exact previous output directory to resume sealed
  # shards after a timeout. The entry point rejects any changed input/code.
  L1F_OUTPUT="${L1F_RESUME_OUT:-$L1F_BASE/l1f_${SLURM_JOB_ID}}"
  srun --ntasks=1 --gpus=4 --cpu-bind=none "$L1F_VENV/bin/python" -B -u \
    scripts/labelfix/clariden/l1f_run.py --config config/l1f_job.json --out "$L1F_OUTPUT"
fi
