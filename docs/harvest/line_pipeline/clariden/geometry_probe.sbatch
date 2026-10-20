#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:05:00
set -euo pipefail
export LD_PRELOAD=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PATH=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/runtime/node-v22.23.3-linux-arm64/bin:$PATH
srun --cpu-bind=none /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/../venv_l1/bin/python -B /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/geometry_probe.py /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/d67c76bc6e93e8ae/projects /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018
