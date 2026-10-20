"""N1-Cc approval, deterministic draw, exclusion and retained-artifact checks."""
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from greekocr.numerics.locks import load_locks

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/n1'
SCRATCH=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_cache')

def rows(name):
    path=OUT/name
    if name=='controls/approved.jsonl' and not path.exists():
        path=SCRATCH/'n1cc_approved_proposed.jsonl'
    return [json.loads(s) for s in path.read_text().splitlines()]

def data():
    path=OUT/'N1Cc_GENERATION.json'
    if not path.exists():path=SCRATCH/'n1cc_generation_pending.json'
    return json.loads(path.read_text())

def test_exact_approved_cell_mapping():
    approved=rows('controls/approved.jsonl')
    expected={'baseline dot':set(range(1,13))|{14,15}|set(range(18,25)),
        'comma':set(range(25,48)),
        'hyphen or dash':{49,50,51,53,54}|set(range(56,71))|{73,75,76,77,78,80,81},
        'nothing':{84,87,89,90,91,92,94},'raised dot':{1,2,3,4}}
    assert len(approved)==len({r['slot_id'] for r in approved})==82
    assert {t:{r['approval_cell_number'] for r in approved if r['truth']==t} for t in expected}==expected
    original={r['slot_id']:r for n in ['controls/candidates_v2.jsonl','controls/c1_references_v2.jsonl'] for r in rows(n)}
    for r in approved:
        assert original[r['slot_id']]['cell_number']==r['approval_cell_number']
        assert r['c1_control_only']==(r['truth']=='raised dot')
        assert not r['reference_only']

def test_exclusions_and_c1_control_only():
    locks=load_locks(OUT)
    devdocs={r['document'] for r in rows('frame_step1.jsonl') if r['partition']=='step1'}
    c1=set(json.loads((OUT/'locked_eval_docs.json').read_text())['excluded_c1_line_ids'])
    for r in rows('controls/approved.jsonl'):
        locks.assert_fit_rows([r['line_id']])
        assert r['document'] not in locks.reserved_docs
        if r['document'] in devdocs:
            assert r['c1_control_only']
            assert dict(slot_id=r['slot_id'],document=r['document']) in data()['c1_document_conflicts']
        assert (r['line_id'] in c1)==r['c1_control_only']
    for p in rows('controls/raised_pool_cc.jsonl'):
        r=p['slot'];locks.assert_fit_rows([r['line_id']])
        assert r['document'] not in devdocs|locks.reserved_docs
        assert r['line_id'] not in c1
        assert p['geometry']['geom_status']=='ok'
        assert r['selection_sources']
    assert len(data()['c1_document_conflicts'])==4

def test_deterministic_document_capped_draw():
    pool=rows('controls/raised_pool_cc.jsonl')
    random.Random('20261017:N1Cc:raised').shuffle(pool)
    selected=[];counts=Counter()
    for p in pool:
        s=p['slot']
        if counts[s['document']]>=3:continue
        selected.append(s['slot_id']);counts[s['document']]+=1
        if len(selected)==36:break
    actual=rows('controls/raised_candidates_cc.jsonl')
    assert [r['slot_id'] for r in actual]==selected
    assert len(actual)<=36 and max(counts.values(),default=0)<=3
    assert [r['cell_number'] for r in actual]==list(range(101,101+len(actual)))
    assert data()['summary']['raised_pool']==len(pool)

def test_measurements_and_old_zooms_retained():
    old={r['slot_id']:r for n in ['step1_rendered_v2.jsonl','controls/candidates_v2.jsonl','controls/c1_references_v2.jsonl'] for r in rows(n)}
    new=rows('step1_rendered_v3.jsonl')+rows('controls/approved.jsonl')
    assert len(new)==640
    assert {r['slot_id'] for r in rows('step1_rendered_v3.jsonl')}=={r['slot_id'] for r in rows('step1_rendered_v2.jsonl')}
    for r in new:
        previous=old[r['slot_id']]
        assert r['measurements']==previous['measurements']
        assert r['geometry']==previous['geometry']
        assert r['line_sha256']==previous['line_sha256']
        assert r['zoom_sha256']!=previous['zoom_sha256']
        assert hashlib.sha256(Path(previous['zoom']).read_bytes()).hexdigest()==previous['zoom_sha256']
    assert len(rows('zoom_measurement_checks_cc.jsonl'))==640

def test_new_sheets_and_zoom_check_priority():
    d=data();index=json.loads((Path(d['summary']['zoom_check']).parent/'sheets_index_cc.json').read_text())
    assert all(n<=12 for n in Counter(r['sheet'] for r in index['raised']).values())
    assert {r['slot_id'] for r in index['raised']}=={r['slot_id'] for r in rows('controls/raised_candidates_cc.jsonl')}
    sample=index['zoom_check'];assert len(sample)==12
    assert [r['cell_number'] for r in sample[:7]]==[84,87,89,90,91,92,94]
    assert {r['slot_id'] for r in sample}<={r['slot_id'] for r in rows('controls/approved.jsonl')}

def test_custody_hashes_and_verified_crops():
    d=data()
    for group in ['inputs','outputs','prior_unchanged']:
        for p,digest in d[group].items():
            assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
    for r in rows('controls/crop_checks_cc.jsonl'):
        assert not r['crop_unavailable']
        assert '/scratchpad/n1_cache/crops/' in r['crop']
        assert hashlib.sha256(Path(r['crop']).read_bytes()).hexdigest()==r['crop_sha256']
