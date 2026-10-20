#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=labelfix_L1_s6
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/logs/L1_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
if [[ "${L1_MOCK:-0}" == 1 ]]; then
  export PYTHONPATH="$PWD"
  "${L1_PYTHON:?}" -B -u scripts/labelfix/clariden/l1_run.py \
    --mock ${L1_WRITE_EXPECTED:+--write-expected} --detector "${L1_DETECTOR:-s6}" \
    --binding artifacts/labelfix_l1/binding \
    --source docs/harvest/collection/v2/import_real_v2_train.jsonl \
    --c1-alignments "${L1_C1_ALIGNMENTS:?}" --ctc "${L1_CTC:?}" --r1 "${L1_R1:?}" \
    --crop-root "${L1_CROP_ROOT:?}" --layout toolkit --out "${L1_OUT:?}"
else
  L1_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
  E3_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
  L1_PYTHON="$E3_ROOT/venv_l1/bin/python"
  cd "$L1_ROOT"
  export PYTHONPATH="$L1_ROOT"
  sha256sum --check L1_DEPLOY_SHA256.txt
  sha256sum --check L1_EXTERNAL_SHA256.txt
  "$L1_PYTHON" -B scripts/labelfix/clariden/l1_runtime.py --root "$E3_ROOT" --out "$L1_ROOT/runtime" --verify
  srun --ntasks=1 --cpu-bind=none "$L1_PYTHON" -B -u scripts/labelfix/clariden/l1_run.py \
    --detector "${L1_DETECTOR:-s6}" --binding artifacts/labelfix_l1/binding \
    --source "$E3_ROOT/collection_v2/import_real_v2_train.jsonl" \
    --c1-alignments "$E3_ROOT/labelfix_c1_20261016/output_3678590/C1_alignments.jsonl.gz" \
    --ctc "$E3_ROOT/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt" \
    --r1 "$E3_ROOT/labelfix_r1_20261016/output_3678928/A/best.pt" \
    --crop-root "$E3_ROOT/collection_v2/crops" --layout e3 --out "$L1_ROOT/output_${SLURM_JOB_ID}"
fi
