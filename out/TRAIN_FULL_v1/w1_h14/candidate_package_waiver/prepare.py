"""Compute-node preparation: reuse byte-exact S1 shards; frozen factory for harvest.

Only the owner invokes this on Clariden. No download/build/submit fallback.
"""
import argparse
from collections import Counter
from pathlib import Path
import subprocess
import sys
import unicodedata

from common import atomic, bound, digest, read, rows, sha, spec, write_rows
from horizon import resolve, verify_full_pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))


def nonletter_label(text):
    """No script under the frozen factory/S1 tagger's exact character ranges.

    S1 export.py -> e4_wave2.encode_admissions uses tag(text) or 'furniture'.
    Leave script-bearing records to the unchanged native classifier. This is
    independent of primary_class: numerics_tables may also contain letters.
    """
    return not any(('A' <= c <= 'Z' or 'a' <= c <= 'z'
                    or 0xc0 <= ord(c) <= 0x24f or 0x370 <= ord(c) <= 0x4ff
                    or 0x1f00 <= ord(c) <= 0x1fff)
                   for c in unicodedata.normalize('NFD', text))


def harvest_record(row):
    record = dict(id='harvest:' + row['wave'] + ':' + row['id'], text=row['text'],
        doc=row['edition_id'], crop_path=row['crop_path'], source_dataset=row['source'],
        split='train' if row['split'] == 'train' else 'reserved', admitted=True)
    if nonletter_label(row['text']):
        record['script_class'] = 'furniture'
    return record


def factory_coverage(info, feed):
    # Appearance/length and their aggregate audit_ok are explicitly report-only
    # for real imports. Admission/custody/coverage remain mandatory, as in S1.
    if info['records_sha256'] != sha(feed) or info.get('drop_ledger'):
        raise ValueError('factory dropped/changed admitted release rows; inspect, never silently filter')


def parquet_rows(directory, hashes, split):
    import pyarrow.parquet as pq
    directory = Path(directory)
    actual = {str(p.relative_to(directory)): sha(p) for p in directory.rglob('shard-*.parquet')}
    if actual != hashes:
        raise ValueError('changed shard inventory: ' + str(directory))
    result = []
    for name in sorted(hashes):
        if Path(name).parts[0] == split:
            result.extend(pq.read_table(directory / name).to_pylist())
    if not result:
        raise ValueError('empty pool: ' + str(directory) + '/' + split)
    if any(r['split'] != split or r['codec_version'] != 'v2.1' for r in result):
        raise ValueError('shard split/codec mismatch')
    return result


def asset_path(path, mappings):
    path = Path(path)
    matches = [(Path(a), Path(b)) for a, b in mappings.items() if path.is_relative_to(a)]
    if len(matches) > 1:
        raise ValueError('ambiguous S1 asset relocation')
    if matches:
        a, b = matches[0]
        path = b / path.relative_to(a)
    return str(path)


def mix_rows(mix_spec, split, mappings):
    mix = read(bound(mix_spec))
    if mix['codec_version'] != 'v2.1' or any(c['kind'] != 'real' for c in mix['components']):
        raise ValueError('expected real v2.1 evaluation mix')
    return [r for c in mix['components'] for r in
            parquet_rows(asset_path(c['shard_dir'], mappings), c['shard_sha256'], split)]


def write_pool(path, data):
    import pyarrow as pa
    import pyarrow.parquet as pq
    path = Path(path)
    if not data:
        raise ValueError('empty required pool: ' + str(path))
    path.mkdir(parents=True)
    files = []
    for start in range(0, len(data), 4096):
        file = path / ('part-%06d.parquet' % start)
        pq.write_table(pa.Table.from_pylist(data[start:start + 4096]), file)
        files.append(spec(file))
    return dict(rows=len(data), files=files)


