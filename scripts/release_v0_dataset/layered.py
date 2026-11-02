"""Layered physical export. The frozen trainer view is supplied separately by A1."""
from collections import defaultdict
import json
import itertools
from pathlib import Path
import re

import pyarrow.parquet as pq

from .deadline import atomic_boundary
from .common import (Shards, TABLES, atomic_json, canonical, digest, info, records,
                     safe_path, schema, verify_file)

LAYER_CONFIGS = (set(TABLES) - {'label_versions'}) | {
    'label_versions', 'lines', 'labels_current', 'current_features', 'crops', 'synthetic_lines'}
TEXT_FIELDS = {'text', 'raw_text', 'raw_text_sha256', 'gt_nfc', 'gt_nfd', 'label_ids',
               'codec_version', 'label_sha256', 'label_version', 'trainer_variants',
               'corrections_applied', 'correction_route_statuses', 'corrections_applied_json',
               'correction_route_statuses_json'}


def component(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]+', value) or value in ('.', '..'):
        raise ValueError('unsafe producer/version component: ' + str(value))
    return value


def unpack(row):
    """Typed columns plus retained provenance, used by the card join and tools."""
    result = json.loads(row.get('record_json') or '{}')
    for key, value in row.items():
        if key == 'record_json':
            continue
        if isinstance(result.get(key), (list, dict)) and isinstance(value, str):
            if canonical(result[key]) != value:
                raise ValueError('record/table projection changed: ' + key)
            value = result[key]
        elif value is not None and result.get(key) is not None and result[key] != value and str(result[key]) != value:
            raise ValueError('record/table projection changed: ' + key)
        if value is not None or key not in result:
            result[key] = value
    return result


def config_rows(root, config, configs=None):
    root = Path(root)
    configs = configs or json.loads((root / 'manifests/CONFIGS.json').read_text())
    for paths in configs[config].values():
        for path in paths:
            for batch in pq.ParquetFile(safe_path(root, path)).iter_batches(batch_size=256):
                for row in batch.to_pylist():
                    yield unpack(row)


def write_rows(builder, name, directory, rows, singleton=False):
    stage = 'layer:' + directory
    checkpoint = builder.work / (digest(stage) + '.json')
    if checkpoint.exists():
        files = json.loads(checkpoint.read_text())['files']
        for entry in files:
            verify_file({**entry, 'path': str(safe_path(builder.out, entry['path']))})
        return files
    writer = Shards(builder.out, name, directory, builder.cap, builder.target, builder.work / 'batches', stream_resume=True)
    skip = writer.committed_rows
    for n, row in enumerate(rows):
        if n < skip:
            continue
        builder.deadline.check()
        writer.add(row)
    files = writer.close()
    with atomic_boundary():
        if singleton and len(files) == 1:
            old = builder.out / files[0]['path']
            new = builder.out / (directory + '.parquet')
            old.replace(new)
            old.parent.rmdir()
            files = [{**info(new, builder.out), 'rows': files[0]['rows']}]
        atomic_json(checkpoint, {'files': files})
    builder.transaction_boundary(stage, sum(f['rows'] for f in files))
    return files


# Bounded VALUES joins avoid both Python's per-row SQL overhead and SQLite's
# preference for (t,k) when ORDER BY k accompanies a row-key JSON predicate.
EXPORT_BATCH = 256  # <= 999 SQL variables even for the three-column feature join.


def batches(rows):
    rows = iter(rows)
    while batch := list(itertools.islice(rows, EXPORT_BATCH)):
        yield batch


def export_indexes(db):
    # Build after derive: no cost on every ingest/update, and safe on resume.
    db.execute("""CREATE INDEX IF NOT EXISTS records_export_labels_row
        ON records(json_extract(j,'$.row_key'),k) WHERE t='label_versions'""")
    db.execute("""CREATE INDEX IF NOT EXISTS records_export_features_row
        ON records(json_extract(j,'$.row_key'),json_extract(j,'$.label_variant'))
        WHERE t='row_features'""")


