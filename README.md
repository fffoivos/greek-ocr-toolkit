# Greek OCR toolkit

## 1. Greek OCR: data, tools and models

**Greek OCR reads Greek (modern/monotonic and polytonic), Latin, Cyrillic, mixed Greek–Latin text, numbers and page furniture.** This repository contains the code and evidence for building its line datasets, reviewing corrections, training recognizers and using them through Docling. Results and limits are tied to their recorded populations; a supported script is not a claim of equal accuracy on every book.

These are the release targets in pipeline order. **Publication is in preparation:** HF paths below describe the planned public layout; final file/commit pins, model scores and the collection URL are pending. The [version register](VERSIONS.md) records counted rounds, aliases and unresolved historical counts. `v0.n (n unresolved)` is an explicit provenance gap, not a published tag.

1. These are the source pages and line boxes: [Greek OCR Lines — pages and geometry](https://huggingface.co/datasets/fffoivos/greek-ocr-lines/tree/main/tables), part of the line dataset (legacy **v0.4 / v4**, combined release version pending). Source metadata should identify the exact book, edition, volume and page; raw Google responses are excluded from the public snapshot.
2. This is our segmenter (**v0.3**, three A-lineage generations): [pixel-first implementation](greekocr/pages/), [R7/R8 lineage and evidence](docs/A_ocr_development/MODEL_GENERATIONS.md). The B crop policy is separately **v0.13 / 0.9-s5**, with [its tool binding](docs/harvest/line_pipeline/tool_versions.json).
3. This is how we filter and compose the lines: [content gate **v0.3**, repair **v0.2**, composer **v0.3**, final eligibility **v0.3**](greekocr/harvest/line_pipeline.py), [census **v0.7** and inventory **v0.1**](greekocr/harvest/line_pipeline_census.py). [The pipeline graph](docs/B_training_data/c_pipeline/pipeline.mmd) shows the order and retained HOLD/DROP evidence.
4. These are the corrected Google lines: [Greek OCR Lines — real lines](https://huggingface.co/datasets/fffoivos/greek-ocr-lines/tree/main/data/real), the same dataset release (legacy **v0.4**, new combined version pending). Raw and corrected label variants remain distinct. These are machine-produced/corrected labels with recorded review, rather than a claim that every row is human transcription.
5. These are the correction tools: [SF7 **v0.7**, RU1 **v0.3**, N1 **v0.3**, dashes **v0.1**](docs/B_training_data/b_tools/README.md). SF7's recorded candidate status, N1's assisted scope and dash tags' lack of a general repair release remain explicit in the register.
6. This is how we reviewed: [review code](greekocr/adjudicate/), [line-by-line review contract](docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md) and [recorded revision method](docs/B_training_data/d_review/README.md). Review is a method spanning the component versions above; it is not assigned an invented independent generation.
7. This is the latest dataset of synthetic lines we have produced: [Greek OCR Lines — synthetic lines](https://huggingface.co/datasets/fffoivos/greek-ocr-lines/tree/main/data/synthetic), **v0.n (n unresolved)**, current codec-v2.1 clone with **190,486 train rows** consumed by Stage C. Synthetic lines have their own files/configuration, separate from real lines. [The generator and recipe interface](greekocr/synth/) and [Rust linefactory](greekocr/_vendor/factory/) are **v0.n (generator count unresolved)**. The release retains configured distributions, applied operation names/order and available origin fields; missing per-operation parameters/seeds remain documented gaps.
8. This is how we trained: [the maintained trainer](greekocr/train/), [the sealed producing implementation](docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/), [consolidation mapping](greekocr/train/CONSOLIDATION.md) and [export/parity commands](scripts/release_v0_export/COMMANDS.md). The release builder is **v0.n (n unresolved)**; its [public-file inventory tools](scripts/release_v0_publish/) prepare the reviewable snapshot. A future release commit contains the producing source; it did not retroactively train these models.
9. This is the model we have trained: [Greek OCR](https://huggingface.co/fffoivos/greek-ocr), working **v0.10** (historical uncertainties in the register), compact widths **×1 / ×1.5 / ×2**, codec v2.1 / 266 classes / NFD head. [MODELS.json](MODELS.json) binds attempts **014 h14 / 013 / 013**, original packages/configs and pending final weights/scores. The retired ×1 h13 lane is excluded. Three-model completion and real-weight export parity remain pending.
10. This is how to use the models with Docling: [the plugin](greekocr/deploy/docling_plugin/) loads the SHA-bound release directory through `greekocr.train`, uses strict state loading and returns NFC text. [Release format and commands](scripts/release_v0_export/COMMANDS.md) describe model **v0.10**; plugin integration is not a separately counted training generation.
11. These are the [known gaps](docs/programme_20261028/RELEASE_v0/GAPS.md), gathered for checkpoint triage into [GitHub issues labelled `gap`](https://github.com/fffoivos/greek-ocr-toolkit/issues?q=is%3Aissue+label%3Agap). The HF collection is **Greek OCR — URL pending**; it will connect the pinned dataset and model commits.

The repository has two aspects: **A — OCR and segmenter development**, and **B — training-data creation**. B consumes frozen A tools. Python package and CLI: `greekocr`. Source identities, inputs and outputs are bound by hashes and receipts.

## 2. Map by the owner's taxonomy

All paths below are relative to the repository root. Code keeps its existing import paths.

| Part | What it contains and where the code lives | Documentation |
|---|---|---|
| A | OCR model and segmenter development; the three segmenters and recognition surfaces below. | [A overview](docs/A_ocr_development/README.md) |
| A.i | Slow pixel-first page segmenter: `greekocr/pages/`; crop primitives in `greekocr/glyphs/`. | [Slow pixel segmenter](docs/A_ocr_development/segmenters/SLOW_PIXEL.md) |
| A.ii | Current next-generation prototype, R8: `prototypes/fast_lines/stack/`; physical completion and speed qualification remain partial. | [Next-generation R8](docs/A_ocr_development/segmenters/NEXT_GEN_R8.md) |
| A.iii | Small Paddle detector plus heuristics, R7: the historical predecessor of the same `prototypes/fast_lines/stack/`, rather than a separate current copy. | [Small-detector R7](docs/A_ocr_development/segmenters/SMALL_DETECTOR_R7.md), [generations](docs/A_ocr_development/MODEL_GENERATIONS.md) |
| A — recognition, synthetic data and scoring | `greekocr/recogniser/`, `greekocr/warmstart/`, `greekocr/synth/`, `greekocr/real/`, `greekocr/score/`; synthetic shards come from the separate Rust line factory. | [Recogniser and training](docs/A_ocr_development/RECOGNISER_AND_TRAINING.md) |
| B | Creation of OCR training data: page reads, tools, the organising pipeline and human revision. | [B overview](docs/B_training_data/README.md) |
| B.a | Google OCR on pages: `greekocr/readers/`, `greekocr/harvest/`, `scripts/harvest/`, and source collectors in `collect_v3/`. | [Google page reads](docs/B_training_data/a_google_ocr/README.md) |
| B.b | SF7 polytonic, RU1 Cyrillic, N1 numerics, dash tags, segmentation filter and content gate: `greekocr/labelfix/`, `greekocr/numerics/`, `greekocr/harvest/`, `scripts/labelfix/`, `scripts/secondary/`, `scripts/numerics/`, `scripts/harvest/filter_runtime/`. | [Correction and filtering tools](docs/B_training_data/b_tools/README.md) |
| B.c | The process organising all of B: `greekocr/harvest/line_pipeline.py` and `greekocr/harvest/line_pipeline_census.py`; raw rows through corrections, eligibility, deduplication and immutable export. | [Pipeline](docs/B_training_data/c_pipeline/README.md), [graph](docs/B_training_data/c_pipeline/pipeline.mmd) |
| B.d | Revision of B.b, evidence, owner sheets, publication and returned marks: `greekocr/adjudicate/`; historical label sheets in `greekocr/labelfix/sheet.py`. | [Revision pipeline](docs/B_training_data/d_review/README.md), [sheet contract](docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md) |
| Shared | Deployment, operations, verification, types, CLI and vendor custody: `greekocr/deploy/`, `greekocr/ops/`, `greekocr/verify/`, `greekocr/types.py`, `greekocr/cli.py`, `greekocr/_vendor/`; Clariden scripts in `scripts/harvest/clariden/` and `scripts/labelfix/clariden/`. | [Shared infrastructure](docs/shared/README.md) |
| Records | Dated reports, briefs, handoffs and evidence by track in `docs/records/`. | [Records index](docs/records/INDEX.md) |

## 3. Current versions

The [tool manifest](docs/harvest/line_pipeline/tool_versions.json) records named method generations, component hashes and release status. The pipeline identifier comes from `greekocr/harvest/line_pipeline.py`; the release codec is `greekocr/train/codec/v2.1.json` (266 classes). Versions do not measure accuracy or establish adoption.

| Component | Version | Meaning |
|---|---|---|
| Line pipeline | 0.3.3 | Current orchestration identifier; previous 0.3.2 remains an alias in historical bindings. |
| Segmentation filter | 0.13 (label 0.9-s5) | S4 measurement with one inclusive length band, 0.30–2.00, for all rows; accepted segmentation remains frozen. Band adoption is a recorded coordinator decision. |
| Content gate | 0.3 | Scripts and raw-text length checks before segmentation. |
| Final eligibility | 0.3 | Content, confidence, codec, CTC and split checks; aligned cell exemption. |
| Polytonic | 0.7 / SF7 A | `candidate_pre_audit`; proposal evidence cannot qualify admission. |
| Cyrillic | 0.3 / RU1 | Historical Russian word-final ь→ъ only. |
| Numerics | N1 0.2 assisted release; 0.3 pipeline binding | The assisted separator release is unchanged; the manifest's third generation adds the census03 digit/separator/digit candidate-negative rule. The rejected automatic ink candidate stays disabled. |
| Dashes | 0.1 | Tags only. |
| Inventory | 0.1 | Raw-row script and content inventory. |
| Content repair / composer | 0.2 / 0.3 | Bound repair evidence and compatible raw-parent edit spans. |
| Census orchestration | 0.7 | Durable processing, runtime binding and protected crop deduplication. |
| Codec | v2 | Frozen NFD atoms. |
| Label Quality Benchmark | truth_v1_1; scorer schema v1.2 | Frozen per-class print truth; no 0.n tool version is assigned in the manifest. |

Some A/B overview pages, the graph and the Clariden runbook retain earlier version labels. Use the current manifest and [pipeline stage description](docs/B_training_data/c_pipeline/README.md) for the current source. Historical deployed bundles and results retain their own versions; these identifiers do not establish a new production census result.

## 4. How to run

<a id="toolkit-setup"></a>
Python 3.11 or newer is required. From the repository root, create the local environment, install the package and test dependencies, run tests, and try the CLI:

```sh
UV_CACHE_DIR=/tmp/greekocr-uv-cache uv venv --python 3.11 .venv
UV_CACHE_DIR=/tmp/greekocr-uv-cache uv pip install --python .venv/bin/python -e '.[test]'
# Requires cargo/rustc and the Cargo.lock dependencies already cached locally.
# Resolves or builds debug AND release in scratch; never downloads dependencies.
.venv/bin/python -B -c 'from greekocr.harvest.predictor_path import predictor_binary; print(predictor_binary())'
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/greekocr --help
.venv/bin/greekocr recipes
.venv/bin/greekocr annotate 'ἅλφα Latin'
```

The install creates `.venv/` and its executables. Optional extras in `pyproject.toml` cover `readers`, `warmstart`, `docling`, `docai` and `web`; heavy runtimes load only when needed. The default pytest scope is `tests/`; fast-line prototype tests need an explicit `prototypes/fast_lines/` path. See the [API](docs/API.md) and [standard](docs/STANDARD.md) for contracts.

The frozen font predictor resolver uses `GREEK_OCR_PREDICTOR` (an explicit executable path), then `GREEK_OCR_BUILD_DIR/<profile>/greekocr-frozen-font-predict`, then an existing in-repo `scripts/harvest/filter_runtime/target/<profile>/greekocr-frozen-font-predict`. The default build directory on macOS is `~/Library/Caches/greek-ocr-toolkit/filter_runtime/<Cargo.lock SHA256>/` (`~/.cache/greek-ocr-toolkit/filter_runtime/<Cargo.lock SHA256>/` elsewhere). Set `GREEK_OCR_BUILD_DIR` to a writable scratch target directory for a read-only checkout. If no binary exists, the helper runs `cargo build --offline --locked --target-dir <scratch>` from `scripts/harvest/filter_runtime/`, then the same command with `--release`. `BUILD_RECEIPT.json` in scratch records the Cargo.lock SHA256, rustc version and both binary SHA256 values. A missing toolchain or offline dependency is an error; tests do not silently skip it. The session fixture exports the resolved `GREEK_OCR_PREDICTOR` to tests and replay adapters. Set `GREEK_OCR_DATA_ROOT` to the external data root to include all saved-data test parameters.

The pipeline CLI defaults to reporting-only preflight. This example reads the existing historical census03 configuration and prints its declared parents and correction artifacts:

```sh
.venv/bin/python -B -m greekocr.harvest.line_pipeline_census \
  docs/records/harvest/seg_census/remote_evidence/census03_config.json \
  --out /tmp/greekocr-pipeline-preflight
```

Without `--execute`, this does not validate input files or process rows. A real run needs an exact configuration, external inputs and a verified worker runtime. Read the [pipeline guide](docs/B_training_data/c_pipeline/README.md), [Clariden runbook](docs/B_training_data/c_pipeline/RUNBOOK_CLARIDEN.md) and [job kinds](docs/records/harvest/seg_census/JOB_KINDS.md) before operations. Clariden distinguishes regression, parity and census jobs; deployment verification precedes smoke, and smoke precedes a full run. The archived deployment package has its own versions and resource settings.

## 5. Data policy

No tracked file may exceed **5 MB (5,000,000 bytes)**. Bulk data lives outside the repository under `GREEK_OCR_DATA_ROOT`; custody receipts live in [docs/cleanup_20261019/data_out/RECEIPTS/](docs/cleanup_20261019/data_out/RECEIPTS/). Each receipt records the artifact path, byte count, SHA256 and producing commit. New bulk crops and review sheets stay outside Git; small historical evidence and required test/demo fixtures already retained in Git are explicit exceptions, subject to the same 5 MB limit. Pools, census exports, bundles and other bulk outputs also stay outside git with receipts.

Use the [move manifest](docs/cleanup_20261019/data_out/MOVE_MANIFEST.tsv) to retrieve moved artifacts and the [layout report](docs/cleanup_20261019/LAYOUT_REPORT.md) to translate historical documentation paths. Historical receipts preserve their original hashes and path identities. Source rights and held-out work boundaries remain attached to the data; Anemi material is internal only and must never be redistributed. Credentials belong in the macOS Keychain and are injected at launch.

## 6. Where the history is

The [records index](docs/records/INDEX.md) leads to completed reports, briefs, handoffs and receipts by track. The [12 October public README](docs/records/README_public_20261012.md) preserves the former public description. Old branches remain history; this cleanup does not rewrite git history. The [cleanup record](docs/cleanup_20261019/) contains the owner's brief, plan, inventories, layout report and data custody records. Read [AGENTS.md](AGENTS.md) for working roles and review rules.

Sources: `docs/cleanup_20261019/OWNER_BRIEF.md`; `docs/cleanup_20261019/AGENTS_README_OUTLINE.md`; `docs/cleanup_20261019/PLAN.md`; `docs/cleanup_20261019/LAYOUT_REPORT.md`; `docs/A_ocr_development/README.md`; `docs/B_training_data/README.md`; `docs/B_training_data/a_google_ocr/README.md`; `docs/B_training_data/b_tools/README.md`; `docs/B_training_data/c_pipeline/README.md`; `docs/B_training_data/d_review/README.md`; `docs/shared/README.md`; `docs/records/INDEX.md`; `docs/harvest/line_pipeline/tool_versions.json`; `README.md` (previous contents); `AGENTS.md` (previous contents); `docs/records/README_public_20261012.md`; `docs/B_training_data/c_pipeline/pipeline.mmd`; `docs/B_training_data/c_pipeline/RUNBOOK_CLARIDEN.md`; `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`; `docs/B_training_data/d_review/OWNER_SHEETS.md`; `docs/B_training_data/b_tools/LABEL_QUALITY_BENCHMARK.md`; `docs/ocr_program_2026-10-06/briefs/CLEAN5E_readme_agents.md`; `pyproject.toml`; `greekocr/harvest/line_pipeline.py`; `greekocr/harvest/line_pipeline_census.py`; `tests/test_size_guard.py`; `.gitignore`.
