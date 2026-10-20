# Round 7, task 2: a shared row coordinate system — candidate, not promoted

The native renderer now places rows from letter-body contacts transported through one displacement mesh per region. Ordered white-gap boundaries produce curved bands; endpoints follow assigned ink. The selectable stack path replaces the round-6 detector rerun, nearest-axis rebuild and field-selection vetoes, and bypasses B for modeled rows. It substantially improves several curved pages, including the foot of 4959 p5 and the right ends of 8686 p7.

**Task 2 is PARTIAL. The candidate is not the default.** Review found genuine text losses, incomplete physical leaf separation and excessive cost. Promoting it would violate the instruction to protect approved results. `Stack()` retains the round-6 execution path; `Stack(row_model=True)` selects this experiment. The two field-placement systems never execute together. No page-specific rule or comparison with a saved output controls runtime acceptance. The old implementation has therefore not been deleted: that part of the requested replacement is unfinished.

Base: `f7e2783949d7185d1a8ad56a65a63794b105b22e`. No changes to `greekocr/pages/`, its tests, ink/type runtime, or the unseen 44 pages. All numerical results below concern development pages. Owner marks informed iterations and are not independent validation.

## What was built and what was reused

The coordinator's `r7_T1_check.md` takes precedence over the task-1 review. In particular, I retained M19–M33 recovery/local geometry and M13 approved column evidence. M18's horizontal-source protection remains a layout-uncertainty condition before fitting. The candidate does not use the rejected round-6 `.75h` distance to Paddle's axis, nor rerun Paddle on a straightened region to place rows. I used the existing `geometry_page_field.render/proposals` knowingly as the starting model: neighboring profile registration, common vertical material coordinates and body-centred row phases. The implementation here has array contracts rather than copying its evidence dictionaries.

The execution order of the candidate is Q8, ink ownership/removals, approved column cuts, retained local geometry/joining, type recovery, retained envelope correction, relative faintness, shared rows, B only outside coverage, final overlap ownership and final-footprint faintness. Exact removals and the normal-ink reference exist before row seeds. This preserves the necessary integration contracts, but is not the final minimal architecture: the remaining legacy adapter and final ownership stage are explicit debts.

New reusable code:

- `shared/geometry_page_rows.py`: `observe`, `regions`, `model`, `bands`, `obstacles`, with array inputs/outputs. `Ink` names component arrays; `Field` names region, displacement, row paths, ordered gaps, nested envelopes, component-to-row assignment and endpoints. Coordinates are page pixels; the observation scale is explicit. Components have half-open bounds. Polygon rasterization does not inherit a mathematical half-open convention automatically.
- `shared/geometry_row_context.py`: legacy item/column/exclusion adapter. An incidence matrix records which native components occur inside existing localizations. Newly emitted rows always have source ancestry or explicitly identified source anchors. Anchors do not claim that Paddle found the new ink. The adapter still handles dictionaries and Shapely objects; it is not yet a complete Rust-ready main path.
- `features_geometry/round7_rows.py`, `round7_evidence.py`, `round7_benchmark.py`, `round7_retention.py`, `round7_review.py`: offline component studies, exact slow/fast comparison, fresh stack runs, retention crops and exhaustive owner ledgers. They are not imported by the decision path.

## Native rendering and its iterations

Local paper-normalized contrast yields native connected components after permanent exclusions have been masked. Repeated component heights in local neighborhoods distinguish bodies from detached marks. The normal reference is obtained before geometry; where A has a supported reference it is passed in. The new census uses mean ridge contrast, whereas A's robust reference is not literally the same statistic. This calibration mismatch remains a limitation. Already localized weaker components can retain existing ownership; unlocalized endpoint growth needs a run of normal bodies. This is not front/back recognition and does not settle task 3's faint-front-print question.

Layout is rendered before bend. Full native empty channels and recursive horizontal/vertical whitespace partitions separate body regions. Compact page-number blocks are isolated so they do not hide a real gutter. A narrow word-space river crossed by existing localizations does not become a column. Accepted printed rules supply finite cuts; this implementation reduces each path to a median x, so it is not a general curved boundary representation. Repeated independent horizontal localizations without a native partition leave the region unknown rather than allowing a merge.

