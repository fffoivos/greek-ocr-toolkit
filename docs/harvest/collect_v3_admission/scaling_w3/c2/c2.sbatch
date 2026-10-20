#!/bin/bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --job-name=C2-base-letter
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=128G
#SBATCH --time=01:00:00
#SBATCH --output=c2-%j.log
# CPU only. 1000 rows / 0.20600792 s = 4854.18 rows/s.
# Rows: 592180 / 4854.18 = 121.99 s. Bytes: 14,267,084,151 /
# 20,539,846 * 0.20600792 = 143.09 s. 10*max + 900 = 2330.94 s.
# Round upward to 1h (3600 s), including hashing/validation/readback margin.
set -euo pipefail
: "${C2_ROOT:?package root}"
: "${C2_PYTHON:?Python with pyarrow}"
: "${C2_OUTPUT:?exact new C2 output attempt}"
export E4_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel3_20261020/code/27a49e51fa735e8f
"$C2_ROOT/VERIFY.sh" package
"$C2_ROOT/VERIFY.sh" inputs
exec "$C2_PYTHON" -B "$C2_ROOT/build_c2.py" build --output "$C2_OUTPUT"
