# Fast line finding: combined stack, round 7

**Partial: output is preserved, but the speed target is still missed.** Both fresh runs cover all 208 supplied pages and agree exactly. Every final item equals the current Task 3 default; no new missing native ink was found. Failed row-model routes and the named geometry/ink studies are removed, safe repeated work is consolidated, and `Stack(bend=True)` remains isolated from the default. Task C's field replacement and Task 3's 59 whole non-text removals remain.

Corrections exceed one second on **20 pages in each pass**, with maxima **2008.564 / 1998.657 ms**. Agreement overhead is **60.570 / 63.194 ms median**, **547.714 / 537.945 ms p95**, **642.485 / 647.715 ms maximum**. All-page correction medians are **187.222 / 193.793 ms**. The field still fires on 73 pages and finishes without bands on 35. A curved-column skip trial clipped a real rho descender on c8 p36 and was rejected. No visibly right fix was dropped to improve the timing table.

The complete report is [FAST_LINES_ROUND7_T4_SPEED.md](FAST_LINES_ROUND7_T4_SPEED.md), including all eight checklist dispositions, accepted optimizations, rejected experiments, raw timing comparisons and cleanup scope. Rust contracts and crate selection are **deferred by the owner**. Items 4-02 through 4-06 and 4-08 remain not closed; 4-01 and 4-07 close only the requested speed/cleanup scope.

Final detector JSON and two per-page receipts: **`.astra/fast_lines/out/stack/r7/`**. Review links: [gallery](../../../.astra/fast_lines/out/stack/r7/index.html), [zero changed pages against current default](../../../.astra/fast_lines/out/stack/r7/changed.html), [104 owner comments verbatim](../../../.astra/fast_lines/out/stack/r7/COMMENTS.md), [256 original owner marks](../../../.astra/fast_lines/out/stack/r7/ROWS.md), [timing tails and every slow page](../../../.astra/fast_lines/out/stack/r7/TIMING.md), [native retention ledger](../../../.astra/fast_lines/out/stack/r7/acceptance/pages.json), [validation](../../../.astra/fast_lines/out/stack/r7/validation.json).

Validation: **252 passed, one inherited strict expected failure; 51,122 artifact checks**. All 14 native loss sheets for the seven R6-to-Task3 non-text deletion pages were re-inspected; the three named approved recovery crops are preserved. The 256 unchanged row dispositions are explicitly inherited from prior native reviews, with refreshed context crops. Equality does not resolve the inherited R6 missed recoveries on 3229 p4/4959 p1, faint-front-print false removals, severe curled endpoints, multirow crops or finite-boundary failures. Those remain listed individually in the owner ledgers. The prototype is not ready for promotion. No held-out pages or production page code were touched.

Git staging was blocked by the sandbox at the worktree `index.lock`. The validated patch and guarded `.astra/commit-FT4-r7.sh` are the commit handoff; no commit or push was made in task 4.

The following sections are the **historical R6 report**, retained for traceability; their timings and commit history do not describe r7.

# Historical round 6

**Partial.** The three tracks run together through `Stack()('page.png')`, with imported shared code and no owned copies. Both fresh 208-page runs produce identical final items. The final native-ink duplicate audit goes from **61 pairs on 30 pages to zero**, including all 41 pairs named by the independent review. However, the owner's timing target is **not met**: maximum corrections are **2393.061 / 2379.603 ms**, with **21 / 22 pages over one second**. Agreement overhead is **62.336 / 61.808 ms median**, **564.354 / 561.108 ms p95**, **673.740 / 677.147 ms maximum**. Three previously recovered real text pieces regress on two pages. This version is not ready for promotion.

Final detector JSON and timing receipts are in **`.astra/fast_lines/out/stack/r6/`**. The [gallery](../../../.astra/fast_lines/out/stack/r6/index.html), [73 owner comments verbatim](../../../.astra/fast_lines/out/stack/r6/COMMENTS.md), [256 owner-marked segments](../../../.astra/fast_lines/out/stack/r6/ROWS.md), [208-page visual ledger](../../../.astra/fast_lines/out/stack/r6/review.json), [duplicate audit](../../../.astra/fast_lines/out/stack/r6/DUPLICATES.md), [recovery retention audit](../../../.astra/fast_lines/out/stack/r6/RECOVERY.md), and [raw timings with every slow page and stage](../../../.astra/fast_lines/out/stack/r6/TIMING.md) are the reviewable result. R5's successful timing result below is historical; it does not describe R6.

## Pipeline and interactions

Base is `ea25b8e`: merged task A `1625031`, task B `3a7902d`, task C `5522053`. The ordering is Paddle v6 small → Q8 once → existing back-print/ornament/seal removals → edge-map scout → cheap printed-rule/column boundaries → shared page field → remaining per-line geometry and joins → type recovery and initial completion → guarded envelopes → page-relative faintness → conditional field reconciliation → native row splitting → all-segment duplicate reconciliation → faintness on changed final footprints.

The field now takes ownership before expensive per-line paths on **all 38 pages where it applies**, versus 9 previously. Cheap printed boundaries must precede it: a raw-field-first probe reduced accepted bands and disturbed recovery on 4959. Field-owned rows bypass the old curl/join/row paths. The field still leaves uncertain regions to those paths; this is not whole-page geometric ownership. On eight pages a later selection reconciles changed sources using the same proposal, mesh and detector result. It does not rerun field inference. Exact rejected polygons are permanent exclusions; neither unknown ownership nor a broad stamp disk certifies front text. The completed initial remains protected.

Stable `source_ids` refer to original Paddle indices, including after splitting and duplicate retirement. Recovered lines retain their type witnesses. All exported baselines are null; the current stack renderer, row review and validation use polygons and accept null. This is not a claim about every external downstream consumer. All outputs are detector-format `unit: line` exports. Discounted segments are absent from final OCR items; red review outlines indicate removals rather than retained text.

The obsolete, unconsumed `geometry_field_replace.py`, `geometry_edge_scout.py` and `geometry_edge_walk.py` are deleted. `reuse.json` records live imports and hashes. Production `greekocr/pages/` and its tests are untouched. No PDF text layer, held-out page, page-name gate, or orientation correction is used.

## Relative faintness

The previous single-component/two-piece witness is replaced with a run of **three whole normal-print body components on the segment's own row**. One body gives no adjacency evidence; two give one link that could be a broken glyph; three provide two repeated links. Their shared row and spacing are checked in body-height units. Clipped neighbour fragments do not establish a run. Three is this minimal repeated-adjacency construction, not a fitted page constant or a proof of lexical word identity.

A connected normal word can otherwise appear as one component, so the rule also abstains when normal ink exceeds one median faint-body area, or a short ambiguous row has normal bodies. The discarded alternative using the maximum faint-body area erased real handwriting on `an-778126cc8c2b-p000017`; it is not shipped. The conservative guard keeps the real short word “οἱ” on `an-466cffad2cba-p000242`, but also leaves some ghost rows. The ghost “Ἀριθ. 300” on `s2-0ce9d1025b3f23c7119e-p00001` has no normal run yet survives because its connected dark mass exceeds the allowance. That remains unresolved.

The old whole-page skip based on R5 box cores is removed. The scout evaluates the actual current polygons, including additions; changed field/split/clipped footprints are checked again after final ownership. Calibration still sees the page's final segments. Gaussian sigma is `h/40` with a quarter-pixel numerical minimum; its radius is `ceil(2*sigma)`. The old sigma 0.6 is recovered at body height 24. Fixed one-pixel component-border operations are raster conventions, not physical letter lengths.

The final stack removes **137 faint segments on 34 pages**, versus task C's 140. There are ten newly shaped/new removal records and thirteen old polygon identities absent from the new removal ledger. Two are the same ghosts reshaped and removed again; **eleven are actual returned ghosts on `s2-93f8070059f938bda524-p00001`**, a regression caused by the conservative ambiguity guard. Every changed removal crop was inspected. Existing 61 back-print, 16 ornament and 22 seal removals retain their separate reasons; relative faintness does not replace their independent evidence.

