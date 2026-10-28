import gzip
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from scripts.release_v0_dataset import probe_sources as source
from scripts.release_v0_dataset import probe_synthetic as synthetic


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = ''.join(json.dumps(row) + '\n' for row in rows)
    if path.suffix == '.gz':
        with gzip.open(path, 'wt') as stream:
            stream.write(text)
    else:
        path.write_text(text)


def read(path):
    return json.loads(path.read_text())


def test_inventory_and_keyed_differences_without_image_projection(tmp_path, monkeypatch):
    prep, harvest = tmp_path / 'prep', tmp_path / 'harvest'
    prep.mkdir()
    harvest.mkdir()
    pq.write_table(pa.Table.from_pylist([
        {'line_id': 'harvest:W3:a', 'image_png': b'NEVER EMIT THESE IMAGE BYTES', 'split': 'train'},
        {'line_id': 'harvest:W3:b', 'image_png': b'bad png', 'split': 'train'},
    ]), prep / 'part.parquet')
    jsonl(harvest / 'metadata.jsonl.gz', [
        {'wave': 'W3', 'id': 'a', 'split': 'train'},
        {'wave': 'W4', 'id': 'c', 'split': 'train'},
        {'wave': 'W4', 'id': 'c', 'split': 'train'},
    ])
    original = source.parquet_info
    def projected(path):
        pf, schema = original(path)
        class MetadataOnly:
            metadata = pf.metadata
            def iter_batches(self, **kwargs):
                assert 'image_png' not in kwargs['columns']
                yield from pf.iter_batches(**kwargs)
        return MetadataOnly(), schema
    monkeypatch.setattr(source, 'parquet_info', projected)
    before = {p: source.sha(p) for p in [prep / 'part.parquet', harvest / 'metadata.jsonl.gz']}
    out = tmp_path / 'out'
    assert source.main(['--source', f'prep={prep}', '--source', f'harvest={harvest}',
        '--output-dir', str(out), '--full', '--compare',
        'train=prep|*.parquet|harvest_wave_id|harvest|metadata*|harvest_wave_id']) == 0
    report = read(out / 'prep.inventory.json')
    assert report['files'] == 1
    assert report['bytes'] == (prep / 'part.parquet').stat().st_size
    assert report['tables'][0]['schema']['image_png'] == 'binary'
    assert report['tables'][0]['row_count'] == 2
    comparison = read(out / 'PROBE_RECEIPT.json')['comparisons'][0]
    assert comparison['status'] == 'complete_key_scan'
    assert comparison['intersection'] == 1
    assert comparison['lhs_only']['keys'] == 1
    assert comparison['rhs_only']['keys'] == 1
    assert comparison['rhs']['duplicate_keys'] == 1
    assert 'NEVER EMIT' not in ''.join(p.read_text() for p in out.glob('*.json'))
    assert all(source.sha(p) == value for p, value in before.items())


def test_sample_is_not_a_complete_join(tmp_path):
    root = tmp_path / 'src'
    jsonl(root / 'rows.jsonl', [{'id': str(i)} for i in range(3)])
    out = tmp_path / 'out'
    assert source.main(['--source', f's={root}', '--output-dir', str(out), '--max-rows', '1',
        '--compare', 'self=s|*|id|s|*|id']) == 0
    table = read(out / 's.inventory.json')['tables'][0]
    assert table['rows_scanned'] == 1 and not table['complete'] and table['row_count'] is None
    assert read(out / 'PROBE_RECEIPT.json')['comparisons'][0]['status'].startswith('INCOMPLETE')


