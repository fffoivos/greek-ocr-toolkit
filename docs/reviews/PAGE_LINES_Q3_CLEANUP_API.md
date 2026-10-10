# Q3 — cleanup, page API and documentation

Status: **NOT DONE**. The strict frozen-output gate has recorded failures;
the main ancestry merge and exhaustive constant naming also remain incomplete.

Q3 gathers the page pipeline into `greekocr.pages`, keeps the crop interfaces,
and adds one typed entry point for Python, the CLI and the Docling detector.
Historical report generators are preserved in an archive. The comparison runner
uses exact values and pixel hashes, with no float tolerance.

## Old → new module map

| Original path | Current implementation | Compatibility |
| --- | --- | --- |
| `greekocr/glyphs/pixel_segments.py` | `greekocr/pages/pixels.py` | Old module import aliases the implementation. |
| `greekocr/glyphs/page_text_lines.py` | `greekocr/pages/lines.py` | Old module import aliases the implementation. |
| `greekocr/glyphs/page_font.py` | `greekocr/pages/font.py` | Old module import aliases the implementation. |
| `greekocr/glyphs/boundary_evidence.py` | `greekocr/pages/boundaries.py` | Old module import aliases the implementation. |
| `greekocr/glyphs/line_structure.py` | `greekocr/pages/structure.py` | Old module import aliases the implementation. |
| `greekocr/glyphs/table_lines.py` | `greekocr/pages/tables.py` | Old module import aliases the implementation. |
| `greekocr/glyphs/statistics.py` | `greekocr/pages/statistics.py` | Old module import aliases the implementation. |

The aliases preserve classes, public functions and private imports used by
existing tests/review scripts. The new package owns `api.py` (orchestration),
`options.py`, `records.py`, `layout.py`, `outputs.py`, `render.py`, `delivery.py`,
`provenance.py` and `cli.py`. The existing crop fitter, including
`components.py`, has not been rewritten. The older box-guided `glyphs.page_lines`
API remains available for compatibility.

`render_page_line_segments.py` now calls the shared API; its rendering helper
comes from `pages.render`. `build_statistics.py` still measures frozen geometry
and uses a shared statistics reader. The output auditor and renderer now hash
the same implementation source set. Removed paths include the unused private
`_gaps(persistent=False)` branch, duplicate statistics-table reading and unreachable
labels on discounted lines after they have already been filtered out.
`_median_or_mean` was renamed `_mean` to describe its actual calculation.
Named geometric/sampling constants retain their exact prior values and state
units/reasons. This is not a retuning or a Q4 performance change. Some support-count,
percentile and plotting literals remain inline, so the requested exhaustive
constant naming is not complete.

## Script archive

The complete active/archive script inventory is
[`scripts/glyphs/README.md`](../../scripts/glyphs/README.md).
These historical scripts moved without deleting their algorithms:

| Old path | New path |
| --- | --- |
| `scripts/glyphs/annotate_tables_round4.py` | `scripts/glyphs/archive/annotate_tables_round4.py` |
| `scripts/glyphs/audit_orientation_guides.py` | `scripts/glyphs/archive/audit_orientation_guides.py` |
| `scripts/glyphs/audit_orientation_round4.py` | `scripts/glyphs/archive/audit_orientation_round4.py` |
| `scripts/glyphs/audit_tables_round4.py` | `scripts/glyphs/archive/audit_tables_round4.py` |
| `scripts/glyphs/check_tables_part2.py` | `scripts/glyphs/archive/check_tables_part2.py` |
| `scripts/glyphs/evaluate_orientation_guides.py` | `scripts/glyphs/archive/evaluate_orientation_guides.py` |
| `scripts/glyphs/evaluate_orientation_round4.py` | `scripts/glyphs/archive/evaluate_orientation_round4.py` |
| `scripts/glyphs/evaluate_tables_round4.py` | `scripts/glyphs/archive/evaluate_tables_round4.py` |
| `scripts/glyphs/generate_orientation_guides.py` | `scripts/glyphs/archive/generate_orientation_guides.py` |
| `scripts/glyphs/integrate_docling_tables_round4.py` | `scripts/glyphs/archive/integrate_docling_tables_round4.py` |
| `scripts/glyphs/integrate_orientation_round4.py` | `scripts/glyphs/archive/integrate_orientation_round4.py` |
| `scripts/glyphs/page_before_after.py` | `scripts/glyphs/archive/page_before_after.py` |
| `scripts/glyphs/page_segments_report.py` | `scripts/glyphs/archive/page_segments_report.py` |
| `scripts/glyphs/render_orientation_guides.py` | `scripts/glyphs/archive/render_orientation_guides.py` |
| `scripts/glyphs/render_orientation_round4.py` | `scripts/glyphs/archive/render_orientation_round4.py` |
| `scripts/glyphs/report_orientation_guides.py` | `scripts/glyphs/archive/report_orientation_guides.py` |
| `scripts/glyphs/report_orientation_round4.py` | `scripts/glyphs/archive/report_orientation_round4.py` |
| `scripts/glyphs/report_tables_round4.py` | `scripts/glyphs/archive/report_tables_round4.py` |
| `scripts/glyphs/review_line_boundaries.py` | `scripts/glyphs/archive/review_line_boundaries.py` |
| `scripts/glyphs/review_line_structure.py` | `scripts/glyphs/archive/review_line_structure.py` |
| `scripts/glyphs/review_page_lines_round3.py` | `scripts/glyphs/archive/review_page_lines_round3.py` |
| `scripts/glyphs/review_page_lines_round4_nontable.py` | `scripts/glyphs/archive/review_page_lines_round4_nontable.py` |
| `scripts/glyphs/review_statistics.py` | `scripts/glyphs/archive/review_statistics.py` |
| `scripts/glyphs/score_tables_round4.py` | `scripts/glyphs/archive/score_tables_round4.py` |
| `scripts/glyphs/summarize_page_line_review.py` | `scripts/glyphs/archive/summarize_page_line_review.py` |
| `scripts/glyphs/tessellate_three_lines.py` | `scripts/glyphs/archive/tessellate_three_lines.py` |
| `scripts/glyphs/time_orientation_guides.py` | `scripts/glyphs/archive/time_orientation_guides.py` |

Repository-root calculations, sibling imports, tests and committed Markdown
report commands were updated. Historical result JSON, image fixtures and owner
feedback were not rewritten. `scripts/glyphs/eval/book_pages.py` is preserved
byte-for-byte from local `main`.

## API and documentation

`process_page(image, *, options=PageOptions(), page_key=..., book_id=...,
table_regions=..., layout_provider=..., page_size=..., recognizer=...)` returns a
`PageResult`. Its pages/columns/blocks/rows are typed structure views; `lines`,
`pieces`, `delivery`, `glyphs`, `statistics`, and optional `orientation` expose
the remaining stages. `to_records()` supplies current geometry payloads.
`process_book` processes ordered images or aggregates previously measured page
results, then applies Q2's leave-one-page-out references.

Options cover table recovery, parked orientation, guarded joining with all three
granularities, statistics, keeping/dropping diagnostic lines and selected output
files/images. Dropping remaps the line-index spaces and retains stable address
IDs. Default calls do not write artifacts. The CLI is `greekocr pages DIRECTORY
--out OUTPUT`. The plugin maps its corresponding options through `page_options()`;
its recognizer, codec, routing and text-layer mode remain its own settings.
Q2 retains some invalid active ribbons as diagnostic data. Standalone calls
preserve them by default; `strict_geometry=True` rejects them before delivery.
Docling detector mode sets this flag to preserve its historical rejection rule.

Read [PAGES_GUIDE.md](../PAGES_GUIDE.md) first, then
[PAGES_PIPELINE.md](../PAGES_PIPELINE.md) and
[PAGES_OUTPUT_FORMAT.md](../PAGES_OUTPUT_FORMAT.md).
[API.md](../API.md) and [INVENTORY.md](../INVENTORY.md) are updated.

