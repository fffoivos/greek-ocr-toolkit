#!/bin/bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")" && pwd)
exec "${MIX1_PYTHON:-python3}" -B "$ROOT/run.py" "$@"
