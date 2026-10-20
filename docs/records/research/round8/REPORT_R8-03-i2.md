# R8-03 iteration 2 — preserve M33, close geometry partial

**The continuation removal is not safe in a justified nonempty population. No runtime migration is promoted.** The accepted runtime remains `23ee49c813a02209bee144d8baedefe860bfbdf3`; this iteration adds the missing consumer regression tests, deeper native failure traces and a source-bound closing handoff. M33 still has its independent continuation. No path authority, geometry policy or owner failure was removed. **R8-03 closes PARTIAL; G3 is not passed.**

The worktree was `astra/ff-r8-stack` at `42afb7f`, a planning-only merge above 23ee49c. Runtime matched before work and remains identical afterward. Implementation changes are confined to the requested prototype test file. No `greekocr/`, other worker tree, private page, PDF text, orientation, additional agent, background job, push or successor launch was involved. The supplied meter was 78% at launch; no later reading is available. Actual duration and commit/fallback state are recorded in the iteration handoff.

Evidence: [R8-03-i2 gallery](../../../../.astra/fast_lines/out/round8/R8-03-i2/index.html), [failure receipts](../../../../.astra/fast_lines/out/round8/R8-03-i2/FAILURE_CLASSES.md), [no-parent rows](../../../../.astra/fast_lines/out/round8/R8-03-i2/NO_SEED_ROWS.md), `REUSE_RECEIPT.json`, `CONSOLIDATION_DELTA.json`, and `ITERATION_HANDOFF.json`. The `runtime/` link points explicitly to the unchanged accepted 208 exports and their receipts; these are reused, not mislabelled as a fresh full run.

## The missing consumer test is now meaningful

`features_geometry/test_page_field.py` now exercises `geometry_page_field.certify`, not just its inverse helper. A translated mesh has a finite mathematical domain inside a larger region. Thirty-one valid contacts produce left and right certificate records. Thirty-one undefined-phase contacts pass all other region and size filters but must contribute **no** row-zero `body_bottoms`. Separate all-unknown and empty cases produce no certificate. This fixture would have accepted the bad row assignment without the NaN exclusion.

An isolated execution of `certify` with only the finite-phase exclusion removed fails both assertions. Restoring the real function passes them; runtime source was never altered for that mutation. `CERTIFY_MUTATION.json` records the result and source hash. The full fast-lines suite reports **273 passed, 1 known strict faint-front xfail**. The test closes the independent check's software gap; it is not a physical row fix or M33 consolidation.

## Before/after authority and caller map

| Authority | Live route at both start and finish | Closing obligation |
|---|---|---|
| M11 | `geometry_edge_map.scout` → compose field nomination | Map nomination remains distinct from native row truth. |
| M15 | `geometry_page_field.blocks/render/certify/invert_points` → M17 | Shared displacement candidate; finite inverse is correct mathematically, domains/row membership remain partial. |
| M19/M20 | `geometry_scout.sparse_fast`, map bands and original-source correction → `stack.geometry.run` | Useful localization and native retention stay. No original-source contract is changed. |
| M22 | `geometry_contacts.prepare/trace` → fragments/envelopes | Native observations retained. They are neither semantic baselines nor source labels. |
| M33 | `geometry_envelopes.guided` → `correct` → compose `smooth_envelopes` | Independent tangent, contact assignment, envelope and retention remain active. No migrated population or hidden second route. |
| M37 | `geometry_rows.native/confirmed_partition/analyze` → post-field splitting | Existing partial-word limitation remains; only an offline compatible-coordinate probe was added. |

The seven-entry inventory stays **M11/M15/M19/M20/M22/M33/M37**. Definitions remain **height 6 / ink recipes 9 / ownership 9 / bend 7**. Geometry subpolicies removed: **0**. Runtime delta versus 23ee49c: **+0/−0**; cumulative runtime versus d5dc3e2 remains **+194/−709 = −515**, inherited from earlier work. Tests and offline scripts are accounted for separately, never counted as runtime deletion.

## Why no complete bounded migration is claimed

`DOMAIN_POPULATIONS.json` enumerates the accepted observations for every one of the 208 development pages. M33 triggers on **40 pages**, and actually changes **14 items on nine pages**. Accepted finite rules exist on 45 pages; 13 also trigger M33. None of the 14 changed items is itself an original row recorded in the bilateral termination witness. This is a provenance comparison, not a new runtime membership gate.

