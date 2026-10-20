# N1-T lead check of raised-dot cells (17 Oct 18:36)

**Sheets.** `scratchpad/n1_review/t_lead/raised_01..03.png`. Each cell was judged against the approved raised and baseline references
shown on the same sheet.

| Ruling | Raised cells | n |
|---|---|---:|
| raised dot | 3–17, 18 (Ἰπ. 8, 4· citation), 19 (143·117), 22 (Serbian 63·90) | 18 |
| baseline dot | 20 (lekythos 8.30), 21 (Serbian 257.468) | 2 |
| nothing | 23, 24 (",12" / ",132": target gap between digits) | 2 |
| hold (too faint) | 1 (14·?), 2 (1929…) | 2 |

**Findings.**
- **Agreement holds.** Every slot where both reads agreed on a raised dot in valid contexts is a true raised dot: 12/12.
- **The false raised dots all come from single reads** (cells 20, 21, 23, 24: an r2 call against r1 or against a VOID context). The
  two-read rule caught every one.
- **Edit-rule refinement (lead).** Where the lead has verified a raised dot, the label takes U+00B7 even outside a
  grammar-thousands slot (cells 18, 22), because the label transcribes what is printed. The grammar gate still applies to
  unverified two-read decisions.
- **Data fault for the sourcing lead.** Cell 20's crop (`lekythos--dcfa99599048d352--s000-l0144`) is mirrored left to right.

The review cells (120 of the 650 lead_review slots) are NOT yet ruled. They stay unresolved and keep Google's character in "Ours".

**Update 18:37.** The sourcing lead took the mirrored crop (brief MIR1 on sol/recut-v1 is checking the cause, possibly verso
show-through, and the scope). Until MIR1 reports, `lekythos--dcfa99599048d352--s000-l0144` is **suspect in N1**: excluded from every
N1 decision and label edit, shown on the owner page with the tag `suspect:mirrored`.

**Update 18:44, MIR1 (sourcing lead).** The row is verso show-through, not a flipped raster: it is the last page of the issue,
and the crop holds only the reversed layer. The row is **excluded from N1 scoring and edits** (tag `excluded:show_through`). Any
further mirrored ids go to the sourcing lead.
