"""Offline checks only. All launcher executions use fake probes and readers."""
import json,os,shutil,subprocess,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import HERE,PACK_ROOT,CANONICAL,REFERENCE,rows,sha,dump,jsonl
from repack_config import REPLACEMENTS
from closure import check
from tools.scan_rollout import integrity
from score import score,metric,render,map_records
PAIRS=list(REPLACEMENTS.items())

def key(bed):return json.loads((HERE/'keys'/(bed+'.json')).read_text())

@pytest.mark.parametrize('old,new',PAIRS)
def test_repack_closure(old,new):
 bed,ctx=new
 result=check(bed,ctx,write=False)
 assert result['ok'],result['violations']
 assert integrity(PACK_ROOT/bed/ctx)==([],False)
 assert not (PACK_ROOT/bed/ctx/'answers.jsonl').exists()
 assert {p.name for p in (PACK_ROOT/bed/ctx).iterdir()}=={'cards.jsonl','crops'}

@pytest.mark.parametrize('old,new',PAIRS)
def test_same_cards_and_pixels(old,new):
 oldbed,ctx=old;bed,_=new;ok=key(oldbed);nk=key(bed)
 original=rows(PACK_ROOT/oldbed/ctx/'cards.jsonl');fresh=rows(PACK_ROOT/bed/ctx/'cards.jsonl')
 oldbyline={ok['items'][c['card_id']]['line_id']:c for c in original}
 assert len(fresh)==55
 for c in fresh:
  meta=nk['items'][c['card_id']];before=oldbyline[meta['line_id']]
  assert {k:v for k,v in c.items() if k!='card_id'}=={k:v for k,v in before.items() if k!='card_id'}
  assert sha(PACK_ROOT/oldbed/ctx/before['crop'])==sha(PACK_ROOT/bed/ctx/c['crop'])==meta['crop_sha256']
  assert (PACK_ROOT/bed/ctx/c['crop']).stat().st_nlink==1
 assert set(oldbyline)=={nk['items'][c['card_id']]['line_id'] for c in fresh}

@pytest.mark.parametrize('old,new',PAIRS)
def test_fresh_ids(old,new):
 originalids={c['card_id'] for bed,ctx in REPLACEMENTS for c in rows(PACK_ROOT/bed/ctx/'cards.jsonl')}
 allfresh=[c['card_id'] for bed,ctx in REPLACEMENTS.values() for c in rows(PACK_ROOT/bed/ctx/'cards.jsonl')]
 assert len(allfresh)==len(set(allfresh))==220
 assert not originalids&set(allfresh)
 # Existing nonreplacement packs also have no colliding fresh id.
 for path in PACK_ROOT.glob('*/*/cards.jsonl'):
  if (path.parent.parent.name,path.parent.name) not in REPLACEMENTS.values():
   assert not {c['card_id'] for c in rows(path)}&set(allfresh)

@pytest.mark.parametrize('old,new',PAIRS)
def test_controls_shifted_and_keys_outside(old,new):
 oldbed,ctx=old;bed,_=new;ok=key(oldbed);nk=key(bed)
 def positions(b,k):return {k['items'][c['card_id']]['line_id']:i for i,c in enumerate(rows(PACK_ROOT/b/ctx/'cards.jsonl')) if k['items'][c['card_id']]['control']}
 a,b=positions(oldbed,ok),positions(bed,nk)
 assert set(a)==set(b) and len(a)==5
 assert all(a[i]!=b[i] for i in a)
 assert not (HERE/'keys').is_relative_to(PACK_ROOT)
 assert not list((PACK_ROOT/bed/ctx).rglob('*key*'))


def test_scanner_and_protocol_unchanged():
 assert sha(HERE/'tools/scan_rollout.py')==sha(REFERENCE/'tools/scan_rollout.py')==CANONICAL
 assert sha(HERE/'tools/replay_literal.py')==sha(REFERENCE/'tools/replay_literal.py')
 assert (HERE/'prompts/bsb.md').read_bytes()==(REFERENCE/'prompts/bsb.md').read_bytes()
 text=(HERE/'launchers/run_bed.sh').read_text()
 assert '"$PY" -B "$SCAN" "$ROLL" "$RD"' in text
 assert 'cat "$D/prompts/path_addendum.md" >> "$P"' in text
 assert text.index('cat "$D/prompts/path_addendum.md"')<text.index('RUN=$("$S/run_read.sh"')
 assert (HERE/'prompts/path_addendum.md').read_text().startswith('\n# Tool-use addendum')


