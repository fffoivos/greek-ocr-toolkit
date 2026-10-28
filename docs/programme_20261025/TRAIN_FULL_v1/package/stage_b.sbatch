#!/usr/bin/env bash
# Owner/coordinator-run only: four independent, exactly resumable trials/node.
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=96
#SBATCH --exclusive
#SBATCH --requeue
#SBATCH --signal=B:TERM@600
#SBATCH --time=02:00:00
#SBATCH --job-name=TRAIN_FULL_STAGE_B
#SBATCH --open-mode=append
#SBATCH --output=TRAIN_FULL_STAGE_B_%j.log
set -euo pipefail
: "${TF_PACKAGE:?}" "${SLURM_JOB_ID:?}"
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
export S1_DEADLINE_EPOCH
S1_DEADLINE_EPOCH=$(SLURM_TIME_FORMAT=standard squeue -h -j "$SLURM_JOB_ID" -o %e | xargs -I{} date -d '{}' +%s)
[[ "$S1_DEADLINE_EPOCH" =~ ^[0-9]+$ ]]
child=''
trap '[[ -z "$child" ]] || kill -TERM "$child" 2>/dev/null || true' TERM
set +e
"$TF_PYTHON" -B "$TF_PACKAGE/stage_b.py" node --plan "$1" --group "$2" &
child=$!
wait "$child"
status=$?
if kill -0 "$child" 2>/dev/null; then wait "$child"; status=$?; fi
set -e
if [[ $status == 75 ]]; then
  scontrol requeue "$SLURM_JOB_ID"
  exit 0
fi
exit "$status"
