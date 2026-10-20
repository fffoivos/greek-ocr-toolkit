# N1-T phase A build

**Bed packs ready; calibration awaits the lead's 27 dash assignments. No reading run, probe, owner-sheet replacement or label edit occurred.**

Phase A is **207 distinct lines, 2129 slots**: the union of every current owner-sheet card's line and every line with an exact Google `-` in a 4+-digit token read in a VALID historical r1 context. The summary's cards hash binds the current sheet input. The historical r1 keys, answers, gates and successful run/v4-scan provenance were independently checked. No partial N1-R2 folders or decisions are consumed. Every selected line is in a step1 document; `greekocr.numerics.locks` rejects reserved lines before crop/geometry access. Selection: `artifacts/n1/n1t/selection.json`.

`line_complete.py` uses `tokens.py` without normalisation: all numeric tokens, every adjacent-digit gap including empty gaps, and both boundaries. Exact W1 text/label/DocAI anchors must agree. **2128 geometry OK; 1 failures**. The failed slot is `elstat--fa8be8ddafd5c043--s000-l0110:t0:s2` (reversed digit boxes); it remains in enumeration for lead review and is excluded from reader packs. No geometry is guessed. For line-edge boundary windows, the exact neighbouring symbol edge or crop edge is used, rather than an estimated digit-width extension. Rendering reuses the v3 margin triangles and original marker-preserving renderer; existing outputs remain unchanged. Every render has a side measurement record in `n1t/slots.jsonl`. Native collector Python regenerates SHA-verified crops into scratch only; x86 Python 3.11/Pillow 10.4 renders. An initial inherited-architecture crop import failed before rendering and was corrected with an explicit arm64 collector invocation.

**Dash geometry:** 128 slots have qualifying horizontal components. Single-stroke proposals: hyphen 54, en dash 10, em dash 54; 10 multi-stroke slots remain geometrically ambiguous. Each component records native length, height, height/digit-height, vertical centre/digit-band and length/median width of **all token digits**, derived from exact symbol anchors. The component criterion is fixed (`width >= max(3 pixels, 2*height)`, wholly inside the gap); crossing digit components are retained in raw measurements but not classified as strokes. The starting thresholds **0.75 and 1.45** are reported, never fitted or tuned. A measured type is a proposal, not ink truth.

Histogram by exact Google gap (unit: qualifying components, not slots; multi-stroke slots contribute more than once):

| Google exact gap | <0.75 | 0.75–<1.45 | ≥1.45 | unavailable |
|---|---:|---:|---:|---:|
| `""` | 22 | 1 | 1 | 0 |
| `" "` | 3 | 0 | 0 | 0 |
| `" - "` | 3 | 0 | 0 | 0 |
| `","` | 1 | 0 | 0 | 0 |
| `", "` | 3 | 1 | 0 | 0 |
| `",- "` | 0 | 1 | 2 | 0 |
| `",-- "` | 0 | 0 | 1 | 0 |
| `"-"` | 30 | 6 | 30 | 0 |
| `"- "` | 1 | 0 | 0 | 0 |
| `"--"` | 0 | 2 | 0 | 0 |
| `"."` | 3 | 0 | 0 | 0 |
| `". "` | 1 | 0 | 3 | 0 |
| `". -"` | 0 | 0 | 1 | 0 |
| `". - "` | 0 | 0 | 8 | 0 |
| `". – "` | 0 | 1 | 0 | 0 |
| `".-"` | 1 | 0 | 2 | 0 |
| `".- "` | 2 | 2 | 10 | 0 |

**Dash controls:** `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_review/dash_controls.png` contains all 27 approved hyphen/dash controls, with their original cell numbers 49–81 (rejected numbers stay absent), marked zooms and a ruler representing one median token digit width at the displayed zoom scale. No ratio or geometric type is printed. Private measurement/index: `n1t/dash_controls_index.json`. Lead-entry template: `controls/dash_types_template.jsonl` (`truth`: `hyphen`, `en dash`, `em dash`). All 27 values remain null; no lead truth was invented.

**Packs:** 27 contexts × 2 independent readers, 54 folders, 4742 items including repeated controls. 2128 distinct bed slots occur exactly once per reader. Each context has 9 distinct approved **non-dash** controls, including ≥1 raised dot, and at most 89 items. The 55 non-dash approvals allow packs to be built without inventing dash-control truth. r2 reverses the entire r1 order (including controls), uses fresh opaque IDs, and changes every option letter's meaning. Private keys/measurements stay under `artifacts/n1/n1t/`; public packs under `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1t` contain only item lists and hash-named, metadata-free PNGs. Every item uses all ten sep2 meanings.

**Closure 54/54 PASS**, independently verified against sealed manifests; all 54 real bed-folder launcher dry runs pass without probes or reads. `run_n1.sh` now accepts `n1cal2`/`n1t`, isolates their keys/answers/ledgers from old N1, and selects unchanged `sep2.md`. A fixture calibration of 82 controls also passes closure and launcher dry-run. **The real `n1cal2/cal01/r1` pack is intentionally absent:** its builder refuses with “Lead dash types pending for 27 controls” until the lead fills all dash assignments. Resume with `n1t_packs.py --calibration`; this validates and seals all 82 truths before writing a pack.

