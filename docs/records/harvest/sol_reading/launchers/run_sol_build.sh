#!/usr/bin/env bash
# run_sol_build.sh <Tnn> <label> <brief.md> <net:on|off>  (Sol-reading track; copy of run_wt_medium_git.sh; brief from docs/harvest/sol_reading/briefs/)
# One Codex gpt-6.1-sol implementation run; retries on 429 (8 × 5 min); asserts the model from the rollout; prints <Tnn>_DONE on success.
set -u; T=$1; LABEL=$2; BRIEF=$3; NET=$4; ANEMI=${5:-}
R=~/Projects/greek-ocr-toolkit-sol-reading; L=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/logs
OUT="$L/${LABEL}_final.md"; LOG="$L/${LABEL}.codexlog"; MODEL=gpt-6.1-sol
[ "$NET" = on ] && NETV=true || NETV=false
if [ "$ANEMI" = anemi ]; then export ANEMI_USER="$(security find-generic-password -a "$USER" -s codex-anemi-username -w)"; export ANEMI_PASS="$(security find-generic-password -a "$USER" -s codex-anemi-password -w)"; fi
for i in 1 2 3 4 5 6 7 8; do
  BEFORE=$(date +%s); echo "[$(date '+%H:%M:%S')] $T START attempt $i model=$MODEL net=$NETV brief=$BRIEF"
  codex exec -m "$MODEL" -c "model_reasoning_effort=medium" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
    -c features.remote_plugin=false -c features.apps=false -c sandbox_workspace_write.network_access=$NETV -c 'sandbox_workspace_write.writable_roots=["/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git","/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs"]' -c 'web_search="live"' \
    --sandbox workspace-write --skip-git-repo-check -C "$R" -o "$OUT" - < "$R/docs/harvest/sol_reading/briefs/$BRIEF" > "$LOG" 2>&1
  RC=$?
  if grep -q "429 Too Many Requests" "$LOG"; then echo "[$(date '+%H:%M:%S')] $T 429; waiting 5 min"; sleep 300; continue; fi
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
  echo "[$(date '+%H:%M:%S')] $T END rc=$RC elapsed=$(( ($(date +%s)-BEFORE)/60 ))m requested=$MODEL asserted=${ACTUAL:-UNKNOWN}"
  [ "$ACTUAL" = "$MODEL" ] || { echo "  !! MODEL MISMATCH/UNASSERTED ($ACTUAL)"; echo "${T}_FAILED"; exit 9; }
  tail -2 "$OUT"; echo; echo "${T}_DONE"; exit 0
done
echo "${T}_GAVE_UP_429"; exit 1
