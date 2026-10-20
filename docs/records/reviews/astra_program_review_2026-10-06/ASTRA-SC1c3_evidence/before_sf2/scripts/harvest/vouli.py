#!/usr/bin/env python3
"""T21: full local Vouli render/gate, explicitly authorized DocAI reads, admission.

All modes except --run are offline. Immutable plans and image-hash reservations
make interruption safe; neither retries nor Vision readers are used.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait, FIRST_COMPLETED
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import random
import statistics
import threading
import time

import numpy as np
from PIL import Image
import pypdfium2 as pdfium

from greekocr.harvest import admission
from greekocr.harvest.pipeline import FrozenStack, crop_features, polygon_crop
from greekocr.harvest.readers import Budget, Readers, atomic, read_jsonl
from greekocr.harvest.page_reads import _response_geometry
from greekocr.readers.services.google_docai import DocAIReader
from scripts.harvest import round1
from scripts.harvest.round1_reads import frozen
from scripts.harvest.build_round1_reads_rest import make_rows, cohort_summary
from scripts.harvest.admit_round1 import contact_sheets, stats, write_jsonl
from scripts.harvest import compile_page_reads as compiler

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'docs/harvest/vouli'
BULK = REPO / 'docs/harvest/harvest_big/vouli'
GOOGLE = BULK / 'google'
CAP = 2.50
SOURCE = 'vouli_parliament_1850s'
ADMISSION_SHA = 'e32ba0429908bc405e0b2c2bb26d97cdec5f923733d708deaea018b65cb90a50'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative(path):
    return str(Path(path).relative_to(REPO))


def check_frozen():
    if sha(REPO / 'greekocr/harvest/admission.py') != ADMISSION_SHA:
        raise ValueError('T20 admission module changed; stop')
    if (REPO / '.git/HEAD').read_text().strip() != 'ref: refs/heads/main':
        raise ValueError('T21 requires main')
    round1.load_gate()


def select_holdout(books, seed=20261015):
    """Whole-book seeded draw before reading; includes all 107 input books."""
    ordered = sorted(books, key=lambda b: b['key'])
    if len({b['key'] for b in ordered}) != len(ordered):
        raise ValueError('duplicate book key')
    if len(ordered) < 16:
        raise ValueError('need at least sixteen books')
    chosen = random.Random(seed).sample(ordered, 16)
    return sorted([dict(book_key=b['key'], sha256=b['book'], title=b['title'],
                        year=b['year'], decade=b['decade'],
                        split='dev' if i < 4 else 'test')
                   for i, b in enumerate(chosen)], key=lambda b: b['book_key'])


def gate_image(image_path, stack, gate, limits):
    """Exactly T16 gate_pdf after rendering: same items, features and limits."""
    start = time.perf_counter()
    with Image.open(image_path) as source:
        image = source.copy()
    gray = np.asarray(image)
    result = stack.run(image_path, gray)
    pg = gate.page_gate(gray, result['items'],
                        bend_fired=any(f['side'] != 0 for f in result['harvest_bend']))
    boxes = [gate.bbox(item['polygon']) for item in result['items']]
    features = [crop_features(polygon_crop(image, item['polygon']))
                for item, box in zip(result['items'], boxes)
                if gate.crop_gate(box, boxes, pg, image.size, item,
                                  long_complete=True)['accepted']]
    feat = round1.feature_summary(features)
    suppression = Counter(q.get('removal', 'unknown') for q in result.get('removed', []))
    flags, ratio = round1.quality_flags(feat, suppression, len(result['items']), limits)
    return dict(accepted=pg['accepted'] and not flags, flags=pg['flags'] + flags,
                pilot_gate=pg, supplemental_quality_flags=flags, features=feat,
                feature_rows=len(features), faint_suppression_share=ratio,
                suppression_reasons=dict(suppression), lines=len(result['items']),
                gate_source_sha256=round1.GATE_SHA,
                stack_source_sha256=stack.source_sha256, stack_model_sha256=stack.model_sha256,
                image_sha256=sha(image_path), dpi=200, grayscale=True,
                seconds=time.perf_counter() - start)


def select_pages(manifest, previous_hashes=()):
    """All literal gate accepts; page identities are distinct from image hashes."""
    ids, pages = set(), []
    previous_hashes = set(previous_hashes)
    for p in manifest:
        if p['id'] in ids:
            raise ValueError('duplicate page identity')
        ids.add(p['id'])
        if p['gate']['accepted'] is not True:
            continue
        key = p['image_sha256']
        if key not in previous_hashes:
            pages.append(p)
    return pages


def unique_call_pages(pages):
    """Identical native rasters share one provider response, never a second call."""
    unique = {}
    for p in pages:
        unique.setdefault(p['image_sha256'], p)
    return list(unique.values())


def init_gate_worker(limits):
    global WORKER_STACK, WORKER_GATE, WORKER_LIMITS
    WORKER_STACK = FrozenStack(round1.PILOT / 'pilot/_stack_52cee3b')
    WORKER_GATE, WORKER_LIMITS = round1.load_gate(), limits


def gate_book(b):
    pages = []
    with pdfium.PdfDocument(REPO / b['pdf']) as doc:
        for number in range(1, len(doc) + 1):
            ident = f"{b['key']}-p{number:06d}"
            image_path = BULK / 'images' / f"{b['key']}-{number:06d}.png"
            receipt_path = OUT / 'gates' / (ident + '.json')
            if receipt_path.exists():
                p = json.loads(receipt_path.read_text())
                if p['image_sha256'] != sha(image_path) or p['pdf_sha256'] != b['pdf_sha256']:
                    raise ValueError('resume page hash changed')
            else:
                image_path.parent.mkdir(parents=True, exist_ok=True)
                with closing(doc[number - 1]) as page:
                    bitmap = page.render(scale=200 / 72, grayscale=True)
                    image = bitmap.to_pil().copy().convert('L')
                    bitmap.close()
                image.save(image_path, compress_level=1)
                g = gate_image(image_path, WORKER_STACK, WORKER_GATE, WORKER_LIMITS)
                p = dict(b, id=ident, page=number, volume=None, volume_page=number,
                         image=relative(image_path), image_sha256=sha(image_path),
                         width=image.width, height=image.height, dpi=200, grayscale=True,
                         read_batch='vouli', gate=g, harvest_accepted=g['accepted'])
                atomic(receipt_path, p)
            pages.append(p)
    return pages


def render_gate():
    check_frozen()
    OUT.mkdir(parents=True, exist_ok=True)
    if not (OUT / 'git_before.json').exists():
        atomic(OUT / 'git_before.json', round1.git_snapshot())
    sources = BULK / 'sources.json'
    inputs = json.loads(sources.read_text())['books']
    pdfs = {p.stem for p in (BULK / 'pdf').glob('*.pdf')}
    if len(inputs) != 107 or pdfs != {b['sha256'] for b in inputs}:
        raise ValueError('exact 107-PDF source scope mismatch')
    books = []
    for b in sorted(inputs, key=lambda b: b['sha256']):
        digest = b['sha256']
        path = BULK / 'pdf' / (digest + '.pdf')
        if sha(path) != digest or b['licence'] != 'CC-BY-4.0':
            raise ValueError('PDF hash or licence changed')
        r = b['source_receipt']
        with pdfium.PdfDocument(path) as doc:
            count = len(doc)
        year = r['year']
        books.append(dict(book=digest, key=digest[:12], title=r['title'], year=year,
                          decade=year // 10 * 10 if year is not None else None,
                          pdf=relative(path), pdf_sha256=digest, page_count=count,
                          source_url=b['source_url'], attribution=b['attribution'],
                          licence=b['licence'], source=SOURCE, origin='vouli'))
    frozen(OUT / 'books.json', books)
    frozen(OUT / 'holdout_books.json', select_holdout(books))
    limits = json.loads((round1.OUT / 'selection.json').read_text())['quality_limits']
    manifest, index = [], 0
    total = sum(b['page_count'] for b in books)
    with ProcessPoolExecutor(max_workers=3, mp_context=multiprocessing.get_context('spawn'),
                             initializer=init_gate_worker, initargs=(limits,)) as pool:
        futures = [pool.submit(gate_book, b) for b in books]
        for future in as_completed(futures):
            pages = future.result()
            manifest.extend(pages)
            index += len(pages)
            print(f"render/gate {index}/{total}; accepted {sum(p['harvest_accepted'] for p in manifest)}", flush=True)
    manifest.sort(key=lambda p: (p['book'], p['page']))
    frozen(OUT / 'manifest.json', manifest)
    previous = read_jsonl(REPO / 'docs/harvest/round1/records_all.jsonl')
    previous_hashes = {r['image_sha256'] for r in previous}
    pages = select_pages(manifest, previous_hashes)
    accepted = sum(p['harvest_accepted'] for p in manifest)
    binding = json.loads((round1.OUT / 'reads_d1/plan.json').read_text())['bindings']['docai']
    call_pages = unique_call_pages(pages)
    shared = defaultdict(list)
    for p in pages:
        shared[p['image_sha256']].append(p['id'])
    if len(call_pages) * .0015 > CAP:
        raise ValueError('all accepted pages exceed USD 2.50; stop before reads')
    plan = dict(schema='t21-vouli-plan-1', binding=binding, pages=pages,
                page_count=len(pages), pages_rendered=total, pages_accepted=accepted,
                already_read_hashes=sorted(previous_hashes & {p['image_sha256'] for p in manifest}),
                max_calls=len(call_pages), cap_usd=CAP, max_cost_usd=len(call_pages) * .0015,
                shared_image_groups={key: ids for key, ids in shared.items() if len(ids) > 1},
                quality_limits=limits, gate_sha256=round1.GATE_SHA,
                admission_sha256=ADMISSION_SHA, seed=20261015, automatic_retries=False,
                vision_calls=0, owner_approval='T21, 15 Oct; read every gate-accepted page; no owner look',
                inputs={relative(p): sha(p) for p in (sources, OUT / 'books.json', OUT / 'holdout_books.json',
                    OUT / 'manifest.json', round1.OUT / 'selection.json', round1.OUT / 'reads_d1/plan.json')})
    frozen(OUT / 'plan.json', plan)
    print(json.dumps({k: plan[k] for k in ('pages_rendered', 'pages_accepted', 'page_count', 'max_cost_usd')}), flush=True)
    return plan


class VouliReaders(Readers):
    def __init__(self, plan, root=GOOGLE):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.budget = Budget(self.root / 'budget.jsonl', cap=plan['cap_usd'])
        self.budget.max_calls = min(plan['max_calls'], int(plan['cap_usd'] / .0015))
        b = plan['binding']
        self.docai = DocAIReader(b['project'], b['location'], b['processor'], version=b['version'],
                                user_project=b['user_project'],
                                language_hints=b['options']['ocrConfig']['hints']['languageHints'],
                                enable_symbol=b['options']['ocrConfig']['enableSymbol'],
                                receipts_dir=self.root / 'docai')
        self.rate_lock, self.last_docai = threading.Lock(), 0.0
        if self.docai.binding() != b:
            raise ValueError('T19 DocAI binding changed')

    def call(self, engine, image):
        if engine != 'docai':
            raise ValueError('T21 forbids other readers')
        return super().call(engine, image)

    def _call_locked(self, engine, image, key, result_path):
        if not result_path.exists() and any(r['crop_sha256'] == key for r in read_jsonl(self.root / 'docai/ledger.jsonl')):
            raise RuntimeError('historical provider attempt without parsed cache; no re-read')
        result = super()._call_locked(engine, image, key, result_path)
        if result['status'] == 'ok' and (result['binding'] != self.docai.binding() or result['image_sha256'] != key):
            raise ValueError('cached response binding changed')
        return result


def load_plan():
    check_frozen()
    plan = json.loads((OUT / 'plan.json').read_text())
    for p, digest in plan['inputs'].items():
        if sha(REPO / p) != digest:
            raise ValueError('frozen input changed: ' + p)
    return plan


def run(plan):
    readers = VouliReaders(plan)
    call_pages = unique_call_pages(plan['pages'])
    iterator = iter(call_pages)
    def call(p):
        if sha(REPO / p['image']) != p['image_sha256']:
            raise ValueError('page changed before request')
        result = readers.call('docai', REPO / p['image'])
        return p['id'], result['status'], result.get('error_class')
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {pool.submit(call, next(iterator)) for _ in range(min(3, len(call_pages)))}
            completed = 0
            while pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                results = [f.result() for f in done]
                if any(status != 'ok' for _, status, _ in results):
                    raise RuntimeError('reserved request failed; no retry: ' + str(results))
                for ident, status, error in results:
                    completed += 1
                    if completed % 10 == 0 or completed == len(call_pages):
                        print(f"read unique image {completed}/{len(call_pages)} {ident} {status}", flush=True)
                    p = next(iterator, None)
                    if p is not None:
                        pending.add(pool.submit(call, p))
    finally:
        cost = readers.budget.receipt()
        cost.update(prices={'docai': .0015}, pricing_sources=['https://cloud.google.com/products/document-ai/pricing'],
                    pricing_basis='same T19 USD 1.50/1000-page list-price estimate; not invoice readback')
        atomic(OUT / 'cost_receipt.json', cost)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['render-gate', 'run', 'build', 'validate', 'publish'])
    mode = parser.parse_args().mode
    if mode == 'render-gate':
        render_gate()
    elif mode == 'run':
        run(load_plan())
    else:
        from scripts.harvest.vouli_outputs import build, validate, publish
        {'build': build, 'validate': validate, 'publish': publish}[mode](load_plan())


if __name__ == '__main__':
    main()
