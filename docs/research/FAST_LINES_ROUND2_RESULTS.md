# Q8: conditional printed-rule separators

Materialised A02 as a working conditional path. It adds **10.937604 ms median**
on the 40 agreement controls, calls no correction there, and preserves every
item exactly. Across the supplied pages, the slowest correction is **14.671167
ms**, and the slowest complete addition, including the scout, is **41.655791
ms**. It visibly improves column boundaries on 18 pages. It does **not** solve
missing text, false text boxes, or all remaining line geometry errors.

The owner's target remains, verbatim:

> a good result we could see is something like: for pages where small detector has no errors we add negligable overhead, and for pages where it needs fixes we have sub 1 second corrections.

The owner's full words and standing principles remain in
[CHARTER.md](../../.astra/fast_lines/CHARTER.md). The measured agreement overhead
is about 9% of this run's baseline median. The latency improvement is real;
calling it negligible is application-dependent. Agreement labels do not certify
that the small detector has no errors.

## What was chosen, and why

The ranking and Q7's visible results favour the physical separator witness in
A02. A printed rule can establish a boundary between columns without trusting
another OCR's text or the ours detector's coverage. Q7's costly global Hough
analysis becomes an explicit offline reference; cheap run evidence nominates
only relevant corridors at runtime. Original pixels then decide whether to cut.

I did not materialise the unconditional A02/A03 combination. A03 still has
endpoint/ownership regressions, and always computing dense evidence is precisely
the cost problem Q8 must remove. Q7's unsuccessful recovery sweeps were not
repeated. Unused book-template/duplex ideas need verified book/leaf pairing;
mirrored histograms do not determine spatial foreground ownership. Those are
interesting next experiments, but weaker immediate module candidates.

Implementation: [layout_barriers/fast.py](../../prototypes/fast_lines/layout_barriers/fast.py).
It reuses shared height estimation, image runs, connected components, robust
fitting, polygon contracts and the pinned Q7 small-detector adapter. The shared
review module now renders directional changes. Q7's reference implementation is
retained intact for provenance. The unsuccessful enclosing-grid branch tried
during Q8 was removed; the README records why. `greekocr/pages/` and its tests
were not changed. No push, background job or held-out-page access occurred.

## Runtime mechanism

1. From the small detector's items, estimate provisional body height with the
   existing shared estimator. Area-reduce the grayscale image to at most 12
   samples per body height and 1,200 samples along the page's long side. These
   are sampling budgets, not fixed full-page geometric lengths.
2. Local contrast, short vertical closing and narrow horizontal dilation expose
   long vertical runs. Nominate a corridor only when it crosses at least three
   boxes, each extending six body heights on either side. All geometry uses
   body heights or page coordinates; the algorithm receives no page name,
   direction, cohort or ours-model lines.
3. **Only nominated pages** enter correction. Follow and robustly fit original
   pixel support inside the corridor. Reject discontinuous or non-straight
   strokes. Preserve rules intersecting at least three long horizontal rows.
   Require clear paper beside the rule separately for each proposed line cut.
4. Clip the original polygon against two slanted half-planes beside the rule.
   Retain its outer edges, tilt and score; baselines remain null. This does not
   refit rows, invent baselines, recover missing text, or delete whole boxes.
   Empty detector output is explicitly unresolved, never declared clean.

This is a separator-specific scout, **not a universal error scout**. The cost of
every dependency used by this path is included; Q7's general dense scout is not
silently computed or supplied from a cache. Cases outside this witness's scope
remain unchanged even when incorrect.

## Prediction → result

The complete before/after log is in the
[prototype README](../../prototypes/fast_lines/layout_barriers/README.md).

