# T21 — Wave 1 Vouli page reads and admitted crops

**1,126 pages rendered; 779 accepted and 347 rejected by the page gate; 779 page records read using 772 unique image calls. 48,169 DocAI lines; 37,367 admitted; 10,802 rejected; 37,367 native grey PNG crops.**

All 107 receipted PDFs were processed, every page from 1 through each book's recorded count. The input is broader than the brief's 1850s description: recorded years span **1824–1916**, with **11 undated books**. Actual years and nulls are preserved; `source=vouli_parliament_1850s` is the requested batch identifier, not a verified date assertion. CC-BY-4.0, each source URL and each attribution come unchanged from local sources.json; source sites were not fetched.

Rendering: pypdfium2, scale 200/72, grayscale L PNG, compress_level=1, identical to round 1. Frozen pilot gate SHA-256 `55c2efd673ce5bca8492e4f5a3fda60ec6c6f26f1def1ca3f265c4459ad8a0e1`; the original exported stack and model hashes accompany every page. Photometric guards call the unchanged round-1 feature definitions and quality_flags with selection.json limits. Two-page spreads have no extra rejection or splitting rule; an accepted spread is one full-page DocAI request. No owner-look filter was applied, as authorized on 15 October.

7 shared-image groups occur across accepted PDF pages. Each identical image SHA has one response, reused offline under each book/page identity with its own metadata. The groups are listed in plan.json; no shared page image is read or billed twice.

Quality limits: `{"ink_min": 0.08360392207097954, "ink_max": 0.842926023391813, "component_min": 37.33299999999999, "faint_suppression_max": 0.125, "contrast_min": 70, "calibration": "300 pilot page medians, 1st/99th percentile ink; 1st percentile component contrast; maximum pilot faint-suppression share"}`

| Page-gate flag | Pages (overlapping) |
| --- | ---: |
| bad_darkest_percentile_contrast | 2 |
| bad_faintness_proxy | 2 |
| bad_ink_fraction | 4 |
| bend_scout | 207 |
| faint_components | 2 |
| faint_or_show_through_dominated | 6 |
| more_than_two_columns | 35 |
| non_body_page | 21 |
| rotated | 9 |
| table | 144 |

DocAI uses the T19 project, EU processor, pinned version, Greek hint, symbol option and ADC binding. Line layouts remain in provider order; T15 composes and inverts reported transforms before native bboxes are formed. Mean/min confidence uses symbols fully contained in each line anchor. Reader flags retain T19 semantics: <3 letters for short_line; height >1.7 × counted-line median for tall_box; mean <0.89 for low_confidence. The separate unchanged T20 admission step requires ≥10 letters and applies every rule including bad_page.

| Class | Train admitted | Dev | Test | Total |
| --- | ---: | ---: | ---: | ---: |
| greek_poly | 30,094 | 1,935 | 2,516 | 34,545 |
| greek_mono | 2,068 | 272 | 101 | 2,441 |
| greek_latin_cs | 47 | 4 | 3 | 54 |
| latin | 326 | 1 | 0 | 327 |
| cyrillic | 0 | 0 | 0 | 0 |
| **Total** | **32,535** | **2,212** | **2,620** | **37,367** |

| Admission rejection reason | Lines (overlapping) |
| --- | ---: |
| short_line | 8,696 |
| low_confidence | 4,330 |
| tall_box | 227 |
| symbol_heavy | 5,961 |
| foreign_script | 67 |
| mixed_word | 57 |
| bad_page | 93 |
| label_in_holdout | 497 |
| crop_geometry | 2 |

Hold-out: 16 of 107 books (14.95%), seeded draw 20261015 from sorted full input scope, frozen before reads: 12 test / 4 dev. O5 removed **497** new train lines equal to round-1 or Vouli dev/test labels. The new hold-out also matches **2** old round-1 train rows: [train_pool_exclusions.jsonl](train_pool_exclusions.jsonl) excludes these from the combined pool without rewriting the frozen round-1 artifacts. [train_pool.jsonl](train_pool.jsonl) is the combined training input for this wave; all equal hold-out labels are absent.

**Per-source cap:** before source balancing, Vouli supplies 30,094 / 76,688 = **39.24%** of admitted polytonic train lines after the cross-wave O5 overlay. The combined training pool retains 30,094 Vouli / 76,688 total = **39.24%**, satisfying ≤40%. 0 quality-admitted Vouli train lines are excluded only from the pool by a seeded per-source draw; their admitted records and crops remain available. `train_pool_eligible` makes this distinction explicit. The pool contains 32,535 Vouli lines across classes and 82,484 total lines. No training or shard import was launched.

