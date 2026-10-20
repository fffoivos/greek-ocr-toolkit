# RU1 lead review: shape comparison against same-book ъ/ь references (17 Oct 2026 16:39)

**Sheets.** `scratchpad/ru1_review/lead/review_00{1,2,3}.png` and `audit_00{1..4}.png`. Cell ↔ position mapping is in
`sheets_index.json` (RU1-L). Each cell was judged by shape: does the final glyph carry the left flag at the stem top, matching the
book's ъ reference, or not, matching its ь reference.

## Review set: 27 lead_review positions

| Ruling | Cells | n |
|---|---|---:|
| ъ (flag present) | 1–8, 10–16, 18–22, 24–26 | 23 |
| ь (no flag) | 23 (служить) | 1 |
| **ѣ (yat)** printed, Google wrote ь | 17 (верстѣ), 27 (Королѣ) | 2 |
| uncertain → HOLD | 9 (лучь: faint serif, cannot decide) | 1 |

- **Prior disagreements.** In 21 of the 27, both readers said ъ while the prior said ь_only. The ink agrees with the readers in every
  one I judged. The prior is built from Google's own labels, so it carries Google's ъ → ь flattening. **It is withdrawn as a review
  trigger.**
- **Reader disagreements.** Of the 4:
  - the ink says ъ in 2 (cell 22 оставитъ, cell 24 носитъ);
  - ь in 1 (cell 23 служить);
  - 1 is uncertain (cell 9 лучь).

## Audit set: seeded sample, not reviewed before

- **edit_hard: 30/30 confirmed ъ.** The 95% upper bound on the false-edit rate is about 10% (rule of three).
- **keep_soft: 10/10 confirmed ь.**

## New finding: RU2, the yat

Google also writes printed **ѣ** as ь (word-final locative: верстѣ, Королѣ). This is out of RU1's one-directional ь → ъ scope. Both
rows are HOLD in RU1, and the class goes into the plan as RU2, to be measured later.
