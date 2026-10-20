import subprocess,json,pathlib,hashlib
D=pathlib.Path(__file__).parent
remote=r'''
import pathlib,json,hashlib,socket
W=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'); P=W/'greek-page-ocr'
paths=[P/'out/e1_run4/synthetic/build_info.json',P/'out/e4/wave1b/v2-codec/old_v2/synthetic/build_info.json',P/'factory/recipe.v5.json',P/'factory/recipe.v6.json',P/'factory/appearance_band.json',P/'data/sources.json',W/'benchmark_0.2/seal04/suite.json',W/'benchmark_0.2/seal04/SEAL_RECEIPT.json']
for p in paths:
 b=p.read_bytes(); print(json.dumps(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),content=b.decode())))
for p in [P/'data',P/'factory',P/'out/e1_run4/synthetic',W/'benchmark_0.2/seal04']:
 print(json.dumps(dict(listing=str(p),entries=[dict(name=x.name,bytes=x.stat().st_size,is_dir=x.is_dir()) for x in sorted(p.iterdir())])))
for split in ['test','dev']:
 p=W/f'benchmark_0.2/seal04/benchmark_v02_{split}.jsonl';b=p.read_bytes();print(json.dumps(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),content=b.decode())))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','clariden','python3 -B -'],input=remote,text=True,capture_output=True,timeout=60)
(D/'metadata_ssh_stderr.txt').write_text(r.stderr)
assert r.returncode==0,r.stderr
out=[]
for i,line in enumerate(r.stdout.splitlines()):
 o=json.loads(line)
 if 'content' in o:
  name=('e1_' if '/e1_run4/' in o['path'] else 'a12_' if '/old_v2/' in o['path'] else '')+pathlib.Path(o['path']).name
  (D/name).write_text(o.pop('content'));o['witness']=name
 out.append(o)
(D/'remote_metadata_index.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
