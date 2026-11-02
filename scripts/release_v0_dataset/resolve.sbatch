#!/usr/bin/env bash
#SBATCH --job-name=REL0-resolve
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=0
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --export=NONE
#SBATCH --no-requeue
set -euo pipefail
# Output directory, optional comma-separated items, optional copied v2 directory.
# 4800 s work + at most 600 s reporting = 90 min, below the 120 min limit.
if [[ $# -lt 1 || $# -gt 3 ]]; then
    printf 'Usage: %s OUTPUT_DIR [ITEMS [BOOK_REGISTRY_DIR]]\n' "$0" >&2
    exit 1
fi
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
REL0_DATASET_PYTHON=${REL0_DATASET_PYTHON:-/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python}
if [[ -n "${SLURM_SUBMIT_DIR:-}" ]]; then
    REL0_DATASET_CODE="$SLURM_SUBMIT_DIR/scripts/release_v0_dataset"
else
    REL0_DATASET_CODE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
fi
if [[ ! -f "$REL0_DATASET_CODE/resolve_probe.py" ]]; then
    printf 'ERROR: expected script missing: %s; submit from the checkout root (SLURM_SUBMIT_DIR=%s)\n' \
        "$REL0_DATASET_CODE/resolve_probe.py" "${SLURM_SUBMIT_DIR:-unset}" >&2
    exit 1
fi
# Match the original resolver's private metadata-library location.
export PYTHONPATH="${REL0_DATASET_PYLIB:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/pylib}"
rel0_resolve_args=(--output-dir "$1" --budget-seconds 4800 --samples 3)
if [[ $# -ge 2 ]]; then
    rel0_resolve_args+=(--items "$2")
fi
if [[ $# -eq 3 ]]; then
    rel0_resolve_args+=(--book-registry-dir "$3")
fi
srun --cpu-bind=cores /usr/bin/env -u HF_TOKEN -u HUGGING_FACE_HUB_TOKEN -u HUGGINGFACEHUB_API_TOKEN \
    -u HUGGINGFACE_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS \
    -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
    "$REL0_DATASET_PYTHON" -B "$REL0_DATASET_CODE/resolve_probe.py" "${rel0_resolve_args[@]}"
