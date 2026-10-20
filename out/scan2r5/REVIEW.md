# SCAN2R5 — scanner v4.5.4 re-review

**FAIL — 0 blocking, 1 high, 0 medium findings.** The v4.5.4 candidate is present, all 105 supplied tests pass, and every earlier SCAN2R/R2/R3/R4 negative probe returns VOID. The requested two new recorder-cache variants both incorrectly return VALID. P1 now shares the replay walker's cache and barrier implementation, but rejected helper invocations still bypass that barrier. Comparing final on-disk bytes cannot establish the recorder's identity at an earlier invocation.

## Scope and verification

Reviewed offline on 19 October 2026 at HEAD `4b8652918` (`SCAN2E: scanner v4.5.4`). Read the SCAN2R through SCAN2R5 briefs, SCAN2 ruling, SCAN2E fix brief/handoff, all four prior reviews, external `greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md`, scanner, restricted worker, tests/fixtures, HANDOVER and saved rescan evidence. Inspected `git diff HEAD^ HEAD`, including the scanner's 32-line change.

No network calls, implementation edits, reader launches, answer scoring, ledger changes or existing receipt writes. This report is the only persistent output written. Synthetic packs, actual shell reproductions and witness recovery used self-cleaning OS temporary directories. Additional probes and rescans ran from standard-input Python harnesses; no script was saved. Pre-existing modified `tests/test_scan_rollout.py`, untracked helper/recorder-overwrite fixtures and two untracked SC45 briefs were preserved and included where applicable.

Executed:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**105 tests passed in 106.349 seconds, zero skips.** All six historical witnesses ran. RU1 recovery used manifest-verified temporary snapshots and reported original packs unchanged. Truth/outside/traversal, dynamic loads, manifest mismatches, native mode/pixel/alpha, crop/upscale/distortion, strict MAD boundary and unreplayable-overwrite regressions pass.

## High finding

### H1 — Rejected helper invocations retain stale recorder authority; final restoration defeats the byte check

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:528` and `:543`, before the barrier at `:546`; consumed by P1 at `:427` and `:431`.

`replay_history()` skips a known helper immediately when its argv is not all literal integers. It also skips an expanded helper when `parse_replay()` rejects its body. Neither exit calls `invalidate_helpers()` or clears the other cached scripts. Such a helper still executes in the recorded shell history and can overwrite `zoom/record.py`. `recorded_helpers()` consequently retains the pinned recorder source. P1 compares that stale source with the final reader directory, so a later restoration of the recorder hides its invalid state at the answer invocation.

The following are two variants of this single missing-invalidation finding. Both use `Pack`, `DEFINE`, `RECORDER`, `call`, `exe`, `view` and `returned` from `tests/test_scan_rollout.py`. `DEFINE` is the exact pinned recorder heredoc. Record these five calls separately, in order:

1. `DEFINE`.
2. The `zoom/kill.py` definition below.
3. The indicated invocation of `zoom/kill.py`.
4. `python3 zoom/record.py 'r?/n'`.
5. `DEFINE` again, restoring the recorder **after** the answer invocation.

Then record `exe(view('img/source.png'))` and `returned(p.source)`. The final `zoom/record.py` must contain exactly `(RECORDER+'\n').encode()`, consistent with the last recorded restoration.

**New variant A — noninteger helper argv bypasses the barrier at line 528:**

```sh
cat > zoom/kill.py <<'PY'
from PIL import Image
Image.new('RGB',(1,1)).save('zoom/record.py',format='PNG')
PY
```

Invoke it with `python3 zoom/kill.py label`. The body is otherwise replayable and does not use its argv. The closed shell-unit grammar accepts this invocation, but the integer-only replay gate skips it before checking its writes.

**New variant B — unsupported helper import bypasses the barrier at line 543:**

```sh
cat > zoom/kill.py <<'PY'
from PIL import Image,ImageOps
Image.new('RGB',(1,1)).save('zoom/record.py',format='PNG')
PY
```

Invoke it with `python3 zoom/kill.py 0`. Ordinary Python accepts the unused `ImageOps` import and performs the overwrite. The restricted worker rejects that import, and the exception branch skips the invocation without revoking recorder authority. Inline rejected Python already clears the cache; this expanded-helper branch does not.

**Observed for each variant:** v4.5.4 returns `ok: true`, `violations: []`, `image_match_counts: {"bytes": 1}`. After the first three commands, `recorded_helpers()` still contains both `zoom/record.py` and `zoom/kill.py`. With the final restored source on disk, `answer_data()` rewrites the answer command to `python3 zoom/record.py ANSWER_DATA`.

Separately executed the exact setup, helper definition and invocation through `/bin/sh` in fresh synthetic packs: every command exited 0 and left `zoom/record.py` as a **69-byte PNG**. The answer invocation then exited **1**. The final `DEFINE` exited 0 and restored the exact pinned source bytes. Thus this is a consistent recorded history and final filesystem, rather than reliance on an unexplained matching final file.

Independently loaded the unchanged v4.4 scanner in memory and verified SHA-256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`. Both identical rollouts return **VOID** there, retaining two `/n` outside-path findings at record 3. The image matches the manifest source exactly, so image provenance does not explain either rejection or erroneous promotion.

