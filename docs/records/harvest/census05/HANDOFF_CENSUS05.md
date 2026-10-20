# CENSUS05-A hand-off — ready for lead commit, not deployed

Continuation of attempt 3 (`ae2703a69`), using CODE_SHA `3b4090bf9b15d2d2cac53ee55161e936157ec0e5`. Package **`17b0eb1ca7fe81a7`**, 167 deploy files: **154 CODE_SHA-identical, 13 additive**. Network OFF; no Git metadata writes, reader runs, deployment, remote verification or Slurm operations. The lead commits. Remote readiness still requires CENSUS05-B readback/VERIFY_OK and coordinator smoke review.

## Source capture and package provenance

The first action ran `audit_code_sha.py` against CODE_SHA. SEG10 and PIPE032 both end READY. The manifest is unchanged; **35/35 components and every recomputed tool digest pass**. Both `greek-ocr-toolkit-pipe032/` and the legacy `greek-ocr-toolkit-main-next/` resolve to this CODE_SHA tree; config maps `greek-ocr-toolkit-pipe032` to the deployed package root. [Fresh audit](first_step_code_sha_audit.json).

Paths used after cleanup: `docs/records/harvest/seg_steps/s5_adopt/`, `docs/records/harvest/pipe032/`, retained `docs/harvest/line_pipeline/{README.md,tool_versions.json}`, `greekocr/`, `scripts/`, and `tests/`. Census_04 reference records are now under `docs/records/harvest/seg_census/`; the embedded adapter source remains `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`. The canonical CODE_SHA readout is under `docs/records/harvest/census05/readout/`; the editable package mirror is `docs/harvest/census05/readout/`. The read-only P3 plan is `../greek-ocr-toolkit-main-next/docs/programme_20261019/NIGHT_PLAN.md`. Pipeline 0.3.2 supersedes its 0.3.1.

[Attempt-3 reuse](attempt3_reuse.json) rehashes 264 retained artifacts, all 226 captured source files and their Git blobs, parity chunks/results, frozen parents, metadata, split/neighbor files and the packaged split loader. Its first-step audit was intentionally refreshed and the old bytes checked against ae2703a69. The 305-pass focused result and native 150/888 result are reused by custody, not rerun as qualification.

[build_package.py](build_package.py) follows Python imports, stage-component fingerprints and dynamic fixture calls of the requested regression modules. During final closure review, unused historical reports and false relative-import dependencies from the embedded source location were removed; [closure_pruning.json](closure_pruning.json) lists them. The deployed adapter imports at its installed module path, not its historical nested repository path. Added fixture dependencies are the CODE_SHA font, gate2 replay helper and saved context JSON. All retained/reused bytes remain identical.

[package_provenance.json](package_provenance.json) proves every source blob with source repository path, package path, byte size, SHA256, ls-tree entry and cat-file blob identity. [PROJECTS_SHA256](PROJECTS_SHA256) binds **all 154 packaged CODE_SHA source paths**, independent of later commit IDs. [Census_04 comparison](census04_file_comparison.json) accounts for all 338 prior deploy entries: {'replaced additive': 10, 'dropped': 213, 'retained as CODE_SHA blob': 115}. Its exact retained/dropped/new lists explain each disposition; no pytest cache is deploy payload.

The split/diagnostics adapter already exists at CODE_SHA as the embedded source above and is copied unchanged. Native `line_pipeline_census.py` has no finalized-split loader or frozen_05 diagnostic join. `numeric_cells.py` is now native CODE_SHA code, so no census_04 numeric-cell addition is needed. No production module is modified.

[additive_files.json](additive_files.json) lists all thirteen additive deploy files, origins, bytes and SHA256s. [additive_changes.patch](additive_changes.patch) contains every census_04 job/config-preparation/parity/mock change; [config_diff.patch](config_diff.patch) gives the full config diff. Parity files are lossless copies of the found SEG10 data. Additions supply input relocation, the required full-mode split refusal, output roots, saved-evidence replay and job wrapping. They add no verdict rule, threshold, relabelling or reason/disposition rewrite. Readout is the separately authorized reporting exception.

## Authorized readout version change

Only version handling changed: remove the hard-coded 0.3 constant; accept `--expect-pipeline-version`; require every decision to carry the same non-empty version, equal to that argument when provided. `readout.sbatch` imports `PIPELINE_VERSION` from the packaged `greekocr/harvest/line_pipeline.py`. Output-inside-run refusal is untouched. Tests cover uniform 0.3.2 with/without an expectation, mismatch, mixed versions, missing/empty versions and the spooled CLI. **20 readout tests pass**, including the inherited 600k-row streaming test; the completed mocked attempts pass 14/14 invariants.

[readout_version.patch](readout_version.patch) is the exact patch against the relocated CODE_SHA readout files for the coordinator to merge as a docs-only commit. Only `census_readout.py`, `readout.sbatch` and `test_census_readout.py` differ in the readout directory. Its changed script and wrapper are additive deploy files with hashes; tests are committed evidence. Prior test receipts were preserved byte-for-byte; fresh receipts are under `readout_validation_receipts/`.

