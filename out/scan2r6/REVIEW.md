# SCAN2R6 — scanner v4.5.5 re-review

**PASS — 0 blocking, 0 high, 0 medium findings; rescan justified 15/15.** Every negative probe from SCAN2R through SCAN2R5 returns VOID, as do three new early-exit/restoration variants. The shared walker applies its barrier before every replay admission, rejection, definition insertion or skip. No rollout was promoted for a reason outside P1–P3.

## Scope and execution

Reviewed offline on 19 October 2026 at HEAD `c9f6c55b2` (`SCAN2F: scanner v4.5.5 (barrier first, unconditional)`). Inspected the last commit against its parent, especially the scanner, HANDOVER, canonical version test and new rescan evidence; read SCAN2R through SCAN2R6 briefs, SCAN2's ruling, all five previous reviews, SCAN2/SCAN2F handoffs, the restricted replay worker, tests/fixtures, and the external `greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md` pattern source.

No network calls, implementation edits, original-pack changes, reader launches, answer scoring, ledger changes or existing receipt writes. This report is the only persistent file written. Tests and additional standard-input harnesses used self-cleaning OS temporary packs and replay directories. The pre-existing modified test files/fixture README and untracked SC45 briefs and overwrite fixtures were preserved. All seven tested-source hashes in `out/scan2f/SOURCE.json` match the current files, including the untracked fixtures used by the suite.

Executed:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**107 tests passed in 119.282 seconds, zero skips.** All six historical witnesses ran. RU1 missing crops were recovered only into temporary manifest-verified snapshots, with `original_pack_unchanged=true`. Existing truth-file/outside/traversal, manifest mismatch, dynamic-load, native mode/pixel/alpha, crop/upscale/distortion, strict MAD boundary and unreplayable-overwrite fixtures pass. CQ1 and RU1 historical expectations remain enforced.

## Barrier and restoration assessment

Locations below are in `docs/harvest/sol_reading/tools/scan_rollout.py`.

- **One walker/cache:** `recorded_helpers()` at lines 421–426 drains `replay_history()` into one path-keyed dictionary. It does not independently extract recorder definitions. `history_commands()` at lines 590–599 uses `independent_units()`; unsupported enclosing syntax is retained as an opaque command rather than mined for executable heredocs.
- **Barrier dominates admission:** every walker iteration at lines 605–610 computes `command_writes()`, snapshots the currently executing source, and calls `invalidate_helpers()`. Only afterward can it insert a definition (611–617), emit mkdir (618–619), accept restricted replay (620–623), skip a rejected inline heredoc (624), exit on malformed argv (625–627), reject unknown/noninteger helper argv (628–630), reject mismatching script bytes (631–633), or parse/emit an expanded helper (634–649). There is no earlier `continue`, yield or admission branch. Shell-unit segmentation and write-effect analysis precede the barrier; replay classification does not.
- **Effects independent of admission:** `command_writes()` at lines 564–577 analyzes helper source regardless of integer-argv eligibility or restricted-worker import acceptance. `python_writes()` at lines 485–561 returns unknown effects for unproven destinations, callbacks, rebinding and unsupported APIs. Unknown effects clear the cache at lines 580–587; proven destinations invalidate normalized targets, conservatively case-folded.
- **Historical source identity:** reproduction passes its fresh filesystem to the walker at line 109. Definitions materialize there at lines 613–616, and exact source bytes are checked before helper use at lines 574 and 631. A self-overwriter can finish using its pre-write source snapshot, but that snapshot is never reinserted. The supplied mismatch test confirms that restoring file bytes alone cannot revive a revoked entry.
- **P1 retains both gates:** lines 429–441 require the complete closed answer argv, historical recorder authority, exact current source bytes and the unchanged recorder AST digest. A new literal definition can restore authority; matching final bytes alone cannot.

Instrumented `command_writes`, `invalidate_helpers` and `parse_replay` in memory across ten command/early-exit cases: literal definition, mkdir, read-only cat, accepted inline image code, helper definition, noninteger helper argv, rejected expanded helper, rejected inline import, missing helper and malformed shell quoting. Each began with effect analysis followed by the barrier, before any replay parser call. The suite additionally covers actual filesystem mismatch and subsequent byte restoration. A separate generator-step check placed rejected helper execution, the answer invocation and a later DEFINE in one shell call: the recorder was absent at both earlier yields and reappeared only after the later definition. Future restoration is not moved backward in history.

**SCAN2R5 H1 is closed.** Both original rejected-helper/final-restoration probes now retain `/n` findings and an exact source-image byte match.

