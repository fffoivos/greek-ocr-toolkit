# CLEAN4L3 — test paths after documentation layout

Workspace: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next`, branch `cleanup/20261019`. Completed 20 October 2026. The retrieval map is [LAYOUT_REPORT.md](LAYOUT_REPORT.md).

Updated local literal paths in `tests/`, `scripts/`, and `greekocr/`, including dynamically assembled wave-record paths. The table below records 374 file/path mappings. Repeated segmentation and scanner bases use `tests/_paths.py` (`ADMISSION`, `SOL_READING`, `SEG_STEPS`). `greekocr.ops.data_root` holds the exact 130 move-table aliases, searches repository copies before external mirrors, and still identifies the original custody shard for a missing relocated input.

No documentation was moved, no symlinks were added, and no Git-writing command was issued. This task did not edit root `README.md` or `AGENTS.md`; concurrent CLEAN5E changes to those files were left alone. No existing documentation, JSON receipt, manifest, fixture JSON/JSONL, vendor source snapshot, or saved checksum/hash value was changed. The only documentation written by this task is this report.

Executable documentation fixtures remain byte-identical on disk. A test-only loader translates local path literals and former repository-root parent calculations in memory. It bypasses the historical `__pycache__` objects moved with those fixtures; it neither updates nor deletes those caches. `run_record` applies the same adapter to explicit script execution. Tool decision logic is unchanged.

Two path-sensitive checks need additional explanation. CP7 runtime checks compare the same receipt-relative suffix under its new directory using copies of the receipt dictionaries, preserving every hash value. CP1 gate-mechanics tests use a temporary current-ledger fixture because CLEAN4L also rebased links inside two source briefs; the original ledger, its historical hashes, and truth remain untouched. The temporary fixture binds the actual current source bytes and retains the union-failure and no-side-effect assertions; it does not qualify the historical receipt.

Explicit sibling-worktree paths retain their original layout: CLEAN4L moved this workspace's documentation, not those source checkouts. Unmoved `docs/harvest/harvest_big`, pipeline assets, and synthetic non-relocated paths also retain their identities. Old strings in custody/origin JSON, frozen vendor Rust comments, the alias map, and historical-path resolver tests are intentional. No local executable-source lookup remains at a relocated old literal path outside those explicitly external or frozen identities.

All 19 historical-binding skip decorators in edited test files match the branch base exactly. No test was converted to a historical record because evidence moved. Truly absent inputs use the exact filename as their skip reason. Parameterized evidence that cannot be loaded at collection time has an explicit missing-file skip parameter; synthetic tests from those modules still run. This changes the collected parameter count when a bulk input is absent and does not assert that missing evidence was restored or verified.

## Path changes

Directory mappings include their descendants; the shared helper supplies the destination when a caller no longer repeats its full literal.

| Test/script/code | Old path | New path |
|---|---|---|
| `greekocr/adjudicate/README.md` | `docs/review/HUMAN_REVIEW_SHEETS.md` | `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md` |
| `greekocr/glyphs/baseline.py` | `docs/GLYPHS_PLAN.md` | `docs/records/glyphs/GLYPHS_PLAN.md` |
| `greekocr/glyphs/lines_api.py` | `docs/GLYPHS_CALIBRATION.md` | `docs/records/glyphs/GLYPHS_CALIBRATION.md` |
| `greekocr/glyphs/readability.py` | `docs/GLYPHS_CALIBRATION.md` | `docs/records/glyphs/GLYPHS_CALIBRATION.md` |
| `greekocr/harvest/admission.py` | `docs/briefs` | `docs/records/briefs` |
| `greekocr/harvest/admission.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `greekocr/harvest/application_identity.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `greekocr/harvest/cli.py` | `docs/harvest/pilot_v1` | `docs/records/harvest/pilot_v1` |
| `greekocr/harvest/collection.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `greekocr/harvest/neighbour_words.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `greekocr/harvest/numeric_cells.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `greekocr/harvest/qualified_admission.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `greekocr/harvest/regate.py` | `docs/harvest/pilot_v1` | `docs/records/harvest/pilot_v1` |
| `greekocr/labelfix/__init__.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/build_lexicon.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `greekocr/labelfix/build_lexicon.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/case.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/deck.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/deck_serve.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/ingest_decisions.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/lqb.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/markshape_train.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/pull_firefox.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/reach.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/sample.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `greekocr/labelfix/sample.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/sheet.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/spellcheck_validate.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `greekocr/labelfix/spellcheck_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/textstage.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `greekocr/labelfix/textstage.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/labelfix/validate.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `greekocr/labelfix/validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `greekocr/ops/data_root.py` | `all 130 move-table identities` | `mapped destinations; historical aliases retained for custody receipts and data mirrors` |
| `greekocr/pages/statistics.py` | `docs/reviews` | `docs/records/reviews` |
| `greekocr/readers/services/google_vision.py` | `docs/harvest/vision_failed_lines` | `docs/records/harvest/vision_failed_lines` |
| `scripts/glyphs/README.md` | `docs/glyphs_fixture_labels.json` | `docs/records/glyphs/glyphs_fixture_labels.json` |
| `scripts/glyphs/archive/annotate_tables_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/audit_orientation_guides.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/audit_tables_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/evaluate_tables_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/generate_orientation_guides.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/integrate_docling_tables_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/report_orientation_guides.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/report_orientation_round4.py` | `docs/research` | `docs/records/research` |
| `scripts/glyphs/archive/report_orientation_round4.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/report_orientation_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/report_tables_round4.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/report_tables_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/review_line_boundaries.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/review_line_structure.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/review_line_structure.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/review_page_lines_round3.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/review_page_lines_round4_nontable.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/review_page_lines_round4_nontable.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/review_statistics.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/archive/score_tables_round4.py` | `docs/tables` | `docs/records/tables` |
| `scripts/glyphs/archive/summarize_page_line_review.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/glyphs/build_review_data.py` | `docs/glyphs_shown_batches.json` | `docs/records/glyphs/glyphs_shown_batches.json` |
| `scripts/glyphs/calib/README.md` | `docs/GLYPHS_CALIBRATION.md` | `docs/records/glyphs/GLYPHS_CALIBRATION.md` |
| `scripts/glyphs/eval/fixture_double.py` | `docs/glyphs_fixture_labels.json` | `docs/records/glyphs/glyphs_fixture_labels.json` |
| `scripts/glyphs/run_review.sh` | `docs/GLYPHS_PLAN.md` | `docs/records/glyphs/GLYPHS_PLAN.md` |
| `scripts/glyphs/run_review.sh` | `docs/GLYPHS_STATE.json` | `docs/records/glyphs/GLYPHS_STATE.json` |
| `scripts/glyphs/run_review.sh` | `docs/reviews` | `docs/records/reviews` |
| `scripts/harvest/admit_round1.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/apply_clean.py` | `docs/harvest/analysis` | `docs/records/harvest/analysis` |
| `scripts/harvest/apply_clean.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/clariden/package.py` | `docs/harvest/line_pipeline/README.md` | `docs/records/harvest/line_pipeline_legacy/README.md` |
| `scripts/harvest/collection.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/harvest/collection.py` | `docs/harvest/COLLECTION_PLAN_v1.md` | `docs/records/harvest/COLLECTION_PLAN_v1.md` |
| `scripts/harvest/collection.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/collection.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/collection.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `scripts/harvest/collection.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/commit_census2_guarded.sh` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/commit_census3_guarded.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/compile_page_reads.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/cyrillic.py` | `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `scripts/harvest/cyrillic.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/cyrillic_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/cyrillic_outputs.py` | `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `scripts/harvest/cyrillic_outputs.py` | `docs/harvest/mixed` | `docs/records/harvest/mixed` |
| `scripts/harvest/mixed.py` | `docs/harvest/mixed` | `docs/records/harvest/mixed` |
| `scripts/harvest/mixed.py` | `docs/harvest/openarchives` | `docs/records/harvest/openarchives` |
| `scripts/harvest/mixed.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/mixed_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/mixed_outputs.py` | `docs/harvest/mixed` | `docs/records/harvest/mixed` |
| `scripts/harvest/mixed_outputs.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/montage_controls.py` | `docs/harvest/montage_v1` | `docs/records/harvest/montage_v1` |
| `scripts/harvest/montage_flush.py` | `docs/harvest/montage_v1` | `docs/records/harvest/montage_v1` |
| `scripts/harvest/montage_pilot.py` | `docs/harvest/montage_v1` | `docs/records/harvest/montage_v1` |
| `scripts/harvest/openarchives.py` | `docs/harvest/openarchives` | `docs/records/harvest/openarchives` |
| `scripts/harvest/openarchives.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/openarchives.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/openarchives_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/openarchives_outputs.py` | `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `scripts/harvest/openarchives_outputs.py` | `docs/harvest/openarchives` | `docs/records/harvest/openarchives` |
| `scripts/harvest/openarchives_outputs.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/openarchives_preflight.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/harvest/openarchives_preflight.py` | `docs/harvest/COLLECTION_PLAN_v1.md` | `docs/records/harvest/COLLECTION_PLAN_v1.md` |
| `scripts/harvest/openarchives_preflight.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/page_reads.py` | `docs/harvest/PAGE_READS_v1.md` | `docs/records/harvest/PAGE_READS_v1.md` |
| `scripts/harvest/page_reads.py` | `docs/harvest/page_reads_v1` | `docs/records/harvest/page_reads_v1` |
| `scripts/harvest/page_reads.py` | `docs/harvest/pilot_v1` | `docs/records/harvest/pilot_v1` |
| `scripts/harvest/parliament.py` | `docs/harvest/parliament` | `docs/records/harvest/parliament` |
| `scripts/harvest/parliament.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/parliament_outputs.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/harvest/parliament_outputs.py` | `docs/harvest/COLLECTION_PLAN_v1.md` | `docs/records/harvest/COLLECTION_PLAN_v1.md` |
| `scripts/harvest/parliament_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/parliament_outputs.py` | `docs/harvest/parliament` | `docs/records/harvest/parliament` |
| `scripts/harvest/parliament_outputs.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/parliament_outputs.py` | `docs/harvest/round2` | `docs/records/harvest/round2` |
| `scripts/harvest/parliament_outputs.py` | `docs/harvest/vouli` | `docs/records/harvest/vouli` |
| `scripts/harvest/reissue_census2.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/reissue_census2.py` | `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `scripts/harvest/reissue_census3.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/round1.py` | `docs/harvest/page_reads_v1` | `docs/records/harvest/page_reads_v1` |
| `scripts/harvest/round1.py` | `docs/harvest/pilot_v1` | `docs/records/harvest/pilot_v1` |
| `scripts/harvest/round1.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/round1_reads.py` | `docs/harvest/page_reads_v1` | `docs/records/harvest/page_reads_v1` |
| `scripts/harvest/round1_reads.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/round1_rescue.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/round2.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/round2.py` | `docs/harvest/round2` | `docs/records/harvest/round2` |
| `scripts/harvest/round2.py` | `docs/harvest/vouli` | `docs/records/harvest/vouli` |
| `scripts/harvest/round2.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `scripts/harvest/round2_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/round2_outputs.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/round2_outputs.py` | `docs/harvest/round2` | `docs/records/harvest/round2` |
| `scripts/harvest/round2_outputs.py` | `docs/harvest/vouli` | `docs/records/harvest/vouli` |
| `scripts/harvest/validate_montage.py` | `docs/harvest/montage_v1` | `docs/records/harvest/montage_v1` |
| `scripts/harvest/validate_montage_flush.py` | `docs/harvest/montage_v1` | `docs/records/harvest/montage_v1` |
| `scripts/harvest/validate_page_reads.py` | `docs/harvest/PAGE_READS_v1.md` | `docs/records/harvest/PAGE_READS_v1.md` |
| `scripts/harvest/validate_round1.py` | `docs/harvest/page_reads_v1` | `docs/records/harvest/page_reads_v1` |
| `scripts/harvest/vouli.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/vouli.py` | `docs/harvest/vouli` | `docs/records/harvest/vouli` |
| `scripts/harvest/vouli_outputs.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/harvest/vouli_outputs.py` | `docs/harvest/COLLECTION_PLAN_v1.md` | `docs/records/harvest/COLLECTION_PLAN_v1.md` |
| `scripts/harvest/vouli_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/harvest/vouli_outputs.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `scripts/harvest/vouli_outputs.py` | `docs/harvest/vouli` | `docs/records/harvest/vouli` |
| `scripts/harvest/wikisource.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `scripts/harvest/wikisource_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/agreement_mode_historical.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/c1_job.sbatch` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/l1_detect.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/l1r_mock_check.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/r1_prepare.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/clariden/r1_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/r1_run.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/r1_score.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/r2_deploy.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/r2a_deploy.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/r2a_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/clariden/tr2_l1_detect.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/cn1_measure.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/cn1_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/k1_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/l1a2_cards.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/l1a2_cards.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/l1a2_fetch.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/m2_run.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/m2_score.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/labelfix/owner_pages_build.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/owner_pages_build_combined.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/owner_reading.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_freeze_ia.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `scripts/labelfix/r0_freeze_ia.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_freeze_ib.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/r0_freeze_ib.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `scripts/labelfix/r0_freeze_ib.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_prepare.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/labelfix/r0_prepare.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/r0_prepare.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `scripts/labelfix/r0_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_score.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/r0_score.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_score_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_score_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r0_wholeline_score.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r2_cards_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r2_cards_resolve.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r2_cards_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r2_finalize_manifest.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r2_job1_digest.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/r2a_digest.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/release_gate_sf7.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s2_crops.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s2_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s2_validate.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/s2_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s3_pin_slots.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s3_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s3_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s4_report.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/s4_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s4_train.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s4_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s5_case_train.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s5_notes.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s5_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s5_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s6_notes.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s6_report.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/labelfix/s6_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s6_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_box_regression.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_launch_baseline.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_m2_replay.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_m2_scope.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_validate.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s7_verify.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_fetch.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_fetch_l1m.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/labelfix/s8_fetch_l1m.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_fetch_stage.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_score_truth.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8_verify_evidence.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8b_measure.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8b_regressions.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8b_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/s8b_split.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf1_owner_rescore.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf1_rescore.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf2_replay.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf4_measure.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf4_r1_compatibility.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf5_measure.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/sf5_measure.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf5_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf6_measure.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `scripts/labelfix/sf6_measure.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/labelfix/sf6b_measure.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf6c_audit.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf6c_audit.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/labelfix/sf6c_measure.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/labelfix/sf6c_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf6c_verify.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/labelfix/sf7_deploy.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf7_measure.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf7_opus_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sf7_package.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/labelfix/sheet_build.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/lqb/build_truth.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/lqb/build_truth.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `scripts/lqb/build_truth.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/lqb/build_v2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/lqb/build_v2_1.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/lqb/build_v2_2.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/lqb/finalize.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/lqb/validate_scoreboard.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1_apply_train.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1_report.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1_report.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/numerics/n1_score.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1cb_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1cc_prepare.py` | `docs/harvest/collect_v3` | `docs/records/harvest/collect_v3` |
| `scripts/numerics/n1cc_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1cc_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1cd_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1cd_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1g.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1r2_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1r_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1t_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1t_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1tb_prepare.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1tr.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1tr_f2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1ts.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1ts2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1ts3.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1w1.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1w1_f2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/n1w1_f3.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/numerics/validate_n1.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/pages/check_q5_default.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/pages/write_q3_receipt.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/pages/write_q3b_receipt.py` | `docs/reviews` | `docs/records/reviews` |
| `scripts/review/build_owner_sheets_v2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/review/build_sheet1_demos.py` | `docs/review/demo` | `docs/B_training_data/d_review/demo` |
| `scripts/review/cu4_reemit.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/review/report_os1.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/reading/n1_launch.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/reading/n1tr_driver.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/reading/run_bed.sh` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru1_build_packs.py` | `docs/harvest/collect_v3` | `docs/records/harvest/collect_v3` |
| `scripts/secondary/ru1_finalize.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/secondary/ru1_finalize.py` | `docs/harvest/collect_v3` | `docs/records/harvest/collect_v3` |
| `scripts/secondary/ru1_finalize.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru1_finalize_b.py` | `docs/briefs` | `docs/records/briefs` |
| `scripts/secondary/ru1_finalize_b.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru1_owner_sheet.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru1_version.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru2t.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru2t_apply_lead.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru2t_delivery.py` | `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `scripts/secondary/ru2t_launch.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru2t_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru3t_delivery.py` | `docs/harvest/cyrillic` | `docs/records/harvest/cyrillic` |
| `scripts/secondary/ru3t_delivery.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru3t_f4.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru3t_r3.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru3t_r5.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru3td_edits.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru4e.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru4e2_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru4ef2_receipt.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru4ef3.py` | `docs/labelfix` | `docs/records/labelfix` |
| `scripts/secondary/ru4ef3_score.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/_paths.py + tests/conftest.py` | `historical local paths in executable documentation fixtures` | `move-table destinations; repository parent expressions rebased in memory` |
| `tests/glyphs/test_glyphs.py` | `docs/reviews` | `docs/records/reviews` |
| `tests/labelfix/test_l1r4.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_r2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_r2_readback_digest.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_s4.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_s5.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_s6.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_s7.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_sf1.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_sf2.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_sf4.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/labelfix/test_sf6c.py` | `docs/reviews` | `docs/records/reviews` |
| `tests/labelfix/test_sf7.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/prepare_merge_fixtures.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_adm5b_schema.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_adm5b_schema.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `tests/test_apply_clean.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `tests/test_collection.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `tests/test_collection_outputs.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `tests/test_collection_outputs.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `tests/test_collection_outputs.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `tests/test_content_gate.py` | `docs/harvest/seg_steps and collect_v3_admission inside runpy fixture` | `docs/records/harvest/seg_steps and collect_v3_admission via run_record` |
| `tests/test_geometry_measure.py` | `docs/O4D_G1_measure_v1.json` | `docs/records/glyphs/O4D_G1_measure_v1.json` |
| `tests/test_n1g.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/test_n1t.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/test_neighbour_words.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_numeric_cells.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_owner_sheet.py` | `docs/review/demo` | `docs/B_training_data/d_review/demo` |
| `tests/test_p1b_alignment.py` | `docs/harvest/pilots_v2` | `docs/records/harvest/pilots_v2` |
| `tests/test_round1_rescue.py` | `docs/harvest/round1` | `docs/records/harvest/round1` |
| `tests/test_round2.py` | `docs/harvest/{wave or prior-wave filename}` | `docs/records/harvest/{wave or prior-wave filename}` |
| `tests/test_ru3t.py` | `docs/labelfix` | `docs/records/labelfix` |
| `tests/test_scan_rollout.py` | `docs/harvest/sol_reading` | `docs/records/harvest/sol_reading` |
| `tests/test_seg_cp1.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp1.py` | `ledger source paths to relocated briefs and records` | `temporary current-ledger source bindings; saved ledger and saved hashes untouched` |
| `tests/test_seg_cp2.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp3.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp4.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp5.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp5pb.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp6.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7a3_geometry.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7b_score.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7c.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7c.py` | `docs/harvest/recut_v1` | `docs/records/harvest/recut_v1` |
| `tests/test_seg_cp7c2_runtime.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7c2_runtime.py` | `historical amendment path and frozen files keys` | `same relative suffix at the mapped destination; hash values untouched` |
| `tests/test_seg_cp7c_score_fixtures.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp7d.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_cp8a.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_curve.py` | `docs/harvest/seg_steps` | `docs/records/harvest/seg_steps` |
| `tests/test_seg_deskew.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_deskew.py` | `docs/harvest/seg_steps` | `docs/records/harvest/seg_steps` |
| `tests/test_seg_gate.py` | `docs/harvest/collect_v3_admission` | `docs/records/harvest/collect_v3_admission` |
| `tests/test_seg_gate.py` | `docs/harvest/seg_steps` | `docs/records/harvest/seg_steps` |
| `tests/test_seg_small.py` | `docs/harvest/seg_steps` | `docs/records/harvest/seg_steps` |
| `tests/test_wikisource.py` | `docs/harvest/collection` | `docs/records/harvest/collection` |
| `tests/test_wikisource.py` | `docs/harvest/wikisource` | `docs/records/harvest/wikisource` |
| `tests/test_wikisource.py` | `temporary docs/harvest/prior fixture` | `temporary docs/records/harvest/prior fixture` |

