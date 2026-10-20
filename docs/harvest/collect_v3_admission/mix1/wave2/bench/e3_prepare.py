#!/usr/bin/env python3
"""Offline collection-v2 preparation. No renderer, model, network or GPU calls.

The default run is node-only. --dry-run-human explicitly permits projection,
subsets, hold-out checks and ONLY the human import on macOS.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import json
from pathlib import Path, PurePosixPath
import random
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.common import read_rows, write_rows
from bench.e1_common import ROOT, atomic_json, files_binding, head, read_json, run, sha256
from bench.e1_prepare import factory_build
from bench.o5_prepare import codec_tables, exclusion_text, normalize
from train.mix import shard_inventory, validate

SEED = 20261015
SIZES = (25000, 50000, 100000)
FIXTURE_SIZES = (5, 10, 20)
META_FIELDS = ('wave', 'year', 'book_key', 'page_id', 'confidence', 'label_v1', 'rules_applied')
TRAIN_NAMES = ('full', 'sub_100k', 'sub_050k', 'sub_025k')
SOURCE_FILES = ('import_real_v2_train.jsonl', 'import_real_v2_dev.jsonl',
                'import_real_v2_test.jsonl', 'admitted_all_v2.jsonl')
INSTRUMENTS = ('v2_test', 'wikisource_human')
CYRILLIC_CAUSE = 'codec_v1_lacks_pre_reform_and_serbian_cyrillic'
# 'cyrillic,wikisource' also exempts the Wikisource silver val rows (Russian pages carry yat: 88/1,094 = 8 %).
CODEC_EXEMPT_CHOICES = ('cyrillic', 'cyrillic,wikisource', 'none')


def exempt_names(codec_exempt):
    return set() if codec_exempt == 'none' else set(codec_exempt.split(','))


def policy(human_rows='test', drop_ceiling=.05, codec_exempt='cyrillic'):
    if human_rows != 'test' or not 0 <= drop_ceiling <= 1 or codec_exempt not in CODEC_EXEMPT_CHOICES:
        raise ValueError('invalid E3 policy options')
    return dict(human_rows=human_rows, drop_ceiling=drop_ceiling, codec_exempt=codec_exempt,
                codec_version='v1', decisions_applied=dict(
                    human_view='test-only human labels; line_id + -human; source_doc_id + :human; reserved/gold_aligned',
                    shared_scans='v2_test and wikisource_human intentionally share crops with different label sources',
                    wikisource_val='silver dev rows remain val-only, subject to exposed-text removal and factory drops',
                    exposed_text='remove train/val folded-text matches to all three instruments before subsetting; require zero afterwards',
                    codec='unchanged v1; no label rewrites; unmappable rows accounted by factory drop ledger',
                    instruments='exclude unmappable rows from evaluation; retain full importer feed for drop accounting',
                    cyrillic_exemption=CYRILLIC_CAUSE if 'cyrillic' in exempt_names(codec_exempt) else None,
                    wikisource_exemption=CYRILLIC_CAUSE if 'wikisource' in exempt_names(codec_exempt) else None,
                    validation='all four train mixes use eval-role mixes/val_mix.json, every real_v2 wave val split, concatenate_once'))


def immutable_json(path, value):
    """Never repair a changed existing output by silently overwriting it."""
    path = Path(path)
    if path.exists():
        if read_json(path) != value:
            raise ValueError(f'changed prepared output: {path}; use a fresh --out')
    else:
        atomic_json(path, value)


def immutable_rows(path, rows):
    path = Path(path)
    if path.exists():
        if list(read_rows(path)) != rows:
            raise ValueError(f'changed prepared output: {path}; use a fresh --out')
    else:
        temp = path.with_name(path.name + '.tmp')
        write_rows(temp, rows)
        temp.replace(path)


def bind(out, inputs, *, fixture=False, repo=ROOT, **options):
    """Use E1's byte bindings, including HEAD; reject missing required inputs."""
    inputs = list(map(Path, inputs))
    for path in inputs:
        if not path.is_file():
            raise ValueError(f'missing binding input: {path}')
    binding = dict(inputs=files_binding(inputs), git_head=head(repo), fixture=fixture, **options)
    path = Path(out)/'prepare_binding.json'
    if path.exists() and read_json(path) != binding:
        raise ValueError('preparation inputs changed; use a fresh --out')
    immutable_json(path, binding)
    return binding


def stage(out, name, binding, action):
    """Each stage binds its inputs and reuses only hash-verified outputs."""
    directory = Path(out)/'stages'/name
    immutable_json(directory/'prepare_binding.json', binding)
    receipt = directory/'done.json'
    if receipt.exists():
        info = read_json(receipt)
        for rel, digest in info['artifacts'].items():
            path = Path(out)/rel
            if not path.is_file() or sha256(path) != digest:
                raise ValueError(f'changed prepared output: {path}')
        return info['result']
    result, paths = action()
    artifacts = {str(Path(p).relative_to(out)): sha256(p) for p in paths}
    atomic_json(receipt, dict(result=result, artifacts=artifacts))
    return result


def rewrite_crop(crop, wave):
    parts = PurePosixPath(crop).parts
    prefix = ('docs', 'harvest', 'harvest_big', wave, 'crops')
    if parts[:5] != prefix or len(parts) != 7 or any(p in ('..', '.') for p in parts):
        raise ValueError(f'invalid toolkit crop spelling: {crop}')
    if not parts[-1].endswith('.png'):
        raise ValueError(f'expected PNG crop: {crop}')
    return str(PurePosixPath(wave, *parts[5:]))


