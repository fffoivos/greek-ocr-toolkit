# T6a2: native foreign-ink masking — completed negative safety qualification

**Inference-applicable: yes. Own-ink safety gate: FAIL. Nothing admitted or enabled by default.** The overall CER non-worsening gate passes.

The fixed existing ownership rule removes substantial readable neighbour fragments on 56/57 overrun cards (98.25%), but erases 387/510,558 cached own pixels on crop-ok-y cards (0.0758%). Native inspection confirms real target damage, including a gamma descender, an E serif and an f serif. Strong foreign-pixel removal is not zero own-ink loss or complete background cleanup.

T6a at `6ed722f8` remains its recorded negative, unshipped result. Its code, parameters and evidence are unchanged. This work starts at brief HEAD `9ac8b3572ec2ed0c6cbafcb4f0b1eb6da5041453` on `sol/recut-v1`. Network OFF. F2 only; W1 and admission state were not accessed or changed.

## Step 0: identical inference application

The current page detector is `greekocr/pages/lines.py:segment_page`, used by `pages.api.process_page`. The actual deployment crop consumer is `greekocr/deploy/docling_plugin/model.py:GlossapiOcrModel._detect`, in its for-piece loop immediately before `extract_line_image(image, piece.line)`. `tables.line_piece` supplies the unchanged original native rectangle. The older `glyphs.lines_api.separate_lines` straightens crop-local fits; `glyphs.page_lines.page_lines` requires supplied boxes and is not the present deployment crop consumer.

The opt-in call at that boundary is `mask_detected_line(mask_page, piece.line, runtime_neighbours, piece.box)`, where `mask_page=prepare_mask_page(image)` and `runtime_neighbours` is the non-discounted subset of `analysis.segmentation.lines`. The result is pasted into a private native-page copy before the unchanged extraction call. Centre=(baseline+meanline)/2; the runtime's detected guides supply every own and neighbouring curve. No Google geometry or cached component truth is required. Training proposals use exactly the same function and detector neighbour set inside the saved original training rectangle. Deployment defaults are unchanged; the exact insertion recipe is in [REUSE.md](REUSE.md).

The gate was written and tested before the public library was added. Four fresh F2 runtime pages were used, one per source. Exact equivalent-input masks matched **187/187 training rectangles and 187/187 detector rectangles**. The later public-function check also matches all filled raster bytes and records, and executes the unchanged `extract_line_image` after each insertion: **187/187 actual extraction results identical**. [Initial gate](step0/agreement.json), [public-function identity](step0/public_function_identity.json).

| Source | F2 target lines matched | Runtime / Google complete masks equal | Ink-pixel agreement | Masked-set IoU |
|---|---:|---:|---:|---:|
| gazette_modern | 46/46 | 43/46 | 99.8865% | 98.2917% |
| lekythos_poly1900 | 99/99 | 88/99 | 99.9046% | 99.0792% |
| kosmopolis_poly1900 | 17/17 | 17/17 | 100.0000% | 100.0000% |
| ia_greek_latin | 25/25 | 17/25 | 99.9654% | 98.3841% |

Aggregate runtime-vs-Google comparison: 165/187 exact complete masks, 99.9428% agreement on 1,128,287 ink pixels (645 disagreements), masked-set IoU 102,825/103,470 = 99.3766%. Google-box-derived curves use the existing `fit_box(..., splits=False)` and are a diagnostic comparison only. They are not training-mask inputs. Equivalent-input equality is distinct from detector/Google agreement and from physical glyph ownership.

Existing `pages`/`glyphs` runtime files match `046bd52`; additions are the pre-existing T6a `vertical_recut.py` and this opt-in `foreign_ink.py`. Neither is enabled in deployment. Fresh full-precision runtime curve observations for all 87 F2 pages are bound to source rasters and code in [runtime_manifest.json](runtime_manifest.json). The fixed training-target binding and its driver hashes are frozen in [binding_freeze.json](binding_freeze.json). Eleven unmatched target rectangles remain literal originals (10 Lekythos, 1 IA); no curve or row is invented.

## Reused ownership and local fill

[foreign_ink.py](../../../../../greekocr/glyphs/foreign_ink.py) is opt-in. It directly calls unchanged `recut._voronoi_keep`, reuses `_neighbour` and `LineFit.base_at`, and adapts the existing straightened working grid by reversible integer column translations. Output pixels are never resampled: only the foreign foreground mask inside the original rectangle is filled. No output box expands, shifts or changes dimensions; no line is split, joined or added. The same page observation preparation is used by raw-page and prepared-page calls.

For each selected native component, fill is the per-channel median of its native-page Chebyshev ring between one and three pixels from the component, excluding all binarised foreground. Ring spread is p90 minus p10. Empty rings abstain; there is no constant-white fallback. A measured median of 255 on saturated Gazette paper is a local statistic, not a hard-coded fill. Crop-level median/spread are unweighted medians across component statistics; every per-component ring size, median, spread and fill is retained in the row record.

