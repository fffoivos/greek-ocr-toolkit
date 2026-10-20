# N1-TS: combine two reads, lead check sheets, then owner sheet v2 (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. Inputs:
- the 28 readings under `artifacts/n1/answers/n1t2/` (14 contexts × r1, r2);
- calibration v2 (PASS, 81/82);
- `dash_types.jsonl`, `approved.jsonl`;
- the N1-T/N1-Tb line and slot records;
- `PLAN.md` §9 (the owner's feedback, binding).

**Phase 1, now.**
1. **Gates per reader-context**: more than 1 wrong control → VOID, with u as an abstention and the unsure-dash rule applied. Report
   them in a table. If a context is VOID for both readers, list it for a re-read and stop before phase 2 for those slots.
2. **Combiner v2** (`n1_decide`) over all read slots, plus the geometry-only "nothing" slots. Decide per slot as the brief N1-T
   specified, and split lead_review by reason.
3. **Lead check sheets** in the scratchpad `n1_review/t_lead/`, ≤12 cells per sheet. Each cell shows: the marked zoom large; the
   line small; Google's glyph; both reads; the geometric type and `dash_len_ratio`; the slot id. Two sets:
   - (a) **raised**: EVERY slot with any raised-dot read or a raised-dot truth candidate;
   - (b) **review**: every lead_review slot.

   If (b) exceeds 120 cells, stop at 120 seeded cells and report the rest by reason.

   Above each raised sheet put 2 approved raised-dot controls and 2 baseline-dot controls as references. Write `sheets_index.json`
   and `artifacts/n1/lead_t_template.jsonl`.
4. **Report** in a section "N1-TS phase 1" of `N1T_REPORT.md`:
   - the gate table;
   - decision counts;
   - Google × ours (with dash types) over the decided slots;
   - the geometry-only audit (30 slots): did the readers agree with "nothing"?

**Phase 2** runs only after the lead fills `lead_t_template.jsonl` and says go; do NOT run it now. Implement and test it now:
- apply the lead rulings;
- build the owner sheet v2 (spec in N1-T §6) into `artifacts/n1/owner_sheet/n1_sheet.html`;
- produce the summary.

**Last line:** `N1TS PHASE1 READY: contexts VALID r1 <n>/14, r2 <n>/14; slots decided <n>, lead_review <n> (<reasons>); raised cells <n>, review cells <n> on <n> sheets; geometry-audit agree <n>/30; tests <n> passed`
