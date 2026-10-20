# Read-only Sol-reading tool routing; no reference worktree writes.
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from reference_adapter import closure
from build import BED
directories = [Path(x) for x in sys.argv[1:]] or [BED / c for c in ('c1', 'c2')]
results = [closure(d, compatible=True) for d in directories]
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 2)
