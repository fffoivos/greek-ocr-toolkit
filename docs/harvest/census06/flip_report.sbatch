#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --job-name=census06_flips
set -euo pipefail
: "${CENSUS06_BUNDLE:?}"
W=${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}
"${CENSUS06_PYTHON:-$W/venv_l1/bin/python}" -B "$CENSUS06_BUNDLE/flip_report.py" \
 --before "$W/census_05_20261020/attempts/full-split-001" \
 --after "$W/census_06_20261020/attempts/full-split-002" \
 --out "$W/census_06_20261020/attempts/full-split-002.flips"
