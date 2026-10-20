# SEG-CP5b: fix round for SEG-CP5 (gpt-6.1-sol, medium, network OFF)

The SEG-CP5 review (`docs/records/reviews/SEG_CP5_review.md`) is a **FAIL**: 3 high (H1–H3) and 1 low, acceptance 1/4. Read it in full, plus `docs/records/briefs/SEG_CP5_build.md` (all its constraints still apply), ASTRA-SEG1 §4 and plan item 5, and the committed CP2–CP4 code. Use existing toolkit tools only: no recognizer/OSD, no new angle detector, no height/width-only final decision.

**Lead directions per finding** (if the evidence contradicts a direction, say so and keep the result honest):

- **H2 (KEEP l0019 and the upright controls falsely vertical).**
  - Drop the line-context tight-ink height/width override from the **final** decision: it fails the plan's "no height/width-only final decision" criterion. Use block/region context (`axis_regions`/`resolve_regions`) for the axis. Where line and block disagree, or the line is compact, the result is **abstain**, never vertical.
  - **Composition order:** admission applies the text rules first (short_line ≥ 10 letters; headings ≥ 4; numerics ≥ 4 digits). Report the orientation decisions **standalone** and **in composition** (only rows that pass the text rules reach the screen), separately. Compact upright tokens such as `ΟΙ` and `12` fail the text rules before orientation; say so, but keep their standalone numbers visible.
  - Diagnose l0019 specifically: why is it vertical, and which evidence is wrong?
- **H1 (2/4 rotated witnesses missed: b9f59878 l0034 horizontal, ebdc4d07 l0265 unknown).**
  - Diagnose each from its native evidence: crop, page region, `measure_orientation` outputs. What does the toolkit see?
  - Fix only with existing evidence (e.g. region context, row geometry: CP3 rows running across the crop's short axis are themselves vertical-axis evidence). Do not tune thresholds to the 4 witnesses.
  - If a witness is genuinely undecidable from the toolkit's evidence, it stays unknown. State whether `geometry_unavailable`-style fail-closed should apply to an unknown axis; the lead and coordinator will rule.
- **H3 (no native column-separator inventory, so 22 cases are unresolved).**
  - Find whether the existing toolkit computes separators/columns (page_lines, line_structure, boundary_evidence crossing, rules detection).
  - If it does, prepare that inventory with the **CP2 fallback mechanism**: at most once per source-bound page, explicitly counted, into a separate cache outside the run root, with full identity binding. Then resolve the 22.
  - If no existing tool produces it, say so precisely. The lead will then ask for a ruling (e.g. column-crossing is covered by CP3 row inclusion plus neighbour words, with no separate column evidence required).
- **L1:** update the receipt. KNOWN_ISSUES.md is written (sol-collect 7a026c3d).

No CP6+ work. No publish actions.

Update `seg/CP5_RECEIPT.md` and `seg/CP5_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP5b: done | rotated caught <a>/4 (unknown <u>) | KEEP false drops <b>/22 | upright standalone <c>/11, in composition <d>/<n> | horizontal misses <e> | unresolved required <f> | separator inventory: <prepared n pages|no existing tool> | acceptance: <k>/4 | tests: <n> passed`
