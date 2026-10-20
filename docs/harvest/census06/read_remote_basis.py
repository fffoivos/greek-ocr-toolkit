"""Bounded read-only summary/log inspection; no Slurm submission or data scan."""
import json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
cmd="""python3 -B - <<'REMOTE'
import json,pathlib
w=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020')
p=w/'attempts/full-split-001/summary.json';x=json.loads(p.read_text())
print(json.dumps({'summary_path':str(p),'summary_keys':list(x),'route_status_counts':x.get('route_status_counts'),'timing':{k:v for k,v in x.items() if 'tim' in k.lower()},'parent_tables':{k:v for k,v in x.items() if 'parent' in k.lower()},'log_tails':{str(p):p.read_text()[-10000:] for p in (w/'logs').glob('census-*.log')}}))
REMOTE"""
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','clariden',cmd],capture_output=True,text=True,timeout=55)
(D/'remote_basis.log').write_text(p.stderr)
p.check_returncode();result=json.loads(p.stdout);(D/'remote_basis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
