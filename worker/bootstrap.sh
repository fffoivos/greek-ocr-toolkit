#!/usr/bin/env bash
# Default: offline, sealed wheels only. Never downloads or launches collection.
set -euo pipefail
set +x
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1 OMP_THREAD_LIMIT=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export COLLECT_V3_FIXTURE_ROOT=${COLLECT_V3_FIXTURE_ROOT:-$ROOT/worker/fixtures}
MODE=${1:-}
if [[ $MODE == --verify-only && $# == 1 ]]; then
  # Coordination-host offline proof; no live preflight or installation claim.
  exec "${COLLECT_V3_PYTHON:-python3}" worker/offline_check.py
fi
[[ $# == 0 ]] || { echo 'Usage: bootstrap.sh [--verify-only]' >&2; exit 2; }
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { echo 'Linux x86_64 required' >&2; exit 1; }
. /etc/os-release
[[ ${ID:-} == debian && ${VERSION_ID:-} == 12 ]] || { echo 'Supported distro: Debian 12' >&2; exit 1; }
for cmd in rsync setsid nohup ps git; do command -v "$cmd" >/dev/null || { echo "Missing system package command: $cmd" >&2; exit 1; }; done
BASE_PYTHON=${COLLECT_V3_BASE_PYTHON:-/opt/collect-v3-python/bin/python3.11}
"$BASE_PYTHON" -c 'import sys,ssl,sqlite3,venv; assert sys.version_info[:3] == (3,11,3), "CPython 3.11.3 required"'
if [[ ! -x worker/.venv/bin/python ]]; then "$BASE_PYTHON" -m venv worker/.venv; fi
PYTHON=$ROOT/worker/.venv/bin/python
"$PYTHON" -c 'import sys; assert sys.version_info[:3] == (3,11,3)'
WHEELS=${COLLECT_V3_WHEELHOUSE:-$ROOT/worker/wheelhouse}
"$PYTHON" worker/wheels.py "$WHEELS"
"$PYTHON" -m pip install --no-index --no-deps --only-binary=:all: --find-links "$WHEELS" -r worker/requirements.lock
"$PYTHON" -m pip check
"$PYTHON" worker/offline_check.py
"$PYTHON" worker/prepare.py
"$PYTHON" worker/preflight.py
