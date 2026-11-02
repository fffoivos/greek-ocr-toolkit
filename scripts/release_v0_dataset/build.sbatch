#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=0
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --export=NONE
#SBATCH --no-requeue
#SBATCH --job-name=REL0-lines-smoke
set -euo pipefail
# Starting benchmark shape only. Coordinator chooses the full budget from --plan
# plus measured smoke timings, verifies deployment and performs scheduler dry check.
# Arguments are ordinary builder flags; no credential or submission code belongs here.
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
REL0_DATASET_PYTHON=${REL0_DATASET_PYTHON:-/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python}
# Match resolve.sbatch: jsonschema and ijson are deployed in this private library.
export PYTHONPATH="${REL0_DATASET_PYLIB:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/pylib}"
# Slurm executes a spool copy; submissions must originate at the checkout root.
if [[ -n "${SLURM_SUBMIT_DIR:-}" ]]; then
    REL0_DATASET_CODE="$SLURM_SUBMIT_DIR/scripts/release_v0_dataset"
else
    REL0_DATASET_CODE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
fi
if [[ ! -f "$REL0_DATASET_CODE/build_dataset.py" ]]; then
    printf 'ERROR: expected script missing: %s; submit from the checkout root (SLURM_SUBMIT_DIR=%s)\n' \
        "$REL0_DATASET_CODE/build_dataset.py" "${SLURM_SUBMIT_DIR:-unset}" >&2
    exit 1
fi
srun --cpu-bind=cores "$REL0_DATASET_PYTHON" -B "$REL0_DATASET_CODE/build_dataset.py" "$@"
