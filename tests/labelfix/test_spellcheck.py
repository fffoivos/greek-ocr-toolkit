"""S1 policy boundaries: lexicon proposes, pixels decide, recogniser only locates."""
from dataclasses import replace

import pytest

from greekocr.labelfix.ctc_align import Alignment, CharSpan
from greekocr.labelfix.ink import Blob, MarkEvidence
from greekocr.labelfix.lexicon import Lexicon
from greekocr.labelfix.markshape import mark_class
from greekocr.labelfix.spellink import (Proposal, alternatives, contradiction, dialytika_only, grave_proposal,
    judge, judge_grave, proposals, spell_ink_line, written_freq)
from greekocr.labelfix.text import nfd, tokenize


def lex(**words):
    l=Lexicon('poly19')
    for w,n in words.items(): l.add(nfd(w),n)
    l.finalize()
    return l


def prop(g,p,count=20):
    from greekocr.labelfix.spellink import _proposal
    return _proposal(nfd(g),nfd(p),count,multi=True)


def blob(angle=-50,source='detached',width=3):
    return Blob(10,2,10+width,8,10,source,angle,2.0)


def evidence(**kw):
    d=dict(above=[blob()],below=[],window=(5,25),xh=20,meanline=12,baseline=32,
           body=(10,20),body_source='letter',n_letters_in_span=1)
    d.update(kw)
    return MarkEvidence(**d)


class Shape:
    tau=.998
    def __init__(self,pred='circumflex',prob=.999): self.pred,self.prob=pred,prob
    def predict(self,x): return self.pred,self.prob,{self.pred:self.prob}


def alignment(text):
    text=nfd(text)
    return Alignment(text,[CharSpan(c,i,i,i+1,10+i*5,15+i*5) for i,c in enumerate(text)])


def test_n1_written_acute_is_attested_via_grave_and_never_lexically_proposed():
    l=lex(**{'τοκετὸς':100})
    assert written_freq(nfd('τοκετός'),l)==100
    assert proposals('τοκετός',l)[0]==[]
    assert not alternatives('τοκετός',l)


def test_n2_optional_initial_rho_breathing_not_proposed():
    assert proposals('ροή',lex(**{'ῥοή':100}))[0]==[]
    assert proposals('ῥοή',lex(**{'ροή':100}))[0]==[]


def test_n5_dialytika_only_never_hold(monkeypatch):
    p=prop('ἐυ','ἐϋ')
    assert p and dialytika_only(p)
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence(above=[]))
    rs=spell_ink_line('x',nfd('ἐυ'),nfd('ἐυ'),alignment('ἐυ'),object(),lex(**{'ἐϋ':50}),Shape('none'))
    assert rs[0]['decision']['column'] is None
    assert 'no_two_dots' in rs[0]['contradiction_reasons']


def test_dialytika_accept_needs_two_physical_dots():
    p=prop('λυει','λυεϊ')
    # classifier agreement alone cannot provide the dots
    ev=evidence(above=[blob()])
    j=judge([p],mark_class(p.google_marks),None,('test',0,30,10,20),Shape('dialytika'),.998,ev=ev)
    assert not j.accept


@pytest.mark.parametrize('tail,nxt,want',[('', 'λόγος',True),('', 'τις',False),(',', 'λόγος',True),('',None,True)])
def test_d2_enclitic_and_punctuation_candidates(tail,nxt,want):
    g=tokenize(nfd('καλός'+tail))[0]
    p=grave_proposal(g,nfd(nxt) if nxt else None,lex(**{'καλός':100}))
    assert bool(p)==want
    if tail or nxt is None:
        j=judge_grave(p,evidence(above=[blob(angle=0)]),None,positional=False,book_style='grave')
        assert not j.accept and 'grave_slope_required' in j.reason
        assert judge_grave(p,evidence(above=[blob(angle=50)]),None,positional=False,book_style='grave').accept


