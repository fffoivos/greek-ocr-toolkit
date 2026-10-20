# N1-Cb: regenerate crops with the collector interpreter, render step1 + control sheets (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue N1-C (`docs/records/briefs/N1C_controls_and_packs.md`, report `docs/records/labelfix/secondary/N1C_REPORT.md`, which was blocked by crop
hash mismatches). Same worktree, constraints and allowed writes as N1-C.

**Lead rulings.**
1. **Crop regeneration.** Call `collect_v3.storage.ensure_crop` under the collector's own interpreter,
   `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (arm64, Python 3.11.3, Pillow 12.3.0). That interpreter regenerated all
   1,146 ia_russian crops byte-exactly in RU1-0b. Always pass a row copy whose `crop` is redirected into the scratchpad
   `n1_cache/crops/`. Rendering and measurement may then run under whichever interpreter has the needed packages (x86 with `-s`, as
   in N1-C), because they read the verified crop bytes. Record both interpreters in the receipt.
2. **The 42 misaligned step1 slots** are dropped from the step1 bed and listed with their reasons; they are not replaced. Report the
   28 "digit box outside the crop" cases separately, because they point at clipped crops.
3. **Range-control shortfall.** Draw the missing 11 range-hyphen controls from any other W1 source, using the same exclusions (not in
   step1 documents, not reserved, not C1), seed `20261017:N1C:ctrl:range`. Keep the existing 13. If the whole of W1 still falls short,
   take what exists and report the count.
4. **C1 references.** Drop `elstat--c5f7ea1f26d39839--s000-l0367`, because it is reserved: the guard refusing it was correct. Render
   the other two cards' four slots as reference cells. They go on one separate sheet marked "C1 reference", never in a pack.
5. **Misaligned control candidates** (15) are dropped. Replace them from the same category pools with the same seed stream, then report.

**Do.**
1. Regenerate the crops for the 558 ok step1 slots and for all control candidates. Hash failures → `crop_unavailable`, listed.
2. Render the line and zoom images plus the private geometry/measurement side records for every ok slot, as specified in N1-C.
3. Build the lead's contact sheets in the scratchpad `n1_ctrl_sheets/`:
   - ≤12 cells per sheet;
   - each cell has the zoom large, the line small, the cell number and Google's glyph;
   - write `sheets_index.json` (cell → candidate slot id).
   Self-check at most 2 sheets for layout only. Do not classify any glyph.
4. Write `artifacts/n1/controls/candidates_v2.jsonl` and keep v1.
5. Do NOT build the real packs or the calibration pack: the lead first approves the controls.
6. Write the receipt `artifacts/n1/N1Cb_RECEIPT.json`, append an "N1-Cb" section to `N1C_REPORT.md` (with the sheet paths), and
   re-run the tests.

**Last line:** `N1Cb READY: step1 rendered <n>/558 (crop_unavailable <n>); dropped misaligned 42 (crop-outside <n>); control candidates <n> (thousands <n>, decimal <n>, range <n>, inner-hyphen <n>, empty <n>) on <n> sheets + 1 C1 reference sheet; tests <n> passed`
