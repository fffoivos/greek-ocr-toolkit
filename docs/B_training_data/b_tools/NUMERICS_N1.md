# Numeric separator correction — N1 / tool 0.3

## Purpose

Repair a narrowly qualified numeric-label error: Google `-` or `.` where the print has a raised dot **· (U+00B7)**. Preserve digits, true ranges and every unedited raw byte. `docs/harvest/line_pipeline/tool_versions.json` names **numerics 0.3**: the unchanged assisted separator release plus the census03 digit/separator/digit automatic-negative integration; the failed automatic ink candidate is disabled. The released W1 overlay is **n1_v1_w1**, not the earlier fitted rule or a general punctuation model.

## Owner rules it implements, quoted

`docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md` quotes the owner, 17 Oct:

> the dots replaced by hyphens for numbers are the most serious; create a model for punctuation in numbers the same way we did for accents.

`docs/records/labelfix/secondary/PLAN.md` records the standing rule:

> Labels are the ink. Misprints stay. No correction may override the image.

The numeric plan's one-directional specification says:

> Never touch ranges where ink shows a hyphen-length stroke.

The initial “grammar proposes, ink decides” design is historical. The automatic rule failed; current W1 corrections require two admitted agreeing raised-dot reads and a completed lead pixel ruling. Grammar or vertical thresholds alone do not authorize a correction.

## Version history

| Version / record | Behavior and status |
| --- | --- |
| Step 0 | Numeric token/slot census and U+00B7 convention; no general correction release. |
| N1 automatic candidate / tool 0.1 | Frozen ink threshold; locked-eval raised precision **0/5**, rejected and never applied to training. |
| Assisted N1 / tool 0.2 (historical release) | Two-reader evidence plus lead pixel check for accepted separators. |
| Tool 0.3 (current binding) | Automatic no-candidate result only when no digit/separator/digit pattern exists; unrelated punctuation is not a numeric candidate. The rejected ink rule remains disabled. |
| n1_v1_train | v2 train artifact: **0 edits**, 85 dash tags; not a successful automatic-rule application. |
| N1W1 preparation | Exact ADM5c-admitted W1 ELSTAT subset, 1,312 parent rows; dedicated frozen helpers and sealed packs. |
| N1W1F2 | Sparse raw-text overlay: 22 confirmed edits, 41 new raised agreements pending lead review; superseded by F3. |
| N1W1F3 / n1_v1_w1 | **63 confirmed edits**, 629 output rows (63 edited,566 hold-only), **679 held slots**; current manifest-selected assisted artifact. |

The final SHA is `94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e`. Do not consume F2's earlier 22-edit SHA or imply that W2 corrections already exist; the secondary hand-off plans W2 after admission.

## Inputs

W1 raw Google **text**, exact admitted row IDs/document metadata, exact DocAI digit symbol/text-anchor geometry, crop hashes, frozen release exclusions and local reserved-document/line locks, sealed reader packs/answers, scanner/control/coverage evidence, and lead rulings bound to review sheet and crop hashes. `n1_v1_w1` inherits `google_raw_w1`, whose frozen feature-file hash is `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c`.

The W1 selected parent has 1,312 admitted ELSTAT rows. All selected labels were byte-equal to W1 raw text, establishing exact offset correspondence without remapping. The initial earlier ADM4 preparation was never read and is superseded; its numbers must not replace ADM5c.

## Algorithm in prose

`greekocr/numerics/tokens.py` is a lossless **ASCII-digit** span grammar, without Unicode normalization. Maximal runs contain digits joined by `· · . , - – —` or spaces. Every adjacent digit pair supplies a slot, including empty gaps; token boundaries supply two more slots. Thousands proposals have 1–3 initial digits followed by groups of three, optionally a decimal suffix. Decimal is a final comma/period plus 1–2 digits. Range proposals are ascending 1–4-digit groups separated by one dash, with optional spaces; four-digit years are included. Two or more spaces or an adjacent explicit bar/tab can propose table boundaries. These labels are grammar, not printed truth.

W1 candidate enumeration narrows this to interior single Google `-`/`.` slots in maximal tokens with **at least four ASCII digits**. Ranges remain in the census but are never edit-eligible. Localization uses exact W1 DocAI digit geometry, not projection/proportional fallback. Reserved slots remain visible as holds and enter neither packs nor pixel processing.

Two blind reader rounds use fresh opaque IDs, reversed order and controls. Finalization admits only scanner-clean, correctly model/effort-bound, viewed logical votes under the context control gate; missing, VOID, invalid or unviewed observations cannot vote. More than one wrong viewed control, no correct viewed raised control or fewer than two viewed controls makes a context VOID. Replacement routing keeps logical roles distinct from physical contexts and does not replace valid evidence. An agreed raised dot still needs a lead ruling from pixels; range proposals/rulings always hold. No automatic ink classifier participates in the assisted release.

F3 materializes only the 63 completed rulings onto raw text. It verifies exact per-row diffs, original `-`/`.`, replacement U+00B7 and untouched UTF-8 segments. Settled baseline/dash-only rows are omitted and inherit raw text. Holds remain explicit; a row can contain both a confirmed edit and held slots. The integrated pipeline separately treats producer holds as unresolved, rather than admitting such a row as fully verified.

## Outputs and reason codes

