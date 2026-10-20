# SR1: migrate the lead's hand-run operations into tested toolkit tools (gpt-6.1-sol, medium, network OFF; no .git writes)

Workspace: THIS worktree (`opus/cleanup-1`). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`,
`PYTHONPATH=$PWD`.

**Spec:** `~/Projects/greek-ocr-toolkit-spellcheck/docs/SOL_ROUTING_spellcheck_20261017.md` §A, read-only. Migrate every row marked
**Migrate** (#1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 13) into tools with tests. The rows marked one-off or recurring-to-Sol need no code.

**Hard constraints:**
- No byte change to `greekocr/labelfix/**` or the 16 policy paths; digest 6f62925a stays. Prove it with the pinned sha table
  before/after.
- Additive only: new modules under `greekocr/adjudicate/` (and `greekocr/recogniser/` where it fits) and thin CLIs under
  `scripts/review/`.
- Existing scripts are not deleted. Where they are replaced, add a pointer in their docstring only if they are unpinned.
- Inputs from other worktrees are read-only.

## Tools (one module each, typed and documented, each with tests on small fixtures)

| # | Tool | Must reproduce |
|---|---|---|
| 1 | Page specs as data for `owner_sheet.render`; the page builders under `R2_evidence/page_builders/` become spec files | The re-emission tests from CU4 still pass. |
| 2 | `edit_evidence_crosstab` (per change: kind, head, slot, ink, verdict) | On the 101 audit changes. Pin the lead's slot-lookup bug: start `<` vs `<=`; it must give "with ink 38/38". |
| 3 | `release_census` (substitution tiers per wave, seeded sampler, single-line evidence dump) | Runs on a local fixture. The cluster use stays Sol-briefed (B9). |
| 5 | Named slices in the R2 scorer: capital / ALL-CAPS / numeral, ο-monotonic, subscript, exact-name | Implement in `greekocr.adjudicate.score` as a slice registry. Do NOT edit r2-prep's scorer here; give the patch for it as a file. |
| 7 | `controls_review_sheets` (≤12 per sheet: word zoom + expected form) | The CQ1 sheet layout. |
| 8 | `--batch-check` for answers vs a dealt batch (via the CU4 `protocol.resolve` dry run) | |
| 9 / 10 | `deal_batches` (isolated folders, no key reachable, reader-2 reverse, receipt with hashes; `mark` profile render) | Follow `protocol.deal` and the R2C/B6b deals. |
| 11 | `owner_notes_export` (artifact-db JSON dump → JSONL + card join + status convention per sheet) | The db read itself stays a lead action. |
| 12 | `truth_overlay add` (validates the tuple, parent, evidence paths; symmetric-rescore check) | Reproduce overlay v1.1 from v1 + the ἤγε evidence. |
| 13 | `artifact_custody` (copy + sha manifest + verify) | Used next by WT1's custody step. |

## Report

`docs/records/cleanup_20261017/CLEANUP_SR1_REPORT.md`:
- per tool: API, tests, and what it replaces;
- the pinned sha table and digest;
- the full suite, with pre-existing failures only (the sandbox socket error is reported separately);
- `docs/API.md` regenerated for the new callables.

Last line: `SR1 READY: tools <n>/11; tests <n> passed; pinned unchanged <k>/<k>; digest 6f62925a yes; suite pre-existing only <yes|socket-only>`.
