"""Freeze S8b document membership without inspecting labels or detector errors."""
from greekocr.ops.data_root import input_path as _data_input
import collections
import gzip
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / 'docs/records/labelfix/spellcheck/S8_DEV'
OUT = DEV / 's8b'
SEED = 'S8b-split-20261017'
WAVES = ('parliament', 'round1', 'round2', 'mixed', 'vouli')


def main():
    rows = [json.loads(x) for x in gzip.decompress((_data_input(DEV/'evidence/dev_truth.jsonl.gz')).read_bytes()).decode().splitlines()]
    cut = [r for r in rows if r.get('type') == 'item' and not r['control'] and r['in_cut']]
    membership, counts = {}, {}
    for wave in WAVES:
        rr = [r for r in cut if r['wave'] == wave]
        docs = sorted({r['line_id'].split('-p')[0] for r in rr})
        random.Random(SEED + ':' + wave).shuffle(docs)
        for i, doc in enumerate(docs):
            assert doc not in membership, 'document crosses waves'
            membership[doc] = dict(wave=wave, half='TUNE' if i < len(docs)//2 else 'JUDGE')
        counts[wave] = {half: dict(documents=sum(membership[d]['half'] == half for d in docs),
            cards=sum(membership[r['line_id'].split('-p')[0]]['half'] == half for r in rr))
            for half in ('TUNE', 'JUDGE')}
    result = dict(seed=SEED, method='sorted documents; Python Random(seed + colon + wave).shuffle; first floor(n/2) TUNE',
        truth_sha256=hashlib.sha256((_data_input(DEV/'evidence/dev_truth.jsonl.gz')).read_bytes()).hexdigest(),
        documents=membership, counts=counts)
    OUT.mkdir(exist_ok=True)
    path = OUT/'split.json'
    data = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n'
    if path.exists():
        assert path.read_text() == data, 'split is immutable'
    else:
        path.write_text(data)
    print(json.dumps(dict(counts=counts, split_sha256=hashlib.sha256(path.read_bytes()).hexdigest()), indent=2))


if __name__ == '__main__':
    main()
