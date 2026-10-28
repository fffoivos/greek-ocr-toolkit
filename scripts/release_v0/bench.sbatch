#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --no-requeue
#SBATCH --job-name=REL0-speed
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
REL0_PYTHON=${REL0_PYTHON:-/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python}
REL0_CODE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# --device gpu by default; --device cpu in coordinator commands uses a CPU-only
# allocation override (--gpus-per-node=0). Never run both grids concurrently.
srun --cpu-bind=cores "$REL0_PYTHON" -B "$REL0_CODE/bench_speed.py" --device gpu "$@"
