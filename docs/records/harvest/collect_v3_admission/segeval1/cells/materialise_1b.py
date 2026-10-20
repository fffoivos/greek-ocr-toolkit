"""Materialise the authorised 200 missing samples locally, using the native contract.

No remote command, OCR, detector, policy change, or cache write. The original 50
small/non-numeric PNGs are retained. Missing pages stop this script for an explicit
single-page fetch and receipt rather than silently changing the seeded draw.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image

D = Path(__file__).resolve().parent
ROOT = D.parents[4]
sys.path.insert(0, str(ROOT))
from greekocr.harvest.line_pipeline_native import reconstructed_crop, digest_bytes


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    initial = json.loads((D / 'initial_state_1b.json').read_text())
    assert sha(ROOT / 'greekocr/harvest/line_pipeline_native.py') == initial['native_sha256']
    assert sha(D / 'sample_order.jsonl.gz') == initial['order_sha256']
    pending = [json.loads(line) for line in (D / 'pending_reconstruction.jsonl').read_text().splitlines()]
    orders = {r['group']: r['row_ids'] for r in map(json.loads, gzip.open(D / 'sample_order.jsonl.gz', 'rt'))}
    for group, count in [('cells', 150), ('numeric_not_small', 50)]:
        assert [r['row_id'] for r in pending if r['sample_group'] == group] == orders[group][:count]
    assert len(pending) == 200
    prior = [json.loads(line) for line in (D / 'samples.jsonl').read_text().splitlines()]
    assert len(prior) == 50 and all(r['sample_group'] == 'small_not_numeric' for r in prior)
    assert sha(D / 'samples.jsonl') == initial['initial_samples_sha256']
    wanted = {r['row_id'] for r in pending + prior}
    population = {}
    for line in gzip.open(D / 'population_cells.jsonl.gz', 'rt'):
        row = json.loads(line)
        if row['row_id'] in wanted:
            assert row['row_id'] not in population
            population[row['row_id']] = row
    assert len(population) == 250

    # W2 pages + resolved manifest contain page identity, not per-row crop boxes.
    # Use the already-local, frozen snapshots instead of any Clariden transfer.
    export = json.loads((D / 'export_receipt.json').read_text())
    metadata_inputs, bindings = [], {}
    id_pattern = re.compile(rb'"id"\s*:\s*"([^"\\]+)"')
    for wave in ('W1', 'W2'):
        expected = next(x for x in export['metadata_inputs'] if f'/{wave}_features_' in x['path'])
        path = Path(expected['path'])
        wave_ids = {r['row_id'] for r in pending if r['wave'] == wave}
        h, count, found = hashlib.sha256(), 0, 0
        with path.open('rb') as stream:
            for line in stream:
                h.update(line)
                count += 1
                match = id_pattern.search(line)
                if not match or match[1].decode() not in wave_ids:
                    continue
                row = json.loads(line)
                rid = row['id']
                assert rid not in bindings
                census = population[rid]
                prepared = next(r for r in pending if r['row_id'] == rid)
                assert row['crop_sha256'] == census['crop_sha256'] == prepared['crop_sha256']
                assert row['crop_source_sha256'] == prepared['source_sha256']
                assert row['crop_bbox'] == prepared['bbox']
                assert row.get('crop_color_mode', 'L') == prepared['color_mode']
                bindings[rid] = {k: row[k] for k in (
                    'crop_source_image', 'crop_source_sha256', 'crop_bbox', 'crop_sha256')}
                bindings[rid]['crop_color_mode'] = row.get('crop_color_mode', 'L')
                bindings[rid]['metadata_path'] = str(path)
                found += 1
        assert h.hexdigest() == expected['sha256'] and count == expected['rows']
        assert found == len(wave_ids)
        metadata_inputs.append(dict(path=str(path), sha256=h.hexdigest(), rows=count, selected_rows=found))
    assert len(bindings) == 200

    cache = Path.home() / 'Projects/collect-v3-data/run/cache/pages'
    pages, page_records = {}, {}
    # Verify all pages before making any crops. One decode per unique page.
    for r in pending:
        h = r['source_sha256']
        if h in pages:
            continue
        path = cache / (h + '.jpg')
        assert path.is_file(), f'Missing page: {path}; fetch only this recorded source: {r["source_page"]}'
        assert sha(path) == h, path
        pages[h] = path
        page_records[h] = dict(path=str(path), sha256=h, obtained='local_cache',
                               recorded_remote_path=r['source_page'])

    samples, provenance = [], []
    for r in pending + prior:
        rid = r['row_id']
        census = population[rid]
        group = r['sample_group']
        path = (D / 'samples' / (rid + '.png')).resolve()
        assert census['is_cell'] if group == 'cells' else (
            census['is_numeric_output'] and not census['is_small_image'] if group == 'numeric_not_small'
            else census['is_small_image'] and not census['is_numeric_output'])
        if rid in bindings:
            binding = bindings[rid]
            with Image.open(pages[r['source_sha256']]) as page:
                image, encoded = reconstructed_crop(page, binding['crop_bbox'], binding['crop_color_mode'])
            assert digest_bytes(encoded) == census['crop_sha256'], rid
            assert image.size == (census['width_px'], census['height_px']), rid
            assert not path.exists(), f'Refuse to recrop an existing output: {path}'
            path.write_bytes(encoded)
            obtained = dict(method='local_cache', source_page=str(pages[r['source_sha256']]),
                            page_sha256=r['source_sha256'], recorded_remote_page=r['source_page'],
                            crop_bbox=binding['crop_bbox'], crop_color_mode=binding['crop_color_mode'],
                            metadata_path=binding['metadata_path'])
        else:
            assert path == (D / r['crop_path']).resolve()
            obtained = dict(method='retained_existing_scp_crop', recorded_remote_crop=r['remote_crop'],
                            note='Fetched in SEG-CELLS-1; no new transfer or reconstruction in 1b.')
        assert sha(path) == census['crop_sha256'], rid
        with Image.open(path) as image:
            assert image.size == (census['width_px'], census['height_px'])
            image.verify()
        sample = dict(row_id=rid, parent_id=census['parent_id'], crop_path=str(path),
                      crop_sha256=census['crop_sha256'], sha256=census['crop_sha256'],
                      width=census['width_px'], height=census['height_px'],
                      w=census['width_px'], h=census['height_px'], chars=census['characters'],
                      text=census['raw_text'], source=census['source'],
                      primary_class=census['primary_class'], script_class=census['script_class'],
                      verdict_05=census['verdict_05'], reason_05=census['reason_05'],
                      reason=census['reason_05'], group=group, sample_group=group,
                      wave=census['wave'], pipeline_disposition=census['pipeline_disposition'],
                      text_characters=census['text_characters'], xheight_px=census['xheight_px'],
                      is_cell=census['is_cell'], is_numeric_output=census['is_numeric_output'],
                      is_small_image=census['is_small_image'])
        sample['class'] = census['primary_class']
        samples.append(sample)
        provenance.append(dict(row_id=rid, group=group, crop_path=str(path),
                               crop_sha256=census['crop_sha256'], replacement=False,
                               seeded_rank=orders[group].index(rid) + 1, **obtained))
    assert len(samples) == len({r['row_id'] for r in samples}) == 250
    assert len(list((D / 'samples').glob('*.png'))) == 250
    (D / 'samples.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in samples))
    dump(D / 'sample_receipt.json', dict(
        status='DONE_250_BYTE_EXACT', seed=20261019,
        targets=dict(cells=150, numeric_not_small=50, small_not_numeric=50),
        fetched_counts=dict(Counter(r['group'] for r in samples)), fetched=250,
        local_reconstructed_crops=200, retained_existing_scp_crops=50,
        pages_from_cache=len(pages), pages_scp=0, replacements=0,
        page_count_unit='unique source-page SHA256; 200 reconstructed samples use 156 cached pages',
        source_counts={group: dict(sorted(Counter(r['source'] for r in samples if r['group'] == group).items()))
                       for group in orders},
        order_sha256=hashlib.sha256(gzip.decompress((D / 'sample_order.jsonl.gz').read_bytes())).hexdigest(),
        order_gzip_sha256=sha(D / 'sample_order.jsonl.gz'), samples_sha256=sha(D / 'samples.jsonl'),
        pending_manifest_sha256=sha(D / 'pending_reconstruction.jsonl'),
        population_sha256=sha(D / 'population_cells.jsonl.gz'),
        reconstruction_function='greekocr.harvest.line_pipeline_native.reconstructed_crop (unchanged)',
        native_sha256=sha(ROOT / 'greekocr/harvest/line_pipeline_native.py'),
        metadata_inputs=metadata_inputs,
        w2_local_page_metadata_check='pages/*.json and resolved_manifest.jsonl inspected: page identity only; frozen local feature snapshot has the crop boxes',
        selection='First 150 cells and first 50 numeric_not_small in preserved orders; the original 50 fetched small_not_numeric retained in original order.',
        all_crop_hashes_and_png_dimensions_verified=True,
        remote_commands_1b=[], remote_writes=0, page_fetches=[], replacement_log=[],
        historical_failures='sample_failures.jsonl is the original SEG-CELLS-1 crop-file probe, not 1b page failures or replacements.',
        pages=list(page_records.values()), samples=provenance))
    dump(D / 'selected_metadata_1b.json', dict(inputs=metadata_inputs, rows=bindings))
    print(json.dumps(dict(samples=250, reconstructed=200, cached_pages=len(pages), scp=0,
                          replacements=0, groups=dict(Counter(r['group'] for r in samples))), indent=2))


if __name__ == '__main__':
    main()
