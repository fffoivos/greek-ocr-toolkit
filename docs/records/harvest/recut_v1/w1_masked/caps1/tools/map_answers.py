# Read-only Sol-reading tool routing; no reference worktree writes.
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from reference_adapter import map_answers
if len(sys.argv) != 4 or sys.argv[1] != 'caps1' or sys.argv[2] not in ('c1', 'c2'):
    raise SystemExit('expected: caps1 c1|c2 answers.jsonl')
print(json.dumps(map_answers(sys.argv[2], sys.argv[3])))
