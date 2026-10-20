#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH --time=00:05:00
#SBATCH --job-name=census04_parity
# Slurm stdout is selected with --output at submission, under census_04_seg08.
# Runtimes and margins: ../JOB_KINDS.md. This script never invokes sbatch.
# Slurm executes a spooled copy; the coordinator exports the deployed bundle.
bundle_path=${CENSUS04_BUNDLE:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}
source "$bundle_path/jobs/common.sh"
run_step "$python" -B "$bundle/parity_check.py" --out "$attempt/job-policy-parity.json"
