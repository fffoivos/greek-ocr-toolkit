# S7 — Toolkit geometry qualification

**No substitution qualified for the default.** S1 and S2 regress physical/owner instruments; S3 over-abstains. All candidates remain explicitly selectable for investigation with `read_ink(..., substitutions=[...])`; `QUALIFIED_GEOMETRY` is empty. The accepted-set run is a separate replay of the unchanged SF1 detector. The independent monotonic scope gate is implemented in the M2 combined-checker entry point.

Offline on Mac CPU; no `.git` writes, network, CTC/R1 forward passes, retraining, or model-asset changes. Launch HEAD: `efdf5756c513fc935d7302df4be85a0f9c084702`. There are 1,264 cached evaluation lines (666 held out / 598 DEV), 92 owner lines, and 473 cached Greek/mixed new-source cards. Original S6, SF1, CN1 and M2 measurement files are retained.

Acceptance requires no loss on the fixed presence/capital cohorts or strict complete-owner checks, no new unapproved box loss, and no increase in total owner kind disagreements. A disappeared disagreement is agreement, not an established correction. HOLD is never counted fixed. Negative qualification is not evidence against the toolkit owner rule; it rejects these adapters and feature decisions.

## Saved S6 and the launch runtime

The saved S6 table is not byte-equivalent to the already-installed SF1 runtime. A separate process executed the three original `ink`, `case`, and `reading` sources directly from the launch commit and reproduced **552 TP / 99 FP / 637 FN** pixel capitals and **1172 / 39 / 17** combined capitals. These equal the fresh baseline and accepted-set replay. The saved S6 capital table has 558 / 112 / 631 and 1172 / 48 / 17. This drift predates S7; it is not credited as a substitution result. See [original launch audit](S7_evidence/original_launch_baseline.json) and [instrument](../../../../scripts/labelfix/s7_launch_baseline.py).

| metric | saved S6 | launch SF1 control | accepted set |
| --- | --- | --- | --- |
| pixel capitals P / R | 83.28% / 46.93% | 84.79% / 46.43% | 84.79% / 46.43% |
| combined capitals P / R | 96.07% / 98.57% | 96.78% / 98.57% | 96.78% / 98.57% |
| held-out presence P / R | 98.68% / 95.45% | 98.65% / 95.47% | 98.65% / 95.47% |
| fused presence recall | 60.49% | 60.49% | 60.49% |

Capital truth is the unchanged S5 agreement stratum: 18,960 slots / 1,189 capitals. The separate case-disagreement stratum has 753 slots. Held-out character truth remains 19,249 known / 1,176 UNKNOWN out of 20,425 slots; fused evaluation retains all 756 slots (651 known), and merged-accent evaluation retains all 590 slots (534 known). No ambiguous, fused, clipped or unlocalized slot is removed from these denominators. Presence P/R counts observed detections on the full fixed cohort; UNSEEN availability is reported separately, not awarded as correct absence.

## S1 — rejected

More total owner kind disagreements; Lower held-out presence and fused recall; Strict owner-note losses.

| instrument | SF1 control | S1 |
| --- | --- | --- |
| original 80 disagreements remaining / all owner disagreements | 80 / 80 | 76 / 89 |
| pixel capitals P / R | 84.79% / 46.43% | 83.20% / 43.73% |
| combined capitals P / R | 96.78% / 98.57% | 95.92% / 98.74% |
| 753-slot pixel capital P / R | 15.60% / 2.63% | 17.65% / 2.79% |
| 753-slot combined capital P / R | 94.76% / 97.99% | 94.93% / 98.45% |
| heldout all presence P / R | 98.65% / 95.47% | 98.10% / 94.63% |
| heldout fused presence P / R | 97.03% / 60.49% | 78.99% / 58.02% |
| heldout merged_accent presence P / R | 95.23% / 93.74% | 94.66% / 91.28% |
| heldout ascender false marks | 9 | 10 |
| heldout marks with pixels below S2 per-column meanline | 149 | 145 |
| heldout UNSEEN slots | 0 | 0 |
| dev all presence P / R | 97.56% / 91.81% | 96.02% / 90.26% |
| dev fused presence P / R | 96.52% / 77.29% | 81.11% / 70.12% |
| dev merged_accent presence P / R | 93.32% / 87.83% | 93.57% / 85.60% |
| dev ascender false marks | 1 | 1 |
| dev marks with pixels below S2 per-column meanline | 158 | 160 |
| dev UNSEEN slots | 0 | 0 |
| strict detector review_v16 | 35/49 | 32/49 |
| combined review_v16 fixed / HOLD / unmet | 26 / 12 / 11 | 24 / 14 / 11 |
| strict detector examples_v10 | 33/57 | 31/57 |
| combined examples_v10 fixed / HOLD / unmet | 25 / 17 / 15 | 23 / 18 / 16 |
| strict detector old59 | 46/59 | 44/59 |
| combined old59 fixed / HOLD / unmet | 45 / 8 / 6 | 42 / 11 / 6 |
| strict detector old33 | 18/33 | 16/33 |
| combined old33 fixed / HOLD / unmet | 18 / 6 / 9 | 16 / 8 / 9 |
| strict detector old56 | 26/56 | 24/56 |
| combined old56 fixed / HOLD / unmet | 23 / 16 / 17 | 21 / 18 / 17 |
| saved S6 box lost / added / moved | — | 9 / 4 / 0 |
| launch SF1 box lost / added / moved | — | 9 / 3 / 0 |

