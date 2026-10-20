"""Offline KR1b rebuild. Never overwrite the VOID c2 evidence or an existing c2b."""
import sys
sys.dont_write_bytecode = True
import json
import random
import hashlib
import shutil
import os
from build import HERE, BED, PACK_ROOT, rows, sha, dump, jsonl, io_guard

SEED = 'kr1b:kosmo:c2b'

def snapshot(directory):
    return {str(p.relative_to(directory)): dict(sha256=sha(p), size=p.stat().st_size,
            mtime_ns=p.stat().st_mtime_ns, inode=p.stat().st_ino)
            for p in sorted(directory.rglob('*')) if p.is_file()}

def main():
    io_guard()
    source, target = BED / 'c2', BED / 'c2b'
    assert not target.exists(), 'Refuse to overwrite c2b'
    before = snapshot(source)
    keypath = HERE / 'keys/kosmo2.json'
    key = json.loads(keypath.read_text())
    assert 'c2b' not in key['readers']
    original_key_sha = sha(keypath)
    cards = rows(source / 'cards.jsonl')
    assert len(cards) == 55
    assert [c['card_id'] for c in cards] == key['readers']['c2']
    assert sum(key['items'][c['card_id']]['control'] for c in cards) == 5
    batch = sorted(cards, key=lambda c: c['card_id'])
    random.Random(SEED).shuffle(batch)
    assert [c['card_id'] for c in batch] != key['readers']['c2']
    existing = set(key['items'])
    for p in PACK_ROOT.glob('*/*/cards.jsonl'):
        existing.update(c['card_id'] for c in rows(p))
    (target / 'crops').mkdir(parents=True)
    public, custody, items = [], [], {}
    for c in batch:
        meta = key['items'][c['card_id']]
        iid = 'k' + hashlib.sha256((SEED + ':' + meta['line_id']).encode()).hexdigest()[:10]
        assert iid not in existing and iid not in items
        src, dst = source / c['crop'], target / c['crop']
        assert sha(src) == meta['crop_sha256']
        shutil.copyfile(src, dst)
        assert sha(dst) == meta['crop_sha256'] and dst.stat().st_nlink == 1
        assert not dst.is_symlink() and not os.path.samefile(src, dst)
        public.append(dict(c, card_id=iid))
        items[iid] = dict(meta)
        custody.append(dict(opaque_id=iid, previous_opaque_id=c['card_id'],
                            source=str(src), destination=str(dst), sha256=sha(dst)))
    jsonl(target / 'cards.jsonl', public)
    jsonl(HERE / 'pack_inventory/c2b.cards.jsonl', public)
    replacement = dict(bed='kosmo2', protocol='bsb', seed=SEED, replaces='c2',
                       readers={'c2b': [c['card_id'] for c in public]}, items=items)
    dump(HERE / 'keys/kosmo2_c2b.json', replacement)
    dump(HERE / 'keys/c2b_crop_custody.json', custody)
    # Additive assignment preserves all original c1/c2 mappings for evidence.
    key['readers']['c2b'] = replacement['readers']['c2b']
    key['items'].update(items)
    dump(keypath, key)
    from reference_adapter import closure
    result = closure(target, compatible=True)
    assert result['ok'], result['violations']
    dump(HERE / 'scan/c2b.closure.json', result)
    after = snapshot(source)
    assert before == after, 'c2 evidence changed'
    dump(HERE / 'c2b_build_receipt.json', dict(seed=SEED, order_base='c2 opaque-id ascending',
        items=55, bed_cards=50, controls=5, network='OFF', readers_started=0,
        original_key_sha256=original_key_sha, c2_unchanged=True, c2_snapshot=before,
        assignment_sha256=sha(HERE / 'keys/kosmo2_c2b.json'),
        manifest_sha256=sha(BED / 'MANIFEST.c2b.json'), closure='clean',
        scanner_changed=False, source_items_preserved=True))
    print('c2b: 55 items; closure: clean; c2 unchanged')

if __name__ == '__main__':
    main()
