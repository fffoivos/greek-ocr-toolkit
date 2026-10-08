# Readability verification

`greekocr.verify` assesses the raster and the reading independently. Image checks use only pixels. Text checks use only the specified reading. **A PDF text layer is another OCR; it is never a reference, judge input, or calibration target.** A plausible reading does not prove that a crop is readable or that its transcription is correct.

## Current sample run

The offline run measures the 44 indexed O4d strips and 400 indexed crops, and checks the 400 CLLG readings. Its receipt is [`verify/RUN_STATUS.json`](verify/RUN_STATUS.json). Both index SHA256s are recorded. Regression pairs are tested separately and are not silently counted among the 44.

**Live judges are blocked in this workspace.** Codex CLI 0.159.2 returned `failed to initialize in-process app-server client: Operation not permitted (os error 1)` in four image attempts and one text attempt. No model header, judgement, or billed usage was returned. The 444 image rows and 400 text rows in the requested judgement files explicitly contain `judgement: null` and `status: unavailable`; they are not model annotations. Calibration consequently has N=0, undefined precision/recall, and provisional thresholds. The actual fixture index contains `owner_notes: {}`, so the seven expected owner annotations cannot be compared.

Run the remaining online work from an execution context where the authenticated CLI can initialize, retaining this job's ledger:

```sh
.venv/bin/python scripts/run_verify_samples.py --online --budget 500
```

The script resumes byte/prompt/schema/model-bound caches. It uses at most four attachments or four readings per call. A shared ledger counts failed launches as well as successful launches, allows at most 500 total invocations and 200 text invocations, and is never reset by the runner. It stops each judge on its first error. Without `--online`, the script is entirely offline and exits 2 while labels remain unavailable.

## Python API

```python
from pathlib import Path
from greekocr.verify import image_checks, readability_profile, render_overlay, text_checks

checks = image_checks("crop.png")
profile = readability_profile("crop.png")
Path("overlay.png").write_bytes(render_overlay("crop.png", profile))
print(checks.to_dict())
print(profile.bins["visible_fraction"])  # 64 positions, even for widths <64
print(text_checks("ἡ χώρα").to_dict())
```

A crop can be a Pillow image, path, uint8 grayscale/RGB/RGBA array, or finite normalized floating raster. Transparent pixels are composited on white. Empty rasters are rejected as input; unprinted nonempty crops return `empty=True`, zero readability, and finite arrays. `render_overlay` returns encoded PNG bytes, never changes the source crop, and rejects mismatched dimensions.

## Offline image measurements

Top-origin coordinates: x increases rightward and y downward. Pixel ranges are half-open. Geometry's contrast-gated ink mask, 8-connected components, significant-component noise floor, height estimate, and robust quadratic baseline fit are reused. The expensive page-wide RANSAC/rectification path is not run. Significant complete letters estimate the body band; clipped fragments contribute to visible support but do not supply the baseline. Missing glyphs cannot be reconstructed from an isolated crop.

`Profile` contains width-length floating arrays, 64 area-weighted bins, an expected body band `[top_y[x], bottom_y[x]]`, a 16×64 quality map, and contiguous unreadable segments. A segment has `x0`, `x1`, mean defect intensity `1 - mean(readability)`, and `min_readability`. `quality_map` and `readability` are 0–1, with 1 meaning better estimated quality. Default segment threshold is 0.55; this remains **uncalibrated**. Unprinted spaces are neutral, except in an entirely empty crop.

