Template preview from the bound spec; this is not a completed dataset build.

## Source

The table gives non-null source fields per population from the retained complete book/source probe, not counts from this build. Populations overlap and must not be summed as release lines; a bounded smoke does not reproduce these full scans. Provider and item are measured separately, not as an unmeasured joint fraction. Exact counts and null reasons for canonical book IDs and every source field are in COVERAGE.json `book_bridge.measured_probe.populations`; `book_bridge.populations` reports this build separately.

| Population | Lines | Book ID | Provider | Item | source_url | catalogue_url |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s1 | 364,871 | 364,871/364,871 (100.00%) | 364,871/364,871 (100.00%) | 362,008/364,871 (99.22%) | 280,390/364,871 (76.85%) | 112,754/364,871 (30.90%) |
| v4 | 167,946 | 167,946/167,946 (100.00%) | 167,946/167,946 (100.00%) | 165,572/167,946 (98.59%) | 158,126/167,946 (94.15%) | 112,063/167,946 (66.73%) |
| old | 364,173 | 364,173/364,173 (100.00%) | 364,173/364,173 (100.00%) | 361,799/364,173 (99.35%) | 280,186/364,173 (76.94%) | 112,063/364,173 (30.77%) |
| census | 592,466 | 592,466/592,466 (100.00%) | 580,371/592,466 (97.96%) | 565,955/592,466 (95.53%) | 458,054/592,466 (77.31%) | 199,298/592,466 (33.64%) |
| harvest | 497,556 | 349,258/497,556 (70.19%) | 349,258/497,556 (70.19%) | 497,556/497,556 (100.00%) | 429,456/497,556 (86.31%) | 486,045/497,556 (97.69%) |
| seal04 | 2,690 | 2,690/2,690 (100.00%) | 2,690/2,690 (100.00%) | 2,608/2,690 (96.95%) | 2,195/2,690 (81.60%) | 1,408/2,690 (52.34%) |
| validation | 13,088 | 13,088/13,088 (100.00%) | 12,082/13,088 (92.31%) | 12,082/13,088 (92.31%) | 7,741/13,088 (59.15%) | 0/13,088 (0.00%) |
| synthetic | 203,693 | 0/203,693 (0.00%) | 0/203,693 (0.00%) | 0/203,693 (0.00%) | 0/203,693 (0.00%) | 0/203,693 (0.00%) |

book_id and canonical_book_id are canonical v2 IDs only on a unique typed match; native harvest IDs survive in source_book_id/source_canonical_book_id.

Native §3 field-8 fields take precedence over book enrichment; title is an explicit fallback for source_title. source_record_sha256 hashes the canonical emitted source-reference JSON; the native hash is retained inside it.

Keep native source, item, page, year and any other explicitly recorded source fields on matched and unmatched rows. S4h projects catalogue_url, manifest_url and source_url from provenance.public_links with those exact names. Provider and catalogue_reference come from the uniquely matched v2 book; source_url can be enriched from a unique registry alias/hash-bound sourcing record when absent natively. Unmatched rows retain all native projections but have null canonical IDs and no invented provider.

Known provider_item:<provider> aliases supply provider/item; catalogue_reference aliases remain literal and populate catalogue_url only if HTTP(S); source_url aliases remain literal. Hash-bound book_sources records supply recorded source, source_title, year, volume and source_url. Conflicting book values remain reasoned nulls. Page/page_number_convention are never borrowed from a book.

No measured book origin: all canonical book/source fields are null in this probe. Retain native source_dataset, source_doc_id/doc, text_source_locator/text_sha256 and other text-origin fields unchanged; factory IDs are not book or instrument evidence.

Probe evidence: `out/RELEASE_v0/probes/book-bridge-s4i-002/book_bridge.json`; SHA256 `2edd1eab00a5370ee939bef8d55d7749f165aff26991bf147768f7a08587a7ad`.

Probe evidence: `out/RELEASE_v0/probes/book-bridge-s4i-002/row_instruments.json`; SHA256 `ffee9415af696a4fe689f5efb8e60e5001d8548feebbb546b40585e3a4def5bd`.

Probe evidence: `out/RELEASE_v0/probes/book-bridge-s4i-002/SUMMARY.json`; SHA256 `61c55a86a1d2fc97a5b2fa562b90afd74702c94f86ac1db767e85345076cbec4`.

