#!/usr/bin/env bash
# Explicit operator launch only. --dry-run never probes or reads.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s "$S/n1w1_r3_driver.py" "$@"
