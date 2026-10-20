"""LQB5 admission, saved weight custody, clustering and report contracts."""
from greekocr.ops.data_root import input_path as _data_input
from collections import defaultdict
import json
import sys
import numpy as np
import pytest
from tests._paths import require_file
from greekocr.labelfix import lqb
sys.path.insert(0,str(lqb.ROOT/'scripts/lqb'))
import build_v2_2 as v22

def read(n):return json.loads((_data_input(lqb.DEFAULT/n)).read_text())

@pytest.fixture(scope='module')
def truth():return list(lqb.rows(require_file(lqb.DEFAULT/'truth_v1_1.jsonl')))

@pytest.fixture(scope='module')
def dev(truth):return [r for r in truth if r['provenance']['set']=='S8_DEV']


def test_truth_freeze_and_admission(dev,truth):
    m=read('truth_v1_1.manifest.json')
    assert len(truth)==m['items']==61463 and len(dev)==21892
    assert lqb.sha256(lqb.DEFAULT/'truth_v1_1.jsonl')==m['sha256']
    assert (_data_input(lqb.DEFAULT/'truth_v1_1.sha256')).read_text().split()[0]==m['sha256']
    assert all(r['tier']=='A' and r['sample_type']=='weighted_stratified' for r in dev)
    assert m['dev']['controls']==dict(r1='82/84',r2='82/84',shared_misses=0)
    assert all('Opus' in r['readers'][0] for r in dev)
    assert all(lqb.sample_used(r,'S8b') and not lqb.sample_used(r,'sf6_release') for r in dev)


def test_saved_weights_and_exact_card_exclusions(dev):
    saved=list(lqb.rows(v22.prior.DEV/'evidence/dev_truth.jsonl.gz'))
    items=[r for r in saved if r.get('type')=='item' and not r.get('control')]
    resolved={r['id']:r for r in items if r['status']=='resolved'}
    assert len(resolved)==976
    assert sum(r['status']=='unadjudicated' for r in items)==671
    assert sum(r['status']=='UNKNOWN' for r in items)==2
    assert {r['context']['card_id'] for r in dev}=={k for k,r in resolved.items() if lqb.letters(r['truth'])}
    cards=list(lqb.rows(lqb.DEFAULT/'truth_v1_1_dev_cards.jsonl'))
    assert {r['id'] for r in cards}==resolved.keys()
    assert sum(not r['known_heads'] for r in cards)==8
    assert all(r['weight']==resolved[r['id']]['weight'] for r in cards)
    for r in dev:
        src=resolved[r['context']['card_id']]
        assert r['context']['card_weight']==src['weight']
        assert r['context']['wave']==src['wave']
        assert not r['population_eligible'] and r['weighted_population_eligible']


def test_weighted_ratio_and_bootstrap_hand_witness():
    es=[('a','d1',2,1,1),('a','d2',1,0,1),('b','d1',10,0,1)]
    x=v22.weighted(es,seed=12,replicates=4000)
    assert x['rate']==pytest.approx(2/13)
    # Independent explicit within-wave document resampling; b is fixed.
    rng=np.random.default_rng(12);draw=rng.integers(2,size=(4000,2))
    errors=2*(draw==0).sum(1);den=10+2*(draw==0).sum(1)+(draw==1).sum(1)
    assert x['ci95']==pytest.approx(np.quantile(errors/den,[.025,.975]))
    assert x['documents_by_wave']=={'a':2,'b':1}
    assert x['valid_replicates']==4000
    assert v22.weighted([])['rate'] is None


def test_independent_weighted_google_reaggregation(dev):
    reg=read('versions.json');pred=lqb.load_version('google_raw',reg,{r['line_id'] for r in dev})
    num=den=0
    for r in dev:
        e,n=lqb.error(r,pred[r['line_id']]);w=r['context']['card_weight'];num+=w*e;den+=w*n
    actual=read('score_v2.json')['weighted_dev']['google_raw']
    assert actual['weighted_errors']==pytest.approx(num)
    assert actual['weighted_opportunities']==pytest.approx(den)
    assert actual['rate']==pytest.approx(num/den)
    assert actual['valid_replicates']==4000


