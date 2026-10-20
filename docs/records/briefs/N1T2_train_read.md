# N1-TR: reading-based N1 on the v2 train rows — packs, 70%-stop driver, finaliser (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The coordinator said go (`docs/records/labelfix/secondary/N1G_GATE_FAIL.md`). The ink rule's 0/5 gate failure stands, recorded and not
patched.

**Rule.** Google `-` or `.` → U+00B7 ONLY where two blind Sol reads from valid contexts agree on "raised dot" AND the lead has
pixel-checked that slot. Nothing else is edited. Ranges are never edited. Every other outcome (disagreement, unreadable/other, VOID)
is a hold, recorded per slot.

**Do.**
1. **Candidates.** In `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`, every slot where
   Google's gap is `-` or `.` between digits inside a numeric token with ≥ 4 digits in total (use `greekocr.numerics.tokens`).
   - Count them per source/era.
   - Exclude every id listed in release_exclusions (locked) and the N1 reserved documents.
   - Localise each slot with the exact symbol geometry where the v2 row has it. Otherwise use crop-based digit localisation from the
     existing renderer helpers. Slots that cannot be localised: list them, never guess.
2. **Packs** with sep2: r1 + r2 (exact reverse, fresh ids, fresh option permutations), ≤100 items per context, about 10% approved
   controls with ≥1 raised-dot control each.
   - Root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1tr/`
     (the in-repo guard applies).
   - Keys in `artifacts/n1/n1tr/`. Closure on every pack.
3. **Driver** `scripts/secondary/reading/run_n1tr_all.sh`, like `run_ru3t_all.sh`: a probe before each context, stop at ≥ 70% with
   `STOPPED_AT_70.json`, never rerun a context.
4. **Finaliser** `scripts/numerics/n1tr_finalize.sh`:
   - v4.4 scans, gates, the derived-view coverage rule;
   - two-read combine;
   - a lead sheet of EVERY agreed raised-dot slot, plus raised references from the same document, in the scratchpad
     `n1_review/n1tr/`, with a template;
   - after the lead fills it (a second invocation with `--apply-lead`): `artifacts/n1/n1_v1_train.jsonl` (parent label, new label,
     edits, holds, per-slot provenance), a manifest and sha, LQB registration of `n1_v1_train` and a re-score;
   - partial mode if the driver stopped.

   Test it on fixtures.
5. Write the receipt `artifacts/n1/N1TR_RECEIPT.json` and the report `docs/records/labelfix/secondary/N1TR_REPORT.md`.

**Last line:** `N1TR READY: candidates <n> (by source <...>), unlocalised <n>; contexts <n> ×2; est <pts> pts; closure <ok>; driver dry-run <ok>; finalizer tests <n> passed`
