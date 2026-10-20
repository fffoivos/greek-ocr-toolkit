"""Replacement safety fixtures: no real reader, account probes, or network."""
import json
from pathlib import Path
import sys
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/numerics'),str(ROOT/'scripts/secondary/reading')]
import n1w1 as m
import n1w1_r3 as repl
import n1w1_r3_driver as driver
import n1w1_r3_finalize as final


def setup_driver(tmp_path):
    art=tmp_path/'art';art.mkdir();pack=tmp_path/'pack'
    (pack/'ctx01/r3').mkdir(parents=True)
    return art,pack,dict(replacements=[dict(context='ctx01',reader='r3',items=86)])


def test_dry_run_never_probes_or_reads(tmp_path):
    art,pack,info=setup_driver(tmp_path)
    with patch.object(repl,'validate',return_value=info):
        assert driver.drive(art,pack,True,runner=lambda *a,**k:pytest.fail('read'),prober=lambda *a,**k:pytest.fail('probe'))==0
    assert not (art/'answers').exists()


def test_70_before_context_stops_permanently(tmp_path):
    art,pack,info=setup_driver(tmp_path);probes=[]
    def probe(*a,**k):probes.append(a);return 'primary=70%/10080m'
    with patch.object(repl,'validate',return_value=info):
        for _ in range(2):driver.drive(art,pack,runner=lambda *a,**k:pytest.fail('read'),prober=probe)
    assert len(probes)==1
    assert json.loads((art/'STOPPED_AT_70.json').read_text())['threshold']==70


def test_attempt_claim_survives_crash_and_never_reruns(tmp_path):
    art,pack,info=setup_driver(tmp_path);calls=[];probes=[]
    def run(*a,**k):calls.append(a);raise OSError('fixture crash')
    def probe(*a,**k):probes.append(a);return 'primary=10%/10080m'
    with patch.object(repl,'validate',return_value=info):
        for _ in range(2):driver.drive(art,pack,runner=run,prober=probe)
    assert len(calls)==1 and len(probes)==2
    assert json.loads((art/'answers/ctx01.r3.attempt.json').read_text())['status']=='FAILED'


def vote(sid,status='VALID',view='ok',reader='r2'):
    return dict(slot_id=sid,reader=reader,context_status=status,read_status=view,control=False,meaning='raised dot')


def test_partial_route_preserves_valid_original_vote():
    original=[vote('viewed'),vote('gap',view='unviewed')];fresh=[vote('gap')]
    out=final.route_votes(original,fresh,dict(slot_ids=['gap'],replaces='r2'))
    assert out==[original[0],fresh[0]]
    assert m.combine(dict(slot_id='gap',line_id='x',start=1,end=2,glyph='.',geometry={'geom_status':'ok'},grammar_candidates=['thousands']),[vote('gap',reader='r1'),out[1]])['agreed_raised']


def test_cannot_replace_valid_evidence():
    with pytest.raises(ValueError,match='valid viewed'):
        final.route_votes([vote('x')],[vote('x')],dict(slot_ids=['x'],replaces='r2'))


@pytest.mark.parametrize('fresh',[[],[vote('x'),vote('x')],[vote('x',reader='r1')]])
def test_bad_route_is_rejected(fresh):
    with pytest.raises(ValueError):final.route_votes([vote('x',status='VOID')],fresh,dict(slot_ids=['x'],replaces='r2'))


@pytest.mark.skip(reason="historical binding; last executed green not on record; producing-phase anchor 686ec7de7; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_ready_artifacts_are_complete():
    info=repl.validate();assert info['replacement_contexts']==16 and info['parent_contexts']==11
    assert sum(r['bed'] for r in info['replacements'])==info['bed_positions']
    assert final.finalize(dry_run=True)['positions']==info['bed_positions']
    original=m.rows(m.ART/'decisions.jsonl')
    missing={(d['slot_id'],v['reader']) for d in original for v in d['reads'] if v['context_status']!='VALID' or v['read_status']!='ok'}
    routed={(s,r['replaces']) for r in info['replacements'] for s in r['slot_ids']}
    assert missing==routed
    assert not (repl.R3/'answers').exists()
    index=json.loads((m.REVIEW/'sheets/index.json').read_text())
    assert [len(s['cells']) for s in index['sheets']]==[6,6,6,4]
    assert {c['slot_id'] for s in index['sheets'] for c in s['cells']}=={d['slot_id'] for d in original if d['agreed_raised']}
    for s in index['sheets']:
        assert len(s['references'])==4 and m.sha(s['sheet'])==s['sha256']

# Synthetic rollout fixture only; never starts a reader.
from test_n1w1 import sealed


def test_replacement_collect_keeps_physical_and_logical_identity(sealed,tmp_path):
    import shutil
    art,pack=sealed;rep=tmp_path/'replacement';rep.mkdir()
    shutil.copytree(pack/'ctx01/r1',pack/'ctx01/r3')
    manifest=json.loads((pack/'ctx01/MANIFEST.r1.json').read_text());manifest['reader']='r3'
    m.dump(pack/'ctx01/MANIFEST.r3.json',manifest)
    key=json.loads((art/'keys/ctx01.json').read_text());key['readers']={'r3':key['readers']['r1']}
    m.dump(rep/'keys/ctx01.r3.json',key)
    run=json.loads((art/'answers/ctx01.r1.run.json').read_text())
    records=m.rows(run['rollout']);records[0]['payload']['reader']='r3'
    roll=tmp_path/'r3.rollout.jsonl';m.jsonl(roll,records);run['rollout']=str(roll)
    m.dump(rep/'answers/ctx01.r3.run.json',run)
    vv,ev=final.collect_replacement('ctx01','r3','r2',set(),rep,pack)
    assert ev['gate']['status']=='VALID'
    assert all(v['reader']=='r2' and v['physical_reader']=='r3' and v['context']=='ctx01/r3' for v in vv)
    with pytest.raises(ValueError,match='reused'):
        final.collect_replacement('ctx01','r3','r2',{m.sha(run['rollout'])},rep,pack)
