# Round 6 C: a shared page bend and an outer-third scout

Status: **PARTIAL**, on top of merged A+B `37433bc`. The stack now has the requested edge-strip scout and a shared displacement field. It can rebuild several rows together through one bend instead of fitting a bend to every box. Severe ends, physical leaf separation, isolated missed rows and the full latency target remain open. A changed segment is not counted as a correctly repaired row.

All artifacts below are under `.astra/fast_lines/out/round6/C_curvature/` in the geometry worktree, outside git. The entry point remains `prototypes.fast_lines.stack.Stack()(image_path)`. No `greekocr/pages` code or tests changed. No held-out pages were opened, no PDF text was used, and no runtime decision uses a page name.

## Evidence and scope

The public cohort has 208 pages: the 195 previous pages plus all 13 supplied pages. Every page has a native mesh rendering, a reduced explicit rendering, a route comparison, numbered final segments and detector-format JSON. The final gallery is `final-v2/index.html`; the raw route ledger is `routes-final/ledger.json`. The final JSON exports use `baseline: null` for field bands: the mesh follows row position, not a typographic baseline.

The native mesh was inspected on full-page sheets, including flat pages and unmarked pages. All 129 field OCR sheets from the first frozen replay were inspected. The later column guard rejects previously proposed replacements and consequently changes subsequent B ownership unions; all 23 final-difference sheets (149 polygon crops) were reviewed separately, as were all 75 touched owner-context images on 19 sheets. These are development observations, not independent accuracy estimates. The owner's 256 marked segments are a reference for judgement, not a tuning target. In particular, B's earlier “0 of 97 one-row marks split” was measured on the same marked crops used during development. It is not a held-out result.

## Explicit rendering: one field shared by neighboring rows

`shared/geometry_page_field.py:render(gray, items, route='slow', column_evidence=None, excluded_regions=())` constructs a vertical displacement mesh over each observed text region. Region boundaries use sustained empty horizontal channels or independently validated printed separators. This is a text-region partition, **not a solved physical leaf detector**. A gutter hidden by crossing input boxes can still be missed.

Native connected ink supplies column density profiles. Correlation transports neighboring profiles; vertical mesh knots span about eight letter heights, so several rows share each displacement parameter. Two joint alignment passes limit accumulated drift. Body-component centres, transported through the field, seed row positions; the line list from our slow detector is not an input. All predicted rows interpolate this same mesh. A non-positive vertical Jacobian rejects a folded correspondence.

The mesh itself cannot certify curvature: repeated letters, a header or back-print can create a smooth false field. A separate observation uses native component bottoms. It compares the outer third with the middle-third straight tangent, retains sufficiently supported departures, checks agreement with the mesh, and requires nearby rows to depart in the same direction. The observation is still imperfect: component bottoms are not true baselines and descenders, broken ink and mixed fonts can bias them.

Rendering legend (`mesh-v8/<page>.slow.jpg`): grey original Paddle polygons; blue predicted row paths; cyan mesh columns; green observed profile peaks close to the prediction; red observations disagreeing with it; red row numbers. Seeds on an ornament, watermark or disconnected accent are evidence of a rendering failure, not additional text.

Iterations and counterexamples:

- Initial adjacent-profile integration accumulated character-shape drift. Joint alignment improved the shared mesh; it did not establish foreground ownership.
- Density lobes produced two seeds within some rows. Native body-centre phase reduced that failure; sparse headings and mixed sizes remain uncertain.
- Direct native-contact bands fragmented words and clipped accents/descenders. Those candidates were not promoted. The runtime instead localizes complete rows once in the unbent region, then measures their native envelopes.
- A fixed `0.45h` profile-step bound under-followed `s2-86865c33eef5932c013b-p00005` and `-p00007`. The final bound uses observed row pitch, below half a pitch. This improves some steep paths but does not solve all clipped ends.
- Already rejected back-print still drove the field on `s2-0ce9d1025b3f23c7119e-p00001`. The field now excludes only the exact footprints already rejected by the ink stage. The raw image is untouched; those footprints remain permanent final exclusions. The resulting zero proposals are an abstention, not proof that the rest of the page is flat.
- Mesh rows can still appear over ornaments, headings, empty gaps or visible verso. `an-5c093c79d6bb-p000199`, two-page spreads and dense apparatus expose incomplete physical separation. `86865…-p00023/-p00025` retain steep ends that neither the scout nor the field reliably captures.

Earlier `mesh-v1` through `mesh-v7` and candidate experiments remain in the output directory. `mesh-v8` is the rendered final field. The later batched-interpolation optimization is bit-exact to it on all 208 pages (`exact-optimization.json`).

## Route 1 and route 2 against the rendering

