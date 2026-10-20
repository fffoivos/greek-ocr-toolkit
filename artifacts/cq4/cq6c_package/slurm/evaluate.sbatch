#!/usr/bin/env bash
# CQ6C coordinator resource specification; no job was submitted by the assembler.
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:21:00
#SBATCH --job-name=CQ6C_evaluate
#SBATCH --output=CQ6C_evaluate_%j.log
set -euo pipefail
cd "${CQ6C_PACKAGE_ROOT:?actual reviewed staged package root}"
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
CQ6C_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
"$CQ6C_PYTHON" -B verify_deploy.py --require-ready
# Offline instrument only. Does not establish protection-family adoption.
srun --ntasks=1 --cpu-bind=none "$CQ6C_PYTHON" -B evaluate.py \
  --truth data/wcap_truth.jsonl \
  --predictions "${CQ6C_PREDICTIONS:?complete prediction ledger}" \
  --lead-review "${CQ6C_LEAD_REVIEW:?blind pixel-review receipt}" \
  --lqb "${CQ6C_LQB_LEDGER:?canonical LQB ledger}" \
  --guard data/lqb_guard.jsonl --out "${CQ6C_EVALUATION_OUT:?output outside sealed package}"
