#!/bin/bash
set -euo pipefail
C2_ROOT=$(cd -- "$(dirname -- "$0")" && pwd)
exec "${C2_PYTHON:-python3}" -B "$C2_ROOT/build_c2.py" "${1:-package}"
