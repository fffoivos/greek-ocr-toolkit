# SCALE1 — implemented package and coordinator handoff

20 October 2026. The lead resolved the prior cap ambiguity: edition cap = none, series cap = none; supply means all raw class rows. The earlier scratch cap witness was removed and replaced by an acceptance test selecting all 160 rows of one edition/series. No production job, allocation, spend, staging or commit was performed.

Implementation and complete rules are in README.md. The unchanged classifier copy binds HEAD e6365239b4d087404a7a8a1c20609a0ea1ec2dad and SHA aa950a88f02b083ce4ffb0739c70183000048b9167f7ca8bf99f50ba9d1faff1. Quotas are extracted from the unchanged counts.json copy, without retyping. Reference and targeted RNG seeds, exact rational redistribution, largest-remainder rounding, class order, cap-free rotation and emission order are documented in README and recorded by Job 2 in subsets_plan.json. Unique rows have no training draw caps or repeats.

The release's full bound SHA, read from its live receipt, is `92770112efe63669eb079384da0b2e4754901fff0b14fdcc97208207533e37b9`. Its receipt SHA is `d711836c0a8af471fce06c7c522419b93bb14f52332d806c9df11ebe25aec600`. Census g1-6283e1bcdf124516b599f8028ad910be admitted_train is 7,870,677,512 bytes, SHA `fe955d00af930b90b1d963a0454a4f4cba26de8fd24332ecc6873fd99f42c4f3`; summary SHA `096b18a885f1d6bdced71a9f42e0eeee3cc2b8f61d0ce0eacb26abacbe1402be`. `inputs.json` binds all 11 input paths, sizes and hashes. Large hashes are receipt-derived until the jobs recompute them. Small inputs are rehashed during deployed preflight. Bounded first/last census samples confirmed the decision/final_text/crop fields and nullable v_c crop_bbox. Full-data schema and exposure audits remain job work.

Expected before execution: W1/W2 release 168,637; v_c 196,234; union 364,871; reference output sizes 208,000 and 364,871; targeted output size 208,000. All exposure counts must be zero. Reference nesting must pass. Target class supply, redistribution amounts, availability, source/parent mix at 208k and unclassified-fill count remain unknown until the jobs run. The full-universe point is **"actual maximum; targeted = reference at full universe"**. No 420k subset exists.

## Exact coordinator commands on Clariden

The commands below are for the coordinator to run. The author has not executed either submit script. Use a new attempt name if rerunning; existing output directories fail closed. The same attempt name may be used once for each job, under their distinct tags/subsets roots.

```bash
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/b23cfcc1/VERIFY.sh package
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/b23cfcc1/VERIFY.sh inputs-tags
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/b23cfcc1/submit_tags.sh scale1-c05-002
```

Subsets follow-up, only after the tags job succeeds:

```bash
PKG='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/b23cfcc1'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
TAGS_RECEIPT="$W/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json"
"$W/venv_l1/bin/python" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="ok"; print(d["output"])' "$TAGS_RECEIPT"
TAGS_RECEIPT_SHA=$(sha256sum "$TAGS_RECEIPT" | cut -d ' ' -f 1)
"$PKG/VERIFY.sh" package
"$PKG/VERIFY.sh" inputs-subsets "$TAGS_RECEIPT" "$TAGS_RECEIPT_SHA"
"$PKG/submit_subsets.sh" scale1-c05-002 "$TAGS_RECEIPT" "$TAGS_RECEIPT_SHA"
```

For a pre-tag inspection, `"$PKG/VERIFY.sh" inputs-subsets` checks static inputs and reports tags pending. It does not authorize submission. The subset submit requires the absolute tags receipt path and its 64-digit SHA; no default or unpinned handoff is allowed. Submits create only the parent log directory before sbatch. Both jobs use absolute package/input/output paths and `$W/venv_l1/bin/python`, normal partition, account a0140, one CPU and one task. Output directories are created exclusively by the jobs; successful receipts are written last. Partial failed attempts remain distinguishable by absent status-ok receipts.

## Sbatch sizing arithmetic

`SYNTHETIC_THROUGHPUT.json` records a bounded local 1,000-row synthetic classifier/parser run. Rows contain 250 samples in each of four physical curves and real decision/evidence structure; no production rows were transformed locally. Measured input-equivalent throughput: 110.76 MB/s (15,532 bytes/row, 0.14023 seconds for 1,000 rows); SHA throughput 2,368.81 MB/s. This is a sizing proxy, not a measured Clariden ETA.