def fake_launcher(tmp_path,mode):
 root=tmp_path/'task';(root/'launchers').mkdir(parents=True)
 (root/'runtime.py').write_text('import sys\nsys.path.insert(0,'+repr(str(HERE))+')\nfrom runtime import limit\nlimit(sys.argv[2])\n')
 calls=tmp_path/'calls'
 probe=root/'launchers/limit_probe.sh'
 value='78' if mode=='stop' else '77.9'
 body='echo "limit_id=codex primary='+value+'%/10080m"'
 if mode=='missing':body='echo NONE'
 if mode=='ambiguous':body='echo "primary=1%/10080m secondary=2%/10080m"'
 if mode=='between':body='if [ -e "'+str(calls)+'" ]; then echo "primary=78%/10080m"; else echo "primary=77%/10080m"; fi'
 probe.write_text('#!/bin/bash\n'+body+'\n');probe.chmod(0o755)
 reader=root/'launchers/run_bed.sh';reader.write_text('#!/bin/bash\necho "$*" >> "'+str(calls)+'"\n'+('exit 2\n' if mode=='reader_fail' else ''));reader.chmod(0o755)
 script=(HERE/'launch_repack.sh').read_text().replace(str(HERE),str(root));path=tmp_path/'launch.sh';path.write_text(script)
 run=subprocess.run(['bash',str(path)],capture_output=True,text=True)
 return run,calls.read_text().splitlines() if calls.exists() else []

@pytest.mark.parametrize('mode,count,rc',[('ok',4,0),('stop',0,8),('missing',0,8),('ambiguous',0,8),('between',1,8),('reader_fail',1,2)])
def test_launcher_sequential_stops(tmp_path,mode,count,rc):
 r,calls=fake_launcher(tmp_path,mode)
 assert r.returncode==rc,(r.stdout,r.stderr)
 assert calls==[' '.join(x) for x in REPLACEMENTS.values()][:count]

@pytest.mark.parametrize('bed,ctx',list(REPLACEMENTS.values()))
def test_refuse_rerun_guard(tmp_path,bed,ctx):
 rd=tmp_path/'pack'/bed/ctx;rd.mkdir(parents=True);(rd/'cards.jsonl').write_text('');(rd/'answers.jsonl').write_text('')
 source=(HERE/'launchers/run_bed.sh').read_text().replace(str(PACK_ROOT),str(tmp_path/'pack'))
 path=tmp_path/'run_bed.sh';path.write_text(source)
 result=subprocess.run(['bash',str(path),bed,ctx],capture_output=True,text=True)
 assert result.returncode==8 and 'Refuse rerun' in result.stdout


def test_settings():
 text=(HERE/'launchers/run_read.sh').read_text()
 for token in ['MODEL=gpt-6.1-sol','sandbox_workspace_write.network_access=false','web_search="disabled"','features.multi_agent=false','features.remote_plugin=false','features.apps=false']:assert token in text
 assert '"$P" medium' in (HERE/'launchers/run_bed.sh').read_text()
 assert (HERE/'launch_repack.sh').read_text().count('\nrun_one ')==4


def test_partial_counts_and_void_exclusion():
 r=score();assert r['partial'] and r['included_contexts']==12
 assert [x['n'] for x in r['strata']]==[100,100,100,0,50,100,100,50]
 assert [x['letters']['yes'] for x in r['strata']]==[92,99,93,0,50,96,99,49]
 assert [x['crop_ok']['yes'] for x in r['strata']]==[94,89,88,0,45,98,99,42]
 assert sum(x['controls']['n'] for x in r['strata'])==60
 assert sum(x['controls']['errors'] for x in r['strata'])==1
 assert [x['verdict'] for x in r['strata']]==['PASS','FAIL','FAIL','PENDING','PENDING','PASS','PASS','PENDING']
 assert all(c['selected_context'] not in [b+'/'+ctx for b,ctx in REPLACEMENTS] for c in r['contexts'])


def test_reproducibility(tmp_path):
 for name in ('a','b'):
  p=tmp_path/name;p.mkdir()
  result=subprocess.run([sys.executable,'-B',str(HERE/'score.py'),'--output-dir',str(p)],capture_output=True,text=True)
  assert result.returncode==0,result.stderr
 for f in ('W2C1_RESULTS.md','W2C1_RESULTS.json'):
  assert (tmp_path/'a'/f).read_bytes()==(tmp_path/'b'/f).read_bytes()==(HERE/f).read_bytes()


def test_unknown_denominator():
 assert metric([{'letters':'y'},{'letters':'n'},{'letters':'u'}],'letters')==dict(n=3,yes=1,counts={'n':1,'u':1,'y':1},rate=1/3)
 assert metric([],'crop_ok')['rate'] is None