**Combiner v2:** `n1t_combine.py` requires both complete sep2 readings and successful run/v4 scanner provenance. Two independent, high-confidence agreeing VALID reads produce a truth candidate. A VOID read is secondary-only and cannot replace either required VALID vote. All other states remain lead_review, including unreadable/other/low-confidence, disagreement, geometry failure, and dash reader/geometry disagreement. Edit candidates are exact Google `-`/`.` → U+00B7 only for raised-dot truth candidates with grammar `thousands` among the slot's candidates; range/thousands alternatives are retained explicitly. All dash label outcomes are tags only; no training label is edited.

**Owner sheet v2:** `owner_v2.py` and `n1t_owner_sheet.py` are fixture-tested only. The production builder refuses before complete N1-T readings and decisions, then uses the prescribed cleanup renderer and the same target `artifacts/n1/owner_sheet/n1_sheet.html`. Cards use the line ID for note identity; all numeric slots are boxed/numbered, every non-nothing render has a gap-numbered zoom, full Google/Ours/Gaps rows name marks and confidence, and Printed is prefilled from Ours with `data-printed-source="ours-proposal"`. Unsure gaps retain Google's exact substring. Group order and the three-sentence intro follow the owner's ruling; agreement-only cards are sampled deterministically to at most 12, with omitted agreement lines recorded in the spec. The existing sheet/cards/spec/summary remain byte-identical. Fixture HTML rendering verifies prefill and data attributes. No production owner sheet is published or replaced.

**Tests: 125 passed**, including meaningful fixtures for complete enumeration and locks, threshold boundaries, multi-stroke ambiguity, every sep2 meaning, gate failure and VOID roles, exact edit direction, dash cross-checks, pack isolation/reversal/permutations, calibration refusal, closure tampering, launcher dry runs and the actual owner renderer. JUnit: `N1T_TESTS.xml`, `N1T_IMAGE_TESTS.xml`. The historical frozen pre-reading manifest test is excluded because preserved old r1 packs now carry runtime files; production N1-T seals are independently verified. No N1-R2 tests or products are used.

**Codex estimate:** 4742 bed/control appearances + 82 calibration items = **4824 items**, at 0.2 points/100 = **9.648 points**. Build ran no live usage probe; this is an estimate, not metered consumption. Detailed counts, hashes, gates, failure, dry runs and custody are in `artifacts/n1/N1T_RECEIPT.json`. Network OFF; no `.git` writes, collector-root writes, `run.lock`, reserved-line rendering, fitting, reader execution, or publication.

## N1-Tb

**READY.** This section supersedes the original pack/count and calibration-pending statements above. Lead dash types are sealed in `controls/dash_types.jsonl`, SHA256 `fb600648c3ded3739f37e1acd47c9b5d9a5c8088645f7906df558f36f2459c45` (sidecar `.jsonl.sha256`). Assignments: 14 hyphens, 6 en dashes, 5 em dashes, 2 unsure cells (61/64) scored as any dash; every non-dash answer is wrong, including unreadable on these two controls. The template is preserved.

All 2,129 slots remain in `n1t2/slots.jsonl` on the same 207 complete lines. Exclusive reason counts, with geometry failures first: **637 google-mark** (any nonempty Google substring, including spaces), **391 ink-only**, **1 geom-fail**, **30 audit** = **1059 read slots**. The remaining **1070 geometry-only slots** have `nothing (geometry)` decisions, preserved in the full line record. Audit seed: `20261017:N1Tb:geometry-audit`; 30 slots selected by SHA256 rank from the geometry-only pool before removal. Audited slots require both readings and do not inherit automatic decisions.

Ink screening retains any component bounding box intersecting a positive-width gap beyond digit-box edges, including crossing-component overhangs; this conservative screen may retain extra slots. It uses every component, not just horizontal strokes, with no fitted threshold. The one failed geometry is included using the complete native line plus a 3× whole-line zoom, without a fabricated gap marker; its truth still requires lead review.

**Packs:** 14 contexts ×2 readers under `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1t2`, plus `n1cal2/cal01/r1` (82 calibration items). Nine distinct controls per bed context include ≥1 raised dot and ≥1 each hyphen/en/em dash. Reverse order, fresh IDs, deranged option letters, ten sep2 meanings, and private measurements retain the N1-T structure. The original 54 `n1t` folders and private records remain byte-identical and superseded, inventoried with hashes in `n1t2/superseded.json`. The launcher explicitly accepts `n1t2`; post-reading combiner/owner builder now target that root.

The combiner requires both complete readings for every selected slot, including audit/failure slots, and inserts geometry-only nothing decisions for omitted slots. Owner rows preserve every gap and the complete Ours line, with geometry provenance named; nothing/space slots are not boxed. The existing owner sheet has not been rebuilt.

