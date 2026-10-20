"""Synthetic amendment tests; no claim of real SF7 qualification."""
import json
from pathlib import Path
import sys
import pytest
D=Path(__file__).resolve().parent
P=D/'package/projects/greek-ocr-toolkit-pipe032'
sys.path.insert(0,str(P));sys.path.insert(0,str(P/'tests'))
from test_line_pipeline import row,answer,engine,expected
from greekocr.harvest.line_pipeline import validate_result,span_edits
from test_line_pipeline import VERSIONS

def kept(r,t):
    x=answer(r,t,status='kept_unverified');x['evidence']={'kept_unverified':True,'reason':'SF7 could not verify'};return x

def test_kept_unverified_admits_raw():
    r=row();d=engine(corrector=lambda r,t,e:kept(r,t)).evaluate(r)
    assert d['disposition']=='ADMIT' and d['final_text']==r['raw_text'] and d['edits']==[]
    assert d['routes']['polytonic']['evidence']=={'kept_unverified':True,'reason':'SF7 could not verify'}

def test_kept_unverified_edits_rejected():
    r=row();a=kept(r,'polytonic');a['edits']=span_edits(r['raw_text'],r['raw_text']+' α')
    with pytest.raises(ValueError,match='non-applied'):validate_result(a,r,'polytonic',VERSIONS)

def test_kept_unverified_cyrillic_rejected():
    r=row();a=kept(r,'cyrillic')
    with pytest.raises(ValueError,match='only for polytonic'):validate_result(a,r,'cyrillic',VERSIONS)

@pytest.mark.parametrize('evidence',[{}, {'kept_unverified':True}, {'kept_unverified':True,'reason':''},{'kept_unverified':True,'reason':'   '},{'kept_unverified':False,'reason':'why'},{'reason':'why'},None,{'kept_unverified':True,'reason':7}])
def test_evidence_rejected(evidence):
    r=row();a=kept(r,'polytonic');a['evidence']=evidence
    with pytest.raises(ValueError,match='evidence flag'):validate_result(a,r,'polytonic',VERSIONS)

@pytest.mark.parametrize('status',['required_evidence_unresolved','failed','proposal_only'])
def test_unresolved_still_holds(status):
    d=engine(corrector=lambda r,t,e:answer(r,t,status=status)).evaluate(row())
    assert d['disposition']=='HOLD'
    assert any(r['reason']=='correction_unresolved' for r in d['reasons'])

def test_missing_still_holds():
    assert engine(corrector=lambda *a:None).evaluate(row())['disposition']=='HOLD'

@pytest.mark.parametrize('target',[None,'λόγος καὶ γραμμάτια'])
def test_existing_success_unchanged(target):
    r=row();d=engine(corrector=lambda r,t,e:answer(r,t,target)).evaluate(r)
    assert d['disposition']=='ADMIT' and d['final_text']==(target or r['raw_text'])
    assert d['routes']['polytonic']['status']==('applied' if target else 'verified_no_change')

def test_other_edits_and_normalization_unchanged():
    r=row('λόγος будуть 1.234 - γράμματα')
    declaration=expected(scripts=['greek','cyrillic'],languages=['Greek','Russian'],orthography='polytonic',orthographies={'cyrillic':'historical_russian'})
    def correct(r,t,e):
        if t=='polytonic':return kept(r,t)
        if t=='cyrillic':return answer(r,t,r['raw_text'].replace('будуть','будутъ'))
        if t=='numerics':return answer(r,t,r['raw_text'].replace('1.234','1·234'))
    d=engine(declaration,correct).evaluate(r)
    assert d['disposition']=='ADMIT' and d['final_text']=='λόγος будутъ 1·234 - γράμματα'
    assert all('polytonic' not in e['tools'] for e in d['edits'])

def test_sf7_head_sample(tmp_path):
    import os
    from bind_sf7 import load_and_validate, pairs
    config=json.loads((D/'census06_config.json').read_text())
    from binding_state import pending
    if pending(config):pytest.skip('PENDING: coordinator has not supplied full per-parent SF7 files and SHA256 values')
    baseline=Path(os.environ.get('CENSUS06_REAL_BASELINE','/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/attempts/full-split-001'))
    bindings=[r for r in config['corrections'] if r['tool']=='polytonic']
    args=[x for r in bindings for x in (r['path'],r['sha256'])]
    result,_=load_and_validate(pairs(args),config,baseline,tmp_path/'head',head=int(os.environ.get('CENSUS06_HEAD_N','20')),require_complete=False)
    assert len(result['parents'])==len(config['parents'])
