# Round 7, task 3: ink follow-up

Work is on default `Stack()`, from `afa0c42821d554c8922fe83265701d3b371ac1bc`. The opt-in row model was not promoted or used. Its four protected modules, `greekocr/pages/`, its tests and the held-out 44 pages were not changed or inspected.

The owner's verdict is still the appropriate starting point: **“faintness seems much improved although not perfect”.** This task is **partial**. A clipped neighboring stroke no longer protects the mirrored running head on 44b5 p5; a separate solid-mass witness removes the reviewed blob; a recurrent perimeter rendering removes complete border segments. The short-ghost/normal-run problem and universal growth permission are not solved. The attempted all-stage growth adapter lost real text and was withdrawn.

Artifacts are under `.astra/fast_lines/out/round7/T3_ink/`. `final-v1/index.html` is the changed-page Paddle / R6 / task-3 gallery. Detector JSON and raw timing receipts cover all 208 pages. `explicit-v1/`, `controls/`, `routes/`, `pilot-loss/`, `frame-v*/` and `ivy-v2/` retain component evidence and counterexamples. Intermediate failures are not final output.

## Checklist disposition

| Item | Disposition | Evidence and remaining obstruction |
|---|---|---|
| 3-01, mirror/seal ownership | **Not closed; partial** | Existing mirror and rim mechanisms are retained. 44b5 p5 #123 is corrected by the clipped-component fix. ef481 p150/p151 short margin ghosts, 0ce9's mirrored heading and 93f8's faint pieces remain. A rim witness is not whole-watermark ownership. |
| 3-02, frames/motifs/blob | **Not closed; partial** | Native repeated perimeter units and a separate filled-mass test are rendered. Complete frame segments can be excluded; mixed text/border segments remain. c99 p25 upper ivy remains, while its approved earlier removal is retained. |
| 3-03, faintness and growth | **Not closed** | Real pale-front and mixed-fading controls pass. A typed `NormalInk` contract and explicit run witness are available for study. The integrated adapter failed found-text retention and cost; default stages do **not** yet share its pre-geometry reference or enforce its growth rule. `short_ambiguous` and the substantial-normal-area retention guard remain unresolved. |
| 3-04, scout/final footprint/cache | **Not closed; partial** | Polygon strings are replaced by page-local ownership/generation tokens. Native/reduced/scout comparisons are recorded, including a reduced-resolution blob false positive. Shared pre-geometry calibration is still unpromoted, and a changed final footprint can still cause the old final calibration path to run. |

Source/commit and final acceptance/timing receipt are recorded in the handoff section below. No checklist is represented as closed by passing prototype tests.

## Faintness, normal letters and retained short text

### Explicit rendering and inspected cases

`ink_faintness.components` renders native component boundaries, ridge contrast, peak contrast, noise, stroke width, clipping and body size. The page's normal print supplies the reference. Red component outlines are below its faint boundary; green outlines are above it. Green does **not** certify readable front print. The renderer's per-component records are evidence, not transcribed characters.

`explicit-v1/cases.json` and its native images use the owner's **reading order** from `review_r6/reading_order.py`, not detector-list positions. Each requested region was inspected separately:

| Page and owner number | Observation | Final task-3 disposition |
|---|---|---|
| ef481 p150 #3 | A visibly faint edge piece has a component near core .43 / peak .47; the local boundary is about .377. | Still retained; unresolved. |
| ef481 p151 #9, #10, #29, #30 | Short pale margin marks can have one .4–.5 contrast component or a dark peak. Neither a three-body run nor reliable reflected-glyph witnesses are present. | All remain unresolved. |
| 44b5 p5 #123 | The mirrored running head is pale throughout. A clipped black stroke from neighboring ink had supplied the normal-area guard. | The clipped stroke no longer supplies that guard; the head is removed. |
| 93f8 p1 #1, #89, #117, #126, #127 | The late reference's spread is contaminated by the mixed front/back distribution: boundary about .191. The earlier sample gives about .372. | The promising early-reference correction is not promoted; all remain open, including #127's leftover piece. |
| 93f8 p1 #5 | A real heading is extended sideways over faint letters. | Open; whole-line faintness must not delete the real heading. |
| 8686 p26 #9 and #40 | Real phrases have faint added tails. | Open; the rejected growth adapter is not a fix. |
| 0ce9 p1 mirrored short heading | Corrected reading-order #16 contains a pale mirrored heading plus a black dash: the dash is counted as a body, with area 352, exceeding the median faint-body area. It protects the ghost without a run. Front heading #4 is a separate retained control. | Open. The initial study's #1 crop was the front page number, not this heading; corrected crops are explicitly identified in the supplemental evidence. |

