#!/usr/bin/env python3
"""T19: frozen unread accepted pages; explicitly authorized DocAI-only calls.

Default/--prepare are offline. Reservations survive interruptions; no retries.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import json
from pathlib import Path
import sys
import threading

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.harvest.readers import Budget, Readers, atomic, read_jsonl
from greekocr.readers.services.google_docai import DocAIReader
from scripts.harvest.round1_reads import sha, frozen, ROOT, BULK, GOOGLE
from scripts.harvest.montage_controls import git_state

OUT = ROOT / 'reads_rest'
D1 = ROOT / 'reads_d1/records.jsonl'
CAP = 3.0


def select_pages(manifest, books, previous):
    """Subtract page identities before accepting only the owner's stated scope."""
    already = {r['page_id'] for r in previous}
    seen, selected = set(), []
    for p in manifest:
        if p.get('harvest_accepted') is not True:
            continue
        b = books[p['book']]
        ident = f"{b['key']}-p{p['page']:06d}"
        if ident in seen:
            raise ValueError('duplicate accepted page identity: ' + ident)
        seen.add(ident)
        if ident in already:
            continue
        if not (p['origin'] == 'rescue' or
                p['origin'] == 't16' and b['decade'] in (1890, 1900, 1910, 1920, 1930)):
            raise ValueError('unread accepted page outside authorized scope: ' + ident)
        selected.append(dict(p, id=ident, book_info={k: b[k] for k in ('key', 'title', 'year', 'decade')}))
    return sorted(selected, key=lambda p: (p['book_info']['decade'], p['book_info']['year'], p['book'], p['page']))


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    if not (OUT / 'git_before.json').exists():
        atomic(OUT / 'git_before.json', git_state())
    if (REPO / '.git/HEAD').read_text().strip() != 'ref: refs/heads/main':
        raise ValueError('T19 requires the main worktree')
    selections = [ROOT / 'selection.json', ROOT / 'rescue/selection.json']
    books = {}
    for path in selections:
        for b in json.loads(path.read_text())['books']:
            if b['book'] in books and any(books[b['book']][k] != b[k] for k in ('key', 'title', 'year', 'decade')):
                raise ValueError('conflicting book metadata')
            books[b['book']] = b
    pages = []
    for p in select_pages(json.loads((ROOT / 'manifest_all.json').read_text()), books, read_jsonl(D1)):
        path = REPO / p['image']
        digest = sha(path)
        if digest != p['gate']['image_sha256'] or p['gate']['dpi'] != 200 or not p['gate']['grayscale']:
            raise ValueError('native page hash/render binding changed: ' + p['id'])
        with Image.open(path) as im:
            if im.mode != 'L' or im.format != 'PNG':
                raise ValueError('native 200 DPI grayscale PNG required')
            width, height = im.size
        pages.append(dict(id=p['id'], book=p['book'], **p['book_info'], origin=p['origin'],
                          page=p['page'], volume=p['volume'], volume_page=p['volume_page'],
                          image=p['image'], image_sha256=digest, width=width, height=height,
                          dpi=200, grayscale=True, pdf=p['pdf'], pdf_sha256=p['pdf_sha256']))
    if len(pages) != 1189 or len({p['image_sha256'] for p in pages}) != len(pages):
        raise ValueError('scope cardinality or duplicate-image mismatch')
    if set(p['image_sha256'] for p in pages) & {r['image_sha256'] for r in read_jsonl(D1)}:
        raise ValueError('native page already read in d1')
    bindings = json.loads((ROOT / 'reads_d1/plan.json').read_text())['bindings']['docai']
    plan = dict(schema='t19-docai-only-plan-1', owner_approval='2026-10-14; DocAI ONLY; unread accepted T16 1890–1930 and every rescue',
                inputs={str(p.relative_to(REPO)): sha(p) for p in [ROOT / 'manifest_all.json', D1, *selections, ROOT / 'reads_d1/plan.json']},
                binding=bindings, pages=pages, page_count=len(pages),
                by_decade=dict(Counter(str(p['decade']) for p in pages)),
                by_origin=dict(Counter(p['origin'] for p in pages)),
                max_calls=len(pages), max_cost_usd=len(pages)*.0015, cap_usd=CAP,
                automatic_retries=False, vision_calls=0, crop_calls=0)
    if plan['max_cost_usd'] > CAP:
        raise ValueError('cost ceiling exceeded')
    frozen(OUT / 'plan.json', plan)
    return plan


