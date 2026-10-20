#!/bin/bash
#SBATCH --job-name=scale1-tags
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/tags/scale1-%j.log
set -euo pipefail
PKG='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
export PYTHONDONTWRITEBYTECODE=1
"$PKG/VERIFY.sh" package
exec "$W/venv_l1/bin/python" "$PKG/scale.py" tags --output "$W/scaling_w3/tags/$1"