Route 1 calls the same explicit construction on ink reduced to 12 pixels per estimated letter height. Its images are `mesh-v8/<page>.explicit.jpg`. It generally preserves the large bend, but reduction changes connected components and row seeds. Dense type, faint ink and apparatus can merge or disappear. It was not substituted for native confirmation in the runtime.

Route 2 is `shared/geometry_edge_map.py:scout(pm, items, size)`. It reads Paddle's already computed map. For each sufficiently long box, it samples both outer thirds, extending another third beyond each box end. A middle-third straight fit supplies the tangent. A sustained outer departure greater than `0.35h` nominates only when at least three nearby observations agree in direction. Lengths and search limits are in estimated letter heights or fractions of the box width. The map sampling is a lossy peak rendering; it can switch rows or miss ink. It authorizes a native field measurement, never a correction by itself.

The heuristic is an **outer text-edge check** using box ends. It does not explicitly trace the paper contour or identify which end faces a binding. Both ends are tested, and the window goes past the box. This distinction matters on two-page spreads and short indented rows.

`routes-final/<page>.jpg` overlays native blue paths, reduced green paths and magenta nominated edge observations. The accompanying JSON records every native row, matched reduced row, sampled error along the row, and every edge nomination against the native observed certificate. A failed correspondence is retained. These are comparisons with an imperfect explicit rendering, not precision/recall against truth.

Earlier routes were retained as failed experiments: a density nomination overfired on 126 pages; a native component-bottom scout nominated 90 and cost about 11 ms in exploratory measurements; a tracing walk nominated 86 and cost about 32 ms. The map route nominated 73/208 pages, including 7/40 agreement pages, in the frozen census. Exploratory medians are not final latency claims.

Pure-skew control: `synthetic-v2/` contains flat, positive/negative affine shear and positive/negative bend fixtures. Flat and both pure skews stay quiet; both bends have native and ideal-map witnesses. These are constructed geometric controls, not unseen scans or a learned detector accuracy test. The first fixture put the bend beyond the printed text and therefore failed to test the intended feature; `synthetic-v1` is retained. On real `s2-44b5cf9e0d680b361091-p00005`, skew and local page effects are not independently labeled ground truth.

## Correction in the stack

`geometry_field_detector.run` unbends each natively confirmed region with the shared mesh and runs the existing warm small detector once on the whole region. Native components supply whole-row envelopes and detached marks follow their owning bodies. A whitespace corridor separates adjacent rectified bands only when it crosses no native component. Bands holding native components assigned to another row remain unready. Smooth envelopes are mapped back through the shared field.

`geometry_field_selection.apply` resolves old-to-new ownership from native component coverage. Near-equal owners remain grouped. It then checks the complete final ink union to a fixed point: after any veto, a rejected proposal cannot certify another proposal's loss. Completed initials, independent small cells and every permanent removed footprint are protected. Substantial old native ink must remain in the final union, except inside already validated printed-rule corridors. The three-pixel raster neighborhood handles quantization; it is not a proof of exact vector containment.

The owner asked to replace the older per-line curl paths. Accepted `page_field` items bypass fragment reconstruction, envelope smoothing and B's row splitter. Early replacement is safe only when the unchanged A ownership census proves its existing no-faint-candidate gate. Otherwise the prior geometry must run first so A's exact final removal polygons can be computed; the field then replaces surviving rows. Thus **replacement is incomplete as an execution strategy**: uncertain-A pages still pay both paths. The report does not disguise that cost as a negligible scout.

All A removals, including `removal='relative faintness'`, are byte-for-byte equal to the task-B baseline in both fresh passes. No new exclusion mask is inferred, no rejected line is restored, and field acceptance does not certify front ink. Source IDs and old parent polygons are retained. Original Paddle outputs are freshly recomputed and checked equal.

The shared field also searches the whole region rather than only existing boxes. New unbent rows can replace an owned group of old fragments. Completely unowned candidates are exported in `unowned_candidates` but **are not promoted**: native support alone did not establish foreground ownership and column identity reliably enough. General recovery of isolated missed lines remains unfinished.

## Acting on the independent B review

The review correctly separated a good cut from a bad OCR result. B could follow a whitespace gap while emitting a clipped duplicate of an already covered neighboring row. `geometry_row_ownership.reconcile` now retires a B child only when its substantial native components already belong to a larger neighboring segment. The retained segment receives the exact vector union and ancestry. This removes duplicate OCR submissions without pretending that the remaining crop is clean.

The field preempts many B splits by rebuilding the original curved region before B runs. Saved parent geometry remains available, but this is not a recursive multi-row splitter. Native ambiguity and retention vetoes leave some B children unchanged.

