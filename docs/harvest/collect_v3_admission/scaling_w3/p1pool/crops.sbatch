#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --job-name=p1pool-crops
set -euo pipefail
: "${P1POOL_PACKAGE:?}" "${ATTEMPT:?}" "${CENSUS_CODE:?bound census code}" "${CENSUS_MANIFEST:?}" "${PROJECTS_SUMS_ROOT:?}" "${PROJECTS_SHA256:?}"
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PYTHON="$W/venv_l1/bin/python" CENSUS_PROJECTS="$PROJECTS_SUMS_ROOT"
export LD_PRELOAD="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
bash "$P1POOL_PACKAGE/VERIFY.sh" package
source "$P1POOL_PACKAGE/vendor/binding_checks.sh"
"$PYTHON" -B "$P1POOL_PACKAGE/materialise_hold.py" --selection "$W/scaling_w3/p1pool_attempts/$ATTEMPT/selection.jsonl" --census-code "$CENSUS_CODE" --workers 8
