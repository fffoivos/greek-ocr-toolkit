# CROPS1 staging

Run offline from the checkout root:

```sh
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/stage_crops.py \
  --admitted docs/records/harvest/collect_v3_admission/w1_originals_v3_admitted.jsonl \
  --features ~/Projects/collect-v3-data/run/W1/features.jsonl \
  --out docs/records/harvest/collect_v3_admission/crops
```

The CLI calls the collector's unchanged `collect_v3.storage.ensure_crop` with
only `crop` redirected. Source raster hashes, bounding boxes, admitted hashes,
and encoded PNG hashes are checked. Existing crops and unchanged metadata are
left untouched. Failures are recorded per row and cause exit status 1. A missing
feature row also becomes a failure. Duplicate IDs or a features file changing
during its read abort the run. No collector locks or materialization are used.

`--out` is the PNG root. Its parent receives `crops_manifest.jsonl`,
`crops_receipt.json`, and `crops_failures.jsonl`. Manifest `path` values are relative
to that parent: `crops/<source>/<row_id>.png` for this cohort. Use a separate output
parent for later cohorts to preserve earlier manifests and receipts. Add any
alternative PNG root to gitignore before staging it. The receipt binds the
admitted and features bytes, collector storage code, interpreter, and Pillow.
The requested interpreter is a symlink; both the requested and Python-reported
executable paths are recorded.

Verify the staged cohort with:

```sh
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/test_stage_crops.py
```

Checks cover every PNG's hash, size, class and path, a deterministic random sample
of 50 fresh encodings compared byte for byte, a complete second CLI run with
unchanged file and directory inventory (including inode and modification/change
timestamps), and missing/mismatched source failure recording. Access times are
excluded because read-only verification can update them.

The guarded commit list is `CROPS1_COMMIT_LIST.json`. Run the read-only guard:

```sh
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/guard_crops_commit.py
```

It checks branch, HEAD, empty index, exact file hashes, whitespace, and that every
manifest PNG is ignored while every commit candidate is unignored. It never
stages or commits. Existing unrelated work is excluded from the list.
