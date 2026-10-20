#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --job-name=labelfix_L1R3_CENSUS
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6/logs/L1R3_CENSUS_%j.log
set -euo pipefail
: "${1:?Usage: sbatch --dependency=afterok:L1R3_JOB_ID l1r2_census_job.sbatch L1R3_JOB_ID}"
[[ "$1" =~ ^[1-9][0-9]*$ ]] || { echo 'invalid L1R3 job ID' >&2; exit 2; }
L1R3_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R3_ROOT="$L1R3_BASE/l1r_sf6"
L1R3_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES=''
cd "$L1R3_ROOT"
export PYTHONPATH="$L1R3_ROOT"
sha256sum --check L1R3_DEPLOY_SHA256.txt
srun --ntasks=1 --cpu-bind=none "$L1R3_PYTHON" -B -u scripts/labelfix/clariden/l1r2_census.py \
  --config config/l1r_job.json \
  --input-dir "$L1R3_BASE/l1e_20261017/l1r_sf6_$1" --workers 16 \
  --out "$L1R3_ROOT/census/output_${1}_${SLURM_JOB_ID:?}"
