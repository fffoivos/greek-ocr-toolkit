#!/usr/bin/env bash
# CQ6C coordinator resource specification; no job was submitted by the assembler.
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:21:00
#SBATCH --job-name=CQ6C_smoke
#SBATCH --output=CQ6C_smoke_%j.log
set -euo pipefail
cd "${CQ6C_PACKAGE_ROOT:?actual reviewed staged package root}"
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
CQ6C_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
"$CQ6C_PYTHON" -B verify_deploy.py --require-ready
# Semantic fixtures only; not a qualified real-input training smoke.
srun --ntasks=1 --cpu-bind=none "$CQ6C_PYTHON" -B test_instrument.py
srun --ntasks=1 --cpu-bind=none "$CQ6C_PYTHON" -B test_admission.py
