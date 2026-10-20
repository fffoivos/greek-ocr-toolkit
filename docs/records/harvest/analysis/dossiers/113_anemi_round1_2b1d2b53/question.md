# Adjudication request — dossier 113: anemi_round1 / 2b1d2b5340150ddc135a2b1a

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Μάρκου Τύλλιου Κικέρωνος Ο υπέρ Τίτου Αννίου Μίλωνος λόγος / Ερμηνευθείς και μεταφρασθείς εις την νεωτέραν ελληνικήν γλώσσαν υπό Θεοφάνους Α. Κακριδή.
- Source / key: `anemi_round1` / `2b1d2b5340150ddc135a2b1a` (wave `round1`), year 1928
- Admitted lines: 481 on 12 pages; split {'train': 481}
- Script classes of its lines: {'greek_poly': 288, 'latin': 110, 'greek_latin_cs': 83} (majority `greek_poly`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 3.0 (rank 113 of 557): 2 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 1; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:greek_book_other_lang_gt2pct** (weight 1) — 15.38% of lines guessed as another language than el {'la': 70, 'fr': 2, 'it': 1, 'de': 1} > 2% (same-class book p95 6.87%)

Aspect A features beyond 2σ vs same-class books (3): greek_share_mean z=-4.4 (value 0.7442); latin_share_mean z=+4.4 (value 0.2558); other_language_share z=+3.4 (value 0.1538)
Aspect B features beyond 2σ vs same-class books (1): share numeric_table z=+2.2 (value 0.0104)

Context: majority language `el`, other-language share 0.1538; other-script residue lines 0 (unexplained 0); B line-flag counts {'punct_heavy': 3, 'long_token': 1, 'word_length_outlier': 2, 'repeated_run': 3, 'numeric_table': 5, 'spacing_apostrophe': 14}; C line-flag counts {'cpp_out_of_range': 17, 'conf_min_low': 1, 'cph_out_of_range': 2, 'repeated_word': 3}; median confidence 0.949; two-column book False, column-crossing share None.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `2b1d2b5340150ddc135a2b1a-p000085`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `2b1d2b5340150ddc135a2b1a-p000017-l0009` | greek_poly | 0.9491 | – | τοὺς αὐτοὺς τούτους ὄντας ἐκ τῶν ὀλίγων πιστοτάτων ὀπαδῶν του |
| 2 | random | `2b1d2b5340150ddc135a2b1a-p000017-l0013` | greek_poly | 0.9452 | – | λαοῦ τὴν εὔνοιαν διὰ μεγαλοπρεπῶν ἀγώνων εἶχε κερδίσει καὶ τῶν |
| 3 | random | `2b1d2b5340150ddc135a2b1a-p000017-l0028` | greek_poly | 0.9492 | – | ἀρχήν, 31 Δεκεμ., νέοι δὲ ἀκόμη δὲν εἶχον ἐκλεχθῆ καὶ διὰ τοῦτο ἔπρεπεν, |
| 4 | random | `2b1d2b5340150ddc135a2b1a-p000017-l0031` | greek_poly | 0.9698 | – | λέως ἠμπόδισεν ὁ φίλος τοῦ Κλωδίου δήμαρχος Τίτος Μουνάτιος· |
| 5 | random | `2b1d2b5340150ddc135a2b1a-p000032-l0030` | latin | 0.9904 | A:lang_ne_book | sim vobis defensionem meam, si id memineritis, quod obli |
| 6 | random | `2b1d2b5340150ddc135a2b1a-p000059-l0033` | latin | 0.9775 | A:lang_ne_book | atque ipsa mænia stare eo vivo tamdiu et consulatum eius |
| 7 | random | `2b1d2b5340150ddc135a2b1a-p000070-l0032` | greek_latin_cs | 0.9464 | – | nomen, ἢ πρότερον τὸ cognomen καὶ ὕστερον τὸ nomen, ὡς ἐνταῦθα· τὸ |
| 8 | random | `2b1d2b5340150ddc135a2b1a-p000099-l0011` | greek_poly | 0.9431 | – | Χ., ὅστις ἀπὸ τῆς πρώτης ἡμέρας τῆς ὑπατείας του (1η Ιανουαρίου) ὡμίλησεν |
| 9 | random | `2b1d2b5340150ddc135a2b1a-p000099-l0018` | greek_poly | 0.9513 | – | Σπινθῆρος ἐσηγησαμένου προεβούλευσε κοὶ ὁ δῆμος ἀμφοτέρων τῶν ὑπάτων ἐσενεγ· |
| 10 | random | `2b1d2b5340150ddc135a2b1a-p000112-l0027` | greek_latin_cs | 0.9549 | B:spacing_apostrophe | in castra Etrusca: ὁ ᾿Ασκώνιος νομίζει ὅτι ἐνταῦθα ὁ Κικέρων ὑπαινίσ |
| 11 | random | `2b1d2b5340150ddc135a2b1a-p000112-l0036` | greek_latin_cs | 0.9606 | – | λέγει δὲ καὶ ὁ Κικέρων ἐνταῦθα in castra Etrusca properabat, ἐξ οὗ ἐμφαί- |
| 12 | random | `2b1d2b5340150ddc135a2b1a-p000124-l0004` | latin | 0.9618 | – | 52 τὸν Q. Metellum Scipionem καὶ τὸν P. Plautium Hypsaeum (εἰσαγωγ. |
| 13 | random | `2b1d2b5340150ddc135a2b1a-p000124-l0035` | greek_poly | 0.9635 | – | συνέβη εἰς τὸν Κικέρωνα. Κινδυνεύει δὲ καὶ τρίτον κίνδυνον νὰ τιμωρηθῇ ὑπὸ |
| 14 | random | `2b1d2b5340150ddc135a2b1a-p000124-l0043` | latin | 0.9814 | A:lang_ne_book | auderet) si periculum non timeret?, ἀλλὰ si illo in certamnie potiri posset? |
| 15 | random | `2b1d2b5340150ddc135a2b1a-p000140-l0012` | greek_poly | 0.964 | – | καὶ ἐμπρησμοὺς καὶ παντὸς εἴδους κακουργίας κατὰ τοῦ δημοσίου, |
| 16 | random | `2b1d2b5340150ddc135a2b1a-p000140-l0023` | greek_poly | 0.9542 | – | • στάτων τάξεων ἄνδρας, τὴν εὔνοιαν ποῦ εἶχον πρὸς ἀνδρείους καὶ |
| 17 | random | `2b1d2b5340150ddc135a2b1a-p000140-l0026` | greek_poly | 0.9586 | – | θαρὰ μὲ ἔργα καὶ μὲ τὰς ψήφους τους, τώρα δὰ πρὸ πάντων αὐτὴν |
| 18 | random | `2b1d2b5340150ddc135a2b1a-p000153-l0021` | greek_poly | 0.9309 | – | διὰ τὸ ὁποῖον ὁ Μίλων δὲν λέγω θὰ ἐπέτρεπε (εἰς ἑαυτὸν ἢ τοὺς ἀν- |
| 19 | random | `2b1d2b5340150ddc135a2b1a-p000178-l0007` | greek_poly | 0.9645 | – | νικὸν θρῆνον ὅλων ἡμῶν δὲν παρετηρήσατε κανένα δάκρυ τοῦ |
| 20 | random | `2b1d2b5340150ddc135a2b1a-p000178-l0039` | greek_poly | 0.9285 | – | νομίσω ὅτι ἔμελλε ποτέ να μου λείψῃ ἡ ὑποστήριξις τῶν χρηστῶν |
| 21 | anomalous | `2b1d2b5340150ddc135a2b1a-p000085-l0005` | greek_poly | 0.9494 | B:numeric_table, B:spacing_apostrophe | Κικέρων ἔν τινι ἐπιστολῇ, πρὸς ᾿Αττικὸν (4, 3, 5) γράφει (πρὸ τοῦ θανάτου |
| 22 | anomalous | `2b1d2b5340150ddc135a2b1a-p000070-l0043` | greek_poly | 0.9556 | B:punct_heavy, B:word_length_outlier | (Πλούτ. β. Γαΐου Γράκχου κεφ. 14 κ. ἑ...) |
| 23 | anomalous | `2b1d2b5340150ddc135a2b1a-p000032-l0036` | latin | 0.9756 | A:lang_ne_book, C:cph_out_of_range | natus non sententiis suis solum, sed etiam studiis com. |
| 24 | anomalous | `2b1d2b5340150ddc135a2b1a-p000032-l0007` | latin | 0.9901 | A:lang_ne_book, C:cph_out_of_range | etiam necessarium, cum vi vis illata defenditur. Pudicitiam |
| 25 | anomalous | `2b1d2b5340150ddc135a2b1a-p000085-l0034` | greek_latin_cs | 0.9482 | B:spacing_apostrophe | ἱερέα (᾿Ασκών. argum. § 3), τὸ δὲ legitimum δηλοῖ ὅτι ἦτο ὑπὸ τῶν νόμων |
| 26 | anomalous | `2b1d2b5340150ddc135a2b1a-p000124-l0021` | latin | 0.9655 | B:repeated_run | § 82. proposita invidia, [morte] poena...., καίπερ προκειμένου (αὐτῷ) μί- |
| 27 | anomalous | `2b1d2b5340150ddc135a2b1a-p000070-l0027` | greek_poly | 0.9367 | B:spacing_apostrophe | πέντε. ᾿Αλλὰ δὲν ἦτο ἀνάγκη ἑκάστοτε νὰ λέγωνται ὅλα τὰ ὀνόματα· ἤρκει |
| 28 | anomalous | `2b1d2b5340150ddc135a2b1a-p000124-l0010` | greek_poly | 0.947 | B:spacing_apostrophe | πολιτικοῦ συμφέροντος. ᾿Αλλ' εἶναι φανερὸν ὅτι ἔχει δύναμιν μεγαλυτέραν καὶ |
| 29 | anomalous | `2b1d2b5340150ddc135a2b1a-p000124-l0023` | greek_latin_cs | 0.9382 | B:repeated_run | θανατωθῇ] νὰ τιμωρηθῇ..... Ἡ λέξις morte φαίνεται ἡμῖν νόθος· οὔτε ἡ θέσις |
| 30 | anomalous | `2b1d2b5340150ddc135a2b1a-p000165-l0026` | greek_poly | 0.9461 | C:repeated_word | του». Τοὺς δυστυχεῖς κάποτε πολίτας ποῦ προσέφεραν πολὺ πολὺ |
| 31 | anomalous | `2b1d2b5340150ddc135a2b1a-p000112-l0033` | greek_latin_cs | 0.9598 | B:spacing_apostrophe | tato consilio in urbem redisse». ᾿Αλλ' ἐπειδὴ ὁ Πλούταρχος, βίῳ Κικέρωνος, |
| 32 | anomalous | `2b1d2b5340150ddc135a2b1a-p000085-l0041` | greek_latin_cs | 0.9541 | B:spacing_apostrophe | stera die. Ἰδὲ καὶ Δίωνα Κάσσιον 40,48. (Εσφαλμένως ὁ ᾿Αππιανός, Εμφυλ. |
| 33 | anomalous | `2b1d2b5340150ddc135a2b1a-p000124-l0036` | greek_latin_cs | 0.9544 | B:spacing_apostrophe | τοῦ δικαστηρίου (poena), ὡς τώρα ὁ Μίλων. ᾿Αλλὰ δὲν πρόκειται κἂν ἐνταῦθα |
| 34 | anomalous | `2b1d2b5340150ddc135a2b1a-p000153-l0037` | greek_poly | 0.9432 | B:spacing_apostrophe | ποῦ θὰ ἐτόλμα καὶ θὰ μποροῦσε νά την περιστείλῃ. ᾿Αφοῦ δὲ |
| 35 | anomalous | `2b1d2b5340150ddc135a2b1a-p000112-l0024` | greek_latin_cs | 0.9553 | B:spacing_apostrophe | τασιν πολλοὶ ἐθεώρουν perridiculam οὕτω παρὰ Κικέρωνι de orat 2,77 ὁ ᾿Αντώ- |
| 36 | anomalous | `2b1d2b5340150ddc135a2b1a-p000124-l0022` | greek_poly | 0.9417 | B:repeated_run | σους [θανάτου] τιμωρίας...., τ. ἔ. καίπερ κινδυνεύει προφανῶς νὰ μισηθῇ ἱνὰ |
| 37 | anomalous | `2b1d2b5340150ddc135a2b1a-p000085-l0003` | greek_latin_cs | 0.9608 | B:spacing_apostrophe | occidendum (esse) Milonem: οὐ μόνον ὁ ᾿Ασκώνιος (§ 30) ἀναφέρει ὡς |
| 38 | anomalous | `2b1d2b5340150ddc135a2b1a-p000153-l0035` | greek_poly | 0.941 | B:spacing_apostrophe | φόβον ἀνατροπῆς τοῦ καθεστῶτος; ᾿Απεριόριστος δὲ ἐβλέπετε ὅτι |
| 39 | anomalous | `2b1d2b5340150ddc135a2b1a-p000153-l0031` | greek_poly | 0.9544 | C:repeated_word | ὁποίων ἐγὼ ἀντελαμβανόμην ὅτι σεῖς τότε πολὺ πολὺ συνεκινεῖσθε, |
| 40 | anomalous | `2b1d2b5340150ddc135a2b1a-p000085-l0015` | greek_latin_cs | 0.9404 | B:spacing_apostrophe | liam ἐν Ετρουρίᾳ οὐ μακρὰν τοῦ ᾿Αππεννίνου κειμένοις (Cic. Phil. 12, 23). |

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
