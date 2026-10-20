#!/usr/bin/env python3
"""Fail-closed blind pack inspection. Manifests live beside reader folders."""
import argparse,json,re,sys,random
from collections import Counter
from pathlib import Path
from PIL import Image
from common import *

def scan(directory,bed,write_manifest=True,allow_runtime=False,compare_option_maps=True,r3_seed='20261017:RU1:ctx04:r3'):
    directory=Path(directory);violations=[];files={};expected={itemfile(bed)};images=set()
    def fail(message):violations.append(message)
    suffix='.'+directory.name if directory.name!='r1' else ''
    keypath=ROOT/f'keys/{directory.parent.name}{suffix}.json'
    if not keypath.is_file():return {'ok':False,'directory':str(directory),'violations':['missing private assignment: '+str(keypath)]}
    key=json.loads(keypath.read_text())
    try:data=rows(directory/itemfile(bed))
    except Exception as exc:return {'ok':False,'directory':str(directory),'violations':['item file: '+str(exc)]}
    field=idfield(bed);ids=[r.get(field) for r in data]
    if ids!=key['readers'].get(directory.name):fail('ids/order differ from private assignment')
    if len(set(ids))!=len(ids):fail('duplicate opaque ids')
    if any(not isinstance(i,str) or not re.fullmatch('k[0-9a-f]{10}',i) for i in ids):fail('invalid opaque id')
    forbidden_ids={m['source_id'] for m in key['items'].values() if bed=='owner39'}
    forbidden_ids.update(m['source_id'] for m in key['items'].values() if m.get('source_id'))
    for r in data:
        if set(r)!=FIELDS[bed]:fail('wrong public fields: '+str(r.get(field)))
        for f in ('crop','word_image','line_image'):
            if f not in r:continue
            p=r[f]
            if not isinstance(p,str) or Path(p).is_absolute() or '..' in Path(p).parts:
                fail('unsafe image reference');continue
            images.add(p)
        if bed=='owner39':
            if not isinstance(r.get('options'),dict) or not 1<=len(r['options'])<=4 or not set(r['options'])<=set('ABCD'):fail('invalid options')
        if bed=='yer' and (type(r.get('slots')) is not int or r['slots']<0 or re.findall(r'⟦(\d+)⟧',r['masked_text'])!=[str(i+1) for i in range(r['slots'])]):fail('invalid yer mask slots')
    if bed=='owner39' and len({len(r['options']) for r in data if isinstance(r.get('options'),dict)})!=1:fail('inconsistent number of options within bed')
    expected|=images
    if bed=='owner39':
        expected|={'README.md','answer_schema.json'}
        for n in ('README.md','answer_schema.json'):
            if not (directory/n).is_file() or sha(directory/n)!=sha(EFF/'packs/owner39/E0a/r1'/n):fail('owner protocol changed: '+n)
    allowed_dirs={str(Path(p).parent) for p in images}
    for p in sorted(directory.rglob('*')):
        rel=str(p.relative_to(directory))
        if allow_runtime and (rel=='answers.jsonl' or rel=='zoom' or rel.startswith('zoom/')):
            if p.is_symlink() or (p.is_file() and p.stat().st_nlink!=1): fail('unsafe runtime entry: '+rel)
            continue
        if p.is_symlink():fail('symlink: '+rel);continue
        if p.is_dir():
            if rel not in allowed_dirs:fail('unexpected directory: '+rel)
            continue
        if not p.is_file():fail('non-regular file: '+rel);continue
        if p.stat().st_nlink!=1:fail('hardlink: '+rel)
        if rel not in expected:fail('unexpected file: '+rel)
        files[rel]=sha(p)
        if p.suffix.lower()=='.png':
            if p.name!=files[rel]+'.png':fail('image filename not content hash: '+rel)
            try:
                with Image.open(p) as im:
                    im.load()
                    if im.format!='PNG' or im.mode not in {'L','RGB'}:fail('image not L/RGB PNG: '+rel)
                    if im.info:fail('image contains metadata: '+rel)
            except Exception as exc:fail('PNG decode: '+rel+': '+str(exc))
        else:
            try:text=p.read_text()
            except UnicodeError:fail('non-text public file: '+rel);continue
            if re.search(r'(?<![A-Za-z0-9])[ca]\d{3}(?![A-Za-z0-9])',text):fail('efficiency id in '+rel)
            if re.search(r'(?i)(?:truth|verdict|source_id|line_id|expected_form|lead_verified|opus_reference)',text):fail('private label in '+rel)
            if any(i and i in text for i in forbidden_ids):fail('source id in '+rel)
    for p in expected-set(files):fail('missing file: '+p)
    other=directory.parent/('r2' if directory.name=='r1' else 'r1')/itemfile(bed)
    if other.is_file():
        sibling=rows(other)
        strip=lambda r:{k:v for k,v in r.items() if k!='item_id' and (compare_option_maps or k!='options')}
        if directory.name == 'r3':
            ordered = list(sibling); random.Random(r3_seed).shuffle(ordered)
            if [strip(r) for r in data] != [strip(r) for r in ordered]: fail('reader content is not seeded r3 order')
        elif [strip(r) for r in data]!=[strip(r) for r in reversed(sibling)]:fail('reader content is not exact reverse')
        if set(ids)&{r['item_id'] for r in sibling}:fail('reader ids overlap')
    if directory.name == 'r3':
        for earlier in ('r1', 'r2'):
            kp = ROOT/f"keys/{directory.parent.name}{'.r2' if earlier == 'r2' else ''}.json"
            if kp.exists() and set(ids) & set(json.loads(kp.read_text())['items']): fail('reader ids overlap earlier assignment')
    result={'ok':not violations,'directory':str(directory),'bed':bed,'items':len(data),'violations':violations,'files':files}
    if write_manifest and not violations:
        manifest=directory.parent/f'MANIFEST.{directory.name}.json';dump(manifest,{'bed':bed,'reader':directory.name,'files':files});result['manifest_sha256']=sha(manifest)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reader_dirs',type=Path,nargs='*');args=parser.parse_args()
    dirs=args.reader_dirs or sorted(PACK_ROOT.glob('ctx*/r[123]'))
    results=[scan(d,'yer') for d in dirs]
    if not dirs:results.append(dict(ok=False,violations=['no contexts built: required blind packs absent']))
    expected={d.parent.name for d in dirs}
    root_bad=[str(p) for p in PACK_ROOT.iterdir() if p.is_symlink() or not p.is_dir() or p.name not in expected]
    for d in dirs:
        root_bad.extend(str(p) for p in d.parent.iterdir() if p.is_symlink() or p.name not in {'r1','r2','r3','MANIFEST.r1.json','MANIFEST.r2.json','MANIFEST.r3.json'})
    if root_bad:results.append(dict(ok=False,violations=['unexpected pack-root/context entries']+root_bad))
    print(json.dumps(results,ensure_ascii=False,indent=2));return int(any(not r['ok'] for r in results))
if __name__=='__main__':sys.exit(main())
