"""Coordinator L1E gate and receipt failures, all synthetic and CPU-only."""
from copy import deepcopy
import json
import pytest
from greekocr.labelfix.reading import LineReading
from greekocr.labelfix.release_gate import compose,compose_runtime,serialize,ENSEMBLE_CAVEAT


def runtime():
    c=[dict(start=0,base='α',scored=True,evidence_state='unadjudicated',uncertainty=[])]
    p=[dict(start=0,base='α',parts=['acute'])]
    s=dict(start=0,end=1,base='α',parts=['psili'],unnamed=[],word_final=True,
        localisation_unknown=False,segmentation_uncertain=False,evidence=dict(clipped_top=False,clipped_bottom=False))
    return dict(id='x',recogniser_text='α',coverage=c,r1_predictions=p,
        peer_predictions={a:deepcopy(p) for a in ('B','E')},peer_coverage={a:deepcopy(c) for a in ('B','E')},
        detector=serialize(LineReading('ἀ',[s],[])))


@pytest.mark.parametrize('mode',['ENSEMBLE_AB','ENSEMBLE_AE'])
def test_clean_agreement_ignores_detector_kind_and_names_from_A(mode):
    r=runtime();o=compose_runtime(r,mode)
    assert not o['hold_slots'] and o['slots'][0]['label_status']=='ACCEPT' and o['text']=='ά'
    assert compose_runtime(r,'PRESENCE')['hold_slots'] and compose_runtime(r,'FULL')['hold_slots']
    r['peer_predictions'][mode[-1]][0]['parts']=['grave']
    assert mode.lower()+'_mark_set_disagreement' in compose_runtime(r,mode)['hold_slots'][0]['reasons']


@pytest.mark.parametrize('arm',['A','B','E'])
@pytest.mark.parametrize('case',['missing','invalid','unknown','prediction_uncertainty','missing_coverage','missing_state',
    'missing_uncertainty','unknown_coverage','uncertainty','unscored','base_mismatch','coverage_base_mismatch'])
def test_every_reader_uncertainty_holds_even_on_agreement(arm,case):
    r=runtime();mode='ENSEMBLE_AE' if arm=='E' else 'ENSEMBLE_AB'
    p=r['r1_predictions'] if arm=='A' else r['peer_predictions'][arm]
    c=r['coverage'] if arm=='A' else r['peer_coverage'][arm]
    if case=='missing':p.clear()
    if case=='invalid':p[0].pop('parts')
    if case=='unknown':p[0]['evidence_state']='UNKNOWN'
    if case=='prediction_uncertainty':p[0]['uncertainty']=['no_pixel_evidence']
    if case=='missing_coverage':c.clear()
    if case=='missing_state':c[0].pop('evidence_state')
    if case=='missing_uncertainty':c[0].pop('uncertainty')
    if case=='unknown_coverage':c[0]['evidence_state']='UNKNOWN'
    if case=='uncertainty':c[0]['uncertainty']=['out_of_image_span']
    if case=='unscored':c[0]['scored']=False
    if case=='base_mismatch':p[0]['base']='ω'
    if case=='coverage_base_mismatch':c[0]['base']='ω'
    assert compose_runtime(r,mode)['hold_slots']


@pytest.mark.parametrize('mode',['ENSEMBLE_AB','ENSEMBLE_AE'])
@pytest.mark.parametrize('case',['localisation_unknown','segmentation_uncertain','unnamed','physical','ambiguity',
    'top','bottom','left','right','unseen','K1','edit_guard','geometry'])
