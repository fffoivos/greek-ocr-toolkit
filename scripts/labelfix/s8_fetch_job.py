"""S8a3: compute-only, stdlib-only resume of selected saved L1M evidence.

No submission, inference, network access, or login-node extraction. Python 3.6+.
The local `mock` subcommand invokes the same run/merge/checkpoint entry point.
"""
from greekocr.ops.data_root import input_path as _data_input
import argparse
import fcntl
import gzip
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import socket
import sys
import tempfile
import time
import unicodedata

try:
    from . import s8_fetch_l1m as l1m
except ImportError:
    import s8_fetch_l1m as l1m

BASE = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
OUT = BASE / 's8_dev_extract'
DONE = dict(BE='BE_done', A='A_done', alignment='alignment_done')


def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()


def read_gzip(path):
    return json.loads(gzip.decompress(_data_input(Path(path)).read_bytes()))


def atomic_json(path, value, compressed=False):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    if compressed:
        raw = gzip.compress(raw, compresslevel=3)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)


def request_sha(request):
    # Exact S8a2 identity serialization, including its default ASCII escaping.
    return hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()


def progress(data, request):
    ids = set(request['ids'])
    data['missing_runtime_ids'] = sorted(ids - set(data['runtime']))
    data['missing_A_ids'] = sorted(k for k in ids if not data['runtime'].get(k, {}).get('historical_A_verified'))
    data['missing_alignment_ids'] = sorted(set(request['missing_alignment_ids']) - set(data['alignments']))
    data['complete'] = not any(data[k] for k in ('missing_runtime_ids', 'missing_A_ids', 'missing_alignment_ids'))
    return {key: len(data[value]) for key, value in DONE.items()}


def load_resume(config):
    base, out = Path(config['base']), Path(config['out'])
    if out.resolve() != base.resolve() / 's8_dev_extract':
        raise ValueError('output must be the dedicated s8_dev_extract directory')
    request = json.loads((out / 'request.json').read_text())
    fingerprint = request_sha(request)
    data = read_gzip(out / 'partial.json.gz')  # Required; never silently start fresh.
    if fingerprint != config['request_sha256'] or data['request_sha256'] != fingerprint:
        raise ValueError('request SHA mismatch; checkpoint cannot be resumed')
    ids, missing = set(request['ids']), set(request['missing_alignment_ids'])
    if len(ids) != len(request['ids']) or len(ids) != config['expected_ids'] or not missing <= ids:
        raise ValueError('invalid request population')
    if set(request['crop_to_id'].values()) != ids:
        raise ValueError('crop join differs from request population')
    cache_path = Path(config['local_alignment_cache'])
    if sha(cache_path) != config['local_alignment_sha256']:
        raise ValueError('local alignment cache SHA mismatch')
    cache = read_gzip(cache_path)
    if set(cache) != ids - missing:
        raise ValueError('local alignment cache does not exactly complement remote request')
    if not set(data['runtime']) <= ids or not set(data['alignments']) <= missing:
        raise ValueError('checkpoint contains unrequested evidence')
    if data['schema'] != 's8a2-l1m-selected-v1' or data['remote_scratch'] != str(out):
        raise ValueError('checkpoint schema or output identity mismatch')
    for key in DONE.values():
        if len(data[key]) != len(set(data[key])):
            raise ValueError('duplicate checkpoint shard: ' + key)
    shards = dict(BE=sorted((base / 'l1e_20261017/output_3679545/inference').glob('shard-*-combined.jsonl.gz')),
                  A=sorted((base / 'output_3679313/combined').glob('shard-*-combined.jsonl.gz')),
                  alignment=sorted((base / 'output_3679313/alignment').glob('worker_*.jsonl.gz')))
    if len(shards['BE']) != config['expected_BE_shards']:
        raise ValueError('B/E shard inventory changed')
    for kind, paths in shards.items():
        if not set(data[DONE[kind]]) <= {p.name for p in paths}:
            raise ValueError('checkpoint shard missing from input inventory: ' + kind)
    for key, row in data['runtime'].items():
        if row['id'] != key or row['BE_shard'] not in {p.name for p in shards['BE']}:
            raise ValueError('checkpoint runtime/shard mismatch: ' + key)
        if bool(row.get('historical_A_verified')) != (row['BE_shard'] in data['A_done']):
            raise ValueError('checkpoint A verification/done mismatch: ' + key)
        for field in l1m.S8_FIELDS:
            if l1m.s8_digest(row[field]) != row['historical_field_sha256'][field]:
                raise ValueError('checkpoint field digest mismatch: ' + key)
    return request, data, cache, shards