@pytest.fixture
def completed(tmp_path):
 root=tmp_path/'fixture';root.mkdir()
 for sub in ('receipts','scan','answers'):shutil.copytree(HERE/sub,root/sub)
 for path in (HERE/'keys').glob('*.json'):
  dest=root/'keys'/path.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(path,dest)
 for path in (HERE/'keys').glob('*/draw.jsonl'):
  dest=root/'keys'/path.parent.name/path.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(path,dest)
 (root/'tools').mkdir();shutil.copyfile(HERE/'tools/scan_rollout.py',root/'tools/scan_rollout.py')
 for bed,ctx in REPLACEMENTS.values():
  k=key(bed);cards=rows(PACK_ROOT/bed/ctx/'cards.jsonl');a=[];n=0
  for c in cards:
   m=k['items'][c['card_id']];x=dict(card_id=c['card_id'],letters='y',marks='y',crop_ok='y',errors=[],detail='')
   if m['control']:x.update(m['expected'])
   else:
    n+=1;x['letters']='y' if n<=45 else 'u';x['crop_ok']='y' if n<=44 else 'n'
   a.append(x)
  jsonl(root/'answers'/bed/(ctx+'.jsonl'),a);mapped,controls=map_records('bsb',ctx,a,k,cards)
  jsonl(root/'answers'/bed/(ctx+'.mapped.jsonl'),mapped);dump(root/'answers'/bed/(ctx+'.controls.json'),controls)
  rollout=root/(bed+'_'+ctx+'.rollout.jsonl');rollout.write_text('{"fixture":true}\n')
  dump(root/'scan'/bed/(ctx+'.scan.json'),dict(ok=True,violations=[],scanner_version='v4.4-canonical',manifest_check_skipped=False,rollout=str(rollout),rollout_sha256=sha(rollout)))
  dump(root/'receipts'/bed/(ctx+'.json'),dict(status='audit clean',rc=0,scanner_rc=0,map_rc=0,canonical_scanner_sha256=CANONICAL,rollout=str(rollout),controls=controls,context_flagged=False,weekly_used_before=7,weekly_used_after=7))
 return root


def test_completed_reread_route(completed):
 r=score(completed);assert not r['partial'] and r['included_contexts']==16
 assert sum(x['n'] for x in r['strata'])==800
 assert sum(x['controls']['n'] for x in r['strata'])==80
 s=r['strata'][3];assert s['letters']['yes']==90 and s['crop_ok']['yes']==88 and s['verdict']=='FAIL'
 assert r['strata'][4]['verdict']=='FAIL' # 89 crop successes /100
 assert all('pending Opus' in x['marks'] for x in r['strata'])

@pytest.mark.parametrize('corruption',['scanner','scan','rollout','answers','mapping','controls','draw'])
def test_score_fail_closed(completed,corruption):
 bed,ctx=next(iter(REPLACEMENTS.values()));base=completed
 if corruption=='scanner':(base/'tools/scan_rollout.py').write_text('altered')
 elif corruption=='scan':
  p=base/'scan'/bed/(ctx+'.scan.json');v=json.loads(p.read_text());v['ok']=False;dump(p,v)
 elif corruption=='rollout':(base/(bed+'_'+ctx+'.rollout.jsonl')).write_text('changed')
 elif corruption=='answers':
  p=base/'answers'/bed/(ctx+'.jsonl');a=rows(p);a.pop();jsonl(p,a)
 elif corruption=='mapping':
  p=base/'answers'/bed/(ctx+'.mapped.jsonl');a=rows(p);a[0]['letters']='n';jsonl(p,a)
 elif corruption=='controls':
  p=base/'receipts'/bed/(ctx+'.json');v=json.loads(p.read_text());v['context_flagged']=True;dump(p,v)
 elif corruption=='draw':
  p=base/'keys/w2c1_nlg_poly1900/draw.jsonl';a=rows(p);a[0]['id']='changed';jsonl(p,a)
 with pytest.raises(ValueError):score(base)


def rewrite_answers(root,bed,ctx,answers):
 cards=rows(PACK_ROOT/bed/ctx/'cards.jsonl');k=key(bed)
 mapped,controls=map_records('bsb',ctx,answers,k,cards)
 jsonl(root/'answers'/bed/(ctx+'.jsonl'),answers)
 jsonl(root/'answers'/bed/(ctx+'.mapped.jsonl'),mapped)
 dump(root/'answers'/bed/(ctx+'.controls.json'),controls)
 p=root/'receipts'/bed/(ctx+'.json');receipt=json.loads(p.read_text())
 receipt.update(controls=controls,context_flagged=controls['flagged']);dump(p,receipt)


def test_exact_bars_and_marks_ignored(completed):
 bed='w2c1_nlg_poly1900_r2';k=key(bed)
 for ctx in ('c1','c2'):
  a=rows(completed/'answers'/bed/(ctx+'.jsonl'))
  next(x for x in a if not k['items'][x['card_id']]['control'] and x['crop_ok']=='n')['crop_ok']='y'
  for x in a:x['marks']='n'
  rewrite_answers(completed,bed,ctx,a)
 s=score(completed)['strata'][3]
 assert s['letters']['yes']==s['crop_ok']['yes']==90 and s['verdict']=='PASS'


def test_two_control_errors_prevent_pass(completed):
 bed='w2c1_nlg_greek_poly_r2';ctx='c1';k=key(bed)
 a=rows(completed/'answers'/bed/(ctx+'.jsonl'));wrong=0
 for x in a:
  if k['items'][x['card_id']]['control']:
   if wrong<2:x['letters']='n' if x['letters']=='y' else 'y';wrong+=1
  else:x['letters']=x['crop_ok']='y'
 rewrite_answers(completed,bed,ctx,a)
 s=score(completed)['strata'][4]
 assert s['observed_gate']=='PASS' and s['verdict']=='FAIL' and s['controls']['flagged']