The [known-front controls](../../../.astra/fast_lines/out/stack/r6/faint-front-controls.jpg) explicitly expose the unresolved ambiguity: grey rubric, lighter grey text, light italic and a blurred small footnote among black rows are falsely removed (**four failures**); the red-rubric luminance control is kept. These are synthetic known-front renderings, not claimed examples from captured colour pages. Photometry alone cannot establish print ownership. The strict expected-failure test retains this limitation rather than asserting success. The task-A report now acknowledges its actual commit `1625031`; the older no-commit statement was stale.

## Duplicate retirement and row quality

Every final segment is compared with spatial neighbours using inclusive paper-relative native ink and its observed darker mode. A share of at least 80% nominates reconciliation. The smaller/older owner is clipped by the existing owned polygon; remaining connected pieces with unique ink survive. Field ownership and completed initials are preferred. An independent rerun on all 208 saved final lists finds **zero remaining nominated duplicate pairs**.

The 61 initial pairs require **68 operations: 29 complete retirements and 39 clips**, producing 52 pieces before subsequent reconciliation. All 41 coordinator-listed pairs on 25 pages are retired or changed. [DUPLICATES.md](../../../.astra/fast_lines/out/stack/r6/DUPLICATES.md) lists each page and the mapping to the review. This is broader than retiring B children: older boxes and field bands are audited too.

This is not exact raster conservation. The subtraction audit finds **27 uncovered inclusive-ink boundary pixels**: five on `an-9ea1564fcf4f-p000218`, one on `s2-49598b2e848ab1f0ee1e-p00004`, and 21 on `s2-44b5cf9e0d680b361091-p00001`. Uncovered vector area is 25128.368276 square pixels, mainly discarded background; it is not a text-loss measure. Full duplicate crops did not show a whole lost word from this operator, but small boundary losses remain. Unique slivers and isolated word fragments are intentionally not erased merely to achieve a pleasing row count. Some surviving owners still contain multiple rows.

All 256 owner marks were reviewed, including full before/final OCR crops for the 75 changed marks: **97 one-row marks retained**, **25 two-row marks fixed**, **45 partly fixed**, **88 not fixed**, **one outside this round** (parked orientation). Three of the retained one-row polygons are tighter; 94 are exact. This is development evidence, not independent held-out accuracy. Several split crops remain two-plus-two or three-plus-one rows, notably `an-a73d22211479-p000301`. Smooth bands improve many rows on 3229 and 4959, but lower straight boxes, detached starts and extreme ends remain.

## Recovery regressions and visual review

**55 pages change against task C; 153 remain exact.** Every page overview, every owner-marked region, all changed full OCR crops, all 68 duplicate-operation panels, and all changed removal crops were viewed. Page overviews alone missed three substantial recovered-text losses. A subsequent native audit of all **76 task-C additions** found 51 with exact ink coverage and 25 with some uncovered pixels. Eighteen cases over ten pixels were enlarged and inspected; seven smaller differences remain numerical observations.

Three losses are substantial and visibly real:

- `s2-3229200bf47ca465a42d-p00004`, old addition 0, y=712–801: **12558 / 13696** formerly covered ink pixels are uncovered. The changed regional crop is rejected by type's existing multirow-height veto.
- `s2-49598b2e848ab1f0ee1e-p00001`, old addition 0, y=2911–2974: **7612 / 8231** pixels uncovered, in a real central sentence. Field-first geometry changes lattice/table context and the slot is protected as a table.
- The same page, old addition 11, y=2866–2973: **3678 / 4145** pixels uncovered in the left continuation. Residual localization spans a larger vertical range and hits the multirow veto.

These are **not faintness removals**, and five fewer additions on 4959 p1 cannot be described as harmless replacement by field bands. An offline one-to-one parent-grid nomination probe did not restore them; a many-to-one variant was rejected by the API's correspondence guard. Neither is promoted. Correcting curved-region recovery ownership and table evidence remains necessary. The other 15 enlarged recovery differences are small edge/accent losses rather than whole missing rows, documented individually in [RECOVERY.md](../../../.astra/fast_lines/out/stack/r6/RECOVERY.md). There is no claim that every visibly right prior fix was preserved.

The 73 owner comment dispositions are **47 fixed, 18 partly, seven not fixed, one outside this round**; they concern the specific comment, not overall page correctness. The ledgers preserve every owner's comment verbatim, including the smooth-shape goal. The eight previously unavailable originals are now included. Known field gaps remain on 86865 p5 (all proposals vetoed), p26 (mostly heading bands), lower 3229 p4/p5/p6, and the extreme right ends of 3229 p5 and 86865 p7. The scout still misses e46611 p41, 3229 p9, 86865 p23 and p25. There are **83 unowned candidates in the final selection ledgers**, none promoted as missed text. Physical-leaf boundaries, universal smooth envelopes, general large initials, black border decoration and dark stains remain open. Orientation remains parked.

## Repeated timings and attempted cost reductions

Each cell is **median / p95 / maximum in milliseconds**. Two fresh executions cover all 208 allowed pages; repeat 2 reverses order and asserts exact final items. Decode, Paddle preprocessing/inference/postprocessing, scouts, proposals, reconciliation and every correction are charged. Warm model startup is separate; JSON writing and review rendering are outside the timer. ONNX is single-threaded. This Mac's OpenCV GCD reports ten threads despite the requested positive cap, so these are not bounded-two-worker results.

| Cohort | n | Repeat | Paddle from file | Added corrections | Final from file |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 | 1 | 149.841 / 171.348 / 205.099 | 62.336 / 564.354 / 673.740 | 214.034 / 695.938 / 824.255 |
| Agreement | 40 | 2 | 146.259 / 169.984 / 195.909 | 61.808 / 561.108 / 677.147 | 210.471 / 692.230 / 836.217 |
| Discrepancy | 101 | 1 | 146.752 / 232.541 / 282.710 | 209.185 / 1380.784 / 2226.745 | 351.747 / 1548.463 / 2423.398 |
| Discrepancy | 101 | 2 | 144.155 / 226.953 / 279.804 | 210.404 / 1387.362 / 2192.943 | 356.624 / 1569.360 / 2389.713 |
| All original non-agreement | 155 | 1 | 147.311 / 231.650 / 282.710 | 212.084 / 1441.492 / 2393.061 | 365.851 / 1701.954 / 2586.505 |
| All original non-agreement | 155 | 2 | 146.180 / 227.435 / 279.804 | 216.055 / 1438.504 / 2379.603 | 371.736 / 1701.149 / 2573.394 |
| Supplied review pages | 13 | 1 | 151.353 / 215.325 / 218.397 | 580.653 / 1426.747 / 1805.346 | 729.080 / 1635.505 / 2018.624 |
| Supplied review pages | 13 | 2 | 149.794 / 211.265 / 213.009 | 573.653 / 1439.002 / 1834.807 | 723.449 / 1644.090 / 2044.910 |
| All supplied | 208 | 1 | 148.364 / 230.040 / 282.710 | 189.438 / 1372.439 / 2393.061 | 330.361 / 1543.114 / 2586.505 |
| All supplied | 208 | 2 | 146.224 / 224.829 / 279.804 | 187.094 / 1386.783 / 2379.603 | 332.065 / 1564.698 / 2573.394 |

The 155 includes 54 development/challenge pages in addition to the 101 discrepancies. The worst page, **4959 p1**, is a development page. Its field proposal costs **857.365 / 848.355 ms**, early selection **148.327 / 141.317**, remaining geometry **105.647 / 100.578**, type **768.098 / 757.226**, shaping **72.758 / 94.031**, faintness **54.051 / 53.434**, late selection **138.209 / 140.726**, rows **53.059 / 51.563**, final duplicate ownership **123.012 / 120.040**, final faintness **5.852 / 6.211**. Other scouts and cuts make up the remainder. These are non-overlapping stage timers; nested substage costs are not added twice.

On **4959 p4**, total corrections are **1913.034 / 1931.118 ms**; fragment verification is now **54.482 / 54.925 ms**. On **p5**, corrections are **2226.745 / 2192.943 ms**; rows cost **379.999 / 397.220 ms**, down from the reported approximately 600 ms but still too expensive. The current worst total exceeds task C's **2191.694 / 2170.486 ms**: stronger final auditing adds work. All 22 pages failing either repeat are listed by name with stages in TIMING.md. One, `an-7a2b17a3fb0f-p000200`, now fails without firing the field scout; it costs 963.326 / 1016.181 ms.

