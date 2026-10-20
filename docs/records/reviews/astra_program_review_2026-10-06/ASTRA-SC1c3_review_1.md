# ASTRA-SC1 cycle 3 — narrowed release-gate re-review

**FAIL: do not bind releases recomposed under the current SF3 gate to wave 1c yet, including as a pseudo-label experiment.** The original uncertainty and unsupported-deletion probes now abstain, and the release payloads correctly exclude HOLD. However, SF3 introduces a relevant-clipping bypass for capital diaeresis. The owner-page adapter also omits evidence used by the release path. Of the five requested cycle-2 findings, **2 are FIXED and 3 are PARTLY fixed**. There is **1 new BLOCKER, 1 new MAJOR and 1 new MINOR**; the remaining notes-binding defect is a residual of C2-N02, not another new finding.

Reviewed 17 October 2026. Repository: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, HEAD **`63119b842c8edebcba452ce8e742765c331b5944`**. Source `file:line` references below resolve under that root. Review output and new witnesses reside only in the writable `ASTRA-SC1c3` scratch directory. Repository status and HEAD were unchanged at the final check.

Current policy: **`sf3-release-v1`**, digest **`db81e2c4748c4de3781cf78aae8c82ad1dab0c05e80772bcc051bda39b455ed4`**. No network, GPU work, CTC/R1 inference, training or native-crop decoding was performed. The pixel witnesses use synthetic arrays. Saved-data checks include the 92 owner records, the earlier 160-line SF2 mock and the 64-line L1E mock; these are not new crop/model runs or production-cohort accuracy measurements. The coordinator's R0/R2/S7 deferrals remain outside the verdict.

## Requested cycle-2 verdicts

| Finding | Verdict | Verified repair and remaining boundary |
|---|---|---|
| **C2-B01 — recorded uncertainty accepted** | **PARTLY** | The original UNKNOWN/no-pixels, UNKNOWN/out-of-image, segmentation and clipping probes now HOLD. Reader prediction/coverage uncertainty is consumed at `greekocr/labelfix/release_gate.py:150–168`; detector uncertainty at `:224–235`; K1 at `:249–261,324–330`. L1 ignores cached modes and recomposes at `scripts/labelfix/clariden/l1_common.py:45–60`. Nevertheless, SF3's capital relevance predicate now discards a **relevant** top-cut veto and releases a mark deletion: **C3-B01 below**. Thus the original broad observation-safety requirement is not closed. |
| **C2-M01 — unsupported mark deletion** | **FIXED** | The character/mark domain and multiplicities are explicit at `release_gate.py:23–25,75–85`. Raw and NFD guards at `:121–147` reject unsupported deletions, non-Greek diacritic edits and base substitutions. L1 checks both original→recogniser and original→proposal at `l1_common.py:57–60`, and retains original bytes for unchanged labels at `:61–62`. The actual-overlay macron, Latin-accent and double-accent witnesses HOLD in both modes. Current targeted tests and the supplementary domain checks below pass. This closes unsupported-mark deletion; it does not certify observation of editable marks. |
| **C2-M02 — page/composer parity** | **PARTLY** | M2 is a direct shared-composer alias (`scripts/labelfix/m2_run.py:113–114`); the combined page calls that composer (`scripts/labelfix/owner_pages_build_combined.py:162–168`). Replaying saved evidence gives **92/92 current PRESENCE text/slot matches**, both opening quotes restored and **15/15 former missing-prediction/localisation/unnamed witnesses held**. But the page cannot supply the diagnostic E evidence now used by runtime relevance: **C3-M01 below**. The old CN1 outputs remain historical, not repaired in place. |
| **C2-N01 — divergent agreement diagnostic/overwritten flag** | **FIXED** | `scripts/labelfix/agreement_mode.py:18–24` passes external flags into `compose_runtime`. Its actual CLI now reports one HOLD for each original witness: external K1 flag, and Google=R1 with detector-family disagreement. The old diagnostic is explicitly historical and non-release (`agreement_mode_historical.py:1–5`); its decisive flag/disagreement chain is repaired at `:43–47`. |
| **C2-N02 — box stability mistaken for ownership/approval** | **PARTLY** | `scripts/labelfix/box_regression.py:69–83` compares owners, absolute pixel membership/source IDs and status even at IoU 1, with missing fields reported UNKNOWN. Its notes CLI requires and verifies a page/notes binding at `:116–137`. **The other identified approval path is still open:** `scripts/labelfix/owner_implicit_changes.py:68–75` hashes the pages/sidecars but loads arbitrary notes without binding or hashing them; `:46–54` can emit `REGRESSION? (reviewed snapshot approval)`. The scratch CLI witness supplies unbound notes and succeeds. Apply the same notes-binding requirement there; keep this residual at its original MINOR severity. |

