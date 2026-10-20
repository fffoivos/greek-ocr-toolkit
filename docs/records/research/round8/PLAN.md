# Round 8: consolidate the existing feature detectors

[Implementation map](../../../A_ocr_development/reference/LINE_SEGMENTATION.md) · [Documentation index](../../../shared/DOCUMENTATION_INDEX.md) · [Owner closing note](OWNER_CLOSING_SUMMARY.md) · [Current handoff](LOOP_HANDOFF.md). Earlier amendments are dated history. FP8ap refines the conditional recommendation; FP8ao closure and the current ROSTER state still govern. Old launch instructions are inactive.

**The active round-8 allocation is closed. No next task is allocated or launchable.** AUDIT-02 scope is DONE at 1/1 and independently ACCEPT WITH NOTES. The round's segmentation, simplification and speed goals remain PARTIAL. Both owner field allocations still await go. FONT's unused slot stays parked; no unused slot transfers.

## Owner direction for the next allocation — FP8ap, 15 October

**Planning input only: round 8 remains closed, and questions (a)/(b) still await the owner's go.** No task, iteration, worker prompt or launch is created. The proposed four iterations for (a) and two for (b) remain conditional ceilings. The first separately measured step of (a) should now remove unnecessary field computation by preserving the scout's side and finite extent; the field-band crop consumer follows the checked result. This is within the proposed (a) allowance, not an extra speed task or permission to change resolution/passes under (b).

Owner words, relayed verbatim by the coordinator on 15 October:

> what features of the page correlate with taking more time? can we predict them in advance?
>
> is it n of lines?

> right one thing I said but isnt followed now is
>
> whether we can only check for curvature at one of the edges / meaning side of the page, since the page is not likely to have curvature at both sides of the page, or on the hwole page

> Right the main point of doing is that is finding ways to cut time on computations that dont matter so this should be sent to the planner

### What predicts cost, and what the timing does not prove

The coordinator analysed both arms of AUDIT's [TIMING_RAW.json](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/.astra/fast_lines/out/round8/R8-AUDIT-02-i1/TIMING_RAW.json), averaging each page before classifying it. The planner checked the saved JSON and the call path read-only; no timing or OCR run was repeated. The field route, followed by workload within it, is the useful signal. Number of lines alone is not a sound reason to skip correction.

| Saved 208-page observation | Result |
|---|---:|
| Field/scout-triggered route | 73 pages; 135 without field proposals |
| Mean correction time at least 1 s | 30 pages, all on the triggered route |
| Field proposal share of total corrections | 41.8%; slow-page median 923 ms; zero on untriggered pages |
| Early field replacement share | 5.0% |
| Triggered and at least 120 final items | 27 pages, 20 slow |
| Triggered and at least 80 final items | 42 pages, 26 of the 30 slow |
| Untriggered, at least 120 final items | About 356 ms median; none at least 1 s |

The coordinator also reports approximately 11 ms/line versus 2.4 ms/line and Spearman 0.59 versus 0.24 for triggered versus untriggered pages. These are descriptive associations, not the causal cost of adding one line or a validated runtime predictor. **The raw timing writer stores `items=len(result['items'])`, the final export count.** An early prediction must instead use the already available primary detector count and scout result; validate that association before presenting the 80/120 cutoffs as post-detection predictions. Do not put those cutoffs into a quality gate, drop dense pages, or build a separate learned cost model.

One numerical correction to the relay: untriggered maximum is **991.4 ms**, on `an-7a2b17a3fb0f-p000200` (660 final items; 988.7/994.0 ms in the two arms), not about 700 ms. The next highest is 696.0 ms. The main conclusion still holds: all 30 pages averaging at least a second take the field route. Thirty is an average-per-page count; it is not the earlier union of 32 threshold crossings. Averaging the drifted arms does not cure the load changes or establish a speedup. The observations locate work to investigate.

### The existing handoff loses locality

At runtime 046bd52, `shared/geometry_edge_map.scout(pm, items, size)` samples the already charged detector map and emits per-line `side`, `window`, interior reference and coherent neighbours. Its nomination requires at least three coherent records on the same side. `stack/pipeline.compose` consumes only `edge['trigger']` when calling `geometry_field_detector.run`; it does not forward side/window. Thus untriggered pages already skip this route; that is existing behaviour, not a prospective saving.

`run` calls `geometry_page_field.render(route='slow')`. It prepares whole-page density, samples the full width of every selected block, tracks from the centre in both directions, and `certify` checks either edge. For each certified curved block, `unbend` remaps the whole block and `detector.infer` runs again on that block. These callers and `geometry_contacts.prepare` were inspected at the checked runtime; the five source files match 046bd52 byte for byte. This is the concrete computation scope to replace, not another page model or Rust translation. Flat 0ce9 p1 remains a known false-trigger control.

### Revised first step, if (a) is authorised

Carry the existing coherent nomination's **side and measured window, with sufficient straight interior anchor/context**, through the existing field callers. Cheap left/right evidence can select the side; expensive confirmation, density convolution, curved tracking, remapping and regional re-detection should follow only that selected edge domain. The supported interior stays straight apart from its measured skew. Do not compute both sides or a whole block and crop the result afterward. On pages without a coherent one-sided bend, skip this field work and preserve ordinary detection/recovery. Correcting flat false nominations is part of this feature contract, not a line-count shortcut.

Use the binding side as a physical expectation, not a hard-coded left/right choice. Cover both right-curl positives and the owner's left-binding books. A spread contains separate leaves; existing layout evidence must distinguish a leaf from a text column. Conflicting/two-sided evidence is an explicit counterexample to review, not permission to silently process both sides, declare it flat or lose text. If locality cannot preserve final output, keep the candidate unqualified and name the missing dependency.

Reuse `geometry_contacts.prepare(..., density_regions=...)` where its contract fits: it already supports finite convolution domains with Gaussian halos and native page-edge padding. It still measures native components on the whole page; do not claim that passing this argument eliminates all page work. Keep genuinely shared observations that other consumers need. Bind domains to the correct image coordinates, scale, exclusions and complete read/halo support. A partial density/field must never be advertised to downstream users as a complete native-page preparation. No new cache or duplicate detector pipeline. Reducing detector crop windows can change row discovery (the earlier 4959 jitter); keep residual/no-seed recovery and validate actual final masks, not just the mesh.

**Separate qualification before extending the crop consumer:** freeze the current triggered population plus untriggered dense controls, flat/skew negatives (including 0ce9), known right curls, left-binding owner pages, spreads and tables. Demonstrate fewer processed pixels/mesh columns, remap regions and detector calls or detector input area; a shorter final clock alone does not prove removed work. Require same or better whole-page segmentation and every produced strip on development pages, preserving letters, marks, missing-row recovery, columns and source exclusions. Record every changed crop and remaining failure. Run the full 208 and coordinator-only private pages on a frozen candidate; coordinator shows both whole pages, every strip and actual-mask coverage maps. Exposed owner remarks become development-retest, not hidden validation.

Use sequential paired timings in both orders on the triggered pages, with source/settings identities and detector load controls. Report median, p95, maximum, per-page losses as well as gains, and untriggered overhead. Count preparation, field replacement, regional inference and downstream give-back; do not double-count nested stages or credit skipped text as speed. No guaranteed multiplier or new timing run is claimed here.

**Order recommended, not allocated:** side/extent-limited computation and its output/cost check → shared-field crop bands and flat/binding-side completion, with later steps chosen after review → separately authorised resolution/pass work under (b) if still needed. Prefer removing irrelevant domains before sacrificing sampling quality. FONT remains parked; no worker prompt until the owner says go.

## Close the active allocation — FP8ao, 15 October

Carry the checked audit **`2f1c91a09b844c87696b95b6c89cd5c3ff7beede`**, runtime **`046bd52dddeea7ada7727971f1038d34328ba5b7`**. Stack integration `843480a7b6a2e5d9b6d3c0e7a0cd0ec9fddccec3` and ff-merged `b75808bfc05ceb9cc321e8f474a4c8ce10cc93fe` are verified read-only. Audit worker Sol 6.1/high thread `01a13c9d-54fb-7312-aee8-bb3b0807e1a3` is finished. The full [independent check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-AUDIT-02-i1_check.md) accepts the audit with notes. The [dated companion addendum](AUDIT_CHECK_ADDENDUM.md) corrects the committed report/handoff's stale no-commit/pending-review wording and records all six review notes without rewriting the original evidence. Runtime/tests are unchanged; no private 44 repeat or planner page run is needed.

### What the allocation delivered

Final crop masks equal R7 on **205/208 development pages**. Four R rows on 4959 p5, the lower B row on 3229 p2, and the missing A body on 8686 p5 improve; 15,093 items become 15,094. All exclusions remain identical. Some improvements retain old neighbour overlap; 3229 remains a letter-hugging outline and the recovered body still clips its curved end. They are six improved lines, not six wholly clean lines. Separate provenance metadata differs on 33 items/10 pages. General smooth tessellation remains experimental/off-default and complete curved-end gains remain zero. Earlier coordinator-only private checking found one analogous recovered body; the latest INK44 remains identical to its accepted predecessor.

Real deletions include six ink copies (485 lines), unused caches, M06's neighbour propagation and duplicate atlas input authority, plus repeated kernels (103 closings, 8 remaps, 2,205 histograms, 368 mean filters). **Duplicated implementation decreased; competing physical decisions remain.** Live runtime grew net 920 lines versus R7. Inherited 6/9/9/7 counts carry the M33 ink-family caveat in the addendum, not an exhaustive new count. The methodology reviews' demands for physical reference, a real consumer and a displaced decision remain unmet in substantial areas.

The rejected full row replacement, Paddle-seeded slow adapter, CURL B and FONT bodies-only adapter each have a named first wrong input/decision. CURL's failure does not falsify the page field or every local retreat: per-pixel ownership, whole-anchor/row rejection and box-strip tabs prevented a valid final crop. FONT's missing detached-mark input and separate export/reconcile failures must not be called proof that measured guides cannot work. M35's 153-removal ledger and independent 38-case/13-page sample found no confirmed current-leaf loss; the proposed B5-front and slow-reference restoration witnesses would return ghosts. No universal ink-source model was certified.

Final uninstrumented default timings are **descriptive only**: corrections median 264.4/264.6 ms, p95 1766.8/1992.8 ms, max 2735.1/3311.6 ms; 29/32 pages ≥1 s, union 32. Aggregate detector drift 5.674% conceals +20–25% then about −8% within the reverse pass. Do not infer a round-wide gain/regression or a stable slow-page union. Field proposals cost about 41% of corrections; corrections about 3.5× primary detection. Only the earlier source-paired Python rewrite claim survives (~−5% field, ~−3% total on its sample); numerical Rust is exact and 9.3% slower in its tested field boundary. No final clean-page or every-page speed gate is closed.

The audit binds 44 active mechanism groups, 20 old conditions, 104 original comment records and 256 marked segments without changing owner authorship/status. Condition 4-01 passes only its narrow freeze/accounting acceptance text; its advertised detector Rust binding remains absent. Mixed list/string fields, generic checklist pointers and the possible ink-taxonomy omission are documented limitations, not grounds to fabricate clean machine evidence or restart implementation.

### Disposition and owner decisions

| Task | Used / maximum | Final disposition |
|---|---:|---|
| R8-AUDIT-02 | 1/1 | DONE for audit scope; ACCEPT WITH NOTES. No next audit iteration. |
| R8-INK-02 | 2/3 | CLOSED PARTIAL; contract/removal audit complete; i3 retired. |
| R8-RUST-02 | 2/3 | CLOSED PARTIAL; negative speed evidence; i3 retired. |
| R8-CURL-03 | 3/3 | CLOSED PARTIAL; A retained, no complete end gains. |
| R8-GEOM-04 | 3/3 | CLOSED PARTIAL; whole-page experiment stays off. Earlier GEOM allocations remain closed. |
| R8-FONT-03 | 2/3 | One unused slot parked, not launchable or transferred. |

**22 used + 3 retired + 1 parked FONT = 26. Zero active future iterations.** This is the existing allocation's accounting, not all historical round-8 attempts. Meter 18% is the coordinator's report; no 15 October daily cap. The 97%/99% safeguards remain; capacity does not authorise another task. No next worker prompt is written. Coordinator returns to the owner rather than launching an automatic successor.

**Question (a), pending/unallocated:** authorise crops as shared-field bands between neighbouring midlines beyond anchors, with flat/no-curl and binding-side handling? This could connect the existing page field to the owner's smooth shared separators and curled ends. Include both owner-supplied left-curl books as development material, never as private 44. Neither the display curves nor the off-default tessellation are evidence that this default consumer already works.

**Question (b), pending/unallocated:** authorise field-path resolution or pass-count changes under native quality checks? The measured heavy field path makes this the direct speed-design question; a lower-cost setting is not yet qualified. Once-computed density restricted to its read domain and deferred audit-list conversion are separate unimplemented hypotheses (combined suggested 1.1–1.15×, not a measured result). A positive answer to one question does not answer the other.

**Recommendation only if authorised:** (a) first, up to four iterations; (b) next, up to two if separately approved. These proposed maxima are not added to the 26-slot roster or promised sufficient. Start (a) with one actual final-crop consumer of the existing field/midlines, removing the displaced continuation decision; evaluate whole pages across the frozen multi-book geometry/curl controls and owner books. Local component uncertainty must not silently restore whole overlapping rows. Subsequent iterations are chosen after each independent result/check, including flat and left-binding counterexamples. Qualification needs whole letters/marks, smooth shared boundaries, column separation, no new faint-front loss, reviewed per-page exceptions and measured cost; a single repaired page is not general completion. Then (b) compares cheaper field settings to the checked geometry output and records the full 208 tails. Coordinator alone evaluates frozen candidates on private 44 with whole pages, every strip and before/after coverage maps. Exposed owner remarks become development-retest; do not tune to hidden pages.

Keep FONT parked. No new font provider, Rust port, retained-ghost filter or field-speed change is silently bundled into current scope. Retained ghosts (ef481610 p151 items 19/23/36), M55 support, a73d reconcile, mixed/two-row parents, domain and mark/faint-front debts remain individually named backlog. Astra writes a next prompt only after an owner scope/allocation decision; the historical automatic-loop authorisation does not create bonus iterations.

## Close INK and audit the checked round — FP8an, 15 October

**Carry `046bd52dddeea7ada7727971f1038d34328ba5b7`; close R8-INK-02 PARTIAL at 2/3 and retire i3.** The full independent [i2 check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-INK-02-i2_check.md) is ACCEPT WITH NOTES. Coordinator reports stack at 046bd52 and ff-merged 89c2817 with equal runtime. The atlas contract/hardening and preset M35 audit are complete; broader source/frame/mark work is not. No cap is rewritten and no unused slot transfers.

Next is [R8-AUDIT-02 i1](prompts/R8-AUDIT-02-i1.md), **fresh Sol 6.1/high**, track ff8-review, `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review`, branch `astra/ff-review`. Coordinator fast-forwards its clean `fd7bdc52c1eff09c7b2b7ef531aaa817cd2585e6` ancestor to 046bd52 plus FP8an docs, launches with thread argument `-` and records the ID. This follows the owner's Sol execution/Astra planning split and fresh-thread policy at task boundaries. The old Astra review thread's mechanism/methodology reports remain inputs; the separate Opus independent check is unchanged. Planner launches nothing.

### What i2 established, and why a third INK iteration is not justified

The worker reviewed **153/153 M35 removals on 34 development pages**, bound to their native masks, pre-removal pools and actual consumers. Exactly 150 came from the post-envelope call; three from changed post-split/reconcile footprints. The checker verified the complete ledger and reran five pages at both commits, reproducing the origins and unchanged final output. This is a completed physical audit of that removal population, not a source classifier.

The worker confirmed no current-leaf text loss. The checker independently inspected **38 removals on 13 pages across every category**, finding show-through, stamps, blots, gaps or specks and no current-leaf loss. Many of the worker's uncertain/symmetric labels are visibly mirrored at native zoom: asymmetric digits, punctuation side, running headers and names provide stronger human evidence. State these bounded findings accurately; zero confirmed losses is **not proof of zero loss across all 208 pages or all faint text**, nor independent visual review of all 153.

Two apparent correction opportunities instead falsify the proposed replacements:

- **0ce9 source 40**, panel 072, `[1757,2644,2244,2697]`, is distinct from #34/#36. It reads forward, but the checker places it in the ghost layer below the current leaf's last print/signatures. B5 votes 4/0 front; restoring it returns a ghost. This resolves the worker's source question for the removal decision by contextual visual adjudication, without certifying the exact originating leaf or supplying a runtime witness. Panels 113/128 also show qualified direct-favouring B5 votes on mirrored digits. A blanket B5-front veto is refuted.
- **8686 p26 source 41**, panel 147, `[116,419,561,538]`, would survive the slow all-row reference. It is mirrored «καὶ τῆς Γερουσίας». The default removal is right on this example; slow-reference agreement is not ground truth. All 153 native selected masks agree across the compared fast/slow observations, while numerical fields and reference populations differ.

There is therefore no demonstrated, safely separable front-loss population for another correction under the present scope. I3 would either harden unused API cases or start a new source classifier/retained-ghost question. Closing now follows the evidence, not the meter. It does not claim M35's photometric proxy, M55's centre test, source labels, DN floors, FONT or geometry are solved.

### Retained software and private results

GlyphAtlas construction is sealed to one ordered census, including structural validation, fixed dtypes, native exemplar metadata, read-only views and explicit raw-list rejection before the empty-input branch. I2 runtime is **+30/−6, net+24 lines**, only `ink_photometry.py`; combined INK i1/i2 is +43, with no source-policy deletion or physical crop change. The reviewer caught 12/13 mutants, including every i1 survivor; the survivor is equivalent for today's list caller. Deepcopy/pickle produces writable arrays, but no live consumer copies an atlas. Record that lifetime limit; it does not justify another contract-only iteration.

The corrected default B5 census is **255 calls**: 207 ink_run, 26 type recovery, 20 residual proposals, one residual completion, one stack refresh_children; refresh_export is off-default. M35 source/exclusion decisions remain unchanged. 208/208 exports, 15,094 items, actual masks/coverage and non-clock evidence equal 603fbf1; worktree 430 passed/15 strict xfails, bare 429/one older skip/15. No speed gain is claimed. Coordinator-only private 44: **44/44 polygon-identical**, corrections −0.6 ms versus detector −0.9 ms (noise), no republish. These private findings are relayed; planner and workers have not inspected the pages.

### Retained-ghost backlog, not a new allocation

On `an-ef481610a820-p000151`, three mirrored margin marks remain exported in the same column as approved M35 removals: item 19 `[1106,962,1170,1005]`, item 23 `[1108,805,1168,851]`, item 36 `[974,287,1160,339]`. These are retained ghosts, not text losses, and were outside i2's removal population. AUDIT records/binds this known example and the asymmetric-digit/full-stop cues; it does **not** perform a fresh census or implement a filter.

A future retained-ghost audit would need a frozen multi-book retained-and-removed population, genuine faint-front negatives and zero new text losses. Membership in the same column or ordinary/reflected template votes alone is not permission to delete; do not restore M06 neighbour propagation. This is an unallocated backlog item, not an extra owner question or a transferred INK slot. FRAME57, mixed tails, FONT22 and owner cases retain their existing unresolved status.

### What the final audit must deliver

AUDIT is a read-only-code task at 046bd52 plus docs. Reconcile both original reviews, all 44 active mechanism groups and the old 20 assignment conditions; preserve their identities, current callers, physical-reference limits and deletion evidence. Recheck definition counts under the same taxonomy rather than calling a shared value a unified page model. Separate default, explicit optional, offline and parked-branch results.

Rebind all 104 historical owner/coordinator comment records and 256 marked segments to final masks or explicitly unknown status, preserving quotes and old identities. Inspect every final default difference and representative protected/open native witnesses; reuse unchanged evidence with source proof rather than claiming a new full visual review. Keep the independent 38-case sample distinct from the worker 153-case audit, and all development/appendix/private populations separate. The field drawings, experimental whole-page tessellation and Rust parity are not default segmentation fixes.

Close the final-source timing record: reuse two valid uninstrumented full 208 passes only if source/settings-equivalent; otherwise run the two established sequential forward/reverse passes. The instrumented 208 census and 59-page paired INK runs are not that evidence. Report default median/p95/max, every ≥1 s page, agreement 40 overhead, actual threads and detector control; retain invalid timings and evidence limits. Do not attribute off-default 20–34 s tails to default or call exact Rust arithmetic a shipped gain.

Write a portable compact audit plus machine-readable mechanism/owner/backlog records and local evidence manifest. Correct stale documentation navigation and append dated report/check adjudications. No runtime/test/fixture fixes, source moves, new models or hidden feature iteration. A complete audit may conclude the round's architecture, physical and speed gates are PARTIAL. The coordinator still independently checks the audit. A docs-only source-equivalent audit needs no new private 44 run; any genuinely necessary coordinator reproduction includes whole pages, every strip and coverage maps with both versions.

### Pending decisions, order and limits

**Owner question (a), field-band allocation, remains unanswered:** shared-field crop bands between neighbouring midlines beyond anchors; flat-page no-curl behaviour; binding-side detection, including the two owner books. **Owner question (b), field-path speed design, remains unanswered:** lower resolution or fewer passes under separate native-quality gates. Neither is allocated. Exact consumed-density-domain and deferred audit-list hypotheses remain unallocated implementation backlog too. Permission for one question would not answer the other. Keep FONT parked and current Python/final_export=False/bend=False defaults.

| Task | Used / maximum | Disposition |
|---|---:|---|
| R8-INK-02 | 2/3 | CLOSED PARTIAL; atlas and removal audit complete, physical source debt open; i3 retired. |
| R8-AUDIT-02 | 0/1 | Fresh Sol audit prompt issued; last active task in this allocation. |
| R8-RUST-02 | 2/3 | CLOSED PARTIAL; i3 retired. |
| R8-FONT-03 | 2/3 | Last slot parked; no automatic restart. |

**21 used + 3 retired + 2 future including parked FONT = 26.** Only one active iteration remains: AUDIT. Estimate roughly 1–3 hours and 1–2 meter points, with evidence gaps reported rather than fabricated; these are forecasts, not stopping limits. Meter 17% reported; no 15 October daily cap. Standing 97% launch / 99% run safeguards stay. After AUDIT result and full independent check, Astra closes the active allocation and presents the unresolved decisions; no automatic successor or prewritten implementation prompt. Fallbacks remain executable, source/head/hash-bound and callable bare with optional `--check`.

## Audit the actual faintness removals — FP8am, 14 October

**Carry `603fbf1076019a2aa15406f94d7415e7a595bf41`. INK i1's atlas contract is DONE; physical INK remains PARTIAL.** The full independent [i1 check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-INK-02-i1_check.md) is ACCEPT WITH NOTES. Coordinator reports stack at 603fbf1 and ff-merged 36404ac with equal runtime. Resume Sol 6.1/high thread `01a13bcd-9d33-7572-b942-0c308fe17d06`, ff8-ink, ff-ink worktree, `astra/ff-ink`, for [INK-02 i2](prompts/R8-INK-02-i2.md) from this head plus FP8am docs. No later prompt or worker is launched by the planner.

### What the contract achieved

`match_glyphs(query, observation)` takes one frozen GlyphAtlas for scored vectors, aspects and ordered native exemplar metadata. The independently supplied `prepared=` and raw-list routes are deleted and callers migrated. Runtime +31/−12, net +19: this removes an unsafe input authority, not a physical source policy. No natural crop defect was attributed to the former interface. Definition counts remain 6/9/9/7; DN policies 2/2.

208/208 exports and all 15,094 items, masks, coverage and source exclusions equal accepted H. The checker verified all 194 runtime hashes and independently reran five pages with identical outputs. Worktree 421 passed / 15 strict xfails; bare 420 / one older skip / 15. Twelve of fourteen mutations fail; two missing guards concern dtype and raw-list rejection. Current valid callers are consistent. Coordinator-only private44 is 44/44 polygon-identical; corrections median +0.7 ms against detector +0.9 ms, within noise. No speed or physical source gain is claimed.

The active atlas population is 40 pages / 25 books / 47 builds, not the six historical sharing pages. However, equal 254-call totals hid different inventories: the harness missed stack `refresh_children`, the saved-evidence inventory missed 4959 p5's second residual call. Both are atlas-0 and outputs are covered. I2 corrects identities and names `refresh_export` as off-default, alongside the actual live callers.

### I2 engages a physical population

Take the checker's **153 M35 relative-faintness removals on 34 development pages** as the complete target, rather than choosing another isolated mark or restarting frame grouping. The accepted 208 inventory fixes the denominator; preserve i1's atlas cohort separately. M35 has been described mainly through 0ce9's 21 removals, leaving 132 elsewhere without a per-removal physical account. This directly answers the owner's wider-sample direction.

For each removal, bind native image/polygon/mask and responsible stage/census, render a panel with neighbouring print and current B5 native exemplar witnesses, and inspect M35's reference/body/clipping/normal-run decision. Compare its fast observation with existing native slow components on the same footprints/calibration strips; use full slow `render` on disagreements and representative controls, explicitly separating its all-row reference from the fast sampled reference. Neither brightness nor renderer agreement establishes ink source.

All 153 records must be reviewed. Keep separate handedness, text support and leaf-source judgments, including **unknown/mixed**. Do not force an unreadable patch into a certified class. Count confirmed current-leaf losses with exact page IDs, and distinguish zero confirmed losses from proved absence of loss. Every B5-front/M35-drop conflict gets an evidenced disposition or an explicit unresolved source question. The known 0ce9 `[1757,2644,2244,2697]` conflict has 4 front / 0 back votes; its mapping to #34/#36 is tentative, not a verified loss. B5 front means ordinary glyph shape and can include forward-reading show-through. A blanket B5 veto would just add another unsupported authority.

A bounded runtime replacement is allowed only after a loss is independently witnessed and an **existing** physical discriminator separates it from negative controls. Identify and remove/replace the wrong M35 branch; do not add a second full-page source pass or new calibration/noise/threshold family. Require a real final-mask gain, discriminating native tests, all unrelated 208 decisions unchanged, no returned ghost and no reproducible cost increase. If evidence is insufficient, retain M35 unchanged and carry the audited limitation to the i3 decision. The complete audit can be progress without pretending a new policy is certified.

Two handoff corrections are binding. The ἐξόδων breathing is already whole: 20 pixels in 8686 p5 strip #33, none in #35. It is a preservation control; its attachment problem belongs only to withdrawn CURL B. **ἀποξήρανσίν must remain retained**; the check's final sentence accidentally says excluded. The 15 inherited 0ce9 ghosts remain exclusions. Keep faint forward-reading #34/#36 as adversarial source controls without calling their inferred deeper-leaf origin certain.

I2 also closes inexpensive contract gaps: construction shape/length/dtype checks, raw-list rejection, read-only array views, and ordinary metadata-replacement protection through the single factory. Tests pin both former surviving mutants and returned native witness identity without per-query revalidation/rebuild. Correct caller identities and append dated i1 commit/breathing corrections. These do not replace the main physical audit or count as a text gain. M55 centre-only, frame57's unresolved specks, FONT22 and mixed endpoints remain distinct debt; no unqualified provider is promoted.

### Pending owner questions and remaining allocation

**(a) Field-band allocation remains unanswered:** shared-field bands between neighbouring midlines beyond the anchor, flat-page no-curl behaviour and binding-side detection. Rust's closure does not grant it. The two owner books, smooth/no-overlap contract and incomplete curved ends stay visible backlog.

**(b) Field-path resolution/passes for speed remains unanswered:** a separate algorithm task might evaluate lower working resolution or fewer passes with native-text/curvature gates. No permission is inferred. Exact density-domain and unused audit-list hypotheses also remain unallocated implementation backlog for AUDIT to record. INK/AUDIT do not quietly perform them. Permission for either question would not answer the other; coordinator relays any owner response and Astra replans.

| Task | Used / maximum | Disposition |
|---|---:|---|
| R8-RUST-02 | 2/3 | CLOSED PARTIAL; unused i3 retired. Runtime speed result remains negative. |
| R8-INK-02 | 1/3 | Resume i2 for the full M35 audit and small contract notes; i3 prompt follows result/check. |
| R8-AUDIT-02 | 0/1 | Follows best checked INK head; source-bound quality, timing and open-debt accounting. |
| R8-FONT-03 | 2/3 | Last slot parked; no launch or transfer. |

**20 used + 2 retired + 4 future including parked FONT = 26**; three active future slots (INK 2, AUDIT 1). Caps unchanged. Meter 15% reported, no 14 October daily cap; standing 97% launch / 99% run guards stay. Continue the same iteration after any capacity pause. Astra writes each exact next prompt only after the worker result and full independent check.

For changed frozen runtime, coordinator alone compares 603fbf1/candidate on private44 with whole-page segmentation, every actual line strip, actual-mask coverage maps for both, source/exclusion/support identities and paired cost. Review every changed crop. Identical visuals may be reused with equality evidence; source-equivalent offline/tests-only changes need no rerun. Workers/planner see no private pages. The checkpoint retains Python backend, `final_export=False`, `bend=False`, A/H and the R/B rows. A failed source hypothesis does not justify losing those gains. At INK's cap, advance honestly to AUDIT from the best checked subset.

## Close Rust and repair the ink atlas contract — FP8al, 14 October

**R8-RUST-02 is CLOSED PARTIAL at 2/3; retire unused i3. Carry `3605b9276c6885492550ab06777f19c5090b0329`.** The independent i2 check is ACCEPT WITH NOTES. Runtime is byte-identical to 5560714: qualified H hardening remains default, the exact slower Rust field batch remains explicit/off-default. Coordinator reports ff-merged b851790 with the same runtime. No private 44 rerun was needed; the previous qualified private identity and protect timing still apply by source equivalence.

Next is [R8-INK-02 i1](prompts/R8-INK-02-i1.md), **fresh Sol 6.1/high**, track ff8-ink, `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink`, branch `astra/ff-ink`. Coordinator fast-forwards its clean fb03df1 ancestor to 3605b92 plus these docs, launches with thread argument `-`, then records the returned thread ID. Keep `FAST_LINES_FIELD_BACKEND=python`, `final_export=False`, `bend=False`. This planner turn changes documentation only and launches nothing.

### Why Rust closes now

The fixed SLOW27 selection is exact. All 27 pages invoke field proposals; this says they take the field route, **not that all 27 are physically curled**. Flat-page false activation remains an open field defect. Plain correction sums are 44.1866/44.8465 s. The largest coherent interpreted-Python upper bound is field proposals at 19.908%, below the 25% selection gate; its approximate free-Python upper ceiling is 1.2486×. The checker reproduced 14.3% pooled on three pages, 19.7% under a looser bound. Untraced NumPy work and profiler overhead are included in the conservative bound; they are not all interpreter work.

**Sensitivity that the worker omitted:** field_proposals plus field_replace sum to 25.8%/26.8% raw, 23.3–25.0% stage-scaled. That does not qualify as the one boundary required by the prompt. Selection is a separate operation, runs on different item sets early and late, and shares only already-shared preparation with proposals. Interpreter work is spread over eight or more functions. The additional tolist/asarray churn is about 2.8 s (~6%) across dozens of callers. We are declining another port under this allocation's evidence and scope; this is not a theorem that no future native architecture could help.

No safe duplicate deletion was found. The 27 expensive density blurs are once per field page and already shared. Native-page and unbent-crop CC runs use different images. Two extra prepares use original pixels where the field prepared exclusion-filled copies; reusing those copies would be wrong. Two row-selection calls use changed item sets. Runtime and page latency did not improve. The useful progress is a narrower cost diagnosis, lossless smaller fixtures and stronger tests; Rust speed is stalled by evidence, not awaiting a third try.

Fixture bytes fall from 15,499,914 to 6,481,989 (about 58%): 187 arrays are byte-identical, including dtype/order/shape, with content-keyed profile storage and all expected outputs retained. All six real Rust render-consumer tests now fail when the selector is forced to Python. Suite: 412 passed / 15 strict xfails worktree; 411 / one older skip / 15 bare; 451 / one skip / 15 bare with the checker's own build; 82 rust_field tests, zero skips. Remaining minor test debt: missing all render JSON fixtures currently produces a glob empty-parameter skip. AUDIT should record the missing expected-fixture manifest assertion; it is not ink work or a reason for Rust i3.

### Speed backlog and a separate owner decision

These are **unallocated implementation items for the final audit/backlog**, not extra work for INK or the retired Rust slot:

| Item | Evidence and bounded future proof | Limit |
|---|---|---|
| Compute density only where consumed | `geometry_contacts.prepare` already has `density_regions`. Whole-page sepFilter2D accounts for 5.57 s / 27 calls (~12.6% of corrections). A future exact-domain replacement must prove the union of every render/remap and join-fragment contact read, halos/border behaviour and bit identity at all consumed pixels, including future/adaptive domains. Target at least 4 s of the 5.6 s removed. | The blur is already shared, not a duplicate. Tiled/full OpenCV arithmetic and complete domain coverage have not been proved. Do not silently restrict it now. |
| Defer unused audit-path list conversion | `separate_bands`' path-to-list conversion costs roughly 0.5–0.9 s on SLOW27. Defer materialisation only after proving who reads it; evidence must remain identical or explicitly versioned. | Do not drop consumed geometry/audits, globally change polygon representation or call dispersed conversions one port boundary. |

The checker's rough combined potential is 1.1–1.15×, not a measured gain or a guarantee. SLOW27 median is about 1.45 s and maximum 2.64 s, so this forecast would not put every page below 1 s. Field proposals occupy about half their correction time and mostly call compiled blur, labelling, remapping and regional Paddle inference.

**New question for the coordinator to relay to the owner, not an allocation:** should we authorise a separate field-path algorithm task to evaluate lower working resolution or fewer passes, with explicit native-text/curvature quality gates, in pursuit of the under-one-second target? Those choices change the algorithm and its trade-offs; exactness and quality cannot be presumed. The evidence suggests such a design decision may be needed, not that all exact alternatives are mathematically impossible. Do not lower resolution or suppress passes in INK/AUDIT, and do not revive the completed Rust allocation while waiting.

### INK i1 has one implementation target

The prepared glyph atlas has two independent sources of truth: `glyph_atlas` returns immutable numerical arrays, while `match_glyphs(query, atlas, prepared=...)` accepts a possibly different ordered atlas. `ink_ownership.analyze` dereferences match IDs in that separate atlas to obtain native witness boxes. The current caller supplies a consistent pair; there is no demonstrated natural page error from stale preparation. Nevertheless same-length replacement/reordering or mutable metadata can pair scores with the wrong exemplars. The existing changed-membership test rebuilds the preparation and does not test that defect.

