#!/usr/bin/env bash
# run_read.sh <label> <reader_dir> <prompt_file> [effort] [-- image ...]
# One blind Sol reading run: cwd = the isolated reader dir, workspace-write limited to it, no network, no web search.
# Asserts the model from the rollout and prints token usage + wall time; prints <label>_DONE / _FAILED.
set -u; LABEL=$1; RD=$2; PROMPT=$3; EFFORT=${4:-medium}; shift 4 2>/dev/null || shift $#
IMGS=(); [ "${1:-}" = "--" ] && { shift; for f in "$@"; do IMGS+=(-i "$f"); done; }
S=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/ruc1/launchers; LOG="$S/logs/$LABEL.codexlog"; OUT="$S/logs/${LABEL}_final.md"; MODEL=gpt-6.1-sol
B=$(date +%s); echo "[$(date '+%H:%M:%S')] $LABEL START effort=$EFFORT dir=$RD images=${#IMGS[@]}"
codex exec -m "$MODEL" -c "model_reasoning_effort=$EFFORT" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
  -c features.remote_plugin=false -c features.apps=false -c sandbox_workspace_write.network_access=false -c 'web_search="disabled"' \
  --sandbox workspace-write --skip-git-repo-check -C "$RD" -o "$OUT" "${IMGS[@]}" - < "$PROMPT" > "$LOG" 2>&1
RC=$?; E=$(( $(date +%s)-B ))
SID=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -m1 -oE 'session id: [0-9a-f-]+' | awk '{print $3}')
ROLL=""; [ -n "$SID" ] && ROLL=$(ls "$HOME"/.codex/sessions/*/*/*/rollout-*"$SID".jsonl 2>/dev/null | head -1)
python3 - "$ROLL" "$LABEL" "$E" "$RC" <<'PY'
import json,sys
roll,label,el,rc=sys.argv[1:]
model=None; tot=None; rl=None; tools={}
def find_model(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='model' and isinstance(v,str): return v
            r=find_model(v)
            if r: return r
    return None
for l in open(roll) if roll else []:
    o=json.loads(l); p=o.get('payload') or {}
    if model is None and o.get('type') in ('session_meta','turn_context'): model=find_model(p)
    if isinstance(p,dict):
        if p.get('type')=='token_count':
            i=p.get('info') or {}; tot=i.get('total_token_usage') or tot
            if p.get('rate_limits'): rl=p['rate_limits']
        if p.get('type') in ('function_call','custom_tool_call','local_shell_call'):
            n=p.get('name') or p.get('type'); tools[n]=tools.get(n,0)+1
print(json.dumps({"label":label,"rc":int(rc),"wall_s":int(el),"model":model,"rollout":roll,"usage":tot,"tool_calls":tools,"rate_limits_in_rollout":rl}))
PY
