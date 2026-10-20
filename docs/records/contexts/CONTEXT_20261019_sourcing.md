# Context pack — "Sourcing for OCR experiments" lead (name unchanged)

Your scope narrows to sourcing proper. Your own hand-off: `docs/records/harvest/collect_v3_admission/HANDOFF_20261018_sourcing.md` and `MORNING_NOTE_20261018.md`.

**Important for you:** the admission screens you built (`greekocr.harvest.qualified_admission`, the CP ledger) are PARKED. The owner's pipeline on Clariden is the admission tool now, and its segmentation stage is the owner's three rules (0.8). Do not resume screen development. The segmentation tool, the cells branch and the census rerun are owned by the "Segmentation and secondary corrections" lead from today.

## What changed since your 18 October hand-off (coordinator, 19 Oct 13:45 Athens)

**18 Oct evening — the owner worked directly with Sol while the coordinator was at its usage ceiling.** Result: the line filtering + correction pipeline 0.2 on Clariden (`$W/filter_pipeline_20261018`; stages segmentation 0.5 → polytonic 0.7 (= sf7, candidate_pre_audit) → RU1 0.3 → N1 0.2; design in `~/Projects/ocr-review-sites-20261018/docs/FILTER_PIPELINE_IMPLEMENTATION_20261018.md`). Census runs: census_02 over all 592,466 sourced lines (0 ADMIT because of four integration defects; segmentation verdicts DROP 17,036 / UNCERTAIN 151,931 / KEEP 423,499); census_03 (job 3695426, done 07:08) = 65,900 train rows ADMIT — a skewed subset, because every row the correction tools could not verify is HELD by design.

**19 Oct — coordinator + owner, segmentation tool:**
- Blind check of segmentation 0.5 on 150 unseen lines (Sol reads crop + Google text side by side; scored on the OWNER STANDARD below): false rejects 26/50, misses 8/100. 24 of the 26 false rejects came from the length rule.
- 0.6 = text box measured in the detected row frame (de-skew), Sol commit 58978481 (`sol/seg-deskew`).
- 0.7 = line inventory → gate → length, but with two rules the coordinator added without being asked (a height guard, a "target line cut" test); the owner rejected them: "stop adding rules I didn't tell you to".
- **0.8 = exactly the owner's three rules** (commit 410f4566, branch `sol/seg-gate2`, 157 tests, hand-off `docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md` in the sol-recut worktree): (1) other lines: >2 whole words from other rows or a second complete line = DROP, cut-off words do not count; (2) de-skewed main-line box, long side normalised by its own height, vs Google output through the unchanged predictor, 0.5–1.5; (3) crop height ≤ upright box height + 1.5 × de-skewed line height. On the 150: false rejects 18, misses 11, HOLD 11; agreement with the owner's 135 rated calibration lines 94 (0.5: 98).
- Numeric cells: 39,014 of the census rows are numeric output + small image (≤200×40 px, ≤10 chars), all in W1/W2 (gazette 21,489, elstat 12,626); 0.5 drops 2,419 of them and holds 5,068. Short numeric crops follow their own width/height-vs-characters line (0.46·chars + 0.79, spread 0.63) against text lines (0.39·chars + 2.0, spread 3.1), so the text-line model expects every short numeric crop to be wider than it is. Files: `segeval1/cells/` (Sol, branch `sol/seg-cells`, commits 7350e39c + 84fe2099, whole-census table `population_cells.jsonl.gz`, 250 byte-exact sample crops) and `segeval1/cells_opus/` (Opus study: `size_vs_output.md`, `short_non_numeric_typology.md`). The cell RULE is not decided; the owner is reviewing the sheet.
- Experiment A is PREPARED, not launched (greek-page-ocr-wave1c worktree, commit 6c9bf96; `out/e4/expA_prep/SUBMIT.md`; two variants: full filter 0.5 drops 3,405 rows / without the length rules 1,770; RU1 edits bound; sf7 switched off until its audit passes). Waits on the owner's go and variant choice.
- Wave 1c result (18 Oct): RU1 corrections validated as a label tool (ъ recall 104→127/144) but not a CER lever. Label versions are edits-only files over the raw Google import. Canonical rollout scanner v4.5.5 adopted (`opus/sol-reading` ec200b87).

