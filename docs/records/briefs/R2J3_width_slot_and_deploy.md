# R2J3: resolve the width-gated slot, then deploy R2a + DEV (gpt-6.1-sol, medium; network ON for the deploy/sha/test-only steps only; no .git writes; NEVER submit)

R2J2 stopped correctly: 1 of the 1,573 overlay slots fails the frozen R1 extractor's width gate. The slot is crop
`82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8`, NFD start 46, line `ia_poly1850--3773a91327e98bc0--s001-l0005`,
`width_outside_0.2_2.0_median_ctc`.

**Lead ruling:** the frozen extractor gate stands, with no exception path. Drop that slot from the overlay.
- Write a corrected manifest `artifacts/r2a_manifest/r2a_slots_v2.jsonl` (1,572 slots; the dropped slot goes into `quarantined` with
  reason `frozen_extractor_width_gate`). Keep the v1 file unchanged.
- Record both shas.
- Update every count: 1,149 or 1,150 negative depending on the slot's role; state which. Update the recipe table (+1,572 identities)
  and the receipt/report.
- The report and receipt also state the coordinator-accepted deviation: "R2a admits 1,572 print-checked slots against the plan's
  4,000; per-slice deficits recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)". The readback template
  (`r2_readback_verify.py` / report) must carry the same sentence.

Then:
1. Re-run the mock and tests. Rebuild `R2A_DEPLOY_FILES.txt` / `R2A_DEPLOY_SHA256.txt` and `LEAD_COMMIT_PATHS.txt`.
2. **STOP with "LEAD COMMIT NEEDED"** if the verifier requires committed files. Check this BEFORE deploying: the lead commits
   `LEAD_COMMIT_PATHS.txt` right after you finish.
   - So do deploy + remote sha + `sbatch --test-only` (cert valid until 19:18 Athens; an auth error means STOP, never refresh) BEFORE
     stopping. Remote sha is computed on files that are identical to what the lead will commit; the verifier then runs after the
     commit.
   - Write the exact verifier command to `docs/records/labelfix/spellcheck/R2/evidence/r2a/VERIFY_CMD.sh` so the lead can run it verbatim.

Last line: `R2J3 READY: slots 1572 (neg <n>/pos <n>); manifest v2 sha <12>; mock pass; tests <n>; deployed <n> files sha match <n>/<n>; test-only <ok|fail>; lead commit list <path>; verify cmd <path>`.
