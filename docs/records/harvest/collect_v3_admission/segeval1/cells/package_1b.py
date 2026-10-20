"""Extend imported sol/seg-cells in an isolated Git directory; never push."""
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


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def unchanged(initial):
    for name, expected in initial['protected'].items():
        assert sha(ROOT / name) == expected, name
    assert run(['git', 'rev-parse', 'HEAD']) == initial['head']
    assert subprocess.check_output(['git', 'for-each-ref', '--format=%(refname) %(objectname)'], cwd=ROOT, text=True) == initial['refs']
    index = Path(run(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'index']))
    assert sha(index) == initial['index_sha256']
    assert hashlib.sha256(subprocess.check_output(['git', 'diff', '--binary'], cwd=ROOT)).hexdigest() == initial['diff_sha256']
    assert sha(ROOT / 'greekocr/harvest/line_pipeline_native.py') == initial['native_sha256']


def main():
    initial = json.loads((D / 'initial_state_1b.json').read_text())
    assert not initial['shared_git_writable'], 'This package is the authorised fallback for read-only shared Git.'
    validation = json.loads((D / 'validation_1b.json').read_text())
    assert validation['status'] == 'PASS' and validation['samples_byte_exact_to_census'] == 250
    receipt = json.loads((D / 'sample_receipt.json').read_text())
    assert sha(D / 'samples.jsonl') == receipt['samples_sha256']
    unchanged(initial)
    parent = initial['seg_cells_head']
    assert parent == run(['git', 'rev-parse', 'sol/seg-cells'])
    subprocess.run(['git', 'merge-base', '--is-ancestor', '7350e39c0461bc89cce812186b2e3cdafe46bb2a', parent], cwd=ROOT, check=True)
    common = Path(run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir']))
    gitdir = Path(tempfile.mkdtemp(prefix='segcells1b-', dir='/private/tmp')) / 'repo.git'
    subprocess.run(['git', 'init', '--bare', '--quiet', str(gitdir)], check=True)
    (gitdir / 'objects/info/alternates').write_text(str(common / 'objects') + '\n')
    ident = run(['git', 'var', 'GIT_AUTHOR_IDENT'])
    match = re.fullmatch(r'(.*) <([^>]+)> (\d+) ([+-]\d+)', ident)
    assert match
    g = ['git', '--git-dir=' + str(gitdir), '--work-tree=' + str(ROOT)]
    for key, value in (('user.name', match[1]), ('user.email', match[2])):
        run(g + ['config', key, value])
    run(g + ['read-tree', parent])
    names = ['initial_state_1b.json', 'materialise_1b.py', 'package_1b.py',
             'samples.jsonl', 'sample_receipt.json', 'selected_metadata_1b.json',
             'sample_observations.md', 'visual_review_1b.json', 'visual_zoom_1b.png',
             'validate_1b.py', 'validation_1b.json']
    owned = [str((D / name).relative_to(ROOT)) for name in names]
    owned += [str(p.relative_to(ROOT)) for p in sorted((D / 'samples').glob('*.png'))]
    run(g + ['add', '-f', '--', *owned])
    changes = run(g + ['diff', '--cached', '--name-only', parent]).splitlines()
    png_changes = [p for p in changes if p.endswith('.png') and '/samples/' in p]
    assert len(png_changes) == 200
    assert set(changes) <= set(owned)
    assert all(p.startswith(str(D.relative_to(ROOT)) + '/') for p in changes)
    implementation = run(g + ['commit-tree', run(g + ['write-tree']), '-p', parent], input=(
        'Materialise all 250 SEG-CELLS samples with byte-exact local reconstruction\n\n'
        'SEG-CELLS-1b: use unchanged native reconstructed_crop for 200 missing PNGs '
        'from 156 hash-verified cached pages; retain original 50 control PNGs. '
        'Preserve seeded prefixes, verify all census hashes and dimensions, '
        'record per-sample provenance and 40 native-image observations. '
        'No Clariden command, page fetch, replacement, production code change or push.\n'))

    handoff = D / 'HANDOFF.md'
    original_handoff = subprocess.check_output(['git', 'show', parent + ':' + str(handoff.relative_to(ROOT))], cwd=ROOT)
    # Append once to the imported hand-off; the old blocked section remains historical.
    assert handoff.read_bytes() == original_handoff
    section = f'''

## 1b

**Complete: 250/250 samples are present and byte-exact to the frozen census.**
This section supersedes the historical sample-availability blocker above.
The saved seeded orders and descriptive classifier are unchanged: the first
150 cells and first 50 numeric-not-small rows were reconstructed, and the
original 50 small-non-numeric PNGs were retained byte-for-byte. No replacement
was needed.

### Local reconstruction and provenance

The 200 new crops use **156 unique cached pages**, all verified against their
recorded source SHA256. Both frozen W1/W2 feature snapshots were already local;
their full hashes and row counts were rechecked against `export_receipt.json`.
The W2 page JSON and resolved manifest were inspected first; the feature
snapshot supplies the per-row boxes. Every selected metadata crop hash, page
hash, bbox and colour mode was rebound to the prepared/census records.

The script imports `greekocr.harvest.line_pipeline_native.reconstructed_crop`
and `digest_bytes` directly. That production file is unchanged. It makes the
same page conversion, bbox crop and PNG encoding as the pipeline, and checks
`digest_bytes(encoded) == crop_sha256` before writing each PNG. **200 local
line crops** were made, within the authorised limit. No cache file was written.
There were **zero page fetches, zero SCP page reads, zero replacements and zero
Clariden commands** in 1b. The original 50 controls remain labelled as existing
SEG-CELLS-1 SCP crop reads; they are not counted as page-cache reconstructions.
The old pending receipt and crop-file failure log describe SEG-CELLS-1 history.

[samples.jsonl](samples.jsonl) now contains absolute local crop paths, crop
SHA256, width/height, character count, literal OCR text, source/classes, literal
0.5 verdict/reason and group for every sample. [sample_receipt.json](sample_receipt.json)
contains all 250 per-sample acquisition records, original seeded ranks,
page hashes/paths, zero fetch/replacement logs, and metadata verification.
[selected_metadata_1b.json](selected_metadata_1b.json) keeps the 200 compact
source/bbox bindings. Page counts in the final line mean **unique source-page
hashes**, not sample counts (200 samples use 156 pages).

### Visual review and validation

**40 of the 150 native cell PNGs were opened individually with the image tool**;
ten difficult cases were additionally viewed at 6× display scale. See
[sample_observations.md](sample_observations.md),
[visual_review_1b.json](visual_review_1b.json) and
[visual_zoom_1b.png](visual_zoom_1b.png). They show page-number-like crops,
amounts, a date, parenthesized markers of unresolved role, faint/broken or
heavy ink, sideways strips and clipped extra strokes. These are visual
observations, not new rules, corrected OCR, owner labels or independent gold.

[validation_1b.json](validation_1b.json) records **PASS**: all 250 physical PNG
hashes/dimensions and required fields match the census; both numeric seeded
prefixes and all original controls are preserved; 156 page hashes match;
the native function and all five pre-existing edited files are unchanged.
The shared HEAD, refs, index and existing diff are also unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B docs/harvest/collect_v3_admission/segeval1/cells/validate_1b.py
```

### Commit delivery

The shared Git write probe returned `Operation not permitted`. The authorised
[SEGCELLS1B.bundle](SEGCELLS1B.bundle) therefore extends imported branch
`sol/seg-cells` at `{parent}` in an isolated writable Git directory.
Materialisation/observations/validation commit: **`{implementation}`**.
A following hand-off-only commit contains this section; its hash is recorded
in [bundle_receipt_1b.json](bundle_receipt_1b.json). The final line names the
materialisation commit to avoid a self-referential commit hash.
Independent bundle import verifies the branch tip, ancestry and every changed
file's committed bytes. No production path was changed; nothing was pushed.

SEGCELLS1B: done | samples 250/250 byte-exact | pages from cache 156, scp 0, replacements 0 | commit {implementation}
'''
    handoff.write_bytes(original_handoff + section.encode())
    hp = str(handoff.relative_to(ROOT))
    run(g + ['add', '-f', '--', hp])
    head = run(g + ['commit-tree', run(g + ['write-tree']), '-p', implementation],
               input='Append SEG-CELLS-1b completion hand-off and sample receipts\n')
    run(g + ['update-ref', 'refs/heads/sol/seg-cells', head])
    run(g + ['symbolic-ref', 'HEAD', 'refs/heads/sol/seg-cells'])
    bundle = D / 'SEGCELLS1B.bundle'
    run(g + ['bundle', 'create', str(bundle), 'sol/seg-cells', '^' + parent])
    verification = subprocess.run(g + ['bundle', 'verify', str(bundle)], cwd=ROOT,
                                  text=True, capture_output=True, check=True)
    verifydir = Path(tempfile.mkdtemp(prefix='segcells1b-verify-', dir='/private/tmp')) / 'repo.git'
    subprocess.run(['git', 'init', '--bare', '--quiet', str(verifydir)], check=True)
    (verifydir / 'objects/info/alternates').write_text(str(common / 'objects') + '\n')
    vg = ['git', '--git-dir=' + str(verifydir)]
    run(vg + ['fetch', '--quiet', str(bundle), 'refs/heads/sol/seg-cells:refs/heads/sol/seg-cells'])
    assert run(vg + ['rev-parse', 'sol/seg-cells']) == head
    assert run(vg + ['rev-parse', implementation + '^']) == parent
    assert run(vg + ['rev-list', '--count', parent + '..' + head]) == '2'
    paths = run(vg + ['diff-tree', '--no-commit-id', '--name-only', '-r', parent, head]).splitlines()
    assert set(paths) == set(changes) | {hp}
    for name in paths:
        committed = subprocess.check_output(vg + ['show', head + ':' + name], cwd=ROOT)
        assert hashlib.sha256(committed).hexdigest() == sha(ROOT / name), name
    for name in initial['protected']:
        assert run(vg + ['rev-parse', head + ':' + name]) == run(['git', 'rev-parse', parent + ':' + name])
    assert run(vg + ['diff-tree', '--no-commit-id', '--name-only', '-r', implementation, head]) == hp
    unchanged(initial)
    result = dict(branch_in_bundle='sol/seg-cells', parent=parent,
                  implementation_commit=implementation, handoff_commit=head,
                  bundle_sha256=sha(bundle), bundle_bytes=bundle.stat().st_size,
                  bundle_verify_stdout=verification.stdout, bundle_verify_stderr=verification.stderr,
                  isolated_git_dir=str(gitdir), independent_import_git_dir=str(verifydir),
                  changed_paths=paths, changed_file_bytes_verified=len(paths),
                  newly_committed_sample_pngs=len(png_changes), sample_delivery_status='250/250 byte-exact',
                  production_paths_changed=[], shared_head_refs_index_and_existing_diff_unchanged=True,
                  protected_five_files_unchanged=True, never_pushed=True)
    (D / 'bundle_receipt_1b.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('changed_paths', 'bundle_verify_stdout', 'bundle_verify_stderr')}, indent=2))


if __name__ == '__main__':
    main()