Implemented savings preserve their audited operation rather than weaken a score: the shared mesh batches identical knot-window correlations (124 fields checked, maximum displacement difference **3.839595308363641e-12 pixels**, dispatch unchanged); exact native prepared context is reused when image/height/masking identity permits; field proposals are built once; already field-owned groups skip later replacement; remaining expensive per-line paths abstain on those owners. The mesh equality log is `.astra/r6-mesh-equality.log`. These savings are insufficient to meet the target. No successful sub-second result is inferred from them.

A cheaper centroid scout was rejected: it reduced nominations from 73 to 49 and saved seven empty attempts, but lost eight accepted field pages including 3229 p2/p6. A sequential OpenCV probe was slower (exploratory roughly 2.8 vs 2.2 s), not promoted. The final scout fires on **73 pages, including seven agreement pages**. **35 pages pay for a field with no applied bands**: proposal median **160.719 / 161.578 ms**, p95 **303.936 / 310.719**, max **348.543 / 360.205**. Flat/near-no-op field nomination remains an unresolved cost source; dropping these solely from observed page identities would violate the generality requirement.

Agreement median duplicate auditing alone costs **27.787 / 28.442 ms**, rows **3.165 / 3.101**, faintness **1.039 / 1.023**, ink **4.896 / 4.802**, edge scout **4.188 / 4.091**, Q8 scout **5.680 / 5.695**. Stage medians do not sum to the page median. The agreement maximum is `an-e259bbf5081c-p000198`: field proposal **488.294 / 485.074 ms**, early selection **64.742 / 70.715**. Clean-page overhead is plainly not negligible. The original 305 ms ink tail on `an-778126cc8c2b-p000011` remains resolved: B costs **16.692 / 16.797 ms**, complete corrections **56.785 / 54.973 ms**. Its old 1,802 negative ornament-template calls are not the present bottleneck.

## Contributions, validation and readiness

Across 208 pages: **308 Q8 cuts; 61 back-print, 16 ornament, 22 seal and 137 relative-faintness removals; 10 map reshapes; 92 curved-rule cuts; 279 column cuts; 18 fragment-join groups reducing 19 pieces; 71 type additions; 14 final envelopes; 42 row partitions; 1060 final field bands on 38 pages; 68 duplicate operations**. These overlap in source ownership and are not independent fixes or 1060 proven correct rows. Full per-page contributions are in `contributions.json` and each evidence receipt.

The scout's map 0.3 is the existing Paddle binary-map threshold, not calibrated confidence. Densities .035/.05 are binary body-occupancy fractions after letter-scaled smoothing. The inherited .08×255 contrast floor in field native contacts is an eight-bit texture floor, **not illumination invariant**; the source now says so. It has not been given an invented derivation or silently changed during integration. Calibration remains open. The row run uses native body heights; the fixed pixel operations that remain are raster boundaries or numerical sampling floors.

**224 tests pass; one strict expected failure remains (225 total)** for genuine faint-front controls. The two final runs pass **65,454 artifact checks**, including all source hashes, fresh Paddle identity, exact repeated items, source genealogy, count ledgers, valid polygons, null baselines, bounds, numbering, all owner comments and links, all owner-mark reviews and changed-removal reviews. A separate saved-output native audit finds zero final duplicate nominations. The runtime's 215 Python-file hashes match both repeated snapshots; source key `071d0d2dcfe24e68e848a3f0c4eb771452871016742b45af840f9a002e37432f`. These checks establish reproducibility and export integrity, not OCR accuracy or completion of the owner's three issues.

Ready for further prototype work: the common entry point, imported dependency composition, permanent exclusion/source ledgers, field-first ownership, final duplicate audit, and reproducible review/benchmark harness. **Not ready as a production correction module:** timing, the three recovered-text regressions, faint-front ambiguity, returned ghosts, raster boundary losses, multirow/sliver output and severe curvature coverage must be resolved first. No production integration or push was performed.

## Historical round 5b result

The following section describes the earlier 200-page R5 version only.


The combined stack now keeps **all 200 supplied pages below one second of corrections in both fresh runs**, without changing any final item from the unoptimized merged R5 pipeline. The maxima are **964.147 / 965.406 ms**. This is a measured result on this Mac, with only 35 ms of margin, not a bound for the 44 unseen pages. Agreement-page overhead is **18.449 / 18.019 ms median**, **51.414 / 51.674 ms p95**, **82.879 / 77.691 ms maximum**. The owner's overall goal remains **partial**: clean-page overhead is not negligible everywhere, smooth shapes are not universal, and many owner-marked defects remain.

Final detector JSON and per-page timing receipts: **`.astra/fast_lines/out/stack/r5/`**. Open the [200-page gallery](../../../.astra/fast_lines/out/stack/r5/index.html), [every owner comment verbatim and its final status](../../../.astra/fast_lines/out/stack/r5/COMMENTS.md), [73 changed common pages with raw / R4b / R5 crops](../../../.astra/fast_lines/out/stack/r5/changes.html), [200-page visual ledger](../../../.astra/fast_lines/out/stack/r5/review.json), [timing summary](../../../.astra/fast_lines/out/stack/r5/summary.json), and [export validation](../../../.astra/fast_lines/out/stack/r5/validation.json). Earlier versions remain intact.

## Composition and ownership

`Stack()('page.png')` imports the final merged geometry, ink and type modules from base `6e0e1b4` (geometry `d49667a`, ink `4887211`, type `07efa3f`). No owned copy is reintroduced. R5b's requested fixes and cost reductions live in the original shared modules, with hashes in [reuse.json](../../../prototypes/fast_lines/stack/reuse.json).

Order: Paddle v6 small → one Q8 scout and printed-rule split → back-print, ornament and seal-rim removals → geometry on surviving original sources → curved-rule cuts → verified column cuts → native fragment joins → grid and native residual recovery → large-initial completion → guarded smooth envelopes.

Removal comes before any operation that could reconnect or recover removed ink. Its exact original polygons remain permanent exclusions for fragment joins and recovery, not evidence that nearby text is front print. Geometry retains original source IDs; split pieces cannot impersonate their unsplit detector contour. Column evidence is shared with C, which validates native support separately for each resulting text piece. Final shaping sees recovered neighbors and preserves `initial_completed`, so it cannot flatten the recovered large E. Q8 and the geometry scout run once; native component labels are shared between fragment verification and final shaping only within that page. Orientation remains parked. No production page code, PDF text layer, held-out pages or page-specific runtime constants were used.

## Timings

Each cell is **median / p95 / maximum, milliseconds**. These are two complete fresh file-to-lines runs; repeat 2 reverses page order. Decode, Paddle preprocessing/inference/postprocessing and every correction are charged. Warm model startup is recorded separately; artifact rendering and serialization are outside the per-page timer. All 400 receipts retain raw seconds, stage costs, input and source hashes.

**Threading correction:** the default requests `image_threads=2`, but this Mac's OpenCV build uses **GCD**, which does not honor a positive worker cap. Every final receipt reports `getNumThreads() == 10`. ONNX explicitly uses one intra/inter-op thread. These are GCD timings, not a bounded-two-worker result. The earlier interpretation of the one-versus-two-request probe as two bounded workers was incorrect; the local documentation and probe are saved in [threading.json](../../../.astra/fast_lines/out/stack/r5/threading.json). A post-timing code-comment correction is AST-identical to the timed source, recorded separately. No measured runtime expression changed.

