"""Seal the 17 October lead rulings and snapshot custody before offline packing."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.numerics.locks import load_locks
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/n1'
SCRATCH=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p): return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

def main():
    source=SCRATCH/'n1_cache/n1cc_approved_proposed.jsonl'
    approved=rows(source); bed=rows(OUT/'step1_rendered_v3.jsonl'); frame=rows(OUT/'frame_step1.jsonl')
    locks=load_locks(OUT)
    assert len(approved)==len({r['slot_id'] for r in approved})==82
    assert len(bed)==558
    step_lines={r['line_id'] for r in frame if r['partition']=='step1'}
    step_docs={r['document'] for r in frame if r['partition']=='step1'}
    raised=[r for r in approved if r['truth']=='raised dot']; assert len(raised)==4
    candidates=rows(OUT/'controls/raised_candidates_cc.jsonl')
    # 101 aliases the already approved hyphen cell 58; preserve only that original approval.
    for candidate in candidates:
        matches=[r for r in approved if r['slot_id']==candidate['slot_id']]
        if candidate['cell_number']==101:
            assert len(matches)==1 and matches[0]['approval_cell_number']==58 and matches[0]['truth']=='hyphen or dash'
        else: assert not matches
    prior={str(p):sha(p) for p in OUT.rglob('*') if p.is_file()}
    prior[str(ROOT/'docs/records/labelfix/secondary/prompts/sep.md')]=sha(ROOT/'docs/records/labelfix/secondary/prompts/sep.md')
    for r in approved:
        locks.assert_fit_rows([r['line_id']])
        assert r['line_id'] not in step_lines
        assert r['document'] not in locks.reserved_docs
        assert r['document'] not in step_docs or r['c1_control_only']
        r['approval_provenance']=dict(task='N1-Cd',lead_ruling_date='2026-10-17',source=str(source),source_sha256=sha(source),
            c1_document_ruling='The four C1 raised-dot controls are allowed: their lines are disjoint from every step1 line and the reserved set; they are C1 evidence lines that N1 never fits on. Document-level exclusion was intended to prevent controls resembling bed items, not to protect truth.',
            c1_evidence_control_only=bool(r['c1_control_only']),
            candidate_rulings={'101':'spaced hyphen; duplicate of cell 58; excluded from controls','102':'baseline dot under a dotted leader; excluded from controls'})
    for r in bed+approved:
        for name in ('line','zoom'):
            assert sha(Path(r[name]))==r[name+'_sha256']
    target=OUT/'controls/approved.jsonl'
    with target.open('x') as f: f.write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in approved))
    with (OUT/'usage_ledger.json').open('x') as f: f.write('[]\n')
    receipt=dict(task='N1-Cd',seed='20261017:N1-1',approved_count=82,approved_sha256=sha(target),
        approved_source_sha256=sha(source),prior_unchanged=prior,inputs={str(source):sha(source)},
        network=False,git_writes=False,reader_run=False,run_lock_access=False,
        c1_ruling='Approved by lead 2026-10-17; line-level disjointness checked against all step1 and reserved lines.',
        rejected_candidates={'101':'spaced hyphen (cell 58 duplicate)','102':'baseline dot under dotted leader'})
    (SCRATCH/'n1_cache/n1cd_preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(approved_sha256=sha(target),bed=len(bed),controls=len(approved))))
if __name__=='__main__': main()
