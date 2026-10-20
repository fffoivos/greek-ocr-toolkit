#!/bin/bash
# Coordinator entry point. Never invoked by package verification.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
if [[ $# != 1 || ! "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ || "$1" == pkg ]]; then
  echo 'usage: submit_release_v4.sh NEW_ATTEMPT_NAME' >&2
  exit 64
fi
OUTPUT="$W/release_v4/$1"
[[ ! -e "$OUTPUT" ]] || { echo 'attempt already exists' >&2; exit 1; }
bash "$ROOT/VERIFY.sh" package
bash "$ROOT/VERIFY.sh" inputs
# Log lives in existing release_v4 root; the builder exclusively creates the attempt.
TIME=$("$W/venv_l1/bin/python" -B "$ROOT/size_release_v4.py" --config "$ROOT/INPUTS.json" --field time)
MEM=$("$W/venv_l1/bin/python" -B "$ROOT/size_release_v4.py" --config "$ROOT/INPUTS.json" --field memory_gib)
exec sbatch --time="$TIME" --mem="${MEM}G" --output="$W/release_v4/rel4-$1-%j.log" "$ROOT/release_v4.sbatch" "$ROOT" "$OUTPUT"
