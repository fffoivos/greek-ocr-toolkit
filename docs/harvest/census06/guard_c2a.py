"""Read-only C2a handoff checks; never stage, deploy or submit."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
PREFIX = 'docs/harvest/census06/'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

paths = (D/'C2A_COMMIT_PATHS.txt').read_text().splitlines()
assert paths == sorted(set(paths))
assert all(p.startswith(PREFIX) and '..' not in Path(p).parts for p in paths)
assert all((ROOT/p).is_file() and not (ROOT/p).is_symlink() for p in paths)
seal_path = PREFIX+'C2A_COMMIT_SHA256SUMS'
sealed = {}
for line in (ROOT/seal_path).read_text().splitlines():
    digest, path = line.split('  ', 1)
    assert path not in sealed
    sealed[path] = digest
assert set(sealed) == set(paths)-{seal_path}
for path, digest in sealed.items():
    assert sha(ROOT/path) == digest, path
changed = subprocess.check_output(['git','diff','--name-only','--',PREFIX], cwd=ROOT, text=True).splitlines()
assert set(changed) <= set(paths), 'unlisted tracked bundle changes'
assert not (D/'c2a-test-tmp').exists()
tests = list(ET.parse(D/'tests.xml').iter('testcase'))
assert not any(t.find('failure') is not None or t.find('error') is not None for t in tests)
passed = sum(t.find('skipped') is None for t in tests)
assert (passed,len(tests)-passed) == (461,19)
manifest = (D/'DEPLOY_SHA256SUMS').read_bytes()
ident = hashlib.sha256(manifest).hexdigest()
package = json.loads((D/'package_id.json').read_text())
assert package['package_id'] == ident[:16] == 'fb0194d597f20655'
assert package['manifest_sha256'] == ident and package['sf7_binding'] == 'PENDING'
lines = manifest.decode().splitlines()
assert package['files'] == len(lines) == 182
payload_paths = []
for line in lines:
    digest,path = line.split('  ',1)
    assert sha(ROOT/path) == digest, path
    payload_paths.append(path)
assert payload_paths == (D/'DEPLOY_PATHS.txt').read_text().splitlines()
assert payload_paths == [PREFIX+p for p in (D/'PAYLOAD_PATHS.txt').read_text().splitlines()]
# Protect C1 behavior, pending guards, pipeline and tool digests byte-for-byte.
for rel in ('submit_chain.sh','jobs/census.sbatch','jobs/common.sh','jobs/readout.sbatch',
            'timing_c1.py','test_timing_c1.py','prepare_config.py','binding_state.py','bind_sf7.sbatch',
            'package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py',
            'package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census04.py',
            'package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py',
            'package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json'):
    assert (D/rel).read_bytes() == subprocess.check_output(['git','show','672e981f2:'+PREFIX+rel],cwd=ROOT),rel
baseline = subprocess.check_output(['git','show','57ba1416b:'+PREFIX+'DEPLOY_SHA256SUMS'],cwd=ROOT)
assert hashlib.sha256(baseline).hexdigest()[:16] == 'de597753a70a5d6d'
def parse(raw):
    return {p.removeprefix(PREFIX):h for h,p in (s.split('  ',1) for s in raw.decode().splitlines())}
old,new = parse(baseline),parse(manifest)
diff = json.loads((D/'payload_diff.json').read_text())
assert diff['baseline_package_id'] == 'de597753a70a5d6d' and diff['package_id'] == ident[:16]
assert diff['changed'] == [dict(path=p,before_sha256=old[p],after_sha256=new[p]) for p in sorted(old.keys()&new.keys()) if old[p]!=new[p]]
assert diff['inherited_files'] == len(old) == 180
assert diff['unchanged'] == sum(old[p]==new[p] for p in old.keys()&new.keys()) == 172
assert diff['additive_paths'] == sorted(new.keys()-old.keys())
assert diff['dropped_paths'] == sorted(old.keys()-new.keys()) == []
# The copied coordinator procedure differs only in its initial code directory.
doc = (D/'CENSUS06.md').read_text()
section = doc.split('## CENSUS06-C2a —',1)[1]
original = doc[doc.index('```bash\n#!/usr/bin/env bash\n# REVIEW ONLY. NOT EXECUTED IN B.'):]
original = original.split('\n```',1)[0]
latest = section[section.index('```bash\n#!/usr/bin/env bash\n# REVIEW ONLY. NOT EXECUTED IN B.'):].split('\n```',1)[0]
assert latest == original.replace('export PRE_ID=de597753a70a5d6d','export PRE_ID='+ident[:16])
print(f'C2a GUARD OK: {len(paths)} files; {passed} passed/19 skipped; basetemp deleted; package {ident[:16]} PENDING (not deployed); no jobs submitted')
