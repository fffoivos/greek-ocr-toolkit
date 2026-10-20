# RU4E-2: census of ALL Cyrillic rows in v2_test/v2_dev + LQB test failures (gpt-6.1-sol, medium, network OFF; no .git writes; no blind glyph-READER runs, no browser or computer-use; reading local files is allowed)

RU4E found 0 rows of the 9 training books in v2_test/v2_dev, because the splits are by document. The wave-1c Cyrillic test slice
therefore comes from OTHER books.

**Do.**
1. **Census over every Cyrillic row** (≥3 Cyrillic letters, or script class Cyrillic) in `import_real_v2_test.jsonl` and
   `import_real_v2_dev.jsonl`, on the RAW Google text:
   - per book: rows, language guess, word-final ь and ъ counts, ѣ/і/ѳ/ѵ counts;
   - orthography class (pre_reform: ≥5 final ъ or any ѣ/і/ѳ/ѵ);
   - candidate positions (final ь) in pre_reform books.
   Also locate the wave-1c Cyrillic test slice: `~/Projects/greek-page-ocr-wave1c/` (read only; find the eval/test manifest it
   scored) and confirm it equals these rows.
2. **If there are candidates:** build packs, driver and finaliser exactly as in RU4E (reuse its tools; root `sol_packs/ru4e/`; the
   output is still `ru1_v3_test_edits.jsonl`), with a Codex estimate. Do not read.
3. **LQB test failures:** RU4E reported 14 failures in the broader LQB tests. List each with its cause. Fix only the ones that are
   genuine regressions in this worktree's LQB code (with tests), and report the rest. Do not touch other worktrees.

**Last line:** `RU4E2 READY: cyrillic rows test <n>/dev <n> in <n> books (pre_reform <n>); candidates <n> positions in <n> lines; matches wave1c slice <yes|no>; contexts <n> ×2; est <pts> pts; LQB failures <n> (fixed <n>, other <n>)`
