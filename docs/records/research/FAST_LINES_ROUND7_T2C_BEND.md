# Round 7 task 2c: bend edits of retained segments

**PARTIAL. Do not promote. `Stack()` keeps the merged round-6/task-3 behavior. `Stack(bend=True)` selects this experiment.** The required curvature examples do not all pass. The field scout still misses genuine curl, the column partition is incomplete on spreads, and removing the old field replacement changes found-text coverage beyond the narrow edits. A zero-loss check against the adapter's own input is not preservation of the saved final R6 output.

Starting commit: `1dd05c2`. The 44 held-out pages were not accessed. Production `greekocr/pages` and its tests are untouched. No new row-model ownership partition was introduced. The old experimental `row_model=True` route is unchanged apart from moving reusable definitions; it is never called by this candidate.

## What was implemented

`geometry_bend.py` fits one column field from the edge scout's map-ridge samples. Repeated neighboring segment endpoints nominate columns; M13 rules and a reduced-image white channel certify their boundaries. Each column subtracts one common affine slope before nominating a bend. Three consecutive observed ridge departures must agree. Nomination is measured from the samples, not from the fitted curve. Reduced body components refine a tensor field with a linear term and two cubic end terms, quadratic in y. Body height is measured in a column; row phase peaks come from observed components, never empty pitch slots.

`geometry_bend_edits.py` keeps input crops, splits an observed two-row box at a native white corridor, and unions admitted terminal growth with the kept polygon. A piece can be retired only after a native dark-pixel transfer check. New rows require a native normal run on an observed unoccupied phase. Tables nominated by the existing short-cell lattice or multiple verified finite rules are protected. Running-head separation uses the measured pitch gap. The adapter protects completed initials and tall crop geometry; **this is not yet the full required native large-component test**.

There is no mesh render, unbent detector rerun, residual-parent subtraction or `geometry_row_context` on the bend route. It replaces both early and late M15–M18 field application on that route, including flat pages. The old code remains available only to preserve the unpromoted default. Changed items use the existing `page_field` abstention marker for local envelopes and B splitting. The final deletion checks remain in the old order.

`NormalInk` now lives in `ink_normal.py`. The historical row module imports it there; the growth contract no longer imports the row model. The shared finite-rule verifier and smooth-corridor primitive also have standalone modules. `may_grow` remains a diagnostic region guard. The new `follow_letters` operation uses component material positions and a separate normal decision for every body. Two kept terminal letters can support one new letter. A faint body breaks the run. Found units survive even when faint or when the reference is unknown. No early reference is supplied to the deletion classifier.

The calibration is performed once on nominated curved pages, before the adapter mutates geometry. It is not yet limited to pages with a fully confirmed growth proposal; that distinction matters to timing. Geometry is read at reduced scale; native terminal contexts and split corridors authorize edits. The native loss raster is the one intentional whole-column verification.

## Explicit rendering before the cheap route

All artifacts are under `.astra/fast_lines/out/round7/T2c_bend/`.

`explicit-v1` was rendered and inspected on all 14 requested pages before adding crop mutations. It showed underfit curled endpoints, extra phase peaks and the false merged-column bend on 9ea1 p218. Subsequent native renderings tested cubic end terms, body refinement and channel certification. A rejected local-channel variant produced spurious narrow regions and an implausible field across the d83 spread; it is not the handoff source. Early benchmark directories are experiments, not timing evidence.

`native-handoff/`, `reduced-handoff/` and `route-comparison/` retain the final native/reduced observations on all 14 pages. `route-comparison.json` contains 1,237 nearest-phase path comparisons. Those correspondences are diagnostic: matching row counts or nearby paths does not prove correct rows. Native/reduced rows differ, including 3229 p6 and the table. Both routes share the scout's misses. The rendered bend on 8686 p7 is broadly plausible, but the measured scout fails to nominate it. On 8686 p5 the final nomination chooses the left side although the problem is the right curl. These are failures, not abstentions counted as successes.

Lengths are in body heights except the 1,200-pixel maximum thumbnail used to certify channels. The cubic hinges at normalized x = ±0.4, the h/4 profile smoothing, h/2 phase tolerance and three-body run are explicit modeling choices, **not empirically established universal constants**. The fixed thumbnail is another unresolved departure from a fully body-scaled route.

## Gap rule and ink contract

