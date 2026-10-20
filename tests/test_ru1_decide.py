import copy
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
from ru1_decide import decide, combine


def position(**kw):
    return dict(dict(row_id='row',source_id='row',offset=3,google='ь',kind='final',prior='unknown',control=False),**kw)


def reads(calls=('ъ','ъ'),gates=('VALID','VALID')):
    return [dict(reader=r,context=f'ctx01/{r}',gate_status=g,call=c) for r,c,g in zip(['r1','r2'],calls,gates)]


@pytest.mark.parametrize('calls,gates,expected',[
    (('ъ','ъ'),('VALID','VALID'),'edit_hard'),
    (('ъ','ъ'),('VALID','VOID'),'edit_hard'),
    (('ъ','ъ'),('VOID','VALID'),'edit_hard'),
    (('ъ','ъ'),('VOID','VOID'),'lead_review'),
    (('ъ','ь'),('VALID','VALID'),'lead_review'),
    (('u','ъ'),('VALID','VALID'),'lead_review'),
    (('ъ','other'),('VALID','VALID'),'lead_review'),
    (('ь','ь'),('VALID','VALID'),'keep_soft'),
])
def test_rule(calls,gates,expected):
    assert decide(position(),reads(calls,gates))['decision']==expected


@pytest.mark.parametrize('fields',[dict(google='ъ'),dict(kind='pre_hyphen'),dict(control=True)])
def test_never_edit_non_candidates(fields):
    assert decide(position(**fields),reads()) is None


@pytest.mark.parametrize('calls,prior',[(('ъ','ъ'),'ь_only'),(('ь','ь'),'ъ_only')])
def test_prior_disagreement(calls,prior):
    d=decide(position(prior=prior),reads(calls));assert d['decision']=='lead_review' and d['prior_disagreement']
    assert d['vote_decision'] in {'edit_hard','keep_soft'}


def test_missing_r2():
    d=decide(position(),reads()[:1]);assert d['decision']=='lead_review' and d['reads']['r2'] is None


def test_same_context_not_independent():
    v=reads();v[1]['context']=v[0]['context'];assert decide(position(),v)['decision']=='lead_review'


def test_join_by_row_offset_and_summary(tmp_path):
    a=tmp_path/'answers';a.mkdir()
    for n in range(1,5):
        for reader in ['r1', 'r3' if n == 4 else 'r2']:
            stem=f'ctx{n:02}'+('.'+reader if reader!='r1' else '')
            ps=[dict(position(row_id=f'row{n}',prior='ь_only'),item_id=f'{reader}-{n}',call='ъ',context_void=False,confidence='high')]
            (a/f'{stem}.mapped.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in ps))
            (a/f'{stem}.controls.json').write_text(json.dumps(dict(status='VALID')))
            (a/f'{stem}.scan.json').write_text(json.dumps(dict(ok=True)))
    s=combine(tmp_path);assert s['status']=='complete' and s['positions']==4
    assert s['prior_disagreement_count']==4 and len(s['prior_disagreements'])==4
    out=[json.loads(l) for l in (tmp_path/'decisions.jsonl').read_text().splitlines()]
    assert all(d['decision']=='lead_review' and d['reads'].get('r2', d['reads'].get('r3')) for d in out)
    (a/'ctx01.r2.scan.json').write_text('{"ok": false}')
    with pytest.raises(ValueError,match='unclean'):combine(tmp_path)