## Stage composition

| Stage | Version | Recomputed SHA256 digest | Match |
|---|---|---|---|
| polytonic | 0.7 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` | yes |
| cyrillic | 0.3 | `f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123` | yes |
| numerics | 0.3 | `f1b5c0aa990b76dac5f757af9fdf16bc0374dc3fc1dd98f64979c021b5bed2b9` | yes |
| dashes | 0.1 | `a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb` | yes |
| segmentation | 0.13 | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` | yes |
| content_gate | 0.3 | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` | yes |
| content_repair | 0.2 | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` | yes |
| composer | 0.3 | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` | yes |
| final_eligibility | 0.3 | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` | yes |
| census | 0.7 | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` | yes |
| inventory | 0.1 | `a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb` | yes |

Pipeline **0.3.2**; segmentation **0.13**, label **0.9-s5**, policy SHA256 `5888fe704e6170b51081d6fa4200a725d2b29f0c70301f238faf7b32088b5b99`. The brief’s final-line template incorrectly says pipeline 0.3.1; the truthful READY line below uses 0.3.2.

## Native runtime and parity

CODE_SHA runtime sources hash-equal lineage `3679c8412`. The three build inputs Cargo.toml, Cargo.lock and src/main.rs also hash-equal the census_03-bound build source tree: [runtime_source_audit.json](runtime_source_audit.json). Predictor `2cc882d6…`, Node, codec and runtime manifest `84ed3add…` remain remote inputs. No live remote hash readback is claimed. The local native predictor used for attempt-3 parity and current synthetic native tests is the SEG10 debug build `d2fe37a5…`; built artifacts are not packaged.

**Parity route: found existing, hash-checked.** `../greek-ocr-data/docs/records/harvest/seg_steps/s5_adopt/replay.jsonl`, 42,991,967 bytes, SHA256 `6e9ab21d28340ec7acf9d2b1b39bc7cf899a6bfc87b754e59d986265da417f32`. The receipt artifact entry supplies its hash; replay_receipt.json supplies row/flip totals. Ordered decompression of parity/replay-01.jsonl.gz and replay-02.jsonl.gz recreates those exact bytes. No expectation was rebuilt. The retained native result is **150/150 + 888/888 verdict AND reason exact**, input order preserved, 0 readers. Its 60.62-second result is hash-reused. The real spooled parity job separately executes the saved evidence through the packaged policy and passes all 1,038 rows: [parity_policy_audit.json](parity_policy_audit.json).

## Corrections — census_03 → census_05

All 14 original canonical ledgers match census_03 hashes and the current producer releases. Exactly **five N1 ledgers regenerated, five cyrillic standing, four polytonic unbound**; no superseded-source ledger remains. All ten bound files pass full CODE_SHA `ArtifactCorrector.load`, which validates every record against registered original parents. All 592,466 parent observations were canonicalized and registered locally; no image inference or reader occurs in this validation.

[regenerate_n1.py](regenerate_n1.py) uses exact `canonical_result`, `legacy_convert` and `n1_candidates` functions extracted from census_03 prepare_remote.py, with CODE_SHA identity/span/validation functions and active numerics 0.3/digest. Full original prepare_remote.py and finalize_remote.py are copied under corrections/converter_original/. The extraction patch shows every removed orchestration section; the extracted converter functions themselves have **no changed line**. Finalize’s obsolete code-patching/digest-restamping pass is not executed. Only binding to already-packaged active numerics functions replaces that step. Producer input hashes and tokenizer/scanner definitions match the original receipt. Remote producer names are preserved in evidence while the same hash-checked bytes are read locally.

The first local regeneration used local provenance paths. The final regeneration repeated the converter with the original producer path identities, eliminating that unnecessary provenance-only difference. **Final record diff: zero status moves, zero edit/hold changes, zero content changes beyond tool_version/tool_digest, identical record membership/order for every ledger.** The expected numeric-adjacency change produces no difference in these canonical converter outputs; no status movement is invented. [Full ledger report](corrections/report.json), [execution log](corrections_regeneration.log).

| Tool | Parent | State | Records 03→05 | Edits 03→05 | Holds 03→05 | No-change 03→05 |
|---|---|---|---|---|---|---|
| polytonic | collection-v2-train | not bound in census_05 | 213831→unbound | 0→unbound | 113176→unbound | 100655→unbound |
| numerics | collection-v2-train | regenerated | 214436→214436 | 0→0 | 1919→1919 | 212517→212517 |
| cyrillic | collection-v2-train | standing | 6229→6229 | 424→424 | 256→256 | 5549→5549 |
| polytonic | collection-v2-train | not bound in census_05 | 605→unbound | 605→unbound | 0→unbound | 0→unbound |
| polytonic | collection-v2-dev | not bound in census_05 | 5412→unbound | 0→unbound | 0→unbound | 5412→unbound |
| numerics | collection-v2-dev | regenerated | 13413→13413 | 0→0 | 0→0 | 13413→13413 |
| cyrillic | collection-v2-dev | standing | 401→401 | 64→64 | 14→14 | 323→323 |
| polytonic | collection-v2-test | not bound in census_05 | 15409→unbound | 0→unbound | 0→unbound | 15409→unbound |
| numerics | collection-v2-test | regenerated | 43766→43766 | 0→0 | 0→0 | 43766→43766 |
| cyrillic | collection-v2-test | standing | 2250→2250 | 290→290 | 180→180 | 1780→1780 |
| numerics | collect-v3-W1-20261018-0524 | regenerated | 93998→93998 | 47→47 | 582→582 | 93369→93369 |
| cyrillic | collect-v3-W1-20261018-0524 | standing | 4164→4164 | 0→0 | 0→0 | 4164→4164 |
| numerics | collect-v3-W2-20261018-0524 | regenerated | 190632→190632 | 0→0 | 0→0 | 190632→190632 |
| cyrillic | collect-v3-W2-20261018-0524 | standing | 6854→6854 | 0→0 | 0→0 | 6854→6854 |

| Tool / parent | Census_03 bytes / SHA256 | Census_05 bytes / SHA256 |
|---|---|---|
| polytonic / collection-v2-train | 316316955 / `16511ff260a9e11c695225415914b713bbb7b5905192d79662a349299ac35320` | not bound in census_05 |
| numerics / collection-v2-train | 198927711 / `404b30414607092bb8d58bb14cf07f5975f5de8ed147c5e53b1047958b8f3128` | 198927711 / `ce079c59d40161cb0204a5b22ae5e35ede5456799e2d510eeb21ca11e01044ce` |
| cyrillic / collection-v2-train | 5224083 / `90c8a8f4ccb8cca9a83392c4d93cff0e5a88c3c259f58923532dbc77cb464b4e` | 5224083 / `90c8a8f4ccb8cca9a83392c4d93cff0e5a88c3c259f58923532dbc77cb464b4e` |
| polytonic / collection-v2-train | 714568 / `51dae7b4da738e26a46f434fa25a5ee7ea9e2be39be50b26e28e92ced6e1935c` | not bound in census_05 |
| polytonic / collection-v2-dev | 3461240 / `d7ff0686a678f264f21414704cb56c1500c6c53ab2fe4d1d3bb2fa18876ee17f` | not bound in census_05 |
| numerics / collection-v2-dev | 10556613 / `fc3fb99a3f3fb996ca77ca7fc4863aedc0e94a8f5516ac53edce115b4af2f8a7` | 10556613 / `506646b1b9636e917bffb6b26d540f63daca30b00bc292adb33c4a67304cfc18` |
| cyrillic / collection-v2-dev | 367289 / `9339706c96c70de0f3ad30b27276c3b364e87d3c5a9b091c71a93c0546bf0e6b` | 367289 / `9339706c96c70de0f3ad30b27276c3b364e87d3c5a9b091c71a93c0546bf0e6b` |
| polytonic / collection-v2-test | 9856279 / `ec35a62a9f8efda4e0855ff9a0de4077e3ad9bf4a12c3e4447a403f06ec9a0ea` | not bound in census_05 |
| numerics / collection-v2-test | 34491534 / `a09c903b48e084552f6816d30adb14280d7f78f271f994ab9be970f72c6925b6` | 34491534 / `4b2913261285f6affa198fd1ad44b15658aa2b932fd79287a0d6496f877e9053` |
| cyrillic / collection-v2-test | 2263037 / `9f673101f4063e72b587d82c49b24e63e0304ddddd915fd5f7ef43bdec17df69` | 2263037 / `9f673101f4063e72b587d82c49b24e63e0304ddddd915fd5f7ef43bdec17df69` |
| numerics / collect-v3-W1-20261018-0524 | 76975345 / `edb43176cc77a8968224e0d9ab7f38d91514ae4bda3c03e2e650e0b570435c1f` | 76975345 / `29cfa22d3edc97a9337bb1e6503202db08caec702220b548001cc6eed685c0ae` |
| cyrillic / collect-v3-W1-20261018-0524 | 3386517 / `3810fd03892f509db00a3f3438335e0ab241c25c807b84d4771ee4b858ed132d` | 3386517 / `3810fd03892f509db00a3f3438335e0ab241c25c807b84d4771ee4b858ed132d` |
| numerics / collect-v3-W2-20261018-0524 | 155889454 / `f5e24bb3eaf4f7735910eb2dd7b80dd2b336fa52ea000959006c33d30b1e6652` | 155889454 / `ebf7e6876323849f765a285a882247bf0252bdd04ca9cf6f2109be1fd0dc578c` |
| cyrillic / collect-v3-W2-20261018-0524 | 5654550 / `0eaa814123a1f778f62aedbc2fe73b2afe8837d41f6b93bf024c4c3a390c7cf4` | 5654550 / `0eaa814123a1f778f62aedbc2fe73b2afe8837d41f6b93bf024c4c3a390c7cf4` |

Each regenerated ledger’s status-transition matrix is in corrections/report.json, including all unchanged transitions; the changed-record list is empty for all five. Exact new files are local ignored correction inputs, transported to `$W/census_05_20261020/inputs/` by FOLLOW_UP. The **35 gzip chunks** are gitignored; durable copy at the data root, receipt `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archive_receipt.json`, checksums `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/ARCHIVES_SHA256SUMS`, archives `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archives/`. All 35 compressed hashes match `corrections/archive_receipt.json`; see `c_evidence/archives.json`. They are input evidence, outside the code deploy manifest.

The four polytonic files above (including the 605-row SF7 candidate) are **not bound in census_05**. Config explicitly sets `routes_out_of_scope: ["polytonic"]`. SF7/TR2: when SF7’s audit passes, a later census restores this route and rebinds its ledgers at the then-current status; nothing is prepared to apply tonight.

## Config and finalized split

Config changes only codec/versions/component-root paths, the correction bindings and polytonic route scope. Output root is selected by the job wrapper. `@CENSUS05_PROJECTS@` is resolved by preparation into the deployed package root, avoiding a package-ID/config hash cycle. [Field-by-field diff](config_diff.json) includes complete before/after values. Parents, metadata, native settings, held-out policy and frozen_05 are unchanged. Census_03 remains 592,466 rows, 9,119 protected crops and 61 held-out editions. Frozen_05 remains an output-only diagnostic join, not a verdict source.

The P1 split compressed SHA256 is `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`, equal to git show aa860af55 in sol-recut. The schema and **packaged loader** validate 320,479 unique parent+row assignments, 1,359 editions, one split per edition, 99 forced-test editions (52,468 forced-test rows) all test. Zero unmatched split rows and zero unmatched W1/W2 parent rows in either direction. The 436 later BSB pages remain outside the frozen parents and unassigned. The split itself is not packaged; FOLLOW_UP names its exact new remote input path and submit-time environment binding.

| Parent | Rows | Train | Dev | Test | Unmatched |
|---|---:|---:|---:|---:|
| collection-v2-train | 214436 | frozen | frozen | frozen | 0 |
| collection-v2-dev | 13522 | frozen | frozen | frozen | 0 |
| collection-v2-test | 44029 | frozen | frozen | frozen | 0 |
| collect-v3-W1-20261018-0524 | 101098 | 71796 | 1720 | 27582 | 0 |
| collect-v3-W2-20261018-0524 | 219381 | 181606 | 5287 | 32488 | 0 |
| Finalized W1/W2 total | 320479 | 253402 | 7007 | 60070 | 0 |

Expectation resolution, CODE_SHA gate 0.3 on every hash-verified local parent row: **592,466 page override; 0 book declaration; 0 source policy; 0 unresolved**. Metadata hash `dd2da654…` is unchanged. These attempt-3 counts are reused only after all input/loader hashes pass: [input_audit.json](input_audit.json), [attempt3_reuse.json](attempt3_reuse.json).

## Jobs, mocks, tests and runtime

| Job | Partition | Nodes/tasks | CPUs | Limit |
|---|---|---|---|---|
| regression | normal | 1/1 | 256 | 00:05:00 |
| parity | normal | 1/1 | 256 | 00:05:00 |
| census | normal | 1/1 | 256 | 04:00:00 |
| readout | normal | 1/1 | 16 | 00:30:00 |

Real scripts are copied to a mock Slurm spool and launched from unrelated /private/tmp. Only srun and native image/reader I/O are doubled. The real config preparer, CODE_SHA pipeline, adapter, import/validation, gate, admission, durable publication and readout run. The mock input is the same 200 real raw rows/crops as census_04, with segmentation outcomes replaced by the hash-verified attempt-3 native results. Synthetic no-change correction fixtures and broad declared metadata remain mock-only, as in census_04. To exercise **all 200 rows under smoke’s unchanged 40-row-per-parent cap**, the two large fixture groups are subdivided into mock-only parent IDs; no production parent or raw label/crop changes. Fixture allocations and frozen diagnostics are explicitly synthetic test inputs, not new production splits or independent accuracy evidence.

| Mock | Rows | ADMIT | DROP | HOLD | Readout |
|---|---:|---:|---:|---:|---|
| smoke-mode-i | 200 | 43 | 29 | 128 | 14/14 PASS |
| smoke-mode-ii | 200 | 119 | 42 | 39 | 14/14 PASS |
| full-mode-ii | 200 | 119 | 42 | 39 | 14/14 PASS |
| full-mode-i (no split) | refused | — | — | — | no pipeline/readout run |

Full-without-split exits 2 before executing the pipeline; mismatched path/SHA pairs also refuse. [Mock results](mock_batch_results.json), [spooled run log](mock_batch.log), [refusal](mocks/full-without-split.log). Readout outputs remain sibling `<attempt>.readout/`; its inside-run refusal stays intact.

Verbatim readout last lines:

- **smoke-mode-i**: `CENSUS READOUT: rows 200 (complete yes); ADMIT 43 HOLD 128 DROP 29; admitted_train 43; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 14/14 PASS`
- **smoke-mode-ii**: `CENSUS READOUT: rows 200 (complete yes); ADMIT 119 HOLD 39 DROP 42; admitted_train 103; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 14/14 PASS`
- **full-mode-ii**: `CENSUS READOUT: rows 200 (complete yes); ADMIT 119 HOLD 39 DROP 42; admitted_train 103; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 14/14 PASS`

The spooled packaged regression passes **360 tests, 0 failed, 9 skipped**, including content_gate, line_pipeline, integration_fixes, numeric_cells and all four test_seg modules. Skips are missing relocated external fixtures, using CODE_SHA’s own require_file policy (listed in regression_tests.log); no test or invariant was weakened. Readout: **20 passed, 0 failed**. Combined final distinct suites: **380 passed, 0 failed, 9 skipped**. The reused 305-test focused run is not added to this count; neither is the coordinator’s reported 7,305-test full suite claimed here.

The committed S4 and SEG10 replay records have no per-row timing fields; their aggregate receipts are 117.149 s/1,288 S4 rows (old+new native runs) and 64.111 s/1,705 SEG10 rows. Those are not comparable per-row 0.8 baselines. A separate local **timing-only supplement** measures the same saved 150+888 rows under 0.8 and SEG10, preserving parity as attempt-3 evidence. Totals: 49.592 s vs 62.618 s, ratio 1.262667. Applying that ratio to census_03 01:49:19 yields **02:18**, with **01:42 margin** to 04:00:00. This is a same-row local segmentation ratio extrapolated to whole census time, not remote qualification; production metadata/mix/cache behavior can differ. Per-row timings are in timing_rows.jsonl and summary in runtime_estimate.json. S4 timing is absent, not fabricated; SEG10 reports zero measurement differences from S4. The four-hour job limit stays unchanged.

## Deployment and P4 contract

[DEPLOY_PATHS.txt](DEPLOY_PATHS.txt), [DEPLOY_SHA256SUMS](DEPLOY_SHA256SUMS), [package_id.json](package_id.json) bind all 167 code payload files. The package ID is the first 16 hex of SHA256(DEPLOY_SHA256SUMS), not a commit. No ignored payload remains; local native target symlink, SQLite validation files and mock runtimes are excluded. [INPUTS.json](INPUTS.json) separately binds five regenerated ledgers plus the split. [FOLLOW_UP.md](FOLLOW_UP.md) contains literal deploy/refuse-nonempty/readback, unchanged verifier, debug placeholder smoke/full afterok chains, expected sibling-readout outputs and main re-pointing commands. No command in that document was executed.

The brief names four `.sbatch` job kinds but says “all five”. Four verifier commands are supplied for the four named kinds; common.sh is hash-verified shared code, not a fifth submitted job. Clarification was requested while work continued. No fictitious fifth job is created. The later explicit sibling readout rule supersedes the earlier inside-attempt wording.

P4 uses the full READOUT.md and readout.json, with raw counts and all invariants. Exact sections from the completed full mock are: `Totals`, `Disposition reason occurrences`, `Route statuses`, `Segmentation availability`, `Gate totals`, `V3 splits`, `Pending totals`, `Pipeline versions`, `Admission export`, `Completeness`, `Invariants`, `all_disposition_reasons`, `all_reasons`, `all_reasons_totals`, `by_stratum`, `class`, `class_rates`, `class_totals`, `class_totals_rates`, `deciding_reasons`, `deciding_reasons_totals`, `decisions_by_parent_split`, `gate_by_class`, `gate_by_parent`, `gate_by_source`, `gate_reasons`, `input_rows`, `input_splits`, `segmentation_reasons`, `segmentation_reasons_totals`, `source`, `source_class`, `source_class_rates`, `source_class_totals`, `source_class_totals_rates`, `source_rates`, `source_totals`, `source_totals_rates`, `toolchain_versions`, `Timing`, `Tool version binding`, `Diagnostics (first 20 in file order)`, `File provenance`. A full run with the optional census_03 summary adds `baseline`. The last-line format and expected complete files are in FOLLOW_UP; real census admissions are not predicted from the mock.

## Attempt 1

`5ca995d34`: stopped correctly on stale census digest; resolved by the current recomputation.

## Attempt 2

`0387e9177`: stopped correctly on segmentation 0.9-s5 violating the numeric version invariant and old numerics identities. PIPE032 supplies segmentation 0.13/label 0.9-s5; all five incompatible N1 ledgers have now been regenerated and fully loaded. Attempt 3’s readout blocker is resolved by the explicit authorization in this brief. Historical blocker scripts/logs remain evidence of their recorded attempts, not current launch checks.

## Commit and scope

The lead uses [commit_paths.txt](commit_paths.txt), with the exact procedure in [COMMIT_LIST.md](COMMIT_LIST.md). [receipt.json](receipt.json) and [scope_guard.json](scope_guard.json) bind current artifacts and enumerate the final changed files, all under docs/harvest/census05/. Unrelated pre-existing docs/harvest/seg09/ is preserved. No .git write, network, reader, deploy or Slurm occurred.

Scope exception recorded candidly: an initial regression command used one extra `..` in its output path, temporarily creating docs/harvest/regression_tests.log and docs/harvest/regression-tmp/. They were immediately moved under census05/; no such outside artifact remains, and the successful runs use corrected paths. The final worktree changes are entirely in the authorized subtree.

CENSUS05-A READY: CODE_SHA 3b4090bf; package 17b0eb1ca7fe81a7 files 167 (CODE_SHA-identical 154, additive 13); versions pipeline 0.3.2 seg 0.9-s5 gate 0.3 final 0.3; corrections 10 ledgers (new numerics-v2-train,v2-dev,v2-test,W1,W2, standing 5, superseded-source 0); parity 150 150/150 888 888/888 = SEG10 yes; mock 200 ADMIT/DROP/HOLD 119/42/39; readout invariants 14/14 PASS; split validated 320479 rows; runtime estimate 02:18 vs 04:00; tests 380 passed 0 failed


## B: deploy + verify

Completed 2026-10-20; no submission. HEAD `0736754c12dc6240fed2557df2a8ab68bb5f8841` descends from `a09642bd4`; the sole extra commit touches only `docs/briefs/CENSUS05_B_deploy.md`. Branch `opus/seg-census`. Pre-existing untracked `docs/harvest/seg09/` preserved. No Git mutation commands used. All B artifacts are under this directory.

Remote root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7`; bundle: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05`. New empty destinations were checked before copying. Repository-relative paths preserved. [Readback](b_evidence/readback.json): **173/173 deployed files and inputs match** (167 payload + 6 inputs), plus **5/5 standing cyrillic ledgers** hashed in place; no cyrillic copies. [Raw remote hashes](b_evidence/remote_sha256sum.txt), [deployment command receipts](b_evidence/deploy_commands.json). Remote scope check: 167 code files, 6 inputs, no attempts or logs ([receipt](b_evidence/remote_final_scope.log)).

Verifier block executed unchanged from FOLLOW_UP.md before tracked handoff edits; no allow-list, exemption, script change or credential repair. Outputs:

```text
regression: VERIFY_OK (verify-regression.json)
parity: VERIFY_OK (verify-parity.json)
census: VERIFY_OK (verify-census.json)
readout: VERIFY_OK (verify-readout.json)
```

[Live partition/accounting evidence](b_evidence/remote_inspection.log): debug MaxTime **01:30:00**, DefaultTime 00:45:00, MinNodes 0, MaxNodes 4, State UP. Every job requests 1 node/1 task. Smoke uses **00:10:00** for each kind. [Measured mock smoke](b_evidence/smoke_timing.json): 200 rows / 0.844411542 s = 236.851334 rows/s; 600 s allows over 700 times that duration. Native observations are saved and corrections synthetic: this is a scheduling basis, not remote throughput qualification. The first timing invocation used incompatible system NumPy; its failure log is retained, then the prescribed sol-recut venv completed the run. Regression evidence is 2.86 s; retained native parity is 60.62 s. Coordinator must review real smoke before full.

Census_03 baseline **found**: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json`, 130590 bytes, SHA256 `b187a2e7a0e218b433aa28dbc96d31f0c8f7e7e373b35027ba366b0467894fe3`; copied only as [census03_summary.json](census03_summary.json). CURRENT.json identifies this completed generation and identical hash. No remote decisions downloaded. Committed readout `--baseline` parsed it against the 200-row mock: [log](b_evidence/baseline_parse.log), [readout](b_evidence/baseline-mock-readout/readout.json), 14/14 invariants PASS; mock-versus-production deltas are parser evidence only. `sacct -j 3695426`: ocr_filter_census03, normal, COMPLETED, 1 node/288 allocated CPUs, 01:49:40 elapsed / 04:00:00 limit; principal Python step 01:49:19, 256 CPUs.

