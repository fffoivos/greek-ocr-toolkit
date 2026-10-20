# SF3 — release-gate relevance

17 October 2026. **ENSEMBLE_AB holds 256/666 lines, down from 268, and corrects 49/80 errors, up from 46. Wrong/new remain 2/6, with identical slot identities and mark sets.** PRESENCE holds 339 lines, down from 345. All **450 labelfix tests pass**; no existing test was changed.

The checkout is `opus/spellcheck` at `6081dd4e2489598248086f32910df9d3e9792fd9`, which adds only the SF3 brief after L1E `fd967dc4`. No Git metadata was written. Network use was restricted to the Clariden measurement and its evidence readback. Detector, R1 and CTC population inference runs: **zero**. M2 replay used Mac CPU and saved evidence only.

## Gate changes and safety boundary

[`release_gate.py`](../../../../greekocr/labelfix/release_gate.py) is the only existing source file changed. Release, measurement and owner-page adapters continue to call this shared gate. Policy is `sf3-release-v1`, digest `db81e2c4748c4de3781cf78aae8c82ad1dab0c05e80772bcc051bda39b455ed4`.

**Bottom clipping:** a slot is held for a bottom cut when its base is α/η/ω, including capitals; it is an explicit or possible iota-adscript slot; or subscript is present in detector, original recogniser, A, B or E evidence. The frozen L1E gate already implemented the α/η/ω restriction, so there is no population reduction to claim from adding that restriction. SF3 closes the missing-signal and adscript cases. A written ι/Ι immediately following Α/Η/Ω is conservatively treated as a possible adscript without claiming a linguistic adjudication. Irrelevant clipping remains in the serialized evidence.

**Top clipping:** the saved meanline and x-height at the slot's local x determine whether crop top `y=0` intersects its upper mark zone. The lower-case/rho extent is `meanline − .9 × xh`, using the existing observation-zone contract; capital side marks use `capital-height meanline − .35 × xh`, from the detector's preposed-mark zone. A `.06 px` margin covers saved-coordinate rounding. A consonant without an upper Greek mark zone does not acquire one merely because a signal contains a mark. Missing, invalid or non-finite geometry cannot prove clearance. No geometry is refitted and no pixel/model extraction is repeated.

**Unobserved remains unobserved:** explicit relevant UNKNOWN/UNSEEN zones, reader uncertainty, missing evidence, localisation/segmentation failures and unnamed marks still hold. This is a relevance rule over stored local geometry, not a validated per-pixel observability mask or a new physical-accuracy claim.

**K1:** the same relevance predicate filters known clipping/zone observation flags at line, slot and external-flag entry points, including saved HOLD reasons. Orthographic conflicts and unknown observation predicates remain decisive. The actual 666 contain **64 `K1:observation:unnamed` and 44 `K1:observation:localisation_unknown` receipts, unchanged**. Neither is an irrelevant clipping flag. Total K1 receipts stay **260**, on **144 distinct slots**.

