# N1-W1 lead pixel check, agreed raised dots (18 Oct 01:58)

**Sheets.** `scratchpad/n1_review/n1w1/sheets/raised_01..04.png`: the 22 agreed raised-dot cells from the first pass (13 valid
contexts). Each cell was judged against the approved raised references (dot centre at about 53% of digit height) and the baseline
references (dot on the baseline).

**Result: 22/22 confirmed raised dot** (cells 01–22, all ELSTAT `ee37bc488988f1bd`).
- In every cell the dot centre sits clearly above the baseline, at 55–73% of digit height.
- Cells 07 (5·936·566), 09 (13·169), 13 (359·822), 14 (427·869) and 16 (1·165) sit lower than the references, but far above the
  baseline. They are the same face's raised dots: none rests on the baseline.

**Ruling.** These 22 slots get `pixel_checked: true` with printed = the Google line with that slot changed to U+00B7. Raised dots
from the replacement reads (r3/r4) get their own lead check before `--apply-lead`.

## Replacement-read cells (18 Oct 02:33)

**Sheets.** `scratchpad/n1_review/n1w1/sheets2/raised_01..07.png`: 41 new agreed raised cells. **41/41 are confirmed raised dots.**
In every cell the dot centre is clearly above the baseline (55–73% of digit height), the same face as the first 22. Cell 01 is a
second ELSTAT document (`daec83cb9a364cd1`).

**Total: 63/63 agreed raised dots confirmed.**
