**ASTRA-SC1 cycle 3 — verification pass 2: SF5 only**

**CLOSED. The three SF5 rules hold in the reviewed code and probes. Recomposition under `sf5-release-v1` is allowed.** No SF5 defect remains from this verification. The earlier C3/C2 findings remain closed; their repository regressions pass. This verdict concerns the specified rule changes and saved evidence, not print precision or a completed full-production release.

Verified 17 October 2026, read-only repository `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, HEAD **`05a9bf4a5db26982c976dcc1af1c2f3acf212a2e`**. The three production files are byte-identical to **`5bdbcd41`**; the subsequent commit adds only the verification brief. The frozen baseline files were independently checked against **`c6064650`**. Current policy: **`sf5-release-v1`**, digest **`0f557baafd8531be83ced3613e3899aed60ef5c8b4c17b2230067412e3ef64b9`**. [Source/baseline receipt](ASTRA-SC1c3v2_evidence/initial_receipt.json). Source `file:line` references below resolve under the repository root.

**The three ruled changes.** I read `c6064650..5bdbcd41`, the SF5 report and the supplied L1A print-audit report. The production diff is confined to `text.py`, `release_gate.py` and `l1_common.py`. Reader agreement, observation relevance, coverage requirements, mark naming and supported-character checks are unchanged. The punctuation-guard exception is the specified atomic spacing-breathing attachment.

| Rule | Verdict | Evidence |
|---|---|---|
| Never delete a word-final elision shared by Google and the recogniser | **Holds** | `greekocr/labelfix/text.py:44–70` classifies the five aliases after a letter cluster and records letter boundaries. `release_gate.py:159–181` requires identical letter sequences, restores missing consensus signs and retains Google's alias spelling. A sequence mismatch returns an unmodified proposal, but `l1_common.py:60–63` still applies both edit guards and withholds the label. **4,000 contextual overlay probes: 3,500 released, 500 HOLD, zero released consensus losses; 20/20 base-sequence mismatch cases HOLD with no label.** Cases include multiple elisions, repeated signs, apostrophe plus quote, line-final signs, hyphenation, line breaks and combining marks before the sign. |
| Consume spacing ᾿/᾽ only together with the attached breathing | **Holds** | `text.py:50–60`, `release_gate.py:98–100,128–148,164–179,221–222`. The same letter boundary must have the source spacing breathing and a proposed combining breathing. Without attachment, the spacing codepoint is retained or the line HOLDs. **256 release cases** exercise attachment/nonattachment; **seven direct `_breathing_pair` cases** retain real word-final apostrophes and surrounding quotes, retain an unattached breathing, and refuse a mismatched-letter substitution. The two saved doubled-breathing witnesses become one breathing each. |
| Alias-only changes are not corrections | **Holds** | `text.py:73–76` folds only eligible elision codepoints while retaining combining marks and other text. `l1_common.py:56–65` returns original label bytes and empty changes for unchanged lines; `:140–145,175` counts `alias_only` only within `unchanged`. **600 accounting probes** distinguish pure aliases from concurrent acute/grave, breathing, subscript and diaeresis edits: no real mark edit is hidden. The actual manifest/overlay/paired-control regression also passes. |

[Reviewer probe code](ASTRA-SC1c3v2_evidence/reviewer_probes.py), [results](ASTRA-SC1c3v2_evidence/reviewer_probes.json), [run output](ASTRA-SC1c3v2_evidence/reviewer_probes.log). These are finite counterexample checks, not a proof over arbitrary Unicode text. Held proposals may still omit an elision; the release boundary emits no label for HOLD. That distinction is preserved in the checks.

**Saved evidence and slot parity.** Fresh executions of `sf5_measure.py witnesses`, `heldout` and `m2`, directed entirely into scratch, reproduce the checked-in SF5 metrics exactly. I also compared the actual slot records and HOLD lists, rather than relying on the boolean proof rows. Fifteen input-file hashes verify. [Independent readback](ASTRA-SC1c3v2_evidence/readback.json), [readback code](ASTRA-SC1c3v2_evidence/readback.py).

| Cohort | Verified result | Evidence boundary |
|---|---|---|
| 56 witnesses | **56/56 frozen SF4 labels/statuses reproduced; 2,096 slot records identical; 59/59 consensus atoms retained; 2/2 doubled breathings repaired; both known reader errors unchanged.** | Actual saved-runtime recomposition. The seeded overlays lack diagnostic E; no E or original full-envelope digest was invented. |
| Held-out 666 | **81,700 slot/mode records identical**, including parts, decisions and reasons; all mark event identities and totals unchanged. | **Saved-decision text replay, not full runtime recomposition.** Complete extraction coverage is unavailable locally. The run rerenders with both versions and verifies equal recogniser/proposal guard outcomes while retaining frozen decisions. |
| M2 DEV | **273 cards; 39,848 slot/mode records identical**, including HOLD lists; mark-pair events and control edits unchanged. | Actual saved-runtime recomposition, filtered to the frozen DEV allowlist before runtime decoding. No locked stratum (ii) runtime or truth row was evaluated. |

The unchanged held-out mark rows are:

| Mode | Corrected | Wrong | Missed | HOLD errors | New |
|---|---:|---:|---:|---:|---:|
| PRESENCE | 42 | 1 | 2 | 35 | 5 |
| FULL | 37 | 0 | 0 | 43 | 3 |
| ENSEMBLE_AB | **45** | **2** | 6 | 27 | **6** |
| ENSEMBLE_AE | 46 | 2 | 6 | 26 | 9 |

These retain the existing 80-error denominator and 10,046 known / 300 unknown-truth mapped slots per mode. They do not establish new print truth. On M2 DEV, PRESENCE/FULL remain 7 corrected, 6 missed and 30 HOLD errors out of 43; AB/AE remain 0 corrected, 6 missed and 37 HOLD errors because peer evidence is missing. Accepted changed control slots remain 16/9/0/0 respectively. [Held-out metrics](ASTRA-SC1c3v2_evidence/heldout/metrics.json), [M2 metrics](ASTRA-SC1c3v2_evidence/m2_dev/metrics.json).

**Elision truth and the 26→1 claim.** The source and coverage are stated correctly. The R0 continuity records contain **213 print-positive sites and 5 explicitly absent sites on 180/666 lines; zero complete lines are certified**. Of the positives, **212** have a matching pixel-adjudicated human Wikisource emission and **one** uses R0 fallback. Across all 218 scored sites, the split is **214 human-supported / 4 R0 fallback**. Ten adjudicated quote sites and one unresolved site are excluded. The two adjudicated word-initial elisions count as present when emitted; they are not silently excluded merely because SF5's preservation rule is word-final. M2 DEV has **zero certified elision sites**, so its elision accuracy remains **UNKNOWN**, not zero errors.

An independent codepoint scan, using the frozen R0 letter-alignment convention, reproduces the effective-label counts:

| Mode | SF4 kept / deleted / added | SF5 kept / deleted / added |
|---|---:|---:|
| PRESENCE | 188 / 25 / 1 | 212 / 1 / 1 |
| FULL | 189 / 24 / 1 | 212 / 1 / 1 |
| ENSEMBLE_AB | **187 / 26 / 1** | **212 / 1 / 1** |
| ENSEMBLE_AE | 187 / 26 / 1 | 212 / 1 / 1 |

Thus **AB deleted 26→1 is correct under the stated effective-label definition**: absence relative to adjudicated print, with Google retained for held lines. The remaining omission is `51fe7386-p000024-l0017`, R0 card `item01026`: Google already has `ἐς` where print has `'ς`; the line stays held. The one added sign is also already in Google on held `384c3f89-p000179-l0019`, card `item00061`. Neither is a new SF5 released edit. Added counts cover only the five certified absent sites. Candidate proposals, before held-line fallback, remain a different row: 42→2 omitted sites in every mode. [Per-site omission/addition trace](ASTRA-SC1c3v2_evidence/readback.json), [complete replay events](ASTRA-SC1c3v2_evidence/heldout/elision_events.jsonl).