**Closure 29/29 PASS** on all new packs; dry runs PASS for all new folders and all 54 preserved `n1t` folders. **142 tests passed**, JUnit `N1Tb_TESTS.xml` and `N1Tb_IMAGE_TESTS.xml`. One historical pre-reading manifest test remains excluded because old r1 packs contain runtime files; preserved N1-T and new packs are independently sealed and verified. **Codex estimate:** 2370 bed/control appearances + 82 calibration = **2452 items**, at 0.2 points/100 = **4.904 points** (original estimate 9.648). No live usage probe, reading run, network, `.git` write, label edit, collector write, or owner-sheet publication. Receipt: `artifacts/n1/N1Tb_RECEIPT.json`.


## N1-CAL2S

**PASS.** Independent re-score of the 17:05 calibration v2 raw answers: **81/82 correct**, including **24/25 typed dashes**, raised dot **4/4**, **zero** non-raised controls answered as raised dot, and **one disagreement**. All four lead requirements pass. The two unsure cells (61/64) accept hyphen, en dash or em dash; both were answered em dash and count as correct.

**File custody:** every one of the seven current shared `artifacts/n1/answers/cal01.r1.*` files is byte-identical to `git show 1a779e810:<path>`. They belong to the first calibration (`sep.md`), rollout `01a149fc-3d7d-7801-8b2e-27461de372e3` (16:10). No overwrite occurred. Those committed bytes were restored by copy into `artifacts/n1/answers/n1cal/`. The seven v2 files were already under `artifacts/n1/n1cal2/answers/`, rollout `01a14a2e-d39a-7853-a077-96a2db799001` (17:05, `sep2.md`); they were copied into `artifacts/n1/answers/n1cal2/`. All source files remain intact. Each run was checked against its run JSON, launcher log, rollout session ID and pack path, codexlog session ID, exact ordered public/private item IDs and option maps, pack answers, prompt, mapped slots and successful v4 scan. Per-file original/copy hashes and provenance are in `artifacts/n1/N1CAL2S_RECEIPT.json`.

The generic “hyphen or dash” score belongs to the first calibration. The v2 source score already distinguishes dash types and is exactly equal to the independent re-score from `controls/approved.jsonl` plus `controls/dash_types.jsonl`. The scorer now explicitly accepts and validates that second seal against the calibration key, rejecting missing/duplicate assignments or incomplete mapped populations. A fresh derived score, including confusion matrix, disagreement list and lead gate, is saved as `answers/n1cal2/cal01.r1.N1CAL2S.score.json`; copied historical outputs remain byte-exact.

| Approved class | Correct / total | Accuracy |
|---|---:|---:|
| Raised dot | 4/4 | 100% |
| Baseline dot | 21/21 | 100% |
| Comma | 23/23 | 100% |
| Hyphen | 14/14 | 100% |
| En dash | 5/6 | 83.33% |
| Em dash | 5/5 | 100% |
| Unsure dash (any dash) | 2/2 | 100% |
| Nothing | 7/7 | 100% |

Confusion matrix (rows = sealed truth; columns = decoded answer):

| Truth \ Answer | Raised | Baseline | Comma | Hyphen | En | Em | Nothing |
|---|---:|---:|---:|---:|---:|---:|---:|
| Raised | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| Baseline | 0 | 21 | 0 | 0 | 0 | 0 | 0 |
| Comma | 0 | 0 | 23 | 0 | 0 | 0 | 0 |
| Hyphen | 0 | 0 | 0 | 14 | 0 | 0 | 0 |
| En | 0 | 0 | 0 | 1 | 5 | 0 | 0 |
| Em | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| Unsure dash | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| Nothing | 0 | 0 | 0 | 0 | 0 | 0 | 7 |

**Disagreement:** `kd4ec059384`, slot `gazette_modern--98dfb00fa203c6d5--s000-l0025:t0:s7`: sealed **en dash**, answered **hyphen**. No truth was changed. The HOLD-only contact sheet is not required for this PASS.

**Paths fixed:** launcher and mapper share a validated output-stem helper: `artifacts/n1/answers/<root>/<context>.<reader>.*` for all five roots (`n1`, `n1cal`, `n1cal2`, `n1t`, `n1t2`). The mapper CLI now takes `--root`, `--context`, optional `--reader` and `--output-base` instead of an arbitrary positional destination. The N1-T combiner consumes the same canonical directory. Reader log labels include the root, and usage-probe scratch output follows the root answer directory. No two roots share an output path. Real closure/dry-run checks pass for `n1cal/cal01/r1`, `n1cal2/cal01/r1` and `n1t2/ctx01/{r1,r2}` without probes or reader execution. An initial plain-Python dry run hit the local Pillow architecture mismatch before execution; all checks then passed with the explicit arm64 collector environment.

**Tests: 176 passed** (113 integration/regression, 15 targeted, 48 additional regression/rendering); JUnit `N1CAL2S_TESTS.xml`, `N1CAL2S_TARGETED_TESTS.xml`, `N1CAL2S_REGRESSION.xml`. The historical frozen pre-reading manifest test remains deselected because completed old packs contain runtime files; real requested packs independently pass completed-pack closure. Tests cover exact gate thresholds and independent HOLD conditions, root isolation, mapper CLI, combiner consumption, seal/mapping rejection and fake-reader refusal/overwrite behavior. Network OFF; no `.git` writes, real reading run, usage probe, label edits, pack mutation or owner-sheet replacement.

