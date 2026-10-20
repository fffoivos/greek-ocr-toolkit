# Adjudication request — dossier 118: anemi_round2 / 39fbbdfd2c8030f211a318b7

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Βρύλλειον-Τρίγλεια : Ιστορική και γεωγραφική μελέτη από του Ε' αιώνος π.Χ. μέχρι των καθ' ημάς / Τρύφωνος Ε. Ευαγγελίδου.
- Source / key: `anemi_round2` / `39fbbdfd2c8030f211a318b7` (wave `round2`), year 1934
- Admitted lines: 395 on 12 pages; split {'train': 395}
- Script classes of its lines: {'greek_poly': 371, 'latin': 16, 'greek_latin_cs': 6, 'greek_mono': 2} (majority `greek_poly`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 3.0 (rank 118 of 557): 2 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 1; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 0) — 1 of 395 lines carry other-script residue (by primary kind {'unexpected_ref_letter': 1}; 0 not explained by a number-adjacent reference letter or a letter+digit token) (0.25%; same-class book p95 0.37%) — discount: all residue lines explained (letter+digit / number-adjacent reference letter), A §7
- **A:greek_book_other_lang_gt2pct** (weight 1) — 2.28% of lines guessed as another language than el {'de': 5, 'fr': 4} > 2% (same-class book p95 6.87%)

Aspect A features beyond 2σ vs same-class books (1): katharevousa_score_median z=+3.6 (value 0.0769)
Aspect B features beyond 2σ vs same-class books (2): share bibliographic z=+5.8 (value 0.0456); share long_token z=+3.2 (value 0.0304)

