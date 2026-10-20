# L1M — Does masking foreign ink remove the detector's safety holds? (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-l1` (branch `opus/spellcheck-l1`). No `.git` writes. Do not touch other worktrees. Analysis
only; the release gate is FROZEN at `sf4-release-v1` (code in `~/Projects/greek-ocr-toolkit-spellcheck` at c6064650 — import it read-only via
`PYTHONPATH`, or copy the needed modules into a scratch dir; never modify it). Mac CPU, 200 lines (within the ≤ 10k rule). Clariden: only to
fetch the per-line saved evidence for these 200 lines (small extract, streamed on the login node; ≤ a few minutes; else STOP). SSH transient
errors retry ≤ 3; auth/cert error STOP; never refresh the cert.

## Staging
The 200 are ready (`l1e_sample_r3/`: 186/186 pages, 199/200 masked, 174/200 crops changed, own-ink loss 0 px on 190/196 measured lines).
The 60 vouli (`l1e_sample_vouli/`) may still be running: if its `receipt.json` is absent or incomplete when you reach that step, run the 200
and make the vouli stratum a one-command rerun (`--sample vouli`) that appends to the report; state "vouli pending" in the result line.

## Question (coordinator, 17 Oct)
Under the complete gate L1E keeps only 9.7% of training lines; a 1,024-line pilot shows `localisation_unknown` dominates (≈ 8k of ≈ 9k hold
entries; A/B disagreement only 129). Hypothesis: foreign (neighbour-line) ink inside the crop breaks the detector's component ownership. Test:
run the SAME detector (S6/SF4 code) on the original vs the sourcing lead's MASKED crop of 200 held lines, keeping the reader evidence fixed.

## Inputs
- Line ids: `docs/records/labelfix/spellcheck/L1M_masking_sample_ids.txt` (200: round1 80, round2 60, mixed 60) plus
  `L1M_masking_sample_ids_vouli.txt` (60 vouli); all ENSEMBLE_AB-held in L1E 3679545, seed 20261017. Report vouli as its own stratum.
  **Limit (state it in the report):** parliament is not sampled (two-column neighbour matching unsettled); no projection to parliament.
- Masked crops: `~/Projects/collect-v3-data/v2_masked/l1e_sample_r3/` (the 200) and `…/v2_masked/l1e_sample_vouli/` (the 60), each with
  `crops/<wave>/<doc>/<file>.png`, `lines.jsonl` (old box, foreign pixels removed, own pixels lost, match status, audit status — 'unknown'
  audits stay in, reported separately) and `receipt.json` (from the sourcing lead's T6d run: masked crops beside originals, per-line
  records with foreign pixels removed / own pixels lost, receipt; lines whose matching failed are left unmasked and recorded — report them
  separately, don't drop them).
- Original crops: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/` (read-only).
- Recogniser alignments: `.cache/labelfix/clariden/C1_alignments.jsonl.gz` for C1 lines; for the other lines, extract them from the L1 job's
  alignment output on Clariden (`labelfix_l1_20261017/output_3679313/alignment/`).
- A/B/E predictions + coverage: from L1-v0 `output_3679313/combined/` (A) and L1E `l1e_20261017/output_3679545/inference/` (B, E) on Clariden —
  extract only these 200 lines.

## Do
1. For each line: S6/SF4 `read_ink` on the original crop and on the masked crop (same recogniser text + alignment, same reader evidence).
   Count per line and in total: `localisation_unknown`, `segmentation_uncertain`, `clipped_top`, `clipped_bottom`, unnamed, components per
   letter.
2. Compose both under the frozen gate (`release_gate.compose_runtime`, policy sf4-release-v1) in PRESENCE and ENSEMBLE_AB; report lines held
   before/after, lines kept-and-corrected (label changed) before/after, and slot hold reasons before/after.
3. Stratify by wave and by the sourcing record (foreign pixels removed: none / small / large; matching failed). Note: masking can also remove
   own pixels — report own-pixel loss and any new localisation failures it causes.
4. A 12-panel visual check (original vs masked crop, the detector's letter components) for lines whose verdict flips, inspected yourself.

## Border-blob attribution (coordinator, binding)
For EVERY clipped_top / clipped_bottom flag on the 260 lines (original crop): identify the border-touching blob(s) behind it and attribute
each to THIS line or to a NEIGHBOUR line using `greekocr/glyphs/recut.py::_voronoi_keep` ownership (the sourcing lead's `lines.jsonl` carries
the per-line ownership/foreign-pixel masks — use them; where a blob's attribution cannot be determined, mark it `undecidable`, never guess).
Report flag counts before/after masking split by attribution (neighbour / own / undecidable), per wave. Interpretation to state explicitly:
neighbour-owned border blobs → masking removes the flags legitimately; own-line blobs (this line's accents/breathings touching a too-tight
crop top or descenders at the bottom) → masking cannot help; the fix is crop padding at cut time (a different decision). Give both numbers.
Visual check: 12 panels split across neighbour-owned and own-line attributions, inspected yourself.

## Read against the census
Include `docs/records/labelfix/spellcheck/L1C_census_3679781/AB_SF4_SUMMARY.md` (population per-wave hold reasons under sf4) in the report and read
the masking verdict against it: e.g. if masking clears clipping on the sample, project how many of the population's clipping-only lines
(≥ 30,280) and clipping+localisation lines it would release, per wave — stating the projection's assumptions.

## Deliverables
`docs/records/labelfix/spellcheck/L1M_REPORT.md` + evidence; last line:
`L1M RESULT: 260 lines (masked <m>, matching-failed <f>); localisation_unknown slots <a>→<b>; segmentation_uncertain <c>→<d>; clipping <e>→<f> (border blobs neighbour <n1>% / own <o1>% / undecidable <u1>%); AB lines held <g>/200→<h>/200, corrected <k>→<l>; PRESENCE <i>→<j>; verdict: <masking fixes most | partial | does not>`.
