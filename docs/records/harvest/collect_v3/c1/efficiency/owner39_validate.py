"""Closed-folder validation for owner39; no Pillow or source imports needed."""
import hashlib
import json
from pathlib import Path
import random
import struct


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_pack(root, pack):
    d=root/pack['path']
    assert d.is_dir() and d.resolve().is_relative_to(root/'packs/owner39')
    assert not any(p.is_symlink() for p in [d,d.parent,d.parent.parent])
    assert {p.name for p in d.parent.iterdir()}=={'r1','r2'}
    assert all(p.is_dir() and not p.is_symlink() for p in d.parent.iterdir())
    assert {p.name for p in d.iterdir()}=={'cards.jsonl','PROTOCOL.md','README.md','answer_schema.json','img'}
    assert not any(p.is_symlink() for p in d.rglob('*'))
    disk={p for p in d.rglob('*') if p.is_file()}
    assert disk=={root/f['path'] for f in pack['files']}
    for f in pack['files']:
        p=root/f['path'];assert p.resolve().is_relative_to(d.resolve())
        assert p.stat().st_nlink==1
        assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256']
    truth=json.loads((root/'keys/owner39/truth.json').read_text())
    mapping=json.loads((root/'keys/owner39/input_mapping.json').read_text())
    private_needles={t['db_id'] for t in truth.values()}
    private_needles.update(t['owner_note'] for t in truth.values() if t['owner_note'])
    private_needles.update(m['line_id'] for m in mapping.values())
    for p in disk:
        if p.suffix=='.png':
            assert p.parent==d/'img' and p.stem==sha(p)
            raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
            offset=8
            while offset<len(raw):
                length=struct.unpack('>I',raw[offset:offset+4])[0]
                assert raw[offset+4:offset+8] in (b'IHDR',b'IDAT',b'IEND'), 'Unexpected PNG metadata'
                offset+=length+12
            assert offset==len(raw)
        else:
            assert p.name in {'cards.jsonl','PROTOCOL.md','README.md','answer_schema.json'}
            text=p.read_text()
            assert not any(s in text for s in ('/Users/','/private/','../','owner_note','owner_status','truth_word','truth_marks','google_word','reader_word','db_id','"section"','google_error','reader_errors_39'))
            assert not any(needle in text for needle in private_needles), 'Private owner/source text in reader folder'
    rows=[json.loads(s) for s in (d/'cards.jsonl').read_text().splitlines()]
    assert len(rows)==39==pack['items_per_reader']
    assert [r['card_id'] for r in rows]==pack['item_ids']
    assert len(set(pack['item_ids']))==39 and set(pack['item_ids'])==set(truth)
    expected_fields={'card_id','word_image','line_image','anchor_index','anchor_base','options','extra_options'}
    if pack['arm']=='E2': expected_fields=(expected_fields-{'line_image'})|{'letter_image'}
    referenced=set()
    for row in rows:
        assert set(row)==expected_fields
        cid=row['card_id'];m=mapping[cid]
        assert len(cid)==24 and all(c in '0123456789abcdef' for c in cid)
        assert row['anchor_index']==m['letter_in_word'] and row['anchor_base']==truth[cid]['base']
        assert set(row['options'])=={'A','B','C','D'} and set(row['extra_options'])=={'literal','unreadable'}
        assert not any(t['db_id'] in json.dumps(row) for t in truth.values())
        w,h=m['native_size']
        for field in ('word_image','line_image','letter_image'):
            if field not in row: continue
            name=row[field];p=Path(name)
            assert len(p.parts)==1 and p.suffix=='.png' and not p.is_absolute()
            dest=d/'img'/p;assert dest.resolve().is_relative_to(d.resolve()) and dest.is_file()
            referenced.add('img/'+name)
            dims=struct.unpack('>II',dest.read_bytes()[16:24])
            if field=='line_image': expected=(w,h)
            else:
                box=m['letter_box'] if field=='letter_image' else m['word_box']
                scale=8 if field=='letter_image' else 3 if pack['arm']=='E2' else m['zoom_scale']
                assert scale in (1,2,3,8)
                expected=((box[2]-box[0])*scale,(box[3]-box[1])*scale)
            assert dims==expected
        if pack['arm']=='E2':
            assert m['images']['line'] not in {row['word_image'],row['letter_image']}
    copies={c['path']:c for c in pack['copied_crops']}
    assert referenced==set(copies)=={str(p.relative_to(d)) for p in disk if p.suffix=='.png'}
    for rel,c in copies.items(): assert sha(d/rel)==c['sha256']
    key=json.loads((root/f'keys/owner39/{pack["arm"]}.json').read_text())
    order=sorted(truth);seed=f'eff:owner39:{pack["arm"]}';random.Random(seed).shuffle(order)
    assert key['seed']==seed and key['order']==order
    assert key['readers']=={'r1':order,'r2':list(reversed(order))}
    assert pack['item_ids']==key['readers'][pack['reader']]
    return disk,len(copies)
