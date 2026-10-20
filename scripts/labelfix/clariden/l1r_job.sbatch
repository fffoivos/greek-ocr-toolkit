#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --job-name=labelfix_L1R3_SF6
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6/logs/L1R_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
L1R_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R_ROOT="$L1R_BASE/l1r_sf6"
L1R_VENV=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1
cd "$L1R_ROOT"
sha256sum --check L1R3_DEPLOY_SHA256.txt
sha256sum --check L1R3_EXTERNAL_SHA256.txt
(
  cd "$L1R_VENV"
  sha256sum --check --quiet "$L1R_BASE/runtime/L1_scipy_SHA256.txt"
)
export PYTHONPATH="$L1R_ROOT"
"$L1R_VENV/bin/python" -B -c 'import pathlib,sys,scipy; assert pathlib.Path(scipy.__file__).is_relative_to(pathlib.Path(sys.prefix)); print("SCIPY",scipy.__version__,scipy.__file__)'
srun --ntasks=1 --cpu-bind=none "$L1R_VENV/bin/python" -B -u scripts/labelfix/clariden/l1r_recompose_ext.py \
  --config config/l1r_job.json --workers 32 \
  --out "$L1R_BASE/l1e_20261017/l1r_sf6_${SLURM_JOB_ID:?}"
