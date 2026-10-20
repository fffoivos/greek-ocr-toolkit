# SEG-CP5′: the `edge_clip` screen from the existing native-extent mechanics (gpt-6.1-sol, medium, network OFF, no reading)

**Coordinator ruling (after the CP7 fresh-100 FAIL, 7b16c5cf):** an end-clip, i.e. a label carrying ink the crop cuts off at the left or right edge, is a drop. It is the geometry error class E3 found largest, and the owner's label rule is "the label is the ink". All earlier SEG constraints still apply: existing toolkit tools only, no new detector, ownership `801d517e` frozen, measure-only, no publish actions, and the live run root read-only.

## Build
1. **Rule `edge_clip`.** Using the **CP4 H2 code path** (full native component extent and parent provenance, shared-parent split letters resolved) plus the **CAPS3 edge-clip evidence** (find it in sol-collect or sol-recut, read-only):
   - for the **target** row, find its own native components that intersect the crop's **left or right** edge;
   - DROP when such a component's native extent continues **beyond** that crop edge by more than a tolerance;
   - a component that merely **touches** the edge, or ends within tolerance, is kept.

   Top and bottom edges are not part of this rule; neighbour words and merged rows already cover them.
2. **Tolerance:** state it in **pixels and in x-height units**. Calibrate it on the CP7 draw:
   - the 4 reader end-clips must DROP: nlg--6ae0ac01064a587e--s007-l0013, gazette_modern--feb39c43ac177ef8--s000-l0665, gazette_modern--73f0e4003296ba2e--s000-l0097, bsb_poly1850--9342f9a56a4065cd--s004-l0005;
   - the other 96 must KEEP (excluding the 2 geometry_unavailable, which stay unavailable);
   - **0 false drops on the 22 owner KEEP**, and all CP1 ledger numbers unchanged.

   Report the full tolerance curve (drops on clips vs non-clips) and pick the setting at the middle of the passing interval. If no interval passes, say so and stop.
3. **Admission integration.** Add `edge_clip` to the composed union and the admission tool (bump the version); `geometry_unavailable` behaviour is unchanged. Add a CP7 replay hook that counts `edge_clip` per source × class.
4. **Tests:**
   - planted cases: a last glyph cut mid-body → drop; a glyph touching the edge → keep; a punctuation stop cut → drop; a left-edge first-letter cut → drop; a shared-parent split letter at the edge → resolved, not a false drop;
   - the 4 clips and the 22 KEEP as regressions;
   - every CP3/CP4/CP5 acceptance number unchanged.

**Note:** this calibrates on the CP7 draw. Per the plan, the gate is a **new** fresh 100 after the refreeze, which is a later brief.

Write `seg/CP5p_RECEIPT.md` and `seg/CP5p_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP5p: done | tolerance <px> px / <xh> xh (passing interval <a>-<b> xh) | clips 4/4 | CP7 non-clip false drops <n>/96 | KEEP 22/22 | CP3/CP4/CP5 unchanged: yes/no | tests: <n> passed`
