# SEG-CP4: make neighbour-word evidence body-aware and local (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Authority.** This executes **CP4 of the ASTRA-SEG1 plan, exactly as written**: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md`, §"Numbered PLAN", item 4. Read the whole review first (findings F1–F3, §§1–6, and the plan). The deliverable, tests, Sol review criteria and acceptance numbers are the review's. Do no later-checkpoint work.

**Earlier checkpoints are committed** (CP1 eac7ca91: the frozen truth ledger `docs/records/harvest/collect_v3_admission/seg/calibration_ledger.json`, the union gate, GATE_FAIL). The NW drafts (`greekocr/harvest/neighbour_words.py`, the `admission.py` and stage_crops edits) are uncommitted drafts: build on them or replace them as the plan requires.

**Owner standard (verbatim):**
- "the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well";
- "In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration".

**Use the toolkit's existing segmenter tools** (`greekocr/glyphs/*`; the collector's `collect_v3/vendor/geometry` read-only). Add no new detector, no ownership retuning (`801d517e` frozen) and no masking.

**Forbidden:** publishing, re-issuing or modifying any admission file, `crops_manifest.jsonl` or crop PNG; writes or locks in the live run root `~/Projects/collect-v3-data/run` (read only). The byte-exact interpreter is `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.

**CP4 notes:**
- CP2 (geometry adapter) and CP3 (supported row inclusion, with rows of invalid geometry marked unavailable explicitly) are committed; build on them.
- The gate is CP1's ledger (22 KEEP, the DROP set).
- The live run root changes during this work: the collector `materialize` (pid 50737) writes and discards W2/crops and cache/g1b. That is not SEG activity; see `seg/CP3_M1_lead_process_evidence.md`. The Sol sandbox cannot run `ps`, so state assurances as 'no write by SEG code'.
- **Owner standard for a positive:** at least one whole word from a neighbouring line visible. Half-letters at the edge never drop.

## Output
- Code and tests as the plan's CP4 states.
- `docs/records/harvest/collect_v3_admission/seg/CP4_RECEIPT.md`: every acceptance number from the plan with its measured value.
- `seg/CP4_COMMIT_LIST.json`: guarded, with file shas and base HEAD.

The last line must be exactly:
`SEG-CP4: done | acceptance: <k>/<n> met | <each acceptance number, short> | publish actions: 0 | tests: <n> passed`
