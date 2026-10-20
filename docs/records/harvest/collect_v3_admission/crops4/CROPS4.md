# CROPS4C deployment package

CROPS4C extends CROPS4B (`fafbaca7c`, remote `add0b5f8`) for census_06. The final census manifest is deliberately absent: its code id changes after sf7 binding. Use the exact coordinator commands in `../CROPS4C_RECEIPT.md` after the census_06 readout. This package submits nothing itself.

## Submit-time identity

`CENSUS_MANIFEST` is an alias for the existing `PROJECTS_SUMS` input, with precedence when set. `PROJECTS_SHA256` is the full SHA256 of that manifest. `PROJECTS_SUMS_ROOT` is the deployed census code directory, whose basename must equal the first 16 manifest hex digits when `CENSUS_MANIFEST` is set. The complete manifest is checked from that root, then the existing module-in-manifest guard runs. The imported reconstruction module must be inside `CENSUS_CODE` and match `RECONSTRUCTION_SHA256`, default `e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7`.

`binding_checks.sh` contains those checks and is sourced by the batch wrapper before either srun step. Coordinators source the same file for light pre-submit checks. No census rows are parsed by that file. The pinned census05 manifest remains unchanged; leave `CENSUS_MANIFEST` unset and the CROPS4B `PROJECTS_SUMS`, root and code exports continue to work.

`VERIFY.sh --deploy-only` checks the package manifest and interpreter/Pillow/codec readability, prints `VERIFY_DEPLOY_OK crops4 <directory name>`, and reads no census. Ordinary `VERIFY.sh` retains its existing input verification behavior. `CROPS4_PACKAGE` must point to the deployed sbatch because Slurm spools that script elsewhere.

## Materialisation and smoke gate

Use `crops4_c06_smoke_01` with `TRANCHE=W2 INCLUDE_HELDOUT=1`, followed by `crops4_c06_full_01` with `TRANCHE=all INCLUDE_HELDOUT=1` and the smoke receipt/dependency. Smoke writes its first sorted 500 W2 bindings only below its attempt's `smoke/collection_w2_originals`. Full requires that successful 500/500 receipt with identical census, code, interpreter, codec and heldout provenance, checks the sorted smoke selection, and rehashes all smoke files. Only tranche may differ. A census05 smoke cannot authorize census06 full.

The completed CURRENT selects an immutable generation and authenticates its summary; every consumed output is hashed. Heldout decisions join to diagnostic reconstruction metadata. No admission policy is changed.

Full outputs stay `$W/collection_w{1,2}_originals/<source>/<row_id>.png`. Existing byte-identical files are `skipped_valid`. Conflicting files are `mismatch`, preserved in place and cause a failed receipt/nonzero exit. Absent files alone are reconstructed with the imported native function and published with an exclusive hard link. Existing files are never rewritten or deleted, including in a race. On mismatch report the expected/observed SHA, bbox, page SHA and reconstruction/interpreter/codec identities; preserve all evidence.

`materialise_crops.py` changed only to aggregate `per_tranche.W1` and `.W2` counts (`selected`, `written`, `skipped_valid`, `mismatches`, `failures`, `bytes`). A failing test (`TEST_RED_PER_TRANCHE.log`, KeyError) demonstrated that reporting was absent. No pixel, encoding, publication, failure-status or smoke-gate code changed.

Receipt artifacts remain `upload_receipt.json`, `crops_manifest.jsonl`, `crops_sha256.txt`, `sha256check.log`, `failures.jsonl`, and the wrapper's prepared/verify/materialise logs. The receipt records aggregate counts and the new tranche counts; context records immutable input hashes, code path/hash, reconstruction path/hash/function, interpreter/hash, codec/hash, tranche and heldout scope. Status is ok only with zero mismatches/failures and checksum exit zero.

## Validation and sizing

Run `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/harvest/collect_v3_admission/crops4/test_crops4.py`. The tests use existing read-only source pages and temporary mock roots, with a local srun stub. The 500-row gate has 20 independent bindings plus 480 named aliases; the separate rate sample has 500 independent originals. Production reconstruction defaults remain pinned; local mocks explicitly export their distinct native SHA. See TESTS.log and TEST_RESULTS.json.

All original 16 tests remain, plus submit-time census06 layout, manifest SHA failure, code-directory mismatch, wrong reconstruction SHA, all-tranche existing/new counts and repeat preservation, mismatch job failure/preservation, and light deploy verification without census inputs.

Measured Clariden jobs 3704831 (W2) and 3704856 (W1) took 24m13s + 20m36s = 44m49s combined; materialisation receipts took 1038.521 + 866.124 = 1904.645s. The receipt documents the arithmetic and skip estimate. Batch default/full limit is 90m; smoke override is 45m. Local mock rates are not the production sizing basis.

## Guarded handoff

COMMIT_LIST.json binds every file under this package plus CROPS4C_RECEIPT.md and the supplied CROPS4C brief. `guard_commit.py` checks exact hashes, scope and unrelated staged paths and prints an explicit command without running git add or git commit. Regenerate deliberately after edits; never stage other worktree changes.
