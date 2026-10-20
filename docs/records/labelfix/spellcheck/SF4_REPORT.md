# SF4 — conservative cycle 3 fixes

17 October 2026. C3-B01, C3-M01, C3-N01 and the C2-N02 notes-binding residual are repaired. **All five original review witnesses fail on the snapshotted SF3 source and pass on SF4.** The full labelfix run has **627 passed and one environment setup error**: the sandbox rejects the existing HTTP capture test’s loopback `socket.bind` with `PermissionError: [Errno 1] Operation not permitted`. There are no assertion failures, skips, deselections or weakened tests. The all-green suite requirement remains unverified for that one test.

Launch HEAD was `5d074d28d307be3497114148401c33868a74b2ef`, branch `opus/spellcheck`. The launch gate bytes match the reviewed SF3 policy exactly. Work used local CPU and saved evidence; no network, Clariden work, reader/CTC inference, detector rerun, training or release publication was performed. Synthetic geometry is used only in the regression tests. No `.git` writes were made; all seven files in this worktree’s Git metadata directory retain their launch hashes ([check](SF4_evidence/git_unchanged.json)).

## Policy and adapters

**C3-B01.** Either uppercase recogniser case or a saved physical capital case/band makes every recorded top cut decisive. Saved capital pixel votes, capital bands and capital geometry cannot be overruled by a lowercase recogniser vote. There is no capital side-zone exception. Bottom-cut relaxation applies only to lowercase slots that cannot carry a below mark, have no adscript context, and have no subscript predicted by detector, recogniser, A, B or diagnostic E. K1 observation flags and saved hold reasons use the same conservative rule.

The scalar SF3 meanline/x-height records do not establish clearance of the whole overhead **and** preposed upper zone. SF4 therefore keeps their top cuts on mark-bearing letters; it does not invent another clearance predicate. Empty reader predictions never reduce the observation requirement. This deliberately gives back SF3 coverage gains. Lowercase consonant negative controls remain covered.

**C3-M01.** `bind_runtime` binds recogniser text/context, raw detector geometry/decisions, A predictions and coverage, every saved peer’s predictions and coverage, and K1 inputs under one content digest. Release, M2 and saved replay adapters pass that full runtime. Owner pages accept `--runtime` files hash-bound by the reading configuration’s `runtime` path-to-SHA256 mapping, require explicit B/E evidence entries, and compose the saved detector record without rerunning the detector. The sidecar and release overlay retain the evidence digest. Historical partial owner calls produce an explicit HOLD; they cannot claim release parity. Differing B/E predictions are tested through both the adapter and the actual page CLI.

**C3-N01.** Slotting, detector/release rendering, K1 and owner HTML share the elision classification. Every declared alias (`'`, `’`, `ʼ`, `᾽`, `᾿`) is exercised through actual slotting/composition/K1 in final, prefix, internal and closing positions. Offsets and letter correspondence are asserted. Historical modifier-apostrophe slots are preserved as punctuation evidence, with unresolved evidence retaining a veto.

**C2-N02 residual.** `owner_implicit_changes.py --review-binding` uses the same validator as `box_regression.py`. Approval language requires the exact reviewed-page hash and notes-file hashes, verified against actual bytes. Missing, mismatched and subsequently changed page/notes inputs fail before output; the positive case records the binding and its digest.

Current policy: `sf4-release-v1`, digest `52fb3a5b183b214f6fe1e0986672060b4b41493b9a731ffa259c022714184a36`. Source bindings are in the [held-out receipt](SF4_evidence/heldout/receipt.json).

## Held-out instrument: SF3 → SF4

Frozen domain: **666 lines, 80 Google mark errors, 10,046 known and 300 unknown-truth mapped/scored slots**. Unknown truth is excluded from outcome totals. Outcomes count slots; a whole line releases only when every slot clears the gate.

| Mode | Corrected / 80 | Wrong | Missed | HOLD errors | New | Lines held / 666 |
|---|---:|---:|---:|---:|---:|---:|
| PRESENCE | 46 → 42 | 1 → 1 | 2 → 2 | 31 → 35 | 5 → 5 | 339 → 348 |
| FULL | 41 → 37 | 0 → 0 | 0 → 0 | 39 → 43 | 3 → 3 | 357 → 365 |
| ENSEMBLE_AB | 49 → 45 | 2 → 2 | 6 → 6 | 23 → 27 | 6 → 6 | 256 → 274 |
| ENSEMBLE_AE | 49 → 46 | 2 → 2 | 6 → 6 | 23 → 26 | 9 → 9 | 242 → 261 |

**Measurement boundary:** the Mac has the complete saved SF3 decisions, S6 physical records, frozen S4 truth, Google labels and A/B/E predictions, but lacks the complete extraction coverage records. This is a saved-decision observation replay, **not a full 666-line runtime recomposition**. It retains every existing reader/coverage/guard veto and output, and applies only additional observation vetoes. No missing coverage was synthesized. Both phases are scored by the same frozen scorer. Every SF3 table cell and error event is reproduced exactly; punctuation output, edit guards and orthographic K1 are checked unchanged on this cohort.