def project_row(row, meta, *, human=False):
    text = meta['human_label'] if human else row['label']
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f'empty text: {row["id"]}')
    licence = row['licence']
    if human:
        licence = meta['human_transcription_licence'] + '; scan: ' + licence
    record = dict(crop=rewrite_crop(row['crop'], row['wave']), text=text,
                  source_doc_id=row['doc'] + (':human' if human else ''),
                  line_id=row['id'] + ('-human' if human else ''),
                  split='reserved' if human else row['split'], source_dataset=row['source'],
                  license=licence, label_tier='gold_aligned' if human else row['label_tier'],
                  admitted=row['admitted'], script_class=row['script_class'],
                  source_url=row.get('source_url'), attribution=row.get('attribution'))
    sidecar = dict(line_id=record['line_id'], **{k: meta.get(k, row.get(k)) for k in META_FIELDS})
    return record, sidecar


def projection_plan(v2, *, human_rows='test'):
    policy(human_rows=human_rows)
    metadata = {}
    for row in read_rows(Path(v2)/'admitted_all_v2.jsonl'):
        if row['id'] in metadata:
            raise ValueError(f'duplicate admitted id: {row["id"]}')
        metadata[row['id']] = row
    groups, sidecars, originals = defaultdict(list), defaultdict(list), {}
    for name in ('v2_test', 'wikisource_human'):
        groups[name], sidecars[name] = [], []
    for filename, split in (('train', 'train'), ('dev', 'val'), ('test', 'reserved')):
        for row in read_rows(Path(v2)/f'import_real_v2_{filename}.jsonl'):
            if row['split'] != split:
                raise ValueError(f'wrong split in {filename}: {row["id"]}')
            if row['id'] in originals:
                raise ValueError(f'duplicate source id: {row["id"]}')
            originals[row['id']] = row
            if row['id'] not in metadata:
                raise ValueError(f'no admitted metadata: {row["id"]}')
            name = 'v2_test' if split == 'reserved' else row['wave']
            record, meta = project_row(row, metadata[row['id']])
            groups[name].append(record)
            sidecars[name].append(meta)
    if set(metadata) != set(originals):
        raise ValueError('admitted/import id inventories differ')
    for line_id, meta in metadata.items():
        if meta.get('human_label') is not None and originals[line_id]['split'] == 'reserved':
            record, sidecar = project_row(originals[line_id], meta, human=True)
            groups['wikisource_human'].append(record)
            sidecars['wikisource_human'].append(sidecar)
    # Deterministic byte order, independent of input-file row ordering.
    for mapping in (groups, sidecars):
        for name in mapping:
            mapping[name].sort(key=lambda r: r['line_id'])
    return dict(groups), dict(sidecars)


def projection_conflicts(groups):
    ids, docs = defaultdict(list), defaultdict(lambda: defaultdict(list))
    for name, rows in groups.items():
        for row in rows:
            ids[row['line_id']].append(name)
            docs[row['source_doc_id']][row['split']].append(row['line_id'])
            if not row['text'].strip():
                raise ValueError(f'empty text: {row["line_id"]}')
    return dict(duplicate_ids={k: v for k, v in ids.items() if len(v) > 1},
                document_split_conflicts={k: dict(v) for k, v in docs.items() if len(v) > 1},
                counts={name: dict(Counter(r['split'] for r in rows)) for name, rows in sorted(groups.items())})


def codec_inventory(groups):
    atoms, folds = codec_tables()
    report = {}
    for name, rows in sorted(groups.items()):
        missing, affected = Counter(), []
        for row in rows:
            bad = Counter(ch for ch in normalize(row['text'], folds) if ch not in atoms)
            if bad:
                missing.update(bad)
                affected.append(row['line_id'])
        report[name] = dict(unmappable_rows=len(affected), line_ids=affected,
                            characters=[dict(character=ch, codepoint=f'U+{ord(ch):04X}',
                                             name=unicodedata.name(ch, 'UNNAMED'), occurrences=n)
                                        for ch, n in sorted(missing.items())])
    return report


def remove_exposed(groups, sidecars, e1_real):
    before = disjointness(groups, e1_real, [])
    hits = defaultdict(set)
    for collision in before['collisions']:
        hits[collision['line_id']].add(collision['instrument'])
    exclusions = []
    for name, rows in groups.items():
        if name in INSTRUMENTS:
            continue
        exclusions.extend(dict(id=r['line_id'], line_id=r['line_id'], split=r['split'], wave=name,
                               instruments=sorted(hits[r['line_id']])) for r in rows if r['line_id'] in hits)
        groups[name] = [r for r in rows if r['line_id'] not in hits]
        sidecars[name] = [r for r in sidecars[name] if r['line_id'] not in hits]
    return sorted(exclusions, key=lambda r: r['line_id']), before


def row_counts(rows):
    # Language tags are source-declared Wikisource edition tags, not guesses
    # from script. Other sources have no row-language field in collection v2.
    def language(r):
        source = r.get('source_dataset', '')
        return source.removeprefix('wikisource_') if source.startswith('wikisource_') else 'unknown'
    return dict(n_rows=len(rows), by_class=dict(sorted(Counter(r.get('script_class', 'unknown') for r in rows).items())),
                by_language=dict(sorted(Counter(language(r) for r in rows).items())))


