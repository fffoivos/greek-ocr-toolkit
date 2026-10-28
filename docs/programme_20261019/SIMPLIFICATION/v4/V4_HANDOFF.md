# Release v4 handoff — aspect A complete

Release on Clariden: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01`.

Receipt: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01/RELEASE_V4_RECEIPT.json`; SHA256 **`dbc99bdc7fd9c770e25880139ef3bd3184392bfe65e1eb2baf89544c8e390f32`**.

Bound release package **`fde561ca305425db4a5a8418300f07f61581f60bc04574d78101c6e1bea0c80a`** (`fde561ca`), source sol-recut **`b083574d4e71ddaf771f2152d6ee19741526fc6d`**. Release job **3713178 COMPLETED 0:0, 00:15:37**; handoff job **3713294 COMPLETED 0:0, 00:02:46**. The existing handoff printer ran once in that allocation; it verified the paths/hashes below. No submission is pending for RUNNER1.

Census bound ID **`31316332c860d411`**, final generation **2**, export **`g2-e310b8ef84cc4763b036fd0abfc0295d`**, pipeline **0.3.3**. Final authoritative readout: **592,466 rows, complete=true, INFRA_ERROR=0, UNPROCESSED=0, all 16 invariants PASS**. [Readout path/hash and invariants](SIMPLIFIED/FINAL_READOUT/RESULT.md).

## Rows available to wave-2 inputs

| Input scope | Rows |
| --- | ---: |
| Census collection-v2-train ADMIT | 196,234 |
| W1 raw-label release train | 50,622 |
| W2 raw-label release train | 117,324 |
| W1 + W2 raw-label release train | 167,946 |
| All three train parents in census admitted_train | 364,180 |
| W1/W2 held-out diagnostics (excluded from release) | 39,297 |
| W1/W2 sf7 applied edits in separate overlay | 904 |

| Wave-2 arm | Available census-selected old rows | Available v4 new rows | Available real source rows before factory/codec intersection | Labels |
| --- | ---: | ---: | ---: | --- |
| ctrl | 196,234 | 0 | 196,234 | Existing factory labels; select by census train ADMIT |
| add | 196,234 | 167,946 | 364,180 | Same selected control pool + v4 immutable raw `label` |
| add_corr | 196,234 | 167,946 | 364,180 | Same membership as add; registered corrections applied by exact ID downstream |

These are **source-input availability counts**, not prepared factory inventories, training draws or post-codec counts. The existing wave-2 driver intersects the factory pool with census train ADMIT, encodes the new rows and records codec rejections. RUNNER2's one CPU preparation allocation must report actual ctrl/add/add_corr row counts and correction substitutions; those artifacts do not yet exist in this handoff. The 904 sf7 edits count covers the W1/W2 release only and must not be reported as the total number of all-arm corrections.

The base release preserves raw labels; use **`raw_label_field=label`**. The registry's sf7 entry is **version `0.7`**, tool digest `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5`, mode `external_registered_not_applied`, `applied_to_release=false`, key `(parent_id,row_id)`. It points to the W1/W2 sf7 edits export and all five normalized parent ledgers. The separate overlay uses `parent_text`/`text` with mandatory provenance. Keep `kept_unverified` raw labels unchanged; 44,495 W1/W2 release rows have that status. Register RU1/N1/sf7 through the existing downstream mechanism; do not treat census final_text as the raw admission target.

## Printer-verified paths and SHA256

The machine-readable authoritative arguments are [HANDOFF_ARGUMENTS.json](SIMPLIFIED/RELEASE_HANDOFF/HANDOFF_ARGUMENTS.json). They were fully hashed in-job, including the large census JSONL files. The receipt's own SHA is shown above.

- **census06_CURRENT.json**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/attempts/full-split-002/CURRENT.json`

  SHA256: `6da9b78e03269f125ac1af018412445416108168fc0188bce480ad8556cd0d2c`

- **census06_admission_records**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/admission_records.jsonl`

  SHA256: `a3daa187e9b215b49724411d982893dc4200ff0207d320bc7e63d20d74ec9d45`

- **census06_admitted_train**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/admitted_train.jsonl`

  SHA256: `f32bcd197caa468114005a4f8762fa2d530e8b4709928f74cef971fe83423f52`

- **census06_summary.json**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/summary.json`

  SHA256: `f12d31f10cc2282942492e85f40625bdc3da11e6ace1507a3b8b92e516ce33d2`

- **corrections_registry.json**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01/corrections_registry.json`

  SHA256: `36d7d9957edfffb5743aef5f367936442d45b7f5e6dde4311698f3d4838d1756`

- **release_v4_admission.jsonl**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01/release_v4_admission.jsonl`

  SHA256: `dcae2aebc239c2f22eb5bec6da01218958fb235388553730f3ece14dca6dfa75`

- **release_v4_sf7_edits.jsonl**

  Path: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01/release_v4_sf7_edits.jsonl`

  SHA256: `823f9e20064feb1c2bb6f22bfc60ef4e02d4dfea26b6b742beb9292792e22538`

## Release acceptance evidence

CROPS4C smoke **500/500 byte-exact**; full **207,243/207,243**, all skipped-valid, including held-out diagnostics. Full receipt `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_attempts/crops4_c06_full_01/upload_receipt.json`, SHA256 `dbead984d9425dc3181efae0d00e5448e6334227b6d366e160d8a619bb9f7148`. Release `missing_crop_new_admits=0` in both parents and total; no missing-exact-crop exclusions. Original crop roots are `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_w1_originals` and `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_w2_originals`; use each admission's recorded crop_relative_path relative to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3` and exact crop_sha256.

Release flips versus v3: **0 added / 691 removed**, all ELSTAT polytonic holds (W1 114, W2 577). Benchmark key/pixel and dev/test edition exclusions each 0; existing seal04/edition protections remain bound. Non-sf7 edits output is empty. All five output sizes/hashes, count reconciliation, exclusions, protection pins and ten referenced native-crop examples are in [RELEASE_CHECK.md](RELEASE_CHECK.md).

The ten-example check records residual raw OCR error and crop-edge fragments, without changing release membership or labels. It is not an exhaustive accuracy claim. Aspect B retains its assigned v4 acceptance review, exposure recount, smoke and production launch gates.