def test_d2_book_print_and_ink_must_agree():
    p=grave_proposal(tokenize(nfd('καλός'))[0],nfd('λόγος'),lex(**{'καλός':100}))
    flat=evidence(above=[blob(angle=0)])
    assert judge_grave(p,flat,None,positional=True,book_style='grave').accept
    assert not judge_grave(p,flat,None,positional=True,book_style='unknown').accept
    assert not judge_grave(p,evidence(above=[blob(angle=-50)]),None,positional=True,book_style='grave').accept
    assert not judge_grave(p,evidence(above=[blob(angle=50)]),None,positional=True,book_style='acute').accept


def test_absent_subscript_contradicts_but_clipping_is_abstention():
    p=prop('τῆ','τῇ')
    assert contradiction(p,evidence(),None,'circumflex',.99)==('contradicts','no_blob_below')
    assert contradiction(p,evidence(clipped_bottom=True),None,'circumflex',.99)==('abstains','clipped_band')
    assert contradiction(p,evidence(body_source='merged'),None,'circumflex',.99)[0]=='abstains'


def test_contradiction_classifier_google_at_dev_threshold_and_absent_above():
    p=prop('μηνα','μήνα')
    assert contradiction(p,evidence(above=[]),None,'none',.99)==('contradicts','too_few_above_blobs')
    p=prop('μήνα','μῆνα')
    assert contradiction(p,evidence(),dict(pred='acute',prob=.99),'acute',.99)[0]=='contradicts'
    assert contradiction(p,evidence(),dict(pred='acute',prob=.989),'acute',.99)[0]=='abstains'
    assert contradiction(p,evidence(above=[replace(blob(),faint=True)]),dict(pred='acute',prob=1),'acute',.99)[0]=='abstains'


def test_d1_unique_constraint_minimal_fallback_and_attested_preference():
    ps,why=proposals('βέ́́',lex())
    assert len(ps)==1 and ps[0].form==nfd('βέ') and why=='constraint_minimal'
    ps,why=proposals('εστι',lex(**{'ἐστι':40,'ἔστι':100}))
    assert {p.form for p in ps}=={nfd('ἐστι'),nfd('ἔστι')}
    assert why=='constraint_attested'


def test_l2_proposes_only_attested_possible_mark_alternatives(monkeypatch):
    l=lex(**{'μήνα':50,'μῆνα':5,'μὴνα':500,'μἡνα':500,'μηνα':4})
    ps=alternatives('μήνα',l)
    assert [p.form for p in ps]==[nfd('μῆνα')]
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence())
    r=spell_ink_line('x',nfd('μήνα'),nfd('μήνα'),alignment('μήνα'),object(),l,Shape())[0]
    assert r['stage']=='L2' and r['decision']['column']=='ACCEPT'
    assert r['decision']['proposal']=='μῆνα'
    r=spell_ink_line('x',nfd('μήνα'),nfd('μήνα'),alignment('μήνα'),object(),l,Shape(prob=.9))[0]
    assert r['decision']['column'] is None # never HOLD on L2


def test_model_different_word_changes_diagnostic_never_candidate_or_decision(monkeypatch):
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence())
    l=lex(**{'μῆνα':40})
    rs=[spell_ink_line('x',nfd('μήνα'),nfd(m),alignment(m),object(),l,Shape())[0] for m in ('μῆνα','χῶρα')]
    assert rs[0]['decision']==rs[1]['decision']
    assert rs[0]['proposals']==rs[1]['proposals']
    assert rs[0]['model_agrees'] and not rs[1]['model_agrees']
    assert rs[1]['locator']=='proportional'


def test_unique_hold_competing_abstains_and_physical_contradiction_vetoes(monkeypatch):
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence())
    def run(l):return spell_ink_line('x',nfd('μήνα'),nfd('μήνα'),alignment('μήνα'),object(),l,Shape(prob=.9))[0]
    assert run(lex(**{'μῆνα':40}))['decision']['column']=='HOLD'
    assert run(lex(**{'μῆνα':40,'μηνα':10}))['decision']['column'] is None
    assert run(lex(**{'μῇνα':40}))['decision']['column'] is None


