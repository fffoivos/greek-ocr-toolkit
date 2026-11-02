"""Physical layer readback and lossless card-join verification for inherited checks."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from .common import canonical, digest, safe_path
from .layered import LAYER_CONFIGS, config_rows


def load_frozen(a):
    """Read exact public bytes, indexing occurrences by A1's prepared locator."""
    from .accept_dataset import decode_sample, require
    from .build_locks import validate_frozen
    from .frozen_identity import public_file, public_logical
    frozen = a.manifest.get('frozen_trained', {})
    a.frozen_available = bool(frozen.get('files'))
    if not a.frozen_available:
        return
    snapshot = frozen.get('public_snapshot_root') if a.validation_mode == 'external-cache' else None
    mapping = None
    if frozen.get('schema') == 'hfd-frozen-trained-v1':
        # Portable binding first: the packaged, manifest-verified A1 receipt and the
        # public occurrence mapping. Only the stronger source modes open the
        # external absolute A1 path as well.
        report = packaged_a1(a, frozen)
        if a.validation_mode in ('external-cache', 'complete-download-a1-source'):
            a.ledger.verify_many([frozen['a1']])
            validate_frozen(frozen, Path(frozen['a1']['path']))
            from .common import sanitize
            require(sanitize(json.loads(Path(frozen['a1']['path']).read_text())) == report,
                    'packaged A1.json differs from the source A1 receipt')
        require(frozen == a.lock['frozen_trained'], 'manifest/input frozen lock differs')
        mapping = {f['public_path']: f for f in frozen['occurrence_mapping']}
    # Schema-less historical fixtures use package-local frozen files. Versioned
    # locks always require the A1 occurrence mapping, never a public/prepared join.
    by_path = {entry['path']: entry for entry in frozen['files']}
    a.ledger.verify_many({**entry, 'path': str(public_file(snapshot, entry['path'])
        if snapshot else safe_path(a.root, entry['path']))} for entry in frozen['files'])
    kwargs = dict(root=Path(snapshot)) if snapshot else {}
    for path, natives in a.parquet_units('frozen', by_path, **kwargs):
        entry = by_path[path]
        locator = mapping[path] if mapping else None
        ordered, rows = hashlib.sha256(), 0
        for ordinal, native in enumerate(natives):
            if locator:
                ordered.update((canonical(public_logical(native, locator['pool'],
                    locator['source_shard'], ordinal)) + '\n').encode())
            binary = native.pop('image_png', None)
            image = native.pop('image', None)
            binary = binary or (image.get('bytes') if isinstance(image, dict) else image)
            require(binary is not None, 'frozen trainer image missing')
            if ordinal < 4:
                decode_sample(binary)
            a.image_count += 1
            rows += 1
            a.db.execute('INSERT INTO frozen VALUES(?,?,?,?,?)',
                (entry['pool'], locator['prepared_path'] if locator else entry['source_shard'],
                 ordinal, canonical(native), binary))
        if locator:
            require(rows == locator['rows'] and ordered.hexdigest() == locator['ordered_digest'],
                    'frozen ordered digest/count differs from A1: ' + path)


def packaged_a1(a, frozen):
    """Verify the frozen view from the public package alone (M4).

    manifests/A1.json is covered by MANIFEST/SHA256SUMS, so byte_check has already
    verified it. It must be a complete PASS receipt that reproduces the published
    occurrence mapping and every frozen file identity, and equal the A1 identity
    bound into the packaged INPUT_LOCK.
    """
    from .accept_dataset import require
    from .build_locks import validate_frozen
    from .card import validate_a1
    from .frozen_identity import occurrence_mapping
    path = a.root / 'manifests/A1.json'
    require('manifests/A1.json' in {e['path'] for e in a.manifest['files']} and path.is_file(),
            'packaged manifests/A1.json is missing from the manifest')
    report = validate_a1(json.loads(path.read_text()))
    validate_frozen(frozen)
    require(occurrence_mapping(report) == frozen['occurrence_mapping'], 'packaged A1 occurrence mapping differs')
    require(report.get('revision') == frozen['revision'] and report.get('repo') == frozen['repo'],
            'packaged A1 revision/repo differs from the frozen tree')
    require(not report.get('first_20_mismatches') and not any(f.get('first_20_mismatches') for f in report['files']),
            'packaged A1 contains mismatches')
    by_path = {f['public_path']: f for f in report['files']}
    require(len(by_path) == len(report['files']) and set(by_path) == {f['path'] for f in frozen['files']},
            'packaged A1 and frozen trained paths differ')
    for entry in frozen['files']:
        f = by_path[entry['path']]
        require(f['public_sha256'] == entry['sha256'] and f['pool'] == entry['pool']
                and f['source_shard'] == entry['source_shard'] and f['prepared_rows'] == f['public_rows']
                and f['prepared_ordered_digest'] == f['public_ordered_digest'], 'packaged A1 frozen shard identity differs')
    if a.lock.get('trained_identity') is not None:
        require(a.lock['trained_identity'] == report, 'packaged A1 differs from the INPUT_LOCK trained identity')
    return report


