#!/usr/bin/env bash
set -euo pipefail
A=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$A/driver.py" run "$@"
