"""R1 contracts: labels, native font geometry, fused acceptance and isolation."""
import numpy as np
from PIL import Image, ImageDraw
import pytest
from scripts.labelfix.clariden.r1_common import agreement_targets, compose, check_disjointness, transfer_record, factors
from scripts.labelfix.clariden.r1_extract import window, window_geometry
from scripts.labelfix.clariden.r1_pixels import plausible_span, font_size, fused_slots, threshold_image


def test_exact_agreement_only():
    assert agreement_targets('ἄλφα ῥῶ','ἄλφα ῥῶ')[0]==[1,1,0,0]
    assert not agreement_targets('ἄλφα','ἂλφα')
    assert not agreement_targets('Ἄλφα','ἄλφα')
    assert not agreement_targets('άλλο','ἄλλο')
    assert agreement_targets('«ἄλφα»,','ἄλφα')[0]==[1,1,0,0]


def test_compound_roundtrip():
    assert compose([2,3,0,1])=='dasia+circumflex+subscript'
    assert factors('\u0314\u0342\u0345')==[2,3,0,1]
    assert compose([0,0,0,0])=='none'
    assert factors('\u0301\u0300') is None
    assert factors('\u0304') is None


def test_window_scaled_to_font_not_spacing():
    assert window_geometry([20,30],20)==(-10,45,[30*128/55,40*128/55])
    assert window_geometry([20,30],20,.75)[:2]==(5,45)
    a=Image.new('L',(80,40),255);b=Image.new('L',(80,80),255)
    ImageDraw.Draw(a).rectangle((20,10,29,29),fill=0)
    ImageDraw.Draw(b).rectangle((20,10,29,29),fill=0)
    letters=[('α',0,[20,30])]*3
    sa=font_size(threshold_image(a)[0],letters);sb=font_size(threshold_image(b)[0],letters)
    assert sa['pixel_height']==sb['pixel_height']
    x,m=window(a,[20,30],20)
    assert x.shape==(64,128) and len(m)==2
    assert x[:,0].max()==255


def test_fused_diagnostic_never_rejects():
    binary=np.zeros((40,60),bool);binary[10:30,10:40]=True
    letters=[('α',0,[10,25]),('υ',1,[25,40]),('ο',2,[42,57])]
    size=font_size(binary,letters);f=fused_slots(binary,letters,size['pixel_height'])
    assert f[0]['fused'] and f[1]['fused']
    assert plausible_span([10,25],size)[0]
    assert not plausible_span([10,100],size)[0]


def test_planted_overlap_fails():
    selection=[dict(doc='wikisource:a',id='a-p1-l1')]
    exclusions=dict(sets=dict(test=dict(documents=['wikisource:b'],line_ids=['b-p1-l1'])))
    assert check_disjointness(selection,exclusions)['test']['document_count']==0
    exclusions['sets']['test']['documents']=['wikisource:a:human']
    with pytest.raises(ValueError,match='C1 overlap'):check_disjointness(selection,exclusions)
    exclusions['sets']['test']['documents']=[]
    exclusions['sets']['test']['line_ids']=['a-p1-l1-human']
    with pytest.raises(ValueError,match='C1 overlap'):check_disjointness(selection,exclusions)


def test_transfer_matches_s4():
    from greekocr.labelfix.ctc_align import Alignment, transfer_alignment
    al=dict(prediction='α β',spans=[['α',0,1,0.,10.],[' ',1,2,10.,20.],['β',2,3,20.,30.]],n_frames=3,scale=1.,strip_width=30,confidence=.9)
    r,changed=transfer_record('α γβ',al)
    assert changed
    assert r['spans']==transfer_alignment('α γβ',Alignment.from_record(al)).to_record()['spans']


def test_score_preserves_truth_and_unscored_none():
    from scripts.labelfix.clariden.r1_score import map_lines,summaries
    line=dict(line_id='l',doc='d',dev=False,recogniser_text='αε',slots=[
        dict(slot=1,base='α',truth=[['accent','acute']],bbox=[0,0,10,20]),
        dict(slot=2,base='ε',truth=[['breathing','psili']],bbox=[10,0,20,20])],
        recogniser_slots=[dict(start=0,base='α',component_slot=1,locator_span=[0,10]),
                          dict(start=1,base='ε',component_slot=2,locator_span=[10,20])])
    meta={'l':dict(recogniser_text='αε',coverage_by_start={0:dict(fused=True),1:dict(fused=False)})}
    pred={('l',0):dict(cls='acute')}
    mapped,_=map_lines([line],meta,pred);stats=summaries(mapped)
    assert stats['all_unscored_none']['total']['tp']==1
    assert stats['all_unscored_none']['total']['fn']==1
    assert stats['scored']['total']['fn']==0
    assert mapped[0]['slots'][1]['truth']==line['slots'][1]['truth']
    assert mapped[0]['slots'][1]['detected']==[]
    assert stats['fused_scored']['total']['tp']==1


def test_balancing_arms_and_natural_none():
    from scripts.labelfix.clariden.r1_train import ArmBatches
    y=np.array([[0,0,0,0]]*60+[[1,1,0,0]]*10+[[0,1,0,0]]*30)
    for arm in 'ABCDE':
        sampler=ArmBatches(y,100,arm,42);batch=next(iter(sampler));yy=y[batch]
        assert len(batch)==100
        if arm in 'ABC':assert sum(~yy.any(axis=1))==40
        if arm=='E':assert sum(~yy.any(axis=1))==60
        if arm=='D':assert sorted(batch)==list(range(100))
        if arm!='D':assert sum(np.count_nonzero(yy,axis=1)>=2)>=5
