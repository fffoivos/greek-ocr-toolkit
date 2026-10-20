import sys,json,random,re,subprocess,os,xml.etree.ElementTree as ET
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import *
from runtime import limit

@pytest.fixture(scope='session')
def snapshot():return snapshot_rows()

@pytest.mark.parametrize('source,cls',STRATA)
def test_pool_filters(source,cls,snapshot):
 pool=rows(HERE/'keys'/bedname(source,cls)/'pool.jsonl');cfg,classes,_=exclusions();excluded=set().union(*classes.values())
 receipt=json.loads((HERE/'build_receipt.json').read_text());allrows=snapshot
 expected=[]
 for r in allrows:
  if r['source']!=source or r['primary_class']!=cls:continue
  if source=='gazette_modern' and r.get('gazette_stratum')!='measured_1986_1990':continue
  x0,y0,x1,y1=r['crop_bbox']
  if r['tranche']=='W2' and r['candidate_usable'] is True and r['screen_merged'] is False and r['id'] not in excluded and not (y1-y0>x1-x0 and len(''.join(r['label'].split()))>=4):expected.append(r['id'])
 assert [r['id'] for r in pool]==sorted(expected)
 assert len({r['id'] for r in pool})==len(pool)

@pytest.mark.parametrize('source,cls',STRATA)
def test_seed(source,cls):
 bed=bedname(source,cls);pool=rows(HERE/'keys'/bed/'pool.jsonl');selected=rows(HERE/'keys'/bed/'draw.jsonl');key=json.loads((HERE/'keys'/(bed+'.json')).read_text())
 expected=random.Random('w2c1:'+source+':'+cls).sample(sorted(pool,key=lambda r:r['id']),min(100,len(pool)))
 assert selected==expected and key['seed']=='w2c1:'+source+':'+cls
 controls=json.loads((HERE/'keys/control_truth.json').read_text())
 for n,ctx in enumerate(('c1','c2')):
  lines=[r['id'] for r in selected[n*50:(n+1)*50]]+[r['line_id'] for r in controls if r['context']==ctx]
  random.Random(key['seed']+':order:'+ctx).shuffle(lines)
  assert [key['items'][i]['line_id'] for i in key['readers'][ctx]]==lines

@pytest.mark.parametrize('source,cls',STRATA)
@pytest.mark.parametrize('ctx',['c1','c2'])
def test_closure(source,cls,ctx):
 from closure import check
 result=check(bedname(source,cls),ctx,write=False)
 assert result['ok'],result['violations']
 from tools.scan_rollout import integrity
 assert integrity(PACK_ROOT/bedname(source,cls)/ctx)==([],False)

@pytest.mark.parametrize('source,cls',STRATA)
def test_crop_sha(source,cls):
 bed=bedname(source,cls);custody=json.loads((HERE/'keys/crop_custody.json').read_text())
 for r in custody:
  if r['bed']!=bed:continue
  src,dst=Path(r['source']),Path(r['destination'])
  assert sha(src)==sha(dst)==r['sha256']
  assert dst.name==r['sha256']+'.png' and not dst.is_symlink() and dst.stat().st_nlink==1 and not os.path.samefile(src,dst)
  from PIL import Image
  with Image.open(dst) as im:assert not im.info and im.mode in ('L','RGB')

def test_canonical():
 assert sha(REFERENCE/'tools/scan_rollout.py')==sha(HERE/'tools/scan_rollout.py')==CANONICAL
 assert sha(REFERENCE/'tools/replay_literal.py')==sha(HERE/'tools/replay_literal.py')
 launcher=(HERE/'launchers/run_bed.sh').read_text()
 assert 'SCAN=$D/tools/scan_rollout.py' in launcher and '"$PY" -B "$SCAN" "$ROLL" "$RD"' in launcher
 assert CANONICAL in launcher and 'canonical_scanner_sha256' in (HERE/'runtime.py').read_text()

def test_prompt():assert (HERE/'prompts/bsb.md').read_bytes()==(REFERENCE/'prompts/bsb.md').read_bytes()

@pytest.mark.parametrize('value',[0,76.4,77.999])
def test_limit_accept(value):assert limit('limit_id=codex primary='+str(value)+'%/10080m secondary=99%/300m')==value
@pytest.mark.parametrize('line',['primary=78%/10080m','primary=80%/10080m','primary=99%/300m secondary=78%/10080m','primary=nan%/10080m','NONE','primary=0%/300m','primary=77%/10080m secondary=76%/10080m'])
def test_limit_reject(line):
 with pytest.raises(ValueError):limit(line)

