#!/usr/bin/env bash
# Coordinator submits from the SHA-verified checkout root. No builder/work DB.
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=0
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --export=NONE
#SBATCH --no-requeue
#SBATCH --job-name=HFD-P2m-audit
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
R=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0
export PYTHONPATH="$SLURM_SUBMIT_DIR:$R/pylib"
cd "$SLURM_SUBMIT_DIR"
sha256sum -c DEPLOYMENT_SHA256SUMS >&2
srun --cpu-bind=cores /capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python -B \
    scripts/release_v0_dataset/audit_harvest_merges.py --code-root "$SLURM_SUBMIT_DIR" "$@"
