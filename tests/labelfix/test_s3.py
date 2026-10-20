"""Physical S3 regressions: stroke/speck/cutoff, vowel union and pinned slots."""
from types import SimpleNamespace as C
import json
from pathlib import Path
import numpy as np
from greekocr.labelfix.ink import Blob, MarkEvidence, mark_evidence, snap_body, subscript_shape
from greekocr.labelfix.linemetric import score_slots
from greekocr.labelfix.owner_slots import overlap_slots
from tests.labelfix.test_s2 import synthetic


def test_subscript_stroke_wedge_and_speck_darkness():
    ci=synthetic(np.zeros((65,65),bool));ev=MarkEvidence(xh=20,baseline=40,body=(10,30))
    assert subscript_shape(Blob(12,40,16,55,43,'detached',80,3),ev,ci)
    assert subscript_shape(Blob(12,40,17,46,20,'detached',50,1.4),ev,ci)
    assert not subscript_shape(Blob(12,42,14,44,4,'detached',0,1),ev,ci)
    assert not subscript_shape(Blob(45,40,48,48,20,'detached',80,2),ev,ci)
    b=Blob(12,40,15,48,20,'detached',80,2,faint=True)
    assert not subscript_shape(b,ev,ci)


def test_connected_subscript_and_cutoff_is_unknown():
    labels=np.zeros((55,60),int);labels[20:40,10:28]=1;labels[40:48,12:15]=1
    c=C(index=1,cx=19,x0=10,x1=28,y0=20,y1=48,w=18,h=28,role='letter',darkness=20)
    ci=synthetic(labels>0,[c]);ci.labels=labels
    ev=mark_evidence(ci,10,28,base_letter='η')
    assert len(ev.below)==1 and ev.below[0].source=='attached'
    assert not mark_evidence(ci,10,28,base_letter='ρ').below
    labels[48:,12:15]=1;c.y1=55;ci=synthetic(labels>0,[c]);ci.labels=labels
    ev=mark_evidence(ci,10,28,base_letter='η')
    assert ev.clipped_bottom and not ev.below
    m=score_slots([dict(truth=[['subscript','subscript']],detected=[],unknown_kinds=['subscript'])])
    assert m['total']['fn']==0 and m['total']['unknown_subscript_slots']==1


def test_split_eta_union_credits_arch_over_second_stroke():
    labels=np.zeros((65,70),int);labels[20:41,10:14]=1;labels[20:41,23:27]=2;labels[9:14,19:28]=3
    comps=[C(index=1,cx=12,x0=10,x1=14,y0=20,y1=41,w=4,h=21,role='letter',darkness=20),
           C(index=2,cx=25,x0=23,x1=27,y0=20,y1=41,w=4,h=21,role='letter',darkness=20),
           C(index=3,cx=23.5,x0=19,x1=28,y0=9,y1=14,w=9,h=5,role='mark',darkness=20)]
    ci=synthetic(labels>0,comps);ci.labels=labels
    assert snap_body(ci,11,26,vowel=True)==(10.,27.,'letter',1)
    ev=mark_evidence(ci,10,14,core_x0=11,core_x1=26,base_letter='η')
    assert ev.body==(10,27) and len(ev.above)==1
    assert not mark_evidence(ci,10,14,base_letter='η').above


def test_v8_fixture_maps_by_overlap_and_never_by_index():
    fixture=json.loads((Path(__file__).parents[1]/'fixtures/labelfix/owner_v8_slot.json').read_text())
    assert overlap_slots(fixture['v8_x0'],fixture['v8_x1'],fixture['current_slots'])==(9,[9])
    assert overlap_slots(100,110,fixture['current_slots'])==(None,[])
    assert overlap_slots(10,30,[dict(slot=1,bbox=[10,0,20,20]),dict(slot=2,bbox=[20,0,30,20])])==(None,[1,2])
