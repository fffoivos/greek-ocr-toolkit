# CROPS4: Clariden package that materialises the admitted original crops (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Coordinator decision (P8, 20 Oct night):** no Mac staging, no upload from the Mac. The original W2 crops are materialised **on Clariden** by a CPU job that the coordinator submits after census_05 completes. This task builds the deployable package: code, VERIFY and sbatch, all mock-tested. **It submits nothing and runs no ssh.**

## Facts the lead checked on Clariden (read-only ssh, 20 Oct)
- `$W = /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.
- **No crop files exist there for W1/W2.** The census decisions record `crop_path = $W/filter_pipeline_20261018/inputs/collect-v3-data/run/W2/crops/<row_id>.png`, but that directory does not exist. The census reconstructs crops **in memory** from `crop_source_image` (`$W/filter_pipeline_20261018/inputs/collect-v3-data/run/cache/pages/<sha256>.jpg`) plus `crop_bbox`, and binds them to `crop_sha256` (`crop_identity_status: "bound"`).
- **Page cache coverage:**
  - 4,130 page images on Clariden;
  - W2 needs 2,791 pages for 219,381 rows, with **0 missing**;
  - W1 needs 1,339 pages for 101,098 rows, with 0 missing.
  The check compared the 05:24 snapshots' `crop_source_image` basenames against the remote listing.
- **The census job environment** (census_03.sbatch, reused by the census):
  - `python=$W/filter_pipeline_20261018/venv_l1/bin/python`;
  - `LD_PRELOAD=$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng` (the byte-exact PNG codec);
  - `PYTHONPATH=<prepared projects>/greek-ocr-toolkit-sol-recut`;
  - hash-bound `SHA256SUMS` checks first;
  - `OMP_NUM_THREADS=1` and the like;
  - TMPDIR inside the attempt;
  - account a0140, partition normal, `srun` per step.
- **The W1 precedent layout:** `$W/collection_w1_originals/<source>/<row_id>.png` (28,798 files, from 17 Oct; Mac-staged, byte-exact).

## Method: the census's own reconstruction, unchanged
1. Find the function the census uses to rebuild W1/W2 crops in memory. Look in `greekocr/harvest/line_pipeline_sources.py` / `line_pipeline_adapters.py` and `tests/test_fp3_external_crop_input.py`, in `~/Projects/greek-ocr-toolkit-main-next` (the census_05 code) and `~/Projects/greek-ocr-toolkit-segcensus`, read-only.
   - At job time, **import it from the census_05 deployment's own prepared projects tree**, so the bytes are produced by exactly the code the census ran. Do not copy or rewrite it.
   - Record its module path and the sha of the file.
2. **Rows:** take `--census-attempt <dir>` (census_05 on Clariden). Resolve `CURRENT.json` → `admitted_train.jsonl` and `decisions.jsonl`.
   - Select rows whose `binding.parent_id` starts with `collect-v3-W2-` (W2 is the default; `--tranche W1|W2|all`).
   - **Scope:**
     - the default is `admitted_train.jsonl`;
     - `--include-heldout` also takes rows from `decisions.jsonl` with `admitted: true` and split dev/test.
     The benchmark draw (P5/P7) needs the crops of admitted TEST/DEV rows, which admitted_train may not hold. Report both counts in the receipt.
3. **Output:** write `$W/collection_w2_originals/<source>/<row_id>.png` (W1: `$W/collection_w1_originals/…`, skipping valid existing files).
   - Write atomically (tmp + rename).
   - Make it idempotent: skip a file whose sha matches; **never overwrite** a file whose sha differs. That is a failure, reported.
4. **Verify:** write `crops_sha256.txt` from the census `binding.crop_sha256` and run `sha256sum -c` over the tree.
   - Write `upload_receipt.json`: rows selected, written, skipped-valid, mismatches (**must be 0** for status ok), failures, bytes, the code sha, the reconstruction module + sha, the codec preload sha, the interpreter, and Athens times.
   - Write `crops_manifest.jsonl` (row_id, parent_id, source, split, relative path, sha256, bytes).
5. **Parallelism:** a process pool on one node, chunked by source page so each page is decoded once. Keep memory bounded.

## Package (`docs/harvest/collect_v3_admission/crops4/`)
- `materialise_crops.py`, plus `crops4.sbatch`:
  - account a0140, partition normal, 1 node, `--time` sized from a measured mock rate with a 3× margin (≤ 2 h), `--cpus-per-task` stated;
  - output and TMPDIR under `$W/crops4_attempts/<attempt>/`;
  - a `MODE=smoke|full` variable: smoke = the first 500 W2 rows by sorted row_id, writing into the attempt directory and **not** into `collection_w2_originals`; it must report 500/500 byte-exact before full is allowed.
- `VERIFY.sh`, run on Clariden before submission:
  - sha-compares the deployed files with `DEPLOY_SHA256SUMS`;
  - checks the census attempt has CURRENT.json and the admitted file;
  - checks the page-cache coverage for the selected rows (0 missing);
  - prints exactly `VERIFY_OK <n_rows> <n_pages>` or fails.
- `DEPLOY_PATHS.txt` and `DEPLOY_SHA256SUMS`: what the coordinator rsyncs, to where.
- `CROPS4.md`: the exact deploy → VERIFY → smoke → full commands; the expected counts and bytes (W2 all rows ≈ 3.24 GB, from CROPS3); the receipt fields; and what to do on a mismatch (stop; report pixel vs encoder difference; never accept pixel-equal byte-different).

## Tests (local mock, no network)
- A mock census attempt: CURRENT.json, a small admitted_train and decisions, a mock page cache built from 20 local W2 rows whose source pages exist under `~/Projects/collect-v3-data/run/cache/pages` (read-only), and a mock `$W`.
- Then:
  - the materialiser reproduces those rows' `crop_sha256` exactly with the local byte-exact interpreter `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, through the same reconstruction function;
  - smoke never writes into the collection path;
  - idempotent re-run;
  - a pre-existing corrupt file → failure, not overwritten;
  - `--include-heldout` selection;
  - VERIFY fails on a hash drift and on a missing page;
  - `sha256sum -c` (or `shasum -a 256 -c` locally) passes.
- Run the sbatch script end to end against the mock with `srun` stubbed (mock-test cluster scripts).

Write a guarded commit list (crops4/ + this brief). The last line must be exactly:
`CROPS4: done | reconstruction <module>:<function> (sha <8>) | mock <k>/<k> byte-exact | smoke gate 500 | time limit <hh:mm> cpus <c> | VERIFY mock ok+fail cases | tests: <n> passed`