def test_launch_all(tmp_path):
 # Execute the exact generated shell using deterministic fake probes and runs.
 script=(HERE/'launch_all.sh').read_text();assert script.count('\nrun_one ')==16 and '&\n' not in script
 root=tmp_path/'task';(root/'launchers').mkdir(parents=True)
 (root/'runtime.py').write_text('import sys\nsys.path.insert(0,'+repr(str(HERE))+')\nfrom runtime import limit\nlimit(sys.argv[2])\n')
 probe=root/'launchers/limit_probe.sh';probe.write_text('#!/bin/bash\necho "limit_id=codex primary=${TEST_WEEKLY}%/10080m"\n');probe.chmod(0o755)
 runner=tmp_path/'fake-run.sh';runner.write_text('#!/bin/bash\necho "$*" >> "'+str(tmp_path/'calls')+'"\n');runner.chmod(0o755)
 script=script.replace(str(HERE),str(root)).replace(str(PACK_ROOT/'launchers/run_bed.sh'),str(runner));p=tmp_path/'launch.sh';p.write_text(script)
 for value,count,rc in [('77.9',16,0),('78',0,8),('80',0,8)]:
  calls=tmp_path/'calls';calls.unlink(missing_ok=True)
  r=subprocess.run(['bash',str(p)],env=dict(os.environ,TEST_WEEKLY=value),capture_output=True,text=True)
  assert r.returncode==rc,(r.stdout,r.stderr)
  assert len(calls.read_text().splitlines())==count if calls.exists() else count==0
 assert (root/'run.log').exists()

def test_rotated_boundary():
 for bbox,label,result in [([0,0,10,11],'1 2 3 4',True),([0,0,10,11],'123',False),([0,0,10,10],'1234',False)]:assert rotated(dict(crop_bbox=bbox,label=label))==result

def test_network_model():
 text=(HERE/'launchers/run_read.sh').read_text()
 for token in ['MODEL=gpt-6.1-sol','sandbox_workspace_write.network_access=false','web_search="disabled"','features.multi_agent=false','features.remote_plugin=false','features.apps=false']:assert token in text
 assert 'medium' in (HERE/'launchers/run_bed.sh').read_text()


def test_snapshot_binding(snapshot):
 receipt=json.loads((HERE/'build_receipt.json').read_text())
 assert receipt['features_path']==str(SNAPSHOT)
 assert receipt['features_sha256']==SNAPSHOT_SHA and receipt['w2_rows']==219381
 assert receipt['bsb_snapshot_pages']==298 and receipt['bsb_partial']
 assert receipt['gazette_filter']==dict(field='gazette_stratum',value='measured_1986_1990')

@pytest.mark.parametrize('bad_sha,bad_count',[(True,False),(False,True)])
def test_snapshot_rejects_tampering(tmp_path,bad_sha,bad_count):
 p=tmp_path/'snapshot.jsonl'
 p.write_text(json.dumps(dict(tranche='W2',source='nlg',primary_class='poly1850'))+'\n')
 with pytest.raises(ValueError,match='snapshot (sha256|row count) mismatch'):
  snapshot_rows(p,'0'*64 if bad_sha else sha(p),2 if bad_count else 1)

def test_gazette_stratum_boundary():
 r=dict(tranche='W2',source='gazette_modern',primary_class='modern_scanned',candidate_usable=True,screen_merged=False,crop_bbox=[0,0,100,10],label='abcd',id='test')
 assert not eligible(r,'gazette_modern','modern_scanned',set())
 r['gazette_stratum']='measured_1986_1990'
 assert eligible(r,'gazette_modern','modern_scanned',set())
 r['gazette_stratum']='other'
 assert not eligible(r,'gazette_modern','modern_scanned',set())

@pytest.mark.parametrize('operation',[
 "open(str(LIVE/'W2/features.jsonl'),'rb')",
 "open(str(LIVE/'W1/features.jsonl'),'rb')",
 "__import__('socket').socket()",
 "open(str(LIVE/'w2c1_forbidden_write'),'w')",
])
def test_preparation_guard(operation):
 code='from build import *\nguard()\ntry:\n '+operation+'\nexcept PermissionError:\n pass\nelse:\n raise AssertionError("guard did not reject")\n'
 result=subprocess.run([sys.executable,'-B','-c',code],cwd=HERE,capture_output=True,text=True)
 assert result.returncode==0,result.stderr


def test_launch_stops_between_contexts(tmp_path):
 script=(HERE/'launch_all.sh').read_text()
 root=tmp_path/'task';(root/'launchers').mkdir(parents=True)
 (root/'runtime.py').write_text('import sys\nsys.path.insert(0,'+repr(str(HERE))+')\nfrom runtime import limit\nlimit(sys.argv[2])\n')
 calls=tmp_path/'calls'
 probe=root/'launchers/limit_probe.sh'
 probe.write_text('#!/bin/bash\nif [ -e "'+str(calls)+'" ]; then value=78; else value=77.9; fi\necho "limit_id=codex primary=$value%/10080m"\n');probe.chmod(0o755)
 runner=tmp_path/'fake-run.sh';runner.write_text('#!/bin/bash\necho "$*" >> "'+str(calls)+'"\n')
 script=script.replace(str(HERE),str(root)).replace(str(PACK_ROOT/'launchers/run_bed.sh'),str(runner))
 p=tmp_path/'launch.sh';p.write_text(script)
 result=subprocess.run(['bash',str(p)],capture_output=True,text=True)
 assert result.returncode==8
 assert calls.read_text().splitlines()==['w2c1_bsb_poly1850_poly1850 c1']
