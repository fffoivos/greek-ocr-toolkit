#!/bin/bash
# Prepared only. Run explicitly after owner authorization for the full population.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../../.." && pwd)"
PYTHON="$ROOT/../greek-ocr-toolkit-sol-collect/.venv/bin/python"
OUT="$HOME/Projects/collect-v3-data/geometry_prep"
WORKERS="${1:-4}"
[[ "$WORKERS" =~ ^[1-9][0-9]*$ ]] || { echo 'workers must be positive' >&2; exit 1; }
mkdir -p "$OUT"
if [[ -f "$OUT/population.pid" ]] && kill -0 "$(cat "$OUT/population.pid")" 2>/dev/null; then
  echo 'Population preparation already running' >&2; exit 1
fi
# The Python entry point also fails closed below 10 GB, before submitting pages.
# A lock covers duplicate launch races; the worker wrapper removes it on exit.
mkdir "$OUT/launcher.lock" || { echo 'Launcher lock exists; inspect before retry' >&2; exit 1; }
nohup bash -c '
  trap '\''rmdir "$1/launcher.lock"'\'' EXIT
  export PYTHONPATH="$2" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  /usr/bin/nice -n 10 "$3" -B "$4/prepare_population_geometry.py" --workers "$5" --output "$1" &
  child=$!
  echo "$child" > "$1/population.pid"
  trap '\''kill -TERM "$child" 2>/dev/null || true; wait "$child" || true'\'' TERM INT
  wait "$child"
' population-worker "$OUT" "$ROOT" "$PYTHON" "$HERE" "$WORKERS" \
  >> "$OUT/population.log" 2>&1 < /dev/null &
echo "$!" > "$OUT/launcher.pid"
echo "Detached launcher PID $(cat "$OUT/launcher.pid"); progress: $OUT/progress.json"
