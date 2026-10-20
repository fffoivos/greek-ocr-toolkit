#!/usr/bin/env bash
# Lead-only: one context, probe -> read -> canonical scan -> mapping -> probe.
set -euo pipefail
BED=${1:?bed}; RDR=${2:?reader}
S=$(cd "$(dirname "$0")" && pwd)
D=$(cd "$S/.." && pwd)
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python
case "$BED/$RDR" in segcp7r2_a/r1|segcp7r2_b/r1) ;; *) exit 64;; esac
RD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/$BED/$RDR
EXPECTED=dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547
[ "$(shasum -a 256 "$D/../tools/scan_rollout.py" | awk '{print $1}')" = "$EXPECTED" ] || exit 8
[ ! -e "$RD/answers.jsonl" ] && [ ! -e "$S/logs/SEG-CP7-$BED-$RDR.codexlog" ] || { echo 'Refuse rerun: answers exist'; exit 8; }
"$PY" -B "$D/../runtime_r2.py" verify
mkdir -p "$S/logs" "$S/prompts_rendered" "$D/answers/$BED" "$D/scan/$BED"
BEFORE=$("$S/limit_probe.sh" "before:$BED/$RDR" | tail -1); echo "$BEFORE"
"$PY" -B "$D/../runtime_r2.py" limit "$BEFORE"
P=$S/prompts_rendered/${BED}_${RDR}.md
cat "$D/../prompts/bsb.md" "$D/../prompts/segcp7_crop_rubric_r2.md" "$D/../prompts/path_addendum_r2.md" > "$P"
RUN=$("$S/run_read.sh" "SEG-CP7-$BED-$RDR" "$RD" "$P" medium | tail -1); echo "$RUN"
ROLL=$(echo "$RUN" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["rollout"])')
cp "$P" "$D/answers/$BED/$RDR.prompt.md"
SC=0
"$PY" -B "$D/../tools/scan_rollout.py" "$ROLL" "$RD" > "$D/scan/$BED/$RDR.scan.json" || SC=$?
[ ! -f "$RD/answers.jsonl" ] || cp "$RD/answers.jsonl" "$D/answers/$BED/$RDR.jsonl"
MC=0
"$PY" -B "$D/../runtime_r2.py" map "$BED" || MC=$?
AFTER=$("$S/limit_probe.sh" "after:$BED/$RDR" | tail -1); echo "$AFTER"
"$PY" -B "$D/../runtime_r2.py" receipt "$BED" "$RUN" "$BEFORE" "$AFTER" "$SC" "$MC"
"$PY" -B "$D/../runtime_r2.py" limit "$AFTER"
