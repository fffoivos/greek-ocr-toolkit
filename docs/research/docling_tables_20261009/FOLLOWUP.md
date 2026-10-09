# Follow-up from the owner: two separate questions

The owner points out that there are two different requirements, and the report must answer each one separately:

> "there is a difference between what the layout model needs to classify it as a table, and then there is what the
> tables-model needs to create the table"

## A. What the layout model needs, so that the region is classified as a table

- Does Docling's layout model (the heron layout model in 2.135) decide "Table" from the page image alone? Or do our
  OCR cells influence the decision: through cluster post-processing, cell assignment, orphan-cell handling,
  confidence thresholds, or merging and splitting of clusters?
- Can our cells cause a table region to be lost, shrunk, split, or relabelled (text, list, picture)? For example:
  - cells that cross the table's border;
  - cells fused across the table and the text beside it;
  - no cells in part of the table, as on s2-831443dc5e6f1ccfbaf5-p00020, where our detector misses the first two
    columns;
  - faint or discounted ink.
- Measure it. Run the layout stage on the three table pages with the same cell variants (a), (b), (c), plus "no cells
  in part of the table". Report the table clusters found (count, boxes, confidence) under each variant. If layout
  does not depend on the cells, show that from the code and with the numbers.

## B. What the table-structure model needs, so that it builds the table correctly

This is what your report already covers: TableFormer, cell matching, granularity, fused and crossing cells,
coordinates and fields. Keep it as its own section.

Then add to `REPORT.md`:
- a separate section for A, and a separate section for B;
- in the plain-words answer at the top, one sentence for each;
- if A and B ask different things of our cells, say exactly where they conflict and what we should deliver to satisfy
  both.

End with the same last-line format: `RESULT: <ANSWERED|PARTIAL> <one line>`
