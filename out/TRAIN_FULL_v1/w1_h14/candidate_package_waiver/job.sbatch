#!/usr/bin/env bash
# Owner-run only. S1 wheel runtime, no uenv GPU library view.
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --exclusive
#SBATCH --requeue
#SBATCH --signal=B:TERM@600
#SBATCH --time=12:00:00
#SBATCH --job-name=TRAIN_FULL_v1
#SBATCH --open-mode=append
#SBATCH --output=TRAIN_FULL_%j.log
set -euo pipefail
: "${TF_PACKAGE:?}" "${TF_RUNTIME:?}" "${TF_OUTPUT:?}" "${SLURM_JOB_ID:?}"
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
export S1_DEADLINE_EPOCH
S1_DEADLINE_EPOCH=$(SLURM_TIME_FORMAT=standard squeue -h -j "$SLURM_JOB_ID" -o %e | xargs -I{} date -d '{}' +%s)
[[ "$S1_DEADLINE_EPOCH" =~ ^[0-9]+$ ]]
# Forward the allocation warning through srun; S1 handles it at an optimizer boundary.
child=''
trap '[[ -z "$child" ]] || kill -TERM "$child" 2>/dev/null || true' TERM
set +e
srun --cpu-bind=none --nodes=1 --ntasks=1 "$TF_PYTHON" -B "$TF_PACKAGE/segment.py" \
  --runtime "$TF_RUNTIME" --out "$TF_OUTPUT" --mode "${TF_MODE:-train}" &
child=$!
wait "$child"
status=$?
if kill -0 "$child" 2>/dev/null; then wait "$child"; status=$?; fi
set -e
if [[ $status == 75 ]]; then
  if [[ ${TF_MODE:-train} == smoke-requeue && ${SLURM_RESTART_COUNT:-0} == 0 ]]; then
    # Deliberate scheduler requeue is part of the owner-run smoke only.
    scontrol requeue "$SLURM_JOB_ID"
    exit 0
  fi
  # Deadline segment yields COMPLETED/0:0, authenticated by SEGMENT_YIELD.json.
  # chain.py's next job continues the same state; preemption uses --requeue.
  exit 0
fi
exit "$status"
