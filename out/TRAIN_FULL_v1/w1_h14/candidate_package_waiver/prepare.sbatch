#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=04:00:00
#SBATCH --requeue
#SBATCH --job-name=TRAIN_FULL_prepare
#SBATCH --open-mode=append
#SBATCH --output=TRAIN_FULL_prepare_%j.log
set -euo pipefail
: "${TF_PACKAGE:?}" "${TF_DATA_CONFIG:?}" "${TF_PREP_ROOT:?}"
source "$TF_PACKAGE/runtime_env.sh"
srun --cpu-bind=none --nodes=1 --ntasks=1 "$TF_PYTHON" -B "$TF_PACKAGE/prepare_job.py" \
  --config "$TF_DATA_CONFIG" --out "$TF_PREP_ROOT"
