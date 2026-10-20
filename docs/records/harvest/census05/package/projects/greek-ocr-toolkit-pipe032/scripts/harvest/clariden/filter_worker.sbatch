#!/usr/bin/env bash
# Thin payload adapter: reuse the established Greek OCR srun/receipt helper.
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:45:00
set -euo pipefail
projects=${1:?immutable projects bundle}
root=${2:?run workspace}
mode=${3:?qualify or inventory}
output=${4:?new attempt output directory}
manifest_sha=${5:?bound code manifest SHA256}
[[ "$mode" == qualify || "$mode" == inventory || "$mode" == prepare || "$mode" == census || "$mode" == census-preflight ]]
[[ "$mode" == census || ! -e "$output" ]]
[[ "$(sha256sum "$projects/SHA256SUMS" | cut -d' ' -f1)" == "$manifest_sha" ]]
(cd "$projects"; sha256sum --check --quiet SHA256SUMS)
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR="$root/runtime/rust-target"
toolkit="$projects/greek-ocr-toolkit-sol-recut"
python="$root/../venv_l1/bin/python"
lib=$($python -B -c 'import hashlib,json,sys; m=json.load(open(sys.argv[1]));p=m["library"];assert hashlib.sha256(open(p,"rb").read()).hexdigest()==m["sha256"];print(p)' "$root/runtime/png-codec.json")
export LD_PRELOAD="$lib"
node=$($python -B -c 'import json,sys;print(json.load(open(sys.argv[1]))["node"])' "$root/runtime/node.json")
export PATH="$(dirname "$node"):$PATH"
export PYTHONPATH="$toolkit"
source "$projects/greek-page-ocr-wave2/scripts/clariden/common.sh" "out/filter_pipeline/${SLURM_JOB_ID:?}"
E3_PYTHON=("$python")
mkdir -p "$output"
run_step cargo build --release --locked --offline --manifest-path "$toolkit/scripts/harvest/filter_runtime/Cargo.toml"
run_step "$python" -B -m pytest -q "$toolkit/tests/test_line_pipeline.py"
run_step "$python" -B "$toolkit/scripts/harvest/verify_filter_parity.py" \
    --review-root "$projects/ocr-review-sites-20261018" \
    --predictor "$root/runtime/rust-target/release/greekocr-frozen-font-predict" --out "$output/policy-parity.json"
run_step "$python" -B "$toolkit/scripts/harvest/clariden/worker.py" "$mode" \
    --root "$root" --out "$output/$mode" "${@:6}"