“FIXED” refers to the stated defect, not independent print-truth qualification. The tally does not include the explicitly deferred cycle-1 findings or C2-M03.

## New findings, ranked

### C3-B01 — BLOCKER: the capital side-zone rule releases clipped overhead diaeresis

**Trigger and code.** `release_gate.py:182–192` treats every uppercase base or pixel-classified capital as having the `.35 × xh` top extent. That extent comes from the **preposed upper-left** search (`greekocr/labelfix/ink.py:482–505`), not a complete upper-mark zone for every capital. Capital Ι and Υ also carry **overhead dialytika**. The detector retains overhead blobs through its separate above-mark path (`ink.py:390–398,429–452`), so reducing the whole upper observation requirement to the side zone is inconsistent with the evidence it can produce.

**Executable witness.** The review constructs a capital body with top `y=8`, `xh=20`, and two overhead dot fragments touching crop row zero. The real `mark_evidence()` geometry helper emits **two above blobs, both `touches_border=True`, and `clipped_top=True`**, with `case_class=capital` and `band_source=capital_height`. Detector naming is supplied as dialytika; A and B are supplied as identical empty mark sets with clean, scored coverage. No classifier/reader inference is run or asserted.

The SF3 predicate computes `8 − .35×20 = 1`, declares `top_cut=False`, and drops the recorded cut. The actual L1 overlay returns:

| Original | A/B sets | Detector evidence | SF3 release result |
|---|---|---|---|
| `Ϊ` (`Ι` + U+0308) | empty / empty | dialytika; two top-border blobs; clipped top | **`Ι`, corrected, no HOLD** |
| `Ϋ` (`Υ` + U+0308) | empty / empty | same synthetic geometry | **`Υ`, corrected, no HOLD** |

The byte-identical L1E-baseline gate, verified against `fd967dc4`, returns **HOLD / `detector_clipped_top`** on these same records. This is a newly introduced release bypass, not merely an unmeasured common A/B classification error: the policy has an explicit observation warning and erroneously declares it irrelevant. The edit guard correctly recognises dialytika as editable and therefore cannot compensate.

Evidence: [capital_diaeresis_witnesses.json](ASTRA-SC1c3_evidence/capital_diaeresis_witnesses.json), [before/after](ASTRA-SC1c3_evidence/capital_before_after.json), [scratch tests](ASTRA-SC1c3_evidence/test_c3_scope.py), [failure log](ASTRA-SC1c3_evidence/pytest_new_witnesses.log). These establish policy reachability and synthetic pixel custody, **not prevalence or a demonstrated erroneous production label**.

**Required repair.** Evaluate all potential mark zones for the character, including capital overhead dialytika, separately from preposed marks. An empty A/B prediction cannot remove a zone from the observability requirement. Only discard a recorded cut when saved geometry establishes clearance for every relevant zone; otherwise HOLD. Also do not infer a capital-height envelope solely from recogniser case when the saved physical case/band disagrees. Add the capital-dot witnesses and recompose under a newly bound policy. No R2 retraining or S7 adoption is needed to retain this conservative veto.

### C3-M01 — MAJOR: owner-page ENSEMBLE_AB drops a relevance input used by L1r

`release_gate.py:350–356` gathers `signal_parts` from **every** saved peer, including diagnostic E, and passes them into composition. `:282–285,304–305` uses those signals when deciding whether bottom clipping is relevant. This matches SF3's explicit “subscript predicted by any signal” rule and its E witness (`tests/labelfix/test_sf3.py:65–73`).

