#!/bin/bash
#SBATCH --account=a0140
#SBATCH --job-name=MIX1D-manifests
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=mix1d-manifests-%j.log
# 9 plans x 8 x 428872 = 30,878,784 index rows; five 64-bit fields
# alone need 1,235,151,360 bytes before JSON IDs, compression and Python objects.
set -euo pipefail
"$MIX1_ROOT/VERIFY.sh" package
exec "$MIX1_PYTHON" -B "$MIX1_ROOT/run.py" build --subset-receipt "$MIX1_SUBSET_RECEIPT" --subset-sha "$MIX1_SUBSET_SHA" --output "$MIX1_OUTPUT"