| Step | Prediction | Measured or visible result |
|---|---|---|
| R2.1 | Reuse Q7 reference products; render the 21 missing pages first | 195 reference renderings. Only 21 new baseline/dense-reference runs; old image hashes verified. Dense Hough also follows stamps, aligned letters and borders, so it is not truth. |
| R2.2 | Short run witness finds prose rules; agreement pages remain untouched | 20 nominated pages, 10 changed. Missed development `an-a73d22211479-p000301`; table `s2-200e977f2dab5291c42c-p00035` received two unwanted cell cuts. Zero agreement nominations. |
| R2.3 | More samples, short-break bridging and sustained fitting recover thin rules; enclosing-grid test protects tables | Recovered 40 cuts on the development a73d page and 39 on `…p000141`. Enclosing-grid protection failed: eight unwanted currency cuts on `s2-200e…p00035`, nine on `s2-831443dc5e6f1ccfbaf5-p00020`. |
| R2.4 | Require prose-width text on both sides; remove ineffective grid branch | Both currency regressions disappear. 18 changed pages. A new spanning-heading invariant fails, exposing a local paper-estimation bug: 42/43 tests pass. |
| R2.5 | Estimate paper outside the proposed line's narrow strip | 43/43 tests pass; one extra proposal vetoed on each of `s2-a0e233bc6efda91a641b-p00002` and `s2-c0b02fe229794d2fe76d-p00005`. 18 pages still change. |
| R2.6 | Freeze source, inspect every seam/page, measure three fresh passes | 308 changed source boxes on 18 pages; 24 nominations; 177 exactly unchanged pages. All 308 seams inspected. All 585 fresh outputs reproduce the frozen study exactly. Zero agreement corrections; all additions below 42 ms. |

No successful study was rerun with the same source and inputs. Three runtime
passes were declared in advance specifically to measure variation; they are not
three parameter trials. Earlier variants and failed-test evidence remain under
the ignored output tree. The final study is `study-f186b9c26f02`.

## Timing

CPU, macOS 26.5.1 arm64, OpenCV 5.0.0, single OpenCV and ONNX execution threads,
Q7's pinned Paddle small ONNX model at its existing 960 long-side input limit.
195 pages × three seeded shuffled repetitions = **585 executions**. The one
previously parked development orientation case is exported unchanged and
excluded from upright aggregate timings; it still has three measured detector
runs. No orientation detector or rotation was introduced.

Each execution freshly decodes the PNG, preprocesses, runs ONNX inference,
postprocesses DB output, and computes the scout and any correction. No cached
map, baseline, paper image or morphology enters the timed path. Cached baselines
and study outputs are compared **after** timing and match in all 585 executions.
Review rendering, JSON serialization and these assertions are excluded. PNG
decode is measured separately and included in the supplied end-to-end rows.
ONNX session startup: **0.016119417 s**; one warmup: **0.107522125 s**.
Python/process import startup was not measured. These are warm-session timings,
not a cold command-line startup claim.

All table times below are **milliseconds**. Quantiles pool the three declared
repetitions; the sample count is explicitly given. Totals are timed directly,
not made by adding separately calculated medians.

| Cohort | Pages / executions | Baseline median | Added median / p95 / max | Correction median / max | Total median / max |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 / 120 | 117.68875 | 10.93760 / 13.50056 / 23.16929 | 0 / 0 | 128.64177 / 168.41437 |
| Discrepancy set | 80 / 240 | 127.52438 | 11.68869 / 29.92195 / 41.65579 | 0 / 14.67117 | 138.78062 / 195.00696 |
| Extra set | 21 / 63 | 129.98183 | 10.70204 / 21.14883 / 21.69325 | 0 / 5.31375 | 141.09758 / 167.51479 |
| Upright development | 53 / 159 | 127.99454 | 11.43867 / 25.98865 / 31.40354 | 0 / 8.45100 | 140.81733 / 171.50546 |
| Activated pages, all sets | 24 / 72 | 134.42996 | 18.10104 / 35.51010 / 41.65579 | 7.31167 / 14.67117 | 155.43390 / 195.00696 |

Agreement scout-only median/p95/max: **10.746021 / 13.269743 / 22.979000 ms**.
The small additional wrapper/allocation cost remains included in “added”.
No correction runs on any agreement page, even as an unsuccessful attempt.
For the 24 nominated pages, six attempts abstain completely; cost follows this
physical witness, not an oracle of perfect need.

The maximum added time and correction time occur on
`s2-661ddf05c8865e7b2c45-p00010`. Maximum total processing is 195.006958 ms on
`s2-d12a9a4feb23254f4080-p00008`; including PNG decode, its maximum is
299.809042 ms. Agreement end-to-end median/p95/max including decode:
157.450813 / 184.550004 / 223.865875 ms.

