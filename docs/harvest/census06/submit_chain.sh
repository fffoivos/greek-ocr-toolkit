#!/usr/bin/env bash
# Coordinator only; this file is never invoked by C1 against real Slurm.
set -euo pipefail
: "${CENSUS06_BUNDLE:?}" "${CENSUS06_ATTEMPT:?}" "${E4_SMOKE:?}"
W=${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}
python=${CENSUS06_PYTHON:-$W/venv_l1/bin/python}
full_time=${SBATCH_TIMELIMIT:-}
common=()
common_time=
while (($#)); do
  case "$1" in
    --full-time) full_time=${2:?--full-time needs HH:MM:SS}; shift 2;;
    --full-time=*) full_time=${1#*=}; shift;;
    --time|-t) common_time=${2:?time needs a value}; common+=("$1" "$2"); shift 2;;
    --time=*) common_time=${1#*=}; common+=("$1"); shift;;
    -t?*) common_time=${1#-t}; common+=("$1"); shift;;
    *) common+=("$1"); shift;;
  esac
done
case "$E4_SMOKE" in 0|1);; *) echo 'E4_SMOKE must be 0 or 1' >&2; exit 2;; esac
"$python" -B "$CENSUS06_BUNDLE/binding_state.py" --submit
runroot="$W/census_06_20261020"
if [[ "$E4_SMOKE" == 0 ]]; then
  # Refusal happens before even the regression submission.
  "$python" -B "$CENSUS06_BUNDLE/timing_c1.py" \
    --attempts "$runroot/attempts" --smoke-readout "${CENSUS06_SMOKE_READOUT:-}" \
    --full-time "${full_time:-$common_time}"
fi
mkdir -p "$runroot/attempts" "$runroot/logs"
submit() {
  local kind=$1 dependency=$2 limit=$3
  local options=() effective=${common_time:-$limit}
  if [[ "$E4_SMOKE" == 1 ]]; then
    options+=(--partition=debug --time=00:30:00)
    effective=${common_time:-00:30:00}
  fi
  options+=("${common[@]}")
  if [[ "$kind" == census && "$E4_SMOKE" == 0 && -n "$full_time" ]]; then
    options+=(--time="$full_time")
    effective=$full_time
  fi
  if [[ -n "$dependency" ]]; then options+=(--dependency="afterok:$dependency"); fi
  printf '%s effective --time=%s\n' "$kind" "$effective" >&2
  # Slurm environment variables beat #SBATCH directives. Remove only this one
  # from every invocation; express the full census override as a CLI option.
  env -u SBATCH_TIMELIMIT sbatch --parsable "${options[@]}" --chdir="$runroot" \
    --export=ALL --output="$runroot/logs/$kind-%j.log" "$CENSUS06_BUNDLE/jobs/$kind.sbatch"
}
regression=$(submit regression '' 00:05:00)
parity=$(submit parity "$regression" 00:05:00)
census=$(submit census "$parity" 04:00:00)
readout=$(submit readout "$census" 00:30:00)
printf 'regression=%s parity=%s census=%s readout=%s\n' "$regression" "$parity" "$census" "$readout"