**Expected:** VOID. The answer command did not invoke the audited recorder at that point in history; a later restoration cannot authorize its earlier argv exemption. This demonstrates a P1 authority bypass, not an observed truth-file leak.

**Required correction:** route every possible helper execution through conservative mutation invalidation, including noninteger-argv and rejected-body branches. If its writes cannot be established, revoke affected authority or clear the cache before continuing. Keep execution admission separate from mutation uncertainty, preserve the closed argv/AST pin, and add both histories with the post-invocation restoration as negative fixtures. No correction was implemented in this review.

## Requested structure and closure matrix

`recorded_helpers()` at lines 413–418 now creates a path-keyed dictionary and drains `replay_history(history, helpers)`. It no longer independently extracts heredocs or applies textual invalidation. The shared walker calls `independent_units()` at line 495, admits definitions at 511–512, and invokes the same `invalidate_helpers()` implementation for accepted whole-command, isolated inline and expanded-helper replay at 506, 518 and 546. Unknown enclosing shell syntax clears the cache at 498. All three P1 callers pass `directory`; the exact source-byte check and recorder AST digest remain in place.

**Structural assessment:** the requested shared cache/walker policy is present, with one dictionary per walk and one write-barrier implementation. The claim that all possible mutations cross that barrier is false at the two exits demonstrated above. The exact earlier failures are closed; the general authority guarantee remains incomplete.

Every row below was rerun in this review, through the supplied suite or an additional in-memory harness. No negative outcome was inferred solely from an earlier report.

| Origin / probe | v4.5.4 | Assessment |
|---|---|---|
| SCAN2R H1: false branch around image heredoc | VOID | Closed |
| SCAN2R H1: uncalled function around image heredoc | VOID | Closed |
| SCAN2R H2: accepted inline command overwrites batch helper | VOID | Closed |
| SCAN2R H3: unused loop-header `/tmp/outside` | VOID | Closed |
| SCAN2R H3: unused loop-header `../truth.json` | VOID | Closed |
| SCAN2R2 additional H1: `while false; do` | VOID | Closed |
| SCAN2R2 additional H1: `false &&` | VOID | Closed |
| SCAN2R2 H1 A: second helper overwrites batch helper | VOID | Closed |
| SCAN2R2 H1 B: self-overwrite, blue overwrite, stale reinvocation | VOID | Closed |
| SCAN2R2 additional H3: unused loop-header `/n` | VOID | Path finding retained |
| SCAN2R2 additional H3: unused loop-header `../outside` | VOID | Traversal/outside findings retained |
| SCAN2R3 computed batch target `'zoom/'+'batch.py'` | VOID | Stale invocation skipped |
| SCAN2R3 keyword/normalized self target `fp='zoom//batch.py'` | VOID | Stale invocation skipped; surviving image 1×1 blue |
| SCAN2R3 combined unused loop paths, two exact returns | VOID | Path findings retained |
| SCAN2R3 computed recorder overwrite | VOID | Cached recorder revoked despite matching final source |
| SCAN2R3 recorder definition inside false branch | VOID | Definition not admitted |
| SCAN2R4 recorder overwrite through variables | VOID | Cache cleared |
| SCAN2R4 recorder overwrite through second helper | VOID | Cache cleared |
| SCAN2R4 recorder overwrite inside literal loop | VOID | Cache cleared |
| New A: recorder overwrite through noninteger-argv helper, then final restoration | **VALID** | H1 |
| New B: recorder overwrite through rejected-import helper, then final restoration | **VALID** | H1 |

Also reran SCAN2R3's exploratory `fp='./zoom//batch.py'` spelling: VOID, with both path and unmatched-image findings. The supplied new tests also reject a missing/changed/no-final-newline recorder, an uncalled recorder-definition function and a recorder heredoc embedded in a Python string. These additional checks pass.

## P1–P3 and rescan adjudication

