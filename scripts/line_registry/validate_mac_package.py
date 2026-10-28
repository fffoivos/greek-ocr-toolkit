"""Independent packaged-byte readback and three census→Google→raster joins.

Reads the portable package, a small fresh Clariden witness, and the legacy
representation receipt. Does not access original Mac payload paths or the network.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import struct
import tarfile
import time

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq


def sha(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20), b''):
            h.update(b)
    return h.hexdigest()


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def object_bytes(root, rec):
    with (root/rec['shard_path']).open('rb') as f:
        f.seek(rec['offset'])
        b = f.read(rec['length'])
    assert len(b) == rec['bytes'] and sha(b) == rec['stored_sha256']
    return b


def image_bytes(root, rec):
    # File reads restricted to one Parquet row group containing this source object.
    p = pq.ParquetFile(root/rec['shard_path'])
    first = 0
    for i in range(p.num_row_groups):
        n = p.metadata.row_group(i).num_rows
        if first <= rec['shard_row'] < first+n:
            b = p.read_row_group(i, columns=['image_bytes'])['image_bytes'][rec['shard_row']-first].as_py()
            assert sha(b) == rec['image_sha256'] and len(b) == rec['source_bytes']
            return b
        first += n
    raise AssertionError('invalid page shard row')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--remote', type=Path, required=True)
    ap.add_argument('--legacy-representation', type=Path, required=True)
    ap.add_argument('--receipt', type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    root = args.root
    manifest_path = root/'manifests/mac-artifacts.json'
    m = json.loads(manifest_path.read_text())
    for a in m['artifacts']:
        p = root/a['path']
        assert p.stat().st_size == a['bytes'] <= 1_000_000_000
        assert file_sha(p) == a['sha256'], ('shard SHA mismatch', p)
    print(canonical(dict(event='all_artifact_shas_pass', files=len(m['artifacts']))), flush=True)
    sums = (root/'manifests/MAC_SHA256SUMS').read_text()
    expected_sums = ''.join(f"{a['sha256']}  {a['path']}\n" for a in m['artifacts'])
    expected_sums += f'{file_sha(manifest_path)}  manifests/mac-artifacts.json\n'
    assert sums == expected_sums
    listed = {a['path'] for a in m['artifacts']} | {'manifests/mac-artifacts.json','manifests/MAC_SHA256SUMS'}
    files = [str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()]
    # hf upload-large-folder creates local progress metadata here on future
    # resumptions; the CLI excludes this cache from publication automatically.
    upload_cache = [p for p in files if p.startswith('.cache/huggingface/')]
    actual = set(files)-set(upload_cache)
    assert listed == actual, ('unexpected/unlisted file', sorted(actual-listed), sorted(listed-actual))
    pages = pq.read_table(root/'pages/pages.parquet').to_pylist()
    objects = pq.read_table(root/'provenance/mac/source_objects.parquet').to_pylist()
    assert len(pages) == m['page_objects'] and len(objects) == m['source_objects']
    page_ids = {r['page_object_id']:r for r in pages}
    object_ids = {r['source_object_id']:r for r in objects}
    assert len(page_ids) == len(pages) and len(object_ids) == len(objects)
    source_by_member = {(r['shard_path'],r['member_path']):r for r in objects}
    assert len(source_by_member) == len(objects)
    page_payloads = source_payloads = page_bytes = source_bytes = 0
    for a in m['artifacts']:
        p = root/a['path']
        if a['path'].startswith('pages/rasters/'):
            shard_rows = 0
            for batch in pq.ParquetFile(p).iter_batches(batch_size=8):
                for r in batch.to_pylist():
                    rec = page_ids[r['page_object_id']]
                    assert rec['shard_path']==a['path'] and rec['shard_row']==shard_rows
                    assert sha(r['image_bytes']) == rec['image_sha256']
                    assert len(r['image_bytes']) == rec['source_bytes']
                    for k in ['image_sha256','width','height','source_root','source_relative_path']:
                        assert rec[k] == r[k]
                    shard_rows += 1
                    page_payloads += 1
                    page_bytes += len(r['image_bytes'])
            assert shard_rows == a['records']
        elif p.suffix == '.tar':
            n = 0
            with tarfile.open(p, 'r:') as tf:
                for member in tf:
                    rec = source_by_member[(a['path'], member.name)]
                    assert member.size == rec['bytes'] and member.offset_data == rec['offset']
                    b = tf.extractfile(member).read()
                    assert sha(b) == rec['stored_sha256']
                    n += 1
                    source_payloads += 1
                    source_bytes += len(b)
            assert n == a['records']
    assert page_payloads == len(pages) and source_payloads == len(objects)
    assert page_bytes == m['page_bytes'] and source_bytes == m['source_bytes']
    print(canonical(dict(event='all_embedded_payloads_pass', images=page_payloads, source_objects=source_payloads)), flush=True)

    remote = json.loads(args.remote.read_text())
    legacy_representation = json.loads(args.legacy_representation.read_text())
    observations = pq.read_table(root/'provenance/mac/w_page_observations.parquet').to_pylist()
    observations = {r['source_page_id']:r for r in observations}
    # Both source groups use the same schema, independently imported from archived responses.
    box_paths = [str(root/a['path']) for a in m['artifacts'] if '/google_boxes/' in a['path']]
    boxes = ds.dataset(box_paths, format='parquet')
    unique = set()
    original_by_source = {}
    box_total = 0
    image_missing = 0
    for batch in boxes.to_batches(columns=['box_id','page_object_ids_json','source_object_id','response_original_sha256']):
        for r in batch.to_pylist():
            assert r['box_id'] not in unique
            unique.add(r['box_id'])
            box_total += 1
            matches = json.loads(r['page_object_ids_json'])
            assert all(p in page_ids for p in matches)
            image_missing += not matches
            if r['response_original_sha256']:
                prev = original_by_source.setdefault(r['source_object_id'],r['response_original_sha256'])
                assert prev == r['response_original_sha256']
    outcome_counts = Counter()
    outcome_boxes = 0
    non_document_kinds = Counter()
    sidecar_targets = Counter()
    by_source_path = {(r['source_root'],r['source_relative_path']):r for r in objects}
    frames_by_sha = {}
    for r in pages:
        frames_by_sha.setdefault(r['image_sha256'],set()).add((r['width'],r['height']))
    frame_mismatches = []
    for a in m['artifacts']:
        if a['path'].endswith('_page_results.parquet'):
            for r in pq.read_table(root/a['path']).to_pylist():
                assert r['source_object_id'] in object_ids
                outcome_counts[r['status']] += 1
                outcome_boxes += r['box_count']
                if r.get('dimension_json') and r.get('image_match_count'):
                    dim = json.loads(r['dimension_json'])
                    if (dim.get('width'),dim.get('height')) not in frames_by_sha[r['page_image_sha256']]:
                        frame_mismatches.append(r['source_object_id'])
                if r['status']=='not_document':
                    detail = json.loads(r['detail_json'])
                    if 'raw_json_path' in detail:
                        non_document_kinds['response_receipt_sidecar'] += 1
                        relative = detail['raw_json_path'].split('/harvest_big/',1)[1]
                        target = (by_source_path.get(('harvest',relative)) or
                                  by_source_path.get(('harvest',relative+'.dedup.gz')) or
                                  by_source_path.get(('harvest',relative+'.gz')))
                        sidecar_targets['resolved' if target else 'unresolved'] += 1
                        if target and target['original_response_sha256']:
                            assert target['original_response_sha256'] == detail['raw_sha256']
                        if target and target['source_object_id'] in original_by_source:
                            assert original_by_source[target['source_object_id']] == detail['raw_sha256']
                    elif 'error' in detail:
                        non_document_kinds['request_error_record'] += 1
                    else:
                        non_document_kinds['other'] += 1
    assert box_total == outcome_boxes, 'partial parsing/count mismatch'
    joins = []
    sql = sqlite3.connect(':memory:')
    sql.executescript('CREATE TABLE pages(page_id TEXT PRIMARY KEY, image_sha TEXT);'
        'CREATE TABLE boxes(box_id TEXT PRIMARY KEY, page_id TEXT);'
        'CREATE TABLE rows(row_key TEXT PRIMARY KEY, box_id TEXT);')
    for witness in remote['rows']:
        obs = witness['observation']
        if witness['parent_id'].startswith('collect-v3'):
            page = observations[witness['page_id']]
            source_record = object_ids[page['source_object_id']]
            pg = json.loads(object_bytes(root, source_record))
            image_sha = pg['image_sha256']
            candidates = [r for r in objects if r['acquisition_group']=='w_raw_responses'
                          and Path(r['source_relative_path']).name == Path(pg['response']).name]
            assert len(candidates)==1
            response = candidates[0]
            assert response['stored_sha256'] == pg['response_sha256']
            line_index = obs['docai_line_index']
            expected_bbox = obs['bbox']
        else:
            legacy = witness['legacy']['record']
            image_sha = legacy['image_sha256']
            suffix = legacy_representation['path'].split('/harvest_big/',1)[1]
            candidates = [r for r in objects if r['source_relative_path']==suffix]
            assert len(candidates)==1
            response = candidates[0]
            line_index = legacy['docai_index']
            expected_bbox = legacy['bbox']
            assert legacy['id'] == witness['row_id']
            assert legacy['page_id'] == witness['page_id'] == obs['page_id']
            assert 'round1:'+legacy['book_key'] == obs['book_id'] == witness['edition_id']
            assert legacy['docai_raw_text'].strip() == obs['raw_text'].strip()
            if obs.get('crop_source_sha256') is not None:
                assert image_sha == obs['crop_source_sha256']
        b = object_bytes(root, response)
        raw = json.loads(gzip.decompress(b) if response['source_relative_path'].endswith('.gz') else b)
        if 'response' in raw:
            raw = raw['response']
        google = raw['document']['pages'][0]
        assert not google.get('transforms'), 'sample needs explicit coordinate-frame mapping'
        line = google['lines'][line_index]
        matches = boxes.to_table(filter=(ds.field('source_object_id')==response['source_object_id']) &
                    (ds.field('raw_page_index')==0) & (ds.field('reading_order')==line_index)).to_pylist()
        assert len(matches)==1
        box = matches[0]
        assert json.loads(box['raw_segmenter_json'])==line
        assert json.loads(box['bbox_px_json']) == expected_bbox
        assert box['text_anchor_text'].strip() == obs['raw_text'].strip()
        candidates = [r for r in pages if r['image_sha256']==image_sha and not r['auxiliary']]
        assert len(candidates)==1
        page = candidates[0]
        assert page['page_object_id'] in json.loads(box['page_object_ids_json'])
        image = image_bytes(root, page)
        assert [google['dimension']['width'],google['dimension']['height']] == [page['width'],page['height']]
        reconstructed = None
        if witness['legacy']:
            assert sha(b)==legacy_representation['stored_sha256']
            expected_original = legacy_representation['original_response_sha256']
            im = google['image']
            im.pop('content_stripped')
            im['content'] = base64.b64encode(image).decode()
            reconstructed = sha((canonical(raw)+'\n').encode())
            assert reconstructed == expected_original
        row_key = sha(canonical([witness['parent_id'],witness['row_id']]).encode())
        sql.execute('INSERT INTO pages VALUES (?,?)', (page['page_object_id'],image_sha))
        sql.execute('INSERT INTO boxes VALUES (?,?)', (box['box_id'],page['page_object_id']))
        sql.execute('INSERT INTO rows VALUES (?,?)', (row_key,box['box_id']))
        joins.append(dict(parent_id=witness['parent_id'],row_id=witness['row_id'],row_key=row_key,
            box_id=box['box_id'],page_object_id=page['page_object_id'],image_sha256=image_sha,
            response_stored_sha256=response['stored_sha256'],
            reconstructed_original_response_sha256=reconstructed,
            crop_sha256=witness['crop']['sha256'],crop_verified_on=remote['host'],
            page_hash_binding='keyed_original_harvest_record' if witness['legacy'] else 'W_page_record',
            census_page_image_sha256=obs.get('crop_source_sha256'),
            google_transforms=google.get('transforms'),
            bbox=expected_bbox,raw_line_index=line_index,raw_text_matches=True,
            dimensions_match=True,join_pass=True))
    joined = sql.execute('SELECT count(*) FROM rows r JOIN boxes b USING(box_id) JOIN pages p USING(page_id)').fetchone()[0]
    assert joined == 3
    result = dict(schema='runner4-hf-phase1-validation-v1', root=str(root),
        scope='all shard SHA256s; all embedded image/source payload SHA256s; imported boxes/outcomes; three current Clariden row joins using portable Mac inputs',
        manifest_sha256=file_sha(manifest_path), validator_sha256=file_sha(Path(__file__)),
        remote_witness_sha256=file_sha(args.remote), legacy_representation_receipt_sha256=file_sha(args.legacy_representation),
        artifact_files=len(m['artifacts']),artifact_bytes=sum(a['bytes'] for a in m['artifacts']),
        max_artifact_bytes=max(a['bytes'] for a in m['artifacts']),
        page_objects=page_payloads,source_objects=source_payloads,
        verified_image_bytes=page_bytes,verified_source_bytes=source_bytes,
        raw_box_count=box_total,boxes_without_retained_raster=image_missing,
        response_outcomes=dict(outcome_counts),joins_pass=joined,joins=joins,
        non_document_source_kinds=dict(non_document_kinds),sidecar_response_targets=dict(sidecar_targets),
        unique_raster_hashes=len(frames_by_sha),native_frame_mismatches=len(frame_mismatches),
        native_frame_mismatch_examples=frame_mismatches[:10],
        native_frame_mismatch_source_object_ids=frame_mismatches,
        ignored_local_upload_cache_files=len(upload_cache),
        elapsed_seconds=time.monotonic()-start,
        limitations=['Three representative joins only, not the entire census or release population',
          'HF handoff HIGH remains open until publication + pinned Clariden download/readback',
          'Temporary staging path requires relocation to owner-requested durable root'])
    args.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(canonical(result),flush=True)


if __name__=='__main__':
    main()