def prepare(config, manifest, out, *, factory_runner=subprocess.run, fixture=False):
    from train.cer import load_codec
    cfg = read(config)
    mappings = cfg.get('s1_asset_relocations', {})
    out = Path(out)
    if out.exists():
        raise ValueError('immutable preparation exists; use a fresh attempt')
    manifest = Path(manifest)
    receipt = read(manifest / 'MANIFEST.json')
    for value in receipt['files'].values():
        bound(value)
    if receipt['fixture'] and not fixture:
        raise ValueError('fixture manifest cannot prepare production')
    if not fixture and receipt.get('package_sha256') != sha(ROOT / 'PAYLOAD.json'):
        raise ValueError('manifest belongs to another package; re-audit this population')
    data = list(rows(bound(receipt['files']['rows.jsonl'])))
    # Check every model-input identity before creating any outputs.
    shared_info = read(bound(cfg['s1_build_info']))
    shared_mix = read(bound(cfg['s1_shared_mix']))
    c = shared_mix['components'][0]
    if c['shard_sha256'] != shared_info['shard_sha256']:
        raise ValueError('S1 shared shard binding mismatch')
    original = {r['line_id']: r for r in parquet_rows(asset_path(c['shard_dir'], mappings), c['shard_sha256'], 'train')}
    codec = load_codec(str(ROOT / 'vendor/codec/v2.1.json'))
    v4 = []
    v4_meta = {r['id']: r for r in data if r['release'] == 'v4'}
    if not set(v4_meta) <= set(original):
        raise ValueError('S1 stored rows missing')
    # S1 selected from physical shard order, not SCALE1 manifest order.
    for ident, r in original.items():
        if ident not in v4_meta:
            continue
        row = v4_meta[ident]
        if (r['source_doc_id'] != row['edition_id'] or r['source_dataset'] != row['source']
                or codec.decode(r['label_ids']) != unicodedata.normalize('NFD', row['text'])):
            raise ValueError('S1 stored-label/source join mismatch: ' + row['id'])
        v4.append(r)
    node = read(bound(cfg['s1_node']))
    selection = node['arms'][0]['parameters']['val_mix']
    validation = mix_rows(dict(path=asset_path(selection, mappings), sha256=node['inputs'][selection]), 'val', mappings)
    panels = {}
    for split in ('dev', 'test'):
        path = node['instruments']['benchmark_v02_' + split]
        panel = mix_rows(dict(path=asset_path(path, mappings), sha256=node['inputs'][path]), 'reserved', mappings)
        expected = {r['id'] for r in data if r['release'] == 'seal04' and r['split'] == split}
        if len(panel) != len(expected) or {r['line_id'] for r in panel} != expected:
            raise ValueError('seal04 prepared membership mismatch')
        panels['seal04_' + split] = panel
    synthetic_root = Path(cfg['synthetic']['path'])
    syn_info = read(synthetic_root / 'build_info.json')
    if sha(synthetic_root / 'build_info.json') != cfg['synthetic']['build_info_sha256']:
        raise ValueError('S1 synthetic build changed')
    synthetic = parquet_rows(synthetic_root, syn_info['shard_sha256'], 'train')
    factory = bound(cfg['factory'])
    out.mkdir(parents=True)
    feed = []
    admitted = {}
    for row in data:
        if row['release'] != 'harvest':
            continue
        uid = 'harvest:' + row['wave'] + ':' + row['id']
        if uid in admitted:
            raise ValueError('harvest duplicate namespaced line')
        admitted[uid] = row
        if sha(row['crop_path']) != row['crop_sha256']:
            raise ValueError('harvest changed after manifest')
        feed.append(harvest_record(row))
    write_rows(out / 'import.jsonl', feed)
    factory_runner([str(factory), 'import-real', '--records', str(out / 'import.jsonl'),
        '--crops', '/', '--partition', 'TRAIN_FULL_v1', '--codec-json', str(ROOT / 'vendor/codec/v2.1.json'),
        '--out', str(out / 'factory')], check=True)
    info = read(out / 'factory/build_info.json')
    factory_coverage(info, out / 'import.jsonl')
    harvested = []
    for split in ('train', 'reserved'):
        harvested.extend(parquet_rows(out / 'factory', info['shard_sha256'], split))
    if len(harvested) != len(feed) or {r['line_id'] for r in harvested} != set(admitted):
        raise ValueError('factory exact coverage mismatch')
    for r in harvested:
        source = admitted[r['line_id']]
        if nonletter_label(source['text']) and r['script_class'] != 'furniture':
            raise ValueError('nonletter S1 class mismatch: ' + r['line_id'])
    real = list(v4)
    for split in ('dev', 'test'):
        panels['harvest_' + split] = [r for r in harvested if admitted[r['line_id']]['split'] == split]
    real.extend(r for r in harvested if admitted[r['line_id']]['split'] == 'train')
    # Preserve S1's real-source share rule: parliament at most 1/4 of real draws.
    parl = [r for r in real if r['source_dataset'] == 'parliament_proceedings_1975_2000']
    non = [r for r in real if r['source_dataset'] != 'parliament_proceedings_1975_2000']
    share = min(len(parl) / len(real), .25)
    groups = [('non_parliament', non, .5 * (1 - share), 'real')]
    if parl:
        groups.append(('parliament', parl, .5 * share, 'real'))
    groups.append(('synthetic', synthetic, .5, 'synthetic'))
    pools = {name: write_pool(out / name, rr) for name, rr, _, _ in groups}
    pools['validation'] = write_pool(out / 'validation', validation)
    pools.update({name: write_pool(out / name, rr) for name, rr in panels.items()})
    references = {}
    for split in ('dev', 'test'):
        references['seal04_' + split] = {r['id']: r['text'] for r in data
            if r['release'] == 'seal04' and r['split'] == split}
        references['harvest_' + split] = {'harvest:' + r['wave'] + ':' + r['id']: r['text'] for r in data
            if r['release'] == 'harvest' and r['split'] == split}
    runtime = dict(schema='TRAIN_FULL-runtime-v1', mock=bool(fixture), manifest=spec(manifest / 'MANIFEST.json'),
        package_sha256=sha(ROOT / 'PAYLOAD.json') if (ROOT / 'PAYLOAD.json').exists() else None,
        config=spec(config), pools=pools, references=references,
        components=[dict(name=name, kind=kind, fraction=fraction, recipe_sha256=syn_info['recipe_sha256']
                        if kind == 'synthetic' else None) for name, _, fraction, kind in groups],
        seed=20261015, codec_version='v2.1', factory=cfg['factory'],
        synthetic=cfg['synthetic'], train_rows=len(real),
        train_source_counts=dict(Counter(r['source_dataset'] for r in real)))
    runtime['import_diagnostics'] = dict(
        nonletter_class='furniture',
        s1_nonletter_classes=dict(Counter(r['script_class'] for r in v4
            if nonletter_label(codec.decode(r['label_ids'])))),
        harvest_nonletter_by_split=dict(Counter(r['split'] for r in admitted.values()
            if nonletter_label(r['text']))),
        factory_build_info=spec(out / 'factory/build_info.json'),
        audit_ok=info.get('audit_ok'), audit_policy='report_only')
    if len(real) != receipt['train_unique']:
        raise ValueError('prepared real population differs from audited unique TRAIN count')
    runtime['horizon_recipe'] = cfg.get('horizon_recipe', 'full')
    runtime['horizon'] = resolve(read(ROOT / 'recipe.json'), len(real), runtime['horizon_recipe'])
    if runtime['horizon_recipe'] != 's1-literal':
        runtime['full_pass_check'] = verify_full_pass(runtime['components'],
            {name: pool['rows'] for name, pool in pools.items()}, len(real))
    # Save only summaries locally; full runtime/crops/shards remain on Clariden.
    atomic(out / 'runtime.json', runtime)
    return runtime


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    prepare(a.config, a.manifest, a.out)
