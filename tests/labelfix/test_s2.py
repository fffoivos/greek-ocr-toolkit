from types import SimpleNamespace as C
import numpy as np
from greekocr.labelfix.ink import CropInk, Blob, MarkEvidence, attached_marks, subscript_shape, punctuation_dot, faint_letter, apostrophe_candidates
from greekocr.labelfix.spellink import above_count_matches, judge
from greekocr.labelfix.linemetric import score_slots, pooled, mark_set, printed_words
from greekocr.labelfix.text import nfd
from tests.labelfix.test_spellcheck import prop, Shape, evidence, blob


def synthetic(mask, components=()):
    h,w=mask.shape
    return CropInk(np.where(mask,20.,245.),mask,mask.astype(int),20.,np.full(w,20.),np.full(w,40.),list(components),245.,w,h,20.)


def test_ascender_needs_a_real_neck():
    m=np.zeros((55,50),bool);m[10:40,20:28]=1
    c=C(index=1,x0=20,x1=28,y0=10,y1=40)
    assert not attached_marks(synthetic(m),c,20)[0]
    m[:]=0;m[10:16,20:28]=1;m[16:19,23]=1;m[19:40,20:28]=1
    assert attached_marks(synthetic(m),c,20)[0]


def test_speck_subscript_and_border():
    ci=synthetic(np.zeros((55,50),bool));ev=evidence(body=(10,30),baseline=40)
    assert not subscript_shape(Blob(12,42,14,43,2,'detached',0,1),ev,ci)
    b=Blob(12,40,15,46,15,'detached',80,2)
    assert subscript_shape(b,ev,ci)
    b.touches_border=True
    assert not subscript_shape(b,ev,ci)


def test_exclamation_dot_and_apostrophe():
    dot=C(index=1,cx=30,x0=28,x1=32,y0=38,y1=41,w=4,h=3,role='punct')
    stem=C(index=2,cx=30,x0=28,x1=32,y0=20,y1=34,w=4,h=14,role='punct')
    ci=synthetic(np.zeros((55,60),bool),[dot,stem])
    assert punctuation_dot(dot,ci)
    m=np.zeros((55,60),bool);m[12:18,29:33]=1
    ci=synthetic(m,[C(index=1,cx=31,x0=29,x1=33,y0=12,y1=18,w=4,h=6,role='mark')])
    assert apostrophe_candidates(ci,[(C(cx=21,x1=28),'δ',True)])
    assert not apostrophe_candidates(ci,[(C(cx=21,x1=28),'α',True)])


def test_faint_letter_not_accent():
    ci=synthetic(np.zeros((55,50),bool))
    assert faint_letter(C(cx=20,h=20,y0=20,y1=40,darkness=200),ci)


def test_fused_compound_count_and_judgement():
    p=prop('η','ᾗ');ev=evidence(above=[blob()],below=[blob()])
    assert above_count_matches(p.marks,ev)
    assert judge([p],'none',None,None,Shape(p.mark_cls),.998,ev=ev).accept
    assert not above_count_matches(nfd('ΐ')[1:],ev)


def test_two_line_metric_unknowns_and_exact_kinds():
    a=score_slots([dict(truth=mark_set('acute'),detected=mark_set('grave')),dict(truth=set(),detected=set())])
    b=score_slots([dict(truth=mark_set('dasia+circumflex+subscript'),detected=mark_set('dasia+circumflex')),dict(truth=None,detected=mark_set('acute'))])
    c=pooled([a,b])['total']
    assert (c['tp'],c['fp'],c['fn'],c['unknown_slots'])==(1,1,2,1)
    assert c['precision']==.5 and c['recall']==1/3


def test_print_truth_never_uses_unedited_prefill_or_recognizer_alone():
    l=dict(line_id='x',google=nfd('καλός η'),human=nfd('καλὸς η'),model=nfd('καλός ἡ'))
    assert printed_words(l,{})=={0:None,1:None}
    assert printed_words(l,{'x|0':dict(printed='καλός')})[0]==nfd('καλός')


def test_exclamation_dot_cannot_be_a_subscript_even_if_wedge_sized():
    from greekocr.labelfix.ink import mark_evidence
    m=np.zeros((60,60),int);m[20:37,28:32]=1;m[41:47,28:31]=2
    stem=C(index=1,cx=30,x0=28,x1=32,y0=20,y1=37,w=4,h=17,role='letter',darkness=20)
    dot=C(index=2,cx=29.5,x0=28,x1=31,y0=41,y1=47,w=3,h=6,role='punct',darkness=20)
    ci=synthetic(m>0,[stem,dot]);ci.labels=m
    assert not mark_evidence(ci,28,32,base_letter='η').below


def test_print_rescore_preserves_human_score_and_hold_column():
    from greekocr.labelfix.spellcheck_validate import score_print
    r=dict(google_core=nfd('ἡ'),decision=dict(column='HOLD',proposal='ἠ'),ratio_decision=dict(column='HOLD',proposal='ἠ'),outcome='correct')
    score_print(r,nfd('ἡ'))
    assert r['print_outcome']=='google_right' and r['outcome']=='correct'
    assert r['decision']['column']=='HOLD'
    score_print(r,None)
    assert r['print_outcome']=='unknown'
