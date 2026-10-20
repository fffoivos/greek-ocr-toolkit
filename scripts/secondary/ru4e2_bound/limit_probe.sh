#!/usr/bin/env bash
# limit_probe.sh <tag>: one-word non-ephemeral gpt-6.1-sol call; prints the rate-limit buckets from its rollout; appends to limit_probe.log
S=$(cd "$(dirname "$0")" && pwd); TAG=${1:-probe}; W=$(cd "$S/../../.." && pwd); A="/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary/artifacts/ru1/ru4e2/answers"; mkdir -p "$A"; D=$(mktemp -d "$A/probe.XXXX")
for i in 1 2 3; do
  LOG="$D/p$i.log"
  codex exec -m gpt-6.1-sol -c model_reasoning_effort=low -c project_doc_max_bytes=0 -c features.remote_plugin=false -c features.apps=false \
    -c features.multi_agent=false -c sandbox_workspace_write.network_access=false -c 'web_search="disabled"' --sandbox read-only --skip-git-repo-check -C "$D" "Reply with the single word ok." < /dev/null > "$LOG" 2>&1
  SID=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -m1 -oE 'session id: [0-9a-f-]+' | awk '{print $3}')
  ROLL=$(ls "$HOME"/.codex/sessions/*/*/*/rollout-*"$SID".jsonl 2>/dev/null | head -1)
  OUT=$(python3 - "$ROLL" <<'PY'
import json,sys,datetime
rl=None
for l in open(sys.argv[1]):
    o=json.loads(l); p=o.get('payload') or {}
    if isinstance(p,dict) and p.get('type')=='token_count' and p.get('rate_limits'): rl=p['rate_limits']
if not rl: print('NONE'); sys.exit()
def w(x):
    if not x: return '-'
    r=x.get('resets_at'); r=datetime.datetime.fromtimestamp(r).strftime('%a %H:%M') if r else '?'
    return f"{x.get('used_percent')}%/{x.get('window_minutes')}m reset {r}"
print(f"limit_id={rl.get('limit_id')} primary={w(rl.get('primary'))} secondary={w(rl.get('secondary'))}")
PY
)
  echo "$OUT" | grep -q 'limit_id=codex ' && break
done
echo "$(date '+%Y-%m-%d %H:%M:%S') $TAG $OUT" | tee -a "$A/limit_probe.log"
