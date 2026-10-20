"""Native planted witnesses and the owner-labelled NW1b calibration gate."""
import hashlib
import importlib.util
import json
from pathlib import Path
from tests._paths import ADMISSION

import numpy as np
import pytest
from PIL import Image
from greekocr.glyphs.foreign_ink import prepare_mask_page, _centre_fit, PARAMETERS
from greekocr.harvest.neighbour_words import components, runs, frozen, PARAMS_SHA, DEFAULTS
from greekocr.harvest.admission import evaluate, run_files, NEIGHBOUR_PARAMS

BASE = ADMISSION / 'nw1b'
CARDS = json.loads((BASE.parent/'seg/calibration_ledger.json').read_text())['cases']
REPORT = json.loads((BASE/'calibration.json').read_text())


def line(centre):
    return dict(x0=0, x1=190, xheight=10., baseline=np.full(190,centre+5.), meanline=np.full(190,centre-5.))


@pytest.mark.parametrize('case,drop', [('full_word',True),('six_tenths',True),('lower_halves',False),('upper_halves',False),('clean',False)])
def test_original_crop_planted(case,drop):
    pixels=np.full((80,190),255,np.uint8)
    for x in range(10,166,13):
        pixels[45:55,x:x+8]=0
        if case!='clean':
            pixels[15:25,x:x+8]=0
    image=Image.fromarray(pixels)
    before=image.tobytes()
    page=prepare_mask_page(image)
    own=_centre_fit(line(50));other=_centre_fit(line(20))
    box=[0,20 if case=='lower_halves' else 19 if case=='six_tenths' else 10,190,60]
    if case=='upper_halves':
        # Own line above the neighbour; retain only its top half at bottom edge.
        own,other=other,own;box=[0,10,190,50]
    measure=dict(matched=True,xheight=10.,components=components(page,own,[other],box))
    assert bool(runs(measure,**NEIGHBOUR_PARAMS)) is drop
    result=evaluate(dict(label='ἑλληνικὸς πλήρης λόγος',source='bsb_poly1850',primary_class='poly1850'),neighbour_measurement=measure)
    assert result['failed_rules'] == ['geometry_unavailable']
    assert result['status'] == 'fail' and not result['passed']
    assert result['checks']['neighbour_words'] == 'n/a'
    assert image.tobytes()==before


def test_frozen_parameters_and_median_not_individual_height():
    assert frozen()==PARAMS_SHA
    assert hashlib.sha256(json.dumps(PARAMETERS,sort_keys=True,separators=(',',':')).encode()).hexdigest()==PARAMS_SHA
    m=dict(xheight=10,components=[dict(box=[x,0,x+4,h],height_xh=h/10,half_only=False) for x,h in zip((0,10,20,30),(2,6,6,10))])
    result=runs(m)[0]
    assert result['width_xh']==3.4 and result['median_height_xh']==.6
    assert result['components']==4 and result['min_height_xh']==.2
    assert not runs(m,min_components=5)
    assert not runs(m,min_width_xh=3.41)
    assert not runs(m,min_height_xh=.61)
    m['components'][3]['box']=[30,20,34,30]
    assert not runs(m)


def test_half_only_components_cannot_accumulate_into_word():
    m=dict(xheight=10,components=[dict(box=[x,0,x+8,8],height_xh=.8,half_only=True) for x in range(0,160,12)])
    assert not runs(m,**NEIGHBOUR_PARAMS)


def test_receipt_records_parameters(tmp_path):
    p=tmp_path/'input.jsonl'
    p.write_text(json.dumps(dict(source='bsb_poly1850',primary_class='poly1850',label='ἑλληνικὸς πλήρης λόγος'))+'\n')
    r=run_files([p],output_dir=tmp_path/'out')
    assert r['neighbour_words_ownership_params_sha256']==PARAMS_SHA
    assert r['neighbour_words_params']==NEIGHBOUR_PARAMS


@pytest.mark.parametrize('card',[c for c in CARDS if c['truth']=='keep'],ids=lambda c:c['row_id'])
def test_owner_22_keep_gate(card):
    assert not runs(card['measurement'],**NEIGHBOUR_PARAMS)


@pytest.mark.parametrize('card',[c for c in CARDS if c['truth']=='drop'],ids=lambda c:c['row_id'])
def test_all_drop_witnesses(card):
    assert runs(card['measurement'],**NEIGHBOUR_PARAMS)


