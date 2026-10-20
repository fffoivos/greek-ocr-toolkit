#!/bin/bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --time=00:01:00
# Retained filename, fail closed: choose the explicit stage.
set -euo pipefail
printf '%s\n' 'Use submit_mix1.sh manifests|export; see MIX1.md.' >&2
exit 2
