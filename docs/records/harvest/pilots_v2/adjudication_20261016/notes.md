# Blind pixel adjudication: alignment pilot (P1), 3 sources × 40 cards

Inputs: `docs/records/harvest/pilots_v2/blind_sheets/{wikisource,gutenberg,perseus}/sheet.html` and the native line crops they reference (`../../bulk/crops/*.png`). Each card was judged against its native crop, with 2–4× zooms where diacritics or line ends were in doubt. Accepted/rejected status was never consulted; no ledgers or keys were opened.
Per-card results: `adjudication.jsonl` (120 rows).

## Counts

| source | y | n | u | none | hyphen_or_linebreak | partial_span | markup_artifact | transcription_error | orthography_normalised | wrong_line | illegible |
|---|---|---|---|---|---|---|---|---|---|---|---|
| wikisource | 22 | 18 | 0 | 22 | 8 | 4 | 1 | 4 | 1 | 0 | 0 |
| gutenberg  | 26 | 14 | 0 | 26 | 10 | 3 | 0 | 1 | 0 | 0 | 0 |
| perseus    | 12 | 28 | 0 | 12 | 6 | 7 | 15 | 0 | 0 | 0 | 0 |
| **total**  | 60 | 60 | 0 | 60 | 24 | 14 | 16 | 5 | 1 | 0 | 0 |

Confidence: wikisource 31 high / 8 medium / 1 low; gutenberg 37 high / 3 medium; perseus 37 high / 3 medium.
No card was illegible at native resolution. No card was a whole wrong line: every mismatch is at the edge of the line or inside a single word.

## Rules applied
- A missing line-end hyphen, or a missing line-end elision apostrophe (ὑπ’ / καθ’), counts as `hyphen_or_linebreak`.
- Margin line numbers (Perseus/Herodian edition) are visible ink inside the crop. I counted them as missing text (`n`). Where they are the only problem (P12, P13, P31) the kind is `partial_span` at medium confidence. **If the pipeline is meant to ignore margin numerals, those 3 cards become `y`.**
- When a card has several defects, the most serious one sets the kind and the others are listed in the notes.
- Typographic spaces before `;` `!` `;)` in the print were ignored.

## Systematic findings
1. **Every source drops line-end hyphens (24 of 60 mismatches).** This happens in all three sources: Wikisource 8, Gutenberg 10, Perseus 6. The ink line ends `στρα-`, `pro-`, `κτω-` and the text ends `στρα`, `pro`, `κτω`. Two Wikisource cards keep their hyphen (W02 `ὑπογεγραμ-`, W25 `πρό-`), so the drop is not universal. Line-end elision apostrophes go the same way (W13 `ὑπ’`→`ὑπ`, G04 `καθ’`→`καθ`).
2. **Perseus: the ου-ligature `ȣ` is corrupted to `ἑ??ʼ` (13 cards, plus Ῥαȣέννης and Ἀδȣέντον).** The edition prints Latin "v" names with the ου-ligature: Σεȣῆρος, Ῥαȣέννης, Ἀδȣέντον. Every such text has `Σἑ??ʼήρου`, which adds a rough breathing that is not in the ink plus literal `??`. Any Perseus line containing Severus, Ravenna or Adventus is unusable as written. This one defect accounts for over half of all Perseus mismatches.
3. **Perseus: the text drops the first word or word fragment of the line (P02, P04, P06, P14).** Examples: `ελθεῖν`, `τος`, `λευσε,`, `κρῖνος`. The fragment is the tail of a word hyphenated on the previous line, so the alignment boundary is off by one token at the start of the line.
4. **Perseus: margin line numbers are in the crop but never in the text** (12 of 40 cards: 5, 2/15, 30, 4, 10/7, 2, 6, 10, 15, 4, 8, 10/2). When the numeral is stripped, the text often keeps a leading space (P13, P22, P26).
5. **Perseus writes `:` for the printed ano teleia `·`** (P06, P15), and once writes a combining psili (U+0313) where the ink has an apostrophe (P17 `ἐφ̓`).
6. **Wikisource: dialogue dashes at the start of a line are dropped** (W03, W05, W31). The text keeps a leading space where the `—` was. W17 likewise loses the leading `Π`.
7. **Wikisource: the transcription "corrects" the print in display headings and accents.** Examples: ΜΕΛΕΤΟΠΟΛΟΣ→ΜΕΛΕΤΟΠΟΥΛΟΣ (W06), ΧΑΡΑΛΑΜΠΗΣ→ΧΑΡΑΛΑΜΠΑΚΗΣ (W10), grave→acute before a full stop (W29), and one dropped adscript ι (W34). One card has a template-like duplication (W37 `ἐδύναντο ἐδύ-`).
8. **Gutenberg: the text is faithful to the print, including its quirks** (G08 copies the misprint `ἔνθουσιασμὸν`). Its errors are dropped hyphens and dropped opening/closing quotation marks at line edges (G37, G40). G31 loses both edge glyphs, a leading curly beta `ϐ` and a trailing `ου`.
9. **Crop geometry:** W15 and W26 (degraded 22fda82b scan) include fragments of the lines above and below. G21 ends tight on `Νο`, so a hyphen may sit outside the crop. Every crop contained its full target line.

## Ten most instructive cards
1. **perseus 16 / 24 / 37**: the `ȣ`→`ἑ??ʼ` corruption is clear-cut and repeats across the book. It is the single biggest Perseus defect and needs a fix at source.
2. **perseus 20**: `Ἀδ̔??ʼέντον` shows the corruption is the ligature, not the name Severus. It also hits Adventus and Ravenna (P08).
3. **perseus 14**: the text drops the first word `κρῖνος`. This is a start-of-line alignment offset, not an encoding fault.
4. **perseus 12**: the words match perfectly, and only the margin numerals `2`/`15` differ. This tests the policy on margin apparatus.
5. **wikisource 06**: at 4× the ink has no Υ, so ΜΕΛΕΤΟΠΟΥΛΟΣ is a correction made by the human transcriber. A proofread source can still disagree with the pixels.
6. **wikisource 10**: ΧΑΡΑΛΑΜΠΗΣ vs ΧΑΡΑΛΑΜΠΑΚΗΣ, two extra letters in a heading. Same lesson as W06.
7. **wikisource 37**: the text has a word that is not on the line (`ἐδύναντο ἐδύ-`), probably an expanded hyphenation template.
8. **wikisource 29**: grave vs acute (`ζαντιακὴν.`/`ζαντιακήν.`). A one-accent difference that a CER-level gate would miss.
9. **gutenberg 17**: `μυρί’` in ink vs `μυρἴ` in text, where an elision apostrophe has been recoded as a breathing on the iota. A subtle polytonic mislabel.
10. **gutenberg 31**: both edge glyphs dropped (`ϐ…ου`). Shows that edge loss also hits the Gutenberg text.

## Bottom line
Restoring line-end hyphens/apostrophes (24 cards) and the dropped edge dashes/quotes (5 cards) would turn 29 of the 60 `n` cards into `y`; a margin-numeral policy would decide 3 more. Repairing `ȣ` would fix most of the rest of Perseus. The remaining true text disagreements are few: Wikisource W06, W10, W26, W29, W34, W37; Gutenberg G17.