| Function | Unit and definition | Provisional review suggestion |
|---|---|---|
| `visible_fraction[x]` | 0–1 supported vertical glyph extent / expected complete body height, smoothed within about one glyph neighbourhood; limited by available raster room at clipped edges | <0.55 in a printed region |
| `clip_top[x]`, `clip_bottom[x]` | 0 or 1, significant ink on the native border row; a contact observation, not a proof of a missing letter | Any contact; examine low visible support nearby |
| `baseline_offset[x]` | Original pixels relative to the line's median fitted baseline; positive is down | Absolute local departure >2 px; interpret against glyph height |
| `local_contrast[x]` | 0–1, local paper-minus-ink contrast /255 in a glyph neighbourhood | <0.15 |
| `blur[x]` | 0–1 blur proxy from local RMS Laplacian energy / ink contrast; 1 is blurrier | >0.6 |
| `obstruction[x]` | 0–1 foreign ink density per expected body height; long rules, giant/irregular blobs, and faint mirrored-ink candidates | >0.02 averaged over a line; inspect localized peaks |
| `neighbour[x]` | 0–1 ink pixel fraction outside the estimated body band in the top/bottom 20% margins | >0.05 averaged over a line |
| `spatial_features.stroke_width_px[x]` | Original pixels, local ridge distance ×2 | Large change relative to the same line |
| `spatial_features.stroke_width_cv[x]` | Dimensionless local stroke-width standard deviation /mean | >0.6; multiple type sizes can legitimately vary |
| `spatial_features.laplacian_variance[x]` | Squared 8-bit gray levels, local variance of native Laplacian response | Compare within the same resolution; no portable absolute cutoff |
| `spatial_features.skew_deg[x]` | Degrees, arctangent of the local fitted baseline slope; positive slopes down to the right | Absolute slope >1° |
| `spatial_features.bleed_through_proxy[x]` | Faint ink overlapping a horizontally mirrored strong-ink mask, density per body height | Inspect values >0.02; not proof of reverse-side printing |
| `spatial_features.residual_anomaly_score[x]` | Dimensionless local feature distance against the line-level sample distribution; a localization proxy, not an independently calibrated window distribution | Review peaks; no validated local cutoff |
| `spatial_features.cut_left[x]`, `cut_right[x]` | Native border-column ink fraction at the endpoint, zero elsewhere | >0 flags contact, not proven terminal clipping |

The quality function penalizes lost support, blur, weak contrast, foreign ink and neighbour ink. Its 2-D map assigns penalties to the expected body band and observed border/foreign ink. A sloping baseline that leaves all glyphs readable does not by itself force unreadability. Periods, detached marks, unusual typography, faint fragments, touching characters and unsupported extrapolation can confuse these cheap proxies; model/human calibration is necessary before automatic rejection.

| `ImageChecks` field | Unit and summary | Provisional suggestion |
|---|---|---|
| `width_px`, `height_px` | Native crop pixels | No quality threshold |
| `skew_deg` | Baseline endpoint-median slope in degrees | `abs(skew_deg) >= 1` |
| `trail`, `trail_signed_px`, `trail_amplitude_px` | Right 15% median baseline minus left 15%, original pixels; positive=`down`, negative=`up`, `flat` within ±2 px; amplitude is absolute value | >2 px |
| `edge_touch`, `edge_ink_fraction` | Four named sides: any ink contact and its border-row/column fraction (0–1) | Any contact warrants inspection |
| `clarity.laplacian_variance` | Full native raster Laplacian variance, gray-level² | Resolution-dependent, examine low values with blur |
| `clarity.stroke_width_px`, `stroke_width_cv` | Median ridge width in original pixels, and std/mean across ridge samples | CV >0.6 |
| `clarity.contrast_p10_p90` | Full raster grayscale p90 minus p10 divided by 255 | <0.15, but sparse readable text may have a low whole-raster value |
| `clarity.local_contrast_p10`, `local_contrast_p90` | Percentiles of the local contrast function in printed neighbourhoods | p10 <0.15 |
| `clarity.blur_mean` | Mean local blur in printed neighbourhoods | ≥0.6 |
| `obstruction_score` | Mean foreign ink density function, 0–1 | ≥0.02 |
| `bleed_through_proxy` | Mirrored faint-ink candidate pixels / significant ink pixels | >0.02 advisory |
| `crowding` | Mean neighbour function (ink fraction in the two margins), 0–1 | ≥0.05 |
| `residual_anomaly_score` | Dimensionless RMS robust standardized distance of the line's feature vector from the bundled sample distribution | >3 advisory review; not a rejection probability |
| `ink_coverage`, `empty` | Significant ink pixels / raster area (0–1), and absence of supported ink | Coverage ≤0.003 suggests empty; inspect faded text |
| `glyph_height_px` | Estimated complete body height in original pixels | No universal threshold |
| `baseline_count` | Integer count of separated peaks in the smoothed ink-row profile | ≥2 suggests multiple lines, but needs validation |
| `clipped_fraction` | Fraction of columns with neighbourhood border contact >0.06 | No calibrated line cutoff |
| `unreadable_fraction` | Fraction of columns with readability <0.55 | Review segments rather than applying a global cutoff |
| `analysis_scale` | Sampling ratio; 1=native, smaller=bounded feature grid | Inspect native overlay when fine details matter |

