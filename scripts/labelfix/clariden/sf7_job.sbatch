#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --job-name=labelfix_sf7_rc1
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017/logs/SF7_%j.log
set -euo pipefail
# Resolve our own deployed root, regardless of the submitter's cwd.
SF7_SCRIPT=${BASH_SOURCE[0]}
SF7_ROOT=$(cd "$(dirname "$SF7_SCRIPT")/../../.." && pwd)
# Slurm copies the script to its spool: production root is explicit there.
if [[ -n ${SLURM_JOB_ID:-} ]]; then
  SF7_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017
fi
cd "$SF7_ROOT"
export PYTHONPATH="$SF7_ROOT" PYTHONDONTWRITEBYTECODE=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum --check SF7_DEPLOY_SHA256.txt
else
  shasum -a 256 --check SF7_DEPLOY_SHA256.txt
fi
if [[ ${1:-} == --mock ]]; then
  shift
  SF7_PYTHON=${SF7_MOCK_PYTHON:?}
  exec "$SF7_PYTHON" -B -u scripts/labelfix/clariden/sf7_recompose.py "$@"
fi
SF7_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
if [[ ${1:-} == --dry-run ]]; then
  shift
  exec "$SF7_PYTHON" -B -u scripts/labelfix/clariden/sf7_recompose.py \
    --config config/sf7_job.json --workers 1 --limit 2000 "$@"
fi
srun --ntasks=1 --cpu-bind=none "$SF7_PYTHON" -B -u scripts/labelfix/clariden/sf7_recompose.py \
  --config config/sf7_job.json --workers 32 --out "$SF7_ROOT/output_${SLURM_JOB_ID:?}"
