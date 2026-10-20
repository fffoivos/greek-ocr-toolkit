# SCAN2R3 — scanner v4.5.2 re-review

**Verdict: FAIL — 0 blocking, 1 high, 0 medium findings.** All 98 supplied tests pass. SCAN2R's five concrete image-replay/path probes and both SCAN2R2 helper-overwrite probes now return VOID, as do the three requested new variants. However, P1's separate recorder-history implementation still admits nonexecuting definitions and stale overwritten source: two additional negative probes incorrectly return VALID. The 15 historical rescan verdicts remain justified by P1–P3 only.

## Scope and execution

Reviewed offline on 19 October 2026 at HEAD `ee274e6d2`; inspected its scanner diff against its parent, the SCAN2R/SCAN2R3 review criteria, prior reviews, SCAN2/SCAN2B/SCAN2C rulings and handoffs, HANDOVER, and the external `greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md` pattern source. No network tools or network commands were used.

The working tree already contained modified `tests/test_scan_rollout.py`, untracked `tests/fixtures/v45/helper_overwrites.json`, and two untracked SC45 briefs. These were preserved. The test edits add `Scan2BProbes` and `Scan2CProbes`; both classes were included in verification. Synthetic packs, witness recovery and replay workers used self-cleaning OS temporary directories. This report is the only persistent file written by the review; implementation, original packs, rollouts, ledgers and existing receipts were not edited.

Executed:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**98 tests passed in 102.832 seconds, zero skips.** All six historical witnesses ran, including CQ1 and RU1. Missing RU1 crops were recovered only into temporary manifest-verified snapshots; the harness reports original packs unchanged. Truth/outside/traversal, dynamic loads, manifest mismatches, native mode/pixel/alpha, crop/upscale/distortion, and unreplayable-overwrite regression fixtures pass.

## High finding

### H1 — P1 trusts a separate recorder cache without execution-context or write invalidation

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:413–419`, consumed by `:428–432`.

`recorded_helpers()` still extracts definitions with `HEREDOC.finditer()` from arbitrary shell contexts. It invalidates a recorder only when its complete filename appears textually in a later command. It does not use `independent_units()` or the conservative replay write barrier. Consequently, `answer_data()` can pin an obsolete or never-executed recorder AST and erase `/n` from subsequent path inspection. The fixes to `replay_history()` do not protect this separate P1 authority path.

**Probe A: computed overwrite of the pinned recorder.** Using `Pack`, `call`, `exe`, `view`, `returned` and `DEFINE` from `tests/test_scan_rollout.py`, run this in-memory harness (with normal `setUp()`/`tearDown()`):

```python
overwrite = """python3 - <<'PY'
from PIL import Image
target='zoom/'+'record.py'
Image.new('RGB',(1,1)).save(target,format='PNG')
PY"""
r = p.scan(
    call(DEFINE), call(overwrite),
    call("python3 zoom/record.py 'r?/n'"),
    exe(view('img/source.png')), returned(p.source),
)
```

`DEFINE` is the exact pinned recorder definition already used by the positive fixtures. The overwrite is a confined image command and replaces the real recorder with PNG bytes. Its command text does not contain the contiguous filename `zoom/record.py`, so `recorded_helpers()` retains the original Python. At the invocation the recorder is no longer the pinned helper.

**Observed v4.5.2:** `ok: true`, `violations: []`, `image_match_counts: {"bytes": 1}`. Calling `answer_data()` directly on the first two history entries yields `python3 zoom/record.py ANSWER_DATA`. Independently loaded the v4.4 scanner from `c21b21565^` into memory, verified SHA-256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`, and scanned the identical rollout: **VOID**, with two outside-path `/n` findings at record 2.

**Probe B: recorder definition in a false branch.** Record `call('if false; then\n' + DEFINE + '\nfi')`, then `call("python3 zoom/record.py 'r?/n'")`. **Observed v4.5.2:** `ok: true`, `violations: []`. The definition never executes, but its AST still authorizes the exemption.

**Expected:** both remain VOID under the review's pinned-recorder requirement. Closed answer atoms alone are insufficient: the P1 exemption is restricted to the pack's audited recorder, whose historical identity has not been established in either history. These probes demonstrate an authorization bypass, not an observed truth-file leak. They are two manifestations of one unguarded recorder-history authority, counted as one high finding.

**Required correction:** apply execution-context validation and conservative mutation invalidation to P1's recorder authority as well as P3 replay. Preserve the recorder AST pin and complete closed-argv grammar. Add both negative histories. No fix was implemented in this read-only review.

## Requested closure probes

The five original concrete probes ran through `Scan2BProbes`; the two SCAN2R2 probes ran through `Scan2CProbes`. Three additional variants ran from an in-memory harness using the same synthetic pack.

| Probe | v4.5.2 outcome | Evidence / assessment |
|---|---|---|
| SCAN2R H1: false branch around image heredoc | VOID | Original negative passes |
| SCAN2R H1: uncalled function around image heredoc | VOID | Original negative passes |
| SCAN2R H2: accepted inline command overwrites batch helper | VOID | Original negative passes |
| SCAN2R H3: unused loop-header `/tmp/outside` | VOID | Original path finding retained |
| SCAN2R H3: unused loop-header `../truth.json` | VOID | Original path finding retained |
| SCAN2R2 H1 A: helper overwrites another helper | VOID | Stale invocation skipped; reproduced view missing |
| SCAN2R2 H1 B: self-overwrite, blue image overwrite, stale reinvocation | VOID | Stale invocation skipped; surviving image is 1×1 blue |
| New helper variant: overwrite target assigned as `'zoom/'+'batch.py'` | VOID | Overwriter executes with return code 0; unknown computed target clears cached helpers; final invocation skipped |
| New self variant: `save(fp='zoom//batch.py', format='PNG')` | VOID | Overwriter executes with return code 0; normalized keyword target invalidates self; final invocation skipped; surviving image 1×1 blue |
| New loop/path variant: unused header `["../truth.json","/tmp/outside"]`, two exact source returns | VOID | Both images match bytes; traversal/forbidden and outside-path findings survive expansion |

