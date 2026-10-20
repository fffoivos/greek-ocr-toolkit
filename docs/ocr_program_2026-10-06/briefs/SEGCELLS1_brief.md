# SEG-CELLS-1 — numeric cells: classify by image dimension + numeric output, census the whole population, show samples (gpt-6.1-sol, xhigh, network ON read-only for Clariden streaming only)

Workspace: this worktree, branch from `sol/seg-gate2` (commit 410f4566 = segmentation 0.8) as `sol/seg-cells` (bundle fallback `docs/records/harvest/collect_v3_admission/segeval1/cells/SEGCELLS1.bundle`). Never push. Do not touch the five pre-existing uncommitted edits. `.venv/`. **No verdict or policy change in this task**: this is classification + census + samples. No Slurm, no readers, no writes on Clariden; read-only SSH streaming only, exactly as `segeval1/tools/export_remote.py` does (same immutable census_02 export `…/attempts/census_02/census/generations/g1-1c775230225d4bbea5871d4fae2475da/decisions.jsonl`, 592,466 rows, sha 568d4759…; verify the receipt as that tool does).

## Owner (19 Oct, verbatim)
"I think we need a different rule for the small number cells. We should be checking the image dimension and if the output is number. This should help us classify if it is a cell. You should also check over the whole corpus what type of segments you find by this rule."

Context: on the 150-line check, 13 of the 18 remaining false rejects of segmentation 0.8 are tiny crops of 1–9 characters whose output is a number or a number-like token ("29)", "3.237.787", "270", "ΙΙ"); the length rule has no real font height to normalise against on them. See `segeval1/gate2/replay_segeval1.jsonl` (fields `after.frame.source_width/height`, `after.evidence.characters`, Google text in `segeval1/scored/owner_rows.jsonl`).

## Deliverable 1 — the classifier (`greekocr/harvest/numeric_cells.py`, pure function, no side effects)
`classify_cell(text, width_px, height_px, xheight_px=None) -> {is_numeric_output, is_small_image, is_cell, reasons}` where:
- `is_numeric_output`: the Google text, after trimming, consists of digits with optional separators and signs (`. , : / - – — % ( ) + ' ′ § №` and spaces), or a Roman numeral, or a single digit-dominated token; letters beyond a Roman numeral make it non-numeric. State the exact grammar in the docstring and in the hand-off. Do not invent further classes.
- `is_small_image`: derive the thresholds FROM THE CORPUS (deliverable 2), not by guess: report the width and height distributions (in pixels and, where the saved evidence has it, in x-heights) of numeric-output rows vs all rows, and propose a cut (e.g. width ≤ N x-heights or ≤ M px and ≤ K characters) with the numbers that justify it. Record the chosen thresholds as named constants.
- `is_cell = is_numeric_output and is_small_image`.
Unit tests on the 13 tiny false rejects above and on 20 ordinary lines from the 150 (must not be cells).

## Deliverable 2 — census over the whole population
Stream the census_02 export read-only and reduce per row: row_id, source, primary/script class, wave/parent, raw text, crop width/height (from the segmentation evidence `frame.source_width/height`), character count, x-height if present in evidence, the 0.5 segmentation verdict + reason, and the pipeline disposition. Save the reduced table gzipped under `segeval1/cells/population_cells.jsonl.gz` with the export receipt. Then report, in the hand-off:
- how many rows are numeric-output; how many are cells under the proposed thresholds; by source, by class, by wave (table);
- what the 0.5 filter did with them (KEEP / DROP by reason / UNCERTAIN) — i.e. how many of the 16,736 census DROPs and 151,645 HOLDs are cells;
- the dimension distributions (histograms as text tables: width px, height px, chars) for numeric-output rows vs the rest;
- "what type of segments you find": draw 150 cells uniformly (seed 20261019) across sources and fetch their crops read-only (scp from the census crop locations recorded in the export; if a crop is not fetchable, say so and draw another) into `segeval1/cells/samples/`, plus 50 numeric-output rows that are NOT small (to show the boundary) and 50 small rows that are NOT numeric; write `samples.jsonl` (row_id, source, class, text, w, h, chars, 0.5 verdict, reason, crop path, sha256). The coordinator builds the owner sheet from this file.
- on the 150 evaluation lines: which of the 18 false rejects and which of the 150 overall are cells.

## Constraints
Read-only everywhere on Clariden; stream, do not copy the 8 GB export; Mac work is the reduction and the 250 crops only. No change to any policy, versions file or verdict. State every threshold with the numbers that led to it. No accuracy claim about cells beyond what the samples show.

Hand-off `segeval1/cells/HANDOFF.md`; last line exactly:
`SEGCELLS1: done | numeric-output rows <n>/<N> | cells <n> (thresholds: <w>, <h>, <chars>) | cells among 0.5 DROP <n>, HOLD <n>, KEEP <n> | samples fetched <n>/250 | tests <n> passed | commit <sha>`
