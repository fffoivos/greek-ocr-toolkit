# RU3T-0 — full remaining coverage ready

Prepared **1,631 lines / 1,896 candidate positions** across the same nine books. The 200 RU2T lines (233 positions) are excluded from these packs and retain their final decisions. Their frozen label file remains SHA-256 `b47c113ff926bf73adc9d76bb46d1ad443befbd014ae4c8a22c5d83c55ba40e8`. The disjoint union is exactly the RU2T census: 1,831 lines / 2,129 candidate positions.

No OCR readings, live limit probes, network, browser, computer use, or `.git` writes occurred. Production v3 labels, LQB registration/rescoring, and lead sheets are deferred to the finaliser after readings; only synthetic fixture finalisations ran here.

## Packs and budget

External pack root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru3t`. Private keys: `artifacts/ru1/ru3t/keys/`. The external-root guard passes and its repository-root rejection fixture passes. All 38 reader folders pass canonical pack closure. RU1 yer schema, globally fresh opaque IDs, exact reversed r2 assignments, 94–95 items per reader context. Each pair has 85–86 candidate lines and nine controls. There are 171 control items per reader, covering all 65 adjudicated positions.

Nineteen pairs produce **3,604 item reads**: 3,262 candidate-line reads and 342 control-line reads. Public masks include all terminal signs as in RU2T: **4,109 masked slots per reader**, including 358 control slots; 8,218 masked-slot reads total. The last-line `slots` value means the 1,896 new candidate positions, not every masked hard sign/control.

Codex planning estimate: **7.208 weekly points**, using the established 0.2 points/100 item reads. This excludes probes and any future fresh-r3 retries. RU2T's measured ledger has 590 item reads and 1 measured weekly points, suggesting 6.108 points by simple scaling; this is a weak estimate because seven of eight measured deltas are zero at the meter's precision. Its wall-time scaling is about 131.5 minutes, excluding new pack complexity and probe/validation overhead. No current balance or completion before the threshold is assumed.

## Driver

Run `scripts/secondary/reading/run_ru3t_all.sh` only when reader execution is intended. Order: ctx01–ctx19/r1, then ctx01–ctx19/r2, through the existing launcher with root `ru3t`, model `gpt-6.1-sol`, medium effort, reader network disabled.

The driver uses the existing limit-probe helper before each unattempted context, requires one valid 10080-minute weekly bucket, and stops at **≥70%**. It writes `artifacts/ru1/ru3t/STOPPED_AT_70.json` with contexts done and next context. A pre-existing stop marker prevents launches. The launcher retains its own before/after probes and applies the same 70% threshold for RU3T (the earlier RU2T route retains 78%). If its second pre-context probe reaches 70%, the driver records that stop too.

A process lock prevents concurrent drivers; a permanent exclusive attempt claim precedes every launcher invocation. Existing claims, run records, launcher logs or answers prevent repeats, including failed or interrupted attempts. Failed contexts require fresh-r3 review rather than retries. Results append to `context_results.jsonl`; complete output goes to per-context driver logs. A crash between claim and result remains visibly CLAIMED and is never retried automatically.

Offline checks: `scripts/secondary/reading/run_ru3t_all.sh --dry-run` and `scripts/secondary/reading/run_ru2t.sh ru3t ctx01 r1 --dry-run` both pass. The driver dry-run contains all 38 contexts in the required order and launches/probes nothing.

## Finaliser

`scripts/secondary/ru3t_finalize.sh` validates bound parent, frozen RU2T labels/decisions, tools, keys and pack hashes, and canonical v4.4 scanner SHA `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`. It checks model/effort, independent rollout hashes, canonical scan and control gates. VOID or failed contexts contribute no votes. Direct and temporally traced derived images count under RU2T-F3; only unviewed items lose their read. Positions lacking two admitted independent reads, disagreements and uncertain calls go to `lead_review`, leaving labels HOLD. Missing-read positions are listed in `fresh_r3_positions.jsonl` for fresh-ID independent r3 re-reading.

Only eligible parent `ь` positions can change to `ъ`, including pre-hyphen terminal positions as in RU2T. Original hard signs remain untouched. The combiner retains the RU1 edit rule; RU3T additionally excludes all VOID votes. RU2T final rows are inherited byte-equivalent as parsed records, including existing holds. `decisions_merged.jsonl` retains both populations. The registered parent is the original **collection_v2_train label**, not ru1_v2_train.

Normal output: `artifacts/ru1/ru1_v3_train.jsonl`, `_manifest.json`, `.sha256`. When the stop marker exists: `ru1_v3_train_partial.jsonl`, corresponding manifest/sha, and `artifacts/ru1/ru3t/covered_lines.txt`. The partial file still has all 214,436 original IDs; its covered-lines list identifies inherited RU2T lines plus new lines whose every candidate position has two admitted reads. Unread new candidates remain explicit HOLD.

Delivery renders lead-review cells and a seeded audit of 40 edit_hard + 20 keep_soft positions in `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/ru1_review/ru3t` using the retained geometry and same-book references. Agreement references and Google-label-only fallbacks are explicitly distinguished. If a partial population cannot provide 40/20, all available positions are sampled and the exact shortfall is reported, with no fabricated audit cells. Seed: `20261017:RU3T0:audit`.

The finaliser registers the full/partial version and invokes the existing offline LQB trend scorer against frozen truth v1.1, producing `docs/records/labelfix/lqb/score_<version>.json`, `artifacts/ru1/ru3t/lqb_delta.json`, and `FINALIZED_RECEIPT.json`. Registration, scores and sheets have been fixture-tested, not claimed as production results.

## Validation

- **27 RU3T fixtures passed**: frozen merge/parent, disjoint selection/reverse IDs, direct/derived/unviewed item coverage, VOID exclusion, missing/failed/wrong-model/forbidden/reused/incomplete contexts, disagreements, tamper rejection, partial mode, ordered driver, exact-70 stop, stop progress, failure/crash restart protection, malformed probe rejection, external-root guard, seeded 40/20 sheet generation, and LQB command/truth/version routing.
- **30 existing RU2T regression fixtures passed**.
- Shell syntax, all 38 closures, global uniqueness of 3,604 item IDs, all 65 control positions represented, complete candidate union, and both real-pack offline dry-runs passed.

Evidence: [receipt](../../../../artifacts/ru1/RU3T0_RECEIPT.json), [build](../../../../artifacts/ru1/ru3t/build.json), [closure](../../../../artifacts/ru1/ru3t/closure.json), [driver dry-run](../../../../artifacts/ru1/ru3t/driver_dry_run.jsonl), [RU3T tests](../../../../artifacts/ru1/ru3t/tests_ru3t.txt), [RU2T regressions](../../../../artifacts/ru1/ru3t/tests_ru2t_regression.txt).

RU3T0 READY: lines 1631, slots 1896; contexts 19 ×2; est 7.208 pts; closure ok; driver dry-run ok; finalizer tests 27 passed

## RU3T-R3

Prepared offline on 2026-10-18. No reader jobs, usage probes, browser, computer use, network calls, label writes, registry updates or `.git` writes. Original tools and their frozen build bindings remain unchanged.

### VOID causes

F1 calls eight contexts FAILED on canonical scan and four VOID on controls; all twelve are excluded readers for replacement. Each line below identifies the recorded finding, without interpreting glyphs.

- **ctx03/r1** — scan finding: 1 × absolute path outside reader_dir; 19 × unresolvable load expression.
- **ctx05/r1** — scan finding: 1 × absolute path outside reader_dir; 1 × image provenance: unmatched image provenance.
- **ctx06/r1** — control errors: 2 wrong signs / 17 scored controls; 0 abstentions.
- **ctx08/r1** — scan finding: 1 × image provenance: unmatched image provenance.
- **ctx09/r2** — scan finding: 18 × absolute path outside reader_dir.
- **ctx12/r2** — scan finding: 1 × absolute path outside reader_dir.
- **ctx13/r1** — control errors: 2 wrong signs / 19 scored controls; 0 abstentions.
- **ctx14/r1** — scan finding: 5 × image provenance: unmatched image provenance.
- **ctx15/r1** — control errors: 2 wrong signs / 17 scored controls; 0 abstentions.
- **ctx18/r1** — scan finding: 2 × absolute path outside reader_dir; 17 × unresolvable load expression.
- **ctx18/r2** — control errors: 2 wrong signs / 20 scored controls; 1 abstentions.
- **ctx19/r2** — scan finding: 10 × unresolvable load expression.

Systematic pattern: eight scanner failures involve path/provenance traceability (including unresolved `${load("base")}` expressions), while all four control failures have exactly two wrong signs. No context in this list became VOID from coverage alone. Gates and canonical scanner were not relaxed.

### Packs and routing

| New pack | Replaces | Items |
|---|---|---:|
| ctx03/r3 | ctx03/r1 | 95 |
| ctx05/r3 | ctx05/r1 | 95 |
| ctx06/r3 | ctx06/r1 | 95 |
| ctx08/r3 | ctx08/r1 | 95 |
| ctx09/r3 | ctx09/r2 | 95 |
| ctx12/r3 | ctx12/r2 | 95 |
| ctx13/r3 | ctx13/r1 | 94 |
| ctx14/r3 | ctx14/r1 | 95 |
| ctx15/r3 | ctx15/r1 | 95 |
| ctx18/r3 | ctx18/r1 | 95 |
| ctx18/r4 | ctx18/r2 | 95 |
| ctx19/r3 | ctx19/r2 | 95 |

Pack root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru3t`. The new root subfolders are `r3/ctxNN/r3/` and `r4/ctx18/r4/`. Every pack retains exactly the same public items, crop bytes, private slot attribution and controls as its original context. Orders use independent seeds `20261018:RU3T-R3:v1:<replaced-context/reader>`; all 1,139 opaque IDs are fresh and globally disjoint from the originals and each other. ctx18/r3 and ctx18/r4 have distinct orders. Private keys and build evidence are in `artifacts/ru1/ru3t/r3_replacements/`.

