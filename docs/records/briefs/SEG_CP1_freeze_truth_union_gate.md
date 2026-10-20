# SEG-CP1: freeze truth and make the gate describe the actual union (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Authority.** This executes **CP1 of the ASTRA-SEG1 plan, exactly as written**: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md`, §"Numbered PLAN", item 1. Read the whole review first, especially F1, §5 "Calibration, provenance and the release gate", and the plan. The deliverable, tests and acceptance numbers are the review's. Do not add work from later checkpoints (CP2–CP7).

**Owner standard (verbatim):**
- "the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well";
- "In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration".

## Worktree state you start from (uncommitted; sort it first)
- **NW1/NW1b drafts.** These were stopped and superseded by this plan: `greekocr/harvest/neighbour_words.py`, the edits to `greekocr/harvest/admission.py`, `tests/test_neighbour_words.py`, the edits to `stage_crops.py`/`test_stage_crops.py`, `docs/records/harvest/collect_v3_admission/nw1/` and `nw1b/`. They are a **draft**. CP1 changes `nw1b/calibrate.py`, `prepare_w1.py`, `reissue.py` and their tests, as the plan says.
- **ADM5b/ADM5c leftovers** that were never committed: `tests/test_adm5b_schema.py`, `tests/test_adm5c_variants.py`, `greekocr/_vendor/codec/v2.json`, the `.gitignore` edit, and `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017*`. Check whether they belong to the committed ADM5c state (84b5df8d). If so, list them in a **separate** commit group `ADM5c-leftovers`, apart from the CP1 group.
- **Never** re-issue, overwrite or modify any admission file (`w1_originals_v3_admission.jsonl`, `_admitted.jsonl`, `_receipt.json`) or `crops_manifest.jsonl` / crop PNGs. **0 publish actions** is an acceptance number. The run root `~/Projects/collect-v3-data/run` is live: read only, no locks.

## Truth for the ledger
- **22 KEEP, 1 borderline and the DROP set:** exactly as listed in `docs/records/briefs/NW1b_neighbour_words_recalibrated.md` §2. The owner's "true issue" cards come from his segmentation-sheet review; the eighth id is unidentified and must stay marked as such unless you find it with provenance.
- **C1 and gallery witness lists:** keep them separate, as the review asks: `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/` and `segmentation_gallery/`.
- **The pre-screen population:** the collector's builder `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/build_w1_originals_v3.py` (read-only).

## Output
- Code and tests as the plan's CP1 states.
- `docs/records/harvest/collect_v3_admission/seg/CP1_RECEIPT.md`: each acceptance number from the plan with its measured value, the ledger path and sha, the commit list.

The last line must be exactly:
`SEG-CP1: done | KEEP unique: <n> | DROP published: <n> (provenance ok) | union failure detected: <x>/22 | publish actions: <n> | regression incl. 4 ids: <yes/no> | tests: <n> passed`
