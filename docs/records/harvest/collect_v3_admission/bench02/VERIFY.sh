#!/usr/bin/env bash
# Run from the deployed repository root; optional argument is a census directory.
set -euo pipefail
[[ $# -le 1 ]] || { echo 'Usage: VERIFY.sh [CENSUS_DIRECTORY]' >&2; exit 2; }
B=docs/harvest/collect_v3_admission/bench02
sha256sum -c "$B/DEPLOY_SHA256SUMS" >&2
python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
[[ -f "$python" && -x "$python" ]]
export PYTHONDONTWRITEBYTECODE=1
"$python" -B -c 'import sys; assert sys.version_info >= (3, 10), "Python >=3.10 required"'
"$python" -B "$B/bench02_draw.py" --help >&2
if [[ $# -eq 1 ]]; then
  [[ -d "$1" ]]
  for name in decisions.jsonl evaluation_diagnostics.jsonl; do
    [[ -f "$1/$name" && -r "$1/$name" ]]
    # Opening read-only confirms access without streaming the multi-GB census.
    : < "$1/$name"
  done
fi
deploy_sha=$(sha256sum "$B/DEPLOY_SHA256SUMS")
printf 'VERIFY_OK bench02 %.8s\n' "$deploy_sha"
