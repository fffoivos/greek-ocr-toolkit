# SEG-CP5c: apply the coordinator's orientation rulings to close CP5 (gpt-6.1-sol, medium, network OFF)

**Context:** the SEG-CP5 review 2 (`docs/records/reviews/SEG_CP5_review_2.md`) left H1 (2/4 rotated unknown) and H4 (5/22 KEEP unknown) open. The coordinator ruled as the lead recommended. Implement exactly this; reopen nothing else. All CP5 constraints still apply.

1. **Regional inheritance, for unknown-axis lines only.**
   - A line whose own axis is **unknown** inherits **vertical** when it lies inside a page region that the existing `axis_regions`/`resolve_regions` resolve as **vertical and unmixed**.
   - A measured horizontal line axis is **never** overridden. Mixed or unresolved regions give no inheritance.
   - Record the decision source per row: `measured` | `regional` | `unknown`.
2. **Unknown after inheritance → admit (fail open, for orientation only).**
   - The row is not dropped by orientation, and it is **not** a verified keep: status `orientation_unknown`, counted.
   - Add the CP7 counting hooks:
     - unknown-axis rows per source × class;
     - the subset of those that the **old rotated_crop heuristic** (`w1_rotated_crop_ids.txt` membership, and the h>w ∧ ≥4 non-space characters rule) would have excluded, with count and ids.
3. **Acceptance; rerun all of it natively, standalone and in the union:**
   - rotated **4/4** (2 measured + 2 regional);
   - **0/22** KEEP false drops;
   - **0** upright control false drops;
   - **0** horizontal misses;
   - unknowns reported, not counted as verified (list the KEEP unknowns after inheritance);
   - the CP3/CP4 numbers unchanged (KEEP 22/22, C1 6/6, gallery 6/6, D 9/9 composed, fragments 0/12).
   - Tests: a unknown line in a vertical unmixed region → vertical; in a mixed region → unknown/admit; a measured horizontal line in a vertical region → stays horizontal.
4. **Record the rulings** and the coordinator's condition in `seg/CP5_RECEIPT.md`: "if the CP7 fresh 100-card read finds ≥ 1 rotated crop admitted, orientation returns to CP5 before publication".

Update `seg/CP5_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP5c: done | rotated <a>/4 (measured <m>, regional <r>) | KEEP false drops <b>/22 | KEEP unknown after inheritance <u> | upright FP <c> | horizontal misses <d> | CP3/CP4 unchanged: yes/no | hooks: added | tests: <n> passed`