## Prior probe closure matrix

All rows were executed in this review, through `Scan2BProbes`, `Scan2CProbes`, `Scan2EProbes`, `Scan2FProbes`, or additional standard-input harnesses. No outcome below is copied from an earlier execution without rerunning it.

| Origin / negative probe | v4.5.5 |
|---|---|
| SCAN2R H1: false branch around image heredoc | VOID |
| SCAN2R H1: uncalled function around image heredoc | VOID |
| SCAN2R H2: accepted inline image command overwrites helper | VOID |
| SCAN2R H3: unused loop-header `/tmp/outside` | VOID |
| SCAN2R H3: unused loop-header `../truth.json` | VOID |
| SCAN2R2 additional H1: `while false; do` | VOID |
| SCAN2R2 additional H1: `false &&` | VOID |
| SCAN2R2 H1 A: second helper overwrites batch helper | VOID |
| SCAN2R2 H1 B: self-overwrite, blue overwrite, stale reinvocation | VOID |
| SCAN2R2 additional H3: unused loop-header `/n` | VOID |
| SCAN2R2 additional H3: unused loop-header `../outside` | VOID |
| SCAN2R3: computed batch target `'zoom/'+'batch.py'` | VOID |
| SCAN2R3: keyword/normalized self target `fp='zoom//batch.py'` | VOID |
| SCAN2R3: combined unused loop paths and two exact returns | VOID |
| SCAN2R3 H1: computed recorder overwrite | VOID |
| SCAN2R3 H1: recorder definition inside false branch | VOID |
| SCAN2R4: recorder overwrite through variables | VOID |
| SCAN2R4: recorder overwrite through second helper | VOID |
| SCAN2R4: recorder overwrite inside literal loop | VOID |
| SCAN2R5 A: noninteger-argv overwriter, then final restoration | VOID |
| SCAN2R5 B: rejected-import overwriter, then final restoration | VOID |

Also reran SCAN2R3's exploratory `fp='./zoom//batch.py'`: VOID, with path and image findings. Missing/changed/no-final-newline recorder, uncalled recorder-definition function and recorder heredoc embedded in a Python string also remain rejected by the suite.

## Three new early-exit/restoration variants

These use `Pack`, `DEFINE`, `RECORDER`, `call`, `exe`, `view` and `returned` from `tests/test_scan_rollout.py`. Each starts with DEFINE, records the mutation sequence below, invokes `python3 zoom/record.py 'r?/n'`, then records DEFINE again **after** that invocation. The final reader file contains exactly `(RECORDER+'\n').encode()`. Each ends with an exact `img/source.png` view/return, excluding image provenance as the cause of rejection.

**N1 — unsupported shell operator before final restoration.** Define `zoom/kill.py` as:

```python
from PIL import Image
Image.new('RGB',(1,1)).save('zoom/record.py',format='PNG')
```

Invoke `python3 zoom/kill.py 0; :`. The enclosing command is outside the independent-unit grammar, so its effects are unknown and the cache clears before the unsupported-command exit. **VOID**, retaining the answer invocation's `/n` outside-path finding. Ordinary synthetic shell execution succeeds and leaves a 69-byte PNG before final DEFINE restores the recorder.

**N2 — rejected inline Path.open before final restoration.** Record this inline Python heredoc:

```python
from pathlib import Path
p=Path('zoom/record.py')
p.open('w').close()
```

The worker rejects this code; its possible truncation still revokes authority before the inline-heredoc skip. **VOID**, retaining `/n`. Ordinary synthetic shell execution succeeds and leaves a zero-byte recorder before final restoration.

**N3 — rejected helper internally restores exact bytes.** Define `zoom/kill.py` with the following body, substituting `repr(RECORDER+'\n')` as the literal argument to `write_text`:

```python
from pathlib import Path
p=Path('zoom/record.py')
p.open('w').close()
p.write_text(<literal original recorder source including final newline>)
```

Invoke `python3 zoom/kill.py label`. Its argv is noninteger and its body is outside replay admission. The unknown-effect barrier revokes authority even though ordinary Python truncates and then restores the exact source before the answer. **VOID**, retaining `/n`; byte equality does not repopulate the cache. Synthetic shell execution confirms the intermediate final bytes equal the 778-byte recorder source. This is the conservative restoration-policy witness, rather than a claim that the restored script itself is invalid.

For all three, direct prefix checks confirm `recorded_helpers()` lacks `zoom/record.py` and `answer_data()` leaves the answer command unchanged. Appending a new literal DEFINE restores the exemption. Actual synthetic shell mutation/restoration commands all exit zero; final DEFINE restores the exact expected bytes. These executions were confined to temporary packs.

