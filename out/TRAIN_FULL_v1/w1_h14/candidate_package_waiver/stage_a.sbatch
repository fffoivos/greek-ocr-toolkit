#!/usr/bin/env bash
# Measurement only; owner submits. No models/checkpoints retained.
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=96
#SBATCH --exclusive
#SBATCH --requeue
#SBATCH --time=03:00:00
#SBATCH --job-name=TRAIN_FULL_STAGE_A
#SBATCH --open-mode=append
#SBATCH --output=TRAIN_FULL_STAGE_A_%j.log
set -euo pipefail
: "${TF_PACKAGE:?}" "${TF_RUNTIME:?}" "${TF_STAGE_A:?}"
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
# No scheduler time strings are read. Slurm propagates preemption to all srun
# steps; complete points are reused, unfinished disposable measurements repeat.
exec "$TF_PYTHON" -B "$TF_PACKAGE/stage_a.py" node --runtime "$TF_RUNTIME" --out "$TF_STAGE_A"
