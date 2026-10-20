# T6c2: v2_test masking and paired harm gate

From this checkout (`sol/recut-v1`), run these **two commands**, in order:

```sh
nice -n 15 .venv/bin/python -B docs/records/harvest/recut_v1/v2_test/run.py
nice -n 15 .venv/bin/python -B docs/records/harvest/recut_v1/v2_test/harm.py
```

Both use `~/Projects/collect-v3-data/v2_masked/v2_test/`. The masking command requires a fresh directory; the harm command requires a completed masking receipt and a fresh `harm/` subdirectory. Existing crops, receipts and evaluation inputs are never overwritten. For a second run, supply the same fresh `--out /absolute/path` to both commands. Do not point the production run into this checkout.

The output contains only PNG crops under `crops/<wave>/<doc>/<file>.png`; manifests, page logs and receipts are elsewhere in the output root. `lines.jsonl` records every completed line's re-cut/stored/masked hashes, native pixel equality, nearest-curve match and candidate count, mask application, pixel/component counts, fill statistics and changes. `real_v2_test_masked.jsonl` preserves the exact E3 projected import fields and original labels, `reserved` split and codec v1, with absolute crop paths. Matched paths point under the new output's `crops/`; unmatched paths point to originals.

The masking command also runs the pinned offline `linefactory import-real` to create **`real_v2_test_masked/reserved/shard-*.parquet`**, the same import format used by E3/E4, with a `test` alias to `reserved`. Factory `--crops` uses the common ancestor of the output and original harvest (normally `~/Projects`), satisfying its canonical-path containment check for both kinds of crop. Every imported crop hash, line ID, reference, codec and script class is checked; additional drops fail the run. The emitted factory codec is compared to the pinned v1 artifact before import. All new Parquet and import receipt hashes are bound in `mask_receipt.json`. Existing evaluation shards and imports stay untouched.

The unchanged T6a2 matcher is loaded directly from its frozen source functions. Parameters: `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`; masking library: `f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5`. Ambiguous lines are masked using the nearest eligible curve and retain all candidate diagnostics. Unmatched lines remain unmasked and point to the original crop. **The pilot's zero-ambiguity rule is retired in favour of the paired harm test**, explicitly recorded in both receipts. Parliament remains excluded pending its separate matching fix.

Population comes from the hash-pinned `import_real_v2_test.jsonl` and E3's `~/Projects/greek-page-ocr/out/e3d/prepare/instrument_exclusions.jsonl` (SHA256 `3f1683e479f6a8a551d45c556cfc44c9f585a636f0af6bd38c086fca62a8b636`). Only its `instrument == v2_test` entries are used: exactly **1,991** unique exclusions. The same file also contains 151 human-instrument exclusions, which do not apply here. The runner independently reproduces the rejection identities using unchanged E3 codec normalization and binds the codec, Rust codec source and normalization code.

| Wave | Lines after codec exclusions | Pages | Action |
|---|---:|---:|---|
| round1 | 8,083 | 188 | mask |
| round2 | 3,651 | 75 | mask |
| mixed | 2,151 | 67 | mask |
| vouli | 1,739 | 49 | mask |
| openarchives | 4,642 | 154 | mask |
| cyrillic | 346 | 21 | mask |
| wikisource | 9,490 | 342 | mask |
| parliament | 11,936 | 99 | excluded |
| **Before parliament exclusion** | **42,038** | **995** | |
| **Production population** | **30,102** | **896** | |

The verified non-parliament population has **896 pages**, rather than the brief's approximate 680. The runner does not discard additional pages to reach that approximation.

`page_index.jsonl` freezes the eligible native raster paths, hashes and headers (896 pages, SHA256 `d18af4c743d521b79a3c43e050be6c752967006bfe975fdb919b5af99cc48c56`). It is a compact extract of the pilot feasibility scan (source SHA256 `7e88434b248d6411d40c17b302f90e6fab35c32408ca5454aa4e789d98b357bb`); the temporary scan file is no longer a runtime dependency. The E3 exclusion and projected-import files and the original harvest remain read-only runtime inputs.

Each page uses a fresh process and one numerical thread. At most six pages run concurrently; when any active or proposed page exceeds 20 MP, total concurrency is capped at three. All 896 current eligible raster headers are below 20 MP (maximum 17.294453 MP); unit tests also cover the large-page and mixed-size cases. Each page verifies its native raster hash, admitted crop hash and re-cut pixel equality. Different PNG encodings are recorded separately; unchanged masked crops preserve the stored original bytes. Failed pages retain explicit failure receipts and worker logs while the remaining pages continue. An incomplete mask receipt cannot enter the harm gate.

