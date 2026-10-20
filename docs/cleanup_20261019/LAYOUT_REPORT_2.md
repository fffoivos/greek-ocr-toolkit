# CLEAN4L2 — second documentation layout pass

Workspace: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next`, branch `cleanup/20261019`. Completed 20 October 2026. Read [PLAN.md](PLAN.md), [LAYOUT_REPORT.md](LAYOUT_REPORT.md), and [TEST_PATHS_AFTER_LAYOUT.md](TEST_PATHS_AFTER_LAYOUT.md) before work.

## Result and scope

Moved **40 file/subtree paths covering 96 files** using filesystem renames. Every moved file remains present. No file was deleted. All moved non-Markdown files, including JSON specs, receipts, logs, patches, saved Python, deployment lists and checksums, retain their exact pre-move bytes. Markdown edits update navigation and path references; historical scientific conclusions remain unchanged.

The A reference documents are linked individually from [A's README](../A_ocr_development/README.md). Reader guides are linked from [B.a](../B_training_data/a_google_ocr/README.md); shared navigation links the relocated documentation index, organization guide and web-render guide. The [records index](../records/INDEX.md) now covers cleanup reports/evidence, contexts, owner sheets, archive, operations, review scratch and census05. `docs/harvest/` contains only `line_pipeline/`, `seg_census/`, and the requested two-line README.

`docs/ops/` held only `DISK1_inventory_brief.md`, a dated storage-inventory task brief rather than a live operations runbook, so it moved to records. The additional root leftovers were placed as follows: the documentation index and organization guide in shared; phase-1 validation and its exact environment alongside their verification snapshots; spellcheck routing among contexts; the SHEET-1 handoff, compatibility pointer and historical review scratch together in records. The harvest census05 readout moved intact to harvest records.

## Move table

Paths are repository-relative. Directory rows include every descendant; there are no symlinks or old-location copies. This table is also the complete list of **40 added alias rows** in [LAYOUT_ALIASES_2.tsv](LAYOUT_ALIASES_2.tsv).

| Old | New |
|---|---|
| `docs/CLEANUP_MERGE_REHEARSAL.md` | `docs/records/cleanup_20261017/CLEANUP_MERGE_REHEARSAL.md` |
| `docs/CLEANUP_MERGE_REHEARSAL_optionC.md` | `docs/records/cleanup_20261017/CLEANUP_MERGE_REHEARSAL_optionC.md` |
| `docs/CLEANUP_PLAN_20261017.md` | `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017.md` |
| `docs/CLEANUP_PLAN_20261017_api.md` | `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_api.md` |
| `docs/CLEANUP_PLAN_20261017_blinding.md` | `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_blinding.md` |
| `docs/CLEANUP_PLAN_20261017_inventory.md` | `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_inventory.md` |
| `docs/CLEANUP_PLAN_20261017_sourcing.md` | `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_sourcing.md` |
| `docs/CLEANUP_SR1_REPORT.md` | `docs/records/cleanup_20261017/CLEANUP_SR1_REPORT.md` |
| `docs/CLEANUP_STEP3_REPORT.md` | `docs/records/cleanup_20261017/CLEANUP_STEP3_REPORT.md` |
| `docs/CLEANUP_STEP4_REPORT.md` | `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md` |
| `docs/CONTEXT_20261019_segmentation_and_secondary.md` | `docs/records/contexts/CONTEXT_20261019_segmentation_and_secondary.md` |
| `docs/CONTEXT_20261019_sourcing.md` | `docs/records/contexts/CONTEXT_20261019_sourcing.md` |
| `docs/CONTEXT_20261019_spellcheck.md` | `docs/records/contexts/CONTEXT_20261019_spellcheck.md` |
| `docs/LINE_METADATA.md` | `docs/A_ocr_development/reference/LINE_METADATA.md` |
| `docs/LINE_SEGMENTATION.md` | `docs/A_ocr_development/reference/LINE_SEGMENTATION.md` |
| `docs/LINE_SEGMENTATION_METHOD.md` | `docs/A_ocr_development/reference/LINE_SEGMENTATION_METHOD.md` |
| `docs/LINE_SEGMENTATION_TESTS.md` | `docs/A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md` |
| `docs/MERGE_REPORT_20261017.md` | `docs/records/cleanup_20261017/MERGE_REPORT_20261017.md` |
| `docs/MR_C_REPORT.md` | `docs/records/cleanup_20261017/MR_C_REPORT.md` |
| `docs/MR_C_evidence` | `docs/records/cleanup_20261017/MR_C_evidence` |
| `docs/O4D_GEOMETRY.md` | `docs/A_ocr_development/reference/O4D_GEOMETRY.md` |
| `docs/PAGES_GUIDE.md` | `docs/A_ocr_development/reference/PAGES_GUIDE.md` |
| `docs/PAGES_OUTPUT_FORMAT.md` | `docs/A_ocr_development/reference/PAGES_OUTPUT_FORMAT.md` |
| `docs/PAGES_PIPELINE.md` | `docs/A_ocr_development/reference/PAGES_PIPELINE.md` |
| `docs/PAGE_LINES_ALGORITHM.md` | `docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md` |
| `docs/PAGE_LINE_SEGMENTS.md` | `docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md` |
| `docs/READERS_DOCAI.md` | `docs/B_training_data/a_google_ocr/readers/READERS_DOCAI.md` |
| `docs/READERS_TRANSKRIBUS.md` | `docs/B_training_data/a_google_ocr/readers/READERS_TRANSKRIBUS.md` |
| `docs/READERS_VISION.md` | `docs/B_training_data/a_google_ocr/readers/READERS_VISION.md` |
| `docs/SOL_ROUTING_spellcheck_20261017.md` | `docs/records/contexts/SOL_ROUTING_spellcheck_20261017.md` |
| `docs/owner_sheets` | `docs/records/owner_sheets` |
| `docs/archive` | `docs/records/archive` |
| `docs/ops` | `docs/records/ops` |
| `docs/review` | `docs/records/review` |
| `docs/WEB_RENDER.md` | `docs/shared/WEB_RENDER.md` |
| `docs/REPOSITORY_ORGANIZATION.md` | `docs/shared/REPOSITORY_ORGANIZATION.md` |
| `docs/README.md` | `docs/shared/DOCUMENTATION_INDEX.md` |
| `docs/VALIDATION.md` | `docs/records/verify_20261008/VALIDATION.md` |
| `docs/test-environment.txt` | `docs/records/verify_20261008/test-environment.txt` |
| `docs/harvest/census05` | `docs/records/harvest/census05` |

## Links fixed

- Rebased **246 Markdown/reference/inline-HTML link occurrences**; the exact old/new source and URL pairs are in [LAYOUT_LINK_FIXES_2.tsv](LAYOUT_LINK_FIXES_2.tsv).
- Verified **3,570 previously resolving local target occurrences** from the pre-move Markdown snapshot after relocation: **zero relocation regressions**. This checks file targets, not fragment anchors, external URLs or already absent private/bulk artifacts.
- Updated repository-path mentions across documentation, root README/AGENTS navigation, and relevant script documentation. Historical cleanup plans/move tables, immutable receipts, saved code and explicit other-worktree paths keep their original identities.
- Updated `scripts/generate_api_docs.py` so regenerating `docs/API.md` retains the new page-guide link.

## Retrieval aliases and callers

CLEAN4L3's 130 aliases are hardcoded in `greekocr/ops/data_root.py`. The instruction not to edit `greekocr/` is preserved: [scripts/layout_paths.py](../../scripts/layout_paths.py) loads the 40 companion TSV rows and extends the resolver table in memory. Both old and new identities participate in local lookup, historical external-mirror lookup and custody-shard attribution. Rows are ordered by both path lengths so a broad reverse alias for an earlier draft home cannot hide a newly moved reference file.

[tests/_paths.py](../../tests/_paths.py) imports the shared table/helper at session startup, retaining the existing in-memory loader for immutable documentation fixtures. The owner-sheet tests and metadata test translate their direct paths with the same helper. Repository owner-sheet builders, spec preparation, report generation and crop recovery use the helper; the cleanup report generator also maps its output destination. Explicit source paths in other checkouts remain bound to those checkouts.

The bridge is installed when `scripts.layout_paths` (or `tests._paths`) is imported. Package-only consumers importing `greekocr.ops.data_root` alone retain CLEAN4L3's original table; this pass does not change installed-package behavior. Repository callers affected by these moves import the bridge. No test has been newly skipped or weakened because a file moved.

The 40 parameterized resolver checks exercise each new row through relocated local lookup, historical mirror lookup, and the exact historical custody receipt for an absent input. The focused run passed: **150 passed, 7 skipped in 4.46s**. Its skips retain existing historical/absent-input reasons. The first focused attempt exposed 11 reverse-alias shadowing cases; ordering the combined table by both identities fixed them before the successful focused run and final suite.

## Full suite

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q -p no:cacheprovider --junitxml=/private/tmp/clean4l2-final.xml
```

