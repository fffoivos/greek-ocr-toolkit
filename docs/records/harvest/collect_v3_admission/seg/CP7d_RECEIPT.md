# SEG-CP7d receipt

**Gate: FAIL.** Both contexts passed controls (5/5 each), all 100 fresh rows mapped and scored, and both canonical scans are ok with 0 violations. This is scoring against the existing reader verdicts; lead pixel adjudication remains pending. No readers, OCR, geometry preparation, network calls, tuning, or threshold changes were performed. Reader receipts identify gpt-6.1-sol; the frozen launcher specifies medium effort and network OFF.

Amendment: **recorded**, not newly written. CP7c2 commit `1eea5e9b9a778544a6e4ea97dfdc4c6989730b99` already contains [the runtime-only amendment](cp7/r2/runtime_amendment_cp7c2.json), SHA `20d7b3ad44b8801f0c65c02efa35c687b105f443afb22170a56a693bf1e6d41b`. The record and runtime were compared byte-for-byte with that commit. Runtime old SHA `c70c24f56973b83b29a0a28cede10a15f3c84cba2344cf00509969b0e4738b6f`; required amended SHA `6a821cef734a81f1b48d1689dc36ffba90476133daa8bf114bd481143f11fe28`. Reason: use recorded closure hashes after reading, allowing only answers.jsonl and zoom/** while retaining strict pre-read closure.

Original freeze remains `dd2e7234c4f0f96a19b552daf8863c8dcd4eacaef074abd37c99ac3d22066833`. Because score_r2.py is itself frozen, [score_cp7d.py](cp7/score_cp7d.py) temporarily binds only its verify function to the pinned CP7c2 runtime verifier and calls the original main. All 257 other bound file/geometry entries, including score_r2.py, r2_common.py, screen/admission code, parameters and calibration remain exact. Verification passed before and after scoring; sealed decisions remain `a34e24d9377adc8069634b8b2d1d05909ffe684ea6a76c81a438cee089939b40`, matching the build receipt.

Execution: `.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/cp7/score_cp7d.py` from the repository root with `PYTHONDONTWRITEBYTECODE=1`. The original scorer enforces network/subprocess OFF, validates the freeze, draw, seal, pack manifests, raw-to-mapped answers, crop hashes, controls, scan/rollout/usage/log custody, and writes its original outputs. [Scoring log](cp7/r2/score_cp7d.log).

DROP-truth = neighbour_whole_word ∨ multi_line ∨ rotated ∨ horizontally_missegmented. Every individual screen is compared to that common DROP-truth, as CP7c designed; individual screen FN is not a claim about its narrower target class. The measured denominator is 93, excluding geometry_unavailable as policy.

| Screen / composition | TP | FP | FN | TN |
|---|---:|---:|---:|---:|
| union | 2 | 3 | 1 | 87 |
| merged | 2 | 2 | 1 | 88 |
| neighbour_words | 2 | 2 | 1 | 88 |
| orientation | 2 | 1 | 1 | 89 |
| crossing | 0 | 0 | 3 | 90 |
| composed including policy (100) | 2 | 10 | 1 | 87 |

The final status line uses the measured union screen matrix. The gate requires FP=FN=0 for every reported screen and measured union, controls 10/10, mapped/scored 100/100, and clean scans. Screen errors fail it. Full composed accounting includes seven policy drops; these are reported separately from measured screen errors.

Geometry unavailable: **7/100**, reader KEEP **7**, reader DROP **0**. Row IDs and reasons remain in score_summary.json / geometry_summary.json.

End-clip known class: **8/100 (8%)**, excluded from DROP-truth and gating. Candidate agreement: **85/93 (91.40%)** on available diagnostics; TP 2, FP 2, FN 6, TN 83. Candidate unavailable 7; candidate positive 4. This is the frozen lower-bound diagnostic.

Rotated-miss: **1/3**, defined as reader rotated=yes with orientation screen false. The same one row is missed by the measured union and full composition: `gazette_modern--0020420cfe156a73--s000-l0002`. [Machine-readable verdicts](cp7/r2/cp7d_diagnostics.json).

Orientation unknown: **12/100**; reader KEEP **12**, reader DROP **0**, reader rotated=yes **0**. Three are geometry policy drops and nine are composed KEEP. These are existing reader verdicts, not fresh pixel adjudications.

| orientation_unknown row | Reader truth | Rotated | Composed verdict |
|---|---|---|---|
| elstat--0877c813a8512b56--s000-l0232 | KEEP | no | KEEP |
| elstat--5f85f8679b2fe3c7--s000-l0102 | KEEP | no | DROP (geometry policy) |
| gazette_modern--84c075460704110b--s000-l0069 | KEEP | no | KEEP |
| elstat--07520765bc203a33--s001-l0405 | KEEP | no | DROP (geometry policy) |
| gazette_modern--78abf3276f0df3f0--s000-l0008 | KEEP | no | KEEP |
| elstat--88112979c8a843cb--s000-l0192 | KEEP | no | DROP (geometry policy) |
| elstat--ee37bc488988f1bd--s000-l0527 | KEEP | no | KEEP |
| elstat--ee37bc488988f1bd--s000-l0551 | KEEP | no | KEEP |
| nlg--df6ccc87357b61b6--s034-l0041 | KEEP | no | KEEP |
| elstat--06e84fee760bdfed--s000-l0107 | KEEP | no | KEEP |
| elstat--c4d30f00b317e558--s000-l0229 | KEEP | no | KEEP |
| elstat--07520765bc203a33--s000-l0488 | KEEP | no | KEEP |

Adjudication: **43 unique rows**: 6 with at least one per-screen FP/FN, 39 flagged, 0 unreadable, and 8 end-clips (overlapping categories). [Adjudication sheet](cp7/r2/ADJUDICATION_SHEET.md) includes all reader reasons and sealed evidence. [Contact sheet 1](cp7/r2/ADJUDICATION_01.png) contains 30 rows; [contact sheet 2](cp7/r2/ADJUDICATION_02.png) contains 13. Manifest coverage, dimensions and PNG decoding were verified for every selected row. No pixel adjudication was performed.

Validation: **93 passed, 4 deselected** in [cp7d_tests.log](cp7/r2/cp7d_tests.log), including amendment/runtime/screen/scorer drift rejection, original scorer invocation, truth/matrix/gate fixtures, contact-sheet output, and post-read custody. The initial full historical run had **93 passed, 4 failed** ([retained log](cp7/r2/cp7d_legacy_tests.log)): four CP7c pre-read checks demand the original runtime hash, strictly unopened A/B packs, or absent run_r2.log. They were explicitly deselected for the post-read run; frozen tests were left unchanged.

[Commit list / review manifest](CP7d_COMMIT_LIST.json). No Git commit or staging performed; existing unrelated changes and context B reader products were preserved.

SEG-CP7d: done | amendment: recorded | controls 10/10 | mapped 100/100 | screens TP 2 FP 3 FN 1 TN 87 | policy geometry_unavailable 7 (reader keep 7) | end_clip known class 8/100 (candidate agreement 85/93) | rotated-miss 1 | gate: FAIL | to adjudicate 43 | tests: 93 passed
