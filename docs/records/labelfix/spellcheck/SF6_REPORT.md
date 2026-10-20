# SF6 — two positive absence signals for Google-character deletion

Policy **`sf6-release-v1`**. The keraia witness is **HOLD**; **64/64 reviewer quote probes HOLD**. A release with an uncertified deletion becomes a whole-line HOLD. Insertions, SF5 text proposals, reader naming, agreement, observation predicates and K1 are unchanged.

**All-green acceptance is not met:** 1100 labelfix tests pass, with 1 environment setup error(s). The unchanged capture test cannot bind its loopback socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`). The SF5 baseline has the same setup error with 847 passes. No test is skipped, deselected or weakened to hide it. **census witnesses pending**.

Launch HEAD `f267dfaa` on `opus/spellcheck`; frozen production sources are read directly from `05f2dafb` and verified byte-identical to launch. Network OFF; Mac CPU; saved evidence only; detector/R1/CTC inference 0; no `.git` or other-worktree writes. The aborted first evidence directory was renamed to `SF6_evidence_aborted_run1/` and none of its files were reused.

## The one rule and the evidence contract

Every removed or replaced NFD character is checked at its original letter boundary. Canonical Unicode equivalence is unchanged. SF5 word-final elision aliases remain one atom, including next to real mark edits; other replacements count as deletions. Repeated signs keep their multiplicity. A spacing breathing attached as a combining mark still deletes the old spacing character, so SF6 can HOLD an otherwise valid SF5 atomic proposal.

Combining/spacing marks require **reader AND detector**, or **reader AND recogniser text**. The coordinator’s **A∧B counts as one reader** in every mode, including PRESENCE/FULL; AE also retains its E check. Agreement is not independent print evidence. Apostrophes, quotes and numeral keraia require **detector AND recogniser text**; R1 supplies no punctuation absence signal. Other characters require a supported reader absence and a second source; no such reader head exists in the retained evidence, so these deletions HOLD.

A reader absence needs a supported head, saved predictions from both A and B, scored coverage with a finite in-image span, a known evidence state, an empty uncertainty list, and no applicable slot/observation veto. Missing or conflicting B is not a reader absence, even if A and the detector agree. Detector absence needs an actually scored head, explicit `OBSERVED` coverage of the relevant region, a valid window, resolved localisation and segmentation, no unnamed or uncertain ink and no relevant clipping. Empty candidate lists without that evidence are UNKNOWN. The current apostrophe detector only scores word-final δ/τ/ρ/θ/π; an empty Ι, κ or μ slot is not a negative punctuation observation. Quote absence additionally needs the leading-left region observed. Keraia has no scored absence head in these saved records.

Recogniser-text absence needs aligned letter context, a finite saved `recognition_confidence` in [0,1], a located in-image span, and no applicable uncertainty/clipping. An unscored string is not a positive absence. Its score is now included in the content-bound evidence envelope because SF6 consumes it. No missing confidence, coverage or observation state is filled in. This is evidence plumbing for the deletion rule, not a new source decision.

Production changes: `release_gate.py` adds the deletion inventory/guard, policy id and score binding; `l1_common.overlay` records each decision and adds the whole-line HOLD before release. Existing composer functions and the SF5 text policy are byte/AST unchanged. All no-HOLD outputs retain their exact SF5 label and status. The verification checks this worktree and branch’s Git metadata separately from the shared common directory: concurrent other-worktree/branch changes and `info/refs` drift are recorded explicitly, not reported as globally unchanged. [Verification receipt](SF6_evidence/verification.json).

## Held-out 666 — SF5 → SF6

The original instrument has 80 Google combining-mark errors, 10,046 known and 300 unknown-truth mapped/scored slots per mode. Frozen slot decisions remain identical (81,700 records). The table applies only SF6’s additional whole-line veto to those original slot scores; a failing deletion can therefore HOLD other slots on that same line. These are scores with the new release veto applied, not newly inferred reader scores. The original SF5 slot rows are the left side of each arrow. Existing SF5 line vetoes are not retroactively added to that historical slot instrument.

The local 666-line artifact lacks full extraction coverage. Its certified frozen decisions are retained, but unavailable raw coverage is never used as positive reader absence. This is a saved-decision replay, not full runtime recomposition. Before applying SF6, all 2,664 SF5 effective line labels and statuses reproduce exactly.

| Mode | Row | Corrected /80, elision K/D/A or deleted characters | Wrong | Missed | HOLD errors | New | Instrument lines held /666 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | mark | 42 → 10 | 1 → 0 | 2 → 2 | 35 → 68 | 5 → 0 | 348 → 383 |
| PRESENCE | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| PRESENCE | deletion mark/apostrophe/quote/keraia/other | 22/0/1/0/0 → 0/0/0/0/0 | — | — | — | — | new HOLD 17/0/1/0/0 |
| FULL | mark | 37 → 8 | 0 → 0 | 0 → 0 | 43 → 72 | 3 → 0 | 365 → 391 |
| FULL | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| FULL | deletion mark/apostrophe/quote/keraia/other | 11/0/1/0/0 → 0/0/0/0/0 | — | — | — | — | new HOLD 9/0/1/0/0 |
| ENSEMBLE_AB | mark | 45 → 11 | 2 → 0 | 6 → 6 | 27 → 63 | 6 → 1 | 274 → 325 |
| ENSEMBLE_AB | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| ENSEMBLE_AB | deletion mark/apostrophe/quote/keraia/other | 34/0/2/0/0 → 0/0/0/0/0 | — | — | — | — | new HOLD 27/0/2/0/0 |
| ENSEMBLE_AE | mark | 46 → 10 | 2 → 0 | 6 → 6 | 26 → 64 | 9 → 6 | 261 → 317 |
| ENSEMBLE_AE | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| ENSEMBLE_AE | deletion mark/apostrophe/quote/keraia/other | 33/0/3/0/0 → 0/0/0/0/0 | — | — | — | — | new HOLD 26/0/3/0/0 |

The deletion row counts Google NFD characters removed from **released** labels, by source character class; it is not print-truth scoring. New HOLD vectors count lines, and classes can overlap. The elision row scores effective labels, retaining original Google on HOLD. Print truth covers 213 printed elisions and 5 certified absent sites on 180/666 lines, with 0 complete lines certified: pixel-adjudicated Wikisource text when supported by R0, otherwise the R0 adjudication. Ten quote scopes and one unresolved scope are excluded. The exact coverage and source counts are preserved in [held-out metrics](SF6_evidence/heldout/metrics.json).

Actual whole-line release statuses, including the original Google guards:

| Mode | Corrected lines | Unchanged lines | Held lines |
| --- | --- | --- | --- |
| PRESENCE | 24 → 6 | 276 → 276 | 366 → 384 |
| FULL | 15 → 5 | 269 → 269 | 382 → 392 |
| ENSEMBLE_AB | 35 → 6 | 333 → 333 | 298 → 327 |
| ENSEMBLE_AE | 38 → 9 | 338 → 338 | 290 → 319 |

Every changed mark outcome is listed below. The source parts and physical records did not change; only the SF6 whole-line veto changed the score. [Full per-slot events, including reasons](SF6_evidence/heldout/per_slot_changes.jsonl), [original slot identity proof](SF6_evidence/heldout/per_slot_proof.jsonl.gz), [line proposals, labels and absence checks](SF6_evidence/heldout/release_labels.jsonl.gz).

| Line ID | Mode | Physical slot / recogniser start | SF5 → SF6 |
| --- | --- | --- | --- |
| 9c1dca9b-p000015-l0062 | PRESENCE | 20 / 25 | corrected → HOLD |
| 9c1dca9b-p000015-l0062 | FULL | 20 / 25 | corrected → HOLD |
| 9c1dca9b-p000015-l0062 | ENSEMBLE_AB | 20 / 25 | corrected → HOLD |
| 9c1dca9b-p000015-l0062 | ENSEMBLE_AE | 20 / 25 | corrected → HOLD |
| 9c1dca9b-p000015-l0065 | PRESENCE | 8 / 10 | corrected → HOLD |
| 9c1dca9b-p000015-l0065 | FULL | 8 / 10 | corrected → HOLD |
| 9c1dca9b-p000015-l0065 | ENSEMBLE_AB | 8 / 10 | corrected → HOLD |
| 9c1dca9b-p000015-l0065 | ENSEMBLE_AE | 8 / 10 | corrected → HOLD |
| 602cc72e-p000353-l0006 | PRESENCE | 6 / 5 | corrected → HOLD |
| 602cc72e-p000353-l0006 | FULL | 6 / 5 | corrected → HOLD |
| 602cc72e-p000353-l0006 | ENSEMBLE_AB | 6 / 5 | corrected → HOLD |
| 602cc72e-p000353-l0006 | ENSEMBLE_AE | 6 / 5 | corrected → HOLD |
| 177b717d-p000097-l0007 | PRESENCE | 1 / 0 | corrected → HOLD |
| 177b717d-p000097-l0007 | FULL | 1 / 0 | corrected → HOLD |
| 177b717d-p000097-l0007 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 177b717d-p000097-l0007 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 602cc72e-p000167-l0027 | ENSEMBLE_AB | 14 / 18 | wrong → HOLD |
| 602cc72e-p000167-l0027 | ENSEMBLE_AE | 14 / 18 | wrong → HOLD |
| 177b717d-p000013-l0009 | PRESENCE | 1 / 0 | corrected → HOLD |
| 177b717d-p000013-l0009 | FULL | 1 / 0 | corrected → HOLD |
| 177b717d-p000013-l0009 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 177b717d-p000013-l0009 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 177b717d-p000067-l0009 | ENSEMBLE_AB | 27 / 34 | corrected → HOLD |
| 177b717d-p000067-l0009 | ENSEMBLE_AE | 27 / 34 | corrected → HOLD |
| 384c3f89-p000096-l0005 | PRESENCE | 4 / 4 | corrected → HOLD |
| 384c3f89-p000096-l0005 | FULL | 4 / 4 | corrected → HOLD |
| 384c3f89-p000096-l0005 | ENSEMBLE_AB | 4 / 4 | corrected → HOLD |
| 384c3f89-p000096-l0005 | ENSEMBLE_AE | 4 / 4 | corrected → HOLD |
| 177b717d-p000097-l0010 | PRESENCE | 2 / 1 | corrected → HOLD |
| 177b717d-p000097-l0010 | FULL | 2 / 1 | corrected → HOLD |
| 177b717d-p000097-l0010 | ENSEMBLE_AB | 2 / 1 | corrected → HOLD |
| 177b717d-p000097-l0010 | ENSEMBLE_AE | 2 / 1 | corrected → HOLD |
| 384c3f89-p000096-l0004 | ENSEMBLE_AB | 15 / 20 | wrong → HOLD |
| 51fe7386-p000026-l0016 | ENSEMBLE_AB | 5 / 5 | corrected → HOLD |
| 51fe7386-p000026-l0016 | ENSEMBLE_AE | 5 / 5 | corrected → HOLD |
| 384c3f89-p000068-l0036 | PRESENCE | 2 / 1 | corrected → HOLD |
| 384c3f89-p000068-l0036 | FULL | 2 / 1 | corrected → HOLD |
| 384c3f89-p000068-l0036 | ENSEMBLE_AB | 2 / 1 | corrected → HOLD |
| 384c3f89-p000068-l0036 | ENSEMBLE_AE | 2 / 1 | corrected → HOLD |
| 384c3f89-p000096-l0010 | PRESENCE | 3 / 1 | corrected → HOLD |
| 384c3f89-p000096-l0010 | FULL | 3 / 1 | corrected → HOLD |
| 384c3f89-p000096-l0010 | ENSEMBLE_AB | 3 / 1 | corrected → HOLD |
| 384c3f89-p000096-l0010 | ENSEMBLE_AE | 3 / 1 | corrected → HOLD |
| 384c3f89-p000091-l0017 | PRESENCE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000091-l0017 | FULL | 1 / 0 | corrected → HOLD |
| 384c3f89-p000091-l0017 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 384c3f89-p000091-l0017 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000068-l0033 | ENSEMBLE_AB | 2 / 1 | corrected → HOLD |
| 384c3f89-p000068-l0033 | ENSEMBLE_AE | 2 / 1 | corrected → HOLD |
| 384c3f89-p000050-l0041 | PRESENCE | 11 / 12 | corrected → HOLD |
| 384c3f89-p000050-l0041 | FULL | 11 / 12 | corrected → HOLD |
| 384c3f89-p000050-l0041 | ENSEMBLE_AB | 11 / 12 | corrected → HOLD |
| 384c3f89-p000050-l0041 | ENSEMBLE_AE | 11 / 12 | corrected → HOLD |
| 384c3f89-p000142-l0003 | PRESENCE | 12 / 11 | corrected → HOLD |
| 384c3f89-p000142-l0003 | FULL | 12 / 11 | corrected → HOLD |
| 384c3f89-p000142-l0003 | ENSEMBLE_AE | 12 / 11 | corrected → HOLD |
| 384c3f89-p000091-l0039 | ENSEMBLE_AB | 29 / 44 | corrected → HOLD |
| 384c3f89-p000091-l0039 | ENSEMBLE_AE | 29 / 44 | corrected → HOLD |
| 384c3f89-p000053-l0004 | PRESENCE | 14 / 20 | corrected → HOLD |
| 384c3f89-p000053-l0004 | FULL | 14 / 20 | corrected → HOLD |
| 384c3f89-p000182-l0016 | PRESENCE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000182-l0016 | FULL | 1 / 0 | corrected → HOLD |
| 384c3f89-p000182-l0016 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 384c3f89-p000182-l0016 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000183-l0029 | PRESENCE | 2 / 1 | corrected → HOLD |
| 384c3f89-p000183-l0029 | FULL | 2 / 1 | corrected → HOLD |
| 384c3f89-p000183-l0029 | ENSEMBLE_AB | 2 / 1 | corrected → HOLD |
| 384c3f89-p000183-l0029 | ENSEMBLE_AE | 2 / 1 | corrected → HOLD |
| 384c3f89-p000205-l0011 | PRESENCE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000205-l0011 | FULL | 1 / 0 | corrected → HOLD |
| 384c3f89-p000205-l0011 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 384c3f89-p000205-l0011 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000050-l0027 | PRESENCE | 3 / 3 | corrected → HOLD |
| 384c3f89-p000050-l0027 | FULL | 3 / 3 | corrected → HOLD |
| 384c3f89-p000050-l0027 | ENSEMBLE_AB | 3 / 3 | corrected → HOLD |
| 384c3f89-p000050-l0027 | ENSEMBLE_AE | 3 / 3 | corrected → HOLD |
| 51fe7386-p000024-l0016 | PRESENCE | 31 / 40 | corrected → HOLD |
| 51fe7386-p000024-l0016 | FULL | 31 / 40 | corrected → HOLD |
| 51fe7386-p000024-l0016 | ENSEMBLE_AB | 31 / 40 | corrected → HOLD |
| 51fe7386-p000024-l0016 | ENSEMBLE_AE | 31 / 40 | corrected → HOLD |
| 384c3f89-p000096-l0031 | PRESENCE | 22 / 34 | corrected → HOLD |
| 384c3f89-p000096-l0031 | FULL | 22 / 34 | corrected → HOLD |
| 384c3f89-p000096-l0031 | ENSEMBLE_AB | 22 / 34 | corrected → HOLD |
| 384c3f89-p000096-l0031 | ENSEMBLE_AE | 22 / 34 | corrected → HOLD |
| 384c3f89-p000059-l0023 | PRESENCE | 15 / 24 | corrected → HOLD |
| 384c3f89-p000059-l0023 | FULL | 15 / 24 | corrected → HOLD |
| 384c3f89-p000059-l0023 | ENSEMBLE_AB | 15 / 24 | corrected → HOLD |
| 384c3f89-p000059-l0023 | ENSEMBLE_AE | 15 / 24 | corrected → HOLD |
| 384c3f89-p000053-l0028 | PRESENCE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000053-l0028 | FULL | 1 / 0 | corrected → HOLD |
| 384c3f89-p000053-l0028 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 384c3f89-p000053-l0028 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000030-l0010 | PRESENCE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000030-l0010 | FULL | 1 / 0 | corrected → HOLD |
| 384c3f89-p000030-l0010 | ENSEMBLE_AB | 1 / 0 | corrected → HOLD |
| 384c3f89-p000030-l0010 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000205-l0005 | ENSEMBLE_AE | 1 / 0 | corrected → HOLD |
| 384c3f89-p000182-l0027 | PRESENCE | 8 / 12 | corrected → HOLD |
| 384c3f89-p000182-l0027 | PRESENCE | 28 / 42 | corrected → HOLD |
| 384c3f89-p000182-l0027 | FULL | 8 / 12 | corrected → HOLD |
| 384c3f89-p000182-l0027 | ENSEMBLE_AB | 8 / 12 | corrected → HOLD |
| 384c3f89-p000182-l0027 | ENSEMBLE_AB | 28 / 42 | corrected → HOLD |
| 384c3f89-p000182-l0027 | ENSEMBLE_AE | 28 / 42 | corrected → HOLD |
| 384c3f89-p000182-l0031 | PRESENCE | 8 / 11 | corrected → HOLD |
| 384c3f89-p000182-l0031 | ENSEMBLE_AB | 8 / 11 | corrected → HOLD |
| 384c3f89-p000182-l0031 | ENSEMBLE_AE | 8 / 11 | corrected → HOLD |
| 51fe7386-p000024-l0020 | PRESENCE | 39 / 51 | corrected → HOLD |
| 51fe7386-p000024-l0020 | FULL | 39 / 51 | corrected → HOLD |
| 51fe7386-p000024-l0020 | ENSEMBLE_AB | 39 / 51 | corrected → HOLD |
| 51fe7386-p000024-l0020 | ENSEMBLE_AE | 39 / 51 | corrected → HOLD |
| 177b717d-p000017-l0012 | PRESENCE | 34 / 49 | corrected → HOLD |
| 177b717d-p000017-l0012 | FULL | 34 / 49 | corrected → HOLD |
| 177b717d-p000017-l0012 | ENSEMBLE_AB | 34 / 49 | corrected → HOLD |
| 177b717d-p000017-l0012 | ENSEMBLE_AE | 34 / 49 | corrected → HOLD |
| 384c3f89-p000142-l0030 | PRESENCE | 30 / 35 | corrected → HOLD |
| 384c3f89-p000142-l0030 | FULL | 30 / 35 | corrected → HOLD |
| 384c3f89-p000142-l0030 | ENSEMBLE_AB | 30 / 35 | corrected → HOLD |
| 384c3f89-p000142-l0030 | ENSEMBLE_AE | 30 / 35 | corrected → HOLD |
| 384c3f89-p000059-l0027 | PRESENCE | 1 / 0 | wrong → HOLD |
| 384c3f89-p000059-l0027 | ENSEMBLE_AE | 1 / 0 | wrong → HOLD |
| 384c3f89-p000121-l0023 | PRESENCE | 28 / 36 | corrected → HOLD |
| 384c3f89-p000121-l0023 | FULL | 28 / 36 | corrected → HOLD |
| 384c3f89-p000121-l0023 | ENSEMBLE_AB | 28 / 36 | corrected → HOLD |
| 384c3f89-p000121-l0023 | ENSEMBLE_AE | 28 / 36 | corrected → HOLD |
| 384c3f89-p000030-l0021 | PRESENCE | 39 / 52 | corrected → HOLD |
| 384c3f89-p000030-l0021 | ENSEMBLE_AB | 39 / 52 | corrected → HOLD |
| 384c3f89-p000030-l0021 | ENSEMBLE_AE | 39 / 52 | corrected → HOLD |
| 9c1dca9b-p000005-l0017 | PRESENCE | 23 / 28 | corrected → HOLD |
| 9c1dca9b-p000005-l0017 | FULL | 23 / 28 | corrected → HOLD |
| 9c1dca9b-p000005-l0017 | ENSEMBLE_AB | 10 / 12 | corrected → HOLD |
| 9c1dca9b-p000005-l0017 | ENSEMBLE_AB | 23 / 28 | corrected → HOLD |
| 9c1dca9b-p000005-l0017 | ENSEMBLE_AE | 10 / 12 | corrected → HOLD |
| 9c1dca9b-p000005-l0017 | ENSEMBLE_AE | 23 / 28 | corrected → HOLD |
| 384c3f89-p000091-l0014 | PRESENCE | 10 / 13 | corrected → HOLD |
| 384c3f89-p000091-l0014 | FULL | 10 / 13 | corrected → HOLD |
| 384c3f89-p000091-l0014 | ENSEMBLE_AE | 10 / 13 | corrected → HOLD |

## M2 DEV — SF5 → SF6

Only the 273-card DEV allowlist is decoded from the cache; 0 locked stratum (ii) records are decoded or composed. There are 43 enumerated Google mark-error pairs and 212 marks-correct reference cards. B/E are missing in this cache; ensemble HOLDs remain. Complete saved runtime is replayed. Original slot decisions remain identical; the table adds only SF6’s whole-line veto, even on lines that already had a different SF5 line HOLD. That explains why slot scores can decrease while the final release counts stay unchanged.

| Mode | Row | Corrected /43, elision K/D/A or deleted characters | Missed | HOLD errors | Changed control slots | Instrument lines held /273 |
| --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | mark | 7 → 2 | 6 → 6 | 30 → 35 | 16 → 0 | 257 → 260 |
| PRESENCE | elision kept/deleted/added | UNKNOWN → UNKNOWN (0 certified scopes) | — | — | — | — |
| PRESENCE | deletion mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | new HOLD 0/0/0/0/0 |
| FULL | mark | 7 → 2 | 6 → 6 | 30 → 35 | 9 → 0 | 258 → 261 |
| FULL | elision kept/deleted/added | UNKNOWN → UNKNOWN (0 certified scopes) | — | — | — | — |
| FULL | deletion mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | new HOLD 0/0/0/0/0 |
| ENSEMBLE_AB | mark | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AB | elision kept/deleted/added | UNKNOWN → UNKNOWN (0 certified scopes) | — | — | — | — |
| ENSEMBLE_AB | deletion mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | new HOLD 0/0/0/0/0 |
| ENSEMBLE_AE | mark | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AE | elision kept/deleted/added | UNKNOWN → UNKNOWN (0 certified scopes) | — | — | — | — |
| ENSEMBLE_AE | deletion mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | new HOLD 0/0/0/0/0 |

DEV elision truth is UNKNOWN: 0 certified positive or negative sites, 0/273 lines with punctuation truth, human fields all null. No elision-accuracy claim is made. [DEV metrics](SF6_evidence/m2_dev/metrics.json), [allowlist/input receipt](SF6_evidence/m2_dev/receipt.json).

| Mode | Corrected lines | Unchanged lines | Held lines |
| --- | --- | --- | --- |
| PRESENCE | 0 → 0 | 13 → 13 | 260 → 260 |
| FULL | 0 → 0 | 12 → 12 | 261 → 261 |
| ENSEMBLE_AB | 0 → 0 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AE | 0 → 0 | 0 → 0 | 273 → 273 |

Changed DEV mark-pair outcomes, by mapped slot group (all are the new whole-line veto):

| Card | Mode | Google NFD letter offsets | SF5 → SF6 |
| --- | --- | --- | --- |
| t4c/bsb_poly1850/c013 | PRESENCE | [45, 46, 47, 48, 49, 50, 51, 52, 53, 54] | corrected → HOLD |
| t4c/bsb_poly1850/c013 | FULL | [45, 46, 47, 48, 49, 50, 51, 52, 53, 54] | corrected → HOLD |
| t4c/bsb_poly1850/c033 | PRESENCE | [74, 75, 76, 78, 79] | corrected → HOLD |
| t4c/bsb_poly1850/c033 | FULL | [74, 75, 76, 78, 79] | corrected → HOLD |
| t4c/oa_poly1900/c006 | PRESENCE | [32, 33, 34, 35, 36] | corrected → HOLD |
| t4c/oa_poly1900/c006 | FULL | [32, 33, 34, 35, 36] | corrected → HOLD |
| t4c/pleias_poly1850/c037 | PRESENCE | [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12] | corrected → HOLD |
| t4c/pleias_poly1850/c037 | FULL | [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12] | corrected → HOLD |
| c0/ia_greek_latin/c004 | PRESENCE | [57, 59, 60] | corrected → HOLD |
| c0/ia_greek_latin/c004 | FULL | [57, 59, 60] | corrected → HOLD |

The complete per-slot control changes are linked separately: [DEV per-slot changes](SF6_evidence/m2_dev/control_slot_changes.jsonl).

## Punctuation-deletion HOLDs by class

Each cell is **newly held / all held with an uncertified attempted deletion**. The latter includes lines already held under SF5. Counts are lines per mode/cohort; classes can overlap. Punctuation uses detector AND recogniser text throughout, never R1 A+B.

| Cohort | Mode | Apostrophe | Quote | Keraia | Distinct punctuation lines |
| --- | --- | --- | --- | --- | --- |
| held-out | PRESENCE | 0 / 4 | 1 / 6 | 0 / 0 | 1 / 10 |
| held-out | FULL | 0 / 4 | 1 / 6 | 0 / 0 | 1 / 10 |
| held-out | ENSEMBLE_AB | 0 / 4 | 2 / 6 | 0 / 0 | 2 / 10 |
| held-out | ENSEMBLE_AE | 0 / 4 | 3 / 6 | 0 / 0 | 3 / 10 |
| M2 DEV | PRESENCE | 0 / 2 | 0 / 2 | 0 / 1 | 0 / 5 |
| M2 DEV | FULL | 0 / 2 | 0 / 2 | 0 / 1 | 0 / 5 |
| M2 DEV | ENSEMBLE_AB | 0 / 2 | 0 / 2 | 0 / 1 | 0 / 5 |
| M2 DEV | ENSEMBLE_AE | 0 / 2 | 0 / 2 | 0 / 1 | 0 / 5 |
| l1a | ENSEMBLE_AB | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| quote_probe | PRESENCE | 0 / 0 | 16 / 16 | 0 / 0 | 16 / 16 |
| quote_probe | FULL | 0 / 0 | 16 / 16 | 0 / 0 | 16 / 16 |
| quote_probe | ENSEMBLE_AB | 0 / 0 | 16 / 16 | 0 / 0 | 16 / 16 |
| quote_probe | ENSEMBLE_AE | 0 / 0 | 16 / 16 | 0 / 0 | 16 / 16 |
| sf5 | ENSEMBLE_AB | 2 / 2 | 0 / 0 | 1 / 1 | 3 / 3 |

Across all measured released SF5 line/mode identities, deduplicating overlapping witness cohorts: **8 single-certified-source deletions released → 0**; **74 newly held punctuation line/mode identities** (apostrophe 2, quote 71, keraia 1). This includes all four held-out/DEV modes and all 64 synthetic reviewer probes; it is not a full-production prevalence estimate. Missing-evidence deletions are also held and are counted separately from single-certified-source cases in the machine-readable metrics.

## SF5 and L1A regression witnesses

All 56 SF5 witnesses and all 48 L1A audit lines are listed individually. Ten SF5 lines and seven L1A lines change from release to HOLD; every other label/status is exact SF5 parity. Cohorts overlap on the six original L1A defect witnesses. Both known reader naming errors now HOLD: their saved wrong mark predictions remain unchanged. The two spacing-breathing proposals also HOLD because attachment replaces Google’s spacing character and the reader does not say that breathing is absent. [Full original/recogniser/before/after labels and source checks](SF6_evidence/witness_results.jsonl.gz), [source custody and all 48 L1A slot-parity checks](SF6_evidence/witness_inputs_receipt.json).

### 56 SF5 lines

| Line ID | SF5 | SF6 | Deleted characters requiring HOLD |
| --- | --- | --- | --- |
| 32aae9fec147d3b483deb96e-p000076-l0012 | unchanged | unchanged | — |
| 650670ab271096716888b108-p000033-l0054 | unchanged | unchanged | — |
| 5a69150abb15eb1006f5a3ba-p000947-l0013 | unchanged | unchanged | — |
| a300f5e1c3f6a38d97201791-p000054-l0115 | unchanged | unchanged | — |
| 650670ab271096716888b108-p000006-l0047 | unchanged | unchanged | — |
| fdbb6015b076a41fcf67486b-p000020-l0067 | unchanged | unchanged | — |
| 32aae9fec147d3b483deb96e-p000035-l0070 | unchanged | unchanged | — |
| 2c8742589d947f8d749c7ba2-p000040-l0014 | unchanged | unchanged | — |
| 0bff55647d1c2acd1caa8bf3-p000231-l0006 | unchanged | unchanged | — |
| 0b2cede5e125323a082f684b-p000015-l0028 | unchanged | unchanged | — |
| d9d705c23499ff012aa70783-p000031-l0058 | unchanged | unchanged | — |
| 2c8742589d947f8d749c7ba2-p000022-l0057 | unchanged | unchanged | — |
| b5f8ce187b707837e5669281-p000038-l0033 | unchanged | unchanged | — |
| 5be5bc5b3ea6-p000001-l0002 | unchanged | unchanged | — |
| c57e3067ed37cedf17f285e6-p000049-l0021 | unchanged | unchanged | — |
| dc390fceb64d9bb60a12d6b8-p000118-l0005 | unchanged | unchanged | — |
| a300f5e1c3f6a38d97201791-p000442-l0085 | corrected | hold | U+0027 keraia |
| bf2ce6d100950eec319cef00-p000010-l0059 | unchanged | unchanged | — |
| e988c46677e75b38c15117fc-p000063-l0015 | unchanged | unchanged | — |
| 92ab1a099d56dc9022fc4778-p000032-l0025 | unchanged | unchanged | — |
| 39fbbdfd2c8030f211a318b7-p000063-l0005 | unchanged | unchanged | — |
| bb8faba1e9b543fe5a1ce6dd-p000017-l0012 | unchanged | unchanged | — |
| b5f8ce187b707837e5669281-p000038-l0060 | unchanged | unchanged | — |
| d9d705c23499ff012aa70783-p000006-l0049 | unchanged | unchanged | — |
| 1092c25534f45a95669f3d2b-p000041-l0003 | unchanged | unchanged | — |
| 95a8decfdafb3b75d6549383-p000031-l0010 | unchanged | unchanged | — |
| 5a69150abb15eb1006f5a3ba-p000947-l0007 | unchanged | unchanged | — |
| 453f156dc6352286456a08cb-p000100-l0002 | corrected | hold | U+1FBF apostrophe |
| 3ae256de8a055af974b9ec8f-p000144-l0026 | unchanged | unchanged | — |
| d9d705c23499ff012aa70783-p000036-l0027 | unchanged | unchanged | — |
| 143e78b5de2e6e784534ee0d-p000061-l0032 | corrected | hold | U+0301 mark |
| 80f0c63471e19f7383fa6f66-p000057-l0016 | unchanged | unchanged | — |
| bf2ce6d100950eec319cef00-p000028-l0081 | unchanged | unchanged | — |
| b518f9f9b73fe9a3257fe2f0-p000041-l0022 | corrected | hold | U+1FBF apostrophe |
| fdcac2103d02191960287381-p000010-l0019 | unchanged | unchanged | — |
| cc0e056392dd2ef4916b3e7d-p000095-l0027 | unchanged | unchanged | — |
| 4c949ab8ae19e68be5a06c43-p000047-l0010 | unchanged | unchanged | — |
| 42c339ce492d83665f00774d-p000049-l0055 | unchanged | unchanged | — |
| 043b454a8c255b6690fd3777-p000054-l0053 | unchanged | unchanged | — |
| bf2ce6d100950eec319cef00-p000020-l0020 | unchanged | unchanged | — |
| d9d705c23499ff012aa70783-p000041-l0008 | unchanged | unchanged | — |
| 916a006055a9d43fdaa4c41b-p000067-l0016 | unchanged | unchanged | — |
| 13dcc39a-p000003-l0088 | unchanged | unchanged | — |
| c20219eff76f2fbc39f4c6fd-p000030-l0038 | unchanged | unchanged | — |
| 137e9af6a0045d5746e26efa-p000008-l0008 | corrected | hold | U+0313 mark |
| 60b9798cc3e6f9f631070765-p000017-l0001 | unchanged | unchanged | — |
| b4bb45a610fbcbc974b0eb32-p000019-l0016 | unchanged | unchanged | — |
| 8961f6bdd6daf004b4a84dfa-p000025-l0051 | corrected | hold | U+0300 mark |
| bd99a3200cffaf6bf4d7c23a-p000040-l0009 | unchanged | unchanged | — |
| 6c0a582885e55adc7c535c48-p000136-l0043 | unchanged | unchanged | — |
| 00c322b3ee04b419d1979f22-p000115-l0022 | corrected | hold | U+0313 mark |
| 399d224c580127635c47cd8d-p000019-l0010 | unchanged | unchanged | — |
| 32aae9fec147d3b483deb96e-p000052-l0026 | unchanged | unchanged | — |
| 827d2345ad77e5cdec320e80-p000028-l0019 | corrected | hold | U+0345 mark |
| a963b33d02c23d4127f5ec26-p000012-l0029 | corrected | hold | U+1FBF mark |
| 32aae9fec147d3b483deb96e-p000060-l0057 | corrected | hold | U+1FBF mark |

### 48 L1A audit lines

| Line ID | SF5 | SF6 | Deleted characters requiring HOLD |
| --- | --- | --- | --- |
| ef3cad078cfd452259f5b836-p000028-l0019 | unchanged | unchanged | — |
| f77a8c0084022edb7981fb15-p000017-l0028 | unchanged | unchanged | — |
| fdbb6015b076a41fcf67486b-p000031-l0024 | unchanged | unchanged | — |
| 3cb3c1caf7324ded3b11c1e5-p000034-l0043 | corrected | hold | U+0301 mark |
| fdbb6015b076a41fcf67486b-p000035-l0063 | unchanged | unchanged | — |
| 3cb3c1caf7324ded3b11c1e5-p000034-l0022 | unchanged | unchanged | — |
| 99c8dbb018ec2c87af3fdce9-p000025-l0024 | unchanged | unchanged | — |
| 8961f6bdd6daf004b4a84dfa-p000092-l0012 | corrected | hold | U+0301 mark |
| 60b9798cc3e6f9f631070765-p000027-l0033 | unchanged | unchanged | — |
| 7cb612112b4f28a4f704a9cb-p000075-l0032 | unchanged | unchanged | — |
| b08a5423fb059fbb291900aa-p000107-l0076 | corrected | corrected | — |
| c20219eff76f2fbc39f4c6fd-p000016-l0049 | unchanged | unchanged | — |
| 2d29e5e76d90adc4cc1b093a-p000023-l0035 | unchanged | unchanged | — |
| 00c322b3ee04b419d1979f22-p000115-l0022 | corrected | hold | U+0313 mark |
| 8b231047fdbd96ec30e1eded-p000038-l0018 | unchanged | unchanged | — |
| 99c8dbb018ec2c87af3fdce9-p000054-l0028 | unchanged | unchanged | — |
| 3cb3c1caf7324ded3b11c1e5-p000024-l0014 | unchanged | unchanged | — |
| 290a133b0e55593eb4ecdcfd-p000098-l0050 | unchanged | unchanged | — |
| 399d224c580127635c47cd8d-p000019-l0010 | unchanged | unchanged | — |
| 32aae9fec147d3b483deb96e-p000052-l0026 | unchanged | unchanged | — |
| c3468c02b6d929362f6e3fe7-p000082-l0019 | unchanged | unchanged | — |
| 5a69150abb15eb1006f5a3ba-p000514-l0046 | unchanged | unchanged | — |
| adc48c3e94eb469347d7cb4a-p000233-l0006 | unchanged | unchanged | — |
| 32aae9fec147d3b483deb96e-p000011-l0018 | unchanged | unchanged | — |
| 827d2345ad77e5cdec320e80-p000059-l0023 | unchanged | unchanged | — |
| 39fbbdfd2c8030f211a318b7-p000053-l0015 | unchanged | unchanged | — |
| 827d2345ad77e5cdec320e80-p000028-l0019 | corrected | hold | U+0345 mark |
| 0efd675a10c9a91816c7a41a-p000186-l0025 | unchanged | unchanged | — |
| b518f9f9b73fe9a3257fe2f0-p000171-l0026 | unchanged | unchanged | — |
| 6c0a582885e55adc7c535c48-p000029-l0018 | unchanged | unchanged | — |
| a963b33d02c23d4127f5ec26-p000012-l0029 | corrected | hold | U+1FBF mark |
| 5a69150abb15eb1006f5a3ba-p000660-l0013 | corrected | hold | U+0300 mark |
| 32aae9fec147d3b483deb96e-p000060-l0057 | corrected | hold | U+1FBF mark |
| c8654864d161aa7fc41f65cb-p000226-l0020 | unchanged | unchanged | — |
| 5165f9e7fe1f3d7053f5adcf-p000003-l0049 | unchanged | unchanged | — |
| d0eda948e5b1f3632f8687fb-p000773-l0032 | unchanged | unchanged | — |
| e32f8d6932bd505c2a0b1c8e-p000012-l0007 | unchanged | unchanged | — |
| 8a482dd5cb341a70d157d5c4-p000364-l0021 | unchanged | unchanged | — |
| d0eda948e5b1f3632f8687fb-p000927-l0052 | unchanged | unchanged | — |
| 137e9af6a0045d5746e26efa-p000008-l0023 | unchanged | unchanged | — |
| 6f9ad9bf99fd956607f4f9b3-p000020-l0016 | unchanged | unchanged | — |
| 341f77df7fe3f09264ceee79-p000017-l0008 | unchanged | unchanged | — |
| d7059ecf7417-p000013-l0002 | unchanged | unchanged | — |
| 535ad352d7a7-p000015-l0014 | unchanged | unchanged | — |
| 91252504a906-p000019-l0028 | unchanged | unchanged | — |
| 91252504a906-p000016-l0013 | unchanged | unchanged | — |
| 838d5080b03f-p000008-l0029 | unchanged | unchanged | — |
| 91252504a906-p000014-l0051 | unchanged | unchanged | — |

Reviewer probe coverage: 64/64 cases HOLD across PRESENCE/FULL/AB/AE, each reproduced from the reviewer’s saved original/recogniser/mode case before applying SF6. The probe runtimes are synthetic fixtures; no invented observation is treated as scored production evidence. Additional saved quote-deletion lines are listed below (including previously held lines).

| Line ID | Mode | SF5 → SF6 |
| --- | --- | --- |
| 0b7bf21d-p000002-l0004 | ENSEMBLE_AB | hold → hold |
| 177b717d-p000067-l0009 | ENSEMBLE_AB | hold → hold |
| 177b717d-p000077-l0005 | ENSEMBLE_AB | hold → hold |
| 177b717d-p000077-l0007 | ENSEMBLE_AB | corrected → hold |
| 177b717d-p000097-l0010 | ENSEMBLE_AB | corrected → hold |
| 384c3f89-p000030-l0010 | ENSEMBLE_AB | hold → hold |
| c0/nlg_poly/c023 | ENSEMBLE_AB | hold → hold |
| t4c/oa_poly1900/c009 | ENSEMBLE_AB | hold → hold |
| 0b7bf21d-p000002-l0004 | ENSEMBLE_AE | hold → hold |
| 177b717d-p000067-l0009 | ENSEMBLE_AE | corrected → hold |
| 177b717d-p000077-l0005 | ENSEMBLE_AE | hold → hold |
| 177b717d-p000077-l0007 | ENSEMBLE_AE | corrected → hold |
| 177b717d-p000097-l0010 | ENSEMBLE_AE | corrected → hold |
| 384c3f89-p000030-l0010 | ENSEMBLE_AE | hold → hold |
| c0/nlg_poly/c023 | ENSEMBLE_AE | hold → hold |
| t4c/oa_poly1900/c009 | ENSEMBLE_AE | hold → hold |
| 0b7bf21d-p000002-l0004 | FULL | hold → hold |
| 177b717d-p000067-l0009 | FULL | hold → hold |
| 177b717d-p000077-l0005 | FULL | hold → hold |
| 177b717d-p000077-l0007 | FULL | hold → hold |
| 177b717d-p000097-l0010 | FULL | corrected → hold |
| 384c3f89-p000030-l0010 | FULL | hold → hold |
| c0/nlg_poly/c023 | FULL | hold → hold |
| t4c/oa_poly1900/c009 | FULL | hold → hold |
| 0b7bf21d-p000002-l0004 | PRESENCE | hold → hold |
| 177b717d-p000067-l0009 | PRESENCE | hold → hold |
| 177b717d-p000077-l0005 | PRESENCE | hold → hold |
| 177b717d-p000077-l0007 | PRESENCE | hold → hold |
| 177b717d-p000097-l0010 | PRESENCE | corrected → hold |
| 384c3f89-p000030-l0010 | PRESENCE | hold → hold |
| c0/nlg_poly/c023 | PRESENCE | hold → hold |
| t4c/oa_poly1900/c009 | PRESENCE | hold → hold |

## Tests and reproduction

- New SF6 suite: **135 failures on the frozen 05f2dafb implementation**, with the same witnesses passing on SF6. [Failing-before log](SF6_evidence/witness_tests_before.log), [SF5 + SF6 witness suite](SF6_evidence/witness_tests_after.log).
- SF5 tests retain their exact composer assertions and positive controls. Only explicit deletion-release expectations change to exact HOLD checks, including unchanged effective Google bytes, no changes, and the SF6 reason. No general “either release or HOLD” assertion was substituted.
- Full labelfix suite: **1100 passed, 1 environment setup error(s), 0 assertion failures**. [Full result](SF6_evidence/tests_after.log), [SF5 baseline](SF6_evidence/tests_before.log). The capture test was not modified.
- Coverage includes both valid two-source mark pairs, valid detector+recogniser punctuation, one-source and missing/unscored/clipped/uncertain controls, A/B-as-one, replacement deletions, multiplicity, explicit numeral signs, insertion parity, elision aliases, confidence binding and deterministic census selection.

```sh
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY scripts/labelfix/sf6_measure.py all
SF6_TEST_BASELINE=1 $PY -m pytest tests/labelfix/test_sf6.py -q -p no:cacheprovider
$PY -m pytest tests/labelfix -q -p no:cacheprovider
$PY scripts/labelfix/sf6_report.py
$PY scripts/labelfix/sf6_verify.py
# One-command census addition once the pulled evidence lands:
$PY scripts/labelfix/sf6_measure.py --add-census /path/to/deletion_census.jsonl.gz
```

The census addition samples 30 distinct released-deletion lines with seed 6 from sorted IDs, writes source/hash custody, adds repository regression cases, replays both pools, runs all labelfix tests and refreshes this report and verification. It accepts JSON/JSONL runtime rows or L1R2’s aggregate `CHANGES.json`; the latter samples its AB deletion-example ID pool, not the full population. Aggregate IDs require a `deletion_witness_inputs.jsonl.gz` sidecar (record+runtime), or a full `overlay_ensemble_ab.jsonl.gz` with edit evidence and Google’s original labels available locally. Missing evidence writes a pending receipt and fails loudly; no source is reconstructed from guesses. The test harness validates both formats with independent 40-row fixtures. **census witnesses pending**. The read-only L1R2 report was checked at the end of this run: jobs prepared, no production job submitted and no pulled production census available; mock census counts are not substituted.

SF6 RESULT: policy sf6-release-v1; keraia witness HOLD yes; quote witnesses HOLD 64/64; held-out AB corrected 11, wrong 0, new 1, lines held 327; single-source deletions released 8→0; punctuation-deletion HOLDs 74 (apostrophe/quote/keraia 2/71/1); tests 1100 passed

## SF6b — same-kind spacing-breathing MOVE

Before = **SF6**; after = **SF6b**. Policy id remains `sf6-release-v1`. Only `deletion_guard` changes in production: a consumed spacing psili (`᾿`/`᾽`) or dasia (`῾`) can MOVE to a newly written combining breathing of the same kind on the same capital, when A∧B names it with known, scored, uncertainty-free coverage inside the saved window and the capital has no existing slot veto. AE retains its E check. No positive absence is asserted for a MOVE. All other deletion checks, composer/slot decisions, observation gates, K1 and punctuation rules are unchanged.

Policy sha **`704c47a3ee5b742376b3c73a8dcf0722dc0077f48a839b1109355cf3980f360e`**, previously `544ad37c4b6c0c1e1c98a8c0d7642afc5c188bbd52e79aaf6eef0d1dce233460`. The existing `policy_binding()` hashes the changed source automatically; the replay passes this binding and sha to release overlays. [Policy and comparison receipt](SF6b_evidence/comparison.json).

The unchanged SF6 instruments were rerun twice from saved evidence: frozen launch sources for SF6, then SF6b. Every before line/check/metric reproduces the original SF6 evidence exactly. Original SF6 evidence and the pre-SF6b report prefix are preserved. No network, inference, `.git` writes or other-worktree writes. Launch HEAD: `b1104e3273e7d44acb95fe1d53495df0535f1a77`.

### Held-out 666 — SF6 → SF6b

| Mode | Row | Corrected /80, elision K/D/A or raw deleted | Wrong | Missed | HOLD errors | New | Instrument lines held /666 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | mark | 10 → 10 | 0 → 0 | 2 → 2 | 68 → 68 | 0 → 0 | 383 → 383 |
| PRESENCE | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| PRESENCE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| FULL | mark | 8 → 8 | 0 → 0 | 0 → 0 | 72 → 72 | 0 → 0 | 391 → 391 |
| FULL | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| FULL | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AB | mark | 11 → 11 | 0 → 0 | 6 → 6 | 63 → 63 | 1 → 1 | 325 → 325 |
| ENSEMBLE_AB | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| ENSEMBLE_AB | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AE | mark | 10 → 10 | 0 → 0 | 6 → 6 | 64 → 64 | 6 → 6 | 317 → 317 |
| ENSEMBLE_AE | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| ENSEMBLE_AE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |

No held-out label, status, check or slot outcome changes. Missing full runtime coverage remains unknown; it cannot qualify a MOVE. The 81,700 frozen slot/mode records remain identical. [SF6 replay](SF6b_evidence/before/heldout/metrics.json), [SF6b replay](SF6b_evidence/after/heldout/metrics.json).

### M2 DEV 273 — SF6 → SF6b

| Mode | Row | Corrected /43 or raw deleted | Wrong | Missed | HOLD errors | Changed control slots | Instrument lines held /273 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | mark | 2 → 2 | 0 → 0 | 6 → 6 | 35 → 35 | 0 → 0 | 260 → 260 |
| PRESENCE | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| PRESENCE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| FULL | mark | 2 → 2 | 0 → 0 | 6 → 6 | 35 → 35 | 0 → 0 | 261 → 261 |
| FULL | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| FULL | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AB | mark | 0 → 0 | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AB | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| ENSEMBLE_AB | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AE | mark | 0 → 0 | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AE | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| ENSEMBLE_AE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |

No M2 label, status, check or slot outcome changes. B/E remain missing; no replacement evidence is invented. Only the DEV allowlist is decoded: locked stratum (ii) decoded/composed **0**. Punctuation truth remains UNKNOWN. [SF6 replay](SF6b_evidence/before/m2_dev/metrics.json), [SF6b replay](SF6b_evidence/after/m2_dev/metrics.json).

Actual whole-line status counts (corrected/unchanged/HOLD):

| Cohort | Mode | SF6 → SF6b |
| --- | --- | --- |
| held-out | PRESENCE | 6/276/384 → 6/276/384 |
| held-out | FULL | 5/269/392 → 5/269/392 |
| held-out | ENSEMBLE_AB | 6/333/327 → 6/333/327 |
| held-out | ENSEMBLE_AE | 9/338/319 → 9/338/319 |
| M2 DEV | PRESENCE | 0/13/260 → 0/13/260 |
| M2 DEV | FULL | 0/12/261 → 0/12/261 |
| M2 DEV | ENSEMBLE_AB | 0/0/273 → 0/0/273 |
| M2 DEV | ENSEMBLE_AE | 0/0/273 → 0/0/273 |

### Witnesses and every changed line

Both capital witnesses release with exactly one psili, consuming one spacing sign. A and B both name psili; their saved spans are within the saved windows, scored, known and uncertainty-free. The detector’s empty observation map is not used as an absence signal. These lines occur in both SF5 and L1A witness cohorts; they are two unique lines, four cohort records.

| Line ID | Cohort / mode | SF6 | SF6b label | Explanation |
| --- | --- | --- | --- | --- |
| a963b33d02c23d4127f5ec26-p000012-l0029 | sf5 / ENSEMBLE_AB | hold | -Ἀνεξιχνίαστοι αἱ βουλαὶ τοῦ Ὑψίστου, κυρα- | HOLD → corrected: U+1FBF psili moves to U+0313 on the same Α; scored A∧B psili, no other veto. |
| 32aae9fec147d3b483deb96e-p000060-l0057 | sf5 / ENSEMBLE_AB | hold | ΕΡΝΕΣΤΟΣ. -Ἀλλά, συγγνώμην, ἀγαπητέ μου, ποὺ σὲ | HOLD → corrected: U+1FBF psili moves to U+0313 on the same Α; scored A∧B psili, no other veto. |
| a963b33d02c23d4127f5ec26-p000012-l0029 | l1a / ENSEMBLE_AB | hold | -Ἀνεξιχνίαστοι αἱ βουλαὶ τοῦ Ὑψίστου, κυρα- | HOLD → corrected: U+1FBF psili moves to U+0313 on the same Α; scored A∧B psili, no other veto. |
| 32aae9fec147d3b483deb96e-p000060-l0057 | l1a / ENSEMBLE_AB | hold | ΕΡΝΕΣΤΟΣ. -Ἀλλά, συγγνώμην, ἀγαπητέ μου, ποὺ σὲ | HOLD → corrected: U+1FBF psili moves to U+0313 on the same Α; scored A∧B psili, no other veto. |

Saved capital coverage (no evidence fields filled in):

| Line ID | Recogniser NFD start | Window | A span | B span | Reader evidence |
| --- | --- | --- | --- | --- | --- |
| a963b33d02c23d4127f5ec26-p000012-l0029 | 2 | [34.5, 69.5] | [41.3, 48.8] | [41.3, 48.8] | A=psili; B=psili; both scored, unadjudicated (known), uncertainty=[] |
| 32aae9fec147d3b483deb96e-p000060-l0057 | 12 | [204.0, 240.0] | [210.4, 220.6] | [210.4, 220.6] | A=psili; B=psili; both scored, unadjudicated (known), uncertainty=[] |

The 56 SF5 witnesses now have 48 releases / 8 HOLDs (SF6: 46 / 10); the 48 L1A lines have 43 releases / 5 HOLDs (SF6: 41 / 7). All other witness outcomes and deletion checks are exact SF6 parity; the known reader mistakes remain HOLD. Quote probes remain **64/64 HOLD** and the keraia witness remains **HOLD**. No mark scoring is inferred for the witness cohort. [Full before](SF6b_evidence/before/witness_results.jsonl.gz), [full after](SF6b_evidence/after/witness_results.jsonl.gz), [per-line changes](SF6b_evidence/line_changes.jsonl), [changed checks](SF6b_evidence/check_changes.jsonl).

Released raw spacing-character removals change 0 → 2 per capital-witness cohort; all two are explicitly `operation=MOVE`, with the original absence signals still false. They are not content deletions. True released deletions remain 0 in held-out, M2 and these witness cohorts. Apostrophe/quote/keraia HOLD counts are unchanged in every cohort and mode.

The mismatched-kind control consumes spacing psili while proposing dasia, with no second certified psili-absence source: HOLD, no MOVE. The unnamed-reader control remains HOLD even for a forced attached-psili proposal. Unscored, uncertain, missing/conflicting B, clipped, unseen, outside-window, lowercase, already-attached, other-boundary and duplicate-sign controls retain exact HOLD assertions. Matching dasia is checked directly in the deletion guard; the unchanged composer/punctuation guard does not gain a new dasia rewrite route. [Concrete synthetic evidence](SF6b_evidence/synthetic_witnesses.json).

### Tests and reproduction

Full labelfix: **1260 passed, 1 environment setup error(s), 0 assertion failures**. The unchanged capture test cannot bind its loopback socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`), also reproduced before the change (1100 passed, 1 error). All-green acceptance remains unmet in this sandbox; no test is skipped, deselected or weakened. [Before](SF6b_evidence/tests_before.log), [after](SF6b_evidence/tests_after.log).

