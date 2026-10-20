# Content gate 0.3, part 3: final eligibility follows the cell amendment; homoglyph ruling recorded; full suite green (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no census)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. HEAD contains content gate 0.3 parts 1 and 2:
`docs/harvest/line_pipeline/gate03/REPORT.md`, `REPORT_part2.md` and the briefs `docs/records/briefs/GATE_03_content_gate.md` and
`GATE_03b_short_lines.md`. Write `gate03/REPORT_part3.md`. The untouchables are the same as before.

The lead has placed `scripts/harvest/clariden/{worker.py,bootstrap.py,filter_crop_paths.py,filter_worker.sbatch,package.py}`.
They are byte copies of this branch's committed `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/`
and identical to sol-recut's working files. Verify the shas against the package copies and do not edit them.

## 1. Final eligibility follows the owner's cell amendment (coordinator ruling)

In `final_eligibility`:
- **For a cell** (the same A ≤ 6 cell definition and the same shared helper as the part-2 gate), the only length/shape check is
  alnum > 1. `short_line`, `nonletter_fraction` and the ≥4-digit / 60% `numeric_shape` do not apply to cells.
- **For a non-cell numeric line** (`numerics_tables` role OR numeric grammar), keep the existing checks unchanged.
- **For an ordinary line**, change nothing.
- `codec_unencodable`, `ctc_*`, `low_confidence`, `heldout_edition` and the `content_issues` recheck apply to every row, as now.

The gate and `final_eligibility` must agree. Every row the gate admits as a cell can fail at the end only for one of those
non-length reasons. Add a test for that: run a cell through both with a segmenter and correctors that KEEP and change nothing.

**Diagnostic.** Re-run part 2's diagnostic count, read only, on the 150, 888, 250 and 417 sets:
- the rows whose final-eligibility outcome this changes, before → after, by reason;
- the remaining non-cell numeric rows still excluded by `numeric_shape` or `nonletter_fraction`.

## 1b. The shared test fixture must default to an ordinary line

Part 2 changed the shared `row()` fixture in `tests/test_line_pipeline.py` to a default `crop_bbox` of 100×20 (A = 5, a CELL). The
old tests were written for ordinary lines. With that default, and with this part's cell rule, they would silently test the cell
path instead.
- Change the default to a wide ordinary line, e.g. 1000×20 (A = 50). Tests that are about cells pass cell dimensions
  explicitly.
- Report every existing test whose outcome changes under the new default, with the cause.
- If an old test only passed because its row was a cell, give it explicit dimensions that match what it is testing, and show
  the diff.

## 2. Record the homoglyph ruling in the gate docs

Add this to `docs/records/harvest/line_pipeline_legacy/README.md`, gate section, and to `gate03/REPORT_part3.md`.

**Owner, 14 Oct.** Any Greek word containing a Latin, Cyrillic or other-script letter drops the whole line automatically. Examples:
ΚΕΦΑΛΑΙΟN, Δαβій, Fιδον, λόγoς. There is no look-alike correction and no model pass. The earlier repair-and-admit path for such
words was a deviation from the owner's rule, and gate 0.3 removes it.

**Owner, 18 Oct.** The only allowance is a secondary-script WHOLE word, per class, when it has at least one letter with no
look-alike in the primary script.

**Check, read only.** Does the current code implement the 18 Oct allowance? Report where, or that it does not. Do not implement
it in this run.

## 3. The full suite runs green

- Run `tests/test_content_gate.py`, `tests/test_line_pipeline.py` and the four `tests/test_seg_*.py` with the clariden scripts
  present.
- Report the counts verbatim. The target is 0 failures.
- If any test still fails, give the traceback and its cause. Fix it only if the cause is in code changed by gate 0.3 parts 1–3.
  Otherwise report it and stop.

## 4. Versions and scope

- The content gate stays 0.3; final eligibility becomes 0.3, with the iteration "cells: alnum > 1 is the only length/shape
  check, consistent with the gate".
- The `build_filter_versions.py` definitions for census include the clariden scripts: regenerate `tool_versions.json` now that
  they exist. List `version-build-fallbacks.json` before and after.
- Write a scope guard and a receipt.

**Last line:** `GATE 0.3 PART 3 READY: final cell rule <ok>; gate/final agree <ok>; final outcomes changed <n> (by reason); clariden shas <5/5>; 18-Oct allowance <implemented at X|absent>; tests <n> passed <n> failed`