Visual counterexamples still present: the ownership-union crops on `49598…-p00001/-p00005`, `44b5…-p00002`, `c3cc…-p00002` and `3229…-p00005` retain neighboring fragments. Absorbing a duplicate does not trim all top/bottom slivers. Multi-row parents on `an-a73d22211479-p000301` and `an-7a2b17a3fb0f-p000200` are not solved by one valley or by this conservative ownership pass.

An unmarked page exposed a new regression: the first frozen field output joined translation columns on `an-9ea1564fcf4f-p000170`. A gap threshold was inadequate because the boxes nearly touched or overlapped. The final guard preserves horizontally independent old owners whenever replacement would reduce their number, even with a narrow gutter. Unit controls cover narrow gaps and overlapping envelopes. Final images were checked against the rejected first version. Already joined sources and unproven leaf boundaries remain open.

That conservative guard also rejects legitimate joins of detached starts/ends on `3229…-p00004/-p00005/-p00006/-p00008`, `49598…-p00001/-p00004/-p00005` and `86865…-p00007`. Final difference crops show their old fragments and clipped neighboring rows reinstated. This is a deliberate unresolved ambiguity, not a successful separation inference. Full-page ownership is needed to distinguish a narrow column gutter from a gap in one curled row.

B's native cost was reduced by exact vectorized body matching and by omitting unused accent-bridge construction in measure-only calls. Every B item and all 70 cuts remain exactly equal on all 208 A inputs (`exact-optimization.json`). A reduced-resolution B gate was also tried; with an uncertainty margin it preserved the cuts but made the expensive pages slower, so it was reverted. Cached peaks/vector interpolation in the existing contact renderer are a separate exact performance fix checked on 23 affected pages (`contact-equivalence.json`).

## Final counts, owner correspondence and timing

Two fresh serial passes, forward then reverse, reproduce all **208 outputs exactly**. There are **1,048 accepted field bands on 38 pages**, replacing 1,049 pre-field items; only nine of those pages use early replacement. This is a count of emitted bands, not 1,048 proven fixes. The final stack retains 308 Q8 changes, 92 earlier curved cuts, 61 back-print removals, 22 seal removals, 16 ornament removals and all 140 A faintness removals. The new ownership stage retires **14** B duplicate children. The offline 34-child experiment and first frozen 15-child result are not final counts.

The same geometric audit used in the coordinator's review finds **58** B children at least 80% covered by another larger final segment before C and **17** after C. Some disappeared through field replacement and others through ownership union. This audit only counts items still carrying B's `row_partition` flag. It neither proves one-row crops nor detects every kind of duplicate, including overlaps among field bands or with untouched fallback items. `B-duplicate-audit.json` preserves every surviving case. A separate final audit of every accepted field band finds zero bands at least 80% inside another larger final item (`field-overlap-audit.json`); this still does not rule out smaller overlaps or multiple rows inside one crop.

`owner-marks.json` contains all 318 measured records, including all 256 owner marks. C changes the spatial correspondence for **70 of 159 “two”**, **3 of 97 “one”**, and two unmarked records; 89 “two” footprints remain exact. **These are touched counts, not solved counts.** The three changed “one” cases are `an-2cfe28da5103-p000135/22`, `3229…-p00002/23`, and `74cdb…-p00007/37`. Their main row is retained in the reviewed field crop. The owner-context images reuse the old mark's viewport: a neighboring current item can appear as a clipped strip there. Such strips must be checked in the full `field-*` OCR sheets before judging them as emitted fragments. The helper's label “child” means spatial correspondence in these images, not necessarily a new split child.

Route comparison records **14,949 native predicted rows**, of which 13,712 have a reduced-route correspondence within half a height; the other 1,237 are explicit failures of correspondence. There are 20,509 edge observations, 1,376 coherent nominations, and 191 nominations with a corresponding native observed certificate. The native rendering nominates 71 pages, the scout 73, and they agree positively on 39. Those differences are substantial and visible; the native construction is not a reference label. There are **91 entirely unowned candidates**, all diagnostic only.

Timings are wall-clock milliseconds on this Mac, with a warm single-thread ONNX session and OpenCV's requested two workers (the receipt records the actual setting). Image decoding and initial Paddle inference are separate from `correction_s`; every correction dependency is inside it. Export rendering and JSON writing are outside the timer. No CPU experiment ran concurrently with either final timing pass. Raw per-page receipts, source/model hashes and platform are in `final-v2/`.