Only the two released capital expectations change in existing regression tests; their output strings are exact. Existing unscored SF5 synthetic attachments still HOLD. The new positive MOVE tests fail on frozen SF6 (72 failures) and pass on SF6b (633 SF5/SF6 tests passed); all other SF6 absence tests are retained. [Frozen-SF6 failures](SF6b_evidence/witness_tests_before.log), [SF5/SF6 suite after](SF6b_evidence/witness_tests_after.log). Census witnesses remain pending; the original SF6 saved evidence is the measurement scope.

```sh
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY scripts/labelfix/sf6b_measure.py measure
$PY -m pytest tests/labelfix -q -p no:cacheprovider > docs/records/labelfix/spellcheck/SF6b_evidence/tests_after.log 2>&1
$PY scripts/labelfix/sf6b_measure.py report
$PY scripts/labelfix/sf6b_measure.py verify
```

SF6b RESULT: breathing-move exception; capital witnesses released 2/2; mismatched-kind HOLD yes; unnamed HOLD yes; held-out AB corrected 11, wrong 0; tests 1260 passed; policy sha 704c47a3ee5b742376b3c73a8dcf0722dc0077f48a839b1109355cf3980f360e

## SF6c — evidence certification (B01/B02)

Before = **SF6b** (`8c5ad361` production sources); after = **SF6c**. Policy id remains `sf6-release-v1`. The SF6 Boolean rule, character inventory, SF5 composer, slot decisions and same-kind capital MOVE exception are unchanged. This section supersedes the original SF6 claim that the old loader never filled a missing score.

