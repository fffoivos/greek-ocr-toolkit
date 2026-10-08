# CP-G3 — certification

**HOLD.** [Full review with reproductions, raw failures and fixes](CP-G3_review_1.md).

## Findings

Four HIGH findings require fixes before S3:

1. `components.py:96` — faint-ink filtering deletes legitimate letters.
2. `lines_api.py:77` — missing rows are attributed to both crop edges.
3. `report.py:131` — flattened records omit column offsets and identity.
4. `build_review_data.py:66` — the unchanged builder crashes with `KeyError: 'baseline'`.

The report also documents five MEDIUM/LOW findings covering None priors, sparse rules, over-inked capitals, neighbour metrics and capitals cohort wording.

## Claims re-derived

- **43 committed tests pass; seven independent regressions fail.**
- **40/444 crops split**, including all required owner examples.
- Neighbours: **167/199 matched**, 32 missed.
- Capitals: **2,057 scored across 118 lines**.

## Cleared

CP-G2’s peak-search, two-speck, vanished-count and singleton fixes reproduce. Required owner column decisions and numeric straightening checks pass. All **27 scoped file hashes remain unchanged**.

VERDICT: HOLD Fix faint-letter deletion, cut-edge attribution, flattened coordinates and builder compatibility before S3. | BLOCKERS: 0 | HIGH: 4