Every changed column logs `word_gaps_h` and `gap_limit_h`. Positive gaps shorter than 2h are measured among bodies assigned to each observed phase. The maximum permitted gap is `min(2h, max(h, 1.5 × measured 95th-percentile gap))`. The 1h floor avoids mistaking letter spacing for the page's word-space limit when the sample contains few actual word gaps. The 2h ceiling follows A4; a strict 1h ceiling from T3 can block a normal space before a short curled word. This is a measured, bounded proposal and remains experimental; the percentile/margin need independent validation. Ink beyond a gap is eligible only as a separate three-body native run, never as a bridge from the retained crop.

Each new body must meet the typed page reference, be at least two-thirds of body height, and lie within h/2 of the predicted material row. The old crop is the geometric floor. A new isolated normal body does not authorize an arbitrary extension to a proposed edge. Small punctuation already held by a crop does not face a growth test. The extension band can include adjacent marks; its ownership of every new accent/punctuation mark has not been fully established. Exclusion holes that the output polygon format cannot represent are not silently filled or converted to triangular OCR fragments.

## Invariant and limits

The adapter tests gray <200 inside the replaced input crops, outside the supplied early exclusions, against the union of its proposed column output. Any remaining loss returns the column transaction unchanged and is logged as a failure. Splits and absorbed pieces also receive native transfer checks.

**This does not close A7.** At the early replacement point, the input crops are retained pre-field segments, not the saved final R6 polygons. Later type, B, faintness and duplicate operations can change the result. In particular, removing the old field affects 38 historically field-replaced pages. The offline acceptance therefore separately checks final R6 found pixels and all exact R6/task-3 exclusion footprints. Those failures cannot be excused by the adapter's local invariant or by new removals.

## Acceptance and individual comments

The final handoff is `final-v2/`: 208 pages, two timing passes, a separate fresh 208-page replay, and unchanged runtime source hashes throughout. A field drawing, passing unit tests or fewer segments is never a passing owner-comment verdict. Promotion requires all five acceptance groups; it is disabled.

### Native/reduced visual audit of the field

All 14 requested route comparisons were opened and inspected. These are field observations, separate from the final OCR-crop review below.

| Pages | Observation |
|---|---|
| 3229 p4/p5 | The shared curve follows the main block and curls on the appropriate side. Some short/header phases extend across empty margins in the diagnostic drawing. New crop correctness still depends on endpoints and native retention. |
| 3229 p6 | Both routes draw a plausible left bend, with 35 versus 36 observed phases. The final scout does not nominate the column, so the bend cannot fix the required boxes. |
| 4959 p1/p5 | Separate main columns; left-side body registration is close between routes. It does not establish missing-row recovery or successful absorption of the lower tilted pieces. |
| 4959 p4 | The right-edge bend is represented. One unmatched/shifted phase makes the nearest-path comparison exceed one body height. It is not route equality. |
| 44b5 p2 | Body fields broadly match, but only the left column is nominated. Removing the old wrongly phased field bands is not itself proof of a correct replacement. |
| 8686 p5 | Some upper faint/noisy ink becomes additional observed phases. Reduced observation has an extra top phase. The nominated side is wrong; right-end edits are not authorized by this scout. |
| 8686 p7 | Both drawings show a right bend, but the scout reports no curved column. Leader/table phases are drawn diagnostically and must not be mistaken for emitted bands. |
| c8 p68 | Four physical text columns are visible in the final drawing; all are inactive. The old cross-leaf field is absent from the candidate. |
| e259 p198 | Two separated inactive regions; broadly affine body rows. |
| 9ea1 p218 | The extreme old all-spread bend is gone, but the final regions still include an empty narrow region and an incorrect region spanning the inner content/gutter. All regions are inactive. **Column separation is not accepted.** |
| d83 p99 | The three inferred regions do not represent its two leaves. Inactive fitted paths extrapolate badly through the gutter. The scout prevents crop edits but this is a failed explicit field, not a verified flat model. |
| 8314 p20 | Inactive fits in the left table domain extrapolate wildly. No bend crop operation runs. A preserved table control does not validate this field construction. |

Among the 346 diagnostic matches in nominated columns, maximum path difference is 1.455h and p95 is 0.154h. The large differences include unmatched phase peaks, so they are not all pure bend displacement errors. Across every drawn fit, the maximum is 81.285h, driven by invalid inactive extrapolations. That number is retained rather than excluding the failed controls from the study.

