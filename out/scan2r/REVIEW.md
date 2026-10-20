# SCAN2R — canonical scanner v4.5 review

**Verdict: FAIL — 0 blocking, 3 high, 0 medium findings.** The supplied 93 tests pass, but three additional negative probes return VALID incorrectly. The 15 CQ4 adjudications are individually supported by P1–P3; no rollout was found promoted for an unrelated reason.

## Scope and verification

Reviewed offline on 19 October 2026. HEAD `b69593e90` adds only the SCAN2R brief; the implementation diff reviewed is `c21b21565^..c21b21565`, including scanner, tests, fixtures and HANDOVER. Read `out/scan2/HANDOFF.md`, the SCAN2 ruling, and the external `CQ4E_VOIDS.md` pattern source. No implementation, original pack, rollout, ledger or receipt was edited. Test/replay scratch files were confined to temporary directories; this report is the only persistent output.

Executed:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

Result: **93 passed in 91.206 seconds, no skips** (40 new, 53 existing). All six historical witnesses ran, including CQ1 record 24 remaining VOID and RU1 ctx04 retaining exactly 15 provenance findings. Missing RU1 crops were restored only into temporary, manifest-verified snapshots by the test harness. Existing truth/outside/traversal, dynamic-load, manifest, native-pixel/mode/alpha and unreplayable-overwrite fixtures retain their expected outcomes. The authorized general-scale change to the old 1024-pixel negative assertion is consistent with P2.

## High findings

### H1 — Replay extracts heredocs without proving that their shell context executes

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:444` (also lines 445–459).

After whole-command parsing fails, `HEREDOC.finditer` extracts a Python heredoc from anywhere in the command and replays it independently. Surrounding unsupported shell control flow is discarded. P3 permits isolating **independent** image commands, not executing bodies of false branches or uncalled functions.

Using the synthetic pack from `tests/test_scan_rollout.py`, record `mkdir -p zoom`, then this command:

```sh
if false; then
python3 - <<'PY'
from PIL import Image
Image.open('img/source.png').resize((360,240)).save('zoom/batch.png')
PY
fi
```

Record a view of `zoom/batch.png` returning the 360×240 resized source. The scanner reports **VALID**, `{'reproduced': 1}`, no violations. The shell never creates that view. Wrapping the same heredoc in an uncalled `build() { ... }` produces the same incorrect result. Both probes are **VOID under the parent v4.4 scanner**. The enlargement makes the returned image distinct from all preserved source candidates, so this specifically exercises fabricated reconstruction rather than an existing-original byte match.

Required correction: recognize only a closed grammar of independent shell units; reject or skip the entire uncertain control-flow scope. Add false-branch and uncalled-function negatives alongside the mixed-heredoc positives.

### H2 — Successful replay commands can overwrite a helper without invalidating its cached source

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:439` (early `continue` at line 441; invalidation only at lines 462–464).

`replay_history` caches the text written to `zoom/batch.py`. A subsequent command accepted directly by `parse_replay` bypasses helper invalidation. Later invocation is expanded from the cached text even if an intervening accepted command replaced the helper's bytes.

Reproduced with this history:

1. Record `mkdir -p zoom` and a literal `cat > zoom/batch.py` heredoc containing `from PIL import Image` and `Image.open('img/source.png').resize((360,240)).save('zoom/batch.png')`.
2. Record a valid image heredoc containing `from PIL import Image` and `Image.new('RGB',(1,1)).save('zoom/batch.py',format='PNG')`.
3. Record `python3 zoom/batch.py 0`, then a view of `zoom/batch.png` returning the 360×240 source enlargement.

Result: **v4.5 VALID**, `{'reproduced': 1}`, no violations; **v4.4 VOID**. At invocation time the actual helper is a PNG, so Python cannot execute the original helper. The restricted worker's confinement does not establish historical helper identity. This defeats P3's historical replay requirement and the unreplayable-overwrite protection.

Required correction: track helper mutations across every history command and require the helper bytes at invocation to match the recorded source, or invalidate its authority whenever a possible mutation cannot be excluded. Add an intervening accepted-command overwrite negative; the current final-tree and unsafe-helper negatives do not cover this case.

### H3 — Loop replacement erases forbidden literals before path checks

**Location:** `docs/harvest/sol_reading/tools/scan_rollout.py:562` (mutation at lines 565–566; path inspection follows at lines 575–576).

The expanded calls replace the entire original loop. Literal array values disappear if the body does not interpolate the loop variable. Consequently, forbidden path literals can evade all path checks without qualifying as P1 answer data.

Both recorded calls below, followed by the exact `img/source.png` return, report **v4.5 VALID with zero violations**:

```javascript
for(const n of ["/tmp/outside"])image((await tools.view_image({path:"img/source.png"})).image_url);
for(const n of ["../truth.json"])image((await tools.view_image({path:"img/source.png"})).image_url);
```

