"""T6h orchestration only. All masking/matching/guard code stays in phase0_mask.

Page records are the atomic resume units. records.jsonl is rebuilt from those
units on restart, so an interrupted append never loses or duplicates a page.
"""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
              'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[_name] = '1'
os.environ.update(PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import fcntl
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import tarfile
import threading
import time
import traceback
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE = HERE.parent / 'v2_clariden'
RECEIPTS = PHASE / 'receipts'
SOURCE = Path.home() / 'Projects/greek-ocr-toolkit'
TREE = '63c640a3aa4abe08d200258cf24d235dfa4a1625'
PARAM = '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'
FLOOR = 10_000_000_000
STATUSES = {'masked', 'guarded_original', 'unmatched_original', 'parliament_skipped', 'failed_page'}
ARCHIVE_PATHS = ('greekocr', 'docs/harvest/recut_v1/v2_test/run.py',
                 'docs/harvest/recut_v1/v2_pilot/run.py', 'docs/harvest/recut_v1/w1_masked/run.py',
                 'docs/harvest/recut_v1/masking/probe.py', 'docs/harvest/recut_v1/masking/params.json')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def atomic(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def write_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def write_rows(path, values):
    atomic(path, ''.join(json.dumps(v, ensure_ascii=False, sort_keys=True) + '\n' for v in values))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def offline():
    def audit(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind', 'socket.sendto'):
            raise PermissionError('T6h network OFF')
    sys.addaudithook(audit)


def priority():
    value = os.getpriority(os.PRIO_PROCESS, 0)
    if value < 15:
        raise RuntimeError(f'nice >=15 required; actual nice={value}; launch blocked')
    return value


def can_launch(active, next_mp, workers=4):
    cap = min(workers, 3 if any(mp > 20 for mp in [*active, next_mp]) else 4)
    return len(active) < cap


class DiskWatchdog:
    """Sample even while the coordinator is hashing/resuming a large page."""
    def __init__(self, out):
        self.out = out
        self.minimum_free = shutil.disk_usage(out).free
        self.low = threading.Event()
        self.done = threading.Event()
        self.processes = {}
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def check(self):
        self.minimum_free = min(self.minimum_free, shutil.disk_usage(self.out).free)
        if self.minimum_free < FLOOR:
            self.low.set()
        return self.low.is_set()

    def ensure(self):
        if self.check():
            raise RuntimeError('disk_below_10_GB; run stopped')

    def watch(self):
        while not self.done.wait(.5):
            if self.check():
                for process in list(self.processes.values()):
                    if process.poll() is None:
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                return

    def __enter__(self):
        self.ensure()
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.done.set()
        self.thread.join(timeout=2)


def page_name(page):
    return page['wave'] + '--' + page['page_id']


def output_path(page, line):
    return str(Path('crops') / page['wave'] / page['doc'] / Path(line['crop']).name)


def contained(base, path):
    result = Path(path)
    if not result.is_absolute():
        result = base / result
    if not result.resolve().is_relative_to(base.resolve()):
        raise ValueError(f'path outside {base}: {path}')
    return result


def code_snapshot(out):
    """Export Git's frozen tree; never use a mutable checkout as runtime code."""
    archive = subprocess.check_output(['git', 'archive', TREE, '--', *ARCHIVE_PATHS], cwd=ROOT)
    expected = {}
    code = out / 'code'
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f'non-file in frozen archive: {member.name}')
            path = contained(code, member.name)
            content = tar.extractfile(member).read()
            expected[member.name] = hashlib.sha256(content).hexdigest()
            if path.exists():
                if sha(path) != expected[member.name]:
                    raise RuntimeError(f'frozen snapshot drift: {path}')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    extra = {str(p.relative_to(code)) for p in code.rglob('*') if p.is_file()} - expected.keys()
    if extra:
        raise RuntimeError(f'extra files in frozen code: {extra}')
    for binding in json.loads((RECEIPTS / 'frozen_sources.json').read_text()):
        if expected[binding['path']] != binding['sha256']:
            raise RuntimeError('T6f frozen source mismatch: ' + binding['path'])
    return expected


def population(source=SOURCE):
    """Reuse the phase-0 import reader, including reserved -> test normalization."""
    inventory = load('t6h_inventory', PHASE / 'phase0_inventory.py')
    frozen = json.loads((RECEIPTS / 'local_population.json').read_text())
    data, bindings = [], {}
    for split, values, receipt in inventory.population(source):
        if receipt != frozen[split]:
            raise RuntimeError(f'full {split} population/hash drift')
        data.extend(values)
        bindings[f'import_{split}'] = receipt['manifest_sha256']
    if len(data) != 258465 or len({r['id'] for r in data}) != len(data):
        raise RuntimeError('population must be 258465 unique train/test crops')
    return data, bindings


def make_selection(source=SOURCE, mock=False):
    data, bindings = population(source)
    inventory = load('t6h_inventory_keys', PHASE / 'phase0_inventory.py')
    if mock:
        wanted = {r['id'] for r in rows(RECEIPTS / 'mock_50.jsonl')}
        data = [r for r in data if r['id'] in wanted]
        if len(data) != 50 or {r['id'] for r in data} != wanted:
            raise RuntimeError('mock identity drift')
    groups = defaultdict(list)
    for row in data:
        groups[inventory.key(row)].append(row)
    scan = {(r['wave'], r['doc'], r['page']): r for r in rows(RECEIPTS / 'pages.jsonl')}
    wanted = {r['id'] for r in data}
    admitted = {}
    frozen = json.loads((RECEIPTS / 'local_population.json').read_text())
    for wave in sorted({r['wave'] for r in data}):
        path = source / 'docs/harvest' / wave / 'admitted.jsonl'
        bindings['admitted_' + wave] = sha(path)
        if bindings['admitted_' + wave] != frozen['admitted_sha256'][wave]:
            raise RuntimeError('admitted file changed: ' + wave)
        for row in rows(path):
            if row['id'] in wanted:
                if row['id'] in admitted:
                    raise RuntimeError('duplicate admitted id: ' + row['id'])
                admitted[row['id']] = row
    if set(admitted) != wanted:
        raise RuntimeError('missing admitted crops')
    pages, destinations = [], set()
    for key, values in sorted(groups.items()):
        wave, doc, number = key
        observation = scan[key]
        raster = contained(source / 'docs/harvest', observation['path'])
        page = dict(wave=wave, doc=doc, page=number, page_id=f'{doc}-p{number:06d}',
                    scan=observation, raster=str(raster),
                    megapixels=observation['w'] * observation['h'] / 1e6, lines=[])
        for row in values:
            saved = admitted[row['id']]
            if saved['crop_path'] != row['crop']:
                raise RuntimeError('import/admitted crop mismatch: ' + row['id'])
            contained(source / 'docs/harvest', source / row['crop'])
            line = dict(id=row['id'], split=row['split'], crop=row['crop'],
                        crop_bbox=saved['crop_bbox'], crop_sha256=saved['crop_sha256'],
                        script_class=row['script_class'], admitted_split=saved['split'])
            dest = output_path(page, line)
            if dest in destinations:
                raise RuntimeError('output collision: ' + dest)
            destinations.add(dest)
            page['lines'].append(line)
        pages.append(page)
    if not mock:
        parliament = [p for p in pages if p['wave'] == 'parliament']
        if (len(pages), len(parliament), sum(len(p['lines']) for p in parliament)) != (5585, 645, 76463):
            raise RuntimeError('full page/parliament population drift')
    bindings['page_inventory'] = sha(RECEIPTS / 'pages.jsonl')
    return pages, bindings


def prepare(out, source, mock, watchdog=None):
    out.mkdir(parents=True, exist_ok=True)
    for name in ('pages', 'crops', 'work', 'logs', 'tmp', 'inputs'):
        (out / name).mkdir(exist_ok=True)
    pages, inputs = make_selection(source, mock)
    if watchdog:
        watchdog.ensure()
    selection = json.dumps(pages, sort_keys=True)
    digest = hashlib.sha256(selection.encode()).hexdigest()
    code = code_snapshot(out)
    binding = dict(tree_sha=TREE, params_sha256=PARAM, source=str(source), mode='mock' if mock else 'full',
                   selection_sha256=digest, inputs=inputs, code=code,
                   adapter_sha256=sha(PHASE / 'phase0_mask.py'), runner_sha256=sha(__file__))
    if (out / 'binding.json').exists():
        if json.loads((out / 'binding.json').read_text()) != binding:
            raise RuntimeError('resume bindings changed; keep the existing run intact')
    else:
        atomic(out / 'selection.json', selection + '\n')
        write_json(out / 'binding.json', binding)
    if hashlib.sha256(json.dumps(json.loads((out / 'selection.json').read_text()), sort_keys=True).encode()).hexdigest() != digest:
        raise RuntimeError('selection drift')
    # A fresh worker reads only its own page, not the 258k-line selection again.
    for i, page in enumerate(pages):
        path = out / 'inputs' / f'{i:05d}.json'
        if path.exists():
            if json.loads(path.read_text()) != page:
                raise RuntimeError('page input drift: ' + str(path))
        else:
            write_json(path, page)
    return pages


def originals(page, source, out, status, error=None):
    """Copy source bytes for parliament or an explicitly recorded failed page."""
    result = []
    for line in page['lines']:
        original = source / line['crop']
        dest = contained(out, output_path(page, line))
        record = dict(id=line['id'], wave=page['wave'], split=line['split'], page_id=page['page_id'],
                      original_path=str(original), original_sha256=line['crop_sha256'],
                      output_path=output_path(page, line), output_sha256=None,
                      masked_pixel_count=0, masked_component_count=0, changed=False,
                      guard_status=status, match_status='skipped' if status == 'parliament_skipped' else 'failed',
                      wrong_line_risk=False, host=socket.gethostname(), tree_sha=TREE, code_tree_sha=TREE,
                      params_sha256=PARAM)
        if status == 'parliament_skipped':
            record['skipped_wave'] = 'parliament'
        if error:
            record['page_error'] = error
        try:
            content = original.read_bytes()
            actual = hashlib.sha256(content).hexdigest()
            if actual != line['crop_sha256']:
                raise RuntimeError('original/admitted hash mismatch')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            record['output_sha256'] = actual
        except Exception:
            record.update(guard_status='failed_page', page_error=traceback.format_exc())
        result.append(record)
    return result


def page_worker(out, index):
    priority()
    page = json.loads((out / 'inputs' / f'{index:05d}.json').read_text())
    binding = json.loads((out / 'binding.json').read_text())
    source = Path(binding['source'])
    attempt = out / 'work' / page_name(page)
    # Only this page's uncommitted scratch is replaceable on restart.
    if attempt.exists():
        shutil.rmtree(attempt)
    attempt.mkdir()
    for name in ('pages', 'page-lines', 'crops', 'tmp'):
        (attempt / name).mkdir()
    write_json(attempt / 'selection.json', [page])
    started = time.monotonic()
    error = None
    if page['wave'] == 'parliament':
        records = originals(page, source, attempt, 'parliament_skipped')
    else:
        try:
            adapter = load('t6h_phase0', PHASE / 'phase0_mask.py')
            if sha(PHASE / 'phase0_mask.py') != binding['adapter_sha256']:
                raise RuntimeError('phase0 adapter changed')
            sys.argv = [str(PHASE / 'phase0_mask.py'), '--code', str(out / 'code'),
                        '--harvest', str(source / 'docs/harvest'), '--out', str(attempt), '--worker', '0']
            adapter.main()
            records = list(rows(attempt / 'page-lines' / (page_name(page) + '.guarded.jsonl')))
            for record in records:
                record.update(output_path=record['masked_path'], tree_sha=TREE)
        except Exception:
            error = traceback.format_exc()
            print(error, flush=True)
            records = originals(page, source, attempt, 'failed_page', error)
    write_rows(attempt / 'records.jsonl', records)
    write_json(attempt / 'result.json', dict(page_id=page['page_id'], wave=page['wave'],
               host=socket.gethostname(), tree_sha=TREE, worker_pid=os.getpid(), nice=priority(),
               wall_seconds=time.monotonic() - started, error=error,
               failed=any(r['guard_status'] == 'failed_page' for r in records)))


def validate_records(page, records, out, source, rehash=True):
    expected = {r['id']: r for r in page['lines']}
    if len(records) != len(expected) or {r['id'] for r in records} != set(expected):
        raise ValueError('incomplete/duplicate page records')
    for record in records:
        line = expected[record['id']]
        original = source / line['crop']
        if (record['wave'], record['split'], record['page_id'], record['original_sha256']) != (
                page['wave'], line['split'], page['page_id'], line['crop_sha256']):
            raise ValueError('record identity/custody mismatch')
        if (not record['host'] or record['code_tree_sha'] != TREE or record['tree_sha'] != TREE
                or record['params_sha256'] != PARAM or record['guard_status'] not in STATUSES
                or record['output_path'] != output_path(page, line)
                or Path(record['original_path']) != original):
            raise ValueError('record provenance/path mismatch')
        if (record['match_status'] not in ('matched', 'ambiguous', 'unmatched', 'skipped', 'failed')
                or any(not isinstance(record[key], int) or record[key] < 0
                       for key in ('masked_pixel_count', 'masked_component_count'))):
            raise ValueError('missing/invalid match or mask counts')
        status = record['guard_status']
        if page['wave'] == 'parliament' and status not in ('parliament_skipped', 'failed_page'):
            raise ValueError('parliament was masked')
        if status == 'parliament_skipped' and (page['wave'] != 'parliament' or record['skipped_wave'] != 'parliament'):
            raise ValueError('wrong skip')
        if status == 'guarded_original' and (not record['wrong_line_risk'] or record['own_ink_masked_fraction'] <= .30):
            raise ValueError('wrong guard')
        if status == 'masked' and record.get('wrong_line_risk'):
            raise ValueError('guarded mask retained')
        if status == 'unmatched_original' and record['match_status'] != 'unmatched':
            raise ValueError('wrong unmatched status')
        if status == 'failed_page' and not record.get('page_error'):
            raise ValueError('silent page failure')
        if status in ('guarded_original', 'unmatched_original', 'parliament_skipped', 'failed_page'):
            if record['output_sha256'] is not None and record['output_sha256'] != record['original_sha256']:
                raise ValueError('original fallback changed bytes')
        dest = contained(out, record['output_path'])
        if record['output_sha256'] is None:
            if status != 'failed_page' or not record.get('page_error'):
                raise ValueError('silent missing output')
        elif rehash and sha(dest) != record['output_sha256']:
            raise ValueError('output bytes changed: ' + record['id'])
        if rehash and sha(original) != record['original_sha256']:
            raise ValueError('original bytes changed: ' + record['id'])


def completed(page, out, source):
    path = out / 'pages' / (page_name(page) + '.records.jsonl')
    try:
        records = list(rows(path))
        validate_records(page, records, out, source)
        # Missing source/output is recorded, but is not a complete resume unit.
        if any(r['output_sha256'] is None for r in records):
            return None
        return records
    except (OSError, ValueError, KeyError, TypeError):
        return None


def add_counts(counts, records):
    for r in records:
        c = counts.setdefault(r['wave'], {}).setdefault(r['split'],
                dict(total=0, changed=0, guarded=0, unmatched=0, failed=0, parliament_skipped=0, masked=0))
        c['total'] += 1
        c['changed'] += r['output_sha256'] is not None and r['output_sha256'] != r['original_sha256']
        for name, status in (('guarded', 'guarded_original'), ('unmatched', 'unmatched_original'),
                             ('failed', 'failed_page'), ('parliament_skipped', 'parliament_skipped'), ('masked', 'masked')):
            c[name] += r['guard_status'] == status


def gate(mock_out, expected_binding):
    receipt = json.loads((mock_out / 'mock-comparison.json').read_text())
    binding = json.loads((mock_out / 'binding.json').read_text())
    for key in ('tree_sha', 'params_sha256', 'source', 'code', 'adapter_sha256', 'runner_sha256'):
        if binding[key] != expected_binding[key]:
            raise RuntimeError('mock/full binding mismatch: ' + key)
    if not receipt['ok'] or receipt['identical'] != 50:
        raise RuntimeError('full run requires a new 50/50 Mac mock')
    # Recheck the actual 50 outputs, never accept a receipt alone.
    compare_mock(mock_out)


def compare_mock(out):
    expected = {r['id']: r for r in rows(RECEIPTS / 'mock_mac_records.jsonl')}
    pages = json.loads((out / 'selection.json').read_text())
    binding = json.loads((out / 'binding.json').read_text())
    actual = {}
    for page in pages:
        records = completed(page, out, Path(binding['source']))
        if records is None:
            raise RuntimeError('mock page incomplete: ' + page_name(page))
        for record in records:
            if record['id'] in actual:
                raise RuntimeError('duplicate mock id')
            actual[record['id']] = record
    if len(expected) != 50 or set(actual) != set(expected):
        raise RuntimeError('mock must contain exactly the original 50 IDs')
    fields = ('output_sha256', 'guard_status', 'match_status', 'wrong_line_risk',
              'masked_pixel_count', 'masked_component_count')
    diff = {key: [f for f in fields if actual[key].get(f) != expected[key].get(f)]
            for key in expected}
    diff = {key: value for key, value in diff.items() if value}
    result = dict(ok=not diff, identical=sum(actual[k]['output_sha256'] == expected[k]['output_sha256'] for k in expected),
                  compared=50, differences=diff, baseline_sha256=sha(RECEIPTS / 'mock_mac_records.jsonl'))
    write_json(out / 'mock-comparison.json', result)
    if not result['ok']:
        raise RuntimeError('mock differs from Mac baseline: ' + json.dumps(result))
    return result


def run(out, source, workers, mock, detached):
    priority()
    if detached and os.getsid(0) != os.getpid():
        raise RuntimeError('detached run requires setsid; launch blocked')
    out.mkdir(parents=True, exist_ok=True)
    with (out / '.run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if detached:
            atomic(HERE / 'run.pid', str(os.getpid()) + '\n')
        with DiskWatchdog(out) as watchdog:
            pages = prepare(out, source, mock, watchdog)
            binding = json.loads((out / 'binding.json').read_text())
            if not mock:
                gate(HERE / 'mock-out', binding)
            watchdog.ensure()
            return schedule(out, source, pages, workers, watchdog, lock.fileno())


def schedule(out, source, pages, workers, watchdog, lock_fd=None):
    started = time.monotonic()
    counts, pending, active = {}, [], {}
    watchdog.processes = active
    done, resumed, fresh_masked, minimum_free = 0, 0, 0, shutil.disk_usage(out).free
    # Recover only committed page units; discard an interrupted aggregate tail.
    with (out / 'records.jsonl.tmp').open('w') as aggregate:
        for i, page in enumerate(pages):
            watchdog.ensure()
            records = completed(page, out, source)
            if records is None:
                pending.append(i)
            else:
                add_counts(counts, records)
                aggregate.write((out / 'pages' / (page_name(page) + '.records.jsonl')).read_text())
                done += 1
        aggregate.flush()
        os.fsync(aggregate.fileno())
    os.replace(out / 'records.jsonl.tmp', out / 'records.jsonl')
    resumed = done
    stop = None
    previous_handlers = {}

    def interrupt(signum, frame):
        nonlocal stop
        stop = 'signal_' + str(signum)

    for signum in (signal.SIGTERM, signal.SIGINT):
        previous_handlers[signum] = signal.signal(signum, interrupt)

    def summary(state):
        elapsed = time.monotonic() - started
        rate = fresh_masked * 60 / elapsed if fresh_masked else None
        remaining = sum(1 for i in pending if pages[i]['wave'] != 'parliament') + sum(
            1 for i in active if pages[i]['wave'] != 'parliament')
        eta = datetime.now(ZoneInfo('Europe/Athens')) + timedelta(minutes=remaining / rate) if rate else None
        value = dict(state=state, host=socket.gethostname(), tree_sha=TREE, params_sha256=PARAM,
                     pid=os.getpid(), nice=os.getpriority(os.PRIO_PROCESS, 0), workers=workers,
                     pages_total=len(pages), pages_complete=done, pages_resumed=resumed,
                     masking_pages_this_session=fresh_masked, active_pages=len(active),
                     pending_pages=len(pending), elapsed_seconds=elapsed, pages_per_minute=rate,
                     eta_athens=eta.isoformat() if eta else None, minimum_free_bytes=minimum_free,
                     stop_reason=stop, per_wave_split=counts)
        write_json(out / 'summary.json', value)
        return value

    try:
        with (out / 'records.jsonl').open('a') as aggregate:
            summary('running')
            last_status = time.monotonic()
            while pending or active:
                minimum_free = min(minimum_free, watchdog.minimum_free)
                if watchdog.check():
                    stop = 'disk_below_10_GB'
                if stop:
                    break
                while pending and can_launch([pages[i]['megapixels'] for i in active], pages[pending[0]]['megapixels'], workers):
                    i = pending.pop(0)
                    log = (out / 'logs' / (page_name(pages[i]) + '.log')).open('ab')
                    try:
                        process = subprocess.Popen([sys.executable, '-B', str(HERE / 'run.py'), 'page',
                                                    '--out', str(out), '--index', str(i)],
                                                   stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                                   pass_fds=() if lock_fd is None else (lock_fd,))
                    finally:
                        log.close()
                    active[i] = process
                changed = False
                for i, process in list(active.items()):
                    rc = process.poll()
                    if rc is None:
                        continue
                    if watchdog.low.is_set():
                        stop = 'disk_below_10_GB'
                        break
                    page = pages[i]
                    attempt = out / 'work' / page_name(page)
                    try:
                        if rc:
                            raise RuntimeError(f'worker exit {rc}; see logs/{page_name(page)}.log')
                        records = list(rows(attempt / 'records.jsonl'))
                        validate_records(page, records, attempt, source)
                    except Exception:
                        attempt.mkdir(exist_ok=True)
                        records = originals(page, source, attempt, 'failed_page', traceback.format_exc())
                        write_rows(attempt / 'records.jsonl', records)
                    for record in records:
                        if record['output_sha256'] is not None:
                            dest = contained(out, record['output_path'])
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            os.replace(contained(attempt, record['output_path']), dest)
                    committed = out / 'pages' / (page_name(page) + '.records.jsonl')
                    os.replace(attempt / 'records.jsonl', committed)
                    aggregate.write(committed.read_text())
                    aggregate.flush()
                    os.fsync(aggregate.fileno())
                    add_counts(counts, records)
                    done += 1
                    fresh_masked += page['wave'] != 'parliament' and not any(r['guard_status'] == 'failed_page' for r in records)
                    del active[i]
                    print(json.dumps(dict(page=page_name(page), completed=done, total=len(pages),
                                          failed=sum(r['guard_status'] == 'failed_page' for r in records))), flush=True)
                    changed = True
                if changed or time.monotonic() - last_status >= 5:
                    summary('running')
                    last_status = time.monotonic()
                time.sleep(.25)
    finally:
        for process in active.values():
            if process.poll() is None:
                process.terminate()
        for process in active.values():
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
        failures = sum(c['failed'] for wave in counts.values() for c in wave.values())
        state = 'stopped' if stop or done != len(pages) else 'completed_with_failures' if failures else 'completed'
        result = summary(state)
        print(json.dumps(result), flush=True)
    return 0 if result['state'] == 'completed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'mock', 'run', 'page', 'compare'))
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--index', type=int)
    parser.add_argument('--detached', action='store_true')
    args = parser.parse_args()
    offline()
    if args.source.resolve() != SOURCE.resolve():
        parser.error('source must be the read-only main checkout')
    out = args.out or HERE / ('mock-out' if args.mode in ('mock', 'compare') else 'out')
    out = out.absolute()
    if out.resolve() != out or not (out.is_relative_to(HERE / 'out') or out.is_relative_to(HERE / 'mock-out')):
        parser.error('outputs must stay in v2_full/out or v2_full/mock-out without symlinks')
    if args.mode == 'prepare':
        print(json.dumps(dict(pages=len(prepare(out, args.source, False)), out=str(out))))
        return 0
    if args.mode == 'page':
        if args.index is None:
            parser.error('--index required')
        page_worker(out, args.index)
        return 0
    if args.mode == 'compare':
        print(json.dumps(compare_mock(out)))
        return 0
    result = run(out, args.source, args.workers, args.mode == 'mock', args.detached)
    if result == 0 and args.mode == 'mock':
        print(json.dumps(compare_mock(out)), flush=True)
    return result


if __name__ == '__main__':
    sys.exit(main())
