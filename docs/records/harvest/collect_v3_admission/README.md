# ADM5c standard admission

`greekocr.harvest.admission`, tool/table version `ADM5c-20261017.1`, implements the coordinator rulings in [ADM5c_rule_variants.md](../../briefs/ADM5c_rule_variants.md). All work was offline; the collector, training codec origin, and v2 input splits were read-only. No rows were removed from v2.

## Expected table and Serbian codec

The source table lists `serbia` as Cyrillic with expected characters `ј ћ њ љ ђ џ Ј Ћ Њ Љ Ђ Џ`. This is the exact collector-order extension from `~/Projects/greek-ocr-toolkit-sol-collect/collect_v3/vendor/classify.py:57`, the `serbian_codec` path through `inspect(..., serbian=True)`. Only `serbia` rows use codec v2 plus this extension. Other sources continue using the base codec and their declared script rules. The full extension includes `ј`, already present in v2; base codec bytes remain unchanged.

Every receipt records `serbian_extension_atoms` as this ordered list and `serbian_extension_sha256` as SHA-256 of the concatenated atom string encoded as UTF-8, without delimiters or newline:

`202a906c5f4b96d4e06d01783e9cffad20f4626db8eea4dc80a9ca3ed1105850`

Base codec: `greekocr/_vendor/codec/v2.json`, version `v2`, SHA-256 `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9`. Its frozen-training provenance and historical ADM5b investigation remain in [ADM5b_CODEC_AUDIT.json](ADM5b_CODEC_AUDIT.json).

Expected-table SHA-256: `f90d7ec213d334ce334be2fee36ff3241844e8853c1ebc38617767127d380f88`. The hash covers canonical compact sorted-key UTF-8 JSON of table version, source policies including provenance/Serbian characters, class expectations, mixed-class aliases, and class rule variants.

## Class rule variants

| Declared class | Length / shape rule | Nonletter rule |
|---|---|---|
| numerics_tables | `numeric_shape`: at least 4 Unicode decimal digits and at least 60% digits or `. , · - / space` | replaces `short_line` and `nonletter_frac` |
| headings_caps | `short_line`: at least 4 Unicode letters | retains `nonletter_frac` |
| all others | `short_line`: at least 10 Unicode letters | retains `nonletter_frac` |

Numeric percentage counts all characters in the normalized label, including interior spaces; integer arithmetic includes exactly 60%. Normalization remains DOT ABOVE → middle dot, NFC, and whitespace collapse. The reported `nonletter_frac` remains the original nonspace NFC diagnostic even when it is not an active rejection rule.

Both variant classes retain confidence, geometry, expected-language, expected-script, mixed-word and codec checks. Greek policies continue allowing minority standalone Latin; majority Latin requires an explicit mixed class. V2 expectations come from source/wave/script_class, never OCR text. No look-alike correction or Roman mixed-word exemption is applied.

Rule map remains R1 → short_line (class threshold above), R2 → low_confidence, R3 → tall_box, R4 → nonletter_frac, R5 → unexpected_language / unexpected_script, R6 → mixed_script_word, R7 → foreign_char; R8 is normalization only. `numeric_shape` replaces R1/R4 only for numerics_tables.

## Output schema and replay

Per-row JSONL retains exactly the ADM5b schema: `row_id`, `source`, `class`, `pass`, `rules_failed`, `expected_language`, `expected_scripts`, `letters`, `nonletter_frac`, `scripts_seen`, `mixed_script_words`, `foreign_chars`. `foreign_chars` lists unique literal NFD atoms absent from the applicable source codec. The `expected_scripts` field remains script names; the source table separately lists Serbian expected characters.

Receipts retain all ADM5b fields and add only the two required Serbian extension fields. Rule maps include `numeric_shape`, with zero counts when absent. Counts overlap. The multi-input census receipt hashes exact concatenated input bytes in listed order; per-input hashes and wave × rule counts remain in the census Markdown. Passing admitted rows retain original fields plus normalized label and full admission diagnostics. The historical source-free Wave-0 API is preserved.

```sh
.venv/bin/python -m greekocr.harvest.admission admit \
  ~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/w1_originals_v3.jsonl \
  --output-dir docs/records/harvest/collect_v3_admission

.venv/bin/python -m greekocr.harvest.admission census \
  ~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl \
  ~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_dev.jsonl \
  ~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl \
  --output-prefix docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017

.venv/bin/python docs/records/harvest/collect_v3_admission/compare_adm5c.py
.venv/bin/python -m pytest tests/test_harvest_admission.py tests/test_round1_admission_outputs.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py -q
```

For later W2, Gazette, BSB and final release_v3 inputs, use the same admit command with the new input path. It writes `<name>_admitted.jsonl`, `<name>_admission.jsonl` and `<name>_admission_receipt.json`. Census writes per-row/receipt files and Markdown only.

## Results against ADM5b

| W1 group | ADM5b pass | ADM5c pass | Total |
|---|---:|---:|---:|
| all | 26489 | 28798 | 30114 |
| serbia | 563 | 1204 | 1226 |
| elstat numerics_tables | 0 | 1312 | 2519 |
| headings_caps (all sources) | 1757 | 2113 | 2198 |

All source × class counts for both populations are side by side in [ADM5c_COMPARISON.md](ADM5c_COMPARISON.md) and [ADM5c_COMPARISON.json](ADM5c_COMPARISON.json). [ADM5b_BASELINE.json](ADM5b_BASELINE.json) preserves pre-rerun counts and receipts; the comparison checks input hash and group-size equality. Total W1 change is +2309, accounted for by Serbia +641, ELSTAT numerics +1312, and headings +356. Other source/classes are unchanged.

The v2 census remains **10370 / 271987 failures** (261617 passing). V2 has no `serbia` source or declared variant classes, so its passing rows are unchanged. Its census still contains every original row. Older `*_decisions.jsonl` and `ADMISSION_CENSUS_20261017.json` remain superseded ADM5 snapshots, excluded from the commit list.

Validation: **146 passed**. Tests cover exact collector atom equality, Serbian source scoping, numeric and heading thresholds, exact 60% boundary, retained checks, all earlier planted cases, Wave-0 compatibility, both full output schemas, input/tool/table hashes and receipt aggregates. Network connections are blocked by the test fixture.

[ADM5_COMMIT_LIST.json](ADM5_COMMIT_LIST.json) binds exact paths and hashes to the current branch and starting HEAD. Run `.venv/bin/python docs/records/harvest/collect_v3_admission/guard_adm5_commit.py` before staging. The guard checks hashes, scope, empty index and whitespace; it stages and commits nothing. Unrelated files remain excluded. The list includes the pre-existing untracked codec v2 and schema test required for a reproducible checkout.