**Count reconciliation:** 1,139 item reads = 1,031 bed items + 108 control items. These cover 1,187 missing candidate read slots and 224 control slots. The 1,100-position scratchpad contains 1,195 missing-reader slots: the requested VOID replacements touch 1,093 positions and supply all missing roles for 1,092 positions if admitted. Eight missing slots in eight positions remain outside the requested twelve: ctx05/r2 (1), ctx10/r1 (3), ctx17/r1 (4). One of those positions also needs a requested VOID replacement. These are coverage gaps in otherwise admitted contexts; this preparation does not claim all 1,100 positions are repaired. The receipt lists the exact residual row/offset/reader triples.

**Codex estimate: 2.278 percentage points**, using the existing RU3T0 planning rate of 0.2 points per 100 item reads. Probe overhead is additional; this is an estimate, not measured usage.

### Driver and finaliser

Later execution: `bash scripts/secondary/reading/run_ru3t_r3_all.sh`. Offline preview: append `--dry-run`. It validates original and replacement input bindings and closure, probes immediately before every unattempted context, stops at weekly usage **>=70%**, persists the stop marker, and makes an exclusive permanent attempt claim before launch. Failed or interrupted attempts, existing answers, run evidence and launcher logs are never rerun. Reader configuration remains `gpt-6.1-sol`, `medium`, network off; the canonical scanner remains v4.4.

