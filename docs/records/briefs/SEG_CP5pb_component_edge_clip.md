# SEG-CP5′b: a component-based `edge_clip` within the target band (gpt-6.1-sol, medium, network OFF, no reading)

**Coordinator ruling** after the CP5′ FAIL (`docs/records/reviews/SEG_CP5p_review.md`: the row-based rule had no passing tolerance, because for 2/4 clips the recorded target row ends inside the crop) is **Option A, one round only**. All CP5′ constraints still apply: existing tools, no new detector, ownership 801d517e frozen, measure-only, no publish actions, live root read-only.

## Rule
`edge_clip` drops a row when there is a native component that meets **all** of these:
- it is **cut by the crop's left or right edge**, whatever its row assignment;
- it overlaps the **target row's vertical band** (from CP2/CP3 row geometry: the target's body band) by **≥ 50%** of its own height;
- it is **letter-scale**: height ≥ 0.5 × the target x-height, using the existing letter roles (marks and noise excluded);
- its **native extent continues beyond the crop edge by > t**.

Use the CP4 H2 native-extent code (full parent provenance; shared-parent split letters resolved).

## Calibration, exactly as ruled
On the CP7 draw:
- the 4 clips DROP (nlg 6ae0… l0013, gazette feb39… l0665, gazette 73f0… l0097, bsb 9342… l0005);
- **0/96** non-clip false drops (the 2 geometry_unavailable stay unavailable);
- **22/22** owner KEEP;
- every CP1 ledger number unchanged.

Report the full curve. Take **t at the middle of the passing interval** (px and xh). **If no interval passes, STOP** and write `CP5pb_GATE_FAIL.md`. The coordinator has pre-ruled the fallback (option C): end-clips are admitted as a known class. In that case, keep the measure as a **non-gating diagnostic** `edge_clip_candidate` with a replay counting hook per source × class, at the tolerance that best separates the classes (state it), and clearly not a drop rule.

## If it passes
- Add it to the composed union and the admission tool (version bump) with the replay hook.
- Tests: planted cases (cut last glyph → drop; touching → keep; cut stop → drop; left first-letter cut → drop; a neighbour-column glyph cut at the edge but outside the target band → keep; marks or noise cut → keep), with the 4 clips and the 22 KEEP as regressions.
- CP3/CP4/CP5 unchanged.

Update `seg/CP5p_RECEIPT.md` (section b) and the commit list. The last line must be exactly:
`SEG-CP5pb: <pass|stopped->diagnostic> | tolerance <px> px / <xh> xh (interval <a>-<b>) | clips <n>/4 | non-clip FP <n>/96 | KEEP <n>/22 | CP3/CP4/CP5 unchanged: yes/no | tests: <n> passed`