Context: majority language `el`, other-language share 0.0228; other-script residue lines 1 (unexplained 0); B line-flag counts {'digit_heavy': 11, 'long_token': 12, 'word_length_outlier': 7, 'bibliographic': 18, 'final_sigma_error': 2, 'spacing_apostrophe': 53}; C line-flag counts {'conf_min_low': 3, 'aspect_out': 1, 'oov_pool_high': 3}; median confidence 0.951; two-column book False, column-crossing share None.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `39fbbdfd2c8030f211a318b7-p000149`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `39fbbdfd2c8030f211a318b7-p000015-l0010` | greek_poly | 0.9425 | B:spacing_apostrophe | φόρου ὑποτελὲς τοῖς ᾿Αθηναίοις, ἵνα, τῶν Περσῶν ἐν τῷ μέλλοντι |
| 2 | random | `39fbbdfd2c8030f211a318b7-p000015-l0014` | greek_poly | 0.9612 | – | εἶτα τοῖς Ρωμαίοις, μετὰ τούτους τοῖς Βυζαντινοῖς, οἵτινες διετήρη- |
| 3 | random | `39fbbdfd2c8030f211a318b7-p000053-l0019` | greek_poly | 0.9647 | B:long_token | Κωνσταντινουπόλεως Νικόλαος Α΄ ὁ Μυστικός (901-907) ἀφώρισε |
| 4 | random | `39fbbdfd2c8030f211a318b7-p000063-l0016` | greek_poly | 0.9594 | – | καὶ πάντας ὑπερασπιζόμενος, ἐπεξηγούμενος τὰ τοιαῦτα, ἀδικίαν ἐργα- |
| 5 | random | `39fbbdfd2c8030f211a318b7-p000077-l0004` | greek_poly | 0.941 | – | κανόνας τῆς ἁγίας τοῦ Χριστοῦ᾽ Εκκλησίας· καὶ ὅταν τύχωσιἀναμεταξύ |
| 6 | random | `39fbbdfd2c8030f211a318b7-p000077-l0014` | greek_poly | 0.9731 | – | τριαρχικὴν καὶ συνοδικὴν ἡμῶν ταύτην παραγγελίαν καὶ νουθεσίαν, |
| 7 | random | `39fbbdfd2c8030f211a318b7-p000077-l0018` | greek_poly | 0.9722 | – | φύσει μόνου Θεοῦ καὶ κατηραμένος, καὶ ἀσυγχώρητος, καὶ ἄλυτος |
| 8 | random | `39fbbdfd2c8030f211a318b7-p000090-l0007` | greek_poly | 0.9515 | – | ὑπὸ τῶν Τούρκων ἔτυχεν ἰδιαιτέρας προστασίας παρὰ τοῦ φίλου αὐ- |
| 9 | random | `39fbbdfd2c8030f211a318b7-p000090-l0010` | greek_poly | 0.9592 | B:spacing_apostrophe | κοῦ Πανεπισνημίου. Τῷ 1919 διέτριβεν ἐν ᾿Αθήναις καὶ τῷ 1922 ἐ- |
| 10 | random | `39fbbdfd2c8030f211a318b7-p000090-l0019` | greek_poly | 0.9311 | – | 1900 διδάκταῳ ἀναγορευθεὶς ἀπῆλθεν εἰς Χαρτούμ τοῦ Αἰγυπτιακοῦ |
| 11 | random | `39fbbdfd2c8030f211a318b7-p000090-l0030` | greek_poly | 0.9517 | B:spacing_apostrophe | γλείας Δὶς ᾿Αναστασία Φούντα καὶ ἡ Δὶς Ἡρακλέους Τσίτερ. |
| 12 | random | `39fbbdfd2c8030f211a318b7-p000102-l0018` | greek_poly | 0.9312 | – | 20 Ιουλίου ἐν τῷ ναῷ τοῦ ῾Αγίου Ιωάννου τοῦ Θεολόγου, ἐν ᾧ παῖς |
| 13 | random | `39fbbdfd2c8030f211a318b7-p000102-l0025` | greek_poly | 0.9612 | – | Φοιτήσας καὶ κατὰ τὸ 1862 συνεστήθη ὑπὸ τοῦ Προύσης πρὸς |
| 14 | random | `39fbbdfd2c8030f211a318b7-p000114-l0021` | greek_poly | 0.9743 | – | διά τε κολύβων καὶ ἄρτων πισινίων καλουμένων. |
| 15 | random | `39fbbdfd2c8030f211a318b7-p000114-l0039` | greek_poly | 0.9547 | – | Γεωργίου Σιγουριτᾶ καὶ Γιαννακοῦ Τσίπουρα καὶ ἐγένοντο ὀχλαγω |
| 16 | random | `39fbbdfd2c8030f211a318b7-p000124-l0016` | latin | 0.9835 | – | Fragm 2, G. Dittemberger Sylloge Inscriptionum Graeco |
| 17 | random | `39fbbdfd2c8030f211a318b7-p000124-l0021` | latin | 0.9755 | A:lang_ne_book, B:bibliographic | ἀριθμ. 236 σ. 11 καὶ ἐν Bulletin de Correspondanee Hellènique |
| 18 | random | `39fbbdfd2c8030f211a318b7-p000124-l0033` | greek_latin_cs | 0.9119 | B:spacing_apostrophe | 19) ᾿Ανεδημοσιεύθη ἐν BCH· ἔνθ᾽ ἀνωτέρω. |
| 19 | random | `39fbbdfd2c8030f211a318b7-p000149-l0019` | greek_poly | 0.9466 | – | ποκρίτου εὐλαβείας ἠκροῶντο τῶν ἱερῶν ἀκολουθιῶν. |
| 20 | random | `39fbbdfd2c8030f211a318b7-p000149-l0031` | greek_poly | 0.9572 | – | τὰ ἄνθη χρυσάνθεμα, Περὶ δὲ τῶν γλυκυσμάτων ἰδὲ Μ. Ι. Γεδεὼν ἐν |
| 21 | anomalous | `39fbbdfd2c8030f211a318b7-p000102-l0035` | greek_poly | 0.9563 | B:long_token, B:spacing_apostrophe, B:word_length_outlier, C:oov_pool_high | ριοδικὸν «Τσιτάλιστε» (᾿Αναγνωστήριον), βουλγαριστὶ ὄργανον τῶν |
| 22 | anomalous | `39fbbdfd2c8030f211a318b7-p000149-l0027` | greek_latin_cs | 0.9513 | B:bibliographic, B:digit_heavy, B:spacing_apostrophe | Society τοῦ ᾿Ιουλίου 1891 σ. 46-49 καὶ διάλογος ποιητικὸς ᾿Αθιγ- |
| 23 | anomalous | `39fbbdfd2c8030f211a318b7-p000149-l0032` | greek_poly | 0.9243 | B:bibliographic, B:spacing_apostrophe, C:oov_pool_high | Προικοννήσω, Κων/πολις 1906 σ.2 καὶ 8 ἐν «᾿Εκκλησιαστικῇ ᾿Αλη- |
| 24 | anomalous | `39fbbdfd2c8030f211a318b7-p000015-l0019` | greek_poly | 0.9526 | B:spacing_apostrophe, B:word_length_outlier | τόμ. Ι΄. τεῦχος Α΄, Β΄, Γ΄. Ἐν ᾿Αθήναις 1888, σελὶς 83 καὶ τεῦχος |
| 25 | anomalous | `39fbbdfd2c8030f211a318b7-p000149-l0008` | greek_poly | 0.946 | B:spacing_apostrophe, C:conf_min_low | Βιθυνίας καὶ συμφοιτητοῦ μου, ᾿Αθ. 1905 τόμ. Α΄ Πρβλ. καὶ «Ξε- |
| 26 | anomalous | `39fbbdfd2c8030f211a318b7-p000102-l0020` | greek_poly | 0.9346 | B:bibliographic, B:spacing_apostrophe | «Εὐαγγελικῷ Κήρυκι» ᾿Αθηνῶν (1861 τόμ. Ε΄ σ. 442 ἑξ.) μετὰ |
| 27 | anomalous | `39fbbdfd2c8030f211a318b7-p000053-l0010` | greek_poly | 0.9344 | B:bibliographic, B:spacing_apostrophe | τοῖς ἐμοῖς «Βίοις τῶν ῾Αγίων», (᾿Αθ. 1895 σ. 240) ἔγραψα, ὅτι ὁ |
| 28 | anomalous | `39fbbdfd2c8030f211a318b7-p000138-l0013` | greek_poly | 0.9356 | B:bibliographic, B:spacing_apostrophe | πρβλ. καὶ Βασιλείου Ι. Κάνδη, ἡ Προῦσα, ᾿Αθ. 1884 σ. 127. |
| 29 | anomalous | `39fbbdfd2c8030f211a318b7-p000149-l0030` | greek_poly | 0.9515 | B:long_token, B:spacing_apostrophe | 164) ᾿Αγιοδημητριάτικα ἐκ τοῦ μηνὸς ῾Αηδημητριάτη καλοῦνται |
| 30 | anomalous | `39fbbdfd2c8030f211a318b7-p000149-l0024` | latin | 0.9307 | A:lang_ne_book, B:spacing_apostrophe | Ἰδὲ But etin de la societé d' anthropologie τῆς 3 ᾿Απριλίου |
| 31 | anomalous | `39fbbdfd2c8030f211a318b7-p000090-l0026` | greek_poly | 0.9594 | B:spacing_apostrophe, C:oov_pool_high | λόγος, ὁ ᾿Αναστάσιος Κελέκης ἀκτινολόγος, ὁ Στ. Κελέκης ἀκτινο- |
| 32 | anomalous | `39fbbdfd2c8030f211a318b7-p000124-l0023` | latin | 0.9716 | B:bibliographic, B:digit_heavy | chäologischen Instituts, Athen 1892, τόμ. ΧV σ. 342. |
| 33 | anomalous | `39fbbdfd2c8030f211a318b7-p000114-l0012` | greek_poly | 0.9019 | A:mark_density_high, B:word_length_outlier | Μετὰ τὴν ταφὴν τοῦ νεκροῦ ἐν τῇ «Ρυακιᾷ» ἢ ἐν τῷ᾽ «Σκυ- |
| 34 | anomalous | `39fbbdfd2c8030f211a318b7-p000149-l0012` | greek_latin_cs | 0.9747 | B:bibliographic, B:digit_heavy | Lipziae 1909 τόμ. Β΄ σ. 40 καὶ 41 καὶ ὁ μητροπολίτης πρώην Λεον- |
| 35 | anomalous | `39fbbdfd2c8030f211a318b7-p000138-l0010` | latin | 0.9678 | B:bibliographic, B:digit_heavy | Grecques, Paris 1874 σ. 195-197 Πρβλ. Karl Krumbacher, |
| 36 | anomalous | `39fbbdfd2c8030f211a318b7-p000124-l0022` | latin | 0.9757 | B:bibliographic, B:digit_heavy | 1890, τόμ. XVII σ. 544 καὶ ἐν Milheilungen des Deutschen Ar- |
| 37 | anomalous | `39fbbdfd2c8030f211a318b7-p000138-l0012` | greek_poly | 0.9508 | B:bibliographic, B:digit_heavy | σ 433-444 καὶ 681 καὶ Μεσαιωνική Βιβλιοθήκη τόμ. Ε΄ σ. 263 |
| 38 | anomalous | `39fbbdfd2c8030f211a318b7-p000124-l0025` | greek_poly | 0.9535 | B:bibliographic, B:digit_heavy | 16) Αὐτόθι σ. 544-Αὐτόθι 342· ἀλλὰ Νικία-θρεψέσης |
| 39 | anomalous | `39fbbdfd2c8030f211a318b7-p000124-l0024` | greek_latin_cs | 0.962 | B:bibliographic, B:digit_heavy | 15) Αὐτόθι σ. 544-Mitteil αὐτόθι. |
| 40 | anomalous | `39fbbdfd2c8030f211a318b7-p000102-l0026` | greek_poly | 0.9836 | A:mark_density_low, B:long_token | τὸν ἐν Κωνσταντινουπόλει διατρίβοντα τότε πλούσιον Φιλιππουπολί- |

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