### Amendment disposition before final acceptance

| Amendment | Disposition |
|---|---|
| A1 | Incomplete: columns and affine-first measured scout implemented; spread partition and scout recall fail. The scout now pays reduced-image/body work and is not a 4ms map-only operation. |
| A2 | Partial: shared low-order field and measured column bodies/pitch; native endpoints/corridors. Not every native/reduced phase agrees. |
| A3 | Partial: body material phase and complete-transfer check, with column rollback on failed retirement. Curled pieces remain separate on required examples. |
| A4 | Partial: per-body normal continuity, bounded measured gaps, retained-crop floor. Endpoint geometry/marks and every protected rule still require final audit. |
| A5 | Implemented for nominated two-row boxes: a native white corridor with smoothed shoulders; unresolved corridors leave the box intact. The requested rows are not all nominated or split. |
| A6 | Incomplete: computed table/header/crop-size protection exists; the native large-component requirement and every missed-row control are not fully covered. |
| A7 | Incomplete: transactional native input retention is checked, but final saved-R6 retention is a separate failing obligation. |
| A8 | Implemented on the opt-in route: neither early nor late field replacement runs. Default is intentionally retained because promotion fails. |

The new numeric primitives are array based. The scout still accepts the edge/rule evidence dictionaries and the legacy adapter transports item/evidence dictionaries; this is **not** a claim of complete Rust-ready array-only plumbing. Task 4 can remove the historical row modules after resolving their remaining experimental imports. It must not delete the default field implementation on the assumption that this candidate passed.

The benchmark runs the three correction paths sequentially against the same freshly decoded page and Paddle map, then repeats in reverse page order. Detector/decode time is recorded separately and charged to each route's reported file-to-lines total; it is not rerun three times within one page. Correction timing includes the full dependency chain. Repeat comparison covers polygon, baseline, score, score source and source IDs. The independent R6 comparison uses **full exported item dictionaries**, including geometry/provenance metadata. No assertion of repeat equality for every diagnostic evidence dictionary is made.

### Every curvature comment, judged on the image

Quotes below are verbatim from `review_r6/COMMENTS_CHECKED.md`; numbers retain the owner’s R6 reading order. Each linked image is raw ink / R6 / 2c, with lost R6 dark pixels in red. These are local judgments, not automatic labels.

#### s2-3229200bf47ca465a42d-p00004

> still a missed line between 10 and 11

- **10–11** — A crop now reaches the Γ. Μαυρομιχάλης row, but the column transaction fell back and adjacent found letters are clipped. This is not an accepted bend recovery; the field-free legacy route also changes these crops. PARTIAL locally, FAIL for acceptance. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00004.10-11.png).

#### s2-3229200bf47ca465a42d-p00005

> still some last missed chars for 13 14 18 on the curvature

- **13** — The curled νὰ remains outside the main crop. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00005.13-14.png).
- **14** — The curled τοῦ remains outside. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00005.13-14.png).
- **18** — The δι’/εἴτε curl remains separate or outside the row crop. Column fallback is a failure. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00005.18-18.png).

#### s2-3229200bf47ca465a42d-p00006

> still a line missed between 26 and 27
>
> words horizontally between 33 and 36
> and also between 35 and 38
> and also the line before 39 (vertically) is missed

- **26–27** — The straight box still holds two rows; the first has no independent crop. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00006.26-27.png).
- **33–36** — Tilted left pieces remain separate; the intervening νόμου is not joined to its row. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00006.33-38.png).
- **35–38** — The «ἀπὸ region is not correctly absorbed into its row. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00006.33-38.png).
- **before 39** — The two-row box persists. The scout nominates no bend on this page. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-3229200bf47ca465a42d-p00006.38-39.png).

#### s2-49598b2e848ab1f0ee1e-p00001

> missed line between 41 and 44
>
> missed lines between 67 and 75
>
> first word before 75 and 90 is still missed

- **41–44** — The δυνατόν… row still lacks its own band. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00001.41-44.png).
- **67–75** — Several intervening rows still have no crop. A partial lower recovery does not recover the missing block. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00001.67-75.png).
- **before 75** — Curled starts remain fragmented and native panels show additional loss of found prefixes. FAIL, regression. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00001.75-75.png).
- **before 90** — The μα before σμικρύνει stays outside the main row. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00001.90-90.png).

#### s2-49598b2e848ab1f0ee1e-p00004