Policy sha **`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`**, previously `704c47a3ee5b742376b3c73a8dcf0722dc0077f48a839b1109355cf3980f360e`. The binding now covers the score loader, frame-score provenance and all live M2/Clariden runtime builders, as well as the original gate/consumer sources. [Comparison and source binding](SF6c_evidence/comparison.json).

### Diffs and confidence floor

- **B01:** `Alignment.confidence` defaults to `None`; omitted/null scores remain missing through load, save, transfer, M2 and Clariden. Legacy runtime copies explicitly retain `scored: false` with missing/unprovenanced provenance. A genuine **0.0 is never positive**. Recogniser absence requires an explicit finite line score **> 0.5**, plus explicit scored observation of the complete saved target window, also **> 0.5**. A finite line average alone cannot authorize absence.
- The `ctc-window-score-v1` envelope binds the alignment digest, transcript digest, NFD start/base, image width, target window, valid frame range and score method. Regional confidence is the **minimum** max posterior over **every overlapping frame**, including blanks. New alignments retain actual frame probabilities with their original transcript digest; legacy alignments without them produce **no regional scores**. Object transfers preserve a transferred flag; record transfers are detected by the frame/transcript ownership digest. Transferred spans cannot supply regional observation. The historical shared transfer helper and its old scoring receipt remain unchanged. No saved frame score is invented.
- M2 inference and cached-detector replay write those fields. `l1_infer`, `l1e_run` and the held-out L1E builder preserve explicit score/provenance or explicitly mark it unavailable. The historical L1 detector builder existed only in the immutable `artifacts/labelfix_l1e/reference/` snapshot: `scripts/labelfix/clariden/l1_detect.py` is the same builder with only confidence, regional evidence and native width added. Historical references/deploy snapshots remain unchanged. R1 extraction records `line_confidence_missing`, rather than converting missing to zero.
- **B02:** MOVE, ordinary reader A/B/E absence, and recogniser locator/window validation all call `_source_in_window`. Native source spans must be finite, inside the image, and contained in the saved target-letter window. A scored recogniser region must cover the **whole** target window. Padded reader inputs need not have the detector window dimensions. Historical R1 coverage retains the extractor’s explicit native-span check (`window_contract`, known/scored state, recorded empty uncertainty); `out_of_image_span` disqualifies it. Generic finite spans without native bounds provenance remain unavailable. This preserves both saved capital MOVEs without inventing image widths.
- Recognition score, regional provenance and image width are included in the content-bound runtime envelope. No recogniser/detector/reader decisions, alias handling, independent-signal combinations or whole-line HOLD dispatch change.

