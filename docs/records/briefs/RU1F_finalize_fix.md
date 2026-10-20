# RU1-F: fix label↔Google offset mapping in the sheet builder, then finalise (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints and interpreters as RU1-S/RU1-R3. The ctx04/r3 reading is DONE (the lead ran it; its scan must clear).

**Error.** `scripts/secondary/ru1_finalize.sh` stopped in the sheet build with "current label differs from retained Google line;
manual geometry required". Positions are offsets in the W1 `label`, which is post-convention (see `fixed_label` and `literal_label`),
but the symbol boxes belong to the Google line text.

**Do.**
1. **Map** label offsets to Google-text offsets with a deterministic character alignment, `difflib`-style or the collector's own
   convention records if they exist; check `collect_v3` for a convention diff.
   - Accept a mapping only when the yer position and its word align unambiguously: same word, same letter, with differences only
     elsewhere in the line.
   - Otherwise there is no zoom. The card shows the line crop alone and is tagged `zoom: unaligned`. Never guess geometry.
   - Count how many positions fall into each case.
   - Add tests on real-shaped fixtures: a convention change elsewhere in the line, a convention change inside the word, and an
     ambiguous repeated word.
2. **Proposed row.** It is built on the W1 `label` (the current label version), not on the Google text. Say this in the intro's last
   sentence.
3. **Run the finalisation yourself:** `scripts/secondary/ru1_finalize.sh`, covering the scan check (ctx04/r3 replaces ctx04/r2),
   mapping, combiner, owner sheet HTML and summary.
   - If ctx04/r3's scan does not clear, stop and report the findings. Do not widen the scanner.
   - Open at most 3 rendered cards to check the layout, and classify nothing.
4. **Report** in a section "RU1-F" of `RU10_REPORT.md`:
   - the final decision counts, the lead_review reasons, and the prior disagreements;
   - control gates per reader-context;
   - the HTML path, size and card count per group.

   Write the receipt `artifacts/ru1/RU1F_RECEIPT.json`.

**Last line:** `RU1F READY: ctx04/r3 scan <ok|VOID>; edit_hard <n>, keep_soft <n>, lead_review <n> (<reasons>); prior disagreements <n>; zoom aligned <n>, unaligned <n>; sheet <path> <MB> MB, cards <n>; tests <n> passed`
