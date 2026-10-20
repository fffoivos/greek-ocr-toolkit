# RU3T-D: explain the inherited differences; issue the edits-only version (gpt-6.1-sol, medium, network OFF; no .git writes; no blind glyph-READER runs, no browser or computer-use; reading local files is REQUIRED and allowed)

The coordinator's wave-1c bind compared `artifacts/ru1/ru1_v3_train.jsonl` (sha e23fcab1…) with the v2 Google import. It differs on
11,951 rows: 314 rows / 331 edits are ь→ъ, and 11,637 rows are "inherited text differences, including Greek apostrophe
normalisation". The bind detail is in `~/Projects/greek-page-ocr-wave1c/out/e4/wave1c_reg/substitution_explanation.json` and
`bind_final/substitution.json` (read only).

**Do.**
1. **Diagnose.**
   - Which field and file did RU2T/RU3T use as `label_parent`? Trace it through ru1_v2_train and ru1_v3_train.
   - Which transform (NFC/NFD, an apostrophe fold, codec normalisation, whitespace…) produced the 11,637 differences relative to the
     v2 Google import (`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`, field as the bind used
     it)?
   - Classify the differences by kind, with counts.
   - Explain my count of 396 edits against the bind's 331 edits on 314 rows. Possible reasons: edits on rows whose base differs,
     double counting, or rows the bind could not match.
2. **The new rule** (coordinator, binding): a registered label version contains ONLY the rows it corrects, with the parent's exact
   text everywhere else, so that exactly one correction is measured at a time.
   - Write `artifacts/ru1/ru1_v3_edits.jsonl`: only the rows with ≥1 ь→ъ edit, plus hold rows marked as hold. Each row's text is the
     v2 Google import text, byte-identical, with ONLY the decided ь→ъ characters changed at their offsets (re-map the offsets if
     the earlier parent differed). Same provenance per edit.
   - Verify: per row, the diff against the import is exactly the listed edits.
   - Manifest and sha. Re-register in the LQB as `ru1_v3_edits` (parent `google_raw_v2_import`), and mark `ru1_v3_train` superseded.
3. Compare with the coordinator's `ru1_v3_edits`, if Sol on their side produced one. Read-only path, if findable under
   `~/Projects/greek-page-ocr-wave1c/`. Report whether the two are identical.
4. Write the receipt and the report `docs/records/labelfix/secondary/RU3TD_REPORT.md`.

**Last line:** `RU3TD READY: parent used <field/file>; inherited diffs <n> by kind <...>; edits mine <n> vs bind <n> (reason); ru1_v3_edits rows <n> edits <n> holds <n> sha256 <hex>; matches coordinator's <yes|no|not found>`
