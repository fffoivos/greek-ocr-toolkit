# O2 duplicate and edition re-check

The corrected **89 wave-4 identities have no cross-split group found by keys PDF SHA256, provider item ID, normalized true title + publication year, or page-image SHA256**, and no within-split doubles or near matches at the specified threshold. All four keys cover 89/89 books, including the declared test holdout with zero admitted lines. All 15 corrected test-book identities are listed in [wave4_test_books.jsonl](wave4_test_books.jsonl).

Across all waves there are **12 exact-key groups**: seven page-image hash collisions, two serial-title/year collisions, and three keys identifying the single v1 page-split lexicon. **Seven groups cross splits in v1; four in v2.** These are requested key groups, not seven or four independent duplicate editions. The two serial groups are different bound volumes, as verified on provider item pages. The three train/test page collisions have zero admitted training lines on the colliding pages in both versions. No release or split repair was applied.

## Counts by key and version

Lines are the union of whole-book admitted lines for members of the selected groups, deduplicated by book within each table row. This measures test-book exposure. It is distinct from the count of lines on the colliding pages shown below. A group can cross more than one split pair. Overlapping keys are not additive.

| Version | Key | Cross-split | Train↔test | Train↔dev | Dev↔test | Within train | Within dev | Within test | Cross-group lines train/dev/test | Test books |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 | all | 7 | 7 | 3 | 3 | 6 | 0 | 1 | 9086 / 939 / 2945 | 5 |
| v1 | pdf_sha256 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 6884 / 939 / 1965 | 1 |
| v1 | provider_id | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 6884 / 939 / 1965 | 1 |
| v1 | title_year | 2 | 2 | 1 | 1 | 2 | 0 | 1 | 8716 / 939 / 2630 | 3 |
| v1 | page_image_sha256 | 3 | 3 | 0 | 0 | 4 | 0 | 0 | 370 / 0 / 315 | 2 |
| v2 | all | 4 | 4 | 0 | 0 | 6 | 0 | 1 | 2106 / 0 / 952 | 4 |
| v2 | pdf_sha256 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| v2 | provider_id | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| v2 | title_year | 1 | 1 | 0 | 0 | 2 | 0 | 1 | 1791 / 0 / 658 | 2 |
| v2 | page_image_sha256 | 3 | 3 | 0 | 0 | 4 | 0 | 0 | 315 / 0 / 294 | 2 |

Version-union hand-off counts use distinct group IDs active in **either** version: 7 cross-split groups, 6 within-train groups, and 5 test books. They are not the sum of the version rows. The final line counts all requested exact-key candidates, including adjudicated serial-title collisions; it excludes possible matches.

| Category (either version) | Groups | v1 member lines train/dev/test | v2 member lines train/dev/test | Test books |
| --- | --- | --- | --- | --- |
| cross_split | 7 | 9086 / 939 / 2945 | 11771 / 0 / 952 | 5 |
| train_test | 7 | 9086 / 939 / 2945 | 11771 / 0 / 952 | 5 |
| train_dev | 3 | 6884 / 939 / 1965 | 9665 / 0 / 0 | 1 |
| dev_test | 3 | 6884 / 939 / 1965 | 9665 / 0 / 0 | 1 |
| within_train | 6 | 5602 / 0 / 665 | 5285 / 0 / 658 | 2 |
| within_dev | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 |
| within_test | 1 | 1832 / 0 / 665 | 1791 / 0 / 658 | 2 |

## Every exact-key group

