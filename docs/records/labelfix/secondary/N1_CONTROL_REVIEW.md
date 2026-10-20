# N1 control review (lead pixel check, 17 Oct 2026)

**Sheets reviewed.** `n1cb_controls_01..08.png` and `n1cb_c1_reference.png` from N1-Cb. Cell → slot mapping is in the scratchpad
`n1_ctrl_sheets/sheets_index.json`. Every cell was read on its zoom plus the whole-line image.

## Approved controls (truth meaning)

| Truth | Cells | n |
|---|---|---:|
| baseline dot | 1–12, 14, 15, 18–24 | 21 |
| comma | 25–47 | 23 |
| hyphen or dash | 49, 50, 51, 53, 54, 56–70, 73, 75, 76, 77, 78, 80, 81 | 27 |
| nothing | 84, 87, 89, 90, 91, 92, 94 | 7 |
| **raised dot** | **C1 reference cells 1–4**: `elstat--ee37bc488988f1bd--s000-l0445` (4·547·331, both gaps) and `elstat--ee37bc488988f1bd--s000-l0457` (4·479·781, both gaps). All four are mid-height dots that Google wrote as `-`. | 4 |

**Total approved: 82.**
- **C1 raised-dot slots.** They are C1 lines, already outside both N1 frames and outside the reserved documents (the reserved C1 card
  `…c5f7…l0367` stays excluded). Using them as controls is a lead ruling: they are the only verified raised dots outside the frames.
- **Cells 77 and 58** are spaced hyphens (`86 - 87`, `254 - 255`). Their truth is "hyphen or dash", because a mark is printed.

## Rejected (not controls)

| Cells | Reason |
|---|---|
| 13, 17 | The mark could be a comma (tail ambiguous). |
| 16 | A stray dot above the left digit could be read as a raised dot. |
| 48 | Noise or handwriting. |
| 52 | Google `-`, but the ink shows a baseline dot under a dotted leader. Good fault evidence, ambiguous as a control. |
| 55 | A heavy mark that could be a dot or a short hyphen. |
| 71, 74 | The left character is not a clear digit, or blurred. |
| 72 | Google `-`; the ink is a mid-height dot. In context (`67·12.5.1986`, "Με την … πράξη") it is probably a broken slash, so it is ambiguous. |
| 79, 82 | Handwriting. |
| 83, 85, 86, 88, 93 | The zoom shows two or more gaps and has no marker, so the target gap is ambiguous; or spacing sits between space and nothing. |

## Findings that change the next build

1. **The zoom needs the gap marker.** Its padding shows neighbouring digits, so in `707` or `.314` a reader cannot tell which gap is
   asked. The zoom must carry the same grey triangles as the line image, in added margins.
2. **Raised-dot positives are scarce.** No raised dot came from the planned pools: the "inner hyphen" pool was all true hyphens apart
   from cell 72. More raised-dot candidates will be drawn from `w1_elstat_separator_ambiguous_ids.txt` rows outside the step1 and
   reserved documents.
3. **"Space" vs "nothing" is weakly defined** for tabular figures. "Nothing" controls are kept only where the digits plainly touch.
   Bed answers of space/nothing are not used for any edit (N1 edits only `-`/`.` → `·`), so this ambiguity cannot cause a false edit.