P1 retains the complete closed answer-atom grammar and AST pin, with negative fixtures for real `/n`, `/tmp/outside`, `../truth.json`, invalid/mixed atoms, shell additions and changed source. The historical eight removed path findings belong only to records 40, 78, 116 and 124 of `wcap_initial_001`, whose pinned recorder and answer atoms qualify. The new rejected-overwriter/restoration histories do not occur there.

P2 retains a common non-upscaling scale with intersecting per-axis ≤1-pixel intervals, strict RGB MAD `<2.0` in byte units (equivalent to `<2/255`), named standard resampling filters and opaque alpha. Native same-size mode/pixel comparison remains exact. Crop/upscale/distortion, transparency and strict-boundary negatives pass.

P3 retains finite literal array/range expansion, output ordering, literal integer helper argv, independent mkdir preservation and image-heredoc isolation. Inspected the accepted reconstruction save targets across all 15 saved receipts: they are PNG outputs under `zoom/`, including literal, f-string and percent-formatted batch names. The 19 overwritten batch snapshots remain historical reconstructions. No new rescan exception appears in the scanner diff.

Independently reran `inspect()` on **all 15 original rollouts**, with manifest checking enabled and at most three concurrent scans. Verified rollout and parent-manifest SHA-256 values against `rescan_v454.json` before replay. Every result is VALID and exactly matches both the saved v4.5.4 and v4.5.2 receipts on `ok`, `violations`, complete `image_matches` including reconstruction evidence, `image_match_counts` and `loop_expansions`. Comparisons remained in memory; no rescan output was regenerated.

For every old image-finding output ordinal, bound the original returned image blocks to the new matches and excluded already-matching companion originals. Manifest-seeded reconstructions account for exactly **64 removed image findings: 47 resized + 17 exact**. Independently decoded all these returned images. The 47 resized returns satisfy opaque alpha, common-scale/non-upscaling dimensions and receipt dimensions; their accepted RGB MAD values are strictly below 2, with maximum **0.4761051364434188/255**. All 17 exact reconstructed returns have exact mode/size/pixels. The eight removed path findings are the four duplicated P1 answer-command findings described above.

Verified all **22 protected CQ4 hashes** against `cq4_receipts_sha256.json`. Across those files, all existing SCAN2 JSON files and the scanner, **89 file hashes remained unchanged before/after replay**.

All rows below remain VOID → VALID with zero remaining findings:

| Rollout | Removed v4.4 findings | Justification within P1–P3 |
|---|---:|---|
| wcap_initial_000 | 1 image | P2 resize; P3 literal array at record 62 |
| wcap_initial_001 | 3 image + 8 path | P2 resizes; P1 pinned-recorder answer argv |
| wcap_initial_002 | 5 image | P2 resizes; P3 independent image heredoc at 131 |
| wcap_initial_003 | 3 image | P2 resizes |
| topup_initial_002 | 5 image | P2 resizes; P3 literal range at 56 |
| topup_initial_003 | 3 image | P2 resizes |
| topup_initial_004 | 20 image | P3 helper/literal argv and historical snapshots; P2 for 3 resizes, plus 17 exact returns |
| topup_initial_005 | 1 image | P2 resize; P3 literal array at 62 |
| topup_initial_006 | 6 image | P2 resizes; P3 mkdir at 19 and independent image unit at 174 |
| topup_initial_007 | 2 image | P2 resizes; P3 literal arrays and independent units at 52 |
| topup_initial_008 | 1 image | P2 resize; P3 literal range at 99 and setup isolation at 19 |
| topup_initial_009 | 5 image | P2 resizes; P3 mkdir at 19 and independent image unit at 166 |
| topup_initial_010 | 5 image | P2 resizes |
| topup_initial_011 | 2 image | P2 resizes; P3 independent image heredoc at 171 |
| topup_initial_012 | 2 image | P2 resizes; P3 independent image heredoc at 176 |

**Promoted outside P1–P3: none found; 15/15 justified.** This does not accept or score reader answers and does not waive H1.

## HANDOVER identity

The actual scanner, `docs/harvest/sol_reading/HANDOVER.md:102`, `out/scan2e/HANDOFF.md` and `out/scan2/rescan_v454.json` agree on SHA-256:

```text
c3abc4c7a2bcb16afc8ba2345d384d0935476f353cc27ded4cd595864bf4d844
```

The candidate is available and its version is `4.5.4`; SCAN2R4's unavailable-candidate blocking finding is closed.

SCAN2R5: FAIL | blocking 0 | high 1 | medium 0 | rescan justified 15/15
