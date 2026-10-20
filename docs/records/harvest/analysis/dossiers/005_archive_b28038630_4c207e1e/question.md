# Adjudication request — dossier 005: archive_b28038630 / 4c207e1e

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: A Greek-English lexicon
- Source / key: `archive_b28038630` / `4c207e1e` (wave `mixed`), year 1883
- Admitted lines: 9788 on 70 pages; split {'train': 6884, 'test': 1965, 'dev': 939}
- Script classes of its lines: {'latin': 7003, 'greek_latin_cs': 2627, 'greek_poly': 99, 'greek_mono': 59} (majority `latin`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 6.0 (rank 5 of 557): 4 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as top-60 by suspicion.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 65 of 9788 lines carry other-script residue (by primary kind {'isolated_standalone': 14, 'unexpected_ref_letter': 26, 'unexpected_standalone_lookalike': 5, 'isolated_ref_letter': 9, 'isolated_alnum': 1, 'unexpected_word': 7, 'isolated_standalone_lookalike': 1, 'unexpected_alnum': 1, 'unexpected_standalone': 1}; 28 not explained by a number-adjacent reference letter or a letter+digit token) (0.66%; same-class book p95 1.79%)
- **B:final_sigma_above_class_p95** (weight 1) — final-sigma error rate 0.0005 (14/27021 Greek words) > latin book p95 0.0001 (N=19 books)
- **D:page_line_count_outlier** (weight 0) — 5 page(s) above and 0 below the mixed page line-count p99/p1 — discount: wave p1/p99 page rule, ~1 % of pages per side by construction (D §9)

Aspect A features beyond 2σ vs same-class books (1): cyrillic_share_mean z=+2.7 (value 0.0002)
Aspect B features beyond 2σ vs same-class books (4): share final_sigma_error z=+4.2 (value 0.0014); share numeric_table z=+4.0 (value 0.0737); median punct_share z=+2.3 (value 0.1429); median digit_share z=+2.0 (value 0.0536)
Aspect C features beyond 2σ vs same-class books (1): conf_min z=-2.6 (value 0.59)
Aspect D features beyond 2σ vs same-class books (1): lines_vs_wave_median z=+3.6 (value 4.825)

Context: majority language `en`, other-language share 0.3029; other-script residue lines 65 (unexplained 28); B line-flag counts {'digit_heavy': 523, 'punct_heavy': 113, 'long_token': 3, 'word_length_outlier': 158, 'repeated_run': 1, 'numeric_table': 721, 'bibliographic': 5, 'final_sigma_error': 14, 'spacing_apostrophe': 75, 'dictionary_like': 112}; C line-flag counts {'cpp_out_of_range': 365, 'conf_mean_low': 49, 'conf_min_low': 123, 'aspect_out': 128, 'oov_pool_high': 63, 'cph_out_of_range': 119, 'len_vs_book_high': 47, 'repeated_word': 9}; median confidence 0.965; two-column book True, column-crossing share 0.006.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `4c207e1e-p001018`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `4c207e1e-p000147-l0101` | latin | 0.9479 | – | 8. 5, Thuc. 5. 111, etc.; μίασμα.. ἀν. τρέφειν to keep it till 'tis past |
| 2 | random | `4c207e1e-p000276-l0064` | greek_latin_cs | 0.9776 | – | δικαιοσύνη πρὸς ἀδικίαν αὐτὴν κριθείη, occurs in Plat. Rep. 612 C, etc.; |
| 3 | random | `4c207e1e-p000305-l0178` | greek_latin_cs | 0.9324 | – | μόνῃ μοι τῆσδ᾽ ἄτερ β.; Soph. Ant. 566; οὐκ ἂν ἦν βιώσιμα ἀνθρώποις |
| 4 | random | `4c207e1e-p000447-l0188` | greek_latin_cs | 0.9277 | – | picere, πάντες δὲ θεοὺς ὡς εἰσορόωσιν ΙΙ. 12. 312; μιν .. θεὸν ὡς εἰσο- |
| 5 | random | `4c207e1e-p000559-l0005` | latin | 0.9808 | – | ἐπικελεύω, to exhort or encourage besides, to cheer on again, c. dat., |
| 6 | random | `4c207e1e-p000559-l0123` | latin | 0.9666 | B:numeric_table | clamation, Arist. Oec. 2. 31, 2; ἐπικηρυχθεὶς χθονί, Lat. rex renunciatus, |
| 7 | random | `4c207e1e-p000575-l0117` | latin | 0.9513 | – | ἐπισπαστικός, ή, όν, drawing to oneself, drawing in, τοῦ ὑγροῦ Arist. |
| 8 | random | `4c207e1e-p000640-l0102` | greek_latin_cs | 0.9505 | – | 709; εὐτυχῆ κλύουσα πρᾶξιν Soph. Tr. 293; c. dat., εὐτ. ἱκέσθαι τινί |
| 9 | random | `4c207e1e-p000640-l0189` | latin | 0.9771 | B:digit_heavy, B:word_length_outlier | to be in good repute, C. I. 4389. |
| 10 | random | `4c207e1e-p000811-l0032` | latin | 0.9581 | – | κάτω-κάρα, Adv. head downwards, Pind. Fr. 134, Ar. Ach. 945; heels |
| 11 | random | `4c207e1e-p000891-l0081` | latin | 0.9531 | – | λαβύρινθος [υ], ὁ, a labyrinth or maze, a large building consisting of |
| 12 | random | `4c207e1e-p001081-l0084` | greek_latin_cs | 0.9432 | – | point, ἔγχος ὀξ. σιδήρῳ Epigr. Gr. 790.5; ἄκρη ἐς μυχὸν ὀξυνθεῖσα Dion. |
| 13 | random | `4c207e1e-p001081-l0114` | latin | 0.9412 | B:digit_heavy, B:numeric_table | ὀξυθυμίας, ου, ὁ, one who is quick to anger, Poll. 2. 231., 6. 124. |
| 14 | random | `4c207e1e-p001176-l0049` | latin | 0.9875 | – | παρηγορητέον, verb. Adj. one must apply remedies, πρός τι Galen. |
| 15 | random | `4c207e1e-p001397-l0083` | latin | 0.9545 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | Gloss. Hipp.: hence to speak bitterly, sneer, εἰρωνεύεσθαι μετ᾿ ἐπισυρμοῦ 18.21,6; v. Wytt. Plut. 2. 79 C:-Pass. to grow fleshy, Aret. Caus. M. |
| 16 | random | `4c207e1e-p001397-l0122` | latin | 0.9434 | – | σαρκό-θλᾶσις, ἡ, and –θλασμα, τό, α bruise of the flesh, Theophan. |
| 17 | random | `4c207e1e-p001397-l0159` | latin | 0.9578 | – | σάρξ, ἡ, gen, σαρκός, Aeol. σύρξ Ε. Μ. 708. 31: (deriv. uncertain) :- |
| 18 | random | `4c207e1e-p001491-l0147` | latin | 0.9736 | B:digit_heavy, B:numeric_table | etc.; distinguished from mere ὁμοφωνία, Id. Pol. 2. 5, 14, Plut. 2. 389 |
| 19 | random | `4c207e1e-p001571-l0003` | latin | 0.957 | A:homoglyph_word, C:aspect_out, D:column_crossing_line | it as a shorter form of TA, ΤΑΝ, ΤΕΝ, τείνω, comparing ΓΑ, \| sodden flesh, Eur. Cycl. 246; ἄλφιτα πυρὶ τ. is consumed, Theocr. 2. |
| 20 | random | `4c207e1e-p001651-l0007` | latin | 0.9684 | – | such as Hesiod's, ὑποθῆκαι, cf. Isocr. 15 B, 23 C. |
| 21 | anomalous | `4c207e1e-p001588-l0092` | greek_latin_cs | 0.9371 | B:digit_heavy, B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | form τοσσάκι, ΙΙ. 21. 268., 22. 197, Simon., etc.; elided, τοσσάχ᾽ ὕδωρ \| 149, cf. Thuc. 6. 37; ἕτεροι οι ἄλλοι τοσοῦτοι as many again, Andoc. |
| 22 | anomalous | `4c207e1e-p001018-l0179` | latin | 0.9411 | B:digit_heavy, B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | Νεκύσιος, ὁ, the 11th month among the Cretans (24 July-22 Aug.), inf., οὐ γάρ τις νέμεσις φυγέειν κακόν 11. 14. 80, cf. Od. 1. 350; c. acc. |
| 23 | anomalous | `4c207e1e-p000844-l0036` | latin | 0.9579 | B:spacing_apostrophe, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | κοιμισμός, οῦ, ὁ, a putting to sleep: metaph. a softening of the accent Simon. 144, etc. (cf. κοινοβωμία); κοινὸν ἔρχεται κῦμ᾽ ᾿Αΐδα Pind. N. |
| 24 | anomalous | `4c207e1e-p000844-l0160` | greek_latin_cs | 0.9482 | A:homoglyph_word, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | (λόγος). To commune or take counsel with, τινι Hdt. 6. 23, and Att.; 19; κοινὸς ἅπασι γενέσθαι Isocr. 98 B, etc.; τῇ πρὸς πάντας φιλανθρωπία |
| 25 | anomalous | `4c207e1e-p001000-l0152` | latin | 0.9663 | B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | μονοφυσῖται, οἱ, monophysites, heretics who believed but one nature in Lys. 109. 11, cf. 108. 26., 110. 44; prob. so called, because they were |
| 26 | anomalous | `4c207e1e-p000320-l0191` | latin | 0.9553 | B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | γαλακτόομαι, Pass. to become milk or milky, Theophr. C. P. 1. 7, 3, καὶ εὐδίαις Arist. Η. Α. 4. 8, 15:-metaph. of the mind, calmness, gen- |
| 27 | anomalous | `4c207e1e-p000734-l0075` | latin | 0.9401 | B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | ἰσο-ϋψής, ές, equally high, τινι with another, Polyb. 8. 6, 4, Strabo 805. 152:-from Hom. downwds. the syncop. dual and pl. forms of the pf. |
| 28 | anomalous | `4c207e1e-p000164-l0118` | greek_latin_cs | 0.9549 | C:aspect_out, C:conf_min_low, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | ἀντιδουλεύω, to serve in turn, τοῖς τεκοῦσι γὰρ δύστηνος ὅστις μάντι- \|establish instead, substitute, ἄλλα Hdt. 9. 93; μὴ ἐλάσσω ἀντικαταστῆ- |
| 29 | anomalous | `4c207e1e-p000703-l0142` | greek_latin_cs | 0.9464 | B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | θραῦλος, η, ον, (not θραυλός, Arcad. p. 53. 10):-frangible, brittle, δύναμις τῆς ψυχῆς θρ. καὶ γεννητική Arist. de An. 2. 4, 14; ἡ θρ. ψυχή |
| 30 | anomalous | `4c207e1e-p001510-l0165` | latin | 0.9643 | C:aspect_out, C:conf_min_low, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | συνεπισύρομαι [1], Med, to draw to oneself together, Ideler Phys. I. Plut. Ages. 35. II. to collect, gather, Luc. Lexiph. 17; παρα- |
| 31 | anomalous | `4c207e1e-p000276-l0012` | latin | 0.9642 | B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | αὐτό-ποιος, ον, self-produced, i. e. not planted by man, naturally grown, Xen. An. 1. 2, 20; αὐτὸς βασιλεύς, αὐτὸς πατήρ, etc. 2. of oneself, |
| 32 | anomalous | `4c207e1e-p000415-l0080` | greek_latin_cs | 0.947 | C:aspect_out, C:conf_min_low, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | δυσημερία, Dor. – ᾶμερία, ἡ, an unlucky day, a mishap, misery, δυσα- · πρὸς δύσιν Arist. Mund. 3,8; ἀπὸ δύσεως C. Ι. 1755; πρὸς δύσει Polyb. |
| 33 | anomalous | `4c207e1e-p001287-l0185` | greek_latin_cs | 0.9259 | B:numeric_table, C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | πραϋ-τένων, Ιοπ. πρηϋτ-, ὁ, with tamed neck, ταῦρος Anth. P. 9. 299. πρέσβα θεά 5. 721., 8. 383, etc.; also, πρέσβα Διὺς θυγατὴρ ῎Ατη 19. |
| 34 | anomalous | `4c207e1e-p001000-l0107` | latin | 0.9659 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | μονοτροφία, ἡ, a rearing singly, opp. to κοινὴ ἐπιμέλεια, Plat. Polit. ὁ, ἡ, one-eyed, of the Cyclopes, Eur. Cycl. 21, 648; of the Arimaspi, |
| 35 | anomalous | `4c207e1e-p000621-l0080` | greek_latin_cs | 0.9409 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | εὐεπίβᾶτος, ον, easy to ascend, λόφος Strabo 234, Polyaen. 6.5 :-easy \| εὐεργέα λώπην Od. 13. 224; of gold, wrought, χρυσοῦ . . εὐεργέος ἑπτὰ |
| 36 | anomalous | `4c207e1e-p000575-l0003` | latin | 0.9449 | B:spacing_apostrophe, C:aspect_out, C:len_vs_book_high, D:column_crossing_line | ἔοικεν Menand. ᾿Ανδρ. 1, etc. :-Pass. to be in the dark or in uncertainty, \| proverb., ὅλην τὴν ἅμαξαν ἐπεσπάσω, Lat. plaustrum perculisti, Luc, |
| 37 | anomalous | `4c207e1e-p000276-l0005` | latin | 0.9723 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | αὐτο-ποιητικός, ή, όν, opp. to εἰδωλοποιϊκός, making not a copy, but either precedes both the Article and Subst., or follows them both, e. g. |
| 38 | anomalous | `4c207e1e-p001700-l0072` | greek_latin_cs | 0.9473 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | φιλόσπονδος, ον, used in drink-offerings, φιλοσπόνδου λιβός, of liba- μεθ' εἶναι ἐκ πατέρων φιλότητος Od. 15. 197; so, Soph. Aj. 1410, Ph. |
| 39 | anomalous | `4c207e1e-p001018-l0005` | latin | 0.9377 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | νεκρο-φάγος [α], ov, eating corpses or carrion, ὄρνιθες Dio C. 47. 40. parsley, Or. Sib. 5. 45:-Adj. Νέμειος, α, ον, Nemean, τὸν Ν. θῆρα Eur |
| 40 | anomalous | `4c207e1e-p000604-l0084` | latin | 0.9566 | C:aspect_out, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | ἔρρῖνον, τό, (ἐν, ῥίν) an errhine, sternutatory medicine, Paus. ap. Eust. ἐρεύθω); c. gen., Nonn. D. 11. 92: to blush scarlet, Anth. P. 12. 8; |

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