def merge(data, result, request):
    kind, name, records, provenance = result
    if kind == 'BE':
        # S8a2's timeout could save selected rows before committing BE_done.
        # Re-read that shard and accept only byte-equivalent selected fields.
        for key in set(records) & set(data['runtime']):
            if records[key] != data['runtime'][key]:
                raise ValueError('duplicate/conflicting B/E selected ID across shards')
        data['runtime'].update(records)
    elif kind == 'A':
        expected = {k for k, row in data['runtime'].items() if row['BE_shard'] == name}
        if set(records) != expected:
            raise ValueError('historical A shard lacks selected IDs: ' + name)
        # Validate the whole result before mutating any verification flag.
        for key, hashes in records.items():
            if hashes != data['runtime'][key]['historical_field_sha256']:
                raise ValueError('historical A mismatch: ' + key)
        for key in records:
            data['runtime'][key]['historical_A_verified'] = True
    else:
        for key, row in records.items():
            if key in data['alignments'] and row != data['alignments'][key]:
                raise ValueError('conflicting saved alignments: ' + key)
        data['alignments'].update(records)
    if records:
        data['provenance'].append(provenance)
    data[DONE[kind]].append(name)
    progress(data, request)


def worker_init():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


def allocation_guard(config):
    if Path(config['base']) != BASE or Path(config['out']) != OUT:
        raise ValueError('production paths must match the fixed S8 scratch contract')
    if (not os.environ.get('SLURM_JOB_ID') or os.environ.get('SLURM_JOB_PARTITION') != 'debug'
            or os.environ.get('SLURM_JOB_NUM_NODES') != '1' or not socket.gethostname().startswith('nid')):
        raise ValueError('STOP: extraction requires a one-node Slurm debug compute allocation')
    if not 16 <= config['workers'] <= 32 or int(os.environ.get('SLURM_CPUS_PER_TASK', '0')) < config['workers']:
        raise ValueError('require 16-32 workers within allocated CPUs')
    if not 0 < config['budget_seconds'] <= 1050:
        raise ValueError('compute budget must leave reserve within the 20 minute job')


