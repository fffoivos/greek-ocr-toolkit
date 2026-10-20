#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH --time=00:05:00
#SBATCH --job-name=census04_regression
# Slurm stdout is selected with --output at submission, under census_04_seg08.
# Runtimes and margins: ../JOB_KINDS.md. This script never invokes sbatch.
# Slurm executes a spooled copy; the coordinator exports the deployed bundle.
bundle_path=${CENSUS04_BUNDLE:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}
source "$bundle_path/jobs/common.sh"
run_step "$python" -B -m pytest -q -p no:cacheprovider --basetemp="$attempt/job-test-tmp" \
  "$PYTHONPATH/tests/test_line_pipeline.py" "$PYTHONPATH/tests/test_fp3_numeric_adjacency.py" \
  "$PYTHONPATH/tests/test_fp3_external_crop_input.py" "$bundle/tests/test_census04.py"
