#!/usr/bin/env bash
# Offline evidence processing only. --apply-lead requires completed pixel checks.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru4e.py" finalize "$@"
