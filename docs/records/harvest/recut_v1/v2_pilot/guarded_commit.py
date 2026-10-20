"""T6c1 source-bound commit; data and commit receipts stay outside checkouts.

Adapted from masking/guarded_commit.py. No ignored files, force-add, retry,
alternate index or unrelated staged content. Requires real pilot results.
"""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
OUTPUT = Path.home() / "Projects/collect-v3-data/v2_masked/pilot"
MANIFEST = OUTPUT / "commit-inputs.json"
STATUS = OUTPUT / "COMMIT_STATUS.json"
EXPECTED_HEAD = "a9ae2a7afce314204be7f33a5870d0efce9ecb80"
PATHS = tuple(str((BASE / name).relative_to(ROOT))
              for name in ("run.py", "guarded_commit.py", "test_run.py", "PILOT.md"))


def git(*args, check=True, stdin=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=stdin, capture_output=True, check=check)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def guards():
    if os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise RuntimeError("require actual nice >=15; refusing Git processing")
    if OUTPUT.resolve() != OUTPUT:
        raise RuntimeError("pilot output must not be a symlink")
    if git("branch", "--show-current").stdout.decode().strip() != "sol/recut-v1":
        raise RuntimeError("wrong branch")
    if git("rev-parse", "HEAD").stdout.decode().strip() != EXPECTED_HEAD:
        raise RuntimeError("unexpected starting HEAD")
    if git("diff", "--cached", "--name-only").stdout.strip():
        raise RuntimeError("unrelated staged content")
    receipt = OUTPUT / "pilot_receipt.json"
    external = OUTPUT / "PILOT.md"
    if not receipt.is_file() or not external.is_file():
        raise RuntimeError("real external pilot receipt/report required")
    if (BASE / "PILOT.md").read_bytes() != external.read_bytes():
        raise RuntimeError("worktree report is not the external report copy")
    value = json.loads(receipt.read_text())
    if value.get("schema") != "t6c1-pilot-1" or not value.get("binding", {}).get("runner_sha256"):
        raise RuntimeError("pilot did not reach source-bound execution")
    if value["binding"]["runner_sha256"] != digest(BASE / "run.py"):
        raise RuntimeError("runner changed after execution")
    for path in PATHS:
        if (ROOT / path).is_symlink():
            raise RuntimeError("symlink in commit scope")
    ignored = git("check-ignore", "--no-index", "-z", "--stdin", check=False,
                  stdin=b"".join(p.encode() + b"\0" for p in PATHS))
    if ignored.returncode not in (0, 1) or ignored.stdout:
        raise RuntimeError("ignored path or ignore-check failure")
    return receipt, external


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    receipt, external = guards()
    if args.prepare:
        write(MANIFEST, dict(schema="t6c1-guarded-commit-1", base_HEAD=EXPECTED_HEAD,
                             branch="sol/recut-v1", files=[dict(path=p, sha256=digest(ROOT / p)) for p in PATHS],
                             receipt_sha256=digest(receipt), external_report_sha256=digest(external),
                             message="harvest: record bounded large-page v2 masking pilot"))
        print("Prepared four source-bound paths; no crop data in commit")
        return
    manifest = json.loads(MANIFEST.read_text())
    if manifest["base_HEAD"] != EXPECTED_HEAD or [r["path"] for r in manifest["files"]] != list(PATHS):
        raise RuntimeError("manifest scope or HEAD changed")
    for row in manifest["files"]:
        if digest(ROOT / row["path"]) != row["sha256"]:
            raise RuntimeError("source hash changed: " + row["path"])
    if digest(receipt) != manifest["receipt_sha256"] or digest(external) != manifest["external_report_sha256"]:
        raise RuntimeError("external pilot evidence changed")
    if args.check_only:
        print("Validated exact HEAD/branch, empty index, four paths and external evidence hashes")
        return
    try:
        git("add", "--", *PATHS)
        if set(git("diff", "--cached", "--name-only").stdout.decode().splitlines()) != set(PATHS):
            raise RuntimeError("staged paths differ from manifest")
        git("diff", "--cached", "--check")
        result = git("commit", "-m", manifest["message"])
        commit = git("rev-parse", "HEAD").stdout.decode().strip()
        write(STATUS, dict(status="committed", commit=commit, manifest_sha256=digest(MANIFEST)))
        print(result.stdout.decode())
        print(commit)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        message = ((exc.stderr or exc.stdout or b"").decode(errors="replace")
                   if isinstance(exc, subprocess.CalledProcessError) else str(exc))
        write(STATUS, dict(status="commit_blocked", reason=message, base_HEAD=EXPECTED_HEAD,
                           retry_attempted=False, alternate_index_used=False,
                           manifest_sha256=digest(MANIFEST)))
        print(message, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
