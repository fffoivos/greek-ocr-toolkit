"""RUNNER4 Phase 1: local, exact-byte Mac handoff; no HF/network/cluster calls.

python3 scripts/line_registry/package_mac.py --output /private/tmp/hf-staging/greek-ocr-lines
Only the pinned Mac selection is packaged. This is not the census/feature builder.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]
PIN = REPO / 'docs/programme_20261019/registry/SOURCE_MANIFEST.json'
PIN_SHA = 'f468812a38687cad4aa025290c207ea9148eac2068aa721f7809f933e78c6578'
TARGET = 512_000_000
MAXIMUM = 1_000_000_000
RESERVE = 50_000_000_000  # 40 GB W3 allowance plus owner's 10 GB free floor
PAGE_GROUPS = ['legacy_page_images', 'w_cache', 'legacy_composite_images']
RAW_GROUPS = ['legacy_raw_responses', 'w_raw_responses']
META_GROUPS = ['w_page_records', 'w_state_receipts', 'legacy_page_metadata',
               'legacy_google_receipts', 'legacy_metadata', 'legacy_assignments']


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def write_json(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.partial')
    tmp.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(p)


def source_id(r):
    return digest(canonical([r['root'], r['relative_path']]).encode())


def dimensions(b):
    import struct
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return (*struct.unpack('>II', b[16:24]), 'png')
    assert b[:2] == b'\xff\xd8', 'unsupported selected image format'
    f = io.BytesIO(b)
    f.seek(2)
    while True:
        marker = f.read(1)
        if not marker:
            raise ValueError('JPEG has no SOF')
        if marker != b'\xff':
            continue
        while marker == b'\xff':
            marker = f.read(1)
        if marker[0] in (0xd8, 0xd9):
            continue
        n = struct.unpack('>H', f.read(2))[0]
        if marker[0] in (0xc0, 0xc1, 0xc2, 0xc3):
            height, width = struct.unpack('>HH', f.read(5)[1:])
            return width, height, 'jpeg'
        f.seek(n - 2, 1)


BOX_SCHEMA = pa.schema([(k, t) for k, t in [
    ('box_id', pa.string()), ('source_object_id', pa.string()),
    ('response_stored_sha256', pa.string()), ('response_original_sha256', pa.string()),
    ('segmenter', pa.string()), ('segmenter_run_id', pa.string()),
    ('page_image_sha256', pa.string()), ('page_object_ids_json', pa.string()),
    ('raw_page_index', pa.int64()), ('reading_order', pa.int64()),
    ('width', pa.float64()), ('height', pa.float64()),
    ('bbox_px_json', pa.string()), ('polygon_px_json', pa.string()),
    ('polygon_normalized_json', pa.string()), ('raw_segmenter_json', pa.string()),
    ('text_anchor_text', pa.string()), ('response_representation', pa.string())]])


class SmallParquet:
    def __init__(self, ctx, prefix, schema):
        self.ctx, self.prefix, self.schema = ctx, prefix, schema
        self.buffer, self.artifacts, self.writer = [], [], None
        self.count = self.part = self.part_count = self.part_payload = 0

    def add(self, row):
        self.buffer.append(row)
        if len(self.buffer) >= 4000:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        t = pa.Table.from_pylist(self.buffer, schema=self.schema)
        if self.writer is None:
            self.path = self.ctx.output / f'{self.prefix}/part-{self.part:05d}.parquet'
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.writer = pq.ParquetWriter(self.path.with_suffix('.partial'), self.schema,
                                          compression='zstd', use_dictionary=False)
        self.writer.write_table(t)
        self.part_count += len(self.buffer)
        self.count += len(self.buffer)
        self.part_payload += t.nbytes
        self.buffer.clear()
        if self.part_payload >= TARGET:
            self.close_part()

    def close_part(self):
        if self.writer:
            self.writer.close()
            self.path.with_suffix('.partial').replace(self.path)
            self.artifacts.append(self.ctx.artifact(self.path, self.part_count))
            self.writer = None
            self.part += 1
            self.part_count = self.part_payload = 0

    def finish(self):
        self.flush()
        self.close_part()
        return self.artifacts


class Context:
    def __init__(self, output):
        self.output = output
        self.local = output.parent / (output.name + '.receipts')
        self.local.mkdir(parents=True, exist_ok=True)
        self.code_sha = file_sha(Path(__file__))
        assert file_sha(PIN) == PIN_SHA
        self.pin = json.loads(PIN.read_text())
        self.roots = {k: Path(v) for k, v in self.pin['roots'].items()}
        self.groups = {}
        self.artifacts = []
        self.page_index = []
        self.source_index = []
        self.page_by_sha = defaultdict(list)
        self.w_response_sha = {}
        self.free_before = shutil.disk_usage(output.parent).free
        for group in PAGE_GROUPS + RAW_GROUPS + META_GROUPS:
            g = self.pin['groups'][group]
            p = REPO / g['inventory_path']
            assert file_sha(p) == g['inventory_sha256'], ('inventory pin', group)
            rows = list(csv.DictReader(p.open(), delimiter='\t'))
            assert len(rows) == g['files']
            self.groups[group] = rows
            for r in rows:
                s = self.path(r).stat()
                assert (s.st_size, s.st_mtime_ns) == (int(r['bytes']), int(r['mtime_ns'])), ('source drift', r)
        total = sum(int(r['bytes']) for rs in self.groups.values() for r in rs)
        # Resumes count existing verified bytes as already allocated, never duplicate them.
        existing = sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) if output.exists() else 0
        assert self.free_before - max(0, int(total * 1.08) + 2_000_000_000 - existing) >= RESERVE, 'insufficient disk for W3 + 10 GB floor'
        for r in self.groups['w_page_records']:
            d = json.loads(self.path(r).read_bytes())
            if d.get('response') and d.get('response_sha256'):
                name = Path(d['response']).name
                prev = self.w_response_sha.setdefault(name, d['response_sha256'])
                assert prev == d['response_sha256']
        print(canonical(dict(event='preflight', source_files=sum(map(len, self.groups.values())),
                             source_bytes=total, free_bytes=self.free_before, reserved_bytes=RESERVE)), flush=True)

    def path(self, r):
        return self.roots[r['root']] / r['relative_path']

    def check_space(self):
        assert shutil.disk_usage(self.output.parent).free >= RESERVE, 'W3 + free-floor reserve reached; stopped'

    def read(self, r):
        p = self.path(r)
        before = p.stat()
        b = p.read_bytes()
        after = p.stat()
        assert (before.st_size, before.st_mtime_ns) == (int(r['bytes']), int(r['mtime_ns']))
        assert (after.st_size, after.st_mtime_ns) == (before.st_size, before.st_mtime_ns)
        sha = digest(b)
        expected = r['expected_stored_sha256']
        basis = r['hash_basis']
        # W response basenames identify PAGE bytes, not response bytes. The old
        # selection's filename claim is retained, never treated as a response pin.
        if r['group'] == 'w_raw_responses':
            expected = self.w_response_sha.get(p.name)
            basis = 'page_record_response_sha256' if expected else 'no_historical_stored_pin'
        if expected:
            assert expected == sha, ('stored source hash mismatch', str(p), basis, expected, sha)
        return b, sha, basis, expected

    def artifact(self, p, records=None):
        size = p.stat().st_size
        assert size <= MAXIMUM, ('shard exceeds cap', p, size)
        return dict(path=str(p.relative_to(self.output)), bytes=size, sha256=file_sha(p), records=records)

    def resume(self, group):
        p = self.local / f'{group}.json'
        if not p.exists():
            return None
        r = json.loads(p.read_text())
        assert r['code_sha256'] == self.code_sha and r['source_manifest_sha256'] == PIN_SHA, 'resume binding changed'
        assert file_sha(self.local/f'{group}.index.json') == r['index_sha256']
        for a in r['artifacts']:
            p = self.output / a['path']
            assert p.stat().st_size == a['bytes'] and file_sha(p) == a['sha256']
        self.artifacts.extend(r['artifacts'])
        print(canonical(dict(event='resume_verified', group=group)), flush=True)
        return r

    def receipt(self, group, start, artifacts, **extra):
        r = dict(group=group, code_sha256=self.code_sha, source_manifest_sha256=PIN_SHA,
                 elapsed_seconds=time.monotonic()-start, artifacts=artifacts,
                 index_sha256=file_sha(self.local/f'{group}.index.json'), **extra)
        write_json(self.local/f'{group}.json', r)
        self.artifacts.extend(artifacts)
        print(canonical(dict(event='group_complete', group=group, seconds=r['elapsed_seconds'],
                             shards=len(artifacts), bytes=sum(a['bytes'] for a in artifacts), **extra)), flush=True)


def package_pages(c, group):
    resumed = c.resume(group)
    if resumed:
        index = json.loads((c.local/f'{group}.index.json').read_text())
        c.page_index.extend(index)
        for r in index:
            c.page_by_sha[r['image_sha256']].append(r['page_object_id'])
        return
    start = time.monotonic()
    schema = pa.schema([(k, t) for k, t in [
        ('page_object_id', pa.string()), ('source_root', pa.string()), ('source_relative_path', pa.string()),
        ('image_sha256', pa.string()), ('image_format', pa.string()), ('width', pa.int64()),
        ('height', pa.int64()), ('source_bytes', pa.int64()), ('image_bytes', pa.binary())]])
    artifacts, index = [], []
    batch, payload, part, writer, ordinal = [], 0, 0, None, 0

    def flush():
        nonlocal batch
        if batch:
            writer.write_table(pa.Table.from_pylist(batch, schema=schema))
            batch = []

    def close():
        nonlocal writer
        if writer:
            flush()
            writer.close()
            tmp.replace(path)
            artifacts.append(c.artifact(path, ordinal))
            writer = None
            c.check_space()
            print(canonical(dict(event='page_shard', group=group, part=part, records=ordinal)), flush=True)

    for i, r in enumerate(c.groups[group]):
        b, sha, basis, expected = c.read(r)
        if writer and payload + len(b) > TARGET - 16_000_000:
            close()
            part += 1
            payload = ordinal = 0
        if writer is None:
            path = c.output / f'pages/rasters/{group}/part-{part:05d}.parquet'
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix('.partial')
            writer = pq.ParquetWriter(tmp, schema, compression=None, use_dictionary=False)
        width, height, fmt = dimensions(b)
        record = dict(page_object_id=source_id(r), source_root=r['root'], source_relative_path=r['relative_path'],
                      image_sha256=sha, image_format=fmt, width=width, height=height, source_bytes=len(b))
        index.append(dict(**record, shard_path=str(path.relative_to(c.output)), shard_row=ordinal,
                          acquisition_group=group, auxiliary=(group=='legacy_composite_images'),
                          historical_stored_sha256=expected, historical_hash_basis=basis))
        c.page_by_sha[sha].append(record['page_object_id'])
        batch.append(dict(**record, image_bytes=b))
        payload += len(b)
        ordinal += 1
        if sum(x['source_bytes'] for x in batch) >= 32_000_000:
            flush()
    close()
    write_json(c.local/f'{group}.index.json', index)
    c.page_index.extend(index)
    c.receipt(group, start, artifacts, source_files=len(index), source_bytes=sum(r['source_bytes'] for r in index))


def response_data(b, r):
    obj = json.loads(gzip.decompress(b) if r['relative_path'].endswith('.gz') else b)
    if 'response' in obj:
        return obj['response'], obj.get('image_references', []), obj.get('raw_sha256'), 'dedup_gzip_wrapper'
    return obj, [], r.get('original_response_sha256') or None, 'stored_json'


def import_boxes(c, b, r, sha, sink, outcomes):
    try:
        obj, refs, original, representation = response_data(b, r)
        doc = obj.get('document', obj)
        if 'pages' not in doc:
            outcomes.append(dict(source_object_id=source_id(r), status='not_document', box_count=0,
                                 detail_json=canonical(obj)))
            return
        fallback = Path(r['relative_path']).stem if r['group']=='w_raw_responses' else Path(r['relative_path']).parent.name.split('-')[0]
        for pi, page in enumerate(doc['pages']):
            image_sha = next((x.get('sha256') for x in refs if x.get('page')==pi), fallback)
            dim = page.get('dimension', {})
            width, height = float(dim.get('width', 0)), float(dim.get('height', 0))
            lines = page.get('lines', [])
            for li, line in enumerate(lines):
                poly = line.get('layout', {}).get('boundingPoly', {})
                norm = [[v.get('x', 0), v.get('y', 0)] for v in poly.get('normalizedVertices', [])]
                px = [[v.get('x', 0), v.get('y', 0)] for v in poly.get('vertices', [])]
                if not px:
                    px = [[x*width, y*height] for x, y in norm]
                envelope = [min(x for x,y in px), min(y for x,y in px), max(x for x,y in px), max(y for x,y in px)] if px else None
                segments = line.get('layout', {}).get('textAnchor', {}).get('textSegments', [])
                text = ''.join(doc.get('text', '')[int(s.get('startIndex', 0)):int(s['endIndex'])] for s in segments)
                sink.add(dict(box_id=digest(canonical([source_id(r),pi,li,'google-raw-v1']).encode()),
                    source_object_id=source_id(r), response_stored_sha256=sha, response_original_sha256=original,
                    segmenter='google', segmenter_run_id=digest(canonical(['retained-google',source_id(r),sha]).encode()),
                    page_image_sha256=image_sha, page_object_ids_json=canonical(c.page_by_sha.get(image_sha, [])),
                    raw_page_index=pi, reading_order=li, width=width, height=height,
                    bbox_px_json=canonical(envelope), polygon_px_json=canonical(px), polygon_normalized_json=canonical(norm),
                    raw_segmenter_json=canonical(line), text_anchor_text=text, response_representation=representation))
            outcomes.append(dict(source_object_id=source_id(r), raw_page_index=pi, page_image_sha256=image_sha,
                status='ok' if lines else 'zero_detections', box_count=len(lines),
                image_match_count=len(c.page_by_sha.get(image_sha, [])), dimension_json=canonical(dim),
                detail_json=None))
    except (ValueError, KeyError, TypeError) as e:
        # Exact source object still archived. Expose, never silently discard, parse failures.
        outcomes.append(dict(source_object_id=source_id(r), status='parse_error', box_count=0,
                             detail_json=str(e)))


def package_tar(c, group):
    resumed = c.resume(group)
    if resumed:
        c.source_index.extend(json.loads((c.local/f'{group}.index.json').read_text()))
        return
    start = time.monotonic()
    index, artifacts, outcomes = [], [], []
    sink = SmallParquet(c, f'provenance/mac/google_boxes/{group}', BOX_SCHEMA) if group in RAW_GROUPS else None
    tf, part, part_count = None, 0, 0
    prefix = 'provenance/google' if sink else 'provenance/sources/mac'

    def close():
        nonlocal tf
        if tf:
            tf.close()
            tmp.replace(path)
            artifacts.append(c.artifact(path, part_count))
            tf = None
            c.check_space()
            print(canonical(dict(event='tar_shard', group=group, part=part, records=part_count)), flush=True)

    for r in c.groups[group]:
        b, sha, basis, expected = c.read(r)
        padded = ((len(b)+511)//512)*512
        if tf and tf.offset + 512 + padded + 10240 > TARGET:
            close()
            part += 1
            part_count = 0
        if tf is None:
            path = c.output / f'{prefix}/{group}/part-{part:05d}.tar'
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix('.partial')
            tf = tarfile.open(tmp, 'w', format=tarfile.USTAR_FORMAT)
        member = 'objects/' + source_id(r) + ''.join(Path(r['relative_path']).suffixes)
        # source path retained in index, short deterministic member needs no PAX header.
        ti = tarfile.TarInfo(member)
        ti.size, ti.mtime, ti.uid, ti.gid, ti.mode = len(b), 0, 0, 0, 0o644
        offset = tf.offset + 512
        tf.addfile(ti, io.BytesIO(b))
        part_count += 1
        index.append(dict(source_object_id=source_id(r), source_root=r['root'], source_relative_path=r['relative_path'],
            acquisition_group=group, bytes=len(b), stored_sha256=sha, historical_stored_sha256=expected,
            historical_hash_basis=basis, original_response_sha256=r.get('original_response_sha256') or None,
            shard_path=str(path.relative_to(c.output)), member_path=member, offset=offset, length=len(b)))
        if sink:
            import_boxes(c, b, r, sha, sink, outcomes)
    close()
    if sink:
        artifacts.extend(sink.finish())
        p = c.output/f'provenance/mac/{group}_page_results.parquet'
        outcome_schema = pa.schema([(k, t) for k, t in [
            ('source_object_id', pa.string()), ('raw_page_index', pa.int64()),
            ('page_image_sha256', pa.string()), ('status', pa.string()),
            ('box_count', pa.int64()), ('image_match_count', pa.int64()),
            ('dimension_json', pa.string()), ('detail_json', pa.string())]])
        pq.write_table(pa.Table.from_pylist(outcomes, schema=outcome_schema), p, compression='zstd')
        artifacts.append(c.artifact(p, len(outcomes)))
    write_json(c.local/f'{group}.index.json', index)
    c.source_index.extend(index)
    c.receipt(group, start, artifacts, source_files=len(index), source_bytes=sum(r['bytes'] for r in index),
              boxes=sink.count if sink else 0, outcomes=dict(Counter(r['status'] for r in outcomes)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--groups', nargs='+', help='optional bounded first batch; no final manifest until all groups complete')
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    c = Context(args.output)
    selected = set(args.groups or c.groups)
    for g in PAGE_GROUPS:
        # Raw import needs the complete hash alias table, even in a resumed run.
        if g in selected or selected.intersection(RAW_GROUPS) or (c.local/f'{g}.json').exists():
            package_pages(c, g)
    for g in RAW_GROUPS + META_GROUPS:
        if g in selected:
            package_tar(c, g)
    if set(c.groups) != selected:
        print(canonical(dict(event='bounded_batch_complete', groups=sorted(selected))), flush=True)
        return
    for name, records in [('pages/pages.parquet', c.page_index), ('provenance/mac/source_objects.parquet', c.source_index)]:
        p = c.output/name
        p.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.Table.from_pylist(records), p, compression='zstd')
        c.artifacts.append(c.artifact(p, len(records)))
    observations = []
    for r in c.source_index:
        if r['acquisition_group'] != 'w_page_records':
            continue
        with (c.output/r['shard_path']).open('rb') as f:
            f.seek(r['offset'])
            b = f.read(r['length'])
        assert digest(b) == r['stored_sha256']
        d = json.loads(b)
        observations.append(dict(source_object_id=r['source_object_id'], source_page_id=d['id'],
            source=d.get('source'), tranche=d.get('tranche'), book_id=d['id'].rsplit('--s', 1)[0],
            provider_item_id=d.get('item'), provider_page=d.get('page'), status=d.get('status'),
            image_sha256=d.get('image_sha256'), response_sha256=d.get('response_sha256'),
            page_object_ids_json=canonical(c.page_by_sha.get(d.get('image_sha256'), [])),
            rights_json=canonical(d.get('rights')), raw_page_record_json=canonical(d)))
    p = c.output/'provenance/mac/w_page_observations.parquet'
    pq.write_table(pa.Table.from_pylist(observations), p, compression='zstd')
    c.artifacts.append(c.artifact(p, len(observations)))
    # Archive selected inventories + pin: consumers need no Mac paths to resolve payloads.
    for p in [PIN] + [REPO/c.pin['groups'][g]['inventory_path'] for g in c.groups]:
        dst = c.output/'manifests/mac-selection'/p.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dst)
        c.artifacts.append(c.artifact(dst))
    manifest = dict(schema='runner4-mac-handoff-v1', phase='mac-packaged-not-published', complete_v4=False,
        created_utc=datetime.now(timezone.utc).isoformat(), source_manifest_sha256=PIN_SHA,
        code_sha256=c.code_sha, producing_head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip(),
        code_path='scripts/line_registry/package_mac.py', code_uncommitted=True,
        page_objects=len(c.page_index), source_objects=len(c.source_index),
        page_bytes=sum(r['source_bytes'] for r in c.page_index), source_bytes=sum(r['bytes'] for r in c.source_index),
        disk_before_free_bytes=c.free_before, disk_after_free_bytes=shutil.disk_usage(c.output.parent).free,
        disk_reserved_bytes=RESERVE, shard_target_bytes=TARGET, shard_max_bytes=MAXIMUM,
        image_representation='exact original PNG/JPEG bytes embedded in Parquet; no re-encoding',
        identity='page_object_id identifies a source raster locator, not yet the final logical page observation; join aliases by image_sha256',
        limitations=['Final census rows/features/crops/references/synthetic remain Clariden Phase 2',
          'Per-source metadata and all per-page parse/zero/missing-image outcomes retained; aliases and contributor reconciliation pending',
          'Historical original response hashes are distinct from stored-object hashes; no global reconstruction claim'],
        artifacts=sorted(c.artifacts, key=lambda a:a['path']))
    p = c.output/'manifests/mac-artifacts.json'
    write_json(p, manifest)
    sums = ''.join(f"{a['sha256']}  {a['path']}\n" for a in manifest['artifacts'])
    sums += f'{file_sha(p)}  manifests/mac-artifacts.json\n'
    (c.output/'manifests/MAC_SHA256SUMS').write_text(sums)
    print(canonical(dict(event='package_complete', artifacts=len(c.artifacts),
        bytes=sum(a['bytes'] for a in c.artifacts), manifest_sha256=file_sha(p))), flush=True)


if __name__ == '__main__':
    main()
