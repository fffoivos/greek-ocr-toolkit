# RU3T-F4: final ru1_v3_train (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

Apply `docs/records/labelfix/secondary/RU3T_LEAD_AUDIT.md`:
- audit cell 293 → hold_uncertain;
- the other audit cells → lead_audit_confirmed;
- every lead_review position → hold (reason kept).

Run the finaliser's write step: `artifacts/ru1/ru1_v3_train.jsonl` (parent = the v2 train label; it includes the RU2T decisions),
the manifest and sha, LQB registration of `ru1_v3_train` and a re-score. Report the counts.

**Last line:** `RU3TF4 READY: ru1_v3_train rows <n> (ok <n>, hold <n>); edits <n>; sha256 <hex>; LQB registered <ok>`
