"""Validate exact CP3 review scope and bytes; never stage/commit/publish."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
SEG='docs/harvest/collect_v3_admission/seg/'
FILES={'greekocr/harvest/geometry_observations.py','greekocr/harvest/row_inclusion.py',
       'tests/test_seg_cp3.py',*[SEG+n for n in ('guard_cp3_commit.py','verify_cp3.py',
       'prepare_cp3_geometry.py','CP3_RECEIPT.md','CP3_pytest.log','CP3_verification.json',
       'CP3_preparation.jsonl','audit_cp3b_geometry.py','CP3b_geometry_audit.json',
       'CP3b_collector_window.json')]}
DEPENDENCIES={
    'docs/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md',
    'docs/reviews/SEG_CP3_review.md','docs/briefs/SEG_CP3_build.md',
    'docs/briefs/SEG_CP3b_fix.md',
    SEG+'calibration_ledger.json',SEG+'protected_before.json',
    'greekocr/glyphs/foreign_ink.py','greekocr/pages/boundaries.py','greekocr/pages/structure.py',
    'greekocr/harvest/admission.py','greekocr/harvest/neighbour_words.py',
    *[str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/collect_v3/vendor/geometry'/n)
      for n in ('io.py','ownership.py','magnitude.py')],
}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(manifest):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head!=manifest['base_HEAD']:raise ValueError('STOP: base HEAD moved')
    for key,scope in [('files',FILES),('read_only_dependencies',DEPENDENCIES)]:
        entries=manifest[key]
        if len(entries)!=len(scope) or {r['path'] for r in entries}!=scope:
            raise ValueError('STOP: exact review scope changed: '+key)
        for r in entries:
            p=Path(r['path'])
            if not p.is_absolute():p=ROOT/p
            if sha(p)!=r['sha256']:raise ValueError('STOP: bytes changed: '+r['path'])
    ledger=json.loads((ROOT/SEG/'calibration_ledger.json').read_text())
    pages={r['row_id'].rsplit('-l',1)[0] for r in ledger['cases']}
    expected_cache={SEG+'CP3_geometry/'+pid+'.attempt.json' for pid in pages}
    expected_cache.update(SEG+'CP3_geometry/'+pid+'/'+name for pid in pages
                          for name in ('detector.json.gz','ink.png','labels.npz','receipt.json'))
    entries=manifest['prepared_cache_files']
    if len(entries)!=len(expected_cache) or {r['path'] for r in entries}!=expected_cache:
        raise ValueError('STOP: prepared evidence scope changed')
    for row in entries:
        p=ROOT/row['path']
        if not p.resolve().is_relative_to((ROOT/SEG/'CP3_geometry').resolve()):
            raise ValueError('STOP: unexpected prepared cache path')
        if sha(p)!=row['sha256']:raise ValueError('STOP: prepared evidence changed: '+row['path'])
    print(f"SEG-CP3 guard: PASS; {len(FILES)} exact files; HEAD {head}; no staging/commit/publication")


if __name__=='__main__':
    verify(json.loads((ROOT/SEG/'CP3_COMMIT_LIST.json').read_text()))