`artifacts/n1/n1_v1_w1.jsonl` contains `text`, `parent_text`, edits, holds, explicit status and per-slot/read provenance. It has no inherited post-convention `label`. Companion manifest, `.sha256`, resolved pending record, F3 receipt and per-row verification preserve custody. Holds cover **105 disagreements +574 missing-two-usable-read slots =679**, including 40 reserved/unlocalized slots in the missing group. There are **582 rows with holds**, including 16 edited rows.

Integration accepts numeric edits only for `-`/`.`→`·`; other replacements fail `numeric result exceeds qualified separator edits`. Explicit producer holds become `required_evidence_unresolved`. A scan with none of `. - ·` can emit verified-no-change evidence; merely seeing a digit does not imply a separator correction. Dash tags do not change the text.

## Evidence: review sets and owner marks

Initial C1 ELSTAT **100 cards** had separator faults on **3/100**, while digits were correct on **98/100**. These are fault prevalence measurements on that C1 stratum, not N1 correction accuracy.

The automatic rule (SHA prefix 90080b5a) called five locked-eval baseline dots raised. The lead checked all five as baseline; raised precision **0/5**, zero false range edits. Its dev positives were concentrated in ELSTAT ee37…; held-out raised precision had **n=0**. The rule failed its ≥99% gate and remained a tag-only diagnostic. `N1G_GATE_FAIL.md` is authoritative over the earlier plan to ship an ink rule.

W1: **1,109 candidates** (1,102 periods,seven hyphens) on 891 rows; **1,069 localized /40 reserved holds**, all 857 required crops SHA-matched. Fourteen contexts×two initial rounds used 85–86 items each including nine controls. Replacement-aware finalization records **20/44 physical contexts VALID**, 21 VOID, three INVALID; effective routed logical contexts **19/28 VALID**, seven VOID,two INVALID. Candidate outcomes before lead checks: **63 raised /2 hyphen-dash /365 baseline /0 other /105 disagreement /574 missing** =1,109.

Lead review in `N1W1_LEAD_RAISED.md`: **22/22** original sheet cells and **41/41** replacement cells confirmed raised, total **63/63**. Dot centres are recorded at 55–73% of digit height, compared with approved raised and baseline references. Original 22 are ELSTAT ee37bc488988f1bd; the final edit set also includes daec83cb9a364cd1. These are **lead** marks, not new owner marks or an independent held-out precision sample of the release.

The final **63 edits on 63 rows** coexist with 679 held slots, so edit count alone is not coverage. LQB truth_v1_1 re-score has **zero edited rows overlapping truth**; its **103 separator truth items remain in-sample**, with **33 errors** and zero eligible paired separator headline items. This release has no measured held-out LQB separator improvement. Owner-facing N1 sheet and lead review have distinct purposes; no additional owner acceptance tally is asserted by these reports.

## Tests

Historical N1W1 preparation reports **38 passed**, including synthetic two-reader→lead→apply→LQB registration; exact population/exclusions, geometry, range vetoes, required lead checks, malformed/VOID/unviewed contexts, reuse/model/effort mismatch, reverse/fresh packs, partial holds and retry prevention. Relevant files: `tests/test_n1w1.py`, `test_n1w1_r3.py`, `test_numeric_tokens.py`, `test_numeric_locks.py`, `test_n1g.py`, `test_n1_score.py`. F3 serialized verification checks every emitted row's exact edits; it does not add new glyph adjudication. CLEAN5C did not execute these tests or finalizers.

## Known limitations

The automatic rule is rejected. Assisted corrections are concentrated in two ELSTAT documents, with many unresolved slots and no independent LQB edit coverage. Numeric text grammar cannot distinguish every table boundary from grouped values; ranges are protected conservatively. This release does not repair commas, digits or every dash class. Gate cells (A≤6 and >1 alnum), S4 small segments (≤8 characters and A≤6), and descriptive numeric cells (original width≤200,height≤40,≤10 visible chars) are separate definitions. No size rule authorizes N1 edits.

## Code paths

`greekocr/numerics/tokens.py` and locks/geometry helpers; dedicated `scripts/numerics/n1w1_*` finalizers/materializers, including `n1w1_f3.py`; reader drivers under `scripts/secondary/reading/`; `greekocr/harvest/line_pipeline.py` validation; `greekocr/harvest/numeric_cells.py` descriptive classification; `docs/records/labelfix/lqb/versions.json` for overlay loading. Evidence: `artifacts/n1/n1w1/r3/finalization/{N1W1F3_RECEIPT.json,f3_row_verification.json,f3_lqb_rescore.json}`.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `docs/harvest/line_pipeline/tool_versions.json`.
- `docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md`; `docs/records/labelfix/secondary/{PLAN.md,N1G_GATE_FAIL.md,N1W1_REPORT.md,N1W1_LEAD_RAISED.md,HANDOFF_20261018.md}`.
- `greekocr/numerics/tokens.py`; `greekocr/harvest/{numeric_cells.py,line_pipeline.py}`; `scripts/numerics/n1w1_f3.py` (materializer contract).
- `docs/records/labelfix/lqb/versions.json`; `greekocr/labelfix/lqb.py`; `tests/test_n1w1.py`; `tests/test_n1w1_r3.py` (targeted source reads).
