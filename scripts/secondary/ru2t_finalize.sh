#!/usr/bin/env bash
# Offline only: no readers, probes, network or .git writes.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru2t.py" finalize "$@"
