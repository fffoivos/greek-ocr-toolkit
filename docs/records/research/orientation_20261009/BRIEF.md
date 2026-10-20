# Research: the orientation of the writing — what Docling does, and how we should detect it

You are an independent RESEARCHER. Answer from code and from experiments, not from memory. Do not edit anything
outside this directory (the working directory).

Ground rules:
- Do not start background jobs.
- Work offline: `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. The Docling models are cached in `~/.cache/huggingface`.
- Python with Docling 2.135.0: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`. Its
  site-packages hold the Docling source.
- Tesseract is installed (`/opt/homebrew/bin/tesseract`, with `osd.traineddata`).
- The PDF text layer is another OCR's output, never a reference.

## Context

We are building a Greek OCR engine (1800s Greek books and 1880s parliamentary records) that plugs into Docling as an
OCR model. Our page-line detector (`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4`,
`greekocr/glyphs/page_text_lines.py` and `pixel_segments.py`) assumes all writing is horizontal and upright.

On `pages/s2-6419488b7f8e69fd20da-p00001.png`, a ruled table printed sideways, it reads the vertical text as
horizontal: 327 kept "lines" with a median length of 45 px, against a median x-height of 26 px. 69% are shorter than
three x-heights, i.e. slices across the vertical text. Its output for 10 pages is in `round3/`.

Docling's findings for tables are in
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/research/DOCLING_TABLES_20261009.md`. It shows
that layout runs before OCR from the image alone, and that table cells use only axis-aligned boxes.

The owner, verbatim:
- "we have no capacity to check for orientation of writting, which we generally should be doing";
- "it must be that we need to figure out orientation of the words";
- "We could ask sol to do different tests as well with rotated pages".

So orientation is to be determined **for words**, not only for whole pages: one page can mix horizontal text,
sideways table headers, vertical labels and rotated blocks.

## What to establish

1. **Docling and rotation.** Trace in the installed source what Docling 2.135 does with rotated content:
   - page-level rotation, e.g. the PDF `/Rotate` attribute or an orientation classifier; check whether any exists in
     2.135 and its options;
   - how the layout model behaves on a page rotated by 90°, 180° or 270°: run it;
   - how TableFormer behaves on a table rotated 90°: run it;
   - what the `TextCell` fields `rect` (four corners), `text_direction` and any orientation fields mean, and whether
     any later stage uses them.

   From this, state the frame our cells must be in when the writing is rotated:
   - Do we rotate the page before Docling sees it?
   - Do we return cells in the original page frame with rotated rectangles?
   - Does a sideways table still become a table?
2. **Candidate orientation detectors, at page, block and word level:**
   - Tesseract OSD;
   - a projection-profile / component-geometry method that uses the ink alone: the direction of text lines, and the
     asymmetries of Greek letters (ascenders, descenders, accents above letters);
   - anything else that runs offline here.

   Evaluate each for accuracy, failure modes, speed, and the smallest unit it can decide reliably (page, block, line,
   word).
3. **Tests with rotated pages.** Build a reproducible test set from `pages/`:
   - **Whole pages** rotated by 90°, 180° and 270°.
   - **Composite pages:** a block, or a set of words, rotated 90° or 270° and pasted into an otherwise upright page.
     This mimics sideways headers and labels.
   - **Small skews,** ±1–5°, as a control: that is skew, not orientation.
   - **The real sideways page,** s2-6419488b7f8e69fd20da-p00001, with its orientation labelled by you from the image.

   Run each candidate detector, and Docling's layout model, on the set. Run our current line detector on the rotated
   whole pages too (`segment_page` from `greekocr.glyphs.page_text_lines`, in the worktree above, read-only) and
   describe how it fails.

## Deliverable

Write `REPORT.md` in this directory:
1. **The answer for the owner, in plain words first:**
   - what Docling does with rotated writing;
   - what our engine must do;
   - which detector to use, at which level (word, line or block).
2. **The Docling trace,** with file:line evidence.
3. **The test set:** how it is generated (the script is in this directory) and its contents.
4. **The results table:** detector, unit, rotation, accuracy, time per page. Separately, Docling layout and our line
   detector on rotated pages.
5. **The specification for part 3 of our implementation:** what to detect, where in the pipeline, the outputs, and the
   acceptance tests using this test set.
6. **What you could not verify.**

The last line must be exactly: `RESULT: <ANSWERED|PARTIAL> <one line>`