| Cohort | n | Repeat | Paddle file-to-lines | Added corrections | Final file-to-lines |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 | 1 | 149.257 / 174.067 / 202.467 | 18.449 / 51.414 / 82.879 | 168.726 / 220.324 / 225.736 |
| Agreement | 40 | 2 | 145.602 / 170.836 / 196.784 | 18.019 / 51.674 / 77.691 | 162.639 / 219.252 / 223.900 |
| Discrepancy | 101 | 1 | 146.578 / 231.803 / 283.436 | 98.412 / 519.961 / 880.235 | 251.360 / 746.725 / 1083.848 |
| Discrepancy | 101 | 2 | 144.905 / 228.731 / 293.346 | 101.415 / 511.877 / 863.219 | 256.199 / 736.080 / 1073.709 |
| New curved | 5 | 1 | 147.986 / 158.787 / 159.396 | 72.716 / 247.729 / 253.139 | 218.709 / 401.898 / 412.536 |
| New curved | 5 | 2 | 152.055 / 156.554 / 156.706 | 77.225 / 239.847 / 244.116 | 229.281 / 390.885 / 400.822 |
| All supplied | 200 | 1 | 147.338 / 229.353 / 283.436 | 64.802 / 476.537 / 964.147 | 212.739 / 712.079 / 1158.308 |
| All supplied | 200 | 2 | 145.592 / 224.828 / 293.346 | 66.856 / 482.433 / 965.406 | 207.477 / 699.650 / 1158.220 |

The all-page maximum is `s2-49598b2e848ab1f0ee1e-p00001`, a development page, so it is not included in the 101-page discrepancy maximum. The originally requested problem pages now take **859.196 / 857.801 ms** (p4) and **880.235 / 863.219 ms** (p5). Full file-to-lines time still exceeds one second: all-page maxima are **1158.308 / 1158.220 ms**. No hard worst-case or unseen-page guarantee is claimed.

The present agreement tail is `s2-3229200bf47ca465a42d-p00002`: final shaping costs 48.514 / 35.697 ms while geometry costs 19.955 / 28.018 ms. The earlier R4b stamp/fragment tail on `an-dbd045ccd84c-p000249` is now **43.397 / 43.790 ms total corrections**; B removes its seal-rim candidate before fragment verification, whose cost is only 0.531 / 0.684 ms. The original 305 ms ink tail on `an-778126cc8c2b-p000011` stays resolved: **27.184 / 24.949 ms total corrections**, **18.222 / 16.421 ms in B**. That old tail was negative ornament-template enumeration (1,802 matchTemplate calls); B's retained recurrence nomination avoids it. It is not the cause of the current tail.

## Bringing the merged pipeline under one second

The first unoptimized merged pass cost 1476.114 ms on 4959 p4, 1474.112 ms on p1, 1214.076 ms on p5, 1145.481 ms on 9ea156 p202 and 1055.721 ms on 7a2b p200. Those are exploratory one-pass observations in `r5-merged/`, not repeat-qualified final numbers.

- Native fragment filtering now computes the same separable Gaussian only on the exact trace-remap domains plus its complete finite halo. Connected components remain global. The audit covers all 27 nominated pages and 71 traces: paths, alternatives, contacts and decisions match, with maximum sampled support error **0**. No trace or right fix is skipped.
- Final shaping reuses the same native connected-component field when its image shape and height match. After ownership and extension checks establish that a row is ambiguous and cannot be accepted, the runtime skips unused extrema-envelope construction. Diagnostic rendering retains the full route. No accepted envelope changes.
- Type's localized leader check caches immutable row medians; the v5 path avoids a flood-fill census that was immediately overwritten. Polygon ownership batches only the bbox-negative checks and still runs the identical OpenCV polygon predicate for every possible hit. Residual neighborhoods are queried in a batch with original neighbor order; groups too short to be used do not compute unused medians.

An initial per-point bbox optimization was **rejected**: it increased dictionary page `an-9ea1564fcf4f-p000202` to 1923.351 ms in `r5-candidate/`. Batched negative filtering replaced it. A focused earlier probe with `image_threads=1` still exceeded one second; it is not offered as meeting the target. These failures remain in the receipts and logs rather than being omitted from the account.

The final expensive stages on 4959 p1 are C **644.776 / 648.135 ms**, total geometry **210.805 / 206.410 ms**, and shaping **78.703 / 80.656 ms**. On p4 the formerly ~500 ms fragment stage is **194.056 / 205.754 ms**. All **200 final item lists equal the unoptimized merged results exactly**, and repeat 2 asserted exact final items for every page. The optimization therefore does not trade a visible fix for speed on the supplied cohort.

## Contributions and interactions

Across 200 pages: **308 Q8 cuts, 61 back-print removals, 16 ornament removals, 21 seal-rim removals, 32 map reshapes, 92 curved-rule cuts, 270 additional column cuts, 18 fragment-join groups (19 fewer pieces), 76 recovered segments and 14 final smooth-envelope changes**. These are operator counts, not independent corrected-page counts or an accuracy score. Recovery includes 56 native residual additions and 20 grid additions; one large E is completed within an existing recovered line.

Compared with R4b, **73 of the 195 common pages change and 122 stay item-for-item identical**. All 200 final overviews were inspected, with detailed owner-marked and changed regions checked against the raw/before/after images. No new visual regression was identified in this review scope; this does not prove glyph-level accuracy.

The combination is not the sum of the isolated track numbers. Type's independent R5 study had 69 additions against old A/B. The new column geometry gives **seven further real pieces** on 4959: p1 9→12, p4 5→7, p5 14→16. The full final pages show these on visible text, although detached starts and severe curls remain. Geometry's independent 16 final bands become **14**: `an-466cffad2cba-p000277` preserves the completed large E instead of reshaping it, and `s2-86865c33eef5932c013b-p00007` rejects one competing band after C adds a neighboring row. These are intended ownership interactions, not missing independent-track calls.

The five extra curved pages receive no new C recovery. 3229 p5 gains three joins and one map reshape; p8 gains one map reshape. The other three retain Paddle output. Visual improvement on a few rows does not solve those pages' curved ends.

Relay files `000800-from-stack.md` to geometry/ink/type described the proposed shared-field, shape and Hough work; `001900-from-stack.md` to type described the exact-cost changes. The final combined measurements and remaining limitations are recorded on the shared board and sent to the tracks. No unpublished alternative track runtime was copied.

## Independent-review points

**Curve divisor:** the original 8→32 change had no historical derivation in the record. The misleading “two-height radius” comment is corrected. For the quadratic term `y = d²/(32h)`, the vertex radius is `16h`; over `d=4h`, rise is `h/2` and slope is `1/4`. The former divisor `8h` gives radius `4h` and slope 1 there. This explains the geometric meaning of the gentler prior; it does **not** retroactively establish why 32 was selected or prove optimality. The body/neighbor retention guards remain decisive, and calibration remains open.

**Paper-relative ink:** the envelope's absolute `255*.06` neighbor-ink cutoff is replaced by six percent of local paper level. This matches the intended contrast-relative notion and changes no final supplied-page item.

**Every segment:** the existing smoother was evaluated beyond its bent/extended-page and line gates. The exploratory broad long-row pass on 40 agreement pages cost **185.190 / 287.746 / 341.070 ms** median / p95 / max in shaping alone. Across 199 non-parked pages it cost **169.934 / 305.608 / 460.995 ms** and proposed 893 accepted changes. Those proposals are not all visually validated and are not promoted. This study used the `image_threads=1` request and predates the final ambiguous-row construction shortcut; it is a measured cost of that implementation, not a two-repeat final-runtime forecast. Even this broad route still guards short, split, initial and ambiguous ownership cases; it is not literal every-segment smoothing. Universal smooth bands remain unfinished.

**Hough 40/28:** the source now explains their roles at the normalized eight-pixels-per-body scale: 40 is the high gradient/Canny threshold (the low threshold is 20), 28 the circle-center accumulator threshold. They only nominate circles; native rim evidence makes removal decisions. Their original numeric calibration is not documented, so no invented derivation is claimed. They remain unchanged and require future sensitivity testing.

**Large initials:** the rule in `type_extended.py` was not widened. The specifically supported E completion is preserved through the combined output. General large initials remain open.

## Owner review and remaining failures

[COMMENTS.md](../../../.astra/fast_lines/out/stack/r5/COMMENTS.md) contains **all 73 owner comment blocks verbatim**, plus the new shape goal and the curved-page statement. It records **36 fixed, 12 partly, 16 not fixed, 9 outside this round**. Eight of the last group have only numbered review images, with no original in the authorized 195+5 inputs; one is the parked sideways page. These are comment dispositions, not whole-page accuracy judgments. The unchanged 122 pages retain their earlier named observations in the newly inspected 200-page ledger.

Every unresolved owner-comment page is listed below. Additional inherited weaknesses on non-comment pages are preserved in the full ledger.