**Replace the incompatible paired-input interface with one invocation-local authoritative atlas observation.** Arrays and exemplar identity/order must come from the same selected census; migrate the matcher, analyze and every caller/test. Prefer correctness by construction over another per-query consistency scan/hash. Bind the current source/glyph metadata, retain fresh B5 votes and selection, and preserve existing pixel/tile preparation sharing. A real caller/deletion map and native-witness mutation tests are required. This is removal of an ambiguous data authority, not removal of a source policy or evidence that the 6/9/9/7 physical definitions changed. The task title remains ink/source work; i1 is its specific input-contract prerequisite, not a promise to solve the entire task in one iteration.

Freeze all current atlas-active development pages from the saved 208-page B5 observations, plus same-book no-atlas negatives and named faint/source/recovery controls, before edits. The six historical sharing pages are not assumed to be the whole active population. Require exact current matching/witness/source/exclusion and final-mask parity, the actual once-per-census preparation count, and no reproducible cost regression. Full 208-page census remains the denominator; the 22 owner pages remain a separate appendix. Retain H, A, R and B. No newly recovered text is claimed from this refactor alone.

The same slot produces a short **readiness handoff from existing physical evidence**, not another model or exhaustive census: M55 still centre-only, offline 14/57 versus 43 unresolved with the speck/unit distinction; M35 alone excludes the 15 0ce9 ghosts and #34/#36 source remains uncertain; the named breathing / 22 FONT controls have an unqualified guide-input and export dependency. Do not import the offline frame/guide probes, waive specks, recalibrate DN floors or turn the slot into FONT/geometry. This lets the next result/check choose one bounded physical i2 target instead of assuming a source/frame model is ready. Three INK iterations remain the maximum; no later prompt is written now.

### Pending field-band allocation remains visible

No new owner words or answer arrived. The coordinator's earlier question remains pending: whether to allocate shared-field crop bands between neighbouring midlines, flat-page no-curl behaviour and binding-side detection, originally posed as before or after Rust. Rust is now closed, but that does **not** grant the allocation or silently move it into INK. Keep the owner's smooth/no-overlap output contract and the two left-curl books in the backlog. The field pictures can look useful while the default crops still do not follow the field. The new speed-design question is separate; permission for one would not imply the other. Coordinator relays any answer verbatim; Astra then revises scope/order.

### Loop, evaluation and remaining slots

| Task | Used / maximum | Current disposition |
|---|---:|---|
| R8-RUST-02 | 2/3 | CLOSED PARTIAL; i3 retired, not transferable. Carry 3605b92.|
| R8-INK-02 | 0/3 | Fresh i1 prompt issued. Source/frame/atlas and bounded mark debt; no field algorithm/export work.|
| R8-AUDIT-02 | 0/1 | Follows best checked INK head; audit current runtime, quality/cost and all explicit backlog. No new field/speed implementation allocation.|
| R8-FONT-03 | 2/3 | One unused slot parked.|

Accounting: **19 used + 2 retired + 5 future including parked FONT = 26**; active maximum is four iterations (INK 3, AUDIT 1). Original caps are not rewritten to hide early closure. Meter 15% reported; no 14 October cap, standing 97% launch/99% run safeguards remain. Coordinator now executes executable fallbacks directly after the i2 Python-shebang/bash mismatch; scripts must have a correct shebang, run bare and support optional `--check`. Use dated commit addenda rather than leaving “no commit” as current truth.

For a changed frozen INK runtime, coordinator alone evaluates 3605b92 versus candidate on all private 44: whole-page segmentation, every actual line strip and actual-mask coverage maps for both; native text, source/row/exclusion identities, lost/foreign/duplicated ink and paired cost. Unchanged visuals may be reused with an equality receipt; source-equivalent docs/tests-only work needs no redundant rerun. Workers/planner never inspect private pages; owner-disclosed cases become development-retest. After every result/full check Astra supplies the next exact prompt, coordinator checks the four launch sections, then launches. No success-assuming prompt chain.

## Rust needs a large Python bottleneck — FP8ak, 14 October

**Carry forward `55607147cee021c6c1027ec3b2b7552abd0ce321`; launch [RUST-02 i2](prompts/R8-RUST-02-i2.md).** The independent i1 check is ACCEPT WITH NOTES. Default is the qualified support-bound hardening H (`8bfcbd0`); the exact Rust batch R stays explicit/off-default. Coordinator reports ff-merged `1e2c4a3`, same runtime. Resume Sol 6.1/high thread `01a13b3a-2eb7-7b13-8a8f-8a6b5ce7af4d`, ff8-stack, existing ff-r8-stack worktree/branch, on this head plus FP8ak docs. Keep `final_export=False`, `bend=False`, `FAST_LINES_FIELD_BACKEND=python`.

### What i1 established

The support-bound hardening is **adopted and qualified**, not waiting for another page-clock test. It is exactly the reviewed patch, used only by the supported local-unknown branch in `type_barriers.protect`. Two physical xfails now pass. The witness adds synthetic blank paper, zero ink; this is a bounds correction, not another recovered line. Worker timing is +0.138 ms/affected call; coordinator's private timer is +0.060 ms/call (p95 +0.075, maximum +0.078), about 0.06 ms on the affected private page. Both pass ≤1 ms/call and ≤5 ms/page. Private44 polygons are identical against fea451c, paired correction median +0.7 ms with detector control −0.1 ms. The recovered private body remains. No need to keep H experimental or requalify it as unfinished CURL work.

The `shifts_many` Rust batch is a real callback-free port, not a Python fallback. Checker rebuilt offline from committed source and reproduced bit-exact render/certify/final output on 8686 p5 and c8 p36, with 56/161 actual Rust entries and zero fallbacks. All 230 saved item files (208 + owner 22-page appendix) and non-clock stage evidence match Python; 7,246 real calls across those cohorts. Only two owner pages call it; forced display replay on owner 1868 p23 remains display-only. Worktree: 411 passed / 15 strict xfails. Bare archive: 410 / one older skip / 15; with the checker's Rust build: 449 / one older skip / 15, including 80 native tests without skips. FMA and summation-order mutations fail the real render consumers. The current numerical equivalence is qualified on the recorded Apple arm64/NumPy build, not all platforms.

**It does not save time.** Full 208-page batch sum 4.741772 → 5.183365 s is 9.3% slower; the checker's 24-batch replay reproduces 6.6% slower. Faster search removes only about 2.6 percentage points. This arithmetic was already in compiled NumPy; FFI is under 1%. Integrated clocks change sign with run order. Approximate removable fraction is 5.144% of corrections: even free execution yields `1/(1−.05144) = 1.0542×`; owner appendix ceiling is 1.024×. These use replay and integrated runs, so are estimates, not directly measured achievable speedups. No general Rust speed forecast follows.

I1 default H census: correction median 248.7 ms, p95 1675.7 ms, maximum 2636.2 ms, **27/208 >1 s**. Different cohorts/clocks must not be combined with historical medians or private 44 as a trend. Field proposal's 37.6 s of the 92 s correction total includes inference and M17; type is 14.7 s, ownership 8.1 s. Even `prepare`'s 0.10–0.135 s is mostly compiled work, only about 0.014 s own Python in the sampled calls. Correctness has progressed; speed is stalled at this boundary, and its blocker moved into distributed or compiled work.

### I2 decision: profile first; stop translation if the premise fails

**Do the checker's 27-page gate before deciding to abandon all further Rust.** The two sampled call trees do not establish that every slow page lacks a substantial interpreter bottleneck. Freeze the exact 27-page set by the i1 `TIMING_PER_PAGE.json` rule in the prompt, including zero-call pages, before changing source. Distinguish self/descendant Python, compiled-library/inference time, conversions and unknown attribution. Never call a Python wrapper's inclusive clock interpreted Python, or add unrelated stages until a fraction passes.

A new port is allowed only for one coherent existing boundary with interpreted Python ≥25% of summed corrections on the fixed 27-page cohort; show per-page coverage and uncertainty. This gives an approximate free-Python ceiling ≥1.333× and is an allocation rule, not a universal claim about language performance. Preset qualification: the whole boundary including conversions is ≥2× faster, and correction median **and p95** on the fixed 27-page cohort improve ≥10% repeatably in both orders, with exact parity and no reproducible full 208-page/owner 22-page appendix or no-call regression. No more `shifts_many` tuning; no automatic `prepare` port or historical M17 migration.

**The “close Rust, remove duplicate Python work” branch applies after that profile, not before it.** If nothing qualifies, stop translation in i2. The existing task already includes consolidation: permit one coherent, measured exact duplicate-work removal in this same slot, by explicit result passing and deletion of the old work. Do not allocate a new Python task or use a physical approximation. If no safe deletion is evidenced, retain the profile and test/fixture cleanup. After the check, close RUST PARTIAL at 2/3 on this branch and retire unused i3; then INK follows. Smaller real savings are useful partial consolidation, not a Rust win or global completion. If a qualifying boundary is implemented, its result/check decides whether one bounded i3 is justified. No prompt chain assumes success.

Regardless of branch, add the missing actual-Rust-entry assertion to the real render consumer and compact the 15 MB fixture storage without changing reconstructed numerical inputs/expected bits. Preserve all 24 batches and six render consumers; share a profile only if its full identity matches. Aim for roughly 5–6 MB, report actual bytes. Keep the i1 kernel explicit/off-default as a tested experiment; storage reduction is not runtime deletion. Safe H is carried on every branch.

### The field-band decision remains with the owner

Owner, verbatim:

> they look quite good. / is it fast? / has it helped us to correct segmentation?

The coordinator's five page measurements put field construction at 0.04–0.24 s, with much more work elsewhere. On owner 1868 p23 the runtime edge check stayed silent: its 0.04 s display field is not an active detector cost or segmentation gain. The view's arbitrary parallel curves are useful diagnostic evidence; crops still do not follow them. Curved endings and ordinary overlaps are unchanged by CURL/Rust. CURL's retained physical gain is one admitted body on development and another privately, not completed curled ends.

**Pending owner question, no answer relayed:** should a new task implement shared-field bands between neighbouring row midlines beyond the anchor, flat-page no-curl behaviour and binding-side detection, before or after Rust? The coordinator already asked. No extra iteration, placeholder task, implementation or reordering is authorised here. Continue the written sequence until the owner's reply; record it verbatim when it arrives. Rust must not port a secretly revised field algorithm, and INK must not inherit general crop/field work. FONT stays parked. The specific `ἐξόδων` breathing and comparable attachment controls stay within INK's existing scope. The owner 22-page appendix material remains internal development, not private validation or an all-curled positive set.

### Sequence, review and resources

| Next task | Slots used / maximum | Action and close rule |
|---|---:|---|
| R8-RUST-02 | 1 / 3 | I2 now: fixed 27-page cohort selection gate, one qualified port or bounded exact deletion. No qualifying port boundary → close PARTIAL after i2/check and retire i3. Otherwise planner decides from evidence whether i3 is worthwhile. Full completion still needs the target route, real consolidation and global quality/speed obligations. |
| R8-INK-02 | 0 / 3 | Starts from best checked compatible Rust/deletion head; source/frame/atlas and bounded mark attachment. No new field-band work. First prompt only after Rust closes and is checked. |
| R8-AUDIT-02 | 0 / 1 | Final retained-source quality, architecture and timing accounting, all open debts and experimental switches. Later ink changes require fresh final-head qualification. |
| R8-FONT-03 | 2 / 3 | One unused slot parked, no launch or transfer. |

CURL and GEOM remain CLOSED PARTIAL at their caps. For any changed frozen runtime the coordinator compares baseline 5560714 and candidate privately: whole-page segmentation, **every actual strip and actual-mask coverage maps for both versions**, native text/support/exclusions/identities and paired complete cost on all 44; explicit native routes also need actual entry counts. Unchanged exports may reuse visuals with an equality receipt; runtime-equivalent fixture/docs-only results need no redundant private processing. Workers/planner never access private pages. Exposed owner cases become development-retest.

Astra writes each later prompt after the worker result and full independent check; coordinator checks four sections and launches unchanged except header/placeholders. No Rust i3 or INK prompt prewritten. Accounting now **18 used + 1 retired + 7 future including parked FONT = 26**; six active slots remain at most (Rust 2, Ink 3, Audit 1). Early Rust retirement would reduce future work, never transfer it. Meter 14% reported, no 14 October daily cap, standing 97% launch/99% run safeguards unchanged. Planner edits documentation only, launches nothing; fallback executes bare with optional `--check`.

## Close CURL and begin the measured Rust route — FP8aj, 14 October

**Carry forward `5faa178ebd18c593f9f1c47af64bcbc5dc7ea100`, runtime identical to fea451c.** The independent CURL i3 check is ACCEPT WITH NOTES. The coordinator reports merge 22746a3 in ff-merged. [R8-RUST-02 i1](prompts/R8-RUST-02-i1.md) starts fresh Sol 6.1/high (`-`, record its returned thread ID), ff8-stack, the existing stack worktree/branch, on this head plus FP8aj docs. Keep `final_export=False`, `bend=False`; no Rust backend is currently adopted.

The owner authorised continuing after closing the chat. Their standing sequencing instruction remains:

> ok lets just normally continue with the rest of the tasks in the plan

### CURL closure and corrected diagnosis

A is retained: one recovered body on 8686 p5 and one on the coordinator's private pages. I3 changes no runtime: all 208 exports match fea451c, and the checker reproduced four pages. Worktree tests: 368 passed / 17 strict xfails; bare archive: 367 passed / one older skip / 17 xfails. No redundant private44 run was needed. **Zero complete curved endings were retained in three iterations.** Admission has a physical gain; curved-end output is stalled while the mechanism is better located.

The support-bound patch is a small, ready correction. Its unclipped fixture traverses real recover→protect, but the added overhang is synthetic blank paper (zero ink), with no natural occurrence among 208 pages. It proves the geometric bound, not newly protected text. Two strict xfails pass under the patch. Every attempted whole-page clock was invalid; invalid clocks establish neither a slowdown nor a failure of this correction.

B remains withdrawn. The 3229 p5 tab duplicates 512 pixels of the upper row's «ρο»; its owner retains all 609. Rectangular old-strip unions account for that construction's tabs. On 8686 src37, however, the first obstruction is **its own initial φ** at the left anchor while only the right end is being extended. Requiring every glyph pixel to be closest to one phase misclassifies a descender; `shape=original` resets the whole row. Removing that reset diagnostically reaches a 3×4 mark, probably the breathing over «ἐξόδων», then still encounters whole-row `rule_barriers` and `owned_retention.lost_ink` checks. The attempted migration removed one gate and retained or introduced others. Correct the archived conclusion to these named failures; **local retreat itself was not falsified**. No further CURL implementation is authorised by this amendment.

### Land the narrow hardening first, within RUST i1

Accept the reviewer's recommendation now, not deferred to AUDIT. RUST i1 begins with an independently reviewable hardening checkpoint **before any port**, reusing `evidence/curl03_i3_support_bounds_unqualified.patch`, the existing helper and real-caller tests. Remove only its two repaired xfail markers; keep the curved-end xfail. This is included in the existing first Rust slot, not a fourth CURL slot or a separate task.

I take responsibility for correcting the previous timing rule here: a whole-page detector-drift test is the wrong instrument for two polygon clips and one small point-in-polygon check. Measure the increment around `protect`, with representative real branch inputs, fresh immutable arguments, alternating fixed batches and timer overhead shown. Preset hardening budget: median incremental cost ≤1 ms per affected call and ≤5 ms per affected page after multiplying by measured call counts. Use the existing 208 equality, bound to the exact patch, plus fresh focused reruns; redo 208 only if source, inputs or outputs differ. Coordinator checks private44 identity and the affected private `protect` call before accepting this checkpoint. A stable excess needs investigation, not repeated page timing until it passes. Keep the stage measurement, theoretical nature and inherited global cost separate; no speedup claim for hardening.

Then qualify a substantial stable numerical Rust boundary against the hardened Python source. First choice is the M15 mesh calculation inside `geometry_page_field.render` (`shifts_many` interpolation/lag scoring, outward propagation and template refinement), selected with a current non-overlapping profile. It feeds existing `certify`, `geometry_field_detector.run/unbend/displacement`, field selection and M33; porting it must preserve their current behaviour. Do not spend another pilot on historical M17 alone: its measured 1.62× local gain was only 2.8–4.0% in corrections, and callbacks occupied about 75% of its Rust stage. Choose a coarse typed-array boundary and measure all preparation, copies, allocations and remaining callbacks. Current M17 request-completion changes are absent from the old pilot; do not merge its old runtime over them.

A parity-checked, faster native boundary is useful partial progress. A test oracle may remain, but adopted execution must not call both implementations or preserve copied bridge decisions. An experimental explicit backend is allowed during qualification; default adoption requires integrated parity, real speed evidence, clean build/tests and the coordinator's check. Full task completion still requires the declared route, actual duplicate removal, preserved quality and the speed gate. No forecast of a 1.5–2.5× whole-pipeline gain is reinstated.

### The owner's field picture changes what we can claim

Owner, verbatim:

> can we make a representation of the results as we initially discussed? i.e. parallel lines that are independent of the text / that will be straight if curvature is zero but bend according to the curvature of the page? / how are we from this?

