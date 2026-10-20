"""Stage original admitted crops offline; metadata lives beside --out.

Run with ~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python.
The live collector run is read-only. Only ensure_crop's output path changes.
"""
import argparse
import hashlib
import gzip
import shutil
import json
import os
from pathlib import Path
import sys

INTERPRETER = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'
COLLECTOR = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect'
W2_PARENT = 'collect-v3-W2-20261018-0524'
READ_ONLY = (Path.home() / 'Projects/collect-v3-data/run', Path.home() / 'Projects/collect-v3-data/snapshots')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def component(value):
    if not isinstance(value, str) or not value or value in ('.', '..') or '/' in value or '\\' in value:
        raise ValueError('unsafe path component')
    return value


def write_if_changed(path, data, atomic_bytes):
    if not path.exists() or path.read_bytes() != data:
        atomic_bytes(path, data)


def adapt_admission(rows):
    """Census exports retain canonical `id`; older admissions use `row_id`."""
    census = any('parent_id' in r for r in rows)
    if census:
        if any('parent_id' not in r for r in rows):
            raise ValueError('mixed census/legacy admission formats')
        rows = [r for r in rows if r['parent_id'] == W2_PARENT]
        if not rows:
            raise ValueError('zero W2 rows in admission')
    result = []
    for row in rows:
        key = row.get('row_id', row.get('id'))
        component(key)
        if 'id' in row and 'row_id' in row and row['id'] != row['row_id']:
            raise ValueError('conflicting admission row identities')
        if not census and (row.get('pass') is False or row.get('admitted') is False):
            raise ValueError('non-admitted row in admission input')
        if census and (row.get('split', 'train') != 'train' or
                       row.get('decision', {}).get('disposition', 'ADMIT') != 'ADMIT'):
            raise ValueError('non-ADMIT/train census row')
        result.append(dict(row, row_id=key))
    if not result:
        raise ValueError('zero admitted rows')
    return result, 'census' if census else 'legacy'


def guard_output(out, features):
    # Guard the metadata directory too: metadata lives beside --out.
    output = out.parent.resolve()
    for protected in (*READ_ONLY, features.parent):
        protected = protected.resolve()
        if output.is_relative_to(protected) or out.resolve().is_relative_to(protected) or protected.is_relative_to(out.resolve()):
            raise ValueError('output/metadata overlaps read-only input root')


