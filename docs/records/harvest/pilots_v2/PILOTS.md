# P1 — collection and alignment pilots

**Execution:** 544 scan-page deliveries; 539 unique paid attempts reserved; **USD 0.8085** at list price, below the USD 5 cumulative P1 cap. This is reservation accounting, not invoice readback. All published human-text labels remain **proposals pending the coordinator’s blind pixel adjudication**; released reference lines = 0.

The old collection has separate wave ledgers. P1 preserves their format in `google/budget.jsonl` and `google/docai/ledger.jsonl`; copies prepared for tracking are [reservations](receipts/p1-budget.jsonl) and [provider ledger](receipts/p1-provider-ledger.jsonl). The [authorization interpretation](receipts/authorization.json), [historical ledger hashes](receipts/prior-ledger-snapshot.json), [processor binding](receipts/processor-binding.json) and [pricing receipt](receipts/pricing.json) record the scope. Every new attempt was reserved before network I/O. No failed/ambiguous attempt is refunded by the local cap, and no free tier is deducted. [Official pricing](https://cloud.google.com/products/document-ai/pricing).

## Scope and reading rules

Collection targeted 370 pages in the six Google-read pilots. Actual front matter was added after native review found bindings among the first leaves; the original pages stay in every read denominator. IA documents remain below 40 sampled pages each. Kosmopolis has 32 and 20 pages from two issues. Three first OA downloads were physically born digital and are retained as excluded witnesses; replacement records link three actual scanned statistical publications (1962, 1974, 1982). Their unrelated metadata titles/years are not used as printed facts. These are one provider stratum, not evidence of broad OA diversity.

**Gutenberg qualification limit:** PG #69810, Blackie, *The Pronunciation of Greek* (1852), is English prose with Greek, Latin and German quotations. It credits IA as image provider without an item locator. The matched IA edition is separately bound by title/imprint/year and page headers. Only **33 Greek-bearing candidates / 50 pages = 0.66/page** qualify for the target cohort; the 802 all-language candidates cannot be used as a Greek yield. Target script is classified from the proofread label; raw OCR script counts are retained separately. This is a disclosed exploratory philology pilot. **The strict Greek-language-catalogue IA-citation pairing requested in the brief remains unqualified**; this report does not assert that condition was fulfilled.

Rasters are grayscale, maximum long side 3500 px; PDF rendering uses at most 200 dpi. All sampled pages are read, including page/detector failures, covers and zero-label leaves. Main harvest/source modules remain unchanged. G1b is imported read-only from the supplied geometry worktree; its detector cache uses this worktree’s actual page/glyph code hash.

Admission keeps main content rules and confidence ≥0.89, with the requested overlays: caps ≥3 letters; digit share ≥40%; ≥5-dot runs retained with `DOTS:n` plus literal repeated-dot canonical text; tall heading candidates get a separate crop path. Long dot runs without a contents/index pattern are not counted as leader targets. Dot counts from Google remain silver counts, not independently adjudicated physical truth. Page-quality rejection is retained, exempting heading crops from the tall-box page trigger. The shipped codec is v1; unsupported characters are rejected visibly. No codec-v2 recovery is assumed.

A usable candidate is admitted after page quality, codec-supported, G1b-negative and not an exact crop/label duplicate across the Google-read pilots. G1b positives and unresolved rows are withheld. This is a measured pipeline yield, not a released training count. Exact-identifier/URL/PDF overlap checks and unresolved semantic edition binding are recorded separately; no training, lexicon or synthetic-seed release occurs.

## Collection results

| Pilot | Fetched/rendered | Sampled/read | Lines | Admitted | + codec | Usable candidates | Rows/read page | Mixed lines | G1b + / evaluable (unresolved) | USD | 20-page sheet |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ia1850 | 115/115 | 115/115 | 2511 | 2037 | 1790 | 1657 | 14.41 | 41 (1.6%) | 88/1745 = 5.04% (45) | 0.1710 | [sheet](contact_sheets/ia1850-20-pages.jpg) |
| ia1900 | 67/67 | 67/67 | 1737 | 1547 | 1286 | 1197 | 17.87 | 15 (0.9%) | 44/1241 = 3.55% (45) | 0.0945 | [sheet](contact_sheets/ia1900-20-pages.jpg) |
| bsb | 50/50 | 50/50 | 1872 | 1734 | 1677 | 1626 | 32.52 | 225 (12.0%) | 44/1670 = 2.63% (7) | 0.0750 | [sheet](contact_sheets/bsb-20-pages.jpg) |
| elstat | 50/50 | 50/50 | 12880 | 9873 | 9760 | 7152 | 143.04 | 460 (3.6%) | 643/7795 = 8.25% (1965) | 0.0750 | [sheet](contact_sheets/elstat-20-pages.jpg) |
| kosmopolis | 66/66 | 52/52 | 4740 | 4498 | 3996 | 3603 | 69.29 | 31 (0.7%) | 24/3627 = 0.66% (369) | 0.0780 | [sheet](contact_sheets/kosmopolis-20-pages.jpg) |
| openarchives | 120/120 | 60/60 | 12396 | 9678 | 9538 | 7358 | 122.63 | 53 (0.4%) | 890/8248 = 10.79% (1290) | 0.0900 | [sheet](contact_sheets/openarchives-20-pages.jpg) |
| ajax | 68/68 | 68/0 | 3364 | 2928 | 2819 | 2040 | n/a | 921 (27.4%) | 276/2316 = 11.92% (503) | 0.0000 | [sheet](contact_sheets/ajax-20-pages.jpg) |

Ajax has 3,364 actual paired files versus the README’s stated 3,356. Of its 921 mixed lines, 783 pass content admission plus codec. Its confidence gate is inapplicable to publisher-declared human GT; content-rule and codec counts are shown rather than inventing confidence scores. The archive supplies 68 full native page images; 332 GT crop pairs belong to eight other page groups whose full-page images are absent. Those pairs remain geometry-unresolved in the denominator ([binding coverage](receipts/ajax-binding-coverage.json)). Pixel-template binding and G1b are reported separately. Original GT/images and their pinned archive remain under `bulk/ajax/`.

## Script classes, tags and admission rules

| Pilot | Raw script classes | Raw line tags (overlapping) | Accepted rule firings (overlapping) | Rejection reasons (overlapping) |
|---|---|---|---|---|
| ia1850 | cyrillic: 2; greek_latin_cs: 29; greek_mono: 239; greek_poly: 1455; latin: 507; nonletter: 279 | caps: 202; dialogue_punctuation: 89; dot_run_candidate: 4; heading: 13; numeric: 221 | base: 1815; caps_3_letters: 59; digits_40pct: 158; heading_crop: 5; leader_run: 2 | bad_page: 42; foreign_script: 5; low_confidence: 239; mixed_word: 2; short_line: 250; symbol_heavy: 168; tall_box: 16 |
| ia1900 | greek_latin_cs: 10; greek_mono: 105; greek_poly: 1245; latin: 179; nonletter: 198 | advertisement_candidate: 5; caps: 106; dialogue_punctuation: 127; heading: 9; numeric: 186 | base: 1369; caps_3_letters: 36; digits_40pct: 141; heading_crop: 5 | bad_page: 39; foreign_script: 4; low_confidence: 80; mixed_word: 3; short_line: 112; symbol_heavy: 27; tall_box: 19 |
| bsb | greek_latin_cs: 37; greek_mono: 2; greek_poly: 23; latin: 1687; nonletter: 123 | caps: 19; dialogue_punctuation: 33; dot_run_candidate: 1; heading: 1; numeric: 78 | base: 1652; caps_3_letters: 4; digits_40pct: 77; heading_crop: 1; leader_run: 1 | foreign_script: 1; low_confidence: 58; mixed_word: 4; short_line: 104; symbol_heavy: 80; tall_box: 1 |
| elstat | cyrillic: 3; greek_latin_cs: 257; greek_mono: 1233; greek_poly: 502; latin: 2032; nonletter: 8853 | advertisement_candidate: 11; caps: 148; dialogue_punctuation: 320; dot_run_candidate: 4; heading: 291; numeric: 8996 | base: 1593; caps_3_letters: 24; digits_40pct: 8183; heading_crop: 78; leader_run: 2 | bad_page: 414; foreign_script: 3; low_confidence: 1061; mixed_word: 27; short_line: 1889; symbol_heavy: 410; tall_box: 41 |
| kosmopolis | cyrillic: 1; greek_latin_cs: 29; greek_mono: 202; greek_poly: 4422; latin: 20; nonletter: 66 | advertisement_candidate: 7; caps: 85; dialogue_punctuation: 228; dot_run_candidate: 1; fiction_source: 1771; numeric: 59 | base: 4394; caps_3_letters: 54; digits_40pct: 50 | foreign_script: 1; low_confidence: 125; mixed_word: 2; short_line: 150; symbol_heavy: 17 |
| openarchives | cyrillic: 9; greek_latin_cs: 34; greek_mono: 1442; greek_poly: 1004; latin: 1929; nonletter: 7978 | advertisement_candidate: 1; caps: 250; dialogue_punctuation: 101; dot_run_candidate: 2; heading: 163; numeric: 7965 | base: 2056; caps_3_letters: 48; digits_40pct: 7483; heading_crop: 103; leader_run: 1 | bad_page: 63; foreign_script: 5; low_confidence: 773; mixed_word: 17; short_line: 2048; symbol_heavy: 204; tall_box: 288 |
| ajax | greek_latin_cs: 351; greek_mono: 161; greek_poly: 718; latin: 1943; nonletter: 191 | advertisement_candidate: 1; caps: 164; dialogue_punctuation: 45; dot_run_candidate: 1; numeric: 135 | base: 2683; caps_3_letters: 111; digits_40pct: 134; leader_run: 1 | foreign_script: 145; mixed_word: 154; short_line: 186; symbol_heavy: 141 |

Rule eligible/admitted/usable counts and fractions are in `pilots.jsonl` (`admission_rule_yield`); rule firings overlap. Script class uses the unchanged main classifier. The mixed-line flag additionally counts Greek inside Latin-majority lines; those must not disappear into the Latin-majority class. Kosmopolis fiction-source tags identify the sampled article PDFs for episodes/stories 61109, 61117, 61118 and 61120; shared pages may include neighbouring material, so this is a source-level fiction cohort rather than adjudicated line-level semantics. Explicit dialogue punctuation is counted separately. Primary allocations below are disjoint; target-coverage flags in `pilots.jsonl` overlap and must not be summed.

## Quota inputs: usable primary rows per read page

| Primary target | Target rows | ia1850 | ia1900 | bsb | elstat | kosmopolis | openarchives | Best measured source / indicative pages |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| poly1850 | 40000 | 8.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | ia1850 / 4,462 |
| poly1900 | 50000 | 0.00 | 12.81 | 0.00 | 0.00 | 0.00 | 0.00 | ia1900 / 3,905 |
| modern_scanned | 40000 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 12.63 | openarchives / 3,167 |
| mixed_greek_latin | 20000 | 0.23 | 0.18 | 4.06 | 3.84 | 0.46 | 0.17 | bsb / 4,927 |
| latin | 8000 | 3.32 | 1.51 | 27.16 | 10.68 | 0.23 | 13.00 | bsb / 295 |
| cyrillic | 12000 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | not piloted; no quota inferred from incidental rows |
| headings_caps | 6000 | 0.51 | 0.39 | 0.00 | 0.96 | 0.50 | 1.62 | openarchives / 3,712 |
| numerics_tables | 10000 | 0.69 | 1.27 | 1.04 | 121.62 | 0.92 | 95.12 | elstat / 83 |
| leaders_indices | 4000 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | not estimable; no qualifying pilot rows |
| dialogue_fiction | 12000 | 0.39 | 1.39 | 0.00 | 0.18 | 27.38 | 0.10 | kosmopolis / 439 |

These page projections use the measured primary allocation once. They do not add another admission/codec multiplier. They remain planning estimates from purposive pilots, including covers and front/back matter, and do not certify repository-wide yield. Cyrillic was not a selected collection pilot.

**Numeric unit:** a row here is a provider line crop, often one table cell or a single digit. It is not a reconstructed physical table row. The numeric projections therefore estimate cell/line examples only. BSB mixed yield is below the data plan’s 10 mixed lines/page planning assumption; this pilot does not support that assumption.

| Pilot | Usable numeric crops: 1 digit | 2–3 digits | 4–7 digits | ≥8 digits |
|---|---:|---:|---:|---:|
| ia1850 | 0 | 68 | 9 | 2 |
| ia1900 | 3 | 62 | 20 | 0 |
| bsb | 0 | 52 | 0 | 0 |
| elstat | 381 | 2436 | 3148 | 121 |
| kosmopolis | 0 | 46 | 2 | 0 |
| openarchives | 313 | 3315 | 2020 | 60 |

## Alignment release-contract accounting

| Source | Read pages | All-language label candidates | All labels/read page | Greek-bearing target labels (per page) | All retained NFD characters / proofread body | Target / all page-OCR characters | Zero all-label pages | Page witness verified | 40-line blind sheet |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| wikisource | 50 | 699 | 13.98 | 699 (13.98) | 34370/65463 (52.5%) | 52.2% | 1 | 50 | [blind sheet](blind_sheets/wikisource/sheet.html) |
| gutenberg | 50 | 802 | 16.04 | 33 (0.66) | 40000/59802 (66.9%) | 2.5% | 0 | 50 | [blind sheet](blind_sheets/gutenberg/sheet.html) |
| perseus | 50 | 491 | 9.82 | 491 (9.82) | 27843/90618 (30.7%) | 29.4% | 1 | 49 | [blind sheet](blind_sheets/perseus/sheet.html) |

NFD sequence alignment assigns only uniquely owned literal spans with anchored boundaries, ≥0.92 sequence similarity and ≥0.90 matched-atom support. These thresholds nominate candidates; Google similarity never establishes truth. Printed line-end hyphens absent from the proofread source abstain. Repeated spans, inside-word boundaries, unknown markup/editorial regions, unverified printed page numbers and G1b-positive/unresolved crops abstain.

Each candidate retains the scan hash, exact text revision/body hash, proofreading declaration, source span and raw-wikitext NFD offsets or XML/HTML XPath text-node offsets. TEI `choice` resolves only an explicit printed branch (`orig`, `sic`, `abbr`), otherwise abstains; supplied text/apparatus/notes are not flattened into body truth. PG boilerplate, moved notes/references and editorial notes are recorded transformations/excluded regions. Wikisource uses validated revision-pinned pages with zero overlap with the prior 400-page manifest.

All 50 sampled pages per source remain in coverage, including empty/zero-label pages. Proofread-body coverage and page-OCR-character coverage are separate. Neither is a full-page truth claim. Reference release is pending the 40-card accepted/rejected blind audit for each source; no judgments have been supplied. Candidate works are listed as excluded from future training/lexicon/synthetic inputs; existing global seed pools were not rewritten or certified clean by this pilot.

| Source | Alignment rejection reasons (overlapping) |
|---|---|
| wikisource | alignment_similarity_below_0.92: 25; ends_inside_proofread_word: 213; geometry_positive_or_unresolved: 125; matched_atom_coverage_below_0.90: 18; no_source_span: 125; printed_hyphen_not_owned: 276; raw_wikitext_span_not_unique_or_markup_interrupted: 76; repeated_source_span: 37; span_too_short: 62; starts_inside_proofread_word: 212; unanchored_literal_boundary: 339 |
| gutenberg | alignment_similarity_below_0.92: 111; ends_inside_proofread_word: 161; geometry_positive_or_unresolved: 62; matched_atom_coverage_below_0.90: 115; no_source_span: 253; printed_hyphen_not_owned: 163; repeated_source_span: 34; span_too_short: 31; starts_inside_proofread_word: 161; unanchored_literal_boundary: 265 |
| perseus | alignment_similarity_below_0.92: 15; editorial_or_template_region: 2; editorial_or_unresolved_text_ownership: 2; ends_inside_proofread_word: 380; geometry_positive_or_unresolved: 122; matched_atom_coverage_below_0.90: 30; no_source_span: 206; printed_hyphen_not_owned: 459; printed_page_header_not_verified: 28; starts_inside_proofread_word: 372; unanchored_literal_boundary: 898 |

Coverage includes the full normalized Document AI document text, including headers and page numbers outside the proofread body. [Every sampled page](alignment_pages.jsonl), [every accepted/rejected provider region with crop coordinates and literal ownership](alignment_regions.jsonl), and [grouped coverage/reasons](alignment_coverage.jsonl) retain the denominator. Layout and dominant script regime below are detector/classifier diagnostics, not adjudicated layout truth. No unanchored nonspace document characters were silently removed.

| Source / edition | Layout / dominant regime | Pages | Target lines / all provider lines | Target characters / all page OCR characters | Coverage | Zero-target pages |
|---|---|---:|---:|---:|---:|---:|
| gutenberg / pronunciationofg00blacuoft | multi_column_candidate / latin | 1 | 0/32 | 0/1482 | 0.0% | 1 |
| gutenberg / pronunciationofg00blacuoft | single_column_candidate / latin | 49 | 33/1451 | 1775/70854 | 2.5% | 33 |
| perseus / bub_gb_ghIMAAAAYAAJ | multi_column_candidate / greek_poly | 1 | 7/38 | 401/1957 | 20.5% | 0 |
| perseus / bub_gb_ghIMAAAAYAAJ | single_column_candidate / greek_poly | 49 | 484/1741 | 27442/92648 | 29.6% | 1 |
| wikisource / 22fda82b | multi_column_candidate / greek_mono | 2 | 5/27 | 88/474 | 18.6% | 0 |
| wikisource / 22fda82b | multi_column_candidate / greek_poly | 1 | 9/26 | 214/850 | 25.2% | 0 |
| wikisource / 22fda82b | single_column_candidate / greek_mono | 1 | 0/4 | 0/58 | 0.0% | 1 |
| wikisource / 22fda82b | single_column_candidate / greek_poly | 4 | 61/144 | 3146/6717 | 46.8% | 0 |
| wikisource / 69e993c1 | multi_column_candidate / greek_mono | 1 | 8/20 | 221/357 | 61.9% | 0 |
| wikisource / 69e993c1 | multi_column_candidate / greek_poly | 9 | 132/248 | 6860/12864 | 53.3% | 0 |
| wikisource / 69e993c1 | multi_column_candidate / nonletter | 1 | 43/104 | 437/746 | 58.6% | 0 |
| wikisource / 69e993c1 | single_column_candidate / greek_mono | 1 | 2/6 | 19/42 | 45.2% | 0 |
| wikisource / 69e993c1 | single_column_candidate / greek_poly | 30 | 439/839 | 23385/43778 | 53.4% | 0 |

## Item rights and witnesses

Rights are records, not an acquisition gate under the owner’s P1 instruction. An owner-authorised cloud read is not rewritten as a source-issued cloud licence. Every selected item has a [rights/witness record](items.jsonl); the detailed records preserve original metadata, physical corrections and unresolved fields.

| Item | Pilot | Printed/source title | Scan/text/retention/training/redistribution record |
|---|---|---|---|
| 22fda82b | wikisource | Διηγήματα | [item record](receipts/items/22fda82b.json) |
| 69e993c1 | wikisource | Βίοι Πελοποννησίων ανδρών | [item record](receipts/items/69e993c1.json) |
| 8ZSUP92_18 | ia1850 | Galatée, drame grec en 5 actes, en prose | [item record](receipts/items/8ZSUP92_18.json) |
| Wecklein1894 | ajax | Sophokleus Aias | [item record](receipts/items/Wecklein1894.json) |
| b33028709 | ia1850 | Perigraphē tōn en Kythnō, Aidipsō kai Hypatē iamatikōn hydatōn kai hodēgiai peri tēs chrēseōs autōn | [item record](receipts/items/b33028709.json) |
| bsb10234118 | ajax | Sophoclis Aiax | [item record](receipts/items/bsb10234118.json) |
| bsb11189761 | bsb | Philologus : Zeitschrift für antike Literatur und ihre Rezeption. 33. 1874 | [item record](receipts/items/bsb11189761.json) |
| bub_gb_ghIMAAAAYAAJ | perseus | Herodiani Ab excessu divi Marci | [item record](receipts/items/bub_gb_ghIMAAAAYAAJ.json) |
| cu31924087948174 | ajax | Sophocles | [item record](receipts/items/cu31924087948174.json) |
| elstat1930 | elstat | Στατιστική Επετηρίς της Ελλάδος 1930 | [item record](receipts/items/elstat1930.json) |
| greekboyathomest01rousuoft | ia1900 | A Greek boy at home, a story written in Greek; [with a vocabulary] | [item record](receipts/items/greekboyathomest01rousuoft.json) |
| historiatsnsouke00psyl | ia1900 | Historia ts nsou Keas | [item record](receipts/items/historiatsnsouke00psyl.json) |
| neoellnikaanale00unkngoog | ia1850 | Neoellēnika analekta | [item record](receipts/items/neoellnikaanale00unkngoog.json) |
| oa-GRESYE_02_0101_00033 | openarchives | Αποτελέσματα της απογραφής πληθυσμού - κατοικιών της 19 Μαρτίου 1961, τεύχος I, Δημογραφικά χαρακτηριστικά | [item record](receipts/items/oa-GRESYE_02_0101_00033.json) |
| oa-GRESYE_02_0101_00061 | openarchives | Προσωρινά αποτελέσματα της Απογραφής Πληθυσμού, Οικοδομών - Κατοικιών και Γεωργίας - Κτηνοτροφίας | [item record](receipts/items/oa-GRESYE_02_0101_00061.json) |
| oa-GRESYE_02_0201_00032 | openarchives | Δελτίον στατιστικής κοινωνικής προνοίας και υγιεινής 1972 | [item record](receipts/items/oa-GRESYE_02_0201_00032.json) |
| pronunciationofg00blacuoft | gutenberg | The Pronunciation of Greek; Accent and Quantity | [item record](receipts/items/pronunciationofg00blacuoft.json) |
| sophoclesplaysa05campgoog | ajax | Sophocles: The Plays and Fragments | [item record](receipts/items/sophoclesplaysa05campgoog.json) |
| sophokle1v3soph | ajax | Sophokles, Erstes Bändchen: Aias. Philoktetes | [item record](receipts/items/sophokle1v3soph.json) |
| xrysallis-61104 | kosmopolis | Περί μαγείας και υπερφυσικών φαινομένων / Χρυσαλλίς | [item record](receipts/items/xrysallis-61104.json) |
| xrysallis-61105 | kosmopolis | Αγγλοδανικός πόλεμος / Χρυσαλλίς | [item record](receipts/items/xrysallis-61105.json) |
| xrysallis-61106 | kosmopolis | Η ανθοδέσμη της κυρίας Πρεβώ. Ήθη και έθιμα των ανθοπωλών / Χρυσαλλίς | [item record](receipts/items/xrysallis-61106.json) |
| xrysallis-61107 | kosmopolis | Ποικίλα / Χρυσαλλίς | [item record](receipts/items/xrysallis-61107.json) |
| xrysallis-61108 | kosmopolis | Τα εν τω Πολυτεχνείω εκτεθέντα του έτους τούτου διαγωνίσματα / Χρυσαλλίς | [item record](receipts/items/xrysallis-61108.json) |
| xrysallis-61109 | kosmopolis | Οι οπαδοί του Ιηού / Χρυσαλλίς | [item record](receipts/items/xrysallis-61109.json) |
| xrysallis-61112 | kosmopolis | Περί πώγωνος / Χρυσαλλίς | [item record](receipts/items/xrysallis-61112.json) |
| xrysallis-61113 | kosmopolis | Αι προς απελευθέρωσιν της αγίας γης γενόμεναι σταυροφορίαι / Χρυσαλλίς | [item record](receipts/items/xrysallis-61113.json) |
| xrysallis-61114 | kosmopolis | Βιβλιογραφία : Μύθοι του Λαφονταίνου εκ του γαλλικού / Χρυσαλλίς | [item record](receipts/items/xrysallis-61114.json) |
| xrysallis-61117 | kosmopolis | Οι οπαδοί του Ιηού / Χρυσαλλίς | [item record](receipts/items/xrysallis-61117.json) |
| xrysallis-61118 | kosmopolis | Ο τέταρτος / Χρυσαλλίς | [item record](receipts/items/xrysallis-61118.json) |
| xrysallis-61119 | kosmopolis | Τίνι τρόπω γράφονται τα μυθιστορήματα / Χρυσαλλίς | [item record](receipts/items/xrysallis-61119.json) |
| xrysallis-61120 | kosmopolis | Το μελετηθέν έγκλημα / Χρυσαλλίς | [item record](receipts/items/xrysallis-61120.json) |

## Artifacts and limitations

- [Pilot records](pilots.jsonl), [all page witnesses including exclusions](pages.jsonl), [item records](items.jsonl), [line-file manifest](lines_manifest.jsonl), [page-quality decisions](page_quality.jsonl), [file inventory](FILES.tsv).
- Bulk raster pages, original downloads, raw Google responses, native crops, detector caches and row/alignment ledgers are ignored under this directory. Contact and blind sheets remain available locally at their linked paths.
- The [geometry source receipt](receipts/source-bindings.json), [admission contract checks](receipts/admission-contract-check.json), [budget checks](receipts/budget-contract-check.json) and [validation](receipts/validation.json) bind the methods. G1b thresholds are inherited diagnostics in a new source population; positives are not adjudicated error prevalence.
- Source sampling is purposive, not representative. The OA pilot is restricted to three scanned statistical publications. The Gutenberg scope and provider-credit limitation are explicit above. Dot counts remain silver until native adjudication. No proposed label, crop repair or source exception was promoted into a production dataset.
- The [Gutenberg qualification evidence](receipts/gutenberg-qualification.json) binds the bounded S1 census and full Fairley follow-up. It does not assert that no qualifying ebook exists.
- Interactive browser QA was blocked by the managed environment. [Representative static raster inspection](receipts/visual-qa.json) and all-card/link checks are recorded separately from unperformed browser UI verification.
- Git staging/commit was blocked because the shared worktree index is outside the writable roots; no files were staged or committed. The [source-bound staging handoff](README.md) and `receipts/git-handoff.json` record the exact normal-terminal continuation. Bulk files are not candidates for Git tracking.

Footer geometry denominator: 1733/24326 evaluable admitted+codec collection rows (six Google pilots; Ajax reported separately). Footer alignment yields count Greek-bearing target candidates; coverage is their retained NFD characters divided by all sampled page-OCR NFD characters. The auxiliary English/Latin-only labels are not counted as Greek reference yield. Footer collection yields are the disjoint primary focus-class yields: historical/later polytonic, mixed Greek+Latin, numeric tables, fiction/dialogue and modern scanned Greek respectively. All-class yields are kept in the first table.

P1: done | pages_read: 544 usd: 0.8085 | collection: ia1850 8.97 ia1900 12.81 bsb 4.06 elstat 121.62 kosmopolis 27.38 openarchives 12.63 ajax 2819 | geometry_positive: 7.12% | alignment: wikisource 13.98 gutenberg 0.66 perseus 9.82 coverage 27.48% | sheets: 13

## P1b

**Executed on `sol/source-inventory`, baseline head `1fe86c33`.** All 150 original pages and all 4,680 provider regions remain in the rerun. **New Google reads: 0; new spend: USD 0.00.** P1 pages, crops, raw responses, ledgers and original blind packs were preserved. [Baseline hashes](p1b/baseline.json), [cached-input bindings](p1b/cached_inputs.jsonl), [before/after summary](p1b/summary.json), [validation](p1b/validation.json). Labels remain proposals for second adjudication; released training/reference lines = 0. The requested strict replacement Gutenberg witness remains **unqualified**, as detailed below.

The earlier P1 sections are a historical snapshot. The [first adjudication](adjudication_20261016/notes.md) supplied 60 matching / 60 nonmatching cards, with no wrong-line findings; the old “no judgments supplied” wording describes the baseline handoff only. P1b has no second-round judgments yet.

### Yield and coverage on the same pages

| Source | Pages | Greek-bearing proposals before → after | Labels/page before → after | Target source-span NFD / full page OCR NFD before → after | Target page-OCR coverage before → after | All-language body coverage before → after |
|---|---:|---:|---:|---|---:|---:|
| wikisource | 50 | 699 → 1107 | 13.98 → 22.14 | 34,370/65,886 → 57,748/65,886 | 52.17% → 87.65% | 52.50% → 88.21% |
| perseus | 50 | 491 → 1067 | 9.82 → 21.34 | 27,843/94,605 → 60,451/94,605 | 29.43% → 63.90% | 30.73% → 66.80% |
| gutenberg | 50 | 33 → 55 | 0.66 → 1.10 | 1,775/72,336 → 2,943/72,336 | 2.45% → 4.07% | 66.89% → 90.23% |

All-language labels are Wikisource 699→1,107, Perseus 491→1,067 and Gutenberg 802→1,085. Gutenberg’s Greek-bearing yield is 33→55, not its English/Latin total. Zero-Greek-label pages are Wikisource 1→1, Perseus 1→1 and Gutenberg 34→30; covers/empty/failed regions remain in all denominators. These are proposal yields, not measured pixel accuracy.

Coverage uses the same full cached page-OCR NFD denominators as P1. The numerator counts owned characters in the prepared proofread source, with added edge glyphs separately recorded. Actual rendered Greek-bearing labels have 58,261 / 61,023 / 2,970 NFD characters (Wikisource / Perseus / Gutenberg). The Perseus prepared-body denominator changes 90,618→90,495 because the explicit ligature repairs collapse 123 damaged source atoms; previous-page context is excluded from that denominator. Its raw XML remains unchanged. Source-node ownership is checked across pages as well as within each page.

### Repairs, abstentions and triage

- **Printed edges:** letter/mark matching uses a disposable projection; labels use literal proofread atoms plus explicitly owned cached-reader edge punctuation. Hyphens, apostrophes, dialogue dashes and quotes survive at both edges. An inside-word end without a printed split glyph abstains. A following fragment needs a preceding printed hyphen and contiguous source ownership, or explicit previous-TEI-page context. No page-read letter is substituted for a proofread letter. `edge_fixed=1,033` counts regions where a requested edge glyph was absent/different in the baseline candidate; 830 of these are eligible proposals. It is a rule-firing count over accepted and rejected regions, not 1,033 newly adjudicated fixes.

- **Perseus `ȣ`:** the actual pinned TEI already has `Σἑ??ʼ`, `Ῥἁ??ʼ`, `Ἀδ̔??ʼ`; it does not contain a raw `ȣ` to preserve. Only these three adjudicated name families receive an explicit node-offset-bound repair to U+0223. Existing U+0223 is preserved unchanged. Other `??` corruption abstains. Forty baseline candidates containing the damaged strings now contain `ȣ`; 41 current candidates contain `ȣ`, of which 25 otherwise qualify. The raw source and hash are retained, and every nonliteral atom records its repair. Printed `·` replaces `:` only where the cached reader supplies it; a consonant-attached breathing used as an elision apostrophe likewise has an explicit printed-punctuation correction.

- **Codec discrepancy:** the checked local `greek-page-ocr/codec/v2.proposed.json` lacks U+0223, contrary to the brief. [Exact file/hash check](p1b/codec_support.json). P1b preserves the glyph in proposals and tags `codec_v2_ou_ligature`; it neither folds/drops the glyph nor silently changes a codec or promotes a training release.

- **Margin numerals:** a narrow digit token, spatially separated from letter-bearing tokens at either edge and physically inside the native crop, produces `margin_numeral_in_crop` and withholds the label. Tokens assigned to a different provider line are still considered if their ink lies in this crop. Internal prose numerals and numerals outside the crop are not withheld by this rule. All 12 original contaminated cards are caught; 390 regions are withheld across the pilot, plus 47 unresolved edge-number cases. No raster trimming or detector/G1b reevaluation is claimed.

- **Carried fragments:** P02, P04, P06 and P14 now start `ελθεῖν`, `τος`, `λευσε,`, `κρῖνος` respectively. Their source atoms come from the preceding TEI page’s final joined word. The body/previous-page boundary and original XML node offsets remain explicit; no source atom is assigned twice across accepted lines.

- **Wikisource disagreements:** 210 otherwise eligible labels carry `disagrees_with_page_read`; another 75 flagged candidates fail independent gates. This is deliberately a broad owner/ink queue, not a claim that Google is correct. Of the 210 eligible labels, 181 have a repeated edit signature in the cached pilot; single observations remain identifiable in `disagreement_evidence`. Expanded duplicate hyphenation is also flagged even when the printed prefix can be owned. The proofread letters/accents are retained. [Owner-first queue](p1b/owner_ink_checks.html), [machine-readable queue](p1b/owner_ink_checks.jsonl). Gutenberg spelling and printed misprints remain source-faithful.

Known residuals are not hidden: original W17/W29/W34 still fail independent similarity/support gates; W15/W26 remain poor geometry/text witnesses. Gutenberg G17’s internal `μυρἴ` disagreement remains a second-audit case. Margin-contaminated crops appear in the blind delta pack with their improved text but remain withheld. [Every original card’s new text and disposition](p1b/original_card_regressions.jsonl).

### Second blind adjudication

[Delta blind index](p1b/delta_blind/index.html) has two deterministic shuffled packs: **focus: 87 cards = all 57 changed original cards + 30 unchanged controls**; **complete: 1,542 cards = all 1,512 changed pilot regions + the same 30 controls**. Each has exactly ten unchanged controls per source. The complete pack has 39 parts of at most 40 cards. Rejected proposals are included when their displayed text changed. Admission-only changes are separately recoverable from the region ledger.

Native PNGs are byte-identical anonymous copies with full-page context. The sheets expose no old labels, source names, release status, flags, change/control identities or adjudication outcomes. Unblinding keys live separately in `p1b/delta_keys/`; do not give those or the owner queue to the blind adjudicator. [Pack counts](p1b/delta_summary.json). All links, native hashes, controls, source-node reconstruction and inside-word release invariants passed. Browser rendering could not be verified: the managed environment closed installed Chrome during headless launch, and the bundled Playwright browser is absent. [QA receipt](p1b/visual_qa.json).

### Gutenberg replacement witness and spend boundary

No strict replacement was qualified. The cached 221-ebook Greek catalogue and front-matter census were rechecked at the atom level: only PG 32549/37641 (Athanasius) and PG 57629 (Lucian/Rouse) have substantial preserved polytonic prose; these are ancient/bilingual material, not the requested katharevousa/demotic witness. This is a bounded search, not a claim that no qualifying ebook exists.

The concrete Modern Greek candidate [PG 36205, *Η Φόνισσα*](https://www.gutenberg.org/ebooks/36205) names the 1912 Fexis edition, but its cached transcription is monotonic. An IA search finds [an upload of *Η Φόνισσα*](https://archive.org/details/20251019_20251019_1610), whose metadata says 1903; it is not a certified 1912 edition binding and is not cited by the PG credits. The Gutenberg community-text mirror is a mirror of the ebook, not an independent original-scan witness. It would be misleading to replace the pilot with this pair or silently restore missing diacritics from OCR. [Discovery/qualification receipt](p1b/gutenberg/witness.json). No replacement 50-page scan set was fetched because the candidate failed qualification first.

**A new 50-page Enterprise Document OCR read would reserve USD 0.0750** at USD 1.50/1,000 pages, without a free-tier deduction ([official pricing](https://cloud.google.com/products/document-ai/pricing), checked 2026-10-16). That is a future-read estimate, not spend. No read was attempted and no budget authorization is inferred. The same original Gutenberg 50-page cohort supplies the before/after numbers above.

### Reproduction and handoff

Run `/usr/bin/arch -x86_64 python3 docs/records/harvest/pilots_v2/align.py`, then `delta_p1b.py`, `validate_p1b.py`, `report_p1b.py` and `make_files.py` under the same directory. `align.py` now routes to the cached-only runner and writes only `p1b/`, leaving historical P1 outputs intact. The x86_64 invocation matches the installed Pillow/lxml wheels; native-arm `python3` cannot load those wheels. The runner has no provider-read path.

**Tests: 170 passed** (`tests/test_p1b_alignment.py`, `tests/test_wikisource.py`, `tests/test_harvest_admission.py`); 31 are new focused regressions for printed edges, absent-edge abstention, carried fragments, explicit ligature repair, ano teleia and margin geometry/release. The original source/admission suites also pass. [Test receipt](p1b/tests.json). The [P1b validator](validate_p1b.py) passes 53,346 contract/link/ownership checks; those do not replace the requested second pixel adjudication. [File inventory](FILES.tsv) includes the new methods, reports, keys, sheets, cached-input bindings and test file, plus ignored bulk by hash. No Git commit was requested or created.

P1b: done | labels/page: wikisource 13.98→22.14 perseus 9.82→21.34 gutenberg 0.66→1.10 | edge_fixed 1033 ȣ_fixed 40 margin_withheld 390 disagree_flags 210 | delta_sheet: docs/records/harvest/pilots_v2/p1b/delta_blind/index.html | tests: 170 passed
