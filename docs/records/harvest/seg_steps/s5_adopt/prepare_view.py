"""Temporary read-only compatibility view for CLEAN3 data and CLEAN4L docs moves.

Only four historical replay scripts are copied so their unchanged parents[4]
root calculation still applies. All evidence/code/assets are symlinks to their
current custody locations. The real checkout and archives are never restored.
"""
from pathlib import Path
import csv, hashlib, json, shutil, tempfile

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'greek-ocr-data'


def prepare():
    base = Path(tempfile.mkdtemp(prefix='seg10-', dir='/private/tmp'))
    view = base / 'Projects' / ROOT.name
    view.mkdir(parents=True)
    verified = {}
    receipts = {}
    for shard in sorted((ROOT / 'docs/cleanup_20261019/data_out/RECEIPTS').glob('receipt_*.tsv')):
        for rec in csv.DictReader(shard.open(), delimiter='\t'):
            receipts[rec['path']] = (rec, str(shard.relative_to(ROOT)))

    def merge(source, target, external=False):
        for p in source.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:
                continue
            q = target / p.relative_to(source)
            if q.exists():
                continue
            q.parent.mkdir(parents=True, exist_ok=True)
            if external:
                rel = str(p.relative_to(DATA))
                rec, shard = receipts[rel]
                actual = hashlib.sha256(p.read_bytes()).hexdigest()
                assert actual == rec['sha256'], (p, actual, rec)
                verified[rel] = dict(sha256=actual, receipt=shard)
            q.symlink_to(p)

    for rel in ('seg_steps', 'collect_v3_admission/segeval1'):
        target = view / 'docs/harvest' / rel
        merge(ROOT / 'docs/records/harvest' / rel, target)
        merge(DATA / 'docs/harvest' / rel, target, True)
    for step in ('s1', 's2', 's3', 's4'):
        p = view / 'docs/harvest/seg_steps' / step / 'replay.py'
        p.unlink()
        shutil.copyfile(ROOT / 'docs/records/harvest/seg_steps' / step / 'replay.py', p)
    for name in ('greekocr', 'scripts'):
        (view / name).symlink_to(ROOT / name)
    p = view / 'docs/harvest/line_pipeline'
    p.mkdir(parents=True)
    merge(ROOT / 'docs/harvest/line_pipeline', p)
    analysis = p / 'gate03/part2_analysis.py'
    analysis.unlink()
    shutil.copyfile(ROOT / 'docs/harvest/line_pipeline/gate03/part2_analysis.py', analysis)
    (view / 'tests').mkdir()
    for name in ('conftest.py', 'test_content_gate.py', 'test_line_pipeline.py', 'test_seg_gate.py',
                 'test_seg_deskew.py', 'test_seg_curve.py', 'test_seg_small.py', 'test_integration_fixes.py'):
        shutil.copyfile(ROOT / 'tests' / name, view / 'tests' / name)
    (view / 'tests/fixtures').symlink_to(ROOT / 'tests/fixtures')
    for name in ('greek-ocr-toolkit-sol-recut', 'ocr-review-sites-20261018',
                 'greek-ocr-toolkit-secondary', 'greek-ocr-toolkit-spellcheck'):
        (view.parent / name).symlink_to(ROOT.parent / name)
    receipt = dict(view=str(view), data_root=str(DATA), verified_external=verified,
                   replay_scripts='byte-identical copies of s1-s4; original depth restored',
                   tests='byte-identical copies of requested tests and conftest', fallback='temporary layout view only')
    (OUT / 'view_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return view


if __name__ == '__main__':
    print(prepare())