> lines are missed still between:
>
> 50 and 52
> 108 and 112
> 112 and 116
>
> also some last word to the right of the right column where there is curvature are missed: 42 59 118 127

- **50–52** — The intervening required row remains unboxed. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.50-52.png).
- **108–112** — The required intervening rows remain without their own crops. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.108-112.png).
- **112–116** — The γωμεν τὸν κρίθινον ἄρτον… row remains unboxed. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.112-116.png).
- **42** — The right end rises outside the horizontal crop. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.42-42.png).
- **59** — The curl has a separate small crop instead of joining its row. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.59-59.png).
- **118** — The right-end word remains outside/separate from its row. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.118-118.png).
- **127** — The curled Ἐγώ remains outside the main crop. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00004.127-127.png).

#### s2-49598b2e848ab1f0ee1e-p00005

> some segments contain two lines eg 116 adn 117 which cause ocr confusion

- **116** — The lower right two-row box is not correctly split. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00005.116-117.png).
- **117** — The lower left two-row box persists. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-49598b2e848ab1f0ee1e-p00005.116-117.png).

#### s2-44b5cf9e0d680b361091-p00002

> line 123 does not target its line well
>
> and after these many segments contain two lines

- **123** — Removing the old half-row-offset field does not yield an accepted independently aligned row 123. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-44b5cf9e0d680b361091-p00002.122-128.png).
- **after 123** — Retained straight boxes still straddle rows in this bottom block; the required clean split is not achieved. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-44b5cf9e0d680b361091-p00002.122-128.png).

#### s2-86865c33eef5932c013b-p00005

Supplementary curl case explicitly required in the brief.

- **curled last words** — The right curl remains outside or separated. The final scout nominates the wrong (left) side. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-86865c33eef5932c013b-p00005.1-10.png).

#### s2-86865c33eef5932c013b-p00007

Supplementary curl case explicitly required in the brief.

- **curled last words** — The scout nominates no bend. Long-row curled words are still separate or clipped; native loss includes real letters. FAIL. [Native context](../../../.astra/fast_lines/out/round7/T2c_bend/final-v2/comment-crops/s2-86865c33eef5932c013b-p00007.6-13.png).

The coordinator’s supplementary observations, retained verbatim:

> - p00005: the bend was found (up to 1.7 letter heights at the right edge), but all 38 rebuilt segments were rejected:
>   21 "candidate contains another native row", 9 "separate horizontal sources retained", 4 "native ink would be
>   lost", 2 "independent small cells retained".
> - p00007: 13 of 79 were accepted, mostly headings and short lines. The long curled lines were rejected for losing
>   8–158 pixels of ink, or for touching the row above. The column guard also blocks single lines that Paddle broke at
>   the curl.
> - In both, the bend itself passes through the curled last words. The words are lost afterwards: the per-line rebuild
>   only uses letters within 0.75 letter heights of the fitted line, and then the vetoes reject the segment.

The final candidate still fails these two cases, now also through incorrect/missed scout nomination. Its four whole-column fallbacks (3229 p4, 032e p4, 3229 p5 and 3229 p8) count as failures. They restore the early adapter input, not the final R6 result.

All **97/97 owner “one” polygons remain exactly present**. Seventeen lie on changed pages. This geometric check does not certify every adjacent crop; the required “two” cases above still fail. All 256 owner-mark native contexts are provided, but they were not all individually adjudicated.

### Final acceptance: 0 of 5 groups pass

| Required group | Result | Evidence |
|---|---|---|
| 1. R6 equality on no-field, no-bend pages; all 40 agreement pages | **FAIL** | 158/164 eligible flat pages match the full R6 exported items; 36/40 agreement pages match. |
| 2. Every curvature comment; “two” split and “one” retained | **FAIL** | Individual dispositions above. All 97 “one” polygons remain, but required curls, missing rows and two-row splits fail. |
| 3. Spreads, tables and initials | **FAIL** | Incorrect explicit spread fields, changed 8686 p7 table, and lost large E on 466 p277. |
| 4. Exact exclusions, rules, faintness, zero native real-text loss | **FAIL** | Five R6 exclusion footprints missing; native review confirms 14 real-text loss clusters. Rule audit not certified. |
| 5. Two-pass timing | **FAIL** | Nominated curved pages add median 175.7/188.6ms; flat scout median 14.5/14.2ms. |

