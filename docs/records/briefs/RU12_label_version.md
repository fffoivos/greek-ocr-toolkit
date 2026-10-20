# RU1-2: label version ru1_v1 + visual owner summary page (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints and interpreters as RU1-F/RU1-L. Inputs:
- `artifacts/ru1/decisions.jsonl`;
- the lead's rulings in `docs/records/labelfix/secondary/RU1_LEAD_REVIEW.md` (cell numbers map to positions through the scratchpad
  `ru1_review/lead/sheets_index.json`);
- W1 rows `~/Projects/collect-v3-data/run/W1/features.jsonl`, ia_russian, read only.

**Do.**
1. **Apply the lead rulings** to the 27 review positions:
   - cells 1–8, 10–16, 18–22 and 24–26 → edit_hard;
   - cell 23 → keep_soft;
   - cells 17 and 27 → hold_yat (printed ѣ, out of RU1 scope);
   - cell 9 → hold_uncertain.

   Record `lead_ruling` with a reference to the review doc. Audit cells (28–67) change nothing; record them as `lead_audit_confirmed`.
2. **Label version** `artifacts/ru1/ru1_v1.jsonl`, one row per ia_russian W1 row id that has ≥1 Google-final-ь position in the bed:
   - fields: `id`, `label_parent` (= the W1 `label`), `label_ru1_v1`, `edits` [{offset, from:"ь", to:"ъ", basis:
     two_reads|lead_ruling}], `holds` [{offset, reason}], `status` (ok | hold);
   - a row is `hold` if it has any hold;
   - only ь → ъ at decided offsets; every other character is byte-identical to `label_parent`.
   - Test it: non-edited characters are identical, every edit offset holds ь in the parent, Google ъ and pre_hyphen slots are never
     touched, and hold rows are marked.

   Also write `artifacts/ru1/ru1_v1_manifest.json`: row counts (ok/hold), edit counts by basis, the sha256 of `ru1_v1.jsonl` and of
   every input, and the list of bed lines excluded as controls (they keep `label`).
3. **Owner summary page.** Rebuild `artifacts/ru1/owner_sheet/ru1_sheet.html` with the same renderer and the same title "RU1 Hard
   Sign Decisions". The owner does not read Cyrillic, so this page needs NO reading.
   - **intro** (≤4 sentences, in plain words): pre-1918 Russian prints mark some word endings with a hard sign (ъ, a small flag on
     top), and Google writes it as the soft sign (ь, no flag); give the decision counts; give the audit result; and say "nothing to
     review here unless a letter on the left does not look like the one in the middle".
   - **One group "What a change looks like"**, with 12 seeded edit cards. Each card shows: the 8× final-letter crop of the edited
     position between the book's ъ reference (left, labelled "hard sign ъ, flag") and ь reference (right, labelled "soft sign ь,
     no flag"); the word crop; the tags edit / book. The rows are `Google` (the W1 `text`) and `Proposed` (`label_ru1_v1`), each
     with the edited word only highlighted using a `<mark>`.
   - **One group "Held back"** with the 3 hold rows, same layout.
   - Keep it under 5 MB.
4. **Receipt** `artifacts/ru1/RU12_RECEIPT.json` and a section "RU1-2" in `RU10_REPORT.md`. Run the tests.

**Last line:** `RU12 READY: ru1_v1 rows <n> (ok <n>, hold <n>); edits <n> (two_reads <n>, lead_ruling <n>); sha256 <hex>; owner page <MB> MB; tests <n> passed`
