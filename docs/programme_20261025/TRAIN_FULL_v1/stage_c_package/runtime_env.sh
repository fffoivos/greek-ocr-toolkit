#!/usr/bin/env bash
# Source after any owner-selected runtime/view. S1 used the direct wheel venv,
# with no uenv GPU-library view (record/launch_20261022/SUBMISSION.json).
export TF_PYTHON=${TF_PYTHON:-/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python}
[[ -x "$TF_PYTHON" ]]
unset LD_LIBRARY_PATH LD_PRELOAD
export PYTHONPATH="$TF_PACKAGE/vendor:$TF_PACKAGE" HUGETLB_ELFMAP=no
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 PYTHONFAULTHANDLER=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 SLURM_EXPORT_ENV=ALL