Cost: **772 reserved DocAI calls; USD 1.1580 (USD 1.16 rounded), below USD 2.50**. Same T19 USD 1.50/1,000-page estimate; no free allowance deducted. This is a reservation estimate, not invoice readback. The budget ledger is `docs/records/harvest/harvest_big/vouli/google/budget.jsonl`; every image SHA occurs once. Reservations precede requests under hash locks; ambiguous attempts cannot retry. Zero Vision calls. [Offline cache replay](resume_check.json) invoked every successful cache with the provider method forbidden and changed no ledger hashes.

Failures: **0 lost pages**, **0 empty reads**, **0 pages without line layouts**; **0 transformed pages** were inverse-mapped. Admission excludes all lines on **1 bad pages**. **2 additional quality-admitted lines cannot be cropped by the unchanged T20 rule** and are rejected as `crop_geometry`; [crop_failures.json](crop_failures.json) records their native boxes, neighbours and exception. Hold-out labels from these lines remain conservatively reserved against train. [failures.json](failures.json) lists every empty/no-line page, transform and bad-page decision. Page-gate rejects are recorded, not read failures. Native DocAI layouts can still cross physical rows or contain incorrect text; the automatic checks and complete compiled pages support the owner's later review, not a human transcription guarantee.

[Sample visual QA](visual_qa.json) records a concrete retained error: `0271e3cae771-p000001-l0031` repeats the opening word and adds a partial repeated word absent from the visible printed row, yet its mean confidence is 0.952862 and it passes the unchanged T20 gates before O5. Low-confidence hallucinated text elsewhere on the sampled page is rejected. The same page prints a July 1849 session inside a book whose supplied metadata year is 1850; per-book metadata does not certify every printed page's date.

The inspected mono-class sample `3e08dd4de36e-p000018-l0036` includes the upper arc of the next printed row at its lower left edge. It follows the requested native bbox, overlap threshold and padding exactly. Pixel parity and the fixed trim rule therefore do not prove single-row glyph ownership; the example is retained for the owner's after-the-fact crop review.

Crops: T20 spatial neighbours, >15% overlap midpoint trim, then in-page 4 px horizontal / 2 px vertical padding; 20,459 trimmed. 1 labels retain standalone spacing marks. All crop hashes, dimensions, trim geometry and native source pixels were verified. Contact sheets use the unchanged T20 sheet builder: 60 random unique admitted crops per populated class, or all available when fewer than 60, with explicit empty sheets for empty classes.

Every read page has an approved-format compiled JPEG under `compiled/<actual-year-or-unknown>_<title40>_<sha6>/pNNNN.jpg`. The reusable compile_page_reads.py raster builder retains the original fonts, quartile font fit, text positions, colours, 40 px margins/gap, grey rule and JPEG q85. Only optional output naming and independent page workers were added. Validation replayed every final compiled raster, text position, JPEG hash and dimension.

**230 offline tests passed.** [Full validation](validation.json), [tests](tests.xml), [plan](plan.json), [book/page counts](books.json), [page gates](manifest.json), [records](records.jsonl), [admitted](admitted.jsonl), [rejected](rejected.jsonl), [hold-out](holdout_books.json), [summary](admission_summary.json), [cost](cost_receipt.json), [inventory](inventory.json), [original gate equivalence](gate_equivalence.json), [Git audit](git_audit.json). The T20 admission module remains byte-identical. Main worktree HEAD, index, main ref/logs, packed refs and config unchanged from the pre-render snapshot: **True**. The shared .git snapshot also records 88 changed paths, including other worktrees' branch/log/index and object records. This task issued no Git mutation commands; the complete before/after main-bookkeeping hashes and shared changes are in the audit.

