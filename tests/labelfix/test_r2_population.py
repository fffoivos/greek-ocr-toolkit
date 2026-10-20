"""R2P2 role isolation and teacher-seen provenance regression checks."""
import json
from pathlib import Path
import pytest
from PIL import Image
from scripts.labelfix.clariden.r1_common import rows,write_rows,sha256
from scripts.labelfix.clariden.r2_manifest import ManifestPool
from scripts.labelfix.clariden import r2_teacher as teacher

@pytest.mark.parametrize('role',['validation_reserve','witness','calibration','supervision','unknown'])
@pytest.mark.parametrize('operation',['add','remove','unknown'])
def test_manifest_refuses_nontrain_before_any_slot_operation(tmp_path,role,operation):
    from unittest.mock import patch
    p=tmp_path/'manifest.jsonl'
    r=dict(role=role,slot_id=['a'*64,0])
    if operation=='remove':r['removes']=r['slot_id']
    if operation=='unknown':r['unknown']=['accent']
    write_rows(p,[r])
    old=type('Old',(),dict(path=tmp_path,arm='A',index=[]))()
    with patch('scripts.labelfix.clariden.r2_manifest.inventory_ids',return_value=[]):
        with pytest.raises(ValueError,match='requires train role'):ManifestPool(old,p,tmp_path/'unused')

def test_teacher_writes_four_physically_separate_roles_and_provenance(tmp_path,monkeypatch):
    # Exercise the complete export routing/receipts without model inference.
    image=tmp_path/'crop.png';Image.new('L',(40,20),255).save(image)
    checkpoint=tmp_path/'model';checkpoint.write_bytes(b'fixture')
    monkeypatch.setattr(teacher,'TEACHER_SHA',sha256(checkpoint))
    class Alignment:
        def to_record(self):return dict(prediction='α')
    class Recognizer:
        def __init__(self,*a,**kw):pass
        def align_batch(self,images):return [Alignment() for _ in images]
    monkeypatch.setattr(teacher,'Recognizer',Recognizer)
    monkeypatch.setattr(teacher,'load_reader',lambda *a:None)
    coverage=[dict(start=0,base='α',span=[4,14],reason='test',fused=False,evidence_state='known')]
    monkeypatch.setattr(teacher,'extract_line',lambda *a,**kw: ([(0,0,0,0,0,0,[0]*4,[[0,1]])],[],None,None,coverage,dict(threshold=128,pixel_height=12)))
    monkeypatch.setattr(teacher,'full_predictions',lambda *a: [dict(start=0,base='α',heads={},factors=[0]*4)])
    monkeypatch.setattr(teacher,'plausible_span',lambda *a:(True,None))
    records=[dict(line_id=role,doc=role,source='test',role=role,image=str(image),crop_sha256=sha256(image),teacher_seen_document=role=='train') for role in teacher.ROLES]
    population=tmp_path/'population.jsonl';write_rows(population,records)
    out=tmp_path/'export';teacher.export(population,checkpoint,checkpoint,out,'cpu',True,recognizer_sha256=sha256(checkpoint))
    paths=[out/f'chunk-000000-{role}.jsonl.gz' for role in teacher.ROLES]
    assert len(set(paths))==4
    for role,p in zip(teacher.ROLES,paths):
        result=list(rows(p));assert len(result)==1
        assert result[0]['line_id']==role and result[0]['role']==role
        assert result[0]['teacher_seen_document']==(role=='train')

@pytest.mark.parametrize('role',['validation_reserve','witness','calibration'])
def test_stage_a_refuses_bound_nontrain_even_if_manifest_omits_role(tmp_path,monkeypatch,role):
    from scripts.labelfix.clariden import r2_run
    from scripts.labelfix.clariden.r2_mock import prepare
    cfg=prepare(tmp_path/'mock',__file__,__file__)
    monkeypatch.setattr(r2_run,'TEACHER_SHA',sha256(__file__))
    population=list(rows(cfg['line_list']))
    population[0]['role']=role
    write_rows(cfg['line_list'],population);cfg['sha256'][cfg['line_list']]=sha256(cfg['line_list'])
    manifest=list(rows(cfg['manifest']));manifest[0].update(doc=population[0]['doc'],line_id=population[0]['line_id'])
    write_rows(cfg['manifest'],manifest);cfg['sha256'][cfg['manifest']]=sha256(cfg['manifest'])
    with pytest.raises(ValueError,match='requires train role'):r2_run.validate(cfg,True)


def test_stage_a_refuses_dropped_teacher_seen_flag(tmp_path,monkeypatch):
    from scripts.labelfix.clariden import r2_run
    from scripts.labelfix.clariden.r2_mock import prepare
    cfg=prepare(tmp_path/'mock',__file__,__file__)
    monkeypatch.setattr(r2_run,'TEACHER_SHA',sha256(__file__))
    population=list(rows(cfg['line_list']));population[0]['teacher_seen_document']=True
    write_rows(cfg['line_list'],population);cfg['sha256'][cfg['line_list']]=sha256(cfg['line_list'])
    manifest=list(rows(cfg['manifest']));manifest[0].update(doc=population[0]['doc'],line_id=population[0]['line_id'])
    write_rows(cfg['manifest'],manifest);cfg['sha256'][cfg['manifest']]=sha256(cfg['manifest'])
    with pytest.raises(ValueError,match='missing teacher_seen_document'):r2_run.validate(cfg,True)
