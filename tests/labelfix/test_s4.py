"""S4 pixel ownership, per-blob naming and independent cached line readings."""
import json
from pathlib import Path
from types import SimpleNamespace as C
import numpy as np
import pytest
from greekocr.labelfix.ink import Blob, MarkEvidence, mark_evidence
from greekocr.labelfix.markshape import name_marks, load_model
from greekocr.labelfix.ctc_align import Alignment, CharSpan
from greekocr.labelfix.reading import read_line_details, recogniser_slots, render_reading
from greekocr.labelfix.text import nfd
from tests.labelfix.test_s2 import synthetic

FIX = Path(__file__).parents[1]/'data/labelfix_s4'
ROOT = Path(__file__).parents[2]


def component(i, box, role):
    x0,y0,x1,y1=box
    return C(index=i,x0=x0,y0=y0,x1=x1,y1=y1,cx=(x0+x1)/2,
             w=x1-x0,h=y1-y0,role=role,darkness=20)


def ink_components(boxes):
    labels=np.zeros((70,100),int)
    cs=[]
    for i,(box,role) in enumerate(boxes,1):
        c=component(i,box,role);cs.append(c)
        labels[c.y0:c.y1,c.x0:c.x1]=i
    ci=synthetic(labels>0,cs);ci.labels=labels
    return ci


def test_capital_gap_excludes_previous_letter_and_distant_quote():
    ci=ink_components([((8,20,20,40),'letter'),((55,8,78,40),'letter'),
                       ((42,10,49,18),'mark'),((9,7,16,15),'mark'),
                       ((24,9,29,18),'punct')])
    ev=mark_evidence(ci,55,78,base_letter='Η')
    assert [(b.x0,b.x1) for b in ev.above]==[(42,49)]
    assert not mark_evidence(ci,8,20,base_letter='ν').above


def test_stacked_neighbour_needs_lower_anchor_and_cannot_touch_top():
    ci=ink_components([((30,20,48,40),'letter'),((35,12,42,18),'mark'),
                       ((32,3,46,9),'neighbour')])
    assert [b.source for b in mark_evidence(ci,30,48,base_letter='η').above]==['stacked','detached']
    ci.components[2].y0=0
    assert len(mark_evidence(ci,30,48,base_letter='η').above)==1
    ci.components[1].role='noise';ci.components[2].y0=3
    assert not mark_evidence(ci,30,48,base_letter='η').above


def test_split_letter_union_has_one_recogniser_owner():
    ci=ink_components([((20,20,24,40),'letter'),((34,20,38,45),'letter')])
    al=Alignment('η',[CharSpan('η',0,0,1,19,39)])
    slots=recogniser_slots(ci,'η',al)
    assert len(slots)==1 and slots[0]['component_ids']==[1,2]
    assert (slots[0]['component'].x0,slots[0]['component'].x1)==(20,38)
    lam=recogniser_slots(ci,'λ',Alignment('λ',[CharSpan('λ',0,0,1,19,39)]))
    assert len(lam[0]['component_ids'])==2
    al=Alignment('ηι',[CharSpan('η',0,0,1,19,29),CharSpan('ι',1,1,2,30,40)])
    assert all(len(s['component_ids'])==1 for s in recogniser_slots(ci,'ηι',al))


def test_certified_body_cannot_resnap_into_overlapping_consonant():
    ci=ink_components([((20,8,43,40),'letter'),((38,20,49,40),'letter')])
    ev=mark_evidence(ci,38,49,base_letter='ι',certified_body=(38,49))
    assert ev.body==(38,49) and not ev.above


class WeakPair:
    def predict(self,x):
        if x[0]>=2:
            return 'psili+grave',.38,{}
        return ('grave',.98,{}) if x[6]>.2 else ('psili',.98,{})


def test_low_probability_pair_composes_psili_grave_and_renders_alpha():
    a=Blob(10,5,15,13,20,'detached',0,1.2)
    b=Blob(19,4,24,14,20,'detached',60,2.5)
    ev=MarkEvidence(above=[a,b],xh=20,meanline=20,body=(10,28))
    named=name_marks(ev,WeakPair())
    assert named.parts==('psili','grave') and not named.unnamed
    assert render_reading('ά',[dict(start=0,parts=named.parts)])=='ἂ'


def test_unnamed_blob_is_parallel_flag_and_removes_recogniser_marks():
    class Unknown:
        def predict(self,x):return 'none',.3,{}
    ev=MarkEvidence(above=[Blob(10,5,15,10,10,'detached',0,1)],xh=20,body=(10,28))
    names=name_marks(ev,Unknown())
    assert names.unnamed==(0,) and not names.parts
    assert render_reading('ἅ',[dict(start=0,parts=names.parts)])=='α'


def test_whole_set_keeps_subscript_feature_context_used_in_training():
    class Context:
        def predict(self,x):
            return ('circumflex+subscript',.99,{}) if x[1] else ('none',.3,{})
    ev=MarkEvidence(above=[Blob(10,5,24,10,30,'detached',0,2)],
                    below=[Blob(11,40,15,49,20,'detached',80,2)],xh=20,body=(10,28))
    names=name_marks(ev,Context())
    assert names.parts==('circumflex','subscript') and names.method=='whole'


@pytest.fixture(scope='module')
def model():
    return load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json')


@pytest.mark.parametrize('line_id,required',[
    ('384c3f89-p000096-l0004','ᾗσι'),
    # Native crops conflict with the strings in the brief. These assertions
    # preserve visible ink rather than changing a classifier to fit that text.
    ('384c3f89-p000068-l0028','ἆσσον'),
    ('177b717d-p000013-l0009','Ἤταν'),
    ('51fe7386-p000024-l0015','Ὁ Ὄλυμπος'),
])
def test_actual_owner_lines_use_only_recogniser_letters_and_detector_marks(model,line_id,required):
    case=next(r for r in json.loads((FIX/'cases.json').read_text()) if r['line_id']==line_id)
    al=Alignment.from_record(case['alignment'])
    r=read_line_details(FIX/(line_id+'.png'),case['recogniser_text'],al,model)
    assert required in r.text and '?' not in r.text
    if line_id=='51fe7386-p000024-l0015':
        assert 'Ὄσσα' in r.text
    if line_id=='384c3f89-p000096-l0004':
        eta=[s for s in r.slots if s.get('parts')==('dasia','circumflex','subscript')]
        assert len(eta)==1 and len(eta[0]['component_ids'])==2
    # Changing recogniser accents does not change its base-letter locations.
    altered=''.join(c for c in nfd(case['recogniser_text']) if not __import__('unicodedata').combining(c))
    rr=read_line_details(FIX/(line_id+'.png'),altered,al,model)
    assert rr.text==r.text
