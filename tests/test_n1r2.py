"""Offline N1-R2 policies, custody, sheet coverage and launcher dry run."""
from collections import Counter
import json
import os
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from n1_decide import decide, edit_rule, load_reads
from n1r2_prepare import PACK_ROOT, OUT, SCRATCH, rows, sha, build_context
from n1_pack_closure import scan
from n1_score import decode_and_gate
from n1_map_answers import map_answers

SLOT=dict(slot_id='s',line_id='l',document='doc',glyph='-',position='thousands',grammar_candidates=['thousands'],start=1,end=2)
def vote(reader='r1',meaning='raised dot',gate='VALID',status='ok'):
    return dict(reader=reader,meaning=meaning,context_status=gate,read_status=status)

@pytest.mark.parametrize('meaning',['raised dot','baseline dot','comma','hyphen or dash','space','nothing'])
def test_two_valid_agreeing_reads(meaning):
    result=decide(SLOT,[vote(meaning=meaning),vote('r2',meaning)])
    assert result['truth_candidate']==meaning
    assert result['status']==('lead_review' if meaning=='raised dot' else 'no_edit')
    assert result['apply_edit'] is False and result['edit'] is None

@pytest.mark.parametrize('gates',[('VALID','VOID'),('VOID','VALID'),('VOID','VOID'),('MISSING','VALID'),('VALID','INVALID')])
def test_void_is_never_primary_or_sufficient_second(gates):
    result=decide(SLOT,[vote(gate=gates[0]),vote('r2',gate=gates[1])])
    assert result['truth_candidate'] is None and result['edit_candidate'] is None
    assert result['status']=='lead_review'

@pytest.mark.parametrize('meanings',[('raised dot','baseline dot'),('unreadable','unreadable'),('other','other'),('nothing','space'),('other','raised dot')])
def test_disagreement_and_uncertain(meanings):
    result=decide(SLOT,[vote(meaning=meanings[0]),vote('r2',meanings[1])])
    assert result['status']=='lead_review' and result['truth_candidate'] is None

@pytest.mark.parametrize('glyph,position,meaning,expected',[
    ('-','thousands','raised dot',True),('.','thousands','raised dot',True),
    ('-','range','raised dot',False),('-','decimal','raised dot',False),
    (' -','thousands','raised dot',False),('–','thousands','raised dot',False),
    ('·','thousands','raised dot',False),(',','thousands','raised dot',False),
    ('.','thousands','baseline dot',False),('-','other','raised dot',False),
])
def test_n1_rule_exact_glyph_and_primary_grammar(glyph,position,meaning,expected):
    result=edit_rule(glyph,position,meaning)
    assert bool(result)==expected
    if result: assert result==dict(original=glyph,replacement='·')

def test_no_reads_single_read_and_duplicate_fail_closed():
    assert decide(SLOT,[])['status']=='lead_review'
    assert decide(SLOT,[vote()])['truth_candidate'] is None
    with pytest.raises(ValueError,match='duplicate reader'): decide(SLOT,[vote(),vote()])

def test_r2_mapper_and_gate_abstention():
    meanings=['raised dot','baseline dot','comma']; options=dict(zip('ABC',meanings))
    key=dict(readers={'r2':['a','b','c']},items={i:dict(slot_id=i,option_map=options,control_truth=truth,geometry={},google_glyph='-') for i,truth in zip('abc',meanings)})
    answers=[dict(item_id=i,answer=letter,confidence='high') for i,letter in zip('abc','ABC')]
    assert map_answers(key,answers)['context_status']=='VALID'
    assert decode_and_gate(key,answers)[0]['status']=='VALID'
    key['items']['a']['option_map']=dict(options,D='unreadable');answers[0]['answer']='D'
    gate,_=decode_and_gate(key,answers)
    assert gate['abstentions']==1 and gate['wrong']==0
    for bad in (answers[:-1],answers+[answers[0]],answers+[dict(item_id='alien')]):
        with pytest.raises(ValueError): decode_and_gate(key,bad)

