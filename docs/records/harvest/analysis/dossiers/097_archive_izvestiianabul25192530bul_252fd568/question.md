# Adjudication request — dossier 097: archive_izvestiianabul25192530bul / 252fd568

You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and evaluation data (line image → text). Each admitted line is a crop of the scan plus Google's transcription (the "label"). An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the book's labels are usable.

## The book

- Title: Izvestiia na Bulgarskoto entomologichno druzhestvo
- Source / key: `archive_izvestiianabul25192530bul` / `252fd568` (wave `cyrillic`), year 1924
- Admitted lines: 1454 on 35 pages; split {'train': 1454}
- Script classes of its lines: {'cyrillic': 1355, 'latin': 99} (majority `cyrillic`; greek_poly = polytonic Greek, greek_mono = monotonic, greek_latin_cs = Greek with Latin words, latin, cyrillic)
- Suspicion score 3.0 (rank 97 of 557): 1 aspect(s) with a feature beyond 2σ of same-class books + weighted hard flags 2; selected as non-discounted hard flag.

## Why it was flagged

Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):

- **A:other_script_residue** (weight 1) — 9 of 1454 lines carry other-script residue (by primary kind {'isolated_alnum': 3, 'isolated_standalone': 3, 'isolated_ref_letter': 2, 'isolated_standalone_lookalike': 1}; 4 not explained by a number-adjacent reference letter or a letter+digit token) (0.62%; same-class book p95 1.47%)
- **A:book_other_lang_gt2pct** (weight 1) — 2.82% of lines guessed as another language than bg {'ru': 29, 'it': 1, 'la': 3, 'de': 4, 'fr': 3, 'en': 1} > 2% (same-class book p95 10.08%)
- **D:page_line_count_outlier** (weight 0) — 0 page(s) above and 2 below the cyrillic page line-count p99/p1 — discount: wave p1/p99 page rule, ~1 % of pages per side by construction (D §9)

Aspect A features beyond 2σ vs same-class books (1): greek_share_mean z=+2.6 (value 0.0002)

Context: majority language `bg`, other-language share 0.0282; other-script residue lines 9 (unexplained 4); B line-flag counts {'digit_heavy': 50, 'punct_heavy': 3, 'all_caps': 1, 'long_token': 7, 'word_length_outlier': 8, 'bibliographic': 1, 'dictionary_like': 11}; C line-flag counts {'cpp_vs_book_out': 22, 'conf_min_low': 18, 'aspect_out': 10, 'cph_out_of_range': 16}; median confidence 0.971; two-column book False, column-crossing share 0.27.

## What to look at

1. `sheet.jpg`: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. lines 1-20 random admitted lines (number in black), 21-40 most anomalous (number in dark red; most line flags across A-D). Compare every label with the pixels above it.
2. `page.jpg`: one compiled page of this book (page `252fd568-p000161`): the scan on the left, Google's reading of every line drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) and whether the text really is in the language/script the labels say.
3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).

