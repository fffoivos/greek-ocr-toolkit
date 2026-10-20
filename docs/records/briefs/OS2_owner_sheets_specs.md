# OS2: REDIRECT of OS1. Improved spec files for the two owner sheets the coordinator already published (gpt-6.1-sol, medium, network OFF; no .git writes)

OS1 was stopped mid-run, and its partial outputs are in this worktree. **Change of plan:** the coordinator has already rendered and
published both sheets with `greekocr.adjudicate.owner_sheet`. The owner is writing notes on them, keyed by line id.
- Do **not** design new pages.
- Produce IMPROVED SPECS that render through the coordinator's builder, so the coordinator can republish to the SAME two URLs and the
  owner's notes persist.

**Base:** `docs/records/owner_sheets/inputs/coordinator_build_sheets.py`, a copy of the coordinator's builder. Its output today:
- failure modes: 116 cards, 14 classes;
- segmentation: 34 cards.

**Hard compatibility rules:**
- Keep every existing card's db doc id (= line id) and its section. Cards may be ADDED or re-tagged; an existing card is removed only
  if its evidence is wrong, and each removal is listed with the reason.
- Keep the 14 classes and their order as the coordinator built them.

## Improvements

1. **Richer fault classification per card.** Each card gets explicit fault-type tags from the checker's error codes (verdict files /
   c1_results), not one generic tag.
2. **Add the yer cards** (ъ→ь; `c1/yer_adjudication/table.json`) and the **T6b masked-card verdicts** for the three held sources
   (find them under `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/`; name the path). Use 3–6 cards per fault type;
   when fewer exist, say so on the subsection with the count; never fabricate.
3. **Printed prefilled** wherever an adjudicated print exists: C1 card adjudications, the yer table, the R0/print-truth sets. Otherwise
   leave it empty. Record the source of each prefill.
4. **Segmentation sheet:**
   - add the SG2 missing-box group, from `segmentation_gallery/sg2_*`, `SG2.md` and the `sg2-*-strip.png` files;
   - follow the existing groups, with the same card template (strip with the box where one exists, crop, Google row, Printed, tags,
     note).

## Renderer change

OS1 edited `greekocr/adjudicate/owner_sheet.py` (+13/−3, uncommitted). Either:
- revert it, if the coordinator's builder doesn't need it; or
- keep it only if it is additive and backward-compatible: the re-emission tests in `tests/adjudicate` must stay identical, and a new
  test must cover the change. Say which, and why.

## Output

1. Specs as data under `docs/records/owner_sheets/{failure_modes_per_class,segmentation_failures}/spec.json`.
2. The builder, adapted from the coordinator's copy, at `scripts/review/build_owner_sheets_v2.py`.
3. Rendered HTML at `artifacts/owner_sheets/v2/failure_modes_per_class.html` and `artifacts/owner_sheets/v2/segmentation_failures.html`.
4. A diff report vs the coordinator's current build in `docs/records/owner_sheets/OS2_REPORT.md`:
   - cards kept / added / re-tagged / removed, per section;
   - Printed prefills with their sources;
   - doc-id continuity: every old id present, or listed as removed.
5. Tests: the specs render, every card has a doc id, no image is missing, aspect ratios are kept, there are no model names and no "?"
   placeholders. Run `tests/adjudicate`.

Last line: `OS2 READY: failure modes <old>→<new> cards (added <n>, retagged <n>, removed <n>); segmentation <old>→<new> (SG2 <n>); prefilled <n>; doc ids kept <yes>; renderer change <reverted|kept: why>; tests <n> passed`.
