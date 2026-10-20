"""S7 contracts: physical ambiguity, curved guides, crop coverage and scope."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from PIL import Image
from greekocr.labelfix import ink as I, toolkit_geometry as G
from greekocr.labelfix.ctc_align import Alignment, Recognizer
from greekocr.labelfix.reading import read_ink
from greekocr.labelfix.markshape import load_model
from greekocr.labelfix.text import clusters,nfd
from greekocr.glyphs.letters import LetterBox

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/'tests/data/labelfix_s6'


@pytest.mark.parametrize('variant',[[],['S1'],['S2'],['S3'],['S1','S2','S3']])
def test_substitutions_keep_every_recognizer_letter_and_native_pixels(variant,monkeypatch):
    def forbidden(*a,**k):raise AssertionError('recognition forbidden')
    monkeypatch.setattr(Recognizer,'__init__',forbidden)
    row=json.loads((FIX/'cases.json').read_text())[0]
    ci=I.analyse(Image.open(FIX/(row['line_id']+'.png')))
    labels=ci.labels.copy();pixels=ci.ink.copy()
    out=read_ink(ci,row['recogniser_text'],Alignment.from_record(row['alignment']),
                 load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json'),substitutions=variant)
    assert [s['start'] for s in out.slots]==[c.start for c in clusters(nfd(row['recogniser_text'])) if c.base.isalpha()]
    assert np.array_equal(ci.labels,labels) and np.array_equal(ci.ink,pixels)
    if 'S1' in variant:
        assert all('physical_resolved' in s for s in out.slots)
        assert all(not s.get('ambiguity') or s['localisation_unknown'] for s in out.slots)
    if 'S2' in variant:
        for s in out.slots:
            for b in s['evidence'].above:
                ys,xs=zip(*b.pixel_keys())
                assert np.all(np.array(ys)<np.floor(ci.shared_guides.mean[np.array(xs)]))


def test_unresolved_physical_group_is_never_split_by_ctc_count(monkeypatch):
    row=json.loads((FIX/'cases.json').read_text())[0]
    ci=I.analyse(Image.open(FIX/(row['line_id']+'.png')))
    c=next(c for c in ci.components if c.role=='letter')
    box=LetterBox(0,c.y0,ci.width,c.y1,(c.index,),1,3,False)
    monkeypatch.setattr(G,'letter_boxes',lambda g:[box])
    slots=G.physical_slots(ci,row['recogniser_text'],Alignment.from_record(row['alignment']))
    assert len(slots)>3
    assert all(s['component_ids']==[c.index] for s in slots)
    assert all(s['region_bounds']==[0,ci.width] for s in slots)
    assert all(s['localisation_unknown'] and not s['physical_resolved'] for s in slots)
    assert len(ci.physical_letters)==1


def test_validity_holes_and_directional_cut_are_unseen_even_with_no_border_ink():
    ci=SimpleNamespace(width=10,height=40,xh=10.,top=np.full(10,15.),bottom=np.full(10,25.),
        ink=np.zeros((40,10),bool),valid_mask=np.ones((40,10),bool),cut_masks={},toolkit_cuts=[])
    slot=dict(region_bounds=[2,8])
    assert G.observation(ci,slot)['above']=='OBSERVED'
    ci.valid_mask[8,4]=False
    assert G.observation(ci,slot)['above']=='UNSEEN'
    assert G.observation(ci,slot)['below']=='OBSERVED'
    ci.cut_masks={'bottom':np.ones(10,bool)}
    assert G.observation(ci,slot)['below']=='UNSEEN'


def test_invalid_validity_mask_rejected():
    with pytest.raises(ValueError,match='validity shape'):
        I.analyse(Image.new('L',(20,30),'white'),valid_mask=np.ones((2,2),bool))


@pytest.mark.parametrize('classes,eligible',[
    ('greek_monotonic',False),(['greek_monotonic','latin'],False),
    (['greek_monotonic','greek_polytonic'],True),('greek_polytonic',True),([],True), (None,True)])
def test_scope_uses_explicit_script_class(classes,eligible):
    assert G.polytonic_scope(classes)==eligible


def test_m2_preserves_unseen_hold_without_constraint_flags():
    from scripts.labelfix.m2_run import combine
    from greekocr.labelfix.reading import LineReading
    raw=LineReading('α',[dict(start=0,base='α',parts=[],unseen_zones=['above'],hold=True,
        locator_span=[0,10],component=None,evidence={})],[])
    pred={0:dict(parts=[],mark_probabilities={})}
    out=combine('α',raw,pred,[],'PRESENCE')
    assert out['slots'][0]['hold']
    assert 'crop_UNSEEN:above' in out['slots'][0]['hold_reasons']


def test_monotonic_scope_returns_before_any_reader_or_detector():
    from scripts.labelfix.m2_run import infer_line
    out=infer_line('line',None,None,None,None,script_class=['greek_monotonic'])
    assert out==dict(id='line',status='skipped',skip_reason='monotonic_scope')


def test_shared_body_repair_preserves_toolkit_curvature():
    from dataclasses import replace
    row=json.loads((FIX/'cases.json').read_text())[0]
    ci=I.analyse(Image.open(FIX/(row['line_id']+'.png')))
    curve=45.+3.*((np.arange(ci.width)/ci.width)-.5)**2
    ci.glyphs.band=replace(ci.glyphs.band,bottom=curve,top=curve-40.,xh=40.,degree=2)
    ci.xh=31.;ci.bottom=np.full(ci.width,44.);ci.top=ci.bottom-31.
    ci.font_fit=dict(source='pixel_lowercase_bodies',n=8,xh=31.)
    guides=G.shared_guides(ci,apply=True)
    assert guides.decision['winner']=='S6_body_repair'
    assert guides.decision['toolkit_xh']==40 and guides.decision['selected_xh']==31
    assert np.allclose(np.diff(guides.base),np.diff(curve))
    assert np.allclose(guides.base-guides.mean,31.)
    assert ci.shared_guides is guides


def test_no_runtime_substitution_is_implicitly_enabled():
    from greekocr.labelfix.reading import QUALIFIED_GEOMETRY
    assert not QUALIFIED_GEOMETRY