def stage(admitted, features, out, *, extend=False, minimum_free_gb=10):
    if not os.path.samefile(sys.executable, INTERPRETER):
        raise RuntimeError('use ' + str(INTERPRETER))
    sys.path.insert(0, str(COLLECTOR))
    from collect_v3.storage import ensure_crop
    from collect_v3.common import atomic_bytes
    import PIL

    admitted, features, out = (Path(p).expanduser().absolute() for p in (admitted, features, out))
    guard_output(out, features)
    if minimum_free_gb < 0:
        raise ValueError('negative disk floor')
    if admitted.resolve().is_relative_to(out.resolve()):
        raise ValueError('admitted input is inside output')
    data = gzip.decompress(admitted.read_bytes()) if admitted.suffix == ".gz" else admitted.read_bytes()
    rows = [json.loads(line) for line in data.splitlines() if line.strip()]
    rows, admission_format = adapt_admission(rows)
    applications = {r.get('application_manifest_sha256', r.get('admission', {}).get('application_manifest_sha256')) for r in rows}
    if len(applications) > 1:
        raise ValueError('mixed application identities')
    application = next(iter(applications), None)
    ids = [row['row_id'] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate admitted row_id')
    wanted = set(ids)
    joined = {}
    feature_hash = hashlib.sha256()
    # One read-only descriptor, no locks, no collector materialize/finalize calls.
    with features.open('rb') as stream:
        before = os.fstat(stream.fileno())
        for line in stream:
            feature_hash.update(line)
            if not line.strip():
                continue
            row = json.loads(line)
            key = row.get('row_id', row.get('id'))
            if key in wanted:
                if key in joined:
                    raise ValueError('duplicate feature row_id: ' + key)
                joined[key] = row
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('features changed during read; retry against a stable file')
    if admission_format == 'legacy' and any(f.get('tranche') == 'W2' for f in joined.values()):
        # Select the W2 cohort even when legacy input contains other waves.
        rows = [dict(r, parent_id=W2_PARENT) for r in rows
                if joined.get(r['row_id'], {}).get('tranche') == 'W2']
    if 'W2' in features.name and not any(f.get('tranche') == 'W2' for f in joined.values()):
        raise ValueError('zero W2 rows in admission')
    old_path = out.parent / "crops_manifest.jsonl"
    previous = [json.loads(line) for line in old_path.read_text().splitlines()] if old_path.exists() else []
    if len({r["row_id"] for r in previous}) != len(previous):
        raise ValueError("duplicate previous manifest row_id")
    manifest, failures = [], []
    disk_deferred = []
    new_count = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    free_before = shutil.disk_usage(out.parent).free
    verified_sources = set()
    for index, row in enumerate(rows, 1):
        key = row['row_id']
        try:
            source = component(row['source'])
            component(key)
            feature = joined[key]
            for field in ('source', 'crop_bbox', 'crop_sha256'):
                if row[field] != feature[field]:
                    raise ValueError('admitted/feature mismatch: ' + field)
            path = out / source / (key + '.png')
            if path.is_symlink() or not path.resolve().is_relative_to(out.resolve()):
                raise ValueError('output path escapes root')
            # Also verify retained sources on resumed runs (ensure_crop returns early
            # for an already present, hash-matching PNG).
            source_key = (feature['crop_source_image'], feature['crop_source_sha256'])
            if path.exists() and source_key not in verified_sources:
                if sha(feature['crop_source_image']) != feature['crop_source_sha256']:
                    raise ValueError('crop source hash mismatch')
                verified_sources.add(source_key)
            new = not path.exists()
            if not new and sha(path) != feature['crop_sha256']:
                raise ValueError('existing staged crop hash mismatch')
            # Reserve a conservative raw pixel bound before each new PNG. A
            # below-floor run can still verify already staged, byte-exact files.
            x0, y0, x1, y1 = feature['crop_bbox']
            reserve = 2 * (x1-x0) * (y1-y0) + 1_000_000
            if new and shutil.disk_usage(out.parent).free - reserve < minimum_free_gb * 1_000_000_000:
                disk_deferred.append(dict(row_id=key, source=source, reason='disk_floor', minimum_free_gb=minimum_free_gb))
                continue
            if row.get('parent_id') == W2_PARENT and feature.get('tranche') != 'W2':
                raise ValueError('census parent/feature tranche mismatch')
            ensure_crop(dict(feature, crop=str(path)))
            new_count += int(new)
            digest = sha(path)
            if digest != feature['crop_sha256']:
                raise ValueError('staged crop hash mismatch')
            manifest.append(dict(row_id=key, parent_id=row.get('parent_id'), source=source, admitted=True,
                                 **{'class': row.get('primary_class', row.get('class', row.get('admission', {}).get('class')))},
                                 path=path.relative_to(out.parent).as_posix(),
                                 sha256=digest, bytes=path.stat().st_size))
        except (OSError, ValueError, KeyError) as error:
            failures.append(dict(row_id=key, source=row.get('source'), reason=f'{type(error).__name__}: {error}'))
        if index % 1000 == 0 or index == len(rows):
            print(f'{index}/{len(rows)} processed; {len(failures)} failures', flush=True)
    active_count = len(manifest)
    staged_ids = {r["row_id"] for r in manifest}
    for row in previous:
        if row["row_id"] not in staged_ids:
            retained = out.parent / row["path"]
            if not retained.resolve().is_relative_to(out.resolve()) or retained.is_symlink():
                raise ValueError("withdrawn path escapes crops root")
            if sha(retained) != row["sha256"]:
                raise ValueError("withdrawn crop hash mismatch")
            manifest.append(dict(row, admitted=row.get("admitted", True) if extend else False))
    # Validate the complete replacement custody immediately before publication.
    for entry in manifest:
        retained = out.parent / entry['path']
        if retained.is_symlink() or not retained.resolve().is_relative_to(out.resolve()):
            raise ValueError('retained path escapes crops root')
        if sha(retained) != entry['sha256'] or retained.stat().st_size != entry['bytes']:
            raise ValueError('retained crop hash/size mismatch')
    manifest.sort(key=lambda r: r["row_id"])
    receipt = dict(count=active_count, retained_count=len(manifest), withdrawn_count=sum(not r["admitted"] for r in manifest), total_bytes=sum(r['bytes'] for r in manifest),
                   failures=len(failures), admitted_count=len(rows), admission_format=admission_format,
                   admitted_file=str(admitted), admitted_sha256=hashlib.sha256(data).hexdigest(),
                   features_file=str(features), features_sha256=feature_hash.hexdigest(),
                   interpreter_path=str(INTERPRETER), interpreter_executable=sys.executable,
                   interpreter_version=sys.version, pillow_version=PIL.__version__,
                   collector_storage_sha256=sha(COLLECTOR / 'collect_v3/storage.py'),
                   manifest_path_base='parent of --out', output_root=str(out))
    if application is not None:
        receipt['application_manifest_sha256'] = application
        for entry in manifest:
            if entry['row_id'] in staged_ids:
                entry['application_manifest_sha256'] = application
    if extend or minimum_free_gb:
        receipt.update(extend=extend, new_count=new_count, disk_deferred=len(disk_deferred),
                       minimum_free_gb=minimum_free_gb, free_before=free_before,
                       free_after=shutil.disk_usage(out.parent).free)
    prefix = admitted.name.removesuffix('.gz').removesuffix('.jsonl') + '_crops' if extend else 'crops'
    for name, content in (
        ('crops_manifest.jsonl', ''.join(encode(r) + '\n' for r in manifest)),
        (prefix + '_failures.jsonl', ''.join(encode(r) + '\n' for r in failures)),
        (prefix + '_receipt.json', json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + '\n'),
    ):
        if name == "crops_manifest.jsonl" and failures:
            continue  # A failed retained/admitted validation cannot replace custody.
        write_if_changed(out.parent / name, content.encode(), atomic_bytes)
    if extend:
        write_if_changed(out.parent / (prefix + '_deferred.jsonl'), ''.join(encode(r) + '\n' for r in disk_deferred).encode(), atomic_bytes)
    print(encode(receipt), flush=True)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--admitted', required=True, type=Path)
    parser.add_argument('--features', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--extend', action='store_true', help='preserve prior tranche manifest membership')
    parser.add_argument('--minimum-free-gb', type=float, default=10, help='decimal GB floor for new images')
    args = parser.parse_args()
    receipt = stage(args.admitted, args.features, args.out, extend=args.extend, minimum_free_gb=args.minimum_free_gb)
    return 1 if receipt['failures'] else 2 if receipt.get('disk_deferred', 0) else 0


if __name__ == '__main__':
    sys.exit(main())
