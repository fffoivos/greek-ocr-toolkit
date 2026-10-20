#!/bin/bash
set -euo pipefail
PKG='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90'
PY='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python'
export PYTHONDONTWRITEBYTECODE=1
case "${1:-}" in
 package|inputs-tags) exec "$PY" "$PKG/scale.py" verify --mode "$1" ;;
 inputs-subsets)
   if [[ $# == 1 ]]; then exec "$PY" "$PKG/scale.py" verify --mode inputs-subsets; fi
   [[ $# == 3 ]] || { echo 'usage: VERIFY.sh inputs-subsets [ABS_TAGS_RECEIPT SHA256]' >&2; exit 2; }
   exec "$PY" "$PKG/scale.py" verify --mode inputs-subsets --tags-receipt "$2" --tags-receipt-sha "$3" ;;
 *) echo 'usage: VERIFY.sh package|inputs-tags|inputs-subsets' >&2; exit 2 ;;
esac
