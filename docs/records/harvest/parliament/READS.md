# T23 — Wave 3 Parliament proceedings: page reads and admitted crops

**72 selected volumes; 1153 pages rendered / 705 accepted / 690 read. 95,438 lines; 85,042 admitted native crops.**

**Scope shortfall:** the supplied 76,246-row catalogue has eligible proceedings in 18 of 26 requested years. Missing years: 1990, 1991, 1992, 1993, 1997, 1998, 1999, 2000. Four volumes per available year gives 72 rather than 104; the absent 32 volumes were not replaced from other years. Complete live `title:YYYY` search results also returned no eligible records for these eight years; this checks dated titles, not a claim that the repository can never acquire those proceedings. The run proceeds on the available authorized source scope, with this limitation explicit. [Probe](missing_year_probe.json).

Volumes selected/resolved/downloaded/skipped(size)/failed: **72 / 77 / 77 / 0 / 1**. 5 downloaded candidates were too short for twelve distinct sampled pages. These counts include replaced candidates in resolved/downloaded; the 72 final selections each have an ORIGINAL PDF receipt. All PDFs and partial downloads from this run were deleted after sampling; PDF SHA-256, byte count, bitstream checksum and decoded page count remain. [Selection table](SELECTION.md), [candidate dispositions](selection_summary.json), [volume receipts](volumes/).

Selection uses seed 20263, four chronological session strata per year, with deterministic shuffled backups within each stratum. The raw rights must contain CC BY 4.0; any NC/ND declaration is excluded. Each source URL is the catalogue handle, and attribution is `Hellenic Parliament Library; <title>`. Source declaration is retained verbatim.

Each PDF is streamed into `<uuid>.pdf` under the 250,000,000-byte bound. Twelve pages span inclusive 8–95% positions, with independently seeded 0–2 offsets and unique page identities. A failed slot gets at most two following physical neighbours (original plus at most two retries), without crossing the 95% boundary or borrowing another slot’s page. Short session PDFs have few unreserved neighbours. [Slots](slots.json) records every attempt and exhausted slot.

Rendering is pypdfium2, 200 dpi grayscale L PNG. Frozen gate SHA `55c2efd673ce5bca8492e4f5a3fda60ec6c6f26f1def1ca3f265c4459ad8a0e1`; unchanged T16 photometric guards and limits. Two-column handling is inherited exactly, including rejection of `more_than_two_columns`; no threshold relaxation. No owner look during this run, as recorded in the collection execution state.

| Page-gate reason | Pages (overlapping) |
| --- | ---: |
| bad_darkest_percentile_contrast | 1 |
| bad_faintness_proxy | 1 |
| bad_ink_fraction | 1 |
| bend_scout | 137 |
| more_than_two_columns | 10 |
| non_body_page | 11 |
| rotated | 13 |
| table | 315 |

DocAI uses the unchanged T19 EU processor/version, Greek hint, symbol setting and ADC binding. The same T21 raw/cache SHA and binding checks apply. T19 native line layouts, inverse transforms, symbol-scoped mean/min confidence and line flags remain unchanged. T20 admission is byte-identical, including bad_page, mixed_word and all other rules.

Native frame correction: **539 pages** have provider integer vertices inconsistent with the native image's normalized vertices. The T23 adapter uses the provider normalized vertices relative to the explicitly reported native pixel dimensions, as defined in [NormalizedVertex](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document#NormalizedVertex). Agreeing integer frames retain their original coordinates; recorded-transform cases retain the T15 inverse mapping. Raw responses, text anchors, confidence values and T20 rules are unchanged. Native before/after cards in [frame_before_visual_selection.json](frame_before_visual_selection.json) and [visual_qa_corrected_selection.json](visual_qa_corrected_selection.json) verify the corrected row association. The initial integer-frame build was superseded before publication.

Reads use a forward queue with three workers and a backward queue with six workers paced at ≥6.1 s between new starts. Both queues share image-SHA locks, parsed caches and one budget ledger; cache hits do not call the provider. The fixed selection and hold-outs predate both queues.

Storage: complete raw responses are retained as lossless gzip archives. For exact embedded copies of an input PNG, `.json.dedup.gz` keeps every other response field and a SHA-bound reference to the saved native PNG. The loader reconstructs the original base64 field and canonical response bytes, verifying the original raw SHA-256. No pixels, text, confidences or geometry are discarded. Full gzip remains the fallback when the embedded image differs. To materialize one original JSON offline: `python -m scripts.harvest.compact_parliament_raw --restore <original-raw-json-path>`. The archive journal is `harvest_big/parliament/google/raw_archives.jsonl`; intermediate full archives may be superseded by their deduplicated representation.

