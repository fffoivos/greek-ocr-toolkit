# SCAN2R4 — requested v4.5.3 re-review

**FAIL — 1 blocking, 1 high, 0 medium findings.** The requested v4.5.3 implementation is absent. The available canonical scanner is byte-for-byte v4.5.2 and retains SCAN2R3 H1. Both original recorder probes and all three requested new overwrite variants incorrectly return VALID. Earlier image-replay and loop/path probes remain closed. The 15 historical verdicts of the available scanner are independently justified by P1–P3 only; this does not qualify an unavailable v4.5.3 candidate.

## Scope and verification

Reviewed offline on 19 October 2026 at HEAD `d707758af4534909a0098472318d8e898819f779` (`SCAN2D/SCAN2R4 briefs`). Its diff against its parent contains only the two briefs. Read the SCAN2R/R2/R3/R4 criteria, SCAN2 ruling, SCAN2D structural-fix brief, all three prior reviews, implementation handoffs, HANDOVER, scanner/tests/fixtures, saved rescans and external `greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md` pattern source. The latest scanner implementation remains the SCAN2C change, not a SCAN2D implementation.

No network calls, implementation edits, reader launches, scoring, ledger changes or existing receipt writes. This report is the only persistent output. Synthetic packs, replay workers and witness recovery used self-cleaning OS temporary directories. All probes were supplied through in-memory/standard-input harnesses; no probe script was saved. Pre-existing changes to `tests/test_scan_rollout.py`, untracked `tests/fixtures/v45/helper_overwrites.json` and two untracked SC45 briefs were preserved.

Executed the full supplied suite:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**98 tests passed in 112.346 seconds, zero skips.** Both `Scan2BProbes` and `Scan2CProbes` ran, as did all six historical witnesses. The RU1 witness recovery reported manifest-verified temporary snapshots and unchanged original packs. Truth/outside/traversal, dynamic loads, manifest mismatches, native mode/pixel/alpha, crop/upscale/distortion and unreplayable-overwrite regressions pass. Passing these existing tests does not close the recorder probes below, which are absent from the suite.

## Blocking finding

### B1 — The requested v4.5.3 candidate and structural design have not been delivered

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:88`; independent caches at `:414` and `:489`; `docs/harvest/sol_reading/HANDOVER.md:100`.

The file declares `VERSION='4.5.2'`, with SHA-256:

```text
7b3647162c527426225f26b3c8eba494fb89b52302002594eb0b8246e5642f4e
```

This exactly equals the prior SCAN2R3-reviewed file, the current HANDOVER digest and `out/scan2/rescan_v452.json`. Neither `out/scan2d/HANDOFF.md` nor `out/scan2/rescan_v453.json` exists. There is no scanner diff in the current HEAD commit. `recorded_helpers()` and `replay_history()` still create separate dictionaries, and the P1 path never enters the replay write barrier. The requested shared cache, single barrier and current-content validation therefore cannot be certified. This is an unavailable review subject, not merely a forgotten version-string update.

Required resolution: deliver the SCAN2D implementation and its actual identity/qualification artifacts before claiming v4.5.3 acceptance. No implementation was attempted in this read-only review.

## High finding

### H1 — SCAN2R3 H1 remains open: P1 exempts answer atoms using stale or nonexecuting recorder source

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:413–419`, consumed at `:428–432`; compare the separate replay barriers at `:502`, `:514` and `:542`.

`recorded_helpers()` extracts heredocs from arbitrary enclosing shell contexts and invalidates cached source only when the complete path appears textually in a subsequent command. It neither uses `independent_units()` nor applies `invalidate_helpers()`. `answer_data()` then trusts the old AST digest and replaces the answer argv with `ANSWER_DATA`, suppressing the ordinary `/n` path finding. No comparison with the recorder's historical current bytes occurs.

All five recorder probes below return **`ok: true`, `violations: []`**, and a direct call to `answer_data()` returns **`python3 zoom/record.py ANSWER_DATA`**. Each image-bearing probe returns the exact manifest source, with no image-provenance ambiguity. Expected outcome: VOID, because the pinned recorder either never existed or has been overwritten.

Reproduction uses `Pack`, `DEFINE`, `call`, `exe`, `view` and `returned` from `tests/test_scan_rollout.py`. `DEFINE` is the exact audited recorder heredoc. For each overwrite history, record `DEFINE`, the indicated overwrite command(s), then:

```python
call("python3 zoom/record.py 'r?/n'"),
exe(view('img/source.png')), returned(p.source)
```

**New variant 1 — computed target through variables:**

```sh
python3 - <<'PY'
from PIL import Image
base='zoom/'
name='record.py'
target=base+name
Image.new('RGB',(1,1)).save(target,format='PNG')
PY
```

**New variant 2 — overwrite through a second helper:** record the following definition and invocation as separate calls:

```sh
cat > zoom/kill.py <<'PY'
from PIL import Image
target='zoom/'+'record.py'
Image.new('RGB',(1,1)).save(target,format='PNG')
PY
python3 zoom/kill.py 0
```

**New variant 3 — overwrite inside a literal loop:**

```sh
python3 - <<'PY'
from PIL import Image
for name in ['record.py']:
    target='zoom/'+name
    Image.new('RGB',(1,1)).save(target,format='PNG')
PY
```

The variable and loop commands pass the restricted replay parser. Separately executed each of the three fully specified overwrite histories in a fresh temporary synthetic pack: every command exited 0 and left `zoom/record.py` as a 69-byte PNG, rather than the pinned Python source. The scanner nevertheless grants the exemption. The second-helper body uses only the supported image operations and literal integer invocation.

