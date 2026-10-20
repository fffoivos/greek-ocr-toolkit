# SEG-CP5′ code review

18 October 2026. **FAIL for edge-clip qualification; the negative calibration and decision to stop are supported.** Reviewed the uncommitted CP5p script, calibration, receipt, and commit list against `docs/records/briefs/SEG_CP5p_edge_clip.md`. No integration was implemented or qualified. Only this review document was written in the workspace; test fixtures used `/tmp/seg-cp5p-review-tests`. No network, reader, preparation, staging, commit, or publication was performed.

## Findings by severity

### Blocking — 0

No additional blocking implementation finding. The brief explicitly requires stopping when no tolerance interval passes (`docs/records/briefs/SEG_CP5p_edge_clip.md:17`). Omitting admission integration, the version bump, replay hook, and new integration regressions after that stop is consistent with this instruction.

### High — 1

**H1 — No tolerance satisfies the required clip/KEEP acceptance.** `docs/records/harvest/collect_v3_admission/seg/calibrate_cp5p.py:54`, `docs/records/harvest/collect_v3_admission/seg/calibrate_cp5p.py:70`, `docs/records/harvest/collect_v3_admission/seg/CP5p_RECEIPT.md:14`.

Independent native-cache replay exactly equals `CP5p_calibration.json`, including every row, extent, parent id, breakpoint, and input hash. At zero tolerance the candidate catches **2/4**, falsely drops **1/96** CP7 non-clips, and preserves **19/22** owner KEEP. These are diagnostic results, not an accepted operating point.

| Required clip | Frozen target | Target x extent | Crop x extent | Overflow |
|---|---|---|---|---|
| NLG `6ae0ac01064a587e s007-l0013` | row-00013 | [112,1152) | [107,1151) | 1 px / 0.04894797777986215 xh |
| BSB `9342f9a56a4065cd s004-l0005` | row-00003 | [172,1175) | [169,1177) | 0 |
| Gazette `73f0e4003296ba2e s000-l0097` | row-00087 | [875,1555) | [870,1554) | 1 px / 0.08358462117853842 xh |
| Gazette `feb39c43ac177ef8 s000-l0665` | row-00115 | [99,375) | [93,535) | 0 |

The BSB and second Gazette target extents are wholly inside the crop horizontally. Neither can be caught by a nonnegative continuation tolerance on this frozen target evidence. Separately, keeping all 22 requires **t ≥ 0.05836231050571471 xh**, whereas catching the NLG clip requires **t < 0.04894797777986215 xh**. No midpoint exists. This is an unmet acceptance condition, accurately disclosed by the receipt, rather than authorization to substitute targets or retune ownership.

## Independently reproduced curve

Lower endpoints are inclusive; upper endpoints are exclusive. The footer uses the zero-tolerance diagnostic row so its three counts refer to the same setting.

| Tolerance, xh | Clips /4 | Non-clip FP /96 | Owner KEEP preserved /22 |
|---|---:|---:|---:|
| [0, 0.04680107281224919) | 2 | 1 | 19 |
| [0.04680107281224919, 0.04894797777986215) | 2 | 1 | 20 |
| [0.04894797777986215, 0.0490997669730924) | 1 | 1 | 20 |
| [0.0490997669730924, 0.057572474472484474) | 1 | 1 | 21 |
| [0.057572474472484474, 0.05836231050571471) | 1 | 0 | 21 |
| [0.05836231050571471, 0.08358462117853842) | 1 | 0 | 22 |
| [0.08358462117853842, infinity) | 0 | 0 | 22 |

Fixed-pixel tolerance gives 2 clips, 1 FP, and 19 KEEP for [0,1) px; at ≥1 px it gives 0 clips, 0 FP, and 22 KEEP. All positive measured overflows are 1 px. The receipt correctly states the row-dependent conversion `t_px = t_xh × xheight`; it does not invent a common pixel equivalent or choose an edge-case threshold.

At zero tolerance the non-clip FP is `bsb_poly1850--9f1e10e4cc7f1532--s006-l0058`. The owner false drops are `ia_poly1850--c39403323b6d5d89--s005-l0007`, `nlg--1144074169f43992--s006-l0032`, and `nlg--3d6bd7bd688acb61--s006-l0005`.

## Mechanics and unavailable accounting