**Suite summary: 0 failed / 0 errors; 6676 passed, 187 skipped, 9 warnings, 63 subtests passed in 164.64s (0:02:44).**

Native pytest summary:

```text
6676 passed, 187 skipped, 9 warnings, 63 subtests passed in 164.64s (0:02:44)
```

JUnit independently records `failures="0"` and `errors="0"` (6,926 cases including 63 subtests). The 187 skips match the preceding CLEAN4L3 full-suite count.

Logs and JUnit node dispositions: `/private/tmp/clean4l2-final.log`, `/private/tmp/clean4l2-final.xml`. No suite-selection changes, fixture substitutions or new missing-input skips were introduced in this pass.

## Preservation and Git boundary

All **478 files under `greekocr/`** were fingerprinted before the move and remain byte-identical. Bytecode/cache writes are disabled for testing. The live pipeline assets, deployment package, `origins/` and `verify/` remain in place.

No Git-writing command was issued: no staging, commit, checkout, reset, merge, push, index edit or Git metadata edit. Read-only Git queries/checks use the existing checkout. Other work occurred concurrently: the shared index and `cleanup/20261019` branch-ref fingerprints changed during this run; this pass did not cause or revert those changes. `git diff --check` passes.

## Final `ls docs`

```text
API.md
A_ocr_development
B_training_data
INVENTORY.md
STANDARD.md
VERIFY.md
cleanup_20261019
harvest
ocr_program_2026-10-06
origins
programme_20261019
records
shared
verify
```
