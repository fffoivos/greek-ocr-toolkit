"""Read-only C1 commit allowlist/seal check. Never stages, commits or deploys."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
PREFIX = 'docs/harvest/census06/'
paths = (D/'C1_COMMIT_PATHS.txt').read_text().splitlines()
assert paths == sorted(set(paths))
assert all(p.startswith(PREFIX) and '..' not in Path(p).parts for p in paths)
assert all((ROOT/p).is_file() and not (ROOT/p).is_symlink() for p in paths)
seal_path = PREFIX+'C1_COMMIT_SHA256SUMS'
sealed = {}
for line in (ROOT/seal_path).read_text().splitlines():
    sha, path = line.split('  ', 1)
    assert path not in sealed
    sealed[path] = sha
assert set(sealed) == set(paths)-{seal_path}
for path, sha in sealed.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, path
changed = subprocess.check_output(['git', 'diff', '--name-only', '--', PREFIX], cwd=ROOT, text=True).splitlines()
assert set(changed) <= set(paths), 'unlisted tracked bundle changes'
assert not (D/'c1-test-tmp').exists()
tests = list(ET.parse(D/'tests.xml').iter('testcase'))
assert not any(t.find('failure') is not None or t.find('error') is not None for t in tests)
passed = sum(t.find('skipped') is None for t in tests)
skipped = len(tests)-passed
assert passed == 438 and skipped == 19, (passed, skipped)
assert re.search(r'\bMaxTime=12:00:00\b', (D/'partition_normal_c1.txt').read_text())
manifest = (D/'DEPLOY_SHA256SUMS').read_bytes()
ident = hashlib.sha256(manifest).hexdigest()
package = json.loads((D/'package_id.json').read_text())
assert package['package_id'] == ident[:16] and package['manifest_sha256'] == ident
assert package['sf7_binding'] == 'PENDING'
for line in manifest.decode().splitlines():
    sha, path = line.split('  ', 1)
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, path
assert package['files'] == len(manifest.decode().splitlines()) == 182
print(f'C1 GUARD OK: {len(paths)} exact paths; {passed} passed/{skipped} skipped; basetemp deleted; local package {ident[:16]} PENDING (not deployed)')
