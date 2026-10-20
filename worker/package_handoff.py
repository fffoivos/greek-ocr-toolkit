#!/usr/bin/env python3
"""Create a self-contained offline source+fixture archive; never includes credentials."""
import argparse,tarfile,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import sha,read_json
from collect_v3.commit_helper import nonignored
from collect_v3.portable import verify
from worker.runtime import ROOT

def package(destination):
    destination=Path(destination).resolve()
    if destination.exists():raise ValueError('destination already exists; choose a new archive path')
    fixtures=ROOT/'worker/fixtures';verify(fixtures)
    names={'pyproject.toml','.gitignore'}
    for directory in ('greekocr','collect_v3','worker'):
        for path in (ROOT/directory).rglob('*'):
            if path.is_file() and not path.is_symlink():names.add(str(path.relative_to(ROOT)))
    names,_=nonignored(sorted(names))
    names=set(names)
    for name in read_json(ROOT/'worker/planned_inputs.json')['sha256']:names.add('docs/harvest/collect_v3/'+name)
    names.update('worker/fixtures/'+name for name in read_json(ROOT/'worker/fixture_manifest.json')['sha256'])
    # A clean extract needs the declared harvest directory ignores only for documentation.
    names.add('docs/harvest/collect_v3/.gitignore')
    names=sorted(names)
    for name in names:
        path=ROOT/name
        if not path.is_file() or path.is_symlink():raise ValueError('invalid package input: '+name)
    checksum=''.join(sha(ROOT/name)+'  '+name+'\n' for name in names)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tarfile.open(destination,'w:gz',compresslevel=1) as archive:
        for name in names:archive.add(ROOT/name,arcname=name,recursive=False)
        import io
        value=checksum.encode();info=tarfile.TarInfo('HANDOFF_SHA256SUMS');info.size=len(value);info.mode=0o644
        archive.addfile(info,io.BytesIO(value))
    print('handoff archive:',destination)
    print('archive SHA256:',sha(destination))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination');a=p.parse_args();package(a.destination)
