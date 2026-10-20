#!/usr/bin/env bash
# run_bed.sh <bed> <reader> : one blind Sol reading run with limit probes, rollout leak scan, mapping and ledger entry.
# Stops (exit 8) before the run if weekly used >= 78%. Exit 2 = leak (run void).
set -u; BED=$1; RDR=$2
S=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps1/launchers; W=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut; D=$W/docs/harvest/recut_v1/w1_masked/caps1
RD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/$BED/$RDR; P=$S/prompts_rendered/${BED}_${RDR}.md; LABEL=SR-$BED-$RDR
case $RDR in r1) CL="";; *) CL=" (The README mentions cards_reverse.jsonl for reader 2: your cards.jsonl is already in your assigned order; use it as given.)";;esac
python3 - "$D/prompts/$BED.md" "$P" "$CL" <<'PY'
import sys; t=open(sys.argv[1]).read().replace('{{READER2_CLAUSE}}',sys.argv[3]); open(sys.argv[2],'w').write(t)
PY
N=$(wc -l < "$RD/$( [ $BED = yer ] && echo items || echo cards ).jsonl" | tr -d ' ')
BEFORE=$("$S/limit_probe.sh" "before:$BED/$RDR" | tail -1); echo "$BEFORE"
USED=$(echo "$BEFORE" | grep -oE 'primary=[0-9.]+' | cut -d= -f2)
[ -n "$USED" ] || { echo "NO PROBE READING - stop"; exit 8; }
python3 -c "import sys; sys.exit(0 if float('$USED')<78 else 1)" || { echo "STOP: weekly used $USED% >= 78%"; exit 8; }
RUN=$("$S/run_read.sh" "$LABEL" "$RD" "$P" medium | tail -1); echo "$RUN"
ROLL=$(echo "$RUN" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['rollout'])")
mkdir -p "$D/answers/$BED"; cp "$P" "$D/answers/$BED/$RDR.prompt.md"
cd "$W"; /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$D/tools/scan_rollout.py" "$ROLL" "$RD" > "$D/scan/$BED/$RDR.scan.json"; SC=$?
echo "scan rc=$SC $(head -c 300 "$D/scan/$BED/$RDR.scan.json")"
[ -f "$RD/answers.jsonl" ] && cp "$RD/answers.jsonl" "$D/answers/$BED/$RDR.jsonl"
python3 -B "$D/tools/map_answers.py" "$BED" "$RDR" "$D/answers/$BED/$RDR.jsonl"; MC=$?; echo "map rc=$MC"
AFTER=$("$S/limit_probe.sh" "after:$BED/$RDR" | tail -1); echo "$AFTER"
python3 -B "$D/tools/ledger.py" add --run "$RUN" --before "$BEFORE" --after "$AFTER" --bed "$BED" --reader "$RDR" --items "$N"; echo "ledger rc=$?"
[ $SC -eq 0 ] || { echo "$LABEL VOID (leak scan rc=$SC)"; exit 2; }
echo "$LABEL DONE items=$N"
