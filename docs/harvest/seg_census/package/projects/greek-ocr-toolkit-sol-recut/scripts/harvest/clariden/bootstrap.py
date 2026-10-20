"""Provision a private Node runtime from official hashes; no corpus processing."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

root=Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=True)
def fetch(url,path=None):
    with urllib.request.urlopen(url,timeout=60) as response:
        if path is None:return response.read()
        with path.open('wb') as output:
            while chunk:=response.read(1024*1024):output.write(chunk)

versions=json.loads(fetch('https://nodejs.org/dist/index.json'))
version=next(v['version'] for v in versions if v['version'].startswith('v22.') and v['lts'])
name=f'node-{version}-linux-arm64.tar.xz';base=f'https://nodejs.org/dist/{version}/'
hashes=fetch(base+'SHASUMS256.txt').decode()
wanted=next(line.split()[0] for line in hashes.splitlines() if line.split()[-1]==name)
archive=root/name
if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest()!=wanted:fetch(base+name,archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==wanted
directory=root/f'node-{version}-linux-arm64'
if not directory.exists():
    with tarfile.open(archive) as tar:tar.extractall(root,filter='data')
node=directory/'bin/node'
actual=subprocess.check_output([str(node),'--version'],text=True).strip()
assert actual==version
receipt=dict(version=version,archive_sha256=wanted,node=str(node),node_sha256=hashlib.sha256(node.read_bytes()).hexdigest(),source=base+name)
(root/'node.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
