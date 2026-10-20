#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=00:20:00
#SBATCH --signal=TERM@90
#SBATCH --job-name=S8_DEV_fetch
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/S8F_%j.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
[[ -n "${SLURM_JOB_ID:-}" && "${SLURM_JOB_PARTITION:-}" == debug && "${SLURM_JOB_NUM_NODES:-}" == 1 ]] || {
  echo 'STOP: compute-only one-node debug job; never run on login node' >&2; exit 2;
}
S8F_JOB=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/job
cd "$S8F_JOB"
sha256sum --check S8F_DEPLOY_SHA256.txt
# The extractor and wrapper use only Python 3.6+ standard-library modules.
srun --ntasks=1 --cpus-per-task=32 --cpu-bind=none \
  /usr/bin/python3 -B -u scripts/labelfix/s8_fetch_job.py run --config job_config.json
