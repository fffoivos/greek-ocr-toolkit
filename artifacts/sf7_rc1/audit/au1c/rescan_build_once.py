import sys
sys.path.insert(0,'artifacts/sf7_rc1/audit')
from driver import *
out=A/'au1c';out.mkdir(exist_ok=False)
old=load(A/'scanner_binding.json');new=canonical_binding();assert new['version']=='v4.5.5'
dump(out/'previous_scanner_binding.json',old)
shutil.copyfile(A/'reread_contexts.json',out/'previous_reread_contexts.json')
dump(A/'scanner_binding.json',new)
dump(out/'rebind_receipt.json',dict(previous=old,current=new,action='explicit AU1C canonical rebind; original builds and runs preserved',network=False,reader_runs=0))
scan=scanner(out)
results={}
for c in load(A/'contexts.json'):
 folder=A/'runs'/c['name'];rec=load(folder/'receipt.json');roll=rec['read']['rollout'];assert sha(roll)==rec['read']['rollout_sha256']
 path=out/(c['name']+'.scan.json')
 with path.open('w') as f:p=subprocess.run([sys.executable,'-B',str(scan),roll,c['reader_dir']],stdout=f,stderr=subprocess.STDOUT)
 result=load(path);assert p.returncode in (0,2)
 effective=dict(rec,original_status=rec['status'],original_receipt_sha256=sha(folder/'receipt.json'),scan_path=str(path),scan_sha256=sha(path),scanner_binding=new,status='VOID')
 if p.returncode==0 and result['ok']:
  integrity(c);answer=Path(c['reader_dir'])/'answers.jsonl';decoded,gate=validate(c,answer)
  effective['controls']=gate
  if gate['passed'] and not rec.get('post_probe_error'):
   dst=out/(c['name']+'.answers.jsonl');shutil.copyfile(answer,dst)
   effective.update(status='VALID',answers_path=str(dst),answers_sha256=sha(dst));effective.pop('error',None)
 else:effective['error']='canonical v4.5.5 scanner VOID'
 results[c['name']]=effective
 print(c['name'],effective['status'],'violations',len(result['violations']))
dump(out/'rescan_receipts.json',results)