class DocAIOnlyReaders(Readers):
    """Reuse T17's locked call/cache implementation with a T19-only budget.

    There is no Vision reader instance. All historical ledgers are checked while
    holding the same per-image cache lock before reserving any new request.
    """
    def __init__(self, plan, root=GOOGLE):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.budget = Budget(self.root / 'budget_rest.jsonl', cap=plan['cap_usd'])
        # T19 explicitly authorizes >1000 page calls. The hard microdollar cap in
        # Budget.reserve still applies, and this batch cannot exceed its plan.
        self.budget.max_calls = min(plan['max_calls'], int(plan['cap_usd'] / .0015))
        b = plan['binding']
        self.docai = DocAIReader(b['project'], b['location'], b['processor'], version=b['version'],
                                user_project=b['user_project'],
                                language_hints=b['options']['ocrConfig']['hints']['languageHints'],
                                enable_symbol=b['options']['ocrConfig']['enableSymbol'],
                                receipts_dir=self.root / 'docai')
        self.rate_lock = threading.Lock()
        self.last_docai = 0.0
        if self.docai.binding() != b:
            raise ValueError('DocAI binding differs from T17')

    def call(self, engine, image):
        if engine != 'docai':
            raise ValueError('T19 forbids other readers')
        return super().call(engine, image)

    def _call_locked(self, engine, image, key, result_path):
        if not result_path.exists():
            historical = [r for r in read_jsonl(self.root / 'budget.jsonl')
                          if r['engine'] == engine and r['key'] == key]
            ledger = [r for r in read_jsonl(self.root / 'docai/ledger.jsonl')
                      if r['crop_sha256'] == key]
            if historical or ledger:
                # A raw success can be recovered offline by an explicit operator;
                # ambiguous prior attempts must never silently become a re-read.
                raise RuntimeError('historical attempt lacks parsed cache; no re-read: ' + key)
        result = super()._call_locked(engine, image, key, result_path)
        if result['status'] == 'ok' and (result['binding'] != self.docai.binding() or result['image_sha256'] != key):
            raise ValueError('cached response binding changed')
        return result


def run(plan):
    readers = DocAIOnlyReaders(plan)
    iterator = iter(plan['pages'])

    def call(p):
        if sha(REPO / p['image']) != p['image_sha256']:
            raise ValueError('page changed before request')
        result = readers.call('docai', REPO / p['image'])
        return p['id'], result['status'], result.get('error_class')

    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {pool.submit(call, next(iterator)) for _ in range(min(3, len(plan['pages'])))}
            completed = 0
            while pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                results = [f.result() for f in done]
                if any(status != 'ok' for _, status, _ in results):
                    raise RuntimeError('reserved request failed; no retry: ' + str(results))
                for ident, status, error in results:
                    completed += 1
                    print(f'read {completed}/{plan["page_count"]} {ident} {status}' + (f' {error}' if error else ''), flush=True)
                    p = next(iterator, None)
                    if p is not None:
                        pending.add(pool.submit(call, p))
    finally:
        receipt = readers.budget.receipt()
        receipt['pricing_verified_utc'] = '2026-10-14'
        receipt['pricing_sources'] = ['https://cloud.google.com/products/document-ai/pricing']
        receipt['prices'] = {'docai': .0015}
        atomic(OUT / 'cost_receipt.json', receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--publish', action='store_true', help='offline report, receipt and inventory after validation')
    args = parser.parse_args()
    plan = prepare()
    if args.run:
        run(plan)
    elif args.publish:
        from scripts.harvest.build_round1_reads_rest import publish
        publish(plan)
    elif not args.prepare:
        from scripts.harvest.build_round1_reads_rest import build
        build(plan)
    print(json.dumps({k: plan[k] for k in ('page_count', 'by_decade', 'by_origin', 'max_calls', 'max_cost_usd')}))


if __name__ == '__main__':
    main()
