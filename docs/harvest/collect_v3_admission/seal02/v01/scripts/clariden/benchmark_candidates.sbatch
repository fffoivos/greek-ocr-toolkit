#!/usr/bin/env bash
# Bounded benchmark candidate/evaluation evidence build, not a training-data release.
# Reuse the existing allocation/receipt helper; no submit/retry controller.
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:40:00
set -euo pipefail
bundle=${1:?immutable benchmark source}
toolkit=${2:?existing frozen source adapter}
helper=${3:?existing frozen common.sh}
config=${4:?bound benchmark configuration}
output=${5:?new immutable benchmark output}
source_sha=${6:?benchmark source manifest SHA}
config_sha=${7:?configuration SHA}
[[ "$(sha256sum "$bundle/SHA256SUMS" | cut -d' ' -f1)" == "$source_sha" ]]
[[ "$(sha256sum "$config" | cut -d' ' -f1)" == "$config_sha" ]]
(cd "$bundle"; sha256sum --check --quiet SHA256SUMS)
[[ ! -e "$output" ]]
source "$helper" "out/benchmark_candidates/${SLURM_JOB_ID:?}"
python="$W/venv_l1/bin/python"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$toolkit"
export OCR_BENCHMARK_TOOLKIT="$toolkit"
codec_manifest="$W/filter_pipeline_20261018/runtime/png-codec.json"
lib=$($python -B -c 'import json,hashlib,sys;m=json.load(open(sys.argv[1]));p=m["library"];assert hashlib.sha256(open(p,"rb").read()).hexdigest()==m["sha256"];print(p)' "$codec_manifest")
export LD_PRELOAD="$lib"
E3_PYTHON=("$python")
run_step "$python" -B -c 'import sys;sys.path.insert(0,sys.argv[1]);import pytest;raise SystemExit(pytest.main(["-q","--rootdir",sys.argv[1],"--confcutdir",sys.argv[1],sys.argv[1]+"/bench/tests/test_benchmark_suite.py"]))' "$bundle"
run_step "$python" -B -c 'import sys;sys.path.insert(0,sys.argv.pop(1));from bench.benchmark_build import main;main()' "$bundle" --config "$config" --out "$output"
