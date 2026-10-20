"""Cycle-2 release counterexamples. Synthetic inputs; no model inference."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from greekocr.labelfix.reading import LineReading
from scripts.labelfix.m2_run import combine


def raw(parts=(), **kw):
    s=dict(start=0,end=1,base='α',parts=list(parts),unnamed=[],locator_span=[10,20],
           component=None,bbox=[10,10,20,30],evidence=dict(above=[],below=[],clipped_top=False,clipped_bottom=False))
    s.update(kw)
    return LineReading('α',[s],[])


def coverage(**kw):
    return [dict(start=0,scored=True,evidence_state='unadjudicated',uncertainty=[],**kw)]


@pytest.mark.parametrize('mode',['PRESENCE','FULL'])
@pytest.mark.parametrize('case',['unknown','outside','uncertainty','segmentation','top','bottom','localisation','unnamed','missing','missing_coverage','unscored'])
def test_invalid_observation_holds(case,mode):
    r=raw(); cov=coverage(); pred={0:dict(parts=[],mark_probabilities={})}
    if case in ('unknown','outside','uncertainty'):
        cov[0].update(evidence_state='UNKNOWN' if case!='uncertainty' else 'unadjudicated',uncertainty=['out_of_image_span' if case=='outside' else 'no_pixel_evidence'])
    elif case=='segmentation':r.slots[0]['segmentation_uncertain']=True
    elif case in ('top','bottom'):r.slots[0]['evidence']['clipped_'+case]=True
    elif case=='localisation':r.slots[0]['localisation_unknown']=True
    elif case=='unnamed':r.slots[0]['unnamed']=[0]
    elif case=='missing':pred={}
    elif case=='missing_coverage':cov=[]
    elif case=='unscored':cov[0].update(scored=False,reason='span_rejected')
    assert combine('ά',r,pred,cov,mode)['hold_slots']


def test_page_quote_and_missing_r1(monkeypatch):
    from scripts.labelfix import owner_pages_build_combined as p
    monkeypatch.setattr(p,'LINE_TEXT',{'synthetic':'α'})
    monkeypatch.setattr(p,'R1',{('synthetic',0):dict(cls='none')})
    r=raw();r.opening_quotes=[dict(bbox=[0,0,3,5])];r.text='“α'
    assert p.combine('synthetic',r)[0].text=='“α'
    monkeypatch.setattr(p,'R1',{})
    assert p.combine('synthetic',raw())[0].slots[0].get('hold')


@pytest.mark.parametrize('field,value,key',[('display_slot',2,'owner_changed'),('pixel_runs',[[0,1,3]],'pixels_changed'),('status','HOLD','status_changed')])
def test_matched_box_state(field,value,key):
    from scripts.labelfix.box_regression import diff_line
    a=dict(reading='αα',boxes=[dict(kind='above',bbox=[5,2,8,5],display_slot=1,pixel_runs=[[0,0,3]],source_ids=[1],status='raw-detection')])
    b=deepcopy(a);b['boxes'][0][field]=value
    assert diff_line(a,b,.3).get(key)


@pytest.mark.parametrize('original,proposal',[('ᾱ','α'),('é','e'),('α\u0301\u0300','α'),('α','α\u0304'),('α','a'),('α,','α.')])
def test_edit_guard(original,proposal):
    from greekocr.labelfix.release_gate import edit_guard
    assert edit_guard(original,proposal)


def test_external_flags_and_disagreement_are_decisive():
    from scripts.labelfix.agreement_mode import decide
    s=raw(['acute']).slots[0]
    assert decide(s,dict(parts=['acute'],mark_probabilities={}),coverage()[0],'PRESENCE',flagged=True)['action']=='HOLD'
    s['parts']=['psili']
    assert decide(s,dict(parts=['acute'],mark_probabilities={}),coverage()[0],'PRESENCE')['action']=='HOLD'


def test_review_binding_required(tmp_path):
    from scripts.labelfix.box_regression import validate_review_binding
    with pytest.raises(ValueError):validate_review_binding(None,{},[])


def test_apostrophe_pixel_boxes_are_serialized():
    import numpy as np
    from types import SimpleNamespace as NS
    from unittest.mock import patch
    from greekocr.labelfix import reading as R,ink as I
    from scripts.labelfix.owner_reading import serialize
    lab=np.zeros((40,40),int);lab[10:30,10:20]=1;lab[3:7,22:24]=2
    ci=I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,np.full(40,10.),np.full(40,30.),[],255.,40,40,20.)
    blob=I._blob(lab==2,0,0,'apostrophe',ci)
    c=NS(x0=10,x1=20,y0=10,y1=30,cx=15,index=1)
    s=dict(start=0,end=1,base='α',component=c,component_ids=[1],localisation_unknown=False,word_final=True)
    with patch.object(R,'recogniser_slots',return_value=[s]),patch('greekocr.labelfix.case.estimate_font'),patch('greekocr.labelfix.case.prepare'),patch.object(I,'apostrophe_candidates',return_value={0:[blob]}),patch.object(I,'mark_evidence',return_value=I.MarkEvidence()),patch.object(I,'opening_quote_candidates',return_value=[]),patch.object(R,'name_marks',return_value=NS(parts=(),unnamed=())):
        r=R.read_ink(ci,'α',None,None,filtered=False)
    assert serialize(r)['slots'][0]['evidence']['apostrophes']==[blob.to_record()]


@pytest.mark.parametrize('mode',['PRESENCE','FULL'])
def test_resolved_fused_slot_stays_eligible(mode):
    c=coverage();c[0].update(fused=True,component_owners=[0,1])
    r=combine('α',raw(),{0:dict(parts=[],mark_probabilities={})},c,mode)
    assert not r['hold_slots'] and r['slots'][0]['label_status']=='ACCEPT'


@pytest.mark.parametrize('mode',['presence','full'])
@pytest.mark.parametrize('original,base',[('ᾱ','α'),('é','e'),('α\u0301\u0300','α')])
def test_actual_overlay_rejects_unsupported_deletions(original,base,mode):
    from scripts.labelfix.clariden.l1_common import overlay
    from greekocr.labelfix.release_gate import serialize
    r=raw();r.slots[0]['base']=base;r.text=base
    runtime=dict(recogniser_text=original,detector=serialize(r),r1_predictions=[dict(start=0,parts=[])],coverage=coverage())
    rec=dict(id='synthetic',label=original,script_class='greek_poly')
    out=overlay(rec,runtime,mode,dict(detector='s6',r1_sha256='test',policy_sha256='test'))
    assert out['status']=='hold' and 'label' not in out


@pytest.mark.parametrize('case',['unknown','segmentation','clipping','flag'])
def test_actual_overlay_recomputes_old_modes(case):
    from scripts.labelfix.clariden.l1_common import overlay
    from greekocr.labelfix.release_gate import serialize
    r=raw();c=coverage()
    if case=='unknown':c[0].update(evidence_state='UNKNOWN',uncertainty=['no_pixel_evidence'])
    if case=='segmentation':r.slots[0]['segmentation_uncertain']=True
    if case=='clipping':r.slots[0]['evidence']['clipped_top']=True
    if case=='flag':r.constraint_flags=[dict(start=0,rule='test',reason='impossible_by_rule')]
    rt=dict(recogniser_text='ά',detector=serialize(r),r1_predictions=[dict(start=0,parts=[])],coverage=c,
            modes={'PRESENCE':dict(text='α',hold_slots=[])})
    o=overlay(dict(id='x',label='ά',script_class='greek_poly'),rt,'presence',dict(detector='s6',r1_sha256='x',policy_sha256='x'))
    assert o['status']=='hold' and o['gate_decisions'][0]['label_status']=='HOLD'


@pytest.mark.parametrize('original,proposal',[('e\u0301 α','é ά'),('α\u0304 α','ᾱ ά')])
def test_unsupported_cluster_bytes_cannot_be_normalized(original,proposal):
    from greekocr.labelfix.release_gate import edit_guard
    assert edit_guard(original,proposal)


def test_unsupported_cluster_can_stay_identical_while_supported_edit_changes():
    from greekocr.labelfix.release_gate import edit_guard
    assert not edit_guard('é α','é ά')


def test_full_vs_presence_and_same_pixels_kind_gate():
    r=raw(['grave']);r.slots[0]['evidence']['above']=[dict(bbox=[10,2,14,6],area=10)]
    pred={0:dict(parts=['acute'],mark_probabilities={})}
    assert not combine('ά',r,pred,coverage(),'PRESENCE')['hold_slots']
    assert combine('ά',r,pred,coverage(),'FULL')['hold_slots']
    r.slots[0]['parts']=['psili']
    assert combine('ά',r,pred,coverage(),'PRESENCE')['hold_slots']


def test_bound_notes_detect_tampering(tmp_path):
    from scripts.labelfix.box_regression import validate_review_binding
    import hashlib
    page=tmp_path/'old.html';page.write_text('reviewed')
    notes=tmp_path/'notes.jsonl';notes.write_text('{"line_id":"x","note":""}\n')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    binding=tmp_path/'binding.json';binding.write_text(json.dumps(dict(reviewed_page=str(page),reviewed_page_sha256=digest(page),notes_sha256={str(notes):digest(notes)})))
    assert validate_review_binding(binding,dict(page_sha256=digest(page)),[str(notes)])
    notes.write_text('changed')
    with pytest.raises(ValueError,match='notes binding'):validate_review_binding(binding,dict(page_sha256=digest(page)),[str(notes)])


def test_s7_geometry_probe_ambiguity_is_not_release_evidence():
    """C2-M03 is contained at release; the off-default adapter is unchanged."""
    from types import SimpleNamespace as NS
    from unittest.mock import patch
    import numpy as np
    from greekocr.labelfix import ink as I,toolkit_geometry as G
    from greekocr.labelfix.ctc_align import Alignment
    from greekocr.glyphs.letters import LetterBox
    lab=np.zeros((40,40),int);lab[10:30,5:15]=1;lab[10:30,25:35]=2
    ci=I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,np.full(40,10.),np.full(40,30.),[],255.,40,40,20.)
    ci.components=[NS(index=i) for i in (1,2)]
    boxes=[LetterBox(5,10,15,30,(1,),1,1),LetterBox(25,10,35,30,(2,),1,1)]
    al=Alignment.from_record(dict(prediction='α',spans=[['α',0,1,5.,35.]],confidence=.9,n_frames=10,scale=1.,strip_width=40))
    with patch.object(G,'glyph_view',lambda ink:None),patch.object(G,'letter_boxes',lambda view:boxes):slots=G.physical_slots(ci,'α',al)
    assert ci.physical_mapping['ambiguous']
    r=raw();r.slots[0].update({k:slots[0][k] for k in ('component_ids','localisation_unknown','segmentation_uncertain','ambiguity')})
    r.geometry={'physical_mapping':ci.physical_mapping}
    assert combine('α',r,{0:dict(parts=[],mark_probabilities={})},coverage(),'PRESENCE')['hold_slots']


def test_s7_per_x_prefilter_probe_cannot_release_absence():
    from types import SimpleNamespace as NS
    import numpy as np
    from greekocr.labelfix import ink as I
    lab=np.zeros((70,80),int);lab[21:24,18:22]=1
    mean=35.-.5*np.arange(80);base=mean+20
    ci=I.CropInk(np.where(lab>0,20.,255.),lab>0,lab,20.,mean,base,[],255.,80,70,20.)
    ci.components=[NS(index=1,x0=18,x1=22,y0=21,y1=24,w=4,h=3,cx=20.,role='mark',darkness=20.,area=12)]
    ci.shared_guides=NS(mean=mean,base=base,ascender=mean-10,descender=base+10)
    body=NS(index=2,x0=15,x1=45,y0=20,y1=40,w=30,h=20,cx=30.,role='letter')
    ev=I.mark_evidence(ci,15,45,base_letter='α',certified_body=(15,45),letter_region=dict(component=body,component_ids=[],region_bounds=[15,45],case_class='lowercase_body'))
    b=I._blob(lab==1,0,0,'detached',ci)
    assert I.zone_blob(ci,b,upper=mean).area==12 and not ev.above
    r=raw(evidence=ev);r.geometry={'substitutions':['S2']}
    assert combine('ά',r,{0:dict(parts=[],mark_probabilities={})},coverage(),'PRESENCE')['hold_slots']


def test_box_cli_refuses_unbound_notes(tmp_path,monkeypatch):
    from scripts.labelfix import box_regression as box
    old=tmp_path/'old.json';new=tmp_path/'new.json';notes=tmp_path/'notes.jsonl'
    old.write_text(json.dumps(dict(lines={})));new.write_text(old.read_text());notes.write_text('')
    monkeypatch.setattr('sys.argv',['box_regression',str(old),str(new),'--notes',str(notes)])
    with pytest.raises(ValueError,match='review-binding'):box.main()


def test_measurement_guards_original_unsupported_marks():
    from scripts.labelfix.m2_score import changes_for
    r=combine('α',raw(),{0:dict(parts=[],mark_probabilities={})},coverage(),'PRESENCE')
    run=dict(status='ok',recogniser_nfd='α',modes={m:r for m in ('PRESENCE','FULL')})
    events,_=changes_for(dict(google_label='ᾱ'),run)
    assert events['PRESENCE'][0]['status']=='HOLD'


def test_l1_release_pairs_actual_control_payload(tmp_path):
    from scripts.labelfix.clariden.l1_common import release,rows,write_rows
    from greekocr.labelfix.release_gate import serialize
    source=tmp_path/'source';source.write_text('ORIGINAL source bytes')
    selection=tmp_path/'selection.jsonl'
    rec=dict(id='x',label='α',wave='round1',source='test',script_class='greek_poly')
    write_rows(selection,[rec]);runtime=tmp_path/'runtime.jsonl'
    write_rows(runtime,[dict(id='x',recogniser_text='α',detector=serialize(raw()),r1_predictions=[dict(start=0,parts=[])],coverage=coverage())])
    binding=dict(detector='s6',r1_sha256='test',policy_sha256='test',code_commit='test',detector_commit='test')
    receipt=dict(exclusions={},out_of_scope={},r0_policy='test',input_documents_sha256='test')
    out=tmp_path/'release';counts=release(selection,[runtime],out,binding,source,receipt)
    for v in ('presence','full'):
        manifest=json.loads((out/f'release_{v}.json').read_text())
        assert manifest['release']==f'v2-corrected-{v}-r'
        assert list(rows(out/f'ctrl_subset_{v}.jsonl.gz'))[0]['label']=='α'
        assert (out/f'kept_{v}_line_ids.txt').read_text()=='x\n'
        assert counts[v]['unchanged']==1 and source.read_text()=='ORIGINAL source bytes'


def test_invalid_prediction_is_not_none_and_duplicate_coverage_rejected():
    assert combine('ά',raw(),{0:{}},coverage(),'PRESENCE')['hold_slots']
    with pytest.raises(ValueError,match='duplicate R1 coverage'):
        combine('ά',raw(),{0:dict(parts=[],mark_probabilities={})},coverage()+coverage(),'PRESENCE')


def test_irrelevant_bottom_clip_on_rho_does_not_ban_resolved_slot():
    r=raw();r.slots[0]['base']='ρ';r.slots[0]['evidence']['clipped_bottom']=True
    assert not combine('ρ',r,{0:dict(parts=[],mark_probabilities={})},coverage(),'FULL')['hold_slots']


def test_legacy_missing_owner_pixels_and_status_stay_unknown():
    from scripts.labelfix.box_regression import diff_line
    a=dict(reading='α',boxes=[dict(kind='above',bbox=[1,1,3,3])])
    b=deepcopy(a);b['boxes'][0].update(display_slot=1,status='raw-detection',pixel_runs=[[0,0,2]])
    d=diff_line(a,b,.3)
    assert d['owner_unknown'] and d['pixels_unknown'] and d['status_unknown']
    assert not d['owner_changed'] and not d['pixels_changed'] and not d['status_changed']


def test_saved_disagreement_strata_are_not_geometry_truth():
    root=Path(__file__).resolve().parents[2]
    from collections import Counter
    rows=[json.loads(s) for s in (root/'docs/records/labelfix/spellcheck/S7_evidence/kind_disagreements.jsonl').read_text().splitlines()]
    rows=[r for r in rows if r['variant']=='baseline']
    zones=lambda ps:{'below' if p=='subscript' else 'above' for p in ps}
    assert len(rows)==80
    assert sum(zones(r['detector_parts'])==zones(r['r1_parts']) for r in rows)==33
    assert Counter('unknown' if r['truth'] is None else 'R1' if r['r1_right'] else 'detector' if r['detector_right'] else 'neither' for r in rows)==dict(R1=62,detector=3,neither=2,unknown=13)
