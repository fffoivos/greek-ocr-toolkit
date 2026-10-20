"""Validate CP2's exact review list; never stage, commit, or publish anything."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
SEG='docs/harvest/collect_v3_admission/seg/'
FILES={
    'greekocr/harvest/geometry_observations.py',
    'greekocr/harvest/neighbour_words.py',
    'greekocr/harvest/admission.py',
    'tests/test_seg_cp2.py','tests/test_neighbour_words.py',
    'tests/test_harvest_admission.py','tests/test_adm5b_schema.py',
    'tests/test_adm5c_variants.py','tests/test_seg_cp1.py',
    *[SEG+n for n in ('verify_cp2.py','guard_cp2_commit.py','CP2_RECEIPT.md',
                     'CP2_verification.json','CP2_pytest.log')],
}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    manifest=json.loads((ROOT/SEG/'CP2_COMMIT_LIST.json').read_text())
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if actual!=manifest['base_HEAD']:raise SystemExit('STOP: base HEAD moved')
    files=manifest['files']
    if len(files)!=len(FILES) or {r['path'] for r in files}!=FILES:
        raise SystemExit('STOP: review scope changed')
    for r in [*files,*manifest['read_only_dependencies']]:
        p=Path(r['path'])
        if not p.is_absolute():p=ROOT/p
        if sha(p)!=r['sha256']:raise SystemExit('STOP: bytes changed: '+r['path'])
    print(f'SEG-CP2 guard: PASS; {len(files)} exact files; HEAD {actual}; no staging/commit/publication')


if __name__=='__main__':main()