| # | sample | id | class | conf | flags | label |
|---:|---|---|---|---:|---|---|
| 1 | random | `252fd568-p000062-l0013` | cyrillic | 0.9703 | – | значителната си часть, бѣха унищожени, скакалецътъ въ по- |
| 2 | random | `252fd568-p000062-l0041` | cyrillic | 0.9426 | – | въ резултатъ отъ което сж се появили масово щитоносните |
| 3 | random | `252fd568-p000112-l0028` | cyrillic | 0.9824 | – | и съ тази фауна, обаче, това познание е толкова малко, щото |
| 4 | random | `252fd568-p000136-l0010` | cyrillic | 0.9821 | – | Съ това свое наблюдение той потвърдява наблюдннията на |
| 5 | random | `252fd568-p000136-l0042` | cyrillic | 0.9698 | – | сливитѣ въ държавния овощенъ разсадникъ при Павлово, въ |
| 6 | random | `252fd568-p000234-l0038` | cyrillic | 0.9575 | – | нитѣ форми на този бръмбаръ сж нападнали младитѣ чере- |
| 7 | random | `252fd568-p000281-l0021` | cyrillic | 0.9592 | – | нува подъ името „мрътвешка глава“. Това име пеперу- |
| 8 | random | `252fd568-p000281-l0034` | cyrillic | 0.9788 | – | рика и Мадагаскаръ) е свързанъ съ множество интересни био- |
| 9 | random | `252fd568-p000294-l0044` | cyrillic | 0.9744 | – | колѣние, както това личи отъ следното отглеждане. Една |
| 10 | random | `252fd568-p000316-l0047` | latin | 0.9883 | – | metridae 49, Syntomidae 1, Arctiidae 12, Zygaenidae |
| 11 | random | `252fd568-p000451-l0021` | cyrillic | 0.9875 | – | ната зимната пшеница, която е пострадала най-силно. Силно |
| 12 | random | `252fd568-p000451-l0048` | cyrillic | 0.9844 | – | по-слабо и 5. засилване растенията чрезъ добра обработка |
| 13 | random | `252fd568-p000463-l0033` | cyrillic | 0.9797 | – | перени крила (Spannweite) мѣри 23 мм; напречната кафяво- |
| 14 | random | `252fd568-p000476-l0050` | cyrillic | 0.972 | C:cph_out_of_range | не можахъ да |
| 15 | random | `252fd568-p000486-l0003` | latin | 0.9627 | A:script_share_outlier, B:digit_heavy | 90. Stauropus fagi L. (786) Само единъ екзем- |
| 16 | random | `252fd568-p000522-l0032` | cyrillic | 0.9791 | – | ревматизъмъ, безразлично хронически или остъръ (ставенъ), |
| 17 | random | `252fd568-p000548-l0022` | cyrillic | 0.9775 | – | Рила планина.. Периодическо списание. кн. 59, стр. |
| 18 | random | `252fd568-p000559-l0019` | cyrillic | 0.9557 | C:conf_min_low | пжтека, която води по дѣсния брѣгъ на рѣката, ся насадени |
| 19 | random | `252fd568-p000571-l0042` | cyrillic | 0.9584 | – | морско крайбрѣжие: при Бургасъ Чорбаджиевъ я е ловилъ |
| 20 | random | `252fd568-p000571-l0045` | cyrillic | 0.9587 | – | 1). Срѣщането. въ Евксиноградския паркъ на Argynnis aphi- |
| 21 | anomalous | `252fd568-p000500-l0038` | latin | 0.9718 | B:digit_heavy, D:column_crossing_line, D:column_merge_line | 264. Calimorpha quadripunctaria Poda. (4248) - |
| 22 | anomalous | `252fd568-p000438-l0013` | latin | 0.9511 | A:lang_ne_book, A:other_script_residue:isolated_standalone, C:cph_out_of_range | Dorcadion pedestre Poda И Dorcadion y |
| 23 | anomalous | `252fd568-p000062-l0046` | cyrillic | 0.9649 | A:homoglyph_word, A:script_share_outlier, C:cpp_vs_book_out | 4. Боровата процесионка (Thaumetopoea pi- |
| 24 | anomalous | `252fd568-p000365-l0009` | latin | 0.9818 | A:lang_ne_book, B:bibliographic, B:digit_heavy | the Balkans in 1925. The Entomologis Record Vol., 38, 1926. въ |
| 25 | anomalous | `252fd568-p000136-l0012` | latin | 0.9773 | A:lang_ne_book, A:script_share_outlier, B:digit_heavy | 4, Ha 15.XII 1915 г. реферира 2 статии въ Zoollogische- |
| 26 | anomalous | `252fd568-p000329-l0002` | cyrillic | 0.9777 | A:lang_ne_book, A:script_share_outlier, C:cpp_vs_book_out | у интерсексуалнитѣ Lymantria dispar. |
| 27 | anomalous | `252fd568-p000500-l0031` | cyrillic | 0.9526 | D:column_crossing_line, D:column_merge_line | ство екземпляри отъ Орловъ въ околноститѣ на града презъ |
| 28 | anomalous | `252fd568-p000161-l0038` | cyrillic | 0.9758 | D:column_crossing_line, D:column_merge_line | Финия, Русия, Кавказъ, Туркестанъ, Сибиръ и Китай (Пекинъ |
| 29 | anomalous | `252fd568-p000161-l0033` | latin | 0.9766 | D:column_crossing_line, D:column_merge_line | Plagiognatus albipennis Fall. Намѣренъ до сега въ |
| 30 | anomalous | `252fd568-p000161-l0037` | cyrillic | 0.9766 | D:column_crossing_line, D:column_merge_line | ция, Алжиръ, Италия, Швейцария, Унгария, Ромжния, Гърция, |
| 31 | anomalous | `252fd568-p000161-l0030` | cyrillic | 0.97 | D:column_crossing_line, D:column_merge_line | нитѣ Бунарджикъ и Джендемъ-тепе (Пловдивъ) презъ Май |
| 32 | anomalous | `252fd568-p000136-l0004` | cyrillic | 0.9653 | A:homoglyph_word, A:script_share_outlier | 2. Ha 7.VII 1925 реферира статията на Th. Dobshansky |
| 33 | anomalous | `252fd568-p000136-l0033` | cyrillic | 0.975 | A:homoglyph_word, A:script_share_outlier | Реферира за корояда Jps rectangulus Eichw, който е |
| 34 | anomalous | `252fd568-p000161-l0036` | cyrillic | 0.9715 | D:column_crossing_line, D:column_merge_line | Познатъ въ Британия, Швеция, Германия, Белгия, Фран- |
| 35 | anomalous | `252fd568-p000136-l0007` | cyrillic | 0.9523 | A:homoglyph_word, B:digit_heavy | 3. Ha 29.IX, 1925 съобщи за наблюдаваната отъ него хе- |
| 36 | anomalous | `252fd568-p000500-l0036` | cyrillic | 0.9662 | D:column_crossing_line, D:column_merge_line | Видѣхъ два еклемпляра въ сбирката на мяжката гимназия, |
| 37 | anomalous | `252fd568-p000426-l0006` | cyrillic | 0.9651 | A:homoglyph_word, B:digit_heavy | най-усилена деятелность отъ 1-10. VI. Ha 14. VIII. 1927 год. |
| 38 | anomalous | `252fd568-p000161-l0031` | cyrillic | 0.969 | D:column_crossing_line, D:column_merge_line | и Витоша (мѣстностьта Капакливецъ) презъ Юлий. |
| 39 | anomalous | `252fd568-p000500-l0039` | cyrillic | 0.9512 | D:column_crossing_line, D:column_merge_line | Единъ екземпляръ въ Преображенския манастиръ на 24.VII. |
| 40 | anomalous | `252fd568-p000161-l0034` | cyrillic | 0.9669 | D:column_crossing_line, D:column_merge_line | едно само находище: сухитѣ ридове при гара Бѣлово по пи- |

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
