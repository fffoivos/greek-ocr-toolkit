#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH --time=00:10:00
set -euo pipefail
projects=${1:?projects}
root=${2:?root}
output=${3:?new output}
script=${4:?pilot script}
script_sha=${5:?pilot hash}
[[ ! -e "$output" ]]
[[ "$(sha256sum "$script" | cut -d' ' -f1)" == "$script_sha" ]]
(cd "$projects"; sha256sum --check --quiet SHA256SUMS)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python="$root/../venv_l1/bin/python"
lib=$($python -B -c 'import hashlib,json,sys;m=json.load(open(sys.argv[1]));p=m["library"];assert hashlib.sha256(open(p,"rb").read()).hexdigest()==m["sha256"];print(p)' "$root/runtime/png-codec.json")
export LD_PRELOAD="$lib"
node=$($python -B -c 'import json,sys;print(json.load(open(sys.argv[1]))["node"])' "$root/runtime/node.json")
export PATH="$(dirname "$node"):$PATH"
source "$projects/greek-page-ocr-wave2/scripts/clariden/common.sh" "out/filter_throughput/${SLURM_JOB_ID:?}"
E3_PYTHON=("$python")
run_step "$python" -B "$script" --projects "$projects" --root "$root"     --configs "$root/attempts/scaling_04/qualify/config_w64_pf16.json" "$root/attempts/scaling_04/qualify/config_w64_pf32.json" "$root/attempts/scaling_04/qualify/config_w64_pf64.json"     --out "$output" --per-parent 2048
