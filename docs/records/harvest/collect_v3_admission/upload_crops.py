"""Manifest-only transfer, followed by destination byte verification.

CROPS3_MOCK_REMOTE is a local directory; that branch never invokes ssh/rsync.
CROPS3_MOCK_CORRUPT is a test-only relative path corrupted after the mock copy.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

REMOTE = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_w2_originals/'


def stamp():
    return subprocess.check_output(['date', '+%Y-%m-%dT%H:%M:%S%z'],
                                   env=dict(os.environ, TZ='Europe/Athens'), text=True).strip()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def upload(tree, manifest):
    tree, manifest = Path(tree).resolve(), Path(manifest).resolve()
    mock = os.environ.get('CROPS3_MOCK_REMOTE')
    receipt = dict(file_count=0, bytes=0, mismatches=0, remote_path=REMOTE,
                   started_at=stamp(), mode='local-mock' if mock else 'clariden', status='failed')
    try:
        rows = [json.loads(s) for s in manifest.read_text().splitlines() if s.strip()]
        if not rows:
            raise ValueError('empty manifest')
        for failure in manifest.parent.glob('*_failures.jsonl'):
            if failure.read_text().strip():
                raise ValueError('nonempty failure sidecar: ' + str(failure))
        for state in manifest.parent.glob('*_receipt.json'):
            r = json.loads(state.read_text())
            if r.get('output_root') and Path(r['output_root']).resolve() == tree and (r.get('failures', 0) or r.get('disk_deferred', 0)):
                raise ValueError('incomplete staging receipt: ' + str(state))
        paths, checks = [], []
        for row in rows:
            if row.get('failure') or row.get('failures') or row.get('error') or row.get('pass') is False or row.get('status') in ('failure', 'failed') or row.get('reason'):
                raise ValueError('failure row in manifest')
            if row.get('admitted', True) is False:
                continue
            source, key = row['source'], row['row_id']
            if not all(isinstance(v, str) and re.fullmatch(r'[A-Za-z0-9_.-]+', v) and v not in ('.', '..') for v in (source, key)):
                raise ValueError('unsafe source/row_id')
            relative = source + '/' + key + '.png'
            # Legacy stager paths are relative to the manifest directory.
            path = manifest.parent / row['path']
            if path.is_symlink() or path.resolve() != tree / relative or not path.resolve().is_relative_to(tree):
                raise ValueError('manifest path does not match tree/source/row_id')
            if relative in paths:
                raise ValueError('duplicate manifest path')
            if not re.fullmatch('[0-9a-f]{64}', row['sha256']):
                raise ValueError('invalid checksum')
            if digest(path) != row['sha256'] or path.stat().st_size != row['bytes']:
                receipt['mismatches'] += 1
                raise ValueError('local hash/size mismatch: ' + relative)
            paths.append(relative)
            checks.append(row['sha256'] + '  ' + relative + '\n')
            receipt['bytes'] += row['bytes']
        if not paths:
            raise ValueError('zero active manifest rows')
        receipt['file_count'] = len(paths)
        with tempfile.TemporaryDirectory(prefix='crops3-upload-') as temporary:
            temporary = Path(temporary)
            checksum = temporary / 'crops_sha256.txt'
            checksum.write_text(''.join(checks))
            filelist = temporary / 'files.txt'
            filelist.write_text('\n'.join(paths) + '\n')
            if mock:
                destination = Path(mock).resolve()
                if destination == tree or destination.is_relative_to(tree) or tree.is_relative_to(destination):
                    raise ValueError('mock destination overlaps local tree')
                destination.mkdir(parents=True, exist_ok=True)
                for relative in paths:
                    target = destination / relative
                    if target.is_symlink() or not target.resolve().is_relative_to(destination):
                        raise ValueError('unsafe mock target')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(tree / relative, target)
                shutil.copyfile(checksum, destination / checksum.name)
                corrupt = os.environ.get('CROPS3_MOCK_CORRUPT')
                if corrupt:
                    if corrupt not in paths:
                        raise ValueError('mock corruption must select a manifest path')
                    (destination / corrupt).write_bytes(b'injected corruption\n')
                result = subprocess.run(['sha256sum', '-c', checksum.name], cwd=destination,
                                        text=True, capture_output=True)
            else:
                subprocess.run(['ssh', 'clariden', 'mkdir -p ' + shlex.quote(REMOTE)], check=True)
                subprocess.run(['rsync', '-rt', '--files-from=' + str(filelist), str(tree) + '/', 'clariden:' + REMOTE], check=True)
                subprocess.run(['rsync', '-rt', str(checksum), 'clariden:' + REMOTE + checksum.name], check=True)
                result = subprocess.run(['ssh', 'clariden', 'cd ' + shlex.quote(REMOTE) + ' && sha256sum -c ' + checksum.name],
                                        text=True, capture_output=True)
            receipt['checksum_stdout'] = result.stdout
            receipt['checksum_stderr'] = result.stderr
            receipt['mismatches'] = sum(': FAILED' in line for line in result.stdout.splitlines())
            if result.returncode:
                receipt['mismatches'] = max(1, receipt['mismatches'])
                raise ValueError('destination checksum verification failed')
        receipt['status'] = 'verified'
        return 0
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        receipt['error'] = str(error)
        return 1
    finally:
        receipt['finished_at'] = stamp()
        target = manifest.parent / 'upload_receipt.json'
        fd, name = tempfile.mkstemp(prefix='.upload_receipt-', dir=target.parent)
        with os.fdopen(fd, 'w') as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write('\n')
        os.replace(name, target)
        print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: upload_crops.sh <local tree> <manifest>')
    sys.exit(upload(*sys.argv[1:]))
