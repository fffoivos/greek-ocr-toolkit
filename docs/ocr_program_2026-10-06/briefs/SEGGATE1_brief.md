# SEG-GATE-1 — segmentation 0.7: line inventory and cut-off gate FIRST, length rule second (gpt-6.1-sol, xhigh, network OFF)

Workspace: this worktree (`greek-ocr-toolkit-sol-recut`). Start from branch `sol/seg-deskew` (commit 58978481 = segmentation 0.6, row-frame text box; its hand-off is `docs/records/harvest/collect_v3_admission/segeval1/deskew/HANDOFF.md`). Create `sol/seg-gate` from it; if the shared Git directory is not writable, deliver a bundle as last time (`segeval1/gate/SEGGATE1.bundle`) and say so. Never push. Do NOT touch the five pre-existing uncommitted edits (`.gitignore`, `test_stage_crops.py`, `geometry_observations.py`, `row_inclusion.py`, `pyproject.toml`). Use `.venv/`. Mac replay of the 150 + 888 crops is authorised for this brief. No Clariden, no Slurm, no readers.

## Owner design (19 Oct, verbatim)
"we need full detection of all the lines, and how much they are cutoff. if we had this decision we could decide to drop or keep from the get go: our verdict now is that 2 words or less from other lines are allowed to show in full, and other cutoff words. only if it passes this gate do we then measure main lines tight box's long side in relation to output"

Standard for a good crop (owner, 19 Oct): (a) exactly one central line of text; (b) the OCR text matches the visible line exactly, neither more nor less (letters cut through, the line leaving the crop, omitted or extra spans are faults); (c) no other line shows completely, and at most 2 whole words from other lines are visible; cut-off words are allowed.

## Two witnesses (from the SEGEVAL-1 replay, `segeval1/deskew/replay_segeval1.jsonl`)
- `847e1ec1-p000015-l0035` must be DROP: `skew_line` on this crop reports angle −1.235°, a baseline crossing at x≈1817 "whole letter body leaves the crop through the bottom edge", a bottom cut span 1990–2044, and 10 cut letters (3 top, 7 bottom). The 0.6 policy returned UNCERTAIN because the neighbour check needed page context.
- `b8b6779da9a68fbed0ccdb5b-p000011-l0018` must be KEEP: `second_line` reports the only neighbour trace as support 5, bodies 1, coverage 0.10, visible 0.27 — one partial letter body, not a word. 0.6 returned UNCERTAIN for the same reason.
These measures come from `greekocr/glyphs/baseline.py` (`text_lines`, `second_line`, `skew_line` with `cut_spans`, `cut_letters`, `crossings`) on the same `line_glyphs` pass the segmentation stage already runs. Build on them and on `greekocr/harvest/neighbour_words.py` (word runs) and the component roles from `greekocr/glyphs/components.py`. Do not write a new detector.

## Policy 0.7 (implement exactly this order; new version, new policy sha; the predictor and the length thresholds stay byte-identical)
**Stage A — line inventory (crop-only, always computed, page context optional).** For the crop in the measurement frame:
1. All rows: `text_lines` (up to 3 per side) — for each row record side, votes, visible fraction, coverage (supported x-range / width), letter bodies ≥60% visible (`second_line`-style count per band), and whether the row is *complete* (a full printed line: bodies across most of the width with high visibility — derive the rule from the existing `second_line` fields, state the thresholds).
2. Whole-word count per non-main row, crop-only: group that band's neighbour-role components into words by gaps (use the `neighbour_words.runs` grouping or the same gap logic; state which); a group is a **whole word** when it has ≥2 letter bodies each ≥60% visible and does not touch the left/right crop edge; otherwise it is a **cut-off word**. Record whole and cut-off counts per row. When page context IS available, also record the existing reconciled count, and report the agreement between the two on the replays — but the decision must not require context.
3. Main row cut-off: `skew_line` cut evidence — `crossings` (letter bodies leaving the crop), `cut_spans` with their `min_visible`, `cut_letters` with `body_cut`/`touches`. Record all of it.
**Gate (decides before any length measurement):**
- DROP "target line cut": a baseline crossing out of the crop, or any cut span where the letter body visibility falls below 0.6, or a de-skewed (row-frame) box taller than the upright box (clipped ink; the 0.6 guard).
- DROP "second complete line": any non-main row is complete.
- DROP "too many whole neighbour words": whole words over all non-main rows > 2.
- UNCERTAIN only when no main row is found or the orientation is unresolved (as today).
- Otherwise PASS to stage B.
**Stage B — length (only after PASS):** the 0.6 row-frame tight box of the main row's text components; long side vs OCR output through the unchanged predictor and 0.5–1.5 thresholds; the 0.6 padding input unchanged. Reasons must name the stage ("gate: …" / "length: …").
**Evidence:** `evidence.lines` = the inventory (one record per row with all fields above), `evidence.gate` = {verdict, reason, whole_words, cutoff_words, complete_rows, main_cut}, then the 0.6 `box_evidence`/`padding_evidence`. The owner sheets will render this, so keep it flat and complete.

## Checks
- CP1 (design note, ≤1 page, `segeval1/gate/DESIGN.md`, written BEFORE coding): which toolkit function gives each field, the completeness and whole-word thresholds you chose and why, and the two witnesses walked through by hand with the numbers.
- CP2 unit tests: the two witnesses (DROP / KEEP with the right gate reason); a synthetic crop with a complete second line (DROP); one with three whole neighbour words (DROP) and one with two (PASS); a θ=0 clean line whose stage-B numbers equal the 0.6 values to the digit.
- CP3 replay on the 150 (`segeval1/crops`, decisions `keys/sealed_decisions.jsonl`, reader answers `scored/owner_rows.jsonl`): score against the OWNER STANDARD, where a line is faulty if the reader set any of multi_line / neighbour_whole_word / rotated / horizontally_missegmented = yes OR any of the error codes extra_text, missing_word_or_span, crop_clipped, merged_two_lines (crop_overrun alone is NOT a fault). Report the confusion table (REJECT/ACCEPT/UNCERTAIN × fine/faulty/unresolved) for 0.5, 0.6 and 0.7 side by side, and a flip table 0.6→0.7 with gate reason, whole/cut-off word counts, main-cut evidence, reader state and detail. `segeval1/gate/replay_segeval1.jsonl` with full evidence per row.
- CP4 replay on the 888 calibration crops as in SEG-DESKEW-1 (`deskew/replay_calibration.py` pattern), with owner ratings; flip table 0.6→0.7 and agreement with owner ratings where rated. `segeval1/gate/replay_calibration.jsonl`.
- Scope guard as before: diff limited to the segmentation stage, crop-tools features, the policy script (new sha, version 0.7), versions builder; predictor and length thresholds byte-identical; pre-existing edits untouched.

Hand-off `segeval1/gate/HANDOFF.md` (sections: design, tests, 150 confusion tables, flip tables, 888, open issues, context-vs-crop-only agreement); last line exactly:
`SEGGATE1: done | 150 owner-standard 0.7: FP <n>/50-rejects FN <n> UNC <n> | vs 0.6: FP <n> FN <n> UNC <n> | 888 flips 0.6->0.7 <n> | tests <n> passed | commit <sha>`
