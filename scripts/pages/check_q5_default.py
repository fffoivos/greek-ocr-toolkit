"""Fresh 54-page, 16-mode default gate against source-bound Q4 receipts.

Q4's committed receipt already contains reference outputs. Require every Q4
production source file to be byte-identical before reusing that reference;
then run Q5's default API afresh and use the strict Q4 fingerprint comparison.
No prototype, float tolerance or extra metadata exclusion enters this gate.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    reference_path = ROOT/"docs/records/reviews/q4-speed-evidence/current-equality.json.gz"
    with gzip.open(_data_input(reference_path), "rt") as stream:
        reference = json.load(stream)
    mismatches = [name for name, expected in reference["source_manifest"].items()
                  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected]
    if mismatches:
        raise ValueError(f"Q4 sources changed; generate a fresh Q4 archive reference: {mismatches}")
    keys = sorted(p.stem for p in (ROOT/".astra/pages").glob("*.png"))
    if len(keys) != 54:
        raise ValueError(f"Expected all 54 development pages, found {len(keys)}")
    reference["pages"] = [p for p in reference["pages"] if p["page_key"] in keys]
    if sorted(p["page_key"] for p in reference["pages"]) != keys:
        raise ValueError("Q4 reference does not contain the same 54 pages")
    left, right, comparison = (args.out/name for name in ("q4", "current", "comparison"))
    left.mkdir(parents=True, exist_ok=True)
    (left/"summary.json").write_text(json.dumps(reference))
    binding = dict(q4_receipt_sha256=hashlib.sha256(_data_input(reference_path).read_bytes()).hexdigest(),
                   production_files_checked=len(reference["source_manifest"]), source_mismatches=mismatches,
                   page_keys=keys)
    (args.out/"binding.json").write_text(json.dumps(binding, indent=2))
    runner = str(ROOT/"scripts/pages/benchmark_q4.py")
    subprocess.run([sys.executable, runner, "equality", "--out", str(right), "--workers", str(args.workers),
                    "--keys", *keys], cwd=ROOT, check=True)
    return subprocess.call([sys.executable, runner, "compare", "--left", str(left), "--right", str(right),
                            "--out", str(comparison)], cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