Relative to Q7's reported ~34 ms mandatory scout and ~360 ms unconditional
agreement correction layer, this is a substantial reduction. It is **not** a
same-capability speedup: the path deliberately narrows to verified separators.
Its corrections are comfortably under one second, but many needed corrections
are not made at all.

## Visible results by direction

Directions label ink coverage, not correctness. All 54 development and 141 new
pages have final images and detector-format JSON. The 141 new labels are exactly
41 `ours_more`, 46 `paddle_more`, eight `both`, 46 `neither`. The latter contains
40 agreement controls and six straddle-only discrepancy pages.

| Direction | Pages | Nominated | Changed pages | Changed source boxes | Added median / max (ms) |
|---|---:|---:|---:|---:|---:|
| ours_more | 41 | 3 | 2 | 11 | 8.11917 / 30.68150 |
| paddle_more | 46 | 11 | 10 | 226 | 12.69819 / 33.08342 |
| both | 8 | 0 | 0 | 0 | 7.07863 / 12.93921 |
| neither | 46 | 6 | 4 | 28 | 11.31756 / 41.65579 |
| Development, including parked page | 54 | 4 | 2 | 43 | See upright timing table |

**Review scope:** every explicit-reference page and every final page was opened
in the 33 six-page overview sheets. Every changed source box was separately
checked at its cut, using 25 enlarged boards with raw pixels next to the overlay.
Selected full pages and supplied diff images were also enlarged. No discounted
ours-model lines are loaded or rendered by Q8. Unchanged pages were inspected at
overview scale, not every glyph. This is a recorded agent visual review, not an
independent human ground-truth annotation or a complete OCR accuracy metric.

The [195-page review ledger](FAST_LINES_ROUND2_REVIEW.json) binds each image hash,
direction, overview sheet and changed line IDs to the final source. Each page's
`.comparison.json` accounts for **every one of 13,639 original Paddle items**:
dense rule crossings, fast nomination and final action. There are 3,207 source
items crossed by some dense hypothesis and 590 nominated by the fast witness.
Those counts cannot be used as recall: many dense hypotheses are visibly wrong.

All 308 inspected cuts lie on printed separators between independent text;
no new glyph cut or wrong-column split was observed. These are **308 boundary
improvements**, not 308 certified correct final lines. Several new polygons
inherit vertical straddles, clipped letters at old edges or multirow regions.

### Every changed page

| Page | Direction | Cuts | Visible result and remaining limitation |
|---|---|---:|---|
| `an-a73d22211479-p000301` | development | 40 | Central prose columns separated. Source line 30 is still multirow; other top/bottom overlaps remain. |
| `s2-49598b2e848ab1f0ee1e-p00001` | development | 3 | Correct lower newspaper column divisions; most geometry unchanged. |
| `an-a73d22211479-p000047` | paddle_more | 31 | Correct central separator cuts; uncut crossings and row straddles remain. |
| `an-a73d22211479-p000141` | paddle_more | 39 | Clear column-boundary win; original row overlap remains. |
| `an-a73d22211479-p000231` | paddle_more | 4 | Correct divisions in the short upper two-column block; other joins remain. |
| `an-b9d6f9c086e2-p000162` | paddle_more | 34 | Correct prose-column boundary; oversized source boxes remain. |
| `an-b9d6f9c086e2-p000255` | paddle_more | 36 | Correct boundary; source line 5 still contains multiple rows. |
| `an-b9d6f9c086e2-p000370` | paddle_more | 32 | Correct boundary; inherited overlap around heavy print remains, including line 13. |
| `an-c8b96a901917-p000036` | ours_more, extra | 5 | Correct left-page column divisions; no missing-text recovery. |
| `s2-49598b2e848ab1f0ee1e-p00004` | ours_more | 6 | Correct newspaper divisions; missing ink and row ownership untouched. |
| `s2-4b80fdb36fbd33dfabcf-p00008` | paddle_more | 4 | Separates independent name/vote columns, retaining votes on their sides. |
| `s2-60f24a3d8a2d714767f2-p00004` | neither, discrepancy | 9 | Correct newspaper seams; inherited top/bottom geometry retained. |
| `s2-661ddf05c8865e7b2c45-p00004` | neither, discrepancy | 6 | Correct newspaper seams; other joined and overlapping rows remain. |
| `s2-661ddf05c8865e7b2c45-p00010` | neither, discrepancy | 2 | Two correct seams, many uncorrected joins. |
| `s2-922e617957fca8dfafd0-p00005` | paddle_more | 34 | Clear separation of independent name/vote columns; original overlaps not repaired. |
| `s2-a0e233bc6efda91a641b-p00002` | paddle_more | 3 | Correct name/vote divisions; the ink-side veto preserves a questionable fourth proposal. |
| `s2-c0b02fe229794d2fe76d-p00005` | neither, discrepancy | 11 | Correct newspaper divisions; another proposal vetoed; residual joins remain. |
| `s2-c0b02fe229794d2fe76d-p00007` | paddle_more | 9 | Correct newspaper divisions; other row geometry unchanged. |

