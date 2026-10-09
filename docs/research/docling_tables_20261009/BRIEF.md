# Research: what Docling's table pipeline needs from our OCR plugin

You are an independent RESEARCHER. Answer the question below from Docling's actual code and from small experiments,
not from memory or documentation alone. Do not edit anything outside this directory (the working directory).

Ground rules:
- Do not start background jobs. Work offline: set `HF_HUB_OFFLINE=1`; the Docling models are already cached in
  `~/.cache/huggingface/hub` (`docling-project--docling-models` contains TableFormer).
- Python with Docling 2.135.0 and docling-ibm-models 4.0.3:
  `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
  Its site-packages hold the Docling source to read.
- The text layer of a PDF is another OCR's output, never a reference. Do not use the `text` of `pages/*.boxes.json`
  as truth.

## Context

We are building a Greek OCR engine that plugs into Docling as an OCR model. Docling runs OCR before layout analysis:
the plugin receives the page image and the regions to OCR, and returns text cells (`TextCell`, with boxes). Docling's
layout model, table-structure model (TableFormer) and reading order then work on those cells.

Our plugin and its contract tests:
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/deploy/docling_plugin/`;
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/tests/test_docling_contract.py`;
- `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/DOCLING_PLUGIN_CONTRACT.md`,
  an earlier analysis written against docling 2.81; check it against 2.135.

Our cells come from a page-line detector. It finds printed lines from the pixels and cuts each into curve-following
segments that are passed to a line recogniser. On normal text a cell is one printed line, or one line piece between
column boundaries. On tables the detector is weak: it sometimes joins the contents of several table cells into one
line, crosses ruled boundaries, or misses columns.

The owner's question, in their words: "research … on what the specs of what we should deliver to docling with our
line detections are? is it eg just clean detection of each element in each cell independently of each other? is it ok
if they are fused and docling separates them? or something else?"

## What to establish

1. **The path a text cell takes into a table.** Trace it from the OCR model's returned cells through layout, the table
   structure stage (TableFormer) and the final `TableItem` / table cells. Give file and line references in the
   installed source.
   - Where are text cells matched to the predicted table cells?
   - Which option controls this (e.g. `do_cell_matching`, `TableStructureOptions`, `TableFormerMode`), and what does
     each setting change?
2. **Granularity.** Which text granularity does the matching expect and handle best: word-level, cell-level or
   line-level? What does Docling's own OCR (e.g. EasyOCR, Tesseract) return for table regions?
3. **Fused and crossing cells.** Is it acceptable if one of our text cells spans two or more table cells (fused across
   a column, or across a rule)?
   - Does Docling split it, assign it whole to one table cell, duplicate it, or drop it?
   - What happens to a text cell that lies partly outside every predicted table cell?
4. **Coordinates and other fields.** Which coordinate system, origin and box conventions, and which fields of
   `TextCell` (confidence, `from_ocr`, rect or polygon, text direction) the table stage actually uses. Is a skewed or
   curved line's box handled?
5. **Does the table stage re-OCR or read pixels itself?** Does TableFormer look at the image only for structure, and
   take all text from our cells? Does any path read the PDF text layer instead of the OCR cells for scanned pages?

## Experiments (offline, small, in this directory)

The pages are in `pages/`: three table pages from our development set.
- `an-7a2b17a3fb0f-p000200`: navigation tables, a two-page spread.
- `s2-200e977f2dab5291c42c-p00035`: a Vouli table.
- `s2-831443dc5e6f1ccfbaf5-p00020`: a Vouli table.

Our detector's current output for them is in `round3/`: `lines.json`, with per-pixel curves and `x0, x1, top,
bottom`; `segments.json`; and `lines.jpg` to look at.

Run Docling's table structure on these pages with controlled OCR cells, through a stub OCR engine or by injecting
cells, to measure how the result depends on the cells we give it. Compare at least:
- (a) our current line cells;
- (b) the same lines split at wide gaps into pieces;
- (c) word-level cells, approximated by splitting at word gaps.

Use placeholder text that identifies each cell, so you can see where each cell's text lands in the output table.
- Report what changes in the table output: cells assigned, split, duplicated or lost.
- Keep each experiment small. If running a page takes more than a few minutes on this MacBook CPU, use one table
  region crop instead and say so.

## Deliverable

Write `REPORT.md` in this directory:
1. **The answer for the owner, in plain words first:** what our line detections should deliver to Docling for tables
   to come out right, and whether fused cells are acceptable.
2. **The specification:** granularity, which boundaries a cell must not cross, coordinates, fields and options, with
   the evidence (file:line, and experiment results with numbers).
3. **The experiment table:** setting, page, table cells found, text cells assigned / split / duplicated / lost.
4. **What we should change, and the acceptance test** for a table development cycle on our table pages.
5. **What you could not verify.**

The last line must be exactly: `RESULT: <ANSWERED|PARTIAL> <one line>`
