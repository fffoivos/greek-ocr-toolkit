# SS6 — Q3 final tables, samples.jsonl, and the owner review sheet (no reading)

You are Sol, executing for the small-segment analysis lead. Produce the Q3 tables from the typed sample with the lead's eye
corrections applied, the deliverable `samples.jsonl`, and an owner review sheet rendered through the toolkit's owner_sheet package.

Worktree `~/Projects/greek-ocr-toolkit-sol-recut`; `SS = docs/records/harvest/collect_v3_admission/segeval1/small_segments`.
Owner-sheet package: branch `coord/review-sheets`, checked out at `~/Projects/greek-ocr-toolkit-review` — import
`greekocr.adjudicate.owner_sheet` from there (e.g. `PYTHONPATH=~/Projects/greek-ocr-toolkit-review`), read
`docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md` there and follow it; use `docs/records/review/reference_scratch/build_gate_sheet.py` only as a data
adapter reference. Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

## Hard constraints
Write ONLY under `SS/q3/`, `SS/sheet/`, `SS/tools/`, `SS/tests/` (new files), plus `SS/samples.jsonl`. Do not edit the
review worktree or the package; no git add/commit; no reading runs; no `codex`.

## Inputs
`SS/q3/typing.jsonl` (SS5), `SS/q3/LEAD_EYE.json` (the lead's corrections under `corrections`: line_id → final `type`, `text`,
`crop`, `note`; rows not listed keep Sol's values; `checked` lists every line_id the lead looked at; `observations` are the lead's
notes on Sol's errors — quote them in T13), `SS/q3/sample.jsonl`, `SS/q1/owner_joined.jsonl`,
`SS/q3/AGREEMENT.json`.

## Final type and class (per bed row)
`final_type` = lead's type if listed, else Sol's. `class`:
- `legit_text`: final_type ∈ {word, caps_display, abbrev_label, marker, roman_lower, digits_letters, number} and crop = ok;
- `printed_nonletter`: punctuation with crop = ok;
- `non_text`: noise, handwriting, figure_ornament, watermark, show_through;
- `out_of_scope_script`: foreign_script;
- `segmentation_fault`: cut_fragment, multi_line, part_of_line, or any legit/punctuation type whose crop is clipped/extra;
- `other`: other.
`label_ok` = final text ∈ {match, minor}.

## Tables (`q3/Q3_TABLES.md` + `q3/q3.json`)
- **T7** counts per final_type and per class, overall and per stratum (opus, inside_by_source, mixed, rotated, border_outside,
  owner), with 3 example line_ids each, median w×h, chars, A, and the share with label_ok.
- **T8** population estimate for nonnumeric small rows (definition `chars ≤ 8 and A ≤ 6`): from the inside_by_source stratum
  weighted by each source's pool share (SS3 receipt), per class and per final_type, with a 95% Wilson interval on the unweighted
  shares; say it is a 150-row sample.
- **T9** per source (inside_by_source): class shares.
- **T10** Google text profile per class: share of rows whose text is letters only / digits+letters / punctuation only / contains a
  non-Greek-Latin-Cyrillic script character / empty, and label_ok share. If the toolkit has a local word list or lexicon (search
  `greekocr/` and `artifacts/` for spellcheck lexicons), report the share of Google tokens (≥ 2 letters) found in it per class and
  name the file; if none is found, say so and skip.
- **T11** mixed (digits + letters) stratum: final_type and class counts, examples.
- **T12** owner-judged rows in the sample: final class vs the owner's good/bad.
- **T13** lead eye vs Sol: how many rows the lead checked, how many changed, per Sol type (from LEAD_EYE.json).

## `SS/samples.jsonl`
One row per crop looked at (all 437 sample rows incl. controls, controls flagged): line_id, crop_path, text, width, height, chars,
A, source, book, class (primary_class), wave, verdict_05, reason category, inside, stratum, Sol type/text/crop/rotated, lead
type/text/crop/note if any, final_type, final class, label_ok, opus_type if any.

## Owner sheet (`SS/sheet/small_segments_sheet.html`)
- One card per bed row (controls excluded), **grouped by final_type** in this order: word, caps_display, abbrev_label, marker,
  roman_lower, digits_letters, number, punctuation, foreign_script, handwriting, watermark, figure_ornament, show_through, noise,
  cut_fragment, multi_line, part_of_line, other. Within a group: inside rows first, then border_outside; then by source.
- Group header: type name, a one-line description (from `SS/prompts/type.md`), count, and the proposed class.
- Card: crop with the Google text beneath (package default); rows: "Type (Sol / lead)", "Text vs crop" (text, crop, rotated,
  detail), "Opus type" if any, "Size" (w×h px, chars, A, inside/outside), "Source" (source, book, wave); tool verdicts = the last
  two versions available for the line: 0.5 (census) and 0.8 where the replay files have it (`SS/q1/owner_joined.jsonl` has 0.8
  for owner-judged lines; otherwise only 0.5). Inner frame = the latest of those verdicts (package behaviour).
- Owner mark meaning (state in the intro): **KEEP = this crop with its Google text is a usable training line; DROP = it is not.**
  Intro also: what the sheet is (Q3 typology of non-numeric small segments, small = chars ≤ 8 and long/short side ≤ 6), the
  colour legend, keys, and the group counts.
- Sheet prefix for db ids: `smallseg` (ids `smallseg:<line_id>`). Do not write on load (package behaviour).
- Do a headless render check if a headless browser is available locally; otherwise validate the HTML parses and every card has
  an image, and say which.

## Tests (`SS/tests/test_ss6.py`)
Class mapping on each type; lead override precedence; group order; ids unique and stable; samples.jsonl has every sample row.

## Receipt
`SS/q3/SS6_RECEIPT.json` (inputs/outputs sha256, card counts per group, render check, tests).
Last line exactly: `SS6 READY: Q3 tables q3/Q3_TABLES.md, samples.jsonl <n>, sheet SS/sheet/small_segments_sheet.html (<k> cards)`
(or `SS6 FAILED: <reason>`).
