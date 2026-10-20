#!/bin/bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PYTHON=${REL4_PYTHON:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python}
export PYTHONDONTWRITEBYTECODE=1
exec "$PYTHON" -B "$ROOT/verify_release_v4.py" "${@:-package}"
