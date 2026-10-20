#!/usr/bin/env bash
set -euo pipefail
set +x
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PYTHON=${COLLECT_V3_PYTHON:-$ROOT/worker/.venv/bin/python}
exec "$PYTHON" worker/control.py launch "$@"
