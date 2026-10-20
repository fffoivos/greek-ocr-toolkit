# SS1 — "What is small": census dimensions, font-line break curves, candidate definitions (read-only analysis)

You are Sol, executing for the small-segment analysis lead. This is a read-only descriptive analysis. Write a script, tests,
tables and a receipt. Do not judge or recommend; the lead does that from your tables.

Worktree: `~/Projects/greek-ocr-toolkit-sol-recut` (branch `sol/recut-v1`). Base dir below:
`B = docs/records/harvest/collect_v3_admission/segeval1`. Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python` (the system python
has a broken numpy). Network off.

## Hard constraints
- Write ONLY under `B/small_segments/q1/`, `B/small_segments/tools/` and `B/small_segments/tests/`. Change nothing else anywhere
  (no tool code, no other segeval1 file, no git commit, no git add).
- Read-only inputs (list each with sha256 in the receipt):
  - `B/cells/population_cells.jsonl.gz` — the census, 592,466 rows (schema in `B/cells/HANDOFF.md`). Stream it; drop
    `pipeline_reasons`, `remote_crop` etc. that you do not need.
  - `B/owner_marks_20261019.jsonl` — 240 owner marks: `sheet`, `line_id`, `owner_mark` (KEEP/DROP), `note`, `updated`.
  - `B/gate2/replay_calibration.jsonl` — 888 rows; `owner_rating` is null or a dict with `decision` (135 non-null);
    also `verdict_05`..`verdict_08`, `line_id`.
  - `B/gate2/replay_segeval1.jsonl` — the 150 replay (`verdict_05`..`verdict_08` per `line_id`, same layout as above).
  - `B/scored/owner_rows.jsonl` — the 150 blind check: `decision` = pipeline ACCEPT/REJECT, `reader_state` = blind readers'
    fine/flagged/unresolved (readers, NOT the owner).
- No Clariden, no network, no image reading in this brief.

## Definitions (implement exactly; put each in one function with a docstring)
- `chars` = census field `characters` (saved visible count). Also carry `text_characters`.
- **Rotation (the segmentation lead's step 2 turns height>width crops 90° right before any measurement):**
  `rotated = height_px > width_px`; `L = max(width_px, height_px)`, `S = min(width_px, height_px)`; `A = L / S`.
  Also keep the unrotated `w/h`.
- `xh` = `xheight_px` (may be 0/None; report how many are unusable). Derived: `S_xh = S/xh`, `L_xh = L/xh` when xh > 0.
- Output type (from `raw_text`, after `str.strip()`): `numeric` = census `is_numeric_output` true; `mixed` = not numeric, ≥1
  Unicode decimal digit and ≤2 letters (Unicode category L*); `nonnumeric` = everything else (incl. empty text — count empties).
- `wave_group`: `collect_v3` if wave in {W1, W2} else `v2`. Report the wave vocabulary with counts.
- **verdict_05 reason category.** First enumerate every distinct `(verdict_05, reason_05)` string with counts (table T0, all
  strings, full text). Then map to: `KEEP`; `DROP_too_little` (reason mentions "Too little OCR output");
  `DROP_too_much` ("Too much OCR output"); `UNC_no_row` (UNCERTAIN whose reason says no supported/detected row);
  any other reason gets its own short slug derived from the string (e.g. `DROP_second_line`, `DROP_padding`,
  `DROP_neighbour_words`, `UNC_<slug>`). Print the full string → category mapping in T0 so the lead can check it.
  `box_fail` = DROP_too_little ∪ DROP_too_much ∪ UNC_no_row.

## Owner-judged lines (join to census by `line_id == row_id`; report unmatched ids; if a source row carries a crop sha256, use it
as a fallback join and report which join matched)
- `O_marks`: every mark in owner_marks (good = KEEP, bad = DROP), with `sheet` and `note`.
- `O_ratings`: replay_calibration rows with non-null `owner_rating`; report the `decision` vocabulary; good/bad mapping:
  KEEP/ACCEPT/GOOD-like = good, DROP/REJECT/BAD-like = bad, anything else listed as `other` (print the mapping).
- Attach `verdict_06/07/08` from the replay files where the line is present (both replay files).
- `R_150`: the 150 blind check reader_state (secondary evidence, readers not owner) — kept separate from owner sets.
- A line may be in several sets: count per set and unique lines.
- `owner_bad_box`: owner notes containing "box" (case-insensitive) — flag them.

## Tables (write `q1/Q1_TABLES.md` with all tables, and `q1/q1.json` with the same numbers machine-readable)
- **T0** reason vocabulary + mapping (above). Census totals by verdict and category.
- **T1** quantiles p1, p5, p10, p25, p50, p75, p90, p95, p99 of `width_px, height_px, L, S, A, chars, xh, S_xh, L_xh`:
  overall; by output type; by `chars ≤ 10` vs `> 10`; by wave_group.
- **T1b** rotation by chars: for chars = 1, 2, 3, 4, 5, 6–9, 10–15, 16+ and output type: n, n rotated (h>w), n with h > 1.25·w,
  n with h > 2·w.
- **T2** break curves. For chars = 1…30 individually, then 31–40, 41–60, 61+: n, % KEEP, % DROP_too_little, % DROP_too_much,
  % UNC_no_row, % other non-KEEP, % box_fail. Three versions: all rows; numeric; nonnumeric+mixed. Plus each split by
  rotated yes/no (rows with n<30 still printed, marked).
- **T2b** the same break-curve columns by bucket of: `A` (edges 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50, ∞);
  `S` px (≤10, 15, 20, 25, 30, 40, 50, 60, 80, 100, ∞); `L` px (≤25, 50, 75, 100, 150, 200, 300, 500, 1000, ∞);
  `xh` px (≤4, 6, 8, 10, 12, 15, 20, 25, 30, 40, ∞, plus unusable); `L_xh` (≤1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50, ∞).
- **T3** 2-D: chars bucket (1, 2, 3, 4, 5, 6–7, 8–9, 10–12, 13–15, 16–20, 21–30, 31+) × A bucket (as T2b) → n and % box_fail.
- **T4** candidate definitions. For each candidate: rows captured (n, % of census) and by output type and wave_group;
  % box_fail and % KEEP inside vs outside; % box_fail inside among chars ≤ 10 only; owner-judged inside vs outside as counts
  `good/bad` per set (O_marks per sheet, O_ratings) and unique; among owner-good inside: how many verdict_05 ≠ KEEP and,
  where available, verdict_08 ≠ KEEP (false rejects the candidate would route to the small path); same for owner-good outside;
  R_150 fine/flagged inside vs outside. Candidates (all on rotated dims):
  - C1 `chars ≤ k`, k ∈ {1, 2, 3, 4, 5, 6, 8, 10, 12, 15}
  - C2 `A ≤ a`, a ∈ {1.5, 2, 3, 4, 5, 6, 8}
  - C3 `L ≤ N px`, N ∈ {50, 100, 150, 200}
  - C4 `L_xh ≤ q`, q ∈ {3, 5, 8, 10, 15} (xh unusable → outside, count them)
  - C5 `S ≤ 40 and L ≤ 200 and chars ≤ 10` (the SEG-CELLS `is_small_image`, rotated)
  - C6 `chars ≤ k or A ≤ a`, (k, a) ∈ {3, 5, 8} × {2, 3, 4}
  - C7 `chars ≤ k and A ≤ a`, (k, a) ∈ {3, 5, 8} × {3, 4, 6}
- **T5** every owner-judged line with chars ≤ 20 or A ≤ 6, sorted by chars then A: line_id, set(s), owner good/bad, note,
  raw_text, chars, width_px, height_px, rotated, L, S, A, xh, L_xh, output type, source, wave, verdict_05 + category,
  verdict_08. Also as `q1/owner_joined.jsonl` with ALL owner-judged lines (not only the small ones) and all fields above.
- **T6** for the owner-good lines with verdict_05 or verdict_08 ≠ KEEP: chars histogram (1, 2, 3, 4, 5, 6–9, 10–15, 16–30, 31+)
  split by reason category — where the false rejects sit.

## Tests (`small_segments/tests/test_ss1_q1.py`, pytest, run with the venv python)
A synthetic fixture of ~20 rows (write it inside the test) covering: rotation (h>w, h==w, h<w), `A` bucket edges (value exactly
on an edge goes to the lower bucket: `≤`), reason mapping for each category including an unknown reason, mixed vs numeric vs
nonnumeric vs empty text, xh = 0, candidate membership for one C1/C2/C6/C7 case each, the owner join (one unmatched id, one line
in two sets). Run the tests and include the pass output in the receipt.

## Receipt and report
- `q1/SS1_RECEIPT.json`: inputs (path, sha256, row count), outputs (path, sha256), script sha256, python + pandas/numpy versions,
  census row count read (must be 592,466 — stop and report if not), owner-join counts per set (matched/unmatched), test result.
- Final message: a short summary with the census totals, T0 category counts, the owner-join counts, any anomaly, and the paths.
- Last line exactly: `SS1 READY: q1/Q1_TABLES.md, q1/q1.json, q1/owner_joined.jsonl, receipt q1/SS1_RECEIPT.json` (or
  `SS1 FAILED: <reason>`).
