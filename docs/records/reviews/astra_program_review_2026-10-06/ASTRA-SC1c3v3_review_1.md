**ASTRA-SC1c3v3 — SF6 and SF6b verification: NOT CLOSED.** Two ordinary-deletion paths accept an absence source without the required scored or in-window evidence. Both reproduce through the release overlay in PRESENCE, FULL, ENSEMBLE_AB and ENSEMBLE_AE. The SF6b MOVE exception passes the scoped checks; the SF5 test edits are not weakened. Earlier C2/C3 closures remain unchanged.

Reviewed `05f2dafb..8c5ad361`. Observed checkout HEAD is `21551aca3b210e068be4eb845d62d513a5dfb0e4`; the later commit changes only the review brief. Reviewed production and test files match `8c5ad361`. Policy is `sf6-release-v1`, digest `704c47a3ee5b742376b3c73a8dcf0722dc0077f48a839b1109355cf3980f360e`. Frozen SF5 sources match `05f2dafb`. See the [initial receipt](ASTRA-SC1c3v3_evidence/initial_receipt.json) and [reviewed diff](ASTRA-SC1c3v3_evidence/production_and_test.diff). This report supersedes the interrupted pre-SF6b start.

| Requested check | Verdict | Evidence |
| --- | --- | --- |
| Exact two-positive-absence rule | **NOT FIXED** | 12 release failures below: 3 witnesses × 4 modes |
| Changes confined to deletion policy and its evidence plumbing | **Confirmed** | Existing composer, SF5 text functions and slot decisions preserved |
| SF5 tests not weakened | **Confirmed** | Exact HOLD replacements; composer assertions retained |
| Claimed held-out cost | **Reproduced, with local-evidence limitation** | AB corrections 45→11; corrected lines 35→6; wrong 2→0 |
| SF6b same-kind capital MOVE | **Confirmed within requested probes** | Saved capital witnesses restored; mismatch, unnamed, non-capital and extra-deletion controls HOLD |

**SF6-V3-B01 — BLOCKER: an absent recogniser score becomes a positive absence through the existing loader.**

[release_gate.py:394](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:394) accepts any finite `recognition_confidence` in `[0,1]`, including zero, together with a finite locator span and absence from the transcript. However, [ctc_align.py:89](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/ctc_align.py:89) loads a missing confidence as `0.0`; [m2_run.py:127](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/m2_run.py:127) writes `alignment.confidence` into the runtime consumed by the gate. The gate cannot distinguish that default from an actual score.

The witness calls the real `Alignment.from_record` on a saved alignment for `δ` with a valid span but **no confidence field**, then uses the producer's confidence mapping in an otherwise observed synthetic punctuation runtime. Google is `δ'`, recogniser text is `δ`, and the supported word-final δ detector explicitly reports absence. With the runtime score key absent, the overlay HOLDs. With the loader's default `0.0`, it releases `δ`, deleting Google's apostrophe. Reader predictions/coverage are absent and cannot certify punctuation anyway.

| Recogniser score provenance | Gate signals: reader / detector / recogniser | Actual result, all 4 modes | Required result |
| --- | --- | --- | --- |
| Runtime key missing | false / true / false | HOLD | HOLD |
| Missing saved score defaulted to `0.0` | false / true / true | **corrected: `δ'`→`δ`**, no HOLD | HOLD |

This is one supported detector absence plus an **unscored transcript** promoted to a second signal. It directly contradicts the report's claim that no missing confidence is filled in. The test does not claim a production frequency or a pixel-adjudicated error; it proves release reachability from the existing loader convention.

The score's meaning also limits the claimed certification: [ctc_align.py:197](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/ctc_align.py:197) computes a mean of maximum frame probabilities over the entire line, including blank frames. A finite line average and a neighbouring letter's location do not themselves document scored observation of the omitted character's region. Closure needs explicit score/observation provenance for the relevant region, with missing/defaulted evidence remaining unavailable. Merely binding the number into a hash, or choosing an arbitrary positive threshold, does not resolve that distinction.

**SF6-V3-B02 — BLOCKER: ordinary deletion accepts source spans disjoint from the target window.**

[_finite_span at release_gate.py:277](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:277) checks only finite nonnegative endpoints and positive width. Ordinary reader checks at lines 367–379 and recogniser checks at lines 395–397 do not verify image bounds or coverage of the saved target window. In contrast, the new MOVE path explicitly checks window containment at lines 339–341.

Both following synthetic runtimes have saved target window `[8,20]`; every release mode emits `α` from Google `ά`, with no HOLD:

| Invalid source | Other evidence | Gate signals: reader / detector / recogniser | Actual result |
| --- | --- | --- | --- |
| A/B/E reader spans `[100000,100010]` | Detector explicitly observes acute absence; recogniser retains `ά`; no recogniser confidence | true / true / false | **corrected: `ά`→`α`** |
| Recogniser locator `[100000,100010]` | Valid A/B/E empty-mark predictions; detector observation missing; recogniser `α`, confidence `0.9` | true / false / true | **corrected: `ά`→`α`** |

These are deliberately contradictory geometry records, not evidence that such coordinates occurred in production. They demonstrate that a `scored` flag and a merely finite span override the stated in-window requirement. The required repair is validation of source-specific crop/window ownership and bounds before counting absence; it need not assume that all legitimate source windows have identical dimensions. Until then, one valid source plus an invalidly located source can authorize deletion.

The complete inputs, outputs and absence flags are in [unsafe_release_witnesses.json](ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json). Executable [reviewer tests](ASTRA-SC1c3v3_evidence/test_sf6_reviewer.py) produce **12 failed, 63 passed** ([log](ASTRA-SC1c3v3_evidence/pytest_reviewer.log)). The failures are the two findings above. Passing controls cover missing evidence, unscored A, missing B, clipping, uncertainty, missing locator, valid reader+detector deletion, replacements, repeated signs, mark movement between letters, elision aliases and insertion.

