"""Delete only the coordinator's three explicitly authorized pytest basetemps."""
from pathlib import Path
import json,subprocess,shutil
D=Path(__file__).resolve().parents[1];rows=[]
for name in ['033-regression-tmp','baseline-regression-tmp','test-tmp']:
 p=D/name
 assert p.parent==D and not p.is_symlink()
 if not p.exists():continue
 assert p.is_dir()
 kib=int(subprocess.check_output(['du','-sk',str(p)]).decode().split()[0])
 logical=sum(f.stat().st_size for f in p.rglob('*') if f.is_file() and not f.is_symlink())
 row=dict(path=str(p),allocated_KiB=kib,regular_file_bytes=logical)
 shutil.rmtree(p);assert not p.exists();row['deleted']=True;rows.append(row)
receipt=dict(deleted=rows,total_allocated_KiB=sum(r['allocated_KiB'] for r in rows),total_regular_file_bytes=sum(r['regular_file_bytes'] for r in rows),preserved=['baseline/','mock_batch/','corrections/','corrections/archives/','*.log','*.xml'])
(D/'b_evidence/cleanup_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
