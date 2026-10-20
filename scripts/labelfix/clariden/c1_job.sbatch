#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=labelfix_C1_align
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_c1_20261016/logs/C1_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1
if [[ "${C1_MOCK:-0}" == 1 ]]; then
  export PYTHONPATH="$PWD"
  "${C1_PYTHON:?}" -u scripts/labelfix/clariden/c1_run.py \
    --selection "${C1_SELECTION:?}" --checkpoint "${C1_CHECKPOINT:?}" \
    --crop-root "${C1_CROP_ROOT:-$PWD}" --crop-layout toolkit --out "${C1_OUT:?}" \
    --device cpu --workers 1 --threads 4 --chunk-size 32 --batch-size 16 \
    --mock --compare-cache .cache/labelfix/align_s0.jsonl
else
  C1_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_c1_20261016
  cd "$C1_ROOT"
  sha256sum --check DEPLOY_SHA256.txt
  sha256sum --check CHECKPOINT_SHA256.txt
  source /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/runtime.sh
  export PYTHONPATH="$C1_ROOT"
  srun --ntasks=1 --cpu-bind=none "${E3_PYTHON[@]}" -u scripts/labelfix/clariden/c1_run.py \
    --selection docs/records/labelfix/spellcheck/clariden/C1_selection.jsonl \
    --checkpoint /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt \
    --crop-root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/crops \
    --crop-layout e3 --out "$C1_ROOT/output_${SLURM_JOB_ID}" \
    --device cuda --workers 4 --threads 8 --batch-size 16 --chunk-size 512
fi
