"""Offline second-read packs. Never invokes a reader or a network operation."""
import hashlib
import json
from pathlib import Path
import random
import shutil
from n1_render import SCRATCH
from n1_pack_closure import scan

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/n1'
PACK_ROOT=SCRATCH/'sol_packs/n1'
SEED='20261017:N1R2:reverse'

def rows(path): return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,value): Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def build_context(ctx, pack_root=PACK_ROOT, out=OUT):
    directory=pack_root/ctx/'r2'
    keypath=out/'keys'/f'{ctx}.r2.json'
    if directory.exists() or keypath.exists(): raise ValueError('refusing to overwrite second-read pack')
    key=json.loads((out/'keys'/f'{ctx}.json').read_text())
    first=rows(pack_root/ctx/'r1/items.jsonl')
    assert [r['item_id'] for r in first]==key['readers']['r1']
    rng=random.Random(SEED+':'+ctx); used=set(key['items']); public=[]; private={}
    (directory/'img').mkdir(parents=True)
    for item in reversed(first):
        meanings=list(item['options'].values())
        while True:
            rng.shuffle(meanings)
            options=dict(zip('ABCDEFGH',meanings))
            if all(options[k]!=item['options'][k] for k in options): break
        while True:
            iid='k'+f'{rng.getrandbits(40):010x}'
            if iid not in used: break
        used.add(iid)
        new=dict(item,item_id=iid,options=options); public.append(new)
        private[iid]=dict(key['items'][item['item_id']], option_map=options)
        for name in ('line','zoom'):
            target=directory/item[name]
            if not target.exists(): shutil.copyfile(pack_root/ctx/'r1'/item[name], target)
    (directory/'items.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in public))
    dump(keypath,dict(readers={'r2':[r['item_id'] for r in public]}, items=private, calibration=False, seed=SEED))
    closure=scan(directory,out)
    if not closure['ok']: raise ValueError(closure['violations'])
    return dict(context=ctx,items=len(public),controls=sum(v['control_truth'] is not None for v in private.values()),closure=closure)

def main():
    # Preserve every existing artifact and completed r1 file before generating anything.
    prior={str(p):sha(p) for base in (OUT,PACK_ROOT) for p in base.rglob('*') if p.is_file()}
    snapshot=SCRATCH/'n1_review/n1r2_prior.json'; snapshot.parent.mkdir(parents=True,exist_ok=True)
    if snapshot.exists(): raise ValueError('existing preparation snapshot')
    dump(snapshot,prior)
    built=[build_context(f'ctx{i:02}') for i in range(1,8)]
    closure=[scan(PACK_ROOT/f'ctx{i:02}'/r,OUT,completed=True) for i in range(1,8) for r in ('r1','r2')]
    assert all(r['ok'] for r in closure),[(r['directory'],r['violations']) for r in closure if not r['ok']]
    assert all(sha(p)==h for p,h in prior.items())
    dump(OUT/'N1R2_PACKS.json',dict(seed=SEED,contexts=built,closure=closure,prior_snapshot=str(snapshot),prior_unchanged=True))
    print(json.dumps(dict(packs=len(built),closure_ok=sum(r['ok'] for r in closure),closure_total=len(closure))))
if __name__=='__main__': main()
