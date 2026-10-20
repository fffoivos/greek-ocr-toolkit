# CENSUS3 guarded commit list

Prepared and verified; no staging or commit performed. Network off.

Check: `PYTHONPATH=$PWD ~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python scripts/harvest/commit_census3_guarded.py`

Commit this exact list: append `--commit`. The helper verifies HEAD, branch, empty index, manifest and file hashes, local import, census receipt, and whitespace; staging uses `git add --sparse`.

- `greekocr/harvest/admission.py`
- `greekocr/harvest/lookalikes.py`
- `greekocr/_vendor/bench/e1_readout.py`
- `tests/test_census3_secondary_scripts.py`
- `scripts/harvest/reissue_census3.py`
- `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018b.md`
- `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018b_admission.jsonl`
- `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018b_admission_receipt.json`
- `docs/records/harvest/collection/v2/census3_changed_rows.json`
- `docs/records/harvest/collection/v2/census3_comparison.json`
- `docs/records/harvest/collection/v2/census3_validation.json`
- `scripts/harvest/commit_census3_guarded.py`
- `docs/records/harvest/collection/v2/CENSUS3_COMMIT_LIST.md`
- `docs/records/harvest/collection/v2/census3_commit_manifest.json`
