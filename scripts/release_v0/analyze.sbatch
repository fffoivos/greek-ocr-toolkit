#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --no-requeue
#SBATCH --job-name=REL0-analysis
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
REL0_PYTHON=${REL0_PYTHON:-/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python}
REL0_CODE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
srun --cpu-bind=cores "$REL0_PYTHON" -B "$REL0_CODE/analyze_models.py" --jobs "${SLURM_CPUS_PER_TASK:-16}" "$@"
