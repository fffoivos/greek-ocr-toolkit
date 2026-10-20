# SEG-GATE-2 hand-off — segmentation 0.8

## Complete policy: exactly the owner's three rules

Owner, 19 October, verbatim:

> The rules are
> 1. detection of other lines, at least two words cutoff doesn't count
> 2. Comparison of de skewed lines' long sides normalized for height (the deskewed line's) with google output
> 3. And also height of deskewed line box x 1.5 + bounding box's height

> stop adding rules I didn't tell you to

The policy's complete rule list, in execution order:

1. **Other lines.** Run the unchanged 0.7 crop-only line inventory first. DROP for an additional complete line, preserving the frozen 0.5 `detectedRowsJudgement` additional-complete-line rule and feeding it from the crop-only inventory. DROP when whole words from other rows total **>2**. Exactly two whole words pass; cut-off words do not count. The existing absent/unsupported main row and unresolved orientation conditions remain the only gate UNCERTAIN cases. Context is optional diagnostics and never required.
2. **Length.** Measure the main row's text components with the unchanged **0.6 de-skewed row-frame box**, normalise its long side by its own height through the unchanged predictor, then call byte-identical `boxLengthJudgement` with **0.5–1.5**. The saved Google output character count is unchanged. The unchanged comparison ratio is `(characters+1)/(predicted_characters+1)`.
3. **Padding.** Call byte-identical `paddingJudgement` with **1.5** and input `(segment_height − upright_box_height) / row_frame_height`. Thus crop height may be at most upright box height + 1.5 × de-skewed line height.

**No rule beyond these three exists in the policy.** The row-frame-taller-than-upright guard and `gate: target line cut` veto are removed entirely. No baseline crossing, low-visibility span or cut letter affects a verdict. `skew_line` crossings, cut spans and cut letters remain in `evidence.gate.main_cut` for owner-sheet diagnostics, together with the unchanged raw heights; the `row_frame_taller` field is removed and the remaining `cut` summary is diagnostic only. No rule, threshold, epsilon, cap or detector was added or tuned. The 0.6 flat-angle identity handling and all 0.7 inventory definitions remain unchanged.

The retained inventory has all existing detected rows, visible fractions, body counts/IDs, supported x-ranges, coverage, component IDs, whole/cut-off word groups and optional context counts. The existing complete-row proxy is votes ≥6, bodies ≥6, visibility ≥.9, coverage ≥.6. Existing word groups use the .35-x-height gap; a whole group needs ≥2 ≥60%-visible bodies and neither horizontal crop edge. These are unchanged inventory definitions from 0.7, not new decision tests. Order is **inventory → other-lines gate → length → padding**. Non-passing gates skip length/padding. The frozen numerical functions retain their existing missing/invalid-measurement handling.

## Witnesses and tests

| Witness | Computed length ratio | Verdict | Padding in row-frame heights | Whole / cut-off other words |
| --- | ---: | --- | ---: | ---: |
| `51db636c-p000048-l0024` | 0.922038187286444 | KEEP | 0.2702702702702703 | 0 / 0 |
| `847e1ec1-p000015-l0035` | 0.5077247645452321 | KEEP | 0.0 | 0 / 6 |
| `b8b6779da9a68fbed0ccdb5b-p000011-l0018` | 0.9347717358014447 | KEEP | 0.09901735852524789 | 0 / 4 |

`847e1ec1-p000015-l0035` now passes the gate and **KEEP** follows from ratio **0.5077247645452321**, inside the unchanged interval. It still records the baseline exit at x=1817.4010238826568, span [1990,2044) with min_visible=.869, and 10 cut letters. Those observations do not veto it. Its 0.6 full verdict was UNCERTAIN under the old neighbour logic; only its frozen numerical evidence is reused for identity checking. No verdict was forced to fit the old DROP witness designation.

`b8b6779da9a68fbed0ccdb5b-p000011-l0018` remains **KEEP**, with 0 whole / 4 cut-off words. The clean θ=0 witness `51db636c-p000048-l0024` has box, prediction and padding evidence equal to 0.6 to the digit.

