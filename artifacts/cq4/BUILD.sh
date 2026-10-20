#!/usr/bin/env bash
# Offline build only. Refuses to overwrite existing blind contexts.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
export PYTHONNOUSERSITE=1
PY=(/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B)
"${PY[@]}" "$S/tools/build.py"
"${PY[@]}" "$S/tools/finalize.py"
"${PY[@]}" "$S/tools/validate_build.py"
