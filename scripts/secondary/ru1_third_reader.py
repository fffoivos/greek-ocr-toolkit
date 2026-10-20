"""Build ctx04/r3 once, offline, with unchanged r1 pixels and private metadata."""
import json
import random
import secrets
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent/'reading'))
from common import ROOT, PACK_ROOT, rows, dump, jsonl, sha
from scan_packs import scan

SEED = '20261017:RU1:ctx04:r3'


def build():
    source = PACK_ROOT/'ctx04/r1'; dest = PACK_ROOT/'ctx04/r3'
    keypath = ROOT/'keys/ctx04.r3.json'
    if dest.exists() or keypath.exists() or (dest.parent/'MANIFEST.r3.json').exists():
        raise ValueError('refuse to overwrite prepared r3')
    key = json.loads((ROOT/'keys/ctx04.json').read_text())
    original = rows(source/'items.jsonl')
    assert [i['item_id'] for i in original] == key['readers']['r1']
    used = {i for p in (ROOT/'keys').glob('ctx*.json') for i in json.loads(p.read_text())['items']}
    ordered = list(original); random.Random(SEED).shuffle(ordered)
    new = []; private = {}
    (dest/'crops').mkdir(parents=True)
    for item in ordered:
        iid = 'k'+secrets.token_hex(5)
        while iid in used: iid = 'k'+secrets.token_hex(5)
        used.add(iid)
        meta = key['items'][item['item_id']]
        src = source/item['crop']; target = dest/item['crop']
        assert sha(src) == meta['source_crop_sha256']
        if not target.exists(): shutil.copyfile(src, target)
        assert sha(target) == sha(src)
        new.append(dict(item, item_id=iid)); private[iid] = meta
    jsonl(dest/'items.jsonl', new)
    dump(keypath, dict(context='ctx04', reader='r3', seed=SEED,
         readers={'r3':[i['item_id'] for i in new]}, items=private))
    result = scan(dest, 'yer')
    dump(ROOT/'closure_RU1R3.json', result)
    if not result['ok']: raise ValueError(result['violations'])
    return dict(ok=True, items=len(new), controls=sum(m['control'] for m in private.values()),
                seed=SEED, pack=str(dest), manifest_sha256=result['manifest_sha256'], key_sha256=sha(keypath))


if __name__ == '__main__': print(json.dumps(build(), indent=2))
