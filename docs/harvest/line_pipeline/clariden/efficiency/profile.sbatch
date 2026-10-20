#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=00:10:00
set -euo pipefail
projects=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/fd4d5e20283b4f1b/projects
(cd "$projects"; sha256sum --check --quiet SHA256SUMS)
source "$projects/greek-page-ocr-wave2/scripts/clariden/common.sh" "out/filter_profile/${SLURM_JOB_ID:?}"
E3_PYTHON=(/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/../venv_l1/bin/python)
run_step "${E3_PYTHON[@]}" -B /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/profile_native.py --projects "$projects" --root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018 --out /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/profile_01