def test_json_arrays_maps_parent_namespace_and_nulls(tmp_path):
    root = tmp_path / 'src'
    root.mkdir()
    (root / 'metadata.json').write_text(json.dumps({'rows': [
        {'parent_id': 'A', 'row_id': 'x'}, {'parent_id': 'B', 'row_id': 'x'},
        {'parent_id': None, 'row_id': 'x'}]}))
    (root / 'build_info.json').write_text(json.dumps({'crop_sha256': {'x': 'a' * 64}}))
    out = tmp_path / 'out'
    assert source.main(['--source', f's={root}', '--output-dir', str(out), '--full',
        '--json-array', 's|metadata.json|rows.item', '--json-map', 's|build_info.json|crop_sha256',
        '--compare', 'parents=s|metadata.json|parent_row|s|metadata.json|parent_row']) == 0
    tables = {t['path']: t for t in read(out / 's.inventory.json')['tables']}
    assert tables['metadata.json']['row_count'] == 3
    assert tables['build_info.json']['sample_keys'] == [{'_map_key': 'x'}]
    assert read(out / 'PROBE_RECEIPT.json')['comparisons'][0]['lhs']['distinct'] == 2


def test_missing_selector_side_is_incomplete(tmp_path):
    root = tmp_path / 'src'
    jsonl(root / 'rows.jsonl', [{'id': 'a'}])
    out = tmp_path / 'out'
    source.main(['--source', f's={root}', '--output-dir', str(out), '--full',
                 '--compare', 'missing=s|rows*|id|s|absent*|id'])
    assert read(out / 'PROBE_RECEIPT.json')['comparisons'][0]['status'].startswith('INCOMPLETE')


def test_missing_corrupt_and_symlink_inputs_are_explicit(tmp_path):
    root = tmp_path / 'src'
    root.mkdir()
    (root / 'bad.jsonl').write_text('{bad\n')
    outside = tmp_path / 'private.json'
    outside.write_text('{"id":"do-not-read"}')
    (root / 'link.json').symlink_to(outside)
    out = tmp_path / 'out'
    assert source.main(['--source', f's={root}', '--source', f'missing={tmp_path / "absent"}',
                        '--output-dir', str(out)]) == 2
    assert read(out / 's.inventory.json')['symlinks_skipped'] == 1
    assert read(out / 's.inventory.json')['errors']
    assert not read(out / 'missing.inventory.json')['exists']


@pytest.mark.parametrize('output_is_parent', [False, True])
def test_output_never_overlaps_inputs(tmp_path, output_is_parent):
    root = tmp_path / 'src'
    root.mkdir()
    output = tmp_path if output_is_parent else root / 'out'
    with pytest.raises(ValueError, match='overlap'):
        source.prepare_output(output, [root])


def test_credentials_refused_without_disclosure(monkeypatch):
    monkeypatch.setenv('HF_TOKEN', 'DO_NOT_DISCLOSE')
    with pytest.raises(ValueError) as exc:
        source.offline()
    assert 'DO_NOT_DISCLOSE' not in str(exc.value)


def test_large_json_requires_explicit_selector(tmp_path):
    path = tmp_path / 'large.json'
    with path.open('wb') as stream:
        stream.truncate(32_000_001)
    with pytest.raises(RuntimeError, match='explicit'):
        next(source.json_records(path))


def test_footer_only_table_does_not_claim_key_scan(tmp_path):
    root = tmp_path / 'src'
    root.mkdir()
    pq.write_table(pa.table({'unrelated_field': [1, 2]}), root / 'part.parquet')
    out = tmp_path / 'out'
    source.main(['--source', f's={root}', '--output-dir', str(out), '--full'])
    table = read(out / 's.inventory.json')['tables'][0]
    assert table['row_count'] == 2 and table['rows_scanned'] == 0 and not table['complete']


@pytest.fixture
def synth_build(tmp_path):
    root = tmp_path / 'synthetic'
    root.mkdir()
    rows = [dict(image_png=b'not an image', width=50, gt_nfc='ἄλφα', gt_nfd='ἄλφα',
        line_id='line-a', reuse_index=0, split='train', severity=2, applied_ops=['ink_bleed', 'crop:tight:a1.0'],
        font='Font-A', polarity='dark', bg_type='flat', accent_survival=1.0,
        source_dataset='corpus', source_doc_id='doc-1', label_ids=[1], codec_version='v2.1', script_class='greek')]
    pq.write_table(pa.Table.from_pylist(rows), root / 'part.parquet')
    (root / 'build_info.json').write_text(json.dumps({'recipe_sha256': '1' * 64,
        'recipe_effective_sha256': '2' * 64, 'fonts': [{'stem': 'Font-A', 'sha16': '3' * 16}],
        'recipe': {'seed': 7, 'severity_weights': [1, 1, 1, 1]}}))
    return root