- **CP4 H2 reuse:** `calibrate_cp5p.py:35` loads existing native caches, and lines 36–50 consume only the frozen target's H2 letter boxes/provenance plus its otherwise unrepresented native components, retaining CP3 exclusions. Full parent conservation and toolkit split partitioning remain in `greekocr/harvest/neighbour_words.py:222`. There is no new detector or ownership assignment. The frozen parameter hash independently remains `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`.
- **CAPS3 evidence:** `docs/records/harvest/recut_v1/w1_masked/caps3/screen_receipt.json:15` records the existing crop-edge helpers, 6/6 clips and 17/89 false positives. CP5p binds that artifact and documents its limitation; it does not import the crop-touch predicate as a qualified native-continuation screen.
- **Target and edges:** `calibrate_cp5p.py:36` selects the explicit target; lines 54–57 require crop intersection and measure only left/right overflow. Top/bottom overflow does not enter the score. Independent in-memory mechanical probes confirmed right clipping (1 px), exact touching (0), left clipping (2 px), vertical-only clipping (0), and the omitted-native-component fallback (1 px). The fallback probe is mechanical component coverage, not a newly qualified punctuation regression.
- **Shared parents:** independent reuse of the CP4 joined-parent fixture produced resolved children [40,46) and [46,58). A crop ending at x=46 measures zero overflow despite the sibling extending to x=58; ending at x=47 genuinely intersects and clips that sibling, measuring 11 px. Ending at x=58 keeps both. Parent-wide extent is not falsely charged to the first child. The existing conservation regression also passed. The real replay contains 368 split extents; none of its positive edge hits is unresolved. This is not a general qualification of unresolved letters.
- **Unavailable:** `calibrate_cp5p.py:33` returns null measurements before cache access; line 70 excludes unavailable CP7 rows from positives. Exactly two remain unavailable: `lekythos--9447d290d59a2411--s001-l0432` and `nlg--3d71f4f87abea186--s027-l0004`. Thus the /96 population comprises 94 measurable non-clips and two unavailable, with neither unavailable called clip or verified KEEP. Existing `geometry_unavailable` composition in `greekocr/harvest/admission.py:507` is unchanged.

## Earlier checkpoints and reproduction limits

Reproduction used `.venv/bin/python -B`, `PYTHONDONTWRITEBYTECODE=1`, and offline environment variables. The scoped suite was:

```sh
.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp5p-review-tests tests/test_seg_cp1.py tests/test_seg_cp2.py tests/test_seg_cp3.py tests/test_seg_cp4.py tests/test_seg_cp4c.py tests/test_seg_cp5.py tests/test_seg_cp6.py tests/test_seg_cp7b_score.py
```

**377 passed in 5.43 s.** These are existing regressions; CP5p adds no test file.

- **CP1:** fresh `calibrate.build_report()` gives unique KEEP 22, required DROP 9, union TP=9/FP=4/FN=0/TN=18, gate=false. The current ledger has six required C1 witnesses following the prior c068 ruling. The standalone historical `verify_cp1.py` does not complete: the guarded entrypoint rejects the stale qualification report at `nw1b/calibrate.py:142`. Nothing was regenerated on disk.
- **CP3:** fresh `verify_cp3.py` gives KEEP 22/22, C1 6/6, gallery 6/6, zero detector/network calls and writes. The receipt's **historical** CP3 C1 7/7 artifact is byte-preserved, but 7/7 is not the current six-witness ledger denominator; it was not reproduced as a current result.
- **CP4:** the unmodified command stops on the stale admission-adapter binding in `verify_cp4.py:185`. I reran `verify_cp4_controls.py`, supplied its newly computed JSON to the CP4 verifier through an in-memory `Path.read_text` substitution, and left both saved files untouched. Fresh acceptance is 5/5, KEEP 22/22, C1 6/6, gallery 6/6, required DROP 8/9 measured plus one unavailable policy loss = 9/9 composed. Controls remain 0/12 fragment drops (one unresolved), 10/10 short mechanics, 0/11 CP3 planted FP. Acceptance numbers equal the saved results; binding/version/page-coverage metadata do not.
- **CP5:** the unmodified verifier similarly stops on its stale CP4 binding at `verify_cp5.py:137`. With the freshly computed CP4 output supplied in memory, all 1,715 crops were remeasured. The four historical orientation requirements still pass: rotated 4/4 (two measured, two regional), KEEP orientation FP 0/22, upright FP 0/11, horizontal C1/gallery 6/6, explicit unknowns (five KEEP). **The current expanded CP5 verifier is not an exact 4/4 replay:** it evaluates eight requirements and returns 5/8, with separator coverage/union resolution/union KEEP preservation failing; current composed KEEP admission is 0/22, verified KEEP 0. Historical saved union verified KEEP is 17/22. These later verifier/dependency differences must not be described as freshly reproduced unchanged overall CP5 acceptance. No guards were disabled and no dependency binding was forged; the supplied CP4/controls outputs were freshly computed.

These reproduction caveats predate the CP5p diagnostic: its protected historical artifacts and production inputs match their recorded hashes. They do not establish a CP5p-caused runtime regression, and they do not authorize refreshing caches or historical evidence during this read-only review.

## Preservation and side effects

All nine protected admission/census/manifest artifacts match `seg/protected_before.json` by **SHA-256, size, and mtime**. All **28,798 retained PNGs** match the unchanged crops manifest in the native verification runs. All CP5p input bindings and all four listed deliverable hashes match. Admission, neighbour, row-inclusion, geometry, orientation, and ownership modules are byte-identical to HEAD; unrelated staging and recut drafts were not changed by this review.

The CP5p replay runs under the filesystem/network audit at `calibrate_cp5p.py:85`; successful completion allows no runtime write or mutation. CP3/CP4 report zero writes and detector/network calls; CP5 reports an empty forbidden-attempt list. These executions wrote nothing to the live root and performed **zero publish actions**. This confirms the observed replays and protected-file preservation, not a retrospective audit of every other process on the machine.

SEG-CP5p review: FAIL | blocking: 0 | high: 1 | reproduced: clips 2/4, non-clip FP 1/96, KEEP 19/22 | publish actions: 0