Whole-line AB accounting reproduces **133→35 corrected**, **235→333 unchanged**, **298→298 held**, with **75 alias-only lines included within unchanged**. The reported **431** production AB alias-only lines are historical SF4 audit counts; this verification does not claim to have regenerated all production labels.

**Out of scope notes — recorded, not ruled.**

- Among the 56 witnesses, **one Google-only apostrophe deletion remains released**: `a300f5e1c3f6a38d97201791-p000442-l0085`, `Ι'.` → `Ι.`. The recogniser lacks that sign; this is outside the consensus rule and remains SF4 behavior.
- The two saved word-initial prefix edits also remain: `453f156dc6352286456a08cb-p000100-l0002`, `᾿στὸν` → `'στὸν`, alongside its existing accent edit; and `b518f9f9b73fe9a3257fe2f0-p000041-l0022`, initial `᾿ποὺ` → `“'ποὺ`, alongside restoration of the later consensus elision. These are not counted as word-final alias-only changes.
- The held-out aligned source census has **one Google-only proposal deletion**, on a held line, versus **201/201 consensus atoms kept** across 608 aligned lines. M2 DEV has **one Google-only proposal deletion**, also retained behind HOLD, versus **4/4 consensus atoms kept** across 173 aligned lines. The 58/100 base-mismatched lines are excluded from those site censuses. These cohort counts are not an estimate of residual deletions in the full training release.
- A synthetic leading opening quote with no detector quote is removed under **both SF4 and SF5**. The initial scratch spacing probe overreached by also requiring that quote to survive, producing 64 assertion failures. All 64 were checked against frozen SF4 and separated from the SF5 breathing assertions; the original probe/log/results are retained with `.initial` suffixes. [Before/after quote cases](ASTRA-SC1c3v2_evidence/out_of_scope_quote_probe.json). This unchanged quote policy does not alter the verdict.

**Regression execution and release decision.** **606 repository tests passed in 3.18s**: 386 prior SF2/L1E/SF3/SF4 tests, including the original C3 witnesses, plus all 220 SF5 tests. The Ϊ→Ι witness still HOLDs. No repository test was edited. [Pytest log](ASTRA-SC1c3v2_evidence/pytest_regressions.log). The broader suite's previously reported loopback setup issue was not rerun or used as a new gate finding in this SF5-only pass.

All runs used the requested Python, repository-root `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`, and pytest `-p no:cacheprovider`. No network, detector/GPU/CTC/R1 inference or native-crop decoding occurred. Outputs are confined to this scratch directory; repository HEAD and status are unchanged.

**Recompose under SF5: yes.** The SF4 releases remain unbound as directed. A new release must actually use this SF5 policy and retain the existing receipt, kept/control, no-HOLD-fallback and pseudo-label-caveat requirements. This verification permits that recomposition; it does not claim a completed production payload or measured training-wave precision.

ASTRA-SC1c3v2 VERDICT: CLOSED; SF5 rules hold yes; slot decisions unchanged yes; recompose under sf5-release-v1 allowed: yes
