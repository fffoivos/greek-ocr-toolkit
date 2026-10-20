# CENSUS05-C review inputs

Current package **997b7d2ab5a8775b**, bundle `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05`, 167 files. Manifest SHA256 `997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb`.

Changes since the Astra review:

- H1: `readout/census_readout.py` mirrors packaged `line_pipeline_census.py:167–171`; configured crops union observed dev/test crops, plus existing protected editions. `test_astra_config_only_crop` reproduces the one-row witness: leaks 1, exit 1; without configuration: leaks 0, exit 0.
- L1: `admitted_train_equals_eligible` mirrors packaged `line_pipeline_census.py:204–214`, using inventory train split and ADMIT decisions, exact row content hashes and unique identities. The subset invariant stays. `test_astra_missing_export` (three eligible decisions, empty export) fails with exit 1. `test_export_equality` also covers duplicates and changed row contents.
- M2: `readout/test_census_readout.py` finds its own repository root, skips absent historical fixtures with their paths in the reason, and writes all outputs and receipts to `tmp_path`. Synthetic successful exports now contain every eligible row. Tests: **28 passed in 31.23s** (0 failed, 0 skipped); packaged regression: **360 passed, 9 skipped in 3.11s** (0 failed). Logs in `c_evidence/`.
- M3: `INPUTS.json`, this handoff and `REVIEW_INPUTS.md` record durable archive custody; `c_evidence/archives.json` verifies **35/35** hashes against the original receipt and data-root checksum list.

`readout_fix.patch` targets `docs/records/harvest/census05/readout/` and supersedes `readout_version.patch`: it includes both the prior pipeline-version fix and these changes (including the prior wrapper change). No pipeline source changes. The 154 CODE_SHA-identical files and PROJECTS_SHA256 are byte-identical; DEPLOY_PATHS.txt was regenerated with identical bytes. The deployed payload changes only `readout/census_readout.py`; tests change locally but were never part of the deploy manifest. Updated manifests are DEPLOY_SHA256SUMS, additive_files.json and package_id.json.

Archive custody: gitignored; durable copy at the data root, receipt `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archive_receipt.json`, checksums `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/ARCHIVES_SHA256SUMS`, archives `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archives/`.

| File | SHA256 |
|---|---|
| `DEPLOY_SHA256SUMS` | `997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb` |
| `PROJECTS_SHA256` | `4864a067da0a597ea410d5bcb8346ec6736fb6f689beddff7f8d92da53c333e6` |
| `package_id.json` | `e01916f633e607f04f25c97ee343c5d210338562a156fb7dada38a7f7eda5467` |
| `INPUTS.json` | `15e5f79e02dcca02e0e1a0cdb07e0ae79e6570bc09fa7b20737120aaa2681720` |
| `readout/census_readout.py` | `f6af78899571c46ef8fe4b92d49f5e4bc072f1de25a4a51bdd3bb1e15ca4b944` |
| `readout/test_census_readout.py` | `b527942e6bdbe509088a58ee0e97ce477dec309c4e93a2b9c0b978d879bf23ab` |
| `readout_fix.patch` | `2e8f1d7571fa02d8768647530dbad242d233ef6025c8e45ece2c81ee80268677` |
| `c_evidence/readback.json` | `7109715b171c819ba42b840b6cb4fa794a9afb575973ce9dbda2f7113498f79c` |
| `c_evidence/archives.json` | `5f93ff6ab537660b72d0c3456dc0c3f67bab1b18fc07c5078e1e74a01b6e8b1b` |
| `c_evidence/witnesses.json` | `919bde41189e5e1e35bb784a891dd515beaa2ad30e7540ab67c0a085216a24ae` |
| `c_evidence/readout_tests.log` | `51f5986dd4da96907a07a7f5fa41ffb049524851ee2fdc2495b20a84081afe44` |
| `c_evidence/regression_tests.log` | `c283a24f24e1df7f8b33f0e9b39a42454c5063d13041d908fe953388e3572f29` |
| `c_evidence/package_comparison.json` | `6b92421ebf629677dd30f0f08e7b2029e985a72f5f550cf65435dd1a8886d6f4` |

Current verifier receipts: `d_evidence/verify-{regression,parity,census,readout}.json` and matching `.log` files; all four are VERIFY_OK after the lead commit (hashes below). Scheduler dry-check receipts remain `c_evidence/test_only.json`. No submission.

# Historical B review inputs (superseded by C below)

