# CROPS3: W2 original crops for Clariden, preparation only (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Context (night plan step P8, prep only):** release v3 needs the **original** W2 crops on Clariden, byte-exact to each row's `crop_sha256`.
- The admitted W2 rows are not known until census_05 lands. So the stager and uploader must **take an admission file as input**.
- Tonight: build and test them, and measure the bytes. **Do not stage at full scale and do not upload.** Neither the Mac staging run nor the upload is part of this task.
- Precedent: the W1 originals, 28,798 rows (467 MB local; 506 MB on Clariden), are at `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_w1_originals/<source>/<row_id>.png`. CROPS1 staged them with `docs/harvest/collect_v3_admission/stage_crops.py`.

**Rules:**
- Reuse `stage_crops.py`. It already takes `--admitted --features --out --extend --minimum-free-gb` and encodes byte-exactly through `collect_v3.storage.ensure_crop`. Extend it only as far as needed; do not write a new cropper.
- Only `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` may regenerate crops.
- Read-only: the live run root `~/Projects/collect-v3-data/run` and the snapshots.
- Athens time, stamped from `date`. No pushes. No ssh; the uploader is written and mock-tested, never run against Clariden.

## Inputs (read-only)
- **Rows:** `~/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl`. Verify its sha256 against `SHA256_20261018_0524.txt`. It holds 219,381 W2 rows (the SPLIT1 count).
- **Admission-file formats to accept:**
  - the census output `admitted_train.jsonl`: one row per admitted line, keyed by `(parent_id, row_id)`, parent `collect-v3-W2-20261018-0524` (see the seg_census package in `~/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/seg_census/`, read-only, for the exact row fields);
  - the older `w2_originals_v3_admitted.jsonl` format that stage_crops already reads.

  Detect the format, select the W2 rows, and refuse an input with zero W2 rows.

## Do
1. **Stager.**
   - Add an adapter so that `stage_crops.py` accepts the census admission file; keep the current CLI working.
   - Output: `~/Projects/collect-v3-data/w2_originals_v3/<source>/<row_id>.png`, plus `crops_manifest.jsonl` (row_id, parent_id, source, relative path, sha256, bytes) and a receipt.
   - Every file must have sha256 == `crop_sha256`. Mismatches go to failures, never into the tree.
   - Keep the disk floor (`--minimum-free-gb`, default 10) and resume/idempotence (valid files are skipped).
2. **Uploader:** `docs/harvest/collect_v3_admission/upload_crops.sh`.
   - Takes `<local tree> <manifest>`, and rsyncs to `clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_w2_originals/` (same layout as W1).
   - Then runs a remote `sha256sum -c` over a manifest-derived checksum file, copied up alongside.
   - Writes `upload_receipt.json`: file count, bytes, mismatches (must be 0), remote path, times.
   - It must refuse to start if the local manifest has any failure rows.
   - Mock-test it against a local directory standing in for the remote, with an injected corrupt file. **Never run it against Clariden.**
3. **Measurement** (light; this is the only crop generation allowed tonight):
   - Regenerate a **seeded, source-stratified sample of 2,000 W2 rows** into `~/Projects/collect-v3-data/crops_w2_estimate/` with the byte-exact interpreter. Check sha == crop_sha256 for every row.
   - Report:
     - mean, median and p95 bytes per row per source;
     - the estimate for **all 219,381 W2 rows** (Σ source rows × mean bytes, with a 95% interval);
     - the **admitted-only** formula: bytes = Σ over sources of admitted rows × mean bytes per row.
   - Give a **rough** admitted-only figure under a stated proxy: the W1 admitted share 28,798/101,098 = 28.5%, applied per source. Label it a proxy.
   - Also report the time per 1,000 crops, to project the full staging time.
4. **Tests:**
   - the census-format adapter (fixture rows);
   - byte-exactness on the sample;
   - idempotent re-run;
   - the disk-floor stop;
   - the uploader mock (good tree passes; corrupt file → mismatch > 0 → failure exit);
   - no writes under the run root.
5. **`docs/harvest/collect_v3_admission/CROPS3.md`:**
   - the exact staging and upload commands for the moment the census_05 admission file exists;
   - the measured bytes table;
   - one note: staging all admitted W2 rows on the Mac is a MacBook processing run (owner per-run go). The alternative is CROPS2 (reconstruct on Clariden from the cached pages; brief `docs/briefs/CROPS2_clariden_w1w2_original_crops.md`, coordinator submits).

Write a guarded commit list: code, tests, CROPS3.md, the estimate table and this brief. No PNGs in git. The last line must be exactly:
`CROPS3: done | sample <k>/2000 byte-exact | W2 all-rows est <GB> GB (95% <lo>-<hi>) | admitted proxy <GB> GB | <s> s per 1k crops | uploader mock pass | tests: <n> passed`
