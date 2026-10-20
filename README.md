# Greek OCR toolkit

## 1. What this repository is

This is the private toolkit for the Greek OCR programme, especially printed polytonic Greek. The owner's standard (8 October 2026) is that every tool sits behind a typed API with tests. The Python package is `greekocr`; the command-line tool has the same name. Source identities, inputs and outputs are bound by hashes and receipts.

The repository has two separate aspects: **A — development of OCR and our segmenters**, and **B — creation of training data for OCR**. B uses frozen tool versions from A; developing a segmenter and admitting training rows are separate work. A PDF text layer is another OCR observation, and agreement between readers is not human ground truth.

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

The [tool manifest](docs/harvest/line_pipeline/tool_versions.json) records named method generations, component hashes and release status. The pipeline identifier comes from `greekocr/harvest/line_pipeline.py`; the codec is `greekocr/_vendor/codec/v2.json`. Versions do not measure accuracy or establish adoption.

| Component | Version | Meaning |
|---|---|---|
| Line pipeline | 0.3.2 | Current orchestration identifier. |
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
