#!/usr/bin/env bash
# Source after W/runtime.sh. Match successful wave-1c job 3686532: wheel venv,
# no uenv view, no LD_LIBRARY_PATH or LD_PRELOAD. Never edit the shared runtime.
unset LD_LIBRARY_PATH LD_PRELOAD
export PYTHONPATH="${E4_ROOT:?}" PYTHONDONTWRITEBYTECODE=1
export PYTHONFAULTHANDLER=1 HUGETLB_ELFMAP=no
export GIT_OPTIONAL_LOCKS=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 SLURM_EXPORT_ENV=ALL
# Retain S1's existing deterministic-workspace setting.
export CUBLAS_WORKSPACE_CONFIG=:4096:8
run_step() {
  srun -A a0140 --partition="${SLURM_JOB_PARTITION:?Slurm allocation required}" \
    --cpu-bind=none --nodes=1 --ntasks=1 env -u LD_LIBRARY_PATH -u LD_PRELOAD \
    PYTHONPATH="$E4_ROOT" PYTHONFAULTHANDLER=1 HUGETLB_ELFMAP=no "$@"
}