**Punctuation:** the shared release composer preserves prefix elisions and closing quotes that the old renderer removed globally. Only word-final elisions after Greek letters are replaced by the detector's canonical `’`; opening quotes retain the existing detector policy. The guard accepts the explicit apostrophe aliases `'`, `᾽`, `᾿`, `’`, `ʼ`, single/double quote codepoint variants, and internal/trailing NBSP/narrow-NBSP versus ordinary space. Quote content and the number of internal/trailing spaces still have to match. Base substitutions, unsupported marks, punctuation deletion outside the stated detector policy and arbitrary whitespace changes remain held. The detector/reader implementation and historical scorer bindings are unchanged.

## Held-out instrument: L1E final → SF3

Both phases ran on Clariden with the saved A/B/E predictions, S6 detector records and frozen S4 ownership/print-truth instrument used by L1E. The baseline reproduced **all 666 complete decision records and every L1E table cell exactly**. The fixed domain remains **80 Google mark errors**, **10,046 known** and **300 unknown-truth** mapped/scored slots. Unknown truth is excluded from outcome counts. These are slot outcomes; a line with any HOLD is excluded from whole-line release.

| Mode | Corrected / 80 | Wrong | Missed | HOLD errors | New | Lines held / 666 |
|---|---:|---:|---:|---:|---:|---:|
| PRESENCE | 42 → 46 | 1 → 1 | 2 → 2 | 35 → 31 | 5 → 5 | 345 → 339 |
| FULL | 37 → 41 | 0 → 0 | 0 → 0 | 43 → 39 | 3 → 3 | 362 → 357 |
| ENSEMBLE_AB | 46 → 49 | 2 → 2 | 6 → 6 | 26 → 23 | 6 → 6 | 268 → 256 |
| ENSEMBLE_AE, diagnostic | 46 → 49 | 2 → 2 | 6 → 6 | 26 → 23 | 9 → 9 | 253 → 242 |

The per-slot comparison checks **identical wrong/new IDs, offsets, Google/truth/reader mark sets and outcomes in all four modes**, not just equal totals. Thus there are no held-out wrong/new transitions requiring a new error explanation. The unchanged unsafe slots and all changed error events are enumerated in [heldout_comparison.json](SF3_evidence/heldout_comparison.json); [slot_changes.jsonl.gz](SF3_evidence/slot_changes.jsonl.gz) retains every changed decision.

Newly corrected error slots are:

| Line | Recogniser NFD start / frozen slot | Google marks → print/reader marks | Modes gaining correction | Removed veto |
|---|---|---|---|---|
| `9c1dca9b-p000015-l0067` | 13 / 8 | acute → none | PRESENCE, FULL, AB | irrelevant top cut |
| `51fe7386-p000024-l0012` | 22 / 22 | acute → grave | all four | irrelevant top cut |
| `51fe7386-p000024-l0015` | 43 / 29 | dasia+acute → psili+acute | all four | irrelevant top cut |
| `384c3f89-p000142-l0003` | 11 / 12 | psili+grave → dasia+grave | PRESENCE, FULL, AE | closing quote retained by composer |

AB still holds the last row for A/B disagreement; AE still holds the first row for A/E disagreement.

### HOLD reasons after SF3

Counts below are reason incidences over serialized slots. Rows can overlap; K1 combines its individual receipts. Unsupported raw/NFD checks duplicate the same protected clusters and must not be added as distinct slots. Complete exact reason/index counts and line counts are in each phase's [reasons.json](SF3_evidence/heldout_after/reasons.json).

| Reason | PRESENCE | FULL | AB | AE | AB lines held for this family alone |
|---|---:|---:|---:|---:|---:|
| K1, all receipts | 260 | 260 | 260 | 260 | 9 |
| detector_clipped_top | 79 | 79 | 79 | 79 | 18 |
| detector_clipped_bottom | 131 | 131 | 131 | 131 | 67 |
| detector_segmentation_uncertain | 114 | 114 | 114 | 114 | 16 |
| detector_localisation_unknown | 44 | 44 | 44 | 44 | 0 |
| detector_unnamed_mark | 64 | 64 | 64 | 64 | 0 |
| detector mark-kind disagreement | 457 | — | — | — | — |
| detector exact mark-set disagreement | — | 498 | — | — | — |
| ensemble exact mark-set disagreement | — | — | 75 | 58 | 40 |
| edit_guard punctuation_mismatch | 37 | 37 | 37 | 37 | 1 |
| edit_guard unsupported_raw_character, all indices | 295 | 295 | 295 | 295 | 0 |
| edit_guard unsupported_character, all indices | 295 | 295 | 295 | 295 | 0 |
| A missing / unscored | 18 / 18 | 18 / 18 | 18 / 18 | 18 / 18 | 0 |
| Peer missing / unscored | — | — | 18 / 18 | 18 / 18 | 0 |
| A UNKNOWN / out-of-image uncertainty | 3 / 3 | 3 / 3 | 3 / 3 | 3 / 3 | 0 |
| Peer UNKNOWN / out-of-image uncertainty | — | — | 3 / 3 | 3 / 3 | 0 |

Top-cut incidences are **183 → 79**; bottom-cut incidences are **127 → 131**. Distinct slots with any clipping veto are **303 → 209**. Distinct slots with any edit-guard veto are **461 → 332**. These distinct-slot unions are the units used in the final result line. Lines held solely for top clipping change **28 → 18**; solely for bottom clipping **58 → 67**, because removing other vetoes exposes bottom clipping as the sole remaining reason.

The four added bottom-cut receipts are conservative relevance repairs, not false-absence releases:

| Line / recogniser NFD start | Base | Additional relevance evidence |
|---|---|---|
| `384c3f89-p000053-l0028` / 57 | ρ | peer subscript prediction; also held for AB disagreement |
| `384c3f89-p000142-l0007` / 47 | ρ | peer subscript prediction; also held for AB disagreement |
| `51fe7386-p000026-l0029` / 42 | υ | original recogniser subscript; also held for unsupported marks/K1 |
| `4ad622a4-p000043-l0019` / 1 | Ι | possible adscript after Α; kept-control slot now HOLD |

## Complete edit-guard character audit

All **15 failing lines** were examined across all four modes. Their proposals share A's names. There are **five punctuation-failure lines** and **ten unsupported-cluster lines**. The exact strings, NFD/raw index, Unicode name/codepoint of every offending character, and every punctuation edit are preserved in [baseline guard audit](SF3_evidence/heldout_before/guard_audit.jsonl), [after audit](SF3_evidence/heldout_after/guard_audit.jsonl) and [character inventory](SF3_evidence/character_inventory.json). Counts below count each actual offending cluster once, rather than repeating it for every held slot or raw/NFD guard receipt.

### Punctuation failures

| Line | Offending character / count | Classification and decision |
|---|---|---|
| `9c1dca9b-p000015-l0066` | `'` U+0027 × 1 before `φελᾷ` | composer bug: prefix elision was dropped; preserve it |
| `51fe7386-p000024-l0017` | `'` U+0027 × 1 before `ς` | composer bug: prefix elision was dropped; preserve it |
| `384c3f89-p000142-l0003` | `'` U+0027 × 1 after `.` | composer bug: closing quote was dropped; preserve it |
| `384c3f89-p000030-l0025` | `'` U+0027 × 1 after `.` | composer bug: closing quote was dropped; preserve it |
| `384c3f89-p000053-l0003` | combining acute U+0301 × 1 attached to a space before `Ἄ` | genuinely unsupported spacing/mark cluster; keep HOLD |

