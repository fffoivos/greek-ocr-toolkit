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
[`scripts/glyphs/README.md`](../../../scripts/glyphs/README.md).
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

Read [PAGES_GUIDE.md](../../A_ocr_development/reference/PAGES_GUIDE.md) first, then
[PAGES_PIPELINE.md](../../A_ocr_development/reference/PAGES_PIPELINE.md) and
[PAGES_OUTPUT_FORMAT.md](../../A_ocr_development/reference/PAGES_OUTPUT_FORMAT.md).
[API.md](../../API.md) and [INVENTORY.md](../../INVENTORY.md) are updated.

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


## Q3b

Q3b restores the Q1b partial-joining contract without changing fitted geometry,
crops or descriptive statistics. Q3 is committed as `bb06ee4`; the branch now
contains main through merge `e123b9b`. The earlier Q3 status above is historical.

### Restored contract

`process_page(..., options=PageOptions(join_lines=True, granularity="rows"))`
returns and writes the safe joined rows even when other rows are unsafe.
`rows.json` retains `schema_version`, `rows`, `blocked_rows`, `complete` and
`geometry_policy`. Every refusal has the original `row_id`, `line_indices`,
`table_id`, reason and crossing evidence. `complete` is false whenever any row
is blocked. `PageResult.blocked_rows`, `PageResult.complete` and `PageResult.joining`
also expose the audit in memory; the CLI reports refusals and writes the row
envelope by default at rows granularity.

The strict one-row `join_pieces` guard is unchanged: it rejects mixed page/column/
block/row addresses, duplicate piece ordinals, inconsistent overlap and boundary
crossings. The page-level joining stage catches those refusals and continues.
All active structure rows keep `joinable`; accepted boundary, fold and column
proposal links use Q1b's names, and crossings keep row, piece and proposal links.
`default` still delivers ordinary rows and separate table pieces; `pieces` keeps
all individual pieces. Both expose the whole-row safety audit and its refusals.
Joining off keeps the unaudited Q2 structure, as in the frozen book files.

Source pixels remain the public default page units: arbitrary rasters do not
imply a DPI. The documented legacy option is
`page_size=(image.width / 3, image.height / 3)`. Every equality call uses it;
`page_size` and `box_page` remain strictly compared numeric fields.

### Allowlist

These are exact paths within the named file family. `[]` matches an array index.
Only the named audit `provenance` object exempts descendants. There is no blanket
ID, timestamp, unit, evidence or numeric-field filter.

| File family | Field | Reason |
| --- | --- | --- |
| `stats.json` | `$.implementation_sha256` | The implementation identity changes with the source revision. |
| `stats.json` | `$.lines_file_sha256` | The serialized input file hash changes with JSON formatting. |
| `stats.json` | `$.source_image` | The input path belongs to the run, not the measured page. |
| `stats.json` | `$.source_sha256` | The input-file identity is recorded separately in the gate manifest. |
| `stats.json` | `$.seconds` | Elapsed wall time is not deterministic page behaviour. |
| `stats.json` | `$.units` | This is a human-readable unit description; numeric coordinates remain exact. |
| `checks.json` | `$.implementation_sha256` | The implementation identity changes with the source revision. |
| `checks.json` | `$.source_sha256` | The input-file identity is recorded separately in the gate manifest. |
| `checks.json` | `$.seconds` | Elapsed wall time is not deterministic page behaviour. |
| `cells.json` | `$.page_units` | This is a human-readable frame description; page_size and box_page remain exact. |
| `cells.json` | `$.orientation_mode` | This labels a separately generated historical orientation review. |
| `cells.json` | `$.orientation_output` | This links a separately generated historical orientation review. |
| `structure.json` | `$.units` | This is a human-readable unit description; all geometry remains exact. |
| `structure.json` | `$.provenance` | This is the historical audit input-hash receipt, not boundary evidence. |
| `structure.json` | `$.rejected_boundaries[].id` | An internal name of a rejected candidate is not an accepted boundary. |
| `structure.json` | `$.rejected_boundaries[].proposal_id` | An internal proposal name of a rejected candidate is not a delivered link. |
| `structure.json` | `$.rejected_boundaries[].track_id` | An internal track name of a rejected candidate is not an accepted track. |

