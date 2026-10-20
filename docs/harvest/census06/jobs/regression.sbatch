#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH --time=00:05:00
#SBATCH --job-name=census06_regression
# Slurm stdout is selected with --output at submission, under census_04_seg08.
# Runtimes and margins: ../JOB_KINDS.md. This script never invokes sbatch.
# Slurm executes a spooled copy; the coordinator exports the deployed bundle.
bundle_path=${CENSUS06_BUNDLE:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}
source "$bundle_path/jobs/common.sh"
# Tests consume the same bound native predictor; binary remains a runtime input.
mkdir -p "$PYTHONPATH/scripts/harvest/filter_runtime/target/debug"
ln -sfn "${CENSUS06_PREDICTOR:-$root/runtime/rust-target/release/greekocr-frozen-font-predict}" "$PYTHONPATH/scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict"
cd -- "$PYTHONPATH"
run_step "$python" -B -m pytest -q -p no:cacheprovider --basetemp="$attempt/job-test-tmp" \
  tests/test_content_gate.py tests/test_line_pipeline.py tests/test_integration_fixes.py \
  tests/test_numeric_cells.py tests/test_seg_gate.py tests/test_seg_deskew.py tests/test_seg_curve.py tests/test_seg_small.py \
  "$bundle/test_pipeline_033.py"
