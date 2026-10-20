# Content gate 0.3, part 2

The shared raw-text length check now runs after the unchanged part-1 exclusions, before crop identity and segmentation. Cells (rotation-free long/short pixel aspect A ≤6) and numeric lines (role or exact grammar) are exempt from the letter minimum when Unicode L*/Nd count is >1. Otherwise cells DROP as `single_character_cell`, non-cell numerics DROP as `numeric_shape`, and ordinary prose/headings DROP as `short_line` below 10/4 letters. Missing crop dimensions HOLD as `cell_status_unresolved`. All exclusions return through `finish()`, with every route `not_run_due_to_prior_exclusion` and no segmentation stage.

`evaluate()` and census `prepare()` call the same `content_gate_exclusion`; final eligibility calls the same `short_line_exclusion`, using the raw inventory even after edits. Role precedence remains expected.content_role > row.content_role > row.primary_class > prose. `nonletter_fraction` and the role-only numeric requirement (≥4 digits and ≥60% allowed shape) are unchanged. Admitted cell/numeric lines therefore remain subject to those final checks.

`numeric_text` reproduces the numeric branch of the read-only common.py, including its exact separators, whitespace handling and canonical uppercase Latin Roman grammar with its optional final dot or closing parenthesis. There is no runtime import from sol-recut. Content gate remains 0.3, with the amendment recorded within its third documented generation to retain the manifest's version/iteration invariant. All other method versions and PIPELINE_VERSION remain unchanged; shared-source digests change. README executed steps 2/7 and the requested Mermaid edge are updated.

## Read-only finite-set counts

Counts below are actual first reasons after part-1 precedence, not independent hypothetical matches. The sets overlap: totals count set entries, not unique crop IDs. No Pipeline evaluation, segmentation, reader or census was run for these counts. The analysis calls only metadata/inventory/gate/final-eligibility functions.

| Set | Rows | short_line DROP | single_character_cell DROP | numeric_shape DROP (≤1) | cell_status_unresolved HOLD | Part-1 mixed DROP | Part-1 foreign HOLD |
|---|---:|---:|---:|---:|---:|---:|---:|
| segeval1 | 150 | 3 | 7 | 0 | 0 | 1 | 2 |
| calibration | 888 | 42 | 6 | 1 | 0 | 10 | 10 |
| cells | 250 | 0 | 36 | 0 | 0 | 0 | 1 |
| typology | 417 | 50 | 57 | 0 | 0 | 3 | 23 |

Dimensions come from `crop_bbox` for 112 of the 150 rows, with width=x1−x0 and height=y1−y0. The other 38/888/250/417 rows use the bound crop's image header size through `crop_path`; every header-backed file was checked against its saved crop_sha256. No bbox from the text/ink detector is used, no rotation is applied, and the ≤8 character small-segment condition is absent.

Finite inputs are S4 `inputs.jsonl` (150 segeval1, 888 calibration, 250 cells) and S4 `typology_replay.jsonl` (417 manifest.control=false, excluding the 20 controls). Text is the saved row.raw_text. For source expectations, the analysis retains existing metadata, restores cells source/wave from `cells/samples.jsonl` with exact text/hash joins, and takes typology source/wave from its saved manifest. Missing W1/W2 source/book/page fields use the existing stable ID components, without inferring language from text. Existing source policies resolve expectations with no new declarations or role overrides. Diagnostic split values remain the saved unassigned values; this is not an admission run.

[Reproduction script](part2_analysis.py), [aggregate counts, breakdowns and examples](part2-counts.json), [all row decisions](part2-row-decisions.jsonl), [input fingerprints](part2-input-hashes.json). Run from this checkout with `PYTHONPATH=. <python> docs/harvest/line_pipeline/gate03/part2_analysis.py`.

Numeric grammar parity is **150/150 + 888/888 + 250/250 + 417/417 = 1705/1705**, against common.py's `output_type(text) == "numeric"`, tested on every raw output including rows excluded by part 1.

## Diagnostic only: unchanged final exclusions

These are gate-admitted cells or numeric non-cells, evaluated on raw labels without running correction tools. They do not forecast post-correction final labels or change any eligibility rule. The final shared length check produces no new exclusion on these admitted rows.

| Set | Admitted cells | Admitted numeric non-cells | nonletter_fraction | numeric_shape | <4 digits | <60% shape | Both numeric defects |
|---|---:|---:|---:|---:|---:|---:|---:|
| segeval1 | 26 | 2 | 1 | 5 | 5 | 0 | 0 |
| calibration | 213 | 19 | 16 | 43 | 42 | 2 | 1 |
| cells | 178 | 16 | 0 | 48 | 48 | 0 | 0 |
| typology | 267 | 0 | 29 | 14 | 14 | 2 | 2 |

Totals: **46 nonletter_fraction**, **110 numeric_shape**. Of the nonletter_fraction exclusions, 45 are cells and one is a numeric non-cell. All 110 numeric_shape exclusions are cells with the numerics_tables role. Of those, 109 have <4 digits, four fail the 60% shape condition, and three fail both. The columns overlap; numeric_shape is the union, not the sum.

Examples (exact raw text; additional examples and per-kind counts in JSON):

