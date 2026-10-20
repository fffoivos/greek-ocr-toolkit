# ADM5c v2 admission census

2,489 / 271,987 rows would fail today. No v2 rows removed or rewritten.

Tool: `ADM5c-CENSUS3-20261018.1`. Expected table: `ADM5c-CENSUS3-20261018.1` / `654adb940fdeabb31da1404167c87fb32ca804d612731dd03911527cb2366c7a`.
Codec: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-census/greekocr/_vendor/codec/v2.json`, version `v2`, SHA-256 `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9`.

Confidence and geometry are n/a when absent. Source/wave/class expectations are declared, never inferred from OCR. Rule counts overlap. DOT ABOVE is normalized before coverage checks; no look-alike correction or Roman exemption.

| wave | rows | fail | short_line | numeric_shape | low_confidence | tall_box | nonletter_frac | unexpected_language | unexpected_script | mixed_script_word | lookalike_only_word | foreign_char |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | 12900 | 717 | 0 | 0 | 0 | 0 | 0 | 0 | 315 | 0 | 221 | 193 |
| mixed | 30839 | 1172 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 845 | 327 |
| openarchives | 25372 | 188 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 31 | 156 |
| parliament | 81181 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 32 |
| round1 | 58213 | 174 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 4 | 35 | 134 |
| round2 | 23128 | 113 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 4 | 104 |
| vouli | 28259 | 29 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 25 |
| wikisource | 12095 | 64 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 51 |

## Rule map

- short_line: R1: fewer than 10 Unicode letters (NFC); headings_caps requires 4
- numeric_shape: numerics_tables: fewer than 4 decimal digits or less than 60% digits/separators
- low_confidence: R2: available mean DocAI confidence < 0.89
- tall_box: R3: height > 1.7 times page median line height
- nonletter_frac: R4: more than one third of nonspace characters are nonletters
- unexpected_language: R5 language branch: majority Latin without mixed class on a Greek source
- unexpected_script: R5 script branch: letter script outside source expectations
- mixed_script_word: R6: multiple letter scripts within one delimited word (no Roman exemption)
- lookalike_only_word: R6b: secondary-script word has no letter without a primary-script lookalike
- foreign_char: R7: normalized NFD atom absent from codec
- R8: DOT ABOVE → middle dot; normalization only, never a failure.

## Inputs (SHA-256)

- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`: `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3` (214436 rows)
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_dev.jsonl`: `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` (13522 rows)
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl`: `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` (44029 rows)

For multiple inputs, receipt input_path is a JSON path array encoded as a string; input_sha256 is SHA-256 of the exact concatenated input bytes in that order.

## CENSUS3 comparison against CENSUS2 3f93d204

Fails: 9,427 → 2,489; passes: 269,498. Decision changes: 6,938. Reclassified Latin → mixed_greek_latin: 6,799 (includes rows failing another rule).

Class comparisons below use class_original. Every row adds class_original and lookalike_only_words; changed_existing_field_rows counts differences in prior fields, including expanded expected_scripts. Inputs and CENSUS2 decisions are hash-verified unchanged. All other existing rules and codec coverage are identical row by row. Serbian document policy, headings and numerics remain unchanged. Zero network requests.

| original class | fail → pass | pass → fail |
|---|---:|---:|
| cyrillic | 1110 | 0 |
| greek_latin_cs | 0 | 0 |
| greek_mono | 0 | 0 |
| greek_poly | 0 | 0 |
| latin | 5828 | 0 |

### Top 10 documents by changed decisions

| document | fail → pass | pass → fail |
|---|---:|---:|
| mixed:4c207e1e | 4759 | 0 |
| cyrillic:94847f75 | 333 | 0 |
| cyrillic:252fd568 | 173 | 0 |
| cyrillic:4b2c4367 | 153 | 0 |
| mixed:5725651930e832195811bd81 | 149 | 0 |
| cyrillic:b930919b | 142 | 0 |
| mixed:4a34388c9884fda746d2a8cd | 140 | 0 |
| cyrillic:e2a71638 | 90 | 0 |
| cyrillic:ae1a00a3 | 81 | 0 |
| round1:3cb3c1caf7324ded3b11c1e5 | 75 | 0 |

### Per-rule failures

| rule | CENSUS2 | CENSUS3 |
|---|---:|---:|
| short_line | 1 | 1 |
| numeric_shape | 0 | 0 |
| low_confidence | 0 | 0 |
| tall_box | 0 | 0 |
| nonletter_frac | 2 | 2 |
| unexpected_language | 0 | 0 |
| unexpected_script | 8471 | 315 |
| mixed_script_word | 20 | 20 |
| lookalike_only_word | 0 | 1150 |
| foreign_char | 1022 | 1022 |

lookalike_only_word: 1,150 failed rows. Twenty example tokens (most frequent, case-sensitive): `ον` (482), `ΙΙ` (82), `ν` (70), `III` (63), `Α` (50), `Β` (40), `Ε` (38), `Ι` (36), `p` (36), `Η` (34), `II` (29), `Ο` (27), `a` (27), `Ν` (18), `I` (18), `Μ` (14), `C` (14), `Τ` (13), `Ερ` (12), `Ρ` (12).

Lookalike table: `greekocr.harvest.lookalikes.HOMOGLYPHS`, SHA-256 `f5dddff62b61fca9af6b1fb115ac23ef3ece4bd50e14e9031c25ec4f51ed7acd` (ordered compact UTF-8 JSON, no newline).

Provenance clarification: CENSUS2 mixed_script_word did **not** use any lookalike table: it rejects any token containing multiple letter scripts. The existing case-sensitive `greekocr/_vendor/bench/e1_readout.py::HOMOGLYPHS` groups were extracted unchanged into a shared module for the new rule and the existing diagnostic consumer. No external table, folding or mapping is introduced; tests compare all groups against CENSUS2. The P in Paris has a Cyrillic counterpart in that table; s is distinguishing, so Paris passes. Checks inspect NFC letter code points exactly, without stripping accents or changing labels.

Secondary word admission is per declared cyrillic/latin class. Only all-single-script tokens qualify; lookalike-only tokens fail and are listed. Any admitted Greek token reclassifies a Latin row even if another rule fails. Receipt source|class groups use the resulting class.

[Full comparison](census3_comparison.json) · [Changed rows](census3_changed_rows.json)

Admission file SHA-256: `ef694589fa0e8e6875ac712159222d19177e0d02213d48031fa92ff1efbc6451`.

## Ruling (coordinator, 18 Oct 2026): no lookalike exemption

The 1,150 `lookalike_only_word` failures stay failures. No exemption is made for Roman numerals (I, II, III) or single capitals (A, B, E…) in a secondary script, and there is no re-run. In these tokens the ink is identical in both scripts (I/Ι, A/Α, B/Β), so the script of the label cannot be decided from the print. Admitting them would teach the model an arbitrary script choice; dropping ≈ 0.4% of lines is the cheaper side.

**CENSUS3 (`ADMISSION_CENSUS_20261018b_admission.jsonl`, sha `ef694589fa0e8e6875ac712159222d19177e0d02213d48031fa92ff1efbc6451`) is the standard v2 census.** `greekocr/harvest/lookalikes.py` is the single source of the lookalike table.
