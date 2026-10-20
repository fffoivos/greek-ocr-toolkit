"""LQB4 source and scope contracts, executable before DEV tier admission."""
import importlib.util
from pathlib import Path
from tests._paths import require_file
import sys
import pytest
from greekocr.labelfix import lqb
sys.path.insert(0,str(lqb.ROOT/'scripts/lqb'))
import build_v2_1 as v21

@pytest.fixture(scope='module')
def dev():return v21.dev_records({},None)

@pytest.fixture(scope='module')
def sub():return v21.substitution_records({})

def test_sx1_v2_verified_membership():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    xs,r=v21.verify_sx1({})
    assert r['verified'] and r['audit100_released']==r['audit100_total']==99
    assert len(xs)==101 and r['mode']=='ENSEMBLE_AB'


def test_dev_census_and_scope_binding(dev):
    rs,google,ids,n=dev
    assert len(rs)==21892 and n==976 and len(ids)==600 and len(google)==600
    assert len({r['line_id'] for r in rs})==391
    labels={r['line_id']:r['google_text'] for r in google}
    for r in rs:
        s=r['slot'];ctx=r['context']
        assert ctx['reference']==''.join(c[0] for c in lqb.letters(labels[r['line_id']]))
        assert lqb.error(r,labels[r['line_id']]) is not None
        assert r['target']==lqb.factors(lqb.letters(ctx['printed_word'])[s['letter']])[lqb.HEADS.index(s['head'])]


def test_dev_enriched_and_construction_exposure(dev):
    rs=dev[0]
    assert all(r['sample_type']=='enriched' and not r['population_eligible'] for r in rs)
    assert all(lqb.sample_used(r,'S8b') and not lqb.sample_used(r,'sf6_release') for r in rs)
    # Do not fabricate the model identities missing in the peer metadata.
    assert all('unspecified' in r['readers'][0] for r in rs)


def test_substitution_reviewed_heads_only(sub):
    rs,google,unknown,ids=sub
    assert len(ids)==60 and len(rs)==63 and len({r['line_id'] for r in rs})==57
    assert len(unknown)==3
    assert all(r['tier']=='A' and r['sample_type']=='decision_audit' and r['context']['reviewed_head_only'] for r in rs)
    assert not {r['line_id'] for r in rs}&{r['line_id'] for r in unknown}
    assert all(r['slot']['head']== 'dialytika' or r['slot']['head'] in ('accent','breathing') for r in rs)


def test_substitution_exact_owner_correction(sub):
    rs=[r for r in sub[0] if r['line_id']=='b963a5d59be557e9eef8498b-p000065-l0055']
    assert {r['slot']['head']:r['target'] for r in rs}=={'accent':1,'dialytika':1}


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@45a0a6441; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_new_exclusions_respect_all_classes_and_dev_ruling(dev,sub):
    new,info=v21.exclusions(dev[2]|sub[3],dev[2],{})
    assert len(new)==60 and set(new)==sub[3] and not set(new)&dev[2]
    assert info['dev_class']=='eval_only_dev' and info['dev_registry_sync_pending']==600


@pytest.mark.parametrize('text,expected',[('αἴ βότα γ',0),('αἴ βοτα γ',1),('x αἴ βότα γ',0)])
def test_scoped_marks_keep_marks_and_shift_with_line(text,expected):
    r=dict(line_id='x',slot=dict(kind='scoped_mark',start=2,end=6,letter=1,head='accent'),
           **{'class':'marks'},target=1,context=dict(reference='αιβοταγ',printed_word='βότα'))
    assert lqb.error(r,text)==(expected,1)


def test_frozen_v1_remains_intact():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    assert lqb.sha256(lqb.DEFAULT/'truth_v1.jsonl')=='9f31e392e51b2c1b39e6d7ae5d23f949f4580f1b0bbefdd4d2d6e158013dfbe4'
    assert lqb.sha256(lqb.DEFAULT/'truth_v1_flags.jsonl')=='945cb12e114fce3200d401935d5300ff11b1e1329862a2ef1c5ae7b38b4a0f59'
