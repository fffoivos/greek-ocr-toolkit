#!/usr/bin/env bash
# Explicit later reader invocation. --dry-run does not probe or read glyphs.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
exec /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/ru4ef1.py" drive "$@"
