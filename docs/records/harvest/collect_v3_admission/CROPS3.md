# CROPS3: preparation for admitted W2 originals

Prepared 2026-10-19T23:54:53+0300 (Athens, stamped by `date`). **No full-scale Mac staging, upload, ssh, network access or push was performed.** Census_05 admitted rows remain unknown. The only regenerated crops were the seeded 2,000-row measurement. The requested sample directory was denied by the sandbox; the verified sample is at `/private/tmp/crops3-estimate-20261019/crops_w2_estimate` instead.

## Staging after census_05 exists and the owner gives per-run go

From this checkout, set `ADMISSION` to the actual census_05 `admitted_train.jsonl` path. The command below checks that this input exists; it does not assume a census_05 deployment path that has not been supplied.

```sh
ADMISSION=/absolute/path/to/census_05/admitted_train.jsonl
test -f "$ADMISSION" && \
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python \
  docs/harvest/collect_v3_admission/stage_crops.py \
  --admitted "$ADMISSION" \
  --features ~/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl \
  --out ~/Projects/collect-v3-data/w2_originals_v3 \
  --minimum-free-gb 10
```

The census adapter accepts canonical `id` or `row_id`, selects parent `collect-v3-W2-20261018-0524`, rejects zero W2 rows and duplicate/conflicting identities, and checks final ADMIT/train fields when present. Raw collector `admitted` flags are not census verdicts. The legacy admission format remains supported, including W1 callers; W2 features select the W2 cohort. The CLI and `--extend` remain available. For the complete census_05 cohort use the command above without `--extend`: withdrawn membership must not be carried into a new admission set. Use `--extend` only for intentionally cumulative tranches with the same admission identity.

Crops go to `~/Projects/collect-v3-data/w2_originals_v3/<source>/<row_id>.png`. Metadata stays beside `--out`, preserving the CROPS1 CLI contract:

- `~/Projects/collect-v3-data/crops_manifest.jsonl`: row_id, parent_id, source, path relative to this directory, sha256, bytes and admission metadata.
- `crops_receipt.json` and `crops_failures.jsonl`; extended runs use admission-specific receipt/failure/deferred names.
- Exit 0 means complete, 1 means failures, 2 means disk-deferred rows. The default free-space floor is 10 decimal GB. Valid staged files are verified and skipped on resume.

`ensure_crop` checks the PNG hash before atomic publication. Encoding mismatches are recorded as failures and never published. Existing corrupt files are reported and are not silently replaced. Failure runs cannot publish a replacement manifest; the uploader also checks failure sidecars and incomplete staging receipts to reject stale or partial custody. The run root, snapshots and their output/metadata overlaps are guarded explicitly.

## Upload command, prepared only

After successful authorized staging, review its receipt (failures=0, disk_deferred=0) and run this only when upload is authorized:

```sh
docs/harvest/collect_v3_admission/upload_crops.sh \
  ~/Projects/collect-v3-data/w2_originals_v3 \
  ~/Projects/collect-v3-data/crops_manifest.jsonl
```

This sends only active manifest files to `clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_w2_originals/`, copies the derived `crops_sha256.txt` alongside, and executes `sha256sum -c` there. Local hashes/sizes, failure rows/sidecars, deferred receipts and paths are checked before transport. `upload_receipt.json` beside the local manifest records file_count, bytes, mismatches, remote_path, Athens start/end times and status. A verification error exits nonzero; a successful receipt requires 0 mismatches. The local mock uses `CROPS3_MOCK_REMOTE`; `CROPS3_MOCK_CORRUPT` injects corruption after copy only in that mock branch. Tonight all uploader executions used the mock branch.

## Measurement

| Source | W2 rows | Sample | Mean bytes | Median bytes | p95 bytes |
|---|---:|---:|---:|---:|---:|
| bsb_poly1850 | 20,316 | 185 | 22,030.96 | 22,450.0 | 40,662 |
| elstat | 14,835 | 135 | 2,815.21 | 1,447.0 | 10,484 |
| gazette_modern | 119,033 | 1,085 | 6,362.55 | 4,221.0 | 14,357 |
| ia_poly1850 | 48,454 | 442 | 32,780.62 | 33,990.0 | 67,246 |
| nlg | 9,889 | 90 | 32,729.00 | 37,795.5 | 51,339 |
| serbia | 6,854 | 63 | 11,477.70 | 12,725.0 | 19,887 |


All **219,381 rows**: **3.237 GB** (95% **3.129–3.346 GB**). Admitted-only formula: **Σₛ admitted_rowsₛ × source_mean_bytesₛ**. W1-share proxy, applied per source: **0.922 GB** using 28,798/101,098 (28.49%). The proxy is not a census_05 estimate based on known admissions.

Measured **9.33 seconds per 1,000 crops**; rough full-row staging **34.1 minutes**, admitted-proxy staging **9.7 minutes**. See [CROPS3_ESTIMATE.md](CROPS3_ESTIMATE.md) and [CROPS3_ESTIMATE.json](CROPS3_ESTIMATE.json) for sample sizes, method, interval and timing limits.

## Tests and execution boundary

```sh
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -m unittest discover \
  -s docs/harvest/collect_v3_admission -p test_crops3.py -v
```

The measurement tests read the existing temporary sample and its measurement receipt; rerunning them does not regenerate crops. The fixture tests create only opaque byte fixtures. The estimate helper has no full-scale mode and refuses an existing output tree. Its census-shaped sample selection is for measurement only and is not an admission decision.

Staging all admitted W2 rows on the Mac is a **MacBook processing run requiring owner per-run go**. The alternative is **CROPS2**, reconstruction on Clariden from cached pages: [brief](../../briefs/CROPS2_clariden_w1w2_original_crops.md); **the coordinator submits**. Neither route is authorized by this preparation task.
