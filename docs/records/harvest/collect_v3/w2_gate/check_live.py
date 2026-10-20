"""Read-only, fail-closed pre-install check; never acquire a run lock."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

OLD_SHA = "eb4a17ed1924ff77a863460fe8445f8437c62a5a68a9b4418f159e71fbf7dc98"
RUN = Path.home() / "Projects/collect-v3-data/run"

def check():
    actual = hashlib.sha256((RUN / "c1_gate.json").read_bytes()).hexdigest()
    if actual != OLD_SHA:
        raise RuntimeError(f"Live gate drift: {actual}")
    recorded = json.loads((RUN / "collector_pids.json").read_text())
    dead = []
    for key in ("supervisor", "worker"):
        pid = recorded[key]
        if type(pid) is not int or pid <= 0:
            raise RuntimeError(f"Invalid {key} PID")
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            dead.append(pid)
        else:
            raise RuntimeError(f"Collector PID still alive: {pid}")
    processes = subprocess.run(["/bin/ps", "-axo", "pid=,command="], check=True, capture_output=True, text=True).stdout
    active = [line for line in processes.splitlines() if re.search(r"(?:collect_v3/(?:run|detach)\.py|(?:^|\s)-m\s+collect_v3(?:\.run|\.detach)?(?:\s|$))", line)]
    if active:
        raise RuntimeError("Collector process found: " + repr(active))
    # Reject every open descriptor, a conservative superset of held locks.
    # lsof exit 1 with empty output/error means no matching open file.
    lock = RUN / "run.lock"
    if not lock.is_file():
        raise RuntimeError("Missing run.lock; cannot verify idle state")
    result = subprocess.run(["/usr/sbin/lsof", "-nP", "-F", "pfn", str(lock)], capture_output=True, text=True)
    if result.returncode != 1 or result.stdout.strip() or result.stderr.strip():
        raise RuntimeError(f"run.lock open or check inconclusive: {result.returncode} {result.stdout} {result.stderr}")
    return {"live_gate_sha256": actual, "recorded_dead_pids": dead, "collector_processes": [], "run_lock_open": False, "locks_acquired": False}

if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
