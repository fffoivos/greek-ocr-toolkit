# Recogniser, synthetic data, warm-start and training

Documentation for `docs/A_ocr_development/RECOGNISER_AND_TRAINING.md`, inspected 19 October 2026 on `cleanup/20261019` at `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`. This describes toolkit APIs and the experiment lineage they support. No training, generation, inference, deployment or test suite ran for this documentation change.

Paths are repository-root paths. References to **greek-page-ocr** documents below use document names only: that repository owns E1–E4 drivers, run bindings, execution ledgers and results. A wrapper added later is not evidence the historical experiment imported that wrapper.

## Recogniser API

`greekocr/recogniser` is the phase-1 common API over frozen implementations. Its README directs new OCR tools to this API; pinned callers keep original imports until gate recertification. The package does not copy forward, preprocessing, decoding or alignment algorithms.

```python
from greekocr.recogniser import load, align, AlignmentCache, forbid_forward

recogniser = load(checkpoint, codec=codec, device='cpu', threads=4)
readings = recogniser.read(crops, profile='labelfix', bs=16)
alignment = align(readings[0])
slots = alignment.slots()
evidence = alignment.evidence(slots, image_width)
reader = recogniser.as_reader(profile='eval')
```

`load(checkpoint, codec=None, device='cpu', threads=None, strict=True)` loads local checkpoint metadata and validates codec version, exact codec SHA, class count and NFD head. An absent head keeps the legacy NFD default; missing codec SHA fails strict mode. `strict=False` records issues while preserving each delegated backend's own checks; it is not a promise an incompatible checkpoint can load. A supplied thread count must be positive. Backends initialize lazily per profile; there is no download or checkpoint conversion.

| Profile | Delegated implementation | Input/output and preserved distinction |
| --- | --- | --- |
| `labelfix` (default) | `greekocr.labelfix.ctc_align.Recognizer.align_batch` | Ordered path/PIL crops, batch size 16 by default; text, alignment, confidence/frame evidence, scale and strip width. Raw first-pass spans remain unrounded. |
| `eval` | `greekocr._vendor.bench.e2_reader_parity.E1Reader.read` | One path at a time; PIL inputs serialize to temporary PNGs. Literal atom strings preserved. The public method exposes no alignment/confidence, so those fields remain `None`. |
| `serve` | `greekocr.deploy.docling_plugin.recognizer.inference.Recognizer` | Prepared float32 strips pass unchanged, or path/PIL crops go through the serving `extract_strip`. Prepared arrays must be finite 2-D, height 48, width 64–2560, values 0–1. Text is NFC with serving confidence. |

`Reading` carries `text`, `profile`, provenance, optional alignment, confidence, frames, scale, strip width and IDs. IDs remain unavailable from old public methods. No extra forward fills missing evidence. `align(reading)` refuses profiles without alignment. Different background/halo and normalization rules remain separate; no profile is a universal replacement.

`recogniser.logits(images, dtype=np.float32)` delegates the evaluation backend's inherited E1 logits path; `dtype=np.float64` requests the older returned precision. The logits float halo differs from `E1Reader.read`. `as_reader(profile='eval')` supplies the existing reader protocol plus source binding.

Provenance separately hashes checkpoint, any explicit/sibling safetensors file, codec, API package Python sources and delegated implementation sources; it records device, float32 model dtype, Torch version and binding issues. These envelope fields are not added to the frozen alignment serialization/hash.

### Alignment, transfer and replay

`Alignment.slots()` groups frozen atom spans by text cluster and exports locator windows, not detected glyph boxes or physical ink ownership. `evidence()` delegates the existing score computation. `confidence_matches` checks finite [0,1] frame values and mean confidence with absolute tolerance `1e-6` and no relative tolerance.

`transfer(alignment_or_record, new_text)` uses the original nearest-neighbour span transfer, normalizes the new text to NFD, deep-copies, removes frame confidences/prediction-score binding and flags `transferred`, including identity transfers. It is deliberately different from the old identity no-op and the older record helper that retained frame scores.

`AlignmentCache(path, recogniser).get(crops, bs=16)` and `run_shard` use C1's strict canonical `crop_key`: paths must contain `docs/harvest/`. Loading refuses duplicate stored canonical keys. Missing crops run the labelfix profile and append records with provenance; **all** returned alignments, including first-run results, round-trip through record serialization. Old rows without provenance remain readable. The cache is single-writer; shards require distinct paths. Input failures report an index, not an invented empty success.

