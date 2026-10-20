#!/usr/bin/env python3
"""Freeze the collector dependency closure from local installed metadata, offline."""
from importlib import metadata as md
import json,platform,sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.markers import default_environment

ROOT=Path(__file__).resolve().parent
DIRECT=['numpy','Pillow','scipy','opencv-python-headless','pypdfium2','beautifulsoup4','requests','google-auth','pytest']

def pins():
    pending=list(DIRECT);found={};env=default_environment()
    env.update(sys_platform='linux',platform_system='Linux',platform_machine='x86_64',python_version='3.11',python_full_version='3.11.3',extra='')
    while pending:
        dist=md.distribution(pending.pop());name=dist.metadata['Name'].lower().replace('_','-')
        if name in found:continue
        found[name]=dist.version
        for value in dist.requires or []:
            req=Requirement(value)
            if req.marker and not req.marker.evaluate(env):continue
            dependency=md.distribution(req.name)
            if dependency.version not in req.specifier:raise ValueError('installed dependency does not satisfy '+str(req))
            pending.append(req.name)
    return dict(sorted(found.items()))

if __name__=='__main__':
    result=pins()
    (ROOT/'requirements.lock').write_text('# CPython 3.11.3, Linux x86_64. Exact installed collector closure.\n# Wheel hashes must be sealed from target Linux wheels; Mac RECORD hashes are not wheel hashes.\n'+''.join(name+'=='+version+'\n' for name,version in result.items()))
    (ROOT/'lock_provenance.json').write_text(json.dumps(dict(python=platform.python_version(),source='local .venv importlib.metadata; no index queries',target='CPython 3.11.3 Linux x86_64',packages=result,hashes='Target wheels unavailable offline; seal worker/wheelhouse before bootstrap.'),indent=2)+'\n')
    print('locked packages:',len(result))
