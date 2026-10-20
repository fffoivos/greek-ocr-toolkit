# SEGEVAL-2 handoff

Both SEGEVAL-1 contexts rescan VALID under canonical v4.5.5, hash verified against the canonical HANDOVER.md. Zero violations; no manifests skipped. No new reads or network access. No fresh-ID repack is needed.

The final result is FP 29/50 (58%), OCR-length reasons 27/43 (62.79%), FN 5/100 (5%); reader-unresolved REJECT 2 and ACCEPT 1. Controls pass 10/10. Rubric FN: horizontal clipping 4, whole neighbour word 1, multiple complete lines 0, orientation 0. Counts are unchanged from v4.4. No owner proceed threshold or acceptance decision is invented.

Review `SEGEVAL1_RESULT.md`, `scored/summary.json`, and `scored/owner_rows.jsonl`. Original v4.4 scans remain in `scan/segeval1_{a,b}` and original scores in `scored/v4.4`; new scans and full custody are in `scan/v4.5.5`, with comparison in `scan/verdicts.json`. No intermediate v4.5.x verdict is inferred without a receipt.

Reproduction: `tools/segeval2_rescan.py` audits existing files only; `segeval1_score.py` now gates on the pinned v4.5.5 custody before scoring. Eight scoring tests pass; `segeval2_verification.json` records artifact checks. `SEGEVAL2.bundle` is a standalone Git artifact bundle of this task's scoring/custody/report evidence, with commit, SHA256, file inventory and verification in `segeval2_package_receipt.json`. Existing crops, public packs and raw rollouts remain at their original paths; their hashes are bound by custody. Shared Git state and unrelated worktree changes are left untouched.

SEGEVAL2: done | scans: a VALID b VALID | FP 29/50 (length rules 27/43) | FN 5/100 | commit bundle
