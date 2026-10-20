"""CP6 exact review scope/bytes/base-HEAD guard. Never stages or commits."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SEG = 'docs/harvest/collect_v3_admission/seg/'
FILES = {
    'greekocr/harvest/admission.py', 'greekocr/harvest/lookalikes.py',
    'greekocr/harvest/text_primitives.py', 'greekocr/harvest/serbian.py',
    'greekocr/labelfix/text.py', 'greekocr/_vendor/bench/common.py',
    'greekocr/_vendor/bench/e1_readout.py', 'tests/test_adm5b_schema.py',
    'tests/test_seg_cp6.py',
    *[SEG + name for name in ('verify_cp6.py', 'guard_cp6_commit.py',
        'CP6_text_fixtures.json', 'CP6_RECEIPT.md', 'CP6_verification.json',
        'CP6_pytest.log')],
}
DEPENDENCIES = {
    'greekocr/_vendor/codec/v2.json', 'greekocr/_vendor/train/cer.py',
    'docs/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md',
    'docs/briefs/SEG_CP6_build.md', 'docs/briefs/SEG_CP5c_rulings.md',
    SEG + 'calibration_ledger.json', SEG + 'protected_before.json',
    SEG + 'CP5_verification.json', SEG + 'verify_cp5.py',
    'greekocr/harvest/orientation_screen.py',
    'greekocr/glyphs/foreign_ink.py', 'tests/test_seg_cp5.py',
}
EXTERNAL = {
    str(ROOT.parent / 'greek-ocr-toolkit' / f'docs/harvest/collection/v2/import_real_v2_{s}.jsonl')
    for s in ('train', 'dev', 'test')
}
EXTERNAL.update(str(ROOT.parent / 'greek-ocr-toolkit-sol-census' / p) for p in (
    'greekocr/harvest/admission.py', 'greekocr/harvest/lookalikes.py',
    'docs/harvest/collection/v2/ADMISSION_CENSUS_20261018b_admission.jsonl',
    'docs/harvest/collection/v2/ADMISSION_CENSUS_20261018b_admission_receipt.json',
    'docs/harvest/collection/v2/census2_document_language.json'))
EXTERNAL.add(str(ROOT.parent / 'greek-ocr-toolkit-sol-collect/.venv/bin/python'))
EXTERNAL.add(str(ROOT.parent / 'collect-v3-data/run/W1/features.jsonl'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(manifest):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if head != manifest['base_HEAD']:
        raise ValueError('STOP: base HEAD moved')
    for key, scope in (('files', FILES), ('read_only_dependencies', DEPENDENCIES | EXTERNAL)):
        rows = manifest[key]
        if len(rows) != len(scope) or {r['path'] for r in rows} != scope:
            raise ValueError('STOP: exact review scope changed: ' + key)
        for row in rows:
            p = Path(row['path']); p = p if p.is_absolute() else ROOT / p
            if sha(p) != row['sha256']:
                raise ValueError('STOP: bytes changed: ' + str(p))
    protected = json.loads((ROOT / SEG / 'protected_before.json').read_text())
    for path, binding in protected.items():
        if sha(ROOT / path) != binding['sha256']:
            raise ValueError('STOP: protected artifact changed: ' + path)
        # Some original-crop exports are deliberately untracked in this tree.
        tracked = subprocess.run(['git', 'cat-file', '-e', f'{head}:{path}'], cwd=ROOT,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if tracked:
            raw = subprocess.check_output(['git', 'show', f'{head}:{path}'], cwd=ROOT)
            if hashlib.sha256(raw).hexdigest() != binding['sha256']:
                raise ValueError('STOP: protected artifact differs from HEAD: ' + path)
    changes = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).splitlines()
    if any(p.endswith('.png') or p.endswith('crops_manifest.jsonl') or p in protected for p in changes):
        raise ValueError('STOP: protected tracked diff')
    # Verify every retained raster against the unchanged existing manifest.
    for line in (ROOT / 'docs/harvest/collect_v3_admission/crops_manifest.jsonl').read_text().splitlines():
        row = json.loads(line)
        if sha(ROOT / 'docs/harvest/collect_v3_admission' / row['path']) != row['sha256']:
            raise ValueError('STOP: retained crop changed: ' + row['path'])
    codec = ROOT / 'greekocr/_vendor/codec/v2.json'
    original = subprocess.check_output(['git', 'show', f'{head}:greekocr/_vendor/codec/v2.json'], cwd=ROOT)
    if hashlib.sha256(original).hexdigest() != sha(codec):
        raise ValueError('STOP: codec bytes changed')
    values = json.loads((ROOT / SEG / 'CP6_verification.json').read_text())
    if values['census_field_differences'] or values['unintended_text_changes'] or values['label_changes']:
        raise ValueError('STOP: text parity failed')
    if values['publish_actions'] or values['forbidden_attempts']:
        raise ValueError('STOP: forbidden action')
    print(f'SEG-CP6 guard: PASS; {len(FILES)} exact files; HEAD {head}; no staging/commit/publication')


if __name__ == '__main__':
    verify(json.loads((ROOT / SEG / 'CP6_COMMIT_LIST.json').read_text()))
