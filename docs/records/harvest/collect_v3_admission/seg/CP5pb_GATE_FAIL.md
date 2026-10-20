# CP5pb GATE FAIL — option C

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
