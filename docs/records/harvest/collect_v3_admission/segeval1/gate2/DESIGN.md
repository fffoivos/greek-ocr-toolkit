# SEG-GATE-2: policy 0.8

The complete policy has exactly the owner’s three rules, in order:

1. Crop-only inventory, then other-lines gate: an additional complete line is DROP, as in frozen 0.5; more than two whole words from other rows is DROP. Cut-off words do not count. Missing main row or unresolved orientation stays UNCERTAIN. Inventory detectors and thresholds are unchanged from 0.7; context is optional diagnostics.
2. Length: measure the main row text components in the 0.6 de-skewed row frame and run the unchanged height-normalised predictor and byte-identical boxLengthJudgement (0.5–1.5).
3. Padding: byte-identical paddingJudgement using (segment_height − upright_box_height) / row_frame_height, with the unchanged 1.5 allowance.

Remove the row-frame-taller-than-upright flag and the target-line-cut veto. Keep skew_line crossings, cut spans and cut letters as diagnostics only; no verdict reads these. Keep diagnostic heights without comparing them. No rule beyond these three exists in the policy; no threshold, epsilon, cap or detector is added or changed.

Replay the same 150 and 888 local inputs with fresh native crop evidence, using the same offline replay workflow, saved 0.5/0.6/0.7 decisions, owner-standard scoring and owner_rating.decision. Validate every decision, invariant diagnostics, context independence, Stage-B equality with 0.6, predictor outputs, source scope, generated fingerprints and protected edits. Package sol/seg-gate2 from exact implementation 67e670ba in an isolated writable Git directory and the authorised bundle fallback; never push.
