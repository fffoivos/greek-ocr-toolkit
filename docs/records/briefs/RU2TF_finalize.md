# RU2T-F: finalise ru1_v2_train (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The RU2T readings are done: ctx01 r1/r2, ctx02 r1 + r3 (r2 VOID), ctx03 r1 + r3 (r2 VOID). If an r3 scan fails, stop. Run `scripts/secondary/ru2t_finalize.sh` (RU2T-0/0b): scan check with canonical
v4.4, mapping, control gates, the combiner with the ru1 edit rule, `artifacts/ru1/ru1_v2_train.jsonl`, the per-row decision counts,
the manifest and sha, and the LQB registration `ru1_v2_train`.
- If any accepted reader-context fails its scan or gate, stop and report. Never widen anything.
- **Lead_review positions** (disagreement, u/other, single valid read): build a shape-comparison sheet as in RU1-L, with same-book
  ъ/ь references left and right, in the scratchpad `ru1_review/ru2t/`. Write a template. Those rows stay HOLD in ru1_v2_train until
  the lead rules.
- **Audit sheet:** 20 seeded edit_hard + 10 keep_soft cells, in the same layout.
- **LQB:** re-score with ru1_v2_train registered, and write the delta lines into `docs/records/labelfix/lqb/SCORE_v2.md` (v2.3).

**Last line:** `RU2TF READY: rows <n> (ok <n>, hold <n>); edits <n>; keep <n>; lead_review <n>; ru1_v2_train sha256 <hex>; LQB registered <ok>; review cells <n>, audit cells 30`
