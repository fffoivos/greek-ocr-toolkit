#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:30:00
#SBATCH --job-name=crops4
# Submit with --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" (directory must exist).
set -euo pipefail
B="$(cd "$(dirname "${CROPS4_PACKAGE:-$0}")" && pwd)"
W="${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}"
: "${CENSUS_ATTEMPT:?completed census attempt}"
: "${CENSUS_PROJECTS:?census prepared projects tree}"
: "${PROJECTS_SHA256:?sha256 of census manifest from its launch binding}"
: "${ATTEMPT:?unique CROPS4 attempt name}"
: "${MODE:?smoke or full}"
[[ "$ATTEMPT" =~ ^[A-Za-z0-9_-]+$ ]]
[[ "$MODE" == smoke || "$MODE" == full ]]
A="$W/crops4_attempts/$ATTEMPT"
mkdir -p "$A/tmp" "$A/cache"
export TMPDIR="$A/tmp" XDG_CACHE_HOME="$A/cache"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHON="${PYTHON:-$W/venv_l1/bin/python}"
export LD_PRELOAD="${CODEC_PRELOAD-$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng}"
# Empty preload is allowed only by an explicit local mock invocation; production default must exist.
[[ -z "$LD_PRELOAD" || -f "$LD_PRELOAD" ]]
export PYTHONPATH="${CENSUS_CODE:-$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut}"
source "$B/binding_checks.sh" >"$A/prepared-check.log" 2>&1
ARGS=(--census-attempt "$CENSUS_ATTEMPT" --census-code "$PYTHONPATH" --work-root "$W" --attempt "$A" --tranche "${TRANCHE:-W2}" --mode "$MODE")
if [[ "${INCLUDE_HELDOUT:-0}" == 1 ]]; then ARGS+=(--include-heldout); fi
if [[ "$MODE" == full ]]; then ARGS+=(--smoke-receipt "${SMOKE_RECEIPT:?500/500 smoke receipt required}"); fi
run_step() {
  srun -A a0140 --partition="${SLURM_JOB_PARTITION:-normal}" --cpu-bind=none --nodes=1 --ntasks=1 "$@"
}
run_step bash "$B/VERIFY.sh" "${ARGS[@]}" >"$A/verify.log" 2>"$A/verify-check.log"
run_step "$PYTHON" -B "$B/materialise_crops.py" "${ARGS[@]}" --workers "${SLURM_CPUS_PER_TASK:-8}" >"$A/materialise.log" 2>&1
if [[ "$MODE" == smoke ]]; then
  "$PYTHON" -B -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["status"]=="ok" and r["selected"]==r["byte_exact"]==500, "smoke must report 500/500 byte-exact"' "$A/upload_receipt.json"
fi