def declared_configs(a, strict=True):
    """Emulate `load_dataset` per config with pyarrow, from the README YAML.

    Every declared file must open, the YAML must equal the manifest configs, and
    each config must have one Arrow schema across all its files and splits (the
    HF parquet builder concatenates them as one feature set). Final acceptance
    is strict; other modes record a FAIL, which withholds qualified loading.
    """
    try:
        return _declared_configs(a)
    except (ValueError, OSError) as exc:
        if strict:
            raise
        return {'status': 'FAIL', 'reason': str(exc)[:500]}


def _declared_configs(a):
    from .accept_dataset import require
    from .common import safe_path
    from .frozen_identity import public_file
    import pyarrow.parquet as pq
    try:
        import yaml
    except ImportError as exc:
        raise ValueError('README YAML config check requires PyYAML') from exc
    front = yaml.safe_load((a.root / 'README.md').read_text().split('---', 2)[1])
    declared = {c['config_name']: {f['split']: [f['path']] if isinstance(f['path'], str) else list(f['path'])
                for f in c['data_files']} for c in front['configs']}
    require(len(declared) == len(front['configs']), 'duplicate README YAML config')
    require(declared == a.manifest['configs'], 'README YAML configs differ from the manifest')
    default = 'real' if 'real' in declared else 'lines'
    require([c['config_name'] for c in front['configs'] if c.get('default')] == [default], 'README default config differs')
    frozen = a.manifest.get('frozen_trained', {})
    frozen_paths = {f['path'] for f in frozen.get('files', [])}
    snapshot = frozen.get('public_snapshot_root') if a.validation_mode == 'external-cache' else None
    result = {}
    for name, splits in sorted(declared.items()):
        schema, rows = None, {}
        for split, paths in splits.items():
            require(paths and len(paths) == len(set(paths)), 'empty or duplicated declared split: ' + name + '/' + split)
            rows[split] = 0
            for path in paths:
                file = public_file(snapshot, path) if snapshot and path in frozen_paths else safe_path(a.root, path)
                parquet = pq.ParquetFile(file)
                measured = parquet.schema_arrow.remove_metadata()
                schema = schema or measured
                require(measured.equals(schema), f'config {name} declares more than one schema ({split}: {path})')
                rows[split] += parquet.metadata.num_rows
        result[name] = rows
    return {'status': 'PASS', 'loader': 'pyarrow emulation of README YAML data_files', 'rows': result}