`glyphs.letters.letter_boxes` runs after restricting native ink to the current middle band. Its split-or-unresolved boxes and complete parent sets are retained in reading geometry. Cached spans only map recognized letters onto these physical groups. Shared, missing and unresolved groups explicitly carry ambiguity/HOLD; the recognizer never chooses a physical split count. Unassigned physical groups remain in the line receipt, and every recognized letter remains in evaluation. Physical mapping totals: `{"letters": 33859, "unmatched_physical": 1956, "unresolved_physical": 259}`.

## S2 — rejected

Lower pixel capital recall and combined capital precision; Lower held-out presence recall; Strict owner-note losses.

| instrument | SF1 control | S2 |
| --- | --- | --- |
| original 80 disagreements remaining / all owner disagreements | 80 / 80 | 73 / 88 |
| pixel capitals P / R | 84.79% / 46.43% | 84.89% / 45.84% |
| combined capitals P / R | 96.78% / 98.57% | 95.59% / 98.49% |
| 753-slot pixel capital P / R | 15.60% / 2.63% | 9.80% / 1.55% |
| 753-slot combined capital P / R | 94.76% / 97.99% | 92.67% / 97.83% |
| heldout all presence P / R | 98.65% / 95.47% | 98.60% / 94.99% |
| heldout fused presence P / R | 97.03% / 60.49% | 93.33% / 60.49% |
| heldout merged_accent presence P / R | 95.23% / 93.74% | 96.81% / 88.37% |
| heldout ascender false marks | 9 | 4 |
| heldout marks with pixels below S2 per-column meanline | 149 | 0 |
| heldout UNSEEN slots | 0 | 0 |
| dev all presence P / R | 97.56% / 91.81% | 97.94% / 91.70% |
| dev fused presence P / R | 96.52% / 77.29% | 97.41% / 74.90% |
| dev merged_accent presence P / R | 93.32% / 87.83% | 95.99% / 87.42% |
| dev ascender false marks | 1 | 1 |
| dev marks with pixels below S2 per-column meanline | 158 | 0 |
| dev UNSEEN slots | 0 | 0 |
| strict detector review_v16 | 35/49 | 34/49 |
| combined review_v16 fixed / HOLD / unmet | 26 / 12 / 11 | 25 / 12 / 12 |
| strict detector examples_v10 | 33/57 | 31/57 |
| combined examples_v10 fixed / HOLD / unmet | 25 / 17 / 15 | 25 / 17 / 15 |
| strict detector old59 | 46/59 | 43/59 |
| combined old59 fixed / HOLD / unmet | 45 / 8 / 6 | 42 / 11 / 6 |
| strict detector old33 | 18/33 | 17/33 |
| combined old33 fixed / HOLD / unmet | 18 / 6 / 9 | 17 / 7 / 9 |
| strict detector old56 | 26/56 | 24/56 |
| combined old56 fixed / HOLD / unmet | 23 / 16 / 17 | 22 / 16 / 18 |
| saved S6 box lost / added / moved | — | 9 / 12 / 6 |
| launch SF1 box lost / added / moved | — | 9 / 11 / 6 |

