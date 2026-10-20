# CENSUS3: secondary-script table entries + lookalike_only_word, v2 census re-run (gpt-6.1-sol, medium, network OFF)

**Coordinator rulings after CENSUS2 (3f93d204).** Wave 1c binds to this output.

1. **cyrillic class:** Latin is an allowed **secondary** script, at **whole-word level** (citations and Latin words, e.g. the Bulgarian academy volumes and archive_b24878935).
2. **latin class:** Greek is an allowed secondary script, at whole-word level. Such lines (with ≥ 1 admitted Greek word) are **RECLASSIFIED to the existing `mixed_greek_latin` class** (e.g. archive_b28038630, the anemi latin rows). Record `class_original` and `class` (the new one) per row; the receipt's source|class counts use the new class.
3. **Condition for both** (owner: "words with more than one script = char confusion"):
   - a secondary-script word is admitted only if it contains **at least one letter with NO lookalike in the primary script**;
   - use **the same lookalike table that `mixed_script_word` already uses** (name it, with its sha);
   - a secondary-script word made only of lookalike letters (e.g. Latin "coco"/"pace" in a Cyrillic line, or Greek "ΑΒΕ" in a Latin line) is a confusion candidate and **fails the line**, under the new rule id **`lookalike_only_word`**;
   - mixed-script words (several scripts inside one word) still fail as `mixed_script_word`, as before.
4. **Everything else unchanged:** the Serbian-by-document rule (CENSUS2), the numerics and headings variants, and the codec. Bump `tool_version` and the table sha.
5. **Re-run** the census over all 271,987 rows in the same format: `ADMISSION_CENSUS_20261018b_admission.jsonl`, `..._receipt.json`, `ADMISSION_CENSUS_20261018b.md`. The per-row schema adds `class_original` and `lookalike_only_words: [str…]`; all other fields stay.
6. **Report:**
   - rows changed vs CENSUS2, per class (fail→pass, pass→fail) and per document (top 10);
   - the `lookalike_only_word` fail count with 20 example words;
   - reclassified rows (latin → mixed_greek_latin) count;
   - the resulting census totals and per-rule counts.
7. **Tests:**
   - Cyrillic line + "Paris" (P/s have no Cyrillic lookalike) → pass;
   - Cyrillic line + "coco" → lookalike_only_word;
   - latin line + "λόγος" (λ/γ have no Latin lookalike) → pass, reclassified;
   - latin line + "ΑΒΕ" → lookalike_only_word;
   - "Δαβій" → still mixed_script_word;
   - all CENSUS2 tests still pass.

As before: `PYTHONPATH=$PWD ~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python`, and assert `greekocr.__file__` lies in this worktree. Inputs are read-only. Use `git add --sparse` for docs/records/harvest/collection/v2.

Leave a guarded commit helper and list. The last line must be exactly:
`CENSUS3: done | v2 census: <fail>/271987 (was 9427) | lookalike_only_word: <n> | reclassified latin->mixed_greek_latin: <n> | changed vs CENSUS2: <short per class> | file sha: <sha> | tests: <n> passed`
