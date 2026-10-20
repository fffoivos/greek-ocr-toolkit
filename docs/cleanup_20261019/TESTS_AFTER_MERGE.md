# CLEAN4T — tests after the integrated merge

The import, subprocess checkout, temporary-output, and available fixture failures were repaired without changing segmentation, gate, SF7, RU1, N1, or admission decision rules. The full suite is **not green**: remaining policy/output disagreements, historical freeze checks, and unavailable inputs are listed below. No freeze, origin hash, truth record, reader answer, or accepted policy was rewritten to make an assertion pass.

## Scope and verification

- Requested starting tree: `cleanup/20261019`, `ac1c38cf6`.
- The coordinator advanced HEAD to `70a3a4de6b7eb5da72292b7d9bbb6ad52a3a59e5` during this task. A separate run also added the data-root adapter to many runtime files. Those edits are not CLEAN4T changes and were not reverted. The final run includes that live working tree, not just the original merge.
- A candidate run saw late edits to `greekocr/ops/__init__.py` and `tests/test_data_root.py`. The final full run was restarted after those edits. A separate current-tree check passed **31 tests** across data-root tests, N1 gate tests, and repaired N1 receipt/order assertions. Source fingerprints were compared around the final run; see the qualification receipt below.
- No git-writing command was run. `docs/cleanup_20261019/drafts/` was not read or modified.

## Before and after

Owner-supplied before result (including six collection errors):

```text
153 failed, 7,025 passed, 20 skipped, 47 errors
```

Initial diagnostic full run, started before the fixes but overlapping fixture restoration (not a pristine baseline):

```text
143 failed, 7070 passed, 20 skipped, 9 warnings, 12 errors, 35 subtests passed in 347.49s (0:05:47)
```

Intermediate full run, overlapping the other run's data-root edits:

```text
98 failed, 7187 passed, 21 skipped, 9 warnings, 5 errors, 63 subtests passed in 364.15s (0:06:04)
```

Final full run (zero collection errors and zero setup errors):

```text
73 failed, 7222 passed, 26 skipped, 9 warnings, 63 subtests passed in 389.39s (0:06:29)
```

## Repairs

In this table, `CP7` means `docs/records/harvest/collect_v3_admission/seg/cp7/`.