The shared object uses toolkit per-x curvature and four guides. Class contacts from `pages.font.evidence` supply measured ascender/descender offsets; unavailable offsets remain explicitly fallback (no neighbouring-page evidence is available here to borrow). S6 lowercase-body support can change height and vertical gauge, never straighten the curve. Capital geometric features retain the frozen S5 model and its existing 0.4 supporting-probability threshold; no feature weight or model is trained. Overhead and subscript masks are clipped per column; capital side masks use the shared ascender/mean guides.

Per-line winners: `{"S6_body_repair": 1243, "toolkit": 21}`. Every decision and provenance is in [guide_decisions.jsonl](S7_evidence/guide_decisions.jsonl). Required witnesses:

| line | toolkit x-height | selected x-height | winner |
| --- | --- | --- | --- |
| 602cc72e-p000155-l0009 | 48.0 | 31.0 | S6_body_repair |
| 602cc72e-p000113-l0030 | 40.0 | 31.0 | S6_body_repair |

## S3 — rejected

No presence or kind-disagreement gain; Conservative coverage sends known corrections and fixed notes to HOLD.

| instrument | SF1 control | S3 |
| --- | --- | --- |
| original 80 disagreements remaining / all owner disagreements | 80 / 80 | 80 / 80 |
| pixel capitals P / R | 84.79% / 46.43% | 84.79% / 46.43% |
| combined capitals P / R | 96.78% / 98.57% | 96.78% / 98.57% |
| 753-slot pixel capital P / R | 15.60% / 2.63% | 15.60% / 2.63% |
| 753-slot combined capital P / R | 94.76% / 97.99% | 94.76% / 97.99% |
| heldout all presence P / R | 98.65% / 95.47% | 98.65% / 95.47% |
| heldout fused presence P / R | 97.03% / 60.49% | 97.03% / 60.49% |
| heldout merged_accent presence P / R | 95.23% / 93.74% | 95.23% / 93.74% |
| heldout ascender false marks | 9 | 9 |
| heldout marks with pixels below S2 per-column meanline | 149 | 149 |
| heldout UNSEEN slots | 0 | 6628 |
| dev all presence P / R | 97.56% / 91.81% | 97.56% / 91.81% |
| dev fused presence P / R | 96.52% / 77.29% | 96.52% / 77.29% |
| dev merged_accent presence P / R | 93.32% / 87.83% | 93.32% / 87.83% |
| dev ascender false marks | 1 | 1 |
| dev marks with pixels below S2 per-column meanline | 158 | 158 |
| dev UNSEEN slots | 0 | 4287 |
| strict detector review_v16 | 35/49 | 35/49 |
| combined review_v16 fixed / HOLD / unmet | 26 / 12 / 11 | 8 / 31 / 10 |
| strict detector examples_v10 | 33/57 | 33/57 |
| combined examples_v10 fixed / HOLD / unmet | 25 / 17 / 15 | 10 / 36 / 11 |
| strict detector old59 | 46/59 | 46/59 |
| combined old59 fixed / HOLD / unmet | 45 / 8 / 6 | 20 / 35 / 4 |
| strict detector old33 | 18/33 | 18/33 |
| combined old33 fixed / HOLD / unmet | 18 / 6 / 9 | 8 / 18 / 7 |
| strict detector old56 | 26/56 | 26/56 |
| combined old56 fixed / HOLD / unmet | 23 / 16 / 17 | 7 / 34 / 15 |
| saved S6 box lost / added / moved | — | 0 / 1 / 0 |
| launch SF1 box lost / added / moved | — | 0 / 0 / 0 |

S3 accepts crop validity and directional cut masks, adds toolkit body-cut spans, and records above/below coverage as OBSERVED or UNSEEN. Missing top/bottom mark-search extent is conservatively UNSEEN even without edge ink. A relevant UNSEEN zone preserves the visible proposal but holds its slot through both combined paths. This broad envelope is why it fails qualification: it does not recover ink, and on M2 it reduces PRESENCE correction from 25/77 to 3/77. The adapter remains off; a narrower physically validated coverage policy is still needed.

## Original 80 disagreements: who is supported