**Floor justification.** `0.5` is the existing saved R1 extraction admissibility cutoff, not a threshold fitted to release outcomes. A strict majority posterior on every observed frame is a conservative lower bound for a positive scored observation; zero and values at the floor HOLD. The saved distribution below places all 666 held-out and all 273 DEV line scores above it, while the broader saved C1 cache has 8/91,469 at or below it. Thus the floor does not manufacture a yield change in these cohorts. These are **line averages**, not regional minimum scores or calibrated absence probabilities: the saved evidence cannot calibrate regional accuracy. Missing regional observations HOLD regardless of a high line mean. Provenance and full-window observation, not the floor alone, repair B01.

| Saved score population | n | min | p01 | median | max | at/below 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| held-out matching S0 alignments | 666 | 0.945503 | 0.959674 | 0.980864 | 0.999478 | 0 |
| M2 DEV runtime | 273 | 0.519740 | 0.660494 | 0.970228 | 0.995106 | 0 |
| C1 saved alignment cache | 91469 | 0.301551 | 0.878730 | 0.973886 | 0.998988 | 8 |

### Runtime-source audit and newly held lines

Every loose runtime/combined/detector-shard and witness-input source on disk was enumerated and hashed; original-label overlays were compared under frozen SF6b and SF6c. DEV filtering occurs **before JSON decoding** for every M2 variant. The locked R0 alignment file was hashed only; locked stratum (ii) decoded/composed **0**. [Per-file audit, distributions, writer paths and status counts](SF6c_evidence/runtime_audit.json).

