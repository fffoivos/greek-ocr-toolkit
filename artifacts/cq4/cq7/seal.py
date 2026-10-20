"""Offline CQ7 additive freeze; retain the pre-CQ7 freeze byte-for-byte."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
CQ=HERE.parent
ROOT=CQ.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
old=load(HERE/'baseline/build_hashes.json')
changes=[]
for rel,h in old.items():
 p=CQ/rel
 if sha(p)==h:continue
 archive=HERE/'baseline/workflow.py' if rel=='tools/workflow.py' else CQ/'cq6_package/evidence/cq4_before_amendment1a'/rel
 assert archive.is_file() and sha(archive)==h,(rel,'old freeze not proven')
 if rel not in ('tools/workflow.py','R2A2_PREREGISTRATION.md'):
  before=load(archive);after=load(p)
  assert after.pop('cq6_amendment1a_binding')==load(CQ/'cq6_preregistration_binding.json')
  assert before==after,'unexplained receipt change'
 changes.append(dict(path=rel,old_sha256=h,current_sha256=sha(p),original_archive=str(archive),
    reason='CQ7 aggregate integration and explicit CQ6 amendment-1a hash binding' if rel=='tools/workflow.py' else 'CQ6 amendment 1a, already present before CQ7'))
 current=sha(p);old[rel]=current
# No historical source bytes are replaced. Update only the live additive freeze.
dump(CQ/'build_hashes.json',old)
dump(HERE/'custody_amendments.json',dict(previous_freeze_sha256=sha(HERE/'baseline/build_hashes.json'),changes=changes,
    current_freeze_sha256=sha(CQ/'build_hashes.json'),scanner_version='4.5.5',scanner_sha256=sha(CQ/'tools/scan_rollout.py')))
# Freeze every CQ7 build artifact except runtime outputs/verification result.
paths=[p for p in HERE.rglob('*') if p.is_file() and p.name not in ('freeze.json','ledger.json','validation.json','TEST.sh')
       and not any(part in ('scans','__pycache__') for part in p.relative_to(HERE).parts)]
for rel in ('tools/build.py','tools/workflow.py','tools/scan_rollout.py','tools/replay_literal.py','tools/closure.py','tools/common.py',
            'build_hashes.json','cq6_preregistration_binding.json','R2A2_PREREGISTRATION.md','launchers/run_read.sh','launchers/limit_probe.sh',
            'initial_ledger.json','rescan_ledger.json','reread_ledger.json','contexts.json','reread_contexts.json',
            'keys/topup_selected.jsonl','keys/wcap_selected.jsonl','keys/control_pool.json','control_review/lead_review.json','control_review/controls.png'):
 paths.append(CQ/rel)
for c in load(CQ/'contexts.json')+load(CQ/'reread_contexts.json'):
 paths.append(Path(c['key']))
dump(HERE/'freeze.json',{str(p):sha(p) for p in sorted(set(paths))})
