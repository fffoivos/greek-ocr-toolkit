"""Prepare unwrapped canonical audit, closure adapter and sequential launchers."""
from build import *
def executable(p,text):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);p.chmod(0o755)
def prepare():
 guard();tools=HERE/'tools';tools.mkdir(exist_ok=True)
 assert sha(REFERENCE/'tools/scan_rollout.py')==CANONICAL
 bindings={}
 for name in ('scan_rollout.py','replay_literal.py','common.py','map_answers.py','owner39_validate.py','owner39_common.py','ledger.py','scan_packs.py'):
  src=REFERENCE/'tools'/name;shutil.copyfile(src,tools/name);bindings[str(src)]=sha(src)
 assert sha(tools/'scan_rollout.py')==CANONICAL
 # The rollout scanner and replay helper above remain byte-for-byte canonical.
 # Only the closure checker follows the approved CAPS1 L-mode/disjoint-batch adapter.
 p=tools/'scan_packs.py';s=p.read_text();assert s.count("im.mode!='RGB'")==1 and s.count("if directory.name!='r3':")==1
 s=s.replace("im.mode!='RGB'","im.mode not in ('RGB','L')").replace("if directory.name!='r3':","if not bed.startswith('w2c1_') and directory.name!='r3':")
 p.write_text(s)
 common=tools/'common.py';s=common.read_text();s+='\n# W2C1 path/schema configuration; rollout scanner is unchanged.\nROOT = Path('+repr(str(HERE))+')\nPACK_ROOT = Path('+repr(str(PACK_ROOT))+')\nFIELDS.update({b: FIELDS["bsb"] for b in '+repr([bedname(*s) for s in STRATA])+'})\n';common.write_text(s)
 for name in ('run_read.sh','limit_probe.sh'):
  src=REFERENCE/'launchers'/name;s=src.read_text();s=s.replace('S=$(cd "$(dirname "$0")" && pwd)','S='+str(HERE/'launchers'));executable(HERE/'launchers'/name,s);bindings[str(src)]=sha(src)
 for d in ('logs','prompts_rendered'):(HERE/'launchers'/d).mkdir(parents=True,exist_ok=True)
 (HERE/'prompts').mkdir(exist_ok=True);shutil.copyfile(REFERENCE/'prompts/bsb.md',HERE/'prompts/bsb.md')
 # No protocol additions: the sole templated READER2 clause is empty for one-reader batches.
 for source,cls in STRATA:
  bed=bedname(source,cls)
  for d in ('answers','scan','receipts'):(HERE/d/bed).mkdir(parents=True,exist_ok=True)
 launcher='''#!/usr/bin/env bash
set -euo pipefail
BED=$1; RDR=$2
D=__HERE__; S=$D/launchers
[ -f "$D/READY.json" ] || { echo "W2C1 preparation not yet validated"; exit 8; }
RD=__PACK__/$BED/$RDR
case "$BED" in __BEDS__) ;; *) exit 64;; esac
case "$RDR" in c1|c2) ;; *) exit 64;; esac
[ ! -e "$RD/answers.jsonl" ] || { echo "Refuse rerun: answers exist"; exit 8; }
PY=__PY__
SCAN=$D/tools/scan_rollout.py
EXPECTED=__SHA__
[ "$(shasum -a 256 "$SCAN" | awk '{print $1}')" = "$EXPECTED" ] || { echo 'canonical scanner hash mismatch'; exit 8; }
BEFORE=$("$S/limit_probe.sh" "before:$BED/$RDR" | tail -1); echo "$BEFORE"
python3 -B "$D/runtime.py" limit "$BEFORE"
P=$S/prompts_rendered/${BED}_${RDR}.md
python3 - "$D/prompts/bsb.md" "$P" <<'RENDER'
import sys
open(sys.argv[2],'w').write(open(sys.argv[1]).read().replace('{{READER2_CLAUSE}}',''))
RENDER
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
'''
 for a,b in {'__HERE__':str(HERE),'__PACK__':str(PACK_ROOT),'__PY__':str(COLLECTOR/'.venv/bin/python'),'__SHA__':CANONICAL,'__BEDS__':'|'.join(bedname(*s) for s in STRATA)}.items():launcher=launcher.replace(a,b)
 executable(HERE/'launchers/run_bed.sh',launcher)
 public=PACK_ROOT/'launchers/run_bed.sh';current=public.read_text();prefix='if [[ "${1:-}" == w2c1_* ]]; then exec bash '+str(HERE/'launchers/run_bed.sh')+' "$@"; fi\n'
 if prefix not in current:
  dump(HERE/'public_launcher_before.json',dict(path=str(public),sha256=sha(public),text=current));first,rest=current.split('\n',1);executable(public,first+'\n'+prefix+rest)
 lines=[]
 for source,cls in STRATA:
  for ctx in ('c1','c2'):lines.append('bash '+str(public)+' '+bedname(source,cls)+' '+ctx)
 (HERE/'launch_lines.txt').write_text('\n'.join(lines)+'\n')
 launch='''#!/usr/bin/env bash
set -euo pipefail
D=__HERE__
exec >> "$D/run.log" 2>&1
run_one() {
  local before
  before=$("$D/launchers/limit_probe.sh" "launch_all:$1/$2" | tail -1)
  echo "$before"
  python3 -B "$D/runtime.py" limit "$before" || return 8
  bash __PUBLIC__ "$1" "$2"
}
'''.replace('__HERE__',str(HERE)).replace('__PUBLIC__',str(public))
 launch+='\n'.join('run_one '+bedname(source,cls)+' '+ctx for source,cls in STRATA for ctx in ('c1','c2'))+'\n'
 executable(HERE/'launch_all.sh',launch)
 dump(HERE/'runtime_bindings.json',dict(reference_sources=bindings,canonical_scanner_sha256=sha(tools/'scan_rollout.py'),scanner_wrappers=False,public_launcher_sha256=sha(public),readers_started=0))
if __name__=='__main__':prepare()