def card_recipe(a):
    """Execute the card's literal pyarrow loader and join blocks on this package."""
    from .accept_dataset import require
    from .card import card_generation, recipe_blocks
    text = (a.root / 'README.md').read_text()
    blocks = recipe_blocks(text)
    generation = card_generation(text)
    require(f'"{generation}"' in blocks['loader-datasets'], 'card loader revision differs from the card generation')
    compile(blocks['loader-datasets'], 'README.md:loader-datasets', 'exec')
    try:
        import pandas  # noqa: F401
    except ImportError as exc:
        raise ValueError('final acceptance executes the card recipe and requires pandas') from exc
    env = {'__name__': 'hfd_card_recipe', 'root': a.root}
    try:
        exec(compile(blocks['loader-pyarrow'], 'README.md:loader-pyarrow', 'exec'), env)
        exec(compile(blocks['join'], 'README.md:join', 'exec'), env)
    except AssertionError as exc:
        require(False, 'card recipe assertion failed: ' + repr(exc))
    frozen = a.manifest['frozen_trained']['occurrence_mapping']
    expected = {name: sum(f['rows'] for f in frozen if f['public_path'].startswith('data/' + name + '/'))
                for name in ('real', 'synthetic')}
    lines = a.db.execute("SELECT COUNT(*) FROM r WHERE t='lines'").fetchone()[0]
    require(len(env['real']) == expected['real'], 'card recipe real trained cardinality differs')
    require(len(env['synthetic']) == expected['synthetic'], 'card recipe synthetic trained cardinality differs')
    require(len(env['current']) == lines, 'card recipe real observation cardinality differs')
    views = {}
    for split, view in env['views'].items():
        count = a.db.execute("SELECT COUNT(*) FROM r WHERE t='synthetic' AND json_extract(j,'$.split')=?", (split,)).fetchone()[0]
        require(len(view) == count, 'card recipe synthetic view cardinality differs: ' + split)
        views[split] = len(view)
    return {'status': 'PASS', 'model': str(env['MODEL']), 'real_trained': len(env['real']),
            'synthetic_trained': len(env['synthetic']), 'real_observations': len(env['current']),
            'null_trainer_line_id': int(env['current']['trainer_line_id'].isna().sum()),
            'ambiguous_synthetic': int((env['synthetic']['synthetic_mapping_status'] != 'unique_exact').sum()),
            'synthetic_views': views, 'generation': generation}


ENRICH_RECEIPTS = ('manifests/ENRICH_RECEIPT.json', 'ENRICH_RECEIPT.json')
ENRICH_MODULE = r'scripts\.release_v0_enrich(?:\.[A-Za-z_][A-Za-z0-9_]*)+'
ENRICH_FUNCTION = r'[A-Za-z_][A-Za-z0-9_]*'


ENRICH_PACKAGE = Path(__file__).resolve().parents[1] / 'release_v0_enrich'


def _supp_entries(value):
    if isinstance(value, dict):
        if {'root', 'path', 'sha256'} <= value.keys():
            yield value
        for item in value.values():
            yield from _supp_entries(item)
    elif isinstance(value, list):
        for item in value:
            yield from _supp_entries(item)


def enrichment_identity(root, base):
    """Everything a cached enrichment result depends on, for the resume binding.

    The supplied base's manifest digests are recomputed on every construction, so
    a different or changed base never matches a saved binding. Also bound: the
    receipt, the E1 code it names, the E1 verifier code that would run now, and
    stat stamps of every supplementary source file in the packaged SUPP_LOCK.
    """
    from .common import sha
    from .readback_state import stamp
    root = Path(root)
    identity = {'base': None, 'receipt_sha256': None, 'receipt_code': None, 'verifier_code': None,
                'supp_lock_sha256': None, 'supp_sources': None}
    if base is not None:
        base = Path(base).resolve()
        identity['base'] = {'path': str(base), **{name: sha(base / name) if (base / name).is_file() else None
                            for name in ('manifests/MANIFEST.json', 'C_MANIFEST.json')}}
    found = [p for p in ENRICH_RECEIPTS if (root / p).is_file()]
    if not found:
        return identity
    receipt = json.loads((root / found[0]).read_text())
    identity.update(receipt_sha256=sha(root / found[0]), receipt_code=receipt.get('code'),
                    verifier_code={p.name: sha(p) for p in sorted(ENRICH_PACKAGE.glob('*.py'))}
                    if ENRICH_PACKAGE.is_dir() else None)
    lock_path = root / 'manifests/SUPP_LOCK.json'
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text())
        roots = lock.get('roots') or {}
        sources = {}
        for entry in _supp_entries(lock.get('entries', lock)):
            if entry['root'] not in roots:
                continue
            path = Path(roots[entry['root']]) / entry['path']
            sources[str(path)] = stamp(path) if path.is_file() else 'missing'
        identity.update(supp_lock_sha256=sha(lock_path), supp_sources=sources)
    return identity


