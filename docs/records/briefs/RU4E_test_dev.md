# RU4E: ru1 on the v2_test + v2_dev rows of the 9 Russian books — census, packs, driver, edits-only finaliser (gpt-6.1-sol, medium, network OFF; no .git writes; no blind glyph-READER runs, no browser or computer-use; reading local files is allowed)

**Coordinator request.** Wave 1c is uninterpretable because the Cyrillic TEST reference still carries Google's ь where the print has
ъ. Apply the RU3T protocol to the test and dev rows: two agreeing blind Sol reads + the lead's pixel check, edits-only, parent
`google_raw_v2_import` (the RAW Google text, NOT the convention `label`), per-edit provenance.

**Inputs (read only):** `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl` and
`import_real_v2_dev.jsonl`; the 9 book identities from the RU2T-0 census (`artifacts/ru1/` census/manifest); crops as referenced by
the rows.

**Do.**
1. **Census.** Rows in v2_test and v2_dev from those 9 books. Every word-final ь in the RAW Google text, in final position (Google ъ
   is never a candidate). Report counts per split and book, and the candidate lines/positions.
2. **Packs:** the RU3T layout, r1 + r2 (exact reverse, fresh ids), ≤100 items per context, about 10% controls from the 65
   adjudicated positions. Root `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru4e/`
   (the in-repo guard applies), keys `artifacts/ru1/ru4e/`, closure on every pack. Give a Codex estimate at 0.2 points per 100
   reads plus controls.
3. **Driver** `run_ru4e_all.sh` (probe before each context, stop at 70%, never rerun), with its OWN bound copies of the helpers.
4. **Finaliser** `ru4e_finalize.sh`:
   - v4.4 scans, gates, derived-view coverage, combine;
   - VOID contexts → automatic r3 pack builds listed for the lead;
   - lead sheets: an audit of 20 edit_hard + 10 keep_soft, plus genuine disagreements;
   - `--apply-lead` → `artifacts/ru1/ru1_v3_test_edits.jsonl` (rows with ≥1 edit, plus hold rows; raw Google text byte-identical
     except the ь→ъ characters; the split recorded per row), manifest + sha, LQB registration `ru1_v3_test_edits`.

   Test on fixtures.
5. Write the receipt and the report `docs/records/labelfix/secondary/RU4E_REPORT.md`. Do not read.

**Last line:** `RU4E READY: rows test <n>/dev <n> in 9 books; candidates <n> positions in <n> lines; contexts <n> ×2; est <pts> pts; closure <ok>; dry-run <ok>; tests <n> passed`
