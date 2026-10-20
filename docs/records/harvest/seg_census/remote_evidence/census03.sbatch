#!/usr/bin/env bash
# Cloned payload order/environment from frozen filter_worker.sbatch, census_02.
# Census_02 accounting: normal; elapsed 01:46:11; limit 06:00:00; step CPUs 256.
# FP3 owner instruction: same partition, time 04:00:00. NO SUBMISSION BY FP3.
# Existing predictor is hash-bound: no Cargo build or runtime-tree mutation.
# The original common.sh writes outside FP3's boundary, so use its same srun
# invocation directly with all outputs and temporary files inside this attempt.
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH --time=04:00:00
#SBATCH --job-name=ocr_filter_census03
#SBATCH --output=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/slurm-%j.log
set -euo pipefail
root=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018
attempt=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03
projects=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/code/87407ec7430a375f/projects
config=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/census_w64_pf64.json
python="$root/../venv_l1/bin/python"
mkdir -p "$attempt/tmp" "$attempt/cache"
cd "$attempt"
export TMPDIR="$attempt/tmp" XDG_CACHE_HOME="$attempt/cache"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export LD_PRELOAD="$root/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export PATH="$root/runtime/node-v22.23.3-linux-arm64/bin:$PATH"
export PYTHONPATH="$projects/greek-ocr-toolkit-sol-recut"
[[ "$(sha256sum "$projects/SHA256SUMS" | cut -d' ' -f1)" == "7c885291db4b661b026ffdad9f3c6d9e5f7a6dcdb426ddda7b2bdc8f037ea05c" ]]
(cd "$projects"; sha256sum --check --quiet SHA256SUMS)
[[ "$(sha256sum "$config" | cut -d' ' -f1)" == "b945ffa6bc16cd5c137223f4b48748bf9c31f5ce900fa393473a2bbe427c5b5a" ]]
run_step() {
  srun -A a0140 --partition="${SLURM_JOB_PARTITION:?}" --cpu-bind=none --nodes=1 --ntasks=1 "$@"
}
run_step "$python" -B -m pytest -q -p no:cacheprovider --basetemp="$attempt/job-test-tmp" \
  "$PYTHONPATH/tests/test_line_pipeline.py" "$PYTHONPATH/tests/test_fp3_numeric_adjacency.py" "$PYTHONPATH/tests/test_fp3_external_crop_input.py"
run_step "$python" -B "$PYTHONPATH/scripts/harvest/verify_filter_parity.py" \
  --review-root "$projects/ocr-review-sites-20261018" \
  --predictor "$root/runtime/rust-target/release/greekocr-frozen-font-predict" --out "$attempt/job-policy-parity.json"
run_step "$python" -B -m greekocr.harvest.line_pipeline_census "$config" --out "$attempt" --execute
