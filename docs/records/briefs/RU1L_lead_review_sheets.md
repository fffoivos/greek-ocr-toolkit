# RU1-L: lead review sheets with same-book reference glyphs (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints and interpreters as RU1-F. The owner does not read Cyrillic, so the lead adjudicates every RU1 review case
by shape comparison. You build the sheets; you classify nothing.

**Do.**
1. **Reference glyphs.** For each of the 10 books, pick from the controls with ink truth (`artifacts/ru1/keys/control_inventory.json`
   plus the table truth) one ъ and one ь final letter, preferring same-book controls read correctly by every reader.
   - If a book lacks one, use bed positions where all reads agree and Google wrote ъ (for ъ) or all reads agree on ь (for ь).
     Mark those as "agreement reference, not adjudicated".
   - Render each as an 8× final-letter crop, using the same crop geometry as the review zooms.
2. **Lead sheets** in the scratchpad `ru1_review/lead/`, ≤10 cells per sheet. Each cell has:
   - a cell number;
   - the 8× final-letter crop of the position, with the book's reference ъ on its LEFT and reference ь on its RIGHT, at the same
     scale and each labelled ъ / ь;
   - the 4× word crop and a small line crop;
   - the r1/r2(/r3) calls;
   - no prior and no Google text.

   Two sets:
   - (a) **review**: all 27 lead_review positions;
   - (b) **audit**: 30 edit_hard positions, seeded `20261017:RU1L:audit`, stratified by book in proportion, plus 10 keep_soft
     positions seeded the same way.

   Write `sheets_index.json` (cell → row id, offset, set, decision, reads).
3. **Answer file** for the lead: an empty `artifacts/ru1/lead_review_template.jsonl`, one row per cell with
   `{cell, row_id, offset, set, lead: null, note: ""}`.
4. Write the receipt `artifacts/ru1/RU1L_RECEIPT.json` and a section "RU1-L" in `RU10_REPORT.md`. No tests are needed beyond an index
   ↔ cell count check.

**Last line:** `RU1L READY: references <n> books (agreement-only <n>); review cells 27 on <n> sheets; audit cells 40 on <n> sheets`
