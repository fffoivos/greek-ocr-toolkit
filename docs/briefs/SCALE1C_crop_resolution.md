# SCALE1C: resolve W1/W2 crops to the CROPS4 originals; test on real crops; redeploy (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend, no jobs)

**Failure:** the subsets job 3705085 failed (`$W/scaling_w3/subsets/scale1-3705085.log`) at `scaling_w3/scale.py:193` in `exposure()`, called from `build_job` at line 258:

`require(p.is_file(),'missing crop …')` on `/iopsstor/…/filter_pipeline_20261018/inputs/collect-v3-data/run/W2/crops/gazette_modern--2c53a696417985d2--s000-l0020.png`

**Cause:** the census `crop_path` for W1/W2 rows points into the 18 Oct filter-pipeline input tree, which no longer exists. The byte-exact W1/W2 crops are the CROPS4 originals:
- `$W/collection_w1_originals/<source>/<row_id>.png`;
- `$W/collection_w2_originals/<source>/<row_id>.png`.

REL3 resolves them this way: its `release_v3_admission.jsonl` rows carry `crop_relative_path` (e.g. `collection_w1_originals/bsb_poly1850/<row_id>.png`) and `crop_sha256`. The v_c rows stay on their census `crop_path` (`$W/collection_v2/crops/<wave>/…`); the lead verified 2,003/2,003 of those byte-exact. `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Do
1. **The minimal fix in `scale.py`.**
   - W1/W2 rows get their crop path from the bound REL3 release row, `$W/` + `crop_relative_path`, and their sha from the release `crop_sha256`. Assert that this equals the census decision's `binding.crop_sha256` for the same key.
   - v_c rows keep the census `crop_path`.
   - Apply this everywhere a crop path is read or written to the subset outputs, not only in `exposure()`.
   - Every other check stays, including the re-hash of every crop.
   - Grep the package for any other use of census `crop_path` / `crop` / `crop_source_image` on W1/W2 rows and fix it the same way. List each one.
2. **Real-crop test (the subsets run must not be the first thing to touch a path).** On Clariden, read-only and light:
   - take ≥ 20 real rows per parent: W1 and W2 from the release file, v_c from census admitted_train (the 60-row real fixture is fine);
   - resolve each crop path through the **package's own resolver function**, open it, and re-hash it against crop_sha256;
   - all must exist and match. Quote the counts.
   - Add a test that runs the resolver on the committed real fixture rows, plus a test that fails if a W1/W2 row would resolve to the census crop_path.
3. **Reuse the completed tags output.** The tags job 3705068 (attempt `scale1-c05-002`) completed. Its receipt is `$W/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json`.
   - Read its status and sha live.
   - Confirm that the new package's tags code is byte-identical to the one that produced it, so the receipt stays valid: either compare the code shas recorded in the tags receipt with the new package, or show that the tag path is untouched by this fix. If the tag code changed, stop and report.
4. Re-run all tests. Regenerate the manifests. Deploy to a **new** `$W/scaling_w3/data_pkg/<sha8>/`, leaving `d14521ee` and `b23cfcc1` as they are, and read every sha back. Run `VERIFY.sh package` and `VERIFY.sh inputs-subsets <tags receipt> <its sha>` there; it must pass.
   - Check read-only that `$W/scaling_w3/subsets/scale1-c05-003` does not exist. If it does, use the next free name.
5. Add a SCALE1C section to `SCALE1.md`:
   - the fix and each changed site;
   - the real-crop results;
   - the tags-receipt reuse check;
   - **the exact two-line coordinator block** (`VERIFY.sh inputs-subsets …` and `submit_subsets.sh scale1-c05-003 <receipt> <sha>`), with the new root and the full receipt sha filled in.

Write a guarded commit list. Do not run `git add` or `git commit`. Do not touch `seal02/`.

The last line must be exactly:
`SCALE1C: done | W1/W2 crops via CROPS4 originals (REL3 relative path), v_c via census crop_path | real crops W1 <a>/<a> W2 <b>/<b> v_c <c>/<c> byte-exact | tags receipt <sha8> reused, tag code unchanged | package <root> VERIFY package ok inputs-subsets ok | tests <n> passed | no jobs submitted`
