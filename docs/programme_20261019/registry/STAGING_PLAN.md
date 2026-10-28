# RUNNER4 — source inventory and staging plan after Astra review 1

22 October 2026. **STAGING PLAN READY; build remains on HOLD.** No source transfer, registry implementation/build, cluster job, or git metadata write. The owner has not authorized the proposed bulk transfer.

The exact missing selection is **35,198,780,622 bytes = 35.20 GB = 32.78 GiB**, **32,294 files**. Provisional remote reuse is **6,097,473,408 bytes / 10,329 files**. The complete physical selection totals **41,296,254,030 bytes / 42,623 files**, excluding the separately listed census/release/crops/parent inputs already on Clariden. These are physical file counts, not logical pages or Google boxes.

## Pinned selection and verification limits

Selected manifest: [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json), SHA256 **`f468812a38687cad4aa025290c207ea9148eac2068aa721f7809f933e78c6578`**; [checksum](SOURCE_MANIFEST.sha256). It pins every per-group file inventory, transfer list, remote receipt/probe, exact source root and representation contract. TSV inventories contain root-relative path, size, mtime, transfer/reuse action, stored hash when available, expected hash basis, and original response SHA separately. Inventory byte hashes are newly computed.

This is a **pinned selection, not a completed byte-verified source snapshot**. **18,514** selected files have no expected stored-object SHA yet; this includes legacy stripped responses and images lacking a supplied custody hash. Hashes from filenames/old receipts are marked unverified, and must be checked against bytes. No historical original response hash is relabeled as a stored-file hash. No bulk page/response hashing was done on the Mac. Small source/assignment records were hashed for the inventory (6,192 files, about 1.73 GB in aggregate), and a three-object legacy representation probe was read. Large census/parent hashes remain producer pins; only the bounded remote metadata/crop-manifest objects and sample page/crops were freshly hashed. The manifest explicitly records these limits.

Paths:

- `$W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3` on Clariden; live filesystem inspected on `clariden-ln004`.
- `$C=/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data` on Mac.
- `$H=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big` on Mac.
- `$M=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest` in this worktree (legacy metadata/assignments).
- `$D=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data` on Mac (moved raw row records).
- Proposed new source snapshot: **`/capstor/scratch/cscs/fffoivos/greek-ocr-data/line_registry/sources/runner4-20261022`**. Parent `/capstor/scratch/cscs/fffoivos` exists and is writable; no destination directory was created. The similarly named `/capstor/.../greek-ocr-e3` is a different, partial tree; sampled missing sources were absent there too.

## Exact physical inventory and transfer selection

| Source group | Selected files | Selected bytes | Transfer files | Transfer bytes |
| --- | ---: | ---: | ---: | ---: |
| legacy_assignments | 6,131 | 1,675,284,598 | 0 | 0 |
| legacy_composite_images | 18 | 3,360,892 | 18 | 3,360,892 |
| legacy_google_receipts | 13 | 8,965,337 | 13 | 8,965,337 |
| legacy_metadata | 61 | 51,151,088 | 1 | 111,356 |
| legacy_page_images | 8,574 | 22,244,548,982 | 8,574 | 22,244,548,982 |
| legacy_page_metadata | 7 | 3,294,563 | 7 | 3,294,563 |
| legacy_raw_responses | 13,099 | 6,577,672,285 | 13,099 | 6,577,672,285 |
| legacy_row_records | 8 | 767,867,104 | 0 | 0 |
| w_cache | 5,389 | 4,453,652,987 | 1,259 | 850,371,013 |
| w_page_records | 4,707 | 20,980,770 | 4,707 | 20,980,770 |
| w_raw_responses | 4,612 | 5,489,236,156 | 4,612 | 5,489,236,156 |
| w_state_receipts | 4 | 239,268 | 4 | 239,268 |

Each group links to `out/runner4/SOURCE_FILES_<group>.tsv` through the selected manifest. Rows with `REUSE_REMOTE_SIZE_MATCH_HASH_PENDING` are size matches, not freshly certified identical copies.

**Pages and raw Google boxes.** All 5,389 W cache objects are selected: 4,130 same-size resident objects are reused, and 1,259 missing objects (850,371,013 bytes) need transfer. W1/W2 page records (1,370 + 3,337), four state/receipt files, and all 4,612 W raw responses are absent at the expected remote paths and selected from `$C`. Legacy native images: 8,574 files, including rescue and prior page reads; 18 montage composites are recorded separately. Legacy raw-response inventory includes all retained JSON/compressed custody objects in the eight waves **plus page_reads_v1 and montage_v1** (13,099 objects / 6,577,672,285 bytes). It intentionally preserves coexisting storage representations instead of guessing which loose/archive object can be discarded. Transfer stored representations; decode/reconstruct only later on Clariden. These are objects, not unique API responses/boxes.

