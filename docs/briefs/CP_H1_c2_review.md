# CP-H1 cycle 2 — re-certification of H1 fix 1 (scoped). Reviewer: gpt-6.1-sol, xhigh.
ROLE: independent certifier; implementer ≠ certifier. No network, no background jobs. SANDBOX workspace-write only for pytest temp (TMPDIR=$PWD/.review_tmp; delete after); do not edit tracked files.
READ FIRST: docs/reviews/CP-H1.md (your cycle-1 HOLD), docs/briefs/H1_fix1_geometry.md, docs/reviews/CP-H1-FIX1.md (implementer's self-review), docs/harvest/PILOT_v1.md §"Fix 1 (offline re-gate)".
SCOPE: git range 5c8b39d..4af4fc5 — greekocr/harvest/{core,pipeline,readers}.py, tests/test_harvest.py, the re-gate sidecars under docs/harvest/pilot_v1/.
Evidence outside the repo: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/ (records.jsonl, pages/, pilot_review_images/).
MANDATE:
1. HIGH 1 (cross-column crops): confirm bands come from page gutters + box clusters, polygons are split at the gutter before gating, cross-band crops are rejected; re-run your
   cycle-1 example and 5 more two-column pages by eye (page renders): are real two-column body lines preserved and fused ones split/rejected?
2. HIGH 2 (neighbour slivers): confirm the intrusion measurement and thresholds (12% height / 30% width); re-run your cycle-1 example; check 10 random sampled lines that the new
   gate REJECTS (126 of 500 are now rejected, 2,012 extra rejects on 14,200) by eye: is each rejection justified, or is the gate over-strict? Report the count of unjustified
   rejections out of 10; if ≥ 3 are unjustified, that is a HIGH.
3. MEDIUM fixes: table gate (rules AND lattice) on the cycle-1 border page; test path portability.
4. Tests: `.venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest`; report counts.
DISPOSITION: BLOCKER/HIGH fixed before scale-up; MEDIUM/LOW logged. DELIVERABLE: markdown; verdict line; findings with path:line; by-eye table (line id → justified yes/no, why).
Last line exactly: `VERDICT: <PASS|HOLD> ... | BLOCKERS: <n> | HIGH: <n>`.