def projection(v2, out, *, e1_real=(), human_rows='test', fail_on_conflict=True):
    groups, sidecars = projection_plan(v2, human_rows=human_rows)
    source_counts = projection_conflicts(groups)['counts']
    exclusions, before = remove_exposed(groups, sidecars, e1_real)
    report = projection_conflicts(groups)
    report.update(source_counts=source_counts, exposed_rows_removed=len(exclusions),
                  overlap_rows_by_instrument_before=before['overlap_rows_by_instrument'],
                  shared_scans=dict(intentional=True, label_sources=['silver', 'human'],
                                    n_crops=len({r['crop'] for r in groups['v2_test']} &
                                                {r['crop'] for r in groups['wikisource_human']})))
    report['codec'] = codec_inventory(groups)
    # Keep the complete witness even when strict source gates refuse publication.
    atomic_json(Path(out)/'projection_report.json', report)
    if fail_on_conflict and (report['duplicate_ids'] or report['document_split_conflicts']):
        raise ValueError('projection id/document split conflicts; see projection_report.json')
    exclusions_path = Path(out)/'exclusions.jsonl'
    immutable_rows(exclusions_path, exclusions)
    instrument_exclusions = []
    report['instruments'] = {}
    for name in INSTRUMENTS:
        bad = set(report['codec'][name]['line_ids'])
        report['instruments'][name] = row_counts([r for r in groups[name] if r['line_id'] not in bad])
        instrument_exclusions.extend(dict(instrument=name, line_id=r['line_id'], id=r['line_id'],
                                          reason='unmapped_codepoint', script_class=r['script_class'])
                                     for r in groups[name] if r['line_id'] in bad)
    instrument_path = Path(out)/'instrument_exclusions.jsonl'
    immutable_rows(instrument_path, instrument_exclusions)
    atomic_json(Path(out)/'projection_report.json', report)
    paths = [Path(out)/'projection_report.json', exclusions_path, instrument_path]
    for name in sorted(groups):
        for suffix, rows in (('.jsonl', groups[name]), ('.meta.jsonl', sidecars[name])):
            path = Path(out)/'records'/(name + suffix)
            immutable_rows(path, rows)
            paths.append(path)
    return report, paths


