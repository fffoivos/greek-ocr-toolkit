#!/usr/bin/env bash
# Prepared only: resume with context B. Never launch context A here.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python
RD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/segcp7r2_b/r1
[ ! -e "$RD/answers.jsonl" ] && [ ! -e "$D/r2/launchers/logs/SEG-CP7-segcp7r2_b-r1.codexlog" ] && [ ! -e "$D/r2/receipts/segcp7r2_b.json" ] || { echo 'Refuse rerun: context B outputs exist'; exit 8; }
# Preserve the strict pre-read closure for the new context.
"$PY" -B "$D/runtime_r2.py" pre-read segcp7r2_b
exec > >(tee -a "$D/run_r2.log") 2>&1
exec "$D/r2/launchers/run_bed.sh" segcp7r2_b r1
