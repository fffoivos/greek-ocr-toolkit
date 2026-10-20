# Adjudication request — dossier 032: anemi_round1 / 3cb3c1caf7324ded3b11c1e5

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Εθνογραφικαί Σελίδες : το Πατριαρχείον της Αλεξάνδρειας, το κλίμα και η δικαιοδοσία αυτού: Εκλιπούσαι Εκκλησίαι / Γεωργίου Κλεάνθους Σκαλιέρη.
- Source / key: `anemi_round1` / `3cb3c1caf7324ded3b11c1e5` (wave `round1`), year 1927
- Admitted lines: 885 on 11 pages; split {'train': 885}
- Script classes of its lines: {'greek_poly': 630, 'latin': 162, 'greek_latin_cs': 61, 'greek_mono': 32} (majority `greek_poly`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 4.5 (rank 32 of 557): 3 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 1.5; selected as top-60 by suspicion.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:greek_book_other_lang_gt2pct** (weight 1) — 9.83% of lines guessed as another language than el {'fr': 84, 'it': 2, 'de': 1} > 2% (same-class book p95 6.87%)
- **C:hard_oov_pool** (weight 0.5) — book OOV share (pool vocab, support<=1 book)=0.2533 > greek_poly book p95=0.1995 (N=370 books) — discount: class p5/p95 rule, ~5 % of books flagged by construction (C Limits)
- **D:page_line_count_outlier** (weight 0) — 3 page(s) above and 0 below the round1 page line-count p99/p1 — discount: wave p1/p99 page rule, ~1 % of pages per side by construction (D §9)

Aspect A features beyond 2σ vs same-class books (3): latin_share_mean z=+3.0 (value 0.1774); greek_share_mean z=-3.0 (value 0.8226); other_language_share z=+2.1 (value 0.0983)
Aspect B features beyond 2σ vs same-class books (1): share spacing_apostrophe z=+2.5 (value 0.1718)
Aspect C features beyond 2σ vs same-class books (1): oov_pool_share z=+2.6 (value 0.2533)

Context: majority language `el`, other-language share 0.0983; other-script residue lines 0 (unexplained 0); B line-flag counts {'digit_heavy': 3, 'punct_heavy': 14, 'all_caps': 2, 'long_token': 5, 'word_length_outlier': 18, 'repeated_run': 1, 'final_sigma_error': 1, 'spacing_apostrophe': 152}; C line-flag counts {'cpp_out_of_range': 34, 'cpp_vs_book_out': 35, 'conf_mean_low': 19, 'conf_min_low': 20, 'aspect_out': 2, 'oov_pool_high': 33, 'cph_out_of_range': 61, 'repeated_word': 6}; median confidence 0.935; two-column book True, column-crossing share 0.001.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `3cb3c1caf7324ded3b11c1e5-p000044`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `3cb3c1caf7324ded3b11c1e5-p000007-l0036` | greek_poly | 0.9431 | – | καὶ αἱ τοῦ Πρασίνου ἀκρωτηρίου ἦσαν παλαιόθεν γνωσταί, ὅτι ἡ Μαυρι- |
| 2 | random | `3cb3c1caf7324ded3b11c1e5-p000007-l0152` | greek_poly | 0.9184 | – | τό των ὀρίων, ἃ διέγραψαν καὶ ἐπύκνωσαν δύο προλήψεις. ἡ Αἰγυπτιακή |
| 3 | random | `3cb3c1caf7324ded3b11c1e5-p000007-l0160` | greek_poly | 0.9466 | – | πρὸς τὰς ἀρχαίας προχριστιανικὰς καὶ μεταχριστιανικὰς πηγάς, θὰ πει |
| 4 | random | `3cb3c1caf7324ded3b11c1e5-p000010-l0026` | greek_poly | 0.9225 | – | Αἴγυπτος ἢ κυρίως, ἰδίᾳ Αἴγυπτος ἐλέγετο ἡ δυτικῶς τῆς |
| 5 | random | `3cb3c1caf7324ded3b11c1e5-p000010-l0028` | greek_poly | 0.93 | – | αὐτοκρατορικὴ δὲ |
| 6 | random | `3cb3c1caf7324ded3b11c1e5-p000010-l0049` | greek_poly | 0.9093 | – | σον χώρα, ἦτο ἡ Αὐτοκρατορικὴ καὶ ἡ πρὸς δυσμάς, ἡ ἐντεῦ- |
| 7 | random | `3cb3c1caf7324ded3b11c1e5-p000010-l0071` | greek_poly | 0.9495 | – | μέση Αἴγυπτος, ἀποτελουμένη ἐκ τῶν νομῶν Μεμφίτου, Ἡρα- |
| 8 | random | `3cb3c1caf7324ded3b11c1e5-p000024-l0070` | greek_poly | 0.9217 | – | κον εἰς φῶς καὶ ἔδειξαν τὸ θαυμαστὸν ἔργον τῶν μοναχικῶν ἢ |
| 9 | random | `3cb3c1caf7324ded3b11c1e5-p000024-l0078` | greek_poly | 0.9497 | – | καὶ οὗτοι μεταγενέστεροι, ἐν γλώοσῃ δημοτικὴ αἰγυπτιακῇ, τη |
| 10 | random | `3cb3c1caf7324ded3b11c1e5-p000024-l0080` | greek_poly | 0.9275 | – | αὐτὰ τὰ γράμματα ἐλήφθησαν. αν. Ἡ προκαλέσασα ἰδιαίτατα τὸ |
| 11 | random | `3cb3c1caf7324ded3b11c1e5-p000028-l0113` | greek_poly | 0.9573 | – | γενόμενοι, ἐπεβοήθουν καὶ ἐνίσχυον τὸ προστασίας |
| 12 | random | `3cb3c1caf7324ded3b11c1e5-p000034-l0017` | greek_poly | 0.9375 | B:spacing_apostrophe | ἐκλιπούσης τῆς ᾿Αλεξανδρείας τρισενδόξου Ἐκκλησίας. ᾿Αλλὰ |
| 13 | random | `3cb3c1caf7324ded3b11c1e5-p000034-l0070` | greek_poly | 0.9462 | – | θοδόξων, τῶν ὀρθοτομούντων τὸν λόγον τῆς ἀληθείας, τὰ σωστικὰ δό- |
| 14 | random | `3cb3c1caf7324ded3b11c1e5-p000034-l0075` | greek_poly | 0.9661 | B:word_length_outlier | ἐθνικῆς συνειδήσεως συγκρότησιν χαώδους παγχριστιανικῆς |
| 15 | random | `3cb3c1caf7324ded3b11c1e5-p000044-l0012` | latin | 0.9893 | – | glo égyptien, auj. Gébel Barkal. |
| 16 | random | `3cb3c1caf7324ded3b11c1e5-p000044-l0021` | latin | 0.95 | A:lang_ne_book, A:script_share_outlier | Νεῖλος, ου, (δ), Nil, fl. Égypte et Éthiopie ; Νείλου Δέλτα, |
| 17 | random | `3cb3c1caf7324ded3b11c1e5-p000044-l0078` | latin | 0.9702 | A:lang_ne_book | Basse-Egypte, auj. Kafr ed-Daoûar. |
| 18 | random | `3cb3c1caf7324ded3b11c1e5-p000046-l0079` | latin | 0.9154 | – | Συκάμινος Ἱερά, (7), Hiera sycamminos, v. Basse-Nubic, |
| 19 | random | `3cb3c1caf7324ded3b11c1e5-p000051-l0035` | greek_poly | 0.9351 | – | βαρβάρων, ἣν ἀπέτρεψαν τοῦ Βυζαντιακοῦ Κράτους οἱ ἀπα- |
| 20 | random | `3cb3c1caf7324ded3b11c1e5-p000051-l0075` | greek_poly | 0.9362 | B:spacing_apostrophe | οἱ Κᾶρες, οἱ Ἴωνες, οἱ ᾿Αχαιοί, οἱ Τυρσηνοί, οἱ Δαναοί |
| 21 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000007-l0073` | greek_poly | 0.9233 | B:spacing_apostrophe, B:word_length_outlier, C:cph_out_of_range, C:cpp_vs_book_out | σύνθεσις τῶν ἐν τῇ ᾿Α- |
| 22 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000018-l0087` | greek_poly | 0.9258 | A:mark_density_low, B:spacing_apostrophe, B:word_length_outlier, C:oov_pool_high | ᾿Αδρυμήτου, Ηρακλείας, Ιουστινιανῆς |
| 23 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000010-l0072` | greek_mono | 0.9421 | B:spacing_apostrophe, B:word_length_outlier, C:conf_min_low, C:oov_pool_high | κλεοπολίτου, ᾿Αρσινοΐτου, ᾿Αφροδιτοπολίτου, Οξυρυγχίτου. Κυ- |
| 24 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000010-l0065` | greek_poly | 0.9206 | C:cph_out_of_range, C:cpp_vs_book_out, C:repeated_word | τῆς Λιβύης Λιβύης χώρας, χώρας, ἡ ἡ αὐτοκρατορικὴ αὐτοκρατορική Αἴγυπτος, ἀποτελουμένη |
| 25 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000007-l0055` | greek_poly | 0.9042 | B:spacing_apostrophe, C:cph_out_of_range, C:cpp_vs_book_out | ἠγείροντο ᾿Εκκλησίαι |
| 26 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000044-l0053` | latin | 0.9345 | A:lang_ne_book, D:column_crossing_line, D:column_merge_line | Νιτρία, ας, (ἡ), Nitria, 1. v. Basse-Egypte, auj. Bir Hooker, HID première, Algérie occidentale, auj. Djemilah. |
| 27 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000044-l0077` | greek_latin_cs | 0.9342 | B:punct_heavy, B:word_length_outlier, C:conf_min_low | Πάθνη, ης, (ἡ), Πάφνη, ης, (ἡ), la même que Φάτνη, ν. |
| 28 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000044-l0068` | latin | 0.9093 | A:lang_ne_book, B:punct_heavy, C:cph_out_of_range | Σόϊς, εως, (ἡ), Ξόη, ης, (ἡ), Xoïs, v. Basse-Égypte, auj.Saha. |
| 29 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000007-l0012` | greek_mono | 0.9059 | C:conf_mean_low, C:cph_out_of_range, C:cpp_vs_book_out | μαρτιροίσαι |
| 30 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000046-l0014` | latin | 0.9298 | A:lang_ne_book, B:punct_heavy, C:conf_min_low | Σάπη, ης, (ή), Σαπαϊκή, ῆς, (†), Sapé, Sapaïque, v. et pays |
| 31 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000028-l0025` | greek_poly | 0.9578 | A:mark_density_low, B:long_token, B:word_length_outlier | τικὸς πατριάρχης Κωνσταντινουπόλεως Νεστόριος, |
| 32 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000028-l0110` | greek_poly | 0.9114 | A:mark_density_high, C:cph_out_of_range, C:cpp_vs_book_out | Οὗτοι καὶ οἱ παρὰ |
| 33 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000040-l0020` | greek_latin_cs | 0.9328 | A:homoglyph_word, B:spacing_apostrophe | κ΄) ᾿Αδουλίτιδος ἢ ᾿Αδουλιτικῆς, Adulitis ou Adulitique, 32-33. |
| 34 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000051-l0029` | greek_poly | 0.9043 | B:repeated_run, B:spacing_apostrophe | ἀρ. ΙΙΙΙ) τὴν ἐπαρχίαν τῆς Βυζαντιακῆς ᾿Αφρικῆς, ἐκκλήσια- |
| 35 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000028-l0017` | greek_poly | 0.8959 | B:spacing_apostrophe, C:repeated_word | 15) Μεταξὺ τῆς Συήνης Συήνης (Ασου (᾿Ασουάν) καὶ τῶν Ὄμβρων, |
| 36 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000018-l0120` | greek_poly | 0.9223 | B:spacing_apostrophe, C:oov_pool_high | 4. Υπέκειντο τῇ ᾿Επισκοπῇ καὶ αἱ παρακείμεναιν ησίδες Γαῦλος |
| 37 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000010-l0010` | greek_poly | 0.9392 | C:cpp_vs_book_out, C:repeated_word | μέσης Αἰγύπτου, ττου, καὶ καὶ δύο δύο τῆς τῆς ἄνω Αἰγύπτου, τῆς Θηβαΐδος, ὑ |
| 38 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000040-l0038` | greek_latin_cs | 0.9016 | B:punct_heavy, B:spacing_apostrophe | ᾿Ερυθραί, ῶν, (αἱ), ᾿Ερυθρά, ᾶς, (ἡ), Erythræ, Erythra, |
| 39 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000044-l0070` | latin | 0.9474 | A:lang_ne_book, B:spacing_apostrophe | ᾿Οσαία, ας, (ἡ), Osoea, la même qu' ᾿Αριστιανή, ν. Sardai- |
| 40 | anomalous | `3cb3c1caf7324ded3b11c1e5-p000022-l0097` | greek_mono | 0.9668 | B:spacing_apostrophe, C:oov_pool_high | ᾿Αδήδου κώμην (Δαουασίρ), |

Pool-wide LINE-LEVEL rules that will be applied to every book anyway (do not answer DROP_PATTERN/RELABEL just for these, unless this
book shows them at an unusual rate or in a form the rule would miss):
- breathing/accent on a capital written as a separate spacing mark (`᾿Α`) is normalised to the precomposed capital (`Ἀ`);
- the University of Crete library stamp (`ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ`), `ΒΙΒΛΙΟΘΗΚΗ` stamps and `Digitized by Google` footers are dropped;
- lines whose box runs across the gutter of a two-column page (two half-lines from different columns joined) are dropped;
- `ς` inside a word where the same word with `στ` is attested (the στ ligature read as final sigma) is relabelled to `στ`;
- duplicate copies of the same page/text under two keys keep one copy only.

## Your answer

Write `decision.json` in this folder:

```json
{"decision": "KEEP | DROP_BOOK | DROP_PATTERN | RELABEL", "confidence": 0.0, "rule_or_pattern": "", "evidence": [], "notes": ""}
```

- **KEEP** — labels match the crops; the flags reflect genre/layout (dictionary, verse, bilingual edition, tables), not wrong labels.
- **DROP_BOOK** — the labels are unreliable throughout (wrong script or language, garbled, columns merged everywhere, not text) or the book duplicates another.
- **DROP_PATTERN** — most lines are fine but a describable subset is not; give the subset as a regex on the label or a precise rule (e.g. "lines whose label starts with `ΠΑΝΕΠΙΣΤΗΜ`", "lines wider than 0.8 of the text width on two-column pages", "Latin-script lines").
- **RELABEL** — the readings are systematically wrong in a fixable way; say exactly what to replace with what (e.g. "`ς` before a letter → `στ`", "Latin `A` before a Greek letter → Greek `Α`").
- `confidence`: 0–1, how sure you are. `evidence`: the sheet line numbers that support the decision (e.g. [3, 17, 22]). `notes`: 2–4 sentences on what you saw (what is wrong, how widespread, anything the flags missed).
- Judge the labels against the pixels, not against modern spelling: 19th-century orthography, katharevousa, polytonic accents, foreign quotations and abbreviations are correct when the print has them.