`forbid_forward()` patches the relevant old/new forward entry points for local replay and restores them on exit. It is process-local/nestable, not thread isolation. Stored alignment replay is separate from re-inference.

## Synthetic line generation and custody

**All synthetic training/evaluation data must originate from linefactory sources.** `greekocr/synth/__init__.py` exposes the captured factory and custody rules; it does not introduce a Python synthetic training-data generator. Synthetic glyph/page unit fixtures are controlled evaluation constructions, not production shard sources.

| API | Inputs and effects | Required output/binding |
| --- | --- | --- |
| `recipe_registry()` | Loads captured v5/v7/v8 recipe identities from `greekocr/_vendor/origins.json` | `Recipe(name, path, sha256, origin_commit)`; digest is captured source identity, not a mutable rehash. |
| `verify_recipe_sha` | Registered recipe/name or custom path with explicit expected digest | Refuses missing custom digest or byte mismatch. |
| `build_shards(recipe, binary, out, *, pool, workdir=None, timeout=3600)` | Invokes the supplied existing binary as `linefactory build --recipe ... --pool ... --out ...`; requires fresh/empty output | `build_info.json` with matching recipe SHA, `audit_ok=True`, and exact nonempty shard hash inventory. Does not build/download the binary. |
| `build_mix(..., repo, seed=0, codec_version='v1', role='train')` / `validate_mix` | Manifest-only mix custody through vendored `train.mix` | Validates committed recipe identity, role, receipt fields and exact shard membership; legacy unprovenanced evaluation is distinct from train/validation. |
| `assemble_mix(groups, fractions, seed, epoch=0, max_rows=None)` | Existing largest-remainder quotas and deterministic seed/epoch/component cycling | Selected rows plus group counts, without rewriting source shards. |

The Rust source is captured under `greekocr/_vendor/factory/src/`, including build/render/distortion, recipe, corpus, codec, shard, audit, measurement and real-import components. Recipe v5 is the training source in the cited E1–E4 lineage; v7/v8 are separately bound evaluation distributions described by greek-page-ocr's `data_contracts.md` and `E2_NOTES.md`. Version names alone do not establish an artifact's recipe/shard/codec custody.

`tests/test_custody.py` checks captured recipe identities, HEAD-blob rather than dirty-worktree custody, wrong hashes/roles/inventories, failed-build nonpublication, real-import receipts, quota/epoch sampling and the factory command/receipt boundary. Its mocked factory invocation is not evidence of a newly generated production shard set.

## Donor conversion and training implementation

`greekocr/warmstart/__init__.py` delegates to vendored E2 code:

- `map_donor_state(family, state)` and `map_paddle_state` perform exact state mapping. Unsupported keys/families fail rather than fuzzy matching.
- `convert_donor(family, checkpoint, config, out, revision, *, codec, seed=0)` retains donor backbone/neck, swaps the final CTC classifier for the codec's NFD classes, and binds source/config/codec/revision/license/seed and layer mapping.
- `verify_init` verifies the resulting initialization payload; `preprocess`, `compare_endpoints` and `qualify_parity` expose the independent native preprocessing/logit qualification boundary.

Families in `greekocr/_vendor/bench/e2_warmstart.py` are R01 (Greek PP-OCRv5 mobile recogniser), R02 (PP-OCRv6 small recogniser), and R03 (encoder/CTC-FRM path with auxiliary SMTR removed). **These are recogniser donors, not the small page detector used by R7/R8.** R01/R02 require official HF JSON configs; R03 also accepts its YAML architecture. The conversion records RGB kernels retained, grayscale replication in training, and R01/R02 trainer-only right-background extension to a multiple of four.

Outputs include `native_before_swap.pt`, `donor_provenance.json` and `donor_init.pt`; retained tensors are checked exactly. Conversion sets parity status to a separate node-only gate; key compatibility and successful head replacement do not prove native logits parity. `e2_parity.py` compares endpoint shape/finiteness, normalized max-absolute error ≤`1e-4`, and identical greedy output, with separately pinned native preprocessing. The initial module's description “exact donor conversion” must not be read as zero numerical tolerance across distinct frameworks.

