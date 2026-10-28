#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --requeue
#SBATCH --signal=B:TERM@600
#SBATCH --time=23:00:00
#SBATCH --job-name=TRAIN_FULL_STAGE_C
#SBATCH --open-mode=append
set -euo pipefail
: "${TF_PACKAGE:?}" "${SLURM_JOB_ID:?}"
source "$TF_PACKAGE/runtime_env.sh"
TF_C_CONTROLS="$(dirname "$1")/signal-controls"
mkdir -p "$TF_C_CONTROLS"
export TF_C_STOP="$TF_C_CONTROLS/${SLURM_JOB_ID}-${SLURM_RESTART_COUNT:-0}.stop"
# Install BEFORE Python verification/startup. Never signal an srun client.
warning_generation=0
trap 'warning_generation=$((warning_generation + 1)); if [[ ! -e "$TF_C_STOP" ]]; then printf "TERM job=%s restart=%s\n" "$SLURM_JOB_ID" "${SLURM_RESTART_COUNT:-0}" > "$TF_C_STOP.pending"; mv "$TF_C_STOP.pending" "$TF_C_STOP"; fi' TERM
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
export S1_DEADLINE_EPOCH
# Original stop hook subtracts 300; offset another 300 to match TERM@600.
S1_DEADLINE_EPOCH=$(SLURM_TIME_FORMAT=standard squeue -h -j "$SLURM_JOB_ID" -o %e | xargs -I{} date -d '{}' +%s)
[[ "$S1_DEADLINE_EPOCH" =~ ^[0-9]+$ ]]
S1_DEADLINE_EPOCH=$((S1_DEADLINE_EPOCH - 300))
set +e
"$TF_PYTHON" -B "$TF_PACKAGE/stage_c.py" node --plan "$1" --index "$2" &
child=$!
# wait can be interrupted repeatedly by trapped TERM. Keep the actual child
# status; do not turn TERM's synthetic 143 into a failed lane or a requeue.
while true; do
  before=$warning_generation
  wait "$child"
  status=$?
  # Retry even if the child exited at the instant wait was interrupted. Bash
  # retains its real status; kill -0 alone can race and preserve a false 143.
  if [[ $before == "$warning_generation" ]]; then break; fi
done
set -e
if [[ $status == 75 ]]; then
  scontrol requeue "$SLURM_JOB_ID"
  exit 0
fi
exit "$status"
