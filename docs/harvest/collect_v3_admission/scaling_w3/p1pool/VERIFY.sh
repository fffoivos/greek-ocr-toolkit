#!/usr/bin/env bash
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
if [[ -z "${PYTHON:-}" && -x /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python ]]; then export PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python; fi
exec "${PYTHON:-python3}" -B "$B/verify_p1pool.py" "${@:-package}"
