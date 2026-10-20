# T24b — Open Archives Wave 4 rerun

**Blocked before downloads; harvest not complete.** The null-score fix yields 1,352 eligible documents, all in 2 repositories. The <=10-per-repository rule permits only 20 documents, so neither the 173-candidate overdraw nor the 130-document sample is feasible. No PDF/network/ADC requests or paid reads were made.

The 15 October coordinator correction is applied without replacing nulls by zero: null mojibake passes; null Greek badness passes and is excluded from the median. Non-null mojibake must equal zero; measured Greek badness must not exceed the median **2.7398518953617668**, computed over 2,703 distinct documents after all other filters, including the joined 200 status. T20 admission remains byte-identical.

Final inputs: 175,973 metadata rows; 561,271 external-PDF rows; 830,313 all-links rows; 140 collections. No partial metadata file exists. All four input SHA-256 values were checked before/after preparation and in independent validation.

Join coverage: **64,340/175,973 (36.56%)** overall; **10,658/41,675 (25.57%)** scanned. 63,000 distinct external rows matched; 53 metadata rows had multiple matches. Matches use (collection_slug, canonical full PDF URL); explicit edm_url fallback added no matches. Queries and reserved escapes retain identity; no filename, host, title or cross-collection fallback was used.

| Sequential filter | Documents / rows remaining |
| --- | ---: |
| All metadata rows | 175,973 |
| ocr_success is true | 41,675 |
| filter == ok | 25,723 |
| is_empty is false | 25,372 |
| percentage_greek >= 80 | 14,874 |
| Mojibake zero OR null (T24b) | 14,874 |
| Page count 20–600 | 6,141 |
| Greek badness finite OR null (T24b) | 6,141 |
| Joined external row has status 200 | 2,703 |
| Distinct PDF documents before median | 2,703 |
| Measured Greek badness <= median OR null | 1,352 |

| Repository | Eligible documents | Maximum at cap 10 |
| --- | ---: | ---: |
| Dione | 570 | 10 |
| IKEE_AUT | 782 | 10 |

Year coverage: 1,352/1,352 (100.00%). Years come only from metadata date fields, preferring publication chronology over accession dates. No title/creator-year inference or extra chronology/character threshold was introduced.

The expected approximately 6,000 pool is approached **before** the required join: 6,141 documents pass quality/page filters, but 3,438 cannot join. For 3,438 of those, the exact PDF URL exists in external_pdfs under a different collection_slug. These are input identity inconsistencies; assuming only the slug is wrong would attach unverified metadata, years, quality scores and repository labels to PDFs. There are 0 explicit EDM fields in this pre-join population. Examples and counts per repository are in [identity_audit.json](identity_audit.json).

Wave 5: 7,341 scanned latin_percentage 20–50 records remain in [wave5_candidates.json](wave5_candidates.json), with original metadata and join/status flags. Their bytes are unchanged from the T24 file consumed by T25. That retention does not certify upstream PDF/metadata identity.

| Execution metric | Count |
| --- | ---: |
| Documents tried / downloaded / dead-link / skipped-size | 0 / 0 / 0 / 0 |
| Pages rendered / accepted / read | 0 / 0 / 0 |
| Lines / admitted / rejected / crops | 0 / 0 / 0 / 0 |
| Train / dev / test | 0 / 0 / 0 |
| Google reservations / USD | 0 / 0.00 |

The admission summary is explicitly `not_run`, with zero class × split × repository counts. No hold-out, compiled pages, crops or contact sheets were fabricated. All existing hold-outs remain unchanged. The USD 3.00 ledger and state have no reservations; zero Vision calls.

Disk: 16.02 GiB free at publication. There are no PDFs, rendered images or raw responses for this wave. The required 3,500-pixel cap, scale/native-size receipt, PNG compression 6, pre-save response image stripping, one-PDF lifetime and <4 GB graceful abort remain execution requirements; they have not been exercised. No acquisition/read runner is claimed as complete.

**144 offline tests passed**, covering the reused join, corrected null/finite filters, measured-only median, deterministic type/decade/repository stratification, repository-cap infeasibility, 20-document 15/5 hold-out, cross-collection mismatch diagnostics and unchanged T20 admission. Full-input offline validation independently recomputed the join/pool/draw and verified empty execution artifacts. Git bookkeeping unchanged during T24b: **True**; no Git commands or writes issued. Native-image/crop verification is not applicable. The original T24 report and receipts are retained under [t24_preflight/](t24_preflight/READS.md).

**Required to continue:** corrected metadata-to-PDF identities or an explicit document-to-EDM mapping that supplies enough qualifying repositories. A cross-collection URL fallback or higher per-collection cap would change the brief and has not been applied.

[Selection](SELECTION.md), [pool](pool_summary.json), [preflight](preflight.json), [identity audit](identity_audit.json), [validation](validation.json), [tests](tests.xml), [cost](cost_receipt.json), [Git audit](git_audit.json), [inventory](inventory.json).

T24b: blocked | docs: 0/0 | pages: 0/0/0 | lines: 0 | admitted: 0 | mono: 0 | cs: 0 | train: 0 | dev: 0 | test: 0 | usd: 0.00 | tests: 144 passed
