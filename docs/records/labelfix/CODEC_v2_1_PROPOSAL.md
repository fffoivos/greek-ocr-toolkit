# Codec v2.1 proposal: one target per printed sign (elision apostrophe, numeral sign)

Status: proposal for the training track, 17 Oct 2026. It is a label-contract change and goes in its own arm in the wave after 1b, one variable. Codec v2 for wave 1b is frozen without it (coordinator).

Principle (owner rule): transcribe what is printed. Identical ink gets one target. Otherwise the recogniser learns which source or OCR engine produced the label, not what the page shows.

## Evidence: counts in `import_real_v2_train.jsonl`

Labels are NFD; counts are occurrences / rows.

| Codepoint | Name | Occurrences / rows | In v1 | In v2 (frozen) |
|---|---|---:|---|---|
| U+0027 ' | APOSTROPHE | 5,571 / 5,259 | yes | yes |
| U+1FBF ᾿ | GREEK PSILI (spacing) | 6,127 / 5,895 | no | added |
| U+1FBD ᾽ | GREEK KORONIS (spacing) | 4,027 / 3,877 | no | added |
| U+2019 ’ | RIGHT SINGLE QUOTATION MARK | 2 / 2 | yes | yes |
| U+02BC ʼ | MODIFIER LETTER APOSTROPHE | 0 | no | no |
| U+0384 ΄ | GREEK TONOS (spacing) | 2,499 / 2,325 | no | added |

The 2,325 tonos rows split by script class as greek_poly 1,517, greek_mono 749, greek_latin_cs 44 and latin 15. By wave: parliament 617, vouli 545, round1 511, round2 401, mixed 167, openarchives 84.

## Ink sample: what U+0384 is in print

**Method.** 40 seeded rows (seed 20261017) containing U+0384. One Opus reader viewed every line crop and classified all 44 occurrences. This is a single reader, so the result is indicative, not adjudicated. Raw answers are in `R0_evidence/tonos_ink_sample.jsonl`.

| Printed sign at the U+0384 position | Count |
|---|---:|
| Greek numeral sign (keraia) after a letter-numeral or digit: Β΄, γ΄, ΣΤ΄, 26΄ | **38** |
| Prime / minute (18.30΄, 2΄ λεπτά) | 2 |
| Elision apostrophe (καθ΄ ὕλην, line-final ν΄) | 2 |
| Opening double quote printed as two strokes (΄΄) | 2 |
| Accent detached from its vowel | **0** |

The glyph is acute-shaped in older polytonic prints and comma-shaped (like ’) in the sans-serif parliament and openarchives prints.

The reader noted three label errors along the way:
- stigma Ϛ printed where the label has Γ΄;
- α΄ printed where the label has χ΄;
- ' used for a keraia in a line whose other keraiai are ΄.

## Proposal

1. **Elision apostrophe: fold to one atom.** Word-final elision ' ᾿ ᾽ ’ ʼ becomes **U+2019 ’**.
   - **The word-final rule.** Fold only when the sign directly follows a Greek letter at the end of a word core: next character is a space, punctuation or end of line, and the preceding token is a Greek word. Examples: δ’, τ’, ἀλλ’, καθ’, μηδ’.
   - **What stays.**
     - A spacing ᾿/᾽ standing for a breathing or koronis on a following capital or vowel, as in ᾿Ο or a crasis coronis, stays as it is. Better still, it attaches as the combining mark when the print shows it on the letter.
     - ' or ’ used as a quotation mark (paired with an opening quote) stays a quote.
     - ' after a digit or Latin letter stays.
   - **The count to disclose** is about 15,700 occurrences across the four codepoints. The exact elision subset is computed with the rule above at build time, and the folded count goes in the release receipt.
2. **U+0384 standalone tonos: keep it, as the numeral sign (keraia).** It is NOT a detached-accent artefact: 0 of 44 were. Map by context:
   - after a Greek letter-numeral or digit → keep **U+0384** as the keraia atom. U+0374 GREEK NUMERAL SIGN would be the principled choice, but NFC turns it into U+02B9; keeping U+0384 avoids a normalisation trap.
   - in elision position by the rule above → **U+2019**.
   - in a time or measurement after digits (18.30΄) → keep U+0384. A prime atom is not worth a codec change for 2 / 44.
   - paired ΄΄ used as an opening quote → **“**.
3. **Spacing ᾿ / ᾽ before a capital** (Google's "breathing as apostrophe", seen on NLG in M2): not folded into ’. When the print shows the breathing on the capital, the label should carry it as a combining mark on that capital. This is a label correction (wave 1c / L1 territory), not a codec fold. Until corrected, it stays as it is.

## Arm design (one variable)

v2.1 = v2 atoms with labels rewritten by rules 1–2. The control is v2 with unchanged labels. Both arms use the same data, seeds and recipe.

Judge on:
- the locked R0 strata and the 666 for marks;
- apostrophe/elision accuracy against print truth from R0b's punctuation cards (227 apostrophe/quote disagreement cards + 208 S4 apostrophe candidates);
- keraia accuracy on numeral-bearing lines.

Report folded counts per wave in the release receipt.
