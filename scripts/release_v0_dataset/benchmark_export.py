#!/usr/bin/env python3
"""Offline complexity benchmark of P2e selection versus bounded indexed joins."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time
from types import SimpleNamespace

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .build_dataset import Store
from .common import canonical
from .deadline import Deadline
from .layered import current_labels, current_features, export_indexes


def old_labels(builder):
    for _, row in builder.store.rows('rows'):
        # Force the actual live P2e plan, even after the new index exists.
        labels = [json.loads(j) for j, in builder.store.db.execute("""SELECT j FROM records
            INDEXED BY sqlite_autoindex_records_1 WHERE t='label_versions'
            AND json_extract(j,'$.row_key')=? ORDER BY k""", (row['row_key'],))]
        selected = [v for v in labels if v['label_variant'] == 'release']
        if len(selected) != 1:
            raise ValueError('exactly one release label required: ' + row['row_key'])
        yield selected[0]


def old_features(builder):
    for label in old_labels(builder):
        for raw, in builder.store.db.execute("""SELECT j FROM records WHERE t='row_features'
            AND json_extract(j,'$.row_key')=? AND json_extract(j,'$.label_variant')=?""",
            (label['row_key'], label['label_version_id'])):
            yield json.loads(raw)


def measure(db, action):
    ticks = 0
    def tick():
        nonlocal ticks
        ticks += 1
        return 0
    db.set_progress_handler(tick, 100)
    started = time.monotonic()
    h = hashlib.sha256(); rows = 0
    try:
        for row in action():
            h.update((canonical(row) + '\n').encode()); rows += 1
    finally:
        db.set_progress_handler(None, 0)
    return dict(seconds=time.monotonic() - started, vm_steps_rounded=ticks * 100,
                rows=rows, logical_sha256=h.hexdigest())


def benchmark(n):
    store = Store(':memory:')
    b = SimpleNamespace(store=store, deadline=Deadline())
    for i in range(n):
        key = f'{i:08}'
        store.put('rows', dict(row_key=key, page_id=str(i % 7)))
        for variant in ('raw', 'release', 'route'):
            store.put('label_versions', dict(row_key=key, label_version_id=key + variant, label_variant=variant))
        store.put('row_features', dict(row_key=key, label_variant=key + 'release', feature_version='v1'))
    before = measure(store.db, lambda: iter_join(old_labels(b), old_features(b)))
    start = time.monotonic(); export_indexes(store.db)
    index_seconds = time.monotonic() - start
    after = measure(store.db, lambda: iter_join(current_labels(b), current_features(b)))
    store.db.close()
    assert before['logical_sha256'] == after['logical_sha256'] and before['rows'] == after['rows']
    return dict(input_rows=n, labels=3*n, before=before, after=after, index_seconds=index_seconds,
                speedup=before['seconds']/after['seconds'], vm_reduction=before['vm_steps_rounded']/after['vm_steps_rounded'])


def iter_join(a, b):
    yield from a
    yield from b


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', type=int, nargs='+', default=[1000, 2000])
    args = parser.parse_args()
    print(json.dumps({'sqlite': sqlite3.sqlite_version, 'benchmark': [benchmark(n) for n in args.rows],
                      'qualification': 'generated local metadata; no Parquet, filesystem or production timing claim'}, indent=2))
