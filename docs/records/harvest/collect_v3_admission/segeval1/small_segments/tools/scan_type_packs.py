"""Q3 closure wrapper: single r1, exact three public fields, byte-copy PNGs.
The canonical scan_packs.scan hard-codes beds, private keys and reverse r2;
this wrapper reuses common helpers, applies closure without those assumptions,
and preserves the manifest format consumed by canonical scan_rollout in place.
"""
import json,re,struct
from ss4_common import *
def png_chunks(data):
    if data[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('not PNG')
    pos=8
    while pos<len(data):
        n=int.from_bytes(data[pos:pos+4],'big'); kind=data[pos+4:pos+8]; yield kind; pos+=12+n
    if pos!=len(data): raise ValueError('invalid PNG chunks')
def scan(ctx,write_manifest=True,layout="type"):
    itemfile, imagefolder = ("items.jsonl", "img") if layout=="type2" else ("cards.jsonl", "crops")
    c,key=assignment(ctx,layout); rd=PACK_ROOT/layout/ctx/'r1'; errors=[]; files={}; images=set()
    def fail(s): errors.append(s)
    data=rows(rd/itemfile); ids=[r.get('card_id') for r in data]
    if ids!=c['card_ids'] or len(set(ids))!=len(ids): fail('assignment/order mismatch')
    if len(ids)>100: fail('too many cards')
    for r in data:
        if set(r)!={'card_id','crop','google_text'}: fail('private/incorrect fields')
        if not re.fullmatch(r'k[0-9a-f]{10}',r['card_id']): fail('invalid opaque id')
        if not re.fullmatch(imagefolder+r'/[0-9a-f]{64}\.png',r['crop']): fail('unsafe crop')
        images.add(r['crop'])
    expected={itemfile}|images
    for p in rd.rglob('*'):
        rel=str(p.relative_to(rd))
        if p.is_symlink(): fail('symlink '+rel); continue
        if p.is_dir():
            if rel!=imagefolder: fail('unexpected directory '+rel)
            continue
        if not p.is_file() or p.stat().st_nlink!=1: fail('not independent regular file '+rel); continue
        files[rel]=sha(p)
        if p.suffix=='.png':
            if p.name!=files[rel]+'.png': fail('hash name mismatch')
            chunks=list(png_chunks(p.read_bytes()))
            if any(k in chunks for k in (b'tEXt',b'zTXt',b'iTXt',b'eXIf')): fail('PNG private metadata')
    if set(files)!=expected: fail('file closure mismatch')
    result=dict(ctx=ctx,ok=not errors,items=len(data),violations=errors,files=files)
    if write_manifest and not errors:
        manifest=dict(bed=layout,reader='r1',files=files)
        dump(rd.parent/'MANIFEST.r1.json',manifest); dump(SS/'q3/manifests'/layout/f'{ctx}.r1.json',manifest)
        result['manifest_sha256']=sha(rd.parent/'MANIFEST.r1.json')
    return result
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--layout', choices=['type','type2'], default='type'); a=p.parse_args()
    contexts=json.loads((SS/f'q3/keys/{a.layout}.json').read_text())['contexts']; results=[scan(c,layout=a.layout) for c in contexts]
    dump(SS/('q3/PACK_SCAN.json' if a.layout=='type' else 'q3/TYPE2_PACK_SCAN.json'),results)
    sys.exit(int(any(not r['ok'] for r in results)))
