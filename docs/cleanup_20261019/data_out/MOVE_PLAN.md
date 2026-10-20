# CLEAN3A — proposed data relocation; no moves performed

Snapshot: `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33 HEAD -> cleanup/20261019`. Data root: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data/`; destination for each MOVE is `$GREEK_OCR_DATA_ROOT/<path>` with the repository-relative path unchanged. MB is decimal: 5,000,000 bytes; directory byte threshold is strictly >20,000,000, and extension threshold is ≥50 combined PNG/JPG/JSONL/JSONL.GZ/HTML files (case-insensitive). Nothing is removed from history.

`MOVE_PLAN.tsv` inventories **all 61,533 HEAD paths**, a conservative superset of the requested >5 MB and bulk-directory union. This avoids treating a recursive threshold on `docs/` or the repo root as permission to move source. `BULK_DIRECTORIES.tsv` lists direct and recursive metrics for every qualifying non-root directory; the repository root also qualifies recursively. Every descendant is covered, including source/configuration/record siblings. Decisions classify individual files, not whole qualifying directories. HEAD blob lengths come from `git cat-file`; every working regular file and symlink target was SHA256-hashed and its Git blob identity checked against HEAD. An independent recursive HEAD tree traversal (3,360 tree objects) confirmed that the index path set and object IDs exactly match all 61,533 HEAD blobs. Symlinks are measured as stored target text, not followed. Every producing commit is the exact result of `git log -1 --format=%h -- <path>`; it means last path touch, not necessarily original generation.

## Totals by kind

| Group | Inventoried count | Inventoried bytes | MOVE count | MOVE bytes |
|---|---:|---:|---:|---:|
| bundle | 11 | 169,310,442 | 11 | 169,310,442 |
| census-export | 90 | 413,773,463 | 82 | 413,575,400 |
| crop-set | 13,755 | 690,969,795 | 13,734 | 689,106,085 |
| key | 601 | 1,368,436,895 | 571 | 1,360,686,424 |
| log | 3,256 | 127,883,243 | 3,239 | 127,880,732 |
| model-output | 559 | 527,420,958 | 556 | 527,256,096 |
| montage | 3 | 1,065,866 | 3 | 1,065,866 |
| other | 41,168 | 3,491,513,896 | 34,443 | 3,281,859,804 |
| pool | 1,987 | 5,793,107,082 | 1,980 | 5,790,330,721 |
| sheet | 103 | 272,898,861 | 103 | 272,898,861 |

## Totals by top-level directory

| Group | Inventoried count | Inventoried bytes | MOVE count | MOVE bytes |
|---|---:|---:|---:|---:|
| (root files) | 12 | 4,232,898 | 0 | 0 |
| artifacts | 6,208 | 1,278,904,352 | 5,448 | 1,236,546,678 |
| collect_v3 | 53 | 352,480 | 0 | 0 |
| config | 10 | 2,226,340 | 0 | 0 |
| docs | 52,303 | 11,467,730,292 | 48,168 | 11,327,247,562 |
| greekocr | 350 | 5,092,461 | 0 | 0 |
| legacy_l1 | 260 | 2,508,044 | 0 | 0 |
| out | 155 | 8,111,238 | 127 | 7,945,215 |
| prototypes | 396 | 27,235,889 | 40 | 17,078,612 |
| scripts | 513 | 5,105,282 | 0 | 0 |
| seed | 4 | 8,320 | 0 | 0 |
| tests | 1,246 | 54,800,652 | 939 | 45,152,364 |
| worker | 23 | 72,253 | 0 | 0 |

Decisions: ASK: 19, KEEP: source: 6,763, KEEP: ≤ 5 MB and referenced by code/tests: 29, MOVE: 54,722. Proposed MOVE: **54,722 files / 12,633,970,431 bytes**. Oversized subset: **232 / 8,559,279,830 bytes**. Counts are unique paths, not distinct hashes; no hardlink/dedup or filesystem-allocation savings are assumed. Moving files and untracking them will not shrink existing `.git` history.

## Lead receipt reconciliation and custody

Inputs (preserved, never edited):

- `docs/records/harvest/seg_census/OUT_OF_GIT_RECEIPT.md`
- `docs/records/labelfix/spellcheck/OUT_OF_GIT_RECEIPT.md`
- `docs/records/harvest/collect_v3_admission/OUT_OF_GIT_RECEIPT.md`
- `docs/records/harvest/pilots_v2/RECEIPTS_OUT_OF_GIT.md`

`RECEIPT_RECONCILIATION.tsv` checks every parseable per-file receipt row against this HEAD: 13,230 rows; 213 tracked byte/hash matches; 23 conflicts. “OUT of git” in the spellcheck, small-segment and pilot receipts describes their source worktrees at receipt time, not proof those bytes were moved into the new data root. Paths absent from this HEAD are custody follow-ups, not added to MOVE totals. The spellcheck summary additionally covers 988 files / 2,250,088,199 bytes at `artifacts/sf7_rc1/output_3687228/`, with 985 hashes in its tracked READBACK_RECEIPT; the three remaining files are individually tabled. Do not double-count those 988 with table rows. The pilots receipt covers 3,460 files / 7,273,359 bytes in the inventory worktree; its committed RECEIPTS_MANIFEST.tsv remains authoritative. The six small-segment files listed by the sourcing lead remain custody obligations outside this HEAD. Symlink rows are recorded separately in RECEIPT_LINKS.tsv; their target strings are not mistaken for SHA256s.

**Receipt contradictions requiring reconciliation:** `RECEIPT_CONFLICTS.tsv` lists both HEAD and lead bytes/hashes for every conflict. These are different versions at the same relative paths. The HEAD hash in MOVE_PLAN.tsv is the version inventoried here; it does not invalidate the source-worktree version in the lead receipt. Preserve both and settle versioned custody before copying to a shared mirrored destination; never overwrite or call the older receipt wrong. Conflicting paths:

- `artifacts/cq4/aggregate_receipt.json`
- `artifacts/cq4/build_hashes.json`
- `artifacts/cq4/build_receipt.json`
- `artifacts/cq4/closure/topup_reread_000.json`
- `artifacts/cq4/contexts.json`
- `artifacts/cq4/keys/topup_reread_000.json`
- `artifacts/cq4/lead_queue.jsonl`
- `artifacts/cq4/lead_queue.png`
- `artifacts/cq4/limit_probe.log`
- `artifacts/cq4/logs/topup_reread_000_final.md`
- `artifacts/cq4/logs/topup_reread_000.codexlog`
- `artifacts/cq4/quarantine/topup.jsonl`
- `artifacts/cq4/quarantine/wcap.jsonl`
- `artifacts/cq4/reread_build_receipt.json`
- `artifacts/cq4/reread_contexts.json`
- `artifacts/cq4/reread_ledger.json`
- `artifacts/cq4/scans/topup_reread_000.json`
- `artifacts/cq4/tools/build.py`
- `artifacts/cq4/tools/scan_rollout.py`
- `artifacts/cq4/tools/workflow.py`
- `artifacts/cq4/truth/topup.jsonl`
- `artifacts/cq4/truth/wcap.jsonl`
- `docs/records/labelfix/spellcheck/R2/CQ4_REPORT.md`

The segmentation lead explicitly keeps `artifacts/n1/n1_v1_train.sha256`, `docs/records/labelfix/lqb/truth_v1_1.sha256` and the 1.7 MB `segeval1/keys/census02_segmentation_evidence.jsonl` in git. This plan keeps them. The small frozen evidence is a documented lead exception to general bulk placement; `KEEP: source` includes retained provenance records and does not claim the JSONL is executable source. Literal references alone do not make a bulk artifact source. Small directly referenced test fixtures use the explicitly allowed ≤5 MB KEEP decision; audit that exception before enforcing a zero-bulk interpretation.

**SEGEVAL1.bundle must be preserved as a file.** Its on-disk bundle header names `b3b5aaa19835ac626af6576da37e008386b26879 refs/heads/segeval1-artifacts`; read-only `git cat-file -t` returns 128 (object unavailable). The lead also states that head is not in history. Required receipt: 147,025,055 bytes, SHA256 `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`. Before any future untracking, copy without overwrite to the mirrored data-root path, hash-read it back, retain the bundle header/ref plus producing commit and readers in the git receipt, and establish durable custody. Do not substitute a pointer to repository history or regenerate this bundle in place.

`candidate_order_KEEP.jsonl`: 476,509,196 bytes, SHA256 `08b1b5a054bd5161534ac637c81b4155be6d4d6c843ab41421f584b0c285dd07`. The lead says no semantic code reader opens this sampling key by name. It is still a protected path in historical guards. Moving this key and the bundle makes the following stored checks report missing if rerun unchanged:

- `docs/records/harvest/seg_steps/s1/initial_hashes.json`
- `docs/records/harvest/seg_steps/s2/initial_hashes.json`
- `docs/records/harvest/seg_steps/s3/initial_hashes.json`
- `docs/records/harvest/seg_steps/s4/initial_hashes.json`
- `docs/records/harvest/seg_steps/gate_rereport/initial_scope.json`
- `docs/harvest/line_pipeline/gate03/part3-initial-hashes.json`

Preserve those historical records unchanged. A new replay wrapper must look up moved protected paths by their original names in the relocation receipt, resolve through GREEK_OCR_DATA_ROOT, and verify the original recorded hash. Report relocation separately from an altered or missing artifact; do not silently drop guards or rewrite their historical success claims. Other moved historical inputs need the same treatment.

## Reader changes required before relocation

`readers` is a case-sensitive literal-basename grep over all regular text files in the working tree, with hidden/ignored files included; `.git/` and these generated planning outputs are excluded, and symlink directories are not followed. Each cell lists distinct referencing files (self-reference excluded), or `none`; it is not a semantic dependency claim. Binary/compressed content is not decoded. Short names and shared basenames produce intentional false positives. `READERS_TO_UPDATE.tsv` provides every MOVE/code-or-test basename pair with a one-line fix; 3,343 unique source readers / 147,952 pairs. It includes archived code, producers and documentation strings inside code, so review literal access sites before changing them. A basename match alone cannot establish that every same-named MOVE path will break that reader. Actual direct accesses will fail after relocation unless resolved or staged; historical reports should stay historical.

Use a resolver requiring `GREEK_OCR_DATA_ROOT`, accepting an original repository-relative receipt key, rejecting absolute/`..` escapes, and checking expected bytes/hash. Existing code roots must continue locating source and small retained assets inside the repository. Resolve only the relocated data paths; do not replace a general repository ROOT wholesale. For offline fixtures, provision bytes by receipt before tests, and fail with a retrieval instruction when missing; do not skip coverage. HTML sheet relative image/JSON links need the whole mirrored asset subtree or a receipt-backed staging tree; file:// browser access cannot directly read a shell env var. Package/build scripts and generated outputs need the data-root destination as well as input lookup.

Direct access sites checked in source (separate from the broad basename candidates):

| Source site | Behavior after the proposed move | One-line fix |
|---|---|---|
| `scripts/numerics/n1g.py:310` | Passes the moved frozen `truth_v1_1.jsonl` to `lqb.run`. | Resolve `docs/records/labelfix/lqb/truth_v1_1.jsonl` under GREEK_OCR_DATA_ROOT before calling the scorer. |
| `scripts/secondary/ru2t_apply_lead.py:78` | Supplies the moved truth path as the scorer's `--truth` argument. | Pass the receipt-resolved external truth path to `--truth`, keeping the code/registry paths in the repo. |
| `scripts/secondary/ru2t_delivery.py:127` | Binds the moved frozen truth to its scoring input. | Bind the original truth receipt key to GREEK_OCR_DATA_ROOT and verify its frozen SHA256. |
| `tests/test_lqb5.py:14,23` | Opens and hashes the moved truth directly under `lqb.DEFAULT`. | Resolve only the truth file through its external receipt; retain manifest/sidecar lookup in the repo and provision the truth before the test. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/classify_population.py:53–54` | Hashes the moved census gzip before processing it. | Replay through a wrapper resolving `docs/records/harvest/collect_v3_admission/segeval1/cells/population_cells.jsonl.gz` at the data root without rewriting historical source. |
| `docs/records/harvest/seg_steps/gate_rereport/analyze.py:262–264` | Tracks and opens that moved census gzip. | Use a receipt-backed replay input resolver preserving the historical original-path/hash key. |
| `tests/glyphs/test_initial_batches.py:13–14` | Globs fixture crop directories; moving most PNGs leaves an incomplete pool even though no moved basename is literal here. | Build a receipt-backed fixture view combining retained repo fixtures and moved data-root crops under their original relative names before globbing. |

Producer-only examples: `scripts/numerics/n1_apply_train.py:133` names `n1_v1_train.jsonl` as an output default; route the new output to the data root. `scripts/numerics/n1r_receipt.py:96` mentions it in report prose, so that mention alone needs no data-reader patch. Tests that construct same-named files in `tmp_path` are independent fixtures and should keep doing so.

One-line fix for every literal source-reference candidate (full target list is in `READERS_TO_UPDATE.tsv`):