## N1-TS phase 1

Calibration v2 PASS (81/82). No reading run or network use. Two high-confidence VALID votes required; VOID votes are secondary only. Control `unreadable` (u) abstains except on unsure-dash controls, where only a dash type is accepted. No label edits applied.

| Context | r1 wrong | u | control gate | usable | r2 wrong | u | control gate | usable |
|---|---:|---:|---|---|---:|---:|---|---|
| ctx01 | 0 | 0 | VALID | INVALID | 1 | 0 | VALID | VALID |
| ctx02 | 2 | 0 | VOID | VOID | 0 | 0 | VALID | VALID |
| ctx03 | 1 | 0 | VALID | VALID | 2 | 0 | VOID | VOID |
| ctx04 | 0 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |
| ctx05 | 0 | 0 | VALID | VALID | 2 | 0 | VOID | VOID |
| ctx06 | 2 | 0 | VOID | VOID | 1 | 0 | VALID | VALID |
| ctx07 | 0 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |
| ctx08 | 1 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |
| ctx09 | 0 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |
| ctx10 | 1 | 0 | VALID | VALID | 1 | 0 | VALID | VALID |
| ctx11 | 0 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |
| ctx12 | 0 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |
| ctx13 | 0 | 0 | VALID | VALID | 1 | 0 | VALID | VALID |
| ctx14 | 0 | 0 | VALID | VALID | 0 | 0 | VALID | VALID |

ctx01.r1 has 0 wrong controls but failed the recorded v4 scan: an absolute-path write to `/tmp/ocr_write_placeholder`. It is INVALID for voting. Its canonical answer copy was recovered from the existing completed pack; see `artifacts/n1/n1t2/answer_recovery.json`. The failed scan was preserved.

Both-VOID re-read contexts: none.

Decisions: 1479/2129 (409 read; 1070 nothing by geometry); lead_review 650. Reasons use exclusive precedence: geometry unavailable, dash mismatch, invalid provenance, VOID, unreadable/other, low confidence; two usable conflicting votes are disagreement.

| lead_review reason | slots |
|---|---:|
| dash_geometry_disagreement_or_unavailable | 40 |
| geometry_unavailable | 1 |
| invalid_context_provenance | 76 |
| low_confidence | 45 |
| reader_disagreement | 66 |
| unreadable_or_other | 118 |
| void_context | 304 |

Decided meanings: {"nothing": 1151, "space": 88, "baseline dot": 132, "comma": 63, "em dash": 16, "hyphen": 15, "raised dot": 12, "en dash": 2}.

Google × ours over ALL decided slots (geometry-only included; dash types are named tags):

| Google | Ours | slots |
|---|---|---:|
| "" | baseline dot | 2 |
| "" | comma | 1 |
| "" | nothing | 1150 |
| "" | space | 76 |
| " " | space | 9 |
| " - " | hyphen | 1 |
| "," | baseline dot | 4 |
| "," | comma | 37 |
| ", " | comma | 23 |
| ",-" | comma | 1 |
| "-" | em dash | 9 |
| "-" | en dash | 2 |
| "-" | hyphen | 14 |
| "-" | raised dot | 11 |
| "-." | baseline dot | 1 |
| "." | baseline dot | 113 |
| "." | comma | 1 |
| "." | raised dot | 1 |
| "." | space | 3 |
| ". " | baseline dot | 2 |
| ". " | em dash | 1 |
| ". - " | em dash | 2 |
| ".," | baseline dot | 2 |
| ".-" | baseline dot | 3 |
| ".-" | em dash | 1 |
| ".- " | em dash | 3 |
| ".-." | baseline dot | 1 |
| ".." | nothing | 1 |
| "...." | baseline dot | 1 |
| "......" | baseline dot | 1 |
| ".–" | baseline dot | 2 |

Geometry-only audit: both raw reads say nothing on 17/30; 9/30 also qualify as decided nothing after gates/confidence. These are evidence about the pruned population, not validation of every geometry-only slot. Full slot-level audit in `artifacts/n1/N1TS_PHASE1.json`.

Lead sheets: 24 raised cells; 120 seeded review cells; 13 sheets. Raised pages carry 8 targets + 4 approved references; review pages have at most 12 targets. Seed `20261017:N1TS:review`. Deferred review counts: {"void_context": 253, "unreadable_or_other": 100, "reader_disagreement": 55, "invalid_context_provenance": 56, "dash_geometry_disagreement_or_unavailable": 33, "low_confidence": 33}. Every deferred slot/reason is in `sheets_index.json`; the template includes them with an empty sheets list. They still require rulings before phase 2.