The bend registers neighboring vertical body-density profiles over windows spanning several rows. Knots are spaced in body heights, with one shared displacement field and a monotone vertical coordinate. The flat case is zero displacement; there is no independent curve per detector item. Row phases come from actual body centres in the unbent coordinate. An existing localized singleton can establish a short row. Unlocalized candidates need repeated bodies and a neighboring localization anchor.

Native pixels of assigned bodies and marks form obstacles to a family of ordered shared cuts. A whitespace search near each predicted inter-row gap is constrained by these obstacles. A common one-body tube inside those gaps avoids including entire blank paragraphs or horizontal rules in an OCR crop; actual assigned ink expands that tube for accents and initial shoulders. It is not a separate curve fit. Row endpoints are the individual measurement. The geometry is monotone, but wrong component-to-row assignment can still produce an impossible obstacle conflict, clipped text, or the wrong ownership. Ordered vectors alone are not a proof of correct OCR crops.

The iterations were prediction, rendering, inspection, then revision:

1. Native v1–v3 showed that raw component-centre peaks split accent clusters into rows. Local repeated height and mark attachment improved them. Gaps sampled at `h/4` still shaved letters; later versions use native x sampling.
2. v4–v7 exposed small apparatus letters mistaken for marks, initial shoulders cut by nominal paths and false whitespace channels through short blocks. Local height modes, whole-component ownership and initial shoulder association improved the explicit crops. On d83 p99, the whole `Υπομνηστικόν` word reappeared. On 00f143 p258 the large initial and following row became separate crops.
3. Full-cohort v2 found table-cell merges, thin rules treated as initials and narrow columns rejoined on 93f807 p1. Existing ruled-table regions stay outside the new horizontal model. Compact initials exclude long narrow rules. Unknown independent-column layouts preserve existing localizations.
4. A v5 whole-region rejection based on overlapping component rectangles discarded most useful curl correction. It was falsified and removed. v6 uses actual native component pixels as shared-gap obstacles. This is a change in representation, not another acceptance veto.
5. v7's normal-body retention diagnostic counted 293 lost and 860 gained components relative to R6. All 125 loss contexts were inspected in sheets and selected enlargements. Some losses were ornaments, but others were genuine numbers, letters and curled words. An overbroad layout uncertainty span discarded the left field on 4959 p5; restoring the full repeated-column span changed its diagnostic loss from 38 to zero. This is not a claim that all its OCR crops are correct.
6. Compact margin-block separation exposed 0ce9's native gutter. A proposed finite whitespace-channel extension admitted false channels through large headings; adding every visible component then produced no accepted channels. Neither route was promoted. Native continuation of the existing rule on 4959 p1 failed both straight and curved verifiers.
7. v9 allowed one localized body to establish a row and preserved localized connected words. Borrowing the existing leader renderer with the new census falsely protected prose on 8686 p25 and 31f40 p1, causing losses. That experiment was removed. v10 retains the narrow-word-river check, localized ownership, the whole initial shoulder and long vertical text outside the horizontal model. The latter is insufficient for mixed-orientation tables; 7534 p16 remains a counterexample.

All thresholds are in body heights, page coordinates, native raster units or photometric contrast. They are development choices, not proven universal typography constants. No constants depend on page identifiers. The full-cohort studies repeatedly falsified apparent wins on owner-marked pages.

## What the inspected pages show