The coordinator produced the [field view](https://claude.ai/artifact/Ni4tvVh1UvhDpVF96rFvSs). I read the local display script and development/owner metadata, not private pages. It samples constant-phase curves from `geometry_page_field` via `geometry_field_detector.displacement`. Curve locations are independent of individual text rows, but the estimated mesh is still derived from text observations; this is not a recovered blank-page 3D surface. When the runtime edge check is silent, the view computes `render(..., route='slow')` **for display only**. Those curves must not be presented as active runtime detection.

The coordinator's measurements: median maximum departure from a straight line is 0.66 line heights on 14 flat negatives (maximum 1.61), 1.03 on four positives and 0.73 on skewed negatives. Edge check/certification: positives 4/4 and 4/4; flat negatives 5/14 and 2/14. Private aggregate, coordinator only: median 0.67, with 16/44 firing and certifying. These counts do not provide a private false-positive rate without private labels. **Bend magnitude alone does not discriminate physical curl.** The earlier “adequate mesh” claim is bounded to the known right-edge examples; flat/no-curl and binding-side performance are open defects, not implementation details that a port fixes.

New owner material: seven 1868 d8dfd7 pages and fifteen 1876 292f4a pages, 22 total, are internal Anemi **development** cases. The 1868 p0023 binding-side curl is owner-confirmed; do not label every page in both books positive. On p0023 the measured field under-bends the line starts and runtime edge/certify stay silent. Only 2/22 owner pages trigger. Use the `owner/` PNGs and `owner_out/fields.json` under the coordinator's fieldview directory named in the prompt; originals remain in glossapi-ocr-local. Keep `_REPL` filenames distinct and freeze hashes before using the appendix. Do not modify the existing 41/208 denominators or present this appendix as private validation. Never publish internal scans or read fieldview's `heldout/` or mixed `files.json`.

### Exact place of field-band construction in the remaining plan

The proposed replacement is well aligned with the owner's “middle line” idea: beyond an observed anchor, use the shared-field strip between adjacent row-phase midlines as the crop, with whole-component, local ownership exceptions. Ordered phases tile only within a finite, monotone, shared column domain and consistent raster convention. They do not by themselves prove correct row identities, detached-mark ownership, finite gutter boundaries or smooth transitions to old in-anchor crops. Treat this as a promising **unimplemented replacement contract**, not a checked construction or evidence that all flat-page paths are valid.

| Work | Owner in this allocation |
|---|---|
| Numerical field computation, optional backend/build, exact input reuse and measured speed | RUST-02. Preserve Python semantics including known flat/left-edge defects; do not repair them while claiming port parity. New owner pages provide a separately reported parity appendix, and display-only field replay is labelled separately from runtime calls. |
| Breathing over «ἐξόδων» and comparable marks under another row's descender | INK-02, a bounded component/body attachment question using existing native evidence and the 22 FONT cases. No “every pixel nearest phase” rule, universal font-model restart or automatic smoothing-policy change. Unknown stays explicit. Existing source/frame obligations remain. |
| Replace M33 edit/veto geometry with field bands; remove anchor reset and remaining whole-row gates locally; correct flat/left-edge detection | **CURL/geometry backlog, with no implementation slot in the remaining plan.** First prospective cases are the two new left-curl books, plus known right curls and flat/skew negatives. Not smuggled into Rust or INK. Requires a later owner allocation. |
| Trace all of these obligations and whether hardening/port/mark work is actually retained | AUDIT-02. Preserve whole-page/strip/coverage evidence and original owner ledgers; open geometry stays PARTIAL. |

This remaining allocation cannot honestly promise complete curvature/segmentation. It can deliver speed on a stable route, narrower ink decisions and a clear final audit. No extra slot is inferred from the new field-view request or the new examples. FONT's unused slot remains parked.

### Review loop, resources and delivery

For any changed default/runtime candidate, the coordinator privately compares the checked baseline, hardening checkpoint and proposed native route as needed: **whole-page segmentation, every actual line strip, actual-mask coverage maps for both versions on every private page**, including unchanged pages and the recovered Anemi body. Compare polygons, mask/ink coverage, exclusions, source/row identities, missing/extra text, curved ends and timing; include a private stage timer for the hardening branch. A frozen source-equivalent checkpoint need not rerun identical work; record equivalence. Private images/data stay with the coordinator. Owner-disclosed pages become development-retest.

After each worker result and full independent check, Astra writes the next exact prompt; coordinator checks its four sections and launches it unchanged except header/placeholders. No RUST i2 or INK prompt is prewritten. At each maximum close honestly and advance on the best checked compatible head. Timing claims distinguish the small repair, native boundary, complete stage, corrections and file-to-final; later INK changes require final-head requalification.

Accounting: 17 used + 1 retired + 8 future (including one parked FONT) = 26. Remaining active work is seven iterations: RUST 3, INK 3, AUDIT 1. Meter 13% reported, no 14 October daily cap; standing 97% launch/99% run safeguards remain. No arbitrary time cap or extra worker. Planner is read-only on code and launches nothing. Fallback scripts execute bare; `--check` may validate only.

## Keep the recovered rows; make continuation refusal local — FP8ai, 14 October

**Best checked head: `fea451c5ec234e196076074cc1f9bd9233da41f3`. CURL-03 has used 2/3 iterations; [i3](prompts/R8-CURL-03-i3.md) is the last slot**, resuming Sol 6.1/high thread `01a13968-c97e-7191-8842-cb64b8b62789` in ff8-stack. The coordinator reports ff-merged a9fc83a has the same runtime. Start from fea451c plus these docs; keep `final_export=False`, `bend=False`. General geometry stays CLOSED PARTIAL and FONT's last slot parked.

### What is retained, and what remains blocked

I2 is PARTIAL, independently ACCEPT WITH NOTES. Only `type_barriers.protect` changes at runtime (+22/−2 lines). An unverified vertical-run nomination now keeps exactly one independently witnessed side through existing `piece_support`. The 8686 p5 row body “τρου χωρητικότητος … ὀψίμως συλλεγομέ” survives final compose. Its 24 witnessed components are preserved; other tail/terminal support is still clipped. Do not call the entire line or all its glyphs complete.

Development: 207/208 pages identical; 8686 p5 gains one crop. Coordinator private44: 43 identical, one Anemi page gains one correct body line between retained neighbours. No other final crops change. These are two changed pages across the cohorts; avoid the check's inconsistent “251/252” aggregate. Private timing is +1.4 ms paired median (detector +0.4), +19 ms on the changed page, seven pages over 1 s in both arms. Development affected-page cost is +35/+38 ms. Bare archive: 363 passed, one older skip, 14 strict xfails; worktree: 364 passed, 14 xfails. Restoring whole-proposal rejection fails the actual returned-raster assertion. M4's all-witness mutation is equivalent because `piece_support` already restricts to the clipped piece; do not write an artificial test merely to kill it.

Duplicated native ink around the recovered row is overwhelmingly its own descenders under the unchanged legacy box below: 687 of 708 inspected Otsu pixels (97%). Report the small other/uncertain residue too. Non-overlap remains unsolved. Flat floors trim 5–13% of several tails, about 24% of the terminal μ; risen νων remains out. These are exact extent debts, not evidence that the line admission was wrong.

M33 part B is wholly withdrawn and byte-identical to the old runtime. The common mesh, finite search and better ownership signal still recover zero whole end letters because `material_foreign` returns at the first contested component and `correct` rejects the entire row. Src37: 119 off-row pixels in ten components veto 16,857 own pixels. On 8686 p5 every row refuses. The attempted `material_band` revision also crashes on 4959 p5, c8 p36 and 9ea1 p202 with an empty grid. **Converging on mechanism, stalled on curved-end output; admission now has a retained physical gain.**

### I3 decisions

**Accept the local-retreat recommendation.** Reuse the existing finite shared continuation and unchanged in-anchor map path, but remove the supported population's whole-row refusal. Return finite conflicting/unknown component intervals instead of a first-error string. Starting at the anchor, retain safe continued support, retreat the appropriate boundary locally around an obstruction using existing clipping/clearance, and retain the old shape only in that affected stretch where it exists. Outside old support, leave the unresolved component unclaimed. If a safe connected continuation cannot pass it, stop that end there; do not reject the rest of the row, its other end or other rows. Do not merge sparse conflicts into one first-to-last fallback span or import GEOM-04's full-height legacy interval machinery. No ownership relaxation, tiny-speck waiver or percentage-of-safe-ink rule. A joined two-row component is not a whole glyph to assign by majority.

Drop `material_band` from the candidate; use the existing M33 envelope and actual polygon consumers. Do not install an empty-grid guard around that rejected separator branch. No mesh/knot refit, M17 separator rebuild, experimental tessellation activation or new page model. Unsupported rows retain today's route. The old cap/veto and the new policy must not both run as independent decisions in the adopted population.

**Accept the supported-extent hardening, narrowly.** A now returns before recovery's fallback, so a theoretical overhang can escape `type_support_bounds`; the check found zero development occurrences. For A's newly retained local-unknown side, reuse `supported_extent` with that proposal's valid existing bounds before final support acceptance, then re-evaluate the existing body-chain contract on the clipped piece. Do not trim every ordinary proposal, infer new bounds or introduce a second extent formula. These admission bounds are not a permanent limit on later continuation with new native support. Commit an overhang fixture through the real call chain, in local and native frames, with a mutation bypassing the clip. Preserve the checked 8686 admission and controls. If clipping loses accepted true support, retain A unchanged and document the unresolved contract. Removing the redundant `here` filter is optional cleanup, not a physical-gain or speed claim.

### Targets, review and closure

Preset i3 target: src37's “ἐξόδων πη-” is complete in its own final crop; χο/μέ/ἀμέ whole end-component counts improve, with zero newly acquired other-row components. Count whole endings on all four positives. Aim for a majority of the same baseline 30 M33 rows on 8686 p5 to accept useful continuation, but that is a reach diagnostic, not a guard or substitute for complete final text. Freeze native witnesses first. Preserve A's body and existing R/B, 20 flat/skew negatives, both 8314 controls, 93f8 abstention and 9ea narrowing; no crashes on the three named controls.

Use the unchanged 41-page hashed cohort, then fresh 208 and paired timing bound to the retained source. Report intermediate M33 versus final compose masks, retained versus new text, local-retreat spans, foreign/unknown components, cuts, lost ink, duplicates and gaps per page. Known legacy overlap cannot be hidden or used as a whole-row veto again. New wrong-row text/cuts must be repaired or rejected. Keep the ≤100 ms affected-page incremental criterion against both fea451c and the pre-CURL 0b620be reference, including A's existing cost; global under-one-second debt remains open.

The coordinator alone evaluates a changed candidate on private44 against fea451c: **whole pages, every actual strip and actual-mask coverage maps for both versions**, changed and unchanged cases, all retained recovered rows, curved ends, loss/ownership/overlap/gaps and paired cost. No private inputs/images to worker/planner; repeatedly used44 is regression evaluation. Owner-exposed cases become development-retest. A runtime-identical result needs no redundant private rerun.

**Close after i3 regardless of outcome.** At least one complete formerly clipped end surviving final compose, controls and cost is a retained continuation gain; it is not automatically full CURL completion. Mark CURL complete only if the original shared-curl/continuation contract and required multi-page owner cases are actually met. Otherwise close PARTIAL with A and any independently qualified i3 subset retained. If no end meets the target, keep fea451c (or safe hardening/tests) and archive the withdrawn local-retreat experiment, exact first blockers and per-case ledger. No i4, no default promotion to satisfy the cap.

After the result/full check, Astra supplies **R8-RUST-02 i1** on the best checked compatible runtime. Rust owns stable-stage speed and retained continuation cost, not repair of an unqualified ownership algorithm. Unfinished curled ends/νων/mesh residuals become explicit CURL backlog; general crop floor/legacy overlap/reconcile stays geometry backlog; source uncertainty remains INK-02 debt. AUDIT-02 records every open witness, including incomplete bodies/ends and mutation gaps. Do not port withdrawn B/material_band or quietly move unresolved geometry into Rust. RUST (3) → INK (3) → AUDIT (1), with FONT's last slot parked; no later prompt prewritten.

Accounting: 16 used + 1 retired + 9 future (including parked FONT) = 26. Meter 12% reported, no 14 October daily cap; weekly 97% launch/99% run safeguards unchanged. Fallback scripts execute bare with optional read-only `--check`. Planner edits only docs and launches nothing.

## Repair the CURL consumers, preserve the mesh — FP8ah, 14 October

**CURL-03 i1 used one of three slots. Best checked head: `034bff94b0072d88f69cda4e88af112cd32bd5ba`; next is [CURL-03 i2](prompts/R8-CURL-03-i2.md), resuming Sol thread `01a13968-c97e-7191-8842-cb64b8b62789`, gpt-6.1-sol/high.** Runtime is byte-identical to0b620be; experimental `final_export=False`. The coordinator reports merge a86821b in ff-merged, with the same runtime. Start the worker from034bff9 plus this docs merge, not by resetting its branch.

The worker reported NOT DONE and retained no physical gain. The independent check accepts its evidence/tests with notes (bare archive357 passed,1 older skip,14 xfailed). No new private44 run was necessary because runtime is unchanged; the earlier GEOMi3 off-run remains the latest private default comparison. This is accepted evidence, not an accepted curvature repair.

**The diagnosis changes materially.** Native letter-bottom measurements show the existing M15 mesh predicts the curl: end residual medians about−6px on8686p5,0 onp7,−1.8 on4959p4,+2.3 on3229p5. Its path makes533/569 sampled end letters eligible, against199/569 for the capped tangent. These diagnostic samples use slow-reference association and are not final ownership ground truth. The last10–20px edge error is a possible later refinement, not the first blocker. The rejected envelope loop reused the last row's `shared` variable; fixing its scope restores p7/c8 parity. 9ea's remaining lost narrowing comes from replacing the in-anchor map path. The archived diff and its passing rejection test do not falsify shared continuation.

The real default loss is M33's whole-row overlap veto against other legacy straight polygons (27/30 rows on8686p5;17,144 offending pixels under adjacent-row boxes versus613 under same-row fragments), plus the box+6h domain that never reaches src37's last letters. The missing row is already discovered by the residual route. `verify_rule` correctly rejects a supposed rule made of five rows' curled letters; `type_barriers.protect` incorrectly drops the entire witnessed proposal. The native word is **χωρητικότητος**, correcting the older check/report's γεωργικότητος. The local fixture also mixes coordinate frames: its polygon is local, while both `type_support_bounds` and `type_witness_points` remain native. Version its adapter/metadata before extending the real-caller tests.

### Decisions on the checker's proposed i2 work

| Proposal | Decision |
|---|---|
| Unverified separator becomes local unknown; retain the witnessed side | **First, independently retainable repair.** Reuse `protect`, existing `clip_polygon`, witnesses and downstream `piece_support`; keep verified-rule, ink-beside-rule and short-crossing semantics. Test missing/balanced/ambiguous support and multiple nominations. The scratch result recovers the row body on8686 plus seven unchanged controls; it has not passed208. Do not call a nomination “not a rule” universally, or certify the remaining risen νων as recovered. |
| Fix shared scope, preserve in-anchor map path, extend only the continuation over finite field support | **Yes.** Store the continuation/phase per row. Keep the current in-anchor computation and9ea narrowing; bound the external path by the observed field and real finite rules, not box+6h or page margins. Reuse M15 evidence once; no mesh redesign or independent line refit. |
| Replace legacy-box overlap veto with field-phase ownership for supported rows | **Highest-value continuation experiment.** Replace the old decision in that population rather than add another vote. Use `invert_points` and current row/body witnesses on complete native components; preserve known neighbouring bodies/marks and local unknowns. A monotone mesh gives ordered virtual paths, not correct row identities or ink ownership by itself. The checker has not prototyped this decision; it must be judged on actual final strips. Unsupported rows keep the existing route. |
| Join same-row end fragments afterwards | **Secondary, only if needed for a demonstrated final-row gain.** Reuse `endpoint_pairs` as nomination, check shared phase and complete support, and retire only a fully subsumed redundant fragment. The current helper checks owned contacts and path distance; it does not itself implement a0.25h material-phase proof. Do not introduce that number as a new magic acceptance threshold. No global reconcile-priority change. |
| Refine the mesh boundary/knot spacing | **Defer out of i2.** The useful field already exists. If repaired consumers leave a measured final-letter residual, bind it for i3's decision; do not vary knots, smoothing or row phases before a real consumer uses the present prediction. |

The first fix may qualify while continuation remains partial. Keep that checked subset after a fresh208 comparison; do not discard it merely because i2's larger target is incomplete. Conversely, do not retain a harmful continuation merely to preserve a separator gain. Avoid a third renamed i1 variant: this repairs a demonstrated coding bug and replaces two falsified consumer assumptions, rather than fitting another curve or adding guards.

### I2 acceptance and review

Preset target: the missing row's witnessed body survives full compose, and src37's “ἐξόδων πη-” plus the checker-identified χο/μέ/ἀμέ endings are complete in their own final rows; bind those native components before editing. Check all four curl positives and every page in the unchanged **41-page** manifest, then all208. Preserve current20 flat/skew negatives, table/leader/noise controls and accepted R/B rows. Score recovered row body, remaining νων, main endings and fragment retirement separately. The seven-page unchanged scratch control result is not generalization.

Inspect each changed final crop and its neighbours. Mesh-phase eligibility, whole-component preservation and zero lost pixels are not equivalent to correct accent/row ownership. Quantify newly covered text, cuts, wrong-row ink, duplicates and gaps using frozen baseline domains; distinguish legacy wrong coverage revealed by a recovered row from a new wrong assignment. Never hide doubled ink or claim tessellation because virtual phase boundaries do not cross. General export notches/overlap and costly experimental tessellation remain closed-partial geometry debt; do not reactivate final_export.

The coordinator privately evaluates any retained runtime candidate: both baseline and candidate whole pages, every actual line strip and actual-mask coverage maps for all44, per-page text/ownership/missing/extra/overlap/gap/cost, including unchanged pages. No private inputs/images to planner/workers; repeated44 is regression evidence and disclosed pages are development-retest. Keep the existing paired timing/drift and≤100ms incremental gates, reporting inherited subsecond debt separately. No timing or quality relaxation.

Progress categories must distinguish (1) retained native crop gain, (2) experimental gain blocked downstream, (3) mechanism/test repair, and (4) diagnosis only. Ask the reviewer which previous counterexample now passes through the actual consumer and what the next iteration no longer needs to rediscover. I1 is converging on diagnosis; it has no physical gain.

CURL now1/3 used, i2 issued, i3 unwritten. Then RUST-02(3), INK-02(3), AUDIT-02(1); FONTlast1 parked, GEOM-04 CLOSED PARTIAL. At task maxima move on honestly from the best checked compatible head. Accounting15 used+1 retired+10 future(including parkedFONT)=26. Meter11% reported, no14October daily cap; weekly97% launch/99% run guards unchanged. Commit fallback scripts must execute with **no required flag**, since the runner calls them bare; optional `--check` may validate only. Planner edits documentation, launches nothing.

## Owner decision: continue with the remaining tasks — FP8ag, 14 October

Owner, verbatim:

> ok lets just normally continue with the rest of the tasks in the plan

**GEOM-04 is CLOSED PARTIAL at 3/3; next is CURL-03 i1.** The coordinator's subsequent request for GEOM-04 i4 conflicts with that direct instruction. Its new owner quotations identify curvature faults; they do not reopen the geometry allocation. This amendment therefore incorporates the check and supplies CURL's first prompt, not an i4 prompt. This is a sequencing decision, not a claim that smoothness, ownership or cost is finished. No slots are transferred or increased. FONT's last slot stays parked.

**Checked source: `0b620be070cf2a1f16e84a41089e9058d391cd4d`, with `final_export=False`.** The full independent i3 check accepts this head with notes. Default output remains identical to 9e8a196, including the previously retained R/B gains. Keep the literal export as an explicit experiment, not the accepted output or a prerequisite for CURL. This replaces the earlier FP8ag draft's pending-review status.

### What i3 established

The literal construction reaches the whole page and the four failed qualification gates are gone. Experimental doubled pixels fall about 71% on the frozen 12 pages, 70% on the 208 development pages and 80% on the coordinator's 44. On the private 44, median overlap share falls 4.7%→0.2%, duplicated ink 0.79%→0.06%, and ink in no line 2.13%→1.79%. The coordinator sees smooth shared seams on body text from actual crop masks, with local notches and heading tabs. This is real experimental progress; those aggregate figures do not establish every row's ownership or visual quality.

The experiment stays off. About 97.3% of remaining doubles and 99.2% of gaps on the 12 pages fall in legacy intervals; most restore the accepted export's existing overlap. True interlocks occupy 368 columns, but smoothing and first-to-last fallback expand that to 66,535 reverted columns. A scratch repair halves much of this residue but still adds cuts on c3cc. κατ’ is whole and unique on the experimental development witness; real final-export lower-row accents remain unmeasured. All 4,085 lost Otsu pixels lie outside the relative-ink mask, and inspected examples are background, but only 4 of 18 affected pages were viewed; do not certify them all as non-print.

Cost is not qualified: worker paired blocks are invalid. The coordinator's quiet private run has default corrections median 123 ms and experimental median 575 ms, paired +501 ms, maximum 34.5 s, 13 pages over 1 s. Profiled causes are repeated per-region faintness/paper estimation and scalar per-column path/sort work. Bare-archive tests: 352 passed, 1 older skip, 13 xfailed. Crossing-constraint averaging, removal of the under-1-pixel tie rule and removal of rule protection still have no discriminating mutation test.

### Disposition of every proposed i4 repair

| Finding / proposal | Planner decision and owner |
|---|---|
| Narrow smoothing-induced infeasibility to true interlock runs; avoid full-height fallback | Agree with the diagnosis. Keep as **unfunded geometry-export backlog**, with `tree_fixA` and c3cc's remaining pixel/cut counterexample. A per-component notch must preserve the right row and its neighbour; an entire touching two-row component is not one letter. No hidden i4 in CURL. |
| Replace legacy-box restoration and row-wide content-refresh refusal with component-local decisions | Agree in principle; no blanket permission to admit outside ink. General exception/reconcile replacement remains geometry backlog. CURL owns only the outside components needed for its continued rows, using the existing source/exclusion decisions once. INK-02 owns the underlying source/photometry contract debt; it does not inherit general export repair. |
| Clip gutter/end support using existing finite column/rule evidence | Agree; existing rule y ranges must be honoured. General final-export clipping remains geometry backlog. CURL must consume these boundaries correctly for its own paths, without a new gutter detector or full-height median-x cut. |
| Give components of mixed two-row boxes to existing single-row neighbours | Plausible only where existing row identities and native evidence support it; nearest distance alone is not a certificate. General mixed-row/reconcile work remains geometry backlog, including a73d item54. Do not widen CURL to all row splitting. |
| Vectorise repeated path/key work; reuse compatible paper observations; avoid repeated mask work | Hand exact-work evidence to **RUST-02**, with stable default stages first. The experimental branch may receive an isolated exact rewrite if still useful, but must not become the accepted port target by default. Prove image/ROI/scale/kernel/threshold and membership contracts; a regional paper estimate is not automatically the same as a page estimate. No new memoization layer or silently relaxed cost gate. The reviewer's 300–500 ms forecast is not an approved target or measurement. |
| Add the three missing mutations; measure real final accents | The next task touching the relevant decision must protect it; otherwise **AUDIT-02** records the holes. CURL adds tests for its own actual field/continuation consumer and checks the 22 FONT cases if their support changes. No claim that synthetic or proposal-only attribution validates final exports. |
| 8686 risen endings and text outside boxes | **CURL-03 now**, across the full curl cohort. Full-page evidence, shared page/column bend, native whole-component continuation and a representation capable of steep turns. Do not repeat the failed unclaimed-component window tracker or merely loosen the slope cap. |
| 8686 wholly missing row | **CURL-03 owns a separate, bounded discovery trace in i1**, through existing field proposals/replacement and residual recovery. Determine the first lost native row and whether it is the earlier row-5 witness. A continuation cannot conjure a seedless row. Repair only an identified existing discovery/admission contract within CURL's three slots when the check supports it; otherwise close that exact discovery dependency partial and pass it to AUDIT's open ledger. This does not fund a new detector or reopen general geometry. |

The inside/outside distinction is now measured: on 12 pages, inside-box duplicated ink falls 57% and cut components 74%; outside boxes only 5.2% of text-sized ink is reached and 68% of remaining cuts straddle a box edge. On 8686 p5, about 78k pixels of text-sized ink are outside all accepted boxes; 1.4% is reached, with 53% of that outside ink at the risen ends. These size-derived counts are diagnostic populations, not front-text truth. A whole missing row and uncovered starts are distinct from curl. The check falsifies a simple window tracker (7,940 noise components on 74cd) and shows that a fixed x-monotone export slope cap cannot express the steep turn. The original slow pixel-seeded construction already follows many of these endings; use it as an explicit comparison and source of mechanisms, not ground truth or runtime replacement.

### Remaining order and launch loop

| Order | Task | Remaining maximum | Start / scope |
|---|---|---:|---|
| 1 | R8-CURL-03 | 3 | Fresh Sol 6.1/high, ff8-stack, from checked 0b620be plus these docs. Shared edge curl and supported continuation; bounded missing-row trace. [Iteration 1 prompt](prompts/R8-CURL-03-i1.md). |
| 2 | R8-RUST-02 | 3 | Best checked compatible CURL head. Stable-stage speed/port work and explicit experimental cost debt; no geometry-quality promotion. |
| 3 | R8-INK-02 | 3 | Best checked compatible speed head. Existing source/frame/photometry observations, deletion and required invalidation. |
| 4 | R8-AUDIT-02 | 1 | Checked final head, honest final feature/owner/speed ledger including the unfinished geometry and discovery cases. |
| Parked | R8-FONT-03 | 1 reserved | No automatic restart or full-font prerequisite; retain its evidence and revisit only for a demonstrated consumer need. |

After each worker result and full independent check, Astra writes the next exact prompt; the coordinator checks the four launch criteria and launches unchanged except header/placeholders. At each maximum, close honestly and advance from the best checked compatible route even if partial. Do not prewrite later iterations or silently absorb all earlier failures into the next task. All implementation is sequential in the shared stack worktree; fresh Sol feature threads, resume within a task.

The coordinator alone runs private44. For every frozen changed candidate show **baseline and candidate whole-page segmentation, every actual line strip and coverage maps**, including unchanged pages, missing/extra/sliver items, finite column ends and curved ends. Compare default and any experimental route explicitly; no enclosing-polygon substitute for `crop_mask`. Record per-page text/ownership/cuts, gaps/doubles and paired cost with detector load control. These repeatedly used pages are a regression evaluation, not fresh untouched generalization; any owner-exposed page becomes development-retest. Workers and planner never inspect private inputs or images.

Accounting: 14 worker iterations used, 1 earlier Rust slot retired, 11 future slots including parked FONT, total 26. Meter 10% reported by coordinator, not independently polled; no 14 October daily cap. Existing weekly 97% launch / 99% run safeguards and stop signal remain. Planner edits docs only and launches nothing.

## Literal construction with local exceptions — FP8af, 14 October

I2 retains better tests, a real final caller and reusable native/raster/identity plumbing. Default output is identical to 9e8a196. Committed suite 344/13; bare archive 343 passed, 1 older skip, 13 xfailed. I1's R gain is now protected. The experimental route changes 491 crops on 156 pages, but 438 are isolated rows; only 32 of 3,583 nominated pairs are adopted and doubled pixels fall 0.13%. Neither required column nor κατ’ is solved.

**Private 44:** default-off is identical on 44/44. Experimental-on changes 37 pages/120 items; doubled pixels 14.56 M→14.53 M (−0.24%), median overlap about 4.8% and duplicated ink 0.83% unchanged. Coordinator inspection finds wavy, tight letter outlines. Median corrections 148→237 ms; paired +110 ms and detector +27 ms were measured under concurrent checker load, so are descriptive, not qualified. Worker paired blocks are all invalid; default-off 278→297 ms also needs measurement before neutrality is claimed.

**The approach, including my earlier prompt, is the blocker.** In `geometry_final_support.observe`, every-anchor fit and any-contested-component gates refuse roughly 94% of items before bands exist. Connected-group fallback then spreads a one-pixel refusal through a 4959 chain. FP8af removes those gates and that fallback policy. The owner's construction must be measured before qualifications are added.

The independent diagnostic gives concrete evidence: on the same 12 pages, literal centre paths, nearest row-path component ownership and shared smoothed middle lines reduce doubled pixels 8,257,000→378,374 (about 95%), doubled Otsu ink 534,622→46,034 (about 91%) and pair-domain gaps 3,759,119→1,307. It is not qualified runtime: 246 lost Otsu pixels, some new interlock cuts, gutter/initial errors and FONT accents untested. The foreign-ink metric uses its own owners and some diagnostics use first-claim masks; actual final-export evaluation must be independent of those shortcuts.

Owner, verbatim:

> Our goal now is smooth clear lines for segmentation, without overlap. If the lines are tight as normal on the page, the segments should then tesselate the plane

**Decision:** replace i2's experimental `tessellate` algorithm in its existing post-frame slot with the literal construction. Reuse current robust fitting, ink preparation, seam filters, half-open masks and callers. First save the unrepaired real-caller 12-page table; then handle five exception classes locally: same-row/mixed items, finite gutter/rule/end support, interlocking components, existing non-text/oversized support, close detached marks checked on all 22 FONT cases. No new detector/model; no second live engine. A failed interval retains legacy coverage only there, on both shared sides with correct joins, never a whole row chain. Whole-component assignment is not proof of correct ownership when one component contains letters from two rows.

**Content and export shape:** unchanged owned components/provenance keep their source/motif/frame decisions; paper-padding changes update export identity without repeated content inference. Replace unconditional `refresh_export` (168 ms of motif work on 44b5). Real content/calibration changes refresh only their affected existing dependency once; exclusions remain respected. This explicitly supersedes FP8ae's broad changed-mask refresh, while preserving actual input contracts rather than asserting that arbitrary ROIs are equal.

[GEOM-04 i3](prompts/R8-GEOM-04-i3.md) keeps the 12-book sample, 42 GEOM/22 FONT/full owner controls, and compares accepted, i2-on, unrepaired literal and repaired candidate per page. Fixed-domain gaps, all-item doubled pixels/ink, cuts, lost/foreign ink and local legacy extent are reported separately; no hidden population or display ownership. Then fresh 208 and coordinator-only 44, with **every whole page, every actual strip and coverage map in both versions**. Smooth bands and physical text are judged by eye as well as counts. Revised-on remains explicit/default-off for frozen independent review; no promotion of the current i2 experiment.

I3 is one additional authorised iteration, not a new completion cap. GEOM-04 now 3 allocated/2 used; 13 worker iterations used overall, 1 retired Rust slot, 12 bounded future slots, total 26. FP8ae's 3–6 forecast included i2; arithmetic remainder 2–5 is conditional, not revalidated merely by spending that iteration. Update from the literal integration result. FONT last 1/CURL 3 remain conditional; genuine geometry dependencies stay open before Rust/ink/audit. No later prompt prewritten.

Meter 8% reported; no 14 October daily cap. Existing weekly 97% launch/99% run guards and stop signal remain. The planner edits docs only and launches nothing.

## Whole-page final export after the first shared pair — FP8ae, 14 October

I1 proved the construction but exposed a scope error in the first prompt. Accepted 9e8a196 changes only four R polygons on 4959 p5. Rows 107/105 are smooth, whole and exactly tiled; outer domains retain 61/384 gaps and 3229 B remains unchanged. Half-open masks are wired into real consumers. The committed suite is 323 passed / 11 xfails, not 332: nine physical tests are ignored and depend on 4.3 GB captures. I2 must bring small real gain-protecting tests into the repository.

**Held-out result:** coordinator baseline 3e92e98 versus 9e8a196 is identical 44/44, no migrated items; correction median 123 ms, max 1807 ms, 6 over 1 s, paired +0.5 ms. Forty of 44 pages still have pixels claimed by multiple lines (21/22 s2, median about 4.8%). The independent 12-book sample attributes roughly 94% of doubled pixels to Paddle/clipped/field combinations. More R-only qualification cannot meet the owner's whole-page contract.

Owner, verbatim:

> Our goal now is smooth clear lines for segmentation, without overlap. If the lines are tight as normal on the page, the segments should then tesselate the plane

> I want to see whole page segmentation, and teh lines it produces.

**Design decision:** adopt one final `geometry_bands.tessellate` authority after `frame_exclude` at compose's final-item boundary, using existing row hypotheses and observations. Every ordinary origin is considered. Replace redundant upstream smoothing/final overlapping extent work in adopted populations; no second page detector or competing vote. Supported component ownership must distinguish genuine row ink from current duplicated mask claims, then produce smooth bands and shared boundaries. The two corrections to the checker's sketch are explicit: nearest-body alone cannot own ambiguous accents; unchanged component IDs do not preserve mask/ROI-sensitive faintness/frame inputs. Reuse identical decisions and refresh affected existing decisions transactionally, with current footprint/raster identity.

**Outer edges:** allow one-sided clearance against non-owned ink without requiring a fully qualified outer neighbour; keep true column/rule/exclusion barriers and inner shared edges. It is outer avoidance, not evidence of two-sided tessellation. **Κατ’:** permit whole-component closure where existing finite row/word support gives one owner and no competing row/source claim. Otherwise exclude whole or keep unresolved; no partial mark, no blanket adoption of every unowned speck, no new font model.

[The i2 prompt](prompts/R8-GEOM-04-i2.md) freezes 12 development books, all final ordinary-row pairs/domains/exclusions, 42 GEOM cases and 22 FONT controls, with fresh 208 all-item overlap/ink/gap census. Primary whole-column targets are 4959 p5 right and 44b5 p1. Rows 22/103 must cease sharing text without losing either row. Preserve R/B, qualify the 3229 apostrophe through the final consumer and report clipped/field reach on a73d p47/c3cc. All unresolved/excluded items remain in all-page metrics; no favourable denominator changes.

Coordinator-private evaluation is baseline 9e8a196/candidate, **every page, every strip, plus coverage maps** with real half-open masks, native detail and stable mapping. Inspect physical text and source preservation as well as gaps/multiple claims. Repeated 44 is regression evidence, not fresh untouched data; disclosed cases become development-retest. No private inputs/images go to planner/workers.

The first experiment supports a low-confidence **3–6 further implementation-iteration estimate including i2** for the wider geometry gate: 1–2 for final export/owner integration, 1–2 for remaining marks/straddlers, 1–3 for finite-domain/missing-row causes, with overlapping work. Export alone may take 1–2; discovery/domain failures could exceed 6. This is a forecast, not permission or a cap. Only the requested i2 is newly allocated; further prompts follow result/full check/private evaluation. FONT's last 1 and CURL's 3 remain conditional, not mandatory subsystems. General geometry prerequisites remain open before Rust/ink/audit.

Allocation accounting: 12 used, 1 earlier retired Rust slot, 12 future slots including i2, total 25. GEOM-04 now has two allocated iterations, one used; full completion budget is unset. Coordinator meter 7%. The 13 October daily 17/20 limits expired; no daily cap exists today. Existing weekly 97% launch refusal/99% guard and stop signal remain. This planner changes docs only and launches nothing.

## Smooth exports and shared text-region separators — FP8ad, 13 October

This finalises the pending FP8ac replan. The independent FONT i2 check accepts the source and finds 11 correct experimental mark owners across seven pages/four books, real experimental crop/row gains, and an in-scope adapter input defect: feeding only bodies starves the detached-accent class. The three λ fused-neck xfails remain real slow-code defects. Runtime remains unchanged; no new font consumer or measured speed gain. Export defects are the ρ-tip/rule pixels and four new duplicate-clipped slivers, alongside 19 inherited small slivers. Preserve the write-once native fixture and add dated report corrections in the worker task.

Owner, verbatim:

> Our goal now is smooth clear lines for segmentation, without overlap. If the lines are tight as normal on the page, the segments should then tesselate the plane

The contract is one smooth band per qualified row and a shared finite separator for each normal close neighbour pair, with no gaps/overlap in their text region and one raster ownership convention. It is not a request to cover gutters, paragraph whitespace or illustrations. Both final neighbours must consume the seam; independent child clipping is insufficient. Reuse `_boundaries` as explicit reference and the fast envelope/corridor construction, replacing `raster_envelope` at R/B callers with compatible support. Preserve selection; qualify native vector exports only where their existing full membership supports it. No new font pipeline, row model or extra output checker.

The first-trial target is the five retained R/B rows plus at least one real final shared-separator pair. Full geometry remains open. Freeze all42 existing cases, the22 FONT census and naturally reached export calls/pairs on their page union with the layout/negative controls. Review every changed208 final crop. Coordinator evaluation now presents **whole-page segmentation and every produced line strip on every private44 page, baseline and frozen candidate**, including unchanged cases, missing/extra/sliver items and gap/overlap coverage. Private inputs/images remain coordinator-only; disclosed cases become exposed development-retest.

**FONT ordering decision:** accept export first and reserve the last existing FONT slot for the demonstrated adapter-input/mark-consumer repair after export qualification **if attribution failures remain**. Do not launch it automatically or build a comprehensive separate subsystem. If tested segmentation works without FONT/CURL, retire redundant work with evidence. If export stays blocked, do not burn the FONT slot on the same downstream failure. A needed measured-mark consumer is a dependency inside the open geometry phase, not a way to offload final crop/reconcile debt. GEOM-04 retains a73d non-field item54 and the 3229 upper/omitted-mark prerequisites; the check's older CURL assignment is superseded.

GEOM-04 has one first-trial slot, fresh thread, checked3e92e98 plus this docs merge. After result/full independent check and coordinator-held evaluation, Astra estimates the remaining geometry work by mechanism and writes the next exact prompt. No GEOM04 i2/FONT i3 is prewritten. Used allocations remain11 worker iterations,1 earlier retired Rust slot,12 bounded future slots including the one conditional FONT slot and one GEOM trial (total24); full geometry completion allocation remains undetermined. Meter5% reported; daily launch17%/kill20% and owner20% cap unchanged. Planner edits docs, launches nothing.

## Geometry first, with one segmentation construction — FP8ac, 13 October

Historical FP8ac draft, finalised by FP8ad above: its pending-check state is now resolved.

The owner says: “But the whole point of this generation of our model was so that we odnt have to have duplicate checks” and “ok lets start by geometry which seems to be in itself quite more comprehensive than we had initially supposed if we also delivery my idea”. These override FP8ab's FONT-first gate.

**GEOM-04 is next after the completed FONT i2 result is independently checked and the input head selected.** A finished font provider is not a prerequisite. Preserve useful tests and offline witnesses from i2, park FONT i3 and do not relaunch the completed worker. The worker report at 3e92e98 is not yet an independently accepted result.

The [geometry-first plan](FONT_GEOMETRY_REPLAN.md) binds the architectural target: share prepared observations under compatible contracts; one row/component ownership decision; one finite row-path representation; one final smooth-band/shared-separator construction. Font and curl evidence inform those same decisions only when qualified and useful. Every adoption identifies the old decision, migrated caller and deleted work. A new helper, extra vote or chained correction is not consolidation.

First test the owner's smoother boundaries and shared middle separators on known-correct memberships, then the wider development sample and coordinator-held pages. Do not demand a comprehensive font model first or widen a crop across unresolved neighbouring text. Use the initial trial's reviewed failures to estimate the actual geometry completion allocation. Required membership, column/domain, final reconcile and missing-row dependencies remain geometry's responsibility. CURL is a possible shared-continuation dependency, not a place to move unfinished crop work.

Existing task usage is not reset. FONT's unused final slot is parked and not transferred. GEOM-04 retains the planned single first trial; completion iterations follow its independent/held-out evidence. Later feature work does not advance past an unfinished prerequisite or become mandatory if geometry already supplies its function. No implementation, held-out access or worker launch occurs in this planning pass.

## Restore FONT, then return to geometry — FP8ab, 13 October

Historical draft, superseded by FP8ac above. Its FONT-first entry gate is no longer active.

[FONT_GEOMETRY_REPLAN.md](FONT_GEOMETRY_REPLAN.md) defines the original FONT deliverable for discussion: body height, four main font guides plus accent bounds, valid class/row contacts, measured/borrowed/unknown provenance and a real replacement consumer. FONT i1 was geometry follow-up and verification, not a font provider. Preserve the current i2 work and judge its result against that contract; future FONT work must not become another crop/reconcile repair.

After FONT qualifies, **R8-GEOM-04** returns explicitly to the owner's smooth, broader crop bands and shared middle separators. One first implementation/evaluation iteration is planned; the coordinator tests its frozen candidate on the private 44 as well as the worker's development evidence. Astra then estimates the remaining iterations by actual failure mechanism and proposes the completion allocation. No arbitrary new three-iteration geometry cap or success claim is set now.

General final extent, row/column domains, missing-row/admission and competing-crop reconciliation move back to geometry, including a73d non-field item 54 and 3229's upper child/omitted apostrophe. CURL owns shared edge bend and supported continuation only. If that module proves necessary for a required geometry case, build it while geometry remains open and requalify the result. Otherwise it follows the base geometry gate as an optional refinement. Rust and later work wait for their actual semantic dependencies.

**Spending limits no longer imply advancement past an unresolved prerequisite.** FONT's existing cap is unchanged pending its check; a needed extension must be stated explicitly. GEOM-04 has one bounded first trial, not a complete-phase budget. Its completion allowance is determined after the trial/check/private evaluation. Existing CURL/RUST/INK/AUDIT caps and daily 17%/20% guards remain. Full completion cost is therefore not yet allocated. Historical closed tasks and used iterations are not reset or relabelled.

The new replan supersedes FP8aa's placement of general crop construction/reconciliation in CURL and FP8z's automatic FONT-to-CURL transition. It preserves the original cohort/gate and all issued prompts as historical receipts. No worker interruption, code changes, processing, held-out access or launches occur here.

## Curvature after detection; smooth final crops — FP8aa, 13 October

Historical draft. FP8ac retains the crop/module ideas but supersedes this section's task order and assignment of general geometry debt to CURL.

The owner proposes an independently testable module after detection, without declaring segmentation finished:

> we can try to develop as a module after the detection if that makes sense,
>
> and so we dont have to accept that line segmentation is finished; although it might be

The preceding crop-shape direction was:

> (1) create a smooth line around the selected letters, by broading a little the boundary around the central line of the text
>
> (2) make sure there is no overlap with other lines by finding the middle line

**Logical order: initial text/row detection → optional shared curvature refinement → smooth crop construction and final validation.** This is a module boundary inside the existing stack, not a new detector or an instruction to reorder every existing stage. The curvature module receives the full page and current row observations with their finite reliable spans, column boundaries, component support and uncertainty. It can use reliable portions of incomplete detections; perfect row/mark ownership and completed line segmentation are not entry conditions. Tight crop images alone are insufficient because the module must examine the missing endings outside them.

CURL-03 continues to own the shared page/column bend, onset and supported continuation, using existing field/envelope callers. Character/font observations measure and check the paths; they do not independently refit a rival curvature model for every row. Return evidenced curl, evidenced no-curl or insufficient support. A known-correct row needs no additional correction. The module must not invent evidence for a seedless row or reassign an ambiguous accent merely because its predicted curve is nearby. Native evidence still validates any newly proposed support.

**Final crop shape is separate from exact component membership.** For already qualified rows, replace the exported letter-tracing outline with a smooth band along the row, containing the complete selected letters, accents and descenders plus a modest paper margin. Reuse the exact component mask for verification, not as a requirement that the visible edge track every pixel column. Construct one shared separator through the gap between adjacent occupied text bands; move from the midpoint only as required to preserve their complete ink. Both crops use that separator and one explicit raster-boundary convention. Respect columns, rules, forbidden regions and finite support; do not obtain smoothness by clipping owned ink or adding neighbouring text. An unresolved ownership conflict remains a distinct problem, not a reason to reject a smooth crop where ownership is already valid. Start verification with the retained 3229 p2 row, then the existing multi-book cohort.

Test the module off/on from **identical initial detections**, then run all downstream geometry-dependent decisions on the resulting rows. Report its incremental recovered text, wrong inclusions, non-overlap, flat/skewed negative behaviour and cost. Report base row detection, curvature continuation and crop-shape quality separately. If initial segmentation already passes a population's physical contract, call that population complete and make curvature a no-op there. If the module adds no benefit on the intended curl cases, reconsider or remove it rather than preserving it as a mandatory layer.

This clarification changes the target and responsibility boundaries, not the current checked results. R8-FONT-03 i2 remains unchanged; no worker is interrupted and no later iteration prompt is prewritten. CURL keeps its existing three-iteration cap and inherited field/non-field reconciliation debt; smoothing is part of final extent construction, not another funded task. Astra will bind the next exact prompt to the next result and independent check. No runtime edits or processing are performed here.

## Measured guides must decide the mark's row — FP8z, 13 October

Best checked head **56afb02**, FONT-03 i1 PARTIAL, ACCEPT WITH NOTES. Runtime remains byte-identical to aa6d3d4. Retained progress is verification: returned-polygon assertions now make the vector-return mutation fail 14 tests, the omitted κατ’ apostrophe has a strict physical xfail and a real final-reconciler preservation test, and the offline row renderer disables unqualified completion. Suite 314 passed/8 xfailed. No new default crop, font-guide consumer or runtime cost was retained; no private 44 rerun was needed.

**The planner's and i1 experiment's attribution premise was wrong.** Mark 147 is the grave on lower row D's “νὰ”, track 3/body 77. The native nearest-box rule chose upper row C's χρ descender (body 56, 6.8 px) over the lower α (10.2 px); `best + .08h` excluded the true owner by about 0.5 px. “Unique candidate” did not establish physical ownership. The old FP8y description of a73d's unique attachment records an algorithmic observation, not a valid own-row accent. Correct the report/input contract/hand-off/test wording with dated source-bound addenda. The first failure is attribution; reconciliation is a second independent failure.

I1's dense side-constrained refinement is useful reusable machinery: native's own `.25h` clearance, other callers' `.2h` preserved, correct final polyline instead of coarse resampling. It was fed the wrong side. Correct attribution alone still leaves 6 accent pixels clipped on the coarse export, so i2 must validate/refine every newly admitted valley with nearby marks, including formerly non-crossing ones.

**The wider sample supports a real FONT target.** There are 22 mark-only candidate valleys on 12 pages: one wrong a73d admission,20 identity refusals and one b9d6 component crossing. In 19 of the 20, candidate bodies belong to both bounding rows. Native review shows the same lower-row-accent/upper-descender ambiguity on c3cc census 14 mark 159 and 44b5 census 17 mark 95. Specks on 3229 p4 and 4959 p5 must remain protective unknowns. Baseline/meanline and mark-class evidence can address this recurring pattern; a geometric gap alone is not enough to classify noise as an accent.

### FONT i2 scope and default retention decision

[Iteration 2](prompts/R8-FONT-03-i2.md) resumes Sol thread 01a13620-6408-72c0-b3c6-b1fc5c8d47b9, high, on 56afb02 plus FP8z docs. Use native's same-call bodies/labels/transform to supply measured per-track baseline/meanline and supported mark bands at `geometry_rows.native` attachment construction. Reuse existing `font.evidence/fit_guides` and contact calculations with compatible row/class inputs; do not call density tracks baselines or line-height proxies x-height. Hold disputed marks out of fitting, expose actual contacts and borrowed guides, and leave unresolved class evidence unknown. Replace the decision, not merely add an unused guide plot.

Prove correct native ownership on a73d/c3cc/44b5 and keep speck/ambiguous/body-crossing controls. For the **first live migration use the existing cross-row-ambiguous attachment branch**, re-scoring all 20 refusals and all naturally reached calls. This is a semantic population already present in the caller, not a good-page whitelist. Corrected a73d native attribution remains a mandatory experimental witness; its unique legacy branch need not be published while its independent final consumer is blocked. A shared measured-guide consumer can be retained on a safe existing branch with real physical/decision evidence even if a73d still fails. State exactly which legacy population remains unconverted.

No runtime promotion may worsen final crops. If the existing branch cannot be separated without new ad hoc selectors or final regressions, retain tests/evidence and withdraw that candidate. Do not freeze wrong labels, install an unused provider, keep rival votes or add a new reconciliation guard to claim progress. Default guide/decision gains, final-crop gains and experimental ownership corrections are separate result columns. Preserve four R rows and the 3229 lower B row. FONT i3 remains unwritten and the task-level measured-guide consumer/deletion contract remains unchanged.

### CURL owns non-field straddling reconciliation too

**CURL-03 owns `stack_ownership._pass` selection against both field-owned and non-field straddling items.** A73d item 54 is a four-vertex “verified separator clip” at y903–978, **not** a page_field item. It straddles C and D. After the 80%-shared-ink nomination, the smaller-ink new D child is retired and this larger mixed-row rectangle wins, regardless of which side owns the accent. I1 reproduced shared ink 1047→3290 px and 22 newly partial components. FONT must freeze this actual pair/physical failure for CURL and leave priority unchanged. CURL's future replacement must distinguish genuine single-row support, rather than globally prefer every new child.

The 3229 upper field-owned crop and κατ’ omission remain CURL prerequisites: account for unassigned outside-parent marks before preferring B upper children; the returned-output mutation tests are now fixed. This expands the explicit **ownership of the debt**, not CURL's 3-slot cap or a general reconciliation rewrite. Any unresolved portion remains named in AUDIT's backlog.

Reuse GEOM03_COHORT byte-for-byte (42 cases), plus freeze/hash all 20 identity refusals and the other two census cases. 44b5 is part of the existing 208, not new validation. Preserve development-retest labels and full owner ledgers. Test all 20 through the final caller, including safe unknowns, before claiming wider success. Do not compare the 208 median 187–195 ms with the private 44's 120 ms as a slowdown; these are different populations. I1 retained 0 ms new runtime work.

Order/caps stay FONT(2 remaining) → CURL 3 → RUST 3 → INK 3 → AUDIT 1. Twelve future slots, ten used, one retired; ceiling 23 unchanged. Reported meter 4%, launch stop 17%/kill 20%, owner cap 20%; no reset/bypass. After each result/full check Astra writes the next exact prompt. This is documentation-only, with no code edits, processing or launches.

## Geometry closed partial; font attribution begins — FP8y, 13 October

**GEOM-03 is CLOSED PARTIAL at 3/3**, best independently checked head **aa6d3d4**, ACCEPT WITH NOTES. Retain the four whole right rows on 4959 p5 and the new lower-row B gain on 3229 p2 mark 5. The latter preserves 57 native members and excludes 25 following-row components from its crop; the removed ink is covered by other final rows. Fresh 208 changes one polygon versus d468a9f. This is a real second consumer and positive book, not a completed owner group. The upper child still loses to the existing field-owned crop. No row/bend authority count decreased; the architectural result is a conditional replacement of final vector extent with shared native evidence, with substantial added code.

The full frozen gate remains unmet. R-right is retained; B is converging with a second-book gain; R-left, A admission/trim, F domains and M missing-row admission remain open. A fresh recheck of 17 captured partitions found no further narrow B retention: remaining causes are row count, component identity, horizontal truncation and field-owned final reconciliation. This closure ends the geometry allocation, not the unresolved physical questions.

Independent cost: 3229 p2 +51.0/+43.3 ms against the original reference, within 100 ms. 4959 p5 +2.0/−6.8 ms versus retained R is noise; its combined page excess is inherited. Five timing generations correspond to five actual source revisions and all passed the positive-page gate, not rerun-until-pass. Coordinator private 44 remains 44/44 polygon-identical to r7, corrections median 120 ms/max 1792 ms, 7 over 1 s, paired−0.7 ms versus detector−1.4 ms. Global speed remains incomplete.

**Correct the claims that the review disproved.** The vector-slice mutation passed the suite: the tests inspected receipts/old pieces, not returned polygons. The returned geometry is physically better, but those tests do not prove it. The proposed upper B child silently omits its own “κατ’” apostrophe (component 32, outside the parent but not at the strip edge and beyond existing attachment reach). Default output retains it through the field crop. The field crop has five neighbouring sliver components, about 26 ink pixels, plus that correctly retained apostrophe; final upper/lower hulls share14 ink pixels. Do not call all six components foreign, both children complete or final ownership duplicate-free. The checked suite is 310 passed/7 xfailed, with this known blind spot.

### Debt ownership after geometry

| Debt | Accountable later task | Required boundary |
|---|---|---|
| Returned-polygon mutation and phase assertions (review note 1) | **FONT-03 i1 now** | Small direct physical assertions on actual outputs; restoring the old vector pieces must fail. No runtime rollback. |
| Silent outside-parent apostrophe omission (note 2) | **CURL-03 before any B preference/extent change**; earlier toucher must resolve it first | FONT i1 pins a strict real-caller xfail and passing final-preservation check. No broad distance increase, global B withdrawal or unsupported clean-child claim. Any newly reached consumer must conserve native ink. AUDIT verifies it stays visible if unresolved. |
| Mark 5 upper field-owned extent and reconcile priority | **CURL-03** | Accept the checker's reassignment: field-domain/continuation task owns this witness. Note2 and returned-output tests are prerequisites before preferring B, not permission to globally reverse priority. |
| a73d accent-bridge valley veto; row/class identity; R-left axes; A/M observations | **FONT-03**, within its measured-guide contract | i1 revalidates a uniquely attached accent on native ink. Ambiguous marks/body crossings stay protective. Broader admission/identity debts remain explicit unless a real consumer reaches them. |
| 3229 m7/m8 box truncation; c8/e259 finite domains; 8686 curled ends | **CURL-03** | Existing shared field/continuation with proper finite support; no new generic gutter model. Missing-row admission is separately tracked. |
| 4959 page cost/headroom and slow pages, including 0ce9 | **RUST-02** | Port current qualified semantics; preserve physical gains. Faster code alone does not solve the one-body identity blockers. |
| Source/forbidden/B5/M35 refresh and M55/DN/faint-front debt | **INK-02** | Changed polygons require current source evidence. No geometry fallback certifies non-front ink. |
| All remaining targets, exposed-validation labels, report/receipt discrepancies and final contract/cost | **AUDIT-02** | Audit verifies real progress and open debt; it is not an extra repair slot. |

### FONT-03 first launch and the unchanged loop

The owner direction stands: “Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample”. Use a **fresh Sol 6.1/high thread**, track ff8-stack, stack worktree/branch, from aa6d3d4 plus FP8y docs. [FONT-03 i1](prompts/R8-FONT-03-i1.md) replaces a coarse mark-only valley veto in `geometry_rows.native` with existing native corridor refinement and complete revalidation, using the same call's labels, body/track/bridge evidence and transform. Native 13 on a73d has one uniquely attached accent blocking valley[0, 3]; mark 81 ambiguity and native 14's real body crossings remain negative controls. Check the actually exported path, not a dense internal path that is discarded by later sampling.

The intended gain is another correct separation on a third book. It can still leave vector-sliced crops and one multirow child. This is a **FONT attribution prerequisite**, not a measured four-font-line provider and not full FONT completion. The task's three-slot contract still requires correct row/class evidence feeding measured or explicitly borrowed guides in a real consumer and removal of the displaced policy. I1 produces a concise source-bound input-contract receipt for those existing tools; the next exact step depends on its result and check. Do not silently spend all three font slots on unrelated geometry repairs.

Reuse **GEOM03_COHORT.json unchanged**: all 42 per-case outcomes across the fixed books/layouts, plus every actual mark-only refusal reached in 208. Preserve the first validation receipts; subsequent use is development-retest. Count positive native changes separately from unchanged pages. Correct the natural-partition failure labels where multiple rows per child precede an identity short-circuit. Preserve R and the 3229 lower final B hull and all named negative controls.

Order remains **FONT-03 → CURL-03 → RUST-02 → INK-02**, maximum 3 each, then **AUDIT-02**, maximum 1. Thirteen future slots, nine used, one retired, total ceiling 23 unchanged. Each starts from its best checked predecessor, even if partial. Every result plus full independent check returns to Astra for the next prompt; FONT i2 is unwritten. No second geometry allocation or parallel edits to shared callers.

Reported meter 4%, about one point for the last iteration; owner cap 20%, launch stop 17%, kill 20%. Checkpoint before 20; no reset/bypass or assumption all remaining slots fit today. This planning update edits documentation only and launches nothing.

## Retained geometry and the final wider-sample iteration — FP8x, 13 October

The owner says, verbatim: “Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample”. **There is now retained physical progress.** GEOM-03 i2 is PARTIAL, independently ACCEPT WITH NOTES, at **d468a9f**. Four right-column rows on 4959 p5 are whole by default, including their descenders/marks and excluding the rule bar. Both genuine windows give identical hulls; 26/26 raster cases and six mutations pass. The fresh 208 changes exactly those four polygons. 35 metadata-only differences are on 11 pages, not 10. Coordinator private 44 remains polygon-identical to r7; 128 ms median/1915 ms maximum, 7 pages over 1 s, paired+5.2 ms with detector+3.5 ms is noise. These are measured local gains, not completion of the frozen geometry gate.

Independent request medians 83.0/99.8/95.1/91.2 ms meet the 100 ms bound with almost no margin in one order; natural worst 89.3/89.9. R already adds about 119/125 ms to the 4959 page across requests. R's gate is per request; B's is per affected page including R, so do not buy a B pass there by subtracting R or subdividing the page. The next B positive is 3229 p2, which has no R work. I3 uses repeated unchanged references from **both orders**, correcting the single-forward-reference bias. Bounds remain unchanged.

**B's next step is evidenced, not another broad rebuild.** The native-3 fixture for 3229 mark 5 has two rows and an accepted valley; the old vector slice partly includes 56 components. The worker's trial wrongly admitted a strip-edge fragment of a preceding ')' with zero parent pixels. The checker's non-admission correction passes the fixture certificate/hull/mapped-export checks. Original-page ink, actual compose consumers, 13-origin perturbations, 208 coverage and page cost still need qualification. Marks 7/8 instead truncate actual row ends; a73d has four rows but only one valley, with accent-bridge vetoes upstream. Preserve these different causes rather than claim a single universal B blocker.

[Final geometry prompt](prompts/R8-GEOM-03-i3.md): resume Sol 01a1348b, high, on d468a9f plus these docs. Reuse same-call native strip/mask/ink/CC8/transform and the retained R refinement/certificate/hull. Replace final vector extent after `confirmed_partition` succeeds; preserve native discovery and one legacy fallback on unsupported inputs. The two-condition outside-fragment rule preserves legacy non-admission, not a new speck/noise tolerance. A component with parent pixels still requires whole support. Verify forbidden regions and changed-geometry decisions through the real stack. No page-specific runtime selection, new row finder or default-M17 change. R stays retained even if B fails. The target is a qualified second-book gain, not reopening all fronts at once.

Score all 42 frozen cases and every naturally reached accepted partition in 208. Keep 21 exact mark bindings distinct from the four fuzzy field-owned ones; original validation remains development-retest. Give physical reasons for partial→partial, and report default gains, experimental progress and diagnosis separately. The independent check should state whether the B blocker narrowed and which additional book improved. No new claim for an unchanged or unknown case.

### Closure after i3 and accountable open debt

Three slots total, two used, one remains. After i3, **close COMPLETE only on the unchanged GEOM03_GATE; otherwise CLOSED PARTIAL**. The four qualified R rows, and any qualified B population, remain solved in their bounded runtime contracts. The broader row/column gate and a–d geometry are not thereby solved. No fourth geometry iteration, no second GEOM03 after curl and no transfer of slots. Each later task retains its own feature/deletion contract; debt is evidence for that task, not a promise to finish every inherited case or an enlarged allocation.

| Later task (order unchanged) | Maximum | Geometry handoff and scope |
|---|---:|---|
| R8-FONT-03 |3| a73d accent/body bridges and valley veto; unique identities on c3cc/b9d6/4959; R-left row axes; A window/trim and M no-seed observation inputs. Correct row/class attribution where measured guides feed a real consumer. Any broader discovery/admission issue not reached remains explicit. |
| R8-CURL-03 |3| Horizontal support on 3229 m7/m8, 8686 clipped ends, finite c8/e259/field-owned domains needed for shared continuation. Detect actual page-edge curl and consume it; no generic replacement gutter model. M missing-row admission is not silently claimed fixed by continuation. |
| R8-RUST-02 |3| Current accepted R/B contracts and source; native_bands headroom, combined page totals, 0ce9 debt and slow-page list. Port stable computations, not experimental membership or evidence-only support_accounting. |
| R8-INK-02 |3| Expanded-support/forbidden/source refresh receipts, B5/M35 population, M55 and DN/source debts, weak/pale controls. Preserve known exclusions without treating unknown geometry as non-front ink. |
| R8-AUDIT-02 |1| Final accepted-source native gains, actual deletion and architecture, full owner ledger, font/curl consumers and speed. Carry every unresolved geometry target in an explicit backlog; audit is not another repair slot. |

The planner writes FONT-03 only after i3's result and full independent check. Best checked heads carry forward even on partial closure. Fourteen future slots, eight used and one retired, total ceiling 23 unchanged. Runtime tasks remain sequential; planner writes every next exact prompt after review.

**Daily budget update:** reported meter 3%; coordinator launch stop 17%, kill 20%, owner cap 20%. These replace FP8w's18/21 assumptions. Checkpoint before 20; no reset/bypass. The reported one point per Sol iteration is encouraging, not a guarantee that all 14 slots fit today. This planning pass edits documentation only and launches nothing.

## Retain progress and reach the wider callers — FP8w, 13 October

Owner instructions since i1, verbatim, in order:

> ok I dont want you to use more than 20% of limit today

> Ok what does Astra say? Are we making progress though?

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

**There is real progress.** The independent check reproduces the corrected 26-case raster certificate, six discriminating mutations, four complete right rows under both genuine windows, and exact work removal reducing request cost by 35–45 ms. The best experimental source is GEOM-03-i1's `experimental-source/` (detector SHA256 prefix fe4058ef3d), not the older timed source. No physical repair was retained, so accepted source remains a documentation-only head. Report those two facts together rather than describing an incomplete task as no progress.

**The cost failure is unconfirmed.** During the worker's final timings the unchanged baseline/detector slowed about 15%/13%. The checker's quiet corrected-source 10-sample order medians are 85.5–97.5 ms, with one 5-sample block at 101.2; natural request1 is 87.7/86.3. This is near the 100 ms ceiling, not a robust pass or a demonstrated algorithmic overrun. The i2 protocol measures the exact corrected source, prespecifies 10 pairs per order/window, invalidates entire blocks on >5% detector-control drift independently of candidate outcome, retains all raw samples and permits one replacement per invalid block. Persistent drift is inconclusive. The100 ms gate is unchanged; no normalized/subtracted clocks or retries until success.

**The wider sample must reach the mechanism.** Completion ran on 52 residual targets across 14 pages/9 books:4 completed on 4959,48 safe unknowns, zero regressions. This corpus receipt binds the timed source; the final corrected source still needs a fresh208 comparison. None of the 25 marked groups enters request completion. Actual caller capture comes first: the check nominates10 marks on 3229/a73d/c3cc as B (an accepted valley followed by vector slicing of the original box);15 marks stop earlier at the two-word-run gate (A). R is the seven residual witness rows; M is8686 row 5 admission; F is page-field/column geometry; N is the seven negatives. These are nominations to verify, not physical truth. The genuine 2cfe m19 witness is one whole row plus neighbouring slivers, needing trimming rather than a fabricated split.

[Iteration 2 prompt](prompts/R8-GEOM-03-i2.md) has two independently retainable parts: first qualify/checkpoint the four-row R repair with stable timing and a fresh corrected-source 208 comparison; then reuse its certificate/refinement/whole-component hull in `geometry_rows.partition/confirmed_partition` after a captured accepted valley. Keep `native`'s row discovery, window gate, tracks and input population. Pass this caller's own rectified strip/labels/transform explicitly; no residual chains or new ink model. Verify original-page export, forbidden regions and actual downstream consumers. Preserve the legacy vector split when new extent is unknown; do not undo a successful old split. The prompt corrects the i5 assumption that motif/rule costs are vertex-bound: their changed-ROI refresh is required; remaining numerical cost is mostly `native_bands`.

**I2 success is smaller than full closure.** Aim to retain R plus physical B gains on each of two working books, and score the c3cc retest and every frozen target. An independently qualified R-only or one-book B gain is useful PARTIAL and must survive a rejected later trial. Do not spend the whole iteration retiming4959 or undertake A trimming/F domains/M admission/R-left together. Report all 42 case rows with captured caller, native reason, before/after status, crop evidence, regression flag and default/experimental/fallback state. The original validation pages were exposed in i1: preserve their first scores and now label development-retest. No fresh-generalization claim or cohort reselection.

The [preset gate](GEOM03_GATE.md) and [cohort](GEOM03_COHORT.json) retain their targets and cost limits. Two GEOM-03 slots remain; i3 is not written. Order afterwards stays FONT03 → CURL03 → RUST02 → INK02 (3 each), AUDIT02 (1), from best checked predecessor heads under the result/check/planner-prompt loop. Fifteen future slots, seven used, one retired; ceiling 23 unchanged. Native gains, mechanism/deletion, experimental convergence and stalled fronts must be reviewed separately.

**Today's owner cap overrides earlier resource assumptions.** Coordinator reports meter 2%, up from 1% over i1, and daily launch stop 18%/emergency kill 21%. Plan and checkpoint to stay below the owner's 20%;21% is an emergency backstop, not authorised spend. Verify the effective daily guard before launch: read-only inspection still finds 97% in the inner `r8_task.sh`, so that older weekly check alone cannot enforce today. Coordinator-supplied outer guards may do so; no planner edit or verified active-process claim is made. Stop before 20%, no reset/bypass today; pause rather than close the task for lack of capacity. Today's cap constrains how far the sequence runs, not the per-task maximum. Do not assume future iterations will cost the same one point as i1.

## Geometry first, three slots — FP8v, 13 October

Owner instructions, verbatim, in order:

> ok I think we should keep going but try to use sol 6.1 as execution and astra as planner

> ok I want us to close the geometry aspect first before we continue so lets say we get +3 iterations

**Move R8-GEOM-03 to the front and use its existing maximum of 3.** GEOM-02's five iterations remain a closed historical task. This is the authorised continuation of its demonstrated repair, not a renamed failed assumption: the i5 check supplies an independently passing raster counterfactual and identifies avoidable implementation cost. There is no GEOM-02 i6–i8, no extra 3 on top of GEOM-03, and no second GEOM-03 after CURL-03. FONT/CURL each own their subsequent consumer integration and deletion inside their unchanged caps.

### Preset geometry closure

[GEOM03_GATE.md](GEOM03_GATE.md) is the binding, checkable end condition; [GEOM03_COHORT.json](GEOM03_COHORT.json) fixes exact IDs, source hashes and splits. Require complete single-row crops for all 25 marked groups on eight pages/books, all seven 4959 p5 request rows in both genuine windows, missing 8686 p5 row 5, and the c8 p36 finite-rule/e259 p198 leaf targets. Preserve all native letters/marks, no duplicate or neighbouring ink, finite column boundaries and the default-route invariants. Validate three reserved pages from different books, not just alternate windows of 4959. Tables, skewed/flat pages and 93f8's spurious rule count are explicit negatives. Keep the full 133-mark/nine-missing-page ledger and report remaining cases rather than calling equality a fix.

Completion requires actual default consumption and removal of the displaced extent/decision in its qualified scope. Require the 26-case native raster gate and discriminating mutations; disabled-route equality and identical-input page-field M17 isolation; every changed 208 crop/exclusion independently reviewed; fresh geometry-dependent ink/source decisions; coordinator private 44 qualification. Against db899f1, the median paired increase for **every affected request** must be ≤100 ms in at least five warm pairs per ordering, including refreshed decisions. Non-request changes use the affected page with the same 100 ms ceiling; no subdivision to evade it. Clean pages gain no extra processing pass or reproducible slowdown beyond paired controls. Report full 208 tails; inherited failures of the global <1 s target remain speed debt.

Call success **“GEOM-03 row/column gate COMPLETE”**, not completion of all a–d geometry or all 133 owner marks. Font guides and shared edge curvature are still named later features. The broader task gate is deliberately more than i5's right-column subset. At the cap, unmet targets mean CLOSED PARTIAL, with safe gains retained and exact failure evidence; administrative closure does not assert the problem solved. Apply the standing loop rule: after the result/check, the planner writes the next task's prompt from the best checked head. No automatic fourth geometry iteration.

### First iteration and following order

The [first exact prompt](prompts/R8-GEOM-03-i1.md) lands the corrected endpoint/raster construction and removes repeated hull/decision work through `recover` → `complete_request` → `native_bands/separate_bands`. Its smaller target is the four right rows, 26/26 native cases, unchanged left fallback, measured cost, default retention and broader-cohort evaluation. A sound subset can survive PARTIAL; it need not repair the left axes and every mark in one iteration. Later exact prompts depend on the result and independent check, not an assumed successful chain.

| Order | Task | Max iterations | Worker / worktree | Dependency and close |
|---|---|---:|---|---|
| 1 | R8-GEOM-03 | 3 | Fresh Sol 6.1/high / ff-r8-stack | db899f1 plus docs; preset row/column gate, or CLOSED PARTIAL at cap. |
| 2 | R8-FONT-03 | 3 | Fresh Sol 6.1/high / ff-r8-stack | Best checked GEOM03; measured-guide consumer and own displaced-policy deletion. |
| 3 | R8-CURL-03 | 3 | Fresh Sol 6.1/high / ff-r8-stack | Best checked FONT03; shared edge-curl detection/rendering/continuation and own integration/deletion. |
| 4 | R8-RUST-02 | 3 | Fresh Sol 6.1/high / ff-r8-stack | Best checked CURL03; port qualified stable computations, not unqualified experiments. |
| 5 | R8-INK-02 | 3 | Fresh Sol 6.1/high / ff-ink | Best checked RUST02; source/frame/ink debt and final geometry refresh. |
| 6 | R8-AUDIT-02 | 1 | Existing independent review arrangement / ff-review | Best checked implementation; assess all open gates and actual quality/cost/deletions. |

All implementation tasks stay sequential, with a fresh worker per task and resume within it; the existing worktrees remain. Every task starts from the best independently checked predecessor even if partial. Sixteen future slots remain, six used and one retired, ceiling 23 unchanged. This geometry phase may take roughly 3–9 worker hours plus review if all three slots are used; it is not a run-time cap or a completion promise.

The coordinator has implemented per-launch `MODEL=gpt-6.1-sol EFFORT=high` after loading spec5; the planner remains Astra/xhigh. Read-only inspection confirms the override. No new worker exists until the coordinator launches and records its thread ID. The reset is reported complete, meter 1% at this relay; keep 97% launch/99% run guards, not a stale 92% budget forecast. Old dated orders and no-extension text below are historical and superseded by this explicit owner authorisation.

## Sol worker context transfer and checked i5 — FP8u, 13 October

The owner asks to keep this planner and use Sol 6.1 to save tokens. Keep the Astra planner and independent review; use fresh **gpt-6.1-sol implementation threads per feature task**, resuming within that task. Preserve existing sequential worktrees and caps. [SOL_TRANSFER.md](SOL_TRANSFER.md) records the verified relay configuration and coordinator action; [SOL_WORKER_HANDOFF.md](SOL_WORKER_HANDOFF.md) is the compact starting brief. Supply that brief, one exact iteration prompt, the latest full independent check and named source/evidence pointers. Do not inject the complete historical chat. Each result adds a short checked delta before the next prompt. `high` effort is an initial recommendation to evaluate, not a measured optimum or token-saving guarantee. Model selection in the roster alone does not change the runner; no switch or launch occurred in this planning pass.

I5's integrated experiment completed the four right-column rows of 4959 p5 in both windows with identical membership and polygons; its 208-page enabled pass changed only those four crops. It was withdrawn because exported raster partition still fails at certain lattice origins, and request cost is +114–151 ms, above the +100 ms bound. The checker pins the remaining defect to half-pixel path versus rounded inclusive raster fill; its endpoint/clearance counterfactual passes 26/26 phase/window combinations but lacks full corpus and timing qualification. The three left rows remain unknown upstream. Retained source is tests/fixture/docs, not a shipped physical correction. The independently accepted i5 source supersedes the worker's stale b96cd9d handoff recommendation.

Carry native component memberships as useful font evidence, not as measured font guides. Keep the verified corridor/hull experiment for GEOM-03 integration; do not reopen GEOM-02 as i6 or divert FONT-03 into another separator retry. Unqualified trial code must not enter the default or Rust route.

The owner's sampling concern is correct: **four repaired rows on one page are one positive page**, even across two windows and 26 phase checks. The 208-page pass mainly establishes regression preservation. Each new physical feature task must freeze a small multi-page, multi-book positive cohort, negative controls and previously unused development validation examples before adjusting the mechanism; select from the existing development allowlist. Report positive physical successes separately from unchanged pages. Do not tune against the coordinator's private44.

The order is **FONT-03 → CURL-03 → GEOM-03 → RUST-02 → INK-02**, at most three iterations each, then **AUDIT-02**, at most one. GEOM-02 is closed at five and pilot i2 retired: **16 maximum future slots, 6 used, 1 retired; ceiling 23**. Reset authorisation and 97%/99% safeguards remain. The FP8t section below preserves the previous allocation rationale; its pending-i5 state and old worker assignments are superseded here. Every next prompt still follows a result and independent check; this context packet is not a launch prompt.

## Owner-directed completion and repository organization — FP8t, 12 October

The owner asks to fold the component/font-line construction, shared page-edge curvature and repository organization into the plan. [GEOMETRY_COMPLETION_PLAN.md](GEOMETRY_COMPLETION_PLAN.md) gives the task contracts, functions, controls, workers and close rules. This amendment supersedes the automatic i5-to-Rust transition and resolves the scheduling gap noted in the subsequent clarification sections.

| Order | Task | Maximum remaining iterations | Concrete outcome |
|---|---|---:|---|
| 1 | R8-GEOM-02 i5 | 1 | Finish/close the already-issued separator task at its original total cap of 5. |
| 2 | R8-FONT-03 | 3 | Existing component/font tools feed a real guide-based crop consumer; delete its displaced decision in the verified scope. |
| 3 | R8-CURL-03 | 3 | Detect edge curl if present, render shared virtual lines, and replace independent row continuation with that geometry. |
| 4 | R8-GEOM-03 | 3 | Integrate row/guide/bend/boundary consumers, remove competing policies and verify complete crops and cost. |
| 5 | R8-RUST-02 | 3 | Port substantial stable computations; retain current build/test/deletion obligations. |
| 6 | R8-INK-02 | 3 | Existing source/frame/ink task, with recomputed geometry-dependent evidence. |
| 7 | R8-AUDIT-02 | 1 | Independent final assessment of physical features, architecture, owner cases and measured speed. |

The **6–10 geometry-iteration forecast** includes the one already-issued i5 and assumes early closure where successful. New task maxima are 3/3/3; the old geometry maximum is not extended and retired slots do not transfer. All runtime tasks are sequential; same stack worker/worktree for the three new tasks and Rust, existing ink/review workers afterwards. Every task starts from the best checked predecessor head even if partial. Reliable existing geometry can support curl work if the font task remains partial; no universal body/ink provider is presumed.

Expect a retained measured-guide consumer or a concrete replaced mechanism within the first 2–3 new feature iterations. An offline-only guide plot, another empty successful population or extra auditing does not satisfy that milestone. Complete task closure also requires the named final native results and deletions. The next iteration's exact prompt comes from the planner after the result and independent check; none of the three future prompt chains is pre-written.

The GitHub-facing documentation now has five entry points: **generations; tests/evidence; charter/method; architecture/responsibilities; current state**. See [documentation index](../../../shared/DOCUMENTATION_INDEX.md) and [organization guide](../../../shared/REPOSITORY_ORGANIZATION.md). The charter is preserved in tracked documentation, original APIs are labelled, and the guide explains which results are local-only. Code paths and private evidence are not moved. Actual removal/module cleanup belongs to each feature's caller migration, not a parallel mass rename or another generation directory.

There are 17 remaining maximum worker slots including downstream Rust/ink/audit; 5 used and 1 retired bring the revised allocation ceiling to 23. The reset and 97%/99% safeguards remain. The geometry forecast is roughly 3–15 worker hours plus checks, not a deadline. This planning pass performs documentation/link/JSON checks only and prepares local Git integration; no new run or publication is claimed. The older dated sections below remain the history, not the current task order.

## Owner clarification: the paper surface is the geometry model, 12 October

The owner's latest objective, verbatim:

> The goal should be this, it is very important you understand this:
>
> if we can build a model of the blank page, and its geometry in space,
>
> then we could be able to simulate how we would be seeing parallel lines drawn on that page any way we like.
>
> If we do this, then simply knowing the line passing through line of text, would predict how it would bend on the page

**The model describes the paper and its projection into the image.** Give the paper intrinsic coordinates `(u, v)`, a surface `S(u, v)` in space and a viewing projection `P`; the common mapping is `F(u, v) = P(S(u, v))`. A straight line drawn on that paper, at any chosen position and direction, projects through this same mapping. For an ordinary text row, locating its straight reference line on the paper predicts its curved image path, including its continuation beyond a clipped detector box. The font guides are other lines on the same surface. Text observations help estimate the geometry; the geometry must remain renderable when the text is hidden.

This is stronger than pooling independently fitted text curves, or obtaining a good separator on four rows. A restricted displacement mesh may implement part of the mapping, but its expressive limits and physical evidence must be established. A single image does not establish a unique 3D surface/camera reconstruction; if an equivalent image mapping is used, state what it predicts and what depth remains unidentified. Do not describe a smooth ink-density mesh as a verified paper surface merely because it renders smoothly.

**Required geometric evidence:** show the inferred blank surface/view and projected families of parallel lines at several positions and directions, then overlay the same mapping on the native page. Show where bending begins and how it varies across the sheet, where observations support the continuation, and where the geometry remains undetermined. Check predictions on text portions not used to fit that local path, against native pixels and the first-generation construction with its known errors. Use known-surface synthetic renderings to test arbitrary-direction predictions that the real printed page may not constrain. Columns constrain text extent; a column boundary alone is not evidence of a separate paper surface. Two leaves may require separate surfaces.

**Connection to simplification:** row discovery locates each row in paper coordinates; the common mapping supplies its skew and curvature; measured font geometry supplies its guides; ownership and layout determine its complete crop. Migrate callers and remove competing continuation decisions where this construction is verified. Paper geometry does not by itself identify row count, font height, source ink or every detached mark. Conversely, perfectly completing every crop is not a prerequisite to investigating the surface from reliable observations.

**Planning consequence:** the current i5 prompt is a bounded crop/separator repair, not this deliverable. The previously scheduled transition from that repair to Rust leaves the surface objective without a concrete remaining milestone. At the next result/check, the planner must revise the remaining sequence around this objective and identify the existing calculations to reuse; it must not silently claim i5 or a faithful port completes it. Earlier worker constraints against a new page model must not erase this owner-defined feature, nor should the feature become a separate replacement pipeline. This records the objective and scheduling gap; it does not rewrite an issued prompt, launch a worker, assign extra iterations or change code. The next allocation/prompt remains an explicit planner deliverable in the coordinator loop.

### Practical scope: detect book-induced edge curl, if present

The owner's subsequent clarification, verbatim:

> Right our idea is mostly to target the edge of the page, where actual curvature presents due to book structure, and have a heuristic that actually detects it, if any

This narrows the implementation milestone above. The paper-surface model provides the physical explanation and shared geometry; the immediate task is a lightweight heuristic for **whether edge curl is present, where it starts, and its displacement across nearby rows**. Full 3D surface/camera reconstruction, arbitrary-direction validation and a complete new page model are not prerequisites for this first edge-curl milestone. Do not turn the conceptual blank-paper representation into an unnecessarily broad reconstruction project.

Use reliable interior text geometry as the reference for straightness/skew, and evidence from multiple neighbouring rows to establish a shared departure near the edge. Inspect the original font/pooled-curve tools and existing page-field implementation for reusable measurements. Compare physical row/font geometry, not merely an image-density trend. Do not assume that every page bends, that the bend always occurs at a predetermined margin, or that every row has an identical displacement. Separate unsupported evidence from an evidenced absence of curl.

The concrete rendering is the owner's family of virtual parallel lines across the page: straight or skewed through supported flat regions, bending together where edge curl is detected. Show onset, direction and displacement, with the same geometry over native text. Positive controls must include the known curled endings; negative controls must include straight and skewed pages so perspective, short text, noisy margins or a printed rule do not by themselves establish curl. An inferred surface remains a hypothesis verified against observed geometry, not recovered ground truth.

The detected edge geometry must then drive continuation of existing text-row lines and font guides, respecting neighbouring rows and layout boundaries. Identify which independent continuation policy is replaced. A diagnostic bend overlay alone is not completion of the intended correction, and the local separator repair alone is not detection of page-edge curl. The next planner revision should scope and sequence this concrete feature, preserving useful existing code and the established result/check loop.

## Owner clarification: three generations, 12 October

The owner explicitly distinguishes our original model alone, the small neural detector plus heuristics, and the current third-generation revision. [MODEL_GENERATIONS.md](MODEL_GENERATIONS.md) identifies the first as the pixel-first `glyphs/page_text_lines.py` lineage, now `greekocr/pages/lines.py` with its font/pixel tools; it is not the failed Paddle-seeded R8 adapter. The current source and saved 23-page slow reference retain that implementation. The first-generation model already connects row identity, columns, skew, curvature and font-guide boundaries.

Use that connected construction as concrete comparison evidence, not merely a historical citation. On the same native failure, the next check should show the first-generation rows/guides/ownership/boundaries beside the fast result and identify their earliest divergence. Reuse a successful existing calculation with its proper input contract before inventing a replacement; keep the old model's own failures explicit. This clarification does not silently change the issued i5 prompt, launch another task or enlarge the caps. It accompanies the next result review and subsequent planner-written prompt, including selection of stable Rust semantics.

## After geometry iteration 4 — FP8s, 12 October

**Spend i5 narrowly.** The [full independent check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i4_check.md) now recommends the final iteration. Its real-caller counterfactual completes three right-column rows in both genuine windows, while #109 is blocked by four endpoint pixels of upper-neighbour component 622. This is a reusable repair of a narrowed dependency, not a request to rebuild all seven rows. No physical change is yet retained; left-column row axes still cut λ689 and ς1131 and remain outside this iteration.

The owner's response to i2's target crop, verbatim:

> bro, I am not sure I fllow. iteration 2 is quite good

**Agreed about the shape.** The planner inspected i2's native whole-row comparison and the checker's two-window drawings. I2's tight per-word outline restores the descenders and looks better than the accepted clipped box. Its shape should be reused. The rejected membership dropped the apostrophe and absorbed neighbour words on other rows; that does not make a tight hull undesirable. I5 therefore uses the verified separator corridor to select whole components, then draws the tight hull around exactly those, with the apostrophe included. Preserve this distinction in the owner's next visual review.

**Correct the i3/i4 seam explanation.** Earlier text below, and the i4 prompt, incorrectly described a native per-pixel path lost through simplification. There is no such path: `valley_path` solves a roughly 13 px by 4 px lattice over 5×5-dilated ink. Interpolation does not restore native resolution. Window 0 happens to hit a two-pixel opening; window 1's crop-dependent lattice shift misses it and cuts β/λ. The earlier y2759 path touches φ and passed only because of a crossing tolerance. Removing decimation alone is not a fix. This amendment supersedes that causal claim, without rewriting the historical experiment.

**What i4 established.** Finite upper-neighbour grouping and lateral union now pass experimentally: preceding descender 588 stays outside, own 736/757/721/738/754 remain whole, and “το” retains 180/69/303 pixels. One batched request is order-invariant. Its final trial still completed 0/7. The missing right-column inputs are physical rule edges (supports begin inside the rule's ink), and owned neighbour bodies 622/707 omitted from span-only support. The checker's three corrections complete “καὶ τακτοποιήση”, “πάτε” and “τος,” in both windows; #109's four-pixel residual must be repaired, not tolerated. Window differences of 39/18/4/33 pixels are not a quality threshold. The naive full-resolution Python counterfactual costs about twice as much, so the runtime version needs bounded native refinement.

**I5 scope and explicit removal.** Reuse i4 `complete_request` and its single M17 batch, existing accepted rule evidence, native mask/components and i2 hull construction. In a request-only keyword mode, refine the coarse separator on undilated native ink with zero-tolerance whole-component validation; clip supports and polygons to the accepted rule's actual finite ink edge; use fragment spans union whole owned-body support for neighbours too. Then the verified component hull replaces crop-sensitive raw detector extent/owned-only completion in the qualified population. This is a conditional local replacement, not removal of all residual extent policy, M33 or seven bend authorities. No new discovery, bend, gutter, font/ink model, left-axis repair or finite-domain retry.

Default page-field M17 must retain its old behaviour: i4's shared changes regressed 4959 p4 row105 and p5 “πάτε”. The sole opt-in caller of the new separator mode is `complete_request`. Default/disabled completion must preserve all 208 final outputs; the integrated residual candidate may change the intended crops and must undergo complete changed-crop review, with page-field outputs still unchanged at identical inputs. An opt-in-only gain is labelled as such, not claimed to improve shipped default crops. All geometry-dependent source/ownership decisions must be recomputed.

**Preset scoped success:** #109 and the other three right-column rows complete in both windows, with tight hulls, whole letters/marks, no neighbouring text or rule bar, preserved left-column fallback and order independence. Final membership must agree; inspect every residual raster difference instead of accepting an IoU or pixel allowance. Require actual consumer/mutation tests, default-route isolation on 208, review of every changed integrated crop/exclusion, and at most +100 ms per affected request in paired orders against b96cd9d/0474bf8. No hard-coded page/right-column population. A separately qualified non-empty subset can be retained as partial physical progress even if all four do not pass. No further design expansion if the bounded repairs still fail.

**Close at the cap after the check.** Four rows passing completes the scoped iteration, not the wider G3 domain/curl/ownership obligations. Geometry closes COMPLETE only if those actual obligations passed; otherwise CLOSED PARTIAL, carrying safe improvements or unchanged b96cd9d runtime and exact residual debt. The next task is R8-RUST-02 from the best independently checked head. The planner writes its first prompt only after this result/check. No i6 or transfer of the retired pilot slot.

The reviewer must report completion, retained output/mechanism progress and experimental process progress separately, naming old witnesses now passing, reusable corrections, remaining dependency/scope, generalization controls, cost and recommended checked head. Preserve i3's STALLED and i4's CONVERGING-right/STALLED-left verdicts as dated assessments. Additional bookkeeping or all-unknown equality is not a physical gain.

**Current source/resources.** b96cd9d adds one test file plus documentation; runtime remains 0474bf8 including its audit, outputs inherit its checked equality to 54cc8f9. The i4 suite is 282 passed/7 xfailed. No new private44 or final-runtime timing run was needed for unchanged runtime; do not label rejected-trial timings as retained results. Definitions remain 6/9/9/7 and cumulative runtime −452 lines from d5dc3e2. Five slots are used (pilot 1 plus geometry 4), one retired, eight maximum slots remain: geometry 1, Rust 3, ink 3, audit 1. The reset authorisation and 97%/99% safeguards stand. Meter does not shorten this sequence; no current reading is claimed.

FP8s governs the current head, next launch and corrected seam mechanism. Amendments below preserve the planning history.

## After geometry iteration 3 — FP8r, 12 October

The coordinator relays the owner's latest instructions verbatim:

> ok keep going with the task, dont just say failure from now on. You have to ask the reviewer more about the process, as in is there progress towards the solution even if the task didnt complete.

> We will do a reset don't worry about it

**Choose narrow geometry i4.** The [full independent check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i3_check.md) recommends closing because three iterations kept no physical improvement and neighbour construction risks expanding into a new row model. That concern remains valid after the reset. I4 is justified by the exact bounded alternative in the same check: correct finite neighbour representation, supported seam range, dense-path clipping and lateral conservation. It does not commission a complete new row model or repeat the whole seven-row design without changing its failing inputs.

**What i3 established.** One request-level call replaced seven in the rejected trial, reducing its added cost from +383–415 to +95–132 ms. Source-bound captures now locate both failed sides of #109: the lower valley passes between φ 754 and β 906, but ~12 px seam sampling cuts the real 3 px corridor; above, five finite fragments are treated as separate full-row neighbours and extrapolated over unsupported x. Fragment 21 mixes target-line and cross-rule support, and owned-body-only lateral extent drops “το” (1433/1466/1420). These are reusable causal witnesses. They narrowed the location, not the overall scope, of the blocked repair.

The final trial completed **0/7**, all unknown and byte-identical to its baseline windows. Its apparent order independence therefore is not evidence of a successful physical replacement. The retained `support_accounting` runs only on page-field M17, not residual completion, and feeds no decision. It is cheap, output-neutral bookkeeping. Its 230 substantial partial records on 29 pages are unadjudicated candidates, not proven final errors. Keep it as evidence; do not port it as part of the Rust numeric contract. The ambiguity fixture pins existing M17 behaviour rather than distinguishing the rejected residual trial. Both residual xfails now fail for the intended physical clipping, and the float tie is fixed.

Best head **0474bf8 includes the audit** (+24/−1 runtime, net +23; −452 cumulative from d5dc3e2). Feature counts remain 6/9/9/7; DB extent, finite full-height and M33 policies remain. The suite is 282 passed/5 xfailed with local images; the checker archive is 281 passed/1 skipped/5 xfailed. Source manifests match their own heads; they are not 190 hashes identical to 54cc8f9. Fresh 208 output/evidence comparisons and the coordinator's 44/44 output parity are accepted. Paired timing is noise, including the coordinator's −3.3 ms median versus detector −1.3 ms. The single fresh full208 is 183.868/1233.653/1917.055 ms, 20 over one second; historical clocks do not establish a gain.

**I4 scope.** Reuse the archived `complete_request` and live `native_bands/separate_bands`. Assemble fragments of an already observed line on the correct accepted-rule side, retaining native chain identity and finite support. Remove target-line duplicates from its neighbour set. Limit each seam to the neighbour's supported x, and use the dense valley for the actual clipping polygon, not just a preliminary check. Restore lateral union of the admitted piece and owned bodies within its column. No new row discovery, page bend, ink threshold, finite-domain reconstruction or M33 migration. The `geometry_columns.apply` wide-box 6h split precondition does not fit short fragments; the brief explicitly requires a compatible adapter using existing accepted rule/clipping evidence.

The primary result is #109 completed through the real caller in both windows with φ/apostrophe inside and 588/906 outside, plus “τος,” retaining its initials. All seven rows remain non-regression controls. A separately verified live seam correction can survive if the complete row repair remains partial. If the target still cannot pass its separators after the bounded input/path repairs, stop expanding the design and return the exact remaining counterexample. I5 is not automatic: the planner and independent review decide whether a demonstrated reusable correction warrants the remaining slot, or geometry closes partial and Rust follows.

**Progress review is now an explicit deliverable.** Completion and progress are separate verdicts. The check must name (1) each old pixel witness now passing through the real consumer, (2) the retained code or source-bound experimental correction that removed a specific dependency, (3) what can be reused without repeating this iteration, (4) whether the remaining blocker narrowed in location and scope, (5) what control suggests the repair generalizes and (6) the next bounded action or reason to close. Report retained final-output progress, retained mechanism progress, reusable experimental progress and diagnosis-only/stalled status separately. An audit key, an empty successful population or unchanged unknown fallback does not demonstrate a physical repair. The i3 STALLED verdict is not revised upward retrospectively.

**Reset supersedes prior budget forecasts.** The earlier two-point reserve, 95% plan closure, and predictions that Rust/ink would not fit no longer govern the sequence. Preserve the geometry/Rust/ink/audit maxima **5/3/3/1** and the already retired pilot slot. At **97%** the runner refuses launches; at **99%** its guard stops running work. The coordinator saves the checkpoint, pauses and resumes after the authorised reset and actual available capacity. Do not bypass guards, trigger resets from a worker or call a pause a task failure. Resume unfinished work under the same iteration identity; the reset does not grant additional iterations. Current meter is unknown here; i3's supplied launch reading was 90%. Four slots are used (pilot i1 plus geometry i1–i3), one is retired, nine maximum slots remain. The authorised sequence continues through Rust, ink and closing audit across the reset, with each prompt written only after its preceding result/check.

FP8r governed the i4 launch. FP8s above supersedes its seam explanation, source head and next-iteration decision.

## After geometry iteration 2 — FP8q, 12 October

The owner, after asking whether the iterations were making cumulative progress on specific failures, said:

> ok keep doing that then

**Use the next geometry slot for the concrete request-level repair below.** The [full independent i2 check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i2_check.md) recommends closing geometry because another attempt may consume the remaining Rust budget, but also supplies a concrete i3. The owner's latest instruction makes continued focused geometry the next priority. This does not override the 97% refusal limit, the closing reserve or the five-iteration cap. The coordinator must check the current meter before launching; no further owner confirmation is required within those bounds.

**The independent findings correct the worker's account and the planner's initial summary.** I2 made the target crop equal across two windows and restored descenders, but its new owned-only hull removed an unassigned apostrophe. Existing smooth bands retain all 88 diagnostic mark pixels, although they also reach the next row. The slow reference and nearest-box attachment both misassign the mark; neither is a certificate. More seriously, the trial loses whole recovered rows, crosses the column rule and absorbs “θέσ” and “δὲν ἴδε” from neighbours. Only the target row agrees across windows. This was not one missing apostrophe away from acceptance. The trial also repeated the entire request's M17 assignment/separation seven times, causing most of its +383–415 ms per-request cost.

The accepted 0d4dc50 retains no runtime change or policy removal. It has 280 passing tests and five strict xfails. The new non-empty M18/native-band test is meaningful; one separated residual fixture instead fails at a 3e-13 px floating-point tie, and neither synthetic mark fixture reproduces the native ambiguity. Fix their failure reasons and add the missing counterexample. All 190 runtime files and the 208/624 input/artifact rebinding were independently verified; inherited timing stays 199.421/1287.272/2007.555 ms, with 22 pages over one second. No fresh private44 result is claimed for this unchanged runtime.

**I3's one target is simultaneous residual completion between verified native separators.** In the existing `type_residual_recovery.recover` caller, collect the request's eligible pieces with correct chain identities and use `geometry_field_detector.native_bands` once against a stable neighbourhood. Reuse the existing smooth bands and `separate_bands` whitespace corridors, preserving whole components and finite column boundaries. Do not keep the rejected owned-only hull or use the unconstrained smooth envelope as a finished solution. Unassigned marks can remain inside a verified segment without being called positive row/body/source evidence; shared/unknown support must stay visible. Where corridor sides establish row membership, they displace the nearest-body decision in that measured population. This does not require a semantic classifier for every mark.

Neighbour rows that themselves span two lines or cross a rule are real input debt. Their polygon centres cannot become trusted row axes by batching them. Validate existing native chains and separator support; do not fit one axis to different chains selected solely by x-range. Keep unresolved pieces on the existing route and report incomplete migration, rather than dropping the row or declaring success. Validate the final seam/polygon, including simplified or extrapolated portions, against native support. No new page model, nearest-distance variant or gutter detector.

Acceptance covers **all seven** baseline additions in both 4959 p5 windows, the apostrophe and descenders, whole-row preservation, absence of neighbouring words and rule crossings, and proposal-order independence. Full success requires all completed row polygons/support to agree; unresolved legacy pieces leave the result partial. Recheck source decisions after geometry changes. Measure one request-level call and postprocessing against accepted runtime; reducing the rejected trial's overhead is not a baseline speedup. A verified, independently useful caller or audit correction may be retained even if full completion is unresolved. Tests/evidence alone are still labelled as such. Finite-domain construction and M33 migration are **not** additional i3 objectives.

**Budget forecast changes:** 88% was the reading at i2 launch; i2, its review and this planning work have since run. Current usage is unknown to the planner, so the former seven-point estimate is stale. Geometry i3 and closing review take priority; a substantive Rust iteration is now conditional and may not fit. Renewed ink remains unlikely. The coordinator reserves roughly two points for closure and does not launch i3 if it cannot leave that headroom. At early resource closure, audit the best checked head and label unstarted tasks NOT STARTED (budget). There are ten remaining maximum slots (geometry 3, Rust 3, ink 3, audit 1), not ten funded iterations. No i4 or later task prompt is written now.

The amendment below records the earlier i1 decision and forecast; FP8q governed that historical launch and has now been superseded by FP8r.

## After geometry iteration 1 — FP8p, 12 October

**Continue with geometry iteration 2.** The [independent check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i1_check.md) identifies a concrete, testable dependency. The worker made a real finite-domain repair through `blocks/render/certify`, M17 and M18, fixed c8's internal heading domain, then correctly withdrew it after native losses. Nothing in the runtime was promoted. The retained result adds tests/evidence: 279 passes and three strict xfails, including two finite-domain defects and the inherited faint-front defect. No policy was removed; definition counts remain 6/9/9/7 and runtime remains −475 lines from d5dc3e2. The coordinator skipped another private44 run because runtime is identical to its checked 54cc8f9.

The checker settled the residual failure the worker had left unresolved. On 4959 p5, changing the regional detector request from y2576–3080 to y2583–3079 changes the target polygon from y2683–2759 to y2691–2757 and loses the preceding row. This persists at both local heights 40 and 48. The recovered row takes the raw Paddle polygon as its final extent. Accepted final #109 already clips descenders; the trial clips more letters/marks. Changing the field census exposed this dependency rather than creating it. Freezing the old census or request windows would hide it.

**I2 first replaces the residual extent decision in `type_residual_recovery.recover(version=11)`.** Use the existing native component/envelope and M17 body/mark attachment machinery, with a focused compatible input extension where needed. The two real detector windows must yield the same completed native row, with whole descenders/accents and no neighbouring-row text. Record genuine detections and support provenance; add a nontrivial consumer test and check native crops. A stable but clipped polygon is not acceptance. Do not blindly enable `snap_components`: its intersecting-component selection and inherited polygon envelope do not by themselves make extent independent of the window. No new row/page model or global body-height estimator is commissioned.

Only after that passes, retry finite domains. Keep the measured rule interval; put the computational transition in an evidenced corridor between complete rows, rather than raw y≈995 through c8's accents and initial Ὅ. Use one native raster mask per field with explicit transform/boundary semantics, instead of per-pixel Shapely tests. The rejected trial added 4.63/4.14 s on 80 paired controls, almost entirely field proposal; the checker's roughly 5.1 s mask-work estimate explains a plausible cause, not a measured saving. Test non-empty M18 proposals and actual native-band consumers. Adjudicate every changed row, including 4959 p1's 122→119 items and the unmatched 44b5 rows, not just the headline regression.

Keep a valid residual repair separately reviewable if the domain retry fails. If neither is valid, retain 09b74cf's tests/docs and unchanged 54cc8f9 runtime. Record the first failing assumption rather than another guard. I2 can make useful physical progress while G3 remains PARTIAL. It must report which old decision was replaced, which callers consume the new support, and what remains for Rust; no claim that all seven path authorities or owner cases are resolved.

The earlier dependency order was incomplete: the finite-domain experiment exposed a downstream residual-extent prerequisite. Its revised local order is **native residual completion → finite domains and their consumers → remaining row/class/body/continuation work**. This changes the next implementation, not the five-iteration geometry cap or the later task order. After the i2 result/check, the planner chooses whether a specific further geometry repair is worth another iteration or geometry closes partial and moves to R8-RUST-02. It will not consume all five merely because they are available. No later prompt is written now.

**What should fit this meter:** at the coordinator's latest **88%**, about seven points remain before the two-point closing reserve at 95%; the runner refuses launches at 97%. Expect geometry i2, one substantive Rust iteration and a closing audit. One additional geometry iteration may fit if progress is concrete and the live meter still leaves room for the Rust iteration and audit. A renewed ink iteration is unlikely this meter; completing all five geometry or all three Rust iterations is also not the current forecast. Recent workers cost about 1–2 points, with planner/check overhead also charged. These are conditional planning expectations, not reservations or automatic launches. If costs run high, close implementation early and audit the checked result; mark unstarted tasks NOT STARTED (budget), not failed or completed. The caps remain maxima, not promised expenditure. The owner again authorised the automatic loop; no additional permission step is introduced.

## Owner-directed loop revision — FP8o, 12 October

The owner has now approved rearranging the plan and continuing the coordinator's automatic loops:

> ok re arrange your plan as you see fit, and I ll leave you to the autoamtic loops workings next

This owner-directed ordering remains in force; the FP8s result and next-launch amendment above supersedes its original i1 launch state and reset policy. Keep the current iteration maxima and resource limits. **Run geometry in Python first, then the next substantial Rust stage, then ink/source repair, then the audit.** R8-RUST-02 moves ahead of R8-INK-02. The pilot stays closed and parked. This changes task order, not worker allowances, the page-quality requirements or the final speed target. At FP8o the next launch was R8-GEOM-02 i1 from 54cc8f9 plus documents. That iteration has now run; see FP8p above for its result and i2 handoff.

**Why.** The current Python stack already has the full behaviour, native inspection tools and regression cases. Use it to resolve changing physical assumptions without simultaneously maintaining a port. Rust's language complexity is secondary to that transition cost. After geometry, a stable computational stage can move before the harder ink/source investigation. Unresolved source classification does not by itself invalidate a numerical field/row contract. Conversely, changing language does not settle row identity or glyph ownership. This sequencing does not require every OCR issue, or the Python subsecond target, to be solved before Rust starts.

**Unit of work.** Each geometry/ink prompt chooses one primary page feature and follows its provider through the live callers: the observed feature and explicit/native reference, the exact input contract, the old decision being displaced, and the downstream crops. A supporting contract fix is in scope; another broad inventory or an unused shared wrapper is not the implementation target. Preserve useful existing behaviour, delete the displaced rule only when its replacement is verified, and record unknown support honestly. A bug repair can be valuable without reducing a top-level definition count; it is reported as that repair, not as complete consolidation. Each report separates physical fixes, policy deletions, computational savings and remaining counterexamples.

For geometry, the dependency order is finite domains → row identity (including residual/no-seed rows) → complete glyph/class attribution → justified body/font measurements → shared continuation and removal of the superseded policies. This is a dependency order, **not five pre-assigned iteration prompts**. The result/check determines which link is actually ready next. No new pipeline, from-scratch page model or renamed failed assumption. The first prompt attempted finite-rule repair. The checked result now puts residual extent ahead of its next retry, as recorded in FP8p.

**When a Rust boundary is ready.** At R8-RUST-02 entry, use the checked geometry head and current profile. Select a substantial complete computation only when (a) its input/output coordinates, support, ownership, ordering and invalidation are explicit, (b) real callers and counterexamples have source-bound differential fixtures, and (c) the proposed ink work can change its input values without redefining that interface, or the interface dependency has been resolved first. Stable means an understood contract, not a claim of universally correct page decisions. Known defects remain in the ledger. Measure the whole call including Python/native callbacks, copies, allocation and integration; the M17 numeric-only fraction cannot stand for the whole stage. Port current computation and physical corrections separately so failures can be attributed.

The Rust task first resolves build/collection blockers for any code it adopts. Retire displaced active Python/bridge copies after qualification and retain Python as an offline oracle; do not create a second evolving production algorithm. If no substantial boundary is ready, record the specific unresolved input and carry safe build/test/consolidation work; do not invent a new model to fill the port allocation. Close partial at the task cap or resource closure. A valid local port is scoped progress; full migration and the whole-page speed gate remain separate obligations. No larger speed multiplier is promised.

**Ink after Rust.** R8-INK-02 starts from the best checked Rust-task head, even if that task closed partial or retained Python. It still implements the unresolved physical observations in the existing Python providers where they live. It must not fork a newly adopted Rust decision back into a parallel Python runtime. Before touching a ported interface, update its authoritative fixtures and implementation together; if it cannot remain valid, withdraw that port from the active route explicitly and report the lost saving. Unknown source cases are not solved by geometry. The prepared-atlas contract remains an ink prerequisite, except that R8-RUST-02 must fix it itself before any port touches that producer/consumer boundary.

**Timing and final head.** R8-RUST-02 qualifies its then-current route; ink changes can invalidate those output and timing receipts. The final ink candidate must supply fresh 208 output evidence and paired timings for changed paths, and the final full timing qualification if the runtime changed after the Rust qualification. The audit checks source identity against the actual final head; it cannot call an older Rust benchmark the final speed result. If resources prevent the final qualification, mark that gate unqualified/partial. No extra iteration is created for it.

**Autonomous handoff.** The coordinator merges these scoped planning files, checks the next prompt's four sections and the live meter, and launches it through the established runner. After each worker result and independent check, it returns both to this planner for the next complete prompt. Routine partial results advance the existing loop from the best checked head; no owner confirmation is needed within this authorisation. Do not pre-write later prompts, start a competing scheduler or launch workers from the planner. If a worker has already started by the time this revision is received, let its current checked brief finish and apply the ordering/handoff changes afterward. Use [LOOP_HANDOFF.md](LOOP_HANDOFF.md) as the coordinator's short entry point.

## After the pilot: Python repairs and stable Rust stages

Finish language-independent deletion and caller consolidation, but defer elaborate Python-specific tuning. The representative Rust stage has been measured before translating the entire unresolved stack. Compare release-built Rust and Python on the same inputs, native backends and resource budget; include conversions, inference and final output. The current code remains the behaviour reference, with its known physical defects explicit. Python is not required to meet the final speed target before migration.

The binding sequence is now: completed Rust pilot → concrete geometry repairs in Python → substantial stable Rust stages and consolidation → focused ink/source repairs → final-head audit. Geometry moves ahead of broad translation after R8-04 i1 showed the remaining exact-sharing gains are small. All workers run sequentially in this allocation. The finite-y rule bug is reopened as geometry work; supported explicit Rust features may replace fast approximations only after actual native and speed comparisons.

The pilot has now answered its limited question. Its measured 2.83–4.01% correction and 2.16–3.03% file-to-final savings do not support the earlier 1.5–2.5x correction / 1.3–2x overall planning ranges. Those ranges are withdrawn as forecasts and retained only as history in [RUST_SPEED_ESTIMATE.json](RUST_SPEED_ESTIMATE.json). A broader port requires measurements of substantially more work and its conversion/glue costs.

R8-04 i1 has finished and is accepted at 54cc8f9; its old i2 is absorbed as mapped in the allocation below. Old R8-05 is superseded by the one-iteration closing audit. Historical tables and prompts remain evidence only; their old allowances cannot add slots to this allocation. G1b/G2/G3/G4 remain partial.

## After the Rust pilot — FP8n

**Close R8-RUST-01 now; do not launch iteration 2.** The check confirms exact parity for 44 real crop replays and 208 pages / 15,093 items, and reproduces the speed gain. That satisfies the experiment's close rule. It does not make the crate ready for adoption or pass any physical/speed gate. The unused slot is retired, not transferred. Keeping three versions of M17 while geometry changes would add maintenance work for a small immediate gain. With the weekly meter at about 85%, use the next iteration for the located geometry defect rather than extending this boundary or starting another pilot on M15.

The full [independent pilot check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-RUST-01-i1_check.md), [worker report](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust/docs/research/round8/REPORT_R8-RUST-01-i1.md) and [handoff](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust/.astra/fast_lines/out/round8/R8-RUST-01-i1/ITERATION_HANDOFF.md) are preserved. Their original pending/no-worker-commit wording is superseded by the runner's 953fc4a commit, ACCEPT WITH NOTES and the coordinator's private44 results. This amendment records that status without editing the parked worktree.

M17 takes 5.604850 → 3.456970 s over the sum of 44 per-call medians (1.621x, seven alternating pairs). Retained Python/OpenCV/SciPy/Shapely callbacks account for approximately 2.61 s, about 75% of the hybrid stage. With those callbacks unchanged, even a free Rust part caps this boundary near **5.60/2.61 ≈ 2.1x**. M17 is about 7.7% of corrections, so a completely free M17 caps correction speedup near **1/(1−0.077) ≈ 1.083x**; the measured local gain predicts about 1.030x. These are scope-specific approximate ceilings, not bounds on a future broader port. The 95-page paired runs measure corrections −4.006%/−2.834% and file-to-final −3.028%/−2.156%. The Rust full208 has 18 pages over one second. The coordinator's private run reports −4.9% correction sum and −1.3 ms median; workers do not access that data. The default remains Python, so these gains require the experimental switch.

The pilot-close prompt targeted `geometry_page_field.blocks` discarding finite rule y support; FP8p above records its rejected trial and the new prerequisite. It requires a live producer/consumer repair, native c8 spanning-heading and finite-boundary controls, and deletion of the all-height rule interpretation. It preserves the established M33 endings/narrowings while missing-field and unruled multi-leaf domains remain debt. It does not retry the failed M33 replacement on unchanged inputs or build a new page model. Correct region inputs come before row/glyph/body and continuation consolidation. The five-iteration geometry maximum is unchanged.

**Integration boundary:** the coordinator merges these planning/measurement documents into the checked 54cc8f9 stack line. Do not merge 953fc4a, its crate, backend switch, build-dependent tests or bridge. The report and large replay evidence remain referenced at the parked worktree; a docs-only copy is optional, never a whole-commit merge. R8-GEOM-02 does not maintain Python/Rust parity with this historical implementation. Changed geometry contracts and witnesses go to R8-RUST-02, which must qualify any re-port against the then-current checked Python behaviour.

**R8-RUST-02 receives this explicit debt:** clean-checkout Python test collection must work without a compiled extension; explicitly requested Rust must fail clearly when absent. Commit the required build/link configuration, remove hard-coded interpreter/vendor paths, and qualify the target platform. Preserve the meaningful M17/gap-consumer tests; add the nontrivial sampled-before-dilation mutation and assert source-replacement targets were found. Label the 44 real crops as replay evidence unless a reproducible fixture-backed test is actually added. Diagnose the same-sign `shape_s`/`rows_native_s` downstream give-back (net 0.12–0.37 s on call pages). Reconcile requested OpenCV threads (2 in replay) with reported threads (10), repair the renamed `native_bands` census hook, and distinguish structural call/fallback counts from instrumented ones. None is a reason to merge the broken clean-checkout dependency now. On adoption, port current semantics and relevant callback/glue work, remove displaced live Python/bridge copies and retain one offline reference. Do not spend the later task automatically on M17: use its new profile to choose a substantial stable boundary, such as M15 field construction, and compare integration cost before expansion. Atlas validity remains R8-INK-02 debt unless the earlier Rust task touches that contract, in which case it must resolve it before use; M37's remaining full-plane cost stays with R8-RUST-02.

## Earlier accepted Python speed result

The planner read the full [R8-04-i1 independent check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-04-i1_check.md), worker report and current code. Its conditional acceptance is satisfied by the coordinator's private 44/44 identical result. Best head is 54cc8f9. Five live exact rewrites removed repeated M17 ordering/grouping/pair/cost work, M15 energy work and glyph/atlas preparation. Runtime +40 this iteration, -475 cumulative from d5dc3e2; definitions stay 6/9/9/7. All 208 exports (15,093 items) and non-clock evidence are identical; 278 tests pass plus one strict xfail. The independent 40-crop M17 comparison was exact, but is not a committed consumer test.

Field-stage gain is 5.1%/5.6%, total correction gain 3.3%/2.6% across the checker's 83 paired pages, with 0ce9 paired separately. The full 208 candidate is 199.421/1287.272/2007.555 ms median/p95/max corrections, with 22 above one second. The paired slow subset has 20→19 or 20→20; do not confuse that with the full-pass count. Field proposals still total 26.238 s, type 11.500 s and ownership 8.248 s. All 363 model requests are distinct within pages; do not claim duplicate inference to remove. Current profiles put native bands at 321 ms on 4959 p1, including 205 ms separation. The older 380 ms is not the Rust baseline. Native kernels and model work remain. These Python gains predate the Rust measurement and are not credited to the port; the broad Rust multipliers are now withdrawn above.

The pilot closed the M17 ownership/partition and actual gap-consumer weaknesses in its parked test tree, subject to the remaining mutation/collection issues above. The Python geometry base does not inherit those tests automatically; add relevant consumer coverage when its code is touched. Actual stale prepared-atlas membership/order tests and an enforceable contract remain with ink (a length check cannot detect same-length reordering); M37's remaining full-plane gap caller stays with final consolidation. None of these software contracts certifies a physical ink or row decision.

## Binding iteration allocation — owner relay, 12 October about 10:40 Athens

> OK talk with the planner we have adjusted the plan to keep pushing on some of the work
>
> ask them adjust the plan for the latest results, and also to give you the iterations allowed for each of the tasks.
>
> These are the max iterations each of the tasks will have this time.
>
> You coordinate the calles from now on.
>
> Make sure astra planner produces the prompt for every task iteration.

These are the maximum worker iterations for this allocation, not estimates or targets. Prior overnight iterations do not consume these new task maxima; they remain historical completed allocations. Stop a task early if it completes. After its maximum, close it COMPLETE or PARTIAL and move to the next task from the best independently checked head. A partial predecessor does not prohibit the next task. Failed or build-blocked worker iterations still count; internal debugging and the separate planner/reviewer turns are not extra worker iterations. Unused slots do not transfer and no task gains an automatic extension. Rejected code is not carried forward merely to use the latest commit.

| Task / purpose | Worker | Worktree / branch | Start head / dependency | Max iterations | Parallel | Close rule / carry-forward |
|---|---|---|---|---:|---|---|
| R8-RUST-01 — Measured M17 pilot, CLOSED DONE at i1 | `fresh` (pilot worker, completed) | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust` / `astra/ff-rust` | 54cc8f9 + this docs merge; after R8-04 | 2 (used 1; unused slot retired) | None | Measured result complete at 953fc4a; crate parked, runtime 54cc8f9 carried forward; build/test/timing debt to R8-RUST-02. |
| R8-GEOM-02 — Repair domains, rows and ownership; replace competing continuation | `01a12688-cfa4-7952-8edb-f98e8818f1ad` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack` / `astra/ff-r8-stack` | I5: b96cd9d + current docs merge, runtime equals 0474bf8; after closed R8-RUST-01 | 5 (used 4; last i5) | None | Complete: required native row/curl fixes and migrated/deleted policies. Partial: carry safe fixes, open owner cases and port compatibility debt. |
| R8-RUST-02 — Port substantial stable stages and consolidate the checked route | `01a12688-cfa4-7952-8edb-f98e8818f1ad` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack` / `astra/ff-r8-stack` | Best checked head after R8-GEOM-02; after R8-GEOM-02 and closed pilot | 3 | None | Complete: target route migrated, duplicate work removed, quality retained and speed gate met on this checked head. Later ink changes need fresh final qualification. Partial: enumerate Python remainder, unchanged policies and timing misses. |
| R8-INK-02 — Repair atlas contract and explicit frame/source/ink observations | `01a12667-cd89-7cc2-b180-81b44b989949` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink` / `astra/ff-ink` | Best checked head after R8-RUST-02; after R8-RUST-02 | 3 | None | Complete: supported source/frame decisions and old-policy deletion, preserved faint front. Partial: carry exact unknowns, retained legacy decisions and cost. |
| R8-AUDIT-02 — Audit both reviews, owner cases and measured final status | `01a12a41-405a-78e2-aa49-390c91867a97` | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review` / `astra/ff-review` | Best checked head after R8-INK-02; after R8-INK-02 across reset if needed | 1 | None | Complete: source-bound honest audit of attempted work and remaining cases. Open feature/performance gates stay partial; unstarted tasks are identified. |

**Order and concurrency.** Tasks run sequentially: geometry → Rust/consolidation → ink → audit, after the closed pilot. The stack worker owns geometry and the subsequent port; ink then consumes that checked head and rebuilds source anchors/calibration on its actual rows. The existing reviewer retains both-review context. The coordinator advances worktrees to the stated checked heads without resetting uncommitted work. No parallel workers or overlapping benchmarks. The ff-rust worktree already exists and remains parked. No worker is launched by the planner.

**Why this order changed.** R8-04 i1 found no duplicate whole-field build or identical inference request. Another broad exact-sharing pass is unlikely to close a roughly 50% worst-page deficit. The Rust answer is now available; spend the remaining early capacity on concrete geometry repairs before investing in a broader translation of their old behaviour. Ink's three iterations are a bounded renewed attempt, not a forecast that the 10+ category of source research will be solved. Move stable-stage port work before that investigation so source uncertainty does not postpone all target-language progress. All tasks still remove validated redundant or competing work when their replacement is ready.

**Resources, updated after the owner-authorised reset.** The weekly meter no longer limits the planned allocation. The runner still refuses launches at 97% and stops active runs at 99%. The coordinator pauses, preserves the source/evidence checkpoint and resumes after the reset when actual capacity is available. The former 95% early closure/two-point reserve and “Rust/ink unlikely this meter” forecast are superseded. No guard bypass, worker-triggered reset or cap extension. Interrupted unfinished work resumes within the same numbered iteration rather than consuming or creating an unrecorded extra slot.

Five of fourteen maximum slots are used, one unused pilot slot is retired, and eight remain: geometry 1, Rust 3, ink 3, audit 1. Continue the authorised sequence across the reset from each best independently checked head, even when the preceding task closes PARTIAL. The reset is not a promise that every task completes, nor a reason to keep repeating a falsified assumption. The next prompt still follows the worker result and independent completion/progress check; no later prompt is prewritten.

**Prompt loop, binding.** After every worker result and independent check, the coordinator brings both to the Astra planner. The planner writes the next iteration's full prompt, or the next task's first prompt when the current task closes. The coordinator checks (1) named existing code/callers, (2) compatible inputs, (3) removal and verification scope and (4) no new pipeline/page model, then launches that prompt unchanged except a coordinator header and declared placeholders. R8-RUST-01 iteration 1 is historical; only R8-GEOM-02 iteration 5 is the next launchable prompt now, subject to runner safeguards; i1–i4 are executed history. Later iterations/tasks deliberately have no prompt file and are not launchable until that loop supplies one. No success-assuming prompt chain and no worker self-launch. The coordinator retains its independent Opus check, native-page review and private 44; workers never see held-out data or outputs.

**Old R8-04 i2 is absorbed, not an extra task or extra slot.** Its M17 ownership/gap caller tests go into R8-RUST-01. Its atlas membership contract/test goes into R8-INK-02 before changed atlas use, or into the earlier R8-RUST-02 if that port touches the boundary. Its remaining M37 full-plane gap-cost caller and measured M15/native/type/ownership opportunities go into R8-RUST-02. R8-RUST-02 supplies clean-cohort and two-pass timing qualification; R8-INK-02 must refresh final-head qualification when subsequent runtime changes invalidate it, and the audit verifies that final evidence. Old R8-05 is superseded by R8-AUDIT-02 with maximum 1. The new table overrides their old two-iteration allowances.

## What we are doing

The owner clarified the two objectives on 12 October:

**A — Architectural consolidation.** Keep substantially the existing code and roughly its established useful behavior while giving measurements and decisions clear ownership and removing duplicate processes. Fewer repeated operations should make it faster; measure that expectation. Avoid gratuitous algorithm or output changes. Roughly preserved behavior does not mean preserving known errors or requiring identical polygons and bitwise output.

**B — Physical grounding.** Use the established explicit tools wherever they model the required page feature well. Where an in-scope feature lacks an adequate model, develop or improve a focused explicit tool, inspect what it detects on the raw page, then derive and measure the cheap heuristic against that detection. Each heuristic making a page-feature decision must have this grounding. Merely choosing a statistic that separates the current example images does not satisfy it.

Statistics remain useful estimators inside a stated feature model: for example, fitting a baseline through identified body contacts or estimating height from compatible letter bodies. A global component-height mode does not by itself establish letter height, and a density peak does not by itself establish a text row. State which physical quantity a statistic estimates, its assumptions, visual evidence and failure cases. This provides a reason to expect generalization; it is not a guarantee of it.

The objectives are complementary. Sharing an unsupported decision satisfies neither the full architecture nor the methodology goal. Replacing working code with a new detector without demonstrated need undermines A. Keep behavior changes tied to physical evidence, required corrections and measured speed improvements, and record consolidation separately from changes in decisions.

The end state is Paddle localization followed by shared measurements of the page, one account of its boundaries and row paths, one glyph/row ownership relation, and one construction of the final crops. Corrections run where measured evidence says they are needed. Initial Paddle boxes may be split, extended or discarded after their rows have been identified. Source ancestry remains explanatory metadata. Existing useful ink, boundary, typography and recovery work survives through this common route.

This is primarily consolidation and deletion, together with physical-feature work where the existing tools are inadequate. We cannot promise that deletion alone fixes the remaining slivers, lost initials or uncertain front/back ink. Those failures require an explicit account of what the existing detector got wrong. Develop the missing physical explanation when needed; do not substitute an ungrounded statistical row model or a stack of new guards.

## After G1

R8-01 failed honestly after 47 minutes and one revision. The [independent check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-01_check.md) confirms real letter cuts, lost Ψ and table numbers, a collapsed two-leaf spread, and false rows. Candidate `880aee0da37a481fc03b82f3d5eb45a153f5b662` stays off-default. Its component-height mode, contact-density peak rows and unanimous phase-vote ownership are rejected. Paddle localizations were stored but never consumed. None of `_discover`, `_pool_geometry`, `_assign` or `_make_lines` was reused. This did not test the owner's procedure.

The saved unmodified slow run already follows the curled endings on 8686 p5/p7, keeps Γ. Μαυρομιχάλης on 3229 p4, follows the 3229 p6 droop, separates e259's leaves, finds the 39 printed rows on 77d1, preserves 7a2b's “32” and keeps the weak τῆς inside its column on 31f40. These are checked examples, not a declaration that the entire slow detector is correct. Its slivers on 3229 p6/ffccc, misregistered 4959 p4 line, missing Ψ and small end clips remain local repair obligations. The tables and many marks were not inspected by the G1 reviewer.

The first revision proposed a separate slow-reference construction task. That attempt ran at `1eae16f` and failed through an incompatible Paddle seed substitution, detailed below. Its launch brief and input substitution are superseded. R8-01b now starts the actual consolidation: select existing feature providers, share their measurements, migrate consumers and remove duplicate computations. G1b checks that scoped architectural result. The still-unmet row/curl quality requirements move explicitly to G3, where row decisions are replaced; they have not been passed or waived. The failed G1 remains failed.

R8-02 through R8-05 are all rewritten. 02 consolidates ink consumers using existing native references; 03 consolidates the existing stack geometry, using the actual pixel-seeded slow functions only as offline reference; 04 finishes cost reduction and removal; 05 audits both reviews. No task depends on a new `physical_page.PageContext`, a new universal reference, or acceptance of 880aee0. The failed worker is not resumed. The existing stack worker owns architecture, row integration and speed, with the existing ink specialist and reviewer: three workers, five sequential prospective tasks.

## Iteration loop — historical overnight allocation

The owner authorised the overnight loop on 12 October at about 01:20 Athens, relayed by the coordinator:

> If so you can keep working on it with the planner, iterating at the end of each task.
>
> This task can have at least 3 more rounds, and if there is significant progress by then 2 more.
>
> If compelted you can move on the rest of the tasks, each task has 2 iterations each. If one doesnt compelte you dont
> stop, you move to the next one; and I will review the results for each in the mornign

This supersedes earlier instructions to stop the whole sequence at an incomplete gate or seek permission to start the next task. There are no per-task clock or meter caps. Each iteration ends with a coherent candidate/report, independent check and a planner-written next prompt. Internal debugging attempts are not separate iterations. The coordinator checks each prompt and launches it unchanged except declared placeholders and the verbatim authorisation. No worker self-launches its next iteration.

| Task | Iteration allocation | Transition |
|---|---|---|
| R8-01b consolidation | Closed PARTIAL after iterations 1–4. Criteria 1/3 FAIL, 2/4 PASS; 5–6 not authorised. | Best checked head cb4d6b4. Advance to R8-02 with explicit physical failures. |
| R8-02 ink | Closed PARTIAL after i2; no third ink iteration. | Best checked head fb03df1. Carry M55/M35/DN/source debt and narrow glyph-preparation reuse to 03, speed debt to 04. |
| R8-03 rows/geometry | CLOSED PARTIAL after i2; no third geometry iteration. | Best checked head 5961754, runtime equal to 23ee49c. No M33 removal; NaN-consumer test added. Carry domains, missing/clipped rows and finite-y bug explicitly. |
| R8-04 speed/removal | I1 accepted at 54cc8f9, G4 PARTIAL. Old i2 superseded/absorbed. | Its remaining work follows the binding Rust-first table above; there is no standalone R8-04 i2 slot. |
| R8-05 audit | Two iterations. | Audit the actual partial or complete result; second iteration can resolve evidence gaps. Produce the morning report with all remaining failures. |

**Carry-forward rule.** Task order is a scheduling dependency, not a prerequisite that every earlier quality gate passes. At each handoff the coordinator records (a) the latest tested candidate, (b) the best independently checked head, (c) the task's completion status and (d) defects/uncertain contracts still open. The next task starts from that best checked head, which can be an earlier iteration if a newer candidate regresses. A safe partial change can become the working base without being called a completed task. Keep unsafe experiments committed separately with their evidence; do not carry new glyph losses or unsupported exclusions merely to follow the latest commit. A merge into ff-merged is a separate coordinator decision, not necessary for candidate continuation.

At consolidation close, iteration 4's `cb4d6b4` was the best independently checked head; G1b remains PARTIAL and consolidation is closed. The full check is FL/review_r8/R8c-01b-i4_check.md. It preserves 208 output/stage evidence, removes 368 duplicate native mean filters through `retention_ink`, and restores M35 full-strip validity semantics. Runtime is −540 lines cumulatively from d5dc3e2; paired overall timing is neutral. The coordinator confirms private 44 identical. Definitions remain 6/9/9/7 and the two DN policies remain two. The shared calibration failed native paper-sample assignment and the independent-noise assumption; blank plateaus and blocky near-white raster variation became support. Criteria 1/3 fail, so iterations 5–6 are not authorised. R8-02 iteration 1 started from cb4d6b4, using existing native frame/source evidence to remove unsupported decisions, with M55 centre ownership as its first target. The DN-mask debt stays with 02, but another variant of mean-paper darkness versus bright-neighbor independent-noise calibration is forbidden. Body row/class/height attribution stays with 03. No new pipeline or page model is authorised.

R8-02 iteration 1 was independently accepted as best head `3b09d57`; the coordinator's private 44 also remain unchanged. Its complete M06 neighbour-row propagation deletion removes one unsupported source subpolicy (2→1), net −11 runtime lines and −551 from d5dc3e2. All 208 exports/exclusion polygons remain identical. It does not complete M55: the native whole-support attempt explains 10/57 approved removals, missing joined/fragmented flowers and marks. The i2 brief targeted that observation and the real caller migration first; its checked outcome is recorded below. The check also found 0ce9's eight-row M35 calibration population changed, now including ghosts; faint forward-reading fragments #34/#36 must be distinguished from the mirrored examples. I2 audited the actual sample contributions without another calibration variant. The real +195/+216 ms cost on 0ce9 raises the development >1 s count to 22; only exact-input sharing may reduce it here, otherwise 04 inherits it. M20 deletion was rejected on the lost front word “ἀποξήρανσίν”. These are explicit debts, not grounds to restore propagation. R8-03 starts from the best checked head after i2, with source uncertainty, actual M55 status, current M35 population and no claimed measured body provider. No third ink iteration is authorised.

R8-02 closed PARTIAL at iteration 2, accepted best head `fb03df1`; the coordinator reports private 44 identical. I2 shares only exact native threshold/CC preparation across B5 calls, with fresh height-dependent selection and source votes. Net runtime is −523 from d5dc3e2; 208 output/exclusion/stage evidence remains identical. The measured saving is about 5 ms on 0ce9, with at most 6 pages reaching the reuse path. M55 is unchanged: the offline grouping attempt explains 14/57 removals; 19 of the 43 remaining crops fail on at most 10 unresolved pixels, including 7 on one pixel. This is partly an unresolved speck/support model, not simply more failed grouping. No tolerance or rejected frame provider is authorised. M35's population record is honest but source/class validity remains unresolved; M20/DN and mixed-tail debt persist. The 21-page full-run / 22-page accepted slow union and about +200 ms 0ce9 debt go to 04.

R8-03 i1 had a concrete removal target: replace M33's independent per-box end continuation with the checked existing M15 shared deformation and native row contacts. Trace early field selection and late row/clipping consumers so bypassed or lost rows cannot be called fixed. The seven-entry inventory (M11/M15/M19/M20/M22/M33/M37) distinguishes nominations and physical decisions; a new provider beside all seven, or retaining the old path under a fallback, is not a definition reduction. Pixel-seeded slow `_discover/_pool_geometry/_assign/_make_lines` remain offline reference only. The fast stack must represent native residual rows without mandatory Paddle ancestry, recompute B5/M35 census-dependent decisions after regrouping, and establish body/class evidence before claiming measured guides. That brief required actual caller migration, full pilot/regression evidence and a precise i2 failure ledger. Its failed migration and the narrowed final-iteration work are recorded below. No new pipeline or page model.

R8-03 i1 is independently ACCEPT WITH NOTES at `23ee49c`; the coordinator reports private 44 identical, so it replaces fb03df1 as best head. It keeps only the finite inverse-domain correction: NaN outside the monotone mesh, with render/certify skipping unknown phases. Runtime +13/−5 (−515 cumulative from d5dc3e2), 208 unchanged, no removal or owner fix; all seven path authorities remain. The certificate's NaN skip has no direct test yet. False phase candidates remain, and 4959 p4 gains another in blank paper; mathematical domain correctness is not physical improvement.

Both M33 trials were rejected. The next prompt distinguishes wrong domains/row placement (9ea #131, dbd #25, d323 #23 and p5 row 5) from failed retention followed by a shorter incoming-box fallback (466 #0, 7792 #40 and c8 #87). I2 reuses existing `geometry_columns.analyze` evidence, M15/M17/M18 and residual machinery; it adds no gutter or page model. Its scope is one complete M33 continuation removal, globally or throughout an independently defined physical population, with all six crops and p5/p7 controls checked. No old tangent remains inside a claimed migrated population; global counts must still include it elsewhere. It supersedes the broader i1 proposal to refactor M17/M18/M37/M38 as additional projects. Add the missing `certify` NaN-consumer test. If a removal cannot preserve the accepted text, keep 23ee49c's runtime, record the first failing assumption and close G3 PARTIAL after i2. Tests/docs-only work can accompany that unchanged runtime. R8-04 inherits the actual best checked head, the named 22 slow pages, 0ce9's inherited cost and all unresolved geometry/ink obligations. No third geometry iteration.

Current no-seed account: p5 row 5 remains absent because regional proposal 34 straddles rows and is unowned; rows 40/41 are present but their curled tops remain partly clipped. P7 “ἀμπέλων” and row 40 already existed before geometry and are preservation controls. The c8 tick is of uncertain identity, not a certified accent. The current review also confirms “32” remains grouped with 30/31 and ffccc's wide-gap last word remains absent; inherited optimistic descriptions are not new fixes.

R8-03 is CLOSED PARTIAL at accepted `5961754`. All 190 runtime hashes equal 23ee49c; the meaningful NaN-consumer tests fail under the isolated mutation and pass on the actual function (273 tests, one strict xfail). The coordinator's private check is inherited by runtime identity, not presented as a new run. There was no live retry or removal in i2. The 40 M33-trigger pages contain 14 useful refinements on nine pages; 466/d323/dbd have no M15 field, 9ea has no accepted column rule and c8's heading spans above its finite rule. No supported migration population was established. All six rejected outputs fell back to the incoming boxes, losing useful endings or narrowings. No newly complete πό- is claimed: the tiny trailing mark already lies outside the accepted crop. Runtime remains −515 lines cumulatively, with definitions 6/9/9/7 and all seven path authorities.

R8-04 starts with objective A: the existing code and useful behavior, fewer duplicate processes, measured savings. The real cost leader is M15/M17 field proposal (26.916 s/208, top stage on 19 of 22 slow pages), then type (11.390 s), row ownership (8.047 s), ink (6.018 s), early field selection (4.471 s) and row splitting (3.759 s); clocks nested inside those totals are not added. M33 costs 2.452 s and stays as useful code. Each supplied profile builds M15 once, so do not invent whole-field duplication. I1 removes repeated invariant computation/native scans in the dominant route and then the next demonstrated duplicate, including exact glyph/atlas preparation where useful. Existing sharing and changed-census invalidation remain intact. A faster equivalent feature calculation is permitted; output identity is not a blanket restriction. Each removed active path is checked against native controls and accepted full output.

The located `geometry_page_field.blocks` finite-y bug (lines 29–31) stays geometry debt for the owner's morning review. It consumes a finite rule as a full-height median-x cut, notably above c8's rule. Changing that partition affects physical row domains and is not necessary for exact-input sharing or removal of repeated arrays; speed does not reopen geometry. Record full finite rule/region/mesh dependencies in reuse so a later fix cannot use stale observations. If a shortcut requires changing the partition, reject that shortcut and continue independent speed work. No claim that the existing domain is certified, harmless or fixed. The i1 prompt names the first concrete cost changes, all preservation controls, one fresh 208 pass plus paired timing for a partial result, and the two fresh full passes required for any G4 pass. I2 is judged on the remaining measured work and the clean/every-page targets. Carry the named 22 slow pages, 0ce9's +200 ms debt and all G2/G3 failures through to audit.

Every successor reads an `ITERATION_HANDOFF` record with the inherited failures, next repair owner, exact evidence and which measurements remain provisional. If a missing dependency prevents one change, keep the last checked behavior for that part, expose its limitation and do the next independent work. The morning report distinguishes preserved known failures, newly fixed cases, rejected regressions and unknowns. Move on after the allocation without erasing failed gates. Only real access/resource constraints or an explicit owner change interrupt the whole loop; unsupported scientific branches are recorded and abandoned while other authorised work continues.

### Significant progress after iteration 4

**Decision recorded:** these criteria were applied at cb4d6b4: FAIL/PASS/FAIL/PASS. Consolidation is closed PARTIAL; 5–6 are not authorised. The original rule is retained below as history, not a pending allocation.

At the iteration-4 check, “significant progress” means the best checked candidate has all of the following, measured cumulatively against iteration 1 (`d5dc3e2`):

- A real reduction in active, independently chosen feature definitions or decision policies, beyond merely merging the algebraically equivalent product/division spelling. At least one additional redundant mask or height decision must be gone, with all its callers migrated and the surviving physical meaning checked. Count decisions/populations, not wrapper function names.
- Zero-reuse cache machinery has actually been removed or replaced by plain shared operations, with a source-level runtime deletion receipt and lower redundant execution. Report additions, deletions and net runtime lines separately; moving code, minifying it or leaving dormant alternatives does not count. Net-negative runtime lines are the target. If a necessary physical provider makes the net positive, the coordinator must explicitly justify that exception from the eliminated decisions and measured work; line count alone cannot grant continuation.
- Letter-body attribution has advanced beyond labels and plots: the clipped 4959 p1 measurement and a tall/joined-component case (3229 p6 or 31f40 p1) have physically checked complete-body support, and at least one real consumer uses the resulting justified measurement or explicit measured/borrowed/unknown distinction. Simply adding `uncertain=True` while using the old value as body height does not count. If height remains partial, an independently checked ink-feature improvement that replaces an unsupported runtime decision can establish physical progress instead; explicitly carry the unfinished height cases. Diagnostic plots alone are insufficient.
- Native text is preserved in a source-bound full 208 pass and independent review, including historical recoveries and changed crops; no new unresolved loss is carried as progress. Stage work is measurably reduced; a wall-clock gain is reported only if paired measurements distinguish it from noise. A stable overall time with demonstrated removal of redundant work can qualify; a material unexplained slowdown cannot.

If these hold and useful consolidation remains, iterations 5 and 6 are authorised. Otherwise advance to 02 with the best checked head and honest partial findings. If consolidation completes earlier, advance immediately. These are review criteria for allocating the extra iterations, never runtime thresholds or page-specific rules. Independent Opus and the coordinator decide; the worker supplies the receipts.

### Corrected reference and sequencing

The earlier reference attempt `1eae16f` actually ran and failed. It fed tight original Paddle line polygons into `_discover` through `PixelPage.boxes`. `_discover` expects rough multi-line pixel regions and fully contained components. Tight boxes discarded curled support; missing Paddle rows were omitted by `_recover_bodies`'s `if not segments: continue`; short fitted spans were then extended with capped straight slopes across neighbours. This explains lost full rows on 8686 p5 and mixed/lost rows on p7. Read FL/round8/CATCHUP_FOR_PLANNER.md and the full FL/review_r8/R8-01b_check.md. Neither failed candidate (`880aee0` or `1eae16f`) is an implementation base.

R8-03 now uses the unmodified **pixel-seeded slow construction as its offline physical reference**, preserving its actual discovery contract and known local limitations. Paddle remains actual localization input to the fast route. Its boxes nominate text and observed pieces, not the exhaustive universe of rows or permissible ink. Do not feed tight Paddle polygons, or cosmetic padded versions of them, into the slow region-discovery API. The fast route must retain native/residual hypotheses for rows with no Paddle parent and replace its own independent end continuation with one checked shared page/column bend across the valid domain. `_at`'s capped straight extrapolation explains the failed slow adapter; editing that offline function alone is not a runtime replacement. No full slow detector in the timed default path and no new universal model.

R8-01b iterations 2–4 attempted the letter-body attribution work needed to replace misleading height estimates, but established no runtime body-height provider. The remaining row/class/source attribution belongs to 03. Existing `pixels.prepare_pixels`, `font.evidence` and `fit_guides` give explicit class contacts, but depend on row identity, scale and complete component ownership; those inputs must be checked and provenance recorded. The failed scalar fit must not be promoted or renamed by 02. Full row reconstruction and body attribution remain 03's task; 02 keeps its inherited height assumptions explicit while verifying ink/support exclusions.

## The method required for every physical decision

Each task adds to one concise `FEATURE_OWNERSHIP.md` and machine-readable companion, not another broad review catalogue. Each feature record names:

1. The actual page property and units: for example, small-letter body height, finite rule support, the four font guides, or weak ink relative to compatible front print.
2. The existing or specifically developed explicit function and native rendering used to observe it, the raw crops checked, known counterexamples and the limits of that explanation.
3. The selected runtime provider and its consumers, with source pointers. Several different quantities may share observations; they must not silently share a misleading scalar.
4. The cheap heuristic, precisely which observation it approximates, and the comparison including positive, negative, rejected and quiet cases. A quiet scout is checked by bypassing it for the reference, so shared omissions remain visible.
5. The competing computations and decision passes removed or replaced, remaining migration debt with its task, and the evidence that their useful text has survived.

Use existing saved reference outputs when their inputs and source match. Render or run only the missing comparisons. First check that the explicit detection describes the raw page; then compare the heuristic with it. Agreement with a wrong slow answer is not success. A component is not automatically a glyph, a detector polygon is not automatically a row, and pale ink is not automatically back print.

The common model means common authority, not one forced scalar or one new monolithic class. Body height is measured for compatible local typography; headings and large initials are not squeezed into a page median. Ink measurements share paper/contrast observations but preserve the distinction between darkness, stroke damage, reflection evidence and source uncertainty. Native component support, coordinates and finite boundaries have a single documented meaning. Geometry uses one bend field within valid leaf/column domains, with row-specific guides. Whole glyphs and attached marks have one final row/cell owner. Cheap nominations may coexist; competing final answers may not.

## Existing code to keep, compare, replace and delete

The charter calls the slow detector “neither ground truth nor a design to copy.” The new evidence warrants reuse of demonstrated stack functions and direct inspection of the slow construction as an offline reference, with source lineage and local comparisons. It does not warrant copying every threshold, running the whole five-second detector on every page, or trusting its table and initial handling without inspection. `greekocr/` remains unchanged. Import the page-line functions only in offline references with their pixel-seeded inputs. Runtime work consolidates the existing stack providers; do not copy the slow detector into another pipeline.

The feature table retains the physical obligations. The closures above record what was actually achieved; unmet consolidation/ink/geometry objectives remain debt for the owner, not prerequisites or extra reconstruction tasks for speed.

| Feature | Existing explicit reference and preferred starting point | Cheap comparison | Consolidation/deletion and owner |
|---|---|---|---|
| Paper, ink support and local letter scale | Native component/contact preparation; `shared/ink_faintness.py` dense components/reference, `shared/type_profiles.py` explicit measurement, slow pixel preparation and `pages/font.py` guide fits. Check the known box-height/body-height mismatch, mixed fonts and initials. | Compare actual support, body guides and local height, including weak/short/connected text. A faster census must retain the relevant observations. | 01b shares preparation and measured scale, migrates callers and removes duplicated equivalent work. 02 reconciles ink calibration; 03 completes row/font consumers. M03 box height loses physical authority. `ink_normal.follow_letters` is an off-default rejected experiment, not the selected normal-ink model. |
| Front/back ink, faintness and stroke condition | Existing dense ink, reflected glyph, rim, motif, disk/counter and frame renderers in `features_ink` and `shared/ink_*`. Inspect raw pale fronts and mixed rows. | False front deletions, missed ghosts and endpoints on quiet/positive scouts, with the same native support and compatible print reference. | 02 removes incompatible calibration and repeated classification/recovery filters. Retain useful specialized physical evidence; replace M55 centre-in-frame ownership and whole-row-only treatment of mixed tails. Do not collapse distinct features to brightness. |
| Leaves, columns, finite rules, gutters and cells | Existing Q8 native rule/flank checks M05, bilateral termination M13, geometry regions/curved rules, and slow `boundaries.py`/`layout.py`; inspect unruled columns and tables as well. | Compare where a boundary actually exists, its endpoints and the text/cell assignments it changes; include boundaries above a visible half-rule. | 01b shares native observations; 03 makes one finite-layout owner. Remove independent whole-table/region vetoes and invented rule-end slabs. Keep supported witnesses; a missing rule is not permission to cross a column. |
| Bend, skew, four font guides and row identity | Execute `_discover`, `_pool_geometry`, `fit_guides` and their supporting slow construction; use existing fast contact/path primitives only where measured against those physical curves. Saved R8-01 slow runs are the initial evidence. | Full native curves and one-to-one rows within leaf/column/cell, unmatched rows, guide error, whole glyphs and endpoints. Include 8686 p5/p7 and quiet scouts. | 03 attempted consolidation against the pixel-seeded offline reference but removed no path authority; M33 and all seven remain. 04 can remove repeated calculations in these providers, preserving their useful support. No new contact-density peak/phase-vote model. |
| Complete ownership, curve search, missing rows and final crops | `_assign` assigns components beyond seed boxes; `_make_lines` follows their extent; `_boundaries` uses neighbours; existing residual contacts find missed text. Check accents, descenders, short numbers and initials. | Whole glyph/mark ownership and final native/normalized crops, all owner marks, earlier accepted recoveries, real words beyond gaps, no partial neighbour letters. Native ink unions are diagnostics, not truth. | 03 replaces M17/M18/M21/M23/M28/M31 and independent M36–M38 policies. Delete parent retention/subtraction, conflicting join/completion decisions and destructive late clipping after common ownership accounts for their useful text. |
| Whether work is needed and how much it costs | The accepted explicit feature observations above, evaluated independently of the cheap dispatcher. There is no new physical feature called “needs correction.” | Scouts on all relevant positive and quiet controls, full changed-text review; end-to-end correction timing including every native operation and extra inference. | Every task removes waste. 04 verifies dispatch and removes demonstrated repeated observations, exact repeated inference and obsolete orchestration through explicit passing. A once-built field is not a duplicate. A regional Paddle rerun may remain only as a uniquely useful locator with measured cost, never as row truth. |

The prior A grades (M05/M13/M22) are narrow useful evidence, not a certificate for their whole caller. The 26 B mechanisms largely already have explicit feature work: complete their missing comparisons and fix demonstrated causes, rather than rewrite them all. The five C mechanisms need a checked physical decision in their place. Necessary D machinery—decode, Paddle localization, ancestry and scheduling—can remain as engineering. Unsupported D decisions about rows and ownership must go. The complete per-ID map below prevents this distinction from becoming a blanket deletion of useful code.

## Tasks, order and workers — historical Python-first sequence

| Task | Worker and purpose | Concrete handoff |
|---|---|---|
| R8-01b | Stack thread, ff8-stack / astra/ff-r8-stack; closed at cb4d6b4 after i4. | Checked code/kernel removals carried forward; physical criteria failed. DN-mask debt to 02, row/class/body-height debt to 03. No iterations 5–6. |
| R8-02 | Resume ink `01a12667-cd89-7cc2-b180-81b44b989949`, track ff8-ink, existing ff-ink / `astra/ff-ink`, after the consolidation allocation, complete or partial. | Remove and verify existing ink decisions, starting with M55 complete frame support and the M35/M06 source audit. Preserve native specialized evidence; carry the DN-mask failure explicitly without retrying its falsified assumption. Closed PARTIAL at fb03df1 after i2; native glyph-preparation sharing is accepted, but M55/source/DN failures persist. No third ink iteration. |
| R8-03 | Resume stack, same candidate worktree; allocation closed after i2. | CLOSED PARTIAL at 5961754, runtime 23ee49c. Only inverse-domain correctness and its consumer test were kept; no path removal or owner geometry fix. All unresolved obligations go in the closing ledger. |
| R8-04 | Resume stack from checked 5961754; two iterations. | Implement the cheaper existing feature calculations and remove actual repeated work, first in field proposal. Keep M33 refinements and all ink/recovery controls; finite-y bug stays geometry debt. Measure clean-page/every-page timing and hand actual residual cost to i2/audit. |
| R8-05 | Resume review `01a12a41-405a-78e2-aa49-390c91867a97`, track ff8-review, existing ff-review / `astra/ff-review`. | Concise source/evidence audit of both reviews, all owner records and actual final timing. No implementation. |

The stack worker knows the compose order, repeated computation, timings and previously lost recoveries; that history directly helps deletion. Its harmful inherited constraint was exact output preservation, explicitly removed here. It must read the slow-code call sequence and G1 check instead of assuming previous integration choices were right. The ink worker knows the native controls and its own pale-front failures; it must migrate decisions, not protect its old scalar or guards. The reviewer knows both review ledgers and the difference between a physical model and clean software; it produces a closure audit, not another census. Independent Opus remains separate from these three workers.

Do not resume the failed model agent for a third construction. Do not split typography, curvature, rows and recovery between separate implementers: that recreated competing ownership. The long geometry and T2c histories remain required evidence of narrowed briefs and failed partitions. The type chat includes later recovery/initial work despite INFRA's shorthand “idle since round 4”; read the actual handoffs. All tracks run sequentially, all parallel groups are null, and no subagents/background jobs are requested.

Coordinator: start ff-r8-stack from checked 5961754 plus this planning-docs merge and pin `<HEAD>` to that launch head. Verify runtime identity and set cwd explicitly. G2/G3 are CLOSED PARTIAL; R8-04 has two slots. After i1, return the result/check to the planner for i2. Carry only the best independently checked speed changes and advance to audit after the allocation even if G4 is partial. Do not import planner commit helpers into worker trees. Later pin each best checked working head and carry its partial ledger. Exclude rejected 880aee0/1eae16f and the falsified i4 calibration. Never reset uncommitted work. The stack worker continues with 04 after the closed geometry allocation; it must use its assigned candidate cwd. Reports/independent checks carry the handoff between workers.

## Scope and owner evidence

The frozen R7 ledger has 104 comments: 50 fixed, 24 partly fixed, 27 not fixed, 3 outside scope. Its 256 marks contain 97 “one” controls and 159 “two” marks: 25 fixed, 45 partial, 88 not fixed, one parked orientation case. R7 inherited the row verdicts unchanged from R6. The 62 unmarked contexts are not owner marks. Both complete appendices below are preserved; grouping cases in this plan does not replace the original comments or marks.

02 owns faintness O08–O12 and decorations/ink portions of O17–O24 plus every older related comment. 03 owns A/B/C, O01–O07, O13, O15–O20, C01–C04 and all geometric/row cases; mixed cases use 02's evidence. All previous successes are regression obligations, including c0b02 #118, d83 #108 and 3229 p6 #26. Restore the R5 additions lost in R6 on 3229 p4 addition 0 and 4959 p1 additions 0/11. O16's new line under 108 is not the already recovered 108. Keep whole table words, weak endings, short words and large initials.

The R8 pilot is the existing 23-page manifest in the failed candidate's evidence, with 127 owner marks; it is a convenient starting subset, not a new evaluation truth. No need to reconstruct a universal reference to use it. 03 must inspect all 23 and all 127 marks, including the previously unchecked tables, before the complete 208 run and all 256-mark handoff. Account for the slow reference’s slivers (3229 p6 row 38, ffccc row 47), 4959 p4 rows 28/29 offset, missing Ψ and end clips against native pixels; require the fast candidate to handle these correctly. Trace first wrong contacts/row identity/ownership, without deleting thin rows or adding height/count gates. This does not require a separate slow-detector repair project. Glyph loss remains failure even if row counts look right.

R4-12's stale blob verdict and O24's later fixed verdict need current evidence. O25/R4-10 “6,7,” needs an owner interpretation if it affects an action; do not invent one. O26 and the single orientation mark remain parked. The coordinator may bundle the ambiguous wording with its concrete crop in the owner report; it does not block independent work. General font identity/book borrowing, under/over-inking versus back-print separation, script-adaptive guides, image/caption recognition and borderless/spanning-table semantics are not automatically solved by this refactor. Record limits honestly; if one prevents an in-scope owner fix, that fix remains open and the quality gate fails.

## Coordinator checks and stop rules

Candidate commit → independent Opus source/report/image check + coordinator eyes + coordinator-private 44 → record best checked head and task status → planner's next prompt → coordinator launch. Do not merge before review. A self-reported DONE does not select the next head; an incomplete gate does not cancel the next authorised iteration/task. Run the actual changed candidate on 44, not only an unchanged default. Held-out pages and outputs never reach the agents; only abstract failure classes may be returned, with analogous development evidence used for diagnosis.

| Gate | What must be checked | What a pass means |
|---|---|---|
| G1b after 01b | Read the provider/deletion map and actual callers. Selected measurements must describe native controls and agree with their explicit references on positives and quiet cases. Verify one preparation per required representation, truthful units/local scale, no new model and no real-text regression in a fresh candidate 208 pass. Inspect changed native crops; compare preserved owner records. | Shared measurements are consolidated. Known unchanged row/curl failures remain explicitly pending G3. This is not a retrospective pass of failed G1 or acceptance of a new reference. |
| G2 after 02 | Native ink/scout comparisons, all named pale-front/mixed-tail/frame controls, actual calibration consumers, exclusions, removed repeated filters and every changed crop; fresh 208 candidate regression and private 44. | Ink consolidation and its scoped fixes pass. If a required source/cutoff distinction remains unsupported, keep G2 partial, finish independent authorised work and advance to 03 after the two ink iterations with explicit failures for the morning report. Do not pass the problem to geometry disguised as certain ownership. |
| G3 after 03 | Prove the offline reference keeps pixel-native seeds; Paddle is consumed by the fast route without tight-box substitution; native residual rows survive with no parent; the existing shared page/column deformation replaces a named independent runtime path decision (M33 is the final-iteration target, globally or within a completely migrated physical population); compare actual reused features, local repairs and cheap/native decisions. Verify all four launch requirements and distinguish full authority removal from partial caller migration. Inspect all 23 pilot pages/127 marks, then all 104 comments/256 dispositions and every changed or still-open crop from a fresh 208 run. Check all old accepted recoveries, columns/cells and complete glyphs. Verify obsolete row/field/overlap policies are removed from the candidate path. | Owner curl/search/single-row obligations are fulfilled on the development evidence without unexplained loss. All in-scope geometric marks must pass; no quiet omissions, third model or known-wrong fallback. This establishes G3 completion; speed work is also scheduled after a partial G3, carrying its open defects separately. |
| G4 after 04 | Two fresh full 208 runs, reversed page order in the second, all correction work charged. Every page below 1000 ms in both; inspect all changed crops/controls and quiet-scout misses. Measure verified-clean pages against Paddle-only and show distributions. Audit removal and final compose order; private 44. | Quality retained under the new algorithms and final speed target met. “Negligible” must be judged from measured absolute overhead, not detector agreement or a newly invented percentage gate. |
| G5 after 05 | Opus checks the auditor's source/evidence claims, coordinator views final pages and runs final 44 on the exact runtime commit. Confirm all 44 old mechanism dispositions, 20 checklist entries, owner records, deletion receipts and remaining uncertainties. | Report the actual complete/partial result to the owner. No production or Rust migration is implied. |

Every changed physical feature gets the explicit-reference/heuristic check in its implementing task, not only a methodology audit at the end. Compare ordered one-to-one rows within each leaf/column/cell, unmatched rows on both sides, guide/endpoint errors and complete glyph/mark ownership. A reference row may not be reused to match several candidate rows. Exact array/old-output equality can verify a mechanical refactor; it cannot certify physical correctness. Native union, duplicate counts and tests are likewise supporting checks.

Quality gates govern task completion and which candidate code is safe to carry forward; they do not veto the owner's authorised task sequence. Within an iteration, continue evidence-backed work without clock caps. New glyph losses, wrong domains and false exclusions block carrying that regression into the working base. Diagnose and repair them, or retain the earlier best checked head and record the rejected candidate. At the iteration boundary, send the coordinator the result/evidence for independent review and the planner's next prompt. Foundational failures and missing evidence enter the carry-forward ledger; abandon the disproven branch, do other authorised work and advance after the allocation even if PARTIAL. A third variant of R8-01's rejected density/phase assumption remains forbidden.

Existing empirical constants must be documented and tested, not relabelled physical laws. Add no case-specific, count, percentage or size guard to rescue a wrong feature model. Numerical/statistical methods are allowed when their relationship to the modeled feature is explicit and checked. A focused missing-feature tool is legitimate work toward objective B; replacing the entire detector without evidence of that need is not. The coordinator retains independent review and the actual shared-resource limits.

A task cannot claim consolidation merely because it adds a shared object. Its handoff lists removed calls/policies, retained specialized evidence, and why any apparently duplicated operation measures a genuinely different quantity. Dead code and offline renderers are distinguished; preserve reproducible reference evidence. A useful second locator is not deleted blindly: compare its unique recovered native text before removal. The one-authority requirement concerns physical decisions, not an arbitrary file-count reduction.

## Time and weekly meter

R7 correction timing was about 190 ms median, 1.30 s p95 and 2.00 s maximum; the same 20 pages exceeded one second in both passes. The 40 detector-agreement pages still had roughly 61–63 ms median and 538–548 ms p95 overhead, and agreement did not establish they were clean. Those are the baseline costs to improve, not accepted final targets.

The earlier 48% meter figure predates the latest run. The R8-02 iteration-1 report records 71% at launch, R8-03 i1 records 75% and i2 records 78% at launch; none is a current meter query. The coordinator checks live shared capacity before each launch. Do not treat the old single-pass forecast as the cost of this loop.

Working estimates per iteration remain roughly 1–1.5 h for consolidation/ink, 1–2 h for speed, 2–3 h for row integration and 0.5–1 h for audit, plus independent checks. If every remaining unconditional slot is used (two each for 04–05), that is 4 worker launches and roughly 3–6 worker hours, before coordinator checks; early completion can shorten it. Consolidation iterations 5/6 are not authorised and add no allocation. These are deliberately visible estimates, not deadlines or assurances of overnight completion. Reuse unchanged evidence and stop redundant benchmarking; report actual duration/cost after each iteration.

No per-task clock or meter cutoff is introduced. Actual platform/shared-resource constraints, including INFRA's 95% runner limit, still apply. The coordinator forecasts remaining capacity across all tasks and records any unavoidable resource interruption in the morning report; the owner's instruction to move on from partial tasks remains the scheduling rule. There is no pre-authorisation request between the listed tasks/iterations. Additional work outside this allocation needs a new owner decision.

The owner clarification is preserved verbatim:

> I wouldnt necesserily cap the task ... it might require more time
>
> Our goal is to create (A) basically the same code with roughly the same behaviour but more architectonically sound and we would expect it to be actually faster because of the fewer duplicate processes and (B) to actually try to build or use established tools we have built that are actually modelling features of a page that we can expect to generalize, and make sure that all the heuristics we use are grounded on tehse and not general statistical properties of the images we are processing. correct?


## Reading and evidence basis

Read the two R7 reviews and JSON ledgers, old assignment, task reports/independent checks, charter/research/stack docs, owner ideas/full messages, coordinator lessons/INFRA and relevant chat exports. The preceding planner passes read all 30 exported chats' instructions and handoffs; raw rollouts were not exhaustively replayed. This rewrite uses the saved G1 check/report/source and earlier native image inspections; it makes no new OCR, timing or full 208 visual-review claim. The exact source record remains in git and the linked evidence.

R8 sources: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/round8/`. Failed candidate evidence, including the unmodified slow 23 controls: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/`. Its saved `inputs.json` is the pilot/input lineage source, not runtime data. Default baseline and full owner records are the R7 gallery linked in the appendices. No held-out page was accessed by this planner.

## Every old assignment item has a destination

The old checklist supplies obligations, not a mandate to retain its architecture.

| Item | Current disposition |
|---|---|
|2b-01|01b/02: share measured observations, local scale and calibrated ink; preserve the distinct physical quantities.|
|2b-02|01b/03: reuse finite boundary evidence and one layout owner; remove unresolved-column keep-all surrogates.|
|2b-03|03: reuse checked slow curves/rows/assignment; consolidate existing geometry consumers.|
|2b-04|02/03: search to physical boundaries, classify ink consistently; no three-body or radius gate.|
|2b-05|03: reconstruct rows independently of initial partitions; delete parent-leftover subtraction.|
|2b-06|03/04: remove field/veto duplicates; retain any regional locator only with unique-text/cost evidence.|
|2b-07|03: one row/glyph ownership and all 256 marks; remove destructive duplicate clipping.|
|2b-08|G3: full 208, 104 comments, 256 marks and independent/private 44 checks before acceptance.|
|3-01|02: share calibrated mirror/seal evidence, including all recovery consumers.|
|3-02|02/04: native motif/blob/frame evidence and complete mixed glyph ownership; measure cheap routes.|
|3-03|02/03: preserve pale-front controls and classify mixed endpoints; old normal-run growth policy is superseded.|
|3-04|01b/02/04: shared observations and stable evidence versions; remove repeated footprint calibration.|
|4-01|04: keep decoder/localizer as engineering; no Rust port.|
|4-02|01b/02/03: consolidate actual scale/ink/contact providers and consumers, not only interfaces.|
|4-03|01b/03: share finite boundary/cell/leader evidence.|
|4-04|04: compare cheap dispatch against explicit features even when it is quiet.|
|4-05|03: missing-row/endpoint recovery through common ownership; retain every accepted historical recovery.|
|4-06|03/04: one curve/gap/crop construction replaces competing join and smoothing decisions.|
|4-07|04: keep offline evidence harness; delete dead runtime paths.|
|4-08|04/05: complete timing and both review ledgers; defer Rust readiness.|

M41–M52 are historical proposals, not active mechanisms: 41 observations→01b/02; 42 layout→03; 43 surface→03; 44 rows→03; 45 native obstacle reduction→01b/04; 46 crops→03; 47 endpoints→02/03; 48 reassignment→03; 49 source adapter→03; 50 need detection→04; 51 evidence→G3/G4; 52 offline harness→04/05. Do not resurrect failed implementations to close their labels.

## Every active mechanism has a disposition

Grades are the R7 methodology grades, not promised upgrades. Each retained physical decision needs the feature/reference/comparison record above; required engineering remains labelled engineering.

| ID | R7 grade | Mechanism | Current disposition |
|---|---|---|---|
|M00|D|File decode, warm session and explicit parked-page input|04/05 retain input/session/parked scope as engineering; charge its cost.|
|M01|D|Paddle resize, normalization and learned localization map|03/04 retain Paddle as actual localization input, never physical row truth.|
|M02|D|DB threshold, contour score, expansion and quad/polygon output|03/04 retain useful DB proposal construction; initial polygons are replaceable.|
|M03|D|Height proxy, straight axes, raster/ROI primitives and call-local geometry memo|01b remove box-height authority; share raster/ROI preparation and measured local scale.|
|M04|B|Reduced printed-rule nomination|01b/03/04 share rule nominations; compare native confirmations and quiet misses.|
|M05|A|Native straight-rule/flank verification and Q8 cut|01b/03 preserve native finite rule/flank evidence through one layout owner.|
|M06|B|Weak-layer nomination and reflected-glyph ownership, including recovery callers|02/03 preserve reflected-glyph evidence; unify calibration and recovery consumers.|
|M07|B|Native seal-rim trace and tangent-letter exclusion|02 preserve native rim/letter evidence; check partial rims and mixed stamp/text.|
|M08|B|Coarse connected-ornament and recurrence gate|02/04 share ornament nominations; compare missed/false native cases.|
|M09|B|Spatial repeated-ink support and residual-glyph veto|02 keep native repeat support; replace unsupported text veto by whole-glyph evidence.|
|M53|B|Compact isolated solid-mass nomination and native disk/counter test|02/04 preserve native disk/counter confirmation; measure reduced mass nomination.|
|M10|B|Disconnected motifs with border/layout nomination|02/04 share motif/layout evidence; preserve disconnected letters.|
|M11|B|Outer-third map-ridge coherence scout for the shared page field|03/04 remove independent field scout as authority; share need evidence and test quiet curls.|
|M12|B|Native straight/curved rule verification and grid rejection|01b/03 share finite straight/curved rules and cell context; remove whole-grid veto.|
|M13|A|Bilateral column termination certificate and shared-edge split|01b/03 retain bounded bilateral termination witness, not a claim about all gutters.|
|M14|B|Native paper/ink components and body-contact preparation|01b/02 one native observation preparation per justified representation, cached for consumers.|
|M15|B|Shared page-field mesh, row phases and native edge certificate|03 replace competing mesh/phase authority with reused pooled curves and row coordinates.|
|M16|B|Field-based image unbending and regional Paddle rerun|03/04 keep unbending as evidence; retain rerun only for measured unique localization.|
|M17|C|Native components assigned to rectified row bands|03 replace rectified axis-band assignment with complete glyph/mark row/cell ownership.|
|M18|D|Old-to-new field ownership, horizontal-source veto and fixed-point retention|03 delete field/parent veto and fixed-point retention chain after accounting for useful text.|
|M19|B|Per-line sparse DB ridge scout and affine/residual measurement|01b/03/04 share scale and consolidate box ridge scouting with common row/bend need.|
|M20|B|Local geometry correction, component completion and original-ink retention|03/04 replace standalone box completion with common owned extent and crop construction.|
|M21|D|Angled short-fragment and Hermite box-join nomination|03 remove box-pair/Hermite nomination as final authority; join by physical row identity.|
|M22|A|Native endpoint paths and tangent agreement|03 reuse checked native endpoint tangent primitive within common row construction.|
|M23|C|Fragment join authorization and column/rule protection|03 replace join authorization policy by row/cell/glyph evidence.|
|M24|B|Local type pitch, phase and missing-slot nomination|01b/03 share measured local typography; slot nominations cannot define a second row system.|
|M25|B|Missing-slot body contacts and point ownership|01b/03 share contacts; replace point/centre ownership authority.|
|M26|B|Table, leader and repeated-dot structural exclusion|01b/03 one cells/rules/leaders account; no whole-table exemption from single-row crops.|
|M27|D|Lattice-slot regional Paddle confirmation|03/04 remove regional-detector confirmation authority and redundant inference.|
|M28|C|Recovered component completion and repeated ink-ownership filters|02/03 replace repeated ink filters/completion with common evidence and complete assignment.|
|M29|B|Unowned residual-ink scout|03 use common residual native support to nominate missing rows; check quiet misses.|
|M30|B|Native residual body height, lower-contact chains and ambiguity|01b/03 reuse native body/contact chains with shared scale and row identity.|
|M31|C|Residual regional recovery, axis vetoes and separator-piece checks|03 replace axis/height/residual veto policy; preserve short rows and earlier recoveries.|
|M32|B|Large initial observation and first-row completion|03 preserve full initial support/ownership, not centre inclusion or height rejection.|
|M33|B|Smooth native contact envelope and component-preserving application|03/04 one gap/envelope/crop construction constrained by owned glyphs.|
|M34|B|Longitudinal faintness scout and sampled page calibration|02/04 one sampled calibration and scout measured against dense ink observations.|
|M35|B|Relative component faintness and whole-segment suppression|02/03 common calibrated ink evidence; mixed endpoints and pale fronts need whole-glyph decisions.|
|M36|B|Two-band scout for merged detector rows|03 replace parent two-band authority with reused discovery of all rows, including partial neighbours.|
|M37|B|Native curved gap path, retained-ink split and guard|03 replace independent parent-window split with common row gaps and complete ownership.|
|M38|D|Final duplicate/overlap reconciliation|03 delete destructive final overlap clipping; resolve ownership before crop assembly.|
|M39|D|Changed-footprint faintness recheck and exclusion bookkeeping|02/04 keep versioned exclusion scheduling as engineering; remove redundant string/footprint work.|
|M54|B|Native recurrent frame units, connected sides and ragged corridor|02/04 share native recurrent-frame/corridor evidence and measure its scout.|
|M55|C|Whole-segment frame ownership and deletion|02/03 replace centre-in-corridor deletion with whole text/decoration support and explicit uncertainty.|
|M40|D|Compose order, permanent exclusions, source ancestry and result contract|01b/03/04/05 one documented composition; diagnostics and ancestry do not decide ownership.|

## Owner algorithms, verbatim

These words are included in every launch prompt; no later checklist weakens them.


### Preserved source text

## A. Missed words at the end of curved pages, using the curvature detection heuristic

10 Oct 14:10:
> the other is simply search heuristics that might be required to apply; i.e. dont apply our algo fully; figure out
> much simpler way to take what small detector gives us and for example compute hte mean line you got, and then then
> compute in a lightweight way if there is curvature at the end of the page or if the line actually tracks the text.

11 Oct 01:02, the owner's three major issues after reviewing the pages:
> (2) a heuristic for detecting curvature at the end of pages, and deciding on a way this might help to reorganize all
> segments efficiently i.e. consider how many parallel lines would change if this curvature would be applied

11 Oct 10:51, asking for a picture of the curvature:
> is it possible to actually create a graphical representation of the curvature detected?
> i.e show the parallel straight lines where we think there is no curvature
> and then how they bend

11 Oct 11:22–11:43, reviewing the round-6 bend pictures:
> I see that for s2-86865c33eef5932c013b-p00005 bend was detected but no fixes were applied?

> similarly for s2-86865c33eef5932c013b-p00007

> yeah but it wasnt used to capture the last word of each line

> right but now the whole page bend should be global we dont need to check individual lines right?
>
> so if we know the bend and we have the text-lines' lines we can just follow them to the end of the page in a way
> that does not impose on the other liens

11 Oct 11:53, the round-6 verdict:
> we also need to extend improvements on curvature by applying the idea we have discussed now.

## B. Following the curve as a search mechanism

8 Oct 17:58:
> Ok it seems we have solved line detection and skewing.
>
> But doesn't this mean that we can go back to the mapping of the recognizer on the page and apply a particular curve
> in each line?
>
> The only thing we have to do is identify each line we are seeing and put the puzzle pieces together

8 Oct 18:01:
> No bro you just follow the line we demarcate.
>
> You either keep following the curve or you widen the box to fit the top and bottom lines

8 Oct 19:21, the main algorithm:
> We should be thinking clearly, write this down as the main algorithm we are follwoing, if we do this it is an easy
> problem:
>
> (1) there should be a coordinate system for every line (a) where in the recognizer's segment it is, and if there are
> more than one in a segment where in the segment they are. They could be up, down, left, right.
> (2) so eg if the cropped top of a line is above our target line we could easily say in which segment we will find it
> (the top neighbour)
> (3) we have already figured out how to follow the curve (which could be a straight line) of any given text-line
> (4) we have also figured out (a) where small letters like α, σ, ι live, (b) top-long letters live δ, β etc (c) and so
> on for bottom-long letters; and similarly for accents and even capital letters. This should generally be consistent
> in a page so as long as writting is writtin in the same font in a page the 4 lines we can find, top, middle-top,
> middle-bottom, bottom of the fonts define a line.
> (5) the 4 font lines should be following the curve (3) for each text-line
> (6) therefore by computing the 4 curves for each text-line, and then computing the middle of the distance for each
> neighbour according to (1) at every step k, we can define a text-line and an adequate boundary without overlap
> (7) we are very good at detecting when a curve or skew is trailing outside the segments boundary, it is better to
> over do it and follow the continuation of the line as much as possible than lose the text. We should stop at page
> boundary, otherwise we will cut back if we find some type of graphical boundary or a very large gap.

9 Oct 01:14, what to send to Astra:
> that you expect it to start or improve your pixel segmenter
> that you expect to detect multiple lines within segments
> that you expect it to detect line skew or curvature, and the 4 lines defining the font and how the skew or curve
> that the goal is to take that and then finish by creating segments that follow this curvature or skeness and unroll
> in lines that contain no cutoff because of the skew or curve trailing the line outside the segment, but the segment
> follows the true line from beginning to end. These segments should be so, so that normalized can be passed to OCR
> without any ambiguity about their contents.
>
> These are basically technical constraints on teh algorithm I had stated before.
>
> These segments should respect column boundaries as well

9 Oct 12:27, on the font lines and accent lines:
> OK, this is basically important for following the curve or skew of the lines

## C. Not more than one line in a line segment

8 Oct 15:27:
> I only want you to track with more precision the second lines as well even if only the edges are showing like
>
> s2-86865c33eef5932c013b-p00005-l00020
> s2-7534648e60694be1d180-p00023-l00011
> there is a third line here at the bottom s2-200e977f2dab5291c42c-p00035-l00002
> this has a curved geometry at hte nd which is undetected s2-b1ce8959da62cc55c839-p00009-l00068 , you can even say
> there are 4 lines here if you are very prickly

8 Oct 16:10:
> you also have a tag "two lines in the crop" it would be better to state the accurate n of lines detected

8 Oct 16:14:
> we need to keep a careful balance of extending a single line, and not trying to align two lines that do not have the
> same alignment

8 Oct 16:37:
> (2) to build an API on top of it to (a) seperate the lines when there is more than one (we can eg then use the google
> documents API to get text contents) and (b) to fix the geometry

11 Oct 01:02:
> (3) some segments contain more than one line and we need to fix that!

11 Oct 01:11:
> you misunderstood (3), I am talking about vertically contained now not horizontally. this is something we havent
> talked much about and I havent reviewed much because it's per segment not per page

The owner's per-segment marks of how many rows each segment holds ("one", "two", ...) are in
`../review_r5_rows/owner_marks.json`, and their status after round 7 is in the r7 `ROWS.md`.

## D. Method: what "principled" means, speed, and how ideas are pursued

11 Oct 15:56, on the round-7 mechanism review:
> I noticed that the review output might have interpreted principled as "well structured software"
> i.e. noticing duplicates and so on
> which is very good
> but I had more in mind principled in the sense of our methodology
> does it track real features? is each component developed according to a more robust and slow model of the page?
> with the hopes that if there are true our mechanisms will generalize better.

10 Oct 14:10, on speed:
> I am also having a feeling that our previous framing of speeding up but retaining exactly the same output was wrong
> for optimization; because there might other classes of algorithms very near our current own, that could be found by
> radically or somewhat different approaches, that are way faster but basically ahve the same results.

10 Oct 14:14:
> Ideas don't come from adding some retarded percentage gates
>
> Ideas come from divine insight about hte working of nature, and relentlessly pursuing the image of your dreams until
> it becomes reality.

11 Oct 11:53, the round-6 verdict:
> faintness seems much improved although not perfect, boundary respect seems very good as well.
> [...] finally speed is getting a little out of hand so we will need a speed improvement round, and home cleaning,
> de-sloppification.

Additional procedure from OWNER_MESSAGES_ALL.md, 8 October, 16:45:56 UTC; this is part of the specification:

> so the algorithm should:
>
> (1) get the line segments as an input
> (2) draw the curves/skew lines and 4 lines for each line in the segment; you then give them the coordinates to seperate their identities
> (3) after you have the curves you have the 4 lines for each text-line you forget the initial line segments completely
> (4) you can draw a new segment simply by finding the middle between the bottom and top lines from neightbouring lines, and by extending left and right along the curve until you find a boundary

## Appendix: every comment at the frozen R7 baseline

Full source: [/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/COMMENTS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/COMMENTS.md). These are prior verdicts, not new R8 adjudications. All records are regression obligations for03/04/05. Ink/frame records have02 as repair owner; geometry/recovery/boundary records have03, using the existing explicit code;01b consolidates shared measurements. Mixed cases require both. Record links preserve all original details and images.

### O01: s2-3229200bf47ca465a42d-p00004

> still a missed line between 10 and 11

R7 record: **not fixed.** The Μαυρομιχάλης row still lacks a segment. #10 is field-owned; #11 is original source33. RECOVERY.md identifies the lost prior addition and the multirow-height veto.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-3229200bf47ca465a42d-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O01.historical.jpg)

### O02: s2-3229200bf47ca465a42d-p00005

> still some last missed chars for 13 14 18 on the curvature

R7 record: **not fixed.** Curled words remain beyond #13/#14/#18. These final items retain original sources35/34/30, so this is failed replacement/endpoint recovery, not a successful field band cutting them.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-3229200bf47ca465a42d-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O02.historical.jpg)

### O03: s2-3229200bf47ca465a42d-p00006

> still a line missed between 26 and 27
>
> words horizontally between 33 and 36
> and also between 35 and 38
> and also the line before 39 (vertically) is missed

R7 record: **not fixed.** #27/#39 retain broad original boxes; left words between original fragments33–38 remain uncovered. #26 is a real residual addition, which does not fix the next mixed row.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-3229200bf47ca465a42d-p00006.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O03.historical.jpg)

### O04: s2-49598b2e848ab1f0ee1e-p00001

> missed line between 41 and 44
>
> missed lines between 67 and 75
>
> first word before 75 and 90 is still missed

R7 record: **not fixed.** Unboxed rows and curled starts are visible. #41 is a B partition child; #44/#67/#75/#90 retain original sources. R6 recovery audit attributes two returned omissions to table context and multirow rejection.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-49598b2e848ab1f0ee1e-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O04.historical.jpg)

### O05: s2-49598b2e848ab1f0ee1e-p00004

> lines are missed still between:
>
> 50 and 52
> 108 and 112
> 112 and 116
>
> also some last word to the right of the right column where there is curvature are missed: 42 59 118 127

R7 record: **not fixed.** Residual additions #108/#112 are present, but rows between them and curled ends remain missing. #127 is a column-cut original, not page_field. The full-page overview also shows the earlier gap.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-49598b2e848ab1f0ee1e-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O05.historical.jpg)

### O06: s2-49598b2e848ab1f0ee1e-p00005

> some segments contain two lines eg 116 adn 117 which cause ocr confusion

R7 record: **not fixed.** The mixed bottom rows are real. #116/#117 are verified-curved-separator descendants of original sources1 and 0/1, not accepted page-field polygons. Attribution in the briefing to rebuilt bands is too broad for these IDs.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-49598b2e848ab1f0ee1e-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O06.historical.jpg)

### O07: s2-44b5cf9e0d680b361091-p00002

> line 123 does not target its line well
>
> and after these many segments contain two lines

R7 record: **not fixed.** The foot is misaligned as reported. #122/#123/#125–128 are bilateral-column descendants, not page_field items; #123 has duplicate_clipped=True. shape changes are empty. Shared rows must repair inherited boxes too.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-44b5cf9e0d680b361091-p00002.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O07.historical.jpg)

### O08: an-ef481610a820-p000150

> faint letter lines are still in 3

R7 record: **not fixed.** The small margin mark remains in original source38. Short/ambiguous component handling is the relevant ink path; it is not recovered text.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ef481610a820-p000150.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O08.historical.jpg)

### O09: an-ef481610a820-p000151

> many faint lines still in 9 10 29 30

R7 record: **not fixed.** All four short margin pieces remain while similar surrounding pieces were removed. Current source indices46/45/31/25 retain their original boxes.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ef481610a820-p000151.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O09.historical.jpg)

### O10: s2-44b5cf9e0d680b361091-p00005

> 123 is faint

R7 record: **fixed.** The mirrored bottom running head at historical #123 is removed by the inherited Task 3 faintness change. Native removed pixels are mirrored back print, not front text. Other multirow geometry on the page remains outside this specific verdict.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-44b5cf9e0d680b361091-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O10.historical.jpg)

### O11: s2-93f8070059f938bda524-p00001

> 1, 89, 117, 126, 127 are faint
>
> 5 also extends over faint chars

R7 record: **not fixed.** #1 and #5 are accepted page-field items; #5 visibly includes faint left words. #89/#117/#126/#127 retain original ghost pieces, including the right remainder of a bottom line. Final mixed-segment preservation cannot trim a faint endpoint.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-93f8070059f938bda524-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O11.historical.jpg)

### O12: s2-86865c33eef5932c013b-p00026

> some boxes like 9 and 40 are extended to include faint words

R7 record: **not fixed.** Both named polygons carry page_field=True and extend over pale back words. Whole-segment faintness correctly sees normal print in the central phrase, so endpoint classification must happen inside geometry.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-86865c33eef5932c013b-p00026.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O12.historical.jpg)

### O13: an-c8b96a901917-p000155

> 2 goes across the boundary (even though the boundary is half here)

R7 record: **not fixed.** Original source90 spans the columns above the visible rule. The finite-rule certificate has no supported continuation through that row.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-c8b96a901917-p000155.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O13.historical.jpg)

### O14: s2-c0b02fe229794d2fe76d-p00010

> also a line is missed 3 from the bottom on the right

R7 record: **fixed.** The questioned row has its own final segment #118, type_residual=1, and is unboxed in a fresh Paddle-only tile. It should be a protected recovery control, not counted as an open R6 omission.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-c0b02fe229794d2fe76d-p00010.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O14.historical.jpg)

### O15: an-ffccc97c07de-p000354

> missed 64's last word

R7 record: **not fixed.** The word ἀμέλ after the gap has no segment. #64 ends after the Arabic-script word and is a column-cut source; endpoint/grouping must allow a real word after wide whitespace.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ffccc97c07de-p000354.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O15.historical.jpg)

### O16: an-d83e7a198ade-p000099

> missed line under 108

R7 record: **not fixed.** Διαμπάξ, διόλου remains unboxed below #108. #108 itself is an accepted residual addition, so the older fixed recovery comment on the same page is a separate success.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-d83e7a198ade-p000099.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O16.historical.jpg)

### O17: an-ef481610a820-p000181

> missed 1 lines between 19 and 20

R7 record: **not fixed.** σι τὸ ἴ remains between the two boxes. The next row #20 is a residual addition. Five-body/4h–5h eligibility is an explicit limitation for short continuations.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ef481610a820-p000181.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O17.historical.jpg)

### O18: an-00f143ecce59-p000258

> 1 lines missed between 16 and 17

R7 record: **not fixed.** The second row beside the large initial has no separate segment. #16/#17 are original-source boxes. The crop does not justify saying #16 fully contains both rows; some second-row ink is outside it.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-00f143ecce59-p000258.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O18.historical.jpg)

### O19: an-1ba3fdb1436b-p000035

> missed line at bottom

R7 record: **not fixed.** The final real row remains unboxed near the removed frame. R6 evidence says its proposal touches a forbidden footprint. Exclusion semantics must be checked at exact ink/row support, not broadened bbox space.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1ba3fdb1436b-p000035.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O19.historical.jpg)

### O20: an-00f143ecce59-p000192

> last line is missed here, and watermark is selected as well

R7 record: **partly.** The bottom row remains unboxed; rim removals are preserved, but a small boxed piece inside the stamp is still visible. “Watermark removed” must not imply the whole stamp interior is clean.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-00f143ecce59-p000192.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O20.historical.jpg)

### O21: an-7792a3301892-p000059

> boundary is added unlike in other cases

R7 record: **partly.** Five whole flower-frame segments are removed. The native loss sheet contains decoration only. The top frame is still boxed, and mixed frame/text boxes remain; this is not complete frame removal.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000059.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O21.historical.jpg)

### O22: an-7792a3301892-p000104

> boundary is added unlike in other cases

R7 record: **partly.** Ten whole flower-frame segments are removed, including the top and bottom border strips. Mixed text/frame boxes and page-number ornaments remain. No removed native context contains a front letter.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000104.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O22.historical.jpg)

### O23: an-c99f1c450f55-p000025

> 1 correct removal, but 11 should have been removed as well

R7 record: **not fixed.** The approved first removal survives; the upper ivy strip remains. Keep both positive and failed motif examples.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-c99f1c450f55-p000025.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O23.historical.jpg)

### O24: s2-922e617957fca8dfafd0-p00001

> ink blob is captured at 23

R7 record: **fixed.** The isolated right-margin blob at historical #23 is removed. The native context shows a solid ink spot, and surrounding text rows are unchanged.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-922e617957fca8dfafd0-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O24.historical.jpg)

### O25: s2-7534648e60694be1d180-p00018

> 6,7,

R7 record: **outside this round.** The comment identifies numbers without a requested change. Preserve it verbatim, do not invent a defect or mark it fixed. Task 1 can finish without resolving task-specific owner intent.

Task responsibility: Coordinator: clarify the requested action; 03/05 preserve the unresolved wording.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-7534648e60694be1d180-p00018.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O25.historical.jpg)

### O26: s2-6419488b7f8e69fd20da-p00001

> faint lines not removed from 249 to 255

R7 record: **outside this round.** Sideways page is passed through after Paddle by the explicit parked flag. Its faintness and one two-row mark are outside the active correction comparison.

Task responsibility: Parked orientation; all tasks preserve scope, 05 audits the exclusion.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-6419488b7f8e69fd20da-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/O26.historical.jpg)

### C01: s2-86865c33eef5932c013b-p00005

> bend reaches curled words but all rebuilt candidates fail

R7 record: **not fixed.** 38 proposals; late decisions have21 foreign-row, 9 separate-horizontal, 4 lost-ink, 2 small-cell groups, plus 2 unowned proposals. Zero accepted early or late. The four reason counts sum 36, not38.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-86865c33eef5932c013b-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/C01.historical.jpg)

### C02: s2-86865c33eef5932c013b-p00007

> long curled rows rejected;13 of79 accepted

R7 record: **not fixed.** 79 proposals; 9 early and 4 late accepted. Late6 candidates remain unowned; 40 decision groups preserve small cells. A physically correct shared bend cannot rescue a bad per-row rebuild.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-86865c33eef5932c013b-p00007.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/C02.historical.jpg)

### C03: an-e259bbf5081c-p000198

> two columns fitted as one bend region

R7 record: **not fixed.** The displayed mesh spans separate columns with row-phase offsets; it is not a leaf certificate.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-e259bbf5081c-p000198.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/C03.historical.jpg)

### C04: an-c8b96a901917-p000068

> spread fitted across the binding

R7 record: **not fixed.** A middle fitted region crosses the two page leaves and bridges different row phases.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-c8b96a901917-p000068.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/C04.historical.jpg)

### C05: an-7792a3301892-p000154

> Task3 additional decorative-frame control

R7 record: **partly.** All 24 inherited whole-frame removals on this page are retained. Native loss sheets contain recurrent flower decoration. The upper border and tall right border still share retained boxes with nearby text; those mixed segments remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000154.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/C05.historical.jpg)

### R4-01: s2-6419488b7f8e69fd20da-p00001

> faint lines not removed from 249 to 255

R7 record: **outside this round.** The sideways page is passed through unchanged because orientation is parked. The faint boxes remain.

Task responsibility: Parked orientation; all tasks preserve scope, 05 audits the exclusion.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-6419488b7f8e69fd20da-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-01.historical.jpg)

### R4-02: an-dbd045ccd84c-p000249

> watermark is captuerd at 38

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-dbd045ccd84c-p000249.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-02.historical.jpg)

### R4-03: an-7792a3301892-p000107

> boundary is added unlike in other cases + watermark

R7 record: **partly.** Sixteen whole frame segments are removed on p107; native loss sheets contain only recurrent flower decoration. The earlier seal-rim removal is preserved. Ornament inside retained mixed text/page-number boxes is still not removed.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000107.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-03.historical.jpg)

### R4-04: s2-831443dc5e6f1ccfbaf5-p00042

> many faint lines added at the bottom

R7 record: **fixed.** The faint bottom back-page numeric grid is removed (36 relative-faintness removals). Front table entries remain; this does not make all table cells single-row.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-831443dc5e6f1ccfbaf5-p00042.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-04.historical.jpg)

### R4-05: an-7792a3301892-p000104

> boundary is added unlike in other cases

R7 record: **partly.** Ten whole frame segments are now removed on p104. Native deletion views show no front-text loss; mixed text/frame boxes and page-number ornaments remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000104.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-05.historical.jpg)

### R4-06: an-3352d912f2e9-p000160

> 36 faint character

R7 record: **fixed.** The isolated faint bottom character is removed; normal front body print remains.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-3352d912f2e9-p000160.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-06.historical.jpg)

### R4-07: an-466cffad2cba-p000267

> 28 is watermark

R7 record: **fixed.** The original is now included. Seal-rim lettering is removed and the pale front body remains.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-466cffad2cba-p000267.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-07.historical.jpg)

### R4-08: an-d6fd2cf2f618-p000047

> 38 watermark

R7 record: **fixed.** The faint watermark-letter segment is removed by page-relative faintness.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-d6fd2cf2f618-p000047.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-08.historical.jpg)

### R4-09: an-1be60011c435-p000215

> 3 lines are on watermark

R7 record: **partly.** Two seal-rim boxes are removed. The uncertain inner seal text remains boxed; pale front text is retained.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1be60011c435-p000215.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-09.historical.jpg)

### R4-10: s2-7534648e60694be1d180-p00018

> 6,7,

R7 record: **not fixed.** The comment does not specify what to change. The two indicated rows look like front text and remain. No intent was invented from the numbers.

Task responsibility: Coordinator: clarify the requested action; 03/05 preserve the unresolved wording.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-7534648e60694be1d180-p00018.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-10.historical.jpg)

### R4-11: s2-032eaf8e6b3b83918feb-p00004

> missed line between 46 and 47

R7 record: **partly.** The original is now included. One real row is recovered and 14 field bands follow curved rows. Mixed broad boxes and small residual fragments remain, so the local region is not fully clean.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-032eaf8e6b3b83918feb-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-11.historical.jpg)

### R4-12: s2-922e617957fca8dfafd0-p00001

> ink blob is captured at 23

R7 record: **not fixed.** The dark blob at the right remains boxed. Neither darkness nor stroke width supplies a safe generic non-text decision.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-922e617957fca8dfafd0-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-12.historical.jpg)

### R4-13: an-ffccc97c07de-p000152

> stain at 34

R7 record: **fixed.** The faint stain segment is removed by relative faintness. This is not a general dark-stain classifier.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ffccc97c07de-p000152.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-13.historical.jpg)

### R4-14: an-d6002cf45e4d-p000058

> 8 on watermark

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-d6002cf45e4d-p000058.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-14.historical.jpg)

### R4-15: s2-86865c33eef5932c013b-p00026

> some boxes including 5, 11 17 18 and 29 are faint letters from the back

R7 record: **partly.** Four faint ghost segments are removed. Other ghost boxes and severe curved body crossings remain; the six field bands mostly affect headings.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-86865c33eef5932c013b-p00026.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-15.historical.jpg)

### R4-16: an-00f143ecce59-p000258

> 2 lines missed

R7 record: **partly.** The second row beside the large I is recovered. Another missing row remains; the I belongs to the preceding row and is not moved.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-00f143ecce59-p000258.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-16.historical.jpg)

### R4-17: an-ef481610a820-p000151

> 53 is watermark

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ef481610a820-p000151.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-17.historical.jpg)

### R4-18: an-ef481610a820-p000150

> faint letter lines are added such as 11 18 13 14

R7 record: **partly.** Five faint ghost segments are removed among the retained front dialogue. Some ambiguous short or mixed fragments remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ef481610a820-p000150.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-18.historical.jpg)

### R4-19: s2-c0b02fe229794d2fe76d-p00010

> line 3 is unieted across boundary
>
> also a line is missed 3 from the bottom on the right

R7 record: **fixed.** Both clauses are addressed: the top crossing is split at the central rule and the missing third-from-bottom right-column row is recovered.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-c0b02fe229794d2fe76d-p00010.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-19.historical.jpg)

### R4-20: an-d6002cf45e4d-p000010

> watermark is captuerd at 15

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-d6002cf45e4d-p000010.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-20.historical.jpg)

### R4-21: an-1be60011c435-p000120

> 60 is from the watermark

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1be60011c435-p000120.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-21.historical.jpg)

### R4-22: an-7792a3301892-p000059

> boundary is added unlike in other cases

R7 record: **partly.** The bottom flower row and seal-rim lettering are removed. The top and side decoration fragments remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000059.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-22.historical.jpg)

### R4-23: s2-74cdb23a34ca4a6cd01e-p00012

> line 127 united across boundary

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-74cdb23a34ca4a6cd01e-p00012.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-23.historical.jpg)

### R4-24: an-7792a3301892-p000154

> non-word boundary is captured as line

R7 record: **partly.** Twenty-four whole frame segments are now removed on p154. The upper and right frame still occur in retained mixed boxes. The earlier faint-ghost removals are preserved.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-7792a3301892-p000154.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-24.historical.jpg)

### R4-25: an-2cfe28da5103-p000084

> missed 2 lines on the footnote section of the left page

R7 record: **fixed.** Both missing left-page footnote rows are recovered at their own small body scale.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-2cfe28da5103-p000084.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-25.historical.jpg)

### R4-26: an-3352d912f2e9-p000036

> watermark is line 36

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-3352d912f2e9-p000036.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-26.historical.jpg)

### R4-27: an-1be60011c435-p000066

> 65 is from the watermark

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1be60011c435-p000066.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-27.historical.jpg)

### R4-28: an-00f143ecce59-p000192

> last line is missed here, and watermark is selected as well

R7 record: **partly.** Two faint watermark segments are removed and duplicate overlap is clipped. The missing bottom body row is still not recovered.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-00f143ecce59-p000192.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-28.historical.jpg)

### R4-29: an-db97e3dd59ca-p000066

> watermark is captuerd at 37

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-db97e3dd59ca-p000066.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-29.historical.jpg)

### R4-30: an-e74539ae215c-p000338

> watermark

R7 record: **partly.** The right-rim seal box is removed. Overlapping/interior watermark material is not established as removable.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-e74539ae215c-p000338.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-30.historical.jpg)

### R4-31: s2-831443dc5e6f1ccfbaf5-p00039

> kept faint line 139

R7 record: **fixed.** The faint bottom back-page line is removed. Front table text remains.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-831443dc5e6f1ccfbaf5-p00039.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-31.historical.jpg)

### R4-32: an-db97e3dd59ca-p000042

> watermark is captuerd at 37

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-db97e3dd59ca-p000042.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-32.historical.jpg)

### R4-33: s2-74cdb23a34ca4a6cd01e-p00003

> line 127 united across boundary

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-74cdb23a34ca4a6cd01e-p00003.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-33.historical.jpg)

### R4-34: s2-74cdb23a34ca4a6cd01e-p00006

> line 3 united across boundary

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-74cdb23a34ca4a6cd01e-p00006.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-34.historical.jpg)

### R4-35: s2-7247ee9b1bc2374b3980-p00001

> 111 connects across the boundary

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-7247ee9b1bc2374b3980-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-35.historical.jpg)

### R4-36: s2-74cdb23a34ca4a6cd01e-p00002

> 3 is across the boundary

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-74cdb23a34ca4a6cd01e-p00002.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-36.historical.jpg)

### R4-37: s2-74cdb23a34ca4a6cd01e-p00007

> line 3 and 126 united across boundary

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-74cdb23a34ca4a6cd01e-p00007.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-37.historical.jpg)

### R4-38: s2-44b5cf9e0d680b361091-p00001

> 58 and 115 go across boundary

R7 record: **fixed.** The original is now included; the marked crossings are split at the printed divider. Row containment is still partial elsewhere, with small unique remnants after duplicate clipping.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-44b5cf9e0d680b361091-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-38.historical.jpg)

### R4-39: s2-44b5cf9e0d680b361091-p00002

> 121 adn 122 union across boundary

R7 record: **fixed.** The original is now included; marked crossings are split at the printed divider. Field bands improve several rows, but mixed straight boxes and small remnants remain.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-44b5cf9e0d680b361091-p00002.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-39.historical.jpg)

### R4-40: s2-44b5cf9e0d680b361091-p00003

> 122 across boundary

R7 record: **fixed.** The original is now included; marked crossings are separated at the central rule. This does not resolve other tall row boxes.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-44b5cf9e0d680b361091-p00003.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-40.historical.jpg)

### R4-41: s2-44b5cf9e0d680b361091-p00005

> 122 is faint

R7 record: **fixed.** The faint mirrored row is separated from the front row by overlap clipping and then removed by final faintness. The front text remains.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-44b5cf9e0d680b361091-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-41.historical.jpg)

### R4-42: an-466cffad2cba-p000323

> 27 on watermark

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-466cffad2cba-p000323.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-42.historical.jpg)

### R4-43: an-ef481610a820-p000181

> missed 2 lines between 19 and 20 + watermark

R7 record: **partly.** The longer missing list entry is recovered and the seal-rim box is removed. The short preceding fragment remains unsupported.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-ef481610a820-p000181.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-43.historical.jpg)

### R4-44: s2-d12a9a4feb23254f4080-p00006

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-d12a9a4feb23254f4080-p00006.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-44.historical.jpg)

### R4-45: s2-93f8070059f938bda524-p00001

> 1 is faint

R7 record: **not fixed.** The faint ghost heading remains. Relative faintness now abstains on short/ambiguous normal-body evidence; 11 ghosts removed by task C return here. This is a recorded regression.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-93f8070059f938bda524-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-45.historical.jpg)

### R4-46: an-c153f2c605b3-p000040

> 34 on watermark

R7 record: **fixed.** The faint watermark lettering is removed; the adjacent front print remains.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-c153f2c605b3-p000040.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-46.historical.jpg)

### R4-47: an-1ba3fdb1436b-p000012

> boundary wasnt also removed for line 2

R7 record: **fixed.** The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1ba3fdb1436b-p000012.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-47.historical.jpg)

### R4-48: an-1f8e7d022643-p000003

> 21 on watermark

R7 record: **fixed.** The marked seal-rim lettering is removed. Ordinary front text remains; the circle interior itself is not excluded.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1f8e7d022643-p000003.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-48.historical.jpg)

### R4-49: an-c99f1c450f55-p000025

> 1 correct removal, but 11 should have been removed as well

R7 record: **not fixed.** The previously correct lower-strip removal is retained; the upper ivy strip still remains boxed because the full spatial verifier rejects its tall arches.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-c99f1c450f55-p000025.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-49.historical.jpg)

### R4-50: an-1ba3fdb1436b-p000035

> missed line at bottom

R7 record: **not fixed.** The real last row remains missed. Its proposal intersects the already removed frame footprint; preserving that veto costs recall here.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1ba3fdb1436b-p000035.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-50.historical.jpg)

### R4-51: s2-0ce9d1025b3f23c7119e-p00001

> missed removal of faint letters at 17, 42, 43, 44, 45

R7 record: **partly.** The 56 old back-print removals remain and six further faint segments are removed. The ghost heading “Ἀριθ. 300” remains: a connected dark mass exceeds the conservative faint-body allowance. It is not a normal-print run.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-0ce9d1025b3f23c7119e-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-51.historical.jpg)

### R4-52: s2-3229200bf47ca465a42d-p00006

> many lines are missed here, but none are added

R7 record: **partly.** Ten residual/grid segments are recovered and 12 final field bands improve rows. Several lower straight crops still contain neighbouring lines; no unowned field candidate is promoted.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-3229200bf47ca465a42d-p00006.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-52.historical.jpg)

### R4-53: an-d83e7a198ade-p000099

> missed line under 106

R7 record: **fixed.** The missing left apparatus row under the reviewed 106 is recovered. Existing apparatus envelopes also receive guarded shaping; other short fragments are not claimed solved.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-d83e7a198ade-p000099.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-53.historical.jpg)

### R4-54: s2-661ddf05c8865e7b2c45-p00005

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-661ddf05c8865e7b2c45-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-54.historical.jpg)

### R4-55: s2-49598b2e848ab1f0ee1e-p00001

> missed lines between 67, 75
>
> missed start of lines from 75, up to 103
> also between 41 and 44

R7 record: **partly.** Regression against task C: the real central row at y=2911–2974 and its left continuation at y=2866–2973 are mostly absent (7,612/8,231 and 3,678/4,145 old owned ink pixels uncovered). Field-first composition changes the grid/table context; table protection and a subsequent multirow veto reject them. The 60 field bands and seven additions are not evidence that these old fixes survived.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-49598b2e848ab1f0ee1e-p00001.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-55.historical.jpg)

### R4-56: s2-661ddf05c8865e7b2c45-p00004

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-661ddf05c8865e7b2c45-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-56.historical.jpg)

### R4-57: s2-49598b2e848ab1f0ee1e-p00004

> there is a column boundary in the middle which is ignored completely and the lines are unified.
>
> also many lines are missed here, but none are added
>
> also there is curvature to teh right and some chars at ends of lines are missed

R7 record: **partly.** Column crossings are cut; seven real text pieces are recovered and 17 field bands follow the right bend. Some right-end words remain detached or outside the bands, and some neighbouring straight crops still cross rows.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-49598b2e848ab1f0ee1e-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-57.historical.jpg)

### R4-58: s2-c0b02fe229794d2fe76d-p00007

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-c0b02fe229794d2fe76d-p00007.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-58.historical.jpg)

### R4-59: s2-60f24a3d8a2d714767f2-p00004

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-60f24a3d8a2d714767f2-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-59.historical.jpg)

### R4-60: an-466cffad2cba-p000242

> 26 is watermark

R7 record: **fixed.** The original is now included. Watermark lettering is removed; 17 field bands follow the body bend. The real short word “οἱ” is retained.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-466cffad2cba-p000242.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-60.historical.jpg)

### R4-61: s2-c0b02fe229794d2fe76d-p00005

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-c0b02fe229794d2fe76d-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-61.historical.jpg)

### R4-62: s2-661ddf05c8865e7b2c45-p00010

> there is a column boundary in the middle which is ignored completely and the lines are unified.

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-661ddf05c8865e7b2c45-p00010.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-62.historical.jpg)

### R4-63: s2-3229200bf47ca465a42d-p00004

> missed 2 lines between 9 and 10

R7 record: **partly.** Regression against task C: the recovered name row at y=712–801 is mostly absent (12,558 of 13,696 old owned ink pixels uncovered). The changed regional detection hits the existing multirow-height veto. Other field bands improve the bend, but broad straight boxes and detached starts remain.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-3229200bf47ca465a42d-p00004.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-63.historical.jpg)

### R4-64: s2-a0e233bc6efda91a641b-p00002

> there are 2 columns at the bottom which are read as one paragraph

R7 record: **fixed.** The marked joined segments are separated at the observed central printed divider. This fixes the specific column comment, not every glyph or page-layout defect.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-a0e233bc6efda91a641b-p00002.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-64.historical.jpg)

### R4-65: an-fd4fa0018ae1-p000035

> 2 is decoration boundary

R7 record: **fixed.** The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-fd4fa0018ae1-p000035.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-65.historical.jpg)

### R4-66: an-fd4fa0018ae1-p000028

> 19 is decoration boundary

R7 record: **fixed.** The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-fd4fa0018ae1-p000028.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-66.historical.jpg)

### R4-67: an-466cffad2cba-p000277

> missed large first letter on the new line

R7 record: **fixed.** The large E is included with the first recovered paragraph row, with its tall shoulder preserved through final shaping. The large-initial rule was not widened.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-466cffad2cba-p000277.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-67.historical.jpg)

### R4-68: an-00f143ecce59-p000221

> correct addition of missing line!

R7 record: **fixed.** The owner-approved missing-row addition is preserved.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-00f143ecce59-p000221.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-68.historical.jpg)

### R4-69: an-fd4fa0018ae1-p000031

> 9 is decoration boundary

R7 record: **fixed.** The marked horizontal decoration row is removed. The adjacent text and previously recovered paragraph row remain.

Task responsibility: 02 ink/decoration repair or preservation; 03 consumes it, 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-fd4fa0018ae1-p000031.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-69.historical.jpg)

### R4-70: an-1ba3fdb1436b-p000009

> very good addition and removal!

R7 record: **fixed.** The owner-approved addition and ornament removal are preserved.

Task responsibility: 02 supplies ink/source ownership; 03 completes row recovery; 04/05 preserve and audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/an-1ba3fdb1436b-p000009.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-70.historical.jpg)

### R4-71: s2-86865c33eef5932c013b-p00005

> missed line content internally between 1 and 8 (horizontal)
>
> and also missed lines between 15 and 16
> and also 2 below 57
>
> also many words missed to the right of lines as page curves to the right

R7 record: **partly.** Seven native join groups and three recovered pieces remain. All field proposals are vetoed, so internal omissions and severe curled right ends remain unresolved.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-86865c33eef5932c013b-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-71.historical.jpg)

### R4-72: s2-49598b2e848ab1f0ee1e-p00005

> there is a column boundary in the middle which is ignored completely and the lines are unified.
>
> also many lines are missed here, but none are added
>
> there is curvature to the left
>
> the added line is not smooth enough and very close to the chars

R7 record: **partly.** Columns are separated, 16 segments are recovered and 31 field bands follow the left bend. Several marked rows are now isolated; other crops remain multirow or include clipped strips. The added-row shape improves locally but smooth segments are not universal.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-49598b2e848ab1f0ee1e-p00005.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-72.historical.jpg)

### R4-73: s2-86865c33eef5932c013b-p00007

> curvature to the right, and many last chars are missed

R7 record: **partly.** Three recovered pieces, three joins and 13 field bands help selected rows. Severe right-end words remain uncovered; the field does not solve the whole curl.

Task responsibility: 01 explicit geometry reference; 03 row/boundary/recovery repair or preservation; 04/05 audit.

[Final page](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/s2-86865c33eef5932c013b-p00007.jpg) · [Historical numbered view](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/R4-73.historical.jpg)

## Appendix: every original row mark at the frozen R7 baseline

All256 marks below belong to03 for repair/preservation and04/05 for regression/audit;02 must preserve their native text while changing ink. [Original polygons/marks](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r5_rows/owner_marks.json) and [full R7 row record](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/ROWS.md) are authoritative historical context. Each quoted disposition below is R7 inherited evidence, not a new planner judgement. The same page/number in a different gallery may mean a different item.

| Page and historical segment | Verbatim owner mark | R7 disposition | Native context |
|---|---|---|---|
|an-2cfe28da5103-p000135: historical segment 22|one|Retained: the marked single row is now tighter; all three spatial matches are complete neighbouring rows, not accent-only crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000135.mark-22.png)|
|an-2cfe28da5103-p000135: historical segment 40|two|Partly: the target body row is isolated, but the matched upper row still includes neighbour letters.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000135.mark-40.png)|
|an-2cfe28da5103-p000135: historical segment 68|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000135.mark-68.png)|
|an-3352d912f2e9-p000104: historical segment 5|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-3352d912f2e9-p000104.mark-5.png)|
|an-3352d912f2e9-p000104: historical segment 19|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-3352d912f2e9-p000104.mark-19.png)|
|an-778126cc8c2b-p000010: historical segment 21|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-778126cc8c2b-p000010.mark-21.png)|
|an-778126cc8c2b-p000010: historical segment 37|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-778126cc8c2b-p000010.mark-37.png)|
|an-7a2b17a3fb0f-p000200: historical segment 65|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-65.png)|
|an-7a2b17a3fb0f-p000200: historical segment 81|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-81.png)|
|an-7a2b17a3fb0f-p000200: historical segment 171|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-171.png)|
|an-7a2b17a3fb0f-p000200: historical segment 227|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-227.png)|
|an-7a2b17a3fb0f-p000200: historical segment 228|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-228.png)|
|an-7a2b17a3fb0f-p000200: historical segment 229|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-229.png)|
|an-7a2b17a3fb0f-p000200: historical segment 235|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-235.png)|
|an-7a2b17a3fb0f-p000200: historical segment 243|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-243.png)|
|an-7a2b17a3fb0f-p000200: historical segment 257|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-257.png)|
|an-7a2b17a3fb0f-p000200: historical segment 272|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-272.png)|
|an-7a2b17a3fb0f-p000200: historical segment 273|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-273.png)|
|an-7a2b17a3fb0f-p000200: historical segment 278|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-278.png)|
|an-7a2b17a3fb0f-p000200: historical segment 282|two|Partly: the numeric rows are separated; a clipped edge of the next digit row still enters one crop.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-282.png)|
|an-7a2b17a3fb0f-p000200: historical segment 287|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-287.png)|
|an-7a2b17a3fb0f-p000200: historical segment 294|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-294.png)|
|an-7a2b17a3fb0f-p000200: historical segment 301|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-301.png)|
|an-7a2b17a3fb0f-p000200: historical segment 322|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-322.png)|
|an-7a2b17a3fb0f-p000200: historical segment 343|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-343.png)|
|an-7a2b17a3fb0f-p000200: historical segment 361|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-361.png)|
|an-7a2b17a3fb0f-p000200: historical segment 374|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-374.png)|
|an-7a2b17a3fb0f-p000200: historical segment 412|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-412.png)|
|an-7a2b17a3fb0f-p000200: historical segment 420|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-420.png)|
|an-7a2b17a3fb0f-p000200: historical segment 426|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-426.png)|
|an-7a2b17a3fb0f-p000200: historical segment 434|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-434.png)|
|an-7a2b17a3fb0f-p000200: historical segment 453|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-453.png)|
|an-7a2b17a3fb0f-p000200: historical segment 506|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-506.png)|
|an-7a2b17a3fb0f-p000200: historical segment 534|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-534.png)|
|an-7a2b17a3fb0f-p000200: historical segment 548|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-548.png)|
|an-7a2b17a3fb0f-p000200: historical segment 563|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-563.png)|
|an-7a2b17a3fb0f-p000200: historical segment 593|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-593.png)|
|an-7a2b17a3fb0f-p000200: historical segment 595|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-595.png)|
|an-7a2b17a3fb0f-p000200: historical segment 634|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-634.png)|
|an-7a2b17a3fb0f-p000200: historical segment 635|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-635.png)|
|an-7a2b17a3fb0f-p000200: historical segment 642|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-642.png)|
|an-7a2b17a3fb0f-p000200: historical segment 646|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000200.mark-646.png)|
|an-a73d22211479-p000301: historical segment 12|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-12.png)|
|an-a73d22211479-p000301: historical segment 14|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-14.png)|
|an-a73d22211479-p000301: historical segment 15|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-15.png)|
|an-a73d22211479-p000301: historical segment 16|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-16.png)|
|an-a73d22211479-p000301: historical segment 38|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-38.png)|
|an-a73d22211479-p000301: historical segment 55|two|Not fixed: the marked row is now part of a three-row final crop.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-55.png)|
|an-a73d22211479-p000301: historical segment 56|two|Partly: four rows became two crops, each still containing two rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-56.png)|
|an-a73d22211479-p000301: historical segment 57|two|Partly: one row is separated; the other final crop still contains three rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-57.png)|
|an-a73d22211479-p000301: historical segment 61|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000301.mark-61.png)|
|an-d3237d690aa0-p000138: historical segment 64|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-d3237d690aa0-p000138.mark-64.png)|
|an-d3237d690aa0-p000138: historical segment 170|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-d3237d690aa0-p000138.mark-170.png)|
|an-d83e7a198ade-p000099: historical segment 13|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-d83e7a198ade-p000099.mark-13.png)|
|an-d83e7a198ade-p000099: historical segment 17|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-d83e7a198ade-p000099.mark-17.png)|
|an-d83e7a198ade-p000099: historical segment 20|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-d83e7a198ade-p000099.mark-20.png)|
|an-d83e7a198ade-p000099: historical segment 46|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-d83e7a198ade-p000099.mark-46.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 10|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-10.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 18|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-18.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 73|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-73.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 78|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-78.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 83|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-83.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 113|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-113.png)|
|s2-200e977f2dab5291c42c-p00035: historical segment 122|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00035.mark-122.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 0|two|Partly: the main row follows its bend; the adjacent straight crop still includes neighbouring row text.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-0.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 1|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-1.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 18|two|Partly: the main row is isolated by the field; a detached line beginning and a contaminated adjacent straight crop remain.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-18.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 19|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-19.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 22|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-22.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 24|two|Fixed: the target and neighbouring body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-24.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 27|two|Partly: the main curved row is isolated, but the neighbouring straight crop still contains several row edges.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-27.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 28|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-28.png)|
|s2-3229200bf47ca465a42d-p00004: historical segment 30|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00004.mark-30.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 65|two|Fixed: the main sentence and adjacent rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-65.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 76|two|Partly: the two rows are separated, but letters from their other neighbours still enter the crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-76.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 78|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-78.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 80|two|Partly: the main curved row is isolated; adjacent straight crops still include other rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-80.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 82|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-82.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 86|two|Partly: curved body rows are isolated, but the adjacent straight crop still contains neighbouring letters.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-86.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 90|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-90.png)|
|s2-49598b2e848ab1f0ee1e-p00001: historical segment 98|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00001.mark-98.png)|
|s2-6419488b7f8e69fd20da-p00001: historical segment 29|two|Outside this round: the sideways table is passed through unchanged; orientation is parked.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-6419488b7f8e69fd20da-p00001.mark-29.png)|
|s2-831443dc5e6f1ccfbaf5-p00020: historical segment 138|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00020.mark-138.png)|
|s2-831443dc5e6f1ccfbaf5-p00020: historical segment 154|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00020.mark-154.png)|
|s2-831443dc5e6f1ccfbaf5-p00020: historical segment 188|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00020.mark-188.png)|
|s2-831443dc5e6f1ccfbaf5-p00020: historical segment 203|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00020.mark-203.png)|
|s2-831443dc5e6f1ccfbaf5-p00020: historical segment 226|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00020.mark-226.png)|
|s2-831443dc5e6f1ccfbaf5-p00020: historical segment 273|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00020.mark-273.png)|
|an-00f143ecce59-p000117: historical segment 12|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-00f143ecce59-p000117.mark-12.png)|
|an-00f143ecce59-p000192: historical segment 27|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-00f143ecce59-p000192.mark-27.png)|
|an-00f143ecce59-p000258: historical segment 2|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-00f143ecce59-p000258.mark-2.png)|
|an-1be60011c435-p000066: historical segment 17|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-1be60011c435-p000066.mark-17.png)|
|an-1be60011c435-p000120: historical segment 48|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-1be60011c435-p000120.mark-48.png)|
|an-2cfe28da5103-p000084: historical segment 6|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000084.mark-6.png)|
|an-2cfe28da5103-p000084: historical segment 16|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000084.mark-16.png)|
|an-2cfe28da5103-p000084: historical segment 18|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000084.mark-18.png)|
|an-2cfe28da5103-p000084: historical segment 19|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-2cfe28da5103-p000084.mark-19.png)|
|an-3352d912f2e9-p000029: historical segment 4|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-3352d912f2e9-p000029.mark-4.png)|
|an-3352d912f2e9-p000055: historical segment 1|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-3352d912f2e9-p000055.mark-1.png)|
|an-3352d912f2e9-p000055: historical segment 3|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-3352d912f2e9-p000055.mark-3.png)|
|an-3352d912f2e9-p000055: historical segment 7|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-3352d912f2e9-p000055.mark-7.png)|
|an-778126cc8c2b-p000007: historical segment 19|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-778126cc8c2b-p000007.mark-19.png)|
|an-778126cc8c2b-p000011: historical segment 11|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-778126cc8c2b-p000011.mark-11.png)|
|an-778126cc8c2b-p000011: historical segment 13|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-778126cc8c2b-p000011.mark-13.png)|
|an-7a2b17a3fb0f-p000012: historical segment 2|two|Partly: two body rows are isolated; an extra thin smudge-only crop remains.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-7a2b17a3fb0f-p000012.mark-2.png)|
|an-9ea1564fcf4f-p000170: historical segment 98|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-9ea1564fcf4f-p000170.mark-98.png)|
|an-9ea1564fcf4f-p000202: historical segment 12|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-9ea1564fcf4f-p000202.mark-12.png)|
|an-9ea1564fcf4f-p000202: historical segment 25|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-9ea1564fcf4f-p000202.mark-25.png)|
|an-9ea1564fcf4f-p000202: historical segment 87|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-9ea1564fcf4f-p000202.mark-87.png)|
|an-9ea1564fcf4f-p000218: historical segment 133|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-9ea1564fcf4f-p000218.mark-133.png)|
|an-a73d22211479-p000047: historical segment 37|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000047.mark-37.png)|
|an-a73d22211479-p000141: historical segment 11|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000141.mark-11.png)|
|an-a73d22211479-p000141: historical segment 12|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000141.mark-12.png)|
|an-a73d22211479-p000141: historical segment 50|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000141.mark-50.png)|
|an-a73d22211479-p000141: historical segment 51|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000141.mark-51.png)|
|an-a73d22211479-p000141: historical segment 69|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-a73d22211479-p000141.mark-69.png)|
|an-b9d6f9c086e2-p000162: historical segment 2|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000162.mark-2.png)|
|an-b9d6f9c086e2-p000162: historical segment 3|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000162.mark-3.png)|
|an-b9d6f9c086e2-p000162: historical segment 15|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000162.mark-15.png)|
|an-b9d6f9c086e2-p000162: historical segment 27|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000162.mark-27.png)|
|an-b9d6f9c086e2-p000162: historical segment 81|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000162.mark-81.png)|
|an-b9d6f9c086e2-p000255: historical segment 7|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-7.png)|
|an-b9d6f9c086e2-p000255: historical segment 8|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-8.png)|
|an-b9d6f9c086e2-p000255: historical segment 38|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-38.png)|
|an-b9d6f9c086e2-p000255: historical segment 39|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-39.png)|
|an-b9d6f9c086e2-p000255: historical segment 46|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-46.png)|
|an-b9d6f9c086e2-p000255: historical segment 48|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-48.png)|
|an-b9d6f9c086e2-p000255: historical segment 63|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-63.png)|
|an-b9d6f9c086e2-p000255: historical segment 69|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-69.png)|
|an-b9d6f9c086e2-p000255: historical segment 70|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000255.mark-70.png)|
|an-b9d6f9c086e2-p000370: historical segment 5|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000370.mark-5.png)|
|an-b9d6f9c086e2-p000370: historical segment 15|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000370.mark-15.png)|
|an-b9d6f9c086e2-p000370: historical segment 29|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-b9d6f9c086e2-p000370.mark-29.png)|
|an-e74539ae215c-p000633: historical segment 70|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/an-e74539ae215c-p000633.mark-70.png)|
|s2-200e977f2dab5291c42c-p00025: historical segment 9|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00025.mark-9.png)|
|s2-200e977f2dab5291c42c-p00025: historical segment 14|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00025.mark-14.png)|
|s2-200e977f2dab5291c42c-p00025: historical segment 68|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-200e977f2dab5291c42c-p00025.mark-68.png)|
|s2-31f40cef90235c91b023-p00001: historical segment 18|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-31f40cef90235c91b023-p00001.mark-18.png)|
|s2-31f40cef90235c91b023-p00001: historical segment 42|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-31f40cef90235c91b023-p00001.mark-42.png)|
|s2-31f40cef90235c91b023-p00001: historical segment 63|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-31f40cef90235c91b023-p00001.mark-63.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 0|two|Fixed: the two visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-0.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 5|two|Partly: the upper row is isolated, but the marked lower row remains in a broad crop with neighbour letters.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-5.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 6|two|Partly: the target curved row is isolated; the adjacent crop contains neighbour remnants.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-6.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 7|two|Partly: the main row is isolated, but the next row includes a neighbour edge and a tiny extra sliver remains.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-7.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 8|two|Partly: upper row isolated; lower crop still includes the following row edge.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-8.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 9|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-9.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 10|two|Partly: target curved row isolated; upper straight crop still includes neighbouring rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-10.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 17|two|Fixed: main and adjacent body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-17.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 22|two|Partly: main and upper rows isolated; lower straight neighbour remains contaminated.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-22.png)|
|s2-3229200bf47ca465a42d-p00002: historical segment 23|one|Retained: marked single row is tighter; spatial match also finds a complete neighbouring row.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00002.mark-23.png)|
|s2-3229200bf47ca465a42d-p00003: historical segment 4|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00003.mark-4.png)|
|s2-3229200bf47ca465a42d-p00003: historical segment 13|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00003.mark-13.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 7|two|Partly: target and upper rows isolated; a detached beginning of another row remains a separate crop.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-7.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 13|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-13.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 14|two|Fixed: the two main rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-14.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 17|two|Partly: main row is separated but its crop retains neighbour text and a stepped edge.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-17.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 18|two|Fixed: both main rows are separately cropped along the bend.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-18.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 20|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-20.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 25|two|Partly: target and next row isolated; the previous short row still includes neighbour fragments.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-25.png)|
|s2-3229200bf47ca465a42d-p00006: historical segment 26|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00006.mark-26.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 4|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-4.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 19|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-19.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 27|two|Partly: main row still includes the next row at the curled ends; a detached word and tiny extra crop remain.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-27.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 44|two|Partly: main row has a neighbour fragment at the right end; a detached word remains.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-44.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 51|two|Partly: the two target rows follow the bend separately; another matched row is split into body and end fragment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-51.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 57|two|Fixed: visible body rows follow their curves in separate crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-57.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 68|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-68.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 72|two|Fixed: the two body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-72.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 76|two|Partly: target row follows bend; upper straight crop retains neighbour letters.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-76.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 85|two|Partly: two main curved rows separated; another matched row has a detached right-end word.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-85.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 105|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-105.png)|
|s2-49598b2e848ab1f0ee1e-p00004: historical segment 109|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00004.mark-109.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 0|two|Partly: the lower row is separated; upper crop still holds two rows and a thin extra strip remains.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-0.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 1|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-1.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 2|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-2.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 3|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-3.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 4|two|Partly: the two rows are separated but both retain neighbouring row edges; next curved row is isolated.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-4.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 5|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-5.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 6|two|Partly: body rows separated, but an extra clipped text strip remains and row edges still enter both crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-6.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 8|two|Partly: body rows separated but both crops still hold neighbouring row edges.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-8.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 9|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-9.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 10|two|Partly: main rows separated; an extra half-height text strip remains.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-10.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 11|two|Partly: main row separated but neighbour text remains, with a clipped upper-row strip.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-11.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 13|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-13.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 14|two|Fixed: target and neighbouring body rows follow the curve separately.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-14.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 15|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-15.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 16|two|Fixed: visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-16.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 17|two|Not fixed: all three matched crops still include parts of neighbouring rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-17.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 18|two|Fixed: both body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-18.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 19|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-19.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 20|two|Partly: target row is isolated; the upper straight crop still includes two rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-20.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 21|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-21.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 22|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-22.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 25|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-25.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 27|two|Partly: target row isolated; both adjacent straight crops include neighbouring rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-27.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 39|two|Fixed: main and neighbouring rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-39.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 45|two|Fixed: main and upper body rows have separate curved crops; the short lower row is a complete row end.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-45.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 57|two|Partly: main row isolated; upper straight crop remains contaminated.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-57.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 76|two|Partly: main curved row isolated; other matches include a contaminated short row and a detached row end.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-76.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 82|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-82.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 84|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-84.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 86|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-86.png)|
|s2-49598b2e848ab1f0ee1e-p00005: historical segment 94|two|Fixed: main and upper rows have separate curved crops; the short lower crop is the complete end of its row.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-49598b2e848ab1f0ee1e-p00005.mark-94.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 1|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-1.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 7|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-7.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 9|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-9.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 11|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-11.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 13|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-13.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 23|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-23.png)|
|s2-74cdb23a34ca4a6cd01e-p00007: historical segment 37|one|Retained: the marked single row is tighter and follows its bend; adjacent matches are separate rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-74cdb23a34ca4a6cd01e-p00007.mark-37.png)|
|s2-831443dc5e6f1ccfbaf5-p00007: historical segment 273|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00007.mark-273.png)|
|s2-831443dc5e6f1ccfbaf5-p00039: historical segment 93|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00039.mark-93.png)|
|s2-831443dc5e6f1ccfbaf5-p00039: historical segment 134|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00039.mark-134.png)|
|s2-831443dc5e6f1ccfbaf5-p00042: historical segment 195|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-831443dc5e6f1ccfbaf5-p00042.mark-195.png)|
|s2-86865c33eef5932c013b-p00023: historical segment 2|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00023.mark-2.png)|
|s2-86865c33eef5932c013b-p00023: historical segment 6|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00023.mark-6.png)|
|s2-86865c33eef5932c013b-p00026: historical segment 7|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00026.mark-7.png)|
|s2-86865c33eef5932c013b-p00026: historical segment 24|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00026.mark-24.png)|
|s2-86865c33eef5932c013b-p00026: historical segment 25|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00026.mark-25.png)|
|s2-86865c33eef5932c013b-p00026: historical segment 31|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00026.mark-31.png)|
|s2-c3ccfa3cea1347d7ad54-p00002: historical segment 1|two|Partly: the main row follows its bend; upper straight crop still includes neighbouring text.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-c3ccfa3cea1347d7ad54-p00002.mark-1.png)|
|s2-c3ccfa3cea1347d7ad54-p00002: historical segment 2|two|Partly: lower curved row is isolated; upper straight crops retain several row edges and a tiny extra sliver remains.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-c3ccfa3cea1347d7ad54-p00002.mark-2.png)|
|s2-c3ccfa3cea1347d7ad54-p00002: historical segment 19|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-c3ccfa3cea1347d7ad54-p00002.mark-19.png)|
|s2-d12a9a4feb23254f4080-p00006: historical segment 2|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00006.mark-2.png)|
|s2-d12a9a4feb23254f4080-p00006: historical segment 4|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00006.mark-4.png)|
|s2-d12a9a4feb23254f4080-p00006: historical segment 8|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00006.mark-8.png)|
|s2-d12a9a4feb23254f4080-p00006: historical segment 10|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00006.mark-10.png)|
|s2-d12a9a4feb23254f4080-p00006: historical segment 12|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00006.mark-12.png)|
|s2-d12a9a4feb23254f4080-p00006: historical segment 14|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00006.mark-14.png)|
|s2-d12a9a4feb23254f4080-p00008: historical segment 9|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-d12a9a4feb23254f4080-p00008.mark-9.png)|
|s2-3229200bf47ca465a42d-p00005: historical segment 0|two|Fixed: both body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00005.mark-0.png)|
|s2-3229200bf47ca465a42d-p00005: historical segment 6|two|Partly: main row follows the bend; a detached row end and contaminated adjacent straight crop remain.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00005.mark-6.png)|
|s2-3229200bf47ca465a42d-p00005: historical segment 7|two|Partly: upper and lower rows have curved crops; middle crop still includes the lower neighbour edge, with a tiny sliver.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00005.mark-7.png)|
|s2-3229200bf47ca465a42d-p00005: historical segment 13|two|Partly: main and upper rows are isolated; the adjacent row is split into body and end fragment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00005.mark-13.png)|
|s2-3229200bf47ca465a42d-p00005: historical segment 14|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00005.mark-14.png)|
|s2-3229200bf47ca465a42d-p00005: historical segment 23|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00005.mark-23.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 1|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-1.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 4|two|Partly: target row isolated; neighbouring straight crops retain other rows and a detached beginning.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-4.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 6|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-6.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 7|two|Partly: target and upper curved rows isolated; lower straight crop remains contaminated.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-7.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 11|two|Partly: upper and lower rows follow their bends, but the marked middle row still includes neighbour text.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-11.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 13|two|Fixed: target and adjacent body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-13.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 15|two|Fixed: the two body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-15.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 16|two|Fixed: target and adjacent body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-16.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 19|two|Partly: target row isolated; upper straight crop retains neighbouring row text.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-19.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 22|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-22.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 23|two|Partly: target and upper rows isolated; lower straight crop still includes other rows.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-23.png)|
|s2-3229200bf47ca465a42d-p00008: historical segment 27|two|Fixed: both visible body rows have separate curved crops.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-3229200bf47ca465a42d-p00008.mark-27.png)|
|s2-86865c33eef5932c013b-p00025: historical segment 7|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00025.mark-7.png)|
|s2-86865c33eef5932c013b-p00025: historical segment 9|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00025.mark-9.png)|
|s2-86865c33eef5932c013b-p00025: historical segment 10|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00025.mark-10.png)|
|s2-86865c33eef5932c013b-p00025: historical segment 25|two|Not fixed: exact R5 polygon; the owner-marked extra row or word remains inside the segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00025.mark-25.png)|
|s2-86865c33eef5932c013b-p00025: historical segment 28|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00025.mark-28.png)|
|s2-86865c33eef5932c013b-p00025: historical segment 36|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00025.mark-36.png)|
|s2-86865c33eef5932c013b-p00029: historical segment 12|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00029.mark-12.png)|
|s2-86865c33eef5932c013b-p00029: historical segment 13|one|Retained: exact R5 polygon; the owner-marked single row remains one segment.|[crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/acceptance/s2-86865c33eef5932c013b-p00029.mark-13.png)|