The [per-slot proof](SF4_evidence/heldout/per_slot_proof.jsonl.gz) covers **81,700 slot/mode records**: accepted SF4 slots are a subset of accepted SF3 slots and every output mark set is unchanged. **812 slot/mode decisions** gain reasons. The [comparison](SF4_evidence/heldout/comparison.json) enumerates each wrong/new slot by line ID, recogniser start, frozen slot, Google/truth/reader mark sets and outcome. Those unsafe identities and mark sets are **identical in all four modes**; none was added. [Changed slots](SF4_evidence/heldout/slot_changes.jsonl.gz) retain their saved physical evidence.

Corrections returning to HOLD are the top-cut witnesses at `9c1dca9b-p000015-l0067` start 13, `51fe7386-p000024-l0012` start 22, and `51fe7386-p000024-l0015` start 43; the last line also loses a correction at start 3 to the restored capital bottom-cut veto. The per-mode error events preserve each transition.

An independent check uses the **complete saved 64-line verification runtime**: all **256 mode/line and 7,620 slot/mode decisions** match the full composer and owner adapter exactly. The observation replay also matches full recomposition on those records ([parity receipt](SF4_evidence/runtime64_parity.json)). This remains a verification sample, not new inference or production accuracy evidence.

## HOLD reasons

Counts are reason incidences over slots, SF3 → SF4; rows overlap. Indexed unsupported-character receipts and unscored-width reasons are grouped below. K1 has 260 incidences over 144 distinct slots in each mode. Exact reasons, line counts and sole-family line counts are in [reasons.json](SF4_evidence/heldout/reasons.json).

| Reason family | PRESENCE | FULL | AB | AE |
|---|---:|---:|---:|---:|
| K1 | 260 → 260 | 260 → 260 | 260 → 260 | 260 → 260 |
| detector_clipped_top | 79 → 202 | 79 → 202 | 79 → 202 | 79 → 202 |
| detector_clipped_bottom | 131 → 214 | 131 → 214 | 131 → 214 | 131 → 214 |
| segmentation uncertainty | 114 → 114 | 114 → 114 | 114 → 114 | 114 → 114 |
| localisation unknown | 44 → 44 | 44 → 44 | 44 → 44 | 44 → 44 |
| unnamed detector mark | 64 → 64 | 64 → 64 | 64 → 64 | 64 → 64 |
| detector kind/set disagreement | 457 → 457 | 498 → 498 | 0 → 0 | 0 → 0 |
| ensemble set disagreement | 0 → 0 | 0 → 0 | 75 → 75 | 58 → 58 |
| punctuation guard | 37 → 37 | 37 → 37 | 37 → 37 | 37 → 37 |
| unsupported raw character | 295 → 295 | 295 → 295 | 295 → 295 | 295 → 295 |
| unsupported NFD character | 295 → 295 | 295 → 295 | 295 → 295 | 295 → 295 |
| A missing | 18 → 18 | 18 → 18 | 18 → 18 | 18 → 18 |
| A unscored | 18 → 18 | 18 → 18 | 18 → 18 | 18 → 18 |
| A UNKNOWN / uncertainty | 6 → 6 | 6 → 6 | 6 → 6 | 6 → 6 |
| selected peer missing | 0 → 0 | 0 → 0 | 18 → 18 | 18 → 18 |
| selected peer unscored | 0 → 0 | 0 → 0 | 18 → 18 | 18 → 18 |
| selected peer UNKNOWN / uncertainty | 0 → 0 | 0 → 0 | 6 → 6 | 6 → 6 |

## Verification and retained evidence

- [Original review witnesses against SF3](SF4_evidence/witnesses_before.log): **5 failed**; [against SF4](SF4_evidence/witnesses_after.log): **5 passed**. The repository copy is byte-identical to the review witness file.
- [Additional SF4 tests](SF4_evidence/tests_sf4.log): **173 passed**, covering conflicting case/band signals, every bound runtime input, differing diagnostic peers, the actual owner CLI, every elision alias and notes binding failures/success.
- Existing SF3 assertions that allowed unsafe top clipping now require HOLD. The prior page-parity test retains exact slot/text equality and now supplies the complete runtime. Other existing tests/assertions were retained.
- [Full labelfix run](SF4_evidence/tests_after.log): **627 passed, 1 setup error** at the sandbox-denied loopback bind. That error also existed before the fix ([baseline log](SF4_evidence/tests_before.log)). It was neither skipped nor converted to a pass.
- Changing the reading sources invalidated the historical R1 source receipt. Before rebinding it, **12,640 saved A–E raw/normalised readings** were regenerated from frozen S4 slots and saved predictions, matching texts, K1 flags/removals and serialization exactly. [Compatibility proof](SF4_evidence/r1_compatibility.json) and [prior receipt](SF4_evidence/r1_score_receipt_before.json) retain the evidence. Historical metrics/results are unchanged; this is explicitly not a full metric rescore.
- `git diff --check` passes. [Verification receipt](SF4_evidence/verification.json) binds the current policy, evidence and tests.

Reproduce locally with bytecode and pytest cache writes disabled:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/labelfix -q -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/sf4_measure.py --out /private/tmp/SF4-fresh-heldout
```

Agreement remains stability of correlated readers. The existing wrong/new slots remain unresolved; these saved-evidence checks do not establish training-wave print precision.

SF4 RESULT: C3-B01/M01/N01 + C2-N02 residual fixed; review witnesses as tests 5/5; AB held-out lines held 256→274, corrected 49→45, wrong 2→2, new 6→6; tests 627 passed