def test_l2_includes_unmarked_vowel_but_never_holds(monkeypatch):
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence())
    l=lex(**{'των':50,'τῶν':100})
    r=spell_ink_line('x',nfd('των'),nfd('των'),alignment('των'),object(),l,Shape())[0]
    assert r['stage']=='L2' and r['decision']['column']=='ACCEPT'
    assert r['decision']['proposal']=='τῶν'
    r=spell_ink_line('x',nfd('των'),nfd('των'),alignment('των'),object(),l,Shape(prob=.9))[0]
    assert r['decision']['column'] is None


def test_line_end_non_grave_lexical_proposal_not_hidden_by_failed_d2(monkeypatch):
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence(above=[blob(angle=0)]))
    l=lex(**{'καλή':50,'καλῆ':100})
    r=spell_ink_line('x',nfd('καλή,'),nfd('καλή,'),alignment('καλή,'),object(),l,Shape())[0]
    assert r['stage']=='L2' and r['decision']['proposal']=='καλῆ'
    assert r['decision']['column']=='ACCEPT' and 'grave_slope_required' in r['d2_attempt']


def test_initial_capital_policy_and_legacy_lexicon_unchanged(monkeypatch):
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence())
    l=lex(**{'τοκετὸς':100,'μῆνα':49})
    assert l.freq('τοκετός')==0 # N1 must not modify Lexicon.freq / old rules
    def run(): return spell_ink_line('x',nfd('Μήνα'),nfd('Μήνα'),alignment('Μήνα'),object(),l,Shape())[0]
    assert run()['decision']['reason']=='excluded:initial_capital_unattested_50'
    l.counts[nfd('μῆνα')]=50;l.finalize()
    assert run()['decision']['column']=='ACCEPT'
    l.names[nfd('μῆνα')]=3
    assert run()['decision']['column'] is None


def test_ratio_is_separate_diagnostic_column(monkeypatch):
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence())
    l=lex(**{'μήνα':5,'μῆνα':100})
    r=spell_ink_line('x',nfd('μήνα'),nfd('χῶρα'),alignment('χῶρα'),object(),l,Shape(prob=.9))[0]
    assert r['stage']=='L2' and r['decision']['column'] is None
    assert r['ratio_stage']=='L1' and r['ratio_decision']['column']=='HOLD'
    assert r['ratio_decision']['proposal']=='μῆνα'


def test_d1_multicluster_requires_every_changed_cluster(monkeypatch):
    l=lex(**{'ἐστιν':100})
    class PerClusterShape(Shape):
        def predict(self,x):
            cls='psili' if x[0] else 'none'
            return cls,.999,{cls:.999}
    def ev(*a,**kw):
        return evidence(above=[blob()] if kw['core_x0']<20 else [])
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',ev)
    def run():return spell_ink_line('x',nfd('εστινͅ'),nfd('εστινͅ'),alignment('εστινͅ'),object(),l,PerClusterShape())[0]
    r=run()
    assert r['stage']=='D1' and r['decision']['column']=='ACCEPT' and len(r['cluster_checks'])==2
    def clipped(*a,**kw):
        e=ev(*a,**kw)
        if kw['core_x0']>=20:e.clipped_bottom=True
        return e
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',clipped)
    r=run()
    assert r['decision']['column']=='HOLD'
    assert any(not ck['accept'] and ck['reason']=='abstain:clipped_band' for ck in r['cluster_checks'])


def test_combined_breathing_grave_repair_cannot_hold_at_line_end(monkeypatch):
    # D1 owns the missing breathing, but its repair cannot bypass the slope-only grave rule.
    monkeypatch.setattr('greekocr.labelfix.spellink.mark_evidence',lambda *a,**k:evidence(above=[replace(blob(),faint=True)]))
    l=lex(**{'ἣ':50})
    r=spell_ink_line('x',nfd('ή'),nfd('ή'),alignment('ή'),object(),l,Shape('dasia+grave',.9))[0]
    assert r['stage']=='D1' and r['decision']['column'] is None
    r=spell_ink_line('x',nfd('ή'),nfd('ή'),alignment('ή'),object(),l,Shape('dasia+grave'),book_style='acute')[0]
    assert r['decision']['column'] is None and r['decision']['reason']=='abstain:book_prints_acute'