**Policy scope and SF6b MOVE.** The ordinary Boolean rule at [release_gate.py:399](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:399) has the requested source combinations. A∧B counts as one reader even in PRESENCE/FULL; AE additionally checks E. Unsupported character classes lack a reader absence and HOLD. The deletion inventory includes replaced characters and multiplicity while excluding canonical equivalence and pure word-final elision aliases. [l1_common.py:60](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/l1_common.py:60) adds every denied atom to whole-line HOLD before emitting changes. The failure is evidence certification, not that Boolean combination or HOLD dispatch.

The MOVE branch at [release_gate.py:302](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:302) requires an adjacent supported capital, the same base sequence and boundary, no already-attached original breathing, the matching singleton psili/dasia output, and A/B naming with known scored coverage inside the saved window. AE also requires E. The exception is keyed to the consumed spacing sign's original offset; other removed atoms are still checked individually. Independent probes verify that a mismatched kind without two ordinary absences, unnamed B, lowercase target, duplicated spacing sign, additional deleted quote and out-of-window reader cannot obtain release through MOVE.

The two saved capital lines `a963b33d02c23d4127f5ec26-p000012-l0029` and `32aae9fec147d3b483deb96e-p000060-l0057` regain their exact SF5 labels. Each has one allowed `operation=MOVE` with all three absence signals false. Both psili aliases pass full-overlay tests; matching dasia is also checked directly in the deletion guard by [test_sf6.py:99](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/tests/labelfix/test_sf6.py:99). This does not add a new rough-spacing rewrite to the unchanged SF5 composer. No held-out or M2 outcome changes from SF6 to SF6b. A mismatched breathing is not MOVE; an independently valid ordinary two-absence deletion remains governed by SF6, as ruled.

**SF5 tests are not weakened.** The diff adds one exact HOLD helper and modifies four existing test functions; none is deleted. [test_sf5.py:55](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/tests/labelfix/test_sf5.py:55) requires HOLD, the original effective label, empty changes, a denied deletion and the SF6 reason. It does not accept either release or HOLD.

| Edited test | Retained requirement |
| --- | --- |
| Saved 56 witnesses, lines 63–89 | Exact composer-slot equality executes before the HOLD branch; 8 named cases require HOLD; SF6b restores both capital witnesses' exact original SF5 expectations |
| Spacing breathing consumed, lines 113–126 | Incomplete-evidence fixtures require HOLD; the exact atomic SF5 proposal is still asserted |
| Unattached spacing, lines 130–139 | HOLD preserves the original sign; the removed-atom list must be exactly the acute accent |
| Single-source presence, lines 166–177 | Only undetected Google-only punctuation changes to exact HOLD; source census assertions remain |

Function-level comparison confirms existing render/composer/mark-decision functions and `text.py` are unchanged. Changes are the deletion helpers, runtime score binding and overlay enforcement, plus policy metadata. See [readback.json](ASTRA-SC1c3v3_evidence/readback.json).

**The measured cost is reproduced, but it describes the supplied local evidence.** Fresh saved-evidence replays match SF6b's checked-in held-out and M2 metrics exactly, and all witness result rows match. Nineteen input hashes were verified. AB has **45→11 corrected marks, 2→0 wrong, 6→1 new**, and actual releases have **35→6 corrected lines, 333→333 unchanged, 298→327 HOLD**. The mark table applies the additional SF6 line veto to the historical slot instrument; it is not a fresh accuracy score restricted to those six released lines.

The limitation is stronger than reader absence being “often” unavailable: [sf6_measure.py:165](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/sf6_measure.py:165) builds every held-out runtime with empty coverage, no B/E extraction records and no `recognition_confidence`, while retaining the frozen slot decisions. Across AB's 628 proposed removed atoms on 141 proposal-deletion lines, the replay records **zero positive reader, detector or recogniser absence signals and zero allowed deletions**. Twenty-nine previously released lines become HOLD. Thus 11 is the result of the rule applied to this incomplete local evidence; it does not measure the rule's intrinsic yield under full-runtime recomposition.

A full-runtime answer requires the same 666 lines with genuine source-bound A/B predictions and scored extraction coverage (E for AE), valid crop/window ownership, explicit detector observation/head coverage, and recogniser absence evidence with reliable scoring and location provenance. Clipping, uncertainty and missing evidence must remain represented. Recompose from those records under the verified policy, then rescore the same truth and report both slot and actual release outcomes. Filling gaps or copying A into B cannot supply the missing experiment. The current replay cannot predict how many of the 45 corrections would survive.

Verification ran the scoped repository suites `test_sf2`, `test_l1e`, `test_sf3`, `test_sf4`, `test_sf4_review`, `test_sf5` and `test_sf6`: **1,019 passed** ([log](ASTRA-SC1c3v3_evidence/pytest_regressions.log)). Earlier C2/C3 regression witnesses pass and their closures stand. Fresh witness results are SF5: 46 unchanged / 8 HOLD / 2 corrected; L1A: 40 / 5 / 3; quote probes: 64/64 HOLD. The keraia witness remains HOLD. This was a read-only review with no network, detector/R1/CTC inference or crop inspection; outputs are confined to scratch. Pytest ran from the repository root with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`. The two failing certification paths prevent approval to recompose releases for binding under this policy.

ASTRA-SC1c3v3 VERDICT: NOT CLOSED; SF6 rule exact no; SF5 tests not weakened yes; recompose under sf6-release-v1 allowed: no