Updated replacement-aware finalisation entrypoint: `bash scripts/secondary/ru3t_r3_finalize.sh`. It routes each missing logical r1/r2 role to its assigned r3/r4 pack and uses the existing `collect_context` model, effort, independent-rollout, canonical-scan, control and per-item coverage gates. Original excluded readers are not reconsidered and cannot vote. Admitted physical reader/context identity is retained alongside the logical combiner role. The existing RU3T combiner, inherited RU2T merge and delivery remain in use. A replacement stop marker propagates partial-mode finalisation. Missing or rejected replacements remain lead review/HOLD. The original finalisation entrypoint remains bound to its frozen build; use this new entrypoint after replacement reads.

### Validation and receipt

All **12 pack closures** passed; offline driver preview lists **12** fresh contexts. **6 targeted fixtures** passed for offline preview, exact-70 stop, persistent stop, malformed-probe rejection, permanent failure claims, existing-answer protection and ctx18 physical routing with unchanged combination. **28 existing RU3T fixtures** passed. Both new shell entrypoints passed `bash -n`. No live finalisation was run.

[RU3TR3 receipt](../../../../artifacts/ru1/ru3t/RU3TR3_RECEIPT.json) · [build](../../../../artifacts/ru1/ru3t/r3_replacements/build.json) · [closure](../../../../artifacts/ru1/ru3t/r3_replacements/closure.json) · [dry-run](../../../../artifacts/ru1/ru3t/r3_replacements/driver_dry_run.jsonl)

RU3TR3 READY: void causes 8 scan + 4 control; r3/r4 contexts 12; items 1139; est 2.278 pts; closure ok; dry-run ok
