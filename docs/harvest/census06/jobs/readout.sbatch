#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --job-name=census06_readout
set -euo pipefail
CENSUS06_RUN=${CENSUS06_RUN:-${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}/census_06_20261020/attempts/${CENSUS06_ATTEMPT:?}}
CENSUS06_READOUT_OUT=${CENSUS06_READOUT_OUT:-${CENSUS06_RUN}.readout}
CENSUS06_PROJECT_ROOT="$CENSUS06_BUNDLE/package/projects/greek-ocr-toolkit-pipe032"
CENSUS06_BUNDLE="$CENSUS06_BUNDLE/readout"
: "${CENSUS06_RUN:?}" "${CENSUS06_READOUT_OUT:?}" "${CENSUS06_BUNDLE:?}"
[[ "$CENSUS06_BUNDLE" = /* ]] || { echo 'CENSUS06_BUNDLE must be absolute' >&2; exit 2; }
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
# Inherit the allocation's uenv, exactly as seg_census/jobs/common.sh does.
# BUNDLE is the absolute deployed directory containing census_readout.py.
python=${CENSUS06_PYTHON:-${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}/venv_l1/bin/python}
package=${CENSUS06_PROJECT_ROOT:-$CENSUS06_BUNDLE/../package/projects/greek-ocr-toolkit-pipe032}
version=$(PYTHONPATH="$package" "$python" -B -c 'from greekocr.harvest.line_pipeline import PIPELINE_VERSION; print(PIPELINE_VERSION)')
args=(--expect-pipeline-version "$version" --run "$CENSUS06_RUN" --out "$CENSUS06_READOUT_OUT")
if [[ -n "${CENSUS06_BASELINE:-}" ]]; then args+=(--baseline "$CENSUS06_BASELINE"); fi
if [[ -n "${CENSUS06_EXPECT_ROWS:-}" ]]; then args+=(--expect-rows "$CENSUS06_EXPECT_ROWS"); fi
srun -A a0140 --partition="${SLURM_JOB_PARTITION:?}" --cpu-bind=none --nodes=1 --ntasks=1 \
  "$python" -B "$CENSUS06_BUNDLE/census_readout.py" "${args[@]}"