`_voronoi_keep` exposes **no ownership tolerance parameters**. No tuning grid, new semantic attachment rule or label-derived protection guard was introduced. Its unchanged nearest-centroid rule has a high detached-mark counterexample; its body-band touching test can also cut an own descender or serif. The wrapper is not claimed to cure those limitations.

## F2 development: all 160 pinned v2 cards

The same v2 keys, cards, verdict bytes and features were reverified against the existing T6a binding and pinned revision `2f34ed52`. There are 58 crop-ok-n and 102 crop-ok-y cards; 57 n cards have `crop_overrun`, while Lekythos c037 is a horizontal clip. The visual metric below means **at least one previously readable neighbour fragment substantially removed**, including partial improvements. It does **not** mean all neighbouring ink is gone.

| Source | n / y | Changed y inspected | Visual fragment removal / overruns | Cached foreign pixels, n before → after | Cached own pixels lost / total, y | Own component appearances touched |
|---|---:|---:|---:|---:|---:|---:|
| gazette_modern | 18 / 22 | 19 | 17/18 | 12,571 → 0 | 0/64,198 | 0/1022 |
| lekythos_poly1900 | 11 / 29 | 29 | 10/10 | 7,982 → 60 | 20/58,067 | 4/1271 |
| kosmopolis_poly1900 | 26 / 14 | 13 | 26/26 | 28,988 → 144 | 11/35,829 | 1/714 |
| ia_greek_latin | 3 / 37 | 33 | 3/3 | 2,974 → 59 | 356/352,464 | 9/1261 |
| overall | 58 / 102 | 94 | 56/57 | 52,515 → 263 | 387/510,558 | 14/4268 |

All 160 paired cards and **every one of the 94 changed y cards** were inspected in 32 contact sheets. All 14 cached own-component loss witnesses and five larger native contexts were also inspected. This is an unblinded agent inspection, not a new owner blind verdict. [Visual observations](dev/visual_review.jsonl), [summary](dev/visual_summary.json), [hashed review artifacts](dev/review_artifacts.json).

Decisive native y witnesses: IA c023 cuts the initial gamma's lower descender (94 cached pixels in that component); IA c040 removes the capital E's upper-left serif (91); IA c019 shortens the target Latin f's upper serif (12). Other small removed dots or boundary fragments have unresolved semantic attachment. IA c001's larger context confirms its own iota subscript remains. Therefore 387 is the independent **cached ownership pixel** loss, not a claim that every removed dot is semantically own text. The confirmed target damage alone falsifies zero loss. Capturing the original _voronoi_keep arguments for the three confirmed failures shows each component nearer its own centre but also touching a neighbour body band: its unchanged midline-cut branch removes the target extremity. The frozen masks reproduce exactly in this trace ([mechanisms](dev/confirmed_loss_mechanisms.json)). [Component audit](dev/component_audit.jsonl), [native loss list](dev/loss_witnesses.jsonl).

Visual counterexamples to the foreign-pixel metric: Gazette c015 still contains the readable E.S.Y.E. neighbour while its cached foreign count was zero before masking. Gazette c005 loses upper neighbour fragments but retains a readable lower fragment. Lekythos and Kosmopolis cards can retain faint outlines/antialias halos around removed foreground. Lekythos c024 also cuts its own drop-cap H, which the cached own-pixel metric does not cover. No complete cleanup or universally correct ownership is claimed.

Across all 58 n cards, cached foreign pixels fall 52,515 → 263 (99.4992% removed); cached neighbouring body pixels fall 36,080 → 9. Of 2,460 cached foreign component appearances in n crops, 2,435 are fully removed from the crop and 2,443 are touched. These are detector-label measurements, not independent text truth. On y cards, 14/4,268 own component appearances lose pixels across 11/102 cards; all y cards have a measurable cached owner. [Development metrics](dev/summary.json), [component metrics](dev/component_summary.json).

## Fill statistics and frozen identity

| Source | Dev masked pixels / component applications | Dev median ring value / spread | F2 masked pixels / component applications | F2 median ring value / spread |
|---|---:|---:|---:|---:|
| gazette_modern | 18,573 / 700 | 255.00 / 4.00 | 318,632 / 9,962 | 255.00 / 4.00 |
| lekythos_poly1900 | 12,301 / 725 | 213.00 / 16.70 | 996,032 / 71,162 | 214.50 / 15.60 |
| kosmopolis_poly1900 | 42,424 / 1,531 | 243.00 / 13.00 | 551,275 / 18,766 | 243.00 / 13.00 |
| ia_greek_latin | 14,206 / 419 | 252.00 / 9.00 | 307,686 / 6,628 | 252.00 / 9.00 |
| overall | 87,504 / 3,375 | 248.00 / 11.85 | 2,173,625 / 106,518 | 219.00 / 14.80 |

