"""Union the S1 real population and a completed harvest, with whole-book custody.

No imports of harvesting/native inference; no row filtering beyond train dedupe.
All eval rows survive. Eval crop bytes exclude matching train rows with witnesses.
Book/edition/provider/line conflicts still refuse; eval repeats are diagnostics.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import re

from common import atomic, bound, digest, read, rows, sha, spec, write_rows


class Registry:
    @staticmethod
    def identity_namespace(namespace):
        return namespace in ('book_id', 'edition_id', 'seal04_edition_hash', 'line_id_prefix', 'v2_book_id', 'pdf_sha256') or namespace.startswith('provider_item:')

    def __init__(self, authority, extension=()):
        self.books = {}
        # Only namespaces consulted by resolve() carry identity. Collection/search
        # URLs and other provenance remain many-to-one metadata, never candidates.
        self.aliases = defaultdict(set)
        self.metadata_aliases = defaultdict(set)
        for row in [*authority, *extension]:
            bid = row['book_id']
            old = self.books.get(bid)
            if old and any(old[k] != row[k] for k in ('split', 'conflict', 'harvest_protection')):
                raise ValueError('registry v2 assignment changed: ' + bid)
            self.books[bid] = row
            self.aliases[('book_id', bid)].add(bid)
            for alias in row.get('aliases', []):
                namespace = alias['namespace']
                target = self.aliases if self.identity_namespace(namespace) else self.metadata_aliases
                target[(namespace, str(alias.get('value', alias.get('id'))))].add(bid)
        if any(len(v) != 1 for v in self.aliases.values()):
            raise ValueError('ambiguous registry identity aliases')

    def alias_report(self):
        return dict(identity_alias_keys=len(self.aliases),
            metadata_alias_keys=len(self.metadata_aliases),
            metadata_keys_by_namespace=dict(Counter(ns for ns, _ in self.metadata_aliases)),
            metadata_policy='retained as metadata only; never used to resolve book identity',
            shared_metadata_aliases=[dict(namespace=ns, value=value, book_ids=sorted(bids))
                for (ns, value), bids in sorted(self.metadata_aliases.items()) if len(bids) > 1])

    def resolve(self, row):
        candidates = set()
        keys = [('book_id', row.get('book_id')), ('book_id', row.get('canonical_book_id')), ('edition_id', row.get('edition_id')),
                ('seal04_edition_hash', row.get('edition_id')),
                ('v2_book_id', row.get('edition_id')), ('pdf_sha256', row.get('edition_id')),
                ('provider_item:' + row['source'], row.get('item')),
                ('line_id_prefix', re.sub(r'(?:--s\d+|--p\d+|--n\d+|-p\d+).*$', '', row['id']))]
        for ns, val in keys:
            if val is not None:
                candidates.update(self.aliases.get((ns, str(val)), ()))
        if len(candidates) != 1:
            raise ValueError('unknown/contradictory book aliases: ' + row['id'])
        bid = candidates.pop()
        book = self.books[bid]
        if book['conflict'] or book['split'].removeprefix('seal04_') != row['split']:
            raise ValueError('registry split/conflict: ' + row['id'])
        # Protection constrains NEW harvest, not the SHA-bound S1 population.
        if row['split'] == 'train' and row['release'] != 'v4' and book['harvest_protection']:
            raise ValueError('protected train book: ' + row['id'])
        return bid


def relocate(path, mappings, expected, *, fixture=False):
    path = Path(path)
    hits = [(Path(old), Path(new)) for old, new in mappings.items()
            if path.is_relative_to(Path(old))]
    if len(hits) > 1:
        # Nested prefixes need an explicit unambiguous mapping, never a basename guess.
        raise ValueError('ambiguous relocation: ' + str(path))
    if hits:
        old, new = hits[0]
        path = new / path.relative_to(old)
    if not fixture and (not path.is_absolute() or not str(path).startswith(('/iopsstor/', '/capstor/'))):
        raise ValueError('non-Clariden crop path: ' + str(path))
    if sha(path) != expected:
        raise ValueError('crop SHA mismatch: ' + str(path))
    return str(path.resolve())


def combine(records, registry, *, issues=None):
    """Keep v4 before harvest; retain held-out multiplicity; audit ALL inputs first."""
    records = list(records)
    eval_crops = {}
    for row in records:
        if row['split'] in ('dev', 'test'):
            eval_crops.setdefault(row['crop_sha256'], row)
    removed, eval_repeats = [], []
    s1_resolution = Counter()
    seen = {'crop': {}, 'line': {}, 'book': {}, 'edition': {}, 'provider': {}}
    kept, duplicate = [], []
    counts_before = Counter()
    def witness(r):
        return {k: r.get(k) for k in ('release', 'split', 'id', 'source', 'item',
            'book_id', 'canonical_book_id', 'edition_id', 'crop_sha256', 'text')}
    def problem(message, kind, row, previous=None, key=None):
        if issues is None:
            raise ValueError(message + ': ' + row['id'])
        issues.append(dict(kind=kind, message=message, key=key, row=witness(row),
                           previous=witness(previous) if previous else None))
    for row in records:
        if row['split'] not in ('train', 'dev', 'test'):
            raise ValueError('unexpected split')
        counts_before[(row['release'], row['split'], row['source'], row.get('primary_class'))] += 1
        try:
            canonical = registry.resolve(row)
            if row['release'] == 'v4':
                s1_resolution['resolved_split_matches_s1'] += 1
        except ValueError as exc:
            if row['release'] == 'v4':
                s1_resolution['unresolved_or_split_mismatch'] += 1
            problem(str(exc), 'registry', row)
            canonical = row.get('canonical_book_id') or row.get('book_id') or 'UNRESOLVED:' + row['edition_id']
        row = dict(row, canonical_book_id=canonical)
        keys = [('crop', row['crop_sha256']), ('line', (row['source'], row['id'])),
                ('book', row['canonical_book_id']), ('edition', row['edition_id'])]
        if row.get('item'):
            keys.append(('provider', (row['source'], str(row['item']))))
        duplicate_of = None
        for kind, key in keys:
            # Eval wins for crop identity only; inspect all book/edition/line
            # assignments even on train rows that will be excluded.
            if kind == 'crop' and row['split'] == 'train' and key in eval_crops:
                continue
            previous = seen[kind].get(key)
            if previous:
                if kind == 'crop' and row['split'] != 'train':
                    eval_repeats.append(dict(kind='eval_crop_repeat', row=witness(row),
                        previous=witness(previous), labels_equal=row['text'] == previous['text']))
                    continue
                if previous['split'] != row['split']:
                    problem('cross-split ' + kind, kind, row, previous, key)
                if kind in ('crop', 'line'):
                    if previous['text'] != row['text'] or previous['crop_sha256'] != row['crop_sha256']:
                        problem('conflicting duplicate ' + kind, kind, row, previous, key)
                    if previous['canonical_book_id'] != row['canonical_book_id']:
                        problem('duplicate crop/line assigned to different books', kind, row, previous, key)
                    duplicate_of = previous
            else:
                seen[kind][key] = row
        if row['split'] == 'train' and row['crop_sha256'] in eval_crops:
            ev = eval_crops[row['crop_sha256']]
            removed.append(dict(reason='train_crop_matches_eval', row=witness(row),
                eval_witness=witness(ev), labels_equal=row['text'] == ev['text']))
        elif duplicate_of and row['split'] == 'train':
            duplicate.append(dict(release=row['release'], id=row['id'],
                                  kept_release=duplicate_of['release'], kept_id=duplicate_of['id']))
        else:
            kept.append(row)
    def table(records):
        result = Counter((r['release'], r['split'], r['source'], r.get('primary_class')) for r in records)
        return [dict(release=k[0], split=k[1], source=k[2], primary_class=k[3], rows=n)
                for k, n in sorted(result.items(), key=lambda x: str(x[0]))]
    return kept, dict(input_rows=sum(counts_before.values()), retained_rows=len(kept),
        unique_crops=len({r['crop_sha256'] for r in kept}), train_unique=sum(r['split'] == 'train' for r in kept),
        eval_retention='all rows, including same-split repeated crops',
        duplicate_train_rows=len(duplicate), duplicates=duplicate,
        train_eval_removed_rows=len(removed), train_eval_removals=removed,
        eval_crop_repeat_rows=len(eval_repeats), eval_crop_repeats=eval_repeats,
        s1_resolution=dict(input_rows=sum(r['release'] == 'v4' for r in records),
            resolved_split_matches_s1=s1_resolution['resolved_split_matches_s1'],
            unresolved_or_split_mismatch=s1_resolution['unresolved_or_split_mismatch']),
        before=[dict(release=k[0], split=k[1], source=k[2], primary_class=k[3], rows=n)
                for k, n in sorted(counts_before.items(), key=lambda x: str(x[0]))], after=table(kept),
        split_counts=dict(Counter(r['split'] for r in kept)),
        leakage=('FAIL' if issues else 'PASS') + ': train crops disjoint from eval after witnessed exclusion; line/book/provider/edition checked on all input rows')


def harvest_rows(root, receipt_spec, *, required_waves):
    root = Path(root)
    transfer = read(root / 'TRANSFER.json')
    receipt = read(bound(receipt_spec))
    if Path(receipt_spec['path']).resolve() != (root / 'RELEASE_RECEIPT.json').resolve():
        raise ValueError('harvest receipt outside selected release')
    if transfer['release_receipt_sha256'] != receipt_spec['sha256']:
        raise ValueError('harvest receipt transfer mismatch')
    if set(receipt['included_waves']) != set(required_waves):
        raise ValueError('harvest missing/extra waves: ' + str(receipt['included_waves']))
    for name in ('metadata.jsonl', 'registry/book_registry.jsonl.gz',
                 'data/train/metadata.jsonl', 'data/dev/metadata.jsonl', 'data/test/metadata.jsonl'):
        if sha(root / name) != transfer['files'][name]['sha256']:
            raise ValueError('harvest transfer SHA: ' + name)
    if (receipt['registry']['exported_admitted_books_sha256'] != sha(root / 'registry/book_registry.jsonl.gz')):
        raise ValueError('harvest registry receipt mismatch')
    data = []
    split_view = {}
    for row in rows(root / 'metadata.jsonl'):
        rel = Path(row['file_name'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('unsafe relative crop')
        if row['crop_sha256'] != transfer['files'][str(rel)]['sha256']:
            raise ValueError('harvest crop transfer mismatch')
        if __import__('hashlib').sha256(row['text'].encode()).hexdigest() != row['label_sha256']:
            raise ValueError('harvest exact label mismatch')
        if not rel.is_relative_to(Path('data') / row['split']):
            raise ValueError('harvest root metadata crop outside assigned split')
        normalized = dict(row, file_name=str(rel.relative_to(Path('data') / row['split'])))
        key = (row['split'], row['id'])
        if key in split_view:
            raise ValueError('duplicate harvest metadata id')
        split_view[key] = digest(normalized)
        # Retain training/audit identity fields, not large catalogue provenance.
        data.append(dict({k: row[k] for k in ('id', 'text', 'source', 'split', 'book_id',
            'canonical_book_id', 'edition_id', 'item', 'primary_class', 'wave', 'crop_sha256') if k in row},
            crop_path=str(root / rel), release='harvest'))
    for split in ('train', 'dev', 'test'):
        for row in rows(root / 'data' / split / 'metadata.jsonl'):
            if row['split'] != split or split_view.pop((split, row['id']), None) != digest(row):
                raise ValueError('split-level metadata differs from root metadata')
    if split_view:
        raise ValueError('incomplete split-level metadata')
    if len(data) != receipt['rows'] or dict(Counter(r['split'] for r in data)) != receipt['by_split']:
        raise ValueError('harvest receipt counts mismatch')
    for field, key in (('wave', 'by_wave'), ('source', 'by_source')):
        if dict(Counter(r[field] for r in data)) != receipt[key]:
            raise ValueError('harvest receipt count mismatch: ' + field)
    return data, list(rows(root / 'registry/book_registry.jsonl.gz'))


def build(config, output, *, fixture=False, audit=False):
    cfg = read(config)
    output = Path(output)
    if output.exists():
        raise ValueError('immutable manifest output exists; choose a new attempt')
    authority = list(rows(bound(cfg['registry_v2'])))
    bound(cfg['harvest_transfer'])
    harvest, extension = harvest_rows(cfg['harvest_root'], cfg['harvest_receipt'],
                                    required_waves=cfg['required_waves'])
    registry = Registry(authority, extension)
    # shared records bind original SCALE1 opaque IDs to edition identity.
    shared = {r.get('id', r.get('line_id')): r for r in rows(bound(cfg['s1_records']))}
    info = read(bound(cfg['s1_build_info']))
    data = []
    for row in rows(bound(cfg['s1_subset'])):
        meta = shared[row['row_id']]
        if row['crop_sha256'] != info['crop_sha256'][row['row_id']]:
            raise ValueError('S1 crop join mismatch')
        data.append(dict(id=row['row_id'], text=row['label'], source=row['source'], split='train',
            edition_id=meta.get('edition_id') or meta.get('doc') or meta.get('source_doc_id'),
            book_id=meta.get('book_id'), item=meta.get('item'), primary_class=row['primary_class'],
            crop_path=row['crop_path'], crop_sha256=row['crop_sha256'], release='v4'))
    if len(data) != cfg['s1_subset']['rows']:
        raise ValueError('S1 subset count mismatch')
    # Literal sealed panels stay separate. They also participate in the leakage audit.
    suite_path = bound(cfg['seal_suite'])
    suite = read(suite_path)
    for name, panel in suite['panels'].items():
        panel_path = suite_path.parent / panel['path']
        if sha(panel_path) != panel['sha256']:
            raise ValueError('seal panel SHA mismatch')
        panel_rows = list(rows(panel_path))
        if len(panel_rows) != panel['rows']:
            raise ValueError('seal panel count mismatch')
        for row in panel_rows:
            data.append(dict(row, id=row['id'], text=row['text'], source=row['source'],
                edition_id=row['doc'], split=name.removeprefix('benchmark_v02_'),
                primary_class=row['class'], crop_path=str(suite_path.parent / row['crop_path']), release='seal04'))
    data.extend(harvest)
    for row in data:
        if not row.get('edition_id'):
            raise ValueError('edition missing: ' + row['id'])
        row['crop_path'] = relocate(row['crop_path'], cfg['relocations'], row['crop_sha256'], fixture=fixture)
    issues = [] if audit else None
    kept, report = combine(data, registry, issues=issues)
    report['registry_aliases'] = registry.alias_report()
    population = [r for r in kept if r['release'] != 'seal04']
    report['dataset_unique_crops'] = len({r['crop_sha256'] for r in population})
    report['dataset_retained_rows'] = len(population)
    report['dataset_by_split'] = dict(Counter(r['split'] for r in population))
    unique_population = list({r['crop_sha256']: r for r in reversed(population)}.values())
    report['dataset_unique_by_split'] = dict(Counter(r['split'] for r in unique_population))
    unique_table = Counter((r['release'], r['split'], r['source'], r.get('primary_class')) for r in unique_population)
    report['unique_population_table'] = [dict(release=k[0], split=k[1], source=k[2], primary_class=k[3], rows=n)
        for k, n in sorted(unique_table.items(), key=lambda x: str(x[0]))]
    report['unique_count_attribution'] = 'first release occurrence per crop SHA; eval multiplicity separately retained'
    report['s1_comparison'] = {}
    for field in ('source', 'primary_class'):
        baseline = Counter(str(r.get(field)) for r in data if r['release'] == 'v4')
        full = Counter(str(r.get(field)) for r in kept if r['split'] == 'train')
        report['s1_comparison'][field] = [dict(value=k, s1_rows=baseline[k], full_unique_train=full[k], delta=full[k]-baseline[k])
            for k in sorted(baseline.keys() | full.keys())]
    report['external_seal04_instruments'] = dict(Counter(r['split'] for r in kept if r['release'] == 'seal04'))
    output.mkdir(parents=True)
    write_rows(output / 'train_eval_removals.jsonl', report.pop('train_eval_removals'))
    write_rows(output / 'eval_crop_repeats.jsonl', report.pop('eval_crop_repeats'))
    report['train_eval_removal_file'] = spec(output / 'train_eval_removals.jsonl')
    report['eval_crop_repeat_file'] = spec(output / 'eval_crop_repeats.jsonl')
    if audit:
        write_rows(output / 'collisions.jsonl', issues)
        write_rows(output / 'duplicates.jsonl', report.pop('duplicates'))
        report.update(schema='TRAIN_FULL-audit-v1', fixture=fixture,
            status='BLOCKED' if issues else 'PASS', config=spec(config),
            package=spec(Path(__file__).with_name('PAYLOAD.json')),
            collisions=len(issues), collision_kinds=dict(Counter(r['kind'] for r in issues)),
            collision_examples=issues[:20],
            count_status='UNQUALIFIED: conflicts present' if issues else 'VERIFIED: all crop bytes SHA checked',
            collision_file=spec(output / 'collisions.jsonl'), duplicate_file=spec(output / 'duplicates.jsonl'))
        from horizon import resolve
        report['horizons'] = [resolve(read(Path(__file__).with_name('recipe.json')), report['train_unique'], choice)
                              for choice in ('full', 's1-literal', 'longer')] if not issues else []
        atomic(output / 'AUDIT.json', report)
        if issues:
            raise ValueError('union audit BLOCKED: see AUDIT.json and collisions.jsonl')
    write_rows(output / 'rows.jsonl', kept)
    write_rows(output / 'train.jsonl', (r for r in kept if r['split'] == 'train'))
    report.update(schema='TRAIN_FULL-manifest-v1', fixture=fixture, config=spec(config),
                  package_sha256=sha(Path(__file__).with_name('PAYLOAD.json')) if Path(__file__).with_name('PAYLOAD.json').exists() else None,
                  inputs={k: cfg[k] for k in ('s1_subset', 's1_records', 's1_build_info', 'registry_v2', 'seal_suite', 'harvest_receipt', 'harvest_transfer')},
                  harvest_transfer=spec(Path(cfg['harvest_root']) / 'TRANSFER.json'),
                  files={name: spec(output / name) for name in ('rows.jsonl', 'train.jsonl', 'train_eval_removals.jsonl', 'eval_crop_repeats.jsonl')},
                  audit=spec(output / 'AUDIT.json') if audit else None)
    atomic(output / 'MANIFEST.json', report)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    print(build(a.config, a.out))
