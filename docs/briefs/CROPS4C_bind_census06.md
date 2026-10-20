# CROPS4C: rebind the CROPS4 package to census_06 (TRANCHE all, skip existing byte-identical files); census_06 manifest binding pending (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

The base is CROPS4B (commit fafbaca7c, `docs/harvest/collect_v3_admission/crops4/`, deployed `$W/crops4_package/add0b5f8`). Read `CROPS4.md`, `../CROPS4B_RECEIPT.md`, `crops4.sbatch`, `materialise_crops.py`, `VERIFY.sh` and `test_crops4.py`.

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

**Why:** census_06 (polytonic in scope, pipeline 0.3.3; built in parallel by the CENSUS06 brief, `docs/briefs/CENSUS06_polytonic_in_scope.md`) can admit W1/W2 rows that CROPS4 never materialised for census_05. REL4's byte-exact crop rule needs a CROPS4 run bound to census_06 **before** it can pass. The coordinator submits CROPS4C right after the census_06 readout, and REL4 then binds its receipt.

## What changes
1. **Census_06 binding.**
   - Inputs:
     - attempt `$W/census_06_20261020/attempts/full-split-002`;
     - code `$W/census_06_20261020/code/<id>/`. The id is pending: CENSUS06 deploys a pre-binding package now and a **new** id after the sf7 binding.
   - So the census_06 manifest **cannot be pinned in the package now.** Make it a submit-time input:
     - `CENSUS_MANIFEST=<path to census_06 DEPLOY_SHA256SUMS>` and `PROJECTS_SHA256=<its full sha256>`;
     - the job checks `sha256(CENSUS_MANIFEST) == PROJECTS_SHA256`, and that its first 16 hex equal the code directory's name, as the census_05 convention requires (`997b7d2ab5a8775b`);
     - then it runs the existing full `checksum -c` and the module-in-manifest guard.
   - Check how CROPS4B consumes `PROJECTS_SUMS`; reuse it if it already covers this, and add no new mechanism.
   - Keep the pinned `census05_DEPLOY_SHA256SUMS`, so the census_05 path still works unchanged.
2. **Reconstruction identity:**
   - census_06 changes only `line_pipeline.py` (+ version, readout, tests);
   - the job must assert that the imported `line_pipeline_native.py` sha is **`e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7`**, the same as census_05/CROPS4;
   - any other sha fails before materialising. Make this a pinned env/arg with that default.
3. **TRANCHE all, into the existing trees.**
   - Output base stays `$W/collection_w{1,2}_originals/<source>/<row_id>.png`.
   - The existing behaviour (`materialise_crops.py:161–188`) already:
     - skips files whose bytes match (`skipped_valid`);
     - leaves mismatches untouched (`mismatch`);
     - writes only absent files, exclusively.
   - **Verify this with tests against the real policy:**
     - any `mismatch` makes the job status not-ok and exit non-zero;
     - no existing file is ever rewritten or deleted.
   - The receipt must report `written` (new) vs `skipped_valid` (pre-existing), per tranche.
   - **The smoke gate:** full mode requires a W2 smoke receipt (`materialise_crops.py:266–272`). Keep it, bound to the census_06 attempt: smoke `crops4_c06_smoke_01`, then full `crops4_c06_full_01` with TRANCHE=all and INCLUDE_HELDOUT=1.
4. **Change nothing in `materialise_crops.py`** unless a test proves it necessary. If you change it, report it. Add no new gates beyond the manifest-sha and reconstruction-sha checks above.

## Tests and deploy
- Keep every existing test passing. Add:
  - a census_06-layout mock with an unpinned manifest supplied at submit;
  - a manifest-sha mismatch failing;
  - a manifest/code-dir name mismatch failing;
  - a wrong `line_pipeline_native.py` sha failing before materialising;
  - TRANCHE=all into a tree that already holds byte-identical files (all skipped_valid, new ones written);
  - a pre-existing mismatching file (untouched, job not ok).
- Use the byte-exact interpreter `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, as before.
- Deploy to a **new** `$W/crops4_package/<sha8>/` and read every sha back. Leave `add0b5f8` and the older roots alone.
- Run the light package VERIFY on the login node (`VERIFY_DEPLOY_OK crops4 <sha8>`).
- **Do not run anything against census_06; it does not exist yet.**
- Census_05 regression: with the census_05 env block from `CROPS4B_RECEIPT.md`, the light pre-submit checks still pass against the new root.

## Report
Write `docs/harvest/collect_v3_admission/CROPS4C_RECEIPT.md` containing:
- the diff vs CROPS4B;
- the remote VERIFY output;
- **the exact coordinator block**, with the census_06 placeholders marked `<PENDING: census_06 code id>` and `<PENDING: manifest sha>`:
  - the exports;
  - the light pre-submit checks;
  - the smoke submit;
  - the `SMOKE_OK 500/500` one-liner;
  - the full submit (`--dependency=afterok:<smoke>`, TRANCHE=all);
- time limits: state the arithmetic from the CROPS4 W2 + W1 full jobs' measured runtimes (3704831 / 3704856, from their receipts/logs, read-only) and the expected skip ratio;
- the receipt fields REL4 must bind.

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `crops4/`, `CROPS4C_RECEIPT.md` and this brief; another run works in `release_v4/` and `census06/`. No sbatch or srun.

The last line must be exactly:
`CROPS4C: done | crops4 <root> VERIFY_DEPLOY_OK <sha8> | census_06 manifest submit-time bound (pending id) | reconstruction e7dbe6c4 pinned | TRANCHE all skip-existing tested | census_05 path regression ok | tests <n> passed | no jobs submitted`
