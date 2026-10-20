#!/usr/bin/env bash
# Explicit later execution only; --dry-run is offline and launches nothing.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/../ru3t_r5.py" drive "$@"
