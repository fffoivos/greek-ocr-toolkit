# SEG step 4: small segments are measured by their all-ink box (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits. HEAD contains step 3
(0.9-s3, `docs/records/harvest/seg_steps/s3/`). Use the new output directory `docs/records/harvest/seg_steps/s4/`. Same untouchables as before:
`seg_census/package/`, `seg09/`, and the untracked census02 evidence (read only).

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. A tool is EXACTLY the owner's
  rules; never add a guard, test, threshold or heuristic; extras are diagnostics only.
- `docs/records/harvest/seg_steps/s3/REPORT.md`, `s2/REPORT.md` and `s1/REPORT.md`. Reuse their replay and scoring workflow unchanged.
- `sol-recut segeval1/small_segments/SMALL_SEGMENTS.md` and `q1/Q1_TABLES.md` (read only).

## The single change (owner, 19 Oct; definition adopted)

This is version **0.9-s4**, built on 0.9-s3.

- **Small segment** = Google chars ≤ 8 AND A ≤ 6.
  - A = crop long side / crop short side, on the crop's pixel dimensions; it is rotation-invariant.
  - Chars = the same saved Google character count the length rule uses.
- **For a small segment, the text box comes from ALL ink components:** no roles, no x-height, no row frame.
  - The box is the axis-aligned bounding box, in the crop as processed (after the step-2 turn), of every ink component that the
    existing component extraction finds: marks, dots and specks included.
  - Long side = its width; short side = its height.
  - Rule 2 (length 0.5–1.5) runs the unchanged predictor on that box.
  - Rule 3 (padding ≤ 1.5) uses that box's height as both the box height and the row-frame height.
- Non-small segments are processed exactly as in 0.9-s3.

**Lead ruling on the gate for small segments.** Rule 1 (other lines) is unchanged and runs first. Some 0.9-s3 abstentions come
only from the row machinery, which the owner replaced for small segments:
- `no row with observed support`;
- `no usable text box`;
- `neighbour extent unresolved` when no main row exists.

When a small segment's gate outcome is one of these, the gate does not decide, and the segment goes on to the all-ink length and
padding. A gate DROP (a second complete line, or >2 whole words) still drops.

Diagnostic: report how many small segments this ruling moves, and what their verdicts would be if they had stayed UNCERTAIN.

## Do

1. **Implement, with tests:**
   - chars 8 / A 6.0 is small; chars 9 is not; A 6.01 is not;
   - the all-ink box includes an isolated speck and a diacritic;
   - non-small rows are byte-identical to 0.9-s3;
   - a turned (h > w) small crop uses the turned box.
2. **Replay** 0.9-s4 on the **150**, the **888** and the **250**, scored exactly as in steps 1–3:
   - the 150: FP/FN/UNC;
   - the 888: rated agreement /135;
   - owner marks: /235, latest mark wins.

   Show the columns 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 | 0.9-s4. Give flip tables for s3 → s4: every changed verdict with the owner
   label or mark, chars, A, and the old and new box.
3. **The typology set.** Replay 0.8, 0.9-s3 and 0.9-s4 on the Small-segment typology crops.
   - `SS=~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/small_segments`. Everything there is
     read only.
   - **Inputs:**
     - manifest `$SS/samples.jsonl`: line_id, crop_path, text, width, height, chars, A, final_type, final_class, label_ok, control;
     - crops `$SS/crops/`, 437 PNGs, sha256-verified;
     - `$SS/sheet/card_manifest.json` lists the 417 sheet cards. Exclude the 20 `control=true` rows from scoring; replay them too.
   - **Owner marks:** use `$SS/owner_marks_smallseg.jsonl` if it exists, in the owner_marks_20261019 format. Otherwise read the
     newest timestamped folder `$SS/sheet/marks_dump/*/notes/*.json` (at 20261019T1827: 185 files, 177 KEEP / 8 DROP). The latest
     mark wins. Record which source and which dump you used.
   - **Report:**
     - agreement per `final_type` / `final_class` group and overall;
     - the confusion table per version;
     - the 0.9-s4 verdicts on the owner's 8 DROPs (4 noted "wrong Google output", 4 text=wrong), which are label faults, not box
       faults.
   - **Diagnostic only:** cross-tab the 0.9-s4 verdicts against the length-exempt classes in `$SS/NOTE_steps45_length_exempt.md`
     (punctuation-only, non-text, CJK, faults). Add no rule for them.
   - If any input is missing, do the rest and say so.