Neural training machinery remains in `greekocr/_vendor/train/` (`train.py`, `model.py`, `data.py`, `mix.py`, checkpoint I/O and evaluators), with vendored E1/E2 bench/readout/model/parity components. Historical E1–E4 orchestration is owned by greek-page-ocr. This document does not prescribe a new run or infer a currently deployable best checkpoint from an old result table.

### The font-classifier command is different

`scripts/train_line_font.py --shards PATH --out MODEL.json [--styles styles.json] [--max-lines N]` calls `greekocr.annotate.font.train_font_classifier`. It streams **existing** synthetic rows with exact known factory font IDs, computes NumPy descriptors, and fits nearest-centroid/RMS-radius support entirely on CPU. Optional styles map font IDs to supported style classes. Empty/blank-only data, unknown synthetic fonts, nonpositive limits and an existing output path fail.

The JSON contains schema, model ID, descriptor size, families, styles, counts, centroids, radii, training source and algorithm. Its three-standard-deviation radii with a floor are support detection, not a calibrated posterior or real-scan validation. It neither trains the neural recogniser nor generates shards.

## Real experimental lines

`greekocr/real` exposes the older experiment-facing acquisition/import surface. `DocumentPartition` and `build_partition` require reviewed canonical work/exposure identity; unresolved exclusions fail. `extract_lines` delegates PDF/DjVu text-layer extraction with zero-based API page selection; missing layers remain flagged. `native_rows`/`import_dataset` preserve native dataset formats/labels and reviewed partitions.

`adjudicate_lines`/`adjudicate_file` use independent crop readers and optional teacher binding, preserve rejected rows, and record failures/disagreement. Agreement is a recorded admission method, not independent print truth. `import_real_shards` is the real training-shard writer boundary: it invokes `linefactory import-real`, verifies `kind='real'`, partition ID, exact nonempty shard inventory and `word_tags.jsonl` hash.

`real/geometry.py`, `geometry_measure.py` and `geometry_evaluate.py` expose crop refinement, geometry diagnostics/admission and old/new measurements/review artifacts. This historical text-layer/crop work is not the current B Google page-read pipeline. Current source collection, corrected labels, crop filtering and revision belong to `greekocr/harvest`, `readers/services`, `labelfix`, `numerics` and B documentation.

## Scoring contracts

| API in `greekocr/score/__init__.py` | Meaning |
| --- | --- |
| `edit_distance`, `strict_cer` | Levenshtein/codepoints exactly as supplied. No automatic prediction normalization. |
| `score_readings` | E2 bake-off canonical NFD decomposition of **both** inputs, with mark/homoglyph diagnostics. This is a distinct scoring boundary. |
| `summarize_predictions` | Strict E1 clean-row/readout summary; category strata overlap and must not be summed as disjoint populations. |
| `write_readout` | Prediction-file readout with `require_complete`, optional `transfer_enabled`, and title; delegates the existing E1 readout. |

Declare literal text policy, reference population, denominator, codec exclusions, failed-read handling and instrument identity when reporting a score. A service/reader agreement score, geometry-clean subset, silver test labels and human transcriptions answer different questions. `docs/records/glyphs/GLYPHS_CALIBRATION.md` itself distinguishes NFC/NFD crop results and retracts old E1 limit claims; it is not a universal scorer or current filter release.

## Docling deployment surface

`pyproject.toml` registers the `docling` entry point `glossapi = greekocr.deploy.docling_plugin.docling_plugin`. `ocr_engines()` exposes `GlossapiOcrModel`. Optional `docling` dependencies require local Torch/safetensors/OpenCV and Docling; no install/deploy occurred here.

`GlossapiOcrOptions` requires checkpoint/codec, defaults to CPU, `recognition_mode='textlayer'`, `crop_scale=3.0`, `replace_policy='routed_pages'` (requires a sidecar), tables enabled, joining/statistics disabled. Optional checkpoint SHA pin rejects a mismatch; a pinned `.pt` with a safetensors sibling is refused to prevent resolving different weights.

Detector mode calls the **slow** `greekocr.pages.process_page`, supplies Docling's pre-OCR layout regions and actual image/page dimension ratios, and maps page options with `strict_geometry=True`. It unrolls/prepares each recognition piece separately, pads valid narrow table cells to the serving tensor contract, calls the existing local recognizer and installs `TextCell`s. It does not proportionally divide an already recognized string. Invalid active geometry preserves native cells. Installation clears stale native/prior-OCR words/characters and the backend's cached segmented page so they cannot override the replacement cells. Later Docling stages own semantic table grids/document assembly.

