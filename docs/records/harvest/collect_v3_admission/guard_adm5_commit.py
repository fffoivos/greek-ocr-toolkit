"""Read-only check of the exact ADM5c commit list; never stages or commits."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "docs/harvest/collect_v3_admission/ADM5_COMMIT_LIST.json"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def main():
    manifest = json.loads(MANIFEST.read_text())
    if git("branch", "--show-current") != manifest["branch"]:
        raise SystemExit("wrong branch")
    if git("rev-parse", "HEAD") != manifest["base_HEAD"]:
        raise SystemExit("HEAD changed; review and regenerate list")
    if git("diff", "--cached", "--name-only"):
        raise SystemExit("index is not empty; preserve and review unrelated staged work")
    paths = []
    for row in manifest["files"]:
        path = ROOT / row["path"]
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise SystemExit("path escapes scope")
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise SystemExit("changed file: " + row["path"])
        paths.append(row["path"])
    paths.append(str(MANIFEST.relative_to(ROOT)))
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--", *paths], cwd=ROOT, capture_output=True)
    if ignored.returncode != 1:
        raise SystemExit("ignored paths or check-ignore error: " + ignored.stdout.decode() + ignored.stderr.decode())
    subprocess.run(["git", "diff", "--check", "--", *paths], cwd=ROOT, check=True)
    print(f"ADM5c guard passed: {len(paths)} exact paths; empty index; no staging or commit")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
