#!/usr/bin/env bash
# Resumable cross-session review thread. Same guarantees as run_review_ocrprog.sh (read-only repo, model asserted
# from the rollout), plus: the Codex session id is saved so a later prompt can continue the SAME context.
# Usage: run_review_thread.sh <label> <brief.md> <model> <effort> [resume_sid]
#   new thread : run_review_thread.sh ASTRA-E3mix docs/.../ASTRA_E3_mix_review_brief.md gpt-6-astra xhigh
#   continue   : run_review_thread.sh ASTRA-E3dir docs/.../ASTRA_E3_directions_brief.md gpt-6-astra xhigh "$(cat reviews/ASTRA-E3mix.sid)"
# Web search is live and sandbox network is on (literature search). DO NOT add features.code_mode_host=false.
set -u
LABEL="$1"; BRIEF="$2"; MODEL="${3:-gpt-6-astra}"; EFFORT="${4:-xhigh}"; RESUME="${5:-}"
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
RDIR="$REPO/docs/reviews/astra_program_review_2026-10-06"; mkdir -p "$RDIR"
OUT="$RDIR/${LABEL}_review_1.md"; LOG="$RDIR/${LABEL}_review_1.codexlog"; SIDF="$RDIR/${LABEL}.sid"
BEFORE=$(date +%s)
echo "[$(date '+%H:%M:%S')] THREAD START $LABEL model=$MODEL effort=$EFFORT resume=${RESUME:-new}"
SCRATCH="$HOME/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/$LABEL"
mkdir -p "$SCRATCH"; MARK="$SCRATCH/.start_marker"; touch "$MARK"; sleep 1
DIFF_BEFORE=$(git -C "$REPO" diff | shasum | cut -c1-12)
{ echo "Repository root (READ-ONLY, use absolute paths or \`cd $REPO\` in each command; writes there are blocked): $REPO"
  echo "Writable scratch for temporary outputs: $SCRATCH (your cwd) and /tmp. Run pytest from the repo root with"
  echo "PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider so it never writes into the repository."
  echo; cat "$BRIEF"; } > "$SCRATCH/prompt.md"
CFG=(-m "$MODEL" -c "model_reasoning_effort=$EFFORT" -c project_doc_max_bytes=0 -c approval_policy=never
     -c features.remote_plugin=false -c features.apps=false -c features.multi_agent=false
     -c sandbox_workspace_write.network_access=true -c 'web_search="live"')
if [ -n "$RESUME" ]; then
  # `exec resume` has no --sandbox/-C flags: sandbox via config, cwd via cd (the resumed thread keeps its roots).
  (cd "$SCRATCH" && codex exec resume "${CFG[@]}" -c 'sandbox_mode="workspace-write"' --skip-git-repo-check -o "$OUT" "$RESUME" - < "$SCRATCH/prompt.md") > "$LOG" 2>&1
else
  codex exec "${CFG[@]}" --sandbox workspace-write --skip-git-repo-check -C "$SCRATCH" -o "$OUT" - < "$SCRATCH/prompt.md" > "$LOG" 2>&1
fi
RC=$?
TOUCHED=$(find "$REPO" -type f -newer "$MARK" -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' -not -path "$REPO/docs/reviews/astra_program_review_2026-10-06/*" -not -path "$REPO/bench/runs/*" 2>/dev/null | { if [ -n "${REVIEW_IGNORE_REGEX:-}" ]; then grep -Ev "$REVIEW_IGNORE_REGEX" || true; else cat; fi; })
DIFF_AFTER=$(git -C "$REPO" diff | shasum | cut -c1-12)
SID=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -m1 -oE 'session id: [0-9a-f-]+' | awk '{print $3}')
[ -z "$SID" ] && [ -n "$RESUME" ] && SID="$RESUME"
[ -n "$SID" ] && echo "$SID" > "$SIDF"
ROLL=""; [ -n "$SID" ] && ROLL=$(ls "$HOME"/.codex/sessions/*/*/*/rollout-*"$SID".jsonl 2>/dev/null | head -1)
ACTUAL=""; [ -n "$ROLL" ] && ACTUAL=$(python3 -c "
import json,sys
for l in open(sys.argv[1]):
    try: o=json.loads(l)
    except Exception: continue
    p=o.get('payload') or {}
    if isinstance(p,dict) and isinstance(p.get('model'),str): print(p['model']); break
" "$ROLL")
echo "[$(date '+%H:%M:%S')] THREAD END $LABEL rc=$RC elapsed=$(( ($(date +%s)-BEFORE)/60 ))m"
echo "  requested=$MODEL  asserted=${ACTUAL:-UNKNOWN}  session=${SID:-none}  rollout=${ROLL##*/}"
[ -n "$ACTUAL" ] || { echo "  !! MODEL NOT ASSERTED - treat as NOT certified"; echo "${LABEL}_FAILED"; exit 9; }
[ "$ACTUAL" = "$MODEL" ] || { echo "  !! MODEL MISMATCH requested $MODEL, ran $ACTUAL"; echo "${LABEL}_FAILED"; exit 9; }
case "${ACTUAL:-}" in *claude*|*opus*|*fable*) echo "  !! SAME-FAMILY AS COORDINATOR"; echo "${LABEL}_FAILED"; exit 9;; esac
[ -s "$OUT" ] || { echo "  !! no review produced"; echo "${LABEL}_FAILED"; exit 9; }
if [ -n "$TOUCHED" ] || { [ -z "${REVIEW_IGNORE_REGEX:-}" ] && [ "$DIFF_BEFORE" != "$DIFF_AFTER" ]; }; then
  echo "  !! REPO MODIFIED DURING REVIEW (diff $DIFF_BEFORE -> $DIFF_AFTER):"; echo "$TOUCHED" | head -20; echo "  treat as NOT certified"; echo "${LABEL}_FAILED"; exit 9
fi
RAN=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -c '^exec' || true)
echo "  shell commands the reviewer actually ran: $RAN"
echo "  -> $OUT ($(wc -c < "$OUT") bytes)"; tail -1 "$OUT"; echo "${LABEL}_DONE"
