#!/usr/bin/env bash
set -euo pipefail
A=$(cd "$(dirname "$0")" && pwd)
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
/usr/bin/arch -x86_64 "$PY" -B "$A/driver.py" reread
if [[ "${1:-}" == "--build-only" ]]; then exit 0; fi
/usr/bin/arch -x86_64 "$PY" -B "$A/driver.py" resume-rereads
