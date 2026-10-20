"""Verify SPLIT1's proposed local commit bytes and scope; never stages or commits."""
import hashlib,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=HERE,text=True).strip())
paths=(HERE/'COMMIT_PATHS.txt').read_text().splitlines();prefix=str(HERE.relative_to(ROOT))+'/'
assert paths and len(paths)==len(set(paths))
assert all(x.startswith(prefix) and '..' not in Path(x).parts for x in paths)
for line in (HERE/'COMMIT_SHA256SUMS.txt').read_text().splitlines():
 want,path=line.split('  ',1);assert path in paths
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==want,path
staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
assert set(staged)<=set(paths),f'Unrelated staged paths: {set(staged)-set(paths)}'
print(f'Guarded list verified: {len(paths)} SPLIT1 paths; {len(staged)} staged. No staging, commit or push performed.')
