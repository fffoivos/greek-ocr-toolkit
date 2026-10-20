"""Strict Q3b gate: exact fields outside the enumerated metadata allowlist.

Run the 16 API option combinations on each of the 95 pages in the legacy frame.
Within one page, memoize deterministic stages by their complete pickled inputs,
returning independent copies. No prior run or frozen output supplies a stage result.
This avoids redetecting the identical raster for each joining/statistics switch.
Q2 is loaded independently from its committed source and executed afresh.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import functools
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import pickle
import re
import subprocess
import sys
import tarfile
import time
import warnings
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from PIL import Image
from scripts.pages.check_q3_equality import REFERENCE, digest

# Paths are rooted in the named file family. [] means an array index, never an
# arbitrary descendant. No geometry, accepted ID/link, reason, count or evidence
# predicate is exempt. The exact same table is documented in PAGES_OUTPUT_FORMAT.
ALLOWLIST = {
    'stats': {
        '$.implementation_sha256': 'The implementation identity changes with the source revision.',
        '$.lines_file_sha256': 'The serialized input file hash changes with JSON formatting.',
        '$.source_image': 'The input path belongs to the run, not the measured page.',
        '$.source_sha256': 'The input-file identity is recorded separately in the gate manifest.',
        '$.seconds': 'Elapsed wall time is not deterministic page behaviour.',
        '$.units': 'This is a human-readable unit description; numeric coordinates remain exact.',
    },
    'checks': {
        '$.implementation_sha256': 'The implementation identity changes with the source revision.',
        '$.source_sha256': 'The input-file identity is recorded separately in the gate manifest.',
        '$.seconds': 'Elapsed wall time is not deterministic page behaviour.',
    },
    'cells': {
        '$.page_units': 'This is a human-readable frame description; page_size and box_page remain exact.',
        '$.orientation_mode': 'This labels a separately generated historical orientation review.',
        '$.orientation_output': 'This links a separately generated historical orientation review.',
    },
    'structure': {
        '$.units': 'This is a human-readable unit description; all geometry remains exact.',
        '$.provenance': 'This is the historical audit input-hash receipt, not boundary evidence.',
        '$.rejected_boundaries[].id': 'An internal name of a rejected candidate is not an accepted boundary.',
        '$.rejected_boundaries[].proposal_id': 'An internal proposal name of a rejected candidate is not a delivered link.',
        '$.rejected_boundaries[].track_id': 'An internal track name of a rejected candidate is not an accepted track.',
    },
}


def differences(a, b, path='$'):
    """No tolerances, coercion, rounding or array sorting; floats compare exactly."""
    if type(a) is not type(b):
        yield dict(path=path, kind='type', q2=type(a).__name__, api=type(b).__name__)
    elif isinstance(a, dict):
        for key in sorted(a.keys() | b.keys()):
            at = f'{path}.{key}'
            if key not in a or key not in b:
                yield dict(path=at, kind='missing', q2=key in a, api=key in b)
            else:
                yield from differences(a[key], b[key], at)
    elif isinstance(a, list):
        if len(a) != len(b):
            yield dict(path=path, kind='length', q2=len(a), api=len(b))
        for i, (x, y) in enumerate(zip(a, b)):
            yield from differences(x, y, f'{path}[{i}]')
    elif (a.hex() != b.hex()) if isinstance(a, float) else (a != b):
        yield dict(path=path, kind='value', q2=a, api=b)


def compare(a, b, family):
    # The C encoder checks the overwhelmingly common exact-equality case while
    # preserving float signs/types and array order. Only mismatches need paths.
    encoding = dict(sort_keys=True, separators=(',', ':'), allow_nan=False)
    if json.dumps(a, **encoding) == json.dumps(b, **encoding):
        return dict(equal=True, differences=[], metadata_differences=[])
    allowed, failures = [], []
    paths = ALLOWLIST.get(family, {})
    for difference in differences(a, b):
        path = re.sub(r'\[\d+\]', '[]', difference['path'])
        # Only the explicitly named audit provenance object exempts descendants.
        permit = path in paths or (family == 'structure' and path.startswith('$.provenance.'))
        (allowed if permit else failures).append(difference)
    return dict(equal=not failures, differences=failures, metadata_differences=allowed)


def load_reference(directory):
    ref = directory / 'reference' / 'greekocr'
    spec = importlib.util.spec_from_file_location('q2_reference', ref / '__init__.py',
                                                submodule_search_locations=[str(ref)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


def memoized_stage(fn, receipt):
    cache = {}
    @functools.wraps(fn)
    def call(*args, **kwargs):
        identity = hashlib.sha256(pickle.dumps((args, kwargs), protocol=5)).digest()
        if identity not in cache:
            cache[identity] = pickle.dumps(fn(*args, **kwargs), protocol=5)
            receipt['misses'] += 1
        else:
            receipt['hits'] += 1
        return pickle.loads(cache[identity])
    return call


def reference_join(lines, structure, cells, join_pieces, granularity):
    """Independent literal Q1b writer contract, plus Q1 delivery granularity."""
    structure = deepcopy(structure)
    # Q1b receives Q1's pre-validation names. Recreate that naming convention
    # from Q2's proposal ordinal without borrowing any current API result.
    for boundary in [*structure['boundaries'], *([structure['fold']] if structure['fold'] else []),
                     *(c[k] for c in structure['columns'] for k in ('left_boundary', 'right_boundary'))]:
        if boundary.get('proposal_id', '').startswith('proposal-'):
            boundary['proposal_id'] = boundary['proposal_id'].replace('proposal-', 'boundary-', 1)
    evidence = structure['crossing_evidence']
    for crossing in evidence:
        crossing['piece_indices'] = [p['index'] for p in cells if p['line_index'] == crossing['line_index']]
        crossing['row_id'] = lines[crossing['line_index']]['row_id']
        boundary = next(b for b in structure['boundaries'] if b['id'] == crossing['boundary_id'])
        crossing['proposal_id'] = boundary['proposal_id']
    joined, blocked = [], []
    for row in structure['rows']:
        if row['discounted']:
            continue
        members = [lines[i] for i in row['line_indices']]
        try:
            merged = join_pieces(members, structure=structure)
        except ValueError as exc:
            blocked.append(dict(row_id=row['id'], line_indices=row['line_indices'], table_id=row['table_id'],
                                reason=str(exc), crossings=[c for c in evidence if c['line_index'] in row['line_indices']]))
            row['joinable'] = False
        else:
            row['joinable'] = True
        if granularity == 'pieces' or (granularity == 'default' and row['table_id'] is not None):
            joined.extend(deepcopy(members))
        elif row['joinable']:
            joined.append(merged)
    return structure, dict(schema_version=1, rows=joined, blocked_rows=blocked, complete=not blocked,
                           geometry_policy='Exact original piece samples; interpolate only missing gap samples.')


def run_page(task):
    directory, path, cohort, book = task
    warnings.filterwarnings('ignore', category=np.exceptions.RankWarning)
    load_reference(directory)
    from q2_reference.glyphs.page_text_lines import segment_page, extract_line_image
    from q2_reference.glyphs.table_lines import prepare_delivery
    from q2_reference.glyphs.line_structure import join_pieces
    from q2_reference.glyphs.statistics import page_statistics, write_statistics
    from greekocr.pages import api, PageOptions, OutputOptions, process_page
    from greekocr.pages.layout import read_layout
    from greekocr.pages.lines import extract_line_image as new_extract
    from greekocr.pages.statistics import write_statistics as new_write
    import pyarrow.parquet as pq

    start = time.monotonic()
    key = path.stem
    frozen = ROOT / '.astra/out_after_Q2' / ('book_pages' if cohort == 'book' else '')
    with Image.open(path) as image:
        source = image.copy()
    gray = source.convert('L')
    layout = ROOT / '.astra/layout' / f'{key}.json'
    regions = read_layout(layout, source.size) if layout.exists() else []
    frame = [v / 3 for v in source.size]
    report = dict(page_key=key, cohort=cohort, book_id=book, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  checks={}, failures=[], metadata=[], modes={}, cache={})
    def check(name, a, b, family=''):
        result = compare(a, b, family)
        report['checks'][name] = result['equal']
        if result['differences']:
            report['failures'].append(dict(check=name, differences=result['differences']))
        if result['metadata_differences']:
            report['metadata'].append(dict(check=name, differences=result['metadata_differences']))

    cache_stats = {name: dict(hits=0, misses=0) for name in ('detection', 'delivery', 'statistics')}
    reference_detection = segment_page(gray)
    with patch.object(api.detector, 'segment_page', memoized_stage(api.detector.segment_page, cache_stats['detection'])), \
         patch.object(api, 'prepare_delivery', memoized_stage(api.prepare_delivery, cache_stats['delivery'])), \
         patch.object(api, 'page_statistics', memoized_stage(api.page_statistics, cache_stats['statistics'])):
        for tables in (False, True):
            mode = 'tables' if tables else 'default'
            old, pcs, _ = prepare_delivery(gray, deepcopy(reference_detection), regions if tables else [], supplement=tables)
            lines = [l.to_record() for l in old.lines]
            cells = [p.to_record(i, source.size, frame) for i, p in enumerate(pcs)]
            measured = page_statistics(source, lines, page_key=key, book_id=book, structure=old.structure)
            old_pixels = [(list(np.asarray(crop).shape), hashlib.sha256(np.asarray(crop).tobytes()).hexdigest())
                          for crop in (extract_line_image(gray, p.line) for p in pcs)]
            for statistics in (False, True):
                for granularity in (None, 'default', 'rows', 'pieces'):
                    name = f'{mode}.stats-{statistics}.join-{granularity}'
                    frozen_option = tables == (cohort == 'development') and statistics and granularity == ('rows' if cohort == 'development' else None)
                    selected = {'lines', 'segments', 'structure', 'cells', 'checks', 'delivery'} | ({'rows'} if granularity == 'rows' else set())
                    outputs = OutputOptions(directory / 'api' / cohort, selected) if frozen_option else OutputOptions()
                    result = process_page(source, page_key=key, book_id=book, page_size=frame,
                        table_regions=regions if tables else None,
                        options=PageOptions(tables=tables, statistics=statistics, join_lines=granularity is not None,
                                            granularity=granularity or 'default', outputs=outputs))
                    records = result.to_records()
                    expected_structure, joining = reference_join(lines, old.structure, cells, join_pieces, granularity) if granularity else (old.structure, None)
                    check(name+'.lines', lines, result.lines)
                    check(name+'.structure', expected_structure, result.structure)
                    check(name+'.cells', cells, records['cells']['cells'])
                    check(name+'.segments', [dict(line_id=f'{key}-s{i:05d}', box=list(b)) for i,b in enumerate(old.segments)], records['segments'])
                    check(name+'.diagnostics', old.diagnostics, result.segmentation.diagnostics)
                    check(name+'.delivery', joining['rows'] if joining else [l for l in lines if l['discounted'] is None], result.delivery)
                    check(name+'.joining', joining, result.joining)
                    check(name+'.statistics', measured if statistics else None, result.statistics)
                    if statistics and granularity is None:
                        new_pixels = [(list(np.asarray(crop).shape), hashlib.sha256(np.asarray(crop).tobytes()).hexdigest())
                                      for crop in (new_extract(source, p.line) for p in result.pieces)]
                        check(mode+'.crop_pixels', old_pixels, new_pixels)
                        old_paths = write_statistics(measured, directory / 'q2' / mode)
                        new_paths = new_write(result.statistics, directory / 'measurements' / mode)
                        old_table, new_table = pq.read_table(old_paths['glyphs']), pq.read_table(new_paths['glyphs'])
                        check(mode+'.parquet_schema', str(old_table.schema), str(new_table.schema))
                        check(mode+'.parquet_rows', old_table.to_pylist(), new_table.to_pylist())
                        with gzip.open(directory / f'{key}.{mode}.measurements.json.gz', 'wt') as stream:
                            json.dump(dict(q2=measured, api=result.statistics), stream, allow_nan=False)
                        report['modes'][mode] = dict(crops=len(pcs), glyphs=len(result.glyphs), lines=len(lines))
                    if frozen_option:
                        for field in ('lines', 'structure', 'cells', 'segments', 'rows', 'checks'):
                            reference = frozen / f'{key}.{field}.json'
                            if reference.exists():
                                actual = json.loads(Path(result.files[field]).read_text())
                                check('frozen.'+field, json.loads(reference.read_text()), actual, field)
                        report['blocked_rows'] = len(result.blocked_rows)
                        report['safe_rows'] = len(result.delivery)
                    del result, records, expected_structure, joining
    report['cache'] = cache_stats
    report['seconds'] = round(time.monotonic() - start, 3)
    report['equal'] = not report['failures']
    (directory / f'{key}.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    print(key, report['seconds'], 'checks', len(report['checks']), 'failures', len(report['failures']), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / '.astra/q3b-equality')
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [*sorted((ROOT/'greekocr').rglob('*.py')), Path(__file__)]}
    manifest = args.out / 'source-manifest.json'
    if args.resume:
        assert json.loads(manifest.read_text()) == source_hashes, 'Source changed; use a new output directory'
    else:
        manifest.write_text(json.dumps(source_hashes, indent=2))
    base = args.out / 'reference'
    base.mkdir(exist_ok=True)
    raw = subprocess.check_output(['git', 'archive', REFERENCE, 'greekocr'])
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        archive.extractall(base)
    selection = json.loads((ROOT/'.astra/book_pages/selection.json').read_text())
    identities = {r['page']: r['book'] for r in selection['pages']}
    sources = [(p, c) for c, d in [('development', 'pages'), ('book', 'book_pages')]
               for p in sorted((ROOT/'.astra'/d).glob('*.png'))]
    tasks, previous = [], {}
    for path, cohort in sources:
        if args.keys and path.stem not in args.keys:
            continue
        target = args.out / f'{path.stem}.json'
        if args.resume and target.exists():
            row = json.loads(target.read_text())
            assert row['source_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
            previous[path.stem] = row
        else:
            book = identities.get(path.stem, path.stem.split('-', 1)[-1].rsplit('-p', 1)[0])
            tasks.append((args.out, path, cohort, book))
    if args.workers == 1:
        done = [run_page(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            done = list(executor.map(run_page, tasks))
    previous.update({r['page_key']: r for r in done})
    pages = [previous[p.stem] for p, _ in sources if p.stem in previous]
    summary = dict(reference_commit=REFERENCE, frame='PNG/3', allowlist=ALLOWLIST, pages=pages,
                   equal=all(r['equal'] for r in pages), source_manifest=source_hashes,
                   api_calls=len(pages)*16, crops=sum(m['crops'] for r in pages for m in r['modes'].values()))
    (args.out/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False))
    print('COMPLETE', len(pages), 'pages', summary['api_calls'], 'API calls; equal:', summary['equal'], flush=True)
    return int(not summary['equal'])


if __name__ == '__main__':
    raise SystemExit(main())