| Source | Records audited | Score representation | Regional score records | New HOLD line/mode records |
| --- | --- | --- | --- | --- |
| .cache/labelfix/m2/runtime.jsonl | 273 | above_floor=273 | 0 | 0 |
| artifacts/labelfix_l1e/fixture_v4/mock/historical/combined/shard-00000-combined.jsonl.gz | 64 | missing=64 | 0 | 0 |
| artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-detector.jsonl.gz | 64 | missing=64 | 0 | 0 |
| artifacts/labelfix_l1e/mock/historical/combined/shard-00000-combined.jsonl.gz | 64 | missing=64 | 0 | 0 |
| artifacts/labelfix_l1e/mock/historical/detector/shard-00000-detector.jsonl.gz | 64 | missing=64 | 0 | 0 |
| artifacts/labelfix_l1e/mock_run_v4/inference/shard-00000-combined.jsonl.gz | 64 | missing=64 | 0 | 0 |
| docs/records/labelfix/spellcheck/S7_evidence/m2_S1/runtime.jsonl | 273 | above_floor=233, missing=40 | 0 | 0 |
| docs/records/labelfix/spellcheck/S7_evidence/m2_S2/runtime.jsonl | 273 | above_floor=233, missing=40 | 0 | 0 |
| docs/records/labelfix/spellcheck/S7_evidence/m2_S3/runtime.jsonl | 273 | above_floor=233, missing=40 | 0 | 0 |
| docs/records/labelfix/spellcheck/S7_evidence/m2_accepted/runtime.jsonl | 273 | above_floor=233, missing=40 | 0 | 0 |
| docs/records/labelfix/spellcheck/S7_evidence/m2_scope_only/runtime.jsonl | 273 | above_floor=233, missing=40 | 0 | 0 |
| docs/records/labelfix/spellcheck/SF5_evidence/witness_inputs.jsonl.gz | 56 | missing=56 | 0 | 0 |
| docs/records/labelfix/spellcheck/SF6_evidence/witness_inputs.jsonl.gz | 168 | missing=168 | 0 | 0 |
| docs/records/labelfix/spellcheck/SF6b_evidence/after/witness_inputs.jsonl.gz | 168 | missing=168 | 0 | 0 |
| docs/records/labelfix/spellcheck/SF6b_evidence/before/witness_inputs.jsonl.gz | 168 | missing=168 | 0 | 0 |

