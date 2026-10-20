"""Offline pack custody and launcher integration with executable fake readers only."""
import base64
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from n1_calibration import score
from n1_map_answers import map_answers
D=ROOT/'artifacts/n1'
BASE=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs')

def rows(p): return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def test_sealed_controls():
    approved=rows(D/'controls/approved.jsonl')
    assert len(approved)==len({r['slot_id'] for r in approved})==82
    assert Counter(r['truth'] for r in approved)=={'baseline dot':21,'comma':23,'hyphen or dash':27,'nothing':7,'raised dot':4}
    assert all('C1 evidence lines' in r['approval_provenance']['c1_document_ruling'] for r in approved)
    assert all(r['approval_cell_number']<101 for r in approved)
    assert not {r['line_id'] for r in approved}&{r['line_id'] for r in rows(D/'frame_step1.jsonl') if r['partition']=='step1'}


def test_real_pack_coverage_and_v3_images():
    for manifest_path in sorted(BASE.glob('n1*/**/MANIFEST.r1.json')):
        manifest = json.loads(manifest_path.read_text())
        for name in sorted(manifest['files']):
            required = manifest_path.parent / 'r1' / name
            if not required.is_file():
                pytest.skip(f'missing input: {required}')
    approved=rows(D/'controls/approved.jsonl'); bed=rows(D/'step1_rendered_v3.jsonl')
    records={r['slot_id']:r for r in bed+approved}; seen=[]
    for root,contexts in [('n1',[f'ctx{i:02}' for i in range(1,8)]),('n1cal',['cal01'])]:
        for ctx in contexts:
            key=json.loads((D/'keys'/f'{ctx}.json').read_text()); rd=BASE/root/ctx/'r1'
            items=rows(rd/'items.jsonl'); assert len(items)<=100
            assert [i['item_id'] for i in items]==key['readers']['r1']
            controls=[v for v in key['items'].values() if v['control_truth'] is not None]
            assert len({v['slot_id'] for v in key['items'].values()})==len(items)
            if root=='n1':
                assert len(controls)==9
                assert Counter(v['control_truth'] for v in controls)['raised dot']>=1
                seen.extend(v['slot_id'] for v in key['items'].values() if v['control_truth'] is None)
            else: assert {v['slot_id'] for v in controls}=={r['slot_id'] for r in approved}
            manifest=json.loads((rd.parent/'MANIFEST.r1.json').read_text())
            actual={str(p.relative_to(rd)) for p in rd.rglob('*') if p.is_file()}
            assert set(manifest['files'])<=actual
            assert all(rel=='answers.jsonl' or rel.startswith('zoom/') for rel in actual-set(manifest['files']))
            for rel,h in manifest['files'].items(): assert digest(rd/rel)==h
            for item in items:
                assert set(item)=={'item_id','line','zoom','options'}
                private=key['items'][item['item_id']]; source=records[private['slot_id']]
                for name in ('line','zoom'): assert digest(rd/item[name])==source[name+'_sha256']
    assert len(seen)==558 and Counter(seen)==Counter(r['slot_id'] for r in bed)


def fake_setup(tmp_path, mode='good', root='n1cal'):
    ctx='cal01' if root=='n1cal' else 'ctx01'
    data=tmp_path/'data'; (data/'keys').mkdir(parents=True); (data/'controls').mkdir()
    rd=tmp_path/'packs'/root/ctx/'r1'; (rd/'img').mkdir(parents=True)
    public=[]; private={}
    for i,truth in enumerate(['comma','raised dot']):
        item=f'k{i:010x}'; public.append(dict(item_id=item,line='img/a.png',zoom='img/a.png',options={'A':truth,'B':'nothing'}))
        private[item]=dict(slot_id=f's{i}',option_map=public[-1]['options'],control_truth=truth,geometry={},google_glyph='.')
    key=dict(readers={'r1':[r['item_id'] for r in public]},items=private,calibration=root=='n1cal')
    (data/'keys'/f'{ctx}.json').write_text(json.dumps(key))
    (data/'controls/approved.jsonl').write_text('\n'.join(json.dumps(dict(slot_id=v['slot_id'],truth=v['control_truth'])) for v in private.values()))
    (rd/'items.jsonl').write_text('\n'.join(map(json.dumps,public))+'\n')
    (rd/'img/a.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1cAAAAASUVORK5CYII='))
    files={str(p.relative_to(rd)):digest(p) for p in rd.rglob('*') if p.is_file()}
    (rd.parent/'MANIFEST.r1.json').write_text(json.dumps(dict(files=files)))
    probe=tmp_path/'probe.sh'; probe.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
with (Path(os.environ['N1_TEST_DATA'])/'probes').open('a') as f:f.write(sys.argv[1]+'\\n')
phase=sys.argv[1].split(':')[0]; mode=os.environ['FAKE_MODE']
value=78 if mode=='high_'+phase else 10
print(f'limit_id=codex primary={value}%/10080m secondary=0%/300m')
'''); probe.chmod(0o755)
    reader=tmp_path/'run_read.sh'; reader.write_text('''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