| Reader | MOVE basename pairs | One-line fix |
|---|---:|---|
| `artifacts/cq1/RUN_CMD.sh` | 139 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/RUN_CMD_r1b.sh` | 104 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/launchers/run_bed.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/bind_v2_overlap.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/build.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/build_cq1.py` | 169 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/ledger.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/preflight.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/preflight_r1b.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/reference_adapter.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/scan_packs.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/scan_packs_r1b.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/scan_rollout.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/scan_rollout_v41.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/scan_rollout_v42.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/scan_rollout_v43.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/score_cq1.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/score_cq1_r1b.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/test_scan_rollout_v43.py` | 230 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq1/tools/validate_build.py` | 390 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/AGGREGATE.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/BUILD.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/BUILD_REREAD.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/RESCAN_EXISTING.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/RUN_ALL.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq4f_before/tools/build.py` | 415 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq4f_before/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq4f_before/tools/scan_rollout.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq4f_before/tools/workflow.py` | 88 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evaluate.py` | 34 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/build_cq6.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r1_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r1_extract.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r1_model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r1_train.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r2_manifest.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r2_score.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r2a_digest.py` | 135 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r2a_job.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/r2a_run.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/evidence/seal_cq6.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/slurm/evaluate.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/slurm/prepare.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/slurm/smoke.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/slurm/train.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/test_instrument.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6_package/verify_deploy.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evaluate.py` | 34 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/build_cq6c.py` | 123 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r1_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r1_extract.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r1_model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r1_train.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r2_manifest.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r2_score.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r2a_digest.py` | 135 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r2a_job.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/r2a_run.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/evidence/seal_cq6c.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/slurm/evaluate.sbatch` | 32 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/slurm/prepare.sbatch` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/slurm/smoke.sbatch` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/slurm/train.sbatch` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/test_admission.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/test_instrument.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq6c_package/verify_deploy.py` | 71 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/BUILD.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/IMPORT.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/RUN.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/VERIFY.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/baseline/workflow.py` | 91 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/cq7.py` | 164 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/seal.py` | 122 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/cq7/test_cq7.py` | 137 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/packs/solcap_topup/topup_reread_000/r1/zoom/record.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/packs/solcap_topup/topup_reread_001/r1/zoom/write.py` | 96 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/packs/solcap_topup/topup_reread_002/r1/zoom/record.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/packs/solcap_topup/topup_reread_003/r1/zoom/record.py` | 96 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/packs/solcap_topup/topup_reread_004/r1/zoom/write.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/packs/solcap_wcap/wcap_reread_000/r1/zoom/write.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/prior_cq4/inventory.py` | 316 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/prior_cq4b/inventory.py` | 423 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/prior_cq4b/test_inventory.py` | 275 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/build.py` | 414 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/build_cq6.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/build_cq6c.py` | 123 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/closure.py` | 96 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/finalize.py` | 438 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/inventory.py` | 256 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/report_results.py` | 128 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/seal_cq6.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/seal_cq6c.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/swap_controls.py` | 102 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/test_inventory.py` | 394 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/validate_build.py` | 127 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/verify_cq4f.py` | 128 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/cq4/tools/workflow.py` | 102 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/labelfix_sf6/frozen_sf5_05f2dafb/greekocr/labelfix/release_gate.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/labelfix_sf6/frozen_sf5_05f2dafb/greekocr/labelfix/text.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/labelfix_sf6/frozen_sf5_05f2dafb/scripts/labelfix/clariden/l1_common.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/n1/build_n1l.py` | 111 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/n1/n1g/predecessor/n1_apply_train.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/n1/n1g/predecessor/n1_gate.py` | 91 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/r2_resolve/b6_assemble.py` | 407 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/r2_resolve/b6_gate.py` | 36 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/r2_resolve/b6_resolve.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/r2_resolve/b6_verify.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/r2_resolve/b6b_redeal.py` | 99 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/r2_resolve/b6c_verify.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/phase1/crops_get.original.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/phase1/crops_get.phase1.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/phase1/resume_sheets.py` | 43 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/phase1/sitecustomize.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/phase1/verify.py` | 111 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/ru3t1/prepare_resume.py` | 315 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/ru3t1/ru2t_coverage.bound.py` | 59 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/ru1/ru3t/ru3t1/verify.py` | 98 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/FINAL_SCORE.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/REREAD.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/RUN.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/SCORE.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/au1c/context_build_once.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/au1c/rescan_build_once.py` | 69 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/au1c/scanner/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/au1c/scanner/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/au1c/scanner/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/au1d/build_once.py` | 96 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/build.py` | 256 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/check_au1b.py` | 144 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/check_au1c.py` | 239 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/check_au1d.py` | 188 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/check_final_score.py` | 83 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/check_scoring.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/driver.py` | 146 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/opus_keys/vendor/adjudicate/__init__.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/opus_keys/vendor/adjudicate/deck.py` | 82 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/opus_keys/vendor/adjudicate/protocol.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/opus_keys/vendor/adjudicate/score.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/accent_initial_001_au1b/scanner/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/accent_initial_001_au1b/scanner/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/accent_initial_001_au1b/scanner/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1b/scanner/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1b/scanner/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1b/scanner/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1c/scanner/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1c/scanner/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1c/scanner/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1d/scanner/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1d/scanner/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/runs/capital_initial_001_au1d/scanner/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/audit/validate.py` | 209 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/build_rb7.py` | 55 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/convert_rb7.py` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/report_rb7.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/score_rb7.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sf7_rc1/validate_rb7.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sq1/census.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sq1/find_c1.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sq1/finish_report.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sq1/run_line.py` | 46 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sq1/verify.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sx1/extract.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sx1/extract_v2.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/sx1/validate_v2.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/tr2/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/wt1/build_census.py` | 37 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `artifacts/wt1/build_report.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `collect_v3/audits.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/cards.py` | 32 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/commit_helper.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/common.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/config.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/convention_context.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/detach.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/egress.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/exclusions.py` | 123 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/launch_detached.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `collect_v3/ledger.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/offline.py` | 46 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/pipeline.py` | 87 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/planner.py` | 269 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/portable.py` | 85 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/reader.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/resolution.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/retention.py` | 21 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/review.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/routes/providers.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/rules.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/run.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/runner.py` | 51 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/storage.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/tests/limiter_worker.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/tests/resume_worker.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/tests/test_contracts.py` | 45 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/tests/test_rev2.py` | 112 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/tests/test_w1c.py` | 305 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/tests/test_w1d.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/transport.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/admission.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/assembly_fix.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/classify.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/conventions.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/features.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/geometry/io.py` | 99 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/geometry/magnitude.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/geometry/ownership.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/lookalike_rule.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/vendor/robots.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `collect_v3/verify_offline.py` | 51 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_common.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_detect.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_infer.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_inventory.py` | 271 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_job.sbatch` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_prepare.py` | 44 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_run.py` | 29 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_runtime.py` | 17 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/scripts/labelfix/clariden/l1_verify.py` | 21 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/archive/l1_20261017/tests/labelfix/test_l1.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/A_language_script/analysis_A.py` | 33 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/B_content_style/analysis_B.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/C_geometry_quality/analysis_C.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/D_duplicates_pages/analysis_D.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/aggregate.py` | 286 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/compile_decisions.py` | 282 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/compile_report.py` | 261 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/analysis/write_anomalies.py` | 29 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/blind_checks_v1/c0/c0_make.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/blind_checks_v1/t4c/agg.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/blind_checks_v1/t4c/t4c_agg.py` | 21 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/blind_checks_v1/t4c/t4c_make.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/c1_agg.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/build.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/build_owner39.py` | 82 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/guard_commit.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/owner39_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/owner39_score.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/owner39_validate.py` | 43 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/zoom/ans.py` | 36 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/zoom/crop.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/zoom/pix.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r2/zoom/add.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/zoom/asc.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/zoom/w1.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/zoom/z.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/ascii.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/crop.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/crop.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/w.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/score.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/test_efficiency.py` | 79 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/test_owner39.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/validate.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/c1/efficiency/verify_owner39_rasters.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/append_adm2_poly1850.py` | 98 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/append_adm3_headings_caps.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/build_w1_masked_1d.py` | 74 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/build_w1_originals_v3.py` | 61 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/guard_adm2_commit.py` | 91 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/guard_adm4_commit.py` | 110 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/test_adm2_poly1850.py` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/test_adm3_headings_caps.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/test_adm4_originals_v3.py` | 71 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_admissions/update_adm4_ledger.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/release_exclusions/validate_n1_registration.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/segmentation_gallery/build_gallery.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/segmentation_gallery/build_sg2.py` | 108 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/segmentation_gallery/guarded_commit.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/w2_gate/check_live.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/w2_gate/guard_commit.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/w2_gate/validate.py` | 76 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3/weak_ledger/build_ledger.py` | 236 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/admw2/package_commit.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/admw2/test_artifacts.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/admw2/test_builder.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/admw2/verify_outputs.py` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/audit_codec.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/build_release_admission.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/compare_adm5c.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/guard_adm5_commit.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/guard_crops_commit.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/calibrate.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/finish_w1.py` | 36 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/guard_nw1b_commit.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/merge_cache.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/prepare_w1.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/reissue.py` | 72 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/report.py` | 62 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/nw1b/verify.py` | 89 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/audit_cp3b_geometry.py` | 61 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/audit_cp4_cache.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/calibrate_cp5p.py` | 71 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/calibrate_cp5pb.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/build.py` | 100 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/common.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/finalize_geometry_cp7a3.py` | 51 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/freeze.py` | 46 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launch_cp7.sh` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launch_cp7_r2.sh` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launch_cp7_r2_b.sh` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launch_population_geometry.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/run_bed.sh` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/measure.py` | 264 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/prepare_population_geometry.py` | 122 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/prepare_r2.py` | 65 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/r2/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/r2/launchers/run_bed.sh` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/r2/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/r2_common.py` | 17 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/recompute_gate_geometry.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/recover_cp7c2_a.py` | 126 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/runtime.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/runtime_r2.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/score_cp7b.py` | 212 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/score_cp7d.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/score_r2.py` | 219 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/tools/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/tools/scan_rollout.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/verify_artifacts.py` | 83 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp7/verify_geometry_cp7a3.py` | 34 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/bind_outputs.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/build_manifest.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/compare_admw2.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/custody.py` | 138 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/package_commit.py` | 76 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/qualify.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/cp8a/restore_cp5.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/diagnose_cp5.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/freeze_truth.py` | 45 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/guard_cp2_commit.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/guard_cp3_commit.py` | 134 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/guard_cp4_commit.py` | 71 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/guard_cp5_commit.py` | 148 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/guard_cp6_commit.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/prepare_cp3_geometry.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/prepare_cp4_geometry.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/prepare_cp5_separators.py` | 279 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/review_cp4c.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp1.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp2.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp3.py` | 34 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp4.py` | 113 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp4_controls.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py` | 308 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/seg/verify_cp6.py` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/classify_population.py` | 59 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/distributions.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/export_remote.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/fetch_samples.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/materialise_1b.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/package.py` | 73 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/package_1b.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/prepare_reconstruction.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/reduce_population.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/stream_missing_crops_remote.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/validate.py` | 143 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/validate_1b.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells/write_handoff.py` | 100 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/analyse.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/draw_samples.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/pass1_census.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/pass2_small.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/percentiles.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/sheets.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/typology.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/typology_md.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/baseline/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/check_baseline_drift.py` | 76 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/check_calibration_drift.py` | 68 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/package_commits.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/replay_calibration.py` | 77 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/replay_segeval1.py` | 87 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/validate_replays.py` | 105 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/deskew/write_handoff.py` | 175 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/greekocr/harvest/filtering_assets/segmentation-policy.js` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/package_commits.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/replay.py` | 44 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/validate.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate/write_handoff.py` | 136 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/greekocr/harvest/filtering_assets/segmentation-policy.js` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/tests/test_seg_gate.py` | 28 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/package_commits.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/replay.py` | 44 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/validate.py` | 114 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/gate2/write_handoff.py` | 140 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/launch.sh` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/launchers/run_bed.sh` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/segeval1_score.py` | 74 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/launchers/run_type.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss1_q1.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss2_q2.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss3_sample.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss4_packs.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss4_type2.py` | 68 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss4c_fixtures.py` | 65 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss4c_launcher.py` | 267 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss5_merge.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss6.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss7.py` | 29 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss8.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tests/test_ss9.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/build_type2_packs.py` | 70 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/build_type_packs.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/map_type.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/run_type.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/scan_type_packs.py` | 66 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss1_q1.py` | 61 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss2_q2.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss3_sample.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss4_common.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss4b_replay_fixture.py` | 298 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss4c_replay_fixture.py` | 337 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss5_merge.py` | 103 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss6_build.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss6_validate.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss7_key.py` | 29 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss7_owner_marks.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss8_key_v2.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss8_recheck.py` | 77 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/small_segments/tools/ss9_survivors.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/test_score.py` | 59 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/build_packs.py` | 56 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/export_old_metadata.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/export_remote.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/materialize.py` | 34 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/package.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/prepare_draw.py` | 89 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/runtime.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/scan_rollout.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/segeval2_package.py` | 116 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/segeval2_rescan.py` | 112 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/segeval2_verify.py` | 160 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/verify.py` | 115 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/segeval1/tools/write_handoff.py` | 171 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/split1/build_sheet.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/split1/build_split1.py` | 102 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/split1/headless_qa.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/split1/sheet_adapter.js` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/split1/test_split1.py` | 90 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/split1/verify_commit_scope.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/stage_crops.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/collect_v3_admission/test_stage_crops.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/anemi_probe.py` | 85 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/commit_gr.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/curate.py` | 59 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/funnellib.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/institutions.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/make_handoff.py` | 86 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/make_sheets.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/openarchives_probe.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/probe.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/rebind_catalogues.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/recheck_physical.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/reference/acquire_oa.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/reference/acquire_pdf.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/reference/pilotlib.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/report.py` | 261 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/funnel_v1/gr/validate.py` | 123 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/assessments.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/audit_local_metadata.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/build_inventory.py` | 328 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/commit_inventory.py` | 86 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/fetch_inventory.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/hf_metadata_check.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/probe_lines.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/sanitize_receipts.py` | 47 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/inventory_v2/validate_inventory.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/build_png_codec.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/crop_probe.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/compare_empty_fit_repair.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/empty_fit_probe.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/empty_fit_probe.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/profile.sbatch` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/profile_native.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput.sbatch` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_02.sbatch` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_03.sbatch` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_native.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_native_01.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_native_02.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_native_03.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/efficiency/throughput_native_04.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/geometry_probe.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/geometry_probe.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/historical_fd4/launch_full_census.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/launch_full_census.sh` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/clariden/launch_full_census_6261_historical.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/baseline/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/baseline/line_pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/baseline/line_pipeline_census.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/baseline/test_line_pipeline.py` | 339 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part2-baseline/greekocr/harvest/line_pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part2-baseline/greekocr/harvest/line_pipeline_census.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part2-baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part2-baseline/tests/test_content_gate.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part2-baseline/tests/test_line_pipeline.py` | 339 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part2_analysis.py` | 37 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part3-baseline/greekocr/harvest/line_pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part3-baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part3-baseline/tests/test_content_gate.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part3-baseline/tests/test_line_pipeline.py` | 339 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part3_analysis.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/part3_scope_guard.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/line_pipeline/gate03/rebuild_versions.py` | 21 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/mixed/build_source.py` | 580 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/analyse.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/audit.py` | 385 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/commit_o1.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/fallback.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/fetch_catalogues.py` | 53 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/finalize.py` | 113 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/audit_duplicates.py` | 118 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/build_release.py` | 68 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/check_candidates.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/commit_o2.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/common.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/finalize_o2.py` | 154 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/o2/validate_release.py` | 136 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/oa_rebind_v1/validate.py` | 91 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/parliament/source_snapshots/parliament_outputs-e132c848b056d415ef603abe5e3108d9cddc80456f46d35ace2436355267d631.py` | 620 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/acquire.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/acquire_oa.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/acquire_pdf.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/acquire_perseus.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/acquire_pg.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/acquire_wiki.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/ajax_geometry.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/ajax_outputs.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/ajax_reframe.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/align.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/blind.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/classify.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/delta_p1b.py` | 67 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/discover.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/front_matter.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/make_files.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/p1b_align.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/pilotlib.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/prepare_detector.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/process_reads.py` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/read_pilots.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/replace_oa.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/report.py` | 224 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/report_p1b.py` | 156 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/rerun_p1b.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/sheets.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/stage_handoff.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/validate.py` | 160 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/pilots_v2/validate_p1b.py` | 132 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/guarded_commit.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/l1e_sample/guarded_commit.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/l1e_sample/run.py` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/l1e_sample/tests/test_guarded_commit.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/l1e_sample/tests/test_ownership.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/l1e_sample/tests/test_runner.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/audit_dev.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/explain_losses.py` | 32 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/guarded_commit.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/make_focus.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/package_handoff.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/probe.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/record_review.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/run.py` | 68 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/summarize.py` | 184 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/tests/test_foreign_ink.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/verify_step0.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/masking/write_report.py` | 196 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/run_f2.py` | 155 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/summarize.py` | 265 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/compare_mock.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/detector_import_probe.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/detector_page_probe.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/guarded_commit.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/phase0_inventory.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/phase0_launch.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/phase0_mask.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/phase0_verify.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/prepare_rate_selection.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/receipts/t6f2/setup_initial.py` | 32 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/t6f2_gate.py` | 87 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/t6f2_setup.py` | 32 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/t6f2_validate.py` | 90 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_clariden/validate_receipts.py` | 114 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/guarded_commit.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/locked/guarded_commit.py` | 75 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/locked/prepare.py` | 36 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/locked/run_locked.py` | 85 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/locked/test_locked.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/run.py` | 125 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/test_run.py` | 82 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_full/verify.py` | 66 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/guarded_commit.py` | 89 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/make_sheets.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/matcher.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/run_diag.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/test_matcher.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/verify_artifacts.py` | 110 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/diag/write_report.py` | 146 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/guarded_commit.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/run.py` | 31 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_pilot/test_run.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_test/guarded_commit.py` | 110 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_test/harm.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_test/run.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/v2_test/test_run.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/attempts/materializer_source.py` | 107 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/build.py` | 75 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/guarded_commit.py` | 70 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/launchers/run_bed.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/prepare_launchers.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/reference_adapter.py` | 109 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/test_caps1.py` | 177 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/tools/ledger.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/tools/map_answers.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/tools/replay_literal.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/tools/scan_packs.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/tools/scan_rollout.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps1/write_handoff.py` | 322 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/attempts/pipeline_attempt1.py` | 79 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/build.py` | 74 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/guarded_commit.py` | 126 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/public_run_bed_before.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/run_bed.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/pipeline.py` | 84 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/prepare_launchers.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/reference_adapter.py` | 109 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/test_caps3.py` | 141 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/tools/ledger.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/tools/map_answers.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/tools/replay_literal.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/tools/scan_packs.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/tools/scan_rollout.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/caps3/write_handoff.py` | 264 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/component_audit.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/guarded_commit.py` | 88 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/build.py` | 66 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/public_run_bed_before.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/run_bed.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/prepare_launchers.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/rebuild_c2b.py` | 165 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/reference_adapter.py` | 109 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/test_kosmo2.py` | 150 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/ledger.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/map_answers.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/replay_literal.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/scan_packs.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout_v41.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout_v42.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/score_kr3.py` | 249 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/test_scan_rollout_v41.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/test_scan_rollout_v42.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/mirror/scan.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/build.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/public_run_bed_before.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/run_bed.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/prepare_launchers.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/reference_adapter.py` | 119 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/test_ruc1.py` | 76 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/tools/ledger.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/tools/map_answers.py` | 39 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/tools/replay_literal.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/tools/scan_packs.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/tools/scan_rollout.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/ruc1/tools/score_ruc2.py` | 327 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/run.py` | 107 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/t6g/guarded_commit.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/t6g/pack.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/t6g/test_pack.py` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/test_contract.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/verify.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/build.py` | 55 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/closure.py` | 46 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/finalize.py` | 115 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/launch_all.sh` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/launch_repack.sh` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/launchers/run_bed.sh` | 43 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/prepare.py` | 72 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/rebuild.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/repack.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/repack_config.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/runtime.py` | 47 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/score.py` | 32 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/test_w2c1.py` | 61 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/test_w2c1c.py` | 289 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/ledger.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/map_answers.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/owner39_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/owner39_validate.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/scan_packs.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/recut_v1/w1_masked/w2c1/tools/scan_rollout.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/round1/pilot_core.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/bind_dates.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/census.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/census_kosmopolis_bounded.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/classify.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/commit_gr.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/compact_images.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/enrich_machine.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/f2lib.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/finish_elstat.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/handoff.py` | 51 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/inspect_catalogues.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/make_patch.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/pilotlib.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/pipeline.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/prepare_commit.py` | 82 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/process.py` | 29 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/clipping.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/io.py` | 99 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/magnitude.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/ownership.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/span.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/p1/pilotlib_original.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/p1/prepare_detector.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/p1/process_reads.py` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/reference/p1/read_pilots.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/report.py` | 153 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/review_panels.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/sample.py` | 55 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/survey.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sample_v1/gr/validate.py` | 114 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/assembly_fix.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/commit_helper.py` | 75 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/conventions.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/evaluate.py` | 178 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/review_panels.py` | 139 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/screen.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/screen_v1/validate.py` | 98 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/b2_evidence/readback-tests.py` | 65 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/b2_evidence/verifier-exact.sh` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/compare_suites.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/finalize_package.py` | 36 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/jobs/census.sbatch` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/jobs/common.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/jobs/parity.sbatch` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/jobs/regression.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/mock_batch.py` | 98 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/mock_segmentation.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/mock_split_stage.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-secondary/scripts/secondary/ru1_decide.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/__main__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/admission.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/codec_coverage.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/common.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e1_common.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e1_eval.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e1_readout.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_bakeoff.py` | 33 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_cllg_contract.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_models.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_native.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_parity.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_reader_parity.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_teachers.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/e2_warmstart.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/extract_lines.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/line_categories.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_adjudicate.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_common.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_fetch.py` | 278 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_import_datasets.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_models.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_partition.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o4b_textlayer_lines.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/bench/o5_runtime.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/audit.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/build.rs` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/codec.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/composer.rs` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/corpus.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/custody.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/distort.rs` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/import_real.rs` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/main.rs` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/measure.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/recipe.rs` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/render.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/select.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/factory/src/shard.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/ops/watch_proc.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/ops/watch_slurm.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/pipeline/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/pipeline/page_ocr_detector.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/pipeline/recognize.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/pods/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/pods/pi_pod.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/rec/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/rec/openocr_vendored/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/rec/openocr_vendored/common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/rec/openocr_vendored/rctc_decoder.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/rec/openocr_vendored/svtrv2_lnconv_two33.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/rec/svtrv2_model.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4b_archive.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4b_datasets.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_audit.py` | 133 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_audit_anemi.py` | 154 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_common.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_discover_anemi.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_discover_archive.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_discover_other.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_discover_parliament.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_finalize.py` | 139 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_probe_media.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_probe_print.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/o4c_record_fixtures.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/parliament_pdf_cache.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/r2_cllg_env.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/scripts/fetch/r2_cllg_worker.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/seed/node_scripts/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/seed/node_scripts/build_parity_crops.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/seed/node_scripts/fetch_parliament_s2.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/seed/node_scripts/node_cllg_bakeoff.sh` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/seed/node_scripts/node_vouli2.sh` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_audit.py` | 133 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_audit_anemi.py` | 154 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_common.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_anemi.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_archive.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_other.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_parliament.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_finalize.py` | 139 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_media.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_print.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/source_clis/scripts/fetch/o4c_record_fixtures.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/cer.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/ckpt_io.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/ctc_health.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/data.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/detector_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/eval_cer.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/heads.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/mix.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/train/train.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/_records.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/font.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/line_features.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/sources.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/strata.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/cli.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/docling_plugin.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/model.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/options.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/orientation.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/recognizer/__init__.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/recognizer/ckpt_io.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/recognizer/codec.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/recognizer/inference.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/recognizer/model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/docling_plugin/recognizer/strips.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/node_envs.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/deploy/pods.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/baseline.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/boundary_evidence.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/columns.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/components.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/evaluate.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/foreign_ink.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/ink.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/letters.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/line_structure.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/lines_api.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/orientation.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/orientation_guides.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/orientation_regions.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/oriented_page.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/page_font.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/page_lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/page_text_lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/pixel_segments.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/readability.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/recut.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/report.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/statistics.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/synthetic.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/table_lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/glyphs/vertical_recut.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/admission.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/application_identity.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/cli.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/collection.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/core.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/cyrillic.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/segmentation-policy.js` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/service.mjs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/geometry_observations.py` | 84 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_adapters.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_parallel.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_runtime.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_sources.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/lookalikes.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/mixed.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/montage.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/montage_controls.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/neighbour_words.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/numeric_cells.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/openarchives.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/orientation_screen.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/page_reads.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/parliament.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/parliament_geometry.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/parliament_http.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/parliament_provenance.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/pipeline.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/qualified_admission.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/readers.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/regate.py` | 55 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/report.py` | 228 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/round1.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/round1_reads.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/round1_rescue.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/row_inclusion.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/seg_qualification.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/separator_inventory.py` | 260 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/serbian.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/text_primitives.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/wikisource.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/build_lexicon.py` | 17 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/candidates.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/constraints.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/ctc_align.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/deck.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/deck_serve.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/ingest_decisions.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/ink.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/lexicon.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/markshape.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/markshape_train.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/pull_firefox.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/rules.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/sample.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/tei_extract.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/text.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/textstage.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/labelfix/validate.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/ops/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/ops/rate_limit.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/ops/receipts.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/ops/secrets.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/ops/watch.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/api.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/boundaries.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/cli.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/delivery.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/font.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/layout.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/options.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/outputs.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/pixels.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/provenance.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/records.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/render.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/statistics.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/structure.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/tables.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/pages/torch_prototypes.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/cllg.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/kalchas.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/ours.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/paddle_r01.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/services/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/services/docai_driver.py` | 62 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/services/docai_manifest.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/services/google_docai.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/services/google_vision.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/readers/services/transkribus.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/adjudicate.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/extract.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/geometry.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/geometry_evaluate.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/geometry_measure.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/importers.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/partition.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/sources/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/sources/_runner.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/sources/discovery.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/sources/parliament.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/sources/web_render.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/real/sources/web_sources.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/score/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/synth/__init__.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/types.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/verify/__init__.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/verify/calibration.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/verify/cli.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/verify/images.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/verify/judges.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/verify/text.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/warmstart/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/bootstrap.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/filter_crop_paths.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/filter_worker.sbatch` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/package.py` | 33 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/worker.py` | 311 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/filter_runtime/src/main.rs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/verify_filter_parity.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/tests/test_fp3_external_crop_input.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/tests/test_fp3_numeric_adjacency.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/tests/test_line_pipeline.py` | 339 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/release_gate_sf7.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/greek-page-ocr-wave2/scripts/clariden/common.sh` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/worker/box-length-policy.js` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/parity_check.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/prepare_config.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/remote_evidence/census03.sbatch` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/build_png_codec.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/crop_probe.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/compare_empty_fit_repair.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/empty_fit_probe.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/empty_fit_probe.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/profile.sbatch` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/profile_native.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput.sbatch` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_02.sbatch` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_03.sbatch` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_native.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_native_01.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_native_02.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_native_03.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/efficiency/throughput_native_04.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/geometry_probe.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/geometry_probe.sbatch` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/historical_fd4/launch_full_census.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/launch_full_census.sh` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/launch_full_census_6261_historical.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/filtering_assets/segmentation-policy.js` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/filtering_assets/service.mjs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/geometry_observations.py` | 84 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline_adapters.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline_census.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline_parallel.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline_runtime.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/line_pipeline_sources.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/source_capture/greekocr/harvest/row_inclusion.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_census/tests/test_census04.py` | 21 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/gate_rereport/analyze.py` | 248 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/gate_rereport/augment.py` | 56 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/gate_rereport/report.py` | 235 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/gate_rereport/review.py` | 70 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/baseline/tests/test_seg_gate.py` | 28 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/prepare.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/replay.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/update_metadata.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s1/validate_report.py` | 193 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/baseline/tests/test_seg_deskew.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/baseline/tests/test_seg_gate.py` | 28 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/diagnostics.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/replay.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s2/validate_report.py` | 173 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/baseline/greekocr/glyphs/components.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/baseline/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/baseline/scripts/harvest/build_filter_versions.py` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/prepare_versions.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/replay.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s3/validate_report.py` | 153 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/baseline/greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/baseline/greekocr/harvest/filtering_assets/segmentation-policy.js` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/baseline/greekocr/harvest/filtering_assets/service.mjs` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/baseline/greekocr/harvest/line_pipeline_native.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/extra_numeric.py` | 268 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/prepare_versions.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/replay.py` | 34 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s4/validate_report.py` | 411 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s5/band_sweep.py` | 33 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/s5/build_population.py` | 28 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/sheet/build.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/sheet/vendor/owner_sheet.js` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/sheet/vendor/owner_sheet.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/seg_steps/sheet/verify.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave/tools/build_grave.py` | 103 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave/tools/report_g2.py` | 43 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave/tools/score_grave.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave/tools/test_grave.py` | 116 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p1c1/zoom/add.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/build_full.py` | 98 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/common_full.py` | 96 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/confirm_full.py` | 31 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/flag_full.py` | 46 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/test_full.py` | 45 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/test_g4.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/grave_full/tools/test_g5.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/launchers/limit_probe.sh` | 26 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/launchers/run_bed.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/launchers/run_full.sh` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/launchers/run_grave.sh` | 44 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/launchers/run_read.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/launchers/run_sol_build.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/b2_common.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/b3_reports.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/build_packs.py` | 103 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/build_tiebreak.py` | 65 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/common.py` | 64 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/finalize_receipt.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/geometry.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/ledger.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/map_answers.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/owner39_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/owner39_validate.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/replay_literal.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/resolve.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/run_b3.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/scan_packs.py` | 38 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/scan_rollout.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/scan_rollout_v4.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/score_all.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/summary_b4.py` | 70 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/test_b1.py` | 422 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/test_scan_rollout_canonical.py` | 323 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/test_scan_rollout_v4.py` | 317 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/tools/test_scan_rollout_v45.py` | 349 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/validation/run_tests_b2.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/validation/run_tests_b3.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/validation/run_tests_b4.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/validation/test_b2.py` | 411 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/validation/test_b3.py` | 232 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/sol_reading/validation/test_b4.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/wikisource_r0/commit_guard.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/wikisource_r0/harvest.py` | 131 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/wikisource_r0/report.py` | 167 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/wikisource_r0/review_crops.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/harvest/wikisource_r0/validate.py` | 101 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/review_deck/deck_data.js` | 590 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/aggregate.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/aggregate_login_attempt.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/build_report.py` | 81 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/build_stop_report.py` | 98 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/l1r_recompose_source_readback.py` | 17 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/probe.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1H_evidence/release_gate_source_readback.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/build_report.py` | 439 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/fetch_selected.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/make_panels.py` | 46 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/ownership/analyse.py` | 95 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels.py` | 41 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/ownership/validate.py` | 122 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/ownership/write_section.py` | 192 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/run_pair.py` | 51 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/L1M_evidence/validate_evidence.py` | 118 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R0_evidence/ia/viewer_check.js` | 166 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2/evidence/job1/rescore_r2s.py` | 28 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2/evidence/r2a/VERIFY_CMD.sh` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2/receipts/reference_code/l1a2_cards.py` | 361 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2/receipts/reference_code/s8_prepare.py` | 193 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/adj_prep.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/agreement_mode.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/agreement_zl.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/ans.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/build_audit_page.py` | 30 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/build_audit_template.py` | 36 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/build_r1a_errors.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/build_subst_page.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/contra.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/l1f_diag.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/l1f_extract17.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/mk_ib1_r2.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/mk_ib2_r2.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/mkcomp_b1r2.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/notes6.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/r2.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/r2_090.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/r2_270.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/snap6/build_owner.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/subst_sample.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/tools/build_owner.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/tools/build_owner_r1.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/R2_evidence/page_builders/write_ib2.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/masked/run_s8a7.py` | 351 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/masked/validate_s8a7.py` | 281 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/measured_case.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/case.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/ink.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/markshape.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/reading.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/release_gate.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/segmentation.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/S8_DEV/s8b/prechange/text.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/SF7_evidence/VERIFY_CMD.sh` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/TR1_evidence/probe_remote.py` | 53 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/TR2_evidence/VERIFY_CMD.sh` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/TR2_evidence/readback_dryrun.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/learning_curve.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/model_marks.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/opt1_measure.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/opt1_score.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/opt1_score_pt.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/opt2_unigram.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/memo/options_sheet.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/print_truth/build.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/print_truth/census_pt.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/labelfix/spellcheck/print_truth/reconcile.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/origins/test_docling_plugin_c1.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/owner_sheets/inputs/coordinator_build_sheets.py` | 17 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/owner_sheets/inputs/coordinator_build_sheets_v2.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/docling_tables_20261009/probe_actual_stage.py` | 45 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/docling_tables_20261009/probe_matching.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/docling_tables_20261009/research_layout.py` | 47 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/docling_tables_20261009/research_tables.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/docling_tables_20261009/summarize_experiments.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/docling_tables_20261009/summarize_layout.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/derive_candidates.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/research_docling.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/research_local.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/research_orientation.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/research_rapid.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/research_real_local.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/summarize.py` | 73 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/verify_artifacts.py` | 43 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/research/orientation_20261009/write_report.py` | 79 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/review/reference_scratch/build_cells_sheet.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/review/reference_scratch/build_deskew_flips.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/review/reference_scratch/build_gate_sheet.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/review/reference_scratch/build_segeval_sheet.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/review/reference_scratch/segeval_sheet.js` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/review/reference_scratch/sheet_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1_evidence/native_spotcheck.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1_evidence/review_probes.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_evidence/agreement_probe.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_evidence/geometry_probes.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_evidence/new_probes.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_evidence/review_probes_original.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/agreement_probe.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/audit_saved.py` | 61 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/__main__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/admission.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/codec_coverage.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/common.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e1_common.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e1_eval.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e1_readout.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_bakeoff.py` | 33 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_cllg_contract.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_models.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_native.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_parity.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_reader_parity.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_teachers.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/e2_warmstart.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/extract_lines.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/line_categories.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_adjudicate.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_common.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_fetch.py` | 278 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_import_datasets.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_models.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_partition.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o4b_textlayer_lines.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/bench/o5_runtime.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/pipeline/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/pipeline/page_ocr_detector.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/pipeline/recognize.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/pods/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/pods/pi_pod.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/rec/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/rec/openocr_vendored/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/rec/openocr_vendored/common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/rec/openocr_vendored/rctc_decoder.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/rec/openocr_vendored/svtrv2_lnconv_two33.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/rec/svtrv2_model.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_audit.py` | 133 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_audit_anemi.py` | 154 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_common.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_discover_anemi.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_discover_archive.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_discover_other.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_discover_parliament.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_finalize.py` | 139 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_probe_media.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_probe_print.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/o4c_record_fixtures.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/parliament_pdf_cache.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/scripts/fetch/r2_cllg_worker.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/seed/node_scripts/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/seed/node_scripts/build_parity_crops.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/seed/node_scripts/fetch_parliament_s2.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_audit.py` | 133 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_audit_anemi.py` | 154 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_common.py` | 94 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_anemi.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_archive.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_other.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_parliament.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_finalize.py` | 139 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_media.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_print.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/source_clis/scripts/fetch/o4c_record_fixtures.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/cer.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/ckpt_io.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/ctc_health.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/data.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/detector_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/eval_cer.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/heads.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/mix.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/_vendor/train/train.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/_records.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/font.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/line_features.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/pipeline.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/sources.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/annotate/strata.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/cli.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/docling_plugin.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/model.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/options.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/orientation.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/recognizer/__init__.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/recognizer/ckpt_io.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/recognizer/codec.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/recognizer/inference.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/recognizer/model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/docling_plugin/recognizer/strips.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/node_envs.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/deploy/pods.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/baseline.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/boundary_evidence.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/columns.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/components.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/evaluate.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/ink.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/letters.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/line_structure.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/lines_api.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/orientation.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/orientation_guides.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/orientation_regions.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/oriented_page.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/page_font.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/page_lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/page_text_lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/pixel_segments.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/readability.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/recut.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/report.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/statistics.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/synthetic.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/glyphs/table_lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/admission.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/cli.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/collection.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/core.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/cyrillic.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/mixed.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/montage.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/montage_controls.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/openarchives.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/page_reads.py` | 2 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/parliament.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/parliament_geometry.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/parliament_http.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/parliament_provenance.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/pipeline.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/readers.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/regate.py` | 55 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/report.py` | 228 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/round1.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/round1_reads.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/round1_rescue.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/harvest/wikisource.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/build_lexicon.py` | 17 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/candidates.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/case.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/constraints.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/ctc_align.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/deck.py` | 24 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/deck_serve.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/ingest_decisions.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/ink.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/lexicon.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/linemetric.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/markshape.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/markshape_train.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/owner_slots.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/pull_firefox.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/reach.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/reading.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/rules.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/sample.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/segmentation.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/sheet.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/spellcheck_validate.py` | 53 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/spellink.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/tei_extract.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/text.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/textstage.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/toolkit_geometry.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/labelfix/validate.py` | 57 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/ops/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/ops/rate_limit.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/ops/receipts.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/ops/secrets.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/ops/watch.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/api.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/boundaries.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/cli.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/delivery.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/font.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/layout.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/lines.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/options.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/outputs.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/pixels.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/provenance.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/records.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/render.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/statistics.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/structure.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/tables.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/pages/torch_prototypes.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/cllg.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/kalchas.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/ours.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/paddle_r01.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/services/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/services/docai_driver.py` | 62 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/services/docai_manifest.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/services/google_docai.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/services/google_vision.py` | 16 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/readers/services/transkribus.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/adjudicate.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/extract.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/geometry.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/geometry_evaluate.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/geometry_measure.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/importers.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/partition.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/sources/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/sources/_runner.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/sources/discovery.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/sources/parliament.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/sources/web_render.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/real/sources/web_sources.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/score/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/synth/__init__.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/types.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/verify/__init__.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/verify/calibration.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/verify/cli.py` | 49 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/verify/images.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/verify/judges.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/verify/text.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/greekocr/warmstart/__init__.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/run_tests.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/capture_web_fixture.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/generate_api_docs.py` | 84 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/annotate_tables_round4.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/audit_orientation_guides.py` | 54 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/audit_orientation_round4.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/audit_tables_round4.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/check_tables_part2.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/evaluate_orientation_guides.py` | 54 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/evaluate_orientation_round4.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/evaluate_tables_round4.py` | 54 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/generate_orientation_guides.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/integrate_docling_tables_round4.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/integrate_orientation_round4.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/page_before_after.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/page_segments_report.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/render_orientation_guides.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/render_orientation_round4.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/report_orientation_guides.py` | 86 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/report_orientation_round4.py` | 120 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/report_tables_round4.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/review_line_boundaries.py` | 40 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/review_line_structure.py` | 80 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/review_page_lines_round3.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/review_page_lines_round4_nontable.py` | 76 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/review_statistics.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/score_tables_round4.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/summarize_page_line_review.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/tessellate_three_lines.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/archive/time_orientation_guides.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/audit_page_line_curl.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/audit_page_line_outputs.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_column_geometry_page.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_final_page_data.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_page_review_data.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_recut_page.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_review_data.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_review_page.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/build_statistics.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/calib/calib_analyse.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/calib/calib_measure.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/calib/calib_strips.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/column_line_geometry.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/compare_segments_page.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/detector_review_data.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/draw_page_lines.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/book_pages.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/broken_eval.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/capitals_eval.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/common.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/diverse_pages.py` | 18 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/double_eval.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/eval_glyphs.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/fixture_double.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/mark_stats.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/neighbour_eval.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/recut_summary.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/recut_synth_pages.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/eval/skew_eval.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/recut_real.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/render_page_line_segments.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/segment_lines_review_data.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/glyphs/segment_page_lines.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/_anemi_round1_fetcher.py` | 75 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/admit_round1.py` | 428 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/apply_clean.py` | 31 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/build_round1_reads.py` | 506 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/build_round1_reads_rest.py` | 512 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/collection.py` | 533 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/compact_parliament_raw.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/compile_page_reads.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/cyrillic.py` | 103 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/cyrillic_outputs.py` | 600 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/google_failed_lines.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/mixed.py` | 211 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/mixed_outputs.py` | 563 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/montage_controls.py` | 108 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/montage_flush.py` | 215 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/montage_pilot.py` | 172 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/openarchives.py` | 95 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/openarchives_outputs.py` | 601 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/openarchives_preflight.py` | 488 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/page_reads.py` | 520 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/parliament.py` | 151 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/parliament_outputs.py` | 630 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/parliament_retention.py` | 19 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/round1.py` | 189 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/round1_reads.py` | 53 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/round1_reads_rest.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/round1_rescue.py` | 255 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/round2.py` | 183 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/round2_outputs.py` | 611 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_google_failed_lines.py` | 114 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_montage.py` | 158 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_montage_controls.py` | 198 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_montage_flush.py` | 456 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_page_reads.py` | 512 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_round1.py` | 473 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_round1_admission.py` | 417 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_round1_reads.py` | 160 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_round1_reads_rest.py` | 159 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_round1_rescue.py` | 201 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_three_engines.py` | 154 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/validate_vision_comparison.py` | 167 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/vouli.py` | 83 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/vouli_outputs.py` | 610 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/wikisource.py` | 109 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/harvest/wikisource_outputs.py` | 564 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/agreement_mode.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/box_regression.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/c1_common.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/c1_inventory.py` | 303 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/c1_run.py` | 56 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/c1_select.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_common.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_deploy_check.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_extract.py` | 12 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_model.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_owner.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_pixels.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_prepare.py` | 83 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_run.py` | 42 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_score.py` | 52 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/clariden/r1_train.py` | 20 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/cn1_measure.py` | 78 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/cn1_offline.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/cn1_report.py` | 92 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/k1_validate.py` | 67 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/m2_review.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/m2_run.py` | 33 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/m2_score.py` | 171 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/m2_verify.py` | 165 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/owner_implicit_adjudication_prep.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/owner_implicit_changes.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/owner_pages_build.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/owner_pages_build_combined.py` | 4 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/owner_reading.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/r1_error_types.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s2_crops.py` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s2_report.py` | 83 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s2_validate.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s3_pin_slots.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s3_report.py` | 82 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s3_validate.py` | 54 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s4_report.py` | 90 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s4_train.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s4_validate.py` | 51 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s5_case_train.py` | 22 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s5_notes.py` | 25 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s5_report.py` | 93 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s5_validate.py` | 50 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s6_notes.py` | 67 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s6_report.py` | 155 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s6_validate.py` | 81 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_box_regression.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_launch_baseline.py` | 44 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_m2_replay.py` | 23 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_m2_scope.py` | 27 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_owner.py` | 3 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_report.py` | 99 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_validate.py` | 97 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/s7_verify.py` | 87 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/sf1_owner_rescore.py` | 66 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/sf1_rescore.py` | 63 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/labelfix/sheet_build.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/benchmark_q4.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/benchmark_q5.py` | 48 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/check_q3_books.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/check_q3_equality.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/check_q3b_books.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/check_q3b_equality.py` | 60 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/check_q5_default.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/check_stage_equivalence.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/write_q3_receipt.py` | 79 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/pages/write_q3b_receipt.py` | 90 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/run_verify_samples.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/train_line_font.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/scripts/vendor_sources.py` | 9 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/before_sf2/tests/labelfix/test_sf2.py` | 35 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/geometry_probes.py` | 7 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/new_probes.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/new_probes_adapted.py` | 15 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/review_probes_original.py` | 58 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/run_sf3_before.py` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/test_c3_scope.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v2_evidence/readback.py` | 99 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v2_evidence/reviewer_probes.py` | 11 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/readback.py` | 92 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/test_sf6_reviewer.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v4_evidence/readback.py` | 131 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v4_evidence/test_writer_review.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v_evidence/scoped_replay.py` | 28 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v_evidence/test_c3_scope.py` | 6 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/bind1_unreviewed/sf7_bind.sh` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/bind1_unreviewed/test_sf7_bind.py` | 13 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/merge_20261017.sh` | 43 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/run_review.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/run_review_thread.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/run_wt_medium_git.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/run_wt_medium_gitfull.sh` | 1 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/sync_20261017.sh` | 14 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/test_merge_20261017.py` | 10 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/test_sync_20261017.py` | 5 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/test_wt_remove_20261017.py` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/harness/wt_remove_20261017.sh` | 8 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `docs/records/reviews/q5-gpu-evidence/collect-failures.py` | 46 | Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git. |
| `greekocr/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/__main__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/admission.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/codec_coverage.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/common.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e1_common.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e1_eval.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e1_readout.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_bakeoff.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_cllg_contract.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_models.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_native.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_parity.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_reader_parity.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_teachers.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/e2_warmstart.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/extract_lines.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/line_categories.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_adjudicate.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_common.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_fetch.py` | 278 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_import_datasets.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_models.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_partition.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o4b_textlayer_lines.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/bench/o5_runtime.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/factory/src/audit.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/build.rs` | 4 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/codec.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/composer.rs` | 5 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/corpus.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/custody.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/distort.rs` | 14 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/import_real.rs` | 7 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/main.rs` | 9 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/measure.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/recipe.rs` | 5 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/render.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/select.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/factory/src/shard.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `greekocr/_vendor/ops/watch_proc.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/ops/watch_slurm.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/pipeline/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/pipeline/page_ocr_detector.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/pipeline/recognize.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/pods/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/pods/pi_pod.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/rec/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/rec/openocr_vendored/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/rec/openocr_vendored/common.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/rec/openocr_vendored/rctc_decoder.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/rec/openocr_vendored/svtrv2_lnconv_two33.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/rec/svtrv2_model.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4b_archive.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/scripts/fetch/o4b_datasets.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/scripts/fetch/o4c_audit.py` | 133 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_audit_anemi.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_common.py` | 94 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_discover_anemi.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_discover_archive.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_discover_other.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_discover_parliament.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_finalize.py` | 139 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_probe_media.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_probe_print.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/o4c_record_fixtures.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/parliament_pdf_cache.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/scripts/fetch/r2_cllg_env.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/scripts/fetch/r2_cllg_worker.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/seed/node_scripts/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/seed/node_scripts/build_parity_crops.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/seed/node_scripts/fetch_parliament_s2.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/seed/node_scripts/node_cllg_bakeoff.sh` | 8 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/seed/node_scripts/node_vouli2.sh` | 8 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `greekocr/_vendor/source_clis/scripts/fetch/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_audit.py` | 133 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_audit_anemi.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_common.py` | 94 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_anemi.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_archive.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_other.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_parliament.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_finalize.py` | 139 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_media.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_print.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/source_clis/scripts/fetch/o4c_record_fixtures.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/cer.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/ckpt_io.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/ctc_health.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/data.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/detector_common.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/eval_cer.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/heads.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/mix.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/_vendor/train/train.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/_files.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/artifact_custody.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/batch_check.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/controls_review_sheets.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/deal_batches.py` | 54 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/deck.js` | 1 | Resolve moved inputs through GREEK_OCR_DATA_ROOT or a receipt-backed staging resolver; emit generated sheets/assets under that root. |
| `greekocr/adjudicate/deck.py` | 82 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/edit_evidence_crosstab.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/mark_profile.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/owner_notes_export.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/owner_sheet.js` | 5 | Resolve moved inputs through GREEK_OCR_DATA_ROOT or a receipt-backed staging resolver; emit generated sheets/assets under that root. |
| `greekocr/adjudicate/owner_sheet.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/page_specs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/protocol.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/release_census.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/score.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/adjudicate/truth_overlay.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/_records.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/font.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/line_features.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/pipeline.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/sources.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/annotate/strata.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/cli.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/docling_plugin.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/model.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/options.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/orientation.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/recognizer/__init__.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/recognizer/ckpt_io.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/recognizer/codec.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/recognizer/inference.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/recognizer/model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/docling_plugin/recognizer/strips.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/node_envs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/deploy/pods.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/baseline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/boundary_evidence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/columns.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/components.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/evaluate.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/foreign_ink.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/ink.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/letters.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/line_structure.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/lines_api.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/orientation.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/orientation_guides.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/orientation_regions.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/oriented_page.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/page_font.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/page_lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/page_text_lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/pixel_segments.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/readability.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/recut.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/report.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/statistics.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/synthetic.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/table_lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/glyphs/vertical_recut.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/admission.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/application_identity.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/cli.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/collection.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/core.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/cyrillic.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/filtering_assets/crop-tools.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/filtering_assets/segmentation-policy.js` | 5 | Resolve moved inputs through GREEK_OCR_DATA_ROOT or a receipt-backed staging resolver; emit generated sheets/assets under that root. |
| `greekocr/harvest/filtering_assets/service.mjs` | 1 | Resolve moved inputs through GREEK_OCR_DATA_ROOT or a receipt-backed staging resolver; emit generated sheets/assets under that root. |
| `greekocr/harvest/geometry_observations.py` | 84 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline_adapters.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline_census.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline_native.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline_parallel.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline_runtime.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/line_pipeline_sources.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/lookalikes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/mixed.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/montage.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/montage_controls.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/neighbour_words.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/numeric_cells.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/openarchives.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/orientation_screen.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/page_reads.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/parliament.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/parliament_geometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/parliament_http.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/parliament_provenance.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/pipeline.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/qualified_admission.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/readers.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/regate.py` | 55 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/report.py` | 228 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/round1.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/round1_reads.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/round1_rescue.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/row_inclusion.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/seg_qualification.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/separator_inventory.py` | 260 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/serbian.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/text_primitives.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/harvest/wikisource.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/build_lexicon.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/candidates.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/case.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/constraints.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/ctc_align.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/deck.py` | 24 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/deck_serve.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/ingest_decisions.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/ink.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/lexicon.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/linemetric.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/lqb.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/markshape.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/markshape_train.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/owner_slots.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/pull_firefox.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/reach.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/reading.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/release_gate.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/rules.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/sample.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/segmentation.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/sheet.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/spellcheck_validate.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/spellink.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/tei_extract.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/text.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/textstage.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/toolkit_geometry.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/labelfix/validate.py` | 57 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/combine_v2.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/dash.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/ink_rule.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/line_complete.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/locks.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/owner_v2.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/prune.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/slots_geom.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/numerics/tokens.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/ops/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/ops/rate_limit.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/ops/receipts.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/ops/secrets.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/ops/watch.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/api.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/boundaries.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/cli.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/delivery.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/font.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/layout.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/options.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/outputs.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/pixels.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/provenance.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/records.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/render.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/statistics.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/structure.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/tables.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/pages/torch_prototypes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/cllg.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/kalchas.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/ours.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/paddle_r01.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/services/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/services/docai_driver.py` | 62 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/services/docai_manifest.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/services/google_docai.py` | 80 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/services/google_vision.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/readers/services/transkribus.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/adjudicate.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/extract.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/geometry.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/geometry_evaluate.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/geometry_measure.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/importers.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/partition.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/sources/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/sources/_runner.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/sources/discovery.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/sources/parliament.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/sources/web_render.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/real/sources/web_sources.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/recogniser/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/recogniser/alignment.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/recogniser/api.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/recogniser/cache.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/recogniser/evidence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/recogniser/guard.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/score/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/synth/__init__.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/types.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/verify/__init__.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/verify/calibration.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/verify/cli.py` | 49 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/verify/images.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/verify/judges.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/verify/text.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `greekocr/warmstart/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/__main__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/admission.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/codec_coverage.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/common.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e1_common.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e1_eval.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e1_readout.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_bakeoff.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_cllg_contract.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_models.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_native.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_parity.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_reader_parity.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_teachers.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/e2_warmstart.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/extract_lines.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/line_categories.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_adjudicate.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_common.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_fetch.py` | 278 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_import_datasets.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_models.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_partition.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o4b_textlayer_lines.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/bench/o5_runtime.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/pipeline/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/pipeline/page_ocr_detector.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/pipeline/recognize.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/pods/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/pods/pi_pod.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/rec/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/rec/openocr_vendored/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/rec/openocr_vendored/common.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/rec/openocr_vendored/rctc_decoder.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/rec/openocr_vendored/svtrv2_lnconv_two33.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/rec/svtrv2_model.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_audit.py` | 133 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_audit_anemi.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_common.py` | 94 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_discover_anemi.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_discover_archive.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_discover_other.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_discover_parliament.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_finalize.py` | 139 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_probe_media.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_probe_print.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/o4c_record_fixtures.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/parliament_pdf_cache.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/scripts/fetch/r2_cllg_worker.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/seed/node_scripts/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/seed/node_scripts/build_parity_crops.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/seed/node_scripts/fetch_parliament_s2.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_audit.py` | 133 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_audit_anemi.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_common.py` | 94 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_anemi.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_archive.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_other.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_parliament.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_discover_wikimedia.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_finalize.py` | 139 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_media.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_probe_print.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/source_clis/scripts/fetch/o4c_record_fixtures.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/cer.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/ckpt_io.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/ctc_health.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/data.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/detector_common.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/eval_cer.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/heads.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/mix.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/_vendor/train/train.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/_records.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/font.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/line_features.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/pipeline.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/sources.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/annotate/strata.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/cli.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/docling_plugin.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/model.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/options.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/orientation.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/recognizer/__init__.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/recognizer/ckpt_io.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/recognizer/codec.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/recognizer/inference.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/recognizer/model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/docling_plugin/recognizer/strips.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/node_envs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/deploy/pods.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/baseline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/boundary_evidence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/columns.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/components.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/evaluate.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/ink.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/letters.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/line_structure.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/lines_api.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/orientation.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/orientation_guides.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/orientation_regions.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/oriented_page.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/page_font.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/page_lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/page_text_lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/pixel_segments.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/readability.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/recut.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/report.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/statistics.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/synthetic.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/glyphs/table_lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/admission.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/cli.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/collection.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/core.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/cyrillic.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/mixed.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/montage.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/montage_controls.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/openarchives.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/page_reads.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/parliament.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/parliament_geometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/parliament_http.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/parliament_provenance.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/pipeline.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/readers.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/regate.py` | 55 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/report.py` | 228 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/round1.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/round1_reads.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/round1_rescue.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/harvest/wikisource.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/build_lexicon.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/candidates.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/case.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/constraints.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/ctc_align.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/deck.py` | 24 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/deck_serve.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/ingest_decisions.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/ink.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/lexicon.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/linemetric.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/markshape.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/markshape_train.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/owner_slots.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/pull_firefox.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/reach.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/reading.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/rules.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/sample.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/segmentation.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/sheet.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/spellcheck_validate.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/spellink.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/tei_extract.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/text.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/textstage.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/labelfix/validate.py` | 57 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/ops/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/ops/rate_limit.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/ops/receipts.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/ops/secrets.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/ops/watch.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/api.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/boundaries.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/cli.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/delivery.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/font.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/layout.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/lines.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/options.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/outputs.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/pixels.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/provenance.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/records.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/render.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/statistics.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/structure.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/tables.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/pages/torch_prototypes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/cllg.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/kalchas.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/ours.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/paddle_r01.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/services/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/services/docai_driver.py` | 62 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/services/docai_manifest.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/services/google_docai.py` | 80 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/services/google_vision.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/readers/services/transkribus.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/adjudicate.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/extract.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/geometry.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/geometry_evaluate.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/geometry_measure.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/importers.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/partition.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/sources/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/sources/_runner.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/sources/discovery.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/sources/parliament.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/sources/web_render.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/real/sources/web_sources.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/score/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/synth/__init__.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/types.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/verify/__init__.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/verify/calibration.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/verify/cli.py` | 49 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/verify/images.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/verify/judges.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/verify/text.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/greekocr/warmstart/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/c1_common.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/c1_inventory.py` | 303 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/c1_run.py` | 56 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/c1_select.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_common.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_detect.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_infer.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_inventory.py` | 271 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_prepare.py` | 44 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_run.py` | 29 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_runtime.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/l1_verify.py` | 21 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_common.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_deploy_check.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_extract.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_owner.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_pixels.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_prepare.py` | 83 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_run.py` | 42 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_score.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/clariden/r1_train.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/m2_run.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `legacy_l1/scripts/labelfix/owner_reading.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2/rescan.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2b/make_commit_bundle.py` | 30 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2b/probe_baseline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2b/rescan.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2c/make_commit_bundle.py` | 31 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2c/probe_baseline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2c/rescan.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2e/rescan.py` | 25 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2e/verify.py` | 30 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2f/rescan.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `out/scan2f/verify.py` | 31 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/classical_residual/run.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/__main__.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/acceptance.py` | 76 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/compare.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/crops.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/profile_ink.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_curl_experiment.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_curl_trace.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_field_domain_review.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_finite_boundary_review.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_font_guides.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_frame_attempt.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_frame_parts.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_geometry_review.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_geometry_trace.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_i2_features.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_i3_body.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_i4_noise.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_cohort.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_controls.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_masks.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_panels.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_qualify.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_timing.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_timing_repeat.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_verify.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_i2_witnesses.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_verify.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink02_witnesses.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_ablation.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_acceptance.py` | 31 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_audit.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_i2_acceptance.py` | 34 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_population.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_replay.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_ink_support.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_measurements.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_native_reference.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_regression.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_residual_window_replay.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_rust02.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_rust02_i2.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_rust02_i2_analysis.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_rust02_i2_fixtures.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_rust02_i2_verify.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_rust02_mutations.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_speed_acceptance.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_speed_gallery.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_speed_report.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/r8_speed_work.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/review_r6.py` | 73 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/study.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/evidence/validate.py` | 71 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/artifacts.py` | 376 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/artifacts_round4.py` | 121 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/benchmark.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/benchmark_round4.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/body_paths.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/contact_audit.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/cooperation.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/correction.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/fragments.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/leaf_paths.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/leaves.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/reference.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/review_round4.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_artifacts.py` | 120 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_benchmark.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_columns.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_data.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_endpoints.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_fast_audit.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_new_model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_routes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_shape_correct.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round5_shapes.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round6_rows.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round6_rows_export.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/round6_rows_review.py` | 384 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/rule_ownership.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/rules.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/scout_audit.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/skew_contacts.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/skew_rotation.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/study.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_accent_admission.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_bend.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_context.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_curl_consumer.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_curl_separator.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_final_bands.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_finite_domains.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_fragments.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_geometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_native_font_contract.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_native_seams.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_page_field.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_round5.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_rows.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_scout.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_smooth_bands.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_geometry/test_whole_children.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/cooperate.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/density.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/diagnostic_timing.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/edge_study.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/final.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/image_structure_study.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/motif_gate_study.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/observability_controls.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/observability_study.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/perturb.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/pipeline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/publish.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/publish_round4.py` | 119 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/recurrence_study.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/reference.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/repeat_field_study.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round4_review.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round5_export.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round5_marks.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round5_motifs.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round5_study.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round6_export.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round6_faintness.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/round6_review.py` | 68 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/stroke_review.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/study.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/test_features.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/test_round4.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/test_round5.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/test_round6.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_ink/test_round7.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/audit4.py` | 44 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/book.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/edges4.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/extended4.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/extents4.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/identity4.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/identity_routes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/lattice.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/measure.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/measure4.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/pipeline.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/publish.py` | 117 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/publish4.py` | 74 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/recover4.py` | 44 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/reference.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/review.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/round5.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/round5_validate.py` | 121 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/rows4.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/study.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/table_dots7.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/tables.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/test_request_separators.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/test_residual_completion.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/test_round5.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/test_type.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/features_type/validate4.py` | 107 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/font_guides/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/foreground_profiles/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/image_motifs/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/ink_condition/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/inspect_outputs.py` | 78 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/layout_barriers/fast.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/layout_barriers/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/local_ribbons/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/map_graph/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/native_contours/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/publish_review.py` | 132 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/residual_ledger/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/round2.py` | 75 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/run.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/rust_field/__init__.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/rust_field/build.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `prototypes/fast_lines/rust_field/fixture_data.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/rust_field/src/lib.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `prototypes/fast_lines/rust_field/test_field.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/selective_rerun/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/context.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/contracts.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/detector.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_bands.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_bend.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_bend_edits.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_bend_gap.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_bend_rules.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_columns.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_contacts.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_context.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_edge_map.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_envelopes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_feature_correct.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_feature_paths.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_feature_rules.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_feature_separation.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_field_detector.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_field_selection.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_filter.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_final_support.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_fragment_correct.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_fragments.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_joinbarriers.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_memo.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_page_field.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_pipeline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_regions.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_rows.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/geometry_scout.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/image_evidence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_discrete_motifs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_edges.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_faint_scout.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_faintness.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_footprints.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_frame_field.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_image_structure.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_images.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_motif_gate.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_motifs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_normal.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_observability.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_ownership.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_photometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_recurrence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_repeat_field.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_seal.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_solid.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_stamp_field.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_stamps.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_strokes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/ink_type_identity.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/local_scale.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/manifest.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/observations.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/paddle_db.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/perturbations.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/references.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/review.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/scheduler.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/stack_ownership.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_i4_contracts.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_ink_atlas_contract.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_observations.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_r8_ink.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_r8_ink_i2.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_shared_witnesses.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/test_speed_observations.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/timing.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_barriers.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_book.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_completion.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_contact_band.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_context.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_dot_runs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_extended.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_grid_edges.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_identity.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_initials.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_lattice.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_profiles.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_recovery.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_residual.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_residual_recovery.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_rows.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_table_extent.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/shared/type_tables.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/sheet_lattice/run.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/__main__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/geometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/pipeline.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/test_r5.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/test_r6.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/test_r7.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/stack/test_stack.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/tests/test_prototypes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/tests/test_round2.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/tests/test_shared.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/validate_round2.py` | 74 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/workflow.py` | 66 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/fast_lines/write_report.py` | 132 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/harvest/google_failed_lines.py` | 449 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/harvest/transkribus_failed_lines.py` | 431 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `prototypes/harvest/vision_comparison.py` | 163 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/capture_web_fixture.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/fast_lines/audit_evidence.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/fast_lines/probe_colour.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/fast_lines/probe_mirror_histograms.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/fast_lines/review_atlas.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/generate_api_docs.py` | 86 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/annotate_tables_round4.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/audit_orientation_guides.py` | 54 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/audit_orientation_round4.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/audit_tables_round4.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/check_tables_part2.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/evaluate_orientation_guides.py` | 54 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/evaluate_orientation_round4.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/evaluate_tables_round4.py` | 54 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/generate_orientation_guides.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/integrate_docling_tables_round4.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/integrate_orientation_round4.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/page_before_after.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/page_segments_report.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/render_orientation_guides.py` | 50 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/render_orientation_round4.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/report_orientation_guides.py` | 86 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/report_orientation_round4.py` | 120 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/report_tables_round4.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/review_line_boundaries.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/review_line_structure.py` | 80 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/review_page_lines_round3.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/review_page_lines_round4_nontable.py` | 76 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/review_statistics.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/score_tables_round4.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/summarize_page_line_review.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/tessellate_three_lines.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/archive/time_orientation_guides.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/audit_page_line_curl.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/audit_page_line_outputs.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_column_geometry_page.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_final_page_data.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_page_review_data.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_recut_page.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_review_data.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_review_page.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/build_statistics.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/calib/calib_analyse.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/calib/calib_measure.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/calib/calib_strips.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/column_line_geometry.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/compare_segments_page.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/detector_review_data.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/draw_page_lines.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/book_pages.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/broken_eval.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/capitals_eval.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/common.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/diverse_pages.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/double_eval.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/eval_glyphs.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/extract_poly_lines.sh` | 6 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/glyphs/eval/fixture_double.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/mark_stats.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/neighbour_eval.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/recut_summary.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/recut_synth_pages.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/eval/skew_eval.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/recut_real.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/render_page_line_segments.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/run_review.sh` | 2 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/glyphs/segment_lines_review_data.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/glyphs/segment_page_lines.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/_anemi_round1_fetcher.py` | 75 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/admit_round1.py` | 428 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/apply_clean.py` | 31 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/build_filter_versions.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/build_round1_reads.py` | 506 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/build_round1_reads_rest.py` | 512 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/clariden/bootstrap.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/clariden/filter_crop_paths.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/clariden/filter_worker.sbatch` | 8 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/harvest/clariden/package.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/clariden/worker.py` | 311 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/collection.py` | 533 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/commit_census2_guarded.sh` | 82 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/harvest/commit_census3_guarded.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/compact_parliament_raw.py` | 50 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/compile_page_reads.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/cyrillic.py` | 103 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/cyrillic_outputs.py` | 600 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/filter_runtime/src/main.rs` | 1 | Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt. |
| `scripts/harvest/google_failed_lines.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/mixed.py` | 211 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/mixed_outputs.py` | 563 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/montage_controls.py` | 108 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/montage_flush.py` | 215 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/montage_pilot.py` | 172 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/openarchives.py` | 95 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/openarchives_outputs.py` | 601 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/openarchives_preflight.py` | 488 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/page_reads.py` | 520 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/parliament.py` | 151 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/parliament_outputs.py` | 630 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/parliament_retention.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/reissue_census2.py` | 32 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/reissue_census3.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/round1.py` | 189 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/round1_reads.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/round1_reads_rest.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/round1_rescue.py` | 255 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/round2.py` | 183 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/round2_outputs.py` | 611 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_google_failed_lines.py` | 114 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_montage.py` | 158 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_montage_controls.py` | 198 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_montage_flush.py` | 456 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_page_reads.py` | 512 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_round1.py` | 473 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_round1_admission.py` | 417 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_round1_reads.py` | 160 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_round1_reads_rest.py` | 159 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_round1_rescue.py` | 201 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_three_engines.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/validate_vision_comparison.py` | 167 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/verify_filter_parity.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/vouli.py` | 83 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/vouli_outputs.py` | 610 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/wikisource.py` | 109 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/harvest/wikisource_outputs.py` | 564 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/agreement_mode.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/agreement_mode_historical.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/box_regression.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/c1_common.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/c1_inventory.py` | 303 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/c1_job.sbatch` | 10 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/c1_run.py` | 56 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/c1_select.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1_common.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1_detect.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1_infer.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1c_census.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1c_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1e_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1e_measure.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1e_run.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1e_windows.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1f_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1f_mock_check.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1f_preflight.sh` | 42 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1f_run.py` | 51 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r2_census.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r2_census_job.sbatch` | 3 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1r2_changes.py` | 69 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r3_evidence.py` | 36 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r3_preflight.sh` | 84 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1r4_census.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r4_census_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1r4_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1r4_join.py` | 47 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r4_mock_check.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r4_preflight.sh` | 93 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1r_job.sbatch` | 3 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/l1r_mock_check.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r_recompose.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/l1r_recompose_ext.py` | 69 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_common.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_deploy_check.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_extract.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/r1_model.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_owner.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_pixels.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_prepare.py` | 83 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_run.py` | 42 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_score.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r1_train.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_crop_probe.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_deploy.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/r2_manifest.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_mock.py` | 273 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_native.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_population.py` | 25 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_prepare.py` | 261 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_run.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_stage_crops.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_teacher.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2_util.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2a_deploy.py` | 30 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2a_diagnose.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2a_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/r2a_mock.py` | 298 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2a_preflight.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2a_prepare.py` | 362 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/r2a_run.py` | 49 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/s8_fetch_job.sbatch` | 5 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/sf7_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/sf7_recompose.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_c1_run.py` | 56 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_convert.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_job.sbatch` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/labelfix/clariden/tr2_l1_detect.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_l1_infer.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_legacy_detect.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_recompose.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/clariden/tr2_run.py` | 325 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/cn1_measure.py` | 78 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/cn1_offline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/cn1_report.py` | 92 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/k1_validate.py` | 67 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/l1a2_cards.py` | 361 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/l1a2_fetch.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/m2_review.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/m2_run.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/m2_score.py` | 171 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/m2_verify.py` | 165 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/owner_implicit_adjudication_prep.py` | 35 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/owner_implicit_changes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/owner_pages_build.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/owner_pages_build_combined.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/owner_reading.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_finish.py` | 479 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_freeze_ia.py` | 239 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_freeze_ib.py` | 559 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_prepare.py` | 515 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_score.py` | 435 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_score_report.py` | 413 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_score_validate.py` | 102 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r0_wholeline_score.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r1_error_types.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_cards_prepare.py` | 167 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_cards_resolve.py` | 379 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_cards_validate.py` | 176 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_finalize_manifest.py` | 383 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_job1_digest.py` | 407 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_readback_verify.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2_score.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/r2a_digest.py` | 135 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/release_gate_sf7.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s2_crops.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s2_report.py` | 83 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s2_validate.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s3_pin_slots.py` | 27 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s3_report.py` | 82 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s3_validate.py` | 54 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s4_report.py` | 90 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s4_train.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s4_validate.py` | 51 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s5_case_train.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s5_notes.py` | 25 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s5_report.py` | 93 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s5_validate.py` | 50 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s6_notes.py` | 67 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s6_report.py` | 155 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s6_validate.py` | 81 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_box_regression.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_launch_baseline.py` | 44 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_m2_replay.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_m2_scope.py` | 27 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_owner.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_report.py` | 99 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_validate.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s7_verify.py` | 87 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_fetch.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_fetch_job.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_fetch_l1m.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_fetch_stage.py` | 18 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_prepare.py` | 193 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_report.py` | 212 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_score_truth.py` | 83 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_validate_audit.py` | 157 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_validate_dev.py` | 161 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_validate_truth.py` | 30 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8_verify_evidence.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8b_measure.py` | 99 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8b_regressions.py` | 119 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8b_report.py` | 164 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8b_split.py` | 35 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/s8b_validate.py` | 155 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf1_owner_rescore.py` | 66 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf1_rescore.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf2_replay.py` | 62 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf3_measure.py` | 68 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf4_measure.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf4_r1_compatibility.py` | 47 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf5_measure.py` | 179 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf5_report.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf5_verify.py` | 116 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6_measure.py` | 218 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6_report.py` | 192 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6_verify.py` | 172 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6b_measure.py` | 146 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6c_audit.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6c_measure.py` | 109 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6c_report.py` | 144 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf6c_verify.py` | 101 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf7_deploy.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf7_final_score.py` | 73 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf7_measure.py` | 300 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf7_opus_prepare.py` | 115 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sf7_package.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/labelfix/sheet_build.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/build_scoreboard.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/build_truth.py` | 378 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/build_v2.py` | 120 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/build_v2_1.py` | 156 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/build_v2_2.py` | 224 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/build_versions.py` | 32 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/finalize.py` | 81 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/finalize_v2.py` | 31 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/finalize_v2_1.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/finalize_v2_2.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/lqb/validate_scoreboard.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_apply_train.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_build_packs.py` | 69 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_calibration.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_decide.py` | 62 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_gate.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_map_answers.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_pack_closure.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_prepare.py` | 29 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_raised_sheets.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_render.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_report.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_score.py` | 139 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1_step0.py` | 49 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1cb_prepare.py` | 37 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1cb_receipt.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1cc_prepare.py` | 39 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1cc_receipt.py` | 28 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1cd_prepare.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1cd_receipt.py` | 119 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1e_prepare.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1g.py` | 191 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1r2_prepare.py` | 64 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1r2_receipt.py` | 99 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1r_fit.py` | 71 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1r_receipt.py` | 105 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1t_boxes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1t_combine.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1t_owner_sheet.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1t_packs.py` | 79 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1t_prepare.py` | 148 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1t_receipt.py` | 142 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1tb_prepare.py` | 96 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1tr.py` | 191 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1tr_f2.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1tr_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/numerics/n1ts.py` | 50 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1ts2.py` | 94 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1ts3.py` | 84 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1.py` | 200 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_closure.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_combine.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_crops.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_f2.py` | 70 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_f3.py` | 69 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/numerics/n1w1_geometry.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_locks.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_packs.py` | 79 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_r3.py` | 142 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_r3_finalize.py` | 131 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_r3_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/numerics/n1w1_render.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_sheets.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_storage.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/n1w1_tokens.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/numerics/validate_n1.py` | 75 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/benchmark_q4.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/benchmark_q5.py` | 48 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/check_q3_books.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/check_q3_equality.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/check_q3b_books.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/check_q3b_equality.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/check_q5_default.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/check_stage_equivalence.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/write_q3_receipt.py` | 79 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/pages/write_q3b_receipt.py` | 90 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/build_failure_modes_per_class.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/build_owner_sheets_v2.py` | 181 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/build_segmentation_failures.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/build_sheet1_demos.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/cu4_pins.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/cu4_reemit.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/cu4_report.py` | 162 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/owner_sheets.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/prepare_os1_specs.py` | 53 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/recover_owner_sheet_crops.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/report_os1.py` | 49 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/retag_owner_sheets_os4.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/sr1.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/sr1_finish.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/sr1_fixtures.py` | 45 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/review/sr1_receipts.py` | 25 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/run_verify_samples.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/common.py` | 64 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/ledger.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/limit_probe.sh` | 26 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/n1_launch.py` | 154 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1tr_driver.py` | 87 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_common.py` | 64 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_coverage.py` | 59 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_driver.py` | 87 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_exclusions.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_launch.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_ledger.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_limit_probe.sh` | 26 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/n1w1_r3_driver.py` | 87 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_replay_literal.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_run_read.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/n1w1_scan_packs.py` | 72 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/n1w1_scan_rollout.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/reference/build_packs.py` | 103 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/reference/map_answers.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/replay_literal.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/ru1_map_answers.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/run_bed.sh` | 101 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_n1.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_n1tr_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_n1w1_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_n1w1_r3_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_read.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_ru2t.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_ru3t_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_ru3t_r3_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/run_ru3t_r5_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/reading/scan_packs.py` | 72 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/scan_rollout.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/scan_rollout_secondary_pre_v44.py` | 101 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/reading/test_scan_rollout_v4.py` | 317 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_build_packs.py` | 373 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_census.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_decide.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_finalize.py` | 318 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru1_finalize_b.py` | 357 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_finalize_r3.py` | 115 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_lead_sheets.py` | 334 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_owner_sheet.py` | 120 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_rescan.py` | 79 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_review.py` | 70 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_second_reader.py` | 65 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_third_reader.py` | 78 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru1_version.py` | 121 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru2t.py` | 434 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru2t_apply_lead.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru2t_coverage.py` | 59 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru2t_delivery.py` | 112 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru2t_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru2t_launch.py` | 152 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru2t_receipt.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t.py` | 437 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t_delivery.py` | 103 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t_driver.py` | 62 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t_f4.py` | 45 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru3t_r3.py` | 184 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t_r3_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru3t_r5.py` | 187 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3t_r5_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru3td_bind_probe.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru3td_edits.py` | 49 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e.py` | 515 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2.py` | 41 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/common.py` | 64 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/ledger.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/limit_probe.sh` | 26 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e2_bound/replay_literal.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/ru1_census.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/ru1_map_answers.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/ru2t_coverage.py` | 59 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/run_read.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e2_bound/scan_packs.py` | 72 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_bound/scan_rollout.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e2_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e2_finalize_f1.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e2_finalize_f2.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e2_receipt.py` | 118 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/common.py` | 64 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/ledger.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/limit_probe.sh` | 26 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e_bound/replay_literal.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/ru1_census.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/ru1_map_answers.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/ru2t_coverage.py` | 59 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/run_read.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4e_bound/scan_packs.py` | 72 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_bound/scan_rollout.py` | 97 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4e_finalize.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/ru4ef1.py` | 109 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4ef2_collect.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4ef2_png.py` | 103 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4ef2_r5.py` | 80 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4ef2_receipt.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4ef3.py` | 72 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/ru4ef3_score.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/secondary/run_ru4e2_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/run_ru4e2_r3_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/run_ru4e2_r5_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/secondary/run_ru4e_all.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `scripts/train_line_font.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `scripts/vendor_sources.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `seed/node_scripts/build_parity_crops.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `seed/node_scripts/fetch_parliament_s2.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `seed/node_scripts/node_cllg_bakeoff.sh` | 8 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `seed/node_scripts/node_vouli2.sh` | 8 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `tests/adjudicate/test_deck_protocol.py` | 41 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_os2_owner_sheets.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_os4_owner_retags.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_os5_owner_sheets.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_owner_runtime.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_reemission.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_score.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/adjudicate/test_sr1.py` | 58 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/conftest.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/fixtures/harvest_fix1/fetch_selection.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/fixtures/o4c/anemi_download_control.js` | 1 | Resolve moved inputs through GREEK_OCR_DATA_ROOT or a receipt-backed staging resolver; emit generated sheets/assets under that root. |
| `tests/glyphs/test_boundary_evidence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_curl.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_glyphs.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_initial_batches.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_line_structure.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_orientation.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_orientation_guides.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_page_line_segments.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_page_lines_round3.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_page_lines_round4_nontable.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_pages_api.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_pages_equality.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_q4_kernels.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_q5_prototypes.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_statistics.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/glyphs/test_vertical_recut.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/fixtures/r2/r1_train_3678928.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/fixtures/r2/r1_train_job_3678928.py` | 20 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_alignment.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_capture.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_constraints.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_ingest.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_k1.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1c.py` | 64 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1e.py` | 43 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1f.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1r.py` | 34 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1r2.py` | 54 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1r3.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_l1r4.py` | 30 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_lexicon.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_markshape.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_policy_frozen_after_merge.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_r1.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_r2.py` | 319 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_r2_population.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_r2_readback_digest.py` | 39 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_r2a_digest.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_r2a_package.py` | 47 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_rules.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s2.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s2_sheet.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s3.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s4.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s5.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s6.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s7.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_s8_fetch_job.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf1.py` | 57 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf2.py` | 35 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf3.py` | 35 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf4.py` | 25 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf4_review.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf5.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf6.py` | 62 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf6_reviewer.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf6c.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf7.py` | 29 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_sf7_package.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/labelfix/test_spellcheck.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/recogniser/audit_pins.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/recogniser/parity.py` | 7 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/recogniser/test_api.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_adm5b_schema.py` | 16 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_adm5c_variants.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_apply_clean.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_census3_secondary_scripts.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_cllg_confidence.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_collection.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_collection_outputs.py` | 344 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_compile_page_reads.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_content_gate.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_custody.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_cyrillic.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_docai.py` | 61 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_docling_contract.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_docling_orientation.py` | 3 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_docling_tables.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_geometry_evaluate.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_geometry_measure.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_google_failed_lines.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_google_vision.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_harvest.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_harvest_admission.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_harvest_fix1.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_harvest_fix2.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_harvest_round1.py` | 68 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_line_metadata.py` | 17 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_line_pipeline.py` | 339 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_lqb.py` | 312 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_lqb3.py` | 55 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_lqb4.py` | 24 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_lqb5.py` | 181 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_mixed.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_montage.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_montage_controls.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_montage_flush.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1_map_answers.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1_packs_render.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1_score.py` | 13 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1_slots_geom.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1cal2s.py` | 52 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1cb_artifacts.py` | 21 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1cc_artifacts.py` | 23 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1cd.py` | 436 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1cd_render.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1g.py` | 259 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1r.py` | 35 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1r2.py` | 139 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1r_gate_apply.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1t.py` | 131 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1tb.py` | 124 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1tr.py` | 376 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1ts.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1ts2.py` | 56 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1ts3.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1w1.py` | 409 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_n1w1_r3.py` | 277 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_neighbour_words.py` | 37 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_numeric_cells.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_numeric_locks.py` | 4 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_numeric_tokens.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_openarchives.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_openarchives_preflight.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_openarchives_run.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ops_deploy_sources.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_owner_sheet.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_p1b_alignment.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_page_reads.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_parliament.py` | 59 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_provenance_cli_api.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_r2_cards.py` | 120 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_r2_finalize_manifest.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_real_annotate_score.py` | 19 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_real_geometry.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_round1_admission_outputs.py` | 29 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_round1_reads.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_round1_reads_rest.py` | 2 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_round1_rescue.py` | 15 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_round2.py` | 40 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru12.py` | 59 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1_census.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1_decide.py` | 28 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1_map_answers.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1_review.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1_second_reader.py` | 71 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1f.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1r3.py` | 160 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1s.py` | 26 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru1s_scanner.py` | 286 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru2t.py` | 369 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru2t_apply_lead.py` | 8 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru3t.py` | 405 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru3t_r3.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru3t_r5.py` | 60 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru4e.py` | 377 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru4e2.py` | 82 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_ru4ef1.py` | 346 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_scan_rollout.py` | 353 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp1.py` | 22 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp2.py` | 93 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp3.py` | 44 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp4.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp4c.py` | 34 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp5.py` | 264 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp5pb.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp6.py` | 11 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7.py` | 264 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7a3_geometry.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7b_score.py` | 12 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7c.py` | 74 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7c2_runtime.py` | 63 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7c_score_fixtures.py` | 24 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp7d.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_cp8a.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_curve.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_deskew.py` | 25 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_gate.py` | 28 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_seg_small.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_transkribus.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_vendor_o4c.py` | 65 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_vendor_o4c_anemi.py` | 51 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_vendor_r2_cllg.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_verify.py` | 51 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_vouli.py` | 33 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_warmstart_readers.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_web_render.py` | 9 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `tests/test_wikisource.py` | 119 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/__init__.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/bootstrap.sh` | 2 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `worker/control.py` | 14 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/install_python.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `worker/launch_w1.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `worker/lock_env.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/offline_check.py` | 45 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/package_handoff.py` | 10 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/preflight.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/prepare.py` | 6 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/runtime.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/status.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `worker/sync.py` | 29 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/sync_back.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `worker/system_packages.sh` | 1 | Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running. |
| `worker/test_offline.py` | 1 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |
| `worker/wheels.py` | 5 | Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too. |

