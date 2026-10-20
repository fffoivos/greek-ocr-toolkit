# CS1: correction status table, first version (gpt-6.1-sol, medium, network OFF; no .git writes)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. Write `docs/records/labelfix/CORRECTION_STATUS_20261017.md`: one row per Google label
fault class except polytonic marks. **Use existing measurements only.** Every number cites its source file and commit; nothing is
estimated without a cited count.

**Columns.**
- `class`;
- `measured rate`: with numerator/denominator, stratum and source;
- `what corrects it today`: rule, reader or nothing, and the label version if one exists;
- `signal it needs`;
- `next gated step` (from `docs/records/labelfix/secondary/PLAN.md`), with its gate;
- `status`: measured / in progress / corrected / tag-only / blocked on owner.

**Classes, in the order of PLAN.md §1, §9, §10:**
1. **N1 numeric separators.**
   - Step-0 census: `N1_STEP0_REPORT.md`.
   - Single-read glyph pass: `N1S_REPORT.md`.
   - Line-complete pass: `N1T_REPORT.md`, including the N1-TS phase-1 section if present.
   - Owner rulings: PLAN §9.
2. **RU1 Russian ъ.** Sources: RU10_REPORT, RU1_LEAD_REVIEW, `ru1_v1_manifest.json`, and the re-check in PLAN §10.
3. **RU2 yat.**
4. **RU3 variant т.**
5. **Capitals case.**
6. **Punctuation**, with sub-rows: ano teleia, ellipsis, line-end hyphen, and em dash as tag-only.
7. **Superscripts.**
8. **Rare glyphs** (ϛ ϗ ȣ ϲ). T10: `DOCAI_FAILED_LINES_v1.md` in `~/Projects/greek-ocr-toolkit` (find it). Codec coverage:
   `~/Projects/greek-page-ocr/codec/v2.json`.
9. **Mixed-script lookalikes**, with Greek/Latin and Cyrillic/Latin sub-rows.
10. **Silent misprint correction.**

**Sources to use:**
- `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/c1_results.json` and `C1_REPORT.md`: per-stratum tallies of
  superscript, dash, separator, lunate and lookalike;
- `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/E3_RESULTS.md`: line-type CER. Mark it clearly as recogniser error, not
  Google label error;
- the RU1 re-check (sol/recut-v1 50147b93 `docs/records/harvest/recut_v1/w1_masked/ruc1/RESULTS.md`);
- owner sheet notes as recorded in PLAN.

**Polytonic marks.** Include them BY REFERENCE only: a short section linking
`~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/CORRECTION_STATUS_MARKS.md` at commit `89c510bd6`, with its row
count. Do not copy or rewrite its rows. State the composition order: marks first on raw Google, the secondary composers after.

**Header.** Date and time from `date`, the commit of every source, and "living document; updated per deliverable".

Add a validation script that checks every cited path exists and every count appears verbatim in its source. Run it and report.

**Last line:** `CS1 READY: rows <n> (+marks by reference 11); citations checked <n>/<n>`