Accepted IDs and links, rejected-candidate geometry/reasons/evidence, row
joinability, blocked-row records and every numeric measurement remain in the
comparison. See [the format contract](../../A_ocr_development/reference/PAGES_OUTPUT_FORMAT.md#strict-equality-and-the-metadata-allowlist-q3b).

### Equality method

`check_q3b_equality.py` calls the public API 16 times per page: tables on/off ×
statistics on/off × joining off/default/rows/pieces. Deterministic stages cache
only their complete serialized inputs within that page and return independent
copies. All cache misses execute current code; no frozen artifact or earlier
run supplies a detector, delivery or statistics result. Committed Q2 stages are
loaded separately from `git archive 10eda96` and rerun. An independent Q1b audit
uses that reference's strict row guard; the 54 frozen Q1b row/structure payloads
are additionally compared directly. The frozen development stage uses tables
and joining at rows granularity; frozen books use both switches off.

The comparison preserves JSON types, exact floats (including signed zero),
array order, Parquet rows/schema and crop dimensions/pixels. It checks segments
and detector diagnostics as well as lines, structures, cells, delivery and
statistics. Book aggregation preserves the original input orders: development
filenames followed by book filenames for the combined collection, and selection
manifest order for the separate book-only snapshot. Orientation stays parked;
its existing tests remain in the passing full suite.

### Equality table

**Q3b is NOT DONE:** the partial-joining contract and its frozen artifacts are
restored, but 95 historical `checks.json` files still differ in 215 fields outside
the approved allowlist. The gate exits nonzero and retains every difference.

| Comparison | Result |
| --- | --- |
| Development pages, all 16 API combinations | **54/54 exact** against fresh Q2 stages plus the Q1b joining audit. |
| Book pages, all 16 API combinations | **41/41 exact** against fresh Q2 stages plus the Q1b joining audit. |
| Public page API calls | **1,520/1,520 exact** lines, structure, cells, segments, detector diagnostics, delivery, joining and statistics. |
| Delivered recognition crops, both table modes | **32,144/32,144 pixel-exact**, including dimensions. |
| Raw glyph Parquet outputs | **190/190 exact** schemas and rows. |
| Joining outcomes | **570/570 exact** table-mode/granularity outcomes, each verified with statistics off and on. |
| Frozen lines, structures, cells and segments | **95/95 exact outside the allowlist for each family**. Accepted links and all numeric geometry match. |
| Frozen Q1b row envelopes | **54/54 exact**, including **5/5 partial envelopes and all 127 blocked rows**; 5,580 safe rows are delivered. |
| Active development row joinability | **5,707/5,707 restored**, including the 127 refusals. |
| Original Q1b row/structure snapshots | **108/108 byte-identical** to the Q2 copies used for direct comparison. |
| Frozen enriched page statistics and glyph Parquet rows | **95/95 exact for each family**, with only the declared statistics metadata exempt. |
| Book aggregation | **168/168 exact** variants over 54 book identities. |
| Frozen book summaries | **54/54 combined-collection and 6/6 book-only files exact**. |
| Corpus summaries | **2/2 exact**, for the 95-page combined collection and 41-page book-only collection. |
| Frozen historical checks | **0/95 exact**: 215 missing fields outside the allowlist, listed below. |
| Full test suite | **2,317 passed, 0 failed, 0 errors, 16 skipped**, out of 2,333 cases. |

The five partial envelopes reproduce the original row order, geometry, refusal
reasons and crossing evidence, not just the blocked-row counts:

| Page | Expected blocked rows | Actual | Entire envelope exact |
| --- | ---: | ---: | --- |
| `an-7a2b17a3fb0f-p000200` | 25 | 25 | Yes |
| `s2-200e977f2dab5291c42c-p00035` | 30 | 30 | Yes |
| `s2-6419488b7f8e69fd20da-p00001` | 15 | 15 | Yes |
| `an-d3237d690aa0-p000138` | 2 | 2 | Yes |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 55 | 55 | Yes |

The test receipt is `.astra/q3b-final-tests.xml`; the 16 skips are the existing
web-render tests whose Chromium executable is unavailable in this sandbox.
All production Python sources and the page equality runner retain their hashes
from the start of the 95-page run. The gate also binds source images, layout
inputs, book selection/order and the compared frozen artifacts by SHA-256.

The committed [equality receipt](PAGE_LINES_Q3B_EQUALITY.json) contains counts,
input/source identities, all 168 book results and the five partial-envelope
results. The [complete differences](PAGE_LINES_Q3B_DIFFERENCES.json.gz) retain
both the 215 failing fields and every allowed metadata difference. Reproduce
with `scripts/pages/check_q3b_equality.py`, then `check_q3b_books.py`, then
`write_q3b_receipt.py`, using the queue's Python and offline environment.
The page checker and final receipt writer currently exit **1**; the book checker
exits **0**.

### Remaining strict-gate failures

These are missing fields, not numeric mismatches in the detector's current
diagnostics. Q3 did not compare frozen checks; Q3b compares them explicitly and
does not silently exclude the historical review additions.

| Path in `checks.json` | Files differing | Historical source |
| --- | ---: | --- |
| `$.hint_comparison` | 95 | The research renderer wrote `null` when hint comparison was not requested. |
| `$.nontable_review_sha256` | 54 | The non-table review writer recorded its own implementation identity. |
| `$.checks.8_nontext_ink.candidate_segments_on_detected_graphics` | 54 | The non-table review writer added segment/graphic overlap results. |
| `$.checks.6_column_crossings.owner_slanted_reference` | 3 | The owner review added manually supplied slanted-divider parameters and old/new crossing results. |
| `$.checks.6_column_crossings.review_crossing_lines` | 3 | The review measured crossings against its separately supplied divider reference. |
| `$.checks.6_column_crossings.review_reference` | 3 | The review retained the explanation of that manual reference. |
| `$.checks.6_column_crossings.review_reference_x` | 3 | The review retained the manual divider coordinate. |

These fields have not been added to the metadata allowlist. The API has no
historical review-input stage, and this change does not inject page-specific
annotations or copy old review results into it. Replaying those review outputs,
or an explicit owner decision that they are outside this gate, remains necessary
before claiming DONE. The full frozen JPEG review-image set and historical
orientation receipts are also not certified here; crop pixel identity is the
image comparison performed by this run. Orientation remains opt-in and its
existing tests pass.

### Q3b commit handoff

`git add` was refused by the sandbox when it tried to create the worktree's
`index.lock` (`Operation not permitted`). No Q3b commit was created, and HEAD
remains `e123b9b2613f4036932dc8b4cb432b2c57f668ba`.

The queue fallback is `.astra/Q3b-joining-contract.patch` and
`.astra/commit-Q3b.sh`, with the required trailers and a file-hash manifest.
The patch is checked in reverse against the working tree and applied forward to
a temporary reconstruction of the HEAD files; every resulting file hash is
verified. The commit script binds the branch and HEAD, checks all 19 file hashes,
and refuses pre-existing staged changes. Its final exit status is deliberately
**1 even after a successful commit**, because the strict equality gate remains
NOT DONE and the queue must stop.