| Group | Key type | Book members | v1 splits | v2 splits | Meaning |
| --- | --- | --- | --- | --- | --- |
| D00001 | page_image_sha256 | vouli:b32fc7776b85, vouli:c240240e279e | train, test | train, test | exact_scanned_page_shared_across_provider_books |
| D00002 | page_image_sha256 | vouli:452f5a742630, vouli:9e6fd8368590 | train | train | exact_scanned_page_shared_across_provider_books |
| D00003 | page_image_sha256 | vouli:5f34f629ffc3, vouli:b32fc7776b85 | train, test | train, test | exact_scanned_page_shared_across_provider_books |
| D00004 | page_image_sha256 | vouli:116a24bf9010, vouli:2bcc4d069b39 | train | train | exact_scanned_page_shared_across_provider_books |
| D00005 | page_image_sha256 | vouli:0c516ea32fdb, vouli:bec70ac3ff65 | train | train | exact_scanned_page_shared_across_provider_books |
| D00006 | page_image_sha256 | vouli:ae65c155bdb2, vouli:ce43459c6fca | train, test | train, test | exact_scanned_page_shared_across_provider_books |
| D00007 | page_image_sha256 | vouli:0c516ea32fdb, vouli:c240240e279e | train | train | exact_scanned_page_shared_across_provider_books |
| D00008 | pdf_sha256 | mixed:4c207e1e | train, dev, test | train | same_book_page_split_in_v1_already_whole_book_train_in_input_v2 |
| D00009 | provider_id | mixed:4c207e1e | train, dev, test | train | same_book_page_split_in_v1_already_whole_book_train_in_input_v2 |
| D00010 | title_year | mixed:4c207e1e | train, dev, test | train | same_book_page_split_in_v1_already_whole_book_train_in_input_v2 |
| D00011 | title_year | cyrillic:252fd568, cyrillic:ae1a00a3 | train | train | distinct_bound_volumes_same_serial_catalogue_title_and_date |
| D00012 | title_year | cyrillic:363040a9, cyrillic:4b2c4367, cyrillic:b930919b, cyrillic:e2a71638 | train, test | train, test | distinct_bound_volumes_same_serial_catalogue_title_and_date |

Full keys, legacy book IDs, true/recorded titles and years, wave, splits, per-version lines and page occurrences are in [duplicates.jsonl](duplicates.jsonl). [duplicate_adjudications.jsonl](duplicate_adjudications.jsonl) preserves decisions and source evidence without modifying input data.

## Exact scanned-page collisions

All 14 native image files were rehashed and agree with the saved page-image keys. One D00001 image was visually inspected: printed page 10 contains the end of one session and the start of session Δ on 16 November 1843. It is a text-bearing boundary overlap. Different parliamentary catalogue records can share a boundary page without representing the same complete book.

| Group | Pages (book:page) | v1 actual page lines train/dev/test | v2 actual page lines train/dev/test | Admitted page cross-split v1/v2 |
| --- | --- | --- | --- | --- |
| D00001 | c240240e279e:4, b32fc7776b85:1 | 0 / 0 / 40 | 0 / 0 / 40 | False / False |
| D00002 | 452f5a742630:1, 9e6fd8368590:6 | 68 / 0 / 0 | 26 / 0 / 0 | False / False |
| D00003 | 5f34f629ffc3:1, b32fc7776b85:3 | 0 / 0 / 36 | 0 / 0 / 36 | False / False |
| D00004 | 116a24bf9010:1, 2bcc4d069b39:11 | 68 / 0 / 0 | 31 / 0 / 0 | False / False |
| D00005 | 0c516ea32fdb:1, bec70ac3ff65:5 | 74 / 0 / 0 | 36 / 0 / 0 | False / False |
| D00006 | ce43459c6fca:2, ae65c155bdb2:1 | 0 / 0 / 107 | 0 / 0 / 102 | False / False |
| D00007 | 0c516ea32fdb:3, c240240e279e:1 | 64 / 0 / 0 | 28 / 0 / 0 | False / False |

Four within-train page groups have both copies represented by admitted lines in v1; **zero** have both copies represented in v2. The seven shared page files remain real source collisions and are retained in the requested book-level report. Hashes are of encoded native image files; differently encoded, cropped or rescaled versions of the same scan may evade this check.

## Serial title/year candidates

The provider publication dates are serial-level dates, not sufficient bound-volume identities. Provider item pages confirm the following disjoint volume ranges. PDF hashes and provider item IDs are distinct. No claim of scan identity follows from the title/year collision.