| Set | Final reason | ID | Raw text | A | Role | Letters | Digits |
|---|---|---|---|---:|---|---:|---:|
| segeval1 | numeric_shape | gazette_modern--f4a16fe9302ade1e--s000-l0180 | "29)" | 1.5 | numerics_tables | 0 | 2 |
| segeval1 | numeric_shape | elstat--24e6586813212fd1--s001-l0357 | "37" | 2 | numerics_tables | 0 | 2 |
| segeval1 | nonletter_fraction | ia_poly1850--4ab77886725d9e1e--s035-l0035 | "ἐᾶν, 95" | 3 | poly1850 | 3 | 2 |
| calibration | numeric_shape | elstat--3b2d88122b3f037c--s000-l0399 | "13" | 1.82353 | numerics_tables | 0 | 2 |
| calibration | numeric_shape | elstat--3b2d88122b3f037c--s000-l0814 | "205" | 2.21053 | numerics_tables | 0 | 3 |
| calibration | nonletter_fraction | elstat--4b280095ac934f7f--s000-l0036 | "total (1)" | 3.48 | latin | 5 | 1 |
| calibration | nonletter_fraction | gazette_modern--6f1750a448273b10--s000-l0054 | "Καλά 7,56»." | 4.54286 | dialogue_fiction | 4 | 3 |
| cells | numeric_shape | gazette_modern--104e152774c2805f--s000-l0026 | "186" | 1.57143 | numerics_tables | 0 | 3 |
| cells | numeric_shape | elstat--3b2d88122b3f037c--s000-l0586 | "592" | 2.41176 | numerics_tables | 0 | 3 |
| typology | nonletter_fraction | bsb_poly1850--91657e0569fe07c8--s004-l0039 | "68. For-" | 4.66667 | latin | 3 | 2 |
| typology | nonletter_fraction | gazette_modern--79750acfeada2565--s000-l0145 | "(Α+Γ)" | 2.64 | modern_scanned | 2 | 0 |
| typology | numeric_shape | bsb_poly1850--97801b0bc5afce27--s011-l0103 | "fr. 91" | 2.68421 | numerics_tables | 2 | 2 |
| typology | numeric_shape | bsb_poly1850--97801b0bc5afce27--s026-l0039 | "fr. 31" | 2.81081 | numerics_tables | 2 | 2 |

## Tests

Interpreter: read-only `~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python`, invoked with `PYTHONPATH=.` to use this checkout. No installs or network access. Initial system-Python attempts encountered incompatible ARM/x86 numpy/Pillow/SciPy modules; their collection-error logs are retained. The final virtualenv run avoids those problems (including an Intel floating-point comparison mismatch).

| Requested suite | Passed | Failed |
|---|---:|---:|
| tests/test_content_gate.py | 33 | 0 |
| tests/test_line_pipeline.py | 110 | 20 |
| Four segmentation suites: gate, deskew, curve, small | 59 | 0 |
| Combined | 202 | 20 |
| Focused gate + four segmentation suites | 92 | 0 |

[Full requested output](part2-tests-after.txt), [focused output](part2-tests-focused.txt), [exact baseline failure-name comparison](part2-failure-comparison.json). All 20 failures exactly match part 1, and raise the pre-existing missing-support exception:

```text
FileNotFoundError: [Errno 2] No such file or directory: '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/scripts/harvest/clariden/worker.py'
```

The new cases use raising downstream adapters for exclusions, verify exact reasons, skipped routes and precedence, ordinary 9/10 and heading 3/4 boundaries on A>6 crops, the A=6 inclusive boundary in both orientations, raw Unicode L*/Nd counts, >1 character exemptions, role resolution, bound header fallback, unresolved dimensions, and final length idempotence. The mock census tests verify empty Observation, zero native attempts/cache entries for every new DROP reason and missing-dimension HOLD. They execute only the existing tiny synthetic test harness, not a population census.

No existing assertions were loosened or changed. The shared synthetic `row()` fixture now explicitly supplies a 100×20 crop_bbox by default (A=5), overridable with actual dimensions or None. This one-line fixture amendment is required because dimensionless fixtures now correctly HOLD; its [exact diff](part2-existing-tests.patch) is included. The existing rescue-by-edit case now describes an explicit exempt cell; the new wide-line tests enforce pre-segmentation rejection with correction adapters forbidden. There is therefore no old-order assertion diff beyond the fixture amendment.

## Versions, scope guard and receipt

`tool_versions.json` was regenerated using the existing [read-only fallback builder](rebuild_versions.py), whose five absent packaging dependencies are read from sol-recut at the previously pinned hashes. No dependency files were copied or changed.

Eight changed source/document/test files:

- `docs/records/harvest/line_pipeline_legacy/README.md`
- `docs/records/harvest/line_pipeline_legacy/pipeline.mmd`
- `docs/harvest/line_pipeline/tool_versions.json`
- `greekocr/harvest/line_pipeline.py`
- `greekocr/harvest/line_pipeline_census.py`
- `scripts/harvest/build_filter_versions.py`
- `tests/test_content_gate.py`
- `tests/test_line_pipeline.py`

All added evidence lives in gate03/, under part2-prefixed names, part2-baseline/, or REPORT_part2.md. Existing part-1 evidence is unchanged. [Full diff against the starting snapshots](part2-scope.patch), [stat](part2-scope-stat.txt), [receipt](part2-receipt.json). The scope guard asserts that git's changed-file list is exactly the eight paths above. No segmentation components, routing or repair rules, native readers, forbidden package/, seg09/, or census02_segmentation_evidence.jsonl were written. No .git writes, commits, network requests, reader runs, population measurement or census execution occurred.

GATE 0.3 PART 2 READY: short_line ok; cell exempt ok; single_character_cell ok; numeric_shape ok; numeric exempt role ok grammar ok; counts 150/888/250/417 short 3/42/0/50 cell1 7/6/36/57 num1 0/1/0/0 unresolved 0/0/0/0; grammar parity 1705/1705; final idempotent ok; still-excluded diag nonletter 46 numeric_shape 110; tests 202 passed 20 failed