**Owner review sheets (claude.ai artifacts, marks autosave):** the 150 lines https://claude.ai/artifact/CCD2D9pnygnnLZCxN7ZLns · de-skew flips https://claude.ai/artifact/P46d9fCCp5bRKwvzLEiPLC · numeric cells and short crops https://claude.ai/artifact/3UHaheQNiGry5jz6MNaVNd · gate sheet https://claude.ai/artifact/QMMk5RiEnbUAPadhoUGSho.

## Standing rules set by the owner on 19 Oct (apply to everything you do)
1. **Segmentation standard for a good crop:** (a) exactly one central line; (b) the Google text matches the visible line exactly, neither more nor less; (c) no other line shows completely and at most 2 WHOLE words from other lines, where whole = 100% visible — a readable but cut word is a cut-off word and does not count. Partial neighbour letter bodies alone are fine.
2. **A tool is exactly the owner's rules.** Never add a guard, test, threshold or heuristic to an owner tool on your own. Anything extra goes into the evidence record as a diagnostic only and onto a sheet as a question.
3. **Gate before length:** line inventory and the other-lines gate decide first; the length rule only runs on crops that passed.
4. **Review sheets:** cards show crop + text together; only the LAST TWO tool versions per card; the outer border is the owner's mark (space toggles KEEP ↔ DROP, no empty state), an inner frame of the same thickness is the latest tool verdict; ↑↓ move, z zooms, hover lens; marks and notes autosave to the artifact database under stable ids; never write to the database on page load; dump marks before every republish. Reference builders: scratchpad of the coordinator, being moved into `greekocr/adjudicate` (design doc in progress at `~/Projects/greek-ocr-toolkit-review/docs/review/`).
5. Unchanged: Sol executes everything (code, CLI, replays) from briefs with checkpoints; leads never submit Clariden jobs (the coordinator verifies deploys and submits); no launch without the owner's explicit go; no pushes; Athens time, stamped from `date`; the Mac is not a bulk worker without the owner's per-run permission; report one line per completed task to the Fable coordinator (SendMessage) and send a numbered plan before starting.

## Priorities after the CSCS filters and corrections (owner, 19 Oct)
P1. Segmentation 0.8 (+ the numeric-cell branch once the owner decides its form) → rerun the census so the admission file reflects it (coordinator submits).
P2. Experiment A: retrain the best model on the same rows, filtered and corrected by the latest tools, to verify the tools improve the training data (launch on the owner's go).
P3. Experiment B: the planned data-scaling runs with the W1/W2 rows, after the final admission file, the original-crop uploads and the W1/W2 split allocation.
P4. Correction releases feeding A/B label versions: sf7 polytonic (audit → release + test counterpart), capitals package.
P5. Owner decisions still open: the cell rule; whether a letter touching a side edge ("end clip") is a fault; adopting 0.8 for the rerun.

## What is still yours
- The inputs experiment B needs from sourcing: the ORIGINAL W1/W2 crops on Clariden (the pipeline reconstructs crops in memory from cached pages; the W1/W2 crop directories do not exist there — see `segeval1/cells/HANDOFF.md` and `SEGCELLS1B`), the Gazette and BSB admissions, and the edition-level W1/W2 split allocation (owner decision still pending).
- The Mac geometry preparation (`seg/cp7/launch_population_geometry.sh`, 3,057 pages) only if the owner gives the per-run go; it is no longer on the critical path unless the owner says the release-v3 file is still wanted alongside the census admission.
- Your worktree carries five uncommitted edits (`.gitignore`, `test_stage_crops.py`, `geometry_observations.py`, `row_inclusion.py`, `pyproject.toml`): decide whether they are yours and commit or revert them on your branch — Sol has been told not to touch them. Also: `sol/seg-deskew`, `sol/seg-gate`, `sol/seg-gate2`, `sol/seg-cells` were imported into this repo today from Sol bundles; leave them alone.

## Your first task
Send the coordinator a numbered plan (no Sol brief before it is acknowledged) covering: (1) what experiment B needs from you and in what order, with the owner decisions each item waits on; (2) the state of BSB resume 2 and the Gazette admissions; (3) the uncommitted edits. Then one line per completed task to "Fable coordinator".
