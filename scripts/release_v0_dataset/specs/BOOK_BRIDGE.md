# REL0-S4j book bridge — 28 October 2026

Decision: **partial, measured**. Both retained S4i-002 item reports have
`complete=true`, `complete_metadata_scan=true`, `registry_inputs_stable=true`
and no missing sources. Their producer intentionally leaves `resolved=false`
and its pending decision for review; this measured spec decision supersedes
that producer placeholder. The coordinator supplied Clariden job **3785164
COMPLETED**, code **rel0-s4i-20261028**, and registry-v2 SHA256SUMS verification.
Those remote statements are supplied evidence; no remote operation ran in S4j.
These are overlapping source observations, not disjoint release-line counts.
No full dataset build or independent release acceptance is established here.

## Bound evidence

- `out/RELEASE_v0/probes/book-bridge-s4i-002/book_bridge.json` — 289,564 bytes; SHA256 `2edd1eab00a5370ee939bef8d55d7749f165aff26991bf147768f7a08587a7ad`.
- `out/RELEASE_v0/probes/book-bridge-s4i-002/row_instruments.json` — 289,568 bytes; SHA256 `ffee9415af696a4fe689f5efb8e60e5001d8548feebbb546b40585e3a4def5bd`.
- `out/RELEASE_v0/probes/book-bridge-s4i-002/SUMMARY.json` — 13,951 bytes; SHA256 `61c55a86a1d2fc97a5b2fa562b90afd74702c94f86ac1db767e85345076cbec4`.

## Identity rule

The canonical input is `docs/programme_20261019/registry/book_registry/v2/`.
`book_id` and `canonical_book_id` in emitted rows both mean its canonical ID;
native book IDs survive in `source_book_id` / `source_canonical_book_id`.
The registry Parquet SHA is attached to every result. The 310-book harvest
registry is no longer the canonical book table.

All matches compare exact namespace/value pairs recorded in `aliases`.
`build_book_registry.py:48-49` defines `prefix`: remove the first
`--s<digits>`, `--p<digits>`, `--n<digits>` or `-p<digits>` and its suffix.
Lines 101-106, 115-125, 342-347, 385-386 and 402-403 deliberately register book
prefixes and document memberships. This permits book identity by equality to
a declared `line_id_prefix`; it never permits string `startswith` matching or
instrument membership by prefix. Titles, crop paths, crop hashes, descriptive
`catalogue_reference` and `page_pdf_sha256` aliases do not establish identity.

The bridge unions every canonical candidate from every supported native key.
Exactly one gives a book; more than one gives **null**, `ambiguous` and the
candidate IDs. A conflicting second selector cannot be overridden by a
preferred alias. No typed key gives `no_key`; typed keys with no match give
`unmatched`. Coverage includes all four outcomes. Joined release rows also
union candidates from their exact source observations, including old→S1.

| Population | Exact typed path |
| --- | --- |
| S1 | `row_id → registry.prefix → line_id_prefix → book_id`. |
| v4 | Native `edition_id → edition_id / seal04_edition_hash / line_id_prefix`; independently `row_id → registry.prefix → line_id_prefix`. The 64-character edition hash is already an alias; no new hash is computed. |
| old | `edition_id → edition_id / seal04_edition_hash / line_id_prefix`; `source_doc_id → v2_book_id / edition_id / line_id_prefix`; independently `line_id → registry.prefix → line_id_prefix`. Exact `old.line_id = s1.row_id` maps its source evidence to the existing tuple, using the S4h unique S1 keyset. |
| census | `binding.id → registry.prefix → line_id_prefix`; no source book key is assumed. |
| harvest | `book_id` / `canonical_book_id → v2_book_id / edition_id / line_id_prefix`; `edition_id → edition_id / seal04_edition_hash / line_id_prefix`; original `id → registry.prefix → line_id_prefix`. Native harvest IDs are not asserted to be canonical v2 IDs. |
| seal04 | Only original `benchmark_v02_{dev,test}.jsonl`, not receipts/readouts: `edition_id` as above; `id → registry.prefix → line_id_prefix`. Native `(parent_id,id)` links to the existing census tuple. |
| validation | Exact original `line_id → registry.prefix → line_id_prefix`; S4h measured `validation.line_id = census.binding.id` supplies the existing row mapping. No factory-ID parsing. |
| synthetic | Only real-origin `source_doc_id` / `doc` / native book/edition keys as above, or an explicitly recorded `original_line_id`. The synthetic `line_id` and dataset name never imply a book. Missing real origin stays null. |

