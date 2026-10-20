# RU2T-F4: apply lead rulings, final ru1_v2_train (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

Apply `docs/records/labelfix/secondary/RU2T_LEAD_REVIEW.md` to `artifacts/ru1/ru1_v2_train.jsonl`. Review cell → position mapping is in
the scratchpad `ru1_review/ru2t/sheets_index.json`.
- Cells 3, 5 and 6 → edit_hard (basis `lead_ruling`).
- Cell 1 → keep_soft.
- Cells 2 and 4 stay hold, with reasons `hold_yat` and `hold_uncertain`.
- Record the audit as `lead_audit_confirmed`.

Rebuild the file, manifest and sha. Update the LQB `versions.json` entry and re-score (`SCORE_v2.md` v2.4). Run the tests.

**Last line:** `RU2TF4 READY: ru1_v2_train rows <n> (ok <n>, hold <n>); edits <n> (two_reads <n>, lead <n>); sha256 <hex>; LQB re-scored <ok>`
