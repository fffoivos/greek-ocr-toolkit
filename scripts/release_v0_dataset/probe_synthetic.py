#!/usr/bin/env python3
"""Inventory existing synthetic builds and local Rust operation implementations.

Does not render, decode images, execute a generator, or infer missing historical
identity from today's source. Full metadata projection is the default.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
try:
    from .probe_sources import (canonical, files, kind, named_path, offline,
                                parquet_info, prepare_output, records, sha, write_json)
except ImportError:
    from probe_sources import (canonical, files, kind, named_path, offline,
                               parquet_info, prepare_output, records, sha, write_json)

PLAN_FIELDS = {
    'Identity': 'line_id reuse_index split factory_build_id source_build',
    'Image': 'image image_sha256 width height',
    'Text': 'text gt_nfd label_ids codec_version script_class',
    'Text origin': 'source_dataset source_doc_id text_source_locator text_sha256',
    'Rendering': 'font font_file_sha256 font_sha16 polarity bg_type accent_survival',
    'Applied': 'severity applied_ops n_ops',
    'Generator': 'generator_code_sha256 generator_binary_sha256 recipe_name recipe_sha256 recipe_effective_sha256',
    'Provenance': 'provenance_completeness historical_unknown_fields',
    'Training': 'trained_in',
}
FIELDS = set(' '.join(PLAN_FIELDS.values()).split())
EXTRA_FIELDS = {'seed', 'line_seed', 'per_line_seed', 'operation_parameters'}
ALIASES = {'image': 'image_png', 'text': 'gt_nfc',
           'font_file_sha256': 'font_sha256', 'font_sha16': 'sha16'}
DISTRIBUTIONS = ('severity', 'script_class', 'font', 'polarity', 'bg_type', 'source_dataset', 'reuse_index')
METADATA_KEYS = FIELDS | EXTRA_FIELDS | {
    'sha16', 'sha256', 'font_sha256', 'stem', 'code_sha256', 'binary_sha256', 'source_sha256',
    'source_effective_sha256', 'source_path', 'source_file', 'path', 'doc_id',
    'content_marginals', 'severity_weights', 'bg_weights', 'polarity_light_fraction',
    'letterspacing_fraction', 'crop', 'ink_transfer', 'fonts', 'strip_contract',
}


def op_implementations(source):
    """Bind a conservative, explicit map to functions actually present locally.

    Line numbers/SHA bind inspection evidence. Unknown new names remain unmapped.
    Rust dynamic crop suffixes map to detector_crop while preserving full names.
    This is a source locator map, not a claim about the producing binary.
    """
    mappings = {}
    sources = {}
    specs = {
        'ink_bleed': ('distort.rs', 'ink_ops'),
        'stroke_loss': ('distort.rs', 'ink_ops'),
        'ink_starve': ('distort.rs', 'ink_ops'),
        'edge_noise': ('distort.rs', 'ink_ops'),
        'ink_transfer_v2': ('distort.rs', 'ink_transfer_v2'),
        'neighbor_spill_above': ('distort.rs', 'neighbor_spill'),
        'neighbor_spill_below': ('distort.rs', 'neighbor_spill'),
        'verso_ghost': ('distort.rs', 'verso_bleed'),
        'verso_ghost_self': ('distort.rs', 'verso_bleed'),
        'crop:*': ('distort.rs', 'detector_crop'),
        'polarity_invert': ('distort.rs', 'finalize'),
        'synth:cs': ('build.rs', 'build_one'),
        'letterspaced': ('build.rs', 'build_one'),
    }
    photo = ('illumination page_stain paper_watermark roller_streaks brightness_contrast '
             'gamma gaussian_blur motion_blur gaussian_noise speckle stamp_overlay rotate '
             'baseline_wobble perspective lowres binarize jpeg').split()
    specs.update({op: ('distort.rs', 'image_ops') for op in photo})
    for file in sorted(source.glob('*.rs')):
        sources[file.name] = {'path': str(file), 'sha256': sha(file)}
    for op, (file, function) in specs.items():
        path = source / file
        if not path.is_file():
            continue
        text = path.read_text()
        match = re.search(r'(?m)^\s*(?:pub(?:\([^)]*\))?\s+)?fn\s+' + re.escape(function) + r'\b', text)
        # Ensure the op literal/family also occurs; a same-named function alone
        # is insufficient evidence for a different factory revision.
        literal = 'crop:' if op == 'crop:*' else f'"{op}"'
        if match and literal in text:
            mappings[op] = {'file': file, 'function': function,
                            'line': text[:match.start()].count('\n') + 1,
                            'source_sha256': sources[file]['sha256']}
            if op == 'jpeg':
                mappings[op]['note'] = 'image_ops records name; encode/decode round-trip in distort.rs:finalize'
            if op in ('synth:cs', 'letterspaced'):
                mappings[op]['note'] = 'build_one records rendering marker; render.rs:render_ink renders glyphs'
    return {'source_root': str(source), 'exists': source.is_dir(), 'files': sources,
            'map': mappings, 'binding': 'local source only; historical code/binary SHA requires build evidence'}


def evidence_fields(value, location='', depth=0, origin=''):
    """Yield nested field locations without writing text, labels, or image bytes."""
    if depth > 20:
        return
    if isinstance(value, dict):
        for key, val in value.items():
            where = f'{location}.{key}' if location else key
            if key in METADATA_KEYS and val is not None:
                # Hashes/seeds and configured distributions are useful evidence.
                # Text/source labels themselves are deliberately not emitted.
                safe = val if (key.endswith('sha256') or key in ('sha16', 'seed', 'strip_contract',
                    'content_marginals', 'severity_weights', 'bg_weights', 'polarity_light_fraction',
                    'letterspacing_fraction', 'crop', 'ink_transfer')) else None
                yield key, where, safe
                if key == 'font_sha256' or (key == 'sha256' and ('fonts' in location.lower() or 'font' in origin.lower())):
                    if isinstance(val, str) and re.fullmatch(r'[0-9a-fA-F]{64}', val):
                        yield 'font_file_sha256', where, val
            if key not in ('image', 'image_png', 'content', 'text', 'gt_nfc', 'gt_nfd'):
                yield from evidence_fields(val, where, depth + 1, origin)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from evidence_fields(item, f'{location}[{i}]', depth + 1, origin)


def inspect_build(name, root, output, op_map, sample_rows=None, evidence=()):
    result = {'name': name, 'root': str(root), 'exists': root.exists(), 'files': [],
              'parquet_tables': [], 'rows_per_split': {}, 'recipes_found': [],
              'metadata_evidence': [], 'errors': [], 'mode': 'sample' if sample_rows else 'full_metadata'}
    present, nonnull = Counter(), Counter()
    metadata = defaultdict(list)
    split_rows = Counter()
    split_scanned = Counter()
    ops = defaultdict(Counter)
    distributions = defaultdict(lambda: defaultdict(Counter))
    total_scanned = 0
    recipe_files = []
    for path in files(root, on_error=lambda exc: result['errors'].append(
            {'path': str(exc.filename), 'error': f'{type(exc).__name__}: directory unreadable'})):
        if path.is_symlink():
            continue
        rel = path.name if root.is_file() else path.relative_to(root).as_posix()
        result['files'].append({'path': rel, 'bytes': path.stat().st_size})
        if kind(path) == 'parquet':
            try:
                pf, schema = parquet_info(path)
                table = {'path': rel, 'schema': schema, 'rows': pf.metadata.num_rows, 'scanned': 0}
                result['parquet_tables'].append(table)
                columns = (FIELDS | EXTRA_FIELDS | set(ALIASES.values()) | set(DISTRIBUTIONS)) - {'image', 'image_png'}
                iterator = records(path, columns=columns)
                for row in iterator if sample_rows is None else itertools.islice(iterator, sample_rows):
                    split = row.get('split') or 'UNKNOWN'
                    split = str(split)
                    split_scanned[split] += 1
                    table['scanned'] += 1
                    total_scanned += 1
                    for field in FIELDS | EXTRA_FIELDS:
                        col = field if field in schema else ALIASES.get(field, field)
                        if col in schema:
                            present[field] += 1
                            if col == 'image_png':
                                # Presence only: null image counts require a later
                                # payload readback, not a metadata probe.
                                continue
                            if row.get(col) is not None:
                                nonnull[field] += 1
                    for op in row.get('applied_ops') or []:
                        ops[split][str(op)] += 1
                    for field in DISTRIBUTIONS:
                        if row.get(field) is not None:
                            distributions[split][field][str(row[field])] += 1
                if table['scanned'] == table['rows']:
                    table['complete'] = True
                    # Per-row split wins over directory labels.
                else:
                    table['complete'] = False
            except Exception as exc:
                result['errors'].append({'path': rel, 'error': f'{type(exc).__name__}: {exc}'})
        elif kind(path) in ('json', 'jsonl'):
            recipe_files.append(path)
        elif path.suffix.lower() in ('.toml', '.yaml', '.yml') and 'recipe' in path.name.lower():
            result['recipes_found'].append({'path': str(path), 'bytes': path.stat().st_size,
                                            'sha256': sha(path), 'parsed': False})
    # Evidence outside the build is explicit and never recursively followed.
    for path in [*recipe_files, *evidence]:
        try:
            if path.is_symlink() or not path.is_file():
                raise ValueError('missing or symlink evidence file')
            entry = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path), 'fields': []}
            result['metadata_evidence'].append(entry)
            # Whole-object receipts are bounded. Large word/source JSONL is
            # streamed; only field presence/locations are collected (max 5 each).
            if kind(path) == 'json' and path.stat().st_size > 32_000_000:
                entry['not_scanned_reason'] = 'large JSON: inspect a selected map with probe_sources --json-map'
                continue
            iterator = records(path)
            for number, value in enumerate(iterator):
                if sample_rows and number >= sample_rows:
                    entry['sampled'] = True
                    break
                if not isinstance(value, dict):
                    continue
                for field, location, val in evidence_fields(value, origin=path.name):
                    record = {'path': str(path), 'field_path': location, 'record': number}
                    if val is not None:
                        record['value'] = val
                    if len(metadata[field]) < 5:
                        metadata[field].append(record)
                    if field not in entry['fields']:
                        entry['fields'].append(field)
                if 'recipe' in value or 'recipe' in path.name.lower() or 'severity_weights' in value:
                    if str(path) not in [x['path'] for x in result['recipes_found']]:
                        result['recipes_found'].append({'path': str(path), 'sha256': entry['sha256'], 'parsed': True})
            entry['fields'].sort()
        except Exception as exc:
            result['errors'].append({'path': str(path), 'error': f'{type(exc).__name__}: {exc}'})
    complete = bool(result['parquet_tables']) and not result['errors'] and all(t.get('complete') for t in result['parquet_tables'])
    if complete:
        split_rows.update(split_scanned)
    result['rows_per_split'] = dict(sorted(split_rows.items())) if complete else None
    result['sample_rows_per_split'] = dict(sorted(split_scanned.items()))
    result['rows_in_footers'] = sum(t['rows'] for t in result['parquet_tables'])
    result['rows_scanned'] = total_scanned
    result['complete'] = complete
    result['field_presence'] = {}
    computable = {'image_sha256': 'hash original embedded image bytes in builder',
                  'height': 'read original PNG header in builder',
                  'n_ops': 'len(ordered applied_ops)', 'text_sha256': 'hash explicitly identified source-text bytes; label hash alone is insufficient',
                  'provenance_completeness': 'derive from retained evidence and unknown reasons',
                  'historical_unknown_fields': 'derive with per-field search receipts',
                  'trained_in': 'join actual per-model draw evidence; availability is separate'}
    for field in sorted(FIELDS | EXTRA_FIELDS):
        field_evidence = metadata[field]
        if field == 'font_sha16':
            field_evidence = field_evidence + [r for r in metadata['sha16']
                if 'fonts[' in r['field_path'] or 'font' in Path(r['path']).name.lower()]
        status = ('row_column' if present[field] else 'build_evidence_only' if field_evidence else
                  'absent_in_searched_evidence' if complete else 'not_observed_in_incomplete_search')
        record = {'status': status, 'column_rows_scanned': present[field],
                  'nonnull_rows_scanned': nonnull[field] if field != 'image' else None,
                  'build_evidence': field_evidence, 'aliases_checked': [ALIASES[field]] if field in ALIASES else []}
        if field in computable:
            record['builder_action'] = computable[field]
        if field == 'seed':
            record['note'] = 'build recipe seed is not a stored per-line seed'
        if field == 'font_file_sha256':
            record['note'] = 'sha16 is not a full file SHA; do not pad or promote it'
        result['field_presence'][field] = record
    result['plan_field_groups'] = {key: value.split() for key, value in PLAN_FIELDS.items()}
    result['font_hash_evidence'] = {'full_sha': metadata['font_file_sha256'],
                                   'sha16': metadata['font_sha16'] + metadata['sha16']}
    result['unbound_identity_candidates'] = {field: metadata[field] for field in
        ('code_sha256', 'binary_sha256', 'source_sha256', 'source_effective_sha256', 'sha256')}
    result['configured_distributions'] = {field: metadata[field] for field in
        ('content_marginals', 'severity_weights', 'bg_weights', 'polarity_light_fraction', 'letterspacing_fraction', 'crop', 'ink_transfer')}
    result['realised_distributions'] = {split: {field: dict(sorted(counts.items())) for field, counts in fields.items()}
                                        for split, fields in distributions.items()}
    result['operations'] = {}
    for split, counts in sorted(ops.items()):
        result['operations'][split] = []
        for name_, count in sorted(counts.items()):
            implementation = op_map['map'].get(name_) or (op_map['map'].get('crop:*') if name_.startswith('crop:') else None)
            result['operations'][split].append({'name': name_, 'occurrences': count,
                'implementation': implementation, 'mapping_status': 'local_source' if implementation else 'UNMAPPED'})
    result['limitations'] = ['no pixels decoded or read from Parquet',
        'op counts are occurrences, not mutually exclusive row percentages; sequence stays in source rows',
        'build evidence is not a validated row-level binding', 'no historical hashes inferred from current local source',
        'field absence is scoped to explicit build/evidence files searched',
        'source text hash must not be replaced with the final label hash']
    write_json(output / f'{name}.synthetic.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='append', required=True, help='NAME=/local/build (repeat)')
    parser.add_argument('--evidence', action='append', default=[], help='BUILD_NAME=/explicit/receipt.json (repeat)')
    parser.add_argument('--factory-src', required=True, type=Path, help='local greekocr/_vendor/factory/src')
    parser.add_argument('--output-dir', required=True, type=Path, help='fresh directory, disjoint from all inputs')
    parser.add_argument('--sample-rows', type=int, help='diagnostic only: limit rows per file')
    args = parser.parse_args(argv)
    offline()
    builds = [named_path(x) for x in args.build]
    extras = [named_path(x) for x in args.evidence]
    if len(dict(builds)) != len(builds) or (args.sample_rows is not None and args.sample_rows <= 0):
        parser.error('unique build names and positive sample-rows required')
    if any(n not in dict(builds) for n, _ in extras):
        parser.error('evidence name must name a build')
    output = prepare_output(args.output_dir, [p for _, p in builds + extras] + [args.factory_src])
    mapping = op_implementations(args.factory_src)
    write_json(output / 'OP_IMPLEMENTATIONS.json', mapping)
    reports = [inspect_build(n, p, output, mapping, args.sample_rows, [v for k, v in extras if k == n]) for n, p in builds]
    write_json(output / 'PROBE_RECEIPT.json', {'schema': 'release-v0-synthetic-probe-1',
        'script_sha256': sha(__file__), 'network_used': False, 'parquet_image_payloads_read': False,
        'shared_helper_sha256': sha(Path(__file__).with_name('probe_sources.py')),
        'python_version': sys.version.split()[0],
        'builds': [{'name': r['name'], 'complete': r['complete'], 'rows': r['rows_in_footers']} for r in reports]})
    return 2 if not mapping['exists'] or any(r['errors'] or not r['exists'] or not r['parquet_tables'] for r in reports) else 0


if __name__ == '__main__':
    raise SystemExit(main())
