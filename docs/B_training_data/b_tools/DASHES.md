# Dash tagger — 0.1

## Purpose

Record dash occurrences without changing labels. The authoritative `docs/harvest/line_pipeline/tool_versions.json` names **dashes 0.1**, one generation, scope **tag only**. This is separate from N1's evidence-backed numeric separator substitutions.

## Owner rules it implements, quoted

`docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md`, under owner rulings:

> Dashes are tagged only; there is no track for them.

`docs/records/labelfix/secondary/PLAN.md` also records:

> Em dashes: tag only

These recorded rulings do not authorize general dash normalization or repair.

## Version history

| Version | Method / status |
| --- | --- |
| 0.1 | First dash tagging generation; no general repair release. |

The manifest's historical component path points to the integrated line-pipeline implementation's original worktree identity. It is not a second version or a later learned dash model.

## Inputs

Pipeline row/raw text, stable parent/id/split/crop hash, tool version/digest and optional observed/composed text. The route detector searches for literal `-` (U+002D), `–` (U+2013), `—` (U+2014), `−` (U+2212). Other Unicode hyphen variants are not implicitly folded into this list.

## Algorithm in prose

`routes()` adds the dash route if any listed character occurs. `automatic_result(...,"dashes",...)` scans the supplied observed text (raw by default), records each offset and literal character, and returns `tag_only` with an empty edit list. It records `coverage_text_sha256` separately from the raw parent hash, so tags on a composed view have an explicit coverage identity. It does not inspect pixels, classify stroke length or infer a different printed dash.

Result validation accepts tag_only **only for dashes**, requires nonempty evidence and correct tool/version/digest/binding, and rejects edits on any non-applied result. Other stages may still HOLD or DROP the row. A successful tag does not override a candidate release status, producer binding failure or another required unresolved route.

## Outputs and reason codes

The pipeline result has `status: "tag_only"`, `edits: []`, evidence `dashes: [{offset, character}, ...]` and policy text **`no qualified general dash repair`**. Stable binding and raw/coverage text hashes accompany it. No repaired text, replacement dash type or dedicated precision verdict is emitted.

## Evidence: review sets and owner marks

The secondary plan reports dash fault tags on **21/1,400 C1 cards**. This is a historical fault census, not an accuracy score for the literal tagger. The N1 dash-control lead review classified **27 strokes** by a one-digit ruler: **14 hyphen /6 en dash /5 em dash /2 unsure en-or-em**. The two unsure controls accept any dash type but reject non-dash answers. These controls qualify reader behavior within N1; the tagger does not consume them to perform repairs.

`n1_v1_train` has **0 edits /85 dash tags**, as recorded in `docs/records/labelfix/secondary/HANDOFF_20261018.md`. It is not a general dash repair release. No owner-mark confusion matrix or frozen precision/recall score for tagger 0.1 is supplied by the cited evidence. LQB has a `dash` class, but the current registry has no standalone dash-corrected label version whose delta would demonstrate repairs.

## Tests

`tests/test_line_pipeline.py` checks the composed multi-tool route reports dash `tag_only`, restricts that status to the dash tagger, and verifies a candidate dash artifact cannot bypass candidate/producer gates. These are implementation checks, not pixel accuracy. CLEAN5C ran no test suite and introduces no new tests.

## Known limitations

Tags describe characters already in the label; they do not establish printed dash identity, discover a missing dash, or correct a confusion with raised dots. The four literal route characters are the code's scope. N1 range protections and lead-verified separator edits must not be described as a general dash model. Historical plans proposing other punctuation work remain proposals.

## Code paths

`greekocr/harvest/line_pipeline.py`: `routes`, `automatic_result`, `validate_result`; version manifest `docs/harvest/line_pipeline/tool_versions.json`; pipeline tests `tests/test_line_pipeline.py`. LQB class declaration/scoring: `greekocr/labelfix/lqb.py`.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`.
- `docs/harvest/line_pipeline/tool_versions.json`; `greekocr/harvest/line_pipeline.py`; `tests/test_line_pipeline.py` (dash-related source/tests).
- `docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md`; `docs/records/labelfix/secondary/{PLAN.md,N1_DASH_CONTROL_TYPES.md,HANDOFF_20261018.md}`.
- `greekocr/labelfix/lqb.py`; `docs/records/labelfix/lqb/versions.json`.
