"""Verify part-3 writes against the captured starting file hashes and git status."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ALLOWED = {
    'greekocr/harvest/line_pipeline.py',
    'scripts/harvest/build_filter_versions.py',
    'tests/test_content_gate.py',
    'tests/test_line_pipeline.py',
    'docs/harvest/line_pipeline/README.md',
    'docs/harvest/line_pipeline/tool_versions.json',
}


def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', *args], cwd=ROOT).decode()


def verify():
    initial = json.loads((HERE / 'part3-initial-hashes.json').read_text())
    changed = {name for name, sha in initial.items()
               if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha}
    assert changed == ALLOWED, sorted(changed ^ ALLOWED)
    assert set(git('diff', '--name-only').splitlines()) == ALLOWED
    assert not git('diff', '--cached', '--name-only').strip()
    subprocess.run(['git', '--no-optional-locks', 'diff', '--check'], cwd=ROOT, check=True)
    before_untracked = [line[3:].rstrip('/') for line in (HERE / 'part3-status-before.txt').read_text().splitlines() if line.startswith('?? ')]
    unexpected = []
    for name in git('ls-files', '--others', '--exclude-standard').splitlines():
        if name.startswith('docs/harvest/line_pipeline/gate03/part3-') or name.startswith('docs/harvest/line_pipeline/gate03/part3_') or name == 'docs/harvest/line_pipeline/gate03/REPORT_part3.md':
            continue
        if not any(name == old or name.startswith(old + '/') for old in before_untracked):
            unexpected.append(name)
    assert not unexpected, unexpected
    for item in json.loads((HERE / 'part3-clariden-shas.json').read_text()):
        assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == item['sha256'] for path in item['paths'])
    assert (HERE / 'version-build-fallbacks.json').read_bytes() == (HERE / 'part3-version-build-fallbacks-before.json').read_bytes()
    assert (HERE / 'version-build-fallbacks.json').read_bytes() == (HERE / 'part3-version-build-fallbacks-after.json').read_bytes()
    for name in ALLOWED:
        assert (HERE / 'part3-baseline' / name).is_file()
    result = dict(status='PASS',initial_files_checked=len(initial),changed_files=sorted(changed),
        all_other_initial_hashes_unchanged=True,unexpected_additions=unexpected,clariden_matches='5/5',
        staged_changes=[],diff_check='PASS',historical_fallback_manifest_unchanged=True)
    (HERE / 'part3-scope-guard.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE / 'part3-scope.patch').write_text(git('diff', '--', *sorted(ALLOWED)))
    (HERE / 'part3-scope-stat.txt').write_text(git('diff', '--stat', '--', *sorted(ALLOWED)))
    (HERE / 'part3-existing-tests.patch').write_text(git('diff', '--', 'tests/test_line_pipeline.py'))
    print(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    verify()