The new helper variants modify the corresponding histories in `tests/fixtures/v45/helper_overwrites.json`, retaining all other commands and the 360×240 requested image. The final normalized self variant has exactly one unmatched-image finding, so an unrelated path diagnostic is not responsible for rejection. An exploratory `./zoom//batch.py` spelling also returned VOID but additionally produced a literal-path finding; it is not used as the clean closure witness.

**Closure assessment:** the exact SCAN2R H1–H3 and SCAN2R2 H1 probes are closed in the image-replay/loop paths. `replay_history()` validates enclosing shell units at lines 491–496 and invalidates sources for whole-command, isolated inline and expanded-helper replay at lines 502, 514 and 542. Computed targets clear the cache; literal paths normalize before removal. Original loop literals remain subject to path inspection. This does not close the analogous, newly demonstrated P1 recorder-history gap above.

## P1–P3 and per-rollout adjudication

P1's complete argv/atom grammar and AST digest remain restricted, and the real answer-command records 40, 78, 116 and 124 of `wcap_initial_001` still qualify. The eight removed historical path findings are precisely the duplicated findings on these four commands. The new P1 failure histories are absent from those commands' recorder history.

P2 retains a common non-upscaling scale, the intersection of per-axis ≤1-pixel rounding intervals, strict RGB MAD `<2.0` in byte units (equivalent to `<2/255`), named standard resampling filters, and opaque alpha. Native same-size mode/pixel matching remains exact. Independently decoded all **47** formerly flagged resized returns from the original rollout image blocks: opacity and common-scale/non-upscaling dimensions pass; their reconstructed-source receipts are manifest verified and their accepted MAD is below 2. The maximum is approximately **0.476105136/255**. The other **17** removed image findings have exact historical reconstructions.

P3 positives for finite literal loops/ranges, output order, literal helper argv, 19 batch snapshots, independent image units and mkdir preservation pass. The reviewed change adds only the expanded-helper invalidation barrier and version update; it introduces no new rescan exception.

Independently reran `inspect()` on all **15 original rollouts**, with manifest checking enabled and at most three concurrent scans. Verified rollout and parent-manifest hashes, scanner identity, and saved v4.5.2 receipt hashes before replay. Every result is VALID and exactly matches the existing v4.5.2 receipt on `ok`, `violations`, `image_matches` (including reconstruction evidence), `image_match_counts` and `loop_expansions`. For each old image-flag ordinal, manifest-seeded reconstruction matches account for every removed image finding: **64 = 47 resized + 17 exact**. Exact original-image returns sharing the same output record were excluded from that accounting.

All 22 protected CQ4 files and existing JSON receipts/summaries were hash checked before and after the completed rescan and remain unchanged. Existing outputs were read and compared in memory, not regenerated on disk.

| Rollout | Removed v4.4 flags | Justification within P1–P3 |
|---|---:|---|
| wcap_initial_000 | 1 image | P2 resize; P3 literal array, record 62 |
| wcap_initial_001 | 3 image + 8 path | P2 resizes; P1 pinned-recorder answer argv |
| wcap_initial_002 | 5 image | P2 resizes; P3 independent image heredoc, record 131 |
| wcap_initial_003 | 3 image | P2 resizes |
| topup_initial_002 | 5 image | P2 resizes; P3 literal range, record 56 |
| topup_initial_003 | 3 image | P2 resizes |
| topup_initial_004 | 20 image | P3 recorded helper/literal argv and historical snapshots; P2 for 3 resized returns, plus 17 exact returns |
| topup_initial_005 | 1 image | P2 resize; P3 literal array, record 62 |
| topup_initial_006 | 6 image | P2 resizes; P3 mkdir at 19 and independent image unit at 174 |
| topup_initial_007 | 2 image | P2 resizes; P3 literal arrays and independent units at 52 |
| topup_initial_008 | 1 image | P2 resize; P3 literal range at 99 and setup isolation at 19 |
| topup_initial_009 | 5 image | P2 resizes; P3 mkdir at 19 and independent image unit at 166 |
| topup_initial_010 | 5 image | P2 resizes |
| topup_initial_011 | 2 image | P2 resizes; P3 independent image heredoc at 171 |
| topup_initial_012 | 2 image | P2 resizes; P3 independent image heredoc at 176 |

All rows remain VOID → VALID with zero remaining flags. **Promoted outside P1–P3: none found; 15/15 justified.** This review does not accept or score reader answers.

## HANDOVER identity

The actual scanner, `docs/harvest/sol_reading/HANDOVER.md:100`, `out/scan2c/HANDOFF.md:3` and `out/scan2/rescan_v452.json` agree on SHA-256:

```text
7b3647162c527426225f26b3c8eba494fb89b52302002594eb0b8246e5642f4e
```

SCAN2R3: FAIL | blocking 0 | high 1 | medium 0 | rescan justified 15/15