## Equality method

The reference implementation is commit `10eda96`, extracted by `git archive` into
an ignored local validation directory and loaded independently. The protected
crop implementations are identical to that commit. For each of the 54 development
and 41 book images, the runner executes default and table delivery, measures Q2
statistics, compares every line/structure/cell/segment/diagnostic JSON value,
compares glyph rows after Parquet serialization, compares every delivered crop's
pixels, and compares all three joining granularities including rejection outcomes.
No tolerance or rounding is added. The 16-way synthetic API option matrix also
executes statistics on/off and joining off/default/rows/pieces with tables on/off.
The separate 41-page book snapshot uses the order in `selection.json`, verified
against every saved book's `page_keys`. The combined 95-page snapshot uses
development filename order followed by book filename order within each book.
These orders are supplied as inputs to both implementations; output arrays are
never sorted to make a comparison pass. The order also matters for exact floating-point reductions.
Some page partitions run concurrently in foreground tool sessions. Their recorded
elapsed seconds describe validation work; they are not a controlled Q4 speed baseline.
The real-page comparisons explicitly pass `page_size=(image_width/3, image_height/3)`
to match Q2's research raster convention. The public API defaults to source-pixel
page units. Therefore an unconfigured call additionally changes `page_size` and
cell `box_page` coordinates; equality under the explicit legacy frame is not a
claim that the API defaults reproduce the research output envelope.

A separate structural check expands named constants and compares relocated stage
ASTs against Q2. It permits only import relocation, the `_mean` name change, and
removal of the unused private gap branch. All seven stages pass this check.
This complements the actual page runs; it is not presented as a substitute.

The frozen `.astra/out_after_Q2` files are also compared directly. They include
historical Q1/Q1b audit output and orientation-review links, not just a fresh Q2
detector run. Those differences count as strict gate failures. Reproducing the
live Q2 implementation alone does not satisfy the owner's stronger artifact gate.

## Results

The full suite passed **2,278 tests**, with **0 failures, 0 errors**, and
**16 skipped** out of 2,294 collected cases. The skips are the
existing web-render tests requiring a Chromium executable unavailable in this
sandbox. The owner set passed **40/40**, the curl set **9/9**, the orientation
families **155/155**, and the new API matrix/contracts **30/30**. These counts
come from `.astra/q3-final-tests.xml`; orientation is still opt-in.
After that run, one extra blank line at the end of `pages/render.py` was removed
to pass the patch whitespace check. Its Python AST is unchanged; the receipt
records both source hashes and this formatting-only change.

An actual offline Docling layout prediction on the navigation-table development
page returned two table regions. This exercises the cached model and image-only
adapter; it does not assert semantic table recognition accuracy.

| Comparison | Result |
| --- | --- |
| Development pages, default and tables | **54/54 exact** against fresh Q2 execution. |
| Book pages, default and tables | **41/41 exact** against fresh Q2 execution. |
| Page executions with statistics | **190/190 exact** JSON values and glyph Parquet rows. |
| Delivered recognition crops | **32,144/32,144 exact** pixel hashes, across both modes. |
| Q1 joining outcomes | **570/570 exact** records or refusal outcomes; this does not certify partial row envelopes. |
| Book aggregation | **168/168 exact** variants over 54 book identities. |
| Corpus aggregation | Both **95-page and 41-page** summaries exact. |
| Frozen line files and enriched glyph tables | **95/95 exact** for each. |
| Frozen book/corpus summaries | **54 combined-collection book files, 6 book-only files and both corpus files exact** with their original input orders. |
| Other compared frozen files | **244 differ**, containing **9,406 observed differences**. |
| Relocated stage ASTs | **7/7 equivalent** after the documented mechanical substitutions. |

The frozen failures are:

