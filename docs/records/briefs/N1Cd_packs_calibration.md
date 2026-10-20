# N1-Cd: seal approved controls, build calibration + glyph-pass packs, N1 launcher (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue N1-Cc (`docs/records/labelfix/secondary/N1C_REPORT.md` § N1-Cc). Same worktree, constraints, interpreters and allowed writes.

**Lead rulings (17 Oct).**
1. **C1 document conflict.** The four C1 raised-dot controls are ALLOWED. Their lines are disjoint from every step1 line and from the
   reserved set, and they are C1 evidence lines that N1 never fits on. The document-level exclusion was meant to keep controls from
   resembling bed items, not to protect truth. Record this ruling in the approved file's provenance.
2. **The two N1-Cc raised candidates (cells 101, 102) are NOT raised dots.** 101 is a spaced hyphen (a duplicate of cell 58); 102 is
   a baseline dot under a dotted leader. Neither becomes a control.
3. **Raised-dot coverage.** There are 4 raised-dot control slots. Every bed context must contain at least 1. They may repeat across
   contexts, never within one.

**Do.**
1. **Seal** `artifacts/n1/controls/approved.jsonl` from `n1cc_approved_proposed.jsonl` (82 rows) with the provenance above, plus a
   sha256 in the receipt.
2. **Calibration pack.** Run `n1_build_packs.py --calibration` with all 82 approved controls in one context, seeded order. Use the
   v3 (marker) zooms.
   - Output root: `PACK_ROOT_CAL=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1cal/cal01/r1/`.
   - Keys: `artifacts/n1/keys/cal01.json`.
   - Run closure.
3. **Glyph-pass packs.** The 558 rendered step1 slots plus controls go to
   `PACK_ROOT=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1/ctxNN/r1/`.
   - Contexts of ≤100 items: ≈80 bed + ≈9 controls each, so 7 contexts, with ≥1 raised-dot control in each and the other controls
     round-robin by class.
   - Seed `20261017:N1-1`. Use the v3 zooms. Run closure on every context.
4. **Launcher** `scripts/secondary/reading/run_n1.sh <root:n1|n1cal> <ctx> [reader]`, modelled on the RU1 `run_bed.sh`:
   - limit probe before and after; refuse at ≥78%;
   - `run_read.sh` with the prompt `docs/records/labelfix/secondary/prompts/sep.md`;
   - leak scan with `scan_rollout.py` v4 against the pack folder;
   - mapping with `n1_map_answers.py`;
   - ledger at `artifacts/n1/usage_ledger.json`;
   - answers to `artifacts/n1/answers/<ctx>.<reader>.*`.

   Calibration scoring: per-class accuracy against the approved truths, a confusion matrix, and the list of disagreements with slot
   ids. Syntax-check it and add a dry-run test with a fake `run_read.sh`. Do NOT invoke the real launcher.
5. **Receipt and report.** Write the receipt `artifacts/n1/N1Cd_RECEIPT.json`, an "N1-Cd" section in `N1C_REPORT.md` (context table
   with bed/control counts per class), and run the tests.

**Last line:** `N1Cd READY: approved 82 sealed <sha8>; calibration ctx 1 (<n> items); bed contexts <n> (bed <n>, controls <n>, raised ≥1 each <yes|no>); closure <n>/<n> ok; launcher dry-run <ok>; tests <n> passed`
