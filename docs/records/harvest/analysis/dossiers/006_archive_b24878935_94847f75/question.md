# Adjudication request — dossier 006: archive_b24878935 / 94847f75

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Anglo-bŭlgarski rechnik (s proiznosheni︠︡iata) = English-Bulgarian dictionary : pronouncing and explanatory
- Source / key: `archive_b24878935` / `94847f75` (wave `cyrillic`), year 1908
- Admitted lines: 1249 on 25 pages; split {'train': 1249}
- Script classes of its lines: {'cyrillic': 1088, 'latin': 161} (majority `cyrillic`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 6.0 (rank 6 of 557): 4 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as top-60 by suspicion.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 4 of 1249 lines carry other-script residue (by primary kind {'isolated_standalone': 4}; 4 not explained by a number-adjacent reference letter or a letter+digit token) (0.32%; same-class book p95 1.47%)
- **C:hard_conf** (weight 0.5) — book median confidence=0.9305 < cyrillic book p5=0.9312 (N=22 books) — discount: class p5/p95 rule, ~5 % of books flagged by construction (C Limits)
- **C:hard_oov_pool** (weight 0.5) — book OOV share (pool vocab, support<=1 book)=0.7174 > cyrillic book p95=0.6958 (N=22 books) — discount: class p5/p95 rule, ~5 % of books flagged by construction (C Limits)

Aspect A features beyond 2σ vs same-class books (2): cyrillic_share_mean z=-2.4 (value 0.8303); latin_share_mean z=+2.4 (value 0.1696)
Aspect B features beyond 2σ vs same-class books (5): share punct_heavy z=+4.2 (value 0.0649); median punct_share z=+3.6 (value 0.1304); median n_tokens z=-2.6 (value 3.0); share dictionary_like z=+2.5 (value 0.028); median n_chars z=-2.2 (value 23.0)
Aspect C features beyond 2σ vs same-class books (6): oov_pool z=+2.9 (value 1.0); aspect z=-2.3 (value 10.903); label_len z=-2.2 (value 23.0); oov_pool_share z=+2.2 (value 0.7174); conf_mean z=-2.1 (value 0.93); width_ratio z=-2.0 (value 0.437)
Aspect D features beyond 2σ vs same-class books (1): multicol_page_share z=+2.2 (value 1.0)

Context: majority language `bg`, other-language share 0.0096; other-script residue lines 4 (unexplained 4); B line-flag counts {'punct_heavy': 81, 'long_token': 3, 'word_length_outlier': 18, 'dictionary_like': 35}; C line-flag counts {'cpp_vs_book_out': 4, 'conf_mean_low': 117, 'conf_min_low': 10, 'aspect_out': 36, 'cph_out_of_range': 147, 'len_vs_book_high': 1}; median confidence 0.93; two-column book True, column-crossing share 0.005.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `94847f75-p000378`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `94847f75-p000086-l0054` | cyrillic | 0.8992 | – | облѣгамъ; подпирамъ; на- |
| 2 | random | `94847f75-p000086-l0087` | cyrillic | 0.9528 | – | ство, животинство. |
| 3 | random | `94847f75-p000107-l0067` | cyrillic | 0.9317 | – | bottling (ботлинг) п. напъл |
| 4 | random | `94847f75-p000170-l0074` | cyrillic | 0.9049 | B:punct_heavy | -ed, а. напоенъ, сить |
| 5 | random | `94847f75-p000170-l0095` | cyrillic | 0.9336 | – | дякамъ, крѣкамъ, свик- |
| 6 | random | `94847f75-p000212-l0055` | cyrillic | 0.9386 | – | тиворѣчивъ, прѣкосло |
| 7 | random | `94847f75-p000233-l0093` | cyrillic | 0.939 | – | вица; овчарска тояга; епи- |
| 8 | random | `94847f75-p000252-l0032` | cyrillic | 0.9412 | – | струментъ за измѣрване |
| 9 | random | `94847f75-p000252-l0076` | latin | 0.9488 | – | decomposition (-позишън) п. |
| 10 | random | `94847f75-p000315-l0023` | cyrillic | 0.9032 | – | живащъ, изтекащъ; ре- |
| 11 | random | `94847f75-p000336-l0067` | cyrillic | 0.8968 | C:conf_mean_low | въ общинско или държав |
| 12 | random | `94847f75-p000356-l0013` | cyrillic | 0.9413 | B:punct_heavy, B:word_length_outlier | faith (фей) п. вѣра, упо- |
| 13 | random | `94847f75-p000378-l0043` | cyrillic | 0.892 | C:conf_mean_low, C:cph_out_of_range | вамъ се: шавамъ. |
| 14 | random | `94847f75-p000378-l0060` | cyrillic | 0.9268 | – | вамъ; употрѣбявамъ ри |
| 15 | random | `94847f75-p000420-l0007` | cyrillic | 0.9479 | – | ликъ; чифликчийски ес- |
| 16 | random | `94847f75-p000420-l0041` | cyrillic | 0.9756 | A:lang_ne_book | вещество у растенията. |
| 17 | random | `94847f75-p000439-l0013` | cyrillic | 0.9598 | – | good-, добросърдеченъ. |
| 18 | random | `94847f75-p000439-l0031` | cyrillic | 0.9156 | C:cph_out_of_range | съ изтравниче. |
| 19 | random | `94847f75-p000439-l0067` | cyrillic | 0.8955 | C:conf_mean_low | душевявамъ; vi. сгоре- |
| 20 | random | `94847f75-p000876-l0015` | latin | 0.9399 | – | supplication (-кейшън) п. |
| 21 | anomalous | `94847f75-p000190-l0004` | cyrillic | 0.9389 | B:word_length_outlier, C:len_vs_book_high, D:column_crossing_line, D:column_merge_line | клонность, усложнение, ❘ complicative (компликейтив) |
| 22 | anomalous | `94847f75-p000378-l0057` | cyrillic | 0.8935 | A:homoglyph_word, C:conf_mean_low, C:cph_out_of_range | вамъ ce въ високозву |
| 23 | anomalous | `94847f75-p000170-l0094` | latin | 0.8925 | A:script_share_outlier, B:punct_heavy, C:conf_mean_low | cluck (клък). vt. vi. кутку- |
| 24 | anomalous | `94847f75-p000690-l0019` | cyrillic | 0.8967 | A:script_share_outlier, C:conf_mean_low, C:conf_min_low | preordain (-ордейн) ст. прѣд- |
| 25 | anomalous | `94847f75-p000212-l0065` | cyrillic | 0.9101 | B:dictionary_like, B:long_token, C:cph_out_of_range | противосъпоставямъ: -се |
| 26 | anomalous | `94847f75-p000356-l0088` | latin | 0.9037 | B:punct_heavy, B:word_length_outlier, C:conf_mean_low | hood, n. лъжа; -nees, n. |
| 27 | anomalous | `94847f75-p000670-l0011` | latin | 0.9069 | A:script_share_outlier, B:punct_heavy, C:conf_mean_low | ness, n. - пость. |
| 28 | anomalous | `94847f75-p000315-l0075` | cyrillic | 0.9268 | A:lang_ne_book, A:script_share_outlier, B:punct_heavy | egotistic (-ти/стик) а. его- |
| 29 | anomalous | `94847f75-p000273-l0025` | cyrillic | 0.8933 | B:dictionary_like, C:conf_mean_low, C:cph_out_of_range | ржа - варено месо по- |
| 30 | anomalous | `94847f75-p000252-l0057` | cyrillic | 0.9344 | A:lang_ne_book, A:script_share_outlier, B:punct_heavy | decoction (-ко/кшън) п. есен- |
| 31 | anomalous | `94847f75-p000356-l0076` | cyrillic | 0.9108 | A:script_share_outlier, B:punct_heavy, B:word_length_outlier | -out, п. разпря; в. fall. |
| 32 | anomalous | `94847f75-p000522-l0033` | cyrillic | 0.8945 | B:dictionary_like, B:punct_heavy, C:conf_mean_low | чително: -ness, n. -ость, |
| 33 | anomalous | `94847f75-p000212-l0034` | latin | 0.9627 | A:other_script_residue:isolated_standalone, A:script_share_outlier | contractile (контрактил) α. |
| 34 | anomalous | `94847f75-p000086-l0003` | cyrillic | 0.8986 | A:homoglyph_word, B:word_length_outlier | да бъде; let it-so, тъй да |
| 35 | anomalous | `94847f75-p000130-l0020` | latin | 0.9079 | A:other_script_residue:isolated_standalone, C:conf_mean_low | cannicular (-пикюлър) α. |
| 36 | anomalous | `94847f75-p000712-l0003` | cyrillic | 0.9368 | A:homoglyph_word, A:script_share_outlier | prowess (ec) п. храбрость, |
| 37 | anomalous | `94847f75-p000378-l0034` | cyrillic | 0.9209 | A:script_share_outlier, B:punct_heavy | flotilla (-ти/ла) п. малка |
| 38 | anomalous | `94847f75-p000439-l0009` | cyrillic | 0.8955 | B:punct_heavy, C:conf_mean_low | ние; -burn, п. изгага, сто- |
| 39 | anomalous | `94847f75-p000252-l0007` | cyrillic | 0.9595 | C:aspect_out, C:cph_out_of_range | обявително. |
| 40 | anomalous | `94847f75-p000233-l0044` | cyrillic | 0.8963 | C:conf_mean_low, C:conf_min_low | Critic (критик) п. критикъ; |

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
