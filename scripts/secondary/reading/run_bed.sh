#!/usr/bin/env bash
# RU1: run_bed.sh ctxNN. PREPARED ONLY: not invoked by RU1-0.
set -euo pipefail
CTX=${1:?usage: run_bed.sh ctxNN [r1|r2|r3]}
READER=${2:-r1}
[[ $READER == r1 || $READER == r2 || $READER == r3 ]] || exit 64
STEM=$CTX
[[ $READER == r1 ]] || STEM=$CTX.$READER
[[ $CTX =~ ^ctx[0-9][0-9]$ ]] || exit 64
[[ $READER != r3 || $CTX == ctx04 ]] || exit 64
[[ $CTX != ctx04 || $READER != r2 ]] || { echo "ctx04/r2 is VOID; use r3" >&2; exit 64; }
S=$(cd "$(dirname "$0")" && pwd)
W=$(cd "$S/../../.." && pwd)
D="$W/artifacts/ru1"
PACK_ROOT=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru1
RD="$PACK_ROOT/$CTX/$READER"
P="$W/docs/records/labelfix/secondary/prompts/yer.md"
if [[ ${RU1_DRY_RUN:-0} == 1 ]]; then
  printf '%s\n' "reader=$READER" "pack=$RD" "answers=$D/answers/$STEM.jsonl" "scan=$D/answers/$STEM.scan.json" "mapped=$D/answers/$STEM.mapped.jsonl" "controls=$D/answers/$STEM.controls.json" "key=$D/keys/$STEM.json"
  exit 0
fi
mkdir -p "$D/answers" "$D/logs"
N=$(wc -l < "$RD/items.jsonl" | tr -d ' ')
BEFORE=$("$S/limit_probe.sh" "before:RU1/$STEM" | tail -1)
echo "$BEFORE"
python3 -B - "$S" "$BEFORE" <<'PY'
import sys
sys.path.insert(0,sys.argv[1])
from ledger import weekly
if weekly(sys.argv[2])>=78:raise SystemExit('STOP: weekly usage >= 78%')
PY
RUN=$("$S/run_read.sh" "RU1-$STEM" "$RD" "$P" medium | tail -1)
echo "$RUN"
ROLL=$(echo "$RUN" | python3 -c 'import json,sys;print(json.load(sys.stdin)["rollout"])')
RC=$(echo "$RUN" | python3 -c 'import json,sys;print(json.load(sys.stdin)["rc"])')
cp "$P" "$D/answers/$STEM.prompt.md"
set +e
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$S/scan_rollout.py" "$ROLL" "$RD" > "$D/answers/$STEM.scan.json"
SC=$?
MC=2
if [ "$SC" -eq 0 ] && [ "$RC" -eq 0 ] && [ -f "$RD/answers.jsonl" ]; then
  cp "$RD/answers.jsonl" "$D/answers/$STEM.jsonl"
  python3 -B "$S/ru1_map_answers.py" "$CTX" "$D/answers/$STEM.jsonl" --reader "$READER"
  MC=$?
fi
AFTER=$("$S/limit_probe.sh" "after:RU1/$STEM" | tail -1)
echo "$AFTER"
python3 -B "$S/ledger.py" add --run "$RUN" --before "$BEFORE" --after "$AFTER" --bed "$CTX" --reader "$READER" --items "$N"
LC=$?
[ "$SC" -eq 0 ] && [ "$RC" -eq 0 ] && [ "$MC" -eq 0 ] && [ "$LC" -eq 0 ] || { echo "RU1-$STEM VOID or failed; inspect scans and controls"; exit 2; }
echo "RU1-$STEM DONE items=$N"