The runtime change is narrow: **clipped components cannot contribute the normal-area retention guard**. A normal run already required three whole, unclipped bodies. Excluding a clipped neighboring stroke from the other guard closes this particular bypass, not the general one-dark-letter problem. The normal body/area and `short_ambiguous` branches were not relabeled as successful normal-run evidence.

### Predict → test → inspect cycles

1. Native crops explained why aggregate “faint” scores miss short ghosts and mixed real/faint rows. The old reference is particularly weak on 93f8.
2. Direct/reflected glyph matching with a larger context was tested. It can vote “back” for the real 93f8 heading, and favor direct matches on a mirrored capital heading. Lowering vote counts was rejected. See `probe.txt` and the native owner crops.
3. A single typed reference was computed before geometry using the existing `analyze(require_reference=True)`. Replacing the old scout boundary outright missed earlier nominations; taking the union of old nominations and this reference repaired that nomination failure. It did not establish ownership.
4. Applying the reference plus a growth adapter through early field replacement, geometry/joining, type completion, native envelopes and late field replacement changed 44 pages. `pilot-loss/an-466cffad2cba-p000277.1.jpg` shows a real ending clipped. `pilot-loss/s2-49598b2e848ab1f0ee1e-p00004.9.jpg` shows a whole genuine row lost after later composition changed. This adapter was withdrawn.
5. Calibration alone, with the growth decisions only logged, changed four pages. It improved the 93f8 ghosts but revived a previously removed faint segment on 8686 p26. It also added substantial median ink cost. It was not promoted.
6. Isolating the clipped-neighbor fix on all 208 changed only 44b5 p5. The final stack retains that change, without the failed reference/growth integration.

The attempted all-page integration's **diagnostic**, non-handoff medians were 29.285 ms before versus 48.783 ms for all ink work; the early reference itself was 25.070 ms. These are failure evidence, not the final timing claim.

### Real controls and what they establish

Native `controls/` crops include 1be6 p215 #45 and #49 (pale front print), #11 and #23 (readable print with faded/broken parts), 466 p242 #20 (short genuine “οἱ”) and 778 p17 #30 (handwriting). Slow native, reduced explicit and localized native decisions are recorded against one reference; none is deleted. The palest page has a broad reference with a zero lower faint boundary: preservation here is an abstention, not proof of a universally successful front/back classifier.

The real-image tests recompute the reference from the actual pixels; stored scores are not test inputs. `round7_controls.json` is study data only. The existing strict xfail stays: the synthetic lighter-front control still fails, and removing the marker would misrepresent that limitation. Existing short/connected-word guards still protect legitimate text but also protect some ghosts. The “Διαμπάξ, διόλου.” and “σι τὸ ἴ;” examples remain explicit limitations of the unchanged short-row/recovery behavior; no new recovery is claimed.

### Contract for the next geometry task

`shared/ink_normal.py` imports the **existing** `NormalInk` unchanged. It adds no second contrast statistic.

- `calibrate(gray, items, height=None) -> (PageInk, evidence)` calls `ink_faintness.analyze(require_reference=True)` once. Call it **before** geometry and bind it to the same pixels. `PageInk` holds the typed reference, detector-height proxy, measured body height/stroke and image size.
- `may_grow(gray, polygon, reference: NormalInk, height, body_height=None, added_polygon=None) -> Growth` observes a native normal-body run in the supplied terminal context. With `added_polygon`, a whole run body must reach the new region. `Growth.allowed`, native `[N,4]` witness bounds and an explicit observed/unknown state are returned.
- Coordinates, height and stroke are native page pixels. Contrast/spread/boundary are dimensionless. Support is a component count. Three whole bodies must share the observed row and two independent adjacency links. A single dark body, area, short-word ambiguity or detector confidence is never affirmative growth evidence.
- Unknown reference/run means **no permission**, not deletion of found text. An affirmative witness is photometric support, not proof that the ink is front print. Existing owned ink, including punctuation and touching letters, needs an independent retention obligation.