| Test file | Cause | Fix / result | Files changed by CLEAN4T |
|---|---|---|---|
| `tests/test_seg_cp7.py` | Secondary-reading `common` already cached in `sys.modules`; CP7 symbols missing | Use a distinct `cp7_common` binding | `CP7/cp7_common.py`, eleven CP7 importers listed below, this test |
| `tests/test_seg_cp7a3_geometry.py` | Same helper collision during collection | Importers use the explicit CP7 helper binding | `CP7/prepare_population_geometry.py` and helper |
| `tests/test_seg_cp7b_score.py` | Same helper collision during collection | Importers use the explicit CP7 helper binding | `CP7/score_cp7b.py` and helper |
| `tests/test_seg_cp7c2_runtime.py` | Same collision, including a local `import common` in a closure test | Import CP7 helper by its unique name | This test, helper and CP7 importers |
| `tests/test_seg_cp7c.py` | Helper collision; CP5 plain JSON absent although its gzip archive is present; later artifact assertions reflect a different run phase | Fix import, restore CP5 from verified gzip; leave freeze/lifecycle assertions visible | CP7 importers; `tests/prepare_merge_fixtures.py`; generated CP5 input |
| `tests/test_seg_cp7c_score_fixtures.py` | Helper collision; frozen standalone preflight rejects the integrated source tree | Fix import; leave freeze disagreement visible | CP7 importers |
| `tests/test_seg_cp7d.py` | Helper collision; original-binding assertion requires historical frozen code | Fix import; leave freeze disagreement visible | CP7 importers |
| `tests/test_scan_rollout.py` | Cached RU1 v4.4 scanner selected instead of canonical v4.5.5; merged tests also lacked source-worktree recorder fixtures/probes | Load exact canonical scanner under its own module key; retain updated v4.5.5 tests and fixtures from sol-reading worktree | This test; `tests/fixtures/v45/{README.md,helper_overwrites.json,recorder_overwrites.json,rejected_recorder_overwrites.json}` |
| `tests/test_seg_small.py` | Tests and S4 replay explicitly invoke `target/debug/...`; release-only build does not satisfy that path | Build release offline as requested, then debug offline for existing replay/test paths; no segmentation code/test changes | Generated `scripts/harvest/filter_runtime/target/` only; fixture preparation script |
| `tests/test_seg_curve.py` | Same predictor dependency | Same builds; all 23 small/curve tests pass from repository root | Generated runtime only |
| `tests/test_r2_cards.py` | Resolver adopted from r2-cards confines outputs to its worktree; pytest system tmp directory violates that rule | Make this module's temporary directory disposable and inside the checkout | This test |
| `tests/adjudicate/test_owner_runtime.py` | Fake overlay DOM lacked `querySelector`, now used by shipped JS | Supply the DOM method in the test harness; keep shipped JS | `tests/adjudicate/owner_sheet_runtime.cjs` |
| `tests/adjudicate/test_os5_owner_sheets.py` | Saved image path names producing cleanup worktree; replay writes equivalent raster here | Verify original/replayed raster bytes before normalizing that single output path | This test |
| `tests/adjudicate/test_os2_owner_sheets.py`, `tests/adjudicate/test_reemission.py`, `tests/adjudicate/test_sr1.py` | Generated HTML, crop cache, and cleanup fixture trees were absent | Restore available byte-preserved archive inputs; SR1 and path/data errors resolved; older HTML output disagreements remain visible | Preparation script plus generated inputs in fixture receipt |
| `tests/test_n1g.py` | Receipt's absolute dictionary keys name producing secondary checkout | Match the exact `scripts/numerics/<name>` suffix and retain hash assertions | This test |
| `tests/test_n1r.py` | Checkout mtimes no longer encode experimental freeze order | Use producing receipt's freeze-order claim, verify rule hash and recorded rule input; retain other physical/selection assertions | This test |
| `tests/test_n1tb.py` | Allowed owner-sheet replacement exception compared against current checkout instead of producing receipt path | Match the relative owner-sheet directory, retaining other superseded-file hashes | This test |
| `tests/test_lqb3.py` | Absolute receipt paths cannot be made relative to this checkout | Derive repository-relative names from the producing worktree; expose real release-registry drift instead of a path exception | This test |
| `tests/test_provenance_cli_api.py` | Test assumed every future local fixture was vendored | Audit complete fixture namespaces declared by origins, while retaining full vendor/deploy/origin audits; actual missing codec provenance remains a failure | This test |
| `tests/test_apply_clean.py` | Optional readback skip tested only surviving validation metadata, not absent bulk corpus/manifests | Skip the five optional readback tests with exact missing-input filenames | This test |
| `tests/labelfix/test_capture.py` | Sandbox denies loopback binding (`EPERM`) | Skip that server fixture with the specific environment reason; other capture tests pass | This test |
| `tests/test_ru1r3.py` | Shell wrapper overwrites `PYTHONPATH` with a different cleanup checkout, bypassing the test environment | Derive the repository root from the wrapper path; retain its existing interpreter and finalizer semantics | `scripts/secondary/ru1_finalize.sh` |
| Child-process tests across SR1/labelfix | Shared interpreter's editable install points at original worktree | Prepend this checkout to child `PYTHONPATH`; suppress bytecode writes | `tests/conftest.py` |

### CP7 import choice

A distinct **`cp7_common` binding** was chosen because putting CP7 first on `sys.path` cannot replace an unrelated `common` already in `sys.modules`. `cp7_common.py` explicitly loads the adjacent original `common.py` by file path and exports its public symbols. Both existing public `common.py` files retain their original behavior; CP7's original remains byte-for-byte intact for historical receipts. Receipt-pinned scanner copies were left intact.

