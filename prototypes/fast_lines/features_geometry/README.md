# Track A geometry: round 4 continuation

The current research pipeline is `shared/geometry_pipeline.run(gray, pm, items)`.
It includes Q8 once, the faster equivalent R3 scout/context, native contour and
curved-rule corrections, then guarded original-ink fragment joining. It is
separate from the stack track's frozen B/C composition. Orientation parking is
still the caller's responsibility. Inputs remain native pixel coordinates.

```python
from prototypes.fast_lines.shared.geometry_pipeline import run
result = run(gray_uint8, probability_map, original_items)
```

For composition, preserve original item identity:

```python
from prototypes.fast_lines.shared.geometry_scout import sparse_fast
from prototypes.fast_lines.shared.geometry_context import correct_geometry
from prototypes.fast_lines.shared.geometry_fragment_correct import run as fragments
# Both optional witnesses below must be charged by the caller.
a = correct_geometry(gray, pm, original_items,
    retained_source_indices=retained_original_ids,
    rule_witness=rule_witness, geometry_scout=geometry_witness)
b = fragments(gray, original_items, current_items,
    forbidden_regions=removed_or_uncertain_regions)
```

`current_items` must have original `source_ids`; split or removed owners cannot
be rejoined. Original competing owners still veto ambiguity. A supplied
`rendering`/`witness` is reused only at caller cost; default runtime computes every
dependency. `forbidden_regions` takes dictionaries with `bbox` or `polygon`;
its veto uses the bounding rectangle. The Q8+A harness does not include B/C.
Joined `baseline` is null and `centreline` is a body-contact path, not a baseline.
All participating old polygon pixels are retained. No wholly missing line is
searched for and no original source is suppressed by the new operator.

`geometry_contacts.render_contacts(gray, items, route='slow'|'explicit_fast',
version=7, selected=None)` exposes components, observed paths, end traces and
ambiguity. `geometry_fragments.candidates(items,size)` is a cheap box/tangent
scout, not a join certificate. Leaf and skew tools are diagnostics only.

The [round-4 legend](ROUND4_README.md) and [visual review record](ROUND4_REVIEW.md)
state every retained failure and the scope of actual inspection. Full report:
`docs/research/FAST_LINES_FEATURES_A.md`; owner gallery:
`.astra/fast_lines/out/features_geometry/round4/index.html`.

## Reproduce round 4

Use the prescribed Python from the worktree root with
`PYTHONDONTWRITEBYTECODE=1`, as below in the historical section. Run sequentially;
no background jobs. The R3 final artifacts/cached inputs must already exist.

```text
-m prototypes.fast_lines.features_geometry.scout_audit --repeat 1
-m prototypes.fast_lines.features_geometry.scout_audit --repeat 2 --groups agreement discrepancy
-m prototypes.fast_lines.features_geometry.body_paths --version 7 --route slow
-m prototypes.fast_lines.features_geometry.body_paths --version 7 --route explicit_fast --no-details
-m prototypes.fast_lines.features_geometry.contact_audit
-m prototypes.fast_lines.features_geometry.fragments --version 5
-m prototypes.fast_lines.features_geometry.leaves --version 4
-m prototypes.fast_lines.features_geometry.skew_contacts --version 2
-m prototypes.fast_lines.features_geometry.skew_rotation
-m prototypes.fast_lines.features_geometry.review_round4
-m prototypes.fast_lines.features_geometry.benchmark_round4 --repeat 1
-m prototypes.fast_lines.features_geometry.benchmark_round4 --repeat 2
-m prototypes.fast_lines.features_geometry.artifacts_round4
-m pytest prototypes/fast_lines/tests prototypes/fast_lines/features_geometry -q -p no:cacheprovider
```

Body rendering skips existing page JSON; the timing harness refuses to overwrite
repeat receipts. Use a fresh output area for a new experiment. Intermediate
`fragments-v1` to v4 images record previous code states; `--version` on that
harness names the output study, not a historical algorithm implementation.
`artifacts_round4` also requires the preserved v3 evidence to verify that final
accepted polygons are a subset of the crops reviewed before the rule veto.

## Preserved round 3 account

# Round 3 A: curvature, skew, separation

This is a research prototype, independent of `greekocr/pages/`. It renders each
feature before conditional correction. Old-model guides and Paddle maps are
fallible observations. Neither line list is an accuracy reference.

Final products live outside git in `.astra/fast_lines/out/features_geometry/`:
`index.html` is the page index, `explicit-v2/` the slow reference renderings,
`routes-v4/` the two routes, `corrections-v6/` the inspected stack, and `detector/`
the fresh timed detector-format exports. Earlier versions preserve failed trials.
The full report is `docs/research/FAST_LINES_FEATURES_A.md`.

## Runtime interface

```python
from prototypes.fast_lines.shared.geometry_feature_correct import run
result = run(gray_uint8, small_detector_probability_map, small_detector_items)
items = result['items']
```