Full exported-item comparison finds **47 changed pages**, including all **38 historical field-band pages**. All 47 Paddle/R6/2c gallery overviews were opened. The comparison uses full item dictionaries (all geometry/provenance fields, sequence order retained), excluding timing metadata; it does not claim byte equality of the complete timed JSON files. Even this item-equality test fails the required unchanged set.

The inherited merged default differs from saved R6 on 7/208 pages (201 equal). Six account for all failed no-field/no-bend equality pages: 7792 p59/p104/p107/p138/p154 and 2922 p1; these already differ under the merged task-3 default. The seventh is 44b5 p5. This distinction explains provenance, but does not waive the requested R6 comparison. The four changed agreement pages are e259 p198, 3229 p2, 2922 p1 and c3cc p2.

R6 has 236 protected exclusion footprints; 231 remain exact. The merged default has 295; 290 remain exact, including all 59 additions. The five missing R6 footprints are on 3229 p4, d1ed p1, 8686 p26, 44b5 p1 and 8686 p29. There are 219 newly included dark pixels beneath R6 exclusions (195 on 3229 p4, 24 on 8686 p26). **Protected exclusions do not pass.**

The conservative finite-rule audit has 49 M13 certificates and 726 candidate crop/rule geometric intersections, versus 675 for R6. Its definition is positive intersection length between a verified finite rule and a polygon inset by 0.5px. These are geometric candidates, **not 726 certified text crossings**. Existing near-rule crops are included; no “zero crossings” result is claimed, and native adjudication of those intersections remains outstanding.

### Native loss and controls

The native check finds **623,747 raw lost dark pixels** and **567 clusters at least h²/40**, after h/2 spatial grouping, using gray <200 and only R6 exclusions. Raw loss includes nontext and does not mean that every cluster is real text. The audit’s h is the unchanged R6 acceptance tool’s detector height proxy, distinct from the per-column body height used by the new growth code; this is a limitation of threshold comparability.

All 567 cluster panels, 44 full native page contact sheets and 146 native viewport tiles are provided. **17 cluster panels were individually inspected: 14 contain real text, one is a table leader dot, and two remain unresolved rule/letter cases. The other 550 are not individually adjudicated.** No complete native-sheet pass is claimed. The inspected real-text failures already disprove the zero-loss gate: the large initial E, letters in πολλάκις and short πό- ending on 466 p277; clipped prefixes/upper letters/end words on 4959 p1; curl letters/descenders on 8686 p7; punctuation and descenders on c8 p68. Each decision and exact image is in `visual-review.json`.

| Control | Visual disposition |
|---|---|
| d83 p99 | Final crops unchanged, gutter visually clear; explicit inactive field still partitions the two leaves incorrectly. |
| 9ea1 p218/p202, c8 p68, e259 p198 | Changed overviews inspected. p218 partition is wrong; p202 is nominated. c8 has native punctuation/descender loss. No spread-preservation pass. |
| 8314 p20 | Table crops exactly unchanged; inactive fitted table field remains invalid. |
| 8686 p7 table | Most small cells stay, but the first label shortens and a leader dot is lost. Both native table blocks inspected; exact preservation fails. |
| fd4 p35; 1ba3 p15; e745 p633 | Outputs unchanged and the inspected large B, E/K and Psi initials remain intact. |
| 466 p277 | Large E and ordinary letters are lost. FAIL. |
| 00f1 p258 | Output unchanged. Pre-existing missing large O and multirow envelopes remain; unchanged is not a correctness claim. |
| ef481 p150 #3; p151 #9/#10/#29/#30 | Faint margin pieces remain unchanged: no worse, still unfixed. |
| 44b5 p5 #123 | Faint mirrored header removed, already in merged default. |
| 93f8 p1 #1/#89/#117/#126/#127; #5 | Indicated mirrored pieces removed; heading has less left faint spill. Nearby faint context is not completely eliminated. |
| 8686 p26 #9/#40 | Indicated faint side extensions trimmed; central dark text retained in these control views. |

All specified faintness control contexts were opened. These observations do not reinstate the withdrawn all-stage growth adapter or certify all faint front print.

### Two-pass performance on the frozen source

Milliseconds below are full correction time. Each route is charged the same freshly measured per-page decode and Paddle inference separately in the file-to-lines receipt. Pass 2 reverses page order. No background workload was launched.

