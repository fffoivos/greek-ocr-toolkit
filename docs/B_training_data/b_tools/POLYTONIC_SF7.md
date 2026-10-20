# Polytonic mark correction — SF7 / tool 0.7

## Purpose

Correct Greek polytonic marks using located letter slots, lexicon/constraint proposals, physical ink and saved mark-reader evidence. It is a label tool built on the segmenter's components and ownership geometry. It does not make Google or recogniser text into print truth. `docs/harvest/line_pipeline/tool_versions.json` names **polytonic 0.7**, scope **SF7 A; existing detector/readers; exact release candidate_pre_audit**. The manifest's seven generations are S1, S2, S3, S4, S5, SF6, SF7; detector S6 and intervening SF review fixes are separately named records, not extra invented tool versions.

## Owner rules it implements, quoted

The secondary standing rule, recorded in `docs/records/labelfix/secondary/PLAN.md`, applies to label corrections:

> Labels are the ink. Misprints stay. No correction may override the image.

`docs/records/labelfix/spellcheck/SF7_PREREGISTRATION.md` records owner GO via the coordinator, and the binding adoption condition:

> Nothing binds before the audit.

The same preregistration explicitly names variant A as the **owner's reader-alone rule**, with a detector-observed-below-mark exception for iota-subscript insertions; substitutions use reader alone. This is the SF7 amendment to the earlier lexicon-proposes/ink-decides contract, not a claim that every SF7 edit requires lexicon attestation. Deletions retain SF6's two positive absence signals.

## Version history

| Manifest generation / related record | Method and evidence |
| --- | --- |
| S1 | Strict attestation; deterministic constraints and lexicon propose, ink decides. CTC only locates. ACCEPT and HOLD separate. |
| S2 | Revised mark detector and print-truth instrument; unknown character ownership stays unknown. |
| S3 | Recall candidate; better subscript/merged-body handling, precision goal not met. |
| S4 | Retrained mark classifier on DEV and C1 agreement data; frozen held-out comparison. Distinct from later **SF4** conservative release-policy fixes. |
| S5 | Case-aware detector, capital zones/body bands; candidate with naming/regression limits. |
| Detector S6, supporting lineage | Per-letter ownership/presence improvements, retained S4 mark and S5 case models; not a separate manifest generation. |
| SF1–SF5 review records | Print-preserving defaults, physical ownership and runtime binding, clipping/coverage guards, quote/elision behavior. These are not fabricated 0.n versions. |
| SF6 / tool 0.6 | Every deletion requires two certified positive absence signals; unqualified deletion makes a whole-line HOLD. |
| SF7 / tool 0.7 | Quote aliases tied to physical groups; reader-only substitutions; A/B insertion variants. A wins the preregistered LQB tie; remains candidate_pre_audit. |

Historical detector scores are different instruments from final released-label precision. S2's 666-line whole-line detector P/R was **92.0%/83.3%**; S3 **91.4%/86.3%**. S5's frozen total was **93.7%/91.6%**, with capital detection P/R **95.6%/98.7%**. These numbers are not SF7 release-accuracy claims.

## Inputs

Immutable raw Google import and stable line IDs/crop identities; recogniser base-letter text and cached alignments; native detector slots/components, physical ownership and observed zones; frozen lexicon/constraints and reader predictions/coverage. Saved runtime binds recogniser context, detector geometry, A/B peers, coverage and policy digests. Missing evidence remains unresolved rather than becoming a negative observation.

SF7 RC1 recomposes the **124,669 training IDs** in the saved SF6/L1R3 population (job 3680729), using **ENSEMBLE_AB** reader mode. SF7 variants A/B are addition policies, not the names of the neural readers A/B. Raw parent is `google_raw_v2_import`, train import SHA `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`.

## Algorithm in prose

The S1 lexical path generates constraint-valid mark alternatives from attestation and deterministic Greek constraints, preserving base letters. Physical support/contradiction decides whether a proposed cluster can be accepted; uncertain localization, merging or clipping can HOLD rather than guessing. Text/recogniser agreement alone does not establish printed marks. Later readers supply four separate heads (breathing, accent, dialytika, subscript) at located slots, while native ownership limits which ink belongs to the letter.

