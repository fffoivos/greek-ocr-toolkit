"""AU1B offline rebuild checks. No Codex, probes, readers, or scanner execution."""
import tempfile
import driver as d
from build import *

def check():
 history=A/'build_history/au1b';receipt=load(history/'receipt.json')
 old=load(history/'contexts.json');new=load(A/'contexts.json')
 assert len(old)==len(new)==2
 all_old=set();all_new=set();comparisons=[]
 for previous,current in zip(old,new):
  d.integrity(previous);d.integrity(current)
  assert current['name']==previous['name']+'_au1b'
  assert not (A/'runs'/current['name']).exists()
  before=rows(Path(previous['reader_dir'])/'items.jsonl');after=rows(Path(current['reader_dir'])/'items.jsonl')
  assert len(before)==len(after)==current['items']+10
  oldkey=load(previous['key']);newkey=load(current['key'])
  for a,b in zip(before,after):
   all_old.add(a['item_id']);all_new.add(b['item_id'])
   assert {k:v for k,v in a.items() if k!='item_id'}=={k:v for k,v in b.items() if k!='item_id'},'order/public bytes/options changed'
   ma=dict(oldkey[a['item_id']]);mb=dict(newkey[b['item_id']]);ma.pop('public');mb.pop('public');assert ma==mb,'target/control provenance changed'
  assert sum(m['control'] for m in newkey.values())==10
  comparisons.append(dict(context=current['name'],targets=current['items'],controls=10,order_images_options_provenance_identical=True))
 assert len(all_new)==102 and not all_old&all_new
 for path,digest in receipt['preserved_sha256'].items():assert sha(path)==digest
 assert load(A/'runs/accent_initial_001/receipt.json')['status']=='BLOCKED'
 binding=canonical_binding();assert binding==load(A/'scanner_binding.json')
 # Copy and verify the actual runtime scanner path, without executing the scanner.
 with tempfile.TemporaryDirectory(prefix='au1b-scanner-') as td:
  target=d.scanner(Path(td));assert sha(target)==binding['expected']
 # A changed HANDOVER binding must stop before scanner copy or any reader budget.
 original_binding=d.canonical_binding
 try:
  d.canonical_binding=lambda:dict(binding,handover_sha256='0'*64)
  with tempfile.TemporaryDirectory(prefix='au1b-drift-') as td:
   try:d.scanner(Path(td))
   except AssertionError as e:assert 'binding changed since build' in str(e)
   else:raise AssertionError('scanner binding drift accepted')
   assert not list(Path(td).iterdir())
 finally:d.canonical_binding=original_binding
 # Repeating the same namespace must refuse without changing any packs or metadata.
 try:build('au1b')
 except AssertionError as e:assert str(e)=='fresh build already exists'
 else:raise AssertionError('namespace was reused')
 for wrapper in ('RUN.sh','REREAD.sh','SCORE.sh'):assert (A/wrapper).stat().st_mode&0o111
 d.input_binding()
 dump(A/'AU1B_validation.json',dict(status='PASS',contexts=comparisons,fresh_item_ids=102,old_new_id_overlap=0,scanner_binding=binding,preserved_files=len(receipt['preserved_sha256']),blocked_attempt_unchanged=True,duplicate_build_refused=True,scanner_drift_refused_before_copy=True,reader_runs=0,probes=0,scanner_executions=0,network=False))
 print('AU1B PASS: 2 fresh contexts, 102 fresh item IDs, 10 controls each; no reads/probes/scans')
if __name__=='__main__':check()
