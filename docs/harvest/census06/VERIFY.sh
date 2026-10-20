#!/usr/bin/env bash
# Binding check supplements, and never replaces, the unchanged external verifier.
set -euo pipefail
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python=${CENSUS06_PYTHON:-python3}
exec "$python" -B "$bundle/binding_state.py" "$@"
