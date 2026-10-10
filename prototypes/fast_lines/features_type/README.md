# Track C: physical type features

Research code only; no `greekocr/pages/` modifications. Final entry point:
`shared.type_recovery.run(gray, items, detector, version=4)` includes round 2
separators, then a type-grid scout, conditional original-pixel confirmation,
regional table evidence, reflected-glyph veto and a local Paddle rerun. It adds
lines only. Guide and font-property censuses are separate on-demand features.

Use the repository's specified Python from the worktree root, with
`PYTHONDONTWRITEBYTECODE=1`. Commands are foreground and single-threaded OpenCV.

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.reference
# Explicit first. Inspect its images before running fast.
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.study slow --version 3
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.study fast --version 3
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.tables slow --version 5
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.tables fast --version 5
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.lattice slow --version 3 --all-pages
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.lattice fast --version 3 --all-pages
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.pipeline study --version 4
# Short fresh timing batch; repeat with 2, and offsets for other cohorts.
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.features_type.pipeline bench --version 4 --group agreement --repeat 1
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m unittest prototypes.fast_lines.features_type.test_type -v
```

All artifacts are outside git at `.astra/fast_lines/out/features_type/`.
The `active-*.json` files locate source-keyed outputs. Historical iterations are
retained. Earlier font/table versions have recorded source digests but not full
source snapshots; final correction runs snapshot their source modules. Do not
claim historical bit-for-bit reconstruction from the current modules alone.

## Iteration record

- Model/A07: inspected real contact/guide geometry; A07 mixes adjacent rows and
  arbitrary page-quarter groups, then anchors each family on one noisy exemplar.
- Type v1 → v2 → v3: contacts → nearest density band + support abstention →
  24 samples/body + joined-ink uncertainty. Sparse envelopes stay nonsemantic.
- Tables v1 → v5: rule/cell graph; stop cross-leaf joins; explicit dots; stop
  adjacent prose expansion; regular dot chains replace transitive flood-fill.
  63c4 p4 remains a failure, and 922e p5 has fragmented protection only.
- Lattice v1 → v3: centroid residual → body-bottom contact → explicit old-polygon
  ownership. Every one of 195 pages has dense, R1 and R2 images/records.
- Corrections v1 → v4: raw grid recovery exposed a mirrored addition; B4 veto
  removes it; component completion exposed preceding-row initial growth; remove
  that growth; regional Q8 crossings abstain; dense slot disagreement abstains.

B snapshots are attributed in `reuse.json`, with only import renaming. Stopped
`0b052af` supplies component completion (detached-initial growth removed) and
regional rule protection. The report contains scope, limitations and timings.

Late independent geometry check: `uncertain=False` is not calibrated confidence.
On 3229 p4 source24, contact size40.4px disagrees with neighbouring21–23px
print. See output `cooperation/body-scale-00.jpg`; do not automatically borrow
these heights without independent evidence. The final recovery does not use
this full-line height census.
