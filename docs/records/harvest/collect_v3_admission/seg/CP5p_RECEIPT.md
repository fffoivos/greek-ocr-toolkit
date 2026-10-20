# SEG-CP5p receipt — stopped at tolerance calibration

No passing tolerance interval exists. No tolerance was selected. Admission, its version, and the composed union were not changed; integration, replay-hook integration, and new planted integration tests were stopped under Build 2. No refreeze or fresh-100 gate is claimed.

Network OFF; no reader, OCR, detector, preparation, staged replay, commit, or publish action. The live run root was read-only. Ownership remains `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. Existing unrelated worktree changes were preserved.

## Mechanics and evidence

`calibrate_cp5p.py` consumes the sealed CP7 draw and CP4 H2 `row_inclusion.rows[].local_groups[].letters` native extents. These preserve parent provenance and the existing toolkit shared-parent split partition. It loads only completed native caches, checks the explicit frozen target row, and retains native components omitted by letter grouping (including punctuation), subject to the existing CP3 rule exclusions. No new detector or ownership assignment is used. Half-open native boxes must intersect the crop horizontally and vertically; overflow is `max(crop_left - native_left, native_right - crop_right, 0)`. Only horizontal overflow strictly greater than tolerance drops. Touching and equality keep. Top and bottom overflow are excluded.

CAPS3 evidence: `docs/records/harvest/recut_v1/w1_masked/caps3/screen_receipt.json` names `greekocr.verify.images.image_checks` and `greekocr.verify.calibration._predict` with `RULES[cut_left/cut_right]`: edge fraction > 0. It caught 6/6 CAPS2 clips but falsely flagged 17/89 crop-ok cards. This is historical crop-edge evidence, not a qualified native-extent tolerance. CP5p measures native continuation as required instead of importing its crop-touch false positives.

## Required clips

| Row | Frozen target | Assigned row x extent | Crop x extent | Maximum overflow px | Maximum overflow xh |
|---|---|---|---|---:|---:|
| nlg--6ae0ac01064a587e--s007-l0013 | row-00013 | [112, 1152] | [107, 1151] | 1 | 0.04894797778 |
| bsb_poly1850--9342f9a56a4065cd--s004-l0005 | row-00003 | [172, 1175] | [169, 1177] | 0 | 0.00000000000 |
| gazette_modern--73f0e4003296ba2e--s000-l0097 | row-00087 | [875, 1555] | [870, 1554] | 1 | 0.08358462118 |
| gazette_modern--feb39c43ac177ef8--s000-l0665 | row-00115 | [99, 375] | [93, 535] | 0 | 0.00000000000 |

Two required clips have zero native continuation for their frozen target: the BSB row ends at x=1175 inside crop right=1177; the gazette feb39 row ends at x=375 inside crop right=535. Their raw native target components also end inside the crop. A nonnegative overflow tolerance cannot make these rows positive. No target substitution or neighbour borrowing was performed.

## Full tolerance curve

These are all decision-constant intervals for every nonnegative tolerance, including owner KEEP breakpoints. Lower endpoints are inclusive; upper endpoints are exclusive. Pixels are row-specific: `tolerance_px = tolerance_xh × row_xheight`. There is no single fixed-pixel equivalent of an x-height tolerance. All observed positive overflows are exactly 1 px.

| Tolerance xh interval | Clips dropped /4 | CP7 non-clip false drops /96 | Owner KEEP false drops /22 |
|---|---:|---:|---:|
| [0.00000000000, 0.04680107281) | 2 | 1 | 3 |
| [0.04680107281, 0.04894797778) | 2 | 1 | 2 |
| [0.04894797778, 0.04909976697) | 1 | 1 | 2 |
| [0.04909976697, 0.05757247447) | 1 | 1 | 1 |
| [0.05757247447, 0.05836231051) | 1 | 0 | 1 |
| [0.05836231051, 0.08358462118) | 1 | 0 | 0 |
| [0.08358462118, ∞) | 0 | 0 | 0 |

| Fixed-pixel tolerance interval | Clips dropped /4 | CP7 non-clip false drops /96 | Owner KEEP false drops /22 |
|---|---:|---:|---:|
| [0, 1) px | 2 | 1 | 3 |
| [1, ∞) px | 0 | 0 | 0 |

The 96 non-clips include the two unchanged geometry-unavailable rows; only 94 have measurable edge evidence. Unavailable rows are never counted as edge-clip positives or certified edge KEEP. They retain the existing fail-closed geometry policy.

At zero tolerance, the non-clip false drop is `bsb_poly1850--9f1e10e4cc7f1532--s006-l0058` (1 px / 0.05757247447 xh). Owner KEEP false drops are:
- `ia_poly1850--c39403323b6d5d89--s005-l0007`: 1 px / 0.04909976697 xh.
- `nlg--1144074169f43992--s006-l0032`: 1 px / 0.05836231051 xh.
- `nlg--3d6bd7bd688acb61--s006-l0005`: 1 px / 0.04680107281 xh.

Keeping all 22 owner KEEP requires tolerance ≥ 0.05836231051 xh; catching the NLG clip requires tolerance < 0.04894797778 xh. This independently disproves a passing interval even among the two detectable clips. Midpoint selection is therefore undefined.

## Preservation and validation

377 existing tests passed in 5.04 s across CP1–CP6 and CP7b scoring (`CP5p_pytest.log`). Required new planted/regression integration tests were not implemented because tolerance qualification failed first. The diagnostic replay covered 100 sealed CP7 rows and all 22 owner KEEP; it is evidence of failure, not acceptance.

CP1 ledger and CP3/CP4/CP5 verification artifacts and production modules match the input hashes recorded in `CP5p_calibration.json`. Their acceptance numbers remain unchanged: CP3 KEEP 22/22, C1 7/7, gallery 6/6; CP4 KEEP 22/22, C1 6/6, gallery 6/6, composed drops 9/9, acceptance 5/5; CP5 acceptance 4/4 (its historical overall `gate=false` is preserved). CP1 remains KEEP unique 22, published DROP 9, historical union failure 4/22. No historical receipt was rewritten.

Reproduce: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/collect_v3_admission/seg/calibrate_cp5p.py` (stdout only; audit hook rejects runtime writes, network, and mutation). Full per-row extents, parent IDs, unavailable IDs, exact breakpoints, and input SHA256 bindings are in `CP5p_calibration.json`.