The parent v4.4 scanner rejects each: outside absolute path for the first; forbidden/traversal and outside-path findings for the second. These are separate probe rollouts. P3 authorizes concrete view binding, not removal of the existing literal-input rules. `tests/test_scan_rollout.py:163` tests only path escapes that survive interpolation into the replacement path, so it misses this case.

Required correction: preserve/check the original loop literals as well as expanded paths, applying only the explicitly ruled exceptions. Add unused-header `/tmp/outside` and `../truth.json` negatives.

## P1 and P2 qualification

P1's recorder AST pin, complete-argv parsing and closed atom grammar pass inspection and fixtures. Actual CQ4 answer commands at records 40, 78, 116 and 124 of `wcap_initial_001` qualify. Real `/n`, `/tmp/outside`, `../truth.json`, invalid/mixed atoms, shell additions and changed-recorder negatives fail as required. There is no broad filename exemption.

P2 implements the intersection of the per-axis ≤1-pixel scale intervals, rejects either axis growing, and uses strict RGB MAD `<2.0` in byte units (equivalent to `<2/255`), a named standard filter, and opaque alpha for the new resized returns. New zoom scales require manifest-seeded reconstruction. Native same-size comparisons remain mode/pixel exact, as explicitly retained by CQ4E. Crop, upscale, distortion, transparent-alpha, unseeded-zoom and MAD-boundary fixtures pass. Independently decoded all **47 previously flagged resized returns** and checked their opacity and common-scale/non-upscaling dimensions against reconstruction receipts; all qualify. The other **17** previously flagged returns are byte-exact historical reconstructions.

P3's normal literal-array/range cases, output order, literal integer helper argv, 19 overwritten batch snapshots, and both literal mkdir forms pass the supplied fixtures. H1–H3 show that its admission boundary is nevertheless too broad.

## Per-rollout adjudication

Compared the preserved v4.4 flags with final v4.5 receipts, rollout/manifest identities and reconstruction evidence. Every one of the 64 removed image findings has a manifest-verified reconstruction. All 47 resized returns have recorded MAD below 2; the maximum first-accepted-filter MAD is approximately **0.476105136/255**. The eight removed path findings are exactly the four duplicated P1 answer-command findings. Verified every path/hash in `out/scan2/cq4_receipts_sha256.json` against the current protected files, including the unchanged v4.4 scanner, ledger and original scans.

Independently reran `inspect()` on **all 15 original rollouts**, first verifying each rollout SHA-256 and parent-manifest SHA-256 against `rescan_v45.json`. All 15 returned VALID and exactly reproduced the saved `ok`, `violations`, `image_matches` (including reconstruction evidence), and `loop_expansions` fields. Results were compared in memory; the existing rescan outputs were not overwritten.

All rows are **VOID → VALID**, with zero remaining flags. “P3” below denotes needed literal view binding, helper replay, mkdir preservation or independent mixed-heredoc isolation.

| Rollout | Removed flags | Justification within the ruling |
|---|---:|---|
| wcap_initial_000 | 1 image | P2 resize + P3 literal view array, including record 62 |
| wcap_initial_001 | 3 image + 8 path | P2 resizes + P1 pinned-recorder answer argv |
| wcap_initial_002 | 5 image | P2 resizes + P3 independent image heredoc at record 131 |
| wcap_initial_003 | 3 image | P2 resizes |
| topup_initial_002 | 5 image | P2 resizes + P3 literal ranges, including record 56 |
| topup_initial_003 | 3 image | P2 resizes |
| topup_initial_004 | 20 image | P3 recorded helper/literal argv and historical snapshots; P2 for 3 resizes, 17 exact returns |
| topup_initial_005 | 1 image | P2 resize + P3 literal array at record 62 |
| topup_initial_006 | 6 image | P2 resizes + P3 mkdir at record 19 and image isolation at 174 |
| topup_initial_007 | 2 image | P2 resizes + P3 literal arrays and independent units at record 52 |
| topup_initial_008 | 1 image | P2 resize + P3 literal ranges, including record 99; setup isolation at 19 |
| topup_initial_009 | 5 image | P2 resizes + P3 mkdir at record 19 and image isolation at 166 |
| topup_initial_010 | 5 image | P2 resizes |
| topup_initial_011 | 2 image | P2 resizes + P3 independent image heredoc at 171 |
| topup_initial_012 | 2 image | P2 resizes + P3 independent image heredoc at 176 |

**Promoted for a reason outside P1–P3: none found (15/15 justified).** This does not accept or score the answers, and does not waive the three scanner findings above.

## HANDOVER identity

`docs/harvest/sol_reading/HANDOVER.md:98` and `out/scan2/HANDOFF.md:3` both match the actual scanner SHA-256:

```text
c5204fe88490c35af07d1257680a9d32d4e43ab7be329b352af83c88a9cee17c
```

SCAN2R: FAIL | blocking 0 | high 3 | medium 0 | rescan justified 15/15