Bundle root `docs/harvest/census05` → `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05`; package **17b0eb1ca7fe81a7**, 167 files. Root identity is SHA256 of DEPLOY_SHA256SUMS, `17b0eb1ca7fe81a789c70c596d80d8ed69e4ea1597a227656f7f873f3f95ddf6`; PROJECTS_SHA256 binds 154 source paths. “Local only” means evidence was not copied to Clariden. All paths below are repository-relative; hashes cover file bytes.

| Repository path | Remote path where deployed | SHA256 |
|---|---|---|
| `docs/harvest/census05/DEPLOY_SHA256SUMS` | `local only` | `17b0eb1ca7fe81a789c70c596d80d8ed69e4ea1597a227656f7f873f3f95ddf6` |
| `docs/harvest/census05/PROJECTS_SHA256` | `local only` | `4864a067da0a597ea410d5bcb8346ec6736fb6f689beddff7f8d92da53c333e6` |
| `docs/harvest/census05/package_id.json` | `local only` | `b637372a8574b438c516fb0b32ee9500aa23ab47489a0ac19d4c5633f5332334` |
| `docs/harvest/census05/verify-regression.json` | `local only` | `065ed1de7d4ed46d90fa5ca6d4fb90710a859ec3f408eabd5271b5037d24b001` |
| `docs/harvest/census05/verify-parity.json` | `local only` | `227939d96ee4dce6a9516342b486868ae9c33bf8e2af8d90b3e1539174b9a051` |
| `docs/harvest/census05/verify-census.json` | `local only` | `43756045748926fad783d0f6f885c3ddfd88c2be486e9d6861982fa9afd72951` |
| `docs/harvest/census05/verify-readout.json` | `local only` | `bfbfb6a2eb2142a7e3c8a7dc085de94779b7c1438ae9ae88cc5384bc1b281539` |
| `docs/harvest/census05/b_evidence/readback.json` | `local only` | `19087e39b0b65c298e080178cf10f47b985e75785f5cb8bbee644a4c6ed0044b` |
| `docs/harvest/census05/regression_tests.log` | `local only` | `84596a06ecd46003ade1b2567c4de63f7cfdbae3b391aa998de488986df833a9` |
| `docs/harvest/census05/readout_version_tests.log` | `local only` | `6497b72269789ad7719127bb18fd1492c6376da0034420c1e15daff63c6c2079` |
| `docs/harvest/census05/parity/source_receipt.json` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/parity/source_receipt.json` | `ec5cc8bdda44cb7b38774ece13bb3e9dd4ace42abe16213a20b673b7662dfa8c` |
| `docs/harvest/census05/parity/replay-01.jsonl.gz` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/parity/replay-01.jsonl.gz` | `faff42574b7993048c4c5c2fc4c6b4ba78003bcbe51cd971135923a64ed3acbc` |
| `docs/harvest/census05/parity/replay-02.jsonl.gz` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/parity/replay-02.jsonl.gz` | `78c25acd769ca15e38cb8eb6265a5dcb337ebea02b2534e2fb4c79f392fb6b86` |
| `docs/harvest/census05/native_parity_audit.json` | `local only` | `12d4e8bb4ab8c3bd358b0dc93c7004ebf2ed1bc5949de11da4ee15a70c63d7d9` |
| `docs/harvest/census05/parity_policy_audit.json` | `local only` | `e5882fc7b028eb9252a9448583c6f4701cba4409acb2043ffe6a7073422107b5` |
| `docs/harvest/census05/b_evidence/test_only.json` | `local only` | `6fe4c3304ed77bf9f883bec98df054a95315f6221f21648943f30878897489da` |
| `docs/harvest/census05/census05_config.json` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/census05_config.json` | `8da7ccdfa88bd16eed288ca7fcf56dc23b6b3ec5a6ba1c6274db367f023ab597` |
| `docs/harvest/census05/config_diff.json` | `local only` | `f766d224d9855e8c8eed3c882e4bdaa2949ca1be6cd869095d456816b7d9fc85` |
| `docs/harvest/census05/config_diff.patch` | `local only` | `3cb56b6508c9dd69a2faba91bd324556e51b19d7abd8737838ed4cf171a640ef` |
| `docs/harvest/census05/corrections/report.json` | `local only` | `870cf65117bb939f5ca8853c639bd0fdf141e0424cc1ee1dcd1f81f482509275` |
| `docs/harvest/census05/INPUTS.json` | `local only` | `7ee332f8982e09f99b34092d1002d1fdeda05a5b38951d2c0833ee67e21857d2` |
| `docs/harvest/census05/input_audit.json` | `local only` | `3a621159ac94bbe4039f1ff633e01e306c4e2e3a7d49e74a77969735e033d88b` |
| `docs/harvest/census05/readout/census_readout.py` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/readout/census_readout.py` | `749d9d1bf6eff04cabf5ddd4f2f7c36e8769d8ab06c4e9128e8e474fad1c56ba` |
| `docs/harvest/census05/jobs/readout.sbatch` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/jobs/readout.sbatch` | `bad70c7235933c48faa2ce4e846c018a5e25a14871e9bb3c46e8c38a8deb092e` |
| `docs/harvest/census05/readout/readout.sbatch` | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/readout/readout.sbatch` | `cb39a8c96e995a386f6f22b096b1bd3400d387628b29c532dc790d1bfce301fd` |
| `docs/harvest/census05/mocks/smoke-mode-i/readout.json` | `local only` | `b84e0542d4fbf91483267987ebca84db538dbd680004242e99ee734163811fd0` |
| `docs/harvest/census05/mocks/smoke-mode-ii/readout.json` | `local only` | `35bcfdc16b425abe48212538a836ffd0ba0003c0b31a0ba939292c109f23d13a` |
| `docs/harvest/census05/mocks/full-mode-ii/readout.json` | `local only` | `94863994cacb86aaf6318a7885d2310fb80f6fbb3f12e2423ab8bdca8a84440d` |
| `docs/harvest/census05/b_evidence/baseline-mock-readout/readout.json` | `local only` | `87be1ceba6022e4bc8afe758451a1c2cb12f60f38630c187758283860a11e6e8` |

Cited package test logs report 360 passed / 0 failed / 9 skipped plus 20 readout tests passed (380 distinct passes). Cited parity results record 150/150 and 888/888 exact verdict and reason; no new native parity run is claimed. Cited mocks contain 200 rows and 14/14 invariants PASS. `test_only.json` contains the four smoke and four full responses, exit 0; these are scheduler dry checks. Config diff/report identify `routes_out_of_scope: ["polytonic"]`, four unbound polytonic ledgers, five regenerated N1 ledgers with empty changed-record/status-moving lists, and split2 binding in INPUTS/input audit and submit environment. Deployed input identities and five standing cyrillic identities are in readback.json.

Code identity: check bundle/manifest, PROJECTS_SHA256, four VERIFY_OK receipts and per-file remote readback.
Config: check the census_04 diff, route scope, component roots and unbound polytonic ledgers.
Corrections: check five regenerated N1 ledgers, moving-status lists and five standing cyrillic hashes.
Split: check split2 SHA256, 320479 assignments and explicit full submit-time binding.
Job settings: check dry responses, debug 00:10:00, normal per-kind limits, afterok chain and sibling readout paths before submission.

C verifier result (CENSUS05-D): **4/4 VERIFY_OK** against committed HEAD `76a6510d4eb2ad4d67b09f881bd81c2630e4ad77`. The unchanged verifier ran all four kinds with the arguments from `c_evidence/verify.py`, changing only `--out` to the external scratch directory; logs were also external. All four finished before receipts and logs were copied into `d_evidence/`. No bypass, deployment, submission or .git writes. Per-kind receipts and logs with SHA256 hashes follow; [checksum list](d_evidence/SHA256SUMS). Scheduler test-only results: smoke **4/4**, full **4/4**, smoke debug **00:30:00**. `c_evidence/protection_recount.json` independently confirms 9,119 configured hashes, 2,215 observed overlap, and **6,904 config-only hashes**.

| Kind | Result / receipt (SHA256) | Log (SHA256) |
|---|---|---|
| regression | **VERIFY_OK** — [verify-regression.json](d_evidence/verify-regression.json) (`c97ef8290918265319830e1506436f41d1a74adb41fd66c736450c0b5bb1a6ab`) | [verify-regression.log](d_evidence/verify-regression.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
| parity | **VERIFY_OK** — [verify-parity.json](d_evidence/verify-parity.json) (`2bbb1532ef81f1ccc0d44f6a5a9e336be8cac0e6746ee9f75f2b6e601af75ce4`) | [verify-parity.log](d_evidence/verify-parity.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
| census | **VERIFY_OK** — [verify-census.json](d_evidence/verify-census.json) (`6ce6e928726a768a34b60ad7b27e8488e484d655249094e5765f438e09cdcec0`) | [verify-census.log](d_evidence/verify-census.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
| readout | **VERIFY_OK** — [verify-readout.json](d_evidence/verify-readout.json) (`959499d3222428bbbaf748d0a540c441cc3aeb6423a082719e4ef1dd6bc9d66b`) | [verify-readout.log](d_evidence/verify-readout.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