These eleven CP7 files change only their helper import:

```text
build.py
finalize_geometry_cp7a3.py
freeze.py
measure.py
prepare_population_geometry.py
r2_common.py
recompute_gate_geometry.py
runtime.py
score_cp7b.py
verify_artifacts.py
verify_geometry_cp7a3.py
```

Those source-line edits necessarily invalidate old whole-file CP7 freeze hashes. The old freeze was deliberately not regenerated or bypassed.

### Scanner version retained

Before the fix, importing `tests/test_ru1s_scanner.py` caches `scripts/secondary/reading/scan_rollout.py` (v4.4) as top-level `scan_rollout`; the later `import scan_rollout` in `tests/test_scan_rollout.py` reuses it despite inserting the sol-reading directory first.

`git show opus/sol-reading:docs/records/harvest/sol_reading/tools/scan_rollout.py` and the integrated file have identical SHA-256:

```text
e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1
```

Thus no scanner implementation file needed replacing. Kept **opus/sol-reading v4.5.5** for the canonical tests, and **opus/secondary-corrections v4.4** for its historical RU1 tests/copies. The updated scanner tests and three added JSON fixtures were present in the sol-reading **working tree**, beyond the committed merged test version. They create the on-disk recorder required by v4.5.5, pass the reader directory to `answer_data`, and include the later overwrite/barrier probes. The canonical scanner alone passes **54 tests, 39 subtests**.

### Segmentation invocation and local prerequisites

Using the requested shared interpreter, collection from the segcensus repository root finds **23 tests** across `test_seg_small.py` and `test_seg_curve.py`; this is not a special alternate-root suite. That source worktree passes all 23. Here, missing `target/debug/greekocr-frozen-font-predict` was the dependency. The live native adapter and crop-tools implementation were byte-identical to `opus/seg-census` before the independent data-root adapters; no alternative segmenter behavior was selected. Baselines under `docs/records/harvest/seg_steps/` are present; after building both profiles, fresh old/current byte-identity comparisons pass without changing the segmenter or expected bytes. Cargo was available, so no native test was skipped.

Prepare the available archived fixtures and both predictor profiles:

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python tests/prepare_merge_fixtures.py --archive /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts --build-runtime
```

This checks existing destination bytes before writing missing files. It restored/verified **340 generated inputs**, including CP5 decompression with its existing recorded SHA-256. [TEST_FIXTURE_RECEIPT.json](TEST_FIXTURE_RECEIPT.json) lists every generated path, source, byte count and hash. These archive copies are local test data, **not source changes to commit as bulk artifacts**. The shared interpreter and external source records remain prerequisites for historical readbacks.

The build commands executed were:

```sh
cargo build --release --offline --manifest-path scripts/harvest/filter_runtime/Cargo.toml
cargo build --offline --manifest-path scripts/harvest/filter_runtime/Cargo.toml
```

## Commands and passing checks

Exact repaired integration-group command on the later working tree:

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_scan_rollout.py tests/test_ru1s_scanner.py tests/test_seg_small.py tests/test_seg_curve.py tests/test_r2_cards.py tests/adjudicate/test_owner_runtime.py tests/adjudicate/test_os5_owner_sheets.py tests/labelfix/test_capture.py
```

```text
137 passed, 1 skipped, 39 subtests passed in 22.84s
```

The single skip is sandbox loopback binding. An earlier, broader repaired group including N1 gate/ink tests passed `185 passed, 1 skipped, 39 subtests passed`; the later source hash changes are kept separate. `git diff --check` passes.

