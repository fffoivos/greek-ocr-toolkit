# Historical sheet builders

These are the unchanged scratch builders and assets that produced the sheets
listed in [the design decision](../../../B_training_data/d_review/HUMAN_REVIEW_SHEETS.md), moved here from
`docs/records/review/reference/` for provenance and behaviour comparisons.

The implementation is now `greekocr.adjudicate.owner_sheet` and its packaged
CSS/JS. New sheets call `render(cards, spec)` directly, supplying saved SVG
overlays, tool verdicts and versions; they do not post-process the HTML or
replace the packaged assets. See [the package README](../../../../greekocr/adjudicate/README.md).

The archived builders retain their original absolute checkout assumptions and
HTML post-processing. They are historical references, not supported entrypoints.
`scripts/review/build_sheet1_demos.py` shows the current rendering API on the
same saved gate evidence and on RU1 correction records, without publishing.