| File family | Files | Differences | Fields |
| --- | ---: | ---: | --- |
| `structure.json` | 54 | 8,728 | Historical `rows[].joinable`, rejected-boundary IDs/track/proposal IDs, accepted/fold/column proposal IDs, crossing row/piece/proposal links, and audit `provenance`. |
| `cells.json` | 95 | 203 | `page_units` descriptions on all pages; historical `orientation_mode` and `orientation_output` links on 54 development pages. Cell arrays themselves match. |
| `stats.json` | 95 | 475 | Historical `implementation_sha256`, `lines_file_sha256`, `seconds`, `source_image`, and `source_sha256` fields are absent from API measurements. Numeric measurements match. |

The machine-readable receipt is [PAGE_LINES_Q3_EQUALITY.json](PAGE_LINES_Q3_EQUALITY.json).
Every observed difference from these comparisons is in
[PAGE_LINES_Q3_DIFFERENCES.json.gz](PAGE_LINES_Q3_DIFFERENCES.json.gz), keyed by
comparison filename. Entries contain a JSON path and a `kind`: `value` records
both values, `length` records both array lengths, and `missing` uses `q2`/`api`
booleans to indicate field presence. No historical timing or source hashes have
been copied into new measurements to manufacture equality.

The full 95-page frozen review-image comparison, frozen checks/segments/partial-row
envelopes, and historical orientation receipts are **not certified** by this run.
The shared line/contact-sheet renderer produces identical JPEG bytes to the old
renderer on the synthetic check. That is narrower evidence than 95-page image
identity. Likewise, the plugin's old active-line-only delivery input differs from
the canonical page input; its 40 contract tests pass, but full 95-page plugin-output
identity has not been established. These limits remain open alongside the measured failures.

## Known joining compatibility gap

The archived Q1b writer saved partial `rows.json` files even when some rows
could not be joined. The API currently uses Q1's strict `delivery_records`
function: unsafe joining raises, and successful row files have `complete=true`
and an empty `blocked_rows` list. It does **not** reproduce these five partial
archived envelopes. This is an additional failed compatibility requirement,
not an exact-output success justified by matching exception messages.

| Frozen page | Blocked rows in its existing rows file |
| --- | ---: |
| `an-7a2b17a3fb0f-p000200` | 25 |
| `s2-200e977f2dab5291c42c-p00035` | 30 |
| `s2-6419488b7f8e69fd20da-p00001` | 15 |
| `an-d3237d690aa0-p000138` | 2 |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 55 |

These are **127 blocked rows across five of the 54 development row files**.
The 41 book snapshots have no historical `rows.json` files. Restoring the
partial-row serialization contract and reconciling historical audit/provenance
fields are required before rerunning the strict gate.

## Main integration and commit

Local `main` is `fc195f2`; its two incoming commits contain the orientation research
archive and `eval/book_pages.py`. All 20 incoming files are present and verified
byte-identical to main, with matching executable modes. The histories have no overlapping changed paths.

`git merge --no-edit main` failed before writing ancestry:

```
fatal: update_ref failed for ref 'ORIG_HEAD': cannot lock ref 'ORIG_HEAD':
Unable to create .../.git/worktrees/greek-ocr-toolkit-astra-lines4/ORIG_HEAD.lock:
Operation not permitted
```

This is a sandbox filesystem refusal. Materialising main's files is not a merge.
A subsequent `git commit --dry-run` failed creating the same worktree's
`index.lock` with `Operation not permitted`. Main is not currently an ancestor of
this branch and must not be reported as fast-forwardable to it.

The handoff is `.astra/Q3-cleanup-api.patch` and `.astra/commit-Q3.sh`, with the
required commit trailers and a file-hash manifest. The patch is checked in reverse
against the working tree and applied forward to a temporary reconstruction of
the Q2 files; every resulting file hash is verified. The script's shell syntax is
checked. It binds the current branch, HEAD and main, records Q3, then merges main.
Whitespace checks accept CRLF endings in main's historical CSV files while still
rejecting actual trailing whitespace; the CSV bytes are preserved.
It deliberately exits nonzero after a successful handoff because Q3 remains
**NOT DONE**, so the queue cannot advance to Q4 on this failed gate.
