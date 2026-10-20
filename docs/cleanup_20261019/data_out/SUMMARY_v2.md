# CLEAN3B summary v2

MOVE **16,888 entries / 9,984,555,912 bytes**; KEEP **44,645 entries / 2,871,824,589 bytes**. All 61,533 CLEAN3A HEAD inventory paths are covered once. 37,858 v1 MOVE entries (2,657,936,043 bytes) now KEEP. All 19 ASK symlinks now MOVE, hashed as stored link text. No file moves, untracking, commits, ignore installation or history changes were executed.

Rules: 232 a; 16376 b; 261 c; 19 d. Small literal inputs exempted: 31. Directories becoming empty: 91 in HEAD and 91 in the observed working tree. See MOVE_PLAN_v2.md and EMPTY_DIRECTORIES_v2.tsv.

## Reader changes

147 existing source files patched at file input/hash boundaries, plus greekocr/ops/data_root.py and tests/test_data_root.py added. Full source changes: LIVE_READER_PATCHES_v2.diff; per-file hashes: reader_changes_v2.json; every path and final byte count: FILES_WRITTEN_v2.tsv. ops/__init__.py lazily loads receipt/rate helpers to avoid a resolver -> receipt -> vendor -> resolver import cycle and importing OCR dependencies merely to resolve a path. Public helper exports are preserved.

Fresh literal scan: 674 live files, 5,651 reader/MOVE pairs; 5,164 rg matches. LIVE_READERS_v2.tsv includes full-path references, basename collisions, producer/example mentions and metadata. A lexical match is not a claim that a specific file is loaded. Code changes resolve at existing input boundaries; output writes and historical docs/ scripts are unchanged.

Existing tests were not edited. 16 test files have direct input-site changes staged in CLEAN4T_READER_HANDOFF_v2.diff; coordinator/CLEAN4T must reconcile and apply that patch after concurrent edits. Other test readers inherit patched shared input helpers.

## Receipt conflicts: HEAD has custody

Each of the 23 lead conflicts is decided below. Complete HEAD and lead sizes, hashes and lead receipt paths remain in RECEIPT_CONFLICT_DECISIONS_v2.tsv; the original CLEAN3A conflict file is unchanged. A lead version is noted, not transferred by this checkout.

