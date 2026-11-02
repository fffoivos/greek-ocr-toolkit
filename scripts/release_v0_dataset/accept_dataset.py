#!/usr/bin/env python3
"""Independent offline readback of a local build or a disjoint downloaded copy.

Full acceptance requires the pinned source lock and source files. Without sources,
the result is explicitly a package self-check, not source/production acceptance.
Release acceptance is `--final` on a complete download: it also executes the
card's literal join recipe and a pyarrow emulation of every README-declared
config, and runs the enrichment hook when ENRICH_RECEIPT.json is present. Only a
final run can report PASS for a layered package.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import sqlite3
import struct
import sys
import tempfile
import traceback
import unicodedata as ud
import zlib

sys.dont_write_bytecode = True
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
import pyarrow.parquet as pq
from .common import (Assets, CAP, PINS, PRIVATE, SOURCE_FIELDS, SYNTHETIC_MATCH_FIELDS, TABLES, assert_clean, atomic_json,
                     canonical, digest, get, mapped, offline, pending_resolvers, records, safe_path,
                     sanitize, sha, verify_file)

from .relations import dependencies, consumer_record, contextual, diagnostic, failure, origin
from .accept_bindings import A12_FIELDS, BindingPolicy
from .book_bridge import (BookBridge, adopted_registry, adopted_train_assignment,
                          count_coverage, metadata, new_coverage)

from .original_crops import CropIndex, eligible as crop_eligible, build_file_index, custody_kind
from .original_inputs import OriginalPayloads, selected_records
from .validation_originals import ValidationOriginals

VALIDATION_MODES = ('external-cache', 'complete-download', 'complete-download-a1-source')
KEYS = {'pages': ['page_id'], 'page_images': ['page_object_id'], 'page_frames': ['page_frame_id'],
        'boxes': ['box_id'], 'segmenter_page_results': ['segmenter_run_id', 'page_id'],
        'rows': ['row_key'], 'label_versions': ['label_version_id'],
        'row_features': ['row_key', 'label_variant', 'feature_version'],
        'row_instruments': ['row_key', 'kind', 'list_name', 'list_sha256'],
        'training_membership': ['membership_id'],
        'references': ['reference_id'], 'book_registry': ['book_id'],
        'book_sources': ['book_id', 'source_locator'],
        'real': ['row_key'], 'synthetic': ['factory_build_id', 'split', 'source_shard', 'source_ordinal']}
BUCKETS = ('greek', 'latin', 'cyrillic', 'digits', 'punctuation', 'other')


def require(ok, reason):
    if not ok:
        raise failure(reason)


def as_json(value):
    if isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        return json.loads(value)
    return value


def decode_sample(b):
    """Consumer-only decoding. A small PNG decoder also works without Pillow.

    This has no encoding path and is never imported by the builder.
    """
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is not None:
        import io
        with Image.open(io.BytesIO(b)) as image:
            image.load()
            return image.size
    require(b[:8] == b'\x89PNG\r\n\x1a\n', 'Pillow required for non-PNG consumer decoding')
    position, compressed, header, ended = 8, bytearray(), None, False
    while position < len(b):
        length = struct.unpack('>I', b[position:position + 4])[0]
        kind = b[position + 4:position + 8]
        data = b[position + 8:position + 8 + length]
        crc = struct.unpack('>I', b[position + 8 + length:position + 12 + length])[0]
        require(zlib.crc32(kind + data) & 0xffffffff == crc, 'PNG chunk CRC mismatch')
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', data)
        elif kind == b'IDAT':
            compressed.extend(data)
        elif kind == b'IEND':
            ended = True
            break
        position += length + 12
    require(header is not None and ended, 'incomplete PNG')
    width, height, depth, color, compression, filtering, interlace = header
    require(compression == filtering == interlace == 0, 'Pillow required for interlaced PNG')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    require(channels is not None and depth in (1, 2, 4, 8, 16), 'unsupported PNG color/depth')
    stride = (width * depth * channels + 7) // 8
    bpp = max(1, (depth * channels + 7) // 8)
    raw = zlib.decompress(compressed)
    require(len(raw) == height * (stride + 1), 'PNG decompressed size mismatch')
    previous = bytearray(stride)
    for y in range(height):
        method = raw[y * (stride + 1)]
        require(method <= 4, 'invalid PNG row filter')
        row = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a, above, corner = (row[x - bpp] if x >= bpp else 0), previous[x], (previous[x - bpp] if x >= bpp else 0)
            if method == 1:
                prediction = a
            elif method == 2:
                prediction = above
            elif method == 3:
                prediction = (a + above) // 2
            elif method == 4:
                p = a + above - corner
                distances = [abs(p - a), abs(p - above), abs(p - corner)]
                prediction = [a, above, corner][distances.index(min(distances))]
            else:
                prediction = 0
            row[x] = (row[x] + prediction) & 255
        previous = row
    return width, height


def replay_text(text, languages, atoms, ranges):
    """Independent implementation of the fixed feature definitions.

    No builder feature helper is imported or called. Shared inputs are the
    hash-pinned codec and Unicode Script data, not stored feature outputs.
    """
    def letter(c):
        if not ud.category(c).startswith('L'):
            return None, None
        if c in atoms and atoms[c]['kind'] in ('punct', 'sym', 'space', 'digit'):
            return None, None
        bases = [v for v in ud.normalize('NFD', c) if not ud.category(v).startswith('M')]
        if not bases:
            return None, None
        base = bases[0]
        atom = atoms.get(base)
        if atom:
            if atom['kind'] != 'base':
                return None, None
            name = {'grek': 'Greek', 'latn': 'Latin', 'cyrl': 'Cyrillic'}.get(atom['script'])
        else:
            name = next((v for v in ('Greek', 'Latin', 'Cyrillic') if v.upper() in ud.name(base, '')), None)
        if name:
            return name.lower(), name
        lo, hi = 0, len(ranges)
        code = ord(base)
        while lo < hi:
            mid = (lo + hi) // 2
            if ranges[mid][0] <= code:
                lo = mid + 1
            else:
                hi = mid
        script = ranges[lo - 1][2] if lo and code <= ranges[lo - 1][1] else 'Unknown'
        return 'other', script if script not in ('Common', 'Inherited') else None
    nfc = ud.normalize('NFC', text)
    counts, names = Counter(), set()
    for c in nfc:
        if c.isspace():
            continue
        if ud.category(c) == 'Nd':
            counts['digits'] += 1
        elif ud.category(c).startswith('P') or atoms.get(c, {}).get('kind') == 'punct':
            counts['punctuation'] += 1
        else:
            bucket, script = letter(c)
            counts[bucket or 'other'] += 1
            if script:
                names.add(script)
    poly, last_base = False, None
    for c in ud.normalize('NFD', text):
        if ud.category(c).startswith('M'):
            if last_base == 'greek' and c in '\u0313\u0314\u0342\u0345\u0300':
                poly = True
        else:
            last_base = letter(c)[0]
    denominator = sum(not c.isspace() for c in nfc)
    result = {'length_chars': len(nfc), 'length_raw_codepoints': len(text), 'nonspace_chars': denominator,
              'polytonic_marks_present': poly, 'numbers_present': counts['digits'] > 0,
              'has_capitals': any(ud.category(c) in ('Lu', 'Lt') for c in text),
              'all_caps': bool([c for c in text if c.lower() != c.upper()]) and not any(c.islower() for c in text),
              'mixed_script': len(names) >= 2, 'named_scripts': sorted(names)}
    for bucket in BUCKETS:
        result[bucket + '_count'] = counts[bucket]
        result[bucket + '_pct'] = counts[bucket] * 100.0 / denominator if denominator else 0.0
    language_values = []
    for entry in languages:
        if entry.get('languageCode'):
            confidence = entry.get('confidence')
            confidence = float(confidence) if confidence is not None and math.isfinite(float(confidence)) else None
            language_values.append((entry['languageCode'], confidence))
    if language_values:
        best = sorted(language_values, key=lambda v: (-(v[1] if v[1] is not None else -math.inf), v[0]))[0]
        result.update(language_guess=best[0], language_guess_confidence=best[1], language_guess_method='google_detectedLanguages')
    else:
        guess = 'mul' if len(names) > 1 else {'Greek': 'el', 'Latin': 'und-Latn', 'Cyrillic': 'und-Cyrl'}.get(next(iter(names), ''), 'und')
        result.update(language_guess=guess, language_guess_confidence=None, language_guess_method='script-tag-v1')
    return result


class Acceptance:
    def __init__(self, root, scratch, input_lock=None, allow_smoke=False, resume=False,
                 validation_mode='complete-download', final=False, enrich_base=None):
        require(validation_mode in VALIDATION_MODES, 'invalid validation mode')
        self.validation_mode = validation_mode
        # complete-download verifies the frozen view from the packaged A1.json and the
        # public occurrence mapping; complete-download-a1-source also replays the
        # external source A1 receipt (stronger, source-side).
        self.complete_download = validation_mode != 'external-cache'
        require(not final or self.complete_download, 'final acceptance requires a complete download')
        self.final = final
        self.enrich_base = enrich_base
        self.root = Path(root).resolve()
        scratch = Path(scratch).resolve()
        require(not (scratch == self.root or self.root in scratch.parents), 'readback scratch overlaps public package')
        scratch.mkdir(parents=True, exist_ok=True)
        require(resume or not (scratch / 'accept.sqlite').exists(), 'existing readback requires resume')
        self.db = sqlite3.connect(scratch / 'accept.sqlite')
        if not resume or not self.db.execute("SELECT 1 FROM sqlite_master WHERE name='r'").fetchone():
            self.db.executescript('''CREATE TABLE r(t TEXT,k TEXT,j TEXT,PRIMARY KEY(t,k));
                CREATE INDEX r_row ON r(t,json_extract(j,'$.row_key'));
                CREATE INDEX r_pool ON r(t,json_extract(j,'$.pool'),json_extract(j,'$.model_id'));
                CREATE INDEX r_synthetic_match ON r(t,json_extract(j,'$.synthetic_match_group'));
                CREATE INDEX r_synthetic_legacy ON r(t,json_extract(j,'$.legacy_key_group'));
                CREATE INDEX r_source_position ON r(t,json_extract(j,'$.source_shard'),json_extract(j,'$.source_ordinal'));
                CREATE TABLE sets(s TEXT,k TEXT,j TEXT,PRIMARY KEY(s,k));
                CREATE TABLE source_sets(s TEXT,k TEXT,PRIMARY KEY(s,k));
                CREATE TABLE source_tuples(s TEXT,k TEXT,row_key TEXT,PRIMARY KEY(s,k));''')
        self.lock_path = input_lock
        self.allow_smoke = allow_smoke
        self.image_count = 0
        self.source_checks = 0
        self.binding_source_checks = 0
        from .readback_state import Ledger
        try:
            self.ledger = Ledger(self, scratch)
        except BaseException:
            self.db.close()
            raise

    def transaction_boundary(self, key):
        # Fault-injection seam: called only after durable SQLite commits.
        pass

    def verify_file(self, entry):
        self.ledger.verify_many([entry])

    def parquet_units(self, stage, paths, *, root=None):
        from .readback_state import parquet_files
        from .frozen_identity import public_file
        pending = []
        for path in paths:
            if not self.ledger.saved(stage + ':' + path):
                pending.append(path)
        physical = [public_file(root, p) if root is not None else safe_path(self.root, p) for p in pending]
        for relative, (path, rows) in zip(pending, parquet_files(physical)):
            with self.ledger.unit(stage + ':' + relative) as run:
                if run:
                    yield relative, rows

    def checked_items(self, stage, table, partner=False, state=None):
        # Keyset checkpoints for row-local checks, including policy counters.
        if not getattr(self, '_ledger_running', False):
            yield from (self.partner_items(table) if partner else self.items(table))
            return
        token = 'rows:' + stage + ':' + table
        saved = self.ledger.saved(token)
        if saved and state is not None:
            from .readback_state import restore
            updated = restore(state, saved['state'].get('local', {}))
            state.clear(); state.update(updated)
        if saved and saved['state'].get('done'):
            return
        last = saved['state']['last'] if saved else ''
        count = 0
        for key, raw in self.db.execute('SELECT k,j FROM r WHERE t=? AND k>? ORDER BY k', (table, last)):
            self.ledger.deadline.check()
            row = json.loads(raw)
            source, adapter = origin(self.lock, row, table)
            with diagnostic(source, adapter, key):
                consumer_record(source, adapter, key)
                valid = True
                if partner:
                    for target, pk in dependencies(table, row):
                        if self.fk_value(table, target, pk) and self.partner_lookup(target, pk) is None:
                            require(self.smoke_skip_allowed(table, key, target, pk),
                                    f'{table} → {target} FK fails: target missing {canonical(pk)[:160]}')
                            valid = False
                if valid:
                    yield key, row
                consumer_record()
            last, count = key, count + 1
            if count % 256 == 0:
                self.ledger.save(token, {'last': last, 'done': False, 'local': state or {}})
        self.ledger.save(token, {'last': last, 'done': True, 'local': state or {}})

    def items(self, table):
        for key, j in self.db.execute('SELECT k,j FROM r WHERE t=? ORDER BY k', (table,)):
            row = json.loads(j)
            source, adapter = origin(getattr(self, 'lock', {'inputs': []}), row, table)
            with diagnostic(source, adapter, key):
                consumer_record(source, adapter, key)
                yield key, row
                # Normal advancement/exhaustion clears the record. If the
                # consumer raises, contextual() retains it while unwinding.
                consumer_record()

    def find(self, table, values):
        j = self.db.execute('SELECT j FROM r WHERE t=? AND k=?', (table, canonical(values))).fetchone()
        return json.loads(j[0]) if j else None

    def smoke_skip_allowed(self, table, record_key, target, partner):
        if not self.allow_smoke or self.receipt['mode'] != 'smoke':
            return False
        if not hasattr(self, '_smoke_skip_keys'):
            self._smoke_skip_keys = set()
            observed = defaultdict(Counter)
            seen = set()
            for path in sorted((self.root / 'manifests/smoke_unloaded_targets').glob('*.jsonl.gz')):
                with gzip.open(path, 'rt') as stream:
                    for line in stream:
                        event = json.loads(line)
                        token = (event['table'], event['key'], event['target'], event['partner'])
                        witness = (event['source'], event['adapter'], *token)
                        require(witness not in seen, 'duplicate smoke skip witness')
                        seen.add(witness)
                        self._smoke_skip_keys.add(token)
                        observed[event['source']][event['adapter']] += 1
            counts = {s: dict(a) for s, a in observed.items()}
            coverage = json.loads((self.root / 'manifests/COVERAGE.json').read_text())
            require(counts == coverage.get('smoke_unloaded_targets', {}) == self.receipt.get('smoke_unloaded_targets', {}),
                    'smoke unloaded-target counts differ from witnesses')
        return (table, canonical(record_key), target, canonical(partner)) in self._smoke_skip_keys

    def partner_lookup(self, table, key):
        if table == 'synthetic_group_count':
            count = self.db.execute("SELECT COUNT(*) FROM r WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=?",
                                    (key[0],)).fetchone()[0]
            return count if count >= key[1] else None
        if table == 'synthetic_group':
            return self.db.execute("SELECT 1 FROM r WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=?", key).fetchone()
        return self.find(table, key)

    def partner_items(self, table):
        for key, row in self.items(table):
            valid = True
            for target, partner in dependencies(table, row):
                if not self.fk_value(table, target, partner):
                    continue
                if self.partner_lookup(target, partner) is None:
                    require(self.smoke_skip_allowed(table, key, target, partner),
                            f'{table} → {target} FK fails: target missing {canonical(partner)[:160]}')
                    valid = False
            if valid:
                yield key, row

    def fk_value(self, table, target, key):
        binding = self.policy.fk_binding(table, target)
        value = key if all(k is not None for k in key) else None
        return self.policy.value(binding, table + ' → ' + target + ' FK', value, count=False)

    def partner(self, table, record_key, target, key):
        if not self.fk_value(table, target, key):
            return None
        row = self.find(target, key)
        if row is None:
            require(all(k is not None for k in key), f'{table} → {target} FK fails: null partner key')
            require(self.smoke_skip_allowed(table, record_key, target, key),
                    f'{table} → {target} FK fails: target missing {canonical(key)[:160]}')
        return row

    @contextual
    def byte_check(self):
        manifest_path = self.root / 'manifests/MANIFEST.json'
        manifest = json.loads(manifest_path.read_text())
        assert_clean(manifest)
        require(0 < manifest['file_cap'] <= CAP, 'invalid manifest file cap')
        inventory = {entry['path']: entry for entry in manifest['files']}
        require(len(inventory) == len(manifest['files']), 'duplicate manifest paths')
        actual = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()}
        frozen = manifest.get('frozen_trained', {})
        local_frozen = self.complete_download or not frozen.get('public_snapshot_root')
        frozen_paths = {e['path'] for e in frozen.get('files', [])} if local_frozen else set()
        retained = manifest.get('retained_public', [])
        from .release_tree import retained_public
        require(retained == retained_public(frozen), 'retained public inventory differs from reviewed tree')
        if self.complete_download:
            frozen_paths.update(e['path'] for e in retained)
        expected = set(inventory) | {'manifests/MANIFEST.json', 'manifests/SHA256SUMS'} | frozen_paths
        # A seal is an external inventory and not part of its own hash cycle.
        if (self.root / 'C_MANIFEST.json').exists():
            expected.add('C_MANIFEST.json')
        require(actual == expected, 'manifest path coverage differs: ' + str(sorted(actual ^ expected)[:10]))
        require(not any(p.is_symlink() for p in self.root.rglob('*')), 'symlink in public package')
        for path in inventory:
            require(safe_path(self.root, path).stat().st_size <= manifest['file_cap'], 'closed file cap exceeded: ' + path)
        self.ledger.verify_many({**entry, 'path': str(safe_path(self.root, path))}
                                for path, entry in inventory.items())
        sums = {}
        for line in (self.root / 'manifests/SHA256SUMS').read_text().splitlines():
            h, path = line.split('  ', 1)
            require(path not in sums, 'duplicate checksum path')
            sums[path] = h
        require(set(sums) == set(inventory) | {'manifests/MANIFEST.json'}, 'checksum coverage differs')
        require(sums['manifests/MANIFEST.json'] == sha(manifest_path), 'manifest checksum mismatch')
        require(all(sums[p] == e['sha256'] for p, e in inventory.items()), 'checksum and manifest disagree')
        for p in (manifest_path, self.root / 'manifests/SHA256SUMS'):
            require(p.stat().st_size <= manifest['file_cap'], 'closed singleton cap exceeded')
        if self.complete_download:
            self.ledger.verify_many({**entry, 'path': str(safe_path(self.root, entry['path']))}
                                    for entry in frozen.get('files', []) + retained)
        self.manifest = manifest
        self.lock = json.loads((self.root / 'manifests/INPUT_LOCK.json').read_text())
        self.receipt = json.loads((self.root / 'manifests/BUILD_RECEIPT.json').read_text())
        self.policy = BindingPolicy(self.lock, self.receipt['mode'] == 'smoke')
        self.coverage = json.loads((self.root / 'manifests/COVERAGE.json').read_text())
        require(self.lock['hf_pins'] == PINS, 'incorrect archive pins')
        require(self.allow_smoke or self.receipt['mode'] == 'full', 'smoke cannot pass release acceptance')
        # Scan copied records including JSON-in-string payloads for removed fields.
        for path in inventory:
            p = self.root / path
            if path.endswith('.json'):
                assert_clean(json.loads(p.read_text()))
            elif path.endswith('.jsonl.gz'):
                with gzip.open(p, 'rt') as f:
                    for line in f:
                        assert_clean(json.loads(line))
            elif path.endswith('.md'):
                import re
                require(not re.search(r'^\s*(?:license|licence|rights)\s*:', p.read_text(), re.M | re.I), 'removed card field')
        return len(inventory) + 2

    @contextual
    def load_tables(self):
        if self.manifest.get('layout') == 'layered-v1':
            from .layer_acceptance import load
            return load(self)
        configs = self.manifest['configs']
        require(set(configs) == set(TABLES) | {'real', 'synthetic'}, 'missing/unexpected HF configs')
        require(configs == json.loads((self.root / 'manifests/CONFIGS.json').read_text()), 'config index mismatch')
        card = (self.root / 'README.md').read_text()
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml:
            front = yaml.safe_load(card.split('---', 2)[1])
            parsed = {v['config_name']: {r['split']: r['path'] for r in v['data_files']} for v in front['configs']}
            require(parsed == configs, 'card HF YAML differs from manifest')
            require(next(v for v in front['configs'] if v['config_name'] == 'real').get('default'), 'real is not default')
        for name, splits in configs.items():
            for split, paths in splits.items():
                require(bool(paths), 'empty HF data_files selection')
                require(all(path in {f['path'] for f in self.manifest['files']} for path in paths),
                        'config path not manifested')
                for path in paths:
                    assert_clean({f.name: str(f.type) for f in pq.ParquetFile(safe_path(self.root, path)).schema_arrow})
                for path, outputs in self.parquet_units('flat:' + name + ':' + split, paths):
                    image_samples = defaultdict(list)
                    for output in outputs:
                        assert_clean(output)
                        row = json.loads(output['record_json'])
                        source, adapter = origin(self.lock, row, name)
                        with diagnostic(source, adapter, [row.get(k) for k in KEYS[name]]):
                            for field, value in output.items():
                                if field not in ('record_json', 'image', 'trainer_image', 'trainer_variants') and value is not None:
                                    if field in row and isinstance(row[field], (list, dict)) and isinstance(value, str):
                                        require(canonical(row[field]) == value, 'record/table projection changed: ' + field)
                                        value = row[field]
                                    elif field in row and row[field] is not None:
                                        # Source page/year identifiers may be int, while the public field is string.
                                        require(row[field] == value or str(row[field]) == value, 'record/table projection changed: ' + field)
                                    row[field] = value
                            if name in ('real', 'synthetic'):
                                require(isinstance(row.get('split'), str) and bool(row['split']),
                                        'published row lacks an explicit split; rebuild required')
                                require(row['split'] == split, 'HF split differs from row split')
                            if name == 'real':
                                variants = []
                                for variant in output.get('trainer_variants') or []:
                                    image = variant['image']
                                    require(image is not None and image.get('bytes') is not None, 'consumed variant image missing')
                                    h = hashlib.sha256(image['bytes']).hexdigest()
                                    require(h == variant['image_sha256'], 'consumed variant embedded hash differs')
                                    variants.append({k: v for k, v in variant.items() if k != 'image'})
                                    self.image_count += 1
                                    if len(image_samples[name, 'trainer_variants']) < 4:
                                        image_samples[name, 'trainer_variants'].append(image['bytes'])
                                row['trainer_variants'] = variants
                            elif output.get('trainer_variants'):
                                row['trainer_variants'] = json.loads(output['trainer_variants'])
                            for image_field, hash_field in (('image', 'crop_sha256' if name == 'real' else 'image_sha256'),
                                                           ('trainer_image', 'training_image_sha256')):
                                image = output.get(image_field)
                                if image is None:
                                    continue
                                require(image.get('bytes') is not None and image.get('path') is None, 'nonportable image value')
                                h = hashlib.sha256(image['bytes']).hexdigest()
                                require(h == row.get(hash_field), 'embedded image hash mismatch')
                                row[image_field + '_measured_sha256'] = h
                                if image_field == 'image' and image['bytes'][:8] == b'\x89PNG\r\n\x1a\n':
                                    w, height = struct.unpack('>II', image['bytes'][16:24])
                                    if row.get('width') is not None:
                                        require(row['width'] == w and row.get('height') == height, 'image header dimensions differ')
                                self.image_count += 1
                                if len(image_samples[name, image_field]) < 4:
                                    image_samples[name, image_field].append(image['bytes'])
                            values = [row.get(k) for k in KEYS[name]]
                            require(all(v is not None for v in values), 'null public key: ' + name)
                            try:
                                self.db.execute('INSERT INTO r VALUES(?,?,?)', (name, canonical(values), canonical(row)))
                            except sqlite3.IntegrityError as exc:
                                raise ValueError('duplicate public key: ' + name + ':' + canonical(values)) from exc
                    # Decode before committing this shard's rows and counters.
                    for samples in image_samples.values():
                        for binary in samples:
                            decode_sample(binary)
        for name, expected in self.manifest['logical_key_sha256'].items():
            h = hashlib.sha256()
            n = 0
            for key, _ in self.items(name):
                h.update((key + '\n').encode())
                n += 1
            require(h.hexdigest() == expected and n == self.manifest['counts'][name], 'relation logical key digest/count differs: ' + name)
        try:
            import datasets
        except ImportError:
            self.loader = 'pyarrow: every config/shard reopened; datasets unavailable'
        else:
            for name, splits in configs.items():
                # Streaming uses no writable dataset cache in the candidate/readback tree.
                ds = datasets.load_dataset('parquet', data_files={s: [str(self.root / p) for p in paths]
                                                                 for s, paths in splits.items()}, streaming=True)
                for split in ds:
                    for _ in itertools_first(ds[split]):
                        pass
            self.loader = 'datasets: each config/split opened offline, all shards separately read with pyarrow'

    @contextual
    def binding_checks(self):
        self.policy.nulls.clear()
        for binding, entry in self.policy.entries.items():
            if entry['status'] == 'historical_unknown':
                self.policy.value(binding, 'binding.value', entry.get('value'))
        # Never let a copied coverage declaration silently change the lock.
        for name, group in (('resolved_bindings', 'resolved_bindings'), ('partial_bindings', 'partial_bindings'),
                            ('historical_unknowns', 'unresolved_bindings'),
                            ('pending_resolver_bindings', 'unresolved_bindings')):
            expected = self.lock.get(group, [])
            if group == 'unresolved_bindings':
                expected = ([e for e in expected if e.get('historical_unknown')] if name == 'historical_unknowns'
                            else pending_resolvers(self.lock))
            require(self.coverage.get(name, []) == expected, 'coverage/lock binding differs: ' + name)
        original = self.coverage.get('original_crops', {})
        entry = self.policy.entries.get('assets.original_crops', {})
        if entry.get('coverage'):
            require(original.get('measured_probe') == {
                'populations': entry['coverage'], 'source_report': entry.get('source_report'),
                'source_report_sha256': entry.get('source_report_sha256'),
                'content_index': entry.get('content_index'),
                'validation_originals': entry.get('validation_originals')},
                'original crop measured coverage/lock differs')
            self.policy.original_coverage(original.get('populations', {}))
        for table in ('pages', 'page_frames', 'segmenter_page_results'):
            if self.policy.status('tables.' + table) == 'historical_unknown':
                require(self.db.execute('SELECT 1 FROM r WHERE t=?', (table,)).fetchone() is None,
                        'fabricated historical_unknown table: ' + table)
        for table in ('rows', 'real', 'boxes', 'page_images', 'page_frames', 'segmenter_page_results', 'synthetic', 'row_features'):
            for _, row in self.checked_items('bindings', table):
                for field, binding in self.policy.columns(table).items():
                    # Optional resolved fields keep their pre-existing optional
                    # contract; an explicit status governs nulls everywhere.
                    if binding in self.policy.entries:
                        self.policy.value(binding, table + '.' + field, row.get(field))
                if (table == 'real' or table == 'rows' and row.get('release')) and 'assets.original_crops' in self.policy.entries:
                    measured = row.get('image_measured_sha256') if table == 'real' else (
                        self.find('real', [row['row_key']]) or {}).get('image_measured_sha256')
                    self.policy.original(table + '.original_image', measured, row.get('original_crop_custody'), row.get('crop_sha256'))
                    require(row.get('original_custody') == custody_kind(row.get('original_crop_custody') or {}),
                            'published original custody kind differs')
                    if not measured:
                        require(all(row.get(f) is None for f in ('width', 'height', 'crop_width_px', 'crop_height_px', 'crop_aspect')),
                                'unverified original has fabricated crop dimensions')
                if table in ('rows', 'synthetic') and self.lock.get('book_bridge'):
                    self.book_row_check(table, row)
                if table == 'synthetic':
                    unknown = as_json(row.get('historical_unknown_fields_json')) or {}
                    for field, binding in A12_FIELDS.items():
                        if binding not in self.policy.entries:
                            continue
                        if row.get(field) is None:
                            require(unknown.get(field, {}).get('reason') and unknown[field].get('search_receipt'),
                                    'unexplained synthetic provenance null: ' + field)
        self.ledger.stage('partial_field_checks', self.partial_field_checks)
        self.ledger.stage('book_coverage_check', self.book_coverage_check)
        self.ledger.stage('synthetic_collision_check', self.synthetic_collision_check)
        self.ledger.stage('resolved_coverage_check', self.resolved_coverage_check)

    def enriched(self):
        from .layer_acceptance import ENRICH_RECEIPTS
        return any((self.root / p).is_file() for p in ENRICH_RECEIPTS)

    def enrichment_stage(self):
        """The C′ enrichment hook, cached only under the exact options, base content,
        E1 code and supplementary-source stamps it ran with."""
        from . import layer_acceptance
        identity = {'final': self.final, 'validation_mode': self.validation_mode,
                    'enrichment': layer_acceptance.enrichment_identity(self.root, self.enrich_base)}
        require(identity['enrichment'] == self.ledger.enrichment_identity,
                'enrichment base/code/sources changed during readback')
        return self.ledger.stage('enrichment', lambda: layer_acceptance.enrichment(self, self.enrich_base),
                                 identity=identity)

    def reference_payload_published(self, reference):
        """A C′ reference variant whose bytes are not its row's crop/trainer image.

        Either appended bytes in an enrichment-declared image config (rows enter
        reference_images only from configs ENRICH_RECEIPT lists as appended), or a
        frozen trainer row addressed through the A1 occurrence mapping. The locator
        must name exactly where the bytes are; nothing else is accepted.
        """
        image = reference['image_sha256']
        locator = as_json(reference.get('payload_locator')) or {}
        config = locator.get('config')
        if config == 'reference_images':
            return ((locator.get('key') or {}).get('crop_sha256') == image and
                    self.db.execute('SELECT 1 FROM reference_images WHERE h=?', (image,)).fetchone() is not None)
        if config == 'real' and getattr(self, 'frozen_available', False):
            occurrence = {f['public_path']: f for f in self.manifest.get('frozen_trained', {}).get('occurrence_mapping', [])}
            entry = occurrence.get(locator.get('public_path'))
            ordinal = locator.get('row_ordinal')
            if entry is None or not isinstance(ordinal, int) or locator.get('pool', entry['pool']) != entry['pool']:
                return False
            if locator.get('source_shard_sha256') not in (None, entry['prepared_sha256']):
                return False
            row = self.db.execute('SELECT b FROM frozen WHERE pool=? AND shard=? AND ordinal=?',
                                  (entry['pool'], entry['prepared_path'], ordinal)).fetchone()
            return row is not None and digest(row[0]) == image
        return False

    def resolved_coverage_check(self):
        seal = self.policy.entries.get('seal04.original_rows_and_references', {})
        # A C′ enrichment adds several reference views (seal04 raw, v2 common/full/
        # original_source, validation); seal04 panel rows are the corrected view only.
        # An unenriched C carries only the seal04 panel rows.
        panel = (" AND json_extract(j,'$.instrument')='seal04' AND json_extract(j,'$.view')='corrected'"
                 if self.enriched() else '')
        for split, expected in seal.get('coverage', {}).get('panel_rows', {}).items():
            count = self.db.execute("SELECT COUNT(*) FROM r WHERE t='references' AND json_extract(j,'$.split')=?"
                                    + panel, (split,)).fetchone()[0]
            self.policy.coverage('seal04.panel_rows.' + split, count, expected)
            if panel:
                raw = self.db.execute("SELECT COUNT(*) FROM r WHERE t='references' AND json_extract(j,'$.split')=? "
                                      "AND json_extract(j,'$.instrument')='seal04' AND json_extract(j,'$.view')='raw'",
                                      (split,)).fetchone()[0]
                self.policy.coverage('seal04.raw_view_rows.' + split, raw, expected)
        validation = self.policy.entries.get('validation.original_tuple_bridge', {})
        count = validation.get('coverage', {}).get('chosen_candidate', {}).get('left_distinct')
        if count is not None:
            actual = self.db.execute("SELECT COUNT(*) FROM r WHERE t='training_membership' AND "
                "json_extract(j,'$.pool')='validation' AND json_extract(j,'$.model_id')=?",
                (self.lock['models'][0],)).fetchone()[0]
            self.policy.coverage('validation.original_tuple_bridge', actual, count)
        census_old = self.policy.entries.get('census_old_seven_key_reconciliation', {}).get('value')
        if census_old:
            require(any(all(c.get(k) == census_old[k] for k in ('left', 'right', 'left_only', 'right_only'))
                        for c in self.lock.get('reconciliations', [])), 'resolved census/old reconciliation differs from lock')
        instruments = self.policy.entries.get('tables.row_instruments', {}).get('coverage', {})
        for pop, expected in instruments.get('population_matches', {}).items():
            actual = self.coverage['book_bridge']['populations'][pop]
            self.policy.coverage('tables.row_instruments.' + pop, {k: actual[k] for k in expected}, expected,
                                 selected=actual['rows'], total=expected['rows'])

    def book_row_check(self, table, row):
        binding = 'bibliography.book_bridge'
        reasons = as_json(row.get('source_missing_reasons_json')) or {}
        for field in ('book_id', 'canonical_book_id', *SOURCE_FIELDS):
            value = row.get(field)
            if value is None:
                require(reasons.get(field, {}).get('reason'), 'unexplained book/source null: ' + field)
                measured = self.lock['book_bridge'].get('coverage', {})
                if measured:
                    if not hasattr(self, '_book_null_reasons'):
                        self._book_null_reasons = {f: {r for c in measured.values() for r in
                            c.get('source_fields', {}).get(f, {}).get('null_reasons', {})}
                            for f in ('book_id', 'canonical_book_id', *SOURCE_FIELDS)}
                    recorded = self._book_null_reasons[field]
                    require(reasons[field]['reason'] in recorded, 'book/source null reason differs from recorded coverage: ' + field)
            if binding in self.policy.entries:
                self.policy.value(binding, table + '.' + field, value,
                                  reasons.get(field, {}).get('reason') if value is None else None, count=False)
        candidates = as_json(row.get('book_bridge_candidates_json')) or []
        bid = row.get('book_id')
        require((bid is not None and candidates == [bid] and row.get('book_bridge_status') == 'match') or
                (bid is None and len(candidates) != 1 and row.get('book_bridge_status') in ('no_key', 'unmatched', 'ambiguous')),
                'book bridge candidate/status/value differs')
        require(row.get('canonical_book_id') == bid, 'canonical book differs from exact bridge')
        if bid is not None:
            self.partner(table, None, 'book_registry', [bid])
        bridge = self.lock['book_bridge']
        require(row.get('book_registry_sha256') == bridge['registry_sha256'] and
                row.get('row_instruments_sha256') == bridge['row_instruments_sha256'], 'book/instrument hash binding differs')
        if row.get('source_record_sha256') is not None:
            require(row['source_record_sha256'] == digest(canonical(as_json(row.get('source_record_json')))),
                    'book source-record hash differs')
        for field in ('lqb_row', 'release_excluded_row'):
            if row.get('row_instrument_status') == 'original_id_unknown':
                require(row.get(field) is None and row.get('row_instrument_missing_reason'),
                        'unknown original instrument identity fabricated or unexplained')
            elif table == 'rows':
                require(isinstance(row.get(field), bool), 'known original instrument flag missing')
                present = self.db.execute("SELECT 1 FROM r WHERE t='row_instruments' AND json_extract(j,'$.row_key')=? "
                                          "AND json_extract(j,'$.kind') IN (?,?)",
                                          (row['row_key'], field, {'lqb_row': 'lqb', 'release_excluded_row': 'release_exclusion'}[field])).fetchone() is not None
                require(row[field] == present, 'instrument flag/relation membership differs')

    def partial_field_checks(self):
        for binding, table, aliases in (
            ('staging.boxes.parsed_provider_fields', 'boxes', {'detectedLanguages': 'detected_languages'}),
            ('bibliography.exact_source_locators', 'rows', {}),
        ):
            entry = self.policy.entries.get(binding)
            if entry is None:
                continue
            # Exact-source locator coverage describes the native projection,
            # before book enrichment; source replay checks that denominator.
            if table == 'rows':
                continue
            observed = {f: Counter() for f in entry.get('coverage', {})}
            for _, row in self.checked_items('partial-fields-' + binding, table, state=observed):
                for field in observed:
                    name = aliases.get(field, field)
                    value = row.get(name)
                    if field == 'languageCode':
                        languages = as_json(row.get('detected_languages')) or []
                        value = next((v.get('languageCode') for v in languages if v.get('languageCode')), None)
                    self.policy.value(binding, table + '.' + field, value, count=field == 'languageCode')
                    observed[field]['nonnull_rows' if value is not None else 'missing_rows'] += 1
                for dest, selector in entry.get('value', {}).get('fields', {}).items():
                    # Raw provider payloads are deliberately not public. If
                    # retained, replay here; otherwise source_replay verifies
                    # the selector against the hash-pinned original file.
                    if selector.split('.')[0] in row:
                        require(as_json(row.get(dest)) == as_json(get(row, selector)),
                                'parsed provider selector differs: ' + dest)
            for field, counts in observed.items():
                expected = entry['coverage'][field]
                for kind in ('nonnull_rows', 'missing_rows'):
                    self.policy.coverage(binding + '.' + field + '.' + kind, counts[kind], expected[kind],
                                         selected=sum(counts.values()), total=expected['nonnull_rows'] + expected['missing_rows'])

    def book_coverage_check(self):
        bridge = self.lock.get('book_bridge')
        if not bridge:
            return
        for name, key in (('registry_input', 'registry_sha256'), ('instruments_input', 'row_instruments_sha256')):
            source = next(s for s in self.lock['inputs'] if s['name'] == bridge[name])
            require(len(source['files']) == 1 and source['files'][0]['sha256'] == bridge[key],
                    'book bridge selected source hash differs: ' + name)
        stored = self.coverage['book_bridge']
        require(stored['measured_probe']['populations'] == bridge.get('coverage', {}), 'book probe/lock coverage differs')
        entry = self.policy.entries.get('bibliography.book_bridge', {})
        require(not entry or entry['coverage'] == bridge.get('coverage', {}), 'partial book coverage/lock differs')
        for pop, counts in stored['populations'].items():
            require(counts['rows'] == sum(counts[k] for k in ('match', 'no_key', 'unmatched', 'ambiguous')),
                    'book coverage status denominator differs: ' + pop)
            for field, values in counts['source_fields'].items():
                require(values['nonnull'] + values['null'] == counts['rows'] and
                        sum(values['null_reasons'].values()) == values['null'], 'book field/null-reason denominator differs')
            expected = bridge.get('coverage', {}).get(pop)
            if expected:
                self.policy.coverage('book_bridge.' + pop, {k: v for k, v in counts.items() if k != 'population'},
                                     expected, selected=counts['rows'], total=expected['rows'])

    def synthetic_collision_check(self):
        observed = Counter()
        split_collisions, split_groups = Counter(), defaultdict(set)
        groups, types = set(), Counter()
        for _, row in self.items('synthetic'):
            group = digest(canonical([row['factory_build_id'], row['line_id'], row['reuse_index']]))
            require(row.get('legacy_key_group') == group, 'synthetic legacy group fingerprint differs')
            count = self.db.execute("SELECT COUNT(*) FROM r WHERE t='synthetic' AND json_extract(j,'$.legacy_key_group')=?",
                                    (group,)).fetchone()[0]
            require(row.get('key_collision_size') == count and row.get('key_collision_group') == (group if count > 1 else None),
                    'synthetic collision group/size differs')
            observed[row['split']] += 1
            if count > 1:
                split_collisions[row['split']] += 1
                split_groups[row['split']].add(group)
                groups.add(group)
        recorded = self.coverage['synthetic_identity']
        require(set(recorded['splits']) == set(observed), 'synthetic identity split set differs')
        for split, count in observed.items():
            require(recorded['splits'][split] == {'rows': count, 'collision_rows': split_collisions[split],
                                                'collision_groups': len(split_groups[split])},
                    'synthetic identity split coverage differs')
        for variants, in self.db.execute("SELECT COUNT(DISTINCT json_extract(j,'$.synthetic_match_group')) "
                "FROM r WHERE t='synthetic' GROUP BY json_extract(j,'$.legacy_key_group') HAVING COUNT(*)>1"):
            types['identical_observation_groups' if variants == 1 else 'differing_observation_groups'] += 1
        require(recorded['collision_groups'] == len(groups) and recorded['collision_rows'] == sum(split_collisions.values()) and
                recorded['collision_types'] == {k: types[k] for k in ('identical_observation_groups', 'differing_observation_groups')},
                'synthetic collision coverage differs')
        membership = []
        for model, role, pool, variant, total, unique, ambiguous, ngroups in self.db.execute("""SELECT
                json_extract(j,'$.model_id'),json_extract(j,'$.role'),json_extract(j,'$.pool'),json_extract(j,'$.variant'),
                COUNT(*),SUM(json_extract(j,'$.synthetic_key') IS NOT NULL),SUM(json_extract(j,'$.synthetic_key') IS NULL),
                COUNT(DISTINCT CASE WHEN json_extract(j,'$.synthetic_key') IS NULL THEN json_extract(j,'$.synthetic_match_group') END)
                FROM r WHERE t='training_membership' AND json_extract(j,'$.synthetic_match_group') IS NOT NULL GROUP BY 1,2,3,4"""):
            membership.append({'model_id': model, 'role': role, 'pool': pool, 'variant': variant, 'rows': total,
                               'unique_exact_rows': unique, 'ambiguous_rows': ambiguous, 'ambiguous_groups': ngroups})
        require(recorded['training_membership'] == membership, 'synthetic membership coverage differs')
        if not self.policy.smoke:
            for source in self.lock['inputs']:
                if source['adapter'] != 'prepared' or not source.get('synthetic') or source['role'] != 'train':
                    continue
                native = Counter(dict(self.db.execute("SELECT json_extract(j,'$.synthetic_match_group'),COUNT(*) FROM r "
                    "WHERE t='synthetic' AND json_extract(j,'$.factory_build_id')=? AND json_extract(j,'$.split')='train' GROUP BY 1",
                    (source['factory_build_id'],))))
                for model in self.lock['models']:
                    used = Counter(dict(self.db.execute("SELECT json_extract(j,'$.synthetic_match_group'),COUNT(*) FROM r "
                        "WHERE t='training_membership' AND json_extract(j,'$.factory_build_id')=? AND json_extract(j,'$.model_id')=? "
                        "AND json_extract(j,'$.pool')=? AND json_extract(j,'$.variant')=? AND json_extract(j,'$.role')='train' GROUP BY 1",
                        (source['factory_build_id'], model, source['pool'], source.get('variant', 'prepared005')))))
                    require(native == used, 'synthetic full train multiset differs from native observations')

    def book_id_policy_check(self):
        """Independently check the retained native link and its report counts."""
        waves, sources, pairs = Counter(), Counter(), Counter()
        for raw, in self.db.execute("SELECT j FROM r WHERE t='rows' AND json_extract(j,'$.book_id_conflict')=1"):
            row = json.loads(raw)
            evidence = row.get('book_id_resolution_json') or {}
            a, b = evidence.get('decision', {}), evidence.get('metadata', {})
            require(evidence.get('policy') == 'harvest-explicit-decision-book-id-v1' and
                    evidence.get('field') == 'book_id' and evidence.get('row_key') == row['row_key'] and
                    evidence.get('wave') == row.get('wave'), 'book resolution policy/identity differs')
            require((a.get('source'), a.get('adapter'), b.get('source'), b.get('adapter')) ==
                    ('harvest_decisions', 'harvest', 'harvest', 'harvest'), 'book resolution writer pair differs')
            old, selected = row.get('source_decision_book_id'), evidence.get('selected_book_id')
            require(old and selected and old != selected and a.get('book_id') == old and
                    b.get('decision_book_id') == old and b.get('book_id') == b.get('canonical_book_id') == selected,
                    'book resolution lacks explicit source alias link')
            native = row.get('source_book_id') if row.get('book_bridge_status') else row.get('book_id')
            require(native == selected and row.get('book_id_conflict_reason') ==
                    'release metadata explicitly links the historical decision book ID to its release book ID',
                    'book resolution selected native identity/reason differs')
            for obs in (a, b):
                locator = obs.get('locator', {})
                require(isinstance(locator.get('ordinal'), int) and locator['ordinal'] >= 0 and any(
                    s['name'] == obs['source'] and s['adapter'] == obs['adapter'] and any(
                        f['path'] == locator.get('path') and f['sha256'] == locator.get('sha256')
                        for f in s['files']) for s in self.lock['inputs']), 'book resolution input is not locked')
            waves[evidence['wave']] += 1
            sources[evidence['wave'], evidence.get('native_source')] += 1
            pairs[evidence['wave'], a['source'], a['adapter'], b['source'], b['adapter']] += 1
        report = self.coverage.get('book_id_resolution', {})
        require(report.get('linked_conflicting_rows') == sum(waves.values()) and report.get('by_wave') == dict(waves) and
                report.get('by_wave_native_source') == [dict(wave=w, native_source=s, rows=n)
                    for (w, s), n in sorted(sources.items(), key=lambda item: repr(item[0]))] and
                report.get('by_wave_source_adapter_pair') == [dict(wave=w, left_source=ls, left_adapter=la,
                    right_source=rs, right_adapter=ra, rows=n)
                    for (w, ls, la, rs, ra), n in sorted(pairs.items())], 'book resolution coverage differs')

    @contextual
    def semantics(self):
        self.book_id_policy_check()
        for table in ('pages', 'page_images', 'page_frames', 'boxes', 'segmenter_page_results', 'book_sources'):
            for _ in self.checked_items('semantics-0', table, partner=True):
                pass
        for key, page in self.checked_items('semantics-1', 'pages'):
            self.partner('pages', key, 'book_registry', [page.get('book_id')])
        for key, box in self.checked_items('semantics-2', 'boxes'):
            self.partner('boxes', key, 'pages', [box.get('page_id')])
        for key, frame in self.checked_items('semantics-3', 'page_frames'):
            self.partner('page_frames', key, 'pages', [frame.get('page_id')])
            if frame.get('mapping_status') != 'verified':
                require(not frame.get('transform') and not frame.get('inverse_transform'), 'unqualified native transform')
        for key, result in self.checked_items('semantics-4', 'segmenter_page_results'):
            self.partner('segmenter_page_results', key, 'pages', [result.get('page_id')])
            require(result['status'] in ('ok', 'zero_detections', 'error', 'not_run'), 'unknown page/run status')
            if result['status'] != 'ok':
                require(bool(result.get('reason') or result.get('outcome_evidence_json')), 'page/run outcome lacks reason')
        for key, row in self.checked_items('semantics-5', 'rows'):
            require(isinstance(row.get('split'), str) and bool(row['split']),
                    'source row lacks an explicit split; rebuild required')
            if row['split'] == 'unknown':
                require(bool(row.get('split_reason')), 'unknown row split lacks a reason')
            expected_key = hashlib.sha256(canonical([row['parent_id'], row['row_id']]).encode()).hexdigest()
            require(row['row_key'] == expected_key, 'original tuple/row_key mismatch')
            require(row.get('decision') is not None and row.get('decision_reasons') is not None,
                    'source key lacks status/reason')
            if row['decision'] in ('HOLD', 'DROP'):
                require(bool(row['decision_reasons']), 'held/dropped source key lacks reason')
            used = bool(row.get('trained_in'))
            if row.get('release'):
                require(self.find('real', [row['row_key']]) is not None, 'published source row omitted from real view')
            box = self.find('boxes', [row.get('box_id')])
            page = self.find('pages', [row.get('page_id')])
            if used or row.get('box_id') is not None:
                box = self.partner('rows', key, 'boxes', [row.get('box_id')])
                page = self.partner('rows', key, 'pages', [row.get('page_id')])
                if box is not None and page is not None:
                    require(box['page_id'] == page['page_id'], 'row → box → page FK fails')
                if page is not None:
                    require(row.get('book_id') == page.get('book_id'), 'row/page book mismatch')
            book = self.find('book_registry', [row.get('book_id')])
            if used or row.get('book_id') is not None:
                book = self.partner('rows', key, 'book_registry', [row.get('book_id')])
                if book is not None:
                    book_split = book.get('split')
                    expected_split = ('unknown' if not book_split or book_split == 'unknown' or
                                      book_split.startswith('unassigned') else book_split)
                    require(row['split'] == expected_split, 'row split disagrees with pinned registry')
                    native = row.get('source_split')
                    if (isinstance(native, str) and native and native != 'unknown' and
                            not native.startswith('unassigned') and expected_split != 'unknown' and
                            native != expected_split):
                        require(row.get('split_conflict') is True and
                                row.get('split_resolution_json', {}).get('source_registry_conflict') is True,
                                'source/registry split disagreement lacks diagnostic flag')
                    if used:
                        require(row['split'] == 'train', 'held-out book used for training')
                        if book.get('exportable') is False:
                            if not hasattr(self, '_registry_adoption'):
                                self._registry_adoption = adopted_registry(self.lock)
                            require(adopted_train_assignment(book, self._registry_adoption),
                                    'non-exportable book used for training without bound adoption')
            if used:
                require(row.get('trained_in') == sorted(self.lock['models']), 'trained_in differs from three model ids')
                models = {v[0] for v in self.db.execute("SELECT DISTINCT json_extract(j,'$.model_id') FROM r "
                    "WHERE t='training_membership' AND json_extract(j,'$.row_key')=? AND json_extract(j,'$.role')='train'",
                    (row['row_key'],))}
                require(models == set(row['trained_in']), 'trained_in lacks exact train membership')
            if row.get('raw_text') is not None:
                require(digest(row['raw_text']) == row['raw_text_sha256'], 'raw label hash mismatch')
            if row.get('text') is not None:
                require(digest(row['text']) == row['label_sha256'], 'final label hash mismatch')
        for _, line in self.checked_items('semantics-6', 'real'):
            row = self.find('rows', [line['row_key']])
            require(row is not None, 'real view → row FK fails')
            require(line.get('id', '').startswith(str(line.get('release')) + ':'), 'unnamespaced public real id')
            for field in ('text', 'label_sha256', 'crop_sha256', 'training_image_sha256', 'trained_in',
                          'split', 'split_reason', 'split_resolution_json'):
                require(line.get(field) == row.get(field), 'real/table variant mismatch: ' + field)
            if line.get('trained_in'):
                self.policy.original('real.original_image', line.get('image_measured_sha256'),
                                     line.get('original_crop_custody'), line.get('crop_sha256'), count=False)
                if not self.manifest.get('layout') or self.frozen_available:
                    require(line.get('trainer_image_measured_sha256'), 'used row lacks trainer image variant')
        for _, membership in self.checked_items('semantics-7', 'training_membership', partner=True):
            if membership.get('membership_kind') == 'reference_image':
                reference = self.find('references', [membership['reference_id']])
                require(reference is not None, 'reference image membership FK fails')
                require(all(membership.get(k) == reference.get(k) for k in ('row_key', 'image_variant', 'label_variant', 'payload_locator', 'image_sha256')), 'reference image variant/locator differs')
                require(membership.get('model_id') is None and membership.get('drawn') is None, 'reference membership fabricates training draw')
                continue
            require(membership.get('model_id') in self.lock['models'], 'membership has unbound model')
            pool = str(membership.get('pool', ''))
            if membership.get('role') == 'test' or pool == 'test' or pool.endswith('_test'):
                require(membership.get('selection_role') == 'report_only' and not membership.get('selection'),
                        'test used for selection')
            if self.lock.get('run_bindings'):
                require(membership.get('run_binding_sha256') == self.lock['run_bindings'][membership['model_id']],
                        'membership run binding differs')
            if membership.get('row_key'):
                row = self.find('real', [membership['row_key']])
                require(row is not None, 'training membership → real FK fails')
                if any(row.get(field) == 'test' or str(row.get(field)).endswith('_test')
                       for field in ('split', 'source_split')):
                    require(not membership.get('selection'), 'test used for selection')
                matches = [v for v in row.get('trainer_variants', []) if all(v.get(k) == membership.get(k)
                           for k in ('pool', 'trainer_line_id', 'variant'))]
                require(len(matches) == 1, 'consumed image/label variant missing or ambiguous')
                row = matches[0]
                require(membership['image_sha256'] == row['image_sha256'], 'trainer embedded bytes differ from membership')
            else:
                group = membership.get('synthetic_match_group')
                candidates = [json.loads(j) for j, in self.db.execute(
                    "SELECT j FROM r WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=?", (group,))]
                require(candidates and len(candidates) == membership.get('synthetic_candidate_count'), 'synthetic membership group FK fails')
                if membership.get('synthetic_key'):
                    line = self.find('synthetic', json.loads(membership['synthetic_key']))
                    require(len(candidates) == 1 and line == candidates[0] and
                            membership['synthetic_mapping_status'] == 'unique_exact', 'synthetic membership FK fails')
                else:
                    require(len(candidates) > 1 and membership['synthetic_mapping_status'] == 'ambiguous_identical_observations',
                            'ambiguous synthetic membership invents a pairing')
                for line in candidates:
                    require(membership['image_sha256'] == line['image_sha256'], 'synthetic consumed bytes differ')
                    require(all(membership.get(k) == line.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')),
                            'synthetic consumed label/codec differs')
                consumed = self.db.execute("""SELECT COUNT(*) FROM r WHERE t='training_membership'
                    AND json_extract(j,'$.synthetic_match_group')=? AND json_extract(j,'$.model_id')=?
                    AND json_extract(j,'$.role')=? AND json_extract(j,'$.pool')=? AND json_extract(j,'$.variant')=?""",
                    (group, membership['model_id'], membership['role'], membership['pool'], membership['variant'])).fetchone()[0]
                require(consumed <= len(candidates), 'synthetic prepared multiplicity exceeds native observations')
                row = candidates[0]
            require(membership['label_sha256'] == digest(membership['gt_nfc']), 'consumed label hash mismatch')
            require(all(membership.get(k) == row.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')), 'consumed label/codec variant mismatch')
            if membership['role'] == 'train':
                if membership.get('row_key'):
                    target = self.find('real', [membership['row_key']])
                    require(membership['model_id'] in target.get('trained_in', []), 'train membership absent from trained_in')
                elif consumed == len(candidates):
                    require(all(membership['model_id'] in c.get('trained_in', []) for c in candidates),
                            'train membership absent from trained_in')
                else:
                    require(all(membership['model_id'] not in c.get('trained_in', []) for c in candidates),
                            'partial identical group claims individual training provenance')
            elif membership['role'] == 'test':
                require(membership['selection_role'] == 'report_only' and not membership['selection'], 'test used for selection')
        for _, label in self.checked_items('semantics-8', 'label_versions', partner=True):
            require(self.find('rows', [label['row_key']]) is not None, 'label → row FK fails')
            require(digest(label['text']) == label['text_sha256'] if label['text'] is not None else label.get('reason') and label['text_sha256'] is None, 'label version hash mismatch')
        for table in ('row_features', 'row_instruments', 'references'):
            for _, item in self.checked_items('semantics-9', table, partner=True):
                require(self.find('rows', [item.get('row_key')]) is not None, table + ' → row FK fails')
        for _, instrument in self.checked_items('semantics-10', 'row_instruments', partner=True):
            if instrument['kind'] in ('lqb_row', 'release_excluded_row'):
                row = self.find('rows', [instrument['row_key']])
                require(row.get(instrument['kind']) is True, 'exact row-instrument flag missing')
        for _, reference in self.checked_items('semantics-11', 'references', partner=True):
            real = self.find('real', [reference['row_key']])
            if reference.get('image_sha256'):
                joined = real is not None and reference['image_sha256'] in (real.get('crop_sha256'), real.get('training_image_sha256'))
                if not joined and self.manifest.get('layout'):
                    joined = self.reference_payload_published(reference)
                require(joined, 'reference image variant does not join published bytes')
            if reference.get('label_version'):
                label = self.find('label_versions', [reference['label_version']])
                require(label is not None and label['row_key'] == reference['row_key'], 'reference label-version FK fails')
                if reference.get('label_sha256'):
                    require(reference['label_sha256'] == label['text_sha256'], 'reference label variant hash differs')
        for _, line in self.checked_items('semantics-12', 'synthetic'):
            require(line['synthetic_key'] == canonical([line[k] for k in KEYS['synthetic']]), 'synthetic position key differs')
            attributes = line['synthetic_native_attributes_json']
            require(set(attributes) == set(SYNTHETIC_MATCH_FIELDS), 'synthetic native attribute coverage differs')
            require(line['synthetic_match_group'] == digest(canonical([line['factory_build_id'], line['image_sha256'], attributes])),
                    'synthetic native match fingerprint differs')
            require(line['n_ops'] == len(line['applied_ops']), 'synthetic operation count mismatch')
            require(line['severity'] in (0, 1, 2, 3), 'synthetic severity out of range')
            require(line['text'] == line['gt_nfc'] == ud.normalize('NFC', line['text']), 'synthetic NFC mismatch')
            if not self.manifest.get('layout') or self.frozen_available or line['split'] in ('val', 'reserved'):
                require(line.get('image_measured_sha256') is not None, 'synthetic image missing')
            if line.get('font_sha16'):
                require(len(line['font_sha16']) == 16, 'invalid font sha16')
            if line.get('font_file_sha256'):
                require(len(line['font_file_sha256']) == 64, 'font sha16 masquerades as full hash')
            unknown = line.get('historical_unknown_fields_json') or {}
            if isinstance(unknown, str):
                unknown = json.loads(unknown)
            for field in ('text_source_locator', 'text_sha256', 'font_file_sha256',
                          'generator_code_sha256', 'generator_binary_sha256'):
                if line.get(field) is None:
                    require(field in unknown and unknown[field].get('reason') and unknown[field].get('search_receipt'), 'unexplained synthetic provenance null: ' + field)

    def load_keysets(self, paths):
        for path in paths:
            with gzip.open(path, 'rt') as f:
                for line in f:
                    row = json.loads(line)
                    try:
                        self.db.execute('INSERT INTO sets VALUES(?,?,?)', (row['set'], row['key'], canonical(row['detail'])))
                    except sqlite3.IntegrityError as exc:
                        raise ValueError('duplicate source keyset key') from exc

    @contextual
    def reconciliation(self):
        paths = sorted((self.root / 'manifests/keysets').glob('*.jsonl.gz'))
        with self.ledger.unit('reconciliation:keysets') as run:
            if run:
                self.load_keysets(paths)
        report = json.loads((self.root / 'manifests/RECONCILIATION.json').read_text())
        require([{k: c[k] for k in ('name', 'left', 'right', 'left_only', 'right_only')} for c in report['checks']] ==
                self.lock.get('reconciliations', []), 'reconciliation requirements differ from lock')
        for check in report['checks']:
            for direction, a, b in (('left_only', check['left'], check['right']), ('right_only', check['right'], check['left'])):
                sql = 'SELECT k FROM sets WHERE s=? EXCEPT SELECT k FROM sets WHERE s=?'
                n = self.db.execute('SELECT COUNT(*) FROM (' + sql + ')', (a, b)).fetchone()[0]
                require(n == check['observed'][direction]['count'], 'key difference receipt disagrees with keys')
                self.policy.coverage('reconciliation.' + check['name'] + '.' + direction,
                                     n, check[direction], comparable=False)
                published = set()
                for part in check['observed'][direction]['parts']:
                    with gzip.open(safe_path(self.root, part['path']), 'rt') as f:
                        for line in f:
                            key = json.loads(line)['key']
                            require(key not in published, 'duplicate directional-difference key')
                            published.add(key)
                require(published == {v[0] for v in self.db.execute(sql, (a, b))}, 'directional key witness incomplete')
        # Population sizes are frozen evidence, never acceptor literals.
        keysets = {'s1': 's1', 'old_union': 'old', 'prepared_s1': 'prepared_train_v4',
                   'harvest': 'harvest', 'prepared_harvest': 'prepared_all_harvest',
                   'prepared_harvest_train': 'prepared_train_harvest'}
        for name, expected in self.lock.get('population_counts', {}).items():
            if name in keysets:
                actual = self.db.execute('SELECT COUNT(*) FROM sets WHERE s=?', (keysets[name],)).fetchone()[0]
            elif name == 'a12':
                actual = self.db.execute("SELECT COUNT(*) FROM r WHERE t='synthetic'").fetchone()[0]
            elif name == 'census_g2':
                actual = sum(bool(row.get('census_generation')) for _, row in self.items('rows'))
            else:
                # Role/pool populations retain one occurrence per model.
                pool = {'prepared_harvest_dev': 'harvest_dev', 'prepared_harvest_test': 'harvest_test',
                        'seal04_dev': 'seal04_dev', 'seal04_test': 'seal04_test',
                        'prepared_validation': 'validation'}.get(name)
                require(pool is not None, 'unmapped frozen population count: ' + name)
                for model in self.lock['models']:
                    actual = self.db.execute("SELECT COUNT(*) FROM r WHERE t='training_membership' "
                        "AND json_extract(j,'$.pool')=? AND json_extract(j,'$.model_id')=?", (pool, model)).fetchone()[0]
                    self.policy.coverage('population_counts.' + name + '/' + model, actual, expected)
                continue
            self.policy.coverage('population_counts.' + name, actual, expected)
        for check in self.lock.get('expected_counts', []):
            count = 0
            for _, row in self.items(check['table']):
                if all(get(row, key) == value for key, value in check.get('where', {}).items()):
                    count += 1
            self.policy.coverage('expected_counts.' + check['name'], count, check['count'])

    @contextual
    def coverage_and_features(self):
        observed = defaultdict(lambda: {'rows': 0, 'fields': Counter(), 'missing_reasons': Counter()})
        for _, row in self.checked_items('feature-source-fields', 'rows', state=observed):
            group = canonical([row.get('release', 'census'), row.get('wave'), row.get('source'), row.get('provider')])
            observed[group]['rows'] += 1
            reasons = row.get('source_missing_reasons_json') or {}
            if isinstance(reasons, str):
                reasons = json.loads(reasons)
            for field in SOURCE_FIELDS:
                if row.get(field) is not None:
                    observed[group]['fields'][field] += 1
                else:
                    observed[group]['missing_reasons'][field] += 1
                    require(field in reasons and reasons[field].get('reason'), 'unexplained bibliography null: ' + field)
        coverage = json.loads((self.root / 'manifests/COVERAGE.json').read_text())['populations']
        require(json.loads(canonical(observed)) == coverage, 'source-field coverage differs from rows')
        bundle = json.loads((self.root / 'manifests/FEATURE_INPUTS.json').read_text())
        require(bundle['sources'] == self.lock['features'], 'feature input provenance differs from lock')
        require(bundle['unicode_version'] == ud.unidata_version, 'Unicode replay version mismatch')
        atoms = {a['ch']: a for a in bundle['codec']['atoms']}
        ranges = sorted(bundle['script_ranges'])
        # Sample 1000 original keys without replacement, then every label variant for them.
        rng = random.Random(20261022)
        reservoir = []
        for n, (_, row) in enumerate(self.items('rows')):
            if n < 1000:
                reservoir.append(row['row_key'])
            else:
                k = rng.randrange(n + 1)
                if k < 1000:
                    reservoir[k] = row['row_key']
        selected, checked = set(reservoir), {'count': 0}
        for _, feature in self.checked_items('feature-replay', 'row_features', partner=True, state=checked):
            require(sum(feature[b + '_count'] for b in BUCKETS) == feature['nonspace_chars'], 'feature buckets do not partition denominator')
            label = self.find('label_versions', [feature['label_variant']])
            require(label is not None and label['row_key'] == feature['row_key'], 'feature → label variant FK fails')
            if self.policy.status('tables.page_frames') == 'historical_unknown':
                for field in ('x_center_norm', 'y_center_norm'):
                    self.policy.value('tables.page_frames', 'row_features.' + field, feature.get(field))
            if feature['row_key'] not in selected:
                continue
            languages = feature.get('provider_languages') or []
            if isinstance(languages, str):
                languages = json.loads(languages)
            recomputed = replay_text(label['text'], languages, atoms, ranges)
            for field, expected in recomputed.items():
                actual = feature.get(field)
                require(abs(actual - expected) < 1e-9 if isinstance(expected, float) else actual == expected,
                        'independent feature replay differs: ' + field)
            row = self.find('rows', [feature['row_key']])
            require(feature.get('crop_width_px') == row.get('width') and feature.get('crop_height_px') == row.get('height'), 'feature crop variant/dimensions differ')
            if row.get('frame_status') != 'verified' or self.policy.status('tables.page_frames') == 'historical_unknown':
                require(feature.get('x_center_norm') is None and feature.get('y_center_norm') is None, 'unqualified normalized position')
            else:
                polygon = row.get('polygon_norm')
                if isinstance(polygon, str):
                    polygon = json.loads(polygon)
                if polygon:
                    xs = [p['x'] if isinstance(p, dict) else p[0] for p in polygon]
                    ys = [p['y'] if isinstance(p, dict) else p[1] for p in polygon]
                    require(abs(feature['x_center_norm'] - (max(xs) + min(xs)) / 2) < 1e-9 and
                            abs(feature['y_center_norm'] - (max(ys) + min(ys)) / 2) < 1e-9, 'independent position replay differs')
            w, h = row.get('width'), row.get('height')
            expected_aspect = w / h if w is not None and h else None
            require(feature.get('crop_aspect') == expected_aspect, 'independent crop-aspect replay differs')
            checked['count'] += 1
        require(checked['count'] > 0 or self.receipt['mode'] == 'smoke' and not selected, 'no feature variants replayed')
        self.feature_checks = checked['count']

    def validation_metadata(self, external):
        """Reopen the frozen join input independently of builder receipts."""
        index = ValidationOriginals(self.db)
        for source in external['inputs']:
            if not source.get('validation_original_metadata'):
                continue
            for file in source['files']:
                self.verify_file(file)
                for ordinal, row in enumerate(records(file['path'], source)):
                    index.observe(row, source['name'], canonical({'path': file['path'], 'ordinal': ordinal}),
                                  file['sha256'])
        return index

    @contextual
    def source_binding_replay(self):
        """Check partial source-observation denominators, including bounded smoke.

        This is still a self-check for smoke: it verifies only selected source
        observations and cannot claim complete source acceptance.
        """
        if self.lock_path is None or not self.policy.entries:
            return
        external = json.loads(Path(self.lock_path).read_text())
        require(sanitize(external) == self.lock, 'external and packaged INPUT_LOCK differ')
        validation_originals = self.validation_metadata(external)
        bridge = self.lock.get('book_bridge')
        def selected(name):
            source = next(s for s in external['inputs'] if s['name'] == name)
            for f in source['files']:
                self.verify_file(f)
                yield from records(f['path'], source)
        engine = (BookBridge(selected(bridge['registry_input']), selected(bridge['instruments_input']),
                             selected(bridge['sources_input']) if bridge.get('sources_input') else (),
                             bridge['registry_sha256'], bridge['row_instruments_sha256']) if bridge else None)
        if engine:
            instrument_counts = self.policy.entries.get('tables.row_instruments', {}).get('coverage', {})
            for name, actual in (('memberships', sum(len(v) for v in engine.instruments.values())),
                                 ('distinct_original_line_ids', len(engine.instruments))):
                if name in instrument_counts:
                    self.policy.coverage('tables.row_instruments.' + name, actual, instrument_counts[name], exact=True)
            for _, instrument in self.items('row_instruments'):
                ident = str(instrument.get('row_id'))
                require(any(all(instrument.get(k) == declared.get(k) for k in ('kind', 'list_name', 'list_sha256'))
                            for declared in engine.instruments.get(ident, [])), 'instrument lacks exact pinned list membership')
                row = self.find('rows', [instrument['row_key']])
                require(row is not None and ident in (str(row.get('row_id')), str(row.get('original_line_id'))),
                        'instrument original ID differs from target row')
        observed = {p: new_coverage() for p in bridge['populations']} if bridge else {}
        self.db.execute('CREATE TABLE IF NOT EXISTS native_books(t TEXT,k TEXT,j TEXT,m TEXT)')
        self.db.execute('CREATE INDEX IF NOT EXISTS native_books_target ON native_books(t,k)')
        partials = [e for e in self.policy.entries.values() if e['field'] in
                    ('staging.boxes.parsed_provider_fields', 'bibliography.exact_source_locators')]
        fields = {e['field']: {f: Counter() for f in e.get('coverage', {})} for e in partials}
        smoke = self.coverage.get('smoke') if self.policy.smoke else None
        for source in external['inputs']:
            pop = source.get('book_population') if bridge else None
            entries = [e for e in partials if e.get('value', {}).get('input') == source['name']]
            if not pop and not entries:
                continue
            state = {'observed': observed, 'fields': fields, 'books': []}
            for file_index, f in enumerate(source['files']):
                if smoke and not external.get('_measure') and file_index and (source['adapter'] in ('prepared', 'synthetic') or source.get('table') == 'page_images'):
                    continue
                with self.ledger.unit('source-binding:' + source['name'] + ':' + f['path'], state) as run:
                    if not run:
                        observed, fields = state['observed'], state['fields']
                        continue
                    self.verify_file(f)
                    observed, fields = state['observed'], state['fields']
                    books = set(state['books'])
                    for ordinal, original in enumerate(records(f['path'], source)):
                        if smoke and not source.get('book_bridge_metadata') and not source.get('validation_original_metadata') and ordinal >= smoke * external.get('smoke_rows_per_source', 512):
                            break
                        if pop == 'validation':
                            original = validation_originals.enrich(original)
                        row = mapped(original, source)
                        if smoke and source['adapter'] in ('row', 's1', 'harvest', 'census'):
                            book = row.get('book_id') or row.get('edition_id') or row.get('source_doc_id')
                            if book is None:
                                book = row.get('row_id') or row.get('id') or get(row, 'binding.id')
                            if book not in books and len(books) >= smoke:
                                continue
                            books.add(book)
                        with diagnostic(source['name'], source['adapter'], {'path': f['path'], 'ordinal': ordinal}):
                            for entry in entries:
                                binding = entry['field']
                                for field in fields[binding]:
                                    dest = {'detectedLanguages': 'detected_languages'}.get(field, field)
                                    selector = entry.get('value', {}).get('fields', {}).get(dest)
                                    value = get(original, selector) if selector else row.get(dest)
                                    if field == 'languageCode':
                                        value = next((v.get('languageCode') for v in as_json(row.get('detected_languages')) or []
                                                      if v.get('languageCode')), None)
                                    # Source-observation nulls are separate units
                                    # from the public row/table null counts.
                                    self.policy.value(binding, 'source.' + source['name'] + '.' + field, value)
                                    fields[binding][field]['nonnull_rows' if value is not None else 'missing_rows'] += 1
                                if source.get('table') == 'boxes':
                                    public = self.find('boxes', [row['box_id']])
                                    require(public is not None, 'selected provider box omitted')
                                    for dest, selector in entry['value'].get('fields', {}).items():
                                        require(as_json(public.get(dest)) == as_json(get(original, selector)),
                                                'source parsed provider field differs: ' + dest)
                            if pop:
                                if source['adapter'] == 'prepared' and smoke:
                                    present = self.db.execute("SELECT 1 FROM r WHERE t='training_membership' AND "
                                        "json_extract(j,'$.source_shard')=? AND json_extract(j,'$.source_ordinal')=?",
                                        (f['path'], ordinal)).fetchone()
                                    if not present:
                                        continue
                                native = metadata(original, pop)
                                match = engine.match(native, pop)
                                resolved = engine.resolve(native, pop, match)
                                count_coverage(observed[pop], resolved, engine.memberships(native, pop), match)
                                target = self.observation_target(source, row, f['path'], ordinal)
                                if target:
                                    self.db.execute('INSERT INTO native_books VALUES(?,?,?,?)',
                                                    (*target, canonical(native), canonical(match)))
                            self.binding_source_checks += 1
                    state['books'] = sorted(books, key=str)
        for entry in partials:
            binding = entry['field']
            for field, expected in entry.get('coverage', {}).items():
                counts = fields[binding][field]
                for kind in ('nonnull_rows', 'missing_rows'):
                    self.policy.coverage(binding + '.source.' + field + '.' + kind, counts[kind], expected[kind],
                                         selected=sum(counts.values()), total=expected['nonnull_rows'] + expected['missing_rows'])
        if bridge:
            stored = self.coverage['book_bridge']['populations']
            # Each selected observation is replayed; the build receipt is not
            # treated as independent evidence for its own coverage counts.
            for pop, counts in observed.items():
                expected = {k: v for k, v in stored[pop].items() if k != 'population'}
                require(json.loads(canonical(counts)) == expected, 'source book coverage differs: ' + pop)
                frozen = bridge.get('coverage', {}).get(pop)
                if frozen:
                    self.policy.coverage('source.book_bridge.' + pop, json.loads(canonical(counts)), frozen,
                                         selected=counts['rows'], total=frozen['rows'])
            for table in ('rows', 'synthetic'):
                for key, row in self.checked_items('book-fields', table):
                    natives = [(json.loads(j), json.loads(m)) for j, m in self.db.execute(
                        'SELECT j,m FROM native_books WHERE t=? AND k=?', (table, key))]
                    candidates = sorted({bid for _, m in natives for bid in m['candidates']})
                    require(candidates == as_json(row.get('book_bridge_candidates_json')),
                            'source book candidates differ from public row')
                    bid = candidates[0] if len(candidates) == 1 else None
                    base = engine.bibliography(bid)[0] if bid else {}
                    for field in SOURCE_FIELDS:
                        if field == 'source_record_sha256':
                            continue  # Checked against canonical public source_record_json.
                        values = [n[field] for n, _ in natives if n.get(field) is not None]
                        if field == 'source_title':
                            values += [n['title'] for n, _ in natives if n.get('title')]
                        if not values:
                            values = [base.get(field)]
                        actual = row.get(field)
                        require(any(actual == v or actual is not None and v is not None and str(actual) == str(v)
                                    for v in values), 'source book field differs: ' + field)

    def observation_target(self, source, row, path, ordinal):
        adapter = source['adapter']
        if adapter == 'synthetic':
            return 'synthetic', canonical([source['factory_build_id'], row['split'], path, ordinal])
        if adapter == 'prepared':
            found = self.db.execute("SELECT json_extract(j,'$.row_key') FROM r WHERE t='training_membership' "
                "AND json_extract(j,'$.source_shard')=? AND json_extract(j,'$.source_ordinal')=? LIMIT 1", (path, ordinal)).fetchone()
            return ('rows', canonical([found[0]])) if found and found[0] else None
        parent = row.get('parent_id', get(row, 'binding.parent_id'))
        ident = row.get('row_id', row.get('id', get(row, 'binding.id')))
        if adapter == 'harvest':
            parent = row.get('parent_id', 'harvest:' + row['wave'])
            ident = row.get('row_id', row.get('id'))
        if parent is not None and ident is not None:
            return 'rows', canonical([digest(canonical([parent, ident]))])
        if source.get('book_population') == 'old':
            found = self.db.execute("SELECT j FROM sets WHERE s='s1' AND k=?", (str(row['line_id']),)).fetchone()
            key = json.loads(found[0]).get('row_key') if found else None
            return ('rows', canonical([key])) if key else None
        return None

    @contextual
    def original_source_replay(self):
        """Independent byte/root/payload replay, also for the smoke selection."""
        if self.lock_path is None:
            return None
        external = json.loads(Path(self.lock_path).read_text())
        require(sanitize(external) == self.lock, 'external and packaged INPUT_LOCK differ')
        checks, report = build_file_index(self.db, external.get('crop_roots', []), cache=external.get('crop_index_cache'))
        require(report == self.coverage['original_crops']['root_index'], 'crop root index report differs')
        crops = CropIndex(self.db, checks)
        payloads = OriginalPayloads(self.db, checks, self.policy)
        validation = self.validation_metadata(external)
        smoke = self.coverage.get('smoke') if self.policy.smoke else None
        for source in external['inputs']:
            if not crop_eligible(source):
                continue
            with self.ledger.unit('original-payload:' + source['name']) as run:
                if run:
                    payloads.load(external, source, smoke, check=self.ledger.deadline.check, verify_entry=self.verify_file)
            # Selection still uses the whole source declaration (book buckets span
            # files). Completed files are skipped without repeating byte custody.
            from itertools import groupby
            for path, observations in groupby(selected_records(external, source, smoke, verify_entry=self.verify_file), key=lambda v: v[0]['path']):
                with self.ledger.unit('original-observe:' + source['name'] + ':' + path) as run:
                    if not run:
                        # Advancing selected_records preserves smoke's cross-file buckets.
                        for _ in observations: pass
                        continue
                    for entry, ordinal, original in observations:
                        if source.get('book_population') == 'validation':
                            original = validation.enrich(original)
                        locator = canonical({'path': entry['path'], 'ordinal': ordinal, 'sha256': entry['sha256']})
                        result = payloads.verify(original, {**source, '_path': entry['path'], '_locator': locator},
                                                 keep_bytes=True)
                        result.pop('bytes', None)
                        crops.observe(original, source, locator, result)
        crops.load_smoke_targets(external, smoke)
        replayed_skips = set()
        for source, loc, target in crops.smoke_witnesses():
            key, partner = [source, loc], [target['source'], target['locator']]
            require(self.smoke_skip_allowed('original_crops', key, 'original_crops', partner),
                    'original crop unloaded target lacks exact smoke witness')
            replayed_skips.add(('original_crops', canonical(key), 'original_crops', canonical(partner)))
        require(replayed_skips == {t for t in getattr(self, '_smoke_skip_keys', ()) if t[0] == 'original_crops'},
                'original crop smoke witnesses differ from pinned source metadata')
        observed = crops.coverage()
        require(observed == self.coverage['original_crops']['populations'], 'original crop source coverage differs')
        self.policy.original_coverage(observed)
        def image_hash(key):
            row = self.find('real', [key])
            return (row.get('image_measured_sha256'),) if row else None
        published = crops.published_counts(image_hash, smoke=bool(smoke),
            populations=self.policy.entries.get('assets.original_crops', {}).get('coverage', {}),
            allow_unselected={s['name'] for s in external['inputs'] if s['adapter'] in ('keyset', 'prepared')})
        require(published == self.coverage['original_crops']['published_images'],
                'published original image population counts differ')
        self.policy.original_published_coverage(published, observed)
        for _, row in self.checked_items('original-custody', 'real'):
            custody = row.get('original_crop_custody') or {}
            direct = self.db.execute('''SELECT o.result_json FROM original_crop_keys k JOIN original_crop_observations o
                ON o.source=k.source AND o.locator=k.locator WHERE k.identity=?''', ('tuple:' + row['row_key'],))
            results = [crops.resolve(['tuple:' + row['row_key']], json.loads(raw)) for raw, in direct]
            require(any(r == custody for r in results), 'published original custody differs from source')
            measured = row.get('image_measured_sha256')
            require(bool(measured) == bool(custody.get('hash_match')), 'verified original source omitted/substituted')
            require(row.get('original_custody') == custody_kind(custody), 'published original custody kind differs')
            if measured:
                self.policy.original('real.replayed_original', measured, custody, row.get('crop_sha256'), count=False)
        return published

    @contextual
    def source_replay(self):
        if self.lock_path is None:
            return False
        external = json.loads(Path(self.lock_path).read_text())
        require(sanitize(external) == self.lock, 'external and packaged INPUT_LOCK differ')
        if self.policy.smoke:
            # Smoke extent is bounded and deliberately cannot establish full-source coverage.
            return False
        assets = Assets(external)
        validation_originals = self.validation_metadata(external)
        for field in ('codec', 'scripts'):
            self.verify_file(external['features'][field])
        bundle = json.loads((self.root / 'manifests/FEATURE_INPUTS.json').read_text())
        require(bundle['codec'] == sanitize(json.loads(Path(external['features']['codec']['path']).read_text())), 'codec bundle differs from source')
        ranges = []
        for line in Path(external['features']['scripts']['path']).read_text().splitlines():
            clean = line.split('#')[0].strip()
            if clean:
                span, name = map(str.strip, clean.split(';'))
                edges = span.split('..')
                ranges.append([int(edges[0], 16), int(edges[-1], 16), name])
        require(sorted(ranges) == bundle['script_ranges'], 'Unicode Script bundle differs from source')
        for entry in external['assets']:
            self.verify_file(entry)
        for source in sorted(external['inputs'], key=lambda s: s['name']):
            state = {'offset': 0}
            for file in source['files']:
                self.verify_file(file)
                with self.ledger.unit('source-replay:' + source['name'] + ':' + file['path'], state) as run:
                    if not run: continue
                    offset = state['offset']
                    scanned = 0
                    for ordinal, original in enumerate(records(file['path'], source)):
                        if source.get('book_population') == 'validation':
                            original = validation_originals.enrich(original)
                        with diagnostic(source['name'], source['adapter'],
                                        {k: original.get(k) for k in ('row_key', 'parent_id', 'row_id', 'line_id')}
                                        or {'path': file['path'], 'ordinal': ordinal}):
                            scanned += 1
                            r = mapped(original, source)
                            adapter = source['adapter']
                            if adapter in ('row', 's1', 'census', 'harvest'):
                                parent = r.get('parent_id', get(original, 'binding.parent_id'))
                                ident = r.get('row_id', get(original, 'binding.id'))
                                if adapter == 'harvest':
                                    parent = r.get('parent_id', 'harvest:' + r['wave'])
                                    ident = r.get('row_id', r.get('id'))
                                key = hashlib.sha256(canonical([parent, ident]).encode()).hexdigest()
                                row = self.find('rows', [key])
                                require(row is not None, 'source key omitted: ' + key)
                                if adapter == 'harvest':
                                    native_book = row.get('source_book_id') if row.get('book_bridge_status') else row.get('book_id')
                                    if r.get('book_id') is not None and native_book is not None and r['book_id'] != native_book:
                                        require(row.get('book_id_conflict') is True,
                                                'source book disagreement lacks explicit resolution')
                                if adapter == 'harvest' and row.get('book_id_conflict'):
                                    evidence = row['book_id_resolution_json']
                                    side = ('decision' if source['name'] == 'harvest_decisions' else
                                            'metadata' if source['name'] == 'harvest' else None)
                                    require(side is not None, 'book resolution includes an uncovered writer')
                                    recorded = evidence[side]
                                    require(recorded['locator'] == {'path': file['path'], 'ordinal': ordinal,
                                            'sha256': file['sha256']}, 'book resolution source locator differs')
                                    require(all(recorded.get(f) == r.get(f) for f in
                                            ('book_id', 'canonical_book_id', 'decision_book_id', 'decision_sha256')),
                                            'book resolution evidence differs from pinned source')
                                if adapter == 'census':
                                    text = r.get('text', r.get('final_text'))
                                elif adapter == 's1':
                                    text = r.get('text', r.get('label'))
                                else:
                                    text = r.get('text', r.get('label_corrected', r.get('label', r.get('final_text'))))
                                for variant, label_text in ((source.get('label_variant', 'raw' if adapter == 'row' else adapter), text),
                                                           ('raw', r.get('raw_text', r.get('label_raw')))):
                                    if label_text is not None:
                                        label_id = hashlib.sha256(canonical([key, variant, source.get('producer_version', source['name'])]).encode()).hexdigest()
                                        label = self.find('label_versions', [label_id])
                                        require(label is not None and label['text'] == label_text and label['text_sha256'] == hashlib.sha256(label_text.encode()).hexdigest(), 'source label variant omitted/changed')
                                if adapter == 'census':
                                    require(row['census_disposition'] == r['disposition'] and row['census_reasons'] == r['reasons'], 'source census verdict/reasons changed')
                                if r.get('crop_sha256'):
                                    require(row.get('crop_sha256') == r['crop_sha256'], 'original crop source hash changed')
                                if source.get('keyset') and all(get(r, k) == v for k, v in source.get('keyset_where', {}).items()):
                                    keyset_key = 'harvest:' + r['wave'] + ':' + str(ident) if adapter == 'harvest' else str(ident)
                                    if source.get('keyset_key'):
                                        keyset_key = key if source['keyset_key'] == 'row_key' else str(get(r, source['keyset_key']))
                                    self.db.execute('INSERT INTO source_sets VALUES(?,?)', (source['keyset'], keyset_key))
                                    self.db.execute('INSERT INTO source_tuples VALUES(?,?,?)', (source['keyset'], keyset_key, key))
                            elif adapter == 'prepared':
                                lid = r['line_id']
                                b = original.get('image_png')
                                require(isinstance(b, bytes), 'prepared source payload missing')
                                if source.get('keyset') and not source.get('synthetic'):
                                    suffix = 'harvest' if lid.startswith('harvest:') else 'v4'
                                    self.db.execute('INSERT INTO source_sets VALUES(?,?)', (source['keyset'] + '_' + suffix, lid))
                                for model in self.lock['models']:
                                    identity = (['prepared-position-v1', model, source['role'], source['pool'],
                                                 source.get('variant', 'prepared005'), source['factory_build_id'], file['path'], ordinal]
                                                if source.get('synthetic') else
                                                [model, source['role'], source['pool'], lid, source.get('variant', 'prepared005')])
                                    member = self.find('training_membership', [digest(canonical(identity))])
                                    require(member is not None, 'prepared source key omitted')
                                    require(member['image_sha256'] == hashlib.sha256(b).hexdigest(), 'source trainer image differs')
                                    require(member['source_ordinal'] == ordinal and member['source_shard'] == file['path'], 'trainer ordinal/shard changed')
                                    require(member['pool_order'] == offset + ordinal, 'trainer pool order changed')
                                    if source.get('synthetic'):
                                        attributes = {k: r.get(k, 0 if k == 'reuse_index' else None) for k in SYNTHETIC_MATCH_FIELDS}
                                        expected_group = digest(canonical([source['factory_build_id'], hashlib.sha256(b).hexdigest(), attributes]))
                                        require(member['synthetic_match_group'] == expected_group, 'prepared source native attributes differ')
                                    require(all(member.get(k) == r.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')), 'source trainer labels/codec differ')
                            elif adapter == 'synthetic':
                                line = self.find('synthetic', [source['factory_build_id'], r['split'], file['path'], ordinal])
                                require(line is not None, 'A12 source observation omitted')
                                require(line['image_sha256'] == hashlib.sha256(original['image_png']).hexdigest(), 'A12 source image differs')
                                require(all(line.get(k) == r.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version', 'applied_ops', 'severity', 'split')), 'A12 source label/operations changed')
                                require(line['synthetic_native_attributes_json'] ==
                                        {k: r.get(k, 0 if k == 'reuse_index' else None) for k in SYNTHETIC_MATCH_FIELDS},
                                        'A12 native attributes differ')
                            elif adapter == 'table':
                                table = source['table']
                                if table == 'row_instruments' and source.get('exact_original_ids'):
                                    # These are original-ID declarations, not
                                    # release tuples. Book coverage replays all
                                    # declarations and public flags/FKs above.
                                    self.source_checks += 1
                                    continue
                                fields = source.get('keys', KEYS[table])
                                if table in ('references', 'row_instruments') and not r.get('row_key'):
                                    require(r.get('parent_id') is not None and r.get('row_id') is not None, 'source relation replay needs explicit original tuple')
                                    r['row_key'] = hashlib.sha256(canonical([r['parent_id'], r['row_id']]).encode()).hexdigest()
                                public = self.find(table, [r[k] for k in fields])
                                require(public is not None, 'source relation key omitted: ' + table)
                                def normal(v):
                                    if isinstance(v, str) and v.lstrip().startswith(('{', '[')):
                                        try:
                                            return json.loads(v)
                                        except ValueError:
                                            pass
                                    return v
                                for k, expected in r.items():
                                    if k in PRIVATE or k in ('image', 'image_png', 'image_bytes'):
                                        continue
                                    binding = self.policy.columns(table).get(k)
                                    if binding and self.policy.status(binding) == 'historical_unknown':
                                        require(public.get(k) is None, 'historical source FK fabricated: ' + table + '.' + k)
                                        if expected is not None:
                                            if k == 'page_id':
                                                refs = as_json(public.get('source_page_references_json')) or []
                                                require(any(v['selector'] == k and v['id'] == str(expected) for v in refs),
                                                        'native page reference lost: ' + table)
                                            else:
                                                require(normal(public.get('source_' + k)) == normal(expected),
                                                        'native source FK evidence lost: ' + table + '.' + k)
                                        continue
                                    actual = public.get(k)
                                    require(normal(actual) == normal(expected) or str(actual) == str(expected),
                                            'retained source relation field differs: ' + table + '.' + k)
                                if table == 'page_images':
                                    binary = original.get('image_bytes', original.get('image_png'))
                                    if binary is None and isinstance(original.get('image'), dict):
                                        binary = original['image'].get('bytes')
                                    require(binary is not None and public['image_sha256'] == hashlib.sha256(binary).hexdigest(), 'source page raster bytes differ')
                                for k in ('status', 'split', 'kind', 'list_name', 'list_sha256', 'diagnostic_only'):
                                    if r.get(k) is not None:
                                        require(public.get(k) == r[k], 'source relation field changed: ' + table + '.' + k)
                            elif adapter == 'keyset':
                                key = str(get(r, source['key_field']))
                                self.db.execute('INSERT INTO source_sets VALUES(?,?)', (source['keyset'], key))
                            self.source_checks += 1
                    state['offset'] += scanned
        with self.ledger.unit('source-replay:keyset-closure') as run:
            if run:
                self.source_keyset_closure()
        return True

    def source_keyset_closure(self):
        for union, members in self.lock.get('keyset_unions', {}).items():
            for member in members:
                self.db.execute('INSERT OR IGNORE INTO source_sets SELECT ?,k FROM source_sets WHERE s=?', (union, member))
        for bridge in self.lock.get('keyset_bridges', []):
            missing = self.db.execute('SELECT k FROM source_sets WHERE s=? EXCEPT SELECT k FROM source_tuples WHERE s=?',
                                      (bridge['left'], bridge['right'])).fetchone()
            require(missing is None, 'source original-tuple bridge lacks a unique right tuple: ' + bridge['name'])
            self.db.execute('INSERT INTO source_sets SELECT ?,r.row_key FROM source_sets l JOIN source_tuples r '
                            'ON l.k=r.k WHERE l.s=? AND r.s=?', (bridge['name'], bridge['left'], bridge['right']))
        names = [s for s, in self.db.execute('SELECT DISTINCT s FROM source_sets ORDER BY s')]
        require(set(names) == {s for s, in self.db.execute('SELECT DISTINCT s FROM sets')}, 'keyset provenance coverage differs')
        for name in names:
            for sql in ('SELECT k FROM source_sets WHERE s=? EXCEPT SELECT k FROM sets WHERE s=?',
                        'SELECT k FROM sets WHERE s=? EXCEPT SELECT k FROM source_sets WHERE s=?'):
                require(self.db.execute(sql, (name, name)).fetchone() is None, 'source keyset differs from package: ' + name)

    @contextual
    def run(self):
        nfiles = self.byte_check()
        if self.lock_path:
            # Hash each pinned external file once, on the allocated CPUs. Later
            # phases reuse only this ledger's unchanged-file verification.
            external = json.loads(Path(self.lock_path).read_text())
            entries = [entry for source in external['inputs'] for entry in source['files']]
            entries += [entry for source in external['inputs']
                        for entry in source.get('original_crops_source', {}).get('files', [])]
            entries += external.get('assets', [])
            entries += [external['features'][name] for name in ('codec', 'scripts')]
            # Multiple declarations may legitimately pin the same physical file.
            pins = {}
            for entry in entries:
                path = str(Path(entry['path']).resolve())
                require(path not in pins or (pins[path]['sha256'], pins[path]['bytes']) ==
                        (entry['sha256'], entry['bytes']), 'conflicting readback file pins: ' + path)
                pins[path] = entry
            self.ledger.verify_many(pins.values())
        self.ledger.stage('load_tables', self.load_tables)
        self.smoke_skip_allowed('', '', '', [])
        self.ledger.stage('binding_checks', self.binding_checks)
        self.ledger.stage('semantics', self.semantics)
        self.ledger.stage('reconciliation', self.reconciliation)
        self.ledger.stage('coverage_and_features', self.coverage_and_features)
        self.ledger.stage('source_binding_replay', self.source_binding_replay)
        original_images = self.ledger.stage('original_source_replay', self.original_source_replay)
        sources = self.ledger.stage('source_replay', self.source_replay)
        layered = bool(self.manifest.get('layout'))
        declared = card_recipe = enrichment = None
        if layered:
            from .accept_layers import raw_acceptance
            from . import layer_acceptance
            self.ledger.stage('raw_acceptance', lambda: raw_acceptance(self))
            declared = self.ledger.stage('declared_configs', lambda: layer_acceptance.declared_configs(self, strict=self.final))
            enrichment = self.enrichment_stage()
            if self.final:
                require(self.manifest.get('frozen_trained', {}).get('schema') == 'hfd-frozen-trained-v1',
                        'final acceptance requires the A1-mapped frozen trained view')
                card_recipe = self.ledger.stage('card_recipe', lambda: layer_acceptance.card_recipe(self))
        declared_ok = bool(declared and declared.get('status') == 'PASS')
        loader_ok = self.loader.startswith('datasets:') or declared_ok
        qualified_loading = not layered or (self.frozen_available and {'real', 'synthetic'} <= self.manifest['configs'].keys() and loader_ok)
        sources_ok = bool(sources) and not self.policy.smoke and qualified_loading
        if not layered:
            status = 'PASS' if sources_ok else 'SELF_CHECK_ONLY'
        elif not sources_ok:
            status = 'SELF_CHECK_ONLY'
        elif not self.final:
            # Source-backed, but the literal card recipe was not executed: never a release PASS.
            status = 'SOURCE_PASS_NOT_FINAL'
        else:
            require(card_recipe and card_recipe.get('status') == 'PASS', 'final acceptance requires the card recipe')
            status = 'PASS'
        a1_binding = {'external-cache': 'packaged A1.json + occurrence mapping + external A1 replay',
                      'complete-download': 'packaged A1.json + occurrence mapping (portable)',
                      'complete-download-a1-source': 'packaged A1.json + occurrence mapping + external A1 replay'}
        return {'status': status, 'final_acceptance': self.final,
                'frozen_loading_verified': qualified_loading,
                'card_join_rows': getattr(self, 'roundtrip_rows', None),
                'card_recipe': card_recipe, 'declared_configs': declared, 'enrichment': enrichment,
                'a1_binding': a1_binding[self.validation_mode] if layered and self.frozen_available else None,
                'validation_mode': self.validation_mode,
                'source_acceptance': sources, 'smoke': self.receipt['mode'] == 'smoke',
                'smoke_unloaded_targets': self.receipt.get('smoke_unloaded_targets', {}),
                'manifest_files': nfiles, 'embedded_images_checked': self.image_count,
                'independent_feature_variants_checked': self.feature_checks,
                'source_records_checked': self.source_checks, 'config_loader': self.loader,
                'source_binding_records_checked': self.binding_source_checks,
                'original_images_replayed': original_images,
                'binding_acceptance': self.policy.report(),
                'public_visibility_refs_archive_privacy': 'coordinator publication readback, outside offline builder'}


def itertools_first(iterator):
    for item in iterator:
        yield item
        break


def failure_message(exc):
    """Keep every chained traceback frame, including the original lookup site."""
    chain, seen = [], set()
    current = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        current = current.__cause__ or (None if current.__suppress_context__ else current.__context__)
    lines = ['acceptance failed: ' + str(exc), 'traceback (original cause first):']
    for error in reversed(chain):
        lines.append(type(error).__name__ + ': ' + str(error))
        for frame in traceback.extract_tb(error.__traceback__):
            lines.append(f'  {frame.filename}:{frame.lineno} in {frame.name}')
            if frame.line:
                lines.append('    ' + frame.line)
    return '\n'.join(lines)


@contextual
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--input-lock', type=Path)
    p.add_argument('--allow-smoke', action='store_true')
    p.add_argument('--validation-mode', choices=VALIDATION_MODES, default='complete-download',
                   help='build uses external-cache; CP-release uses complete-download (portable: packaged A1.json '
                        '+ occurrence mapping) or complete-download-a1-source (also replays the source A1 receipt)')
    p.add_argument('--final', action='store_true',
                   help='release acceptance: also execute the card recipe and README config emulation; only this can PASS')
    p.add_argument('--enrich-base', type=Path, help='base candidate C bound by a C′ ENRICH_RECEIPT.json')
    p.add_argument('--scratch', type=Path, help='durable private readback ledger')
    p.add_argument('--resume', action='store_true')
    p.add_argument('--deadline-seconds', type=float)
    p.add_argument('--report', type=Path, help='fresh report outside candidate directory')
    args = p.parse_args(argv)
    offline()
    if args.report:
        require(not args.report.exists(), 'report must be fresh')
        require(args.root.resolve() not in args.report.resolve().parents, 'report must stay outside candidate')
    from contextlib import nullcontext
    from .deadline import Deadline, BuildPaused
    if args.resume and not args.scratch:
        p.error('--resume requires --scratch')
    if args.deadline_seconds is not None and (not args.scratch or args.deadline_seconds <= 0):
        p.error('--deadline-seconds requires durable --scratch and a positive budget')
    deadline = Deadline(args.deadline_seconds)
    with (nullcontext(args.scratch) if args.scratch else tempfile.TemporaryDirectory(prefix='rel0-accept-')) as scratch:
        verifier = None
        try:
            with deadline:
                verifier = Acceptance(args.root, scratch, args.input_lock, args.allow_smoke, resume=args.resume,
                                      validation_mode=args.validation_mode, final=args.final,
                                      enrich_base=args.enrich_base)
                verifier.db.set_progress_handler(deadline.interrupt_sql, 10000)
                result = verifier.run()
        except (BuildPaused, sqlite3.OperationalError):
            if not deadline.expired:
                raise
            print(canonical({'status': 'PAUSED', 'scratch': str(scratch)}))
            return 0
        finally:
            if verifier:
                verifier.db.set_progress_handler(None, 0)
                verifier.db.rollback()
                verifier.db.close()
    if args.report:
        atomic_json(args.report, result)
    print(canonical(result))
    if result['status'] == 'PASS' or args.allow_smoke:
        return 0
    return 3 if result['status'] == 'SOURCE_PASS_NOT_FINAL' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(failure_message(exc), file=sys.stderr)
        sys.exit(2)