The owner-page adapter passes only A and the selected peer (`owner_pages_build_combined.py:162–168`). Its CLI likewise has only one selected peer binding (`:217–232`), with no path for diagnostic E relevance evidence in ENSEMBLE_AB.

**Witness:** base `ι`; `clipped_bottom=True`; A=B=empty; E=`subscript`; otherwise clean evidence. `compose_runtime(..., 'ENSEMBLE_AB')` produces **HOLD / `detector_clipped_bottom`**. The actual page `combine(..., 'ENSEMBLE_AB')` produces **ACCEPT**, with no reasons. The existing parity test uses identical A/B/E predictions and never exercises this distinction (`tests/labelfix/test_l1e.py:9–16,112–122`).

This discrepancy does not bypass L1r's own veto, but prevents the page from being a faithful review of the release policy. Pass one bound runtime/evidence envelope through every adapter, including all signals used for relevance, and test exact parity on differing diagnostic-peer predictions. The evidence is in the same scratch test and failure log linked above. The confirmed 92-line PRESENCE parity remains valid at its narrower boundary.

### C3-N01 — MINOR: an advertised apostrophe alias can abort composition

SF3 explicitly accepts U+02BC `ʼ` as an elision alias (`release_gate.py:25,88–103`). It is also `isalpha()`, so the current slot builder gives it a letter slot (`greekocr/labelfix/segmentation.py:41–57`). The renderer removes a word-final alias but retains that slot. K1 then rejects the rendered-letter/slot mismatch (`greekocr/labelfix/reading.py:132–135`).

The synthetic `δʼ` runtime, including its legitimate modifier-letter slot and detector elision decision, raises **`ValueError: reading letters and evidence slots differ`** through `compose_runtime`. This fails closed, but can abort recomposition instead of producing an auditable per-line outcome. `tests/labelfix/test_sf3.py:120–124` tests the alias only through `edit_guard`; its composer witnesses at `:138–149` use ASCII apostrophes.

Make the punctuation/letter classification consistent across slotting, rendering and K1, preserving correspondence and offsets. Exercise every declared alias through actual composition, not just string comparison. The fifth scratch-test failure reproduces this defect.

## Gate semantics and edit-guard domain

The main **ENSEMBLE_AB agreement rule is implemented as ruled**: A supplies output names (`release_gate.py:319–320`); exact A/B mark-set agreement is required (`:238–244`); detector family/name disagreement is not a veto in ensemble modes (`:245–248`). Missing B never falls back to A. Both readers' missing/UNKNOWN/uncertain coverage, unresolved localisation/segmentation, explicit relevant UNSEEN, unnamed evidence and K1 flags remain decisive. The retained detector observation vetoes are uncertainty checks, not a restored kind veto. Apostrophes and opening quotes still come from detector decisions (`:94–104,322–324`).

The shared path reaches L1r through `l1_common.overlay`; L1E invokes that recompose path at `scripts/labelfix/clariden/l1e_run.py:122–129`. M2's live composer and saved measurement call the gate (`m2_run.py:114,130`; `m2_score.py:435–439`); current agreement analysis uses `compose_runtime`; owner builders share serialization (`scripts/labelfix/owner_reading.py:44,60–69`). L1E measurement uses the runtime adapter at `l1e_measure.py:64–81`. A shared function alone does not establish caller parity when an adapter omits an input, as C3-M01 demonstrates.

SF3's **bottom relevance** covers α/η/ω including capitals, explicit/possible adscript context, and subscript evidence from detector, recogniser, A and peers (`release_gate.py:195,276–285,350–356`). Relevant explicit UNKNOWN/UNSEEN is still held (`:231–235`). Missing/invalid top geometry cannot establish clearance (`:187–193`). K1 observation flags use the same relevance predicate (`:199–207,286–306`), while unknown observation predicates and orthographic flags remain decisive. The capital-overhead case above is the identified unsafe exception in the top predicate.

The edit domain is **explicit and covers the seven ordinary polytonic mark names**, with a conservative protected remainder:

