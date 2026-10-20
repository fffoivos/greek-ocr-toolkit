# T6a2 reuse addendum — step 0 first

Recorded 2026-10-16 UTC before adding the opt-in library. Network OFF; F2 only; T6a remains a recorded negative and `vertical_recut.py` is immutable.

## Inference placement

`greekocr/glyphs/lines_api.py:separate_lines` straightens crop-local fitted lines. `greekocr/glyphs/page_lines.py:page_lines` is the older box-seeded boundary algorithm. Neither is the current deployment cutter. The 046bd52 runtime is present unchanged in `greekocr/pages/lines.py`, `pixels.py`, `tables.py`, and `glyphs/recut.py` (checked with `git diff 046bd52 -- ...`).

The actual deployment consumer is `greekocr/deploy/docling_plugin/model.py:GlossapiOcrModel._detect` (class name to be verified), in its `for piece in pieces` loop, immediately before `extract_line_image(image, piece.line)`. `process_page` has already called `segment_page(image)` and `prepare_delivery`. `piece.box` is the native original rectangle from `tables.line_piece`: x0/x1 and floor(min(top))/ceil(max(bottom)), clipped to the page. `extract_line_image` currently resamples the native page within the tessellated ribbon.

The proposed opt-in call is `mask_foreign_ink(image, piece.line, runtime_neighbours, piece.box)`. All line centre curves come from the runtime's own `LineSegment.baseline` and `LineSegment.meanline`: centre=(baseline+meanline)/2; body rise=median(baseline-meanline). No Google geometry, reference text, or cached ownership is required by the masking function. The returned crop can be pasted into a private copy of `image` at `piece.box[:2]` before the unchanged `extract_line_image`; source geometry and raster are not mutated. Training uses that same call on the native page and original saved training rectangle, with the same runtime-detected curves. Google-box-derived fits are a comparison arm only.

## Reuse and step-0 gate

Ownership must directly call existing `recut._voronoi_keep`; no new centroid score or segmentation. A reversible integer column translation of the binary working grid adapts curved native coordinates to its constant-own-centre interface. The native output pixels are never resampled. The crop is only an output intersection: ownership receives surrounding page context so clipped fragments are not independently reassigned. Neighbours are nearest overlapping-X runtime centre curves above/below; absent neighbours are infinite (no invented line). `_voronoi_keep` exposes no ownership tolerance keyword parameters, so there is no tuning grid.

Before building the public masker, run a small offline probe on one F2 development page from each source. Compare the exact same ownership function using equivalent runtime curves through serialized training and native runtime adapters (must be bit-identical). Also run the fresh runtime and Google-box-derived `fit_box(..., splits=False)` curves on those pages, report matching coverage, mask equality, ink-pixel agreement and masked-set intersection/union. Actual detector/Google disagreement is a geometry limitation, not equivalent-input equality. Training must use runtime curves to avoid making that disagreement a train-only pixel edit.

STOP if identical application with runtime inputs is unavailable. Step-0 outcome and measured agreement will be appended here before the public library is created.

## Step-0 decision: PASS, before public implementation

The fresh `process_page` runtime ran on four F2 dev pages (one per source). Exact equivalent-input ownership masks matched 187/187 training rectangles and 187/187 runtime `line_piece` rectangles. Google-fit comparison: 165/187 complete masks equal; 645/1,128,287 ink pixels differ (99.9428% agreement); masked-set intersection 102,825 / union 103,470 (99.3766% IoU). Per source: Gazette 43/46 masks equal, 99.8865% ink agreement; Lekythos 88/99, 99.9046%; Kosmopolis 17/17, 100%; IA 17/25, 99.9654%. These results establish application identity with equivalent curves, not physical ownership truth or zero own-ink loss. The Google curves are deliberately not used as training-mask inputs.

Measured receipts and page identities: `step0/agreement.json` and `step0/{source}.json`; executable adapter: `probe.py`; log: `step0.log`. The native runtime source files listed above are byte-identical to 046bd52. The exact deployment class name is `GlossapiOcrModel`.

The gate passes because the same native page, runtime centre curves, neighbouring detected lines and rectangle are available at training and at the deployment cutter. There is no provider-specific requirement. The proposed function remains opt-in; the deployment consumer and all existing defaults will remain unchanged. Next: move the tested adapter into the library, add ring fill and native safety/identity tests, then freeze before harm inference.

