# SCAN2R2 — scanner v4.5.1 re-review

**Verdict: FAIL — 0 blocking, 1 high, 0 medium findings.** All 96 supplied tests pass, including the original H1–H3 probes. H1 and H3 are closed on the additional probes; H2 is only partially closed: replay through a recorded helper can still overwrite a cached helper without invalidating its source. Two new probes incorrectly return VALID. The 15 historical rescan verdicts are nevertheless individually justified by P1–P3.

## Scope and verification

Reviewed offline on 19 October 2026, HEAD `30c361e88`. Read the SCAN2R/SCAN2R2 briefs, SCAN2 ruling, SCAN2B fix brief, both implementation handoffs, prior review, and the external `greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md` pattern source. Reviewed implementation diff `30c361e88^..30c361e88` and the original v4.5 admission rules. The working tree already contains an uncommitted addition of `Scan2BProbes` in `tests/test_scan_rollout.py`; it was included in the executed tests and left unchanged. The two pre-existing untracked SC45 briefs were also left unchanged.

No network, implementation changes, reader launches, answer scoring, original-pack edits, ledger updates or receipt overwrites. Synthetic packs and replay workers used self-cleaning OS temporary directories, as in the prior review. This report is the only persistent output created by this review.

Executed:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**96 tests passed in 110.420 seconds, zero skips.** All six historical witnesses ran. The RU1 missing crops were restored only into temporary, manifest-verified snapshots. Existing truth/outside/traversal, manifest mismatch, dynamic-load, crop/upscale/distortion, native mode/pixel/alpha and unreplayable-overwrite fixtures retain their expected outcomes. The only committed historical-test change is the version assertion from `4.5` to `4.5.1`.

## High finding

### H1 — Expanded helper invocations bypass helper-cache invalidation (SCAN2R H2 remains open)

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:538` and `:540`; compare invalidation at `:502` and `:514`.

`replay_history()` now invalidates helpers for accepted whole-command and isolated inline Python replay. Its helper-invocation branch substitutes literal argv and validates the resulting Python, but yields that replay without calling `invalidate_helpers()`. Consequently, an accepted helper can overwrite another helper, or itself, while the cached historical source remains authoritative for a later invocation. Worker confinement does not establish that the script still contains its original source.

**New probe A — another helper overwrites the cached script.** Using the existing synthetic `Pack` (180×120 source), record these commands in order:

```sh
mkdir -p zoom
cat > zoom/batch.py <<'PY'
from PIL import Image
Image.open('img/source.png').resize((360,240)).save('zoom/batch.png')
PY
cat > zoom/kill.py <<'PY'
from PIL import Image
Image.new('RGB',(1,1)).save('zoom/batch.py',format='PNG')
PY
python3 zoom/kill.py 0
python3 zoom/batch.py 0
```

These are separate recorded calls, with each `cat` heredoc kept intact. Then record `view_image` of `zoom/batch.png` and return `source.resize((360,240))`.

**Observed v4.5.1:** `ok: true`, `violations: []`, `image_match_counts: {"reproduced": 1}`. The reconstruction receipt reports successful replay of the overwrite at record 3 and the obsolete batch source at record 4. The final image has `pixels_exact: true` and SHA-256 `56b5f59f521fbc164cef43ffc624cdef9fed122fb0bbb7a68f15772005095efd`.

**Expected:** VOID. At the second invocation the real `zoom/batch.py` contains a PNG, so Python cannot execute the original image builder; no batch image has previously been produced. The enlargement also excludes an accidental match against a preserved original image.

**New probe B — self-overwrite followed by another invocation.** Define `zoom/batch.py` with this body:

```python
from PIL import Image
Image.open('img/source.png').resize((360,240)).save('zoom/batch.png')
Image.new('RGB',(1,1)).save('zoom/batch.py',format='PNG')
```

Define `zoom/blue.py` to run `Image.new('RGB',(1,1),'blue').save('zoom/batch.png')` after importing `Image`. Record `mkdir -p zoom`, both definitions, then `python3 zoom/batch.py 0`, `python3 zoom/blue.py 0`, and `python3 zoom/batch.py 0`, followed by the same view and 360×240 source return.

**Observed v4.5.1:** again VALID, no violations, one `reproduced` match. All three expanded invocations report return code 0. **Expected:** VOID: the last real invocation cannot execute the self-overwritten PNG script, and the actual image at that point remains the 1×1 blue overwrite. This second probe avoids relying on an absent image alone.

Independently loaded the unchanged v4.4 scanner from `c21b21565^` in memory, verified its SHA-256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`, and reran both probes: both return VOID with unmatched image provenance. Thus the new VALID outcomes exceed P3's historical-helper authority.

**Required correction:** inspect the transformed helper replay for possible writes and invalidate affected cached sources before yielding it, including self-overwrites, just as for inline replay. Add both negative histories as fixtures. These are two manifestations of one missing invalidation branch, counted as one high finding. No correction was implemented during this review.

## Original probes and additional probes

The three original test families contain five concrete negative rollouts; all were rerun through `Scan2BProbes`. Six additional concrete rollouts were run from an in-memory Python harness using the existing `Pack`, `call`, `exe`, `view` and `returned` helpers; no new test file was written.

