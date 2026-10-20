# CLEAN3A summary — analysis only

HEAD `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33 HEAD -> cleanup/20261019`; no files moved, no git writes, no history rewrite. All outputs are under `docs/cleanup_20261019/data_out/`.

| Measure | Files | Bytes |
|---|---:|---:|
| HEAD inventory (complete conservative scope) | 61,533 | 12,856,380,501 |
| >5,000,000-byte files (all MOVE) | 232 | 8,559,279,830 |
| Proposed MOVE (includes oversized subset) | 54,722 | 12,633,970,431 |
| KEEP | 6,792 | 222,407,400 |
| ASK | 19 | 2,670 |

Destination: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data/<original repo-relative path>`, accessed using `GREEK_OCR_DATA_ROOT` or hash-checked receipt lookup. 1,491 directories become empty in the proposed plan. 3,343 code/test source files have literal basename references to MOVE candidates; pair-level fixes are in READERS_TO_UPDATE.tsv. Basename collisions, producer-only references and dynamic directory consumers need execution-time review; these are not all proven read failures.

Lead receipts: 13,230 per-file rows reconciled, 213 current HEAD matches, 23 byte/hash conflicts. Other-worktree custody items are not included in MOVE totals. Segmentation's five tracked large artifacts retain their exact required hashes. The bundle header was read; its bundled head is absent from the local Git object database. Preserve the bundle itself. candidate_order_KEEP and SEGEVAL1.bundle will be missing to unchanged historical s1–s4/gate_rereport/gate03 part-3 scope guards; use a new receipt-backed replay adapter without altering those records.

Open questions before any move:

- Decide the following ASK paths (stored symlink text is hashed; external/dangling targets are not copied):
  - `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_conflicting_inline_fcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_explicit_missing_flacurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_invalid_flags_fail_ccurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_run_autoloads_flags_current` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_overlay_and_admission_popcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_conflicting_inline_fcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_explicit_missing_flacurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_invalid_flags_fail_ccurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_run_autoloads_flags_current` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_overlay_and_admission_popcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_supplemental_google_hash_current` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_conflicting_inline_fcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_explicit_missing_flacurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_invalid_flags_fail_ccurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_run_autoloads_flags_current` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_overlay_and_admission_popcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/labelfix/lqb/validation/pytest_tmp/test_overlay_and_admission_popcurrent` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/artifacts` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.
  - `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/docs` — Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.

- Reconcile the 23 same-path HEAD/lead-receipt byte/hash conflicts listed in RECEIPT_CONFLICTS.tsv. Preserve both versions and settle versioned custody before copying to a shared destination.
- Confirm retention of the lead-mandated 1.7 MB census evidence and the explicitly marked small referenced test fixtures versus a stricter no-bulk-in-git reading. The plan declares these exceptions rather than silently contradicting the lead.
- Confirm retrievable custody at the new root for lead-only paths: spellcheck outputs/READBACK_RECEIPT, six small-segment outputs, and 3,460 pilot receipts. Their source-worktree receipts are inputs, not proof of a completed transfer.
- Review literal-reference candidates and dynamic directory/relative HTML consumers; implement receipt/data-root resolution before relocation. No consumer patch was made here.
- Choose ≤5 MB receipt shards or compression for oversized planning outputs before tracking them. Keep the proposed guard outside tests until the approved execution change; preserve historical evidence unchanged.
- Establish durable external custody and rollback before untracking SEGEVAL1.bundle, frozen LQB truth and sampling/census keys. No destination capacity, copy, move or durability check has been performed.

Deliverables: MOVE_PLAN.tsv, MOVE_PLAN.md, size_guard_test.py, .gitignore.proposed and this SUMMARY.md. Supporting tables record bulk-directory metrics, empty directories, reader fixes and receipt reconciliation. Collector scripts and snapshot/grep caches make the analysis reproducible; they are analysis outputs, not installed repository behavior.

Validation: `VALIDATION.json` records complete HEAD coverage, verified snapshot hashes/sizes, exact path-log producing commits, unchanged HEAD/index IDs and tracked-file lstat metadata, complete MOVE-only ignore coverage, seven independent basename-grep spotchecks, and the proposed guard’s expected 232-path failure. Other cleanup drafts appeared during the shared-workspace run; `READER_REFRESH.json` records the read-only refresh of those untracked text references. No move, source edit, or git-writing command was performed.
