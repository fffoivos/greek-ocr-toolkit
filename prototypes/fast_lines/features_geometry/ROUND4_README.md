# Geometry round 4 owner artifacts

Start with `index.html`. Each of the 195 supplied pages has original-ink curl,
skew and leaf diagnostics, both fast routes, a correction image, and a timed
Q8+A detector JSON. No held-out page or PDF text layer is used. Orientation stays
parked. The old model and both detectors are fallible evidence, not truth.

## Read the images

- `body-slow-v7`: cyan body-sized component rectangles, green observed contact
  paths, grey original Paddle polygons. Raw/after details are grouped six lines
  per image. These are ink contacts, **not typographic baselines**.
- `body-explicit_fast-v7` and `contact-audit`: route 1 uses the same native pixels
  and finite Gaussian support with faster separable filtering; green slow and
  purple fast overlays show every line comparison. Thirteen of 9,086 paths
  differ by one 0.0625-height sample. All observed spans, component inventories
  and 69 candidate agreement decisions match.
- `body-slow-v7/*.route2.jpg`: purple Hermite paths interpolate main/fragment
  box tangents. The cheap heuristic nominates work. It can point at another row
  or a stamp and never authorizes a join alone.
- `skew-v2`: contact affine fit green when central and end residuals are small,
  amber otherwise. Grey contact path; purple map slope and cyan box slope aligned
  at a common centre to isolate slope differences. Green is provisional, not a
  guarantee of a straight line or a page rotation instruction.
- `leaves-v4`: amber sustained dark path; green means flank isolation plus outer
  contact, **not certified physical leaves**. Red spots mark neighboring ink;
  circles mark lateral frame contact. Route 1 adds purple reduced-pixel paths;
  route 2 adds cyan recurring dark columns. Printed table borders can pass.
- `fragments-v5`: green changed geometry over old grey, green added ink, red
  removed separator stripes. Contains Q8, round-3 geometry and 15 new joins.
  Joining retains every pixel in the participating old polygons. It does not
  tighten the old rectangular part into an ideal curved envelope.
- `runtime/detector`: full measured decode + detector + Q8+A seconds; component
  times in `timing`. Baselines for changed paths are null. `source_ids` refers
  to original Paddle items and preserves split ancestry.
- `page-ledger`: every page's contact line comparison, tangent pair errors, skew
  slopes, leaf route matching, and accepted fragment groups. These are evidence
  counts, not a segmentation accuracy score. Leaf routes match nearest median
  x within two body heights; unmatched hypotheses remain explicit.

## Iterations and failures retained

`body-*-v1` through v7 retain the component experiments. Global maximum-density
paths jumped rows. Central priors still lost curled ends; nearest ridge walking,
independent tracing from each existing fragment and a measured peak seed were
needed. The ten-pixel-height reduced route changed row identities and was
rejected. Native fast filtering preserves the observed evidence. Body height
remains a box-derived proxy; track C's census is not borrowed at runtime.

`fragments-v1` through v5 retain the envelope/cell failures. The first envelope
pinched the bridge; adding a measured body ribbon while retaining old pixels
fixed it. Full-corpus review then found joins across numerical cells and an
index rule. Native regional rule verification removes those cases. Unverified
aligned glyph stems inside the already owned main box caused false vetoes;
only an actual inter-box gap can make such an unverified run block a join.

`leaves-v1` through v5 retain failures. Components merged with scanned frames;
straight opening lost curved spines; native continuation recovered the c99 p71
crease but also followed first letters. Flank isolation removed that false path.
A table border on 7a2b p200 still passes. Connected-paper v5 rejects real folds
because white paper connects around the frame or through crease holes, while a
large table panel still passes. No new physical-leaf correction is enabled.

`skew-v1` incorrectly called central straight parts of severe curl pure skew.
V2 also checks held-out ends. Six known ±2-degree image rotations validate angle
response on three supplied pages, not a new evaluation corpus. Two transformed
ef481 p151 cases cross the provisional-straight residual threshold although
angle errors stay small. No new pure-skew-only correction is claimed.

## Measured result and limits

Fifteen fragment groups on seven pages unite 31 old pieces into 15 items (16 fewer
boxes): three groups on 8686 p7, seven on p5, one on 3229 p4 and four elsewhere.
All 40 agreement pages are unchanged by the new join operator. Prior round-3
changes and all Q8 separation remain intact. The 3229 p6 left curl, 8686 p7
source10+11, ambiguous owners and fully missed rows remain unresolved.

Two fresh 195-page runs exactly reproduce baseline, prior and final polygons.
On 40 agreement pages, incremental fragment cost median/p95/max is
0.578/0.878/87.728 ms and 0.513/0.804/79.645 ms. The negative tail is a stamp
candidate on an-dbd045ccd84c-p000249. Q8+A correction maxima on the 101 new pages
are 760.734 and 682.434 ms. Strict negligible overhead is **not** achieved.
These are warm single-thread measurements on a shared Mac, not latency promises.
No B/C correction is included here. Stack's frozen composition adopted the
faster equivalent scout, but does not include these 15 optional joins.

`summary.json`, `validation.json`, `gallery-links.json`, both runtime JSONL files
and their source receipts carry raw counts and per-page costs. Read
`review/notes.md` for what was actually inspected. Full report and reproduction
commands: `docs/research/FAST_LINES_FEATURES_A.md` and
`prototypes/fast_lines/features_geometry/README.md` in the worktree.