| Page | Status | Remaining limitation |
|---|---|---|
| `an-3352d912f2e9-p000160` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `s2-86865c33eef5932c013b-p00026` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `an-ef481610a820-p000150` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `s2-831443dc5e6f1ccfbaf5-p00042` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `s2-831443dc5e6f1ccfbaf5-p00039` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `s2-0ce9d1025b3f23c7119e-p00001` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `s2-93f8070059f938bda524-p00001` | not fixed | The marked faint/second-layer boxes remain. Their appearance does not meet the current independent back-print witness; no new suppression was promoted. |
| `an-d6fd2cf2f618-p000047` | not fixed | The marked watermark box remains; the seal scout/native rim witness does not safely establish ownership here. |
| `an-c153f2c605b3-p000040` | not fixed | The marked watermark box remains; the seal scout/native rim witness does not safely establish ownership here. |
| `s2-6419488b7f8e69fd20da-p00001` | outside this round | The sideways page is passed through unchanged because orientation is parked. The faint boxes remain. |
| `an-7792a3301892-p000107` | partly | The lower seal-rim lettering is removed; the damaged top and vertical flower-frame fragments remain boxed. |
| `an-7792a3301892-p000104` | not fixed | The frame fragments remain. Vertical repeated shapes also match genuine quotation marks on a control page; repetition alone is insufficient for deletion. |
| `an-7792a3301892-p000059` | partly | The bottom flower row and seal-rim lettering are removed. The top and side decoration fragments remain. |
| `an-1be60011c435-p000215` | partly | Two seal-rim boxes are removed. The uncertain inner seal text remains boxed; pale front text is retained. |
| `s2-7534648e60694be1d180-p00018` | not fixed | The comment does not specify what to change. The two indicated rows look like front text and remain. No intent was invented from the numbers. |
| `s2-922e617957fca8dfafd0-p00001` | not fixed | The dark blob at the right remains boxed. Neither darkness nor stroke width supplies a safe generic non-text decision. |
| `an-ffccc97c07de-p000152` | not fixed | The small stain near the bottom remains boxed. No validated generic stain eraser is present. |
| `an-00f143ecce59-p000258` | partly | The second row beside the large I is recovered. Another missing row remains; the I belongs to the preceding row and is not moved. |
| `an-00f143ecce59-p000192` | not fixed | The bottom row still lacks safe ownership against the stamp, and the marked watermark boxes remain. The exclusion policy is not relaxed to recover stamp ink. |
| `an-e74539ae215c-p000338` | partly | The right-rim seal box is removed. Overlapping/interior watermark material is not established as removable. |
| `an-ef481610a820-p000181` | partly | The longer missing list entry is recovered and the seal-rim box is removed. The short preceding fragment remains unsupported. |
| `an-c99f1c450f55-p000025` | not fixed | The previously correct lower-strip removal is retained; the upper ivy strip still remains boxed because the full spatial verifier rejects its tall arches. |
| `an-1ba3fdb1436b-p000035` | not fixed | The real last row remains missed. Its proposal intersects the already removed frame footprint; preserving that veto costs recall here. |
| `s2-3229200bf47ca465a42d-p00006` | partly | Ten real missing rows are recovered. Severe curled ends, detached pieces and some short fragments remain unresolved. |
| `s2-49598b2e848ab1f0ee1e-p00001` | partly | The combined column geometry permits additional real starts/rows. Detached starts remain separate from neighboring right-hand pieces; some marked gaps and curled starts remain unresolved. |
| `s2-49598b2e848ab1f0ee1e-p00004` | partly | The central column crossings are split and real missing right-column text is added. The severe right curl still leaves characters outside several envelopes. |
| `s2-86865c33eef5932c013b-p00005` | partly | The two bottom rows are recovered. The internal omissions, the gap near reviewed 15/16 and many curled right-end words remain unresolved. |
| `s2-49598b2e848ab1f0ee1e-p00005` | partly | The column crossings are split and additional independently supported text pieces are recovered on both sides. The left curl and tight/jagged recovered envelopes remain; the final smoother abstains on competing ownership. |
| `s2-86865c33eef5932c013b-p00007` | partly | One further real row and guarded smooth body envelopes improve the page. Many rightmost characters still lie beyond the accepted segments. |
| `an-466cffad2cba-p000267` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `s2-032eaf8e6b3b83918feb-p00004` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `an-7792a3301892-p000154` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `s2-44b5cf9e0d680b361091-p00001` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `s2-44b5cf9e0d680b361091-p00002` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `s2-44b5cf9e0d680b361091-p00003` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `s2-44b5cf9e0d680b361091-p00005` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |
| `an-466cffad2cba-p000242` | outside this round | Only the numbered owner image is supplied; the original is absent from the authorized 195+5 inputs. The visible defect remains and no fresh correction is claimed. |

No discounted candidates are drawn on the final/Paddle review images. Red boxes are accepted Paddle detections explicitly removed, not detector-discounted proposals. New lines are green; reshapes and cuts are purple over the old grey polygon. Display numbers map back to exported item indices in each `.order.json`.

## Validation and readiness

**179/179 prototype tests pass**. The three new contract tests cover the exact local-filter halo at image borders, wrong-height cache rejection, and batched polygon ownership including concavities and edges. Export validation passes **17,919 checks on 200 pages**, including source accounting, all input hashes, finite bounded polygons, excluded-region rejection, accepted-shape ink retention, fragment source-pixel retention, exact column vector-area conservation and display-number mapping. Two full fresh runs produce exact final items; all 200 also match the unoptimized merged result. Both timed source keys are identical. A separate post-timing receipt verifies the only subsequent Python edit is a comment with identical AST. Integer raster edges of exact vector column clips remain subject to the track's stated rounding limitation.

The import-only composition, stable source accounting, permanent exclusions, shared evidence/cache and exact cost reductions are ready as a **prototype module**. Readiness for production remains partial: universal smooth shapes, severe curls, faint-layer ownership, generic stains/images/frames, robust large-initial recovery and calibrated Hough/shape priors remain open. No production API was changed.

The two review galleries pass **2,444 local-link checks**. Git staging was attempted on `astra/ff-merged` but the sandbox denied the worktree `index.lock`. The requested fallback is [commit-Fstack-r5.sh](../../../.astra/commit-Fstack-r5.sh), with a 17-file patch, exact per-file hashes and both isolated-base forward-apply and current-tree reverse-apply validation. No commit or push was performed. The script verifies branch, base, hashes and staged scope before committing with the requested trailers.

The original R4b report follows as historical evidence; its “no track modules edited” statement applies to R4b only.

---

# Fast line finding: combined stack, round 4b

R4b removes all eight owned track snapshots and imports the final merged modules
from `69db79f`. It adds **15 fragment joins and three real recovered rows** to the
previous stack. All 195 pages were run twice, with exact output agreement between
repeats. The measured correction maximum is **978.564 / 976.601 ms**: below one
second, but with little margin. Clean-page overhead is still not negligible, and
its maximum worsens to **107.472 / 99.312 ms**. The owner's target remains partial.

Final detector JSON: **`.astra/fast_lines/out/stack/r4b/<page>.json`**.
Open the [195-page gallery](../../../.astra/fast_lines/out/stack/r4b/index.html),
[all nine changed pages with raw/before/after crops](../../../.astra/fast_lines/out/stack/r4b/changes.html),
[raw timing summary](../../../.astra/fast_lines/out/stack/r4b/summary.json), and
[validation](../../../.astra/fast_lines/out/stack/r4b/validation.json).
The previous `final/` exports remain unchanged for comparison.

## Imports and composition

Deleted the stack copies of `geometry_scout`, `ink_pipeline`, `ink_ownership`,
`ink_motif_gate`, `ink_recurrence`, `ink_repeat_field`, `recovery` and `type_context`.
[reuse.json](../../../prototypes/fast_lines/stack/reuse.json) now records merged-module
imports and hashes instead of snapshot destinations. B runs through
`features_ink.pipeline.ink_run`; C through `shared.type_extended.recover` and its
shared context/recovery dependencies. Geometry imports `geometry_scout`,
`geometry_context`, `geometry_feature_rules` and `geometry_fragment_correct`.
No track modules were edited, and no track acceptance logic remains copied in stack.

