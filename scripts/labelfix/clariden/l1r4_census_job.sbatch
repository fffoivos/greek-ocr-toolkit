#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --job-name=labelfix_L1R4_CENSUS
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6f/logs/L1R4_CENSUS_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=''
if [[ "${L1R4_MOCK:-0}" == 1 ]]; then
  : "${L1R4_PYTHON:?}" "${L1R4_OUT:?}" "${L1R4_INPUT:?}" "${L1R4_CONFIG:?}"
  export PYTHONPATH="$PWD"
  exec "$L1R4_PYTHON" -B -u scripts/labelfix/clariden/l1r4_census.py \
    --config "$L1R4_CONFIG" --input-dir "$L1R4_INPUT" --out "$L1R4_OUT" --workers 2
fi
: "${1:?Usage: sbatch --dependency=afterok:JOB1 l1r4_census_job.sbatch JOB1}"
[[ "$1" =~ ^[1-9][0-9]*$ ]] || { echo 'invalid L1R4 job ID' >&2; exit 2; }
L1R4_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R4_ROOT="$L1R4_BASE/l1r_sf6f"
L1R4_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
cd "$L1R4_ROOT"
export PYTHONPATH="$L1R4_ROOT"
sha256sum --check L1R4_DEPLOY_SHA256.txt
srun --ntasks=1 --cpu-bind=none "$L1R4_PYTHON" -B -u scripts/labelfix/clariden/l1r4_census.py \
  --config config/l1r4_job.json --workers 16 \
  --input-dir "$L1R4_BASE/l1e_20261017/l1r_sf6f_$1" \
  --out "$L1R4_ROOT/census/output_${1}_${SLURM_JOB_ID:?}"
