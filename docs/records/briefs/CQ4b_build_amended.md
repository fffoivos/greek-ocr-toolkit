# CQ4b: resume the CQ4 build under preregistration amendment 1 (gpt-6.1-sol, medium, network OFF; no .git writes). BUILD ONLY.

Read `docs/records/briefs/CQ4_capitals_witness_and_topup_build.md` (the base spec) and your CQ4 outputs (`docs/records/labelfix/spellcheck/R2/CQ4_REPORT.md`,
`artifacts/cq4/`). CQ4 stopped correctly at the inventory gate: only 3 never-used documents, so at most 90 W-CAP slots.

**Amendment 1** (`~/Projects/greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/R2A2_PREREGISTRATION.md`, now sha256
dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc; record it in the receipt):
1. **W-CAP documents** = the 17 **validation-role** documents (`docs/records/labelfix/spellcheck/R2/doc_roles.json`) plus the 3 never-used
   documents. Calibration-role documents stay excluded. Remove validation docs from the excluded set FOR W-CAP ONLY; they remain excluded
   from the top-up.
2. **Scanner:** the canonical v4.4, copied BY HASH from
   `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`.
   - Verify sha256 = `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547` before and after the copy.
   - No local fork. Remove the cq1 v4.3 wrapper from CQ4's run path.
   - Record the sha in every receipt.
   - As a regression check, re-scan the CQ1 rollouts with it: r1 must be VOID (record 24) and r1b clean.

Then continue the CQ4 spec from §1 (the inventory gate at 70%, so ≥ 210 W-CAP slots) through §4: selection, packs, the 40-control pool
sheet, RUN_ALL / BUILD_REREAD / AGGREGATE, and tests. If the gate fails again, STOP and report the counts per document.

Last line: `CQ4b BUILD READY: W-CAP docs <n> slots <n> (marked-likely <n>/bare-likely <n>); top-up docs <n> slots <n>; contexts <n>; controls pool 40 (sheet <path>); scanner v4.4 sha ok; CQ1 rescan r1 VOID / r1b clean; est. Codex <pts>`.
