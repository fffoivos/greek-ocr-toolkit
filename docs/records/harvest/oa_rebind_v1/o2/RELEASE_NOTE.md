# Collection v2-meta1 — metadata-only release

**25,372 active line records across 88 represented wave-4 books receive corrected metadata. Zero lines were added, dropped, moved or relabelled.** The 89-book sidecar also corrects the declared test holdout with zero admitted lines. This release applies the O1 proposal from commit `c22d7a78` to copies of the 14 existing `collection/v2/` files. Main and funnel worktrees were read-only; no collection rebuild, source cap, rights decision, label cleaning or admission was rerun.

## What changed

Existing source/source_dataset, attribution, publication year/decade and catalogue fields are replaced where present. The original trainer schemas omit book title, collection slug and EDM URL; those complete corrected fields are published in the **89-row auxiliary** [book_metadata.jsonl](v2_meta1/book_metadata.jsonl). It adds no training lines. Existing field sets are retained except the explicitly requested `metadata_status: pending_provider_verification` on Dione line metadata. No old OCR-success, type, ratio, licence or rights field is promoted or replaced.

| Active admitted field | Train changed | Dev changed | Test changed | Total |
| --- | --- | --- | --- | --- |
| attribution | 19625 | 1067 | 4680 | 25372 |
| year | 19090 | 1067 | 4680 | 24837 |
| decade | 13841 | 862 | 3953 | 18656 |
| metadata_status | 2059 | 0 | 769 | 2828 |
| source | 17566 | 1067 | 3911 | 22544 |

Book-level corrections: title 89/89; collection/source 80/89; year 87/89 (86 contradictions plus one previously unknown year resolved); decade 66/89 (65 contradictions plus the same previously unknown decade resolved). Catalogue item URLs were already correct and remain unchanged; all 89 EDM links are retained from the pinned identity evidence in the sidecar. Raw bibliographic type/evidence remain in O1 and are not applied.

The sidecar comparison below is against the original 89 source-book records. Book split counts include the empty declared test holdout. EDM links are newly exposed in this auxiliary schema, not added training lines.

| Auxiliary book field | Train books | Dev books | Test books | Total changed/added metadata |
| --- | --- | --- | --- | --- |
| collection_slug | 62 | 5 | 13 | 80 |
| title | 69 | 5 | 15 | 89 |
| year | 67 | 5 | 15 | 87 |
| source | 62 | 5 | 13 | 80 |
| attribution | 69 | 5 | 15 | 89 |
| edm_url | 69 | 5 | 15 | 89 |
| decade | 49 | 4 | 13 | 66 |
| metadata_status_pending | 7 | 0 | 2 | 9 |

| Split | Active rows before | Active rows after | Rows with metadata changed | Added | Dropped | Moved |
| --- | --- | --- | --- | --- | --- | --- |
| train | 214436 | 214436 | 19625 | 0 | 0 | 0 |
| dev | 13522 | 13522 | 1067 | 0 | 0 | 0 |
| test | 44029 | 44029 | 4680 | 0 | 0 | 0 |

## File receipt and immutable data

| File | Logical rows before/after | Rows with metadata changed | (id, crop hash, label) SHA256 equal | ID sets/order/multisets equal | Added/dropped/moved |
| --- | --- | --- | --- | --- | --- |
| CLEAN_REPORT.md | 0 / 0 | 0 | True | True | 0 / 0 / 0 |
| admitted_all_v2.jsonl | 271987 / 271987 | 25372 | True | True | 0 / 0 / 0 |
| dropped_v2.jsonl | 21449 / 21449 | 232 | True | True | 0 / 0 / 0 |
| import_real_v2_all.jsonl | 271987 / 271987 | 25372 | True | True | 0 / 0 / 0 |
| import_real_v2_dev.jsonl | 13522 / 13522 | 1067 | True | True | 0 / 0 / 0 |
| import_real_v2_test.jsonl | 44029 / 44029 | 4680 | True | True | 0 / 0 / 0 |
| import_real_v2_train.jsonl | 214436 / 214436 | 19625 | True | True | 0 / 0 / 0 |
| manifest_v2_dev.json | 13522 / 13522 | 1067 | True | True | 0 / 0 / 0 |
| manifest_v2_test.json | 44029 / 44029 | 4680 | True | True | 0 / 0 / 0 |
| manifest_v2_train.json | 214436 / 214436 | 19625 | True | True | 0 / 0 / 0 |
| rejected_global_v2.jsonl | 3 / 3 | 0 | True | True | 0 / 0 / 0 |
| relabels_v2.jsonl | 10313 / 10313 | 0 | True | True | 0 / 0 / 0 |
| split_moves_v2.json | 2868 / 2868 | 0 | True | True | 0 / 0 / 0 |
| validation_v2.json | 0 / 0 | 0 | True | True | 0 / 0 / 0 |

