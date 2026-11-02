"""Local-only release I/O. This module never decodes or re-encodes an image."""
from __future__ import annotations

import gzip
from decimal import Decimal
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import struct
import tarfile

import pyarrow as pa
import pyarrow.parquet as pq

CAP = 1_000_000_000
TARGET = 512_000_000
VERSION = 'rel0-s4b-v1'
PINS = {'staging-v4': '8ee9cb2e4c880f450c69b9c45cd683765d4da755',
        'harvest-20261025': '103c6dcd1e5dac6d72a1048462cd5b1864600cca'}
TABLES = ('pages', 'page_images', 'page_frames', 'boxes', 'segmenter_page_results',
          'rows', 'label_versions', 'row_features', 'row_instruments',
          'training_membership', 'references', 'book_registry', 'book_sources')
SOURCE_FIELDS = ('provider source item edition volume source_title year page '
                 'page_number_convention catalogue_url catalogue_reference manifest_url source_url source_record_sha256').split()
# Public native A12 attributes, including native width before image measurement.
# Payload bytes are compared by SHA256; licence fields remain excluded.
SYNTHETIC_MATCH_FIELDS = ('line_id reuse_index split width gt_nfc gt_nfd label_ids codec_version '
                          'script_class severity applied_ops font polarity bg_type accent_survival '
                          'source_dataset source_doc_id').split()


def synthetic_match_group(row, image_sha256, build):
    return digest(canonical([build, image_sha256,
                             {k: row.get(k) for k in SYNTHETIC_MATCH_FIELDS}]))


AUTH = ('HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'HUGGINGFACEHUB_API_TOKEN',
        'HUGGINGFACE_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS', 'AWS_SECRET_ACCESS_KEY',
        'AWS_SESSION_TOKEN')
PRIVATE = {'raw_segmenter_json', 'raw_response', 'response_payload', 'raw_google_payload',
           'raw_page_record_json'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def pending_resolvers(spec):
    entries = spec.get('unresolved_bindings', []) + [e for e in spec.get('partial_bindings', [])
              if (e.get('value') or {}).get('pending_status')]
    return [e for e in entries if e.get('resolve_probe') and not e.get('historical_unknown')]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(4 << 20), b''):
            h.update(chunk)
            from .progress import active
            progress = active.get()
            if progress is not None:
                progress.bytes += len(chunk)
    return h.hexdigest()


def info(path, root=None):
    p = Path(path)
    return {'path': p.relative_to(root).as_posix() if root else str(p.resolve()),
            'bytes': p.stat().st_size, 'sha256': sha(p)}


def parallel_info(paths, root=None):
    """Hash independent closed files on up to eight CPUs, retaining path order.

    Workers never touch SQLite or writers. Hashlib releases the GIL for these
    4-MiB reads; only the parent updates the active progress counter.
    """
    from concurrent.futures import ThreadPoolExecutor
    from .progress import active
    workers = max(1, min(8, int(os.environ.get('SLURM_CPUS_PER_TASK', '8')), os.cpu_count() or 1))
    progress = active.get()
    from collections import deque
    paths = iter(paths)
    pool = ThreadPoolExecutor(max_workers=workers)
    pending = deque()
    try:
        for _ in range(workers):
            path = next(paths, None)
            if path is None:
                break
            pending.append(pool.submit(info, path, root))
        while pending:
            entry = pending.popleft().result()
            if progress is not None:
                progress.bytes += entry['bytes']
            yield entry
            path = next(paths, None)
            if path is not None:
                pending.append(pool.submit(info, path, root))
    finally:
        # At most eight current file reads survive an alarm/error; never queue
        # an entire release's hashes behind a debug allocation's deadline.
        pool.shutdown(wait=True, cancel_futures=True)



def offline():
    if any(os.environ.get(v) for v in AUTH):
        raise ValueError('credential-free CPU process requires authentication variables absent')
    os.environ.update(HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1',
                      OMP_NUM_THREADS='1', ARROW_NUM_THREADS='1')
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)


def forbidden(key):
    return bool(re.search(r'licen[cs]e|licen[cs]ing|copyright|(?:^|_)rights(?:_|$)', key, re.I))


