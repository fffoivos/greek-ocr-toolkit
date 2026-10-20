# T24 — Open Archives Wave 4 preflight

**BLOCKED; the requested harvest is not complete.** All 41,675 `ocr_success == true` records have `mojibake_badness_score: null`; zero meet `mojibake_badness_score == 0`. Missing measurements were not converted to zero. No repository requests, PDF downloads, page renders, Google/ADC calls, lines or crops. USD 0.00.

Input: 175,973 final metadata rows; 561,271 external-PDF rows; 830,313 all-links rows; 140 collections. No `.partial` file was present. All four input hashes were checked before and after the join.

Join: **64,340/175,973 = 36.56%** metadata rows; scanned **10,658/41,675 = 25.57%**. 63,000 distinct external rows were matched; 53 metadata rows matched multiple external rows. All actual matches used (collection_slug, PDF URL); no supplied edm_url produced an additional match. An external row with status 200 is preferred among exact matches. HTML entities, unreserved URL escapes and Unicode normalization are handled; queries and reserved escapes retain their identities. No filename-only or cross-repository fuzzy matching. Unmatched repositories are in pool_summary.json.

| Sequential filter | Documents / rows remaining |
| --- | ---: |
| All metadata rows | 175,973 |
| ocr_success is true | 41,675 |
| filter == ok | 25,723 |
| is_empty is false | 25,372 |
| percentage_greek >= 80 | 14,874 |
| mojibake_badness_score == 0 | 0 |
| page_count 20–600 | 0 |
| Finite Greek badness | 0 |
| Joined external row has status_code 200 | 0 |
| Distinct PDF documents before median | 0 |
| Greek badness <= pool median | 0 |

The Greek-badness median is computed after all other required filters, including the joined 200 status and 20–600 pages, over distinct PDF documents. Here it is **undefined**. Year comes only from metadata date fields, preferring publication chronology over accession dates. Creator life dates and titles are not date sources. With no eligible documents, the pool year share and character-count-per-page statistics are **not applicable**. No extra date or character threshold was invented.

Wave 5: **7,341 scanned records with latin_percentage 20–50 inclusive** are retained in [wave5_candidates.json](wave5_candidates.json), including unmatched or non-200 rows with their status flagged. These candidates are not filtered by the Wave 4 >=80% Greek requirement; their quality fields and original metadata remain available for T25 selection. They have not been downloaded or read.

| Execution metric | Count |
| --- | ---: |
| Documents tried / downloaded / dead-link / skipped-size | 0 / 0 / 0 / 0 |
| Pages rendered / accepted / read | 0 / 0 / 0 |
| Lines / admitted / rejected / crops | 0 / 0 / 0 / 0 |
| Train / dev / test | 0 / 0 / 0 |
| Google reserved calls / USD | 0 / 0.00 |

Admission and class × split × repository statistics are marked **not_run** in [admission_summary.json](admission_summary.json); each class/split has zero lines. No hold-out has been assigned; no crop, compiled page or contact sheet was fabricated. T20 remains byte-identical. Reader, crop and compiled-image validation cannot run without pages. The USD 3.00 cap remains intact; the budget ledger and state contain zero reservations. No Vision calls and no credential checks.

Storage preflight: **1.19 GiB free** on the workspace volume at preparation time. No other wave artifacts were deleted. Free space must be checked again before executing a nonempty pool.

**139 offline tests passed** (T24 fixtures plus all T20 admission tests). Small Parquet/JSONL fixtures cover URL/edm joins, status handling, null scores, the median, every filter, mixed-script candidates, date extraction, deterministic stratification, repository caps and 20-document 15/5 hold-out assignment. Full-input offline validation independently replayed the join and selection. Main Git bookkeeping unchanged over preparation/publication: **True**. No Git mutation commands were issued.

To resume, supply real mojibake measurements or explicitly authorize a rule for missing scores. Any changed eligibility policy must be recorded before selection and before the first paid read. A nonempty pool still requires the download/gate/read/admission workflow; this preflight is not a completed Wave 4.

[Selection](SELECTION.md), [pool audit](pool_summary.json), [preflight](preflight.json), [validation](validation.json), [tests](tests.xml), [cost](cost_receipt.json), [Git audit](git_audit.json), [file inventory](inventory.json).

T24: blocked | docs: 0/0 | pages: 0/0/0 | lines: 0 | admitted: 0 | mono: 0 | cs: 0 | train: 0 | dev: 0 | test: 0 | usd: 0.00 | tests: 139 passed
