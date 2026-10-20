# CROPS1: stage the admitted original crop PNGs for the wave-2 upload (gpt-6.1-sol, medium, network OFF, mechanical)

**Blocker from the coordinator:** `~/Projects/collect-v3-data/run/W1/crops` holds 0 PNGs. The collector's storage diet discards crops after each run, and `materialize` renders page crops only transiently. The admitted rows need their crop PNGs on disk, byte-identical to `crop_sha256`.

## Do
1. **Input:** `docs/records/harvest/collect_v3_admission/w1_originals_v3_admitted.jsonl` (28,798 rows; ADM5c, sha b6d13fa8…).
   - Join each `row_id` to `~/Projects/collect-v3-data/run/W1/features.jsonl` (read-only) for `crop_source_image`, `crop_source_sha256`, `crop_bbox` and `crop_sha256`.
   - The run root is live (a materialize is running): read only, no locks.
2. **Regenerate each crop** with the collector's `collect_v3.storage.ensure_crop` logic, **unchanged**:
   - verify the source raster sha;
   - `convert('L').crop(crop_bbox)`;
   - PNG `compress_level=3`.
   - Redirect **only the output path** to `docs/records/harvest/collect_v3_admission/crops/<source>/<row_id>.png` (git-ignored), and require sha256 == `crop_sha256` for every row.
   - **Use only `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.** It is the only byte-exact interpreter; the x86_64 Python re-encodes differently.
   - Mismatches or missing sources go to `crops_failures.jsonl`, with the reason; none are expected.
3. **Manifest** `docs/records/harvest/collect_v3_admission/crops_manifest.jsonl`, one line per row: row_id, source, class, relative path, sha256, bytes. Plus `crops_receipt.json`: count, total bytes, failures, the input admitted-file sha, the interpreter path and version.
4. Make the tool reusable for later admitted files (W2, Gazette, BSB, final): a CLI `stage_crops.py --admitted <file> --features <W1|W2 features> --out <dir>`.
5. Tests: the byte identity of a sample of 50; path pattern; idempotence (a second run makes no changes).

Leave a guarded commit list (manifest, receipt, tool; PNGs ignored). The last line must be exactly:
`CROPS1: done | staged: <n>/28798 | bytes: <GB> | failures: <n> | root: docs/records/harvest/collect_v3_admission/crops/<source>/<row_id>.png`
