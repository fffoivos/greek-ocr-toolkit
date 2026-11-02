"""Private SQLite readback ledger and bounded, ordered file readers.

Only the owning thread writes SQLite. Unit mutations, counters and their cursor
commit together; an interrupted unit is rolled back and replayed. The public
package stays immutable. Reuse binds code, manifest, lock and verified file stats.
"""
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import json
import os
from pathlib import Path
from queue import Queue, Full
import threading

import pyarrow.parquet as pq

from .common import canonical, sha, verify_file
from .deadline import active_deadline, atomic_boundary, Deadline


def workers():
    return max(1, min(8, int(os.environ.get('SLURM_CPUS_PER_TASK', '8')), os.cpu_count() or 1))


def stamp(path):
    p = Path(path).resolve()
    s = p.stat()
    return [str(p), s.st_size, s.st_mtime_ns, s.st_ino]


def restore(template, value):
    if isinstance(template, Counter):
        return Counter(value)
    if isinstance(template, dict):
        result = template.copy()
        result.clear()
        for key, v in value.items():
            result[key] = restore(template[key] if isinstance(template, defaultdict) else template.get(key), v)
        return result
    return value


class Ledger:
    def __init__(self, owner, scratch):
        self.a, self.db = owner, owner.db
        self.deadline = active_deadline.get() or Deadline()
        self.db.executescript('''CREATE TABLE IF NOT EXISTS readback_units(k TEXT PRIMARY KEY,j TEXT);
            CREATE TABLE IF NOT EXISTS readback_verified(path TEXT PRIMARY KEY,j TEXT);
            CREATE TABLE IF NOT EXISTS readback_binding(j TEXT);''')
        frozen = json.loads((owner.root / 'manifests/MANIFEST.json').read_text()).get('frozen_trained', {})
        from .frozen_identity import public_file
        # Bind cache links as well as blob stats: retargeting a snapshot link must
        # not reuse a completed frozen stage on resume.
        frozen_targets = {f['path']: str(public_file(frozen['public_snapshot_root'], f['path']))
                          for f in frozen.get('files', [])} if owner.validation_mode == 'external-cache' and frozen.get('public_snapshot_root') else {}
        # Final mode, the enrichment base (revalidated by content on every run), the
        # E1 receipt/verifier code and supplementary sources all gate reuse of saved stages.
        from .layer_acceptance import enrichment_identity
        self.enrichment_identity = enrichment_identity(owner.root, getattr(owner, 'enrich_base', None))
        binding = canonical(dict(root=str(owner.root), manifest=sha(owner.root / 'manifests/MANIFEST.json'),
            lock=sha(owner.lock_path) if owner.lock_path else None, allow_smoke=owner.allow_smoke,
            frozen_targets=frozen_targets, validation_mode=owner.validation_mode,
            final=bool(getattr(owner, 'final', False)), enrichment=self.enrichment_identity,
            code={p.name: sha(p) for p in sorted(Path(__file__).parent.glob('*.py'))}))
        saved = self.db.execute('SELECT j FROM readback_binding').fetchone()
        if saved and saved[0] != binding:
            raise ValueError('readback resume binding changed; use a fresh scratch directory')
        if not saved:
            self.db.execute('INSERT INTO readback_binding VALUES(?)', (binding,))
            self.db.commit()
        for path, raw in self.db.execute('SELECT path,j FROM readback_verified'):
            if json.loads(raw) != stamp(path):
                raise ValueError('readback verified input changed: ' + path)

    def snapshot(self):
        a = self.a
        attrs = {k: getattr(a, k) for k in ('image_count', 'source_checks', 'binding_source_checks',
                 'feature_checks', 'loader', 'roundtrip_rows', 'frozen_available') if hasattr(a, k)}
        if hasattr(a, 'policy'):
            attrs['policy_nulls'] = a.policy.nulls
            attrs['slice_comparisons'] = a.policy.slice_comparisons
        return attrs

    def apply(self, attrs):
        for key, value in attrs.items():
            if key == 'policy_nulls':
                self.a.policy.nulls = defaultdict(Counter, {k: Counter(v) for k, v in value.items()})
            elif key == 'slice_comparisons':
                self.a.policy.slice_comparisons = value
            else:
                setattr(self.a, key, value)

    def saved(self, key, state=None):
        row = self.db.execute('SELECT j FROM readback_units WHERE k=?', (key,)).fetchone()
        if row:
            value = json.loads(row[0])
            self.apply(value['runtime'])
            if state is not None:
                updated = restore(state, value['state'])
                state.clear(); state.update(updated)
            return value

    def save(self, key, state=None, result=None, identity=None):
        with atomic_boundary():
            value = dict(runtime=self.snapshot(), state=state or {}, result=result)
            if identity is not None:
                value['identity'] = identity
            self.db.execute('INSERT OR REPLACE INTO readback_units VALUES(?,?)', (key, canonical(value)))
            self.db.commit()
        self.a.transaction_boundary(key)
        self.deadline.check()

    @contextmanager
    def unit(self, key, state=None):
        saved = self.saved(key, state)
        if saved:
            yield False
            return
        self.deadline.check()
        try:
            yield True
            self.save(key, state)
        except BaseException:
            self.db.rollback()
            raise

    def stage(self, name, action, identity=None):
        key = 'stage:' + name
        saved = self.saved(key)
        if saved:
            # A result is only reusable under the identity it was computed for.
            if identity is not None and saved.get('identity') != json.loads(canonical(identity)):
                raise ValueError('cached readback stage identity changed: ' + name + '; use a fresh scratch directory')
            return saved['result']
        from .progress import Progress
        self.deadline.check()
        previous = getattr(self.a, '_ledger_running', False)
        self.a._ledger_running = True
        try:
            with Progress('readback:' + name):
                result = action()
        finally:
            self.a._ledger_running = previous
        self.save(key, result=result, identity=identity)
        return result

    def verify_many(self, entries):
        """At most eight in-flight SHA reads, committing each closed file."""
        pending = deque()
        pool = ThreadPoolExecutor(max_workers=workers())
        def verify(entry):
            before = stamp(entry['path'])
            verify_file(entry)
            if before != stamp(entry['path']):
                raise ValueError('input changed during readback: ' + entry['path'])
            return before
        def wanted():
            for entry in entries:
                self.deadline.check()
                path = str(Path(entry['path']).resolve())
                if self.db.execute('SELECT 1 FROM readback_verified WHERE path=?', (path,)).fetchone():
                    # Ledger constructor verified the saved stat for this invocation.
                    continue
                yield entry
        iterator = iter(wanted())
        try:
            for _ in range(workers()):
                entry = next(iterator, None)
                if entry is None: break
                pending.append((entry, pool.submit(verify, entry)))
            while pending:
                entry, future = pending.popleft()
                measured = future.result()
                self.db.execute('INSERT OR REPLACE INTO readback_verified VALUES(?,?)',
                                (measured[0], canonical(measured)))
                self.save('hash:' + measured[0])
                entry = next(iterator, None)
                if entry is not None:
                    pending.append((entry, pool.submit(verify, entry)))
        finally:
            pool.shutdown(wait=True, cancel_futures=True)


