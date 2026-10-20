# Adjudication request — dossier 108: archive_izvestiianatsars12192829tsar / b930919b

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Izvestiia na Tsarskitia prirodonauchni instituti v Sofiia = Mitteilungen aus den Konigl. naturwissenschaftlichen Instituten in Sofia, Bulgarien = Bulletin des Institutions royales d'histoire naturelle á Sofia, Bulgarie
- Source / key: `archive_izvestiianatsars12192829tsar` / `b930919b` (wave `cyrillic`), year 1928
- Admitted lines: 799 on 22 pages; split {'train': 799}
- Script classes of its lines: {'cyrillic': 729, 'latin': 70} (majority `cyrillic`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 3.0 (rank 108 of 557): 2 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 1; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 12 of 799 lines carry other-script residue (by primary kind {'isolated_alnum': 5, 'isolated_standalone': 5, 'isolated_ref_letter': 1, 'isolated_standalone_lookalike': 1}; 6 not explained by a number-adjacent reference letter or a letter+digit token) (1.50%; same-class book p95 1.47%)
- **A:book_other_lang_gt2pct** (weight 0) — 2.13% of lines guessed as another language than bg {'ru': 14, 'de': 2, 'fr': 1} > 2% (same-class book p95 10.08%) — discount: 14/17 other-language lines are ru/bg/sr confusions of the function-word detector (A key finding 2)
- **D:page_line_count_outlier** (weight 0) — 0 page(s) above and 1 below the cyrillic page line-count p99/p1 — discount: wave p1/p99 page rule, ~1 % of pages per side by construction (D §9)

Aspect A features beyond 2σ vs same-class books (1): residue_line_share z=+2.1 (value 0.015)
Aspect D features beyond 2σ vs same-class books (1): share_dup_within_page z=+2.9 (value 0.02)

Context: majority language `bg`, other-language share 0.0213; other-script residue lines 12 (unexplained 6); B line-flag counts {'digit_heavy': 20, 'punct_heavy': 4, 'long_token': 6, 'word_length_outlier': 4, 'bibliographic': 2, 'dictionary_like': 10}; C line-flag counts {'cpp_vs_book_out': 36, 'conf_mean_low': 2, 'conf_min_low': 14, 'aspect_out': 29, 'cph_out_of_range': 7}; median confidence 0.968; two-column book False, column-crossing share 0.31.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `b930919b-p000296`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `b930919b-p000177-l0025` | cyrillic | 0.9743 | – | ната перка, почти до опашката сж разположени четири тъмни, отдѣлени съ |
| 2 | random | `b930919b-p000187-l0001` | cyrillic | 0.9745 | C:cpp_vs_book_out | Риби отъ семейство Cobitidae въ България |
| 3 | random | `b930919b-p000187-l0033` | cyrillic | 0.9644 | – | петна, разграничени сжщо съ толкова голѣми, само малко по-тѣсни, свѣтли |
| 4 | random | `b930919b-p000277-l0038` | cyrillic | 0.9755 | – | заденъ ржбъ на крилото. |
| 5 | random | `b930919b-p000287-l0030` | latin | 0.9865 | – | (Opistocanthae) |
| 6 | random | `b930919b-p000314-l0022` | cyrillic | 0.9645 | – | ция, Швейцария, Белгия, Англия, Германия, Австрия, Унгария; Сибирь, Се- |
| 7 | random | `b930919b-p000325-l0064` | cyrillic | 0.9523 | – | Очитѣ съ 2-3 пурпурни ивици. |
| 8 | random | `b930919b-p000336-l0034` | cyrillic | 0.9583 | B:dictionary_like | Мжжки: Прилича на женския. Очитѣ съ зеленъ блѣсъкъ и една пур- |
| 9 | random | `b930919b-p000336-l0043` | cyrillic | 0.9714 | – | Централни Родопи Пещерско, Чехлйово (Чепинско); Казанлъшко при |
| 10 | random | `b930919b-p000336-l0044` | cyrillic | 0.9634 | B:bibliographic | с. Турия; Дупница. Май, юни и юли. Недѣлковъ (1912) го споменава отъ: |
| 11 | random | `b930919b-p000365-l0004` | cyrillic | 0.965 | – | отъ него видъ е констатиранъ вече въ България или не и кжде у насъ той |
| 12 | random | `b930919b-p000385-l0013` | cyrillic | 0.939 | – | Бачковския монастиръ (Е. С., 8. VII. 1926 отъ Н. В. Царь Борись III.). 8. Въ |
| 13 | random | `b930919b-p000394-l0005` | cyrillic | 0.9699 | – | Юго-западна България: 1. Витоша при с. Владая (Дрѣнов. 1906 стр. 10 |
| 14 | random | `b930919b-p000402-l0032` | cyrillic | 0.9723 | B:long_token | Отъ видоветѣ на рода Limenitis, този е най-разпространения и най-често |
| 15 | random | `b930919b-p000402-l0039` | cyrillic | 0.9726 | – | презъ месецъ май и началото на юний и друга лѣтна презъ юлий и |
| 16 | random | `b930919b-p000402-l0046` | cyrillic | 0.9589 | C:aspect_out, C:cpp_vs_book_out | роятно грѣшка въ етикетирането, тъй че екзъмпляра ilia вѣроятно не ще да е ловенъ въ Со- |
| 17 | random | `b930919b-p000414-l0029` | cyrillic | 0.9612 | – | Пиринъ пл.: 11. При Бжндеришкитѣ езера и по Уйнатиевъ вр. надъ тѣхъ |
| 18 | random | `b930919b-p000424-l0021` | cyrillic | 0.9844 | – | 1900 м. вис.. Явява се само въ едно поколение презъ годината. |
| 19 | random | `b930919b-p000433-l0021` | cyrillic | 0.9821 | – | Общо разпространение: Цѣла извънполярна Европа, Британия, |
| 20 | random | `b930919b-p000461-l0004` | cyrillic | 0.9738 | – | северо-източна Италия при Гьорцъ (Stauder 1922 p. 15), Австрия, Унгария, |
| 21 | anomalous | `b930919b-p000296-l0041` | cyrillic | 0.9644 | A:other_script_residue:isolated_standalone, D:column_crossing_line, D:column_merge_line | R, напълно кафява. Апикалното петно не е отдѣлено отъ тъмния |
| 22 | anomalous | `b930919b-p000402-l0045` | cyrillic | 0.9736 | A:homoglyph_word, C:aspect_out, C:cpp_vs_book_out | var. eos Ros., който сигурно принадлежи на втората лѣтна генерация. И въ тоя случай има вѣ- |
| 23 | anomalous | `b930919b-p000402-l0042` | cyrillic | 0.9689 | A:homoglyph_word, C:aspect_out, C:cpp_vs_book_out | (Soc. Ent. 1896) и Марковичъ (1909 стр. 7). Ние не сме видѣли обаче нито единъ доказателственъ |
| 24 | anomalous | `b930919b-p000296-l0055` | cyrillic | 0.9715 | C:aspect_out, C:cpp_vs_book_out, D:column_crossing_line | обаче да се докаже и Chr, marmoratus Rossi., който сега се поставя като синонимъ на Chr. |
| 25 | anomalous | `b930919b-p000296-l0015` | cyrillic | 0.9276 | B:punct_heavy, B:word_length_outlier, C:conf_min_low | жината на г. (фиг. 3, в) |
| 26 | anomalous | `b930919b-p000296-l0054` | cyrillic | 0.9747 | C:aspect_out, C:cpp_vs_book_out, D:column_crossing_line | който действително у насъ постига най-широко разпространение. Не е изключена възможностьта |
| 27 | anomalous | `b930919b-p000296-l0051` | cyrillic | 0.9655 | C:aspect_out, C:cpp_vs_book_out, D:column_crossing_line | фия, Панчерево, Своге, Варна, Созополъ и Бургасъ съ бележката, че тоя видъ е най-разпро- |
| 28 | anomalous | `b930919b-p000296-l0050` | cyrillic | 0.9669 | A:lang_ne_book, A:script_share_outlier, D:column_crossing_line | 1) Недѣлковъ (1912. стр. 185) споменава и вида Chrysops marmoratus Rossi. отъ Со- |
| 29 | anomalous | `b930919b-p000296-l0038` | cyrillic | 0.9773 | D:column_crossing_line, D:column_merge_line | Коремчето (абдомена) предимно жълто, съ фини, ясно ограничени |
| 30 | anomalous | `b930919b-p000325-l0018` | cyrillic | 0.9607 | D:column_crossing_line, D:column_merge_line | лѣмитѣ. Очитѣ безъ ивици. І-ия абдоменаленъ сегментъ често |
| 31 | anomalous | `b930919b-p000296-l0046` | cyrillic | 0.9691 | D:column_crossing_line, D:column_merge_line | образувана отъ ясно-свѣтли трижгълни петна. Апикалното петно |
| 32 | anomalous | `b930919b-p000287-l0015` | cyrillic | 0.9195 | A:other_script_residue:isolated_standalone, C:conf_min_low | г. и т. предъ края съединени и клетката R. затворена |
| 33 | anomalous | `b930919b-p000325-l0025` | cyrillic | 0.96 | D:column_crossing_line, D:column_merge_line | 11. Абдомена матно-черникавъ съ 2 широки свѣтли надлъжни ивици |
| 34 | anomalous | `b930919b-p000296-l0044` | cyrillic | 0.972 | D:column_crossing_line, D:column_merge_line | Коремчето предимно тъмно, кално-жълто съ голѣми черни-глан- |
| 35 | anomalous | `b930919b-p000296-l0022` | cyrillic | 0.9495 | D:column_crossing_line, D:column_merge_line | І и ІІ сегм. жълти петна. Една хиалинна ивичка дѣли апикал- |
| 36 | anomalous | `b930919b-p000100-l0029` | cyrillic | 0.9649 | A:homoglyph_word, A:script_share_outlier | пляри принадлежать на ssp. gracilior Geh. |
| 37 | anomalous | `b930919b-p000325-l0029` | cyrillic | 0.9534 | D:column_crossing_line, D:column_merge_line | Горниятъ оченъ ржбъ безъ космици, рѣдко съ кжси космици |
| 38 | anomalous | `b930919b-p000325-l0016` | cyrillic | 0.9693 | D:column_crossing_line, D:column_merge_line | бѣли петна или ивици върху абдомена. Задния оченъ ржбъ безъ |
| 39 | anomalous | `b930919b-p000296-l0017` | cyrillic | 0.968 | D:column_crossing_line, D:column_merge_line | Апикалното петно на крилата преминава на широко г, като за- |
| 40 | anomalous | `b930919b-p000305-l0039` | cyrillic | 0.9759 | D:column_crossing_line, D:column_merge_line | Пипалата и абдомена обрасли изцѣло съ жълти космици Silv. vituli Fabr. |

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
