# SEG-CP5′b code review

18 October 2026. **FAIL for drop-screen qualification: independently reproduced clips 1/4, non-clip FP 0/96, owner KEEP 22/22.** The ruled stop and non-gating fallback are justified. There is also a reporting-hook defect described below. No further detector, ownership tuning, or admission integration is authorized by these results.

Reviewed `docs/records/briefs/SEG_CP5pb_component_edge_clip.md`, receipt section b, the earlier review, and every deliverable in `seg/CP5p_COMMIT_LIST.json`. Paths below are repository-relative; `seg/` abbreviates `docs/records/harvest/collect_v3_admission/seg/`. This review wrote only this workspace document. Pytest fixtures were confined to `/tmp/seg-cp5pb-review-tests`; replays emitted stdout only. No network, reading/OCR, preparation, staging, commit, or publication was performed.

## Findings by severity

### Blocking — 0

The brief explicitly permits stopping and retaining a diagnostic when calibration fails. Consequently, leaving the admission version and composed union untouched is correct for this outcome.

### High — 1

**H1 — The component rule cannot meet the required 4/4 clip acceptance at any nonnegative tolerance.** `seg/calibrate_cp5pb.py:25`, `seg/calibrate_cp5pb.py:54`, `seg/CP5p_RECEIPT.md:103`.

Fresh offline native-cache replay exactly equals the complete saved `CP5pb_calibration.json`, including all per-row extents, provenance, guides, breakpoints, unavailable identities, and input hashes. A separately implemented predicate over those extents gives zero discrepancies. Three clips have zero qualifying continuation, so reducing tolerance cannot recover them:

| Required clip | Qualifying overflow | Reproduced explanation |
|---|---:|---|
| NLG `6ae0ac01064a587e s007-l0013` | 0 | The cut H2 extent is 7 px tall, 0.34263584445903505 xh; it fails the required ≥0.5 xh height. Its target-band overlap is approximately 91.4%. |
| Gazette `feb39c43ac177ef8 s000-l0665` | 0 | No examined H2 letter extent crosses either horizontal edge. |
| Gazette `73f0e4003296ba2e s000-l0097` | 1 px / 0.08358462117853842 xh | The cut extent is 11 px tall with 100% target-body-band overlap. |
| BSB `9342f9a56a4065cd s004-l0005` | 0 | No examined H2 letter extent crosses either horizontal edge. |

This is an unmet qualification condition, accurately disclosed by section b and `CP5pb_GATE_FAIL.md`; it is not evidence that the ruled component inequalities were implemented incorrectly. Retain the failed qualification and the diagnostic boundary. Do not label the screen 4/4 or integrate it as a drop predicate.

### Medium — 1

**M1 — The replay hook replaces content class with membership in the four known clips.** `seg/calibrate_cp5pb.py:81`, `seg/calibrate_cp5pb.py:82`, `seg/calibrate_cp5pb.py:119`; documented at `seg/CP5p_RECEIPT.md:119`.

The requested source × class hook follows the existing CP7 content-class reporting convention (`primary_class`; compare `seg/verify_cp5.py:232`). Instead, this hook creates only `clip`/`non_clip` keys using the hard-coded calibration truth set. `measure()` also discards content-class metadata. It therefore cannot report candidate incidence for headings, numerics, or other content classes, and an unseen clip becomes `non_clip` merely because its ID is absent from the four calibration IDs.

Independent probe: two measured NLG records carrying `primary_class='greek_mono'` and `'headings_caps'` collapse into one `nlg/non_clip` bucket. Joining the actual draw to the measured results yields **13 source × primary_class strata**; the single candidate belongs to `gazette_modern/modern_scanned` (1/47), while Gazette headings are a separate 0/2 stratum. Those distinctions are absent from the implemented hook. Preserve `source` and `primary_class` from the draw and count by them; clip-truth strata can remain an additional calibration breakdown. This does not change the reproduced overall counts or authorize admission integration.

## Component mechanics and tolerance

`seg/calibrate_cp5pb.py:48` consumes all represented rows' existing CP4 H2 `local_groups[].letters`, preserving native parent IDs, resolved status, and shared-parent split status. It does not restrict candidates to the frozen target's assigned row. The target alone supplies the vertical body band and x-height (`:46`, `:30`). This implements the revised **target-band** rule, rather than the superseded target-assignment restriction.

The predicate requires an existing H2 letter role (`:21`), height ≥0.5 target x-height (`:25`), a strict left/right edge crossing `x < edge < z` (`:28`), and target-body-band overlap ≥50% of the extent's own height (`:32`). Existing meanline/baseline guides are sampled at the edge and endpoint-clamped; no guide is fitted. The final diagnostic threshold uses strictly greater-than continuation (`:90`). Top/bottom edges do not generate candidates. Marks/noise are not promoted through a raw-component fallback. No new detector or ownership retuning appears; the actual frozen ownership hash remains `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`.

The passing tests cover right cut, touching, letter-scale stop, first-letter left cut, outside-target-band neighbour, marks/noise exclusion, half-height and half-overlap boundaries, and equality at tolerance. The real CP4 shared-parent fixture resolves both children: ending the crop at x=46 keeps the touching first child; ending at x=47 cuts the sibling and reports its genuine 11 px continuation. Native provenance partitioning remains in `greekocr/harvest/neighbour_words.py:222`. The replay examines 594 shared-split extents across CP7 plus owner KEEP. No qualifying hit is unresolved; unresolved extents elsewhere are not thereby qualified as resolved letters.

The complete independently reproduced curve is:

