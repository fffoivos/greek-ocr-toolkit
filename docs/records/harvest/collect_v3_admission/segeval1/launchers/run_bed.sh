#!/usr/bin/env bash
# Adapted from the sourcing lead's CP7 r2 driver. PREPARED ONLY.
set -euo pipefail
BED=${1:?bed}; RDR=${2:?reader}
S=$(cd "$(dirname "$0")" && pwd)
D=$(cd "$S/.." && pwd)
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python
case "$BED/$RDR" in segeval1_a/r1|segeval1_b/r1) ;; *) exit 64;; esac
RD=/private/tmp/segeval1-packs-20261019/$BED/$RDR
[ ! -e "$RD/answers.jsonl" ] && [ ! -e "$S/logs/SEGEVAL1-$BED-$RDR.codexlog" ] || { echo 'Refuse rerun: answers/log exist'; exit 8; }
# Hash/closure checks for both packs are performed by launch.sh before any reads.
mkdir -p "$S/logs" "$S/prompts_rendered" "$D/answers/$BED" "$D/scan/$BED"
BEFORE=$("$S/limit_probe.sh" "before:$BED/$RDR" | tail -1)
"$PY" -B "$D/tools/runtime.py" limit "$BEFORE"
P=$S/prompts_rendered/${BED}_${RDR}.md
cat "$D/prompts/bsb.md" "$D/prompts/owner_rubric.md" "$D/prompts/path_addendum.md" > "$P"
RUN=$("$S/run_read.sh" "SEGEVAL1-$BED-$RDR" "$RD" "$P" medium | tail -1)
echo "$RUN"
ROLL=$(echo "$RUN" | "$PY" -c 'import json,sys; r=json.load(sys.stdin); assert r["model"]=="gpt-6.1-sol" and r["rc"]==0; print(r["rollout"])')
cp "$P" "$D/answers/$BED/$RDR.prompt.md"
"$PY" -B "$D/tools/scan_rollout.py" "$ROLL" "$RD" > "$D/scan/$BED/$RDR.scan.json"
cp "$RD/answers.jsonl" "$D/answers/$BED/$RDR.jsonl"
"$PY" - "$D" "$BED" "$ROLL" <<'PY_CUSTODY'
import json,hashlib,sys
from pathlib import Path
D=Path(sys.argv[1]);bed=sys.argv[2];roll=Path(sys.argv[3])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=D/'answers'/bed/'r1.jsonl';s=D/'scan'/bed/'r1.scan.json'
r=dict(answers_sha256=sha(a),scan_sha256=sha(s),rollout=str(roll),rollout_sha256=sha(roll),scanner_sha256=sha(D/'tools/scan_rollout.py'))
(s.parent/'r1.custody.json').write_text(json.dumps(r,indent=2)+'\n')
PY_CUSTODY
AFTER=$("$S/limit_probe.sh" "after:$BED/$RDR" | tail -1)
"$PY" -B "$D/tools/runtime.py" limit "$AFTER"
echo "$BEFORE" > "$D/answers/$BED/limits.txt"
echo "$AFTER" >> "$D/answers/$BED/limits.txt"