Nine packed code/measurement/mock archives were also checked without extraction or mutation. Four runtime members (64 records each) in the two mock64 archives all omit confidence and regional scores; SF6c adds zero HOLDs. The other seven archives contain no runtime members. Their complete hashes and member results are in the same audit receipt.

| Archive | Runtime member | n | Missing scores | New HOLD line/mode records |
| --- | --- | --- | --- | --- |
| artifacts/labelfix_l1e/mock64_v4.tar.gz | mock/historical/combined/shard-00000-combined.jsonl.gz | 64 | 64 | 0 |
| artifacts/labelfix_l1e/mock64_v4.tar.gz | mock/historical/detector/shard-00000-detector.jsonl.gz | 64 | 64 | 0 |
| artifacts/labelfix_l1e/mock64.tar.gz | mock/historical/combined/shard-00000-combined.jsonl.gz | 64 | 64 | 0 |
| artifacts/labelfix_l1e/mock64.tar.gz | mock/historical/detector/shard-00000-detector.jsonl.gz | 64 | 64 | 0 |

The 40 missing-score records per S7 runtime are already skipped/out of scope. All 168 SF6/SF6b witness runtimes omit the confidence key (56 SF5 + 48 L1A + 64 synthetic quote probes); the held-out SF6 instrument also omits it for all 666 lines. The five local Clariden mock detector/combined sources each omit it for all 64 records. No observed production score is silently reclassified as zero. The reviewer fixtures separately retain explicit missing/default-zero cases.