| Character/mark class | Policy |
|---|---|
| Same Greek base; psili/dasia, acute/grave/perispomeni, dialytika, ypogegrammeni | Editable subject to reader/observation/K1 gates; at most one per family; bearer restrictions enforced. |
| Macron, breve, unsupported combining marks, duplicate accents/breathings, incompatible breathing+dialytika, marks on unsupported bearers | An altered cluster causes HOLD. |
| Non-Greek letters/diacritics and unsupported Greek clusters | Raw spelling and decomposed content protected; canonical normalization is not permission to rewrite them. |
| Punctuation | Explicit detector-led opening-quote/final-elision policy; other content and internal/trailing space counts preserved, with declared codepoint aliases. C3-N01 is an integration failure in one alias, not an unsafe unsupported-mark deletion. |

Thus this is not a reader for **every** mark printed in polytonic material: length marks and unsupported combinations are deliberately outside its edit vocabulary. They are protected by abstention. The renderer may show a stripped proposal on a held line; the overlay emits no usable label for that HOLD. My supplementary sweep found **24 unsupported precomposed Greek/Greek-Extended cases and 140 synthetic unsupported cluster deletions**, all rejected. This is useful domain coverage, not a proof over all Unicode strings. See [domain checks](ASTRA-SC1c3_evidence/edit_domain_checks.json).

## L1r/L1E receipt and payload checks

The release structure is sufficient for a careful consumer to verify source identity and pairing. `l1r_recompose.py:18–59` checks completed historical inputs, step/binding/shard hashes and exact source/selection bindings; `:61–74` checks the ensemble receipt/shards; `:97–103` verifies inputs unchanged and hashes the output set. The L1E inference path checks A's slot/window identity and shares the actual extraction coverage with B/E (`l1e_run.py:59–78`); its checkpoint loader checks hash, arm and strict model compatibility (`:17–23`). No inference was rerun here.

`l1_common.py:139–157` writes controls only for corrected/unchanged rows and checks the actual control-ID payload. Manifests include source/selection hashes, overlays, kept IDs, wave/source counts, exclusions, input-document bindings, checkpoint hashes and the policy binding (`:165–183`). The overlay has a hash of each original label, explicit decisions and no label on HOLD (`:40–60`). A consumer must use the exact kept-ID set, verify those hashes against the original source, and reject any HOLD/out-of-scope fallback. Hash integrity does not make an erroneously accepted decision safe.

I checked actual files, not just declared booleans:

| Available release | Mode | Corrected / unchanged / HOLD | Kept = original-control rows |
|---|---|---|---|
| Earlier SF2 training-source mock, 160 lines | PRESENCE and FULL, each | 3 / 10 / 147 | 13 |
| Saved L1E verification mock, 64 lines | PRESENCE / FULL / AB | 14/1/49; 11/0/53; 20/3/41 | 15 / 11 / 23 |
| Fresh scratch recomposition of those 64 saved records with current SF3 | PRESENCE / FULL / AB | 15/1/48; 11/0/53; 21/3/40 | 16 / 11 / 24 |

All original-label hashes, original control texts, overlay/control/kept hashes, unique paired IDs, per-wave status totals and no-HOLD fallback checks pass. The earlier SF2 mock's **27 input / 12 output** bindings verify; each L1E/SF3 mock's **20 input / 17 output** bindings verify. The three local checkpoint files independently hash to the declared A/B/E identities. All five current policy-source hashes match.

The exact caveat is present in every checked L1E/current corrected and control manifest:

> A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment.

Keep these receipt boundaries explicit:

- The 64-line artifacts are **verification-only held-out mocks**, with that exclusion/R0 designation. They are not training releases. The old 160-line SF2 mock is also not the full training-wave release. No completed remote production L1E/L1r payload was verified in this offline review.
- The current recomposition retains historical inference `code_sha256` and a hard-coded historical `code_commit` (`l1r_recompose.py:78–82`), alongside the **current** `policy_binding`. Exactly the gate file differs between the recorded inference-source set and this checkout. Use the explicit policy-source bytes/digest for the composer identity; do not interpret the historical commit string as the harness HEAD or relabel a pre-SF3 payload as current.
- **13 apostrophe detections** in the saved 64-line input lack blob boxes; the recomposition receipt records that fact. The boolean decisions are usable for deterministic replay, but these files alone cannot provide exact-pixel apostrophe custody. SF2 already discloses this historical limitation (`docs/records/labelfix/spellcheck/SF2_REPORT.md:62–64`).
- The unchanged held-out wrong/new totals in SF3 are reported against its frozen instrument, not independent training-wave precision. The source report also discloses additional M2 control changes. Neither those totals nor valid receipt hashes neutralise C3-B01's observation bypass.

