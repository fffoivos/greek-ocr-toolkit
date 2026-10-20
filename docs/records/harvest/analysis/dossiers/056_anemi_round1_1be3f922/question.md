# Adjudication request — dossier 056: anemi_round1 / 1be3f9227e2b68a2b9974abe

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Το αναπαλλοτρίωτον της εκκλησιαστικής περιουσίας κατά το δίκαιον της Ορθοδόξου Ανατολικής Εκκλησίας / Υπό Κωνσταντίνου Μ. Ράλλη.
- Source / key: `anemi_round1` / `1be3f9227e2b68a2b9974abe` (wave `round1`), year 1903
- Admitted lines: 306 on 8 pages; split {'train': 306}
- Script classes of its lines: {'greek_poly': 228, 'latin': 43, 'greek_latin_cs': 33, 'greek_mono': 2} (majority `greek_poly`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 4.0 (rank 56 of 557): 2 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as top-60 by suspicion.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 3 of 306 lines carry other-script residue (by primary kind {'isolated_ref_letter': 2, 'unexpected_standalone_lookalike': 1}; 1 not explained by a number-adjacent reference letter or a letter+digit token) (0.98%; same-class book p95 0.37%)
- **A:greek_book_other_lang_gt2pct** (weight 1) — 6.21% of lines guessed as another language than el {'de': 1, 'la': 18} > 2% (same-class book p95 6.87%)

Aspect A features beyond 2σ vs same-class books (3): residue_line_share z=+2.7 (value 0.0098); latin_share_mean z=+2.5 (value 0.1541); greek_share_mean z=-2.5 (value 0.8459)
Aspect B features beyond 2σ vs same-class books (1): share bibliographic z=+5.9 (value 0.0458)

Context: majority language `el`, other-language share 0.0621; other-script residue lines 3 (unexplained 1); B line-flag counts {'digit_heavy': 9, 'punct_heavy': 2, 'long_token': 2, 'word_length_outlier': 14, 'repeated_run': 2, 'numeric_table': 1, 'bibliographic': 14, 'spacing_apostrophe': 20}; C line-flag counts {'cpp_out_of_range': 7, 'height_ratio_low': 1, 'cpp_vs_book_out': 33, 'conf_min_low': 4, 'cph_out_of_range': 41}; median confidence 0.955; two-column book False, column-crossing share None.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `1be3f9227e2b68a2b9974abe-p000023`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `1be3f9227e2b68a2b9974abe-p000011-l0026` | greek_poly | 0.9639 | – | μονὴ τοῦ ἁγίου Νικολάου καὶ τοῦ τιμίου Προδρόμου ἀνεγνωρίσθη |
| 2 | random | `1be3f9227e2b68a2b9974abe-p000023-l0043` | greek_poly | 0.9438 | C:cph_out_of_range | . Καὶ τὸ κανονικὸν δίκαιον τῆς |
| 3 | random | `1be3f9227e2b68a2b9974abe-p000023-l0055` | latin | 0.9905 | C:cph_out_of_range, C:cpp_vs_book_out | quia rerum ecclesiasticarum alie- |
| 4 | random | `1be3f9227e2b68a2b9974abe-p000037-l0020` | greek_latin_cs | 0.961 | – | τίμων ἐσθήτων εἶχεν ἐπιτρέψῃ ἤδη τῷ 483 ὁ praefectus praeto - |
| 5 | random | `1be3f9227e2b68a2b9974abe-p000037-l0022` | greek_poly | 0.9602 | – | καιολόγησε τὴν πρὸς ἀπαλλοτρίωσιν αἰχμαλώτων ἐκποίησιν ἱερῶν |
| 6 | random | `1be3f9227e2b68a2b9974abe-p000037-l0023` | greek_latin_cs | 0.9542 | – | σκευῶν, διὰ τῶν ἑξῆς ῥημάτων : «aurum ecclesia habet non |
| 7 | random | `1be3f9227e2b68a2b9974abe-p000037-l0033` | latin | 0.9636 | A:lang_ne_book | *dendum esse potius quam templis inanimatis». |
| 8 | random | `1be3f9227e2b68a2b9974abe-p000037-l0036` | latin | 0.9814 | A:lang_ne_book | redemptio et vita egentun quae et animas salvant et |
| 9 | random | `1be3f9227e2b68a2b9974abe-p000054-l0013` | greek_poly | 0.9712 | B:long_token | λήλους ἀρχὰς γενόμεναι διαπραγματεύσεις». Ὁ Οἰκονόμου ἐν τοῖς |
| 10 | random | `1be3f9227e2b68a2b9974abe-p000054-l0015` | greek_poly | 0.943 | – | ἐπικαλούμενος τὴν τοῦ Βαλσαμῶνος ἑρμηνείαν εἰς τὸν ιζ' κανόνα τῆς |
| 11 | random | `1be3f9227e2b68a2b9974abe-p000054-l0041` | greek_poly | 0.9683 | – | κῶν Γραμματείαν : «Μεταξὺ τοῦ τόσου πλήθους τῶν μοναστηρίων |
| 12 | random | `1be3f9227e2b68a2b9974abe-p000066-l0031` | greek_poly | 0.9673 | B:digit_heavy | 593, καὶ τὸ ἀπὸ 20 Ὀκτωβρίου 1401 γράμμα τοῦ πατριάρχου |
| 13 | random | `1be3f9227e2b68a2b9974abe-p000078-l0007` | greek_poly | 0.9685 | – | γῶν οἴκων δύνανται μισθοῦσθαι καὶ ἐμφυτεύεσθαι, πάντων τῶν μονα- |
| 14 | random | `1be3f9227e2b68a2b9974abe-p000078-l0009` | greek_poly | 0.9631 | – | φανερούντων συμφέρειν τὸ γινόμενον». Καὶ ἐν τῇ δύσει κατὰ τὴν |
| 15 | random | `1be3f9227e2b68a2b9974abe-p000078-l0015` | greek_poly | 0.9529 | – | βιγγικῶν χρόνων λέγεται πάντοτε ὅτι ἡ πρεκαριακὴ παραχώρησις |
| 16 | random | `1be3f9227e2b68a2b9974abe-p000078-l0022` | greek_poly | 0.9485 | – | κοκρατίας ἡ τῶν μονῶν ἀκίνητος περιουσία δὲν ἐξεποιεῖτο ὑπὸ τῶν |
| 17 | random | `1be3f9227e2b68a2b9974abe-p000106-l0011` | greek_poly | 0.9515 | – | σκόπου, ἀφορίζονται. Κατὰ τὸν καν. 36 τῆς συν. Οξωνίας ἔτ. 1222 |
| 18 | random | `1be3f9227e2b68a2b9974abe-p000106-l0015` | greek_poly | 0.96 | – | ἐκποιηθέν, ἐκπίπτουσι τοῦ ἑαυτῶν ἀξιώματος. Κατὰ τὸν καν. 7 τῆς |
| 19 | random | `1be3f9227e2b68a2b9974abe-p000106-l0029` | greek_poly | 0.9456 | – | τῶν ἐκκλησιῶν καὶ τοῖς διαδόχοις αὐτῶν, τοῖς παραλιποῦσι τὴν ἀνά- |
| 20 | random | `1be3f9227e2b68a2b9974abe-p000106-l0042` | greek_latin_cs | 0.9733 | – | ματα κληρικοῖς excommunicatio ipso facto. Οὕτω καὶ ὁ καν. |
| 21 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0053` | latin | 0.9661 | A:other_script_residue:isolated_ref_letter, B:bibliographic, B:digit_heavy, C:cph_out_of_range, C:cpp_vs_book_out | Schmalzgrueber σ. 207 |
| 22 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0035` | greek_poly | 0.9136 | B:spacing_apostrophe, C:cph_out_of_range, C:cpp_vs_book_out | οἱ τῆς μονῆς ᾿Ασωμάτων |
| 23 | anomalous | `1be3f9227e2b68a2b9974abe-p000078-l0027` | greek_poly | 0.9546 | B:spacing_apostrophe, C:cph_out_of_range, C:cpp_vs_book_out | 1891 ἀπόφασιν τοῦ ᾿Αρείου Πάγου. Βραδύτερον ὅμως ἐκράτησεν ἐν ᾿Αθήναις ἔθιμον, διὰ |
| 24 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0038` | greek_poly | 0.9096 | B:spacing_apostrophe, C:cph_out_of_range, C:cpp_vs_book_out | κατ᾿ ἔθιμον ἐν ᾿Αθήναις ἐπὶ |
| 25 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0031` | greek_mono | 0.9568 | B:spacing_apostrophe, C:cph_out_of_range, C:cpp_vs_book_out | Πατριάρχης ᾿Αλέξιος (1025- |
| 26 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0056` | latin | 0.9907 | A:lang_ne_book, C:cph_out_of_range, C:cpp_vs_book_out | natio in tantum est prohibita, |
| 27 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0015` | greek_poly | 0.9638 | A:mark_density_high, C:cph_out_of_range, C:cpp_vs_book_out | ἢ ἀποσπασθῆναι, |
| 28 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0061` | latin | 0.9888 | A:lang_ne_book, C:cph_out_of_range, C:cpp_vs_book_out | , sed alterius cuiuslibet |
| 29 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0022` | latin | 0.9534 | B:digit_heavy, C:cph_out_of_range, C:cpp_vs_book_out | Voelli et Justelli bibl. II 1245 |
| 30 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0058` | latin | 0.9867 | A:lang_ne_book, C:cph_out_of_range, C:cpp_vs_book_out | et utilitas ecclesiae. Sed |
| 31 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0060` | latin | 0.9894 | A:lang_ne_book, C:cph_out_of_range, C:cpp_vs_book_out | ut non solum translatio dominii |
| 32 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0024` | greek_poly | 0.9492 | B:bibliographic, B:punct_heavy, B:word_length_outlier | συν. Νικ. ἐν Συντ. Β΄, σ. 595, καὶ εἰς καν. λγ' τῆς |
| 33 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0063` | latin | 0.9692 | A:lang_ne_book, C:cph_out_of_range, C:cpp_vs_book_out | prohibeatur; nam etiam |
| 34 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0057` | latin | 0.9654 | A:lang_ne_book, C:cph_out_of_range, C:cpp_vs_book_out | in quantum id exigit favor |
| 35 | anomalous | `1be3f9227e2b68a2b9974abe-p000078-l0006` | greek_poly | 0.9378 | B:bibliographic, B:punct_heavy, B:word_length_outlier | 120 Ματθ. Βλαστ. ἐν Συντ. Γ΄, σ. 250 : «αἱ κτήσεις τῶν εὐα- |
| 36 | anomalous | `1be3f9227e2b68a2b9974abe-p000011-l0007` | greek_poly | 0.9161 | B:repeated_run, B:spacing_apostrophe | 1 Καν. λη΄ ᾿Αποστόλων «.... μὴ ἐξεῖναι δὲ αὐτῷ (ἐπισκόπῳ) |
| 37 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0010` | greek_poly | 0.9283 | A:mark_density_low, B:spacing_apostrophe | 26 Πρβλ. καν. κ5 καὶ λγ Καρθαγένης, καν. β΄ Κυρίλλου ᾿Αλε- |
| 38 | anomalous | `1be3f9227e2b68a2b9974abe-p000106-l0031` | greek_latin_cs | 0.9188 | B:bibliographic, B:spacing_apostrophe | ποινή. Πρβλ. σ. 1 τῆς συν. ᾿Αβινιῶνος ἔτ. 1270 (παρὰ Mansi, |
| 39 | anomalous | `1be3f9227e2b68a2b9974abe-p000037-l0008` | latin | 0.9443 | A:lang_ne_book, B:repeated_run | sior est....». «Quae etiam (res sacrae) per nostram |
| 40 | anomalous | `1be3f9227e2b68a2b9974abe-p000023-l0062` | latin | 0.99 | C:cph_out_of_range, C:cpp_vs_book_out | iuris, ecclesiae multum proficui |

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
