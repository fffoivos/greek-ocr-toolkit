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