Evidence: [release readback](ASTRA-SC1c3_evidence/releases_checks.json), [fresh recomposition receipt](ASTRA-SC1c3_evidence/recomposed_mock64/receipt.json), [checkpoint bindings](ASTRA-SC1c3_evidence/checkpoint_bindings.json), [owner readback](ASTRA-SC1c3_evidence/owner_checks.json), [audit script](ASTRA-SC1c3_evidence/audit_saved.py).

## Probes and repository-test verification

The cycle-2 witness probes **were promoted to repository tests**. `tests/labelfix/test_sf2.py` covers observation/overlay failures, unsupported edits, quotes and missing predictions, external flags, owner/pixel/status diffs and box-CLI notes binding. `test_l1e.py` extends them to both readers, missing peers, exact set agreement, checkpoint/window contracts and actual paired releases. `test_sf3.py` covers the new relevance and punctuation rules. The residual/new counterexamples found here are not covered by those passing tests.

| Fresh execution | Result |
|---|---|
| Current `test_sf2.py`, `test_l1e.py`, `test_sf3.py` | **208 passed** |
| Current SF2 tests against an isolated Python-source snapshot of pre-SF2 `c8b4974b` | **50 failed, 11 passed** |
| Current SF3 tests with the byte-verified `fd967dc4` L1E gate | **28 failed, 42 passed** |
| New scratch witnesses: clipped capital Ι/Υ, page/E parity, residual notes binding, modifier apostrophe | **5 failed**, each at the reported behavior |

The before-run failures include missing new APIs as well as behavioral assertions; they are not 50 separate production-error demonstrations. All pytest invocations ran from the repository root with the requested interpreter, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider` and the repository on `PYTHONPATH`. The pre-SF2 run additionally prioritised the isolated scratch source snapshot. Logs: [current](ASTRA-SC1c3_evidence/pytest_gate.log), [pre-SF2](ASTRA-SC1c3_evidence/pytest_sf2_before.log), [pre-SF3](ASTRA-SC1c3_evidence/pytest_sf3_before.log), [new failures](ASTRA-SC1c3_evidence/pytest_new_witnesses.log).

The original `review_probes_original.py` and `geometry_probes.py` run unchanged from scratch. Their deferred geometry observations are not new findings in this cycle. The unchanged cycle-2 `new_probes.py` stops because the release API now requires raw predictions/coverage instead of trusting `modes`; its scratch adaptation changes only that runtime envelope. `agreement_probe.py` stops because the former top-level loop no longer exists; the replacement checks exercise the actual current CLI and preserve both witness outcomes. These interface failures are recorded, not counted as product failures or silently treated as passing probes. See [unchanged probe runs](ASTRA-SC1c3_evidence/unchanged_probe_runs.json), [adapted probe](ASTRA-SC1c3_evidence/new_probes_adapted.py), [adapted results](ASTRA-SC1c3_evidence/new_probes_main.json), [agreement CLI results](ASTRA-SC1c3_evidence/agreement_cli_checks.json).

## Wave-1c binding decision

**No, for releases recomposed under this current gate.** The pseudo-label caveat properly limits the scientific claim, but does not waive the explicit rule against accepting relevant unobserved evidence. Fix C3-B01, close the page evidence mismatch, and add the failing witnesses before producing a new bound release. Correct the residual notes-binding and apostrophe integration defects within this gate-review work. Then verify the actual complete training-wave overlays, kept/control payloads, exclusions and source/checkpoint/policy hashes, retaining the verbatim caveat and excluding every HOLD. This decision does not reopen the coordinator's deferred R0/R2/S7 work or require those scientific programmes to finish before a properly gated pseudo-label experiment.

ASTRA-SC1c3 VERDICT: FAIL; C2 fixed 2/5; new blockers 1; new majors 1; L1r releases usable for wave 1c: no
