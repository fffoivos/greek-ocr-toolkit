"""Offline AU1D invariants and coordinator flow. Never launches readers/probes."""
import tempfile
import driver as d
from build import *

def check():
 r=load(A/'au1d/context_build_receipt.json');c=r['context'];old=next(x for x in load(A/'au1d/previous_reread_contexts.json') if x['name']==r['replaces'])
 for path,digest in r['preserved_sha256'].items():assert sha(path)==digest,path
 assert canonical_binding()==load(A/'scanner_binding.json')
 assert sha(r['addendum_source'])==r['addendum_source_sha256']==sha(A/'prompts/path_addendum.md')
 d.input_binding();d.integrity(c);prompt=d.reader_prompt(c)
 assert sha(c['prompt'])==c['prompt_sha256']
 assert not (Path(c['reader_dir'])/'answers.jsonl').exists() and not (A/'runs'/c['name']).exists()
 before=rows(Path(old['reader_dir'])/'items.jsonl');after=rows(Path(c['reader_dir'])/'items.jsonl');key=load(c['key'])
 assert len(after)==13 and sum(m['control'] for m in key.values())==10
 assert all({k:v for k,v in p.items() if k!='item_id'}=={k:v for k,v in q.items() if k!='item_id'} for p,q in zip(before,after))
 assert not set(key)&{ident for p in (A/'keys').glob('*.json') if p.stem!=c['name'] and isinstance(load(p),dict) for ident in load(p)}
 obs,receipts=d.observations()
 assert len(obs)==79 and any(x['context']==old['name'] and x['status']=='VOID' for x in receipts)
 assert not any(h.startswith(('RB7-065:17:','RB7-053:0:','RB7-055:6:')) for h in obs)
 saved={n:getattr(d,n) for n in ('A','reread','run','observations','write_context','score','cli')}
 try:
  with tempfile.TemporaryDirectory(prefix='au1d-flow-') as td:
   d.A=Path(td);selected=load(A/'reread_contexts.json');dump(d.A/'reread_contexts.json',selected)
   dump(d.A/'routing.json',load(A/'routing.json'));dump(d.A/'keys/capital_control_pool.json',[])
   calls=[];built=[];h=next(m['heads'][0] for m in key.values() if not m['control'])
   d.reread=lambda:None
   d.cli=lambda *a,**kw:(_ for _ in ()).throw(AssertionError('reader/probe forbidden'))
   def run(phase,name):
    current=next(x for x in load(d.A/'reread_contexts.json') if x['name']==name)
    if current['track']=='capital':assert current['prompt_sha256']==c['prompt_sha256'] and current['prompt']==c['prompt']
    calls.append((phase,name));dump(d.A/'runs'/name/'receipt.json',{'status':'VALID','after':{'weekly_used_percent':27}});return 0
   d.run=run;d.observations=lambda:({h:{'initial':{'breathing':'smooth','accent':'none'}}},[])
   def write(name,track,entries,pool,phase):
    built.append(name);p=d.A/(name+'.json');dump(p,{'kfixture':entries[0]});return dict(name=name,track=track,key=str(p),phase=phase)
   d.write_context=write;d.score=lambda:calls.append('score')
   assert d.resume_rereads()==0
   assert calls==[('initial',c['name']),('reread','accent_reread_001_au1c'),('reread','capital_reread_001_au1d'),'score']
   assert built==['capital_reread_001_au1d']
   calls.clear();dump(d.A/'runs'/c['name']/'receipt.json',{'status':'VOID'})
   assert d.resume_rereads()==1 and not calls
   dump(d.A/'runs'/c['name']/'receipt.json',{'status':'VALID','after':{'weekly_used_percent':78}})
   assert d.resume_rereads()==1 and not calls
 finally:
  for n,v in saved.items():setattr(d,n,v)
 result=dict(status='PASS',context=c['name'],tests=['prior attempts/packs/prompts preserved by SHA-256','canonical v4.5.5 unchanged','same seeded order/options/pixels and 10 controls','fresh IDs and closed pack','verbatim protocol plus sourced addendum and no-loop sentence','VOID excluded from observations and retained in receipts','offline retry then reread flow inherits addendum','VOID and budget stops'],reader_runs=0,probes=0,network=False)
 dump(A/'AU1D_validation.json',result);print(json.dumps(result))

if __name__=='__main__':check()
