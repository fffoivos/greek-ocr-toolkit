# Track C: physical type features

Research code only; no `greekocr/pages/` modifications. Final entry point:
`shared.type_recovery.run(gray, items, detector, version=4)` includes round 2
separators, then a type-grid scout, conditional original-pixel confirmation,
regional table evidence, reflected-glyph veto and a local Paddle rerun. It adds
lines only. Guide and font-property censuses are separate on-demand features.

Round4 continuation: `shared.type_context.recover` composes with current B/A
items, optional precomputed evidence, stable grid quadrilaterals and excluded
regions, without repeating Q8. `shared.type_extended.run` is a separate
experimental Q8+C pipeline: sixteen inspected additions on fourteen pages,
including two new drop-cap rows. It is not the stack's frozen fifteen-addition
pipeline. Full receipts: `out/features_type/round4-README.md` and `round4.html`.

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

## Round4 component work

- `rows4`: native,24/body and8/body component/row assignment and ink-mass paths.
  V1 mixed contacts from neighboring rows; V2 pairs contact populations; V3
  excludes clipped neighbors.3229source24 now abstains, but Arabic17/26/31 remain
  falsely clear. No semantic baseline or reliable joined-script classifier.
- `identity4`: physical glyph masks and alternate native64/R124/R2spatial
  witnesses within seven pages and across four supplied pages of one book.
  Physical dedup fixes overlapping-localization self matches. Simple marginals
  confused theta/slash; spatial occupancy/counter witnesses reduce that failure.
  Font identity remains unknown, and native extraction dominates cost.
- `extents4`: seven-cycle leader-dot/table-boundary work, native/20h/8h.
  V6 protects complete922e and stops above4b80prose, but63c4 remains incomplete.
  Triggered4959 exposes false prose protection. `table_dots7` renders filled
  interiors/counters; it still fails and is not a runtime replacement.
- `edges4`: one-pitch continuations and uncertain interior phase intervals.
  All195 pages have native/R1/R2,389slot comparisons. Ghosts and an ornament
  also satisfy body-grid evidence; independent ownership and regional inference
  remain essential. No font/row census is paid on the clean runtime path.
- `extended4`: three fresh195-page runs,585 exact reproductions; original
  Q8+C items preserved, only two reviewed additions. `validate4` checks29,549
  invariants and records page/line/slot disagreements. `measure4` separately
  times complete on-demand censuses, including extraction. `publish4` adds the
  round4 tables/index without rewriting round3 receipts.

Final reproduction commands are in the output README. Each feature runner uses
`slow` then `fast`; inspect original-pixel renderings before accepting fast work.
`reuse_round4.json` attributes all new B snapshot dependencies. The complete
report is `docs/research/FAST_LINES_FEATURES_C.md`.
