#!/usr/bin/env bash
# Phase-1 routing extension; original hash-bound protocol remains unchanged.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru4ef1.py" finalize "$@"
