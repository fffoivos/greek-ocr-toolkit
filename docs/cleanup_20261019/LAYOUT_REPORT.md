# CLEAN4L — documentation layout report

Completed 19 October 2026 in `cleanup/20261019`. Initial inspected HEAD: `296a72ad12731314fcc1ba6c903071291822a2a3`. All moves used plain `mv` with `mkdir -p`; file edits and empty-directory `rmdir` were confined to documentation, with root `README.md` navigation updated as requested. No git writing command was issued. No edits or removals were made under root `greekocr/`, `scripts/` or `tests/`; bytecode writes were disabled for testing. Another run may change those trees concurrently.

## Result

- Installed all 24 supplied A/B files in final homes, removed their provisional wording, and added the B overview, shared infrastructure index and records index. Root/documentation entry points now expose the owner taxonomy.
- Executed **130 file/subtree moves covering 35,314 files**. Every pre-existing documentation file remains present at its mapped destination; no file was deleted.
- Preserved the superseded pipeline README/graph in `docs/records/harvest/line_pipeline_legacy/`. The live old README and graph now contain the corrected content, with a one-line canonical-home pointer at the top. Relative links in the compatibility README are rebased to the new Google/pipeline guides.
- Moved the human-review contract and demo together to B.d; `docs/review/HUMAN_REVIEW_SHEETS.md` is a one-line pointer. `reference_scratch/` stays in its existing home.
- `docs/harvest/line_pipeline/` keeps its other assets, including `tool_versions.json`; `docs/harvest/seg_census/package/` stays in place. `docs/origins/` and `docs/verify/` stay shared. All snapshotted files in these last three trees retain exact hashes.
- Root O4D JSON and GLYPHS JSON/Markdown, including the lowercase glyph fixture/inspection JSON, are grouped under glyph records. Other root JSON/XML verification snapshots moved to `verify_20261008/`; no root JSON/XML remains.

## Move table

Directory rows include all descendants. Paths below are repository-relative. This table also translates the old paths retained in historical machine-readable custody receipts.