def sanitize(value):
    """Also sanitize JSON inside strings; source metadata frequently uses *_json."""
    if isinstance(value, dict):
        return {k: sanitize(v) for k, v in value.items() if not forbidden(k) and k not in PRIVATE
                and not isinstance(v, (bytes, bytearray, memoryview))}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, Decimal):
        return int(value) if value.is_finite() and value == value.to_integral_value() else float(value) if value.is_finite() else None
    if isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        try:
            return canonical(sanitize(json.loads(value)))
        except (ValueError, TypeError):
            pass
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def assert_clean(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if forbidden(k) or k in PRIVATE:
                raise ValueError('removed public field: ' + k)
            assert_clean(v)
    elif isinstance(value, list):
        for v in value:
            assert_clean(v)
    elif isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        try:
            parsed = json.loads(value)
        except ValueError:
            return
        assert_clean(parsed)


def atomic_json(path, value, cap=CAP):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    b = (canonical(value) + '\n').encode()
    if len(b) > cap:
        raise ValueError('singleton exceeds cap; use record parts: ' + str(p))
    tmp = p.with_name(p.name + '.partial')
    with tmp.open('wb') as f:
        f.write(b)
        f.flush()
        os.fsync(f.fileno())
    if tmp.stat().st_size > cap:
        raise ValueError('closed file exceeds cap')
    tmp.replace(p)


def get(row, path, default=None):
    value = row
    for name in path.split('.'):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                return default
        if isinstance(value, list) and name.isdecimal():
            value = value[int(name)] if int(name) < len(value) else None
        elif isinstance(value, dict):
            value = value.get(name)
        else:
            return default
    return default if value is None else value


def mapped(row, spec):
    result = sanitize(row)
    result.update(spec.get('constants', {}))
    for dest, src in spec.get('fields', {}).items():
        result[dest] = get(row, src)
    for dest, template in spec.get('templates', {}).items():
        result[dest] = template.format_map(result)
    return sanitize(result)


def records(path, spec=None):
    """Selectors are explicit for JSON arrays/maps. Never follow receipt paths."""
    spec = spec or {}
    p = Path(path)
    if p.suffix == '.parquet':
        for batch in pq.ParquetFile(p).iter_batches(batch_size=spec.get('batch_size', 128), columns=spec.get('columns'), use_threads=False):
            yield from batch.to_pylist()
    elif p.name.endswith(('.jsonl', '.jsonl.gz', '.ndjson')):
        opener = gzip.open if p.suffix == '.gz' else open
        with opener(p, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
    else:
        prefix = spec.get('json_prefix', '')
        if prefix or spec.get('json_map'):
            from .probe_sources import json_records
            yield from json_records(p, prefix, bool(spec.get('json_map')))
        else:
            if p.stat().st_size > 32_000_000:
                raise ValueError('large JSON needs explicit json_prefix/json_map: ' + str(p))
            value = json.loads(p.read_text())
            if not isinstance(value, dict):
                raise ValueError('JSON root arrays require explicit json_prefix=item')
            yield value


def dimensions(b):
    """PNG/JPEG/GIF headers only. No image library or decoder is used."""
    if b[:8] == b'\x89PNG\r\n\x1a\n' and len(b) >= 24:
        return struct.unpack('>II', b[16:24])
    if b[:6] in (b'GIF87a', b'GIF89a'):
        return struct.unpack('<HH', b[6:10])
    if b[:2] == b'\xff\xd8':
        f = io.BytesIO(b)
        f.seek(2)
        while True:
            v = f.read(1)
            if not v:
                break
            if v != b'\xff':
                continue
            while v == b'\xff':
                v = f.read(1)
            if not v:
                break
            marker = v[0]
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            size = struct.unpack('>H', f.read(2))[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                _, h, w = struct.unpack('>BHH', f.read(5))
                return w, h
            if size < 2:
                break
            f.seek(size - 2, 1)
    raise ValueError('unsupported or invalid image header; bytes were not decoded')


def row_key(parent, row):
    if parent is None or row is None:
        raise ValueError('missing original parent/row identity; supply explicit fields mapping')
    return digest(canonical([parent, row]))


def safe_path(root, rel, *, allow_hf_cache=False):
    p = Path(rel)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('unsafe relative path')
    root = Path(root).resolve()
    target = root / p
    resolved = target.resolve()
    if allow_hf_cache:
        # Only this repository cache's blobs may sit outside its snapshot.
        # A materialised root still confines every file to itself.
        boundary = root.parent.parent / 'blobs' if root.parent.name == 'snapshots' else root
        if root not in resolved.parents and boundary not in resolved.parents:
            raise ValueError('path escapes root/cache blobs')
        return resolved
    if target.is_symlink() or root not in resolved.parents:
        raise ValueError('path escapes root')
    return target


def verify_file(entry):
    p = Path(entry['path'])
    if p.is_symlink() or not p.is_file():
        raise ValueError('missing/symlink locked input: ' + str(p))
    if p.stat().st_size != entry['bytes'] or sha(p) != entry['sha256']:
        raise ValueError('locked input changed: ' + str(p))


class Assets:
    """Only hash-locked files or members of hash-locked TARs may be opened."""
    def __init__(self, lock):
        self.files = {str(Path(e['path']).resolve()): e for e in lock['assets']}
        self.read = set()

    def payload(self, path, member=None):
        p = str(Path(path).resolve())
        if p not in self.files:
            raise ValueError('payload is not in INPUT_LOCK.assets: ' + p)
        if p not in self.read:
            verify_file(self.files[p])
            self.read.add(p)
        if member is None:
            return Path(p).read_bytes()
        if Path(member).is_absolute() or '..' in Path(member).parts:
            raise ValueError('unsafe TAR member')
        with tarfile.open(p, 'r:*') as tar:
            entry = tar.getmember(member)
            if not entry.isfile():
                raise ValueError('TAR member is not a regular file')
            with tar.extractfile(entry) as f:
                return f.read()


IMAGE = pa.struct([('bytes', pa.binary()), ('path', pa.string())])
S = pa.string()
I = pa.int64()
B = pa.bool_()
F = pa.float64()
LS = pa.list_(S)
LI = pa.list_(I)


def schema(name):
    aliases = {'lines': 'rows', 'labels_current': 'label_versions',
               'current_features': 'row_features', 'synthetic_lines': 'synthetic',
               'crops': 'page_images'}
    if name in aliases:
        base = schema(aliases[name])
        excluded = set()
        if name == 'lines':
            excluded = set(schema('row_features').names) - {'row_key', 'record_json', 'source_locator', 'source_sha256', 'binding_missing_reasons_json', 'coordinate_frame'}
            excluded |= {'text', 'raw_text', 'raw_text_sha256', 'gt_nfc', 'gt_nfd', 'label_ids', 'codec_version', 'label_sha256', 'label_version', 'trainer_variants', 'corrections_applied', 'correction_route_statuses', 'corrections_applied_json', 'correction_route_statuses_json'}
        if name == 'synthetic_lines':
            excluded = {'image'}
        if name == 'crops':
            result = schema('page_images').append(pa.field('crop_sha256', pa.string()))
            metadata = json.loads(result.metadata[b'huggingface'])
            metadata['info']['features']['crop_sha256'] = {'_type': 'Value', 'dtype': 'string'}
            return result.with_metadata({b'huggingface': canonical(metadata).encode()})
        return pa.schema([f for f in base if f.name not in excluded])
    """Stable HF schemas; arbitrary retained source fields live in record_json."""
    fields = {}
    def add(names, typ=S):
        fields.update((n, typ) for n in names.split())
    add('record_json source_locator source_sha256')
    add('source_page_id source_page_namespace source_page_references_json binding_missing_reasons_json '
        'source_box_id source_page_frame_id source_segmenter_run_id')
    if name in ('boxes', 'page_images', 'page_frames', 'segmenter_page_results'):
        add('page page_number_convention')
    if name in ('real', 'rows'):
        add('id parent_id row_id row_key page_id page_frame_id box_id crop_id book_id canonical_book_id edition_id wave release '
            'crop_sha256 training_image_sha256 coordinate_frame frame_status box_kind segmenter segmenter_run_id '
            'text gt_nfc gt_nfd codec_version label_version label_sha256 raw_text raw_text_sha256 split source_book_id '
            'source_split split_reason split_resolution_json assignment_status book_registry_sha256 decision primary_class pool trainer_line_id '
            'feature_version pixel_variant evaluation_role original_custody source_record_json source_missing_reasons_json '
            'corrections_applied_json correction_route_statuses_json crops_json release_memberships_json '
            'crop_bbox polygon_px polygon_norm corrections_applied correction_route_statuses source_record source_missing_reasons source_record_locator decision_reasons census_disposition census_reasons')
        add(' '.join(SOURCE_FIELDS))
        add('book_bridge_status book_bridge_candidates_json book_bridge_evidence_json book_source_candidates_json '
            'row_instruments_sha256 row_instrument_status row_instrument_missing_reason '
            'source_canonical_book_id source_native_record_json source_record_hash_basis '
            'source_decision_book_id book_id_conflict_reason book_id_resolution_json')
        add('harvest_protection lqb_row release_excluded_row split_conflict book_id_conflict', B)
        add('emitted_index reading_order top_index width height', I)
        add('label_ids', LI)
        add('trained_in', LS)
        add('language_guess language_guess_method crop_variant feature_provenance_json')
        add('length_chars length_raw_codepoints nonspace_chars crop_width_px crop_height_px', I)
        add('polytonic_marks_present numbers_present all_caps has_capitals mixed_script', B)
        add('named_scripts', LS)
        add('language_guess_confidence crop_aspect x_center_norm y_center_norm', F)
        for bucket in ('greek', 'latin', 'cyrillic', 'digits', 'punctuation', 'other'):
            add(bucket + '_count', I)
            add(bucket + '_pct', F)
        if name == 'real':
            add('image trainer_image', IMAGE)
            add('trainer_variants', pa.list_(pa.struct([
                ('pool', S), ('trainer_line_id', S), ('variant', S), ('image', IMAGE),
                ('image_sha256', S), ('gt_nfc', S), ('gt_nfd', S), ('label_ids', LI),
                ('codec_version', S), ('width', I), ('height', I)])))
        else:
            add('trainer_variants')
    elif name == 'synthetic':
        add('book_id canonical_book_id book_registry_sha256 book_bridge_status book_bridge_candidates_json '
            'book_bridge_evidence_json book_source_candidates_json source_missing_reasons_json row_instruments_sha256 '
            'row_instrument_status row_instrument_missing_reason source_book_id source_canonical_book_id '
            'source_native_record_json source_record_json source_record_hash_basis')
        add(' '.join(SOURCE_FIELDS))
        add('lqb_row release_excluded_row', B)
        add('synthetic_key source_shard synthetic_match_group key_collision_group '
            'line_id split factory_build_id source_build image_sha256 text gt_nfc gt_nfd codec_version script_class '
            'source_dataset source_doc_id text_source_locator text_sha256 font font_file_sha256 font_sha16 polarity '
            'bg_type generator_code_sha256 generator_binary_sha256 recipe_name recipe_sha256 recipe_effective_sha256 '
            'provenance_completeness historical_unknown_fields_json historical_unknown_fields provenance_computed_json provenance_recovered_json '
            'synthetic_native_attributes_json')
        add('reuse_index source_ordinal key_collision_size width height severity n_ops', I)
        add('accent_survival', F)
        add('label_ids', LI)
        add('trained_in applied_ops', LS)
        add('image', IMAGE)
    elif name == 'training_membership':
        add('membership_id model_id role pool trainer_line_id variant row_key factory_build_id source_build '
            'image_sha256 label_sha256 gt_nfc gt_nfd codec_version source_shard run_binding_sha256 '
            'sampler_json selection_role draw_status synthetic_key synthetic_match_group synthetic_mapping_status image_variant label_variant payload_locator source_sha256 reference_id membership_kind missing_reasons')
        add('reuse_index source_ordinal pool_order draw_count synthetic_candidate_count', I)
        add('available eligible drawn selection evaluation', B)
        add('label_ids', LI)
    elif name == 'pages':
        add('page_id book_id canonical_book_id edition_id split source_namespace source_page_id '
            'provider_item_id physical_page_number page_slot page_number_convention acquisition_status '
            'acquisition_reason image_sha256 page_object_id frame_version source_record_json')
        add('width height', I)
    elif name == 'page_images':
        add('page_object_id image_sha256 page_id image_format')
        add('image', IMAGE)
        add('width height', I)
        add('auxiliary', B)
    elif name == 'page_frames':
        add('page_frame_id page_id response_object_id coordinate_frame frame_status mapping_status '
            'docai_dimension docai_transforms docai_image_metadata mapping_evidence transform inverse_transform '
            'sanitized_record_locator sanitized_record_sha256')
        add('docai_page_index raster_width raster_height', I)
    elif name == 'boxes':
        add('box_id page_id segmenter segmenter_run_id geometry_kind page_frame_id coordinate_frame frame_status '
            'polygon_px polygon_norm bbox_px bbox_norm raw_polygon_px raw_polygon_norm text_anchor orientation '
            'confidence_scope language_scope contributors source_box_ids crop_ids detected_languages '
            'response_object_id response_stored_sha256 response_original_sha256 geometry_transform_json')
        add('emitted_item_index reading_order raw_page_index raw_line_index line_index_from_top', I)
        add('confidence', F)
    elif name == 'segmenter_page_results':
        add('page_id segmenter_run_id status reason code_sha256 model_sha256 config_sha256 input_frame '
            'requested_manifest_sha256 outcome_evidence_json')
        add('box_count', I)
    elif name == 'book_registry':
        add('book_id canonical_book_id split assignment_status aliases assignments identity_provenance '
            'split_labels source_split split_resolution_ruling registry_sha256 unassigned_reason')
        add('exportable harvest_protection conflict', B)
    elif name == 'book_sources':
        add('book_id registry_sha256 source_record_id fields evidence')
    elif name == 'row_instruments':
        add('row_key row_id kind list_name list_sha256 declaration_path declaration_locator')
    elif name == 'references':
        add('reference_id instrument view split row_key line_id image_variant label_variant payload_locator '
            'label_version exposure_notes source_manifest_sha256 selection_role image_sha256 label_sha256')
        add('diagnostic_only', B)
        add('ordinal', I)
    elif name == 'label_versions':
        add('label_version_id row_key label_variant producer producer_version text text_sha256 before_sha256 route_status reason normalization raw_text_field '
            'gt_nfc gt_nfd codec_version correction_bindings route_statuses')
        add('label_ids', LI)
    elif name == 'row_features':
        add('row_key label_variant label_version_id feature_version label_sha256 language_guess language_guess_method '
            'crop_variant pixel_variant coordinate_frame feature_provenance_json provider_languages '
            'language_scope ocr_confidence_scope census_primary_class source_script_class')
        add('length_chars length_raw_codepoints nonspace_chars crop_width_px crop_height_px line_index_from_top', I)
        add('polytonic_marks_present numbers_present all_caps has_capitals mixed_script', B)
        add('named_scripts', LS)
        add('language_guess_confidence ocr_confidence crop_aspect x_center_norm y_center_norm', F)
        for bucket in ('greek', 'latin', 'cyrillic', 'digits', 'punctuation', 'other'):
            add(bucket + '_count', I)
            add(bucket + '_pct', F)
    else:
        raise ValueError('unknown public relation: ' + name)
    result = pa.schema(list(fields.items()))
    def feature(t, name=''):
        if name in ('image', 'trainer_image'):
            return {'_type': 'Image'}
        if pa.types.is_struct(t):
            return {f.name: feature(f.type, f.name) for f in t}
        if pa.types.is_list(t):
            if pa.types.is_struct(t.value_type):
                # HF's legacy one-element list notation preserves list<struct>;
                # Sequence(dict) instead transposes it to a struct of lists.
                return [feature(t.value_type)]
            return {'_type': 'Sequence', 'feature': feature(t.value_type)}
        return {'_type': 'Value', 'dtype': {S: 'string', I: 'int64', B: 'bool', F: 'float64', pa.binary(): 'binary'}[t]}
    metadata = {'info': {'features': {f.name: feature(f.type, f.name) for f in result}}}
    return result.with_metadata({b'huggingface': canonical(metadata).encode()})


def project(row, name):
    result = {}
    for f in schema(name):
        value = row.get(f.name)
        if value is not None and pa.types.is_string(f.type) and not isinstance(value, str):
            value = canonical(value)
        result[f.name] = value
    # A complete sanitized record prevents a narrow Arrow projection losing provenance.
    retained = {k: v for k, v in row.items() if k not in ('image', 'trainer_image', 'record_json')}
    retained['source_locator_scope'] = 'historical input; not a publicly fetchable payload'
    retained['public_record_locator'] = {'index': 'manifests/CONFIGS.json', 'config': name,
        'key': {k: row[k] for k in ('row_key', 'page_id', 'page_object_id', 'box_id', 'book_id',
                                  'synthetic_key', 'source_shard', 'source_ordinal',
                                  'line_id', 'factory_build_id', 'reuse_index', 'label_version_id',
                                  'membership_id', 'reference_id') if row.get(k) is not None}}
    result['record_json'] = canonical(sanitize(retained))
    assert_clean(result)
    return result


class Shards:
    """Bounded buffers, closed-file size checks, recursively split oversized parts."""
    def __init__(self, root, name, directory, cap=CAP, target=TARGET, checkpoints=None, stream_resume=False):
        self.root, self.name, self.directory = Path(root), name, directory
        self.cap, self.target = cap, min(target, cap)
        self.outputs = []
        self.buffer, self.weight = [], 0
        self.pages = set()
        self.checkpoints = Path(checkpoints) if checkpoints else None
        self.stream_checkpoint = self.checkpoints / (digest('stream:' + directory) + '.json') if checkpoints and stream_resume else None
        self.committed_rows = 0
        if self.stream_checkpoint and self.stream_checkpoint.exists():
            saved = json.loads(self.stream_checkpoint.read_text())
            self.outputs = saved['files']
            self.committed_rows = saved['rows']
            for entry in self.outputs:
                verify_file({**entry, 'path': str(safe_path(self.root, entry['path']))})

    def add(self, row):
        from .progress import active
        progress = active.get()
        if progress is not None:
            progress.rows += 1
        row = project(row, self.name)
        size = len(row['record_json'].encode()) + sum(len((row.get(k) or {}).get('bytes') or b'')
                                                     for k in ('image', 'trainer_image')) + 4096
        if isinstance(row.get('trainer_variants'), list):
            size += sum(len((v.get('image') or {}).get('bytes') or b'') for v in row['trainer_variants'])
        page = row.get('page_id')
        if self.buffer and (self.weight + size > self.target or
                            len(self.buffer) >= 16384 and self.name not in ('real', 'synthetic', 'page_images', 'crops') or
                            page and page not in self.pages and len(self.pages) >= 100):
            self.flush()
        self.buffer.append(row)
        self.weight += size
        if page:
            self.pages.add(page)

    def flush(self):
        if not self.buffer:
            return
        from .deadline import atomic_boundary
        self._emit(pa.Table.from_pylist(self.buffer, schema=schema(self.name)))
        with atomic_boundary():
            self.committed_rows += len(self.buffer)
            if self.stream_checkpoint:
                atomic_json(self.stream_checkpoint, {'files': self.outputs, 'rows': self.committed_rows})
            self.buffer, self.weight, self.pages = [], 0, set()

    def _emit(self, table):
        rel = f'{self.directory}/part-{len(self.outputs):06d}.parquet'
        path = safe_path(self.root, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        def logical(value):
            if isinstance(value, bytes):
                return {'binary_sha256': digest(value), 'bytes': len(value)}
            if isinstance(value, dict):
                return {k: logical(v) for k, v in value.items()}
            if isinstance(value, list):
                return [logical(v) for v in value]
            return value
        batch_digest = digest(canonical(logical(table.to_pylist()))) if self.checkpoints else None
        checkpoint = self.checkpoints / (digest(rel) + '.json') if self.checkpoints else None
        if checkpoint and checkpoint.exists():
            receipt = json.loads(checkpoint.read_text())
            if receipt['logical_sha256'] == batch_digest and path.exists():
                verify_file({**receipt['file'], 'path': str(path)})
                self.outputs.append(receipt['file'])
                return
        tmp = path.with_suffix('.parquet.partial')
        pq.write_table(table, tmp, compression='zstd', use_dictionary=False, row_group_size=1024,
                       use_content_defined_chunking=True)
        size = tmp.stat().st_size
        if size > self.cap:
            tmp.unlink()  # Only this writer's uncommitted temporary output.
            if table.num_rows < 2:
                raise ValueError('single record exceeds closed-file cap: ' + self.name)
            middle = table.num_rows // 2
            self._emit(table.slice(0, middle))
            self._emit(table.slice(middle))
        else:
            tmp.replace(path)
            entry = {**info(path, self.root), 'rows': table.num_rows}
            self.outputs.append(entry)
            if checkpoint:
                atomic_json(checkpoint, {'logical_sha256': batch_digest, 'file': entry})

    def close(self):
        self.flush()
        if not self.outputs:
            self._emit(pa.Table.from_pylist([], schema=schema(self.name)))
        return self.outputs
