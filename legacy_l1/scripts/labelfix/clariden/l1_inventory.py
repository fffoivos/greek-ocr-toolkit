"""No image decode: verify C1 inventory, inventory 33,200 new crops and parity crops."""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import time

from scripts.labelfix.clariden.l1_common import canonical, rows, sha256, write_json
from scripts.labelfix.clariden.r1_common import crop_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('binding', 'c1-inventory', 'crop-root', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    assert sha256(a.c1_inventory) == '4dfb7e8e72675c7b0fa415d43a55d082d04b05cd7d6f79f95c6f7bcf51c3da88'
    old = {r['crop']: r for r in rows(a.c1_inventory)}
    assert len(old) == 91469
    selection = list(rows(a.binding / 'selection.jsonl'))
    missing, mismatch = [], []
    counts, waves = Counter(), Counter()
    dest = a.out / 'L1_crop_inventory.jsonl.gz'
    with gzip.open(dest, 'xt', encoding='utf-8', compresslevel=3) as f:
        for r in selection:
            p = crop_path(r['crop'], a.crop_root, 'e3')
            if not p.is_file():
                missing.append(r['crop'])
                continue
            digest, size = sha256(p), p.stat().st_size
            previous = old.get(r['crop'])
            if previous and (size != previous['bytes'] or digest != previous['sha256']):
                mismatch.append(r['crop'])
            counts['c1_reused' if previous else 'new_selection'] += 1
            counts['bytes'] += size
            counts['present'] += 1
            waves[r['wave']] += 1
            f.write(canonical(dict(crop=r['crop'], path=str(p), bytes=size, sha256=digest,
                                   inventory_origin='C1' if previous else 'L1_new_33200')) + '\n')
            if counts['present'] % 10000 == 0:
                print(f'INVENTORY {counts["present"]}/{len(selection)}', flush=True)
    parity_missing = []
    parity_sha = json.loads((a.binding / 'parity_crop_sha256.json').read_text())
    for r in rows(a.binding / 'parity_selection.jsonl'):
        p = crop_path(r['crop'], a.crop_root, 'e3')
        if not p.is_file():
            parity_missing.append(r['crop'])
        elif sha256(p) != parity_sha[r['id']]:
            mismatch.append(r['crop'])
    receipt = dict(schema='l1-crop-inventory-v1', selected=len(selection), counts=dict(counts),
        by_wave=dict(waves), missing=missing, mismatch=mismatch, parity_missing=parity_missing,
        parity_present=32-len(parity_missing), c1_inventory_sha256=sha256(a.c1_inventory),
        selection_sha256=sha256(a.binding / 'selection.jsonl'), inventory_sha256=sha256(dest),
        elapsed_seconds=time.monotonic()-started, no_crop_transfer=True, no_image_decode=True,
        complete=not (missing or mismatch or parity_missing))
    write_json(a.out / 'inventory_receipt.json', receipt)
    print(canonical(receipt), flush=True)
    if missing or mismatch or parity_missing:
        raise SystemExit('STOP: required crops missing/changed; do not transfer crops')
    assert counts['c1_reused'] == 91469 and counts['new_selection'] == 33200


if __name__ == '__main__':
    main()
