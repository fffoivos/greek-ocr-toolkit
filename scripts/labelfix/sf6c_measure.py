"""SF6c offline certification replay; frozen SF6b versus current policy."""
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
import json
import shutil

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden import l1_common
from scripts.labelfix.clariden.r1_common import rows, write_json, write_rows, sha256
from scripts.labelfix import sf6_measure as sf6
from scripts.labelfix.sf5_measure import baseline

EV=sf6.DOC/'SF6c_evidence'
FROZEN=Path('artifacts/labelfix_sf6c/before')
PRIOR=sf6.DOC/'SF6b_evidence/after'


def measure(target=None):
    original=(sf6.EV,sf6.gate,sf6.common,sf6.BINDING)
    try:
        for phase,policy,consumer in [('before',*baseline(FROZEN)),('after',gate,l1_common)]:
            if target and target!=phase:continue
            if phase=='before':
                policy.R=SimpleNamespace(**vars(policy.R))
                policy.R.__file__=str((FROZEN/'greekocr/labelfix/reading.py').resolve())
            dest=EV/phase;dest.mkdir(exist_ok=True)
            for name in ('witness_inputs.jsonl.gz','witness_inputs_receipt.json','census_inputs.jsonl.gz'):
                if (PRIOR/name).exists():shutil.copyfile(PRIOR/name,dest/name)
            sf6.EV=dest;sf6.gate=policy;sf6.common=consumer
            sf6.BINDING=dict(original[3],policy_sha256=policy.policy_binding()['sha256'],policy_binding=policy.policy_binding())
            sf6.heldout();print(phase,'heldout complete',flush=True)
            sf6.m2();print(phase,'M2 DEV complete',flush=True)
            sf6.witnesses();print(phase,'witnesses complete',flush=True)
    finally:
        sf6.EV,sf6.gate,sf6.common,sf6.BINDING=original
    changed=[];checks=[];summary={}
    for cohort,path in [('heldout','heldout/release_labels.jsonl.gz'),('m2_dev','m2_dev/release_labels.jsonl.gz'),
                        ('witness','witness_results.jsonl.gz')]:
        a=list(rows(EV/'before'/path));b=list(rows(EV/'after'/path))
        assert a==list(rows(PRIOR/path)),('SF6b baseline mismatch',cohort)
        assert len(a)==len(b)
        for old,new in zip(a,b):
            assert (old['id'],old['mode'],old.get('cohort'))==(new['id'],new['mode'],new.get('cohort'))
            assert old['before']==new['before']
            if old['checks']!=new['checks']:
                checks.append(dict(cohort=cohort,id=old['id'],mode=old['mode'],before=old['checks'],after=new['checks']))
            effective_old={k:v for k,v in old['after'].items() if k!='deletion_checks'}
            effective_new={k:v for k,v in new['after'].items() if k!='deletion_checks'}
            if effective_old!=effective_new:
                assert old['after']['status']!='hold' and new['after']['status']=='hold'
                changed.append(dict(cohort=cohort,id=old['id'],mode=old['mode'],before=effective_old,after=effective_new))
        summary[cohort]={phase:{mode:dict(Counter(r['after']['status'] for r in rr if r['mode']==mode))
                               for mode in gate.MODES} for phase,rr in [('before',a),('after',b)]}
        if cohort!='witness':
            assert json.loads((EV/'before'/cohort/'metrics.json').read_text())==json.loads((PRIOR/cohort/'metrics.json').read_text())
    write_rows(EV/'line_changes.jsonl',changed);write_rows(EV/'check_changes.jsonl',checks)
    write_json(EV/'comparison.json',dict(policy_before=json.loads((EV/'before_receipt.json').read_text())['policy'],
        policy_after=gate.policy_binding(),sf6b_baseline_exact=True,newly_hold=changed,changed_checks=len(checks),
        release_counts=summary,network=False,detector_runs=0,r1_runs=0,ctc_runs=0,locked_ii_records_decoded=0))
    unsafe_path=Path('docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json')
    unsafe=[]
    binding=dict(sf6.BINDING,policy_sha256=gate.policy_binding()['sha256'])
    for w in json.loads(unsafe_path.read_text()):
        out=l1_common.overlay(dict(id='x',label=w['original'],script_class='greek_poly'),w['runtime'],w['mode'],binding)
        assert out['status']=='hold' and not out['changes'] and 'label' not in out
        unsafe.append(dict(case=w['case'],mode=w['mode'],overlay=out))
    write_json(EV/'unsafe_witnesses_after.json',dict(input_sha256=sha256(unsafe_path),cases=unsafe))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=('before','after'))
    measure(parser.parse_args().phase)
