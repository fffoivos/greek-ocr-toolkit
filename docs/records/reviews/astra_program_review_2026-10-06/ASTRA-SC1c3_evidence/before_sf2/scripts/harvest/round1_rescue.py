#!/usr/bin/env python3
"""T18: reuse the unchanged T16 acquisition/gate loop for owner rescues.

An isolated imported T16 module receives rescue output paths and this report
callback. Its fetch, gate, quality guards, slot replay and bounded replacement
loop are unchanged. Its HTTP directory points to the existing shared rate state.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import datetime as dt
import fcntl
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.harvest.round1_rescue import rescue_selection, combined_manifest, look_relative

BASE = ROOT / 'docs/harvest/round1'
OUT = BASE / 'rescue'
BIG = ROOT / 'docs/harvest/harvest_big/round1/rescue'
LOOK = ROOT / 'docs/harvest/harvest_big/round1_look'
spec = importlib.util.spec_from_file_location('t18_t16_driver', ROOT / 'scripts/harvest/round1.py')
t16 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t16)
# Load and SHA-check the actual frozen T16 gate before adapting output paths.
frozen_gate = t16.load_gate()
t16.OUT, t16.BIG = OUT, BIG
t16.load_gate = lambda: frozen_gate
read, atomic, sha = t16.read, t16.atomic, t16.sha


def verify_inputs(data):
    for path, expected in data['inputs'].items():
        if sha(ROOT / path) != expected:
            raise ValueError('rescue input changed: ' + path)


def verify_resume(data):
    """Never reuse a gate decision after its source PDF/image/receipt changed."""
    path = BIG / 'gate_results.json'
    if not path.exists():
        return
    books = {b['book']: b for b in data['books']}
    fm = t16.fetch_module()
    for p in read(path).values():
        b = books[p['book']]
        v, local = t16.locate(b, p['page'])
        if not fm.valid_receipt(p['fetch_receipt'], BIG / f"records/{b['key']}", b['catalogue'], v, local-1):
            raise ValueError('persisted rescue fetch receipt drift')
        if (sha(ROOT / p['pdf']) != p['pdf_sha256']
                or sha(ROOT / p['image']) != p['gate']['image_sha256']
                or p['gate']['gate_source_sha256'] != t16.GATE_SHA):
            raise ValueError('persisted rescue gate source drift')


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    BIG.mkdir(parents=True, exist_ok=True)
    rescues, selection = read(BASE / 'rescues.json'), read(BASE / 'selection.json')
    if len(rescues['rescued']) != 51:
        raise ValueError('T18 requires exactly 51 explicit owner rescues')
    data = rescue_selection(selection, rescues)
    data['inputs'] = {str(p.relative_to(ROOT)): sha(p) for p in
                      (BASE / 'selection.json', BASE / 'rescues.json', BASE / 'manifest.json',
                       ROOT / 'scripts/harvest/round1.py',
                       ROOT / 'scripts/harvest/_anemi_round1_fetcher.py',
                       BASE / 'pilot_core.py')}
    target = OUT / 'selection.json'
    if target.exists() and read(target) != data:
        raise ValueError('persisted rescue plan differs; refusing to change it')
    if not target.exists():
        atomic(target, data)
    if not (OUT / 'git_before.json').exists():
        atomic(OUT / 'git_before.json', t16.git_snapshot())
    # Share the lock, ledger, backoff and rate-state files themselves, not a copy.
    shared = BIG.parent / 'anemi_http'
    if not (shared / 'rate_state.json').exists():
        raise ValueError('existing T16 Anemi rate state is required')
    link = BIG / 'anemi_http'
    if not link.exists():
        link.symlink_to('../anemi_http', target_is_directory=True)
    if link.resolve() != shared.resolve():
        raise ValueError('rescue transport must share the T16 HTTP state')
    seeds = []
    for b in data['books']:
        for v in b['catalogue']['volumes']:
            source = t16.PILOT / f"harvest_big/anemi_wave3_sample_t13c/records/{b['key']}/{v['volume_id']}/viewer.json"
            target = BIG / f"records/{b['key']}/{v['volume_id']}/viewer.json"
            if source.exists():
                if read(source)['source_pdf_url'] != v['source_pdf_url']:
                    raise ValueError('pilot descriptor source mismatch')
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
                if sha(source) != sha(target):
                    raise ValueError('seeded descriptor drift')
                seeds.append(dict(source=str(source), target=str(target.relative_to(ROOT)), sha256=sha(source)))
    atomic(OUT / 'descriptor_seeds.json', seeds)
    print(json.dumps(dict(books=len(data['books']), pages_planned=sum(b['allocation'] for b in data['books']),
                          books_per_decade=dict(Counter(b['decade'] for b in data['books'])))), flush=True)
    return data


def report(data=None, gate_results=None, slots=None, state=None):
    data = data or read(OUT / 'selection.json')
    gate_results = gate_results if gate_results is not None else read(BIG / 'gate_results.json')
    slots = slots if slots is not None else read(OUT / 'slots.json')
    state = state or read(OUT / 'run_state.json')
    index = {(s['book'], a['page']): (s, a) for s in slots for a in s['chain'] if a['state'] != 'skipped'}
    pages = []
    for g in gate_results.values():
        p = copy.deepcopy(g)
        pair = index.get((g['book'], g['page']))
        p.update(selected=pair is not None, harvest_accepted=bool(pair and g['gate']['accepted']),
                 selection_disposition='selected' if pair else 'superseded_page_plan')
        if pair:
            slot, attempt = pair
            p.update(replacement=g['page'] != slot['original_page'], original_page=slot['original_page'],
                     replacement_chain=slot['chain'][:slot['chain'].index(attempt) + 1])
        else:
            p.update(replacement=False, original_page=g['page'], replacement_chain=[dict(
                page=g['page'], state='not_selected', reasons=['superseded_page_plan'], pdf_sha256=g['pdf_sha256'])])
        pages.append(p)
    pages.sort(key=lambda p: (p['book'], p['page']))
    manifest = dict(schema='t16-round1-manifest-1', origin='rescue', selection_sha256=sha(OUT / 'selection.json'),
                    pilot_gate_sha256=t16.GATE_SHA, pages=pages, slots=slots, complete=state.get('complete', False))
    accepted = [p for p in pages if p['harvest_accepted']]
    books = {b['book']: b for b in data['books']}
    reasons = Counter(f for p in pages if not p['gate']['accepted'] for f in p['gate']['flags'])
    for p in pages:
        if not p['selected']:
            reasons['superseded_page_plan'] += 1
    receipts = t16.fetch_module().receipt_rows(BIG / 'ledger.jsonl')
    latest = {(r['record_id'], r['volume_id'], r['page_index']): r for r in receipts}
    fetched = sum(r['state'] == 'saved' for r in latest.values())
    seconds = state['fetch_seconds']
    summary = dict(schema='t16-round1-summary-1', origin='rescue', complete=state.get('complete', False),
        books_in=len(books), books_out_type=0, books_out_scan=0, books_reduced=0,
        pages_planned=sum(b['allocation'] for b in books.values()), pages_fetched=fetched, pages_gated=len(pages),
        pages_accepted=len(accepted), pages_rejected=len(pages)-len(accepted),
        pages_not_selected=sum(not p['selected'] for p in pages),
        pages_failed_gate=sum(not p['gate']['accepted'] for p in pages),
        replacements=sum(p['replacement'] for p in accepted), replacement_attempts=sum(p['replacement'] for p in pages),
        exhausted_slots=sum(s['accepted_page'] is None and len(s['chain']) == len(s['candidate_pages']) for s in slots),
        failures_by_reason=dict(reasons), fetch_seconds=seconds, fetch_minutes=round(seconds/60, 2),
        throughput_pages_per_minute=round(fetched/max(.001, seconds/60), 3),
        saved_pdf_bytes=sum(r.get('bytes', 0) for r in latest.values() if r['state'] == 'saved'),
        total_seconds=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(state['started_at'])).total_seconds(),
        gate_cpu_seconds=sum(p['gate']['seconds'] for p in pages),
        pages_per_decade=dict(sorted(Counter(books[p['book']]['decade'] for p in accepted).items())),
        pages_per_book={b['book']: dict(allocated=b['allocation'], accepted=sum(p['book']==b['book'] for p in accepted),
                                      decision=b['decision']) for b in books.values()},
        allocation_policy=data['allocation_policy'], ocr_service_calls=0, network_origins=['https://anemi.lib.uoc.gr'],
        pilot_gate_sha256=t16.GATE_SHA, started_at=state['started_at'], finished_at=state.get('finished_at'))
    atomic(OUT / 'manifest.json', manifest)
    atomic(OUT / 'summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('complete', 'books_in', 'pages_fetched', 'pages_accepted',
                                             'replacements', 'fetch_minutes')}), flush=True)
    return manifest, summary


# The shared T16 loop calls this callback at stage checkpoints and completion.
t16.report = report


def publish():
    data = read(OUT / 'selection.json')
    verify_inputs(data)
    manifest, summary = report()
    if not manifest['complete']:
        raise ValueError('rescue acquisition is incomplete')
    combined = combined_manifest(read(BASE / 'manifest.json'), manifest)
    atomic(BASE / 'manifest_all.json', combined)
    books = {b['book']: b for b in data['books']}
    outputs = []
    for p in manifest['pages']:
        if not p['harvest_accepted']:
            continue
        source = ROOT / p['image']
        if sha(source) != p['gate']['image_sha256']:
            raise ValueError('accepted native PNG hash drift')
        target = LOOK / look_relative(books[p['book']], p)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Never overwrite an existing Finder image, including on resume.
        try:
            with target.open('xb') as out, source.open('rb') as inp:
                shutil.copyfileobj(inp, out)
        except FileExistsError:
            if sha(target) != sha(source):
                raise ValueError('existing Finder image differs')
        outputs.append(dict(book=p['book'], page=p['page'], path=str(target.relative_to(ROOT)), sha256=sha(target)))
    atomic(OUT / 'look_manifest.json', outputs)
    readme = LOOK / 'README.txt'
    if not readme.exists():
        with readme.open('x') as f:
            f.write('Round 1 rescue look folder (14 Oct 2026)\n\n'
                'accepted/<decade>s/RESCUED_<year>_<title40>_<id6>/pNNNN.png\n'
                'Native 200 dpi grayscale full pages; _REPL marks accepted replacements.\n'
                'Only the 51 explicit owner rescues were fetched. No Google calls.\n'
                'Existing T16 folders in the archived pilot workspace were left untouched.\n'
                'See docs/harvest/round1/RESCUE_FETCH.md and rescue/look_manifest.json.\n')
    write_report(data, manifest, summary, combined)
    return summary


def write_report(data, manifest, summary, combined):
    accepted = [p for p in manifest['pages'] if p['harvest_accepted']]
    lines = ['# T18 — owner rescue fetch', '',
        f"{summary['books_in']} explicitly rescued books; {summary['pages_planned']} planned slots. "
        f"{summary['pages_fetched']} PDFs fetched and gated; {summary['pages_accepted']} accepted; "
        f"{summary['replacements']} accepted replacements; {summary['exhausted_slots']} exhausted slots.", '',
        f"Fetch/gate chunks: **{summary['fetch_minutes']:.2f} minutes**, "
        f"{summary['throughput_pages_per_minute']:.3f} fetched pages/minute. "
        f"Physical gating: {summary['gate_cpu_seconds']:.2f} seconds. "
        'Fetch time includes the overlapping gate worker, as in T16.', '',
        'Only `rescued` was fetched. `stay_out`, `pending_owner_look_1880s` and bad-scan removals were excluded. '
        'Owner rescues override the historical type decision; faint/math books remain subject to page gating and later line review. '
        'No OCR service calls were made.', '',
        'The unchanged T16 acquisition loop uses seed 20261014, 8–95% positions, offsets 0–2, pilot exclusions '
        'and only physical neighbours +1/+2 (at most two replacement attempts). '
        'The frozen T13c page gate and T16 supplemental quality limits are unchanged. '
        f"Gate SHA-256: `{t16.GATE_SHA}`. The relative-faintness guard remains a proxy for show-through.", '',
        'Anemi HTTPS is the only permitted network origin. Credentials and cookies stay in memory. '
        'The rescue HTTP path links to the existing T16 HTTP directory, sharing its lock, transfer ledger, '
        'rate state and throttle backoff. Page receipts and SHA-bound gate results resume locally.', '',
        f"[Combined manifest](manifest_all.json): {len(combined)} accepted rows "
        f"({sum(p['origin']=='t16' for p in combined)} T16 + {len(accepted)} rescue), each tagged `origin`. "
        '[Rescue manifest](rescue/manifest.json), [summary](rescue/summary.json), '
        '[allocation](rescue/selection.json), [Finder image receipts](rescue/look_manifest.json), '
        '[offline validation](rescue/validation.json), [tests](rescue/tests.xml).', '',
        'The original Finder look folder/README was found in the archived pilot workspace, outside this repo. '
        'It was read only. New full-page native 200-DPI grayscale images are under '
        '`docs/harvest/harvest_big/round1_look/accepted/<decade>s/RESCUED_<year>_<title40>_<id6>/`; '
        '`_REPL` marks replacements. Existing folders and images are preserved.', '',
        'Offline tests cover allocation, exact T16 positions/replacements, excluded owner groups, '
        'accepted-only union provenance/duplicates and Finder names. The folder-name rule was replayed '
        'against all 79 original accepted-book names. Final validation checks every fetch receipt, '
        'PDF/PNG hash, source PDF raster, gate source/quality guard, slot chain and combined row. '
        'Two native pages were visually inspected (body-text pass and four-column rejection); '
        'this does not establish the quality of every accepted page.', '',
        '| Decade | Books | Planned | Fetched | Accepted | Replacements |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for d in sorted({b['decade'] for b in data['books']}):
        bs = [b for b in data['books'] if b['decade']==d]; ids = {b['book'] for b in bs}
        ps = [p for p in manifest['pages'] if p['book'] in ids]
        lines.append(f"| {d}s | {len(bs)} | {sum(b['allocation'] for b in bs)} | {len(ps)} | "
                     f"{sum(p['harvest_accepted'] for p in ps)} | {sum(p['replacement'] and p['harvest_accepted'] for p in ps)} |")
    lines += ['', '| Decade | Year | Book (key) | Planned | Fetched | Accepted | Replacements |',
              '| --- | ---: | --- | ---: | ---: | ---: | ---: |']
    for b in sorted(data['books'], key=lambda b:(b['decade'], b['title'])):
        ps = [p for p in manifest['pages'] if p['book']==b['book']]
        title = b['title'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {b['decade']}s | {b['year']} | {title} (`{b['key']}`) | {b['allocation']} | {len(ps)} | "
                     f"{sum(p['harvest_accepted'] for p in ps)} | {sum(p['replacement'] and p['harvest_accepted'] for p in ps)} |")
    lines += ['', 'Gate failures can carry multiple reasons.', '', '| Reason | Pages |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k,v in sorted(summary['failures_by_reason'].items())]
    (BASE / 'RESCUE_FETCH.md').write_text('\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    # Whole-driver lock protects slot/gate/report checkpoints across invocations.
    BIG.mkdir(parents=True, exist_ok=True)
    with (BIG / 'rescue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.prepare:
            prepare()
        if args.run:
            data = read(OUT / 'selection.json'); verify_inputs(data); verify_resume(data)
            if (OUT / 'run_state.json').exists() and read(OUT / 'run_state.json').get('complete'):
                print('T18 acquisition already complete; no network required', flush=True)
            else:
                if not (OUT / 'run_state.json').exists():
                    atomic(OUT / 'run_state.json', dict(started_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                        fetch_seconds=0, gate_seconds=0, stages=[], complete=False))
                started = time.perf_counter()
                before = read(OUT / 'run_state.json').get('fetch_seconds', 0) if (OUT / 'run_state.json').exists() else 0
                try:
                    t16.run()
                finally:
                    # Include interrupted chunks so resume cannot erase fetch time.
                    if (OUT / 'run_state.json').exists():
                        state = read(OUT / 'run_state.json')
                        state['fetch_seconds'] = max(state['fetch_seconds'], before + time.perf_counter()-started)
                        atomic(OUT / 'run_state.json', state)
                        if (OUT / 'slots.json').exists():
                            report(state=state)
        if args.publish:
            publish()


if __name__ == '__main__':
    main()
