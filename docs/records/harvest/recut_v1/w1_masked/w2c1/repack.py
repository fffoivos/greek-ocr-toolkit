"""Repack the four fixed VOID contexts offline; never invoke a reader or probe."""
from build import *
from repack_config import REPLACEMENTS
from closure import check
from tools.scan_rollout import integrity

def repack():
 assert sha(HERE/'tools/scan_rollout.py') == CANONICAL
 assert (HERE/'prompts/bsb.md').read_bytes() == (REFERENCE/'prompts/bsb.md').read_bytes()
 existing={c['card_id'] for p in PACK_ROOT.glob('*/*/cards.jsonl') for c in rows(p)}
 receipts=[];keys={}
 for (old,ctx),(bed,newctx) in REPLACEMENTS.items():
  directory=PACK_ROOT/bed/ctx
  if directory.exists():raise RuntimeError('Refuse overwrite '+str(directory))
  assert integrity(PACK_ROOT/old/ctx)==([],False)
  oldkey=json.loads((HERE/'keys'/(old+'.json')).read_text())
  scan=json.loads((HERE/'scan'/old/(ctx+'.scan.json')).read_text());assert not scan['ok']
  cards=rows(PACK_ROOT/old/ctx/'cards.jsonl')
  orderseed='w2c1c:'+old+':'+ctx+':repack2'
  shuffled=list(cards);rng=random.Random(orderseed)
  oldpositions={oldkey['items'][c['card_id']]['line_id']:i for i,c in enumerate(cards) if oldkey['items'][c['card_id']]['control']}
  while True:
   rng.shuffle(shuffled)
   if all(oldpositions[oldkey['items'][c['card_id']]['line_id']]!=i for i,c in enumerate(shuffled) if oldkey['items'][c['card_id']]['control']):break
  key=keys.setdefault(bed,dict(bed=bed,protocol='bsb',seed=orderseed,readers={'c1':[],'c2':[]},items={}))
  (directory/'crops').mkdir(parents=True);public=[]
  for card in shuffled:
   iid='k'+hashlib.sha256((orderseed+':'+card['card_id']).encode()).hexdigest()[:10]
   assert iid not in existing;existing.add(iid)
   meta=oldkey['items'][card['card_id']];key['items'][iid]=meta
   source=PACK_ROOT/old/ctx/card['crop'];dest=directory/card['crop']
   assert sha(source)==meta['crop_sha256'];shutil.copyfile(source,dest);assert sha(dest)==meta['crop_sha256']
   public.append(dict(card,card_id=iid))
  key['readers'][ctx]=[c['card_id'] for c in public]
  jsonl(directory/'cards.jsonl',public);jsonl(HERE/'pack_inventory'/bed/(ctx+'.cards.jsonl'),public)
  dump(HERE/'keys'/(bed+'.json'),key)
  # Retain the exact original draw for context-slice closure, with no resampling.
  jsonl(HERE/'keys'/bed/'draw.jsonl',rows(HERE/'keys'/old/'draw.jsonl'))
  for sub in ('answers','scan','receipts'):(HERE/sub/bed).mkdir(parents=True,exist_ok=True)
  dump(HERE/'receipts'/bed/(ctx+'.json'),dict(bed=bed,context=ctx,status='prepared; reader not started',canonical_scanner_sha256=CANONICAL,model='gpt-6.1-sol',effort='medium',network='OFF',replaces=dict(bed=old,context=ctx)))
  receipts.append(dict(original_bed=old,context=ctx,bed=bed,order_seed=orderseed,original_cards_sha256=sha(PACK_ROOT/old/ctx/'cards.jsonl'),cards_sha256=sha(directory/'cards.jsonl')))
 closure=[check(bed,ctx) for bed,ctx in REPLACEMENTS.values()]
 assert all(c['ok'] for c in closure),closure
 dump(HERE/'repack_closure.json',closure)
 dump(HERE/'repack_receipt.json',dict(contexts=receipts,canonical_scanner_sha256=CANONICAL,addendum='prompts/path_addendum.md',addendum_sha256=sha(HERE/'prompts/path_addendum.md'),protocol_sha256=sha(HERE/'prompts/bsb.md'),readers_started=0,network='OFF'))
if __name__=='__main__':repack()
