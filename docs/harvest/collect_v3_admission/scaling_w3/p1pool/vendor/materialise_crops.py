#!/usr/bin/env python3
"""Offline orchestration only; PNG bytes come from the census deployment."""
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from zoneinfo import ZoneInfo

MODULE = 'greekocr.harvest.line_pipeline_native'
FUNCTION = 'reconstructed_crop'


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def now():
    return datetime.now(ZoneInfo('Europe/Athens')).isoformat()


def lines(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def atomic_json(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def safe(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', value) or value in {'.', '..'}:
        raise ValueError('unsafe path component: ' + repr(value))
    return value


def identity(row):
    return {k: row[k] for k in ('parent_id', 'id', 'split', 'crop_sha256')}


def select(args):
    attempt = args.census_attempt.resolve()
    current = json.loads((attempt / 'CURRENT.json').read_text())
    if current['status'] != 'completed':
        raise ValueError('census not completed')
    generation = attempt / 'generations' / safe(current['export_id'])
    summary_file = generation / 'summary.json'
    if sha(summary_file) != current['summary_sha256']:
        raise ValueError('summary hash mismatch')
    summary = json.loads(summary_file.read_text())
    if not summary['complete']:
        raise ValueError('census summary incomplete')
    inputs = {'CURRENT.json': sha(attempt / 'CURRENT.json'), 'summary.json': sha(summary_file)}

    def output(name):
        path = generation / (name + '.jsonl')
        expected = summary['outputs'][name]['sha256']
        if sha(path) != expected:
            raise ValueError(name + ' hash mismatch')
        inputs[name] = expected
        return path

    def wanted(binding):
        return any(binding['parent_id'].startswith('collect-v3-' + t + '-')
                   for t in (('W1', 'W2') if args.tranche == 'all' else (args.tranche,)))

    selected = {}
    def add(row, binding):
        if identity(row) != binding:
            raise ValueError('row/decision binding mismatch')
        key = (row['parent_id'], row['id'])
        compact = {k: row[k] for k in ('parent_id', 'id', 'split', 'crop_sha256', 'source',
                    'crop_source_image', 'crop_source_sha256', 'crop_bbox')}
        compact['crop_color_mode'] = row.get('crop_color_mode', 'L')
        compact['binding'] = binding
        if key in selected and selected[key] != compact:
            raise ValueError('conflicting duplicate binding')
        selected[key] = compact

    for row in lines(output('admitted_train')):
        binding = row.get('binding', row.get('decision', {}).get('binding', identity(row)))
        if wanted(binding):
            if binding['split'] != 'train':
                raise ValueError('nontrain row in admitted_train')
            add(row, binding)
    if args.include_heldout:
        held = {}
        for decision in lines(output('decisions')):
            b = decision['binding']
            if wanted(b) and decision.get('admitted') is True and b['split'] in {'dev', 'test'}:
                held[(b['parent_id'], b['id'])] = b
        for diagnostic in lines(output('evaluation_diagnostics')):
            row = diagnostic['row']
            key = (row['parent_id'], row['id'])
            if key in held:
                add(row, held.pop(key))
        if held:
            raise ValueError('missing heldout reconstruction metadata')
    rows = sorted(selected.values(), key=lambda r: (r['id'], r['parent_id']))
    if args.mode == 'smoke':
        if args.tranche != 'W2':
            raise ValueError('smoke requires W2')
        rows = rows[:500]
    if not rows:
        raise ValueError('empty selection')
    for r in rows:
        safe(r['source']); safe(r['id'])
        for key in ('crop_sha256', 'crop_source_sha256'):
            if not re.fullmatch('[a-f0-9]{64}', r[key]):
                raise ValueError('invalid sha: ' + key)
        r['relative_path'] = str(Path('collection_' + ('w2' if r['parent_id'].startswith('collect-v3-W2-') else 'w1') + '_originals') / r['source'] / (r['id'] + '.png'))
    return rows, inputs


def load_code(root):
    sys.path.insert(0, str(root.resolve()))
    module = importlib.import_module(MODULE)
    path = Path(module.__file__).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('reconstruction imported outside census code tree')
    return module


def init_worker(root):
    global NATIVE
    NATIVE = load_code(Path(root))


def page_job(task):
    from PIL import Image
    page_path, rows, base = task
    results = []
    try:
        actual_page_sha = sha(page_path)
        if any(r['crop_source_sha256'] != actual_page_sha for r in rows):
            raise ValueError('source page hash mismatch')
        with Image.open(page_path) as page:
            page.load()  # one source decode for this page task
            for r in rows:
                result = dict(row=r, state='failure', bytes=0)
                try:
                    dest = Path(base) / r['relative_path']
                    if dest.exists():
                        existing_sha = sha(dest)
                        if existing_sha != r['crop_sha256']:
                            result.update(state='mismatch', observed_sha256=existing_sha, error='existing bytes differ; untouched')
                        else:
                            result.update(state='skipped_valid', bytes=dest.stat().st_size)
                    else:
                        if not NATIVE.valid_box(r['crop_bbox'], page.size):
                            raise ValueError('invalid frozen crop coordinates')
                        image, raw = getattr(NATIVE, FUNCTION)(page, r['crop_bbox'], r['crop_color_mode'])
                        image.close()
                        encoded_sha = hashlib.sha256(raw).hexdigest()
                        if encoded_sha != r['crop_sha256']:
                            result.update(state='mismatch', observed_sha256=encoded_sha, error='reconstructed bytes differ; no write')
                        else:
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            fd, tmp = tempfile.mkstemp(prefix='.crops4-', dir=dest.parent)
                            try:
                                with os.fdopen(fd, 'wb') as f:
                                    f.write(raw); f.flush(); os.fsync(f.fileno())
                                # Atomic no-clobber publication: hard link then unlink temp.
                                # A concurrent writer can never be replaced, even between checks.
                                try:
                                    os.link(tmp, dest)
                                    result.update(state='written', bytes=len(raw))
                                except FileExistsError:
                                    if sha(dest) == r['crop_sha256']:
                                        result.update(state='skipped_valid', bytes=dest.stat().st_size)
                                    else:
                                        result.update(state='mismatch', error='concurrent conflicting file; untouched')
                            finally:
                                os.unlink(tmp)
                except Exception as e:
                    result['error'] = str(e)
                results.append(result)
    except Exception as e:
        results = [dict(row=r, state='failure', bytes=0, error=str(e)) for r in rows]
    return results


def bounded_results(tasks, workers, root):
    with ProcessPoolExecutor(max_workers=workers, initializer=init_worker, initargs=(str(root),)) as pool:
        pending = set()
        tasks = iter(tasks)
        exhausted = False
        while pending or not exhausted:
            while not exhausted and len(pending) < 2 * workers:
                try:
                    pending.add(pool.submit(page_job, next(tasks)))
                except StopIteration:
                    exhausted = True
            if pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in done:
                    yield from future.result()


def checksum_check(base, sums):
    command = ['sha256sum', '-c', str(sums)] if shutil.which('sha256sum') else ['shasum', '-a', '256', '-c', str(sums)]
    with open(sums.parent / 'sha256check.log', 'w') as log:
        return subprocess.run(command, cwd=base, stdout=log, stderr=subprocess.STDOUT).returncode


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--census-attempt', required=True, type=Path)
    p.add_argument('--census-code', required=True, type=Path)
    p.add_argument('--work-root', required=True, type=Path)
    p.add_argument('--attempt', required=True, type=Path)
    p.add_argument('--tranche', choices=['W1', 'W2', 'all'], default='W2')
    p.add_argument('--include-heldout', action='store_true')
    p.add_argument('--mode', choices=['smoke', 'full'], default='full')
    p.add_argument('--smoke-receipt', type=Path)
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--verify-only', action='store_true')
    a = p.parse_args()
    started = now(); tick = time.monotonic()
    rows, inputs = select(a)
    pages = defaultdict(list)
    for r in rows:
        pages[r['crop_source_image']].append(r)
    missing = [s for s in pages if not Path(s).is_file()]
    if missing:
        raise ValueError('missing pages: ' + str(missing[:10]))
    module = load_code(a.census_code)
    codec = os.environ.get('LD_PRELOAD', '')
    codec_sha = sha(codec) if codec else None
    context = dict(inputs=inputs, census_code=str(a.census_code.resolve()),
                   code_sha256=sha(Path(__file__)), reconstruction_module=MODULE,
                   reconstruction_function=FUNCTION, reconstruction_file=module.__file__,
                   reconstruction_sha256=sha(module.__file__), codec_preload=codec,
                   codec_preload_sha256=codec_sha, interpreter=sys.executable,
                   interpreter_sha256=sha(sys.executable), tranche=a.tranche,
                   include_heldout=a.include_heldout)
    if a.verify_only:
        print('VERIFY_OK', len(rows), len(pages)); return 0
    if a.workers < 1:
        raise ValueError('workers must be positive')
    a.attempt = a.attempt.resolve(); a.work_root = a.work_root.resolve()
    if not a.attempt.is_relative_to(a.work_root / 'crops4_attempts'):
        raise ValueError('attempt must be inside work-root/crops4_attempts')
    if a.mode == 'full':
        if not a.smoke_receipt:
            raise ValueError('full requires smoke receipt')
        gate = json.loads(a.smoke_receipt.read_text())
        if not (gate['status'] == 'ok' and gate['mode'] == 'smoke' and gate['selected'] == 500
                and gate['byte_exact'] == 500 and gate['context'] == dict(context, tranche='W2')):
            raise ValueError('smoke gate failed or provenance differs')
        smoke_args = argparse.Namespace(**vars(a)); smoke_args.mode = 'smoke'; smoke_args.tranche = 'W2'
        smoke_rows, _ = select(smoke_args)
        if gate['selection_sha256'] != digest(smoke_rows):
            raise ValueError('smoke selection differs')
        for r in smoke_rows:
            if sha(Path(gate['output_base']) / r['relative_path']) != r['crop_sha256']:
                raise ValueError('smoke output drift')
    a.attempt.mkdir(parents=True, exist_ok=True)
    base = a.attempt / 'smoke' if a.mode == 'smoke' else a.work_root
    base.mkdir(parents=True, exist_ok=True)
    sums = a.attempt / 'crops_sha256.txt'
    sums.write_text(''.join(r['crop_sha256'] + '  ' + r['relative_path'] + '\n' for r in rows))
    counts = dict(written=0, skipped_valid=0, mismatches=0, failures=0, bytes=0)
    per_tranche = {t: dict(selected=0, **counts) for t in ('W1', 'W2')}
    with (a.attempt / 'crops_manifest.jsonl').open('w') as manifest, (a.attempt / 'failures.jsonl').open('w') as failures:
        tasks = ((page, group, str(base)) for page, group in sorted(pages.items()))
        for result in bounded_results(tasks, a.workers, a.census_code):
            state = result['state']; r = result['row']
            counts[{'mismatch': 'mismatches', 'failure': 'failures'}.get(state, state)] += 1
            counts['bytes'] += result['bytes']
            tranche = 'W2' if r['parent_id'].startswith('collect-v3-W2-') else 'W1'
            per_tranche[tranche]['selected'] += 1
            per_tranche[tranche][{'mismatch': 'mismatches', 'failure': 'failures'}.get(state, state)] += 1
            per_tranche[tranche]['bytes'] += result['bytes']
            if state in {'written', 'skipped_valid'}:
                manifest.write(json.dumps(dict(row_id=r['id'], parent_id=r['parent_id'], source=r['source'],
                    split=r['split'], relative_path=r['relative_path'], sha256=r['crop_sha256'], bytes=result['bytes'])) + '\n')
            else:
                failures.write(json.dumps(result) + '\n')
    check = checksum_check(base, sums)
    receipt = dict(context=context, mode=a.mode, output_base=str(base), selected=len(rows), pages=len(pages),
        train_selected=sum(r['split'] == 'train' for r in rows),
        heldout_selected=sum(r['split'] in {'dev', 'test'} for r in rows),
        selection_sha256=digest(rows), byte_exact=counts['written'] + counts['skipped_valid'],
        **counts, per_tranche=per_tranche, sha256check_exit=check, started_at=started, finished_at=now(),
        seconds=time.monotonic() - tick, workers=a.workers)
    receipt['status'] = 'ok' if not (counts['mismatches'] or counts['failures'] or check) else 'failed'
    atomic_json(a.attempt / 'upload_receipt.json', receipt)
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt['status'] == 'ok' else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('CROPS4_ERROR ' + str(error), file=sys.stderr)
        sys.exit(1)