def enrichment(a, base):
    """Generic hook for a derived candidate C′ that carries ENRICH_RECEIPT.json.

    The receipt must bind the base candidate's manifest SHA256 (`base.manifest_sha256`
    or a top-level `base_manifest_sha256`), matching manifests/MANIFEST.json or the
    C_MANIFEST.json seal of --enrich-base, and name its acceptance entry point inside
    scripts.release_v0_enrich, either as {module, function, argv} with {candidate},
    {base} and {receipt} placeholders, or as "module:function" called with
    candidate/base/receipt paths. E1 owns that check; it must return a PASS status
    dict (or exit code 0). SystemExit or any other result fails closed.
    """
    import importlib
    import inspect
    import re
    from .accept_dataset import require
    from .common import sha
    found = [p for p in ENRICH_RECEIPTS if (a.root / p).is_file()]
    if not found:
        return None
    require(len(found) == 1, 'several ENRICH_RECEIPT.json files')
    receipt_path = a.root / found[0]
    receipt = json.loads(receipt_path.read_text())
    bound = (receipt.get('base') or {}).get('manifest_sha256') if isinstance(receipt.get('base'), dict) else None
    bound = bound or receipt.get('base_manifest_sha256')
    require(isinstance(bound, str) and len(bound) == 64, 'ENRICH_RECEIPT lacks its base manifest SHA256 binding')
    require(base is not None, 'ENRICH_RECEIPT requires --enrich-base (the base candidate C)')
    base = Path(base).resolve()
    require(base != a.root, 'enrichment base must be the base candidate, not C′')
    digests = {name: sha(base / name) for name in ('manifests/MANIFEST.json', 'C_MANIFEST.json') if (base / name).is_file()}
    matched = sorted(name for name, value in digests.items() if value == bound)
    require(matched, 'ENRICH_RECEIPT base manifest SHA256 differs from --enrich-base')
    entry = receipt.get('acceptance_entry_point')
    # Portable (complete-download) acceptance uses the packaged A1 only; the external
    # source A1 replay belongs to the explicit stronger modes (CP-enrich finding 4).
    a1_binding = 'packaged' if a.validation_mode == 'complete-download' else 'source'
    values = {'candidate': str(a.root), 'base': str(base), 'receipt': str(receipt_path),
              'validation_mode': a.validation_mode, 'a1_binding': a1_binding}
    if isinstance(entry, dict):
        module, name, argv = entry.get('module'), entry.get('function'), entry.get('argv')
        require(isinstance(argv, list) and all(isinstance(v, str) for v in argv), 'enrichment entry point argv must be strings')
        argv = [values[v[1:-1]] if v.startswith('{') and v.endswith('}') and v[1:-1] in values else v for v in argv]
    else:
        module, _, name = entry.partition(':') if isinstance(entry, str) else (None, None, None)
        argv = None
    require(isinstance(module, str) and re.fullmatch(ENRICH_MODULE, module) and isinstance(name, str)
            and re.fullmatch(ENRICH_FUNCTION, name),
            'enrichment acceptance entry point must name scripts.release_v0_enrich.<module> and a function')
    function = getattr(importlib.import_module(module), name)
    try:
        if argv is not None:
            result = function(argv)
        else:
            parameters = inspect.signature(function).parameters
            aliases = {'candidate': a.root, 'candidate_root': a.root, 'base': base, 'base_root': base,
                       'receipt': receipt_path, 'receipt_path': receipt_path,
                       'validation_mode': a.validation_mode, 'a1_binding': a1_binding}
            unknown = [p for p, v in parameters.items() if p not in aliases and v.default is inspect.Parameter.empty
                       and v.kind not in (v.VAR_POSITIONAL, v.VAR_KEYWORD)]
            require(not unknown, 'enrichment entry point has unsupported required parameters: ' + ', '.join(unknown))
            result = function(**{p: str(v) for p, v in aliases.items() if p in parameters})
    except SystemExit as exc:
        require(False, f'enrichment acceptance exited with {exc.code!r}')
    passed = result == 0 if isinstance(result, int) and not isinstance(result, bool) else (
        isinstance(result, dict) and result.get('status') == 'PASS')
    require(passed, 'enrichment acceptance did not PASS: ' + repr(result)[:300])
    summary = result if isinstance(result, int) else {k: v for k, v in result.items()
                                                      if isinstance(v, (str, int, float, bool, type(None), dict))}
    return {'status': 'PASS', 'receipt': found[0], 'base_binding': matched, 'entry_point': f'{module}:{name}',
            'result': json.loads(json.dumps(summary, default=str))}