Both commands enforce actual nice >=15, block Python socket connections/DNS/bind/sendto, restrict writes to their output directory, monitor free disk every second with a 10,000,000,000-byte floor, and stop their own child process groups at the 90-minute budget. They do not acquire W1 locks. On this sandbox, `nice` prints a permission warning because the inherited priority is already 20; the checked effective priority is recorded in the receipts.

The default harm sample is **10,000 lines**, seed `20261017`, allocated proportionally by wave using largest-remainder quotas and sampled from sorted IDs. CPU E4 ctrl_s0 `best.pt` is hash-verified, and its safetensors sibling is checked tensor-for-tensor against it. The pinned `train/eval_cer.py:evaluate`, `bench/o4b_models.py:strip` and `train/data.py:collate_strips` are exactly the T6a2 CPU evaluator path and adapter. Both arms share the imported `label_ids`, independently checked against the existing E3 codec v1 normalization/folds, and the same width ordering. Inputs are read lazily by batch (16), using four Torch threads.

`harm/REPORT.md` and `harm/harm_receipt.json` report corpus CER for original and masked crops overall, per wave and per script class, plus paired line and page-cluster percentile bootstrap 95% CIs for both CERs and their difference (2,000 resamples). Page clusters include wave and page identity. Both population and sample ambiguous/unmatched counts are reported per wave. Every unchanged sampled crop must produce exactly the same prediction and edit count. The gate passes only when overall masked CER is no worse and unchanged predictions agree; per-wave results are reported even when they worsen. Exit code 2 means a completed, failed harm gate. A small test run never qualifies the production gate.

## Local verification and timing

The git-ignored `test-out/import-verified/` contains the complete two-pages-per-wave run: **14/14 pages, 596/596 lines**, all native pixel equality checks true, plus 596 imported Parquet rows with zero additional drops. Masking timings below include worker startup, detector, matching, masking, factory import, output and receipts. All 596 lines matched uniquely in this sample; 428 changed and 168 were unchanged. Frozen matching policy is also covered by unit tests.

Final masking plus factory import: **35.066 s**; paired CPU harm process: **199.912 s** (596 lines per arm). The small gate passed: **658 -> 656 edits / 36,649 reference codepoints**, CER **0.017954 -> 0.017900**. All **168 unchanged predictions** were identical. The overall delta 95% CI is `[-0.0009095567564689185, 0.0007718182563840027]` by line and `[-0.0006269363526824381, 0.0004148909414575762]` by page; both include zero. The production gate remains **unrun**.

| Test wave | Original CER | Masked CER | Delta |
|---|---:|---:|---:|
| round1 | 0.006652 | 0.007155 | +0.000502 |
| round2 | 0.006277 | 0.006277 | +0.000000 |
| mixed | 0.006392 | 0.006392 | +0.000000 |
| vouli | 0.091278 | 0.090118 | -0.001160 |
| openarchives | 0.000966 | 0.000966 | +0.000000 |
| cyrillic | 0.004053 | 0.004632 | +0.000579 |
| wikisource | 0.008836 | 0.008678 | -0.000158 |

Cyrillic and round1 worsened in this small sample; the overall gate follows the coordinator's rule. All per-wave and per-script-class results, original/masked/delta CIs, matching counts and source bindings are preserved in [validation.json](validation.json) and the ignored `test-out/import-verified/harm/REPORT.md`. The factory's report-only appearance/length audit is false; it produced all 596 requested rows with zero drops and matching references.

Linear extrapolation uses `mask wall * pages / 14 + harm wall * 10000 / 596`:

| Population assumption | Mask + import | 10k paired harm | Total expected wall |
|---|---:|---:|---:|
| Requested approximation: 680 pages | 0.47 h | 0.93 h | **1.4 h** |
| Verified population: 896 pages | 0.62 h | 0.93 h | **1.6 h** |

These are estimates from the 14-page test, not full-run measurements. Page/line widths, CPU contention and disk speed can change wall time. Each command independently enforces a 90-minute limit. The full external run was not executed.


The 25 unit tests cover the exact population and exclusions, parliament removal, output containment/default path, memory caps, disk floor, actual network/write denial, ignored test data, retired ambiguity policy, incomplete-run rejection, seeded sampling, paired intervals and page-cluster identity. Test receipts bind the exact source files. A source/evidence-bound `guarded_commit.py` stages eight explicitly enumerated nonignored code/report/catalogue files only; `--retry` revalidates the same manifest after a blocked Git operation. Ignored outputs and the unrelated `.venv` symlink are excluded.