- **3229 p4:** the native candidate gives the missing `Μαυρομιχάλης` row its own band. **3229 p6:** several curved starts and formerly shared rows improve; the specifically approved #26 control has a separate final audit rather than being inferred from an overall gain count.
- **4959 p4/p5:** shared phases improve the misplaced foot rows. On p5, three last prose rows have separate crops and the earlier six-pixel sliver is not treated as a row. The lower delta belongs to its own row after the internal joined component stopped being misclassified as an initial.
- **8686 p5/p7:** the shared bend reaches severely curled right-hand prose, including small steep fragments previously skipped by B. Dotted leaders, numeric fragments and text physically clipped at the source edge remain incomplete. Native and reduced drawings disagree on some cells and endpoints.
- **44b5 p2:** bottom rows are placed from bodies and gaps rather than the old half-row-offset boxes. The new geometry is not evidence that pure-skew validation is complete across every font/layout.
- **e259 p198:** native whitespace separates the two body columns. **c8b96 p68:** the four body columns and central binding are separated, but running heads still share a region across the binding; margin annotations are imperfect. Therefore physical leaf separation is **partial**, not solved.
- **d83 p99 / ef481 p181 / 00f143 p258:** several short-row/initial-adjacent cases improve; ef481's short `σι τὸ ἴ;` has its own candidate. Dense apparatus and arbitrary short rows remain unresolved. ffccc p354 is included in the cohort and owner ledger, not silently certified by these examples.
- **4959 p1:** unresolved column layout leaves parts outside the candidate, losing text recovered by the old field. **31f40 p1 / 8314 p20:** word endings remain genuine losses. **7a2b p200:** isolated table numerals remain vulnerable. **7534 p16:** horizontal modeling damages sideways table text. These alone prevent promotion.
- **7792 p154:** many components counted as “lost” are decorative border motifs, illustrating why raw ink coverage cannot stand in for text recovery. Some motifs still get bands; this is not a substitute for task 3.

## The two fast routes

The deliberately slow reference iterates over every assigned native ink pixel to render upper/lower obstacles to each shared gap. Route 1 performs the same reductions with array scatter-min/max operations. The offline harness substitutes the slow operator into the same row model, then independently reruns the array route and compares every emitted item. It does not establish that the common row model is ground truth; phase and ownership errors are shared by both and are judged on page images.

Route 2 reduces the observation to about twelve samples per provisional letter height and rebuilds the same feature. It is checked per region and row, recording nearest spatial correspondence, path error and endpoint differences. Correspondence can be ambiguous: these are diagnostic distances, not a one-number accuracy score. Numeric tables and dense apparatus can change row topology under reduction (an earlier 200e p35 study produced 123 versus 195 row candidates). Route 2 is **not used to authorize corrections**. No cheap scout meeting the clean-page target is ready in this task.

## Full outputs, owner outcomes and validation

The final artifact root is `.astra/fast_lines/out/round7/T2_rows/final/`. `index.html` links correction images and detector-format JSON, native renderings, route-1/route-2 overlays and owner crops. Renderings show blue row paths, orange shared gaps, green normal body centres and magenta region bounds; red outlines in route drawings are the fast candidate. Correction images use the existing stack legend: grey detector, purple changed geometry, green additions, red removals. Parked orientation pages are explicitly recorded rather than interpreted as horizontal-row successes.

`review/COMMENTS.md` and `comments.json` have all 31 current and all 73 prior comment entries. `review/ROWS.md` and `owner-marks.json` have all 256 owner marks, with R6 status, current intersecting item indices, modeled indices and side-by-side crops. **The default keeps the prior outcome for every entry.** Candidate exactness/operation counts are not relabeled as “fixed”. Entries without an adequate visual correctness verdict remain explicitly unresolved. This is an incomplete candidate adjudication, not a hidden count of successful marks.

The whole-component audit counts normal-body components touched by R6 but completely untouched by the candidate, and vice versa. It excludes the union of removed footprints. It does not count partially clipped characters, does not identify text versus ornament, and is not OCR accuracy. All failures are retained in `audit/ledger.json` and the loss crops. The native field only certifies vector nonoverlap within its own region; the retained final ownership stage may still change its polygons. Boundary rasterization is not claimed pixel-exact.

Final measured counts, timings, exact-output checks and source hashes are recorded in `final/handoff.json` and the receipt section below. Tests include physical synthetic flat/curved rows, excluded ink before seeds, singleton ownership, faint tails, tall initial shoulders, a page-number-over-gutter example, a word-space river and ancestry. The pre-existing genuinely faint-front-print control remains a strict expected failure.

## What is ready and what remains

