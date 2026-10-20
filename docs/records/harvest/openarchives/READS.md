# T24c — Open Archives Wave 4

Completed 2026-10-15T08:57:41.217618+03:00. 89 downloaded documents from 173 tried; 1443 rendered / 917 accepted / 917 read pages; 30788 lines, 25606 admitted native crops.

The bounded overdraw is exhausted. The 130-document target remains 41 documents short; the approximate 1,500 accepted-page target remains 583 pages short. No draw beyond the authorized 173 candidates was made.

Selection uses pipeline metadata directly: download_success/ocr_success true; filter ok; is_empty false; Greek ≥80%; 20–600 metadata pages; direct http(s) PDF. Null quality scores pass; non-null mojibake is zero. Only measured Greek-badness scores enter the median. No external-table status or collection join controls eligibility.

The coordinator's 6,141 documents are reproduced **before** the measured-median filter. The literal median rule reduces this to 3071 in 20 metadata repositories; median 2.528004398236778. All 6141 pre-median candidates have measured scores. Seed 20264, cap 10, type × decade stratified draw of 173.

Informational URL coverage: 175973/175973 overall; 41675/41675 scanned. Cross-collection URL matches are allowed for status/source external_link lookup only. Metadata repository/title/year are recorded provenance and have not been independently verified against PDF contents. Licence: per-repository (recorded, unverified).

| Sequential filter | Rows/documents remaining |
| --- | ---: |
| metadata_rows | 175973 |
| download_success | 175973 |
| ocr_success | 41675 |
| filter_ok | 25723 |
| is_empty_false | 25372 |
| percentage_greek_ge80 | 14874 |
| mojibake_zero | 14874 |
| pages_20_600 | 6141 |
| finite_greek_badness | 6141 |
| direct_pdf_url | 6141 |
| unique_pre_median_documents | 6141 |
| greek_badness_le_median | 3071 |

| Repository | Pool | Downloaded |
| --- | ---: | ---: |
| Dione | 537 | 9 |
| IKEE_AUT | 821 | 1 |
| KEIED | 19 | 8 |
| Pandemos | 223 | 9 |
| anaktisis | 20 | 9 |
| apothesis | 25 | 9 |
| ariadne | 11 | 0 |
| deltion | 1 | 0 |
| dias | 73 | 0 |
| edulll | 69 | 0 |
| ekke | 19 | 0 |
| elocus | 182 | 0 |
| elstat | 72 | 0 |
| estia | 113 | 0 |
| helios | 77 | 0 |
| hellanicus | 189 | 9 |
| kallipos | 23 | 9 |
| ktisis | 24 | 9 |
| nemertes | 51 | 9 |
| ntua | 522 | 8 |

| Failed PDF URL host | Candidates |
| --- | ---: |
| dias.library.tuc.gr | 1 |
| dspace.lib.ntua.gr | 74 |
| ikee.lib.auth.gr | 8 |
| olympias.lib.uoi.gr | 1 |

Documents tried 173; downloaded 89; dead-link/invalid-PDF 84; skipped-size 0. Document target shortfall: 41 (bounded overdraw exhausted if nonzero). At most three download attempts per candidate. Initial page plus at most two physical neighbours; 12 accepted slots requested per document, no unbounded replacement. Accepted-page target shortfall: 583.

Images: nominal 200 dpi grey, long side ≤3500 px, PNG compression 6. Each page records native PDF points, native 200 dpi dimensions, render scale and effective dpi. All boxes and crops use the rendered frame. One PDF at a time; PDFs deleted after sampled render/gate; SHA/size/page-count and retention receipts kept. Embedded DocAI page image content is stripped before saving with content_stripped note; page PNG is the image of record. Free disk checked throughout; abort threshold 4 GiB.

Unchanged T20 admission SHA: `e32ba0429908bc405e0b2c2bb26d97cdec5f923733d708deaea018b65cb90a50`. Hold-out: 20 whole documents stratified by metadata repository, seed 20261015; 15 test / 5 dev, frozen before paid reads. O5 checks all existing wave hold-outs; 13 previous train rows excluded in the combined training overlay. 4 bad pages; 0 uncuttable crops.

| Class | Train | Dev | Test | Total |
| --- | ---: | ---: | ---: | ---: |
| greek_poly | 236 | 0 | 0 | 236 |
| greek_mono | 17214 | 921 | 3993 | 22128 |
| greek_latin_cs | 1646 | 105 | 503 | 2254 |
| latin | 701 | 57 | 230 | 988 |
| cyrillic | 0 | 0 | 0 | 0 |