def test_real_reverse_fresh_ids_permutations_controls_and_hashes():
    for items_path in sorted(PACK_ROOT.glob('ctx*/r*/items.jsonl')):
        for item in rows(items_path):
            for name in ('line', 'zoom'):
                required = items_path.parent / item[name]
                if not required.is_file():
                    pytest.skip(f'missing input: {required}')
    seen=[]; allids=set()
    for i in range(1,8):
        ctx=f'ctx{i:02}'; first=rows(PACK_ROOT/ctx/'r1/items.jsonl'); second=rows(PACK_ROOT/ctx/'r2/items.jsonl')
        keys=[json.loads((_data_input(OUT/'keys'/f'{ctx}{suffix}.json')).read_text()) for suffix in ('','.r2')]
        assert set(keys[0]['items']).isdisjoint(keys[1]['items'])
        assert [r['item_id'] for r in second]==keys[1]['readers']['r2']
        for a,b in zip(reversed(first),second):
            ka=keys[0]['items'][a['item_id']]; kb=keys[1]['items'][b['item_id']]
            assert ka['slot_id']==kb['slot_id'] and ka['control_truth']==kb['control_truth']
            assert {k:v for k,v in ka.items() if k!='option_map'}=={k:v for k,v in kb.items() if k!='option_map'}
            assert set(a['options'].values())==set(b['options'].values())
            assert all(a['options'][k]!=b['options'][k] for k in a['options'])
            for name in ('line','zoom'):
                assert a[name]==b[name]
                assert sha(PACK_ROOT/ctx/'r1'/a[name])==sha(PACK_ROOT/ctx/'r2'/b[name])
            if kb['control_truth'] is None: seen.append(kb['slot_id'])
        assert not allids&set(keys[1]['items']);allids.update(keys[1]['items'])
        for r in ('r1','r2'):
            manifest=PACK_ROOT/ctx/f'MANIFEST.{r}.json'; before=sha(manifest)
            result=scan(PACK_ROOT/ctx/r,OUT,completed=True)
            assert result['ok'],result['violations']
            assert sha(manifest)==before
    assert Counter(seen)==Counter(r['slot_id'] for r in rows(OUT/'step1_rendered_v3.jsonl'))

def test_prepare_no_overwrite():
    with pytest.raises(ValueError,match='overwrite'): build_context('ctx01')

def test_closure_rejects_tampered_options_and_extra_file(tmp_path):
    import shutil
    out=tmp_path/'data';(out/'keys').mkdir(parents=True)
    for r,suffix in [('r1',''),('r2','.r2')]:
        shutil.copytree(PACK_ROOT/'ctx01'/r,tmp_path/'ctx01'/r)
        shutil.copyfile(OUT/'keys'/f'ctx01{suffix}.json',out/'keys'/f'ctx01{suffix}.json')
        shutil.copyfile(PACK_ROOT/'ctx01'/f'MANIFEST.{r}.json',tmp_path/'ctx01'/f'MANIFEST.{r}.json')
    directory=tmp_path/'ctx01/r2'; (directory/'private.json').write_text('{}')
    assert not scan(directory,out,completed=True)['ok']
    (directory/'private.json').unlink()
    public=rows(directory/'items.jsonl'); public[0]['options']['A'],public[0]['options']['B']=public[0]['options']['B'],public[0]['options']['A']
    (directory/'items.jsonl').write_text('\n'.join(map(json.dumps,public)))
    result=scan(directory,out,completed=True)
    assert not result['ok'] and 'public/private option mismatch' in result['violations']

def test_r2_dry_run_all_contexts_without_real_probe_or_read():
    for i in range(1,8):
        ctx=f'ctx{i:02}'
        result=subprocess.run(['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1',ctx,'r2','--dry-run'],capture_output=True,text=True,
                              env=dict(os.environ,PATH=str(Path(sys.executable).parent)+':/usr/bin:/bin:/usr/sbin:/sbin'))
        assert result.returncode==0,result.stdout+result.stderr
        receipt=json.loads(result.stdout)
        assert receipt['dry_run'] and receipt['reader']=='r2'
        assert receipt['output_stem'].endswith(ctx+'.r2')
        assert not (OUT/'answers'/f'{ctx}.r2.jsonl').exists()