| Measurement | First pass | Reverse pass |
|---|---:|---:|
| Edge scout, 40 agreement pages, median | 4.324 | 4.205 |
| Edge scout, agreement, maximum | 7.209 | 14.250 |
| Gross new C stages, agreement, median | 4.364 | 4.398 |
| Gross new C stages, agreement, maximum | 606.799 | 612.513 |
| Paired net C addition versus fresh A+B, agreement, median | 5.305 | 4.780 |
| Paired net addition, agreement, p95 | 262.461 | 241.627 |
| Paired net addition, agreement, maximum | 617.198 | 619.834 |
| Entire correction, agreement, median | 33.439 | 33.651 |
| Entire correction, agreement, maximum | 659.750 | 663.769 |
| Entire correction, 101 discrepancy pages, median | 184.829 | 183.323 |
| Entire correction, discrepancy, maximum | 2,008.252 | 1,979.732 |
| Entire correction, all 208 pages, maximum | 2,191.694 | 2,170.486 |
| All-page calls exceeding 1 second | 22/208 | 21/208 |

Gross C includes the edge scout, native column evidence, field proposal, ownership/retention and B duplicate reconciliation. It excludes neither a failed nomination nor a rejected field. Net addition compares two fresh 43-page control passes: 40 agreement pages and the three named 49598 tails. The control uses committed A+B orchestration with the current bit-exact shared performance fixes, so it is not a timing replay of the historical unoptimized checkout. The paired differences include normal run-to-run noise. **37/40 agreement-page outputs are exact to B**; the three changed pages are not assumed to be detector errors simply because C changes them.

| 49598 page | B rows before C, first/reverse | B rows after C, first/reverse | Full correction after C, first/reverse |
|---|---:|---:|---:|
| p00001 | 98.149 / 100.117 | 54.009 / 58.725 | 2,191.694 / 2,170.486 |
| p00004 | 262.589 / 269.032 | 183.764 / 163.051 | 1,776.825 / 1,765.276 |
| p00005 | 551.522 / 547.413 | 343.587 / 338.936 | 2,008.252 / 1,979.732 |

On p00005, field proposals alone cost 596.432/583.474 ms and retention/selection 169.911/169.485 ms, alongside type's 628.068/613.959 ms. Native B still costs 328.642/324.863 ms. The B tail is reduced, but total latency worsens. The largest agreement tail is `an-e259bbf5081c-p000198`. **Both the negligible-overhead target and the subsecond correction target fail.** Earlier exploratory or profiled times are not substituted for these results.

Validation: **216/216 prototype tests**, 416 fresh output checks, 103,464 export/report assertions, 2,297 gallery links and 221 additional owner/comment links checked. Assertions cover fresh Paddle equality, exact A exclusions, repeat equality, ancestry, finite/valid/in-bounds field polygons and permanent-footprint intersections; they are not visual correctness tests. `source-r1.json` and `source-r2.json` agree on source signature `f3ab2c3a92e1dcf2ed08793437cf70bac5d3aa278ad3bdaa0c89a7b68312a7e7`. The gallery includes all 73 original owner comments verbatim, retaining inherited A/R5 judgments separately from the C correspondence. `COMMENT_C_OUTCOMES.md` gives a C outcome beside each comment; `OWNER_C_OUTCOMES.md` lists every touched record with its current operations and display numbers. No remaining issue is marked fixed merely because its old polygon disappeared.

## Reuse, interfaces and remaining work

The implementation uses shared ink exclusions, the existing column certificates, Paddle's map, original contour ancestry, native contacts and the existing warm detector. It does not copy an ink or type pipeline, borrow the false-clear type height census, or broaden a table region into a foreground certificate. Round-2 separators stay active. New modules live under `shared/geometry_*`; the only stack edits compose those modules and pass precomputed column evidence.

Ready as experimental modules: `geometry_edge_map.scout(pm, items, size)`; `geometry_page_field.render`; `geometry_field_detector.run(gray, original, detector, ...)`; `geometry_field_selection.apply(gray, items, proposal, ...)`; `geometry_row_ownership.reconcile(gray, items)`. Their decision ledgers are part of the interface. They are not ready to replace the production page API.

Next work should first resolve physical leaf/column ownership before unbending, then let native field bands establish all row ownership once, including trimmed edge fragments. That would remove duplicated per-line work without changing A's evidence. Steep partial words need measured continuation beyond the current map peak window. Independent unowned rows need foreground and column witnesses before promotion. The remaining B multi-row and sliver examples need multi-row ownership, not another single cut. The latency target requires this shared execution model; exact arithmetic optimizations alone did not meet it.

## Handoff

Git staging was blocked when the sandbox refused creation of the worktree `index.lock`; no commit or push was made. The requested fallback is `.astra/commit-FC_curvature-r6.patch`, executable `.astra/commit-FC_curvature-r6.sh`, message and `.validation.json`. The 23-file patch was applied to base-file copies, checked byte-for-byte against the worktree, reversed back to the base, and reverse-checked against the actual worktree. The script checks the branch, base and every file hash and includes both required trailers. Outputs stay outside git.