Sheets: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_review/t_lead`. Index: `sheets_index.json`. Lead input: `artifacts/n1/lead_t_template.jsonl` (set truth to a sep2 meaning or `keep Google`; null is pending). A slot appearing in both sets has one ruling. All raised reads are included even from VOID/INVALID contexts.

Phase 2 is implemented but NOT RUN. After the lead fills every required ruling and says go, run `n1ts.py --phase 2 --lead-approved`. This revalidates source hashes, complete readings, decisions, controls and both-VOID blocks, applies rulings, builds owner sheet v2 and writes a summary. Dash label outcomes stay tag-only; only exact Google -/. → · in grammar-thousands slots can be edit candidates. Current owner sheet is preserved.

Validation: **108 tests passed** (`artifacts/n1/N1TS_TESTS.xml`), covering unsure-dash/u gates, failed-scan exclusion, seeded review selection, complete raised/review/template coverage, lead overrides and missing/duplicate/stale/blocked ruling refusal, and complete phase-2 rendering/summary in a temporary fixture. Phase 2 has not run on production. All five existing owner-sheet product hashes are unchanged. Visual checks covered raised sheets 1/3 and review sheets 1/4, including the unlocalized geometry failure. No .git writes.

## N1-TS phase 2

**READY.** Local owner sheet v2 rebuilt at `artifacts/n1/owner_sheet/n1_sheet.html`: **25.66 MB** (25,660,433 bytes), **207 complete-line cards**, Printed prefilled from Ours on all cards. The lead republishes to the same URL. No network, `.git` write, reading run, probe or training-label edit. The previous phase-1 owner cards and HTML are archived byte-identically under `n1t2/phase1_owner_*` and checked against the phase-1 receipt.

The 24 raised cells were mapped through the sealed scratchpad `t_lead/sheets_index.json` into `artifacts/n1/lead_t.jsonl`: **18 raised dot, 2 baseline dot, 2 nothing, 2 hold (too faint)**. The original template remains intact. SHA256 `eff4bcb39750b6d99b462356d7772d0d55972ec1d8844130e320ebfbf8e520e6`, sidecar `lead_t.jsonl.sha256`. Cells 18 and 22 get U+00B7 despite being outside the thousands grammar. The other label-edit rule is unchanged; 18 lead-verified edit candidates are recorded but no labels are edited.

**Partial authority:** 22 resolved lead rulings (12 reaffirm existing decisions), with **640 unresolved slots** remaining, including holds 1/2. No review-sheet cell receives a ruling just because it was displayed. Every unresolved slot keeps Google in Ours and has an `unsure:<reason>` Gaps entry and card tag. Only lead-verified or agreeing VALID two-read raised dots enter the raised-hyphen group.

| Group | Cards |
|---|---:|
| Raised dot written as hyphen by Google | 16 |
| Dash type differs from Google | 17 |
| Other disagreements | 76 |
| Needs a look | 94 |
| Agreement sample (12) | 4 |

**Boxes:** 162 changed (red solid), 257 unchanged (green solid), **639 unsure (amber dashed)**. All 1,070 geometry-only nothing slots stay named in Gaps and unboxed. One additional unsure slot, `elstat--fa8be8ddafd5c043--s000-l0110:t0:s2`, has reversed digit boxes: it has no physical gap box or number location, retains its whole-line zoom and explicit misaligned/unsure Gaps entry, and is excluded from the drawn-box counts. No coordinates were guessed. Other numbers use the original slot number even after unboxed slots are omitted. Physical raster QA and a dashed/solid raster test passed.

The intro includes the required dashed-outline sentence. Google/Ours names, typed dashes, zooms, editable prefill and line IDs remain. To preserve the two existing owner notes across the slot-to-line change, the shipped note loader reads the SHA-bound legacy slot IDs only when no line note exists, retaining explicitly edited Printed text. A mocked execution of the shipped JavaScript verifies both notes and the absence of remote writes; live remote note loading is not verified offline.

### Geometry-only audit

**Not safe as a transcription rule.** Both readers said nothing on 17/30; **13/30 disagree**. Five are space-only disagreements, while **8 slots include non-space calls**. One baseline-dot slot has two VALID high-confidence votes. The 1,070 automatic nothing proposals are retained provisionally for this requested sheet, not qualified by this audit; the lead should widen the read set. No broader read set was generated or run.

| Audit slot | r1 meaning / confidence / context gate | r2 meaning / confidence / context gate | Both nothing |
|---|---|---|---|
| `bsb_poly1850--515c78c513c1c8c5--s005-l0101:t4:s2` | nothing / high / VALID | nothing / high / VOID | yes |
| `bsb_poly1850--767e91eee85d9120--s004-l0038:t0:s3` | nothing / high / VALID | nothing / high / VALID | yes |
| `bsb_poly1850--97801b0bc5afce27--s005-l0001:t1:s2` | space / high / VALID | space / high / VALID | NO |
| `bsb_poly1850--97801b0bc5afce27--s005-l0050:t0:s6` | space / high / VALID | space / high / VALID | NO |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0045:t0:s0` | nothing / high / VALID | baseline dot / high / VOID | NO |
| `elstat--07520765bc203a33--s000-l0103:t0:s1` | nothing / high / VALID | nothing / low / VALID | yes |
| `elstat--24e6586813212fd1--s000-l0020:t1:s4` | nothing / high / VALID | nothing / high / VALID | yes |
| `gazette_modern--2e613d9290dd13d4--s000-l0139:t0:s0` | nothing / high / VALID | space / high / VALID | NO |
| `gazette_modern--5abbf39e5b783318--s000-l0133:t1:s1` | nothing / high / VALID | nothing / high / VALID | yes |
| `gazette_modern--a5a65c413f92193f--s000-l0053:t0:s4` | nothing / high / VALID | nothing / high / VALID | yes |
| `gazette_modern--f9ac91c777f49b67--s000-l0107:t0:s8` | nothing / high / VOID | nothing / high / VALID | yes |
| `ia_greek_latin--1214ff90d3c31fcb--s000-l0001:t0:s0` | space / high / VALID | space / high / VALID | NO |
| `ia_greek_latin--2b4cfc7c6d70fd98--s000-l0006:t2:s3` | nothing / high / VALID | nothing / high / VALID | yes |
| `ia_greek_latin--2b4cfc7c6d70fd98--s000-l0016:t0:s7` | other / high / VALID | other / high / VALID | NO |
| `ia_greek_latin--7156a8b65e724719--s002-l0004:t1:s0` | unreadable / low / VALID | unreadable / low / VALID | NO |
| `ia_greek_latin--7156a8b65e724719--s002-l0026:t1:s6` | other / high / VALID | other / low / VALID | NO |
| `ia_greek_latin--f42ec9d8d21af31b--s000-l0085:t2:s0` | nothing / high / VOID | nothing / high / VALID | yes |
| `ia_poly1850--c39403323b6d5d89--s005-l0053:t1:s1` | nothing / high / VOID | nothing / high / VALID | yes |
| `ia_russian--3ecca278cf0eea22--s001-l0004:t1:s5` | nothing / high / VALID | nothing / high / VALID | yes |
| `ia_russian--6cfc00f06e0f7241--s004-l0045:t0:s7` | nothing / high / VALID | nothing / high / VALID | yes |
| `lekythos--3bfc4a385d61b883--s002-l0043:t0:s1` | nothing / high / VALID | nothing / high / VALID | yes |
| `lekythos--dcfa99599048d352--s000-l0165:t1:s7` | nothing / low / VALID | other / high / VALID | NO |
| `lekythos--ff539dec2e1680a7--s001-l0068:t0:s5` | other / high / VALID | other / high / VALID | NO |
| `nlg--3d71f4f87abea186--s007-l0021:t1:s1` | nothing / high / VALID | nothing / high / VALID | yes |
| `nlg--3d71f4f87abea186--s007-l0021:t3:s0` | space / high / VALID | space / high / VALID | NO |
| `nlg--3d71f4f87abea186--s007-l0021:t3:s1` | nothing / high / VOID | nothing / high / VALID | yes |
| `serbia--557369d8d117b91a--s000-l0185:t0:s19` | baseline dot / high / VALID | baseline dot / high / VALID | NO |
| `serbia--557369d8d117b91a--s000-l0356:t0:s66` | comma / high / VALID | nothing / high / VALID | NO |
| `serbia--557369d8d117b91a--s000-l0356:t0:s86` | nothing / high / VALID | nothing / high / VOID | yes |
| `serbia--557369d8d117b91a--s000-l0356:t0:s89` | nothing / high / INVALID | nothing / high / VALID | yes |

