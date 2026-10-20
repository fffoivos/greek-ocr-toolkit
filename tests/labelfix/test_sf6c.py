"""SF6c score provenance, native bounds and real runtime-writer regressions."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.ctc_align import Alignment, recognition_fields, transfer_alignment
from scripts.labelfix.clariden import l1_common
from tests.labelfix.test_sf6 import rich, overlay

POLICY=(gate,l1_common)


@pytest.mark.parametrize('value',[None,0.,.1,.5,True,False,float('nan'),float('inf'),-1,1.1,'0.9'])
@pytest.mark.parametrize('mode',gate.MODES)
def test_nonpositive_or_low_or_invalid_line_score_holds(value,mode):
    rt=rich('δ');rt['recognition_confidence']=value
    assert overlay(POLICY,"δ'",rt,mode)['status']=='hold'


@pytest.mark.parametrize('defect',['absent','unscored','no_regions','zero_region','floor_region',
    'wrong_text','wrong_base','wrong_start','no_provenance','line_mean_only','partial_window',
    'outside_image','missing_image_width','duplicate_region','missing_frames','unscored_region'])
def test_explicit_regional_scoring_is_required(defect):
    rt=rich('δ');ev=rt['recognition_evidence'];region=ev['regions'][0]
    if defect=='absent':rt.pop('recognition_evidence')
    elif defect=='unscored':ev['scored']=False
    elif defect=='no_regions':ev['regions']=[]
    elif defect=='zero_region':region['confidence']=0.
    elif defect=='floor_region':region['confidence']=gate.RECOGNISER_ABSENCE_FLOOR
    elif defect=='wrong_text':ev['text_sha256']='0'*64
    elif defect=='wrong_base':region['base']='α'
    elif defect=='wrong_start':region['start']=1
    elif defect=='no_provenance':ev.pop('provenance')
    elif defect=='line_mean_only':region['provenance']='mean_line_posterior'
    elif defect=='partial_window':region['window']=[10,18]
    elif defect=='outside_image':rt['image_width']=region['image_width']=15
    elif defect=='missing_image_width':region.pop('image_width')
    elif defect=='duplicate_region':ev['regions'].append(deepcopy(region))
    elif defect=='missing_frames':region.pop('frames')
    elif defect=='unscored_region':region['scored']=False
    assert overlay(POLICY,"δ'",rt)['status']=='hold'


@pytest.mark.parametrize('score',[.500001,.9,1.])
def test_genuine_regional_score_above_floor_can_certify_absence(score):
    rt=rich('δ');rt['recognition_confidence']=score
    rt['recognition_evidence']['regions'][0]['confidence']=score
    out=overlay(POLICY,"δ'",rt)
    assert (out['status'],out['label'])==('corrected','δ')
    assert out['deletion_checks'][0]['signals']==dict(reader=False,detector=True,recogniser=True)


@pytest.mark.parametrize('source',['A','B','E','recogniser'])
@pytest.mark.parametrize('span',[[0,7],[21,25],[100000,100010],[8,21],[-1,12],[10,1001]])
def test_each_source_must_belong_to_saved_window_and_image(source,span):
    rt=rich('α');rt['detector']['slots'][0]['evidence'].pop('observation')
    if source=='recogniser':rt['detector']['slots'][0]['locator_span']=span
    else:
        cov=rt['coverage'] if source=='A' else rt['peer_coverage'][source]
        cov[0]['span']=span
    assert overlay(POLICY,'ά',rt,'ENSEMBLE_AE')['status']=='hold'


def test_native_bounds_are_not_inferred_from_a_finite_window():
    rt=rich('ά');rt.pop('image_width');rt.pop('recognition_confidence')
    rt['detector']['slots'][0]['parts']=[]
    for preds in [rt['r1_predictions'],*rt['peer_predictions'].values()]:preds[0]['parts']=[]
    assert overlay(POLICY,'ά',rt)['status']=='hold'
    # The historical extractor explicitly checked native bounds, retaining
    # out_of_image_span as uncertainty. Preserve that saved provenance.
    for cov in [rt['coverage'],*rt['peer_coverage'].values()]:
        cov[0]['window_contract']={'schema':'r1-trained-full-height-v1'}
    assert overlay(POLICY,'ά',rt)['label']=='α'
    rt['peer_coverage']['B'][0]['uncertainty']=['out_of_image_span']
    assert overlay(POLICY,'ά',rt)['status']=='hold'


def test_missing_alignment_score_roundtrips_without_becoming_zero():
    record=dict(prediction='δ',n_frames=10,scale=1.,strip_width=40,spans=[['δ',1,2,10.,18.]])
    al=Alignment.from_record(record)
    assert al.confidence is None and Alignment('δ').confidence is None
    assert Alignment.from_record(al.to_record()).confidence is None
    assert recognition_fields({})['recognition_confidence'] is None
    assert recognition_fields({})['recognition_evidence']['scored'] is False
    assert recognition_fields({'recognition_confidence':0.})['recognition_evidence']['scored'] is False
    assert transfer_alignment('δx',al).confidence is None


def test_region_score_uses_all_window_frames_and_never_the_line_mean():
    al=Alignment('δ',n_frames=10,confidence=.99,frame_confidences=[.99]*10)
    slot=rich('δ')['detector']['slots'][0]
    al.frame_confidences[2]=.2
    ev=al.recognition_evidence([slot],40)
    assert ev['regions'][0]['confidence']==.2 and ev['regions'][0]['frames']==[2,5]
    assert Alignment.from_record(al.to_record()).recognition_evidence([slot],40)==ev
    legacy=Alignment.from_record(dict(al.to_record(),frame_confidences=None))
    assert legacy.recognition_evidence([slot],40)['regions']==[]
    changed=transfer_alignment('δx',al)
    assert Alignment.from_record(changed.to_record()).recognition_evidence([slot],40)['regions']==[]
    from scripts.labelfix.clariden.r1_common import transfer_record
    record=al.to_record();record['spans']=[['δ',1,2,10.,18.]]
    transferred,changed=transfer_record('δx',record)
    assert changed and Alignment.from_record(transferred).recognition_evidence([slot],40)['regions']==[]


@pytest.mark.parametrize('key',['recognition_evidence','image_width'])
def test_certification_provenance_and_bounds_are_content_bound(key):
    rt=rich('α');bound=gate.bind_runtime(rt)
    if key=='image_width':rt[key]=999
    else:rt[key]['regions'][0]['confidence']=.8
    assert gate.bind_runtime(rt)['evidence_sha256']!=bound['evidence_sha256']
    bound[key]=rt[key]
    with pytest.raises(ValueError,match='binding mismatch'):gate.bind_runtime(bound)


@pytest.mark.parametrize('writer',['m2','l1'])
def test_real_runtime_builders_preserve_missing_score(tmp_path,monkeypatch,writer):
    from PIL import Image
    from greekocr.labelfix import reading,ink
    from scripts.labelfix import m2_run
    from scripts.labelfix.clariden import l1_detect,r1_extract
    raw=reading.LineReading('δ',rich('δ')['detector']['slots'],[])
    extraction=([],[],[],{},[],{})
    monkeypatch.setattr(reading,'read_ink',lambda *a,**k:raw)
    monkeypatch.setattr(ink,'analyse',lambda image:None)
    monkeypatch.setattr(r1_extract,'extract_line',lambda *a,**k:extraction)
    monkeypatch.setattr(m2_run,'extract_line',lambda *a,**k:extraction)
    monkeypatch.setattr(m2_run,'reader_predictions',lambda *a,**k:{})
    al=Alignment('δ',n_frames=10,strip_width=40)
    if writer=='m2':
        rt=m2_run.infer_line('x',Image.new('L',(40,20)),al,None,None,script_class='greek_poly')
    else:
        image=tmp_path/'line.png';Image.new('L',(40,20)).save(image)
        monkeypatch.setattr(l1_detect,'crop_path',lambda *a:image)
        monkeypatch.setattr(l1_detect,'_STATE',((str(tmp_path),str(tmp_path),'toolkit',False),None))
        l1_detect.chunk((0,[(dict(id='x',crop=str(image)),al.to_record())]))
        from scripts.labelfix.clariden.r1_common import rows
        rt=next(rows(tmp_path/'shard-00000-detector.jsonl.gz'))
    assert rt['recognition_confidence'] is None
    assert rt['recognition_evidence']['scored'] is False and rt['recognition_evidence']['regions']==[]


def test_all_saved_reviewer_unsafe_releases_hold():
    path=Path('docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json')
    for w in json.loads(path.read_text()):
        out=overlay(POLICY,w['original'],w['runtime'],w['mode'])
        assert out['status']=='hold' and out['changes']==[] and 'label' not in out
