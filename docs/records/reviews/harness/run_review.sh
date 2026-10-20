#!/usr/bin/env bash
# One cross-session review. Read-only sandbox: a certifier that can edit what it certifies is not one.
# The model is asserted from the session ROLLOUT FILE, never from what the reviewer says about itself.
# Usage: run_review.sh <label> <brief.md> [model] [effort]
# DO NOT add `-c features.code_mode_host=false`: it disables the reviewer's shell (memory, Sept 2026).
set -u
LABEL="$1"; BRIEF="$2"; MODEL="${3:-gpt-6.1-sol}"; EFFORT="${4:-xhigh}"
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
RDIR="$REPO/docs/reviews/astra_program_review_2026-10-06"; mkdir -p "$RDIR"
OUT="$RDIR/${LABEL}_review_1.md"; LOG="$RDIR/${LABEL}_review_1.codexlog"
BEFORE=$(date +%s)
echo "[$(date '+%H:%M:%S')] REVIEW START $LABEL model=$MODEL effort=$EFFORT"
# v2 (6 Oct, CP0 V1): read-only sandbox blocked ALL temp writes, so the reviewer could not run pytest or the CLI.
# Now: workspace-write sandbox with cwd = a scratch dir OUTSIDE the repo. The repo stays read-only (outside the
# writable roots) and that is PROVEN after the run: any repo file newer than the start marker fails the review.
SCRATCH="$HOME/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/$LABEL"
mkdir -p "$SCRATCH"; MARK="$SCRATCH/.start_marker"; touch "$MARK"; sleep 1
DIFF_BEFORE=$(git -C "$REPO" diff | shasum | cut -c1-12)
{ echo "Repository root (READ-ONLY, use absolute paths or \`cd $REPO\` in each command; writes there are blocked): $REPO"
  echo "Writable scratch for temporary outputs: $SCRATCH (your cwd) and /tmp. Run pytest from the repo root with"
  echo "PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider so it never writes into the repository."
  echo; cat "$BRIEF"; } > "$SCRATCH/prompt.md"
codex exec -m "$MODEL" -c "model_reasoning_effort=$EFFORT" \
  -c project_doc_max_bytes=0 \
  -c features.remote_plugin=false -c features.apps=false \
  --sandbox workspace-write --skip-git-repo-check -C "$SCRATCH" -o "$OUT" - < "$SCRATCH/prompt.md" > "$LOG" 2>&1
RC=$?
# REVIEW_IGNORE_REGEX: paths a DISCLOSED concurrent implementer may touch during this review (recorded in STATE.md).
TOUCHED=$(find "$REPO" -type f -newer "$MARK" -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' -not -path "$REPO/docs/reviews/astra_program_review_2026-10-06/*" 2>/dev/null | { if [ -n "${REVIEW_IGNORE_REGEX:-}" ]; then grep -Ev "$REVIEW_IGNORE_REGEX" || true; else cat; fi; })
DIFF_IGNORE_NOTE=""; [ -n "${REVIEW_IGNORE_REGEX:-}" ] && DIFF_IGNORE_NOTE=" (git-diff hash check skipped: concurrent implementer disclosed, regex '$REVIEW_IGNORE_REGEX')"
DIFF_AFTER=$(git -C "$REPO" diff | shasum | cut -c1-12)
SID=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -m1 -oE 'session id: [0-9a-f-]+' | awk '{print $3}')
ROLL=""; [ -n "$SID" ] && ROLL=$(ls "$HOME"/.codex/sessions/*/*/*/rollout-*"$SID".jsonl 2>/dev/null | head -1)
ACTUAL=""; [ -n "$ROLL" ] && ACTUAL=$(python3 -c "
import json,sys
for l in open(sys.argv[1]):
    try: o=json.loads(l)
    except Exception: continue
    p=o.get('payload') or {}
    if isinstance(p,dict) and isinstance(p.get('model'),str): print(p['model']); break
" "$ROLL")
echo "[$(date '+%H:%M:%S')] REVIEW END $LABEL rc=$RC elapsed=$(( ($(date +%s)-BEFORE)/60 ))m"
echo "  requested=$MODEL  asserted=${ACTUAL:-UNKNOWN}  rollout=${ROLL##*/}"
[ -n "$ACTUAL" ] || { echo "  !! MODEL NOT ASSERTED (session id '${SID:-none}') - treat as NOT certified"; exit 9; }
[ "$ACTUAL" = "$MODEL" ] || { echo "  !! MODEL MISMATCH requested $MODEL, ran $ACTUAL"; exit 9; }
case "${ACTUAL:-}" in *claude*|*opus*|*fable*) echo "  !! SAME-FAMILY AS COORDINATOR"; exit 9;; esac
[ -s "$OUT" ] || { echo "  !! no review produced"; exit 9; }
if [ -n "$TOUCHED" ] || { [ -z "${REVIEW_IGNORE_REGEX:-}" ] && [ "$DIFF_BEFORE" != "$DIFF_AFTER" ]; }; then
  echo "  !! REPO MODIFIED DURING REVIEW (diff $DIFF_BEFORE -> $DIFF_AFTER):"; echo "$TOUCHED" | head -20; echo "  treat as NOT certified"; exit 9
fi
echo "  repo integrity: no undisclosed file touched (diff hash $DIFF_BEFORE)$DIFF_IGNORE_NOTE"
if grep -qiE 'UNREVIEWED|code-mode host is disabled|access (failed|denied)' "$OUT"; then
  echo "  !! REVIEWER COULD NOT READ THE REPO - NOT a certification"; exit 9
fi
RAN=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -c '^exec' || true)
echo "  shell commands the reviewer actually ran: $RAN"
[ "$RAN" -ge 3 ] || { echo "  !! reviewer ran almost nothing ($RAN cmds) - treat as unverified"; exit 9; }
echo "  -> $OUT ($(wc -c < "$OUT") bytes)"; tail -1 "$OUT"
