"""Exact CP4 scope/byte guard. Read-only: never stage, commit or publish."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
SEG='docs/harvest/collect_v3_admission/seg/'
FILES={'greekocr/harvest/geometry_observations.py','greekocr/harvest/neighbour_words.py',
       'greekocr/harvest/row_inclusion.py',
       'greekocr/harvest/admission.py', 'tests/test_seg_cp4c.py',
       'tests/test_seg_cp1.py','tests/test_seg_cp2.py','tests/test_seg_cp3.py',
       'tests/test_harvest_admission.py','tests/test_adm5b_schema.py',
       'tests/test_adm5c_variants.py','tests/test_neighbour_words.py',
       'tests/test_seg_cp4.py',*[SEG+n for n in ('guard_cp4_commit.py','verify_cp4.py',
       'CP4_RECEIPT.md','CP4_pytest.log','CP4_verification.json','CP4_one_letter_words.json',
       'audit_cp4_cache.py','CP4_cache_audit.json','prepare_cp4_geometry.py','CP4_preparation.jsonl',
       'verify_cp4_controls.py','CP4_controls.json','CP4_CP3_verification.json','CP4_C1_conflict.json','freeze_truth.py',
       'calibration_ledger.json','CP4c_KNOWN_ISSUES.md')]}
DEPENDENCIES={SEG+n for n in ('protected_before.json','CP3_COMMIT_LIST.json',
                              'CP3_M1_lead_process_evidence.md')}
DEPENDENCIES.update({'docs/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md',
    'docs/briefs/SEG_CP4b_fix.md','docs/reviews/SEG_CP4_review.md','docs/briefs/SEG_CP4_build.md','docs/harvest/collect_v3_admission/nw1b/GATE_FAIL.md','docs/briefs/SEG_CP4c_rulings.md','docs/reviews/SEG_CP4_review_2.md',
    SEG+'CP3b_geometry_audit.json',SEG+'CP3_RECEIPT.md',
    'greekocr/glyphs/foreign_ink.py','greekocr/glyphs/letters.py','greekocr/glyphs/lines_api.py',
    'greekocr/glyphs/components.py','greekocr/glyphs/oriented_page.py','greekocr/pages/boundaries.py',
    *[str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/collect_v3/vendor/geometry'/n)
      for n in ('io.py','ownership.py','magnitude.py')]})


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(manifest):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head!=manifest['base_HEAD']:raise ValueError('STOP: base HEAD moved')
    for key,scope in [('files',FILES),('read_only_dependencies',DEPENDENCIES)]:
        entries=manifest[key]
        if len(entries)!=len(scope) or {r['path'] for r in entries}!=scope:
            raise ValueError('STOP: exact review scope changed: '+key)
        for row in entries:
            p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
            if sha(p)!=row['sha256']:raise ValueError('STOP: bytes changed: '+row['path'])
    previous=json.loads((ROOT/SEG/'CP3_COMMIT_LIST.json').read_text())['prepared_cache_files']
    if manifest['prepared_cache_files']!=previous:raise ValueError('STOP: inherited geometry scope changed')
    for row in previous:
        p=ROOT/row['path']
        if not p.resolve().is_relative_to((ROOT/SEG/'CP3_geometry').resolve()):
            raise ValueError('STOP: unsafe geometry path')
        if sha(p)!=row['sha256']:raise ValueError('STOP: inherited geometry changed')
    # The one authorized CP4 fallback is isolated and remains unavailable.
    fallback_root=ROOT/SEG/'CP4_geometry'
    expected={str(p.relative_to(ROOT)) for p in fallback_root.rglob('*') if p.is_file()}
    entries=manifest['fallback_cache_files']
    if len(entries)!=len(expected) or {r['path'] for r in entries}!=expected:
        raise ValueError('STOP: fallback cache scope changed')
    if len(list(fallback_root.glob('*.attempt.json')))!=1 or len(expected)!=5:
        raise ValueError('STOP: fallback preparation count changed')
    for row in entries:
        if sha(ROOT/row['path'])!=row['sha256']:
            raise ValueError('STOP: fallback bytes changed')
    attempt=json.loads(next(fallback_root.glob('*.attempt.json')).read_text())
    receipt=json.loads((fallback_root/attempt['page_id']/'receipt.json').read_text())
    for key in ('source','source_sha256','detector_sha256'):
        if attempt[key]!=receipt[key]: raise ValueError('STOP: fallback source binding changed')
    if sha(Path(receipt['source']))!=receipt['source_sha256']:
        raise ValueError('STOP: fallback source changed')
    protected=json.loads((ROOT/SEG/'protected_before.json').read_text())
    for path,before in protected.items():
        if sha(ROOT/path)!=before['sha256']:raise ValueError('STOP: protected artifact changed')
    changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
    if any(p.endswith('.png') or p.endswith('crops_manifest.jsonl') or
           p in protected for p in changed):raise ValueError('STOP: protected tracked diff')
    # A separate docs-only group belongs to sol-collect; a prepared local copy
    # is reviewable but is never reported as installed in the other checkout.
    groups = manifest['commit_groups']
    if {r['path'] for r in groups[0]['files']} != FILES:
        raise ValueError('STOP: recut commit group changed')
    if groups[0]['files'] != manifest['files']:
        raise ValueError('STOP: recut group hashes changed')
    collect = Path.home()/'Projects/greek-ocr-toolkit-sol-collect'
    group = groups[1]
    target = 'docs/harvest/collect_v3/KNOWN_ISSUES.md'
    if (group['checkout'] != str(collect) or len(group['files']) != 1
            or group['files'][0]['path'] != target):
        raise ValueError('STOP: collector docs-only scope changed')
    entry = group['files'][0]
    if entry['prepared_source'] != SEG+'CP4c_KNOWN_ISSUES.md' or sha(ROOT/entry['prepared_source']) != entry['sha256']:
        raise ValueError('STOP: prepared collector documentation changed')
    if group['status'] == 'written':
        if sha(collect/target) != entry['sha256']:
            raise ValueError('STOP: collector documentation differs')
    elif group['status'] != 'blocked_outside_writable_roots':
        raise ValueError('STOP: unknown collector documentation status')
    print('Collector docs group: '+group['status'])
    print(f'SEG-CP4 guard: PASS; {len(FILES)} exact files; HEAD {head}; no staging/commit/publication')


if __name__=='__main__':
    verify(json.loads((ROOT/SEG/'CP4_COMMIT_LIST.json').read_text()))