The existing column handoff is already passed to M15. On **9ea p202 it contains zero rules**, yet M15 has one region spanning four columns and two leaves. There is no missing argument to connect. On **c8 p36**, the positive rule's y support is 995–2740, but `blocks` extends its median-x division above its start. The changed heading is at y688–783: 99 of its observed samples fall in one mesh and 98 in another, with no common domain. Fixing finite-y consumption is necessary there, but does not supply the missing 9ea boundary or correct row membership elsewhere.

The other positive-rule/M33 case, **6f045 p1**, is a short heading within the rule's vertical span, not an observed terminating row. Extending the finite termination certificate to every heading and every point between a median-x cut and the image edge would introduce a new, unchecked domain policy. A single M15 region, absence of a rule/gutter, positive Jacobian or successful candidate crop cannot replace that evidence. The old empty-channel attempt on 9ea/e259/c8 remains rejected; no new gutter variant was built.

Thus no complete nonempty physical population was established from the available providers. This is a substantiated failure to meet the removal target, **not** a claim that all existing fields are physically wrong. There was no live retry using unchanged unsupported inputs and no new count/percentage gate to rescue it. The i1 patches remain evidence only.

## Both failure classes traced to the final crop

Eight fresh actual-Stack traces cover the six rejected crops and p5/p7. They retain original source genealogy, input/output of M33 and subsequent faintness, field replacement, row splitting, reconciliation and final exclusions. All eight outputs and exclusion ledgers match the accepted exports. The native crop evidence was re-rendered and inspected; masked native and display-normalized crops are supplied separately from the historical rejected material.

A useful correction to the i1 diagnosis: **all six rejected final polygons equal their incoming M33 polygons**. The rejected migration did not merely fail to extend three ends; it also failed to perform the useful narrowing on the three neighbour controls. Comparing only to incoming-box ink would miss both classes.

| Control: accepted final / M33 input / original source | Historical rejection/skip | Fresh native outcome and preservation obligation |
|---|---|---|
| 466 p277: 0 / 1 / 1 | Shared envelope fails retention on one unexplained original-mask pixel, then returns shorter input. | That fallback loses 454 accepted-mask pixels at the ending, covering three native contact components. Accepted πό and accent survive in the kept runtime. The tiny trailing horizontal mark is already outside the accepted crop, so complete πό- support is not claimed. |
| 7792 p138: 40 / 42 / 42 | Original retention passes, but new retained-neighbour overlap fails. | Shorter fallback loses 441 accepted-mask pixels, including terminal punctuation and some left-edge support. Accepted punctuation remains. This is not the same retention failure as 466. |
| c8 p36: 87 / 87 / 102 | No field supports the whole heading above the finite rule. | Shorter fallback loses 80 pixels of the isolated right tick. Current crop keeps it. Its identity is uncertain, not a confirmed accent or disposable noise. |
| 9ea p202: 131 / 133 / 173 | Shared route reaches no correction decision for this item; broad incoming box stays. | Incoming box contains previous-row bottoms; accepted local narrowing excludes them. The field's broad domain and path-dependent correction trigger are not row-ownership proof. |
| dbd p359: 25 / 25 / 25 | Shared route reaches no correction decision; incoming multirow box stays. | It includes the preceding “ἀφαιρῇ τῆς πατρίδος …” row. Zero lost ink does not make it correct. Accepted narrowing remains. |
| d323 p138: 23 / 23 / 23 | Competing row contacts veto the proposal before retention. | Incoming box holds preceding word bottoms. Accepted narrowing remains; the rejected rule candidate supplies no domain certificate. |

These pixel counts use the inherited M20 mask and are preservation diagnostics, not complete glyph/source classifications. Whole-component and detached-mark support remain visible in raw crops and NPZ masks. No one-pixel tolerance, mask erasure, neighbour union, blind rectangle or old-tangent runtime comparator was introduced. The unavailable raw polygons of refused i1 proposals are not invented: their recorded decision/source diff, field observations, incoming/final polygons and current native support are distinguished in the receipts.

### P5 no-parent row: compatible input, still no permitted final envelope

