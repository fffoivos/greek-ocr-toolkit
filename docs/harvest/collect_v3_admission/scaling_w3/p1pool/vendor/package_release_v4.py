#!/usr/bin/env python3
"""Seal package and print exact payload identity. No network or Git mutations."""
import argparse
import json
from pathlib import Path
import build_release_v4 as b

CORE = ('build_release_v4.py','rel4_contract.py','verify_release_v4.py','VERIFY.sh',
        'submit_release_v4.sh','release_v4.sbatch','INPUTS.json','test_release_v4.py',
        'bind_release_v4.py','package_release_v4.py','size_release_v4.py','crops4c_contract.py','handoff_release_v4.py')
EXCLUDED = {'DEPLOY_SHA256SUMS','DEPLOY_PATHS.txt','COMMIT_LIST.json','DEPLOY_READBACK.json'}


def identity(root):
    return b.digest(''.join(b.sha(root/n)+'  '+n+'\n' for n in CORE))


def seal(root):
    root=Path(root)
    ident=identity(root)
    (root/'PACKAGE_ID').write_text(ident+'\n')
    paths=sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and not p.is_symlink()
                 and p.name not in EXCLUDED and '__pycache__' not in p.parts and not p.name.endswith('.pyc'))
    (root/'DEPLOY_PATHS.txt').write_text('\n'.join(paths)+'\n')
    (root/'DEPLOY_SHA256SUMS').write_text(''.join(b.sha(root/n)+'  '+n+'\n' for n in paths))
    commit=paths+['DEPLOY_PATHS.txt','DEPLOY_SHA256SUMS','COMMIT_LIST.json']
    b.write_json(root/'COMMIT_LIST.json',dict(paths=commit,guarded_sha256={n:b.sha(root/n) for n in commit if n!='COMMIT_LIST.json'},
        scope='only release_v4 and authorized REL4b brief; no git add/commit executed',package_id=ident,
        brief=dict(path='docs/briefs/REL4b_bind_crops4c_033.md',sha256=b.sha(root.parents[2]/'briefs/REL4b_bind_crops4c_033.md')) if (root.parents[2]/'briefs/REL4b_bind_crops4c_033.md').is_file() else None))
    return ident

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    print(seal(p.parse_args().root))