R0 is a recogniser/print-truth audit, not another mark-correction release: it keeps scoped pixel-adjudicated word truth, excludes unknown glyphs, and distinguishes selected-word letter errors from full-line CER. R1 provides learned mark-reader predictions. Its rescoring uses frozen slots with unknown/unscored/unmapped denominators explicit; it does not certify physical segmentation or untouched-test generalization. Reader A's raw all-unscored-none total P/R is **99.14%/94.20%**, versus **99.14%/98.89%** on scored-only slots, demonstrating why denominator choice must remain visible.

SF6 certifies each removed/replaced NFD atom at its original boundary. For combining/spacing marks it needs reader AND detector, or reader AND scored recogniser text; A∧B is one reader signal. Apostrophe/quote/keraia deletion needs detector AND recogniser text because the mark reader has no punctuation-absence head. Empty/unobserved detector lists and missing scores never prove absence. Any uncertified deletion holds the line.

SF7 keeps that deletion rule. A quote/apostrophe alias immediately before a capital is consumed only when it is the same physical group as the added capital mark compound; separate quote+compound keeps both, unresolved grouping HOLDs. Saved source component IDs establish unique ownership; shared, clipped, unobserved or unresolved ink cannot certify a group. Variant A allows reader additions except subscript needs observed below ink. Variant B needs reader AND (detector ink OR scored recogniser text) for every insertion. Substitutions use the preregistered reader-only rule. Frozen policy binding includes source hashes and preregistration; changed bindings fail rather than silently substituting another policy.

## Outputs and reason codes

Composer outputs distinguish **corrected / unchanged / hold**, with rule traces, per-edit head/kind/signals, deletion checks, quote operations (`CONSUME_ALIAS`, `KEEP_BOTH`, or unresolved HOLD) and bound evidence. A HOLD is not a released correction. The pipeline adapter has its own status vocabulary (`applied`, `verified_no_change`, unresolved/proposal/failed); the two schemas must not be conflated.

Chosen sparse candidate: `artifacts/sf7_rc1/release_edits_only_A.jsonl`, **605 rows /665 edits**, SHA `1e3ac3344d0054d8e7639325afdf13826181e6eec10983b7e162b9648c5faf5a`, status **candidate_pre_audit**, bound=false. Exact forward/inverse UTF-8 patches preserve every unedited byte; 81 formatting-only composer corrections are omitted. Across the full train selection A has **686 corrected /10,807 unchanged /113,176 HOLD**. Those counts describe processing status, not correctness.

## Evidence: review sets and owner marks

Owner-note instruments stay distinct: original 59 notes, 33 review notes, 56 examples, later 49 notes and 57 examples are not pooled. `SF1_REPORT.md` documents stricter replay of current S6 notes **36/49 reported →35/49 replayed**, with examples **33/57** unchanged. These notes test specific owner clauses rather than a random accuracy sample.

LQB choice in `SF7_RC1_LQB.md` excludes in-sample truth, inherited SF6/gate/reader tags, quote_alias and substitution60 exposure. There are **21,920 choice-frame heads /393 lines**, but released A/B coverage is only **604 heads /20 lines** and **564 /19**. Only two corrected DEV lines contribute. There is no tier-B/C marks support in this overlap.

| Version-native covered tier A/B | TP / FP / FN | Precision / recall | Head errors |
| --- | --- | --- | ---: |
| Google, 21,892 heads /391 lines | 1195/50/56 | 95.983936% /95.523581% | 73 |
| SF6, 612 /20 | 38/1/0 | 97.435897% /100% | 1 |
| SF7 A, 604 /20 | 38/0/0 | 100% /100% | 0 |
| SF7 B, 564 /19 | 34/0/0 | 100% /100% | 0 |

These native denominators differ; they are not paired improvements. A/B common **564 heads /19 lines** have zero precision/recall delta; the strict Google/SF6/A/B common **536 heads /18 lines** are all unchanged, with 100% for all four. This cannot measure correction gains. The fixed tie rule selects A without establishing population improvement. Full paired/cluster intervals are in `artifacts/sf7_rc1/lqb_scores.json`.

The blind audit frame samples **100 lines** from 515 eligible corrected candidate lines, seed 20261017, excluding all truth v1/v1.1 and historical audit100 IDs. There are **107 changed heads**: 79 accents, 24 breathings, four subscripts. Current `artifacts/sf7_rc1/audit/final_score/final_score.json` reports **70 correct /0 incorrect /30 pending lines**, 75 correct accents and **32 pending heads** (four accent, 24 breathing, four subscript). Final precision is null, controls_gate_passed=false, release_authorized=false. The 70/70 resolved-subset bootstrap is degenerate [1,1], explicitly not a final audit interval. Adoption needs ≥83/100 plus the preregistered line-class constraint; neither is established.

