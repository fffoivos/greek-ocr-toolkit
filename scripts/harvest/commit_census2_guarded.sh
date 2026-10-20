#!/bin/zsh
set -eu
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-census
PYTHONPATH=$PWD ~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python - <<'GUARD'
import greekocr
from pathlib import Path
assert Path(greekocr.__file__).resolve().is_relative_to(Path.cwd())
import subprocess, hashlib
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip() == '651752a69ee018a495c92811a9731d239e8547a1'
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip() == 'sol/census-v2-serbian'
assert not subprocess.check_output(['git','diff','--cached','--name-only'])
manifest = {'greekocr/harvest/admission.py': '407178d08bb33f98a8e7d7b2b44c9aaec8352810b9d97b9427576ce9f96b9a1b', 'tests/test_adm5c_variants.py': '64ebb0126656c47305ef373c8f87f307df5b23f5848d9bd5388d8e81dda057ed', 'scripts/harvest/reissue_census2.py': '10412eb4ac8223cb9544ba7c3cb97141a03f1915b4ae694e42efc1519761666b', 'docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018.md': '8720980d685da8cf70f03f0b1b1e0c41d839c63f875b66ecebedb4aec1b7c790', 'docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018_admission.jsonl': '090b91abb4ba9bdb5110da90daca29356c3efd65600b88ed3018dc2b3f1932b1', 'docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018_admission_receipt.json': 'f37e1d3f3e995186c9ab19d3fc3cf3f83d04d35845ce83140b6397e59c3163e2', 'docs/records/harvest/collection/v2/census2_changed_rows.json': '1b938f22cdb6090bacfae0fe15f256b8a7397c178f2c7646f25d9eb626bb20a9', 'docs/records/harvest/collection/v2/census2_comparison.json': '7aba8c726f95e4af345cd959e7296ad04e5d071cf1ba32b68e149fc8ab7551e4', 'docs/records/harvest/collection/v2/census2_document_language.json': '82c5450dc9acd7724c95b9b211abda956057362775c9ed6346c9e1155ab92809', 'docs/records/harvest/collection/v2/census2_validation.json': '3e62a225ecdfd57298d175f092229983bdd92b78559e23f9d46a441b1d45ce77'}
for path, expected in manifest.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'add', '--sparse', '--', *manifest], check=True)
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()) == set(manifest)
subprocess.run(['git', 'diff', '--cached', '--check'], check=True)
subprocess.run(['git', 'commit', '-m', 'CENSUS2: reissue v2 admission with metadata-bound Serbian codec extension'], check=True)
GUARD
