#!/usr/bin/env bash
# Resource specification only: STOPPED CQ6 candidate. Nothing has been submitted.
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:21:00
#SBATCH --job-name=CQ6_evaluate
#SBATCH --output=CQ6_evaluate_%j.log
set -euo pipefail
cd "${CQ6_PACKAGE_ROOT:?set the reviewed package root}"
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
CQ6_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
"$CQ6_PYTHON" -B verify_deploy.py --require-ready
echo 'STOP: runtime adaptation is not present in this stopped evidence package' >&2
exit 78
