#!/usr/bin/env bash
# run_bed.sh adaptation: Q3 context, r1 only; pipeline in tools/run_type.py.
# Probe -> reading -> canonical scan -> copy/map -> probe -> ledger.
# Exit 8 = missing weekly probe or >=78%; exit 2 = scan VOID.
set -eu
S=$(cd "$(dirname "$0")" && pwd)
[ "$#" -ge 1 ] || { echo "usage: bash $0 <ctx> [--layout type|type2]" >&2; exit 1; }
exec /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B "$S/../tools/run_type.py" "$@"
