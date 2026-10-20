"""Source/evidence-bound T6c2 commit. Explicit scope, no ignored paths, safe retry."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
import subprocess
import run

BASE_HEAD = "b5fcf4982c8dbd81dfe1fe5898a5633c830e2be6"
BRANCH = "sol/recut-v1"
PATHS = tuple(str((run.HERE / n).relative_to(run.ROOT)) for n in (
    ".gitignore", "run.py", "harm.py", "test_run.py", "guarded_commit.py", "README.md", "validation.json", "page_index.jsonl"))
MESSAGE = "T6c2: build frozen v2_test masking and per-wave paired harm gate"


def git(*args, check=True, stdin=None):
    return subprocess.run(["git", *args], cwd=run.ROOT, input=stdin, capture_output=True, check=check)


def replace_json(path, value):
    # Only helper state in the ignored test directory may be updated on retry.
    temp = path.with_suffix(".tmp")
    with temp.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    temp.replace(path)


def guard(evidence, retry=False):
    run.low_priority()
    if git("branch", "--show-current").stdout.decode().strip() != BRANCH:
        raise RuntimeError("wrong branch")
    if git("rev-parse", "HEAD").stdout.decode().strip() != BASE_HEAD:
        raise RuntimeError("starting HEAD changed")
    git("merge-base", "--is-ancestor", "414ab0b7", "HEAD")
    if not evidence.is_relative_to(run.TEST_OUTPUT) or evidence.resolve() != evidence:
        raise RuntimeError("evidence must be inside ignored test-out without symlinks")
    scope = set(PATHS)
    staged = set(git("diff", "--cached", "--name-only").stdout.decode().splitlines())
    if staged and (not retry or not staged <= scope):
        raise RuntimeError("unrelated or unauthorized staged content")
    for name in PATHS:
        if not (run.ROOT / name).is_file() or (run.ROOT / name).is_symlink():
            raise RuntimeError("missing/symlink commit source: " + name)
    ignored = git("check-ignore", "--no-index", "-z", "--stdin", check=False,
                  stdin=b"".join(p.encode() + b"\0" for p in PATHS))
    if ignored.returncode not in (0, 1) or ignored.stdout:
        raise RuntimeError("ignored path or ignore check failed")
    # Confirm the exclusion rule itself works before Git can see generated data.
    if git("check-ignore", str(evidence / "lines.jsonl"), check=False).returncode != 0:
        raise RuntimeError("test data are not ignored")
    import harm
    receipt, records, _ = harm.verify_mask_output(evidence)
    selection = json.loads((evidence / "selection.json").read_text())
    if not receipt["test_mode"] or receipt["completed_pages"] != 14 or any(sum(p["wave"] == w for p in selection) != 2 for w in run.WAVES):
        raise RuntimeError("real 14-page check required")
    if any(not r["recut_pixels_equal"] for r in records):
        raise RuntimeError("test re-cut pixel equality failed")
    h = json.loads((evidence / "harm/harm_receipt.json").read_text())
    b = json.loads((evidence / "harm/binding.json").read_text())
    u = json.loads((evidence / "unit_receipt.json").read_text())
    validation = json.loads((run.HERE / "validation.json").read_text())
    for name, path in (("mask", evidence / "mask_receipt.json"),
                       ("harm", evidence / "harm/harm_receipt.json"),
                       ("unit", evidence / "unit_receipt.json")):
        if validation[name + "_receipt_sha256"] != run.sha(path):
            raise RuntimeError("reviewable validation copy differs from test evidence")
    if h["status"] != "completed" or h["overall"]["lines"] != len(records) or not h["unchanged"]["identical_predictions"]:
        raise RuntimeError("complete paired test with identical unchanged predictions required")
    if b["harm_sha256"] != run.sha(run.HERE / "harm.py") or b["mask_receipt_sha256"] != run.sha(evidence / "mask_receipt.json"):
        raise RuntimeError("harm source or mask receipt changed")
    if not u["passed"] or not u["tests"]:
        raise RuntimeError("unit tests failed/missing")
    for name, digest in u["sources"].items():
        if run.sha(run.HERE / name) != digest:
            raise RuntimeError("source changed after unit tests: " + name)
    for name, digest in h.items():
        if name == "binding_sha256" and run.sha(evidence / "harm/binding.json") != digest:
            raise RuntimeError("harm binding changed")
        if name == "paired_sha256" and run.sha(evidence / "harm/paired.jsonl") != digest:
            raise RuntimeError("paired results changed")
    return {str(p.relative_to(evidence)): run.sha(p) for p in (
        evidence / "mask_receipt.json", evidence / "harm/harm_receipt.json", evidence / "unit_receipt.json")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=run.TEST_OUTPUT / "import-verified")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--retry", action="store_true", help="revalidate the exact manifest after a blocked Git attempt")
    args = parser.parse_args()
    evidence = args.evidence.expanduser().absolute()
    artifacts = guard(evidence, args.retry)
    manifest_path, status_path = evidence / "commit-inputs.json", evidence / "COMMIT_STATUS.json"
    if args.prepare:
        run.write_json(manifest_path, dict(base_head=BASE_HEAD, branch=BRANCH, message=MESSAGE,
                       files=[dict(path=p, sha256=run.sha(run.ROOT / p)) for p in PATHS], evidence=artifacts))
        print("Prepared eight explicit source/report/catalogue paths; ignored data excluded")
        return
    manifest = json.loads(manifest_path.read_text())
    if manifest["base_head"] != BASE_HEAD or manifest["branch"] != BRANCH or manifest["evidence"] != artifacts:
        raise RuntimeError("manifest base/evidence changed")
    if [r["path"] for r in manifest["files"]] != list(PATHS):
        raise RuntimeError("manifest scope changed")
    for row in manifest["files"]:
        if run.sha(run.ROOT / row["path"]) != row["sha256"]:
            raise RuntimeError("manifest source changed: " + row["path"])
    staged = git("diff", "--cached", "--name-only").stdout.decode().splitlines()
    for path in staged:
        import hashlib
        if hashlib.sha256(git("show", ":" + path).stdout).hexdigest() != run.sha(run.ROOT / path):
            raise RuntimeError("previous staged bytes differ from guarded source")
    if args.check_only:
        print("Validated branch, HEAD, eight nonignored paths, 14 pages, paired readout and unit source hashes")
        return
    if args.retry:
        previous = json.loads(status_path.read_text())
        if previous["status"] != "commit_blocked" or previous["manifest_sha256"] != run.sha(manifest_path):
            raise RuntimeError("retry requires same blocked manifest")
    try:
        git("add", "--", *PATHS)
        if set(git("diff", "--cached", "--name-only").stdout.decode().splitlines()) != set(PATHS):
            raise RuntimeError("staged scope differs")
        git("diff", "--cached", "--check")
        result = git("commit", "-m", manifest["message"])
        commit = git("rev-parse", "HEAD").stdout.decode().strip()
        replace_json(status_path, dict(status="committed", commit=commit, manifest_sha256=run.sha(manifest_path)))
        print(result.stdout.decode(), commit)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        reason = (exc.stderr or exc.stdout or b"").decode(errors="replace") if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        replace_json(status_path, dict(status="commit_blocked", reason=reason, retry_attempted=args.retry,
                                      alternate_index_used=False, manifest_sha256=run.sha(manifest_path)))
        # Reviewable fallback without touching Git's index, still exact scope.
        patch_path = evidence / "source.patch"
        if not patch_path.exists():
            with patch_path.open("xb") as stream:
                for path in PATHS:
                    diff = git("diff", "--no-index", "--binary", "--", "/dev/null", path, check=False)
                    if diff.returncode not in (0, 1):
                        raise RuntimeError("fallback patch failed")
                    stream.write(diff.stdout)
        print(reason, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