Tags: 7,870.68 MB / 110.76 MB/s = 71.06 seconds per parse/classify pass; two streamed passes = 142.12 seconds. One full input hash costs 3.32 seconds at the synthetic local hash rate. Allow 12× on this combined 145.44 seconds for cluster/shape variation, plus 600 seconds for gzip, sorting, metadata and shared-storage overhead: approximately 2,346 seconds. Request **01:00:00, 8 GiB, 1 CPU**. Memory is compact source/confidence/key populations, a key set and flagged set; the 7.87 GB file is never held in memory.

Subsets: one census pass and full hash plus release, tags and metadata joins; conservatively reserve 1,200 seconds. Every subset rehashes every crop: 208,000 + 364,871 + 208,000 = **780,871** crop opens. At an assumed 10 ms/open-and-hash this is 7,808.71 seconds. Add 3,600 seconds storage variation margin: total 12,608.71 seconds < 14,400 seconds. Request **04:00:00, 16 GiB, 1 CPU**. The crop latency assumption is unmeasured; slow shared storage can exceed it, so this is a resource bound rather than an ETA promise. Tags, joined slim universe, split key sets, class queues and permutations are retained, not full census decisions or crop bytes. A longer retry, if needed, remains coordinator-controlled.

## Original SCALE1 validation and deployment (historical)

Acceptance: 20 synthetic tests, including both jobs' complete handoff/output path, prefix nesting, reordered-input determinism, short-class and iterative redistribution, unclassified reference-order fill, rounding, uncapped edition/series selection, source/edition rotation, relative confidence/missing evidence, exact v_c UTF-8 label preservation, every exposure failure, missing and corrupt crops, and receipt SHA rejection. Run locally with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_scale` from this package directory. No production benchmark or full crop audit has run.