| Path | v2 | Decision |
|---|---|---|
| `artifacts/cq4/aggregate_receipt.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/build_hashes.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/build_receipt.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/closure/topup_reread_000.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/contexts.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/keys/topup_reread_000.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/lead_queue.jsonl` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/lead_queue.png` | MOVE | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/limit_probe.log` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/logs/topup_reread_000_final.md` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/logs/topup_reread_000.codexlog` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/quarantine/topup.jsonl` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/quarantine/wcap.jsonl` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/reread_build_receipt.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/reread_contexts.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/reread_ledger.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/scans/topup_reread_000.json` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/tools/build.py` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/tools/scan_rollout.py` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/tools/workflow.py` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/truth/topup.jsonl` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `artifacts/cq4/truth/wcap.jsonl` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |
| `docs/records/labelfix/spellcheck/R2/CQ4_REPORT.md` | KEEP | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |

## Mover and execution boundaries

The coordinator command is:

```sh
python3 docs/cleanup_20261019/data_out/move_data.py --execute --dest /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data
```

The mover first verifies every source and existing destination. Same-hash destinations are skipped, leaving any repository source intact. Different bytes or file/link types stop execution before transfers. Cross-filesystem transfers use exclusive destination creation, hash verification and fsync, with a durable manifest entry before source unlink. MOVE_MANIFEST.tsv and rollback.sh are created only by execution. Interrupted partial destination copies cause a mismatch stop; they are never overwritten automatically. A complete copied destination with its source still present is skipped safely. Rollback restores journaled source losses without overwriting differing repository paths; already-present identical paths are left intact.

RECEIPTS/INDEX.md indexes 1 shard(s), each <=4,000,000 bytes, covering every MOVE entry. SYMLINKS_v2.tsv records the 19 exact link texts; mirrored directories are preserved and external link targets are never copied. SEGEVAL1.bundle and candidate_order_KEEP historical guard notes are in the index.

gitignore_additions_v2.txt has 118 patterns plus comments (<=300 lines). Scoped extension patterns also match some retained small exports: ignore rules cannot express size thresholds. Those KEEP files remain tracked; no source-extension blanket rule is introduced. Small live bulk exceptions are negated explicitly. The oversized generated MOVE_PLAN_v2.tsv is excluded as a local planning artifact. Install additions and untrack only after custody is verified. The size guard checks indexed blob sizes, so missing working files cannot hide tracked large blobs.

## Validation and open questions

- Inventory scope is frozen to CLEAN3A HEAD ac1c38cf6ebab49ef694fffb2a8b3dc757012f33. At the first successful CLEAN3B baseline, HEAD was already 70a3a4de6b7eb5da72292b7d9bbb6ad52a3a59e5, with 44 added CLEAN3A report/draft paths outside that input inventory. Original inventory index modes/blob IDs are unchanged. Those later additions were not folded into the requested v1-based plan; review their disposition separately (notably the generated basename_patterns.txt). The recorded CLEAN3B HEAD/index baseline remains unchanged. INDEX_DELTA_v2.json lists the additions.
- Full dry-run source hashes, receipt coverage, classification, ignore coverage, immutable CLEAN3A files and indexed object identities are checked by validate_v2.py; results are in VALIDATION_v2.json.
- New resolver + read-only mover checks: 24 passed under the x86_64 Python interpreter. No transfer/execute/rollback was exercised on real data.
- Broader pre-move selection: 96 passed, 17 failed. Failures involve incompatible SciPy architecture, missing historical budget ledgers and SHEETS.md. Verify-suite collection also hits the incompatible SciPy installation. These are not evidence of post-move reader qualification; this run did not modify those tests or supply missing external inputs.
- Reconcile the staged existing-test reader edits with CLEAN4T before relocation. Directory enumeration, generated HTML relative assets, command examples and caller-supplied data fields need post-move integration checks; literal references alone cannot certify dynamic consumers.
- Set GREEK_OCR_DATA_ROOT for actual jobs and confirm destination capacity/durability. No destination data or external-worktree custody has been acquired here. A mirror holding a conflicting lead version must be versioned separately; the mover stops on a conflict.
- The 19 stored symlink targets can remain dangling after relocation. This preserves their exact custody, not availability of their external targets.
- Historical s1–s4/gate_rereport/gate03 guards and source-hash-bound records remain unchanged. Replay requires a new receipt-backed adapter or deliberately restored mirror; do not edit old records to make a check pass.

## Files changed by this run

- `greekocr/_vendor/bench/common.py`
- `greekocr/_vendor/bench/e1_common.py`
- `greekocr/_vendor/train/mix.py`
- `greekocr/adjudicate/_files.py`
- `greekocr/harvest/application_identity.py`
- `greekocr/harvest/collection.py`
- `greekocr/harvest/geometry_observations.py`
- `greekocr/harvest/pipeline.py`
- `greekocr/harvest/readers.py`
- `greekocr/harvest/separator_inventory.py`
- `greekocr/labelfix/lqb.py`
- `greekocr/labelfix/spellcheck_validate.py`
- `greekocr/numerics/ink_rule.py`
- `greekocr/ops/__init__.py`
- `greekocr/ops/data_root.py`
- `greekocr/verify/cli.py`
- `prototypes/fast_lines/features_geometry/test_native_font_contract.py`
- `prototypes/fast_lines/shared/manifest.py`
- `prototypes/harvest/google_failed_lines.py`
- `scripts/glyphs/archive/audit_orientation_guides.py`
- `scripts/glyphs/archive/generate_orientation_guides.py`
- `scripts/glyphs/archive/report_orientation_guides.py`
- `scripts/glyphs/archive/review_line_structure.py`
- `scripts/harvest/_anemi_round1_fetcher.py`
- `scripts/harvest/admit_round1.py`
- `scripts/harvest/cyrillic.py`
- `scripts/harvest/cyrillic_outputs.py`
- `scripts/harvest/mixed.py`
- `scripts/harvest/mixed_outputs.py`
- `scripts/harvest/montage_controls.py`
- `scripts/harvest/montage_flush.py`
- `scripts/harvest/montage_pilot.py`
- `scripts/harvest/openarchives.py`
- `scripts/harvest/openarchives_outputs.py`
- `scripts/harvest/openarchives_preflight.py`
- `scripts/harvest/page_reads.py`
- `scripts/harvest/parliament.py`
- `scripts/harvest/parliament_outputs.py`
- `scripts/harvest/parliament_retention.py`
- `scripts/harvest/reissue_census2.py`
- `scripts/harvest/reissue_census3.py`
- `scripts/harvest/round1.py`
- `scripts/harvest/round1_reads.py`
- `scripts/harvest/round1_reads_rest.py`
- `scripts/harvest/round1_rescue.py`
- `scripts/harvest/round2.py`
- `scripts/harvest/round2_outputs.py`
- `scripts/harvest/validate_montage_flush.py`
- `scripts/harvest/validate_page_reads.py`
- `scripts/harvest/validate_round1_reads_rest.py`
- `scripts/harvest/verify_filter_parity.py`
- `scripts/harvest/vouli.py`
- `scripts/harvest/vouli_outputs.py`
- `scripts/labelfix/agreement_mode_historical.py`
- `scripts/labelfix/clariden/l1c_census.py`
- `scripts/labelfix/clariden/l1r_recompose_ext.py`
- `scripts/labelfix/clariden/r1_common.py`
- `scripts/labelfix/cn1_measure.py`
- `scripts/labelfix/cn1_report.py`
- `scripts/labelfix/k1_validate.py`
- `scripts/labelfix/l1a2_cards.py`
- `scripts/labelfix/l1a2_fetch.py`
- `scripts/labelfix/m2_run.py`
- `scripts/labelfix/r0_finish.py`
- `scripts/labelfix/r0_prepare.py`
- `scripts/labelfix/r0_score.py`
- `scripts/labelfix/r0_score_report.py`
- `scripts/labelfix/r2_cards_prepare.py`
- `scripts/labelfix/r2_cards_resolve.py`
- `scripts/labelfix/r2_finalize_manifest.py`
- `scripts/labelfix/r2_job1_digest.py`
- `scripts/labelfix/r2_readback_verify.py`
- `scripts/labelfix/r2a_digest.py`
- `scripts/labelfix/s2_crops.py`
- `scripts/labelfix/s2_report.py`
- `scripts/labelfix/s2_validate.py`
- `scripts/labelfix/s3_pin_slots.py`
- `scripts/labelfix/s3_report.py`
- `scripts/labelfix/s3_validate.py`
- `scripts/labelfix/s4_report.py`
- `scripts/labelfix/s4_train.py`
- `scripts/labelfix/s4_validate.py`
- `scripts/labelfix/s5_report.py`
- `scripts/labelfix/s5_validate.py`
- `scripts/labelfix/s6_report.py`
- `scripts/labelfix/s7_report.py`
- `scripts/labelfix/s7_validate.py`
- `scripts/labelfix/s7_verify.py`
- `scripts/labelfix/s8_fetch.py`
- `scripts/labelfix/s8_fetch_job.py`
- `scripts/labelfix/s8_fetch_l1m.py`
- `scripts/labelfix/s8_fetch_stage.py`
- `scripts/labelfix/s8_prepare.py`
- `scripts/labelfix/s8_score_truth.py`
- `scripts/labelfix/s8_validate_audit.py`
- `scripts/labelfix/s8_validate_truth.py`
- `scripts/labelfix/s8_verify_evidence.py`
- `scripts/labelfix/s8b_report.py`
- `scripts/labelfix/s8b_split.py`
- `scripts/labelfix/sf2_replay.py`
- `scripts/labelfix/sf4_r1_compatibility.py`
- `scripts/labelfix/sf5_verify.py`
- `scripts/labelfix/sf6_measure.py`
- `scripts/labelfix/sf6_verify.py`
- `scripts/labelfix/sf6b_measure.py`
- `scripts/labelfix/sf6c_report.py`
- `scripts/labelfix/sf7_final_score.py`
- `scripts/labelfix/sf7_measure.py`
- `scripts/labelfix/sf7_opus_prepare.py`
- `scripts/lqb/build_scoreboard.py`
- `scripts/lqb/build_v2.py`
- `scripts/lqb/build_v2_1.py`
- `scripts/lqb/validate_scoreboard.py`
- `scripts/numerics/n1_prepare.py`
- `scripts/numerics/n1_score.py`
- `scripts/numerics/n1cb_prepare.py`
- `scripts/numerics/n1g.py`
- `scripts/numerics/n1r_fit.py`
- `scripts/numerics/n1r_receipt.py`
- `scripts/numerics/n1t_combine.py`
- `scripts/numerics/n1t_packs.py`
- `scripts/numerics/n1t_prepare.py`
- `scripts/numerics/n1t_receipt.py`
- `scripts/numerics/n1tb_prepare.py`
- `scripts/numerics/n1tr.py`
- `scripts/numerics/n1tr_f2.py`
- `scripts/numerics/n1ts.py`
- `scripts/numerics/n1w1.py`
- `scripts/numerics/n1w1_f3.py`
- `scripts/numerics/n1w1_packs.py`
- `scripts/pages/check_q5_default.py`
- `scripts/pages/write_q3_receipt.py`
- `scripts/pages/write_q3b_receipt.py`
- `scripts/review/build_owner_sheets_v2.py`
- `scripts/review/build_sheet1_demos.py`
- `scripts/review/prepare_os1_specs.py`
- `scripts/secondary/reading/common.py`
- `scripts/secondary/reading/n1w1_common.py`
- `scripts/secondary/reading/n1w1_exclusions.py`
- `scripts/secondary/reading/reference/build_packs.py`
- `scripts/secondary/ru1_census.py`
- `scripts/secondary/ru3td_bind_probe.py`
- `scripts/secondary/ru3td_edits.py`
- `scripts/secondary/ru4e2_bound/common.py`
- `scripts/secondary/ru4e2_bound/ru1_census.py`
- `scripts/secondary/ru4e_bound/common.py`
- `scripts/secondary/ru4e_bound/ru1_census.py`
- `scripts/secondary/ru4ef3.py`
- `tests/test_data_root.py`
