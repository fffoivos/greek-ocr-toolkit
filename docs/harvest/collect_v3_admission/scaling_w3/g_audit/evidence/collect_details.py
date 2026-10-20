import pathlib,subprocess,json
D=pathlib.Path(__file__).parent
remote=r'''
import pathlib,json,hashlib,importlib.util
P=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/greek-page-ocr')
print(json.dumps(dict(fonttools=bool(importlib.util.find_spec('fontTools')))))
for f in ['out/e1_run4/synthetic/audit_report.json','out/e1_run4/synthetic/select_report.json','out/e1_run4/pool.jsonl.ingest_report.json','out/e1_run4/supply.json','assets/fonts/FONTS_provenance.json','factory/exclusions/realcrops_v1.txt']:
 p=P/f;b=p.read_bytes();print(json.dumps(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),content=b.decode())))
p=P/'out/e1_run4/prepare_binding.json';b=p.read_bytes();a=json.loads(b)
print(json.dumps(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),keys=list(a),inputs={k:v for k,v in a.get('inputs',{}).items() if '/fonts/' not in k or k.endswith(('.ttf','.otf'))},other={k:v for k,v in a.items() if k not in ['inputs','crop_sha256']})))
for p in sorted((P/'assets/fonts').iterdir()):
 if p.suffix.lower() in ['.ttf','.otf']:
  print(json.dumps(dict(font_path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())))
for name in ['corpus.jsonl','pool.jsonl']:
 p=P/'out/e1_run4'/name
 with p.open() as f:head=[next(f) for _ in range(3)]
 print(json.dumps(dict(head_path=str(p),bytes=p.stat().st_size,rows=[json.loads(x) for x in head])))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','clariden','python3 -B -'],input=remote,text=True,capture_output=True,timeout=60)
assert r.returncode==0,r.stderr
out=[]
for line in r.stdout.splitlines():
 o=json.loads(line)
 if 'content' in o:
  name=pathlib.Path(o['path']).name;(D/name).write_text(o.pop('content'));o['witness']=name
 out.append(o)
(D/'remote_details.json').write_text(json.dumps(out,indent=2)+'\n')
print('details records',len(out))