The [receipt](v2_meta1/receipt.json) gives full file SHA256/bytes, physical and logical line counts, before/after ID sets and multiplicities, split counts, immutable JSON-token hashes, ordered tuple hashes and per-field/per-split changes. IDs and crop hashes missing from manifest/import views are joined by the exact original crop path or line ID to the admitted record, with v1 used only for historical dropped/relabel/move rows. Every tuple has a crop hash. Original non-metadata JSON token spelling is preserved, including all labels and split decisions. The active admitted rows are counted once here; repeated import/manifest exports are not additional training rows. The 232 historical dropped wave-4 rows also receive metadata updates without being admitted.

`CLEAN_REPORT.md`, `validation_v2.json`, split-move and relabel/rejection decision records are retained as historical v2 evidence. Their old artifact hashes refer to input v2, not v2-meta1; the new receipt binds the release files. A new independent readback is reported in [validation.json](receipts/validation.json).

## Nine Dione books pending provider verification

The fields are updated from the exact-item-linked official aggregator evidence accepted for this release. All nine auxiliary book rows and their 2,828 active line occurrences carry `metadata_status: pending_provider_verification`. The provider remains unverified; these are not counted as provider-verified titles. No new Dione request was made.

| Book key | True title | Publication year | Train/dev/test active lines | Provider item | EDM |
| --- | --- | --- | --- | --- | --- |
| 0b63328a | Ανάλυση επιχειρηματικών μοντέλων ηλεκτρονικού εμπορίου με έμφαση στις ηλεκτρονικές αγορές | 2015 | 0 / 0 / 555 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/6323) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-6323) |
| 520de75a | Τεχνολογίες χειρουργείου | 2015 | 266 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/6347) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-6347) |
| 57ecc6b2 | Ο ρόλος της διοίκησης ανθρωπίνων πόρων στην περίπτωση των ιατρικών επισκεπτών | 2011 | 272 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/4033) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-4033) |
| 6797597d | Mobile banking. Η τραπεζική ανά χείρας | 2014 | 466 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/6583) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-6583) |
| 8ba4e15e | Ποιότητα της προσφερόμενης μεταφορικής υπηρεσίας. Η ικανοποίηση των τουριστών από τις εταιρείες ενοικιάσεως αυτοκινήτων στην Ελλάδα | 2014 | 228 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/7438) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-7438) |
| 9e7a9507 | Ανάπτυξη εφαρμογής (e-Chartering) με χρήση ASP.NET core και entity framework για την ναυτιλιακή βιομηχανία | 2020 | 253 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/12965) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-12965) |
| a181595d | Η τρομοκρατία ως εργαλείο επικράτησης των μαζικών πολιτικών κινημάτων του 20ου αιώνα | 2014 | 367 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/7254) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-7254) |
| ab5e8994 | Οργάνωση και λειτουργία εξειδικευμένου ιδιωτικού ενδοκρινολογικού πολυϊατρείου | 2006 | 207 / 0 / 0 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/7515) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-7515) |
| c82ac45f | Internet banking: εφαρμογή στην Εθνική Τράπεζα | 2000 | 0 / 0 / 214 | [item](https://dione.lib.unipi.gr/xmlui/handle/unipi/7458) | [EDM](https://www.openarchives.gr/aggregator-openarchives/edm/Dione/000013-7458) |

## Source-cap corrections — recorded, not applied

These counts correct the repository attribution of all 89 downloaded wave-4 books. Train shares below use the unchanged 19,625 wave-4 train lines; the final column uses all 214,436 v2 train lines. Deltas are percentage points. [source_cap_corrections.json](source_cap_corrections.json) also records admitted book counts per split and the v1 comparison. No cap is reapplied and no line membership changes.

| Repository | Old/true downloaded books | Old/true train books | Old/true train lines | Old/true wave-4 train share | Δ wave-4 pp | Δ collection pp |
| --- | --- | --- | --- | --- | --- | --- |
| Dione | 9 / 9 | 7 / 7 | 2059 / 2059 | 10.492% / 10.492% | +0.000 | +0.000 |
| IKEE_AUT | 1 / 0 | 0 / 0 | 0 / 0 | 0.000% / 0.000% | +0.000 | +0.000 |
| KEIED | 8 / 0 | 6 / 0 | 2050 / 0 | 10.446% / 0.000% | -10.446 | -0.956 |
| Pandemos | 9 / 0 | 8 / 0 | 2443 / 0 | 12.448% / 0.000% | -12.448 | -1.139 |
| anaktisis | 9 / 0 | 7 / 0 | 2088 / 0 | 10.639% / 0.000% | -10.639 | -0.974 |
| apothesis | 9 / 1 | 7 / 0 | 1657 / 0 | 8.443% / 0.000% | -8.443 | -0.773 |
| edulll | 0 / 8 | 0 / 6 | 0 / 2050 | 0.000% / 10.446% | +10.446 | +0.956 |
| elstat | 0 / 1 | 0 / 1 | 0 / 194 | 0.000% / 0.989% | +0.989 | +0.090 |
| hellanicus | 9 / 17 | 7 / 14 | 2079 / 4337 | 10.594% / 22.099% | +11.506 | +1.053 |
| kallipos | 9 / 0 | 7 / 0 | 2184 / 0 | 11.129% / 0.000% | -11.129 | -1.018 |
| ktisis | 9 / 9 | 7 / 7 | 2037 / 1657 | 10.380% / 8.443% | -1.936 | -0.177 |
| nemertes | 9 / 0 | 7 / 0 | 1608 / 0 | 8.194% / 0.000% | -8.194 | -0.750 |
| ntua | 8 / 0 | 6 / 0 | 1420 / 0 | 7.236% / 0.000% | -7.236 | -0.662 |
| pergamos | 0 / 18 | 0 / 14 | 0 / 4263 | 0.000% / 21.722% | +21.722 | +1.988 |
| psepheda | 0 / 9 | 0 / 7 | 0 / 2037 | 0.000% / 10.380% | +10.380 | +0.950 |
| rep_ihu | 0 / 13 | 0 / 10 | 0 / 2204 | 0.000% / 11.231% | +11.231 | +1.028 |
| uoi | 0 / 4 | 0 / 3 | 0 / 824 | 0.000% / 4.199% | +4.199 | +0.384 |

## Rights-string corrections — recorded, not applied

**34 books** carry item-specific rights text from the wrong metadata binding. Their exact old raw strings and the true-item evidence strings (including unavailable/null evidence) are retained in [rights_string_corrections.jsonl](rights_string_corrections.jsonl). All 89 book rows are retained in that ledger; the other 55 have only the generic recorded unverified licence, with no old item-specific rights string. Equal-looking licence families do not establish that the old text belonged to the downloaded item. No recorded rights/licence string is changed in any release file. Missing new rights evidence is an unresolved correction, not an inferred permission.

| Book | Old repository → true | Exact old rights string(s) | True-item rights evidence string(s) | Evidence |
| --- | --- | --- | --- | --- |
| 0adaf642 | ktisis → psepheda | ["Attribution-NonCommercial-NoDerivatives 4.0 International"] | ["Το ηλεκτρονικό αντίτυπο της διπλωματικής εργασίας αποδεσμεύτηκε μετά τις 9/7/2010."] | provider; evidence_present |
| 0b63328a | Dione → Dione | ["http://creativecommons.org/licenses/by-nc-nd/4.0/"] | ["http://creativecommons.org/licenses/by-nc-nd/4.0/deed.el Αναφορά Δημιουργού-Μη Εμπορική Χρήση-Όχι Παράγωγα Έργα 4.0 Διεθνές"] | aggregator; provider pending; evidence_present |
| 0b7fade4 | nemertes → rep_ihu | ["0\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | ["Default License"] | provider; evidence_present |
| 0bc198e5 | ktisis → psepheda | ["none"] | [] | provider; not_established |
| 1d5ad22a | ktisis → psepheda | ["none"] | [] | provider; not_established |
| 1d6f440c | nemertes → rep_ihu | ["0\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EL)"] | ["Default License"] | provider; evidence_present |
| 2f4f1c7f | hellanicus → pergamos | ["CC0 1.0 Παγκόσμια"] | [] | provider; not_established |
| 31e5d45b | ktisis → psepheda | ["© Ευρωκέρδος"] | [] | provider; not_established |
| 374194e5 | ktisis → psepheda | ["none"] | [] | provider; not_established |
| 46380632 | ntua → rep_ihu | ["NTUA-policy.xml\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | ["Αναφορά Δημιουργού-Μη Εμπορική Χρήση-Όχι Παράγωγα Έργα 4.0 Διεθνές", "http://creativecommons.org/licenses/by-nc-nd/4.0/deed.el"] | provider; evidence_present |
| 520de75a | Dione → Dione | ["http://creativecommons.org/licenses/by-nc-nd/4.0/"] | ["http://creativecommons.org/licenses/by-nc-nd/4.0/deed.el Αναφορά Δημιουργού-Μη Εμπορική Χρήση-Όχι Παράγωγα Έργα 4.0 Διεθνές"] | aggregator; provider pending; evidence_present |
| 53517087 | ntua → rep_ihu | ["NTUA-policy.xml\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | ["Default License"] | provider; evidence_present |
| 6f036eab | nemertes → rep_ihu | ["0\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | ["Αναφορά Δημιουργού-Μη Εμπορική Χρήση-Όχι Παράγωγα Έργα 3.0 Ελλάδα", "Attribution-NonCommercial-NoDerivs 3.0 Greece"] | provider; evidence_present |
| 7af6439a | ktisis → psepheda | ["none"] | [] | provider; not_established |
| 8abaa601 | ktisis → psepheda | ["open"] | [] | provider; not_established |
| 8ba4e15e | Dione → Dione | ["http://creativecommons.org/licenses/by-nc-nd/4.0/"] | ["http://creativecommons.org/licenses/by-nc-nd/4.0/ Attribution-NonCommercial-NoDerivatives 4.0 Διεθνές"] | aggregator; provider pending; evidence_present |
| 982e0266 | nemertes → rep_ihu | ["12\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EL)"] | ["Default License"] | provider; evidence_present |
| 9e7a9507 | Dione → Dione | ["Attribution-NoDerivatives 4.0 Διεθνές"] | [null] | aggregator; provider pending; not_established |
| a181595d | Dione → Dione | ["http://creativecommons.org/licenses/by-nc-nd/4.0/"] | ["http://creativecommons.org/licenses/by-nc-nd/4.0/ Attribution-NonCommercial-NoDerivatives 4.0 Διεθνές"] | aggregator; provider pending; evidence_present |
| a330e1fc | hellanicus → pergamos | ["CC0 1.0 Παγκόσμια"] | [] | provider; not_established |
| a6e49c3a | nemertes → rep_ihu | ["0\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EL)"] | ["Αναφορά Δημιουργού-Μη Εμπορική Χρήση-Όχι Παράγωγα Έργα 4.0 Διεθνές", "http://creativecommons.org/licenses/by-nc-nd/4.0/deed.el"] | provider; evidence_present |
| aab19902 | nemertes → rep_ihu | ["0\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | [] | provider; not_established |
| ab5e8994 | Dione → Dione | ["http://creativecommons.org/licenses/by-nc-nd/4.0/deed.el"] | ["http://creativecommons.org/licenses/by-nc-nd/4.0/ Attribution-NonCommercial-NoDerivatives 4.0 Διεθνές"] | aggregator; provider pending; evidence_present |
| be9e5061 | ntua → uoi | ["http://creativecommons.org/licenses/by-nd/3.0/gr/"] | ["http://creativecommons.org/licenses/by-nc-nd/3.0/gr/"] | provider; evidence_present |
| c0cb6888 | hellanicus → pergamos | ["CC0 1.0 Παγκόσμια"] | [] | provider; not_established |
| c2842bac | IKEE_AUT → apothesis | ["This record is part of 'IKEE', the Institutional Repository of Aristotle University of Thessaloniki's Library and Information Centre found at http://ikee.lib.auth.gr. Unless otherwise stated above, the record metadata were created by and belong to Aristotle University of Thessaloniki Library, Greece and are made available to the public under Creative Commons Attribution-ShareAlike 4.0 International license (http://creativecommons.org/licenses/by-sa/4.0).\nUnless otherwise stated in the record, the content and copyright of files and fulltext documents belong to their respective authors. Out-of-copyright content that was digitized, converted, processed, modified, etc by AUTh Library, is made available to the public under Creative Commons Attribution-ShareAlike 4.0 International license (http://creativecommons.org/licenses/by-sa/4.0). You are kindly requested to make a reference to AUTh Library and the URL of the record containing the resource whenever you make use of this material."] | ["Αναφορά Δημιουργού-Μη Εμπορική Χρήση 4.0 Διεθνές"] | provider; evidence_present |
| c82ac45f | Dione → Dione | ["http://creativecommons.org/licenses/by-nc-nd/4.0/"] | ["http://creativecommons.org/licenses/by-nc-nd/4.0/ Attribution-NonCommercial-NoDerivatives 4.0 Διεθνές"] | aggregator; provider pending; evidence_present |
| ca84e046 | hellanicus → pergamos | ["CC0 1.0 Παγκόσμια"] | [] | provider; not_established |
| db175fe6 | ntua → rep_ihu | ["ETDFree-policy.xml\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | [] | provider; not_established |
| e2f49c6f | ktisis → psepheda | ["Attribution-NonCommercial-NoDerivatives 4.0 International"] | [] | provider; not_established |
| f35043b8 | nemertes → rep_ihu | ["0\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EL)"] | ["Default License"] | provider; evidence_present |
| fa28678c | ktisis → psepheda | ["none"] | [] | provider; not_established |
| fc3264cd | ntua → rep_ihu | ["BookCommunity-policy.xml\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\r\n\r\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t(EN)"] | ["Default License"] | provider; evidence_present |
| fdbd7fa5 | hellanicus → pergamos | ["http://creativecommons.org/licenses/by-sa/4.0/"] | [] | provider; not_established |

## Duplicate/edition re-check and release implications

The [duplicate report](DUPLICATE_REPORT.md) covers the 558 audit identities across all eight waves and both versions. Wave 4 has no cross-split or within-split key group, with 100% coverage of PDF/provider/title keys. The full audit has 12 exact-key groups, seven crossing splits in either version (four in v2); all are retained in [duplicates.jsonl](duplicates.jsonl). Two title/year groups are disjoint bound volumes according to six fresh provider item pages. Three parliamentary page-hash groups link train and test books, but the matching train pages have zero admitted lines. The v1 lexicon page split is already whole-book train in input v2. Thirty-seven near-title/year pairs are separately marked possible. This is a metadata release, with all such findings recorded and no split or deduplication decisions applied.

The final-line duplicate counts use distinct exact-key groups active in **either v1 or v2**, including the adjudicated title/year candidates; the coverage denominator is 558 including the empty wave-4 holdout. Test-book count is the union of books in those cross-split groups. This avoids confusing the requested key-group census with independent duplicate editions or with admitted-page label leakage.

## Reproduction and hand-off

From the worktree root: `python3 docs/records/harvest/oa_rebind_v1/o2/audit_duplicates.py`, then `build_release.py`, `check_candidates.py`, `finalize_o2.py`, and `validate_release.py` from the same directory. The candidate check reuses archived provider pages on rerun. All writes are constrained to this O2 directory; inputs are rehashed before and after. Six provider item pages were the only network requests; no paid API, model generation, remote compute or PDF transfer was used.

No worker commit was created: the single `git add -- docs/records/harvest/oa_rebind_v1/o2` attempt failed with `Operation not permitted` while creating the main repository shared-worktree `index.lock`, outside the managed writable roots. The exact error is in [commit-status.json](receipts/commit-status.json). The source-bound owner helper is `python3 docs/records/harvest/oa_rebind_v1/o2/commit_o2.py` (use `--check` for validation only); it refuses drift, unrelated staged paths, unexpected output files and symlinks, and never pushes.

O2: done | dup groups cross-split: 7 (train-test 7 train-dev 3 dev-test 3) within-train: 6 | test books involved: 5 | key coverage pdf/provider/title: 94.62%/100.00%/92.11% | v2-meta1 rows changed: 25372 lines added/dropped/moved: 0/0/0 | dione pending: 9