Also independently loaded the unchanged v4.4 scanner from `c21b21565^` into memory, verifying SHA-256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`. Both original SCAN2R3 recorder histories and all three new histories return VOID there, each retaining the two duplicated `/n` outside-path findings. Thus these VALID outcomes exceed the pinned-recorder authority granted by P1. This demonstrates an exemption bypass, not an observed truth-file leak. All five manifestations are counted as one high finding.

Required resolution: bind P1 and P3 to the same path-keyed source authority, execution-context validation and conservative mutation barrier, including expanded helper writes, computed targets and literal-loop writes. Enforce the requested current-source identity condition before invocation. Retain the AST pin and complete closed answer grammar.

## Closure matrix: all prior probes and requested variants

The seven concrete SCAN2R/SCAN2R2 core negatives ran in the supplied suite; the remaining twelve concrete cases ran in the additional in-memory harness. No expected negative below was inferred solely from an old report.

| Origin / probe | Available scanner outcome | Assessment |
|---|---|---|
| SCAN2R H1: false branch around image heredoc | VOID | Closed |
| SCAN2R H1: uncalled function around image heredoc | VOID | Closed |
| SCAN2R H2: accepted inline image command overwrites helper | VOID | Closed |
| SCAN2R H3: unused loop-header `/tmp/outside` | VOID | Closed |
| SCAN2R H3: unused loop-header `../truth.json` | VOID | Closed |
| SCAN2R2 additional H1: `while false; do` | VOID | Closed |
| SCAN2R2 additional H1: `false &&` | VOID | Closed |
| SCAN2R2 H1 A: second helper overwrites batch helper | VOID | Closed in P3 |
| SCAN2R2 H1 B: self-overwrite, blue overwrite, stale reinvocation | VOID | Closed in P3 |
| SCAN2R2 additional H3: unused loop-header `/n` | VOID | Closed |
| SCAN2R2 additional H3: unused loop-header `../outside` | VOID | Closed |
| SCAN2R3 computed batch target `'zoom/'+'batch.py'` | VOID | Overwriter replays; stale invocation skipped |
| SCAN2R3 keyword/normalized self target `fp='zoom//batch.py'` | VOID | Surviving image is 1×1 blue; stale invocation skipped |
| SCAN2R3 combined unused loop paths, two exact returns | VOID | Path findings retained |
| SCAN2R3 computed recorder overwrite | **VALID** | H1 remains open |
| SCAN2R3 recorder definition inside false branch | **VALID** | H1 remains open |
| SCAN2R4 recorder overwrite through variables | **VALID** | H1 |
| SCAN2R4 recorder overwrite through second helper | **VALID** | H1 |
| SCAN2R4 recorder overwrite inside literal loop | **VALID** | H1 |

The exact earlier image-replay fixes remain effective; the separate P1 authority is still unprotected. Every finding across SCAN2R/R2/R3 is therefore **not** closed by the requested design.

## P1–P3 qualification and 15-rollout rescan

P1's complete closed atom grammar, full argv parsing and AST digest remain restricted on their supplied fixtures; real `/n`, `/tmp/outside`, `../truth.json`, invalid/mixed atoms and changed-helper negatives fail. Historical recorder identity is the outstanding limitation. The eight removed historical path findings occur only on the four authorized answer commands at records 40, 78, 116 and 124 of `wcap_initial_001`; the failing synthetic recorder histories do not occur there.

P2 retains strict RGB MAD `<2.0` in byte units, equivalent to `<2/255`, named standard filters, no growth on either axis, intersection of the two ≤1-pixel scale intervals and opaque alpha for resized returns. Native same-size comparisons remain exact. Independently decoded the original image blocks for all 64 removed v4.4 image findings: **47 resized returns** satisfy opacity/common-scale/non-upscaling dimensions, and **17 exact returns** have exact reconstructed pixels. All are manifest-seeded reconstructions. Maximum first-accepted-filter MAD is **0.4761051364434188/255**. Crop/upscale/distortion and strict MAD-boundary negatives pass.

P3's finite literal arrays/ranges, output order, literal helper argv, 19 historical overwritten batch snapshots, independent image heredocs and mkdir preservation pass. Its earlier overwrite probes remain VOID as shown above. No additional rescan exception was introduced in the available file.

Independently reran `inspect()` on **all 15 original rollouts**, with manifest checks enabled and at most three concurrent scans. Verified every rollout and parent-manifest SHA-256 against the saved summary, and every saved v4.5.2 receipt against its recorded hash. Every result is VALID and exactly equals the saved receipt on `ok`, `violations`, `image_matches` including reconstruction evidence, `image_match_counts` and `loop_expansions`. For each formerly flagged output ordinal, seeded reconstruction matches account for exactly the number of removed image findings, excluding already-matching companion returns: **64 = 47 resized + 17 exact**.

Verified all 22 protected CQ4 file hashes against `cq4_receipts_sha256.json`. Across those files, existing SCAN2 JSON outputs and the scanner, **73 file hashes remained unchanged before/after replay**. Results were compared in memory; no saved rescan or receipt was regenerated.

All rows below remain VOID → VALID, with zero remaining findings:

| Rollout | Removed v4.4 findings | P1–P3 justification |
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

**Promoted outside P1–P3: none found; 15/15 justified for the available v4.5.2 scanner.** No reader answers were accepted or scored. HANDOVER matches that actual v4.5.2 file; there is no v4.5.3 identity to verify.

SCAN2R4: FAIL | blocking 1 | high 1 | medium 0 | rescan justified 15/15
