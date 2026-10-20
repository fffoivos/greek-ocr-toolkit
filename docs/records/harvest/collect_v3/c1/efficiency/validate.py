#!/usr/bin/env python3
"""Validate pack closure, original IDs, hashes, allocations, and E2 rasters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import struct

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def image_paths(item):
    if 'word_image' in item:
        return ['img/'+item[f] for f in ('word_image','line_image','letter_image') if f in item]
    return item['crop'] if isinstance(item['crop'],list) else [item['crop']]


def validate(root=ROOT):
    root = Path(root).resolve()
    manifest = json.loads((root/'MANIFEST.json').read_text())
    truth = json.loads((root/'keys/truth.json').read_text())
    listed = set(); counts = {}; images = 0
    for pack in manifest['packs']:
        if pack['bed']=='owner39':
            from owner39_validate import validate_pack
            disk, count = validate_pack(root, pack)
            listed.update(disk); images += count
            continue
        d = root/pack['path']; assert d.is_dir() and d.is_relative_to(root/'packs')
        # An immediate parent contains reader directories only. No colocated
        # keys, answers, output files, manifests, symlinks, or extra payloads.
        assert all(p.is_dir() and not p.is_symlink() for p in d.parent.iterdir())
        disk = {p for p in d.rglob('*') if p.is_file()}
        assert not any(p.is_symlink() for p in d.rglob('*'))
        expected = {root/f['path'] for f in pack['files']}
        assert disk == expected
        for f in pack['files']:
            p = root/f['path']; assert p.resolve().is_relative_to(d.resolve())
            assert p.stat().st_nlink == 1, f'Hardlink: {p}'
            assert sha(p) == f['sha256'] and p.stat().st_size == f['bytes'], p
            assert p.suffix == '.png' or p.name in (pack['items_file'],'PROTOCOL.md')
            listed.add(p)
        for textfile in (d/pack['items_file'],d/'PROTOCOL.md'):
            text = textfile.read_text()
            assert '/Users/' not in text and '/private/' not in text and '../' not in text
        rows = read_rows(d/pack['items_file']); bed = pack['bed']; field = 'card_id' if bed=='bsb' else 'item_id'
        assert len(rows) == pack['items_per_reader']
        assert [r[field] for r in rows] == pack['item_ids']
        referenced = set()
        for row in rows:
            allowed = {'card_id','crop','google_text','word_scripts'} if bed=='bsb' else {'item_id','crop','masked_text','slots'}
            assert set(row) == allowed
            for rel in image_paths(row):
                p = Path(rel)
                assert not p.is_absolute() and '..' not in p.parts
                assert p.parts[0] == 'crops' and p.suffix == '.png'
                target = (d/p).resolve()
                assert target.is_relative_to(d.resolve()) and target.is_file()
                referenced.add(rel)
        copies = {c['path']: c for c in pack['copied_crops']}
        assert referenced == set(copies)
        assert referenced == {str(p.relative_to(d)) for p in disk if p.suffix=='.png'}
        for rel, c in copies.items():
            assert sha(d/rel) == c['sha256']
            if 'source_sha256' in c:
                assert c['sha256'] == c['source_sha256']
        images += len(copies)
        counts.setdefault((bed,pack['arm']), []).extend(pack['item_ids'])
        if pack['arm']=='E2':
            key = json.loads((root/f'keys/{bed}/E2.json').read_text())['e2_mapping']
            for row in rows:
                iid = row[field]; mapping = key[iid]
                if bed=='bsb':
                    assert len(mapping['words']) == len(row['google_text'].split())
                    assert sum(len(w['letters']) for w in mapping['words']) > 0
                else:
                    assert len(mapping['words']) == row['slots']
                    assert sum(len(w['letters']) for w in mapping['words']) == row['slots']
                assert row['crop'] == [r['path'] for r in mapping['images']]
                for im in mapping['images']:
                    x0,y0,x1,y1 = im['native_box']; scale = im['scale']
                    assert scale in (3,8)
                    with (d/im['path']).open('rb') as f:
                        header = f.read(24)
                    assert header[:8] == b'\x89PNG\r\n\x1a\n'
                    assert struct.unpack('>II',header[16:24]) == ((x1-x0)*scale,(y1-y0)*scale)
    assert listed == {p for p in (root/'packs').rglob('*') if p.is_file()}
    for (bed,arm), ids in counts.items():
        assert len(ids) == len(set(ids)) and set(ids)==set(truth[bed])
        key = json.loads((root/f'keys/{bed}/{arm}.json').read_text())
        ordered = sorted(truth[bed]); random.Random(f'eff:{bed}:{arm}').shuffle(ordered)
        assert key['seed']==f'eff:{bed}:{arm}' and ids==key['order']==ordered
    assert len(counts)==12
    for bed in ('bsb','yer'):
        assert sum(p['bed']==bed for p in manifest['packs'])==10
        for arm in manifest['arms']:
            packs = [p for p in manifest['packs'] if p['bed']==bed and p['arm']==arm]
            n = 1 if arm in ('E1','E4') else 2
            assert len(packs)==n
            expected_counts = [100] if n==1 and bed=='bsb' else [59] if n==1 else [50,50] if bed=='bsb' else [30,29]
            assert [p['items_per_reader'] for p in packs]==expected_counts
    if 'owner39' in manifest['reader_counts']:
        packs=[p for p in manifest['packs'] if p['bed']=='owner39']
        assert len(packs)==manifest['reader_counts']['owner39']==8
        assert {(p['arm'],p['reader']) for p in packs}=={(a,r) for a in ('E0a','E0b','E2','E3') for r in ('r1','r2')}
    return {'isolation':'ok','pack_files':len(listed),'images':images,'packs':len(manifest['packs']),
            'reader_counts':manifest['reader_counts'],'id_alignment':'ok','raster_dimensions':'ok','sha256':'ok'}


if __name__=='__main__':
    print(json.dumps(validate(), indent=2))