Totals: **four U+0027 deletions fixed, one U+0301 deletion still held**. The four repaired lines account for **129 slot-level punctuation vetoes** removed: **166 → 37**. No held-out guard was removed solely by the newly explicit quote/space codepoint equivalences. Those representation rules have their own positive and negative witness tests; they do not license deleting a mark or collapsing spaces.

### Unsupported clusters

| Original NFD cluster | Occurrences | Unsupported class | Decision |
|---|---:|---|---|
| `δ̔́` | 1 | breathing/accent on consonant | keep HOLD |
| `ᾶ̀` | 1 | two accents | keep HOLD |
| `δ̀` | 1 | accent on consonant | keep HOLD |
| `ἰ̔͂` | 1 | two breathings | keep HOLD |
| `ξ̀` | 1 | accent on consonant | keep HOLD |
| `ή͂` | 1 | two accents | keep HOLD |
| `ἵ͂` | 1 | two accents | keep HOLD |
| `ὐ̔͂` | 1 | two breathings | keep HOLD |
| `ῥͅ` | 1 | subscript on rho | keep HOLD |
| `ῦͅ` | 1 | subscript on upsilon | keep HOLD |

Character totals within these ten clusters:

| Character / Unicode | Count | Character / Unicode | Count |
|---|---:|---|---:|
| δ U+03B4 | 2 | α U+03B1 | 1 |
| ι U+03B9 | 2 | ξ U+03BE | 1 |
| η U+03B7 | 1 | υ U+03C5 | 2 |
| ρ U+03C1 | 1 | psili U+0313 | 2 |
| dasia U+0314 | 5 | acute U+0301 | 3 |
| grave U+0300 | 3 | perispomeni U+0342 | 6 |
| subscript U+0345 | 2 | | |

There are no macron or Latin-diacritic guard failures in this 666-line audit; their negative witnesses remain held. Unsupported-cluster holds are unchanged: **ten lines / 295 slot-level vetoes for each of the raw and NFD checks**. The brief's 99 and 66 are counts for particular indexed reasons (`…:1` and `…:4`), not the complete unsupported population. Every attempted unsupported-mark deletion remains blocked; no release was published and no original label was modified.

## M2: frozen development cards only

The read-only R0 split supplied **273 DEV cards / 12 sources**, with **43 literal printed→Google target pairs** and **212 marks-correct controls**. [DEV manifest](SF3_evidence/m2_dev_manifest.jsonl) and [split receipt](SF3_evidence/m2_split_receipt.json) are snapshotted. The replay filters the existing cache by these card IDs **before JSON-decoding a payload**. No locked stratum-(ii) card was composed or scored, and no locked truth/prediction file was opened for this replay. All 273 DEV records were accounted for. The earlier 473-card pooled M2 numbers are not reused as this denominator.

| Mode | Corrected / 43 | Wrong target pairs | Missed | HOLD errors | New control changes | Lines held / 273 |
|---|---:|---:|---:|---:|---:|---:|
| PRESENCE | 6 → 10 | 0 → 0 | 6 → 6 | 31 → 27 | 16 → 18 | 255 → 245 |
| FULL | 6 → 10 | 0 → 0 | 6 → 6 | 31 → 27 | 9 → 10 | 256 → 249 |
| ENSEMBLE_AB, missing peer evidence | 0 → 0 | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AE, missing peer evidence | 0 → 0 | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |

