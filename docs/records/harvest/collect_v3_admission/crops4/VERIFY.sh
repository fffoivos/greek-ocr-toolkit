#!/usr/bin/env bash
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"
if command -v sha256sum >/dev/null; then
  (cd "$B" && sha256sum --check DEPLOY_SHA256SUMS) >&2
else
  (cd "$B" && shasum -a 256 -c DEPLOY_SHA256SUMS) >&2
fi
if [[ "${1:-}" == --deploy-only ]]; then
  [[ $# == 1 ]]
  [[ -z "${LD_PRELOAD:-}" || -r "$LD_PRELOAD" ]]
  "${PYTHON:?set PYTHON to census interpreter}" -B -c 'import sys,PIL; print("PYTHON",sys.version.split()[0]); print("PIL",PIL.__version__)'
  printf 'VERIFY_DEPLOY_OK crops4 %s\n' "$(basename "$B")"
  exit 0
fi
"${PYTHON:?set PYTHON to census interpreter}" -B "$B/materialise_crops.py" --verify-only "$@"