All following responses are **test-only predictions**, not submitted jobs. Exact commands, environment and stdout/stderr: [test_only.json](b_evidence/test_only.json). Smoke debug/00:10:00; full retains each script’s normal partition and times regression/parity 00:05:00, census 04:00:00, readout 00:30:00. Both modes bind the deployed split; full binds the found baseline. No dependencies were fabricated for dry checks.

| Mode | Kind | Exit | Scheduler response |
|---|---|---:|---|
| smoke | regression | 0 | sbatch: Job 3703752 to start at 00:48:28 a using 288 processors on nodes nid007648 in partition debug |
| smoke | parity | 0 | sbatch: Job 3703753 to start at 00:48:30 a using 288 processors on nodes nid007648 in partition debug |
| smoke | census | 0 | sbatch: Job 3703755 to start at 00:48:32 a using 288 processors on nodes nid007648 in partition debug |
| smoke | readout | 0 | sbatch: Job 3703757 to start at 00:48:34 a using 288 processors on nodes nid007648 in partition debug |
| full | regression | 0 | sbatch: Job 3703759 to start at 03:49:36 a using 288 processors on nodes nid005423 in partition normal |
| full | parity | 0 | sbatch: Job 3703760 to start at 03:49:38 a using 288 processors on nodes nid005423 in partition normal |
| full | census | 0 | sbatch: Job 3703761 to start at 03:49:40 a using 288 processors on nodes nid005423 in partition normal |
| full | readout | 0 | sbatch: Job 3703763 to start at 03:49:45 a using 288 processors on nodes nid005423 in partition normal |

