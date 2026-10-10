# Faintness, inkiness, images — round 3 track B

This is an experimental feature study, not the production pages API. Read
`docs/research/FAST_LINES_FEATURES_B.md` for measured outcomes and failures.
The runtime candidate composes round 2 separators with conditional reflected-glyph
ownership and spatially repeated ornament evidence. Unknown ownership preserves.
There is no generic image eraser, readability classifier or missing-line recovery.

Use the project Python from this worktree, with `PYTHONDONTWRITEBYTECODE=1`.
All images, JSON, raw timings and frozen source snapshots are outside git under
`.astra/fast_lines/out/features_ink/`. Open `index.html` there for the gallery.

## Reproduce

```sh
export PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY -m prototypes.fast_lines.features_ink.study reference --version new-reference
$PY -m prototypes.fast_lines.features_ink.perturb
$PY -m prototypes.fast_lines.features_ink.edge_study --version new-edges
$PY -m prototypes.fast_lines.features_ink.density --version new-density
$PY -m prototypes.fast_lines.features_ink.final study --version new-study
$PY -m prototypes.fast_lines.features_ink.final benchmark --version new-study --start 0 --count 32 --repeat 0
$PY -m pytest prototypes/fast_lines/features_ink/test_features.py prototypes/fast_lines/tests -q
```

For benchmark repeats 0 and 1, run consecutive batches starting at 0,32,...,192.
For repeat 2, use `--agreement` and starts 0,32. Never run timing batches in
parallel. `publish --version new-study` requires all430 timed page executions,
validates the detector-format JSON, writes measured `seconds`, route comparisons,
galleries, timing summaries and a source snapshot. It fails on duplicate receipts.
Detector startup/warmup and image decode are separate from `seconds`; no cached
feature, map or line list enters the timed path. Cached outputs are read only for
exact equality assertions after timing.

`diagnostic_timing --start N --count 4 --repeat R` separately times optional
feature censuses on the12 explicit pages. This deliberately excludes the detector;
it must not be confused with the fresh end-to-end stack benchmark.

## Interfaces

- `features_ink.pipeline.run(gray, items, detail=False)`: Q8 separators then B;
  returns final `items`, removals, witnesses and charged times. Call with uint8
  grayscale original pixels and full-page detector polygons.
- `shared.ink_ownership.analyze(gray, items, regions=None, detail=False,
  route='explicit')`: full-page rectangle hypotheses, witnesses, suspect/anchor
  indices, `suppress_indices`, `scout_s`, `seconds`. Optional regions allow a
  candidate-only recovery veto. Front is an ordinary-shape hypothesis, not proof.
- `shared.ink_strokes.measure(gray, box, height, samples=None, maps=False)`:
  independent darkness, width, holes and fragments at three relative thresholds.
  `heuristic(...)`: one-threshold area/Crofton-perimeter approximation.
- `shared.ink_edges.profiles(...)`: cross-stroke normal rays and interpolated20/80
  spread, distinct from darkness and width.
- `shared.ink_images.render(...)`: connected area-ink support, including touching
  text. Never use this support or its bounding boxes directly to erase lines.
- `shared.ink_motif_gate.inspect(...)`: cheap continuity → reduced contextual
  spatial repetition → full witness → residual glyph veto. Only this narrow
  image-related witness enters the runtime stack.
- `shared.ink_stamps.analyze(...)`: ellipse/ring diagnostics; no stamp removal.

Offline modules may import the existing pages model. Runtime modules do not.
C's body contacts and grids are consumed by `cooperate.py` from an explicitly
supplied sibling worktree, copied and hashed in the output. They are not a mutable
runtime dependency. Round3 introduced these owned shared modules; round4 changes
only B-owned shared modules. No production modules are edited.

## Round4 continuation

The latest output is `.astra/fast_lines/out/features_ink/round4/index.html`.
Final correction images/JSON are `round4/study-v3/`, with two fresh195-page
benchmarks and exact round3 decisions. Runtime source hashes are frozen in
`round4/runtime-handoff.json` and independently snapshotted by stack.

The negative motif tail now uses a local four-copy recurrence rendering before
both old verifiers. This does not change the final72 B removals. Full native,
8/body explicit and FFT-nominated recurrence images are in `recurrence-v4-*`.
`ink_run(gray,items,detail=False,height=None,ownership_evidence=None)` can reuse
already paid ownership evidence; pixel identity belongs to the caller, while
image size, bbox list and optional height are checked. Height MUST preserve
`shared.geometry.height_proxy` semantics for the current items. Returned
`motif_costs` lists every examined line's nomination and cost. Do not feed C body
heights into this adapter or reuse evidence after separator changes.

New diagnostic APIs, all independent of the correction path:

- `ink_observability.measure(gray,box,height,route='slow',detail=False,version=4)`:
  native local noise, illumination, relative-threshold strokes and topology under
  measured noise. `explicit` uses32 samples/component-height; `heuristic`12.
  `readability` and physical cause remain unknown. Stable empty masks are refused.
- `ink_image_structure.render(gray,height,route='slow',version=4)`: observed long
  edges; `explicit` reduced edges; `heuristic` orientation texture. No exclusions.
- `ink_stamp_field.render(gray,ring,height,route='slow',version=4)`: angle/radius
  unrolling and contrast against both radial flanks. `explicit` reduced census;
  `heuristic`24 spokes. Ring fitting is only a hypothesis, never ownership.
- `ink_type_identity.py` is an unmodified C diagnostic snapshot. Native components
  are physically deduplicated; source/hash/use recorded in `reuse_round4.json`.
  It does not supply recognized letters or fonts, and is not a runtime dependency.

Reproduce the final component work using the mandated Python/environment:

```sh
python -m prototypes.fast_lines.features_ink.recurrence_study --version recurrence-v4-dense --dense --focus
python -m prototypes.fast_lines.features_ink.recurrence_study --version recurrence-v4-explicit
python -m prototypes.fast_lines.features_ink.recurrence_study --version recurrence-v4-heuristic --route heuristic
python -m prototypes.fast_lines.features_ink.observability_study --version observability-v4
python -c 'from prototypes.fast_lines.features_ink.observability_controls import run; run(4)'
python -m prototypes.fast_lines.features_ink.round4_review
python -m prototypes.fast_lines.features_ink.image_structure_study --version 4
python -m prototypes.fast_lines.features_ink.publish_round4
```

The final publisher requires the declared390 fresh receipts and exact reviewed
outputs. It verifies runtime hashes and puts measured warm detector+Q8+B seconds
in every detector-format JSON. `final study/benchmark --version round4/study-v3`
uses the previous CLI; keep foreground timing batches at most32 pages and repeat
before quoting. The one40-page agreement call took under8s here.

Known limits retained in images and report: period-sized templates miss motifs;
coarse noise/topology disagrees on clear letters; E→F stroke loss can be dark and
stable; fitted stamp rings can be paper grain; engraving and table rules both
have long edges; area masks touch decorated initials and real captions. New
readability/generic image/stamp correction remains unaccepted. The optional full
component census takes over2s on0ce9 when extraction is paid; it is not a scout.
