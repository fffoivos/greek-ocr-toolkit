"""Independent, read-only census of native harvest merge disagreements.

No Builder or Store is instantiated. Inputs are opened read-only; stdout is the
only output. Use the companion sbatch for the complete production scan.
Counts are distinct row identities, not the number of unequal cells or pairs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import resource
import sys
import time

FIELDS = ('row_key', 'parent_id', 'row_id', 'page_id', 'book_id', 'split', 'crop_sha256')
REAL = ('row', 's1', 'census', 'harvest')
TARGET = 'd142c98408656375014ca4cdc48c5564590c7e3c5763fba6cab29734195f841a'


def projection(original, source, policy):
    """Project exactly the seven Store guards, without copying labels/images."""
    from scripts.release_v0_dataset.common import get, mapped, row_key, sanitize
    selected = set(FIELDS) | {'id', 'wave', 'line_id', 'trainer_line_id', 'edition_id',
                             'decision_book_id', 'canonical_book_id'}
    row = {k: sanitize(v) for k, v in original.items() if k in selected}
    row.update({k: v for k, v in source.get('constants', {}).items() if k in selected})
    for field, selector in source.get('fields', {}).items():
        if field in selected:
            row[field] = sanitize(get(original, selector))
    if source.get('templates'):
        full = mapped(original, source)
        row.update({k: full[k] for k in selected if k in full})
    raw = dict(row)
    for field, binding in policy.columns('rows').items():
        if field in ('page_id', 'book_id', 'canonical_book_id') and policy.status(binding) == 'historical_unknown':
            row[field] = None
    adapter = source['adapter']
    if adapter == 'census':
        for field, selector in (('parent_id', 'binding.parent_id'), ('row_id', 'binding.id'),
                                ('split', 'binding.split'), ('crop_sha256', 'binding.crop_sha256')):
            row.setdefault(field, get(original, selector))
    if adapter == 'harvest':
        row.setdefault('row_id', row.get('id'))
        if 'parent_id' not in row:
            row['parent_id'] = 'harvest:' + row['wave']
        row['trainer_line_id'] = 'harvest:' + row['wave'] + ':' + str(row['row_id'])
    if adapter in REAL:
        expected = row_key(row.get('parent_id'), row.get('row_id'))
        row['declared_row_key'] = row.get('row_key')
        row['row_key'] = expected
    elif not row.get('row_key') and row.get('parent_id') is not None and row.get('row_id') is not None:
        row['row_key'] = row_key(row['parent_id'], row['row_id'])
    return row, raw


def summarize(groups):
    """Keep pair denominators including zero-conflict waves and source pairs."""
    from scripts.release_v0_dataset.common import canonical
    totals = {field: set() for field in FIELDS}
    wave_rows, wave_fields = defaultdict(set), defaultdict(lambda: defaultdict(set))
    native_rows, native_fields = defaultdict(set), defaultdict(lambda: defaultdict(set))
    covered_aliases = set()
    pairs = {}
    examples = defaultdict(list)
    for identity, observations in groups.items():
        for observation in observations:
            wave_rows[observation['wave']].add(identity)
            native_rows[observation['wave'], observation.get('native_source')].add(identity)
        for left, right in itertools.combinations(observations, 2):
            # Normalize ordered pair by the builder's ingest order, then locator.
            left, right = sorted((left, right), key=lambda o: (o['order'], o['ordinal']))
            wave = right['wave'] or left['wave']
            pair = (wave, left['source'], left['adapter'], right['source'], right['adapter'])
            item = pairs.setdefault(pair, {'rows': set(), 'fields': defaultdict(set)})
            item['rows'].add(identity)
            for field in FIELDS:
                a, b = left['values'].get(field), right['values'].get(field)
                if a is not None and b is not None and a != b:
                    totals[field].add(identity)
                    wave_fields[wave][field].add(identity)
                    item['fields'][field].add(identity)
                    native_fields[wave, right.get('native_source')][field].add(identity)
                    if field == 'book_id':
                        native = right.get('native_fields', {})
                        if native.get('decision_book_id') == a and native.get('canonical_book_id') == b:
                            covered_aliases.add(identity)
                    if len(examples[field]) < 5:
                        examples[field].append({'identity': identity, 'left': left, 'right': right})
    all_rows = set().union(*wave_rows.values()) if wave_rows else set()
    other = set().union(*(totals[f] for f in FIELDS if f != 'book_id'))
    return {'rows': len(all_rows), 'conflicts': {f: len(totals[f]) for f in FIELDS},
            'other_conflicting_rows': len(other),
            'conflicting_rows': len(set().union(*totals.values())),
            'explicit_decision_book_id_alias_rows': len(covered_aliases),
            'uncovered_book_id_conflicting_rows': len(totals['book_id'] - covered_aliases),
            'by_wave': {w: {'rows': len(ids), 'conflicts': {f: len(wave_fields[w][f]) for f in FIELDS}}
                        for w, ids in sorted(wave_rows.items())},
            'by_wave_native_source': [dict(wave=w, native_source=s, rows=len(ids),
                conflicts={f: len(native_fields[w, s][f]) for f in FIELDS})
                for (w, s), ids in sorted(native_rows.items(), key=lambda x: repr(x[0]))],
            'by_wave_source_adapter_pair': [dict(wave=p[0], left_source=p[1], left_adapter=p[2],
                right_source=p[3], right_adapter=p[4], rows=len(v['rows']),
                conflicts={f: len(v['fields'][f]) for f in FIELDS}) for p, v in sorted(pairs.items())],
            'examples': dict(examples)}


def audit(lock_path, frozen_manifest, label_variant_lock, code_root, harvest_only=False):
    sys.path.insert(0, str(code_root))
    from scripts.release_v0_dataset.common import canonical, info, sha
    from scripts.release_v0_dataset.accept_bindings import BindingPolicy
    started = time.monotonic()
    lock = json.loads(Path(lock_path).read_text())
    policy = BindingPolicy(lock, None)
    # Bind the exact production auxiliary locks too. Label adapters only change
    # labels and prepared adapters copy existing guarded fields unchanged.
    bound = [info(p) for p in (lock_path, frozen_manifest, label_variant_lock)]
    sources = sorted(lock['inputs'], key=lambda s: (s.get('priority', {'evidence': 0, 'census': 10,
        'row': 20, 's1': 30, 'harvest': 30, 'synthetic': 40, 'prepared': 60}.get(s['adapter'], 50)), s['name']))
    relevant = [(n, s) for n, s in enumerate(sources)
                if s['adapter'] in REAL or s['adapter'] == 'row_patch' or s.get('table') == 'rows']
    if harvest_only:
        relevant = [(n, s) for n, s in relevant if s['adapter'] == 'harvest']
    groups, aliases, key_to_group = defaultdict(list), {}, {}
    files, target = [], []
    invalid = []
    # Harvest observations define the complete population, including decisions
    # absent from metadata. All remaining native row writers are then scanned.
    ordered = sorted(relevant, key=lambda ns: ns[1]['adapter'] != 'harvest')
    for order, source in ordered:
        for entry in source['files']:
            if not entry['path'].endswith(('.jsonl', '.jsonl.gz', '.ndjson')):
                raise ValueError('unimplemented native writer format: ' + entry['path'])
            if Path(entry['path']).stat().st_size != entry['bytes']:
                raise ValueError('input size changed: ' + entry['path'])
            # Compressed SHA binds compressed bytes; text line numbers below
            # are one-based decompressed JSONL positions.
            h, count = hashlib.sha256(), 0
            with open(entry['path'], 'rb') as binary:
                stream = gzip.GzipFile(fileobj=binary) if entry['path'].endswith('.gz') else binary
                if stream is not binary and sha(entry['path']) != entry['sha256']:
                    raise ValueError('compressed input SHA changed: ' + entry['path'])
                for line_no, line in enumerate(stream, 1):
                    if stream is binary:
                        h.update(line)
                    if not line.strip():
                        continue
                    original = json.loads(line)
                    row, raw = projection(original, source, policy)
                    key, alias = row.get('row_key'), row.get('trainer_line_id', row.get('line_id'))
                    group = key_to_group.get(key) or aliases.get(alias)
                    if source['adapter'] == 'harvest':
                        group = group or key
                        if group is None:
                            raise ValueError('harvest row has no tuple')
                        key_to_group[key] = group
                        aliases[alias] = group
                    count += 1
                    if group is not None:
                        observation = dict(source=source['name'], adapter=source['adapter'], order=order,
                            path=entry['path'], sha256=entry['sha256'], ordinal=count - 1,
                            line=line_no, wave=row.get('wave') or groups[group][0]['wave'],
                            native_source=original.get('source'), book_population=source.get('book_population'),
                            values={f: row.get(f) for f in FIELDS}, native_fields=raw)
                        groups[group].append(observation)
                        if row.get('declared_row_key') and row['declared_row_key'] != key:
                            invalid.append(observation)
                        if key == TARGET:
                            target.append({**observation, 'original': original})
                    if count % 100000 == 0:
                        print(f"{source['name']} rows={count} seconds={time.monotonic()-started:.1f}", file=sys.stderr, flush=True)
                if stream is not binary:
                    stream.close()
            actual = entry['sha256'] if entry['path'].endswith('.gz') else h.hexdigest()
            if actual != entry['sha256']:
                raise ValueError('input SHA changed: ' + entry['path'])
            files.append({**entry, 'source': source['name'], 'adapter': source['adapter'],
                          'rows': count, 'verified_sha256': actual})
    result = summarize(groups)
    metadata_groups = {k: obs for k, obs in groups.items() if any(
        o.get('book_population') == 'harvest' for o in obs)}
    return dict(read_only=True, full_population=True, schema='hfd-p2m-merge-audit-v1',
        writer_scope='harvest adapters only' if harvest_only else 'all native row writers',
        audit_script_sha256=sha(__file__) if Path(__file__).is_file() else None,
        code={p.name: sha(p) for p in (Path(code_root) / 'scripts/release_v0_dataset').glob('*.py')},
        locks=bound, files=files, target=target, invalid_declared_row_keys=invalid[:20],
        invalid_declared_row_key_count=len(invalid), **result,
        metadata_population=summarize(metadata_groups),
        excluded_writers={'prepared': 'copies guarded fields from stored row; validation only fills nulls',
                          'label_variant_adapters': 'writes labels and text, not guarded identity fields',
                          'synthetic': 'separate synthetic table, no harvest row writes'},
        crop_hash_basis='recorded native crop SHA; successful payload custody must equal it or fail closed',
        elapsed_seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-lock', type=Path, required=True)
    parser.add_argument('--frozen-manifest', type=Path, required=True)
    parser.add_argument('--label-variant-lock', type=Path, required=True)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--harvest-only', action='store_true', help='full harvest pair scan; other writers excluded explicitly')
    args = parser.parse_args()
    print(json.dumps(audit(args.input_lock, args.frozen_manifest, args.label_variant_lock,
                           args.code_root, args.harvest_only), ensure_ascii=False, indent=2))
