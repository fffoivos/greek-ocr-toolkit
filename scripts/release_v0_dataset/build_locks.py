"""Shared validation of the credential-free P2c lock wire formats."""
import json
import re
from pathlib import PurePosixPath

from . import card
from .common import verify_file, sha
from .frozen_identity import occurrence_mapping

REVISION = '859fa9873d5ed23e49f01ae7628be6ef3d9c4e50'
WAVES = ('W3', 'W4', 'W3b-1', 'W3b-2', 'W3c-1', 'W5-1', 'W5-2', 'W5-3')


def validate_frozen(value, a1_path=None):
    paths = []
    configs = {}
    for f in value['files']:
        p = PurePosixPath(f['path'])
        if p.is_absolute() or '..' in p.parts or len(p.parts) < 4 or p.parts[:2] not in (('data', 'real'), ('data', 'synthetic')):
            raise ValueError('invalid frozen trained path')
        if not re.fullmatch('[0-9a-f]{64}', f['sha256']) or not isinstance(f['bytes'], int) or f['bytes'] <= 0:
            raise ValueError('invalid frozen LFS size/SHA')
        paths.append(f['path'])
        configs.setdefault(p.parts[1], {}).setdefault(p.parts[2], []).append(f['path'])
    if not paths or len(paths) != len(set(paths)) or value['configs'] != configs:
        raise ValueError('frozen inventory/configs differ or contain duplicate paths')
    if value['revision'] != REVISION:
        raise ValueError('frozen revision differs from public tree pin')
    if not PurePosixPath(value.get('public_snapshot_root', '')).is_absolute():
        raise ValueError('frozen lock requires an absolute public snapshot root')
    mapping = value.get('occurrence_mapping', [])
    if len(mapping) != len(paths) or {f['public_path'] for f in mapping} != set(paths):
        raise ValueError('frozen occurrence mapping differs from inventory')
    if a1_path:
        if sha(a1_path) != value['a1']['sha256']:
            raise ValueError('frozen A1 SHA mismatch')
        report = card.validate_a1(json.loads(a1_path.read_text()))
        if mapping != occurrence_mapping(report):
            raise ValueError('frozen occurrence mapping differs from A1')
        if report['revision'] != value['revision'] or report['repo'] != value['repo']:
            raise ValueError('A1 revision/repo differs from frozen tree')
        if report.get('first_20_mismatches') or any(f.get('first_20_mismatches') for f in report['files']):
            raise ValueError('A1 contains mismatches')
        by_path = {f['public_path']: f for f in report['files']}
        if len(by_path) != len(report['files']) or set(by_path) != set(paths):
            raise ValueError('A1 and frozen trained paths differ')
        for f in value['files']:
            a = by_path[f['path']]
            if (a['public_sha256'] != f['sha256'] or a['pool'] != f['pool'] or a['source_shard'] != f['source_shard']
                    or a['prepared_rows'] != a['public_rows'] or a['prepared_ordered_digest'] != a['public_ordered_digest']):
                raise ValueError('A1 frozen shard identity differs')
    return value


def validate_labels(value, smoke=None):
    if value.get('partial') and not smoke:
        raise ValueError('partial label lock is smoke only')
    if set(value['per_wave']) != set(WAVES):
        raise ValueError('label lock must account for every wave')
    if not value.get('partial') and any(not v['complete'] or not v['raw_hash_equal'] for v in value['per_wave'].values()):
        raise ValueError('incomplete label waves')
    for entry in value['files']:
        verify_file(entry)
    inventory = {(f['path'], f['bytes'], f['sha256']) for f in value['files']}
    for adapter in value['label_variant_adapters']:
        for f in adapter['files']:
            if (f['path'], f['bytes'], f['sha256']) not in inventory:
                raise ValueError('adapter file absent from label lock inventory')
    if set(value['raw_text_responses']) != set(WAVES):
        raise ValueError('missing wave response binding')
    return value