## Added missing-input skips

85 newly skipped nodes name 37 genuinely absent inputs. The other 102 skips retain their existing historical, environmental, or optional-input reasons. Each filename below was rechecked after the final run and is still unavailable locally and through the configured resolver.

| Test/fixture node | Exact skip reason (missing filename) |
|---|---|
| `tests/adjudicate/test_os2_owner_sheets.py::test_os2_checker_codes_and_masked_rasters` | `docs/owner_sheets/inputs/coordinator_labelmap.json` |
| `tests/adjudicate/test_os2_owner_sheets.py::test_os2_source_bound_printed_and_yers` | `docs/owner_sheets/inputs/coordinator_labelmap.json` |
| `tests/adjudicate/test_os2_owner_sheets.py::test_os3_every_google_row_nonempty[failure_modes_per_class]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/artifacts/owner_sheets/v2/failure_modes_per_class.html` |
| `tests/adjudicate/test_os2_owner_sheets.py::test_os3_every_google_row_nonempty[segmentation_failures]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/artifacts/owner_sheets/v2/segmentation_failures.html` |
| `tests/adjudicate/test_os2_owner_sheets.py::test_os3_recomputed_pairs_and_current_coordinator_continuity` | `docs/owner_sheets/inputs/coordinator_labelmap.json` |
| `tests/adjudicate/test_os5_owner_sheets.py::test_os5_full_native_crop_saved_detections_and_highlight` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/artifacts/owner_sheets/v2/failure_modes_per_class.html` |
| `tests/adjudicate/test_sr1.py::test_data_page_specs[accent_corrections_checked-100]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/artifacts/cleanup_sr1/specs/accent_corrections_checked.json` |
| `tests/adjudicate/test_sr1.py::test_data_page_specs[audit_words-100]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/artifacts/cleanup_sr1/specs/audit_words.json` |
| `tests/labelfix/test_r2.py::test_r1_published_continuity_exact` | `docs/records/labelfix/spellcheck/S4_lines.jsonl.gz` |
| `tests/labelfix/test_r2_readback_digest.py::test_population_line_counts_include_lines_without_slots` | `artifacts/labelfix_r2/population/population.jsonl` |
| `tests/labelfix/test_r2_readback_digest.py::test_real_frozen_compound_truth_and_owner_overlays_are_preserved` | `docs/records/labelfix/spellcheck/S4_lines.jsonl.gz` |
| `tests/labelfix/test_r2a_package.py::test_quarantined_real_slot_still_fails_frozen_extractor` | `artifacts/labelfix_r2a/inputs/native_alignments.jsonl.gz` |
| `tests/labelfix/test_sf1.py::test_baseline_name_hash_and_expected_totals_bound` | `docs/records/labelfix/spellcheck/S6_lines.jsonl.gz` |
| `tests/labelfix/test_sf1.py::test_owner_page_same_serialized_reading_and_reference_parity[owner_pages_build]` | `docs/records/labelfix/spellcheck/S6_lines.jsonl.gz` |
| `tests/labelfix/test_sf1.py::test_owner_page_same_serialized_reading_and_reference_parity[owner_pages_build_combined]` | `docs/records/labelfix/spellcheck/S6_lines.jsonl.gz` |
| `tests/labelfix/test_sf5.py::test_saved_56_release_witnesses[witness_inputs.jsonl.gz]` | `docs/records/labelfix/spellcheck/SF5_evidence/witness_inputs.jsonl.gz` |
| `tests/labelfix/test_sf6.py::test_every_released_measured_deletion_has_two_certified_absences` | `docs/records/labelfix/spellcheck/SF6_evidence/heldout/release_labels.jsonl.gz` |
| `tests/labelfix/test_sf6.py::test_keraia_is_held_even_with_two_r1_arms` | `docs/records/labelfix/spellcheck/SF6_evidence/witness_inputs.jsonl.gz` |
| `tests/labelfix/test_sf6.py::test_saved_release_regression[witness_inputs.jsonl.gz]` | `docs/records/labelfix/spellcheck/SF6_evidence/witness_inputs.jsonl.gz` |
| `tests/labelfix/test_sf7.py::test_all_39_cards[cards39_inputs.jsonl.gz-A]` | `docs/records/labelfix/spellcheck/SF7_evidence/cards39_inputs.jsonl.gz` |
| `tests/labelfix/test_sf7.py::test_all_39_cards[cards39_inputs.jsonl.gz-B]` | `docs/records/labelfix/spellcheck/SF7_evidence/cards39_inputs.jsonl.gz` |
| `tests/labelfix/test_sf7.py::test_all_audit_lines[selected_overlays.json.gz-A]` | `docs/records/labelfix/spellcheck/S8_DEV/private/audit100/selected_overlays.json.gz` |
| `tests/labelfix/test_sf7.py::test_all_audit_lines[selected_overlays.json.gz-B]` | `docs/records/labelfix/spellcheck/S8_DEV/private/audit100/selected_overlays.json.gz` |
| `tests/test_adm5b_schema.py::test_delivered_outputs_schema[docs/records/harvest/collect_v3_admission/w1_originals_v3]` | `docs/records/harvest/collect_v3_admission/w1_originals_v3_admission.jsonl` |
| `tests/test_adm5b_schema.py::test_delivered_outputs_schema[docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017]` | `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017_admission.jsonl` |
| `tests/test_collection_outputs.py::test_all_input_rows_are_accounted_for_and_only_train_rejected` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_all_merged_rows_have_uniform_valid_schema` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_import_real_fields_splits_paths_and_document_boundaries` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_lexicon_70_page_repair_counts_and_no_page_crossing` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_manifest_is_exact_projection_of_merged_rows[dev]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_manifest_is_exact_projection_of_merged_rows[test]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_manifest_is_exact_projection_of_merged_rows[train]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_no_global_label_leakage_or_prior_wikisource_exclusions` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_collection_outputs.py::test_validation_caps_counts_and_sample_coverage` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collection/admitted_all.jsonl` |
| `tests/test_content_gate.py::test_numeric_grammar_parity_all_four_sets` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/seg_steps/s4/inputs.jsonl` |
| `tests/test_lqb.py::test_all_frozen_sources_and_rows_have_sample_types` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_capital_target_is_one_letter` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_frozen_truth_integrity` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_ia_letters_pixel_scope_and_pending_ib` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_lqb2_alt_and_flags_integrity` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_lqb2_real_training_split_and_label_parity` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_owner_overlay_is_applied_symmetrically` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_resolved_present_heads_not_dropped` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb.py::test_scoreboard_sample_displays_and_pending_truth` | `docs/records/labelfix/lqb/scoreboard.html` |
| `tests/test_lqb3.py::test_baseline_first_and_page_budget` | `docs/records/labelfix/lqb/validation/lqb3/frozen/scoreboard.html` |
| `tests/test_lqb3.py::test_frozen_truth_and_flags_unchanged` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb3.py::test_n1_registered_unadopted_and_in_sample` | `artifacts/n1/owner_sheet/cards.json` |
| `tests/test_lqb4.py::test_frozen_v1_remains_intact` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb4.py::test_sx1_v2_verified_membership` | `docs/records/labelfix/lqb/truth_v1.jsonl` |
| `tests/test_lqb5.py::test_independent_weighted_google_reaggregation` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/labelfix/lqb/truth_v1_1.jsonl` |
| `tests/test_lqb5.py::test_page_top_line_and_budget` | `docs/records/labelfix/lqb/scoreboard.html` |
| `tests/test_lqb5.py::test_saved_weights_and_exact_card_exclusions` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/labelfix/lqb/truth_v1_1.jsonl` |
| `tests/test_lqb5.py::test_truth_freeze_and_admission` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/labelfix/lqb/truth_v1_1.jsonl` |
| `tests/test_n1_score.py::test_real_outputs_exclude_void_and_bind_cards` | `artifacts/n1/n1t2/phase1_owner_sheet.html` |
| `tests/test_n1r.py::test_locked_complete_selection_and_hash_order` | `artifacts/n1/n1e/slots.jsonl` |
| `tests/test_n1r2.py::test_real_decisions_pending_and_sheet_union` | `artifacts/n1/owner_sheet/cards.json` |
| `tests/test_n1t.py::test_real_bed_coverage_controls_reverse_and_source_image_hashes` | `artifacts/n1/n1t/slots.jsonl` |
| `tests/test_n1t.py::test_real_phase_a_scope_and_one_explicit_failure` | `artifacts/n1/n1t/slots.jsonl` |
| `tests/test_n1tb.py::test_real_pruning_partition_seal_and_superseded_custody` | `artifacts/n1/n1t/slots.jsonl` |
| `tests/test_n1ts.py::test_actual_phase1_accounting_and_coverage` | `artifacts/n1/n1t2/slots.jsonl` |
| `tests/test_n1ts2.py::test_actual_rulings_and_all_pending_slots_retained` | `artifacts/n1/n1t2/slots.jsonl` |
| `tests/test_n1ts2.py::test_legacy_note_loading_preserves_two_notes_without_remote_write` | `artifacts/n1/owner_sheet/n1_sheet.html` |
| `tests/test_n1ts2.py::test_note_identity_legacy_fallback_in_html` | `artifacts/n1/owner_sheet/n1_sheet.html` |
| `tests/test_n1ts3.py::test_sheet_cap_native_rasters_and_jpeg85` | `artifacts/n1/owner_sheet/n1_sheet.html` |
| `tests/test_round1_rescue.py::test_live_owner_input_is_exactly_51_books_693_slots_and_no_pending` | `docs/records/harvest/round1/selection.json` |
| `tests/test_seg_cp5pb.py::test_failed_gate_and_unavailable_accounting` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/seg/CP5pb_calibration.json` |
| `tests/test_seg_cp5pb.py::test_frozen_regression[CP5pb_calibration.json]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/seg/CP5pb_calibration.json` |
| `tests/test_seg_cp7b_score.py::test_adjudication_coverage_and_original_crop_bytes` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/seg/cp7/scored_cp7b.jsonl.gz` |
| `tests/test_seg_cp7b_score.py::test_contact_sheet_complete_at_most_thirty_and_decodes` | `docs/records/harvest/collect_v3_admission/seg/cp7/ADJUDICATION_SHEET.png` |
| `tests/test_seg_cp7b_score.py::test_fresh_results_independently_recounted` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/seg/cp7/scored_cp7b.jsonl.gz` |
| `tests/test_seg_cp7c.py::test_draw_deterministic_disjoint_and_snapshot_bound` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/seg/CP5_verification.json` |
| `tests/test_seg_cp7c_score_fixtures.py::test_fn_and_scan_failure_fail_gate` | `docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz` |
| `tests/test_seg_cp7c_score_fixtures.py::test_known_clip_outputs_and_contact_sheet` | `docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz` |
| `tests/test_seg_cp7c_score_fixtures.py::test_screen_fp_fails_gate[crossing]` | `docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz` |
| `tests/test_seg_cp7c_score_fixtures.py::test_screen_fp_fails_gate[merged]` | `docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz` |
| `tests/test_seg_cp7c_score_fixtures.py::test_screen_fp_fails_gate[neighbour_words]` | `docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz` |
| `tests/test_seg_cp7c_score_fixtures.py::test_screen_fp_fails_gate[orientation]` | `docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz` |
| `tests/test_seg_deskew.py::test_real_zero_angle_is_digit_exact[51db636c-p000048-l0024]` | `docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl` |
| `tests/test_seg_deskew.py::test_real_zero_angle_is_digit_exact[gazette_modern--59ebc3dbeb1516d3--s000-l0066]` | `docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl` |
| `tests/test_seg_deskew.py::test_real_zero_angle_is_digit_exact[gazette_modern--6d6a6fe53e769b59--s000-l0009]` | `docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl` |
| `tests/test_seg_gate.py::test_cut_witness_decides_by_frozen_length` | `docs/records/harvest/collect_v3_admission/segeval1/deskew/replay_segeval1.jsonl` |
| `tests/test_seg_gate.py::test_optional_context_failure_cannot_prevent_crop_decision[error0]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/segeval1/crops/b8b6779da9a68fbed0ccdb5b-p000011-l0018.png` |
| `tests/test_seg_gate.py::test_optional_context_failure_cannot_prevent_crop_decision[error1]` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/segeval1/crops/b8b6779da9a68fbed0ccdb5b-p000011-l0018.png` |
| `tests/test_seg_gate.py::test_partial_body_witness_keeps_without_context` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/segeval1/crops/b8b6779da9a68fbed0ccdb5b-p000011-l0018.png` |
| `tests/test_seg_gate.py::test_stage_b_zero_angle_equals_06_to_digit` | `docs/records/harvest/collect_v3_admission/segeval1/deskew/replay_segeval1.jsonl` |


## Verification

Command (the JUnit option records node-level dispositions without changing suite selection):

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q -p no:cacheprovider --junitxml=/private/tmp/clean4l3-final.xml
```

Final native pytest summary:

```text
6636 passed, 187 skipped, 9 warnings, 63 subtests passed in 159.21s (0:02:39)
```

Pytest omits zero-valued counters. JUnit independently records zero failures and zero errors. The full summary with those counters explicit is:

```text
0 failed, 0 errors, 6636 passed, 187 skipped, 9 warnings, 63 subtests passed in 159.21s (0:02:39)
```

All 1111 fingerprinted source/fixture files are byte-identical before and after this final run. No required source edit remained after the run.

Additional verification: the retrieval alias map equals all 130 rows of `LAYOUT_REPORT.md`; both new resolver tests pass (relocated local paths versus historical data mirrors, and exact historical custody-shard attribution). `git diff --check` passes. Existing tracked documentation and saved JSON/JSONL/Rust snapshot bytes have no diff. Source/fixture fingerprints bracket the final run.

Logs and node receipts: `/private/tmp/clean4l3-final.log`, `/private/tmp/clean4l3-final.xml`. Source fingerprints: `/private/tmp/clean4l3-source-before.json`, `/private/tmp/clean4l3-source-after.json`.
