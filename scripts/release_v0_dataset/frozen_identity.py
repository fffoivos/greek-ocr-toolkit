"""A1 occurrence locators and its exact ordered logical-row digest contract."""
from pathlib import Path, PurePosixPath
import re

from . import card
from .common import digest, safe_path


def occurrence_mapping(report):
    """Use only A1, including its SHA-bound run runtime root for relative shards."""
    card.validate_a1(report)
    roots = set()
    for binding in report.get('run_bindings', []):
        runtime = binding['runtime']
        if (binding['status'] != 'PASS' or runtime['sha256'] != report['runtime_sha256']
                or not PurePosixPath(runtime['path']).is_absolute()
                or binding.get('config', {}).get('runtime', runtime) != runtime):
            raise ValueError('A1 prepared runtime binding differs')
        roots.add(PurePosixPath(runtime['path']).parent)
    result = []
    for f in report['files']:
        source = PurePosixPath(f['source_shard'])
        if '..' in source.parts or not source.parts:
            raise ValueError('unsafe A1 source shard')
        if not source.is_absolute():
            if len(roots) != 1:
                raise ValueError('A1 relative shard requires one bound prepared runtime root')
            source = next(iter(roots)) / source
        if (f['prepared_sha256'] != f['expected_prepared_sha256']
                or f['public_rows'] != f['prepared_rows']
                or f['public_ordered_digest'] != f['prepared_ordered_digest']
                or any(not re.fullmatch('[0-9a-f]{64}', f[k]) for k in
                       ('prepared_sha256', 'public_sha256', 'public_ordered_digest'))):
            raise ValueError('A1 occurrence identity differs')
        result.append(dict(public_path=f['public_path'], pool=f['pool'],
            source_shard=f['source_shard'], prepared_path=str(source),
            prepared_sha256=f['prepared_sha256'], public_sha256=f['public_sha256'],
            rows=f['public_rows'], ordered_digest=f['public_ordered_digest']))
    if len({(f['pool'], f['prepared_path']) for f in result}) != len(result):
        raise ValueError('duplicate A1 prepared occurrence shard')
    return sorted(result, key=lambda f: f['public_path'])


def public_file(root, relative):
    """Resolve HF snapshot symlinks to blobs; callers verify pinned public bytes.

    The frozen cache is external to the public package (whose symlinks stay banned).
    """
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('unsafe frozen public path')
    return safe_path(Path(root), str(path), allow_hf_cache=True).resolve(strict=True)


def public_logical(row, pool, source, ordinal):
    """Exact A1 logical(public=True) contract."""
    # See scripts/hf_datasets/check_trained_identity.py; regression tests compare
    # directly to that implementation without making it a runtime dependency.
    if 'license' in row:
        raise ValueError('unexpected_public_license_column')
    image = row.get('image')
    binary = image.get('bytes') if isinstance(image, dict) else image
    if not isinstance(binary, (bytes, bytearray)):
        raise ValueError('missing embedded image bytes')
    required = ('gt_nfd', 'gt_nfc', 'label_ids', 'codec_version', 'split', 'line_id')
    result = {k: row[k] for k in required}
    result.update(image_sha256=digest(bytes(binary)), pool=row.get('pool'),
                  occurrence=[pool, source, ordinal],
                  metadata={k: v for k, v in row.items()
                            if k not in ('image', 'image_png', 'license', 'pool')})
    return result
