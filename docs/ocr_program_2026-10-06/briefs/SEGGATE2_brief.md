# SEG-GATE-2 — segmentation 0.8: exactly the owner's three rules, remove the coordinator's additions (gpt-6.1-sol, xhigh, network OFF)

Workspace: this worktree. Start from `sol/seg-gate` (commit 67e670ba = 0.7; hand-off `docs/records/harvest/collect_v3_admission/segeval1/gate/HANDOFF.md`). Create `sol/seg-gate2` (bundle fallback as before, `segeval1/gate2/SEGGATE2.bundle`). Never push. Do not touch the five pre-existing uncommitted edits. `.venv/`. Mac replay of the 150 + 888 authorised. No Clariden, Slurm, readers.

## Owner's rules (19 Oct, verbatim) — the complete policy, nothing added
"The rules are
1. detection of other lines, at least two words cutoff doesn't count
2. Comparison of de skewed lines' long sides normalized for height (the deskewed line's) with google output
3. And also height of deskewed line box x 1.5 + bounding box's height"
and: "stop adding rules I didn't tell you to".

## Policy 0.8 = 0.7 minus the two coordinator additions
Keep from 0.7: the crop-only line inventory (Stage A: all rows, visible fraction, bodies, whole vs cut-off word groups per other row; context optional, never required) and the order inventory → other-lines gate → length → padding.
1. **Other lines** (gate): DROP when whole words from other rows > 2 (cut-off words do not count); keep the existing "second complete line" DROP exactly as it is in the owner's frozen 0.5 policy (`detectedRowsJudgement`: additional complete line = DROP), fed by the crop-only inventory. UNCERTAIN only when no main row / orientation unresolved, as today.
2. **Length**: the 0.6 row-frame (de-skewed) box of the main row's text components; long side normalised by that box's height through the unchanged predictor; `boxLengthJudgement` and 0.5–1.5 byte-identical.
3. **Padding**: `paddingJudgement` unchanged, input `(segment_height − upright_box_height) / row_frame_height` (= crop height allowed up to upright box height + 1.5 × de-skewed line height).
**Remove entirely**: the row-frame-taller-than-upright guard and the "gate: target line cut" test (baseline crossings, low-visibility spans, cut letters). Keep `skew_line` cut evidence in the evidence record as diagnostics only (the owner sheets display it); it must not affect any verdict. No other rule, threshold, epsilon, cap or detector change.

## Checks
- Unit tests: adjust `tests/test_seg_gate.py` (the 847e1ec1 witness now decides by length: report its ratio and verdict, do not force it; b8b6779d KEEP; two vs three whole words; second complete line; θ=0 identity with 0.6 to the digit).
- Replay the 150 and the 888 as in SEG-GATE-1 (same scripts, `segeval1/gate2/`), owner-standard scoring, confusion tables for 0.5 / 0.6 / 0.7 / 0.8 side by side, flip table 0.7→0.8, rated agreement on the 888 (owner_rating.decision). Readback validation as before.
- Scope guard: diff limited to the policy script (new sha, version 0.8), the segmentation stage, versions builder; predictor and both judgement functions byte-identical; pre-existing edits untouched. State explicitly that no rule beyond the three exists in the policy, with the policy's rule list in the hand-off.

Hand-off `segeval1/gate2/HANDOFF.md`; last line exactly:
`SEGGATE2: done | 150 owner-standard 0.8: FP <n> FN <n> UNC <n> | 0.7: FP <n> FN <n> UNC <n> | 888 rated agree <n>/135 | 888 flips 0.7->0.8 <n> | tests <n> passed | commit <sha>`