The native-pixel obstacle reduction and common-coordinate array representation are reusable component work. The phase/layout/endpoint construction is **not ready as a replacement module**. Python dependencies are OpenCV morphology/CC/remap/distance transform, NumPy scatter/interpolation, SciPy smoothing/peaks/KD-tree, and Shapely only in the legacy adapter. Rust needs equivalent image primitives, explicit ordered interpolation/scatter, spatial indexing and polygon clipping. Tie order, rounding, connected-component labeling, remapping borders and polygon Boolean behavior must be pinned; a dependency list is not a validated Rust port.

Next work should resolve native layout and incomplete component ownership before optimizing or promoting: separate both leaves including running heads; distinguish real column channels from split word fragments; represent short/connected/table text without losing it when a neighboring modeled row consumes its parent. Then re-audit all approved recoveries and faint exclusions, remove the superseded field and covered legacy mechanisms, and build a cheap flat-page dispatch that still finds missed short rows. A post-hoc “retain everything if anything was lost” veto would hide these model errors and has deliberately not been used.

### Required recovery controls (candidate)

The three coordinator controls were mapped using the owner's reading-order function, not this gallery's numbering. A native paper-relative ink diagnostic inside the old control polygon gives:

| R6 owner segment | Old sampled ink pixels | Uncovered by candidate |
|---|---:|---:|
| c0b02 p10 #118 | 23,261 | 999 |
| d83 p99 #108 | 3,167 | 0 |
| 3229 p6 #26 | 23,838 | 253 |

All three context images were inspected (`final/controls/`). The rows remain visible, but the two nonzero differences prevent an exact-retention claim. The c0b02 change is at the right end; the 3229 context includes two close printed rows. The component-centre audit would miss partial-letter losses of this kind. In the d83 context, the candidate also places the short `Διαμπάξ, διόλου.` row below the retained control. None of these observations authorizes deleting the retained recovery stages. The default retains their original polygons.

### Candidate judgments for current comments

The all-comment ledger preserves every quote. These are the visually inspected candidate judgments, distinct from the unchanged default result:

| Comment | Candidate outcome |
|---|---|
| O01 | Missing name row on 3229 p4 now has a native band. |
| O02 | Curled end behavior changed; exact three named ends not independently adjudicated in the final candidate. |
| O03 | Multiple rows/starts improve; exact-retention control still has 253 differing ink pixels. Partial. |
| O04 | Still unresolved; native layout uncertainty leaves real text losses on 4959 p1. |
| O05 | Many body rows recovered on 4959 p4; every named endpoint not individually certified. Partial. |
| O06 | Last prose rows on 4959 p5 separate in inspected OCR crops. Broader duplicate/fragment correctness remains partial. |
| O07 | Bottom 44b5 p2 rows follow body centres, with separate crops in the inspected full-page rendering. |
| O08–O12 | Ink follow-up remains open. Pre-row exact removals and normal-reference machinery are preserved; no new ownership verdict claimed. |
| O13 | Approved rule machinery retained; candidate boundary result not independently certified. Default unchanged. |
| O14 | Required c0b02 control remains visible but right-end retention is not exact. Missing-third-from-bottom claim not independently closed. |
| O15 | Wide-gap last word remains unadjudicated. |
| O16 | Native candidate has the short row below the retained d83 control; dense apparatus remains partial. |
| O17 | The short ef481 p181 row has its own candidate in the inspected page. |
| O18 | Initial-adjacent row separates on 00f143 p258 in the native rendering. |
| O19–O20 | Included in full exports/retention ledger; last-line correctness not independently closed. Watermark is still an ink task. |
| O21–O24 | Decorative frames/blob remain an ink task, not resolved by assigning rows. |
| O25 | Mixed/rotated content remains outside validated horizontal modeling. |
| O26 | Parked orientation: unchanged. |
| C01–C02 | Severe curled prose is modeled; dotted/cell fragments and all endpoint ownership remain partial. |
| C03 | e259 body columns separated before fitting. |
| C04 | c8 body columns/binding separated; running heads still span the binding. Partial. |
| C05 | Border motifs remain inconsistently boxed. Task 3 unresolved. |

### Array contract and porting boundary

