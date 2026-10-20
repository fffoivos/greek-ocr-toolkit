#!/bin/bash
# Usage: bash submit_job.sh extract|readout CENSUS OUT [CANDIDATES]
set -euo pipefail
MODE="${1:?extract or readout}"; CENSUS="${2:?absolute census directory}"; OUT="${3:?absolute scratch output directory}"
case "$MODE" in extract|readout) ;; *) exit 2;; esac
case "$CENSUS" in /*) ;; *) echo 'Census directory must be absolute' >&2; exit 2;; esac
case "$OUT" in /iopsstor/scratch/*) ;; *) echo 'Output directory must be absolute scratch path' >&2; exit 2;; esac
export BENCH02_DIR="$(cd "$(dirname "$0")" && pwd)"
args=(--census-dir "$CENSUS" --output-dir "$OUT")
if [[ "$MODE" == readout ]]; then
 CANDIDATES="${4:?absolute candidates.jsonl path}"
 case "$CANDIDATES" in /*) ;; *) exit 2;; esac
 args+=(--candidates "$CANDIDATES")
fi
mkdir -p "$OUT"
sbatch --export=ALL --output="$OUT/$MODE-%j.log" "$BENCH02_DIR/$MODE.sbatch" "${args[@]}"