| Tolerance xh interval | Clips /4 | Non-clip FP /96 | Owner KEEP /22 |
|---|---:|---:|---:|
| [0, 0.08358462117853842) | 1 | 0 | 22 |
| [0.08358462117853842, infinity) | 0 | 0 | 22 |

Fixed-pixel tolerance gives the same two decision regions: [0,1) px gives 1/4, 0/96, 22/22; [1,infinity) px gives 0/4, 0/96, 22/22. Lower bounds are inclusive; upper bounds exclusive. There are **no non-clip false-positive IDs** at the selected diagnostic setting.

There is no passing interval and hence no passing-interval midpoint. The diagnostic instead selects the midpoint of the best separation interval, **0.04179231058926921 xh**, under its stated recall-minus-measurable-FPR objective. Its actual row-specific conversion is **0.3552346400087883–1.568370208108398 px** over 120 measurable records. The alternative fixed-pixel midpoint is 0.5 px, with identical observed decisions; it is not asserted to be a universal conversion. Receipt section b states these distinctions correctly (`seg/CP5p_RECEIPT.md:72`).

## Unavailable accounting

`seg/calibrate_cp5pb.py:43` returns null measurements before cache access for unavailable observations. The hook counts these separately (`:86`), and the curve excludes them from positives through `seg/calibrate_cp5p.py:70`. The two unchanged identities are `lekythos--9447d290d59a2411--s001-l0432` and `nlg--3d71f4f87abea186--s027-l0004`.

The /96 comprises 94 measurable non-clips and two unavailable records. Neither unavailable is a candidate clip or a verified KEEP. All 22 owner KEEP are measurable. Production `geometry_unavailable()` and its fail-closed composition at `greekocr/harvest/admission.py:495` and `:507` are byte-unchanged; the diagnostic introduces no admission decision.

## Independent checkpoint and test reproduction

- **CP1:** fresh `nw1b/calibrate.build_report()` equals the entire `CP5pb_preservation.json` CP1 report. Unique KEEP=22, required DROP=9; candidate standalone TP=9/FP=0/FN=0/TN=22, but actual historical union TP=9/FP=4/FN=0/TN=18, gate=false. Every ledger byte and all report fields, including witnesses and non-gating cases, match.
- **CP3:** fresh `verify_cp3.py` gives KEEP 22/22, C1 6/6, gallery 6/6, zero detector/network calls and runtime writes. The historical saved C1 7/7 artifact remains byte-preserved; that historical denominator is not the current six-witness ledger.
- **CP4:** the unmodified verifier stops at the existing stale controls binding (`seg/verify_cp4.py:185`). Fresh `verify_cp4_controls.py` output, supplied only through an in-memory `Path.read_text` substitution, lets the unchanged verifier reproduce acceptance 5/5, KEEP 22/22, C1 6/6, gallery 6/6, measured required DROP 8/9 plus one unavailable policy loss = composed 9/9. Controls reproduce fragment drops 0/12 (one unresolved), short mechanics 10/10, and CP3 planted FP 0/11. No saved dependency or hash was altered.
- **CP5:** with the original W1 feature snapshot, the unmodified verifier stops at its existing stale CP4 binding (`seg/verify_cp5.py:137`). Supplying the freshly computed CP4 report in memory reproduces rotated 4/4 (two measured, two regional), KEEP orientation FP 0/22, upright FP 0/11, C1/gallery 6/6, and five orientation-unknown KEEP. The current expanded verifier returns **5/8**, failing `union_resolved`, `union_keep_preserved`, and `separator_coverage`; composed KEEP admitted=0/22 and verified=0. The historical saved acceptance remains 4/4, byte-unchanged. These pre-existing limitations match the earlier review and must not be represented as freshly reproduced overall CP5 success.

All replays used `PYTHONDONTWRITEBYTECODE=1`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `.venv/bin/python -B`. Diagnostic reproduction ran `seg/calibrate_cp5pb.py` with stdout captured in memory. CP5 used `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl`; no snapshot or cache was regenerated.

The scoped pytest command was:

```sh
.venv/bin/python -B -m pytest -q -p no:cacheprovider \
  --basetemp=/tmp/seg-cp5pb-review-tests \
  tests/test_seg_cp1.py tests/test_seg_cp2.py tests/test_seg_cp3.py \
  tests/test_seg_cp4.py tests/test_seg_cp4c.py tests/test_seg_cp5.py \
  tests/test_seg_cp6.py tests/test_seg_cp7b_score.py tests/test_seg_cp5pb.py
```

**416 passed in 5.60 s.** The 39 new diagnostic tests record the failed clip qualification and mechanical boundaries; they do not demonstrate four detected clips. The independent native replay supplies the cache-backed reproduction beyond those frozen-JSON regressions.

## Preservation and actions

All ten listed deliverables match their commit-list SHA-256 values; all protected input hashes match. All nine admission/census/manifest artifacts match `seg/protected_before.json` by **SHA-256, size, and mtime**. The actual PNG inventory exactly equals the manifest's **28,798 paths**, and all 28,798 PNG contents pass the native verifiers' hash checks. No admission file, crops manifest, or PNG changed relative to the protected evidence. Production admission, H2, geometry, row-inclusion, orientation, and ownership code remain unchanged by this work.

The successful diagnostic replay ran under its filesystem/network/detector audit and reports zero runtime write attempts and zero publish actions. CP3/CP4 report zero writes/calls; CP5 reports an empty forbidden-attempt list. These observed SEG executions wrote nothing to the live root. This verifies the reviewed replay scope, not every other process on the machine. Unrelated staging/recut worktree changes were left untouched.

SEG-CP5pb review: FAIL | blocking: 0 | high: 1 | reproduced: clips 1/4, non-clip FP 0/96, KEEP 22/22 | publish actions: 0
