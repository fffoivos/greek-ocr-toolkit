#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --job-name=labelfix_L1C
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4/l1c/logs/L1C_%j.log
set -euo pipefail
: "${1:?Usage: sbatch l1c_job.sbatch L1R_JOB_ID}"
[[ "$1" =~ ^[1-9][0-9]*$ ]] || { echo 'invalid L1R job ID' >&2; exit 2; }
L1C_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4/l1c
L1C_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES=''
unset PYTHONPATH
cd "$L1C_ROOT"
sha256sum --check L1C_DEPLOY_SHA256.txt
srun --ntasks=1 --cpu-bind=none "$L1C_PYTHON" -B -u l1c_census.py \
  --l1r-job-id "$1" --workers 16 --out "$L1C_ROOT/output_${1}_${SLURM_JOB_ID:?}"