Additional native, typed evidence is usable in each population: `book_key →
line_id_prefix`, full `pdf_sha256` / `full_pdf_sha256 → pdf_sha256`,
`ia_identifier → ia_identifier`, `nlg_catalogue → nlg_catalogue`, and explicit
`(provider,item/provider_item_id) → provider_item:<provider>`. Explicit
`source_url` / `manifest_url` compare against the registry's `source_url`
normalization (`build_book_registry.py:76-84`); this emits no constructed URL.
Missing namespaces/values have no fallback identity. Hash aliases compare
literally; even the verified example `sha256("bsb_poly1850--027215cc6d2a7e8a")`
is resolved using its already recorded `edition_id`, not a new hashing rule.

## Bibliography and instruments

Provider and item come from known `provider_item:<provider>` aliases; `unknown`
is not a provider. `catalogue_reference` is retained verbatim, and an already
recorded HTTP(S) reference may also populate `catalogue_url`. Registry
`source_url` aliases are retained verbatim (the registry drops schemes). No
URL template is expanded. Native row public links/pages retain their exact
values. Multiple book source values give a reasoned null, with candidates and
field evidence retained; a row's own page is never borrowed from another
page of its book. No page number or convention is parsed from a line/crop ID.

`prepare_book_sources.py` builds `book-sources-v2.jsonl` only from
`identity_provenance` references with byte-identical repo copies under
`docs/records/harvest/`. It imports the pinned registry alias definition,
requires one exact alias match within that source's cited books, and retains
original provenance, file SHA and record ordinal. Its `BOOK_SOURCES_RECEIPT.json`
records inspected/missing/different inputs. These portable records are selected
and hash-locked, then exported as `tables/book_sources.parquet`. Per-row field
evidence points to their stable source record IDs, not a repeated full manifest.
`source_record_sha256` hashes the emitted canonical JSON source-reference record;
any native source-record hash is retained separately inside that record.

`row_instruments.parquet` contains `row_id`, `kind`, `list_name`, `list_sha256`,
`declaration_path`: the executable relation replaces S4h's historical null.
For the original-ID selectors in the table, equality joins to `row_id` only.
Kinds `lqb` and `release_exclusion` map to row flags `lqb_row` and
`release_excluded_row`. All list memberships survive, including overlapping
lists. A neighbouring line in the same book gains no flag. Synthetic factory
IDs have no original membership unless an explicit original mapping exists;
without an original ID the flags are null with a reason, counted as
`instrument_original_id_unknown`, rather than asserted absent.
The instrument relation's SHA accompanies the row. Native declarations/list
names and hashes remain visible in the exported relation.

## Measured population coverage

| Population | Rows | Book match | no_key | Unmatched | Ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: |
| s1 | 364,871 | 364,871 | 0 | 0 | 0 |
| v4 | 167,946 | 167,946 | 0 | 0 | 0 |
| old | 364,173 | 364,173 | 0 | 0 | 0 |
| census | 592,466 | 592,466 | 0 | 0 | 0 |
| harvest | 497,556 | 349,258 | 0 | 148,298 | 0 |
| seal04 | 2,690 | 2,690 | 0 | 0 | 0 |
| validation | 13,088 | 13,088 | 0 | 0 | 0 |
| synthetic | 203,693 | 0 | 9,859 | 193,834 | 0 |

## Source projection

book_id and canonical_book_id are canonical v2 IDs only on a unique typed match; native harvest IDs survive in source_book_id/source_canonical_book_id.

Native §3 field-8 fields take precedence over book enrichment; title is an explicit fallback for source_title. source_record_sha256 hashes the canonical emitted source-reference JSON; the native hash is retained inside it.