| Route | Median, pass 1 / 2 | p95, pass 1 / 2 | Maximum, pass 1 / 2 | Pages >1s, pass 1 / 2 |
|---|---:|---:|---:|---:|
| Merged default | 198.7 / 205.2 | 1410.3 / 1429.0 | 2438.3 / 2401.1 | 24 / 24 |
| Same route without early/late M15–M18 | 142.6 / 140.6 | 701.7 / 691.6 | 1609.7 / 1581.1 | 5 / 5 |
| 2c opt-in | 160.2 / 159.7 | 802.4 / 807.4 | 1785.4 / 1806.5 | 8 / 7 |

The historical R6 comparison supplied in the brief is **21–23 correction pages >1s**; the fresh merged default here is 24/24. Fewer slow pages after deleting the expensive field route does not establish the new bend’s added-time requirement.

Paired against the field-free route, the 25 scout-nominated pages add median **175.7/188.6ms**, p95 **299.9/304.0ms**, maximum **381.4/416.7ms**. **19/25 and 20/25 exceed 100ms.** The 183 inactive pages add median **15.0/14.6ms**, p95 **75.6/70.0ms**. Inactive scout alone costs median **14.5/14.2ms**, p95 **72.5/73.5ms**; the inactive adapter is about 0.003ms. Active scout medians are 28.2/28.5ms and active adapter medians 121.9/124.9ms. The labels “active/inactive” describe scout output, not ground-truth curvature: known curls are missed.

File-to-lines medians are **305.6/305.7ms** for 2c (p95 1028.0/1019.1ms, 13/13 pages >1s), **347.5/345.5ms** for default (29/29 >1s), and **284.5/286.3ms** field-free (8/7 >1s). Full tails and per-page stage timings are retained.

All 25 nominated columns log measured gaps (407–2,226 positive samples per column). Twenty-four use the 2h ceiling; 466 p242 uses 1.99375h. Thus the present rule effectively chooses about 2h, following A4 to avoid blocking a word space before a short curl word. The observed percentile does not establish that this ceiling is optimal; a 1h alternative was not accepted by a comparative visual study. Logged operations before rollback are 17 row edits, 14 missed-run additions and 12 splits; 12 row edits and four missed runs lie in rolled-back columns and are discarded. These are proposal counts, not successful final recoveries.

### Replay, tests and handoff

The frozen runtime has **263 passing tests and one inherited expected failure out of 264**, including ten bend/growth tests. The expected failure concerns genuinely faint front text indistinguishable by the existing photometry. Unit tests do not pass the five failed acceptance groups.

The second timing pass’s raw Python comparison reports 188/208 matches for each route because some runtime polygon vertices are tuples while the saved JSON has lists. A separate **fresh full 208-page replay** matches Paddle inputs and **all full exported items on 208/208 pages for each of default, field-free and 2c**, after ordinary JSON serialization. Core fields also match 208/208 after JSON normalization. The original raw comparison flags remain untouched. This proves the independent replay against pass 1; it is not a retroactive claim that every diagnostic dictionary or every unrecorded pass-2 object was compared byte for byte.

`final-v2/source.json` and its source snapshot bind the benchmarked Python files. After the runs, the two extracted gap/rule helpers had only surplus blank EOF lines removed to satisfy patch whitespace checks; normalized bytes and Python ASTs are identical. The final test suite was rerun. `final-source.json` records those two cosmetic differences; input SHA-256 values are in `acceptance/protection.json`. `handoff.json` binds the model, environment, evidence files and source state. The independent acceptance helpers are copied into `final-v2/evidence-tools/`. The report, visual ledger, full loss records, replay, protection and timing receipts are linked from the gallery. Earlier `final-v1` and `rejected-channel-run` are explicitly not handoff timing evidence.

The Git worktree index is read-only in this session. `.astra/commit-FT2c-r7.sh` stages only the ten owned files after checking branch, base and file hashes, and commits with both required trailers. Its companion patch is checked by forward and reverse application against the base with byte/hash verification. The script has been prepared, not executed. It preserves an opt-in failed experiment; it does not promote 2c.

Required work before any future promotion remains concrete: correct leaf/column separation and map-only scout recall, preserve final R6 found text after both field removals and downstream stages, recover every listed curvature case, protect large initials and exact exclusions, resolve all rule/loss candidates, and meet the measured added-time limits. There is no permission to treat this handoff as an accepted replacement for task C.