Exact full-suite command, run to completion:

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q -p no:cacheprovider --continue-on-collection-errors
```

This full command **does not pass**. There is no honest fully passing command to report without resolving the items below; the passing command above covers repaired integration paths, not a claim that the full suite is green.


Final qualification note: all runtime code fingerprints matched the start of the last full run. The independently authored `tests/test_data_root.py` changed after collection; its latest contents were checked separately: **11 passed in 1.58s**. The full-run summary refers to the collected suite; the qualification receipt records the one test-file mismatch explicitly.

## Remaining failures by file

| Test file (remaining nodes) | Cause | Disposition | CLEAN4T files changed |
|---|---|---|---|
| `tests/adjudicate/test_os2_owner_sheets.py` (2) | Archived owner HTML predates coordinator renderer CSS/mark changes. | Needs renderer/snapshot version ruling. | None; see repair table for imported helper/fixture changes |
| `tests/adjudicate/test_reemission.py` (2) | Old owner-card content/sequence differs under integrated renderer. | Needs renderer/output ruling; archived reference not regenerated. | None; see repair table for imported helper/fixture changes |
| `tests/labelfix/test_l1c.py` (1) | Strict no-package-import check rejects the concurrent data-root helper dependency, despite its stdlib-only implementation. | Needs dependency-contract ruling; no import guard weakened. | None; see repair table for imported helper/fixture changes |
| `tests/labelfix/test_policy_frozen_after_merge.py` (2) | SF7 binding and frozen reference checks reject integrated source hashes. | Needs accepted-source/binding ruling. | None; see repair table for imported helper/fixture changes |
| `tests/labelfix/test_s8_fetch_job.py` (2) | Mock/deadline subprocess exceeds bounded timeout in pool shutdown; source was identical to spellcheck before concurrent data-root edits. | Unresolved runtime/environment failure; no timeout inflation or tool change. | None; see repair table for imported helper/fixture changes |
| `tests/labelfix/test_sf1.py` (1) | Historical scoring receipt binds source hashes changed by the independent data-root adapters. | Needs frozen scorer-source ruling. | None; see repair table for imported helper/fixture changes |
| `tests/labelfix/test_sf7.py` (2) | Frozen SF7 preregistration/binding hashes differ from integrated sources. | Needs SF7 binding ruling; no expected hash updated. | None; see repair table for imported helper/fixture changes |
| `tests/labelfix/test_sf7_package.py` (1) | SF7 deployment checksum manifest rejects merged/adapted sources. | Needs package-source/binding ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_census3_secondary_scripts.py` (4) | Merged admission behavior differs from CENSUS3 secondary-class expectations. | Needs admission ruling; no policy/output changed. | None; see repair table for imported helper/fixture changes |
| `tests/test_collection_outputs.py` (3) | Budget ledgers and SHEETS.md referenced by historical collection receipts are unavailable locally. | Restore authoritative input archive; no replacement evidence fabricated. | None; see repair table for imported helper/fixture changes |
| `tests/test_cyrillic.py` (12) | Strict source registry rejects older synthetic archive_book records; T20 admission freeze also differs. | Needs admission/source-contract ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_lqb3.py` (1) | Receipt lookup path repaired; actual sourcing release-exclusion registry no longer matches frozen input. | Needs historical source/registry ruling; hash expectation retained. | `tests/test_lqb3.py` (path/fixture repair only) |
| `tests/test_lqb4.py` (1) | Merged sourcing registry already registers exclusions; old test expects 60 unregistered lines. | Needs registry snapshot/phase ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_lqb5.py` (1) | Historical receipt binds a different lqb.py source hash. | Needs source custody ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_mixed.py` (10) | Older tests supply source/wave combinations rejected by merged admission registry. | Needs admission/source-contract ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1cd.py` (1) | Real scratch reader pack lacks images named in its manifest (and any launcher failures are visible in full log). | Restore exact manifest-bound pack data; no reader output rewritten. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1r.py` (1) | Frozen rule source-input hashes differ after concurrent adapter edits; checkout-mtime assertion repaired. | Needs frozen-source ruling; rule data unchanged. | `tests/test_n1r.py` (path/fixture repair only) |
| `tests/test_n1r2.py` (1) | Scratch pack images are unavailable; any launcher regression is retained in full log. | Restore exact input images; no reconstruction claimed. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1t.py` (1) | Real reader-pack/canonical scanner custody no longer matches saved snapshot. | Needs pack/scanner snapshot ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1tb.py` (1) | Missing image in real pruned scratch pack; receipt owner-sheet path exception repaired. | Restore manifest-bound data. | `tests/test_n1tb.py` (path/fixture repair only) |
| `tests/test_n1ts2.py` (1) | Saved review/scan artifact assertions reflect a different historical tool/run phase. | Needs review/scan snapshot ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1ts3.py` (3) | Saved scan census has 45 entries while merged answers tree has 65 runs; missing pack provenance and historical review state. | Needs artifact census/run-phase ruling and exact input restoration. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1w1.py` (1) | Prepared-only assertion conflicts with answers already present in merged records. | Needs lifecycle/snapshot ruling; completed answers preserved. | None; see repair table for imported helper/fixture changes |
| `tests/test_n1w1_r3.py` (1) | Ready-only assertion conflicts with completed r3 answers already present. | Needs lifecycle/snapshot ruling; answers preserved. | None; see repair table for imported helper/fixture changes |
| `tests/test_openarchives_run.py` (1) | Older openarchives_r synthetic source is rejected by current provenance-bound registry. | Needs source-registry ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_provenance_cli_api.py` (6) | Vendor origin hashes differ; codec/v2.json lacks origin entry; generated API docs omit merged public symbols. | Needs verified origin/source and API documentation reconciliation; no provenance invented. | `tests/test_provenance_cli_api.py` (path/fixture repair only) |
| `tests/test_ru12.py` (3) | Saved RU1 manifest/scanner/owner-sheet expectations differ from integrated artifacts and renderer. | Needs RU1 artifact/renderer snapshot ruling. | None; see repair table for imported helper/fixture changes |
| `tests/test_seg_cp7c.py` (5) | Whole-file freeze differs; packs are post-read, run_r2.log exists, and sealed archive mode is 0644 after checkout rather than 0600. | Needs frozen-source/lifecycle ruling; do not delete evidence or rewrite freeze. | None; see repair table for imported helper/fixture changes |
| `tests/test_seg_cp7c_score_fixtures.py` (1) | Standalone preflight correctly rejects old freeze against changed import/source files. | Needs an explicitly reviewed new binding or historical snapshot strategy. | None; see repair table for imported helper/fixture changes |
| `tests/test_seg_cp7d.py` (1) | Original-binding verification correctly rejects integrated source drift. | Needs frozen-source ruling. | None; see repair table for imported helper/fixture changes |

