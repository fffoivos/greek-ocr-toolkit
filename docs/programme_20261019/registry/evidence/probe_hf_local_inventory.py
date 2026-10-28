"""Re-stat the pinned Mac source selection; never read bulk page/response bytes."""
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

repo=Path(__file__).resolve().parents[2]
p=repo/'docs/programme_20261019/registry/SOURCE_MANIFEST.json'
m=json.loads(p.read_text())
out=dict(at=datetime.now(timezone.utc).isoformat(),basis='fresh stat only; stored SHA gaps remain',
         selected_manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),groups={})
for name,group in m['groups'].items():
    inventory=repo/group['inventory_path']
    assert hashlib.sha256(inventory.read_bytes()).hexdigest()==group['inventory_sha256']
    q=dict(files=0,bytes=0,missing=[],size_changed=[],mtime_changed=[])
    with inventory.open() as f:
        for r in csv.DictReader(f,delimiter='\t'):
            source=Path(m['roots'][r['root']])/r['relative_path']
            if not source.is_file():
                q['missing'].append(str(source));continue
            s=source.stat();q['files']+=1;q['bytes']+=s.st_size
            if s.st_size!=int(r['bytes']):q['size_changed'].append(str(source))
            if s.st_mtime_ns!=int(r['mtime_ns']):q['mtime_changed'].append(str(source))
    out['groups'][name]=q
(repo/'out/runner4/HF_LOCAL_STATS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
