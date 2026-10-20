#!/bin/bash
#SBATCH --account=a0140
#SBATCH --job-name=MIX1D-export
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=128G
#SBATCH --time=04:00:00
#SBATCH --output=mix1d-export-%j.log
# One shared real export: 364871 crops, not 9 x 364871 = 3283839.
# 48 x 2560 = 122880 decoded grayscale bytes/crop maximum;
# 364871 x 122880 = 44835348480 B decoded maximum; one shared copy.
# CPU only, no GPU directive. Estimate is capacity arithmetic, not benchmark ETA.
set -euo pipefail
: "${MIX1_EXPORT_OUTPUT:?new export output directory}"
"$MIX1_ROOT/VERIFY.sh" package
exec "$MIX1_PYTHON" -B "$MIX1_ROOT/run.py" export --subset-receipt "$MIX1_SUBSET_RECEIPT" --subset-sha "$MIX1_SUBSET_SHA" --manifests "$MIX1_OUTPUT" --output "$MIX1_EXPORT_OUTPUT"