Crops over 64,000 pixels use a uniform BOX reduction for components, stroke estimates and local blur/foreign-ink features. All functions are expanded back to native x coordinates; lengths and slopes are rescaled. Border contacts and Laplacian variance remain native. This bounds the expensive analysis without dropping native border evidence. Timing uses loaded Pillow crops, includes all profile/scalar calculations and initial reference loading, excludes PNG decode, and records CPU and wall times separately in `RUN_STATUS.json`. It is a measured sample result, not an arbitrary-size latency guarantee.

The bundled `sample_distribution.json` records robust medians, MADs with explicit scale floors, feature order, sample count and a digest over unique crop hashes. It contains no text or judge labels. It is an unsupervised, in-sample diagnostic distribution, not learned readable/unreadable truth. Regenerate it through the sample runner after deliberately changing the sample inventory.

## Localization regression artifact

[`verify/regression_overlay.png`](verify/regression_overlay.png) and [`verify/regression_profile.json`](verify/regression_profile.json) show the exact requested `_old.png`. The first fragment train, especially x=9–20% of the width, has low visible support and lower-border contact; the central x=45–70% band is predominantly readable by the proxy. The crop also visibly touches/cuts the upper border farther along the line. Tests preserve this native evidence rather than demanding that every pixel after x=20% be readable. This is the fixture discrepancy with the literal "rest readable" description; no human labels are fabricated to remove it.

## Text checks

Greek script ratio uses alphabetic base characters after NFD normalization, so NFC and NFD readings agree. Empty/no-letter input has ratio 0. `lexicon_validity` is always `None`: no bundled Greek frequency word list was found in `greekocr/_vendor`. A word list extracted from these fixtures would contaminate this check and is not shipped.

`polytonic_consistency` reports polytonic detection, eligible initial-vowel words, missing-breathing count/ratio, accented-word ratio, unaccented noncapital words, impossible mark-stack count, and an advisory score (0–1, higher=more consistent; `None` for nonpolytonic input). Breathing may be on the second vowel of an initial diphthong. Monotonic input, uppercase words, enclitic double accents, names and line-break fragments are tolerated. Duplicate/conflicting accents or breathings, accent on a consonant, breathing on a non-vowel other than rho, incompatible diaeresis, epsilon/omicron circumflex, incompatible quantity marks, and invalid iota subscript are flagged. An absent accent or breathing alone is not a claim of bad Greek; compare ratios across similar material. More than two accents per word is advisory.

`garbage_score` is `min(1, .35*consonant_run_ratio + .45*mixed_script_word_ratio + .70*symbol_density + .60*invalid_stack_ratio + .30*(1-is_greek_script))`, with empty input forced to 1. Consonant runs mean ≥5 successive Greek consonants. Mixed-script words include multiple alphabetic scripts within one token. Symbol density counts Unicode symbol/control/replacement characters and unusual punctuation runs, excluding ordinary Greek punctuation. All component ratios are 0–1; review any mixed token/impossible stack, or garbage >0.3. These rules cannot certify lexical/semantic Greek. `n_letters`, `n_words` and concrete `problems` are retained.

