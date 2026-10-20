"""Exact CP5 review scope and bytes. Never stages, commits, or publishes."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
SEG='docs/harvest/collect_v3_admission/seg/'
FILES={'greekocr/harvest/orientation_screen.py','tests/test_seg_cp5.py',
    *[SEG+n for n in ('verify_cp5.py','review_cp4c.py','guard_cp5_commit.py',
        'CP5_RECEIPT.md','CP5_pytest.log','CP5_measurement.log','CP5_verification.json',
        'CP5_cp4_verification.json','CP5_cp4c_review.json','prepare_cp5_separators.py',
        'CP5_separator_preparation.jsonl','diagnose_cp5.py','CP5_native_diagnostics.json')],
    'greekocr/harvest/separator_inventory.py'}
FILES.update(str(p.relative_to(ROOT)) for p in (ROOT/SEG/'CP5_separators').rglob('*') if p.is_file())
BASE_DEPENDENCIES={SEG+n for n in ('calibration_ledger.json','freeze_truth.py',
    'protected_before.json','CP4_COMMIT_LIST.json','CP4_controls.json','CP4_one_letter_words.json',
    'verify_cp4.py','prepare_cp4_geometry.py','CP3_M1_lead_process_evidence.md')}
BASE_DEPENDENCIES.update({'docs/briefs/SEG_CP5c_rulings.md','docs/reviews/SEG_CP5_review_2.md','docs/briefs/SEG_CP5_build.md','docs/briefs/SEG_CP5b_fix.md','docs/reviews/SEG_CP5_review.md','docs/briefs/SEG_CP4c_rulings.md',
    'docs/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md',
    'docs/harvest/collect_v3_admission/nw1b/GATE_FAIL.md',
    'tests/fixtures/fonts/GFSDidot-Regular.ttf'})
BASE_DEPENDENCIES.update(str(p.relative_to(ROOT)) for folder in ('greekocr/pages','greekocr/glyphs','greekocr/harvest')
    for p in (ROOT/folder).glob('*.py') if str(p.relative_to(ROOT)) not in FILES)
BASE_DEPENDENCIES.update('tests/'+n+'.py' for n in ('test_seg_cp4c','test_seg_cp4','test_seg_cp3','test_seg_cp2',
    'test_harvest_admission','test_adm5b_schema','test_adm5c_variants','test_neighbour_words','test_seg_cp1'))
BASE_DEPENDENCIES.update(str(p.relative_to(ROOT)) for folder in ('CP3_geometry','CP4_geometry')
    for p in (ROOT/SEG/folder).rglob('*') if p.is_file())


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def external_dependencies():
    result=json.loads((ROOT/SEG/'CP5_verification.json').read_text())
    deps={result['historical_file'],str(Path.home()/'Projects/collect-v3-data/run/W1/features.jsonl'),
          str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python')}
    deps.update(c['source'] for c in result['cases'] if c.get('source'))
    collector=Path.home()/'Projects/greek-ocr-toolkit-sol-collect'
    deps.add(str(collector/'collect_v3/pipeline.py'))
    deps.add(str(collector/'docs/harvest/collect_v3/KNOWN_ISSUES.md'))
    deps.update(str(p) for folder in ('pages','glyphs') for p in (collector/'greekocr'/folder).glob('*.py'))
    deps.update(str(collector/'collect_v3/vendor/geometry'/n) for n in ('io.py','ownership.py','magnitude.py'))
    cp4=json.loads((ROOT/SEG/'CP5_cp4_verification.json').read_text())
    # Bind actual live cache snapshots used; concurrent new pages are outside scope.
    for page in cp4['page_coverage']:
        binding=page.get('binding')
        if binding:
            cache=Path(binding['cache_directory'])
            if not cache.is_relative_to(ROOT):
                deps.update(str(cache/n) for n in ('receipt.json','detector.json.gz','ink.png','labels.npz'))
    return deps


def verify(manifest):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head!=manifest['base_HEAD']:raise ValueError('STOP: base HEAD moved')
    entries=manifest['files']
    if len(entries)!=len(FILES) or {r['path'] for r in entries}!=FILES:
        raise ValueError('STOP: exact review scope changed')
    deps=BASE_DEPENDENCIES|external_dependencies()
    for key,scope in (('files',FILES),('read_only_dependencies',deps)):
        entries=manifest[key]
        if len(entries)!=len(scope) or {r['path'] for r in entries}!=scope:
            raise ValueError('STOP: exact dependency scope changed')
        for row in entries:
            p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
            if sha(p)!=row['sha256']:raise ValueError('STOP: bytes changed: '+row['path'])
    protected=json.loads((ROOT/SEG/'protected_before.json').read_text())
    tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only',head,'--',*protected],
        cwd=ROOT,text=True).splitlines())
    if sorted(set(protected)-tracked)!=manifest['protected_without_HEAD']:
        raise ValueError('STOP: protected HEAD coverage changed')
    for path,entry in protected.items():
        if sha(ROOT/path)!=entry['sha256']:raise ValueError('STOP: protected artifact changed')
        if path in tracked:
            before=subprocess.check_output(['git','show',head+':'+path],cwd=ROOT)
            if hashlib.sha256(before).hexdigest()!=entry['sha256']:
                raise ValueError('STOP: protected artifact differs from HEAD')
    changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
    if any(p.endswith('.png') or p.endswith('crops_manifest.jsonl') or p in protected for p in changed):
        raise ValueError('STOP: protected tracked diff')
    data=json.loads((ROOT/SEG/'CP5_verification.json').read_text())
    if data['verifier_sha256']!=sha(ROOT/SEG/'verify_cp5.py'):
        raise ValueError('STOP: verifier changed')
    if sha(data['historical_file'])!=data['historical_sha256']:
        raise ValueError('STOP: historical IDs changed')
    if sha(Path.home()/'Projects/collect-v3-data/run/W1/features.jsonl')!=data['features_sha256']:
        raise ValueError('STOP: feature source changed')
    sources={}
    for case in data['cases']:
        if case.get('source'):
            if case['source'] in sources and sources[case['source']]!=case['source_sha256']:
                raise ValueError('STOP: inconsistent source identity')
            sources[case['source']]=case['source_sha256']
        binding=case['orientation'].get('binding')
        if binding and binding['adapter_sha256']!=sha(ROOT/'greekocr/harvest/orientation_screen.py'):
            raise ValueError('STOP: orientation adapter changed')
    for path,expected in sources.items():
        if sha(path)!=expected:raise ValueError('STOP: native source changed')
    for raw in (ROOT/'docs/harvest/collect_v3_admission/crops_manifest.jsonl').read_text().splitlines():
        row=json.loads(raw)
        if sha(ROOT/'docs/harvest/collect_v3_admission'/row['path'])!=row['sha256']:
            raise ValueError('STOP: retained crop changed')
    # Inventory receipts and attempt markers must bind the current strict page
    # cache and current adapter; this never prepares missing evidence.
    import sys
    sys.path.insert(0,str(ROOT))
    from greekocr.harvest import geometry_observations as g, separator_inventory as inventory
    claims={}
    for marker in (ROOT/SEG/'CP5_separators').glob('*.attempt.json'):
        claim=json.loads(marker.read_text())
        key=(claim['source'],claim['source_sha256'],claim['frame'])
        if key in claims:raise ValueError('STOP: duplicate source preparation')
        claims[key]=claim
        directory=marker.parent/claim['page_id']
        receipt=json.loads((directory/'receipt.json').read_text())
        if receipt['preparation_calls']!=1 or receipt['row_detector_calls']!=0:
            raise ValueError('STOP: preparation count changed')
        b=receipt['binding']['page_binding']
        page=g.load_cached_page(b['source'],b['cache_directory'],b['source_sha256'])
        inventory.load(page,directory)
        if claim['preparation_binding']!=receipt['binding']:
            raise ValueError('STOP: preparation identity changed')
    if len(claims)!=data['column_crossing_coverage']['prepared_pages']:
        raise ValueError('STOP: separator count changed')
    if data['runtime_forbidden_attempts'] or data['publish_actions']:
        raise ValueError('STOP: forbidden runtime action')
    if data['ledger_sha256']!='76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f':
        raise ValueError('STOP: ledger changed')
    print(f'SEG-CP5 guard: PASS; {len(FILES)} exact files; HEAD {head}; no staging/commit/publication')


if __name__=='__main__':
    verify(json.loads((ROOT/SEG/'CP5_COMMIT_LIST.json').read_text()))
