"""Package sol/seg-cells without writing shared Git refs, index or objects."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

D = Path(__file__).resolve().parent
ROOT = D.parents[4]


def run(args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, text=True, **kwargs).strip()


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    initial = json.loads((D / 'initial_state.json').read_text())
    validation = json.loads((D / 'validation.json').read_text())
    assert validation['rows_verified'] == 592466
    parent = initial['base']
    assert parent == '410f4566db26a9acefb541a5af12312c661fb918'
    for name, expected in initial['protected'].items():
        assert sha(ROOT / name) == expected
    common = Path(run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir']))
    gitdir = Path(tempfile.mkdtemp(prefix='segcells1-', dir='/private/tmp')) / 'repo.git'
    subprocess.run(['git', 'init', '--bare', '--quiet', str(gitdir)], check=True)
    (gitdir / 'objects/info/alternates').write_text(str(common / 'objects') + '\n')
    ident = run(['git', 'var', 'GIT_AUTHOR_IDENT'])
    match = re.fullmatch(r'(.*) <([^>]+)> (\d+) ([+-]\d+)', ident)
    assert match
    for key, value in (('user.name', match[1]), ('user.email', match[2])):
        run(['git', '--git-dir=' + str(gitdir), 'config', key, value])
    g = ['git', '--git-dir=' + str(gitdir), '--work-tree=' + str(ROOT)]
    run(g + ['read-tree', parent])
    excluded = {'HANDOFF.md', 'SEGCELLS1.bundle', 'bundle_receipt.json', 'package.log'}
    artifacts = [str(p.relative_to(ROOT)) for p in sorted(D.rglob('*'))
                 if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]
    owned = ['greekocr/harvest/numeric_cells.py', 'tests/test_numeric_cells.py', *artifacts]
    assert not set(owned) & set(initial['protected'])
    run(g + ['add', '-f', '--', *owned])
    assert set(run(g + ['diff', '--cached', '--name-only', parent]).splitlines()) == set(owned)
    tree = run(g + ['write-tree'])
    samples = json.loads((D / 'sample_receipt.json').read_text())
    implementation = run(g + ['commit-tree', tree, '-p', parent], input=(
        'Classify numeric cells and census the frozen 592466-row export\n\n'
        'SEG-CELLS-1: pure descriptive classifier (200x40 px, <=10 visible characters), '
        'verified read-only export reduction, complete distribution/census tables, '
        'unchanged historical verdict readback and 121 tests. '
        f'Samples {samples["fetched"]}/250; numeric crop directories absent; '
        'prepare but do not execute hash-bound reconstruction fallback. No policy integration.\n'))
    subprocess.run([str(ROOT / '.venv/bin/python'), str(D / 'write_handoff.py'), implementation],
                   cwd=ROOT, check=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    handoff = str((D / 'HANDOFF.md').relative_to(ROOT))
    run(g + ['add', '-f', '--', handoff])
    head = run(g + ['commit-tree', run(g + ['write-tree']), '-p', implementation],
               input='Record SEG-CELLS-1 census hand-off and crop availability blocker\n')
    run(g + ['update-ref', 'refs/heads/sol/seg-cells', head])
    run(g + ['symbolic-ref', 'HEAD', 'refs/heads/sol/seg-cells'])
    bundle = D / 'SEGCELLS1.bundle'
    run(g + ['bundle', 'create', str(bundle), 'sol/seg-cells', '^' + parent])
    verification = subprocess.run(g + ['bundle', 'verify', str(bundle)], cwd=ROOT, text=True,
                                  capture_output=True, check=True)
    verifydir = Path(tempfile.mkdtemp(prefix='segcells1-verify-', dir='/private/tmp')) / 'repo.git'
    subprocess.run(['git', 'init', '--bare', '--quiet', str(verifydir)], check=True)
    (verifydir / 'objects/info/alternates').write_text(str(common / 'objects') + '\n')
    vg = ['git', '--git-dir=' + str(verifydir)]
    run(vg + ['fetch', '--quiet', str(bundle), 'refs/heads/sol/seg-cells:refs/heads/sol/seg-cells'])
    assert run(vg + ['rev-parse', 'sol/seg-cells']) == head
    assert run(vg + ['rev-parse', implementation + '^']) == parent
    assert run(vg + ['rev-list', '--count', parent + '..' + head]) == '2'
    paths = run(vg + ['diff-tree', '--no-commit-id', '--name-only', '-r', parent, head]).splitlines()
    assert set(paths) == set(owned) | {handoff}
    for name in paths:
        data = subprocess.check_output(vg + ['show', head + ':' + name], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == sha(ROOT / name), name
    for name, expected in initial['protected'].items():
        assert sha(ROOT / name) == expected
        assert run(vg + ['rev-parse', head + ':' + name]) == run(['git', 'rev-parse', parent + ':' + name])
    index = Path(run(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'index']))
    assert sha(index) == initial['index_sha256']
    assert run(['git', 'rev-parse', 'HEAD']) == initial['head']
    assert run(['git', 'for-each-ref', '--format=%(refname) %(objectname)']) == initial['refs']
    assert hashlib.sha256(subprocess.check_output(['git', 'diff', '--binary'], cwd=ROOT)).hexdigest() == initial['diff_sha256']
    receipt = dict(branch_in_bundle='sol/seg-cells', base=parent,
                   implementation_commit=implementation, handoff_commit=head,
                   bundle_sha256=sha(bundle), bundle_bytes=bundle.stat().st_size,
                   bundle_verify_stdout=verification.stdout, bundle_verify_stderr=verification.stderr,
                   isolated_git_dir=str(gitdir), independent_import_git_dir=str(verifydir),
                   committed_paths=paths, committed_file_bytes_verified=len(paths),
                   shared_branch_unchanged=True, shared_refs_and_index_unchanged=True,
                   protected_five_files_not_staged_and_unchanged=True,
                   production_additions=['greekocr/harvest/numeric_cells.py'],
                   existing_production_paths_changed=[], never_pushed=True,
                   sample_delivery_status=samples.get('status', 'complete'), samples_fetched=samples['fetched'])
    (D / 'bundle_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('committed_paths', 'bundle_verify_stdout', 'bundle_verify_stderr')}, indent=2))


if __name__ == '__main__':
    main()