| Old | New |
|---|---|
| `docs/cleanup_20261019/drafts/A` | `docs/A_ocr_development` |
| `docs/cleanup_20261019/drafts/B_ac/a_google_ocr` | `docs/B_training_data/a_google_ocr` |
| `docs/cleanup_20261019/drafts/B_ac/c_pipeline` | `docs/B_training_data/c_pipeline` |
| `docs/cleanup_20261019/drafts/B_b` | `docs/B_training_data/b_tools` |
| `docs/cleanup_20261019/drafts/B_d` | `docs/B_training_data/d_review` |
| `docs/harvest/COLLECTION_PLAN_v1.md` | `docs/records/harvest/COLLECTION_PLAN_v1.md` |
| `docs/harvest/DOCAI_FAILED_LINES_v1.md` | `docs/records/harvest/DOCAI_FAILED_LINES_v1.md` |
| `docs/harvest/MONTAGE_v1.md` | `docs/records/harvest/MONTAGE_v1.md` |
| `docs/harvest/PAGE_READS_v1.md` | `docs/records/harvest/PAGE_READS_v1.md` |
| `docs/harvest/PILOT_v1.md` | `docs/records/harvest/PILOT_v1.md` |
| `docs/harvest/SOL_ROUTING_sourcing_20261017.md` | `docs/records/harvest/SOL_ROUTING_sourcing_20261017.md` |
| `docs/harvest/THREE_ENGINES_v1.md` | `docs/records/harvest/THREE_ENGINES_v1.md` |
| `docs/harvest/VISION_VS_DOCAI_v1.md` | `docs/records/harvest/VISION_VS_DOCAI_v1.md` |
| `docs/harvest/analysis` | `docs/records/harvest/analysis` |
| `docs/harvest/blind_checks_v1` | `docs/records/harvest/blind_checks_v1` |
| `docs/harvest/collect_v3` | `docs/records/harvest/collect_v3` |
| `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `docs/harvest/collection` | `docs/records/harvest/collection` |
| `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `docs/harvest/docai_failed_lines` | `docs/records/harvest/docai_failed_lines` |
| `docs/harvest/docai_failed_lines_review.html` | `docs/records/harvest/docai_failed_lines_review.html` |
| `docs/harvest/fix1` | `docs/records/harvest/fix1` |
| `docs/harvest/fix2` | `docs/records/harvest/fix2` |
| `docs/harvest/funnel_v1` | `docs/records/harvest/funnel_v1` |
| `docs/harvest/inventory_v2` | `docs/records/harvest/inventory_v2` |
| `docs/harvest/mixed` | `docs/records/harvest/mixed` |
| `docs/harvest/montage_review.html` | `docs/records/harvest/montage_review.html` |
| `docs/harvest/montage_v1` | `docs/records/harvest/montage_v1` |
| `docs/harvest/oa_rebind_v1` | `docs/records/harvest/oa_rebind_v1` |
| `docs/harvest/openarchives` | `docs/records/harvest/openarchives` |
| `docs/harvest/page_reads_v1` | `docs/records/harvest/page_reads_v1` |
| `docs/harvest/parliament` | `docs/records/harvest/parliament` |
| `docs/harvest/pilot_v1` | `docs/records/harvest/pilot_v1` |
| `docs/harvest/pilots_v2` | `docs/records/harvest/pilots_v2` |
| `docs/harvest/recut_v1` | `docs/records/harvest/recut_v1` |
| `docs/harvest/round1` | `docs/records/harvest/round1` |
| `docs/harvest/round2` | `docs/records/harvest/round2` |
| `docs/harvest/sample_v1` | `docs/records/harvest/sample_v1` |
| `docs/harvest/screen_v1` | `docs/records/harvest/screen_v1` |
| `docs/harvest/seg_census/.gitignore` | `docs/records/harvest/seg_census/.gitignore` |
| `docs/harvest/seg_census/COMMIT_LIST.md` | `docs/records/harvest/seg_census/COMMIT_LIST.md` |
| `docs/harvest/seg_census/DEPLOY_PATHS.txt` | `docs/records/harvest/seg_census/DEPLOY_PATHS.txt` |
| `docs/harvest/seg_census/DEPLOY_SHA256SUMS` | `docs/records/harvest/seg_census/DEPLOY_SHA256SUMS` |
| `docs/harvest/seg_census/FOLLOW_UP.md` | `docs/records/harvest/seg_census/FOLLOW_UP.md` |
| `docs/harvest/seg_census/HANDOFF_SEGCENSUS1.md` | `docs/records/harvest/seg_census/HANDOFF_SEGCENSUS1.md` |
| `docs/harvest/seg_census/JOB_KINDS.md` | `docs/records/harvest/seg_census/JOB_KINDS.md` |
| `docs/harvest/seg_census/OUT_OF_GIT_RECEIPT.md` | `docs/records/harvest/seg_census/OUT_OF_GIT_RECEIPT.md` |
| `docs/harvest/seg_census/SOURCE_CAPTURE.md` | `docs/records/harvest/seg_census/SOURCE_CAPTURE.md` |
| `docs/harvest/seg_census/b2_evidence` | `docs/records/harvest/seg_census/b2_evidence` |
| `docs/harvest/seg_census/byte_identity_1c.json` | `docs/records/harvest/seg_census/byte_identity_1c.json` |
| `docs/harvest/seg_census/capture_inventory.json` | `docs/records/harvest/seg_census/capture_inventory.json` |
| `docs/harvest/seg_census/capture_paths.txt` | `docs/records/harvest/seg_census/capture_paths.txt` |
| `docs/harvest/seg_census/census04_config.json` | `docs/records/harvest/seg_census/census04_config.json` |
| `docs/harvest/seg_census/compare_suites.py` | `docs/records/harvest/seg_census/compare_suites.py` |
| `docs/harvest/seg_census/final_package_tests.log` | `docs/records/harvest/seg_census/final_package_tests.log` |
| `docs/harvest/seg_census/finalize_package.py` | `docs/records/harvest/seg_census/finalize_package.py` |
| `docs/harvest/seg_census/full_baseline.log` | `docs/records/harvest/seg_census/full_baseline.log` |
| `docs/harvest/seg_census/full_baseline.xml` | `docs/records/harvest/seg_census/full_baseline.xml` |
| `docs/harvest/seg_census/full_current.log` | `docs/records/harvest/seg_census/full_current.log` |
| `docs/harvest/seg_census/full_current.xml` | `docs/records/harvest/seg_census/full_current.xml` |
| `docs/harvest/seg_census/full_tests_1c.log` | `docs/records/harvest/seg_census/full_tests_1c.log` |
| `docs/harvest/seg_census/full_tests_1c_deselected.log` | `docs/records/harvest/seg_census/full_tests_1c_deselected.log` |
| `docs/harvest/seg_census/integration_tests.log` | `docs/records/harvest/seg_census/integration_tests.log` |
| `docs/harvest/seg_census/jobs` | `docs/records/harvest/seg_census/jobs` |
| `docs/harvest/seg_census/mock_batch.log` | `docs/records/harvest/seg_census/mock_batch.log` |
| `docs/harvest/seg_census/mock_batch.py` | `docs/records/harvest/seg_census/mock_batch.py` |
| `docs/harvest/seg_census/mock_batch_results.json` | `docs/records/harvest/seg_census/mock_batch_results.json` |
| `docs/harvest/seg_census/mock_segmentation.py` | `docs/records/harvest/seg_census/mock_segmentation.py` |
| `docs/harvest/seg_census/mock_split_stage.log` | `docs/records/harvest/seg_census/mock_split_stage.log` |
| `docs/harvest/seg_census/mock_split_stage.py` | `docs/records/harvest/seg_census/mock_split_stage.py` |
| `docs/harvest/seg_census/mock_split_stage_results.json` | `docs/records/harvest/seg_census/mock_split_stage_results.json` |
| `docs/harvest/seg_census/mock_stage.log` | `docs/records/harvest/seg_census/mock_stage.log` |
| `docs/harvest/seg_census/mock_stage_1c3.log` | `docs/records/harvest/seg_census/mock_stage_1c3.log` |
| `docs/harvest/seg_census/mock_stage_results.json` | `docs/records/harvest/seg_census/mock_stage_results.json` |
| `docs/harvest/seg_census/package_changes.patch` | `docs/records/harvest/seg_census/package_changes.patch` |
| `docs/harvest/seg_census/package_composition.json` | `docs/records/harvest/seg_census/package_composition.json` |
| `docs/harvest/seg_census/package_id.json` | `docs/records/harvest/seg_census/package_id.json` |
| `docs/harvest/seg_census/package_paths.txt` | `docs/records/harvest/seg_census/package_paths.txt` |
| `docs/harvest/seg_census/package_tests.log` | `docs/records/harvest/seg_census/package_tests.log` |
| `docs/harvest/seg_census/package_tests_complete.log` | `docs/records/harvest/seg_census/package_tests_complete.log` |
| `docs/harvest/seg_census/package_tests_correct.log` | `docs/records/harvest/seg_census/package_tests_correct.log` |
| `docs/harvest/seg_census/package_tests_final.log` | `docs/records/harvest/seg_census/package_tests_final.log` |
| `docs/harvest/seg_census/parity_check.py` | `docs/records/harvest/seg_census/parity_check.py` |
| `docs/harvest/seg_census/prepare_config.py` | `docs/records/harvest/seg_census/prepare_config.py` |
| `docs/harvest/seg_census/pristine_collection_1c.log` | `docs/records/harvest/seg_census/pristine_collection_1c.log` |
| `docs/harvest/seg_census/pristine_collection_1c3.log` | `docs/records/harvest/seg_census/pristine_collection_1c3.log` |
| `docs/harvest/seg_census/receipt.json` | `docs/records/harvest/seg_census/receipt.json` |
| `docs/harvest/seg_census/receipt_b2.json` | `docs/records/harvest/seg_census/receipt_b2.json` |
| `docs/harvest/seg_census/remote_evidence` | `docs/records/harvest/seg_census/remote_evidence` |
| `docs/harvest/seg_census/remote_snapshot_hashes.json` | `docs/records/harvest/seg_census/remote_snapshot_hashes.json` |
| `docs/harvest/seg_census/snapshot_diffs` | `docs/records/harvest/seg_census/snapshot_diffs` |
| `docs/harvest/seg_census/source_capture` | `docs/records/harvest/seg_census/source_capture` |
| `docs/harvest/seg_census/source_capture.json` | `docs/records/harvest/seg_census/source_capture.json` |
| `docs/harvest/seg_census/source_conflicts.patch` | `docs/records/harvest/seg_census/source_conflicts.patch` |
| `docs/harvest/seg_census/split_input.schema.json` | `docs/records/harvest/seg_census/split_input.schema.json` |
| `docs/harvest/seg_census/suite_comparison.json` | `docs/records/harvest/seg_census/suite_comparison.json` |
| `docs/harvest/seg_census/tests` | `docs/records/harvest/seg_census/tests` |
| `docs/harvest/seg_census/verifier_allow_untracked.txt` | `docs/records/harvest/seg_census/verifier_allow_untracked.txt` |
| `docs/harvest/seg_steps` | `docs/records/harvest/seg_steps` |
| `docs/harvest/sol_reading` | `docs/records/harvest/sol_reading` |
| `docs/harvest/transkribus_failed_lines` | `docs/records/harvest/transkribus_failed_lines` |
| `docs/harvest/vision_failed_lines` | `docs/records/harvest/vision_failed_lines` |
| `docs/harvest/vouli` | `docs/records/harvest/vouli` |
| `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `docs/harvest/wikisource_r0` | `docs/records/harvest/wikisource_r0` |
| `docs/labelfix` | `docs/records/labelfix` |
| `docs/reviews` | `docs/records/reviews` |
| `docs/briefs` | `docs/records/briefs` |
| `docs/research` | `docs/records/research` |
| `docs/tables` | `docs/records/tables` |
| `docs/GLYPHS_CALIBRATION.md` | `docs/records/glyphs/GLYPHS_CALIBRATION.md` |
| `docs/GLYPHS_PLAN.md` | `docs/records/glyphs/GLYPHS_PLAN.md` |
| `docs/GLYPHS_STATE.json` | `docs/records/glyphs/GLYPHS_STATE.json` |
| `docs/O4D_G1_measure_v1.json` | `docs/records/glyphs/O4D_G1_measure_v1.json` |
| `docs/O4D_G1_measure_v2.json` | `docs/records/glyphs/O4D_G1_measure_v2.json` |
| `docs/O4D_G1_validation_v2.json` | `docs/records/glyphs/O4D_G1_validation_v2.json` |
| `docs/O4D_G1_validation_v3.json` | `docs/records/glyphs/O4D_G1_validation_v3.json` |
| `docs/T6_VENDOR_UPDATE.json` | `docs/records/verify_20261008/T6_VENDOR_UPDATE.json` |
| `docs/glyphs_fixture_labels.json` | `docs/records/glyphs/glyphs_fixture_labels.json` |
| `docs/glyphs_shown_batches.json` | `docs/records/glyphs/glyphs_shown_batches.json` |
| `docs/pytest-results.xml` | `docs/records/verify_20261008/pytest-results.xml` |
| `docs/t4-pytest-results.xml` | `docs/records/verify_20261008/t4-pytest-results.xml` |
| `docs/t6-pytest-results.xml` | `docs/records/verify_20261008/t6-pytest-results.xml` |
| `docs/t6-scoped-pytest-results.xml` | `docs/records/verify_20261008/t6-scoped-pytest-results.xml` |
| `docs/t8-pytest-results.xml` | `docs/records/verify_20261008/t8-pytest-results.xml` |
| `docs/validation.json` | `docs/records/verify_20261008/validation.json` |
| `docs/review/HUMAN_REVIEW_SHEETS.md` | `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md` |
| `docs/review/demo` | `docs/B_training_data/d_review/demo` |
| `docs/harvest/line_pipeline/README.md` | `docs/records/harvest/line_pipeline_legacy/README.md` |
| `docs/harvest/line_pipeline/pipeline.mmd` | `docs/records/harvest/line_pipeline_legacy/pipeline.mmd` |

## Links fixed

- Checked **21,452** parsed local Markdown/reference/HTML link occurrences from the pre-move snapshot, including **6,688** previously resolving occurrences. Every previously resolving occurrence retains its mapped target; **zero relocation regressions**. The parser checks file targets; it does not certify external websites or Markdown fragment anchors.
- Updated **2,236 destination occurrences**; exact old/new page and target pairs are in [LAYOUT_LINK_FIXES.tsv](LAYOUT_LINK_FIXES.tsv). These include rebasing links out of moved records to repository code and sibling worktrees, updating links from stationary pages, and preserving links between moved siblings.
- **685 existing text files** changed for navigation/path references and final A/B wording; see [LAYOUT_EDITED_FILES.tsv](LAYOUT_EDITED_FILES.tsv). Repository-root `docs/...` mentions were searched across documentation and root README; zero stale standalone references to relocated paths remain outside frozen packages and this intentional move record.
- All direct static file links in the installed A/B guides, new shared index and records index resolve. A/B final documents contain no provisional wording. JSON receipts, inventories, manifests, code snapshots, scripts, logs and checksums retain historical path identities; their retrieval map is the table above plus the existing data-out manifest.

## Directories created

New documentation-home and records paths (including renamed directory roots):

- `docs/A_ocr_development/`
- `docs/A_ocr_development/segmenters/`
- `docs/B_training_data/`
- `docs/B_training_data/a_google_ocr/`
- `docs/B_training_data/b_tools/`
- `docs/B_training_data/c_pipeline/`
- `docs/B_training_data/d_review/`
- `docs/shared/`
- `docs/records/harvest/`
- `docs/records/harvest/seg_census/`
- `docs/records/harvest/line_pipeline_legacy/`
- `docs/records/labelfix/`
- `docs/records/reviews/`
- `docs/records/briefs/`
- `docs/records/research/`
- `docs/records/tables/`
- `docs/records/glyphs/`
- `docs/records/verify_20261008/`

Nested record subdirectories were relocated intact with their parent trees. The exact `mkdir -p` parent paths newly materialised by the move phase were `docs/B_training_data/`, `docs/records/harvest/`, `docs/records/harvest/seg_census/`, `docs/records/glyphs/`, `docs/records/verify_20261008/`, `docs/records/harvest/line_pipeline_legacy/`; `docs/shared/` was added for its new index.

## Files and empty directories removed

**Files removed: none.** Old paths in the move table are renames; the two superseded pipeline files were preserved before replacement.

Removed only these newly empty documentation directories:

- `docs/cleanup_20261019/drafts/B_ac/`
- `docs/cleanup_20261019/drafts/`

`greekocr/lines`, `scripts/lines` and `docs/lines` were already absent on first inspection. This run did not remove them again. The 91 previously removed empty directories belong to the preceding cleanup run. `build/`, `dist/` and egg-info were untouched.

## Requested tests

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_size_guard.py tests/test_provenance_cli_api.py
```

