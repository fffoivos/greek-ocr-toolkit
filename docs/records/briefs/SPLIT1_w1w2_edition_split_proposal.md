# SPLIT1: edition-level W1/W2 split proposal and owner review sheet (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Why this matters:** census_03 on Clariden held **142,959 rows** as `split_or_edition_identity_unresolved`. These are the collect-v3 W1/W2 rows (parent ids `collect-v3-W1-20261018-0524` / `…W2…`, `split: "unassigned"`). They cannot be admitted until each carries an edition identity and a split. The owner allocates the split. This task builds the **proposal plus a review sheet**, from which the owner decides. **It assigns nothing final.**

**Owner rules (19 Oct; binding):**
- A tool is exactly the owner's rules; add no extra guards. Anything extra goes into the evidence as a diagnostic or a question.
- Review sheets follow `~/Projects/greek-ocr-toolkit-review/docs/review/HUMAN_REVIEW_SHEETS.md` (branch coord/review-sheets, read-only; reference builders in `docs/records/review/reference/` and `greekocr/adjudicate/`).
- Athens time, stamped from `date`.
- No pushes. The live run root `~/Projects/collect-v3-data/run` is read-only.
- Use only the byte-exact interpreter `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` for any crop regeneration.

## Inputs (read-only)
- **Rows:** `~/Projects/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl` and `W2_features_20261018_0524.jsonl`. Verify them against `SHA256_20261018_0524.txt`. These are exactly the census_03 W1/W2 inputs.
  - Use **all** rows the census received from them. If you cannot reproduce the census's W1/W2 row selection, report the rule you used and the count vs 142,959.
  - Note: the 436 BSB pages read after 05:24 are not in these snapshots. Mark the 10 BSB W2 documents as partial.
- **Document and edition metadata:** the collector manifests (`run/W1_manifest*.jsonl`, `run/W2_manifest*.jsonl`) and the per-page records (`run/W1|W2/pages/*.json`, read-only): title, year, volume, identifier and source URL where present.
- **Collection v2 splits**, for leakage: `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl` (read-only; fields `doc`, `source_url`, `split`, `year`). Also the locked/eval classes in sol-collect `docs/records/harvest/collect_v3/release_exclusions/release_exclusions.json`.
- **Quotas:** the data plan (find `DATA_PLAN_v2*` in `~/Projects/greek-page-ocr/docs/` or the toolkit docs, read-only). Name the file and section you use.

## Do
1. **Edition identity.**
   - The default unit is the scanned document (`<source>--<dochash>`).
   - Merge documents that are **the same edition**: the same title, year and volume or identifier in the metadata, e.g. two IA scans of one book, or BSB/IA copies of the same edition. Record the evidence for each merge.
   - Gazette: the edition is one issue. **Also group issues by year** for the sheet.
   - Write `edition_id` per row, deterministic (sha of the sorted member document ids).
2. **Leakage against v2.** Any W1/W2 edition that matches a v2 document by identifier, URL or title+year inherits **that v2 split**: v2 test → test, v2 dev → dev; locked/eval → its locked side. List every such match with its evidence. These are forced, not proposals.
3. **Proposed split** for the remaining editions:
   - Whole editions only. Train/dev/test **ratios from the data plan**; if it gives none, propose 85/5/10 by rows, stratified per source × primary class, and say so.
   - Deterministic: seeded by `split1:<source>:<class>`, greedy so that row shares land closest to the target ratios.
   - Report the per source × class row counts per split, against the data-plan quotas.
4. **Outputs** in `docs/records/harvest/collect_v3_admission/split1/`:
   - `editions.jsonl`: edition_id, member documents, metadata, merge evidence, rows per class, forced/proposed split, reason;
   - `row_split_proposal.jsonl.gz`: row id, edition_id, proposed split, forced (bool);
   - `SPLIT_PROPOSAL.md`: method, quotas source, counts tables, leakage list, partial-BSB note, open questions for the owner.
5. **Owner sheet** (HTML, not published; the lead publishes it), following HUMAN_REVIEW_SHEETS.md with one **variant**. Write it into the variant table:
   - one **card per edition**; Gazette editions grouped into **one card per year**, with an issue list;
   - card content:
     - 2 sample crops with their Google text (byte-exact regenerated crops, the hashes checked against crop_sha256);
     - rows per class, source, title/year;
     - the proposed split as the **tool pill** and inner frame: TRAIN green, DEV amber, TEST blue (state the legend);
     - forced editions locked and labelled "forced by v2".
   - **Owner mark:** KEEP = accept the proposed split; DROP = move the edition to the other side (train ↔ held-out). Note textarea.
   - Persistence exactly per §5: collection `notes`, ids `split1:<edition_id>`, never write on load.
   - Groups: forced first, then TEST proposals, DEV, TRAIN.
   - The intro gives the method, the counts table vs quotas and the keys.
   - Keep the page under 10 MB (state its size); headless screenshot check.

Tests: determinism, whole-edition integrity (no edition on two sides), leakage forcing, row counts reconcile with the snapshots, crop shas, and the sheet's no-write-on-load rule.

Write a guarded commit list. The last line must be exactly:
`SPLIT1: done | rows <n> (census held 142,959) | editions <e> (merged <m>, gazette years <y>) | forced by v2 <f> | proposed train/dev/test rows <a>/<b>/<c> | quotas source <file> | sheet <path> <MB> | tests: <n> passed`
