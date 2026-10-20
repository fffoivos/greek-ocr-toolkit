#!/usr/bin/env python3
"""T17: explicit --run reads only frozen owner-approved 1860/1870/1880 pages.

--prepare and the default evidence rebuild are offline. No retries or .git writes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.harvest.readers import Readers, atomic, read_jsonl
from scripts.harvest.montage_controls import git_state, audit_git

ROOT = REPO / 'docs/records/harvest/round1'
OUT = ROOT / 'reads_d1'
BULK = REPO / 'docs/harvest/harvest_big/round1'
GOOGLE = BULK / 'google'
DECADES = (1860, 1870, 1880)
ENGINES = ('vision', 'docai')


def sha(path):
    with _data_input(Path(path)).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def frozen(path, value):
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError('frozen T17 input changed: ' + str(path))
    else:
        atomic(path, value)


def select_pages(selection, manifest):
    books = {b['book']: b for b in selection['books']}
    return sorted((dict(p, book_info={k: books[p['book']][k] for k in ('key', 'title', 'year', 'decade')})
                   for p in manifest['pages'] if p.get('harvest_accepted') is True
                   and books[p['book']]['decade'] in DECADES),
                  key=lambda p: (p['book_info']['decade'], p['book_info']['year'], p['book'], p['page']))


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    if not (OUT / 'git_before.json').exists():
        atomic(OUT / 'git_before.json', git_state())
    selection = json.loads((_data_input(ROOT / 'selection.json')).read_text())
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    if manifest['selection_sha256'] != sha(ROOT / 'selection.json'):
        raise ValueError('selection/manifest binding changed')
    bindings = json.loads((REPO / 'docs/records/harvest/page_reads_v1/sample.json').read_text())['bindings']
    pages = []
    for p in select_pages(selection, manifest):
        path = REPO / p['image']
        digest = sha(path)
        if digest != p['gate']['image_sha256'] or p['gate']['dpi'] != 200 or not p['gate']['grayscale']:
            raise ValueError('native page hash/render binding changed')
        with Image.open(path) as im:
            if im.mode != 'L' or im.format != 'PNG':
                raise ValueError('native 200 dpi grayscale PNG required')
            width, height = im.size
        pages.append(dict(id=f"{p['book_info']['key']}-p{p['page']:06d}", book=p['book'],
                          **p['book_info'], page=p['page'], volume=p['volume'], volume_page=p['volume_page'],
                          image=p['image'], image_sha256=digest, width=width, height=height,
                          dpi=200, grayscale=True, pdf=p['pdf'], pdf_sha256=p['pdf_sha256'],
                          column_bands=p['gate']['pilot_gate'].get('column_bands', [])))
    if not pages or len({p['image_sha256'] for p in pages}) != len(pages):
        raise ValueError('empty or duplicate page plan')
    # Do not knowingly repeat a previously read native page in a new namespace.
    for p in pages:
        for e in ENGINES:
            old = REPO / f"docs/harvest/harvest_big/page_reads_v1/google/parsed/{e}/{p['image_sha256']}.json"
            if old.exists():
                raise ValueError('historical page cache found; explicit reuse needed')
    plan = dict(schema='t17-round1-page-read-plan-1', owner_approval='2026-10-14; only accepted round-1 pages, decades 1860/1870/1880',
                selection_sha256=sha(ROOT / 'selection.json'), manifest_sha256=sha(ROOT / 'manifest.json'),
                t15_sample_sha256=sha(REPO / 'docs/records/harvest/page_reads_v1/sample.json'),
                bindings=bindings, pages=pages, page_count=len(pages),
                by_decade=dict(Counter(str(p['decade']) for p in pages)), max_calls=2*len(pages),
                max_cost_usd=.003*len(pages), cap_usd=2., automatic_retries=False, crop_calls=0)
    if plan['max_cost_usd'] > 2 or plan['max_calls'] > 1000:
        raise ValueError('authorized cost/call ceiling exceeded')
    frozen(OUT / 'plan.json', plan)
    return plan


def run(plan):
    readers = Readers(GOOGLE, cap=2, project=plan['bindings']['vision']['user_project'],
                      processor=plan['bindings']['docai']['processor'])
    readers.budget.max_calls = plan['max_calls']
    if any(getattr(readers, e).binding() != plan['bindings'][e] for e in ENGINES):
        raise ValueError('reader binding differs from T15')
    iterator = iter(plan['pages'])

    def call(p):
        image = REPO / p['image']
        if sha(image) != p['image_sha256']:
            raise ValueError('page changed before call')
        pair = readers.pair(image)
        if any(v['status'] != 'ok' for v in pair.values()):
            raise RuntimeError('reserved request failed; no retry: ' + p['id'] + ' ' +
                               str({e: v.get('error_class', v['status']) for e, v in pair.items()}))
        return p['id']

    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {pool.submit(call, next(iterator)) for _ in range(min(3, len(plan['pages'])))}
            completed = 0
            while pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                # Inspect all completions before scheduling additional work.
                ids = [f.result() for f in done]
                for ident in ids:
                    completed += 1
                    print(f'read {completed}/{plan["page_count"]} {ident}', flush=True)
                    p = next(iterator, None)
                    if p is not None:
                        pending.add(pool.submit(call, p))
    finally:
        receipt = readers.budget.receipt()
        receipt['pricing_verified_utc'] = '2026-10-14'
        atomic(OUT / 'cost_receipt.json', receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    plan = prepare()
    if args.run:
        run(plan)
    elif not args.prepare:
        from scripts.harvest.build_round1_reads import build
        build(plan)
    print(json.dumps({k: plan[k] for k in ('page_count', 'by_decade', 'max_calls', 'max_cost_usd')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
