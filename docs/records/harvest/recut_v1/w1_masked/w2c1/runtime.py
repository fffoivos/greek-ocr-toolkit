"""W2C1 limit parsing, answer mapping and receipts; no rollout-scanner wrapper."""
from build import *
from repack_config import REPLACEMENTS
sys.path.insert(0,str(HERE/'tools'))
from ledger import weekly,record,append

def limit(line):
 value=weekly(line)
 if value>=78:raise ValueError('STOP: weekly used >= 78%')
 return value

def main():
 action,*args=sys.argv[1:]
 if action=='limit':limit(args[0]);return
 bed,ctx=args[:2];assert (bed in [bedname(*s) for s in STRATA] and ctx in ('c1','c2')) or (bed,ctx) in REPLACEMENTS.values()
 receipt=HERE/'receipts'/bed/(ctx+'.json')
 if action=='begin':
  run,before,digest=args[2:];run=json.loads(run);assert digest==CANONICAL==sha(HERE/'tools/scan_rollout.py')
  dump(receipt,dict(bed=bed,context=ctx,run=run,limit_before=before,canonical_scanner_sha256=digest,status='reader returned; audit pending'))
 elif action=='map':
  from map_answers import map_records
  key=json.loads((HERE/'keys'/(bed+'.json')).read_text());mapped,controls=map_records('bsb',ctx,rows(HERE/'answers'/bed/(ctx+'.jsonl')),key,rows(PACK_ROOT/bed/ctx/'cards.jsonl'))
  jsonl(HERE/'answers'/bed/(ctx+'.mapped.jsonl'),mapped);dump(HERE/'answers'/bed/(ctx+'.controls.json'),controls)
 elif action=='finish':
  run,before,after,sc,mc,digest=args[2:];run=json.loads(run);entry=record(run,before,after,bed,ctx,len(rows(PACK_ROOT/bed/ctx/'cards.jsonl')))
  entry.update(canonical_scanner_sha256=digest,scanner_rc=int(sc),map_rc=int(mc),marks_status='pending Opus; not admission evidence',status='audit clean' if sc==mc=='0' and run.get('rc')==0 and run.get('model')=='gpt-6.1-sol' else 'VOID or incomplete')
  assert digest==CANONICAL==sha(HERE/'tools/scan_rollout.py')
  cp=HERE/'answers'/bed/(ctx+'.controls.json')
  entry['controls']=json.loads(cp.read_text()) if cp.exists() else None
  entry['context_flagged']=entry['controls'] is None or entry['controls']['flagged']
  append(HERE/'usage_ledger.json',entry);dump(receipt,entry)
  if run.get('rc')!=0 or run.get('model')!='gpt-6.1-sol':raise ValueError('reader failed or model mismatch')
 else:raise ValueError(action)
if __name__=='__main__':main()
