#!/usr/bin/env python3
"""Fail-closed blind pack inspection. Manifests live beside reader folders."""
import argparse,json,re,sys
from pathlib import Path
from PIL import Image
from common import *

def scan(directory,bed,write_manifest=True):
    directory=Path(directory);violations=[];files={};expected={itemfile(bed)};images=set()
    def fail(message):violations.append(message)
    keypath=ROOT/(f'keys/{bed}_r3.json' if directory.name=='r3' else f'keys/{bed}.json')
    if not keypath.is_file():return {'ok':False,'directory':str(directory),'violations':['missing private assignment: '+str(keypath)]}
    key=json.loads(keypath.read_text())
    try:data=rows(directory/itemfile(bed))
    except Exception as exc:return {'ok':False,'directory':str(directory),'violations':['item file: '+str(exc)]}
    field=idfield(bed);ids=[r.get(field) for r in data]
    if ids!=key['readers'].get('r1' if directory.name=='r1b' else directory.name):fail('ids/order differ from private assignment')
    if len(set(ids))!=len(ids):fail('duplicate opaque ids')
    if any(not isinstance(i,str) or not re.fullmatch('k[0-9a-f]{10}',i) for i in ids):fail('invalid opaque id')
    forbidden_ids={m['source_id'] for m in key['items'].values() if bed=='owner39'}
    forbidden_ids.update(m['line_id'] for m in key['items'].values() if m.get('line_id'))
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
    if bed=='cap1':
        if len(data)!=66:fail('CQ1 must contain 66 items')
        for r in data:
            if r!=key['items'].get(r.get('item_id'),{}).get('public'):fail('public item differs from frozen assignment')
        expected|={'README.md','answer_schema.json'}
        for r in data:
            for field, values in [('breathing_options', {'none','smooth','rough','unreadable'}), ('accent_options', {'none','acute','grave','circumflex','unreadable'})]:
                opts=r.get(field,{})
                if set(opts)!=set('ABCDE'[:len(values)]) or set(opts.values())!=values:fail('invalid option permutation')
    if bed=='owner39':
        expected|={'README.md','answer_schema.json'}
        for n in ('README.md','answer_schema.json'):
            if not (directory/n).is_file() or sha(directory/n)!=sha(EFF/'packs/owner39/E0a/r1'/n):fail('owner protocol changed: '+n)
    allowed_dirs={str(Path(p).parent) for p in images}
    for p in sorted(directory.rglob('*')):
        rel=str(p.relative_to(directory))
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
                    if im.format!='PNG' or im.mode!='RGB':fail('image not RGB PNG: '+rel)
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
    if bed!='cap1' and directory.name!='r3':
        if not other.is_file():fail('reverse reader missing')
        elif data!=list(reversed(rows(other))):fail('r2 is not exact reverse')
    result={'ok':not violations,'directory':str(directory),'bed':bed,'items':len(data),'violations':violations,'files':files}
    if write_manifest and not violations:
        manifest=directory.parent/f'MANIFEST.{directory.name}.json';dump(manifest,{'bed':bed,'reader':directory.name,'files':files});result['manifest_sha256']=sha(manifest)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reader_dirs',type=Path,nargs='*');args=parser.parse_args()
    dirs=args.reader_dirs or [PACK_ROOT/b/r for b in FIELDS for r in ('r1','r2')]
    results=[scan(d,d.parent.name) for d in dirs];print(json.dumps(results,ensure_ascii=False,indent=2));return int(any(not r['ok'] for r in results))
if __name__=='__main__':sys.exit(main())