Deployment root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/d14521ee`. The sha8 is SHA-256 of the lexicographically ordered core-file SHA manifest (scale.py, benchmark.py, test_scale.py, inputs.json and vendor files), first eight digits. This identifies executable/data semantics; DEPLOY_SHA256SUMS binds every deployed payload including rendered absolute-path launchers and documentation. DEPLOY_PATHS.txt and DEPLOY_SHA256SUMS enumerate the package; all hashes, including these two manifests, are compared on readback. The manifests intentionally do not hash themselves recursively.

Remote deployment verification is recorded in DEPLOY_READBACK.json (local evidence only, outside the deployed manifest). It contains every remote SHA, package verification output, static inputs-tags checks and the subsets-pending status. No `sbatch`, git add or git commit was run.

## SCALE1B — decision admission and real-row regression

Job 3705047 failed after 13 seconds because `census_row` treated the collector's legacy `row.admitted` as census admission. The sole production-code change removes that condition, retaining `decision.admitted is True` and `decision.disposition == 'ADMIT'`. All other guards and classifier code remain unchanged. The real head witness at zero-based index 20 (21st physical line) is `bsb_poly1850--027215cc6d2a7e8a--s000-l0025`: collector admitted False, rejection reasons `['short_line']`, census decision admitted True / ADMIT. It now passes. There were no further real-row assumption failures or production-code fixes.

Subset audit: `build_job` validates v_c rows through the same corrected `census_row`; W1/W2 enter from the bound REL3 release and labels. `vc_row` takes `final_text` checked against decision text. No separate collector admission/rejection/usable flag determines subset admission. The full synthetic two-job handoff now deliberately supplies legacy rejected rows to exercise this route. Vendor `slim` derives its admitted field from the decision; unrelated vendor CLI census scans are not called by either SCALE1 job. Vendor bytes are unchanged.

### Real sample and regression tests

Read-only bounded sampling from `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/attempts/full-split-001/current/admitted_train.jsonl` (7,870,677,512 bytes), using `$W/venv_l1/bin/python` over `ssh clariden`. Head: 1,000 W1 rows at byte 0; middle: 1,000 v_c rows at byte 3,935,343,098 after dropping a partial line; tail: last 1,000 complete v_c rows at byte 7,850,309,374. W2 was absent, so six single-row byte probes located it and an extra 1,000 complete W2 rows were read at byte 1,475,764,648. Tail reading was bounded to 32 MiB. No full-file scan or hash ran on the login node.

The fetched 4,000-row copy stays outside git at `/private/tmp/scale1b/real_rows.jsonl`, SHA `b457042a9502c3c0d065e7264d6096238d4847800b29fa1baec90b937bede83f`. The actual `tag_job` ran locally on it, including both passes, `census_row` → `slim` → classifier → complete gzip tag records and receipt. Only the input binding and expected v_c count were overridden for this bounded test. All 4,000 unique rows passed with no exceptions: **W1 1,000; W2 1,000; v_c 2,000**. Legacy collector admitted=False counts were W1 27, W2 262, v_c 0. Relative degraded flags use the sample's per-source population; these are sample results, not full-production class counts or confidence percentiles.

`REAL_SAMPLE_RESULTS.json` records every per-parent primary class and availability field, sampling offsets, source/sample identity, legacy witness and test path. The committed-candidate excerpt `fixtures/real_admitted_train.jsonl` contains 20 unmodified real rows per parent (60 total), including label text and this witness. Its full tag-writer regression, explicit legacy-false acceptance, and decision-rejection checks join the prior suite: **23 tests passed**. The excerpt is prepared for commit; nothing was staged or committed.

| Primary class | W1 | W2 | v_c |
|---|---:|---:|---:|
| caps_headings | 6 | 0 | 0 |
| curved_skewed | 13 | 171 | 90 |
| degraded | 54 | 33 | 0 |
| font_extremes | 4 | 187 | 670 |
| greek_latin | 56 | 0 | 1 |
| latin | 52 | 84 | 0 |
| leaders_dashes | 221 | 23 | 225 |
| long | 99 | 0 | 106 |
| monotonic | 0 | 0 | 2 |
| numeric_cells | 15 | 221 | 0 |
| poly_dictionary_journal | 439 | 56 | 0 |
| polytonic | 40 | 1 | 906 |
| short | 1 | 1 | 0 |
| unclassified | 0 | 42 | 0 |
| vertical_turned | 0 | 181 | 0 |

| Field (available / unavailable) | W1 | W2 | v_c |
|---|---:|---:|---:|
| census.crop_bbox | 1000 / 0 | 1000 / 0 | 0 / 2000 |
| evidence.A | 1000 / 0 | 1000 / 0 | 0 / 2000 |
| evidence.cell_flag | 1000 / 0 | 1000 / 0 | 0 / 2000 |
| tags.cell_flag | 1000 / 0 | 1000 / 0 | 0 / 2000 |
| tags.short | 945 / 55 | 81 / 919 | 0 / 2000 |
| tags.font_extremes | 1000 / 0 | 1000 / 0 | 2000 / 0 |
| evidence.confidence | 1000 / 0 | 1000 / 0 | 0 / 2000 |
| evidence.ink_density | 0 / 1000 | 0 / 1000 | 0 / 2000 |

For v_c, all 2,000 bbox/aspect/cell evidence values and `cell_flag`/`short` tags are unavailable as expected; segmentation font evidence is available. Missing evidence remains explicit. Complete field counts are in the JSON report.

### New package and coordinator handoff

New deployment root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/b23cfcc1`. The old `d14521ee` package is retained untouched. SHA8 uses the prior sorted core manifest convention, adding `fixtures/real_admitted_train.jsonl` to the original six core files; `DEPLOY_SHA256SUMS` binds all payload files, including the sample report. `DEPLOY_PATHS.txt` enumerates payload plus both manifests. Every remote SHA, including both manifest SHAs, is read back and compared with local bytes; verification evidence is in local-only `DEPLOY_READBACK.json`.

Remote checks: `VERIFY.sh package` and `VERIFY.sh inputs-tags` (3/3) pass. Large input preflight checks existence and byte size; full input hashes remain job work. All 23 package tests also pass from the deployed package under `$W/venv_l1/bin/python`. The read-only attempt check found `$W/scaling_w3/tags/scale1-c05-001` exists, so the exact three-line coordinator block above and subsets follow-up use **scale1-c05-002**. Neither submit script was executed. No data, attempts or old packages were deleted; no jobs, allocations or spend were requested.

## SCALE1C — CROPS4 original crop resolution and completed tags reuse

Job 3705085 failed because W1/W2 tag metadata retained census paths into the removed 18 October filter-pipeline input tree. `resolve_crop(census, release)` now takes W1/W2 paths from the bound REL3 row's `crop_relative_path` under `$W`, with `crop_sha256` from that release row. It checks the same parent/row key, source, edition, and equality to census `decision.binding.crop_sha256`; absolute/traversing/incorrect-original paths and resolving to the census path fail closed. W1 uses `collection_w1_originals/<source>/<row_id>.png`; W2 uses `collection_w2_originals/<source>/<row_id>.png`. v_c keeps census `crop_path` and SHA.

Changed production sites and complete crop-use audit:

