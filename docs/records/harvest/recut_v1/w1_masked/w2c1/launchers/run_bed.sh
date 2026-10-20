#!/usr/bin/env bash
set -euo pipefail
BED=$1; RDR=$2
D=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/w2c1; S=$D/launchers
[ -f "$D/READY.json" ] || { echo "W2C1 preparation not yet validated"; exit 8; }
RD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/$BED/$RDR
case "$BED" in w2c1_bsb_poly1850_poly1850|w2c1_ia_poly1850_poly1850|w2c1_nlg_poly1850|w2c1_nlg_poly1900|w2c1_nlg_greek_poly|w2c1_serbia_cyrillic|w2c1_elstat_numerics_tables|w2c1_gazette_modern_modern_scanned|w2c1_nlg_poly1900_r2|w2c1_nlg_greek_poly_r2|w2c1_gazette_modern_modern_scanned_r2) ;; *) exit 64;; esac
case "$RDR" in c1|c2) ;; *) exit 64;; esac
[ -f "$RD/cards.jsonl" ] || { echo "Unprepared context"; exit 64; }
[ ! -e "$RD/answers.jsonl" ] || { echo "Refuse rerun: answers exist"; exit 8; }
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python
SCAN=$D/tools/scan_rollout.py
EXPECTED=dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547
[ "$(shasum -a 256 "$SCAN" | awk '{print $1}')" = "$EXPECTED" ] || { echo 'canonical scanner hash mismatch'; exit 8; }
BEFORE=$("$S/limit_probe.sh" "before:$BED/$RDR" | tail -1); echo "$BEFORE"
python3 -B "$D/runtime.py" limit "$BEFORE"
P=$S/prompts_rendered/${BED}_${RDR}.md
python3 - "$D/prompts/bsb.md" "$P" <<'RENDER'
import sys
open(sys.argv[2],'w').write(open(sys.argv[1]).read().replace('{{READER2_CLAUSE}}',''))
RENDER
case "$BED" in *_r2) cat "$D/prompts/path_addendum.md" >> "$P";; esac
RUN=$("$S/run_read.sh" "SR-$BED-$RDR" "$RD" "$P" medium | tail -1); echo "$RUN"
python3 -B "$D/runtime.py" begin "$BED" "$RDR" "$RUN" "$BEFORE" "$EXPECTED"
ROLL=$(echo "$RUN" | python3 -c 'import json,sys; print(json.load(sys.stdin)["rollout"])')
cp "$P" "$D/answers/$BED/$RDR.prompt.md"
SC=0
"$PY" -B "$SCAN" "$ROLL" "$RD" > "$D/scan/$BED/$RDR.scan.json" || SC=$?
[ ! -f "$RD/answers.jsonl" ] || cp "$RD/answers.jsonl" "$D/answers/$BED/$RDR.jsonl"
MC=0
python3 -B "$D/runtime.py" map "$BED" "$RDR" || MC=$?
AFTER=$("$S/limit_probe.sh" "after:$BED/$RDR" | tail -1); echo "$AFTER"
python3 -B "$D/runtime.py" finish "$BED" "$RDR" "$RUN" "$BEFORE" "$AFTER" "$SC" "$MC" "$EXPECTED"
[ "$SC" -eq 0 ] && [ "$MC" -eq 0 ] || { echo 'VOID or incomplete'; exit 2; }
python3 -B "$D/runtime.py" limit "$AFTER"
echo "SR-$BED-$RDR DONE"
