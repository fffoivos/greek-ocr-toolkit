"""One-time CQ4d deterministic control replacement; preserve bed JSONL bytes."""
import hashlib,random,shutil
from pathlib import Path
from build import OUT,SEED,load,dump,sha,render
from closure import scan
from workflow import verified_control_pool,controls_verified

def main():
 receipt_path=OUT/'control_swap_receipt.json'
 assert not receipt_path.exists(),'Refuse repeat swap'
 frozen=load(OUT/'build_hashes.json')
 # Existing custody must hold except the explicitly amended workflow and tests.
 amended={'tools/workflow.py','tools/test_inventory.py','tools/validate_build.py'}
 for rel,h in frozen.items():
  if rel not in amended:assert hashlib.sha256((OUT/rel).read_bytes()).hexdigest()==h,rel
 backup=OUT/'cq4d_before';backup.mkdir()
 for rel in ('build_hashes.json','contexts.json','build_receipt.json'):shutil.copyfile(OUT/rel,backup/rel)
 contexts=load(OUT/'contexts.json');pool=verified_control_pool();approved={x['source_id'] for x in pool};rng=random.Random(SEED);swaps=[];changed=[]
 prompt=(OUT/'prompts/cap1.md').read_bytes()
 for c in contexts:
  key=load(c['key']);rd=Path(c['directory']);old=(rd/'items.jsonl').read_bytes().splitlines(keepends=True);ids=list(key['items']);placed={x['source_id'] for x in key['items'].values() if x['control']}
  rejected=[i for i,x in key['items'].items() if x['control'] and x['source_id'] not in approved]
  if not rejected:continue
  dest=backup/c['tag'];dest.mkdir();shutil.copyfile(c['key'],dest/'key.json');shutil.copyfile(rd/'items.jsonl',dest/'items.jsonl');shutil.copyfile(rd.parent/f'MANIFEST.{rd.name}.json',dest/'manifest.json')
  before_bed={i:old[n] for n,i in enumerate(ids) if not key['items'][i]['control']};before_order=list(ids)
  for ident in rejected:
   previous=key['items'][ident];candidates=sorted((x for x in pool if x['source_id'] not in placed),key=lambda x:x['source_id']);replacement=rng.choice(candidates);placed.remove(previous['source_id']);placed.add(replacement['source_id'])
   public=render(replacement,rd,rng,c['tag']);public['item_id']=ident
   key['items'][ident]=replacement|dict(public=public)
   old[ids.index(ident)]=(__import__('json').dumps(public,ensure_ascii=False,allow_nan=False)+'\n').encode()
   swaps.append(dict(context=c['tag'],item_id=ident,rejected_source_id=previous['source_id'],replacement_source_id=replacement['source_id']))
  (rd/'items.jsonl').write_bytes(b''.join(old));dump(c['key'],key)
  assert list(key['items'])==before_order
  for n,i in enumerate(ids):
   if i in before_bed:assert old[n]==before_bed[i]
  needed={x['public'][f] for x in key['items'].values() for f in ('word_image','line_image')}
  for p in (rd/'img').iterdir():
   if str(p.relative_to(rd)) not in needed:p.unlink()
  result=scan(rd,key['items']);assert result['ok'],result;dump(OUT/'closure'/f'{c["tag"]}.json',result)
  c['manifest_sha256']=hashlib.sha256((rd.parent/f'MANIFEST.{rd.name}.json').read_bytes()).hexdigest();changed.append(c['tag'])
 dump(OUT/'contexts.json',contexts)
 for c in contexts:
  result=scan(c['directory'],load(c['key'])['items'],write=False);assert result['ok'],result
 controls_verified(contexts);assert (OUT/'prompts/cap1.md').read_bytes()==prompt
 receipt=dict(seed=SEED,rejected_controls=7,verified_controls=33,swaps=swaps,swap_count=len(swaps),changed_contexts=changed,bed_items_byte_identical=True,item_order_identical=True,prompt_sha256=hashlib.sha256(prompt).hexdigest(),all_contexts_closure_ok=True,git_writes=False)
 dump(receipt_path,receipt);build=load(OUT/'build_receipt.json');build.update(status='CQ4d_VERIFIED_CONTROLS_READY',control_swaps=receipt);dump(OUT/'build_receipt.json',build)
 for rel in frozen:frozen[rel]=hashlib.sha256((OUT/rel).read_bytes()).hexdigest()
 for rel in ('tools/swap_controls.py','control_swap_receipt.json','control_review/lead_review.json'):frozen[rel]=hashlib.sha256((OUT/rel).read_bytes()).hexdigest()
 dump(OUT/'build_hashes.json',frozen)
 print('Swaps:',len(swaps),'contexts:',len(changed))
if __name__=='__main__':main()