Inputs use original-page pixel coordinates. The probability map must come from
the repository's pinned DB detector and matching quad postprocessor. Changed
geometry gets `baseline=None`; `centreline` is a DB-band centre, not a semantic
baseline. `source_ids` retains original item identity through separator splits.
Scores are inherited detector scores, not calibrated correction confidence.

`run` includes Q8's scout and separator correction. Do not run another Q8 stack
inside its measured timing. Empty input is unresolved, orientation is handled by
the caller's existing parked-page rule, and there is no missing-line or ghost
suppression operator here. The runtime reads no old-model guides, page names,
corpus labels, cached evidence or other track's files.

Reusable new modules:

- `geometry_feature_paths.bands(pm, items, size, version=4)`: explicit connected
  map bands with exact contour lineage, topology warnings, central affine slope
  and end residual. `sparse(..., version=3)`: bounded sparse scout.
- `geometry_feature_separation.route1(gray, items)` / `route2(items, size)`:
  pixel corridors and repeated endpoint-gap hypotheses. Diagnostics only.
- `geometry_feature_rules.curved_rule`, `boundary_ownership`, `refine`:
  sustained curved strokes, whole-rule glyph-junction uncertainty, and cuts.
- `geometry_feature_correct.retention`, `keep_nearby_ink`: local unique-ink
  conservation and bounded envelope repair. These are preservation guards,
  not proof that an envelope is the ideal segmentation.

## Reproduce

Run from this worktree with
`PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
All commands below are foreground commands, sequentially:

```text
-m prototypes.fast_lines.features_geometry.reference --version 2
-m prototypes.fast_lines.features_geometry.study --version 4
-m prototypes.fast_lines.features_geometry.rules
-m prototypes.fast_lines.features_geometry.correction --version 4
-m prototypes.fast_lines.features_geometry.rule_ownership
-m prototypes.fast_lines.features_geometry.correction --version 6
-m prototypes.fast_lines.features_geometry.cooperation
-m prototypes.fast_lines.features_geometry.artifacts --validate --sheets
-m prototypes.fast_lines.features_geometry.benchmark --repeat 1
-m prototypes.fast_lines.features_geometry.benchmark --repeat 2 --groups agreement discrepancy
-m prototypes.fast_lines.features_geometry.benchmark --summary
-m pytest prototypes/fast_lines/tests prototypes/fast_lines/features_geometry/test_geometry.py -q -p no:cacheprovider
```

`rule_ownership` deliberately reads the earlier V4 proposals to show the failure
before the veto. `cooperation` is optional offline analysis and snapshots track
C's source with a hash; it is never a runtime dependency. The harness accepts
only the existing 195-page manifest. Timings refuse to overwrite a repeat number.
Review images/JSON serialization are outside measured inference/correction time.

## Iteration record

1. Six model guides; then baseline/meanline versus a central tangent to make
   curvature readable. Character-sized flanks remove margin false gutters but
   miss some fold-adjacent whitespace.
2. Map bands selected by box centre pick neighbors; exact DB contour lineage
   repairs the attribution. Independent sparse maxima jump rows; continuity from
   the middle reduces that failure.
3. Box-derived height shrinks the normalized curl signal when the box itself
   grows taller. Measured central DB-band thickness fixes this feedback, without
   pretending to measure font x-height.
4. Unguarded native contours uncover rows and marks. Exact unique-ink accounting
   rejects those changes; only nearby lost marks can enlarge the native envelope.
5. A continuous back-page rule can pass a local word gap. Whole-rule glyph
   junctions veto it. A synthetic crossing then exposed narrow-strip white
   estimation erasing dark crossings; a surrounding-paper estimate fixes that.

Physical page-leaf separation, severely fragmented curled ends and a semantic
baseline from the small detector remain unfinished. See the report for named
failures and the exact limits of visual review.

## Round 5

Runtime changes are imported by the existing `prototypes.fast_lines.stack.Stack`.
`shared.geometry_columns.analyze/apply` provide native rule and bilateral
termination evidence; `shared.geometry_envelopes.guided/correct` provide native
contact envelopes and guarded final shaping. No separate runtime stack is used.

The experiment record is [FAST_LINES_ROUND5_GEOMETRY.md](../../../docs/research/FAST_LINES_ROUND5_GEOMETRY.md).
Outputs, per-line comparisons, owner comments and numbered images are under
`.astra/fast_lines/out/round5/geometry/`. `round5_shapes`, `round5_columns`,
`round5_routes`, `round5_fast_audit`, `round5_new_model` and `round5_endpoints`
produce the component studies; `round5_benchmark` runs the actual public Stack,
and `round5_artifacts` validates saved exports without rerunning inference.
These scripts refuse to overwrite completed experiments/receipts.

The input cohort is the fixed 195-page manifest plus five explicitly supplied
review pages. Offline comparisons require the existing R4b output directory and
`out/round5/geometry/baseline/` for the five new pages, created using the R4b
Stack before R5 changes. Missing pinned baselines raise an error; the current
Stack must never silently generate its own comparison reference. Current code
preserves historical versioned artifacts; old correction versions are recorded
experiments, not a promise that their acceptance code is selectable in this revision.
