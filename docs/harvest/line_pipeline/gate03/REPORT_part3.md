# Content gate 0.3, part 3

Final eligibility 0.3 now follows the cell amendment: on a rotation-free crop aspect A ≤ 6, the shared raw-text check `alnum > 1` is the only length/shape check. Cells bypass the final ≥4-digit / 60% `numeric_shape` and `nonletter_fraction` checks. The existing `short_line_exclusion()` and `crop_aspect()` helpers are shared with the gate. Content issues, codec coverage, confidence, CTC and held-out edition checks still apply to every row. Ordinary lines and all non-cell behavior are unchanged. Content gate and PIPELINE_VERSION stay 0.3.

For clarity, the existing final shape branch is role-specific: non-cell `numerics_tables` rows retain their numeric shape check; grammar-only numeric rows retain their existing nonletter-fraction branch. Both retain the shared >1 alnum gate exemption. No grammar-only row was moved to a different final shape branch.

## Gate/final agreement and shared fixture

Ten new KEEP/no-change cases exercise five cell labels in both orientations at the inclusive A=6 boundary: `ΑΒ`, `(Α+Γ)`, prose `12`, numerics_tables `12`, and numerics_tables `fr. 91`. Each passes the actual gate and segmentation, preserves its label through qualified no-change correctors, and has no final eligibility issue. Four further cases prove that cell exemption retains low confidence, CTC infeasibility, missing required CTC steps and held-out edition exclusions.

The shared `row()` default is now 1000×20 (A=50), an ordinary line. The baseline with Clariden present passed all 222 existing cases. A fixture-only rerun changed exactly one test result: `test_length_is_final_and_can_be_rescued_by_a_qualified_edit` failed, because raw `λόγος` has five letters and an ordinary line must drop before its correction runs. It previously passed because the shared default made it a cell. It now explicitly supplies 100×20 dimensions and retains all assertions; the comment states the cell exemption. Existing wide-line tests continue to forbid rescue of a raw short ordinary line. No other existing test changed pass/fail outcome under the new default.

[Exact shared-fixture/test diff](part3-existing-tests.patch), [complete fixture-only traceback](part3-tests-fixture-only.txt). The relevant failure was:

```text
>       assert d["disposition"]=="ADMIT" and calls==["polytonic"]
E       AssertionError: assert ('DROP' == 'ADMIT'
E         
E         - ADMIT
E         + DROP)
tests/test_line_pipeline.py:47: AssertionError
1 failed, 221 passed in 3.76s
```

This arose from the part-2 fixture amendment and is fixed by the explicit cell dimensions, not by weakening the gate.

## Read-only finite-set comparison

The same 150/888/250/417 inputs, metadata joins, source expectations and bound crop dimensions as part 2 were reread. Header-backed crops were checked against their crop SHA256. All gate-admitted rows were compared using the saved starting `final_eligibility` implementation and the new implementation, on raw saved text with an empty diagnostic policy. No Pipeline, correction adapter, native segmenter, reader or population census was run for this diagnostic. Saved split values remain unchanged. Missing edition IDs are supplied as `None` solely to satisfy the final checker's lookup contract under an empty held-out policy; this does not establish edition provenance or eligibility for admission.

`ELIGIBLE` below means no final-check issues in this diagnostic; it is not a pipeline ADMIT prediction. These overlapping sets count entries, not unique crops.

| Set | Entries | Reason lists changed | Removed numeric_shape | Removed nonletter_fraction | DROP → ELIGIBLE | Numeric non-cell numeric_shape remaining | Numeric non-cell nonletter_fraction remaining |
|---|---:|---:|---:|---:|---:|---:|---:|
| segeval1 | 150 | 6 | 5 | 1 | 5 | 0 | 0 |
| calibration | 888 | 58 | 43 | 15 | 51 | 0 | 1 |
| cells | 250 | 48 | 48 | 0 | 48 | 0 | 0 |
| typology | 417 | 43 | 14 | 29 | 20 | 0 | 0 |
| Total entries | 1705 | 155 | 110 | 45 | 124 | 0 | 1 |

The remaining numeric non-cell is calibration `elstat--daec83cb9a364cd1--s001-l0063`, raw `1936........`, A=6.037037037037037: `nonletter_fraction → nonletter_fraction` (DROP → DROP).

All 155 changed reason lists belong to cells. **124 final outcomes change**: 95 `numeric_shape → none`, 29 `nonletter_fraction → none`. Another 31 remain DROP for unchanged non-length issues. Every non-cell's complete before/after issue list is identical.

| Set | Before → after reason list | Entries |
|---|---|---:|
| segeval1 | numeric_shape → none | 5 |
| segeval1 | nonletter_fraction, low_confidence → low_confidence | 1 |
| calibration | numeric_shape → none | 40 |
| calibration | unexpected_language, numeric_shape → unexpected_language | 3 |
| calibration | unexpected_language, nonletter_fraction → unexpected_language | 3 |
| calibration | nonletter_fraction → none | 11 |
| calibration | nonletter_fraction, codec_unencodable → codec_unencodable | 1 |
| cells | numeric_shape → none | 48 |
| typology | unexpected_language, nonletter_fraction → unexpected_language | 11 |
| typology | nonletter_fraction → none | 18 |
| typology | unexpected_language, numeric_shape → unexpected_language | 12 |
| typology | numeric_shape → none | 2 |

