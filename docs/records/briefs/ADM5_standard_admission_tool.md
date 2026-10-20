# ADM5: the standard admission tool `greekocr.harvest.admission` (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Owner rule (verbatim):** "remember the filters we used before should be standard filters for all experiments! have an expected language for all lines, and expected scripts, check for words with more than one scripts (char confusion) and also for lines with chars that shouldn't be there (korean or whatever else)".

This takes priority over everything except the live collector reads. Build in this worktree (`sol/recut-v1`). **`greekocr/harvest/admission.py` already exists:** read it and its tests first, then **extend it into the single standard tool** (library + CLI). Do not create a parallel module. The main checkout `~/Projects/greek-ocr-toolkit` is read-only (another agent works there).

## The standard checks (14 Oct rules, made standard)
1. ≥ 10 letters.
2. Mean DocAI confidence ≥ 0.89 where a confidence is available; record `n/a` otherwise.
3. Tall box > 1.7 × the page median line height → drop, where geometry is available.
4. More than ⅓ non-letters → drop.
5. **Per-SOURCE expected language and expected script set.** A small, versioned table in the module, one row per source:

   | source | language | expected letters | Latin allowed |
   |---|---|---|---|
   | bsb_poly1850, ia_poly1850, nlg, kosmopolis, lekythos | polytonic Greek | Greek | only for class mixed_greek_latin; otherwise majority-Latin → drop |
   | gazette_modern | modern Greek (monotonic) | Greek | as in the table |
   | elstat | Greek | Greek + digits | as in the table |
   | serbia, ia_russian, cyrillic waves | Cyrillic | Cyrillic | as in the table |
   | v2 waves (round1, round2, mixed, vouli, parliament, openarchives, wikisource, cyrillic) | from their wave/script_class | as in the table | as in the table |

   State every entry's provenance.
6. **Mixed-script word** (Greek + Latin/Cyrillic/other letters inside one word, after splitting on `=` and `-`) → **line dropped**. No look-alike correction. Examples: ΚΕΦΑΛΑΙΟN, Δαβій, Fιδον.
7. **Any character outside the expected scripts and the codec** (CJK, Hangul, Thai, Lao, Tibetan, Indic, Hebrew, Arabic, anything else not in the codec) → line dropped. Keep §, †, °, %, =, +, / only if they are in the codec; name the codec file and its sha.
8. **DOT ABOVE → middle dot** (a normalisation, recorded per row).

**Output per row:** pass/fail, the ids of the rules that failed, and the normalisations applied.
**Receipt:** drop counts per rule per source × class (rows can fail several rules: report the first failure and all failures), the table version, the codec sha and the input sha.

## Apply
- **(a)** `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/w1_originals_v3.jsonl` (read-only). Write `w1_originals_v3_admitted.jsonl` + `w1_originals_v3_admission_receipt.json` into **this** worktree under `docs/records/harvest/collect_v3_admission/`. Provide the CLI command for later files (w2, Gazette, BSB, the final release_v3), so that each run produces `*_admitted.jsonl` plus a receipt.
- **(b)** The OLD collection v2 train/dev/test rows (`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`, read-only): a **census only**, i.e. counts of rows that would fail today, by wave × rule. Write it to `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017.md` (+ json) **in this worktree**. **Remove no rows from v2.** The training builds decide using the receipt.

## Tests with planted cases
- a Korean character → drop;
- `Δαβій` → mixed-script drop;
- `ΚΕΦΑΛΑΙΟN` → mixed-script drop;
- a 6-letter line → length drop;
- a tall box → drop;
- DOT ABOVE → middle dot;
- a clean polytonic line, a clean Cyrillic line and a clean ELSTAT number line → pass.

Keep the module's existing tests passing.

Leave a guarded commit list. The last line must be exactly:
`ADM5: done | tool: greekocr.harvest.admission (CLI <cmd>) | w1_originals_v3: <in> -> <admitted> admitted | v2 census: <n fail>/<n> (<top rules>) | tests: <n> passed`