def largest_remainder(counts, n):
    total = sum(counts.values())
    if not 0 <= n <= total or total == 0:
        raise ValueError(f'subset size {n} outside pool of {total}')
    # Integer remainders avoid platform-dependent float ties.
    quotas = {key: count*n//total for key, count in counts.items()}
    order = sorted(counts, key=lambda key: (-(counts[key]*n % total), key))
    for key in order[:n-sum(quotas.values())]:
        quotas[key] += 1
    return quotas


def nested_subsets(rows, sizes=SIZES, seed=SEED):
    strata = defaultdict(list)
    for row in rows:
        if row['split'] != 'train':
            raise ValueError('scaling pool must contain train rows only')
        wave = PurePosixPath(row['crop']).parts[0]
        strata[(wave, row['script_class'])].append(row)
    counts = {key: len(pool) for key, pool in strata.items()}
    quotas = {n: largest_remainder(counts, n) for n in sizes}
    # Hamilton rounding can exhibit the Alabama paradox: fail rather than quietly
    # violate either exact proportional allocation or nested membership.
    ordered_sizes = sorted(sizes)
    if any(quotas[a][key] > quotas[b][key] for a, b in zip(ordered_sizes, ordered_sizes[1:]) for key in counts):
        raise ValueError('largest-remainder quotas are not nested for these sizes/strata')
    for key, pool in sorted(strata.items()):
        pool.sort(key=lambda r: r['line_id'])
        random.Random(f'{seed}:{key[0]}:{key[1]}').shuffle(pool)
    subsets = {n: sorted([r for key, pool in sorted(strata.items()) for r in pool[:quotas[n][key]]],
                         key=lambda r: r['line_id']) for n in sizes}
    report = dict(seed=seed, full_train_rows=len(rows),
                  strata=[dict(wave=k[0], script_class=k[1], full=counts[k],
                               subsets={str(n): quotas[n][k] for n in sizes}) for k in sorted(counts)])
    return subsets, report


def subset_name(index):
    return ('sub_025k', 'sub_050k', 'sub_100k')[index]


def scaling(out, wave_names, *, fixture=False):
    rows = [r for name in wave_names for r in read_rows(Path(out)/'records'/f'{name}.jsonl') if r['split'] == 'train']
    meta = {r['line_id']: r for name in wave_names for r in read_rows(Path(out)/'records'/f'{name}.meta.jsonl')}
    subsets, report = nested_subsets(rows, FIXTURE_SIZES if fixture else SIZES)
    paths = []
    for i, (n, selected) in enumerate(subsets.items()):
        path = Path(out)/'records'/f'{subset_name(i)}.jsonl'
        immutable_rows(path, selected)
        paths.append(path)
        sidecar = path.with_suffix('.meta.jsonl')
        immutable_rows(sidecar, [meta[r['line_id']] for r in selected])
        paths.append(sidecar)
    immutable_json(Path(out)/'subsets.json', report)
    return report, paths + [Path(out)/'subsets.json']


def text_key(text, folds):
    return exclusion_text(normalize(text, folds))


def e1_texts(e1, component):
    import pyarrow.parquet as pq
    paths = sorted((Path(e1)/component/'reserved').glob('shard-*.parquet'))
    if not paths:
        raise ValueError(f'missing E1 {component} reserved shards')
    return [r['gt_nfc'] for p in paths for r in pq.read_table(p, columns=['gt_nfc']).to_pylist()]


def disjointness(groups, e1_real, synthetic_heldout):
    _, folds = codec_tables()
    held = {name: {text_key(r['text'], folds) for r in groups.get(name, [])}
            for name in ('v2_test', 'wikisource_human')}
    held['e1_real_test'] = {text_key(t, folds) for t in e1_real}
    synth = {text_key(t, folds) for t in synthetic_heldout}
    collisions = []
    synthetic_rows, synthetic_texts = 0, set()
    for name, rows in sorted(groups.items()):
        if name in ('v2_test', 'wikisource_human'):
            continue
        for r in rows:
            key = text_key(r['text'], folds)
            for instrument, texts in held.items():
                if key in texts:
                    collisions.append(dict(line_id=r['line_id'], split=r['split'],
                                           instrument=instrument, normalized_text=key))
            if r['split'] == 'train' and key in synth:
                synthetic_rows += 1
                synthetic_texts.add(key)
    return dict(ok=not collisions, collisions=collisions,
                overlap_rows_by_instrument=dict(Counter(r['instrument'] for r in collisions)),
                synthetic_heldout_train_overlap_rows=synthetic_rows,
                synthetic_heldout_train_overlap_texts=len(synthetic_texts))


def check_disjointness(out, wave_names, e1, *, fail_on_conflict=True):
    groups = {name: list(read_rows(Path(out)/'records'/f'{name}.jsonl'))
              for name in [*wave_names, 'v2_test', 'wikisource_human']}
    report = disjointness(groups, e1_texts(e1, 'real'), e1_texts(e1, 'synthetic_heldout'))
    path = Path(out)/'disjointness.json'
    atomic_json(path, report)
    if fail_on_conflict and not report['ok']:
        raise ValueError('TRAIN/VAL text overlaps an eval instrument; see disjointness.json')
    return report, [path]


def parliament_parts(rows, n):
    if not 1 <= n <= 26:
        raise ValueError('--parliament-parts must be in 1..26')
    books = defaultdict(list)
    for r in rows:
        books[r['source_doc_id']].append(r)
    if len(books) < n:
        raise ValueError('fewer parliament books than requested parts')
    if n == 2:
        # Exact closest-to-half whole-book partition. Bitset subset sum is tiny
        # for this 69k-row wave and avoids an unnecessarily uneven greedy split.
        ordered = sorted(books.items())
        target = len(rows)//2
        mask, reachable, history = (1 << (target+1))-1, 1, []
        for _, pool in ordered:
            history.append(reachable)
            reachable |= (reachable << len(pool)) & mask
        remaining = reachable.bit_length()-1
        selected = set()
        for i in reversed(range(len(ordered))):
            book, pool = ordered[i]
            if remaining >= len(pool) and (history[i] >> (remaining-len(pool))) & 1:
                selected.add(book)
                remaining -= len(pool)
        parts = [[r for book, pool in ordered if (book in selected) == chosen for r in pool]
                 for chosen in (True, False)]
        return [sorted(pool, key=lambda r: r['line_id']) for pool in parts]
    parts = [[] for _ in range(n)]
    # Largest book first, then place in the smallest bin. Never split a book.
    for book, pool in sorted(books.items(), key=lambda item: (-len(item[1]), item[0])):
        index = min(range(n), key=lambda i: (len(parts[i]), i))
        parts[index].extend(pool)
    return [sorted(pool, key=lambda r: r['line_id']) for pool in parts]


def physical_crop(crops, spelling, layout):
    parts = PurePosixPath(spelling).parts
    if len(parts) != 3 or any(p in ('.', '..') for p in parts) or PurePosixPath(spelling).is_absolute():
        raise ValueError(f'invalid node crop spelling: {spelling}')
    relative = Path(parts[0], 'crops', *parts[1:]) if layout == 'toolkit' else Path(*parts)
    path = (Path(crops)/relative).resolve()
    if not path.is_relative_to(Path(crops).resolve()):
        raise ValueError(f'crop outside --crops: {spelling}')
    return path, relative.as_posix()


def drop_summary(info, records, *, name='', drop_ceiling=.05, codec_exempt='cyrillic'):
    ids = [r['line_id'] for r in records]
    ledger = info['drop_ledger']
    dropped = [r['line_id'] for r in ledger]
    if (info['n_records'] != len(records) or info['n_written'] + len(ledger) != len(records)
            or len(set(dropped)) != len(dropped) or not set(dropped) <= set(ids)):
        raise ValueError('inconsistent factory drop ledger/counts')
    excluded_codec = (name in INSTRUMENTS or name in exempt_names(codec_exempt))
    codec_drops = sum(r['reason'] == 'unmapped_codepoint' for r in ledger)
    budget_drops = len(ledger) - (codec_drops if excluded_codec else 0)
    budget_records = len(records) - (codec_drops if excluded_codec else 0)
    return dict(n_records=info['n_records'], n_written=info['n_written'], n_dropped=len(ledger),
                drop_fraction=len(ledger)/len(records) if records else 0,
                drop_ledger=dict(sorted(Counter(r['reason'].split(':', 1)[0] for r in ledger).items())),
                dropped_ids=dropped, drop_ceiling=drop_ceiling,
                codec_exemption=CYRILLIC_CAUSE if name not in INSTRUMENTS and excluded_codec else None,
                instrument_codec_exclusions=codec_drops if name in INSTRUMENTS else 0,
                budget_drops=budget_drops, budget_records=budget_records,
                within_threshold=Decimal(budget_drops) <= Decimal(str(drop_ceiling))*budget_records,
                audit_ok=info.get('audit_ok'), audit_policy='real appearance/length audit is report-only')


def enforce_drops(summary):
    if not summary['within_threshold']:
        raise ValueError(f'import drops exceed {summary["drop_ceiling"]:.0%}: '
                         f'{summary["budget_drops"]}/{summary["budget_records"]}')


def alias_test(directory):
    alias = Path(directory)/'test'
    if alias.is_symlink():
        if alias.readlink() != Path('reserved'):
            raise ValueError(f'changed test alias: {alias}')
    elif alias.exists():
        raise ValueError(f'test must be an alias to reserved: {alias}')
    else:
        alias.symlink_to('reserved', target_is_directory=True)


def import_one(out, name, destination, partition, crops, layout, factory, binding):
    records_path = Path(out)/'records'/f'{name}.jsonl'
    records = list(read_rows(records_path))
    physical = [physical_crop(crops, r['crop'], layout) for r in records]
    import_binding = dict(binding, inputs=files_binding([records_path, factory, *[p for p, _ in physical if p.is_file()]]),
                          missing_crops=[str(p) for p, _ in physical if not p.is_file()], partition_id=partition)
    def action():
        feed = records_path
        if layout == 'toolkit':
            feed = Path(out)/'import_records'/f'{name}.jsonl'
            immutable_rows(feed, [dict(r, crop=relative) for r, (_, relative) in zip(records, physical)])
        dest = Path(out)/destination
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            factory_build(factory, ['import-real', '--records', feed, '--crops', crops, '--partition', partition], dest)
        info = read_json(dest/'build_info.json')
        if (info.get('kind') != 'real' or info['partition_id'] != partition
                or info['records_sha256'] != sha256(feed) or info['shard_sha256'] != shard_inventory(dest)):
            raise ValueError(f'changed factory import: {dest}')
        # factory_build's audit gate is for synthetic builds. A real receipt's
        # audit_ok=false reports length/appearance warnings; drops govern E3.
        summary = drop_summary(info, records, name=name, drop_ceiling=binding.get('drop_ceiling', .05),
                               codec_exempt=binding.get('codec_exempt', 'cyrillic'))
        if name in INSTRUMENTS:
            expected = set(codec_inventory({name: records})[name]['line_ids'])
            actual = {r['line_id'] for r in info['drop_ledger'] if r['reason'] == 'unmapped_codepoint'}
            if actual != expected:
                raise ValueError('factory codec exclusions differ from instrument preflight')
            summary['remaining_rows'] = row_counts([r for r in records if r['line_id'] not in summary['dropped_ids']])
        atomic_json(dest/'import_summary.json', summary)
        summaries_path = Path(out)/'import_summary.json'
        summaries = read_json(summaries_path) if summaries_path.exists() else {}
        summaries[name] = summary
        atomic_json(summaries_path, summaries)
        enforce_drops(summary)
        alias_test(dest)
        paths = [p for p in dest.rglob('*') if p.is_file()]
        if feed != records_path:
            paths.append(feed)
        return summary, paths
    result = stage(out, 'import_' + name, import_binding, action)
    alias_test(Path(out)/destination)
    # The aggregate is derived from individually verified immutable summaries.
    aggregate = read_json(Path(out)/'import_summary.json') if (Path(out)/'import_summary.json').exists() else {}
    aggregate[name] = result
    atomic_json(Path(out)/'import_summary.json', aggregate)
    return result


def real_weights(counts, cap=.25):
    counts = {k: v for k, v in counts.items() if v > 0}
    total = sum(counts.values())
    if total == 0:
        raise ValueError('empty real train pool')
    weights = {k: n/total for k, n in counts.items()}
    if weights.get('parliament', 0) > cap:
        others = total-counts['parliament']
        if others == 0:
            raise ValueError('cannot cap parliament without other waves')
        weights = {k: cap if k == 'parliament' else (1-cap)*n/others for k, n in counts.items()}
    return weights


def real_component(directory, fraction):
    directory = Path(directory).resolve()
    return dict(kind='real', shard_dir=str(directory), fraction=fraction,
                partition_id=read_json(directory/'build_info.json')['partition_id'], source='collection-v2')


def split_count(directory, split):
    import pyarrow.parquet as pq
    return sum(pq.ParquetFile(p).metadata.num_rows
               for p in (Path(directory)/split).glob('shard-*.parquet'))


def manifest(path, components, role, notes):
    spec = path.with_suffix('.components.json')
    immutable_json(spec, components)
    run([sys.executable, '-m', 'train.mix', 'build', '--components', spec, '--out', path,
         '--seed', SEED, '--codec-version', 'v1', '--created-by', 'e3_prepare',
         '--role', role, '--notes', notes])


def verify_instrument(out, name):
    """Hash-validate a real eval manifest and reconcile its actual row identities."""
    import pyarrow.parquet as pq
    out = Path(out)
    mix = validate(out/'mixes'/f'{name}_mix.json', role='eval')
    components = mix['components']
    if (len(components) != 1 or components[0]['kind'] != 'real' or components[0]['fraction'] != 1
            or Path(components[0]['shard_dir']).resolve() != (out/name).resolve()):
        raise ValueError('invalid human eval component')
    actual = []
    for p in sorted((out/name/'reserved').glob('shard-*.parquet')):
        actual.extend(pq.read_table(p, columns=['line_id', 'split', 'codec_version']).to_pylist())
    records = list(read_rows(out/'records'/f'{name}.jsonl'))
    summary = read_json(out/name/'import_summary.json')
    expected = {r['line_id'] for r in records} - set(summary['dropped_ids'])
    ids = [r['line_id'] for r in actual]
    if (not ids or len(ids) != len(set(ids)) or set(ids) != expected
            or any(r['split'] != 'reserved' or r['codec_version'] != 'v1' for r in actual)):
        raise ValueError('instrument written identities/split/codec mismatch')
    return dict(n_mixes=1, reserved_rows={f'{name}_mix': len(ids)},
                remaining_rows=row_counts([r for r in records if r['line_id'] in expected]),
                language_policy='Wikisource source edition suffix; unknown for sources without a language tag')


def build_human_mix(out):
    out = Path(out)
    directory = out/'mixes'
    directory.mkdir(parents=True, exist_ok=True)
    manifest(directory/'wikisource_human_mix.json', [real_component(out/'wikisource_human', 1)],
             'eval', 'E3 human eval-only instrument; split=reserved; codec-unmappable rows excluded')
    report = verify_instrument(out, 'wikisource_human')
    immutable_json(directory/'verification.json', report)
    return report, list(directory.glob('*.json'))


def codec_preflight(out, plan, *, drop_ceiling=.05, codec_exempt='cyrillic', enforce_names=None):
    groups = {name: list(read_rows(Path(out)/'records'/f'{name}.jsonl')) for name, _, _ in plan}
    inventory = codec_inventory(groups)
    report = {}
    for name, destination, _ in plan:
        rows, gap = groups[name], inventory[name]
        codec_ids = set(gap['line_ids'])
        prediction = drop_summary(dict(n_records=len(rows), n_written=len(rows)-len(codec_ids),
                                       drop_ledger=[dict(line_id=i, reason='unmapped_codepoint') for i in sorted(codec_ids)]),
                                  rows, name=name, drop_ceiling=drop_ceiling, codec_exempt=codec_exempt)
        report[destination] = dict(gap, counts=dict(Counter(r['split'] for r in rows)),
                                   n_records=len(rows), predicted_drop_fraction=prediction['drop_fraction'],
                                   codec_exemption=prediction['codec_exemption'],
                                   within_threshold=prediction['within_threshold'],
                                   remaining_rows=row_counts([r for r in rows if r['line_id'] not in codec_ids]))
    path = Path(out)/'codec_gap.json'
    immutable_json(path, report)
    failures = [destination for name, destination, _ in plan if not report[destination]['within_threshold']
                and (enforce_names is None or name in enforce_names)]
    if failures:
        raise ValueError(f'predicted codec drops exceed {drop_ceiling:.0%}: {failures}; see codec_gap.json')
    return dict(imports=list(report), gates_pass=all(r['within_threshold'] for r in report.values()),
                enforced_imports=[destination for name, destination, _ in plan
                                  if enforce_names is None or name in enforce_names]), [path]


def build_mixes(out, e1, wave_names, import_names):
    out, e1 = Path(out), Path(e1)
    directory = out/'mixes'
    directory.mkdir(parents=True, exist_ok=True)
    raw_counts = {wave: sum(r['split'] == 'train' for r in read_rows(out/'records'/f'{wave}.jsonl')) for wave in wave_names}
    parts_by_wave = {wave: [n for n in import_names if n == wave or
                           (wave == 'parliament' and n.startswith('parliament_'))] for wave in wave_names}
    part_counts = {name: split_count(out/'real_v2'/name, 'train') for name in import_names}
    counts = {wave: sum(part_counts[n] for n in parts_by_wave[wave]) for wave in wave_names}
    weights = real_weights(counts)
    component_weights = {}
    full = []
    for wave, weight in sorted(weights.items()):
        sizes = {n: part_counts[n] for n in parts_by_wave[wave]}
        for name, size in sizes.items():
            if size:
                fraction = .5*weight*size/sum(sizes.values())
                full.append(real_component(out/'real_v2'/name, fraction))
                component_weights[name] = fraction
    synthetic = dict(kind='synthetic', build_dir=str(e1/'synthetic'), fraction=.5)
    for name in TRAIN_NAMES:
        components = full + [synthetic] if name == 'full' else [real_component(out/'real_v2'/name, .5), synthetic]
        manifest(directory/f'{name}.json', components, 'train', 'E3 50% real / 50% E1 synthetic; shared validation: val_mix.json, split=val')
    for name, source, kind in (('v2_test_mix', out/'real_v2_test', 'real'),
                               ('wikisource_human_mix', out/'wikisource_human', 'real'),
                               ('e1_real_test_mix', e1/'real', 'real'),
                               ('synthetic_heldout_mix', e1/'synthetic_heldout', 'synthetic')):
        component = real_component(source, 1) if kind == 'real' else dict(kind='synthetic', build_dir=str(source), fraction=1)
        manifest(directory/f'{name}.json', [component], 'eval', 'E3 eval-only instrument; split=reserved')
    val_counts = {name: split_count(out/'real_v2'/name, 'val') for name in import_names}
    val_components = [real_component(out/'real_v2'/name, n/sum(val_counts.values())) for name, n in sorted(val_counts.items()) if n]
    manifest(directory/'val_mix.json', val_components, 'eval', 'Shared E3 validation, load split=val and concatenate once; never sample using train fractions')
    immutable_json(directory/'weights.json', dict(raw_train_counts=raw_counts, written_train_counts=counts,
                   part_train_counts=part_counts, parliament_cap_of_real=.25,
                   within_real=weights, full_component_fractions=component_weights,
                   synthetic_fraction=.5, val_counts=val_counts))
    val_binding = dict(manifest='val_mix.json', split='val', assembly='concatenate_once',
                       manifest_sha256=sha256(directory/'val_mix.json'))
    immutable_json(directory/'validation.json', {name: dict(val_binding, train_manifest_sha256=sha256(directory/f'{name}.json')) for name in TRAIN_NAMES})
    report = verify_mixes(out)
    immutable_json(directory/'verification.json', report)
    return report, list(directory.glob('*.json'))


def verify_mixes(out):
    """Resolve every component and bind all four arms to identical val identities."""
    import pyarrow.parquet as pq
    directory = Path(out)/'mixes'
    names = [*TRAIN_NAMES, 'v2_test_mix', 'wikisource_human_mix', 'e1_real_test_mix', 'synthetic_heldout_mix', 'val_mix']
    resolved = {name: validate(directory/f'{name}.json', role='train' if name in TRAIN_NAMES else 'eval') for name in names}
    eval_counts = {}
    for name in ('v2_test_mix', 'wikisource_human_mix', 'e1_real_test_mix', 'synthetic_heldout_mix'):
        components = resolved[name]['components']
        if len(components) != 1 or components[0]['fraction'] != 1:
            raise ValueError(f'{name}: eval instrument must have one component at fraction 1')
        c = components[0]
        root = Path(c['build_dir'] if c['kind'] == 'synthetic' else c['shard_dir'])
        count = 0
        for p in sorted((root/'reserved').glob('shard-*.parquet')):
            chunk = pq.read_table(p, columns=['split', 'codec_version']).to_pylist()
            if any(r['split'] != 'reserved' or r['codec_version'] != 'v1' for r in chunk):
                raise ValueError(f'{name}: wrong reserved split/codec')
            count += len(chunk)
        if not count:
            raise ValueError(f'{name}: no reserved rows')
        eval_counts[name] = count
    validation = read_json(directory/'validation.json')
    rows = []
    val_directories = []
    for c in resolved['val_mix']['components']:
        root = Path(c['shard_dir'])
        val_directories.append(str(root))
        for p in sorted((root/'val').glob('shard-*.parquet')):
            rows.extend(pq.read_table(p, columns=['line_id', 'split', 'codec_version']).to_pylist())
    ids = [r['line_id'] for r in rows]
    if not rows or len(set(ids)) != len(ids) or any(r['split'] != 'val' or r['codec_version'] != 'v1' for r in rows):
        raise ValueError('invalid shared validation identities/split/codec')
    expected_roots = {str(p.parent.resolve()) for p in (Path(out)/'real_v2').glob('*/val') if list(p.glob('shard-*.parquet'))}
    if set(val_directories) != expected_roots:
        raise ValueError('shared validation omits a wave or includes a foreign component')
    for name in TRAIN_NAMES:
        c = validation[name]
        if (c['manifest'] != 'val_mix.json' or c['split'] != 'val' or c['assembly'] != 'concatenate_once'
                or c['manifest_sha256'] != sha256(directory/'val_mix.json')
                or c['train_manifest_sha256'] != sha256(directory/f'{name}.json')):
            raise ValueError(f'{name}: shared validation binding mismatch')
        components = resolved[name]['components']
        if abs(sum(x['fraction'] for x in components if x['kind'] == 'real')-.5) > 1e-9:
            raise ValueError(f'{name}: expected 50% real')
        if abs(sum(x['fraction'] for x in components if x['kind'] == 'synthetic')-.5) > 1e-9:
            raise ValueError(f'{name}: expected 50% synthetic')
    return dict(n_mixes=len(names), shared_val_rows=len(rows), shared_val_line_ids=sorted(ids),
                reserved_rows=eval_counts,
                validation_split='val', validation_manifest='val_mix.json',
                note='E3b must consume validation.json; train.train default component-local val is unsuitable for these subset mixes')


def prepare(out, v2, crops, e1, factory, *, fixture=False, crops_layout='node',
            parliament_parts_count=1, prepare_only=False, dry_run_human=False,
            human_rows='test', drop_ceiling=.05, codec_exempt='cyrillic'):
    out, v2, crops, e1, factory = [Path(p).resolve() for p in (out, v2, crops, e1, factory)]
    if sys.platform == 'darwin' and not (fixture or prepare_only or dry_run_human):
        raise ValueError('full imports are node-only; use --prepare-only or --dry-run-human on this Mac')
    if not 1 <= parliament_parts_count <= 26:
        raise ValueError('--parliament-parts must be in 1..26')
    applied_policy = policy(human_rows, drop_ceiling, codec_exempt)
    e1_files = [e1/'build_info.json']
    for component in ('real', 'synthetic', 'synthetic_heldout'):
        e1_files.extend([e1/component/'build_info.json', *sorted((e1/component).rglob('shard-*.parquet'))])
    code = [ROOT/'bench/e3_prepare.py', ROOT/'bench/e1_prepare.py', ROOT/'bench/e1_common.py',
            ROOT/'bench/o5_prepare.py', ROOT/'bench/codec_coverage.py', ROOT/'bench/common.py',
            ROOT/'train/mix.py', ROOT/'codec/v1.json', ROOT/'factory/appearance_band.json',
            ROOT/'factory/Cargo.toml', ROOT/'factory/Cargo.lock', *sorted((ROOT/'factory/src').glob('*.rs'))]
    binding = bind(out, [*[v2/name for name in SOURCE_FILES], *e1_files, *code, factory], fixture=fixture,
                   crops=str(crops), crops_layout=crops_layout, e1=str(e1), parliament_parts=parliament_parts_count,
                   subset_sizes=list(FIXTURE_SIZES if fixture else SIZES), seed=SEED,
                   human_rows=human_rows, drop_ceiling=drop_ceiling, codec_exempt=codec_exempt)
    immutable_json(out/'policy.json', applied_policy)
    # Gather every cheap diagnostic before rejecting the run. Written records
    # are candidates only; both global gates MUST pass before the first import.
    projected = stage(out, 'projection', binding, lambda: projection(
        v2, out, e1_real=e1_texts(e1, 'real'), human_rows=human_rows, fail_on_conflict=False))
    if fixture and sum(sum(counts.values()) for name, counts in projected['counts'].items()
                       if name != 'wikisource_human') > 40:
        raise ValueError('--fixture is limited to 40 primary rows; refusing production-sized fixture imports')
    wave_names = sorted(set(projected['counts'])-{'v2_test', 'wikisource_human'})
    stage(out, 'subsets', binding, lambda: scaling(out, wave_names, fixture=fixture))
    checked = stage(out, 'disjointness', binding, lambda: check_disjointness(out, wave_names, e1, fail_on_conflict=False))
    errors = []
    if projected['duplicate_ids'] or projected['document_split_conflicts']:
        errors.append('projection id/document split conflicts; see projection_report.json')
    if not checked['ok']:
        errors.append('TRAIN/VAL text overlaps an eval instrument; see disjointness.json')
    if errors:
        raise ValueError('; '.join(errors))
    import_names = list(wave_names)
    if parliament_parts_count > 1:
        rows = list(read_rows(out/'records/parliament.jsonl'))
        meta = {r['line_id']: r for r in read_rows(out/'records/parliament.meta.jsonl')}
        import_names.remove('parliament')
        for i, pool in enumerate(parliament_parts(rows, parliament_parts_count)):
            name = 'parliament_' + chr(ord('a')+i)
            immutable_rows(out/'records'/f'{name}.jsonl', pool)
            immutable_rows(out/'records'/f'{name}.meta.jsonl', [meta[r['line_id']] for r in pool])
            import_names.append(name)
    plan = [(name, f'real_v2/{name}', f'collection-v2-{name}') for name in import_names]
    plan += [(subset_name(i), f'real_v2/{subset_name(i)}', f'collection-v2-sub{n:03d}k') for i, n in enumerate((25, 50, 100))]
    plan += [('v2_test', 'real_v2_test', 'collection-v2-test'),
             ('wikisource_human', 'wikisource_human', 'collection-v2-wikisource-human')]
    enforced = ['wikisource_human'] if dry_run_human else None
    stage(out, 'codec_policy', dict(binding, enforced_imports=enforced), lambda: codec_preflight(
        out, plan, drop_ceiling=drop_ceiling, codec_exempt=codec_exempt, enforce_names=enforced))
    if prepare_only:
        return dict(projection=projected, imported=[], n_mixes=0)
    if dry_run_human:
        plan = plan[-1:]
    for name, destination, partition in plan:
        import_one(out, name, destination, partition, crops, crops_layout, factory, binding)
    if not dry_run_human:
        mixes = stage(out, 'mixes', binding, lambda: build_mixes(out, e1, wave_names, import_names))
        verify_mixes(out)
    else:
        mixes = stage(out, 'human_mix', binding, lambda: build_human_mix(out))
        verify_instrument(out, 'wikisource_human')
    return dict(projection=projected, imported=[p[0] for p in plan], **mixes)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ('v2', 'crops', 'e1', 'factory', 'out'):
        ap.add_argument('--' + flag, type=Path, required=True)
    ap.add_argument('--fixture', action='store_true', help='5/10/20 scaling sizes; never production counts')
    ap.add_argument('--crops-layout', choices=('toolkit', 'node'), default='node')
    ap.add_argument('--parliament-parts', type=int, default=1)
    ap.add_argument('--human-rows', choices=('test',), default='test')
    ap.add_argument('--drop-ceiling', type=float, default=.05)
    ap.add_argument('--codec-exempt', choices=CODEC_EXEMPT_CHOICES, default='cyrillic')
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument('--prepare-only', action='store_true')
    scope.add_argument('--dry-run-human', action='store_true', help='a,b,e plus ONLY the human import and eval mix; allowed on macOS')
    a = ap.parse_args(argv)
    try:
        result = prepare(a.out, a.v2, a.crops, a.e1, a.factory, fixture=a.fixture,
                         crops_layout=a.crops_layout, parliament_parts_count=a.parliament_parts,
                         prepare_only=a.prepare_only, dry_run_human=a.dry_run_human,
                         human_rows=a.human_rows, drop_ceiling=a.drop_ceiling, codec_exempt=a.codec_exempt)
        summary = {k: result[k] for k in ('imported', 'n_mixes', 'shared_val_rows', 'reserved_rows') if k in result}
        summary['records'] = result['projection']['counts']
        print(json.dumps(summary, ensure_ascii=False))
    except Exception as error:
        atomic_json(a.out/'prepare_failure.json', dict(error=str(error), promoted=False))
        raise


if __name__ == '__main__':
    main()
