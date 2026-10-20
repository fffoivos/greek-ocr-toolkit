#!/usr/bin/env bash
# BUILD ONLY handoff: the lead executes this after pixel-reviewing six controls.
set -euo pipefail
W=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2cards
S="$W/artifacts/cq1"
PACK_ROOT=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/solcap_qual
RD="$PACK_ROOT/cap1/r1"
PY=(/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B)
cd "$W"
[ "$(codex --version)" = "codex-cli 0.159.2" ] || { echo "STOP: HANDOVER requires Codex CLI 0.159.2"; exit 8; }
"${PY[@]}" "$S/tools/preflight.py"
# Check closure against frozen build manifest without rewriting it.
"${PY[@]}" - "$RD" "$S" <<'PY'
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[2])/'tools'))
from scan_packs import scan
from common import sha
rd=Path(sys.argv[1]);p=rd.parent/'MANIFEST.r1.json';before=sha(p)
r=scan(rd,'cap1',write_manifest=False)
assert r['ok'],r['violations']
assert sha(p)==before
frozen=json.loads(p.read_text())['files'];assert r['files']==frozen
PY
BEFORE=$(bash "$S/launchers/limit_probe.sh" 'before:CQ1/cap1/r1' | tail -1)
echo "$BEFORE"
printf '%s\n' "$BEFORE" > "$S/answers/before.txt"
USED=$(printf '%s\n' "$BEFORE" | sed -nE 's/.*weekly_used=([0-9.]+).*/\1/p')
[ -n "$USED" ] || { echo 'STOP: no codex 10080-minute bucket'; exit 8; }
python3 -c 'import sys;sys.exit(0 if float(sys.argv[1])<78 else 8)' "$USED" || { echo 'STOP: weekly budget >=78%'; exit 8; }
# Ensure a failed reading still receives the required after probe.
trap 'bash "$S/launchers/limit_probe.sh" "after:CQ1/cap1/r1:failed" | tee "$S/answers/after_failure.txt"' EXIT
# The owner dashboard overrides this probe; stop at weekly use >=80%, never spend credits.
bash "$S/launchers/run_read.sh" CQ1-cap1-r1 "$RD" "$S/prompts/cap1.md" medium | tee "$S/answers/run.log"
RUN=$(tail -1 "$S/answers/run.log")
ROLL=$(printf '%s\n' "$RUN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["rollout"])')
set +e
"${PY[@]}" "$S/tools/scan_rollout_v42.py" "$ROLL" "$RD" --output "$S/answers/r1.scan.json"
SC=$?
set -e
cp "$RD/answers.jsonl" "$S/answers/r1.jsonl"
AFTER=$(bash "$S/launchers/limit_probe.sh" 'after:CQ1/cap1/r1' | tail -1)
echo "$AFTER"
trap - EXIT
printf '%s\n' "$AFTER" > "$S/answers/after.txt"
python3 - "$S" "$RUN" "$BEFORE" "$AFTER" <<'PY'
import sys,json
from pathlib import Path
s,run,before,after=sys.argv[1:]
p=Path(s)/'usage_ledger.json';entries=json.loads(p.read_text()) if p.exists() else []
entries.append(dict(run=json.loads(run),before=before,after=after,bed='cap1',reader='r1',items=66))
p.write_text(json.dumps(entries,indent=2)+'\n')
PY
[ "$SC" -eq 0 ] || { echo 'CQ1 VOID: leak scan failed'; exit 2; }
"${PY[@]}" "$S/tools/score_cq1.py" "$S/answers/r1.jsonl" "$S/answers/r1.scan.json" --before "$BEFORE" --after "$AFTER"