For proposals 34/35 on 8686 p5, the existing `unbend` function rebuilt the field crop; recorded rectified polygons were shifted by their recorded offset. The existing `geometry_rows.native` and `confirmed_partition` ran on that crop offline. No native polygon was passed to rectified code, no categorical label raster was resized, and no slow-reference ID or fabricated Paddle parent was supplied.

Each proposal has one complete word track, but **zero certified valleys and zero returned pieces**. The neighbouring tracks remain partial under M37's whole-word requirement. M17's gap between 35/34 would cross rectified components **556 and 612**. The native crops show an uncertain small inter-row mark and visible right-end text support; neither can be waived by size. Proposal 34 has 18 foreign-component flags and proposal 35 has 54. Re-running separation alone does not establish safe ownership, and clearing `field_ready` or emitting the broad proposal is not acceptable. P5 reference row 5 remains unmatched, although its local word track is observed. No extra row is claimed recovered.

P5 rows 40/41 retain the existing residual recovery and “ἀποξήρανσίν”, but curled terminal tops remain clipped. P7 “ἀμπέλων” and row 40 remain represented via the prior type slots, with tight mark/descender boundaries. They were present before this task. `NO_SEED_ROWS.json` preserves all prior row identities and adds current represented/partly clipped/unmatched status. Historical ink-review #19 is not raw DB source 19.

## Source-bound preservation and limits of review

`REUSE_RECEIPT.json` verifies **190 runtime file hashes**, all **208 input hashes**, the **208 detector/evidence/timing triples**, and the 18 source files behind the unmodified saved pixel-seeded reference. The 208 exports contain **15,093 items**. Runtime is exactly 23ee49c, so the prompt's explicit test/docs-only exception applies: the accepted full pass is bound and reused instead of another identical 208 inference pass. Eight control traces and four instrumented slow-page profiles freshly reproduce the accepted exports.

The first profiling assertion incorrectly compared raw internal polygon tuples with JSON vertex lists. An isolated replay identifies p5 item 119's tuple/list representation; serialized coordinates and exported items are exact. `RAW_EXPORT_CONTRACT.json` records this software comparison error. No output difference is hidden by a numeric tolerance.

The six regression crops and five required row contexts were freshly inspected. The unchanged **23-pilot/127-mark** review is source-matched and reused, explicitly not claimed as a new all-pilot review. All **104 comments and 256 marks** retain every original field, quote, number and polygon; current status is appended and inherited dispositions remain visible. The remaining 129 marks were not freshly adjudicated. This limitation prevents a G3 pass; equality is not physical correctness.

Existing ordered one-to-one reference comparisons, unmatched lists, endpoint/body-centre differences and slow normalized examples remain linked. No several-to-one rematching, invented semantic baseline or fast four-guide claim was added. Current normalization is polygon masking plus isotropic display scaling, not a verified dewarp. The reference's slivers, shifted rows, missing Ψ and end clips remain counterexamples, not truth.

Historic c0#118 and d83#108, Ψ, large E and weak τῆς remain preserved by exact runtime/evidence identity. The independent Μαυρομιχάλης row, 4959 central recoveries, ffccc wide-gap last word, next row below d83#108, 7a2b's grouped 30/31/32, severe ends and multirow marks remain open. The retained crop is not called correct merely because its ancestry survived. Source questions for 93f8 #5 and 8686 p26 #9/#40 remain G2 debt. M06 propagation stays deleted; M55 centre-only assumptions, M35 population dependence, both DN-floor hypotheses, pale 1be6 and the strict fully faint-front failure are unchanged.

## Measured cost and R8-04 handoff

The runtime is unchanged, so there is no new claimed speed delta or new paired baseline/candidate runtime comparison. The source-matched accepted full run and both-order i1 timing receipts are retained with their true identities: those earlier pairs compared fb03df1 with 23ee49c, **not** a new i2 algorithm. Instrumented trace/profile clocks are not performance measurements.

| Accepted 23ee49c run, milliseconds | Median corrections | p95 | Maximum |
|---|---:|---:|---:|
| All 208 | 194.913 | 1310.153 | 2002.474 |
| 40 agreement pages | 62.299 | 535.772 | 663.349 |
| 101 discrepancy pages | 210.729 | 1331.711 | 1929.179 |

