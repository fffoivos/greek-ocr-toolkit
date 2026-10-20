# Read-only Sol-reading tool routing; no reference worktree writes.
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_adapter import rollout_scanner
raise SystemExit(rollout_scanner().main())
