#!/usr/bin/env bash
set -euo pipefail
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
projects="$bundle/package/projects"
W=${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}
root="$W/filter_pipeline_20261018"
python=${CENSUS04_PYTHON:-$W/venv_l1/bin/python}
E4_SMOKE=${E4_SMOKE:-1}
case "$E4_SMOKE" in 1) mode=smoke;; 0) mode=full;; *) exit 2;; esac
split_mode=mode-i
if [[ -n "${CENSUS04_SPLIT_FILE:-}" ]]; then split_mode=mode-ii; fi
attempt="$root/census_04_seg08/${CENSUS04_ATTEMPT:-$mode-$split_mode}"
mkdir -p "$attempt/tmp" "$attempt/cache"
cd -- "$attempt"
export TMPDIR="$attempt/tmp" XDG_CACHE_HOME="$attempt/cache"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHONPATH="$projects/greek-ocr-toolkit-sol-recut"
export PATH="$root/runtime/node-v22.23.3-linux-arm64/bin:$PATH"
# Same codec injection as census_03; local mocks use the system codec.
if [[ -f "$root/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng" ]]; then
  export LD_PRELOAD="$root/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
fi
run_step() {
  srun -A a0140 --partition="${SLURM_JOB_PARTITION:?}" --cpu-bind=none --nodes=1 --ntasks=1 "$@"
}
