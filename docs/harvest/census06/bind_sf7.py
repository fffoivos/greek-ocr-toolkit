"""Bind full SF7 files on Clariden: PATH SHA [PATH SHA ...], one per parent.

Run in a coordinator-submitted CPU allocation: census05 decisions are large.
No scheduling is performed. Validate everything before publishing new inputs/code.
The committed pre-binding package remains immutable. --check-only does no publish.
"""
import argparse,collections,hashlib,json,os,shutil,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
D=Path(__file__).resolve().parent;P=D/'package/projects/greek-ocr-toolkit-pipe032'
sys.path.insert(0,str(P))
from greekocr.harvest.line_pipeline_census import Ledger,ArtifactCorrector,records,file_sha
from greekocr.harvest.line_pipeline import canonical,validate_result
from greekocr.harvest import admission
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')

def pairs(args):
 if len(args)%2:raise ValueError('expected PATH SHA pairs')
 out=[]
 for path,wanted in zip(args[::2],args[1::2]):
  p=Path(path).resolve()
  if len(wanted)!=64 or any(c not in '0123456789abcdef' for c in wanted):raise ValueError('invalid SHA256')
  if file_sha(p)!=wanted:raise ValueError('SF7 sha mismatch: '+str(p))
  out.append(dict(path=str(p),sha256=wanted,bytes=p.stat().st_size))
 return out

