# ADM5c v2 admission census

10,370 / 271,987 rows would fail today. No v2 rows removed or rewritten.

Tool: `ADM5c-20261017.1`. Expected table: `ADM5c-20261017.1` / `f90d7ec213d334ce334be2fee36ff3241844e8853c1ebc38617767127d380f88`.
Codec: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/greekocr/_vendor/codec/v2.json`, version `v2`, SHA-256 `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9`.

Confidence and geometry are n/a when absent. Source/wave/class expectations are declared, never inferred from OCR. Rule counts overlap. DOT ABOVE is normalized before coverage checks; no look-alike correction or Roman exemption.

| wave | rows | fail | short_line | numeric_shape | low_confidence | tall_box | nonletter_frac | unexpected_language | unexpected_script | mixed_script_word | foreign_char |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | 12900 | 2754 | 0 | 0 | 0 | 0 | 0 | 0 | 1638 | 0 | 1164 |
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
