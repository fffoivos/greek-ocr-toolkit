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
sources → curved-rule cuts → type recovery with permanent rejected-region vetoes.
Geometry retains original contour ancestry. Its retention guard sees only current
survivors. Recovery uses quadrilaterals for grid nomination and real polygons for
ink ownership. Regional separator protection checks additions without another Q8
full-page pass. Features not implemented by the tracks remain unresolved here.

Reproduce the supplied allowlist (195 pages, never discover other pages):

```sh
python -m prototypes.fast_lines.stack benchmark --version new-run --repeat 1
python -m prototypes.fast_lines.stack benchmark --version new-run --repeat 2
python -m prototypes.fast_lines.stack summary --version new-run
python -m prototypes.fast_lines.stack review --version new-run
```

Use the Python/environment above for every invocation. Repeats reverse page order,
refuse existing timing receipts, verify fresh Paddle output against the pinned
baseline and require exact final output equality. A source snapshot and model hash
are saved. Rendering is separate. Review ledgers must be filled through actual
inspection before `python -m prototypes.fast_lines.stack.validate --version new-run`.

The tracked `review.json` is the 195-page human inspection ledger. Output galleries,
raw timings, all detector JSON and validation live under `.astra/fast_lines/out/stack/`.
`reuse.json` records exact upstream snapshots; those owned copies only adapt imports.
No production page API imports, PDF text, held-out inputs or page-keyed runtime gates.
