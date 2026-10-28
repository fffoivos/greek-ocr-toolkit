#!/usr/bin/env bash
# Copy the Stage B search records (configs, loss curves, final scores, train logs, submit receipts)
# from Clariden into this folder, then rebuild summary.csv. Checkpoints and per-line
# predictions stay on Clariden (paths in README.md). Safe to rerun; only overwrites copies.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-009-stage-b-h1/study
mkdir -p "$HERE/runs" "$HERE/trials" "$HERE/submit-controls"
rsync -rt "clariden:$W/PLAN.json" "$HERE/PLAN.json"
rsync -rt "clariden:$W/trials/" "$HERE/trials/"
rsync -rt --include='*.json' --include='*.log' --exclude='*' "clariden:$W/submit-controls/" "$HERE/submit-controls/"
rsync -rt --prune-empty-dirs \
  --include='*/' --include='loss_eval.jsonl' --include='train_log.csv' --include='COMPLETE.json' \
  --include='LOSS_CADENCE.json' --include='eval/step-*[0-9].json' --include='FAILURE_*.json' \
  --exclude='*' "clariden:$W/runs/" "$HERE/runs/"
python3 "$HERE/summarize.py" "$HERE"