Counts sum component applications per crop, rather than claiming distinct physical components across the page population. There are zero empty-ring abstentions. Full-corpus selected fill pixels total 2,173,625; 2,173,617 native pixels actually change. Eight selected pixels in two non-dev crops already equal their component ring median. Those two masks were reexecuted and hash-verified; the other masks were reconstructed from native differences. No crops or settings were changed in response to this verification distinction.

Parameters were frozen at `2026-10-16T23:09:34.795863+00:00`, before harm inference at `2026-10-16T23:15:34.847076+00:00`. Canonical parameter SHA256: `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. Library SHA256: `f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5`. The freeze already records the failed empirical own-ink safety gate. Neither settings nor crops were revised after seeing predictions. [params.json](params.json), [validation](validation.json).

## Paired E4 ctrl_s0 harm test

Same 5,770 F2 lines; 11,540 paired arm observations; Mac CPU, four threads, batch 16, seed 20261017. Checkpoint SHA256 `e20cd6cdfc908339b3c7c8f83e88888120240aabc01370a86b7b48606fa81c30`; local safetensors were verified tensor-for-tensor against the SHA-verified best.pt. The unchanged `train/eval_cer.py:evaluate`, `bench/o4b_models.py:strip` and `data.collate_strips` implement strict NFD codepoint corpus CER against the same fixed Google labels in both arms. The CUDA-runtime custody wrapper `evaluate_run` is not used; this is its unchanged evaluator core with the documented CPU adapter. [Binding](harm/binding.json), [original receipt](harm/original.receipt.json), [masked receipt](harm/masked.receipt.json).

CER values below are fractions. Difference is masked minus original; a negative value favours masking. CIs use 5,000 seeded paired bootstrap replicates, with both line resampling and page-cluster resampling. The original and masked corpus numerator/denominator are retained in the JSON. These CIs describe this F2 population, not W1 or production qualification.

### Overall and per source

The fresh original readout exactly reproduces all 5,770 recorded T6a original predictions, references, edit counts and source assignments; the entire prediction-file SHA256 is identical. [Reproduction receipt](harm/original_reproduction.json).

| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |
|---|---:|---:|---:|---:|---|---|
| gazette_modern | 525 | 0.039642 | 0.016116 | -0.023526 | [-0.031362, -0.016592] | [-0.053922, -0.003112] |
| lekythos_poly1900 | 4023 | 0.011629 | 0.008061 | -0.003569 | [-0.004444, -0.002779] | [-0.005849, -0.001738] |
| kosmopolis_poly1900 | 562 | 0.058271 | 0.015719 | -0.042552 | [-0.052060, -0.034028] | [-0.069627, -0.018490] |
| ia_greek_latin | 660 | 0.038777 | 0.034292 | -0.004485 | [-0.006363, -0.002769] | [-0.007918, -0.001219] |
| overall | 5770 | 0.023249 | 0.012656 | -0.010592 | [-0.012236, -0.009092] | [-0.016978, -0.005965] |

### Changed crops

| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |
|---|---:|---:|---:|---:|---|---|
| gazette_modern | 447 | 0.039371 | 0.013756 | -0.025615 | [-0.034363, -0.017896] | [-0.058602, -0.003537] |
| lekythos_poly1900 | 3818 | 0.011731 | 0.008009 | -0.003722 | [-0.004622, -0.002893] | [-0.005980, -0.001806] |
| kosmopolis_poly1900 | 533 | 0.060322 | 0.016224 | -0.044098 | [-0.053596, -0.035340] | [-0.072787, -0.019077] |
| ia_greek_latin | 601 | 0.043420 | 0.038268 | -0.005152 | [-0.007274, -0.003150] | [-0.008881, -0.001395] |
| overall | 5399 | 0.023787 | 0.012586 | -0.011200 | [-0.012869, -0.009647] | [-0.018045, -0.006307] |

### Unchanged crops

| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |
|---|---:|---:|---:|---:|---|---|
| gazette_modern | 78 | 0.042696 | 0.042696 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| lekythos_poly1900 | 205 | 0.009263 | 0.009263 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| kosmopolis_poly1900 | 29 | 0.001812 | 0.001812 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| ia_greek_latin | 59 | 0.007546 | 0.007546 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| overall | 371 | 0.013877 | 0.013877 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |

All **371 unchanged crops have exactly identical prediction strings and edit counts** in both arms, checked by ID. Crop dimensions keep both arms in the same width ordering. The remaining 5,399 crops changed. [Paired rows](harm/paired.jsonl).

### Crop-ok-n development subset

| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |
|---|---:|---:|---:|---:|---|---|
| gazette_modern | 18 | 0.025328 | 0.006987 | -0.018341 | [-0.032803, -0.006244] | [-0.032121, -0.002055] |
| lekythos_poly1900 | 11 | 0.059448 | 0.012739 | -0.046709 | [-0.132159, 0.000000] | [-0.140363, 0.000000] |
| kosmopolis_poly1900 | 26 | 0.084701 | 0.017072 | -0.067630 | [-0.122682, -0.025542] | [-0.136319, -0.012694] |
| ia_greek_latin | 3 | 0.046296 | 0.018519 | -0.027778 | [-0.115385, 0.000000] | [-0.115385, 0.000000] |
| overall | 58 | 0.058824 | 0.012935 | -0.045889 | [-0.075356, -0.022899] | [-0.083429, -0.016075] |

### Crop-ok-y development subset

| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |
|---|---:|---:|---:|---:|---|---|
| gazette_modern | 22 | 0.021845 | 0.020227 | -0.001618 | [-0.004042, 0.000000] | [-0.003704, 0.000000] |
| lekythos_poly1900 | 29 | 0.007109 | 0.006319 | -0.000790 | [-0.002421, 0.000000] | [-0.002208, 0.000000] |
| kosmopolis_poly1900 | 14 | 0.009736 | 0.009736 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| ia_greek_latin | 37 | 0.034914 | 0.030962 | -0.003953 | [-0.010835, 0.002094] | [-0.007846, 0.000000] |
| overall | 102 | 0.020257 | 0.018358 | -0.001899 | [-0.004223, 0.000000] | [-0.003487, -0.000590] |

### Geometry-clean subset

| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |
|---|---:|---:|---:|---:|---|---|
| gazette_modern | 470 | 0.023113 | 0.014978 | -0.008135 | [-0.013654, -0.003913] | [-0.021126, -0.001909] |
| lekythos_poly1900 | 3762 | 0.009488 | 0.007454 | -0.002035 | [-0.002807, -0.001367] | [-0.003260, -0.001012] |
| kosmopolis_poly1900 | 396 | 0.014411 | 0.010459 | -0.003951 | [-0.005869, -0.002399] | [-0.007625, -0.001562] |
| ia_greek_latin | 660 | 0.038777 | 0.034292 | -0.004485 | [-0.006408, -0.002787] | [-0.007866, -0.001000] |
| overall | 5288 | 0.014856 | 0.011697 | -0.003160 | [-0.003973, -0.002421] | [-0.004846, -0.001896] |

The geometry-clean subset is exactly the T6a detector-defined filter: `geometry_positive is False` and no screen rejection, within the fixed usable/text-exclusion-free F2 pool. It is not an independently certified zero-geometry-error population.

## Contracts, outputs and disposition

The 21 contract/characterization tests pass (11 new cases, including parameterized rectangle checks, plus 10 unchanged T6a tests). They cover ordinary own accents/breathings, connected descenders, apostrophe/coronis, iota subscripts, end punctuation, two-body touching, colour/ring statistics, native pixel preservation, exact adapters, invalid boxes, and an explicit detached-own-mark safety counterexample. A passing characterization test demonstrates that counterexample; it is not a passing universal safety property. [Tests](tests/test_foreign_ink.py), [test log](tests.log).

Native output/hash/label/rectangle verification covers all 5,770 pairs. Original crops are under `f2/<source>/original/`; masked proposals are beside them under `f2/<source>/masked/`. Original source pages and the F2 input trees are unchanged. Raster witnesses and full-precision runtime curve payloads are local ignored artifacts, bound by the tracked receipts. Per-source receipts are [Gazette](gazette_modern/receipt.json), [Lekythos](lekythos_poly1900/receipt.json), [Kosmopolis](kosmopolis_poly1900/receipt.json), [IA](ia_greek_latin/receipt.json).

**Disposition: reject as a safety-qualified crop replacement.** Inference applicability passes; empirical own-ink zero-loss fails, independently confirmed by native target glyph damage. Overall CER non-worsening passes, which does not overrule the own-ink gate. No defaults changed, no rows admitted, and no production path enabled.

The guarded commit attempt was blocked: Git could not create the managed worktree index.lock (Operation not permitted). **No worker commit was created.** No retry or alternate index was used. The exact source-bound manifest and validated local handoff.patch.gz are the coordinator fallback; HANDOFF.json records applying it in a fresh temporary directory and verifying every file hash. See COMMIT_STATUS.json for the actual failure.

T6a2: done | inference-applicable: yes | dev neighbour-ink removed: 98.25% own-ink loss: 0.0758% | harm CER orig/masked overall: 0.023249/0.012656 changed: 0.023787/0.012586 | params: 801d517e2ac5