def test_detector_uncertainty_K1_and_edit_guard_still_hold(mode,case):
    r=runtime();s=r['detector']['slots'][0]
    if case in ('localisation_unknown','segmentation_uncertain'):s[case]=True
    if case=='unnamed':s['unnamed']=[0]
    if case=='physical':s['physical_resolved']=False
    if case=='ambiguity':s['ambiguity']=['equal_owner']
    if case in ('top','bottom','right'):s['evidence']['clipped_'+case]=True
    if case=='left':
        s['base']='Α';r['recogniser_text']='Α'
        r['r1_predictions'][0]['base']='Α'
        for a in ('B','E'):r['peer_predictions'][a][0]['base']='Α'
        s['evidence']['clipped_left']=True
    if case=='unseen':s['evidence']['observation']={'above':'UNKNOWN'}
    if case=='K1':r['detector']['constraint_flags']=[dict(start=0,rule='C2',reason='impossible_by_rule')]
    if case=='edit_guard':r['recogniser_text']='α\u0304'
    if case=='geometry':r['detector']['geometry']={'physical_mapping':{'ambiguous':True}}
    assert compose_runtime(r,mode)['hold_slots']


def test_detector_apostrophes_and_quotes_survive_ensemble():
    r=runtime();s=r['detector']['slots'][0]
    s['apostrophe']=True;s['evidence']['apostrophes']=[dict(bbox=[8,0,10,3])]
    r['detector']['opening_quotes']=[dict(bbox=[0,0,2,4])]
    o=compose_runtime(r,'ENSEMBLE_AB')
    assert not o['hold_slots'] and o['text']=='“ά’'
    assert o['slots'][0]['evidence']['apostrophes']==s['evidence']['apostrophes']


@pytest.mark.parametrize('workers',[1,2])
def test_actual_release_has_caveat_control_pair_and_peer_evidence(tmp_path,workers):
    from scripts.labelfix.clariden.l1_common import release,rows,write_rows
    source=tmp_path/'source';source.write_text('original bytes')
    sel=tmp_path/'selection.jsonl';rt=tmp_path/'runtime.jsonl'
    write_rows(sel,[dict(id='x',label='α',wave='wave1c',source='test',script_class='greek_poly')]);write_rows(rt,[runtime()])
    binding=dict(detector='s6',r1_sha256='Ahash',policy_sha256='policy',code_commit='test',detector_commit='test',checkpoint_sha256={'A':'Ahash','B':'Bhash','E':'Ehash'})
    inp=dict(exclusions={},out_of_scope={},r0_policy='test',input_documents_sha256={})
    out=tmp_path/'release';release(sel,[rt],out,binding,source,inp,('presence','full','ensemble_ab'),workers)
    m=json.loads((out/'release_ensemble_ab.json').read_text());o=list(rows(out/m['overlay']))[0]
    assert m['release']=='v2-corrected-ensemble-ab-r' and m['ensemble_caveat']==ENSEMBLE_CAVEAT
    assert m['coverage_per_wave']['wave1c']['kept']==1 and m['checkpoint_sha256']['B']=='Bhash'
    assert o['status']=='corrected' and o['label']=='ά' and o['gate_decisions'][0]['peer_arm']=='B'
    assert list(rows(out/'ctrl_subset_ensemble_ab.jsonl.gz'))[0]['label']=='α'
    assert (out/'kept_ensemble_ab_line_ids.txt').read_text()=='x\n' and source.read_text()=='original bytes'


def test_wrong_checkpoint_arm_and_digest_are_rejected(tmp_path):
    import torch
    from scripts.labelfix.clariden.l1e_run import load_reader
    from scripts.labelfix.clariden.r1_common import sha256
    p=tmp_path/'best.pt';torch.save({'arm':'A'},p)
    with pytest.raises(ValueError,match='hash mismatch'):load_reader(p,'B','incorrect','cpu')
    with pytest.raises(ValueError,match='arm mismatch'):load_reader(p,'B',sha256(p),'cpu')


def test_missing_peer_does_not_reuse_A():
    r=runtime();r.pop('peer_predictions');assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']
    r=runtime();r.pop('peer_coverage');assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']