The geometry adapter is 38 lines of composition, source-list mapping and receipt
normalization. The shared context accepts intact original sources; Q8 pieces stay
in the current output but cannot masquerade as their original contour or own ink
lost by a reshape. This is conservative when split neighbors exist. All 30 prior
reshapes and all 400 separator cuts remain in the observed result. Shared scouts
are supplied, so Q8 is still called once. B removals precede geometry, fragment
joins and recovery. Their footprints are passed to both new stages.

The resulting order is Paddle → Q8 → B removals → shared geometry → curved-rule
cuts → native fragment joins → extended type recovery. Native contact and the
extended grid are the new runtime dependencies; diagnostic leaf, font, inkiness,
image and stamp censuses remain outside this path. Orientation stays parked.

Type's known v6 table-extent failure was checked explicitly. On
`s2-49598b2e848ab1f0ee1e-p00005`, the post-geometry layout does not nominate a new
supported extension slot, so `table_extents` is null. The prior real recovery at
old slot 15 survives without a bypass or a page-specific exception. The underlying
table-extent flaw remains a limitation on other layouts.

## R4b timings against the owner's target

Each cell is **median / p95 / max, in milliseconds**. Repeat 2 reverses page order.
Decode, original Paddle inference/postprocessing and all conditional corrections
are charged from image file to final items. Model initialization/warmup and review
rendering/serialization remain outside the per-page timer, as in round 4. Raw
receipts preserve the separate startup and stage timings.

| Cohort | n | Repeat | Paddle file-to-lines | Added corrections | Final file-to-lines |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 | 1 | 148.260 / 171.012 / 199.397 | 18.396 / 40.637 / 107.472 | 167.050 / 214.138 / 230.767 |
| Agreement | 40 | 2 | 145.865 / 171.570 / 199.926 | 19.479 / 37.129 / 99.312 | 165.379 / 208.700 / 231.607 |
| Discrepancy | 101 | 1 | 144.759 / 232.447 / 283.099 | 40.311 / 422.769 / 978.564 | 201.741 / 599.435 / 1179.828 |
| Discrepancy | 101 | 2 | 143.504 / 229.803 / 280.637 | 39.048 / 420.418 / 976.601 | 202.943 / 593.836 / 1177.813 |
| All supplied | 195 | 1 | 147.546 / 228.194 / 283.099 | 31.078 / 390.104 / 978.564 | 184.203 / 566.938 / 1179.828 |
| All supplied | 195 | 2 | 145.581 / 227.895 / 280.637 | 32.261 / 388.142 / 976.601 | 182.468 / 566.433 / 1177.813 |

All 390 correction timings are below one second; full file-to-lines time is not:
the maximum is 1179.828 / 1177.813 ms. These are two measured runs on the shared Mac,
not a held-out latency guarantee or a worst-case bound.

There are **latency regressions**. Agreement max was 51.689 / 50.744 ms in the prior
stack and is now 107.472 / 99.312 ms on `an-dbd045ccd84c-p000249`. The new fragment
verifier spends 72.851 / 72.813 ms rejecting a stamp-related candidate; output is
unchanged. Discrepancy max was 688.609 / 653.701 ms and is now 978.564 / 976.601 ms
on `s2-49598b2e848ab1f0ee1e-p00004`: fragment verification costs 590.191 / 603.254 ms
without accepting a join, alongside 290.979 / 287.663 ms in type. These measured
outliers were relayed to geometry and recorded on the shared board. No new gate
was invented here to hide their cost. Lower aggregate medians do not establish a
speedup: Paddle's own timings also changed between rounds on this shared Mac.

The old ink tail stays resolved: `an-778126cc8c2b-p000011` now costs
22.867 / 22.453 ms in combined corrections, including 13.937 / 13.620 ms in B.
The new clean tail has a different cause, native fragment rejection.

## Changed-page review and remaining failures

Exactly **186 complete item lists are unchanged**. All nine changed page overviews
and all **21 raw / previous / R4b crops** were inspected. No new visual regression
was observed in that scope. The two older recoveries on 8686 p7 change their
polygon boundaries, so preservation is not claimed as polygon equality there.
The same visible rows remain covered. Full page observations, including remaining
failures on unchanged pages, are in the updated
[195-page ledger](../../../prototypes/fast_lines/stack/review.json); the
[nine-page change ledger](../../../prototypes/fast_lines/stack/review_r4b_changes.json)
records this round separately.

| Page | Improvement and remaining limitation |
|---|---|
| `an-466cffad2cba-p000323` | One native-validated join reconnects the curved final syllable to its real body row near the stamp. Prior polygon areas stay covered; the stamp overlap and other uneven row boundaries remain. No new visual regression observed. |
| `an-778126cc8c2b-p000010` | One join reconnects the left quotation mark to the same printed dialogue row. Its old rotated envelope leaves an angular corner; nearby quote fragments and central stamp interference remain. No new visual regression observed. |
| `an-a3c2bdf81256-p000112` | One join reconnects a separated ending in the prose heading between grammar tables. Table cells remain separate. The heading still has other fragmented endings; no new visual regression observed. |
| `s2-3229200bf47ca465a42d-p00004` | One join reconnects the left curved fragment with the matching body row. The five previous reshapes persist. Broad old envelopes and many other left-curl straddles remain; no new visual regression observed. |
| `s2-86865c33eef5932c013b-p00005` | Seven joins reconnect real curved right ends, preserving all fourteen old source polygons. Their changed grid also enables a real missing row beginning τους δε, μετα το κοπανισμα, with its right end following the curl. This is a pre-existing bracketed-slot method firing after joins, not a new edge slot. Remaining unjoined ends, incomplete rightmost words and block-edge missing text are visible. No new visual regression observed. |
| `an-466cffad2cba-p000277` | Extended type recovery adds the real first body row below the title beside the large E. The large initial remains outside the main recovered envelope; its full reading-unit geometry is not solved. No new visual regression observed. |
| `an-9ea1564fcf4f-p000202` | One join reconnects the left word continuation with its real dictionary row. Both earlier recovered entries and five reshapes remain. Dense short fragments and adjacent-column boundary difficulties persist; no new visual regression observed. |
| `an-fd4fa0018ae1-p000035` | Extended type recovery adds the real first prose row and includes its large B. It stays above the next body row. The top ornament remains boxed as before; no new visual regression observed. |
| `s2-86865c33eef5932c013b-p00007` | Three joins reconnect two pairs and one three-piece curved row. The two earlier recovered rows remain, but both envelopes shift slightly after the joins change the grid and regional crop. Raw comparisons show the same visible text covered; the last rightmost parts and an unbracketed missing row remain unresolved. No new visual regression observed. |

Totals are **308 Q8 cuts, 92 curved cuts, 30 reshapes, 61 back-print removals,
11 ornament removals, 15 joins and 18 recoveries**. The joins unite 31 prior source
polygons into 15, reducing the count by 16; three extra recoveries bring the final
count to **13,969 items**, down from 13,982. This is not an accuracy score. 58 pages
change relative to Paddle. The new row on 8686 p5 uses an old bracketed-gap slot
that becomes available after the seven joins; it is a combined interaction, beyond
the two new standalone type recoveries. Severe curl, missing ends, broad envelopes,
stamp interference and other failures in the previous ledger remain unresolved.

## Validation and handoff

**142/142 prototype tests pass**, including direct-function identity checks,
no duplicate Q8, rejection-footprint propagation and the raster-boundary audit.
The export validator passes **16,808 checks** over all 195 pages and both repeats:
fresh Paddle equality, source ancestry, Q8 pieces, zero accepted reshape ink loss,
all original joined polygon pixels retained within the actual image, no recovered
polygon intersecting a B removal, valid exports and reviewed outputs.

The first join audit mistakenly counted 22 pixels in the nonexistent column at
`x == image_width`. The audit canvas now clips to the actual half-open image
raster; a regression test distinguishes that boundary from real lost pixels.
No runtime or output changed. Both benchmark source snapshots remain identical;
the two validation-only file changes are separately hashed in
[post-timing-validation-source.json](../../../.astra/fast_lines/out/stack/r4b/post-timing-validation-source.json).
No held-out pages, PDF text layer, production page modules or tests were used.