Debug page assignments are losslessly gzipped under `assignments/`; byte/hash receipts are in `assignment_archives.json`. The requested records and admission JSONL files remain uncompressed. Assignment JSON bytes can be restored with `gzip -dk <file.json.gz>`.

Every gate-accepted native PNG is retained, including failed DocAI inputs, as are native counterexamples for every page-gate flag. Other gate-rejected PNG intermediates have a review preview, original PNG/PDF SHA, source bitstream and exact render recipe in [page_image_retention.json](page_image_retention.json). They were released to fit the requested crops and compiled pages on disk. They contribute no lines. Regeneration, without Google: `python -m scripts.harvest.parliament_retention --restore <page-id>` (public PDF download, SHA check, byte-identical re-render, temporary PDF deletion).

| Class | Split | Era 1975–1981 | Era 1982–2000 | Total |
| --- | --- | ---: | ---: | ---: |
| greek_poly | train | 23184 | 5970 | 29154 |
| greek_poly | dev | 2083 | 5 | 2088 |
| greek_poly | test | 5453 | 1293 | 6746 |
| greek_mono | train | 700 | 36749 | 37449 |
| greek_mono | dev | 60 | 2699 | 2759 |
| greek_mono | test | 206 | 5675 | 5881 |
| greek_latin_cs | train | 78 | 92 | 170 |
| greek_latin_cs | dev | 1 | 7 | 8 |
| greek_latin_cs | test | 18 | 13 | 31 |
| latin | train | 134 | 620 | 754 |
| latin | dev | 0 | 1 | 1 |
| latin | test | 0 | 1 | 1 |
| cyrillic | train | 0 | 0 | 0 |
| cyrillic | dev | 0 | 0 | 0 |
| cyrillic | test | 0 | 0 | 0 |

Era tags describe the catalogue year: 1975–1981 can be polytonic; 1982+ has the monotonic-era tag. The unchanged script classifier decides each line independently; **7268 post-1981 lines classify as greek_poly**. No accents or labels are silently rewritten to fit the year.

| Admission rejection reason | Lines (overlapping) |
| --- | ---: |
| short_line | 6818 |
| low_confidence | 3311 |
| tall_box | 273 |
| symbol_heavy | 3573 |
| foreign_script | 83 |
| mixed_word | 137 |
| bad_page | 165 |
| label_in_holdout | 756 |
| crop_geometry | 0 |

Hold-out seed 20261015: sixteen books from sixteen represented years, spread across sixteen chronological year strata; 12 test / 4 dev, frozen before any Google call. All lines inherit their whole-volume split. O5 excludes 756 new train lines equal to any round-1, Vouli, round-2 or new dev/test label. A combined [training pool](train_pool.jsonl) additionally excludes 10 old train matches; old admitted artifacts stay byte-identical. The inherited Vouli polytonic-source cap also applies to this pool.

API politeness: **254 requests; minimum start gap 2.010081 s (required ≥2 s)**. The serial cross-process lock covers metadata, streamed PDFs, redirects and failed probes. Cache hits are not requests. Two compound-query discovery probes returned HTTP 500 and were replaced by complete title-field queries; no request retry was performed. [Politeness receipt](api_politeness.json); bulk transport ledger `http_t23/requests.jsonl`.