The basename scan does not detect computed filenames, directory globbing, or strings inside compressed manifests. A relocation execution gate must additionally audit directory consumers and relative HTML assets (especially tests/fixtures, crop/zoom directories, sheet img/src links, package manifests, census/pool loaders, and deploy scripts), provision their receipt-backed inputs, and run affected offline tests. This is an analysis limitation, not evidence that unlisted consumers cannot break.

## Directories becoming empty

These are current directories whose every leaf is a MOVE path; retained files, tracked symlinks and untracked files prevent an empty classification. Git does not track empty directories. These counts describe the proposed decisions with ASK paths left in place. Complete list (also machine-readable in `EMPTY_DIRECTORIES.tsv`):

- `artifacts/cq1/answers/`
- `artifacts/cq4/closure/`
- `artifacts/cq4/control_review/`
- `artifacts/cq4/cq4f_before/quarantine/`
- `artifacts/cq4/cq4f_before/truth/`
- `artifacts/cq4/cq6_package/data/`
- `artifacts/cq4/cq6c_package/data/`
- `artifacts/cq4/cq7/baseline/quarantine/`
- `artifacts/cq4/cq7/baseline/truth/`
- `artifacts/cq4/cq7/closure/`
- `artifacts/cq4/cq7/keys/`
- `artifacts/cq4/cq7/scans/`
- `artifacts/cq4/keys/`
- `artifacts/cq4/packs/solcap_topup/topup_reread_000/r1/img/`
- `artifacts/cq4/packs/solcap_topup/topup_reread_001/r1/img/`
- `artifacts/cq4/packs/solcap_topup/topup_reread_002/r1/img/`
- `artifacts/cq4/packs/solcap_topup/topup_reread_003/r1/img/`
- `artifacts/cq4/packs/solcap_topup/topup_reread_004/r1/img/`
- `artifacts/cq4/packs/solcap_wcap/wcap_reread_000/r1/img/`
- `artifacts/cq4/packs/solcap_wcap/wcap_reread_001/r1/img/`
- `artifacts/cq4/packs/solcap_wcap/wcap_reread_001/r1/zoom/`
- `artifacts/cq4/probe.1iPK/`
- `artifacts/cq4/probe.1upM/`
- `artifacts/cq4/probe.2lnn/`
- `artifacts/cq4/probe.4Mqs/`
- `artifacts/cq4/probe.6hYW/`
- `artifacts/cq4/probe.7p60/`
- `artifacts/cq4/probe.9sRN/`
- `artifacts/cq4/probe.BqUF/`
- `artifacts/cq4/probe.GjKP/`
- `artifacts/cq4/probe.LrH2/`
- `artifacts/cq4/probe.NwkX/`
- `artifacts/cq4/probe.OdMb/`
- `artifacts/cq4/probe.U00s/`
- `artifacts/cq4/probe.XIWf/`
- `artifacts/cq4/probe.XxYC/`
- `artifacts/cq4/probe.bHWO/`
- `artifacts/cq4/probe.egs6/`
- `artifacts/cq4/probe.exiz/`
- `artifacts/cq4/probe.hkde/`
- `artifacts/cq4/probe.ofkX/`
- `artifacts/cq4/probe.pGTJ/`
- `artifacts/cq4/probe.qNPK/`
- `artifacts/cq4/probe.qiwK/`
- `artifacts/cq4/probe.qxSw/`
- `artifacts/cq4/probe.veER/`
- `artifacts/cq4/probe.wBAL/`
- `artifacts/cq4/quarantine/`
- `artifacts/cq4/regression/`
- `artifacts/cq4/scans/`
- `artifacts/cq4/scans_v455/`
- `artifacts/cq4/truth/`
- `artifacts/cq4/void_attempt_cq4d/quarantine/`
- `artifacts/cq4/void_attempt_cq4d/truth/`
- `artifacts/labelfix_l1e/fixture_v4/mock/binding/`
- `artifacts/labelfix_l1e/fixture_v4/mock/historical/release/`
- `artifacts/labelfix_l1e/mock_run_v4/recomposition/release/`
- `artifacts/labelfix_r2/population/`
- `artifacts/labelfix_r2a/inputs/`
- `artifacts/n1/answers/n1e/probe.3102/`
- `artifacts/n1/answers/n1e/probe.5C1s/`
- `artifacts/n1/answers/n1e/probe.7AK3/`
- `artifacts/n1/answers/n1e/probe.7pvD/`
- `artifacts/n1/answers/n1e/probe.9Oqe/`
- `artifacts/n1/answers/n1e/probe.Aqff/`
- `artifacts/n1/answers/n1e/probe.BTX0/`
- `artifacts/n1/answers/n1e/probe.DT44/`
- `artifacts/n1/answers/n1e/probe.HJHw/`
- `artifacts/n1/answers/n1e/probe.IUKw/`
- `artifacts/n1/answers/n1e/probe.K8Zi/`
- `artifacts/n1/answers/n1e/probe.KSW1/`
- `artifacts/n1/answers/n1e/probe.KgX9/`
- `artifacts/n1/answers/n1e/probe.LnkE/`
- `artifacts/n1/answers/n1e/probe.LsG2/`
- `artifacts/n1/answers/n1e/probe.Nu4K/`
- `artifacts/n1/answers/n1e/probe.ODTB/`
- `artifacts/n1/answers/n1e/probe.OTNf/`
- `artifacts/n1/answers/n1e/probe.OaKt/`
- `artifacts/n1/answers/n1e/probe.RrDx/`
- `artifacts/n1/answers/n1e/probe.UvPn/`
- `artifacts/n1/answers/n1e/probe.Vdwu/`
- `artifacts/n1/answers/n1e/probe.W95r/`
- `artifacts/n1/answers/n1e/probe.WS1Y/`
- `artifacts/n1/answers/n1e/probe.ZVcl/`
- `artifacts/n1/answers/n1e/probe.b0xV/`
- `artifacts/n1/answers/n1e/probe.bBWy/`
- `artifacts/n1/answers/n1e/probe.diy0/`
- `artifacts/n1/answers/n1e/probe.eX9O/`
- `artifacts/n1/answers/n1e/probe.gCIB/`
- `artifacts/n1/answers/n1e/probe.hLsZ/`
- `artifacts/n1/answers/n1e/probe.kan8/`
- `artifacts/n1/answers/n1e/probe.l28i/`
- `artifacts/n1/answers/n1e/probe.mgUQ/`
- `artifacts/n1/answers/n1e/probe.oKyA/`
- `artifacts/n1/answers/n1e/probe.pN7H/`
- `artifacts/n1/answers/n1e/probe.tnHJ/`
- `artifacts/n1/answers/n1e/probe.uLKl/`
- `artifacts/n1/answers/n1e/probe.uvKE/`
- `artifacts/n1/answers/n1e/probe.vZzN/`
- `artifacts/n1/answers/n1t2/probe.0L5o/`
- `artifacts/n1/answers/n1t2/probe.4FNx/`
- `artifacts/n1/answers/n1t2/probe.7aog/`
- `artifacts/n1/answers/n1t2/probe.9dD0/`
- `artifacts/n1/answers/n1t2/probe.A1tk/`
- `artifacts/n1/answers/n1t2/probe.AZ01/`
- `artifacts/n1/answers/n1t2/probe.B4N8/`
- `artifacts/n1/answers/n1t2/probe.DXkC/`
- `artifacts/n1/answers/n1t2/probe.E6Ky/`
- `artifacts/n1/answers/n1t2/probe.FVE9/`
- `artifacts/n1/answers/n1t2/probe.HhVG/`
- `artifacts/n1/answers/n1t2/probe.IiH4/`
- `artifacts/n1/answers/n1t2/probe.JM3C/`
- `artifacts/n1/answers/n1t2/probe.MD9q/`
- `artifacts/n1/answers/n1t2/probe.MMC9/`
- `artifacts/n1/answers/n1t2/probe.PHAW/`
- `artifacts/n1/answers/n1t2/probe.Q95t/`
- `artifacts/n1/answers/n1t2/probe.QHPt/`
- `artifacts/n1/answers/n1t2/probe.SdZf/`
- `artifacts/n1/answers/n1t2/probe.T4U4/`
- `artifacts/n1/answers/n1t2/probe.WdjH/`
- `artifacts/n1/answers/n1t2/probe.Wp0d/`
- `artifacts/n1/answers/n1t2/probe.Wt9Y/`
- `artifacts/n1/answers/n1t2/probe.X2VZ/`
- `artifacts/n1/answers/n1t2/probe.XTt3/`
- `artifacts/n1/answers/n1t2/probe.Z5KS/`
- `artifacts/n1/answers/n1t2/probe.Zcu1/`
- `artifacts/n1/answers/n1t2/probe.ZdjY/`
- `artifacts/n1/answers/n1t2/probe.Zf2e/`
- `artifacts/n1/answers/n1t2/probe.ZoLL/`
- `artifacts/n1/answers/n1t2/probe.aAbN/`
- `artifacts/n1/answers/n1t2/probe.ciKk/`
- `artifacts/n1/answers/n1t2/probe.d2P9/`
- `artifacts/n1/answers/n1t2/probe.dJ1c/`
- `artifacts/n1/answers/n1t2/probe.e83b/`
- `artifacts/n1/answers/n1t2/probe.fmUn/`
- `artifacts/n1/answers/n1t2/probe.fvwL/`
- `artifacts/n1/answers/n1t2/probe.hdQ0/`
- `artifacts/n1/answers/n1t2/probe.icyb/`
- `artifacts/n1/answers/n1t2/probe.k3Gy/`
- `artifacts/n1/answers/n1t2/probe.mFK9/`
- `artifacts/n1/answers/n1t2/probe.nKyi/`
- `artifacts/n1/answers/n1t2/probe.qYXM/`
- `artifacts/n1/answers/n1t2/probe.qxMV/`
- `artifacts/n1/answers/n1t2/probe.r55i/`
- `artifacts/n1/answers/n1t2/probe.r5Eh/`
- `artifacts/n1/answers/n1t2/probe.sicq/`
- `artifacts/n1/answers/n1t2/probe.tnTI/`
- `artifacts/n1/answers/n1t2/probe.uSnJ/`
- `artifacts/n1/answers/n1t2/probe.ue4p/`
- `artifacts/n1/answers/n1t2/probe.wMYi/`
- `artifacts/n1/answers/n1t2/probe.xCtM/`
- `artifacts/n1/answers/n1t2/probe.y6nK/`
- `artifacts/n1/answers/n1t2/probe.yBFM/`
- `artifacts/n1/answers/n1t2/probe.yqBM/`
- `artifacts/n1/answers/n1t2/probe.zzT9/`
- `artifacts/n1/answers/n1t3/probe.CchV/`
- `artifacts/n1/answers/n1t3/probe.D4FR/`
- `artifacts/n1/answers/n1t3/probe.EcHT/`
- `artifacts/n1/answers/n1t3/probe.Ld5w/`
- `artifacts/n1/answers/n1t3/probe.NB6A/`
- `artifacts/n1/answers/n1t3/probe.NTYz/`
- `artifacts/n1/answers/n1t3/probe.Xxxq/`
- `artifacts/n1/answers/n1t3/probe.asDQ/`
- `artifacts/n1/answers/n1t3/probe.jxcT/`
- `artifacts/n1/answers/n1t3/probe.r2Zi/`
- `artifacts/n1/answers/n1t3/probe.snvN/`
- `artifacts/n1/answers/n1t3/probe.w5OU/`
- `artifacts/n1/answers/probe.2LLp/`
- `artifacts/n1/answers/probe.4jal/`
- `artifacts/n1/answers/probe.B52t/`
- `artifacts/n1/answers/probe.Cwnt/`
- `artifacts/n1/answers/probe.KI1j/`
- `artifacts/n1/answers/probe.Ww3h/`
- `artifacts/n1/answers/probe.YRlj/`
- `artifacts/n1/answers/probe.bat0/`
- `artifacts/n1/answers/probe.cLR5/`
- `artifacts/n1/answers/probe.eo7F/`
- `artifacts/n1/answers/probe.hocf/`
- `artifacts/n1/answers/probe.lmST/`
- `artifacts/n1/answers/probe.mkrb/`
- `artifacts/n1/answers/probe.qhOK/`
- `artifacts/n1/answers/probe.uQre/`
- `artifacts/n1/answers/probe.vfjF/`
- `artifacts/n1/answers/probe.wy4E/`
- `artifacts/n1/answers/probe.wy6O/`
- `artifacts/n1/keys/`
- `artifacts/n1/n1cal2/answers/probe.hAcw/`
- `artifacts/n1/n1cal2/answers/probe.o9aX/`
- `artifacts/n1/n1cal2/controls/`
- `artifacts/n1/n1cal2/keys/`
- `artifacts/n1/n1e/gate_scans/`
- `artifacts/n1/n1e/keys/`
- `artifacts/n1/n1t/`
- `artifacts/n1/n1t/controls/`
- `artifacts/n1/n1t/keys/`
- `artifacts/n1/n1t2/controls/`
- `artifacts/n1/n1t2/keys/`
- `artifacts/n1/n1t3/controls/`
- `artifacts/n1/n1t3/keys/`
- `artifacts/n1/n1tr/answers/`
- `artifacts/n1/n1tr/answers/probe.15uB/`
- `artifacts/n1/n1tr/answers/probe.19W2/`
- `artifacts/n1/n1tr/answers/probe.1BJ1/`
- `artifacts/n1/n1tr/answers/probe.4gC1/`
- `artifacts/n1/n1tr/answers/probe.5RM9/`
- `artifacts/n1/n1tr/answers/probe.5oPU/`
- `artifacts/n1/n1tr/answers/probe.A9Er/`
- `artifacts/n1/n1tr/answers/probe.DSwc/`
- `artifacts/n1/n1tr/answers/probe.GdPB/`
- `artifacts/n1/n1tr/answers/probe.J92S/`
- `artifacts/n1/n1tr/answers/probe.Kcoy/`
- `artifacts/n1/n1tr/answers/probe.QMHB/`
- `artifacts/n1/n1tr/answers/probe.XeUb/`
- `artifacts/n1/n1tr/answers/probe.Y2Qn/`
- `artifacts/n1/n1tr/answers/probe.a7gZ/`
- `artifacts/n1/n1tr/answers/probe.beWM/`
- `artifacts/n1/n1tr/answers/probe.dCao/`
- `artifacts/n1/n1tr/answers/probe.ecYT/`
- `artifacts/n1/n1tr/answers/probe.gxvT/`
- `artifacts/n1/n1tr/answers/probe.inN1/`
- `artifacts/n1/n1tr/answers/probe.kYkY/`
- `artifacts/n1/n1tr/answers/probe.of8O/`
- `artifacts/n1/n1tr/answers/probe.rowM/`
- `artifacts/n1/n1tr/answers/probe.xpno/`
- `artifacts/n1/n1tr/keys/`
- `artifacts/n1/n1w1/answers/`
- `artifacts/n1/n1w1/answers/probe.5L78/`
- `artifacts/n1/n1w1/answers/probe.8t3D/`
- `artifacts/n1/n1w1/answers/probe.B6Pe/`
- `artifacts/n1/n1w1/answers/probe.BSvJ/`
- `artifacts/n1/n1w1/answers/probe.BkWH/`
- `artifacts/n1/n1w1/answers/probe.COaL/`
- `artifacts/n1/n1w1/answers/probe.DSih/`
- `artifacts/n1/n1w1/answers/probe.DvDx/`
- `artifacts/n1/n1w1/answers/probe.JChy/`
- `artifacts/n1/n1w1/answers/probe.KOPd/`
- `artifacts/n1/n1w1/answers/probe.Ke3D/`
- `artifacts/n1/n1w1/answers/probe.M4kz/`
- `artifacts/n1/n1w1/answers/probe.Mcj2/`
- `artifacts/n1/n1w1/answers/probe.NFV2/`
- `artifacts/n1/n1w1/answers/probe.O71b/`
- `artifacts/n1/n1w1/answers/probe.O87m/`
- `artifacts/n1/n1w1/answers/probe.PWA3/`
- `artifacts/n1/n1w1/answers/probe.Qa2X/`
- `artifacts/n1/n1w1/answers/probe.QouE/`
- `artifacts/n1/n1w1/answers/probe.RqAz/`
- `artifacts/n1/n1w1/answers/probe.SHkq/`
- `artifacts/n1/n1w1/answers/probe.T4QW/`
- `artifacts/n1/n1w1/answers/probe.TEaj/`
- `artifacts/n1/n1w1/answers/probe.Whc1/`
- `artifacts/n1/n1w1/answers/probe.X2Ro/`
- `artifacts/n1/n1w1/answers/probe.aVPB/`
- `artifacts/n1/n1w1/answers/probe.aeiy/`
- `artifacts/n1/n1w1/answers/probe.dR6E/`
- `artifacts/n1/n1w1/answers/probe.durn/`
- `artifacts/n1/n1w1/answers/probe.e0ek/`
- `artifacts/n1/n1w1/answers/probe.e5yO/`
- `artifacts/n1/n1w1/answers/probe.emNe/`
- `artifacts/n1/n1w1/answers/probe.eufX/`
- `artifacts/n1/n1w1/answers/probe.f2V5/`
- `artifacts/n1/n1w1/answers/probe.gGAv/`
- `artifacts/n1/n1w1/answers/probe.jnpP/`
- `artifacts/n1/n1w1/answers/probe.kTwA/`
- `artifacts/n1/n1w1/answers/probe.kf8L/`
- `artifacts/n1/n1w1/answers/probe.khw0/`
- `artifacts/n1/n1w1/answers/probe.lVLQ/`
- `artifacts/n1/n1w1/answers/probe.lYNf/`
- `artifacts/n1/n1w1/answers/probe.lpAa/`
- `artifacts/n1/n1w1/answers/probe.lyGJ/`
- `artifacts/n1/n1w1/answers/probe.m03F/`
- `artifacts/n1/n1w1/answers/probe.mUxm/`
- `artifacts/n1/n1w1/answers/probe.oLP6/`
- `artifacts/n1/n1w1/answers/probe.p6Xn/`
- `artifacts/n1/n1w1/answers/probe.qDtZ/`
- `artifacts/n1/n1w1/answers/probe.rIhO/`
- `artifacts/n1/n1w1/answers/probe.tApn/`
- `artifacts/n1/n1w1/answers/probe.tulu/`
- `artifacts/n1/n1w1/answers/probe.vouK/`
- `artifacts/n1/n1w1/answers/probe.xMt0/`
- `artifacts/n1/n1w1/answers/probe.y0Wa/`
- `artifacts/n1/n1w1/answers/probe.yH3g/`
- `artifacts/n1/n1w1/answers/probe.zytC/`
- `artifacts/n1/n1w1/keys/`
- `artifacts/n1/n1w1/r3/answers/`
- `artifacts/n1/n1w1/r3/answers/probe.1eVD/`
- `artifacts/n1/n1w1/r3/answers/probe.3Mev/`
- `artifacts/n1/n1w1/r3/answers/probe.4SCC/`
- `artifacts/n1/n1w1/r3/answers/probe.5XDq/`
- `artifacts/n1/n1w1/r3/answers/probe.6Kkf/`
- `artifacts/n1/n1w1/r3/answers/probe.B7MJ/`
- `artifacts/n1/n1w1/r3/answers/probe.CzSY/`
- `artifacts/n1/n1w1/r3/answers/probe.EFG5/`
- `artifacts/n1/n1w1/r3/answers/probe.EL8T/`
- `artifacts/n1/n1w1/r3/answers/probe.FpKQ/`
- `artifacts/n1/n1w1/r3/answers/probe.JRrW/`
- `artifacts/n1/n1w1/r3/answers/probe.MrLe/`
- `artifacts/n1/n1w1/r3/answers/probe.O2xH/`
- `artifacts/n1/n1w1/r3/answers/probe.P2jB/`
- `artifacts/n1/n1w1/r3/answers/probe.Ryqv/`
- `artifacts/n1/n1w1/r3/answers/probe.UPcv/`
- `artifacts/n1/n1w1/r3/answers/probe.WlIx/`
- `artifacts/n1/n1w1/r3/answers/probe.X8zK/`
- `artifacts/n1/n1w1/r3/answers/probe.YCc9/`
- `artifacts/n1/n1w1/r3/answers/probe.Yw4w/`
- `artifacts/n1/n1w1/r3/answers/probe.ZiQY/`
- `artifacts/n1/n1w1/r3/answers/probe.bvV2/`
- `artifacts/n1/n1w1/r3/answers/probe.hUML/`
- `artifacts/n1/n1w1/r3/answers/probe.iuxb/`
- `artifacts/n1/n1w1/r3/answers/probe.kkuO/`
- `artifacts/n1/n1w1/r3/answers/probe.lnPC/`
- `artifacts/n1/n1w1/r3/answers/probe.mBmI/`
- `artifacts/n1/n1w1/r3/answers/probe.nBKi/`
- `artifacts/n1/n1w1/r3/answers/probe.p09I/`
- `artifacts/n1/n1w1/r3/answers/probe.rNEG/`
- `artifacts/n1/n1w1/r3/answers/probe.wUdr/`
- `artifacts/n1/n1w1/r3/answers/probe.y2Qq/`
- `artifacts/n1/n1w1/r3/keys/`
- `artifacts/n1/owner_sheet/`
- `artifacts/r2_resolve/T2/`
- `artifacts/r2_resolve/T2/final/`
- `artifacts/r2_resolve/T2/final/inputs/`
- `artifacts/r2_resolve/T4/`
- `artifacts/r2_resolve/T4/final/`
- `artifacts/r2_resolve/T4/final/inputs/`
- `artifacts/ru1/RU1S_original_scans/`
- `artifacts/ru1/RU1S_uncleared/`
- `artifacts/ru1/answers/probe.1aZ3/`
- `artifacts/ru1/answers/probe.2Kj2/`
- `artifacts/ru1/answers/probe.4jh4/`
- `artifacts/ru1/answers/probe.5doK/`
- `artifacts/ru1/answers/probe.79aO/`
- `artifacts/ru1/answers/probe.9XQc/`
- `artifacts/ru1/answers/probe.DPEk/`
- `artifacts/ru1/answers/probe.FSFp/`
- `artifacts/ru1/answers/probe.I7lW/`
- `artifacts/ru1/answers/probe.YXCN/`
- `artifacts/ru1/answers/probe.e6cO/`
- `artifacts/ru1/answers/probe.eO27/`
- `artifacts/ru1/answers/probe.fK2b/`
- `artifacts/ru1/answers/probe.kED4/`
- `artifacts/ru1/answers/probe.kFYx/`
- `artifacts/ru1/answers/probe.wNWn/`
- `artifacts/ru1/answers/probe.zWFn/`
- `artifacts/ru1/keys/`
- `artifacts/ru1/owner_sheet/`
- `artifacts/ru1/ru2t/answers/`
- `artifacts/ru1/ru2t/answers/probe.3mQF/`
- `artifacts/ru1/ru2t/answers/probe.JxQ4/`
- `artifacts/ru1/ru2t/answers/probe.K1Q9/`
- `artifacts/ru1/ru2t/answers/probe.KBHE/`
- `artifacts/ru1/ru2t/answers/probe.LyQi/`
- `artifacts/ru1/ru2t/answers/probe.NZQ7/`
- `artifacts/ru1/ru2t/answers/probe.RC2Z/`
- `artifacts/ru1/ru2t/answers/probe.XB2O/`
- `artifacts/ru1/ru2t/answers/probe.XuWK/`
- `artifacts/ru1/ru2t/answers/probe.ejo9/`
- `artifacts/ru1/ru2t/answers/probe.k853/`
- `artifacts/ru1/ru2t/answers/probe.lbHw/`
- `artifacts/ru1/ru2t/answers/probe.oEao/`
- `artifacts/ru1/ru2t/answers/probe.uG8p/`
- `artifacts/ru1/ru2t/answers/probe.uSH9/`
- `artifacts/ru1/ru2t/answers/probe.zpqS/`
- `artifacts/ru1/ru2t/keys/`
- `artifacts/ru1/ru3t/answers/`
- `artifacts/ru1/ru3t/answers/probe.00M5/`
- `artifacts/ru1/ru3t/answers/probe.0N0a/`
- `artifacts/ru1/ru3t/answers/probe.0Ur4/`
- `artifacts/ru1/ru3t/answers/probe.0X8m/`
- `artifacts/ru1/ru3t/answers/probe.0otX/`
- `artifacts/ru1/ru3t/answers/probe.1CNK/`
- `artifacts/ru1/ru3t/answers/probe.1g2f/`
- `artifacts/ru1/ru3t/answers/probe.1mCC/`
- `artifacts/ru1/ru3t/answers/probe.1rei/`
- `artifacts/ru1/ru3t/answers/probe.2heh/`
- `artifacts/ru1/ru3t/answers/probe.2oTG/`
- `artifacts/ru1/ru3t/answers/probe.3dHD/`
- `artifacts/ru1/ru3t/answers/probe.49pf/`
- `artifacts/ru1/ru3t/answers/probe.4MFX/`
- `artifacts/ru1/ru3t/answers/probe.4MRu/`
- `artifacts/ru1/ru3t/answers/probe.4R3R/`
- `artifacts/ru1/ru3t/answers/probe.4vbA/`
- `artifacts/ru1/ru3t/answers/probe.6J0y/`
- `artifacts/ru1/ru3t/answers/probe.6SOu/`
- `artifacts/ru1/ru3t/answers/probe.6mH7/`
- `artifacts/ru1/ru3t/answers/probe.77T5/`
- `artifacts/ru1/ru3t/answers/probe.8dLU/`
- `artifacts/ru1/ru3t/answers/probe.8zeh/`
- `artifacts/ru1/ru3t/answers/probe.9LGp/`
- `artifacts/ru1/ru3t/answers/probe.9m4g/`
- `artifacts/ru1/ru3t/answers/probe.BpA2/`
- `artifacts/ru1/ru3t/answers/probe.BwYa/`
- `artifacts/ru1/ru3t/answers/probe.C4CT/`
- `artifacts/ru1/ru3t/answers/probe.CZQp/`
- `artifacts/ru1/ru3t/answers/probe.D4Yr/`
- `artifacts/ru1/ru3t/answers/probe.DMsG/`
- `artifacts/ru1/ru3t/answers/probe.DROW/`
- `artifacts/ru1/ru3t/answers/probe.DW4I/`
- `artifacts/ru1/ru3t/answers/probe.F5Dn/`
- `artifacts/ru1/ru3t/answers/probe.F5bM/`
- `artifacts/ru1/ru3t/answers/probe.FiMe/`
- `artifacts/ru1/ru3t/answers/probe.Fv11/`
- `artifacts/ru1/ru3t/answers/probe.G4Zn/`
- `artifacts/ru1/ru3t/answers/probe.GLko/`
- `artifacts/ru1/ru3t/answers/probe.HSCQ/`
- `artifacts/ru1/ru3t/answers/probe.KBB3/`
- `artifacts/ru1/ru3t/answers/probe.KL4c/`
- `artifacts/ru1/ru3t/answers/probe.KajV/`
- `artifacts/ru1/ru3t/answers/probe.L3F3/`
- `artifacts/ru1/ru3t/answers/probe.L5Gy/`
- `artifacts/ru1/ru3t/answers/probe.LLfL/`
- `artifacts/ru1/ru3t/answers/probe.Lgyk/`
- `artifacts/ru1/ru3t/answers/probe.MGzZ/`
- `artifacts/ru1/ru3t/answers/probe.MzJN/`
- `artifacts/ru1/ru3t/answers/probe.NHE6/`
- `artifacts/ru1/ru3t/answers/probe.O0we/`
- `artifacts/ru1/ru3t/answers/probe.O8WE/`
- `artifacts/ru1/ru3t/answers/probe.OfDi/`
- `artifacts/ru1/ru3t/answers/probe.OoPk/`
- `artifacts/ru1/ru3t/answers/probe.P2vS/`
- `artifacts/ru1/ru3t/answers/probe.PA8q/`
- `artifacts/ru1/ru3t/answers/probe.PYZd/`
- `artifacts/ru1/ru3t/answers/probe.Q3Sg/`
- `artifacts/ru1/ru3t/answers/probe.QCOt/`
- `artifacts/ru1/ru3t/answers/probe.RDw8/`
- `artifacts/ru1/ru3t/answers/probe.Rhyb/`
- `artifacts/ru1/ru3t/answers/probe.SG6D/`
- `artifacts/ru1/ru3t/answers/probe.Sb0M/`
- `artifacts/ru1/ru3t/answers/probe.TcwF/`
- `artifacts/ru1/ru3t/answers/probe.TpAi/`
- `artifacts/ru1/ru3t/answers/probe.Tula/`
- `artifacts/ru1/ru3t/answers/probe.URSq/`
- `artifacts/ru1/ru3t/answers/probe.UnwR/`
- `artifacts/ru1/ru3t/answers/probe.VKTV/`
- `artifacts/ru1/ru3t/answers/probe.VKsn/`
- `artifacts/ru1/ru3t/answers/probe.Vlxh/`
- `artifacts/ru1/ru3t/answers/probe.VwOE/`
- `artifacts/ru1/ru3t/answers/probe.Vx7T/`
- `artifacts/ru1/ru3t/answers/probe.Wd2w/`
- `artifacts/ru1/ru3t/answers/probe.XDGw/`
- `artifacts/ru1/ru3t/answers/probe.XDS6/`
- `artifacts/ru1/ru3t/answers/probe.XSrl/`
- `artifacts/ru1/ru3t/answers/probe.XXMO/`
- `artifacts/ru1/ru3t/answers/probe.XfrD/`
- `artifacts/ru1/ru3t/answers/probe.XhYV/`
- `artifacts/ru1/ru3t/answers/probe.Y3nu/`
- `artifacts/ru1/ru3t/answers/probe.YBVd/`
- `artifacts/ru1/ru3t/answers/probe.YLHB/`
- `artifacts/ru1/ru3t/answers/probe.YPJm/`
- `artifacts/ru1/ru3t/answers/probe.Yl0c/`
- `artifacts/ru1/ru3t/answers/probe.ZfbF/`
- `artifacts/ru1/ru3t/answers/probe.aSZa/`
- `artifacts/ru1/ru3t/answers/probe.aZRe/`
- `artifacts/ru1/ru3t/answers/probe.bFhx/`
- `artifacts/ru1/ru3t/answers/probe.bZMW/`
- `artifacts/ru1/ru3t/answers/probe.biQw/`
- `artifacts/ru1/ru3t/answers/probe.bvIj/`
- `artifacts/ru1/ru3t/answers/probe.c5BX/`
- `artifacts/ru1/ru3t/answers/probe.cFpV/`
- `artifacts/ru1/ru3t/answers/probe.crgl/`
- `artifacts/ru1/ru3t/answers/probe.cuP0/`
- `artifacts/ru1/ru3t/answers/probe.d0mv/`
- `artifacts/ru1/ru3t/answers/probe.d5zG/`
- `artifacts/ru1/ru3t/answers/probe.dAmC/`
- `artifacts/ru1/ru3t/answers/probe.dPXz/`
- `artifacts/ru1/ru3t/answers/probe.dxBi/`
- `artifacts/ru1/ru3t/answers/probe.e7Zy/`
- `artifacts/ru1/ru3t/answers/probe.eBtz/`
- `artifacts/ru1/ru3t/answers/probe.fQjB/`
- `artifacts/ru1/ru3t/answers/probe.gCg9/`
- `artifacts/ru1/ru3t/answers/probe.gNDo/`
- `artifacts/ru1/ru3t/answers/probe.gt7U/`
- `artifacts/ru1/ru3t/answers/probe.hYyL/`
- `artifacts/ru1/ru3t/answers/probe.haOS/`
- `artifacts/ru1/ru3t/answers/probe.jrN1/`
- `artifacts/ru1/ru3t/answers/probe.jzvi/`
- `artifacts/ru1/ru3t/answers/probe.jzvk/`
- `artifacts/ru1/ru3t/answers/probe.kZ7H/`
- `artifacts/ru1/ru3t/answers/probe.kcXT/`
- `artifacts/ru1/ru3t/answers/probe.kn9Q/`
- `artifacts/ru1/ru3t/answers/probe.kq0o/`
- `artifacts/ru1/ru3t/answers/probe.lEJv/`
- `artifacts/ru1/ru3t/answers/probe.mWtt/`
- `artifacts/ru1/ru3t/answers/probe.mbwo/`
- `artifacts/ru1/ru3t/answers/probe.qDHC/`
- `artifacts/ru1/ru3t/answers/probe.qj6J/`
- `artifacts/ru1/ru3t/answers/probe.qjJ5/`
- `artifacts/ru1/ru3t/answers/probe.rr09/`
- `artifacts/ru1/ru3t/answers/probe.s8l4/`
- `artifacts/ru1/ru3t/answers/probe.sV1t/`
- `artifacts/ru1/ru3t/answers/probe.t8JM/`
- `artifacts/ru1/ru3t/answers/probe.tcmu/`
- `artifacts/ru1/ru3t/answers/probe.tdEW/`
- `artifacts/ru1/ru3t/answers/probe.uG63/`
- `artifacts/ru1/ru3t/answers/probe.vGmj/`
- `artifacts/ru1/ru3t/answers/probe.vtpQ/`
- `artifacts/ru1/ru3t/answers/probe.wFEE/`
- `artifacts/ru1/ru3t/answers/probe.wiVn/`
- `artifacts/ru1/ru3t/answers/probe.wlVR/`
- `artifacts/ru1/ru3t/answers/probe.x96Q/`
- `artifacts/ru1/ru3t/answers/probe.x9VI/`
- `artifacts/ru1/ru3t/answers/probe.xl2y/`
- `artifacts/ru1/ru3t/answers/probe.zNhg/`
- `artifacts/ru1/ru3t/keys/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.1GE4/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.2c6K/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.6Pty/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.8H62/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.9AFj/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.BjRY/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.Ctdy/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.E1kD/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.HImb/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.J2FO/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.WhmF/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.XNTN/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.dArf/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.dPjY/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.j4ko/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.k9hm/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.kYGt/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.qpWx/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.rVqA/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.yl00/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.yliJ/`
- `artifacts/ru1/ru3t/r3_replacements/r3/answers/probe.zw1u/`
- `artifacts/ru1/ru3t/r3_replacements/r3/keys/`
- `artifacts/ru1/ru3t/r3_replacements/r4/answers/`
- `artifacts/ru1/ru3t/r3_replacements/r4/answers/probe.AObe/`
- `artifacts/ru1/ru3t/r3_replacements/r4/answers/probe.O1tz/`
- `artifacts/ru1/ru3t/r3_replacements/r4/keys/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.3kha/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.56U2/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.6lDC/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.IbYS/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.VFrT/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.oxNg/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.pFMk/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.qcBb/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.sTxc/`
- `artifacts/ru1/ru3t/r5_replacements/r5/answers/probe.zPEy/`
- `artifacts/ru1/ru3t/r5_replacements/r5/keys/`
- `artifacts/ru1/ru3t/ru3t1/preflight_failures/`
- `artifacts/ru1/ru4e2/answers/`
- `artifacts/ru1/ru4e2/answers/probe.0d14/`
- `artifacts/ru1/ru4e2/answers/probe.1Txh/`
- `artifacts/ru1/ru4e2/answers/probe.1c8g/`
- `artifacts/ru1/ru4e2/answers/probe.1huF/`
- `artifacts/ru1/ru4e2/answers/probe.2TW0/`
- `artifacts/ru1/ru4e2/answers/probe.4GRQ/`
- `artifacts/ru1/ru4e2/answers/probe.4ewV/`
- `artifacts/ru1/ru4e2/answers/probe.4fnZ/`
- `artifacts/ru1/ru4e2/answers/probe.4mIJ/`
- `artifacts/ru1/ru4e2/answers/probe.68Wo/`
- `artifacts/ru1/ru4e2/answers/probe.6QPH/`
- `artifacts/ru1/ru4e2/answers/probe.83oe/`
- `artifacts/ru1/ru4e2/answers/probe.8Hdg/`
- `artifacts/ru1/ru4e2/answers/probe.8yLG/`
- `artifacts/ru1/ru4e2/answers/probe.9LAx/`
- `artifacts/ru1/ru4e2/answers/probe.AjpG/`
- `artifacts/ru1/ru4e2/answers/probe.Ao83/`
- `artifacts/ru1/ru4e2/answers/probe.BEFi/`
- `artifacts/ru1/ru4e2/answers/probe.BjXf/`
- `artifacts/ru1/ru4e2/answers/probe.BpWP/`
- `artifacts/ru1/ru4e2/answers/probe.D51t/`
- `artifacts/ru1/ru4e2/answers/probe.Dcov/`
- `artifacts/ru1/ru4e2/answers/probe.EahS/`
- `artifacts/ru1/ru4e2/answers/probe.GCqb/`
- `artifacts/ru1/ru4e2/answers/probe.GYCe/`
- `artifacts/ru1/ru4e2/answers/probe.HzQQ/`
- `artifacts/ru1/ru4e2/answers/probe.IPRN/`
- `artifacts/ru1/ru4e2/answers/probe.Jzmu/`
- `artifacts/ru1/ru4e2/answers/probe.K5st/`
- `artifacts/ru1/ru4e2/answers/probe.KQ6p/`
- `artifacts/ru1/ru4e2/answers/probe.KQr8/`
- `artifacts/ru1/ru4e2/answers/probe.LHxW/`
- `artifacts/ru1/ru4e2/answers/probe.LLI1/`
- `artifacts/ru1/ru4e2/answers/probe.LUX0/`
- `artifacts/ru1/ru4e2/answers/probe.LcsW/`
- `artifacts/ru1/ru4e2/answers/probe.Lgtn/`
- `artifacts/ru1/ru4e2/answers/probe.M9ew/`
- `artifacts/ru1/ru4e2/answers/probe.Nl4M/`
- `artifacts/ru1/ru4e2/answers/probe.NmNR/`
- `artifacts/ru1/ru4e2/answers/probe.OCFu/`
- `artifacts/ru1/ru4e2/answers/probe.OuCF/`
- `artifacts/ru1/ru4e2/answers/probe.P3mH/`
- `artifacts/ru1/ru4e2/answers/probe.R87B/`
- `artifacts/ru1/ru4e2/answers/probe.RCj6/`
- `artifacts/ru1/ru4e2/answers/probe.RDy5/`
- `artifacts/ru1/ru4e2/answers/probe.S0gC/`
- `artifacts/ru1/ru4e2/answers/probe.SzVS/`
- `artifacts/ru1/ru4e2/answers/probe.TFIx/`
- `artifacts/ru1/ru4e2/answers/probe.TRba/`
- `artifacts/ru1/ru4e2/answers/probe.UTYV/`
- `artifacts/ru1/ru4e2/answers/probe.VUne/`
- `artifacts/ru1/ru4e2/answers/probe.XKWD/`
- `artifacts/ru1/ru4e2/answers/probe.Xprp/`
- `artifacts/ru1/ru4e2/answers/probe.Xt5k/`
- `artifacts/ru1/ru4e2/answers/probe.YFGV/`
- `artifacts/ru1/ru4e2/answers/probe.YVhU/`
- `artifacts/ru1/ru4e2/answers/probe.YzIo/`
- `artifacts/ru1/ru4e2/answers/probe.ZB5u/`
- `artifacts/ru1/ru4e2/answers/probe.ZIHG/`
- `artifacts/ru1/ru4e2/answers/probe.adl7/`
- `artifacts/ru1/ru4e2/answers/probe.atMw/`
- `artifacts/ru1/ru4e2/answers/probe.b0BB/`
- `artifacts/ru1/ru4e2/answers/probe.cjOZ/`
- `artifacts/ru1/ru4e2/answers/probe.dkGU/`
- `artifacts/ru1/ru4e2/answers/probe.ejQn/`
- `artifacts/ru1/ru4e2/answers/probe.f55r/`
- `artifacts/ru1/ru4e2/answers/probe.fXoe/`
- `artifacts/ru1/ru4e2/answers/probe.gxxW/`
- `artifacts/ru1/ru4e2/answers/probe.hPIm/`
- `artifacts/ru1/ru4e2/answers/probe.hvbY/`
- `artifacts/ru1/ru4e2/answers/probe.jIab/`
- `artifacts/ru1/ru4e2/answers/probe.l5UD/`
- `artifacts/ru1/ru4e2/answers/probe.lQYh/`
- `artifacts/ru1/ru4e2/answers/probe.mjWU/`
- `artifacts/ru1/ru4e2/answers/probe.o3yP/`
- `artifacts/ru1/ru4e2/answers/probe.oKMO/`
- `artifacts/ru1/ru4e2/answers/probe.oscw/`
- `artifacts/ru1/ru4e2/answers/probe.ozsg/`
- `artifacts/ru1/ru4e2/answers/probe.pPmw/`
- `artifacts/ru1/ru4e2/answers/probe.q9nO/`
- `artifacts/ru1/ru4e2/answers/probe.qBwg/`
- `artifacts/ru1/ru4e2/answers/probe.s5RO/`
- `artifacts/ru1/ru4e2/answers/probe.sL0h/`
- `artifacts/ru1/ru4e2/answers/probe.tCnz/`
- `artifacts/ru1/ru4e2/answers/probe.uN4M/`
- `artifacts/ru1/ru4e2/answers/probe.uesl/`
- `artifacts/ru1/ru4e2/answers/probe.ujS9/`
- `artifacts/ru1/ru4e2/answers/probe.xKzP/`
- `artifacts/ru1/ru4e2/failed_metadata_keys/`
- `artifacts/ru1/ru4e2/keys/`
- `artifacts/ru1/ru4e2/lead/crops/`
- `artifacts/ru1/ru4e2/phase1_cache/`
- `artifacts/ru1/ru4e2/r3_replacements/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx01-r2/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx01-r2/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx01-r2/keys/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx04-r2/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx04-r2/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx04-r2/keys/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx07-r1/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx07-r1/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx07-r1/keys/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx08-r1/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx08-r1/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx08-r1/keys/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx11-r1/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx11-r1/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx11-r1/keys/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx12-r1/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx12-r1/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx12-r1/keys/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx14-r2/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx14-r2/answers/`
- `artifacts/ru1/ru4e2/r3_replacements/ctx14-r2/keys/`
- `artifacts/ru1/ru4e2/r4_replacements/`
- `artifacts/ru1/ru4e2/r4_replacements/ctx08-r2/`
- `artifacts/ru1/ru4e2/r4_replacements/ctx08-r2/answers/`
- `artifacts/ru1/ru4e2/r4_replacements/ctx08-r2/keys/`
- `artifacts/ru1/ru4e2/r4_replacements/ctx11-r2/`
- `artifacts/ru1/ru4e2/r4_replacements/ctx11-r2/answers/`
- `artifacts/ru1/ru4e2/r4_replacements/ctx11-r2/keys/`
- `artifacts/ru1/ru4e2/r5_replacements/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx04-r2/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx04-r2/answers/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx04-r2/keys/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx11-r1/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx11-r1/answers/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx11-r1/keys/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx11-r2/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx11-r2/answers/`
- `artifacts/ru1/ru4e2/r5_replacements/ctx11-r2/keys/`
- `artifacts/sf7_rc1/audit/final_score/`
- `artifacts/sf7_rc1/audit/final_scores/`
- `artifacts/sf7_rc1/audit/final_scores/20261019T105122_234081Z/`
- `artifacts/sf7_rc1/audit/keys/`
- `artifacts/sf7_rc1/audit/opus_keys/deck/blind/img/`
- `artifacts/sf7_rc1/audit/opus_keys/deck/private/`
- `artifacts/sf7_rc1/audit/opus_keys/prep_score/`
- `artifacts/tr2/probe.99CM/`
- `docs/MR_C_evidence/`
- `docs/cleanup_20261019/inventory/evidence/`
- `docs/records/harvest/analysis/clean_preview/`
- `docs/records/harvest/blind_checks_v1/c0/ia_greek_latin/`
- `docs/records/harvest/blind_checks_v1/c0/ia_greek_latin/crops/`
- `docs/records/harvest/blind_checks_v1/c0/ia_poly1850/`
- `docs/records/harvest/blind_checks_v1/c0/ia_poly1850/crops/`
- `docs/records/harvest/blind_checks_v1/c0/ia_russian/`
- `docs/records/harvest/blind_checks_v1/c0/ia_russian/crops/`
- `docs/records/harvest/blind_checks_v1/c0/kosmopolis_poly/`
- `docs/records/harvest/blind_checks_v1/c0/kosmopolis_poly/crops/`
- `docs/records/harvest/blind_checks_v1/c0/nlg_poly/`
- `docs/records/harvest/blind_checks_v1/c0/nlg_poly/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/anemi_poly1850/`
- `docs/records/harvest/blind_checks_v1/t4c/anemi_poly1850/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/bsb_mixed/`
- `docs/records/harvest/blind_checks_v1/t4c/bsb_mixed/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/bsb_poly1850/`
- `docs/records/harvest/blind_checks_v1/t4c/bsb_poly1850/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/gazette_modern/`
- `docs/records/harvest/blind_checks_v1/t4c/gazette_modern/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/gazette_poly1900/`
- `docs/records/harvest/blind_checks_v1/t4c/gazette_poly1900/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/lekythos_poly1900/`
- `docs/records/harvest/blind_checks_v1/t4c/lekythos_poly1900/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/oa_poly1900/`
- `docs/records/harvest/blind_checks_v1/t4c/oa_poly1900/crops/`
- `docs/records/harvest/blind_checks_v1/t4c/pleias_poly1850/`
- `docs/records/harvest/blind_checks_v1/t4c/pleias_poly1850/crops/`
- `docs/records/harvest/collect_v3/c1/efficiency/keys/bsb/`
- `docs/records/harvest/collect_v3/c1/efficiency/keys/yer/`
- `docs/records/harvest/collect_v3/c1/verdicts/`
- `docs/records/harvest/collect_v3/item_draws/`
- `docs/records/harvest/collect_v3/offline_replay/`
- `docs/records/harvest/collect_v3/remaining_inventory/`
- `docs/records/harvest/collect_v3/rev2_final_replay/`
- `docs/records/harvest/collect_v3/rev2_verified_replay/`
- `docs/records/harvest/collect_v3/w1c_verified_replay/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/crops/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/probe.J0YP/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/probe.K0Wb/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/probe.OYS4/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/launchers/probe.SGG0/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/crops/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/launchers/probe.18fn/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/launchers/probe.mQx8/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/receipts/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/scan/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/scan/segcp7r2_a/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/scan/segcp7r2_b/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/receipts/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/scan/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/scan/segcp7_a/`
- `docs/records/harvest/collect_v3_admission/seg/cp7/scan/segcp7_b/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/rollouts/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_a/r1/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_a/r1/crops/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_a/r1/zoom/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_b/r1/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_b/r1/crops/`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_b/r1/zoom/`
- `docs/records/harvest/collect_v3_admission/segeval1/cells/samples/`
- `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/crops/`
- `docs/records/harvest/collect_v3_admission/segeval1/crops/`
- `docs/records/harvest/collect_v3_admission/segeval1/deskew/baseline/docs/`
- `docs/records/harvest/collect_v3_admission/segeval1/deskew/baseline/docs/harvest/`
- `docs/records/harvest/collect_v3_admission/segeval1/deskew/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/docs/`
- `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/docs/harvest/`
- `docs/records/harvest/collect_v3_admission/segeval1/gate/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/docs/`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/docs/harvest/`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/collect_v3_admission/segeval1/launchers/probe.0sHp/`
- `docs/records/harvest/collect_v3_admission/segeval1/launchers/probe.OyTS/`
- `docs/records/harvest/collect_v3_admission/segeval1/launchers/probe.mytF/`
- `docs/records/harvest/collect_v3_admission/segeval1/launchers/probe.tHPG/`
- `docs/records/harvest/collect_v3_admission/segeval1/scan/`
- `docs/records/harvest/collect_v3_admission/segeval1/scan/segeval1_a/`
- `docs/records/harvest/collect_v3_admission/segeval1/scan/segeval1_b/`
- `docs/records/harvest/collect_v3_admission/segeval1/scan/v4.5.5/`
- `docs/records/harvest/collect_v3_admission/segeval1/scan/v4.5.5/segeval1_a/`
- `docs/records/harvest/collect_v3_admission/segeval1/scan/v4.5.5/segeval1_b/`
- `docs/records/harvest/collect_v3_admission/segeval1/scored/`
- `docs/records/harvest/collect_v3_admission/segeval1/scored/v4.4/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/crops/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/answers/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/control_sheets/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/eye_sheets/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/keys/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/manifests/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/manifests/type2/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/replay_fixture/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/replay_fixture/fontconfig/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/replay_fixture_ss4c/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/sheet/marks_dump/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/sheet/marks_dump/20261019T1827/`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/sheet/marks_dump/20261019T1827/notes/`
- `docs/records/harvest/collect_v3_admission/split1/crops/`
- `docs/records/harvest/cyrillic/acquisitions/`
- `docs/records/harvest/cyrillic/assignments/`
- `docs/records/harvest/cyrillic/gates/`
- `docs/records/harvest/fix1/`
- `docs/records/harvest/fix2/`
- `docs/records/harvest/funnel_v1/gr/receipts/`
- `docs/records/harvest/funnel_v1/gr/receipts/metadata/`
- `docs/records/harvest/funnel_v1/gr/receipts/oa-catalogue-rebinding/`
- `docs/records/harvest/funnel_v1/gr/receipts/pergamos-queries/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/anemi/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/bank-of-greece/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/elstat/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/gennadius/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/government-gazette/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/kosmopolis/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/laskaridis-travelogues/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/lekythos/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/medusa-veria/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/nlg-digital/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/nlg-newspapers/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/openarchives/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/pergamos/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/pleias/`
- `docs/records/harvest/funnel_v1/gr/receipts/prior/psifiothiki/`
- `docs/records/harvest/funnel_v1/gr/receipts/review/`
- `docs/records/harvest/funnel_v1/gr/receipts/robots/`
- `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/`
- `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/`
- `docs/records/harvest/inventory_v2/receipts/anemi/`
- `docs/records/harvest/inventory_v2/receipts/anemi/http/`
- `docs/records/harvest/inventory_v2/receipts/bank-of-greece/`
- `docs/records/harvest/inventory_v2/receipts/bank-of-greece/http/`
- `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/`
- `docs/records/harvest/inventory_v2/receipts/bulgarian-national-library/`
- `docs/records/harvest/inventory_v2/receipts/bulgarian-national-library/http/`
- `docs/records/harvest/inventory_v2/receipts/e-periodica/`
- `docs/records/harvest/inventory_v2/receipts/e-periodica/http/`
- `docs/records/harvest/inventory_v2/receipts/e-rara/`
- `docs/records/harvest/inventory_v2/receipts/e-rara/http/`
- `docs/records/harvest/inventory_v2/receipts/elstat/`
- `docs/records/harvest/inventory_v2/receipts/elstat/http/`
- `docs/records/harvest/inventory_v2/receipts/gallica/`
- `docs/records/harvest/inventory_v2/receipts/gallica/http/`
- `docs/records/harvest/inventory_v2/receipts/gennadius/`
- `docs/records/harvest/inventory_v2/receipts/gennadius/http/`
- `docs/records/harvest/inventory_v2/receipts/google-books/`
- `docs/records/harvest/inventory_v2/receipts/google-books/http/`
- `docs/records/harvest/inventory_v2/receipts/government-gazette/`
- `docs/records/harvest/inventory_v2/receipts/government-gazette/http/`
- `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/`
- `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/`
- `docs/records/harvest/inventory_v2/receipts/hathitrust/`
- `docs/records/harvest/inventory_v2/receipts/hathitrust/http/`
- `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/`
- `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/`
- `docs/records/harvest/inventory_v2/receipts/internet-archive/`
- `docs/records/harvest/inventory_v2/receipts/internet-archive-code/`
- `docs/records/harvest/inventory_v2/receipts/internet-archive-code/http/`
- `docs/records/harvest/inventory_v2/receipts/internet-archive/http/`
- `docs/records/harvest/inventory_v2/receipts/kosmopolis/`
- `docs/records/harvest/inventory_v2/receipts/kosmopolis/http/`
- `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/`
- `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/`
- `docs/records/harvest/inventory_v2/receipts/lekythos/`
- `docs/records/harvest/inventory_v2/receipts/lekythos/http/`
- `docs/records/harvest/inventory_v2/receipts/local/`
- `docs/records/harvest/inventory_v2/receipts/logios-kalchas/`
- `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/`
- `docs/records/harvest/inventory_v2/receipts/lsj-1940/`
- `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/`
- `docs/records/harvest/inventory_v2/receipts/medusa-veria/`
- `docs/records/harvest/inventory_v2/receipts/medusa-veria/http/`
- `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/`
- `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/`
- `docs/records/harvest/inventory_v2/receipts/nlg-digital/`
- `docs/records/harvest/inventory_v2/receipts/nlg-digital/http/`
- `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/`
- `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/`
- `docs/records/harvest/inventory_v2/receipts/openarchives/`
- `docs/records/harvest/inventory_v2/receipts/openarchives/http/`
- `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/`
- `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/`
- `docs/records/harvest/inventory_v2/receipts/pergamos/`
- `docs/records/harvest/inventory_v2/receipts/pergamos/http/`
- `docs/records/harvest/inventory_v2/receipts/persee-bch/`
- `docs/records/harvest/inventory_v2/receipts/persee-bch/http/`
- `docs/records/harvest/inventory_v2/receipts/perseus-first1k/`
- `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/`
- `docs/records/harvest/inventory_v2/receipts/pleias/`
- `docs/records/harvest/inventory_v2/receipts/pleias/http/`
- `docs/records/harvest/inventory_v2/receipts/pogretra/`
- `docs/records/harvest/inventory_v2/receipts/pogretra/http/`
- `docs/records/harvest/inventory_v2/receipts/polyton-db/`
- `docs/records/harvest/inventory_v2/receipts/polyton-db/http/`
- `docs/records/harvest/inventory_v2/receipts/psifiothiki/`
- `docs/records/harvest/inventory_v2/receipts/psifiothiki/http/`
- `docs/records/harvest/inventory_v2/receipts/research/`
- `docs/records/harvest/inventory_v2/receipts/russian-national-library/`
- `docs/records/harvest/inventory_v2/receipts/russian-national-library/http/`
- `docs/records/harvest/inventory_v2/receipts/serbian-national-library/`
- `docs/records/harvest/inventory_v2/receipts/serbian-national-library/http/`
- `docs/records/harvest/inventory_v2/receipts/snhell/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-bg/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-bg/http/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-el/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-ru/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-sr/`
- `docs/records/harvest/inventory_v2/receipts/wikisource-sr/http/`
- `docs/harvest/line_pipeline/clariden/inventory/`
- `docs/records/harvest/mixed/anemi_fetch_invocations/`
- `docs/records/harvest/mixed/assignments/`
- `docs/records/harvest/mixed/compiled_pages/`
- `docs/records/harvest/mixed/direct_results_B/`
- `docs/records/harvest/mixed/gates/`
- `docs/records/harvest/mixed/read_snapshots/`
- `docs/records/harvest/mixed/visual_samples/`
- `docs/records/harvest/montage_v1/assignments/`
- `docs/records/harvest/montage_v1/determinism/google/`
- `docs/records/harvest/montage_v1/determinism/google/docai/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/0a6727f8bb9602edd6b8c93c6cbefbf2dcb79fafa5d9ff1e0b97b6352d106ef5-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/0ef27a12480c04307af7cac462bd5d74a517408d100d40636f20d11c1d796d32-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/13dc8df82ba264090e9716d6622076ad09f8f570f566ef81104eb737e141db22-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/29bbc139108fa6a2615ac48468fc51b2e42ba6f87ef5b4579ceb936727eab759-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/2f2222bdf80112bb44a77ecea1ef91e8201d1ee3793ff7030eef20109b1003a3-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/3318db9a0a348f59b071e143654e21bebfd5deeaabce96b86a300b0a2beed50d-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/3ffcdbfce2a450fe946d4ffa9518bc33556ad06d29bce006f086d9ff4c2899eb-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/404982c7356ea16cab82c153d1ff9f985307799cb73bee0ea41f6d1d7c19f67b-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/426a8bb906417b3878b3b70ea5253f0976be16e8fa0362357389052601bf09ea-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/502c3af8700c4e8f7997117ef30cfad81b4fa6b6b38ba5229cfb8ef7ae3d2493-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/56f9501f70da7c30bdb48d80f713ca234c4ab2c4a2065086c8567e20f002526a-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/57cdeacdf011c27896d7a0c19c99b7ccc9dc2c846e98f23497dd284f2f7bb1a5-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/596f25a50625be00cd9bb2ce7e4ee8155b5d9ac953a767c44dd2480a72c8cefe-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/61a560daefd6284c14b9c62b1b0d63ec5c16f3a020c928702b07b8e6f5cb444f-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/6409257f4aa3a35cd21aeef6dca877cfd7f59fae34638dd3c692b3b80da37ce5-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/70a9384fa767f3d58686b629ce3a51c457f9f5f77a199c0f27e4d649cdcf06d3-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/8d8d0734d8801eddae5969ed9d223bacaacc7880b21c68b5f23e2638bb73c997-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/8f09fe8a3f774f175d2d965c8e01c4125fe0931fdce493e27186a2a7d184d3d8-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/9233a696c0ce096f9333f0647f378076867dce8bf3479e25de836edb033bcba9-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/a2f02606b63e63d84acb31dcb93ab0176b9724b8b9adcb956c349c225d7fbfd7-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/ac9741a33c500232d0622fc4b9f910f004ae9cf3fb563b1901c91afceea5a7d9-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/b11fcf19f1851cb6664400d649f6691cea36501edd938070f0d810e81329b445-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/bb5b3dfe9a2dc0cdb0fb9a7098c4ab367b6070c4edeeb42ee36e6c9b6e7e44ac-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/be4ae7970a196885910ede09fd0bb393581e2eb65b4b14f97b4331395afeec07-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/bede32efe327e1c62ef6d8136f266381a806a84b48ece945003130094b8d74c3-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/cb3b38a9ac20ea665e63076ab289fadd4287a41a56d2640b878b349f53988595-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/cb6b773a3e589ca6b5d3581e66f8566177ccd1e5763ae17cd07b2a5cee33aeb2-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/e11a8f07ee9940fb3263bbed6de6c9be89b87977970e4137843efcd73556c580-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/eba780127e6d05f0b8593e651a314a7a4b6fdb46f77b26020f55db6d8b1d5eb0-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/f0a88cf0c1ae583b2e7b01f2c4c8f9a9c14d1d4f55969fd99ed45873f0838b27-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/f52a4f7f5f7b483e6a9fcf594fb11d4d386534d147527aa4ce139e5b17d7d2bc-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/docai/6728426b11b3c10f95478ef943eb45ddcdb689384fdc43e85e9a69930fbaec0f/fd6a9b94f78f06251f7ca95573c7bc17036225ac2c153ea7b6010cfd0bd3e522-pretrained-ocr-v2.1-2024-08-07/`
- `docs/records/harvest/montage_v1/determinism/google/parsed/`
- `docs/records/harvest/montage_v1/determinism/google/parsed/docai/`
- `docs/records/harvest/montage_v1/determinism/google/parsed/vision/`
- `docs/records/harvest/montage_v1/determinism/google/vision/`
- `docs/records/harvest/montage_v1/determinism/google/vision/adapter_receipts/`
- `docs/records/harvest/montage_v1/determinism/google/vision/responses/`
- `docs/records/harvest/montage_v1/determinism/norule/assignments/`
- `docs/records/harvest/montage_v1/determinism/norule/images/`
- `docs/records/harvest/montage_v1/determinism/norule/maps/`
- `docs/records/harvest/montage_v1/determinism/singles/`
- `docs/records/harvest/montage_v1/flush/assignments/`
- `docs/records/harvest/montage_v1/flush/assignments/flush/`
- `docs/records/harvest/montage_v1/flush/assignments/norule/`
- `docs/records/harvest/montage_v1/flush/maps/`
- `docs/records/harvest/montage_v1/flush/maps/flush/`
- `docs/records/harvest/montage_v1/flush/maps/norule/`
- `docs/records/harvest/montage_v1/maps/`
- `docs/records/harvest/oa_rebind_v1/o2/receipts/`
- `docs/records/harvest/oa_rebind_v1/o2/receipts/provider_item_pages/`
- `docs/records/harvest/oa_rebind_v1/receipts/aggregator-fallback/`
- `docs/records/harvest/oa_rebind_v1/receipts/bodies/`
- `docs/records/harvest/oa_rebind_v1/receipts/catalogues/`
- `docs/records/harvest/oa_rebind_v1/receipts/robots/`
- `docs/records/harvest/openarchives/acquisitions/`
- `docs/records/harvest/openarchives/assignments/`
- `docs/records/harvest/openarchives/download_attempts/`
- `docs/records/harvest/openarchives/gates/`
- `docs/records/harvest/page_reads_v1/assignments/`
- `docs/records/harvest/page_reads_v1/failure_images/`
- `docs/records/harvest/parliament/assignments/`
- `docs/records/harvest/parliament/gates/`
- `docs/records/harvest/parliament/volumes/`
- `docs/records/harvest/pilot_v1/labels/`
- `docs/records/harvest/pilots_v2/p1b/`
- `docs/records/harvest/pilots_v2/p1b/delta_blind/`
- `docs/records/harvest/pilots_v2/p1b/delta_blind/complete/`
- `docs/records/harvest/pilots_v2/p1b/delta_blind/focus/`
- `docs/records/harvest/pilots_v2/p1b/delta_keys/`
- `docs/records/harvest/pilots_v2/p1b/gutenberg/`
- `docs/records/harvest/r2a/`
- `docs/records/harvest/r2a/crops/`
- `docs/records/harvest/recut_v1/dev/`
- `docs/records/harvest/recut_v1/f2/`
- `docs/records/harvest/recut_v1/f2/gazette_modern/`
- `docs/records/harvest/recut_v1/f2/ia_greek_latin/`
- `docs/records/harvest/recut_v1/f2/kosmopolis_poly1900/`
- `docs/records/harvest/recut_v1/f2/lekythos_poly1900/`
- `docs/records/harvest/recut_v1/masking/dev/`
- `docs/records/harvest/recut_v1/masking/f2/`
- `docs/records/harvest/recut_v1/masking/f2/gazette_modern/`
- `docs/records/harvest/recut_v1/masking/f2/ia_greek_latin/`
- `docs/records/harvest/recut_v1/masking/f2/kosmopolis_poly1900/`
- `docs/records/harvest/recut_v1/masking/f2/lekythos_poly1900/`
- `docs/records/harvest/recut_v1/masking/step0/`
- `docs/records/harvest/recut_v1/v2_clariden/receipts/byte_mismatch_witness/`
- `docs/records/harvest/recut_v1/v2_full/bin/`
- `docs/records/harvest/recut_v1/v2_full/out/`
- `docs/records/harvest/recut_v1/v2_pilot/diag/sheets/`
- `docs/records/harvest/recut_v1/v2_pilot/diag/witnesses/`
- `docs/records/harvest/recut_v1/w1_masked/caps1/keys/`
- `docs/records/harvest/recut_v1/w1_masked/caps1/scan/`
- `docs/records/harvest/recut_v1/w1_masked/caps1/scan/caps1/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/keys/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/probe.Foqp/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/probe.GUqi/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/probe.UMsx/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/launchers/probe.z9ke/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/scan/`
- `docs/records/harvest/recut_v1/w1_masked/caps3/scan/caps3/`
- `docs/records/harvest/recut_v1/w1_masked/cards/gazette_modern/`
- `docs/records/harvest/recut_v1/w1_masked/cards/kosmopolis/`
- `docs/records/harvest/recut_v1/w1_masked/cards/lekythos/`
- `docs/records/harvest/recut_v1/w1_masked/cards_probe_supplement/`
- `docs/records/harvest/recut_v1/w1_masked/checks/verdicts/`
- `docs/records/harvest/recut_v1/w1_masked/gazette_modern/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/keys/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/probe.MTaN/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/probe.MVu9/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/probe.V9ja/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/probe.iVcK/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/probe.kKpm/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/launchers/probe.z3Cw/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/pack_inventory/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/scan/`
- `docs/records/harvest/recut_v1/w1_masked/kosmo2/scan/kosmo2/`
- `docs/records/harvest/recut_v1/w1_masked/kosmopolis/`
- `docs/records/harvest/recut_v1/w1_masked/lekythos/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/keys/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/probe.BrgP/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/probe.WBKb/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/probe.a6KH/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/launchers/probe.kw2i/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/pack_inventory/`
- `docs/records/harvest/recut_v1/w1_masked/ruc1/scan/ruc1/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_bsb_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_elstat_numerics_tables/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_gazette_modern_modern_scanned/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_gazette_modern_modern_scanned_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_ia_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_nlg_greek_poly/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_nlg_greek_poly_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_nlg_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_nlg_poly1900/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_nlg_poly1900_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/w2c1_serbia_cyrillic/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_bsb_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_elstat_numerics_tables/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_gazette_modern_modern_scanned/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_gazette_modern_modern_scanned_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_ia_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_nlg_greek_poly/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_nlg_greek_poly_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_nlg_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_nlg_poly1900/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_nlg_poly1900_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/pack_inventory/w2c1_serbia_cyrillic/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_bsb_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_elstat_numerics_tables/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_gazette_modern_modern_scanned/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_gazette_modern_modern_scanned_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_ia_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_nlg_greek_poly/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_nlg_greek_poly_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_nlg_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_nlg_poly1900/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_nlg_poly1900_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/receipts/w2c1_serbia_cyrillic/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_bsb_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_elstat_numerics_tables/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_gazette_modern_modern_scanned/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_gazette_modern_modern_scanned_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_ia_poly1850_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_nlg_greek_poly/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_nlg_greek_poly_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_nlg_poly1850/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_nlg_poly1900/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_nlg_poly1900_r2/`
- `docs/records/harvest/recut_v1/w1_masked/w2c1/scan/w2c1_serbia_cyrillic/`
- `docs/records/harvest/round1/reads_d1/assignments/`
- `docs/records/harvest/round1/reads_rest/assignments/`
- `docs/records/harvest/round2/assignments/`
- `docs/records/harvest/round2/gates/`
- `docs/records/harvest/round2/read_snapshots/`
- `docs/records/harvest/sample_v1/gr/google/`
- `docs/records/harvest/sample_v1/gr/label_cards/`
- `docs/records/harvest/sample_v1/gr/label_cards/anemi/`
- `docs/records/harvest/sample_v1/gr/label_cards/elstat/`
- `docs/records/harvest/sample_v1/gr/label_cards/government-gazette/`
- `docs/records/harvest/sample_v1/gr/label_cards/kosmopolis/`
- `docs/records/harvest/sample_v1/gr/label_cards/lekythos/`
- `docs/records/harvest/sample_v1/gr/label_cards/nlg-digital/`
- `docs/records/harvest/sample_v1/gr/label_cards/openarchives/`
- `docs/records/harvest/sample_v1/gr/label_cards/pergamos/`
- `docs/records/harvest/sample_v1/gr/label_cards/pleias/`
- `docs/records/harvest/sample_v1/gr/receipts/`
- `docs/records/harvest/sample_v1/gr/receipts/analysis/`
- `docs/records/harvest/sample_v1/gr/receipts/ephemeral-crops/`
- `docs/records/harvest/sample_v1/gr/receipts/items/`
- `docs/records/harvest/sample_v1/gr/receipts/local-review-selection/`
- `docs/records/harvest/sample_v1/gr/receipts/machine/`
- `docs/records/harvest/sample_v1/gr/receipts/metadata/`
- `docs/records/harvest/sample_v1/gr/receipts/pages/`
- `docs/records/harvest/sample_v1/gr/receipts/reads/`
- `docs/records/harvest/sample_v1/gr/receipts/robots/`
- `docs/records/harvest/sample_v1/gr/receipts/superseded-elstat-book-only/`
- `docs/records/harvest/sample_v1/gr/receipts/superseded-ojs-galley-scope/`
- `docs/records/harvest/sample_v1/gr/receipts/verify-items/`
- `docs/records/harvest/sample_v1/gr/receipts/verify-pages/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-secondary/artifacts/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-secondary/artifacts/n1/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-secondary/artifacts/ru1/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/codec/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/annotate/fixtures/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-spellcheck/artifacts/`
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/`
- `docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/qa/`
- `docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/qa/word-tolerance/`
- `docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/review-data/`
- `docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/review-data/font-normalized/`
- `docs/records/harvest/seg_census/source_capture/docs/harvest/line_pipeline/clariden/inventory/`
- `docs/records/harvest/seg_steps/s1/baseline/docs/`
- `docs/records/harvest/seg_steps/s1/baseline/docs/harvest/`
- `docs/records/harvest/seg_steps/s1/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/seg_steps/s1/overlays/`
- `docs/records/harvest/seg_steps/s2/baseline/docs/`
- `docs/records/harvest/seg_steps/s2/baseline/docs/harvest/`
- `docs/records/harvest/seg_steps/s2/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/seg_steps/s2/census_crops/`
- `docs/records/harvest/seg_steps/s2/near_square/`
- `docs/records/harvest/seg_steps/s2/overlays/`
- `docs/records/harvest/seg_steps/s3/baseline/docs/`
- `docs/records/harvest/seg_steps/s3/baseline/docs/harvest/`
- `docs/records/harvest/seg_steps/s3/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/seg_steps/s3/overlays/`
- `docs/records/harvest/seg_steps/s4/baseline/docs/`
- `docs/records/harvest/seg_steps/s4/baseline/docs/harvest/`
- `docs/records/harvest/seg_steps/s4/baseline/docs/harvest/line_pipeline/`
- `docs/records/harvest/sol_reading/grave/keys/synthetic/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/answers/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p1c2/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p1c3/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p1c4/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p2a/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p2b/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p2c3/`
- `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p2c4/`
- `docs/records/harvest/sol_reading/tools/fixtures_v45/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-2ld40jkd/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-2ld40jkd/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-2ld40jkd/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-335uomjg/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-335uomjg/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-6_4abl52/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-6_4abl52/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-6b0yu4oi/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-6b0yu4oi/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-6b0yu4oi/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-6b0yu4oi/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-84up3o4a/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-84up3o4a/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8911llnu/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8911llnu/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8911llnu/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8911llnu/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8o041fnm/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8o041fnm/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8o041fnm/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8o041fnm/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8q5l5h1d/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8q5l5h1d/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-8q5l5h1d/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-9nwz3kz6/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-9nwz3kz6/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-9nwz3kz6/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-abt9va47/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-abt9va47/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-acd5aych/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-acd5aych/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-acd5aych/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-bme1ymjd/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-bme1ymjd/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-bme1ymjd/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-bme1ymjd/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-c21msepq/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-c21msepq/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-c21msepq/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-d7pjn9ax/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-d7pjn9ax/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-epbryhpa/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-epbryhpa/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-epbryhpa/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-epbryhpa/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-f5ipdxac/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-f5ipdxac/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-f5ipdxac/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-f5ipdxac/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-fz4wf2th/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-fz4wf2th/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-g31pl0nz/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-g31pl0nz/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-g31pl0nz/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-g31pl0nz/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-gq62xpct/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-gq62xpct/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-gq62xpct/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-gq62xpct/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-h66g1w7y/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-h66g1w7y/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-h66g1w7y/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-hp9yeq3k/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-hp9yeq3k/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-hp9yeq3k/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-hxjcu13a/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-hxjcu13a/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-itn3vsu7/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-itn3vsu7/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-itn3vsu7/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-l5s9p212/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-l5s9p212/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-lr5e7xfh/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-lr5e7xfh/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-lr5e7xfh/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-lr5e7xfh/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-mhr1r5uw/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-mhr1r5uw/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-nrlsp9yc/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-nrlsp9yc/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-p4j2tr0q/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-p4j2tr0q/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-p4j2tr0q/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-p4j2tr0q/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-qt6lkhwi/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-qt6lkhwi/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-r552hph2/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-r552hph2/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-r83f7hd5/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-r83f7hd5/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-r83f7hd5/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-r83f7hd5/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rbhs2hdc/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rbhs2hdc/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rbhs2hdc/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rga3cdbu/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rga3cdbu/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rga3cdbu/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rj5_l91t/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rj5_l91t/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rj5_l91t/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-rj5_l91t/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s39k1c4p/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s39k1c4p/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s39k1c4p/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s39k1c4p/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s5umxfyl/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s5umxfyl/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s5umxfyl/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-s5umxfyl/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-u1n3hyq0/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-u1n3hyq0/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-u1n3hyq0/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-u1n3hyq0/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-vgs9ycaw/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-vgs9ycaw/packs/bsb/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-vgs9ycaw/packs/bsb/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-vgs9ycaw/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-x20_05sx/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-x20_05sx/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-yebcdx5k/keys/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-yebcdx5k/packs/yer/r1/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-yebcdx5k/packs/yer/r3/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-yebcdx5k/validation/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-ytlwlqo1/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-ytlwlqo1/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-zwd1w7z2/answers/`
- `docs/records/harvest/sol_reading/validation/SYNTHETIC-B2-zwd1w7z2/answers/bsb/`
- `docs/records/harvest/sol_reading/validation/sr-b1-05_q_72d/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-171qskfr/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-1neomgnk/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-30rubb0c/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-3h3mubgc/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-4bb2cpk1/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-4w7m9agg/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-6gr6wlms/`
- `docs/records/harvest/sol_reading/validation/sr-b1-6n3otpg1/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-6n3otpg1/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-6s2baehy/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-6tcqynfs/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-70zdusi8/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-7c_kq3ko/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-7c_kq3ko/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-7lvm73qq/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-7lvm73qq/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-9e7vqw7c/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-_9b46sma/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-_9b46sma/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-_jb_6cju/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-_mam6sr4/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-aupvo8mi/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-b6mciza2/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-bbxtsr5q/`
- `docs/records/harvest/sol_reading/validation/sr-b1-bihxt2gg/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-cia50t8s/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-e1fatkbj/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-e2oe_2ve/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-eb1jdz8_/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-efgdreq4/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-f49ke_0p/`
- `docs/records/harvest/sol_reading/validation/sr-b1-g3603kcs/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-gtb7a137/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-h2shx339/`
- `docs/records/harvest/sol_reading/validation/sr-b1-hf0d8a0e/`
- `docs/records/harvest/sol_reading/validation/sr-b1-hgbilxxj/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-igntazbr/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-igntazbr/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-j9a9pa7h/`
- `docs/records/harvest/sol_reading/validation/sr-b1-jxvzzl29/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-k787g21a/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-lljz5qis/`
- `docs/records/harvest/sol_reading/validation/sr-b1-m4zk9frv/`
- `docs/records/harvest/sol_reading/validation/sr-b1-m9w9ejl_/`
- `docs/records/harvest/sol_reading/validation/sr-b1-p8e0nze2/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-pqtnu1_5/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-q2eky4j8/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-qsd3hgsd/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-r90r8ybk/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-reyx3mo8/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-rlrhmrnb/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-rrb6xxay/`
- `docs/records/harvest/sol_reading/validation/sr-b1-s0e475vb/`
- `docs/records/harvest/sol_reading/validation/sr-b1-supww3j2/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-trag8yxu/`
- `docs/records/harvest/sol_reading/validation/sr-b1-tswurty_/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-tswurty_/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-ub5kpc1f/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-ub5kpc1f/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-uiiqtkrc/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-uxg5sgap/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-uxg5sgap/r1/zoom/`
- `docs/records/harvest/sol_reading/validation/sr-b1-vsj1a0xa/`
- `docs/records/harvest/sol_reading/validation/sr-b1-vt8ss9vb/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-w2qz2qb6/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-wjmocfmv/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-xcpegfhq/`
- `docs/records/harvest/sol_reading/validation/sr-b1-xrg81zqe/`
- `docs/records/harvest/sol_reading/validation/sr-b1-y6gedmoy/`
- `docs/records/harvest/sol_reading/validation/sr-b1-zdagj7xa/r1/`
- `docs/records/harvest/sol_reading/validation/sr-b1-zswxq6a4/r1/`
- `docs/records/harvest/sol_reading/validation/synthetic/`
- `docs/records/harvest/sol_reading/validation/synthetic/bsb/`
- `docs/records/harvest/sol_reading/validation/synthetic/owner39/`
- `docs/records/harvest/sol_reading/validation/synthetic/yer/`
- `docs/records/harvest/transkribus_failed_lines/default_layout/attempts/`
- `docs/records/harvest/transkribus_failed_lines/default_layout/responses/`
- `docs/records/harvest/transkribus_failed_lines/empty_line_detection/attempts/`
- `docs/records/harvest/transkribus_failed_lines/empty_line_detection/responses/`
- `docs/records/harvest/transkribus_failed_lines/error_receipts/`
- `docs/records/harvest/transkribus_failed_lines/omitted_layout/attempts/`
- `docs/records/harvest/transkribus_failed_lines/omitted_layout/responses/`
- `docs/records/harvest/transkribus_failed_lines/prior_attempts/`
- `docs/records/harvest/transkribus_failed_lines/single_line/`
- `docs/records/harvest/transkribus_failed_lines/unassigned_processes/`
- `docs/records/harvest/vouli/assignments/`
- `docs/records/harvest/vouli/gates/`
- `docs/records/harvest/vouli/logs/`
- `docs/records/harvest/wikisource/assignments/`
- `docs/records/harvest/wikisource/cleaned_transcriptions/`
- `docs/records/harvest/wikisource/gates/`
- `docs/records/harvest/wikisource/image_attempts/`
- `docs/records/harvest/wikisource/image_resolution/`
- `docs/records/harvest/wikisource/transcriptions/`
- `docs/records/harvest/wikisource_r0/assignments/`
- `docs/records/harvest/wikisource_r0/provisional/`
- `docs/records/harvest/wikisource_r0/qa/`
- `docs/records/harvest/wikisource_r0/wikitext/`
- `docs/records/labelfix/decisions/`
- `docs/records/labelfix/lexicons/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_conflicting_inline_f0/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_explicit_missing_fla0/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_invalid_flags_fail_c0/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_invalid_flags_fail_c1/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_invalid_flags_fail_c2/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_invalid_flags_fail_c3/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_invalid_flags_fail_c4/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_lqb2_run_autoloads_flags_0/`
- `docs/records/labelfix/lqb/validation/lqb2/pytest_tmp/test_overlay_and_admission_pop0/`
- `docs/records/labelfix/lqb/validation/lqb3/frozen/validation/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_conflicting_inline_f0/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_explicit_missing_fla0/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_invalid_flags_fail_c0/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_invalid_flags_fail_c1/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_invalid_flags_fail_c2/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_invalid_flags_fail_c3/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_invalid_flags_fail_c4/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_lqb2_run_autoloads_flags_0/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_overlay_and_admission_pop0/`
- `docs/records/labelfix/lqb/validation/lqb3/pytest_tmp/test_supplemental_google_hash_0/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_conflicting_inline_f0/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_explicit_missing_fla0/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_invalid_flags_fail_c0/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_invalid_flags_fail_c1/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_invalid_flags_fail_c2/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_invalid_flags_fail_c3/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_invalid_flags_fail_c4/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_lqb2_run_autoloads_flags_0/`
- `docs/records/labelfix/lqb/validation/lqb4/pytest_tmp/test_overlay_and_admission_pop0/`
- `docs/records/labelfix/lqb/validation/pytest_tmp/test_overlay_and_admission_pop0/`
- `docs/records/labelfix/review_deck/cards/`
- `docs/records/labelfix/review_deck/cards/accent/`
- `docs/records/labelfix/review_deck/cards/accent_2/`
- `docs/records/labelfix/review_deck/cards/base_sub/`
- `docs/records/labelfix/review_deck/cards/base_sub_2/`
- `docs/records/labelfix/review_deck/cards/breathing/`
- `docs/records/labelfix/review_deck/cards/constraint/`
- `docs/records/labelfix/review_deck/cards/final_grave/`
- `docs/records/labelfix/review_deck/cards/final_grave_2/`
- `docs/records/labelfix/review_deck/cards/final_sigma/`
- `docs/records/labelfix/review_deck/cards/ink_decisive/`
- `docs/records/labelfix/review_deck/cards/marks_multi/`
- `docs/records/labelfix/review_deck/cards/subscript/`
- `docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/`
- `docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/`
- `docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/`
- `docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/`
- `docs/records/labelfix/spellcheck/L1M_evidence/panels/`
- `docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/`
- `docs/records/labelfix/spellcheck/R0_adjudication_private/`
- `docs/records/labelfix/spellcheck/R0_adjudication_private/ia/`
- `docs/records/labelfix/spellcheck/R0_adjudication_private/ib/`
- `docs/records/labelfix/spellcheck/R0_adjudication_private/readers/`
- `docs/records/labelfix/spellcheck/R0_adjudication_private/readers_ib/`
- `docs/records/labelfix/spellcheck/R0_cards/img/`
- `docs/records/labelfix/spellcheck/R0_cards_ia/img/`
- `docs/records/labelfix/spellcheck/R0_cards_ib/img/`
- `docs/records/labelfix/spellcheck/R2/evidence/tranche6/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit/img/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit100/img/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit100_private/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit100_private/readers/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit100_private/tiebreak/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit_private/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit_private/readers/`
- `docs/records/labelfix/spellcheck/S8_DEV/audit_private/tiebreak/`
- `docs/records/labelfix/spellcheck/S8_DEV/cards/img/`
- `docs/records/labelfix/spellcheck/S8_DEV/cards_private/`
- `docs/records/labelfix/spellcheck/S8_DEV/cards_private/readers/`
- `docs/records/labelfix/spellcheck/S8_DEV/cards_private/tiebreak/`
- `docs/records/labelfix/spellcheck/S8_DEV/evidence/baseline/`
- `docs/records/labelfix/spellcheck/S8_DEV/evidence/baseline/original/`
- `docs/records/labelfix/spellcheck/S8_DEV/masked/baseline/`
- `docs/records/labelfix/spellcheck/S8_DEV/masked/baseline/masked/`
- `docs/records/labelfix/spellcheck/S8_DEV/private/audit/`
- `docs/records/labelfix/spellcheck/S8_DEV/private/cards/`
- `docs/records/labelfix/spellcheck/S8_DEV/s8b/dev_detector/`
- `docs/records/labelfix/spellcheck/S8_DEV/s8b/regression_detector/`
- `docs/records/labelfix/spellcheck/SF1_evidence/`
- `docs/records/labelfix/spellcheck/SF6_evidence_aborted_run1/`
- `docs/records/labelfix/spellcheck/clariden/C1_inventory/`
- `docs/records/labelfix/spellcheck/clariden/C1_job_metadata/`
- `docs/records/labelfix/spellcheck/clariden/L1E_evidence/remote_readback/heldout_final/`
- `docs/records/labelfix/spellcheck/clariden/L1E_evidence/remote_readback/heldout_final/mock/`
- `docs/records/labelfix/spellcheck/clariden/L1F_evidence/remote_readback/preflight/`
- `docs/records/labelfix/spellcheck/clariden/L1F_evidence/remote_readback/preflight/verified_inputs/`
- `docs/records/labelfix/spellcheck/clariden/L1R2_evidence/production_3680629_3680630/release/`
- `docs/records/labelfix/spellcheck/clariden/L1R2_evidence/remote_readback/config/`
- `docs/records/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/release/release/`
- `docs/records/labelfix/spellcheck/clariden/L1R3_evidence/remote_l1r3b/verified/preflight/`
- `docs/records/labelfix/spellcheck/clariden/L1R4_evidence/remote/verified/preflight/`
- `docs/records/labelfix/spellcheck/clariden/L1R4_evidence/upstream/l1r_sf6/census/output_3680729_3680730/changes/`
- `docs/records/labelfix/spellcheck/clariden/L1R_evidence/mock/release/`
- `docs/records/labelfix/spellcheck/clariden/L1R_evidence/mock/shards/shard-00000/release/`
- `docs/records/labelfix/spellcheck/clariden/L1R_evidence/remote_readback/config/`
- `docs/records/labelfix/spellcheck/crops_S2/`
- `docs/records/labelfix/spellcheck/regression/`
- `docs/records/labelfix/spellcheck/sheets/`
- `docs/owner_sheets/failure_modes_per_class/`
- `docs/owner_sheets/segmentation_failures/`
- `docs/B_training_data/d_review/demo/`
- `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/recomposed_mock64/release/`
- `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v_evidence/notes_binding_fixture/`
- `docs/records/reviews/harness/merge_logs/`
- `docs/records/reviews/harness/sync_logs/`
- `docs/records/reviews/q1b-evidence/`
- `docs/records/tables/`
- `docs/records/tables/annotations/`
- `tests/data/docai_failed_lines/crops/`
- `tests/fixtures/borndigital100/crops/`
- `tests/fixtures/o4c/review_pages/`
- `tests/fixtures/polytondb_gold300/imported_gold/`
- `tests/fixtures/polytondb_gold300/imported_gold/crops/`

There are 1,491 such directories, covered by 755 maximal empty subtrees. No directory is removed by this run.

## Proposed guard and ignore rules

`size_guard_test.py` is a proposed pytest, not installed into `tests/`. It reads `git ls-files -z`, measures regular files and stored symlink target text, fails on unavailable tracked paths, and rejects sizes strictly greater than 5,000,000 bytes. It neither reads artifact contents nor writes git. Its callable was checked on this unmodified inventory and failed as expected with exactly 232 oversized paths; no test was installed and no artifact was changed. It intentionally does not prove receipt completeness, validate historical blob size, or prevent force-add; review staged content separately at execution time.

Append `.gitignore.proposed` only in the later approved move change. Its 9,034 anchored rules cover every MOVE path and no retained/ASK HEAD path: whole directories only when every current descendant moves, exact paths otherwise. This protects mixed source/receipt directories and avoids global *.jsonl/*.png/*.html exclusions that would hide legitimate source/test fixtures. Git ignore rules do not affect already tracked paths; relocation/untracking must precede enforcement. Git can override ignore with force-add; the guard supplies the tracked-size backstop. Future ≤5 MB artifact names in mixed directories still require review, rather than a broad unreviewed ignore.

## Future execution gates — not performed here

1. Resolve ASK paths and the small evidence/test fixture exceptions; approve the exact MOVE path list and consumer fixes.
2. Confirm GREEK_OCR_DATA_ROOT points to the designated external root, and check available capacity (no assumption about cross-volume renames or immediate freed bytes).
3. Copy each artifact without overwrite; verify destination bytes and SHA256 against this plan, reconcile lead-only custody items without claiming new transfers, and retain a receipt in git with original path, destination, bytes, SHA256, producing commit, readers and copy verification.
4. Exercise the resolver and affected offline tests, historical guard adapters, deploy/package readers and sheet assets against the external copies. Preserve SEGEVAL1.bundle independently of history.
5. Only after coordinator/owner path-list approval, perform the separately authorized source removals/untracking, append ignores, and install the guard. Never rewrite history. Keep rollback/retrieval receipts; do not regenerate or discard frozen benchmark truths.

The full TSV is deliberately exhaustive and may itself exceed 5 MB. This analysis artifact must stay untracked until it is split into ≤5 MB receipt shards or compressed below the limit, with an index/hash receipt retained. Applying the new guard while force-adding an oversized plan would violate the owner rule. This run does not add any planning output to git.

Validation: `VALIDATION.json` records complete HEAD coverage, verified snapshot hashes/sizes, exact path-log producing commits, unchanged HEAD/index IDs and tracked-file lstat metadata, complete MOVE-only ignore coverage, seven independent basename-grep spotchecks, and the proposed guard’s expected 232-path failure. Other cleanup drafts appeared during the shared-workspace run; `READER_REFRESH.json` records the read-only refresh of those untracked text references. No move, source edit, or git-writing command was performed.