**New HOLDs:** held-out 0; M2 DEV 0; SF5/L1A/quote witnesses 0; all other audited local runtime sources 0. The main replay changes 28 M2 line/mode check records on 11 unique lines: recogniser absence becomes unavailable because regional scoring was never saved. Every affected line was already HOLD. No mark or release outcome changes. [Exact check changes](SF6c_evidence/check_changes.jsonl), [new-HOLD list](SF6c_evidence/line_changes.jsonl).

| Already-held DEV line | Modes with recogniser signal revoked |
| --- | --- |
| t4c/anemi_poly1850/c028 | PRESENCE, FULL |
| t4c/bsb_poly1850/c013 | PRESENCE, FULL |
| t4c/oa_poly1900/c006 | PRESENCE, FULL |
| t4c/oa_poly1900/c009 | PRESENCE, FULL, ENSEMBLE_AB, ENSEMBLE_AE |
| t4c/oa_poly1900/c021 | PRESENCE, FULL |
| t4c/pleias_poly1850/c037 | PRESENCE, FULL |
| c0/ia_greek_latin/c019 | PRESENCE, FULL, ENSEMBLE_AB, ENSEMBLE_AE |
| c0/ia_poly1850/c018 | PRESENCE, FULL |
| c0/ia_poly1850/c040 | PRESENCE, FULL, ENSEMBLE_AB, ENSEMBLE_AE |
| c0/kosmopolis_poly/c014 | PRESENCE, FULL |
| c0/nlg_poly/c005 | PRESENCE, FULL |