def test_real_decisions_pending_and_sheet_union():
    require_file('artifacts/n1/owner_sheet/cards.json')
    decisions=rows(OUT/'decisions.jsonl'); assert len(decisions)==558
    assert all(r['truth_candidate'] is None and r['edit'] is None and r['status']=='lead_review' for r in decisions)
    assert all(len(r['reads'])==2 for r in decisions)
    expected={r['slot_id'] for r in decisions if r['lead_pixel_check_required']}
    expected|={r['slot_id'] for r in json.loads((_data_input(OUT/'owner_sheet/cards.json')).read_text()) if r['group']=='Hyphen printed as raised dot'}
    index=json.loads((_data_input(SCRATCH/'n1_review/raised/sheets_index.json')).read_text()); cells=[c for s in index['sheets'] for c in s['cells']]
    assert len(cells)==len({r['slot_id'] for r in cells})==len(expected)
    assert {c['slot_id'] for c in cells}==expected
    assert any(a['context_status']=='VOID' for c in cells for a in c['reads'])
    for s in index['sheets']:
        assert s['total_cells']<=12 and len(s['references'])==4
        assert Counter(r['truth'] for r in s['references'])=={'raised dot':2,'baseline dot':2}
        assert sha(SCRATCH/'n1_review/raised'/s['file'])==s['sha256']
    assert index['reference_limitation'] and not index['complete_same_document_references']
    assert (_data_input(OUT/'lead_raised_template.jsonl')).read_bytes()==b''


def test_r2_launcher_fake_execution_and_output_names(tmp_path):
    from test_n1cd import fake_setup
    data,rd,ctx,env=fake_setup(tmp_path,root='n1')
    second=rd.with_name('r2');rd.rename(second)
    kp=data/'keys'/f'{ctx}.json'; key=json.loads(_data_input(kp).read_text())
    key['readers']={'r2':key['readers']['r1']}
    (data/'keys'/f'{ctx}.r2.json').write_text(json.dumps(key))
    (second.parent/'MANIFEST.r1.json').rename(second.parent/'MANIFEST.r2.json')
    result=subprocess.run(['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1',ctx,'r2'],env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    assert (data/'answers/n1'/f'{ctx}.r2.mapped.json').exists()
    assert not list((data/'answers').glob(f'{ctx}.r1.*'))
    assert json.loads((_data_input(data/'usage_ledger.json')).read_text())[0]['reader']=='r2'


def test_loader_r2_gate_and_malformed_context_fail_closed(tmp_path):
    import shutil
    out=tmp_path/'data';(out/'keys').mkdir(parents=True);(out/'answers').mkdir()
    for p in (OUT/'keys').glob('ctx*.json'): shutil.copyfile(p,out/'keys'/p.name)
    for p in (OUT/'answers').glob('ctx*.r1.*'): shutil.copyfile(p,out/'answers'/p.name)
    first,gates=load_reads(out)
    for i in range(1,8):
        ctx=f'ctx{i:02}'; key=json.loads((_data_input(out/'keys'/f'{ctx}.r2.json')).read_text()); answers=[]
        for iid,item in key['items'].items():
            meaning=item['control_truth'] or first[item['slot_id']][0]['meaning']
            letter=next(k for k,v in item['option_map'].items() if v==meaning)
            answers.append(dict(item_id=iid,answer=letter,confidence='high'))
        (out/'answers'/f'{ctx}.r2.jsonl').write_text('\n'.join(map(json.dumps,answers))+'\n')
        (out/'answers'/f'{ctx}.r2.scan.json').write_text(json.dumps(dict(ok=True,scanner_version=4)))
        (out/'answers'/f'{ctx}.r2.run.json').write_text(json.dumps(dict(rc=0,model='gpt-6.1-sol')))
    reads,gates=load_reads(out)
    assert all(gates[f'ctx{i:02}.r2']['status']=='VALID' for i in range(1,8))
    assert all(len(v)==2 for v in reads.values())
    frame={r['slot_id']:r for r in rows(OUT/'frame_step1.jsonl') if r['partition']=='step1'}
    results=[decide(frame[sid],votes) for sid,votes in reads.items()]
    assert any(r['truth_candidate']=='raised dot' and r['edit_candidate'] for r in results)
    assert all(r['truth_candidate'] is None for r in results if r['reads'][0]['context_status']=='VOID')
    path=out/'answers/ctx01.r2.jsonl'; path.write_text(_data_input(path).read_text().splitlines()[0]+'\n')
    reads,gates=load_reads(out)
    assert gates['ctx01.r2']['status']=='INVALID'
    assert all(decide(frame[sid],v)['truth_candidate'] is None for sid,v in reads.items() if v[1]['context']=='ctx01')
