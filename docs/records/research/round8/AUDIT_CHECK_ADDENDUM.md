# Dated audit correction — FP8ao, 15 October 2026

This is an additive companion to the audit records at `2f1c91a09b844c87696b95b6c89cd5c3ff7beede`. It supersedes their delivery/pending-review wording and qualifies the claims below; it does not rewrite the worker's original receipts, owner words, judgments or machine records. Read this with [REPORT_R8-AUDIT-02-i1.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/round8/REPORT_R8-AUDIT-02-i1.md), [ITERATION_HANDOFF.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/round8/ITERATION_HANDOFF.md), its JSON counterpart and the audit addendum to SOL_WORKER_HANDOFF at that commit. The audit documents are already integrated on the stack/merged branches; this planner branch does not import their runtime or duplicate the 17-file audit package.

Source: the full independent [R8-AUDIT-02 i1 check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-AUDIT-02-i1_check.md), ACCEPT WITH NOTES, plus the coordinator's delivery/private-result relay. Planner read the check and records, inspected Git identities, and changed documentation only. No new visual inspection, timing, page processing or private-page access is claimed here.

## 1. Delivery and independent review are complete

The worker could not stage; the runner then executed its validated fallback and committed **`2f1c91a09b844c87696b95b6c89cd5c3ff7beede`**. The checker verified all 17 committed documents against the fallback hashes. Thus “no worker commit”, “HEAD remains be6a1ca” and “independent review pending” remain historical statements about worker delivery, not current status. Audit scope is DONE at 1/1, independently ACCEPT WITH NOTES. Physical, architectural and speed goals remain PARTIAL.

Checked runtime is **`046bd52dddeea7ada7727971f1038d34328ba5b7`**; no audit runtime/test change. Integration heads verified read-only: stack `843480a7b6a2e5d9b6d3c0e7a0cd0ec9fddccec3`; ff-merged `b75808bfc05ceb9cc321e8f474a4c8ce10cc93fe`. Audit worker: Sol 6.1/high, `01a13c9d-54fb-7312-aee8-bb3b0807e1a3`, ff8-review / astra/ff-review. Existing 430-pass/15-strict-xfail and bare 429-pass/one-skip/15-xfail receipts are legitimately reused, not newly executed by the audit or planner. No private44 repeat was needed; the latest INK check reported 44/44 unchanged, correction −0.6 ms versus detector −0.9 ms, noise.

## 2. Timing is descriptive, with substantial within-run load drift

Forward corrections median/p95/max are 264.4/1766.8/2735.1 ms; reverse 264.6/1992.8/3311.6 ms. Pages ≥1 s: 29 forward, 32 reverse, union 32. Aggregate detector drift +5.674% already invalidates a paired speed conclusion. It also hides much larger swings: the reverse first half ran about 20–25% slower, the second half about 8% faster. The reverse-only crossings on 3229 p4, 44b5 p3 and 74cd p6 are load effects. Do not call 32 a stable population or infer a regression against the earlier 187–195 ms censuses. The agreement40 set is not certified clean; its timing cannot close negligible clean-page overhead.

Field proposals are about 41% of correction cost and total corrections about 3.5 times primary detection in these descriptive runs. Earlier paired Python gains remain attached to the R8-04 source/sample (field −5.1/−5.6%, total −3.3/−2.6%). The off-default M17 pilot and exact-but-9.3%-slower Rust field batch are separate results; neither is a final default speed gain.

## 3. Masks and export metadata have different accounting

Against R7 52cee3b: 15,093 → 15,094 items, 205/208 pages mask-identical, six improved lines on three pages, all exclusion polygons/masks identical. Separately, `type_support_chains` differs on **33 items / 10 pages**, without changing crops: 4959 p1/p4/p5, 3229 p6, 2cfe p84, d83e p99/p115, 00f1 p258, ef48 p181, c0b0 p10. “Entire difference” applies to crop masks, not complete export files.

## 4. Retained gains have remaining physical defects

Do not describe six clean lines. The checker's actual-mask/Otsu proxy measures about 4,518 shared ink pixels between 4959 p5 #103 and legacy neighbour #22; 3229 p2's unchanged next row retains about 5,473 pixels of the improved lower row's ink. These are coarse ink proxies, not exact character counts. The lower B row follows glyph outlines, not a smooth band. The new 8686 body still has a clipped risen end and inherited neighbour overlap. The clean shared boundary between 4959 #107/#105 is a retained narrow success; it is not whole-page tessellation. General `final_export` remains off, numerical backend Python, `bend=False`.

## 5. Condition 4-01 has a narrower pass than its title

The historical checklist contains 1 closed, 13 partial, 5 not closed and 1 superseded. The 4-01 pass covers frozen detector model/map/postprocess, separate decode/startup accounting and recorded threads. **No detector Rust binding contract was delivered.** Treat that part of its title as open, not implied by the narrow acceptance-text pass. Leave the original grade intact with this explicit qualification. Superseded 2b-08 remains administrative: its physical promotion conditions were never met.

## 6. Machine-record limitations remain visible

`AUDIT_MECHANISMS.json` mixes actual lists and JSON-encoded lists in providers/default_callers/current_modules; checklist entries share four broad evidence pointers. Their prose is specific, but automated consumers need explicit normalization and item-level links before relying on these fields as a schema. No such repair is claimed by this closure.

The inherited definition counts 6/9/9/7 have a taxonomy caveat: M33 `geometry_envelopes.correct`'s relative .06 mean-3h mask is not obviously mapped to the nine ink entries. The checker did not establish a counting error, so neither invent a tenth definition nor present nine as a newly exhaustive census. The conclusion is unchanged: competing policies were not consolidated. Six copied modules (485 lines), M06's propagation subpolicy, cache infrastructure and duplicate atlas input authority were removed; M06's own reflected-glyph votes remain. Live runtime versus R7 still grew +1,651/−731 lines (net +920), with optional/offline code accounted separately.

## Closure and pending scope

The active allocation is closed: **22 used + 3 retired + 1 parked FONT = 26; zero launchable slots**. FONT is not retired or automatically resumed. Both owner questions remain pending/unallocated: (a) field-band crops beyond anchors plus flat/no-curl and binding-side detection; (b) field-path resolution/passes for speed. Exact density-domain and deferred audit-list hypotheses, retained ghosts on ef481610 p151 items 19/23/36, M55/frame support, font/row/source dependencies and the faint-front xfail remain backlog. No new implementation is authorised by an audit note.

See the [owner closing note](OWNER_CLOSING_SUMMARY.md) for the conditional recommendation. No next prompt, launch, default change or private-page run is part of FP8ao.