**157 passed**, using `.venv/`, in [all_tests.log](all_tests.log). Coverage includes the two real witnesses, exactly two versus three whole words, second complete line, horizontal-edge fragments, one-body groups, the exact 60% boundary, the two gate uncertainty cases, seven diagnostic counterexamples that cannot change gate/final decisions, optional context failures, and θ=0 numerical identity. Existing pipeline and geometry regressions pass.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_line_pipeline.py tests/test_seg_deskew.py tests/test_seg_gate.py -q
```

## 150: owner-standard confusion, all versions side by side

Fresh native replay: **150/150**, zero failures, 32.04 seconds. [Full evidence](replay_segeval1.jsonl), [summary](summary_segeval1.json), [replay log](replay_150.log). Version 0.5 is the sealed census decision; 0.6 and 0.7 are the saved native replays on the same byte-bound crops; 0.8 is this fresh native replay. REJECT = DROP; ACCEPT = KEEP.

The unchanged owner standard is recomputed from complete saved answers: a yes in multi_line / neighbour_whole_word / rotated / horizontally_missegmented, or an extra_text / missing_word_or_span / crop_clipped / merged_two_lines error, is faulty. A positive fault takes precedence over unknown flags; otherwise any missing/unknown segmentation flag is unresolved. `crop_overrun` alone is fine; other character/mark/punctuation errors alone are outside this segmentation scoring. Labels: **118 fine / 30 faulty / 2 unresolved**. Saved reader_state and full answers remain alongside these labels in every row.

| Decision | 0.5 fine | 0.5 faulty | 0.5 unresolved | 0.6 fine | 0.6 faulty | 0.6 unresolved | 0.7 fine | 0.7 faulty | 0.7 unresolved | 0.8 fine | 0.8 faulty | 0.8 unresolved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| REJECT | 26 | 22 | 2 | 21 | 16 | 2 | 59 | 16 | 0 | 18 | 10 | 0 |
| ACCEPT | 92 | 8 | 0 | 95 | 11 | 0 | 56 | 8 | 0 | 97 | 14 | 0 |
| UNCERTAIN | 0 | 0 | 0 | 2 | 3 | 0 | 3 | 6 | 2 | 3 | 6 | 2 |

FP = REJECT/fine; FN = ACCEPT/faulty; UNC = all UNCERTAIN verdicts, across **all 150**:

| Version | FP | FN | UNC |
| --- | ---: | ---: | ---: |
| 0.5 | 26 | 8 | 0 |
| 0.6 | 21 | 11 | 5 |
| 0.7 | 59 | 8 | 11 |
| 0.8 | 18 | 14 | 11 |

The last line uses full-population counts, including **0.7 FP 59**. The older 0.7 hand-off's 19/50 fixed-reject-stratum number is not substituted for this count.

## 0.7 → 0.8 flips

All **47** flips on the 150 are DROP→KEEP: 41 owner-fine and 6 owner-faulty. All other decisions retain their verdict. [Exhaustive table](flips_segeval1.md), [full flip records](flips_segeval1.jsonl).

| 0.7 → 0.8 | Rows |
| --- | ---: |
| DROP->DROP | 28 |
| DROP->KEEP | 47 |
| KEEP->KEEP | 64 |
| UNCERTAIN->UNCERTAIN | 11 |


All **388** flips on the 888 are DROP→KEEP; **35** are owner-rated. [Exhaustive table](flips_calibration.md), [full flip records](flips_calibration.jsonl). Both tables include prior/current reasons, whole/cut-off counts, exact ratios, cut diagnostics, former 0.7 flags and saved labels/ratings. Only removing the two additions causes these changes; some formerly target-cut rows still DROP under one of the three retained rules.

| 0.7 → 0.8 | Rows |
| --- | ---: |
| DROP->DROP | 93 |
| DROP->KEEP | 388 |
| KEEP->KEEP | 366 |
| UNCERTAIN->UNCERTAIN | 41 |


## 888: owner-rating confusion, all versions side by side

Fresh native replay: **888/888**, zero failures, 10.81 seconds. [Full evidence](replay_calibration.jsonl), [summary](summary_calibration.json), [replay log](replay_888.log). Fresh crop orientation/refocus/component/line/box detection uses the same local inputs and script workflow as SEG-GATE-1. Frozen raw source-context observations are reconciled again; no page detector or reader is rerun. Text is bound through the same local detail chunks and hashes. Version 0.5 is the historical `judgements.current` saved in the 0.6 replay (`verdict_before`), not a new 0.5 native replay. Versions 0.6/0.7 are saved native replays.

**135 rated** (78 owner KEEP, 57 owner DROP), **753 unrated**. Labels below come strictly from `owner_rating.decision`. Unrated rows have no accuracy label.

| Decision | 0.5 KEEP | 0.5 DROP | 0.5 unrated | 0.6 KEEP | 0.6 DROP | 0.6 unrated | 0.7 KEEP | 0.7 DROP | 0.7 unrated | 0.8 KEEP | 0.8 DROP | 0.8 unrated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| REJECT | 23 | 51 | 32 | 23 | 50 | 32 | 54 | 47 | 380 | 22 | 44 | 27 |
| ACCEPT | 47 | 3 | 660 | 47 | 2 | 658 | 18 | 1 | 347 | 50 | 4 | 700 |
| UNCERTAIN | 8 | 3 | 61 | 8 | 5 | 63 | 6 | 9 | 26 | 6 | 9 | 26 |

| Version | Agreement / 135 | FP: owner KEEP rejected | FN: owner DROP accepted | UNC rated |
| --- | ---: | ---: | ---: | ---: |
| 0.5 | 98 | 23 | 3 | 11 |
| 0.6 | 97 | 23 | 2 | 13 |
| 0.7 | 65 | 54 | 1 | 15 |
| 0.8 | 94 | 22 | 4 | 15 |

0.8 improves rated agreement over 0.7 (**65→94/135**), but remains below 0.5/0.6 (**98/97**). On the 150, false rejects fall **59→18** and false accepts rise **8→14**; uncertainty stays **11**. These are measured outcomes, with no tuning or new rules to force agreement. Existing inventory word/completeness proxies and sparse owner ratings limit accuracy claims; the 753 unrated crops have no agreement claim.

## Readback and scope guard

[validate.py](validate.py) passes [readback validation](replay_validation.json): all **1038** gate/final decisions replay exactly, every crop-only inventory and `skew_line` record matches 0.7 except the explicitly removed flag/summary dependency, and both removing and replacing all cut diagnostics plus removing context leave every final verdict unchanged. All **944** gate-passing box/padding records equal 0.6 exactly, with **944** predictor outputs independently re-run exactly. All **94** blocked rows have no Stage-B measurement. Every historical decision and label/rating is read back from the frozen sources; all confusion/error/agreement totals and flip membership are independently checked. The only excluded equality field is fresh orientation elapsed `seconds`; both original timing records remain stored.

[scope_guard.json](scope_guard.json) and [source_changes.patch](source_changes.patch) restrict production changes to the policy script, the `line_inventory` segmentation stage removal, versions builder and generated versions. `NativeSegmenter` is byte-identical to 0.7, so the census fingerprint is unchanged. Only the segmentation tool fingerprint/version changes. All **468** other source files, the predictor source/config/lock/executable/coefficient bytes, and the five pre-existing edited files match the initial hashes. `boxLengthJudgement` and `paddingJudgement` match frozen 0.5 and 0.7 byte for byte. Shared tracked diff/stat remains unchanged. [Initial receipt](initial_state.json), [design](DESIGN.md).

Policy SHA256: `e5b635ff9a04cc66f454a68e01ce9773229672e655b3ee08296ee5c0d149ee15`. Segmentation digest: `512e362a691c6f2f425acc41e587b4b751dedbaadd10077d42309ed3f1f7bebd`.

## Branch and delivery

Implementation commit: **`410f4566db26a9acefb541a5af12312c661fb918`**, exact parent **`67e670bac293b55afed32c1da823173344e33a38`** (requested 0.7 implementation). `sol/seg-gate` currently has a documentation-only child `f9d83ec4bb2f7722f5518eb82600700eb76af75e`; this branch deliberately starts at the explicitly requested implementation commit.

The shared Git directory is outside the sandbox's writable roots. The authorised fallback creates **`sol/seg-gate2`** in an isolated writable Git directory and packages it in [SEGGATE2.bundle](SEGGATE2.bundle). A separate hand-off commit follows the implementation. [bundle_receipt.json](bundle_receipt.json) records exact ancestry, bundle verification, independent local import and committed-byte readback. The shared checkout stays on `sol/recut-v1`, with shared refs/index untouched. The bundle is scoped to this worktree and retains the prior bundle's dependence on existing untracked runtime assets. **Never pushed.**

Network remained OFF through test fixtures and replay/readback audit hooks. Only the authorised local 150+888 replay ran, using `.venv/`; no Clariden, Slurm, OCR reader or new reader call was used.

SEGGATE2: done | 150 owner-standard 0.8: FP 18 FN 14 UNC 11 | 0.7: FP 59 FN 8 UNC 11 | 888 rated agree 94/135 | 888 flips 0.7->0.8 388 | tests 157 passed | commit 410f4566db26a9acefb541a5af12312c661fb918
