#!/bin/bash
#SBATCH --job-name=scale1-subsets
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/subsets/scale1-%j.log
set -euo pipefail
PKG='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
export PYTHONDONTWRITEBYTECODE=1
"$PKG/VERIFY.sh" package
exec "$W/venv_l1/bin/python" "$PKG/scale.py" subsets --output "$W/scaling_w3/subsets/$1" --tags-receipt "$2" --tags-receipt-sha "$3"
