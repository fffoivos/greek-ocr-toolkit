#!/usr/bin/env bash
# Source from a set -euo pipefail shell after exporting the census environment.
export PYTHONPATH="${CENSUS_CODE:-$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut}"
PROJECTS_SUMS="${CENSUS_MANIFEST:-${PROJECTS_SUMS:-$CENSUS_PROJECTS/SHA256SUMS}}"
PROJECTS_SUMS_ROOT="${PROJECTS_SUMS_ROOT:-$CENSUS_PROJECTS}"
PROJECTS_SUMS="$(cd "$(dirname "$PROJECTS_SUMS")" && pwd)/$(basename "$PROJECTS_SUMS")"
checksum() {
  if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi
}
[[ "$(checksum "$PROJECTS_SUMS" | cut -d' ' -f1)" == "$PROJECTS_SHA256" ]] || { echo 'manifest sha mismatch' >&2; exit 1; }
# Submit-time census manifests use the existing code-root checksum convention.
if [[ -n "${CENSUS_MANIFEST:-}" ]]; then
  [[ "$(basename "$PROJECTS_SUMS_ROOT")" == "${PROJECTS_SHA256:0:16}" ]] || { echo 'manifest/code-dir name mismatch' >&2; exit 1; }
fi
(cd "$PROJECTS_SUMS_ROOT" && checksum -c "$PROJECTS_SUMS")
# Bind the reconstruction module selected for import to an entry in the checked manifest.
MODULE_REL="$("$PYTHON" -B -c 'import os,sys; print(os.path.relpath(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])))' "$PYTHONPATH/greekocr/harvest/line_pipeline_native.py" "$PROJECTS_SUMS_ROOT")"
awk -v path="$MODULE_REL" 'substr($0,67)==path {found=1} END {exit !found}' "$PROJECTS_SUMS" || { echo "reconstruction module not in PROJECTS_SUMS: $MODULE_REL" >&2; exit 1; }
RECONSTRUCTION_SHA256="${RECONSTRUCTION_SHA256:-e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7}"
"$PYTHON" -B - "$PYTHONPATH" "$RECONSTRUCTION_SHA256" <<'PYTHON'
import hashlib, pathlib, sys
sys.path.insert(0, sys.argv[1])
import greekocr.harvest.line_pipeline_native as module
path = pathlib.Path(module.__file__).resolve()
assert path.is_relative_to(pathlib.Path(sys.argv[1]).resolve()), 'reconstruction imported outside census code tree'
actual = hashlib.sha256(path.read_bytes()).hexdigest()
assert actual == sys.argv[2], f'reconstruction sha mismatch: {actual}'
print('RECONSTRUCTION_OK', actual)
PYTHON