`recognition_mode='oriented'` enables the optional local orientation page path; text-layer mode remains separate compatibility behaviour. The plugin's `_get_recognizer` still directly constructs `deploy/docling_plugin/recognizer/inference.py:Recognizer`. The common API's `serve` profile delegates to the same implementation; this is not proof that every pinned consumer has migrated to `greekocr.recogniser`.

Serving uses greedy CTC, 48-row strips, own-background right halo and width-aware batches; confidence is an uncalibrated frame-max-softmax mean. No output confidence is asserted to be a probability of transcription correctness. The Docling plugin does not select the R8 prototype or implicitly schedule other Docling stages.

## E1–E4: which mechanisms were used

These are attributed experiment records/designs, not live job status or new reproduction. Documents are in **greek-page-ocr**, referenced by name only. The toolkit wrappers identify corresponding implementations; historical drivers may import their original paths.

| Experiment / wave | Synthetic, model and training surface | Real-data/scoring boundary and record |
| --- | --- | --- |
| **E1 run4** | Compact NFD CTC model, v5 linefactory training, real-fraction f0/.25/.5/.75/1 sweep, three seeds; existing E1 trainer/evaluator/readout lineage | Reviewed real imports and strict readout; v7 synthetic held-out separate from legacy transfer's unprovenanced eval-only recipe. `E1_REPORT_run4.md`, `E1_NOTES.md`, `data_contracts.md`. No donor conversion claim for the scratch mixture arms. |
| **E2** | Re-executed E1 teachers; R01/R02/R03 donor/model/conversion/parity tooling and native readers; bound E1 v5 retained, v8 evaluation distinct | Teacher bake-off uses canonical NFD on both sides; E1 reader parity is a separate gate. `E2_NOTES.md` records teacher revisions and native-preprocess/endpoint restrictions; `R01_native_preprocess_review.md` is a captured donor-preprocessing record. Not every implemented donor equals a qualified production arm. |
| **E3** | Ten arms: compact scratch sizes 25k/50k/100k/full × two seeds, and full R01 warm-start × two seeds; eight epochs, 428,872 draws, 50% v5 synthetic/50% collection-v2 real, NFD codec v1 | `E3_RESULTS.md` records collection-v2 Google silver training, capped parliament share and four instruments (v2_test, human Wikisource, E1 real, synthetic held-out). Scratch beats the R01 package on primary scanned/real instruments; architecture/microbatch/time-axis differences prevent an initialization-only conclusion. `E3_NOTES.md` preparation sections retain earlier gates; later results supersede their pre-run status. |
| **E4 wave 1a** | Fresh compact controls; synthetic fractions 40/60%, width multipliers 1.5/2, born-digital replay m1; retained factory-v5 lineage | `E4_WAVE1A_RESULTS.md`: 18 completed base runs (six configs × three seeds), grave deferred; aggregate remained PARTIAL and readback had four failed checks despite zero copied SHA mismatches. Training completion and readback completeness are separate. |
| **E4 wave 1b** | v_a codec-v1 control, v_b/v_c codec-v2 models, recovered rows in v_c; width w30 separate; three seeds, eight epochs | `E4_WAVE1B_RESULTS.md`: 12/12 runs and aggregate DONE, readback PASS (193/0). v2-codec and v2-asis releases/control contrasts remain separate. Common-intersection and full-coverage instruments must not be compared as one population; geometry-clean secondary column was skipped. |
| **E4 wave 1c (documented design)** | Reuses wave-1b v_c recipe: codec v2/recovered rows, width ×2, 50% synthetic v5, eight epochs; changes real labels by row-ID overlays | `E4_wave1c_brief.md`: registered correction versions and separate changed-label test slices. A prep brief is not proof of completed runs; no wave-1c result is certified here. |
| **E4 wave 1d (documented design)** | Same v_c recipe/synthetic half; unmasked control versus masked same rows, then masked plus admitted W1 rows | `E4_wave1d_brief.md`: crop substitution by original/masked SHA, guarded originals/parliament retained, masking-status strata. B's crop preparation is an experimental input, not a replacement for factory synthetic provenance. No completed result is inferred from this brief. |
| **E4 wave 1e revision 2 (documented design)** | Synthetic half and total draws fixed; control/uniform u2/targeted ut weak-category real-data shares | `E4_wave1e2_brief.md` replaces the uniform u4 arm with targeted shares. This source is a design revision, not readback evidence. |
| **E4 wave 2 / post-cleanup programme** | v_c-derived control, more unique admitted real rows at fixed compute, optional registered corrections, 50% factory synthetic retained | `E4_wave2_scale_brief.md` defines ctrl/add/add_corr and binding requirements. `POST_CLEANUP_PROGRAMME_20261019.md` places frozen filtering/corrections, benchmark certification and recipe retest before scaling. These are plans, not launches/results established by this document. |