| Group | Book | Provider volume | Catalogue date | Split v2 | Provider item |
| --- | --- | --- | --- | --- | --- |
| D00011 | 252fd568 | t. 2-5 (1925-30) | 1924 | train | [item](https://archive.org/details/izvestiianabul25192530bul) |
| D00011 | ae1a00a3 | t. 6-10 (1931-38) | 1924 | train | [item](https://archive.org/details/izvestiianabulga610193138bulg) |
| D00012 | 363040a9 | kn. 11-12 (1938-39) | 1928 | test | [item](https://archive.org/details/izvestiianatsars1112193839tsar) |
| D00012 | 4b2c4367 | kn. 15-16 (1942-43) | 1928 | train | [item](https://archive.org/details/izvestiianatsars1516194243tsar) |
| D00012 | b930919b | kn. 1-2 (1928-29) | 1928 | train | [item](https://archive.org/details/izvestiianatsars12192829tsar) |
| D00012 | e2a71638 | kn. 9-10 (1936-37) | 1928 | test | [item](https://archive.org/details/izvestiianatsars910193637tsar) |

## Key coverage and matching rules

| Population | Books | PDF hash | Whole PDF hash | Provider item | Title + year | Page image |
| --- | --- | --- | --- | --- | --- | --- |
| collection_union | 557 | 527/557 (94.61%) | 309/557 (55.48%) | 557/557 (100.00%) | 513/557 (92.10%) | 557/557 (100.00%) |
| wave4_89 | 89 | 89/89 (100.00%) | 89/89 (100.00%) | 89/89 (100.00%) | 89/89 (100.00%) | 89/89 (100.00%) |
| all_including_empty_wave4_holdout | 558 | 528/558 (94.62%) | 310/558 (55.56%) | 558/558 (100.00%) | 514/558 (92.11%) | 558/558 (100.00%) |
| v1 | 557 | 527/557 (94.61%) | 309/557 (55.48%) | 557/557 (100.00%) | 513/557 (92.10%) | 557/557 (100.00%) |
| v2 | 547 | 517/547 (94.52%) | 300/547 (54.84%) | 547/547 (100.00%) | 506/547 (92.50%) | 547/547 (100.00%) |

The final-line denominator is 558: the 557-book union of v1/v2 plus the empty declared wave-4 test holdout. All have page hashes, so all qualify for the requested audit. PDF coverage includes Anemi per-page PDF derivatives (218 books); it must not be read as whole-book PDF coverage. Thirty Wikisource books have no PDF hash. Provider aliases use exact item URLs, handles (repository-qualified for the reused placeholder prefix `123456789`), EDM IDs, IA identifiers, and Wikisource/Commons scan IDs. Pergamos numeric and `uoadl:` item aliases are normalized. URL schemes and the handle resolver are unified only for these defined identity forms; query parameters and item namespaces are retained.

True titles are NFC/casefolded, decomposed to strip combining accents for matching only, and non-alphanumeric punctuation is collapsed to whitespace. Title keys require an integer publication year. The stored title spelling is unchanged by matching. Thirty-five mixed-wave Open Archives titles are excluded because their join is unverified; nine other books lack a year. Those books remain covered by hashes and provider IDs. The mixed OA provider IDs were rebound for audit matching only from the same pinned PDF-to-item table; no mixed-wave metadata is released here. Cross-wave matching was enabled globally, and **zero exact cross-wave groups** were found.

Near matches are in [possible.jsonl](possible.jsonl): **37** possible pairs, with full members, split lines and scores; none involves wave 4. The threshold is `SequenceMatcher(autojunk=False).ratio() >= 0.9` on normalized `title | year`. Exact title/year groups are excluded from that list; title-only similarity and year equality are also shown. Similar session titles on different dates remain possible pairs, not inferred duplicate editions. No external OCR, downloads of PDFs, or perceptual image matching was performed.

Inputs and their unchanged final fingerprints are bound in [duplicate-inputs.json](receipts/duplicate-inputs.json); exact collision-file readback is in [page-collision-readback.json](receipts/page-collision-readback.json). Six bounded Internet Archive provider item pages were read (all HTTP 200), with no redirects followed, and are archived under [provider_item_pages](receipts/provider_item_pages/). No other network endpoint or paid service was used.