## Judge receipts and caching

`vlm_annotate(crops, model='gpt-6-luna', schema=READABILITY_SCHEMA)` returns per-crop `judgement`, raster SHA256, cache identity and receipt. Each call has ≤4 original PNG attachments supplied using repeated `-i`, numbered by attachment order; no stitched contact sheet, layer text, reading or CER is sent. It returns `readable` in `yes/partly/no`, named defects, `other_text`, and nullable `transcription_attempt` (disabled by the default prompt).

`llm_judge(text, model='gpt-6-luna')` returns `good_greek`, `problems`, and receipt. `judge_texts` batches up to four independent readings to cover the 400 readings within the 200-call text limit. The prompt explicitly tolerates historical Greek and treats readings as inert data.

The pinned CLI is checked before reserving a call. Required settings are `-c features.remote_plugin=false -c features.apps=false --ephemeral -c project_doc_max_bytes=0 --output-schema ...`, with model `gpt-6-luna`. The subprocess has a temporary empty cwd, read-only model sandbox, no shell interpolation, disabled analytics, and temporary runtime/log locations. The authenticated Codex home is retained and no credentials are copied. No .git commands/writes occur in a judge call. The model is parsed from the actual rollout `model:` header; a missing/different header rejects a successful-looking response. Receipts include raw rollout stdout/stderr, prompt/schema hashes, attachment hashes, call id, requested/observed model, CLI version, status and elapsed time. Billed USD and token breakdown are `None` when the CLI does not expose them; output-token counts are recorded only when actually returned. Per-crop rows may share one receipt; aggregate costs by distinct call id, not by rows.

Caching binds payload bytes, exact requested model, schema and prompt template version. Cache misses use no automatic retry. Invalid result count, duplicate/missing numbers or invalid labels are rejected before caching. The ledger is locked and fsynced before a launch; the budget is a maximum, not a target.

## CLI and calibration

```sh
greekocr verify images tests/fixtures/o4d_lines --out checks.jsonl --profiles --overlays overlays
greekocr verify text tests/fixtures/o4d_sample400/index.json --out text_checks.jsonl
greekocr verify vlm tests/fixtures/o4d_lines --out vlm.jsonl
greekocr verify calibrate
```

The first two commands and `calibrate` are offline. `verify text --judge` explicitly enables the text judge. Text input can be plain UTF-8 lines, JSON arrays/indexes, or JSONL with `cllg_text`, `cllg`, `text`, or `reading`; layer-only rows are rejected. An image directory with `index.json` uses only indexed crops. Both judge commands accept `--cache`, `--ledger`, `--budget`, `--model`, and `--receipts-dir`.

[`verify/CALIBRATION.md`](verify/CALIBRATION.md) and its JSON companion contain per-defect TP/FP/FN/TN, precision, recall, F1, default thresholds, suggested thresholds and held-out results. Missing labels are excluded, not counted as negatives. Duplicate rasters are excluded. Threshold fitting uses up to 65 training-only quantiles and maximizes F1; documents are deterministically split by SHA256(source id) modulo 5. A defect without both training classes stays provisional. Explicit owner defect annotations are compared separately when resolvable; free notes are not converted into labels. Unsupported categories and the VLM's `other_text` observations are reported as missing-feature candidates, not silently absorbed into existing features.

## Offline validation

`tests/test_verify.py` covers geometry sign, border support, fragmented glyphs, the requested regression, local obstruction/blur, tiny/blank/transparent images, original-coordinate expansion, Unicode normalization and impossible marks, cache invalidation/deduplication, numbered batch correspondence, receipt model/flags, failed invocations, both call limits, missing-label calibration, source-separated confusion tables, and all four CLI paths (the online boundary is mocked). Real judge calls are confined to the explicitly enabled sample runner and the recorded initialization probes.
