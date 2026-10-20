#!/usr/bin/env bash
# No reader, network, limit probe, collector/cleanup or .git writes.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$S/../.." && pwd)
export PYTHONPATH="$R${PYTHONPATH:+:$PYTHONPATH}"
exec "$HOME/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python" -B "$S/ru1_finalize_r3.py" "$@"
