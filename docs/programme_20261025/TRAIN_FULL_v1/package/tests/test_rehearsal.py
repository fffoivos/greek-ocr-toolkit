"""Mocked complete release -> manifest -> factory adapter -> training rehearsal."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image
import pyarrow as pa
import pyarrow.parquet as pq

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, read, rows, sha, spec, write_rows
from manifest import build
from prepare import prepare
from chain import dependency
from test_package import book, spawn


def test_prepare_requeue_preserves_partial_and_reuses_only_same_binding(tmp_path):
    from prepare_job import existing_or_preserve
    import pytest
    folder = tmp_path / 'manifest'
    folder.mkdir()
    (folder / 'partial').write_bytes(b'keep evidence')
    config = tmp_path / 'config.json'
    atomic(config, dict(input='original'))
    assert not existing_or_preserve(folder, 'MANIFEST.json', config)
    assert not folder.exists()
    saved = list(tmp_path.glob('manifest.interrupted-*'))
    assert len(saved) == 1 and (saved[0] / 'partial').read_bytes() == b'keep evidence'
    folder.mkdir()
    atomic(folder / 'MANIFEST.json', dict(config=spec(config), package_sha256=sha(PKG / 'PAYLOAD.json')))
    assert existing_or_preserve(folder, 'MANIFEST.json', config)
    atomic(config, dict(input='changed'))
    with pytest.raises(ValueError, match='another data config'):
        existing_or_preserve(folder, 'MANIFEST.json', config)


def test_purged_completed_dependency_and_failed_parent():
    assert dependency('123', '123|COMPLETED|0:0|250\n') is None
    assert dependency('123', '123|RUNNING|0:0|250\n') == 'afterok:123'
    import pytest
    for text in ('', '123|FAILED|1:0|20\n', '123|COMPLETED|1:0|20\n'):
        with pytest.raises(ValueError):
            dependency('123', text)


def test_scheduler_mock_drycheck_exact_and_completed_dependency_omitted(tmp_path, monkeypatch):
    import argparse
    import chain
    import verify
    monkeypatch.setattr(verify, 'verify', lambda: None)
    root = tmp_path / 'pkg'
    root.mkdir()
    atomic(root / 'PAYLOAD.json', dict(files={}))
    (root / 'job.sbatch').write_text('# fixture')
    monkeypatch.setattr(chain, 'ROOT', root)
    output = tmp_path / 'output'
    output.mkdir()
    (output / 'segment.pt').write_bytes(b'checkpoint')
    atomic(output / 'SEGMENT_YIELD.json', dict(job_id='123', checkpoint=spec(output / 'segment.pt')))
    runtime = tmp_path / 'runtime.json'
    atomic(runtime, dict(mock=True))
    calls = []
    def mock_command(argv, **kwargs):
        calls.append(argv)
        if argv[0] == 'sacct':
            return subprocess.CompletedProcess(argv, 0, stdout='123|COMPLETED|0:0|12\n')
        return subprocess.CompletedProcess(argv, 0, stdout='' if '--test-only' in argv else '456;cluster\n')
    args = argparse.Namespace(out=str(output), controls=str(tmp_path / 'controls'), segment=2,
        mode='smoke-requeue', prior='123', runtime=str(runtime), review=None, owner_go=False)
    assert chain.submit(args, command=mock_command) == '456'
    dry, actual = calls[-2:]
    assert '--test-only' in dry
    assert [v for v in dry if v != '--test-only'] == actual
    assert not any(v.startswith('--dependency=') for v in actual)
    import pytest
    with pytest.raises(ValueError, match='existing submission'):
        chain.submit(args, command=mock_command)


def tiny_inputs(tmp):
    rng = np.random.default_rng(5)
    def crop(name):
        path = tmp / (name + '.png')
        Image.fromarray(rng.integers(0, 256, (48, 64), dtype=np.uint8)).save(path)
        return path
    def contract(ident, split, image):
        return dict(line_id=ident, width=64, image_png=image.read_bytes(), label_ids=[2, 3, 4],
            codec_version='v2.1', split=split, source_doc_id='ed-' + ident,
            source_dataset='source', script_class='latin', severity=0, polarity='dark', bg_type='flat', font='real')
    def shards(root, groups):
        hashes = {}
        for split, data in groups.items():
            file = root / split / 'shard-00000.parquet'
            file.parent.mkdir(parents=True)
            pq.write_table(pa.Table.from_pylist(data), file)
            hashes[str(file.relative_to(root))] = sha(file)
        return hashes
    def real_mix(name, split, data):
        root = tmp / name
        hashes = shards(root, {split: data})
        path = tmp / (name + '.json')
        atomic(path, dict(codec_version='v2.1', components=[dict(kind='real', shard_dir=str(root), shard_sha256=hashes)]))
        return spec(path)
    old_image = crop('old')
    old = contract('old', 'train', old_image)
    shared = real_mix('shared', 'train', [old])
    subset = tmp / 'subset.jsonl'
    write_rows(subset, [dict(row_id='old', label='ABC', source='source', primary_class='latin',
                            crop_path=str(old_image), crop_sha256=sha(old_image))])
    records = tmp / 'records.jsonl'
    write_rows(records, [dict(id='old', doc='ed-old')])
    info = tmp / 'info.json'
    atomic(info, dict(crop_sha256={'old': sha(old_image)}, shard_sha256=read(shared['path'])['components'][0]['shard_sha256']))
    suite_dir = tmp / 'seal'
    suite_dir.mkdir()
    panels, instrument_mix, inputs = {}, {}, {}
    authority = [book('book-old', 'train', 'ed-old')]
    for split in ('dev', 'test'):
        image = crop('seal-' + split)
        ident = 'seal-' + split
        authority.append(book('book-' + ident, split, 'ed-' + ident))
        panel_file = suite_dir / (split + '.jsonl')
        write_rows(panel_file, [dict(id=ident, text='ABC', doc='ed-' + ident, split=split,
            source='source', crop_path=str(image), crop_sha256=sha(image), **{'class': 'latin'})])
        panel = dict(path=panel_file.name, sha256=sha(panel_file), rows=1, scorable=True)
        name = 'benchmark_v02_' + split
        panels[name] = panel
        mix = real_mix(name, 'reserved', [contract(ident, 'reserved', image)])
        instrument_mix[name] = mix['path']
        inputs[mix['path']] = mix['sha256']
    suite = suite_dir / 'suite.json'
    atomic(suite, dict(panels=panels))
    validation_image = crop('validation')
    validation = real_mix('validation', 'val', [contract('validation', 'val', validation_image)])
    inputs[validation['path']] = validation['sha256']
    node = tmp / 'node.json'
    atomic(node, dict(arms=[dict(parameters=dict(val_mix=validation['path']))], inputs=inputs, instruments=instrument_mix))
    syn_root = tmp / 'synthetic'
    hashes = shards(syn_root, {'train': [contract('synthetic', 'train', crop('synthetic'))]})
    atomic(syn_root / 'build_info.json', dict(shard_sha256=hashes, recipe_sha256='fake-recipe'))
    release = tmp / 'release'
    release.mkdir()
    harvest, extension = [], []
    for split in ('train', 'dev', 'test'):
        ident = 'harvest-' + split
        image = crop(ident)
        dest = release / 'data' / split / 'W3' / (ident + '.png')
        dest.parent.mkdir(parents=True)
        dest.write_bytes(image.read_bytes())
        b = book('book-' + ident, split, 'ed-' + ident)
        extension.append(b)
        harvest.append(dict(id=ident, wave='W3', text='ABC', split=split, book_id=b['book_id'],
            edition_id='ed-' + ident, source='source', item=ident, primary_class='latin',
            file_name=str(dest.relative_to(release)), crop_sha256=sha(dest),
            label_sha256=hashlib.sha256(b'ABC').hexdigest()))
    write_rows(release / 'metadata.jsonl', harvest)
    for split in ('train', 'dev', 'test'):
        write_rows(release / 'data' / split / 'metadata.jsonl',
            (dict(r, file_name=str(Path(r['file_name']).relative_to(Path('data') / split)))
             for r in harvest if r['split'] == split))
    registry_path = release / 'registry/book_registry.jsonl.gz'
    registry_path.parent.mkdir()
    with gzip.open(registry_path, 'wt') as f:
        for r in extension:
            f.write(json.dumps(r) + '\n')
    atomic(release / 'RELEASE_RECEIPT.json', dict(included_waves=['W3'], rows=3,
            by_split=dict(train=1, dev=1, test=1), by_wave={'W3': 3}, by_source={'source': 3},
            registry=dict(exported_admitted_books_sha256=sha(registry_path))))
    atomic(release / 'TRANSFER.json', dict(release_receipt_sha256=sha(release / 'RELEASE_RECEIPT.json'),
        files={str(p.relative_to(release)): dict(sha256=sha(p)) for p in release.rglob('*') if p.is_file()}))
    authority_path = tmp / 'registry.jsonl'
    write_rows(authority_path, authority)
    factory = tmp / 'fake-linefactory'
    factory.write_bytes(b'fixture-native-adapter')
    cfg = dict(registry_v2=spec(authority_path), s1_subset=dict(spec(subset), rows=1),
        s1_records=spec(records), s1_build_info=spec(info), s1_shared_mix=shared, s1_node=spec(node),
        seal_suite=spec(suite), harvest_root=str(release), harvest_receipt=spec(release / 'RELEASE_RECEIPT.json'),
        harvest_transfer=spec(release / 'TRANSFER.json'),
        required_waves=['W3'], relocations={}, factory=spec(factory),
        synthetic=dict(path=str(syn_root), build_info_sha256=sha(syn_root / 'build_info.json')))
    config = tmp / 'data.json'
    atomic(config, cfg)

    def fake_factory(argv, **kwargs):
        feed = list(rows(argv[argv.index('--records') + 1]))
        root = Path(argv[argv.index('--out') + 1])
        groups = {}
        for r in feed:
            target = contract(r['id'], r['split'], Path(r['crop_path']))
            target.update(source_doc_id=r['doc'], source_dataset=r['source_dataset'])
            groups.setdefault(r['split'], []).append(target)
        hashes = shards(root, groups)
        atomic(root / 'build_info.json', dict(records_sha256=sha(argv[argv.index('--records') + 1]),
            shard_sha256=hashes, drop_ledger=[], audit_ok=True))
    return config, fake_factory


def test_offline_complete_mock_rehearsal(tmp_path):
    config, fake_factory = tiny_inputs(tmp_path)
    from audit_job import execute
    report = execute(config, tmp_path / 'audit', fixture=True)
    assert report['train_unique'] == 2
    assert report['split_counts'] == {'train': 2, 'dev': 2, 'test': 2}
    rt = prepare(config, tmp_path / 'audit/manifest', tmp_path / 'prepared',
                 factory_runner=fake_factory, fixture=True)
    assert rt['mock'] is True and rt['train_rows'] == 2
    assert rt['horizon']['epoch_rows'] == 4 and rt['horizon']['total_updates'] == 8
    assert rt['full_pass_check']['component_draws']['non_parliament'] == 2
    audit = read(tmp_path / 'audit/manifest/AUDIT.json')
    assert audit['collisions'] == 0 and audit['status'] == 'PASS'
    assert audit['dataset_unique_by_split'] == dict(train=2, dev=1, test=1)
    assert sum(r['rows'] for r in audit['unique_population_table']) == audit['dataset_unique_crops'] == 4
    assert execute(config, tmp_path / 'audit', fixture=True)['train_unique'] == 2
    # Exercise the owner forecast with fixture counts explicitly relabelled only
    # inside this local test; no such receipts are exported as production evidence.
    from readout import readout
    report['fixture'] = False
    atomic(tmp_path / 'forecast-manifest.json', report)
    forecast_runtime = dict(rt, mock=False)
    atomic(tmp_path / 'forecast-runtime.json', forecast_runtime)
    forecast = readout(tmp_path / 'forecast-manifest.json', tmp_path / 'forecast-runtime.json', tmp_path / 'forecast.json')
    assert [f['choice'] for f in forecast['forecasts']] == ['full', 's1-literal', 'longer']
    assert forecast['forecasts'][0]['total_updates'] == 8
    assert forecast['forecasts'][1]['total_updates'] == 53616
    output = tmp_path / 'run'
    c = spawn(tmp_path / 'prepared/runtime.json', output)
    assert c.wait(timeout=40) == 0, (output / 'process.log').read_text()
    complete = read(output / 'COMPLETE.json')
    assert complete['binding']['evaluation_steps'] == [2, 4, 6, 8]
    atomic(tmp_path / 'REHEARSAL.json', dict(status='PASS', real_release_inputs=False,
        mocked=['native factory', 'model'], real=['CPU audit job entry/requeue reuse', 'release layout/hash verification', 'registry resolution',
            'cross-release dedupe/leakage', 'pool materialization', 'S1 training loop', 'optimizer',
            'scheduler', 'CTC backward', 'checkpoint evaluation with frozen scorer'],
        fixture_counts=report['split_counts'], final_updates=8, checkpoint_evaluations=4))
