# Combined fast lines prototype — round 7

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

Order: Paddle → one Q8 scout/correction → existing ink removals → edge scout.
If nominated, cheap curved-rule and column cuts establish the ownership boundaries,
then the shared page field takes ownership before the older per-line paths.
Geometry, fragment joins, grid/native recovery, initial completion and envelopes
handle remaining segments. Relative faintness follows; a conditional second field
selection handles changed sources without another mesh or detector pass. Native
row splitting and the all-segment duplicate audit follow. Changed final footprints
receive faintness again, including recovered/field/clipped segments.

The duplicate audit checks both inclusive paper-relative ink and its observed dark
mode. It subtracts the polygon already covered by a neighbour and retains pieces
with unique ink; complete duplicate crops are retired. The inherited R6 audit is not exact raster
conservation: it found 27 uncovered boundary ink pixels on three pages.
Unique slivers can remain. `source_ids` remain original Paddle indices. `baseline`
is null throughout; consumers use polygons.

Reproduce the supplied allowlist (195 pages plus 13 supplied review pages):

```sh
python -m prototypes.fast_lines.stack benchmark --version r7-new-run --repeat 1
python -m prototypes.fast_lines.stack benchmark --version r7-new-run --repeat 2
python -m prototypes.fast_lines.evidence summary --version r7-new-run
python -m prototypes.fast_lines.evidence.acceptance build --version r7-new-run
python -m prototypes.fast_lines.evidence.acceptance validate --version r7-new-run
```

Use the Python/environment above for every invocation. Repeats reverse page order,
refuse existing timing receipts, verify fresh Paddle output against the pinned
baseline and require exact final output equality. A source snapshot and model hash
are saved. Rendering and JSON writing are separate. The current offline tools are
in `prototypes/fast_lines/evidence/`; importing `Stack` loads none of them.

Each version has its own per-page review ledger. R7 contains all 104 owner comments
verbatim in `COMMENTS.md`, all 256 marked segments in `ROWS.md`, native context crops, historical marked OCR views and native retention/exclusion
ledgers. Fill the review ledgers from
inspection before validating. The round-7 output directory is
`.astra/fast_lines/out/stack/r7/`; earlier versions remain available for comparison.

The following numbers describe historical R6; current r7 numbers are in `r7/TIMING.md`.
R6 was a **partial research result**, not ready for promotion. All 208 pages ran
twice with identical final output, but corrections reach 2393.061 / 2379.603 ms;
21 / 22 pages exceed one second. Agreement overhead is 62.336 / 61.808 ms median,
564.354 / 561.108 ms p95. The duplicate audit goes from 61 pairs to zero, but
three previously recovered real text pieces regress on 3229 p4 and 4959 p1.
Fully faint genuine front print among black print fails four explicit controls;
severe curved ends and multirow crops remain incomplete. See `RECOVERY.md`,
`DUPLICATES.md`, `COMMENTS.md`, `ROWS.md` and `TIMING.md` in the R6 directory.

`reuse.json` records imports and hashes of the merged track modules. All eight
owned snapshots were deleted. Stack calls `features_ink.pipeline.ink_run`, shared
`geometry_scout`, `geometry_context`, `geometry_feature_rules`,
`geometry_fragment_correct`, and `type_extended.recover` (which imports
`type_context` / `type_recovery`). No track algorithm is copied into stack.
The merged tree's diagnostic features do not become runtime dependencies merely
because they exist; the native fragment and extended-grid runtime operators do.
No production page API imports, PDF text, held-out inputs or page-keyed runtime gates.


Stack requests `image_threads=2`; this Mac's OpenCV GCD backend does not honor a
positive worker cap, and every timing receipt reports 10. These are GCD timings,
not a two-worker guarantee. ONNX remains single-threaded. The slower
`Stack(image_threads=1)` probe is separate. Warm session startup and serialization are excluded
from the correction target, but decode and full file-to-final time are recorded.
Native fragment filtering uses only the exact remap domains plus the finite
Gaussian halo; connected components remain global. The same native component
field is reused by final shaping. No acceptance threshold is weakened for time.

`python -m prototypes.fast_lines.evidence.study fields` audits full/local fragment
samples; `study all_bands` measures broad guarded shaping (experimental, not the
public default). Both use only the authorized cohort and retain raw receipts.
The broad shape goal and severe curled ends remain partial; see the stack report.


Round 7 task 4 removes the failed `row_model`/residual-parent route and its
switches. `Stack(bend=True)` remains an isolated opt-in experiment and is not the
default. The accepted default keeps the R6 field and Task 3's 59 whole non-text
removals. The failed near-affine column-skip experiment is archived: native review
found a clipped rho descender on c8 p36. Its speed benefit is not promoted.

Repeated polygon geometry is memoized only inside one `compose` call; edited
polygons use new identities. Field ownership shares native labels within the same
image/proposal, while rerunning current exclusion and fixed-point retention checks.
Dot-chain search is shared; sparse Gaussian convolution reads the same native x
positions and preserves observed final outputs, with a different float accumulation
order. None of these caches survive into the next page. The model, first inference,
DB postprocessing, letter-height semantics, and photometric thresholds are unchanged.

See `docs/research/FAST_LINES_ROUND7_T4_SPEED.md` for the measured timing failure,
all eight checklist dispositions, rejected speed routes and cleanup receipts.
Rust data contracts and crate selection are **deferred by the owner**.

## R8 consolidation, iteration 2

Stack uses plain shared numerical observations. The observation cache and its
zero-reuse wrappers are removed; identity resize returns an owned copy. All
relative closing-paper contrast callers use one multiplication form. Type's six
live ink snapshots now import the merged ink providers. The existing R7 polygon
geometry memo and explicit field dependencies remain.

The208 checked exports are unchanged. Small-letter body height is still not a
validated runtime quantity on clipped, joined, numeric or curved controls; the
new class comparisons stay offline under `evidence/r8_i2_features.py`. See
`docs/research/round8/REPORT_R8-01b-i2.md` for source, physical and timing limits.
