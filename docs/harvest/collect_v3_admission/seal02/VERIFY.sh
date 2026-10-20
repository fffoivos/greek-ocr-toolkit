#!/usr/bin/env bash
set -euo pipefail
B=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PY=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
# Local tests may explicitly override the interpreter. Deployment uses the fixed venv.
PY=${SEAL02_PYTHON:-$PY}
export PYTHONDONTWRITEBYTECODE=1
exec "$PY" -B "$B/build_suite02.py" verify "$@"
