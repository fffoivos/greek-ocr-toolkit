"""L1F identity quarantine, actual-frame regions, receipt corruption and resume."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3

from PIL import Image
import pytest
from greekocr.labelfix.ctc_align import Alignment, CharSpan, recognition_fields
from greekocr.labelfix.release_gate import _recogniser_scored
from scripts.labelfix.clariden import l1f_run as f
from scripts.labelfix.clariden.r1_common import write_rows, write_json


def alignment():
    return Alignment('δ', [CharSpan('δ',0,2,3,8.,20.)], 10, 1., 40, .99, [.99]*10)


def runtime():
    return dict(recogniser_text='δ', detector=dict(slots=[dict(start=0,base='δ',locator_span=[10.,18.],
                                                           evidence=dict(window=[8.,20.]))]))


def test_regional_minimum_uses_actual_frames_and_native_image():
    al=alignment(); old=al.to_record(); rt=runtime()
    record,counts,reasons=f.make_record('line',old,rt,al,40,{})
    assert _recogniser_scored(dict(rt,**recognition_fields(record)),rt['detector']['slots'][0],[8.,20.])
    assert counts['sf6c_certified_slots']==1 and not reasons
    al.frame_confidences[3]=.1
    record,counts,reasons=f.make_record('line',old,rt,al,40,{})
    assert record['recognition_evidence']['regions'][0]['confidence']==.1
    assert counts['sf6c_certified_slots']==0
    assert reasons=={'regional_min_confidence_at_or_below_0.5':1}
    assert record['recognition_confidence']==.99
    record,counts,reasons=f.make_record('line',old,rt,al,15,{})
    assert record['recognition_evidence']['regions']==[]
    assert not counts['sf6c_certified_slots']


@pytest.mark.parametrize('key',f.IDENTITY_KEYS)
def test_alignment_identity_mismatch_never_certifies_or_replaces_text(key):
    al=alignment(); old=al.to_record(); rt=runtime(); original=deepcopy(rt)
    old[key]=dict(prediction='α',n_frames=11,scale=2.,strip_width=41,spans=[['δ',1,3,8.,20.]])[key]
    record,counts,reasons=f.make_record('line',old,rt,al,40,{})
    assert key in record['provenance']['alignment_mismatches']
    assert record['recognition_evidence']['scored'] is False
    assert record['recognition_evidence']['regions']==[]
    assert record['frame_confidences']==al.frame_confidences
    assert rt==original and reasons=={'alignment_identity_mismatch':1}


@pytest.mark.parametrize('defect',['transferred','runtime_text'])
def test_transferred_or_unbound_runtime_text_is_withheld(defect):
    al=alignment(); old=al.to_record(); rt=runtime()
    if defect=='transferred':old['transferred']=True
    else:rt['recogniser_text']='α'
    record,_,_=f.make_record('line',old,rt,al,40,{})
    assert not record['provenance']['alignment_identity_match']
    assert record['recognition_evidence']['regions']==[]


def fixture(tmp_path):
    original=tmp_path/'input';original.mkdir(); crop_root=original/'pixels'; selected=[]; inv=[]
    for i in range(2):
        crop=f'docs/harvest/harvest_big/test/crops/doc/{i}.png'
        p=crop_root/crop;p.parent.mkdir(parents=True,exist_ok=True);Image.new('L',(40,48),255).save(p)
        selected.append(dict(id=str(i),crop=crop,wave='test'))
        inv.append(dict(crop=crop,path=str(p),bytes=p.stat().st_size,sha256=f.sha256(p)))
    write_rows(original/'selection.jsonl',selected)
    write_rows(original/'alignments.jsonl',[dict(crop=r['crop'],alignment=alignment().to_record()) for r in selected])
    write_rows(original/'runtime.jsonl',[dict(runtime(),id=r['id']) for r in reversed(selected)])
    write_rows(original/'crops.jsonl',inv)
    write_json(original/'crop_receipt.json',dict(complete=True,selected=2,
        selection_sha256=f.sha256(original/'selection.jsonl'),inventory_sha256=f.sha256(original/'crops.jsonl')))
    (original/'best.pt').write_bytes(b'checkpoint');(original/'best.safetensors').write_bytes(b'weights')
    return dict(verification_only=True,lines=2,input_run=str(original),binding_dir=str(original),
        selection=str(original/'selection.jsonl'),selection_sha256=f.sha256(original/'selection.jsonl'),
        crop_root=str(crop_root),layout='toolkit',crop_inventory=str(original/'crops.jsonl'),
        crop_receipt=str(original/'crop_receipt.json'),checkpoint=str(original/'best.pt'),
        checkpoint_sha256=f.sha256(original/'best.pt'),safetensors_sha256=f.sha256(original/'best.safetensors'),
        mock_runtime=[str(original/'runtime.jsonl')],alignment_sources=[dict(selection=str(original/'selection.jsonl'),
        alignments=str(original/'alignments.jsonl'),workers=1,chunk_size=1,batch_size=16)],
        expected_sha256={str(p):f.sha256(p) for p in original.iterdir() if p.is_file()})


def test_exact_resume_after_aggregation_failure_and_corruption_refusal(tmp_path,monkeypatch):
    cfg=fixture(tmp_path);out=tmp_path/'out';calls=[]
    class Recognizer:
        meta={}
        def __init__(self,*a,**k):pass
        def align_batch(self,images):calls.append(len(images));return [alignment() for _ in images]
    monkeypatch.setattr(f,'Recognizer',Recognizer)
    monkeypatch.setattr(f,'code_sources',lambda:{'test':'unchanged'})
    result=f.run(cfg,out,mock=True)
    assert result['complete'] and result['lines']==2 and result['totals']['alignment_identity_matches']==2
    before={p:p.read_bytes() for p in (out/'shards').glob('*/receipt.json')}
    (out/'receipt.json').unlink()  # allocation ended after durable shards
    assert f.run(cfg,out,mock=True)['complete'] and calls==[1,1]
    assert all(p.read_bytes()==content for p,content in before.items())
    payload=next((out/'shards').glob('*/frames.jsonl.gz'));payload.write_bytes(payload.read_bytes()+b'corruption')
    with pytest.raises(ValueError,match='output hash mismatch'):f.run(cfg,out,mock=True)


def test_crop_corruption_stops_before_plan_or_forward(tmp_path):
    cfg=fixture(tmp_path);p=next((tmp_path/'input/pixels').rglob('*.png'));p.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='crop receipt mismatch'):f.run(cfg,tmp_path/'out',mock=True)
    assert not (tmp_path/'out').exists()


def test_no_allocation_or_historical_output_writes(tmp_path):
    cfg=fixture(tmp_path)
    with pytest.raises(ValueError,match='separate'):f.run(cfg,tmp_path/'input/new',mock=True)
    with pytest.raises(ValueError,match='requires Slurm'):f.run(cfg,tmp_path/'out',mock=False)
