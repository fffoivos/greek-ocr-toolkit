# N1-TS phase 2: GO, with partial lead rulings (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue N1-TS (`docs/records/briefs/N1TS_combine_sheets.md`, report `N1T_REPORT.md` § N1-TS phase 1). Same worktree and constraints.

**Lead rulings.**
- `docs/records/labelfix/secondary/N1T_LEAD_RAISED.md` gives the 24 raised cells. Map them through the scratchpad
  `n1_review/t_lead/sheets_index.json`, fill `lead_t_template.jsonl` for those 24 into `lead_t.jsonl`, and seal it with a sha.
- The edit-rule refinement in that file applies: a lead-verified raised dot gets U+00B7 even outside a thousands slot.
- **The 120 review cells and the other lead_review slots stay UNRESOLVED.** In "Ours" they keep Google's character, and on the card
  they are boxed in the "unsure" style and tagged `unsure:<reason>`.

**Do.**
1. **Phase 2 as specified:** apply the rulings, then build the owner sheet v2 into `artifacts/n1/owner_sheet/n1_sheet.html` (same
   file path; the lead republishes to the same URL so the owner's two notes persist). Additions:
   - **Boxes.** Every slot with a mark is boxed and numbered, in three styles: decided-changed, decided-unchanged, unsure. The
     geometry-only "nothing" slots are not boxed.
   - **Gaps row.** Each slot is named in words for Google and for us, exactly as in N1-T §6, with "unsure" written out.
   - **Intro.** Add one sentence: "boxes with a dashed outline are gaps we have not decided yet; their Google character is kept in
     Ours".
   - **Group "Raised dot written as hyphen by Google":** only lead-verified or two-read raised dots go here.
2. **Geometry audit breakdown.** For the 30 geometry-only audit slots, report what each reader said (13 disagreed with "nothing"),
   and decide whether the geometry-only "nothing" rule is safe. If disagreements involve marks other than "space", list them; the
   lead will widen the read set.
3. **Lead_review triage for a third reader.** Count the lead_review slots by reason that a fresh-order third Sol reader (r3) could
   resolve: VOID, invalid provenance, disagreement, low confidence. Build r3 packs for those slots under `sol_packs/n1t3/` (closure,
   controls as before, sep2), with the launcher root `n1t3`. Do not run them.
4. Write the receipt `artifacts/n1/N1TS2_RECEIPT.json` and a section "N1-TS phase 2" in `N1T_REPORT.md`, with sheet size, card
   count and group counts. Run the tests.

**Last line:** `N1TS2 READY: sheet <MB> MB, cards <n> (groups <...>); boxes changed <n>, unchanged <n>, unsure <n>; geometry-audit disagreements <list>; r3 slots <n> in <n> contexts; tests <n> passed`
