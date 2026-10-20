"""CAPS1 closure adapter: L-mode originals and disjoint contexts only."""
from build import *
sys.path.insert(0,str(HERE/'tools'))
import scan_packs

def check(bed,ctx,write=True):
 result=scan_packs.scan(PACK_ROOT/bed/ctx,bed,write_manifest=False)
 key=json.loads((HERE/'keys'/(bed+'.json')).read_text());cards=rows(PACK_ROOT/bed/ctx/'cards.jsonl');meta=[key['items'][c['card_id']] for c in cards]
 drawrows=rows(HERE/'keys'/bed/'draw.jsonl');expected=drawrows[:50] if ctx=='c1' else drawrows[50:]
 errors=result['violations'];b=[m for m in meta if not m['control']];c=[m for m in meta if m['control']]
 if len(b)!=len(expected) or len(c)!=5:errors.append('wrong bed/control counts')
 if {m['line_id'] for m in b}!={r['id'] for r in expected}:errors.append('bed draw coverage mismatch')
 if any(m['tranche']!='W2' for m in b):errors.append('non-W2 bed row')
 truth=json.loads((HERE/'keys/control_truth.json').read_text());old=json.loads((HERE.parent/'caps1/keys/caps1.json').read_text())
 expectedcontrols=[old['items'][t['opaque_id']] for t in truth if t['context']==ctx]
 if sorted(c,key=lambda m:m['line_id'])!=sorted(expectedcontrols,key=lambda m:m['line_id']):errors.append('approved controls changed')
 if len(set(key['readers']['c1'])&set(key['readers']['c2'])):errors.append('context overlap')
 result['ok']=not errors
 if write and result['ok']:
  dump(PACK_ROOT/bed/('MANIFEST.'+ctx+'.json'),dict(bed=bed,reader=ctx,files=result['files']));result['manifest_sha256']=sha(PACK_ROOT/bed/('MANIFEST.'+ctx+'.json'))
 return result
if __name__=='__main__':
 result=[check(bedname(*s),ctx) for s in STRATA for ctx in ('c1','c2')];dump(HERE/'closure.json',result)
 print(json.dumps([dict(bed=r['bed'],directory=r['directory'],items=r['items'],ok=r['ok'],violations=r['violations']) for r in result],indent=2));sys.exit(0 if all(r['ok'] for r in result) else 2)