def test_owner_calibration_reproducible():
    spec=importlib.util.spec_from_file_location('nw1b_calibrate',BASE/'calibrate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    cards,bindings=module.truth()
    assert bindings['ledger_sha256']!=REPORT['bindings']['ledger_sha256'] # CP4c re-freeze
    assert bindings['code_sha256']!=REPORT['bindings']['code_sha256'] # CP2 invalidates old code binding
    assert cards==CARDS
    assert sum(c['truth']=='keep' for c in CARDS)==22
    current=module.build_report()
    for section in ('default', 'candidate', 'defaults', 'gate', 'selected'):
        assert current[section] == REPORT[section]
    assert len(current['witnesses']['c1']['detected']) == 6
    assert REPORT['defaults']==DEFAULTS
    assert REPORT['default']['standalone']['confusion']==dict(tp=9,fp=4,fn=0,tn=18)
    assert REPORT['candidate']['standalone']['gate']
    assert not REPORT['gate'] and REPORT['selected'] is None
    assert REPORT['candidate']['combined']['confusion']==dict(tp=9,fp=4,fn=0,tn=18)
    assert REPORT['candidate']['params']==NEIGHBOUR_PARAMS


@pytest.mark.parametrize('matched',[True,False])
def test_shared_cli_auto_measures_id_rows(tmp_path, monkeypatch, matched):
    from greekocr.harvest import neighbour_words
    measured=[]
    def measure(records, **kwargs):
        measured.extend(records)
        return {r['row_id']:dict(matched=matched,xheight=10. if matched else None,components=[
            dict(box=[x,0,x+8,10],height_xh=1.,half_only=False) for x in range(0,144,12)] if matched else []) for r in records}
    monkeypatch.setattr(neighbour_words,'measure_rows',measure)
    row=dict(id='w2-test',page_id='p',crop_bbox=[0,0,190,20],source='bsb_poly1850',primary_class='poly1850',label='ἑλληνικὸς πλήρης λόγος')
    p=tmp_path/'w2.jsonl';p.write_text(json.dumps(row)+'\n')
    receipt=run_files([p],output_dir=tmp_path/'out')
    decision=json.loads((tmp_path/'out/w2_admission.jsonl').read_text())
    assert measured[0]['row_id']=='w2-test'
    assert decision['rules_failed']==['geometry_unavailable']
    assert decision['pass'] is False and receipt['rows_pass']==0
    assert receipt['neighbour_words_unmatched']==1
    assert receipt['neighbour_words_unavailable']==1
    assert receipt['neighbour_words_status_counts']=={'unavailable':1}


def test_missing_metadata_does_not_silently_pass(tmp_path):
    from greekocr.harvest.neighbour_words import page_measurements
    with pytest.raises(ValueError,match='missing/ambiguous'):
        page_measurements([dict(row_id='r',page_id='missing',crop_bbox=[0,0,20,20])],run_root=tmp_path/'run',cache=tmp_path/'cache')


@pytest.fixture
def staged_pair(tmp_path):
    import io
    spec=importlib.util.spec_from_file_location('nw1b_stage',BASE.parent/'stage_crops.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    source=tmp_path/'input/source.png';source.parent.mkdir()
    image=Image.fromarray(np.arange(200,dtype=np.uint8).reshape(10,20))
    image.save(source)
    rows=[]
    for i,box in enumerate(([0,0,10,10],[10,0,20,10])):
        buffer=io.BytesIO();image.crop(box).save(buffer,format='PNG',compress_level=3)
        rows.append(dict(row_id=f'test-{i}',id=f'test-{i}',source='bsb_poly1850',primary_class='poly1850',crop_bbox=box,
                         crop_sha256=hashlib.sha256(buffer.getvalue()).hexdigest(),crop_source_image=str(source),crop_source_sha256=module.sha(source)))
    admitted=tmp_path/'admitted.jsonl';features=source.parent/'features.jsonl';out=tmp_path/'output/crops'
    admitted.write_text(''.join(json.dumps(r)+'\n' for r in rows));features.write_bytes(admitted.read_bytes())
    module.stage(admitted,features,out)
    return module,admitted,features,out,rows


def test_withdrawal_preserves_png_bytes_and_marks_false(staged_pair):
    module,admitted,features,out,rows=staged_pair
    before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in out.rglob('*.png')}
    admitted.write_text(json.dumps(rows[0])+'\n')
    receipt=module.stage(admitted,features,out)
    manifest=[json.loads(l) for l in (out.parent/'crops_manifest.jsonl').read_text().splitlines()]
    assert {r['row_id']:r['admitted'] for r in manifest}=={'test-0':True,'test-1':False}
    assert receipt['count']==1 and receipt['retained_count']==2 and receipt['withdrawn_count']==1
    assert before=={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in out.rglob('*.png')}


def test_corrupt_withdrawn_crop_aborts_manifest_publication(staged_pair):
    module,admitted,features,out,rows=staged_pair
    previous=(out.parent/'crops_manifest.jsonl').read_bytes()
    admitted.write_text(json.dumps(rows[0])+'\n')
    (out/'bsb_poly1850/test-1.png').write_bytes(b'corrupt synthetic witness')
    with pytest.raises(ValueError,match='withdrawn crop hash mismatch'):
        module.stage(admitted,features,out)
    assert (out.parent/'crops_manifest.jsonl').read_bytes()==previous
