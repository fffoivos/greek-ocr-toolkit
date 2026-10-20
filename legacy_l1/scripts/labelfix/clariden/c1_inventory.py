"""Read-only existence/hash inventory of selected E3-staged crops; no image decode."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import time

from c1_common import crop_path, read_jsonl, sha256, write_json


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selection', type=Path, required=True)
    ap.add_argument('--crop-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    started = time.time()
    counts, waves, missing = Counter(), Counter(), []
    inventory = a.out / 'C1_crop_inventory.jsonl.gz'
    with gzip.open(inventory, 'xt', encoding='utf-8', compresslevel=3) as f:
        for r in read_jsonl(a.selection):
            p = crop_path(r['crop'], a.crop_root, 'e3')
            counts['selected'] += 1
            if not p.is_file():
                missing.append(r['crop'])
                continue
            size = p.stat().st_size
            f.write(json.dumps(dict(crop=r['crop'], path=str(p), bytes=size, sha256=sha256(p))) + '\n')
            counts['present'] += 1
            counts['bytes'] += size
            waves[r['wave']] += 1
    summary = dict(selection_sha256=sha256(a.selection), counts=counts, by_wave=waves,
                   missing=missing, elapsed_seconds=time.time()-started,
                   inventory_sha256=sha256(inventory),
                   policy='Reuse E3 staged crops; no data transferred when missing is empty')
    write_json(a.out / 'summary.json', summary)
    print(json.dumps(summary), flush=True)
    return bool(missing)


if __name__ == '__main__':
    raise SystemExit(main())