3b. **Owner question: "numeric only, or all small?"** This is a diagnostic only; the rules stay as above.
   - **Population:** every small crop (chars ≤ 8 & A ≤ 6) that has an owner judgement. Take that judgement from:
     - the typology marks (step 3);
     - `owner_marks_20261019.jsonl` (cells 152, gate, de-skew);
     - the 888 owner ratings (135).

     De-duplicate by line_id; the latest explicit mark wins over a rating. List the conflicts.
   - **Split by output type** (numeric / mixed / non-numeric), using the SAME output-type definition as
     `sol-recut segeval1/cells_opus/size_vs_output.md` and `small_segments/q1`. Say which function you used.
   - **For each type, a 2×2:**
     - **Box:** {the 0.9-s3 text box, the all-ink box (0.9-s4)};
     - **Expected length:** {the unchanged text-font predictor, the short-numeric line}.
   - **The short-numeric line: refit per box (coordinator correction).** Never apply a line fitted on crop dimensions to a
     box measurement.
     - **Refit per box type.** For each of the two box types, refit `ratio = a·chars + b` (OLS, the same form as
       `cells_opus/size_vs_output.md`) on the small NUMERIC crops measured with THAT box.
       - The census crops are not local, and no census run is allowed. So fit on EVERY locally available small numeric crop: the
         150 + 888 + 250 replay crops, the 437 typology crops, and any other crop set under
         `sol-recut segeval1/` whose PNGs are present and sha-verifiable. Read only, no fetching.
       - List the sources and the n.
     - **In-sample check.** Report each fit twice: on all those crops, and on only the crops WITHOUT an owner judgement.
       - Use the fit without owner-judged crops in the 2×2.
       - If its n < 100, say so and also give the all-crops version.
     - **Spread.** Report a, b, the residual SD, the MAD and n per box, next to the crop-dimension reference 0.460·chars + 0.787
       (SD 0.634, MAD 0.236, n = 36,307).
     - **Rule-2 test with the refit line.** A box with ratio r predicts pred = (r − b) / a. Then apply the SAME rule-2 test,
       (chars+1)/(pred+1) in 0.5–1.5, with the gate and padding exactly as in that box's version.
     - **The text-font predictor** stays as is: it was fitted on text boxes.
   - **Report:**
     - per type and per cell: the n, and the owner agreement, KEEP/DROP/UNCERTAIN vs owner KEEP/DROP;
     - the n of every fit;
     - a flag on any 2×2 cell with fewer than 30 numeric crops, marked "indicative only";
     - the flips between the two boxes (at a fixed expectation) and between the two expectation lines (at a fixed box), each with
       the owner mark;
     - a short factual paragraph on which cells agree best with the owner, per type. Make no recommendation.
4. **Small-segment diagnostic** on all replay crops:
   - the number of small segments;
   - verdict transitions s3 → s4 by reason;
   - the all-ink vs 0.9-s3 box ratio distribution;
   - the huge few-char blobs (e.g. '*****' 439×427): their verdicts.
5. **Readback:** every non-small row replays byte-identical to step 3. Include a scope guard listing the changed source files.
6. **Report** in `docs/records/harvest/seg_steps/s4/REPORT.md`, plus `flips.jsonl`, `typology_replay.jsonl`, `small.jsonl`,
   `summary.json` and a receipt. Update `tool_versions.json` as before.

**Last line:** `SEG S4 READY: small <n> of 1288 replay (+<n> typology); gate-abstain moved <n>; 150 FP/FN/UNC <s3> → <s4>; 888 rated agree <n> → <n>/135; owner marks agree <n> → <n>/235; typology owner agree 0.8 <n> / s3 <n> / s4 <n> of <N>; 2x2 best cell per type <numeric/mixed/non-numeric>; flips <n>; tests <n> passed`
