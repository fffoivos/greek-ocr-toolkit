#!/usr/bin/env bash
# Explicit later invocation runs a reading; ctx02 and ctx03 use r1/r3 (r2 is VOID).
# Offline preparation check: run_ru2t.sh ru2t ctx03 r3 --dry-run
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/../ru2t_launch.py" "$@"