## Needs a ruling

1. **Admission/source contracts:** CENSUS3 secondary classes and older Cyrillic/mixed/OpenArchives records disagree with the merged source registry/decision behavior. Select the accepted contract before changing tools or expected outputs.
2. **SF7 and historical source bindings:** merged policy/reference/deployment sources do not match frozen SF6c/SF7 hashes. The separate data-root changes add further whole-file hash drift. Do not update expected hashes without deciding which implementation is accepted.
3. **CP7 frozen source and run phase:** import-only repairs change frozen file hashes; prepared-only tests inspect completed packs/logs, and checkout does not preserve a 0600 sealed-file mode. Decide how historical freeze/pre-read tests should be isolated from completed records. No answer/log was removed and no freeze was bypassed.
4. **Owner renderer:** coordinator renderer adds CSS/mark behavior compared with cleanup HTML/reference fixtures. Decide which snapshot contract applies before re-emitting reviewed HTML or weakening comparisons.
5. **LQB/N1/RU1 historical custody:** current release registry, adapted source hashes, scanner identities, and merged run census differ from saved receipt snapshots. The file table and node list identify each assertion; source/data expectations remain visible.
6. **Vendor provenance/API:** accepted merged vendor sources need reconciled origin records; codec v2 currently has no origin entry and API docs lag merged public symbols. No new provenance entry was invented.