**This is a diagnostic contract, not an approved adapter.** `features_ink/round7_growth_experiment.py` preserves the rejected adapter for reproduction. It is not imported by `Stack`. The next geometry task must preserve the full previously found ink and validate short/touching/initial endpoints before integrating it. A universal all-stage call requirement is therefore still unmet.

## Frames, ivy and the blob

### Recurrent perimeter rendering

`shared/ink_frame_field.py` first nominates long narrow vertical segments and aligned compact fragments, in letter-height units. It observes native connected units, normalized shape recurrence and a symmetric distance witness for overfilled versions of a motif. Two separated vertical recurrent chains plus an orthogonal recurrent chain establish the observed perimeter. Adjacent recurrence matters: spatial alignment alone is insufficient. The enclosed page area is never a non-text mask.

The slow route records native unit boxes and traces native ink transversely through the witnessed perimeter corridor. The explicit route observes units at at most 16 samples per height; the coarse route uses 8, with the same native corridor trace. A separate geometry-only nomination is also recorded. Neither equality of unit counts nor recurrence alone proves text exclusion. **The reduced variants are not approved ownership routes:** on p154 they select parts of the last genuine row as a horizontal cross-chain. Native blue boxes select the bottom flower band; orange/green boxes on the words are an explicit false-positive witness in `routes/*p000154.comparison.jpg`. Default uses native rendering behind the geometry-only scout.

The iterations are retained in `frame-v1` through `frame-v14-all`:

- A lobe-based motif description failed when over-inking filled the notches.
- Raw normalized recurrence needed sloping-chain consolidation and separate compact fragments to render p104/p154.
- Symmetric distance evidence recovered filled versions without naming a book or page.
- The initial subtraction left border fringes as apparent text fragments. A body-only remainder filter and hole skipping were unsafe; those variants are not in the default path.
- Full 208 inspection exposed false perimeters through a sideways numeric table (6419 p1), another table (7534 p16), and ditto columns on 8686 p7. Aligned repeated letters were a counterexample to the claimed feature. Requiring adjacent recurrent units rejected these in the final census.
- Native transverse observation extends the observed corridor to witnessed perpendicular sides. It renders most of the full border, but still does not grant safe mixed-box subtraction.

The final default adapter, `exclude_whole`, removes a **whole segment only** when the measured perimeter owns every observed letter-sized body. It never subtracts an annulus from a text crop or removes residual pieces on a body-count test. All mixed segments remain unchanged. The candidate removed 5 / 10 / 16 / 2 / 24 complete segments on 7792 p59 / p104 / p107 / p138 / p154. Native handoff inspection, not those counts, determines whether these deletions are acceptable.

**Still wrong:** this does not make every border leave every text crop. A mixed border/text crop and some disconnected corners remain. Thus the owner's whole-border requirement and checklist 3-02 remain open. The body definition itself is heuristic; a future complete ownership model must represent marks and large initials as well.

### Upper ivy

On c99 p25, the old explicit motif matcher finds a period around 7.56 heights, coverage .502 and span .633 in its expanded context. Those are below its unchanged acceptance condition. A second experiment supplied half-, whole- and one-and-a-half-period templates covering the full band height. Each failed to find four qualifying copies: the ivy's deformation/print variation defeats the full rigid template. No threshold was lowered. `ivy-v2/` retains these failures. The upper strip remains; the earlier approved removal remains protected.

### Solid ink mass

`shared/ink_solid.py` is separate from faintness. Its rendering shows the inscribed interior disk, counters and the same connected mass's enclosing extent. A compact isolated mark must contain a disk at least h/4 in radius, no counter, and no long thin appendage outside twice that disk radius. Isolation is at least 2h; candidate extents are between h/2 and 2h. These are explicit physical size settings, not learned probabilities. They do not prove that all such marks in unseen print are non-text.

The first attempt used median local distance-transform ridges; ragged edge specks made the true blob look thin. The second used the connected interior disk and its enclosing radius. Native full 208 evidence identified the reviewed 922e p1 #23 mark. The reduced explicit route also nominated e259 p176: downsampling removed a small counter. That mismatch was inspected and **native agreement is now required** behind the cheap geometry/reduced nomination. The native-negative mark stays.

The final blob exclusion is the exact detector polygon with reason `solid ink mass`, never a faintness excuse or an inferred stamp interior. Nearby text, holes and thin strokes remain negative controls.