Six pairs remain unscorable because recogniser base letters do not map completely; none is an accepted wrong target pair. **B/E predictions and coverage do not exist in the saved M2 runtime.** The two ensemble rows therefore demonstrate the missing-peer HOLD path; they are not ensemble quality estimates. No peer was substituted and no inference was launched to fill the gap.

M2 “new” is the existing instrument's accepted changed-slot count on `marks:y` blind-reference controls, an upper bound rather than freshly adjudicated print errors. There are no removed control changes and exactly these additions:

| DEV card | Google NFD offset / recogniser start | Proposed change | Modes / count effect | Why now accepted |
|---|---|---|---|---|
| `t4c/gazette_poly1900/c018` | 18 / 18 | `ἐπόμενον` → `ἑπόμενον`: epsilon psili → dasia | PRESENCE +1, FULL +1 | saved local upper zone is clear of the crop top; previous veto was `detector_clipped_top` |
| `t4c/pleias_poly1850/c015` | 20 / 16 | `λωρίδες` → `λωρῖδες`: iota acute → circumflex | PRESENCE +1 | same top-cut relevance repair; FULL retains mark-set disagreement |

Both blind controls say their marks are correct. These are the coverage/precision tradeoff exposed by the requested relevance rule; their acceptance does not establish print correctness. The first breathing's handedness was already uncertain in the historical M2 spot-check. No threshold or exception was selected to hide these outcomes. [M2 comparison](SF3_evidence/m2_comparison.json) records each before/after slot, reasons and blind verdict; [before metrics](SF3_evidence/m2_dev_before/metrics.json), [after metrics](SF3_evidence/m2_dev_after/metrics.json) and their pair ledgers retain the full DEV instrument.

## Execution and verification

The immutable deployed directory `labelfix_l1_20261017/l1e_20261017/`, identified by the coordinator as job 3679545's source, was only read. Candidate code and outputs live separately at `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/sf3_relevance_20261017_final/`. Python bytecode writes were disabled. **325/325 deployed manifest files verified before and after**; no job was submitted, no allocation was changed, and no certificate was refreshed. No SSH retry was needed. Final-source replay elapsed time was **29.714 s before / 26.623 s after**, excluding SSH/copy time.

The measurement entry point is [`sf3_measure.py`](../../../../scripts/labelfix/sf3_measure.py). It verifies the L1E input hashes, extraction index, prediction/checkpoint receipts and observation recovery; it does not invoke L1E's mock/window/model paths. [Candidate source hashes](SF3_evidence/candidate_sources.sha256), [before receipt](SF3_evidence/heldout_before/measurement_receipt.json), [after receipt](SF3_evidence/heldout_after/measurement_receipt.json), [deployment checks before](SF3_evidence/deployment_before.log) and [after](SF3_evidence/deployment_after.log) bind the final run. The local and remote candidate hashes match.

```bash
# Clariden, separate candidate directory; deployed L1E directory remains read-only.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$SF3_ROOT" \
  /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python \
  scripts/labelfix/sf3_measure.py heldout --phase after \
  --deploy "$L1E_DEPLOY" --out "$NEW_OUTPUT"

# Mac: the frozen DEV allowlist is mandatory; use a fresh output directory.
PYTHONPATH="$PWD" /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
  scripts/labelfix/sf3_measure.py m2 --phase after \
  --dev-manifest docs/records/labelfix/spellcheck/SF3_evidence/m2_dev_manifest.jsonl \
  --cache .cache/labelfix/m2/runtime.jsonl --out "$NEW_OUTPUT"
```

Validation: baseline **380 passed**; final **450 passed**. The **70 new witnesses** include all unsupported audited clusters, relevant/irrelevant cuts, capital-side/local-x geometry, missing/invalid geometry, explicit UNSEEN, all subscript signals/adscript context, K1 line/slot/external/saved reasons, composer custody, quote/spacing aliases, forbidden punctuation edits and DEV-cache filtering before payload decode. Against the frozen L1E policy, **28 fail / 42 pass**; against SF3 all 70 pass. Existing test files/assertions are unchanged. See [baseline tests](SF3_evidence/tests_before.log), [L1E witness failures](SF3_evidence/witnesses_before.log), [final tests](SF3_evidence/tests_after.log) and [verification receipt](SF3_evidence/verification.json). `git diff --check` passes.

Agreement still measures stability of correlated readers. The training-wave precision caveat is unchanged; this held-out continuity result and the M2 DEV replay do not qualify a production training release.

SF3 RESULT: AB held-out lines held 268→256, corrected 46→49, wrong 2→2, new 6→6; PRESENCE 345→339; clipping holds 303→209; guard holds 461→332; tests 450 passed
