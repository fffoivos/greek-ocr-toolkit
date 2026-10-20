# ADM5c v2 admission census

9,427 / 271,987 rows would fail today. No v2 rows removed or rewritten.

Tool: `ADM5c-CENSUS2-20261018.1`. Expected table: `ADM5c-CENSUS2-20261018.1` / `f273f0d419201c3eea9c0ecebccc49e379de596f74b121e9a8c9054c6d1f5adf`.
Codec: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-census/greekocr/_vendor/codec/v2.json`, version `v2`, SHA-256 `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9`.

Confidence and geometry are n/a when absent. Source/wave/class expectations are declared, never inferred from OCR. Rule counts overlap. DOT ABOVE is normalized before coverage checks; no look-alike correction or Roman exemption.

| wave | rows | fail | short_line | numeric_shape | low_confidence | tall_box | nonletter_frac | unexpected_language | unexpected_script | mixed_script_word | foreign_char |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | 12900 | 1811 | 0 | 0 | 0 | 0 | 0 | 0 | 1638 | 0 | 193 |
| mixed | 30839 | 6358 | 1 | 0 | 0 | 0 | 0 | 0 | 6077 | 6 | 327 |
| openarchives | 25372 | 385 | 0 | 0 | 0 | 0 | 0 | 0 | 233 | 1 | 156 |
| parliament | 81181 | 55 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 32 |
| round1 | 58213 | 432 | 0 | 0 | 0 | 0 | 2 | 0 | 297 | 4 | 134 |
| round2 | 23128 | 233 | 0 | 0 | 0 | 0 | 0 | 0 | 128 | 6 | 104 |
| vouli | 28259 | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 3 | 25 |
| wikisource | 12095 | 122 | 0 | 0 | 0 | 0 | 0 | 0 | 72 | 0 | 51 |

## Rule map

- short_line: R1: fewer than 10 Unicode letters (NFC); headings_caps requires 4
- numeric_shape: numerics_tables: fewer than 4 decimal digits or less than 60% digits/separators
- low_confidence: R2: available mean DocAI confidence < 0.89
- tall_box: R3: height > 1.7 times page median line height
- nonletter_frac: R4: more than one third of nonspace characters are nonletters
- unexpected_language: R5 language branch: majority Latin without mixed class on a Greek source
- unexpected_script: R5 script branch: letter script outside source expectations
- mixed_script_word: R6: multiple letter scripts within one delimited word (no Roman exemption)
- foreign_char: R7: normalized NFD atom absent from codec
- R8: DOT ABOVE → middle dot; normalization only, never a failure.

## Inputs (SHA-256)

- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`: `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3` (214436 rows)
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_dev.jsonl`: `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` (13522 rows)
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl`: `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` (44029 rows)

For multiple inputs, receipt input_path is a JSON path array encoded as a string; input_sha256 is SHA-256 of the exact concatenated input bytes in that order.

## CENSUS2 comparison against committed ADM5c c9fbf9a8

Fails: 10,370 → 9,427. Changed pass/fail decisions: 943. Changed output rows: 976. No non-Serbian output or decision changed (full ordered comparison).

The sole new table entry adds exactly the ADM5c Serbian codec atoms to wave `cyrillic` documents in the recorded Serbian list. Script/class expectations remain in force, including Latin-class rows; no new script exemption.

| rule | ADM5c | CENSUS2 |
|---|---:|---:|
| short_line | 1 | 1 |
| numeric_shape | 0 | 0 |
| low_confidence | 0 | 0 |
| tall_box | 0 | 0 |
| nonletter_frac | 2 | 2 |
| unexpected_language | 0 | 0 |
| unexpected_script | 8471 | 8471 |
| mixed_script_word | 20 | 20 |
| foreign_char | 1993 | 1022 |

### Wave × rule (old → new)

| wave | short_line | numeric_shape | low_confidence | tall_box | nonletter_frac | unexpected_language | unexpected_script | mixed_script_word | foreign_char |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1638 → 1638 | 0 → 0 | 1164 → 193 |
| mixed | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 6077 → 6077 | 6 → 6 | 327 → 327 |
| openarchives | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 233 → 233 | 1 → 1 | 156 → 156 |
| parliament | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 23 → 23 | 0 → 0 | 32 → 32 |
| round1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 0 → 0 | 297 → 297 | 4 → 4 | 134 → 134 |
| round2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 128 → 128 | 6 → 6 | 104 → 104 |
| vouli | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 3 | 3 → 3 | 25 → 25 |
| wikisource | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 72 → 72 | 0 → 0 | 51 → 51 |

### Document language and changed decisions

| document | language | Serbian | rows | changed decisions |
|---|---|---|---:|---:|
| cyrillic:0b4bf868 | rus | False | 1558 | 0 |
| cyrillic:252fd568 | bul | False | 1438 | 0 |
| cyrillic:363040a9 | ['bul', 'ger'] | False | 209 | 0 |
| cyrillic:4b2c4367 | ['bul', 'ger'] | False | 1008 | 0 |
| cyrillic:7235f8d0 | srp | True | 1531 | 819 |
| cyrillic:94847f75 | ['bul', 'eng'] | False | 1193 | 0 |
| cyrillic:975289f3 | ['srp', 'ger', 'lat'] | True | 219 | 124 |
| cyrillic:9a32fb66 | rus | False | 1712 | 0 |
| cyrillic:ae1a00a3 | bul | False | 1225 | 0 |
| cyrillic:b930919b | ['bul', 'ger'] | False | 783 | 0 |
| cyrillic:be2e7fa5 | rus | False | 1575 | 0 |
| cyrillic:e2a71638 | ['bul', 'ger'] | False | 449 | 0 |

All 12 languages were recorded in `source_books.json` and corroborated by acquisition manifests. No unknown or ambiguous documents; no network used. Multilingual `srp/ger/lat` explicitly includes Serbian. Evidence fields and hashes: [language map](census2_document_language.json). Exact affected rows (including rows still failing other rules): [changed rows](census2_changed_rows.json). Machine-readable comparison: [comparison](census2_comparison.json).

Serbian document-list SHA-256 (sorted compact JSON, no newline): `f101a0893a020e0851c7467c6d14f599c3aed5ec97185bffcf9485eb22a72c73`. Extension SHA-256 unchanged: `202a906c5f4b96d4e06d01783e9cffad20f4626db8eea4dc80a9ca3ed1105850`.

Admission file SHA-256: `090b91abb4ba9bdb5110da90daca29356c3efd65600b88ed3018dc2b3f1932b1`.

## Validation

147 tests passed across `test_harvest_admission.py`, `test_adm5c_variants.py`, and `test_round1_admission_outputs.py`, including Serbian, Russian, Bulgarian, and unknown-language document cases. Local import asserted at startup. See [validation receipt](census2_validation.json).