## Stable footprint identity and cost

`shared/ink_footprints.py` replaces `str(polygon)` identities with page-local integer ownership/revision tokens. Copies keep their token; changed coordinates or source ownership create a new generation. Sibling pieces receive distinct generations. The ledger compares against immutable numeric geometry records; it does not treat a copied old token as a fresh certificate. Tokens are transported internally and exported in separate evidence, not added to detector-format items.

This closes the polygon-string implementation issue, not the whole calibrated-cache obligation. The default changed-footprint recheck still uses the existing final calibration path. No reference cache is claimed when it does not exist.

An exact uint8 histogram computes the native crop's median and 90th percentile in one pass; this replaces two order-statistic scans without changing their values. All new frame/blob/identity work is included in the final ink cost. Parent stages already containing substage timings are counted only once.

## Handoff acceptance and timing

Final measurements and visual dispositions follow. The commit/fallback receipt is recorded in `final-v1/handoff.json`. P0 is dark pixels (`gray < 200`) inside a round-6 polygon, outside only an old approved exclusion, absent from the final crop union. New removals do not automatically excuse those pixels. Clusters at least h²/40 and every owner-commented-page loss are retained for inspection. P1/P5/P11 are reassessed on changed pages; unchanged pages carry their previous verdicts. Column changes and prior exclusion footprints are compared across all 208.

## What the next task still needs

1. A real run/letter representation that distinguishes normal connected front letters from isolated dark contamination without using the short-word guard as positive evidence.
2. A pre-geometry reference whose early sampling preserves every approved exclusion and whose cost follows a validated scout. The failed always-calibrate path must not quietly return as default.
3. Growth as an extension of independently preserved found ink, including punctuation, large initials, touching glyphs and wide gaps. The failed adapter demonstrates why a photometric test alone is insufficient.
4. Complete border ownership and mixed-crop decomposition, then deformation-aware ivy evidence. Alignment/recurrence and frame complements cannot certify non-text.

Some intermediate source revisions were not frozen independently; their images and measurements are retained, and the major rejected adapters/patch are saved. Only the final frozen source is claimed to reproduce the complete handoff outputs. No generic stamp/image or unreadable-character classifier is claimed.


## Frozen handoff results

The two before passes and two final passes each cover 208 supplied pages, sequentially, with a warmed Paddle session. Both final passes reproduce every detector item. 201 pages are exactly unchanged from R6; the remaining 7 only delete whole old segments. All retained items are otherwise identical to R6. No baseline polygon is narrowed or newly grown by this handoff.

The complete prototype suite is **253 passed, 1 strict expected failure**. `tests-final.txt` records the still-failing faint-front synthetic control. `final-v1/acceptance/receipt.json` has **30,602** schema/exclusion/boundary checks. The final code snapshot key is `1a4f9c786378660a0121eaaf8834bfe079ed070081c84e69a7a20536c62cc36a`; `source.json` binds individual source files, model hash, platform and starting commit. Outputs are outside Git.

P0 removed 327,500 dark pixels: 323,418 in flower-frame segments, 1,573 in the blob and 2,509 in the mirrored head. All 14 native contact-sheet views were inspected, with extra 2h-context crops for p107's bottom border/catchword and p154's lower corner. These are observed non-text losses; **no unexplained found-text loss was observed**, rather than a claim of mathematically proven glyph identity. The raw loss masks/counts are not reduced to zero by adding exclusions.

All 236 prior exact exclusion polygons remain: 61 back-print, 22 seal-rim, 16 ornament and 137 relative-faintness exclusions. Task 3 adds 57 frame exclusions, 1 solid mass and 1 relative-faintness exclusion. New ink intrusion under prior exclusions is 0. Every prior column-change result is exact. The old fixed R4-41 faint removal on 44b5 p5 remains distinct from the newly fixed O10 #123. Existing watermark/bottom-border exclusions on p59/p107 and 25 faint removals on p154 remain. The p107 initial and bottom catchword remain visibly intact.

O10 and O24 / R4-12 are fixed for the specifically reviewed head/blob. O21/O22, R4-03/R4-05/R4-22/R4-24 and C05 improve but remain partial: mixed borders, disconnected corners, the p107 inner decorative strips and c99 upper ivy are not all removed. All other owner/row verdicts carry forward unchanged. None of these per-comment improvements closes the full four-item task checklist.

