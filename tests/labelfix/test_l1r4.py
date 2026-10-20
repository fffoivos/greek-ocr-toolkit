"""Receipt, exact identity, omission and audit-set-difference contracts for L1R4."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3

import pytest

from scripts.labelfix.clariden import l1r4_join as j, l1r4_census as census
from scripts.labelfix.clariden import l1c_census as c

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def data():
    spec = c.load(ROOT/'config/l1r4_mock.json')['l1f']
    root=Path(spec['root']); final=c.load(root/'receipt.json')
    records=list(c.rows(root/final['shards'][0]['output']))
    db=sqlite3.connect(f'file:{root / "plan.sqlite"}?mode=ro',uri=True)
    planned={lid:(json.loads(saved),json.loads(rt)) for lid,saved,rt in db.execute('SELECT id,saved,runtime FROM lines')}
    db.close()
    return spec, final, records, planned


def test_verified_l1f_final_all_shards_and_identity_accounting(data):
    spec,final,records,planned=data
    result=j.verify_receipt(spec)
    assert result['lines']==64 and result['shards']==1
    assert result['totals']['alignment_identity_matches']==62
    assert result['totals']['alignment_identity_mismatches']==2


@pytest.mark.parametrize('field,value',[('lines',63),('shards',2),('job_id','wrong'),('config_sha256','bad'),('code_sha256','bad'),('receipt_sha256','bad')])
def test_receipt_rejects_wrong_population_identity_and_provenance(data,field,value):
    spec,*_=data; bad=dict(spec,**{field:value})
    with pytest.raises(ValueError): j.verify_receipt(bad)


def test_identity_refusals_have_all_three_fields_absent(data):
    spec,final,records,planned=data; withheld=0; matched=0
    for row in records:
        saved,rt=planned[row['line_id']]
        fields=j.validate_record(row,saved,rt,spec,final['binding'])
        if row['provenance']['alignment_identity_match']:
            assert all(k in fields for k in j.FIELDS)
            matched+=1
        else:
            assert fields=={} and not any(k in fields for k in j.FIELDS)
            withheld+=1
    assert (matched,withheld)==(62,2)


@pytest.mark.parametrize('defect',['text','saved_span','score','region','width','fresh_hash','false_match'])
def test_reconstruction_rejects_forged_or_misaligned_evidence(data,defect):
    spec,final,records,planned=data
    row=deepcopy(next(r for r in records if r['provenance']['alignment_identity_match']))
    saved,rt=deepcopy(planned[row['line_id']])
    if defect=='text': rt['recogniser_text']+='α'
    elif defect=='saved_span': saved['scale']+=1
    elif defect=='score': row['recognition_confidence']=True
    elif defect=='region': row['recognition_evidence']['regions']=[]
    elif defect=='width': row['image_width']=True
    elif defect=='fresh_hash': row['provenance']['alignment_identity_sha256']='bad'
    else:
        row=deepcopy(next(r for r in records if not r['provenance']['alignment_identity_match']))
        saved,rt=deepcopy(planned[row['line_id']]); row['provenance']['alignment_identity_match']=True
    with pytest.raises(ValueError): j.validate_record(row,saved,rt,spec,final['binding'])


def test_join_by_id_ignores_order_and_drops_stale_fields(data,tmp_path):
    spec,final,records,planned=data
    index=tmp_path/'join.sqlite'; db=sqlite3.connect(index)
    db.execute('CREATE TABLE evidence(id TEXT PRIMARY KEY,anchor_sha TEXT,fields TEXT)')
    runtime=[]
    for row in records:
        saved,rt=planned[row['line_id']]; rt=dict(rt,id=row['line_id'])
        fields=j.validate_record(row,saved,rt,spec,final['binding'])
        db.execute('INSERT INTO evidence VALUES(?,?,?)',(rt['id'],c.digest(j.anchor(rt)),c.canonical(fields)))
        runtime.append(dict(rt,recognition_confidence=.99,recognition_evidence={'scored':True},image_width=999))
    db.commit();db.close()
    joined=j.join_runtime(list(reversed(runtime)),index)
    assert [r['id'] for r in joined]==list(reversed([r['id'] for r in runtime]))
    assert sum('recognition_confidence' not in r for r in joined)==2
    bad=deepcopy(runtime[:1]); bad[0]['detector']['slots'][0]['evidence']['window']=[0,1]
    with pytest.raises(ValueError,match='identity'):j.join_runtime(bad,index)
    with pytest.raises(ValueError,match='identity'):j.join_runtime([dict(runtime[0],id='absent')],index)


def test_census_delta_uses_line_set_difference_even_at_equal_counts(tmp_path):
    src=ROOT/'docs/records/labelfix/spellcheck/clariden/L1R3_evidence'
    old=c.load(src/'mock_changes_CHANGES.json'); new=deepcopy(old)
    rows=list(c.rows(src/'mock_changes_real_mark_correction_lines.jsonl'))
    before=tmp_path/'old.jsonl';after=tmp_path/'new.jsonl'
    from scripts.labelfix.clariden.r1_common import write_rows
    write_rows(before,rows)
    changed=deepcopy(rows);changed[0]['line_id']='new-id'
    write_rows(after,changed)
    result=census.compare(old,new,before,after,tmp_path/'newly.jsonl')
    assert result['newly_real_mark_correction_rows']==1
    assert list(c.rows(tmp_path/'newly.jsonl'))==[changed[0]]
    mode=changed[0]['mode']
    assert result['modes'][mode]['overall']['real_mark_correction_lines']['delta']==0
    assert result['modes'][mode]['no_longer_real_mark_correction_lines']==1


def test_production_decoding_allocation_guard(data,tmp_path,monkeypatch):
    spec,*_=data; monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    with pytest.raises(ValueError,match='Slurm'):j.prepare_join(dict(spec,verification_only=False),[],tmp_path,{})
    with pytest.raises(ValueError,match='64-line'):j.prepare_join(spec,[],tmp_path,{})


def test_sealed_shard_corruption_and_missing_files_are_rejected(data,tmp_path):
    import shutil
    spec,*_=data
    root=tmp_path/'l1f'; shutil.copytree(spec['root'],root)
    changed=dict(spec,root=str(root))
    assert j.verify_receipt(changed)['complete']
    payload=root/'shards/shard-00000/frames.jsonl.gz'
    original=payload.read_bytes();payload.write_bytes(original+b'corrupt')
    with pytest.raises(ValueError,match='SHA-256'):j.verify_receipt(changed)
    payload.unlink()
    with pytest.raises((ValueError,FileNotFoundError)):j.verify_receipt(changed)


def test_complete_join_seals_and_rejects_resume_index_corruption(data,tmp_path):
    spec,*_=data
    selected=list(c.rows(ROOT/'artifacts/labelfix_l1e/fixture_v4/mock/selection.jsonl'))
    result=j.prepare_join(spec,selected,tmp_path,{})
    assert result['complete'] and result['lines']==64
    assert len(result['withheld_lines'])==2
    assert result['per_wave']['heldout-verification']['counts']['sf6c_certified_slots']==1704
    assert j.prepare_join(spec,selected,tmp_path,{})==result
    index=tmp_path/'l1f_join.sqlite';index.write_bytes(index.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='resume'):j.prepare_join(spec,selected,tmp_path,{})


def test_job2_rejects_output_overlap_before_writing(tmp_path):
    cfg=c.load(ROOT/'config/l1r4_mock.json')
    source=tmp_path/'input';source.mkdir()
    config=tmp_path/'cfg.json';c.atomic_json(config,cfg)
    with pytest.raises(ValueError,match='separate'):
        census.run(source,source/'nested',1,config)
    assert list(source.iterdir())==[]