**ours_more:** the two boundary wins are not false-negative recovery wins.
Zero previously uncovered text is recovered by this algorithm. A clear failure
is `an-1ba3fdb1436b-p000009`: the visible body line beginning “Ἐν τῇ πρὸς Θεὸν”
below the Theotokion label remains without a Paddle box. The same page's green
border disagreement is not missing text. On `an-c153f2c605b3-p000056`, much of
the green is border/stamp ink; blindly accepting ours would be wrong.

**paddle_more:** the strongest wins are the listed ruled prose and name columns.
No whole false text box is rejected. `an-ef481610a820-p000151` still has obvious
mirrored bleed-through detections beside the short answers and stamp fragments
at the bottom. Those are visible false positives left unresolved. Blue ink may
also be legitimate text: direction alone never authorises deletion.

**both:** all eight pages remain unchanged: `an-00f143ecce59-p000192`,
`an-00f143ecce59-p000258`, `an-1ba3fdb1436b-p000035`,
`an-c153f2c605b3-p000109`, `an-d83e7a198ade-p000115`,
`an-ef481610a820-p000150`, `s2-658e6dcb48b540357a9d-p00003`,
`s2-7534648e60694be1d180-p00021`. On the first, the bottom body line remains
missed while drop-cap/multirow geometry and stamp boxes remain. On
`an-ef481610a820-p000150`, mirrored bleed-through boxes remain; some ours-only
green is also bleed-through. This path offers no solution to either problem.

**Agreement and neither:** all 40 agreement pages retain exact polygons, scores,
order and count. Controls include the clean single-column
`s2-be269b8c315b16befc35-p00001` and the difficult curved
`s2-86865c33eef5932c013b-p00023`; preservation is not certification of their
baseline quality. Four of six non-agreement `neither` pages receive the listed
column cuts. It would be wrong to equate `neither` with the agreement set.

## All observed failure mechanisms and regressions

* **Final gate false negatives:** clear newspaper rules remain uncorrected on
  `s2-661ddf05c8865e7b2c45-p00005`, `s2-49598b2e848ab1f0ee1e-p00005` and
  `s2-d12a9a4feb23254f4080-p00008`. Their coarse nomination succeeds, but the
  straight-stroke verifier abstains. Development `s2-661ddf…p00009` also abstains.
* **Other completely abstained nominations:** development
  `s2-93f8070059f938bda524-p00001` fails raw support/clear-side checks;
  `an-ffccc97c07de-p000354` fails clear-side checks in its bilingual dictionary.
  These six named pages are the complete list of nominated-but-unchanged pages.
* **Incomplete corrections:** all preserved old outer edges can retain
  row/endpoint errors. The changed-page table and source-ID ledger identify the
  observed multirow examples. Some crossings also fail the six-height width,
  continuity or clear-side requirement and remain unsplit. The path does not
  promise complete column separation even on a changed page.
* **Missing text, false foreground and unruled layouts:** no mechanism was
  materialised for these. Named clear examples are above. Drop caps, marginalia,
  bleed-through, stamps, tables and physical-leaf layout remain unresolved where
  the original detector is wrong. The 177 unchanged pages are enumerated in the
  ledger; their baseline errors were not exhaustively glyph-annotated.
* **Orientation:** the established parked development page is unchanged.
  Supplied sideways table `s2-7534648e60694be1d180-p00016` also remains unchanged.
  No orientation work is claimed.
