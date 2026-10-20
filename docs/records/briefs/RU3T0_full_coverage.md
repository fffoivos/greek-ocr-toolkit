# RU3T-0: full coverage of the v2-train Cyrillic candidates — packs + 70%-stop driver (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The coordinator approved full coverage: all 1,831 candidate lines in the 9 books (RU2T-0 census). The 200 lines already read in
RU2T keep their final decisions (`ru1_v2_train.jsonl`, sha b47c113f…). Read the remaining ≈1,631 lines.

**Do.**
1. **Packs** for the remaining candidate lines, exactly as RU2T:
   - the RU1 yer layout, r1 + r2 (exact reverse, fresh ids), ≤100 items per context, about 10% controls from the 65 adjudicated
     positions;
   - pack root `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru3t/`
     (the in-repo guard must pass);
   - keys in `artifacts/ru1/ru3t/`; closure on every reader folder.
2. **Driver** `scripts/secondary/reading/run_ru3t_all.sh`. It runs the reader contexts in order: all r1, then all r2, each through
   the existing launcher with the `ru3t` root.
   - Before EACH context, run a limit probe. If weekly use is ≥ 70%, stop, and write `artifacts/ru1/ru3t/STOPPED_AT_70.json` with
     the contexts done.
   - Log every context's result line.
   - It never runs a context twice.
3. **Finaliser** `scripts/secondary/ru3t_finalize.sh`.
   - Canonical v4.4 scans, control gates, the derived-view coverage rule (RU2T-F3), and the edit rule.
   - Any VOID or failed reader-context leaves its positions without that read, so they go to lead_review. List them for a fresh-r3
     re-read.
   - **Merge** with the RU2T decisions into `artifacts/ru1/ru1_v3_train.jsonl`: parent = the v2 train label, plus a manifest and sha.
   - **Partial mode:** if `STOPPED_AT_70.json` exists, the output is `ru1_v3_train_partial.jsonl` plus `covered_lines.txt`.
   - **Lead material:** a review sheet for lead_review positions (same-book references, as RU2T) and an audit sheet (40 edit_hard + 20
     keep_soft, seeded), both in the scratchpad `ru1_review/ru3t/`.
   - **LQB:** register `ru1_v3_train` (or the partial version) and re-score.

   Test the finaliser on fixtures.
4. **Receipt and report:** `artifacts/ru1/RU3T0_RECEIPT.json` and `docs/records/labelfix/secondary/RU3T0_REPORT.md`, with contexts, reads
   and a Codex estimate.

**Last line:** `RU3T0 READY: lines <n>, slots <n>; contexts <n> ×2; est <pts> pts; closure <ok>; driver dry-run <ok>; finalizer tests <n> passed`
