# Shared modules

All A01–A12 use S0 manifest, S1 baseline, S3 geometry, S4 contracts/context, S5
references, S6 review, S7 registry/timing. S2 image evidence serves A02–A08/A10/A12;
A09 receives its evidence through requests/fields. S8 is the one composition/scout;
S9 owns the deterministic synthetic perturbations.

- `manifest.py`: only the 54 dev files and 120 exact selection entries; content hashes.
- `detector.py`, `paddle_db.py`: one source-pinned CPU ONNX adapter, eight fixed DB variants.
- `image_evidence.py`: lazy paper, contrast, gradients, persistence, components, runs, strokes.
- `geometry.py`: coordinate scaling, body proxy, strips, continuity, robust fit, pitch.
- `contracts.py`, `context.py`: typed products, request union, seam dedup, one page record/cache.
- `references.py`: dense raw-ink supports, original-resolution crop pairs and cached old guides.
- `review.py`: one discount-safe overlay, detector JSON writer and static gallery.
- `timing.py`: raw times and duplicate-experiment registry; successful keys reuse artifacts.
- `scheduler.py`: independent image coverage plus explicit unresolved work requests.
- `perturbations.py`: seeded known changes; synthetic results kept separate.

Every shared module has a focused test in `../tests/test_shared.py`. Algorithm smoke
and semantic tests are in `test_prototypes.py`. The implementation has no production
page-API imports. Geometric floors of one raster sample represent quantisation;
Paddle's minimum contour sizes/stride are source-defined network units. Other lengths
are local body-height multiples or page fractions. A bootstrap height is not x-height.

Reference line paths are centre supports, never labelled baselines. Old guides and
cached detectors are hypotheses. Unknown ownership is retained and rendered; a
line marked discounted is omitted from every overlay. JSON score null is deliberate
for candidates with no calibrated detector score.

## Perturbation artifact correction — prediction before execution

The first seven-variant run saved correct altered images, but the blur and
thickening change arrays were zero placeholders. Prediction: replacing these
with exact absolute changed-pixel arrays will expose nonzero support on those
two variants for all eight exemplars, with no change to the rendered variants
or their photometric measurements. Preserve the complete first generation and
its source. This is a correction to S9 evidence, not another detector experiment.

Duplicate check: E00 and A01–A12 are reused. Only EP receives a new source identity.
Next: verify pixel differences and equality of the first/new measurements, then
link both generations and retain the limitation that only photometric witnesses
were tested.

Result: all 56 variant measurements and all rendered JPEGs are byte/value identical
to v1; all 16 blur/thickening arrays now carry nonzero changed-pixel support.
The first generation is retained as `out/shared/perturbations-v1`. The corrected
record is `out/shared/perturbation-correction.json`. No prototype was rerun.
Next: use these as physical counterexamples for each witness in round 2; the
current report retains the incomplete per-prototype falsification work.

The main/variant/comparator detector JSON now uses one `detector_record` export
boundary. It clips page coordinates and removes discounted candidates without
mutating algorithm products. The final optional-export audit checked 2595 files;
three had only a floating-point edge overrun. Their original JSONs are retained.
The extracted PaddleX classes retain their source notice; `LICENSE-PaddleX` is
the license copied from the installed PaddleX 3.7.2 distribution.