### Raw timing, milliseconds

Ink cost is charged conservatively as `correction_s` minus the non-ink parent stages (Q8/scout, edge/field geometry, geometry_all, type, shape, row partition and reconciliation). This includes all ink stages, new native frame work, blob confirmation, identity transport and otherwise unattributed composition bookkeeping. The old polygon-string work was not separately timed, so comparing only logged stage sums would undercharge the old path. Nested substage counters are not added twice. `timing-raw.json`, `timing-summary.json` and the per-page repeat receipts retain the raw values.

| Cohort / charged ink | Before 1 | Before 2 | Task 3-1 | Task 3-2 |
|---|---:|---:|---:|---:|
| All 208 median |30.770|31.542|30.539|30.854|
| All 208 p95 |176.497|167.682|191.628|196.649|
| All 208 maximum |417.660|403.325|423.198|434.171|
| Agreement 40 median |9.615|9.306|9.643|9.699|
| Agreement 40 p95 |49.797|50.098|41.915|43.627|
| Agreement 40 maximum |59.620|62.110|51.266|54.565|

All 208 median ink time does not increase in these two observed passes. Agreement median increases 0.028 / 0.393 ms; **zero added agreement overhead is not established**. The ink p95 gets worse. This is measured behavior on these pages, not an unseen-page cost guarantee.

| Complete correction | Before 1 | Before 2 | Task 3-1 | Task 3-2 |
|---|---:|---:|---:|---:|
| All 208 median |192.145|198.284|197.655|198.039|
| All 208 maximum, 4959 p1 |2474.117|2461.245|2434.031|2476.314|
| Discrepancy 101 median |209.128|215.037|217.483|225.402|
| Discrepancy 101 maximum, 4959 p5 |2272.115|2272.521|2239.653|2227.657|

The complete stack is still over 1 second on 23/23 before pages and 22/24 final pages. Task 4's speed obligation remains. The OpenCV request is 2 threads; this macOS GCD build reports 10, so this is not a fixed-worker guarantee. File decode, detector and total times are separately recorded; image/JSON review export is outside the file-to-lines timer.

### Route receipts and reproducibility

The geometry-only frame scout nominates 15 pages; native perimeter evidence survives on 5. The solid geometry scout nominates 15 compact segments; reduced/native disagreement on e259 p176 is rejected by native confirmation. The three faintness renderings agree on all 16 corrected numbered study regions (including the separate front/mirrored 0ce9 controls), but agree on several **wrong** retentions: 93f8 has a wrong reference; ef481 and 0ce9 have no normal run yet remain protected. The scout already nominates these ghosts. This is a classifier/ownership failure, not a request to broaden nomination.

Native / 16px-per-height / 8px-per-height frame unit counts are 136/130/114 on p59, 122/122/119 on p104, 135/131/133 on p107, 114/117/73 on p138, 115/97/79 on p154. Counts are not acceptance: the last includes the explicitly inspected false last-row units. Native/default ownership alone was admitted.

To reproduce the frozen candidate, use the supplied Python with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=.`:

```sh
python -m pytest prototypes/fast_lines -q
python -m prototypes.fast_lines.features_ink.round7_benchmark NEW_OUTPUT_NAME
python -m prototypes.fast_lines.features_ink.round7_acceptance NEW_OUTPUT_NAME
python -m prototypes.fast_lines.features_ink.round7_routes
python -m prototypes.fast_lines.features_ink.round7_controls
```

`NEW_OUTPUT_NAME` must not exist. Use the frozen `final-v1/source/` snapshot and source receipt if later work changes the branch. Diagnostic route/control exporters use fixed study directories; preserve existing artifacts before regenerating them. Raw helper commands for the late numbered-crop correction and timing aggregation are also retained under the output directory.

### Commit handoff

Staging was attempted on `astra/ff-ink`. Git could not create the worktree's `index.lock` (`Operation not permitted`), so no commit or push was made. The fallback is `.astra/commit-FT3-r7.patch`, `.astra/commit-FT3-r7.sh` and `.astra/commit-FT3-r7.validation.json`. The script checks the branch, base commit and all 20 owned file hashes before staging, and uses the exact requested trailers. Forward/reverse application and reconstructed-file hashes are checked in the validation receipt. The final artifact receipt is `final-v1/handoff.json`.
