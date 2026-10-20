#!/bin/bash
#SBATCH --job-name=release-v3
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v3/rel3-%j.log
# submit_release_v3.sh supplies an absolute --output and this package's absolute path.
set -euo pipefail
ROOT=$1
OUTPUT=$2
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PYTHONDONTWRITEBYTECODE=1
bash "$ROOT/VERIFY.sh" package
bash "$ROOT/VERIFY.sh" inputs
exec "$W/venv_l1/bin/python" -B "$ROOT/build_release_v3.py" --config "$ROOT/INPUTS.json" --output "$OUTPUT"
