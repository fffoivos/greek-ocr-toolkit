# N1-CAL2S: fix calibration-v2 output paths and dash-type scoring (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree and constraints as N1-Tb. The lead ran `run_n1.sh n1cal2 cal01 r1` (17:05–17:08). Two problems:
1. Its outputs went to `artifacts/n1/answers/cal01.r1.*`, the same names as the first calibration (`n1cal`, sep.md), which they
   probably overwrote. The first calibration's files are committed at `1a779e810` (`git show 1a779e810:<path>` is read-only and
   allowed).
2. The calibration score still reports the old class "hyphen or dash", so dash types were not scored.

**Do.**
1. **Establish** which run each current `cal01.r1.*` file belongs to: compare against the run json, the rollout id and the pack
   keys. Restore the first calibration's files from `1a779e810` into `artifacts/n1/answers/n1cal/` and move the v2 files into
   `artifacts/n1/answers/n1cal2/`, by copy, keeping the originals. Record everything in the receipt.
2. **Fix** `run_n1.sh` and the mapper so that every root writes under `artifacts/n1/answers/<root>/`. Run a dry-run test for
   `n1cal`, `n1cal2` and `n1t2`. Never let two roots share a file name.
3. **Re-score** calibration v2 from its raw answers against `approved.jsonl` plus `dash_types.jsonl`:
   - per-class accuracy with hyphen, en dash and em dash separate (the 2 "unsure" cells accept any dash type);
   - a confusion matrix;
   - the disagreement list.
4. **Gate** (lead ruling) — **PASS** needs all of:
   - raised dot 4/4;
   - no non-raised control answered as raised dot;
   - dash type correct on at least 23 of the 25 typed dash controls;
   - at most 3 disagreements overall.

   Otherwise HOLD, with a contact sheet of the disagreements in the scratchpad `n1_review/cal2_disagreements.png`.
5. Write the receipt `artifacts/n1/N1CAL2S_RECEIPT.json` and a section in `N1T_REPORT.md`. Run the tests.

**Last line:** `N1CAL2S <PASS|HOLD>: raised <n>/4; baseline <n>/21; comma <n>/23; hyphen <n>/14; en <n>/6; em <n>/5; unsure-dash <n>/2; nothing <n>/7; disagreements <n>; paths fixed <ok>`