| Function | Input | Output / ownership |
|---|---|---|
| `observe` | `gray: u8[H,W]`, provisional height in pixels; optional `excluded: u8[H,W]`; normal reference `f64[3]` | `Ink`: native/reduced labels `i32[Hs,Ws]`, bounds `f64[C,4]`, centres `f64[C,2]`, area/tone `f64[C]`, body/normal `bool[C]`, scale `f64[2]`, height `f64[1]`, reference `f64[3]`. Background label zero never seeds a row. |
| `regions` | `Ink`, localization bounds `f64[N,4]`, certified cuts `f64[R,3]`, optional localized `bool[C]` | Separated rectangular regions `f64[B,4]`. Finite rule paths are currently reduced to x/y extents: curved boundaries and leaf headers are incomplete. |
| `model` | `Ink`, one region `f64[4]`, localized components `bool[C]` | Shared material knots `f64[K]`, displacement `f64[K,X]`, phases `f64[L]`, paths `f64[L,X]`, gaps `f64[L+1,X]`, inner envelopes `f64[L,2,X]`, component owner `i32[C]` (`-1` unknown), endpoints `f64[L,2]` (`NaN` absent). These are body paths, **not typographic baselines**. |
| `obstacles` | Labels in a region, component owner, raster origin/scale, native x samples, row count | Upper/lower constraints `f64[L,X]`, infinities where there is no assigned ink. The slow per-pixel loop and array reduction have the same coordinate/rounding rule. |
| `bands` | `Field` | Packed vertices `f64[V,2]`, offsets `i32[P+1]`, row IDs `i32[P]`. Source ancestry is assigned by the adapter, not encoded as a fictitious baseline. |

The adapter converts original polygons and accepted column evidence to these arrays, then encodes results back into the repository's detector format. It also retains legacy table handling and polygon subtraction. Moving those remaining decisions into explicit arrays, and separating all diagnostics from assembly, is unfinished. No Rust performance or floating-point parity claim has been measured.

### Final timing (milliseconds, two fresh passes)

These runs follow the final subpixel-domain fix. All correction dependencies are charged: retained geometry/recovery, normal-reference work, native row census, assembly, final ownership and faintness. Detector/decode/startup are separate in each receipt. Pass 2 reverses cohort order. Runs are sequential, with no concurrent rendering/audit job; source signatures match at the beginning and end. Earlier measurements remain in the iteration logs and are superseded here.

| Measurement | Pass 1 median / p95 / max | Pass 2 median / p95 / max |
|---|---|---|
| Candidate full corrections, all 208 | 383.151 / 1220.338 / 1779.736 | 377.660 / 1197.576 / 1768.128 |
| Candidate full corrections, 40 agreement | 324.794 / 469.205 / 591.677 | 320.619 / 466.815 / 572.859 |
| Native row stage alone, 40 agreement | 246.461 / 341.827 / 449.168 | 242.876 / 345.671 / 442.833 |
| Unchanged default, 40 agreement | 63.663 / 568.313 / 684.303 | 64.847 / 556.180 / 675.131 |
| Per-page candidate minus default, agreement | 250.167 / 362.642 / 460.762 | 247.376 / 360.788 / 451.943 |
| Candidate full corrections, 101 discrepancy | 418.524 / 1284.833 / 1779.736 | 418.262 / 1264.115 / 1768.128 |

The maximum is 4959 p4 in both passes. Its native row stage costs 726.979 / 708.852 ms and type costs 516.397 / 495.045 ms. Across all pages, 30 / 30 corrections exceed one second; 15 / 16 are in the 101 discrepancy-page union. Agreement overhead is not negligible. **Both charter timing targets fail.**

The default's fresh 208-page replay exactly matches R6 detector items; the 40 agreement pages have a second fresh pass. The candidate's two fresh 208-page passes both exactly reproduce its saved items, including after the sampling-domain fix. These are reproducibility/default-preservation checks, not candidate accuracy. Detector JSON `seconds` records its initial export; `.r1.json` and `.r2.json` are the authoritative final timing measurements.

