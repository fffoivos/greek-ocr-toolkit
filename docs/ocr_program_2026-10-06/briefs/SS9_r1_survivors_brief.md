# SS9 — small segments that survive the owner's admission rule, gate failures removed (read-only analysis)

You are Sol, executing for the small-segment analysis lead. Owner rule (19 Oct, as relayed by the coordinator):
- a **cell** is a crop whose long side is at most 6× its short side (A ≤ 6);
- a cell, numeric or text, is admitted if its Google output has more than one letter-or-digit;
- a non-cell numeric line also needs more than one letter-or-digit;
- any other line is excluded below 10 letters (4 for headings_caps).
The segmentation lead's gate 0.3 part 2 implements this; use its definitions below exactly so the counts line up.

Report Q1–Q3 on what survives, and count what the single-character rule removes. No judging, no crop reading.

Worktree `~/Projects/greek-ocr-toolkit-sol-recut`. `B = docs/records/harvest/collect_v3_admission/segeval1`, `SS = B/small_segments`.
Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

## Hard constraints
- Write ONLY under `SS/r1_survivors/` (new files), plus the new files `SS/small_population_key.v3.jsonl.gz`, `SS/tools/ss9_*.py`
  and `SS/tests/test_ss9.py`.
- Do not modify any existing file. Import the SS1/SS2/SS8 functions (`SS/tools/ss1_q1.py`, `ss2_q2.py`, `ss8_*.py`) instead of
  copying their logic.
- No git add/commit; no `codex`.
- Put temp files only in `SS/r1_survivors/tmp/`, and remove them at the end.

## The rule — the segmentation lead's gate 0.3 part 2, exactly (one function each, with a docstring)
Reference, read only, never import or change: `~/Projects/greek-ocr-toolkit-segcensus/greekocr/harvest/line_pipeline.py`
`short_line_exclusion` and `numeric_text`, plus `docs/records/briefs/GATE_03b_short_lines.md` there (record both sha256s). Re-implement
with the same semantics and the same reason names. Work on `raw_text` as stored, with no normalisation, as that function does.
- `alnum` = characters whose category starts with `L`, or is `Nd`. Punctuation, marks and spaces do not count.
- `letters` = characters whose category starts with `L`.
- `A` = max(width_px, height_px) / min(width_px, height_px). If a dimension is missing or ≤ 0, the reason is
  `cell_status_unresolved`; count those.
- `numeric_grammar(text)` reproduces `numeric_text`. s = text.strip(); an empty s is False. It is True if:
  - s has a decimal digit and every character is a decimal digit, a space, or one of `.,:;/-–—%()+'′§№°`; or
  - s, with one trailing `.` or `)` removed, fully matches `M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})` and is
    non-empty.
- `role` = `primary_class`, or `"prose"` if it is missing.
- Then, in this order:
  1. if A ≤ 6 (a cell): `single_character_cell` if alnum ≤ 1, else admitted;
  2. elif role == `numerics_tables` or numeric_grammar(raw_text): `numeric_shape` if alnum ≤ 1, else admitted;
  3. else: `short_line` if letters < 4 for role `headings_caps`, or letters < 10 otherwise; else admitted.
- `admit` = no reason. Only these rules apply; no other admission rule (final numeric_shape ≥ 4 digits, nonletter fraction,
  confidence…). Say so in every table header.
- Also report, as diagnostics, how many census rows have `numeric_grammar` ≠ census `is_numeric_output`, and how many small rows
  would change if NFC normalisation were applied first.
- `survivor` = small (`chars ≤ 8 & A ≤ 6`) AND admit AND NOT gate_failed. gate_failed comes from
  `SS/small_population_key.v2.jsonl.gz` (SS8) and, for the whole census, from `SS/gate_recheck/foreign_mixed_ids_20261019.json`.

