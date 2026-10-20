"""AU1C offline checks; readers/probes must never execute."""
import tempfile
import driver as d
from build import *

def check():
 binding=canonical_binding();assert binding==load(A/'scanner_binding.json') and binding['version']=='v4.5.5'
 rescans=load(A/'au1c/rescan_receipts.json')
 assert [r['status'] for r in rescans.values()]==['VALID','VOID']
 for name,r in rescans.items():
  assert sha(A/'runs'/name/'receipt.json')==r['original_receipt_sha256']
  assert sha(r['scan_path'])==r['scan_sha256'] and sha(r['read']['rollout'])==r['read']['rollout_sha256']
  assert load(r['scan_path'])['ok']==(r['status']=='VALID')
 selected=load(A/'reread_contexts.json');assert [(c['phase'],c['items']) for c in selected]==[('reread',4),('initial',3)]
 oldids={i for p in (A/'keys').glob('*.json') if p.stem not in [c['name'] for c in selected] and isinstance(load(p),dict) for i in load(p)}
 ids=[]
 for c in selected:
  files=d.integrity(c);rd=Path(c['reader_dir']);key=load(c['key']);ids+=list(key)
  assert not (rd/'answers.jsonl').exists() and not (A/'runs'/c['name']).exists()
  assert len(key)==c['items']+10 and sum(m['control'] for m in key.values())==10
  assert set(files)=={'items.jsonl'}|({'README.md','answer_schema.json'} if c['track']=='capital' else set())|{p[f] for p in rows(rd/'items.jsonl') for f in ('line_image','word_image','letter_image') if f in p}
  for m in key.values():assert sha(m['native_asset'])==m['native_asset_sha256']
 assert len(ids)==len(set(ids)) and not set(ids)&oldids
 obs,_=d.observations();assert len(obs)==79
 # Simulate the staged retry -> dynamic capital reread -> scoring path.
 saved={name:getattr(d,name) for name in ('A','reread','run','observations','write_context','score','cli')}
 try:
  with tempfile.TemporaryDirectory(prefix='au1c-flow-') as td:
   d.A=Path(td);initial={'name':'capital_initial_001_au1c','track':'capital','phase':'initial','key':str(d.A/'key.json')}
   accent={'name':'accent_reread_001_au1c','track':'accent','phase':'reread','key':str(d.A/'accent.json')}
   dump(initial['key'],{'k1':dict(control=False,heads=['h1'])});dump(accent['key'],{})
   dump(d.A/'reread_contexts.json',[accent,initial]);dump(d.A/'routing.json',{'heads':[{'head_id':'h1','released_label':'smooth'}]});dump(d.A/'keys/capital_control_pool.json',[])
   calls=[]
   d.reread=lambda:None
   d.cli=lambda *a,**kw:(_ for _ in ()).throw(AssertionError('reader/probe forbidden'))
   def run(phase,name):
    calls.append((phase,name));dump(d.A/'runs'/name/'receipt.json',{'status':'VALID','after':{'weekly_used_percent':26}});return 0
   d.run=run
   d.observations=lambda:({'h1':{'initial':{'breathing':'smooth','accent':'none'}}},[])
   def write(name,track,entries,pool,phase):
    key=d.A/(name+'.json');dump(key,{'k2':entries[0]});return dict(name=name,track=track,key=str(key),phase=phase)
   d.write_context=write;d.score=lambda:calls.append('score')
   assert d.resume_rereads()==0
   assert calls==[('initial',initial['name']),('reread',accent['name']),('reread','capital_reread_001_au1c'),'score']
   calls.clear();dump(d.A/'runs'/initial['name']/'receipt.json',{'status':'VOID'})
   assert d.resume_rereads()==1 and not calls
   dump(d.A/'runs'/initial['name']/'receipt.json',{'status':'VALID','after':{'weekly_used_percent':78}})
   assert d.resume_rereads()==1 and not calls
 finally:
  for name,value in saved.items():setattr(d,name,value)
 result=dict(status='PASS',tests=['canonical binding and preserved original receipts','rescan and rollout hashes','fresh contexts closure/native hashes/controls/disjoint ids','79 valid accent observations; VOID excluded','offline simulated capital retry and triggered reread','VOID and budget stop'],reader_runs=0,network=False)
 dump(A/'AU1C_validation.json',result);print(json.dumps(result))
if __name__=='__main__':check()