The ledger scores kind sets against the unchanged supported character print/adjudication or agreement-proxy truth. It does not convert owner uncertainty or unsupported marks into negative truth. The baseline has 67 known cases: R1 right in 62, detector right in 3, neither right in 2; 13 remain UNKNOWN. No new print adjudication is claimed. Every original slot remains in [kind_disagreements.jsonl](S7_evidence/kind_disagreements.jsonl).

| variant | disappear | known disappeared / detector right | remaining known: detector / R1 / neither | remaining UNKNOWN | new disagreements |
| --- | --- | --- | --- | --- | --- |
| baseline | 0 | 0 / 0 | 3 / 62 / 2 | 13 | 0 |
| S1 | 4 | 2 / 2 | 3 / 60 / 2 | 11 | 13 |
| S2 | 7 | 6 / 6 | 3 / 56 / 2 | 12 | 15 |
| S3 | 0 | 0 / 0 | 3 / 62 / 2 | 13 | 0 |
| accepted | 0 | 0 / 0 | 3 / 62 / 2 | 13 | 0 |

## CN1 rerun with the accepted detector

The strict SF1/CN1 clauses, exact-name checks, missing-target rules, UNKNOWN preservation and complete-note HOLD gate are reused unchanged. All five original note instruments are included. Physical facets use detector evidence rather than displayed R1 names. Facets overlap and are not independent truth samples. Full per-note and per-clause records: [owner_checks.jsonl](S7_evidence/owner_checks.jsonl).

| note set | strict detector fixed / n | combined fixed / HOLD / unmet | physical | naming | segmentation | punctuation | letter identity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| review_v16 | 35/49 | 26 / 12 / 11 | 43 / 0 / 13 | 3 / 3 / 3 | 14 / 0 / 0 | 1 / 0 / 1 | 3 / 0 / 0 |
| examples_v10 | 33/57 | 25 / 17 / 15 | 57 / 0 / 19 | 1 / 1 / 2 | 5 / 0 / 0 | 11 / 0 / 4 | 4 / 0 / 0 |
| old33 | 18/33 | 18 / 6 / 9 | 38 / 0 / 15 | 26 / 7 / 7 | 0 / 0 / 0 | 7 / 0 / 0 | 0 / 0 / 0 |
| old56 | 26/56 | 23 / 16 / 17 | 56 / 0 / 19 | 44 / 16 / 11 | 4 / 0 / 0 | 11 / 0 / 4 | 4 / 0 / 0 |
| old59 | 46/59 | 45 / 8 / 6 | 38 / 0 / 12 | 26 / 6 / 6 | 0 / 0 / 0 | 9 / 0 / 0 | 0 / 0 / 0 |

Accepted combined HOLD: `{"slots": 87, "lines": 53, "unseen_slots": 0, "localisation_unknown": 0}`. The same 80 kind disagreements remain; 9 K1 flags overlap 2 of them, giving 87 held slots. Print output has no constraint deletions. The existing unheld R1 naming regression on `384c3f89-p000053-l0021` is not corrected by S7.

## Box regression

The unmodified `scripts/labelfix/box_regression.py` was run for every candidate against saved S6 and against the fresh launch control. It was also run separately for the 49-note review and 57-note examples instruments, avoiding an interpretation based only on union-file overwrite order. Old slot identities and explicit zones are retained; ambiguous ownership stays unresolved.

| saved S6 → accepted: status / kind / scope | count |
| --- | --- |
| reviewed with note / added / implicitly approved | 1 |
| lines missing old | 0 |
| lines missing new | 0 |
| lines compared | 92 |
| lines with any change | 1 |

Launch SF1 → accepted: lost 0, added 0, moved 0. Saved-S6 differences already present at launch are not attributed to a substitution. Implicitly approved saved-S6 box changes: lost 0, added 1, moved 0. The sole addition is the already-present launch recovery on `51fe7386-p000024-l0020`, start 13 / old slot 11, bbox `[370, 8, 386, 28]`; it is not an S7 gain. All statuses and native box receipts are in [box_summaries.json](S7_evidence/box_summaries.json) and the linked `boxes_*.json` sidecars.

## M2 transfer and monotonic scope