## Inputs (read-only; sha256 each in the receipt)
- Census `B/cells/population_cells.jsonl.gz`.
- `SS/small_population_key.v2.jsonl.gz` and `SS/gate_recheck/*` (the SS8 tables and json).
- The SS1/SS2 inputs, per their receipts.
- `SS/q1/owner_joined.jsonl`, `SS/samples.jsonl`, `SS/owner_marks_smallseg.jsonl`, `SS/q3/q3.json`, `SS/q3/SS3_RECEIPT.json`.

## 1. What the rule removes (`r1_survivors/REMOVED.md` + `.json`)
Of the 59,002 small rows:
- counts by (gate_failed, reason), with each reason (`single_character_cell`, `numeric_shape`, `short_line`,
  `cell_status_unresolved`) reported separately; on the small set, expect only `single_character_cell` (all small rows are cells);
- for rows the rule removes that are not gate-failed, counts by alnum (0 / 1), by output_type (numeric vs text = mixed +
  nonnumeric), by primary_class and by source;
- for removed rows in the 417 typology bed, counts by final_class and final_type;
- for the same, an estimated population count per final_class: apply each class's share among removed sample rows to the
  removed nonnumeric/mixed count. Label it an estimate.

## 2. Q1 on the admitted population (`r1_survivors/Q1_R1.md` + `.json`)
Population: census minus gate_failed minus rows not admitted. Rerun the Q1 computations:
- every candidate definition row: rows inside, box_fail % inside and outside, owner good/bad inside and outside, owner-good 0.5
  false rejects inside;
- the failure-rate-by-chars curves (nonnumeric+mixed and numeric) on correctly sized crops;
- the owner-judged lines remaining.

Use three columns: original (SS1) / gate-removed (SS8) / admitted + gate.

## 3. Q2 on survivors (`r1_survivors/Q2_R1.md` + `.json`)
For the recommended definition: source shares and density, wave, primary_class, book concentration 50/80/95% vs baseline, and the
page measures. Same three columns.

## 4. Q3 on survivors (`r1_survivors/Q3_R1.md` + `.json`)
- T8 again, with removed rows dropped from the 150-row inside_by_source sample and from the source pool weights (the survivor
  nonnumeric/mixed small count per source).
- Report before / after / delta per class and per final_type, Wilson intervals on the new unweighted shares, and the new n.
- Bed class counts (417, and the 306 inside) before / after.
- label_ok shares for legit text and punctuation, before / after.
- Owner sheet marks on survivors (KEEP/DROP).

## 5. Key v3 — `SS/small_population_key.v3.jsonl.gz`
The v2 rows, order and fields, plus `letters`, `alnum`, `reason` (null if admitted), `admit` and `survivor`. Gzip deterministically; the v2 fields must stay
byte-identical per row.

## Tests (`SS/tests/test_ss9.py`)
- Rule cases:
  - a cell with one digit is removed and a cell with two is kept;
  - a cell "a." (one letter) is removed and "ab" is kept;
  - a punctuation-only cell is removed;
  - a non-cell prose line with 9 letters is removed and one with 10 is kept;
  - a non-cell headings_caps line with 3 letters is removed and one with 4 is kept;
  - a non-cell numerics_tables line "12" is kept, and a non-cell numerics_tables line "7" fails as `numeric_shape`;
  - a non-cell prose-class line matching the numeric grammar ("1.234", "XIV.") is kept;
  - a row with a 0 dimension gives `cell_status_unresolved`;
  - `numeric_grammar` equals the segcensus `numeric_text` on every raw_text of the 417 bed and the 150-row sample (parity,
    reading that file's source only; if it cannot be loaded standalone, compare against the grammar as written here and say so).
- v3 = v2 plus the five fields.
- With the rule off and an empty gate list, the recompute reproduces the SS1/SS2/SS3 numbers exactly.

## Receipt `SS/r1_survivors/SS9_RECEIPT.json`
Inputs/outputs sha256, counts, tests, and the census sha256 before = after.
Last line exactly: `SS9 READY: small 59002 → survivors <n> (numeric <a>, mixed <b>, nonnumeric <c>); single-char rule removes <r> (numeric <rn>, text <rt>), gate removes <g>`
(or `SS9 FAILED: <reason>`).
