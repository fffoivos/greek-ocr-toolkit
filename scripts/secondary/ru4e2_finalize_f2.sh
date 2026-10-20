#!/usr/bin/env bash
# Local scans/recombination, unrun r5 construction, and PNG-only lead material.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
P=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
/usr/bin/arch -x86_64 "$P" -B "$S/ru4ef2_collect.py"
/usr/bin/arch -x86_64 "$P" -B "$S/ru4ef2_r5.py" build
/usr/bin/arch -x86_64 "$P" -B "$S/ru4ef2_png.py"
/usr/bin/arch -x86_64 "$P" -B "$S/ru4ef2_receipt.py"