def test_synthetic_full_field_coverage_and_no_sha_promotion(tmp_path, synth_build):
    src = Path(__file__).resolve().parents[2] / 'greekocr/_vendor/factory/src'
    out = tmp_path / 'out'
    assert synthetic.main(['--build', f'a12={synth_build}', '--factory-src', str(src), '--output-dir', str(out)]) == 0
    report = read(out / 'a12.synthetic.json')
    fields = report['field_presence']
    assert set(synthetic.FIELDS) <= set(fields)
    assert report['rows_per_split'] == {'train': 1}
    assert fields['image']['status'] == fields['text']['status'] == 'row_column'
    assert fields['font_sha16']['status'] == 'build_evidence_only'
    assert fields['font_file_sha256']['status'] == 'absent_in_searched_evidence'
    assert fields['seed']['status'] == 'build_evidence_only'
    assert fields['line_seed']['status'] == 'absent_in_searched_evidence'
    assert fields['recipe_sha256']['build_evidence'][0]['value'] != fields['recipe_effective_sha256']['build_evidence'][0]['value']
    ops = {r['name']: r for r in report['operations']['train']}
    assert ops['ink_bleed']['occurrences'] == 1
    assert ops['ink_bleed']['implementation']['function'] == 'ink_ops'
    assert ops['crop:tight:a1.0']['implementation']['function'] == 'detector_crop'
    assert 'not an image' not in (out / 'a12.synthetic.json').read_text()


def test_synthetic_multiple_splits_and_unmapped_op(tmp_path, synth_build):
    table = pq.read_table(synth_build / 'part.parquet')
    row = table.to_pylist()[0]
    row.update(split='reserved', applied_ops=['new_historical_op'])
    pq.write_table(pa.Table.from_pylist([row]), synth_build / 'other.parquet')
    out = tmp_path / 'out'
    out.mkdir()
    report = synthetic.inspect_build('s', synth_build, out, {'map': {}})
    assert report['rows_per_split'] == {'train': 1, 'reserved': 1}
    assert report['operations']['reserved'][0]['mapping_status'] == 'UNMAPPED'


def test_full_font_sha_in_explicit_manifest_is_distinct_from_sha16(tmp_path, synth_build):
    manifest = tmp_path / 'font_manifest.json'
    manifest.write_text(json.dumps({'fonts': [{'stem': 'Font-A', 'sha256': 'f' * 64}]}))
    out = tmp_path / 'out'
    out.mkdir()
    report = synthetic.inspect_build('s', synth_build, out, {'map': {}}, evidence=[manifest])
    assert report['field_presence']['font_file_sha256']['status'] == 'build_evidence_only'
    assert report['font_hash_evidence']['full_sha'][0]['value'] == 'f' * 64
    assert report['font_hash_evidence']['sha16'][0]['value'] == '3' * 16


def test_synthetic_sample_never_claims_complete_counts(tmp_path, synth_build):
    row = pq.read_table(synth_build / 'part.parquet').to_pylist()[0]
    pq.write_table(pa.Table.from_pylist([row, row]), synth_build / 'part.parquet')
    out = tmp_path / 'out'
    out.mkdir()
    report = synthetic.inspect_build('s', synth_build, out, {'map': {}}, sample_rows=1)
    assert report['rows_per_split'] is None
    assert report['sample_rows_per_split'] == {'train': 1}
    assert not report['complete']
    assert report['field_presence']['line_seed']['status'] == 'not_observed_in_incomplete_search'
