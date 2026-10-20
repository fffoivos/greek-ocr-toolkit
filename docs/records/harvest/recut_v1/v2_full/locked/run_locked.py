"""T6i2 orchestration; unchanged T6h page worker and phase0 masking adapter.

Only this job's resource floor is 5. Cross-root blind cards are byte-copied
into per-raster-root custody mirrors so the frozen HARVEST checks stay intact.
No source tree is modified. Fresh subprocesses handle every page (max two).
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t6h_locked', HERE.parent / 'run.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import shutil
import subprocess
import threading

MIN_NICE = 5
WORKERS = 2


def priority():
    actual = os.getpriority(os.PRIO_PROCESS, 0)
    if actual < MIN_NICE:
        raise RuntimeError(f'locked job requires nice >= {MIN_NICE}; actual {actual}')
    return actual


def population():
    prep = __import__('json').loads((HERE / 'preparation.json').read_text())
    assert h.sha(HERE / 'resolution.jsonl') == prep['resolution_sha256']
    for path, digest in prep['source_bindings'].items():
        assert h.sha(path) == digest, path
    resolved = list(h.rows(HERE / 'resolution.jsonl'))
    assert len(resolved) == len({r['id'] for r in resolved}) == 600
    for stratum, filename, n in [('ii', 'r0_locked_eval_ids.txt', 200),
                                  ('i-b', 'r0_ib_spellcheck_subset_ids.txt', 400)]:
        path = next(Path(p) for p in prep['source_bindings'] if Path(p).name == filename)
        expected = path.read_text().splitlines()
        actual = [r['id'] for r in resolved if r['stratum'] == stratum]
        assert len(expected) == len(set(expected)) == len(actual) == n
        assert set(actual) == set(expected)
    return resolved


def read(path):
    return __import__('json').loads(Path(path).read_text())


def initialize(out, source, pages, custody=None):
    out.mkdir(parents=True, exist_ok=True)
    for name in ('pages', 'work', 'logs', 'inputs', 'crops', 'tmp'):
        (out / name).mkdir(exist_ok=True)
    code = h.code_snapshot(out)
    binding = dict(source=str(source), tree_sha=h.TREE, params_sha256=h.PARAM,
                   adapter_sha256=h.sha(h.PHASE / 'phase0_mask.py'),
                   runner_sha256=h.sha(h.__file__), wrapper_sha256=h.sha(__file__),
                   min_nice=MIN_NICE, workers=WORKERS, code=code, custody=custody)
    if (out / 'binding.json').exists():
        assert read(out / 'binding.json') == binding, 'resume binding drift'
        assert read(out / 'selection.json') == pages, 'resume selection drift'
    h.write_json(out / 'binding.json', binding)
    h.write_json(out / 'selection.json', pages)
    for index, page in enumerate(pages):
        h.write_json(out / 'inputs' / f'{index:05d}.json', page)


def execute(jobs, watchdog):
    """At most two live fresh subprocesses, with the unchanged disk watchdog."""
    mutex = threading.Lock()
    def one(job):
        out, index, page = job
        source = Path(read(out / 'binding.json')['source'])
        watchdog.ensure()
        # Page units are reusable only after rehashing both sides.
        if h.completed(page, out, source) is not None:
            return
        with (out / 'logs' / (h.page_name(page) + '.log')).open('ab') as log:
            process = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()),
                'page', '--out', str(out), '--index', str(index)], stdout=log,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            with mutex:
                watchdog.processes[str(out) + str(index)] = process
            rc = process.wait()
            with mutex:
                del watchdog.processes[str(out) + str(index)]
        watchdog.ensure()
        if rc:
            raise RuntimeError(f'worker exit {rc}: {out}/logs/{h.page_name(page)}.log')
        attempt = out / 'work' / h.page_name(page)
        records = list(h.rows(attempt / 'records.jsonl'))
        h.validate_records(page, records, attempt, source)
        result = read(attempt / 'result.json')
        assert result['nice'] >= MIN_NICE
        for r in records:
            r['nice'] = result['nice']
            r['worker_pid'] = result['worker_pid']
            if r['output_sha256'] is not None:
                dest = h.contained(out, r['output_path'])
                dest.parent.mkdir(parents=True, exist_ok=True)
                os.replace(h.contained(attempt, r['output_path']), dest)
        h.write_rows(out / 'pages' / (h.page_name(page) + '.records.jsonl'), records)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(one, job) for job in jobs]
        for completed, future in enumerate(as_completed(futures), 1):
            future.result()
            print(f'pages {completed}/{len(jobs)}', flush=True)


def compare_mock():
    out = HERE / 'mock-5'
    expected = {r['id']: r for r in h.rows(HERE.parent / 'mock-out/records.jsonl')}
    selection = read(out / 'selection.json')
    actual = []
    for page in selection:
        records = h.completed(page, out, h.SOURCE)
        assert records is not None
        actual.extend(records)
    assert len(actual) == len({r['id'] for r in actual}) == 5
    fields = ('guard_status', 'match_status', 'wrong_line_risk', 'masked_pixel_count', 'masked_component_count', 'output_sha256')
    for r in actual:
        baseline = expected[r['id']]
        assert all(r.get(f) == baseline.get(f) for f in fields), r['id']
        assert (out / r['output_path']).read_bytes() == (HERE.parent / 'mock-out' / baseline['output_path']).read_bytes(), r['id']
    result = dict(ok=True, identical=5, ids=[r['id'] for r in actual],
                  baseline_sha256=h.sha(HERE.parent / 'mock-out/records.jsonl'),
                  binding_sha256=h.sha(out / 'binding.json'), nice=sorted({r['nice'] for r in actual}))
    h.write_json(HERE / 'mock-comparison.json', result)
    return result


def mock(watchdog):
    pages, _ = h.make_selection(mock=True)
    # One ID in each of five distinct pages: five independent fresh processes.
    selected = []
    for page in pages:
        if page['wave'] != 'parliament':
            selected.append(dict(page, lines=page['lines'][:1]))
        if len(selected) == 5:
            break
    assert len(selected) == 5
    out = HERE / 'mock-5'
    initialize(out, h.SOURCE, selected)
    execute([(out, i, p) for i, p in enumerate(selected)], watchdog)
    return compare_mock()


def copy_bound(original, destination, digest):
    assert h.sha(original) == digest, f'source drift: {original}'
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(original, destination)
    assert h.sha(destination) == digest, f'custody mirror drift: {destination}'
    assert h.sha(original) == digest


def locked_jobs(resolved, watchdog):
    groups = defaultdict(list)
    for r in resolved:
        if r['resolution_status'] == 'resolved':
            raster = Path(r['raster'])
            source = next(p for p in raster.parents if (p / 'docs/harvest').is_dir() and raster.is_relative_to(p / 'docs/harvest'))
            groups[source].append(r)
    jobs = []
    for source, values in sorted(groups.items()):
        out = HERE / 'work' / source.name
        mirror = out / 'source'
        grouped = defaultdict(list)
        custody = []
        for r in values:
            watchdog.ensure()
            raster = mirror / Path(r['raster']).relative_to(source)
            original = mirror / 'docs/harvest/locked-originals' / r['stratum'] / (r['id'] + '.png')
            copy_bound(Path(r['raster']), raster, r['scan']['sha'])
            copy_bound(Path(r['original_path']), original, r['original_sha256'])
            custody.append(dict(id=r['id'], raster=r['raster'], original_path=r['original_path'],
                                mirror_raster=str(raster), mirror_original=str(original),
                                raster_sha256=r['scan']['sha'], original_sha256=r['original_sha256']))
            grouped[r['raster']].append((r, raster, original))
        pages = []
        for index, (native_path, lines) in enumerate(sorted(grouped.items())):
            first, raster, _ = lines[0]
            page = dict(wave='locked', doc=f'page-{index:05d}', page=index, page_id=f'page-{index:05d}',
                        scan=first['scan'], raster=str(raster),
                        megapixels=first['scan']['w'] * first['scan']['h'] / 1e6, lines=[])
            for r, _, original in lines:
                page['lines'].append(dict(id=r['id'], split='test', admitted_split='test',
                    crop=str(original.relative_to(mirror)), crop_bbox=r['crop_bbox'],
                    crop_sha256=r['original_sha256'], script_class='unknown'))
            pages.append(page)
        initialize(out, mirror, pages, custody)
        jobs.extend((out, i, p) for i, p in enumerate(pages))
    return jobs


def finalize(resolved, jobs, watchdog):
    by_id = {}
    for out, _, page in jobs:
        source = Path(read(out / 'binding.json')['source'])
        records = h.completed(page, out, source)
        assert records is not None
        for record in records:
            assert record['id'] not in by_id
            by_id[record['id']] = (record, out)
    final = []
    for r in resolved:
        watchdog.ensure()
        if r['resolution_status'] != 'resolved':
            record = dict(r, guard_status='unresolved', nice=priority(), reason=r['reason'])
        else:
            worker, out = by_id[r['id']]
            record = dict(worker)
            relative = str(Path('crops') / r['stratum'] / (r['id'] + '.png'))
            destination = h.contained(HERE, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            assert h.sha(r['original_path']) == r['original_sha256'] == record['original_sha256']
            assert h.sha(r['raster']) == r['scan']['sha']
            copy_bound(out / record['output_path'], destination, record['output_sha256'])
            record.update(worker_original_path=record['original_path'], worker_output_path=record['output_path'],
                          worker_binding=str(out / 'binding.json'), worker_binding_sha256=h.sha(out / 'binding.json'),
                          original_path=r['original_path'], output_path=relative, masked_path=relative,
                          source_raster=r['raster'], source_raster_sha256=r['scan']['sha'],
                          stratum=r['stratum'], training_release_allowed=False, train_pool_eligible=False)
            if record['guard_status'] == 'failed_page':
                record.update(guard_status='unresolved', reason=record['page_error'], worker_guard_status='failed_page')
        final.append(record)
    # Complete final pass before publishing either aggregate.
    for r in final:
        if r.get('original_sha256'):
            assert h.sha(r['original_path']) == r['original_sha256']
        if r.get('output_sha256'):
            assert h.sha(HERE / r['output_path']) == r['output_sha256']
    h.write_rows(HERE / 'records.jsonl', final)
    per = {}
    for s, total in [('ii', 200), ('i-b', 400)]:
        counts = Counter(r['guard_status'] for r in final if r['stratum'] == s)
        assert sum(counts.values()) == total
        per[s] = dict(total=total, masked=counts['masked'], guarded=counts['guarded_original'],
                      unmatched=counts['unmatched_original'], unresolved=counts['unresolved'])
    summary = dict(task='T6i2', state='completed', per_stratum=per, min_nice=MIN_NICE,
        nice=sorted({r['nice'] for r in final}), workers=WORKERS, mock_5_identical=compare_mock()['ok'],
        records_sha256=h.sha(HERE / 'records.jsonl'), resolution_sha256=h.sha(HERE / 'resolution.jsonl'),
        tree_sha=h.TREE, params_sha256=h.PARAM, minimum_free_bytes=watchdog.minimum_free,
        originals_rehashed=600, outputs_rehashed=sum(bool(r.get('output_sha256')) for r in final),
        training_release_allowed=False, train_pool_eligible=False)
    h.write_json(HERE / 'summary.json', summary)
    print(__import__('json').dumps(summary), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['run', 'mock', 'page'])
    p.add_argument('--out', type=Path)
    p.add_argument('--index', type=int)
    a = p.parse_args()
    h.offline()
    priority()
    # Resource policy binding only. The T6h file and page_worker are unchanged.
    h.priority = priority
    if a.mode == 'page':
        assert a.out.resolve().is_relative_to(HERE) and a.out.absolute() == a.out.resolve()
        h.page_worker(a.out, a.index)
        return
    with (HERE / '.run.lock').open('a') as lock:
        h.fcntl.flock(lock, h.fcntl.LOCK_EX | h.fcntl.LOCK_NB)
        with h.DiskWatchdog(HERE) as watchdog:
            mock(watchdog)  # Any identity mismatch aborts before locked processing.
            if a.mode == 'run':
                resolved = population()
                jobs = locked_jobs(resolved, watchdog)
                execute(jobs, watchdog)
                finalize(resolved, jobs, watchdog)

if __name__ == '__main__':
    main()
