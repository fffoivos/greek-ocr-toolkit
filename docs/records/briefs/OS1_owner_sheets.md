# OS1: two owner sheets in the STANDARD sheet format via greekocr.adjudicate.owner_sheet (gpt-6.1-sol, medium, network OFF; no .git writes)

**Owner correction (priority):** two pages were hand-written in a new layout. The owner reviews ONLY in the standard sheet format:
- the reference is `docs/records/labelfix/spellcheck/sheet_format_reference_v4.html`;
- the renderer is `greekocr.adjudicate.owner_sheet.render`, with its css/js package files.

Build both sheets with that renderer. No new layout, no hand-written HTML, no summary strips beyond ONE header block per sheet/section.

Workspace: THIS worktree (`opus/cleanup-1`). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
Inputs are read-only.

**Per card, the standard template:**
- a line-id row;
- the image(s);
- named rows (Google = the label; Printed = the editable field, prefilled with the adjudicated print where one exists, otherwise empty);
- tags (pills);
- the checker's detail as the note text shown on the card;
- ONE autosaving db note per card (doc id `{line_id}`), with Printed saved alongside it;
- the hover magnifier on crops.

**Also:**
- No model names anywhere; no "?" characters as placeholders. Images keep their aspect ratio (never stretched).
- Each sheet's spec is written as data (`docs/records/owner_sheets/<sheet>/spec.json`) and built by a small builder
  `scripts/review/build_<sheet>.py`, with a re-render test (the spec renders, every card has a note doc id, there are no missing images,
  card count = spec).

## Sheet A (FIRST): "Failure modes per class"

**Sections** (one per class, in this order): polytonic 1850s; polytonic 1900s; capitals/headings; numerics; punctuation/dialogue;
mixed Greek+Latin; Latin; Cyrillic Russian; Cyrillic Serbian; modern monotonic Gazette.

**Header line per section:** E3 CER and the measured rate per 100 cards, copied from the coordinator's page saved at
`docs/records/owner_sheets/inputs/label_failure_modes_coordinator.html`. That page is data only. Mirror its classes, fault list and numbers
exactly; do not invent numbers. Cyrillic is one section there, so split its rows by Russian/Serbian as its text says.

**Subsections:** one per Google fault type listed for that class, each with **3–6 example cards**. Pick ids deterministically (seed
20261017) from:
- `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/c1_results.json`, per stratum: mark_errors, top_errors,
  superscript, dash, separator, lunate_sigma, lookalike cases, fails;
- the verdict files in `c1/verdicts/`;
- the yer adjudication table `c1/yer_adjudication/table.json` (ъ→ь cards);
- the T6b masked-card verdicts for the three held sources (find them under `docs/records/harvest/collect_v3/`; name the path in the report).

**Crops:** `~/Projects/collect-v3-data/run/W1/crops/<line_id>.png`.

**Tags:** class, fault type, source.

**Gaps:**
- If a fault type has fewer than 3 cards available, show what exists and tag the subsection "fewer than 3 cards" with the count.
- If a fault has none, list it as a heading with "no card in the checked sets", with no fabricated example.

**Output:** `artifacts/owner_sheets/failure_modes_per_class.html`.

## Sheet B: "Segmentation failures"

One card per line.

**Images:**
- the full crop as Google cut it;
- the page strip with Google's box drawn, where it exists.

**Rows:** Google (the label) and Printed.

**Tags:** failure type (merged / fragment / overrun / rotated / clipped / column), source, class, crop height.

**Card note text:** the checker's detail.

**Inputs:**
- `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/examples.jsonl`: 24 examples, with strips
  (sg1-*-strip.png) and crops in that folder;
- the C1 crop-failure cards (`c1_results.json` neighbour_ink, plus the verdict files with crop_ok = n). Take ALL merged (8), fragment
  (4), column (1) and clipped (5) cards, 12 overruns spread across strata, and 4 rotated Gazette crops (height > width). Deduplicate
  against the 24 SG1 examples by line_id.

**Group order:** merged, fragment, overrun, column, clipped, rotated.

**Counts header at the top**, from `segmentation_gallery/counts.json`: per source screen_merged, rotated, and overrun per 100 before
and after masking. Add the 2.8% / 44% and 19% figures from the coordinator's page, cross-cutting geometry section.

Leave a documented hook for a seventh group, "missing box" (SG2 strips, not yet landed). Don't build it now.

**Output:** `artifacts/owner_sheets/segmentation_failures.html`.

## Report

`docs/records/owner_sheets/OS1_REPORT.md`:
- per sheet: card counts per section/group, ids, input paths with sha256, and gaps;
- a format conformance check vs `sheet_format_reference_v4.html` (the same structural elements and class names).

Tests pass (`tests/adjudicate` + the new tests).

Last line: `OS1 READY: A cards <n> (sections 10, subsections <n>, gaps <n>); B cards <n> (groups 6); size A <MB>, B <MB>; tests <n> passed`.
