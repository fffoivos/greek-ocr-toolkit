#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --gpus-per-node=4
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=sf7_test_dev_A
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019/logs/TR2_%j.log
set -euo pipefail
TR2_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
if [[ -n ${SLURM_JOB_ID:-} ]]; then
 TR2_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019
fi
cd "$TR2_ROOT"
export PYTHONPATH="$TR2_ROOT" PYTHONDONTWRITEBYTECODE=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
if command -v sha256sum >/dev/null; then sha256sum -c TR2_DEPLOY_SHA256.txt; else shasum -a 256 -c TR2_DEPLOY_SHA256.txt; fi
if [[ ${1:-} == --mock ]]; then
 shift
 exec "${TR2_MOCK_PYTHON:?}" -B -u scripts/labelfix/clariden/tr2_run.py --mock "$@"
fi
TR2_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
if [[ ${1:-} == --dry-run ]]; then
 shift
 exec "$TR2_PYTHON" -B -u scripts/labelfix/clariden/tr2_run.py --dry-run "$@"
fi
srun --ntasks=1 --gpus=4 --cpu-bind=none "$TR2_PYTHON" -B -u scripts/labelfix/clariden/tr2_run.py --out "$TR2_ROOT/output_${SLURM_JOB_ID:?}"
