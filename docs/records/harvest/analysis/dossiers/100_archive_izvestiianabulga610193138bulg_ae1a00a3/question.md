# Adjudication request — dossier 100: archive_izvestiianabulga610193138bulg / ae1a00a3

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Izvestiia na Bulgarskoto entomologichno druzhestvo
- Source / key: `archive_izvestiianabulga610193138bulg` / `ae1a00a3` (wave `cyrillic`), year 1924
- Admitted lines: 1238 on 30 pages; split {'train': 1238}
- Script classes of its lines: {'cyrillic': 1142, 'latin': 96} (majority `cyrillic`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 3.0 (rank 100 of 557): 1 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 3 of 1238 lines carry other-script residue (by primary kind {'isolated_standalone_lookalike': 1, 'isolated_standalone': 2}; 3 not explained by a number-adjacent reference letter or a letter+digit token) (0.24%; same-class book p95 1.47%)
- **A:book_other_lang_gt2pct** (weight 1) — 4.36% of lines guessed as another language than bg {'la': 1, 'ru': 25, 'de': 15, 'en': 11, 'fr': 2} > 2% (same-class book p95 10.08%)
- **D:page_line_count_outlier** (weight 0) — 0 page(s) above and 1 below the cyrillic page line-count p99/p1 — discount: wave p1/p99 page rule, ~1 % of pages per side by construction (D §9)

Aspect B features beyond 2σ vs same-class books (2): share numeric_table z=+3.3 (value 0.0016); share bibliographic z=+2.2 (value 0.0048)

Context: majority language `bg`, other-language share 0.0436; other-script residue lines 3 (unexplained 3); B line-flag counts {'digit_heavy': 21, 'punct_heavy': 2, 'all_caps': 12, 'long_token': 11, 'word_length_outlier': 9, 'numeric_table': 2, 'bibliographic': 6, 'dictionary_like': 6}; C line-flag counts {'cpp_vs_book_out': 27, 'conf_mean_low': 2, 'conf_min_low': 13, 'aspect_out': 11, 'cph_out_of_range': 28}; median confidence 0.972; two-column book False, column-crossing share 0.523.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `ae1a00a3-p000150`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `ae1a00a3-p000107-l0015` | cyrillic | 0.9771 | – | на майка си. Още твърде малки и слаби, голѣмната на кои- |
| 2 | random | `ae1a00a3-p000107-l0016` | cyrillic | 0.9177 | B:word_length_outlier | -то не надминава 1/3 - 1/5 мм., а понѣкога и 1/8 мм., тѣ тър- |
| 3 | random | `ae1a00a3-p000128-l0031` | cyrillic | 0.952 | – | ство. Така напр., въ 25 селища отъ горе-посоченитѣ б ма- |
| 4 | random | `ae1a00a3-p000128-l0034` | cyrillic | 0.9628 | B:digit_heavy | нападнати или 49,500 дек. отъ 88,540 дек. всичко за тия се- |
| 5 | random | `ae1a00a3-p000150-l0025` | cyrillic | 0.982 | – | разпространения видъ. |
| 6 | random | `ae1a00a3-p000273-l0014` | cyrillic | 0.9772 | – | ната на по-главнитѣ е достатъчна гаранция за истиностьта на |
| 7 | random | `ae1a00a3-p000317-l0035` | cyrillic | 0.9721 | – | лително отъ общината да бератъ кестени и, разбира се, въ |
| 8 | random | `ae1a00a3-p000358-l0020` | cyrillic | 0.9722 | – | лопатари, които ся развъдени въ казаното ловно стопанство, |
| 9 | random | `ae1a00a3-p000400-l0022` | cyrillic | 0.9771 | – | членъ. Въ височайшия отговоръ, изпратенъ на дружеството |
| 10 | random | `ae1a00a3-p000442-l0019` | cyrillic | 0.964 | – | tria dispar (гжботворката) въ Америка. Пренесена отъ Ев- |
| 11 | random | `ae1a00a3-p000462-l0013` | cyrillic | 0.9871 | – | Следъ като изложихме какво е направено до сега, следва да |
| 12 | random | `ae1a00a3-p000483-l0015` | cyrillic | 0.977 | – | Следъ този първи приносъ, до сега нѣмаме други изуч- |
| 13 | random | `ae1a00a3-p000566-l0019` | cyrillic | 0.9399 | – | (Е. С.). - Общо разпространение: Европа, Северна |
| 14 | random | `ae1a00a3-p000566-l0023` | cyrillic | 0.9589 | – | С. съ 37 екземпляра. — Разпространение въ България: |
| 15 | random | `ae1a00a3-p000609-l0043` | cyrillic | 0.957 | – | стеблена муха и настяпилитѣ измѣнения въ нападнатитѣ |
| 16 | random | `ae1a00a3-p000671-l0024` | cyrillic | 0.9772 | – | мледѣлието, трѣбва сама да даде починъ за една съвременна |
| 17 | random | `ae1a00a3-p000881-l0033` | cyrillic | 0.9759 | – | рата. Въ Харманлийска околия, освенъ това, сърбежният ь |
| 18 | random | `ae1a00a3-p000901-l0035` | latin | 0.9614 | – | Въ 1924 г. Falleroni, изучавайки Ап. maculipennis въ |
| 19 | random | `ae1a00a3-p000921-l0019` | cyrillic | 0.9649 | – | 1. Цѣлиять абдоменъ, който е ясно очертанъ и съ ясно |
| 20 | random | `ae1a00a3-p000965-l0024` | cyrillic | 0.9515 | B:word_length_outlier | а сжщо така и при Виена. |
| 21 | anomalous | `ae1a00a3-p000881-l0001` | cyrillic | 0.8974 | B:all_caps, C:conf_mean_low, C:cph_out_of_range, C:cpp_vs_book_out | БОРБА СЪ ВРЕДНИТЬ НАСѢКОМИ ПО СКЛАДИРА- |
| 22 | anomalous | `ae1a00a3-p000881-l0006` | latin | 0.9841 | A:lang_ne_book, B:all_caps, B:digit_heavy, C:cph_out_of_range | OF TSAREVO DURING 1937 |
| 23 | anomalous | `ae1a00a3-p000587-l0017` | latin | 0.9717 | A:homoglyph_word, A:lang_ne_book, B:digit_heavy | Royale Entomologique d'Egypte“, кн. 1-3, год. 1933. На стр. 77 |
| 24 | anomalous | `ae1a00a3-p000400-l0052` | cyrillic | 0.9318 | B:digit_heavy, B:numeric_table, C:cpp_vs_book_out | стр. 22, 23, 24; кн. IV стр. 22 и пр. Царъ Борись III е почетенъ членъ |
| 25 | anomalous | `ae1a00a3-p000921-l0004` | latin | 0.9865 | A:lang_ne_book, B:all_caps, C:cph_out_of_range | DAS ERSTE FOSSILE INSEKT AUS BULGARIEN |
| 26 | anomalous | `ae1a00a3-p000901-l0003` | cyrillic | 0.9573 | B:all_caps, C:cph_out_of_range, C:cpp_vs_book_out | НА МАЛАРИЯТА |
| 27 | anomalous | `ae1a00a3-p000901-l0002` | cyrillic | 0.9526 | B:all_caps, C:cph_out_of_range, C:cpp_vs_book_out | И ТЪХНАТА РОЛЯ ПРИ РАЗПРОСТРАНЕНИЕТО |
| 28 | anomalous | `ae1a00a3-p000881-l0002` | cyrillic | 0.9309 | B:all_caps, C:cph_out_of_range, C:cpp_vs_book_out | НИТЬ ЗЪРНЕНИ ХРАНИ ВЪ ГР. ЦАРЕВО ПРЕЗЪ 1937 Г. |
| 29 | anomalous | `ae1a00a3-p000901-l0006` | latin | 0.9877 | A:lang_ne_book, B:all_caps, C:cph_out_of_range | THEIR RELATION TO THE DISTRIBUTION OF MALARIA |
| 30 | anomalous | `ae1a00a3-p000881-l0005` | latin | 0.9857 | A:lang_ne_book, B:all_caps, C:cph_out_of_range | STORED GRAIN PEST CONTOL IN THE CITY |
| 31 | anomalous | `ae1a00a3-p000631-l0001` | cyrillic | 0.9193 | B:all_caps, C:cph_out_of_range, C:cpp_vs_book_out | МАТЕРИАЛИ ЗА БОРБА ПРОТИВЪ ТЮТЮНОВИЯТЪ ТРИПСЪ |
| 32 | anomalous | `ae1a00a3-p000150-l0040` | cyrillic | 0.9729 | D:column_crossing_line, D:column_merge_line | вияха и преследваха жертвитѣ си, забелязахме нѣколко жъл- |
| 33 | anomalous | `ae1a00a3-p000150-l0043` | cyrillic | 0.979 | D:column_crossing_line, D:column_merge_line | различа по летежа и по хабитуса си, изобщо, отъ ободитѣ. |
| 34 | anomalous | `ae1a00a3-p000150-l0049` | cyrillic | 0.9674 | D:column_crossing_line, D:column_merge_line | а следяха летящитѣ около добитъка ободи, издебваха сго- |
| 35 | anomalous | `ae1a00a3-p000150-l0046` | cyrillic | 0.974 | D:column_crossing_line, D:column_merge_line | за да се увѣря въ това. Когато почнахъ да ги следя, за да |
| 36 | anomalous | `ae1a00a3-p000150-l0048` | cyrillic | 0.9667 | D:column_crossing_line, D:column_merge_line | едно съ ободитѣ, не кацаха по-добитъка да смучатъ кръвь, |
| 37 | anomalous | `ae1a00a3-p000150-l0039` | cyrillic | 0.9587 | D:column_crossing_line, D:column_merge_line | Пжтувайки съ конетѣ, около които роякъ ободи се |
| 38 | anomalous | `ae1a00a3-p000150-l0044` | cyrillic | 0.9753 | D:column_crossing_line, D:column_merge_line | И първоначално допуснахъ, че това ще да е полярния видъ |
| 39 | anomalous | `ae1a00a3-p000150-l0045` | cyrillic | 0.9752 | D:column_crossing_line, D:column_merge_line | ободъ Tabanus tarandinus. И побързахъ да хвана екземпляръ, |
| 40 | anomalous | `ae1a00a3-p000150-l0050` | cyrillic | 0.9659 | D:column_crossing_line, D:column_merge_line | денъ моментъ и съ сржчностьта на соколъ, сграбваха нѣкой |

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
