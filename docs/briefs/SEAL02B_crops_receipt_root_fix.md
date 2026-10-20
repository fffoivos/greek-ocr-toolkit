# SEAL02B: fix the seal's CROPS4 receipt check, then redeploy (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend, no jobs)

The coordinator's seal attempt failed at `VERIFY.sh inputs --bindings $W/benchmark_0.2/seal01.inputs.json --require-complete` with exit 2: `SEAL02_FAIL: CROPS4 output root/tranche/heldout differs`.

**Diagnosis (lead, read-only, verified):** `seal02/build_suite02.py:107` requires `rec['output_base'] == image_roots[tranche]`. That expectation is wrong; the receipts are right.
- CROPS4 full mode writes with `base = work_root`, so both real receipts have `output_base = /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3` (`$W`).
- Their `crops_sha256.txt` entries are relative paths `collection_w1_originals/<source>/<row_id>.png` and `collection_w2_originals/...`.
- The image roots in the bindings are `$W/collection_w1_originals` and `$W/collection_w2_originals`.
- Tranche and heldout are correct in both receipts:
  - W1: `crops4_c05_w1_full_01`, tranche W1, include_heldout true, status ok, selected 68,779 = byte_exact, 0 mismatches/failures, sha256check_exit 0.
  - W2: `crops4_c05_full_01`, tranche W2, include_heldout true, status ok, selected 139,488 = byte_exact, 0 mismatches/failures, sha256check_exit 0.

## Do
1. Make the minimal fix in `build_suite02.py`: accept the receipt when `Path(output_base) / ('collection_' + tranche.lower() + '_originals') == Path(image_roots[tranche])`. Keep the tranche and heldout checks, and every other check, unchanged.
   - Also check that `crops_sha256.txt` in that receipt's attempt directory uses the `collection_<w1|w2>_originals/` prefix. If the builder has no access to that file, skip this check and say so.
   - Do not change the receipts or CROPS4.
2. **Tests:**
   - update the mock receipts to the real shape (output_base = work root);
   - add one test that the real-shaped receipt passes;
   - add one test that a receipt whose root resolves elsewhere fails.
   - All 18 existing tests pass, or are updated only for the receipt shape; list each one updated.
3. Regenerate DEPLOY_PATHS/DEPLOY_SHA256SUMS/COMMIT_LIST. Deploy to a **new** `$W/benchmark_0.2/pkg/<new sha8>/`, keeping `ac4709c0` as it is, and read every sha back. Run `VERIFY.sh package` there.
4. **Confirm the fix on the real inputs without touching the coordinator's files.**
   - Run `build_suite02.py bind` with the new package's template, writing to the new scratch path `$W/benchmark_0.2/verify_scratch/<new sha8>.inputs.json`, with the five real inputs:
     - the three LF1 files in `$W/benchmark_0.2/lf1_inputs/` (`final_list.jsonl`, `finalize.receipt.json`, `line_verdicts_merged.jsonl`; read their shas live);
     - the two upload receipts above (shas live).
   - Then run `VERIFY.sh inputs --bindings <that scratch file> --require-complete`. It must pass. Quote its output verbatim.
   - Do not run the build or submit anything. Do not write `seal01.*` or any other existing file.
5. Add a short section to `SEAL02.md` (the date is 20 Oct):
   - the fix;
   - the new root;
   - **the exact coordinator command block**, with `CONFIG=$W/benchmark_0.2/seal02.inputs.json` and `OUTPUT=$W/benchmark_0.2/seal02`, and the full shas of the five inputs filled in from what you read;
   - **diagnostics from the LF1 receipt:**
     - flagged 350 = REPLACED 248 + UNFILLED 102; final list 2,691 rows. Give the test/dev split from the receipt, and the check 2,340 + 453 − 102 = 2,691;
     - the vertical control context `vert_w1a_w2_00003` over-flagged 3 horizontal controls as "turned" under the vertical statement. These are over-flags only; no bad line was admitted. Record this as a diagnostic about LF1's strictness, not a seal failure.
   - Also make `build_suite02.py` carry these LF1 diagnostics into `SEAL_RECEIPT.json` if the receipt already has a free-form notes or diagnostics field; otherwise put them only in the report.

Write a guarded commit list. Do not run `git add` or `git commit`. Do not touch `scaling_w3/`, where another run is working.

The last line must be exactly:
`SEAL02B: done | fix output_base=work root + collection_<w>_originals | package <new root> VERIFY package ok | inputs --require-complete ok (scratch bind) | tests <n> passed | no jobs submitted`