def test_page_and_runtime_use_identical_ensemble_decisions(monkeypatch):
    from scripts.labelfix import owner_pages_build_combined as pages
    from greekocr.labelfix.release_gate import deserialize
    r=runtime()
    monkeypatch.setattr(pages,'LINE_TEXT',{'x':r['recogniser_text']})
    monkeypatch.setattr(pages,'R1',{('x',0):r['r1_predictions'][0]})
    monkeypatch.setattr(pages,'COVERAGE',{'x':r['coverage']})
    rd,_=pages.combine('x',deserialize(r['detector']),'ENSEMBLE_AB',
        runtime=r)
    expected=compose_runtime(r,'ENSEMBLE_AB')
    assert serialize(rd)['slots']==expected['slots'] and rd.text==expected['text']


def test_saved_observation_flag_without_rule_holds_instead_of_crashing():
    r=runtime();r['detector']['constraint_flags']=[dict(start=0,reason='localisation_unknown')]
    assert compose_runtime(r,'ENSEMBLE_AB')['hold_slots']


@pytest.mark.parametrize('case',['valid','missing','corrupt','unaccounted'])
def test_window_audit_checks_receipts_shapes_and_all_A_slots(tmp_path,case):
    import numpy as np
    from scripts.labelfix.clariden.l1e_windows import audit
    from scripts.labelfix.clariden.r1_common import write_rows,write_json,sha256
    data=tmp_path/'historical/detector';data.mkdir(parents=True)
    selection=tmp_path/'selection.jsonl';write_rows(selection,[dict(id='x')])
    r=runtime();dp=data/'shard-00000-detector.jsonl.gz';write_rows(dp,[r])
    sp=data/'shard-00000-samples.json';wp=data/'shard-00000-wide.npy'
    write_json(sp,[dict(line=0,start=1 if case=='unaccounted' else 0,letter=0,mask=[20,40])])
    np.save(wp,np.zeros((1,64,128),np.uint8),allow_pickle=False)
    sr=dict(shard=0,complete=True,lines=1,windows=1,sha256={p.name:sha256(p) for p in (dp,sp,wp)})
    rp=data/'shard-00000-receipt.json';write_json(rp,sr)
    tp=data/'detector_receipt.json';write_json(tp,dict(complete=True,selection_sha256=sha256(selection),shards=[sr]))
    write_json(data.parent/'run_receipt.json',dict(complete=True,step_receipts={str(p.relative_to(data.parent)):sha256(p) for p in (rp,tp)}))
    if case=='missing':wp.unlink()
    if case=='corrupt':sp.write_text('[]')
    if case in ('corrupt','unaccounted'):
        with pytest.raises(ValueError):audit(data,selection,tmp_path/'audit.json',workers=1)
    else:
        result=audit(data,selection,tmp_path/'audit.json',workers=1)
        assert result['complete']==(case=='valid') and result['all_A_scored_windows_accounted']


def test_runner_refuses_historical_output_before_writing(tmp_path):
    from scripts.labelfix.clariden.l1e_run import run
    historical=tmp_path/'historical';historical.mkdir();cfg=tmp_path/'config.json'
    cfg.write_text(json.dumps(dict(historical_run=str(historical))))
    with pytest.raises(ValueError,match='immutable'):run(cfg,historical/'new',mock=True)
    assert list(historical.iterdir())==[]


def test_old_observation_recovery_uses_measured_pixels_and_real_width(tmp_path):
    from PIL import Image
    from scripts.labelfix.clariden.l1e_measure import recover_observation
    path=tmp_path/'wikisource/book/line.png';path.parent.mkdir(parents=True)
    Image.new('L',(40,32),255).save(path)
    meta={'x':dict(crop='docs/harvest/harvest_big/wikisource/crops/book/line.png',
        font_size=dict(pixel_measurements=0),coverage=[dict(start=0,span=[-1,41])])}
    receipt=recover_observation(meta,tmp_path)
    assert meta['x']['coverage'][0]['evidence_state']=='UNKNOWN'
    assert meta['x']['coverage'][0]['uncertainty']==['no_pixel_evidence','out_of_image_span']
    assert receipt['x']['width']==40
    meta['x']['coverage']=[dict(start=0,span=[1,39])];meta['x']['font_size']={}
    with pytest.raises(ValueError,match='without pixel measurements'):recover_observation(meta,tmp_path)