* **Retired regressions:** two currency tables were wrongly divided in R2.2/R2.3;
  both now exactly match baseline. The synthetic spanning-heading regression
  exposed in R2.4 is fixed. No new seam regression was observed in final review,
  but the seen-page scope does not establish unseen-page precision.

## View, validate and reproduce

Open the [local gallery](../../.astra/fast_lines/out/round2/rule_separators/index.html).
It links all 195 per-page images, detector JSON, decisions, per-line reference
comparison and seam close-ups. Grey-blue is an unchanged original box; changed
old boxes are grey; new polygons are green over the old geometry; removed ink
is red. No additional foreground ink is claimed by this path. JSON uses full-page
pixel polygons, null baselines, inherited scores and `unit: "line"`. Its `seconds`
is the complete first measured detector-plus-path time, excluding decode/review
I/O; the earlier study's diagnostic JSON explicitly predates final timing.

Raw numbers and receipts, all outside git:

* [benchmark.json](../../.astra/fast_lines/out/round2/rule_separators/benchmark.json): all 585 timing rows, seeded order, source/model hashes and summaries.
* [benchmark.raw.jsonl](../../.astra/fast_lines/out/round2/rule_separators/benchmark.raw.jsonl): append-only measured timing rows.
* [validation.json](../../.astra/fast_lines/out/round2/rule_separators/validation.json): all artifact hashes and validation counts.
* `.astra/fast_lines/out/round2/shared/registry/`: input/config/source-keyed experiment receipts.
* [FAST_LINES_ROUND2_REVIEW.json](FAST_LINES_ROUND2_REVIEW.json): tracked review document; every page and every changed source ID, with explicit limits on adjudication.

Final algorithm source key:
`f186b9c26f026d4bf495fa6907029c0e40edf94f389406521f3a3657728eca87`.
Benchmark receipt:
`f49ee17e376528601ca182bb67ff64511164c4bfd1753e4018951de797b6be3d`.

From the worktree root, with the required Python:

```sh
export PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY -m prototypes.fast_lines.round2 references
$PY -m prototypes.fast_lines.round2 study
$PY -m prototypes.fast_lines.round2 review
$PY -m prototypes.fast_lines.round2 benchmark
$PY -m prototypes.fast_lines.round2 publish
$PY -m prototypes.fast_lines.validate_round2
$PY -m pytest prototypes/fast_lines/tests -q -p no:cacheprovider
```

Completed experiments are skipped by receipts; don't remove receipts to rerun
the same experiment. `review`, `publish` and `validate_round2` only consume saved
products. Validation passed for 195 pages, 13,639 source items, 308 contained
polygon splits and all 40 exact agreement controls. The isolated prototype
suite passes **43/43** tests. The actual fresh 585-execution harness also checks
baseline and output equality, so correctness is not inferred from unit tests alone.

## Readiness and next work

`fast.run(gray, small_items)` is ready as an **optional separator module
candidate**: independent of production pages, bounded to nominated corridors,
measured end to end and accompanied by reviewable abstention reasons. It is not
ready as the general “fix whatever the small detector missed” layer. The owner's
held-out evaluation remains necessary; those pages were not accessed.

Next I would retain this gate, repair vertical straddles only inside its proven
column regions, and develop independent witnesses for uncovered text and spatial
foreground ownership. Each needs explicit raw-pixel examples from both
directions and its own agreement cost budget. I would not restore unconditional
Hough/A03 or loosen rule support merely to improve the page-count metric. No
quantitative foreground FN/FP recall, independent human gold review, cold-process
latency or unseen-page quality result was completed in this round.

## Commit handoff

The sandbox rejected Git's attempt to create
`.git/worktrees/greek-ocr-toolkit-astra-lines4/index.lock` with `Operation not
permitted`, before staging. No commit or push was made. The requested fallback
is [Q8.patch](../../.astra/Q8.patch) and
[commit-Q8.sh](../../.astra/commit-Q8.sh). The patch was checked and applied to a
temporary copy of the nine affected paths from `4e2199d`, then compared byte for
byte with the delivered files. Its hash-bound receipt is
`.astra/Q8-patch-validation.json`. The script checks branch, base commit, empty
index and file hashes before staging only these nine code/document paths and
committing with the requested trailers; it does not push.