**1,109 passed, 4 skipped in 3.56s.** All four skips are the existing historical vendor bindings, with the reason pointing to `TEST_RECORDS.md`. The size guard passed against the current index; no index mutation was performed. The provenance/API suite also passed. Full output and the first-attempt environment failure are in [LAYOUT_TESTS.log](LAYOUT_TESTS.log).

The shell has no `python` command. Its default `python3` initially failed session setup (1,109 errors, 4 skips) because installed Torch dylibs are x86_64 while the interpreter is arm64. The retry used the existing shared interpreter named in `TEST_RECORDS.md`; no dependency installation, fixture bypass or test edits were needed.

## Open issues and boundaries

- The baseline parser found **14,764 already unresolved local/template references**. Many refer to bulk artifacts already moved out, optional/private worktree evidence or captured website paths. This pass preserves their destination identity and fixes relocation links; it does not recreate missing data. No claim is made that every historical sheet or external reference is now self-contained.
- Historical JSON receipts and reproduction scripts retain original paths and hashes. A consumer hardcoding a relocated documentation/evidence path must consult this move map or the data-out manifest; changing runtime callers was outside this docs-only task. The live deployment package is deliberately frozen.
- A/B source inspections and scientific claims remain dated to the heads named in those documents. Concurrent runtime changes, pipeline discrepancies, candidate adoption and population qualification were not re-audited by layout work.
- No commit, staging, push, merge, launch or publication was performed. Rename detection is left to the later commit.
