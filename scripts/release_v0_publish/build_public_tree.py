"""Export a commit's git-archive snapshot, filter it, and validate the assembled tree.

Usage: python -B scripts/release_v0_publish/build_public_tree.py <commit> <out_dir>
Git is used only for read-only rev-parse/archive; no index/ref/worktree mutation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.release_v0_publish.prepare_evidence import PACKAGES
from scripts.release_v0_publish.inventory import (
    MAX_BYTES, inventory, write_tsv, write_review_outputs, write_sharded_tsv,
)

ROOT = Path(__file__).resolve().parents[2]
TESTS = ['tests/train', 'tests/deploy', 'tests/release_v0',
         'tests/test_montage.py', 'tests/test_provenance_cli_api.py']


def archive_commit(repo, commit, destination):
    """git archive honors committed export-ignore/export-subst; never reads worktree bytes."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_REPLACE_OBJECTS='1')
    resolved = subprocess.check_output(['git', 'rev-parse', '--verify', commit+'^{commit}'],
                                       cwd=repo, env=env, text=True).strip()
    with tempfile.TemporaryFile() as stream:
        subprocess.run(['git', 'archive', '--format=tar', resolved], cwd=repo,
                       env=env, stdout=stream, check=True)
        stream.seek(0)
        names = []
        with tarfile.open(fileobj=stream, mode='r:') as archive:
            for member in archive:
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
                    raise ValueError('unsafe archive path')
                target = destination/member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as source, target.open('wb') as out:
                        shutil.copyfileobj(source, out)
                    target.chmod(member.mode & 0o777)
                    names.append(member.name)
                elif member.issym():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to(member.linkname)
                    names.append(member.name)
                else:
                    raise ValueError('unsupported archive member type')
    return resolved, names


