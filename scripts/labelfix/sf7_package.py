"""Build a fully hashed deploy archive without touching Git metadata."""
import json
from pathlib import Path
import tarfile
from scripts.labelfix.clariden.r1_common import sha256
from scripts.labelfix.clariden.sf7_recompose import receipt
from scripts.labelfix.release_gate_sf7 import policy_binding, PREREGISTRATION

EV=Path('docs/records/labelfix/spellcheck/SF7_evidence')


def build():
    files=set(policy_binding()['sources'])
    for folder in ('greekocr/labelfix','scripts/labelfix/clariden'):
        files.update(str(p) for p in Path(folder).glob('*.py'))
    files.update(['greekocr/__init__.py','config/sf7_job.json',
                  'scripts/labelfix/sf7_measure.py','scripts/labelfix/sf7_package.py',
                  'tests/labelfix/test_sf7.py','tests/labelfix/test_sf7_package.py',PREREGISTRATION])
    # Include every imported top-level science helper; no weights or inference
    # inputs are deployed, and all historical production inputs stay in place.
    files.update(str(p) for p in Path('scripts/labelfix').glob('*.py'))
    files.update(str(p) for p in Path('greekocr').rglob('*.py'))
    files=sorted(p for p in files if Path(p).is_file())
    Path('SF7_DEPLOY_FILES.txt').write_text(''.join(p+'\n' for p in files))
    files.append('SF7_DEPLOY_FILES.txt');files.sort()
    Path('SF7_DEPLOY_SHA256.txt').write_text(''.join(sha256(p)+'  '+p+'\n' for p in files))
    with tarfile.open('artifacts/labelfix_sf7/deploy.tar','w') as tf:
        for p in files+['SF7_DEPLOY_SHA256.txt']:
            tf.add(p,arcname=p,recursive=False)
    receipt(EV/'package_receipt.json',dict(files=len(files),every_path_hashed=True,
        manifest_sha256=sha256('SF7_DEPLOY_SHA256.txt'),archive_sha256=sha256('artifacts/labelfix_sf7/deploy.tar'),
        policy=policy_binding(),submitted=False))
    print('deploy files',len(files))


if __name__=='__main__':build()
