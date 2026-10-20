"""Temporary test layout; source bytes copied, missing local evidence linked read-only."""
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'docs/records/harvest/pipe032'
MAIN=ROOT.parent/'greek-ocr-toolkit-main-next'
DATA=ROOT.parent/'greek-ocr-data'

def prepare():
    view=Path(tempfile.mkdtemp(prefix='pipe032-',dir='/private/tmp'))/'Projects'/ROOT.name
    view.mkdir(parents=True)
    files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    # Include the new scoped test; do not copy .git or generated artifacts.
    files += ['tests/test_routes_out_of_scope.py']
    for rel in files:
        if not rel:continue
        p=ROOT/rel;q=view/rel
        if not p.is_file():continue
        q.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.py':shutil.copyfile(p,q)
        else:q.symlink_to(p)
    supplements={}
    def merge(source,target):
        if not source.exists():return
        for p in source.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:continue
            q=target/p.relative_to(source)
            if q.exists():continue
            q.parent.mkdir(parents=True,exist_ok=True)
            if p.suffix=='.py':shutil.copyfile(p,q)
            else:q.symlink_to(p)
            supplements[str(q.relative_to(view))]=str(p)
    alias='docs/cleanup_20261019/LAYOUT_ALIASES_2.tsv'
    q=view/alias;q.symlink_to(MAIN/alias);supplements[alias]=str(MAIN/alias)
    for rel in ['seg_steps','collect_v3_admission','seg_census']:
        merge(DATA/'docs/harvest'/rel,view/'docs/records/harvest'/rel)
        merge(MAIN/'docs/records/harvest'/rel,view/'docs/records/harvest'/rel)
    predictor='scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
    q=view/predictor;q.parent.mkdir(parents=True,exist_ok=True);q.symlink_to(MAIN/predictor)
    supplements[predictor]=str(MAIN/predictor)
    for name in ['greek-ocr-toolkit-sol-recut','greek-ocr-toolkit-secondary','greek-ocr-toolkit-spellcheck','greek-ocr-data','ocr-review-sites-20261018']:
        (view.parent/name).symlink_to(ROOT.parent/name,target_is_directory=True)
    (OUT/'view_receipt.json').write_text(json.dumps(dict(view=str(view),supplements=supplements,source_copies='tracked Python files byte-identical; other tracked files symlink to PIPE032; no Git metadata'),indent=2)+'\n')
    return view
if __name__=='__main__':print(prepare())