def validate_tree(tree, basetemp, logs):
    env = dict(os.environ, PYTHONPATH=str(tree), PYTHONDONTWRITEBYTECODE='1',
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', GIT_OPTIONAL_LOCKS='0',
               PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
    # These run from the exported tree, without pytest's conftest for the import check.
    code = ('import pathlib, greekocr, greekocr.train, greekocr.deploy.docling_plugin; '
            'root=pathlib.Path.cwd().resolve(); '
            'assert all(pathlib.Path(m.__file__).resolve().is_relative_to(root) '
            'for m in (greekocr, greekocr.train, greekocr.deploy.docling_plugin))')
    commands = [[sys.executable, '-B', '-c', code],
                [sys.executable, '-B', '-m', 'pytest', *TESTS, '-q', '-p', 'no:cacheprovider',
                 '--basetemp='+str(basetemp), '--junitxml='+str(logs/'PUBLIC_TREE_TESTS.xml')]]
    results = []
    for label, command in zip(('imports', 'pytest'), commands):
        with (logs/(label+'.log')).open('w') as log:
            result = subprocess.run(command, cwd=tree, env=env, stdout=log, stderr=subprocess.STDOUT)
        results.append(dict(check=label, command=command, exit_code=result.returncode,
                            log=label+'.log'))
    return results


def write_manifest(tree, rows):
    """Payload manifest; large manifests use a TSV index binding <=4 MB parts."""
    fields = ['path', 'bytes', 'sha256']
    manifest = tree/'PUBLIC_TREE_MANIFEST.tsv'
    write_tsv(manifest, rows, fields)
    if manifest.stat().st_size <= MAX_BYTES:
        return dict(layout='flat', path=manifest.name)
    parts = tree/'PUBLIC_TREE_MANIFEST.parts'; parts.mkdir()
    batches = []; batch = []; size = 20
    for row in rows:
        count = len((f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n").encode())
        if batch and size+count > 4_000_000:
            batches.append(batch); batch = []; size = 20
        batch.append(row); size += count
    if batch: batches.append(batch)
    index = []
    for n, batch in enumerate(batches):
        part = parts/f'part-{n:04d}.tsv'; write_tsv(part, batch, fields)
        data = part.read_bytes()
        index.append(dict(path=part.relative_to(tree).as_posix(), bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest()))
    write_tsv(manifest, index, fields)
    return dict(layout='index of complete payload manifest parts', path=manifest.name, parts=index)


def check_evidence(tree):
    problems = []
    for package in PACKAGES:
        payload = tree/package/'PAYLOAD.json'
        if not payload.is_file():
            problems.append(package+'/PAYLOAD.json: absent from commit tree'); continue
        for name, binding in json.loads(payload.read_text())['files'].items():
            if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
                problems.append(package+': unsafe sealed member path'); continue
            member = tree/package/name
            if not member.is_file():
                problems.append(package+'/'+name+': missing sealed member')
            elif member.stat().st_size != binding['bytes'] or hashlib.sha256(member.read_bytes()).hexdigest() != binding['sha256']:
                problems.append(package+'/'+name+': sealed bytes mismatch')
    models = tree/'MODELS.json'
    if models.is_file():
        def bindings(value):
            if isinstance(value, dict):
                path = value.get('path')
                if isinstance(path, str) and not path.startswith('/'):
                    relative = PurePosixPath(path)
                    if '..' in relative.parts:
                        problems.append('unsafe evidence path'); return
                    member = tree/path
                    if not member.is_file(): problems.append(path+': cited evidence absent')
                    elif 'sha256' in value and hashlib.sha256(member.read_bytes()).hexdigest() != value['sha256']:
                        problems.append(path+': cited evidence SHA mismatch')
                    elif 'bytes' in value and member.stat().st_size != value['bytes']:
                        problems.append(path+': cited evidence size mismatch')
                for item in value.values(): bindings(item)
            elif isinstance(value, list):
                for item in value: bindings(item)
        bindings(json.loads(models.read_text()))
    return problems


def build(repo, commit, out):
    out = Path(out).resolve()
    if out.exists():
        raise ValueError('out_dir must not exist (no existing tree is overwritten)')
    if out == repo or repo.is_relative_to(out):
        raise ValueError('unsafe materialisation root')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir()
    receipt = dict(schema='greekocr-public-tree-v1', requested_commit=commit,
                   root=str(out), source='git archive of resolved commit; no working-tree overlay',
                   tooling_sha256={name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                   for name in ('build_public_tree.py', 'inventory.py')})
    try:
        with tempfile.TemporaryDirectory(prefix='rel0-public-source-') as temp:
            snapshot = Path(temp)/'source'; snapshot.mkdir()
            print('exporting commit snapshot', file=sys.stderr, flush=True)
            resolved, names = archive_commit(repo, commit, snapshot)
            print(f'filtering {len(names)} commit files', file=sys.stderr, flush=True)
            receipt['commit'] = resolved
            # The policy is current tooling; evidence exceptions come only from this commit.
            rows, locations = inventory(snapshot, paths=names, progress=lambda n: print(f'filtered={n}', file=sys.stderr, flush=True))
            kept = [r for r in rows if r['decision'] == 'include']
            for row in kept:
                target = out/row['path']; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(snapshot/row['path'], target)
            # Exclusion and path-name review queues describe the commit, not a local scan.
            logs = out/'PUBLIC_TREE_VALIDATION'; logs.mkdir()
            write_review_outputs(logs, rows)
            write_tsv(logs/'CREDENTIAL_LOCATIONS.tsv',
                      [dict(path=p, line=n) for p, n in locations], ['path', 'line'])
            write_sharded_tsv(logs/'EXCLUDED.tsv', [r for r in rows if r['decision'] == 'exclude'],
                      ['path', 'bytes', 'sha256', 'reason'])
            receipt.update(archived_files=len(rows), included=len(kept), excluded=len(rows)-len(kept),
                           manifest=write_manifest(out, kept))
            receipt['evidence_problems'] = check_evidence(out)
            print('validating assembled tree', file=sys.stderr, flush=True)
            # Always run the specified checks, even when missing dependencies are found.
            with tempfile.TemporaryDirectory(prefix='rel0-public-pytest-') as scratch:
                receipt['validation'] = validate_tree(out, Path(scratch)/'basetemp', logs)
            changed = []
            for row in kept:
                target = out/row['path']
                if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
                    changed.append(row['path'])
                    # Older commits' wheel test rewrites historical evidence; preserve exported bytes.
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(snapshot/row['path'], target)
            receipt['validation_modified_payload_paths'] = changed
            # Recheck filters and exact bytes on the actual assembled payload.
            checked, _ = inventory(out, paths=[r['path'] for r in kept])
            receipt['assembled_payload_verified'] = len(kept) == len(checked) and all(
                (a['path'], a['bytes'], a['sha256'], a['decision']) ==
                (b['path'], b['bytes'], b['sha256'], b['decision']) for a, b in zip(kept, checked))
            receipt['passed'] = (receipt['assembled_payload_verified'] and not changed and not receipt['evidence_problems'] and
                                 all(x['exit_code'] == 0 for x in receipt['validation']))
    except BaseException as exc:
        receipt.update(passed=False, error=str(exc))
        raise
    finally:
        receipt['metadata'] = [dict(path=p.relative_to(out).as_posix(), bytes=p.stat().st_size,
                                    sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                               for p in sorted(out.glob('PUBLIC_TREE*')) if p.is_file() and p.name != 'PUBLIC_TREE_RECEIPT.json']
        (out/'PUBLIC_TREE_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('commit'); parser.add_argument('out_dir', type=Path)
    args = parser.parse_args(argv)
    receipt = build(ROOT, args.commit, args.out_dir)
    print(json.dumps({k: receipt[k] for k in ('commit', 'included', 'excluded', 'passed')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
