# Greek OCR toolkit

The private standard for Greek OCR tooling: typed APIs, preserved source logic, byte-bound provenance and offline tests. Python 3.11 or newer; CLI: `greekocr`.

```sh
UV_CACHE_DIR=/tmp/greekocr-uv-cache uv venv --python 3.11 .venv
UV_CACHE_DIR=/tmp/greekocr-uv-cache uv pip install --python .venv/bin/python -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/greekocr recipes
.venv/bin/greekocr annotate 'ἅλφα Latin'
```

The base install supports manifest custody, tags, scoring and text-layer extraction. Reader, warm-start and Docling dependencies are optional extras. Linux worker environment plans isolate Kraken and Paddle; CUDA/Paddle runtimes are not installed by importing this package.

- `greekocr.synth`: captured v5/v7/v8 recipe identity, existing Rust factory calls, HEAD-bound mixes and deterministic sampling.
- `greekocr.real`: reviewed work partitions, PDF/DjVu text layers, Polyton-DB/GRPOLY and other native formats, two-reader adjudication and Rust real import.
- `greekocr.real.sources`: recorded parsers and explicit discovery/fetch APIs, with original rate state and transfer receipts.
- `greekocr.annotate`: frozen script, word and overlapping diagnostic line tags.
- `greekocr.readers`: our raw evaluation reader, Kalchas, persistent CLLG worker, native R01/R03 references and explicit service stubs.
- `greekocr.score`: strict atom CER, bake-off NFD scoring, mark F1/homoglyph diagnostics and by-category summaries.
- `greekocr.warmstart`: exact donor mappings, conversion, state verification and native parity gates.
- `greekocr.deploy`: Docling `glossapi` entry point, reviewable node setup plans and injected Prime Intellect pod operations.
- `greekocr.ops`: atomic receipts, hash verification, environment secrets, rate locks and bounded liveness.

[API examples](docs/API.md), [standard](docs/STANDARD.md), [inventory](docs/INVENTORY.md), [validation](docs/VALIDATION.md).

For real lines: stage recorded source metadata and reviewed rights; build a canonical-work map with explicit held-out exposure evidence; extract/import candidate crops; adjudicate independently; run `import_real_shards`; then build a manifest with exact receipts. Do not split related works by line. Missing text layers are recorded, not reconstructed by OCR.

The Rust factory stays in its source project. `build_shards` requires an existing binary, an ingested pool and the worker's fonts/assets/cwd. Recipes here are copied unchanged. Mix APIs require the custody repository explicitly; the exact recipe bytes must be committed at its HEAD. This scaffold has no Git writes; the coordinator commits it and configures repository visibility.

Discovery is offline by default. Its bridge stages byte-identical native CLIs and redirects their evidence root to the caller's directory, retaining shared ledger/rate locks and adjacent optional S17 exclusions. Fetch/service/pod APIs perform their named external action only when called; this phase exercises them through mocks. The original pod launcher and historical launch shells are archived reference files.

The CPU suite verifies source hashes, custody refusal, recorded discovery replay, import/adjudication edges, strict scoring, persistent-worker behavior, real fixture-model loading/conversion, Docling replacement contracts and operational terminal states. Real released-model recognition, production datasets, Linux/CUDA environments and the original full Corpus cohort are separate qualification work.
