# Line segmentation: tests and evidence

[Documentation index](../../shared/DOCUMENTATION_INDEX.md) · [Method](LINE_SEGMENTATION_METHOD.md) · [Implementations](LINE_SEGMENTATION.md) · [Current checked work](../../records/research/round8/LOOP_HANDOFF.md)

Tests answer different questions. A passing suite, identical exports, a good-looking overlay and an independently verified physical correction are separate kinds of evidence.

## What each check establishes

| Check | Existing location or record | What it establishes; limit |
|---|---|---|
| Package/API and compatibility tests | [tests/glyphs](../../../tests/glyphs/), especially page API and equality tests | Contracts, aliases and controlled regressions. Does not qualify the fast stack or every real page. |
| Fast-stack orchestration and numerical tests | [stack/test_stack.py](../../../prototypes/fast_lines/stack/test_stack.py), [features_geometry](../../../prototypes/fast_lines/features_geometry/), [features_ink](../../../prototypes/fast_lines/features_ink/) | Actual caller behaviour and specified numerical cases. Mocked calls do not prove native geometry. |
| Synthetic feature tests | Geometry/font fixtures within those suites | Known row, glyph, boundary and deformation relationships. Passing artificial pages is not generalization to scans. |
| Native counterexamples and mutation tests | Task reports, checked-in fixtures and task-specific replay evidence | The fix reaches a real consumer and a restored old defect fails the physical assertion. A test that copies the implementation formula or receives no proposals is insufficient. |
| Development-page visual review | Owner comments/row marks, native crop galleries and task reports | Complete rows and marks, exclusions, columns and curl. Every changed crop requires adjudication; a page overview or count is insufficient. |
| Replay/conservation comparisons | Source-bound export, ownership and stage receipts | Reproducibility and what changed or was lost. Equality can preserve an existing error. A threshold mask may miss weak ink. |
| Coordinator-held evaluation | Private 44-page check, coordinator only | Independent generalization evidence. Workers and planner neither inspect nor run these pages. |
| Paired timing and work counts | Per-page/stage receipts, reversed-order runs | Actual cost, tails and removed computation. Report requested versus observed threads, startup and file-to-final boundaries. A faster stage may be offset downstream. |

The [Phase-1 validation report](../../records/verify_20261008/VALIDATION.md) is a dated package result, not the latest line-segmentation score. Likewise the [stack README](../../../prototypes/fast_lines/stack/README.md) contains historical R6/R7 measurements. Current source-bound claims belong to the latest report and independent check identified in the handoff.

## Cohorts and references

- **208 development pages:** the established fast-stack allowlist, comprising 195 plus 13 supplied review pages. Use the existing manifest/runner, not a new directory glob or newly selected favourable subset.
- **23 pilot pages:** the round-8 explicit-reference subset, not an independent test set. The original slow detector has saved runs; see the [generation record](../../records/research/round8/MODEL_GENERATIONS.md) for provenance and known errors.
- **44 held-out pages:** coordinator-only. Report the coordinator's supplied verdict without importing private images or using them to tune a worker.
- **Owner review ledger:** historical R7 contains 104 comments and 256 marked segments. Retain their original text, native coordinates and historical identities; changed row numbering is not a resolved case.
- **Synthetic controls:** record the construction and expected geometry. New tests for shared edge curl must include flat, skewed and known-curled surfaces; negative cases must not acquire a bend merely because the fitter can draw one.

PDF text and detector agreement are not physical ground truth. The first-generation renderer is an explicit comparison tool with known mistakes. Compare the same native ink and coordinates, not row IDs across different implementations.

## Positive coverage versus unchanged controls

GEOM-02 i5's experimental repair covered four rows of one page. Two crop windows and 26 phase/window combinations test robustness on that same page. The enabled 208-page comparison changed just those four polygons, so most pages supplied regression evidence, not positive evidence of the new repair.

Before adjusting each new physical feature, freeze a small multi-page, multi-book positive cohort, negative controls and previously unused development validation examples from the existing allowlist. Record why each example exercises the feature. Report corrected rows and pages separately from unchanged controls and unknown cases. Do not select only successful pages afterwards, call development validation an independent held-out set, or inspect the coordinator's private44. Wider evidence need not mean a new large corpus.

## Reproducing work

Run from the source head, environment and worktree named in the relevant report. `pyproject.toml` limits default pytest discovery to `tests/`; prototype tests require explicit inclusion. Examples of separate test scopes are:

```sh
python -m pytest tests/glyphs
python -m pytest prototypes/fast_lines
```

These commands document scope, not a claim that this checkout has every dependency or that a run occurred for this documentation change. Native replay and benchmarks use the existing task runner under its authorization. Follow the stack README and task-specific report for its allowlist, settings and receipt paths; do not substitute the old Q7 experiment runner for `Stack`.

The parked M17 Rust pilot at `953fc4a` belongs to another branch and has its own historical portability debt. The current `rust_field` numerical batch has source-bound bare-checkout verification: Python collects without a native build; an explicitly requested missing native library fails clearly. Its render-fixture glob still lacks an expected-fixture-manifest assertion. Neither pilot nor numerical parity establishes a default speed gain.

The [15 October audit](../../records/research/round8/AUDIT.md) reconciles the final-source prototype suite: 430 passed / 15 strict xfails in the INK worker/checker worktree; bare 429 passed / one older local-image skip / 15 xfails. These are reused receipts, not package-suite counts or a new full-suite run by the auditor. The audit ran six focused Python render-through-certify fixtures, independently reconstructed every final crop mask and performed two uninstrumented full208 timing passes. Detector drift exceeded the comparison control; agreement40 is not a certified clean cohort. See [cost and limits](../../records/research/round8/AUDIT_COST.md).

## A result must be attributable

Each task should provide: source head/hash and switch configuration; input/native-image identities; environment and thread settings; existing/reference/candidate overlays; all changed crop and exclusion decisions; actual caller/mutation tests; paired timing where runtime changes; deleted decisions and migrated callers; open failures and best checked head. Mark default, opt-in and offline results separately.

Useful physical stages to render are **row/component assignment → class-conditioned font contacts/guides → shared edge geometry → facing-guide boundary → final crop**. Render the earliest failing stage instead of adding a new late filter. New work should use this sequence to judge progress; the recent separator trials did not yet fit the font guides.

## GitHub versus local evidence

Commit explanations, source references, test code and small permitted fixtures. Keep large/native scan collections and private evaluation material in their established evidence stores. In a report, record the source commit, relative evidence path and owning worktree; label local-only links. A GitHub reader must be able to understand the result without access to an absolute Mac path, even when the native evidence itself remains local. Repository publication or visibility changes are separate from this documentation reorganization.
