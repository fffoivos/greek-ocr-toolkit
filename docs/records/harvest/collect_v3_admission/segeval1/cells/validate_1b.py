"""Independent readback of SEG-CELLS-1b sample bytes, census fields and scope."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image

D = Path(__file__).resolve().parent
ROOT = D.parents[4]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    initial = json.loads((D / 'initial_state_1b.json').read_text())
    receipt = json.loads((D / 'sample_receipt.json').read_text())
    samples = [json.loads(line) for line in (D / 'samples.jsonl').read_text().splitlines()]
    ids = {r['row_id'] for r in samples}
    assert len(ids) == len(samples) == len(list((D / 'samples').glob('*.png'))) == 250
    counts = Counter(r['group'] for r in samples)
    assert counts == receipt['targets'] == dict(cells=150, numeric_not_small=50, small_not_numeric=50)
    assert receipt['fetched'] == 250 and receipt['local_reconstructed_crops'] == 200
    assert receipt['retained_existing_scp_crops'] == 50
    assert receipt['page_fetches'] == receipt['replacement_log'] == receipt['remote_commands_1b'] == []
    assert receipt['pages_from_cache'] == 156
    assert receipt['pages_scp'] == receipt['replacements'] == receipt['remote_writes'] == 0
    assert sha(D / 'samples.jsonl') == receipt['samples_sha256']
    assert sha(D / 'sample_order.jsonl.gz') == initial['order_sha256'] == receipt['order_gzip_sha256']
    order_bytes = gzip.decompress((D / 'sample_order.jsonl.gz').read_bytes())
    assert hashlib.sha256(order_bytes).hexdigest() == receipt['order_sha256']
    orders = {r['group']: r['row_ids'] for r in map(json.loads, order_bytes.splitlines())}
    for group, count in [('cells', 150), ('numeric_not_small', 50)]:
        assert [r['row_id'] for r in samples if r['group'] == group] == orders[group][:count]

    manifest_path = str((D / 'samples.jsonl').relative_to(ROOT))
    original_bytes = git('show', initial['seg_cells_head'] + ':' + manifest_path)
    assert hashlib.sha256(original_bytes).hexdigest() == initial['initial_samples_sha256']
    original = [json.loads(line) for line in original_bytes.splitlines()]
    retained = [r for r in samples if r['group'] == 'small_not_numeric']
    assert [r['row_id'] for r in retained] == [r['row_id'] for r in original]
    assert [r['sha256'] for r in retained] == [r['sha256'] for r in original]

    export = json.loads((D / 'export_receipt.json').read_text())
    assert sha(D / 'population_cells.jsonl.gz') == receipt['population_sha256'] == export['reduced_sha256']
    census = {}
    for line in gzip.open(D / 'population_cells.jsonl.gz', 'rt'):
        row = json.loads(line)
        if row['row_id'] in ids:
            assert row['row_id'] not in census
            census[row['row_id']] = row
    assert len(census) == 250
    provenance = {r['row_id']: r for r in receipt['samples']}
    assert len(provenance) == len(receipt['samples']) == 250
    bindings = json.loads((D / 'selected_metadata_1b.json').read_text())
    assert bindings['inputs'] == receipt['metadata_inputs']
    assert len(bindings['rows']) == 200
    for r in samples:
        c = census[r['row_id']]
        p = Path(r['crop_path'])
        assert p.is_absolute() and p.parent == (D / 'samples').resolve()
        assert p.name == r['row_id'] + '.png'
        assert sha(p) == r['sha256'] == r['crop_sha256'] == c['crop_sha256']
        with Image.open(p) as im:
            assert im.format == 'PNG'
            assert im.size == (r['width'], r['height']) == (r['w'], r['h']) == (c['width_px'], c['height_px'])
            im.verify()
        fields = {'chars': 'characters', 'text': 'raw_text', 'source': 'source', 'class': 'primary_class',
                  'primary_class': 'primary_class', 'script_class': 'script_class', 'parent_id': 'parent_id',
                  'verdict_05': 'verdict_05', 'reason_05': 'reason_05', 'reason': 'reason_05',
                  'pipeline_disposition': 'pipeline_disposition'}
        assert all(r[a] == c[b] for a, b in fields.items()), r['row_id']
        assert r['group'] == r['sample_group']
        if r['group'] == 'cells':
            assert c['is_cell']
        elif r['group'] == 'numeric_not_small':
            assert c['is_numeric_output'] and not c['is_small_image']
        else:
            assert c['is_small_image'] and not c['is_numeric_output']
        provenance_row = provenance[r['row_id']]
        assert provenance_row['crop_path'] == str(p) and provenance_row['crop_sha256'] == c['crop_sha256']
        assert provenance_row['replacement'] is False
        assert provenance_row['seeded_rank'] == orders[r['group']].index(r['row_id']) + 1
        if r['group'] != 'small_not_numeric':
            assert provenance_row['method'] == 'local_cache'
            binding = bindings['rows'][r['row_id']]
            assert binding['crop_bbox'] == provenance_row['crop_bbox']
            assert binding['crop_color_mode'] == provenance_row['crop_color_mode']
            assert binding['crop_source_sha256'] == provenance_row['page_sha256']
            assert binding['crop_sha256'] == c['crop_sha256']
        else:
            assert provenance_row['method'] == 'retained_existing_scp_crop'
    assert len(receipt['pages']) == len({p['sha256'] for p in receipt['pages']}) == 156
    assert {r['page_sha256'] for r in receipt['samples'] if r['method'] == 'local_cache'} == {p['sha256'] for p in receipt['pages']}
    for page in receipt['pages']:
        assert page['obtained'] == 'local_cache' and sha(page['path']) == page['sha256']
    review = json.loads((D / 'visual_review_1b.json').read_text())
    assert review['status'] == 'REVIEWED_WITH_IMAGE_TOOL'
    assert len(review['samples']) == len({r['row_id'] for r in review['samples']}) == 40
    for r in review['samples']:
        assert r['reviewed'] and r['observation']
        assert samples[r['cell_index'] - 1]['row_id'] == r['row_id']
        assert sha(r['crop_path']) == r['sha256']

    for name, expected in initial['protected'].items():
        assert sha(ROOT / name) == expected, name
    native = 'greekocr/harvest/line_pipeline_native.py'
    assert sha(ROOT / native) == initial['native_sha256'] == receipt['native_sha256']
    assert (ROOT / native).read_bytes() == git('show', initial['seg_cells_head'] + ':' + native)
    assert git('rev-parse', 'HEAD').decode().strip() == initial['head']
    assert git('for-each-ref', '--format=%(refname) %(objectname)').decode() == initial['refs']
    index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    assert sha(index) == initial['index_sha256']
    assert hashlib.sha256(git('diff', '--binary')).hexdigest() == initial['diff_sha256']
    result = dict(status='PASS', samples_byte_exact_to_census=250,
                  png_dimensions_and_required_fields_verified=250, groups=dict(counts),
                  numeric_seeded_prefixes_preserved=True, original_50_small_non_numeric_retained=True,
                  crop_reconstruction_count_1b=200, source_pages_from_cache_verified=156,
                  source_pages_scp=0, replacements=0, samples_reviewed_with_image_tool=40,
                  unchanged_native_reconstruction_function=True, protected_five_files_unchanged=True,
                  shared_head_refs_index_and_existing_diff_unchanged=True, remote_commands_1b=0,
                  pipeline_policy_or_verdict_changes=0)
    (D / 'validation_1b.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
