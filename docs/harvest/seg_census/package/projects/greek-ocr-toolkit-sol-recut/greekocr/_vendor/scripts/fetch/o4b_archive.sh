#!/usr/bin/env bash
# Candidate list is a TSV despite its .txt suffix. Only verified=yes rows download.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
IDS="${1:-data/sources/o4b_archive_ids.txt}"
if [ "$#" -gt 0 ]; then shift; fi
exec "${PYTHON:-python3}" -m bench.o4b_fetch archive --ids "$IDS" --out "${RAW_ROOT:-data/raw}/o4b_archive" "$@"
