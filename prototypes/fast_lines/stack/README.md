# Combined fast lines prototype

One file-to-lines entry point, using a warm reusable Paddle v6 small session:

```python
from prototypes.fast_lines.stack import Stack
stack = Stack()
result = stack('page.png')
lines = result['items']
```

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.stack page.png --output result.json
```

The export uses the existing detector format, `unit: line`, page/image size, polygons,
null baselines, scores and provenance. `source_ids` are indices in the ORIGINAL
Paddle list; newly recovered lines carry their type-slot provenance. Timings include
decode, inference, detector postprocessing and all corrections. JSON writing and
review rendering are outside the timer. Model startup is reported separately.

Order: Paddle → one Q8 scout/correction → ink removals → geometry on surviving
sources → curved-rule cuts → native fragment joins → extended type recovery,
with permanent rejected-region vetoes in both new stages.
Geometry retains original contour ancestry. Its shared context receives only intact
surviving sources; separated pieces stay in the output and cannot own lost ink.
The adapter maps shared results back to the existing order without copying any
acceptance logic. Joins retain original source IDs and receive B removal footprints. Recovery uses quadrilaterals for grid nomination and real polygons for
ink ownership. Regional separator protection checks additions without another Q8
full-page pass. Features not implemented by the tracks remain unresolved here.

Reproduce the supplied allowlist (195 pages, never discover other pages):

```sh
python -m prototypes.fast_lines.stack benchmark --version new-run --repeat 1
python -m prototypes.fast_lines.stack benchmark --version new-run --repeat 2
python -m prototypes.fast_lines.stack summary --version new-run
python -m prototypes.fast_lines.stack review --version new-run
python -m prototypes.fast_lines.stack.compare --previous final --version new-run
```

Use the Python/environment above for every invocation. Repeats reverse page order,
refuse existing timing receipts, verify fresh Paddle output against the pinned
baseline and require exact final output equality. A source snapshot and model hash
are saved. Rendering is separate. Review ledgers must be filled through actual
inspection before `python -m prototypes.fast_lines.stack.validate --version new-run`.

The tracked `review.json` is the 195-page human inspection ledger. Output galleries,
raw timings, all detector JSON and validation live under `.astra/fast_lines/out/stack/`.
Current exports are in `.astra/fast_lines/out/stack/r4b/`; `final/` is the earlier
round-4 snapshot, preserved for comparison. `changes.json` and change crops compare
R4b to it; unchanged pages retain their prior visual observations.

`reuse.json` records imports and hashes of the merged track modules. All eight
owned snapshots were deleted. Stack calls `features_ink.pipeline.ink_run`, shared
`geometry_scout`, `geometry_context`, `geometry_feature_rules`,
`geometry_fragment_correct`, and `type_extended.recover` (which imports
`type_context` / `type_recovery`). No track algorithm is copied into stack.
The merged tree's diagnostic features do not become runtime dependencies merely
because they exist; the native fragment and extended-grid runtime operators do.
No production page API imports, PDF text, held-out inputs or page-keyed runtime gates.