Non-space disagreements requiring widened lead review:

- `bsb_poly1850--fccefa9e9f9823aa--s000-l0045:t0:s0`: baseline dot.
- `ia_greek_latin--2b4cfc7c6d70fd98--s000-l0016:t0:s7`: other.
- `ia_greek_latin--7156a8b65e724719--s002-l0004:t1:s0`: unreadable.
- `ia_greek_latin--7156a8b65e724719--s002-l0026:t1:s6`: other.
- `lekythos--dcfa99599048d352--s000-l0165:t1:s7`: other.
- `lekythos--ff539dec2e1680a7--s001-l0068:t0:s5`: other.
- `serbia--557369d8d117b91a--s000-l0185:t0:s19`: baseline dot.
- `serbia--557369d8d117b91a--s000-l0356:t0:s66`: comma.

Reader totals: r1 {"nothing": 20, "space": 4, "other": 3, "unreadable": 1, "baseline dot": 1, "comma": 1}; r2 {"nothing": 18, "space": 5, "baseline dot": 2, "other": 4, "unreadable": 1}.

### Third-reader triage

| Fresh r3 reason | Original phase-1 slots | Remaining after lead rulings |
|---|---:|---:|
| VOID | 304 | 301 |
| invalid provenance | 76 | 75 |
| disagreement | 66 | 63 |
| low confidence | 45 | 40 |