The reduced census exposed a subpixel slab whose near-zero spacing requested an unbounded Gaussian filter. The model now reports no resolved rows below one observation pixel; a physical-domain regression test covers it. No page-specific exception was introduced, and all native candidate outputs remained identical after this fix.

### Complete candidate retention ledger

Across all **207 non-parked pages**, the complete-normal-component diagnostic finds **140 lost and 805 gained** components relative to R6. There are 19 pages with at least one such loss. These are raw component counts, not lost/recovered character or line counts. The final loss crops reproduce the previously inspected 48 v10 contexts. Partial clipping is additional, as the required-recovery pixel audit demonstrates.

| Page | Lost components | What the context shows / limit |
|---|---:|---|
| an-7a2b17a3fb0f-p000200 | 12 | Real isolated table numerals; regression. |
| an-c8b96a901917-p000068 | 1 | Small marginal punctuation/body ownership remains unresolved. |
| s2-49598b2e848ab1f0ee1e-p00001 | 19 | Genuine curved words/ends outside resolved layout; regression. |
| s2-831443dc5e6f1ccfbaf5-p00020 | 11 | Genuine table/prose word endings; regression. |
| an-00f143ecce59-p000192 | 1 | Watermark context; not evidence of a lost front-text row. |
| an-1ba3fdb1436b-p000009 | 1 | Decorative mark beside text; not a recovered-text score. |
| an-778126cc8c2b-p000005 | 1 | Small punctuation/context uncertain. |
| an-7792a3301892-p000138 | 1 | Decorative frame context. |
| an-a73d22211479-p000141 | 4 | Genuine short text `ἔτζι)` lost; regression. |
| an-ef481610a820-p000150 | 1 | Weak ink context; ownership not resolved by this audit. |
| an-fd4fa0018ae1-p000031 | 1 | Mark/letter-edge context; not certified harmless. |
| s2-31f40cef90235c91b023-p00001 | 6 | Genuine word ending lost; regression. |
| s2-63c4d6b9e02507b34a10-p00004 | 3 | Leader-dot context; endpoint semantics incomplete. |
| s2-7534648e60694be1d180-p00016 | 49 | Sideways table text; horizontal model is inapplicable and damages it. |
| s2-77d1bd63d5babbe0df73-p00002 | 2 | Partial neighboring-word context remains uncertain. |
| s2-be269b8c315b16befc35-p00003 | 2 | Accented word context; not certified harmless. |
| s2-d12a9a4feb23254f4080-p00008 | 4 | Large heading letters; regression. |
| s2-d12a9a4feb23254f4080-p00009 | 2 | Heading/black-mark context, including real letter loss. |
| an-7792a3301892-p000154 | 19 | Decorative frame motifs; illustrates the difference between ink and text. |

The final ancestry audit checks all 14,681 non-parked output items and requires every newly modeled item to have source IDs. Summed vector intersection between final modeled bands and their pre-row exact exclusions is `6.966963874543205e-13` square pixels (floating-point Boolean residue). This checks that particular exclusion contract; it does not certify that the ink classifier selected every unwanted region or that no unrelated retained legacy item touches one.

### Owner-mark crop inspection limits and additional failures

All 32 sheets (`final/review/marks-00.jpg` through `marks-31.jpg`) were viewed, covering all 256 marked contexts as raw/R6/candidate triptychs. These are context-scale inspections, not a proof that every full OCR polygon contains exactly one whole row. Where the crop or ownership is ambiguous, the ledger leaves the candidate unresolved instead of assigning a success count.

The large standalone Ψ on `an-e74539ae215c-p000633`, owner segment #70 marked **one**, is partly discarded and cut into lower bands (`final/review/an-e74539ae215c-p000633.owner-70.jpg`). It lies outside the modeled body/initial size class. This is a genuine new regression that the normal-body component audit does **not** count. Large glyphs and partial characters must be covered by any future retention assessment.