| Repository | Class | Train | Dev | Test |
| --- | --- | ---: | ---: | ---: |
| Dione | greek_poly | 0 | 0 | 0 |
| Dione | greek_mono | 1713 | 0 | 625 |
| Dione | greek_latin_cs | 280 | 0 | 121 |
| Dione | latin | 112 | 0 | 24 |
| Dione | cyrillic | 0 | 0 | 0 |
| IKEE_AUT | greek_poly | 0 | 0 | 0 |
| IKEE_AUT | greek_mono | 0 | 0 | 210 |
| IKEE_AUT | greek_latin_cs | 0 | 0 | 18 |
| IKEE_AUT | latin | 0 | 0 | 33 |
| IKEE_AUT | cyrillic | 0 | 0 | 0 |
| KEIED | greek_poly | 0 | 0 | 0 |
| KEIED | greek_mono | 1941 | 177 | 0 |
| KEIED | greek_latin_cs | 77 | 18 | 0 |
| KEIED | latin | 35 | 14 | 0 |
| KEIED | cyrillic | 0 | 0 | 0 |
| Pandemos | greek_poly | 185 | 0 | 0 |
| Pandemos | greek_mono | 2040 | 246 | 0 |
| Pandemos | greek_latin_cs | 139 | 56 | 0 |
| Pandemos | latin | 89 | 23 | 0 |
| Pandemos | cyrillic | 0 | 0 | 0 |
| anaktisis | greek_poly | 0 | 0 | 0 |
| anaktisis | greek_mono | 1904 | 190 | 427 |
| anaktisis | greek_latin_cs | 143 | 22 | 12 |
| anaktisis | latin | 52 | 1 | 1 |
| anaktisis | cyrillic | 0 | 0 | 0 |
| apothesis | greek_poly | 0 | 0 | 0 |
| apothesis | greek_mono | 1464 | 0 | 496 |
| apothesis | greek_latin_cs | 160 | 0 | 42 |
| apothesis | latin | 59 | 0 | 27 |
| apothesis | cyrillic | 0 | 0 | 0 |
| hellanicus | greek_poly | 0 | 0 | 0 |
| hellanicus | greek_mono | 1847 | 0 | 661 |
| hellanicus | greek_latin_cs | 145 | 0 | 79 |
| hellanicus | latin | 96 | 0 | 48 |
| hellanicus | cyrillic | 0 | 0 | 0 |
| kallipos | greek_poly | 51 | 0 | 0 |
| kallipos | greek_mono | 1919 | 0 | 632 |
| kallipos | greek_latin_cs | 150 | 0 | 98 |
| kallipos | latin | 86 | 0 | 27 |
| kallipos | cyrillic | 0 | 0 | 0 |
| ktisis | greek_poly | 0 | 0 | 0 |
| ktisis | greek_mono | 1813 | 0 | 489 |
| ktisis | greek_latin_cs | 193 | 0 | 59 |
| ktisis | latin | 41 | 0 | 41 |
| ktisis | cyrillic | 0 | 0 | 0 |
| nemertes | greek_poly | 0 | 0 | 0 |
| nemertes | greek_mono | 1427 | 0 | 453 |
| nemertes | greek_latin_cs | 126 | 0 | 74 |
| nemertes | latin | 62 | 0 | 29 |
| nemertes | cyrillic | 0 | 0 | 0 |
| ntua | greek_poly | 0 | 0 | 0 |
| ntua | greek_mono | 1146 | 308 | 0 |
| ntua | greek_latin_cs | 233 | 9 | 0 |
| ntua | latin | 69 | 19 | 0 |
| ntua | cyrillic | 0 | 0 | 0 |

| Reason (overlapping) | Lines |
| --- | ---: |
| short_line | 4440 |
| low_confidence | 856 |
| tall_box | 255 |
| symbol_heavy | 3361 |
| foreign_script | 12 |
| mixed_word | 93 |
| bad_page | 235 |
| label_in_holdout | 42 |
| crop_geometry | 0 |

Google: USD 1.3755 reserved at USD 0.0015/page, cap USD 3.00; 917 unique page-SHA reservations, zero Vision calls. Reservations include failed/ambiguous attempts; this is not an invoice readback. No automatic Google retries.

Validation: 269 offline tests passed; 25606 crops checked against source pixels; 917 compiled rasters replayed; offline cache reuse added no calls/reservations. Minimum logged acquisition same-host request gap 1.0498130321502686 s. Git metadata unchanged: True; no Git write operations. All four source tables and the 7,341 Wave 5 candidates retain their pre-run hashes.

One extra standalone connection probe was made to an already failed IKEE HTTPS endpoint; it returned RemoteDisconnected and downloaded zero PDF bytes. This exceeded the intended three-attempt boundary for that endpoint by one diagnostic request; it is recorded in [connection_probe.json](connection_probe.json). Subsequent acquisition starts are journalled across resume.

Read failures: 0 empty / 0 no-line / 0 lost-geometry pages. Sample visual checks covered 12 crops across four populated classes, a compiled page, and all four bad-page headings. One terminal hyphen extends beyond the DocAI bbox/crop and is omitted in the label; it is retained under unchanged T20 rules. A concrete metadata/PDF-source mismatch is also recorded in [visual spot checks](visual_qa.json).

Automatic admission and raster checks do not establish transcription accuracy or glyph ownership. ocr_success records pipeline routing and does not certify a physical scan. Contact sheets and compiled pages are available for owner review; no owner acceptance is claimed.

[Selection](SELECTION.md) · [records](records.jsonl) · [admitted](admitted.jsonl) · [rejected](rejected.jsonl) · [hold-outs](holdout_books.json) · [summary](admission_summary.json) · [combined training pool](train_pool.jsonl) · [validation](validation.json) · [inventory](inventory.json)

T24c: done | docs: 89/173 | pages: 1443/917/917 | lines: 30788 | admitted: 25606 | mono: 22128 | cs: 2254 | train: 19797 | dev: 1083 | test: 4726 | usd: 1.38 | tests: 269 passed