**479 slots in 6 contexts**, fresh seeded order `20261017:N1TS2:r3:fresh`, reader `r3`, root `n1t3`, unchanged `sep2.md`. Packs: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1t3`; private keys, slots and controls: `artifacts/n1/n1t3/`. Nine distinct approved controls per context include raised dot and each typed dash. At most 89 items per context, 54 controls total, 533 appearances. New opaque IDs, fresh option permutations and order distinct from both previous readers are checked. **Closure 6/6 and launcher dry runs 6/6 PASS. No r3 answers, logs, probes or readings.**

Deferred outside this r3 selection: {"unreadable_or_other": 118, "dash_geometry_disagreement_or_unavailable": 40, "lead_hold_too_faint": 2, "geometry_unavailable": 1}. A third vote can pair only with an existing VALID high-confidence vote; it cannot by itself repair geometry/dash conflicts or establish truth with a VOID/INVALID vote. Two faint lead holds remain unresolved.

**Tests: 145 passed**, `artifacts/n1/N1TS2_TESTS.xml`. Includes partial/hold authority, out-of-thousands lead edits, complete pending retention, real control/pack seals, fresh r3 order/IDs, physical dashed boxes and original numbering, existing combiner/geometry/mapper/scorer regressions, and shipped-JS note compatibility. Historical scorer tests use the SHA-verified old sheet archive; custody tests permit only the specifically authorized owner-output replacement. Receipt: `artifacts/n1/N1TS2_RECEIPT.json`.

## N1-TS3

**READY.** Folded the completed six-context r3 reading into independent control, scan and pack-provenance gates. Two agreeing VALID, high-confidence votes establish a truth candidate; geometry and typed-dash gates still apply. Sealed lead rulings override, including the two faint holds. No labels were edited.

Historical phase-2 lead_review: **640**. With the mirrored/show-through row explicitly excluded, the comparable pre-r3 count is **639**, falling to **467** after r3. All **5 slots** on `lekythos--dcfa99599048d352--s000-l0144` have no truth or edit candidate and carry `suspect:mirrored` / `excluded:show_through`; they are excluded from scoring and edits. Unresolved slots retain Google in Ours.

| lead_review reason | Historical phase 2 | Before r3, exclusion applied | After r3 |
|---|---:|---:|---:|
| dash_geometry_disagreement_or_unavailable | 40 | 39 | 66 |
| geometry_unavailable | 1 | 1 | 1 |
| invalid_context_provenance | 75 | 75 | 144 |
| lead_hold_too_faint | 2 | 2 | 2 |
| low_confidence | 40 | 40 | 13 |
| reader_disagreement | 63 | 63 | 62 |
| unreadable_or_other | 118 | 118 | 119 |
| void_context | 301 | 301 | 60 |

R3 resolves 172 previously unresolved slots. Another 27 slots gain a reading consensus but remain withheld by the typed-dash geometry gate. A failed r3 context may change the exclusive unresolved reason to invalid provenance; earlier valid votes are retained and are not newly voided. The receipt preserves every before/after reason transition.

### Canonical v4.4 reconciliation

Scanner SHA256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547` matches the canonical source. The old copy is retained as `scripts/secondary/reading/scan_rollout_secondary_pre_v44.py`. Every original scan is preserved beside its replacement as `*.scan.pre_v44.json`. The scanner file itself is copied verbatim.

**45 recorded attempts checked: 41 clean, 4 VOID; no previously clean rollout became VOID. No failed context was newly accepted.** The archived failed calibration launch has no rollout and remains VOID. Clean scans are ACCEPTED for scan purposes; control gates still apply. Scan-VOID contexts have INVALID voting provenance and cannot establish truth. Failed-scan r3 answers were copied from completed sealed packs for secondary evidence only; no reader was launched.

| Recorded attempt | Old scan | v4.4 scan | Old findings | New findings |
|---|---|---|---:|---:|
| `cal01.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx01.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx02.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx03.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx04.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx05.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx06.r1` | clean | ACCEPTED | 0 | 0 |
| `ctx07.r1` | clean | ACCEPTED | 0 | 0 |
| `failed_nested_attempt_N1CAL/cal01.r1` | VOID | VOID | 1 | 1 |
| `n1cal/cal01.r1` | clean | ACCEPTED | 0 | 0 |
| `n1cal2/cal01.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx01.r1` | VOID | VOID | 2 | 2 |
| `n1t2/ctx01.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx02.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx02.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx03.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx03.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx04.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx04.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx05.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx05.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx06.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx06.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx07.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx07.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx08.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx08.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx09.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx09.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx10.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx10.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx11.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx11.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx12.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx12.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx13.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx13.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx14.r1` | clean | ACCEPTED | 0 | 0 |
| `n1t2/ctx14.r2` | clean | ACCEPTED | 0 | 0 |
| `n1t3/ctx01.r3` | clean | ACCEPTED | 0 | 0 |
| `n1t3/ctx02.r3` | clean | ACCEPTED | 0 | 0 |
| `n1t3/ctx03.r3` | clean | ACCEPTED | 0 | 0 |
| `n1t3/ctx04.r3` | clean | ACCEPTED | 0 | 0 |
| `n1t3/ctx05.r3` | VOID | VOID | 3 | 2 |
| `n1t3/ctx06.r3` | VOID | VOID | 2 | 2 |

