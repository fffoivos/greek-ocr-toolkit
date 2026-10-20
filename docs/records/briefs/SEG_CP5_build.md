# SEG-CP5: qualify orientation and horizontal structural cases separately (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Authority.** This executes **CP5 of the ASTRA-SEG1 plan, exactly as written**: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md`, §"Numbered PLAN", item 5. Read the whole review first (findings F1–F3, §§1–6, and the plan). The deliverable, tests, Sol review criteria and acceptance numbers are the review's. Do no later-checkpoint work.

**Earlier checkpoints are committed** (CP1 eac7ca91: the frozen truth ledger `docs/records/harvest/collect_v3_admission/seg/calibration_ledger.json`, the union gate, GATE_FAIL). The NW drafts (`greekocr/harvest/neighbour_words.py`, the `admission.py` and stage_crops edits) are uncommitted drafts: build on them or replace them as the plan requires.

**Owner standard (verbatim):**
- "the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well";
- "In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration".

**Use the toolkit's existing segmenter tools** (`greekocr/glyphs/*`; the collector's `collect_v3/vendor/geometry` read-only). Add no new detector, no ownership retuning (`801d517e` frozen) and no masking.

**Forbidden:** publishing, re-issuing or modifying any admission file, `crops_manifest.jsonl` or crop PNG; writes or locks in the live run root `~/Projects/collect-v3-data/run` (read only). The byte-exact interpreter is `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.

**CP5 notes:**
- CP2–CP4 are committed (81e7756c): the geometry adapter, supported row inclusion, body-aware neighbour words, and `geometry_unavailable` fail-closed.
- The ledger is `seg/calibration_ledger.json` (sha 76ea2d35…).
- Rotated positives: `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/w1_rotated_crop_ids.txt` (1,681 historical heuristic ids). Audit them as the plan says; do not grandfather them blindly.
- **Also review the CP4c additions** (the `geometry_unavailable` rule in `admission.py`, the ledger re-freeze), which no separate Sol review has covered. Report any defect as a CP5 finding.
- The live root changes because of the collector materialize; see `seg/CP3_M1_lead_process_evidence.md`.

## Output
- Code and tests as the plan's CP5 states.
- `docs/records/harvest/collect_v3_admission/seg/CP5_RECEIPT.md`: every acceptance number from the plan with its measured value.
- `seg/CP5_COMMIT_LIST.json`: guarded, with file shas and base HEAD.

The last line must be exactly:
`SEG-CP5: done | acceptance: <k>/<n> met | <each acceptance number, short> | publish actions: 0 | tests: <n> passed`
