# H1 fix 1 — CP-H1 HIGH 1 + HIGH 2 (+ MEDIUM table-gate borders, MEDIUM test path) in greekocr/harvest (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). No network, no Google calls, no `.git` writes. Do NOT rerun the pilot or touch docs/records/harvest/pilot_v1 outputs;
this is a code fix with tests, certified by a re-review before any scale-up.
Review: docs/records/reviews/CP-H1.md (read all findings). Plan §H1: ~/Projects/glossapi-development/docs/experiments/glossapi_improvement_20261006/PLAN_GLOSSAPI_v3_20261007.md.
Evidence lives outside the repo: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/ (records.jsonl, pages/, pilot_review_images/, google/).
Required:
1. HIGH 1 — cross-column crops receive labels (greekocr/harvest/core.py ~line 82: one band inferred from already-fused polygons; horizontal joining ~line 79 preserves the
   fusion). Fix: derive column bands from the page (the stack's column/gutter information or the page's box x-extent clusters), split any polygon that spans two bands at the
   gutter BEFORE gating, and reject (gate reason `crosses_column`) any crop whose x-extent covers more than one band by > 15% of the band width. The list-return join must
   never join pieces across a gutter. Reproduce on the reviewer's example and add it as a regression fixture (page + polygon → expected split/reject).
2. HIGH 2 — neighbour slivers pass the pre-Google gate (pipeline.py ~line 238 ignores fitted neighbours below 50% visibility; reviewer example `1697d5cc… p106 l41`). Fix:
   compute the fraction of the crop's height occupied by ink that belongs to the neighbouring rows (above/below the fitted body band) and reject when a neighbour's ink
   intrudes more than 12% of the crop height or its x-span covers more than 30% of the crop width; record `neighbour_sliver` with the measured fractions. Regression fixture
   from the example.
3. MEDIUM — borders falsely trigger the table gate (core.py ~111, example `0cb3f672… p20`): require BOTH long rules AND a box lattice (short boxes aligned in x and y) for
   `page_table`; a page frame alone (rules only at the margins, no lattice) is not a table. Fixture from the example.
4. MEDIUM — tests reference an absent archived fetcher (tests/test_harvest.py ~128): point the test at the vendored copy or a fixture; no absolute paths outside the repo.
5. Re-run the gate stage OFFLINE over the stored 14,200 records (no Google) and report how the gate counts change (before/after table in docs/records/harvest/PILOT_v1.md addendum
   "Fix 1 (offline re-gate)"); do not change tiers or labels of the 500 sampled lines except to mark any that the new gates would now reject (add `post_fix1_gate` field in a
   sidecar file, not by editing records.jsonl).
6. Tests: `.venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest` green; INVENTORY for fixtures.
Last line exactly: `H1FIX1: done | regated_rejects_added: <n> | sampled_now_rejected: <n> | tests: <n> passed`.
