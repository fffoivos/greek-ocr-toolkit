#!/usr/bin/env python3
"""Create FROZEN_TRAINED.json and P1_LABELS.json on a CPU node; no credentials or network."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

sys.dont_write_bytecode = True
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from . import card, layered
from .build_locks import REVISION, WAVES, validate_frozen, validate_labels
from .common import atomic_json, canonical, digest, info, offline, records, sha, verify_file
from .progress import Progress, active
from .frozen_identity import occurrence_mapping, public_file


def frozen_lock(tree_path, a1_path, public_snapshot_root=None):
    tree = json.loads(tree_path.read_text())
    a1 = card.validate_a1(json.loads(a1_path.read_text()))
    mapping = occurrence_mapping(a1)
    public_snapshot_root = (public_snapshot_root or tree_path.parent).resolve()
    identities = {f['public_path']: f for f in a1['files']}
    files, configs = [], {}
    for item in sorted(tree, key=lambda v: v['path']):
        if not item['path'].startswith(('data/real/', 'data/synthetic/')):
            continue
        a = identities.get(item['path'])
        if a is None or not item.get('lfs') or item['size'] != item['lfs']['size']:
            raise ValueError('public trained path lacks A1 identity or matching LFS size')
        f = dict(path=item['path'], bytes=item['size'], sha256=item['lfs']['sha256'],
                 pool=a['pool'], source_shard=a['source_shard'])
        verify_file({**f, 'path': str(public_file(public_snapshot_root, f['path']))})
        files.append(f)
        _, config, split, _ = item['path'].split('/', 3)
        configs.setdefault(config, {}).setdefault(split, []).append(item['path'])
    return validate_frozen(dict(schema='hfd-frozen-trained-v1', repo='fffoivos/greek-ocr-lines',
        revision=REVISION, a1=info(a1_path), public_tree=info(tree_path), files=files, configs=configs,
        public_snapshot_root=str(public_snapshot_root), occurrence_mapping=mapping), a1_path)


def label_lock(recovery, out, allow_partial=False):
    with Progress('locks:labels'):
        return _label_lock(recovery, out, allow_partial)


def _label_lock(recovery, out, allow_partial=False):
    """Consume closed recovery products only. Never read the writer's working SQLite DB.

    Add the exact metadata occurrence locator required by Builder.import_label_variants.
    Keep the recovered release observation under its own variant; Builder owns 'release'.
    """
    coverage_path, labels_path = recovery / 'COVERAGE.json', recovery / 'labels.parquet'
    ready = coverage_path.is_file() and labels_path.is_file()
    coverage = json.loads(coverage_path.read_text()) if ready else {}
    if ready and coverage.get('status') != 'PASS' and not allow_partial:
        raise ValueError('recovery COVERAGE is not PASS')
    per_wave = {w: dict(rows=0, raw_hash_equal=0, label_rows=0, complete=False) for w in WAVES}
    complete = ready and coverage.get('status') == 'PASS' and not coverage.get('absent_waves') and all(coverage.get('per_wave', {}).get(w, {}).get('rows', 0) for w in WAVES)
    if not complete and not allow_partial:
        raise ValueError('partial recovery waves; --allow-partial is smoke only')
    files, adapters = [], []
    excluded = defaultdict(Counter)
    route_texts_suppressed = Counter()
    if ready:
        # COVERAGE is written after Parquet closes. Sidecar streams may still be in flight;
        # require both for final locks, and hash/readback all closed semantic outputs.
        selected = [labels_path, coverage_path]
        for name in ('MISMATCHES.jsonl', 'RAW_NE_FINAL.jsonl'):
            p = recovery / name
            if not p.is_file():
                if not allow_partial:
                    raise ValueError('recovery sidecar not complete: ' + name)
                complete = False
            else:
                selected.append(p)
        files = [info(p) for p in selected]
        metadata_sha = coverage['input_sha256']['metadata']
        metadata = Path(coverage.get('metadata_path') or '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_with_gennadius_cached_v4/metadata.jsonl')
        # Recover the exact path from a recorded release locator, not a new source guess.
        for r in records(labels_path):
            if r['label_variant'] == 'release' and r.get('source_locator'):
                metadata = Path(json.loads(r['source_locator'])['path'])
                break
        metadata_entry = info(metadata)
        if metadata_entry['sha256'] != metadata_sha:
            raise ValueError('recovery metadata SHA mismatch')
        files.append(metadata_entry)
        adapter_path = out / 'P1_ADAPTER.jsonl'
        if adapter_path.exists():
            raise ValueError('adapter output must be fresh')
        with tempfile.TemporaryDirectory(prefix='hfd-lock-', dir=out) as scratch:
            with sqlite3.connect(':memory:') as db:
                # Disposable index, never a resume artifact. Keep hot B-trees in RAM;
                # default SQLite's 2 MiB disk cache thrashes on millions of seen keys.
                # ~0.5M metadata / 3.5M compact keys fit the prescribed 32 GiB job.
                db.executescript('PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; '
                                 'PRAGMA cache_size=-262144; PRAGMA temp_store=MEMORY;')
                db.execute('CREATE TABLE rows(k TEXT PRIMARY KEY,locator TEXT,raw_sha TEXT,wave TEXT,changed INTEGER) WITHOUT ROWID')
                expected = Counter()
                for n, row in enumerate(records(metadata)):
                    key = row.get('row_key') or digest(canonical(['harvest:' + row['wave'], row['id']]))
                    locator = canonical(dict(path=str(metadata), ordinal=n, sha256=metadata_sha))
                    db.execute('INSERT INTO rows VALUES(?,?,?,?,?)', (key, locator, row.get('raw_text_sha256'), row['wave'], row.get('raw_text_sha256') != row.get('label_sha256')))
                    expected[row['wave']] += 1
                    active.get().rows += 1
                db.execute('CREATE TABLE seen(k TEXT,variant TEXT,PRIMARY KEY(k,variant)) WITHOUT ROWID')
                observed = defaultdict(Counter)
                partial_path = adapter_path.with_suffix('.jsonl.partial')
                with partial_path.open('w') as stream:
                    for row in layered.adapter_rows([labels_path]):
                        target = db.execute('SELECT locator,raw_sha,wave FROM rows WHERE k=?', (row['row_key'],)).fetchone()
                        if target is None or target[2] != row['wave'] or row['wave'] not in WAVES:
                            raise ValueError('recovery row/wave absent from recorded metadata')
                        db.execute('INSERT INTO seen VALUES(?,?)', (row['row_key'], row['label_variant']))
                        active.get().rows += 1
                        projected = layered.publication_label(row)
                        if projected is None:
                            excluded[row['label_variant']]['rows'] += 1
                            excluded[row['label_variant']]['non_null_texts'] += row['text'] is not None
                            continue
                        if row['text'] is not None and projected['text'] is None:
                            route_texts_suppressed[row['label_variant']] += 1
                        row = projected
                        row['row_source_locator'] = target[0]
                        if row['label_variant'] == 'raw':
                            if row['text'] is not None and row['text_sha256'] != target[1]:
                                raise ValueError('recovery raw hash differs from metadata')
                            observed[row['wave']]['rows'] += 1
                            observed[row['wave']]['raw_hash_equal'] += row['text'] is not None
                        if row['label_variant'] == 'release':
                            row['original_label_variant'] = 'release'
                            row['label_variant'] = 'recovered_release'
                        observed[row['wave']]['label_rows'] += 1
                        stream.write(canonical(row) + '\n')
                for w in WAVES:
                    stats = observed[w]
                    report = coverage.get('per_wave', {}).get(w, {})
                    if stats['rows'] != report.get('rows', 0) or stats['raw_hash_equal'] != report.get('raw_hash_equal', 0):
                        raise ValueError('recovery counts differ from Parquet: ' + w)
                    full_wave = stats['rows'] == expected[w] and expected[w] > 0
                    per_wave[w] = dict(rows=stats['rows'], raw_hash_equal=stats['raw_hash_equal'],
                                       label_rows=stats['label_rows'], complete=full_wave)
                    complete = complete and full_wave
                # COVERAGE precedes the sidecars in P1's writer. Prove their entire
                # denominators, so a concurrently open/truncated sidecar is not final.
                for name in ('MISMATCHES.jsonl', 'RAW_NE_FINAL.jsonl'):
                    sidecar = recovery / name
                    if not sidecar.is_file():
                        continue
                    db.execute('CREATE TABLE sidecar_seen(k TEXT PRIMARY KEY) WITHOUT ROWID')
                    counts = Counter()
                    for row in records(sidecar):
                        target = db.execute('SELECT wave,changed FROM rows WHERE k=?', (row['row_key'],)).fetchone()
                        if not target or target[0] != row['wave'] or name == 'RAW_NE_FINAL.jsonl' and not target[1]:
                            raise ValueError('sidecar key differs from metadata: ' + name)
                        db.execute('INSERT INTO sidecar_seen VALUES(?)', (row['row_key'],))
                        counts[row['wave']] += 1
                        active.get().rows += 1
                    for w in WAVES:
                        if name == 'RAW_NE_FINAL.jsonl':
                            expected_count = db.execute('SELECT COUNT(*) FROM rows WHERE wave=? AND changed=1', (w,)).fetchone()[0]
                        else:
                            stats = coverage.get('per_wave', {}).get(w, {})
                            expected_count = stats.get('rows', 0) - stats.get('chain_ends_at_release_hash', 0)
                        if counts[w] != expected_count:
                            complete = False
                    db.execute('DROP TABLE sidecar_seen')
                if not complete and not allow_partial:
                    raise ValueError('partial recovery waves or sidecars; --allow-partial is smoke only')
                partial_path.replace(adapter_path)
        adapter_entry = info(adapter_path)
        files.append(adapter_entry)
        adapters = [dict(name='p1_recovery', producer='p1_recovery', producer_version='recorded-edits-v1', files=[adapter_entry])]
        for f in files:
            if info(Path(f['path'])) != f:
                raise ValueError('recovery changed while locking')
    return validate_labels(dict(schema='hfd-labels-v1', partial=not complete,
        smoke_only=not complete, per_wave=per_wave, files=files, label_variant_adapters=adapters,
        raw_text_responses={w: per_wave[w]['raw_hash_equal'] > 0 for w in WAVES},
        publication_projection=dict(decision='STATE 2026-10-29 18:06',
            allowed_variants=sorted(layered.PUBLIC_ADAPTER_VARIANTS - {'recovered_release'}),
            release_adapter_variant='recovered_release', route_text='null with recorded status and reason',
            excluded_variants={k: dict(v) for k, v in sorted(excluded.items())},
            suppressed_route_texts=dict(route_texts_suppressed)),
        excluded_work_files=['recovery.sqlite', 'recovery.sqlite-journal', 'recovery.sqlite-wal', 'recovery.sqlite-shm'],
        pending_reason=None if ready else 'No closed labels.parquet + COVERAGE.json yet; smoke has no recovery adapters'), smoke=allow_partial)


def make_locks(tree, a1, recovery, out, allow_partial=False, public_snapshot_root=None):
    out.mkdir(parents=True, exist_ok=True)
    if any((out / n).exists() for n in ('FROZEN_TRAINED.json', 'P1_LABELS.json')):
        raise ValueError('lock outputs must be fresh; use separate smoke/final directories')
    with Progress('locks:frozen'):
        frozen = frozen_lock(tree, a1, public_snapshot_root)
    labels = label_lock(recovery, out, allow_partial)
    atomic_json(out / 'FROZEN_TRAINED.json', frozen)
    atomic_json(out / 'P1_LABELS.json', labels)
    return frozen, labels


def main(argv=None):
    offline()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--public-tree', required=True, type=Path)
    p.add_argument('--a1-report', required=True, type=Path)
    p.add_argument('--public-snapshot-root', required=True, type=Path,
                   help='local pinned public HF snapshot; every frozen file is SHA verified')
    p.add_argument('--recovery-dir', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--allow-partial', action='store_true', help='smoke only; final build refuses this lock')
    a = p.parse_args(argv)
    make_locks(a.public_tree.resolve(), a.a1_report.resolve(), a.recovery_dir.resolve(), a.out.resolve(),
               a.allow_partial, a.public_snapshot_root.resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
