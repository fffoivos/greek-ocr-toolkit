#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH --time=04:00:00
#SBATCH --job-name=census04_census
# Slurm stdout is selected with --output at submission, under census_04_seg08.
# Runtimes and margins: ../JOB_KINDS.md. This script never invokes sbatch.
# Slurm executes a spooled copy; the coordinator exports the deployed bundle.
bundle_path=${CENSUS04_BUNDLE:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}
source "$bundle_path/jobs/common.sh"
args=(--source "${CENSUS04_CONFIG:-$bundle/census04_config.json}" --projects "$projects" --out "$attempt/inputs")
if [[ "$E4_SMOKE" == 1 ]]; then args+=(--smoke); fi
if [[ -n "${CENSUS04_SPLIT_FILE:-}" ]]; then
  args+=(--split-file "$CENSUS04_SPLIT_FILE" --split-sha256 "${CENSUS04_SPLIT_SHA256:?}")
fi
run_step "$python" -B "$bundle/prepare_config.py" "${args[@]}"
run_step "$python" -B -m greekocr.harvest.line_pipeline_census04 "$attempt/inputs/config.json" --out "$attempt" --execute
