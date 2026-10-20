# SEG-CELLS-1b — visual observations

The directory now has **250 byte-exact PNGs**: 150 cells, 50 numeric-not-small,
and the original 50 small-non-numeric samples. The saved seeded orders were
preserved; no replacements were needed. The 200 new crops came from 156
hash-verified local cached pages through the unchanged native reconstruction
function. The other 50 PNGs retain their original SCP provenance.

I opened **40 of the 150 cells individually with the image tool**, at native
resolution. Ten difficult examples were also viewed at 6× nearest-neighbour
display scale in [visual_zoom_1b.png](visual_zoom_1b.png). The complete IDs,
sample hashes, selection and individual observations are in
[visual_review_1b.json](visual_review_1b.json). The selection deliberately covers
different sources, typography and awkward shapes; it does not estimate their
frequency. No source page was visually reviewed, so functional labels below
remain appearance-based.

The reviewed crops include isolated page-number-like `420` and `78`, compact
table/amount-like groups (`1.545.926`, `143.135,01`, `11.438.953`), a date-shaped
`30.5.87.`, and year-like `1961-` and `1936.`. Some are ranges or references
(`183-191`, `232, 19.`); another holds three separated decimal groups on a single
baseline (`1,0 1,2 0,30`). The cell population is visually broader than one
isolated number per table box.

Parenthesized `(7)` and `(5)` look like short reference/list/footnote-style marks,
but their actual role cannot be established from the crop. `III` and `XI.` are
Roman-numeral-like. The lexical `Mi` example is a sideways, edge-cut multi-stroke
shape; I cannot certify a clean Roman numeral from its pixels.

Ink quality varies markedly. Cell 1 is dark-on-dark with little contrast, cell 8
has faint thin strokes, and cell 18 has disconnected digit pieces. In cell 39,
heavy ink fills counters and merges strokes. Several gazette crops are sideways
or diagonal; orientation has been preserved in the sample PNGs.

Selected witnesses below use the 1-based cell order in `samples.jsonl` and the
review manifest. OCR strings are the unchanged census strings, not corrected
transcriptions.

| Cell | Saved OCR | Observation |
| --- | --- | --- |
| 1 | `4.-` | Very low contrast against grey paper; punctuation is hard to separate from background. |
| 12, 61 | `420`, `78` | Isolated serif numbers, page-number-like in appearance. |
| 18 | `92` | Tiny, broken-looking digit shapes with detached pieces. |
| 39 | `1,036,678` | Heavy merged ink makes individual digit interiors difficult to resolve. |
| 43, 69 | `7571`, `920` | Narrow sideways strips with extra edge-cut strokes. They may contain fragments of longer numbers or neighbouring content; the full extent is unresolved. |
| 48, 146 | `(7)`, `(5)` | Parenthesized markers; footnote versus list/clause function remains unresolved. |
| 105 | `1` | Broken upright stroke with a detached mark at the right edge. |
| 110 | `11` | Raster shows two stacked horizontal strokes, rather than two upright ones. |
| 125 | `30.5.87.` | Clearly date-shaped, with a trailing stop. |
| 130 | `3 500 000` | Low-height amount with a tiny clipped mark at the far left. |
| 131 | `4.267.49%` | Main number looks like `4.267.482`; a band of clipped glyph tops is visible underneath. |

These are observations from 40 crops, not owner labels, independent gold,
segmentation decisions, or proposed rules. They do not change classifier limits,
OCR text, or any historical verdict. Byte-exact reconstruction establishes the
sample's identity; it does not establish OCR or segmentation correctness.
