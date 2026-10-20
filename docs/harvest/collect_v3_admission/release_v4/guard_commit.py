#!/usr/bin/env python3
"""Print a hash-guarded allowlist. Performs no Git mutation."""
import json
from pathlib import Path
import build_release_v4 as b
root=Path(__file__).resolve().parent
manifest=json.loads((root/'COMMIT_LIST.json').read_text())
for name in manifest['paths']:
    p=Path(name)
    b.require(not p.is_absolute() and '..' not in p.parts and not {'seal02','bench02','.git'}.intersection(p.parts),'forbidden commit path')
    b.require((root/p).is_file(),'missing commit file: '+name)
for name,h in manifest['guarded_sha256'].items():
    b.require(b.sha(root/name)==h,'commit hash changed: '+name)
for name in manifest['paths']:
    print('docs/harvest/collect_v3_admission/release_v4/'+name)

brief=manifest.get('brief')
if brief:
    b.require(brief['path']=='docs/briefs/REL4b_bind_crops4c_033.md','unexpected brief path')
    b.require(b.sha(root.parents[2]/'briefs/REL4b_bind_crops4c_033.md')==brief['sha256'],'brief hash changed')
    print(brief['path'])