Still-VOID findings:

- `artifacts/n1/answers/failed_nested_attempt_N1CAL/cal01.r1.run.json`: old: missing rollout: .. New: no rollout; failed launch rc=2.
- `artifacts/n1/answers/n1t2/ctx01.r1.run.json`: old: absolute path outside reader_dir [/tmp/ocr_write_placeholder]; absolute path outside reader_dir [/tmp/ocr_write_placeholder]. New: absolute path outside reader_dir [/tmp/ocr_write_placeholder]; absolute path outside reader_dir [/tmp/ocr_write_placeholder].
- `artifacts/n1/answers/n1t3/ctx05.r3.run.json`: old: absolute path outside reader_dir [/zoom/group1.png]; image provenance: unmatched image provenance; absolute path outside reader_dir [/zoom/detail57.png]. New: absolute path outside reader_dir [/zoom/group1.png]; image provenance: unmatched image provenance.
- `artifacts/n1/answers/n1t3/ctx06.r3.run.json`: old: absolute path outside reader_dir [/tmp/noop_unused]; absolute path outside reader_dir [/tmp/noop_unused]. New: absolute path outside reader_dir [/tmp/noop_unused]; absolute path outside reader_dir [/tmp/noop_unused].

The only removed finding is ctx05/r3 record 257 (`/zoom/detail57.png`); its other path finding and unmatched returned image remain. Complete old/new findings, reader directories, scan hashes and disposition reasons are in `artifacts/n1/N1TS3_SCANS.json` and the receipt.

| r3 context | Wrong controls | Abstentions | Control gate | Scan | Voting gate |
|---|---:|---:|---|---|---|
| ctx01.r3 | 1 | 0 | VALID | ACCEPTED | VALID |
| ctx02.r3 | 0 | 0 | VALID | ACCEPTED | VALID |
| ctx03.r3 | 1 | 0 | VALID | ACCEPTED | VALID |
| ctx04.r3 | 0 | 0 | VALID | ACCEPTED | VALID |
| ctx05.r3 | 2 | 0 | VOID | VOID | INVALID |
| ctx06.r3 | 0 | 0 | VALID | VOID | INVALID |

Each read is bound to its private option map and sealed pack manifest, approved typed controls, answer bytes, run metadata and current v4.4 scan receipt. Every r3 slot matches the corresponding original slot record. Final decisions and all per-read gates: `artifacts/n1/n1t3/combined_decisions.json`.

### Lead sheets

`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_review/t_lead/geo_audit.png`: **17 cells**, all 13 geometry-audit slots with a non-nothing call plus four seeded both-nothing anchors (`N1TS3:anchors`). Each cell carries the marked zoom, line, both original reads and geometry record; `geo_audit_template.jsonl` retains the full record and image hashes. The geometry-only rule remains provisional; this sheet supplies evidence for lead review, with no new ruling inferred.

`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_review/t_lead/raised_r3.png`: **0 newly raised candidates**. No previously unruled slot gains a raised-dot truth candidate from r3. The sheet states this explicitly and includes the approved raised/baseline references; `raised_r3_template.jsonl` is empty. Existing lead-raised rulings are retained.

### Owner sheet under the cap

`artifacts/n1/owner_sheet/n1_sheet.html`: **12.49 MB** (12,490,750 bytes), **207 complete-line cards**. Native line pixels are converted to gray PNG with the existing colored solid/dashed boxes and number lane; they are never enlarged. Zooms are grayscale JPEG quality 85 and only retained for slots with a Google mark or a saved gap component. Empty-gap zooms, including the unlocalized whole-line duplicate zoom, are omitted. The complete unlocalized line and unsure Gaps record remain.

**No card groups were cut; the seeded 40-card fallback was unnecessary.** The intro, named Gaps row, Printed prefill, line note identities and legacy note loader remain. Unsure means unresolved after r3; the excluded mirrored row is explicitly tagged.

| Group | Cards |
|---|---:|
| Raised dot written as hyphen by Google | 16 |
| Dash type differs from Google | 26 |
| Other disagreements | 87 |
| Needs a look | 71 |
| Agreement sample (12) | 7 |

Drawn boxes: **225 changed, 365 unchanged, 468 unsure**. The one misaligned slot remains unlocalized and is not included in drawn-box counts. Geometry-only empty slots stay unboxed, including on the excluded row. Physical raster examples were inspected; tests decode every embedded line PNG to verify native width and height plus the 30-pixel numbering lane and check JPEG quality tables. No live remote note-store or browser UI claim is made.

**Tests: 204 passed**, `artifacts/n1/N1TS3_TESTS.xml`. Includes three-vote majority, invalid/VOID/low-confidence exclusions, all scan reconciliations, lead authority, mirrored exclusion, complete sheet/template coverage, native image dimensions, size cap, control/pack seals, historical custody through original scan archives and legacy note compatibility. Launcher tests use local fake readers/probes only. No production reading run or network call. Receipt: `artifacts/n1/N1TS3_RECEIPT.json`.