Final literal coordinator commands below are **unexecuted**, for owner-required Astra review and coordinator approval before submission. Create attempts/logs only at that stage. Run the smoke chain, stop for review, then separately run the full block after its gates.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS05_BUNDLE="$W/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05"
RUN_ROOT="$W/census_05_20261020"
mkdir -p "$RUN_ROOT/attempts" "$RUN_ROOT/logs"
submit_census05() {
  local regression parity census readout
  regression=$(sbatch --parsable "$@" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS05_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable "$@" --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS05_BUNDLE/jobs/parity.sbatch")
  census=$(sbatch --parsable "$@" --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS05_BUNDLE/jobs/census.sbatch")
  readout=$(sbatch --parsable "$@" --dependency="afterok:$census" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/readout-%j.log" "$CENSUS05_BUNDLE/jobs/readout.sbatch")
  printf 'regression=%s parity=%s census=%s readout=%s\n' "$regression" "$parity" "$census" "$readout"
}
unset CENSUS05_RUN CENSUS05_READOUT_OUT CENSUS05_CONFIG CENSUS05_BASELINE
export CENSUS05_SPLIT_FILE="$W/census_05_20261020/inputs/row_split.jsonl.gz"
export CENSUS05_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS05_ATTEMPT=smoke-split-001 CENSUS05_EXPECT_ROWS=200
submit_census05 --partition=debug --time=00:10:00

# Separate coordinator action, only after smoke review and P3's gates pass.
# This uses the normal partition and each script's original production time.
export E4_SMOKE=0 CENSUS05_ATTEMPT=full-split-001 CENSUS05_EXPECT_ROWS=592466
# Optional real census_03 summary supplies the readout's baseline delta table.
export CENSUS05_BASELINE="$W/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json"
submit_census05
```

The readout submission in each chain points to the deployed `jobs/readout.sbatch`, which invokes the deployed `readout/census_readout.py`, derives version 0.3.2 from deployed package code, and writes a sibling `<attempt>.readout/`. Exact expanded full readout command inside that allocation (unexecuted):

```bash
PYTHONPATH="/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032" \
  "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python" -B "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05/readout/census_readout.py" \
  --expect-pipeline-version 0.3.2 \
  --run "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/attempts/full-split-001" \
  --out "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/attempts/full-split-001.readout" \
  --baseline "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json" --expect-rows 592466
```

[B receipt](B_RECEIPT.json) and [Astra review inputs](REVIEW_INPUTS.md). No real smoke, production census, or remote readout was run by B.


## C: readout fix + redeploy

New package **997b7d2ab5a8775b**, 167 files; bundle `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05`. No submission and no .git writes. Old B evidence and command block above remain historical. C smoke uses **--partition=debug --time=00:30:00** for all four kinds; full retains the packaged limits.

Changes since the Astra review:

- H1: `readout/census_readout.py` mirrors packaged `line_pipeline_census.py:167–171`; configured crops union observed dev/test crops, plus existing protected editions. `test_astra_config_only_crop` reproduces the one-row witness: leaks 1, exit 1; without configuration: leaks 0, exit 0.
- L1: `admitted_train_equals_eligible` mirrors packaged `line_pipeline_census.py:204–214`, using inventory train split and ADMIT decisions, exact row content hashes and unique identities. The subset invariant stays. `test_astra_missing_export` (three eligible decisions, empty export) fails with exit 1. `test_export_equality` also covers duplicates and changed row contents.
- M2: `readout/test_census_readout.py` finds its own repository root, skips absent historical fixtures with their paths in the reason, and writes all outputs and receipts to `tmp_path`. Synthetic successful exports now contain every eligible row. Tests: **28 passed in 31.23s** (0 failed, 0 skipped); packaged regression: **360 passed, 9 skipped in 3.11s** (0 failed). Logs in `c_evidence/`.
- M3: `INPUTS.json`, this handoff and `REVIEW_INPUTS.md` record durable archive custody; `c_evidence/archives.json` verifies **35/35** hashes against the original receipt and data-root checksum list.

`readout_fix.patch` targets `docs/records/harvest/census05/readout/` and supersedes `readout_version.patch`: it includes both the prior pipeline-version fix and these changes (including the prior wrapper change). No pipeline source changes. The 154 CODE_SHA-identical files and PROJECTS_SHA256 are byte-identical; DEPLOY_PATHS.txt was regenerated with identical bytes. The deployed payload changes only `readout/census_readout.py`; tests change locally but were never part of the deploy manifest. Updated manifests are DEPLOY_SHA256SUMS, additive_files.json and package_id.json.

Deployment completed into the new empty destination only. `c_evidence/readback.json`: **178/178** hashes match (167 payload, six unchanged inputs rehashed in place, five standing Cyrillic ledgers). No input copies or writes to the old package. The original four verifier invocations and eight scheduler dry checks have receipts in `c_evidence/`. After the lead commit, CENSUS05-D reran the unchanged verifier: all four are VERIFY_OK, with current receipts and logs in `d_evidence/` (hashes below).

Mock readout last lines (synthetic generations, not production):

```text
CENSUS READOUT: rows 200 (complete yes); ADMIT 43 HOLD 128 DROP 29; admitted_train 43; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
CENSUS READOUT: rows 200 (complete yes); ADMIT 119 HOLD 39 DROP 42; admitted_train 103; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
CENSUS READOUT: rows 200 (complete yes); ADMIT 119 HOLD 39 DROP 42; admitted_train 103; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
```

Coordinator commands prepared only; require a successful unchanged verifier and owner review before actual submission:

```bash
# C COORDINATOR COMMANDS — NOT EXECUTED; REQUIRE VERIFY_OK AND REVIEW
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS05_BUNDLE="$W/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05"
RUN_ROOT="$W/census_05_20261020"
mkdir -p "$RUN_ROOT/attempts" "$RUN_ROOT/logs"
submit_census05() {
  local regression parity census readout
  regression=$(sbatch --parsable "$@" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS05_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable "$@" --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS05_BUNDLE/jobs/parity.sbatch")
  census=$(sbatch --parsable "$@" --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS05_BUNDLE/jobs/census.sbatch")
  readout=$(sbatch --parsable "$@" --dependency="afterok:$census" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/readout-%j.log" "$CENSUS05_BUNDLE/jobs/readout.sbatch")
  printf 'regression=%s parity=%s census=%s readout=%s\n' "$regression" "$parity" "$census" "$readout"
}
unset CENSUS05_RUN CENSUS05_READOUT_OUT CENSUS05_CONFIG CENSUS05_BASELINE
export CENSUS05_SPLIT_FILE="$W/census_05_20261020/inputs/row_split.jsonl.gz"
export CENSUS05_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS05_ATTEMPT=smoke-split-001 CENSUS05_EXPECT_ROWS=200
submit_census05 --partition=debug --time=00:30:00

# Separate coordinator action, only after smoke review and P3's gates pass.
# This uses the normal partition and each script's original production time.
export E4_SMOKE=0 CENSUS05_ATTEMPT=full-split-001 CENSUS05_EXPECT_ROWS=592466
# Optional real census_03 summary supplies the readout's baseline delta table.
export CENSUS05_BASELINE="$W/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json"
submit_census05
```

C verifier result (CENSUS05-D): **4/4 VERIFY_OK** against committed HEAD `76a6510d4eb2ad4d67b09f881bd81c2630e4ad77`. The unchanged verifier ran all four kinds with the arguments from `c_evidence/verify.py`, changing only `--out` to the external scratch directory; logs were also external. All four finished before receipts and logs were copied into `d_evidence/`. No bypass, deployment, submission or .git writes. Per-kind receipts and logs with SHA256 hashes follow; [checksum list](d_evidence/SHA256SUMS). Scheduler test-only results: smoke **4/4**, full **4/4**, smoke debug **00:30:00**. `c_evidence/protection_recount.json` independently confirms 9,119 configured hashes, 2,215 observed overlap, and **6,904 config-only hashes**.

| Kind | Result / receipt (SHA256) | Log (SHA256) |
|---|---|---|
| regression | **VERIFY_OK** — [verify-regression.json](d_evidence/verify-regression.json) (`c97ef8290918265319830e1506436f41d1a74adb41fd66c736450c0b5bb1a6ab`) | [verify-regression.log](d_evidence/verify-regression.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
| parity | **VERIFY_OK** — [verify-parity.json](d_evidence/verify-parity.json) (`2bbb1532ef81f1ccc0d44f6a5a9e336be8cac0e6746ee9f75f2b6e601af75ce4`) | [verify-parity.log](d_evidence/verify-parity.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
| census | **VERIFY_OK** — [verify-census.json](d_evidence/verify-census.json) (`6ce6e928726a768a34b60ad7b27e8488e484d655249094e5765f438e09cdcec0`) | [verify-census.log](d_evidence/verify-census.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
| readout | **VERIFY_OK** — [verify-readout.json](d_evidence/verify-readout.json) (`959499d3222428bbbaf748d0a540c441cc3aeb6423a082719e4ef1dd6bc9d66b`) | [verify-readout.log](d_evidence/verify-readout.log) (`01ea8fe3ef4e2db89a56f3a2b41e81e1d12252a696f06ca0ae4b9baac76aa787`) |
