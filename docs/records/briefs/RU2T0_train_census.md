# RU2T-0: RU1 on collection-v2 train Cyrillic — census, orthography, budget plan, packs (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

**Owner priority** (via the coordinator): apply the RU1 rule to the Cyrillic rows already in the training set.
- Every word-final ь in Google's label gets the Sol glyph question, with two reads.
- ъ is written only when both reads agree on ъ; Google's ъ is never touched; an unreadable read means hold.
- Output `ru1_v2_train.jsonl`, registered in the LQB.
- **Budget ≈ 1 Codex weekly point**, which is about 450 reads, so about 225 lines at 2 reads each.

**Inputs (read only).** The collection-v2 train labels are
`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`; crops are referenced from the rows. If a crop is
not on this Mac, list it; do not fetch. Reuse the RU1 tooling in `scripts/secondary/` (census, pack builder, the yer prompt, the
combiner) and the canonical scanner already adopted by hash.

**Do.**
1. **Census** of the Cyrillic rows (script class Cyrillic, or any row with ≥3 Cyrillic letters):
   - per source/book: rows, word-final ь (final / pre_hyphen), word-final ъ, and ѣ і ѳ ѵ counts;
   - language guess (Russian, Bulgarian, Serbian, …) from the source metadata.
2. **Orthography class per book.**
   - `pre_reform` if Google wrote ≥5 word-final ъ OR any ѣ/і/ѳ/ѵ. This covers Russian before 1918 and Bulgarian before 1945, which
     also used a final ъ.
   - `modern` otherwise.
   - Only pre_reform books have candidate positions. Modern books are never edited: their word-final ь is correct by orthography.
     Report modern books, with a 10-position seeded list for a later spot check.
3. **Budget plan.** Count the candidate lines in pre_reform books.
   - **If the 2-read cost fits about 1 point** (≤ 225 lines, 2 reads each, plus about 10% controls at 0.2 points per 100 items):
     build the full packs.
   - **If it does not fit:** build packs for a seeded, book-stratified sample of 200 lines, write the full candidate list, and
     report the point cost of covering everything. The lead decides whether to extend.
4. **Packs:** the RU1 layout, r1 and r2 (exact reverse, fresh ids), ≤100 items per context, controls from the 65 adjudicated RU1
   positions, closure on every pack.
   - Root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/`, with a launcher root `ru2t` in `run_bed.sh` or an equivalent wrapper.
   - Crops are copied by sha from the collection-v2 crop paths.
5. **Finalise script** `scripts/secondary/ru2t_finalize.sh`. After the readings it does: scan check (canonical v4.4), mapping,
   combining (the ru1 edit rule), `artifacts/ru1/ru1_v2_train.jsonl`, per-row decision counts, a manifest with sha, and the LQB
   registration of the version (`versions.json` entry `ru1_v2_train`, parent = collection-v2 train label). Test it on fixtures.
6. Write the receipt `artifacts/ru1/RU2T0_RECEIPT.json` and the report `docs/records/labelfix/secondary/RU2T0_REPORT.md` (census table,
   orthography classes, budget plan).

**Last line:** `RU2T0 READY: cyrillic rows <n>; books pre_reform <n> / modern <n>; candidate ь positions <n> in <n> lines; plan <full|sample 200> (<points> pts for full); contexts <n> ×2; closure <ok>; tests <n> passed`
