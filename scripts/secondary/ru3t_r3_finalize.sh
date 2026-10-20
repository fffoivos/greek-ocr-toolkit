#!/usr/bin/env bash
# Replacement-aware offline finaliser. No readers or probes.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru3t_r3.py" finalize "$@"