## Public-function verification

After the gate, `verify_step0.py` executed `mask_foreign_ink` on exact serialized training curves and `mask_detected_line` on native `process_page` objects. All 187 original training rectangles had identical mask bytes, filled raster bytes and records. All 187 corresponding detector-native rectangles also agreed; pasting each result into a private native-page copy and calling the actual `extract_line_image` produced identical runtime strips. See `step0/public_function_identity.json`. This verifies the proposed insertion in `GlossapiOcrModel._detect` through the existing extraction call; it does not enable that insertion by default.

Concrete opt-in insertion at that loop:

```python
from greekocr.glyphs.foreign_ink import prepare_mask_page, mask_detected_line
# Once after analysis, before the for-piece loop:
mask_page = prepare_mask_page(image)
runtime_neighbours = [l for l in analysis.segmentation.lines if l.discounted is None]
# Within the existing loop, before extract_line_image:
proposal = mask_detected_line(mask_page, piece.line,
                             runtime_neighbours, piece.box)
private_page = image.copy()
private_page.paste(proposal.image, piece.box[:2])
crop = np.asarray(extract_line_image(private_page, piece.line), dtype=np.float32) / 255.
```

Training calls the same `mask_foreign_ink` on the original native rectangle. Detector curves are full precision; the existing rounded `to_record()` curves are not substituted. The F2 runtime is executed only to supply these curves: it adds no output rows or segmentation to the training data. A missing training-target match conservatively retains the original and is counted. The fixed training binding selects the nearest body centre to the original rectangle centre among detector lines with at least 50% horizontal overlap and at most 1.5 x-height centre distance. This binding is not an ownership rule or a tuned parameter. The inference caller already has its own explicit target line.

## Ownership limits established before inference

The existing function exposes no tolerance parameters. Its nearest-centroid rule can erase a detached own mark situated closer to the neighbouring centre. The contract suite includes ordinary accents/breathings, descenders, apostrophe/coronis, iota subscripts, end punctuation, and a component touching two bodies; it also preserves an explicit high-detached-mark counterexample as a characterization test. Passing the tests must not be reported as universal own-ink safety. No saved training-owner mask is used to protect the output: cached labels are used only for independent loss measurement.

The integer column translations adapt the existing straightened working grid without resampling output pixels. Context is the existing 4.2-x-height recut window, enlarged to observe the complete original rectangle, with original line/crop X extent. `_neighbour` is reused unchanged (including its 1.2–4.5 x-height pitch and 2-x-height overlap gates). Missing neighbouring sides use infinity, so they cannot erase ink. Ring fill is native-page, per component, RGB channel-wise median over the 1-to-3-pixel Chebyshev annulus excluding all foreground. Empty rings abstain; there is no white fallback. Crop summaries are unweighted medians of component statistics; the complete per-component values are retained.

The inference recipe explicitly uses the same non-discounted detector neighbour set as the training adapter and the step-0 proof. `process_page` normally retains discounted records for diagnostics, so passing that unfiltered diagnostic list would be a different input. The masker accepts either set; this experiment freezes the non-discounted set. No training-only source is needed for that filtering.

## Frozen development outcome

Parameter SHA256 `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8` was frozen at 2026-10-16T23:09:34.795863+00:00, before harm inference. On all 160 dev cards: 152 changed, including 94/102 crop-ok-y cards; cached own-pixel loss is 387/510,558 over 14 component appearances on 11 y cards. No protective override was added. Native inspection confirms the gamma descender (IA c023), capital E serif (IA c040), and Latin f serif (IA c019) are really shortened. Tracing the unchanged function shows their components are closer to their own centre but touch a neighbouring body band, so the existing midline-cut branch is taken. `dev/confirmed_loss_mechanisms.json` reproduces each complete frozen mask exactly. Zero own-ink loss is therefore falsified, independently of semantic uncertainty about the smaller removed dots.

The visual removal count is 56/57 overrun cards with at least one previously readable neighbouring fragment substantially removed; this includes partial improvements and is not a claim of complete cleanup. Gazette c015 retains its readable E.S.Y.E. neighbour while cached foreign pixels were zero. Several older scans retain faint outlines around filled foreground. The cached foreign-component measure and visual observations are reported separately.
