#!/usr/bin/env bash
# PREPARED ONLY: the lead invokes this after handoff; never used during building.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python
"$PY" -B "$D/tools/runtime.py" verify
"$D/launchers/run_bed.sh" segeval1_a r1
"$D/launchers/run_bed.sh" segeval1_b r1
"$PY" -B "$D/segeval1_score.py" --answers-a "$D/answers/segeval1_a/r1.jsonl" --answers-b "$D/answers/segeval1_b/r1.jsonl" --scan-a "$D/scan/segeval1_a/r1.scan.json" --scan-b "$D/scan/segeval1_b/r1.scan.json" --out "$D/scored"
