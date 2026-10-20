# OS5: add a "What moved in R2a" group to the failure-modes sheet (gpt-6.1-sol, medium, network OFF; no .git writes)

Builder: `scripts/review/build_owner_sheets_v2.py` and spec `docs/records/owner_sheets/failure_modes_per_class/spec.json` (OS2–OS4). Keep every
existing doc id and card unchanged. ADD one group at the end, "What moved in R2a (not adopted)", with 5 cards:

| Seed | Line / slot | Truth tuple | BASE → R2a |
|---|---|---|---|
| 16 | 384c3f89-p000053-l0021:s8 | [0,0,0,0] | [0,0,0,0] → [0,0,0,1] |
| 17 | 177b717d-p000054-l0004:s4 | [1,3,0,0] | [1,3,0,0] → [1,3,0,1] |
| 17 | 177b717d-p000017-l0012:s24 | [0,3,0,0] | [0,3,0,0] → [0,3,1,0] |
| 18 | 22fda82b-p000063-l0039:s10 | [0,3,0,1] | [0,3,0,1] → [0,3,0,0] |
| 18 | 602cc72e-p000167-l0027:s10 (owner witness) | [0,2,0,0] | [0,2,0,0] → [1,2,0,0] |

Source of record: `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/evidence/r2a/r2rb2_paired_slots.json` and
`r2rb2_owner_regressions.json`. Verify the tuples there. The tuple order is (breathing, accent, dialytika, subscript), with indexes as in
`HEADS` (r1_common).

**Each card:** the full line crop with our detections, as in the R1 held-out sheets.
- Find the crop and slot geometry the way `R2_evidence/page_builders/build_r1a_errors.py` did for these held-out lines; read-only from the
  r1 / r2-prep worktrees.
- Highlight the slot letter.

**Rows:** Google, plus "Before" (BASE) and "After (R2a, seed N)" as words with the slot's marks applied. Printed is prefilled with the
truth word.

**Tags:** seed; the change ("subscript invented", "dialytika invented", "subscript dropped", "breathing added"); "owner witness" on the
last card.

**Doc id:** `{line_id}:s{slot}`, the same convention as the reader-errors sheet, so any existing owner note on that slot carries over.

No model names: say "before" and "after". Re-render `artifacts/owner_sheets/v2/failure_modes_per_class.html`, update its sha in
`docs/records/owner_sheets/v2_html_sha256.txt`, and add an OS5 section to OS2_REPORT.md. Tests pass.

Last line: `OS5 READY: group added 5 cards; existing doc ids identical yes; tests <n> passed; html sha <12>`.
