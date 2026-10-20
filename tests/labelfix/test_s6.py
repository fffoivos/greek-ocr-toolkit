"""Native S6 witnesses: physical regions/marks, independent of naming labels."""
import hashlib,json
from pathlib import Path
from collections import Counter
import numpy as np
import pytest
from PIL import Image
from greekocr.labelfix import ink as I
from greekocr.labelfix.ctc_align import Alignment,Recognizer
from greekocr.labelfix.reading import read_ink
from greekocr.labelfix.markshape import load_model
from greekocr.labelfix.text import clusters,nfd
R=Path(__file__).parents[2];F=R/'tests/data/labelfix_s6'

@pytest.fixture(scope='module')
def witnesses():
    model=load_model(R/'docs/records/labelfix/markshape_model_S4.json');out={}
    for r in json.loads((F/'cases.json').read_text()):
        with Image.open(F/(r['line_id']+'.png')) as im:ci=I.analyse(im)
        labels=ci.labels.copy();mask=ci.ink.copy()
        reading=read_ink(ci,r['recogniser_text'],Alignment.from_record(r['alignment']),model)
        assert np.array_equal(labels,ci.labels) and np.array_equal(mask,ci.ink)
        assert Counter(s['start'] for s in reading.slots)==Counter(c.start for c in clusters(nfd(r['recogniser_text'])) if c.base.isalpha())
        out[r['line_id']]=(ci,reading)
    return out


def safe(reading):
    for s in reading.slots:
        ev=s['evidence']
        assert all(b.y1<=ev.meanline for b in ev.above if b.source!='preposed')
        assert all(b.y0>=ev.baseline for b in ev.below)
        boxes=[(b.x0,b.y0,b.x1,b.y1) for b in ev.above]
        assert len(boxes)==len(set(boxes))


def test_merged_iota_breathing_is_found_without_cutting_body(witnesses):
    ci,r=witnesses['602cc72e-p000155-l0009'];safe(r)
    s=next(s for s in r.slots if s['component_ids']==[3])
    assert s['base']=='ι' and s['case_class']!='capital'
    assert len(s['evidence'].above)==1 and s['evidence'].above[0].source=='attached'
    # The one acute touching upsilon must not gain a second body fragment.
    u=next(s for s in r.slots if s['component_ids']==[5])
    assert len(u['evidence'].above)==1
    assert s['evidence'].meanline<26


def test_owner_mid_top_boundary_for_every_mark(witnesses):
    ci,r=witnesses['602cc72e-p000113-l0030'];safe(r)
    assert ci.font_fit['source']=='pixel_lowercase_bodies'
    assert 28<=ci.xh<=34
    assert any(b.source=='attached' for s in r.slots for b in s['evidence'].above)


def fusion(reading,bases):
    groups={}
    for s in reading.slots:
        if s['fused']:groups.setdefault(tuple(s['component_ids']),[]).append(s)
    return next(ss for ss in groups.values() if ''.join(s['base'] for s in ss)==bases)


def test_tau_upsilon_each_has_a_region_accent_owned_by_upsilon(witnesses):
    ci,r=witnesses['384c3f89-p000091-l0039'];safe(r)
    t,u=fusion(r,'τυ')
    assert t['region_bounds'][1]==u['region_bounds'][0]
    assert t['component'].x1<=u['component'].x0
    assert not t['evidence'].above and u['evidence'].above
    assert not t['localisation_unknown'] and not u['localisation_unknown']


def test_three_fused_letters_keep_omega_mark(witnesses):
    ci,r=witnesses['8b6b0de9-p000007-l0030'];safe(r)
    ss=fusion(r,'στω')
    assert all(s['fusion_size']==3 and not s['localisation_unknown'] for s in ss)
    assert all(a['region_bounds'][1]==b['region_bounds'][0] for a,b in zip(ss,ss[1:]))
    assert ss[-1]['evidence'].above and not any(s['evidence'].above for s in ss[:-1])


def test_split_eta_has_one_owner_and_both_top_marks(witnesses):
    ci,r=witnesses['384c3f89-p000142-l0002'];safe(r)
    eta=r.slots[0]
    assert eta['base']=='η' and eta['split_union'] and len(eta['component_ids'])==2
    assert len(eta['evidence'].above)==2
    assert not any(set(s['component_ids'])&set(eta['component_ids']) for s in r.slots[1:])


def test_reader_cannot_forward_ctc_and_does_not_use_recogniser_mark_names(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('CTC forward forbidden')
    monkeypatch.setattr(Recognizer,'__init__',forbidden)
    r=json.loads((F/'cases.json').read_text())[0]
    model=load_model(R/'docs/records/labelfix/markshape_model_S4.json');al=Alignment.from_record(r['alignment'])
    from greekocr.labelfix.reading import read_line_details
    a=read_line_details(F/(r['line_id']+'.png'),r['recogniser_text'],al,model)
    bare=''.join(c.base for c in clusters(nfd(r['recogniser_text'])))
    b=read_line_details(F/(r['line_id']+'.png'),bare,al,model)
    assert a.text==b.text


def test_one_joined_lobe_crossing_fusion_boundary_is_counted_once(monkeypatch):
    from types import SimpleNamespace
    from greekocr.labelfix import case
    from greekocr.labelfix.ctc_align import CharSpan
    from tests.labelfix.test_s2 import synthetic
    labels=np.zeros((60,70),int)
    labels[20:40,10:49]=1
    labels[8:18,24:35]=1
    labels[18:21,28:30]=1
    c=SimpleNamespace(index=1,x0=10,x1=49,y0=8,y1=40,w=39,h=32,cx=29.5,role='letter',darkness=20)
    ci=synthetic(labels>0,[c]);ci.labels=labels
    # Slight slope makes the two region-local cuts differ by a pixel.
    ci.top=20+np.arange(70)*.025;ci.bottom=ci.top+20
    monkeypatch.setattr(case,'classify',lambda *a,**k:dict(case_class='lowercase_body',pixel_class='lowercase_body',raw_pixel_class='lowercase_body',capital_probability=0.,all_caps=False))
    class Unknown:
        def predict(self,x):return 'none',.1,{}
    al=Alignment('αα',[CharSpan('α',0,0,1,10,29.5),CharSpan('α',1,1,2,29.5,49)])
    r=read_ink(ci,'αα',al,Unknown());safe(r)
    assert len(r.slots)==2 and all(s['fused'] for s in r.slots)
    assert sum(len(s['evidence'].above) for s in r.slots)==1


def test_rho_breathings_are_not_vetoed_as_ascender_or_descender_ink(witnesses):
    ci,r=witnesses['8b6b0de9-p000011-l0019'];safe(r)
    rhos=[s for s in r.slots if s['base']=='ρ']
    assert len(rhos)==2
    assert all(len(s['evidence'].above)==1 for s in rhos)
    assert all(s['evidence'].above[0].source=='attached' for s in rhos)