The imported composition is ready as a prototype; native negative-tail cost and
type's imperfect extent protection remain reasons not to claim the owner's whole
target achieved. The original stack patch was applied by the coordinator as
`f903ec5`; the material below is the historical round-4 record, not current imports
or current measurements.

Git staging was blocked by the sandbox (`index.lock: Operation not permitted`); no new commit or push was made. The requested fallback is [commit-Fstack-r4b.sh](../../../.astra/commit-Fstack-r4b.sh) with its [validated patch](../../../.astra/commit-Fstack-r4b.patch), exact file/deletion manifest and both required trailers.

---

## Historical round 4: owned snapshot version `final`

The combined prototype preserves all round-3 corrections: 308 printed-rule cuts,
92 curved-rule cuts, 30 reshapes, 61 back-print removals and 11 ornament removals.
It recovers 15 lines on 13 pages, one more than type alone. These are measured
operations, not precision/recall scores. Significant errors remain. Timing results
below judge the owner's target literally:

> for pages where small detector has no errors we add negligable overhead, and for pages where it needs fixes we have sub 1 second corrections.

The full [charter](../../../.astra/fast_lines/CHARTER.md) retains the owner's words about
faintness and inkiness, tables, images, curvature, skew, separation and font geometry.
This composition does not turn those requests into solved categories.

Open the [final gallery](../../../.astra/fast_lines/out/stack/final/index.html),
[raw timing summary](../../../.astra/fast_lines/out/stack/final/summary.json),
[validation](../../../.astra/fast_lines/out/stack/final/validation.json) and
[195-page inspection ledger](../../../prototypes/fast_lines/stack/review.json).
The [entry point and commands](../../../prototypes/fast_lines/stack/README.md) use
`prototypes.fast_lines.stack.Stack` or `python -m prototypes.fast_lines.stack IMAGE`.

## Pipeline and interactions

1. Decode the image once; run PP-OCRv6 small once and postprocess it. Keep its original
   probability map and ordered polygon list. No large detector enters this path.
2. Run Q8's cheap printed-rule scout once. Refine and split only its nominated
   corridors. Preserve original source indices on every piece. This establishes
   columns before ownership and grid measurements.
3. Run B's reflected-print ownership and ornament checks on the separated items.
   Delete only their accepted boxes. Store the actual removed polygons permanently.
   Broad image masks and front/unknown ownership never certify recovery.
4. Run A's probability-map geometry scout on original Paddle contours. Its faster
   batched arithmetic preserves the original samples, continuity walk and decisions.
   Dense bands run only on nominated pages. Only intact surviving original sources
   can reshape; the retention guard sees surviving polygons, so a removed neighbour
   cannot hide lost ink. Q8 pieces keep their exact geometry.
5. Refine curved rules from the existing Q8 witness, without repeating its scout.
   Rule ownership still sees all original crossings, including removed ones: deleting
   a back-print box must not manufacture evidence that its rule belongs to the front.
   Cut current survivors along accepted rules.
6. Recover type-grid gaps last. The grid receives a quadrilateral view of curved
   ribbons; ink ownership uses the actual ribbons. Rejected regions veto candidate
   seeds before regional inference and veto proposed/completed polygons afterwards.
   Local table, reflected-print and separator checks remain conditional. New lines
   get regional rule protection, without repeating the full-page Q8 pass.

There is one reusable detector session, decode, map, Q8 witness and source ledger.
The standalone A/B/C wrappers each owned Q8; none of those wrappers is called.
Their distinct geometry, mirror, ornament and grid measurements still have costs;
calling them “one check” would conceal that work. Full-page character censuses,
type profiles and general image masks are not runtime dependencies. Lengths retain
track letter-height/page scaling; no runtime code dispatches by page name.

Type supplied a no-Q8 adapter and concave-polygon exclusions. Its 194 unparked-page
replay kept all 15 additions exactly. Geometry supplied `sparse_fast`: independently
checked 195 page dispatches and 9,586 line witnesses, maximum numeric difference
1.2505552149377763e-11; paths/support and decisions match. Source hashes are in
[reuse.json](../../../prototypes/fast_lines/stack/reuse.json). Copies live within stack
ownership; no track module was edited. The relay exchanges and shared
[stack board](../../../.astra/fast_lines/board/stack.md) record the coordination.

## Measurements

**The sub-second correction target holds on both measured runs; negligible clean-page overhead does not.** All 390 correction timings are below one second. On agreement controls the paired median overhead is 12.857% / 12.543% of Paddle file-to-lines time. Even after the tail fix, roughly 20 ms median and 41–49 ms p95 are material extra work. No latency promise is made for unseen pages.

All times below are milliseconds, shown as **median / p95 / max**, separately for each repeat. Full floating-point values and every page are retained in the receipts.

| Cohort | n | Repeat | Paddle file-to-lines | Added corrections | Final file-to-lines |
|---|---:|---:|---:|---:|---:|
| Agreement | 40 | 1 | 162.326 / 214.133 / 221.794 | 20.400 / 48.545 / 51.689 | 181.795 / 256.500 / 266.600 |
| Agreement | 40 | 2 | 162.499 / 190.368 / 229.310 | 19.910 / 40.811 / 50.744 | 184.350 / 229.361 / 264.700 |
| Discrepancy | 101 | 1 | 170.010 / 258.198 / 290.048 | 40.328 / 371.628 / 688.609 | 226.254 / 542.397 / 922.662 |
| Discrepancy | 101 | 2 | 161.273 / 255.795 / 314.431 | 38.132 / 365.389 / 653.701 | 206.013 / 528.826 / 889.406 |
| Pages with corrections | 52 | 1 | 171.044 / 255.373 / 261.320 | 111.436 / 455.750 / 688.609 | 299.108 / 653.395 / 922.662 |
| Pages with corrections | 52 | 2 | 163.517 / 253.327 / 262.880 | 105.435 / 419.720 / 653.701 | 298.275 / 633.638 / 889.406 |
| All supplied | 195 | 1 | 167.163 / 255.050 / 290.048 | 31.765 / 280.884 / 688.609 | 206.636 / 477.317 / 922.662 |
| All supplied | 195 | 2 | 163.436 / 251.913 / 314.431 | 30.805 / 268.807 / 653.701 | 197.382 / 474.634 / 889.406 |

Both worst discrepancy correction times are `s2-49598b2e848ab1f0ee1e-p00005` (688.609 / 653.701 ms). Its first-run type stage is 532.077 ms, geometry including curved cuts 116.992 ms. The cost comes from conditional recovery and refinement. Agreement maxima are `an-db97e3dd59ca-p000042` (51.689 ms) and curved `s2-3229200bf47ca465a42d-p00002` (50.744 ms). The db97 first-run cost comprises 16.894 ms Q8 scout and 29.689 ms ink, so residual negative checks remain a target.

The agreement median stage costs (repeat 1 / 2) are: Q8 scout 12.412 / 11.898 ms; ink 3.327 / 3.617 ms; geometry scout 3.190 / 3.141 ms; type 0.892 / 0.907 ms. Medians of stages need not sum to a median total. Detector-session startup is 21.719 / 19.630 ms separately; module imports/process startup are outside those startup numbers. These are warm-session, likely warm-filesystem measurements on macOS 26.5.1 arm64 while the other agents were active, not cold-cache guarantees.

The fixed allowlist is 54 development + 40 agreement + 80 discrepancy + 21 extra
discrepancy pages. The discrepancy table pools the latter 101. The same 195 images
are used in both repeats, reversing order in the second run. OpenCV and ONNX use
one thread. One explicit untimed detector warmup precedes each run. The reported
per-page total starts at opening the image file and ends with final polygons;
serialization, drawing and startup are excluded, startup separately recorded.
`paddle_file_s` is decode + original detector inference/postprocess within the same
run; `correction_s` is the paired added cost. This avoids subtracting unrelated
wall-clock runs on a Mac shared with three agents. Raw per-page times, environment,
image hashes, model hash and a frozen Python source tree accompany each repeat.

The 40 agreement pages are controls, not error-free truth: `s2-3229200bf47ca465a42d-p00002`
is visibly curved and acquires one justified reshape. The other 39 retain their
Paddle polygons. There is no PDF text-layer reference and no held-out access.