[Reproduction script](part3_analysis.py), [counts](part3-counts.json), [every gate-admitted row before/after](part3-row-decisions.jsonl), [input hashes](part3-input-hashes.json). Reproduce with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python docs/harvest/line_pipeline/gate03/part3_analysis.py`.

## Owner homoglyph ruling

**Owner, 14 Oct.** Any Greek word containing a Latin, Cyrillic or other-script letter drops the whole line automatically. Examples: ΚΕΦΑΛΑΙΟN, Δαβій, Fιδον, λόγoς. There is no look-alike correction and no model pass. The earlier repair-and-admit path for such words was a deviation from the owner's rule, and gate 0.3 removes it.

**Owner, 18 Oct.** The only allowance is a secondary-script WHOLE word, per class, when it has at least one letter with no look-alike in the primary script.

**Read-only implementation check: absent.** `inventory()` in `greekocr/harvest/line_pipeline.py` detects multiple scripts within each word. `content_gate_exclusion()` drops these before tools. `content_issues()` uses declared scripts or the source-level `latin_policy == "mixed_class_or_minority"`, which allows Latin but flags majority Latin. These paths have no per-class whole-word test requiring a letter without a primary-script look-alike. The legacy source/class policy code in `admission.py` likewise does not supply this condition to the current pipeline. The 18 October allowance was not implemented in this run. The ruling and implementation gap are also recorded in the README gate section.

## Tests

Interpreter: read-only sol-recut `.venv/bin/python`, this checkout on `PYTHONPATH=.`, bytecode writes disabled and pytest cache provider disabled. No installation or network access. The four requested segmentation suites are gate, deskew, curve and small, as in part 2. Existing synthetic census-coordinator tests execute tiny mock fixtures only; no population census or reader was run.

Verbatim final counts:

```text
47 passed in 1.13s
130 passed in 1.87s
59 passed in 2.65s
236 passed in 3.83s
```

These correspond respectively to [content gate](part3-tests-content.txt), [line pipeline](part3-tests-pipeline.txt), [four segmentation suites](part3-tests-segmentation.txt), and the [combined requested suite](part3-tests-after.txt). Final failures: **0**. [Baseline](part3-tests-baseline.txt): `222 passed in 4.01s`. The temporary fixture-only failure and its resolution are documented above.

## Versions, Clariden and scope

`final_eligibility` is 0.3 with the exact new iteration: `cells: alnum > 1 is the only length/shape check, consistent with the gate`. Content gate remains 0.3. All other tool method versions and PIPELINE_VERSION are unchanged; dependent source digests are regenerated.

`tool_versions.json` was regenerated directly by `scripts/harvest/build_filter_versions.py`, with every declared component present and every resulting component hash independently verified. Census already includes the five Clariden scripts. The build did not invoke `rebuild_versions.py` or any fallback.

The historical `version-build-fallbacks.json` is preserved as prior-run evidence; its literal before/after lists are identical. [Before](part3-version-build-fallbacks-before.json), [after](part3-version-build-fallbacks-after.json), [fallbacks actually used by this build](part3-version-build-used-fallbacks.json): `[]`.

| Historical requested fallback | Before manifest | After manifest | Used now |
|---|---|---|---|
| clariden/worker.py | Listed | Listed | No |
| clariden/bootstrap.py | Listed | Listed | No |
| clariden/filter_crop_paths.py | Listed | Listed | No |
| clariden/filter_worker.sbatch | Listed | Listed | No |
| clariden/package.py | Listed | Listed | No |

All five working Clariden files match both their committed package copies and sol-recut's working files byte for byte; none were edited. Full paths and SHA256 values: [Clariden verification](part3-clariden-shas.json).

The scope guard compares all 26,839 initial tracked/protected file hashes, verifies exactly six changed tracked paths, rejects additions outside gate03/ relative to the initial untracked inventory, and rechecks Clariden hashes. The only changed source/document/test files are:

- `greekocr/harvest/line_pipeline.py`
- `scripts/harvest/build_filter_versions.py`
- `tests/test_content_gate.py`
- `tests/test_line_pipeline.py`
- `docs/records/harvest/line_pipeline_legacy/README.md`
- `docs/harvest/line_pipeline/tool_versions.json`

All new evidence is under gate03/ with part3-prefixed names or `REPORT_part3.md`. [Scope guard](part3_scope_guard.py), [guard result](part3-scope-guard.json), [diff](part3-scope.patch), [stat](part3-scope-stat.txt), [receipt](part3-receipt.json). The package/, seg09/, segmentation evidence JSONL, previous gate reports/evidence, segmentation code, readers, routing and repair logic remain unchanged. No .git-writing command, network request, reader run, compute launch or population census was executed.

GATE 0.3 PART 3 READY: final cell rule ok; gate/final agree ok; final outcomes changed 124 (numeric_shape 95, nonletter_fraction 29; 155 reason lists changed); clariden shas 5/5; 18-Oct allowance absent; tests 236 passed 0 failed


**Lead correction (19 Oct, after this run).**
- The "18 Oct" allowance above was a coordinator ruling, not the owner's.
- It is superseded by the owner's two gate rules and will not be implemented.
- Look-alike-only words are a label-quality question for the correction tools.
- See the README gate section.
