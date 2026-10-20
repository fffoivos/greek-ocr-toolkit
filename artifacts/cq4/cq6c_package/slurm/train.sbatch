#!/usr/bin/env bash
# CQ6C coordinator resource specification; no job was submitted by the assembler.
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:21:00
#SBATCH --job-name=CQ6C_train
#SBATCH --output=CQ6C_train_%j.log
set -euo pipefail
cd "${CQ6C_PACKAGE_ROOT:?actual reviewed staged package root}"
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
CQ6C_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
"$CQ6C_PYTHON" -B verify_deploy.py --require-ready
# Actual R2a admission rejects UNKNOWN heads. Never weaken this gate.
"$CQ6C_PYTHON" -B verify_deploy.py --require-training-ready
echo 'No admitted production runtime is sealed in CQ6C' >&2
exit 78