def current_labels(builder):
    db = builder.store.db
    keys = (key for key, in db.execute(
        "SELECT json_extract(j,'$.row_key') FROM records WHERE t='rows' ORDER BY page,k"))
    for batch in batches(keys):
        builder.deadline.check()
        values = ','.join('(?,?)' for _ in batch)
        params = [v for n, key in enumerate(batch) for v in (n, key)]
        labels = defaultdict(list)
        for n, raw in db.execute(f"""WITH wanted(n,row_key) AS (VALUES {values})
            SELECT w.n,l.j FROM wanted w CROSS JOIN records l INDEXED BY records_export_labels_row
            ON l.t='label_versions' AND json_extract(l.j,'$.row_key')=w.row_key
            ORDER BY w.n,l.k""", params):
            label = json.loads(raw)
            if label['label_variant'] == 'release':
                labels[n].append(label)
        for n, key in enumerate(batch):
            if len(labels[n]) != 1:
                raise ValueError('exactly one release label required: ' + key)
            yield labels[n][0]


def current_features(builder):
    db = builder.store.db
    for batch in batches(current_labels(builder)):
        builder.deadline.check()
        values = ','.join('(?,?,?)' for _ in batch)
        params = [v for n, label in enumerate(batch)
                  for v in (n, label['row_key'], label['label_version_id'])]
        # The incumbent records_row lookup enumerated equal keys by rowid.
        # Keep that order even when several feature versions match one label.
        for raw, in db.execute(f"""WITH wanted(n,row_key,variant) AS (VALUES {values})
            SELECT f.j FROM wanted w CROSS JOIN records f INDEXED BY records_export_features_row
            ON f.t='row_features' AND json_extract(f.j,'$.row_key')=w.row_key
              AND json_extract(f.j,'$.label_variant')=w.variant
            ORDER BY w.n,f.rowid""", params):
            yield json.loads(raw)