| Book (actual metadata) | Year | Split | Rendered | Gate accepted / read | Lines | Admitted |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΓ΄(43) 05 ΙΟΥΛΙΟΥ 1850](https://hdl.handle.net/20.500.14199/1501) (`0271e3cae771`) | 1850 | train | 9 | 9 | 373 | 339 |
| [Προϋπολογισμός των εξόδων της Βουλής](https://hdl.handle.net/20.500.14199/91923) (`05a4cbfdcb62`) | unknown | test | 2 | 1 | 102 | 33 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΗ΄(38) 11 ΝΟΕΜΒΡΙΟΥ 1875](https://hdl.handle.net/20.500.14199/55022) (`07bc68f92367`) | 1875 | train | 4 | 4 | 160 | 136 |
| [ΣΥΝΕΔΡΙΑΣΗ ΙΘ΄(19) 20 ΝΟΕΜΒΡΙΟΥ 1887](https://hdl.handle.net/20.500.14199/56783) (`0954e4e59815`) | 1887 | test | 3 | 3 | 123 | 107 |
| [ΣΥΝΕΔΡΙΑΣΗ Β΄(2) 9 ΝΟΕΜΒΡΙΟΥ 1843](https://hdl.handle.net/20.500.14199/57978) (`0c516ea32fdb`) | 1843 | train | 3 | 3 | 124 | 108 |
| [ΣΥΝΕΔΡΙΑΣΗ ΞΕ΄(65) 23 ΙΑΝΟΥΑΡΙΟΥ 1889](https://hdl.handle.net/20.500.14199/56903) (`0d2e3015ff99`) | 1889 | test | 11 | 11 | 440 | 360 |
| [Πληροφορίαι ζητηθείσαι υπό του Βουλευτού Άρτης Κωνστ. Καραπάνου](https://hdl.handle.net/20.500.14199/93780) (`0d5814a3d03f`) | unknown | train | 1 | 1 | 132 | 35 |
| [Περί μεταρρρυθμίσεως του από 15 Δεκεμβρίου 1845 νόμου περί διοικητικής διαιρέσεωςτου Κράτους](https://hdl.handle.net/20.500.14199/94303) (`0e777453c7a8`) | 1845 | train | 3 | 3 | 366 | 298 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΔ΄(24) 8 ΔΕΚΕΜΒΡΙΟΥ 1851](https://hdl.handle.net/20.500.14199/59003) (`116a24bf9010`) | 1851 | train | 6 | 2 | 79 | 73 |
| [ΣΥΝΕΔΡΙΑΣΗ Θ΄(9) 11 ΙΑΝΟΥΑΡΙΟΥ 1871](https://hdl.handle.net/20.500.14199/24913) (`1365c8bbb0a8`) | 1871 | train | 13 | 3 | 297 | 233 |
| [ΣΥΝΕΔΡΙΑΣΗ ΙΗ΄(18) 28 ΙΑΝΟΥΑΡΙΟΥ 1849](https://hdl.handle.net/20.500.14199/116693) (`17cbdf94881f`) | 1849 | train | 4 | 4 | 159 | 123 |
| [ΣΥΝΕΔΡΙΑΣΗ Β΄(2) 17 ΔΕΚΕΜΒΡΙΟΥ 1870](https://hdl.handle.net/20.500.14199/53642) (`18167bc1e4a8`) | 1870 | train | 3 | 3 | 107 | 92 |
| [ΣΥΝΕΔΡΙΑΣΗ Π΄(80) 27 ΜΑΪΟΥ 1882](https://hdl.handle.net/20.500.14199/46440) (`182619a5630d`) | 1882 | train | 14 | 13 | 1060 | 949 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΘ΄(29) 10 ΝΟΕΜΒΡΙΟΥ 1876](https://hdl.handle.net/20.500.14199/42837) (`189ba02195ca`) | 1876 | train | 16 | 4 | 417 | 359 |
| [Περιληπτική σημείωσις των πράξεων των εργοστασίων κοπής καπνού κλπ](https://hdl.handle.net/20.500.14199/88715) (`1d3256c8ba4f`) | unknown | train | 2 | 0 | 0 | 0 |
| [ΣΥΝΕΔΡΙΑΣΗ ϞΘ΄(99) 11 ΜΑΪΟΥ 1863](https://hdl.handle.net/20.500.14199/35507) (`1f485870372f`) | 1863 | train | 10 | 10 | 990 | 450 |
| [ΣΥΝΕΔΡΙΑΣΗ ΠΒ΄(82) 17 ΑΠΡΙΛΙΟΥ 1863](https://hdl.handle.net/20.500.14199/35470) (`1ff160a5dd27`) | 1863 | train | 9 | 9 | 377 | 338 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΗ΄(58) 14 ΦΕΒΡΟΥΑΡΙΟΥ 1883](https://hdl.handle.net/20.500.14199/46566) (`206e4332c358`) | 1883 | train | 28 | 3 | 174 | 140 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΘ΄(59) 25 ΟΚΤΩΒΡΙΟΥ 1865](https://hdl.handle.net/20.500.14199/45280) (`23e59c57bd30`) | 1865 | train | 10 | 10 | 442 | 380 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΘ΄(49) 10 ΙΑΝΟΥΑΡΙΟΥ 1880](https://hdl.handle.net/20.500.14199/45410) (`240e6345063d`) | 1880 | train | 13 | 9 | 882 | 760 |
| [Επί του περί βοσκής νομοσχεδίου](https://hdl.handle.net/20.500.14199/89327) (`2495f1aad484`) | unknown | train | 1 | 1 | 117 | 102 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΓ΄(23) 7 ΔΕΚΕΜΒΡΙΟΥ 1851](https://hdl.handle.net/20.500.14199/59002) (`2bcc4d069b39`) | 1851 | train | 11 | 6 | 254 | 228 |
| [Περί τροποποιήσεως του ΤΟΕ' νόμου της 10 Οκτωβρίου 1856 έτους περί συστάσεως ταμείου των χηρών και των ορφανών των αξιωματικών του Β. Ναυτικού και του ΦΑ' νόμου της 27 Μαρτίου 1874 έτους περί συστάσεως ταμείου των αποστράτων αξιωματικών του Β. Ναυτικού](https://hdl.handle.net/20.500.14199/95493) (`32be4ecfc42d`) | 1856 | train | 3 | 2 | 241 | 195 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΕ΄(25) 5 ΙΑΝΟΥΑΡΙΟΥ 1844](https://hdl.handle.net/20.500.14199/58010) (`3445120e6970`) | 1844 | train | 7 | 7 | 293 | 266 |
| [Περί προαγωγής του κατα το άρθρον 6 του από 23 Μαρτίου 1839 νόμου περί ενοικιάσεως των ιχθυοτροφείων αδικήματος της λαθραλιείας](https://hdl.handle.net/20.500.14199/64758) (`37120de0c594`) | 1839 | test | 2 | 2 | 253 | 170 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΗ΄(58) 14 ΙΑΝΟΥΑΡΙΟΥ 1889](https://hdl.handle.net/20.500.14199/56896) (`3e08dd4de36e`) | 1889 | dev | 19 | 19 | 1767 | 779 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΗ΄(58) 14 ΜΑΪΟΥ 1887](https://hdl.handle.net/20.500.14199/24717) (`3f73a30995aa`) | 1887 | train | 14 | 3 | 385 | 363 |
| [Περί τροποποιήσεως και ερμηνείας διατάξεων τινων των νόμων ΣΜΔ΄ του 1867 και ΣΞΗ΄ του 1868 περί διαλύσεως των εν Κερκύρα διηνεκών αγροληψιών και ακυρώσεως των καταχρηστικών συμβάσεων](https://hdl.handle.net/20.500.14199/75876) (`4029e9d7c943`) | 1867 | dev | 4 | 4 | 495 | 461 |
| [Περί κυρώσεως του από 23 Δεκεμβρίου 1915 Νομοθετικού Διατάγματος περί των όρων της αναθέσεως εις την Εθνικήν Τράπεζαν ή άλλο νομικόν πρόσωπον της προμηθείας και πωλήσεως θείου και θεϊκού χαλκού δια λογαριασμόν του Κράτους](https://hdl.handle.net/20.500.14199/8968) (`4201e2b2e554`) | 1915 | train | 6 | 5 | 295 | 264 |
| [ΣΥΝΕΔΡΙΑΣΗ ΡΛΕ΄(135) 1 ΑΥΓΟΥΣΤΟΥ 1846](https://hdl.handle.net/20.500.14199/61140) (`4310963292e1`) | 1846 | train | 20 | 18 | 770 | 690 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΑ΄(21) 30 ΟΚΤΩΒΡΙΟΥ 1876](https://hdl.handle.net/20.500.14199/55122) (`4522d4e8fd58`) | 1876 | train | 5 | 4 | 163 | 139 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΑ΄(31) 5 ΔΕΚΕΜΒΡΙΟΥ 1887](https://hdl.handle.net/20.500.14199/56820) (`4523e5094991`) | 1887 | train | 9 | 9 | 634 | 292 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΗ΄(38) 12 ΑΠΡΙΛΙΟΥ 1852](https://hdl.handle.net/20.500.14199/1571) (`452f5a742630`) | 1852 | train | 4 | 4 | 256 | 195 |
| [Περί παροχών του Δημοσίου εις τα Ταμεία της Εθνικής Αμύνης και του Εθνικού Στόλου εκ των πλεονασμάτων των χρήσεων 1910 και 1911](https://hdl.handle.net/20.500.14199/64131) (`466e44f50ab7`) | 1910 | train | 4 | 3 | 200 | 170 |
| [ΣΥΝΕΔΡΙΑΣΗ Ρ΄(100) 17 ΜΑΡΤΙΟΥ 1877](https://hdl.handle.net/20.500.14199/44364) (`477888d3d8e1`) | 1877 | train | 6 | 0 | 0 | 0 |
| [ΣΥΝΕΔΡΙΑΣΗ ΟΘ΄(79) 26 ΦΕΒΡΟΥΑΡΙΟΥ 1880](https://hdl.handle.net/20.500.14199/45571) (`5090074e9fac`) | 1880 | train | 16 | 12 | 1178 | 1019 |
| [Περί της λογιστικής υπηρεσίας του Ταμείου Αμύνης και περί τροποποιήσεως διατάξεων των νόμων  ΓΚΖ΄ του 1904 ΓΡΝΖ΄ του 1906 και ΓΦΜΘ΄ του 1910 περί του ταμείου Εθνικής Αμύνης](https://hdl.handle.net/20.500.14199/69458) (`535ad352d7a7`) | 1904 | train | 18 | 14 | 754 | 665 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΔ΄(24) 11 ΙΟΥΝΙΟΥ 1885](https://hdl.handle.net/20.500.14199/47272) (`5467a109e4a5`) | 1885 | train | 17 | 0 | 0 | 0 |
| [ΣΥΝΕΔΡΙΑΣΗ ΠΣΤ΄(86) 22 ΑΠΡΙΛΙΟΥ 1863](https://hdl.handle.net/20.500.14199/34636) (`593b45a064a4`) | 1863 | train | 14 | 8 | 611 | 554 |
| [ΣΥΝΕΔΡΙΑΣΗ ΞΒ΄(62) 19 ΙΑΝΟΥΑΡΙΟΥ 1889](https://hdl.handle.net/20.500.14199/56900) (`5b698f75a768`) | 1889 | train | 7 | 7 | 281 | 224 |
| [ΣΥΝΕΔΡΙΑΣΗ Μ΄(40) 25 ΙΑΝΟΥΑΡΙΟΥ 1844](https://hdl.handle.net/20.500.14199/58003) (`5be5bc5b3ea6`) | 1844 | train | 18 | 18 | 779 | 684 |
| [ΣΥΝΕΔΡΙΑΣΗ Α΄(1) 7 ΣΕΠΤΕΜΒΡΙΟΥ 1844](https://hdl.handle.net/20.500.14199/58129) (`5c950fbb119c`) | 1844 | train | 5 | 4 | 214 | 176 |
| [ΣΥΝΕΔΡΙΑΣΗ Ε΄(5) 17 ΝΟΕΜΒΡΙΟΥ 1843](https://hdl.handle.net/20.500.14199/57957) (`5f34f629ffc3`) | 1843 | train | 5 | 5 | 217 | 151 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΑ΄(31) 2 ΜΑΡΤΙΟΥ 1896](https://hdl.handle.net/20.500.14199/14231) (`63b665a3fb0f`) | 1896 | train | 11 | 11 | 426 | 351 |
| [ΣΥΝΕΔΡΙΑΣΗ ΞΖ΄(67) 17 ΝΟΕΜΒΡΙΟΥ 1865](https://hdl.handle.net/20.500.14199/38174) (`6469abc6abd1`) | 1865 | train | 13 | 1 | 88 | 76 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΣΤ΄(26) 13 ΦΕΒΡΟΥΑΡΙΟΥ 1852](https://hdl.handle.net/20.500.14199/117331) (`65ad46153b1f`) | 1852 | train | 23 | 21 | 961 | 878 |
| [ΣΥΝΕΔΡΙΑΣΗ ΟΑ΄(71) 23 ΜΑΡΤΙΟΥ 1891](https://hdl.handle.net/20.500.14199/57316) (`671b5e17cedf`) | 1891 | train | 10 | 5 | 230 | 154 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΕ΄(55) 26 ΙΟΥΛΙΟΥ 1851](https://hdl.handle.net/20.500.14199/116979) (`68ff7ed0985f`) | 1851 | train | 24 | 24 | 988 | 908 |
| [Περί εγκρίσεως προϋπολογισμού ολικής δαπάνης δια την ανέγερσιν στρατώνος αμυντικού, έδρας λόχου, προς νότον της Αγίας Παρασκευής του χωρίου Γριζάνου](https://hdl.handle.net/20.500.14199/95154) (`6c5b4b526a58`) | unknown | train | 2 | 1 | 134 | 92 |
| [ΣΥΝΕΔΡΙΑΣΗ ΣΕ΄(205) 15 ΙΑΝΟΥΑΡΙΟΥ 1864](https://hdl.handle.net/20.500.14199/37142) (`6cc7ddf6ed4e`) | 1864 | train | 15 | 7 | 649 | 581 |
| [ΕΝΑΡΚΤΗΡΙΑ ΣΥΝΕΔΡΙΑΣΗ 18 ΟΚΤΩΒΡΙΟΥ 1871](https://hdl.handle.net/20.500.14199/53764) (`6d6305f7542e`) | 1871 | test | 4 | 4 | 125 | 116 |
| [Περί δημοτικών προσόδων, δανείων και βαρών](https://hdl.handle.net/20.500.14199/97214) (`6db81fc97db3`) | unknown | train | 48 | 4 | 415 | 343 |
| [Περί τροποποιήσεως του Νόμου ΧhΕ΄ της 16ης Οκτωβρίου 1861 περί προβιβασμών](https://hdl.handle.net/20.500.14199/67575) (`746bca682ecc`) | 1861 | train | 2 | 1 | 36 | 31 |
| [ΣΥΝΕΔΡΙΑΣΗ Ξ΄(60) 13 ΙΟΥΝΙΟΥ 1845](https://hdl.handle.net/20.500.14199/1341) (`785410af1e5b`) | 1845 | train | 2 | 2 | 85 | 79 |
| [ΣΥΝΕΔΡΙΑΣΗ ΠΘ΄(89) 15 ΜΑΪΟΥ 1846](https://hdl.handle.net/20.500.14199/61056) (`808a6f56ea4d`) | 1846 | test | 36 | 15 | 812 | 534 |
| [ΣΥΝΕΔΡΙΑΣΗ Ν΄(50) 22 ΦΕΒΡΟΥΑΡΙΟΥ 1860](https://hdl.handle.net/20.500.14199/60317) (`838d5080b03f`) | 1860 | train | 28 | 20 | 842 | 670 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΔ΄(34) 12 ΔΕΚΕΜΒΡΙΟΥ 1879](https://hdl.handle.net/20.500.14199/45317) (`8392b35378bd`) | 1879 | dev | 16 | 10 | 878 | 803 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΣΤ΄(36) 29 ΙΟΥΛΙΟΥ 1865](https://hdl.handle.net/20.500.14199/46131) (`87d27561a995`) | 1865 | train | 21 | 1 | 102 | 78 |
| [Περί τροποποιήσεως του περί δημαιρεσιών νόμου της 19 Νοεμβρίου 1864](https://hdl.handle.net/20.500.14199/92171) (`8a45d1fb9dda`) | 1864 | train | 2 | 1 | 120 | 96 |
| [Περί επεκτάσεως της ισχύος του υπ' αριθ. 807 Διατάγματος της 10 Δεκεμβρίου 1916 της εν Θεσσαλονίκη Προσωρινής Κυβερνήσεως Περί οργανώσεως της εξωτερικής υπηρεσίας της Ανωτάτης Διευθύνσεως των Δημοσίων Κτημάτων και του Εσωτερικού Αποικισμού](https://hdl.handle.net/20.500.14199/61632) (`8c8a53ab3dd7`) | 1916 | train | 8 | 7 | 856 | 777 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΔ΄(44) 13 ΦΕΒΡΟΥΑΡΙΟΥ 1867](https://hdl.handle.net/20.500.14199/46192) (`8cd0e8c1f0e5`) | 1867 | train | 5 | 4 | 404 | 366 |
| [ΣΥΝΕΔΡΙΑΣΗ ϞΒ΄(92) 12 ΙΟΥΛΙΟΥ 1848](https://hdl.handle.net/20.500.14199/116456) (`8e7c72b937d4`) | 1848 | dev | 5 | 5 | 201 | 169 |
| [ΣΥΝΕΔΡΙΑΣΗ ΙΘ΄(19) 9 ΙΑΝΟΥΑΡΙΟΥ 1863](https://hdl.handle.net/20.500.14199/35379) (`91252504a906`) | 1863 | train | 30 | 30 | 1861 | 1131 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΣΤ΄(56) 12 ΜΑΪΟΥ 1855](https://hdl.handle.net/20.500.14199/59560) (`920a5a65051f`) | 1855 | train | 14 | 13 | 797 | 538 |
| [Περί δημοτικών προσόδων, δανείων και βαρών (Ως τροποποιηθέν υπό της κυβερνήσεως, προτείνεται εις β΄ αναγνώσιν)](https://hdl.handle.net/20.500.14199/91406) (`92d580f394fe`) | unknown | train | 37 | 8 | 1173 | 393 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΖ΄(57) 02 ΙΟΥΝΙΟΥ 1845](https://hdl.handle.net/20.500.14199/1347) (`935a967cc006`) | 1845 | train | 6 | 6 | 281 | 200 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΓ΄(23) 22 ΙΟΥΝΙΟΥ 1892](https://hdl.handle.net/20.500.14199/57415) (`971b6ed3092a`) | 1892 | train | 5 | 4 | 172 | 135 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΓ΄(33) 23 ΙΟΥΛΙΟΥ 1869](https://hdl.handle.net/20.500.14199/24829) (`9dd6d49acbbc`) | 1869 | test | 16 | 9 | 755 | 692 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΖ΄(37) 10 ΑΠΡΙΛΙΟΥ 1852](https://hdl.handle.net/20.500.14199/117220) (`9e6fd8368590`) | 1852 | train | 6 | 4 | 169 | 145 |
| [ΣΥΝΕΔΡΙΑΣΗ ΞΒ΄(62) 19 ΙΑΝΟΥΑΡΙΟΥ 1877](https://hdl.handle.net/20.500.14199/44244) (`9f3aab5d3aef`) | 1877 | train | 13 | 2 | 219 | 138 |
| [Περί συμπληρώσεως των διατάξεων του άρθρου 69 του νομοθετικού Β. Διατάγματος της 31 Δεκεμβρίου 1836 περί δημοτικής αστυνομίας](https://hdl.handle.net/20.500.14199/85051) (`9fa786287967`) | 1836 | train | 1 | 1 | 125 | 96 |
| [Περί τροποποιήσεων διατάξεων του Νόμου περί στρατολογίας](https://hdl.handle.net/20.500.14199/90875) (`a42c34d162b6`) | unknown | train | 2 | 2 | 243 | 194 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΖ΄(47) 16 ΦΕΒΡΟΥΑΡΙΟΥ 1852](https://hdl.handle.net/20.500.14199/59015) (`a4fcf40ac18f`) | 1852 | train | 20 | 20 | 829 | 777 |
| [Περί ερμηνείας του νόμου της 24 Ιανουαρίου 1852 περί εξοφλήσεως των χρεών των Δήμων](https://hdl.handle.net/20.500.14199/91934) (`ae65c155bdb2`) | 1852 | test | 2 | 2 | 241 | 197 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΕ΄(25) 01 ΑΠΡΙΛΙΟΥ 1846](https://hdl.handle.net/20.500.14199/116246) (`aea7ecc2ca24`) | 1846 | train | 15 | 15 | 616 | 570 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΘ΄(49) 22 ΙΟΥΝΙΟΥ 1873](https://hdl.handle.net/20.500.14199/38356) (`aed4abe1314b`) | 1873 | train | 27 | 20 | 1714 | 1519 |
| [ΣΥΝΕΔΡΙΑΣΗ ΟΗ΄(78) 27 ΑΠΡΙΛΙΟΥ 1860](https://hdl.handle.net/20.500.14199/60345) (`aee93d1337df`) | 1860 | train | 22 | 22 | 1093 | 895 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΕ΄(45) 12 ΔΕΚΕΜΒΡΙΟΥ 1880](https://hdl.handle.net/20.500.14199/55741) (`aeef1e4e6d36`) | 1880 | train | 8 | 8 | 328 | 281 |
| [ΣΥΝΕΔΡΙΑΣΗ Δ΄(4) 16 ΝΟΕΜΒΡΙΟΥ 1843](https://hdl.handle.net/20.500.14199/57955) (`b32fc7776b85`) | 1843 | test | 3 | 3 | 138 | 118 |
| [Περί κυρώσεως της μεταξύ Ελλάδος, Βελγίου, Γαλλίας, Ιταλίας, και Ελβετίας προσθέτου συμβάσεως εις την νομισματικήν Σύμβασιν της 6 Νοεμβρίου 1885](https://hdl.handle.net/20.500.14199/83209) (`b63ac145f7c7`) | 1885 | train | 3 | 3 | 396 | 263 |
| [Δάνεια 1824 και 1825](https://hdl.handle.net/20.500.14199/75862) (`b76e3bd467e8`) | 1824 | train | 1 | 0 | 0 | 0 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΖ΄(47) 5 ΦΕΒΡΟΥΑΡΙΟΥ 1897](https://hdl.handle.net/20.500.14199/18052) (`ba1c7cd4c91a`) | 1897 | train | 5 | 5 | 195 | 157 |
| [ΣΥΝΕΔΡΙΑΣΗ Α΄(1) 8 ΝΟΕΜΒΡΙΟΥ 1843](https://hdl.handle.net/20.500.14199/57977) (`bec70ac3ff65`) | 1843 | train | 5 | 5 | 279 | 205 |
| [Έκθεσις της επιτροπής επί του ορισμού του σήματος αναγνωρίσεως των κ.κ. Βουλευτών κατά τας επισήμους τελετάς και εορτάς](https://hdl.handle.net/20.500.14199/90386) (`c01ce1ebca0d`) | unknown | test | 1 | 1 | 105 | 61 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΘ΄(39) 18 ΦΕΒΡΟΥΑΡΙΟΥ 1892](https://hdl.handle.net/20.500.14199/57355) (`c0950dc22b56`) | 1892 | train | 6 | 6 | 569 | 184 |
| [ΣΥΝΕΔΡΙΑΣΗ Γ΄(3) 15 ΝΟΕΜΒΡΙΟΥ 1843](https://hdl.handle.net/20.500.14199/57953) (`c240240e279e`) | 1843 | train | 4 | 4 | 213 | 125 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΒ΄(42) 20 ΔΕΚΕΜΒΡΙΟΥ 1879](https://hdl.handle.net/20.500.14199/45376) (`c51bdcd31a4d`) | 1879 | train | 14 | 10 | 1080 | 912 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΔ΄(24) 15 ΔΕΚΕΜΒΡΙΟΥ 1859](https://hdl.handle.net/20.500.14199/60274) (`c8e289692021`) | 1859 | train | 3 | 3 | 142 | 116 |
| [Περί αυθεντικής ερμηνείας του άρθρου 34 § 1 του νόμου υπό στοιχ. ΣΞΓ' της 16 Δεκεμβρίου 1867 περί οδοποιίας](https://hdl.handle.net/20.500.14199/79373) (`ce43459c6fca`) | 1867 | train | 2 | 2 | 243 | 94 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΣΤ΄(36) 11 ΑΠΡΙΛΙΟΥ 1855](https://hdl.handle.net/20.500.14199/59537) (`d1dd97640ccb`) | 1855 | train | 13 | 13 | 781 | 537 |
| [ΣΥΝΕΔΡΙΑΣΗ Δ΄(4) 12 ΝΟΕΜΒΡΙΟΥ 1851](https://hdl.handle.net/20.500.14199/117256) (`d2e1fea00fc5`) | 1851 | train | 4 | 4 | 186 | 146 |
| [ΣΥΝΕΔΡΙΑΣΗ ΙΒ΄(12) 10 ΔΕΚΕΜΒΡΙΟΥ 1891](https://hdl.handle.net/20.500.14199/57333) (`d6ab744aab1a`) | 1891 | train | 8 | 8 | 316 | 266 |
| [ΣΥΝΕΔΡΙΑΣΗ ΚΗ΄(28) 17 ΔΕΚΕΜΒΡΙΟΥ 1851](https://hdl.handle.net/20.500.14199/58995) (`d7059ecf7417`) | 1851 | train | 13 | 9 | 566 | 375 |
| [ΣΥΝΕΔΡΙΑΣΗ ΡΙΒ΄(112) 28 ΑΠΡΙΛΙΟΥ 1848](https://hdl.handle.net/20.500.14199/58241) (`d9b7dfa900e3`) | 1848 | train | 16 | 14 | 721 | 485 |
| [ΣΥΝΕΔΡΙΑΣΗ ΜΓ΄(43) 2 ΜΑΡΤΙΟΥ 1871](https://hdl.handle.net/20.500.14199/53698) (`da9a31d7669d`) | 1871 | train | 25 | 22 | 904 | 800 |
| [ΣΥΝΕΔΡΙΑΣΗ Δ΄(4) 18 ΝΟΕΜΒΡΙΟΥ 1850](https://hdl.handle.net/20.500.14199/117067) (`e046c3916322`) | 1850 | train | 8 | 8 | 331 | 298 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΘ΄(39) 13 ΜΑΡΤΙΟΥ 1896](https://hdl.handle.net/20.500.14199/13894) (`e1c6d3b880e6`) | 1896 | train | 18 | 18 | 748 | 591 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΖ΄(57) 3 ΜΑΡΤΙΟΥ 1860](https://hdl.handle.net/20.500.14199/60335) (`e79333756394`) | 1860 | train | 23 | 21 | 1045 | 848 |
| [ΣΥΝΕΔΡΙΑΣΗ ΟΑ΄(71) 17 ΣΕΠΤΕΜΒΡΙΟΥ 1846](https://hdl.handle.net/20.500.14199/116092) (`ee869c7b44f9`) | 1846 | train | 5 | 5 | 187 | 159 |
| [(Ανταλλαγή επιστολών μεταξύ Αιγυπτίου Υπουργού Ζουλφικάρ Πασά και Γενικού Πρόξενου της Ελλάδος στην Αλεξάνδρεια Γ. Αργυρόπουλου)](https://hdl.handle.net/20.500.14199/82315) (`eece7910fb1b`) | unknown | train | 4 | 4 | 456 | 403 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΗ΄(58) 19 ΜΑΡΤΙΟΥ 1871](https://hdl.handle.net/20.500.14199/53723) (`ef698aa554cc`) | 1871 | train | 4 | 3 | 126 | 112 |
| [Περί τροποποιήσεως και προσθήκης διατάξεων εις τον Νόμον ΑΦΚΗ΄ του 1887 περί στρατολογίας του κατά γην Στρατού, ως ετροποποιήθη δια μεταγενεστέρων τοιούτων](https://hdl.handle.net/20.500.14199/10896) (`f26baf097e5a`) | 1887 | train | 6 | 5 | 263 | 182 |
| [ΣΥΝΕΔΡΙΑΣΗ ϞΒ΄(92) 12 ΣΕΠΤΕΜΒΡΙΟΥ 1845](https://hdl.handle.net/20.500.14199/115883) (`f4e509d76b55`) | 1845 | train | 13 | 13 | 524 | 481 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΒ΄(32) 3 ΝΟΕΜΒΡΙΟΥ 1875](https://hdl.handle.net/20.500.14199/55052) (`f723eb9e115a`) | 1875 | train | 4 | 4 | 166 | 141 |
| [ΣΥΝΕΔΡΙΑΣΗ ΝΘ΄(59) 16 ΦΕΒΡΟΥΑΡΙΟΥ 1883](https://hdl.handle.net/20.500.14199/46568) (`f99b42fb2efb`) | 1883 | test | 22 | 3 | 339 | 232 |
| [Περί εγκρίσεως προϋπολογισμού ολικής δαπάνης δια την ανέγερσιν καπνοκοπτηρίου εν Αθήναις](https://hdl.handle.net/20.500.14199/78262) (`fa250d8c009a`) | unknown | test | 3 | 1 | 93 | 0 |
| [ΣΥΝΕΔΡΙΑΣΗ ΛΖ΄(37) 23 ΝΟΕΜΒΡΙΟΥ 1867](https://hdl.handle.net/20.500.14199/46259) (`fefd8ab7740f`) | 1867 | train | 12 | 12 | 1128 | 973 |

T21: done | pages: 1126/779/779 | lines: 48169 | admitted: 37367 | poly: 34545 | train: 32535 | dev: 2212 | test: 2620 | usd: 1.16 | tests: 230 passed
