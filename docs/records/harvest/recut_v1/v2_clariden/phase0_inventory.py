"""Read-only population/page inventory and seeded crop custody check for T6f."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import socket
import subprocess

SEED = 20261017
REMOTE = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def jsonl(path, values):
    with Path(path).open('w') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + '\n')


def key(row):
    crop = Path(row['crop'])
    page = re.fullmatch(r'p(\d+)-l\d+\.png', crop.name)
    if not page:
        raise ValueError(crop)
    return row['wave'], crop.parent.name, int(page[1])


def population(root, remote=False):
    base = root / ('collection_v2' if remote else 'docs/harvest/collection/v2')
    result = {}
    for split in ('train', 'test'):
        path = base / f'import_real_v2_{split}.jsonl'
        data = rows(path)
        for r in data:
            assert r['split'] == ('train' if split == 'train' else 'reserved')
            r['import_split'] = r['split']
            r['split'] = split
        ids = sorted(r['id'] for r in data)
        assert len(set(ids)) == len(ids)
        result[split] = dict(lines=len(data), per_wave=dict(sorted(Counter(r['wave'] for r in data).items())),
                             ids_sha256=hashlib.sha256(('\n'.join(ids)+'\n').encode()).hexdigest(),
                             manifest_sha256=sha(path))
        yield split, data, result[split]


def local(args):
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    grouped, summary, all_rows = {}, {}, []
    for split, data, receipt in population(args.root):
        summary[split] = receipt
        for r in data:
            assert r['split'] == split
            grouped.setdefault(key(r), []).append(r)
        all_rows.extend(data)
    assert len({r['id'] for r in all_rows}) == len(all_rows)
    scan = { (r['wave'], r['doc'], r['page']): r for r in rows(args.scan) }
    assert set(grouped) <= set(scan), f'missing scan pages: {set(grouped)-set(scan)}'
    pages = []
    for k in sorted(grouped):
        s = scan[k]
        p = args.root / 'docs/harvest' / s['path']
        assert p.stat().st_size == s['bytes'], str(p)
        pages.append(dict(s, local_path=str(p), line_count=len(grouped[k]),
                          split_counts=dict(Counter(r['split'] for r in grouped[k])),
                          needed_for_masking=k[0] != 'parliament'))
    summary.update(pages=len(pages), page_bytes=sum(p['bytes'] for p in pages),
                   non_parliament_pages=sum(p['needed_for_masking'] for p in pages),
                   non_parliament_page_bytes=sum(p['bytes'] for p in pages if p['needed_for_masking']),
                   dev='out of scope', seed=SEED, scan_sha256=sha(args.scan),
                   host=socket.gethostname(),
                   code_tree_sha=subprocess.check_output(['git', 'rev-parse', '63c640a3'], text=True).strip())
    sample = random.Random(SEED).sample(sorted(all_rows, key=lambda r:r['id']), 2000)
    # Independently stratified 50 across every non-parliament wave; no codec exclusion.
    rng = random.Random(SEED)
    waves = sorted({r['wave'] for r in all_rows if r['wave'] != 'parliament'})
    mock = []
    for i, wave in enumerate(waves):
        pool = sorted((r for r in all_rows if r['wave'] == wave), key=lambda r:r['id'])
        mock.extend(rng.sample(pool, 50//len(waves) + (i < 50 % len(waves))))
    wanted = {r['id'] for r in sample + mock}
    admitted = {}
    admitted_hashes = {}
    for wave in sorted({r['wave'] for r in all_rows}):
        path = args.root / 'docs/harvest' / wave / 'admitted.jsonl'
        admitted_hashes[wave] = sha(path)
        for r in rows(path):
            if r['id'] in wanted:
                assert r['id'] not in admitted
                admitted[r['id']] = r
    assert set(admitted) == wanted
    def bind(r):
        a = admitted[r['id']]
        assert r['crop'] == a['crop_path'], r['id']
        actual = sha(args.root / r['crop'])
        assert actual == a['crop_sha256'], r['id']
        return dict(r, crop_sha256=actual, crop_bbox=a['crop_bbox'], admitted_split=a['split'])
    bound = [bind(r) for r in sample]
    jsonl(out / 'sample_2000.jsonl', bound)
    jsonl(out / 'mock_50.jsonl', [bind(r) for r in mock])
    jsonl(out / 'pages.jsonl', pages)
    summary['admitted_sha256'] = admitted_hashes
    summary['sample_2000_per_split'] = dict(Counter(r['split'] for r in bound))
    summary['sample_2000_local_sha_match'] = True
    write(out / 'local_population.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k != 'admitted_sha256'}))


def remote(args):
    summary = {split: receipt for split, _, receipt in population(REMOTE, remote=True)}
    local_summary = json.loads((args.out / 'local_population.json').read_text())
    summary['full_count_match'] = all(summary[s]['lines'] == local_summary[s]['lines'] for s in ('train','test'))
    summary['full_id_set_match'] = all(summary[s]['ids_sha256'] == local_summary[s]['ids_sha256'] for s in ('train','test'))
    expected = {r['id']:r for r in rows(args.out / 'sample_2000.jsonl')}
    actual = {}
    for split, data, _ in population(REMOTE, remote=True):
        for r in data:
            if r['id'] in expected:
                e = expected[r['id']]
                assert (r['crop'], r['split'], r['wave']) == (e['crop'],e['split'],e['wave'])
                crop = REMOTE / 'collection_v2/crops' / r['wave'] / Path(r['crop']).parent.name / Path(r['crop']).name
                actual[r['id']] = sha(crop)
    mismatches = [i for i in expected if actual.get(i) != expected[i]['crop_sha256']]
    summary.update(host=socket.gethostname(), code_tree_sha=local_summary['code_tree_sha'],
                   sample_size=len(expected), sample_crops_hashed=len(actual), sample_mismatches=mismatches)
    write(args.out / 'remote_population.json', summary)
    print(json.dumps(summary))
    assert summary['full_count_match'] and summary['full_id_set_match'] and not mismatches


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=('local', 'remote'))
    p.add_argument('--root', type=Path)
    p.add_argument('--scan', type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    globals()[args.mode](args)
