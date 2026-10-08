# T3 — O4d G1 v2: fix the regressions measured on real pages (gpt-6.1-sol, xhigh). Workspace = this repo. No `.git` writes (T3_HANDOFF.json).
Measurement (docs/O4D_G1_measure_v1.json; 400 real parliament lines, CLLG readings scored against the text layer; coordinator, 8 Oct 13:19):
v1 made crops WORSE: mean CER 0.106 → 0.136, median 0.042 → 0.082, exact matches 100 → 27 (the 100 silver lines: 100 → 20), worsened 272 /
improved 67, two-line split triggered 0 times, scan gate admitted 394/400. Visual diagnosis (tests/fixtures/o4d_lines/regressions/*_old.png =
text-layer crop, *_new.png = v1 output):
 - s2-411b3a86…-l00021: v1 ERASED every diacritic (breathings/accents are separate components above the body band; the neighbour-removal
   step dropped them and whitened their pixels). Polytonic lines lose all marks → CLLG output loses them. Unacceptable.
 - s2-60526f38…-l00104: v1 locked onto the intruding line below (largest-support cluster) and produced a blurred garbage strip.
 - rectified strips are visibly lower-contrast/blurred (interpolated resampling).
Required changes (keep the API; bump GEOMETRY_POLICY to v2; record in docs/O4D_GEOMETRY.md):
1. Never erase ink inside the line's own band. Define the band from the chosen baseline curve: [baseline − A, baseline + D] with
   A = 1.9 × body height (room for stacked breathing+accent and capitals) and D = 0.6 × body height; every component whose bbox overlaps the
   band is KEPT regardless of cluster; only components fully outside the band AND assigned to another baseline cluster are masked.
   Diacritic components (small, above the body band, horizontally over a kept body component) are always kept.
2. Target cluster = the baseline curve whose mean y is nearest to the original text-layer box's vertical centre (not the largest support);
   expose the choice and the alternative clusters in diagnostics.
3. Resampling: integer per-column row shift (nearest-neighbour), no interpolation; the strip must keep the source pixel values.
4. Ink-preservation invariant, tested on all 44 fixtures + the 4 regression pairs: ink mass of the refined strip within the band ≥ 0.97 ×
   ink mass of the original crop within the same band (count dark pixels), and ink above the x-height (diacritic zone) ≥ 0.95 × original.
5. Two-line split: lower BASELINE_CLUSTER_TOLERANCE handling so the fixture line01_large (two visible tracks) splits; keep determinism.
6. A `greekocr geometry measure` helper that, given a JSONL of {line_id, crop_path(original), bbox_pixel, page_image_path, text} and a
   reader callable, computes old/new CER/exact counts (the coordinator's script logic) so the measurement is reproducible from the toolkit.
Run the full suite; report counts. Last line exactly: `T3: done | tests: <n> passed`.