Keep native source, item, page, year and any other explicitly recorded source fields on matched and unmatched rows. S4h projects catalogue_url, manifest_url and source_url from provenance.public_links with those exact names. Provider and catalogue_reference come from the uniquely matched v2 book; source_url can be enriched from a unique registry alias/hash-bound sourcing record when absent natively. Unmatched rows retain all native projections but have null canonical IDs and no invented provider.

Known provider_item:<provider> aliases supply provider/item; catalogue_reference aliases remain literal and populate catalogue_url only if HTTP(S); source_url aliases remain literal. Hash-bound book_sources records supply recorded source, source_title, year, volume and source_url. Conflicting book values remain reasoned nulls. Page/page_number_convention are never borrowed from a book.

No measured book origin: all canonical book/source fields are null in this probe. Retain native source_dataset, source_doc_id/doc, text_source_locator/text_sha256 and other text-origin fields unchanged; factory IDs are not book or instrument evidence.

S4h native harvest source_url coverage remains 201,000/497,556; after literal book-source enrichment the measured total is 429,456/497,556. Native catalogue_url remains 486,045/497,556 and manifest_url 424,376/497,556. A source link is not proof of a unique book match. Every missing field keeps its measured reason.

## Exact row instruments

| Population | Rows | Instrument rows | Memberships | lqb_row | release_excluded_row | Original ID unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s1 | 364,871 | 572 | 572 | 3 | 569 | 0 |
| v4 | 167,946 | 569 | 569 | 0 | 569 | 0 |
| old | 364,173 | 572 | 572 | 3 | 569 | 0 |
| census | 592,466 | 3,650 | 3,670 | 1,524 | 2,140 | 0 |
| harvest | 497,556 | 0 | 0 | 0 | 0 | 0 |
| seal04 | 2,690 | 4 | 4 | 0 | 4 | 0 |
| validation | 13,088 | 130 | 130 | 0 | 130 | 0 |
| synthetic | 203,693 | 0 | 0 | 0 | 0 | 203,693 |

The pinned relation contains **5,803 memberships / 5,383 distinct original IDs**. Multiple memberships survive. Synthetic has no known original mapping on all 203,693 observations, so flags remain null; zero observed memberships does not mean known absence. Counts overlap across populations and must not be added.

## Every §3 field-8 field and canonical ID

The values below are copied exactly from `populations.<p>.source_fields`, also stored in `source-spec-001.json` and published under COVERAGE.json `book_bridge.measured_probe.populations`. Runtime source-observation counts remain under `book_bridge.populations`; smoke counts are separate.

