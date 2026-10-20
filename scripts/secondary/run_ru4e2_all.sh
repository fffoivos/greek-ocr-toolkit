#!/usr/bin/env bash
# Explicit later invocation only. --dry-run performs no probe or glyph reading.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru4e2.py" drive "$@"