def export(builder):
    from .progress import Progress, active
    with Progress('export:indexes') as progress:
        with builder.store.db:
            export_indexes(builder.store.db)
    builder.timings.append({**progress.result, 'diagnostic_only': True})
    configs = {}
    def emit(name, directory, rows, singleton=False):
        parent = active.get()
        with Progress('export:' + directory) as progress:
            files = write_rows(builder, name, directory, rows, singleton)
        builder.timings.append({**progress.result, 'diagnostic_only': True})
        if parent is not None:
            parent.rows += progress.rows
            parent.bytes += progress.bytes
        configs[name] = {'inventory': [f['path'] for f in files]}
        return files
    for table in TABLES:
        if table in ('label_versions', 'page_images'):
            continue
        files = builder.export_table(table)
        configs[table] = {'inventory': [f['path'] for f in files]}
    # Real group 4 and 7 are joined from labels/current_features; no hidden copy in record_json.
    excluded = TEXT_FIELDS | (set(schema('row_features').names) - {
        'row_key', 'record_json', 'source_locator', 'source_sha256', 'coordinate_frame',
        'binding_missing_reasons_json'})
    emit('lines', 'tables/lines', ({k: v for k, v in row.items() if k not in excluded}
        for _, row in builder.store.rows('rows') if row.get('release')), True)
    # Fixed sorted SHA boundaries: corrections never invoke this writer.
    def crops():
        for h, in builder.store.db.execute("SELECT DISTINCT json_extract(j,'$.crop_sha256') FROM records WHERE t='rows' AND json_extract(j,'$.original_crop_custody.hash_match')=1 ORDER BY 1"):
            payload = builder.payload(h)
            if payload:
                from .common import dimensions
                w, height = dimensions(payload['bytes'])
                yield {'crop_sha256': h, 'image_sha256': h, 'page_object_id': h,
                       'image': payload, 'width': w, 'height': height}
    image_files = emit('crops', 'images/crops', crops())
    configs['page_images'] = {'inventory': [f['path'] for f in write_rows(builder,
        'page_images', 'images/pages', ({**r, 'image': builder.payload(r.get('image_sha256'))}
            for _, r in builder.store.rows('page_images')))]}
    paths = []
    groups = builder.store.db.execute("SELECT DISTINCT json_extract(j,'$.producer'),json_extract(j,'$.producer_version') FROM records WHERE t='label_versions' ORDER BY 1,2").fetchall()
    for producer, version in groups:
        directory = 'labels/versions/' + component(producer) + '/' + component(version)
        rows = (json.loads(j) for j, in builder.store.db.execute("SELECT j FROM records WHERE t='label_versions' AND json_extract(j,'$.producer')=? AND json_extract(j,'$.producer_version')=? ORDER BY k", (producer, version)))
        paths.extend(f['path'] for f in write_rows(builder, 'label_versions', directory, rows))
    if not paths:
        paths = [f['path'] for f in write_rows(builder, 'label_versions', 'labels/versions/empty/initial', [])]
    configs['label_versions'] = {'inventory': paths}
    emit('labels_current', 'labels/current', current_labels(builder), True)
    emit('current_features', 'tables/current_features', current_features(builder), True)
    emit('synthetic_lines', 'tables/synthetic_lines', (r for _, r in builder.store.rows('synthetic')), True)
    # Rev 2 H02 permits identified non-training synthetic splits as byte views.
    identified = sorted({r['split'] for _, r in builder.store.rows('synthetic') if r['split'] in ('val', 'reserved')})
    if identified:
        configs['synthetic'] = {}
        for split in identified:
            configs['synthetic'][split] = [e['path'] for e in builder.export_table('synthetic', 'synthetic', split)]
    # A1 supplies the exact inventory and configs. Never manufacture trainer shard names.
    frozen = builder.lock.get('frozen_trained', {})
    for name in ('real', 'synthetic'):
        if name in frozen.get('configs', {}):
            configs.setdefault(name, {}).update(frozen['configs'][name])
    boundaries = []
    for entry in image_files:
        pf = pq.ParquetFile(builder.out / entry['path'])
        hashes = pf.read(columns=['crop_sha256']).column(0).to_pylist()
        boundaries.append({**entry, 'first_crop_sha256': hashes[0] if hashes else None,
                           'last_crop_sha256': hashes[-1] if hashes else None})
    return configs, boundaries


# STATE 2026-10-29 18:06: only observations and recorded statuses are public.
ROUTE_VARIANTS = frozenset(('sf7', 'ru1', 'n1', 'dashes', 'content_repair'))
PUBLIC_ADAPTER_VARIANTS = ROUTE_VARIANTS | {'raw', 'release', 'recovered_release'}


def publication_label(row):
    """Explicit allowlist shared by the lock generator and the final consumer."""
    variant = row['label_variant']
    if variant not in PUBLIC_ADAPTER_VARIANTS:
        return None
    row = dict(row)
    if variant in ROUTE_VARIANTS:
        # Retain recorded status/provenance; reconstructed or replayed text is not adopted.
        row.update(text=None, text_sha256=None,
                   reason=row.get('reason') or 'missing_recorded_edits')
    return row


def adapter_rows(paths, batch_size=8192):
    """P1 interface: nullable text requires reason; values must carry their own hashes.

    P1 proves response/anchor/code identity and recorded composition semantics.
    This adapter checks that no unverified value can be silently substituted.
    """
    required = {'row_key', 'label_variant', 'text', 'text_sha256', 'before_sha256', 'route_status', 'reason'}
    for path in paths:
        for row in records(path, {'batch_size': batch_size}):
            if not required <= row.keys():
                raise ValueError('label adapter missing fields: ' + ','.join(sorted(required - row.keys())))
            if row['text'] is None:
                if not row['reason'] or row['text_sha256'] is not None:
                    raise ValueError('null label adapter value needs reason and null hash')
            elif digest(row['text']) != row['text_sha256']:
                raise ValueError('label adapter text/hash mismatch')
            yield row
