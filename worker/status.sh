#!/usr/bin/env bash
set -euo pipefail
set +x
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PYTHON=${COLLECT_V3_PYTHON:-$ROOT/worker/.venv/bin/python}
if [[ ${1:-} == --stop && $# == 1 ]]; then
  exec "$PYTHON" worker/control.py stop
fi
[[ $# == 0 ]] || { echo 'Usage: status.sh [--stop]' >&2; exit 2; }
exec "$PYTHON" worker/control.py status
