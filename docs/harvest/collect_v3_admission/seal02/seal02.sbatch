#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
set -euo pipefail
B=${1:?absolute package root}
CONFIG=${2:?absolute bound inputs file}
CONFIG_SHA=${3:?bindings sha256}
OUTPUT=${4:?absolute new output}
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
[[ "$B" == /* && "$CONFIG" == /* && "$OUTPUT" == "$W"/benchmark_0.2/* && ! -e "$OUTPUT" ]]
[[ $(sha256sum "$CONFIG" | cut -d' ' -f1) == "$CONFIG_SHA" ]]
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset SEAL02_PYTHON
bash "$B/VERIFY.sh" package
# A production build has no --mock switch in this launcher.
exec "$W/venv_l1/bin/python" -B "$B/build_suite02.py" build --bindings "$CONFIG" --output "$OUTPUT"