## Unresolved inputs and environment

- Missing manifest-bound scratch-pack images and historical wave budget/sheet inputs remain unresolved. The complete log retains exact paths and errors; available archive restorations are individually hashed in the fixture receipt.
- S8 mock/deadline pool-shutdown timeouts remain visible. Neither the tool nor test timeout was changed.
- The loopback-server test skips on this sandbox's EPERM. Five optional collection-v2 readback tests skip because the bulk corpus/manifests are absent, listing their exact filenames. These skips are not claims that those physical readbacks passed.

## Final failure node list

```text
tests/adjudicate/test_os2_owner_sheets.py::test_os2_offline_render_native_images_and_identity[failure_modes_per_class]
tests/adjudicate/test_os2_owner_sheets.py::test_os2_offline_render_native_images_and_identity[segmentation_failures]
tests/adjudicate/test_reemission.py::test_owner_content_and_pixels[reader_errors_heldout-39]
tests/adjudicate/test_reemission.py::test_owner_content_and_pixels[accent_corrections_checked-100]
tests/labelfix/test_l1c.py::test_no_gate_reader_or_detector_imports
tests/labelfix/test_policy_frozen_after_merge.py::test_policy_binding_remains_sf6c
tests/labelfix/test_policy_frozen_after_merge.py::test_greekocr_sha256_list_matches_spellcheck
tests/labelfix/test_s8_fetch_job.py::test_exact_job_entrypoint_mock
tests/labelfix/test_s8_fetch_job.py::test_deadline_terminates_inflight_pool
tests/labelfix/test_sf1.py::test_rescoring_receipt_and_current_note_sets_bound
tests/labelfix/test_sf7.py::test_sf6_full_outputs_identical_after_sf7_import
tests/labelfix/test_sf7.py::test_binding_is_additive_and_preregistered
tests/labelfix/test_sf7_package.py::test_exact_entrypoint_and_sf6_release_schema
tests/test_census3_secondary_scripts.py::test_secondary_words[\u042d\u0442\u043e
tests/test_census3_secondary_scripts.py::test_secondary_words[This
tests/test_census3_secondary_scripts.py::test_secondary_words[This
tests/test_census3_secondary_scripts.py::test_existing_mixed_class_and_greek_policy_unchanged
tests/test_collection_outputs.py::test_provenance_sums_all_wave_budgets
tests/test_collection_outputs.py::test_frozen_wave_inputs_remain_unchanged
tests/test_collection_outputs.py::test_sheet_index_lists_every_existing_admission_image
tests/test_cyrillic.py::test_cyrillic_class[\u0420\u0443\u0441\u0441\u043a\u0430\u044f
tests/test_cyrillic.py::test_cyrillic_class[\u0411\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438
tests/test_cyrillic.py::test_cyrillic_class[\u0421\u0440\u043f\u0441\u043a\u0438
tests/test_cyrillic.py::test_mixed_script_word_drops_line[\u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446a]
tests/test_cyrillic.py::test_mixed_script_word_drops_line[\u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u03b1]
tests/test_cyrillic.py::test_mixed_script_word_drops_line[\u0411\u044a\u043b\u0433a\u0440\u0441\u043a\u0438]
tests/test_cyrillic.py::test_mixed_script_word_drops_line[\u0421\u0440\u043f\u0441\u043a\u03b1]
tests/test_cyrillic.py::test_latin_byproduct_kept_on_cyrillic_page
tests/test_cyrillic.py::test_page_exclusion_appends_every_t20_failure
tests/test_cyrillic.py::test_page_rejects_clean_line
tests/test_cyrillic.py::test_o5_and_page_exclusion_together
tests/test_cyrillic.py::test_frozen_t20_module
tests/test_lqb3.py::test_v2_source_hashes_and_outputs
tests/test_lqb4.py::test_new_exclusions_respect_all_classes_and_dev_ruling
tests/test_lqb5.py::test_all_version_and_output_custody
tests/test_mixed.py::test_o5_uses_every_previous_holdout_source[anemi_round1]
tests/test_mixed.py::test_o5_uses_every_previous_holdout_source[vouli_parliament_1850s]
tests/test_mixed.py::test_o5_uses_every_previous_holdout_source[anemi_round2]
tests/test_mixed.py::test_o5_uses_every_previous_holdout_source[parliament_1975_2000]
tests/test_mixed.py::test_o5_uses_every_previous_holdout_source[openarchives_repo]
tests/test_mixed.py::test_current_holdout_blocks_new_and_prior_train[A-anemi_mixed]
tests/test_mixed.py::test_current_holdout_blocks_new_and_prior_train[B-openarchives_mixed_repo]
tests/test_mixed.py::test_current_holdout_blocks_new_and_prior_train[C-archive_b28038630]
tests/test_mixed.py::test_mixed_classes_follow_unchanged_t20_majority[\u03a4\u03bf
tests/test_mixed.py::test_mixed_classes_follow_unchanged_t20_majority[This
tests/test_n1cd.py::test_real_pack_coverage_and_v3_images
tests/test_n1r.py::test_frozen_artifact_and_document_split
tests/test_n1r2.py::test_real_reverse_fresh_ids_permutations_controls_and_hashes
tests/test_n1t.py::test_real_dash_sheet_assignments_original_cells_and_custody
tests/test_n1tb.py::test_real_pruned_pack_coverage_controls_failure_and_independence
tests/test_n1ts2.py::test_actual_r3_coverage_fresh_ids_controls_and_completed_reading
tests/test_n1ts3.py::test_all_scans_reconciled_and_no_new_voids
tests/test_n1ts3.py::test_actual_combination_authority_and_independence
tests/test_n1ts3.py::test_review_sheets_complete_and_templates_unfilled
tests/test_n1w1.py::test_prepared_population_and_pack_accounting
tests/test_n1w1_r3.py::test_ready_artifacts_are_complete
tests/test_openarchives_run.py::test_admission_checks_prior_holdouts_and_retains_metadata_repository
tests/test_provenance_cli_api.py::test_every_vendor_file_has_origin_and_exact_bytes[greekocr/_vendor/bench/common.py]
tests/test_provenance_cli_api.py::test_every_vendor_file_has_origin_and_exact_bytes[greekocr/_vendor/bench/e1_common.py]
tests/test_provenance_cli_api.py::test_every_vendor_file_has_origin_and_exact_bytes[greekocr/_vendor/bench/e1_readout.py]
tests/test_provenance_cli_api.py::test_every_vendor_file_has_origin_and_exact_bytes[greekocr/_vendor/train/mix.py]
tests/test_provenance_cli_api.py::test_all_vendored_files_are_in_inventory
tests/test_provenance_cli_api.py::test_public_callables_typed_and_documented
tests/test_ru12.py::test_manifest_hashes_and_controls
tests/test_ru12.py::test_owner_structure_and_size
tests/test_ru12.py::test_owner_seed_geometry_and_holds
tests/test_seg_cp7c.py::test_freeze_binding_list
tests/test_seg_cp7c.py::test_pack_closure_opacity_crop_shas_and_controls[segcp7r2_a]
tests/test_seg_cp7c.py::test_pack_closure_opacity_crop_shas_and_controls[segcp7r2_b]
tests/test_seg_cp7c.py::test_scanner_prompt_and_launcher
tests/test_seg_cp7c.py::test_frozen_gate_and_seal
tests/test_seg_cp7c_score_fixtures.py::test_standalone_launcher_preflight_from_unrelated_directory
tests/test_seg_cp7d.py::test_original_bindings_verified
```

Full final output: [TESTS_AFTER_MERGE.final.log](TESTS_AFTER_MERGE.final.log).
Qualification/source fingerprints: [TESTS_AFTER_MERGE.qualification.json](TESTS_AFTER_MERGE.qualification.json).