**Book/page/edition and precomputed row metadata.** The 6,131 assignment files include Round1 reads_d1/reads_rest and the other retained assignment trees; all are present remotely with matching sizes. They preserve page descriptors and parsed DocAI custody/line records. Of 61 other legacy metadata files, 60 have matching-size resident copies. The missing one is `$M/pilots_v2/lines_manifest.jsonl` (111,356 bytes). Seven additional page/wave descriptor/ledger files under `$H` are selected for transfer. All eight legacy raw row files at `$D/docs/harvest/<wave>/records*.jsonl` are present in `$W/greek-ocr-toolkit/docs/harvest/<wave>/`; together 767,867,104 bytes. Existing codec/class/script/length metadata remains in the pinned W feature snapshots, census metadata/exports and old records. Actual hashes for all reused bulk files still require readback.

**Census, release, splits and crop manifests — resident, no Mac transfer:**

| Physical Clariden file | Bytes | SHA256 | Basis |
| --- | ---: | --- | --- |
| `$W/collection_v2/import_real_v2_train.jsonl` | 144,079,429 | `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3` | producer pin; full readback pending |
| `$W/collection_v2/import_real_v2_dev.jsonl` | 9,314,684 | `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` | producer pin; full readback pending |
| `$W/collection_v2/import_real_v2_test.jsonl` | 33,589,759 | `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` | producer pin; full readback pending |
| `$W/filter_pipeline_20261018/inputs/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl` | 503,777,486 | `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c` | producer pin; full readback pending |
| `$W/filter_pipeline_20261018/inputs/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl` | 1,087,822,541 | `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4` | producer pin; full readback pending |
| `$W/filter_pipeline_20261018/prepared/87407ec7430a375f/metadata.json` | 124,410,793 | `dd2da6548a2dd6ed5624299be552e32204efb85220f4463590fb4c8e3ddd3bf5` | producer pin; full readback pending |
| `$W/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/admission_records.jsonl` | 11,267,047,584 | `a3daa187e9b215b49724411d982893dc4200ff0207d320bc7e63d20d74ec9d45` | producer pin; full readback pending |
| `$W/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/admitted_train.jsonl` | 8,506,810,372 | `f32bcd197caa468114005a4f8762fa2d530e8b4709928f74cef971fe83423f52` | producer pin; full readback pending |
| `$W/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/decisions.jsonl` | 11,014,509,459 | `9f00d46b11b4599fa5e4ff2e4d7c8f165f56eb6270b480e46e9fb5b0bd64e095` | producer pin; full readback pending |
| `$W/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/evaluation_diagnostics.jsonl` | 2,679,537,357 | `0490a9e1ef724970d29ee98264b7e5cf377cd1213eb2352a0ec8b781a562a7b8` | producer pin; full readback pending |
| `$W/release_v4/rel4_c06_full_01/release_v4_admission.jsonl` | 173,049,274 | `dcae2aebc239c2f22eb5bec6da01218958fb235388553730f3ece14dca6dfa75` | producer pin; full readback pending |
| `$W/release_v4/pkg/fde561ca/inputs/edition_map.jsonl` | 644,541 | `1cf086f3d4bb41a7159e1ac395915d38a839925bef56dcca7ac0400691a92854` | fresh bytes |
| `$W/release_v4/pkg/fde561ca/inputs/row_split.jsonl.gz` | 1,032,585 | `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82` | fresh bytes |
| `$W/crops4_attempts/crops4_c06_full_01/crops_manifest.jsonl` | 70,696,962 | `d72d247d7a3ccc51931e7f2df765219ce398907a021d1bcaa4f4eec44c5c224a` | fresh bytes |
| `$W/crops4_attempts/crops4_c06_full_01/crops_sha256.txt` | 30,960,336 | `3d08559df8634d751fdec0a5864d384a7af5030790c1afeb0d65c3962b1a8b8f` | fresh bytes |

The manifest contains the remaining output/receipt file sizes and hashes as well. Census CURRENT still pins completed generation **2**, export **`g2-e310b8ef84cc4763b036fd0abfc0295d`**, binding **`3e05d2f2b5b908f11e20010c7f85dc046920717590f82ba1520f7b0df92febe4`**. Its 592,466 observations reconcile by producer summary to 456,967 ADMIT / 84,754 HOLD / 50,745 DROP. The source parent files have 214,436 train / 13,522 dev / 44,029 test collection-v2 rows and 101,098 W1 / 219,381 W2 rows. Release v4 has 167,946 base rows and 904 separately registered sf7 overlays. Counts are the bound producer counts, corroborated by Astra's recent fresh release/manifest counts, not a new full 11 GB decision scan.