The same 473 eligible cached cards are accounted for: **40 homogeneous monotonic lines excluded, 433 checked**, plus the original 40 Cyrillic exclusions in the 513-card inventory. The script class is inherited only from an independent pixel-reviewed homogeneous page annotation. Mixed Greek monotonic/polytonic pages and unknown classes remain eligible. No source-name heuristic, Google label, blind verdict, or recognizer combining mark determines scope. The manifest contains no reference text: [m2_script_classes.jsonl](S7_evidence/m2_script_classes.jsonl) and [annotation bindings](S7_evidence/m2_script_classes.receipt.json).

Both requested M2 scripts were rerun with every candidate and the accepted set. CTC spans, R1 predictions, extraction and checkpoints are hash-bound cached inputs; **zero CTC and R1 forward passes**. All 77 original mark-only error pairs remain in scoring. Excluded monotonic cards contain none of those 77 pairs. The gate excludes the two previously wrong modern accent→breathing spot checks before either polytonic reader runs.

| detector / scope | PRESENCE corrected / HOLD / missed | capital-breathing corrected / 19 | new changed slots on marks-correct cards | HOLD / original 473 | HOLD / checked |
| --- | --- | --- | --- | --- | --- |
| M2 original | 25 / 40 / 12 | 1 | 30 | 367/473 (77.59%) | 367/473 (77.59%) |
| scope_only | 25 / 40 / 12 | 1 | 20 | 327/473 (69.13%) | 327/433 (75.52%) |
| S1 | 26 / 38 / 13 | 2 | 18 | 357/473 (75.48%) | 357/433 (82.45%) |
| S2 | 27 / 38 / 12 | 2 | 20 | 329/473 (69.56%) | 329/433 (75.98%) |
| S3 | 3 / 62 / 12 | 0 | 8 | 430/473 (90.91%) | 430/433 (99.31%) |
| accepted | 25 / 40 / 12 | 1 | 20 | 327/473 (69.13%) | 327/433 (75.52%) |

The final 30→20 change reduction is entirely the scope gate; it is not a geometry improvement. These changes are conditional upper bounds from the blind marks-correct labels, not newly adjudicated errors. Final FULL: `{"HOLD": 41, "missed": 12, "corrected": 24}`, new changed slots 10. No 20-example queue is fabricated for candidates with fewer accepted changes; `--no-spotcheck-queue` skips only that optional queue, leaving every scoring assertion and denominator intact.

## Validation and reproduction

Validation: **241 passed; one unchanged HTTP fixture blocked by the sandbox**. All existing labelfix test sources and assertions are unchanged. The full test command is recorded in [pytest_full.txt](S7_evidence/pytest_full.txt); the unchanged HTTP capture integration fixture cannot bind a socket in this sandbox (`PermissionError: Operation not permitted`). The explicitly offline run is in [pytest_offline.txt](S7_evidence/pytest_offline.txt). The source-bound R1 scorer was rerun and its metrics/RESULT compared byte-for-byte with SF1 before refreshing its current-source receipt; historical receipt preserved in this evidence directory. [Verification](S7_evidence/verification.json) binds final source, assets, instruments and artifacts.

```sh
export PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY -m scripts.labelfix.s7_launch_baseline
$PY -m scripts.labelfix.s7_validate
$PY -m scripts.labelfix.s7_m2_scope
$PY -m scripts.labelfix.s7_m2_replay
$PY -m scripts.labelfix.s7_box_regression
$PY -m scripts.labelfix.s7_verify
$PY -m scripts.labelfix.s7_report
```

Qualification replay: 218.7 s on CPU; [final run log](S7_evidence/qualification_final.log). No performance/generalization claim is made. All candidates are rejected on these fixed instruments; the 80-slot detector weakness, low pixel-only capital recall and fused presence misses remain open.

S7 RESULT: accepted none; kind-disagreements 80→80; pixel-only capitals P/R 83.28% / 46.93%→84.79% / 46.43% (launch 84.79% / 46.43%); presence P/R 98.68% / 95.45%→98.65% / 95.47%; fused R 60.49%→60.49%; owner notes review_v16 35→35, examples_v10 33→33; implicit box changes lost 0 added 1; CN1 combined review_v16 26→26, examples_v10 25→25; M2 HOLD lines 77.6%→69.13% (75.52% of 433 checked), corrected 25/77→25/77; regressions: no accepted geometry change; pre-existing saved-S6/SF1 drift and R1 naming error remain; S1/S2 physical losses and S3 over-abstention rejected; HTTP fixture sandbox-blocked.
