**ASTRA-SC1c3v4 — SF6c verification: CLOSED.** SF6-V3-B01 and SF6-V3-B02 are fixed. The imported reviewer tests retain their release/HOLD assertions. The SF6 rule and SF6b MOVE exception remain intact. Releases recomposed under the verified policy may be used for wave 1c as a pseudo-label experiment.

Reviewed HEAD: `d893a04d3dffbf73f5e99641af8a308618879d9b` on the supplied worktree, against SF6b `8c5ad361`. Policy: `sf6-release-v1`, SHA-256 **`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`**. The policy digest now covers the loader, frame-score producer and live runtime writers. [Initial receipt](ASTRA-SC1c3v4_evidence/initial_receipt.json), [production/test diff](ASTRA-SC1c3v4_evidence/production_and_test.diff), [verification readback](ASTRA-SC1c3v4_evidence/readback.json).

| Finding/check | Verdict | Reproduced evidence |
| --- | --- | --- |
| SF6-V3-B01: missing/defaulted recogniser score | **FIXED** | Missing remains `None`; genuine zero and floor values cannot certify absence; local regional evidence is required |
| SF6-V3-B02: source containment | **FIXED** | Shared helper rejects the previous disjoint spans and enforces native bounds provenance |
| Reviewer tests not weakened | **YES** | All 75 pass; only executable import adaptation is the loader-default assertion |
| Scope and outcome preservation | **CONFIRMED** | Saved slot/release outcomes unchanged; 28 already-held M2 checks lose recogniser absence |

**B01 — missing remains missing through the reviewed paths.** [ctc_align.py:81](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/ctc_align.py:81) defaults confidence to `None`; loading at line 108 uses `r.get('confidence')`. Saving retains null, and alignment transfer retains the value without substituting zero. [recognition_fields at line 30](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/ctc_align.py:30) preserves existing evidence or explicitly records unavailable provenance with `scored: false` and no regions.

| Writer/consumer | Verified behavior |
| --- | --- |
| [m2_run.py:127](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/m2_run.py:127), cached replay at line 289 | Writes the actual alignment confidence, native image width and regional evidence; missing remains null |
| [l1_detect.py:40](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/l1_detect.py:40) | Loads through `Alignment.from_record` and writes the same three fields |
| [l1_infer.py:88](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/l1_infer.py:88) | Copies saved score/evidence through `recognition_fields` |
| [l1e_run.py:78](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/l1e_run.py:78) | Preserves saved fields; legacy records receive explicit unavailable provenance |
| [l1e_measure.py:65](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/l1e_measure.py:65) | Uses only saved metadata fields; missing data is not upgraded |
| [r1_extract.py:58](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/r1_extract.py:58) | Missing confidence produces `line_confidence_missing` and unscored coverage |

The restored `l1_detect.py` matches `artifacts/labelfix_l1e/reference/l1_detect.py` **byte for byte after removing exactly two added lines** containing `recognition_confidence`, `image_width` and `recognition_evidence`. The claim about restoration is correct; no other builder behavior changed.

[_recogniser_scored at release_gate.py:308](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:308) requires finite line and regional scores strictly **greater than 0.5**, explicit scored provenance, matching transcript and slot identity, and a regional observation covering the entire saved target window. Zero, null, booleans, invalid values, exactly 0.5 and a high line mean without regional observation cannot be positive absence.

[ctc_align.py:118](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/ctc_align.py:118) derives regional confidence from the minimum maximum posterior over every overlapping valid frame, including blanks. New recogniser alignments retain those actual frame scores at line 268. Legacy alignments without them provide no regions. Object-transfer flags and record-transfer transcript digests prevent borrowed locations from certifying regional observation. Recognition evidence and width are content-bound at [release_gate.py:650](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:650).

The **0.5 floor is justified as the stated conservative admissibility floor**, using the existing R1 cutoff and requiring a strict majority posterior throughout the region. It is not empirically calibrated as an absence probability. The freshly repeated saved-score audit confirms the report:

| Saved line-score population | Records | Minimum | At/below 0.5 |
| --- | ---: | ---: | ---: |
| Matching held-out S0 alignments | 666 | 0.945503 | 0 |
| M2 DEV runtime | 273 | 0.519740 | 0 |
| C1 alignment cache | 91,469 | 0.301551 | 8 |

These distributions establish the stated cutoff's effect on saved **line means**, not regional accuracy. The repair depends on preserving provenance and requiring actual regional observation, rather than on the numeric floor alone.

**B02 — one shared containment contract.** [_source_in_window at release_gate.py:288](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/greekocr/labelfix/release_gate.py:288) now serves ordinary reader A/B/E checks, recogniser location/region checks and MOVE. It requires finite positive spans contained in the saved target window. Native bounds are established from an explicit width, or, for historical reader coverage, the named extraction contract plus scored/known state and an explicitly empty uncertainty list. The historical fallback is supported by the extractor's actual `out_of_image_span` check at [r1_extract.py:84](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/clariden/r1_extract.py:84); generic finite coordinates without that provenance fail. This preserves the two saved capital MOVEs without inventing widths.