| Class | Probe | v4.5.1 outcome | Assessment |
|---|---|---|---|
| Original H1 | `if false; then` around image heredoc | VOID | Fixed |
| Original H1 | Uncalled `build() { ... }` around image heredoc | VOID | Fixed |
| Original H2 | Accepted inline image command overwrites `zoom/batch.py` | VOID | Exact original probe fixed |
| Original H3 | Unused loop-header `/tmp/outside` | VOID | Fixed |
| Original H3 | Unused loop-header `../truth.json` | VOID | Fixed |
| New H1 A | `while false; do` around image heredoc | VOID | Closed enclosing grammar holds |
| New H1 B | `false &&` before image heredoc | VOID | Closed enclosing grammar holds |
| New H2 A | Recorded helper overwrites another recorded helper | **VALID** | High finding above |
| New H2 B | Recorded helper overwrites itself, then is invoked again | **VALID** | Same high finding |
| New H3 A | Unused loop-header `/n` | VOID | Outside-path finding retained |
| New H3 B | Unused loop-header `../outside` | VOID | Traversal and outside-path findings retained |

Both new H1 probes request the same distinct 360×240 historical image; their reconstruction receipts skip the entire unsupported shell command and report the reproduced view missing. Both new H3 probes return the exact source image, isolating the literal-path checks from image provenance.

## P1–P3 qualification and historical rescan

P1 still uses complete argv parsing, the closed atom grammar and the recorded recorder AST pin. `/n`, `/tmp/outside`, `../truth.json`, mixed/invalid atoms, shell additions and changed-recorder negatives pass. For the actual four duplicated path-flag records (40, 78, 116, 124 of `wcap_initial_001`), the removed path findings arise solely from authorized answer atoms.

P2 retains the intersection of the two ≤1-pixel scale intervals, rejects growth of either axis, and compares RGB MAD strictly below 2 in byte units, equivalent to `<2/255`, under a named standard filter. Native same-size mode/pixel checks remain exact. All 47 previously failing resized returns were independently decoded again: all are fully opaque RGBA, have a common non-upscaling scale against the receipt's manifest-seeded source, and satisfy the dimensions recorded in the receipt. Their maximum accepted MAD is approximately `0.476105136/255`. The remaining 17 previously failing returns are exact historical reconstructions.

P3's literal loops/ranges, output order, literal helper argv, independent mkdir retention and mixed-command isolation pass the supplied positive/negative fixtures. The new finding limits the helper identity guarantee; it does not occur in these 15 rollouts. Inspection of their successful reconstruction commands found read-only `open()` calls and PNG save targets, including the literal/f-string/percent-formatted batch names; none writes helper source.

Independently reran `inspect()` on **all 15 original rollouts**, with at most three concurrent scans and results compared in memory. Before scanning, verified every rollout and parent-manifest SHA-256 against both rescan summaries, the v4.5 baseline summary hash, and the v4.5.1 scanner hash. Every result is VALID with manifest checking enabled and exactly matches both saved v4.5 and v4.5.1 receipts on `ok`, `violations`, `image_matches` (including reconstruction evidence) and `loop_expansions`. Verified all 22 protected files listed in `out/scan2/cq4_receipts_sha256.json` before and after the rescan; all hashes match.

For each historical image-flag ordinal, the number of seeded reconstruction matches equals the number of removed v4.4 image findings: **64 total = 47 resized + 17 exact**. The eight removed path findings are the four duplicated P1 cases. All rows below are VOID → VALID, with zero remaining findings.

| Rollout | Removed v4.4 flags | Justification within P1–P3 |
|---|---:|---|
| wcap_initial_000 | 1 image | P2 resize; P3 literal array including record 62 |
| wcap_initial_001 | 3 image + 8 path | P2 resizes; P1 pinned-recorder answer argv |
| wcap_initial_002 | 5 image | P2 resizes; P3 independent image heredoc at record 131 |
| wcap_initial_003 | 3 image | P2 resizes |
| topup_initial_002 | 5 image | P2 resizes; P3 literal ranges including record 56 |
| topup_initial_003 | 3 image | P2 resizes |
| topup_initial_004 | 20 image | P3 recorded helper/literal argv and 19 historical batch snapshots; P2 for 3 resizes, with 17 exact returns |
| topup_initial_005 | 1 image | P2 resize; P3 literal array at record 62 |
| topup_initial_006 | 6 image | P2 resizes; P3 mkdir at record 19 and image isolation at 174 |
| topup_initial_007 | 2 image | P2 resizes; P3 literal arrays and independent units at record 52 |
| topup_initial_008 | 1 image | P2 resize; P3 literal range at record 99 and setup isolation at 19 |
| topup_initial_009 | 5 image | P2 resizes; P3 mkdir at record 19 and image isolation at 166 |
| topup_initial_010 | 5 image | P2 resizes |
| topup_initial_011 | 2 image | P2 resizes; P3 independent image heredoc at 171 |
| topup_initial_012 | 2 image | P2 resizes; P3 independent image heredoc at 176 |

**Promoted for a reason outside P1–P3: none found; 15/15 justified.** This is a scanner adjudication, without acceptance or scoring of the reader answers.

## HANDOVER identity

`docs/harvest/sol_reading/HANDOVER.md:99`, `out/scan2b/HANDOFF.md:3`, `out/scan2/rescan_v451.json` and the actual scanner file agree:

```text
d326e808d9e1964c4b58afc39b69d3377b4a8e8a13e650a125d63b262f393b42
```

The prior v4.5 digest in `out/scan2/HANDOFF.md` remains a historical implementation identity, not the current v4.5.1 digest.

SCAN2R2: FAIL | blocking 0 | high 1 | medium 0 | rescan justified 15/15