def run(config, mock=False):
    if not mock:
        allocation_guard(config)
    elif Path(config['base']).resolve() == BASE:
        raise ValueError('mock cannot access production inputs')
    out = Path(config['out'])
    # Nonblocking exclusion: two coordinator submissions cannot corrupt partial.
    with (out / 'job.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return run_locked(config)


def run_locked(config):
    started = time.monotonic()
    request, data, cache, shards = load_resume(config)
    out = Path(config['out'])
    initial_sha = sha(out / 'partial.json.gz')
    initial = dict(progress(data, request), runtime=len(data['runtime']), alignments=len(data['alignments']))
    data.update(workers=config['workers'], threads=1, inference_runs=0,
                extraction_mode='s8a3-debug-shards', ids=sorted(request['ids']))
    data.pop('last_error', None)
    pool = None
    old_signals = {}
    failure = None

    def interrupted(signum, frame):
        raise InterruptedError('allocation signal {}'.format(signum))

    def save():
        progress(data, request)
        data['last_attempt_seconds'] = time.monotonic() - started
        atomic_json(out / 'partial.json.gz', data, compressed=True)

    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            old_signals[sig] = signal.signal(sig, interrupted)
        if time.monotonic() - started >= config['budget_seconds']:
            raise TimeoutError('compute extraction budget exhausted; checkpoint retained')
        # Explicit spawn avoids inheriting unrelated runtime threads/locks when
        # exercised inside the full detector/reader regression suite.
        pool = multiprocessing.get_context('spawn').Pool(config['workers'], initializer=worker_init)
        for kind in ('BE', 'A', 'alignment'):
            tasks = []
            for path in shards[kind]:
                if path.name in data[DONE[kind]]:
                    continue
                wanted = set(request['ids']) if kind == 'BE' else (
                    {k for k, row in data['runtime'].items() if row['BE_shard'] == path.name}
                    if kind == 'A' else set(request['missing_alignment_ids']) - set(data['alignments']))
                if kind != 'BE' and not wanted:
                    continue
                tasks.append((kind, str(path), wanted, request['crop_to_id'] if kind == 'alignment' else {}))
            results = pool.imap_unordered(l1m.s8_read_shard, tasks, chunksize=1)
            remaining = len(tasks)
            while remaining:
                if time.monotonic() - started >= config['budget_seconds']:
                    raise TimeoutError('compute extraction budget exhausted; checkpoint retained')
                try:
                    result = results.next(timeout=0.5)
                except multiprocessing.TimeoutError:
                    continue
                merge(data, result, request)
                remaining -= 1
                save()
                print(json.dumps(dict(stage=kind, remaining_shards=remaining, completed=progress(data, request))), flush=True)
            if kind == 'BE' and set(data['runtime']) != set(request['ids']):
                raise ValueError('B/E inventory lacks requested runtime IDs')
            if kind == 'A' and any(not r.get('historical_A_verified') for r in data['runtime'].values()):
                raise ValueError('historical A verification incomplete')
        progress(data, request)
        if not data['complete']:
            raise ValueError('requested saved alignments incomplete')
        # partial retains only the 166 requested remote alignments for next resume.
        final = dict(data, alignments=dict(data['alignments'], **cache))
        if set(final['alignments']) != set(request['ids']):
            raise ValueError('final alignment population mismatch')
        for key, row in final['alignments'].items():
            if unicodedata.normalize('NFD', final['runtime'][key]['recogniser_text']) != row['alignment']['prediction']:
                raise ValueError('saved alignment/recogniser identity mismatch: ' + key)
        final['local_alignment_custody'] = dict(path=config['local_alignment_cache'], sha256=config['local_alignment_sha256'])
        final['last_attempt_seconds'] = time.monotonic() - started
        atomic_json(out / 'remote.json.gz', final, compressed=True)
    except Exception as exc:
        failure = exc
        data['last_error'] = repr(exc)
        data['complete'] = False
    finally:
        # Terminate in-flight readers at deadline; do not wait for an entire shard.
        if pool is not None:
            pool.terminate()
            pool.join()
        # Prevent a second signal from interrupting the final atomic checkpoint.
        for sig in old_signals:
            signal.signal(sig, signal.SIG_IGN)
        save()
        receipt = dict(schema='s8a3-fetch-receipt-v1', complete=failure is None,
                       request_sha256=data['request_sha256'], initial_checkpoint_sha256=initial_sha,
                       checkpoint_sha256=sha(out / 'partial.json.gz'), initial=initial,
                       final=dict(progress(data, request), runtime=len(data['runtime']), alignments=len(data['alignments'])),
                       seconds=time.monotonic() - started, workers=config['workers'], threads=1,
                       python=sys.version, python_executable=sys.executable, hostname=socket.gethostname(),
                       slurm_job_id=os.environ.get('SLURM_JOB_ID'), inference_runs=0,
                       input_writes=0, error=repr(failure) if failure else None,
                       custody_limit=data.get('custody_limit'), local_alignment_sha256=config['local_alignment_sha256'])
        if failure is None:
            receipt['remote_sha256'] = sha(out / 'remote.json.gz')
            receipt['final']['merged_alignments'] = len(final['alignments'])
        atomic_json(out / 'receipt.json', receipt)
        for sig, previous in old_signals.items():
            signal.signal(sig, previous)
    if failure is not None:
        raise failure
    return receipt


def make_mock(root):
    """Three lines, three combined shards, two crop-key alignment workers."""
    base = Path(root)
    out = base / 's8_dev_extract'
    out.mkdir(parents=True)
    request = dict(ids=['one', 'two', 'three'], missing_alignment_ids=['two', 'three'],
                   crop_to_id={'docs/harvest/mock/' + key + '.png': key for key in ('one', 'two', 'three')})
    atomic_json(out / 'request.json', request)
    data = dict(schema='s8a2-l1m-selected-v1', runtime={}, alignments={}, provenance=[],
                BE_done=[], A_done=[], alignment_done=[], request_sha256=request_sha(request),
                remote_scratch=str(out), submitted_jobs=0, inference_runs=0,
                custody_limit='Synthetic L1M-format saved evidence; no inference.')

    def jsonl(path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(('\n'.join(json.dumps(row, ensure_ascii=False) for row in rows) + '\n').encode()))

    for i, key in enumerate(request['ids']):
        name = 'shard-{:05d}-combined.jsonl.gz'.format(i)
        row = dict(id=key, recogniser_text='ἄλφα', recogniser_nfd='ἄλφα', coverage=[dict(start=0)],
                   r1_predictions=[dict(start=0, cls='psili+acute')], peer_predictions=dict(B=[], E=[]),
                   peer_coverage=dict(B=[], E=[]), detector={'must_not_fetch': True})
        for folder in ('l1e_20261017/output_3679545/inference', 'output_3679313/combined'):
            path = base / folder / name
            jsonl(path, [dict(row, id='unselected'), row])
            atomic_json(path.with_name(name.replace('-combined.jsonl.gz', '-receipt.json')), dict(mock=True))
    alignment = lambda key: dict(crop='/old/worktree/docs/harvest/mock/' + key + '.png',
                                 alignment=dict(prediction='ἄλφα', spans=[], confidence=1.0))
    for i, key in enumerate(('two', 'three')):
        jsonl(base / 'output_3679313/alignment' / ('worker_{}.jsonl.gz'.format(i)),
              [alignment('unselected'), alignment(key)])
    cache = out / 'dev_c1_alignments.json.gz'
    atomic_json(cache, {'one': alignment('one')}, compressed=True)
    # Genuine pre-existing S8a2 checkpoint: first B/E shard already extracted.
    first = base / 'l1e_20261017/output_3679545/inference/shard-00000-combined.jsonl.gz'
    merge(data, l1m.s8_read_shard(('BE', str(first), {'one'}, {})), request)
    atomic_json(out / 'partial.json.gz', data, compressed=True)
    return dict(base=str(base), out=str(out), request_sha256=request_sha(request), expected_ids=3,
                expected_BE_shards=3, workers=16, budget_seconds=30,
                local_alignment_cache=str(cache), local_alignment_sha256=sha(cache))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command')
    real = sub.add_parser('run')
    real.add_argument('--config', type=Path, required=True)
    mock = sub.add_parser('mock')
    mock.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'run':
        result = run(json.loads(args.config.read_text()))
    elif args.command == 'mock':
        with tempfile.TemporaryDirectory(prefix='s8a3-mock-') as tmp:
            config = make_mock(Path(tmp) / 'fixture')
            before = {str(p): sha(p) for p in Path(config['base']).rglob('*')
                      if p.is_file() and Path(config['out']) not in p.parents}
            for name in ('request.json', 'dev_c1_alignments.json.gz'):
                path = Path(config['out']) / name
                before[str(path)] = sha(path)
            result = run(config, mock=True)
            final = read_gzip(Path(config['out']) / 'remote.json.gz')
            assert result['initial']['BE'] == 1 and result['final']['merged_alignments'] == 3
            assert set(final['runtime']) == set(final['alignments']) == {'one', 'two', 'three'}
            assert all('detector' not in row and row['historical_A_verified'] for row in final['runtime'].values())
            assert all(sha(path) == digest for path, digest in before.items())
            # A completed checkpoint is itself resumable, with no repeated reads.
            rerun = run(config, mock=True)
            assert rerun['initial']['BE'] == 3 and rerun['initial']['A'] == 3
            result.update(mock_ok=True, input_hashes_unchanged=True, completed_resume_ok=True)
        atomic_json(args.receipt, result)
    else:
        parser.error('choose run or mock')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