def enrichment_configs(a, configs):
    """Configs a C′ enrichment appended: allowed only when every one of their paths
    is listed as appended by its ENRICH_RECEIPT.json (base configs stay exact)."""
    extra = set(configs) - {'real', 'synthetic'} - LAYER_CONFIGS
    if not extra:
        return set()
    from .accept_dataset import require
    found = [p for p in ENRICH_RECEIPTS if (a.root / p).is_file()]
    require(len(found) == 1, 'unexpected HF configs without an enrichment receipt: ' + ', '.join(sorted(extra)))
    appended = set(json.loads((a.root / found[0]).read_text()).get('appended') or [])
    for name in extra:
        require(all(path in appended for paths in configs[name].values() for path in paths),
                'enrichment config not declared as appended: ' + name)
    return extra


def load(acceptor):
    from .accept_dataset import KEYS, decode_sample, require
    a = acceptor
    configs = a.manifest['configs']
    extra = enrichment_configs(a, configs)
    require(set(configs) - {'real', 'synthetic'} - extra == LAYER_CONFIGS, 'missing/unexpected HF configs')
    require(configs == json.loads((a.root / 'manifests/CONFIGS.json').read_text()), 'config index mismatch')
    try:
        import yaml
    except ImportError:
        yaml = None
    if yaml:
        front = yaml.safe_load((a.root / 'README.md').read_text().split('---', 2)[1])
        parsed = {c['config_name']: {s['split']: s['path'] for s in c['data_files']} for c in front['configs']}
        require(parsed == configs, 'card HF YAML differs from manifest')
    a.db.executescript('CREATE TABLE IF NOT EXISTS images(h TEXT PRIMARY KEY,b BLOB); CREATE TABLE IF NOT EXISTS frozen(pool TEXT,shard TEXT,ordinal INTEGER,j TEXT,b BLOB,PRIMARY KEY(pool,shard,ordinal)); CREATE TABLE IF NOT EXISTS reference_images(h TEXT PRIMARY KEY);')
    manifested = {e['path'] for e in a.manifest['files']}
    for name in sorted(configs):
        if name in ('real', 'synthetic'):
            continue
        for paths in configs[name].values():
            require(all(p in manifested for p in paths), 'config path not manifested')
        paths = [p for values in configs[name].values() for p in values]
        for path, outputs in a.parquet_units('layer:' + name, paths):
            for output in outputs:
                from .layered import unpack
                row = unpack(output)
                if name == 'crops' or (name in extra and 'crop_sha256' in row and 'image' in row):
                    image = row.get('image') or {}
                    binary = image.get('bytes')
                    require(binary is not None and image.get('path') is None, 'nonportable image value')
                    require(digest(binary) == row['crop_sha256'], 'embedded image hash mismatch')
                    if name != 'crops':
                        # Appended reference variants never replace or duplicate published crops.
                        require(a.db.execute('SELECT 1 FROM images WHERE h=?', (row['crop_sha256'],)).fetchone() is None,
                                'appended reference image duplicates published bytes')
                        a.db.execute('INSERT INTO reference_images VALUES(?)', (row['crop_sha256'],))
                    a.db.execute('INSERT INTO images VALUES(?,?)', (row['crop_sha256'], binary))
                    a.image_count += 1
                    if a.image_count < 5:
                        decode_sample(binary)
                    continue
                target = {'synthetic_lines': 'synthetic'}.get(name, name)
                if name == 'page_images':
                    image = row.get('image') or {}
                    binary = image.get('bytes')
                    require(binary is not None and digest(binary) == row.get('image_sha256'), 'page embedded image hash mismatch')
                    row.pop('image', None)
                    row['image_measured_sha256'] = digest(binary)
                    a.image_count += 1
                if target not in KEYS:
                    key = [row['row_key']]
                else:
                    key = [row.get(k) for k in KEYS[target]]
                require(all(k is not None for k in key), 'null public key: ' + name)
                try:
                    a.db.execute('INSERT INTO r VALUES(?,?,?)', (target, canonical(key), canonical(row)))
                except Exception as exc:
                    raise ValueError('duplicate public key: ' + name + ':' + canonical(key)) from exc
    # Identified validation/reserved synthetic byte views are separate from frozen train.
    # The builder exports them in synthetic_key order (store key; page ''), so a view
    # re-projected to the frozen 19-column schema (H3) joins by position within its
    # split, verified by image bytes and identity/label fields. A view that still
    # carries the key columns joins by key.
    import pyarrow.parquet as pq
    for split, paths in configs.get('synthetic', {}).items():
        if split not in ('val', 'reserved'):
            continue
        require(all(path in manifested for path in paths), 'synthetic view path not manifested')
        ordered = [k for k, in a.db.execute(
            "SELECT k FROM r WHERE t='synthetic' AND json_extract(j,'$.split')=? ORDER BY k", (split,))]
        offsets, total = {}, 0
        for path in paths:
            offsets[path] = total
            total += pq.ParquetFile(safe_path(a.root, path)).metadata.num_rows
        require(total == len(ordered), 'synthetic view row count differs from metadata: ' + split)
        for path, outputs in a.parquet_units('synthetic-view', paths):
            for ordinal, output in enumerate(outputs, offsets[path]):
                from .layered import unpack
                row = unpack(output) if 'record_json' in output else output
                binary = (row.get('image') or {}).get('bytes')
                require(binary is not None, 'synthetic view image missing')
                measured = digest(binary)
                if all(row.get(k) is not None for k in KEYS['synthetic']):
                    key = canonical([row[k] for k in KEYS['synthetic']])
                    require(key == ordered[ordinal], 'synthetic view is not in synthetic_key order: ' + split)
                key = ordered[ordinal]
                base = a.find('synthetic', json.loads(key))
                require(base is not None and base['split'] == split, 'synthetic view -> metadata FK fails')
                require(row.get('image_sha256', measured) == measured == base['image_sha256'], 'synthetic embedded hash differs')
                require(all(row[k] == base.get(k) for k in ('line_id', 'reuse_index', 'gt_nfc', 'gt_nfd', 'label_ids',
                                                            'codec_version', 'split') if k in row),
                        'synthetic view identity/label differs from metadata')
                base['image_measured_sha256'] = measured
                a.db.execute("UPDATE r SET j=? WHERE t='synthetic' AND k=?", (canonical(base), key))
                a.image_count += 1
    # Open frozen trainer files supplied by A1. A missing frozen view is not a release PASS.
    load_frozen(a)
    for key, row in a.checked_items('frozen-synthetic', 'synthetic'):
        candidate = a.db.execute("SELECT frozen.b FROM frozen JOIN r ON json_extract(r.j,'$.pool')=frozen.pool AND json_extract(r.j,'$.source_shard')=frozen.shard AND json_extract(r.j,'$.source_ordinal')=frozen.ordinal WHERE r.t='training_membership' AND json_extract(r.j,'$.synthetic_match_group')=? LIMIT 1", (row['synthetic_match_group'],)).fetchone()
        if candidate:
            require(digest(candidate[0]) == row['image_sha256'], 'synthetic frozen payload differs')
            row['image_measured_sha256'] = digest(candidate[0])
            a.db.execute("UPDATE r SET j=? WHERE t='synthetic' AND k=?", (canonical(row), key))
    # Reconstruct real groups from lines -> current labels -> features -> crop, plus trainer membership.
    count = 0
    for _, line in a.checked_items('roundtrip', 'lines'):
        row = a.find('rows', [line['row_key']])
        require(row is not None, 'line -> row FK fails')
        for key, value in line.items():
            if key in ('record_json', 'public_record_locator', 'source_locator_scope'):
                continue
            require(value == row.get(key), 'line/row round-trip differs: ' + key)
        current = a.find('labels_current', [line['row_key']])
        require(current is not None, 'line -> current label FK fails')
        historical = a.find('label_versions', [current['label_version_id']])
        require(historical is not None and {k: v for k, v in historical.items() if k != 'public_record_locator'} == {k: v for k, v in current.items() if k != 'public_record_locator'}, 'current -> label version differs')
        if not a.manifest.get('incumbent_generation'):
            require(current['text'] == row.get('text'), 'current label round-trip differs')
        feature = a.find('current_features', [line['row_key']])
        if current['text'] is not None:
            require(feature is not None and feature['label_version_id'] == current['label_version_id'], 'current feature version differs')
            require(feature['label_sha256'] == current['text_sha256'], 'current feature hash differs')
        line.update(text=row.get('text'), label_sha256=row.get('label_sha256'))
        if feature:
            line.update({k: v for k, v in feature.items() if k not in ('row_key', 'label_variant', 'label_version_id', 'public_record_locator', 'source_locator_scope')})
        original = a.db.execute('SELECT b FROM images WHERE h=?', (line.get('crop_sha256'),)).fetchone()
        if row.get('original_crop_custody', {}).get('hash_match'):
            require(original is not None, 'verified original crop missing from images')
            line['image_measured_sha256'] = digest(original[0])
        variants = {}
        for j, in a.db.execute("SELECT j FROM r WHERE t='training_membership' AND json_extract(j,'$.row_key')=?", (line['row_key'],)):
            m = json.loads(j)
            if m.get('membership_kind') == 'reference_image':
                continue
            key = (m['pool'], m['trainer_line_id'], m['variant'])
            variants[key] = {k: m.get(k) for k in ('pool', 'trainer_line_id', 'variant', 'image_sha256', 'gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')}
            native = a.db.execute('SELECT j,b FROM frozen WHERE pool=? AND shard=? AND ordinal=?', (m['pool'], m['source_shard'], m['source_ordinal'])).fetchone()
            if a.frozen_available:
                require(native is not None, 'frozen occurrence missing for trainer membership')
                require(digest(native[1]) == m['image_sha256'], 'frozen trainer bytes differ')
                fields = json.loads(native[0])
                require(fields.get('trainer_line_id', fields.get('line_id')) == m['trainer_line_id'], 'frozen trainer occurrence ID differs')
                require(fields.get('pool', m['pool']) == m['pool'], 'frozen trainer pool differs')
                require(all(fields.get(k) == m.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')), 'frozen trainer label/codec differs')
                line['trainer_image_measured_sha256'] = m['image_sha256']
        line['trainer_variants'] = list(variants.values())
        for key in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version', 'raw_text', 'raw_text_sha256'):
            line[key] = row.get(key)
        a.db.execute('INSERT INTO r VALUES(?,?,?)', ('real', canonical([line['row_key']]), canonical(line)))
        count += 1
    count = a.db.execute("SELECT COUNT(*) FROM r WHERE t='real'").fetchone()[0]
    require(count == sum(1 for _, r in a.items('rows') if r.get('release')), 'line round-trip cardinality differs')
    if a.frozen_available:
        missing = a.db.execute("SELECT frozen.pool,frozen.shard,frozen.ordinal FROM frozen LEFT JOIN r ON r.t='training_membership' AND json_extract(r.j,'$.pool')=frozen.pool AND json_extract(r.j,'$.source_shard')=frozen.shard AND json_extract(r.j,'$.source_ordinal')=frozen.ordinal WHERE r.k IS NULL LIMIT 1").fetchone()
        require(missing is None, 'extra frozen occurrence without trainer membership')
        for j, in a.db.execute("SELECT j FROM r WHERE t='training_membership' AND json_extract(j,'$.synthetic_match_group') IS NOT NULL"):
            member = json.loads(j)
            native = a.db.execute('SELECT j,b FROM frozen WHERE pool=? AND shard=? AND ordinal=?', (member['pool'], member['source_shard'], member['source_ordinal'])).fetchone()
            require(native is not None, 'synthetic frozen occurrence missing')
            fields = json.loads(native[0])
            require(fields.get('trainer_line_id', fields.get('line_id')) == member['trainer_line_id'], 'synthetic frozen occurrence ID differs')
            require(digest(native[1]) == member['image_sha256'], 'synthetic frozen image differs')
            require(all(fields.get(k) == member.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')), 'synthetic frozen label/codec differs')

    a.roundtrip_rows = count
    for name, expected in a.manifest['logical_key_sha256'].items():
        h = hashlib.sha256()
        n = 0
        for key, _ in a.items(name):
            h.update((key + '\n').encode())
            n += 1
        require(h.hexdigest() == expected and n == a.manifest['counts'][name], 'relation logical key digest/count differs: ' + name)
    try:
        import datasets
    except ImportError:
        a.loader = 'pyarrow: every config/shard reopened; datasets unavailable (A5 pending)'
    else:
        from .accept_dataset import itertools_first
        for name, splits in configs.items():
            from .frozen_identity import public_file
            frozen = a.manifest.get('frozen_trained', {})
            frozen_paths = {f['path'] for f in frozen.get('files', [])}
            snapshot = frozen.get('public_snapshot_root') if a.validation_mode == 'external-cache' else None
            ds = datasets.load_dataset('parquet', data_files={s: [str(public_file(snapshot, p)
                if snapshot and p in frozen_paths else a.root / p) for p in paths]
                for s, paths in splits.items()}, streaming=True)
            for split in ds:
                list(itertools_first(ds[split]))
        a.loader = 'datasets: each config/split opened offline, all shards separately read with pyarrow'
