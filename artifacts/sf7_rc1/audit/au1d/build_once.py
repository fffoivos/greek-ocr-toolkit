"""AU1D offline repack only. No readers, probes, scanning or network."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from driver import *

def main():
 archive=A/'au1d';receipt=archive/'context_build_receipt.json'
 assert not receipt.exists(),'AU1D already built; refuse overwrite'
 input_binding();assert canonical_binding()==load(A/'scanner_binding.json')
 selected=load(A/'reread_contexts.json')
 old=next(c for c in selected if c['name']=='capital_initial_001_au1c')
 assert load(A/'runs'/old['name']/'receipt.json')['status']=='VOID'
 name='capital_initial_001_au1d'
 assert not (A/'keys'/f'{name}.json').exists() and not (A/'runs'/name).exists()
 paths=[*sorted((A/'runs').rglob('*')),A/'contexts.json',A/'routing.json',A.parent/'audit100_frame.jsonl',A/'scanner_binding.json',*sorted((A/'prompts').glob('*.md'))]
 for c in all_contexts():
  paths += [Path(c['key']),Path(c['reader_dir']).parent/f'MANIFEST.{c["name"]}.json',*sorted(Path(c['reader_dir']).rglob('*'))]
 preserved={str(p):sha(p) for p in paths if p.is_file()}
 (archive/'previous_reread_contexts.json').write_bytes((A/'reread_contexts.json').read_bytes())
 source=PROJECTS/'greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/w2c1/prompts/path_addendum.md'
 addendum=A/'prompts/path_addendum.md';assert not addendum.exists();addendum.write_bytes(source.read_bytes())
 prompt=A/'prompts/capital_au1d.md';assert not prompt.exists()
 prompt.write_bytes((A/'prompts/capital.md').read_bytes()+addendum.read_bytes()+b'\ndo not iterate over image paths in code; call the view tool once per image, with the literal path\n')
 # AU1C used these entries in key order and its own name as the order seed.
 original=load(A/'keys/capital_initial_001_au1b.json')
 entries=[m for m in original.values() if not m['control']]
 fresh=write_context(name,'capital',entries,load(A/'keys/capital_control_pool.json'),'initial',order_name=old['name'])
 fresh.update(prompt=str(prompt),prompt_sha256=sha(prompt))
 oldkey=load(old['key']);key=load(fresh['key']);before=rows(Path(old['reader_dir'])/'items.jsonl');after=rows(Path(fresh['reader_dir'])/'items.jsonl')
 assert len(after)==13 and sum(m['control'] for m in key.values())==10
 for p,q in zip(before,after):
  assert {k:v for k,v in p.items() if k!='item_id'}=={k:v for k,v in q.items() if k!='item_id'},'seeded order/options/pixels drift'
  assert {k:v for k,v in oldkey[p['item_id']].items() if k!='public'}=={k:v for k,v in key[q['item_id']].items() if k!='public'}
 oldids={ident for p in (A/'keys').glob('*.json') if p.stem!=name and isinstance(load(p),dict) for ident in load(p)}
 assert not oldids.intersection(key),'reused public IDs'
 integrity(fresh);reader_prompt(fresh)
 dump(A/'reread_contexts.json',[fresh if c['name']==old['name'] else c for c in selected])
 for path,digest in preserved.items():assert sha(path)==digest,'preserved artifact changed: '+path
 dump(receipt,dict(status='BUILT_ONLY',context=fresh,replaces=old['name'],seed=SEED,order_seed=f'{SEED}:{old["name"]}',targets=[h for m in key.values() if not m['control'] for h in m['heads']],fresh_item_ids=list(key),same_order_options_pixels=True,addendum_source=str(source),addendum_source_sha256=sha(source),addendum_sha256=sha(addendum),base_prompt_sha256=sha(A/'prompts/capital.md'),preserved_sha256=preserved,model='gpt-6.1-sol',effort='medium',reader_runs=0,probes=0,network=False))
 print(json.dumps({'status':'BUILT_ONLY','context':name,'items':3,'controls':10,'reader_runs':0}))

if __name__=='__main__':main()