**OC1/OC2:** `SF7_AUDIT_OPUS_PREP.md` prepares two blind Opus folders, each **32 targets +4 controls =36 cards**; reverse reader order, private keys, fresh options and document-disjoint verified controls. The seven unresolved Sol lines are **three capital breathing and four lowercase accent heads**, correcting the brief's description. OC2 merges Sol and Opus after control gates, requires 2-of-2 or 2-of-3, and preserves pending heads/lines. The package is build-only; empty assigned answer files are not completed readings.

**TR1/TR2:** TR1 finds complete saved evidence missing for **28,620 test +8,110 dev =36,730** eligible Greek-poly lines. TR2 prepares the frozen SF7-A recipe with fresh evidence and exact raw split parents, not a policy change. The final 500-line CPU dry-run (250 per split) exits 0: test **3 corrected /16 unchanged /231 HOLD**, sparse **2 rows /2 edits**; dev **7/70/173**, sparse **7 rows /7 edits**. Deployment has **687/687** payload SHA matches and scheduler test-only success. These establish bounded workflow validation, not full counterpart completion or accuracy; the package report says no production job submitted and no labels bound.

## Tests

`tests/labelfix/test_sf7.py` covers quote-alias witnesses and real quote controls, atomic alias replacement, absent/shared/clipped/ambiguous groups, frozen SF6 behavior and insertion/deletion rules. `test_sf7_package.py` and `test_policy_frozen_after_merge.py` cover bindings. OC final-score preparation reports **13 passed** synthetic-answer tests. TR2's mock verifies exact forward/reverse byte patches (13 edited rows /15 edits on its saved 64-line fixture), then the separate 500-line real-input readback checks every identity/patch. Historical SF6 reports **1,100 passes +one sandbox loopback setup error**, so it is not an all-green claim. CLEAN5C ran no tests, inference, audits or release commands.

## Known limitations

Candidate_pre_audit is authoritative despite documents informally saying “release.” Full audit and train/test counterpart binding remain unresolved in the cited records. Narrow LQB coverage cannot show population benefit or A/B equivalence. The early classifier's held-out books were previously used for baseline calibration; S1–S3 explicitly disclose this exposure. Physical ownership, capital zones, clipped subscripts, missing scored runtime and unknown truth limit coverage. Do not equate R1 slot scores, owner-note success, LQB head precision and all-head line audit precision.

## Code paths

`greekocr/labelfix/{spellink,textstage,lexicon,constraints,ink,reading,release_gate,lqb,sheet}.py`; `scripts/labelfix/release_gate_sf7.py`; `scripts/labelfix/sf7_final_score.py`; `scripts/labelfix/sf7_opus_prepare.py`; `scripts/labelfix/r2_cards_resolve.py`; Clariden recomposition/package paths under `scripts/labelfix/clariden/`. The manifest points to historical worktree-prefixed source identity; local integrated paths above are the code locations, not a claim that historical receipts were regenerated.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `docs/harvest/line_pipeline/tool_versions.json`.
- `docs/records/labelfix/secondary/PLAN.md`; `docs/records/labelfix/spellcheck/{S1_REPORT.md,S2_REPORT.md,S3_REPORT.md,S4_REPORT.md,S5_REPORT.md,S6_REPORT.md,SF1_REPORT.md,SF4_REPORT.md,SF5_REPORT.md,SF6_REPORT.md}` (relevant lineage/evidence sections).
- `docs/records/labelfix/spellcheck/R0_REPORT.md`; `docs/records/labelfix/spellcheck/clariden/R1_result_3678928/RESULT.md` (scoped truth/reader tables).
- `docs/records/labelfix/spellcheck/{SF7_PREREGISTRATION.md,SF7_RC1_LQB.md,HANDOFF_20261018_spellcheck.md,SF7_AUDIT_PARTIAL.md,SF7_AUDIT_OPUS_PREP.md,SF7_TEST_COUNTERPART.md,SF7_TEST_PACKAGE.md}`.
- `docs/records/briefs/OC1_opus_audit_cards.md`; `artifacts/sf7_rc1/audit/final_score/final_score.json` (summary).
- `scripts/labelfix/release_gate_sf7.py`; `greekocr/harvest/line_pipeline.py`; `greekocr/labelfix/lqb.py`; `tests/labelfix/test_sf7.py` (targeted source reads).
