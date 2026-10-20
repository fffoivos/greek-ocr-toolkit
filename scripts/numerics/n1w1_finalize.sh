#!/usr/bin/env bash
# Offline finalisation only. Second invocation requires completed lead template.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s "$S/n1w1.py" finalize "$@"