## P1–P3 and independent rescan

**P1:** closed answer-atom/full-argv grammar and AST pin remain unchanged. Real `/n`, `/tmp/outside`, `../truth.json`, invalid/mixed atoms, shell additions and changed-source negatives fail. Independently walked `wcap_initial_001`'s command history and confirmed the pinned source/grammar exemption at records **40, 78, 116 and 124**. Those four commands account for all **eight** removed v4.4 path findings.

**P2:** lines 58–84 retain per-axis non-upscaling, intersecting common-scale intervals with ≤1-pixel rounding, named standard resampling filters, strict RGB MAD `<2.0` in byte units (equivalent to `<2/255`), and opaque alpha. Native same-size mode/pixels remain exact. For each previously flagged image ordinal, independently decoded original returned image blocks and matched them to manifest-verified reconstruction receipts: **64 removed image findings = 47 resized + 17 exact**. Companion original-image returns were excluded. All 47 resized returns satisfy opacity, common-scale/non-upscaling and receipt dimensions; maximum accepted MAD is **0.4761051364434188/255**. All 17 exact reconstruction receipts report exact mode/size/pixels. Crop/upscale/distortion and strict-boundary fixtures pass.

**P3:** finite literal loops/ranges, output order, literal integer helper argv, independent mkdir/image heredocs and 19 overwritten batch snapshots remain qualified. Compared the saved v4.5.5 and v4.5.4 evidence: all non-command image evidence is identical. All **64** reconstruction command lists differ in representation, but their normalized replayed mkdir/Python AST effects, return codes and stderr are identical; grouping/skipped-definition bookkeeping does not introduce another admission rule.

Independently reran `inspect()` on **all 15 original rollouts**, with manifest checks enabled and at most three concurrent scans. Verified each rollout SHA-256 and parent-manifest SHA-256 against `rescan_v455.json`. Every result is VALID and exactly equals its saved v4.5.5 receipt on `ok`, `violations`, complete `image_matches` including reconstruction commands/evidence, `image_match_counts` and `loop_expansions`. Comparisons stayed in memory; existing outputs were not regenerated.

Verified all **22 protected CQ4 hashes**. Across those files, all SCAN2 JSON evidence and the scanner, **105 file hashes remained unchanged before/after the independent rescan**.

| Rollout | Removed v4.4 findings | Justification within P1–P3 |
|---|---:|---|
| wcap_initial_000 | 1 image | P2 resize; P3 literal array at 62 |
| wcap_initial_001 | 3 image + 8 path | P2 resizes; P1 pinned-recorder answer argv |
| wcap_initial_002 | 5 image | P2 resizes; P3 independent image heredoc at 131 |
| wcap_initial_003 | 3 image | P2 resizes |
| topup_initial_002 | 5 image | P2 resizes; P3 literal range at 56 |
| topup_initial_003 | 3 image | P2 resizes |
| topup_initial_004 | 20 image | P3 helper/literal argv and historical snapshots; P2 for 3 resizes, plus 17 exact returns |
| topup_initial_005 | 1 image | P2 resize; P3 literal array at 62 |
| topup_initial_006 | 6 image | P2 resizes; P3 mkdir at 19 and image isolation at 174 |
| topup_initial_007 | 2 image | P2 resizes; P3 literal arrays and independent units at 52 |
| topup_initial_008 | 1 image | P2 resize; P3 literal range at 99 and setup isolation at 19 |
| topup_initial_009 | 5 image | P2 resizes; P3 mkdir at 19 and image isolation at 166 |
| topup_initial_010 | 5 image | P2 resizes |
| topup_initial_011 | 2 image | P2 resizes; P3 independent image heredoc at 171 |
| topup_initial_012 | 2 image | P2 resizes; P3 independent image heredoc at 176 |

All rows remain VOID → VALID with zero remaining findings. **Promoted outside P1–P3: none found; 15/15 justified.** This audits recorded inputs/outputs and does not score reader answers or establish OS isolation.

## Canonical identity

The actual scanner, `docs/harvest/sol_reading/HANDOVER.md:102`, `out/scan2f/HANDOFF.md` and `out/scan2/rescan_v455.json` agree on version 4.5.5 and SHA-256:

```text
e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1
```

No blocking, high or medium findings remain in the reviewed scope.

SCAN2R6: PASS | blocking 0 | high 0 | medium 0 | rescan justified 15/15
