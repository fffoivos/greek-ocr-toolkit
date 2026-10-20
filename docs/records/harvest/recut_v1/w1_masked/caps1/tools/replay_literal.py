# Read-only Sol-reading tool routing; no reference worktree writes.
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_adapter import load_reference, REPLAY_SUBSTITUTIONS
load_reference('replay_literal', REPLAY_SUBSTITUTIONS).worker(sys.argv[1], sys.stdin.read())
