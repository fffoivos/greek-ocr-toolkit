#!/usr/bin/env bash
# Dry-run by default. --execute is required to launch future blind reads.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru4ef2_r5.py" drive "$@"