All-page file-to-final median/p95/max: 331.739 / 1519.407 / 2193.561 ms. **22 named pages exceed 1 s**. Agreement pages are not proven error-free, and their overhead is not negligible. `TIMING.md` carries the complete slow-page list, stage distributions and raw per-page links. Earlier paired correction deltas changed sign (+1.690 and −11.866 ms median), so no gain is inferred or normalized by detector drift. All dependencies, copies, native observations and regional inference remain charged.

The largest accepted aggregate correction work is field proposal (26.916 s over 208), type (11.390 s), row ownership (8.047 s), ink (6.018 s), early field selection (4.471 s), and row splitting (3.759 s). Nested stage clocks must not be added. M33 itself totals 2.452 s: deleting it would neither solve the whole cost problem nor preserve its useful crops.

Fresh cProfile receipts on 4959 p1/p5, 0ce9 p1 and 8686 p5 expose actual array/inference work, separately from timing. For example 4959 p1 performs 235 CC8 builds, 184 morphology calls, 243 box filters and 141 remaps; p5 performs 197/159/435/213. On 0ce9 there are 2,744 resizes and 194 CC8 builds. These are total instrumented calls, not proven duplicate savings. `R8-04_HANDOFF.md` names the caller costs, safe reuse contracts and unique-text dependencies. Regional inference remains necessary for current accepted residual/type rows; a page with an unfixed row can still contain useful field/recovery work. Do not delete all field or recovery work, restore neighbour propagation, or reuse source decisions across changed censuses to meet timing.

0ce9's roughly +200 ms debt versus cb4d6b4 remains. Exact glyph preparation sharing saved only about 5 ms there in the accepted ink check. This iteration does not generalize that saving or silently repeat an ink-source experiment.

## Closing disposition

| Required deliverable | Result |
|---|---|
| Complete M33 continuation migration in a justified scope | **Not met.** No nonempty supported scope; seven authorities and all M33 callers remain. |
| Both failure classes and retained-ending accounting | Source-bound fresh traces/native crops supplied; historical rejection causes corrected. No safe repair promoted. |
| Undefined-phase consumer regression | Complete; mutation fails as required, valid support processed. |
| Preservation and source-bound 208 evidence | Accepted 208 reused under explicit unchanged-runtime exception; eight fresh control traces and four profiles exact. |
| Full physical owner/row/guide completion | **Not met.** Unmatched/clipped/multirow/source cases and inherited review limits remain. |
| Timing target | **Not met.** 22 pages above 1 s; agreement overhead remains material. |

Recommend **23ee49c as the runtime best head**. The scoped test/docs candidate can accompany that runtime after independent review; it is not a promoted geometry replacement. R8-03 closes **CLOSED PARTIAL**. The coordinator checks this handoff and launches R8-04; no third geometry iteration or self-launch is requested. Open geometry/ink obligations accompany speed work rather than being erased or reclassified as success.

The dated i1 addendum and `POST_CHECK_STATUS.json` record runner-applied 23ee49c, ACCEPT WITH NOTES and the coordinator-reported private outcome. Original staging failures, images, arrays and rejected source diffs remain historical evidence. Actual i2 commit/fallback state follows below and in ITERATION_HANDOFF.

## Recorded staging outcome

Git staging failed creating the worktree index.lock: Operation not permitted. No worker commit was made. The validated five-file fallback is `.astra/commit-F8-R8-03-i2.sh`; its exact patch, source binding and forward/reverse validation are in `R8-03-i2/COMMIT_VALIDATION.json`. It stages only the consumer test and four task documents. Runtime remains 23ee49c.

## Post-check addendum — 12 October 2026

The coordinator applied the candidate as `5961754bde92badddc14e8d403fd2a6a791eec65`. The independent R8-03-i2 check returned **ACCEPT WITH NOTES**. This is the best checked head at R8-04 launch; its 190 runtime files still equal 23ee49c. The coordinator reports reuse of its identical private-44 result for that unchanged runtime. The worker did not access those pages or outputs. Geometry remains CLOSED PARTIAL, with no M33 authority removed. The staging failure above is the historical worker outcome, not the current commit state. `R8-03-i2/POST_CHECK_STATUS.json` records this update without altering old arrays, images or receipts.
