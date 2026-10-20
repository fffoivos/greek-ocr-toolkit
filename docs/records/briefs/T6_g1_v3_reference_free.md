# T6 — G1 v3 cutter + reference-free crop evaluation (gpt-6.1-sol, xhigh). Workspace = this repo. No `.git` writes (T6_HANDOFF.json). No network, no GPU.
Owner review (8 Oct 14:05) of docs/O4D_G1_measure_v1/v2: "attempt 1 is consistently better than the original line"; the previous gate
("exact matches with the PDF text layer") was WRONG because the text layer is just another OCR. Rule: the layer is never a reference.
Build:
1. `refine_line(..., policy='v3')`: attempt-1 neighbour removal (components assigned to another baseline cluster are masked, as in v1)
   COMBINED with the diacritic-keeping band of v2 (any component overlapping [baseline − 1.9·body, baseline + 0.6·body] is kept; small
   components above the body horizontally over a kept body component are always kept); nearest-cluster target; nearest-neighbour row shift.
   Keep v1/v2 selectable for comparison; GEOMETRY_POLICY 'o4d-local-line-geometry-v3'.
2. `greekocr.real.geometry.crop_quality(original_crop, refined_crop, diagnostics) -> dict` — reference-free signals computed from pixels only:
   diacritic_ink_retained (dark pixels in the zone above x-height, refined/original, over the shared x-range), body_ink_retained,
   neighbour_ink_removed (dark pixels outside the line band removed, fraction), clipped_left/right (ink touching the strip edge),
   curl_residual_px (after rectification, the fitted baseline's remaining deviation), contrast and blur deltas. Plus hooks for reader-based
   signals supplied by the caller: `reader_confidence` (mean per-character log-probability from a reader that exposes it) and
   `inter_reader_agreement` (CER between two independent readers' outputs on the same crop).
3. CLLG worker confidence: in the vendored worker copy (greekocr/_vendor/scripts/fetch/r2_cllg_worker.py or the toolkit's reader wrapper),
   add an optional `--confidence` mode that returns, per crop, the text AND the mean/min per-character confidence from Kraken's prediction
   records (records[0].confidences); keep the plain mode byte-identical. Tests mock the worker protocol.
4. `greekocr geometry evaluate --records lines.jsonl --page-images ... --policies original,v1,v2,v3 --readers cllg[,ours] --out DIR`: for every
   line and policy produce the crop, the pixel signals, each reader's text + confidence, inter-reader CER, and a summary table per policy:
   mean reader confidence, mean inter-reader agreement, diacritic retention, neighbour removal, clipping rate — NO text-layer column except
   as a clearly labelled diagnostic. Also emit `ab_pairs.json` for a blind A/B page: per line the policy crops in a shuffled order with the
   mapping kept separately.
Tests on the 44 fixtures + 4 regression pairs: v3 retains ≥ 0.97 diacritic and body ink vs original on every fixture; neighbour ink removed
on the two neighbour-intrusion fixtures; determinism; evaluate CLI runs with a mocked reader. Docs: update docs/A_ocr_development/reference/O4D_GEOMETRY.md (why the
previous gate was invalid; the new signals). Last line exactly: `T6: done | tests: <n> passed`.