The later E3 record corrects Open Archives metadata without changing images/labels/IDs/splits; do not reuse early historical-period interpretations. E4's codec-v2 releases and external experiment recipes are not implied by the toolkit wrapper's default codec-v1 argument or registry containing v5/v7/v8. Inspect the actual experiment binding rather than silently adding a new toolkit version.

## Tests and evidence scope

Documented commands only, in an already configured environment:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/recogniser
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_custody.py tests/test_warmstart_readers.py tests/test_real_annotate_score.py tests/test_real_geometry.py tests/test_geometry_measure.py tests/test_geometry_evaluate.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_docling_contract.py tests/test_docling_tables.py tests/test_docling_orientation.py tests/test_ops_deploy_sources.py
```

`tests/recogniser/test_api.py` and frozen L1F fixtures cover common-API/replay contracts. The golden-cache test defaults to sibling `greek-ocr-toolkit-spellcheck/.cache/labelfix`, overridable by `CU3_CACHE_ROOT`, and **asserts** that `align_s0.jsonl` exists; a missing required cache fails rather than silently skipping. Additional locked caches are included when available. `tests/recogniser/parity.py` is an explicit 200-crop forward experiment, never ordinary pytest collection, and requires separate forward authorization. `tests/test_warmstart_readers.py` checks exact mapping/refusal and parity interfaces; controlled/fixture-model conversion does not certify a released native checkpoint. CPU/mock tests and old source-bound receipts are not current experiment results.

The package `0.1.0` version, recogniser phase-1 status, factory recipe versions, donor R01–R03 names, experiment E1–E4 waves and B manifest tool versions are different namespaces. The B authoritative manifest's current segmentation `0.13` (label `0.9-s5`) / gate `0.3` overrides stale crop-filter prose; it does not certify new training.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`, `docs/cleanup_20261019/PLAN.md`, `docs/harvest/line_pipeline/tool_versions.json`, `pyproject.toml`, `README.md`.
- `greekocr/recogniser/README.md`, `greekocr/recogniser/{__init__,api,alignment,cache,guard}.py`.
- `greekocr/{synth,warmstart,score}/__init__.py`; `greekocr/_vendor/bench/e2_warmstart.py`, endpoint/preprocessing portions of `greekocr/_vendor/bench/e2_parity.py`; vendored source-file inventory.
- `greekocr/real/{__init__,extract,importers,partition,adjudicate}.py`; API declarations in `greekocr/real/{geometry,geometry_measure,geometry_evaluate}.py`.
- `scripts/train_line_font.py`, `greekocr/annotate/font.py`.
- `greekocr/deploy/docling_plugin/{docling_plugin,options,model}.py`, loading/batching portions of `greekocr/deploy/docling_plugin/recognizer/inference.py`; `docs/A_ocr_development/reference/PAGES_GUIDE.md`, `docs/A_ocr_development/reference/PAGES_PIPELINE.md`, `docs/records/glyphs/GLYPHS_CALIBRATION.md`.
- `tests/test_custody.py`, portions of `tests/test_warmstart_readers.py`, `tests/test_real_annotate_score.py` and `tests/recogniser/test_api.py`; test-file inventory under `tests/recogniser` and related package tests.
- Captured greek-page-ocr documents: `E2_NOTES.md`, `data_contracts.md`, `R01_native_preprocess_review.md` (matching excerpts under this repository's origins tree).
- Greek-page-ocr documents, read for experiment context by name: `E1_REPORT_run4.md`, `E3_NOTES.md`, `E3_RESULTS.md`, `E4_WAVE1A_RESULTS.md`, `E4_WAVE1B_RESULTS.md`, `E4_wave1c_brief.md`, `E4_wave1d_brief.md`, `E4_wave1e2_brief.md`, `E4_wave2_scale_brief.md`, `POST_CLEANUP_PROGRAMME_20261019.md` (relevant opening/design/result sections).
