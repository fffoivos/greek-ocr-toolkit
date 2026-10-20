# Adjudication request — dossier 134: archive_izvestiianatsars1112193839tsar / 363040a9

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Izvestiia na Tsarskitia prirodonauchni instituti v Sofiia = Mitteilungen aus den Konigl. naturwissenschaftlichen Instituten in Sofia, Bulgarien = Bulletin des Institutions royales d'histoire naturelle á Sofia, Bulgarie
- Source / key: `archive_izvestiianatsars1112193839tsar` / `363040a9` (wave `cyrillic`), year 1928
- Admitted lines: 214 on 6 pages; split {'test': 214}
- Script classes of its lines: {'cyrillic': 182, 'latin': 32} (majority `cyrillic`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 3.0 (rank 134 of 557): 1 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 5 of 214 lines carry other-script residue (by primary kind {'isolated_standalone': 2, 'isolated_ref_letter': 3}; 2 not explained by a number-adjacent reference letter or a letter+digit token) (2.34%; same-class book p95 1.47%)
- **A:book_other_lang_gt2pct** (weight 1) — 5.14% of lines guessed as another language than bg {'it': 1, 'ru': 6, 'de': 4} > 2% (same-class book p95 10.08%)

Aspect A features beyond 2σ vs same-class books (3): residue_line_share z=+3.6 (value 0.0234); latin_share_mean z=+2.0 (value 0.1509); cyrillic_share_mean z=-2.0 (value 0.8491)

Context: majority language `bg`, other-language share 0.0514; other-script residue lines 5 (unexplained 2); B line-flag counts {'digit_heavy': 7, 'punct_heavy': 1, 'long_token': 3}; C line-flag counts {'cpp_vs_book_out': 6, 'conf_min_low': 4, 'aspect_out': 10, 'cph_out_of_range': 2}; median confidence 0.968; two-column book False, column-crossing share 0.319.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `363040a9-p000104`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `363040a9-p000104-l0024` | cyrillic | 0.9757 | – | двойка. Хитинената покривка съ космици: |
| 2 | random | `363040a9-p000104-l0030` | latin | 0.9762 | – | 1. родъ Dysdera |
| 3 | random | `363040a9-p000114-l0016` | cyrillic | 0.9619 | – | която посока ся прониквали и по-добре диференциранитѣ видове. И днесъ |
| 4 | random | `363040a9-p000114-l0033` | cyrillic | 0.973 | C:cpp_vs_book_out | Разпространение въ България: Брезникъ (Дрѣнски 1936, |
| 5 | random | `363040a9-p000358-l0011` | cyrillic | 0.9662 | – | Презъ 1928 год. бѣ построено отъ сегашниятъ инспекторъ градинаръ г. В. |
| 6 | random | `363040a9-p000358-l0013` | cyrillic | 0.9459 | – | говия брѣгъ бѣ изграденъ сжщо така съ скаленъ материалъ, за да могатъ |
| 7 | random | `363040a9-p000358-l0015` | cyrillic | 0.9675 | – | Презъ 1928/29 год. бѣ коренно преустроенъ стариятъ алпинеумъ въ |
| 8 | random | `363040a9-p000358-l0039` | cyrillic | 0.9711 | – | една гиздава дървена кжщица, която стана канцелария на трудолюбивия |
| 9 | random | `363040a9-p000368-l0006` | cyrillic | 0.9853 | – | нение на Максъ Колбъ за отглеждане на високопланински растения. Загла- |
| 10 | random | `363040a9-p000368-l0020` | cyrillic | 0.9587 | – | логъ (1926 г.) най-ласкави думи за Поханъ Келереръ, който още презъ 1883 г. |
| 11 | random | `363040a9-p000368-l0022` | cyrillic | 0.9559 | C:aspect_out | и особено по Монте Роза. Въ казаниятъ каталогъ се споменавать много отъ |
| 12 | random | `363040a9-p000368-l0026` | cyrillic | 0.9635 | B:long_token | при сътрудничеството на градинаритѣ-алпинисти Йоханъ Обристь и Йоханъ Келереръ, |
| 13 | random | `363040a9-p000442-l0003` | cyrillic | 0.9717 | – | 3. Мжжкитѣ копулационни органи въ видъ на крушовидна луковица, ясно |
| 14 | random | `363040a9-p000442-l0019` | cyrillic | 0.979 | – | нено. Женското полово отверстие винаги е съ хитинена скулптура, |
| 15 | random | `363040a9-p000450-l0002` | cyrillic | 0.906 | C:aspect_out | Пенчо Дрѣнски |
| 16 | random | `363040a9-p000450-l0009` | latin | 0.9701 | – | Фиг. 18 и 19. Uloborus walckenaerius Latr. |
| 17 | random | `363040a9-p000450-l0017` | cyrillic | 0.9622 | – | Сжщо медитерански видъ, ограниченъ само върху срѣдиземномор- |
| 18 | random | `363040a9-p000450-l0024` | cyrillic | 0.9751 | – | Търново. Плете паяджината си предъ малкитѣ дупки и пещерки на издаде- |
| 19 | random | `363040a9-p000450-l0026` | latin | 0.9432 | B:digit_heavy | Родъ Hyptiotes Walckenaer 1833. |
| 20 | random | `363040a9-p000450-l0038` | latin | 0.9782 | – | H. paradoxus |
| 21 | anomalous | `363040a9-p000104-l0041` | cyrillic | 0.9509 | A:other_script_residue:isolated_ref_letter, C:cph_out_of_range, D:column_crossing_line, D:column_merge_line | (фиг. 1, b). Заднитѣ очи ясно отдѣлени отъ страничнитѣ (фиг. 6, d) |
| 22 | anomalous | `363040a9-p000442-l0016` | cyrillic | 0.9668 | A:lang_ne_book, A:script_share_outlier, C:cpp_vs_book_out | на метатарзуса у вида Amaurobius ferox. |
| 23 | anomalous | `363040a9-p000104-l0039` | cyrillic | 0.9348 | D:column_crossing_line, D:column_merge_line | Тарзалнитѣ членчета най-малко на III и IV двойки крачка носятъ по 2 |
| 24 | anomalous | `363040a9-p000104-l0036` | cyrillic | 0.9701 | D:column_crossing_line, D:column_merge_line | космици между тѣхъ (фиг. 1, а). Очитѣ на задната двойка се почти |
| 25 | anomalous | `363040a9-p000104-l0042` | cyrillic | 0.9794 | D:column_crossing_line, D:column_merge_line | 4. Всички тарзуси съ по 2 нокетовидни кукички и съ снопчета космици меж- |
| 26 | anomalous | `363040a9-p000104-l0032` | cyrillic | 0.944 | D:column_crossing_line, D:column_merge_line | страна; устнитѣ пластинки съ единъ добре забележимъ ржбъ (килъ). |
| 27 | anomalous | `363040a9-p000104-l0015` | cyrillic | 0.9614 | A:other_script_residue:isolated_standalone, D:column_crossing_line | Съ 3 или 2 нокътчета по тарзалнитѣ членчета (фиг. 1, а, b). Предната |
| 28 | anomalous | `363040a9-p000104-l0040` | cyrillic | 0.9733 | D:column_crossing_line, D:column_merge_line | нокътовидни кукички, отдѣлени помежду си съ снопчета космици |
| 29 | anomalous | `363040a9-p000104-l0031` | cyrillic | 0.975 | D:column_crossing_line, D:column_merge_line | Челюстнитѣ пластинки на върха заоблени и косо изрѣзани по външната си |
| 30 | anomalous | `363040a9-p000104-l0027` | cyrillic | 0.9795 | D:column_crossing_line, D:column_merge_line | 2. Челюстнитѣ пластинки (lames maxillaires) на върха заострени, а устната |
| 31 | anomalous | `363040a9-p000104-l0035` | cyrillic | 0.9625 | D:column_crossing_line, D:column_merge_line | 3. Тарзалнитѣ членчета носять по 3 нокетовидни кукички, безъ снопчета |
| 32 | anomalous | `363040a9-p000104-l0048` | cyrillic | 0.956 | C:conf_min_low, D:column_crossing_line | двойки крачка съ 3 кукички, безъ снопчета космици. В копулацио- |
| 33 | anomalous | `363040a9-p000358-l0021` | cyrillic | 0.9476 | A:lang_ne_book, A:script_share_outlier | динандъ І, на Елъ-тепе, 7. VII. 1914), Artemisia laxa Frit. (отъ Царъ Борись III, |
| 34 | anomalous | `363040a9-p000358-l0048` | cyrillic | 0.9392 | A:script_share_outlier, C:conf_min_low | Sünd., Alsine ledebouriana Fil. (отъ Мала Азия, събр. Князетѣ Борисъ и Ки- |
| 35 | anomalous | `363040a9-p000442-l0043` | cyrillic | 0.9442 | A:lang_ne_book, C:aspect_out | Фиг. 6. Разположението на очитѣ у родоветѣ: a. Eresus, 6. Uloborus, в. Uroctea. |
| 36 | anomalous | `363040a9-p000104-l0011` | cyrillic | 0.9718 | C:cpp_vs_book_out, D:column_crossing_line | Таблица за опредѣление на подсемействата и родоветѣ: |
| 37 | anomalous | `363040a9-p000450-l0034` | cyrillic | 0.9671 | C:cph_out_of_range, C:cpp_vs_book_out | Таблица за опредѣление на видоветѣ: |
| 38 | anomalous | `363040a9-p000104-l0006` | cyrillic | 0.9559 | C:aspect_out, D:column_crossing_line | троглоксени или ксенокавни видове, които еднакво добре живѣятъ |
| 39 | anomalous | `363040a9-p000358-l0026` | cyrillic | 0.9703 | A:homoglyph_word | kaea heldreichii Boiss. (отъ Тесалийския Олимпъ, 1937), една хубава серия |
| 40 | anomalous | `363040a9-p000358-l0030` | cyrillic | 0.9765 | A:homoglyph_word | Лондонската ботанич. градина), една друга серия отъ омайничета: Geum Bo- |

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
