#!/usr/bin/env bash
# Owner submits this short CPU-only audit before factory preparation or GPU smoke.
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:20:00
#SBATCH --requeue
#SBATCH --job-name=TRAIN_FULL_audit
#SBATCH --open-mode=append
#SBATCH --output=TRAIN_FULL_audit_%j.log
set -euo pipefail
: "${TF_PACKAGE:?}" "${TF_DATA_CONFIG:?}" "${TF_PREP_ROOT:?}"
source "$TF_PACKAGE/runtime_env.sh"
srun --cpu-bind=none --nodes=1 --ntasks=1 "$TF_PYTHON" -B "$TF_PACKAGE/audit_job.py" \
  --config "$TF_DATA_CONFIG" --out "$TF_PREP_ROOT"