label,folder,prompt,effort=sys.argv[1:]; assert effort=='medium'; assert Path(prompt).name=='sep.md'
rd=Path(folder); mode=os.environ['FAKE_MODE']; data=Path(os.environ['N1_TEST_DATA'])
(data/'reader_called').write_text('fake only')
items=[json.loads(l) for l in (rd/'items.jsonl').read_text().splitlines()]
answers=[dict(item_id=r['item_id'],answer='A') for r in items]
if mode=='wrong': answers[0]['answer']='B'
if mode=='missing': answers=answers[:1]
(rd/'answers.jsonl').write_text('\\n'.join(map(json.dumps,answers))+'\\n')
roll=data/'fake_rollout.jsonl'
roll.write_text(json.dumps({'payload':{'type':'function_call','name':'exec_command','arguments':json.dumps({'cmd':'cat /outside/key.json'})}})+'\\n' if mode=='leak' else '')
print(json.dumps(dict(label=label,rc=1 if mode=='reader_fail' else 0,wall_s=1,model='gpt-6.1-sol',rollout=str(roll),usage={k:1 for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens']},tool_calls={})))
'''); reader.chmod(0o755)
    env=dict(os.environ,N1_TEST_MODE='1',N1_TEST_DATA=str(data),N1_TEST_PACKS=str(tmp_path/'packs'),N1_TEST_READER=str(reader),N1_TEST_PROBE=str(probe),FAKE_MODE=mode)
    return data,rd,ctx,env


def launch(ctx,env,root='n1cal'):
    return subprocess.run(['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),root,ctx],env=env,capture_output=True,text=True)


@pytest.mark.parametrize('root',['n1cal','n1'])
def test_launcher_fake_success_and_no_overwrite(tmp_path,root):
    data,rd,ctx,env=fake_setup(tmp_path,root=root)
    result=launch(ctx,env,root); assert result.returncode==0,result.stdout+result.stderr
    assert len((data/'probes').read_text().splitlines())==2
    entry=json.loads((data/'usage_ledger.json').read_text())[0]; assert entry['bed']==root+'/'+ctx
    assert entry['launcher_status']=='VALID'
    assert json.loads((data/'answers'/root/f'{ctx}.r1.scan.json').read_text())['scanner_version']=='v4.4-canonical'
    if root=='n1cal':
        scoring=json.loads((data/'answers/n1cal/cal01.r1.calibration.json').read_text())
        assert scoring['correct']==2 and scoring['disagreements']==[]
    assert launch(ctx,env,root).returncode==2
    assert len((data/'probes').read_text().splitlines())==2


@pytest.mark.parametrize('mode',['high_before','high_after','leak','reader_fail','missing'])
def test_launcher_refuses_and_probes_after_attempt(tmp_path,mode):
    data,rd,ctx,env=fake_setup(tmp_path,mode)
    result=launch(ctx,env); assert result.returncode==2,result.stdout+result.stderr
    if mode=='high_before':
        assert not (data/'reader_called').exists() and not (data/'usage_ledger.json').exists()
        assert len((data/'probes').read_text().splitlines())==1
    else:
        assert len((data/'probes').read_text().splitlines())==2
        entries=json.loads((data/'usage_ledger.json').read_text()); assert len(entries)==1
        assert entries[0]['launcher_status']=='FAILED'
    if mode=='leak': assert not (data/'answers/n1cal/cal01.r1.mapped.json').exists()


def test_calibration_disagreements_and_missing(tmp_path):
    data,rd,ctx,env=fake_setup(tmp_path,'wrong')
    result=launch(ctx,env); assert result.returncode==0,result.stderr
    scoring=json.loads((data/'answers/n1cal/cal01.r1.calibration.json').read_text())
    assert scoring['per_class']['comma']==dict(total=1,correct=0,accuracy=0)
    assert scoring['confusion_matrix']['comma']['nothing']==1
    assert scoring['disagreements'][0]['slot_id']=='s0'
    key=json.loads((data/'keys/cal01.json').read_text()); approved=rows(data/'controls/approved.jsonl')
    missing=score(key,map_answers(key,[]),approved)
    assert missing['confusion_matrix']['comma']['<missing>']==1
    approved.pop()
    with pytest.raises(ValueError,match='every sealed control'): score(key,map_answers(key,[]),approved)


def test_launcher_shell_syntax():
    subprocess.run(['bash','-n',str(ROOT/'scripts/secondary/reading/run_n1.sh')],check=True)


def test_reused_helpers_redirect_logs_without_disk_edits(tmp_path):
    sys.path.insert(0,str(ROOT/'scripts/secondary/reading'))
    from n1_launch import reading_command, HERE
    for name in ('run_read.sh','limit_probe.sh'):
        script=HERE/name; before=script.read_bytes()
        cmd=reading_command(script,['fixture'],tmp_path/'logs with spaces')
        assert cmd[:2]==['bash','-c'] and cmd[3]==str(script)
        assert '$W/artifacts/ru1' not in cmd[2]
        subprocess.run(['bash','-n','-c',cmd[2]],check=True)
        assert script.read_bytes()==before
        assert 'gpt-6.1-sol' in cmd[2] and 'network_access=false' in cmd[2]
        assert 'web_search="disabled"' in cmd[2]
