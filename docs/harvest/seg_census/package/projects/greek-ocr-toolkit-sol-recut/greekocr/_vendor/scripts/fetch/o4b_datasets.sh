#!/usr/bin/env bash
# Network-enabled coordinator only; discover metadata or fetch reviewed checksum-pinned payloads.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec "${PYTHON:-python3}" -m bench.o4b_fetch "${@}"
