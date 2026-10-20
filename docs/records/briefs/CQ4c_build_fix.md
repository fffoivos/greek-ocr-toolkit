# CQ4c: fix two errors in the lead's CQ4 spec, then finish the build (gpt-6.1-sol, medium, network OFF; no .git writes). BUILD ONLY.

CQ4b stopped correctly: the top-up had 3 documents (upper bound 360 < 844 slots), and the W-CAP located slots were unknown. Both come
from the lead's spec. The owner has now given GO for R2a-2 once these inputs exist, so finish the build tonight.

**Fix 1: top-up documents.** CQ4's exclusion union wrongly removed every T2 / supervision-role document from the TOP-UP. The top-up is
TRAINING data, so supervision-role documents are its natural source.
- The top-up may use supervision-role documents.
- It excludes: the slots already on T2 cards, every R2a v2 manifest slot, and every document in W-CAP, T4, validation, calibration, the
  old-pool held-out 16, DEV, the LQB truth sets and CQ1.
- The old pool's 316 training documents are allowed for the top-up (training-on-training is fine). Their R1 targets get REPLACED when a
  top-up slot hits an old identity: replace, never append; an overlay hitting a duplicated old key means STOP, as in R2J4.

**Fix 2: W-CAP slot location.** Locate the capitals on validation-role lines from the saved recogniser alignments and teacher exports of
R2 job 3681404, in the validation_reserve role. They are read back and sha-verified at
`~/Projects/greek-ocr-toolkit-spellcheck-r2prep/artifacts/labelfix_r2/output_3681404/` (B stage, alignments plus teacher export), plus the
R2P2 population and crops. The same goes for the 3 unused documents, if their alignments exist; otherwise drop them and say so.

Everything else is as CQ4/CQ4b specify:
- preregistration sha dbac559f… (amendment 1);
- canonical scanner v4.4 by hash;
- the 40-control pool sheet;
- RUN_ALL / BUILD_REREAD / AGGREGATE;
- the 70% inventory gate.

Last line: `CQ4c BUILD READY: W-CAP docs <n> slots <n> (marked-likely <n>/bare-likely <n>); top-up docs <n> slots <n>; contexts <n>; controls pool 40 (sheet <path>); est. Codex <pts>`.