Narrow multirow boxes persist on `an-a73d22211479-p000301` #56/#57, `an-7a2b17a3fb0f-p000200` #235/#634/#635, and `s2-200e977f2dab5291c42c-p00035` #18/#122. Existing table protection prevents the new model from resolving them; it does not make them correct. The tilted/vertical table contexts on 8314 p39/p42 likewise remain unresolved. In contrast, the 4959 p5 marked prose contexts and several 3229 p5/p8 contexts show rows placed on their bodies rather than the previous half-row offsets. Those visible improvements do not cancel the recorded regressions.

The final native drawings for all 208 pages were also inspected in 18 overview sheets (`final/review/native-overview-00.jpg` through `17.jpg`), including the explicitly parked page. This is a layout-level census, supplemented by the larger curved-page, short-row, retention and owner-context crops above. The overview makes the coverage gaps visible: several dense dictionary/table regions have no accepted shared model; some ornaments still resemble rows; running heads on spreads are not consistently separated. An absent path is unresolved coverage, not a successful correction or evidence that no text exists there.

### Commit handoff

Git staging was attempted with the eleven explicit task files. The sandbox denied creation of `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-fl-geometry/index.lock`; no commit or push was made. The required fallback is `.astra/commit-FT2-r7.patch` plus executable `.astra/commit-FT2-r7.sh`, file-hash manifest and `.validation.json`. The script verifies branch, base, empty index and exact file hashes before staging and committing with the requested trailers. It is intended to run in this worktree once Git metadata is writable; it does not bypass that restriction.

A further scope limit: the layout recursion can split one physical column into separate horizontal text blocks, each with its own displacement mesh. Rows within a region share a model, but these block meshes are not constrained by one physical-leaf surface across paragraph/font changes. Thus this is progress toward the owner's page model, not a completed single bend for every whole column or leaf.

### Final route and validation receipt

Route 1 reproduces the slow renderer's emitted items exactly on **207/207 non-parked pages**. The raw fields contain **11,447 finite-endpoint paths**, each represented in the per-row route-2 comparison ledger. These include paths the adapter may not emit; they are not a count of correctly segmented text lines. The reduced route has **11,422 paths** and a different path count on **75 pages**. **199 native paths have no reduced spatial-region match**. The other nearest-path associations can still be ambiguous; equal counts do not establish equal ownership.

| Explicit example | Native paths | Reduced paths | Interpretation |
|---|---:|---:|---|
| 3229 p4 | 38 | 38 | Equal counts; shared model errors still possible. |
| 4959 p5 | 118 | 118 | Equal counts; final crop review remains necessary. |
| 8686 p7 | 42 | 42 | Severe prose curl is represented; dotted/cell ownership remains partial. |
| e259 p198 | 61 | 61 | Body columns separated in the explicit rendering. |
| c8b96 p68 | 127 | 127 | Headers across the binding remain unresolved on both routes. |
| d83 p99 | 37 | 37 | Dense apparatus remains outside full model coverage. |
| 200e p35 | 54 | 96 | Reduced sampling changes row topology; not safe for correction dispatch. |

The final tests are **234 passed, 1 existing strict expected failure** (`test_lighter_front_and_blurred_footnote_controls`): **235 total**. The final receipt validates **31,120 detector/artifact assertions**, separately from the **14,681 ancestry item checks**, and **1,297 gallery links**. All 104 comment entries and all 256 mark records have output references. Exact candidate replay covers 208 pages in each of two fresh passes; default parity covers all 208.

Frozen prototype source signature: `4bccb67644eaaa612091b00999103adb8723aaff85cb16b2fde3201c4bce90dc`. `final/handoff.json` includes individual source hashes, raw timing summaries, all over-one-second page lists, retention failures and the three required recovery-control pixel audits. No held-out data or OCR text layer was used as a reference.

Post-measurement formatting: the final whitespace check removed exactly one extra EOF newline from `geometry_page_rows.py`. Its parsed Python AST and every non-whitespace byte are unchanged. The measured source above is retained in the receipts, with the exact prior file saved under `frozen_source/`; the handoff source signature is `3afb12f2911eee76cc21b82487f6c0d8ea418e511a35f4f536e39ef1324922de`. `format-only.json` and `handoff.json` record both byte hashes. No decision or timing code changed, and timing was not rerun for this whitespace-only edit.