@pytest.mark.parametrize('kind',['word_letter','scoped_mark','letter_index'])
@pytest.mark.parametrize('printed,text,direction',[('ά','α','missing'),('α','ά','extra'),('ά','ὰ','wrong mark'),('ά','ά',None)])
def test_head_direction_actual_prediction(kind,printed,text,direction):
    slot=dict(kind=kind,head='accent',letter=0,word=0,start=0,end=1,index=0)
    r=dict(slot=slot,**{'class':'marks'},printed=printed,target=lqb.factors(printed)[1],context=dict(printed_word=printed,reference='α'))
    for d in ['missing','extra','wrong mark']:assert v22.direction_error(r,text,d)==int(d==direction)


def test_baseline_order_and_collapsed_gaps():
    base=read('baseline_v2.json');byclass=defaultdict(list)
    for r in base:byclass[r['class_name']].append(r)
    for cls,rs in byclass.items():
        gaps=[i for i,r in enumerate(rs) if r['status']!='measured']
        assert len(gaps)==1
        if gaps:assert gaps==[len(rs)-1] and rs[-1]['unmeasured_scopes']
    assert sum(r['status']=='measured' for r in base)==read('LQB5_RECEIPT.json')['baseline_measured_rows']
    directions=[r for r in base if r['status']=='measured' and r['metric'].split(' / ')[-1] in ('missing','extra','wrong mark')]
    assert {r['source_set'] for r in directions}=={'S8_DEV','audit100','substitution60'}
    c1=[r for r in base if r['source_set'].startswith('C1/') and r['metric'].startswith('marks (') and r['n']]
    assert c1 and all(r['marks_y']+r['marks_n']==r['n'] for r in c1)


def test_release_not_proposal_and_headline_coverage():
    reg=read('versions.json');release=lqb.load_version('sf6_release',reg)
    assert len(release)==99 and reg['versions']['sf6_release']['mode']=='ENSEMBLE_AB'
    h=read('headline_v2.json');p=h['by_source']['S8_DEV/weighted_stratified']
    assert p['status']=='not measured' and p['delta'] is None and p['ci95'] is None
    assert p['sf6_covered_lines']==2 and h['line'].startswith('DEV (weighted_stratified)')
    audit=h['by_source']['audit100/decision_audit']
    assert (audit['a_errors'],audit['b_errors'],audit['items'])==(87,16,2232)
    assert len(h['bottom_line'].split('. '))<=4 and h['bottom_line'].startswith('Marks change:')
    covered=p['covered_subset']
    assert covered['heads']==76 and not covered['population_estimate_eligible']
    assert covered['bootstrap']['valid_replicates']==4000
    assert covered['weighted_delta_ci95'][0]==covered['weighted_delta_ci95'][1]
    assert not read('score_v2.json')['weighted_dev']['sf6_release']['population_estimate_eligible']


def test_page_top_line_and_budget():
    require_file('docs/records/labelfix/lqb/scoreboard.html')
    p=lqb.DEFAULT/'scoreboard.html';s=_data_input(p).read_text()
    assert _data_input(p).stat().st_size<14_000_000
    assert s.index('id="bottom-line"')<s.index('id="baseline"')<s.index('id="headline"')
    assert 'Not measured — remaining scopes' in s
    assert 'weighted estimate' in s and '976 resolved' in s and '671 unread' in s
    assert 'LQB5_RECEIPT.json' in s
    assert read('score_v2.json')['truth_sha256']==read('truth_v1_1.manifest.json')['sha256']


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@45a0a6441; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_all_version_and_output_custody():
    r=read('LQB5_RECEIPT.json')
    for p,h in r['inputs'].items():assert lqb.sha256(p)==h,p
    for p,h in r['outputs'].items():assert lqb.sha256(lqb.DEFAULT/p)==h,p
    assert not any(r[k] for k in ['network','git_writes','peer_writes','browser_launched'])
    assert set(read('score_v2.json')['versions'])==set(read('versions.json')['versions'])
