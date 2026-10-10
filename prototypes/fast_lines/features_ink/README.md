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
runtime dependency. No existing shared or production modules were edited.