### Held-out 666 — SF6b → SF6c

| Mode | Row | Corrected /80, K/D/A or raw deleted | Wrong | Missed | HOLD errors | New | Instrument lines held /666 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | mark | 10 → 10 | 0 → 0 | 2 → 2 | 68 → 68 | 0 → 0 | 383 → 383 |
| PRESENCE | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| PRESENCE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| FULL | mark | 8 → 8 | 0 → 0 | 0 → 0 | 72 → 72 | 0 → 0 | 391 → 391 |
| FULL | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| FULL | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AB | mark | 11 → 11 | 0 → 0 | 6 → 6 | 63 → 63 | 1 → 1 | 325 → 325 |
| ENSEMBLE_AB | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| ENSEMBLE_AB | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AE | mark | 10 → 10 | 0 → 0 | 6 → 6 | 64 → 64 | 6 → 6 | 317 → 317 |
| ENSEMBLE_AE | elision kept/deleted/added | 212/1/1 → 212/1/1 | — | — | — | — | — |
| ENSEMBLE_AE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |

This remains the **incomplete local frozen-slot instrument**, not full-runtime recomposition. It has no saved B/E extraction coverage, no recogniser score and no positive absence signals. The original 81,700 slot/mode records stay identical. The 11 AB corrected marks are an instrument result; actual AB released corrected **lines** remain 6. [Before](SF6c_evidence/before/heldout/metrics.json), [after](SF6c_evidence/after/heldout/metrics.json).

### M2 DEV 273 — SF6b → SF6c

| Mode | Row | Corrected /43 or raw deleted | Wrong | Missed | HOLD errors | Changed control slots | Instrument lines held /273 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | mark | 2 → 2 | 0 → 0 | 6 → 6 | 35 → 35 | 0 → 0 | 260 → 260 |
| PRESENCE | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| PRESENCE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| FULL | mark | 2 → 2 | 0 → 0 | 6 → 6 | 35 → 35 | 0 → 0 | 261 → 261 |
| FULL | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| FULL | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AB | mark | 0 → 0 | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AB | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| ENSEMBLE_AB | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |
| ENSEMBLE_AE | mark | 0 → 0 | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AE | elision | UNKNOWN → UNKNOWN | — | — | — | — | — |
| ENSEMBLE_AE | raw deleted mark/apostrophe/quote/keraia/other | 0/0/0/0/0 → 0/0/0/0/0 | — | — | — | — | — |

B/E remain missing; no reader is copied into another arm. DEV punctuation truth remains UNKNOWN. [Before](SF6c_evidence/before/m2_dev/metrics.json), [after](SF6c_evidence/after/m2_dev/metrics.json).

Actual whole-line status counts (corrected/unchanged/HOLD):

| Cohort | Mode | SF6b → SF6c |
| --- | --- | --- |
| held-out | PRESENCE | 6/276/384 → 6/276/384 |
| held-out | FULL | 5/269/392 → 5/269/392 |
| held-out | ENSEMBLE_AB | 6/333/327 → 6/333/327 |
| held-out | ENSEMBLE_AE | 9/338/319 → 9/338/319 |
| M2 DEV | PRESENCE | 0/13/260 → 0/13/260 |
| M2 DEV | FULL | 0/12/261 → 0/12/261 |
| M2 DEV | ENSEMBLE_AB | 0/0/273 → 0/0/273 |
| M2 DEV | ENSEMBLE_AE | 0/0/273 → 0/0/273 |

### Witnesses — SF6b → SF6c

| Witness cohort | Mode | n | Corrected/unchanged/HOLD: SF6b → SF6c |
| --- | --- | --- | --- |
| sf5 | ENSEMBLE_AB | 56 | 2/46/8 → 2/46/8 |
| l1a | ENSEMBLE_AB | 48 | 3/40/5 → 3/40/5 |
| quote_probe | PRESENCE | 16 | 0/0/16 → 0/0/16 |
| quote_probe | FULL | 16 | 0/0/16 → 0/0/16 |
| quote_probe | ENSEMBLE_AB | 16 | 0/0/16 → 0/0/16 |
| quote_probe | ENSEMBLE_AE | 16 | 0/0/16 → 0/0/16 |

Deletion-related HOLD lines by class (classes may overlap; unchanged across SF6b → SF6c):

| Cohort | Mode | mark/apostrophe/quote/keraia/other HOLD lines |
| --- | --- | --- |
| held-out | PRESENCE | 79/4/6/0/74 → 79/4/6/0/74 |
| held-out | FULL | 79/4/6/0/74 → 79/4/6/0/74 |
| held-out | ENSEMBLE_AB | 79/4/6/0/74 → 79/4/6/0/74 |
| held-out | ENSEMBLE_AE | 79/4/6/0/74 → 79/4/6/0/74 |
| M2 DEV | PRESENCE | 113/2/2/1/112 → 113/2/2/1/112 |
| M2 DEV | FULL | 113/2/2/1/112 → 113/2/2/1/112 |
| M2 DEV | ENSEMBLE_AB | 113/2/2/1/112 → 113/2/2/1/112 |
| M2 DEV | ENSEMBLE_AE | 113/2/2/1/112 → 113/2/2/1/112 |
| sf5 | ENSEMBLE_AB | 5/2/0/1/0 → 5/2/0/1/0 |
| l1a | ENSEMBLE_AB | 5/0/0/0/0 → 5/0/0/0/0 |
| quote_probe | PRESENCE | 8/0/16/0/0 → 8/0/16/0/0 |
| quote_probe | FULL | 8/0/16/0/0 → 8/0/16/0/0 |
| quote_probe | ENSEMBLE_AB | 8/0/16/0/0 → 8/0/16/0/0 |
| quote_probe | ENSEMBLE_AE | 8/0/16/0/0 → 8/0/16/0/0 |

Both saved capital witnesses still release the exact SF6b labels with one `operation=MOVE`, no absence signals. Mismatched kind, unnamed reader, extra deletion and invalid-location controls HOLD. The keraia witness remains HOLD and quote probes remain 64/64 HOLD. Raw spacing-sign removals remain 2 per SF5/L1A cohort, all MOVEs; true released deletions remain zero. Punctuation-deletion HOLD counts by class are unchanged. Census witnesses remain pending: the requested L1R2 report/census is absent on disk.

All **16/16** saved reviewer JSON cases now HOLD: the 12 formerly unsafe releases (3 witness paths × 4 modes) plus 4 already-held missing-key controls. [Inputs retained read-only](../../reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json), [after overlays](SF6c_evidence/unsafe_witnesses_after.json).

### Tests, scope and reproduction

The reviewer’s 75 cases are now `tests/labelfix/test_sf6_reviewer.py`: frozen SF6b reproduces **12 failed / 63 passed**; SF6c passes **75/75**. Its only harness adaptation changes the obsolete loader-default assertion from `0.0` to `None`; every release/HOLD assertion is preserved. The shared positive synthetic fixture now explicitly supplies image width and actual synthetic regional frame scores; production saved evidence is untouched. Every existing test assertion is unchanged. An additional 95 certification cases cover missing/zero/floor/invalid scores, regional provenance, all reader arms, bounds, transfers, both real runtime writers under mocked inference, and the saved unsafe JSON.

Full labelfix: **1430 passed, 1 environment setup error, 0 assertion failures**. Baseline was **1260 passed, 1 identical setup error**. The unchanged `test_capture.py::test_server_appends_each_decision_and_serves_static` cannot bind a loopback socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`). No skip, deselection, mock or test weakening is used for that test. **All-green acceptance remains unmet in this environment**. [Baseline log](SF6c_evidence/tests_before.log), [full after log](SF6c_evidence/tests_after.log), [reviewer before](SF6c_evidence/reviewer_before.log), [reviewer after](SF6c_evidence/reviewer_after.log).

Saved evidence only; network OFF; detector/R1/CTC inference runs 0; no `.git` writes by this run; other worktrees read-only. This checkout’s HEAD, branch and index remain unchanged. Concurrent activity changed the separate `spellcheck-s8` worktree’s shared Git metadata; those differences are recorded separately and were not restored or edited. [Git custody differences](SF6c_evidence/git_metadata_changes.json). Before replay matches every saved SF6b row and metric. [Scope/custody verification](SF6c_evidence/verification.json).

```sh
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY scripts/labelfix/sf6c_measure.py
$PY scripts/labelfix/sf6c_audit.py
$PY -m pytest tests/labelfix/test_sf6_reviewer.py -q -p no:cacheprovider > docs/records/labelfix/spellcheck/SF6c_evidence/reviewer_after.log 2>&1
$PY -m pytest tests/labelfix -q -p no:cacheprovider > docs/records/labelfix/spellcheck/SF6c_evidence/tests_after.log 2>&1
$PY scripts/labelfix/sf6c_report.py
$PY scripts/labelfix/sf6c_verify.py
```

SF6c RESULT: B01 fixed yes (floor 0.5); B02 fixed yes; reviewer tests 75/75; held-out AB corrected 11, wrong 0; tests 1430 passed; policy sha 6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406
