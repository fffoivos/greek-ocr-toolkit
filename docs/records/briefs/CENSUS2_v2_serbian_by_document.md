# CENSUS2: re-issue the v2 admission census with the Serbian-by-document rule (gpt-6.1-sol, medium, network: archive.org metadata only, if needed)

**Coordinator ruling.** The Serbian codec extension (exactly the ADM5c `serbia` extension atoms and sha) also applies to v2 wave `cyrillic` rows **whose document is Serbian, judged by document/language metadata, never by letter presence**. The current census (ADM5c, `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017*`, commit c9fbf9a8) wrongly fails those rows on unexpected_script/foreign_char. A training wave (1c) is waiting on this re-issue.

**This worktree** (`~/Projects/greek-ocr-toolkit-sol-census`, branch `sol/census-v2-serbian`, from c9fbf9a8 = the committed ADM5c tool) is **clean of the NW/SEG drafts**: use its `greekocr/harvest/admission.py`. Run Python as `PYTHONPATH=$PWD ~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python …`, and **assert at startup** that `greekocr.__file__` lies inside this worktree. Never touch `~/Projects/greek-ocr-toolkit-sol-recut` (live SEG work) or the main checkout `~/Projects/greek-ocr-toolkit` (read-only input). Note: `docs/records/harvest/collection/v2/` is outside the sparse checkout here; create it, and the commit will use `git add --sparse`.

## Do
1. **Document language.**
   - For each distinct `doc`/`source` in the v2 wave `cyrillic` rows (`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`; the rows carry no language field), find its language from **recorded metadata first**: the harvest manifests and IA metadata saved during the Cyrillic harvest (search `~/Projects/greek-ocr-toolkit/docs/harvest/` and `~/Projects/greek-ocr-toolkit-sol-collect/`, read-only).
   - Only for documents with no recorded language, query `https://archive.org/metadata/<identifier>` (≤ 1 req/s, contact UA, honour Retry-After, no auth), and save the raw responses under `docs/records/harvest/collection/v2/census2_ia_metadata/`.
   - Write `census2_document_language.json`: doc → language code, evidence path/url, Serbian yes/no. Ambiguous or unknown documents stay **not Serbian**; list them.
2. **Table entry and re-issue.**
   - Add one expected-table entry: wave `cyrillic` + document in the Serbian list → the ADM5c Serbian extension. Bump `tool_version` and the table sha; record the Serbian document list and its sha in the receipt.
   - Re-run the census over all 271,987 rows in the **ADM5c format** (the per-row file + receipt, the same schema and rule ids). Name the outputs `ADMISSION_CENSUS_20261018_admission.jsonl`, `..._receipt.json` and `ADMISSION_CENSUS_20261018.md`.
3. **Report:**
   - per-rule fail counts, old (ADM5c) vs new;
   - per wave × rule;
   - the rows that changed decision, by document;
   - confirmation that no non-Serbian row changed decision.
4. **Tests:**
   - a Serbian-document row with њ passes;
   - the same character in a Russian/Bulgarian document still fails;
   - unknown-language documents stay strict;
   - the existing admission tests pass.

Leave a guarded commit list. The last line must be exactly:
`CENSUS2: done | serbian docs: <n> (rows <n>) | v2 census: <fail>/271987 (was 10370) | per rule: <short> | changed rows: <n> (all serbian docs: yes/no) | file sha: <sha> | tests: <n> passed`
