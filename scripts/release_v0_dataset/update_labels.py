#!/usr/bin/env python3
"""Produce a metadata-only update overlay; the coordinator commits all listed paths together."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unicodedata as ud

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import (CAP, TARGET, Shards, atomic_json, canonical, digest, info,
                     offline, records, safe_path, sha, verify_file)
from .features import Features
from .layered import component, config_rows


def allowed(paths):
    for value in paths:
        p = Path(value)
        if p.is_absolute() or '..' in p.parts or not p.parts:
            raise ValueError('unsafe update path: ' + value)
        if p.parts[0] in ('data', 'images'):
            raise ValueError('update attempts immutable data/ or images/ operation: ' + value)
        if p.parts[0] not in ('labels', 'tables', 'manifests') and value not in ('README.md', 'UPDATING.md'):
            raise ValueError('update path outside metadata allowlist: ' + value)
    return list(paths)


def encode(text, codec):
    # Pinned factory codec.rs::normalize_gt: NFD, G0-3 folds, trim/collapse whitespace.
    fold = {'\u02bc': "'", '\u1fbd': "'", '\u1fbf': "'", '\u03f2': '\u03c3', '\u1ffe': '', '\u0384': ''}
    nfd = ' '.join(''.join(fold.get(c, c) for c in ud.normalize('NFD', text)).split())
    atoms = codec.get('atoms', [])
    ids = {a['ch']: a.get('id') for a in atoms}
    if not ids or any(v is None for v in ids.values()) or len(set(ids.values())) != len(ids):
        raise ValueError('pinned codec needs unique explicit atom IDs')
    unknown = sorted(set(nfd) - ids.keys())
    if unknown:
        raise ValueError('text not codec-encodable: ' + ','.join('U+%04X' % ord(c) for c in unknown))
    if not nfd:
        raise ValueError('empty normalized correction')
    return {'gt_nfc': ud.normalize('NFC', nfd), 'gt_nfd': nfd,
            'label_ids': [ids[c] for c in nfd], 'codec_version': codec['version'],
            'normalization': 'factory normalize_gt: NFD + G0-3 + whitespace collapse/trim'}


def update(root, corrections, out, generation):
    root, out = Path(root).resolve(), Path(out).resolve()
    if root == out or root in out.parents or out in root.parents:
        raise ValueError('update overlay must be disjoint from base')
    if not re.fullmatch(r'v0\.\d+', generation):
        raise ValueError('generation must be v0.n')
    from .card import card_generation
    previous = card_generation((root / 'README.md').read_text())
    if int(generation.split('.')[1]) <= int(previous.split('.')[1]):
        raise ValueError(f'generation {generation} must follow the card generation {previous}')
    manifest = json.loads((root / 'manifests/MANIFEST.json').read_text())
    inventory = {f['path']: f for f in manifest['files']}
    request = []
    for row in records(corrections):
        required = {'row_key', 'text', 'producer', 'producer_version', 'reason',
                    'expected_label_version_id', 'expected_text_sha256'}
        if row.get('row_key') is None and (row.get('synthetic_key') is not None or
                                           {'factory_build_id', 'source_shard', 'source_ordinal'} <= row.keys()):
            # No occurrence-keyed synthetic label layer exists yet (HF_DATASETS/p3/GAPS.md).
            raise ValueError('synthetic corrections are not supported in this generation: '
                             'no occurrence-keyed synthetic label layer; see GAPS')
        if not required <= row.keys() or any(row[k] is None for k in required):
            raise ValueError('correction missing required predecessor/text/provenance fields')
        if not isinstance(row['text'], str) or not row['reason']:
            raise ValueError('correction needs text and reason')
        component(row['producer']); component(row['producer_version'])
        request.append({k: row[k] for k in sorted(required)})
    request.sort(key=lambda r: (r['row_key'], r['producer'], r['producer_version']))
    dedup = {}
    for row in request:
        if row['row_key'] in dedup and row != dedup[row['row_key']]:
            raise ValueError('conflicting duplicate correction: ' + row['row_key'])
        dedup[row['row_key']] = row
    request = list(dedup.values())
    if not request:
        raise ValueError('empty correction table')
    request_sha = digest(canonical({'base': sha(root / 'manifests/MANIFEST.json'), 'generation': generation, 'rows': request}))
    receipt_path = out / 'manifests/UPDATE_RECEIPT.json'
    if out.exists():
        if receipt_path.is_file():
            receipt = json.loads(receipt_path.read_text())
            if receipt['request_sha256'] == request_sha:
                for entry in receipt['files']:
                    verify_file({**entry, 'path': str(safe_path(out, entry['path']))})
                if sorted(receipt['commit_paths']) != sorted([e['path'] for e in receipt['files']] + receipt['delete_paths']):
                    raise ValueError('update receipt operation inventory differs')
                return allowed(receipt['commit_paths'])
        raise ValueError('existing update/version cannot be overwritten')
    versions = {(r['producer'], r['producer_version']) for r in request}
    for producer, version in versions:
        if (root / f'labels/versions/{producer}/{version}').exists() or any(p.startswith(f'labels/versions/{producer}/{version}/') for p in inventory):
            raise ValueError('existing producer version cannot be overwritten')
    used = {'manifests/CONFIGS.json', 'manifests/FEATURE_INPUTS.json', 'manifests/COVERAGE.json', 'manifests/UPDATES.jsonl', 'README.md'}
    for config in ('labels_current', 'row_features', 'rows', 'current_features', 'label_versions'):
        for paths in manifest['configs'][config].values():
            used.update(paths)
    for path in used:
        verify_file({**inventory[path], 'path': str(safe_path(root, path))})
    bundle = json.loads((root / 'manifests/FEATURE_INPUTS.json').read_text())
    if bundle['unicode_version'] != ud.unidata_version:
        raise ValueError('Unicode version mismatch')
    # Validate everything before opening an output directory. Indexes stay in disposable scratch.
    with tempfile.TemporaryDirectory(prefix='rel0-update-') as scratch:
        scratch = Path(scratch)
        db = sqlite3.connect(scratch / 'index.sqlite')
        db.execute('CREATE TABLE current(k TEXT PRIMARY KEY,j TEXT)')
        db.execute('CREATE TABLE rows(k TEXT PRIMARY KEY,j TEXT)')
        for row in config_rows(root, 'labels_current'):
            db.execute('INSERT INTO current VALUES(?,?)', (row['row_key'], canonical(row)))
        for row in config_rows(root, 'rows'):
            db.execute('INSERT INTO rows VALUES(?,?)', (row['row_key'], canonical(row)))
        codec = bundle['codec']
        atomic_json(scratch / 'codec.json', codec)
        (scratch / 'Scripts.txt').write_text(''.join('%04X..%04X ; %s\n' % tuple(r) for r in bundle['script_ranges']))
        features = Features(scratch / 'codec.json', scratch / 'Scripts.txt', bundle['unicode_version'])
        # Persist the original pinned feature provenance, not scratch paths.
        original_provenance = None
        for f in config_rows(root, 'row_features'):
            original_provenance = f.get('feature_provenance_json')
            break
        correction_sha = sha(corrections)
        new_labels, new_features = [], []
        for correction in request:
            key = correction['row_key']
            prior = db.execute('SELECT j FROM current WHERE k=?', (key,)).fetchone()
            row = db.execute('SELECT j FROM rows WHERE k=?', (key,)).fetchone()
            if not prior or not row:
                raise ValueError('unknown row_key: ' + key)
            prior, row = json.loads(prior[0]), json.loads(row[0])
            if (prior['label_version_id'] != correction['expected_label_version_id'] or
                    prior['text_sha256'] != correction['expected_text_sha256']):
                raise ValueError('stale predecessor label_version_id/text_sha256: ' + key)
            if prior['text'] == correction['text']:
                raise ValueError('no-op correction does not allocate a generation')
            encoded = encode(correction['text'], codec)
            label = {**prior, **encoded, 'text': correction['text'], 'text_sha256': digest(correction['text']),
                     'producer': correction['producer'], 'producer_version': correction['producer_version'],
                     'label_variant': 'release', 'before_sha256': prior['text_sha256'],
                     'predecessor_label_version_id': prior['label_version_id'], 'route_status': 'applied',
                     'reason': correction['reason'], 'source_sha256': correction_sha,
                     'source_locator': {'correction_table_sha256': correction_sha, 'row_key': key}}
            label['label_version_id'] = digest(canonical([key, 'release', label['producer'], label['producer_version']]))
            new_labels.append(label)
            feature = features.compute(label['text'], row, label['label_version_id'])
            feature.update(label_version_id=label['label_version_id'], label_variant_name='release',
                           feature_provenance_json=original_provenance or canonical(features.provenance))
            new_features.append(feature)
            db.execute('UPDATE current SET j=? WHERE k=?', (canonical(label), key))
        out.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=out.name + '.partial-', dir=out.parent))
        try:
            configs = json.loads((root / 'manifests/CONFIGS.json').read_text())
            changed = []
            def write(name, directory, values, singleton=False):
                writer = Shards(stage, name, directory, manifest['file_cap'], min(TARGET, manifest['file_cap']))
                for value in values:
                    writer.add(value)
                files = writer.close()
                if singleton and len(files) == 1:
                    old = stage / files[0]['path']
                    new = stage / (directory + '.parquet')
                    old.replace(new); old.parent.rmdir()
                    files = [{**info(new, stage), 'rows': files[0]['rows']}]
                changed.extend(f['path'] for f in files)
                return [f['path'] for f in files]
            for producer, version in sorted(versions):
                paths = write('label_versions', f'labels/versions/{producer}/{version}',
                              (r for r in new_labels if (r['producer'], r['producer_version']) == (producer, version)))
                configs['label_versions']['inventory'].extend(paths)
                paths = write('row_features', f'tables/row_features/updates/{producer}/{version}',
                              (f for f, r in zip(new_features, new_labels) if (r['producer'], r['producer_version']) == (producer, version)))
                configs['row_features']['inventory'].extend(paths)
            old_current = [p for paths in configs['labels_current'].values() for p in paths]
            old_features = [p for paths in configs['current_features'].values() for p in paths]
            configs['labels_current'] = {'inventory': write('labels_current', 'labels/current', (json.loads(j) for j, in db.execute('SELECT j FROM current ORDER BY k')), True)}
            new_by_key = {f['row_key']: f for f in new_features}
            def current_features():
                for f in config_rows(root, 'current_features'):
                    if f['row_key'] not in new_by_key:
                        yield f
                yield from sorted(new_features, key=lambda f: f['row_key'])
            configs['current_features'] = {'inventory': write('current_features', 'tables/current_features', current_features(), True)}
            # Overflow transitions need deletes in the same atomic remote commit.
            deleted = sorted((set(old_current + old_features) - set(changed)))
            allowed(deleted)
            atomic_json(stage / 'manifests/CONFIGS.json', configs)
            updates = (root / 'manifests/UPDATES.jsonl').read_text()
            event = {'generation': generation, 'request_sha256': request_sha, 'rows': len(request),
                     'versions': sorted(versions), 'predecessors': request}
            (stage / 'manifests/UPDATES.jsonl').write_text(updates + canonical(event) + '\n')
            coverage = json.loads((root / 'manifests/COVERAGE.json').read_text())
            from .accept_bindings import BindingPolicy
            policy = BindingPolicy(json.loads((root / 'manifests/INPUT_LOCK.json').read_text()), False)
            governed = policy.columns('row_features')
            field_coverage = coverage.get('binding_writes', {}).get('field_coverage', {})
            for field, binding in governed.items():
                count = {'null': 0, 'nonnull': 0}
                for f in config_rows(root, 'row_features'):
                    count['null' if f.get(field) is None else 'nonnull'] += 1
                for f in new_features:
                    count['null' if f.get(field) is None else 'nonnull'] += 1
                field_coverage[binding + ':row_features.' + field] = {k: v for k, v in count.items() if v}
            coverage['current_label_update'] = {'generation': generation, 'rows': len(request), 'request_sha256': request_sha}
            atomic_json(stage / 'manifests/COVERAGE.json', coverage)
            # Keep config YAML aligned on overflow and move every generation reference
            # (title, introduction, loader revisions) to the new generation together.
            from .card import card_generation, front_matter, retarget
            text = (root / 'README.md').read_text()
            previous = card_generation(text)
            text = retarget(front_matter(text, configs), generation)
            (stage / 'README.md').write_text(text.rstrip('\n') + f'\n\nCorrection generation {generation} supersedes '
                f'{previous} for current labels ({len(request)} rows); earlier tags stay immutable.\n')
            for p in stage.rglob('*'):
                if p.is_file():
                    allowed([p.relative_to(stage).as_posix()])
            changes = [info(p, stage) for p in sorted(stage.rglob('*')) if p.is_file()]
            for path in deleted:
                inventory.pop(path, None)
            inventory.update({e['path']: e for e in changes})
            manifest.update(files=sorted(inventory.values(), key=lambda f: f['path']), configs=configs,
                            incumbent_generation=generation, parent_manifest_sha256=sha(root / 'manifests/MANIFEST.json'))
            # Append-only history changes its physical key digests; source rows stay frozen.
            db.execute('CREATE TABLE logical(t TEXT,k TEXT,PRIMARY KEY(t,k))')
            for name, extra, keys in (('label_versions', new_labels, ('label_version_id',)),
                                      ('row_features', new_features, ('row_key', 'label_variant', 'feature_version'))):
                for r in config_rows(root, name):
                    db.execute('INSERT INTO logical VALUES(?,?)', (name, canonical([r[k] for k in keys])))
                for r in extra:
                    db.execute('INSERT INTO logical VALUES(?,?)', (name, canonical([r[k] for k in keys])))
                h = hashlib.sha256()
                count = 0
                for key, in db.execute('SELECT k FROM logical WHERE t=? ORDER BY k', (name,)):
                    h.update((key + '\n').encode()); count += 1
                manifest['logical_key_sha256'][name] = h.hexdigest()
                manifest['counts'][name] = count
            # Source relation counts remain frozen; updated version counts are explicit.
            manifest['label_update_rows'] = len(request)
            atomic_json(stage / 'manifests/MANIFEST.json', manifest)
            sums = manifest['files'] + [info(stage / 'manifests/MANIFEST.json', stage)]
            (stage / 'manifests/SHA256SUMS').write_text(''.join(f"{e['sha256']}  {e['path']}\n" for e in sorted(sums, key=lambda f: f['path'])))
            files = [info(p, stage) for p in sorted(stage.rglob('*')) if p.is_file()]
            paths = allowed(sorted([e['path'] for e in files] + deleted))
            # Receipt is local transport metadata, not a public operation.
            atomic_json(stage / 'manifests/UPDATE_RECEIPT.json', {'request_sha256': request_sha, 'commit_paths': paths,
                'files': files, 'delete_paths': deleted, 'unchanged_immutable_files': [e for e in manifest['files'] if e['path'].startswith(('data/', 'images/'))]})
            stage.replace(out)
            return paths
        except BaseException:
            shutil.rmtree(stage)
            raise
        finally:
            db.close()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('corrections', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--generation', required=True)
    args = p.parse_args(argv)
    offline()
    paths = update(args.root, args.corrections, args.out, args.generation)
    print(canonical({'commit_paths': paths}))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print('update failed: ' + str(exc), file=sys.stderr)
        sys.exit(2)
