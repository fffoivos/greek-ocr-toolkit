#!/usr/bin/env bash
set -euo pipefail
# Lead only: --extra-attempt candidate_w2_00004 candidate_w2_00013 authorizes attempt 3.
# --contexts selects a roster, including its sealed per-context vertical prompt.
LF1_DIR=$(cd "$(dirname "$0")" && pwd)
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$LF1_DIR/tools/run.py" "$@"
