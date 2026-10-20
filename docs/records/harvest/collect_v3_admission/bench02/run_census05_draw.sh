#!/bin/bash
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"
P="${PROJECTS_ROOT:-$HOME/Projects}"
A="$(dirname "$B")"
if [[ -f "$A/split2/row_split.jsonl.gz" ]]; then
 SPLIT="$A/split2/row_split.jsonl.gz"
 EDITIONS=("$A/split1/editions.jsonl" "$A/split2/edition_map.jsonl")
else
 SPLIT="$A/split1/row_split_proposal.jsonl.gz"
 EDITIONS=("$A/split1/editions.jsonl")
fi
python3 -B "$B/bench02_draw.py" draw \
 --tags "$B/census05/tags.jsonl.gz" --split "$SPLIT" --editions "${EDITIONS[@]}" \
 --features "$P/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl" "$P/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl" \
 --v2 "$P/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl" "$P/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_dev.jsonl" "$P/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl" \
 --exclusions "$P/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/release_exclusions.json" \
 --require-receipt-sha --output "$B/census05"
