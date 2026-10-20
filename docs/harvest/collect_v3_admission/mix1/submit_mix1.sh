#!/bin/bash
# Coordinator only; this script is never called by qualification/deployment.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")" && pwd)
export MIX1_ROOT="$ROOT"
: "${MIX1_PYTHON:?Python with pyarrow and Pillow}"
: "${MIX1_SUBSET_RECEIPT:?subset receipt path}"
: "${MIX1_SUBSET_SHA:?subset receipt SHA}"
: "${MIX1_OUTPUT:?new manifests output directory}"
"$ROOT/VERIFY.sh" package >&2
"$ROOT/VERIFY.sh" inputs --subset-receipt "$MIX1_SUBSET_RECEIPT" --subset-sha "$MIX1_SUBSET_SHA" >&2
case "${1:-}" in
 manifests) exec sbatch --parsable --export=ALL "$ROOT/manifests.sbatch" ;;
 export)
  : "${MIX1_EXPORT_OUTPUT:?new export output directory}"
  : "${MIX1_MANIFESTS_JOB:?successful manifests job id for afterok dependency}"
  "$MIX1_PYTHON" -B -c 'import json,sys; x=json.load(open(sys.argv[1])); assert x["status"]=="ok", "EXPORT stopped: "+"; ".join(x["gaps"])' "$ROOT/EXPORT_STATUS.json"
  exec sbatch --parsable --dependency="afterok:$MIX1_MANIFESTS_JOB" --export=ALL "$ROOT/export.sbatch" ;;
 *) printf 'Usage: %s manifests|export\n' "$0" >&2; exit 2 ;;
esac