- `build_job` release join: retain compact release path/SHA bindings; the census pass validates every matching W1/W2 decision, resolves its crop and replaces the inherited tag path/SHA in the universe. Missing or duplicate census bindings fail. Labels still come from REL3; all existing release/tag checks remain.
- `vc_row`: calls the same resolver after its existing census/tag equality checks, preserving census paths and exact labels.
- `exposure` crop open/re-hash and `build_job` subset JSONL writer: both consume the corrected universe `crop_path`/`crop_sha256`; neither inherits the stale W1/W2 tag path. Their code and every-crop SHA checks remain unchanged.
- `census_row`: its absolute-path/schema and decision SHA checks remain unchanged; it never opens a crop. `tag_job` availability counting and emitted `crop_path` metadata remain byte-identical to the successful producer. Those metadata are not used as W1/W2 crop locations after the subset join.
- `vendor/bench02_draw.py` candidate metadata helper (`crop_source_image`, `crop_bbox`): unused by SCALE1 tags/subsets; unchanged. No other production `crop`/`crop_path`/`crop_source_image` location consumer was found. `benchmark.py` uses a synthetic v_c path; fixture/test paths are provenance and regression inputs.
- `tags_binding`: retain the current-wrapper SHA check, and additionally accept only the exact successful producer wrapper `3de88fc645d2b165191094ec5244bf56d5ee7286189218f40b2383cd33f3adea` when the byte-source fingerprint of all 11 tag functions/helpers matches `a962ebfd13d812366f90a1e6329af01bd28e44655e6b67e3080fb70b0df2ff64`. Receipt SHA, status, classifier SHA, exact input bindings, output location/size, and full output hashing in the subsets job remain enforced. A changed tag path is rejected by regression test.

### Real crop evidence and tag reuse

Read-only Clariden probe, before any subsets execution: **W1 20/20, W2 20/20, v_c 20/20 byte-exact**. All 60 files were opened and SHA-256 hashed through this package's `resolve_crop`. W1/W2 rows were fetched unmodified from the bound REL3 release file for the 40 keys in the existing real census fixture; v_c uses the 20 census admitted_train rows. `fixtures/real_release.jsonl` preserves those release rows. `REAL_CROP_RESULTS.json` records every resolved path, expected/actual SHA, fixture SHA and tag-reuse evidence. `check_real_crops.py` repeats the read-only probe from the deployed package. This is a bounded acceptance check, not the full production exposure audit.

Live tags receipt: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json`; status **ok**, rows **364871**, full SHA **e4a155ebf5a2b13e28b5b3a45f3244bc0d2612e1704b00df3b24362a03335d39**. Its wrapper SHA matches the live `b23cfcc1/scale.py` byte-for-byte. `tag_job`, `census_row`, `relative_flags`, `inputs`, `classifier`, `key`, `rows`, `dump`, `info`, `sha`, and `require` compare byte-for-byte with that live producer. The classifier (SHA `aa950a88f02b083ce4ffb0739c70183000048b9167f7ca8bf99f50ba9d1faff1`), counts, input manifest, VC constant and pre-existing imports remain unchanged; the only added import is standard-library `ast` for the compatibility fingerprint. Launchers change only the absolute package root. Tag output metadata remains as produced, and no tags regeneration is needed.

### Deployment and coordinator handoff

New package root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90`. The sorted core manifest convention now includes `check_real_crops.py` and `fixtures/real_release.jsonl` alongside the seven prior core files. `DEPLOY_SHA256SUMS` binds all payloads; `DEPLOY_PATHS.txt` enumerates payloads plus both manifests. Readback covers every SHA including both manifests. `DEPLOY_READBACK.json` is local-only evidence. Both old roots `d14521ee` and `b23cfcc1` are retained, with their complete file hashes checked before/after. All **27 tests pass** locally and remotely. Remote `VERIFY.sh package` and `VERIFY.sh inputs-subsets` with the pinned receipt pass; large input and tags-output full hashes remain enforced by the job, as before.

Read-only check found `$W/scaling_w3/subsets/scale1-c05-003` absent. Exact two-line coordinator block (prepared only; the submit line was not executed):

```bash
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90/VERIFY.sh inputs-subsets /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json e4a155ebf5a2b13e28b5b3a45f3244bc0d2612e1704b00df3b24362a03335d39
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90/submit_subsets.sh scale1-c05-003 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json e4a155ebf5a2b13e28b5b3a45f3244bc0d2612e1704b00df3b24362a03335d39
```

No jobs, allocations, spend, git staging or commits. `seal02/` was not touched. See `GUARDED_COMMIT_LIST.md` for exact review scope.
