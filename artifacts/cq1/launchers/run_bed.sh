#!/usr/bin/env bash
# CQ1 copy of the run_bed driver; paths and pipeline live in the reviewable handoff.
set -euo pipefail
S=$(cd "$(dirname "$0")/.." && pwd)
W=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2cards
[ "${1:-cap1}" = cap1 ] && [ "${2:-r1}" = r1 ] || exit 8
exec bash "$S/RUN_CMD.sh"