def load_and_validate(entries,config,baseline,work,head=None,require_complete=True):
 """Full production loader, original registered rows, disk-backed coverage sets."""
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 original=sqlite3.connect(Path(baseline/'ledger.sqlite').resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 versions=json.loads((P/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 codec=admission.load_codec(P/'greekocr/_vendor/codec/v2.json')
 parents={p['id']:p['sha256'] for p in config['parents']}
 ledger=Ledger(work/'binding.sqlite',{'purpose':'SF7 full per-row binding validation'})
 ledger.db.execute('CREATE TABLE expected(parent TEXT,id TEXT,PRIMARY KEY(parent,id))')
 ledger.db.execute('CREATE TABLE supplied(parent TEXT,id TEXT,PRIMARY KEY(parent,id))')
 cur=json.loads((baseline/'CURRENT.json').read_text());generation=baseline/'generations'/cur['export_id']
 if cur['status']!='completed':raise ValueError('census05 incomplete')
 if file_sha(generation/'summary.json')!=cur['summary_sha256']:raise ValueError('summary mismatch')
 summary=json.loads((generation/'summary.json').read_text())
 if file_sha(generation/'decisions.jsonl')!=summary['outputs']['decisions']['sha256']:raise ValueError('baseline decisions mismatch')
 if require_complete:
  for _,d in records(generation/'decisions.jsonl'):
   if d.get('routes',{}).get('polytonic',{}).get('status')=='not_applied_out_of_scope':
    b=d['binding'];ledger.db.execute('INSERT INTO expected VALUES (?,?)',(b['parent_id'],b['id']))
 reports=[];releases=[];seen_parents=set()
 for entry in entries:
  count=0;counts=collections.Counter();reason_counts=collections.Counter();parent=None;sample=work/(str(len(reports))+'.head.jsonl')
  with sample.open('w') as output:
   for _,r in records(entry['path']):
    if head is not None and count>=head:break
    b=r['binding'];pid=b['parent_id']
    if parent is None:parent=pid
    if pid!=parent or pid not in parents:raise ValueError('mixed or unknown parent')
    found=original.execute('SELECT payload FROM observations WHERE parent=? AND id=?',(pid,b['id'])).fetchone()
    if not found:raise ValueError('SF7 row outside registered parent')
    row=json.loads(found[0]);validate_result(r,row,'polytonic',versions)
    ledger.register(row,codec)
    ledger.db.execute('INSERT INTO supplied VALUES (?,?)',(pid,b['id']))
    output.write(canonical(r)+'\n');count+=1;counts[r['status']]+=1
    if r['status']=='kept_unverified':reason_counts[r['evidence']['reason']]+=1
  if parent is None or parent in seen_parents:raise ValueError('empty or duplicate parent file')
  seen_parents.add(parent);ledger.db.commit()
  path=sample if head is not None else Path(entry['path'])
  release=dict(tool='polytonic',parent_id=parent,path=str(path),sha256=file_sha(path),format='line-tool-result-v1',status='released',parent_manifest_sha256=parents[parent],tool_version=versions['polytonic']['version'],tool_digest=versions['polytonic']['digest'])
  ArtifactCorrector(ledger,versions,parents).load(release)
  reports.append(dict(entry,parent_id=parent,records=count,status_counts=dict(counts),kept_unverified_reason_counts=dict(reason_counts),ArtifactCorrector_load='PASS'));releases.append(release)
 if require_complete:
  if seen_parents!=set(parents):raise ValueError('missing parent files')
  for query in ('SELECT * FROM expected EXCEPT SELECT * FROM supplied','SELECT * FROM supplied EXCEPT SELECT * FROM expected'):
   if ledger.db.execute(query).fetchone():raise ValueError('SF7 coverage mismatch (missing or extra routed row)')
  expected=dict(ledger.db.execute('SELECT parent,count(*) FROM expected GROUP BY parent'))
 else:expected={}
 if json.loads((baseline/'CURRENT.json').read_text())!=cur:raise ValueError('baseline changed')
 ledger.db.close();original.close()
 return dict(status='PASS',parents=reports,coverage=expected,complete=require_complete),releases

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('bindings',nargs='+');p.add_argument('--work',type=Path,required=True);p.add_argument('--check-only',action='store_true');p.add_argument('--baseline',type=Path,default=W/'census_05_20261020/attempts/full-split-001');a=p.parse_args()
 if not W.is_dir():p.error('execute on Clariden with the full census05 publication mounted')
 entries=pairs(a.bindings);config=json.loads((D/'census06_config.json').read_text())
 a.work.mkdir(parents=True,exist_ok=False);started=time.monotonic()
 report,releases=load_and_validate(entries,config,a.baseline,a.work/'validation');report['elapsed_seconds']=time.monotonic()-started
 (a.work/'sf7_binding_report.json').write_text(json.dumps(report,indent=2)+'\n')
 if a.check_only:return
 # Content-addressed subdirectory: the B numerics inputs already occupy inputs/.
 ident=hashlib.sha256(canonical(entries).encode()).hexdigest()[:16]
 dest=W/'census_06_20261020/inputs'/('sf7-'+ident);dest.mkdir(parents=True,exist_ok=False)
 for r in releases:
  target=dest/(r['parent_id']+'.jsonl')
  with Path(r['path']).open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
  if file_sha(target)!=r['sha256']:raise ValueError('copied SF7 mismatch')
  r['path']=str(target)
 stage=a.work/'stage';bundle=stage/'docs/harvest/census06';bundle.mkdir(parents=True)
 for rel in (D/'PAYLOAD_PATHS.txt').read_text().splitlines():
  src=D/rel;target=bundle/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
 config['corrections']=[r for r in config['corrections'] if r['tool']!='polytonic']+releases
 (bundle/'census06_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
 inputs=json.loads((D/'INPUTS.json').read_text());inputs=[x for x in inputs if x.get('kind')!='pending_sf7']
 inputs.extend(dict(remote_path=r['path'],sha256=r['sha256'],bytes=Path(r['path']).stat().st_size,kind='sf7_full_per_row') for r in releases)
 (bundle/'INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n')
 (bundle/'sf7_binding_report.json').write_text(json.dumps(report,indent=2)+'\n')
 from build_package import build
 package=build(bundle,stage)
 target=W/'census_06_20261020/code'/package['package_id'];target.mkdir(parents=True,exist_ok=False)
 subprocess.run(['rsync','-a',str(stage)+'/',str(target)+'/'],check=True)
 for line in (bundle/'DEPLOY_SHA256SUMS').read_text().splitlines():
  h,rel=line.split('  ',1)
  if file_sha(target/rel)!=h:raise ValueError('code readback mismatch')
 print(json.dumps(dict(package,root=str(target),sf7_binding='OK')))
if __name__=='__main__':main()
