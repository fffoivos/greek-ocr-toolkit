#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --time=02:00:00
#SBATCH --job-name=p1pool-select
set -euo pipefail
: "${P1POOL_PACKAGE:?}" "${REL4_CONFIG:?bound completed REL4 config}" "${ATTEMPT:?}"
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PYTHONDONTWRITEBYTECODE=1
bash "$P1POOL_PACKAGE/VERIFY.sh" package
"$W/venv_l1/bin/python" -B "$P1POOL_PACKAGE/build_p1pool.py" --rel4-config "$REL4_CONFIG" --attempt "$ATTEMPT" --output "$W/scaling_w3/p1pool_attempts/$ATTEMPT"