Google: **705 unique reserved calls, USD 1.0575**, within USD 2.50. [Document AI list price](https://cloud.google.com/products/document-ai/pricing) checked 15 October 2026: USD 1.50/1,000 OCR pages; the conservative ledger deducts no free allowance. This is a reservation estimate, not invoice readback. `harvest_big/parliament/google/budget.jsonl` reserves before calling, at most once per page-image SHA. No Vision instance/calls, provider retries or second reads. Definitive HTTP 400 size refusals retain their raw response and reservation and are never retried; other pages continue at native 200 dpi. See [Document AI limits](https://docs.cloud.google.com/document-ai/limits). [Cache replay](resume_check.json) makes zero network calls.

Zero-acceptance volumes: 1 (fb8a9d34). They retain their original selection and whole-volume split, with zero reads; they are not replaced by a quality-driven volume draw. Read failures: 15 definitive size refusals; 0 unusable geometry pages; 0 empty reads; 0 no-line reads; 0 inverse-transformed pages. Admission: 2 bad pages; 0 uncuttable geometries rejected; 38561 native crops trimmed. Crops retain the T20 spatial-neighbour >15% midpoint rule and 4/2 px padding. All final native crop pixels and compiled rasters are replayed. Bad read pages retain a visible red rejection heading in their compiled JPEG. Automatic checks do not establish transcription accuracy or single-row glyph ownership. [Visual sample](visual_qa.json) records the inspected physical evidence. The compiled raster, fonts and quality 85 remain the approved format; optimized JPEG entropy coding reduces disk use while retaining the same decoded pixels.

A retained counterexample is `f401a95f-p000044-l0116`: the provider combines two physical rows and reverses their reading order. It has mean confidence 0.964975 and passes the unchanged T20 quality rules. The native frame correction aligns its box to those rows, but does not repair the teacher text or impose an extra admission rule. The record and context remain available for post-hoc owner review.

**270 offline tests passed**. [Validation](validation.json), [tests](tests.xml), [plan](plan.json), [records](records.jsonl), [admitted](admitted.jsonl), [rejected](rejected.jsonl), [summary](admission_summary.json), [hold-outs](holdout_books.json), [inventory](inventory.json), [Git audit](git_audit.json). Main Git bookkeeping unchanged: True; no Git mutation commands were issued.

| Year | UUID | Split | PDF pages | Rendered | Accepted | Read | Lines | Admitted |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1975 | e345c3be-b853-4afe-b622-c1beda45ccf8 | train | 20 | 13 | 5 | 5 | 699 | 639 |
| 1975 | b567b1c6-b2fa-4206-986e-fab28812690a | dev | 94 | 22 | 9 | 9 | 947 | 869 |
| 1975 | 71d82b4d-9530-4de6-9a00-c9c7cf70956f | train | 20 | 12 | 11 | 11 | 1567 | 1410 |
| 1975 | ebb7b04b-8918-4eab-af4c-fe5e08941d5d | train | 14 | 12 | 3 | 3 | 446 | 426 |
| 1976 | 133c1ea6-e34b-4079-a836-c1b766afa5cd | train | 26 | 13 | 11 | 11 | 1474 | 1275 |
| 1976 | 7f661ed4-97cf-4adc-af01-bdac92d7ab67 | dev | 36 | 15 | 10 | 10 | 1368 | 1275 |
| 1976 | 7aea9867-6352-4567-929e-e78f524d7d05 | train | 56 | 21 | 8 | 8 | 1129 | 1046 |
| 1976 | 52b46e46-11b3-42ed-8463-0daba41167bd | train | 36 | 18 | 10 | 10 | 1365 | 1188 |
| 1977 | 7765f98b-6c1c-4c1b-a800-a92499af0bf8 | train | 32 | 14 | 11 | 10 | 1461 | 1011 |
| 1977 | 51e4207d-a81d-422d-b184-6254f621ec3e | test | 40 | 23 | 8 | 8 | 991 | 895 |
| 1977 | dd625312-f377-45b1-82a9-d0f21532fd48 | train | 50 | 16 | 12 | 12 | 1668 | 1522 |
| 1977 | b4557a07-45d1-4c6b-b0ad-84affcc96a27 | train | 32 | 18 | 10 | 10 | 1411 | 1318 |
| 1978 | 64dc8c3d-6b96-42a5-a809-490a5c82dea8 | train | 30 | 15 | 10 | 10 | 1399 | 1263 |
| 1978 | 0b33fccd-88e6-4a02-ac8f-c1248edea74b | train | 34 | 18 | 8 | 8 | 1143 | 1050 |
| 1978 | 129cff40-ee21-4ca6-ace9-c99d3f8ebf8a | test | 22 | 13 | 9 | 8 | 1116 | 1059 |
| 1978 | aac90dd4-d02d-4286-bc95-11de4a08dbac | train | 38 | 14 | 10 | 9 | 1258 | 1042 |
| 1979 | 13ea41c1-7726-4268-b329-45ee6285078c | train | 24 | 14 | 10 | 5 | 691 | 639 |
| 1979 | 6260d773-1721-4213-84ac-55c0c01cfb75 | train | 24 | 15 | 6 | 6 | 825 | 786 |
| 1979 | 1d27927c-b608-4fe2-b059-e5d7ff45cfa2 | train | 38 | 19 | 8 | 8 | 1124 | 1028 |
| 1979 | a65a813d-e85f-4148-82a6-a483162d45da | test | 28 | 15 | 8 | 8 | 1124 | 996 |
| 1980 | 20900789-ed69-4a6c-b0ed-2b3cdfe68faf | test | 50 | 16 | 11 | 11 | 1593 | 1408 |
| 1980 | 1a035976-b917-49a9-a779-04d1c30c3822 | train | 50 | 15 | 11 | 11 | 1554 | 1321 |
| 1980 | 76aff04c-9948-4b24-a961-54866df40355 | train | 26 | 14 | 12 | 12 | 1738 | 1621 |
| 1980 | 96acdae7-3ca8-483d-af83-e8c40462428d | train | 46 | 16 | 11 | 11 | 1542 | 1221 |
| 1981 | 3455d0e7-a3fc-458f-95f5-84d5089ad9b6 | train | 30 | 12 | 12 | 12 | 1735 | 1481 |
| 1981 | f401a95f-a319-41f9-9341-e552d15bba32 | train | 58 | 19 | 11 | 11 | 1570 | 1403 |
| 1981 | 847e1ec1-0e97-43ee-85fe-613da088c2a3 | train | 40 | 14 | 11 | 11 | 1568 | 1406 |
| 1981 | 100763df-a69f-471a-86a3-66a38868ad45 | test | 36 | 18 | 11 | 11 | 1461 | 1319 |
| 1982 | 548cab64-2488-4f0d-8169-0b566f88816d | test | 34 | 13 | 10 | 10 | 1412 | 1312 |
| 1982 | f47c50c8-7458-4ee5-8dff-e8e99b663e3e | train | 22 | 14 | 9 | 9 | 1155 | 987 |
| 1982 | 13dcc39a-4631-4fd0-a0d6-74b36ec019dc | train | 34 | 15 | 11 | 11 | 1561 | 1437 |
| 1982 | f36aba38-2b15-4485-b70e-0602947913c7 | train | 30 | 14 | 11 | 11 | 1441 | 1282 |
| 1983 | 95d812ab-43c0-4e4c-825f-cb3901f2868a | train | 54 | 13 | 12 | 12 | 1598 | 1454 |
| 1983 | 48a58eb5-1560-4660-aa00-911d53198cff | train | 108 | 15 | 12 | 12 | 1399 | 1212 |
| 1983 | 1a915aad-9a29-4d6c-9e04-64d1c7ea6b09 | train | 40 | 26 | 5 | 5 | 732 | 661 |
| 1983 | 3be8f3b1-58dd-45d1-8186-128c3f9d7b09 | train | 46 | 15 | 12 | 12 | 1694 | 1540 |
| 1984 | 30d76051-9efd-4cd2-a608-1656c69f0cc4 | train | 60 | 17 | 12 | 12 | 1674 | 1438 |
| 1984 | 87d33c70-92cd-49e9-85fe-09c8111daab3 | test | 40 | 12 | 12 | 10 | 1530 | 1393 |
| 1984 | 01c618de-65e6-4563-b84b-ec421c33e01f | train | 26 | 13 | 10 | 7 | 996 | 924 |
| 1984 | a5914b37-861e-445f-b177-d5b2270c2554 | train | 48 | 23 | 9 | 9 | 1240 | 1081 |
| 1985 | 55062aa4-e0c6-4f3c-be58-2ed2f22c8f93 | train | 132 | 23 | 7 | 7 | 936 | 805 |
| 1985 | 9864afa9-84bf-4a4f-863e-ea71d3d507f1 | train | 34 | 17 | 10 | 10 | 1448 | 1304 |
| 1985 | c72a5c9e-4647-4286-b643-9104d35ef143 | train | 30 | 16 | 10 | 10 | 1455 | 1365 |
| 1985 | a92e918e-50e3-4296-9ceb-f1460e24f1e7 | test | 78 | 20 | 11 | 11 | 1534 | 1312 |
| 1986 | 4534d6a1-9260-46a3-b482-6906e1c05f2c | train | 30 | 13 | 12 | 12 | 1707 | 1586 |
| 1986 | 0590d5cb-bf87-4da5-a3ba-e0faabf605a5 | train | 26 | 13 | 12 | 12 | 1642 | 1484 |
| 1986 | 7c411292-3116-4e40-b211-ca4bc2e69b48 | train | 44 | 13 | 12 | 12 | 1746 | 1518 |
| 1986 | 7bd6c40b-c5c4-412f-946b-6155b0796a65 | test | 64 | 13 | 11 | 11 | 1567 | 1390 |
| 1987 | 1efea0f4-a2dc-4e66-a72c-6c953b89136e | train | 26 | 18 | 6 | 6 | 866 | 714 |
| 1987 | e8ea7178-2aaa-4d20-8b5b-7357cf707b6e | train | 46 | 19 | 11 | 11 | 1611 | 1381 |
| 1987 | 5a2536ee-cd1b-42d6-958e-f91a07e60eb1 | train | 28 | 12 | 12 | 12 | 1740 | 1545 |
| 1987 | 5674da8d-52e8-4765-b8aa-18f05bac3128 | dev | 48 | 16 | 10 | 10 | 1386 | 1192 |
| 1988 | 37e22f57-c558-4021-8b0c-b8994cfc6f9e | test | 40 | 29 | 1 | 1 | 123 | 87 |
| 1988 | 7b996aa5-4130-4962-b75f-a6ee2df76db6 | train | 46 | 14 | 10 | 10 | 1355 | 1178 |
| 1988 | a8b6ae98-7e4e-41b4-bda4-41cb77fdd2f5 | train | 24 | 15 | 10 | 10 | 1728 | 1480 |
| 1988 | 859c90dc-f38e-40ed-90e3-1147c4321543 | train | 26 | 14 | 8 | 8 | 1181 | 1068 |
| 1989 | 9a494f31-dea2-4bdf-a744-d58af7f7df08 | train | 66 | 24 | 6 | 5 | 678 | 594 |
| 1989 | fb8a9d34-a82e-495a-a269-b5a180616928 | test | 46 | 29 | 0 | 0 | 0 | 0 |
| 1989 | 3bbe5ef7-5eae-4df2-b5b1-39c80682663b | train | 46 | 15 | 10 | 9 | 1300 | 1220 |
| 1989 | f1cf6e4b-1956-4de8-8fcf-64003c6df213 | train | 35 | 13 | 11 | 11 | 1679 | 1509 |
| 1994 | 76d25f50-cb4b-4480-8185-9a6c82991bf6 | test | 46 | 16 | 11 | 11 | 1603 | 1488 |
| 1994 | f74236d5-9fff-44de-bf9e-e1e3d1e17429 | train | 42 | 12 | 12 | 12 | 1724 | 1633 |
| 1994 | d4c4e5ce-46b8-4ed4-b4a9-b8b30a56e581 | train | 26 | 15 | 7 | 7 | 904 | 805 |
| 1994 | 608b6841-ec70-4eb4-a410-59ca91b26e92 | train | 54 | 12 | 12 | 12 | 1737 | 1591 |
| 1995 | 26ee7610-6a95-42c7-94b9-17a1fd276735 | train | 223 | 20 | 10 | 10 | 517 | 261 |
| 1995 | be486d8c-7b5f-425d-9774-ceecf59103b8 | dev | 63 | 12 | 12 | 12 | 1646 | 1520 |
| 1995 | 7a1452d8-0a6b-4b3b-b84f-f4c02e2f2b05 | train | 36 | 17 | 11 | 11 | 1593 | 1479 |
| 1995 | 2b989b7d-88d2-482f-be2d-4a7b0c7ac5f0 | train | 124 | 13 | 12 | 12 | 1297 | 1154 |
| 1996 | 18369cae-f57c-4b5c-82cd-af49d1bbc793 | train | 68 | 12 | 12 | 12 | 1492 | 1301 |
| 1996 | 30fff481-48eb-4223-8420-9741c25496db | train | 56 | 13 | 12 | 12 | 1723 | 1555 |
| 1996 | de9da003-c8a6-47a9-960c-d16b02372d02 | train | 42 | 18 | 10 | 10 | 1383 | 1260 |
| 1996 | 29bccf95-74b1-464f-9917-35e2572d338d | train | 58 | 13 | 12 | 12 | 1738 | 1625 |

T23: done | volumes: 72 | pages: 1153/705/690 | lines: 95438 | admitted: 85042 | mono: 46089 | poly: 37988 | train: 67527 | dev: 4856 | test: 12659 | usd: 1.06 | tests: 270 passed