The requested success footer would falsely claim clips 4/4 and a passing interval. The truthful stop footer follows.

SEG-CP5p: stopped | tolerance none px / none xh (passing interval none) | clips at most 2/4 | CP7 non-clip false drops 1/96 at zero tolerance | KEEP 19/22 at zero tolerance | CP3/CP4/CP5 unchanged: yes | tests: 377 passed

## b. SEG-CP5pb — stopped, diagnostic only

No passing interval exists. The one ruled component-based round ends here.
End-clips are admitted as a known class by this screen: `edge_clip_candidate`
is a non-gating diagnostic, never a drop/admission predicate. Other existing
admission rules continue to apply. No ownership changes, new detector,
reader, network access, refreeze, staging, commit or publish actions occurred.

The best diagnostic separation is the interval [0, 0.08358462117853842) xh.
Its midpoint is 0.04179231058926921 xh. The objective is clip recall minus
measurable non-clip false-positive rate, with owner false positives as tie
break. Every point in this interval gives 1/4 clips, 0/96 FP and 22/22 KEEP.
The equivalent fixed-pixel decision interval is [0, 1) px (midpoint 0.5 px).
These are alternative parameterizations with identical observed decisions;
there is no universal conversion between pixels and x-height. The selected
xh tolerance is multiplied by each target's own x-height; this yields
0.3552346400087883–1.568370208108398 px over the measured 122-row population
(120 measured, two unavailable). Every per-row conversion is in the JSON.

## Complete decision curve