| Population | Field | Non-null / rows | Null | Measured null reasons |
| --- | --- | ---: | ---: | --- |
| s1 | `book_id` | 364,871/364,871 | 0 | none |
| s1 | `canonical_book_id` | 364,871/364,871 | 0 | none |
| s1 | `catalogue_reference` | 112,754/364,871 | 252,117 | not recorded for this exact row/book in registry or hash-bound sourcing records: 252,117 |
| s1 | `catalogue_url` | 112,754/364,871 | 252,117 | not recorded for this exact row/book in registry or hash-bound sourcing records: 252,117 |
| s1 | `edition` | 0/364,871 | 364,871 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,871 |
| s1 | `item` | 362,008/364,871 | 2,863 | multiple recorded book source values; inspect book_source_candidates_json: 2,863 |
| s1 | `manifest_url` | 0/364,871 | 364,871 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,871 |
| s1 | `page` | 0/364,871 | 364,871 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,871 |
| s1 | `page_number_convention` | 0/364,871 | 364,871 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,871 |
| s1 | `provider` | 364,871/364,871 | 0 | none |
| s1 | `source` | 364,871/364,871 | 0 | none |
| s1 | `source_record_sha256` | 364,871/364,871 | 0 | none |
| s1 | `source_title` | 150,062/364,871 | 214,809 | not recorded for this exact row/book in registry or hash-bound sourcing records: 214,809 |
| s1 | `source_url` | 280,390/364,871 | 84,481 | multiple recorded book source values; inspect book_source_candidates_json: 80,261; not recorded for this exact row/book in registry or hash-bound sourcing records: 4,220 |
| s1 | `volume` | 41,879/364,871 | 322,992 | multiple recorded book source values; inspect book_source_candidates_json: 1,545; not recorded for this exact row/book in registry or hash-bound sourcing records: 321,447 |
| s1 | `year` | 148,878/364,871 | 215,993 | not recorded for this exact row/book in registry or hash-bound sourcing records: 215,993 |
| v4 | `book_id` | 167,946/167,946 | 0 | none |
| v4 | `canonical_book_id` | 167,946/167,946 | 0 | none |
| v4 | `catalogue_reference` | 112,063/167,946 | 55,883 | not recorded for this exact row/book in registry or hash-bound sourcing records: 55,883 |
| v4 | `catalogue_url` | 112,063/167,946 | 55,883 | not recorded for this exact row/book in registry or hash-bound sourcing records: 55,883 |
| v4 | `edition` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| v4 | `item` | 165,572/167,946 | 2,374 | multiple recorded book source values; inspect book_source_candidates_json: 2,374 |
| v4 | `manifest_url` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| v4 | `page` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| v4 | `page_number_convention` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| v4 | `provider` | 167,946/167,946 | 0 | none |
| v4 | `source` | 167,946/167,946 | 0 | none |
| v4 | `source_record_sha256` | 167,946/167,946 | 0 | none |
| v4 | `source_title` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| v4 | `source_url` | 158,126/167,946 | 9,820 | multiple recorded book source values; inspect book_source_candidates_json: 5,600; not recorded for this exact row/book in registry or hash-bound sourcing records: 4,220 |
| v4 | `volume` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| v4 | `year` | 0/167,946 | 167,946 | not recorded for this exact row/book in registry or hash-bound sourcing records: 167,946 |
| old | `book_id` | 364,173/364,173 | 0 | none |
| old | `canonical_book_id` | 364,173/364,173 | 0 | none |
| old | `catalogue_reference` | 112,063/364,173 | 252,110 | not recorded for this exact row/book in registry or hash-bound sourcing records: 252,110 |
| old | `catalogue_url` | 112,063/364,173 | 252,110 | not recorded for this exact row/book in registry or hash-bound sourcing records: 252,110 |
| old | `edition` | 0/364,173 | 364,173 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,173 |
| old | `item` | 361,799/364,173 | 2,374 | multiple recorded book source values; inspect book_source_candidates_json: 2,374 |
| old | `manifest_url` | 0/364,173 | 364,173 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,173 |
| old | `page` | 0/364,173 | 364,173 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,173 |
| old | `page_number_convention` | 0/364,173 | 364,173 | not recorded for this exact row/book in registry or hash-bound sourcing records: 364,173 |
| old | `provider` | 364,173/364,173 | 0 | none |
| old | `source` | 150,055/364,173 | 214,118 | not recorded for this exact row/book in registry or hash-bound sourcing records: 214,118 |
| old | `source_record_sha256` | 364,173/364,173 | 0 | none |
| old | `source_title` | 150,055/364,173 | 214,118 | not recorded for this exact row/book in registry or hash-bound sourcing records: 214,118 |
| old | `source_url` | 280,186/364,173 | 83,987 | multiple recorded book source values; inspect book_source_candidates_json: 79,767; not recorded for this exact row/book in registry or hash-bound sourcing records: 4,220 |
| old | `volume` | 41,879/364,173 | 322,294 | multiple recorded book source values; inspect book_source_candidates_json: 1,545; not recorded for this exact row/book in registry or hash-bound sourcing records: 320,749 |
| old | `year` | 148,871/364,173 | 215,302 | not recorded for this exact row/book in registry or hash-bound sourcing records: 215,302 |
| census | `book_id` | 592,466/592,466 | 0 | none |
| census | `canonical_book_id` | 592,466/592,466 | 0 | none |
| census | `catalogue_reference` | 199,298/592,466 | 393,168 | not recorded for this exact row/book in registry or hash-bound sourcing records: 393,168 |
| census | `catalogue_url` | 199,298/592,466 | 393,168 | not recorded for this exact row/book in registry or hash-bound sourcing records: 393,168 |
| census | `edition` | 0/592,466 | 592,466 | not recorded for this exact row/book in registry or hash-bound sourcing records: 592,466 |
| census | `item` | 565,955/592,466 | 26,511 | multiple recorded book source values; inspect book_source_candidates_json: 14,416; not recorded for this exact row/book in registry or hash-bound sourcing records: 12,095 |
| census | `manifest_url` | 0/592,466 | 592,466 | not recorded for this exact row/book in registry or hash-bound sourcing records: 592,466 |
| census | `page` | 0/592,466 | 592,466 | not recorded for this exact row/book in registry or hash-bound sourcing records: 592,466 |
| census | `page_number_convention` | 0/592,466 | 592,466 | not recorded for this exact row/book in registry or hash-bound sourcing records: 592,466 |
| census | `provider` | 580,371/592,466 | 12,095 | not recorded for this exact row/book in registry or hash-bound sourcing records: 12,095 |
| census | `source` | 213,774/592,466 | 378,692 | not recorded for this exact row/book in registry or hash-bound sourcing records: 378,692 |
| census | `source_record_sha256` | 592,466/592,466 | 0 | none |
| census | `source_title` | 213,774/592,466 | 378,692 | not recorded for this exact row/book in registry or hash-bound sourcing records: 378,692 |
| census | `source_url` | 458,054/592,466 | 134,412 | multiple recorded book source values; inspect book_source_candidates_json: 129,056; not recorded for this exact row/book in registry or hash-bound sourcing records: 5,356 |
| census | `volume` | 54,218/592,466 | 538,248 | multiple recorded book source values; inspect book_source_candidates_json: 1,592; not recorded for this exact row/book in registry or hash-bound sourcing records: 536,656 |
| census | `year` | 212,204/592,466 | 380,262 | not recorded for this exact row/book in registry or hash-bound sourcing records: 380,262 |
| harvest | `book_id` | 349,258/497,556 | 148,298 | book identity unmatched: 148,298 |
| harvest | `canonical_book_id` | 349,258/497,556 | 148,298 | book identity unmatched: 148,298 |
| harvest | `catalogue_reference` | 349,258/497,556 | 148,298 | book identity unmatched: 148,298 |
| harvest | `catalogue_url` | 486,045/497,556 | 11,511 | book identity unmatched: 11,511 |
| harvest | `edition` | 0/497,556 | 497,556 | book identity unmatched: 148,298; not recorded for this exact row/book in registry or hash-bound sourcing records: 349,258 |
| harvest | `item` | 497,556/497,556 | 0 | none |
| harvest | `manifest_url` | 424,376/497,556 | 73,180 | book identity unmatched: 21,302; not recorded for this exact row/book in registry or hash-bound sourcing records: 51,878 |
| harvest | `page` | 497,556/497,556 | 0 | none |
| harvest | `page_number_convention` | 0/497,556 | 497,556 | book identity unmatched: 148,298; not recorded for this exact row/book in registry or hash-bound sourcing records: 349,258 |
| harvest | `provider` | 349,258/497,556 | 148,298 | book identity unmatched: 148,298 |
| harvest | `source` | 497,556/497,556 | 0 | none |
| harvest | `source_record_sha256` | 497,556/497,556 | 0 | none |
| harvest | `source_title` | 0/497,556 | 497,556 | book identity unmatched: 148,298; not recorded for this exact row/book in registry or hash-bound sourcing records: 349,258 |
| harvest | `source_url` | 429,456/497,556 | 68,100 | book identity unmatched: 51,426; multiple recorded book source values; inspect book_source_candidates_json: 4,945; not recorded for this exact row/book in registry or hash-bound sourcing records: 11,729 |
| harvest | `volume` | 0/497,556 | 497,556 | book identity unmatched: 148,298; not recorded for this exact row/book in registry or hash-bound sourcing records: 349,258 |
| harvest | `year` | 497,503/497,556 | 53 | not recorded for this exact row/book in registry or hash-bound sourcing records: 53 |
| seal04 | `book_id` | 2,690/2,690 | 0 | none |
| seal04 | `canonical_book_id` | 2,690/2,690 | 0 | none |
| seal04 | `catalogue_reference` | 1,408/2,690 | 1,282 | not recorded for this exact row/book in registry or hash-bound sourcing records: 1,282 |
| seal04 | `catalogue_url` | 1,408/2,690 | 1,282 | not recorded for this exact row/book in registry or hash-bound sourcing records: 1,282 |
| seal04 | `edition` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| seal04 | `item` | 2,608/2,690 | 82 | multiple recorded book source values; inspect book_source_candidates_json: 82 |
| seal04 | `manifest_url` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| seal04 | `page` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| seal04 | `page_number_convention` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| seal04 | `provider` | 2,690/2,690 | 0 | none |
| seal04 | `source` | 2,690/2,690 | 0 | none |
| seal04 | `source_record_sha256` | 2,690/2,690 | 0 | none |
| seal04 | `source_title` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| seal04 | `source_url` | 2,195/2,690 | 495 | multiple recorded book source values; inspect book_source_candidates_json: 271; not recorded for this exact row/book in registry or hash-bound sourcing records: 224 |
| seal04 | `volume` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| seal04 | `year` | 0/2,690 | 2,690 | not recorded for this exact row/book in registry or hash-bound sourcing records: 2,690 |
| validation | `book_id` | 13,088/13,088 | 0 | none |
| validation | `canonical_book_id` | 13,088/13,088 | 0 | none |
| validation | `catalogue_reference` | 0/13,088 | 13,088 | not recorded for this exact row/book in registry or hash-bound sourcing records: 13,088 |
| validation | `catalogue_url` | 0/13,088 | 13,088 | not recorded for this exact row/book in registry or hash-bound sourcing records: 13,088 |
| validation | `edition` | 0/13,088 | 13,088 | not recorded for this exact row/book in registry or hash-bound sourcing records: 13,088 |
| validation | `item` | 12,082/13,088 | 1,006 | not recorded for this exact row/book in registry or hash-bound sourcing records: 1,006 |
| validation | `manifest_url` | 0/13,088 | 13,088 | not recorded for this exact row/book in registry or hash-bound sourcing records: 13,088 |
| validation | `page` | 0/13,088 | 13,088 | not recorded for this exact row/book in registry or hash-bound sourcing records: 13,088 |
| validation | `page_number_convention` | 0/13,088 | 13,088 | not recorded for this exact row/book in registry or hash-bound sourcing records: 13,088 |
| validation | `provider` | 12,082/13,088 | 1,006 | not recorded for this exact row/book in registry or hash-bound sourcing records: 1,006 |
| validation | `source` | 9,963/13,088 | 3,125 | not recorded for this exact row/book in registry or hash-bound sourcing records: 3,125 |
| validation | `source_record_sha256` | 13,088/13,088 | 0 | none |
| validation | `source_title` | 9,963/13,088 | 3,125 | not recorded for this exact row/book in registry or hash-bound sourcing records: 3,125 |
| validation | `source_url` | 7,741/13,088 | 5,347 | multiple recorded book source values; inspect book_source_candidates_json: 5,347 |
| validation | `volume` | 2,336/13,088 | 10,752 | not recorded for this exact row/book in registry or hash-bound sourcing records: 10,752 |
| validation | `year` | 9,963/13,088 | 3,125 | not recorded for this exact row/book in registry or hash-bound sourcing records: 3,125 |
| synthetic | `book_id` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `canonical_book_id` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `catalogue_reference` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `catalogue_url` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `edition` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `item` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `manifest_url` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `page` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `page_number_convention` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `provider` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `source` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `source_record_sha256` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `source_title` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `source_url` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `volume` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
| synthetic | `year` | 0/203,693 | 203,693 | book identity no_key: 9,859; book identity unmatched: 193,834 |