The recogniser additionally requires the observed region itself inside its recorded image and covering the whole target window. A letter span merely lying somewhere in the image is insufficient. The former `[100000,100010]` reader and locator witnesses now HOLD in all four modes. **All 16 saved JSON cases HOLD**: the 12 formerly unsafe releases and four existing missing-key controls, with no released label and empty changes. [Fresh overlays](ASTRA-SC1c3v4_evidence/replay/unsafe_witnesses_after.json).

**The reviewer tests were not weakened, and the fixture does not conceal missing production evidence.** AST comparison against the original pass-3 scratch file confirms that replacing `alignment.confidence==0.` with `alignment.confidence is None` is the only executable difference in the imported 75 tests; the comment is updated accordingly. Every release/HOLD assertion is identical. [Exact import diff](ASTRA-SC1c3v4_evidence/reviewer_test_import.diff).

`test_sf6.py` changes only `rich`: it adds an explicit synthetic image width and regional evidence generated by the real `Alignment.recognition_evidence` function from declared synthetic frame scores. This supplies the evidence required by the positive-control fixture. It neither changes saved production records nor fills their missing regional scores.

To check that distinction across writer boundaries, I added [16 scratch tests](ASTRA-SC1c3v4_evidence/test_writer_review.py). They exercise the real M2/L1 writers and saved L1E builder through the release overlay, mocking only inference/extraction. Missing, genuine zero, floor, high legacy line-only and low-regional scores HOLD; valid regional evidence permits the intended detector+recogniser punctuation deletion. **16 passed** ([log](ASTRA-SC1c3v4_evidence/pytest_writer_review.log)).

**SF6c stays within B01/B02.** Function comparisons confirm no changes to the character inventory, SF5 text composer, source-combination Boolean rule, ordinary HOLD dispatch or SF6b matching-kind/capital requirements. MOVE gains the shared bounds check; it gains no new exception. `text.py`, `reading.py`, `segmentation.py`, `l1_common.py`, `r1_common.py` and `test_sf5.py` are byte-identical to SF6b. The missing-confidence extraction reason and expanded evidence/policy binding belong to the two repairs.

Fresh before/after replays match the checked-in SF6c metrics, per-slot proofs and release rows. **No local held-out, M2 or saved-witness release outcome changes**, and no newly held lines occur in these cohorts. The 28 changed M2 line/mode check records concern 11 unique lines: the old recogniser-absence signal becomes unavailable because regional scores were never saved; every affected line was already HOLD.

| Cohort | SF6b → SF6c |
| --- | --- |
| Held-out AB mark instrument | Corrected 11→11; wrong 0→0; new 1→1 |
| Held-out AB actual lines | Corrected 6→6; unchanged 333→333; HOLD 327→327 |
| M2 DEV, all modes | Mark metrics and release statuses identical; AB/AE remain 273/273 HOLD |
| SF5 witnesses, 56 | 46 unchanged / 8 HOLD / 2 corrected, unchanged |
| L1A witnesses, 48 | 40 unchanged / 5 HOLD / 3 corrected, unchanged |
| Quote probes, 64 | 64/64 HOLD, unchanged |

The separate repeated runtime/archive audit also matches every saved per-file result and score distribution; archive enumeration order was normalized for comparison. It adds no HOLDs. Input hashes were rechecked, and locked stratum (ii) records were not decoded or composed. [Replay comparison](ASTRA-SC1c3v4_evidence/replay/comparison.json), [changed checks](ASTRA-SC1c3v4_evidence/replay/check_changes.jsonl), [runtime audit](ASTRA-SC1c3v4_evidence/runtime_audit.json).

The 666-line replay still lacks complete extraction and recogniser regional evidence. Its 11 corrected marks and six released corrected lines remain results of that incomplete local instrument; SF6c does not establish full-runtime yield or training-wave precision. Recomposition under the exact policy digest above is allowed for the stated pseudo-label experiment, preserving HOLDs and the existing ensemble caveat.

Validation: **1,189 scoped repository tests passed**, including all 75 imported reviewer cases, all 95 SF6c certification cases and the earlier SF2/L1E/SF3/SF4/SF5/SF6 regressions ([log](ASTRA-SC1c3v4_evidence/pytest_scoped.log)). The additional 16 writer checks passed. This is not a claim that the entire labelfix suite was rerun; the report's separate full-suite socket setup limitation remains as documented. Repository read-only; scratch outputs only; no network or detector/R1/CTC inference, no real crops inspected. Pytest used the repository root, `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`. No earlier finding is reopened and no new scope is added.

ASTRA-SC1c3v4 VERDICT: CLOSED; B01 fixed yes; B02 fixed yes; reviewer tests not weakened yes; recompose under sf6-release-v1 allowed: yes
