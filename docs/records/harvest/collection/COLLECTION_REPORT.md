# Collection plan v1 — T28 close-out

> **Superseded for training by collection v2** (15 Oct 2026, anomaly decisions applied): 271,987 lines, see [v2/CLEAN_REPORT.md](v2/CLEAN_REPORT.md). The numbers below describe pool v1.

Offline close-out, 15 October 2026. **293,439 admitted lines** after page-split repair and 41 global train exclusions. **8/8 input artifact deliveries**, 8/8 with admitted crops. Historical Google ledger reservations total **USD 9.9450**. No network or Google calls, training, or Git writes were made by T28.

8/8 wave artifact deliveries, 8/8 with admitted crops. Wikisource delivered 12,356 evaluation crops from 400 read pages; human labels are available only for one-to-one aligned lines. Source-cap violations below remain in the manifests as requested; closing this collection does not establish that the targets or mix were met.

## Targets and gaps

Targets come directly from [plan §1](../COLLECTION_PLAN_v1.md#1-targets-and-gaps). The plan gives a combined dev+test target, so a separate dev or test quota cannot be inferred. The polytonic target row includes only recorded years 1850–1935; later or undated polytonic remains in the collection and is shown separately in the all-years pool counts. Gaps are max(target − have, 0); surpluses are not reassigned across classes.

| Class | Train target | Dev+test target | Have train | Have dev | Have test | Train gap | Dev+test gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Polytonic 1850–1935 | 120000 | 8000 | 102535 | 6738 | 23752 | 17465 | 0 |
| Modern Greek, scanned | 100000 | 5500 | 60803 | 4302 | 10748 | 39197 | 0 |
| Greek with Latin inside | 40000 | 3500 | 6019 | 661 | 1370 | 33981 | 1469 |
| Latin only | 20000 | 2300 | 11598 | 1272 | 2331 | 8402 | 0 |
| Cyrillic | 20000 | 2300 | 12269 | 424 | 3533 | 7731 | 0 |
| Total within target scope | 300000 | 21600 | 193224 | 13397 | 41734 | 106776 | 0 |
| All-years collection (reference) | — | — | 228445 | 15646 | 49348 | — | — |

Unmet class-specific quotas sum to 106,776 train and 1,469 dev+test lines; surplus held-out lines in another class do not fill those class-specific gaps.

All-years polytonic counts are 137,756 train / 8,987 dev / 31,366 test. Later parliamentary polytonic is useful but outside the target date range. Within 1850–1935 the polytonic counts are **102,535 train / 6,738 dev / 23,752 test**, leaving a scoped train gap of 17,465 and combined hold-out gap of 0. Modern-class counts follow the supplied tags; metadata OCR routing is not physical proof of a scanned page. Furniture has no admitted rows or §1 line quota.

## Pages, cost and delivery

| Wave | Artifact delivery | Rendered / accepted / read pages | Provider lines | Wave admitted | Collection admitted | Ledger USD |
| --- | --- | --- | --- | --- | --- | --- |
| 0: round1 | delivered | 1532 / 1532 / 1532 | 75061 | 61882 | 61865 | 2.8125 |
| 1: vouli | delivered | 1126 / 779 / 779 | 48169 | 37367 | 37362 | 1.1580 |
| 2: round2 | delivered | 781 / 613 / 613 | 29943 | 24430 | 24416 | 0.9195 |
| 3: parliament | delivered | 1153 / 705 / 690 | 95438 | 85042 | 85041 | 1.0575 |
| 4: openarchives | delivered | 1443 / 917 / 917 | 30788 | 25606 | 25604 | 1.3755 |
| 5: mixed | delivered | 1396 / 782 / 782 | 46515 | 33114 | 33112 | 1.1730 |
| 6: cyrillic | delivered | 663 / 566 / 566 | 37398 | 13683 | 13683 | 0.8490 |
| 7: wikisource | delivered | 400 / 400 / 400 | 14967 | 12356 | 12356 | 0.6000 |

Total read pages: 6,279; total ledger USD: **9.9450** (9.95 rounded). Round 1's 1,532 pages are reused, with zero new T20/T28 reads. Its historical ledgers cost USD 2.8125, including any DocAI and Vision pilot reservations recorded there. These sunk charges are included once, even though the plan lists wave 0 incremental spend as zero. The total is the sum of integer micro-USD budget reservations, including failed attempts, without free-tier deductions; it is not an invoice. Adapter receipt ledgers corroborate processor IDs and are not charged again. Full ledger paths, hashes and per-engine totals are in [data_provenance.json](data_provenance.json).

## Missing deliveries and bounded shortfalls

- **round1** — wave report's last nonblank line: All sheet layouts were visually inspected. Native top/bottom regions covered 48 examples. Some source boxes contain neighbouring text or text beyond the supplied label, including `83df10d25e7c4c1cefe2aed5-p000053-l0042` and `18f82018e84dda79e88e0726-p000157-l0060`; university stamp crops also need review. The crops implement the requested DocAI-box rule; these observed cases remain admitted under the specified text gates. [Visual QA examples](../round1/admission_visual_qa.json) keep this separate from the owner’s pending accuracy review. Round 1 has zero admitted Cyrillic lines, so its sheet records that empty class rather than sampling unavailable crops.
- **vouli** — wave report's last nonblank line: T21: done | pages: 1126/779/779 | lines: 48169 | admitted: 37367 | poly: 34545 | train: 32535 | dev: 2212 | test: 2620 | usd: 1.16 | tests: 230 passed
- **round2** — wave report's last nonblank line: T22: done | books: 50 | pages: 781/613/613 | lines: 29943 | admitted: 24430 | poly: 22311 | train: 19693 | dev: 703 | test: 4034 | usd: 0.92 | tests: 214 passed
- **parliament** — wave report's last nonblank line: T23: done | volumes: 72 | pages: 1153/705/690 | lines: 95438 | admitted: 85042 | mono: 46089 | poly: 37988 | train: 67527 | dev: 4856 | test: 12659 | usd: 1.06 | tests: 270 passed
- **openarchives** — wave report's last nonblank line: T24c: done | docs: 89/173 | pages: 1443/917/917 | lines: 30788 | admitted: 25606 | mono: 22128 | cs: 2254 | train: 19797 | dev: 1083 | test: 4726 | usd: 1.38 | tests: 269 passed
- **mixed** — wave report's last nonblank line: T25: done | sources: 40/40/1 | pages: 1396/782/782 | lines: 46515 | admitted: 33114 | cs: 3979 | latin: 10326 | poly: 16276 | mono: 2533 | usd: 1.17 | tests: 248 passed
- **cyrillic** — wave report's last nonblank line: T26: done | items: 13 | pages: 663/566/566 | lines: 37398 | admitted: 13683 | cyr: 13108 | latin: 575 | train: 12786 | dev: 232 | test: 665 | usd: 0.85 | tests: 192 passed
- **wikisource** — wave report's last nonblank line: T27e: done | works: 20/10 | pages: 300/100 | lines: 14967 | aligned: 2030 | admitted: 12356 | cer_el: 4.93% | cer_ru: 1.98% | usd: 0.60 | tests: 227 passed

All eight wave summaries are present; no entire input folder is absent.

From [round2/READS.md](../round2/READS.md):

> Exactly 13 initial slots/book spread 8–95%, with seeded 0–2 offsets. Failed pages can use +1/+2 neighbours only. **Accepted-page target shortfall: 37.** 63 accepted replacements. Exhausted slots are retained in [slots.json](../round2/slots.json); no extra page search weakens the frozen gate or replacement bound.

From [parliament/READS.md](../parliament/READS.md):

> **Scope shortfall:** the supplied 76,246-row catalogue has eligible proceedings in 18 of 26 requested years. Missing years: 1990, 1991, 1992, 1993, 1997, 1998, 1999, 2000. Four volumes per available year gives 72 rather than 104; the absent 32 volumes were not replaced from other years. Complete live `title:YYYY` search results also returned no eligible records for these eight years; this checks dated titles, not a claim that the repository can never acquire those proceedings. The run proceeds on the available authorized source scope, with this limitation explicit. [Probe](../parliament/missing_year_probe.json).

From [openarchives/READS.md](../openarchives/READS.md):

> The bounded overdraw is exhausted. The 130-document target remains 41 documents short; the approximate 1,500 accepted-page target remains 583 pages short. No draw beyond the authorized 173 candidates was made.

From [openarchives/READS.md](../openarchives/READS.md):

> Documents tried 173; downloaded 89; dead-link/invalid-PDF 84; skipped-size 0. Document target shortfall: 41 (bounded overdraw exhausted if nonzero). At most three download attempts per candidate. Initial page plus at most two physical neighbours; 12 accepted slots requested per document, no unbounded replacement. Accepted-page target shortfall: 583.

From [mixed/READS.md](../mixed/READS.md):

> Target 980 accepted pages; actual shortfall 198 after bounded neighbour replacements. Repository documents tried 88, downloaded/rendered 40, failed 48. No more than five selected documents per repository. Repository and IA PDFs were deleted after rendering; SHA-256, size, page count and download receipts remain.

From [cyrillic/READS.md](../cyrillic/READS.md):

> 585 sampled slots; 19 exhausted slots after bounded replacement. Approximate target: 550 gate-accepted pages; actual 566; shortfall 0. No threshold was relaxed. The script-page gate applies after paid reads and does not trigger additional requests.

From [wikisource/READS.md](../wikisource/READS.md):

> Page PNGs are grey, at most 3500 px on the long side, never upsampled, with nominal 200-dpi delivery metadata; physical source dpi must not be inferred from that metadata. Any 1920/1280 px fallback is recorded explicitly and falls below the original 2000 px target under the coordinator exception. Embedded `document.pages[*].image.content` is removed before raw responses are saved. Compiled scan / Google / human triptychs are under `harvest_big/wikisource/compiled/<lang>/<year>_<title40>/pNNNN.jpg`; unaligned human panels are marked explicitly. Native greyscale crops retain original-resolution pixels from the delivered PNG. Template encounter counts include discarded modern variant arguments; only unresolved sentinels surviving in the selected text prevent alignment. Unresolved template counts: `{"simpleleader block/s": 3, "simpleleader": 76, "simpleleader block/e": 3, "εικόνα": 5, "largeinitial": 3, "3*d": 10, "---": 11, "акут": 7, "гравис": 4, "3*": 2, "эпиграф": 2, "опечатка": 4, "αστεράκι": 5, "roman": 131, "ё": 304, "градус": 2, "нп": 3, "якорь": 2, "σλβτ": 2, "namespacenumber": 1, "#ifeq:⟦unresolved template⟧": 1, "poemx1": 2, "ы": 2, "angbr": 7, "=": 10, "float right": 1, "во": 2, "мби": 12, "right2": 2, "разделитель": 4, "χρώμα": 1}`. Hyphenation events retained: 189. All HTTP response bodies, robots files and raw source wikitext are frozen under harvest_big/wikisource.

Artifact delivery does not imply that the proposed page, source, line or mix targets were met. The source report tails and saved shortfall paragraphs above state the delivered scope and reasons.

## Split repair and global hold-out

Repairs affect collection outputs only. Eligible admitted pages are sorted by page ID, shuffled with Python Random(20261015), then assigned floor(0.70N) train, floor(0.10N) dev, remainder test. Every class and line on the same page follows that page. This explicitly replaces book-disjoint hold-out for the repaired source with page-disjoint hold-out; it is not evidence of generalization to a new book. All other source/book assignments are retained. [split_repairs.json](split_repairs.json) records every page assignment and changed ID, plus the zero-train-class scan.

### mixed / archive_b28038630

70 pages; final page allocation {'train': 49, 'dev': 7, 'test': 14}. Reason: explicit T28 wave-5 part-C lexicon repair.

| Class | Before train | Before dev | Before test | Repair train | Repair dev | Repair test | Final train | Final dev | Final test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| greek_poly | 0 | 0 | 99 | 72 | 6 | 21 | 72 | 6 | 21 |
| greek_mono | 0 | 0 | 59 | 40 | 6 | 13 | 40 | 6 | 13 |
| greek_latin_cs | 0 | 0 | 2627 | 1884 | 263 | 480 | 1884 | 263 | 480 |
| latin | 0 | 0 | 7003 | 4888 | 664 | 1451 | 4888 | 664 | 1451 |

0 additional wave/source repairs were needed for train=0 and test>0 in a populated class due to a single held-out source. Intentional Wikisource evaluation-only rows are never eligible for repair.

After repair, NFC/whitespace/DocAI-dot normalization is applied consistently with T20. All dev/test labels across all waves reserve their text; Wikisource human labels do too. The 16,693 distinct usable saved Wikisource human/Google/audit labels also remain reserved, including rejected Google labels and unaligned human source lines, preserving the wave-7 whole-work contamination exclusions. **41 train rows** moved to [rejected_global.jsonl](rejected_global.jsonl) with reason `label_in_holdout`, full normalized rows and matching hold-out references. Dev/test rows remain. Zero train/held-out label collisions remain. This union is rebuilt from the wave admitted files, not the older cumulative train_pool overlays.

| Wave | Global train exclusions |
| --- | --- |
| round1 | 17 |
| vouli | 5 |
| round2 | 14 |
| parliament | 1 |
| openarchives | 2 |
| mixed | 2 |
| cyrillic | 0 |
| wikisource | 0 |

## Class × split tallies per wave

### round1

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 46593 | 3205 | 8172 | 57970 |
| greek_mono | 1360 | 124 | 223 | 1707 |
| greek_latin_cs | 903 | 22 | 101 | 1026 |
| latin | 1078 | 14 | 70 | 1162 |
| cyrillic | 0 | 0 | 0 | 0 |
| furniture | 0 | 0 | 0 | 0 |

### vouli

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 30091 | 1935 | 2516 | 34542 |
| greek_mono | 2066 | 272 | 101 | 2439 |
| greek_latin_cs | 47 | 4 | 3 | 54 |
| latin | 326 | 1 | 0 | 327 |
| cyrillic | 0 | 0 | 0 | 0 |
| furniture | 0 | 0 | 0 | 0 |

### round2

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 17869 | 617 | 3825 | 22311 |
| greek_mono | 598 | 7 | 114 | 719 |
| greek_latin_cs | 362 | 21 | 33 | 416 |
| latin | 850 | 58 | 62 | 970 |
| cyrillic | 0 | 0 | 0 | 0 |
| furniture | 0 | 0 | 0 | 0 |

### parliament

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 29154 | 2088 | 6746 | 37988 |
| greek_mono | 37448 | 2759 | 5881 | 46088 |
| greek_latin_cs | 170 | 8 | 31 | 209 |
| latin | 754 | 1 | 1 | 756 |
| cyrillic | 0 | 0 | 0 | 0 |
| furniture | 0 | 0 | 0 | 0 |

### openarchives

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 236 | 0 | 0 | 236 |
| greek_mono | 17212 | 921 | 3993 | 22126 |
| greek_latin_cs | 1646 | 105 | 503 | 2254 |
| latin | 701 | 57 | 230 | 988 |
| cyrillic | 0 | 0 | 0 | 0 |
| furniture | 0 | 0 | 0 | 0 |

### mixed

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 13813 | 276 | 2187 | 16276 |
| greek_mono | 2119 | 170 | 242 | 2531 |
| greek_latin_cs | 2891 | 492 | 596 | 3979 |
| latin | 7372 | 1139 | 1815 | 10326 |
| cyrillic | 0 | 0 | 0 | 0 |
| furniture | 0 | 0 | 0 | 0 |

### cyrillic

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 0 | 0 | 0 | 0 |
| greek_mono | 0 | 0 | 0 | 0 |
| greek_latin_cs | 0 | 0 | 0 | 0 |
| latin | 517 | 0 | 58 | 575 |
| cyrillic | 12269 | 232 | 607 | 13108 |
| furniture | 0 | 0 | 0 | 0 |

### wikisource

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 0 | 866 | 7920 | 8786 |
| greek_mono | 0 | 49 | 194 | 243 |
| greek_latin_cs | 0 | 9 | 103 | 112 |
| latin | 0 | 2 | 95 | 97 |
| cyrillic | 0 | 192 | 2926 | 3118 |
| furniture | 0 | 0 | 0 | 0 |

## Wave rejection reasons

Original wave reasons are recomputed from rejected.jsonl and checked against each summary. Reason counts overlap; they need not sum to rejected rows. Global exclusions are additional.

| Reason | round1 | vouli | round2 | parliament | openarchives | mixed | cyrillic | wikisource |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bad_page | 152 | 93 | 236 | 165 | 235 | 1945 | 7795 | 2 |
| crop_geometry | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 |
| foreign_script | 93 | 67 | 32 | 83 | 12 | 499 | 50 | 28 |
| label_in_holdout | 221 | 497 | 7 | 756 | 42 | 15 | 19 | 0 |
| low_confidence | 4786 | 4330 | 2005 | 3311 | 856 | 4212 | 8741 | 1307 |
| mixed_word | 117 | 57 | 48 | 137 | 93 | 1091 | 695 | 23 |
| not_cyrillic_page | 0 | 0 | 0 | 0 | 0 | 0 | 12260 | 0 |
| short_line | 8632 | 8696 | 3660 | 6818 | 4440 | 6927 | 4168 | 1972 |
| symbol_heavy | 5560 | 5961 | 2233 | 3573 | 3361 | 6938 | 3114 | 1449 |
| tall_box | 1112 | 227 | 593 | 273 | 255 | 617 | 53 | 172 |

## Source shares and 40% cap

Denominator: final train rows in the same class. Hellenic Parliament, each Anemi round, each repository, and each Internet Archive item are sources. Wave-4 `openarchives_X` and wave-5 `openarchives_mixed_X` are combined as the same repository. Vouli and modern parliamentary proceedings are combined as `hellenic_parliament`, since both use the Hellenic Parliament Library repository. Original source tags stay in rows/manifests. A share strictly above 40% is a violation; exactly 40% passes. No cap thinning was performed.

| Class | Source | Train | Class train | Share | >40% |
| --- | --- | --- | --- | --- | --- |
| cyrillic | archive_AA9613308335D0B014B | 2314 | 12269 | 18.86% |  |
| cyrillic | archive_b24878935 | 1088 | 12269 | 8.87% |  |
| cyrillic | archive_bub_gb_Cmg6AQAAIAAJ | 1517 | 12269 | 12.36% |  |
| cyrillic | archive_bub_gb_mG0mAQAAIAAJ | 1554 | 12269 | 12.67% |  |
| cyrillic | archive_izvestiianabul25192530bul | 1355 | 12269 | 11.04% |  |
| cyrillic | archive_izvestiianabulga610193138bulg | 1142 | 12269 | 9.31% |  |
| cyrillic | archive_izvestiianatsars12192829tsar | 729 | 12269 | 5.94% |  |
| cyrillic | archive_izvestiianatsars1516194243tsar | 976 | 12269 | 7.96% |  |
| cyrillic | archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1594 | 12269 | 12.99% |  |
| greek_latin_cs | anemi_mixed | 507 | 6019 | 8.42% |  |
| greek_latin_cs | anemi_round1 | 903 | 6019 | 15.00% |  |
| greek_latin_cs | anemi_round2 | 362 | 6019 | 6.01% |  |
| greek_latin_cs | archive_b28038630 | 1884 | 6019 | 31.30% |  |
| greek_latin_cs | hellenic_parliament | 217 | 6019 | 3.61% |  |
| greek_latin_cs | openarchives_Dione | 407 | 6019 | 6.76% |  |
| greek_latin_cs | openarchives_KEIED | 113 | 6019 | 1.88% |  |
| greek_latin_cs | openarchives_Pandemos | 147 | 6019 | 2.44% |  |
| greek_latin_cs | openarchives_anaktisis | 262 | 6019 | 4.35% |  |
| greek_latin_cs | openarchives_apothesis | 197 | 6019 | 3.27% |  |
| greek_latin_cs | openarchives_hellanicus | 157 | 6019 | 2.61% |  |
| greek_latin_cs | openarchives_kallipos | 254 | 6019 | 4.22% |  |
| greek_latin_cs | openarchives_ktisis | 248 | 6019 | 4.12% |  |
| greek_latin_cs | openarchives_nemertes | 128 | 6019 | 2.13% |  |
| greek_latin_cs | openarchives_ntua | 233 | 6019 | 3.87% |  |
| greek_mono | anemi_mixed | 492 | 60803 | 0.81% |  |
| greek_mono | anemi_round1 | 1360 | 60803 | 2.24% |  |
| greek_mono | anemi_round2 | 598 | 60803 | 0.98% |  |
| greek_mono | archive_b28038630 | 40 | 60803 | 0.07% |  |
| greek_mono | hellenic_parliament | 39514 | 60803 | 64.99% | VIOLATION |
| greek_mono | openarchives_Dione | 2051 | 60803 | 3.37% |  |
| greek_mono | openarchives_KEIED | 2061 | 60803 | 3.39% |  |
| greek_mono | openarchives_Pandemos | 2070 | 60803 | 3.40% |  |
| greek_mono | openarchives_anaktisis | 2324 | 60803 | 3.82% |  |
| greek_mono | openarchives_apothesis | 1666 | 60803 | 2.74% |  |
| greek_mono | openarchives_hellanicus | 1900 | 60803 | 3.12% |  |
| greek_mono | openarchives_kallipos | 2089 | 60803 | 3.44% |  |
| greek_mono | openarchives_ktisis | 2021 | 60803 | 3.32% |  |
| greek_mono | openarchives_nemertes | 1471 | 60803 | 2.42% |  |
| greek_mono | openarchives_ntua | 1146 | 60803 | 1.88% |  |
| greek_poly | anemi_mixed | 13679 | 137756 | 9.93% |  |
| greek_poly | anemi_round1 | 46593 | 137756 | 33.82% |  |
| greek_poly | anemi_round2 | 17869 | 137756 | 12.97% |  |
| greek_poly | archive_b28038630 | 72 | 137756 | 0.05% |  |
| greek_poly | hellenic_parliament | 59245 | 137756 | 43.01% | VIOLATION |
| greek_poly | openarchives_Pandemos | 198 | 137756 | 0.14% |  |
| greek_poly | openarchives_anaktisis | 1 | 137756 | 0.00% |  |
| greek_poly | openarchives_apothesis | 1 | 137756 | 0.00% |  |
| greek_poly | openarchives_kallipos | 51 | 137756 | 0.04% |  |
| greek_poly | openarchives_ktisis | 2 | 137756 | 0.00% |  |
| greek_poly | openarchives_ntua | 45 | 137756 | 0.03% |  |
| latin | anemi_mixed | 600 | 11598 | 5.17% |  |
| latin | anemi_round1 | 1078 | 11598 | 9.29% |  |
| latin | anemi_round2 | 850 | 11598 | 7.33% |  |
| latin | archive_b24878935 | 161 | 11598 | 1.39% |  |
| latin | archive_b28038630 | 4888 | 11598 | 42.15% | VIOLATION |
| latin | archive_bub_gb_Cmg6AQAAIAAJ | 26 | 11598 | 0.22% |  |
| latin | archive_bub_gb_mG0mAQAAIAAJ | 8 | 11598 | 0.07% |  |
| latin | archive_izvestiianabul25192530bul | 99 | 11598 | 0.85% |  |
| latin | archive_izvestiianabulga610193138bulg | 96 | 11598 | 0.83% |  |
| latin | archive_izvestiianatsars12192829tsar | 70 | 11598 | 0.60% |  |
| latin | archive_izvestiianatsars1516194243tsar | 57 | 11598 | 0.49% |  |
| latin | hellenic_parliament | 1080 | 11598 | 9.31% |  |
| latin | openarchives_Dione | 197 | 11598 | 1.70% |  |
| latin | openarchives_KEIED | 411 | 11598 | 3.54% |  |
| latin | openarchives_Pandemos | 98 | 11598 | 0.84% |  |
| latin | openarchives_anaktisis | 249 | 11598 | 2.15% |  |
| latin | openarchives_apothesis | 516 | 11598 | 4.45% |  |
| latin | openarchives_hellanicus | 368 | 11598 | 3.17% |  |
| latin | openarchives_kallipos | 114 | 11598 | 0.98% |  |
| latin | openarchives_ktisis | 501 | 11598 | 4.32% |  |
| latin | openarchives_nemertes | 62 | 11598 | 0.53% |  |
| latin | openarchives_ntua | 69 | 11598 | 0.59% |  |

The two Parliament wave tags separately contribute:

| Class | Original source tag | Train | Class train | Share |
| --- | --- | --- | --- | --- |
| greek_latin_cs | parliament_proceedings_1975_2000 | 170 | 6019 | 2.82% |
| greek_latin_cs | vouli_parliament_1850s | 47 | 6019 | 0.78% |
| greek_mono | parliament_proceedings_1975_2000 | 37448 | 60803 | 61.59% |
| greek_mono | vouli_parliament_1850s | 2066 | 60803 | 3.40% |
| greek_poly | parliament_proceedings_1975_2000 | 29154 | 137756 | 21.16% |
| greek_poly | vouli_parliament_1850s | 30091 | 137756 | 21.84% |
| latin | parliament_proceedings_1975_2000 | 754 | 11598 | 6.50% |
| latin | vouli_parliament_1850s | 326 | 11598 | 2.81% |

## Realised mix marginals

The comparison baseline specified in T28 is modern 40 / polytonic 25 / Greek–Latin 15 / Latin 10 / Cyrillic 5 / furniture 5 percent. These are mix weights, distinct from §1 ceiling quotas. Both the total admitted pool and train-only mix are shown. No resampling was applied.

| Class | Proposed % | Pool lines | Pool % | Difference pp | Train % |
| --- | --- | --- | --- | --- | --- |
| greek_poly | 25 | 178109 | 60.70 | +35.70 | 60.30 |
| greek_mono | 40 | 75853 | 25.85 | -14.15 | 26.62 |
| greek_latin_cs | 15 | 8050 | 2.74 | -12.26 | 2.63 |
| latin | 10 | 15201 | 5.18 | -4.82 | 5.08 |
| cyrillic | 5 | 16226 | 5.53 | +0.53 | 5.37 |
| furniture | 5 | 0 | 0.00 | -5.00 | 0.00 |

Decades use recorded metadata year (unknown retained). Length is normalized label length in NFC Unicode code points, including spaces and punctuation; buckets below are T28 reporting buckets. Digit-bearing means ≥1 Unicode Nd character; all-caps means Python str.isupper() (at least one cased character, every cased character uppercase). The plan specifies no numeric decade, length, digit or all-caps marginal, so their target and gap are undefined rather than invented.

| decade | Pool lines | Pool % | Train lines | Target |
| --- | --- | --- | --- | --- |
| 1810 | 232 | 0.08 | 0 | unspecified |
| 1830 | 266 | 0.09 | 96 | unspecified |
| 1840 | 5619 | 1.91 | 4798 | unspecified |
| 1850 | 6305 | 2.15 | 5747 | unspecified |
| 1860 | 19300 | 6.58 | 14631 | unspecified |
| 1870 | 20628 | 7.03 | 15258 | unspecified |
| 1880 | 28167 | 9.60 | 18543 | unspecified |
| 1890 | 16392 | 5.59 | 14219 | unspecified |
| 1900 | 23267 | 7.93 | 17542 | unspecified |
| 1910 | 23831 | 8.12 | 18201 | unspecified |
| 1920 | 26673 | 9.09 | 22459 | unspecified |
| 1930 | 8658 | 2.95 | 6859 | unspecified |
| 1940 | 871 | 0.30 | 871 | unspecified |
| 1950 | 1116 | 0.38 | 811 | unspecified |
| 1960 | 1037 | 0.35 | 273 | unspecified |
| 1970 | 21785 | 7.42 | 16691 | unspecified |
| 1980 | 49904 | 17.01 | 39796 | unspecified |
| 1990 | 16651 | 5.67 | 13160 | unspecified |
| 2000 | 5888 | 2.01 | 4563 | unspecified |
| 2010 | 10017 | 3.41 | 8077 | unspecified |
| 2020 | 4902 | 1.67 | 4289 | unspecified |
| unknown | 1930 | 0.66 | 1561 | unspecified |

| length_buckets | Pool lines | Pool % | Train lines | Target |
| --- | --- | --- | --- | --- |
| 0-19 | 14289 | 4.87 | 11208 | unspecified |
| 20-39 | 37055 | 12.63 | 28116 | unspecified |
| 40-79 | 227627 | 77.57 | 177879 | unspecified |
| 80-139 | 14329 | 4.88 | 11128 | unspecified |
| 140+ | 139 | 0.05 | 114 | unspecified |

| Marginal | Pool lines | Pool share | Train share | Target |
| --- | --- | --- | --- | --- |
| digit_bearing | 39574 | 13.49% | 13.79% | unspecified |
| all_caps | 3324 | 1.13% | 1.08% | unspecified |

## Google versus human CER (wave 7)

| Language / mark cohort | Google lines | Aligned | Aligned share | Human characters | Edits | CER |
| --- | --- | --- | --- | --- | --- | --- |
| el | 11175 | 1737 | 15.54% | 49219 | 2425 | 4.93% |
| el / breathings | 1293 | 1293 | 100.00% | 40628 | 2078 | 5.11% |
| el / iota_subscript | 197 | 197 | 100.00% | 6658 | 388 | 5.83% |
| el / perispomeni | 803 | 803 | 100.00% | 26172 | 1272 | 4.86% |
| el / grave | 1054 | 1054 | 100.00% | 33237 | 1558 | 4.69% |
| el / dialytika | 14 | 14 | 100.00% | 427 | 39 | 9.13% |
| ru | 3792 | 293 | 7.73% | 9503 | 188 | 1.98% |
| ru / breathings | 0 | 0 | undefined | 0 | 0 | undefined |
| ru / iota_subscript | 0 | 0 | undefined | 0 | 0 | undefined |
| ru / perispomeni | 0 | 0 | undefined | 0 | 0 | undefined |
| ru / grave | 0 | 0 | undefined | 0 | 0 | undefined |
| ru / dialytika | 0 | 0 | undefined | 0 | 0 | undefined |

Figures are copied from the delivered [wave-7 summary](../wikisource/admission_summary.json). CER is NFC character edits divided by human characters before admission, conditional on one-to-one alignment and its similarity threshold; it is not an unbiased estimate over all scanned text. Mark cohorts contain full lines bearing that mark, overlap, and do not measure isolated mark accuracy. Unaligned crops have human_label=null and cannot supply human-reference evaluation.

## Schemas and trainer handoff

[admitted_all.jsonl](admitted_all.jsonl) contains one flat JSON object per row, with identical keys: `id`, `wave`, `source`, `licence`, `source_url`, `book_key`, `page_id`, `year`, `decade`, `script_class`, `split`, `label`, `human_label`, `confidence`, `bbox`, `crop_path`, `crop_sha256`, `crop_width`, `crop_height`, `read_batch`, `attribution`, `human_transcription_licence`. `book_key` is the original document key; `page_id` retains page identity for the repair audit. `crop_path` is relative to this repository root; `crop_width`/`crop_height` are native pixels, using round-1 names. `bbox` is the supplied provider box in that wave's rendered-page frame, not the post-trim crop box. `human_label` and its transcription licence are null outside Wikisource; unknown year/decade/URL/attribution stay null. Round-1 source URLs are recovered from saved selection metadata, never fetched.

[manifest_train.json](manifest_train.json), [manifest_dev.json](manifest_dev.json), and [manifest_test.json](manifest_test.json) are JSON arrays with exactly these seven fields: `crop`, `label`, `script_class`, `source`, `licence`, `wave`, `year`. `crop` aliases `crop_path`; other names match admitted rows. Labels remain Google labels; human labels are retained separately in the union.

The checked local greek-page-ocr `factory/src/import_real.rs` reads JSONL and additionally requires `id` and `doc`, accepts `train`/`val`/`reserved`, and consumes `source_dataset`/`license` aliases. The seven-field JSON arrays alone are therefore insufficient for that CLI. Companion `import_real_train.jsonl`, `import_real_dev.jsonl`, `import_real_test.jsonl`, and the combined [import_real_all.jsonl](import_real_all.jsonl) supply those fields, preserving source, licence, URL and attribution. Mapping: train→train, dev→val, test→reserved. Labels are `silver` Google labels. For repaired sources only, importer `doc` is the namespaced page ID so the importer's document-split check enforces the intentional page boundary; otherwise it is namespaced book_key. Use `--crops` equal to this repo root. No import or training was launched. Example from greek-page-ocr:

```sh
linefactory import-real \
  --records /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/import_real_all.jsonl \
  --crops /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit \
  --out /path/to/new/collection-v1-import --partition collection-v1-t28
```

[data_provenance.json](data_provenance.json) records each wave's brief, read batches, observed DocAI processor IDs, ledger USD, pages, input/admitted/remaining lines, and admission module SHA. A processor ID is null when there was no provider receipt. Anemi remains research/internal-only; per-repository licences remain recorded and unverified as in the wave inputs.

## Validation and owner review

Every one of the 293,480 input admitted rows passed uniform-schema, unique ID/path and file-existence checks before exclusions. SHA-256, PNG integrity and recorded dimensions were checked for a deterministic 2,000-row sample per nonempty wave (all rows for a wave smaller than 2,000); 16,000 crops checked, zero failures. Sampling happens before global rejection, so all final splits and excluded rows are eligible. This is sampled integrity verification, not every-file hashing or visual transcription validation.

Offline tests: **66 passed**. [validation.json](validation.json) records counts, crop sample IDs, source caps and mix marginals. [tests.xml](tests.xml) contains test outcomes; [inventory.json](inventory.json) binds inputs, code and outputs. The recorded admission-module SHA matches the current T20 module. [git_audit.json](git_audit.json) compares Git file metadata/content fingerprints before and after; Git object payloads use size/mtime metadata rather than rehashing the whole object store.

Owner after-the-fact review starts at [SHEETS.md](../../../harvest/harvest_big/collection/SHEETS.md), with absolute Finder-ready sheet paths and compiled-image folders. Original wave sheets are unchanged and may show old splits. Prior physical crop/label counterexamples remain admitted under the original text policy; this merge provides integrity and leakage checks, not owner accuracy acceptance. The wave-7 CER is limited to its aligned sample; it does not validate every Cyrillic or Greek crop.

Admission-sheet images not delivered for: wikisource. The image index lists the available compiled-image folders for owner review.

T28: done | waves: 8/8 | train: 228445 | dev: 15646 | test: 49348 | poly: 178109 | mono: 75853 | cs: 8050 | latin: 15201 | cyr: 16226 | usd_total: 9.95 | tests: 66 passed