| Tolerance xh interval | Clips /4 | Non-clip FP /96 | Owner KEEP /22 |
|---|---:|---:|---:|
| [0, 0.08358462117853842) | 1 | 0 | 22 |
| [0.08358462117853842, infinity) | 0 | 0 | 22 |

| Fixed-pixel tolerance interval | Clips /4 | Non-clip FP /96 | Owner KEEP /22 |
|---|---:|---:|---:|
| [0, 1) px | 1 | 0 | 22 |
| [1, infinity) px | 0 | 0 | 22 |

Lower endpoints are inclusive, upper endpoints exclusive; equality keeps.
The /96 includes 94 measurable non-clips and two unchanged unavailable rows.
Unavailable is neither a candidate positive nor a verified KEEP.

## Required clips

| Frozen row | Maximum qualifying continuation | Result |
|---|---:|---|
| nlg--6ae0ac01064a587e--s007-l0013 | 0 | Not flagged: cut H2 component is 7 px tall / 0.34263584445903505 xh, below 0.5 xh |
| gazette_modern--feb39c43ac177ef8--s000-l0665 | 0 | No H2 letter extent cut by either horizontal edge |
| gazette_modern--73f0e4003296ba2e--s000-l0097 | 1 px / 0.08358462117853842 xh | Flagged; 11 px height, 100% target-body-band overlap |
| bsb_poly1850--9342f9a56a4065cd--s004-l0005 | 0 | No H2 letter extent cut by either horizontal edge |

The replay uses all rows' CP4 H2 letter extents in the saved CP3 evidence,
with full native parents and toolkit split partitioning; it does not borrow
the target row identity to replace the band. A cut satisfies x0 < edge < x1;
body-band overlap is the vertical intersection divided by native height.
Existing target meanline/baseline guides are sampled at the cut column,
endpoint-clamped outside the recorded target x span. No guide is fitted.
Only existing H2 letters enter; no raw-component fallback promotes omitted
marks/noise. Height must be at least half the target x-height. The saved
JSON includes every examined extent, cut candidate, provenance, band overlap,
full target guides and unavailable identity.

`calibrate_cp5pb.replay_counts(rows, tolerance, unit)` counts total, measured,
unavailable and `edge_clip_candidate` per source × frozen clip/non-clip class.
It returns counters only. The CP7 replay has one diagnostic candidate in
Gazette's clip class and zero in every other source/class. No admission
integration or version bump was made after this failure.

CP1 freshly gives KEEP=22, DROP=9, union TP=9/FP=4/FN=0/TN=18, gate=false;
the complete freshly computed CP1 report and unchanged input proofs are in
`CP5pb_preservation.json`. Every ledger byte is unchanged. CP3/CP4/CP5 code
and historical verification artifacts are unchanged, not newly qualified.
The pre-existing stale verifier bindings and expanded CP5 failures documented
in `docs/records/reviews/SEG_CP5p_review.md` remain unresolved; no historical acceptance
numbers were rewritten or presented as current successful replays.
All nine protected artifacts retain SHA256, size and mtime. The runtime audit
rejects writes, mutations, detector calls and network access. No PNG or live
run file was written by this replay; protected manifests remain unchanged.

416 tests passed (377 earlier regressions plus 39 diagnostic tests), including
cut/touch/stop/left-edge/out-of-band/mark/noise/half-height mechanics, strict
tolerance, real H2 shared-parent splitting, the four failed-qualification clip
regressions and 22 owner KEEP regressions. These qualify mechanics and record
the failed calibration; they do not qualify a drop screen.

Reproduce offline with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1 .venv/bin/python -B
 docs/records/harvest/collect_v3_admission/seg/calibrate_cp5pb.py` (stdout only).

SEG-CP5pb: stopped->diagnostic | tolerance 0.3552346400087883–1.568370208108398 px / 0.04179231058926921 xh (interval 0-0.08358462117853842) | clips 1/4 | non-clip FP 0/96 | KEEP 22/22 | CP3/CP4/CP5 unchanged: yes | tests: 416 passed
