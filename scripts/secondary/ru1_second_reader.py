"""Prepare reverse blind packs offline. Preserve runtime outputs outside input closure."""
import json
import secrets
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'reading'))
from common import ROOT, PACK_ROOT, SCRATCH, rows, dump, jsonl, sha
from scan_packs import scan


def build():
    archive=[]; results=[]
    used={i['item_id'] for p in PACK_ROOT.glob('ctx*/r1/items.jsonl') for i in rows(p)}
    for ctx in sorted(PACK_ROOT.glob('ctx*')):
        r1=ctx/'r1';dest=ctx/'r2'
        if dest.exists():raise ValueError('refuse to overwrite r2: '+str(dest))
        key=json.loads((ROOT/f'keys/{ctx.name}.json').read_text())
        original=rows(r1/'items.jsonl');new=[];private={}
        assert [r['item_id'] for r in original]==key['readers']['r1']
        dest.mkdir();(dest/'crops').mkdir()
        for item in reversed(original):
            iid='k'+secrets.token_hex(5)
            if iid in used:raise ValueError('opaque collision')
            used.add(iid);m=key['items'][item['item_id']]
            src=r1/item['crop'];assert sha(src)==m['source_crop_sha256']
            target=dest/item['crop']
            if not target.exists():shutil.copyfile(src,target)
            assert sha(target)==sha(src)
            new.append(dict(item,item_id=iid));private[iid]=m
        jsonl(dest/'items.jsonl',new)
        dump(ROOT/f'keys/{ctx.name}.r2.json',dict(context=ctx.name,reader='r2',readers={'r2':[r['item_id'] for r in new]},items=private))
        # Reader-produced evidence is retained byte-for-byte, outside blind input folders.
        for p in sorted(r1.iterdir()):
            if p.name in {'items.jsonl','crops'}:continue
            target=SCRATCH/'ru1_review/r1_runtime'/ctx.name/p.name
            if target.exists():raise ValueError('archive exists')
            target.parent.mkdir(parents=True,exist_ok=True)
            hashes={str(f.relative_to(p)) if p.is_dir() else p.name:sha(f) for f in (p.rglob('*') if p.is_dir() else [p]) if f.is_file()}
            shutil.move(str(p),str(target))
            actual={str(f.relative_to(target)) if target.is_dir() else target.name:sha(f) for f in (target.rglob('*') if target.is_dir() else [target]) if f.is_file()}
            assert hashes==actual
            archive.append(dict(original=str(p),archive=str(target),files=hashes))
        results.extend([scan(r1,'yer'),scan(dest,'yer')])
    assert len(results)==8 and all(s['ok'] for s in results),results
    dump(ROOT/'closure_RU11b.json',results);dump(ROOT/'runtime_archive_RU11b.json',archive)
    return results

if __name__=='__main__':
    print(json.dumps([dict(directory=r['directory'],ok=r['ok'],items=r['items']) for r in build()],indent=2))