## The 305 ms ink tail

The initial combined run reproduced the tail on `an-778126cc8c2b-p000011`:
294.383750 ms added cost. This was not geometry, image decoding or ink ownership.
Independent repeated line profiling put ownership at 0.739/0.688 ms; rejected motif
searches on source 13 took 47.062/45.170 ms, source 11 46.738/47.431 ms, source 14
43.675/43.841 ms, source 12 39.117/39.321 ms and source 10 33.924/34.260 ms. Each
reported “reduced spatial repetition absent”. B's separate cProfile found 1,802
`matchTemplate` calls consuming 201 of 305 ms, with enumeration overhead explaining
much of the remainder. The offending work was negative reduced ornament searching.
The [profile receipt](../../../.astra/fast_lines/out/stack/ink-profile-an-778126cc8c2b-p000011.json)
and initial v1 artifacts remain available. These initial single-pass numbers are
not the final repeated timing result.

B replaced that expensive negative nomination with local four-copy recurrence,
using patch correlations and a bounded displacement shortlist. The old reduced and
full template witnesses still make the removal decision. A first FFT/template
shortcut lost real ornaments and B did not ship it. The accepted gate preserved
all final 195-page outputs exactly in this combined run, including all 11 motifs;
this is observed equivalence, not proof of unseen ornament recall.

On the old tail page the complete stack now takes **26.301 / 33.770 ms** of
corrections, with **16.839 / 24.438 ms** in B. The former 305 ms mechanism is resolved
on that page. Positive ornament verification can still be costly:
`an-c99f1c450f55-p000025` spends **533.025 / 480.620 ms** in B. The retained
`motif_costs` records identify every line's nomination/refinement time and reason.
Shared Q8 height is reused only when no Q8 split changed the items; otherwise B
computes its own exact `height_proxy`. Neither map-band height nor type contact
height substitutes for that proxy.

## What the corrections contribute

| Operation | Count | Pages | Combined observation |
|---|---:|---:|---|
| Q8 printed-rule cuts | 308 | 18 | All original Q8 pieces survive unchanged or are explicitly removed by B. |
| A curved-rule cuts | 92 | 3 | 16 on 4959 p5; 55/21 on 661d p5/p9; front column rules produce separate rows. |
| A curved reshapes | 30 | 11 | All pass the surviving-ink conservation guard; no losses hidden by deleted neighbours. |
| B back-print removals | 61 | 3 | 56 on 0ce9 p1, four on 31f40 p1, one on 93f807 p1. |
| B ornament removals | 11 | 10 | Repeated headpieces/strips removed; drop capitals retained. |
| C additions | 15 | 13 | All 14 type-only additions remain, plus a newly available 4959 p5 row. |

52 pages change. Starting with 13,639 Paddle items, 400 cuts, 72 removals and 15
additions produce 13,982 final polygons. Geometry reshapes do not change the count.
Counts are not counts of correctly segmented real lines.

The new interaction is `s2-49598b2e848ab1f0ee1e-p00005`: after five reshapes and
16 curved column cuts, the type grid recovers the real left-column row beginning
“πληθὺς τῶν ἡμεδαπῶν καὶ ξένων μηχανικῶν”. The crop ends before the printed
separator. Type independently inspected the same raw crop and agreed it is real left-column text ending before the separator. Its letter/mark boundary is still imperfect. No page-specific rule was
added to get it. B removal footprints overlap none of the 15 final additions.

## Visual review, remaining failures and regressions

Every one of the 195 final page overviews was inspected against visible print;
all 15 added lines also received raw/after crop inspection. Selected changed pages
were enlarged. The complete ledger records a page-specific observation for every
page. This is not exhaustive glyph-level adjudication of 13,982 polygons. Existing
track reports provide their deeper raw crop reviews; agreement with either detector
is never treated as truth.

No new composition regression was observed in that review scope. Known bad geometry,
incomplete recovery and false positives remain; “unchanged” is not “correct”. In
particular:

- `s2-86865c33eef5932c013b-p00005` remains badly fragmented at the curl. On p7 two
  recovered rows are real, but right ends and an unbracketed missing row remain;
  p23 is an agreement page with visibly imperfect curved geometry.
- `s2-3229200bf47ca465a42d-p00002` gets one useful reshape, but many boxes still
  straddle rows. p3 stays wrong; p4/p6 improve only selected contours.
- `an-d83e7a198ade-p000099` retains overlapping/multirow apparatus boxes despite
  one reshape; `an-d3237d690aa0-p000138` dense index fragments remain (full identifiers in ledger).
- `s2-0ce9d1025b3f23c7119e-p00001` loses the 56 accepted mirrored boxes but retains
  short ghost boxes at the top and elsewhere. `an-ef481610a820` p150/p151 retain
  mirrored/stamp fragments, and p181 remains unchanged. No broad mask was allowed
  to erase nearby text.
- `an-00f143ecce59-p000192` still misses bottom body text; p258 retains tall/drop-cap
  problems. `an-466cffad2cba-p000277` leaves the first body row below its initial unboxed.
- `an-778126cc8c2b-p000007` recovers a true row overlapping a stamp. Stamp exclusion
  is unresolved. `an-c99f1c450f55-p000046` recovers a true row whose envelope touches
  the lower part of the preceding drop capital B.
- The 4959 and 661d newspaper pages improve substantially, but dense multirow and
  cross-column joins remain. `s2-d12a9a4feb23254f4080` p8 abstains on a tight curved-rule corridor.
  `s2-93f8070059f938bda524-p00001` correctly does not turn its back rule into a front
  separator, leaving the corresponding layout difficulty unresolved.
- `s2-63c4d6b9e02507b34a10` p4's dot-leader/table layout is incomplete. Arabic joined-script
  fragments and physical-leaf boundaries remain unresolved. Orientation is parked;
  the designated `s2-6419488b7f8e69fd20da` p1 and sideways `s2-7534648e60694be1d180` p16 receive no rotation.

All full page identifiers and observations are in the tracked ledger, including
otherwise clean-looking controls. No aggregate accuracy or generalization claim is
made; the 44 held-out pages were neither searched for nor inspected.

## Readiness and validation

The one-entry composition, stable source provenance, permanent removal vetoes,
quad-only grid view and owned snapshots are ready as a prototype module. The
printed-rule, geometry, ownership, ornament and recovery operators retain their
track-specific limitations. Production adoption still needs independent held-out
review and a decision about the measured clean-page overhead. Unreadability,
causal inkiness, watermark/stamp separation, general image rejection and severe
curl recovery are not finished by composing the tracks.

**97/97 prototype tests pass** (90 pre-existing plus seven stack integration tests).
The final export audit passes **16,788 assertions on 195 pages**: image identity,
fresh Paddle equality, valid detector-format polygons, null semantic baselines,
no discounted output, original-source accounting, every Q8 piece accounted for,
zero accepted geometry ink loss, no addition intersecting a removal, both timing
receipts and completed page observations. The second fresh run enforces exact
final-item equality page by page. All 195 final exports also match the separately
reviewed initial v1 exports exactly, so the visual ledger transfers without an
unreviewed output change. The public import and single-image CLI were smoke-tested;
the exported line list matches the batch result.

No production `greekocr/pages/` source or tests changed, and importing stack loads
no production page module. No push or background job was started.

The sandbox blocked staging with `index.lock: Operation not permitted` in this
worktree's Git metadata. No commit or push was made. The requested fallback is
[validated patch](../../../.astra/commit-Fstack.patch) and
[commit script](../../../.astra/commit-Fstack.sh), with exact file hashes and both
required trailers. The script checks branch, base commit and unchanged files before
staging only the stack directory and this report.

## R6 commit handoff

Git staging was attempted on `astra/ff-merged` and denied when creating the worktree `index.lock` (`Operation not permitted`). No R6 integration commit was made. The authorized fallback is `.astra/commit-Fstack-r6.sh`, with `.patch`, `.files.json` and `.message.txt` alongside it. The script verifies the exact base, branch, clean index, changed-file hashes and patch before staging only the reviewed paths and committing with the requested trailers. Artifacts remain under `.astra/fast_lines/out/stack/r6/`; no push was attempted.
