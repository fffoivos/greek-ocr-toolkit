# Adjudication request — dossier 061: parliament_proceedings_1975_2000 / 26ee7610

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: ΣΥΝΕΔΡΙΑΣΗ ΝΔ΄(54) 11 ΙΑΝΟΥΑΡΙΟΥ 1995
- Source / key: `parliament_proceedings_1975_2000` / `26ee7610` (wave `parliament`), year 1995
- Admitted lines: 261 on 10 pages; split {'train': 261}
- Script classes of its lines: {'latin': 169, 'greek_mono': 79, 'greek_latin_cs': 13} (majority `latin`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 4.0 (rank 61 of 557): 2 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 1 of 261 lines carry other-script residue (by primary kind {'isolated_standalone_lookalike': 1}; 1 not explained by a number-adjacent reference letter or a letter+digit token) (0.38%; same-class book p95 1.79%)
- **A:book_other_lang_gt2pct** (weight 1) — 36.78% of lines guessed as another language than en {'el': 92, 'de': 1, 'fr': 3} > 2% (same-class book p95 40.37%)

Aspect B features beyond 2σ vs same-class books (1): share running_title_or_page_number z=+2.7 (value 0.0498)
Aspect C features beyond 2σ vs same-class books (3): crop_h z=+3.0 (value 70.0); crop_w z=+2.2 (value 1790.0); chars_per_100px z=-2.1 (value 2.833)

Context: majority language `en`, other-language share 0.3678; other-script residue lines 1 (unexplained 1); B line-flag counts {'digit_heavy': 6, 'punct_heavy': 3, 'all_caps': 29, 'long_token': 1, 'word_length_outlier': 10, 'running_title_or_page_number': 13, 'dictionary_like': 4}; C line-flag counts {'cpp_out_of_range': 52, 'conf_mean_low': 1, 'conf_min_low': 1, 'aspect_out': 4, 'oov_pool_high': 3, 'cph_out_of_range': 39, 'len_vs_book_high': 19}; median confidence 0.979; two-column book False, column-crossing share 0.0.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `26ee7610-p000143`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `26ee7610-p000019-l0004` | latin | 0.9882 | – | development of |
| 2 | random | `26ee7610-p000019-l0027` | latin | 0.9858 | – | depositary of this Agreement. |
| 3 | random | `26ee7610-p000019-l0039` | latin | 0.9497 | C:cph_out_of_range | approval; or |
| 4 | random | `26ee7610-p000019-l0051` | latin | 0.9837 | – | network link, in a continuous manner, the territories of at |
| 5 | random | `26ee7610-p000071-l0046` | greek_mono | 0.9704 | A:lang_ne_book | Νυρεμβέργη |
| 6 | random | `26ee7610-p000071-l0093` | latin | 0.9334 | – | (Forbach-) Saarbrucken |
| 7 | random | `26ee7610-p000071-l0101` | latin | 0.975 | – | Bebra (-Gerstungen) |
| 8 | random | `26ee7610-p000071-l0105` | latin | 0.9561 | C:cph_out_of_range | Schirnding - |
| 9 | random | `26ee7610-p000090-l0032` | greek_mono | 0.97 | A:lang_ne_book, B:all_caps | ΧΑΡΤΗΣ ΤΩΝ ΣΙΔΗΡΟΔΡΟΜΙΚΩΝ ΓΡΑΜΜΩΝ ΠΟΥ ΑΠΟΤΕΛΟΥΝ ΜΕΡΟΣ |
| 10 | random | `26ee7610-p000108-l0007` | latin | 0.9405 | B:word_length_outlier | (Göteborg-) Frederikshavn-Arhus-Fredericia (-Flensburg) |
| 11 | random | `26ee7610-p000108-l0040` | latin | 0.9684 | – | (-Petrovice U. Karviné) |
| 12 | random | `26ee7610-p000127-l0019` | latin | 0.9814 | – | it is easily and quickly accessible by road from the economic |
| 13 | random | `26ee7610-p000127-l0021` | latin | 0.9863 | – | within the rail network, it is well connected with long-distance |
| 14 | random | `26ee7610-p000127-l0023` | latin | 0.9845 | – | has good access to the fast freight trains of combined transport. |
| 15 | random | `26ee7610-p000127-l0025` | latin | 0.9826 | – | The minimum standards for intermediate stations stipulated below shall |
| 16 | random | `26ee7610-p000127-l0029` | latin | 0.9854 | C:cph_out_of_range | Minimum standards for intermediate stations |
| 17 | random | `26ee7610-p000143-l0048` | greek_mono | 0.9862 | A:lang_ne_book | = Μέρος της γραμμής σημαντικό για συνδυασμένες |
| 18 | random | `26ee7610-p000159-l0005` | latin | 0.9543 | B:all_caps, C:cph_out_of_range, D:dup_within_book_suspicious | ΕΠΙΣΗΜΗ ΜΕΤΑΦΡΑΣΗ TRADUCTION OFFICIELLE |
| 19 | random | `26ee7610-p000159-l0014` | latin | 0.9648 | C:cph_out_of_range | C-E 562 Bucuresti -Constanta |
| 20 | random | `26ee7610-p000176-l0027` | latin | 0.9819 | – | Constanta (Τουρκία |
| 21 | anomalous | `26ee7610-p000143-l0001` | greek_mono | 0.9306 | A:lang_ne_book, B:all_caps, B:digit_heavy, B:running_title_or_page_number, C:cph_out_of_range | ΣΥΝΕΔΡΙΑΣΗ ΝΔ' – 11 ΙΑΝΟΥΑΡΙΟΥ 1995 |
| 22 | anomalous | `26ee7610-p000159-l0001` | greek_mono | 0.9319 | A:lang_ne_book, B:all_caps, B:digit_heavy, B:running_title_or_page_number, C:cph_out_of_range | ΣΥΝΕΔΡΙΑΣΗ ΝΔ' – 11 ΙΑΝΟΥΑΡΙΟΥ 1995 |
| 23 | anomalous | `26ee7610-p000159-l0030` | greek_mono | 0.9702 | A:lang_ne_book, B:all_caps, C:cph_out_of_range, D:dup_within_book_suspicious | ΜΕΤΑΦΡΑΣΤΙΚΟ ΓΡΑΦΕΙΟ ΥΠΟΥΡΓΕΙΟΥ ΕΞΩΤΕΡΙΚΩΝ ΑΘΗΝΑ |
| 24 | anomalous | `26ee7610-p000143-l0051` | greek_mono | 0.9447 | A:lang_ne_book, B:all_caps, C:aspect_out, C:cph_out_of_range | ΜΕΤΑΦΡΑΣΤΙΚΟ ΓΡΑΦΕΙΟ ΥΠΟΥΡΓΕΙΟΥ ΕΞΩΤΕΡΙΚΩΝ, ΑΘΗΝΑ |
| 25 | anomalous | `26ee7610-p000071-l0001` | greek_mono | 0.936 | A:lang_ne_book, B:all_caps, B:digit_heavy, B:running_title_or_page_number | ΣΥΝΕΔΡΙΑΣΗ ΝΔ' - 11 ΙΑΝΟΥΑΡΙΟΥ 1995 |
| 26 | anomalous | `26ee7610-p000090-l0033` | greek_mono | 0.9655 | A:lang_ne_book, B:all_caps, C:cph_out_of_range, C:oov_pool_high | ΤΟΥ ΕΥΡΩΠΑΙΚΟΥ ΔΙΚΤΥΟΥ |
| 27 | anomalous | `26ee7610-p000055-l0001` | greek_mono | 0.9221 | A:lang_ne_book, B:all_caps, B:digit_heavy, B:running_title_or_page_number | ΣΥΝΕΔΡΙΑΣΗ ΝΔ' – 11 ΙΑΝΟΥΑΡΙΟΥ 1995 |
| 28 | anomalous | `26ee7610-p000019-l0001` | greek_mono | 0.935 | A:lang_ne_book, B:all_caps, B:digit_heavy, B:running_title_or_page_number | ΣΥΝΕΔΡΙΑΣΗ ΝΔ' - 11 ΙΑΝΟΥΑΡΙΟΥ 1995 |
| 29 | anomalous | `26ee7610-p000055-l0002` | greek_mono | 0.9692 | A:lang_ne_book, B:all_caps, B:running_title_or_page_number, C:cph_out_of_range | ΕΠΙΣΗΜΗ ΜΕΤΑΦΡΑΣΗ |
| 30 | anomalous | `26ee7610-p000176-l0039` | latin | 0.971 | A:lang_ne_book, B:all_caps, C:cph_out_of_range, D:dup_within_book_suspicious | BUREAU DES TRADUCTIONS DU MINISTERE DES AFFAIRES ETRANGERES DE |
| 31 | anomalous | `26ee7610-p000143-l0031` | greek_mono | 0.9805 | A:lang_ne_book, C:aspect_out, C:len_vs_book_high | περίπτωση δεν υποδηλώνει εάν τα κράτη είναι ή προτίθενται να |
| 32 | anomalous | `26ee7610-p000071-l0002` | greek_mono | 0.9681 | A:lang_ne_book, B:all_caps, B:running_title_or_page_number | ΕΠΙΣΗΜΗ ΜΕΤΑΦΡΑΣΗ |
| 33 | anomalous | `26ee7610-p000090-l0021` | greek_mono | 0.9291 | A:lang_ne_book, B:all_caps, C:conf_min_low | · ΕΠΙΣΗΜΗ ΜΕΤΑΦΡΑΣΗ |
| 34 | anomalous | `26ee7610-p000071-l0081` | greek_mono | 0.8983 | A:lang_ne_book, B:punct_heavy, C:conf_mean_low | (Λιέγη-) Άαχεν |
| 35 | anomalous | `26ee7610-p000143-l0003` | latin | 0.9435 | B:all_caps, C:cph_out_of_range, D:dup_within_book_suspicious | ΕΠΙΣΗΜΗ ΜΕΤΑΦΡΑΣΗ TRADUCTION OFFICIELLE |
| 36 | anomalous | `26ee7610-p000071-l0085` | greek_latin_cs | 0.9714 | A:lang_ne_book, B:dictionary_like, C:cph_out_of_range | Duisburg - Ντόρτμουντ |
| 37 | anomalous | `26ee7610-p000090-l0003` | latin | 0.9474 | B:all_caps, B:running_title_or_page_number, C:cph_out_of_range | TRADUCTION OFFICIELLE |
| 38 | anomalous | `26ee7610-p000159-l0031` | latin | 0.9791 | A:lang_ne_book, B:all_caps, D:dup_within_book_suspicious | BUREAU DES TRADUCTIONS DU MINISTERE DES AFFAIRES ETRANGERES DE |
| 39 | anomalous | `26ee7610-p000143-l0052` | latin | 0.9553 | A:lang_ne_book, B:all_caps, C:cph_out_of_range | BUREAU DESK TRADUCTIONS DU MINISTERE DES AFFAIRES ETRANGERES DE |
| 40 | anomalous | `26ee7610-p000176-l0038` | greek_mono | 0.961 | A:lang_ne_book, B:all_caps, D:dup_within_book_suspicious | ΜΕΤΑΦΡΑΣΤΙΚΟ ΓΡΑΦΕΙΟ ΥΠΟΥΡΓΕΙΟΥ ΕΞΩΤΕΡΙΚΩΝ ΑΘΗΝΑ |

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