CROPS4C's 207,243 selected crop files / 3,595,018,320 bytes / 3,997 pages are bound by its live receipt and the freshly verified manifest/checksum-list hashes above. Crop locations are `$W/collection_w1_originals/<source>/<row_id>.png` and `$W/collection_w2_originals/...`; no new crops are needed for this selection. The separate collection-v2 crop root is `$W/collection_v2/crops/<wave>/...`; one reviewed crop freshly matches its row SHA. Its directory-wide file/byte total was **not** re-enumerated in this bounded probe, and CROPS4C does not certify it. Build preflight must reconcile those keyed crops and used-row coverage; it must not assume 207,243 describes every census crop. Mutable `ledger.sqlite` is 24,841,252,864 bytes, opened read-only for indexed samples only; it has no selected whole-file hash and is not a production snapshot input. Immutable generation exports provide production decisions/corrections.

**Pod backups.** Read-only checks against configured `PrimeIntellect` and `PrimeO5` failed respectively with authentication denial and connection reset. No pod backup was inventoried or selected; path, bytes, file count and hashes there are **unknown**. No instance was started or credentials changed. The plan depends on the verified Mac and Clariden locations only. See `out/runner4/POD_BACKUP_PROBE.json`.

## Three joins repeated entirely on Clariden

Evidence: `out/runner4/STAGING_JOINS.json` and full source probe `STAGING_REMOTE.json`. Each exact `(parent,id)` has one indexed observation and one decision, train/ADMIT, empty reasons.

| Parent / exact row | Resident geometry | Page / crop byte checks | Complete raw Google join |
| --- | --- | --- | --- |
| W1 / `bsb_poly1850--027215cc6d2a7e8a--s000-l0001` | line index 0; `[786,158,839,188]`; crop `[784,156,841,190]` | page SHA `3ef838b275c8633d0afa1c686fb516509e73758411f46eb93af4b7a872fd09c0`, 1592×2472; crop SHA `3c8c2a651868aad583ee4aad868604ba954e2496492db4c0ac7eb6e392c5b88e`, both match | **Blocked:** raw response and page record absent |
| W2 / `bsb_poly1850--91657e0569fe07c8--s014-l0001` | line index 0; `[171,78,227,110]`; crop `[169,76,229,112]` | page SHA `0059956e093e97b10213b2f17c4c29e3e916e3f247c56f1d2791172cfbac8f6d`, 1312×1976; crop SHA `fb0a303ea834c38c6681f6624d1db719026daf4bb84c333c38e6f97a8a2f5efd`, both match | **Blocked:** raw response and page record absent |
| collection-v2-train / `66112e132fd96ac8e30e5328-p000016-l0004` | remote `round1/records_all.jsonl`, line 516; DocAI index 3; `[693,151,1334,197]` | crop SHA `39cf1541e47312c720759883ac17b5385b5d708920f708e5618b94712cea1a2d` matches; page SHA `820e8b0f62cb34b73a46ede7be38f69ab2d0dc2adcf817572dc45868213713fb` recorded but raster absent | **Blocked:** page raster and raw response absent |

Result: **2/3 complete joins to retained harvest geometry and page pixels; 0/3 complete joins to raw Google geometry and page pixels.** The two W census crop paths are stale; resolve the actual files through CROPS4C custody roots, which match their hashes. Local raw-response/representation probes support the adapter but do not turn these into remote raw-Google passes.

Missing staging blocks raw polygon/text-anchor preservation for all three examples; it also blocks legacy pixel/dimension/position checks and segmentation of the missing full pages. Without it, global Google-box counts, every-used-row joins and later toolkit comparison denominators cannot be certified. The seven-page Vouli and four-entry Round1 discrepancies, cross-source aliases and any manifests pointing outside the named roots remain visible reconciliation work. This exact physical selection is not a claim of global logical completeness; newly discovered required sources need a manifest revision and an explicit additional transfer selection.

## Proposed transfer and SHA readback — documentation only

After the owner's explicit go for **35,198,780,622 bytes / 32,294 files**, including source/destination checksum reads:

1. Re-stat the selected file lists against pinned size/mtime and recheck resident target absence/presence. Freeze the selection and create a separate source-byte SHA256 manifest; fill currently blank hashes from the actual stored objects. For content-address/receipt pins require equality where they describe stored bytes. Keep historical original hashes separate. Hash scans of Mac bulk files are part of this future authorized operation, not something started here.
2. Create a private new snapshot directory at the proposed `/capstor` path; copy the pinned source manifest, file lists and byte checksums. Use each `TRANSFER_<root>.files` with the corresponding root; no directory-wide sync, deletion or source moves. The selected `TRANSFER_data.files` is empty because old row files are resident. Reuse resident files by root mapping and record verified hashes; no need to duplicate census/crops/W cache/assignments onto capstor.
3. Run the following **template once for each nonempty root list** (`collect`, `harvest`, `metadata`), substituting its exact absolute root and pinned list. The Mac's installed openrsync reports rsync 2.6.9 compatibility; the options below avoid newer flags. A small metadata-only readback is the only return transfer needed.

```sh
# PROPOSED ONLY — NOT EXECUTED
rsync -a --relative --partial-dir=.rsync-partial \
  --files-from=out/runner4/TRANSFER_collect.files \
  /Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/ \
  clariden:/capstor/scratch/cscs/fffoivos/greek-ocr-data/line_registry/sources/runner4-20261022/collect/
```

For `harvest`, use `$H/`, `TRANSFER_harvest.files`, destination `.../harvest/`; for `metadata`, use `$M/`, `TRANSFER_metadata.files`, destination `.../metadata/`. Files-from paths are root-relative and preserve their exact layouts. Lists contain no payload data. Keep a transfer log/elapsed/bytes receipt. Retry only selected partial/new objects; preserve conflicts for review. Do not use `--delete` or overwrite resident originals. Directory creation, manifest deployment and rsync are all pending owner authorization.

4. On Clariden, run `sha256sum` over the selected destination files in deterministic order; compare path/bytes/**stored** SHA to the source-byte manifest. Hash resident reused files against their expected pins, including immutable census/parent/release inputs; stream large reads in the later authorized verification allocation, not a large login-node workload. Reconstruct original response hashes only for supported representations. Read back the checksums/receipt, compare manifest SHA on the Mac, and seal a **new byte-verified** source manifest linked to this selection SHA. Never silently edit this pinned plan to imply verification occurred.
5. Repeat these same three joins entirely on Clariden using the staged page records/raw response/image objects, exact crops and transforms; preserve raw Google polygons, original/source hash checks and per-page results. Report all three passes or the exact remaining absence. Only after staging/coverage evidence and Astra/owner disposition is builder implementation unheld. This authorization would not itself authorize registry build, new segmenter inference or training.

## Transfer duration and storage

For 35,198,780,622 bytes, payload-only times are **58m40s at 10 MB/s**, **23m28s at 25 MB/s**, **11m44s at 50 MB/s**, **5m52s at 100 MB/s** (decimal MB). No transfer benchmark was run. With 32,294 small files, SSH/proxy latency, source/destination checksum passes and retries, plan **30–120 minutes** at a usable 10–50 MB/s; throughput below that can take longer. SHA passes read the transferred payload once at source and once at destination in addition to rsync I/O; resident readback is extra, dominated by the large census exports. Revise from the actual first transfer receipt; no measured ETA is claimed.

New staged payload needs **35.20 GB** on capstor; allow **45 GB** for partials, manifests and headroom. No duplicate allocation for 6.10 GB of reused selected sources, existing 3.60 GB CROPS4C or census/release inputs. The previously estimated later registry publication remains 1–4 GB, budget 10 GB; temporary join scratch should budget **20 GB** and project columns/locators rather than copying the 11 GB decision JSON wholesale. The later one-job 8-CPU/32-GiB, 30–90-minute build estimate is unchanged and unmeasured; transfer/checksum time is separate.

## Review disposition and stop

MEDIUM 2: distinct stored/original/reconstructed hashes plus a matching real reconstruction witness. MEDIUM 3: correct codec/NFD/name terminology, separate named Script-property detection, explicit mixed/tie language tag and null heuristic confidence. MEDIUM 4: actual `detector_record` JSON boundary, retained/clipped box population, exported item order, and `segmenter_page_results` including zero/error/not_run outcomes. These are design changes only.

HIGH 1 remains open: missing sources have not been staged; full byte custody and the three raw-Google remote joins are not passed. No production registry module or job wrapper was created. The owner can now review a concrete **35.20 GB** transfer selection; no transfer approval is inferred from this design task.

**STAGING PLAN READY — 35,198,780,622 bytes to transfer; 6,097,473,408 bytes selected for provisional remote reuse.**