def parquet_files(paths):
    """Read/decompress independent shards on <=8 CPUs; <=2 batches per reader.

    Consume in manifest order for identical duplicate checks and sample choices.
    Cancellation never waits for a producer blocked on a full queue.
    """
    paths = iter(paths)
    stop = threading.Event()
    pool = ThreadPoolExecutor(max_workers=workers())
    pending = deque()
    end = object()
    def produce(path, queue):
        def put(value):
            while not stop.is_set():
                try:
                    queue.put(value, timeout=.05)
                    return
                except Full:
                    pass
        try:
            pf = pq.ParquetFile(path)
            for batch in pf.iter_batches(batch_size=128, use_threads=False):
                if stop.is_set(): break
                put(batch.to_pylist())
        except BaseException as exc:
            put(exc)
        finally:
            put(end)
    def submit():
        path = next(paths, None)
        if path is None: return
        queue = Queue(maxsize=2)
        pending.append((path, queue, pool.submit(produce, path, queue)))
    try:
        for _ in range(workers()): submit()
        while pending:
            path, queue, future = pending.popleft()
            def rows():
                while True:
                    value = queue.get()
                    if value is end: break
                    if isinstance(value, BaseException): raise value
                    yield from value
            yield path, rows()
            future.result()
            submit()
    finally:
        stop.set()
        pool.shutdown(wait=True, cancel_futures=True)
